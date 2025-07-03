import requests
from bs4 import BeautifulSoup
import time
import re
import os
import django
import os

# 初始化Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lalacloud.settings")
django.setup()

from artists.models import Artist, Song

# 配置请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://music.163.com/",
    "Origin": "https://music.163.com",
}


# 获取热门歌手列表
def get_artists():
    url = "https://music.163.com/api/artist/top"
    params = {
        "offset": 0,
        "total": True,
        "limit": 100,  # 获取100位歌手
    }

    try:
        response = requests.get(url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        artists = []
        for artist in data["artists"][:100]:
            netease_id = artist["id"]  # 歌手唯一ID
            name = artist["name"]
            origin_url = f"https://music.163.com/artist?id={netease_id}"  # 歌手原始链接

            # 获取歌手图片URL
            try:
                avatar_url = artist["img1v1Url"]
            except KeyError:
                print(f"歌手 {name} 没有图片")
                avatar_url = ""

            if avatar_url:
                # 标准化URL
                if avatar_url.startswith("http://"):
                    avatar_url = avatar_url.replace("http://", "https://")
                elif avatar_url.startswith("//"):
                    avatar_url = "https:" + avatar_url
                elif not avatar_url.startswith("http"):
                    avatar_url = "https://" + avatar_url.lstrip(":/")

            artists.append(
                {
                    "name": name,
                    "netease_id": netease_id,
                    "origin_url": origin_url,
                    "avatar_url": avatar_url,
                }
            )

        print(f"成功获取{len(artists)}位歌手信息")
        return artists

    except Exception as e:
        print("获取歌手列表失败:", e)
        return []


# 获取歌手简介
def get_artist_intro(artist):
    url = f"https://music.163.com/artist/desc?id={artist['netease_id']}"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        desc_div = soup.find("div", class_="n-artdesc")

        if desc_div:
            paragraphs = desc_div.find_all("p")
            description = "\n\n".join(
                p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)
            )
            description = description.strip()
            if len(description) > 1000:
                description = description[:1000] + "..."
            return description
        else:
            print(f"未找到 {artist['name']} 的简介")
            return "暂无简介"

    except Exception as e:
        print(f"获取 {artist['name']} 详情失败: {str(e)}")
        return "暂无简介"


# 获取歌曲歌词
def get_song_lyrics(song_id):
    url = f"https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        # 提取歌词文本
        if data["code"] == 200:
            # 获取歌词文本（优先使用翻译后的歌词）
            lyric_text = ""
            if "lrc" in data and "lyric" in data["lrc"]:
                lyric_text = data["lrc"]["lyric"]

            # 移除时间轴和空行
            if lyric_text:
                # 移除时间轴 [00:00.00]
                lyric_text = re.sub(r"\[\d{2}:\d{2}\.\d{2,3}\]", "", lyric_text)
                # 移除多余的空行
                lyric_text = re.sub(r"\n\s*\n", "\n", lyric_text).strip()

            return lyric_text

    except Exception as e:
        print(f"获取歌词失败: {str(e)}")
        return ""


def get_song_cover(song_id):
    # 获取歌曲详情的API
    url = f'https://music.163.com/api/v3/song/detail?c=[{{"id":{song_id}}}]'

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == 200 and data.get("songs"):
            album_info = data["songs"][0].get("al", {})
            image_url = album_info.get("picUrl", "")

            if image_url.startswith("//"):
                return "https:" + image_url
            return image_url

        return ""

    except Exception as e:
        print(f"获取封面失败: {str(e)}")
        return ""


# 获取歌手热门歌曲
def get_artist_top_songs(artist_id, artist_name, limit=20):
    api_url = f"https://music.163.com/api/artist/top/song?id={artist_id}"
    params = {
        "offset": 0,
        "total": True,
        "limit": 20,  # 获取20首歌曲
    }

    try:
        response = requests.get(api_url, headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        if data["code"] != 200:
            print(
                f"获取 {artist_name} 的热门歌曲失败: {data.get('message', '未知错误')}"
            )
            return []

        songs = []
        for song in data["songs"]:
            song_id = song["id"]  # 歌曲唯一ID
            title = song["name"]
            origin_url = f"https://music.163.com/song?id={song_id}"  # 歌曲原始链接
            album = song["al"]["name"] if "al" in song else "未知专辑"
            songs.append(
                {
                    "title": title,
                    "origin_url": origin_url,
                    "song_id": song_id,
                    "album": album,
                }
            )

        print(f"成功获取 {artist_name} 的 {len(songs)} 首热门歌曲")
        return songs

    except Exception as e:
        print(f"获取 {artist_name} 热门歌曲失败: {str(e)}")
        return []


# 获取歌手详情和歌曲数据
def get_artists_detail(artists):
    for i, artist in enumerate(artists):
        print(f"\n处理中 ({i+1}/{len(artists)}): {artist['name']}")

        # 获取歌手简介
        artist["description"] = get_artist_intro(artist)

        # 获取热门歌曲
        songs = get_artist_top_songs(artist["netease_id"], artist["name"])
        artist["songs"] = songs

        # 为每首歌曲获取歌词
        for song in artist["songs"]:
            song["lyrics"] = get_song_lyrics(song["song_id"])
            song["image_url"] = get_song_cover(song["song_id"])
            time.sleep(0.3)

        time.sleep(1.2)

        # 每处理10位歌手保存一次进度
        if (i + 1) % 10 == 0:
            print(f"已处理 {i+1} 位歌手，正在保存进度...")
            save_to_database(artists[: i + 1])


# 保存数据到数据库
def save_to_database(artists_data):
    saved_count = 0
    for artist_data in artists_data:
        try:
            # 创建或更新歌手
            artist, created = Artist.objects.update_or_create(
                netease_id=artist_data["netease_id"],  # 统一字段名
                defaults={
                    "name": artist_data["name"],
                    "avatar_url": artist_data.get("avatar_url", ""),
                    "description": artist_data.get("description", ""),
                    "origin_url": artist_data["origin_url"],
                },
            )
            artist.songs.all().delete()

            for song_data in artist_data.get("songs", []):
                Song.objects.create(
                    artist=artist,
                    title=song_data["title"],
                    album=song_data.get("album", ""),
                    song_id=song_data.get("song_id", None),
                    origin_url=song_data.get("origin_url", ""),
                    lyrics=song_data.get("lyrics", ""),
                    image_url=song_data.get("image_url", ""),
                )

            saved_count += 1
            print(f"已保存歌手: {artist_data['name']}")

        except Exception as e:
            print(f"保存歌手 {artist_data['name']} 失败: {str(e)}")

    return saved_count


# 主函数
def main():
    print("=" * 50)
    print("开始爬取网易云音乐热门歌手数据")
    print("=" * 50)

    # 获取歌手列表
    artists = get_artists()

    if not artists:
        print("未获取到歌手信息，程序退出")
        return

    # 获取歌手详情和歌曲数据
    get_artists_detail(artists)

    # 最终保存所有数据
    saved_count = save_to_database(artists)
    print("=" * 50)
    print(f"数据爬取完成！共保存 {saved_count} 位歌手数据到数据库")
    print("=" * 50)


if __name__ == "__main__":
    main()
