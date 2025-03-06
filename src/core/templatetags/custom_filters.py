from django import template

register = template.Library()

@register.filter
def get_item(lst, index):
    """Returns the item at the given index of a list"""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return ''
