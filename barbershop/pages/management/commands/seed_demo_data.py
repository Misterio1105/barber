from datetime import date, time
from decimal import Decimal

from django.core.management.base import BaseCommand

from appointments.models import Appointment
from masters.models import Master
from reviews.models import Review
from services.models import Service
from users.models import User


class Command(BaseCommand):
    help = "Creates minimal demo data for barbershop pages."

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(
            username="demo_client",
            defaults={
                "email": "demo@example.com",
                "phone": "+375291111111",
                "birth_date": date(2000, 1, 1),
            },
        )
        user.set_password("demo12345")
        user.save()

        fade, _ = Service.objects.get_or_create(
            name="Стрижка Fade",
            defaults={
                "description": "Классическая мужская стрижка с плавным переходом.",
                "price": Decimal("35.00"),
                "duration": 60,
                "is_active": True,
            },
        )
        beard, _ = Service.objects.get_or_create(
            name="Оформление бороды",
            defaults={
                "description": "Контур и форма бороды с уходом.",
                "price": Decimal("22.00"),
                "duration": 40,
                "is_active": True,
            },
        )

        master_1, _ = Master.objects.get_or_create(
            name="Илья",
            surname="Сидоров",
            defaults={
                "specialization": "Fade, классические стрижки",
                "experience": 5,
                "bio": "Работает с мужскими стрижками и укладкой.",
                "rating": Decimal("4.80"),
                "is_active": True,
            },
        )
        master_2, _ = Master.objects.get_or_create(
            name="Антон",
            surname="Ковалев",
            defaults={
                "specialization": "Борода и королевское бритье",
                "experience": 7,
                "bio": "Специализируется на оформлении бороды.",
                "rating": Decimal("4.90"),
                "is_active": True,
            },
        )

        master_1.services.add(fade, beard)
        master_2.services.add(beard)

        Appointment.objects.get_or_create(
            user=user,
            master=master_1,
            service=fade,
            date=date.today(),
            time=time(12, 0),
            defaults={"status": "pending", "comment": "Учебная запись"},
        )

        Review.objects.get_or_create(
            user=user,
            master=master_1,
            service=fade,
            defaults={
                "rating": 5,
                "comment": "Отличный мастер, аккуратная стрижка.",
                "is_approved": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data created or already exists."))
