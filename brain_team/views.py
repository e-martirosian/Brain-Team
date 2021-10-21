from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from brain_team.constance import *
from . import events, constance
from .models import Profile, Company


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

    return render(request, 'pages/sign_in.html', get_full_context(request, {'PAGE_NAME': SIGN_IN_PAGE_NAME}))


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
    return render(request, 'pages/sign_up.html', get_full_context(request, {'PAGE_NAME': SIGN_UP_PAGE_NAME}))


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
    return render(request, 'pages/profile/company.html', get_full_context(request,
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
    return render(request, 'pages/profile/create_company.html',
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

    return render(request, 'pages/profile/choose_company.html',
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
