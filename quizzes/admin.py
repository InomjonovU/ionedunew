from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import AttemptAnswer, Choice, Question, Quiz, QuizAttempt


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    min_num = 2
    fields = ('text', 'is_correct', 'order')
    verbose_name = "Javob varianti"
    verbose_name_plural = "Javob variantlari (kamida 2 ta, biri to'g'ri belgilangan bo'lsin)"


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    show_change_link = True
    fields = ('question_type', 'text', 'image', 'order', 'score')
    classes = ('collapse',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'type_badge', 'related_content',
        'questions_count', 'time_limit', 'pass_score',
        'max_attempts', 'is_published',
    )
    list_display_links = ('title',)
    list_filter = ('quiz_type', 'is_published')
    search_fields = ('title', 'lesson__title', 'quarter__subject__name')
    list_editable = ('is_published',)
    list_per_page = 30
    autocomplete_fields = ('lesson', 'quarter')
    inlines = [QuestionInline]

    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('title', 'quiz_type'),
        }),
        ('Bog\'lanish', {
            'fields': ('lesson', 'quarter'),
            'description': 'Dars testi uchun — "lesson", chorak testi uchun — "quarter" ni tanlang.',
        }),
        ('Sozlamalar', {
            'fields': ('time_limit', 'pass_score', 'max_attempts', 'is_published'),
        }),
    )

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('lesson', 'quarter', 'quarter__subject')
            .annotate(_qcount=Count('questions'))
        )

    @admin.display(description='Savollar', ordering='_qcount')
    def questions_count(self, obj):
        return obj._qcount

    @admin.display(description='Turi')
    def type_badge(self, obj):
        if obj.quiz_type == 'quarter':
            return format_html(
                '<span style="background:#F5F3FF;color:#6D28D9;padding:2px 10px;border-radius:999px;font-size:.72rem;font-weight:600;">'
                '<i class="bi bi-bookmark-star"></i> Chorak</span>'
            )
        return format_html(
            '<span style="background:#EFF6FF;color:#1D4ED8;padding:2px 10px;border-radius:999px;font-size:.72rem;font-weight:600;">'
            '<i class="bi bi-clipboard-check"></i> Dars</span>'
        )

    @admin.display(description='Tegishli')
    def related_content(self, obj):
        if obj.lesson_id:
            return format_html('<small>{}</small>', obj.lesson.title[:40])
        if obj.quarter_id:
            q = obj.quarter
            return format_html('<small>{} · {}-sinf · {}-chorak</small>', q.subject.name, q.grade, q.number)
        return '—'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('short_text', 'quiz', 'question_type', 'order', 'score', 'choices_info')
    list_display_links = ('short_text',)
    list_filter = ('question_type', 'quiz')
    search_fields = ('text', 'quiz__title')
    list_editable = ('order', 'score')
    autocomplete_fields = ('quiz',)
    list_per_page = 40
    inlines = [ChoiceInline]

    @admin.display(description='Savol')
    def short_text(self, obj):
        return (obj.text[:70] + '…') if len(obj.text) > 70 else obj.text

    @admin.display(description='Variantlar')
    def choices_info(self, obj):
        total = obj.choices.count()
        correct = obj.choices.filter(is_correct=True).count()
        color = '#10B981' if correct == 1 else '#EF4444'
        return format_html(
            '<span style="color:{}">{} / {} (to\'g\'ri: {})</span>', color, total, total, correct
        )


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'quiz', 'score_badge', 'correct_count', 'total_questions',
        'pass_badge', 'is_completed', 'started_at',
    )
    list_filter = ('is_passed', 'is_completed', 'quiz__quiz_type', 'started_at')
    search_fields = ('user__username', 'user__email', 'quiz__title')
    readonly_fields = ('started_at', 'finished_at', 'score', 'correct_count', 'total_questions', 'is_passed')
    autocomplete_fields = ('user', 'quiz')
    date_hierarchy = 'started_at'
    list_per_page = 50

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'quiz')

    @admin.display(description='Ball', ordering='score')
    def score_badge(self, obj):
        if obj.score is None:
            return '—'
        color = '#10B981' if obj.is_passed else '#EF4444'
        return format_html('<strong style="color:{};">{}%</strong>', color, obj.score)

    @admin.display(description='Natija')
    def pass_badge(self, obj):
        if not obj.is_completed:
            return format_html('<span style="color:#64748B;">Yakunlanmagan</span>')
        if obj.is_passed:
            return format_html('<span style="color:#10B981;font-weight:600;">✓ O\'tildi</span>')
        return format_html('<span style="color:#EF4444;font-weight:600;">✗ O\'tilmadi</span>')


@admin.register(AttemptAnswer)
class AttemptAnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question_short', 'selected_choice', 'is_correct_display')
    list_filter = ('attempt__quiz',)
    search_fields = ('attempt__user__username', 'question__text')
    raw_id_fields = ('attempt', 'question', 'selected_choice')
    list_per_page = 50

    @admin.display(description='Savol')
    def question_short(self, obj):
        return obj.question.text[:60]

    @admin.display(description='To\'g\'rimi', boolean=True)
    def is_correct_display(self, obj):
        return bool(obj.selected_choice and obj.selected_choice.is_correct)
