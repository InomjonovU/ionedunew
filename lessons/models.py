import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from subjects.models import Subject


YOUTUBE_PATTERNS = [
    re.compile(r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/)([A-Za-z0-9_-]{11})'),
]


def extract_youtube_id(url: str) -> str | None:
    """YouTube URL-dan video ID ni ajratib olish."""
    if not url:
        return None
    url = url.strip()
    for pattern in YOUTUBE_PATTERNS:
        m = pattern.search(url)
        if m:
            return m.group(1)
    # Oddiy ID kiritilgan bo'lishi mumkin
    if re.fullmatch(r'[A-Za-z0-9_-]{11}', url):
        return url
    return None


class Quarter(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='quarters',
        verbose_name='Fan',
    )
    grade = models.PositiveSmallIntegerField(
        choices=[(i, f'{i}-sinf') for i in range(1, 12)],
        verbose_name='Sinf',
    )
    number = models.PositiveSmallIntegerField(
        choices=[(i, f'{i}-chorak') for i in range(1, 5)],
        verbose_name='Chorak',
    )
    title = models.CharField(max_length=200, blank=True, verbose_name='Sarlavha')

    class Meta:
        verbose_name = 'Chorak'
        verbose_name_plural = 'Choraklar'
        unique_together = ('subject', 'grade', 'number')
        ordering = ['grade', 'subject', 'number']

    def __str__(self):
        return f'{self.subject.name} | {self.grade}-sinf | {self.number}-chorak'


class Lesson(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Fan',
    )
    grade = models.PositiveSmallIntegerField(
        choices=[(i, f'{i}-sinf') for i in range(1, 12)],
        verbose_name='Sinf',
    )
    quarter = models.ForeignKey(
        Quarter,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Chorak',
    )
    title = models.CharField(max_length=255, verbose_name='Dars sarlavhasi')
    slug = models.SlugField(max_length=255, unique=True, verbose_name='Slug')
    description = models.TextField(blank=True, verbose_name='Tavsif')
    youtube_url = models.URLField(
        blank=True,
        verbose_name='YouTube video havolasi',
        help_text="YouTube video URL (masalan: https://youtube.com/watch?v=XXXXXXXXXXX yoki https://youtu.be/XXXXXXXXXXX)",
    )
    # Eski fieldlar — orqaga mosligi uchun qoldiriladi (keyin migratsiyalar orqali olib tashlash mumkin)
    video_url = models.URLField(blank=True, verbose_name='Eski video URL (ishlatilmaydi)')
    video_file = models.FileField(
        upload_to='lesson_videos/',
        null=True, blank=True,
        verbose_name='Eski video fayl (ishlatilmaydi)',
    )
    video_provider = models.CharField(
        max_length=15,
        default='youtube',
        blank=True,
        verbose_name='Video manbai',
    )
    pdf_conspect = models.FileField(
        upload_to='conspects/',
        null=True,
        blank=True,
        verbose_name='PDF konspekt',
    )
    thumbnail = models.ImageField(
        upload_to='lesson_thumbnails/',
        null=True,
        blank=True,
        verbose_name='Muqova rasmi',
    )
    duration_minutes = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name='Davomiyligi (daqiqa)',
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Tartib')
    is_published = models.BooleanField(default=True, verbose_name='Chop etilgan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dars'
        verbose_name_plural = 'Darslar'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f'{self.subject.name} | {self.grade}-sinf | {self.title}'

    # ── YouTube helpers ─────────────────────────────────────
    @property
    def youtube_id(self) -> str | None:
        return extract_youtube_id(self.youtube_url)

    @property
    def youtube_embed_url(self) -> str:
        vid = self.youtube_id
        if not vid:
            return ''
        return f'https://www.youtube.com/embed/{vid}?rel=0&modestbranding=1'

    @property
    def youtube_thumbnail_url(self) -> str:
        vid = self.youtube_id
        if not vid:
            return ''
        return f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg'

    def clean(self):
        super().clean()
        if self.youtube_url and not extract_youtube_id(self.youtube_url):
            raise ValidationError({
                'youtube_url': "Yaroqsiz YouTube havolasi. Namuna: https://youtube.com/watch?v=dQw4w9WgXcQ"
            })


class LessonView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_views',
        verbose_name='Foydalanuvchi',
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name='Dars',
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False, verbose_name="To'liq ko'rildi")

    class Meta:
        verbose_name = 'Dars ko\'rish'
        verbose_name_plural = 'Dars ko\'rishlar'
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f'{self.user} → {self.lesson.title}'


class LessonComment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_comments',
        verbose_name='Foydalanuvchi',
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Dars',
    )
    text = models.TextField(verbose_name='Izoh matni')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dars izohi'
        verbose_name_plural = 'Dars izohlari'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} — {self.lesson.title}: {self.text[:50]}'
