from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Lesson, LessonComment, LessonView, Quarter


@admin.register(Quarter)
class QuarterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'grade', 'number', 'title', 'lessons_count')
    list_display_links = ('subject',)
    list_filter = ('subject', 'grade', 'number')
    search_fields = ('title', 'subject__name')
    list_per_page = 30
    ordering = ('grade', 'subject', 'number')

    fieldsets = (
        (None, {
            'fields': ('subject', 'grade', 'number', 'title'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject').annotate(_lessons=Count('lessons'))

    @admin.display(description='Darslar soni', ordering='_lessons')
    def lessons_count(self, obj):
        return obj._lessons


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'subject', 'grade', 'quarter_number',
        'youtube_badge', 'duration_minutes', 'order', 'is_published',
    )
    list_display_links = ('title',)
    list_filter = ('is_published', 'subject', 'grade', 'quarter__number')
    search_fields = ('title', 'description', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('order', 'is_published')
    list_per_page = 30
    autocomplete_fields = ('subject', 'quarter')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'youtube_preview')

    fieldsets = (
        ('Asosiy', {
            'fields': ('title', 'slug', 'description'),
        }),
        ('Tasnif', {
            'fields': ('subject', 'grade', 'quarter', 'order'),
        }),
        ('YouTube video', {
            'fields': ('youtube_url', 'youtube_preview', 'duration_minutes'),
            'description': 'Video faqat YouTube orqali yuklanadi. Havolani to\'liq kiriting.',
        }),
        ('Qo\'shimcha materiallar', {
            'fields': ('pdf_conspect', 'thumbnail'),
            'classes': ('collapse',),
        }),
        ('Sozlamalar', {
            'fields': ('is_published', 'created_at', 'updated_at'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('subject', 'quarter')

    @admin.display(description='Chorak', ordering='quarter__number')
    def quarter_number(self, obj):
        return f'{obj.quarter.number}-chorak' if obj.quarter else '—'

    @admin.display(description='Video')
    def youtube_badge(self, obj):
        if obj.youtube_id:
            return format_html(
                '<span style="background:#FEF2F2;color:#B91C1C;padding:2px 8px;border-radius:4px;font-size:.75rem;font-weight:600;">'
                '<i class="bi bi-youtube"></i> YouTube</span>'
            )
        return format_html(
            '<span style="background:#FFFBEB;color:#92400E;padding:2px 8px;border-radius:4px;font-size:.75rem;">'
            'Video yo\'q</span>'
        )

    @admin.display(description='Video preview')
    def youtube_preview(self, obj):
        if not obj.youtube_id:
            return '— (YouTube URL kiritilmagan)'
        return format_html(
            '<div style="max-width:480px;"><div style="position:relative;padding-top:56.25%;border-radius:8px;overflow:hidden;">'
            '<iframe src="{}" style="position:absolute;inset:0;width:100%;height:100%;border:0;" allowfullscreen></iframe>'
            '</div><div style="margin-top:6px;font-size:.8rem;color:#64748B;">Video ID: <code>{}</code></div></div>',
            obj.youtube_embed_url,
            obj.youtube_id,
        )


@admin.register(LessonView)
class LessonViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'completed', 'viewed_at')
    list_filter = ('completed', 'viewed_at')
    search_fields = ('user__username', 'user__email', 'lesson__title')
    list_per_page = 50
    date_hierarchy = 'viewed_at'
    autocomplete_fields = ('user', 'lesson')
    readonly_fields = ('viewed_at',)


@admin.register(LessonComment)
class LessonCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'short_text', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'lesson__title')
    list_per_page = 50
    date_hierarchy = 'created_at'
    autocomplete_fields = ('user', 'lesson')
    readonly_fields = ('created_at',)

    @admin.display(description='Izoh')
    def short_text(self, obj):
        return (obj.text[:80] + '…') if len(obj.text) > 80 else obj.text
