from django.db import models
from services.models import Service
# Create your models here.
class Master(models.Model):
    name = models.CharField('Имя', max_length=100)
    surname = models.CharField('Фамилия', max_length=100)
    specialization = models.CharField('Специализация', max_length=200)
    experience = models.IntegerField('Стаж (лет)')
    bio = models.TextField('Биография')
    photo = models.ImageField(upload_to='masters/', blank=True, null=True)
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=2, default=5.00)
    services = models.ManyToManyField(Service, related_name='masters')
    is_active = models.BooleanField('Работает', default=True)
    
    @property
    def full_name(self):
        return f"{self.name} {self.surname}"
    
    def __str__(self):
        return self.full_name

class WorkSchedule(models.Model):
    master = models.ForeignKey(Master, on_delete=models.CASCADE, related_name='schedule')
    day_of_week = models.IntegerField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_start = models.TimeField(blank=True, null=True)
    break_end = models.TimeField(blank=True, null=True)
    is_working = models.BooleanField(default=True)