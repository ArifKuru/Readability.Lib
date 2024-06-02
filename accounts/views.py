import json

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction

# Create your views here.
from accounts.forms import LoginForm,RegisterForm
from django.urls import reverse
from django.shortcuts import render, redirect

from django.contrib import messages
from .forms import RegisterForm
from pages.models import Profile, LanguageSetting
import random



def user_login(request):
    if request.method =="POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user=authenticate(request,username=username,
                              password=password)

            if user is not None:
                if user.is_active:
                    if user.profile.isEmailVerified:
                        login(request,user)
                        return redirect(reverse('pages:main'))
                    else:
                        login(request, user)
                        generate_verification_code()
                        send_verification_code(request.user,otp)
                        return redirect("verifyEmail")
                else:
                    messages.info(request,"Disabled Account")
            else:
                messages.info(request,"Check Your Username and Password")
    else:
        form = LoginForm()

    if request.user.is_authenticated:
        return redirect(reverse('pages:main'))

    return render(request,"login.html",{"form":form})


otp = None


def generate_verification_code():
    global otp
    otp = random.randint(100000, 999999)
    return otp

def send_verification_code(user, code):
    subject = 'Email Verification Code for Readability.Lib'
    message = (f'Thanks For Register to Readability.Lib \n Your verification code is : {code} \n\n If this email does not belong to you,Please ignore it.')
    send_mail(subject, message, 'noreply@readability.lib', [user.email], fail_silently=False)

def user_register(request):
        if request.method == "POST":
            form=RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                user=form.save()
                Profile.objects.create(user=user)
                LanguageSetting.objects.create(user=user)
                generate_verification_code()
                send_verification_code(user,otp)
                login(request, user)
                return redirect("verifyEmail")

        else:
            form = RegisterForm()

        if request.user.is_authenticated:
            return redirect(reverse('pages:main'))

        return render(request,"register.html",{"form":form})

@csrf_exempt
def checkOTP(request):
    global otp
    print(otp)
    data = json.loads(request.body)
    input = int(data.get('input', ''))
    if(input==int(otp)):
        with transaction.atomic():
            request.user.profile.isEmailVerified = True
            request.user.profile.save()
        return JsonResponse({'status': 'success', 'redirect_url': '/accounts/login/'})
    else:
        return  JsonResponse({'status': False})
def verify_Email(request):
    return render(request,"verifyEmail.html")
def user_logout(request):
    logout(request)
    return redirect(reverse('pages:home'))

def dashboard(request):
    pass