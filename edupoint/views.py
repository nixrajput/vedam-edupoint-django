from django.contrib.auth import login
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.conf import settings

from .forms import *
from .models import *
from .tokens import *


@login_required(login_url='login')
def home(request):
    current_user = request.user

    try:
        profile_img = [UserProfileImage.objects.filter(user_id=current_user.userId).latest('updated_at')]
    except ObjectDoesNotExist:
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


@login_required(login_url='login')
def online_test(request):
    current_user = request.user
    # qstn_list = Question.objects.all()
    # paginator = Paginator(qstn_list, 1)
    # page_num = request.GET.get('page', 1)
    #
    # try:
    #     qstn_obj = paginator.page(page_num)
    # except PageNotAnInteger:
    #     qstn_obj = paginator.page(1)
    # except EmptyPage:
    #     qstn_obj = paginator.page(paginator.num_pages)

    test_list = TestPaper.objects.all()

    try:
        profile_img = [UserProfileImage.objects.filter(user_id=current_user.userId).latest('updated_at')]
    except ObjectDoesNotExist:
        profile_img = []

    return render(request, 'online-test.html', {'test_list': test_list, 'profileImg': profile_img})


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

            message = get_template('register_email.html').render({'confirm_url': url})

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

            message = get_template('contact_email.html').render({'message': message, 'sender': sender, 'name': name})

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
