from django.db.models.signals import post_save
from django.dispatch import receiver

from catalog.models import ConfigurationImage
from content.models import CardConfigurationImage
from catalog.utils import generate_webp


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


@receiver(post_save, sender=CardConfigurationImage)
def handle_configuration_card(sender, instance, created, **kwargs):
    """Сохранение фото в формате webp"""
    if created and not instance.webp_image:
        generate_webp(instance)
