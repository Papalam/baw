from django.core.validators import FileExtensionValidator
from django.db import models


class BaseModel(models.Model):
    """Абстрактная базовая модель с сортировкой и активностью"""
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Порядок сортировки"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )

    class Meta:
        abstract = True  # Не создает таблицу в БД
        ordering = ['order']


class Menu(BaseModel):
    """Модель меню"""
    title = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название меню"
    )

    class Meta:
        verbose_name = "Меню"
        verbose_name_plural = "Меню"

    def __str__(self):
        return self.title


class MenuItem(BaseModel):
    """Пункт меню"""
    title = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name="Название пункта"
    )
    url = models.CharField(
        max_length=255,
        verbose_name="URL"
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name='items',  # Более короткое и понятное
        verbose_name="Меню"
    )

    class Meta:
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"


class GeneralInfo(BaseModel):
    """Общая информация"""
    key = models.CharField(
        max_length=50,
        verbose_name='Ключ записи на EN',
        blank=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название поля'
    )
    value = models.CharField(
        max_length=255,
        verbose_name='Значение поля'
    )
    desc = models.TextField(
        verbose_name='Описание использования',
        blank=True
    )

    def __str__(self):
        return f'{self.name}: {self.value}'

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'Общая информация'


class CompanyInfo(BaseModel):
    """Информация о компании"""
    key = models.CharField(
        max_length=50,
        verbose_name='Ключ записи на EN',
        blank=True
    )
    name = models.CharField(
        max_length=250,
        verbose_name='Название поля'
    )
    value = models.TextField(
        verbose_name='Значение поля'
    )
    desc = models.TextField(
        verbose_name='Описание использования',
        blank=True
    )
    is_display_in_company_details = models.BooleanField(
        default=False,
        verbose_name="Отображать в карточке компании"
    )
    microdata = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Микроразметка schema.org'
    )

    def __str__(self):
        return f'{self.name}: {self.value}'

    class Meta:
        verbose_name = 'запись о компании'
        verbose_name_plural = 'Информация о компании'


class HTMLContent(BaseModel):
    """HTML фрагменты"""
    key = models.CharField(
        max_length=50,
        verbose_name='Ключ записи на EN',
        blank=True
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название поля'
    )
    value = models.TextField(
        verbose_name='Значение поля'
    )
    desc = models.TextField(
        verbose_name='Описание использования',
        blank=True
    )

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'запись'
        verbose_name_plural = 'HTML фрагменты'


class HeroSection(BaseModel):
    """Блоки видео на странице"""
    video_file = models.FileField(
        upload_to='hero_videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        verbose_name='Фоновое видео MP4'
    )

    # main-top__name
    car_model = models.CharField(
        max_length=50,
        verbose_name='Модель автомобиля',
        help_text='Например: BAW 212'
    )

    # h1
    main_title = models.CharField(
        max_length=200,
        verbose_name='Главный заголовок H1',
        help_text='Например: готов к любым дорогам'
    )

    # main-top__price-title
    price_title = models.CharField(
        max_length=100,
        verbose_name='Заголовок цены',
        default='СПЕЦИАЛЬНАЯ ЦЕНА ОТ:',
        help_text='Текст перед основной ценой'
    )

    # main-top__price-num
    price_value = models.CharField(
        max_length=50,
        verbose_name='Цена',
        help_text='Например: 4 440 000 ₽'
    )

    # main-top__btn текст
    button_text = models.CharField(
        max_length=100,
        verbose_name='Текст кнопки',
        default='СТАТЬ ВЛАДЕЛЬЦЕМ'
    )

    # main-top__btn ссылка
    button_url = models.CharField(
        max_length=100,
        verbose_name='Ссылка кнопки',
        help_text='Ссылка на страницу (например /) или идентификатор блока (например #price-section)',
        blank=True,
        null=True
    )

    bottom_title_text = models.CharField(
        max_length=200,
        verbose_name='Заголовок описания',
        help_text='Заголовок под блоком видео'
    )

    bottom_description_text = models.TextField(
        verbose_name='Текст описания',
        blank=True,
        help_text='Текст описания под блоком видео'
    )

    bottom_button_text = models.CharField(
        max_length=100,
        verbose_name='Текст кнопки'
    )

    bottom_button_url = models.CharField(
        max_length=100,
        verbose_name='Ссылка кнопки',
        help_text='Ссылка на страницу (например /) или идентификатор блока (например #price-section)',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    class Meta:
        verbose_name = 'Hero-секция'
        verbose_name_plural = 'Hero-секции'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.car_model} - {self.main_title}"
