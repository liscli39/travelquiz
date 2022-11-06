from django.contrib import admin
from .models import Question, Choice, Team, AnswerChoice, KeywordQuestion, AnswerKeyword


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text',)
    fieldsets = [
        (None, {'fields': ['question_text']}),
    ]
    inlines = [ChoiceInline]


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

# Register your models here.
admin.site.register(Question, QuestionAdmin)
admin.site.register(Team)
admin.site.register(AnswerChoice)
admin.site.register(KeywordQuestion)
admin.site.register(AnswerKeyword)
