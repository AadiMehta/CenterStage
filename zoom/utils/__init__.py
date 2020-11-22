import json
import base64
import logging
import requests
import urllib

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from zoomus import ZoomClient as ZoomUsClient

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

    def __init__(self):
        logger.debug('Initializing zoom client')

        self.oauth_url = 'https://zoom.us/oauth/token'
        self.api_base_url = 'https://api.zoom.us/v2'

        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET

        if not all([self.client_id, self.client_secret]):
            raise ImproperlyConfigured(NOT_CONFIGURED_MESSAGE)

        self.encoded_token = base64.b64encode('{}:{}'.format(self.client_id, self.client_secret).encode('ascii')).decode('ascii')
        self.client = ZoomUsClient(self.client_id, self.client_secret)
        self.config = self.client.config
        logger.debug('Zoom client initialized')

    def get_access_token(self, code, redirect_uri):
        headers = {
            "Authorization": "Basic {}".format(self.encoded_token),
            "Content-Type": "application/json"
        }
        url = "{}?grant_type=authorization_code&code={}&redirect_uri={}".format(
                        self.oauth_url, code,
                        urllib.parse.quote(redirect_uri)
                    )
        resp = requests.post(
            url,
            headers=headers
        )
        if resp.status_code == 200:
            data = resp.json()
            print(data)
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

    def get_user_details(self, access_token):
        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json"
        }
        url = "{}/users/me".format(self.api_base_url)
        resp = requests.get(
            url,
            headers=headers
        )
        if resp.status_code == 200:
            return resp.json()

    def create_meeting(self,
            access_token, topic, meeting_type, 
            start_time, duration=None
        ):
        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        }
        url = "{}/users/me/meetings".format(self.api_base_url)
        data = dict(
            topic=topic, start_time=start_time,
            type=meeting_type, timezone="Asia/Kolkata"
        )
        if duration:
            data.update(duration=duration)

        resp = requests.post(
            url,
            headers=headers,
            data=json.dumps(data)
        )
        print(resp)
        print(resp.reason)
        if resp.status_code == 201:
            return resp.json()

    def list_meetings(self, access_token):
        headers = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type": "application/json",
        }
        url = "{}/users/me/meetings".format(self.api_base_url)
        resp = requests.get(
            url,
            headers=headers
        )
        if resp.status_code == 200:
            return resp.json()


zoomclient = ZoomClient()
