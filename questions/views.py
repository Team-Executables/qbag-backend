from re import T
from django.shortcuts import render
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import os
from django.conf import settings
from datetime import datetime
from qbag_api.permissions import IsTeacher, IsOther
from .models import *
from .serializers import *

class createQuestionsView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = QuestionSerializer

    def post(self, request):
        data = request.data

        question_data={}
        question_data['type']=data.get('type')
        question_data['setter']=request.user.pk
        question_data['grade']=data.get('grade')
        question_data['board']=data.get('board')
        question_data['marks']=data.get('marks')
        question_data['difficulty']=data.get('difficulty')
        question_data['subject']=data.get('subject')
        question_data['title']=data.get('title')

        keywords = data.get('keywords')

        serializer = self.serializer_class(data=question_data)
        if serializer.is_valid(raise_exception=True):
            question = serializer.save()

        for keyword in keywords:
            Keyword.objects.create(
                question=question,
                keyword=keyword
            )
        
        if question_data['type'] != "d":
            options = data.get("options")
            for option in options:
                Option.objects.create(
                    question=question,
                    option=option['option'],
                    correct=option['correct']
                )
        else:
            match_pairs = data.get("match")
            print("Inside else")
            for pair in match_pairs:
                Match.objects.create(
                    question=question,
                    key=pair['key'],
                    value=pair['value']
                )

        return Response({"message": "Accepted"} ,status=status.HTTP_201_CREATED)

# from qbag_api.permissions import IsOther, IsTeacher
# from .models import Question, Option, Match, Keyword
# from .serializers import QuestionSerializer, OptionSerializer, KeywordSerializer, MatchSerializer
# from rest_framework import generics, permissions,  status
# from django.core.exceptions import ObjectDoesNotExist
# from rest_framework.response import Response

class GetQuestionView(generics.GenericAPIView):
    permission_classes = (IsTeacher,)
    serializer_class = QuestionSerializer

    def get(self, request, ques_id):
        try:
            ques = Question.objects.get(id=ques_id)
        except ObjectDoesNotExist:
            return Response({
                'message':'Invalid Class Id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = QuestionSerializer(instance=ques)
        keyword_obj = Keyword.objects.filter(question=ques)
        keyword_ser = KeywordSerializer(instance=keyword_obj, many=True)

        if serializer.data['type'] != 'd':
            opt_obj = Option.objects.filter(question=ques)
            opt_ser = OptionSerializer(instance=opt_obj, many=True)
            data = {
                'question_data': serializer.data,
                'keyword_data': keyword_ser.data,
                'option_data': opt_ser.data
            }
        else:
            match_obj = Match.objects.filter(question=ques)
            match_ser = MatchSerializer(instance=match_obj, many=True)
            data = {
                'question_data': serializer.data,
                'keyword_data': keyword_ser.data,
                'match_data': match_ser.data
            }

        return Response(data, status=status.HTTP_200_OK)


class RetreiveQuestionView(generics.GenericAPIView):
    permission_classes = (IsTeacher,)
    serializer_class = QuestionSerializer
    
    def post(self, request):
        data = request.data
        all_ques = list()
        
        easy_ques = Question.objects.filter(
            difficulty='a', 
            board=data.get('board'), 
            grade=data.get('grade')
        )[:int(data.get('easy'))]
        all_ques.append(easy_ques)
        
        medium_ques = Question.objects.filter(
            difficulty='b',
            board=data.get('board'),
            grade=data.get('grade')
        )[:int(data.get('medium'))]
        all_ques.append(medium_ques)
        
        hard_ques = Question.objects.filter(
            difficulty='c',
            board=data.get('board'), 
            grade=data.get('grade')
        )[:int(data.get('hard'))]
        all_ques.append(hard_ques)
        
        questions = list()
        
        for diff in all_ques:
            for ques in diff:
                serializer = QuestionSerializer(instance=ques)
                keyword_obj = Keyword.objects.filter(question=ques)
                keyword_ser = KeywordSerializer(instance=keyword_obj, many=True)

                if serializer.data['type'] != 'd':
                    opt_obj = Option.objects.filter(question=ques)
                    opt_ser = OptionSerializer(instance=opt_obj, many=True)
                    questions.append({
                        'question_data': serializer.data,
                        'keyword_data': keyword_ser.data,
                        'option_data': opt_ser.data
                    })
                else:
                    match_obj = Match.objects.filter(question=ques)
                    match_ser = MatchSerializer(instance=match_obj, many=True)
                    questions.append({
                        'question_data': serializer.data,
                        'keyword_data': keyword_ser.data,
                        'match_data': match_ser.data
                    })
                

        return Response(questions, status=status.HTTP_200_OK)
        
        
        
        
        

'''
return Response(
    {
        'question_data': ques_ser.data,
        'match_data': match_ser.data
    }
)
'''




