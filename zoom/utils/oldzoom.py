import json
import logging

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from zoomus import ZoomClient as ZoomUsClient

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

        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET
        self.client = ZoomUsClient(settings.ZOOM_CLIENT_ID, settings.ZOOM_CLIENT_SECRET)

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
            return data
    
    def refresh_token(self, refresh_token):
        headers = {
            "Authorization": "Basic {}".format(self.config.get("token")),
            "Content-Type": "application/json",
        }
        url = "{}?grant_type=refresh_token&refresh_token={}".format(
                        self.oauth_url, refresh_token
                    )
        resp = requests.post(
            url,
            headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            return data

    def get_user_details(self, code):
        headers = {
            "Authorization": "Bearer {}".format(self.access_token)),
            "Content-Type": "application/json",
        }
        url = "{}/meeting/create".format(self.base_url)
        resp = requests.get(
            url,
            headers=headers
        )
        if resp.status_code == 200:
            return resp.json()
    
    def create_meeting(self, user_id, topic):
        headers = {
            "Authorization": "Bearer {}".format(self.access_token)),
            "Content-Type": "application/json",
        }
        url = "{}/meeting/create".format(self.base_url)
        resp = requests.get(
            url,
            headers=headers
        )
        /users/{userId}/meetings


zoom = ZoomClient()



