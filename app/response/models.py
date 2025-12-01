from django.db import models
from django.utils import timezone


class Response(models.Model):
    """Модель ответов (без связей, все данные хранятся как строки)"""
    
    SOURCE_CHOICES = [
        ('manual', 'Ручной ввод'),
        ('excel', 'Из Excel'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    parametrs = models.TextField(verbose_name='Входные параметры')
    domen = models.CharField(max_length=255, verbose_name='Домен')
    html = models.TextField(verbose_name='HTML')
    user = models.CharField(max_length=255, verbose_name='Пользователь')
    model = models.CharField(max_length=255, verbose_name='Модель')
    assistant = models.CharField(max_length=255, verbose_name='Ассистент')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name='Источник')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'response'
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-createAt']
    
    def __str__(self):
        return f"Response #{self.id} - {self.domen} ({self.createAt.strftime('%Y-%m-%d %H:%M')})"
