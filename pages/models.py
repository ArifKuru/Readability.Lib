from django.db import models
from django.shortcuts import get_object_or_404
from django_countries.fields import CountryField
from django.contrib.auth.models import User
from django.utils import timezone
class InteractiveGame(models.Model):
    id=models.BigAutoField(primary_key=True)
    name=models.TextField(null=True,blank=True)
    descriptionOfGame=models.TextField(null=True,blank=True)
    instructions = models.TextField(null=True,blank=True)
    music = models.TextField(null=True,blank=True)
    image=models.ImageField(null=True,blank=True,upload_to="games/")
    numberOfPlayer=models.IntegerField(null=True)


    def __str__(self):
        return str(self.id)

    def get_Interactives(self,current_user):
        return list(Interactive.objects.filter(gameOf=self,user=current_user))

    # def get_InteractiveById(self,interactive_id):
    #     return get_object_or_404(Interactive, id=interactive_id)



class Interactive(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    name= models.TextField(null=True,blank=True)
    gameOf=models.ForeignKey(InteractiveGame,null=True,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id)


    def get_stories(self):
        return list(Interactive_Story.objects.filter(partOf=self.id))

    def get_contents(self):
        return list(InteractiveContent.objects.filter(partOf=self.id))

    def get_last_content(self):
        return InteractiveContent.objects.filter(partOf=self.id).latest('id')

    def delete_all_stories(self):
        stories = Interactive_Story.objects.filter(partOf=self.id)
        stories.delete()

class Interactive_Story(models.Model):
    id = models.BigAutoField(primary_key=True)
    parts = models.TextField(null=True)
    roles= models.TextField(null=True)
    partOf=models.ForeignKey(Interactive,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id)

class InteractiveContent(models.Model):
    id=models.BigAutoField(primary_key=True)
    content=models.TextField()
    partOf=models.ForeignKey(Interactive,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="games/playing/",null=True)
    def __str__(self):
        return str(self.id)

class Pdf(models.Model):
    id = models.BigAutoField(primary_key=True)
    content=models.TextField(null=True)
    user=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    date=models.DateField(auto_now=True)
    image=models.ImageField(upload_to="pdfs/images/")
    def __str__(self):
        return str(self.id)

class Page(models.Model):
    partOf=models.ForeignKey(Pdf,null=True,on_delete=models.CASCADE)
    content=models.TextField(null=True)
    id = models.BigAutoField(primary_key=True)

    def __str__(self):
        return str(self.id)


class LanguageSetting(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    language_choices = [
        ("en-US", "English"),
        ("es-ES", "Spanish"),
        ("de-DE", "German"),
        ("fr-FR", "French"),
        ("tr-TR", "Turkish"),
        ("ar-XA", "Arabic"),
        ("it-IT", "Italian"),
        ("ru-RU", "Russian")
    ]
    PostLanguage = models.CharField(choices=language_choices, max_length=50, default="en-US")
    TranslateLanguage = models.CharField(choices=language_choices, max_length=50, default="en-US")
    ReadingLanguage = models.CharField(choices=language_choices, max_length=50, default="en-US")
    TranscribeLanguage=models.CharField(choices=language_choices, max_length=50, default="en-US")
    GenerativeLanguage=models.CharField(choices=language_choices, max_length=50, default="en-US")
    Reader_gender_choices = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]
    Reader_gender=models.CharField(choices=Reader_gender_choices, max_length=50, default="Male")


    # PostLanguage = models.
class Rating(models.Model):
    id = models.BigAutoField(primary_key=True)
    user=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    isLiked = models.BooleanField(null=True,blank=True)
    date=models.DateField(auto_now=True,null=True,blank=True)
    story=models.ForeignKey("Story",on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        if self.isLiked:
            self.date = timezone.now().date()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

# Create your models here.
class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    user=models.ForeignKey(User,null=True,on_delete=models.CASCADE)
    content=models.TextField(null=True)
    date=models.DateField(auto_now=True)
    story = models.ForeignKey("Story",on_delete=models.CASCADE)
    def __str__(self):
        return str(self.id)

# class Notification(models.Model):


class Profile(models.Model):
    gender_choices = [
        ("Male", "Male"),
        ("Female", "Female"),
    ]
    gender = models.CharField(choices=gender_choices, null=True, max_length=50, blank=True)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    bio = models.TextField(null=True, default="Write here about you ,for other authors!")
    UserId = models.BigAutoField(primary_key=True)
    country = CountryField()
    # LANGUAGE SETTINGS
    # VOICE SETTINGS
    image = models.ImageField(upload_to="profiles/", default="profiles/default_profile.png",null=True,blank=True)
    isEmailVerified=models.BooleanField(default=False)
    def __str__(self):
        return str(self.user)


class Story(models.Model):
    author = models.ForeignKey(User,null=True, on_delete=models.CASCADE)
    category = models.TextField(null=True)
    wordSize = models.IntegerField(null=True)
    content = models.TextField(null=True)
    prompt = models.TextField(blank=True, null=True)
    createDate = models.DateField(auto_now=True)
    isPublic = models.BooleanField(default=False)
    PublishDate = models.DateField(auto_now=False,null=True,blank=True)
    # Diğer alanlar buraya eklenebilir
    storyId = models.BigAutoField(primary_key=True)
    def save(self, *args, **kwargs):
        if self.isPublic:
            self.PublishDate = timezone.now().date()
        super().save(*args, **kwargs)

    def upload_path(instance, filename):
        # Yükleme yolu oluştur
        story_id = instance.storyId
        extension = filename.split('.')[-1]
        new_filename = f"{story_id}.{extension}"
        return f"stories/{new_filename}"

    image = models.ImageField(upload_to=upload_path, default="stories/book.png")

    def get_comment_count(self):
        return self.comment_set.count()

    def get_thumb_up(self):
        return self.rating_set.filter(isLiked=True).count()

    def get_thumb_down(self):
        return self.rating_set.filter(isLiked=False).count()
    def __str__(self):
        return str(self.storyId)

    class Meta:
        verbose_name ="Story"
        verbose_name_plural="Stories"

class Room_for_2p(models.Model):
    game = models.ForeignKey(InteractiveGame, on_delete=models.CASCADE, related_name='rooms_2p')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_created_2p')
    id = models.BigAutoField(primary_key=True)
    key = models.TextField(null=True)
    second_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_joined_2p', blank=True, null=True)
    gameRef=models.ForeignKey(Interactive,on_delete=models.CASCADE,related_name="rooms_reference_2p", blank=True, null=True)
    isOpen=models.BooleanField(null=True,default=True)

    def __str__(self):
        return str(self.game.id) + " To " + self.creator.username + str(self.id)

class Room_for_3p(models.Model):
    game = models.ForeignKey(InteractiveGame, on_delete=models.CASCADE, related_name='rooms_3p')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_created_3p')
    id = models.BigAutoField(primary_key=True)
    key = models.TextField(null=True)
    second_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_joined_3p', blank=True, null=True)
    third_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_joined_3p_3rd', blank=True, null=True)
    gameRef=models.ForeignKey(Interactive,on_delete=models.CASCADE,related_name="rooms_reference_4p", blank=True, null=True)
    isOpen=models.BooleanField(null=True,default=True)


    def __str__(self):
        return str(self.game.id) + " To " + self.creator.username + str(self.id)

class Room_for_4p(models.Model):
    game = models.ForeignKey(InteractiveGame, on_delete=models.CASCADE, related_name='rooms_4p')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_created_4p')
    id = models.BigAutoField(primary_key=True)
    key = models.TextField(null=True)
    second_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_joined_4p', blank=True, null=True)
    third_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_joined_4p_3rd', blank=True, null=True)
    fourth_player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rooms_joined_4p_4th', blank=True, null=True)
    gameRef=models.ForeignKey(Interactive,on_delete=models.CASCADE,related_name="rooms_reference_3p", blank=True, null=True)
    isOpen=models.BooleanField(null=True,default=True)

    def __str__(self):
        return str(self.game.id) + " To " + self.creator.username + str(self.id)


class second_player_respond(models.Model):
    respond = models.TextField(null=True)

class third_player_respond(models.Model):
    respond = models.TextField(null=True)

class fourth_player_respond(models.Model):
    respond = models.TextField(null=True)



