from .models import (
    Question,
    Option,
    Match,
    Keyword
)
from .serializers import (
    QuestionSerializer,
    OptionSerializer,
    KeywordSerializer,
    MatchSerializer
)
from rest_framework import viewsets, permissions


class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    serializer_class = QuestionSerializer

    def get_queryset(self):
        question_id = self.request.query_params["question_id"]
        if question_id:
            return Question.objects.get(id=question_id)

    def perform_create(self, serializer):
        serializer.save(setter=self.request.user)


class OptionsViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    serializer_class = OptionSerializer

    def get_queryset(self):
        question = self.request.query_params["question_id"]
        return Option.objects.filter(question=question)
    
    
class KeywordViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    serializer_class = KeywordSerializer

    def get_queryset(self):
        question = self.request.query_params["question_id"]
        return Keyword.objects.filter(question=question)
    

class MatchViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]
    serializer_class = MatchSerializer

    def get_queryset(self):
        question = self.request.query_params["question_id"]
        return Match.objects.filter(question=question)
