from django.urls import path
from . import views

app_name = 'survey'

urlpatterns = [
    path('<int:id>/', views.survey_detail, name='detail'),
    path('create/', views.survey_create, name='create'),
    path('results/<int:survey_id>/', views.survey_results, name='results'),
]