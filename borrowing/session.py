import os

import stripe

from borrowing.models import Borrowing, Payment
from library_service import settings
from dotenv import load_dotenv

load_dotenv()
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
HOST = "http://127.0.0.1:8000"
SECRET_API_KEY = settings.STRIPE_SECRET_KEY


class CreateSession:
    @staticmethod
    def create_session(borrowing: Borrowing) -> None:
        stripe.api_key = STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": borrowing.book.title,
                        },
                        "unit_amount": borrowing.total_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=HOST + "/api/payments/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=HOST + "/api/payments/cancel/?session_id={CHECKOUT_SESSION_ID}",
        )
        payment = Payment.objects.create(
            status="IN_PROCESS",
            borrowing=borrowing,
            session_id=session.id,
            session_url=session.url,
            payment_amount=borrowing.total_amount,
        )
        payment.session_url = session.url
        payment.session_id = session.id
        payment.save()
