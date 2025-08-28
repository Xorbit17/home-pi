from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from pathlib import Path
from typing import cast
import re

register = template.Library()

@register.simple_tag
def weather_svg(icon_name: str):
    """
    Inline a weather SVG from STATICFILES.
    Usage: {% weather_icon forecast.icon "wicon wicon-96 text-blue" %}
    """
    if not icon_name:
        return "<!-- weather_icon: empty icon name -->"
    rel_path = f"static/svg/weather-bas/{icon_name}"
    data = f'<img src="{rel_path}" alt="{icon_name}" width="128" height="128">'
    return mark_safe(data)
