from datetime import datetime
from enum import unique
from django.db import models
from authentication.models import Teacher, User

# Create your models here.
class Question(models.Model):
    type = models.CharField(max_length=2)
    setter = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.IntegerField()
    board = models.CharField(max_length=100)
    marks = models.IntegerField()
    difficulty = models.CharField(max_length=2)
    subject = models.CharField(max_length=100)
    medium = models.CharField(max_length=50)
    title = models.TextField(max_length=500)
    
    def __str__(self):
        return f"{self.type}-{self.title}"
    

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.CharField(max_length=100)
    correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question}-{self.option}"
    

class Match(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.question}, {self.key}-{self.value}"


class Keyword(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.question}-{self.keyword}"


class Vote(models.Model):
    class Meta:
        unique_together = (('teacher', 'question'),)
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    vote = models.IntegerField()
    
    def __str__(self):
        return f"{self.question}, {self.teacher}: {self.vote}"
    
class Paper(models.Model):
    export_date = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.teacher} - {self.name}"
    

class QuestionPaper(models.Model):
    class Meta:
        unique_together = (('paper', 'question'),)
    
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.paper.name} - {self.question}"

class File(models.Model):
    file = models.FileField(blank=False, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
