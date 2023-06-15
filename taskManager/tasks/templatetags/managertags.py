from django import template

register = template.Library()

#Разрешает доступ к многоуровневым словарям в html-шаблонах (dict.task.id)
@register.simple_tag
def dict_get(dct, key):
    return dct.get(key)