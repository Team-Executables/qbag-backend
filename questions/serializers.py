from rest_framework import serializers
from .models import (
    Question,
    Option,
    Match,
    Keyword
)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = "__all__"
    
    def create(self, validated_data):
        type = validated_data["type"]
        setter = validated_data["setter"]
        grade = validated_data["grade"]
        board = validated_data["board"]
        marks = validated_data["marks"]
        difficulty = validated_data["difficulty"]
        subject = validated_data["subject"]
        title = validated_data["title"]
        keywords = validated_data["keywords"]
        
        question = Question.objects.create(
            type,
            setter,
            grade,
            board,
            marks,
            difficulty,
            subject,
            title,
        )
        
        for keyword in keywords:
            Keyword.objects.create(
                question,
                keyword
            )
        
        if type != "d":
            options = validated_data.pop["options"]
            for option in options:
                Option.objects.create(
                    question,
                    option.option,
                    option.correct
                )
        else:
            match_pairs = validated_data.pop["match"]
            
            for pair in match_pairs:
                Match.objects.create(
                    question,
                    pair.key,
                    pair.value
                )


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
