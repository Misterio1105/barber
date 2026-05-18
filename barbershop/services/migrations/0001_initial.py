from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Название')),
                ('description', models.TextField(verbose_name='Описание')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Цена')),
                ('duration', models.IntegerField(verbose_name='Длительность (мин)')),
                ('image', models.ImageField(blank=True, null=True, upload_to='services/')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
            ],
        ),
    ]
