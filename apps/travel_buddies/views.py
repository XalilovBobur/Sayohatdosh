from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import Http404
from django.utils import timezone

from .models import TravelBuddyPost, BuddyRequest
from .forms import TravelBuddyPostForm, BuddyRequestForm, TravelBuddyFilterForm
from .services import get_matching_posts, auto_deactivate_expired_posts
from apps.locations.models import Location


class TravelBuddyListView(LoginRequiredMixin, ListView):
    """Barcha hamroh postlari"""
    model = TravelBuddyPost
    template_name = 'travel_buddies/list.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        # Avtomatik expire qilish
        auto_deactivate_expired_posts()
        
        queryset = TravelBuddyPost.objects.filter(
            is_active=True,
            status='active'
        ).exclude(user=self.request.user).select_related('user', 'location')
        
        # Filter primerni qo'llash
        form = TravelBuddyFilterForm(self.request.GET)
        
        if form.is_valid():
            location = form.cleaned_data.get('location')
            travel_date_from = form.cleaned_data.get('travel_date_from')
            travel_date_to = form.cleaned_data.get('travel_date_to')
            preferred_group = form.cleaned_data.get('preferred_group')
            transport_type = form.cleaned_data.get('transport_type')
            budget_from = form.cleaned_data.get('budget_from')
            budget_to = form.cleaned_data.get('budget_to')
            
            if location:
                queryset = queryset.filter(location=location)
            
            if travel_date_from:
                queryset = queryset.filter(travel_date__gte=travel_date_from)
            
            if travel_date_to:
                queryset = queryset.filter(travel_date__lte=travel_date_to)
            
            if preferred_group:
                queryset = queryset.filter(preferred_group=preferred_group)
            
            if transport_type:
                queryset = queryset.filter(transport_type=transport_type)
            
            if budget_from:
                queryset = queryset.filter(Q(budget_to__gte=budget_from) | Q(budget_to__isnull=True))
            
            if budget_to:
                queryset = queryset.filter(Q(budget_from__lte=budget_to) | Q(budget_from__isnull=True))
        
        return queryset.order_by('-travel_date', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TravelBuddyFilterForm(self.request.GET)
        return context


class TravelBuddyCreateView(LoginRequiredMixin, CreateView):
    """Yangi hamroh post yaratish"""
    model = TravelBuddyPost
    form_class = TravelBuddyPostForm
    template_name = 'travel_buddies/create.html'
    success_url = reverse_lazy('travel_buddies:list')
    
    def get_initial(self):
        initial = super().get_initial()
        location_id = self.request.GET.get('location_id')
        if location_id:
            try:
                initial['location'] = Location.objects.get(id=location_id)
            except Location.DoesNotExist:
                pass
        return initial
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "✅ Hamroh post muvaffaqiyatli yaratildi!")
        return super().form_valid(form)


class TravelBuddyDetailView(LoginRequiredMixin, DetailView):
    """Post detaili va hamroh topish"""
    model = TravelBuddyPost
    template_name = 'travel_buddies/detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # O'tib ketgan vaqt postni check qilish
        if post.is_expired():
            post.is_active = False
            post.status = 'completed'
            post.save()
        
        # Mos postlarni topish
        matching_posts = get_matching_posts(post, limit=4)
        context['matching_posts'] = matching_posts
        
        # User bu postga request yuboraganmi?
        context['user_has_requested'] = BuddyRequest.objects.filter(
            from_user=self.request.user,
            post=post
        ).exists()
        
        return context


class MyTravelBuddyPostsView(LoginRequiredMixin, ListView):
    """Mening postlarim"""
    model = TravelBuddyPost
    template_name = 'travel_buddies/my_posts.html'
    context_object_name = 'posts'
    paginate_by = 12
    
    def get_queryset(self):
        return TravelBuddyPost.objects.filter(
            user=self.request.user
        ).select_related('location').order_by('-created_at')


class SentBuddyRequestsView(LoginRequiredMixin, ListView):
    """Men yuborgan requestlar"""
    model = BuddyRequest
    template_name = 'travel_buddies/sent_requests.html'
    context_object_name = 'requests'
    paginate_by = 12
    
    def get_queryset(self):
        return BuddyRequest.objects.filter(
            from_user=self.request.user
        ).select_related('post', 'to_user', 'post__location').order_by('-created_at')


class ReceivedBuddyRequestsView(LoginRequiredMixin, ListView):
    """Menga kelgan requestlar"""
    model = BuddyRequest
    template_name = 'travel_buddies/received_requests.html'
    context_object_name = 'requests'
    paginate_by = 12
    
    def get_queryset(self):
        return BuddyRequest.objects.filter(
            to_user=self.request.user
        ).select_related('post', 'from_user', 'post__location').order_by('-created_at')


class SendBuddyRequestView(LoginRequiredMixin, View):
    """Hamroh request yuborish"""
    
    def post(self, request, post_id):
        post = get_object_or_404(TravelBuddyPost, id=post_id)
        
        # Validation: o'z postiga request yubora olmasin
        if post.user == request.user:
            messages.error(request, "❌ O'z postiga hamroh request yubora olmaysiz!")
            return redirect('travel_buddies:detail', pk=post_id)
        
        # Validation: hali request yuboraganmi?
        existing_request = BuddyRequest.objects.filter(
            from_user=request.user,
            post=post
        ).first()
        
        if existing_request:
            if existing_request.status == 'pending':
                messages.warning(request, "⏳ Siz allaqachon request yuboringansiz!")
            elif existing_request.status == 'rejected':
                messages.info(request, "😔 Sizning request rad etilgan!")
            else:
                messages.info(request, "✅ Siz allaqachon qabul qilingansiz!")
            return redirect('travel_buddies:detail', pk=post_id)
        
        # Request yaratish
        form = BuddyRequestForm(request.POST)
        if form.is_valid():
            buddy_request = form.save(commit=False)
            buddy_request.from_user = request.user
            buddy_request.to_user = post.user
            buddy_request.post = post
            buddy_request.save()
            
            messages.success(request, "✅ Hamroh request yuborildi! Javobni kutmoqda...")
            return redirect('travel_buddies:detail', pk=post_id)
        
        messages.error(request, "❌ Xato bo'ldi. Iltimos, qayta urinib ko'ring.")
        return redirect('travel_buddies:detail', pk=post_id)


class AcceptBuddyRequestView(LoginRequiredMixin, View):
    """Request qabul qilish"""
    
    def post(self, request, request_id):
        buddy_request = get_object_or_404(BuddyRequest, id=request_id)
        
        # Validation: faqat post egasi qabul qila olsin
        if buddy_request.to_user != request.user:
            messages.error(request, "❌ Sizga bu huquq yo'q!")
            return redirect('travel_buddies:received_requests')
        
        # Validation: pending holatda bo'lishi kerak
        if buddy_request.status != 'pending':
            messages.warning(request, "⚠️ Bu request endi kutilmoqda emas!")
            return redirect('travel_buddies:received_requests')
        
        buddy_request.status = 'accepted'
        buddy_request.save()
        
        messages.success(request, f"✅ {buddy_request.from_user.username} ni qabul qildingiz! 🎉")
        return redirect('travel_buddies:received_requests')


class RejectBuddyRequestView(LoginRequiredMixin, View):
    """Request rad etish"""
    
    def post(self, request, request_id):
        buddy_request = get_object_or_404(BuddyRequest, id=request_id)
        
        # Validation: faqat post egasi rad eta olsin
        if buddy_request.to_user != request.user:
            messages.error(request, "❌ Sizga bu huquq yo'q!")
            return redirect('travel_buddies:received_requests')
        
        # Validation: pending holatda bo'lishi kerak
        if buddy_request.status != 'pending':
            messages.warning(request, "⚠️ Bu request endi kutilmoqda emas!")
            return redirect('travel_buddies:received_requests')
        
        buddy_request.status = 'rejected'
        buddy_request.save()
        
        messages.info(request, f"{buddy_request.from_user.username} ni rad ettingiz.")
        return redirect('travel_buddies:received_requests')


class CancelBuddyPostView(LoginRequiredMixin, View):
    """Post bekor qilish"""
    
    def post(self, request, post_id):
        post = get_object_or_404(TravelBuddyPost, id=post_id)
        
        # Validation: faqat post egasi bekor qila olsin
        if post.user != request.user:
            messages.error(request, "❌ Faqat yaratuvchi bekor qila oladi!")
            return redirect('travel_buddies:list')
        
        post.status = 'cancelled'
        post.is_active = False
        post.save()
        
        messages.success(request, "✅ Hamroh post bekor qilindi!")
        return redirect('travel_buddies:my_posts')
