from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter and return a list"""
    return [x.strip() for x in value.split(delimiter)]

@register.filter
def strip(value):
    """Strip whitespace from a string"""
    return value.strip() 