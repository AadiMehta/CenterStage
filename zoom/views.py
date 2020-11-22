import logging

from datetime import datetime

from django.conf import settings
from django.http import HttpResponseRedirect

from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import authentication, permissions

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
        teacher_id = kwargs.get('teacher_id')
        teacher = TeacherProfile.objects.get(id=teacher_id)
        zoom_authorization_code = request.GET.get('code')
        redirect_uri = '{}/profile/teacher/{}/zoom/connect'.format(
                                settings.API_BASE_URL, teacher_id
                            )
        access_info = zoomclient.get_access_token(zoom_authorization_code, redirect_uri)
        if not access_info:
            return Response(dict(msg="Something wrong"), status=status.HTTP_400_BAD_REQUEST)
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
        teacher_id = kwargs.get('teacher_id')
        redirection_url = request.GET.get('redirection_url')
        teacher = TeacherProfile.objects.get(id=teacher_id)
        account = TeacherAccounts.objects.get(teacher=teacher)
        account.delete()
        if redirection_url:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return Response(dict(msg="Disconnected Zoom Account"), status=status.HTTP_200_OK)


class ZoomMeetingAPIView(generics.CreateAPIView, generics.ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = []
  
    def create(self, request, *args, **kwargs):
        teacher_id = kwargs.get('teacher_id')
        teacher = TeacherProfile.objects.get(id=teacher_id)

        access_token = request.META.get('HTTP_ACCESS_TOKEN')

        topic = request.data.get('topic')
        meeting_type = request.data.get('type')
        start_time = request.data.get('start_time')
        duration = request.data.get('duration')

        print(access_token, topic, meeting_type, start_time, duration)
        meeting = zoomclient.create_meeting(access_token, topic, meeting_type, start_time, duration)

        return Response(meeting, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        teacher_id = kwargs.get('teacher_id')
        teacher = TeacherProfile.objects.get(id=teacher_id)

        access_token = request.META.get('HTTP_ACCESS_TOKEN')

        meetings = zoomclient.list_meetings(access_token)

        return Response(dict(meetings=meetings), status=status.HTTP_200_OK)
