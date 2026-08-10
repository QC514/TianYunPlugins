# [pin: true]
# [title: 分发接收助手]
# [icon: https://gcore.jsdelivr.net/gh/lhz03/img@647fefb92bd14443b57c923e4706a9979c9af3a5/2026/04/03/f1fcd076ace5effb9db55f747d2d432d.png]
# [language: python]
# [rule: ^分发接收$]
# [disable:false]
# [cron:]
# [open_source: false]
# [platform: qq,qb,wx,gw,sb,wb,tg,tb,qx,xy,ip]
# [class: 工具类]
# [priority: 999999999]
# [public: true]
# [admin: false]
# [version: 1.0.5]
# [author: yuhualhh]
# [price: 0]
# [service: ]
# [description: <br>❶这是关于云市场助手的插件分发功能的专用分发接收助手<br>❷使用本插件需授予一定权限，前往"系统管理-插件权限"全部启用 <img src="https://gcore.jsdelivr.net/gh/lhz03/img@6e746210d9a953e3356ab27ac2635376763197ed/2026/04/09/51cf7635f89406dd8ffc8a15eef551c9.png">]

import middleware
import requests
import json
import time
import re
import os
import hashlib
import uuid

RECEIVE_SERVER_URL = "http://yuhualhh.250666.xyz/api/plugin_receive.php"
RECEIVE_API_SECRET = "YuhuaReceiveApi888"
DIST_SECRET = "YuhuaDist888888"

def _make_request(method, url, **kwargs):
    for _ in range(3):
        try:
            if method.lower() == 'get':
                response = requests.get(url, **kwargs)
            else:
                response = requests.post(url, **kwargs)
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            time.sleep(1)
    return None

def _get_autman_cookie(sender):
    cookie = sender.bucketGet("yuhua_sqzs_receive", "autMan")
    if cookie:
        return cookie
    for _ in range(3):
        try:
            username = sender.bucketGet("autMan", "adminUsername")
            password = sender.bucketGet("autMan", "adminPassword")
            port = middleware.port()
            if not all([username, password, port]):
                return None
            login_url = f"http://127.0.0.1:{port}/login"
            data = {"username": username, "password": password}
            headers = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
            response = _make_request("post", login_url, data=data, headers=headers, timeout=5)
            if response and response.status_code == 200 and response.json().get("code") == 200:
                cookie_value = response.headers.get("Set-Cookie").split(';')[0]
                middleware.bucketSet("yuhua_sqzs_receive", "autMan", cookie_value)
                return cookie_value
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None

def _autman_api_request(sender, method, endpoint, **kwargs):
    for _ in range(3):
        cookie = _get_autman_cookie(sender)
        if not cookie:
            return None
        port = middleware.port()
        url = f"http://127.0.0.1:{port}{endpoint}"
        headers = kwargs.get("headers", {})
        headers["Cookie"] = cookie
        kwargs["headers"] = headers
        response = _make_request(method, url, **kwargs)
        if not response:
            return None
        try:
            data = response.json()
            if response.status_code == 200 and data.get("code") == 200:
                return response
            if response.status_code == 401 or data.get("code") == 401:
                try:
                    middleware.bucketDel("yuhua_sqzs_receive", "autMan")
                except Exception:
                    pass
                continue
            return response
        except Exception:
            if response.status_code == 401:
                try:
                    middleware.bucketDel("yuhua_sqzs_receive", "autMan")
                except Exception:
                    pass
                continue
            return response
    return None

def _distribution_keystream(length):
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(hashlib.sha256(f"{DIST_SECRET}:{counter}".encode("utf-8")).digest())
        counter += 1
    return bytes(output[:length])

def _decrypt_distribution_cloud_user(enc_cloud_user):
    try:
        raw = bytes.fromhex(str(enc_cloud_user).strip())
        ks = _distribution_keystream(len(raw))
        plain = bytes([a ^ b for a, b in zip(raw, ks)])
        return plain.decode("utf-8")
    except Exception:
        return None

def _parse_distribution_voucher(voucher):
    voucher = str(voucher).strip()
    match = re.match(r'^([0-9a-fA-F]+)-(plugins|plugins_script)-(.+)$', voucher)
    if not match:
        return None

    enc_cloud_user = match.group(1).lower()
    target_bucket = match.group(2)
    target_name = match.group(3).strip()

    if ":" not in target_name:
        return None
    if target_bucket == "plugins_script" and "." not in target_name:
        return None

    cloud_user_id = _decrypt_distribution_cloud_user(enc_cloud_user)
    if not cloud_user_id:
        return None

    return {
        "voucher": voucher,
        "enc_cloud_user": enc_cloud_user,
        "target_bucket": target_bucket,
        "target_name": target_name,
        "cloud_user_id": cloud_user_id
    }

def _derive_bucket_key(target_bucket, target_name):
    author, file_name = target_name.split(":", 1)
    if target_bucket == "plugins":
        return f"{author}:{os.path.splitext(file_name)[0]}"
    return f"{author}:{file_name}"

def _extract_distribution_token(distribution_link):
    distribution_link = str(distribution_link).strip()
    match = re.search(r'(?:\?|&)token=([a-zA-Z0-9_]+)', distribution_link)
    if match:
        return match.group(1)
    if re.match(r'^[a-zA-Z0-9_]+$', distribution_link):
        return distribution_link
    return None

class PluginReceiveRemoteHandler:
    def get_meta(self):
        try:
            response = requests.get(
                f"{self.url}?action=get_meta&token={self.token}",
                timeout=10
            )
            if response and response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    return {
                        "voucher": data.get("voucher", ""),
                        "target_bucket": data.get("target_bucket", ""),
                        "target_name": data.get("target_name", ""),
                        "status": data.get("status", ""),
                        "expires_in": data.get("expires_in", 0)
                    }
                if data.get("code") == -1:
                    return "expired"
        except Exception:
            pass
        return None
    def __init__(self, url, token=None):
        self.url = url.rstrip('/')
        self.token = token or f"r_{uuid.uuid4().hex[:16]}"
    def init_session(self, voucher_data):
        payload = {
            "voucher": voucher_data["voucher"],
            "enc_cloud_user": voucher_data["enc_cloud_user"],
            "target_bucket": voucher_data["target_bucket"],
            "target_name": voucher_data["target_name"]
        }
        for _ in range(3):
            try:
                response = requests.post(
                    f"{self.url}?action=init_session&token={self.token}",
                    json=payload,
                    headers={
                        "X-API-Key": RECEIVE_API_SECRET,
                        "Content-Type": "application/json"
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        return True
            except Exception:
                time.sleep(1)
        return False

    def get_user_url(self):
        return f"{self.url}?token={self.token}"

    def poll_result(self):
        try:
            response = requests.get(
                f"{self.url}?action=poll_result&token={self.token}",
                headers={"X-API-Key": RECEIVE_API_SECRET},
                timeout=10
            )
            if response and response.status_code == 200:
                data = response.json()
                if data.get("code") == 0 and data.get("plugin_text"):
                    return True, {
                        "plugin_text": data.get("plugin_text"),
                        "uploaded_name": data.get("uploaded_name", "")
                    }
                if data.get("code") == -1:
                    return False, "expired"
                if data.get("code") == 1 and data.get("status") in ("success", "fail"):
                    return False, data.get("status")
        except Exception:
            pass
        return None, None

    def report_result(self, success, msg=""):
        try:
            requests.post(
                f"{self.url}?action=report_result&token={self.token}",
                json={"success": success, "msg": msg},
                headers={
                    "X-API-Key": RECEIVE_API_SECRET,
                    "Content-Type": "application/json"
                },
                timeout=10
            )
        except Exception:
            pass

def _restart_autman(sender):
    endpoints = [
        "/restart",
        "/reboot",
        "/system/restart",
        "/admin/restart"
    ]
    for endpoint in endpoints:
        try:
            response = _autman_api_request(sender, "post", endpoint, timeout=5)
            if response and response.status_code == 200:
                return True
        except Exception:
            pass
    return False

def handle_plugin_distribution_receive(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return

    try:
        chat_id = sender.getChatID()
        if str(chat_id) not in ("0", "", "None"):
            sender.reply("""=====分发接收=====
❌ 当前功能仅允许私聊使用
💡 请切换至私聊环境后重试
==================""")
            return
    except Exception:
        pass

    local_cloud_user_id = sender.bucketGet("cloud", "username") or ""
    if not local_cloud_user_id:
        sender.reply("""=====分发接收=====
❌ 插件未能获取到本地的云账号
💡 请检查是否已授予本插件权限
==================""")
        return

    sender.reply("""=====分发接收=====
请输入分发凭证
------------------
请在60秒内完成
输入"q"退出""")
    voucher_input = sender.input(60000, 0, False)
    if not voucher_input:
        sender.reply("❌ 输入超时")
        return
    if str(voucher_input).strip().lower() == 'q':
        sender.reply("✅ 已退出操作")
        return

    clean_voucher = re.sub(r'^分发凭证[:：\s]*', '', str(voucher_input).strip()).strip()
    voucher_data = _parse_distribution_voucher(clean_voucher)
    if not voucher_data:
        sender.reply("""=====分发接收=====
❌ 分发凭证格式错误
💡 请检查后重新输入
==================""")
        return

    if str(voucher_data["cloud_user_id"]) != str(local_cloud_user_id):
        sender.reply(f"""=====分发接收=====
🗯️ 本地账号: {local_cloud_user_id or '未知'}
🎫 目标账号: {voucher_data["cloud_user_id"]}
✨ 操作结果: 当前分发凭证不属于本机
==================""")
        return

    sender.reply("""=====分发接收=====
请输入分发链接
------------------
请在60秒内完成
输入"q"退出""")
    distribution_link_input = sender.input(60000, 0, False)
    if not distribution_link_input:
        sender.reply("❌ 输入超时")
        return
    if str(distribution_link_input).strip().lower() == 'q':
        sender.reply("✅ 已退出操作")
        return

    clean_link = re.sub(r'^分发链接[:：\s]*', '', str(distribution_link_input).strip()).strip()
    distribution_token = _extract_distribution_token(clean_link)
    if not distribution_token:
        sender.reply("""=====分发接收=====
❌ 分发链接格式错误
💡 请检查后重新输入
==================""")
        return

    remote = PluginReceiveRemoteHandler(RECEIVE_SERVER_URL, distribution_token)

    meta = remote.get_meta()
    if meta == "expired":
        sender.reply("""=====分发接收=====
❌ 分发链接已超时销毁
💡 请重新发送指令获取
==================""")
        return
    if not meta:
        sender.reply("""=====分发接收=====
❌ 获取分发链接信息失败
💡 请稍后再试或重发指令
==================""")
        return

    if (
        str(meta.get("voucher", "")) != str(voucher_data["voucher"]) or
        str(meta.get("target_bucket", "")) != str(voucher_data["target_bucket"]) or
        str(meta.get("target_name", "")) != str(voucher_data["target_name"])
    ):
        sender.reply("""=====分发接收=====
❌ 分发凭证与分发链接不匹配
💡 请仔细检查无误后重新输入
==================""")
        return

    if meta.get("status") == "success":
        sender.reply("""=====分发接收=====
❌ 该分发链接已被处理完成
💡 请重新发送指令获取链接
==================""")
        return

    if meta.get("status") == "fail":
        sender.reply("""=====分发接收=====
❌ 该分发链接处理失败
💡 请重新发送指令获取
==================""")
        return

    if meta.get("status") not in ("uploaded", "waiting"):
        sender.reply("""=====分发接收=====
❌ 当前分发链接状态异常
💡 请你重新发送指令获取
==================""")
        return

    status = None
    result = None
    start_ts = time.time()

    while time.time() - start_ts < 60:
        status, result = remote.poll_result()
        if status is True and result:
            break
        if status is False:
            if result == "expired":
                sender.reply("""=====分发接收=====
❌ 分发链接已超时销毁
💡 请重新发送指令获取
==================""")
                return
            if result == "success":
                sender.reply("""=====分发接收=====
❌ 该分发链接已被处理完成
💡 请重新发送指令获取链接
==================""")
                return
            if result == "fail":
                sender.reply("""=====分发接收=====
❌ 该分发链接处理失败
💡 请重新发送指令获取
==================""")
                return
        time.sleep(1)

    if not (status is True and result):
        sender.reply("""=====分发接收=====
❌ 获取分发数据已超时
💡 请重新发送指令获取
==================""")
        return

    target_bucket = voucher_data["target_bucket"]
    target_key = _derive_bucket_key(target_bucket, voucher_data["target_name"])
    payload = result.get("plugin_text", "")

    if not payload:
        remote.report_result(False, "分发数据内容为空")
        sender.reply("""=====分发接收=====
❌ 分发数据内容为空
💡 请你重新获取数据
==================""")
        return

    try:
        middleware.bucketSet(target_bucket, target_key, payload)
    except Exception as e:
        remote.report_result(False, f"写入数据桶失败: {str(e)[:80]}")
        sender.reply(f"""=====分发接收=====
❌ 写入数据桶失败
------------------
⚠️ 错误: {str(e)[:80]}
==================""")
        return

    remote.report_result(True, f"写入成功: {target_bucket}/{target_key}")
    sender.reply(f"""=====分发接收=====
🗯️ 本地账号: {local_cloud_user_id}
📦 目标桶名: {target_bucket}
🔑 目标键名: {target_key}
✨ 操作结果: 插件已成功写入数据桶
==================""")

    sender.reply("""=====分发接收=====
❶即将自动重启奥特曼
❷你可以选择暂停重启
------------------
请在10秒内输入
输入"q"暂停""")
    restart_input = sender.input(10000, 0, False)
    if restart_input and str(restart_input).strip().lower() in ("q", "取消"):
        sender.reply("""=====分发接收=====
✨ 已取消重启操作
💡 请自行重启生效
==================""")
        return

    if _restart_autman(sender):
        sender.reply("""=====分发接收=====
✨ 已发起重启指令
💡 请等待系统恢复
==================""")
    else:
        sender.reply("""=====分发接收=====
⚠️ 自动重启未成功
💡 请手动重启生效
==================""")
    return

def _perform_maintenance_check() -> bool:
    from bs4 import BeautifulSoup

    url = "https://yuhualhh.250666.xyz/shouquan"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache"
    }
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=(5, 10),
                verify=True,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='note-content')
            if content_div:
                return "服务正常中" in content_div.get_text(strip=True)
            return any("服务正常中" in tag.get_text() for tag in soup.find_all(['div', 'p']))
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < 2:
                time.sleep(2)
                continue
            return False
        except requests.exceptions.HTTPError:
            return False
        except Exception:
            return False
    return False

def check_maintenance_page() -> bool:
    import base64
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    cache_bucket = "time"
    cache_key = "status_cache"
    ttl_seconds = 1 * 3600
    try:
        salt = b'\x8a\x9b\x1f\xe3\x7d\x4c\x5b\x6a\x01\x23\x45\x67\x89\xab\xcd\xef'
        identifier = "yuhua888"
        key = hashlib.sha256(salt + identifier.encode('utf-8')).digest()
        aesgcm = AESGCM(key)
        cached_data_str = middleware.bucketGet(cache_bucket, cache_key)
        if cached_data_str:
            decoded_data = base64.b64decode(cached_data_str.encode('utf-8'))
            nonce = decoded_data[:12]
            ciphertext = decoded_data[12:]
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            cached_data = json.loads(decrypted_bytes.decode('utf-8'))
            if (time.time() - cached_data.get("timestamp", 0)) < ttl_seconds and cached_data.get("status") is True:
                return True
    except Exception:
        pass
    live_status = _perform_maintenance_check()
    new_cache_payload = {
        "status": live_status,
        "timestamp": time.time()
    }
    try:
        salt = b'\x8a\x9b\x1f\xe3\x7d\x4c\x5b\x6a\x01\x23\x45\x67\x89\xab\xcd\xef'
        identifier = "yuhua888"
        key = hashlib.sha256(salt + identifier.encode('utf-8')).digest()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        plaintext = json.dumps(new_cache_payload).encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        encrypted_payload = base64.b64encode(nonce + ciphertext).decode('utf-8')
        middleware.bucketSet(cache_bucket, cache_key, encrypted_payload)
    except Exception:
        pass
    return live_status
        


def main():
    sender_id = middleware.getSenderID()
    sender = middleware.Sender(sender_id)
    msg = sender.getMessage().strip()

    if not check_maintenance_page():
        sender.reply("❌ 服务端无法连通, 插件停止运行")
        return

    if msg == "分发接收":
        handle_plugin_distribution_receive(sender)
        return

if __name__ == "__main__":
    main()