from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from appointments.models import Appointment
from masters.models import Master
from reviews.models import MasterComment
from services.models import Service

from .forms import (
    AppointmentForm,
    LoginForm,
    MasterCommentForm,
    ProfileUpdateForm,
    RegisterForm,
)


def staff_required(view_func):
    return login_required(user_passes_test(lambda u: u.is_staff)(view_func))


def home(request):
    services = Service.objects.filter(is_active=True)[:4]
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
    comment_form = None

    if request.user.is_authenticated:
        if request.method == "POST" and "comment_submit" in request.POST:
            comment_form = MasterCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.user = request.user
                comment.master = master
                comment.save()
                messages.success(request, "Отзыв добавлен.")
                return redirect("pages:master_detail", pk=master.pk)
        else:
            comment_form = MasterCommentForm()

    context = {
        "title": master.full_name,
        "master": master,
        "comments": master.comments.select_related("user"),
        "comment_form": comment_form,
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
    if request.method == "POST" and "profile_submit" in request.POST:
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Данные профиля обновлены.")
            return redirect("pages:profile")
    else:
        profile_form = ProfileUpdateForm(instance=request.user)

    appointments = (
        Appointment.objects.filter(user=request.user)
        .select_related("master", "service")
        .order_by("-date", "-time")
    )
    context = {
        "title": "Личный кабинет",
        "appointments": appointments,
        "profile_form": profile_form,
    }
    return render(request, "pages/profile.html", context)


@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)

    if appointment.status in ("completed", "cancelled"):
        messages.error(request, "Эту запись нельзя отменить.")
        return redirect("pages:profile")

    if request.method == "POST":
        appointment.status = "cancelled"
        appointment.save()
        messages.success(request, "Запись отменена.")
        return redirect("pages:profile")

    return render(
        request,
        "pages/cancel_appointment.html",
        {"title": "Отмена записи", "appointment": appointment},
    )


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
def comment_edit(request, pk):
    comment = get_object_or_404(MasterComment.objects.select_related("master"), pk=pk)

    if request.method == "POST":
        form = MasterCommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, "Отзыв обновлён.")
            return redirect("pages:master_detail", pk=comment.master.pk)
    else:
        form = MasterCommentForm(instance=comment)

    return render(
        request,
        "pages/comment_edit.html",
        {"title": "Редактирование отзыва", "form": form, "comment": comment},
    )


@staff_required
def comment_delete(request, pk):
    comment = get_object_or_404(MasterComment.objects.select_related("master"), pk=pk)

    if request.method == "POST":
        master_pk = comment.master.pk
        comment.delete()
        messages.success(request, "Отзыв удалён.")
        return redirect("pages:master_detail", pk=master_pk)

    return render(
        request,
        "pages/comment_delete.html",
        {"title": "Удаление отзыва", "comment": comment},
    )
