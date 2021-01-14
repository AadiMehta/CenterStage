from django import forms

class LessonCreateFormStep1(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=100)
    no_of_participants = forms.CharField(max_length=100)
    language = forms.CharField(max_length=100)
    no_of_sessions = forms.CharField(max_length=100)


class LessonCreateFormStep2(forms.Form):
    slot_type = forms.CharField(max_length=100)
    start_date = forms.CharField(max_length=100)
    end_date = forms.CharField(max_length=100)
    weekdays = forms.CharField(max_length=100)
    mon_start_time = forms.CharField(max_length=100, required=False)
    mon_end_time = forms.CharField(max_length=100, required=False)
    tue_start_time = forms.CharField(max_length=100, required=False)
    tue_end_time = forms.CharField(max_length=100, required=False)
    wed_start_time = forms.CharField(max_length=100, required=False)
    wed_end_time = forms.CharField(max_length=100, required=False)
    thu_start_time = forms.CharField(max_length=100, required=False)
    thu_end_time = forms.CharField(max_length=100, required=False)
    fri_start_time = forms.CharField(max_length=100, required=False)
    fri_end_time = forms.CharField(max_length=100, required=False)
    sat_start_time = forms.CharField(max_length=100, required=False)
    sat_end_time = forms.CharField(max_length=100, required=False)
    sun_start_time = forms.CharField(max_length=100, required=False)
    sun_end_time = forms.CharField(max_length=100, required=False)
    no_of_sessions = forms.CharField(max_length=100, required=False)
    price_per_session_currency = forms.CharField(max_length=100, required=False)
    price_per_session_value = forms.CharField(max_length=100, required=False)
    weekly_session_currency = forms.CharField(max_length=100, required=False)
    weekly_session_value = forms.CharField(max_length=100, required=False)
    monthly_session_currency = forms.CharField(max_length=100, required=False)
    monthly_session_value = forms.CharField(max_length=100, required=False)


class LessonCreateFormStep3(forms.Form):
    link = forms.CharField(max_length=100)


class LessonCreateFormStep4(forms.Form):
    learn = forms.CharField(max_length=100)


class LessonCreateFormPreview(forms.Form):
    success = forms.CharField(max_length=100, required=False)