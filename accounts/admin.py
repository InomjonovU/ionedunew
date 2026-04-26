from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'username', 'email', 'full_name_display', 'grade_display',
        'total_score', 'language', 'is_staff', 'is_active', 'date_joined',
    )
    list_display_links = ('username', 'email')
    list_filter = ('grade', 'language', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 50
    date_hierarchy = 'date_joined'
    readonly_fields = ('date_joined', 'last_login', 'total_score')

    fieldsets = (
        ('Hisob ma\'lumotlari', {
            'fields': ('username', 'password'),
        }),
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio'),
        }),
        ('EduSphere sozlamalari', {
            'fields': ('grade', 'language', 'total_score'),
        }),
        ('Ruxsatlar', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Tizim', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'grade', 'language'),
        }),
    )

    @admin.display(description='F.I.Sh.')
    def full_name_display(self, obj):
        full = obj.get_full_name()
        return full or format_html('<span style="color:#94a3b8;">—</span>')

    @admin.display(description='Sinf', ordering='grade')
    def grade_display(self, obj):
        if obj.grade:
            return f'{obj.grade}-sinf'
        return '—'
