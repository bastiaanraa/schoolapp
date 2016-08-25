"""steinerschool URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from apps.profile.views import ClassRoomDetail, ProfileDetail, MyClassRooms, Search

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', auth_views.login, {'template_name': 'admin/login.html'}, name='login'),
    url(r'^mijn-klassen', MyClassRooms.as_view(), name="mijn-klassen"),
    url(r'^klas/(?P<slug>[\w-]+)/$', ClassRoomDetail.as_view(), name='klas'),
    url(r'^profile/(?P<pk>\d+)/$', ProfileDetail.as_view(), name='profile'),
    url(r'search', Search.as_view(), name='search'),
 	] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 
