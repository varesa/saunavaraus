#!/usr/bin/env python3

from flask import Flask, request
import json
import requests
import textwrap


app = Flask(__name__)

with open('config.json', 'r') as f:
    config = json.load(f)


def format_notification(data):
    return textwrap.dedent(f"""
    Date: {data['date']}
    Guests: {data['numGuests']}
    ----
    """) + data['message']


def send_notification(data):
    response = requests.post(
        f"https://api.telegram.org/bot{config['bot_token']}/sendMessage",
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
    app.run(host='0.0.0.0', port=54433)
