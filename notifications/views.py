from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health_check(request):
    """
    Health check API
    """
    return Response(dict({"status": "System running with no issues!"}), status=200)


def send_signup_email(user):
    """
    Send sign up email to the user
    """
    message = render_to_string('signup_email.html', {'user': user.get_full_name()})
    message_plain = "Hello {0},\n\nThank you for signing up on CenterStage.".format(user.get_full_name())
    send_mail('Welcome to CenterStage!', message_plain, 'no-reply@{}'.format(settings.SITE_URL), [user.email],
              fail_silently=False, html_message=message)
    return


def send_paid_meeting_invites(users, teacher_name, meeting_link):
    """
    Send paid meeting invites to all users
    from the input list
    """
    message = render_to_string('send_paid_meeting_invite.html', {'teacher_name': teacher_name,
                                                                 'meeting_link': meeting_link})
    message_plain = "Hello,\n\nYou have been invited by {} for a meeting.\nThanks".format(teacher_name)
    send_mail('Meeting Invite!', message_plain, 'support@{}'.format(settings.SITE_URL), users,
              fail_silently=False, html_message=message)
    return


def lesson_created(user):
    """
    Send mail to creator about successful creation of lesson
    """
    pass


def lesson_subscribed(user):
    """
    Send mail to subscriber about successful subscription
    to a lesson
    """
    pass
