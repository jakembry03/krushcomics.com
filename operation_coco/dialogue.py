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


# DRAFT DIALOGUE — Jake will rewrite
# One line is picked at random when she misses a question three times.
UNLOCK_ENCOURAGE = {
    "draft": True,
    "lines": [
        {"speaker": "agent", "pose": "happy",
         "text": "Take your time, Coco. No rush. The answer's already in there somewhere."},
        {"speaker": "agent", "pose": "happy",
         "text": "Stuck? Try the hint. Even the best agents need a nudge now and then."},
        {"speaker": "agent", "pose": "happy",
         "text": "Think back for a moment. You remember more than you give yourself credit for."},
        {"speaker": "agent", "pose": "happy",
         "text": "Don't worry, it won't lock you out. Try saying it a different way."},
    ],
}

# DRAFT DIALOGUE — Jake will rewrite
# The villain's entrance on the desktop. His last line's cue makes him
# cackle; he flies off when she moves past it.
DESKTOP_VILLAIN = {
    "draft": True,
    "lines": [
        {"speaker": "villain", "pose": "cackle",
         "text": "Well, well, WELL! Look who finally made it in. Allow me to introduce myself..."},
        {"speaker": "villain", "pose": "smug",
         "text": f"I am {VILLAIN_NAME}! Master of frost, lord of the blizzard, and the coolest guy you'll ever meet. Literally."},
        {"speaker": "villain", "pose": "cackle",
         "text": "And I have frozen Jake's heart. Solid! Like a sad, lonely little ice cube!"},
        {"speaker": "villain", "pose": "point",
         "text": "See that little heart up there? Zero percent thawed. ZERO! Doesn't that just give you chills?"},
        {"speaker": "villain", "pose": "smug",
         "text": "Oh, and every memory on this computer? Frozen too. Every single one. I've been very busy."},
        {"speaker": "villain", "pose": "point",
         "text": "Better hurry, Coco. The longer that ice sets, the colder he gets. Tick tock, tick tock..."},
        {"speaker": "villain", "pose": "cackle",
         "text": "Toodle-oo! Try not to catch a cold! Mwa-ha-ha-HAAA!",
         "cue": "villain_exit"},
    ],
}

# DRAFT DIALOGUE — Jake will rewrite
# Agent Orange's rundown. The thaw cue on the second-to-last line thaws
# the first app.
DESKTOP_AGENT = {
    "draft": True,
    "lines": [
        {"speaker": "agent", "pose": "worried",
         "text": "Coco, are you alright? Sorry I'm late. Time-travel traffic is murder this time of year."},
        {"speaker": "agent", "pose": "worried",
         "text": "It's worse than I feared. Jake's heart has been frozen over, and we'll need to move fast."},
        {"speaker": "agent", "pose": "point",
         "text": "That meter up top is his heart. Right now it's a block of ice. We have to get it warm again."},
        {"speaker": "agent", "pose": "idle",
         "text": "You're the only one who can save him. I'll help however I can, but the real power here is yours."},
        {"speaker": "agent", "pose": "idle",
         "text": "Every app on this desktop holds a memory. Each one you recover will thaw his heart a little more."},
        {"speaker": "agent", "pose": "cast",
         "text": "Let me crack the first one open for you. Stand back... this might get a little toasty.",
         "cue": "thaw"},
        {"speaker": "agent", "pose": "happy",
         "text": "There! See it glowing? Click that app to begin. I'll be right here, Coco."},
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
