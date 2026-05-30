from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from masters.models import Master
from reviews.models import MasterComment
from users.models import User

COMMENT_SAMPLES = [
    "Отличный мастер, всегда аккуратно стрижёт.",
    "Хорошая атмосфера, вернусь ещё.",
    "Бороду оформил идеально, рекомендую.",
    "Записался без проблем, всё по времени.",
    "Профессионал своего дела.",
    "Стрижка получилась именно такой, как хотел.",
    "Вежливый и внимательный мастер.",
    "Уютное место, качественный сервис.",
    "Fade сделали чётко, доволен результатом.",
    "Королевское бритье — лучшее, что пробовал.",
]


class Command(BaseCommand):
    help = "Добавляет комментарии к мастерам от существующих пользователей."

    def handle(self, *args, **options):
        users = list(User.objects.filter(is_staff=False).order_by("id"))
        masters = list(Master.objects.filter(is_active=True).order_by("id"))

        if not users:
            self.stdout.write(self.style.ERROR("В базе нет пользователей."))
            return
        if not masters:
            self.stdout.write(self.style.ERROR("В базе нет активных мастеров."))
            return

        yesterday = timezone.localdate() - timedelta(days=1)
        created_count = 0

        for index, user in enumerate(users):
            master = masters[index % len(masters)]
            text = COMMENT_SAMPLES[index % len(COMMENT_SAMPLES)]
            hour = 10 + (index % 9)
            minute = (index * 7) % 60

            comment, was_created = MasterComment.objects.get_or_create(
                user=user,
                master=master,
                text=text,
                defaults={"rating": 4 + index % 2, "created_at": timezone.now()},
            )
            if was_created:
                created_at = timezone.make_aware(
                    datetime.combine(yesterday, datetime.min.time().replace(hour=hour, minute=minute))
                )
                MasterComment.objects.filter(pk=comment.pk).update(created_at=created_at)
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(f"Добавлено комментариев: {created_count}. Дата: {yesterday}.")
        )
