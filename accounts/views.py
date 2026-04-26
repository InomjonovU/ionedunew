from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Avg, Count
from django.shortcuts import redirect, render

from leaderboard.models import UserBadge
from lessons.models import LessonView
from quizzes.models import QuizAttempt
from subjects.models import Subject

from .forms import LoginForm, ProfileUpdateForm, RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or '/dashboard/'


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def dashboard_view(request):
    user = request.user

    # So'nggi 5 ta ko'rilgan dars
    recent_views = (
        LessonView.objects
        .filter(user=user)
        .select_related('lesson__subject')
        .order_by('-viewed_at')[:5]
    )

    # Fan bo'yicha progress
    subjects = Subject.objects.filter(is_active=True)
    subject_progress = []
    for subject in subjects:
        total = subject.lessons.filter(is_published=True).count()
        viewed = LessonView.objects.filter(
            user=user, lesson__subject=subject
        ).count()
        if total > 0:
            subject_progress.append({
                'subject': subject,
                'total': total,
                'viewed': viewed,
                'percent': int((viewed / total) * 100),
            })

    # So'nggi test natijalari
    recent_attempts = (
        QuizAttempt.objects
        .filter(user=user, is_completed=True)
        .select_related('quiz')
        .order_by('-started_at')[:5]
    )

    # Statistika
    stats = {
        'lessons_viewed': LessonView.objects.filter(user=user).count(),
        'tests_passed': QuizAttempt.objects.filter(user=user, is_passed=True).count(),
        'certificates': user.certificates.count(),
        'total_score': user.total_score,
    }

    # O'qilmagan bildirishnomalar
    unread_count = user.notifications.filter(is_read=False).count()

    context = {
        'recent_views': recent_views,
        'subject_progress': subject_progress,
        'recent_attempts': recent_attempts,
        'stats': stats,
        'unread_count': unread_count,
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user

    form = ProfileUpdateForm(request.POST or None, request.FILES or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request, 'Profil muvaffaqiyatli yangilandi!')
        return redirect('accounts:profile')

    # Fan bo'yicha progress
    subjects = Subject.objects.filter(is_active=True)
    subject_progress = []
    for subject in subjects:
        total = subject.lessons.filter(is_published=True).count()
        viewed = LessonView.objects.filter(user=user, lesson__subject=subject).count()
        if total > 0:
            subject_progress.append({
                'subject': subject,
                'percent': int((viewed / total) * 100),
            })

    badges = UserBadge.objects.filter(user=user).select_related('badge')
    avg_score = QuizAttempt.objects.filter(
        user=user, is_completed=True
    ).aggregate(avg=Avg('score'))['avg'] or 0

    context = {
        'form': form,
        'subject_progress': subject_progress,
        'badges': badges,
        'avg_score': round(avg_score, 1),
        'certificates': user.certificates.select_related('quiz').order_by('-issued_at'),
    }
    return render(request, 'accounts/profile.html', context)
