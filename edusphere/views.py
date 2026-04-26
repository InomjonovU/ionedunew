from django.db.models import Count
from django.shortcuts import render

from accounts.models import User
from certificates.models import Certificate
from lessons.models import Lesson
from panel.models import SiteSettings
from quizzes.models import Question, Quiz
from subjects.models import Subject


def _get_stats():
    """Sayt statistikasini qaytaradi — haqiqiy yoki admin tomonidan kiritilgan."""
    settings = SiteSettings.load()

    if settings.use_real_stats:
        total_users = User.objects.filter(is_staff=False).count()
        total_lessons = Lesson.objects.filter(is_published=True).count()
        total_subjects = Subject.objects.filter(is_active=True).count()
        total_certs = Certificate.objects.count()
        total_questions = Question.objects.count()
        total_quizzes = Quiz.objects.filter(is_published=True).count()

        return {
            'students_count': f'{total_users:,}',
            'video_lessons_count': f'{total_lessons:,}',
            'subjects_count': str(total_subjects),
            'certificates_count': f'{total_certs:,}',
            'active_students_count': f'{total_users:,}',
            'average_rating': settings.average_rating,
            'test_questions_count': f'{total_questions:,}',
            'grades_count': settings.grades_count,
        }

    return {
        'students_count': settings.students_count,
        'video_lessons_count': settings.video_lessons_count,
        'subjects_count': settings.subjects_count,
        'certificates_count': settings.certificates_count,
        'active_students_count': settings.active_students_count,
        'average_rating': settings.average_rating,
        'test_questions_count': settings.test_questions_count,
        'grades_count': settings.grades_count,
    }


def home(request):
    stats = _get_stats()

    subjects_preview = []
    subjects = Subject.objects.filter(is_active=True).order_by('order', 'name')[:8]
    for s in subjects:
        lesson_count = Lesson.objects.filter(
            quarter__subject=s, is_published=True
        ).count()
        subjects_preview.append({'subject': s, 'lesson_count': lesson_count})

    context = {
        'stats': stats,
        'subjects_preview': subjects_preview,
    }
    return render(request, 'home.html', context)


def about(request):
    stats = _get_stats()
    context = {
        'stats': stats,
    }
    return render(request, 'pages/about.html', context)
