from django.contrib import admin
from .models import Models, Assistant, Inputer


@admin.register(Models)
class ModelsAdmin(admin.ModelAdmin):
    """Админ-панель для AI моделей"""
    
    # Список отображаемых полей
    list_display = (
        'id',
        'name',
        'url',
        'key_preview',
        'is_active',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'is_active',
        'createAt',
    )
    
    # Поля для поиска
    search_fields = (
        'name',
        'url',
        'key',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Все поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'url', 'key')
        }),
        ('Настройки', {
            'fields': ('is_active',)
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt',)
    
    # Поля для быстрого редактирования в списке
    list_editable = ('is_active',)
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    def key_preview(self, obj):
        """Превью ключа (первые 20 символов)"""
        if obj.key:
            return f"{obj.key[:20]}..." if len(obj.key) > 20 else obj.key
        return "-"
    key_preview.short_description = "Ключ (превью)"


@admin.register(Inputer)
class InputerAdmin(admin.ModelAdmin):
    """Админ-панель для полей ввода"""
    
    # Список отображаемых полей
    list_display = (
        'id',
        'title',
        'type',
        'size',
        'assistants_count',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'type',
        'size',
        'createAt',
    )
    
    # Поля для поиска
    search_fields = (
        'title',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Все поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title',)
        }),
        ('Настройки поля', {
            'fields': ('type', 'size')
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt',)
    
    # Поля для быстрого редактирования в списке
    list_editable = ('type', 'size')
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    def assistants_count(self, obj):
        """Количество связанных ассистентов"""
        return obj.assistants.count()
    assistants_count.short_description = "Кол-во ассистентов"


class InputerInline(admin.TabularInline):
    """Inline для редактирования связей Inputer в Assistant"""
    model = Assistant.input_columns.through
    extra = 1
    verbose_name = "Поле ввода"
    verbose_name_plural = "Поля ввода"


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    """Админ-панель для ассистентов"""
    
    # Список отображаемых полей
    list_display = (
        'id',
        'title',
        'instruction_preview',
        'maks_token',
        'temperatures',
        'input_columns_count',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'createAt',
        'maks_token',
        'temperatures',
    )
    
    # Поля для поиска
    search_fields = (
        'title',
        'instruction',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Все поля для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'instruction')
        }),
        ('Параметры AI', {
            'fields': ('maks_token', 'temperatures')
        }),
        ('Поля ввода', {
            'fields': ('input_columns',)
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt',)
    
    # ManyToMany с удобным интерфейсом
    filter_horizontal = ('input_columns',)
    
    # Inline для связанных объектов
    # inlines = [InputerInline]
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    def instruction_preview(self, obj):
        """Превью инструкции (первые 50 символов)"""
        if obj.instruction:
            return f"{obj.instruction[:50]}..." if len(obj.instruction) > 50 else obj.instruction
        return "-"
    instruction_preview.short_description = "Инструкция (превью)"
    
    def input_columns_count(self, obj):
        """Количество полей ввода"""
        return obj.input_columns.count()
    input_columns_count.short_description = "Кол-во полей"
