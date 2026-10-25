"""
Dialogue scripts, one per scene.

Every line here is a placeholder. Jake writes the real dialogue himself,
and real content never gets committed: it will arrive later through the
admin or a private, git-ignored fixture.

A script has a speaker and a list of lines. Each line has a sprite pose
and its text; the last line may carry a button whose url_name is
resolved with prepare() before it reaches the page.
"""
from copy import deepcopy

from django.urls import reverse

PHASE1_INTRO = {
    "speaker": "[Agent codename]",
    "lines": [
        {"pose": "worried", "text": "[PLACEHOLDER: agent stops her and explains the password won't work]"},
        {"pose": "idle",    "text": "[PLACEHOLDER: agent introduces himself as Jake from the future]"},
        {"pose": "worried", "text": "[PLACEHOLDER: the ice villain froze present-day Jake's heart]"},
        {"pose": "point",   "text": "[PLACEHOLDER: only she can thaw it, and he'll guide her]"},
        {"pose": "happy",   "text": "[PLACEHOLDER: call to action]",
         "button": {"label": "[PLACEHOLDER: button label]", "url_name": "operation_coco:next"}},
    ],
}


def prepare(script):
    """
    Return a copy of a script ready for json_script, with each button's
    url_name swapped for its resolved URL.
    """
    script = deepcopy(script)
    for line in script["lines"]:
        button = line.get("button")
        if button:
            line["button"] = {
                "label": button["label"],
                "url": reverse(button["url_name"]),
            }
    return script
