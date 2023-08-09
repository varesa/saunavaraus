#!/usr/bin/env python3

from flask import Flask, request

from telegram import send_notification
from config import Config
from gcalendar import Calendar
from reservation_request import ReservationRequest, InvalidReservationException
from state import State

app = Flask(__name__)
config = Config.load()
calendar = Calendar.login(config)


def html_response(content: str) -> str:
    return f"""
    <html>
        <body>
            {content}
            <br>
            <a href="/">Palaa lomakkeeseen / Return to the form</a>
        <body>
    </html>
    """


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/post", methods=['POST'])
def post():
    try:
        reservation = ReservationRequest.from_formdata(request.form)
        state = State(email=reservation.email)
        event_id = calendar.try_add(reservation.date, reservation.header, reservation.details_as_text, state)
        if not event_id:
            return html_response(f"""
                <p>Varauspyyntöäsi ei voitu vahvistaa. On mahdollista että valitsemasi päivä on jo varattu - tarkistathan tämän varauskalenterista</p>
                <p>We were unable to confirm your reservation. It is possible that the date you selected has already been reserved. Please check this from the reservation calendar</p>
            """)
        send_notification(reservation, event_id, config)
    except InvalidReservationException as e:
        return html_response(f"""
            <p>Varauspyyntösi hylättiin / Your reservation request was rejected due to: <br>
            {e.args[0]}
        """)
    except Exception as e:
        print(e)
        return html_response(f"""
                <p>Something went wrong. If this repeats, please contact the 
                tenant committee at astmk@pirkat.net or ask in the Telegram group
        """)

    return html_response("""
        <p>Varauspyyntösi on otettu vastaan ja se on asukastoimikunnalla vahvistettavana.</p>
        <p>Your reservation has been received and it is waiting for confirmation from the tenant commitee.</p>
    """)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=54433)
