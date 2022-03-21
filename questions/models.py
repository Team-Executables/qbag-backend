from django.db import models
from authentication.models import User

# Create your models here.
class Question(models.Model):
    type = models.CharField(max_length=2)
    setter = models.ForeignKey(User, on_delete=models.CASCADE)
    grade = models.IntegerField()
    board = models.CharField(max_length=100)
    marks = models.IntegerField()
    difficulty = models.CharField(max_length=2)
    subject = models.CharField(max_length=100)
    title = models.TextField(max_length=500)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    
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
