from django.urls import path

from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list_view, name='list'),
    path('unread-count/', views.unread_count_ajax, name='unread_count'),
    path('mark-all-read/', views.mark_all_read_ajax, name='mark_all_read'),
]
