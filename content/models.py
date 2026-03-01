from django.core.validators import FileExtensionValidator
from django.db import models

from catalog.models import Configuration, Color
from content.base import BaseModel


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

    def __str__(self):
        return self.title

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


class CardConfiguration(BaseModel):
    title = models.TextField(
        verbose_name='Описание'
    )
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        related_name='cards',
        verbose_name='Комплектация'
    )

    def __str__(self):
        return f'{self.configuration}'

    class Meta:
        verbose_name = 'карточка комплектаций'
        verbose_name_plural = 'Карточки комплектаций'


class CardConfigurationFeature(BaseModel):
    """Свойства для блока карточки комплектаций"""
    card_configuration = models.ForeignKey(
        CardConfiguration,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name='Карточка комплектации'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    icon = models.FileField(
        upload_to='cards/icons/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
        verbose_name='Иконка'
    )
    value = models.CharField(
        max_length=100,
        verbose_name='Значение'
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Единица измерения',
        help_text='Например Л.С'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'особенность комплектации'
        verbose_name_plural = 'Особенности комплектации'


class CardConfigurationImage(BaseModel):
    """Изображения для блока с карточками комплектаций"""
    card_configuration = models.ForeignKey(
        CardConfiguration,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Карточка комплектации'
    )
    title = models.TextField(
        max_length=100,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name="Описание"
    )
    image = models.ImageField(
        upload_to='cards/images/original/',
        validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'jpg'])],
        verbose_name='Изображение'
    )
    webp_image = models.ImageField(
        upload_to='cards/webp/',
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
    )


class Question(BaseModel):
    """Блок вопросов и ответов"""
    question = models.TextField(
        max_length=255,
        verbose_name='Вопрос',
        help_text='Максимальная длина вопроса 255 символов',
    )
    answer = models.TextField(
        verbose_name='Ответ',
        help_text='Максимальная длина не ограничена'
    )

    def __str__(self):
        return f'{self.question}'

    class Meta:
        verbose_name = 'вопрос-ответ'
        verbose_name_plural = 'Вопросы и ответы'


class BawComparison(BaseModel):
    """Блок сравнение комплектаций Baw"""
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок',
        help_text='Заголовок блока'
    )
    title_form = models.CharField(
        max_length=200,
        verbose_name='Заголовок формы'
    )
    sub_title_form = models.CharField(
        max_length=255,
        verbose_name='Подзаголовок формы'
    )
    text_form = models.TextField(
        verbose_name='Текст формы'
    )
    text_red_button = models.CharField(
        max_length=100,
        verbose_name='Текст красной кнопки'
    )
    url_red_button = models.CharField(
        max_length=50,
        verbose_name='Url красной кнопки'
    )
    text_black_button = models.CharField(
        max_length=100,
        verbose_name='Текст черной кнопки'
    )
    url_black_button = models.CharField(
        max_length=50,
        verbose_name='Url черной кнопки'
    )
    image = models.ImageField(
        upload_to='comparisons/original/',
        blank=True,
        null=True,
        verbose_name='Изображение блока'
    )
    webp_image = models.ImageField(
        upload_to='comparisons/webp/',
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f'Форма сравнения #{self.pk}'

    class Meta:
        verbose_name = 'форма'
        verbose_name_plural = 'Формы сравнения'


class BawComparisonConfiguration(BaseModel):
    form = models.ForeignKey(
        BawComparison,
        on_delete=models.CASCADE,
        related_name='configurations',

    )
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        related_name='comparisons',
        verbose_name='Комплектация'
    )

    def __str__(self):
        return f'{self.form} - {self.configuration}'

    class Meta:
        verbose_name = 'конфигурацию'
        verbose_name_plural = 'Сравнение конфигураций'


class BawTesting(BaseModel):
    """Блок испытаний Baw"""
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок блока'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Текст под заголовком'
    )
    video = models.FileField(
        upload_to='testing/video/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        verbose_name='Фоновое видео MP4'
    )
    subtitle = models.CharField(
        max_length=255,
        verbose_name='Второй заголовок',
        help_text='Заголовок под блоком видео',
    )
    title_full_control = models.CharField(
        max_length=255,
        verbose_name='Третий заголовок',
        help_text='Заголовок под блоком с 3 фото'
    )
    image = models.FileField(
        upload_to='testing/images/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
        verbose_name='Изображение',
        help_text='Изображение в блоке полного контроля'
    )
    alt = models.CharField(
        max_length=50,
        blank=True,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'блок'
        verbose_name_plural = 'Блок проходимости (контроль)'


class BawTestingFeature(BaseModel):
    block = models.ForeignKey(
        BawTesting,
        on_delete=models.CASCADE,
        related_name='features',
        verbose_name='Блок проходимости'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    icon = models.FileField(
        upload_to='testing/icons/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
        verbose_name='Иконка'
    )
    value = models.CharField(
        max_length=100,
        verbose_name='Значение'
    )
    unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Единица измерения',
        help_text='Например Л.С'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'особенность'
        verbose_name_plural = 'Особенности'


class BawTestingImage(BaseModel):
    block = models.ForeignKey(
        BawTesting,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Блок'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='testing/images/',
        verbose_name='Изображение'
    )
    webp_image = models.ImageField(
        upload_to='testing/webp/',
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=50,
        blank=True,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'изображение'
        verbose_name_plural = 'Изображения'


class BawTestingItems(BaseModel):
    """Пункты для блока МЕХАНИКА ПОД ПОЛНЫМ КОНТРОЛЕМ"""
    block = models.ForeignKey(
        BawTesting,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Блок'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    value = models.CharField(
        max_length=10,
        verbose_name='Обозначение',
        help_text='Например 2H или 4L'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Пункты блока механика'
        verbose_name_plural = 'Механика под полным контролем'


class VideoCard(BaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'блок'
        verbose_name_plural = 'Видеоблок'


class VideoCardContent(BaseModel):
    block = models.ForeignKey(
        VideoCard,
        on_delete=models.CASCADE,
        related_name='content',
        verbose_name='Блок'
    )
    image = models.ImageField(
        upload_to='video-blocks/images/',
        verbose_name='Превью'
    )
    webp_image = models.ImageField(
        upload_to='video-blocks/webp/',
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=50,
        blank=True,
    )
    video = models.FileField(
        upload_to='video-blocks/video/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        verbose_name='Видео'
    )


class TechnologyBlock(BaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Текст',
        help_text='Расположен под заголовком'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'блок'
        verbose_name_plural = 'Технологии'


class TechnologyBlockContent(BaseModel):
    block = models.ForeignKey(
        TechnologyBlock,
        on_delete=models.CASCADE,
        related_name='content',
        verbose_name='блок'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Текст'
    )
    image = models.ImageField(
        upload_to='technology-blocks/images/',
        validators=[FileExtensionValidator(allowed_extensions=['jpeg', 'png', 'jpg'])],
        verbose_name='Изображение'
    )
    webp_image = models.ImageField(
        upload_to='technology-blocks/webp/',
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=50,
        blank=True,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'карточка'
        verbose_name_plural = 'Карточки технологий'


class ServicesBlock(BaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    icon = models.FileField(
        upload_to='services/icons/',
        validators=[FileExtensionValidator(allowed_extensions=['svg'])],
        verbose_name='Иконка'
    )
    slug = models.SlugField(
        unique=True,
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'сервис'
        verbose_name_plural = 'Сервисы'


class NewsBase(BaseModel):
    """Базовая модель новости"""
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Текст новости'
    )
    slug = models.SlugField(
        unique=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Создано'
    )

    class Meta:
        abstract = True


class NewsArticle(NewsBase):
    """Новости в статьях"""
    image = models.ImageField(
        upload_to='news/images/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        verbose_name='Изображение'
    )
    webp_image = models.ImageField(
        upload_to='news/webp/',
        blank=True,
        null=True,
    )
    is_main = models.BooleanField(
        default=False,
        verbose_name='Показывать на главной странице'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'новость'
        verbose_name_plural = 'Новости (статьи)'
        unique_together = (('title', 'created_at'),)


class NewsVideo(NewsBase):
    """Новостные видеоролики"""
    video = models.FileField(
        upload_to='news/video/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        verbose_name='Видео'
    )

    class Meta:
        verbose_name = 'новость'
        verbose_name_plural = 'Новости (видео)'
        unique_together = (('title', 'created_at'),)


class CarApplication(models.Model):
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.PROTECT,
        related_name='car_applications',
        verbose_name='Комплектация'
    )
    outside_color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        limit_choices_to={'color_type': 'exterior'},
        related_name='outside_applications',
        verbose_name='Цвет экстерьера'
    )
    inside_color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        limit_choices_to={'color_type': 'interior'},
        related_name='inside_applications',
        verbose_name='Цвет интерьера'
    )
    dealer = models.CharField(
        max_length=255,
        verbose_name='Дилер'
    )
    first_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Фамилия'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Телефон'
    )
    agreement = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку персональных данных'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'заявка'
        verbose_name_plural = 'Заявки'


class OurAdventure(BaseModel):
    title = models.CharField(
        max_length=255,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        unique=True,
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Название'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='our_adventure/images/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        verbose_name='Обложка'
    )
    webp_image = models.ImageField(
        upload_to='our_adventure/webp/',
        blank=True,
        null=True
    )
    video = models.FileField(
        upload_to='our_adventure/video/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4'])],
        verbose_name='Видео'
    )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'приключение'
        verbose_name_plural = 'Наши приключения'


class History(BaseModel):
    title = models.CharField(
        max_length=100,
        verbose_name='Заголовок'
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Город'
    )
    description = models.TextField(
        verbose_name='Отзыв'
    )
    image = models.ImageField(
        upload_to='history/images/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    webp_image = models.ImageField(
        upload_to='history/webp/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.title} - {self.city}'

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы клиентов'


class Society(BaseModel):
    key = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Ключ записи'
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    button_title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Заголовок кнопки'
    )
    button_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Текст кнопки'
    )
    button_url = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='URL кнопки'
    )
    image = models.ImageField(
        upload_to='society/images/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    webp_image = models.ImageField(
        upload_to='society/webp/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.title} - {self.key}'

    class Meta:
        verbose_name = 'сообщество'
        verbose_name_plural = 'Сообщества'


class Banner(BaseModel):
    key = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Ключ баннера'
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    image = models.ImageField(
        upload_to='banner/images/',
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])],
    )
    webp_image = models.ImageField(
        upload_to='banner/webp/',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'{self.title} - {self.key}'

    class Meta:
        verbose_name = 'баннер'
        verbose_name_plural = 'Баннеры'
