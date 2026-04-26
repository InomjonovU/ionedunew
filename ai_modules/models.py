from django.conf import settings
from django.db import models


class AIConversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_conversations',
        verbose_name='Foydalanuvchi',
    )
    # Dars sahifasidagi chatbot uchun (ixtiyoriy)
    lesson_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Dars ID',
    )
    lesson_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Dars sarlavhasi (kontekst)',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'AI suhbat'
        verbose_name_plural = 'AI suhbatlar'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.user} | suhbat #{self.pk}'

    def message_count(self):
        return self.messages.count()


class AIMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'Foydalanuvchi'),
        ('assistant', 'AI'),
    ]

    conversation = models.ForeignKey(
        AIConversation,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Suhbat',
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        verbose_name='Rol',
    )
    content = models.TextField(verbose_name='Matn')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'AI xabar'
        verbose_name_plural = 'AI xabarlar'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role}: {self.content[:60]}'


class AIEssayCheck(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='essay_checks',
        verbose_name='Foydalanuvchi',
    )
    original_text = models.TextField(verbose_name="Asl matn")
    feedback = models.TextField(blank=True, verbose_name='AI tahlili')
    grammar_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Grammatika bali (0-100)',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Insho tekshiruvi'
        verbose_name_plural = 'Insho tekshiruvlari'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} | {self.created_at.date()}'


class AILessonSummary(models.Model):
    lesson_id = models.PositiveIntegerField(unique=True, verbose_name='Dars ID')
    lesson_title = models.CharField(max_length=255, verbose_name='Dars sarlavhasi')
    summary = models.TextField(verbose_name='AI xulosasi')
    key_terms = models.TextField(
        blank=True,
        verbose_name='Asosiy atamalar (JSON)',
        help_text='JSON formatida: ["atama1", "atama2"]',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dars AI xulosasi'
        verbose_name_plural = 'Dars AI xulosalari'

    def __str__(self):
        return f'Xulosa: {self.lesson_title}'


class AIRecommendation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ai_recommendations',
        verbose_name='Foydalanuvchi',
    )
    # Tavsiya etilgan dars ID lari (JSON list)
    recommended_lesson_ids = models.TextField(
        default='[]',
        verbose_name='Tavsiya etilgan darslar (JSON)',
    )
    reasoning = models.TextField(blank=True, verbose_name='Sabab')
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'AI tavsiya'
        verbose_name_plural = 'AI tavsiyalar'

    def __str__(self):
        return f'{self.user} uchun tavsiyalar'
