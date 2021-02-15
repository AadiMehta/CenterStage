import json
import pytz
import base64
from django.utils import timezone
from pytz import timezone as pytztimezone
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView

from rest_framework import status
from rest_framework.response import Response
from frontend.forms.lesson import LessonCreateFormStep1, LessonCreateFormStep2, LessonCreateFormStep3, \
    LessonCreateFormStep4, LessonCreateFormPreview
from frontend.utils import get_user_from_token, is_authenticated
from engine.models import MeetingTypes
from engine.serializers import LessonCreateSerializer, LessonSlotCreateSerializer
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ParseError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import MultiPartParser
from users.models import TeacherAccounts, TeacherAccountTypes, TeacherAccountTypes
from zoom.utils import zoomclient

from frontend.constants import languages as language_options
from frontend.constants import timezones as timezone_options


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
        "step1": "lesson/step1.html",
        "step2": "lesson/step2.html",
        "step3": "lesson/step3.html",
        "step4": "lesson/step4.html",
        "preview": "lesson/preview.html",
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
        context['language_options'] = language_options
        context['timezone_options'] = timezone_options
        if self.steps.current == 'preview':
            data = self.get_all_cleaned_data()
            data['goals'] = json.loads(data.get('goals')) if data.get('goals') else []
            data['requirements'] = json.loads(data.get('requirements', '')) if data.get('requirements') else []
            data['language'] = json.loads(data.get('language', '')) if data.get('language') else []
            data['files'] = json.loads(data.get('files', '')) if data.get('files') else []
            context.update({'form_data': data})
        return context

    def dispatch(self, request, *args, **kwargs):
        user = self.get_user()
        if not user:
            return redirect('/')
        else:
            return super(LessonCreateWizard, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_user(self):
        if is_authenticated(self.request.COOKIES.get('auth_token')):
            return get_user_from_token(self.request.COOKIES.get('auth_token'))
        else:
            return False

    def done(self, form_list, **kwargs):
        final_data = {}
        for form in form_list:
            final_data.update(form.cleaned_data)
        final_data['goals'] = json.loads(final_data.get('goals')) if final_data.get('goals') else []
        final_data['requirements'] = json.loads(final_data.get('requirements', '')) if final_data.get('requirements') else []
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

    def create(self, form_data):
        """
        Create Lesson with lesson details
        Create slots based on slot session information
        """
        try:
            user = self.get_user()
            account = user.teacher_profile_data.accounts.get(
                account_type=TeacherAccountTypes.ZOOM_VIDEO
            )
            access_token = account.info.get('access_token')
            if not access_token:
                return redirect('new-lesson')

            cover_image = form_data.pop("cover_image")
            if cover_image:
                cover_image, _ = self.base64_file(cover_image)

            topic = form_data.get('name', 'Free Meeting')
            meeting_type = form_data.get('type', '2')
            start_time = form_data.get('start_time', timezone.now().isoformat())
            duration = form_data.get('duration', '30')

            meeting = zoomclient.create_meeting(access_token, topic, meeting_type, start_time, duration)
            form_data['meeting_link'] = meeting.get('join_url')
            form_data['meeting_info'] = meeting

            serializer = LessonCreateSerializer(data=form_data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save(creator=user.teacher_profile_data)

            # Uncomment below lines once bucket gets created on s3
            # On Jan 29 - An error occurred (NoSuchBucket) when calling the PutObject operation: The specified bucket does not exist
            # if cover_image:
            #     lesson.cover_image = cover_image
            #     lesson.save()

            now = timezone.now()
            thirty_months = now + timezone.timedelta(days=90)
            start_date = form_data.get('start_date') or now.strftime('%m/%d/%Y')
            end_date = form_data.get('end_date') or thirty_months.strftime('%m/%d/%Y')
            weekdays = form_data.get('weekdays')

            sessions_in_day = form_data.get('sessions_in_day') or [{
                "start_time": "11:00",
                "end_time": "12:00",
                "timezone": "Asia/Kolkata"
            }]
            session_tz = form_data.get('timezone')
            self.add_available_slots(
                user.teacher_profile_data, lesson, form_data, start_date, end_date,
                weekdays, sessions_in_day, session_tz
            )

            return render(self.request, 'lesson/done.html', {
                'lesson': lesson,
            })
        except Exception as e:
            print(str(e))
            raise e
            return redirect('new-lesson')

    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext

    @staticmethod
    def add_available_slots(creator, lesson, form_data, start_date, end_date, weekdays, sessions_in_day, session_tz):
        """
        Add Slots for lessons provided by creator
        using date range between start_date and
        end_date with weekdays filter and appending
        start_time and end_time with timezone
        """
        start_date = timezone.datetime.strptime(start_date, '%m/%d/%Y')
        end_date = timezone.datetime.strptime(end_date, '%m/%d/%Y')
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
                serializer = LessonSlotCreateSerializer(data=dict(
                    lesson_from=lesson_from.astimezone(pytz.timezone(lesson_tz)),
                    lesson_to=lesson_to.astimezone(pytz.timezone(lesson_tz))
                ))
                serializer.is_valid(raise_exception=True)
                serializer.save(creator=creator, lesson=lesson)
