from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'style': 'width: 60%; margin: 0 auto; border: 2px solid black; border-radius: 0; background-color: #EBB42C;',
                                                             'placeholder': 'Enter your username here*'}))

    password = forms.CharField(widget=forms.PasswordInput(attrs={'id': "id_password",
                                                                    'class': 'form-control',
                                                                 'style': 'width: 60%; margin: 0 auto; border: 2px solid black; border-radius: 0; background-color: #EBB42C;',
                                                                 'placeholder': 'Password*'}))


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                               'style': 'width: 30%; border: 2px solid black; border-radius: 0; background-color: #EBB42C;',
                                                               'placeholder': 'First name*'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                              'style': 'width: 30%; border: 2px solid black; border-radius: 0; background-color: #EBB42C; margin-left: 10px;',
                                                              'placeholder': 'Last name*'}))

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control',
                                                             'style': 'width: 60%; margin: 0 auto; border: 2px solid black; border-radius: 0; background-color: #EBB42C;',
                                                             'placeholder': 'Username*'}))

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control',
                                                            'style': 'width: 60%; margin: 0 auto; border: 2px solid black; border-radius: 0; background-color: #EBB42C;',
                                                            'placeholder': 'Enter your E-mail here*'}))

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'id': "id_password1",
                                                                  'class': 'form-control',
                                                                 'style': 'width: 60%; margin: 0 auto; border: 2px solid black; border-radius: 0; background-color: #EBB42C;',
                                                                 'placeholder': 'Password*'}))

    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'id': "id_password2",'class': 'form-control', 'style': 'width: 60%; margin: 0 auto; border: 2px solid black; border-radius: 0; background-color: #EBB42C;', 'placeholder': 'Retype Password*'}))



    class Meta:
        model = User
        fields = ["first_name","last_name","username","email","password1","password2"]