from django.test import SimpleTestCase, override_settings
from django.urls import reverse


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
