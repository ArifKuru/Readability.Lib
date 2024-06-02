from django import forms
from pages.models import LanguageSetting


class LanguageSettingForm(forms.ModelForm):
    class Meta:
        model = LanguageSetting
        fields = ['ReadingLanguage', 'TranscribeLanguage', 'Reader_gender',"TranslateLanguage"]