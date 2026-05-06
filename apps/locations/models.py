from django.db import models
from django.core.exceptions import ValidationError
from apps.survey.models import Interest

class Location(models.Model):
    GROUP_TYPE_CHOICES = [
        ('large_group', '10-15 kishidan iborat guruh'),
        ('medium_group', '6-10 kishidan iborat guruh'),
        ('small_group', '1-5 kishidan iborat guruh'),
        ('group', 'Guruh shaklda'),
        ('family_1_child', 'Ota-ona + 1ta yosh bola bn'),
        ('family_2_children', 'Ota-ona + 2ta yosh bola bn'),
        ('family_companions', 'Oilaviy hamrohlar'),
        ('1_2_partners', '1-2 ta sherik bilan'),
        ('solo', 'Yakka'),
        ('friends', 'Dostlar bilan'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()

    category = models.ForeignKey(Interest, on_delete=models.CASCADE)

    latitude = models.FloatField()
    longitude = models.FloatField()

    is_family_friendly = models.BooleanField(default=True)
    difficulty = models.IntegerField(default=1) # 1-5

    avg_duration = models.IntegerField(default=60)  # minut

    group_type = models.CharField(
        max_length=20,
        choices=GROUP_TYPE_CHOICES,
        default='solo',
        verbose_name='Guruh turi'
    )

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

    def get_images(self):
        """Lokatsiyaning barcha rasmlari"""
        return self.images.all()

    def get_first_image(self):
        """Birinchi rasm"""
        image = self.images.first()
        return image.image if image else None


class LocationImage(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='locations/')
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"{self.location.name} - Rasm {self.order + 1}"