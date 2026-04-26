from django.urls import path

from . import views

app_name = 'ai_modules'

urlpatterns = [
    path('chat/', views.chat_ajax, name='chat'),
    path('lesson-summary/<int:lesson_pk>/', views.lesson_summary_view, name='lesson_summary'),
    path('essay-check/', views.essay_check_view, name='essay_check'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
]
