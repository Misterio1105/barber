from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from appointments.models import Appointment
from masters.models import Master
from services.models import Service

from .forms import AdminAppointmentForm, AppointmentForm, LoginForm, RegisterForm


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


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
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    sort = request.GET.get("sort", "name")

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


def masters_page(request):
    context = {
        "title": "Мастера",
        "masters": Master.objects.filter(is_active=True).order_by("-rating"),
    }
    return render(request, "pages/masters.html", context)


def master_detail(request, pk):
    master = get_object_or_404(Master, pk=pk, is_active=True)
    context = {
        "title": master.full_name,
        "master": master,
    }
    return render(request, "pages/master_detail.html", context)


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

    next_url = request.GET.get("next") or request.POST.get("next")

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Вы вошли в аккаунт.")
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("pages:profile")
    else:
        form = LoginForm()

    return render(
        request,
        "pages/login.html",
        {"title": "Вход", "form": form, "next": next_url},
    )


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
    master = None
    service = None
    master_id = request.GET.get("master") or request.POST.get("master")
    service_id = request.GET.get("service") or request.POST.get("service")
    if master_id:
        master = Master.objects.filter(pk=master_id, is_active=True).first()
    if service_id:
        service = Service.objects.filter(pk=service_id, is_active=True).first()

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, "Запись успешно создана.")
            return redirect("pages:profile")
    else:
        initial = {}
        if master:
            initial["master"] = master
        if service:
            initial["service"] = service
        form = AppointmentForm(initial=initial)

    return render(
        request,
        "pages/booking.html",
        {
            "title": "Онлайн-запись",
            "form": form,
            "selected_master": master,
            "selected_service": service,
        },
    )


@staff_required
def admin_dashboard(request):
    pending_count = Appointment.objects.filter(status="pending").count()
    context = {
        "title": "Админка",
        "pending_count": pending_count,
        "total_count": Appointment.objects.count(),
    }
    return render(request, "pages/admin_dashboard.html", context)


@staff_required
def admin_appointments(request):
    queryset = Appointment.objects.select_related("user", "master", "service").order_by(
        "-date", "-time"
    )
    status = request.GET.get("status", "").strip()
    if status:
        queryset = queryset.filter(status=status)

    context = {
        "title": "Записи",
        "appointments": queryset,
        "status_filter": status,
        "status_choices": Appointment.STATUS_CHOICES,
    }
    return render(request, "pages/admin_appointments.html", context)


@staff_required
def admin_appointment_edit(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        form = AdminAppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, "Запись обновлена.")
            return redirect("pages:admin_appointments")
    else:
        form = AdminAppointmentForm(instance=appointment)

    return render(
        request,
        "pages/admin_appointment_edit.html",
        {"title": "Редактирование записи", "form": form, "appointment": appointment},
    )


@staff_required
def admin_appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    if request.method == "POST":
        appointment.delete()
        messages.success(request, "Запись удалена.")
        return redirect("pages:admin_appointments")

    return render(
        request,
        "pages/admin_appointment_delete.html",
        {"title": "Удаление записи", "appointment": appointment},
    )
