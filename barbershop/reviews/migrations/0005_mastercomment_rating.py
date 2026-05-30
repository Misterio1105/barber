# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("reviews", "0004_delete_review"),
    ]

    operations = [
        migrations.AddField(
            model_name="mastercomment",
            name="rating",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                default=5,
                verbose_name="Оценка",
            ),
        ),
        migrations.AlterField(
            model_name="mastercomment",
            name="text",
            field=models.TextField(verbose_name="Отзыв"),
        ),
        migrations.AlterModelOptions(
            name="mastercomment",
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Отзыв",
                "verbose_name_plural": "Отзывы",
            },
        ),
    ]
