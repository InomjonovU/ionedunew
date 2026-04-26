from django.urls import path

from . import views

app_name = 'quizzes'

urlpatterns = [
    path('<int:pk>/', views.quiz_start_view, name='start'),
    path('<int:pk>/submit/', views.quiz_submit_view, name='submit'),
    path('<int:pk>/result/', views.quiz_result_view, name='result'),
    path('save-answer/', views.save_answer_ajax, name='save_answer'),
]
