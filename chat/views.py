import json
from datetime import datetime

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from accounts.decorators import email_verification_required
from chat.models import Chat, Messages
from django.db.models import F,Q
from cryptography.fernet import Fernet

from django.utils.dateparse import parse_datetime

def check_new_messages(request):
    data = json.loads(request.body)
    id_of_last_message = data.get('id_of_last_message', '')
    print(id_of_last_message)
    last_message=get_object_or_404(Messages,id=id_of_last_message)
    print(last_message.id)
    current_chat=last_message.partOf
    latest_message = Messages.objects.filter(partOf=current_chat).order_by('-id').first()
    if not id_of_last_message ==latest_message.id:
        isThereNewMessage = True
    else:
        isThereNewMessage=False
    return JsonResponse({"isThereNewMessage":isThereNewMessage})
@email_verification_required
def chat_panel(request,username):
    if username =="general":
        redirectedTo=False
    else:
        print(username)
        redirectedTo = User.objects.get(username=username)
    users=User.objects.all()
    chats = Chat.objects.filter(Q(user=request.user) | Q(secondUser=request.user))
    context={
        "chats":chats,
        "users":users,
        "redirectedTo":redirectedTo
    }
    return render(request,"chat/chat_panel.html", context)
@email_verification_required
def message_panel(request, username):
    sender = request.user
    if username == "PLACEHOLDER":
        receiver = False
        messages = False
    else:
        receiver = User.objects.get(username=username)
        chat = create_or_get_chat(sender, receiver)
        messages = Messages.objects.filter(partOf=chat).order_by(F('date').desc())

        for message in messages:
            print("Message Content (encrypted):", message.content)
            print("Type of message.content:", type(message.content))

            try:
                fernet = Fernet(message.key)
                decrypted_content = fernet.decrypt(message.content).decode()
                message.content=decrypted_content
            except Exception as e:
                print("Decryption Error:", e)

    context = {
        "receiver": receiver,
        "sender": sender,
        "messages": messages,
    }
    return render(request, "chat/message_panel.html", context)

def create_or_get_chat(sender, receiver):

    chat = Chat.objects.filter(user=sender, secondUser=receiver).first()

    if not chat:
        chat = Chat.objects.filter(user=receiver, secondUser=sender).first()

    if not chat:
        chat = Chat.objects.create(user=sender, secondUser=receiver)

    return chat

def sendMessage(request):
    data = json.loads(request.body)
    sender_username = data.get('sender', '')
    print((sender_username))
    receiver_username = data.get("receiver", '')
    print((receiver_username))

    sender = User.objects.get(username=sender_username)

    receiver_username = data.get("receiver", '')
    receiver = User.objects.get(username=receiver_username)

    content = data.get("content", '')

    key = Fernet.generate_key()
    fernet = Fernet(key)
    enc_content = fernet.encrypt(content.encode())  # Encrypting the content and encoding it to bytes
    chat = create_or_get_chat(sender, receiver)

    message = Messages.objects.create(
        key=key,
        sender=sender,
        receiver=receiver,
        content=enc_content,
        partOf=chat
    )

    print("Message Content (encrypted):", message.content)

    try:
        fernet_new = Fernet(message.key)
        decrypted_content = fernet_new.decrypt(message.content).decode()  # Decrypting the content and decoding it to string
        print("Decrypted Content:", decrypted_content)
    except Exception as e:
        print("Decryption Error:", e)

    return JsonResponse({'success': "success"})



