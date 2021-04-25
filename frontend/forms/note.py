from django import forms


class NoteCreateFormStep1(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=100)
    language = forms.CharField(max_length=100)
    subscription_type = forms.CharField(max_length=100)
    # note_type = forms.CharField(max_length=100)


class NoteCreateFormStep2(forms.Form):
    is_private = forms.CharField(max_length=100)
    files = forms.CharField(max_length=10000, required=False)
    drive_url = forms.CharField(max_length=100, required=False)

class NoteCreateFormStep3(forms.Form):
    price_currency = forms.CharField(max_length=100)
    price_value = forms.CharField(max_length=100)
    reading_duration = forms.CharField(max_length=100)
    cover_image = forms.CharField(widget=forms.Textarea, required=False)
    goals = forms.CharField(max_length=10000)

class NoteCreateFormPreview(forms.Form):
    success = forms.CharField(max_length=100, required=False)
