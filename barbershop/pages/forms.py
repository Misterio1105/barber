from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from appointments.models import Appointment
from masters.models import Master
from services.models import Service

from reviews.models import MasterComment

User = get_user_model()

BOOKING_YEAR = 2026
BOOKING_DATE_MIN = date(BOOKING_YEAR, 1, 1)
BOOKING_DATE_MAX = date(BOOKING_YEAR, 12, 31)


def booking_date_min():
    today = date.today()
    if today.year < BOOKING_YEAR:
        return BOOKING_DATE_MIN
    if today.year > BOOKING_YEAR:
        return BOOKING_DATE_MAX
    return max(BOOKING_DATE_MIN, today)


def default_booking_date():
    today = date.today()
    if BOOKING_DATE_MIN <= today <= BOOKING_DATE_MAX:
        return today
    return booking_date_min()


class RegisterForm(UserCreationForm):
    phone = forms.CharField(
        label="Телефон",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "+375291234567"}),
    )
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "email@example.com"}),
    )

    class Meta:
        model = User
        fields = ("username", "phone", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Логин"
        self.fields["password"].label = "Пароль"
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "phone", "email")
        labels = {
            "username": "Логин",
            "phone": "Телефон",
            "email": "Email",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("master", "service", "date", "time")
        labels = {
            "master": "Мастер",
            "service": "Услуга",
            "date": "Дата",
            "time": "Время",
        }
        widgets = {
            "master": forms.Select(attrs={"class": "form-control"}),
            "service": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["master"].queryset = Master.objects.filter(is_active=True)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)

        self.fields["date"].widget.attrs["min"] = booking_date_min().isoformat()
        self.fields["date"].widget.attrs["max"] = BOOKING_DATE_MAX.isoformat()

        if not self.initial.get("date") and not self.data.get("date"):
            self.fields["date"].initial = default_booking_date()

        master, service = self._resolve_master_and_service()

        if master:
            self.fields["master"].initial = master.pk
            self.fields["service"].queryset = master.services.filter(is_active=True)
            if service:
                self.fields["service"].initial = service.pk
        elif service:
            self.fields["service"].initial = service.pk
            masters_qs = Master.objects.filter(
                is_active=True, services=service
            ).distinct()
            self.fields["master"].queryset = masters_qs
            if master and masters_qs.filter(pk=master.pk).exists():
                self.fields["master"].initial = master.pk

    def _resolve_master_and_service(self):
        master = self.initial.get("master")
        service = self.initial.get("service")
        if isinstance(master, int):
            master = Master.objects.filter(pk=master, is_active=True).first()
        if isinstance(service, int):
            service = Service.objects.filter(pk=service, is_active=True).first()

        if self.data:
            service_id = self.data.get("service")
            master_id = self.data.get("master")
            if service_id:
                service = Service.objects.filter(pk=service_id, is_active=True).first()
            if master_id:
                master = Master.objects.filter(pk=master_id, is_active=True).first()

        return master, service

    def clean_date(self):
        value = self.cleaned_data.get("date")
        if not value:
            return value
        if not (BOOKING_DATE_MIN <= value <= BOOKING_DATE_MAX):
            raise forms.ValidationError(f"Запись возможна только в {BOOKING_YEAR} году.")
        if value < date.today():
            raise forms.ValidationError("Нельзя записаться на прошедшую дату.")
        return value

    def clean(self):
        cleaned = super().clean()
        master = cleaned.get("master")
        service = cleaned.get("service")
        if master and service and not master.services.filter(pk=service.pk).exists():
            raise forms.ValidationError("Выбранный мастер не выполняет эту услугу.")
        return cleaned


class AdminAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ("user", "master", "service", "date", "time", "status")
        labels = {
            "user": "Клиент",
            "master": "Мастер",
            "service": "Услуга",
            "date": "Дата",
            "time": "Время",
            "status": "Статус",
        }
        widgets = {
            "user": forms.Select(attrs={"class": "form-control"}),
            "master": forms.Select(attrs={"class": "form-control"}),
            "service": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["master"].queryset = Master.objects.filter(is_active=True)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)


class MasterCommentForm(forms.ModelForm):
    class Meta:
        model = MasterComment
        fields = ("text",)
        labels = {"text": "Комментарий"}
        widgets = {
            "text": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Ваш комментарий"}
            ),
        }
