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
    path("comments/<int:pk>/edit/", views.comment_edit, name="comment_edit"),
    path("comments/<int:pk>/delete/", views.comment_delete, name="comment_delete"),
]
