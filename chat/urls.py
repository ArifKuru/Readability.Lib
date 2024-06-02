
from django.contrib import admin
from django.urls import path,include
from chat import views

app_name = 'chat'

urlpatterns = [
    path("<str:username>/",views.chat_panel,name="chat_panel"),
    path("messages/<str:username>/", views.message_panel, name="message_panel"),
    path("general/send_message/",views.sendMessage,name="send_message"),
    path("general/check_new_messages/",views.check_new_messages,name="check_new_messages")
]
