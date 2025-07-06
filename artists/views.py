from django.shortcuts import render, get_object_or_404, redirect

# Create your views here.
from .models import Artist, Song
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time
from django.conf import settings
import os


# 歌手列表页
def artist_list(request):
    start_time = time.time()

    # 搜索功能，后端分页
    search_query = request.GET.get("q", "")
    if search_query:
        artists = Artist.objects.filter(name__icontains=search_query).order_by("id")
    else:
        artists = Artist.objects.all().order_by("id")

    all_artists = Artist.objects.all().order_by("id")
    # 分别传参本页歌手和全部歌手
    # 按id即热度排序

    search_time = time.time() - start_time  # 记录检索时间
    # 创建分页器
    paginator = Paginator(artists, 28)  # 28个歌手为一页
    page = request.GET.get("page")

    try:
        artists = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是整数，显示第一页
        artists = paginator.page(1)
    except EmptyPage:
        # 如果页数超出范围，显示最后一页
        artists = paginator.page(paginator.num_pages)

    # 获取推荐歌手（随机6位）
    recommended_artists = Artist.objects.order_by("?")[:6]
    # ? 是 Django ORM 支持的特殊语法，表示让数据库返回的结果顺序是随机的

    # 传递给模板的上下文数据
    context = {
        "artists": artists, # 分页歌手
        "page_title": "热门歌手列表",
        "artist_count": paginator.count,
        "recommended_artists": recommended_artists, # 猜你喜欢歌手
        "all_artists": all_artists, # 全部歌手
        "search_results_count": paginator.count,
        "search_time": round(search_time * 1000, 2),  # 转换为毫秒并保留2位小数
        "search_query": search_query,
    }

    return render(request, "artists/list.html", context)



# 歌手详情页

from artists.utils.lyrics_processor import LyricsProcessor
def artist_detail(request, netease_id):
    # 获取歌手对象，如果不存在则返回404
    artist = get_object_or_404(Artist, netease_id=netease_id)

    # 获取该歌手的所有歌曲
    songs = Song.objects.filter(artist=artist)
    
    # 获取所有歌词
    lyrics_list = [song.lyrics for song in songs if song.lyrics]
    print(len(lyrics_list))
    # 生成词云
    wordcloud_path = os.path.join(settings.BASE_DIR, 'wordclouds')
    if lyrics_list:
        processor = LyricsProcessor(artist.id,artist.name)
        word_freq = processor.process_lyrics(lyrics_list)
        
        # # 可选：使用特定形状的遮罩
        # mask_image = os.path.join(settings.BASE_DIR, 'static', 'images', 'music_mask.png')

        relative_path = processor.generate_wordcloud(word_freq,artist.id)
        
        if relative_path:
            # 构建完整的媒体 URL - 确保以斜杠开头
            wordcloud_path = f"{settings.MEDIA_URL.rstrip('/')}/{relative_path.lstrip('/')}"
    
    # 准备上下文
    top_words = []
    if word_freq:
        top_words = word_freq.most_common(10)
    
    context = {
        'artist': artist,
        'songs': songs,
        'wordcloud_path': wordcloud_path,
        'top_words': top_words,
        'word_count': sum(word_freq.values()) if word_freq else 0
    }

    return render(request, "artists/detail.html", context)

# 歌曲列表页
def song_list(request):
    start_time = time.time()

    # 搜索功能，后端分页
    search_query = request.GET.get("q", "")
    if search_query:
        song_list = Song.objects.filter(title__icontains=search_query).order_by('id')
    else:
        song_list = Song.objects.all().order_by('id')

    all_songs = Song.objects.all().order_by('id')

    search_time = time.time() - start_time  # 记录检索时间

    # 创建分页器
    paginator = Paginator(song_list, 20)  # 每页20首歌曲
    page = request.GET.get('page')

    try:
        songs = paginator.page(page)
    except PageNotAnInteger:
        # 如果page参数不是整数，显示第一页
        songs = paginator.page(1)
    except EmptyPage:
        # 如果页数超出范围，显示最后一页
        songs = paginator.page(paginator.num_pages)

    context = {
        'songs': songs,
        'page_title': '歌曲列表',
        'song_count': Song.objects.count(),
        "all_songs":all_songs,
        "search_results_count": paginator.count,
        "search_time": round(search_time * 1000, 2),  # 转换为毫秒并保留2位小数
        "search_query": search_query,

    }
    return render(request, 'songs/list.html', context)



# 歌曲详情页
def song_detail(request, song_id):
    # 获取歌曲对象，如果不存在则404
    song = get_object_or_404(Song, song_id=song_id)
    # 格式化歌词为行列表（用于前端换行显示）
    lyrics_lines = song.lyrics.split("\n") if song.lyrics else []
    context = {
        "song": song,
        "lyrics_lines": lyrics_lines,
        "page_title": f"{song.title} - 歌曲详情",
    }
    return render(request, "songs/detail.html", context)


# 歌曲评论
from .forms import CommentForm
from .models import Comment

def song_detail(request, song_id):
    song = get_object_or_404(Song, song_id=song_id)
    lyrics_lines = song.lyrics.split("\n") if song.lyrics else []

    # 处理评论提交
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            # 保存评论，但不提交到数据库
            new_comment = form.save(commit=False)
            # 设置评论对应的歌曲
            new_comment.song = song
            # 保存到数据库
            new_comment.save()
            # 重定向到当前页面，避免重复提交
            return redirect("song_detail", song_id=song.song_id)
    else:
        form = CommentForm()

    # 获取当前歌曲的所有已审核评论
    comments = song.comments.filter(approved=True)

    context = {
        "song": song,
        "lyrics_lines": lyrics_lines,
        "page_title": f"{song.title} - 歌曲详情",
        "form": form,
        "comments": comments,
    }

    return render(request, "songs/detail.html", context)


from django.http import JsonResponse
import random

def random_artist(request):
    # 获取所有歌手的ID列表
    artist_ids = Artist.objects.values_list('id', flat=True)
    
    if not artist_ids:
        return JsonResponse({
            'success': False,
            'message': '没有可用的歌手数据'
        })
    
    # 随机选择一个歌手ID
    random_id = random.choice(artist_ids)
    
    # 获取随机歌手对象
    artist = Artist.objects.get(id=random_id)
    
    # 构建返回数据
    data = {
        'success': True,
        'artist': {
            'netease_id': artist.netease_id,
            'name': artist.name,
            'avatar_url': artist.avatar_url,
            'description': artist.description,
        }
    }
    
    return JsonResponse(data)