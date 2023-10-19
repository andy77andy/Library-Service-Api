from django.contrib import admin

from borrowing.models import Borrowing
from payment.models import Payment


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass
