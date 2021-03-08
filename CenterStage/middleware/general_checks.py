import logging
from django.urls import reverse
from django.shortcuts import HttpResponseRedirect
from users.models import TeacherProfile, StudentProfile
from frontend.utils.auth import is_authenticated, get_user_from_token
from CenterStage.settings import STUDENT_TEMPLATES_PATH, TEACHER_TEMPLATES_PATH, API_URL, CENTERSTAGE_STATIC_PATH

logger = logging.getLogger(__name__)


def check_onboarding(user):
    try:
        # teacher user check profile
        if user.user_type == "CR" and user.teacher_profile_data is not None:
            return True, user.user_type
        elif user.user_type == "ST" and user.student_profile_data is not None:
            return True, user.user_type
        else:
            return False
    except TeacherProfile.DoesNotExist:
        return False, "CR"
    except StudentProfile.DoesNotExist:
        return False, "ST"
    except Exception as e:
        print(str(e))
        return True, ""


class CheckOnboarding(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        if request.path.startswith(API_URL) or request.path.startswith(CENTERSTAGE_STATIC_PATH):
            return self.get_response(request)

        if is_authenticated(request.COOKIES.get('auth_token', None)):
            status, user_type = check_onboarding(get_user_from_token(request.COOKIES.get('auth_token')))
            # if onboarded, don't route to onboarding
            if status:
                if user_type == "CR":
                    if request.path == reverse('onboarding-step-1'):
                        return HttpResponseRedirect(reverse('dashboard-main'))
                    elif request.path.startswith(STUDENT_TEMPLATES_PATH):
                        return HttpResponseRedirect(reverse('dashboard-main'))
                    else:
                        response = self.get_response(request)
                elif user_type == "ST":
                    if request.path == reverse('student-onboarding-step-1'):
                        return HttpResponseRedirect(reverse('student-dashboard-main'))
                    elif request.path.startswith(TEACHER_TEMPLATES_PATH):
                        return HttpResponseRedirect(reverse('student-dashboard-main'))
                    else:
                        response = self.get_response(request)
                else:
                    response = self.get_response(request)
            else:
                # route to the onboarding process
                if user_type == "CR":
                    if request.path.startswith(reverse('onboarding-step-1')):
                        response = self.get_response(request)
                    else:
                        return HttpResponseRedirect(reverse('onboarding-step-1'))
                elif user_type == "ST":
                    if request.path == reverse('student-onboarding-step-1'):
                        response = self.get_response(request)
                    else:
                        return HttpResponseRedirect(reverse('student-onboarding-step-1'))
                else:
                    response = self.get_response(request)
        else:
            # user not logged in
            if request.path != "/":
                return HttpResponseRedirect(reverse('homepage'))
            else:
                response = self.get_response(request)
        return response
