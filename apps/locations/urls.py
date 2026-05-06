from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('', views.location_list, name='list'),
    path('<int:id>/', views.location_detail, name='detail'),
]