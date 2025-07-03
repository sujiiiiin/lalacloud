from django.shortcuts import render

# Create your views here.
from .models import Artist, Song


# 歌手列表页
def artist_list(request):
    # 获取所有歌手并按名字排序
    artists = Artist.objects.all().order_by("name")

    # 传递给模板的上下文数据
    context = {
        "artists": artists,
        "page_title": "热门歌手列表",
        "artist_count": artists.count(),
    }

    return render(request, "artists/list.html", context)

# 歌手详情页
from django.shortcuts import render, get_object_or_404

def artist_detail(request, netease_id):
    # 获取歌手对象，如果不存在则返回404
    artist = get_object_or_404(Artist, netease_id=netease_id)
    
    # 获取该歌手的所有歌曲
    songs = artist.songs.all()
    
    context = {
        'artist': artist,
        'songs': songs,
        'page_title': f'{artist.name} - 详情'
    }
    
    return render(request, 'artists/detail.html', context)


# 歌曲详情页
def song_detail(request, song_id):
    """
    歌曲详情页面
    :param request: HTTP请求对象
    :param song_id: 歌曲ID (来自URL)
    :return: 渲染的歌曲详情页
    """
    # 获取歌曲对象，如果不存在则404
    song = get_object_or_404(Song, song_id=song_id)
    
    # 格式化歌词为行列表（用于前端换行显示）
    lyrics_lines = song.lyrics.split('\n') if song.lyrics else []
    
    context = {
        'song': song,
        'lyrics_lines': lyrics_lines,
        'page_title': f'{song.title} - 歌曲详情',
    }
    
    return render(request, 'songs/detail.html', context)