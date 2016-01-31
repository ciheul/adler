from django import forms
from django.forms.utils import ErrorList


class PasswordResetForm(forms.Form):
    """Force user to input password by complexity. Check settings.py for
       configuration. Field 'PasswordField' is from django-passwords."""
    # new_password1 = PasswordField()
    # new_password2 = PasswordField()
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean(self):
        cd = self.data

        if cd['new_password1'] != cd['new_password2']:
            self._errors['new_password2'] = ErrorList(['Password yang diisikan ke kedua kolom tidak sama.'])
        return self.cleaned_data

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
