from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=50)
    email = forms.CharField(max_length=65)
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)
