import json

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, FormView, TemplateView

from accounts.models import UserProfileImage
from edupoint.forms import QuestionForm
from edupoint.models import TestPaper, Sitting, Progress
from rest_framework.views import APIView
from rest_framework.response import Response


def home(request):
    try:
        logged_in_user = request.user.is_authenticated()
    except TypeError:
        logged_in_user = request.user.is_authenticated

    if logged_in_user:
        current_user = request.user
        try:
            profile_img = [UserProfileImage.objects.filter(
                user_id=current_user.userId).latest('updated_at')]
        except ObjectDoesNotExist:
            profile_img = []
    else:
        profile_img = []

    return render(request, 'home.html', {'profileImg': profile_img})


class TestMarkerMixin(object):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TestMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        test_filter = self.request.GET.get('test_filter')
        if test_filter:
            queryset = queryset.filter(testpaper__name__icontains=test_filter)

        return queryset


class UserProgressView(TemplateView):
    template_name = 'tests/progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserProgressView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        context['tests'] = progress.show_tests()

        try:
            self.logged_in_user = self.request.user.is_authenticated()
        except TypeError:
            self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            try:
                profile_img = [UserProfileImage.objects.filter(
                    user_id=self.request.user.userId).latest('updated_at')]
            except ObjectDoesNotExist:
                profile_img = []
        else:
            profile_img = []

        context['profileImg'] = profile_img
        return context


class TestMarkingList(TestMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting
    template_name = 'tests/sitting_list.html'

    def get_queryset(self):
        queryset = super(TestMarkingList, self).get_queryset().filter(
            complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset


class TestMarkingDetail(TestMarkerMixin, DetailView):
    model = Sitting
    template_name = 'tests/sitting_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TestMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] = context['sitting'].get_questions(
            with_answers=True)
        return context


class TestListView(ListView):
    model = TestPaper
    template_name = 'tests/test_list.html'

    def get_context_data(self, **kwargs):
        context = super(TestListView, self).get_context_data(**kwargs)

        try:
            self.logged_in_user = self.request.user.is_authenticated()
        except TypeError:
            self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            try:
                profile_img = [UserProfileImage.objects.filter(
                    user_id=self.request.user.userId).latest('updated_at')]
            except ObjectDoesNotExist:
                profile_img = []
        else:
            profile_img = []

        context['profileImg'] = profile_img

        return context

    def get_queryset(self):
        queryset = super(TestListView, self).get_queryset()
        return queryset.filter(roll_out=True)


class TestDetailView(DetailView):
    model = TestPaper
    slug_field = 'slug'
    template_name = 'tests/test_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.roll_out is not True:
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super(TestDetailView, self).get_context_data(**kwargs)

        try:
            self.logged_in_user = self.request.user.is_authenticated()
        except TypeError:
            self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            try:
                profile_img = [UserProfileImage.objects.filter(
                    user_id=self.request.user.userId).latest('updated_at')]
            except ObjectDoesNotExist:
                profile_img = []
        else:
            profile_img = []

        context['profileImg'] = profile_img

        return context


class TestTakeView(FormView):
    form_class = QuestionForm
    template_name = 'tests/online_test.html'
    result_template_name = 'tests/result.html'
    single_complete_template_name = 'tests/single_complete.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.testpaper = get_object_or_404(TestPaper, slug=self.kwargs['slug'])
        if self.testpaper.roll_out is not True:
            raise PermissionDenied

        try:
            self.logged_in_user = self.request.user.is_authenticated()
        except TypeError:
            self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            self.sitting = Sitting.objects.user_sitting(
                request.user, self.testpaper)

            try:
                profile_img = [UserProfileImage.objects.filter(
                    user_id=self.request.user.userId).latest('updated_at')]
            except ObjectDoesNotExist:
                profile_img = []

            self.profile_img = profile_img

        if self.sitting is False:
            context = {
                'profileImg': self.profile_img
            }
            return render(request, self.single_complete_template_name, context)

        return super(TestTakeView, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
            self.progress = self.sitting.progress()

        form_ = self.form_class

        return form_(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(TestTakeView, self).get_form_kwargs()
        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        if self.logged_in_user:
            self.form_valid_user(form)
            if self.sitting.get_first_question() is False:
                return self.final_result_user()

        self.request.POST = {}

        return super(TestTakeView, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(TestTakeView, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['testpaper'] = self.testpaper
        context['sitting'] = self.sitting
        context['profileImg'] = self.profile_img
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(self.testpaper.correct_marking)
            progress.update_score(self.question, 1, 0, 1)

        elif is_correct == 'skipped':
            self.sitting.add_to_score(0)
            self.sitting.add_skipped_question(self.question)
            progress.update_score(self.question, 0, 1, 1)

        else:
            self.sitting.add_to_score(-self.testpaper.negative_marking)
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 0, 1)

        if self.testpaper.answers_at_end is not True:
            self.previous = {'previous_answer': guess,
                             'previous_outcome': is_correct,
                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question.__class__.__name__: True}}
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            'paper': self.testpaper,
            'score': self.sitting.get_current_score,
            'negative_score': self.sitting.get_negative_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_testpaper_complete()

        if self.testpaper.answers_at_end:
            results['questions'] = self.sitting.get_questions(
                with_answers=True)
            results['incorrect_questions'] = self.sitting.get_incorrect_questions
            results['skipped_questions'] = self.sitting.get_skipped_questions
            results['profileImg'] = self.profile_img

        if self.testpaper.save_record is False:
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)
