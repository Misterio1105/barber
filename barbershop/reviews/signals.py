from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import MasterComment
from .services import refresh_master_rating


@receiver(post_save, sender=MasterComment)
def update_rating_on_save(sender, instance, **kwargs):
    refresh_master_rating(instance.master)


@receiver(post_delete, sender=MasterComment)
def update_rating_on_delete(sender, instance, **kwargs):
    refresh_master_rating(instance.master)
