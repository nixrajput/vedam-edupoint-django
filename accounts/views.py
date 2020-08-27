from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import auth
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, reverse
from django.template.loader import get_template
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from accounts.forms import SignupForm, ProfileImageForm, ContactForm
from accounts.models import CustomUser, UserProfileImage, TeamMember
from accounts.tokens import user_tokenizer
from VedamEdupoint import settings


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

            message = get_template('accounts/register_email.html').render({'confirm_url': url})

            mail = EmailMessage('Vedam EduPoint Email Confirmation', message, to=[user.email],
                                from_email=settings.DEFAULT_FROM_EMAIL, )
            mail.content_subtype = 'html'
            mail.send()

            return render(request, 'components/success.html', {
                'message1': f'A verification email has been sent to {user.email}.',
                'message2': f'Please verify your account to complete registration.'
            })

    else:
        form = SignupForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            try:
                form.clean()
            except ValidationError:
                return render(request, 'accounts/login.html', {'form': form, 'invalid_creds': True})

            login(request, form.get_user())

            if not request.user.is_valid:
                auth.logout(request)
                return render(request, 'accounts/login.html', {
                    'form': AuthenticationForm(),
                    'message': f'Your account is not verified. Please verify your account to login.'
                })

            if request.user.is_active is False:
                auth.logout(request)
                return render(request, 'accounts/login.html', {
                    'form': AuthenticationForm(),
                    'message': f'Your account is deactivated. Please contact us for any query.'
                })

            return redirect(reverse('home'))

    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


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
            return redirect('home')

    else:
        form = ProfileImageForm()
    return render(request, 'accounts/profile.html', {'profileImg': profile_img, 'form': form})


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

    return render(request, 'accounts/login.html', context)


def confirm_password_reset(request):
    return render(request, 'accounts/reset_password_confirm.html')


def success_confirmation(request):
    return render(request, 'components/success.html')


def about_us(request):
    try:
        logged_in_user = request.user.is_authenticated()
    except TypeError:
        logged_in_user = request.user.is_authenticated

    if logged_in_user:
        try:
            profile_img = [UserProfileImage.objects.filter(user_id=request.user.userId).latest('updated_at')]
        except ObjectDoesNotExist:
            profile_img = []
    else:
        profile_img = []
        

    try:
        user_list = TeamMember.objects.all()
    except ObjectDoesNotExist:
        user_list = []

    context = {
        'user_list': user_list,
        'profileImg': profile_img,
    }

    return render(request, 'about.html', context)


def contact_us(request):
    try:
        logged_in_user = request.user.is_authenticated()
    except TypeError:
        logged_in_user = request.user.is_authenticated

    if logged_in_user:
        try:
            profile_img = [UserProfileImage.objects.filter(user_id=request.user.userId).latest('updated_at')]
        except ObjectDoesNotExist:
            profile_img = []
    else:
        profile_img = []

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()

            name = form.cleaned_data['full_name']
            message = form.cleaned_data['comment']
            sender = form.cleaned_data['email']
            subject = form.cleaned_data['subject']

            message = get_template('accounts/contact_email.html').render(
                {'message': message, 'sender': sender, 'name': name})

            mail = EmailMessage(subject=subject, body=message, from_email=settings.DEFAULT_FROM_EMAIL,
                                to=[settings.EMAIL_HOST_USER])

            mail.content_subtype = 'html'
            mail.send()

            return render(request, 'components/success.html', {
                'message1': f'Your message has been sent successfully.',
                'message2': f'Thank you for your valuable message.'
            })

    else:
        form = ContactForm()
    return render(request, 'contact.html', {'profileImg': profile_img, 'form': form})
