from django.contrib import admin
from django.db import models
from django.utils.html import format_html

from .models import Menu, MenuItem, HeroSection, HTMLContent, CardConfiguration, CardConfigurationFeature, \
    CardConfigurationImage, Question, BawComparison, BawComparisonConfiguration, BawTesting, BawTestingImage, \
    BawTestingFeature, BawTestingItems, VideoCardContent, VideoCard, TechnologyBlockContent, TechnologyBlock, \
    ServicesBlock, NewsArticle, NewsVideo, OurAdventure, History, Society, Banner, HistoryBaw, SocialNetwork, \
    CompanyInfo, QuestionTopic, CallbackRequest, TestDriveRequest, SpecialOffer
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


class BawTestingFeatureInline(admin.TabularInline):
    model = BawTestingFeature
    extra = 0
    fields = ('title', 'icon', 'value', 'unit', 'preview')
    readonly_fields = ('id', 'preview')

    def preview(self, obj):
        if obj.pk and obj.icon:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.icon.url
            )
        return "Иконка"

    preview.short_description = "Превью"


class BawTestingImageInline(admin.TabularInline):
    model = BawTestingImage
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


class BawTestingItemsInline(admin.TabularInline):
    model = BawTestingItems
    extra = 1
    fields = ('title', 'description', 'value')


class BawComparisonConfigurationInline(admin.TabularInline):
    model = BawComparisonConfiguration
    extra = 1
    fields = ('configuration', 'order', 'is_active')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'is_active']
    readonly_fields = ['id']
    search_fields = ['title']
    ordering = ['order', 'id']
    inlines = [MenuItemInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'key')
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


@admin.register(QuestionTopic)
class QuestionTopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'id', 'order', 'is_active']
    list_display_links = ['name', 'id']
    readonly_fields = ['id']
    search_fields = ['name']
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('name',)
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['topic', 'question', 'id', 'order', 'is_active']
    list_display_links = ['question', 'id', 'order', 'is_active']
    readonly_fields = ['id']
    search_fields = ['question']
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('topic', 'question', 'answer')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(BawComparison)
class BawComparisonAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'order', 'is_active']
    list_display_links = ['title', 'id']
    readonly_fields = ('id', 'preview')
    inlines = (BawComparisonConfigurationInline,)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'title_form', 'sub_title_form', 'text_form', 'image', 'preview', 'alt')
        }),
        ('Кнопки', {
            'fields': ('text_red_button', 'url_red_button', 'text_black_button', 'url_black_button')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return "Фото"

    preview.short_description = "Превью"


@admin.register(BawTesting)
class BawTestingAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'order', 'is_active']
    list_display_links = ['title', 'id']
    readonly_fields = ['id']
    ordering = ['order', 'id']
    inlines = (BawTestingFeatureInline, BawTestingImageInline, BawTestingItemsInline)
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'description', 'video', 'subtitle', 'title_full_control', 'image', 'alt')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


class VideoCardContentInline(admin.TabularInline):
    model = VideoCardContent
    extra = 1
    fields = ['image', 'preview', 'alt', 'video']
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return "Фото"


@admin.register(VideoCard)
class VideoCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'order', 'is_active']
    readonly_fields = ('id',)
    inlines = [VideoCardContentInline]
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


class TechnologyBlockContentInline(admin.TabularInline):
    model = TechnologyBlockContent
    extra = 1
    fields = ['title', 'description', 'image', 'preview', 'alt']
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return "Фото"


@admin.register(TechnologyBlock)
class TechnologyBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'order', 'is_active']
    readonly_fields = ('id',)
    inlines = [TechnologyBlockContentInline]
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'description')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )


@admin.register(ServicesBlock)
class ServicesBlockAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'order', 'is_active']
    readonly_fields = ('id', 'preview')
    ordering = ['order', 'id']
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'description', 'icon', 'preview', 'slug')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Иконка'


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'created_at', 'order', 'is_active']
    list_display_links = ['title', 'id']
    readonly_fields = ('id', 'preview', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'description', 'image', 'preview', 'slug', 'is_main', 'created_at')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    formfield_overrides = {
        models.TextField: {'widget': RichTextEditorWidget}
    }

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Изображение'


@admin.register(NewsVideo)
class NewsVideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'created_at', 'order', 'is_active']
    list_display_links = ['title', 'id']
    readonly_fields = ('id', 'preview')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'description', 'video', 'image', 'preview', 'slug')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Изображение'


@admin.register(OurAdventure)
class OurAdventureAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'name', 'order', 'is_active']
    list_display_links = ['title', 'id']
    readonly_fields = ('id', 'preview')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'name', 'description', 'image', 'preview', 'video', 'slug')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Обложка'


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'city', 'order', 'is_active']
    list_display_links = ['title', 'id']
    readonly_fields = ('id', 'preview')
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'city', 'description', 'image', 'preview')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Изображение'


@admin.register(Society)
class SocietyAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'key', 'order', 'is_active']
    list_display_links = ['title', 'id', 'key']
    readonly_fields = ('id', 'preview')
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'key', 'description', 'button_title',
                       'button_text', 'button_url', 'image', 'preview', 'webp_image_mobile')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Изображение'


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'key', 'order', 'is_active']
    list_display_links = ['title', 'id', 'key']
    readonly_fields = ('id', 'preview')
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'key', 'description', 'image', 'preview')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Изображение'


@admin.register(HistoryBaw)
class HistoryBawAdmin(admin.ModelAdmin):
    list_display = ['year', 'id', 'period', 'order', 'is_active']
    list_display_links = ['year', 'id', 'period']
    readonly_fields = ('id', 'preview')
    ordering = ['order', 'id']
    fieldsets = (
        ('Основная информация', {
            'fields': ('year', 'id', 'period', 'description', 'image', 'preview')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.image.url
            )
        return 'Изображение'


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('platform', 'id', 'url', 'is_active', 'order')
    readonly_fields = ('id', 'preview')
    ordering = ('order', 'id')
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'platform', 'url', 'icon', 'preview')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        }),
    )

    def preview(self, obj):
        if obj.pk and obj.icon:
            return format_html(
                '<img src="{}" style="max-height:60px; max-width:80px;" />',
                obj.icon.url
            )
        return 'Изображение'


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'value', 'is_display_in_company_details']
    list_filter = ['is_display_in_company_details']
    search_fields = ['name', 'key', 'value']
    readonly_fields = ('id',)
    fieldsets = (
        ('Идентификация', {
            'fields': ('id', 'key', 'name')
        }),
        ('Содержимое', {
            'fields': ('value', 'desc')
        }),
        ('Отображение', {
            'fields': ('is_display_in_company_details', 'microdata')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(CallbackRequest)
class CallbackRequestAdmin(admin.ModelAdmin):
    # Поля, которые отображаются в списке
    list_display = ['name', 'phone', 'is_sent_to_crm', 'created_at']

    # Фильтрация в боковой панели
    list_filter = ['is_sent_to_crm', 'created_at']

    # Поиск по основным данным клиента
    search_fields = ['name', 'phone', 'comment']

    # Поля только для чтения (дату создания нельзя менять вручную)
    readonly_fields = ('id', 'created_at')

    fieldsets = (
        ('Данные клиента', {
            'fields': ('id', 'name', 'phone')
        }),
        ('Содержимое запроса', {
            'fields': ('comment',)
        }),
        ('Статус и системная информация', {
            'fields': ('is_sent_to_crm', 'created_at')
        }),
    )


@admin.register(TestDriveRequest)
class TestDriveRequestAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'phone', 'desired_date', 'desired_time', 'is_sent_to_crm', 'created_at']
    list_filter = ['is_sent_to_crm', 'created_at', 'desired_date']
    search_fields = ['first_name', 'last_name', 'phone', 'comment']
    readonly_fields = ('id', 'created_at')
    fieldsets = (
        ('Данные клиента', {
            'fields': ('id', 'first_name', 'last_name', 'phone')
        }),
        ('Детали заявки', {
            'fields': ('desired_date', 'desired_time', 'comment', 'consent')
        }),
        ('Статус и системная информация', {
            'fields': ('is_sent_to_crm', 'created_at')
        }),
    )


@admin.register(SpecialOffer)
class SpecialOfferAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'valid_from', 'valid_until', 'order', 'is_active']
    list_display_links = ['title', 'id']
    readonly_fields = ('id', 'preview', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ['order', '-created_at']
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'id', 'description', 'image', 'preview', 'webp_image', 'alt', 'slug', 'created_at')
        }),
        ('Срок действия', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Активность и сортировка', {
            'fields': ('order', 'is_active')
        })
    )

    def preview(self, obj):
        if obj.pk and obj.image:
            return format_html('<img src="{}" style="max-height:60px; max-width:80px;" />', obj.image.url)
        return 'Изображение'

    preview.short_description = 'Превью'


admin.site.site_header = "Администрирование сайта Baw"
