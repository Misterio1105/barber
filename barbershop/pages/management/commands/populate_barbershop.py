from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from appointments.models import Appointment
from masters.models import Master, WorkSchedule
from reviews.models import Review
from services.models import Service
from users.models import User

SERVICES = [
    ("Стрижка Fade", "Классическая мужская стрижка с плавным переходом.", "35.00", 60),
    ("Оформление бороды", "Контур и форма бороды с уходом.", "22.00", 40),
    ("Королевское бритье", "Бритье опасной бритвой с горячим полотенцем.", "40.00", 50),
    ("Стрижка машинкой", "Быстрая стрижка под одну длину.", "25.00", 30),
    ("Комплекс Стрижка+борода", "Полный уход за стрижкой и бородой.", "55.00", 90),
]

MASTERS = [
    ("Илья", "Сидоров", "Fade, классические стрижки", 5, "4.80", [0, 1, 4]),
    ("Антон", "Ковалев", "Борода и королевское бритье", 7, "4.90", [1, 2]),
    ("Максим", "Лебедев", "Машинка и спортивные стрижки", 3, "4.70", [3, 0]),
    ("Дмитрий", "Новик", "Комплексные услуги", 6, "4.85", [4, 1, 2]),
    ("Сергей", "Мельник", "Fade и борода", 4, "4.75", [0, 1, 3]),
]

USERS = [
    ("client01", "+375291000001", "client01@mail.ru"),
    ("client02", "+375291000002", "client02@mail.ru"),
    ("client03", "+375291000003", "client03@mail.ru"),
    ("client04", "+375291000004", "client04@mail.ru"),
    ("client05", "+375291000005", "client05@mail.ru"),
]


class Command(BaseCommand):
    help = "Заполняет БД тестовыми данными (по 5 записей в каждую таблицу)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--only",
            choices=["services", "masters", "users", "schedules", "appointments", "reviews", "all"],
            default="all",
        )

    def handle(self, *args, **options):
        only = options["only"]
        if only in ("services", "all"):
            self._seed_services()
        if only in ("masters", "all"):
            self._seed_masters()
        if only in ("users", "all"):
            self._seed_users()
        if only in ("schedules", "all"):
            self._seed_schedules()
        if only in ("appointments", "all"):
            self._seed_appointments()
        if only in ("reviews", "all"):
            self._seed_reviews()
        self.stdout.write(self.style.SUCCESS("Готово."))

    def _seed_services(self):
        for name, desc, price, duration in SERVICES:
            Service.objects.get_or_create(
                name=name,
                defaults={
                    "description": desc,
                    "price": Decimal(price),
                    "duration": duration,
                    "is_active": True,
                },
            )
        self.stdout.write("Услуги: 5")

    def _seed_masters(self):
        services = list(Service.objects.all()[:5])
        if len(services) < 5:
            self.stdout.write(self.style.WARNING("Сначала добавьте услуги."))
            return
        for name, surname, spec, exp, rating, svc_idx in MASTERS:
            master, created = Master.objects.get_or_create(
                name=name,
                surname=surname,
                defaults={
                    "specialization": spec,
                    "experience": exp,
                    "bio": f"Мастер {name} {surname}, стаж {exp} лет.",
                    "rating": Decimal(rating),
                    "is_active": True,
                },
            )
            if created or not master.services.exists():
                master.services.set([services[i] for i in svc_idx if i < len(services)])
        self.stdout.write("Мастера: 5")

    def _seed_users(self):
        for username, phone, email in USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    "phone": phone,
                    "email": email,
                    "birth_date": date(1998, 1, 1),
                },
            )
            if created:
                user.set_password("pass12345")
                user.save()
        self.stdout.write("Пользователи: 5")

    def _seed_schedules(self):
        masters = list(Master.objects.all()[:5])
        for i, master in enumerate(masters):
            WorkSchedule.objects.get_or_create(
                master=master,
                day_of_week=i,
                defaults={
                    "start_time": time(10, 0),
                    "end_time": time(20, 0),
                    "is_working": True,
                },
            )
        self.stdout.write("Расписание: 5")

    def _seed_appointments(self):
        users = list(User.objects.all()[:5])
        masters = list(Master.objects.all()[:5])
        if not users or not masters:
            self.stdout.write(self.style.WARNING("Нужны пользователи и мастера."))
            return
        for i in range(5):
            service = masters[i].services.first() or Service.objects.first()
            if not service:
                continue
            Appointment.objects.get_or_create(
                user=users[i],
                master=masters[i],
                service=service,
                date=date.today() + timedelta(days=i + 1),
                time=time(10 + i, 0),
                defaults={"status": "pending", "comment": f"Запись №{i + 1}"},
            )
        self.stdout.write("Записи: 5")

    def _seed_reviews(self):
        users = list(User.objects.all()[:5])
        masters = list(Master.objects.all()[:5])
        comments = [
            "Отличная стрижка, рекомендую.",
            "Аккуратно оформили бороду.",
            "Быстро и качественно.",
            "Приятная атмосфера в салоне.",
            "Вернусь ещё раз.",
        ]
        for i in range(5):
            service = masters[i].services.first() or Service.objects.first()
            if not service:
                continue
            Review.objects.get_or_create(
                user=users[i],
                master=masters[i],
                service=service,
                defaults={
                    "rating": 5 - (i % 2),
                    "comment": comments[i],
                    "is_approved": True,
                },
            )
        self.stdout.write("Отзывы: 5")
