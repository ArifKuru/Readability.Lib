from django.contrib import admin
from django.urls import path,include
from accounts import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("verifyEmail/",views.verify_Email,name="verifyEmail"),
    path("login/",views.user_login,name="login"),
    path("register/", views.user_register, name="register"),
    path("dashboard/",views.dashboard,name="dashboard"),
    path("logout/",views.user_logout,name="logout"),
    path("reset_password/",auth_views.PasswordResetView.as_view(template_name="accounts/reset_password.html"),name="reset_password"),
    path("reset_password_sent/", auth_views.PasswordResetDoneView.as_view(template_name="accounts/reset_password_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>", auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset_password_complete/", auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), name="password_reset_complete"),
    path("check-otp/",views.checkOTP,name="check-otp")
]
