from django import template
from django.template.defaulttags import register

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary.get(key):
        return dictionary.get(key)
    else:
        return ""
