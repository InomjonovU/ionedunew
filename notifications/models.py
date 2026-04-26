from django.conf import settings
from django.db import models


class Notification(models.Model):
    TYPE_CHOICES = [
        ('new_lesson', 'Yangi dars'),
        ('test_result', 'Test natijasi'),
        ('certificate', 'Sertifikat'),
        ('system', 'Tizim xabari'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Foydalanuvchi',
    )
    notification_type = models.CharField(
        max_length=15,
        choices=TYPE_CHOICES,
        verbose_name='Tur',
    )
    title = models.CharField(max_length=255, verbose_name='Sarlavha')
    message = models.TextField(verbose_name='Xabar matni')
    is_read = models.BooleanField(default=False, verbose_name="O'qildi")
    created_at = models.DateTimeField(auto_now_add=True)

    # Ixtiyoriy havolalar
    related_lesson_id = models.PositiveIntegerField(null=True, blank=True)
    related_quiz_id = models.PositiveIntegerField(null=True, blank=True)
    related_certificate_id = models.PositiveIntegerField(null=True, blank=True)
    action_url = models.CharField(max_length=300, blank=True, verbose_name='Havola')

    class Meta:
        verbose_name = 'Bildirishnoma'
        verbose_name_plural = 'Bildirishnomalar'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} | {self.title}'

    def get_icon(self):
        icons = {
            'new_lesson': 'bi-play-circle',
            'test_result': 'bi-clipboard-check',
            'certificate': 'bi-award',
            'system': 'bi-info-circle',
        }
        return icons.get(self.notification_type, 'bi-bell')
