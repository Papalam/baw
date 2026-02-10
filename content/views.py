from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from catalog.models import Configuration
from content.models import MenuItem, HeroSection, CardConfiguration, HTMLContent, Question


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
        block_baw_choices_title = HTMLContent.objects.get(key='block_baw_choices_title')
        configurations = Configuration.objects.filter(is_active=True, car__pk=1).prefetch_related(
            'characteristics').order_by('order')

        block_questions = Question.objects.filter(is_active=True)

        context['submenu_items'] = submenu
        context['hero_sections'] = hero_sections
        context['card_configuration'] = card_configuration
        context['block_baw_choices_title'] = block_baw_choices_title
        context['configurations'] = configurations
        context['questions'] = block_questions

        return context
