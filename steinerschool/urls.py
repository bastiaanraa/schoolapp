from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from profile.views import ProfileDetail, Search, LogoutView
from classrooms.views import ClassRooms, ClassRoomDetail, MyClassRoom
from werkgroepen.views import WerkgroepDetail

urlpatterns = [
    #url(r"^$", MyClassRoom.as_view(), name="mijn-klassen"),
    url(r'^$', ClassRooms.as_view(), name='klassen'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/', LogoutView.as_view(), name='logout'),
    url(r'^schoolgids', MyClassRoom.as_view(), name="schoolgids"),
    url(r'^klas/(?P<slug>[\w-]+)/$', ClassRoomDetail.as_view(), name='klas'),
    url(r'^klassen', ClassRooms.as_view(), name='klassen'),
    url(r'^profile/(?P<pk>\d+)/$', ProfileDetail.as_view(), name='profile'),
    url(r'search', Search.as_view(), name='search'),
    url(r'werkgroep/(?P<slug>[\w-]+)/$', WerkgroepDetail.as_view(), name='werkgroep'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

admin.site.site_title = "SCHOOL INTERN"
admin.site.site_header = "SCHOOL INTERN"