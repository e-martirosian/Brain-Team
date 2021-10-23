"""brain_team URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from brain_team import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('sign_in', views.sign_in, name='sign_in'),
    path('sign_up', views.sign_up, name='sign_up'),
    path('profile', views.profile, name='profile'),
    path('sign_out', views.sign_out, name='sign_out'),
    path('company', views.company, name='company'),
    path('create_company', views.create_company, name='create_company'),
    path('company', views.choose_company, name='company'),
    path('add_to_company', views.add_to_company, name='add_to_company'),
    path('teams', views.teams, name='teams'),
    path('schedule', views.home, name='schedule'),
    path('create_team', views.create_team, name='create_team'),
    path('request_to_team', views.request_to_team, name='request_to_team'),
    path('requests_teams_list', views.requests_teams_list, name='requests_teams_list'),
    path('add_to_team', views.add_to_team, name='add_to_team'),
    path('events', views.events_list, name='events'),
]
