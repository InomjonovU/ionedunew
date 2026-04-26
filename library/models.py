from django.conf import settings
from django.db import models

from subjects.models import Subject


class LibraryItem(models.Model):
    ITEM_TYPE_CHOICES = [
        ('pdf_book', 'PDF kitob'),
        ('audio_book', 'Audio kitob'),
        ('textbook', 'Darslik'),
        ('material', "Qo'shimcha material"),
    ]

    title = models.CharField(max_length=255, verbose_name='Sarlavha')
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='library_items',
        verbose_name='Fan',
    )
    grade = models.PositiveSmallIntegerField(
        choices=[(i, f'{i}-sinf') for i in range(1, 12)],
        null=True,
        blank=True,
        verbose_name='Sinf',
    )
    author = models.CharField(max_length=200, blank=True, verbose_name='Muallif')
    item_type = models.CharField(
        max_length=15,
        choices=ITEM_TYPE_CHOICES,
        default='pdf_book',
        verbose_name='Tur',
    )
    file = models.FileField(
        upload_to='library/',
        null=True,
        blank=True,
        verbose_name='Fayl',
    )
    cover_image = models.ImageField(
        upload_to='library_covers/',
        null=True,
        blank=True,
        verbose_name='Muqova',
    )
    description = models.TextField(blank=True, verbose_name='Tavsif')
    view_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rish soni")
    download_count = models.PositiveIntegerField(default=0, verbose_name='Yuklab olish soni')
    is_published = models.BooleanField(default=True, verbose_name='Chop etilgan')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kutubxona materiali'
        verbose_name_plural = 'Kutubxona materiallari'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class LibraryItemView(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='library_views',
        verbose_name='Foydalanuvchi',
    )
    item = models.ForeignKey(
        LibraryItem,
        on_delete=models.CASCADE,
        related_name='user_views',
        verbose_name='Material',
    )
    viewed_at = models.DateTimeField(auto_now_add=True)
    downloaded = models.BooleanField(default=False, verbose_name='Yuklab olindi')

    class Meta:
        verbose_name = "Materialga kirish"
        verbose_name_plural = "Materiallarga kirishlar"
        unique_together = ('user', 'item')
