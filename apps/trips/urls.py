from django.urls import path
from . import views

app_name = 'trips'

urlpatterns = [
    path('result/<int:survey_id>/', views.trip_result, name='trip_result'),
]