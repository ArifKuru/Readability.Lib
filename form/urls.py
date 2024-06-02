
from django.contrib import admin
from django.urls import path,include
from form import views

app_name = 'form'

urlpatterns = [
    path('<str:category>/', views.form_page, name='form'),
    path("detail/<int:story_id>", views.form_detail, name="detail"),
    path('create_comment/<int:story_id>/', views.CreateComment, name='create_comment'),
    path("create_rating/placeholder",views.create_rating,name="create_rating"),
    path("voice_command_transcribe/",views.voice_command_transcribe,name="voice_command_transcribe"),
]
