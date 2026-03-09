from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, DetailView

from catalog.models import Configuration, ConfigurationCharacteristic, ConfigurationImage, CarImage, Car, \
    CarAdvantages, Color, Characteristic
from content.forms import CarApplicationForm
from content.models import MenuItem, HeroSection, CardConfiguration, Question, BawComparison, \
    BawComparisonConfiguration, BawTesting, VideoCard, TechnologyBlock, ServicesBlock, NewsVideo, NewsArticle, Banner, \
    OurAdventure, History, Society, HistoryBaw


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = 'content/home_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        submenu = MenuItem.objects.filter(menu__pk=2, is_active=True)
        hero_sections = HeroSection.objects.all()
        card_configuration = (CardConfiguration.objects
                              .filter(is_active=True)
                              .select_related('configuration')
                              .prefetch_related('features', 'images')
                              .order_by('order')
                              )
        block_baw_comparison = BawComparison.objects.prefetch_related(
            Prefetch(
                'configurations',  # BawComparisonConfiguration
                queryset=BawComparisonConfiguration.objects.prefetch_related(
                    Prefetch(
                        'configuration__characteristics',
                        queryset=ConfigurationCharacteristic.objects.filter(
                            is_active=True
                        ).select_related('characteristic').filter(
                            characteristic__group__key='comparison'
                        ).order_by(
                            'characteristic__order', 'order'
                        ),
                        to_attr='active_characteristics'
                    ),
                    Prefetch(
                        'configuration__images',
                        queryset=ConfigurationImage.objects.filter(
                            is_active=True,
                            is_main=True
                        ).order_by('order'),
                        to_attr='main_images'
                    )
                ).filter(form_id=1),
                to_attr='comparison_configs'
            )
        ).get(pk=1)

        features = BawTesting.objects.prefetch_related('features', 'images', 'items').first()
        video_card = VideoCard.objects.prefetch_related('content').first()

        # Галерея
        images_prefetch = Prefetch(
            'images',
            queryset=CarImage.objects.filter(is_active=True)
            .select_related('color')
            .order_by('color__order', 'color__id', 'order'),
            to_attr='active_images'
        )

        car = get_object_or_404(Car.objects.prefetch_related(images_prefetch))

        gallery = {'exterior': {}, 'interior': {}}

        for img in car.active_images:
            ctype = img.image_type
            if img.color not in gallery[ctype]:
                gallery[ctype][img.color] = []
            gallery[ctype][img.color].append(img)

        advantages = CarAdvantages.objects.prefetch_related('items').filter(is_active=True)
        technology = TechnologyBlock.objects.prefetch_related('content').first()
        services = ServicesBlock.objects.filter(is_active=True).order_by('order')
        main_features = Characteristic.objects.filter(is_active=True, group__key='main').order_by('order')
        outside_colors = Color.objects.filter(is_active=True, color_type='exterior').order_by('order')
        inside_colors = Color.objects.filter(is_active=True, color_type='interior').order_by('order')
        news_video = NewsVideo.objects.filter(is_active=True).order_by('order', 'created_at')
        news_article = NewsArticle.objects.filter(is_active=True).order_by('order', 'created_at')
        block_questions = Question.objects.filter(is_active=True).order_by('order', 'pk')

        configurations = Configuration.objects.filter(is_active=True).order_by('order', 'pk')

        values_dict = {(v[0], v[1]): v[2]
                       for v in ConfigurationCharacteristic.objects.filter(is_active=True)
                       .values_list('characteristic_id', 'configuration_id', 'value')
                       }

        context['submenu_items'] = submenu
        context['hero_sections'] = hero_sections
        context['card_configuration'] = card_configuration
        context['block_baw_comparison'] = block_baw_comparison
        context['features'] = features
        context['video_card'] = video_card
        context['gallery'] = gallery
        context['advantages'] = advantages
        context['technology'] = technology
        context['services'] = services
        context['configurations'] = configurations
        context['main_features'] = main_features
        context['values_dict'] = values_dict
        context['outside_colors'] = outside_colors
        context['inside_colors'] = inside_colors
        context['news_video'] = news_video
        context['news_article'] = news_article
        context['questions'] = block_questions

        return context

    def post(self, request, *args, **kwargs):
        """Обработка отправки формы"""
        form = CarApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            # Добавляем сообщение об успехе
            messages.success(request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
            # Редирект после успешной отправки (Post/Redirect/Get pattern)
            return redirect('home')  # или имя вашей success-страницы

        # Если форма невалидна, возвращаем страницу с формой и ошибками
        messages.error(request, 'Произошла ошибка. Проверьте правильность заполнения полей.')
        return self.render_to_response(self.get_context_data(form=form))


class OurWorld(TemplateView):
    template_name = 'content/our_world.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        banner = Banner.objects.get(key='our-world')
        news_main = NewsArticle.objects.filter(is_active=True, is_main=True).order_by('order', 'created_at')
        news = NewsArticle.objects.filter(is_active=True, is_main=False).order_by('order', 'created_at')
        adventures = OurAdventure.objects.filter(is_active=True).order_by('order', 'id')
        history = History.objects.filter(is_active=True).order_by('order', 'id')
        society = Society.objects.get(key='our-world')
        news_video = NewsVideo.objects.filter(is_active=True).order_by('order', 'created_at')

        context['banner'] = banner
        context['news_main'] = news_main
        context['news'] = news
        context['adventures'] = adventures
        context['history'] = history
        context['society'] = society
        context['news_video'] = news_video

        return context


class About(TemplateView):
    template_name = 'content/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        submenu = MenuItem.objects.filter(menu__key='about', is_active=True)
        banner = Banner.objects.get(key='about')
        other_banners = Banner.objects.filter(key__regex=r'history-\d+$')
        history_baw = HistoryBaw.objects.filter(is_active=True).order_by('order', 'id')

        adventures = OurAdventure.objects.filter(is_active=True).order_by('order', 'id')
        news_video = NewsVideo.objects.filter(is_active=True).order_by('order', 'created_at')
        news_article = NewsArticle.objects.filter(is_active=True).order_by('order', 'created_at')

        context['submenu_items'] = submenu
        context['banner'] = banner
        context['other_banners'] = other_banners

        context['adventures'] = adventures
        context['news_video'] = news_video
        context['news_article'] = news_article
        context['history_baw'] = history_baw

        return context


class NewsDetail(DetailView):
    model = NewsArticle
    template_name = 'content/news_detail.html'
    context_object_name = 'news_article'
    slug_field = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        submenu = MenuItem.objects.filter(menu__key='baw_212', is_active=True)
        other_news = (NewsArticle.objects.filter(is_active=True)
                      .exclude(id=self.object.id)
                      .order_by('order', 'id'))

        context['submenu'] = submenu
        context['other_news'] = other_news

        return context
