import json
import textwrap
import requests
from requests import Session
from requests.adapters import HTTPAdapter
import datetime
from urllib3.util import Retry
from typing import Optional, Iterable

from reservation_request import ReservationRequest
from config import Config


session = Session()
retries = Retry(
    total=10,
    backoff_factor=0.2,
)
session.mount('https://', HTTPAdapter(max_retries=retries))


class CallbackAction:
    raw: dict = {}
    data: dict = {}

    def __init__(self, update: dict, config: Config):
        self.config = config
        self.raw = update
        self.data = json.loads(update['callback_query']['data'])

    def answer(self):
        response = session.post(
            f"https://api.telegram.org/bot{self.config.bot_token}/answerCallbackQuery",
            json={
                "callback_query_id": self.raw['callback_query']['id']
            },
            timeout=(2, 10))

        if response.status_code != 200:
            raise Exception(response.text)

    def append_text(self, text: str):
        chat_id = self.raw['callback_query']['message']['chat']['id']
        message_id = self.raw['callback_query']['message']['message_id']
        new_text = self.raw['callback_query']['message']['text'] + '\n\n' + text

        response = session.post(
            f"https://api.telegram.org/bot{self.config.bot_token}/editMessageText",
            json={
                "chat_id": chat_id,
                "message_id": message_id,
                "text": new_text,
            },
            timeout=(2, 10))

        if response.status_code != 200:
            raise Exception(response.text)

    @property
    def date_formatted(self):
        return (datetime.datetime.fromtimestamp(int(self.raw['callback_query']['message']['date']))
                .strftime("%Y-%m-%d %H:%M"))

    @property
    def user_name(self):
        return (self.raw['callback_query']['from'].get('username', '')
                or self.raw['callback_query']['from'].get('first_name', '')
                or "unknown")


def format_notification(reservation: ReservationRequest) -> str:
    return textwrap.dedent(f"""
    Date: {reservation.date.isoformat()}
    Guests: {reservation.num_guests}

    By: {reservation.name} ({reservation.address})
    Contact: {reservation.email} / {reservation.phone}
    ----
    """) + reservation.message


def send_notification(reservation: ReservationRequest, event_id: str, config: Config):
    response = session.post(
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
        },
        timeout=(2, 10))

    if response.status_code != 200:
        raise Exception(response.text)


last_update = None


def get_callbacks(config: Config) -> Iterable[CallbackAction]:
    global last_update
    params = {"timeout": 30}
    if last_update:
        params['offset'] = last_update + 1
    print("getting updates")
    response = session.post(
        f"https://api.telegram.org/bot{config.bot_token}/getUpdates", 
        json=params,
        timeout=(2, 45))
    print("got updates")

    if response.status_code != 200:
        raise Exception(response.text)

    for event in response.json()['result']:
        last_update = event['update_id']
        if 'callback_query' not in event.keys():
            continue
        yield CallbackAction(event, config)
