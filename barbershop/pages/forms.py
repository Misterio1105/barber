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
        fields = ("master", "service", "date", "time", "comment")
        labels = {
            "master": "Мастер",
            "service": "Услуга",
            "date": "Дата",
            "time": "Время",
            "comment": "Комментарий",
        }
        widgets = {
            "master": forms.Select(attrs={"class": "form-control"}),
            "service": forms.Select(attrs={"class": "form-control"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "time": forms.TimeInput(attrs={"class": "form-control", "type": "time"}),
            "comment": forms.Textarea(
                attrs={"class": "form-control", "rows": 3, "placeholder": "Пожелания к записи"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["master"].queryset = Master.objects.filter(is_active=True)
        self.fields["service"].queryset = Service.objects.filter(is_active=True)

        master = self.initial.get("master")
        if master:
            if isinstance(master, int):
                master = Master.objects.filter(pk=master, is_active=True).first()
            if master:
                self.fields["service"].queryset = master.services.filter(is_active=True)
                self.fields["master"].initial = master.pk

    def clean(self):
        cleaned = super().clean()
        master = cleaned.get("master")
        service = cleaned.get("service")
        if master and service and not master.services.filter(pk=service.pk).exists():
            raise forms.ValidationError("Выбранный мастер не выполняет эту услугу.")
        return cleaned
