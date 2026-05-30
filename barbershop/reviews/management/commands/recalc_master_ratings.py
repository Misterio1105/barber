from django.core.management.base import BaseCommand

from reviews.services import refresh_all_master_ratings


class Command(BaseCommand):
    help = "Пересчитывает рейтинг мастеров по отзывам."

    def handle(self, *args, **options):
        refresh_all_master_ratings()
        self.stdout.write(self.style.SUCCESS("Рейтинги мастеров обновлены."))
