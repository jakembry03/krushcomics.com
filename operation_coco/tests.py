import re

from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from .templatetags.coco_agent import POSES


# The site's CompressedManifestStaticFilesStorage needs `collectstatic` to
# have run before {% static %} can resolve, so tests use plain storage.
@override_settings(
    STORAGES={
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
)
class PageTests(SimpleTestCase):

    def test_pages_render(self):
        """
        Each page returns 200 with its own template.
        """
        pages = {
            "operation_coco:gate": "operation_coco/gate.html",
            "operation_coco:login": "operation_coco/login.html",
            "operation_coco:next": "operation_coco/next.html",
        }
        for url_name, template in pages.items():
            with self.subTest(url_name=url_name):
                response = self.client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, template)

    def test_login_rejects_post(self):
        """
        The lock screen never accepts a submitted password.
        """
        response = self.client.post(
            reverse("operation_coco:login"),
            {"password": "anything"},
        )
        self.assertEqual(response.status_code, 405)


class AgentSpriteTests(SimpleTestCase):

    def render_agent(self, pose="idle"):
        return Template(
            '{% include "operation_coco/partials/agent.html" with pose=pose %}'
        ).render(Context({"pose": pose}))

    def test_partial_inlines_every_pose(self):
        """
        All five poses are inlined so the page can swap them by class.
        """
        html = self.render_agent("worried")
        self.assertIn('class="agent agent--worried"', html)
        for pose in POSES:
            with self.subTest(pose=pose):
                self.assertIn(f"agent__pose--{pose}", html)
                self.assertIn(f'id="agent-{pose}-head"', html)

    def test_named_group_ids_are_unique(self):
        """
        Prefixing keeps ids like #head unique with every pose on the page.
        """
        ids = re.findall(r'\bid="([^"]+)"', self.render_agent())
        self.assertEqual(len(ids), len(set(ids)))

    def test_unknown_pose_is_an_error(self):
        with self.assertRaises(TemplateSyntaxError):
            Template('{% load coco_agent %}{% agent_pose "dab" %}').render(Context())
