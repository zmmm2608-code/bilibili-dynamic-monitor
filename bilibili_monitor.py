import requests
import json
import os
from datetime import datetime

# ========== 配置 ==========
UID = "322005137"  # 替换成你想监听的UP主UID
# 优先从 GitHub Secrets 读取 PUSHPLUS_TOKEN，没有就使用本地写死的 token
PUSH_TOKEN = os.getenv("PUSHPLUS_TOKEN") or "a1dbf0a51e394c77af96b533ebab1d2a"
LAST_ID_FILE = "last_id.txt"
# ==========================

def pushplus_notify(title, content):
    url = "https://www.pushplus.plus/send"
    data = {
        "token": PUSH_TOKEN,
        "title": title,
        "content": content,
        "template": "html"
    }
    try:
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code == 200:
            print("✅ PushPlus 推送成功！")
        else:
            print(f"⚠️ PushPlus 推送失败：{resp.text}")
    except Exception as e:
        print(f"❌ 推送出错：{e}")

def get_latest_dynamic(uid):
    api_url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={uid}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(api_url, headers=headers, timeout=10)
        data = resp.json()
        cards = data.get("data", {}).get("items", [])
        if not cards:
            print("⚠️ 未获取到动态信息，可能UP主无动态或接口变化")
            return None

        latest = cards[0]
        dynamic_id = latest.get("id_str")
        modules = latest.get("modules", {})
        author = modules.get("module_author", {}).get("name", "未知UP主")
        dynamic_module = modules.get("module_dynamic", {})

        desc = ""
        if "desc" in dynamic_module:
            desc = dynamic_module["desc"].get("text", "")
        elif "major" in dynamic_module:
            major = dynamic_module["major"]
            if "archive" in major:
                desc = "📹 发布了视频：" + major["archive"]["title"]
            elif "draw" in major:
                desc = "🖼 发布了图文动态"
            elif "article" in major:
                desc = "📖 发布了专栏：" + major["article"]["title"]

        url = f"https://t.bilibili.com/{dynamic_id}"
        return {
            "id": dynamic_id,
            "author": author,
            "desc": desc,
            "url": url
        }

    except Exception as e:
        print(f"❌ 获取动态出错：{e}")
        return None

def main():
    print("🚀 开始检查UP主动态...\n")
    latest = get_latest_dynamic(UID)
    if not latest:
        print("⚠️ 未获取到最新动态，结束。")
        return

    print(f"🧾 当前动态ID：{latest['id']}")
    print(f"🧍 UP主：{latest['author']}")
    print(f"🗒 内容：{latest['desc']}")
    print(f"🔗 链接：{latest['url']}")

    if os.path.exists(LAST_ID_FILE):
        with open(LAST_ID_FILE, "r", encoding="utf-8") as f:
            last_id = f.read().strip()
    else:
        last_id = ""

    if latest["id"] != last_id:
        print("✨ 检测到新动态，准备推送！")
        content = f"<b>{latest['author']}</b> 有新动态啦！<br><br>{latest['desc']}<br><br><a href='{latest['url']}'>点此查看B站动态</a>"
        pushplus_notify(f"{latest['author']}的新动态", content)
        with open(LAST_ID_FILE, "w", encoding="utf-8") as f:
            f.write(latest["id"])
    else:
        print("🕒 暂无新动态。")

    print(f"\n✅ 检查完成于：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
