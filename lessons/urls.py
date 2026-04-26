from django.urls import path

from . import views

app_name = 'lessons'

urlpatterns = [
    path('<int:pk>/', views.lesson_detail_view, name='detail'),
    path('<int:pk>/complete/', views.mark_lesson_complete, name='complete'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
]
