from datetime import datetime
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from config import Config

SCOPES = ['https://www.googleapis.com/auth/calendar.events']


class Event:
    @staticmethod
    def from_api_result(data: dict) -> "Event":
        event = Event()
        event.date = data['start']['date']
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

    def get_events(self):
        now = datetime.utcnow().isoformat() + 'Z'
        result = self.service.events().list(calendarId=self.id, timeMin=now, maxResults=10, singleEvents=True,
                                   orderBy='startTime').execute()
        for event in result['items']:
            yield Event.from_api_result(event)
