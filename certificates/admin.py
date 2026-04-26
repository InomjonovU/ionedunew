from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz', 'score_display', 'issued_at', 'view_link')
    list_filter = ('quiz__quiz_type', 'issued_at')
    search_fields = ('user__username', 'user__email', 'quiz__title', 'uuid')
    readonly_fields = ('uuid', 'issued_at', 'view_link')
    autocomplete_fields = ('user', 'quiz', 'attempt')
    date_hierarchy = 'issued_at'
    list_per_page = 50

    fieldsets = (
        ('Sertifikat', {
            'fields': ('uuid', 'user', 'quiz', 'attempt', 'score'),
        }),
        ('Vaqt', {
            'fields': ('issued_at', 'view_link'),
        }),
    )

    @admin.display(description='Ball', ordering='score')
    def score_display(self, obj):
        return format_html('<strong style="color:#10B981;">{}%</strong>', obj.score)

    @admin.display(description='Havola')
    def view_link(self, obj):
        try:
            url = reverse('certificates:detail', args=[obj.uuid])
            return format_html('<a href="{}" target="_blank"><i class="bi bi-box-arrow-up-right"></i> Ochish</a>', url)
        except Exception:
            return '—'
