from django import forms
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label


class MailForm(forms.Form):
    mail_address = forms.CharField(
        label = 'Mail Address',
        max_length = 100,
        required = True,
        widget = forms.TextInput()
    )



