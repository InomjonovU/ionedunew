from django.contrib import admin
from .models import AIConversation, AIMessage, AIEssayCheck, AILessonSummary, AIRecommendation

class AIMessageInline(admin.TabularInline):
    model = AIMessage
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson_title', 'message_count', 'created_at')
    inlines = [AIMessageInline]

@admin.register(AIEssayCheck)
class AIEssayCheckAdmin(admin.ModelAdmin):
    list_display = ('user', 'grammar_score', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(AILessonSummary)
class AILessonSummaryAdmin(admin.ModelAdmin):
    list_display = ('lesson_title', 'lesson_id', 'updated_at')

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'generated_at')
