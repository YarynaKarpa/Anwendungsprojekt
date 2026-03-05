from django.db import models

class PosterCard(models.Model):
    subject = models.CharField(max_length=200, db_index=True)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"[{self.subject}] {self.question[:60]}..."
