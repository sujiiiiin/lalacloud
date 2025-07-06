from django.contrib import admin

# Register your models here.
# 服务于/admin管理员登陆时的CRUD（增删查改）：create/read/update/delete
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


# 评论管理
from .models import Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("name", "song", "short_content", "created_at", "approved")
    list_filter = ("approved", "created_at")
    search_fields = ("name", "content", "song__title")
    actions = ["approve_comments", "disapprove_comments"]
    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    short_content.short_description = "评论内容"

    def approve_comments(self, request, queryset):
        queryset.update(approved=True)

    approve_comments.short_description = "审核通过所选评论"

    def disapprove_comments(self, request, queryset):
        queryset.update(approved=False)

    disapprove_comments.short_description = "取消审核所选评论"
