from rest_framework.authtoken.models import Token
from users.models import User


# Temporary Function for get and set user
def get_user_from_token(auth_token):
    try:
        user_id = Token.objects.get(key=auth_token).user_id
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        pass


def is_authenticated(auth_token):
    """
    Validate if the user is authenticated one
    """
    try:
        user = Token.objects.get(key=auth_token)
        return True
    except Token.DoesNotExist:
        return False
