#!/usr/bin/env python3

from flask import Flask, request
import json
import requests
import textwrap
import sys
import os


class Config:
    # Telegram bot token and chat id
    bot_token: str = ""
    chat_id: str = ""

    @staticmethod
    def find_file() -> str:
        """
        Try to find the path to the config file. Prefers command line
        argument and defaults to './config.json' if argument is not given.
        Checks that a file exists at the given path and aborts the program otherwise.
        """
        if len(sys.argv) == 2:
            config_path = sys.argv[2]
        else:
            config_path = './config.json'

        if not os.path.isfile(config_path):
            print(textwrap.dedent(f"""\
                Error: Could not find config file. Defaults to config.json in working directory.

                Usage: {sys.argv[0]} [config_path]
            """))
            sys.exit(1)

        return config_path

    def is_valid(self) -> bool:
        """
        Checks that the config object contains the necessary keys.
        """
        valid = True

        # Check all the type annotated properties of the Config class
        for key in Config.__annotations__.keys():
            if not self.__dict__.get(key):
                print(f"Error: '{key}' not present in config file")
                valid = False

        return valid

    @staticmethod
    def load() -> "Config":
        config_path = Config.find_file()

        config = Config()
        with open(config_path, 'r') as f:
            j: dict = json.load(f)
            for key, value in j.items():
                setattr(config, key, value)

        if not config.is_valid():
            print("Error: Config file failed validation")
            sys.exit(1)

        return config


app = Flask(__name__)
config = Config.load()


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
    app.run(host='0.0.0.0', port=54433)
