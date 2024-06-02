from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from google.cloud import texttospeech

from accounts.decorators import email_verification_required
from pages.models import LanguageSetting
from settings.forms import LanguageSettingForm


# Create your views here.
@email_verification_required
def settings(request):
    current_user = request.user
    language_setting_instance, created = LanguageSetting.objects.get_or_create(user=current_user)

    if request.method == 'POST':
        form = LanguageSettingForm(request.POST, instance=language_setting_instance)
        if form.is_valid():
            form.save()
            return redirect(reverse("pages:main"))
    else:
        form = LanguageSettingForm(instance=language_setting_instance)

    return render(request, 'settings.html', {'form': form})

# def list_voices(request):
#     """Lists the available voices."""
#     client = texttospeech.TextToSpeechClient.from_service_account_file("key.json")
#
#     # Performs the list voices request
#     voices = client.list_voices()
#
#     voice_data = []
#
#     for voice in voices.voices:
#         # Display the voice's name. Example: tpc-vocoded
#         print(f"Name: {voice.name}")
#         voice_info = {
#             'name': voice.name,
#             'language_codes': voice.language_codes,
#             'ssml_gender': texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
#             'natural_sample_rate_hertz': voice.natural_sample_rate_hertz
#         }
#         voice_data.append(voice_info)
#         # Display the supported language codes for this voice. Example: "en-US"
#         for language_code in voice.language_codes:
#             print(f"Supported language: {language_code}")
#
#         ssml_gender = texttospeech.SsmlVoiceGender(voice.ssml_gender)
#
#         # Display the SSML Voice Gender
#         print(f"SSML Voice Gender: {ssml_gender.name}")
#
#         # Display the natural sample rate hertz for this voice. Example: 24000
#         print(f"Natural Sample Rate Hertz: {voice.natural_sample_rate_hertz}\n")
#
#     return JsonResponse({'voices': voice_data})


