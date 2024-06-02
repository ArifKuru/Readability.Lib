
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from pages import views
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("",include("pages.urls")),
    path("settings/", include("settings.urls")),
    path("profile/",include("userProfile.urls")),
    path("form/",include("form.urls")),
    path("chat/",include("chat.urls"))
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





admin.site.site_title = "Readability Admin"


admin.site.site_header =" Readability Admin Portal"

admin.site.index_title = "Welcome to Readability Admin Portal"


