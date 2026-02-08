import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="render_markdown")
def render_markdown(value):
    """Convert markdown text to safe HTML."""
    if not value:
        return ""
    html = md.markdown(str(value), extensions=["fenced_code", "tables", "nl2br"])
    return mark_safe(html)
