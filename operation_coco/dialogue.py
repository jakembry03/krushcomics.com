"""
Dialogue scripts, one per scene.

Every line here is a placeholder. Jake writes the real dialogue himself,
and real content never gets committed: it will arrive later through the
admin or a private, git-ignored fixture.

A script is a list of lines. Each line names its speaker ("agent" or
"villain"), the pose for that speaker's sprite, and its text. A line may
carry a cue (an animation the page plays when the line starts), and the
last line may carry a button whose url_name prepare() resolves before
the script reaches the page.
"""
from copy import deepcopy

from django.urls import reverse

# Working names; Jake will rename them. Used for every name tag.
AGENT_NAME = "Agent Orange"
VILLAIN_NAME = "[Villain name TBD]"

SPEAKERS = {
    "agent": {"name": AGENT_NAME},
    "villain": {"name": VILLAIN_NAME},
}

PHASE1_INTRO = {
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
    Return a copy of a script ready for json_script: speaker names added,
    every line's speaker filled in (default "agent"), and each button's
    url_name swapped for its resolved URL.
    """
    script = deepcopy(script)
    script["speakers"] = deepcopy(SPEAKERS)
    for line in script["lines"]:
        line.setdefault("speaker", "agent")
        button = line.get("button")
        if button:
            line["button"] = {
                "label": button["label"],
                "url": reverse(button["url_name"]),
            }
    return script
