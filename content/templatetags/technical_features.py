from django import template

register = template.Library()


@register.simple_tag
def feature_value(values_dict, feature_id, configuration_id):
    return values_dict.get((feature_id, configuration_id), '-')


@register.inclusion_tag('content/blocks/breadcrumbs.html')
def breadcrumbs(*crumbs):
    """
    Использование:
      {% breadcrumbs "Главная" "home" "Новости" "" %}

    Принимает пары: (title, url_name). Если url_name пустой — элемент неактивный (текущая страница).
    Пример:
      {% breadcrumbs "Главная" "home" "Каталог" "catalog:list" "Товар" "" %}
    """
    items = []
    it = iter(crumbs)
    for title in it:
        url_name = next(it, '')
        items.append({'title': title, 'url_name': url_name})
    return {'crumbs': items}