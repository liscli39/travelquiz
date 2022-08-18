from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib import admin, messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.urls import path, reverse
from django.db.models import Count
from django.utils.html import format_html

from .models import Question, Choice, User, Answer, Week, Island, Rank


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
    # def answers(self, obj):
    #     answers = Answer.objects.filter(user=obj)
    #     corrects = Question.objects.filter(week__is_active=True, question_id__in=answers.filter(choice__is_correct=True, question__isnull=False)
    #                                        .values_list('question_id', flat=True))
    #     total = Question.objects.filter(week__is_active=True, question_id__in=answers.values_list('question_id', flat=True))
    #     return f'{corrects.count()}/{total.count()}'

    # answers.short_description = 'Corrects/Total'
    def get_address(self, obj):
        return (obj.address[:75] + '...') if obj.address and len(obj.address) > 75 else obj.address

    def get_office(self, obj):
        return (obj.office[:75] + '...') if obj.office and len(obj.office) > 75 else obj.office

    list_display = ('phone', 'name', 'get_address', 'get_office')
    get_address.short_description = 'address'
    get_office.short_description = 'office'
    fieldsets = (
        ('None', {'fields': ('phone', 'password', 'name', 'address', 'office', 'resets')}),
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
    search_fields = ('user_id', 'phone', 'name', 'address', 'office')
    ordering = ('phone',)


class IslandInline(admin.TabularInline):
    model = Island
    extra = 0

class WeekAdmin(admin.ModelAdmin):
    def question_count(self, obj):
        return obj.question_set.count()

    list_display = ('name', 'is_active', 'question_count', 'show_rank')
    list_editable = ('is_active', 'show_rank')
    inlines = [IslandInline]


class AnswerAdmin(admin.ModelAdmin):
    @admin.display(boolean=True)
    def is_correct(self, obj):
        return obj.choice.is_correct if obj.choice else False

    raw_id_fields=['user']
    search_fields = ('user__user_id', 'user__phone')
    list_display = ('user', 'question', 'is_correct' ,'time', 'choice')
    ordering = ('-answer_id',)

class WeekFilter(admin.SimpleListFilter):
    title = _('week')
    parameter_name = 'week'

    def lookups(self, request, model_admin):
        weeks = Week.objects.all()
        return [(week.week_id, _(week.name)) for week in weeks]

    def choices(self, cl):
        week = Week.objects.filter(is_active=True).first()
        week_id = week.week_id if week is not None else None

        for lookup, title in self.lookup_choices:
            week_id = week_id if self.value() is None else self.value()
            yield {
                'selected': str(week_id) == str(lookup),
                'query_string': cl.get_query_string({ self.parameter_name: lookup }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        week = Week.objects.filter(is_active=True).first()
        week_id = week.week_id if week is not None else None
        week_id = week_id if self.value() is None else self.value()
        return queryset.filter(week_id=week_id)


class RankAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [path('reload/', self.reload_ranks)]
        return my_urls + urls

    def reload_ranks(self, request):
        week_id = request.GET.get('week')
        week = Week.objects.filter(pk=week_id).first()
        if week is None:
            week = Week.objects.filter(is_active=True).first()
        
        if week is None:
            self.message_user(request, 'There is no active week!', level=messages.ERROR)
            return HttpResponseRedirect('../')

        week_id = week.week_id if week is not None else None

        completed = Answer.objects.values('user_id').annotate(question_count=Count('question_id'))\
            .filter(question_count=30, question__week_id=week_id).values_list('user_id', flat=True)

        corrects = '''
            SELECT COUNT(V0.`question_id`) AS `count`
            FROM `app_question` V0
            WHERE
                V0.`week_id` = {} AND
                V0.`question_id` IN(
                    SELECT U0.`question_id`
                    FROM `app_answer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    WHERE  U1.`is_correct` AND U0.`question_id` IS NOT NULL AND U0.`user_id` = `app_user`.`user_id`
                ) LIMIT 1
        '''.format(week_id)

        users = User.objects.raw('''
            SELECT
                `app_user`.`user_id`,
                `app_user`.`phone`,
                `app_user`.`name`,
                ({corrects}) AS `corrects`,
                (
                    SELECT SUM(U0.`time`)
                    FROM `app_answer` U0
                    INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
                    INNER JOIN `app_question` U2 ON (U0.`question_id` = U2.`question_id`)
                    WHERE 
                        U1.`is_correct` AND 
                        U2.`week_id` = {week_id} AND
                        U0.`question_id` IS NOT NULL AND 
                        U0.`user_id` = `app_user`.`user_id`
                    GROUP BY U0.`user_id`
                    ORDER BY NULL
                    LIMIT 1
                ) AS `time`
            FROM `app_user`
            WHERE 
                NOT `app_user`.`is_superuser` 
                AND `app_user`.`user_id` IN ({completed}) 
                AND ({corrects}) > 0
            ORDER BY `corrects` DESC, `time` ASC
            LIMIT 500;
        '''.format(completed=completed.query, corrects=corrects, week_id=week_id))

        Rank.objects.filter(week_id=week_id).delete()
        Rank.objects.bulk_create([
            Rank(week=week, user_id=user.user_id, corrects=user.corrects, time=user.time)
            for user in users
        ])            

        week.rank_updated_at = datetime.now()
        week.save()

        self.message_user(request, 'All ranks are now updated')
        return HttpResponseRedirect('../?week={}'.format(week_id))

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        week_id = request.GET.get('week')
        week = Week.objects.filter(pk=week_id).first()
        if week is None:
            week = Week.objects.filter(is_active=True).first()
    
        title = week.name if week is not None else None
        updated_at = week.rank_updated_at if week is not None else None
        action = 'reload/' + ('?week={}'.format(week.week_id) if week is not None else '')

        extra_context = {'title': title, 'updated_at': updated_at, 'action': action}
        return super(RankAdmin, self).changelist_view(request, extra_context=extra_context)

    def name(self, obj):
        url = reverse('admin:app_user_change', args=(obj.user_id,))
        return format_html("<a href='{}'>{}</a>", url, obj.user.name)

    def phone(self, obj):
        return obj.user.phone

    change_list_template = 'rank_changelist.html'
    list_display = ('selected', 'name', 'phone','corrects', 'time')
    list_editable = ('selected',)
    list_display_links = None
    ordering = ('-selected', '-corrects', 'time')
    sortable_by = ()
    list_filter = ('selected', WeekFilter)


admin.site.register(Question, QuestionAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(Rank, RankAdmin)
# admin.site.register(Group)
# admin.site.register(GroupUser)
# admin.site.register(GroupAnswer)
