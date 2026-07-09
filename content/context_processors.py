from collections import defaultdict

from django.shortcuts import get_object_or_404

from baw import settings
from catalog.models import Dealership
from .models import MenuItem, SocialNetwork, CompanyInfo


def header_menu(request):
    menu_items = MenuItem.objects.filter(menu__pk=1, is_active=True)

    return {
        'header_menu_items': menu_items,
    }


def footer_menu(request):
    footer_dealerships = Dealership.objects.filter(is_active=True).order_by('order').values('city', 'address', 'slug')
    social_networks = SocialNetwork.objects.filter(is_active=True).order_by('order')
    qs = CompanyInfo.objects.filter(is_active=True, key__isnull=False).exclude(key='').order_by('name')

    company = {}
    company_list = defaultdict(list)
    for obj in qs:
        company[obj.key] = obj
        # Группируем по префиксу до первого "_" + цифры
        # phone_1, phone_2 → group key = "phone"
        base = obj.key.rstrip('_0123456789')
        company_list[base].append(obj)

    def get_children(menu_key):
        return MenuItem.objects.filter(
            menu__key=menu_key,
            is_active=True
        ).select_related('menu').order_by('order')

    return {
        'footer_menu_models': get_children('footer_models'),
        'footer_menu_customers': get_children('footer_customers'),
        'footer_menu_owners': get_children('footer_owners'),
        'footer_menu_baw_russia': get_children('footer_baw_russia'),
        'footer_dealerships': footer_dealerships,
        'social_networks': social_networks,
        'company': company,
        'company_list': dict(company_list),
    }


def static_version(request):
    return {
        'staticfiles_version': getattr(settings, 'STATICFILES_VERSION', '1.0'),
    }


def yandex_metrika(request):
    return {
        'YANDEX_METRIKA_ID': getattr(settings, 'YANDEX_METRIKA_ID', ''),
    }
