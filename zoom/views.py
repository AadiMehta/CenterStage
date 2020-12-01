import logging

from datetime import datetime, timedelta

from django.conf import settings
from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.views import APIView

from zoom.utils import zoomclient

from users.models import (
    User, TeacherProfile, TeacherAccounts,
    TeacherAccountTypes
)

logger = logging.getLogger(__name__)


class ZoomConnectAPIView(generics.RetrieveAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        teacher = TeacherProfile.objects.get(user=request.user)

        zoom_authorization_code = request.GET.get('code')
        redirect_uri = '{}/profile/zoom/connect'.format(
                                settings.API_BASE_URL
                            )
        access_info = zoomclient.get_access_token(zoom_authorization_code, redirect_uri)
        if not access_info:
            return Response(dict(msg="Something wrong"), status=status.HTTP_400_BAD_REQUEST)
        expires_in = access_info.get('expires_in')
        expire_time = datetime.now() + timedelta(seconds=expires_in)
        access_info['expire_time'] = expire_time.strftime('%Y-%m-%dT%H:%M:%S')
        access_token = access_info.get('access_token')
        user_info = zoomclient.get_user_details(access_token)

        account_info = dict(access_info=access_info, user_info=user_info)

        account, created = TeacherAccounts.objects.get_or_create(teacher=teacher)
        account.account_type = TeacherAccountTypes.ZOOM_VIDEO
        account.info = account_info
        account.save()
        return Response(dict(msg="SuccessFully Connected", account_id=account.id), status=status.HTTP_200_OK)


class ZoomDisconnectAPIView(generics.RetrieveAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = []
 
    def get(self, request, *args, **kwargs):
        redirection_url = request.GET.get('redirection_url')
        teacher = TeacherProfile.objects.get(user=request.user)
        account = TeacherAccounts.objects.get(teacher=teacher)
        account.delete()
        if redirection_url:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return Response(dict(msg="Disconnected Zoom Account"), status=status.HTTP_200_OK)


class ZoomMeetingAPIView(generics.CreateAPIView, generics.ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = []
  
    def create(self, request, *args, **kwargs):
        teacher = TeacherProfile.objects.get(user=request.user)
        account = teacher.accounts.get(account_type=TeacherAccountTypes.ZOOM_VIDEO)
        access_token = self.get_access_token(account)
        if not access_token:
            return Response(dict(msg="Something wrong"), status=status.HTTP_400_BAD_REQUEST)

        topic = request.data.get('topic')
        meeting_type = request.data.get('type')
        start_time = request.data.get('start_time')
        duration = request.data.get('duration')

        meeting = zoomclient.create_meeting(access_token, topic, meeting_type, start_time, duration)

        return Response(meeting, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        teacher = TeacherProfile.objects.get(user=request.user)
        account = teacher.accounts.get(account_type=TeacherAccountTypes.ZOOM_VIDEO)
        access_token = self.get_access_token(account)
        if not access_token:
            return Response(dict(msg="Something wrong"), status=status.HTTP_400_BAD_REQUEST)

        meetings = zoomclient.list_meetings(access_token)
        return Response(dict(meetings=meetings), status=status.HTTP_200_OK)

    @staticmethod
    def get_access_token(account):
        access_info = account.info.get('access_info')
        expire_time = datetime.strptime(access_info.get('expire_time'), '%Y-%m-%dT%H:%M:%S')
        if expire_time > datetime.now():
            access_token = access_info.get('access_token')
            return access_token
        refresh_token = access_info.get('refresh_token')
        new_access_info = zoomclient.refresh_token(refresh_token)
        if not new_access_info:
            return
        new_access_token = new_access_info.get('access_token')
        expires_in = new_access_info.get('expires_in')
        expire_time = datetime.now() + timedelta(seconds=expires_in)
        new_access_info['expire_time'] = expire_time.strftime('%Y-%m-%dT%H:%M:%S')
        account_info = account.info
        account_info.update(access_info=new_access_info)
        account.info = account_info
        account.save()
        return new_access_token
