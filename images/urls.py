from django.urls import path
from . import views


urlpatterns = [
    path('generate/', views.generate_images, name='generate_images'),
    path('result/<str:task_id>/', views.check_task_status, name='task_result')
]
