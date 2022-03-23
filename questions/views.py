from re import T
from turtle import title
from django.shortcuts import render
from numpy import tensordot
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
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter

with open('./questions/saved_model.pickle', 'rb') as handle:
    new_model = pickle.load(handle)

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
            
            ques_objs = Question.objects.filter(type=question_data['type'], grade=question_data['grade'], board=question_data['board'], subject=question_data['subject'])
            tensor_list=[]
            for i in ques_objs:
                tensor_list.append(new_model.encode([i.title], convert_to_tensor=True))
            encoded_sent = new_model.encode([question_data['title']], convert_to_tensor=True)
            
            for i, val in enumerate(tensor_list):
                if cosine_similarity(encoded_sent, val) > .80:
                    similar_data = QuestionSerializer(instance=ques_objs[i])
                    return Response({
                        'message': 'Similar question already exists',
                        'similar_question_data': similar_data.data
                        }, status=status.HTTP_409_CONFLICT)
            
            # embed2 = new_model.encode(sent2, convert_to_tensor=True)
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
            for pair in match_pairs:
                Match.objects.create(
                    question=question,
                    key=pair['key'],
                    value=pair['value']
                )

        return Response({
            "message": "Accepted",
            "question_data": serializer.data
            } ,status=status.HTTP_201_CREATED)


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

class GetSimilarQuestions(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = QuestionSerializer

    def post(self, request, ques_id):
        try:
            ques = Question.objects.get(id=ques_id)
        except ObjectDoesNotExist:
            return Response({
                'message':'Invalid Class Id'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = QuestionSerializer(instance=ques)
        ques_objs = Question.objects.filter(type=serializer.data['type'], grade=serializer.data['grade'], board=serializer.data['board'], subject=serializer.data['subject'])

        if len(ques_objs) > 3:
            ques_objs = ques_objs[:3]
        
        tensor_list=[]
        for i in ques_objs:
            tensor_list.append([new_model.encode([i.title], convert_to_tensor=True), 0, i])
        encoded_sent = new_model.encode([serializer.data['title']], convert_to_tensor=True)
        
        for i in tensor_list:
            i[1] = cosine_similarity(encoded_sent, i[0])
        tensor_list = sorted(tensor_list, key=itemgetter(1))
        objs = [i[2] for i in tensor_list]
        objs_ser = [QuestionSerializer(obj).data for obj in objs]
        # print(tensor_list)

        return Response(objs_ser, status=status.HTTP_200_OK)
