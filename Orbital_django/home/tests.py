from django.test import TestCase
from models import User
from django.db import IntegrityError

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class TestUser(TestCase):
    def test_create_user(self):
        new_user = User()
        new_user.save()
        count = User.objects.all().count()
        self.assertEqual(count, 1)

    def test_user_default_property(self):
        new_user = User()
        new_user.save()
        portrait_url = new_user.portrait_url
        is_active = new_user.is_active
        nickname = new_user.nickname
        self.assertEqual(portrait_url, "media/portrait/default_portrait.png")
        self.assertEqual(is_active, True)
        self.assertEqual(nickname, "")

    def test_create_user_with_same_email_address(self):
        new_user = User()
        new_user.email_address = "test@test.test"
        new_user2 = User()
        new_user2.email_address = new_user.email_address
        new_user.save()
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(User.objects.filter(email_address="test@test.test").count(), 1)
        try:
            new_user2.save()
            self.assertTrue(False)
        except IntegrityError:
            self.assertTrue(True)

    def test_create_user_with_same_empty_email_address(self):
        new_user = User()
        new_user2 = User()
        new_user.save()
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(User.objects.filter(email_address="").count(), 1)
        try:
            new_user2.save()
            self.assertTrue(False)
        except IntegrityError:
            self.assertTrue(True)


class BrowserUITest(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def test_login_btn_functionality(self):
        self.browser.get(self.live_server_url)
        login_btn = self.browser.find_element_by_class_name("logInButton")
        login_btn.click()
        login_popup_window = self.browser.find_element_by_class_name("layui-layer")
        self.assertNotEqual(login_popup_window, None)
        self.assertIsNotNone(login_popup_window)
