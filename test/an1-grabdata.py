import sqlite3
import re
from collections import Counter
import json

# 连接SQLite数据库
conn = sqlite3.connect("db.sqlite3")  # 替换为你的数据库路径
cursor = conn.cursor()

# 1. 从数据库中读取歌手简介
cursor.execute("SELECT id, name, description FROM artists_artist")  # 替换为你的表名
singers = cursor.fetchall()


# 2. 出生地提取函数
def extract_birthplace(description):
    """从简介中提取出生地信息"""
    if not description:
        return None

    # 常见出生地关键词模式
    patterns = [
        r"出生于(.*?)[,，。]",
        r"出生在(.*?)[,，。]",
        r"生于(.*?)[,，。]",
        r"來自(.*?)[,，。]",
        r"来自(.*?)[,，。]",
        r"籍贯(.*?)[,，。]",
        r"出生地：(.*?)[\n]",
    ]

    for pattern in patterns:
        match = re.search(pattern, description)
        if match:
            location = match.group(1).strip()
            # 清理数据
            location = re.sub(r"[《》<>()（）\"\']", "", location)
            return location

    return None


# 3. 地域标准化映射
def standardize_location(location):
    """将提取的地域信息标准化"""
    if not location:
        return "未知"

    # 省级行政区映射
    province_mapping = {
        r"北京(市)?|京": "北京",
        r"上海(市)?|沪": "上海",
        r"天津(市)?|津": "天津",
        r"重庆(市)?|渝": "重庆",
        r"河北(省)?|冀": "河北",
        r"山西(省)?|晋": "山西",
        r"辽宁(省)?|辽": "辽宁",
        r"吉林(省)?|吉": "吉林",
        r"黑龙江(省)?|黑": "黑龙江",
        r"江苏(省)?|苏": "江苏",
        r"浙江(省)?|浙": "浙江",
        r"安徽(省)?|皖": "安徽",
        r"福建(省)?|闽": "福建",
        r"江西(省)?|赣": "江西",
        r"山东(省)?|鲁": "山东",
        r"河南(省)?|豫": "河南",
        r"湖北(省)?|鄂": "湖北",
        r"湖南(省)?|湘": "湖南",
        r"广东(省)?|粤": "广东",
        r"海南(省)?|琼": "海南",
        r"四川(省)?|川": "四川",
        r"贵州(省)?|贵|黔": "贵州",
        r"云南(省)?|云|滇": "云南",
        r"陕西(省)?|陕|秦": "陕西",
        r"甘肃(省)?|甘|陇": "甘肃",
        r"青海(省)?|青": "青海",
        r"台湾(省)?|台": "台湾",
        r"内蒙古(自治区)?|蒙": "内蒙古",
        r"广西(壮族自治区)?|桂": "广西",
        r"西藏(自治区)?|藏": "西藏",
        r"宁夏(回族自治区)?|宁": "宁夏",
        r"新疆(维吾尔自治区)?|新": "新疆",
        r"香港|港": "香港",
        r"澳门|澳": "澳门",
    }

    # 城市级映射
    city_mapping = {
        r"哈尔滨": "黑龙江",
        r"长春": "吉林",
        r"沈阳": "辽宁",
        r"大连": "辽宁",
        r"济南": "山东",
        r"青岛": "山东",
        r"南京": "江苏",
        r"苏州": "江苏",
        r"杭州": "浙江",
        r"宁波": "浙江",
        r"厦门": "福建",
        r"福州": "福建",
        r"广州": "广东",
        r"深圳": "广东",
        r"东莞": "广东",
        r"成都": "四川",
        r"武汉": "湖北",
        r"西安": "陕西",
        r"郑州": "河南",
    }

    # 先尝试匹配省级行政区
    for pattern, province in province_mapping.items():
        if re.search(pattern, location):
            return province

    # 再尝试匹配城市级
    for pattern, province in city_mapping.items():
        if re.search(pattern, location):
            return province

    # 特殊处理
    if "中国" in location or "大陆" in location:
        return "其他(中国)"
    if "台湾" in location:
        return "台湾"

    return location  # 无法识别的返回原始值


# 4. 处理所有歌手数据
birthplace_counter = Counter()
processed_data = []

for singer in singers:
    singer_id, name, desc = singer
    raw_location = extract_birthplace(desc)
    std_location = standardize_location(raw_location) if raw_location else "未知"

    # 存储处理结果
    processed_data.append(
        {
            "id": singer_id,
            "name": name,
            "raw_location": raw_location,
            "std_location": std_location,
        }
    )

# 5. 保存结果
# 保存原始数据
with open("singer_birthplaces.json", "w", encoding="utf-8") as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=2)

# 关闭数据库连接
conn.close()
