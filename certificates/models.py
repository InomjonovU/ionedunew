import uuid

from django.conf import settings
from django.db import models

from quizzes.models import Quiz, QuizAttempt


class Certificate(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='UUID',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name='Foydalanuvchi',
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name='Test',
    )
    attempt = models.OneToOneField(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name='certificate',
        verbose_name='Test urinishi',
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Ball (%)',
    )
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name='Berilgan sana')

    class Meta:
        verbose_name = 'Sertifikat'
        verbose_name_plural = 'Sertifikatlar'
        ordering = ['-issued_at']

    def __str__(self):
        return f'{self.user} | {self.quiz.title} | {self.score}%'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('certificates:view', kwargs={'uuid': self.uuid})
