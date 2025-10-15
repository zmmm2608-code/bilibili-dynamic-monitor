import requests
import json
import os

# 配置
UID = 322005137
PUSH_TOKEN = "a1dbf0a51e394c77af96b533ebab1d2a"  # ← 换成你的真实 PushPlus token
DATA_FILE = "latest_dynamic.json"

# PushPlus 推送函数
def send_push(title, content):
    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSH_TOKEN,
        "title": title,
        "content": content,
        "template": "html"
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            print("✅ PushPlus 推送成功")
        else:
            print("⚠️ PushPlus 推送失败:", resp.text)
    except Exception as e:
        print("❌ PushPlus 异常:", e)

# 获取 UP 最新动态
def get_latest_dynamic(uid):
    url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0 Safari/537.36",
        "Referer": f"https://space.bilibili.com/{uid}/",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code != 200 or not resp.text.strip():
        raise Exception(f"请求失败，状态码: {resp.status_code}, 内容: {resp.text[:100]}")
    data = resp.json()
    card = data["data"]["cards"][0]
    desc = card["desc"]
    dynamic_id = desc["dynamic_id_str"]
    timestamp = desc["timestamp"]
    uname = desc["user_profile"]["info"]["uname"]
    content_json = json.loads(card["card"])
    text = content_json["item"].get("description", "")
    pictures = content_json["item"].get("pictures", [])
    pic_urls = [p["img_src"] for p in pictures]
    return {
        "id": dynamic_id,
        "uid": uid,
        "uname": uname,
        "text": text,
        "time": timestamp,
        "pics": pic_urls
    }


# 主逻辑
def main():
    print("🚀 正在检查 UP 主动态...")
    latest = get_latest_dynamic(UID)
    print(f"🧾 最新动态ID: {latest['id']}")
    print(f"🧍 用户: {latest['uname']}")
    print(f"📝 内容: {latest['text']}")

    # 读取本地上次记录
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            last = json.load(f)
    else:
        last = {}

    # 对比是否有新动态
    if last.get("id") != latest["id"]:
        print("✨ 检测到新动态，准备推送...")
        link = f"https://t.bilibili.com/{latest['id']}"
        pic_html = "".join([f'<img src="{url}" width="300"><br>' for url in latest['pics']])
        content = f"<b>{latest['uname']}</b> 发布新动态：<br>{latest['text']}<br><a href='{link}'>查看动态</a><br>{pic_html}"
        send_push("Bilibili 动态更新提醒", content)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(latest, f, ensure_ascii=False, indent=2)
    else:
        print("⏳ 暂无新动态。")

if __name__ == "__main__":
    main()
