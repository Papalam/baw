import os

from django.core.exceptions import ValidationError


def validate_mp4_file(value):
    """Проверка видео файла mp4"""

    ext = os.path.splitext(value)[1]
    if ext != ".mp4":
        raise ValidationError('Разрешены только MP4 файлы')
