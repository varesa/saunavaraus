import json
import textwrap
import requests
from reservation_request import ReservationRequest
from config import Config


def format_notification(reservation: ReservationRequest) -> str:
    return textwrap.dedent(f"""
    Date: {reservation.date.isoformat()}
    Guests: {reservation.num_guests}
    ----
    """) + reservation.message


def send_notification(reservation: ReservationRequest, event_id: str, config: Config):
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
                            "callback_data": json.dumps({
                                "action": "accept",
                                "id": event_id,
                            })
                        }
                    ],
                    [
                        {
                            "text": "❌Decline",
                            "callback_data": json.dumps({
                                "action": "decline",
                                "id": event_id,
                            })
                        },
                    ]
                ]
            }
        })

    if response.status_code != 200:
        raise Exception(response.text)
