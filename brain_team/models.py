from django.contrib.auth.models import User
from django.contrib.postgres.fields import *
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Company(models.Model):
    name = models.CharField(max_length=100, default='')
    superadmin_id = models.IntegerField(default=0, null=False)


class Team(models.Model):
    admin = models.IntegerField(default=0)
    name = models.CharField(max_length=100, default='')
    requests = models.ManyToManyField(User())
    members = models.ManyToManyField(User(), related_name='team_members', related_query_name='team_members')


class QuizQuestion(models.Model):
    question = models.CharField(max_length=500, default='')
    answer_type = models.IntegerField(null=False)
    answers = ArrayField(models.CharField(max_length=100), null=True, default=[])
    true_answer = models.IntegerField(default=0, null=False)


class Quiz(models.Model):
    name = models.CharField(max_length=100, default='')
    team = models.ForeignKey(Team, related_name='quiz_team', related_query_name='quiz_team',
                             on_delete=models.CASCADE, null=True)
    teams = models.ManyToManyField(Team())
    num_questions = models.IntegerField(default=10)
    datetime = models.DateTimeField()
    chosen_capitan = models.BooleanField(default=False)
    started = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    finished = models.BooleanField(default=False)
    timer = models.DateTimeField(default=timezone.now, null=False)
    current_question = models.IntegerField(default=0)
    questions = models.ManyToManyField(QuizQuestion())
    result_show = models.BooleanField(default=False)


class QuizAnswer(models.Model):
    user = models.ForeignKey(User, related_name='quiz_answer_user', related_query_name='quiz_answer_user',
                             on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey(Quiz, related_name='quiz_answer', related_query_name='quiz_answer',
                             on_delete=models.CASCADE, null=True)
    quiz_question = models.ForeignKey(QuizQuestion, related_name='quiz_answer_quiz_question',
                                      related_query_name='quiz_answer_quiz_question',
                                      on_delete=models.CASCADE, null=True)
    answer = models.IntegerField(default=-1)
    points = models.IntegerField(default=0)


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user', related_query_name='user', on_delete=models.CASCADE,
                                primary_key=True)
    name = models.CharField(max_length=100, default='')
    surname = models.CharField(max_length=100, default='')
    patronymic = models.CharField(max_length=100, default='')
    birthday = models.DateField()
    company = models.ForeignKey(Company, related_name='profile_company', related_query_name='profile_company',
                                on_delete=models.CASCADE, null=True)

    avatar = models.ImageField(upload_to='user_avatars/', blank=True,
                               null=True, default='user_avatars/default.png')

    status = models.IntegerField(default=0)
    teams = models.ManyToManyField(Team())

    def get_absolute_url(self):
        return reverse("profile", kwargs={"user_id": self.user_id})


class QuizProfileActions(models.Model):
    quiz = models.ForeignKey(Quiz, related_name='quiz_action', related_query_name='quiz_action',
                             on_delete=models.CASCADE, null=True)
    profile = models.ForeignKey(Profile, related_name='profile_quiz_action', related_query_name='profile_quiz_action',
                                on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Team, related_name='team_quiz_action', related_query_name='team_quiz_action',
                             on_delete=models.CASCADE, null=True)
    last_action = models.IntegerField(default=0)
    answers = models.ManyToManyField(QuizAnswer())
    is_ready = models.BooleanField(default=False)
    points = models.IntegerField(default=0)
