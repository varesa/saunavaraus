#!/usr/bin/env python3

from flask import Flask, request
import requests
import textwrap

from config import Config
from gcalendar import Calendar
from reservation_request import ReservationRequest, InvalidReservationException

app = Flask(__name__)
config = Config.load()
calendar = Calendar.login(config)


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
            "chat_id": config['chat_id'],
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


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/post", methods=['POST'])
def post():
    try:
        reservation = ReservationRequest.from_formdata(request.form)
    except InvalidReservationException as e:
        return f"""
        <html>
            <body>
                <p>Varauspyyntösi hylättiin / Your reservation request was rejected due to: <br>
                {e.args[0]}
                <br>
                <a href="/">Palaa lomakkeeseen / Return to the form</a>
            <body>
        </html>
        """
    except Exception as e:
        print(e)
        return f"""
        <html>
            <body>
                <p>Something went wrong. If this repeats, please contact the 
                tenant committee at astmk@pirkat.net or ask in the Telegram group
                <br>
                <a href="/">Palaa lomakkeeseen / Return to the form</a>
            <body>
        </html>
        """


    send_notification(reservation)
    return "OK"


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=54433)
