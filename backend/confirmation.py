
from telegram import get_callbacks
from config import Config
from gcalendar import Calendar
import smtplib

config = Config.load()
calendar = Calendar.login(config)


def send_email(recipient: str, config: Config):
    server = smtplib.SMTP('localhost', 2500)
    server.ehlo('localhost')
    server.sendmail(config.email_address, recipient, "Your sauna reservation has been accepted")
    server.quit()


for callback in get_callbacks(config):
    print(callback)
    event_action = callback.data['action']
    event_id = callback.data['id']

    event = calendar.get_by_id(event_id)
    reservation_email = event.get_sate().email

    # TODO: Notify user
    if event_action == 'decline':
        calendar.delete(event)
    elif event_action == 'accept':
        calendar.confirm(event)
        send_email(reservation_email)
    else:
        raise Exception(f"Unknown action {event_action}")
