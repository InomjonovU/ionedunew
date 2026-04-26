from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, render

from lessons.models import Lesson, LessonView, Quarter

from .models import Subject


def subject_list_view(request):
    subjects = Subject.objects.filter(is_active=True).annotate(
        lesson_count=Count('lessons', filter=Q(lessons__is_published=True))
    )
    return render(request, 'subjects/list.html', {'subjects': subjects})


def subject_detail_view(request, slug):
    subject = get_object_or_404(Subject, slug=slug, is_active=True)

    grade = None
    quarters = []
    lessons = []
    selected_quarter_obj = None
    quarter_quiz = None
    quarter_quiz_available = False
    quarter_quiz_reason = ''
    quarter_progress = None

    if request.user.is_authenticated:
        grade = request.GET.get('grade', request.user.grade)
        quarter_num = request.GET.get('quarter')

        try:
            grade = int(grade)
        except (TypeError, ValueError):
            grade = request.user.grade

        quarters = Quarter.objects.filter(subject=subject, grade=grade).order_by('number')

        if quarter_num:
            try:
                selected_quarter_obj = quarters.get(number=int(quarter_num))
                lessons = list(
                    Lesson.objects
                    .filter(quarter=selected_quarter_obj, is_published=True)
                    .order_by('order')
                )
                viewed_ids = set(
                    LessonView.objects.filter(
                        user=request.user,
                        lesson__in=lessons,
                        completed=True,
                    ).values_list('lesson_id', flat=True)
                )
                for i, lesson in enumerate(lessons):
                    lesson.is_viewed = lesson.pk in viewed_ids
                    # Ketma-ketlik qulflari
                    if i == 0:
                        lesson.is_locked = False
                    else:
                        lesson.is_locked = lessons[i - 1].pk not in viewed_ids

                # Chorak testi (agar mavjud bo'lsa)
                quarter_quiz = getattr(selected_quarter_obj, 'quiz', None)
                if quarter_quiz and quarter_quiz.is_published:
                    quarter_quiz_available = quarter_quiz.is_available_for(request.user)
                    quarter_quiz_reason = quarter_quiz.availability_reason(request.user)

                # Progress
                total = len(lessons)
                done = len(viewed_ids)
                quarter_progress = {
                    'total': total,
                    'done': done,
                    'percent': int((done / total) * 100) if total else 0,
                }
            except Quarter.DoesNotExist:
                pass
    else:
        grade = request.GET.get('grade', 9)

    context = {
        'subject': subject,
        'grade': grade,
        'quarters': quarters,
        'lessons': lessons,
        'grades': range(1, 12),
        'selected_quarter': request.GET.get('quarter'),
        'selected_quarter_obj': selected_quarter_obj,
        'quarter_quiz': quarter_quiz,
        'quarter_quiz_available': quarter_quiz_available,
        'quarter_quiz_reason': quarter_quiz_reason,
        'quarter_progress': quarter_progress,
    }
    return render(request, 'subjects/detail.html', context)
