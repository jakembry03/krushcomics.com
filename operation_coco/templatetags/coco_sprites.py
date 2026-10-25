import re

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

register = template.Library()

# Characters and their poses, one SVG per pose in img/<character>/.
POSES = {
    "agent": ("idle", "talk", "point", "happy", "worried", "cast"),
    "villain": ("idle", "cackle", "point", "smug", "angry"),
}


def _inline_svg(path, prefix, svg_class):
    with open(path, encoding="utf-8") as svg_file:
        svg = svg_file.read()
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    # Several SVGs share a page, so keep ids (and references to them,
    # like filter="url(#glow)") unique.
    svg = re.sub(r'\bid="([^"]+)"', rf'id="{prefix}\1"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}\1)", svg)
    svg = re.sub(r'href="#([^"]+)"', rf'href="#{prefix}\1"', svg)
    svg = svg.replace(
        "<svg ",
        f'<svg class="{svg_class}" aria-hidden="true" focusable="false" ',
        1,
    )
    return mark_safe(svg)


@register.simple_tag
def app_icon(icon):
    """
    Inline a desktop app icon from static/operation_coco/img/apps/.
    """
    if not re.fullmatch(r"[a-z0-9-]+", icon or ""):
        raise template.TemplateSyntaxError(f"Bad icon name: {icon!r}")
    path = finders.find(f"operation_coco/img/apps/{icon}.svg")
    if path is None:
        return ""
    return _inline_svg(path, f"app-{icon}-", "app__glyph")


@register.simple_tag
def sprite_pose(character, pose):
    """
    Inline one pose SVG from static/operation_coco/img/<character>/.

    The SVG is inlined rather than linked so coco.css can color it and
    animate its named groups (#hood, #mask, #eyes, ...). Pages still
    refer to poses only by file name, so the art can be swapped freely.
    """
    if pose not in POSES.get(character, ()):
        raise template.TemplateSyntaxError(f"Unknown pose: {character!r} {pose!r}")

    path = finders.find(f"operation_coco/img/{character}/{pose}.svg")
    if path is None:
        return ""
    return _inline_svg(path, f"{character}-{pose}-", f"sprite__pose sprite__pose--{pose}")


@register.simple_tag
def villain_car():
    """
    Inline the villain's flying car (img/villain/car.svg).
    """
    path = finders.find("operation_coco/img/villain/car.svg")
    if path is None:
        return ""
    return _inline_svg(path, "villain-car-", "villain-car__svg")
