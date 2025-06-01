from django import template
register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(str(key))

@register.filter
def as_form_field(form, field_name):
    if form and hasattr(form, field_name):
        return getattr(form, field_name)
    return ''
