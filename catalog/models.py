import uuid

from django.core.exceptions import ValidationError
from django.db import models

from catalog.utils import default_configuration_slug
from content.base import BaseModel

COLOR_TYPE_CHOICE = [
    ('exterior', 'Экстерьер'),
    ('interior', 'Интерьер')
]


class Group(BaseModel):
    """Группа характеристик (например Двигатель, Комфорт)"""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название группы'
    )
    is_visible = models.BooleanField(
        default=True,
        verbose_name='Видимость'
    )
    key = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ключ',
        help_text='Используется в сочетании с видимостью, нужно для выбора группы характеристик по ключу'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'группу характеристик'
        verbose_name_plural = 'Группы характеристик'


class Characteristic(BaseModel):
    """Характеристика (например мощность)"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название характеристики'
    )
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='characteristics')
    unit = models.CharField(
        max_length=255,
        unique=True,
        blank=True,
        verbose_name='Единица измерения',
        help_text='например л.с.',
    ),
    image = models.ImageField(
        upload_to='characteristics/',
        blank=True,
        null=True,
        verbose_name='Иконка',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'характеристика'
        verbose_name_plural = 'Характеристики автомобиля'


class Car(BaseModel):
    """Базовый класс автомобиля"""
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Модель автомобиля'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'автомобиль'
        verbose_name_plural = 'Автомобили (модели)'


class Configuration(BaseModel):
    """Комплектация автомобиля"""
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='configurations'
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Название комплектации',
    )
    price = models.DecimalField(
        max_digits=14,
        decimal_places=0,
        blank=True,
        null=True,
        verbose_name='цена'
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        default=default_configuration_slug,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'комплекция'
        verbose_name_plural = 'Комплектации'


class ConfigurationCharacteristic(BaseModel):
    """Значение характеристики для комплектации"""
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        related_name='characteristics',
        verbose_name='Комплектация'
    )
    characteristic = models.ForeignKey(
        Characteristic,
        on_delete=models.CASCADE,
        related_name='configurations',
        verbose_name='Характеристика',
    )
    value = models.CharField(
        max_length=100,
        verbose_name='Значение'
    )

    def __str__(self):
        return f'{self.configuration}: {self.characteristic} - {self.value}'

    class Meta:
        unique_together = ['configuration', 'characteristic']
        verbose_name = 'значение'
        verbose_name_plural = 'Значения характеристик'


class ConfigurationImage(BaseModel):
    """Изображение комплектаций"""
    configuration = models.ForeignKey(
        Configuration,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Изображение'
    )
    image = models.ImageField(
        upload_to='configuration/original/%Y/%m/%d',
        verbose_name='Изображение'
    )
    webp_image = models.ImageField(
        upload_to='configuration/webp/%Y/%m/%d',
        blank=True,
        null=True,
    )
    alt = models.CharField(
        max_length=255,
        blank=True,
    )
    is_main = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f'Фото {self.pk}'

    class Meta:
        verbose_name = 'изображение'
        verbose_name_plural = 'Изображения'
        ordering = ['order']


class Color(BaseModel):
    """Цвета для интерьера и экстерьера"""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название цвета'
    )
    color_type = models.CharField(
        max_length=8,
        choices=COLOR_TYPE_CHOICE,
        verbose_name='Тип цвета'
    )
    hex_code = models.CharField(
        max_length=7,
        blank=True,
        verbose_name='Цвет',
        help_text='#FF0000'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'цвет'
        verbose_name_plural = 'Цвета'
        unique_together = ['color_type', 'name']


class CarImage(BaseModel):
    """Фото автомобиля с привязкой к цвету"""
    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Автомобиль'
    )
    image_type = models.CharField(
        max_length=8,
        choices=COLOR_TYPE_CHOICE,
        verbose_name='Тип фото'
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.PROTECT,
        related_name='images',
        verbose_name='Цвет'
    )
    image = models.ImageField(
        upload_to='cars/original/%Y/%m/%d',
        verbose_name='Фото автомобиля'
    )
    webp_image = models.ImageField(
        upload_to='cars/webp/%Y/%m/%d',
        blank=True,
        null=True,
    )

    def __str__(self):
        return f'{self.car.name} - {self.color.name} ({self.get_image_type_display()})'

    def clean(self):
        """Проверка соответствия типов"""
        if not self.image_type == self.color.color_type:
            raise ValidationError('Тип фото должен совпадать с типом цвета')

    class Meta:
        verbose_name = 'фото автомобиля'
        verbose_name_plural = 'Фото автомобилей'
