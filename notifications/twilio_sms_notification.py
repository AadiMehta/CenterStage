import logging
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)

NOT_CONFIGURED_MESSAGE = (
    "TWILIO_ACCOUNT_SID or TWILIO_AUTH_TOKEN or TWILIO_NUMBER missing."
)


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MessageClient(metaclass=Singleton):

    def __init__(self):
        logger.debug('Initializing messaging client')

        twilio_number = settings.TWILIO_NUMBER
        twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        twilio_auth_token = settings.TWILIO_AUTH_TOKEN

        if not all([twilio_account_sid, twilio_auth_token, twilio_number]):
            raise ImproperlyConfigured(NOT_CONFIGURED_MESSAGE)

        self.twilio_number = twilio_number
        self.twilio_client = Client(twilio_account_sid, twilio_auth_token)

        logger.debug('Twilio client initialized')

    def send_message(self, body, to):
        self.twilio_client.messages.create(
            body=body,
            to=to,
            from_=self.twilio_number,
        )

twilio = MessageClient()


