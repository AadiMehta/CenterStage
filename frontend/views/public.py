from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.db.models import Avg, Count
from rest_framework.response import Response

from rest_framework import status
from rest_framework import generics
from django.conf import settings
from engine.models import LessonData, LessonStatuses, LessonTypes
from users.models import (
    TeacherProfile, RecommendationChoices, TeacherRating,
    TeacherRecommendations, TeacherFollow, TeacherLike,
    User
)
from engine.serializers import LessonTeacherPageSerializer

from users.authentication import AuthCookieAuthentication

class TeacherPageView(TemplateView):
    template_name = "public/teacherpage.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.get(pk=85)        
        teacher = user.teacher_profile_data

        context['user'] = user
        context['teacher'] = teacher
        lessons = LessonData.objects.filter(
            creator=teacher,
            status=LessonStatuses.ACTIVE,
            is_private=False
        )
        context['BASE_URL'] = settings.BASE_URL
        all_lessons = lessons.order_by('-created_at')
        context['all_lessons'] = LessonTeacherPageSerializer(all_lessons, many=True).data
        ratings = TeacherRating.objects.filter(creator=teacher).aggregate(Avg('rate'))
        context['avg_rating'] = round(ratings.get('rate__avg') or 0, 1)
        context['years_of_exp'] = teacher.year_of_experience
        student_count = 0
        for lesson in lessons:
            student_count += lesson.enrollments.count()
        context['student_count'] = student_count
        context['sharing_link'] = '{}://{}.{}'.format(settings.SCHEME, teacher.subdomain, settings.SITE_URL)
        most_popular_lessons = lessons.annotate(count=Count('enrollments')).order_by('count')
        context['most_popular_lessons'] = LessonTeacherPageSerializer(most_popular_lessons, many=True).data
        one_on_one_lessons = lessons.filter(lesson_type=LessonTypes.ONE_ON_ONE).order_by('-created_at')
        context['one_on_one_lessons'] = LessonTeacherPageSerializer(one_on_one_lessons, many=True).data
        group_lessons = lessons.filter(lesson_type=LessonTypes.GROUP).order_by('-created_at')
        context['group_lessons'] = LessonTeacherPageSerializer(group_lessons, many=True).data
        context['reviews'] = teacher.ratings.all()

        liked = False
        followed = False
        user_recommended = []

        if not self.request.user.is_anonymous:
            liked = TeacherLike.objects.filter(
                user=request.user,
                creator=teacher
            ).exists()
            followed = TeacherFollow.objects.filter(
                user=request.user,
                creator=teacher
            ).exists()

            for recommendation_type in recommendations:
                recommended = TeacherRecommendations.objects.filter(
                    user=request.user, creator=teacher, recommendation_type=recommendation_type
                ).exists()
                if recommended:
                    user_recommended.append(recommendation_type)

        recommendations = teacher.recommendations.all()
        total_recommendations = {
            'LESSON_QUALITY': recommendations.filter(recommendation_type=RecommendationChoices.LESSON_QUALITY),
            'LESSON_CONTENT': recommendations.filter(recommendation_type=RecommendationChoices.LESSON_CONTENT),
            'LESSON_STRUCTURE': recommendations.filter(recommendation_type=RecommendationChoices.LESSON_STRUCTURE),
            'TEACHER_HELPFULNESS': recommendations.filter(recommendation_type=RecommendationChoices.TEACHER_HELPFULNESS),
            'TEACHER_COMMUNICATION': recommendations.filter(recommendation_type=RecommendationChoices.TEACHER_COMMUNICATION),
            'TEACHER_KNOWLEDGE': recommendations.filter(recommendation_type=RecommendationChoices.TEACHER_KNOWLEDGE),
        }
        context['recommendations'] = total_recommendations
        return context
    
    def dispatch(self, request, *args, **kwargs):
        user = User.objects.get(pk=85)
        teacher = TeacherProfile.objects.filter(user=user).first()
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
    authentication_classes = [AuthCookieAuthentication]    
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        teacher_id = data.get('teacher_id')
        teacher = TeacherProfile.objects.get(pk=teacher_id)
        
        recommendation_type = data.get('recommendation_type')
        try:
            TeacherRecommendations.objects.get(
                creator=teacher,
                user=user,
                recommendation_type=recommendation_type
            ).delete()
            msg = 'Recommendation Removal Successful'
            action = 'removed'
        except TeacherRecommendations.DoesNotExist:
            TeacherRecommendations(
                creator=teacher,
                user=user,
                recommendation_type=recommendation_type
            ).save()
            msg = 'Recommendation Successful'
            action = 'added'
        return Response(dict({"msg": msg, "action": action}), status=status.HTTP_200_OK)


class FollowTeacherAPIView(generics.CreateAPIView):
    """
    Follow Teacher
    """
    authentication_classes = [AuthCookieAuthentication]    
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        teacher_id = data.get('teacher_id')
        teacher = TeacherProfile.objects.get(pk=teacher_id)
        
        try:
            TeacherFollow.objects.get(
                creator=teacher,
                user=user
            ).delete()
            msg = 'Follower Removal Successful'
            action = 'removed'
        except TeacherFollow.DoesNotExist:
            TeacherFollow(
                creator=teacher,
                user=user
            ).save()
            msg = 'Followed Successful'
            action = 'added'
        return Response(dict({"msg": msg, "action": action}), status=status.HTTP_200_OK)


class LikeTeacherAPIView(generics.CreateAPIView):
    """
    Like Teacher
    """
    authentication_classes = [AuthCookieAuthentication]    
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        teacher_id = data.get('teacher_id')
        teacher = TeacherProfile.objects.get(pk=teacher_id)
        
        try:
            TeacherLike.objects.get(
                creator=teacher,
                user=user
            ).delete()
            msg = 'Like Removal Successful'
            action = 'removed'
        except TeacherLike.DoesNotExist:
            TeacherLike(
                creator=teacher,
                user=user
            ).save()
            msg = 'Liked Successful'
            action = 'added'
        return Response(dict({"msg": msg, "action": action}), status=status.HTTP_200_OK)



class SubmitTeacherReview(generics.CreateAPIView):
    """
    Submit Review For Teacher
    """
    authentication_classes = [AuthCookieAuthentication]    
    permission_classes = []

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        review = data.get('review')
        rate = data.get('rate')
        recommendations = data.get('recommendations')
        teacher_id = data.get('teacher_id')
        teacher = TeacherProfile.objects.get(pk=teacher_id)

        rating, created = TeacherRating.objects.update_or_create(
            creator=teacher,
            user=user,
            rate=rate,
            review=review
        )
        TeacherRecommendations.objects.filter(
            creator=teacher,
            user=user
        ).delete()

        for recommendation_type in recommendations:
            TeacherRecommendations(
                creator=teacher,
                user=user,
                recommendation_type=recommendation_type
            ).save()

        if created:
            return Response(dict({'msg': 'Rating Submitted Successfull'}), status=status.HTTP_201_CREATED)
        return Response(dict({'msg': 'Rating Updated Successfull'}), status=status.HTTP_200_OK)
