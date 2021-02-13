from rest_framework.authtoken.models import Token
from users.models import User


# Temporary Function for get and set user
def get_user_from_token(auth_token):
    try:
        user_id = Token.objects.get(key=auth_token).user_id
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return False


def is_authenticated(auth_token):
    """
    Validate if the user is authenticated one
    """
    try:
        user = Token.objects.get(key=auth_token)
        return True
    except Token.DoesNotExist:
        return False


def get_time_duration(td, formatted=False):
    hours = minutes = seconds = 0
    seconds_delta = int(td.total_seconds()) if td else 0
    if seconds_delta > 86400:
        raise ValueError('Do not support beyond one day')
    seconds = seconds_delta % 60
    minutes_delta = int(divmod(seconds_delta, 60)[0])
    minutes = minutes_delta % 60
    hours_delta = int(divmod(seconds_delta, 3600)[0])
    hours = hours_delta % 60
    if formatted:
        final_format = ''
        if seconds > 0:
            final_format = '{} Seconds'.format(seconds, final_format)
        if minutes > 0:
            final_format = '{} Minutes{}'.format(minutes, final_format or '')
        if hours > 0:
            if hours == 1:
                final_format = '{} Hour{}'.format(hours, final_format or '')
            else:
                final_format = '{} Hours{}'.format(hours, final_format or '')
        return final_format
    return hours, minutes, seconds
    