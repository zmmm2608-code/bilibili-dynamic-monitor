import requests
import time

UID = "322005137"  # 替换为你要监听的UP主UID
PUSH_TOKEN = "a1dbf0a51e394c77af96b533ebab1d2a"  # 替换为你的 PushPlus token
LAST_ID_FILE = "last_id.txt"

def push_wechat(title, content):
    url = f"https://www.pushplus.plus/send?token={PUSH_TOKEN}&title={title}&content={content}"
    requests.get(url)

def get_latest_dynamic():
    url = f"https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?host_mid={UID}"
    r = requests.get(url, timeout=10).json()
    card = r["data"]["items"][0]
    dynamic_id = card["id_str"]
    desc = card["modules"]["module_dynamic"]["desc"]["text"]
    author = card["modules"]["module_author"]["name"]
    return dynamic_id, author, desc

def main():
    try:
        last_id = ""
        try:
            with open(LAST_ID_FILE, "r") as f:
                last_id = f.read().strip()
        except:
            pass

        dynamic_id, author, desc = get_latest_dynamic()
        if dynamic_id != last_id:
            push_wechat(f"{author} 有新动态啦！", desc)
            with open(LAST_ID_FILE, "w") as f:
                f.write(dynamic_id)
    except Exception as e:
        print("运行出错：", e)

if __name__ == "__main__":
    main()
