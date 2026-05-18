from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from appointments.models import Appointment
from masters.models import Master
from services.models import Service

User = get_user_model()


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
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["master"].queryset = Master.objects.filter(is_active=True)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)

        master = self.initial.get("master")
        service = self.initial.get("service")
        if isinstance(master, int):
            master = Master.objects.filter(pk=master, is_active=True).first()
        if isinstance(service, int):
            service = Service.objects.filter(pk=service, is_active=True).first()

        if master:
            self.fields["master"].initial = master.pk
            self.fields["service"].queryset = master.services.filter(is_active=True)
            if service:
                self.fields["service"].initial = service.pk
        elif service:
            self.fields["service"].initial = service.pk
            self.fields["master"].queryset = Master.objects.filter(
                is_active=True, services=service
            ).distinct()

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
