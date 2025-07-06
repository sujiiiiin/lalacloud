from django.db import models

# Create your models here.


class Artist(models.Model):
    # 静态属性
    netease_id = models.IntegerField(unique=True, verbose_name="歌手ID")
    name = models.CharField(max_length=100, verbose_name="歌手名")
    avatar_url = models.URLField(max_length=500, verbose_name="歌手图片url")
    origin_url = models.URLField(
        max_length=500,
        verbose_name="歌手原始网站url",
        default="https://music.163.com/#/artist?id=",
    )
    description = models.TextField(blank=True, verbose_name="歌手简介")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "歌手"
        verbose_name_plural = "歌手列表"
        ordering = ["name"]  # 默认按名字排序

    def __str__(self):
        return self.name

    # 动态方法
    # 自动填充原始URL的方法
    def save(self, *args, **kwargs):
        if not self.origin_url.endswith(str(self.netease_id)):
            self.origin_url = f"https://music.163.com/#/artist?id={self.netease_id}"
        super().save(*args, **kwargs)


class Song(models.Model):
    song_id = models.IntegerField(unique=True, verbose_name="歌曲ID")
    artist = models.ForeignKey(
        Artist,
        on_delete=models.CASCADE,
        related_name="songs",   # 反向搜索：允许通过 artist.songs.all() 反向查询该歌手的所有歌曲
        verbose_name="歌手名",
    )

    title = models.CharField(max_length=200, verbose_name="歌曲名")
    album = models.CharField(max_length=200, verbose_name="专辑名称")
    image_url = models.URLField(max_length=500, verbose_name="歌曲图片url", default="")
    origin_url = models.URLField(
        max_length=500,
        verbose_name="原始链接",
        blank=True,
    )

    lyrics = models.TextField(blank=True, verbose_name="歌词", help_text="歌曲完整歌词")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲列表"
        ordering = ["-created_at"]  # 默认按创建时间倒序

    # 歌词摘要（用于后台显示）
    def lyrics_preview(self):
        return self.lyrics[:50] + "..." if self.lyrics else "无歌词"

    lyrics_preview.short_description = "歌词预览"

    def __str__(self):
        return f"{self.title} - {self.artist.name}"

    # 自动填充原始URL的方法
    def save(self, *args, **kwargs):
        if not self.origin_url.endswith(str(self.song_id)):
            self.origin_url = f"https://music.163.com/#/song?id={self.song_id}"
        super().save(*args, **kwargs)


class Comment(models.Model):
    song = models.ForeignKey(
        Song,
        on_delete=models.CASCADE,
        related_name='comments', # 反向搜索：允许通过song.conmments.all() 反向查询该歌曲的所有评论
        verbose_name="歌曲"
    )
    name = models.CharField(max_length=100, verbose_name="昵称")
    content = models.TextField(max_length=1000, verbose_name="评论内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    approved = models.BooleanField(default=True, verbose_name="审核通过")
    
    class Meta:
        verbose_name = "评论"
        verbose_name_plural = "评论列表"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} 对《{self.song.title}》的评论"