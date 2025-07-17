from django import template
register = template.Library()

@register.filter
def pluck(lista, key):
    return [item[key] for item in lista]