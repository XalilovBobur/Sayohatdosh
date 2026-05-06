from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from apps.locations.models import Location

class TravelBuddyPost(models.Model):
    """Hamroh topish uchun post"""
    
    PREFERRED_GROUP_CHOICES = [
        ('everyone', 'Barchasi'),
        ('boys', 'Faqat yigitlar'),
        ('girls', 'Faqat qizlar'),
        ('family', 'Oila'),
        ('group', 'Guruh'),
    ]
    
    TRANSPORT_TYPE_CHOICES = [
        ('any', 'Ixtiyoriy'),
        ('own_car', 'Shaxsiy mashina'),
        ('taxi', 'Taksi'),
        ('bus', 'Avtobus'),
        ('train', 'Poyezd'),
        ('walking', 'Piyoda'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Faol'),
        ('completed', 'Tugatilgan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    # Basic fields
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='travel_buddy_posts')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='buddy_posts')
    travel_date = models.DateField()
    
    # Trip preferences
    preferred_group = models.CharField(
        max_length=10,
        choices=PREFERRED_GROUP_CHOICES,
        default='everyone'
    )
    people_needed = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Budget
    budget_from = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    budget_to = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # Transport
    transport_type = models.CharField(
        max_length=15,
        choices=TRANSPORT_TYPE_CHOICES,
        default='any'
    )
    
    # Additional info
    note = models.TextField(blank=True, null=True, max_length=500)
    
    # Status
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['location', 'travel_date']),
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.location.name} ({self.travel_date})"
    
    def is_expired(self):
        """Sana o'tib ketganmi tekshirish"""
        return self.travel_date < timezone.now().date()
    
    def auto_deactivate_if_expired(self):
        """O'tib ketgan vaqt postlarini avtomatik inactive qilish"""
        if self.is_expired() and self.is_active:
            self.is_active = False
            self.status = 'completed'
            self.save()


class BuddyRequest(models.Model):
    """Hamroh bo'lish uchun request"""
    
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('accepted', 'Qabul qilindi'),
        ('rejected', 'Rad etildi'),
        ('cancelled', 'Bekor qilindi'),
    ]
    
    from_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_buddy_requests'
    )
    to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_buddy_requests'
    )
    post = models.ForeignKey(
        TravelBuddyPost,
        on_delete=models.CASCADE,
        related_name='requests'
    )
    
    message = models.TextField(blank=True, null=True, max_length=500)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'post')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['to_user', 'status']),
            models.Index(fields=['from_user', 'status']),
            models.Index(fields=['post', 'status']),
        ]
    
    def __str__(self):
        return f"{self.from_user.username} -> {self.post.location.name}"
    
    def save(self, *args, **kwargs):
        """Validation: user o'z postiga request yubora olmasin"""
        if self.from_user == self.post.user:
            raise ValueError("O'z postiga hamroh request yubora olmaysiz!")
        super().save(*args, **kwargs)
