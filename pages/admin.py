from django.contrib import admin
from .models import Story, Profile, Comment, Rating, LanguageSetting, Interactive, Interactive_Story, \
    InteractiveGame, InteractiveContent, Page, Pdf, Room_for_4p, Room_for_2p, Room_for_3p, fourth_player_respond, \
    third_player_respond, second_player_respond


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("storyId","author","isPublic")
    list_filter = ("isPublic",)
    search_fields = ("author",)


admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(LanguageSetting)
admin.site.register(Pdf)
admin.site.register(Page)
admin.site.register(Room_for_2p)
admin.site.register(Room_for_3p)

admin.site.register(second_player_respond)
admin.site.register(third_player_respond)
admin.site.register(fourth_player_respond)


admin.site.register(Room_for_4p)

admin.site.register(Interactive)
admin.site.register(Interactive_Story)
admin.site.register(InteractiveGame),
admin.site.register(InteractiveContent)





