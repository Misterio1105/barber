from django.db import models
from users.models import User
from masters.models import Master


class MasterComment(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="master_comments")
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name="comments")
    rating = models.PositiveSmallIntegerField("Оценка", choices=RATING_CHOICES, default=5)
    text = models.TextField("Отзыв")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"

    def __str__(self):
        return f"{self.user.username} → {self.master.full_name} ({self.rating}★)"

    @property
    def stars_display(self):
        return "★" * self.rating + "☆" * (5 - self.rating)
