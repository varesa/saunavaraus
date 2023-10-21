
from telegram import get_callbacks
from config import Config
from gcalendar import Calendar
import smtplib
import time
import textwrap

config = Config.load()
calendar = Calendar.login(config)


def send_email(recipient: str, config: Config):
    message = textwrap.dedent(f"""\
        From: {config.email_address}
        To: {recipient}
        Subject: Kattosaunan varauksen vahvistus / Rooftop sauna confirmation
        
        Moi, onnistuu...
    """)
    server = smtplib.SMTP('localhost', 25)
    server.ehlo('localhost')

    server.sendmail(config.email_address, recipient, message)
    server.quit()


while True:
    for callback in get_callbacks(config):
        event_action = callback.data['action']
        event_id = callback.data['id']

        event = calendar.get_by_id(event_id)
        reservation_email = event.get_state().email

        # TODO: Notify user
        if event_action == 'decline':
            calendar.delete(event)
            status = f"Hylännyt {callback.date_formatted} {callback.user_name}. Lähetä viestiä <<TODO>>"
        elif event_action == 'accept':
            calendar.confirm(event)
            send_email(reservation_email, config)
            status = f"Hyväksynyt {callback.date_formatted} {callback.user_name}"
        else:
            raise Exception(f"Unknown action {event_action}")

        callback.answer()
        callback.append_text(status)
    time.sleep(5)
