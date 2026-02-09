from .models import MenuItem


def header_menu(request):
    menu_items = MenuItem.objects.filter(menu__pk=1, is_active=True)

    return {
        'header_menu_items': menu_items,
    }
