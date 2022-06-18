from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin

from .models import Question, Choice, User, Answer, Group, GroupUser, GroupAnswer, Week


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    def answer_count(self, obj):
        return Answer.objects.filter(question=obj).count()

    list_display = ('question_text', 'answer_count', 'week')
    list_editable = ('week',)
    fieldsets = [
        (None, {'fields': ['question_text', 'week', 'wiki_url', 'wiki_title']}),
    ]
    inlines = [ChoiceInline]

class CustomUserAdmin(UserAdmin):
    def answers(self, obj):
        answers = Answer.objects.filter(user=obj)
        corrects = Question.objects.filter(week__is_active=True, question_id__in=answers.filter(choice__is_correct=True, question__isnull=False)
                                           .values_list('question_id', flat=True))
        total = Question.objects.filter(week__is_active=True, question_id__in=answers.values_list('question_id', flat=True))
        return f'{corrects.count()}/{total.count()}'

    answers.short_description = 'Corrects/Total'
    list_display = ('phone', 'name', 'answers')
    fieldsets = (
        ('None', {'fields': ('phone', 'password', 'name')}),
    )
    add_fieldsets = (
        (
            'None', {
                'classes': ('wide',),
                'fields': ('phone', 'name', 'password1', 'password2')
            }
        ),
    )
    form = UserChangeForm
    search_fields = ('user_id', 'phone', 'name')
    ordering = ('phone',)

class WeekAdmin(admin.ModelAdmin):
    def question_count(self, obj):
        return obj.question_set.count()

    list_display = ('name', 'is_active', 'question_count')
    list_editable = ('is_active',)

class AnswerAdmin(admin.ModelAdmin):
    @admin.display(boolean=True)
    def is_correct(self, obj):
        return obj.choice.is_correct if obj.choice else False

    list_display = ('user', 'question', 'is_correct' ,'time', 'choice')
    list_filter  = ('user',)
    ordering = ('-answer_id',)

admin.site.register(Question, QuestionAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Week, WeekAdmin)
# admin.site.register(Group)
# admin.site.register(GroupUser)
# admin.site.register(GroupAnswer)
