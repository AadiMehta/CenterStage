import json
import logging

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from users.utils.helpers import generate_jwt

logger = logging.getLogger(__name__)

NOT_CONFIGURED_MESSAGE = (
    "ZOOM_CLIENT_ID or ZOOM_CLIENT_SECRET missing. Are you sure, you have .env file configured?"
)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ZoomClient(metaclass=Singleton):

    def __init__(self, code):
        logger.debug('Initializing zoom client')

        if not all([client_id, client_secret]):
            raise ImproperlyConfigured(NOT_CONFIGURED_MESSAGE)

        self.base_url = 'https://api.zoom.us/v2'
        self.oauth_url = 'https://zoom.us/oauth/token'
        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.token = generate_jwt(client_id, client_secret)

        self.get_access_token(code)

        logger.debug('Zoom client initialized')

    def get_access_token(self, code):
        headers = {
            "Authorization": "Basic {}".format(self.config.get("token")),
            "Content-Type": "application/json",
        }
        url = "{}?grant_type=authorization_code&code={}&redirect_uri={}".format(
                        self.oauth_url, code,
                        settings.ZOOM_REDIRECT_URL
                    )
        resp = requests.post(
            url,
            headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')

    def refresh_access_token(self):
        headers = {
            "Authorization": "Basic {}".format(self.config.get("token")),
            "Content-Type": "application/json",
        }
        url = "{}?grant_type=refresh_token&refresh_token={}".format(
                        self.oauth_url, self.refresh_token
                    )
        resp = requests.post(
            url,
            headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            self.access_token = data.get('access_token')
            self.refresh_token = data.get('refresh_token')

    def get_user_details(self, access_token):
        headers = {
            "Authorization": "Bearer {}".format(access_token)),
            "Content-Type": "application/json",
        }
        url = "{}/meeting/create".format(self.base_url)
        return requests.get(
            url,
            headers=headers
        )

    def create_meeting(self, 
            host_id: str, topic: str, start_time: str, type: int = 2,
            agenda: str='', timezone: str = 'Asia/Calcutta',
            duration: int = 30, password: str = None
        ) -> None:
        params = dict(
            host_id=host_id, topic=topic,
            type=type, start_time=start_time,
        )
        if agenda:
            params.update(agenda=agenda)
        if timezone:
            params.update(timezone=timezone)
        if duration:
            params.update(duration=duration)
        if password:
            params.update(password=password)

        headers = {
            "Authorization": "Bearer {}".format(self.access_token)),
            "Content-Type": "application/json",
        }
        url = "{}/meeting/create".format(self.base_url)
        return requests.post(
            url,
            params=params,
            headers=headers
        )


zoom = ZoomClient()

