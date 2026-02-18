from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Prefetch
from django.views.generic import TemplateView

from catalog.models import Configuration, ConfigurationCharacteristic, ConfigurationImage
from content.models import MenuItem, HeroSection, CardConfiguration, Question, BawComparison, \
    BawComparisonConfiguration, BawTesting, VideoCard, TechnologyBlock, ServicesBlock, NewsVideo, NewsArticle


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

        advantages = BawTesting.objects.prefetch_related('features', 'images', 'items').first()
        video_card = VideoCard.objects.prefetch_related('content').first()
        technology = TechnologyBlock.objects.prefetch_related('content').first()
        services = ServicesBlock.objects.filter(is_active=True).order_by('order')
        news_video = NewsVideo.objects.filter(is_active=True).order_by('order', 'created_at')
        news_article = NewsArticle.objects.filter(is_active=True).order_by('order', 'created_at')
        block_questions = Question.objects.filter(is_active=True)

        context['submenu_items'] = submenu
        context['hero_sections'] = hero_sections
        context['card_configuration'] = card_configuration
        context['block_baw_comparison'] = block_baw_comparison
        context['advantages'] = advantages
        context['video_card'] = video_card
        context['technology'] = technology
        context['services'] = services
        context['news_video'] = news_video
        context['news_article'] = news_article
        context['questions'] = block_questions

        return context
