
from django.contrib import admin
from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views


app_name = 'profile'

urlpatterns = [
    path('',views.profile,name="profile"),
    path('remove_profile_img/', views.removeProfileImg, name='remove_profile_img'),
    path("change_password/", auth_views.PasswordChangeView.as_view(template_name="accounts/change_password.html"),
         name="change_password"),
    path("password_change_done/",auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"),name="password_change_done"),
    path('<str:username>/', views.visit_Profile, name='visit_profile'),
]
