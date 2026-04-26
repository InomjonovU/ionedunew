from django.contrib import admin
from django.utils.html import format_html

from .models import Badge, UserBadge


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('icon_preview', 'name', 'badge_type', 'color_preview', 'users_count')
    list_display_links = ('name',)
    list_filter = ('badge_type',)
    search_fields = ('name', 'description')
    list_per_page = 30

    fieldsets = (
        (None, {
            'fields': ('name', 'badge_type', 'description'),
        }),
        ('Ko\'rinish', {
            'fields': ('icon', 'color'),
            'description': "Bootstrap Icons class nomi, masalan: bi-award-fill",
        }),
    )

    @admin.display(description='Ikon')
    def icon_preview(self, obj):
        return format_html(
            '<i class="bi {}" style="font-size:1.3rem;color:{};"></i>',
            obj.icon, obj.color or '#64748B',
        )

    @admin.display(description='Rang')
    def color_preview(self, obj):
        if not obj.color:
            return '—'
        return format_html(
            '<span style="display:inline-block;width:16px;height:16px;border-radius:4px;background:{};border:1px solid #ddd;vertical-align:middle;"></span> <code>{}</code>',
            obj.color, obj.color,
        )

    @admin.display(description='Olganlar')
    def users_count(self, obj):
        return obj.user_badges.count() if hasattr(obj, 'user_badges') else '—'


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at')
    list_filter = ('badge', 'earned_at')
    search_fields = ('user__username', 'user__email', 'badge__name')
    autocomplete_fields = ('user', 'badge')
    readonly_fields = ('earned_at',)
    date_hierarchy = 'earned_at'
    list_per_page = 50
