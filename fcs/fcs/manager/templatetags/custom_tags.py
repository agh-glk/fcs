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


@register.filter
def is_true(arg):
    return arg is True


@register.filter
def pages(current, total_pages):
    r = 2
    return range(max(1, current - r), min(total_pages, current + r) + 1)