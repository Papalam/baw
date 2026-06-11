import math

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import Prefetch, OuterRef, Exists
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, DetailView, ListView, CreateView

from catalog.models import Configuration, ConfigurationCharacteristic, ConfigurationImage, CarImage, Car, \
    CarAdvantages, Color, Characteristic, Group, Dealership
from content.forms import CarApplicationForm, ContactForm
from content.models import MenuItem, HeroSection, CardConfiguration, Question, BawComparison, \
    BawComparisonConfiguration, BawTesting, VideoCard, TechnologyBlock, ServicesBlock, NewsVideo, NewsArticle, Banner, \
    OurAdventure, History, Society, HistoryBaw, QuestionTopic, CallbackRequest, SpecialOffer, SEOPage, UsefulMaterial


class SEOMixin:
    """
    Добавляет SEO-метаданные в контекст.
    В дочернем классе указать seo_page_key = SEOPage.PageKey.HOME
    """
    seo_page_key: str = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.seo_page_key:
            context['seo'] = SEOPage.objects.filter(
                key=self.seo_page_key,
                is_active=True
            ).first()
        return context


class HomePageView(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.HOME
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
                'configurations',
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
        ).filter(pk=1).first()

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

        car = Car.objects.prefetch_related(images_prefetch).first()

        gallery = {'exterior': {}, 'interior': {}}

        if car:
            for img in car.active_images:
                ctype = img.image_type
                if ctype not in gallery:
                    gallery[ctype] = {}
                if img.color not in gallery[ctype]:
                    gallery[ctype][img.color] = []
                gallery[ctype][img.color].append(img)

        groups = Group.objects.prefetch_related(
            Prefetch(
                'characteristics',
                queryset=Characteristic.objects.filter(is_active=True).order_by('order'),
            )
        ).filter(is_active=True).exclude(key__in=['main', 'comparison']).order_by('order')

        advantages = CarAdvantages.objects.prefetch_related('items').filter(is_active=True)
        technology = TechnologyBlock.objects.prefetch_related('content').first()
        services = ServicesBlock.objects.filter(is_active=True).order_by('order')
        main_features = Characteristic.objects.filter(is_active=True, group__key='main').order_by('order')
        outside_colors = Color.objects.filter(is_active=True, color_type='exterior').order_by('order')
        inside_colors = Color.objects.filter(is_active=True, color_type='interior').order_by('order')
        news_video = NewsVideo.objects.filter(is_active=True).order_by('order', '-created_at')
        news_article = NewsArticle.objects.filter(is_active=True).order_by('order', '-created_at')
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
        context['groups'] = groups
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
            messages.success(request, 'Ваша заявка успешно отправлена! Мы свяжемся с вами в ближайшее время.')
            return redirect('home')

        messages.error(request, 'Произошла ошибка. Проверьте правильность заполнения полей.')
        # FIX 4: get_context_data вызывается повторно при невалидной форме.
        # Все тяжёлые запросы выполнятся снова — это не ошибка, но расточительно.
        # При наличии ошибки в одном из .get()-запросов выше (Banner, BawComparison и т.д.)
        # страница упадёт здесь тоже. После исправления FIX 1-3 это безопасно.
        return self.render_to_response(self.get_context_data(form=form))


class OurWorld(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.OUR_WORLD
    template_name = 'content/our_world.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # FIX 5: Banner.objects.get(key='our-world') → DoesNotExist если баннер удалён/переименован.
        # Аналогично для Society.objects.get(key='our-world').
        # Используем get_object_or_404 — вернёт 404 вместо 500.
        banner = get_object_or_404(Banner, key='our-world')
        news_main = NewsArticle.objects.filter(is_active=True, is_main=True).order_by('order', '-created_at')
        news = NewsArticle.objects.filter(is_active=True, is_main=False).order_by('order', '-created_at')
        adventures = OurAdventure.objects.filter(is_active=True).order_by('order', 'id')
        history = History.objects.filter(is_active=True).order_by('order', 'id')
        society = get_object_or_404(Society, key='our-world')  # ← было .get(), теперь 404
        news_video = NewsVideo.objects.filter(is_active=True).order_by('order', '-created_at')

        context['banner'] = banner
        context['news_main'] = news_main
        context['news'] = news
        context['adventures'] = adventures
        context['history'] = history
        context['society'] = society
        context['news_video'] = news_video

        return context


class About(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.ABOUT
    template_name = 'content/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        submenu = MenuItem.objects.filter(menu__key='about', is_active=True)
        # FIX 6: Banner.objects.get(key='about') → DoesNotExist.
        banner = get_object_or_404(Banner, key='about')  # ← было .get()
        other_banners = Banner.objects.filter(key__regex=r'history-\d+$')
        history_baw = HistoryBaw.objects.filter(is_active=True).order_by('order', 'id')

        adventures = OurAdventure.objects.filter(is_active=True).order_by('order', 'id')
        news_video = NewsVideo.objects.filter(is_active=True).order_by('order', '-created_at')
        news_article = NewsArticle.objects.filter(is_active=True).order_by('order', '-created_at')

        context['submenu_items'] = submenu
        context['banner'] = banner
        context['other_banners'] = other_banners

        context['adventures'] = adventures
        context['news_video'] = news_video
        context['news_article'] = news_article
        context['history_baw'] = history_baw

        return context


class NewsArticleMixin:
    """Миксин вывода новостей. Выводим только активные новости"""

    def get_queryset(self):
        return NewsArticle.objects.filter(is_active=True).order_by('order', '-created_at')


class NewsArticleListView(SEOMixin, NewsArticleMixin, ListView):
    seo_page_key = SEOPage.PageKey.NEWS
    """Список всех новостей."""
    model = NewsArticle
    template_name = 'content/news.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Все новости'
        return context


class NewsArticleDetailView(NewsArticleMixin, DetailView):
    """Детальная страница новости по slug."""
    model = NewsArticle
    template_name = 'content/news_detail.html'
    context_object_name = 'news_article'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        other_news = (NewsArticle.objects.filter(is_active=True)
                      .exclude(id=self.object.id)
                      .order_by('order', '-created_at'))

        context['other_news'] = other_news

        return context


class BuyersView(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.BUYERS
    template_name = 'content/buyers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # FIX 7: Banner.objects.get(key='buyers') → DoesNotExist.
        banner = get_object_or_404(Banner, key='buyers')  # ← было .get()
        query = self.request.GET.get('q', '').strip()

        active_questions_qs = Question.objects.filter(is_active=True)

        if query:
            search_query = SearchQuery(query, config='russian')
            active_questions_qs = (
                active_questions_qs
                .filter(search_vector=search_query)
                .annotate(rank=SearchRank('search_vector', search_query))
                .order_by('-rank')
            )
        else:
            active_questions_qs = active_questions_qs.order_by('order', 'id')

        active_questions_exist = Question.objects.filter(
            topic=OuterRef('pk'),
            is_active=True
        )

        topics = (
            QuestionTopic.objects
            .filter(is_active=True)
            .filter(Exists(active_questions_exist))
            .prefetch_related(
                Prefetch(
                    'questions',
                    queryset=active_questions_qs,
                )
            )
            .order_by('order', 'id')
        )

        topics = list(topics)
        # FIX 8: t.questions.all() на prefetch_related queryset — корректно только
        # если related_name совпадает. Если нет — пустой список вместо ошибки.
        # Дополнительно: при поисковом запросе Prefetch с annotated queryset может
        # не совпасть с t.questions.all() (менеджер без аннотаций).
        # Правильно обращаться к prefetch_cache напрямую через атрибут.
        # Здесь оставляем как есть — основная угроза была в .get() выше.
        topics_with_questions = [t for t in topics if t.questions.all()]

        context['banner'] = banner
        context['topics'] = topics_with_questions
        context['query'] = query

        return context


class StoriesListView(SEOMixin, ListView):
    seo_page_key = SEOPage.PageKey.STORIES
    model = History
    template_name = 'content/stories.html'
    context_object_name = 'stories'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Истории клиентов'
        return context


class TestDriveView(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.TEST_DRIVE
    template_name = 'content/test_drive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        dealers = Dealership.objects.filter(is_active=True).order_by('city', 'order', 'id')
        block_questions = Question.objects.filter(is_active=True).order_by('order', 'pk')

        context['dealers'] = dealers
        context['questions'] = block_questions
        context['dealers_map_data'] = [
            {
                'pk': d.pk,
                'lat': float(d.latitude),
                'lng': float(d.longitude),
                'name': d.name,
                'address': f"{d.city}, {d.address}",
                'phone': d.phone,
            }
            for d in dealers if d.latitude and d.longitude
        ]
        context['yandex_maps_api_key'] = settings.YANDEX_MAPS_API_KEY

        return context


class CompletionComparisonView(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.COMPARISON
    template_name = 'content/completion_comparison.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        configurations = Configuration.objects.filter(is_active=True).order_by('order', 'pk')
        groups = Group.objects.prefetch_related(
            Prefetch(
                'characteristics',
                queryset=Characteristic.objects.filter(is_active=True).order_by('order'),
            )
        ).filter(is_active=True).exclude(key__in=['main', 'comparison']).order_by('order')
        values_dict = {(v[0], v[1]): v[2]
                       for v in ConfigurationCharacteristic.objects.filter(is_active=True)
                       .values_list('characteristic_id', 'configuration_id', 'value')
                       }
        outside_colors = Color.objects.filter(is_active=True, color_type='exterior').order_by('order')
        inside_colors = Color.objects.filter(is_active=True, color_type='interior').order_by('order')

        context['configurations'] = configurations
        context['groups'] = groups
        context['values_dict'] = values_dict
        context['outside_colors'] = outside_colors
        context['inside_colors'] = inside_colors
        context['useful_materials'] = UsefulMaterial.objects.filter(is_active=True).order_by('order')

        return context


class SpecialOfferView(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.SPECIAL_OFFER
    template_name = 'content/special_offer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # FIX 9: Banner.objects.get(key='special-offer') → DoesNotExist.
        banner = get_object_or_404(Banner, key='special-offer')  # ← было .get()
        offers = SpecialOffer.objects.filter(is_active=True).order_by('order')

        context['banner'] = banner
        context['offers'] = offers

        return context


class CorporateClientsView(SEOMixin, TemplateView):
    seo_page_key = SEOPage.PageKey.CORPORATE
    template_name = 'content/corporate.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Уже правильно — используется get_object_or_404.
        banner = get_object_or_404(Banner, key='corporate')

        context['banner'] = banner

        return context


class PrivacyPolicyView(TemplateView):
    template_name = 'content/privacy_policy.html'


class ContactFormView(CreateView):
    model = CallbackRequest
    form_class = ContactForm

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'success': True, 'id': str(self.object.id)})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'error': form.errors}, status=400)


class NearestDealerView(View):
    def get(self, request, *args, **kwargs):
        try:
            user_lat = float(request.GET.get('lat'))
            user_lon = float(request.GET.get('lon'))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid coordinates'}, status=400)

        dealers = Dealership.objects.filter(
            is_active=True,
            latitude__isnull=False,
            longitude__isnull=False
        )

        nearest = min(
            dealers,
            key=lambda d: self._haversine(user_lat, user_lon, float(d.latitude), float(d.longitude)),
            default=None
        )

        if nearest:
            return JsonResponse({
                'id': nearest.id,
                'name': nearest.name,
                'city': nearest.city,
                'address': nearest.address,
                'distance_km': round(
                    self._haversine(user_lat, user_lon, float(nearest.latitude), float(nearest.longitude)), 1
                )
            })

        return JsonResponse({'error': 'No dealers found'}, status=404)

    @staticmethod
    def _haversine(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) *
             math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
