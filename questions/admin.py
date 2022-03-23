from django.contrib import admin
from .models import (
    Question,
    Option,
    Match,
    Keyword,
    Vote
)

# Register your models here.
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Keyword)
admin.site.register(Match)
admin.site.register(Vote)