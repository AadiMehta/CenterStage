from rest_framework import authentication


class BearerAuthentication(authentication.TokenAuthentication):
    """
    Simple token based authentication using username and password

    Clients should authenticate by passing the token key in the 'Authorization'
    HTTP header, prepended with the string 'Bearer '.  For example:

    Authorization: Bearer 956e252a-513c-48c5-92dd-bfddc364e812
    """
    keyword = 'Bearer'


class AuthCookieAuthentication(authentication.TokenAuthentication):
    """
    Extend the TokenAuthentication class to support cookie based authentication
    """
    keyword = 'Bearer'

    def authenticate(self, request):
        # Check if 'auth_token' is in the request cookies.
        # Give precedence to 'Authorization' header.
        if 'auth_token' in request.COOKIES and \
                        'HTTP_AUTHORIZATION' not in request.META:
            return self.authenticate_credentials(
                request.COOKIES.get('auth_token')
            )
        return super().authenticate(request)
