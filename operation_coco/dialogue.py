"""
Dialogue scripts, one per scene.

Every scene here is DRAFT dialogue, marked "draft": True, so the story
has life during development. Jake will rewrite it all. Drafts speak
about the relationship in general terms only and invent no personal
details.

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

# DRAFT DIALOGUE — Jake will rewrite
PHASE1_INTRO = {
    "draft": True,
    "lines": [
        {"speaker": "agent", "pose": "worried",
         "text": "Wait! Don't bother trying again, Coco. That password isn't going to work. Not anymore."},
        {"speaker": "agent", "pose": "worried",
         "text": "Someone broke into Jake's system and locked it up tight. Everything on here is frozen."},
        {"speaker": "agent", "pose": "idle",
         "text": f"Sorry, where are my manners? I'm {AGENT_NAME}. I've come from... let's just say a long way off."},
        {"speaker": "agent", "pose": "point",
         "text": "The system is in lockdown. Before it lets anyone in, you'll have to prove you're really Coco."},
        {"speaker": "agent", "pose": "idle",
         "text": "It'll ask a few questions only the real Coco could answer. Something tells me you'll do just fine."},
        {"speaker": "agent", "pose": "happy",
         "text": "Ready? Let's get you through security.",
         "button": {"label": "Answer the security questions", "url_name": "operation_coco:unlock"}},
    ],
}


# One line is picked at random when she misses a question three times.
UNLOCK_ENCOURAGE = {
    "draft": True,
    "lines": [
        {"speaker": "agent", "pose": "happy", "text": "[PLACEHOLDER: encouragement 1]"},
        {"speaker": "agent", "pose": "happy", "text": "[PLACEHOLDER: encouragement 2]"},
        {"speaker": "agent", "pose": "happy", "text": "[PLACEHOLDER: encouragement 3]"},
    ],
}


# The villain's entrance on the desktop. His last line's cue makes him
# cackle; he flies off when she moves past it.
DESKTOP_VILLAIN = {
    "draft": True,
    "lines": [
        {"speaker": "villain", "pose": "cackle", "text": "[PLACEHOLDER: villain introduces himself]"},
        {"speaker": "villain", "pose": "point", "text": "[PLACEHOLDER: villain points at the heart meter]"},
        {"speaker": "villain", "pose": "smug", "text": "[PLACEHOLDER: villain gloats]"},
        {"speaker": "villain", "pose": "cackle", "text": "[PLACEHOLDER: villain leaves]", "cue": "villain_exit"},
    ],
}

# Agent Orange's rundown. The thaw cue on the second-to-last line thaws
# the first app.
DESKTOP_AGENT = {
    "draft": True,
    "lines": [
        {"speaker": "agent", "pose": "worried", "text": "[PLACEHOLDER: agent rundown]"},
        {"speaker": "agent", "pose": "point", "text": "[PLACEHOLDER: agent mentions Jake's heart]"},
        {"speaker": "agent", "pose": "cast", "text": "[PLACEHOLDER: agent thaws the first app]", "cue": "thaw"},
        {"speaker": "agent", "pose": "happy", "text": "[PLACEHOLDER: click the glowing app]"},
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
