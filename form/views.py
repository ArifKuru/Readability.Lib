import json
import google.generativeai as genai
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from google.cloud import speech

from accounts.decorators import email_verification_required
from pages.models import Story, Comment, Rating, LanguageSetting


# Create your views here.

@email_verification_required
def form_page(request,category):
    if(category=="All"):
        stories = Story.objects.filter(isPublic=True).order_by('-storyId')
    else:
        stories = Story.objects.filter(isPublic=True,category=category).order_by('-storyId')

    context = {
        'stories': stories,
        "category": category
    }
    return render(request,"form/form_flow.html",context)

@email_verification_required
def form_detail(request,story_id):
    current_user = request.user
    story = get_object_or_404(Story, storyId=story_id)
    comments=Comment.objects.filter(story=story).order_by("-id")
    ratings = Rating.objects.filter(story=story)
    context = {
        "story": story,
        "comments": comments,
        "ratings":ratings
    }
    return render(request,"form/form_detail.html",context)

def CreateComment(request,story_id):
    if request.method=="POST":
        content = request.POST.get('content')  # Formdan gelen içeriği al
        currrent_user=request.user
        story = get_object_or_404(Story, storyId=story_id)
        new_comment = Comment(content=content, user=currrent_user, story=story)
        new_comment.save()
        comments = Comment.objects.filter(story=story).order_by("-id")
        context = {
            "story": story,
            "comments": comments
        }
        return  redirect('form:detail', story_id=story_id)

def create_rating(request):
    if request.method == "POST":
        print("create_rating")
        current_user = request.user
        is_liked = request.POST.get("isLiked")
        print(is_liked)
        story_id = request.POST.get("story")

        # Hikaye ve kullanıcıyı al
        story = get_object_or_404(Story, storyId=story_id)
        rating = Rating.objects.filter(user=current_user, story=story).first()
        if(rating):
            if(int(is_liked)==rating.isLiked):
                print(rating.isLiked)
                rating.delete()
            else:
                rating.isLiked=is_liked
                rating.save()
        else:
            new_rating = Rating.objects.create(
                isLiked=is_liked,
                story=story,
                user=current_user
            )
            new_rating.save()
        # Başarı mesajı döndür
        response_data = {"message": "Derecelendirme oluşturuldu."}
        return redirect('form:detail', story_id=story_id)
    else:
        # POST dışındaki istekleri reddedin
        return JsonResponse({"error": "Sadece POST istekleri kabul edilir."}, status=405)

def voice_command(prompt):

    # Set up the model
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    system_instruction = "if the user enter something related with take it back return 1,\nelse if user enter something related with  stop return 2,\nelse if user enter something related with  start return 3,\nelse if user enter something related with fast forward return 4,\nelse return 5."

    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                    generation_config=generation_config,
                                    system_instruction=system_instruction,
                                    safety_settings=safety_settings)

    command = model.start_chat(history=[
    ])

    command.send_message(prompt)
    print(command.last.text)
    response = JsonResponse({'command': command.last.text})
    return response

@csrf_exempt
def voice_command_transcribe(request):
    if request.method == 'POST':
        print("geldi")
        client = speech.SpeechClient.from_service_account_file("key.json")
        file_data = request.FILES['audio_file'].read()
        current_user = request.user
        settings = LanguageSetting.objects.get(user=current_user)
        audio_file = speech.RecognitionAudio(content=file_data)

        config = speech.RecognitionConfig(
            enable_automatic_punctuation=True,
            language_code=settings.TranscribeLanguage,
        )

        response = client.recognize(
            config=config,
            audio=audio_file
        )

        transcripts = [result.alternatives[0].transcript for result in response.results]
        print(transcripts)
        result =voice_command(transcripts)
        return result

    return JsonResponse({'error': 'Method not allowed'}, status=405)
