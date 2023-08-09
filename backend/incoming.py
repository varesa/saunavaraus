#!/usr/bin/env python3

from flask import Flask, request
import requests
import textwrap

from config import Config
from gcalendar import Calendar

app = Flask(__name__)
config = Config.load()
calendar = Calendar.login(config)
print(list(calendar.get_events()))


def format_notification(data):
    return textwrap.dedent(f"""
    Date: {data['date']}
    Guests: {data['numGuests']}
    ----
    """) + data['message']


def send_notification(data):
    response = requests.post(
        f"https://api.telegram.org/bot{config.bot_token}/sendMessage",
        json={
            "chat_id": config['chat_id'],
            "text": format_notification(data),
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
    send_notification(request.form)
    return "OK"


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=54433)
