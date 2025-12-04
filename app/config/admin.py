from django.contrib import admin
from .models import Models, Assistant, Inputer, AssistantInputer


@admin.register(Models)
class ModelsAdmin(admin.ModelAdmin):
    """Админ-панель для AI моделей"""
    
    list_display = (
        'id',
        'name',
        'url',
        'key_preview',
        'is_active',
        'createAt',
    )
    
    list_filter = (
        'is_active',
        'createAt',
    )
    
    search_fields = (
        'name',
        'url',
        'key',
    )
    
    ordering = ('-createAt',)
    
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
    
    readonly_fields = ('createAt',)
    list_editable = ('is_active',)
    list_per_page = 25
    date_hierarchy = 'createAt'
    
    def key_preview(self, obj):
        if obj.key:
            return f"{obj.key[:20]}..." if len(obj.key) > 20 else obj.key
        return "-"
    key_preview.short_description = "Ключ (превью)"


@admin.register(Inputer)
class InputerAdmin(admin.ModelAdmin):
    """Админ-панель для полей ввода"""
    
    list_display = (
        'id',
        'name',
        'label',
        'type',
        'size',
        'placement_preview',
        'type_select',
        'assistants_count',
        'createAt',
    )
    
    list_filter = (
        'type',
        'size',
        'type_select',
        'createAt',
    )
    
    search_fields = (
        'name',
        'label',
        'placement',
    )
    
    ordering = ('-createAt',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'label', 'type')
        }),
        ('Настройки поля', {
            'fields': ('size', 'placement', 'type_select'),
            'description': 'Поля автоматически настраиваются в зависимости от типа'
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('createAt',)
    list_per_page = 25
    date_hierarchy = 'createAt'
    
    def placement_preview(self, obj):
        if obj.placement:
            return f"{obj.placement[:30]}..." if len(obj.placement) > 30 else obj.placement
        return "-"
    placement_preview.short_description = "Подсказка"
    
    def assistants_count(self, obj):
        return obj.assistants.count()
    assistants_count.short_description = "Кол-во ассистентов"


class AssistantInputerInline(admin.TabularInline):
    """Inline для редактирования связей Inputer в Assistant"""
    model = AssistantInputer
    extra = 1
    verbose_name = "Поле ввода"
    verbose_name_plural = "Поля ввода"
    
    fields = ('inputer', 'required', 'createAt')
    readonly_fields = ('createAt',)
    autocomplete_fields = ['inputer']


@admin.register(AssistantInputer)
class AssistantInputerAdmin(admin.ModelAdmin):
    """Админ-панель для связей Ассистент-Инпутер"""
    
    list_display = (
        'id',
        'assistant',
        'inputer',
        'required',
        'createAt',
    )
    
    list_filter = (
        'required',
        'assistant',
        'createAt',
    )
    
    search_fields = (
        'assistant__title',
        'inputer__name',
        'inputer__label',
    )
    
    ordering = ('assistant', 'id')
    
    fieldsets = (
        ('Связь', {
            'fields': ('assistant', 'inputer')
        }),
        ('Настройки', {
            'fields': ('required',)
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('createAt',)
    autocomplete_fields = ['assistant', 'inputer']
    list_per_page = 25
    list_editable = ('required',)


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    """Админ-панель для ассистентов"""
    
    list_display = (
        'id',
        'title',
        'instruction_preview',
        'maks_token',
        'temperatures',
        'input_columns_count',
        'createAt',
    )
    
    list_filter = (
        'createAt',
        'maks_token',
        'temperatures',
    )
    
    search_fields = (
        'title',
        'instruction',
    )
    
    ordering = ('-createAt',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'instruction')
        }),
        ('Параметры AI', {
            'fields': ('maks_token', 'temperatures')
        }),
        ('Системные данные', {
            'fields': ('createAt',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('createAt',)
    inlines = [AssistantInputerInline]
    list_per_page = 25
    date_hierarchy = 'createAt'
    
    def instruction_preview(self, obj):
        if obj.instruction:
            return f"{obj.instruction[:50]}..." if len(obj.instruction) > 50 else obj.instruction
        return "-"
    instruction_preview.short_description = "Инструкция (превью)"
    
    def input_columns_count(self, obj):
        return obj.input_columns.count()
    input_columns_count.short_description = "Кол-во полей"
