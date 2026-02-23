from django import template

register = template.Library()


@register.simple_tag
def feature_value(values_dict, feature_id, configuration_id):
    return values_dict.get((feature_id, configuration_id), '-')
