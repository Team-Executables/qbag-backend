from dataclasses import field
from math import fabs
from operator import mod
from pyexpat import model
from statistics import mode
from rest_framework import serializers
from .models import (
    Paper,
    Question,
    Option,
    Match,
    Keyword,
    QuestionPaper,
    Vote
)
from .models import File


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"

class GetQuestionSerializer(serializers.ModelSerializer):
    setbyTeacher = serializers.SerializerMethodField('is_set_by_teacher')

    def is_set_by_teacher(self, obj):
        if obj.setter.user_type == "teacher":
            return True
        else:
            return False

    class Meta:
        model = Question
        fields = ['type', 'setter', 'grade', 'board', 'marks', 'difficulty', 'subject', 'title', 'setbyTeacher', 'id']
        

class PaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paper
        fields = "__all__"


class QuestionPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionPaper
        fields = "__all__"


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = "__all__"
        

class KeywordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Keyword
        fields = "__all__"
        

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = "__all__"


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = "__all__"


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = '__all__'
