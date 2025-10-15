import requests
import json
import os
import time

# ========== 配置区 ==========
UID = 322005137  # UP主 UID
PUSH_TOKEN = os.getenv("PUSHPLUS_TOKEN") or "a1dbf0a51e394c77af96b533ebab1d2a"
LAST_ID_FILE = "last_dynamic_id.txt"
CHECK_INTERVAL = 600  # 每隔多少秒检测一次（GitHub Actions建议 600 秒）

# ===========================


def get_latest_dynamic(uid):
    """获取UP主最新一条动态"""
    url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history?host_uid={uid}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        "Referer": f"https://space.bilibili.com/{uid}/",
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        text = resp.text.strip()
        if resp.status_code != 200 or not text:
            print(f"❌ 请求失败: {resp.status_code}, 内容: {text[:80]}")
            return None

        data = json.loads(text)
        cards = data.get("data", {}).get("cards", [])
        if not cards:
            print("⚠️ 没有获取到动态（cards 为空）")
            return None

        card = cards[0]
        desc = card.get("desc", {})
        dynamic_id = str(desc.get("dynamic_id_str") or desc.get("dynamic_id"))
        timestamp = desc.get("timestamp")
        uname = desc.get("user_profile", {}).get("info", {}).get("uname")

        try:
            content_json = json.loads(card["card"])
            item = content_json.get("item", {})
            text = item.get("description") or item.get("content") or "（无文字内容）"
            pictures = item.get("pictures", [])
            pic_urls = [p.get("img_src") for p in pictures]
        except Exception as e:
            print(f"⚠️ 解析动态内容失败: {e}")
            text, pic_urls = "(解析失败)", []

        return {
            "id": dynamic_id,
            "uid": uid,
            "uname": uname,
            "text": text,
            "time": timestamp,
            "pics": pic_urls,
        }

    except Exception as e:
        print(f"❌ 请求或解析出错: {e}")
        return None


def send_pushplus(content, title="Bilibili 动态提醒"):
    """通过 PushPlus 推送消息"""
    if not PUSH_TOKEN or PUSH_TOKEN == "你的PushPlusToken":
        print("⚠️ 未设置 PushPlus Token，跳过推送")
        return

    url = "http://www.pushplus.plus/send"
    data = {
        "token": PUSH_TOKEN,
        "title": title,
        "content": content,
        "template": "html",
    }

    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200:
            print("✅ 推送成功")
        else:
            print(f"❌ 推送失败: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"❌ 推送出错: {e}")


def read_last_dynamic_id():
    """读取上次记录的动态ID"""
    if not os.path.exists(LAST_ID_FILE):
        return None
    with open(LAST_ID_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_last_dynamic_id(dynamic_id):
    """保存最新动态ID"""
    with open(LAST_ID_FILE, "w", encoding="utf-8") as f:
        f.write(str(dynamic_id))


def main():
    print("🚀 正在检查 UP 主动态...")

    latest = get_latest_dynamic(UID)
    if not latest:
        print("⚠️ 未检测到新动态（可能接口延迟或被限流）")
        return

    last_id = read_last_dynamic_id()
    print(f"🧾 最新动态ID: {latest['id']}")
    print(f"📄 内容: {latest['text'][:50]}...")

    if last_id == latest["id"]:
        print("ℹ️ 没有新动态，跳过推送。")
        return

    # 格式化时间
    dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(latest["time"]))
    pics_html = "".join([f'<br><img src="{url}" width="250"/>' for url in latest["pics"]])
    text_html = latest["text"].replace("\n", "<br>")

    msg = (
        f"<b>UP主：</b>{latest['uname']}<br>"
        f"<b>时间：</b>{dt}<br>"
        f"<b>内容：</b><br>{text_html}<br>"
        f'<a href="https://t.bilibili.com/{latest["id"]}">🔗 点此查看原动态</a>'
        f"{pics_html}"
    )

    send_pushplus(msg, title=f"{latest['uname']} 有新动态！")
    save_last_dynamic_id(latest["id"])



if __name__ == "__main__":
    main()
