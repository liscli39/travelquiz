from django.db import models

class Question(models.Model):
    def __str__(self):
        return (self.question_text[:60] + '..') if len(self.question_text) > 60 else self.question_text

    question_id = models.BigAutoField(primary_key=True)
    question_text = models.TextField()


class Choice(models.Model):
    def __str__(self):
        return (self.choice_text[:60] + '..') if len(self.choice_text) > 60 else self.choice_text

    choice_id = models.BigAutoField(primary_key=True)
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

class KeywordQuestion(models.Model):
    def __str__(self):
        return (self.question_text[:60] + '..') if len(self.question_text) > 60 else self.question_text

    question_id = models.BigAutoField(primary_key=True)
    question_text = models.TextField()
    image = models.ImageField()
    keyword = models.CharField(max_length=255, null=True, blank=True)
    order = models.SmallIntegerField()


class Team(models.Model):
    team_id = models.BigAutoField(primary_key=True)
    team_name = models.CharField(max_length=255, null=True, blank=True)
    socket_id = models.CharField(max_length=255, null=True, blank=True)
    point_first = models.IntegerField(default=0)
    point_second = models.IntegerField(default=0)
    point_third = models.IntegerField(default=0)
    point_third = models.IntegerField(default=0)
    sec = models.IntegerField(default=0)


class Answer(models.Model):
    answer_id = models.BigAutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    question = models.ForeignKey(KeywordQuestion, on_delete=models.CASCADE, null=True, blank=True)


class KeywordAnswer(models.Model):
    answer_id = models.BigAutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255, null=True, blank=True)
    question = models.ForeignKey(KeywordQuestion, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    sec = models.IntegerField(default=None, null=True, blank=True)
