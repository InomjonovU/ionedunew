import json

from django.conf import settings
from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User
from certificates.models import Certificate
from lessons.models import Lesson, LessonView, Quarter
from library.models import LibraryItem
from notifications.models import Notification
from quizzes.models import Choice, Question, Quiz, QuizAttempt
from subjects.models import Subject

from .decorators import staff_required
from .forms import (
    ChoiceFormSet, LessonForm, LibraryItemForm,
    QuarterForm, QuestionForm, QuizForm, SiteSettingsForm, SubjectForm,
)
from .models import SiteSettings


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@staff_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    stats = {
        'total_users':     User.objects.filter(is_staff=False).count(),
        'total_lessons':   Lesson.objects.filter(is_published=True).count(),
        'total_quizzes':   Quiz.objects.filter(is_published=True).count(),
        'total_certs':     Certificate.objects.count(),
        'library_items':   LibraryItem.objects.filter(is_published=True).count(),
        'new_users_month': User.objects.filter(date_joined__date__gte=month_start).count(),
        'attempts_month':  QuizAttempt.objects.filter(
            started_at__date__gte=month_start, is_completed=True
        ).count(),
        'avg_score': QuizAttempt.objects.filter(is_completed=True).aggregate(
            avg=Avg('score')
        )['avg'] or 0,
    }

    top_lessons = (
        Lesson.objects
        .annotate(view_count=Count('views'))
        .order_by('-view_count')[:5]
    )
    recent_users = User.objects.filter(is_staff=False).order_by('-date_joined')[:10]
    recent_attempts = (
        QuizAttempt.objects
        .filter(is_completed=True)
        .select_related('user', 'quiz')
        .order_by('-started_at')[:8]
    )
    subject_activity = (
        Subject.objects
        .annotate(views=Count('lessons__views'))
        .order_by('-views')[:6]
    )

    context = {
        'stats': stats,
        'top_lessons': top_lessons,
        'recent_users': recent_users,
        'recent_attempts': recent_attempts,
        'subject_activity': subject_activity,
        'avg_score': round(stats['avg_score'], 1),
    }
    return render(request, 'panel/dashboard.html', context)


# ─── FOYDALANUVCHILAR ─────────────────────────────────────────────────────────

@staff_required
def users_list(request):
    q = request.GET.get('q', '')
    grade = request.GET.get('grade', '')

    users = User.objects.filter(is_staff=False).order_by('-date_joined')

    if q:
        users = users.filter(
            Q(first_name__icontains=q) | Q(last_name__icontains=q) | Q(email__icontains=q)
        )
    if grade:
        users = users.filter(grade=grade)

    context = {
        'users': users.annotate(
            cert_count=Count('certificates'),
            attempt_count=Count('quiz_attempts'),
        ),
        'q': q, 'grade': grade,
        'grades': range(1, 12), 'total': users.count(),
    }
    return render(request, 'panel/users.html', context)


# ─── FANLAR (SUBJECTS) ────────────────────────────────────────────────────────

@staff_required
def subjects_list(request):
    subjects = Subject.objects.annotate(
        lesson_count=Count('lessons', filter=Q(lessons__is_published=True)),
        quarter_count=Count('quarters'),
    ).order_by('order')
    return render(request, 'panel/subjects.html', {'subjects': subjects})


@staff_required
def subject_create(request):
    form = SubjectForm(request.POST or None)
    if form.is_valid():
        subject = form.save()
        messages.success(request, f'"{subject.name}" fani yaratildi.')
        return redirect('panel:subjects')
    return render(request, 'panel/subject_form.html', {'form': form, 'title': 'Yangi fan'})


@staff_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    form = SubjectForm(request.POST or None, instance=subject)
    if form.is_valid():
        form.save()
        messages.success(request, f'"{subject.name}" fani yangilandi.')
        return redirect('panel:subjects')
    return render(request, 'panel/subject_form.html', {
        'form': form, 'object': subject, 'title': f'"{subject.name}" — tahrirlash'
    })


@staff_required
@require_POST
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    name = subject.name
    subject.delete()
    messages.success(request, f'"{name}" fani o\'chirildi.')
    return redirect('panel:subjects')


# ─── CHORAKLAR (QUARTERS) ─────────────────────────────────────────────────────

@staff_required
def quarters_list(request):
    subject_id = request.GET.get('subject', '')
    grade = request.GET.get('grade', '')
    quarters = Quarter.objects.select_related('subject').order_by('subject', 'grade', 'number')
    if subject_id:
        quarters = quarters.filter(subject_id=subject_id)
    if grade:
        quarters = quarters.filter(grade=grade)
    context = {
        'quarters': quarters,
        'subjects': Subject.objects.filter(is_active=True),
        'grades': range(1, 12),
        'subject_id': subject_id, 'grade': grade,
    }
    return render(request, 'panel/quarters.html', context)


@staff_required
def quarter_create(request):
    form = QuarterForm(request.POST or None)
    if form.is_valid():
        quarter = form.save()
        messages.success(request, f'Chorak yaratildi: {quarter}')
        return redirect('panel:quarters')
    return render(request, 'panel/quarter_form.html', {'form': form, 'title': 'Yangi chorak'})


@staff_required
def quarter_edit(request, pk):
    quarter = get_object_or_404(Quarter, pk=pk)
    form = QuarterForm(request.POST or None, instance=quarter)
    if form.is_valid():
        form.save()
        messages.success(request, 'Chorak yangilandi.')
        return redirect('panel:quarter_edit', pk=quarter.pk)
    quiz = getattr(quarter, 'quiz', None)
    questions = quiz.questions.prefetch_related('choices').order_by('order') if quiz else []
    quarter_lessons = (
        Lesson.objects
        .filter(quarter=quarter)
        .annotate(view_count=Count('views'))
        .order_by('order', 'title')
    )
    return render(request, 'panel/quarter_form.html', {
        'form': form, 'object': quarter, 'title': 'Chorakni tahrirlash',
        'quiz': quiz, 'questions': questions,
        'quarter_lessons': quarter_lessons,
    })


@staff_required
@require_POST
def quarter_delete(request, pk):
    quarter = get_object_or_404(Quarter, pk=pk)
    quarter.delete()
    messages.success(request, 'Chorak o\'chirildi.')
    return redirect('panel:quarters')


# ─── DARSLAR (LESSONS) ────────────────────────────────────────────────────────

@staff_required
def lessons_list(request):
    subject_id = request.GET.get('subject', '')
    grade = request.GET.get('grade', '')
    q = request.GET.get('q', '')

    lessons = Lesson.objects.select_related('subject', 'quarter').order_by('-created_at')
    if subject_id:
        lessons = lessons.filter(subject_id=subject_id)
    if grade:
        lessons = lessons.filter(grade=grade)
    if q:
        lessons = lessons.filter(title__icontains=q)

    context = {
        'lessons': lessons.annotate(view_count=Count('views'))[:200],
        'subjects': Subject.objects.filter(is_active=True),
        'grades': range(1, 12),
        'subject_id': subject_id, 'grade': grade, 'q': q,
    }
    return render(request, 'panel/lessons.html', context)


@staff_required
def lesson_create(request):
    quarter_pk = request.GET.get('quarter') or request.POST.get('_quarter_pk')
    initial = {}
    quarter_obj = None
    if quarter_pk:
        quarter_obj = Quarter.objects.filter(pk=quarter_pk).select_related('subject').first()
        if quarter_obj:
            initial['quarter'] = quarter_obj.pk
            initial['subject'] = quarter_obj.subject_id
            initial['grade'] = quarter_obj.grade
    form = LessonForm(request.POST or None, request.FILES or None, initial=initial)
    if form.is_valid():
        lesson = form.save()
        messages.success(request, f'"{lesson.title}" darsi yaratildi.')
        if quarter_pk:
            return redirect('panel:quarter_edit', pk=quarter_pk)
        return redirect('panel:lesson_edit', pk=lesson.pk)
    return render(request, 'panel/lesson_form.html', {
        'form': form, 'title': 'Yangi dars',
        'subjects': Subject.objects.filter(is_active=True),
        'quarters': Quarter.objects.select_related('subject').order_by('subject', 'grade', 'number'),
        'from_quarter': quarter_obj,
    })


@staff_required
def lesson_edit(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    form = LessonForm(request.POST or None, request.FILES or None, instance=lesson)
    if form.is_valid():
        form.save()
        messages.success(request, f'"{lesson.title}" darsi yangilandi.')
        return redirect('panel:lesson_edit', pk=lesson.pk)
    quiz = getattr(lesson, 'quiz', None)
    questions = quiz.questions.prefetch_related('choices').order_by('order') if quiz else []
    return render(request, 'panel/lesson_form.html', {
        'form': form, 'object': lesson, 'title': f'"{lesson.title}" — tahrirlash',
        'subjects': Subject.objects.filter(is_active=True),
        'quarters': Quarter.objects.select_related('subject').order_by('subject', 'grade', 'number'),
        'quiz': quiz,
        'questions': questions,
    })


@staff_required
@require_POST
def lesson_delete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    title = lesson.title
    lesson.delete()
    messages.success(request, f'"{title}" darsi o\'chirildi.')
    return redirect('panel:lessons')


@staff_required
@require_POST
def toggle_lesson_publish(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    lesson.is_published = not lesson.is_published
    lesson.save(update_fields=['is_published'])
    return JsonResponse({'published': lesson.is_published})


@staff_required
def lesson_upload_video(request, pk):
    """AJAX: video fayl yuklash progress bilan."""
    lesson = get_object_or_404(Lesson, pk=pk)
    if request.method == 'POST' and request.FILES.get('video_file'):
        video = request.FILES['video_file']
        if lesson.video_file:
            lesson.video_file.delete(save=False)
        lesson.video_file = video
        lesson.video_provider = 'local'
        lesson.save(update_fields=['video_file', 'video_provider'])
        return JsonResponse({'ok': True, 'url': lesson.video_file.url})
    return JsonResponse({'error': 'Fayl yuborilmadi'}, status=400)


# ─── TESTLAR (QUIZZES) ────────────────────────────────────────────────────────

@staff_required
def quizzes_list(request):
    subject_id = request.GET.get('subject', '')
    quiz_type = request.GET.get('type', '')

    quizzes = Quiz.objects.order_by('-created_at')
    if subject_id:
        quizzes = quizzes.filter(
            Q(lesson__subject_id=subject_id) | Q(quarter__subject_id=subject_id)
        )
    if quiz_type:
        quizzes = quizzes.filter(quiz_type=quiz_type)

    context = {
        'quizzes': quizzes.annotate(
            question_count=Count('questions', distinct=True),
            attempt_count=Count('attempts', distinct=True),
            pass_count=Count('attempts', filter=Q(attempts__is_passed=True), distinct=True),
        )[:200],
        'subjects': Subject.objects.filter(is_active=True),
        'subject_id': subject_id, 'quiz_type': quiz_type,
    }
    return render(request, 'panel/quizzes.html', context)


@staff_required
def quiz_create(request):
    initial = {}
    lesson_pk = request.GET.get('lesson') or request.POST.get('lesson')
    quarter_pk = request.GET.get('quarter') or request.POST.get('quarter')
    quiz_type = request.GET.get('type') or request.POST.get('quiz_type')

    if lesson_pk:
        existing = Quiz.objects.filter(lesson_id=lesson_pk).first()
        if existing:
            messages.info(request, 'Bu dars uchun test allaqachon mavjud.')
            return redirect('panel:lesson_edit', pk=lesson_pk)
        initial['lesson'] = lesson_pk
        initial['quiz_type'] = 'lesson'
        lesson_obj = Lesson.objects.filter(pk=lesson_pk).first()
        if lesson_obj:
            initial['title'] = f'{lesson_obj.title} — Test'
    if quarter_pk:
        existing = Quiz.objects.filter(quarter_id=quarter_pk).first()
        if existing:
            messages.info(request, 'Bu chorak uchun test allaqachon mavjud.')
            return redirect('panel:quarter_edit', pk=quarter_pk)
        initial['quarter'] = quarter_pk
        initial['quiz_type'] = 'quarter'
        quarter_obj = Quarter.objects.filter(pk=quarter_pk).select_related('subject').first()
        if quarter_obj:
            initial['title'] = f'{quarter_obj.subject.name} {quarter_obj.grade}-sinf {quarter_obj.number}-chorak testi'
    if quiz_type:
        initial['quiz_type'] = quiz_type

    form = QuizForm(request.POST or None, initial=initial)
    if form.is_valid():
        quiz = form.save()
        messages.success(request, f'"{quiz.title}" testi yaratildi. Endi savollar qo\'shing.')
        if quiz.lesson_id:
            return redirect('panel:lesson_edit', pk=quiz.lesson_id)
        if quiz.quarter_id:
            return redirect('panel:quarter_edit', pk=quiz.quarter_id)
        return redirect('panel:quiz_edit', pk=quiz.pk)
    return render(request, 'panel/quiz_form.html', {
        'form': form, 'title': 'Yangi test',
        'lessons': Lesson.objects.select_related('subject').order_by('subject', 'title'),
        'quarters': Quarter.objects.select_related('subject').order_by('subject', 'grade', 'number'),
    })


@staff_required
def quiz_edit(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    form = QuizForm(request.POST or None, instance=quiz)
    if form.is_valid():
        form.save()
        messages.success(request, 'Test yangilandi.')
        return redirect('panel:quiz_edit', pk=quiz.pk)

    questions = quiz.questions.prefetch_related('choices').order_by('order')
    return render(request, 'panel/quiz_form.html', {
        'form': form, 'object': quiz, 'title': f'"{quiz.title}" — tahrirlash',
        'questions': questions,
        'lessons': Lesson.objects.filter(is_published=True).select_related('subject').order_by('subject', 'title'),
        'quarters': Quarter.objects.select_related('subject').order_by('subject', 'grade', 'number'),
    })


@staff_required
@require_POST
def quiz_delete(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    title = quiz.title
    quiz.delete()
    messages.success(request, f'"{title}" testi o\'chirildi.')
    return redirect('panel:quizzes')


@staff_required
@require_POST
def toggle_quiz_publish(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    quiz.is_published = not quiz.is_published
    quiz.save(update_fields=['is_published'])
    return JsonResponse({'published': quiz.is_published})


# ─── SAVOLLAR (QUESTIONS) ─────────────────────────────────────────────────────

@staff_required
def question_create(request, quiz_pk):
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    form = QuestionForm(request.POST or None, request.FILES or None)
    formset = ChoiceFormSet(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        question = form.save(commit=False)
        question.quiz = quiz
        question.save()
        formset.instance = question
        choices = formset.save(commit=False)
        for i, choice in enumerate(choices):
            choice.order = i
            choice.save()
        formset.save_m2m()
        messages.success(request, 'Savol qo\'shildi.')
        if quiz.lesson_id:
            return redirect('panel:lesson_edit', pk=quiz.lesson_id)
        if quiz.quarter_id:
            return redirect('panel:quarter_edit', pk=quiz.quarter_id)
        return redirect('panel:quiz_edit', pk=quiz_pk)

    return render(request, 'panel/question_form.html', {
        'form': form, 'formset': formset, 'quiz': quiz,
        'title': f'"{quiz.title}" — yangi savol',
    })


@staff_required
def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    form = QuestionForm(request.POST or None, request.FILES or None, instance=question)
    formset = ChoiceFormSet(request.POST or None, request.FILES or None, instance=question)

    if request.method == 'POST' and form.is_valid() and formset.is_valid():
        form.save()
        choices = formset.save(commit=False)
        for i, choice in enumerate(choices):
            choice.order = i
            choice.save()
        for obj in formset.deleted_objects:
            obj.delete()
        formset.save_m2m()
        messages.success(request, 'Savol yangilandi.')
        quiz_obj = question.quiz
        if quiz_obj.lesson_id:
            return redirect('panel:lesson_edit', pk=quiz_obj.lesson_id)
        if quiz_obj.quarter_id:
            return redirect('panel:quarter_edit', pk=quiz_obj.quarter_id)
        return redirect('panel:quiz_edit', pk=question.quiz_id)

    return render(request, 'panel/question_form.html', {
        'form': form, 'formset': formset,
        'quiz': question.quiz, 'object': question,
        'title': 'Savolni tahrirlash',
    })


@staff_required
@require_POST
def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    quiz_obj = question.quiz
    question.delete()
    messages.success(request, 'Savol o\'chirildi.')
    if quiz_obj.lesson_id:
        return redirect('panel:lesson_edit', pk=quiz_obj.lesson_id)
    if quiz_obj.quarter_id:
        return redirect('panel:quarter_edit', pk=quiz_obj.quarter_id)
    return redirect('panel:quiz_edit', pk=quiz_obj.pk)


# ─── KUTUBXONA (LIBRARY) ──────────────────────────────────────────────────────

@staff_required
def library_list(request):
    q = request.GET.get('q', '')
    items = LibraryItem.objects.select_related('subject').order_by('-created_at')
    if q:
        items = items.filter(Q(title__icontains=q) | Q(author__icontains=q))
    context = {
        'items': items[:200], 'q': q,
        'subjects': Subject.objects.filter(is_active=True),
    }
    return render(request, 'panel/library.html', context)


@staff_required
def library_create(request):
    form = LibraryItemForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        item = form.save()
        messages.success(request, f'"{item.title}" qo\'shildi.')
        return redirect('panel:library')
    return render(request, 'panel/library_form.html', {
        'form': form, 'title': 'Yangi material'
    })


@staff_required
def library_edit(request, pk):
    item = get_object_or_404(LibraryItem, pk=pk)
    form = LibraryItemForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, f'"{item.title}" yangilandi.')
        return redirect('panel:library')
    return render(request, 'panel/library_form.html', {
        'form': form, 'object': item, 'title': f'"{item.title}" — tahrirlash'
    })


@staff_required
@require_POST
def library_delete(request, pk):
    item = get_object_or_404(LibraryItem, pk=pk)
    title = item.title
    item.delete()
    messages.success(request, f'"{title}" o\'chirildi.')
    return redirect('panel:library')


@staff_required
@require_POST
def toggle_library_publish(request, pk):
    item = get_object_or_404(LibraryItem, pk=pk)
    item.is_published = not item.is_published
    item.save(update_fields=['is_published'])
    return JsonResponse({'published': item.is_published})


# ─── KONTENT UMUMIY ───────────────────────────────────────────────────────────

@staff_required
def content_overview(request):
    subjects = Subject.objects.annotate(
        lesson_count=Count('lessons'),
        quiz_count=Count('lessons__quiz'),
    ).order_by('order')
    context = {'subjects': subjects}
    return render(request, 'panel/content.html', context)


# ─── TIZIM XABARI ─────────────────────────────────────────────────────────────

@staff_required
@require_POST
def send_system_notification(request):
    title = request.POST.get('title', '').strip()
    message_text = request.POST.get('message', '').strip()
    if not title or not message_text:
        messages.error(request, 'Sarlavha va matn kiritilishi shart')
        return redirect('panel:dashboard')

    users = User.objects.filter(is_staff=False, is_active=True)
    Notification.objects.bulk_create([
        Notification(
            user=u, notification_type='system',
            title=title, message=message_text,
        )
        for u in users
    ])
    messages.success(request, f'{users.count()} ta foydalanuvchiga xabar yuborildi.')
    return redirect('panel:dashboard')


# ─── ANALYTICS ─────────────────────────────────────────────────────────────────

@staff_required
def analytics(request):
    from datetime import timedelta
    end = timezone.now().date()
    start = end - timedelta(days=29)

    daily_views = {}
    for i in range(30):
        day = start + timedelta(days=i)
        daily_views[day.strftime('%d/%m')] = LessonView.objects.filter(
            viewed_at__date=day
        ).count()

    daily_attempts = {}
    for i in range(30):
        day = start + timedelta(days=i)
        daily_attempts[day.strftime('%d/%m')] = QuizAttempt.objects.filter(
            started_at__date=day, is_completed=True
        ).count()

    top_subjects = Subject.objects.annotate(
        total_views=Count('lessons__views')
    ).order_by('-total_views')[:8]

    context = {
        'daily_views_labels': json.dumps(list(daily_views.keys())),
        'daily_views_data': json.dumps(list(daily_views.values())),
        'daily_attempts_labels': json.dumps(list(daily_attempts.keys())),
        'daily_attempts_data': json.dumps(list(daily_attempts.values())),
        'top_subjects': top_subjects,
    }
    return render(request, 'panel/analytics.html', context)


# ─── SAYT SOZLAMALARI ────────────────────────────────────────────────────────

@staff_required
def site_settings(request):
    obj = SiteSettings.load()

    # Haqiqiy statistika (bazadan)
    real_stats = {
        'students': User.objects.filter(is_staff=False).count(),
        'lessons': Lesson.objects.filter(is_published=True).count(),
        'subjects': Subject.objects.filter(is_active=True).count(),
        'certificates': Certificate.objects.count(),
        'questions': Question.objects.count(),
    }

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sayt sozlamalari saqlandi.')
            return redirect('panel:site_settings')
    else:
        form = SiteSettingsForm(instance=obj)

    context = {
        'form': form,
        'real_stats': real_stats,
    }
    return render(request, 'panel/site_settings.html', context)
