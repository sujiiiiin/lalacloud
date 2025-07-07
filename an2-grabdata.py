import json
import re
from snownlp import SnowNLP
from collections import defaultdict
from tqdm import tqdm
import sqlite3
import jieba

def load_song_data(db_path='db.sqlite3'):
    """从SQLite数据库加载歌曲数据"""
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询歌曲数据
        cursor.execute("""
            SELECT artist_id, title, lyrics 
            FROM artists_song
            WHERE lyrics IS NOT NULL AND lyrics != ''
        """)
        
        # 获取数据
        song_data = []
        for row in cursor.fetchall():
            artist, title, lyrics = row
            song_data.append({
                'artist': artist,
                'title': title,
                'lyrics': lyrics
            })
        
        print(f"成功加载 {len(song_data)} 首歌曲数据")
        return song_data
    except sqlite3.Error as e:
        print(f"数据库错误: {str(e)}")
        return []
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        return []
    finally:
        # 确保关闭数据库连接
        if conn:
            conn.close()

def clean_lyrics(lyrics):
    if not lyrics:
        return ""
    lyrics = re.sub(r'\[.*?\]', '', lyrics)
    lyrics = re.sub(r'[^\w\s\u4e00-\u9fff]', '', lyrics)
    lyrics = re.sub(r'\n\s*\n', '\n', lyrics)
    lyrics = re.sub(r'\s+', ' ', lyrics)
    
    return lyrics.strip()

def calculate_sentiment(lyrics):
    """改进的歌词情感分析"""
    if not lyrics:
        return None
    
    try:
        # 1. 预处理：识别并加权处理关键词
        positive_keywords = ['爱', '幸福', '快乐', '梦想', '阳光', '微笑', '美好', '希望']
        negative_keywords = ['伤', '痛', '泪', '死', '哭', '恨', '心碎', '孤独', '离开']
        
        # 2. 计算基础情感值
        s = SnowNLP(lyrics)
        base_score = s.sentiments
        
        # 3. 关键词加权调整
        words = jieba.lcut(lyrics)
        pos_count = sum(1 for word in words if word in positive_keywords)
        neg_count = sum(1 for word in words if word in negative_keywords)
        
        # 4. 调整公式
        adjustment = (pos_count - neg_count) * 0.05
        adjusted_score = base_score + adjustment
        
        # 5. 确保在0-1范围内
        return max(0, min(1, adjusted_score))
    except:
        return None

def analyze_songs(song_data):
    """分析歌曲情感值并分组"""
    # 按歌手分组存储结果
    artist_sentiments = defaultdict(dict)
    
    print("开始分析歌曲情感...")
    for song in tqdm(song_data, desc="处理歌曲"):
        # 获取歌曲信息
        artist = song.get('artist', '未知歌手')
        title = song.get('title', '未知歌曲')
        
        # 清理歌词
        lyrics = clean_lyrics(song.get('lyrics', ''))
        
        # 计算情感值
        sentiment = calculate_sentiment(lyrics)
        
        # 保存结果
        if sentiment is not None:
            artist_sentiments[artist][title] = sentiment
    
    return artist_sentiments

def save_results(artist_sentiments, output_file='song_sentiments.json'):
    """保存结果到JSON文件"""
    # 将defaultdict转换为普通dict
    result_dict = {artist: songs for artist, songs in artist_sentiments.items()}
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)
        print(f"结果已保存到 {output_file}")
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")

def main():
    # 1. 加载歌曲数据
    song_data = load_song_data()
    if not song_data:
        return
    
    # 2. 分析歌曲情感
    artist_sentiments = analyze_songs(song_data)
    
    # 3. 保存结果
    save_results(artist_sentiments)
    
    # 4. 显示统计信息
    print("\n分析统计:")
    print(f"处理歌手数量: {len(artist_sentiments)}")
    
    total_songs = sum(len(songs) for songs in artist_sentiments.values())
    print(f"成功分析歌曲数量: {total_songs}/{len(song_data)}")
    
    # 计算平均情感值
    total_sentiment = 0
    for songs in artist_sentiments.values():
        for sentiment in songs.values():
            total_sentiment += sentiment
    
    if total_songs > 0:
        avg_sentiment = total_sentiment / total_songs
        print(f"所有歌曲平均情感值: {avg_sentiment:.2f}")

if __name__ == "__main__":
    main()