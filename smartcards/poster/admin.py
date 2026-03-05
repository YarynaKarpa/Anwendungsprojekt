from django.contrib import admin
from .models import PosterCard

@admin.register(PosterCard)
class PosterCardAdmin(admin.ModelAdmin):
    list_display = ("subject", "short_question", "created_at")
    list_filter = ("subject", "created_at")
    search_fields = ("subject", "question", "answer")

    def short_question(self, obj):
        return (obj.question or "")[:80]
    short_question.short_description = "Question"
