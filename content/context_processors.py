from baw import settings
from .models import MenuItem


def header_menu(request):
    menu_items = MenuItem.objects.filter(menu__pk=1, is_active=True)

    return {
        'header_menu_items': menu_items,
    }


def static_version(request):
    return {
        'staticfiles_version': getattr(settings, 'STATICFILES_VERSION', '1.0'),
    }
