# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0003_mastercomment"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Review",
        ),
    ]
