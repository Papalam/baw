import os
import uuid
from io import BytesIO

from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
UPLOAD_DIR = 'ckeditor_uploads/'


@csrf_exempt
def ckeditor_upload(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Нет доступа'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не разрешён'}, status=405)

    upload = request.FILES.get('upload')
    if not upload:
        return JsonResponse({'error': 'Файл не получен'}, status=400)

    ext = os.path.splitext(upload.name)[1].lstrip('.').lower()
    if ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({'error': 'Разрешены только jpg, jpeg, png'}, status=400)

    try:
        with Image.open(upload) as img:
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')

            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=85, optimize=True)
            buffer.seek(0)

        filename = uuid.uuid4().hex + '.webp'
        path = default_storage.save(UPLOAD_DIR + filename, ContentFile(buffer.read()))
        url = default_storage.url(path)

    except Exception as e:
        return JsonResponse({'error': f'Ошибка обработки: {e}'}, status=500)

    return JsonResponse({'url': url})
