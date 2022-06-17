from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin

from .models import Question, Choice, User, Answer, Group, GroupUser, GroupAnswer, Week


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'week')
    list_editable = ('week',)
    fieldsets = [
        (None, {'fields': ['question_text', 'week']}),
    ]
    inlines = [ChoiceInline]

class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'is_superuser', 'is_active')
    fieldsets = (
        ('None', {'fields': ('phone', 'password', 'name', 'is_active')}),
    )
    add_fieldsets = (
        (
            'None', {
                'classes': ('wide',),
                'fields': ('phone', 'name', 'password1', 'password2', 'is_active')
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

    list_display = ('user', 'question', 'choice', 'is_correct' ,'time')

admin.site.register(Question, QuestionAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Week, WeekAdmin)
# admin.site.register(Group)
# admin.site.register(GroupUser)
# admin.site.register(GroupAnswer)
