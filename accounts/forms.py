from django.contrib.auth.forms import UserCreationForm, forms

from accounts.models import *


class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'dob')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        else:
            return email


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserProfileImage
        fields = ['img']


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['full_name', 'email', 'subject',  'comment']
