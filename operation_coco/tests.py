import json
import re
from html.parser import HTMLParser
from io import StringIO
from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .answers import check_answer, hash_answer, normalize_answer
from .desktop import DESKTOP_APPS
from .dialogue import AGENT_NAME, PHASE1_INTRO, VILLAIN_NAME, prepare
from .models import SecurityQuestion
from .progress import THAW_KEY, UNLOCKED_KEY
from .templatetags.coco_sprites import POSES

PAGES = {
    "operation_coco:gate": "operation_coco/gate.html",
    "operation_coco:login": "operation_coco/login.html",
    "operation_coco:unlock": "operation_coco/unlock.html",
}


class TagCollector(HTMLParser):
    """
    Collects every start tag as (tag, attrs) so tests can check markup
    without depending on exact formatting.
    """

    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    def find(self, tag, **attrs):
        return [
            found for name, found in self.tags
            if name == tag and all(found.get(k) == v for k, v in attrs.items())
        ]


# The site's CompressedManifestStaticFilesStorage needs `collectstatic` to
# have run before {% static %} can resolve, so tests use plain storage.
plain_static_storage = override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
)


# Real hashers are deliberately slow; tests don't need that.
fast_hashing = override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)


def parse(response):
    collector = TagCollector()
    collector.feed(response.content.decode())
    return collector


@plain_static_storage
class PageTests(TestCase):

    def test_pages_render(self):
        """
        Each page returns 200 with its own template.
        """
        for url_name, template in PAGES.items():
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)

    def test_every_page_is_noindex(self):
        """
        Search engines are asked not to list any page in the app.
        """
        for url_name in PAGES:
            with self.subTest(url_name=url_name):
                tags = parse(self.client.get(reverse(url_name)))
                self.assertEqual(
                    tags.find("meta", name="robots", content="noindex, nofollow"),
                    [{"name": "robots", "content": "noindex, nofollow"}],
                )

    def test_pages_do_not_use_the_site_base_template(self):
        for url_name in PAGES:
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertTemplateUsed(response, "operation_coco/base.html")
                self.assertTemplateNotUsed(response, "core/base.html")

    def test_no_inline_scripts_or_external_assets(self):
        """
        Scripts load from files with defer; the only inline script is
        json_script data. Nothing loads from another host.
        """
        for url_name in PAGES:
            with self.subTest(url_name=url_name):
                tags = parse(self.client.get(reverse(url_name)))
                for attrs in tags.find("script"):
                    if "src" in attrs:
                        self.assertIn("defer", attrs)
                        self.assertTrue(attrs["src"].startswith("/static/operation_coco/"))
                    else:
                        self.assertEqual(attrs.get("type"), "application/json")
                for attrs in tags.find("link"):
                    self.assertTrue(attrs["href"].startswith("/static/operation_coco/"))

    def test_gate_links_to_login(self):
        tags = parse(self.client.get(reverse("operation_coco:gate")))
        self.assertTrue(tags.find("a", href=reverse("operation_coco:login")))

    def test_gate_content(self):
        response = self.client.get(reverse("operation_coco:gate"))
        self.assertContains(response, "<title>Operation Coco</title>", html=True)
        self.assertContains(response, "Coco's Wedding Game")
        self.assertContains(response, "If you are Coco, please proceed.")

    def test_login_form_never_submits(self):
        """
        The password form has no method="post" and no action, so nothing
        Coco types can be sent anywhere.
        """
        tags = parse(self.client.get(reverse("operation_coco:login")))
        forms = tags.find("form")
        self.assertEqual(len(forms), 1)
        for attrs in forms:
            self.assertNotIn("action", attrs)
            self.assertNotEqual(attrs.get("method", "").lower(), "post")

    def test_password_field_is_not_saved(self):
        """
        The password input has no name and autocomplete is off, so the
        browser has nothing to remember.
        """
        tags = parse(self.client.get(reverse("operation_coco:login")))
        fields = tags.find("input", type="password")
        self.assertEqual(len(fields), 1)
        self.assertNotIn("name", fields[0])
        self.assertEqual(fields[0].get("autocomplete"), "off")

    def test_login_rejects_post(self):
        """
        The lock screen never accepts a submitted password.
        """
        response = self.client.post(
            reverse("operation_coco:login"),
            {"password": "anything"},
        )
        self.assertEqual(response.status_code, 405)

    def test_login_has_dialogue_data(self):
        """
        The dialogue script reaches the page through json_script, with the
        last line's button pointing at the next page.
        """
        response = self.client.get(reverse("operation_coco:login"))
        match = re.search(
            r'<script id="dialogue-data" type="application/json">(.*?)</script>',
            response.content.decode(),
            re.S,
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(len(data["lines"]), len(PHASE1_INTRO["lines"]))
        self.assertEqual(data["lines"][-1]["button"]["url"], reverse("operation_coco:unlock"))

    def test_login_dialogue_button_url_is_resolved(self):
        """
        The view swaps url_name for a ready URL before rendering.
        """
        response = self.client.get(reverse("operation_coco:login"))
        last_line = response.context["dialogue"]["lines"][-1]
        self.assertEqual(last_line["button"]["url"], reverse("operation_coco:unlock"))
        self.assertNotIn("url_name", last_line["button"])

    def test_login_shows_the_agent(self):
        response = self.client.get(reverse("operation_coco:login"))
        self.assertTemplateUsed(response, "operation_coco/partials/agent.html")

    def test_next_redirects_to_unlock(self):
        """
        The end of Phase 1 now leads into the security questions.
        """
        response = self.client.get(reverse("operation_coco:next"))
        self.assertRedirects(response, reverse("operation_coco:unlock"))


@plain_static_storage
class ThawLevelTests(TestCase):

    def body_style(self, url):
        tags = parse(self.client.get(url))
        return tags.find("body")[0]["style"]

    def test_every_page_sets_thaw_on_body(self):
        for url_name in PAGES:
            with self.subTest(url_name=url_name):
                self.assertEqual(self.body_style(reverse(url_name)), "--thaw: 0.000")

    def test_thaw_comes_from_the_session(self):
        session = self.client.session
        session[THAW_KEY] = 0.25
        session.save()
        self.assertEqual(self.body_style(reverse("operation_coco:gate")), "--thaw: 0.250")

    @override_settings(DEBUG=False)
    def test_thaw_override_is_ignored_without_debug(self):
        url = reverse("operation_coco:gate") + "?thaw=0.5"
        self.assertEqual(self.body_style(url), "--thaw: 0.000")

    @override_settings(DEBUG=True)
    def test_thaw_override_previews_with_debug(self):
        cases = {"0.5": "0.500", "1": "1.000", "7": "1.000", "-2": "0.000", "nope": "0.000", "nan": "0.000"}
        for value, expected in cases.items():
            with self.subTest(value=value):
                url = reverse("operation_coco:gate") + f"?thaw={value}"
                self.assertEqual(self.body_style(url), f"--thaw: {expected}")


class DialogueTests(SimpleTestCase):

    def test_prepare_adds_speakers(self):
        """
        Every line names a speaker with a name tag, defaulting to the agent.
        """
        script = prepare({"lines": [
            {"pose": "idle", "text": "Hello."},
            {"speaker": "villain", "pose": "cackle", "text": "Mwahaha!", "cue": "villain_exit"},
        ]})
        self.assertEqual([line["speaker"] for line in script["lines"]], ["agent", "villain"])
        self.assertEqual(script["speakers"]["agent"]["name"], AGENT_NAME)
        self.assertEqual(script["speakers"]["villain"]["name"], VILLAIN_NAME)
        self.assertEqual(script["lines"][1]["cue"], "villain_exit")

    def test_prepare_leaves_the_script_unchanged(self):
        prepare(PHASE1_INTRO)
        self.assertIn("url_name", PHASE1_INTRO["lines"][-1]["button"])

    def test_lines_use_known_poses(self):
        for line in PHASE1_INTRO["lines"]:
            with self.subTest(text=line["text"]):
                self.assertIn(line["pose"], POSES["agent"])

    def test_scenes_are_marked_draft(self):
        """
        Jake rewrites all dialogue, so every scene is flagged as a draft.
        """
        self.assertIs(PHASE1_INTRO.get("draft"), True)

    def test_lines_fit_a_phone(self):
        for line in PHASE1_INTRO["lines"]:
            with self.subTest(text=line["text"]):
                self.assertLessEqual(len(line["text"]), 140)


class AgentSpriteTests(SimpleTestCase):

    def render_agent(self, pose="idle"):
        return Template(
            '{% include "operation_coco/partials/agent.html" with pose=pose %}'
        ).render(Context({"pose": pose}))

    def test_partial_inlines_every_pose(self):
        """
        All six poses are inlined so the page can swap them by class.
        """
        html = self.render_agent("worried")
        self.assertIn('class="sprite agent pose-worried"', html)
        for pose in POSES["agent"]:
            with self.subTest(pose=pose):
                self.assertIn(f"sprite__pose--{pose}", html)
                for group in ("head", "hood", "mask", "face", "eyes"):
                    self.assertIn(f'id="agent-{pose}-{group}"', html)

    def test_ids_and_references_are_unique(self):
        """
        Prefixing keeps ids like #glow unique with every pose on the page,
        and references follow their ids.
        """
        html = self.render_agent()
        ids = re.findall(r'\bid="([^"]+)"', html)
        self.assertEqual(len(ids), len(set(ids)))
        for ref in set(re.findall(r"url\(#([^)]+)\)", html)):
            self.assertIn(ref, ids)

    def test_svgs_hold_no_colors(self):
        """
        Colors come from coco.css so the glow can follow the thaw level.
        """
        html = self.render_agent()
        self.assertNotRegex(html, r"#[0-9A-Fa-f]{3,6}\b(?![^<]*-->)")
        self.assertNotRegex(html, r'(fill|stroke)="(?!none)')

    def test_unknown_pose_is_an_error(self):
        with self.assertRaises(TemplateSyntaxError):
            Template('{% load coco_sprites %}{% sprite_pose "agent" "dab" %}').render(Context())


class SecurityQuestionModelTests(TestCase):

    def test_ordered_by_order(self):
        SecurityQuestion.objects.create(order=2, prompt="Favorite color?", answer_hashes=[])
        SecurityQuestion.objects.create(order=1, prompt="Favorite snack?", answer_hashes=[])
        self.assertEqual([q.order for q in SecurityQuestion.objects.all()], [1, 2])

    def test_at_most_three_hints(self):
        question = SecurityQuestion(order=1, prompt="Favorite snack?", hints=["a", "b", "c", "d"])
        with self.assertRaises(ValidationError):
            question.full_clean()


class NormalizeAnswerTests(SimpleTestCase):

    def test_examples_match(self):
        cases = [
            ("The Cat & the Hat", "cat hat"),
            ("A Red Balloon", "red balloon"),
            ("  RED   balloon!!  ", "red balloon"),
            ("Café Paris", "cafe paris"),
            ("rock-and-roll", "rock & roll"),
            ("An Ocean's Song", "oceans song"),
            ("Ｆｕｌｌｗｉｄｔｈ", "fullwidth"),
            ("Room 12B", "room 12 b"),
        ]
        for first, second in cases:
            with self.subTest(first=first, second=second):
                self.assertEqual(normalize_answer(first), normalize_answer(second))

    def test_expected_forms(self):
        self.assertEqual(normalize_answer("The Cat & the Hat"), "cathat")
        self.assertEqual(normalize_answer("A Red Balloon"), "redballoon")

    def test_different_answers_differ(self):
        self.assertNotEqual(normalize_answer("red balloon"), normalize_answer("blue balloon"))
        self.assertNotEqual(normalize_answer("theater"), normalize_answer("ater"))

    def test_only_stop_words_is_empty(self):
        self.assertEqual(normalize_answer("The & a"), "")
        self.assertEqual(normalize_answer(""), "")
        self.assertEqual(normalize_answer(None), "")


@fast_hashing
class CheckAnswerTests(SimpleTestCase):

    def setUp(self):
        self.question = SecurityQuestion(
            order=1,
            prompt="What did the cat wear?",
            answer_hashes=[hash_answer("The Cat in the Hat"), hash_answer("striped hat")],
        )

    def test_accepts_any_variant_loosely_typed(self):
        for answer in ("cat in hat", "THE CAT IN THE HAT!", "Striped Hat", "a striped hat"):
            with self.subTest(answer=answer):
                self.assertTrue(check_answer(self.question, answer))

    def test_rejects_wrong_and_empty(self):
        for answer in ("dog in hat", "", "   ", "the"):
            with self.subTest(answer=answer):
                self.assertFalse(check_answer(self.question, answer))

    def test_hashes_do_not_contain_the_answer(self):
        for stored in self.question.answer_hashes:
            self.assertNotIn("cat", stored)

    def test_empty_answer_cannot_be_hashed(self):
        with self.assertRaises(ValueError):
            hash_answer("The")


@fast_hashing
class SetCocoQuestionsCommandTests(TestCase):

    COMMAND = "operation_coco.management.commands.set_coco_questions"

    def run_command(self, inputs, secrets):
        out = StringIO()
        with patch("builtins.input", side_effect=inputs), \
                patch(f"{self.COMMAND}.getpass", side_effect=secrets):
            call_command("set_coco_questions", stdout=out)
        return out.getvalue()

    def three_questions(self):
        inputs = [
            "What did the cat wear?", "Striped.", "Tall.", "",
            "Favorite fruit?", "",
            "Favorite color?", "Sky.", "Ocean.", "Not green.",
        ]
        secrets = [
            # Question 1: main answer, a mistyped confirmation, then a variant.
            "The Cat in the Hat", "The Cat in the Hat", "striped hat", "striped hta",
            "striped hat", "striped hat", "",
            # Question 2: a blank and a stop-word-only answer are re-asked.
            "", "The", "Banana", "Banana", "",
            # Question 3
            "blue", "blue", "",
        ]
        return inputs, secrets

    def test_saves_three_hashed_questions(self):
        out = self.run_command(*self.three_questions())

        self.assertIn("Saved 3 questions", out)
        questions = list(SecurityQuestion.objects.all())
        self.assertEqual([q.order for q in questions], [1, 2, 3])
        self.assertEqual(questions[0].prompt, "What did the cat wear?")
        self.assertEqual(questions[0].hints, ["Striped.", "Tall."])
        self.assertEqual(questions[1].hints, [])
        self.assertEqual(questions[2].hints, ["Sky.", "Ocean.", "Not green."])
        self.assertEqual([len(q.answer_hashes) for q in questions], [2, 1, 1])

        self.assertTrue(check_answer(questions[0], "cat in hat"))
        self.assertTrue(check_answer(questions[0], "Striped Hat"))
        self.assertFalse(check_answer(questions[0], "striped hta"))
        self.assertTrue(check_answer(questions[1], "banana"))
        self.assertTrue(check_answer(questions[2], "BLUE"))

    def test_never_outputs_or_stores_answers(self):
        out = self.run_command(*self.three_questions())
        stored = repr([(q.prompt, q.answer_hashes, q.hints) for q in SecurityQuestion.objects.all()])
        for answer in ("Cat in the Hat", "cathat", "striped", "Banana", "banana", "blue"):
            with self.subTest(answer=answer):
                self.assertNotIn(answer, out)
                self.assertNotIn(answer, stored.replace("What did the cat wear?", ""))

    def test_replaces_existing_questions_after_confirming(self):
        SecurityQuestion.objects.create(order=1, prompt="Old?", answer_hashes=[])
        inputs, secrets = self.three_questions()
        self.run_command(["y", *inputs], secrets)
        self.assertEqual(SecurityQuestion.objects.count(), 3)
        self.assertFalse(SecurityQuestion.objects.filter(prompt="Old?").exists())

    def test_declining_changes_nothing(self):
        SecurityQuestion.objects.create(order=1, prompt="Old?", answer_hashes=[])
        out = self.run_command(["n"], [])
        self.assertIn("Nothing changed", out)
        self.assertEqual(list(SecurityQuestion.objects.values_list("prompt", flat=True)), ["Old?"])


@fast_hashing
@plain_static_storage
class UnlockTests(TestCase):

    def setUp(self):
        # Made-up questions and answers only.
        SecurityQuestion.objects.create(
            order=1, prompt="What did the cat wear?",
            answer_hashes=[hash_answer("The Cat in the Hat")], hints=["Striped.", "Tall."],
        )
        SecurityQuestion.objects.create(
            order=2, prompt="Favorite fruit?", answer_hashes=[hash_answer("banana")], hints=[],
        )
        SecurityQuestion.objects.create(
            order=3, prompt="Favorite color?", answer_hashes=[hash_answer("blue")], hints=["Sky."],
        )
        self.url = reverse("operation_coco:unlock")

    def post(self, answer="", question=1, action="answer"):
        return self.client.post(
            self.url,
            {"answer": answer, "question": question, "action": action},
            HTTP_ACCEPT="application/json",
        ).json()

    def test_shows_the_first_question(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Account locked")
        self.assertContains(response, "What did the cat wear?")
        self.assertNotContains(response, "Favorite fruit?")
        self.assertContains(response, "Need a hint?")  # in the page, but hidden
        self.assertNotContains(response, "Striped.")

    def test_correct_answers_advance_one_at_a_time(self):
        state = self.post("cat in the hat", question=1)
        self.assertEqual(state["result"], "correct")
        self.assertEqual(state["solved"], 1)
        self.assertEqual(state["question"]["prompt"], "Favorite fruit?")

        state = self.post("BANANA", question=2)
        self.assertEqual((state["result"], state["solved"]), ("correct", 2))

        state = self.post("Blue!", question=3)
        self.assertEqual(state["result"], "unlocked")
        self.assertEqual(state["redirect"], reverse("operation_coco:desktop"))
        self.assertIs(self.client.session[UNLOCKED_KEY], True)

    def test_wrong_answers_do_not_advance(self):
        state = self.post("dog in the hat", question=1)
        self.assertEqual(state["result"], "wrong")
        self.assertEqual(state["solved"], 0)
        self.assertNotIn(UNLOCKED_KEY, self.client.session)

    def test_cannot_skip_ahead_by_tampering(self):
        """
        Answering a later question's answer, or claiming to be on a later
        question, never advances past the current one.
        """
        self.assertEqual(self.post("banana", question=1)["result"], "wrong")
        state = self.post("banana", question=2)
        self.assertEqual((state["result"], state["solved"]), ("stale", 0))

    def test_blank_answer_is_not_a_miss(self):
        self.assertEqual(self.post("   ")["result"], "blank")
        self.assertFalse(self.post("   ")["hint_available"])

    def test_hints_only_after_a_miss(self):
        state = self.post(action="hint")
        self.assertEqual(state["hints"], [])
        self.assertFalse(state["hint_available"])

        self.assertTrue(self.post("dog")["hint_available"])
        self.assertEqual(self.post(action="hint")["hints"], ["Striped."])
        state = self.post(action="hint")
        self.assertEqual(state["hints"], ["Striped.", "Tall."])
        self.assertFalse(state["hint_available"])
        self.assertEqual(self.post(action="hint")["hints"], ["Striped.", "Tall."])

    def test_third_miss_brings_encouragement(self):
        results = [self.post(f"wrong {n}")["result"] for n in range(1, 7)]
        self.assertEqual(results, ["wrong", "wrong", "encourage", "wrong", "wrong", "encourage"])

    def test_without_javascript(self):
        """
        The form also works as a plain POST: a wrong answer re-renders
        with her text kept; a right one redirects.
        """
        response = self.client.post(self.url, {"answer": "dog hat", "question": 1, "action": "answer"})
        self.assertContains(response, "That answer doesn't match our records.")
        self.assertContains(response, 'value="dog hat"')

        response = self.client.post(self.url, {"answer": "cat in hat", "question": 1, "action": "answer"})
        self.assertRedirects(response, self.url)

    def test_unlocked_visitors_go_to_the_desktop(self):
        session = self.client.session
        session[UNLOCKED_KEY] = True
        session.save()
        self.assertRedirects(self.client.get(self.url), reverse("operation_coco:desktop"))

    def test_desktop_requires_unlocking(self):
        self.assertRedirects(self.client.get(reverse("operation_coco:desktop")), self.url)

    def test_no_questions_yet(self):
        SecurityQuestion.objects.all().delete()
        response = self.client.get(self.url)
        self.assertContains(response, "haven't been set up yet")


@plain_static_storage
class DesktopTests(TestCase):

    def setUp(self):
        session = self.client.session
        session[UNLOCKED_KEY] = True
        session.save()
        self.url = reverse("operation_coco:desktop")

    def test_six_frozen_apps_and_the_heart_meter(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "operation_coco/partials/desktop_shell.html")
        tags = parse(response)
        frozen = [a for _, a in tags.tags if "is-frozen" in a.get("class", "").split()]
        self.assertEqual(len(frozen), len(DESKTOP_APPS))
        self.assertEqual(len(DESKTOP_APPS), 6)
        self.assertContains(response, "Jake's heart: </span>0%")
        for app in DESKTOP_APPS:
            self.assertContains(response, app["label"])

    def test_frozen_apps_are_not_links(self):
        tags = parse(self.client.get(self.url))
        self.assertEqual(tags.find("a", **{"data-app-link": None}), [])

    def test_heart_meter_follows_thaw_level(self):
        session = self.client.session
        session[THAW_KEY] = 0.5
        session.save()
        self.assertContains(self.client.get(self.url), "50%")
