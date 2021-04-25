from django.db.models import Q
from django.shortcuts import get_object_or_404
from users.models import User, TeacherProfile, ProfileStatuses, StudentProfile
from users.serializers import TeacherProfileSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication
from rest_framework import status

from django.conf import settings
from chat.serializers import MessageModelSerializer, UserModelSerializer
from chat.models import MessageModel
from rest_framework.views import APIView
from users.authentication import BearerAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from chat.serializers import MessageUserSerializer, MessageContactSerializer


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """

    def enforce_csrf(self, request):
        return

class MessagePagination(PageNumberPagination):
    """
    Limit message prefetch to one page.
    """
    page_size = settings.MESSAGES_TO_LOAD


class MessageModelViewSet(ModelViewSet):
    queryset = MessageModel.objects.all()
    serializer_class = MessageModelSerializer
    allowed_methods = ('GET', 'POST')
    authentication_classes = [BearerAuthentication,]
    permission_classes = []
    pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(Q(recipient=request.user) |
                                             Q(user=request.user))
        target = self.request.query_params.get('target', None)
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__email=target) |
                Q(recipient__email=target, user=request.user))
        # serializer = self.get_serializer(self.queryset,many=True)
        return super(MessageModelViewSet, self).list(request, *args, **kwargs)
        # print(serializer.data)
        # return Response(serializer.data,status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(
            self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk'])))
        serializer = self.get_serializer(msg)
        return Response(serializer.data,status=status.HTTP_200_OK)

class GetMessages(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def get(self, request):
        self.queryset = MessageModel.objects.all()
        self.queryset = self.queryset.filter(Q(recipient=request.user) |
                                             Q(user=request.user))
        target = self.request.query_params.get('target', None)
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__email=target) |
                Q(recipient__email=target, user=request.user))
        serializer = MessageModelSerializer(self.queryset,many=True)
        print(serializer.data)
        return Response(serializer.data,status=status.HTTP_200_OK)

# class MessageModelViewSet(APIView):

#     authentication_classes = [BearerAuthentication]
#     permission_classes = []



#     def get(self, request, *args, **kwargs):
#         print(request.user)
#         queryset = MessageModel.objects.all()
#         queryset = queryset.filter(Q(recipient=request.user) |
#                                              Q(user=request.user))
#         target = request.query_params.get('target', None)
#         print(target)
#         if target is not None:
#             queryset = queryset.filter(
#                 Q(recipient=request.user, user__email=target) |
#                 Q(recipient__email=target, user=request.user))
#         print(queryset)
#         serializer = MessageModelSerializer(queryset,many=True)
#         # return super(MessageModelViewSet, self).list(request, *args, **kwargs)
#         return Response(serializer.data)


class MessageView(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = []

    def get(self, request):
        print(request.user)
        pk = request.query_params.get('id', None)
        queryset = MessageModel.objects.all()
        msg = get_object_or_404(
            queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=pk)))
        serializer = MessageModelSerializer(msg)
        return Response(serializer.data)  


class SendMessageAPI(APIView):
    authentication_classes = [BearerAuthentication]
    permission_classes = []
    
    def post(self, request):
        print(request.data)
        user = request.user
        print(user)
        data = request.data
        recipient = get_object_or_404(
            User, email=data['recipient'])
        msg = MessageModel(recipient=recipient,
                           body=data['body'],
                           user=user)
        msg.save()
        serializer = MessageModelSerializer(msg)
        return Response({"status":"success"})              


class MessageContacts(APIView):

    authentication_classes = [BearerAuthentication]
    permission_classes = []
  
    def get(self,request):
        print(request.user)
        contacts = []
        messages = MessageModel.objects.filter(Q(recipient=request.user) | Q(user=request.user)).order_by('-timestamp')
        for message in messages:
            if message.recipient == request.user:
                if message.user not in contacts:
                    contacts.append(message.user)
            else:
                if message.recipient not in contacts:
                    contacts.append(message.recipient)
        users = User.objects.all()
        context = {'user':request.user}
        contacts_serializer = MessageContactSerializer(contacts,context=context,many=True)
        users_serializer = MessageContactSerializer(users,context=context,many=True)
        resp = {'active':contacts_serializer.data,'inactive':users_serializer.data}
        return Response(resp, status=status.HTTP_200_OK)

