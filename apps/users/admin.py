from django.contrib import admin
from .models import UserProfile, Cart, CartItem

admin.site.register(UserProfile)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ('location', 'added_at')
    readonly_fields = ('added_at',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_items', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    readonly_fields = ('created_at', 'updated_at')
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('location', 'cart', 'added_at')
    list_filter = ('added_at', 'cart__user')
    search_fields = ('location__name', 'cart__user__username')