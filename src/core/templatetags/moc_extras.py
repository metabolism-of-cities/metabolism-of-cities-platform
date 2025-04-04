from django import template
from django.template.defaulttags import register

register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        if dictionary.get(key):
            return dictionary.get(key)
        elif dictionary.get(str(key)):
            return dictionary.get(str(key))
        else:
            return ""
    except:
        return ""

@register.filter
def convert_dash(string):
    return string.replace(r'\u002D', "-")

@register.filter
def convert_quotes(string):
    return string.replace(r'"', "'")

@register.filter
def strip_first_slash(string):
    if string[0:5] == "/http":
        # We have an issue with links to subsites being prefaced with a slash,
        # and we use this hack to remove them. Not pretty but what can we do?!
        return string[1:]
    else:
        return string

@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key)

@register.filter
def split_by_comma(value):
    """Splits a string by commas."""
    if isinstance(value, str):
        return value.split(",")
    return []

@register.filter
def split_tag(value):
    value = str(value)
    return value.split('.')[0] + '.' + value.split('.')[1]


#### TEMP FOR MAP CONVERSION #####
@register.filter
def getmap(string):
    string = string._repr_html_()
    return string
