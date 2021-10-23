from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from brain_team.constance import *
from . import events, constance
from .models import Profile, Company, Team


def get_full_context(request, context):
    profile = None
    if request.user.is_authenticated:
        profile = Profile.objects.get(user__id=request.user.id)
    general_context = {"events": events.get(request), "constance": constance, "profile": profile}
    return {**context, **general_context}


def home(request):
    if request.user.is_authenticated:
        return redirect('/profile')
    return render(request, 'pages/leadpage.html', get_full_context(request, {'PAGE_NAME': LEAD_PAGE_NAME}))


def sign_in(request):
    if request.user.is_authenticated:
        return redirect('/profile')

    if request.method == 'POST':
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect('/')
        else:
            events.add_event(request, {constance.EVENT_ERROR: [constance.NON_CORRECT_DATA]})

    return render(request, 'pages/auth/sign_in.html', get_full_context(request, {'PAGE_NAME': SIGN_IN_PAGE_NAME}))


def valid_field(field):
    return field != "" and field is not None


def sign_up(request):
    if request.user.is_authenticated:
        return redirect('/profile')

    if request.method == 'POST':

        email = request.POST.get('email')
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        password = request.POST.get('password')

        if valid_field(email) and valid_field(name) and valid_field(surname) and valid_field(password):

            user = User.objects.create(username=email)
            patronymic = request.POST.get('patronymic')
            birthday = request.POST.get('birthday')
            user.set_password(password)
            user.save()
            Profile.objects.create(user=user, name=name, surname=surname, status=0, patronymic=patronymic,
                                   birthday=birthday)

            events.add_event(request, {constance.EVENT_INFO: ['Регистация прошла успешно.']})

            return redirect("sign_in")

        else:
            events.add_event(request, {'Ошибка': ['Неправильно заполнены поля.']})
    return render(request, 'pages/auth/sign_up.html', get_full_context(request, {'PAGE_NAME': SIGN_UP_PAGE_NAME}))


@login_required(login_url='/sign_in')
def profile(request):
    return render(request, 'pages/profile/profile.html', get_full_context(request, {'PAGE_NAME': PROFILE_PAGE_NAME}))


@login_required(login_url='/sign_in')
def sign_out(request):
    logout(request)
    return redirect('/')


def get_profile(request):
    return Profile.objects.get(user__id=request.user.id)


def company(request):
    profile = get_profile(request)
    company_requests = []
    if profile.company is not None:
        superadmin = Company.objects.filter(id=profile.company.id, superadmin_id=profile.user.id)
        if superadmin.count() != 0:
            company_requests = Profile.objects.filter(company__id=profile.company.id, status=1)
    return render(request, 'pages/profile/company/company.html', get_full_context(request,
                                                                                  {'PAGE_NAME': COMPANY_PAGE_NAME,
                                                                                   'company_requests': company_requests}))


def create_company(request):
    profile = get_profile(request)
    if profile.status == 2:
        return redirect('/company')

    if request.method == 'POST':
        name = request.POST.get('name')
        if valid_field(name):
            company = Company.objects.create(name=name)
            company.superadmin_id = profile.user.id
            company.save()
            profile.status = 2
            profile.company = company
            profile.save()
            events.add_event(request, {EVENT_INFO: ['Организация успешно создана.']})
        return redirect('profile')
    return render(request, 'pages/profile/company/create_company.html',
                  get_full_context(request, {'PAGE_NAME': COMPANY_PAGE_NAME}))


def choose_company(request):
    profile = get_profile(request)
    if profile.status == 2:
        return redirect('/company')

    if request.method == 'POST':
        id = request.POST.get('id')
        company = Company.objects.all().filter(id=id)
        if company.count() != 0:
            company = company[0]
            profile.company = company
            profile.status = 1
            profile.save()
            events.add_event(request, {EVENT_INFO: ['Запрос отправлен.']})
            return redirect('profile')
        else:
            events.add_event(request, {'Ошибка': ['Нет организации c таким ID.']})

    return render(request, 'pages/profile/company/choose_company.html',
                  get_full_context(request, {'PAGE_NAME': COMPANY_PAGE_NAME}))


def add_to_company(request):
    if request.method == 'POST':
        company_id = request.POST.get('company_id')
        user_id = request.POST.get('user_id')
        add = int(request.POST.get('add'))

        profile = Profile.objects.get(user__id=user_id)
        if add == 1:
            profile.status = 2
            events.add_event(request, {EVENT_INFO: ['Запрос принят.']})
        else:
            events.add_event(request, {EVENT_INFO: ['Запрос отклонен.']})
            profile.status = -1
        profile.save()
    return redirect('/company#requests')


def teams(request):
    profile = get_profile(request)

    profile_teams = []
    for team in profile.teams.all():
        if team.admin == profile.user.id:
            profile_teams.append(team)

    requests_teams_list = []
    for team in profile_teams:
        for user in Team.objects.get(id=team.id).requests.all():
            requests_teams_list.append([team, Profile.objects.get(user__id=user.id)])

    print(requests_teams_list)
    return render(request, 'pages/profile/teams/teams.html',
                  get_full_context(request, {'PAGE_NAME': TEAMS_PAGE_NAME, 'requests_teams_list': requests_teams_list}))


def create_team(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if valid_field(name):
            team = Team.objects.create(name=name, admin=request.user.id)
            team.save()
            profile = get_profile(request)
            profile.teams.add(team)
            profile.save()
        else:
            events.add_event(request, {EVENT_INFO: [NON_CORRECT_DATA]})
    return redirect('/teams#teams')


def request_to_team(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        if valid_field(id):
            team = Team.objects.filter(id=id)
            if team.count() == 0:
                events.add_event(request, {EVENT_ERROR: ['Не найдена команда с таким ID.']})
                return redirect('/teams#request_to_team')
            team = team[0]
            team.requests.add(request.user)
            team.save()
            events.add_event(request, {EVENT_INFO: ['Запрос отправлен.']})
        else:
            events.add_event(request, {EVENT_INFO: [NON_CORRECT_DATA]})
    return redirect('/teams#request_to_team')


def requests_teams_list(request):
    return redirect('/teams#requests_teams_list')


def add_to_team(request):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        user_id = request.POST.get('user_id')
        add = int(request.POST.get('add'))

        print(team_id, user_id, add, request.POST)
        profile = Profile.objects.get(user__id=user_id)
        team = Team.objects.get(id=team_id)
        team.requests.remove(profile.user)
        team.save()

        if add == 1:
            profile.teams.add(team)
            profile.save()
            events.add_event(request, {EVENT_INFO: ['Запрос принят.']})
        else:
            events.add_event(request, {EVENT_INFO: ['Запрос отклонен.']})
        profile.save()
    return redirect('/teams#requests_teams_list')


def events_list(request):
    return render(request, 'pages/profile/events/events.html',
                  get_full_context(request, {'PAGE_NAME': EVENTS_PAGE_NAME}))
