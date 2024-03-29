from re import T
import math
from rest_framework import generics, status, views, permissions
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from qbag_api.permissions import IsTeacher, IsOther
from .models import *
from .serializers import *
import pickle
from sklearn.metrics.pairwise import cosine_similarity
from operator import itemgetter
from pathlib import Path
import csv
import os
import traceback
import random
from authentication.utils import Util


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
        votes = Vote.objects.filter(question_id=ques_id).count()
        upvote = Vote.objects.filter(question_id=ques_id, vote=1).count()
        downvote = Vote.objects.filter(question_id=ques_id, vote=0).count()
        
        if serializer.data['type'] != 'd':
            opt_obj = Option.objects.filter(question=ques)
            opt_ser = OptionSerializer(instance=opt_obj, many=True)
            options = opt_ser.data
            random.shuffle(options)
            data = {
                'question_data': serializer.data,
                'keyword_data': keyword_ser.data,
                'option_data': options,
                'total_votes': votes,
                'upvote': upvote,
                'downvote': downvote
            }
        else:
            match_obj = Match.objects.filter(question=ques)
            match_ser = MatchSerializer(instance=match_obj, many=True)
            data = {
                'question_data': serializer.data,
                'keyword_data': keyword_ser.data,
                'match_data': match_ser.data,
                'total_votes': votes,
                'upvote': upvote,
                'downvote': downvote
            }

        return Response(data, status=status.HTTP_200_OK)




class RetreiveQuestionView(generics.GenericAPIView):
    permission_classes = (IsTeacher,)
    serializer_class = GetQuestionSerializer

    def post(self, request):
        data = request.data
        additional_ques = data.get("additional_ques") or 0.0


        all_ques = list()

        num_easy = math.ceil(int(data.get('easy')) * (1 + additional_ques*0.01))
        num_medium = math.ceil(int(data.get('medium')) * (1 + additional_ques*0.01))
        num_hard = math.ceil(int(data.get('hard')) * (1 + additional_ques*0.01))

        easy_ques = Question.objects.filter(
            difficulty='a',
            board=data.get('board'),
            medium=data.get('langMedium'),
            subject=data.get('subject'),
            grade=data.get('grade')
        )[:num_easy]
        all_ques.append(easy_ques)

        medium_ques = Question.objects.filter(
            difficulty='b',
            board=data.get('board'),
            medium=data.get('langMedium'),
            subject=data.get('subject'),
            grade=data.get('grade')
        )[:num_medium]
        all_ques.append(medium_ques)

        hard_ques = Question.objects.filter(
            difficulty='c',
            board=data.get('board'),
            medium=data.get('langMedium'),
            subject=data.get('subject'),
            grade=data.get('grade')
        )[:num_hard]
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
                    options = opt_ser.data
                    random.shuffle(options)
                    questions.append({
                        'id': ques.id,
                        'upvote': upvote,
                        'downvote': downvote,
                        'question_data': serializer.data,
                        'keyword_data': keyword_ser.data,
                        'option_data': options,
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


# Get All Questions of a Teacher
class GetAllMyQuestionsView(generics.GenericAPIView):
    permission_classes = (IsTeacher,)
    serializer_class = GetQuestionSerializer

    def get(self, request):
        all_ques = Question.objects.filter(setter=request.user.id)

        questions = []
        for ques in all_ques:
            serializer = GetQuestionSerializer(instance=ques)
            keyword_obj = Keyword.objects.filter(question=ques)
            keyword_ser = KeywordSerializer(
                instance=keyword_obj, many=True)

            if serializer.data['type'] != 'd':
                opt_obj = Option.objects.filter(question=ques)
                opt_ser = OptionSerializer(instance=opt_obj, many=True)
                upvote = Vote.objects.filter(question=ques, vote=1).count()
                downvote = Vote.objects.filter(question=ques, vote=0).count()
                options = opt_ser.data
                random.shuffle(options)
                questions.append({
                    'id': ques.id,
                    'upvote': upvote,
                    'downvote': downvote,
                    'question_data': serializer.data,
                    'keyword_data': keyword_ser.data,
                    'option_data': options,
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




# Voting Views
class VotingView(generics.GenericAPIView):
    permission_classes = (IsTeacher, )
    serializer_class = VoteSerializer

    def post(self, request):
        data = request.data

        vote_data = {}
        vote_data['teacher'] = request.user.teacher.pk
        vote_data['vote'] = data.get('vote')
        vote_data['question'] = data.get('question')
        vote_data['reason'] = data.get('reason')

        question = Question.objects.get(id=vote_data['question'])
        if int(question.setter.id) == int(request.user.id):
            return Response({
                "message": "You cannot vote",
            }, status=status.HTTP_401_UNAUTHORIZED)

        if Vote.objects.filter(teacher=vote_data['teacher'], question=vote_data['question']).exists():
            voteObj = Vote.objects.get(teacher=vote_data['teacher'], question=vote_data['question'])
            if(voteObj.vote == vote_data['vote']):
                return Response({
                    "message": "You have already voted",
                }, status=status.HTTP_401_UNAUTHORIZED)
            Vote.objects.filter(teacher=vote_data['teacher'], question=vote_data['question']).update(vote=vote_data['vote'], reason=vote_data['reason'])
        else:
            serializer = self.serializer_class(data=vote_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

        value = "Upvoted" if vote_data['vote'] == 1 else "Downvoted"

        threshold = 2

        if value == "Downvoted":
            total_votes = Vote.objects.filter(
                question=vote_data['question']).count()
            down_votes = Vote.objects.filter(
                question=vote_data['question'], vote=0).count()


            if total_votes > threshold and down_votes > total_votes / 2:
                user = User.objects.get(id = request.user.pk)
                ques = Question.objects.get(id=vote_data['question'])
                reasons = ""
                reasons_objs = Vote.objects.filter(question=ques)
                if len(reasons_objs) > 5:
                    reasons_objs = reasons_objs[:5]
                for idx, reason_obj in enumerate(reasons_objs):
                    reasons+=str(idx+1)
                    reasons+=". "
                    reasons+=reason_obj.reason
                    reasons+="\n"
                print(reasons)
                email_body = 'Hi '+ ques.setter.name + ',\nThe following question was deleted from our question bank as it was downvoted by the community:\n\nQuestion Details:\nGrade:' + str(ques.grade) + '\nBoard: ' + str(ques.board) + '\nMarks: ' + str(ques.marks) + '\n :Subject ' + ques.subject + '\nMedium : ' + ques.medium + '\nTitle : ' + ques.title + '\n\n' + 'Few reasons why your question was removed:\n' + reasons
                data = {'email_body': email_body, 'to_email': ques.setter.email, 'email_subject': 'Deletion of your question'}

                Util.send_email(data)

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
        name = data['name']
        questions_list = data['questions']
        teacher = request.user.teacher.id


        if len(questions_list) == 0 :
            return Response({
            "message": "Paper creation requires atleast 1 question"
        }, status=status.HTTP_400_BAD_REQUEST)

        
        paper = {
            'teacher': teacher,
            'name': name
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




# Get All Papers View
class GetAllPaperView(generics.GenericAPIView):
    permission_classes = (IsTeacher, )
    serializer_class = PaperSerializer

    def get(self, request):
        all_papers = Paper.objects.filter(teacher=request.user.teacher.id)
        data = {"papers": []}
        for paper in all_papers:
            try:
                temp_obj = {"name": paper.name}
                all_questions = paper.questionpaper_set.all()
                temp_obj["board"] = all_questions[0].question.board
                temp_obj["grade"] = all_questions[0].question.grade
                temp_obj["export_date"] = paper.export_date
                marks = 0; num_questions = 0
                for q in all_questions:
                    marks += q.question.marks; num_questions+=1
                temp_obj["total_marks"] = marks
                temp_obj["num_questions"] = num_questions
                temp_obj["id"] = paper.id
                temp_obj.update({'noQues': False})
            except:
                temp_obj = {"name": paper.name, "noQues": True}

            data["papers"].append(temp_obj)
            
        return Response(data, status=status.HTTP_200_OK)




# Get All Questions from a Paper
class GetQuestionFromPaperView(generics.GenericAPIView):
    permission_classes = (IsTeacher,)
    serializer_class = GetQuestionSerializer

    def get(self, request, paper_id):
        
        if request.user.teacher.id != Paper.objects.get(id=paper_id).teacher.id:
            return Response(
                {"message": "Cannot access Paper created by another teacher"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        qp_objs = QuestionPaper.objects.filter(paper=paper_id)
        all_ques = list()
        for qp in qp_objs:
            all_ques.append(qp.question)

        questions = list()
        for ques in all_ques:
            serializer = GetQuestionSerializer(instance=ques)
            keyword_obj = Keyword.objects.filter(question=ques)
            keyword_ser = KeywordSerializer(
                instance=keyword_obj, many=True)

            if serializer.data['type'] != 'd':
                opt_obj = Option.objects.filter(question=ques)
                opt_ser = OptionSerializer(instance=opt_obj, many=True)
                options = opt_ser.data
                random.shuffle(options)

                upvote = Vote.objects.filter(question=ques, vote=1).count()
                downvote = Vote.objects.filter(question=ques, vote=0).count()
                questions.append({
                    'id': ques.id,
                    'upvote': upvote,
                    'downvote': downvote,
                    'question_data': serializer.data,
                    'keyword_data': keyword_ser.data,
                    'option_data': options,
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

# Bulk Upload Questions from CSV File
class BulkUploadView(generics.GenericAPIView):
    serializer_class = QuestionSerializer
    permission_classes = (IsTeacher, )

    def post(self, request):
        if 'file' not in request.data:
            return Response({"message": "file not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = FileSerializer(data=request.data)
            
            if serializer.is_valid(raise_exception=True):
                file_obj = serializer.save()

                record = File.objects.latest('timestamp')
                filename = str(record.file)
                bulk_upload_csv = Path(settings.MEDIA_ROOT)
                file_to_read = bulk_upload_csv / filename

                with open(file_to_read, encoding = 'utf-8') as csv_file_handler:
                    csv_reader = csv.DictReader(csv_file_handler)
                    file_data_rows = [rows for rows in csv_reader]
                
                data = request.data
                qgrade = data.get('grade')
                qboard = data.get('board')
                qmedium = data.get('medium')
                qsubject = data.get('subject')

                for row in file_data_rows:

                    question_data = {}
                    question_data["type"] = row["type"]
                    question_data['setter'] = request.user.id
                    question_data["grade"] = qgrade
                    question_data["board"] = qboard
                    question_data["marks"] = row["marks"]
                    # question_data["difficulty"] = row["difficulty"]
                    question_data["subject"] = qsubject
                    question_data["title"] = row["title"]
                    question_data["medium"] = qmedium

                    if row["difficulty"].lower() == "easy":
                        question_data["difficulty"] = "a"
                    elif row["difficulty"].lower() == "medium":
                        question_data["difficulty"] = "b"
                    else:
                        question_data["difficulty"] = "c"
                
                    serializer = self.serializer_class(data=question_data)

                    try:
                        if serializer.is_valid(raise_exception=True):
                            question = serializer.save()

                            for keyword in row["keywords"].split(";"):
                                Keyword.objects.create(question=question, keyword=keyword)

                            if question.type == "a":
                                for i in range(1,5):
                                    if row[f"option{i}"]:
                                        Option.objects.create(question=question,option=row[f"option{i}"],correct=row[f"correct{i}"])
                            elif question.type != "d":
                                Option.objects.create(question=question,option=row[f"option1"],correct=1)
                            else:
                                print("We don't do match the following")
                    except Exception:
                        traceback.print_exc()
                        return Response({"message": "file corrupted"}, status=status.HTTP_404_NOT_FOUND)
                    
                if os.path.exists(file_to_read):
                    print(file_to_read)
                    os.remove(file_to_read)
                    print("Removed")
                    file_obj.delete()
                
                return Response({"message": "done"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "file corrupted"}, status=status.HTTP_404_NOT_FOUND)


class URLTemplateView(generics.GenericAPIView):
    serializer_class = TemplateSerializer
    permission_classes = (IsTeacher, )

    def post(self, request):
        data = {}
        data['setter'] = request.user.pk
        data['template_string'] = request.data.get('template_string')
        data['name'] = request.data.get('name')
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            question = serializer.save()

        return Response(
            {"message": "done"},
            status=status.HTTP_200_OK
        )


class GetURLTemplateView(generics.GenericAPIView):
    serializer_class = TemplateSerializer
    permission_classes = (IsTeacher, )

    def get(self, request):
        objs = URLTemplate.objects.filter(setter=request.user.pk)
        serializer = TemplateSerializer(instance=objs, many=True)

        return Response({
            'saved_url_templates': serializer.data
        },status=status.HTTP_200_OK) 