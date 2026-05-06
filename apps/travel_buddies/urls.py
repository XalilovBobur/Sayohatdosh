from django.urls import path
from . import views

app_name = 'travel_buddies'

urlpatterns = [
    # Posts
    path('', views.TravelBuddyListView.as_view(), name='list'),
    path('yangi/', views.TravelBuddyCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TravelBuddyDetailView.as_view(), name='detail'),
    
    # My posts
    path('mening-postlarim/', views.MyTravelBuddyPostsView.as_view(), name='my_posts'),
    path('<int:post_id>/bekor-qilish/', views.CancelBuddyPostView.as_view(), name='cancel_post'),
    
    # Requests - Received
    path('requestlar/', views.ReceivedBuddyRequestsView.as_view(), name='received_requests'),
    path('request/<int:request_id>/qabul-qilish/', views.AcceptBuddyRequestView.as_view(), name='accept_request'),
    path('request/<int:request_id>/rad-etish/', views.RejectBuddyRequestView.as_view(), name='reject_request'),
    
    # Requests - Sent
    path('yuborganlarim/', views.SentBuddyRequestsView.as_view(), name='sent_requests'),
    path('<int:post_id>/hamroh-bo-lish/', views.SendBuddyRequestView.as_view(), name='send_request'),
]
