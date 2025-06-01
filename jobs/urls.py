from django.urls import path
from . import views

urlpatterns = [
    path('', views.job_list, name='job_list'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('post/', views.post_job, name='post_job'),
    path('applications/', views.applications_view, name='applications'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('group-request/', views.group_request_view, name='group_request'),
    path('admin-group-requests/', views.admin_group_requests_view, name='admin_group_requests'),
]
