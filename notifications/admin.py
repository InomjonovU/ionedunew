from django.contrib import admin
from django.utils.html import format_html

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('type_badge', 'user', 'title', 'read_status', 'created_at')
    list_display_links = ('title',)
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'user__email', 'title', 'message')
    autocomplete_fields = ('user',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 50
    actions = ['mark_as_read', 'mark_as_unread']

    fieldsets = (
        ('Qabul qiluvchi', {
            'fields': ('user', 'notification_type'),
        }),
        ('Matn', {
            'fields': ('title', 'message', 'action_url'),
        }),
        ('Bog\'lanishlar', {
            'fields': ('related_lesson_id', 'related_quiz_id', 'related_certificate_id'),
            'classes': ('collapse',),
        }),
        ('Holat', {
            'fields': ('is_read', 'created_at'),
        }),
    )

    TYPE_META = {
        'new_lesson': ('#EFF6FF', '#1D4ED8', 'bi-play-circle', 'Yangi dars'),
        'test_result': ('#F5F3FF', '#6D28D9', 'bi-clipboard-check', 'Test natijasi'),
        'certificate': ('#FFFBEB', '#92400E', 'bi-award', 'Sertifikat'),
        'system': ('#F1F5F9', '#334155', 'bi-bell', 'Tizim'),
    }

    @admin.display(description='Turi')
    def type_badge(self, obj):
        bg, fg, icon, label = self.TYPE_META.get(obj.notification_type, ('#F1F5F9', '#334155', 'bi-bell', obj.notification_type))
        return format_html(
            '<span style="background:{};color:{};padding:2px 10px;border-radius:999px;font-size:.72rem;font-weight:600;">'
            '<i class="bi {}"></i> {}</span>',
            bg, fg, icon, label,
        )

    @admin.display(description='Holati')
    def read_status(self, obj):
        if obj.is_read:
            return format_html('<span style="color:#64748B;">O\'qilgan</span>')
        return format_html('<span style="color:#EF4444;font-weight:600;">● Yangi</span>')

    @admin.action(description="O'qilgan deb belgilash")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} ta bildirishnoma o'qilgan deb belgilandi.")

    @admin.action(description="O'qilmagan deb belgilash")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} ta bildirishnoma o'qilmagan deb belgilandi.")
