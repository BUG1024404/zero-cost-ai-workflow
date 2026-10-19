#!/usr/bin/env python3
"""微信 ClawBot/iLink 桥接程序（Muse 用）。

基于腾讯官方 tencent/openclaw-weixin 的 HTTP JSON 协议实现。
注意：本机 Python 直连会被目标服务器掐连接，统一走 curl 子进程。

子命令：
  login   获取二维码并等待扫码，成功后保存 state/session.json
  poll    拉取新消息（JSON 输出），更新游标
  send    给绑定用户发文本消息
  status  检查登录会话是否有效

凭据只存 state/（600 权限），.gitignore 已排除。
"""
import base64
import json
import os
import random
import subprocess
import sys
import time
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_DIR = os.path.join(BASE_DIR, "state")
SESSION_FILE = os.path.join(STATE_DIR, "session.json")
CURSOR_FILE = os.path.join(STATE_DIR, "cursor.txt")

API_BASE = "https://ilinkai.weixin.qq.com"
# 2.4.10 -> (2<<16)|(4<<8)|10
CLIENT_VERSION = str((2 << 16) | (4 << 8) | 10)
BOT_AGENT = "Muse/1.0"


def x_uin():
    return base64.b64encode(str(random.randint(1, 2**32 - 1)).encode()).decode()


def curl_json(method, url, headers, data=None, timeout=30):
    cmd = ["curl", "-sS", "--max-time", str(timeout), "-X", method, url]
    for k, v in headers.items():
        cmd += ["-H", f"{k}: {v}"]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 10)
    if p.returncode != 0:
        raise RuntimeError(f"curl failed: {p.stderr.strip()[:200]}")
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        raise RuntimeError(f"bad json: {p.stdout[:200]}")


def common_headers():
    return {
        "iLink-App-Id": "bot",
        "iLink-App-ClientVersion": CLIENT_VERSION,
    }


def auth_headers(token=None):
    h = {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "X-WECHAT-UIN": x_uin(),
        **common_headers(),
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def base_info():
    return {"channel_version": "2.4.10", "bot_agent": BOT_AGENT}


def load_session():
    if not os.path.exists(SESSION_FILE):
        return None
    with open(SESSION_FILE) as f:
        return json.load(f)


def save_session(sess):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = SESSION_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(sess, f)
    os.chmod(tmp, 0o600)
    os.replace(tmp, SESSION_FILE)


def cmd_login(args):
    """取二维码 -> 打印二维码图片URL -> 轮询等待扫码 -> 保存会话"""
    print("正在获取登录二维码...", flush=True)
    d = curl_json(
        "POST",
        f"{API_BASE}/ilink/bot/get_bot_qrcode?bot_type=3",
        auth_headers(),
        {"local_token_list": []},
    )
    qrcode = d.get("qrcode", "")
    img = d.get("qrcode_img_content", "")
    if not qrcode:
        print(f"取码失败: {json.dumps(d)[:300]}")
        return 1
    print(f"QRCODE_VALUE={qrcode}")
    print(f"QRCODE_IMG={img}")
    print("请用手机微信扫码（需先在微信 设置->插件 启用 ClawBot），二维码 2 分钟内有效。")
    print("等待扫码确认...", flush=True)

    deadline = time.time() + 110
    base = API_BASE
    while time.time() < deadline:
        try:
            st = curl_json(
                "GET",
                f"{base}/ilink/bot/get_qrcode_status?qrcode={qrcode}",
                common_headers(),
                timeout=15,
            )
        except Exception as e:
            # 协议：轮询失败视为 wait，继续等
            print(f"轮询超时，继续等待... ({str(e)[:60]})", flush=True)
            time.sleep(2)
            continue
        status = st.get("status", "")
        if status == "confirmed":
            sess = {
                "bot_token": st.get("bot_token", ""),
                "ilink_bot_id": st.get("ilink_bot_id", ""),
                "ilink_user_id": st.get("ilink_user_id", ""),
                "baseurl": st.get("baseurl") or API_BASE,
                "login_at": int(time.time()),
            }
            save_session(sess)
            print("登录成功，已保存会话。")
            # 通知后端客户端启动
            try:
                curl_json(
                    "POST",
                    f"{sess['baseurl']}/ilink/bot/msg/notifystart",
                    auth_headers(sess["bot_token"]),
                    {"base_info": base_info()},
                    timeout=15,
                )
            except Exception as e:
                print(f"notifyStart 警告（不影响使用）: {e}")
            return 0
        elif status == "expired":
            print("二维码已过期，请重新运行 login。")
            return 2
        elif status == "need_verifycode":
            print("需要在手机微信上输入验证码，请按微信页面提示完成验证后继续等待。")
        elif status == "verify_code_blocked":
            print("验证失败次数过多，请重新运行 login 获取新二维码。")
            return 3
        elif status == "scaned_but_redirect" and st.get("redirect_host"):
            base = "https://" + st["redirect_host"]
            print(f"切换到重定向地址继续等待: {base}")
        # wait / scaned: 继续轮询
        time.sleep(2)
    print("等待超时（110秒），请重新运行 login。")
    return 4


def cmd_poll(args):
    """拉取新消息，JSON 输出到 stdout；游标持久化。"""
    sess = load_session()
    if not sess:
        print(json.dumps({"error": "not_logged_in"}))
        return 1
    cursor = ""
    if os.path.exists(CURSOR_FILE):
        with open(CURSOR_FILE) as f:
            cursor = f.read().strip()
    try:
        d = curl_json(
            "POST",
            f"{sess['baseurl']}/ilink/bot/getupdates",
            auth_headers(sess["bot_token"]),
            {"get_updates_buf": cursor, "base_info": base_info()},
            timeout=45,
        )
    except Exception as e:
        print(json.dumps({"error": str(e)[:200]}))
        return 1
    if d.get("ret") not in (0, None):
        print(json.dumps({"error": f"ret={d.get('ret')} {d.get('errmsg','')}"[:200]}))
        return 1
    new_cursor = d.get("get_updates_buf") or cursor
    if new_cursor != cursor:
        with open(CURSOR_FILE, "w") as f:
            f.write(new_cursor)

    msgs = []
    for m in d.get("msgs", []):
        texts = []
        for item in m.get("item_list", []):
            t = (item.get("text_item") or {}).get("text")
            if t:
                texts.append(t)
            vt = (item.get("voice_item") or {}).get("text")
            if vt:
                texts.append(f"[语音转写]{vt}")
        msgs.append(
            {
                "message_id": m.get("message_id"),
                "from_user_id": m.get("from_user_id"),
                "group_id": m.get("group_id") or "",
                "message_type": m.get("message_type"),
                "create_time_ms": m.get("create_time_ms"),
                "context_token": m.get("context_token") or "",
                "text": "\n".join(texts),
            }
        )
    print(json.dumps({"messages": msgs, "bound_user": sess.get("ilink_user_id")}, ensure_ascii=False))
    return 0


def cmd_send(args):
    """给绑定用户发文本消息。"""
    sess = load_session()
    if not sess:
        print("未登录，先运行 login。")
        return 1
    text = args.text
    if not text:
        print("用法: bridge.py send --text '内容' [--context-token TOKEN]")
        return 1
    msg = {
        "from_user_id": "",
        "to_user_id": sess["ilink_user_id"],
        "client_id": uuid.uuid4().hex,
        "message_type": 2,
        "message_state": 2,
        "item_list": [{"type": 1, "text_item": {"text": text}}],
    }
    if args.context_token:
        msg["context_token"] = args.context_token
    d = curl_json(
        "POST",
        f"{sess['baseurl']}/ilink/bot/sendmessage",
        auth_headers(sess["bot_token"]),
        {"msg": msg, "base_info": base_info()},
        timeout=20,
    )
    if d.get("ret", 0) == 0:
        print("发送成功。")
        return 0
    print(f"发送失败: {json.dumps(d)[:300]}")
    return 1


def cmd_status(args):
    sess = load_session()
    if not sess:
        print("未登录。")
        return 1
    print(f"已登录: bot_id={sess.get('ilink_bot_id','')[:12]}... user_id={sess.get('ilink_user_id','')[:12]}...")
    # 用 getconfig 驗證 token 有效性
    try:
        d = curl_json(
            "POST",
            f"{sess['baseurl']}/ilink/bot/getconfig",
            auth_headers(sess["bot_token"]),
            {"ilink_user_id": sess["ilink_user_id"], "base_info": base_info()},
            timeout=15,
        )
        print(f"token 有效: ret={d.get('ret')}")
        return 0
    except Exception as e:
        print(f"token 校验失败: {e}")
        return 2


def main():
    import argparse

    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("login")
    sub.add_parser("poll")
    sp = sub.add_parser("send")
    sp.add_argument("--text", default="")
    sp.add_argument("--context-token", default="")
    sub.add_parser("status")
    args = ap.parse_args()
    os.makedirs(STATE_DIR, exist_ok=True)
    if args.cmd == "login":
        return cmd_login(args)
    if args.cmd == "poll":
        return cmd_poll(args)
    if args.cmd == "send":
        return cmd_send(args)
    if args.cmd == "status":
        return cmd_status(args)


if __name__ == "__main__":
    sys.exit(main())
