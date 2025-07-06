import os
import re
import jieba
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# 设置工作目录（根据您的实际路径修改）
WORK_DIR = r"D:\\vienna\\vienna\\THUCS\\first summer\\learning_python\\ts1_pycrawler\\lalacloud\\test"  # Windows 路径示例
# WORK_DIR = "/path/to/your/project"  # Linux/Mac 路径示例

# 初始化停用词
def load_stopwords():
    """加载停用词表"""
    stopwords_path = os.path.join(WORK_DIR, "data", "stopwords.txt")
    stopwords = set()
    
    if os.path.exists(stopwords_path):
        with open(stopwords_path, "r", encoding="utf-8") as f:
            for line in f:
                stopwords.add(line.strip())
    
    # 添加一些常见停用词
    common_stopwords = {"的", "了", "和", "是", "就", "都", "而", "及", "与", "这", "那", "在", "有", "要", "我", "你", "他", "她", "它", "我们", "你们", "他们", "啊", "哦", "呢", "吧", "呀"}
    stopwords.update(common_stopwords)
    
    return stopwords

# 歌词清洗函数
def clean_lyrics(text):
    """清洗歌词文本"""
    if not text:
        return ""
    
    # 移除括号内容（如[副歌]、[间奏]等）
    text = re.sub(r'\[.*?\]', '', text)
    # 移除非中文字符
    text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)
    # 移除多余空格
    return re.sub(r'\s+', ' ', text).strip()

# 处理歌词并生成词频统计
def process_lyrics(lyrics_list, stopwords):
    """处理歌词列表，返回词频统计"""
    all_text = ' '.join([clean_lyrics(lyric) for lyric in lyrics_list if lyric])
    
    if not all_text:
        return None
    
    # 使用jieba分词
    words = jieba.cut(all_text)
    
    # 过滤停用词和单字
    filtered_words = [
        word for word in words 
        if word and len(word) > 1 and word not in stopwords
    ]
    
    return Counter(filtered_words)

# 生成词云图片
def generate_wordcloud(word_freq, output_path, mask_image_path=None):
    """生成词云图片并保存到指定路径"""
    if not word_freq:
        print("没有有效的词频数据")
        return False
    
    # 设置字体（确保字体文件存在）
    font_path = os.path.join(WORK_DIR, "fonts", "SimHei.ttf")
    
    # 如果找不到字体，尝试使用系统默认字体（可能不支持中文）
    if not os.path.exists(font_path):
        print(f"警告: 字体文件不存在: {font_path}")
        font_path = None
    
    # 设置词云参数
    wc = WordCloud(
        font_path=font_path,
        background_color='white',
        max_words=200,
        width=1000,
        height=700,
        colormap='viridis',
        contour_width=1,
        contour_color='steelblue'
    )
    
    # 使用形状遮罩（可选）
    mask = None
    if mask_image_path and os.path.exists(mask_image_path):
        try:
            mask = np.array(Image.open(mask_image_path))
            wc.mask = mask
            print("使用遮罩图片生成词云")
        except Exception as e:
            print(f"加载遮罩图片失败: {e}")
    
    # 生成词云
    wc.generate_from_frequencies(word_freq)
    
    # 保存图片
    wc.to_file(output_path)
    print(f"词云已保存到: {output_path}")
    
    # 显示预览
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    
    return True

# 主函数
def main():
    # 1. 加载停用词
    stopwords = load_stopwords()
    print(f"已加载 {len(stopwords)} 个停用词")
    
    # 2. 准备测试歌词数据（替换为实际歌词）
    test_lyrics = [
        "你说你好累已无法再爱上谁",
        "风在山路吹",
        "过往的画面全都是我不对",
        "细数惭愧 我伤你几回",
        "我一路向北 离开有你的季节",
        "方向盘周围 回转着我的后悔",
        "我加速超越 却甩不掉紧紧跟随的伤悲",
        "停止狼狈 就让错纯粹"
    ]
    
    # 3. 处理歌词并生成词频
    word_freq = process_lyrics(test_lyrics, stopwords)
    
    if not word_freq:
        print("无法生成词频数据")
        return
    
    # 打印前20个高频词
    print("\n高频词汇:")
    for word, freq in word_freq.most_common(20):
        print(f"{word}: {freq}次")
    
    # 4. 生成词云
    output_path = os.path.join(WORK_DIR, "artist_wordcloud.png")
    mask_path = os.path.join(WORK_DIR, "masks", "music_note.png")  # 可选遮罩
    
    generate_wordcloud(word_freq, output_path, mask_path)

if __name__ == "__main__":
    main()