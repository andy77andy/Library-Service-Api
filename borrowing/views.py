import datetime
import os

import stripe
from django.core.exceptions import ValidationError
from django.db import transaction
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from borrowing.models import Borrowing, Payment
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer,
    PaymentSerializer,
)
from borrowing.session import CreateSession
from permissions import IsAdminOrReadOnly

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related(
        "book", "user"
    )
    permission_classes = [IsAuthenticated]
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, borrow_date=datetime.date.today())

    @action(
        methods=["POST"],
        detail=True,
        url_name="return",
        url_path="return",
        permission_classes=[
            IsAdminOrReadOnly,
        ],
    )
    @transaction.atomic
    def return_book(self, request, pk=None):
        with transaction.atomic():
            borrowing_returned = Borrowing.objects.get(pk=pk)
            if not borrowing_returned.is_active:
                raise ValidationError({"message": "This borrowing is closed already"})
            borrowing_returned.actual_return_date = datetime.date.today()
            serializer = self.get_serializer_class()(
                borrowing_returned,
                data={"actual_return_date": datetime.date.today()},
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            book = borrowing_returned.book
            book.inventory += 1
            book.save()
            session = CreateSession.create_session(borrowing=borrowing_returned)
            return Response(
                {"message": "Book was successfully returned"}, status=status.HTTP_200_OK
            )

    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")

        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date=None)
            else:
                queryset = queryset.exclude(actual_return_date=None)

        if self.request.user.is_staff:
            if user_id:
                queryset = queryset.filter(user__id=user_id)

            return queryset

        return queryset.filter(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "is_active",
                type=OpenApiTypes.BOOL,
                description="Filter by borrowing's status (ex. ?is_active=true)",
            ),
            OpenApiParameter(
                "user_id",
                type=OpenApiTypes.INT,
                description="Filter by user_id, available only for admin (ex. ?user_id=4)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        this method is created for documentation, to use extend_schema
        for filtering
        """
        return super().list(self, request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action in ("retrieve", "update"):
            return BorrowingDetailSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingSerializer


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Payment.objects.all()
    permission_classes = [
        IsAuthenticated,
    ]
    serializer_class = PaymentSerializer

    @action(
        methods=["GET"],
        detail=False,
        url_path="success",
        url_name="success",
    )
    def success_payment(self, request, pk=None):
        """Change payment status for success"""
        session_id = self.request.query_params.get("session_id")
        payment = Payment.objects.filter(session_id=session_id)
        serializer = PaymentSerializer(payment, data={"status": "PAID"}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": "Payment was successfully performed"}, status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=["GET"],
        url_path="cancel",
        url_name="cancel",
    )
    def payment_cancel(self, request):
        return Response(
            {"message": "Oops, something went wrong, try again later"},
            status=status.HTTP_200_OK,
        )
