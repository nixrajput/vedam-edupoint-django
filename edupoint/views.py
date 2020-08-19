from django.contrib.auth import login
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.views.generic import ListView, DetailView, FormView, TemplateView

from .forms import *
from .models import *
from .tokens import *


def home(request):

    try:
        logged_in_user = request.user.is_authenticated()
    except TypeError:
        logged_in_user = request.user.is_authenticated

    if logged_in_user:
        current_user = request.user
        try:
            profile_img = [UserProfileImage.objects.filter(user_id=current_user.userId).latest('updated_at')]
        except ObjectDoesNotExist:
            profile_img = []
    else:
        profile_img = []

    return render(request, 'home.html', {'profileImg': profile_img})


@login_required(login_url='login')
def profile(request, username):
    current_user = request.user
    try:
        profile_img = [UserProfileImage.objects.filter(user_id=current_user.userId).latest('updated_at')]
    except ObjectDoesNotExist:
        profile_img = []

    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES)

        if form.is_valid():
            fs = form.save(commit=False)
            fs.user = current_user
            fs.save()
            return redirect(reverse('profile'))

    else:
        form = ProfileImageForm()
    return render(request, 'profile.html', {'profileImg': profile_img, 'form': form})


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
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UserProgressView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['paper_scores'] = progress.list_all_paper_scores
        context['tests'] = progress.show_tests()
        return context


class TestMarkingList(TestMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting
    template_name = 'sitting_list.html'

    def get_queryset(self):
        queryset = super(TestMarkingList, self).get_queryset().filter(complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset


class TestMarkingDetail(TestMarkerMixin, DetailView):
    model = Sitting
    template_name = 'sitting_detail.html'

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(TestMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] = context['sitting'].get_questions(with_answers=True)
        return context


class TestListView(ListView):
    model = TestPaper
    template_name = 'test_list.html'

    def get_queryset(self):
        queryset = super(TestListView, self).get_queryset()
        return queryset.filter(roll_out=True)


class TestDetailView(DetailView):
    model = TestPaper
    slug_field = 'slug'
    template_name = 'test_detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.roll_out is not True:
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class TestTakeView(FormView):
    form_class = QuestionForm
    template_name = 'online_test.html'
    result_template_name = 'result.html'
    single_complete_template_name = 'single_complete.html'

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
            self.sitting = Sitting.objects.user_sitting(request.user, self.testpaper)

        if self.sitting is False:
            return render(request, self.single_complete_template_name)

        return super(TestTakeView, self).dispatch(request, *args, **kwargs)

    def get_form(self, *args, **kwargs):
        if self.logged_in_user:
            self.question = self.sitting.get_first_question()
            self.progress = self.sitting.progress()

        form_class = self.form_class

        return form_class(**self.get_form_kwargs())

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
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

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
            'quiz': self.testpaper,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_testpaper_complete()

        if self.testpaper.answers_at_end:
            results['questions'] = self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] = self.sitting.get_incorrect_questions

        if self.testpaper.exam_paper is False:
            self.sitting.delete()

        return render(self.request, self.result_template_name, results)


def register_user(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_valid = False
            user.save()

            token = user_tokenizer.make_token(user)
            user_id = urlsafe_base64_encode(force_bytes(user.userId))

            if settings.DEBUG:
                url = 'http://127.0.0.1:8000' + reverse('confirm_email', kwargs={'user_id': user_id, 'token': token})

            else:
                url = 'https://vedam-edupoint.herokuapp.com' + reverse('confirm_email',
                                                                       kwargs={'user_id': user_id, 'token': token})

            message = get_template('components/register_email.html').render({'confirm_url': url})

            mail = EmailMessage('Vedam EduPoint Email Confirmation', message, to=[user.email],
                                from_email=settings.DEFAULT_FROM_EMAIL, )
            mail.content_subtype = 'html'
            mail.send()

            return render(request, 'success.html', {
                'message1': f'A verification email has been sent to {user.email}.',
                'message2': f'Please verify your account to complete registration.'
            })

    else:
        form = SignupForm()
    return render(request, 'register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            try:
                form.clean()
            except ValidationError:
                return render(request, 'login.html', {'form': form, 'invalid_creds': True})

            login(request, form.get_user())

            if request.user.is_valid:
                return redirect(reverse('home'))
            else:
                auth.logout(request)
                return render(request, 'login.html', {
                    'form': AuthenticationForm(),
                    'message': f'Your account is not verified. A verification email has been sent to your email.'
                               f'Please verify your account to complete registration. '
                })

    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def confirm_registration(request, user_id, token):
    user_id = force_text(urlsafe_base64_decode(user_id))

    user = CustomUser.objects.get(userId=user_id)

    context = {
        'form': AuthenticationForm(),
        'message': 'Email verification error. Please click the forgot password to generate a new '
                   'verification email. '
    }
    if user and user_tokenizer.check_token(user, token):
        user.is_valid = True
        user.save()
        context['message'] = 'Verification complete. Please login to your account.'

    return render(request, 'login.html', context)


def confirm_password_reset(request):
    return render(request, 'reset_password_confirm.html')


def success_confirmation(request):
    return render(request, 'success.html')


def about_us(request):
    try:
        user_list = TeamMember.objects.all()
    except ObjectDoesNotExist:
        user_list = []

    context = {
        'user_list': user_list,
    }

    return render(request, 'about.html', context)


def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()

            name = form.cleaned_data['full_name']
            message = form.cleaned_data['comment']
            sender = form.cleaned_data['email']
            subject = form.cleaned_data['subject']

            message = get_template('components/contact_email.html').render({'message': message, 'sender': sender, 'name': name})

            mail = EmailMessage(subject=subject, body=message, from_email=settings.DEFAULT_FROM_EMAIL,
                                to=[settings.EMAIL_HOST_USER])

            mail.content_subtype = 'html'
            mail.send()

            return render(request, 'success.html', {
                'message1': f'Your message has been sent successfully.',
                'message2': f'Thank you for your valuable message.'
            })

    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})
