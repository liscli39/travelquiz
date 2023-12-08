from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib import admin, messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.urls import path, reverse
from django.db.models import Count
from django.utils.html import format_html

from .models import Question, Choice, User, Answer, Week, Island, Rank, Chart
from django.contrib.admin.filters import AllValuesFieldListFilter
from app.utils.enum import Enum

class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0

class QuestionAdmin(admin.ModelAdmin):
    def answer_count(self, obj):
        return Answer.objects.filter(question=obj).count()

    list_display = ('question_text', 'answer_count', 'week', 'type')
    list_editable = ('week', 'type')
    list_filter = ('week', 'type')
    fieldsets = [
        (None, {'fields': ['question_text', 'week', 'type', 'wiki_url', 'wiki_title']}),
    ]
    inlines = [ChoiceInline]

class CustomUserAdmin(UserAdmin):
    def get_office(self, obj):
        return (obj.office[:75] + '...') if obj.office and len(obj.office) > 75 else obj.office

    list_display = ('phone', 'cccd', 'name', 'allow_access', 'gender', 'year', 'job', 'get_office', 'prefecture', 'district', 'wards')
    list_editable = ['allow_access']
    get_office.short_description = 'office'

    list_filter = (
        ('allow_access'),
        ('gender'),
        ('job', DropdownFilter),
        ('office', DropdownFilter),
        ('prefecture', DropdownFilter),
        ('district', DropdownFilter),
        ('wards', DropdownFilter),
    )
    fieldsets = (
        ('None', {'fields': ('phone', 'password', 'name', 'year', 'cccd', 'gender', 'job', 'office', 'prefecture', 'district', 'wards', 'resets')}),
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
    search_fields = ('user_id', 'phone', 'name', 'gender', 'job', 'address', 'office', 'prefecture', 'district', 'wards')
    ordering = ('phone', 'allow_access')


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
    def week(self, obj):
        return obj.question.week if obj.question is not None else ''

    search_fields = ('user__user_id', 'user__phone')
    list_display = ('user', 'question', 'is_correct' ,'time', 'choice', 'content', 'turn', 'week')
    list_per_page = 40

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super(AnswerAdmin, self).get_search_results(request, queryset, search_term)
        try:
            if search_term is not None and search_term != '':
                queryset =  queryset.order_by('-turn', '-answer_id')
        except:
            pass

        return queryset, use_distinct


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
        completed = Answer.objects.values('user_id', 'turn').annotate(question_count=Count('question_id'))\
            .filter(question_count=1, question__type=Enum.QUESTION_CHOICE, question__week_id=week_id).values_list('user_id', flat=True)

        completed_count = completed.count()

        corrects = '''
            SELECT COUNT(U0.`question_id`) AS `count`
            FROM `app_answer` U0 INNER JOIN `app_choice` U1 ON (U0.`choice_id` = U1.`choice_id`)
            WHERE  U1.`is_correct` AND U0.`question_id` IS NOT NULL AND U0.`user_id` = `app_user`.`user_id`
            GROUP BY turn ORDER BY COUNT(U0.`question_id`) DESC
            LIMIT 1
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
                    INNER JOIN `app_question` U2 ON (U0.`question_id` = U2.`question_id`)
                    WHERE 
                        U2.`week_id` = {week_id} AND
                        U0.`question_id` IS NOT NULL AND 
                        U0.`user_id` = `app_user`.`user_id`
                    GROUP BY U0.`user_id`
                    ORDER BY NULL
                    LIMIT 1
                ) AS `time`,
                ABS(
                    {completed_count} - (
                        SELECT SUBSTRING(`content`, 1, 9)
                        FROM `app_answer` U0
                        INNER JOIN `app_question` U2 ON (U0.`question_id` = U2.`question_id`)
                        WHERE 
                            U2.`week_id` = {week_id} AND
                            U2.`type` = 2 AND
                            U0.`question_id` IS NOT NULL AND 
                            U0.`user_id` = `app_user`.`user_id`
                        ORDER BY NULL
                        LIMIT 1
                    )
                ) AS `delta`,
                (
                    SELECT SUBSTRING(`content`, 1, 9)
                    FROM `app_answer` U0
                    INNER JOIN `app_question` U2 ON (U0.`question_id` = U2.`question_id`)
                    WHERE 
                        U2.`week_id` = {week_id} AND
                        U2.`type` = 2 AND
                        U0.`question_id` IS NOT NULL AND 
                        U0.`user_id` = `app_user`.`user_id`
                    ORDER BY NULL
                    LIMIT 1
                ) AS `predict`
            FROM `app_user`
            WHERE 
                NOT `app_user`.`is_superuser` 
                AND `app_user`.`user_id` IN ({completed}) 
                AND ({corrects}) > 0
            ORDER BY `corrects` DESC, `delta` ASC, `time` ASC
            LIMIT 500;
        '''.format(completed=completed.query, corrects=corrects, week_id=week_id, completed_count=completed_count))

        Rank.objects.filter(week_id=week_id).delete()
        Rank.objects.bulk_create([
            Rank(week=week, user_id=user.user_id, corrects=user.corrects, time=user.time, predict=user.predict if user.predict else 0, delta=user.delta if user.delta else 0)
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
    
        completed_count = Rank.objects.filter(corrects=19, week_id=week_id).count()

        title = week.name if week is not None else None
        updated_at = week.rank_updated_at if week is not None else None
        action = 'reload/' + ('?week={}'.format(week.week_id) if week is not None else '')

        extra_context = {'title': title, 'updated_at': updated_at, 'action': action, 'completed_count': completed_count}
        self.completed_count = completed_count
        return super(RankAdmin, self).changelist_view(request, extra_context=extra_context)

    def name(self, obj):
        url = reverse('admin:app_user_change', args=(obj.user_id,))
        return format_html("<a href='{}'>{}</a>", url, obj.user.name)

    def phone(self, obj):
        return obj.user.phone

    def m_corrects(self, obj):
        return obj.corrects

    def m_time(self, obj):
        return '{} s'.format(obj.time / 100)

    def m_predict(self, obj):
        completed_count = self.completed_count if self.completed_count else 0
        return '{} /{}'.format(obj.predict, completed_count)

    m_predict.short_description = "Dự đoán"
    name.short_description = "Tên"
    phone.short_description = "SĐT"
    m_corrects.short_description = "Số câu đúng"
    m_time.short_description = "Thời gian"

    change_list_template = 'rank_changelist.html'
    list_display = ('name', 'phone', 'm_corrects', 'm_predict', 'm_time')
    # list_editable = ('selected',)
    list_display_links = None

    ordering = ('-selected', '-corrects', 'predict', 'time')
    sortable_by = ()
    list_filter = ('selected', WeekFilter)


class ChartAdmin(admin.ModelAdmin):
    list_display = ('date', 'user_count', 'anwser_count', 'anwser_correct')

admin.site.register(Question, QuestionAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(Rank, RankAdmin)
admin.site.register(Chart, ChartAdmin)
# admin.site.register(Group)
# admin.site.register(GroupUser)
# admin.site.register(GroupAnswer)
