from django.contrib import admin
from .models import Response


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    """Админ-панель для ответов"""
    
    # Список отображаемых полей
    list_display = (
        'id',
        'domen',
        'user',
        'model',
        'assistant',
        'source',
        'parametrs_preview',
        'html_preview',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'source',
        'domen',
        'user',
        'model',
        'assistant',
        'createAt',
    )
    
    # Поля для поиска
    search_fields = (
        'domen',
        'user',
        'model',
        'assistant',
        'parametrs',
        'html',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Все поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('domen', 'source')
        }),
        ('Входные параметры', {
            'fields': ('parametrs',),
            'description': 'JSON или текстовые данные входных параметров'
        }),
        ('Использованные компоненты', {
            'fields': ('user', 'model', 'assistant')
        }),
        ('HTML ответ', {
            'fields': ('html',),
            'classes': ('collapse',)
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt',)
    
    # Поля для быстрого редактирования в списке
    # list_editable = ('source',)  # Можно раскомментировать если нужно
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    # Действия
    actions = ['export_as_json', 'mark_as_manual', 'mark_as_excel']
    
    def parametrs_preview(self, obj):
        """Превью параметров (первые 50 символов)"""
        if obj.parametrs:
            return f"{obj.parametrs[:50]}..." if len(obj.parametrs) > 50 else obj.parametrs
        return "-"
    parametrs_preview.short_description = "Параметры (превью)"
    
    def html_preview(self, obj):
        """Превью HTML (первые 50 символов)"""
        if obj.html:
            return f"{obj.html[:50]}..." if len(obj.html) > 50 else obj.html
        return "-"
    html_preview.short_description = "HTML (превью)"
    
    def mark_as_manual(self, request, queryset):
        """Пометить как ручной ввод"""
        updated = queryset.update(source='manual')
        self.message_user(request, f'{updated} записей отмечено как "Ручной ввод"')
    mark_as_manual.short_description = "Отметить как ручной ввод"
    
    def mark_as_excel(self, request, queryset):
        """Пометить как из Excel"""
        updated = queryset.update(source='excel')
        self.message_user(request, f'{updated} записей отмечено как "Из Excel"')
    mark_as_excel.short_description = "Отметить как из Excel"
    
    def export_as_json(self, request, queryset):
        """Экспорт выбранных записей в JSON (заготовка)"""
        # Здесь можно добавить логику экспорта
        self.message_user(request, f'Выбрано {queryset.count()} записей для экспорта')
    export_as_json.short_description = "Экспортировать в JSON"
