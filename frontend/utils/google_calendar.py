import logging

import google.oauth2.credentials
import googleapiclient.discovery

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GoogleCalendar(metaclass=Singleton):
    def __init__(self, creds):
        credentials = google.oauth2.credentials.Credentials(**creds)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    def create_calendar_invite(
            self,
            lesson,
            lesson_from,
            lesson_to,
            session_no,
            emails=[]
        ):
        # Reference: https://developers.google.com/calendar/v3/reference/events
        try:
            if not len(emails):
                return
            attendees = []
            for email in emails:
                attendees.append({'email': email})
            formatted_lesson_from = lesson_from.isoformat()
            formatted_lesson_to = lesson_to.isoformat()
            event = {
                'summary': 'CS-{}: {}'.format(session_no, lesson.name),
                'description': lesson.description,
                'start': {
                    'dateTime': formatted_lesson_from,
                    'timeZone': lesson.timezone or 'Asia/Kolkata',
                }, 
                'end': {
                    'dateTime': formatted_lesson_to,
                    'timeZone': lesson.timezone or 'Asia/Kolkata',
                },
                'attendees': attendees,
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            invite_info = self.service.events().insert(calendarId='primary', body=event).execute()
            return invite_info
        except Exception as e:
            logger.exception(e)
