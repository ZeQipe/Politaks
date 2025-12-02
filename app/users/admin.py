from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms
from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Форма создания пользователя"""
    
    class Meta:
        model = User
        fields = ('login', 'firstName', 'lastName', 'role')


class CustomUserChangeForm(UserChangeForm):
    """Форма изменения пользователя"""
    
    class Meta:
        model = User
        fields = '__all__'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для модели User"""
    
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Список отображаемых полей
    list_display = (
        'id',
        'login',
        'firstName',
        'lastName',
        'role',
        'is_active',
        'is_superuser',
        'createAt',
    )
    
    # Поля для фильтрации
    list_filter = (
        'role',
        'is_active',
        'is_superuser',
        'createAt',
    )
    
    # Поля для поиска
    search_fields = (
        'login',
        'firstName',
        'lastName',
    )
    
    # Сортировка по умолчанию
    ordering = ('-createAt',)
    
    # Поля, доступные для редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('login', 'password')
        }),
        ('Персональные данные', {
            'fields': ('firstName', 'lastName')
        }),
        ('Права доступа', {
            'fields': ('role', 'is_active', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важные даты', {
            'fields': ('createAt', 'last_login')
        }),
    )
    
    # Поля при создании нового пользователя
    add_fieldsets = (
        ('Обязательные поля', {
            'classes': ('wide',),
            'fields': ('login', 'firstName', 'lastName', 'password1', 'password2', 'role'),
        }),
        ('Дополнительные настройки', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_superuser'),
        }),
    )
    
    # Поля только для чтения
    readonly_fields = ('createAt', 'last_login')
    
    # Поля для быстрого редактирования в списке
    list_editable = ('is_active',)
    
    # Количество элементов на странице
    list_per_page = 25
    
    # Дата иерархия
    date_hierarchy = 'createAt'
    
    # Включаем фильтр по связанным полям
    filter_horizontal = ('groups', 'user_permissions')
