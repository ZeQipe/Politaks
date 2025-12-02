from django.db import models
from django.utils import timezone
from django.conf import settings


class Satellite(models.Model):
    """Модель доменов-сателлитов"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Наименование')
    domen = models.CharField(max_length=255, unique=True, verbose_name='Домен')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'satellite'
        verbose_name = 'Домен-сателлит'
        verbose_name_plural = 'Домены-сателлиты'
        ordering = ['-createAt']
    
    def __str__(self):
        return f"{self.title} ({self.domen})"


class Products(models.Model):
    """Модель товаров"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    title = models.CharField(max_length=255, verbose_name='Название')
    baseLink = models.CharField(max_length=500, blank=True, null=True, verbose_name='Базовая ссылка')
    satelitLink = models.CharField(max_length=500, blank=True, null=True, verbose_name='Сателлит ссылка')
    description = models.TextField(verbose_name='Описание товара')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Кто создал'
    )
    satelitDomens = models.ManyToManyField(
        Satellite,
        blank=True,
        related_name='products',
        verbose_name='Домены сателлитов'
    )
    related_products = models.ManyToManyField(
        'self',
        through='List',
        symmetrical=False,
        blank=True,
        related_name='related_to',
        verbose_name='Связанные товары'
    )
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-createAt']
    
    def __str__(self):
        return self.title


class List(models.Model):
    """Промежуточная модель для связи товаров между собой"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name='product_relations',
        verbose_name='Товар'
    )
    related_product = models.ForeignKey(
        Products,
        on_delete=models.CASCADE,
        related_name='related_product_relations',
        verbose_name='Связанный товар'
    )
    description = models.TextField(blank=True, null=True, verbose_name='Описание связи')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'list'
        verbose_name = 'Связь товаров'
        verbose_name_plural = 'Связи товаров'
        ordering = ['-createAt']
        unique_together = ['product', 'related_product']
    
    def __str__(self):
        return f"{self.product.title} -> {self.related_product.title}"
