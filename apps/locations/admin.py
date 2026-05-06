from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Location, LocationImage

class LocationImageInline(admin.TabularInline):
    model = LocationImage
    extra = 1
    max_num = 4
    fields = ('image', 'order')
    ordering = ('order',)
    
    def get_queryset(self, request):
        # Inline uchun optimized queryset
        return super().get_queryset(request)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'group_type_display', 'image_count')
    list_filter = ('category', 'difficulty', 'is_family_friendly', 'group_type')
    search_fields = ('name', 'description')
    inlines = [LocationImageInline]
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('name', 'description', 'category')
        }),
        ('Joylashuvi', {
            'fields': ('latitude', 'longitude')
        }),
        ('Xususiyatlari', {
            'fields': ('is_family_friendly', 'difficulty', 'avg_duration', 'group_type')
        }),
    )
    
    def group_type_display(self, obj):
        return obj.get_group_type_display()
    group_type_display.short_description = 'Guruh turi'
    
    def image_count(self, obj):
        count = obj.images.count()
        return f"{count}/4 rasm"
    image_count.short_description = 'Rasmlari'

@admin.register(LocationImage)
class LocationImageAdmin(admin.ModelAdmin):
    list_display = ('location', 'order', 'uploaded_at')
    list_filter = ('location', 'uploaded_at')
    ordering = ('location', 'order')
    raw_id_fields = ('location',)