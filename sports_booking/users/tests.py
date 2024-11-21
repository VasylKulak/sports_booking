from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from unittest.mock import patch


class BaseUserTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser",
                                             email="testuser@example.com",
                                             password="password",
                                             role=User.USER)
        self.trainer = User.objects.create_user(username="trainer",
                                                email="trainer@example.com",
                                                password="password",
                                                role=User.TRAINER)


class UserModelTest(BaseUserTestCase):
    def test_user_role_default(self):
        user = User.objects.create_user(username="newuser",
                                        email="newuser@example.com",
                                        password="password")
        self.assertEqual(user.role, User.USER)

    def test_is_trainer_method(self):
        self.assertTrue(self.trainer.is_trainer())
        self.assertFalse(self.user.is_trainer())

    def test_user_str_representation(self):
        self.assertEqual(str(self.user), "testuser")


from users.serializers import RegisterSerializer, UserSerializer


class RegisterSerializerTest(BaseUserTestCase):
    def test_register_serializer_valid(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "password2": "newpassword",
            "role": User.USER
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_register_serializer_password_mismatch(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "password2": "wrongpassword",
            "role": User.USER
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["password"][0],
                         "Password fields didn't match.")


class UserSerializerTest(BaseUserTestCase):
    def test_user_serializer(self):
        serializer = UserSerializer(instance=self.user)
        expected_data = {
            "id": self.user.id,
            "username": "testuser",
            "email": "testuser@example.com",
            "role": User.USER,
            "bio": None
        }
        self.assertDictEqual(serializer.data, expected_data)


class RegisterViewTest(BaseUserTestCase):
    def test_register_success(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "password2": "newpassword",
            "role": User.USER
        }
        response = self.client.post("/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)

    def test_register_password_mismatch(self):
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword",
            "password2": "wrongpassword",
            "role": User.USER
        }
        response = self.client.post("/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Password fields didn't match.",
                      response.data["password"])


class UserProfileViewTest(BaseUserTestCase):
    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "testuser")

    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)
        data = {"bio": "This is a test bio."}
        response = self.client.put("/profile/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, "This is a test bio.")


class ForgotPasswordViewTest(BaseUserTestCase):
    @patch("users.views.send_mail")
    def test_forgot_password_email_sent(self, mock_send_mail):
        data = {"email": "testuser@example.com"}
        response = self.client.post("/forgot-password/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mock_send_mail.called)

    def test_forgot_password_email_invalid(self):
        data = {"email": "nonexistent@example.com"}
        response = self.client.post("/forgot-password/", data)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)


class ResetPasswordViewTest(BaseUserTestCase):
    def test_reset_password_success(self):
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        data = {"token": token, "password": "newpassword",
                "password2": "newpassword"}
        response = self.client.post(f"/reset-password/?uid={uid}", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword"))

    def test_reset_password_invalid_link(self):
        data = {"token": "invalidtoken", "password": "newpassword",
                "password2": "newpassword"}
        response = self.client.post(f"/reset-password/?uid=invaliduid", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "Invalid reset link")
