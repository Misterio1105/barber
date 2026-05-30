from decimal import Decimal, ROUND_HALF_UP

from django.db.models import Avg

from masters.models import Master


def refresh_master_rating(master):
    avg = master.comments.aggregate(avg=Avg("rating"))["avg"]
    if avg is None:
        new_rating = Decimal("5.00")
    else:
        new_rating = Decimal(str(avg)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if master.rating != new_rating:
        master.rating = new_rating
        master.save(update_fields=["rating"])


def refresh_all_master_ratings():
    for master in Master.objects.all():
        refresh_master_rating(master)
