from datetime import datetime, timedelta
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import Config
from typing import Iterator

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
DATE_FORMAT = '%Y-%m-%d'


class Event:
    date: datetime = None

    def __repr__(self):
        return f"<Event on {self.date}>"

    @staticmethod
    def from_api_result(data: dict) -> "Event":
        event = Event()
        event.date = datetime.strptime(data['start']['date'], DATE_FORMAT)
        return event


class Calendar:
    service = None
    id = ""

    @staticmethod
    def login(config: Config) -> "Calendar":
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(config.google_account, SCOPES)
        service = build('calendar', 'v3', credentials=credentials)

        calendar = Calendar()
        calendar.service = service
        calendar.id = config.calendar_id
        return calendar

    def get_events(self) -> Iterator[Event]:
        now = datetime.utcnow().isoformat() + 'Z'
        result = self.service.events().list(calendarId=self.id, timeMin=now, maxResults=365, singleEvents=True,
                                   orderBy='startTime').execute()
        for event in result['items']:
            yield Event.from_api_result(event)

    def is_free(self, date: datetime) -> bool:
        events = self.get_events()
        for event in events:
            if event.date == date:
                return False
        return True

    def try_add(self, date: datetime, header: str, details: str) -> bool:
        if not self.is_free(date):
            return False

        event = {
            'summary': header,
            'description': details,
            'start': {
                'date': date.strftime(DATE_FORMAT)
            },
            'end': {
                'date': (date + timedelta(days=1)).strftime(DATE_FORMAT)
            }
        }

        result = self.service.events().insert(calendarId=self.id, body=event).execute()
        assert result['status'] == 'confirmed'
        return True
