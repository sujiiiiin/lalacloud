from django.contrib import admin

# Register your models here.
# artists/admin.py
from django.contrib import admin
from .models import Artist, Song


class SongInline(admin.TabularInline):
    """在歌手页面直接编辑歌曲的内联方式"""
    model = Song
    extra = 0  # 不显示额外空表单
    fields = ["title", "album"]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """歌手管理界面"""

    list_display = ["name", "netease_id", "created_at"]
    search_fields = ["name", "netease_id"]
    inlines = [SongInline]  # 添加歌曲内联


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    """歌曲管理界面"""

    list_display = ["title", "artist", "album"]
    list_filter = ["artist"]
    search_fields = ["title", "album"]

