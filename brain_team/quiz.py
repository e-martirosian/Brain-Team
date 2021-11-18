import datetime

import pytz
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Profile, Quiz, QuizProfileActions, QuizAnswer, QuizQuestion
from .views import get_profile, get_full_context

IS_READY_TIME = 3
QUESTION_TIME = 3
BREAK_TIME = 10


def is_ready(request):
    quiz_id = request.POST.get('quiz_id')
    quiz = get_object_or_404(Quiz, id=quiz_id)
    profile = get_profile(request)
    profile_action = QuizProfileActions.objects.all().filter(profile=profile, quiz=quiz)

    if profile_action.count() == 0:
        profile_action = QuizProfileActions.objects.create(profile=profile, quiz=quiz)
    else:
        profile_action = profile_action[0]
    profile_action.is_ready = True
    profile_action.save()
    return redirect('/quiz_state' + str(quiz_id))


def all_are_ready(quiz):
    all_are_ready = True

    for team in quiz.teams.all():
        for user in team.members.all():
            profile_action = QuizProfileActions.objects.filter(profile__user__id=user.id, quiz=quiz)
            if profile_action.count() == 0:
                return False
            profile_action = profile_action[0]
            all_are_ready = all_are_ready and profile_action.is_ready

    return all_are_ready


def timer_over(quiz):
    NOW = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    print('CHECK', NOW, quiz.timer)
    if NOW > quiz.timer:
        return True
    return False


def all_answered(quiz):
    all_answered = True
    for team in quiz.teams.all():
        for user in team.members.all():
            profile = Profile.objects.get(user__id=user.id)
            profile_action = QuizProfileActions.objects.get(quiz=quiz, profile=profile)
            print(profile_action.answers.all())
            all_answered = all_answered and (len(profile_action.answers.all()) == quiz.current_question + 1)
    return all_answered


def can_answer(quiz, profile):
    profile_action = QuizProfileActions.objects.get(quiz=quiz, profile=profile)
    return len(profile_action.answers.all()) < quiz.current_question + 1


def update_profile_actions(quiz):
    for team in quiz.teams.all():
        for user in team.members.all():
            profile = Profile.objects.get(user__id=user.id)
            profile_action = QuizProfileActions.objects.get(quiz=quiz, profile=profile)
            quiz_question = quiz.questions.all()[quiz.current_question]
            print('UPA ALL', profile_action.answers.all())
            if len(profile_action.answers.all()) < quiz.current_question + 1:
                profile_action.answers.add(QuizAnswer.objects.create(quiz=quiz, quiz_question=quiz_question))
            else:
                pa_len = len(profile_action.answers.all())
                print("UPA", profile_action.answers.all()[pa_len - 1].answer, quiz_question.true_answer)
                if profile_action.answers.all()[pa_len - 1].answer == quiz_question.true_answer:
                    profile_action.points += 1
                    paa = profile_action.answers.all()[pa_len - 1]
                    qa = QuizAnswer.objects.filter(id=paa.id)[0]
                    qa.points += 1
                    qa.save()
            profile_action.save()


def get_timer(quiz):
    NOW = datetime.datetime.now().replace(tzinfo=pytz.UTC)
    secs = quiz.timer - NOW
    print(secs)
    secs = secs.total_seconds() * 1000
    return secs


def get_profile_answer(request, quiz, i=0):
    qa = QuizAnswer.objects.filter(user=request.user, quiz=quiz,
                                   quiz_question=quiz.questions.all()[quiz.current_question + i])
    if qa.count() == 0:
        return {'answer': -1, 'points': 0}
    print(qa[0].points)
    return qa[0]


def quiz_state(request, quiz_id):
    profile = get_profile(request)
    quiz = get_object_or_404(Quiz, id=quiz_id)

    profile_action = QuizProfileActions.objects.all().filter(profile=profile, quiz=quiz)

    if profile_action.count() == 0:
        profile_action = QuizProfileActions.objects.create(profile=profile, quiz=quiz)
    else:
        profile_action = profile_action[0]

    if quiz.finished:
        return render(request, 'pages/quiz/quiz_result.html', get_full_context(request, {"quiz": quiz,
                                                                                         "profile_action": profile_action}))

    print("QUIZ TIME", quiz.timer)
    NOW = datetime.datetime.utcnow().replace(tzinfo=pytz.UTC)
    if not (all_are_ready(quiz)) and not (timer_over(quiz)):
        return render(request, 'pages/quiz/quiz_start_wait.html', get_full_context(request, {"quiz": quiz,
                                                                                             "profile_action": profile_action,
                                                                                             "quiz_timer": get_timer(
                                                                                                 quiz)}))

    if not (quiz.started):
        print("Quiz start")
        quiz.started = True
        quiz.timer = (NOW + datetime.timedelta(minutes=QUESTION_TIME)).replace(tzinfo=pytz.UTC)
        quiz.current_question = 0
        quiz.result_show = False
        quiz.save()
        return render(request, 'pages/quiz/quiz_question.html', get_full_context(request, {"quiz": quiz,
                                                                                           "profile_action": profile_action,
                                                                                           "quiz_timer": get_timer(
                                                                                               quiz),
                                                                                           "cur_profile_answer": get_profile_answer(
                                                                                               request, quiz),
                                                                                           "question":
                                                                                               quiz.questions.all()[
                                                                                                   quiz.current_question],
                                                                                           "can_answer": can_answer(
                                                                                               quiz, profile)}))

    if not (timer_over(quiz)) and quiz.result_show:
        print("quiz result show true")
        return render(request, 'pages/quiz/quiz_question_result.html', get_full_context(request, {"quiz": quiz,
                                                                                                  "cur_profile_answer": get_profile_answer(
                                                                                                      request,
                                                                                                      quiz),
                                                                                                  "question":
                                                                                                      quiz.questions.all()[
                                                                                                          quiz.current_question],
                                                                                                  "quiz_timer": get_timer(
                                                                                                      quiz),
                                                                                                  "profile_action":
                                                                                                      QuizProfileActions.objects.all().filter(
                                                                                                          profile=profile,
                                                                                                          quiz=quiz)[
                                                                                                          0]}))
    print("ALL answered", all_answered(quiz))
    print("Result show", quiz.result_show, timer_over(quiz))
    if all_answered(quiz) or timer_over(quiz):
        print("In show", quiz.result_show)
        if quiz.result_show:
            quiz.current_question += 1
            quiz.timer = (NOW + datetime.timedelta(minutes=QUESTION_TIME)).replace(tzinfo=pytz.UTC)
            quiz.result_show = False
            quiz.save(force_update=True)
            return render(request, 'pages/quiz/quiz_question.html', get_full_context(request, {"quiz": quiz,
                                                                                               "profile_action": profile_action,
                                                                                               "quiz_timer": get_timer(
                                                                                                   quiz),
                                                                                               "cur_profile_answer": get_profile_answer(
                                                                                                   request, quiz),
                                                                                               "question":
                                                                                                   quiz.questions.all()[
                                                                                                       quiz.current_question],
                                                                                               "can_answer": can_answer(
                                                                                                   quiz, profile)}))
        else:
            print('UPA calling')
            update_profile_actions(quiz)
            # print('GPA', get_profile_answer(request, quiz).answer, get_profile_answer(request, quiz).points)
            if quiz.current_question + 1 == len(quiz.questions.all()):
                quiz.finished = True
            quiz.timer = (NOW + datetime.timedelta(seconds=10)).replace(tzinfo=pytz.UTC)
            quiz.result_show = True
            quiz.save(force_update=True)
            return render(request, 'pages/quiz/quiz_question_result.html', get_full_context(request, {"quiz": quiz,
                                                                                                      "cur_profile_answer": get_profile_answer(
                                                                                                          request,
                                                                                                          quiz),
                                                                                                      "question":
                                                                                                          quiz.questions.all()[
                                                                                                              quiz.current_question],
                                                                                                      "quiz_timer": get_timer(
                                                                                                          quiz),
                                                                                                      "profile_action":
                                                                                                          QuizProfileActions.objects.all().filter(
                                                                                                              profile=profile,
                                                                                                              quiz=quiz)[
                                                                                                              0]}))

    print("NOT ALL ANSWEREWED", all_answered(quiz))
    if not (all_answered(quiz)):
        return render(request, 'pages/quiz/quiz_question.html', get_full_context(request, {"quiz": quiz,
                                                                                           "profile_action": profile_action,
                                                                                           "quiz_timer": get_timer(
                                                                                               quiz),
                                                                                           "cur_profile_answer": get_profile_answer(
                                                                                               request, quiz),
                                                                                           "question":
                                                                                               quiz.questions.all()[
                                                                                                   quiz.current_question],
                                                                                           "can_answer": can_answer(
                                                                                               quiz, profile)}))
    return redirect('/')


def is_not_ready(request):
    quiz_id = request.POST.get('quiz_id')
    quiz = get_object_or_404(Quiz, id=quiz_id)
    profile = get_profile(request)
    profile_action = QuizProfileActions.objects.all().filter(profile=profile, quiz=quiz)

    if profile_action.count() == 0:
        profile_action = QuizProfileActions.objects.create(profile=profile, quiz=quiz)
    else:
        profile_action = profile_action[0]
    profile_action.is_ready = False
    profile_action.save()
    return redirect('/quiz_state' + str(quiz_id))


def add_answer(request):
    if request.method == "POST":
        q_id = request.POST.get("q_id")
        ans_id = request.POST.get("ans_id")
        quiz_id = request.POST.get("quiz_id")
        profile = get_profile(request)
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # print("IN", q_id, ans_id, quiz_id)

        # if QuizProfileActions.objects.filter(quiz=quiz, profile=profile).count() < quiz.current_question:
        #     return redirect('/quiz_state' + str(quiz_id))
        quiz_question = get_object_or_404(QuizQuestion, id=q_id)
        print("OK")
        qa = QuizAnswer.objects.create(quiz=quiz, quiz_question=quiz_question, answer=ans_id, user=request.user)
        print("QA", qa)
        qa.save()
        qpa = QuizProfileActions.objects.filter(quiz=quiz, profile=profile)[0]
        print("QA", qa)
        qpa.answers.add(qa)
        qpa.save()
        return redirect('/quiz_state' + str(quiz_id))
