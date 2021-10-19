from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from brain_team.constance import *
from . import events, constance
from .models import Profile


def get_full_context(request, context):
    general_context = {"events": events.get(request), "constance": constance}
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
            events.add_event(request, {'Ошибка': 'Неправильно заполнены поля.'})
    return render(request, 'pages/sign_up.html', get_full_context(request, {'PAGE_NAME': SIGN_UP_PAGE_NAME}))


@login_required(login_url='/sign_in')
def profile(request):
    return render(request, 'pages/profile.html')


@login_required(login_url='/sign_in')
def sign_out(request):
    logout(request)
    return redirect('/')
