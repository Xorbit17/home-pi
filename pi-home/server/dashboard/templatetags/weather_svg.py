from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from pathlib import Path
from typing import cast
import re

register = template.Library()

@register.simple_tag
def weather_svg(icon_name: str, css_class: str = ""):
    """
    Inline a weather SVG from STATICFILES.
    Usage: {% weather_icon forecast.icon "wicon wicon-96 text-blue" %}
    """
    if not icon_name:
        return "<!-- weather_icon: empty icon name -->"
    rel_path = f"svg/weather-bas/{icon_name}"
    abs_path = finders.find(rel_path, all=False)
    if not abs_path:
        return f"<!-- weather svg not found: {rel_path} -->"
    data = Path(cast(str,abs_path)).read_text()
    if css_class:
        data = data.replace("<svg", f'<svg class="{css_class}"', 1)
    if 'stroke="' not in data:
        data = data.replace("<svg", '<svg stroke="currentColor"', 1)
    return mark_safe(data)
