from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services_page, name="services"),
    path("masters/", views.masters_page, name="masters"),
    path("masters/<int:pk>/", views.master_detail, name="master_detail"),
    path("contacts/", views.contacts_page, name="contacts"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path(
        "profile/appointments/<int:pk>/cancel/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
    path("booking/", views.booking_view, name="booking"),
    path("manage/", views.admin_dashboard, name="admin_dashboard"),
    path("manage/appointments/", views.admin_appointments, name="admin_appointments"),
    path(
        "manage/appointments/<int:pk>/edit/",
        views.admin_appointment_edit,
        name="admin_appointment_edit",
    ),
    path(
        "manage/appointments/<int:pk>/delete/",
        views.admin_appointment_delete,
        name="admin_appointment_delete",
    ),
]
