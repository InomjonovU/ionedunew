from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from certificates.models import Certificate
from lessons.models import LessonView
from notifications.models import Notification

from .models import AttemptAnswer, Choice, Quiz, QuizAttempt


@login_required
def quiz_start_view(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_published=True)

    # Gating: test foydalanuvchi uchun ochiqmi?
    if not quiz.is_available_for(request.user):
        return render(request, 'quizzes/locked.html', {
            'quiz': quiz,
            'reason': quiz.availability_reason(request.user),
        })

    # Kamida bitta savol bor bo'lishi kerak
    if quiz.questions.count() == 0:
        return render(request, 'quizzes/locked.html', {
            'quiz': quiz,
            'reason': "Bu testda hali savollar qo'shilmagan.",
        })

    # Yakunlangan urinishlar soni
    completed_attempts = QuizAttempt.objects.filter(
        user=request.user, quiz=quiz, is_completed=True
    )
    completed_count = completed_attempts.count()

    # Allaqachon o'tgan bo'lsa (ball olgan), qayta ishlash mumkin emas
    passed_attempt = completed_attempts.filter(is_passed=True).first()

    # Max attempts tekshiruvi (0 = cheksiz)
    if quiz.max_attempts > 0 and completed_count >= quiz.max_attempts:
        # 3 marta urinib, o'ta olmagan bo'lsa - avtomatik o'tkazish (ballsiz)
        if not passed_attempt and quiz.quiz_type == 'lesson' and quiz.lesson_id:
            # Darsni tugallangan deb belgilash, lekin ball bermaslik
            LessonView.objects.update_or_create(
                user=request.user,
                lesson_id=quiz.lesson_id,
                defaults={'completed': True},
            )
        return render(request, 'quizzes/no_attempts.html', {
            'quiz': quiz,
            'completed_count': completed_count,
            'passed_attempt': passed_attempt,
            'auto_passed': not passed_attempt,
        })

    # Avvalgi yakunlanmagan urinishni davom ettirish
    attempt = QuizAttempt.objects.filter(
        user=request.user, quiz=quiz, is_completed=False
    ).first()

    if not attempt:
        attempt = QuizAttempt.objects.create(user=request.user, quiz=quiz)

    questions = quiz.questions.prefetch_related('choices').order_by('order')

    # Har bir savol uchun allaqachon berilgan javoblar
    answers_qs = list(attempt.answers.all())
    answered_choice_ids = {a.selected_choice_id for a in answers_qs}
    answered_question_ids = {a.question_id for a in answers_qs}

    attempts_left = quiz.max_attempts - completed_count if quiz.max_attempts > 0 else None

    context = {
        'quiz': quiz,
        'attempt': attempt,
        'questions': questions,
        'answered_choice_ids': answered_choice_ids,
        'answered_question_ids': answered_question_ids,
        'time_limit_seconds': quiz.time_limit * 60 if quiz.time_limit else 0,
        'completed_count': completed_count,
        'attempts_left': attempts_left,
    }
    return render(request, 'quizzes/quiz.html', context)


@login_required
def quiz_submit_view(request, pk):
    if request.method != 'POST':
        return redirect('quizzes:start', pk=pk)

    quiz = get_object_or_404(Quiz, pk=pk)
    attempt = get_object_or_404(
        QuizAttempt, quiz=quiz, user=request.user, is_completed=False
    )

    # Barcha javoblarni saqlash
    for question in quiz.questions.all():
        choice_id = request.POST.get(f'question_{question.pk}')
        if choice_id:
            try:
                choice = Choice.objects.get(pk=choice_id, question=question)
                AttemptAnswer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_choice': choice},
                )
            except Choice.DoesNotExist:
                pass

    # Ball hisoblash
    attempt.calculate_score()
    attempt.finished_at = timezone.now()
    attempt.is_completed = True
    attempt.save()

    # Ball faqat birinchi marta o'tganda beriladi
    first_pass = attempt.is_passed and not QuizAttempt.objects.filter(
        user=request.user, quiz=quiz, is_completed=True, is_passed=True
    ).exclude(pk=attempt.pk).exists()

    if first_pass and attempt.score:
        request.user.total_score += int(attempt.score)
        request.user.save(update_fields=['total_score'])

    # Dars testi bo'lsa va o'tilgan bo'lsa, darsni tugallangan deb belgilash
    if attempt.is_passed and quiz.quiz_type == 'lesson' and quiz.lesson_id:
        LessonView.objects.update_or_create(
            user=request.user,
            lesson_id=quiz.lesson_id,
            defaults={'completed': True},
        )

    # 3 marta urinib o'ta olmasa, avtomatik o'tkazish (ballsiz)
    if not attempt.is_passed and quiz.max_attempts > 0:
        completed_count = QuizAttempt.objects.filter(
            user=request.user, quiz=quiz, is_completed=True
        ).count()
        if completed_count >= quiz.max_attempts:
            if quiz.quiz_type == 'lesson' and quiz.lesson_id:
                LessonView.objects.update_or_create(
                    user=request.user,
                    lesson_id=quiz.lesson_id,
                    defaults={'completed': True},
                )

    # Sertifikat berish (chorak testi + o'tildi)
    if attempt.is_passed and quiz.quiz_type == 'quarter':
        Certificate.objects.get_or_create(
            user=request.user,
            quiz=quiz,
            defaults={'attempt': attempt, 'score': attempt.score},
        )
        Notification.objects.create(
            user=request.user,
            notification_type='certificate',
            title='Sertifikat oldingiz!',
            message=f'"{quiz.title}" uchun sertifikat berildi. Ball: {attempt.score}%',
            related_quiz_id=quiz.pk,
        )

    # Test natijasi bildirishnomasini yuborish
    Notification.objects.create(
        user=request.user,
        notification_type='test_result',
        title='Test natijasi',
        message=f'"{quiz.title}": {attempt.score}% — {"O\'tildi" if attempt.is_passed else "O\'tilmadi"}',
        related_quiz_id=quiz.pk,
        action_url=f'/tests/{quiz.pk}/result/',
    )

    return redirect('quizzes:result', pk=attempt.pk)


@login_required
def quiz_result_view(request, pk):
    attempt = get_object_or_404(QuizAttempt, pk=pk, user=request.user)
    quiz = attempt.quiz

    # Savol + berilgan javob + to'g'ri javob
    answers_data = []
    for question in quiz.questions.prefetch_related('choices').order_by('order'):
        try:
            user_answer = attempt.answers.get(question=question)
            selected = user_answer.selected_choice
        except AttemptAnswer.DoesNotExist:
            selected = None

        correct = question.choices.filter(is_correct=True).first()
        answers_data.append({
            'question': question,
            'selected': selected,
            'correct': correct,
            'is_correct': selected and selected.is_correct,
        })

    certificate = None
    if attempt.is_passed and quiz.quiz_type == 'quarter':
        certificate = Certificate.objects.filter(
            user=request.user, quiz=quiz
        ).first()

    # Qolgan urinishlar
    completed_count = QuizAttempt.objects.filter(
        user=request.user, quiz=quiz, is_completed=True
    ).count()
    attempts_left = quiz.max_attempts - completed_count if quiz.max_attempts > 0 else None
    can_retry = attempts_left is None or attempts_left > 0

    wrong_count = attempt.total_questions - attempt.correct_count
    context = {
        'attempt': attempt,
        'quiz': quiz,
        'answers_data': answers_data,
        'certificate': certificate,
        'wrong_count': wrong_count,
        'attempts_left': attempts_left,
        'can_retry': can_retry,
        'completed_count': completed_count,
    }
    return render(request, 'quizzes/result.html', context)


@login_required
def save_answer_ajax(request):
    """AJAX: test yechish jarayonida bir javobni saqlash."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    attempt_id = request.POST.get('attempt_id')
    question_id = request.POST.get('question_id')
    choice_id = request.POST.get('choice_id')

    try:
        attempt = QuizAttempt.objects.get(
            pk=attempt_id, user=request.user, is_completed=False
        )
        choice = Choice.objects.get(pk=choice_id, question_id=question_id)
        AttemptAnswer.objects.update_or_create(
            attempt=attempt,
            question_id=question_id,
            defaults={'selected_choice': choice},
        )
        return JsonResponse({'status': 'saved'})
    except (QuizAttempt.DoesNotExist, Choice.DoesNotExist):
        return JsonResponse({'error': 'invalid'}, status=400)
