from django.contrib.auth.forms import UserCreationForm, forms

from accounts.models import CustomUser, UserProfileImage, ContactUs
import datetime


class SignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'dob')

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')

        return email

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')

        diff = abs(datetime.date.today() - dob)

        if (diff.days / 365) < 6:
            raise forms.ValidationError("Sorry, you are too young. Your age should be more than 6 years.")

        return dob


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = UserProfileImage
        fields = ['img']


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ['full_name', 'email', 'subject',  'comment']
