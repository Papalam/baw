from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from .models import Menu, MenuItem, HeroSection, HTMLContent, CardConfiguration, CardConfigurationFeature, \
    CardConfigurationImage, Question
from .widgets import RichTextEditorWidget


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ('title', 'url', 'order', 'is_active')


class CardConfigurationFeatureInline(admin.TabularInline):
    model = CardConfigurationFeature
    extra = 1
    fields = ('title', 'icon', 'preview', 'value', 'unit', 'order', 'is_active')
    readonly_fields = ('id', 'preview')

    def preview(self, obj):
        if obj.pk and obj.icon:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px; background-color:black;" />',
                obj.icon.url
            )
        return "Фото"

    preview.short_description = "Превью"


class CardConfigurationImageInline(admin.TabularInline):
    model = CardConfigurationImage
    extra = 1
    fields = ('title', 'description', 'image', 'preview', 'alt', 'order', 'is_active')
    readonly_fields = ('id', 'preview')

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return "Фото"

    preview.short_description = "Превью"


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'is_active']
    readonly_fields = ['id']
    search_fields = ['title']
    ordering = ['order', 'id']
    inlines = [MenuItemInline]
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


@admin.register(CardConfiguration)
class CardConfigurationAdmin(admin.ModelAdmin):
    list_display = ['configuration', 'id', 'order', 'is_active']
    readonly_fields = ('id',)
    inlines = [CardConfigurationFeatureInline, CardConfigurationImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'configuration')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question', 'id', 'order', 'is_active']
    list_display_links = ['question', 'id', 'order', 'is_active']
    readonly_fields = ['id']
    search_fields = ['question']
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('question', 'answer')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


admin.site.site_header = "Администрирование сайта Baw"
