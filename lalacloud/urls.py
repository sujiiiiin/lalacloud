"""
URL configuration for lalacloud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from artists import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.artist_list, name="artist_list"),  # 首页显示歌手列表
    path('artist/<int:netease_id>/', views.artist_detail, name='artist_detail'), # 歌手详情页
    path('song/<int:song_id>/', views.song_detail, name='song_detail'),# 歌曲详情页
    path('songs/', views.song_list, name='song_list'),  #歌曲列表页
    path('random-artist/', views.random_artist, name='random_artist'), #随机推荐
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
