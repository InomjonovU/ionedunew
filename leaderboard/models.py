from django.conf import settings
from django.db import models


class Badge(models.Model):
    BADGE_TYPE_CHOICES = [
        ('lessons_5', '5 ta dars ko\'rildi'),
        ('lessons_20', '20 ta dars ko\'rildi'),
        ('lessons_50', '50 ta dars ko\'rildi'),
        ('first_test', 'Birinchi test topshirildi'),
        ('first_certificate', 'Birinchi sertifikat'),
        ('perfect_score', "100% ball (mukammal natija)"),
        ('streak_7', '7 kun ketma-ket'),
        ('all_subjects', "Barcha fanlardan test o'tildi"),
    ]

    badge_type = models.CharField(
        max_length=20,
        choices=BADGE_TYPE_CHOICES,
        unique=True,
        verbose_name='Badge turi',
    )
    name = models.CharField(max_length=100, verbose_name='Nomi')
    description = models.CharField(max_length=300, verbose_name='Tavsifi')
    icon = models.CharField(
        max_length=50,
        default='bi-award',
        verbose_name='Bootstrap Icons class',
    )
    color = models.CharField(
        max_length=7,
        default='#1A6FD4',
        verbose_name='Rang (hex)',
    )

    class Meta:
        verbose_name = 'Badge'
        verbose_name_plural = 'Badgelar'

    def __str__(self):
        return self.name


class UserBadge(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='badges',
        verbose_name='Foydalanuvchi',
    )
    badge = models.ForeignKey(
        Badge,
        on_delete=models.CASCADE,
        related_name='earned_by',
        verbose_name='Badge',
    )
    earned_at = models.DateTimeField(auto_now_add=True, verbose_name='Olingan sana')

    class Meta:
        verbose_name = 'Foydalanuvchi badgesi'
        verbose_name_plural = 'Foydalanuvchi badgelari'
        unique_together = ('user', 'badge')
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.user} | {self.badge.name}'
