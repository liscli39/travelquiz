from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin

from .models import Question, Choice, User, Answer, Group, GroupUser, GroupAnswer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['question_text']}),
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

admin.site.register(Question, QuestionAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Answer)
admin.site.register(Group)
admin.site.register(GroupUser)
admin.site.register(GroupAnswer)
