from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    """Returns the item at the given index of a list"""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return ''
    
@register.filter
def isdigit(value):
    return value.isdigit() if isinstance(value, str) else False

@register.filter
def to_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None  # Return None if conversion fails
    
@register.filter
def typeof(value):
    return str(type(value))