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




