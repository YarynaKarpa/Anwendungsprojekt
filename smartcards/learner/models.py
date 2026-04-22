from django.db import models
from django.contrib.auth.models import User

class StudyNote(models.Model):
    user = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE
    )
    session_id = models.CharField(
        max_length=64, null=True, blank=True, db_index=True
    )
    question_id = models.CharField(max_length=64, db_index=True)

    text = models.TextField(blank=True, default="")

    selbstbewertung = models.IntegerField(default=0)
    count_correct = models.IntegerField(default=0)
    count_wrong = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "session_id", "question_id")