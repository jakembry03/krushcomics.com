from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import CTF, WriteUp
from .services import get_latest_security_items
from .templatetags.security_markdown import render_markdown


class SecurityTestData(TestCase):

    def setUp(self):
        """
        Create test data before each test runs.

        Django creates a separate temporary test database, so these
        objects do not affect the real development or production data.
        """

        self.ctf = CTF.objects.create(
            name="DEADFACE",
            year=2026,
            slug="deadface-2026",
        )

        self.published = WriteUp.objects.create(
            ctf=self.ctf,
            title="A Pirates Life for Me: Part 1",
            slug="a-pirates-life-part-1",
            category=WriteUp.Category.NETWORKING,
            difficulty=WriteUp.Difficulty.MEDIUM,
            tools="Wireshark, Python, ",
            summary="Find the flag hidden in a packet capture.",
            body="Filter the traffic:\n\n```\nhttp.request\n```",
            lessons_learned="Follow the TCP stream.",
            is_published=True,
        )

        self.draft = WriteUp.objects.create(
            ctf=self.ctf,
            title="Secret Draft Challenge",
            slug="secret-draft",
            category=WriteUp.Category.WEB,
            difficulty=WriteUp.Difficulty.EASY,
            summary="Not finished yet.",
            body="Draft body.",
        )


class WriteUpModelTests(SecurityTestData):

    def test_url_includes_ctf_and_challenge(self):
        """
        Write-up URLs follow /security/writeups/<ctf>/<challenge>/.
        """

        self.assertEqual(
            self.published.get_absolute_url(),
            "/security/writeups/deadface-2026/a-pirates-life-part-1/",
        )


    def test_published_at_set_on_first_publish(self):
        """
        Publishing fills in published_at; drafts leave it empty.
        """

        self.assertIsNotNone(self.published.published_at)
        self.assertIsNone(self.draft.published_at)

        self.draft.is_published = True
        self.draft.save()

        self.assertIsNotNone(self.draft.published_at)


    def test_slug_unique_within_ctf_only(self):
        """
        The same challenge slug may be reused in a different CTF,
        but not twice in the same CTF.
        """

        other_ctf = CTF.objects.create(
            name="DEADFACE",
            year=2027,
            slug="deadface-2027",
        )

        WriteUp.objects.create(
            ctf=other_ctf,
            title="A Pirates Life for Me: Part 1",
            slug="a-pirates-life-part-1",
            category=WriteUp.Category.NETWORKING,
            difficulty=WriteUp.Difficulty.MEDIUM,
            summary="Next year's version.",
            body="Body.",
        )

        with self.assertRaises(IntegrityError):
            WriteUp.objects.create(
                ctf=self.ctf,
                title="Duplicate",
                slug="a-pirates-life-part-1",
                category=WriteUp.Category.MISC,
                difficulty=WriteUp.Difficulty.EASY,
                summary="Duplicate.",
                body="Body.",
            )


    def test_tool_list_ignores_blank_entries(self):

        self.assertEqual(
            self.published.tool_list,
            ["Wireshark", "Python"],
        )


# Page tests render templates that use {% static %}. The site's
# CompressedManifestStaticFilesStorage needs `collectstatic` to have run,
# which CI does not do, so use plain static storage for these tests.
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
class SecurityPageTests(SecurityTestData):

    def test_hub_shows_published_only(self):
        """
        The Security hub carousel lists published write-ups and links
        to all three sections.
        """

        response = self.client.get(reverse("security"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published.title)
        self.assertNotContains(response, self.draft.title)

        self.assertContains(response, reverse("writeup_list"))
        self.assertContains(response, reverse("security_labs"))
        self.assertContains(response, reverse("security_research"))


    def test_latest_items_newest_first(self):

        newer = WriteUp.objects.create(
            ctf=self.ctf,
            title="Newer Challenge",
            slug="newer",
            category=WriteUp.Category.CRYPTO,
            difficulty=WriteUp.Difficulty.HARD,
            summary="Newer.",
            body="Body.",
            is_published=True,
        )

        self.assertEqual(
            get_latest_security_items(),
            [newer, self.published],
        )


    def test_writeup_list_and_search(self):

        response = self.client.get(reverse("writeup_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published.title)
        self.assertNotContains(response, self.draft.title)

        response = self.client.get(
            reverse("writeup_list"),
            {"q": "wireshark"},
        )

        self.assertContains(response, self.published.title)

        response = self.client.get(
            reverse("writeup_list"),
            {"q": "no-such-thing"},
        )

        self.assertNotContains(response, self.published.title)


    def test_ctf_detail_lists_its_writeups(self):

        response = self.client.get(self.ctf.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published.title)
        self.assertNotContains(response, self.draft.title)


    def test_writeup_detail_shows_all_sections(self):

        response = self.client.get(self.published.get_absolute_url())

        self.assertEqual(response.status_code, 200)

        for text in (
            "DEADFACE 2026",
            "Networking",
            "Medium",
            "Wireshark",
            "Summary",
            "Lessons Learned",
            "<pre><code>http.request",
        ):
            self.assertContains(response, text)


    def test_draft_hidden_from_public(self):

        response = self.client.get(self.draft.get_absolute_url())

        self.assertEqual(response.status_code, 404)


    def test_draft_visible_to_staff(self):

        staff = get_user_model().objects.create_user(
            username="staff",
            password="test-password",
            is_staff=True,
        )

        self.client.force_login(staff)

        response = self.client.get(self.draft.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Draft preview")


    def test_coming_soon_sections(self):

        for name in ("security_labs", "security_research"):
            response = self.client.get(reverse(name))

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, "Coming Soon")


    def test_navbar_and_footer_link_to_security(self):
        """
        Security appears in both the navbar and the footer.
        """

        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            'href="/security/"',
            count=2,
        )


class MarkdownTests(TestCase):

    def test_raw_html_is_escaped(self):

        html = render_markdown("<script>alert(1)</script>")

        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)


    def test_unsafe_link_removed(self):

        html = render_markdown("[click](javascript:alert(1))")

        self.assertNotIn("javascript:", html)


    def test_safe_link_kept(self):

        html = render_markdown("[site](https://example.com)")

        self.assertIn('href="https://example.com"', html)
