from django import forms


class LessonCreateFormStep1(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField(max_length=100)
    no_of_participants = forms.CharField(max_length=100)
    language = forms.CharField(max_length=500)
    session_type = forms.CharField(max_length=100)
    lesson_type = forms.CharField(max_length=100)


class LessonCreateFormStep2(forms.Form):
    slot_type = forms.CharField(max_length=100)
    start_date = forms.CharField(max_length=100)
    end_date = forms.CharField(max_length=100)
    weekdays = forms.CharField(max_length=100)
    timezone = forms.CharField(max_length=100)
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
    no_of_sessions = forms.CharField(max_length=100)
    price_type = forms.CharField(max_length=100)
    price_currency = forms.CharField(max_length=100)
    price_value = forms.CharField(max_length=100)
    total_price = forms.CharField(max_length=100)


class LessonCreateFormStep3(forms.Form):
    is_private = forms.CharField(max_length=100)
    cover_image = forms.CharField(widget=forms.Textarea, required=False)
    video_link = forms.CharField(max_length=500, required=False)


class LessonCreateFormStep4(forms.Form):
    goals = forms.CharField(max_length=10000)
    requirements = forms.CharField(max_length=10000)
    files = forms.CharField(max_length=10000)


class LessonCreateFormPreview(forms.Form):
    success = forms.CharField(max_length=100, required=False)
