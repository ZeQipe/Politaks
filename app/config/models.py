from django.db import models
from django.utils import timezone


class Models(models.Model):
    """Модель AI моделей"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Название')
    url = models.CharField(max_length=500, verbose_name='URL')
    key = models.CharField(max_length=255, verbose_name='Ключ')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'models'
        verbose_name = 'AI Модель'
        verbose_name_plural = 'AI Модели'
        ordering = ['-createAt']
    
    def __str__(self):
        return self.name


class Inputer(models.Model):
    """Модель полей ввода"""
    
    TYPE_CHOICES = [
        ('input', 'Поле ввода'),
        ('choise', 'Выбор'),
    ]
    
    SIZE_CHOICES = [
        ('small', 'Маленький'),
        ('normal', 'Обычный'),
        ('high', 'Большой'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Название')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, verbose_name='Размер')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'inputer'
        verbose_name = 'Поле ввода'
        verbose_name_plural = 'Поля ввода'
        ordering = ['-createAt']
    
    def __str__(self):
        return self.title


class Assistant(models.Model):
    """Модель ассистента"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Название')
    instruction = models.TextField(verbose_name='Инструкция')
    maks_token = models.IntegerField(null=True, blank=True, verbose_name='Максимум токенов')
    temperatures = models.FloatField(null=True, blank=True, verbose_name='Температура')
    input_columns = models.ManyToManyField(
        Inputer,
        blank=True,
        related_name='assistants',
        verbose_name='Поля ввода'
    )
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'assistant'
        verbose_name = 'Ассистент'
        verbose_name_plural = 'Ассистенты'
        ordering = ['-createAt']
    
    def __str__(self):
        return self.title
