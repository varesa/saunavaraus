from datetime import date
from telegram import get_callbacks
from config import Config
from gcalendar import Calendar
import smtplib
import time
import textwrap

config = Config.load()
calendar = Calendar.login(config)


def send_email(recipient: str, event_date: date, config: Config):
    date_formatted = event_date.strftime("%d.%m.%Y")
    message = textwrap.dedent(f"""\
        From: {config.email_address}
        To: {recipient}
        Subject: Kattosaunan varauksen vahvistus / Rooftop sauna confirmation {date_formatted}

        <in English below>

        Moi!

        Kattosauna on nyt varattu sinulle {date_formatted}.

        Kertaa kattosaunan tilojen käytön siivousohjeet ja säännöt.
        https://www.pirkat.net/wp-content/uploads/2022/12/KATTOSAUNAN-Siivousohjeet-1.docx
        https://www.pirkat.net/wp-content/uploads/2022/12/KATTOSAUNAN-Saannot-1-1.docx

        Muista varauksen alussa ja lopussa täyttää checkin/checkout, tällöin
        et ole esimerkiksi vastuussa edellisen varaajan aiheuttamista
        vahingoista:

        https://www.pirkat.net/saunacheck

         Sovithan avaimen lainasta vähintään päivää etukäteen.
         Avainten haltijoiden puhelinnumerot löydät:
         - www.kodinportaali.fi -sivulta
         - Telegram ryhmästä -> ryhmän jäsenet -> nimien vieressä“ASTMK P4 av”
         - Ilmoitustaululta (kosketusnäyttö rappukäytävällä)


        Varaus alkaa klo 12 ja päättyy seuraavana päivänä klo 12. Hiljaisuuden
        alkaessa on poistuttava kattosaunan tiloista:
        pe-la klo 23 ja su-to klo 22.

        Muistathan että sauna on laitettava itse päälle! Kytke kiuas päälle
        oleskelutilan seinällä (ovipuhelimen yllä, ilmanvaihto-säätimen alla)
        olevasta ajastimesta paikalle saapuessasi. Kiukaalle pitää laittaa
        heti tarpeeksi aikaa, eli sen voi kytkeä päälle vain kerran illassa,
        seuraavan kerran vasta seuraavana päivänä. Säädä kiukaan lämpö
        sopivaksi itse kiukaasta. Ajastimesta myös tilan sisäänkäynnin oven
        sähkölukko aukeaa. Vaikka ajastimessa olisi aikaa, kiuasta voi
        lämmittää klo 15.30-23.00 välillä enintään 6 tuntia.

        Huolehdithan tilan hyvästä siivouksesta, elektroniikan ja
        valojen sammuttamisesta sekä ovien ja ikkunoiden lukitsemisesta.

        Palauta avain ajoissa ja ilmoita ohjeiden mukaisesti kattosaunan
        puutoksista ja näkemästäsi vahingosta tarvittaessa.

        Kattosaunan ovipuhelin: 133
        Wifi: Kattosauna (salasana: LoylyKauha4)

        Kaikki tarvittavat ohjeet ja säännöt kattosaunan käytöstä
        löydät www.pirkat.net -sivustolta

        Nauti tiloista ja mukavia hetkiä tapahtumaasi! :)

        Terv. Pirkat asukastoimikunta (astmk@pirkat.net)

        <TODO: English version>
    """)
    server = smtplib.SMTP('localhost', 25)
    server.ehlo('localhost')

    server.sendmail(config.email_address, recipient, message.encode())
    server.quit()


while True:
    for callback in get_callbacks(config):
        event_action = callback.data['action']
        event_id = callback.data['id']

        event = calendar.get_by_id(event_id)
        reservation_email = event.get_state().email

        if event_action == 'decline':
            calendar.delete(event)
            status = f"Hylännyt {callback.date_formatted} " + \
                f"{callback.user_name}. Ilmoita hylkäämisestä " + \
                f"itse osoitteeseen {reservation_email}"
        elif event_action == 'accept':
            calendar.confirm(event)
            send_email(reservation_email, event.date, config)
            status = f"Hyväksynyt {callback.date_formatted} " + \
                f"{callback.user_name}"
        else:
            raise Exception(f"Unknown action {event_action}")

        callback.answer()
        callback.append_text(status)
    time.sleep(5)
