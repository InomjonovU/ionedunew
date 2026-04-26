from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        'color_badge', 'name', 'slug', 'icon_preview',
        'lessons_count', 'order', 'is_active',
    )
    list_display_links = ('name',)
    list_filter = ('is_active', 'color')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    list_per_page = 25
    ordering = ('order', 'name')

    fieldsets = (
        ('Asosiy ma\'lumot', {
            'fields': ('name', 'slug', 'description'),
        }),
        ('Ko\'rinish', {
            'fields': ('color', 'icon'),
            'description': 'Bootstrap Icons class nomi (masalan: bi-calculator). Ro\'yxat: https://icons.getbootstrap.com/',
        }),
        ('Sozlamalar', {
            'fields': ('order', 'is_active'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_lessons=Count('lessons'))

    @admin.display(description='Darslar', ordering='_lessons')
    def lessons_count(self, obj):
        return obj._lessons

    @admin.display(description='Rang')
    def color_badge(self, obj):
        return format_html(
            '<span style="display:inline-block;width:16px;height:16px;border-radius:4px;background:{};border:1px solid #ddd;vertical-align:middle;"></span>',
            obj.get_color_hex(),
        )

    @admin.display(description='Ikon')
    def icon_preview(self, obj):
        return format_html(
            '<code style="font-size:.8rem;background:#f1f5f9;padding:2px 6px;border-radius:4px;">{}</code>',
            obj.icon,
        )
