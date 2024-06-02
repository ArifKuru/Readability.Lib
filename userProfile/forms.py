from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Choices
from django.forms import ModelForm, TextInput, Textarea,Select,ImageField,ClearableFileInput

from pages.models import Profile


class ProfileForm(ModelForm):
    class Meta:
        model = Profile
        fields = ["bio", "gender", "country","image"]
        widgets = {
            'bio': Textarea(attrs={
                'class': "form-control",
                'style': 'max-width: 400px;color: white;background-color: transparent',

                'placeholder': 'Write here about you ,for other authors!'
            }),
             'gender': Select({
                 'class': "form-select form-select-custom",
                 'style': 'max-width: 400px;color: white;background-color: transparent',
             }),
            'country': Select({
                'class': "form-select form-select-custom",
                'style': 'max-width: 400px;color: white;background-color: transparent',
            }),


        }
