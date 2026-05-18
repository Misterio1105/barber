from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import redirect, render

from appointments.models import Appointment
from masters.models import Master
from reviews.models import Review
from services.models import Service

from .forms import AppointmentForm, LoginForm, RegisterForm


def home(request):
    services = Service.objects.filter(is_active=True)[:3]
    masters = Master.objects.filter(is_active=True)[:3]
    context = {
        "title": "Барбершоп",
        "services": services,
        "masters": masters,
    }
    return render(request, "pages/home.html", context)


def _apply_service_filters(queryset, request):
    q = request.GET.get("q", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "name")

    if q:
        queryset = queryset.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)

    sort_map = {
        "name": "name",
        "price_asc": "price",
        "price_desc": "-price",
        "duration": "duration",
    }
    return queryset.order_by(sort_map.get(sort, "name"))


def services_page(request):
    queryset = Service.objects.filter(is_active=True)
    context = {
        "title": "Услуги",
        "services": _apply_service_filters(queryset, request),
        "filters": request.GET,
    }
    return render(request, "pages/services.html", context)


def _apply_master_filters(queryset, request):
    q = request.GET.get("q", "").strip()
    min_exp = request.GET.get("min_exp", "").strip()
    sort = request.GET.get("sort", "rating")

    if q:
        queryset = queryset.filter(
            Q(name__icontains=q)
            | Q(surname__icontains=q)
            | Q(specialization__icontains=q)
        )
    if min_exp:
        queryset = queryset.filter(experience__gte=min_exp)

    sort_map = {
        "rating": "-rating",
        "experience": "-experience",
        "name": "surname",
    }
    return queryset.order_by(sort_map.get(sort, "-rating"))


def masters_page(request):
    queryset = Master.objects.filter(is_active=True)
    context = {
        "title": "Мастера",
        "masters": _apply_master_filters(queryset, request),
        "filters": request.GET,
    }
    return render(request, "pages/masters.html", context)


def _apply_review_filters(queryset, request):
    min_rating = request.GET.get("min_rating", "").strip()
    master_id = request.GET.get("master", "").strip()
    sort = request.GET.get("sort", "date")

    if min_rating:
        queryset = queryset.filter(rating__gte=min_rating)
    if master_id:
        queryset = queryset.filter(master_id=master_id)

    sort_map = {
        "date": "-created_at",
        "rating": "-rating",
    }
    return queryset.order_by(sort_map.get(sort, "-created_at"))


def reviews_page(request):
    queryset = Review.objects.filter(is_approved=True).select_related(
        "user", "master", "service"
    )
    context = {
        "title": "Отзывы",
        "reviews": _apply_review_filters(queryset, request),
        "masters": Master.objects.filter(is_active=True),
        "filters": request.GET,
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


def register_view(request):
    if request.user.is_authenticated:
        return redirect("pages:profile")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация прошла успешно.")
            return redirect("pages:profile")
    else:
        form = RegisterForm()

    return render(request, "pages/register.html", {"title": "Регистрация", "form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("pages:profile")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Вы вошли в аккаунт.")
            return redirect("pages:profile")
    else:
        form = LoginForm()

    return render(request, "pages/login.html", {"title": "Вход", "form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("pages:home")


@login_required
def profile_view(request):
    appointments = (
        Appointment.objects.filter(user=request.user)
        .select_related("master", "service")
        .order_by("-date", "-time")
    )
    context = {
        "title": "Личный кабинет",
        "appointments": appointments,
    }
    return render(request, "pages/profile.html", context)


@login_required
def booking_view(request):
    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, "Запись успешно создана.")
            return redirect("pages:profile")
    else:
        form = AppointmentForm()

    return render(
        request,
        "pages/booking.html",
        {"title": "Онлайн-запись", "form": form},
    )
