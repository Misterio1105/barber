from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services_page, name="services"),
    path("masters/", views.masters_page, name="masters"),
    path("reviews/", views.reviews_page, name="reviews"),
    path("contacts/", views.contacts_page, name="contacts"),
    path("bim/", views.bim_page, name="bim"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("booking/", views.booking_view, name="booking"),
]
