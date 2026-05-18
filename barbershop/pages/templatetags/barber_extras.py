from django import template
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static

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
