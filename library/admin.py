from django.contrib import admin
from django.utils.html import format_html

from .models import LibraryItem, LibraryItemView


@admin.register(LibraryItem)
class LibraryItemAdmin(admin.ModelAdmin):
    list_display = (
        'cover_thumb', 'title', 'author', 'subject', 'grade_display',
        'type_badge', 'view_count', 'download_count', 'is_published',
    )
    list_display_links = ('title',)
    list_filter = ('is_published', 'item_type', 'subject', 'grade')
    search_fields = ('title', 'author', 'description')
    list_editable = ('is_published',)
    list_per_page = 30
    autocomplete_fields = ('subject',)
    readonly_fields = ('view_count', 'download_count', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Asosiy', {
            'fields': ('title', 'author', 'description'),
        }),
        ('Tasnif', {
            'fields': ('subject', 'grade', 'item_type'),
        }),
        ('Fayllar', {
            'fields': ('file', 'cover_image'),
        }),
        ('Statistika', {
            'fields': ('view_count', 'download_count', 'created_at'),
            'classes': ('collapse',),
        }),
        ('Sozlamalar', {
            'fields': ('is_published',),
        }),
    )

    TYPE_COLORS = {
        'pdf_book': ('#EFF6FF', '#1D4ED8'),
        'audio_book': ('#F5F3FF', '#6D28D9'),
        'textbook': ('#ECFDF5', '#047857'),
        'material': ('#FFFBEB', '#92400E'),
    }

    @admin.display(description='Muqova')
    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="width:40px;height:52px;object-fit:cover;border-radius:4px;border:1px solid #e2e8f0;">',
                obj.cover_image.url,
            )
        return format_html(
            '<div style="width:40px;height:52px;background:#f1f5f9;border-radius:4px;display:inline-flex;align-items:center;justify-content:center;color:#94a3b8;">'
            '<i class="bi bi-book"></i></div>'
        )

    @admin.display(description='Sinf', ordering='grade')
    def grade_display(self, obj):
        return f'{obj.grade}-sinf' if obj.grade else '—'

    @admin.display(description='Tur')
    def type_badge(self, obj):
        bg, fg = self.TYPE_COLORS.get(obj.item_type, ('#F1F5F9', '#334155'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:999px;font-size:.72rem;font-weight:600;">{}</span>',
            bg, fg, obj.get_item_type_display(),
        )


@admin.register(LibraryItemView)
class LibraryItemViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'downloaded', 'viewed_at')
    list_filter = ('downloaded', 'viewed_at')
    search_fields = ('user__username', 'item__title')
    autocomplete_fields = ('user', 'item')
    readonly_fields = ('viewed_at',)
    date_hierarchy = 'viewed_at'
    list_per_page = 50
