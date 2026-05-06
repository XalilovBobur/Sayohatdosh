from django.contrib import admin
from .models import Interest, Companion, HealthCondition, Survey

admin.site.register(Interest)
admin.site.register(Companion)
admin.site.register(HealthCondition)
admin.site.register(Survey)