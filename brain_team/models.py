from django.contrib.auth.models import User
from django.contrib.postgres.fields import *
from django.db import models
from django.urls import reverse


class Company(models.Model):
    name = models.CharField(max_length=100, default='')
    superadmin_id = models.IntegerField(default=0, null=False)


class Team(models.Model):
    admin = models.IntegerField(default=0)
    name = models.CharField(max_length=100, default='')


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
