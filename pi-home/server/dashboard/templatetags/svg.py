from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from pathlib import Path
from typing import cast, Dict, Literal

register = template.Library()

csv_cache = dict()

def get_cached(path):
    result = csv_cache.get(path, None)
    if result:
        return result
    abs_path: str | None = cast(str | None, finders.find("svg/tabler/" + path, False))

    if not abs_path:
        return f"<!-- svg not found: {path} -->"
    data = Path(abs_path).read_text()
    csv_cache[path] = data
    return data

@register.simple_tag
def svg(path, css_class:str=""):
    """
    Inline an SVG from STATICFILES (e.g. 'icons/tabler/sun.svg').
    Ensures stroke/fill use currentColor so CSS can control color.
    Usage: {% svg 'icons/tabler/sun.svg' 'icon text-blue' %}
    """
    data = get_cached(path)
    if css_class:
        data = data.replace("<svg", f'<svg class="{css_class}"', 1)

    return mark_safe(data)
