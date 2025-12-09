from django.db import models
from django.utils import timezone


class Models(models.Model):
    """Модель AI моделей"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Название')
    url = models.CharField(max_length=500, verbose_name='URL')
    encrypted_key = models.TextField(verbose_name='Зашифрованный ключ')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'models'
        verbose_name = 'AI Модель'
        verbose_name_plural = 'AI Модели'
        ordering = ['-createAt']
    
    def __str__(self):
        return self.name
    
    def set_key(self, api_key: str):
        """Шифрует и сохраняет API ключ"""
        from core.encryption import encrypt_api_key
        self.encrypted_key = encrypt_api_key(api_key)
    
    def get_key(self) -> str:
        """Расшифровывает и возвращает API ключ"""
        from core.encryption import decrypt_api_key
        return decrypt_api_key(self.encrypted_key)


class Inputer(models.Model):
    """Модель полей ввода"""
    
    TYPE_CHOICES = [
        ('single', 'Однострочное поле'),
        ('multiline', 'Многострочное поле'),
        ('photo', 'Загрузка фото'),
        ('select', 'Выбор из списка'),
    ]
    
    SIZE_CHOICES = [
        ('small', 'Маленький (s)'),
        ('medium', 'Средний (m)'),
        ('large', 'Большой (l)'),
    ]
    
    TYPE_SELECT_CHOICES = [
        ('product', 'Товар'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Внутреннее наименование')
    label = models.CharField(max_length=255, verbose_name='Отображаемое имя')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='Тип')
    size = models.CharField(
        max_length=20, 
        choices=SIZE_CHOICES, 
        null=True, 
        blank=True, 
        verbose_name='Размер',
        help_text='Только для multiline'
    )
    placement = models.CharField(
        max_length=255, 
        null=True, 
        blank=True, 
        verbose_name='Подсказка (placeholder)',
        help_text='Недоступно для photo'
    )
    type_select = models.CharField(
        max_length=50, 
        choices=TYPE_SELECT_CHOICES, 
        null=True, 
        blank=True, 
        default=None,
        verbose_name='Тип выбора',
        help_text='Только для select'
    )
    select_search = models.BooleanField(
        default=False,
        verbose_name='Поиск в select',
        help_text='Только для select'
    )
    multi_select = models.BooleanField(
        default=False,
        verbose_name='Мультивыбор',
        help_text='Только для select'
    )
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'inputer'
        verbose_name = 'Поле ввода'
        verbose_name_plural = 'Поля ввода'
        ordering = ['-createAt']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def save(self, *args, **kwargs):
        """Автоматическая установка значений в зависимости от type"""
        # single: size = None
        if self.type == 'single':
            self.size = None
            self.type_select = None
        
        # multiline: size обязателен
        elif self.type == 'multiline':
            self.type_select = None
            if not self.size:
                self.size = 'medium'
        
        # photo: size = None, placement = None
        elif self.type == 'photo':
            self.size = None
            self.placement = None
            self.type_select = None
        
        # select: фиксированные значения
        elif self.type == 'select':
            self.size = None
            self.label = 'Наименование товара'
            if not self.type_select:
                self.type_select = 'product'
        
        super().save(*args, **kwargs)
    
    def get_size_code(self):
        """Возвращает первый символ размера для фронтенда"""
        if self.size:
            return self.size[0]  # s, m, l
        return None


class Assistant(models.Model):
    """Модель ассистента"""
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    key_title = models.CharField(max_length=255, verbose_name='Ключ (системное название)')
    title = models.CharField(max_length=255, verbose_name='Название')
    instruction = models.TextField(verbose_name='Инструкция')
    maks_token = models.IntegerField(null=True, blank=True, verbose_name='Максимум токенов')
    temperatures = models.FloatField(null=True, blank=True, verbose_name='Температура')
    default_sheets_id = models.IntegerField(null=True, blank=True, verbose_name='ID листа по умолчанию')
    input_columns = models.ManyToManyField(
        Inputer,
        through='AssistantInputer',
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


class AssistantInputer(models.Model):
    """Промежуточная таблица для связи Assistant и Inputer"""
    
    REQUIRED_CHOICES = [
        ('required', 'Обязательное'),
        ('optional', 'Не обязательное'),
    ]
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    assistant = models.ForeignKey(
        Assistant,
        on_delete=models.CASCADE,
        related_name='assistant_inputers',
        verbose_name='Ассистент'
    )
    inputer = models.ForeignKey(
        Inputer,
        on_delete=models.CASCADE,
        related_name='inputer_assistants',
        verbose_name='Поле ввода'
    )
    required = models.CharField(
        max_length=20,
        choices=REQUIRED_CHOICES,
        default='required',
        verbose_name='Обязательность'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок отображения'
    )
    createAt = models.DateTimeField(default=timezone.now, verbose_name='Дата создания')
    
    class Meta:
        db_table = 'assistant_inputer'
        verbose_name = 'Связь Ассистент-Инпутер'
        verbose_name_plural = 'Связи Ассистент-Инпутер'
        unique_together = ['assistant', 'inputer']
        ordering = ['order', 'id']
    
    def __str__(self):
        return f"{self.assistant.title} - {self.inputer.name} ({self.get_required_display()})"
