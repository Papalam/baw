import os
import uuid
from io import BytesIO

from PIL import Image
from django.core.files import File


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


def default_configuration_slug():
    """Функция используется для генерации поле slug в модели Configuration"""
    return f'config-{uuid.uuid4().hex[:8]}'
