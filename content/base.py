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