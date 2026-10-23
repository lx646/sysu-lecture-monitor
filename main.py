# main.py
import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime

# 从GitHub Secrets中安全地读取Token
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN")
# 监控的网址
URL = "https://ce.sysu.edu.cn/"
# 本地记录文件，防止重复推送
HISTORY_FILE = "history.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def send_pushplus(title, content, url):
    """发送微信推送"""
    if not PUSHPLUS_TOKEN:
        print("错误：未找到PUSHPLUS_TOKEN，请检查Secrets配置。")
        return
    push_url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSHPLUS_TOKEN,
        "title": title,
        "content": f"<b>{title}</b><br/><br/>链接：<a href='{url}'>{url}</a>",
        "template": "html"
    }
    try:
        res = requests.post(push_url, json=data, timeout=10)
        if res.status_code == 200 and res.json().get("code") == 200:
            print(f"✅ 推送成功: {title}")
        else:
            print(f"❌ 推送失败: {res.text}")
    except Exception as e:
        print(f"推送出错: {e}")

def check_updates():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查更新...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=15)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        for a_tag in soup.find_all('a'):
            href = a_tag.get('href')
            text = a_tag.get_text(strip=True)
            if href and ("讲座" in text or "报告" in text) and len(text) > 5:
                if href.startswith('/'):
                    href = "https://ce.sysu.edu.cn" + href
                news_items.append({"title": text, "url": href})

        history = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = f.read().splitlines()

        new_count = 0
        for item in news_items:
            item_id = f"{item['title']}||{item['url']}"
            if item_id not in history:
                print(f"🔔 发现新讲座: {item['title']}")
                send_pushplus("【中大化院】新学术讲座", item['title'], item['url'])
                history.append(item_id)
                new_count += 1

        if new_count > 0:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                f.write("\n".join(history))
            print(f"更新完成，新增 {new_count} 条记录。")
        else:
            print("未发现新讲座。")
    except Exception as e:
        print(f"抓取网页出错: {e}")

if __name__ == "__main__":
    check_updates()
