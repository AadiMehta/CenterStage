import logging
from django.shortcuts import redirect, render
from formtools.wizard.views import SessionWizardView
from frontend.forms.booking import BookLessonForm1, BookLessonForm2
from engine.serializers import LessonSlotSerializer
from engine.models import LessonData, LessonSlots, EnrollmentChoices, Enrollment
from users.models import StudentProfile

logger = logging.getLogger(__name__)


class BookLessonWizard(SessionWizardView):
    TEMPLATES = {
        "preview": "booking/preview.html",
        "payment": "booking/payment.html"
    }

    FORMS = [
        ("preview", BookLessonForm1),
        ("payment", BookLessonForm2),
    ]

    def get_context_data(self, form, *args, **kwargs):
        context = super(BookLessonWizard, self).get_context_data(form=form, **kwargs)
        data = self.get_all_cleaned_data()
        context.update({'form_data': data})
        lesson_uuid = self.request.resolver_match.kwargs.get('lesson_uuid')
        lesson = LessonData.objects.get(lesson_uuid=lesson_uuid)
        context['lesson'] = lesson
        lesson_date_slots = []
        lesson_time_slots = []
        lesson_time_slot_nos = []
        first_slot = lesson.slots.first()
        for slot in lesson.slots.all():
            lesson_date_slots.append(slot.lesson_from.strftime('%Y-%m-%d'))
            lesson_time_slot_nos.append(slot.session_no)
            lesson_time_slots.append([
                slot.lesson_from.strftime('%H:%M %p'),
                slot.lesson_to.strftime('%H:%M %p'),
                slot.session_no,
                slot.lesson_from.strftime('%a, %d %b'),
            ])
        context['no_of_slots'] = lesson.slots.count()
        context['slot'] = LessonSlotSerializer(first_slot).data
        context['lesson_date_slots'] = lesson_date_slots
        context['lesson_time_slots'] = lesson_time_slots
        return context

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/')
        else:
            return super(BookLessonWizard, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        final_data = {}
        for form in form_list:
            final_data.update(form.cleaned_data)
        time_slot = final_data.get('time_slot')
        final_data['time_slot'] = int(time_slot) if time_slot else 1
        return self.book_lesson(final_data)

    def book_lesson(self, form_data):
        try:
            user = self.request.user
            lesson_uuid = self.request.resolver_match.kwargs.get('lesson_uuid')
            student = StudentProfile.objects.get(user=user)
            lesson = LessonData.objects.get(lesson_uuid=lesson_uuid)
            lesson_slot = LessonSlots.objects.get(session_no=form_data.get('time_slot'), lesson=lesson)

            enrollment = Enrollment.objects.filter(student=student, lesson=lesson, lessonslot=lesson_slot).first()
            if not enrollment:
                enrollment = Enrollment(student=student, lesson=lesson, lessonslot=lesson_slot,
                                        status=EnrollmentChoices.ACTIVE)
                enrollment.save()
            return render(self.request, 'booking/done.html', {
                'enrollment': enrollment
            })
        except Exception as e:
            logger.exception(e)
            return redirect('book-lesson')
