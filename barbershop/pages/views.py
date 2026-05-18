from django.shortcuts import render

from masters.models import Master
from reviews.models import Review
from services.models import Service


def home(request):
    services = Service.objects.filter(is_active=True)[:3]
    masters = Master.objects.filter(is_active=True)[:3]
    context = {
        "title": "Барбершоп",
        "services": services,
        "masters": masters,
    }
    return render(request, "pages/home.html", context)


def services_page(request):
    context = {
        "title": "Услуги",
        "services": Service.objects.filter(is_active=True),
    }
    return render(request, "pages/services.html", context)


def masters_page(request):
    context = {
        "title": "Мастера",
        "masters": Master.objects.filter(is_active=True),
    }
    return render(request, "pages/masters.html", context)


def reviews_page(request):
    context = {
        "title": "Отзывы",
        "reviews": Review.objects.filter(is_approved=True).select_related(
            "user", "master", "service"
        ),
    }
    return render(request, "pages/reviews.html", context)


def contacts_page(request):
    context = {
        "title": "Контакты",
        "address": "г. Минск, ул. Лынькова, 101к3",
        "phone": "+375 (44) 590-99-63",
        "work_time": "Пн-Вс: 10:00 - 21:00",
    }
    return render(request, "pages/contacts.html", context)


def bim_page(request):
    return render(request, "pages/bim.html")
