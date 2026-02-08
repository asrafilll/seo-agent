from django.db import models


class AuditReport(models.Model):
    url = models.URLField(max_length=2000)
    result = models.TextField(help_text="JSON audit result from agent")
    agent_summary = models.TextField(blank=True, help_text="Agent's markdown summary")
    score = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Audit: {self.url} ({self.created_at:%Y-%m-%d %H:%M})"


class KeywordResearch(models.Model):
    seed_keyword = models.CharField(max_length=500)
    result = models.TextField(help_text="JSON keyword research result")
    agent_summary = models.TextField(blank=True, help_text="Agent's markdown summary")
    total_keywords = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Keywords: {self.seed_keyword} ({self.created_at:%Y-%m-%d %H:%M})"


class ContentOptimization(models.Model):
    url = models.URLField(max_length=2000)
    result = models.TextField(help_text="JSON content analysis result")
    agent_summary = models.TextField(blank=True, help_text="Agent's markdown summary")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Optimize: {self.url} ({self.created_at:%Y-%m-%d %H:%M})"


class Conversation(models.Model):
    title = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or f"Conversation #{self.pk}"


class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"
