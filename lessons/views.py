from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Lesson, LessonComment, LessonView


def lesson_detail_view(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk, is_published=True)

    if not request.user.is_authenticated:
        return redirect('accounts:login')

    # Shu chorakdagi barcha darslar (tartib bo'yicha)
    quarter_lessons = (
        Lesson.objects
        .filter(quarter=lesson.quarter, is_published=True)
        .order_by('order', 'created_at')
    )

    # Foydalanuvchining tugatgan darslari
    completed_lesson_ids = set(
        LessonView.objects.filter(
            user=request.user,
            lesson__quarter=lesson.quarter,
            completed=True
        ).values_list('lesson_id', flat=True)
    )

    # Ketma-ketlik tekshiruvi: oldingi darslar tugatilganmi?
    lesson_list = list(quarter_lessons)
    current_index = None
    for i, l in enumerate(lesson_list):
        if l.pk == lesson.pk:
            current_index = i
            break

    is_locked = False
    if current_index is not None and current_index > 0:
        prev_lesson = lesson_list[current_index - 1]
        if prev_lesson.pk not in completed_lesson_ids:
            is_locked = True

    if is_locked:
        return render(request, 'lessons/locked.html', {
            'lesson': lesson,
            'prev_lesson': prev_lesson,
            'quarter_lessons': lesson_list,
            'completed_lesson_ids': completed_lesson_ids,
        })

    # Ko'rish holatini saqlash
    view_obj, _ = LessonView.objects.get_or_create(
        user=request.user, lesson=lesson
    )
    is_viewed = view_obj.completed

    # Dars uchun test mavjudmi va natijasi
    quiz_info = None
    if hasattr(lesson, 'quiz') and lesson.quiz:
        from quizzes.models import QuizAttempt
        quiz = lesson.quiz
        attempts = QuizAttempt.objects.filter(
            user=request.user, quiz=quiz, is_completed=True
        )
        passed = attempts.filter(is_passed=True).exists()
        quiz_info = {
            'quiz': quiz,
            'attempt_count': attempts.count(),
            'passed': passed,
            'attempts_left': quiz.max_attempts - attempts.count() if quiz.max_attempts > 0 else None,
        }

    # Darslar ro'yxati uchun ma'lumot
    lessons_with_status = []
    for i, l in enumerate(lesson_list):
        can_access = True
        if i > 0:
            prev = lesson_list[i - 1]
            if prev.pk not in completed_lesson_ids:
                can_access = False

        lessons_with_status.append({
            'lesson': l,
            'completed': l.pk in completed_lesson_ids,
            'is_current': l.pk == lesson.pk,
            'can_access': can_access,
            'number': i + 1,
        })

    # Izohlar
    comments = lesson.comments.select_related('user').order_by('-created_at')[:50]

    context = {
        'lesson': lesson,
        'is_viewed': is_viewed,
        'lessons_with_status': lessons_with_status,
        'comments': comments,
        'quiz_info': quiz_info,
        'completed_lesson_ids': completed_lesson_ids,
    }
    return render(request, 'lessons/detail.html', context)


@login_required
def mark_lesson_complete(request, pk):
    """AJAX: darsni to'liq ko'rilgan deb belgilash."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    lesson = get_object_or_404(Lesson, pk=pk)
    view_obj, _ = LessonView.objects.get_or_create(
        user=request.user, lesson=lesson
    )
    view_obj.completed = True
    view_obj.save(update_fields=['completed'])

    return JsonResponse({'status': 'ok', 'completed': True})


@login_required
def add_comment(request, pk):
    """Darsga izoh qo'shish."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    lesson = get_object_or_404(Lesson, pk=pk, is_published=True)
    text = request.POST.get('text', '').strip()

    if not text:
        return redirect('lessons:detail', pk=pk)

    LessonComment.objects.create(
        user=request.user,
        lesson=lesson,
        text=text,
    )

    return redirect('lessons:detail', pk=pk)
