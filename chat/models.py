from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='chats_as_user')
    secondUser = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='chats_as_second_user')
    id = models.BigAutoField(primary_key=True)
    date = models.DateField(auto_now=True)


    def __str__(self):
        return str(self.id)


class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='messages_sender')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='messages_receiver')
    date = models.DateField(auto_now=True)
    content = models.BinaryField(null=True)
    partOf = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, related_name='messages')
    key=models.BinaryField(null=True)
    id = models.BigAutoField(primary_key=True)
    def __str__(self):
        return str(self.sender.username + " To " + self.receiver.username)
