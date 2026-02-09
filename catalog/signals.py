import os
from io import BytesIO

from PIL import Image
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver

from catalog.models import ConfigurationImage, Configuration


@receiver(post_save, sender=ConfigurationImage)
def handle_configuration_image(sender, instance, created, **kwargs):
    """Логика после сохранения фото"""
    configuration = instance.configuration

    # Если первая фотография - делаем её главной
    if created and not configuration.images.filter(is_main=True).exists():
        instance.is_main = True
        instance.save(update_fields=['is_main'])

    # Сбрасываем другие основные фото
    elif instance.is_main:
        sender.objects.filter(
            configuration=configuration,
            is_main=True,
        ).exclude(pk=instance.pk).update(is_main=False)

    if created or not instance.webp_image:
        generate_webp(instance)


def generate_webp(instance):
    """Создает дополнительное WebP фото"""
    try:
        # Открываем оригинал
        with Image.open(instance.image.path) as img:
            # Конвертируем в RGB (требуется для WebP)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Буферизируем WebP
            buffer = BytesIO()
            img.save(
                buffer,
                format='WEBP',
                quality=85,
                optimize=True
            )

            # Сохраняем как дополнительное поле
            filename = os.path.splitext(os.path.basename(instance.image.name))[0] + '.webp'
            instance.webp_image.save(filename, File(buffer), save=False)
            instance.save(update_fields=['webp_image'])

    except Exception:
        # Если ошибка - оставляем оригинал
        pass
