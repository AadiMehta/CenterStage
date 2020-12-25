import json
import base64
import logging
import requests
import urllib

from datetime import datetime

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from rest_framework import status

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
        self.oauth_url = 'https://zoom.us/oauth/token'
        self.api_base_url = 'https://api.zoom.us/v2'

        self.client_id = settings.ZOOM_CLIENT_ID
        self.client_secret = settings.ZOOM_CLIENT_SECRET

        if not all([self.client_id, self.client_secret]):
            raise ImproperlyConfigured(NOT_CONFIGURED_MESSAGE)

        self.encoded_auth_token = self.get_encoded_auth_token()

    def get_encoded_auth_token(self):
        """
        Get Encoded Token in Base64 format for API connections
        returns encoded base64 string of `client_id:secret_key`
        """
        auth_token = '{}:{}'.format(self.client_id, self.client_secret).encode('ascii')
        return base64.b64encode(auth_token).decode('ascii')

    def get_access_token(self, code):
        """
        Get Encoded Token in Base64 format for API connections
        returns encoded base64 string of `client_id:secret_key`
        """
        redirect_uri = urllib.parse.quote(settings.ZOOM_REDIRECT_URL)
        headers = {
            "Authorization": "Basic {}".format(self.encoded_auth_token),
            "Content-Type": "application/json"
        }
        url = "{}?grant_type=authorization_code&code={}&redirect_uri={}".format(
                        self.oauth_url, code,
                        redirect_uri
                    )
        return requests.post(
            url,
            headers=headers
        )

    def refresh_token(self, refresh_token):
        headers = {
            "Authorization": "Basic {}".format(self.encoded_auth_token),
            "Content-Type": "application/json",
        }
        url = "{}?grant_type=refresh_token&refresh_token={}".format(
                        self.oauth_url, refresh_token
                    )
        return requests.post(
            url,
            headers=headers
        )


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
        if resp.status_code == 201:
            return resp.json()
        resp.raise_for_status()

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
