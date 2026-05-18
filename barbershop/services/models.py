from django.db import models

# Create your models here.
class Service(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    duration = models.IntegerField('Длительность (мин)')
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    
    def __str__(self):
        return self.name