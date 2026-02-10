from django.db import models

from content.base import BaseModel


class Group(BaseModel):
    """Группа характеристик (например Двигатель, Комфорт)"""
    name = models.CharField(
        max_length=255,
        unique=True,
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
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='цена'
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
