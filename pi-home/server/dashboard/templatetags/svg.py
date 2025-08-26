from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe
from pathlib import Path
from typing import cast

register = template.Library()

@register.simple_tag
def svg(path, css_class=""):
    """
    Inline an SVG from STATICFILES (e.g. 'icons/tabler/sun.svg').
    Ensures stroke/fill use currentColor so CSS can control color.
    Usage: {% svg 'icons/tabler/sun.svg' 'icon text-blue' %}
    """
    abs_path: str | None = cast(str | None,finders.find(path, False))
    if not abs_path:
        return f"<!-- svg not found: {path} -->"
    data = Path(abs_path).read_text()
    # Inject class
    if css_class:
        data = data.replace("<svg", f'<svg class="{css_class}"', 1)

    return mark_safe(data)
