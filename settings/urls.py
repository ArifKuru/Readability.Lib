from django.contrib import admin
from django.urls import path,include
from . import views

app_name ='settings'

urlpatterns = [
    path("", views.settings, name="settings"),
    # path("listVoices",views.list_voices, name="listVoices")
]
