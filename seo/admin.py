from django.contrib import admin

from .models import (
    AuditReport,
    ChatMessage,
    ContentOptimization,
    Conversation,
    KeywordResearch,
)


@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    list_display = ["url", "score", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["url"]


@admin.register(KeywordResearch)
class KeywordResearchAdmin(admin.ModelAdmin):
    list_display = ["seed_keyword", "total_keywords", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["seed_keyword"]


@admin.register(ContentOptimization)
class ContentOptimizationAdmin(admin.ModelAdmin):
    list_display = ["url", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["url"]


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ["role", "content", "created_at"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["__str__", "created_at", "updated_at"]
    inlines = [ChatMessageInline]
