from django.db import models


class Subject(models.Model):
    COLOR_CHOICES = [
        ('blue', "Ko'k"),
        ('red', 'Qizil'),
        ('green', 'Yashil'),
    ]

    name = models.CharField(max_length=100, verbose_name='Fan nomi')
    slug = models.SlugField(unique=True, verbose_name='Slug')
    color = models.CharField(
        max_length=10,
        choices=COLOR_CHOICES,
        default='blue',
        verbose_name='Rang',
    )
    icon = models.CharField(
        max_length=50,
        default='bi-book',
        verbose_name='Bootstrap Icons class',
        help_text='Masalan: bi-calculator, bi-globe',
    )
    description = models.TextField(blank=True, verbose_name='Tavsif')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Tartib')
    is_active = models.BooleanField(default=True, verbose_name='Faol')

    class Meta:
        verbose_name = 'Fan'
        verbose_name_plural = 'Fanlar'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_color_hex(self):
        mapping = {
            'blue': '#1A6FD4',
            'red': '#E63946',
            'green': '#2ABD6E',
        }
        return mapping.get(self.color, '#1A6FD4')

    def get_bg_color_hex(self):
        mapping = {
            'blue': '#EAF2FD',
            'red': '#FDEAEA',
            'green': '#E8FAF1',
        }
        return mapping.get(self.color, '#EAF2FD')
