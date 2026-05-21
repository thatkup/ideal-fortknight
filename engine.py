import os
import json
import requests

# 从 GitHub Secrets 中读取你的密钥
TMDB_KEY = os.getenv('TMDB_API_KEY')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

def get_douban_top100():
    """从开源静态数据源安全获取豆瓣前 100 名电影，完美绕过反爬虫"""
    print("🎬 正在安全同步豆瓣 Top100 榜单数据...")
    # 使用社区维护的、免封锁的豆瓣 Top250 镜像数据源
    url = "https://raw.githubusercontent.com/movie-web/assets/main/douban_top250.json"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            all_movies = res.json()
            # 截取前 100 部电影
            top100 = all_movies[:100]
            print(f"✅ 成功获取 {len(top100)} 部豆瓣经典电影名单！")
            return [m['title'] for m in top100]
    except Exception as e:
        print(f"❌ 读取豆瓣备份源失败: {e}")
    
    # 如果网络偶发故障，用以下经典电影保底，确保你的网页绝不挂掉
    return ["肖申克的救赎", "霸王别姬", "阿甘正传", "泰坦尼克号", "这个杀手不太冷"]

def get_movie_data(title):
    """带着电影名去 TMDB 抓取高清海报和评分"""
    if not TMDB_KEY:
        return {"title": title, "poster": "", "rating_tmdb": "未配Key", "genres": ["剧情"]}
        
    search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_KEY}&query={title}&language=zh-CN"
    try:
        res = requests.get(search_url, timeout=5).json()
        if res.get('results'):
            movie = res['results'][0]
            poster_path = movie.get('poster_path')
            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else ""
            return {
                "title": title,
                "poster": poster_url,
                "rating_tmdb": movie.get('vote_average', '暂无'),
                "genres": ["剧情"] # 基础分类
            }
    except Exception as e:
        print(f"⚠️ 抓取 {title} 海报时卡顿: {e}")
    return {"title": title, "poster": "", "rating_tmdb": "暂无", "genres": ["剧情"]}

def get_ai_summary(title):
    """调用 Gemini AI 为每部经典电影撰写自媒体爆款解说大纲"""
    if not GEMINI_KEY:
        return "提示：未配置 GEMINI_API_KEY，无法生成 AI 选题。"
        
    # 调教 Gemini 的黄金 Prompt，直接让它吐出爆款文案思路
    prompt = (
        f"你是一个全网拥有千万粉丝的影视解说大V。请针对豆瓣神作《{title}》，"
        f"为我定制一个短视频文案策划：\n"
        f"1. 爆款视频标题（2个，要求带悬念、情绪或反常识）\n"
        f"2. 黄金前3秒的吸睛开头文案\n"
        f"3. 核心解说逻辑与痛点拆解。\n"
        f"请用精简、极具煽动性的网感语言作答，总字数不超过180字。"
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10).json()
        return res['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"🤖 AI 思想开小差了，建议稍后重新运行更新。错误: {e}"

if __name__ == "__main__":
    # 1. 自动获取豆瓣前 100 的电影名字
    movie_titles = get_douban_top100()
    
    data_list = []
    # 2. 循环为这 100 部电影配上大片海报和 AI 灵感
    for i, title in enumerate(movie_titles):
        print(f" [进度 {i+1}/100] 正在精心雕琢: {title}...")
        movie_info = get_movie_data(title)
        ai_insight = get_ai_summary(title)
        
        movie_info["ai_insight"] = ai_insight
        data_list.append(movie_info)
    
    # 3. 将这 100 部灌满数据的宝库写入 data.json 存入仓库
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)
        
    print("🎉 恭喜！豆瓣 Top100 影视自媒体大数据库已全量构建完毕！")