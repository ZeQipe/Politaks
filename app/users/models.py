from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    """Менеджер для кастомной модели User"""
    
    def create_user(self, login, password=None, **extra_fields):
        """Создает и сохраняет обычного пользователя"""
        if not login:
            raise ValueError('Поле login обязательно')
        
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, login, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя"""
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        return self.create_user(login, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя"""
    
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    firstName = models.CharField(max_length=150, verbose_name='Имя')
    lastName = models.CharField(max_length=150, verbose_name='Фамилия')
    login = models.CharField(max_length=150, unique=True, verbose_name='Логин')
    password = models.CharField(max_length=128, verbose_name='Пароль')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='Роль')
    is_superuser = models.BooleanField(default=False, verbose_name='Суперпользователь')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['firstName', 'lastName', 'role']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-createAt']
    
    def __str__(self):
        return f"{self.firstName} {self.lastName} ({self.login})"
    
    @property
    def is_staff(self):
        """Свойство для доступа к админке Django"""
        return self.is_superuser or self.role == 'admin'
