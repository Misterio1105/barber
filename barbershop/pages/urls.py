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
]