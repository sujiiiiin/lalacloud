import jieba
import re
from collections import Counter
from wordcloud import WordCloud
import imageio
import os
from django.conf import settings

class LyricsProcessor:
    def __init__(self, artist_id):
        self.artist_id = artist_id
        self.stopwords = self.load_stopwords()
        
    def load_stopwords(self):
        """加载停用词表"""
        stopwords_path = os.path.join(settings.BASE_DIR, 'data', 'stopwords.txt')
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            return set([line.strip() for line in f])
    
    def clean_text(self, text):
        """清洗歌词文本"""
        # 移除括号内容（如[副歌]、[间奏]等）
        text = re.sub(r'\[.*?\]', '', text)
        # 移除非中文字符
        text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def process_lyrics(self, lyrics_list):
        """处理歌词列表，返回词频统计"""
        all_text = ' '.join([self.clean_text(lyric) for lyric in lyrics_list])
        words = jieba.cut(all_text) # 调用jieba库进行分词
        
        # 过滤停用词和单字
        filtered_words = [
            word for word in words 
            if word not in self.stopwords and len(word) > 1
        ]
        
        return Counter(filtered_words)
    
    def generate_wordcloud(self, word_freq, mask_image=None):
        """生成词云图片"""
        # 设置词云参数
        wc = WordCloud(
            font_path=os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SimHei.ttf'),
            background_color='white',
            max_words=200,
            width=800,
            height=600,
            colormap='viridis'
        )
        
        # # 使用形状遮罩（可选）
        # if mask_image:
        #     mask = imageio.imread(mask_image)
        #     wc.mask = mask
        
        # 生成词云
        wc.generate_from_frequencies(word_freq)
        
        # 保存到媒体目录
        output_dir = os.path.join(settings.MEDIA_ROOT, 'wordclouds')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'artist_{self.artist_id}.png')
        wc.to_file(output_path)
        
        return os.path.join('media', 'wordclouds', f'artist_{self.artist_id}.png')