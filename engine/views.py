import base64
import logging
import _thread
from rest_framework import status
from django.utils import timezone
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.base import ContentFile
from users.authentication import BearerAuthentication
from engine.serializers import (
    LessonCreateSerializer, LessonSlotCreateSerializer, MeetingCreateSerializer, NoteCreateSerializer, PostCreateSerializer
)
from users.models import AccountTypes
from zoom.utils import zoomclient
from notifications.views import send_paid_meeting_invites
logger = logging.getLogger(__name__)

from notifications.views import add_notification 

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
        Create slots based on slot session information
        """
        try:
            cover_image = None
            if "cover_image" in request.data.keys():
                cover_image, ext = self.base64_file(request.data.pop("cover_image"))
            serializer = LessonCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            lesson = serializer.save(creator=request.user.teacher_profile_data)

            # Uncomment below lines once bucket gets created on s3
            # if cover_image is not None:
            #     lesson.cover_image = cover_image
            #     lesson.save()

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
            add_notification(lesson.creator.user, 'CenterStage', 'dashboard/lessons', 1)
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
        using date range between start_date and end_date
        with weekdays filter and appending start_time
        and end_time with timezone
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


class MeetingAPIView(APIView):
    """
    API to create meeting
    """
    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def post(self, request):
        """
        Create Meeting with meeting details
        """
        try:
            user = request.user
            account = user.accounts.get(
                account_type=AccountTypes.ZOOM_VIDEO
            )
            access_token = account.info.get('access_token')
            if not access_token:
                return redirect('dashboard-main')

            request_data = request.data
            topic = request_data.get('topic', 'Free Meeting')
            meeting_type = request_data.get('type', '2')
            start_time = request_data.get('start_time', timezone.now().isoformat())
            duration = request_data.get('duration', '30')

            meeting = zoomclient.create_meeting(access_token, topic, meeting_type, start_time, duration)
            request_data['meeting_link'] = meeting.get('join_url')
            request_data['meeting_info'] = meeting

            serializer = MeetingCreateSerializer(data=request_data)
            serializer.is_valid(raise_exception=True)
            serializer.save(creator=request.user.teacher_profile_data)

            _thread.start_new_thread(send_paid_meeting_invites, (request_data.get("invitees", []),
                                                                 request.user.get_full_name(),
                                                                 request_data['meeting_link'], ))
            return Response({
                "msg": "Meeting Created",
                "meeting": serializer.validated_data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(str(e))
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NoteAPIView(APIView):
    """
    API to create note
    """
    authentication_classes = [BearerAuthentication]
    permission_classes = []

    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext

    def post(self, request):

        try:
            cover_image = None
            if "cover_image" in request.data.keys():
                cover_image, ext = self.base64_file(request.data.pop("cover_image"))
            serializer = NoteCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            note = serializer.save(creator=request.user.teacher_profile_data)
            if cover_image is not None:
                note.cover_image = cover_image
                note.save()
            return Response({
                "msg": "Note Created",
                "note": serializer.validated_data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(str(e))
            return Response(dict({
                "error": str(e)
            }), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PostAPIView(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def post(self,request):
        try:
            serializer = PostCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return Response({
                "msg":"Post Created",
                "post": serializer.validated_data
                }, status=status.HTTP_201_CREATED)
        except:
            print('error in creating post')
