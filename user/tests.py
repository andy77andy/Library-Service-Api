from django.contrib.auth import get_user_model
from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

TOKEN_URL = reverse("user:token_obtain_pair")
DETAIL_URL = reverse("user:manage")


class UnauthenticatedUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_forbidden_token_url(self) -> None:
        credentials = {
            "email": "test@test.com",
            "password": "test123456"
        }
        response = self.client.post(TOKEN_URL, credentials)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_me_url(self) -> None:
        response = self.client.post(DETAIL_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test123456",
        )
        self.client.force_authenticate(self.user)

    def test_user_receive_token(self) -> None:
        credentials = {
            "email": "test@test.com",
            "password": "test123456"
        }
        response = self.client.post(TOKEN_URL, credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_me_endpoint(self) -> None:
        user1 = get_user_model().objects.create_user(
            email="test1@test.com",
            password="test1123456",
        )
        response = self.client.get(DETAIL_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("email"), self.user.email)
