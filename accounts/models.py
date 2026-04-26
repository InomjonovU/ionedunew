from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    GRADE_CHOICES = [(i, f'{i}-sinf') for i in range(1, 12)]
    LANGUAGE_CHOICES = [
        ('uz', "O'zbek"),
        ('ru', 'Rus'),
        ('en', 'Ingliz'),
    ]

    grade = models.PositiveSmallIntegerField(
        choices=GRADE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Sinf',
    )
    language = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        default='uz',
        verbose_name='Til',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Avatar',
    )
    total_score = models.PositiveIntegerField(default=0, verbose_name='Umumiy ball')
    bio = models.TextField(blank=True, verbose_name="Qisqacha ma'lumot")

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return self.get_full_name() or self.username

    def get_grade_label(self):
        return f'{self.grade}-sinf' if self.grade else ''
