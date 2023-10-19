import datetime

from django.db import transaction
from rest_framework import serializers

from borrowing.bot import send_telegram_notification
from borrowing.models import Borrowing, Payment


class BorrowingSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "is_active",
            "penalty_for_delay",
        )

    def get_is_active(self, obj):
        return obj.is_active


class BorrowingDetailSerializer(serializers.ModelSerializer):
    is_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_active",
            "penalty_for_delay",
        )

    def get_is_active(self, obj):
        return obj.is_active


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "user",
            "borrow_date",
            "expected_return_date",
            "penalty_for_delay",
        )
        read_only_fields = ("id", "borrow_date", "actual_return_date", "user")

    def validate_book(self, book):
        if book.inventory == 0:
            raise serializers.ValidationError("Book is not available for borrowing.")
        return book

    def validate_user(self, user):
        user = self.context["request"].user
        payments = Payment.objects.filter(borrowing__user=user, status="Pending")
        if payments > 0:
            raise serializers.ValidationError(
                "Sorry, firstly you have to performed your existed payments"
            )
        return user

    def validate(self, attrs):
        if datetime.date.today() >= attrs["expected_return_date"]:
            raise serializers.ValidationError("Change expected_return_date")
        return attrs

    @transaction.atomic
    def create(self, validated_data) -> Borrowing:
        borrowing = Borrowing.objects.create(**validated_data)
        book = self.validated_data["book"]
        book.inventory -= 1
        book.save()
        message = (
            f"New borrowing: {book.title}, "
            f"borrow_date: {borrowing.borrow_date}"
            f"expected_return_date: {borrowing.expected_return_date}"
        )
        send_telegram_notification(message)
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("actual_return_date",)
        read_only_fields = ("actual_return_date",)
