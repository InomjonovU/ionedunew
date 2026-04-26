import json

import anthropic
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from lessons.models import Lesson

from .forms import AIEssayForm
from .models import (
    AIConversation,
    AIEssayCheck,
    AILessonSummary,
    AIMessage,
    AIRecommendation,
)

LANGUAGE_PROMPTS = {
    'uz': "O'zbek tilida javob ber.",
    'ru': 'Отвечай на русском языке.',
    'en': 'Answer in English.',
}


def _get_client():
    return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)


def _premium_required(request):
    """Returns JsonResponse or redirect if user is not premium."""
    if not request.user.is_premium:
        return JsonResponse({'error': 'premium_required', 'message': 'Bu funksiya faqat premium foydalanuvchilar uchun.'}, status=403)
    return None


@login_required
@require_POST
def chat_ajax(request):
    """Dars sahifasidagi AI chatbot (AJAX). Faqat premium foydalanuvchilar."""
    denied = _premium_required(request)
    if denied:
        return denied
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_message = data.get('message', '').strip()
    conversation_id = data.get('conversation_id')
    lesson_id = data.get('lesson_id')

    if not user_message or len(user_message) > 1000:
        return JsonResponse({'error': 'invalid message'}, status=400)

    # Suhbatni topish yoki yaratish
    if conversation_id:
        conversation = get_object_or_404(
            AIConversation, pk=conversation_id, user=request.user
        )
    else:
        lesson_title = ''
        if lesson_id:
            lesson = Lesson.objects.filter(pk=lesson_id).first()
            lesson_title = lesson.title if lesson else ''
        conversation = AIConversation.objects.create(
            user=request.user,
            lesson_id=lesson_id,
            lesson_title=lesson_title,
        )

    # Foydalanuvchi xabarini saqlash
    AIMessage.objects.create(
        conversation=conversation, role='user', content=user_message
    )

    # Kontekst: oxirgi 10 ta xabar
    history = list(
        conversation.messages.order_by('-created_at')
        .values('role', 'content')[:10]
    )
    history.reverse()

    lang = request.user.language
    system_prompt = (
        f"Sen EduSphere ta'lim platformasining AI yordamchisisisan. "
        f"1–11 sinf o'quvchilariga yordam berasan. "
        f"{LANGUAGE_PROMPTS.get(lang, '')}"
    )
    if conversation.lesson_title:
        system_prompt += f" Hozirgi dars mavzusi: {conversation.lesson_title}."

    messages = [{'role': m['role'], 'content': m['content']} for m in history]

    client = _get_client()
    response = client.messages.create(
        model=settings.CLAUDE_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    ai_text = response.content[0].text

    # AI javobini saqlash
    AIMessage.objects.create(
        conversation=conversation, role='assistant', content=ai_text
    )

    return JsonResponse({
        'reply': ai_text,
        'conversation_id': conversation.pk,
    })


@login_required
def lesson_summary_view(request, lesson_pk):
    if not request.user.is_premium:
        return JsonResponse({'error': 'premium_required', 'message': 'Bu funksiya faqat premium foydalanuvchilar uchun.'}, status=403)
    """Dars AI xulosasini qaytarish yoki yaratish."""
    lesson = get_object_or_404(Lesson, pk=lesson_pk, is_published=True)

    summary_obj = AILessonSummary.objects.filter(lesson_id=lesson.pk).first()

    if not summary_obj:
        lang = request.user.language
        prompt = (
            f"Quyidagi dars mavzusini qisqacha xulosala va asosiy atamalarni ajrat.\n"
            f"Dars: {lesson.title}\n"
            f"Tavsif: {lesson.description or '(mavjud emas)'}\n"
            f"{LANGUAGE_PROMPTS.get(lang, '')}\n"
            f"Format: avval qisqa xulosa (3-5 gap), so'ng 'Asosiy atamalar:' bo'limi."
        )
        client = _get_client()
        resp = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=512,
            messages=[{'role': 'user', 'content': prompt}],
        )
        summary_text = resp.content[0].text
        summary_obj = AILessonSummary.objects.create(
            lesson_id=lesson.pk,
            lesson_title=lesson.title,
            summary=summary_text,
        )

    return JsonResponse({'summary': summary_obj.summary})


@login_required
def essay_check_view(request):
    if not request.user.is_premium:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.warning(request, 'Bu funksiya faqat premium foydalanuvchilar uchun.')
        return redirect('accounts:dashboard')
    form = AIEssayForm(request.POST or None)
    result = None

    if form.is_valid():
        text = form.cleaned_data['text']
        lang = form.cleaned_data['language']
        prompt = (
            f"Quyidagi matnni tekshir: grammatika, uslub va mantiq.\n"
            f"Matn ({lang}):\n{text}\n\n"
            f"Javobni shu tilda ber: {LANGUAGE_PROMPTS.get(lang, '')}\n"
            f"Format: 1) Umumiy baho (0-100), 2) Kamchiliklar, 3) Tavsiyalar."
        )
        client = _get_client()
        resp = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=1024,
            messages=[{'role': 'user', 'content': prompt}],
        )
        feedback = resp.content[0].text
        AIEssayCheck.objects.create(
            user=request.user,
            original_text=text,
            feedback=feedback,
        )
        result = feedback

    return render(request, 'ai_modules/essay_check.html', {'form': form, 'result': result})


@login_required
def recommendations_view(request):
    """Foydalanuvchiga shaxsiy tavsiyalar. Faqat premium uchun."""
    if not request.user.is_premium:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.warning(request, 'Bu funksiya faqat premium foydalanuvchilar uchun.')
        return redirect('accounts:dashboard')
    rec = AIRecommendation.objects.filter(user=request.user).first()

    # Agar tavsiya 24 soatdan eski bo'lsa yoki yo'q bo'lsa, yangilaymiz
    from django.utils import timezone
    from datetime import timedelta

    needs_update = (
        rec is None or
        (timezone.now() - rec.generated_at) > timedelta(hours=24)
    )

    if needs_update:
        from quizzes.models import QuizAttempt
        # Oxirgi yomon natijalar
        weak_attempts = (
            QuizAttempt.objects
            .filter(user=request.user, is_completed=True, score__lt=80)
            .select_related('quiz__lesson__subject')
            .order_by('-started_at')[:5]
        )
        weak_topics = [a.quiz.title for a in weak_attempts]

        lang = request.user.language
        prompt = (
            f"O'quvchi ushbu mavzularda zaif natija ko'rsatdi: {', '.join(weak_topics) or 'ma\'lumot yo\'q'}.\n"
            f"Qaysi mavzularni qayta o'rganishi kerakligini tavsiya qil (3-5 ta).\n"
            f"{LANGUAGE_PROMPTS.get(lang, '')}"
        )
        client = _get_client()
        resp = client.messages.create(
            model=settings.CLAUDE_MODEL,
            max_tokens=512,
            messages=[{'role': 'user', 'content': prompt}],
        )
        reasoning = resp.content[0].text

        if rec:
            rec.reasoning = reasoning
            rec.save(update_fields=['reasoning', 'generated_at'])
        else:
            rec = AIRecommendation.objects.create(
                user=request.user,
                reasoning=reasoning,
            )

    return render(request, 'ai_modules/recommendations.html', {'recommendation': rec})
