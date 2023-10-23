import datetime
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from book.models import Book
from book.serializers import BookSerializer
from borrowing.models import Borrowing, Payment
from borrowing.serializers import BorrowingSerializer, BorrowingReturnSerializer

BORROWING_URL = reverse("borrowing:borrowing-list")
PAYMENT_URL = reverse("borrowing:borrowing-list")


def detail_url(borrowing_id: int):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id: int):
    return reverse("borrowing:borrowing-return", args=[borrowing_id])


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


# def sample_user(**params):
#     defaults = {
#         "email": "test@test.com",
#         "password": "test123456",
#     }
#     defaults.update(params)
#
#     return get_user_model().objects.create_user(**defaults)
#
def sample_borrowing(**params):
    defaults = {
        "borrow_date": date.today(),
        "expected_return_date": date.today() + timedelta(days=10),
        "book": sample_book(),
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


class UnauthenticatedUserTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_forbidden_unauthl(self) -> None:
        response = self.client.get(BORROWING_URL)
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test1.com",
            "test1234",
        )
        self.client.force_authenticate(self.user)
        admin = get_user_model().objects.create_user(
            "admin@test.com", "test1234", is_staff=True
        )
        user1 = get_user_model().objects.create_user(
            "test@test2.com",
            "test1234",
        )
        book = Book.objects.create(
            title="test", author="test", cover="SOFT", inventory=10, daily_fee="1.00"
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + timedelta(5),
            book=book,
            user=user1,
        )
        self.borrowing2 = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + timedelta(5),
            book=book,
            user=self.user,
            # actual_return=datetime.date(2023, 10, 10),
        )
        self.borrowing3 = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + timedelta(5),
            book=book,
            user=admin,
            # actual_return=datetime.date(2023, 10, 10),
        )

    def test_list_borrowings(self):
        res = self.client.get(BORROWING_URL)
        serializer = BorrowingSerializer(Borrowing.objects.filter(user_id=1), many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn(Borrowing.objects.filter(user_id=3), res.data)
        self.assertEqual(res.data, serializer.data)

    def test_create_borrowing(self) -> None:
        book1 = Book.objects.create(
            title="test", author="test", cover="SOFT", inventory=10, daily_fee="1.00"
        )
        payload = {
            "expected_return_date": datetime.date.today() + timedelta(5),
            "book": 2,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_decrease_book_inventory_while_borrowing(self) -> None:
        book1 = Book.objects.create(
            title="test", author="test", cover="SOFT", inventory=10, daily_fee="1.00"
        )
        payload = {
            "expected_return_date": datetime.date.today() + timedelta(5),
            "book": 2,
        }
        response = self.client.post(BORROWING_URL, payload)
        book1.refresh_from_db()
        self.assertEqual(book1.inventory, 9)

    def test_unable_create_with_unavailable_book(self) -> None:
        book = Book.objects.create(
            title="test", author="test", cover="SOFT", inventory=0, daily_fee="1.00"
        )
        payload = {
            "expected_return_date": datetime.date.today() + timedelta(5),
            "book": 2,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["book"][0], "Book is not available for borrowing."
        )

    def test_unable_create_wrong_expected_date(self) -> None:
        payload = {
            "expected_return_date": datetime.date.today() - timedelta(5),
            "book": 1,
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"][0], "Change expected_return_date"
        )


class AdminBorrowingTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test1.com", "test1234", is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(
            title="test", author="test", cover="HARD", inventory=10, daily_fee="1.00"
        )
        self.borrowing = Borrowing.objects.create(
            borrow_date=datetime.date.today(),
            expected_return_date=datetime.date.today() + timedelta(5),
            book=self.book,
            user=self.user,
        )

    def test_filter_borrowings(self):
        response = self.client.get(BORROWING_URL)
        serializer = BorrowingSerializer(Borrowing.objects.all(), many=True)
        self.assertEqual(response.data, serializer.data)
        response2 = self.client.get(BORROWING_URL, {"user_id": 2})
        serializer3 = BorrowingSerializer(
            Borrowing.objects.filter(user_id=2), many=True
        )
        self.assertEqual(response2.data, serializer3.data)

    def test_return_borrowings(self):
        url = return_url(borrowing_id=self.borrowing.id)
        response = self.client.post(url)
        self.borrowing.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.borrowing.actual_return_date, datetime.date.today())

    def test_create_payment_while_return(self):
        url = return_url(borrowing_id=self.borrowing.id)
        response = self.client.post(url)
        self.borrowing.refresh_from_db()
        payment = Payment.objects.last()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(payment.borrowing_id, self.borrowing.id)

    def test_book_inventory_after_return(self):
        url = return_url(borrowing_id=self.borrowing.id)
        response = self.client.post(url)
        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.book.inventory, 11)
