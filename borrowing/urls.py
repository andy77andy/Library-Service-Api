from django.urls import path, include
from rest_framework import routers

from book.views import BookViewSet
from borrowing.views import BorrowingViewSet, PaymentViewSet

router = routers.DefaultRouter()
router.register("borrowings", BorrowingViewSet)
router.register("payments", PaymentViewSet)

urlpatterns = router.urls

app_name = "borrowing"
