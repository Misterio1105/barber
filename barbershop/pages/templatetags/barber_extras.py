from urllib.parse import quote

from django import template
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static
from django.urls import reverse

register = template.Library()


def _image_url(uploaded_file, folder, obj_id):
    if uploaded_file:
        return uploaded_file.url
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = f"images/{folder}/{obj_id}.{ext}"
        if find(path):
            return static(path)
    return static(f"images/{folder}/default.svg")


@register.simple_tag
def service_image(service):
    return _image_url(service.image, "services", service.pk)


@register.simple_tag
def master_image(master):
    return _image_url(master.photo, "masters", master.pk)


@register.simple_tag
def booking_url(service_id=None, master_id=None):
    url = reverse("pages:booking")
    params = []
    if service_id:
        params.append(f"service={service_id}")
    if master_id:
        params.append(f"master={master_id}")
    if params:
        url += "?" + "&".join(params)
    return url


@register.simple_tag
def login_for_booking(service_id=None, master_id=None):
    target = booking_url(service_id, master_id)
    return reverse("pages:login") + "?next=" + quote(target, safe="")
