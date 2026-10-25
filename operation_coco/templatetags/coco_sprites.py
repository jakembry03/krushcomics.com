import re

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

register = template.Library()

# Characters and their poses, one SVG per pose in img/<character>/.
POSES = {
    "agent": ("idle", "talk", "point", "happy", "worried", "cast"),
}


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
    with open(path, encoding="utf-8") as svg_file:
        svg = svg_file.read()

    # Every pose is on the page at once, so keep ids (and references to
    # them, like filter="url(#glow)") unique per character and pose.
    prefix = f"{character}-{pose}-"
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r'\bid="([^"]+)"', rf'id="{prefix}\1"', svg)
    svg = re.sub(r"url\(#([^)]+)\)", rf"url(#{prefix}\1)", svg)
    svg = re.sub(r'href="#([^"]+)"', rf'href="#{prefix}\1"', svg)
    svg = svg.replace(
        "<svg ",
        f'<svg class="sprite__pose sprite__pose--{pose}" aria-hidden="true" focusable="false" ',
        1,
    )
    return mark_safe(svg)
