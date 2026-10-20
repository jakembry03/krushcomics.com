import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Link and image addresses must start with one of these. Anything else
# (javascript:, data:, ...) has its href/src removed.
SAFE_URL_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "/",
    "#",
)


class DropUnsafeUrls(Treeprocessor):

    def run(self, root):
        for element in root.iter():
            for attribute in ("href", "src"):
                url = element.get(attribute)

                if url is None:
                    continue

                if not url.strip().lower().startswith(SAFE_URL_PREFIXES):
                    del element.attrib[attribute]


class SafeMarkdown(Extension):
    """
    Escape raw HTML instead of passing it through, and drop unsafe
    link/image addresses, so Markdown is the only formatting allowed.
    """

    def extendMarkdown(self, md):
        md.preprocessors.deregister("html_block")
        md.inlinePatterns.deregister("html")
        md.treeprocessors.register(DropUnsafeUrls(md), "drop_unsafe_urls", 0)


@register.filter
def render_markdown(text):
    """Convert a write-up's Markdown text into HTML."""

    html = markdown.markdown(
        text,
        extensions=[
            SafeMarkdown(),
            "fenced_code",
            "tables",
            "sane_lists",
        ],
    )

    return mark_safe(html)
