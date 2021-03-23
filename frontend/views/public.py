from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.db.models import Avg, Count
from rest_framework import status
from rest_framework import generics
from django.conf import settings
from engine.models import LessonData, LessonStatuses, LessonTypes
from users.models import TeacherProfile, RecommendationChoices, TeacherRating, TeacherRecommendations


class TeacherPageView(TemplateView):
    template_name = "public/teacherpage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        teacher = self.request.user.teacher_profile_data
        context['teacher'] = teacher
        lessons = LessonData.objects.filter(
            creator=teacher,
            status=LessonStatuses.ACTIVE,
            is_private=False
        )
        context['BASE_URL'] = settings.BASE_URL
        context['all_lessons'] = lessons.order_by('-created_at')
        ratings = TeacherRating.objects.filter(creator=teacher).aggregate(Avg('rate'))
        context['avg_rating'] = round(ratings.get('rate__avg') or 0, 1)
        context['years_of_exp'] = teacher.year_of_experience
        student_count = 0
        for lesson in lessons:
            student_count += lesson.enrollments.count()
        context['student_count'] = student_count
        context['sharing_link'] = '{}://{}.{}'.format(settings.SCHEME, teacher.subdomain, settings.SITE_URL)
        context['most_popular_lessons'] = lessons.annotate(count=Count('enrollments')).order_by('count')
        context['one_on_one_lessons'] = lessons.filter(lesson_type=LessonTypes.ONE_ON_ONE).order_by('-created_at')
        context['group_lessons'] = lessons.filter(lesson_type=LessonTypes.GROUP).order_by('-created_at')
        context['reviews'] = teacher.ratings.all()

        recommendations = teacher.recommendations.all()
        context['recommendations'] = {
            'LESSON_QUALITY': recommendations.filter(recommendation_type=RecommendationChoices.LESSON_QUALITY),
            'LESSON_CONTENT': recommendations.filter(recommendation_type=RecommendationChoices.LESSON_CONTENT),
            'LESSON_STRUCTURE': recommendations.filter(recommendation_type=RecommendationChoices.LESSON_STRUCTURE),
            'TEACHER_HELPFULNESS': recommendations.filter(recommendation_type=RecommendationChoices.TEACHER_HELPFULNESS),
            'TEACHER_COMMUNICATION': recommendations.filter(recommendation_type=RecommendationChoices.TEACHER_COMMUNICATION),
            'TEACHER_KNOWLEDGE': recommendations.filter(recommendation_type=RecommendationChoices.TEACHER_KNOWLEDGE),
        }
        return context
    
    def dispatch(self, request, *args, **kwargs):
        teacher = TeacherProfile.objects.filter(user=self.request.user).first()
        if not teacher:
            return redirect('homepage')
        return super(TeacherPageView, self).dispatch(request, *args, **kwargs)



class LessonPageView(TemplateView):
    template_name = "public/teacherpage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class RecommendTeacherAPIView(generics.CreateAPIView):
    """
    Recommend with single recommendation type
    """
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        teacher_subdomain = data.get('teacher_subdomain')
        recommendation_type = data.get('recommendation_type')

        teacher = TeacherProfile.objects.get(subdomain=teacher_subdomain)
        try:
            TeacherRecommendations.objects.get(
                creator=teacher,
                user=user,
                recommendation_type=recommendation_type
            ).delete()
            action = 'Recommendation Removal Successful'
        except TeacherRecommendations.DoesNotExist:
            TeacherRecommendations.objects.filter(
                creator=teacher,
                user=user,
                recommendation_type=recommendation_type
            ).save()
            action = 'Recommendation Successful'
        return Response(dict({"msg": action}), status=status.HTTP_200_OK)



class SubmitTeacherReview(generics.CreateAPIView):
    """
    Submit Review For Teacher
    """
    authentication_classes = []
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = self.request.user
        data = request.data
        review = data.get('review')
        rate = data.get('rate')
        recommendations = data.get('recommendations')
        teacher = TeacherProfile.objects.get(subdomain=teacher_subdomain)

        rating, created = TeacherRating.objects.update_or_create(
            creator=teacher,
            user=user,
            rate=rate,
            review=review
        )

        for recommendation_type in recommendations:
            try:
                TeacherRecommendations.objects.get(
                    creator=teacher,
                    user=user,
                    recommendation_type=recommendation_type
                ).delete()
            except TeacherRecommendations.DoesNotExist:
                TeacherRecommendations.objects.filter(
                    creator=teacher,
                    user=user,
                    recommendation_type=recommendation_type
                ).save()

        if created:
            return Response(dict({'msg': 'Rating Submitted Successfull'}), status=status.HTTP_201_CREATED)
        return Response(dict({'msg': 'Rating Updated Successfull'}), status=status.HTTP_200_OK)
