import json
import base64
from django.utils import timezone
from django.core.files.base import ContentFile
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView
from rest_framework import status
from rest_framework.response import Response
from frontend.forms.note import NoteCreateFormStep1, NoteCreateFormStep2, NoteCreateFormStep3, NoteCreateFormPreview
from frontend.utils.auth import get_user_from_token, is_authenticated
from engine.models import MeetingTypes
from engine.serializers import NoteCreateSerializer
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.exceptions import ParseError
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.parsers import MultiPartParser


class AcceptNoteFileAPI(APIView):
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

class NoteCreateWizard(SessionWizardView):
    TEMPLATES = {
        "step1": "note/step1.html",
        "step2": "note/step2.html",
        "step3": "note/step3.html",
        "preview": "note/preview.html",
    }

    FORMS = [
        ("step1", NoteCreateFormStep1),
        ("step2", NoteCreateFormStep2),
        ("step3", NoteCreateFormStep3),
        ("preview", NoteCreateFormPreview),
    ]

    def get_context_data(self, form, **kwargs):
        context = super(NoteCreateWizard, self).get_context_data(form=form, **kwargs)
        if self.steps.current == 'preview':
            data = self.get_all_cleaned_data()
            data['goals'] = json.loads(data.get('goals')) if data.get('goals') else []
            data['files'] = json.loads(data.get('files', '')) if data.get('files') else []
            print (data['files'])
            context.update({'form_data': data})
        return context

    def dispatch(self, request, *args, **kwargs):
        user = self.get_user()
        print(user)
        if not user:
            return redirect('/')
        else:
            return super(NoteCreateWizard, self).dispatch(request, *args, **kwargs)

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
        final_data['price'] = {
            'currency': final_data['price_currency'],
            'value': final_data['price_value'],
        }
        final_data['documents'] = final_data['files']
        print (final_data['documents'])
        return self.create(final_data)

    def create(self, form_data):
        """
        Create Note with note details
        """
        # try:
        print('in careate')
        user = self.get_user()
        cover_image = form_data.pop("cover_image")
        if cover_image:
            cover_image, _ = self.base64_file(cover_image)
        serializer = NoteCreateSerializer(data=form_data)
        serializer.is_valid(raise_exception=True)
        note = serializer.save(creator=user.teacher_profile_data)

        # Uncomment below lines once bucket gets created on s3
        # On Jan 29 - An error occurred (NoSuchBucket) when calling the PutObject operation: The specified bucket does not exist
        if cover_image:
            note.cover_image = cover_image
            note.save()

        now = timezone.now()
        return render(self.request, 'note/done.html', {
            'note': note,
        })
        # except Exception as e:
        #     print(str(e))
        #     raise e

    @staticmethod
    def base64_file(data, name=None):
        _format, _img_str = data.split(';base64,')
        _name, ext = _format.split('/')
        if not name:
            name = _name.split(":")[-1]
        return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext)), ext