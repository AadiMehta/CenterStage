from django import forms


class ScheduleCreateFormStep1(forms.Form):
    name = forms.CharField(max_length=100)
    invitees = forms.CharField(max_length=100)
    session_type = forms.CharField(max_length=100)


class ScheduleCreateFormStep2(forms.Form):
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
    no_of_sessions = forms.CharField(max_length=100)
    price_type = forms.CharField(max_length=100)
    price_currency = forms.CharField(max_length=100)
    price_value = forms.CharField(max_length=100)
    total_price = forms.CharField(max_length=100)


class ScheduleCreateFormPreview(forms.Form):
    success = forms.CharField(max_length=100, required=False)
