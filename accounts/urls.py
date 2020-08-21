from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings

from . import views
from accounts.tokens import user_tokenizer

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_user, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('confirm-email/<str:user_id>/<str:token>/', views.confirm_registration, name='confirm_email'),
    path('confirm-password-reset/', views.confirm_password_reset, name='confirm-password-reset'),
    path('success/', views.success_confirmation, name='success'),
    path(
        'reset-password/',
        auth_views.PasswordResetView.as_view(
            template_name='reset_password.html',
            html_email_template_name='components/reset_password_email.html',
            subject_template_name='components/reset_password_subject.txt',
            success_url='/confirm_password_reset/',
            token_generator=user_tokenizer),
        name='reset_password'
    ),

    path(
        'reset-password-confirmation/<str:uidb64>/<str:token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='reset_password_update.html',
            post_reset_login=True,
            post_reset_login_backend='django.contrib.auth.backends.ModelBackend',
            token_generator=user_tokenizer,
            success_url=settings.LOGIN_REDIRECT_URL),
        name='password_reset_confirm'
    ),

    path('about-us/', views.about_us, name='about'),
    path('contact-us/', views.contact_us, name='contact'),
]
