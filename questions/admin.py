from django.contrib import admin
from .models import (
    Question,
    Option,
    Match,
    Keyword
)

# Register your models here.
admin.site.register(Question)
admin.site.register(Option)
admin.site.register(Keyword)
admin.site.register(Match)