import base64
from rest_framework import status
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.base import ContentFile
from users.authentication import BearerAuthentication
from engine.models import LessonData
from engine.serializers import LessonCreateSerializer, LessonSlotCreateSerializer


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timezone.timedelta(n)


class LessonAPIView(APIView):
    """
    API to create lesson and book slots
    """
    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def post(self, request):
        """
        Create Lesson with lesson details
        Create slots based on slot session informations
        """
        try:
            cover_image = None
            if "cover_image" in request.data.keys():
                cover_image, ext = self.base64_file(request.data.pop("cover_image"))
            serializer = LessonCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save(creator=request.user.teacher_profile_data)

            # Uncomment below lines once bucket gets created on s3
            # lesson.cover_image = cover_image
            # lesson.save()

            now = timezone.now()
            thirty_months = now + timezone.timedelta(days=90)
            start_date = request.data.get('start_date') or now.strftime('%d-%m-%Y')
            end_date = request.data.get('end_date') or thirty_months.strftime('%d-%m-%Y')
            weekdays = request.data.get('weekdays')
            sessions_in_day = request.data.get('sessions_in_day')
            self.add_available_slots(
                request.user.teacher_profile_data, lesson, start_date, end_date,
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
        using daterange between start_date and end_date with weekdays filter
        and appending start_time and end_time with timezone
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
