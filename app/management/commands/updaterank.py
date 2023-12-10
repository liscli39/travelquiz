from django.core.management.base import BaseCommand, CommandError
from datetime import datetime
from django.utils.translation import gettext_lazy as _

from app.models import Question, Choice, User, Answer, Week, Island, Rank, Chart
from app.utils.enum import Enum
from django.db.models import OuterRef, Subquery, F
from django.db.models.functions import Abs


class Command(BaseCommand):
    def handle(self, *args, **options):
        weeks = Week.objects.filter(is_active=True, rank_status=Enum.RANK_UPDATE_WAITING)
        week_ids = [week_id for week_id in weeks.values_list('week_id', flat=True)]
        weeks.update(rank_status=Enum.RANK_UPDATE_PROCESS)

        weeks = Week.objects.filter(week_id__in=week_ids)
        for week in weeks:
            week_id = week.week_id
            Rank.objects.filter(week_id=week_id).delete()

            question_ids = Question.objects.filter(week_id=week_id, type=Enum.QUESTION_PREDICT).values_list('question_id', flat=True)
            users_count = Answer.objects.filter(question_id__in=question_ids, turn__isnull=False, content__isnull=False).count()
            print('users_count', users_count)

            OFFSET = 0
            LIMIT = 1000
            while True:
                users = Answer.objects.filter(question_id__in=question_ids, turn__isnull=False, content__isnull=False).values_list('user_id', flat=True)[OFFSET:OFFSET+LIMIT]
                if users.count() == 0 or OFFSET > users_count:
                    break

                query = '''
                    SELECT
                    U3.`user_id`,
                    U3.`name`,
                    U0.`turn`,
                    COUNT(*) AS `count`,
                    (
                        SELECT `time` FROM `app_answer` AS A0 
                        WHERE 
                            A0.`user_id` = U0.`user_id` AND
                            A0.`turn` = U0.`turn` AND
                            A0.`content` IS NOT NULL
                        LIMIT 1
                    ) AS `time`,
                    (
                        SELECT SUBSTRING(`content`, 1, 9) FROM `app_answer` AS A0 
                        WHERE 
                            A0.`user_id` = U0.`user_id` AND
                            A0.`turn` = U0.`turn` AND
                            A0.`content` IS NOT NULL
                        LIMIT 1
                    ) AS `predict`,
                    (
                        SELECT COUNT(*) FROM `app_answer` AS A0 
                        WHERE 
                            A0.`user_id` = U0.`user_id` AND
                            A0.`turn` = U0.`turn` AND
                            A0.`content` IS NULL
                    ) AS `total`
                    FROM `app_answer` U0
                    INNER JOIN `app_question` U2 ON (U0.`question_id` = U2.`question_id`)
                    INNER JOIN `app_user` U3 ON (U0.`user_id` = U3.`user_id`)
                    WHERE U0.`is_correct`
                    AND U0.`question_id` IS NOT NULL
                    AND U0.`user_id` IN ({users})
                    AND U2.`week_id` = {week_id}
                    GROUP BY user_id, turn
                    HAVING `predict` IS NOT NULL AND `total` = 19 AND `count` = 19
                '''
                data = User.objects.raw(query.format(users=','.join(map(str, users)), week_id=week_id))

                print(OFFSET, data.__len__())
                Rank.objects.bulk_create([
                    Rank(week=week, user_id=item.user_id, corrects=item.count, time=item.time, predict=item.predict if item.predict else 0, delta=-1)
                    for item in data
                ])

                week.rank_process = (OFFSET / users_count) * 100
                week.save()
                OFFSET += LIMIT

            ranks = Rank.objects.filter(week_id=week_id)
            rank_count = ranks.count()
            ranks.update(delta = Abs(rank_count - F('predict')))

            week.rank_status = Enum.RANK_UPDATE_FINISH
            week.rank_process = 100
            week.rank_updated_at = datetime.now()
            week.save()

    def update_correct(self, *args, **options):
        OFFSET = 0
        LIMIT = 5000

        while True:
            choice = Choice.objects.filter(choice_id=OuterRef('choice_id'))

            answers = Answer.objects.annotate(choice_correct=Subquery(choice.values('is_correct')[:1])).filter(answer_id__gte=OFFSET, answer_id__lt=OFFSET + LIMIT, choice_id__isnull=False, is_correct__isnull=True)
            print(OFFSET, answers.count())
            answers.update(is_correct=F('choice_correct'))
            OFFSET += LIMIT
