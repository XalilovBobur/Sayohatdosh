from django.contrib import admin
from django.utils.html import format_html
from .models import TravelBuddyPost, BuddyRequest


@admin.register(TravelBuddyPost)
class TravelBuddyPostAdmin(admin.ModelAdmin):
    list_display = (
        'location_name',
        'user_name',
        'travel_date',
        'people_needed',
        'status_badge',
        'is_active',
        'created_at'
    )
    list_filter = ('status', 'is_active', 'preferred_group', 'transport_type', 'travel_date', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'location__name', 'note')
    readonly_fields = ('created_at', 'updated_at', 'user')
    date_hierarchy = 'travel_date'
    
    fieldsets = (
        ('Foydalanuvchi', {
            'fields': ('user',)
        }),
        ('Sayohat Ma\'lumotlari', {
            'fields': ('location', 'travel_date', 'people_needed')
        }),
        ('Preferences', {
            'fields': ('preferred_group', 'transport_type')
        }),
        ('Budjet', {
            'fields': ('budget_from', 'budget_to')
        }),
        ('Qo\'shimcha', {
            'fields': ('note',)
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def location_name(self, obj):
        return obj.location.name
    location_name.short_description = 'Joy'
    
    def user_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    user_name.short_description = 'Foydalanuvchi'
    
    def status_badge(self, obj):
        colors = {
            'active': '#28a745',
            'completed': '#6c757d',
            'cancelled': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        label = dict(TravelBuddyPost.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            label
        )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False


@admin.register(BuddyRequest)
class BuddyRequestAdmin(admin.ModelAdmin):
    list_display = (
        'from_user_name',
        'to_user_name',
        'post_location',
        'status_badge',
        'created_at'
    )
    list_filter = ('status', 'created_at')
    search_fields = ('from_user__username', 'to_user__username', 'post__location__name')
    readonly_fields = ('created_at', 'updated_at', 'from_user', 'to_user', 'post')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Requestlar', {
            'fields': ('from_user', 'to_user', 'post')
        }),
        ('Xabar', {
            'fields': ('message',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Vaqtlar', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def from_user_name(self, obj):
        return obj.from_user.get_full_name() or obj.from_user.username
    from_user_name.short_description = 'Kimdan'
    
    def to_user_name(self, obj):
        return obj.to_user.get_full_name() or obj.to_user.username
    to_user_name.short_description = 'Kimga'
    
    def post_location(self, obj):
        return obj.post.location.name
    post_location.short_description = 'Joy'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'accepted': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        label = dict(BuddyRequest.STATUS_CHOICES).get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            label
        )
    status_badge.short_description = 'Status'
    
    def has_add_permission(self, request):
        return False
