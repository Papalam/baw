from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect
from django.forms import TextInput
from django.utils.html import format_html

from catalog.models import Car, Group, Characteristic, Configuration, ConfigurationCharacteristic, ConfigurationImage, \
    Color, CarImage, CarAdvantages, CarAdvantagesItem


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


class CarAdvantagesItemInline(admin.TabularInline):
    model = CarAdvantagesItem
    extra = 1
    fields = ['title', 'description', 'order', 'is_active']


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
    list_display = ['name', 'id', 'is_visible', 'key', 'order', 'is_active']
    list_display_links = ['name', 'id', 'key']
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'id', 'is_visible', 'key')
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
    list_filter = ('group',)
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
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'id')
    inlines = [ConfigurationCharacteristicInline, ConfigurationImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('car', 'name', 'price', 'get_main_image_preview', 'id', 'slug')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )
    actions = ['duplicate_characteristics']

    @admin.action(description='Скопировать характеристики из первой комплектации')
    def duplicate_characteristics(self, request, queryset):
        """Копирует характеристики из первой комплектации"""
        try:
            # Получаем источник - Configuration с pk=1
            source_config = Configuration.objects.get(pk=1)
        except Configuration.DoesNotExist:
            self.message_user(
                request,
                'Комплектация с id=1 не найдена!',
                level='error'
            )
            return

            # Получаем все характеристики источника
        source_characteristics = list(source_config.characteristics.select_related('characteristic'))

        if not source_characteristics:
            self.message_user(
                request,
                f'У комплектации "{source_config}" нет характеристик для копирования!',
                level='warning'
            )
            return

        updated_count = 0

        # Копируем в каждую выбранную комплектацию
        for config in queryset:
            if config.pk == 1:
                continue  # Пропускаем саму исходную

            # Удаляем существующие характеристики
            config.characteristics.all().delete()

            # Создаем копии
            for source_cc in source_characteristics:
                ConfigurationCharacteristic.objects.create(
                    configuration=config,
                    characteristic=source_cc.characteristic,
                    value=source_cc.value
                )
            updated_count += 1

        msg = f'Характеристики из комплектации "{source_config}" (#{source_config.pk}) скопированы в {updated_count} комплектаций.'
        self.message_user(request, msg, level='success')

    def get_main_image_preview(self, obj):
        main_img = obj.images.filter(is_main=True).first()
        if main_img:
            return format_html(
                '<img src="{}" style="max-height:40px;" />',
                main_img.image.url
            )
        return "Нет фото"

    get_main_image_preview.short_description = "Основное фото"


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'color_type', 'order', 'is_active']
    list_display_links = ['name']
    list_filter = ('color_type',)
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'id', 'color_type', 'hex_code')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Изменяем поле hex_code на html5 color"""
        if db_field.name == 'hex_code':
            kwargs['widget'] = TextInput(attrs={'type': 'color'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ['car', 'image_type', 'color', 'id', 'order', 'is_active']
    list_display_links = ['car', 'image_type', 'color']
    list_filter = ('image_type',)
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('car', 'id', 'image_type', 'color', 'image')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(CarAdvantages)
class CarAdvantagesAdmin(admin.ModelAdmin):
    list_display = ['car', 'title', 'order', 'is_active']
    list_display_links = ['car', 'title']
    list_filter = ('car',)
    readonly_fields = ('id',)
    ordering = ('order', 'id')
    inlines = [CarAdvantagesItemInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('car', 'id', 'title', 'description', 'image')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )
