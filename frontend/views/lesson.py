import json
import base64
from django.utils import timezone
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView
from rest_framework import status
from rest_framework.response import Response
from frontend.forms.lesson import LessonCreateFormStep1, LessonCreateFormStep2, LessonCreateFormStep3, \
    LessonCreateFormStep4, LessonCreateFormPreview
from frontend.utils import get_user_from_token, is_authenticated
from engine.serializers import LessonCreateSerializer, LessonSlotCreateSerializer


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timezone.timedelta(n)


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
        user = self.get_user()
        if not user:
            return redirect('/')
        print(form.errors)
        if self.steps.current == 'preview':
            data = self.get_all_cleaned_data()
            data['goals'] = json.loads(data['goals'])
            data['requirements'] = json.loads(data['requirements'])
            context.update({'form_data': data})
        return context

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get_user(self):
        if is_authenticated(self.request.COOKIES.get('auth_token')):
            return get_user_from_token(self.request.COOKIES.get('auth_token'))

    def done(self, form_list, **kwargs):
        final_data = {}
        for form in form_list:
            final_data.update(form.cleaned_data)
        lesson = self.create(final_data)
        return render(self.request, 'lesson/done.html', {
            'lesson': lesson,
        })

    def create(self, form_data):
        """
        Create Lesson with lesson details
        Create slots based on slot session information
        """
        try:
            user = self.get_user()
            cover_image = None
            if "cover_image" in form_data.keys():
                cover_image, _ = self.base64_file(form_data.pop("cover_image"))
            serializer = LessonCreateSerializer(data=form_data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save(creator=user.teacher_profile_data)

            # Uncomment below lines once bucket gets created on s3
            if cover_image is not None:
                lesson.cover_image = cover_image
                lesson.save()

            now = timezone.now()
            thirty_months = now + timezone.timedelta(days=90)
            start_date = form_data.get('start_date') or now.strftime('%d-%m-%Y')
            end_date = form_data.get('end_date') or thirty_months.strftime('%d-%m-%Y')
            weekdays = form_data.get('weekdays')
            sessions_in_day = form_data.get('sessions_in_day') or [{
                "start_time": "11:00",
                "end_time": "12:00",
                "timezone": "Asia/Kolkata"
            }]
            self.add_available_slots(
                user.teacher_profile_data, lesson, start_date, end_date,
                weekdays, sessions_in_day
            )

            return Response({
                "msg": "Lesson Created",
                "lesson": serializer.validated_data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(str(e))
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext

    @staticmethod
    def add_available_slots(creator, lesson, start_date, end_date, weekdays, sessions_in_day):
        """
        Add Slots for lessons provided by creator
        using date range between start_date and
        end_date with weekdays filter and appending
        start_time and end_time with timezone
        """
        start_date = timezone.datetime.strptime(start_date, '%d-%m-%Y')
        end_date = timezone.datetime.strptime(end_date, '%d-%m-%Y')
        for date in daterange(start_date, end_date):
            if date.strftime('%a') in weekdays:
                for session in sessions_in_day:
                    tz = timezone.pytz.timezone(session.get('timezone'))
                    start_time = timezone.datetime.strptime(session.get('start_time'), '%H:%M').time()
                    end_time = timezone.datetime.strptime(session.get('end_time'), '%H:%M').time()
                    lesson_from = timezone.datetime.combine(date.today(), start_time)
                    lesson_to = timezone.datetime.combine(date.today(), end_time)
                    tz_lesson_from = tz.localize(lesson_from)
                    tz_lesson_to = tz.localize(lesson_to)
                    serializer = LessonSlotCreateSerializer(data=dict(
                        lesson_from=tz_lesson_from,
                        lesson_to=tz_lesson_to
                    ))
                    serializer.is_valid(raise_exception=True)
                    serializer.save(creator=creator, lesson=lesson)
