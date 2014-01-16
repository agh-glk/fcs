from django import template

register = template.Library()


@register.filter(name='is_class')
def is_class(field, classname):
    return field.field.widget.__class__.__name__ == classname


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