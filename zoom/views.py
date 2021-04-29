import logging
from datetime import datetime
from django.utils import timezone
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from zoom.serializer import ZoomAuthResponseSerializer
from zoom.utils import zoomclient
from users.serializers import AccountsSerializer
from users.authentication import BearerAuthentication, AuthCookieAuthentication
from users.models import Accounts, AccountTypes
from django.views.generic import TemplateView

logger = logging.getLogger(__name__)


class ZoomConnectAPIView(generics.RetrieveAPIView):
    authentication_classes = [AuthCookieAuthentication]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Zoom redirects to this API with auth code after client authorization

        """
        try:
            zoom_authorization_code = request.GET.get('code')

            resp = zoomclient.get_access_token(zoom_authorization_code)
            resp.raise_for_status()
            if resp.status_code == status.HTTP_200_OK:
                access_info = resp.json()
            else:
                return Response(dict(msg="Zoom Auth Connection Error"), status=status.HTTP_400_BAD_REQUEST)

            serializer = ZoomAuthResponseSerializer(data=access_info)
            serializer.is_valid(raise_exception=True)
            expires_in = serializer.validated_data.get('expires_in')
            expire_time = timezone.now() + timezone.timedelta(seconds=expires_in)
            serializer.validated_data['expire_time'] = expire_time.strftime('%Y-%m-%dT%H:%M:%S')

            serializer = AccountsSerializer(data=dict(account_type=AccountTypes.ZOOM_VIDEO, info=access_info), context={'request': request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return redirect('account-connected-success')
        except Exception as e:
            logger.exception(e)
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ZoomDisconnectAPIView(generics.RetrieveAPIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = []
 
    def get(self, request, *args, **kwargs):
        redirection_url = request.GET.get('redirection_url')
        account = Accounts.objects.get(
            user=request.user,
            account_type=AccountTypes.ZOOM_VIDEO
        )
        if account:
            account.delete()
            if redirection_url:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return Response(dict(msg="Disconnected Zoom Account"), status=status.HTTP_200_OK)


class ZoomMeetingAPIView(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = []
  
    def post(self, request):
        """
        Create New Zoom Meeting link
        """
        try:
            account = request.user.accounts.get(account_type=AccountTypes.ZOOM_VIDEO)
            access_token = self.get_access_token(account)
            if not access_token:
                return Response(dict(msg="Zoom Auth Connection Error"), status=status.HTTP_400_BAD_REQUEST)

            topic = request.data.get('topic', 'Free Meeting')
            meeting_type = request.data.get('type', '2')
            start_time = request.data.get('start_time', timezone.now().isoformat())
            duration = request.data.get('duration', '30')

            meeting = zoomclient.create_meeting(access_token, topic, meeting_type, start_time, duration)

            return Response(meeting, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception(e)
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        account = request.user.accounts.get(account_type=AccountTypes.ZOOM_VIDEO)
        access_token = self.get_access_token(account)
        if not access_token:
            logger.error("Zoom Auth connection error")
            return Response(dict(msg="Zoom Auth Connection Error"), status=status.HTTP_400_BAD_REQUEST)

        meetings = zoomclient.list_meetings(access_token)
        return Response(dict(meetings=meetings), status=status.HTTP_200_OK)

    @staticmethod
    def get_access_token(account):
        expire_time = account.info.get('expires_time')
        if expire_time:
            expire_time = datetime.strptime(expire_time, '%Y-%m-%dT%H:%M:%S')
            if expire_time > timezone.now():
                # If expire time is greater than current time then return
                return account.info.get('access_token')

        # If token is expired then refresh token
        refresh_token = account.info.get('refresh_token')
        resp = zoomclient.refresh_token(refresh_token)
        if resp.status_code == status.HTTP_200_OK:
            access_info = resp.json()
            serializer = ZoomAuthResponseSerializer(data=access_info)
            serializer.is_valid(raise_exception=True)
            expires_in = serializer.validated_data.get('expires_in')
            expire_time = timezone.now() + timezone.timedelta(seconds=expires_in)
            serializer.validated_data['expire_time'] = expire_time.strftime('%Y-%m-%dT%H:%M:%S')

            account.info = serializer.validated_data
            account.save()
            return access_info.get('access_token')


class ZoomVerifyView(TemplateView):
    """
    Onboarding step 3
    """
    template_name = "verifyzoom.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
