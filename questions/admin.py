from django.contrib import admin
from .models import (
    Paper,
    Question,
    Option,
    Match,
    Keyword,
    QuestionPaper,
    Vote
)

# Register your models here.
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Keyword)
admin.site.register(Match)
admin.site.register(Vote)
admin.site.register(Paper)
admin.site.register(QuestionPaper)