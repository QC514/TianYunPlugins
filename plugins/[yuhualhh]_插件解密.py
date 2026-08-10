# [pin: true]
# [title: 插件解密]
# [icon: https://gcore.jsdelivr.net/gh/lhz03/img@83a41e24f620c3195603116058d7d16a698ea9bc/2026/06/21/1ca9a6ea6bc6455906bc07013e94745d.png]
# [language: python]
# [rule: ^插件解密$]
# [disable: false]
# [platform: qq,qb,wx,gw,sb,wb,tg,tb,qx,xy,ip]
# [public: true]
# [open_source: false]
# [class: 工具类]
# [version: 1.0.3]
# [price: 0]
# [admin: false]
# [author: yuhualhh]
# [description: <br>❶该插件可获取已安装的Autman插件进行解密获取插件源码，可用于本地使用或学习研究<br>❷使用本插件需授予一定权限，前往"系统管理-插件权限"全部启用<img src="https://gcore.jsdelivr.net/gh/lhz03/img@991f9103d25f751949f88e2c792bc903c041c7ee/2026/06/21/163cf38a4f750ce4d2b0447d928cd125.png">]

import middleware
import requests
import json
import uuid
import os
import sys
import hashlib
import time

#[param: {"required":false,"key":"yuhua_jmjm.debug_pwd","bool":false,"placeholder":"","name":"调试模式","desc":"非插件开发者无需理会"}]

DECRYPT_API_URL = "http://yuhualhh.250666.xyz/api/plugin_receive.php"
DECRYPT_API_KEY = "YuhuaReceiveApi888"

def printf(msg, level='INFO'):
    c = 32 if level in ['INFO', 'DEBUG'] else 33 if level in ['WARN', 'WARNING'] else 31
    sys.stderr.write(f"\033[{c}m[{level}] {str(msg)}\033[0m\n")
    sys.stderr.flush()

try:
    debug_key = middleware.bucketGet('yuhua_jmjm', 'debug_pwd') or ''
    DEBUG = (debug_key == '123456789abcC@')
except Exception:
    DEBUG = False

if DEBUG:
    printf("🔥🔥🔥 插件解密调试模式已开启，密钥验证通过 🔥🔥🔥", "WARN")


def _distribution_keystream(length):
    secret = "YuhuaDist888888"
    output = bytearray()
    counter = 0
    while len(output) < length:
        output.extend(hashlib.sha256(f"{secret}:{counter}".encode("utf-8")).digest())
        counter += 1
    return bytes(output[:length])


def _encrypt_distribution_cloud_user(cloud_user_id):
    raw = str(cloud_user_id).encode("utf-8")
    ks = _distribution_keystream(len(raw))
    return bytes([a ^ b for a, b in zip(raw, ks)]).hex()


def _is_encrypted(content):
    content = content.strip()
    if not content:
        return False
    if content.startswith('V3v'):
        return True
    if len(content) % 2 == 0 and len(content) >= 32:
        try:
            int(content, 16)
            return True
        except ValueError:
            pass
    return False


def main():
    sender = middleware.Sender(middleware.getSenderID())

    if not sender.isAdmin():
        sender.reply("❌ 权限不足：若非管理员请勿操作")
        return

    cloud_user_id = ""
    try:
        cloud_user_id = sender.bucketGet("cloud", "username") or ""
    except Exception:
        pass
    if not cloud_user_id:
        sender.reply("🚫 未获取到云端账户，请检查是否已授予本插件权限")
        return

    plugin_items = []
    seen = set()

    for bucket in ["plugins_script", "plugins"]:
        try:
            keys_data = middleware.bucketAllKeys(bucket)
            if not keys_data:
                continue
            keys_list = keys_data.split(',') if isinstance(keys_data, str) else keys_data
            for k in keys_list:
                k = str(k).strip()
                if not k or ':' not in k:
                    continue
                author, filename = k.split(':', 1)
                
                display_name = f"{os.path.splitext(filename)[0]}_{author}"
                if display_name in seen:
                    continue
                
                content = middleware.bucketGet(bucket, k)
                is_enc = _is_encrypted(content) if content else False
                
                seen.add(display_name)

                plugin_items.append((display_name, bucket, k, author, filename, is_enc))
        except Exception:
            continue

    if not plugin_items:
        sender.reply("❌ 未找到任何已安装的插件")
        return

    reply_lines = [
        "=====插件解密=====",
        f"🗯️ 本地用户: {cloud_user_id}",
        f"🎉 插件总数: {len(plugin_items)}",
        "------------------"
    ]
    
    for i, (display_name, _, _, _, _, is_enc) in enumerate(plugin_items, 1):
        reply_lines.append(f"[{i}] {display_name}")
        if is_enc:
            reply_lines.append("    ❌ 已加密")
        else:
            reply_lines.append("    ✅ 未加密")
            
    reply_lines.append("------------------")
    reply_lines.append("回复数字选择")
    reply_lines.append('回复"q"退出')
    reply_lines.append("==================")
    sender.reply("\n".join(reply_lines))

    choice = sender.input(60000, 0, False)
    if not choice:
        sender.reply("❌ 输入超时")
        return
    if str(choice).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return

    try:
        idx = int(str(choice).strip()) - 1
        if idx < 0 or idx >= len(plugin_items):
            sender.reply("❌ 无效的选择")
            return
    except ValueError:
        sender.reply("❌ 无效的选择")
        return

    display_name, bucket, key, author, filename, _ = plugin_items[idx]

    encrypted_content = middleware.bucketGet(bucket, key)
    if not encrypted_content:
        sender.reply(f"🚫 读取插件内容失败: {display_name}")
        return

    if not _is_encrypted(encrypted_content):
        sender.reply(f"⚠️ 该插件为开源插件，无需解密")
        return

    sender.reply(f"正在解密...")

    enc_cloud_user = _encrypt_distribution_cloud_user(cloud_user_id)
    target_bucket = bucket
    target_name = key
    voucher = f"{enc_cloud_user}-{target_bucket}-{target_name}"

    decrypt_token = f"d_{uuid.uuid4().hex[:16]}"
    payload = {
        "author": author,
        "plugin_name": filename,
        "admin_user": cloud_user_id,
        "encrypted_content": encrypted_content,
        "voucher": voucher,
        "enc_cloud_user": enc_cloud_user,
        "target_bucket": target_bucket,
        "target_name": target_name
    }
    headers = {
        "X-API-Key": DECRYPT_API_KEY
    }

    if DEBUG:
        printf(f"\n===== [DECRYPT REQUEST START] =====", "DEBUG")
        printf(f"URL: {DECRYPT_API_URL}?action=decrypt_plugin&token={decrypt_token}", "DEBUG")
        printf(f"PAYLOAD: author={author}, plugin_name={filename}, admin_user={cloud_user_id}", "DEBUG")
        printf(f"VOUCHER: {voucher}", "DEBUG")
        printf(f"TARGET_BUCKET: {target_bucket}, TARGET_NAME: {target_name}", "DEBUG")

    max_retries = 3
    last_error = ""
    for attempt in range(max_retries):
        if attempt > 0:
            if DEBUG:
                printf(f"重试第 {attempt} 次...", "WARN")
            time.sleep(2)

        try:
            response = requests.post(
                f"{DECRYPT_API_URL}?action=decrypt_plugin&token={decrypt_token}",
                json=payload,
                headers=headers,
                timeout=60
            )

            if DEBUG:
                printf(f"RESPONSE STATUS: {response.status_code}", "DEBUG")
                printf(f"RESPONSE BODY: {response.text[:500]}", "DEBUG")

            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    link = f"{DECRYPT_API_URL}?token={decrypt_token}"
                    sender.reply(f"分发凭证: {voucher}")
                    sender.reply(f"分发链接: {link}")
                    return
                else:
                    last_error = data.get('msg', '未知错误')
                    sender.reply(f"🚫 解密失败: {last_error}")
                    return
            elif response.status_code >= 500:
                last_error = f"服务器错误 HTTP {response.status_code}"
                if DEBUG:
                    printf(f"服务端错误，将重试: {last_error}", "WARN")
                continue
            else:
                sender.reply(f"🚫 解密请求失败: HTTP {response.status_code}")
                return

        except requests.exceptions.Timeout:
            last_error = "请求超时"
            if DEBUG:
                printf(f"请求超时，将重试 ({attempt+1}/{max_retries})", "WARN")
            continue
        except requests.exceptions.ConnectionError:
            last_error = "无法连接到解密服务"
            if DEBUG:
                printf(f"连接失败，将重试 ({attempt+1}/{max_retries})", "WARN")
            continue
        except Exception as e:
            last_error = str(e)
            if DEBUG:
                printf(f"请求异常: {e}", "WARN")
            continue

    if DEBUG:
        printf(f"重试 {max_retries} 次后仍失败: {last_error}", "WARN")
    sender.reply(f"🚫 解密失败（已重试{max_retries}次）: {last_error}")


if __name__ == "__main__":
    main()
