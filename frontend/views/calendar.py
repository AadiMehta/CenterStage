import logging
import google_auth_oauthlib.flow
from django.conf import settings
from rest_framework import status
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from rest_framework import generics
from rest_framework.response import Response
from users.serializers import AccountsSerializer
from users.authentication import BearerAuthentication, AuthCookieAuthentication
from users.models import Accounts, AccountTypes

logger = logging.getLogger(__name__)


class AuthorizeGoogleCalendar(generics.RetrieveAPIView):
    authentication_classes = [AuthCookieAuthentication]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            'credentials.json',
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/calendar.events',
                'https://www.googleapis.com/auth/calendar',
                'https://www.googleapis.com/auth/calendar.readonly'
            ]
        )
        flow.redirect_uri = '{}/api/profile/google/calendar/oauth/callback'.format(settings.BASE_URL)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return redirect(authorization_url)


class GoogleCalendarCallback(generics.RetrieveAPIView):
    authentication_classes = [AuthCookieAuthentication]
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """
        Google redirects to this API with auth code after client authorization

        """
        try:
            state = request.GET.get('state')
            flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                'credentials.json',
                scopes=[
                    'openid',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'https://www.googleapis.com/auth/userinfo.profile',
                    'https://www.googleapis.com/auth/calendar.events',
                    'https://www.googleapis.com/auth/calendar',
                    'https://www.googleapis.com/auth/calendar.readonly'
                ],
                state=state
            )
            flow.redirect_uri = '{}/api/profile/google/calendar/oauth/callback'.format(settings.BASE_URL)
            authorization_response = '{}{}'.format(settings.BASE_URL, request.get_full_path())

            flow.fetch_token(authorization_response=authorization_response)
            credentials = flow.credentials
            session_credentials = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            # serializer = AccountsSerializer(data=dict(
            #                                     account_type=AccountTypes.GOOGLE_CALENDAR,
            #                                     info=session_credentials
            #                                 ))
            # serializer.is_valid(raise_exception=True)
            # serializer.save(user=request.user)
            account_data = {
                'account_type':AccountTypes.GOOGLE_CALENDAR,
                'info': session_credentials
            }
            account_obj, created = Accounts.objects.new_or_update(request.user, account_data)   # noqa
            return redirect('account-connected-success')
        except Exception as e:
            logger.exception(e)
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GoogleDisconnectAPIView(generics.RetrieveAPIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = []
 
    def get(self, request, *args, **kwargs):
        redirection_url = request.GET.get('redirection_url')
        account = Accounts.objects.get(
            user=request.user,
            account_type=AccountTypes.GOOGLE_CALENDAR
        )
        if account:
            account.delete()
            if redirection_url:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return Response(dict(msg="Disconnected Google Account"), status=status.HTTP_200_OK)
