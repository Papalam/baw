from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from catalog.models import ConfigurationImage, CarImage
from content.models import CardConfigurationImage, BawComparison, BawTestingImage, VideoCardContent, \
    TechnologyBlockContent, NewsArticle
from catalog.utils import generate_webp


@receiver(pre_save, sender=CardConfigurationImage)
@receiver(pre_save, sender=BawComparison)
@receiver(pre_save, sender=BawTestingImage)
@receiver(pre_save, sender=VideoCardContent)
@receiver(pre_save, sender=TechnologyBlockContent)
@receiver(pre_save, sender=NewsArticle)
@receiver(pre_save, sender=CarImage)
def detect_image_changes(sender, instance, **kwargs):
    """Определяем что изображение поменялось"""
    if instance.pk:
        old_image = sender.objects.only('image').get(pk=instance.pk)
        instance._image_changed = old_image != instance.image
    else:
        instance._image_changed = True


@receiver(post_save, sender=CardConfigurationImage)
@receiver(post_save, sender=BawComparison)
@receiver(post_save, sender=BawTestingImage)
@receiver(post_save, sender=VideoCardContent)
@receiver(post_save, sender=TechnologyBlockContent)
@receiver(post_save, sender=NewsArticle)
@receiver(post_save, sender=CarImage)
def handle_configuration_card(sender, instance, update_fields, **kwargs):
    """Сохранение фото в формате webp"""
    if update_fields and 'webp_image' in update_fields:
        return

    if not getattr(instance, '_image_changed', False):
        return

    delattr(instance, '_image_changed')

    # Генерируем файл
    generate_webp(instance)


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
