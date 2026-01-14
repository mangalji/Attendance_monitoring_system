from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr_name):
    """
    Returns the value of an attribute of an object.
    Usage: {{ object|get_attr:"attribute_name" }}
    """
    return getattr(obj, attr_name, None)
