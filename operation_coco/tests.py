import json
import re
from html.parser import HTMLParser

from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse

from .dialogue import AGENT_NAME, PHASE1_INTRO, VILLAIN_NAME, prepare
from .progress import THAW_KEY
from .templatetags.coco_sprites import POSES

PAGES = {
    "operation_coco:gate": "operation_coco/gate.html",
    "operation_coco:login": "operation_coco/login.html",
    "operation_coco:next": "operation_coco/next.html",
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
        self.assertEqual(data["lines"][-1]["button"]["url"], reverse("operation_coco:next"))

    def test_login_dialogue_button_url_is_resolved(self):
        """
        The view swaps url_name for a ready URL before rendering.
        """
        response = self.client.get(reverse("operation_coco:login"))
        last_line = response.context["dialogue"]["lines"][-1]
        self.assertEqual(last_line["button"]["url"], reverse("operation_coco:next"))
        self.assertNotIn("url_name", last_line["button"])

    def test_login_and_next_show_the_agent(self):
        for url_name in ("operation_coco:login", "operation_coco:next"):
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertTemplateUsed(response, "operation_coco/partials/agent.html")


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

    def test_lines_are_placeholders(self):
        """
        Real dialogue never gets committed; every line stays a placeholder.
        """
        for line in PHASE1_INTRO["lines"]:
            with self.subTest(text=line["text"]):
                self.assertTrue(line["text"].startswith("[PLACEHOLDER"))


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
