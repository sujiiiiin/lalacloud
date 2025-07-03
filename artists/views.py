from django.shortcuts import render

# Create your views here.
from .models import Artist, Song
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time


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

    search_time = time.time() - start_time
    # 创建分页器
    paginator = Paginator(artists, 28)
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
    recommended_artists = Artist.objects.order_by('?')[:6]

    # 传递给模板的上下文数据
    context = {
        "artists": artists,
        "page_title": "热门歌手列表",
        "artist_count": paginator.count,
        "recommended_artists": recommended_artists,
        "all_artists": all_artists,
        "search_results_count": paginator.count,
        "search_time": round(search_time * 1000, 2) , # 转换为毫秒并保留2位小数
        "search_query": search_query,
    }

    return render(request, "artists/list.html", context)


# 歌手详情页
from django.shortcuts import render, get_object_or_404


def artist_detail(request, netease_id):
    # 获取歌手对象，如果不存在则返回404
    artist = get_object_or_404(Artist, netease_id=netease_id)

    # 获取该歌手的所有歌曲
    songs = artist.songs.all()
    context = {"artist": artist, "songs": songs, "page_title": f"{artist.name} - 详情"}
    return render(request, "artists/detail.html", context)


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
