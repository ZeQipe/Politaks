from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from app.config.models import Assistant


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
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    firstName = models.CharField(max_length=150, verbose_name='Имя')
    lastName = models.CharField(max_length=150, verbose_name='Фамилия')
    login = models.CharField(max_length=150, unique=True, verbose_name='Логин')
    password = models.CharField(max_length=128, verbose_name='Пароль')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name='Роль')
    default_excel_url = models.CharField(max_length=500, null=True, blank=True, verbose_name='URL Excel по умолчанию')
    assistants = models.ManyToManyField(
        Assistant,
        through='UserAssistant',
        blank=True,
        related_name='users',
        verbose_name='Ассистенты'
    )
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


class UserAssistant(models.Model):
    """Промежуточная таблица для связи User и Assistant"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_assistants',
        verbose_name='Пользователь'
    )
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='assistant_users',
        verbose_name='Ассистент'
    )
    sheets_id = models.IntegerField(null=True, blank=True, verbose_name='ID листа')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'user_assistant'
        verbose_name = 'Связь Пользователь-Ассистент'
        verbose_name_plural = 'Связи Пользователь-Ассистент'
        unique_together = ['user', 'assistant']
        ordering = ['id']
    
    def __str__(self):
        return f"{self.user.login} - {self.assistant.title} (sheets_id: {self.sheets_id})"
