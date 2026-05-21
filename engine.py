import os
import json
import requests

# 1. 这里的 Key 会从你之前在 GitHub Settings 存的 Secret 里读取，非常安全
TMDB_KEY = os.getenv('TMDB_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_movie_data(title):
    # 逻辑：去 TMDB 搜索电影名，换取海报和评分[cite: 1]
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={title}&language=zh-CN"
    res = requests.get(search_url).json()
    if res['results']:
        movie = res['results'][0]
        return {
            "poster": f"https://image.tmdb.org/t/p/w500{movie['poster_path']}",
            "rating_tmdb": movie['vote_average'],
            "genres": ["剧情"], # 简化处理，实际可从 API 获取更多标签[cite: 1]
            "id": movie['id']
        }
    return None

def get_ai_summary(title):
    # 逻辑：调用 Gemini AI 为每部电影写一句话创作建议[cite: 1]
    # 注意：这里需要安装 google-generativeai 库，我们会在下一步的配置中完成
    prompt = f"你是一个影视自媒体专家，请为电影《{title}》写一段30字内的爆款视频选题建议。"
    # 模拟 AI 返回（实际运行时会调用接口）
    return f"AI 建议：本片适合做'人性反转'专题，建议对比国内外同类题材。"

# 主运行逻辑
movies_to_track = ["肖申克的救赎", "霸王别姬", "阿甘正传"]
final_data = []

for m in movies_to_track:
    info = get_movie_data(m)
    if info:
        info['title'] = m
        info['ai_insight'] = get_ai_summary(m)
        final_data.append(info)

# 将结果写入 data.json
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, indent=4)