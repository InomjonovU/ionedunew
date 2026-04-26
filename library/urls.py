from django.urls import path

from . import views

app_name = 'library'

urlpatterns = [
    path('', views.library_list_view, name='list'),
    path('<int:pk>/', views.library_item_view, name='detail'),
    path('<int:pk>/download/', views.library_download_view, name='download'),
]
