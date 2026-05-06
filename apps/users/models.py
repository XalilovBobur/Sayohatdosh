from django.db import models
from django.contrib.auth.models import User
from apps.locations.models import Location

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.user.username


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Cart"
    
    def get_total_items(self):
        return self.items.count()
    
    def get_cart_items(self):
        return self.items.all()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('cart', 'location')
    
    def __str__(self):
        return f"{self.location.name} in {self.cart.user.username}'s cart"