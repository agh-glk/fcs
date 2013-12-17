from django import template
from django.forms import CheckboxSelectMultiple

register = template.Library()


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return field.field.widget.__class__.__name__ == CheckboxSelectMultiple().__class__.__name__


@register.filter(name='alert_tag')
def alert_tag(message_tags):
    tag_map = {'debug': '',
               'info': 'alert-info',
               'success': 'alert-success',
               'warning': 'alert-warning',
               'error': 'alert-danger'}
    try:
        return tag_map[message_tags]
    except KeyError:
        return 'alert-info'