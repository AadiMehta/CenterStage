import json
import pytz
import base64
import logging
from django.utils import timezone
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView
from rest_framework.response import Response
from frontend.forms.schedule import ScheduleCreateFormStep1, ScheduleCreateFormStep2, ScheduleCreateFormPreview
from engine.models import MeetingTypes
from engine.serializers import LessonCreateSerializer, LessonSlotCreateSerializer
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ParseError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from zoom.utils import zoomclient
from frontend.constants import languages as language_options
from frontend.constants import timezones as timezone_options
from frontend.utils.google_calendar import GoogleCalendar
from users.models import TeacherAccounts, TeacherAccountTypes

logger = logging.getLogger(__name__)


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timezone.timedelta(n)


class AcceptFileAPI(APIView):
    """
    Accept and store attached files in temporary storage
    """
    parser_class = (FileUploadParser,)

    def post(self, request, format=None):
        if 'file' not in request.data:
            raise ParseError("Empty content")

        fl = request.data['file']
        fs = FileSystemStorage(location=settings.TEMP_DIR)
        filename = fs.save(fl.name, fl)
        return Response(dict({
            "url": fs.url(filename)
        }))


class ScheduleCreateWizard(SessionWizardView):
    TEMPLATES = {
        "step1": "teacher/schedule/schedule01.html",
        "step2": "teacher/schedule/schedule02.html",
        "preview": "teacher/schedule/preview.html",
    }

    FORMS = [
        ("step1", ScheduleCreateFormStep1),
        ("step2", ScheduleCreateFormStep2),
        ("preview", ScheduleCreateFormPreview),
    ]

    def get_context_data(self, form, **kwargs):
        context = super(ScheduleCreateWizard, self).get_context_data(form=form, **kwargs)
        context['language_options'] = language_options
        context['timezone_options'] = timezone_options
        if self.steps.current == 'preview':
            data = self.get_all_cleaned_data()
            data['invitees'] = json.loads(data.get('invitees')) if data.get('invitees') else []
            context.update({'form_data': data})
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        else:
            return super(ScheduleCreateWizard, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        final_data = {}
        for form in form_list:
            final_data.update(form.cleaned_data)
        final_data['invitees'] = json.loads(final_data.get('invitees')) if final_data.get('invitees') else []
        final_data['meeting_type'] = MeetingTypes.SCHEDULE
        return self.create(final_data)

    def create(self, form_data):
        """
        Create Lesson with lesson details
        Create slots based on slot session information
        """
        try:
            user = self.request.user
            account = user.teacher_profile_data.accounts.get(
                account_type=TeacherAccountTypes.ZOOM_VIDEO
            )
            access_token = account.info.get('access_token')
            if not access_token:
                return redirect('new-schedule')

            topic = form_data.get('name', 'Free Meeting')
            meeting_type = form_data.get('type', '2')
            start_time = timezone.now().isoformat()
            duration = form_data.get('duration', '30')

            meeting = zoomclient.create_meeting(access_token, topic, meeting_type, start_time, duration)
            form_data['meeting_link'] = meeting.get('join_url')
            form_data['meeting_info'] = meeting

            serializer = LessonCreateSerializer(data=form_data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save(creator=user.teacher_profile_data)

            now = timezone.now()
            thirty_months = now + timezone.timedelta(days=90)
            start_date = form_data.get('start_date') or now.strftime('%m/%d/%Y')
            end_date = form_data.get('end_date') or thirty_months.strftime('%m/%d/%Y')
            weekdays = form_data.get('weekdays')

            session_tz = form_data.get('timezone')
            self.add_available_slots(
                user, lesson, form_data, start_date, end_date,
                weekdays, session_tz
            )

            return render(self.request, 'teacher/lesson/done.html', {
                'lesson': lesson,
            })
        except Exception as e:
            logger.exception(e)
            return redirect('new-schedule')

    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext

    @staticmethod
    def add_available_slots(user, lesson, form_data, start_date, end_date, weekdays, session_tz):
        """
        Add Slots for lessons provided by creator
        using date range between start_date and
        end_date with weekdays filter and appending
        start_time and end_time with timezone
        """
        start_date = timezone.datetime.strptime(start_date, '%m/%d/%Y')
        end_date = timezone.datetime.strptime(end_date, '%m/%d/%Y')
        creator = user.teacher_profile_data
        google_calendar_account = TeacherAccounts.objects.get(
            teacher=creator,
            account_type=TeacherAccountTypes.GOOGLE_CALENDAR
        )
        calendar_service = None
        if google_calendar_account:
            calendar_service = GoogleCalendar(google_calendar_account.info)
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
                        lesson_from,
                        lesson_to,
                        session_no,
                        emails=[user.email]
                    )
                    session.save()
