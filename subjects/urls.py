from django.urls import path

from . import views

app_name = 'subjects'

urlpatterns = [
    path('', views.subject_list_view, name='list'),
    path('<slug:slug>/', views.subject_detail_view, name='detail'),
]
