from django import template
from django.template.defaulttags import register

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary.get(key):
        return dictionary.get(key)
    elif dictionary.get(str(key)):
        return dictionary.get(str(key))
    else:
        return ""

@register.filter
def convert_dash(string):
    return string.replace(r'\u002D', "-")

@register.filter
def convert_quotes(string):
    return string.replace(r'"', "'")

@register.filter
def strip_first_slash(string):
    first_chars = string[0:4]
    if first_chars == "/http":
        # We have an issue with links to subsites being prefaced with a slash, 
        # and we use this hack to remove them. Not pretty but what can we do?!
        return string[1:]
    else:
        return string
