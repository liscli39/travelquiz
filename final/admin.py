from django.contrib import admin
from .models import Question, Choice, Team, KeywordQuestion, KeywordAnswer


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
admin.site.register(KeywordQuestion, list_display = ('question_text', 'keyword', 'order'), list_editable=('order',))
admin.site.register(KeywordAnswer)
admin.site.register(Team, list_display=('team_name', 'team_id', ))

class TeamFirstAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('team_name', 'point_first')
    list_editable = ('point_first',)
    list_display_links = None
    sortable_by = ('point_first',)

class TopFirst(Team):
    class Meta:
        proxy = True


admin.site.register(TopFirst, TeamFirstAdmin)

class TeamSecondAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('team_name', 'point_second', 'sec')
    list_editable = ('point_second', 'sec')
    list_display_links = None
    sortable_by = ('point_second', 'sec')

class TopSecond(Team):
    class Meta:
        proxy = True


admin.site.register(TopSecond, TeamSecondAdmin)

class TeamThirdAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('team_name', 'point_third',)
    list_editable = ('point_third',)
    list_display_links = None
    sortable_by = ('point_third',)

class TopThird(Team):
    class Meta:
        proxy = True


admin.site.register(TopThird, TeamThirdAdmin)