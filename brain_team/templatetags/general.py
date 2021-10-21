from django import template

from brain_team import events
from brain_team import settings

register = template.Library()


@register.simple_tag
def events_clear(request):
    events.clear(request)
    return ""


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def is_item(dictionary, key):
    return key in dictionary.keys()


@register.simple_tag
def media(url):
    if settings.DEBUG:
        return "/static/" + url
    return "/media/" + url
