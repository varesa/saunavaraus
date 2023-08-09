from datetime import date, timedelta
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import Config
from typing import Iterator

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


class Event:
    date: date = None

    def __repr__(self):
        return f"<Event on {self.date}>"

    @staticmethod
    def from_api_result(data: dict) -> "Event":
        event = Event()

        event.date = date.fromisoformat(data['start']['date'])
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
        now = date.today().isoformat() + 'T00:00:00Z'
        result = self.service.events().list(calendarId=self.id, timeMin=now, maxResults=365, singleEvents=True,
                                   orderBy='startTime').execute()
        for event in result['items']:
            yield Event.from_api_result(event)

    def is_free(self, date: date) -> bool:
        events = self.get_events()
        for event in events:
            if event.date == date:
                return False
        return True

    def try_add(self, event_date: date, header: str, details: str) -> bool:
        if not self.is_free(event_date):
            return False

        event = {
            'summary': header,
            'description': details,
            'start': {
                'date': event_date.isoformat()
            },
            'end': {
                'date': (event_date + timedelta(days=1)).isoformat()
            }
        }
        print(event)

        result = self.service.events().insert(calendarId=self.id, body=event).execute()
        assert result['status'] == 'confirmed'
        return True
