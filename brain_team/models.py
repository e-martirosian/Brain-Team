from django.contrib.auth.models import User
from django.contrib.postgres.fields import *
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='user', related_query_name='user', on_delete=models.CASCADE,
                                primary_key=True)
    name = models.CharField(max_length=100, default='')
    surname = models.CharField(max_length=100, default='')
    patronymic = models.CharField(max_length=100, default='')
    birthday = models.DateField()
    # company = models.ForeignKey()
    # events = models.ForeignKey()

    avatar = models.ImageField(upload_to='user_avatars/', blank=True,
                               null=True, default='user_avatars/default.png')

    status = models.IntegerField(default=0)

    def get_absolute_url(self):
        return reverse("profile", kwargs={"user_id": self.user_id})