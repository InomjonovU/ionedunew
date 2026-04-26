from django.db import models


class SiteSettings(models.Model):
    """Sayt statistikasi va sozlamalari — admin paneldan boshqariladi."""

    # Hero section stats
    students_count = models.CharField(
        max_length=50, default='0',
        verbose_name="O'quvchilar soni",
        help_text="Masalan: 10,000+",
    )
    video_lessons_count = models.CharField(
        max_length=50, default='0',
        verbose_name='Video darslar soni',
        help_text="Masalan: 800+",
    )
    subjects_count = models.CharField(
        max_length=50, default='0',
        verbose_name='Fanlar soni',
        help_text="Masalan: 15+",
    )
    certificates_count = models.CharField(
        max_length=50, default='0',
        verbose_name='Sertifikatlar soni',
        help_text="Masalan: 4,200+",
    )
    active_students_count = models.CharField(
        max_length=50, default='0',
        verbose_name='Faol o\'quvchilar',
        help_text="Masalan: 10K+",
    )
    average_rating = models.CharField(
        max_length=20, default='4.9',
        verbose_name="O'rtacha baho",
        help_text="Masalan: 4.9",
    )
    test_questions_count = models.CharField(
        max_length=50, default='0',
        verbose_name='Test savollari soni',
        help_text="Masalan: 1,200+",
    )
    grades_count = models.CharField(
        max_length=20, default='11',
        verbose_name='Sinf darslari soni',
        help_text="Masalan: 11",
    )

    # Statistika manbasini tanlash
    use_real_stats = models.BooleanField(
        default=False,
        verbose_name='Haqiqiy statistikani ishlatish',
        help_text="Yoqilganda bazadagi haqiqiy raqamlar ko'rsatiladi",
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sayt sozlamalari'
        verbose_name_plural = 'Sayt sozlamalari'

    def __str__(self):
        return 'Sayt sozlamalari'

    def save(self, *args, **kwargs):
        # Singleton pattern — faqat bitta yozuv bo'lishi kerak
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
