import random

from django.core.serializers import serialize
import os
from transformers import pipeline
import tempfile
import torch
from pathlib import Path
import hashlib
import time
import requests
from datetime import datetime
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
import openai
import json
# You can access the image with PIL.Image for example
import io
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from google.cloud import texttospeech

from accounts.decorators import email_verification_required
from accounts.views import generate_verification_code, send_verification_code, otp
from pages.models import Story, Profile, LanguageSetting, Interactive, Interactive_Story, InteractiveGame, \
    InteractiveContent, Pdf, Page, Room_for_2p, Room_for_3p, Room_for_4p, second_player_respond, third_player_respond, \
    fourth_player_respond
from django.utils import timezone
from django.core.files import File
from google.cloud import speech
from google.cloud.texttospeech import SsmlVoiceGender
import google.generativeai as genai
from django.shortcuts import render


# Create your views here.
openai.api_key = "*"
genai.configure(api_key="*")
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": "Bearer *"}
generated_text="empty"
def home(request):
    return render(request,"home.html")

@email_verification_required
def main_page(request):
    current_user = request.user
    stories = Story.objects.filter(author=current_user).order_by('-storyId')[:3]
    if current_user.profile.isEmailVerified==False:
        send_verification_code(request.user,generate_verification_code())
        return redirect("verifyEmail")
    return render(request,"main_page.html", {'stories': stories})

@email_verification_required
def generated(request,story_id):
    current_user=request.user
    story = get_object_or_404(Story, storyId=story_id)

    return render(request,"generated.html",{"story": story})

def make_visibility(request, story_id):
    story = get_object_or_404(Story, pk=story_id)

    if request.method == 'POST':
        is_public = request.POST.get('visibility') == 'on'  # 'on' değeri checkbox işaretliyken alınan değerdir
        story.isPublic = is_public
        story.save()
        return redirect('pages:generated',
                        story_id=story_id)  # Değiştirilecek olan sayfanın ismini veya URL'sini buraya yazın

    return redirect('pages:generated',
                    story_id=story_id)  # Eğer POST isteği değilse, yine hikaye detay sayfasına yönlendir


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

from pdfminer.high_level import extract_text
from django import forms

class PDFUploadForm(forms.Form):
    pdf_file = forms.FileField(label='Select a PDF file', help_text='max. 10 MB', widget=forms.ClearableFileInput(attrs={'accept': '.pdf'}))



def extract_text_from_pdf(file):
    text = extract_text(file)
    return text
from django import forms
from pdfminer.high_level import extract_text

def extract_pages(pdf_file):
    pages = []
    content = pdf_file.read()
    pdf_io = io.BytesIO(content)
    for page in extract_text(pdf_io).split('\x0c'):
        pages.append(page.strip())
    return pages

def read_pdf(request,pdf_id):
    my_pdf = get_object_or_404(Pdf, id=pdf_id)
    my_pages=Page.objects.filter(partOf=my_pdf)
    context={
        'pdf':my_pdf,
        'my_pages':my_pages
    }
    return render(request,"read_pdf.html",context)

@csrf_exempt
def read_pdf_onload(request):
    print("read - pdf - onload has been requested")
    data = json.loads(request.body)
    pdf_id = data.get('pdf_id', '')
    my_pdf = get_object_or_404(Pdf, id=pdf_id)
    pages = Page.objects.filter(partOf=my_pdf)
    # Sadece içerikleri al
    contents = [page.content for page in pages]
    print(contents)
    return JsonResponse({'pages': contents})

@email_verification_required
def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = request.FILES['pdf_file']
            new_pdf=Pdf(content=pdf_file.name,user=request.user)
            new_pdf.save()
            pages = extract_pages(pdf_file)
            image_bytes = query({
                "inputs": sumUpWithText(pages),
            })
            image = Image.open(io.BytesIO(image_bytes))
            image.save(f"media/pdfs/images/{new_pdf.id}.jpg")
            new_pdf.image = f"pdfs/images/{new_pdf.id}.jpg"
            new_pdf.save()
            for page in pages:
                if page:
                    new_page = Page(content=page,partOf=new_pdf)
                    new_page.save()
            print(pages)
            return JsonResponse({'id': new_pdf.id})
    else:
        form = PDFUploadForm()
    return render(request, 'upload.html', {'form': form})
@email_verification_required
def extract_page(request):
    my_pdfs = Pdf.objects.filter(user=request.user)
    return render(request, 'extract.html',{"pdfs":my_pdfs})

@csrf_exempt
def save_extracted_page(request):
    current_user = request.user
    data = json.loads(request.body)
    input = data.get("input", "")
    return True

def generate_story_gemini(request):

    if request.method == 'POST':

        data = json.loads(request.body)

        prompt = data.get('prompt', '')

        category = data.get("category","")

        word_size=data.get("word_size","")


        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        system_instruction = f"1.You are Story Teller \n2.Create Story Based Prompt\n3.Never ask anything user you have to create directly no return anything only story\n4.Story Category is:${category}\n5.Story Word-Size: ${word_size} ,Never Exceed it bemind word-size limitation\n6.End Story With The End.7.After the story ,and after write The End. write ???portrayal??? and start to portrayal an image for story related with content with, never mix the order First Story and end it with The End. then portrayal image for ai model with image details and start with ???portrayal???,\n8.Try to make story close to {word_size} and do not count portrayal part in this limit"

        model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                      generation_config=generation_config,
                                      system_instruction=system_instruction,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[
        ])

        convo.send_message(prompt)
        generated_text=convo.last.text
        divide_point=generated_text.index("???portrayal???")
        story_part=generated_text[:divide_point]
        portrayal_part=generated_text[divide_point:].replace("???portrayal???","")+"realistic,4k, colorfully,high quality,good contrast"
        print("story_part:" + story_part)
        print("portrayal_part:"+portrayal_part)

        global new_story

        image_bytes = query({
            "inputs": portrayal_part,
        })
        # You can access the image with PIL.Image for example
        image = Image.open(io.BytesIO(image_bytes))

        # from openai import OpenAI
        #
        #
        # os.environ["OPENAI_API_KEY"] = "*"
        #
        #
        # client = OpenAI()
        #
        #
        # response = client.images.generate(
        #     model="dall-e-3",
        #     prompt=inputs,
        #     size="1024x1024",
        #     quality="standard",
        #     n=1,
        # )
        #
        # image_url = response.data[0].url
        # print(image_url)

        new_story=Story(author=request.user,wordSize=word_size,category=category,content = story_part,prompt=prompt,createDate=datetime.now())
        new_story.save()
        path = new_story.storyId
        image.save(f"media/stories/story{path}.jpg")
        new_story.image=f"stories/story{path}.jpg"
        new_story.save()

        return JsonResponse({'story': new_story.storyId})



@csrf_exempt
def translate(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        input=data.get("input","")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            temperature=1,
            messages=[
                {"role": "system", "content": f"Translate to {request.user.languagesetting.TranslateLanguage}"},
                {"role": "user",
                 "content": f"Translate this:{input}"}

            ]
        )
        generated_text = response.choices[0].message.content.strip()

        print(generated_text)

        return JsonResponse({'translated': generated_text})


def generate_story(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        category = data.get("category","")
        word_size=data.get("word_size","")
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            temperature=1,
            messages=[
                {"role": "system", "content": "Only Create Story Nothing else"},
                {"role": "system",
                 "content": "Choose a specific category (e.g., horror, adventure, science fiction, etc.)."},
                {"role": "system",
                 "content": "Specify the word count for your story. Be mindful of this limit and do not exceed it."},
                {"role": "system", "content": "At the worst case if you cannot generate story based user prompt ,create a story related only category"},

                {"role": "system", "content": "Remember to end your story with the phrase 'The End'."},
                {"role": "user", "content": f"You have to finish this sentence as story start to Story with this ("
                                            f"note that you must give me story nothing else,no matter what):{prompt}"
                                            f" and also consider Category:{category} and word-count {word_size},"
                                            f"Be mindful of this limit and do not exceed it."}
            ]
        )
        generated_text = response.choices[0].message.content.strip()
        global new_story
        portrayal_part="4k,realistic,high-contrast"+generated_text

        image_bytes = query({
            "inputs": portrayal_part,
        })
        # You can access the image with PIL.Image for example
        image = Image.open(io.BytesIO(image_bytes))



        new_story=Story(author=request.user,wordSize=word_size,category=category,content = generated_text,prompt=prompt,createDate=datetime.now())
        new_story.save()
        path = new_story.storyId
        image.save(f"media/stories/story{path}.jpg")
        new_story.image=f"stories/story{path}.jpg"
        new_story.save()
        print(new_story.content)
        print(new_story.createDate)
        return JsonResponse({'story': new_story.storyId})

@csrf_exempt
def read(request):
    if request.method=="POST":
        current_user = request.user
        settings = LanguageSetting.objects.get(user=current_user)
        data = json.loads(request.body)
        input = data.get("input","")
        client = texttospeech.TextToSpeechClient.from_service_account_file("key.json")
        synthesis_input = texttospeech.SynthesisInput(text=input)
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )
        voice = texttospeech.VoiceSelectionParams(
            language_code=settings.ReadingLanguage,
            ssml_gender=SsmlVoiceGender[settings.Reader_gender.upper()]
        )
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        with open(os.path.join("static","output.wav"), "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)

        print('Audio content written to file "output.wav"')
        response = JsonResponse({'is_Created': True})
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"  # Tarayıcı önbelleğini atar
        return response




@csrf_exempt
def transcribe(request):
    if request.method == 'POST':
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
        return JsonResponse({'transcripts': transcripts})

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@email_verification_required
def edit(request,story_id):
    story = get_object_or_404(Story, storyId=story_id)
    return render(request,"edit.html",{"story": story})

@email_verification_required
def interactive(request):
    all_games = InteractiveGame.objects.all()
    return render(request,"interactive.html",{"games":all_games})


@email_verification_required
def load_interactives(request,game_id):
    game=get_object_or_404(InteractiveGame, id=game_id)
    histories=game.get_Interactives(request.user)
    context={
        "histories": histories,
        "game":game
    }
    return render(request, "interactive_load.html",context)

@email_verification_required
def interactiveGame(request,interactive_id,game_id):
    try:
        interactive = Interactive.objects.get(id=interactive_id)
    except Interactive.DoesNotExist:
        game = get_object_or_404(InteractiveGame, id=game_id)
        newInteractive = Interactive(user=request.user,gameOf=game)
        newInteractive.save()
        return redirect("pages:interactiveGame" ,game_id=game_id,interactive_id=newInteractive.id)
    context={
        "game": interactive,
        "gameOf": get_object_or_404(InteractiveGame,id=game_id)
    }
    return render(request,"interactive_play.html",context)

def start_Game(request,game_id,room_id):
    game = get_object_or_404(InteractiveGame, id=game_id)
    if game.numberOfPlayer==2:
        room = get_object_or_404(Room_for_2p,id=room_id)
        room.second_player = request.user
    elif game.numberOfPlayer == 3:
        room = get_object_or_404(Room_for_3p, id=room_id)
        if room.second_player is None:
            room.second_player = request.user
        else:
            room.third_player = request.user
    elif game.numberOfPlayer == 4:
        room = get_object_or_404(Room_for_4p, id=room_id)
        if room.second_player is None:
            room.second_player = request.user
        elif room.third_player is None:
            room.third_player = request.user
        else:
            room.fourth_player=request.user

    room.save()

    return JsonResponse({"success":"success"})

def group_Game(request,interactive_id,game_id,room_id):

    try:
        interactive = Interactive.objects.get(id=interactive_id)
    except Interactive.DoesNotExist:
        game = get_object_or_404(InteractiveGame, id=game_id)
        newInteractive = Interactive(user=request.user,gameOf=game)
        newInteractive.save()
        if game.numberOfPlayer == 2:
            room = get_object_or_404(Room_for_2p, id=room_id)
        elif game.numberOfPlayer == 3:
            room = get_object_or_404(Room_for_3p, id=room_id)
        elif game.numberOfPlayer == 4:
            room = get_object_or_404(Room_for_4p, id=room_id)

        room.gameRef=newInteractive
        room.save()
        return redirect("pages:group_game" ,game_id=game_id,interactive_id=newInteractive.id,room_id=room.id)
    gameOf=get_object_or_404(InteractiveGame,id=game_id)
    if gameOf.numberOfPlayer == 2:
        room = get_object_or_404(Room_for_2p, id=room_id)
    elif gameOf.numberOfPlayer == 3:
        room = get_object_or_404(Room_for_3p, id=room_id)
    elif gameOf.numberOfPlayer == 4:
        room = get_object_or_404(Room_for_4p, id=room_id)

    context={
        "game": interactive,
        "gameOf": gameOf,
        "room":room
    }
    return render(request,"group_game/group_game.html",context)


@email_verification_required
def interactive_menu(request,game_id):
    game = get_object_or_404(InteractiveGame, id=game_id)
    return render(request,"interactive_menu.html",{"game":game})


def rooms_list(request,game_id):
    game = get_object_or_404(InteractiveGame, id=game_id)
    if game.numberOfPlayer == 2:
        rooms = Room_for_2p.objects.filter(game=game,isOpen=True)
    elif game.numberOfPlayer == 3:
        rooms = Room_for_3p.objects.filter(game=game,isOpen=True)
    elif game.numberOfPlayer == 4:
        rooms = Room_for_4p.objects.filter(game=game,isOpen=True)

    context={
        "rooms":rooms,
        "game":game
    }
    return render(request, "group_game/rooms_list.html", context)

def create_Room(request,game_id):
    game = get_object_or_404(InteractiveGame, id=game_id)
    random_key = random.randint(100000, 999999)
    print(game.numberOfPlayer)
    if game.numberOfPlayer == 2:
        new_room = Room_for_2p.objects.create(game=game, creator=request.user, key=random_key)
    elif game.numberOfPlayer==3:
        new_room = Room_for_3p.objects.create(game=game, creator=request.user, key=random_key)
    elif game.numberOfPlayer==4:
        new_room = Room_for_4p.objects.create(game=game, creator=request.user, key=random_key)


    return render(request,"group_game/creating_room.html",{"room":new_room})


def Delete_view(request, game_id):
    # Gerekli Django işlemlerini gerçekleştirin
    game = get_object_or_404(InteractiveGame, id=game_id)
    new_interactive = Interactive.objects.filter(user=request.user, gameOf=game).first()
    new_interactive.delete()
    # Burada yeni bir JSON yanıtı oluşturun ve gönderin
    return JsonResponse({'message': 'İlgili veri başarıyla silindi'})

def video_call(request):
    return render(request,"group_game/video_call.html")
@csrf_exempt
def interactive_Ai(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        interactive_id = data.get("interactive_id","")
        game_id =data.get("game_id","")
        game = get_object_or_404(InteractiveGame,id=game_id)
        print(interactive_id)
        new_Interactive = get_object_or_404(Interactive,id=interactive_id)
        print("Generating...")
        print(new_Interactive)

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            }
        ]

        system_instruction = game.instructions


        model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                      generation_config=generation_config,
                                      system_instruction=system_instruction,
                                      safety_settings=safety_settings)
        json_array = []
        histories = new_Interactive.get_stories()
        print(histories)
        if(histories):
            for history in histories:
                json_data = {
                    "role": history.roles,
                    "parts": [history.parts]
                }
                json_array.append(json_data)

        # {
        #     "role": "zser",
        #     "parts": [
        #         {
        #             "text": "start"
        #         }
        #     ]
        # }
        #     {
        #     "role": "model",
        #     "parts": [
        #         {
        #             "text": "Elara, the wind whispers your name through the ancient trees of the Whispering Woods. The gnarled branches seem to reach for you, their leaves rustling secrets only the forest understands. You seek the Gem of Serenity, a jewel whispered to hold the power to calm the most troubled soul. But the path is fraught with peril, and the woods are known to test those who dare enter.\n\nBefore you embark on this journey, choose your tools wisely, for they may be the difference between triumph and tragedy. Will you take up the **Hunter's Bow**, swift and silent, or the **Warrior's Sword**, strong and unwavering? Choose, Elara, and let your journey begin. \n"
        #         }
        #     ]
        # }


        convo = model.start_chat(history=json_array)
        convo.send_message(prompt)
        generated_text = convo.last.text
        print(generated_text)
        story_part = generated_text
        portrayal_part="4k,realistic,colorfully,high-contrast"+story_part
        image_bytes = query({
            "inputs": portrayal_part,
        })
        # You can access the image with PIL.Image for example
        image = Image.open(io.BytesIO(image_bytes))

        user_history = Interactive_Story(parts=prompt, roles="user", partOf=new_Interactive)
        user_history.save()

        model_history= Interactive_Story(parts=story_part,roles="model",partOf=new_Interactive)
        model_history.save()

        new_content = InteractiveContent(content=story_part, partOf=new_Interactive)
        new_content.save()
        image.save(f"media/games/playing/{new_content.id}.jpg")
        new_content.image = f"/games/playing/{new_content.id}.jpg"
        new_content.save()
        response_data = {
            'story': story_part,
        }

        return JsonResponse(response_data)

def check_if_newContent(request):
    try:
        data = json.loads(request.body)
        lastContent_id = data.get('lastContent_id')
        interactive_id=data.get("interactive_id")
        interactive_obj=get_object_or_404(Interactive,id=interactive_id)
        current=interactive_obj.get_last_content().id
        print(current)
        if current == lastContent_id:
            return JsonResponse({'isThere': False})
        else:
            return JsonResponse({'isThere': True})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def history(user,role,part):
    interactive_instance = Interactive.objects.filter(user=user).first()

    # İlgili kullanıcıya yeni bir geçmiş olayı eklemek için aşağıdaki adımları izleyin:
    if interactive_instance:
        history_data = interactive_instance.history
        if not history_data:
            history_data = []
        new_history_item = {"role": role, "parts": part}
        history_data.append(new_history_item)
        interactive_instance.history = history_data
        interactive_instance.save()
    else:
        new_interactive_instance = Interactive.objects.create(user=user,
                                                              history=[{"role": role, "part": part}])
        new_interactive_instance.save()

    return True
def sumUpWithText(text):
        body = text
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        system_instruction = "Give a summary portrayal by this story"
        model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                      generation_config=generation_config,
                                      system_instruction=system_instruction,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[
        ])

        convo.send_message(body)
        summary=convo.last.text
        return summary

def summarize_Gemini(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        body = data.get('body', '')
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        system_instruction = "Give a summary by telling the story in the same way according to the way the text is told."
        model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                      generation_config=generation_config,
                                      system_instruction=system_instruction,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[
        ])

        convo.send_message(body)
        summary=convo.last.text
        return JsonResponse({'sum': summary})

# def Summarize(request):
#     if request.method=="POST":
#         data = json.loads(request.body)
#         body = data.get('body', '')
#         print(body)
#         summarizer = pipeline("summarization", model="Falconsai/text_summarization")
#         sum = summarizer(body, max_length=130, min_length=30, do_sample=False)
#         print(sum)
#         print(sum[0]["summary_text"])
#         print(sum[0]["summary_text"])
#
#         return JsonResponse("sum", str(sum[0]["summary_text"]))


def generate_story_gemini_from_image(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        category = data.get("category","")
        path=data.get("path","")
        word_size=data.get("word_size","")


        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }

        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        uploaded_files = []

        def upload_if_needed(pathname: str) -> list[str]:
            path = Path(pathname)
            print(path)
            print(type(path))
            hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
            try:
                existing_file = genai.get_file(name=hash_id)
                return [existing_file.uri]
            except:
                pass
            uploaded_files.append(genai.upload_file(path=path, display_name=hash_id))
            return [uploaded_files[-1].uri]

        system_instruction = f"1.You are Story Teller \n2.Create Story Based Image\n3.Never ask anything user you have to create directly no return anything only story\n4.Story Category is:${category}\n5.Story Word-Size: ${word_size} ,Never Exceed it bemind word-size limitation\n6.End Story With The End.7.After the story ,and after write The End. write ???portrayal??? and start to portrayal an image for story related with content with, never mix the order First Story and end it with The End. then portrayal image for ai model with image details and start with ???portrayal???,\n8.Try to make story close to {word_size} and do not count portrayal part in this limit"


        # system_instruction ="From user image ,portrayal him like Harry potter character only portrayal the character of user nothing else do not use punctutations only detail of view of character,Add Realistic , 4k Words at the end and in use them while portrayals"
        model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                                      generation_config=generation_config,
                                      system_instruction=system_instruction,
                                      safety_settings=safety_settings)

        convo = model.start_chat(history=[
            {"role": "user", "parts": [genai.upload_file(f"C:\\Users\90551\Desktop\ReadabilityLib\static\images\\{path}")]},

        ])
        prompt = "start"
        convo.send_message(prompt)

        generated_text=convo.last.text
        divide_point = generated_text.index("???portrayal???")
        story_part = generated_text[:divide_point]
        portrayal_part = generated_text[divide_point:].replace("???portrayal???",
                                                               "") + "realistic,4k, colorfully,high-quality,good-contrast"
        print("story_part:" + story_part)
        print("portrayal_part:" + portrayal_part)


        global new_story
        image_bytes = query({
            "inputs": portrayal_part,
        })
        # You can access the image with PIL.Image for example
        image = Image.open(io.BytesIO(image_bytes))

        new_story=Story(author=request.user,wordSize=word_size,category=category,content = story_part,prompt=prompt,createDate=datetime.now())
        new_story.save()

        path = new_story.storyId
        image.save(f"media/stories/story{path}.jpg")
        new_story.image = f"stories/story{path}.jpg"
        new_story.save()
        print(new_story.content)
        print(new_story.createDate)
        for uploaded_file in uploaded_files:
            genai.delete_file(name=uploaded_file.name)
        return JsonResponse({'story': new_story.storyId})

@csrf_exempt
def upload(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        with open('static/images/temp.png', 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        return JsonResponse({'message': "temp.png"})
    return JsonResponse({'message': 'failure'}, status=400)


import torch
from transformers import GPT2Tokenizer

tokenizer = GPT2Tokenizer.from_pretrained('gpt2')


def create_player_respond(request):
    data = json.loads(request.body)
    room_id=data.get("room_id","")
    game_id=data.get("game_id","")
    respond=data.get("respond","")
    current_user=request.user
    game=get_object_or_404(InteractiveGame,id=game_id)
    if game.numberOfPlayer == 2:
        room = get_object_or_404(Room_for_2p, id=room_id)

        new_respond=second_player_respond(respond=respond)
        new_respond.save()

    elif game.numberOfPlayer == 3:
        room = get_object_or_404(Room_for_3p, id=room_id)
        if room.second_player==current_user:
            new_respond = second_player_respond(respond=respond)
        else:
            new_respond=third_player_respond(respond=respond)
        new_respond.save()
    elif game.numberOfPlayer == 4:
        room = get_object_or_404(Room_for_4p, id=room_id)
        if room.second_player == current_user:
            new_respond = second_player_respond(respond=respond)
        elif room.third_player ==current_user:
            new_respond = third_player_respond(respond=respond)
        else:
            new_respond = fourth_player_respond(respond=respond)

        new_respond.save()

        return JsonResponse({"success":"success"})



def check_for_second_player_respond(request):
    try:
        second_respond = second_player_respond.objects.first()

        if second_respond:
            respond = second_respond.respond
            second_respond.delete()
            return JsonResponse({'second_respond': True, 'respond': respond})
        else:
            return JsonResponse({'second_respond': False})
    except Exception as e:
        # Generic exception to catch any unexpected errors
        return JsonResponse({'error': str(e)}, status=500)

def check_for_third_player_respond(request):
    try:
        # Check if there is any instance of SecondPlayerRespond in the database
        third_respond = third_player_respond.objects.first()
        if third_respond:
            respond = third_respond.respond
            third_respond.delete()
            return JsonResponse({'third_respond': True, 'respond': respond})
        else:
            return JsonResponse({'third_respond': False})
    except Exception as e:
        # Generic exception to catch any unexpected errors
        return JsonResponse({'error': str(e)}, status=500)

def check_for_fourth_player_respond(request):
    try:
        # Check if there is any instance of SecondPlayerRespond in the database
        fourth_respond = fourth_player_respond.objects.first()
        if fourth_respond:
            respond = fourth_respond.respond
            fourth_respond.delete()

            return JsonResponse({'fourth_respond': True, 'respond': respond})
        else:
            return JsonResponse({'fourth_respond': False})
    except Exception as e:
        # Generic exception to catch any unexpected errors
        return JsonResponse({'error': str(e)}, status=500)



def check_for_gameRef(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        game_id = data.get("game_id")
        if room_id is None:
            return JsonResponse({'error': 'game_id not provided'}, status=400)

        game=get_object_or_404(InteractiveGame,id=game_id)

        if game.numberOfPlayer == 2:
            room = get_object_or_404(Room_for_2p, id=room_id)
        elif game.numberOfPlayer == 3:
            room = get_object_or_404(Room_for_3p, id=room_id)
        elif game.numberOfPlayer == 4:
            room = get_object_or_404(Room_for_4p, id=room_id)

        if room.gameRef:
            return JsonResponse({'isGameRef': room.gameRef.id})
        else:
            return JsonResponse({'isGameRef': False})


    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
def check_room_for_2p(request):
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        if game_id is None:
            return JsonResponse({'error': 'game_id not provided'}, status=400)

        game = get_object_or_404(InteractiveGame, id=game_id)
        number_of_rooms = Room_for_2p.objects.filter(game=game,isOpen=True).count()

        return JsonResponse({'number_of_rooms': number_of_rooms})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)



def check_all_players_start(request):
    try:
        data = json.loads(request.body)
        room_id = data.get('room_id')
        game_id=data.get('game_id')

        game=get_object_or_404(InteractiveGame,id=game_id)

        if game.numberOfPlayer == 2:
            room = get_object_or_404(Room_for_2p, id=room_id)
            if room.second_player is None:
                return JsonResponse({'isOk': False})
            else:
                room.isOpen=False
                room.save()
                return JsonResponse({'isOk': True})
        elif game.numberOfPlayer == 3:
            room = get_object_or_404(Room_for_3p, id=room_id)
            if room.second_player is not None and room.third_player is not None:
                room.isOpen = False
                room.save()
                return JsonResponse({'isOk': True})
            else:
                return JsonResponse({'isOk': False})
        elif game.numberOfPlayer == 4:
            room = get_object_or_404(Room_for_4p, id=room_id)
            if room.second_player is not None and room.third_player is not None and room.fourth_player is not None:
                room.isOpen = False
                room.save()
                return JsonResponse({'isOk': True})
            else:
                return JsonResponse({'isOk': False})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

def check_room_for_3p(request):
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        if game_id is None:
            return JsonResponse({'error': 'game_id not provided'}, status=400)

        game = get_object_or_404(InteractiveGame, id=game_id)
        number_of_rooms = Room_for_3p.objects.filter(game=game,isOpen=True).count()

        return JsonResponse({'number_of_rooms': number_of_rooms})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def check_room_for_4p(request):
    try:
        data = json.loads(request.body)
        game_id = data.get('game_id')
        if game_id is None:
            return JsonResponse({'error': 'game_id not provided'}, status=400)

        game = get_object_or_404(InteractiveGame, id=game_id)
        number_of_rooms = Room_for_4p.objects.filter(game=game,isOpen=True).count()

        return JsonResponse({'number_of_rooms': number_of_rooms})

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def key_verification(request,room_id,game_id):

    game = get_object_or_404(InteractiveGame,id=game_id)

    if game.numberOfPlayer == 2:
        room = get_object_or_404(Room_for_2p, id=room_id)
    elif game.numberOfPlayer == 3:
        room = get_object_or_404(Room_for_3p, id=room_id)
    elif game.numberOfPlayer == 4:
        room = get_object_or_404(Room_for_4p, id=room_id)

    return render(request,"group_game/key_verification.html",{"room":room})

