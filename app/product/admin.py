from django.contrib import admin
from .models import Products, List, Satellite


@admin.register(Satellite)
class SatelliteAdmin(admin.ModelAdmin):
    """Админ-панель для доменов-сателлитов"""
    
    # Список отображаемых полей
    list_display = (
        'id',
        'title',
        'domen',
        'products_count',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'createAt',
    )
    
    # Поля для поиска
    search_fields = (
        'title',
        'domen',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Все поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'domen')
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt',)
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    def products_count(self, obj):
        """Количество связанных товаров"""
        return obj.products.count()
    products_count.short_description = "Кол-во товаров"


class ListInline(admin.TabularInline):
    """Inline для редактирования связанных товаров"""
    model = List
    fk_name = 'product'
    extra = 1
    verbose_name = "Связанный товар"
    verbose_name_plural = "Связанные товары"
    
    fields = ('related_product', 'description', 'createAt')
    readonly_fields = ('createAt',)
    
    # Для отображения
    autocomplete_fields = ['related_product']


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    """Админ-панель для связей товаров"""
    
    # Список отображаемых полей
    list_display = (
        'id',
        'product',
        'related_product',
        'description_preview',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'createAt',
    )
    
    # Поля для поиска
    search_fields = (
        'product__title',
        'related_product__title',
        'description',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Все поля для редактирования
    fieldsets = (
        ('Связь товаров', {
            'fields': ('product', 'related_product')
        }),
        ('Описание связи', {
            'fields': ('description',)
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt',)
    
    # Автокомплит для выбора товаров
    autocomplete_fields = ['product', 'related_product']
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    def description_preview(self, obj):
        """Превью описания (первые 50 символов)"""
        if obj.description:
            return f"{obj.description[:50]}..." if len(obj.description) > 50 else obj.description
        return "-"
    description_preview.short_description = "Описание связи"


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    """Админ-панель для товаров"""
    
    # Список отображаемых полей
    list_display = (
        'id',
        'title',
        'created_by',
        'baseLink_preview',
        'satelitLink_preview',
        'satellites_count',
        'related_count',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'created_by',
        'createAt',
        'satelitDomens',
    )
    
    # Поля для поиска
    search_fields = (
        'title',
        'description',
        'baseLink',
        'satelitLink',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Все поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description')
        }),
        ('Ссылки', {
            'fields': ('baseLink', 'satelitLink')
        }),
        ('Домены сателлитов', {
            'fields': ('satelitDomens',)
        }),
        ('Создатель', {
            'fields': ('created_by',)
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt',)
    
    # ManyToMany с удобным интерфейсом
    filter_horizontal = ('satelitDomens',)
    
    # Inline для связанных товаров
    inlines = [ListInline]
    
    # Автокомплит для выбора создателя
    autocomplete_fields = ['created_by']
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    def baseLink_preview(self, obj):
        """Превью базовой ссылки"""
        if obj.baseLink:
            return f"{obj.baseLink[:30]}..." if len(obj.baseLink) > 30 else obj.baseLink
        return "-"
    baseLink_preview.short_description = "Базовая ссылка"
    
    def satelitLink_preview(self, obj):
        """Превью сателлит ссылки"""
        if obj.satelitLink:
            return f"{obj.satelitLink[:30]}..." if len(obj.satelitLink) > 30 else obj.satelitLink
        return "-"
    satelitLink_preview.short_description = "Сателлит ссылка"
    
    def satellites_count(self, obj):
        """Количество доменов-сателлитов"""
        return obj.satelitDomens.count()
    satellites_count.short_description = "Кол-во доменов"
    
    def related_count(self, obj):
        """Количество связанных товаров"""
        return obj.related_products.count()
    related_count.short_description = "Связанные товары"
