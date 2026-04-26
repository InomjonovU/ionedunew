from django.urls import path

from . import views

app_name = 'panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Foydalanuvchilar
    path('users/', views.users_list, name='users'),

    # Fanlar
    path('subjects/', views.subjects_list, name='subjects'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),

    # Choraklar
    path('quarters/', views.quarters_list, name='quarters'),
    path('quarters/create/', views.quarter_create, name='quarter_create'),
    path('quarters/<int:pk>/edit/', views.quarter_edit, name='quarter_edit'),
    path('quarters/<int:pk>/delete/', views.quarter_delete, name='quarter_delete'),

    # Kontent umumiy
    path('content/', views.content_overview, name='content'),

    # Darslar
    path('content/lessons/', views.lessons_list, name='lessons'),
    path('content/lessons/create/', views.lesson_create, name='lesson_create'),
    path('content/lessons/<int:pk>/edit/', views.lesson_edit, name='lesson_edit'),
    path('content/lessons/<int:pk>/delete/', views.lesson_delete, name='lesson_delete'),
    path('content/lessons/<int:pk>/toggle/', views.toggle_lesson_publish, name='toggle_lesson'),
    path('content/lessons/<int:pk>/upload-video/', views.lesson_upload_video, name='lesson_upload_video'),

    # Testlar
    path('content/quizzes/', views.quizzes_list, name='quizzes'),
    path('content/quizzes/create/', views.quiz_create, name='quiz_create'),
    path('content/quizzes/<int:pk>/edit/', views.quiz_edit, name='quiz_edit'),
    path('content/quizzes/<int:pk>/delete/', views.quiz_delete, name='quiz_delete'),
    path('content/quizzes/<int:pk>/toggle/', views.toggle_quiz_publish, name='toggle_quiz'),

    # Savollar
    path('content/quizzes/<int:quiz_pk>/questions/create/', views.question_create, name='question_create'),
    path('content/questions/<int:pk>/edit/', views.question_edit, name='question_edit'),
    path('content/questions/<int:pk>/delete/', views.question_delete, name='question_delete'),

    # Kutubxona
    path('content/library/', views.library_list, name='library'),
    path('content/library/create/', views.library_create, name='library_create'),
    path('content/library/<int:pk>/edit/', views.library_edit, name='library_edit'),
    path('content/library/<int:pk>/delete/', views.library_delete, name='library_delete'),
    path('content/library/<int:pk>/toggle/', views.toggle_library_publish, name='toggle_library'),

    # Sayt sozlamalari
    path('settings/', views.site_settings, name='site_settings'),

    # Analytics
    path('analytics/', views.analytics, name='analytics'),

    # Bildirishnoma
    path('notify/', views.send_system_notification, name='notify'),
]
