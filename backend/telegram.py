import textwrap

import requests

from backend.incoming import config
from backend.reservation_request import ReservationRequest


def format_notification(reservation: ReservationRequest) -> str:
    return textwrap.dedent(f"""
    Date: {reservation.date.isoformat()}
    Guests: {reservation.num_guests}
    ----
    """) + reservation.message


def send_notification(reservation: ReservationRequest):
    response = requests.post(
        f"https://api.telegram.org/bot{config.bot_token}/sendMessage",
        json={
            "chat_id": config.chat_id,
            "text": format_notification(reservation),
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {
                            "text": "✅Accept",
                            "callback_data": "accept"
                        }
                    ],
                    [
                        {
                            "text": "❌Decline",
                            "callback_data": "decline"
                        },
                    ]
                ]
            }
        })

    if response.status_code != 200:
        raise Exception(response.text)
