import logging
from django.utils import timezone

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Avg, Count
from formtools.wizard.views import SessionWizardView
from frontend.forms.booking import BookLessonForm1, BookLessonForm2, BookLessonForm3
from engine.serializers import LessonSlotSerializer
from engine.models import LessonData, LessonSlots, EnrollmentChoices, Enrollment, LessonLikes
from users.models import StudentProfile, UserTypes, PaymentTypes
from engine.serializers import LessonTeacherPageSerializer
from django.db.models import Q
from django.views import View
from django.urls import reverse, reverse_lazy

from payments.models import LessonOrder
from frontend.constants import currency_labels

logger = logging.getLogger(__name__)


class BookLessonWizard(LoginRequiredMixin, SessionWizardView):
    TEMPLATES = {
        "preview": "booking/preview.html",
        "payment": "booking/payment.html",
        "checkout": "booking/pay_checkout.html",
    }

    FORMS = [
        ("preview", BookLessonForm1),
        ("payment", BookLessonForm2),
        ("checkout", BookLessonForm3),
    ]

    def get_context_data(self, form, *args, **kwargs):
        context = super(BookLessonWizard, self).get_context_data(form=form, **kwargs)
        data = self.get_all_cleaned_data()
        context.update({'form_data': data})
        context['BASE_URL'] = settings.BASE_URL

        lesson_uuid = self.request.resolver_match.kwargs.get('lesson_uuid')
        lesson = get_object_or_404(LessonData, lesson_uuid=lesson_uuid)
        context['lesson'] = LessonTeacherPageSerializer(lesson).data
        user = self.request.user

        if user.user_type == UserTypes.STUDENT_USER:
            is_student_enrolled = lesson.is_student_enrolled(user.student_profile_data)
            context['is_student_enrolled'] = is_student_enrolled

        slots = lesson.slots.all()
        upcoming_slots = lesson.slots.all().filter(Q(lesson_from__gt=timezone.now()))

        lesson_date_slots = []
        lesson_time_slots = []
        for slot in upcoming_slots:
            lesson_date_slots.append(slot.lesson_from.strftime('%Y-%m-%d'))
            lesson_time_slots.append([
                slot.lesson_from.strftime('%H:%M %p'),
                slot.lesson_to.strftime('%H:%M %p'),
                slot.session_no,
                slot.lesson_from.strftime('%a, %d %b'),
            ])
        context['lesson_date_slots'] = lesson_date_slots
        context['lesson_time_slots'] = lesson_time_slots

        selected_slots = []
        if data:
            set_to_all_sessions = data.get('set_to_all_sessions')
            if set_to_all_sessions:
                selected_slots = upcoming_slots
            else:
                time_slot = data.get('time_slot')
                selected_slots = upcoming_slots.filter(session_no=time_slot)

        selected_time_slots = []
        for slot in selected_slots:
            selected_time_slots.append([
                slot.lesson_from.strftime('%H:%M %p'),
                slot.lesson_to.strftime('%H:%M %p'),
                slot.session_no,
                slot.lesson_from.strftime('%a, %d %b'),
            ])
        context['selected_slots'] = selected_slots
        context['selected_time_slots'] = selected_time_slots

        ratings = lesson.ratings.all().aggregate(Avg('rate'))
        context['avg_rating'] = round(ratings.get('rate__avg') or 0, 1)

        context['enrollments'] = lesson.enrollments.all()
        context['reviews'] = lesson.ratings.all()
        context['seats_remaining'] = lesson.seats_remaining()
        context['total_price'] = len(selected_slots) * int(lesson.price['value'])
        context['total_lesson_price'] = len(upcoming_slots) * int(lesson.price['value'])
        context['currency_info'] = currency_labels[lesson.price['currency']]

        more_lessons_slots = LessonSlots.objects.filter(
            creator=lesson.creator
        ).distinct('lesson').exclude(
            lesson__lesson_uuid=lesson.lesson_uuid
        )
        more_lessons = []
        for mslots in more_lessons_slots:
            more_lessons.append(mslots.lesson)
        context['more_lessons'] = LessonTeacherPageSerializer(more_lessons, many=True).data

        return context

    def dispatch(self, request, *args, **kwargs):
        return super(BookLessonWizard, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        final_data = {}
        for form in form_list:
            final_data.update(form.cleaned_data)
        lesson_uuid = self.request.resolver_match.kwargs.get('lesson_uuid')
        lesson = LessonData.objects.get(lesson_uuid=lesson_uuid)

        try:
            student = StudentProfile.objects.get(user=self.request.user)
        except StudentProfile.DoesNotExist:
            return redirect(reverse('book-lesson', kwargs={'lesson_uuid': lesson.lesson_uuid}))

        selected_slots = []
        set_to_all_sessions = final_data.get('set_to_all_sessions')
        upcoming_slots = lesson.slots.all().filter(Q(lesson_from__gt=timezone.now()))
        if set_to_all_sessions:
            selected_slots = upcoming_slots
        else:
            time_slot = final_data.get('time_slot')
            selected_slots = upcoming_slots.filter(session_no=time_slot)

        selected_time_slots = []
        for slot in selected_slots:
            selected_time_slots.append([
                slot.lesson_from.strftime('%H:%M %p'),
                slot.lesson_to.strftime('%H:%M %p'),
                slot.session_no,
                slot.lesson_from.strftime('%a, %d %b'),
            ])

        final_data['selected_slots'] = selected_slots
        final_data['student'] = student
        return self.book_lesson(final_data)

    def book_lesson(self, form_data):
        """
        create new order
        """
        try:
            user = self.request.user
            lesson_uuid = self.request.resolver_match.kwargs.get('lesson_uuid')
            lesson = LessonData.objects.get(lesson_uuid=lesson_uuid)
            student = form_data.get('student')
            order_id = form_data.get('order_id')
            order_obj = get_object_or_404(LessonOrder, order_id=order_id)

            # check for order status
            if not order_obj.is_completed:
                pass

            return render(self.request, 'booking/done.html', {'lesson': lesson})
        except Exception as e:
            logger.exception(e)
            return redirect(reverse('book-lesson', kwargs={'lesson_uuid': lesson.lesson_uuid}))


class BookLessonPyament(LoginRequiredMixin, View):
    form_class = BookLessonForm3

    def get_lesson(self):
        return get_object_or_404(
            LessonData, lesson_uuid=self.kwargs.get("lesson_uuid")
        )

    def get(self, request, *args, **kwargs):
        lesson = self.get_lesson()
        user = self.request.user
        form = self.form_class()

        order_data = {
            "lesson": lesson,
            "student": user.student_profile_data,
        }
        order_obj, created = LessonOrder.objects.new_or_get(order_data)

        if order_obj.is_completed:
            return redirect(reverse('book-lesson'))

        return render(request, "booking/pay_checkout.html", {
            "order": order_obj,
            "lesson": lesson,
            "form": form
        })
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        lesson = self.get_lesson()

        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            order_obj = LessonOrder.objects.get(order_id=order_id)
            return render(self.request, 'booking/done.html', {'lesson': lesson})
        return render(self.request, 'booking/done.html', {'lesson': lesson})
