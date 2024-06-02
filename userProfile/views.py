from django.shortcuts import render, redirect
import os
import time
import requests
from datetime import datetime
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
import openai
import json
# You can access the image with PIL.Image for example
import io
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from google.cloud import texttospeech

from accounts.decorators import email_verification_required
from pages.models import Story, Profile, Comment
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files import File

from userProfile.forms import ProfileForm


# Create your views here.
@email_verification_required
def visit_Profile(request,username):
    visited_user=get_object_or_404(User,username=username)
    comments = Comment.objects.filter(user=visited_user).order_by("-id")

    if (visited_user==request.user):
        stories= Story.objects.filter(author=visited_user).order_by('-storyId')
        form = ProfileForm(instance=visited_user.profile)

        context = {
            "stories": stories,
            'form': form,
            "comments":comments

        }
        return render(request, "profile.html", context)
    stories = Story.objects.filter(author=visited_user,isPublic=True).order_by('-storyId')

    context={
        "stories": stories,
        'visited': visited_user,
        "comments": comments

    }
    return render(request,"visit_Profile.html",context)

@email_verification_required
def profile(request):
    current_user = request.user
    stories = Story.objects.filter(author=current_user).order_by('-storyId')
    comments= Comment.objects.filter(user=current_user).order_by("-id")
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=current_user.profile)
        if form.is_valid():
            if current_user.profile.image=="":
                current_user.profile.image="profiles/default_profile.png"
                current_user.profile.save()
            form.save()
            # Profil başarıyla güncellendi, başka bir sayfaya yönlendirilebilirsiniz.
    else:
        form = ProfileForm(instance=current_user.profile)

    context = {
        "stories": stories,
        'form': form,
        "comments":comments
    }
    return render(request, "profile.html", context)

def removeProfileImg(request):
    current_user = request.user
    current_user.profile.image = '/media/profiles/default_profile.png'
    current_user.profile.save()
    return JsonResponse("isRemoved",True)

