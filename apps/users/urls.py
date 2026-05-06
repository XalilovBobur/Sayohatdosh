from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='list'),
    path('<int:id>/', views.user_detail, name='detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/<int:id>/', views.profile_view, name='profile'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:location_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
]