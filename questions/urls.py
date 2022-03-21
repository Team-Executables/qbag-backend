from .api import QuestionViewSet, OptionsViewSet, KeywordViewSet, MatchViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register('questions', QuestionViewSet, 'questions')
router.register('options', OptionsViewSet, 'options')
router.register('keyword', KeywordViewSet, 'keywords')
router.register('match', MatchViewSet, 'matches')

urlpatterns = []

urlpatterns += router.urls