from django.contrib import admin
from django.db import models

from .models import Menu, MenuItem, HeroSection, HTMLContent
from .widgets import RichTextEditorWidget


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'is_active']
    readonly_fields = ['id']
    search_fields = ['title']
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'menu', 'order', 'is_active']
    list_display_links = ['menu', 'title', 'id']
    readonly_fields = ['id']
    search_fields = ['title', 'menu__title']
    list_filter = ('menu',)
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('menu', 'title', 'url', 'id')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ['car_model', 'main_title', 'id', 'is_active']
    list_display_links = ['car_model', 'main_title', 'id']
    readonly_fields = ['id', 'created_at']
    search_fields = ['car_model', 'main_title']
    list_filter = ('car_model',)
    ordering = ['order', 'id']
    fieldsets = (
        ('Блок видео', {
            'fields': ('car_model', 'main_title', 'price_title', 'price_value', 'button_text', 'video_file',
                       'button_url', 'created_at')
        }),
        ('Описание под блоком с видео', {
            'fields': ('bottom_title_text', 'bottom_description_text', 'bottom_button_text', 'bottom_button_url')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(HTMLContent)
class HTMLContentAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'id']
    list_display_links = ['name', 'key', 'id']
    readonly_fields = ['id']
    search_fields = ['value', 'desc']
    ordering = ['order', 'id']

    formfield_overrides = {
        models.TextField: {'widget': RichTextEditorWidget}
    }


admin.site.site_header = "Администрирование сайта Baw"
