from datetime import date, timedelta
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import Config
from typing import Iterator, Optional
from state import State

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


class EventNotFoundException(Exception):
    pass


class Event:
    id: str = ""
    date: date = None

    summary: str = ""
    description: str = ""

    def __repr__(self):
        return f"<Event {self.id} on {self.date}>"

    @staticmethod
    def from_api_result(data: dict) -> "Event":
        event = Event()

        event.id = data['id']
        if 'date' in data['start'].keys():
            event.date = date.fromisoformat(data['start']['date'])
        else:
            event_date, _ = data['start']['dateTime'].split('T')
            event.date = date.fromisoformat(event_date)
        event.summary = data.get('summary', None)
        event.description = data.get('description', None)

        return event

    def get_state(self):
        """
        Attempt to get the state from the event message. Bubbles up StateMissingException on failure.
        """
        return State.from_str(self.description)


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

    def try_add(self, event_date: date, header: str, details: str, state: State) -> Optional[str]:
        if not self.is_free(event_date):
            return None

        event = {
            'summary': header,
            'description': details + '\n\n' + state.encode(),
            'start': {
                'date': event_date.isoformat()
            },
            'end': {
                'date': (event_date + timedelta(days=1)).isoformat()
            }
        }

        result = self.service.events().insert(calendarId=self.id, body=event).execute()
        assert result['status'] == 'confirmed'
        return result['id']

    def get_by_id(self, event_id: str) -> Event:
        result = self.service.events().get(calendarId=self.id, eventId=event_id).execute()
        return Event.from_api_result(result)

    def delete(self, event: Event):
        print(f"Deleting {event}")
        self.service.events().delete(calendarId=self.id, eventId=event.id).execute()

    def confirm(self, event: Event):
        print(f"Confirming {event}")
        patch = {
            "summary": event.summary.replace("VAHVISTAMATON ", "")
        }
        result = self.service.events().patch(calendarId=self.id, eventId=event.id, body=patch).execute()
        print(result)

