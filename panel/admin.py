from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'use_real_stats', 'updated_at')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('Manba', {
            'fields': ('use_real_stats',),
            'description': "Yoqilganda hero bo'limidagi raqamlar bazadan hisoblanadi. O'chirilganda quyidagi qo'lda kiritilgan qiymatlar ishlatiladi.",
        }),
        ('Hero statistikasi (qo\'lda)', {
            'fields': (
                'students_count', 'active_students_count',
                'video_lessons_count', 'subjects_count',
                'certificates_count', 'test_questions_count',
                'grades_count', 'average_rating',
            ),
        }),
        ('Tizim', {
            'fields': ('updated_at',),
        }),
    )

    def has_add_permission(self, request):
        # Singleton — faqat bitta yozuv bo'ladi
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
