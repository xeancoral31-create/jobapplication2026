"""Template helpers for rendering notification rows."""
import json

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

_SVG = (
    '<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{}</svg>'
)

_ICONS = {
    "job": '<path d="m12 15 2 2 4-4"/><rect width="18" height="18" x="3" y="3" rx="2"/>',
    "listing": '<rect width="20" height="14" x="2" y="7" rx="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "platform": (
        '<path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21'
        'l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/>'
    ),
    "application": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/>',
}

_COLORS = {
    "job": ("rgba(56, 189, 248, 0.12)", "#38bdf8"),
    "listing": ("rgba(99, 102, 241, 0.12)", "#818cf8"),
    "platform": ("rgba(16, 185, 129, 0.12)", "#10b981"),
    "application": ("rgba(245, 158, 11, 0.12)", "#f59e0b"),
}


@register.simple_tag
def notification_icon(kind):
    return mark_safe(_SVG.format(_ICONS.get(kind, _ICONS["platform"])))


@register.simple_tag
def notification_color(kind, part):
    bg, fg = _COLORS.get(kind, _COLORS["platform"])
    return bg if part == "bg" else fg


@register.filter
def notification_json(value):
    # Autoescaping in the attribute context handles quotes safely.
    return json.dumps(value or [])
