from django.test import TestCase

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from book.models import Book
from book.serializers import BookSerializer

BOOK_URL = reverse("book:book-list")


def detail_url(book_id: int):
    return reverse("book:book-detail", args=[book_id])


def sample_book(**params):
    defaults = {
        "title": "On thr road",
        "author": "Jack Kerouac",
        "cover": "Hard",
        "inventory": 5,
        "daily_fee": 0.77,
    }
    defaults.update(params)

    return Book.objects.create(**defaults)


class BookUnAuthApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_forbidden_unauth(self):
        sample_book()
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BookNotAdminApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test1.com",
            "test1234",
        )
        self.client.force_authenticate(self.user)

    def test_forbidden_unauth(self):
        sample_book()
        response = self.client.get(BOOK_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_book(self):
        payload = {
            "title": "On the road",
            "author": "Jack Kerouac",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": 0.77,
        }
        response = self.client.post(BOOK_URL, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BookAdminApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test1.com", "test1234", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_book(self):
        payload = {
            "title": "On the road",
            "author": "Jack Kerouac",
            "cover": "Hard",
            "inventory": 5,
            "daily_fee": 0.77,
        }
        response = self.client.post(BOOK_URL, payload, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_book(self):
        book = sample_book()
        payload = {
            "inventory": 8,
        }
        url = detail_url(book.id)
        response = self.client.patch(url, payload, format="multipart")
        book.refresh_from_db()
        response1 = self.client.get(BOOK_URL)
        book_list = Book.objects.all()
        serializer = BookSerializer(book_list, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response1.data[0], serializer.data[0])
        self.assertEqual(book_list[0].inventory, payload["inventory"])
