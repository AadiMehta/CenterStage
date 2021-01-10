from django import forms


class LessonCreateFormStep1(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=100)
    no_of_participants = forms.CharField(max_length=100)
    language = forms.CharField(max_length=100)
    no_of_sessions = forms.CharField(max_length=100)


class LessonCreateFormStep2(forms.Form):
    slot_type = forms.CharField(max_length=100)
    no_of_sessions = forms.CharField(max_length=100)


class LessonCreateFormStep3(forms.Form):
    link = forms.CharField(max_length=100)


class LessonCreateFormStep4(forms.Form):
    learn = forms.CharField(max_length=100)


class LessonCreateFormPreview(forms.Form):
    success = forms.CharField(max_length=100, required=False)