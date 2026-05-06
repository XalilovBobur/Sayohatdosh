from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Cart, UserProfile


@receiver(post_save, sender=User)
def create_cart_for_new_user(sender, instance, created, **kwargs):
    """Create a cart for new users"""
    if created:
        Cart.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def ensure_user_has_cart(sender, instance, **kwargs):
    """Ensure user always has a cart"""
    if not hasattr(instance, 'cart'):
        Cart.objects.get_or_create(user=instance)
