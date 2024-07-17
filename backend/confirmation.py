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
        - https://www.kodinportaali.fi -sivulta
        - Telegram ryhmästä (https://pirkat.net/tg)
          -> ryhmän jäsenet -> nimien vieressä “ASTMK P4 av”
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

        ---------------------

        Hi!

        The rooftop sauna has been reserved for you on {date_formatted}.

        Please remind yourself of the rules and cleaning instructions
        as you are responsible for the venue during your reservation:

        Rules: https://docs.google.com/document/d/1k9xfenMVP0mkO11tOJLTNr7vKzplAs-qOTaSjYeb__A
        Cleaning instructions: https://docs.google.com/document/d/10ZCeyDOW6q_6qXfjbAjMIL9u-s61Uor-FBdJIr96ZBA

        At the beginning and end of your reservation please fill the
        checkin/checkout forms, as that way you won't be held liable
        for any damage which may have occurred before your reservation:

        https://www.pirkat.net/saunacheck

        Remember to arrange a time to pick up the key from a tenant commitee
        member *at least a day* in advance. Contact information for
        members who hold a key can be found at:
        - https://www.kodinportaali.fi webpage
        - The telegram group (https://pirkat.net/tg)
          -> group members -> "ASTMK p4 av" label next to name
        - The notice board (touch screen at the building entrance)

        Your booking begins at 12.00 (noon) and ends on the following day
        at 12.00. As silence begins in our buildings, you must leave the
        rooftop sauna: Fri-Sat at 23.00 pm and  Sun-Thu at 22.00.

        Remember to turn on the sauna yourself! Turn on the sauna stove
        from the lounge room wall timer (above the door phone, below the
        AC timer screw) on your left as you enter the lounge. You can set
        the sauna to heat only once a day so it is best to set enough time
        on the timer at once. There is also a power adjustment below the
        stove in the sauna, you can use it to adjust the temperature to
        your preference. Turning the sauna timer on also unlocks the venue
        door leading to the hallway. Even if the timer has time remaining,
        the sauna can only be heated between 15.30-23.00 and at most for
        6 hours per day.

        Make sure the venue is cleaned properly and according to the cleaning
        instructions, all electronics and lights have been turned off, and all
        doors and windows are locked after you leave.

        Return the key to its holder as soon as possible and inform the
        tenant committee of any damages or deficiencies from what is stated
        in the cleaning instructions or rules.

        Rooftop sauna door phone: 133

        Wifi: Kattosauna (password: LoylyKauha4)

        All instructions, rules, and further information is available on
        our website: https://www.pirkat.net


        Enjoy your time at the rooftop sauna!

        Regards, the Pirkat tenant committee (astmk@pirkat.net)
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

        date_now = date.today().isoformat()

        if event_action == 'decline':
            calendar.delete(event)
            status = f"Hylännyt {date_now} " + \
                f"{callback.user_name}. Ilmoita hylkäämisestä " + \
                f"itse osoitteeseen {reservation_email}"
        elif event_action == 'accept':
            calendar.confirm(event)
            send_email(reservation_email, event.date, config)
            status = f"Hyväksynyt {date_now} " + \
                f"{callback.user_name}"
        else:
            raise Exception(f"Unknown action {event_action}")

        callback.answer()
        callback.append_text(status)
    time.sleep(5)
