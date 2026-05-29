from django.db import models
from users.models import User
from masters.models import Master


class MasterComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="master_comments")
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Комментарий к мастеру"
        verbose_name_plural = "Комментарии к мастерам"

    def __str__(self):
        return f"{self.user.username} → {self.master.full_name}"
