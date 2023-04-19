from django import template

register = template.Library()

@register.filter
def abs(value):
    return abs(value)
