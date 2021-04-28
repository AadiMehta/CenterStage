from django import forms


class BookLessonForm1(forms.Form):
    date_slot = forms.CharField(max_length=100, required=False)
    time_slot = forms.CharField(max_length=100, required=False)
    set_to_all_sessions = forms.CharField(max_length=100, required=False)


class BookLessonForm2(forms.Form):
    payment_type = forms.CharField(max_length=100)

class BookLessonForm3(forms.Form):
    order_id = forms.CharField(max_length=120)
    payment_type = forms.CharField(max_length=100)
