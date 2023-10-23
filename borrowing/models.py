import datetime
import decimal

# from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models


def tomorrow_date():
    return datetime.date.today() + datetime.timedelta(days=1)


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        "book.Book", on_delete=models.DO_NOTHING, related_name="borrowings"
    )
    user = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, related_name="borrowings"
    )
    penalty_for_delay = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    @property
    def is_active(self) -> bool:
        return self.actual_return_date is None

    # @property
    # def total_amount(self) -> int:
    #     total_amount = 100 * (
    #         self.actual_return_date - self.borrow_date
    #     ).days * self.book.daily_fee
    #     return int(total_amount)

    @property
    def total_amount(self) -> int:
        self.actual_return_date = datetime.date.today()
        total_amount = (
            100
            * (self.actual_return_date - self.borrow_date).days
            * self.book.daily_fee
        )
        if self.actual_return_date is not None and self.expected_return_date:
            if self.actual_return_date > self.expected_return_date:
                penalty_amount = 100 * (
                    (self.actual_return_date - self.expected_return_date).days
                    * self.book.daily_fee
                    * self.penalty_for_delay
                )
                total_amount += penalty_amount
        return int(total_amount)

    # def full_clean(self, exclude=None, validate_unique=True):
    #     if self.expected_return_date <= self.borrow_date:
    #         raise ValidationError({'expected_return_date': 'Expected return date must be greater than borrow date.'})
    #     if self.actual_return_date:
    #         if self.actual_return_date <= self.borrow_date:
    #             raise ValidationError({'actual_return_date': 'Expected return date must be greater than borrow date.'})
    #     super().full_clean()
    #
    # def save(
    #     self, force_insert=False, force_update=False, using=None, update_fields=None
    # ):
    #     self.full_clean()
    #     # self.book.inventory -= 1
    #     # self.book.save()
    #     return super(Borrowing, self).save(
    #         force_insert, force_update, using, update_fields
    #     )

    class Meta:
        ordering = [
            "user",
            "borrow_date",
        ]

    def __str__(self):
        return f"{self.book}, {self.borrow_date}({self.id})"


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = ("Pending",)
        PAID = "Paid"

    status = models.CharField(max_length=63, choices=StatusChoices.choices)
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(max_length=250, null=True, blank=True)
    session_id = models.CharField(max_length=10, null=True, blank=True)
    payment_amount = models.IntegerField(default=0)

    def __str__(self):
        return f"Payment #{self.id}: {self.status},borrowing {self.borrowing_id}"
