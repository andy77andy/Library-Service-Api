from datetime import date, timedelta

from celery import shared_task

from borrowing.bot import send_telegram_notification
from borrowing.models import Borrowing


@shared_task
def overdue_borrowings_task() -> None:
    today = date.today()
    tomorrow = today + timedelta(days=1)

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=tomorrow, actual_return_date=None
    )

    for borrowing in overdue_borrowings:
        message = (
            f"Overdue borrowing:\n"
            f"User: {borrowing.user.email}\n"
            f"Book: {borrowing.book.title}"
        )
        send_telegram_notification(message)
