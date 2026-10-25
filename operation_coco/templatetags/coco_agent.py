import re

from django import template
from django.contrib.staticfiles import finders
from django.utils.safestring import mark_safe

register = template.Library()

POSES = ("idle", "talk", "point", "happy", "worried")


@register.simple_tag
def agent_pose(pose):
    """
    Inline one agent pose SVG from static/operation_coco/img/agent/.

    The SVG is inlined rather than linked so coco.css can color it and
    animate its named groups (#head, #eyes, #mouth, #cape). Pages still
    refer to poses only by file name, so the art can be swapped freely.
    """
    if pose not in POSES:
        raise template.TemplateSyntaxError(f"Unknown agent pose: {pose!r}")

    path = finders.find(f"operation_coco/img/agent/{pose}.svg")
    if path is None:
        return ""
    with open(path, encoding="utf-8") as svg_file:
        svg = svg_file.read()

    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    # Every pose is on the page at once, so keep the group ids unique.
    svg = re.sub(r'\bid="([^"]+)"', rf'id="agent-{pose}-\1"', svg)
    svg = svg.replace(
        "<svg ",
        f'<svg class="agent__pose agent__pose--{pose}" aria-hidden="true" focusable="false" ',
        1,
    )
    return mark_safe(svg)
