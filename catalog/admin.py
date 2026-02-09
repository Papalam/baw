from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.utils.html import format_html

from catalog.models import Car, Group, Characteristic, Configuration, ConfigurationCharacteristic, ConfigurationImage


class ConfigurationCharacteristicInline(admin.TabularInline):
    model = ConfigurationCharacteristic
    extra = 0
    autocomplete_fields = ['characteristic']
    fields = ('characteristic', 'value')
    ordering = ('characteristic__group', 'characteristic__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request).select_related(
            'characteristic__group'
        )
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'characteristic':
            kwargs['widget'] = AutocompleteSelect(
                ConfigurationCharacteristic.characteristic.field,
                admin.site
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ConfigurationImageInline(admin.TabularInline):
    model = ConfigurationImage
    extra = 1

    readonly_fields = ('preview',)
    fields = ('image', 'alt', 'is_main', 'order', 'is_active', 'preview')

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return "Фото"

    preview.short_description = "Превью"


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'order', 'is_active')
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'id')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'order', 'is_active']
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'id')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'group', 'order', 'is_active']
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    search_fields = ['name']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'id', 'group')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'order', 'is_active']
    readonly_fields = ('id', 'get_main_image_preview')
    search_fields = ['characteristic__name']
    ordering = ('order', 'id')
    inlines = [ConfigurationCharacteristicInline, ConfigurationImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('car', 'name', 'price', 'get_main_image_preview', 'id')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def duplicate_characteristics(self, request, queryset):
        """Копирует характеристики из первой комплектации"""
        first = queryset.first()
        for config in queryset[1:]:
            for char_val in first.char_values.all():
                ConfigurationCharacteristic.objects.get_or_create(
                    configuration=config,
                    characteristic=char_val.characteristic,
                    defaults={'value': char_val.value}
                )

    duplicate_characteristics.short_description = "Скопировать характеристики из первой комплектации"
    actions = ['duplicate_characteristics']

    def get_main_image_preview(self, obj):
        main_img = obj.images.filter(is_main=True).first()
        if main_img:
            return format_html(
                '<img src="{}" style="max-height:40px;" />',
                main_img.image.url
            )
        return "Нет фото"

    get_main_image_preview.short_description = "Основное фото"


@admin.register(ConfigurationCharacteristic)
class ConfigurationCharacteristicAdmin(admin.ModelAdmin):
    list_display = ['configuration', 'characteristic', 'id', 'order', 'is_active']
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('configuration', 'characteristic', 'id')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )