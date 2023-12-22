from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseRedirect
from django.contrib import admin, messages
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin
from django.urls import path, reverse
from django.db.models import Count
from django.utils.html import format_html
from django.db.models import OuterRef, Subquery, F
from django.db.models.functions import Abs

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
        return Answer.objects.filter(question_id=obj.question_id).count()

    list_display = ('question_text', 'answer_count', 'week', 'type')
    list_editable = ('week', 'type')
    list_filter = ('week', 'type')
    fieldsets = [
        (None, {'fields': ['question_text', 'week', 'type', 'wiki_url', 'wiki_title']}),
    ]
    inlines = [ChoiceInline]


class InputFilter(admin.SimpleListFilter):
    template = 'admin/input_filter.html'

    def lookups(self, request, model_admin):
        # Dummy, required to show the filter.
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice['query_parts'] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice

class JobFilter(InputFilter):
    parameter_name = 'job'
    title = _('Job')

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(job__icontains=self.value())

class OfficeFilter(InputFilter):
    parameter_name = 'office'
    title = _('Office')

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(office__icontains=self.value())

class DistrictFilter(InputFilter):
    parameter_name = 'district'
    title = _('District')

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(district__icontains=self.value())

class WardsFilter(InputFilter):
    parameter_name = 'wards'
    title = _('Wards')

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(wards__icontains=self.value())


class CustomUserAdmin(UserAdmin):
    def get_office(self, obj):
        return (obj.office[:75] + '...') if obj.office and len(obj.office) > 75 else obj.office

    list_display = ('phone', 'cccd', 'name', 'allow_access', 'gender', 'year', 'job', 'get_office', 'prefecture', 'district', 'wards')
    list_editable = ['allow_access']
    get_office.short_description = 'office'

    list_filter = (
        ('allow_access'),
        ('gender'),
        ('prefecture', DropdownFilter),
        JobFilter,
        OfficeFilter,
        DistrictFilter,
        WardsFilter
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
    ordering = None


class IslandInline(admin.TabularInline):
    model = Island
    extra = 0

class WeekAdmin(admin.ModelAdmin):
    def question_count(self, obj):
        return obj.question_set.count()

    list_display = ('name', 'is_active', 'question_count', 'show_rank', 'rank_status')
    list_editable = ('is_active', 'show_rank')
    inlines = [IslandInline]


class AnswerAdmin(admin.ModelAdmin):
    def week(self, obj):
        return obj.question.week if obj.question is not None else ''
    
    def content_tr(self, obj):
        return (obj.content[:75] + '...') if obj.content and len(obj.content) > 75 else obj.content

    search_fields = ('user__user_id', 'user__phone')
    list_display = ('user', 'question', 'is_correct' ,'time', 'choice', 'content_tr', 'turn', 'week')
    list_per_page = 40
    raw_id_fields=['user', 'choice', 'question']

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

        week.rank_status = Enum.RANK_UPDATE_WAITING
        week.save()

        self.message_user(request, 'Bảng xếp hạng đang được cập nhật vui lòng đợi ít phút!!')
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
    
        if week is None:
            week = Week.objects.first()

        week_id = week.week_id

        ranks = Rank.objects.filter(week_id=week_id)
        completed_count = ranks.count()
        ranks.update(delta = Abs(completed_count - F('predict')))

        rank_status = week.rank_status if week is not None else None
        rank_process = week.rank_process if week is not None else 0
        title = week.name if week is not None else None
        updated_at = week.rank_updated_at if week is not None else None
        action = 'reload/' + ('?week={}'.format(week.week_id) if week is not None else '')

        extra_context = {'rank_status': rank_status, 'rank_process': rank_process, 'title': title, 'updated_at': updated_at, 'action': action, 'completed_count': completed_count}
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

    ordering = ('-selected', '-corrects', 'delta', 'time')
    sortable_by = ()
    list_filter = ('selected', WeekFilter)


class ChartAdmin(admin.ModelAdmin):
    list_display = ('date', 'user_count', 'anwser_count', 'anwser_correct')

admin.site.register(Question, QuestionAdmin)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(Rank, RankAdmin)
# admin.site.register(Chart, ChartAdmin)
# admin.site.register(Group)
# admin.site.register(GroupUser)
# admin.site.register(GroupAnswer)
