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

        question_data = {}
        question_data['type'] = data.get('type')
        question_data['setter'] = request.user.pk
        question_data['grade'] = data.get('grade')
        question_data['board'] = data.get('board')
        question_data['marks'] = data.get('marks')
        question_data['difficulty'] = data.get('difficulty')
        question_data['subject'] = data.get('subject')
        question_data['title'] = data.get('title')
        question_data['medium'] = data.get('medium')

        keywords = data.get('keywords')

        serializer = self.serializer_class(data=question_data)
        if serializer.is_valid(raise_exception=True):
            if question_data['type'] != "d":
                ques_objs = Question.objects.filter(
                    type=question_data['type'], grade=question_data['grade'], board=question_data['board'], subject=question_data['subject'], medium=question_data['medium'])
                tensor_list = []
                for i in ques_objs:
                    tensor_list.append(new_model.encode(
                        [i.title], convert_to_tensor=True))
                encoded_sent = new_model.encode(
                    [question_data['title']], convert_to_tensor=True)

                for i, val in enumerate(tensor_list):
                    if cosine_similarity(encoded_sent, val) > .80:
                        similar_data = QuestionSerializer(
                            instance=ques_objs[i])
                        return Response({
                            'message': 'Similar question already exists',
                            'similar_question_data': similar_data.data
                        }, status=status.HTTP_409_CONFLICT)

                # embed2 = new_model.encode(sent2, convert_to_tensor=True)
                question = serializer.save()
            else:
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
        }, status=status.HTTP_201_CREATED)


class GetQuestionView(generics.GenericAPIView):
    permission_classes = (IsTeacher,)
    serializer_class = GetQuestionSerializer

    def get(self, request, ques_id):
        try:
            ques = Question.objects.get(id=ques_id)
        except ObjectDoesNotExist:
            return Response({
                'message': 'Invalid Class Id'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = GetQuestionSerializer(instance=ques)
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
    serializer_class = GetQuestionSerializer

    def post(self, request):
        data = request.data
        all_ques = list()

        easy_ques = Question.objects.filter(
            difficulty='a',
            board=data.get('board'),
            medium=data.get('langMedium'),
            subject=data.get('subject'),
            grade=data.get('grade')
        )[:int(data.get('easy'))]
        all_ques.append(easy_ques)

        medium_ques = Question.objects.filter(
            difficulty='b',
            board=data.get('board'),
            medium=data.get('langMedium'),
            subject=data.get('subject'),
            grade=data.get('grade')
        )[:int(data.get('medium'))]
        all_ques.append(medium_ques)

        hard_ques = Question.objects.filter(
            difficulty='c',
            board=data.get('board'),
            medium=data.get('langMedium'),
            subject=data.get('subject'),
            grade=data.get('grade')
        )[:int(data.get('hard'))]
        all_ques.append(hard_ques)

        questions = list()

        for diff in all_ques:
            for ques in diff:
                serializer = GetQuestionSerializer(instance=ques)
                keyword_obj = Keyword.objects.filter(question=ques)
                keyword_ser = KeywordSerializer(
                    instance=keyword_obj, many=True)

                if serializer.data['type'] != 'd':
                    opt_obj = Option.objects.filter(question=ques)
                    opt_ser = OptionSerializer(instance=opt_obj, many=True)
                    upvote = Vote.objects.filter(question=ques, vote=1).count()
                    downvote = Vote.objects.filter(question=ques, vote=0).count()
                    questions.append({
                        'id': ques.id,
                        'upvote': upvote,
                        'downvote': downvote,
                        'question_data': serializer.data,
                        'keyword_data': keyword_ser.data,
                        'option_data': opt_ser.data,
                    })
                else:
                    match_obj = Match.objects.filter(question=ques)
                    match_ser = MatchSerializer(instance=match_obj, many=True)
                    upvote = Vote.objects.filter(question=ques, vote=1).count()
                    downvote = Vote.objects.filter(question=ques, vote=0).count()
                    questions.append({
                        'id': ques.id,
                        'upvote': upvote,
                        'downvote': downvote,
                        'question_data': serializer.data,
                        'keyword_data': keyword_ser.data,
                        'match_data': match_ser.data,
                    })

        return Response(questions, status=status.HTTP_200_OK)


class GetSimilarQuestions(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = GetQuestionSerializer

    def post(self, request, ques_id):
        try:
            ques = Question.objects.get(id=ques_id)
        except ObjectDoesNotExist:
            return Response({
                'message': 'Invalid Class Id'
            }, status=status.HTTP_400_BAD_REQUEST)
        serializer = GetQuestionSerializer(instance=ques)
        ques_objs = Question.objects.filter(
            type=serializer.data['type'], grade=serializer.data['grade'], board=serializer.data['board'], subject=serializer.data['subject'])

        if len(ques_objs) > 3:
            ques_objs = ques_objs[:3]

        tensor_list = []
        for i in ques_objs:
            tensor_list.append(
                [new_model.encode([i.title], convert_to_tensor=True), 0, i])
        encoded_sent = new_model.encode(
            [serializer.data['title']], convert_to_tensor=True)

        for i in tensor_list:
            i[1] = cosine_similarity(encoded_sent, i[0])
        tensor_list = sorted(tensor_list, key=itemgetter(1))
        objs = [i[2] for i in tensor_list]
        objs_ser = [GetQuestionSerializer(obj).data for obj in objs]
        # print(tensor_list)

        return Response(objs_ser, status=status.HTTP_200_OK)


# Voting Views
class VotingView(generics.GenericAPIView):
    permission_classes = (IsTeacher, )
    serializer_class = VoteSerializer

    def post(self, request):
        data = request.data

        vote_data = {}
        vote_data['teacher'] = request.user.teacher.id
        vote_data['vote'] = data.get('vote')
        vote_data['question'] = data.get('question')

        question = Question.objects.get(id=vote_data['question'])
        if int(question.setter.id) == int(request.user.id):
            return Response({
                "message": "You cannot vote",
            }, status=status.HTTP_401_UNAUTHORIZED)

        if Vote.objects.filter(teacher=vote_data['teacher'], question=vote_data['question']).exists():
            Vote.objects.filter(teacher=vote_data['teacher'], question=vote_data['question']).update(
                vote=vote_data['vote'])
        else:
            serializer = self.serializer_class(data=vote_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        value = "Upvoted" if vote_data['vote'] == '1' else "Downvoted"

        threshold = 200

        if value == "Downvoted":
            total_votes = Vote.objects.filter(
                question=vote_data['question']).count()
            down_votes = Vote.objects.filter(
                question=vote_data['question'], vote=0).count()

            if total_votes > threshold and down_votes > total_votes / 2:
                Question.objects.filter(id=vote_data['question']).delete()

        return Response({
            "message": "Voted",
            "vote_data": value
        }, status=status.HTTP_201_CREATED)
        

# Create Question Paper View
class PaperView(generics.GenericAPIView):
    permission_classes = (IsTeacher, )
    serializer_class = PaperSerializer

    def post(self, request):
        data = request.data
        questions = data['questions']
        questions_list = [int(i) for i in questions.split(',')]
        teacher = request.user.teacher.id
        
        paper = {
            'teacher': teacher
        }
        serializer = self.serializer_class(data=paper)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            paper_id = serializer.data['id']
            
            for question in questions_list:
                try:
                    QuestionPaper.objects.create(
                        paper=Paper.objects.get(id=paper_id), 
                        question=Question.objects.get(id=question)
                    )
                except Exception as e:
                    return Response({
                        "message": "Unable to add questions",
                        "exception": str(e)
                    }, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({
                "message": "Question Paper Created",
                "paper": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Question Paper Not Created"
        }, status=status.HTTP_400_BAD_REQUEST)
