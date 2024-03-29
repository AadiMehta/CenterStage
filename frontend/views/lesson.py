import json
import pytz
import base64
import logging
from django.utils import timezone
from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from formtools.wizard.views import SessionWizardView
from rest_framework.response import Response
from rest_framework import generics, status
from frontend.forms.lesson import LessonCreateFormStep1, LessonCreateFormStep2, LessonCreateFormStep3, \
    LessonCreateFormStep4, LessonCreateFormPreview
from engine.models import MeetingTypes, LessonLikes, LessonData, SessionTypes
from engine.serializers import LessonCreateSerializer, LessonSlotCreateSerializer
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ParseError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from zoom.utils import zoomclient
from frontend.constants import languages as language_options
from frontend.constants import currencies as currency_options
from frontend.constants import timezones as timezone_options
from frontend.constants import end_date_timedelta
from frontend.utils.google_calendar import GoogleCalendar
from users.models import Accounts, AccountTypes, PaymentAccounts, PaymentTypes
from users.authentication import AuthCookieAuthentication

logger = logging.getLogger(__name__)

from rest_framework.parsers import MultiPartParser
from notifications.views import add_notification 

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timezone.timedelta(n)


class AcceptFileAPI(APIView):
    """
    Accept and store attached files in temporary storage
    """
    parser_class = (FileUploadParser,)

    def post(self, request):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        fl = request.data['file']
        fs = FileSystemStorage(location=settings.TEMP_DIR)
        filename = fs.save(fl.name, fl)
        return Response(dict({
            "url": fs.url(filename)
        }))


class LessonCreateWizard(SessionWizardView):
    TEMPLATES = {
        "step1": "teacher/lesson/step1.html",
        "step2": "teacher/lesson/step2.html",
        "step3": "teacher/lesson/step3.html",
        "step4": "teacher/lesson/step4.html",
        "preview": "teacher/lesson/preview.html",
    }

    FORMS = [
        ("step1", LessonCreateFormStep1),
        ("step2", LessonCreateFormStep2),
        ("step3", LessonCreateFormStep3),
        ("step4", LessonCreateFormStep4),
        ("preview", LessonCreateFormPreview),
    ]

    def get_context_data(self, form, **kwargs):
        context = super(LessonCreateWizard, self).get_context_data(form=form, **kwargs)
        user = self.request.user
        account = user.accounts.filter(account_type=AccountTypes.ZOOM_VIDEO).first()

        if account:
            access_token = account.info.get('access_token')
            context['zoom_linked'] = True if access_token else False
        payment_account = user.payment_account.filter(payment_type=PaymentTypes.STRIPE).exists()
        context['payment_account_linked'] = payment_account
        context['language_options'] = language_options
        context['currency_options'] = currency_options
        context['timezone_options'] = timezone_options
        data = self.get_all_cleaned_data()
        data['goals'] = json.loads(data.get('goals')) if data.get('goals') else []
        data['requirements'] = json.loads(data.get('requirements', '')) if data.get('requirements') else []
        data['language'] = json.loads(data.get('language', '')) if data.get('language') else []
        data['files'] = json.loads(data.get('files', '')) if data.get('files') else []
        context.update({'form_data': data})
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return redirect('/')
        else:
            return super(LessonCreateWizard, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        final_data = {}
        for form in form_list:
            final_data.update(form.cleaned_data)
        final_data['learnings'] = json.loads(final_data.get('goals')) if final_data.get('goals') else []
        final_data['requirements'] = json.loads(final_data.get('requirements', '')) if final_data.get('requirements') \
            else []
        final_data['language'] = json.loads(final_data.get('language', '')) if final_data.get('language') else []
        final_data['files'] = json.loads(final_data.get('files', '')) if final_data.get('files') else []
        final_data['price'] = {
            'type': final_data['price_type'],
            'currency': final_data['price_currency'],
            'value': final_data['price_value'],
        }
        final_data['meeting_type'] = MeetingTypes.HOST_LESSON
        final_data['notes'] = final_data['files']
        return self.create(final_data)
    
    def get_access_token(self, user):
        account = user.accounts.filter(account_type=AccountTypes.ZOOM_VIDEO).first()
        if account:
            access_token = account.info.get('access_token')
            return access_token
        messages.add_message(self.request, messages.ERROR, _('Zoom account is not connected, please connect it first.'))
        return redirect(reverse('new-lesson'))


    def create(self, form_data):
        """
        Create Lesson with lesson details
        Create slots based on slot session information
        """
        try:
            user = self.request.user
            access_token = self.get_access_token(user)
            cover_image = form_data.pop("cover_image")
            if cover_image:
                cover_image, _ = self.base64_file(cover_image)

            topic = form_data.get('name', 'Free Meeting')
            meeting_type = form_data.get('type', '3')
            start_time = timezone.now().isoformat()
            duration = form_data.get('duration', '30')

            meeting = zoomclient.create_meeting(access_token, topic, meeting_type, start_time, duration)
            form_data['meeting_link'] = meeting.get('join_url')
            form_data['meeting_info'] = meeting

            serializer = LessonCreateSerializer(data=form_data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save(creator=user.teacher_profile_data)

            # Uncomment below lines once bucket gets created on s3
            # On Jan 29 - An error occurred (NoSuchBucket) when calling the PutObject operation:
            # The specified bucket does not exist
            if cover_image:
                lesson.cover_image = cover_image
                lesson.save()

            self.add_available_slots(user, lesson, form_data)

            return render(self.request, 'teacher/lesson/done.html', {
                'lesson': lesson,
            })
        except Exception as e:
            logger.exception(e)
            messages.add_message(self.request, messages.ERROR, _('Error occurred while creating lesson, please try again'))
            return redirect('new-lesson')

    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext

    @staticmethod
    def add_available_slots(user, lesson, form_data):
        """
        Add Slots for lessons provided by creator
        using date range between start_date and
        end_date with weekdays filter and appending
        start_time and end_time with timezone
        """
        session_type = form_data.get('session_type')
        session_tz = form_data.get('timezone')
        creator = user.teacher_profile_data
        try:
            google_calendar_account = Accounts.objects.get(
                user=user,
                account_type=AccountTypes.GOOGLE_CALENDAR
            )
        except Accounts.DoesNotExist:
            google_calendar_account = False

        calendar_service = None
        if google_calendar_account:
            calendar_service = GoogleCalendar(google_calendar_account.info)

        if session_type == SessionTypes.ONGOING_SESSION:
            session_start_date = form_data.get('session_date')
            start_date = timezone.datetime.strptime(session_start_date, '%m/%d/%Y')
            session_end_date = start_date + timezone.timedelta(days=end_date_timedelta)
            end_date = session_end_date

            session_no = 1
            for date in daterange(start_date, end_date):
                lesson_tz = form_data.get('timezone', 'Asia/Kolkata')
                start_time = form_data.get('session_start_time')
                session_start_time = timezone.datetime.strptime(start_time, '%H:%M %p').time()
                end_time = form_data.get('session_end_time')
                session_end_time = timezone.datetime.strptime(end_time, '%H:%M %p').time()
                lesson_from = timezone.datetime.combine(date, session_start_time)
                lesson_to = timezone.datetime.combine(date, session_end_time)
                lesson_from_tz = lesson_from.astimezone(pytz.timezone(lesson_tz))
                lesson_to_tz = lesson_to.astimezone(pytz.timezone(lesson_tz))
                serializer = LessonSlotCreateSerializer(data=dict(
                    lesson_from=lesson_from_tz,
                    lesson_to=lesson_to_tz,
                    session_no=session_no
                ))
                serializer.is_valid(raise_exception=True)
                session = serializer.save(creator=creator, lesson=lesson)
                if calendar_service:
                    session.calendar_info = calendar_service.create_calendar_invite(
                        lesson,
                        lesson_from_tz,
                        lesson_to_tz,
                        session_no,
                        emails=[user.email]
                    )
                    session.save()
                session_no += 1

        elif session_type == SessionTypes.SINGLE_SESSION:
            session_start_date = form_data.get('session_date')
            start_date = timezone.datetime.strptime(session_start_date, '%m/%d/%Y')
            session_end_date = start_date.replace(hour=23, minute=59, second=59)
            end_date = session_end_date
            session_no = 1
            lesson_tz = form_data.get('timezone', 'Asia/Kolkata')
            start_time = form_data.get('session_start_time')
            session_start_time = timezone.datetime.strptime(start_time, '%H:%M %p').time()
            end_time = form_data.get('session_start_time')
            session_end_time = timezone.datetime.strptime(end_time, '%H:%M %p').time()
            lesson_from = timezone.datetime.combine(start_date, session_start_time)
            lesson_to = timezone.datetime.combine(end_date, session_end_time)
            lesson_from_tz = lesson_from.astimezone(pytz.timezone(lesson_tz))
            lesson_to_tz = lesson_to.astimezone(pytz.timezone(lesson_tz))
            serializer = LessonSlotCreateSerializer(data=dict(
                lesson_from=lesson_from_tz,
                lesson_to=lesson_to_tz,
                session_no=session_no
            ))
            serializer.is_valid(raise_exception=True)
            session = serializer.save(creator=creator, lesson=lesson)
            if calendar_service:
                session.calendar_info = calendar_service.create_calendar_invite(
                    lesson,
                    lesson_from_tz,
                    lesson_to_tz,
                    session_no,
                    emails=[user.email]
                )
                session.save()
            session_no += 1
        else:
            session_start_date = form_data.get('start_date')
            start_date = timezone.datetime.strptime(session_start_date, '%m/%d/%Y')
            session_end_date = form_data.get('end_date')
            end_date = timezone.datetime.strptime(session_end_date, '%m/%d/%Y')
            weekdays = form_data.get('weekdays')
            session_no = 1
            for date in daterange(start_date, end_date):
                day = date.strftime('%a')
                if day in weekdays:
                    lesson_tz = form_data.get('timezone', 'Asia/Kolkata')
                    start_time = form_data.get('{}_start_time'.format(day.lower()))
                    session_start_time = timezone.datetime.strptime(start_time, '%H:%M %p').time()
                    end_time = form_data.get('{}_end_time'.format(day.lower()))
                    session_end_time = timezone.datetime.strptime(end_time, '%H:%M %p').time()
                    lesson_from = timezone.datetime.combine(date, session_start_time)
                    lesson_to = timezone.datetime.combine(date, session_end_time)
                    lesson_from_tz = lesson_from.astimezone(pytz.timezone(lesson_tz))
                    lesson_to_tz = lesson_to.astimezone(pytz.timezone(lesson_tz))
                    serializer = LessonSlotCreateSerializer(data=dict(
                        lesson_from=lesson_from_tz,
                        lesson_to=lesson_to_tz,
                        session_no=session_no
                    ))
                    serializer.is_valid(raise_exception=True)
                    session = serializer.save(creator=creator, lesson=lesson)
                    if calendar_service:
                        session.calendar_info = calendar_service.create_calendar_invite(
                            lesson,
                            lesson_from_tz,
                            lesson_to_tz,
                            session_no,
                            emails=[user.email]
                        )
                        session.save()
                    session_no += 1

        
class LikeLessonAPIView(generics.CreateAPIView):
    """
    Like Teacher
    """
    authentication_classes = [AuthCookieAuthentication]
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        lesson_uuid = data.get('lesson_uuid')
        lesson = LessonData.objects.get(lesson_uuid=lesson_uuid)

        try:
            LessonLikes.objects.get(
                lesson=lesson,
                user=user
            ).delete()
            msg = 'Like Removal Successful'
            action = 'removed'
        except LessonLikes.DoesNotExist:
            LessonLikes(
                lesson=lesson,
                user=user
            ).save()
            msg = 'Liked Successful'
            action = 'added'
        return Response(dict({"msg": msg, "action": action}), status=status.HTTP_200_OK)
