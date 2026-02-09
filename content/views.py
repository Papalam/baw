from django.views.generic import TemplateView

from content.models import MenuItem, HeroSection, HTMLContent


class HomePageView(TemplateView):
    template_name = 'content/home_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        submenu = MenuItem.objects.filter(menu__pk=2, is_active=True)
        hero_sections = HeroSection.objects.all()
        hero_bottom_text = HTMLContent.objects.filter(key='hero_section_page_baw_main-bottom').first()

        context['submenu_items'] = submenu
        context['hero_sections'] = hero_sections

        return context
