from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from users.models import User, TeacherProfile
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from users.authentication import BearerAuthentication
from notifications.models import Notification



def ShowNOtifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-date')
    Notification.objects.filter(user=user, is_seen=False).update(is_seen=True)

    template = loader.get_template('notifications.html')

    context = {
        'notifications': notifications,
    }

    return HttpResponse(template.render(context, request))


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health_check(request):
    """
    Health check API
    """
    return Response(dict({"status": "System running with no issues!"}), status=200)


def add_notification(user, sender, action_url, notification_type,):
    print("notification creation")
    notification = Notification(user=user,sender=sender,action_url=action_url,notification_type=1)
    notification.save()


@api_view(["GET"])
@authentication_classes([BearerAuthentication])
@permission_classes([])
def get_notification_count(request):
    user = request.user
    # try:
    notification_count = Notification.objects.filter(user=user)
    print(dir(notification_count))
    print (notification_count)
    # except:
    #     notification_count = 0
    return Response(dict({"count":str(notification_count.count())}))

def send_signup_email(user,template):
    """
    Send sign up email to the user
    """
    # message = render_to_string('signup_email.html', {'user': user.get_full_name()})
    # message_plain = "Hello {0},\n\nThank you for signing up on CenterStage.".format(user.get_full_name())
    # send_mail('Welcome to CenterStage!', message_plain, 'no-reply@center-stage.online', [user.email],
    #           fail_silently=False, html_message=message)
    # return

    message = render_to_string(template, {'user': user.get_full_name()})
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

def send_signup_whatsapp(user):
    phone_no = user.phone_no


@api_view(["POST"])
@authentication_classes([BearerAuthentication])
@permission_classes([])
def send_mail_signup(request):
    teacher = TeacherProfile.objects.get(user=request.user)
    html_message = render_to_string('signup_email.html', {'user': teacher.user.get_full_name()})
    message_plain = "Hello {0},\n\nYour Profile is Registered".format(teacher.user.get_full_name())
    send_mail('Registration complete', message_plain, 'no-reply@center-stage.online', [teacher.user.email],
              fail_silently=False, html_message=html_message)
    return Response(dict({"status": "System running with no issues!"}), status=200)




def lesson_created(user):
    """
    Send mail to creator about successful creation of lesson
    """
    notify = Notification(post=post, sender=sender, user=post.user, notification_type=1)
    pass


def lesson_subscribed(user):
    """
    Send mail to subscriber about successful subscription
    to a lesson
    """
    pass
