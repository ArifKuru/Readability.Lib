
from django.contrib import admin
from django.urls import path,include
from pages import views

app_name = 'pages'

urlpatterns = [
    path("",views.home,name="home"),
    path("main/",views.main_page,name="main"),
    path("generated/<int:story_id>", views.generated, name="generated"),
    # path(route,view,opt(shortcut-name))
    path('generate_story', views.generate_story, name='generate_story'),
    path('read', views.read, name='read'),
    path('make-visibility/<int:story_id>/', views.make_visibility, name='make-visibility'),
    path('transcribe/', views.transcribe, name='transcribe'),
    path("extract/",views.extract_page,name="extract"),
    path('read_pdf/<int:pdf_id>/', views.read_pdf, name='read_pdf'),
    path("read_pdf_onload/",views.read_pdf_onload,name="read_pdf_onload"),
    path("upload_pdf/",views.upload_pdf,name="upload_pdf"),
    path("edit/<int:story_id>",views.edit,name="edit"),
    path("save_extracted_page/",views.save_extracted_page,name="save_extracted_page"),
    path("generate_story_gemini",views.generate_story_gemini,name="generate_story_gemini"),
    path("interactive/",views.interactive,name="interactive"),
    path("interactive_Ai/", views.interactive_Ai, name="interactive_Ai"),
    path("summarize/",views.summarize_Gemini,name="summarize"),
    path("interactiveGame/<int:game_id>/<int:interactive_id>/",views.interactiveGame,name="interactiveGame"),
    path("interactiveMenu/<int:game_id>/", views.interactive_menu, name="interactiveMenu"),
    path("creating_room/<int:game_id>/", views.create_Room, name="creating_room"),
    path("upload/",views.upload,name="upload"),
    path('delete_game/<int:game_id>/', views.Delete_view, name='delete_game'),
    path("generate_story_gemini_from_image",views.generate_story_gemini_from_image,name="generate_story_gemini_from_image"),
    path("load_interactives/<int:game_id>",views.load_interactives,name="load_interactives"),
    path("video_call/",views.video_call,name="video_call"),
    path("group_game/<int:game_id>/<int:interactive_id>/<int:room_id>/",views.group_Game,name="group_game"),
    path("translate/",views.translate,name="translate"),
    path("rooms_list/<int:game_id>/",views.rooms_list,name="rooms_list"),
    path("key_verification/<int:game_id>/<int:room_id>/",views.key_verification,name="key_verification"),
    path("start_game/<int:game_id>/<int:room_id>/", views.start_Game, name="start_game"),
    path("check_room_for_4p/",views.check_room_for_4p,name="check_room_for_4p"),
    path("check_room_for_3p/", views.check_room_for_3p, name="check_room_for_3p"),
    path("check_room_for_2p/", views.check_room_for_2p, name="check_room_for_2p"),
    path("check_for_gameRef/",views.check_for_gameRef,name="check_for_gameRef"),
    path('check-second-player/', views.check_for_second_player_respond, name='check_for_second_player_respond'),
    path('check-third-player/', views.check_for_third_player_respond, name='check_for_second_player_respond'),
    path('check-fourth-player/', views.check_for_fourth_player_respond, name='check_for_second_player_respond'),
    path("create-player-respond/",views.create_player_respond,name="create_player_respond"),
    path("check_if_newContent/",views.check_if_newContent,name="check_if_newContent"),
    path("check_all_players_start/",views.check_all_players_start,name="check_all_players_start")
]
