from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import UserProfile, Cart, CartItem
from apps.trips.models import Trip, TripStop
from apps.travel_buddies.models import TravelBuddyPost
from apps.survey.models import Survey
from apps.locations.models import Location

def user_list(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})

def user_detail(request, id):
    user = User.objects.get(id=id)
    return render(request, 'users/detail.html', {'user': user})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Xush kelibsiz, {username}!")
            return redirect('core:home')
        else:
            messages.error(request, "Login yoki parol xato!")
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, "Tizimdan chiqdingiz!")
    return redirect('core:home')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Bunday foydalanuvchi mavjud!")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Bunday email mavjud!")
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                UserProfile.objects.create(user=user)
                login(request, user)
                messages.success(request, "Ro'yxatdan o'tish muvaffaqiyatli!")
                return redirect('core:home')
        else:
            messages.error(request, "Parollar mos kelmadi!")
    return render(request, 'users/register.html')

@login_required
def profile_view(request, id):
    profile_user = User.objects.get(id=id)

    # Get user's travel history
    trips = Trip.objects.filter(user=profile_user).order_by('-created_at')[:6]

    # Get user's travel buddy posts
    posts = TravelBuddyPost.objects.filter(user=profile_user).order_by('-created_at')[:6]

    # Get user's surveys
    surveys = Survey.objects.filter(user=profile_user).order_by('-created_at')[:3]

    # Get friends/followers (for now, just other users)
    friends = User.objects.exclude(id=profile_user.id)[:8]

    # Get new suggestions (recent locations user hasn't visited)
    visited_locations = TripStop.objects.filter(trip__user=profile_user).values_list('location', flat=True)
    new_suggestions = Location.objects.exclude(id__in=visited_locations)[:6]
    
    # Get user's cart
    try:
        cart = profile_user.cart
        cart_items = cart.get_cart_items()
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=profile_user)
        cart_items = []

    # Profile stats
    stats = {
        'trips_count': trips.count(),
        'posts_count': posts.count(),
        'friends_count': friends.count(),
        'surveys_count': surveys.count(),
        'cart_count': cart.get_total_items(),
    }

    context = {
        'profile_user': profile_user,
        'trips': trips,
        'posts': posts,
        'surveys': surveys,
        'friends': friends,
        'new_suggestions': new_suggestions,
        'cart_items': cart_items,
        'stats': stats,
        'is_own_profile': request.user == profile_user,
    }

    return render(request, 'users/profile.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_cart(request, location_id):
    """Add a location to user's cart (AJAX)"""
    try:
        location = Location.objects.get(id=location_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Add or get the cart item
        cart_item, created = CartItem.objects.get_or_create(cart=cart, location=location)
        
        if created:
            return JsonResponse({
                'success': True,
                'message': f"'{location.name}' savatchaga qo'shildi!",
                'cart_count': cart.get_total_items(),
                'is_new': True
            })
        else:
            return JsonResponse({
                'success': True,
                'message': f"'{location.name}' allaqachon savatchada bor!",
                'cart_count': cart.get_total_items(),
                'is_new': False
            })
    except Location.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Joyi topilmadi'}, status=404)


@login_required
def remove_from_cart(request, item_id):
    """Remove an item from cart"""
    try:
        cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
        location_name = cart_item.location.name
        cart_item.delete()
        messages.success(request, f"'{location_name}' savatchadan o'chirildi!")
    except CartItem.DoesNotExist:
        messages.error(request, "Savatchada bunday joyi yo'q!")
    
    return redirect('users:cart')


@login_required
def cart_view(request):
    """View user's cart"""
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)
    
    context = {
        'cart': cart,
        'cart_items': cart.get_cart_items(),
    }
    return render(request, 'users/cart.html', context)


@login_required
def clear_cart(request):
    """Clear all items from cart"""
    try:
        cart = request.user.cart
        cart.items.all().delete()
        messages.success(request, "Savatchaning barcha narsalari o'chirildi!")
    except Cart.DoesNotExist:
        messages.error(request, "Savatchada narsalar yo'q!")
    
    return redirect('users:cart')