from django.conf import settings
from django.db import models

from lessons.models import Lesson, Quarter


class Quiz(models.Model):
    QUIZ_TYPE_CHOICES = [
        ('lesson', 'Dars testi'),
        ('quarter', 'Chorak testi'),
    ]

    title = models.CharField(max_length=255, verbose_name='Test sarlavhasi')
    quiz_type = models.CharField(
        max_length=10,
        choices=QUIZ_TYPE_CHOICES,
        verbose_name='Test turi',
    )
    # Dars testi uchun
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quiz',
        verbose_name='Dars',
    )
    # Chorak testi uchun
    quarter = models.OneToOneField(
        Quarter,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='quiz',
        verbose_name='Chorak',
    )
    time_limit = models.PositiveSmallIntegerField(
        verbose_name='Vaqt chegarasi (daqiqa)',
        help_text='0 = vaqt chegarasi yo\'q',
        default=0,
    )
    pass_score = models.PositiveSmallIntegerField(
        default=70,
        verbose_name="O'tish bali (%)",
    )
    max_attempts = models.PositiveSmallIntegerField(
        default=3,
        verbose_name="Maksimal urinishlar soni",
        help_text="Necha marta test ishlash mumkin (0 = cheksiz)",
    )
    is_published = models.BooleanField(default=True, verbose_name='Chop etilgan')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Test'
        verbose_name_plural = 'Testlar'

    def __str__(self):
        return self.title

    def question_count(self):
        return self.questions.count()

    def is_available_for(self, user):
        """Test foydalanuvchi uchun ochiqmi?

        - Dars testi: tegishli darsning oldingi darslari tugatilgan bo'lishi kerak
          (dars blokirovkasi mantiqi bilan mos).
        - Chorak testi: chorakdagi BARCHA darslar tugatilgan bo'lishi shart.
        """
        if not user.is_authenticated or not self.is_published:
            return False

        from lessons.models import Lesson, LessonView

        if self.quiz_type == 'quarter' and self.quarter_id:
            quarter_lessons = Lesson.objects.filter(
                quarter_id=self.quarter_id, is_published=True
            )
            total = quarter_lessons.count()
            if total == 0:
                return False
            completed = LessonView.objects.filter(
                user=user,
                lesson__in=quarter_lessons,
                completed=True,
            ).count()
            return completed >= total

        if self.quiz_type == 'lesson' and self.lesson_id:
            # Dars testini ochiq qilish uchun darsning o'zi "ochiq" bo'lishi yetarli
            # (ya'ni oldingi darslar tugatilgan). Tekshiramiz:
            lesson = Lesson.objects.filter(pk=self.lesson_id).first()
            if not lesson:
                return False
            prev_lessons = Lesson.objects.filter(
                quarter=lesson.quarter,
                is_published=True,
                order__lt=lesson.order,
            )
            if not prev_lessons.exists():
                return True
            completed = LessonView.objects.filter(
                user=user, lesson__in=prev_lessons, completed=True
            ).count()
            return completed >= prev_lessons.count()

        return False

    def availability_reason(self, user):
        """Agar yopiq bo'lsa, nega yopiq ekanligini ko'rsatadi."""
        if not user.is_authenticated:
            return "Testni ishlash uchun tizimga kiring."
        if not self.is_published:
            return "Test hali chop etilmagan."
        if self.quiz_type == 'quarter' and self.quarter_id:
            from lessons.models import Lesson, LessonView
            quarter_lessons = Lesson.objects.filter(
                quarter_id=self.quarter_id, is_published=True
            )
            total = quarter_lessons.count()
            if total == 0:
                return "Bu chorakda hali darslar yo'q."
            completed = LessonView.objects.filter(
                user=user, lesson__in=quarter_lessons, completed=True
            ).count()
            if completed < total:
                return f"Chorak testini ishlash uchun avval barcha {total} ta darsni tugating. Hozir {completed} ta dars tugatilgan."
        return "Test hozircha mavjud emas."


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('mcq', "Ko'p tanlovli (A/B/C/D)"),
        ('tf', "To'g'ri / Noto'g'ri"),
        ('image', 'Rasm bilan savol'),
    ]

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Test',
    )
    question_type = models.CharField(
        max_length=5,
        choices=QUESTION_TYPE_CHOICES,
        default='mcq',
        verbose_name='Savol turi',
    )
    text = models.TextField(verbose_name='Savol matni')
    image = models.ImageField(
        upload_to='question_images/',
        null=True,
        blank=True,
        verbose_name='Rasm',
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Tartib')
    score = models.PositiveSmallIntegerField(default=1, verbose_name='Ball')

    class Meta:
        verbose_name = 'Savol'
        verbose_name_plural = 'Savollar'
        ordering = ['order']

    def __str__(self):
        return f'{self.quiz.title} | {self.text[:60]}'


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='Savol',
    )
    text = models.CharField(max_length=500, verbose_name='Variant matni')
    is_correct = models.BooleanField(default=False, verbose_name="To'g'ri javob")
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Tartib')

    class Meta:
        verbose_name = 'Variant'
        verbose_name_plural = 'Variantlar'
        ordering = ['order']

    def __str__(self):
        marker = '✓' if self.is_correct else '✗'
        return f'{marker} {self.text[:60]}'


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts',
        verbose_name='Foydalanuvchi',
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='Test',
    )
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Ball (%)',
    )
    correct_count = models.PositiveSmallIntegerField(default=0, verbose_name="To'g'ri javoblar")
    total_questions = models.PositiveSmallIntegerField(default=0, verbose_name='Jami savollar')
    is_passed = models.BooleanField(default=False, verbose_name="O'tildi")
    is_completed = models.BooleanField(default=False, verbose_name='Yakunlandi')

    class Meta:
        verbose_name = 'Test urinishi'
        verbose_name_plural = 'Test urinishlari'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.user} | {self.quiz.title} | {self.score}%'

    def calculate_score(self):
        answers = self.answers.select_related('selected_choice')
        correct = sum(
            1 for a in answers
            if a.selected_choice and a.selected_choice.is_correct
        )
        total = self.quiz.questions.count()
        if total == 0:
            return 0
        self.correct_count = correct
        self.total_questions = total
        self.score = round((correct / total) * 100, 2)
        self.is_passed = self.score >= self.quiz.pass_score
        return self.score


class AttemptAnswer(models.Model):
    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Urinish',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='attempt_answers',
        verbose_name='Savol',
    )
    selected_choice = models.ForeignKey(
        Choice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='selected_in',
        verbose_name='Tanlangan variant',
    )

    class Meta:
        verbose_name = 'Test javobi'
        verbose_name_plural = 'Test javoblari'
        unique_together = ('attempt', 'question')

    def __str__(self):
        is_correct = self.selected_choice and self.selected_choice.is_correct
        return f'{"✓" if is_correct else "✗"} {self.question.text[:40]}'
