from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.test.client import RequestFactory
from student.tests.factories import UserFactory
from user_api.models import UserPreference
from notification_prefs import NOTIFICATION_PREF_KEY
from notification_prefs.views import enable, disable


class NotificationPrefViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory.create()
        self.value = "test value"
        self.request_factory = RequestFactory()

    def create_pref(self):
        UserPreference.objects.create(user=self.user, key=NOTIFICATION_PREF_KEY, value=self.value)

    def get_pref_exists(self):
        return UserPreference.objects.filter(user=self.user, key=NOTIFICATION_PREF_KEY).exists()

    # Enable view

    def test_enable_get(self):
        request = self.request_factory.get("dummy")
        request.user = self.user
        response = enable(request)
        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.get_pref_exists())

    def test_enable_anon_user(self):
        request = self.request_factory.post("dummy")
        request.user = AnonymousUser()
        response = enable(request)
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.get_pref_exists())

    def test_enable_success(self):
        request = self.request_factory.post("dummy")
        request.user = self.user
        response = enable(request)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.get_pref_exists())

    def test_enable_already_enabled(self):
        self.create_pref()
        request = self.request_factory.post("dummy")
        request.user = self.user
        response = enable(request)
        self.assertEqual(response.status_code, 204)
        self.assertTrue(self.get_pref_exists())
        self.assertEqual(
            UserPreference.objects.get(user=self.user, key=NOTIFICATION_PREF_KEY).value,
            self.value
        )

    def test_enable_distinct_values(self):
        request = self.request_factory.post("dummy")
        request.user = self.user
        enable(request)
        other_user = UserFactory.create()
        request.user = other_user
        enable(request)
        self.assertNotEqual(
            UserPreference.objects.get(user=self.user, key=NOTIFICATION_PREF_KEY).value,
            UserPreference.objects.get(user=other_user, key=NOTIFICATION_PREF_KEY).value
        )

    # Disable view

    def test_disable_get(self):
        self.create_pref()
        request = self.request_factory.get("dummy")
        request.user = self.user
        response = disable(request)
        self.assertEqual(response.status_code, 405)
        self.assertTrue(self.get_pref_exists())

    def test_disable_anon_user(self):
        self.create_pref()
        request = self.request_factory.post("dummy")
        request.user = AnonymousUser()
        response = disable(request)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(self.get_pref_exists())

    def test_disable_success(self):
        self.create_pref()
        request = self.request_factory.post("dummy")
        request.user = self.user
        response = disable(request)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.get_pref_exists())

    def test_disable_already_disabled(self):
        request = self.request_factory.post("dummy")
        request.user = self.user
        response = disable(request)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(self.get_pref_exists())
