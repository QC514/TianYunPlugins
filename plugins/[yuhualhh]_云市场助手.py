# [pin: true]
# [title: 云市场助手]
# [icon: https://gcore.jsdelivr.net/gh/lhz03/img@48d24f5ca4f7aa8cf67bbea103ed719d0d644bb7/2026/04/03/a064605baef0d7906b0b7273db179e6a.png]
# [language: python]
# [rule: ^云端.*$]
# [disable:false]
# [cron: */5 * * * *]
# [open_source: false]
# [platform: qq,qb,wx,gw,sb,wb,tg,tb,qx,xy,ip]
# [class: 工具类]
# [priority: 9999]
# [public: true]
# [version: 1.1.8]
# [author: yuhualhh]
# [price: 0]
# [service: ]
# [description: <br>❶这是一个提供插件开发者使用的十分完善且强大的云市场助手插件，支持 自动采集自建市场已上架插件数据并同步到云订阅助手云端、充币减币、插件授权、插件分发、管理授权、动态推送、定时云备案 等众多细化操作<br>❷使用本插件需授予一定权限，前往"系统管理-插件权限"全部启用<br>❸若非首次安装，需修改插件配置的执行定时为『*/5 * * * *』<br>❹部分功能的实现需自行添加计划任务，关于指令『云端备案』定时『*/30 * * * *』<img src="https://gcore.jsdelivr.net/gh/lhz03/img@8ce6e06c6d739695decf26959fff627e2b4a4f1d/2025/09/22/4265a8969c194f3960702f753c1a12a5.png">]

import middleware
import time
import requests
import json
import re
import sys
import os
import uuid
import hashlib
import gzip
from urllib.parse import quote
from bs4 import BeautifulSoup
from decimal import Decimal, InvalidOperation

#[param: {"required":false,"key":"yuhua_sqzs.local_dispatch","bool":true,"placeholder":"","name":"本地分发","desc":"默认使用羽化自建接口，勾选后会使用本地加密分发接口"}]
#[param: {"required":false,"key":"yuhua_sqzs.cloud_collect","bool":true,"placeholder":"","name":"云端采集","desc":"自动采集自建市场已上架插件数据并同步到云订阅助手云端"}]
#[param: {"required":false,"key":"yuhua_sqzs.user_push","bool":true,"placeholder":"","name":"用户推送","desc":"将插件动态推送已订阅用户"}]
#[param: {"required":false,"key":"yuhua_sqzs.group_push","bool":true,"placeholder":"","name":"群组推送","desc":"将插件动态推送指定群组"}]
#[param: {"required":false,"key":"yuhua_sqzs.group_id","placeholder":"","name":"群组列表","desc":"填写接收插件动态推送的群组ID，多个群请用英文逗号,分隔"}]
#[param: {"required":false,"key":"yuhua_sqzs.debug_pwd","bool":false,"placeholder":"","name":"调试模式","desc":"非插件开发者无需理会"}]

# 封装函数：支持颜色分级(INFO=绿, WARN=黄, 其他=红)，输出到stderr确保控制台可见
def printf(msg, level='INFO'):
    c = 32 if level in ['INFO', 'DEBUG'] else 33 if level in ['WARN', 'WARNING'] else 31
    sys.stderr.write(f"\033[{c}m[{level}] {str(msg)}\033[0m\n")
    sys.stderr.flush()

debug_key = middleware.bucketGet('yuhua_sqzs', 'debug_pwd') or ''
DEBUG = (debug_key == '123456789abcC@')
if DEBUG:
    printf("🔥🔥🔥 调试模式已开启，密钥验证通过 🔥🔥🔥", "WARN")

SUBHUB_BACKEND_URL = 'https://yuhualhh.250666.xyz/api/subscription_hub.php'
SUBHUB_BACKEND_KEY = 'yuhualhh666666'
REMOTE_TIMEOUT = 60

def _make_request(method, url, **kwargs):
    if DEBUG:
        printf(f"\n===== [REQUEST START] =====", "DEBUG")
        printf(f"METHOD: {method} | URL: {url}", "DEBUG")
        printf(f"HEADERS: {json.dumps(kwargs.get('headers', {}), ensure_ascii=False)}", "DEBUG")
        if kwargs.get('json'):
            printf(f"BODY(JSON): {json.dumps(kwargs.get('json'), ensure_ascii=False)}", "DEBUG")
        elif kwargs.get('data'):
            data_str = str(kwargs.get('data'))
            if len(data_str) > 500: data_str = data_str[:200] + "...(truncated)..."
            printf(f"BODY(DATA): {data_str}", "DEBUG")

    for attempt in range(3):
        try:
            if method.lower() == 'get':
                response = requests.get(url, **kwargs)
            else:
                response = requests.post(url, **kwargs)
                
            if DEBUG:
                printf(f"-----[RESPONSE - Attempt {attempt+1}] -----", "DEBUG")
                printf(f"STATUS: {response.status_code}", "DEBUG")
                printf(f"RSP HEADERS: {json.dumps(dict(response.headers), ensure_ascii=False)}", "DEBUG")
                try:
                    printf(f"RSP BODY: {json.dumps(response.json(), ensure_ascii=False)}", "DEBUG")
                except:
                    printf(f"RSP BODY: {response.text[:1000]}", "DEBUG")
                printf(f"===== [REQUEST END] =====\n", "DEBUG")
                
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if DEBUG: printf(f"⚠️ Attempt {attempt+1} Failed: {e}", "WARN")
            time.sleep(1)
        except Exception as e:
            if DEBUG: printf(f"⚠️ Request Error: {e}", "WARN")
            time.sleep(1)
    return None

def _send_multi_platform_push_to_group(group_id, message):
    platforms = ['qq', 'qb', 'wx', 'gw', 'sb', 'wb', 'tg', 'tb', 'qx', 'xy', 'ip']
    for platform in platforms:
        try:
            middleware.push(
                imType=platform,
                groupCode=int(group_id),
                userID=0,
                title="",
                content=message
            )
            time.sleep(0.1)
        except Exception:
            pass

def _send_multi_platform_push_to_user(user_id, message):
    platforms = ['qq', 'qb', 'wx', 'gw', 'sb', 'wb', 'tg', 'tb', 'qx', 'xy', 'ip']
    for platform in platforms:
        try:
            middleware.push(
                imType=platform,
                groupCode=0,
                userID=user_id,
                title="",
                content=message
            )
            time.sleep(0.1)
        except Exception:
            pass

def _get_cloud_username(sender):
    return (sender.bucketGet('cloud', 'username') or '').strip()

def _build_node_id(sender):
    cloud_user = _get_cloud_username(sender) or 'unknown'
    admin = str(sender.bucketGet('autMan', 'adminUsername') or 'unknown')
    seed = f'{cloud_user}|{admin}|cloud_market_hub'
    return hashlib.sha1(seed.encode('utf-8')).hexdigest()[:24]

def _backend_request(method, action, payload=None, timeout=REMOTE_TIMEOUT):
    url = f'{SUBHUB_BACKEND_URL}?action={quote(action)}'
    headers = {'X-API-Key': SUBHUB_BACKEND_KEY}
    last_err = '云端请求失败'
    for attempt in range(1, 4):
        try:
            body = json.dumps(payload or {}, ensure_ascii=False).encode('utf-8')
            gz = gzip.compress(body)
            req_headers = dict(headers)
            req_headers.update({
                'Content-Type': 'application/json',
                'Content-Encoding': 'gzip'
            })
            resp = _make_request('post', url, headers=req_headers, data=gz, timeout=timeout)
            if not resp:
                last_err = '云端请求失败'
                if attempt < 3:
                    time.sleep(1)
                    continue
                return None, last_err
            try:
                data = resp.json()
            except Exception:
                data = {}
            if resp.status_code in [500, 502, 503, 504]:
                last_err = data.get('message') or f'HTTP {resp.status_code}'
                if attempt < 3:
                    time.sleep(1)
                    continue
                return None, last_err
            if resp.status_code != 200:
                return None, data.get('message') or f'HTTP {resp.status_code}'
            if data.get('code') != 200:
                return None, data.get('message') or '云端返回异常'
            return data.get('data'), ''
        except Exception as e:
            last_err = f'云端异常: {str(e)[:120]}'
            if attempt < 3:
                time.sleep(1)
                continue
    return None, last_err

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
                    middleware.bucketDel("yuhua_sqzs", "autMan")
                except Exception:
                    pass
                continue
            else:
                return response
        except json.JSONDecodeError:
            if response.status_code == 401:
                try:
                    middleware.bucketDel("yuhua_sqzs", "autMan")
                except Exception:
                    pass
                continue
            return response
    return None

def _get_user_status(cloud_user_id):
    blacklist_str = middleware.bucketGet("autMarketCfgs", "blacklist") or ""
    if cloud_user_id in [uid.strip() for uid in blacklist_str.split(',')]:
        return "❌ 云端状态: 黑名单"
    whitelist_str = middleware.bucketGet("autMarketCfgs", "testers") or ""
    if cloud_user_id in [uid.strip() for uid in whitelist_str.split(',')]:
        return "✅ 云端状态: 白名单"
    return "✅ 云端状态: 普通用户"

def handle_bind_account(sender):
    local_user_id = sender.getUserID()
    binding_bucket = "yuhua_sqzs_user"
    current_binding = middleware.bucketGet(binding_bucket, local_user_id)
    if current_binding:
        sender.reply(f"""=====云端绑定=====
❌ 您目前已经绑定云账号
💡 发送 云端解绑 解绑账号
==================""")
        return
    prompt_user = """=====云端绑定=====
请输入您的云账号
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    cloud_user_id_input = sender.input(60000, 0, False)
    if not cloud_user_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(cloud_user_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    cloud_user_id = str(cloud_user_id_input).strip()
    if not cloud_user_id:
        sender.reply("🚫 云账号不能为空")
        return
    middleware.bucketSet(binding_bucket, local_user_id, cloud_user_id)
    user_status = _get_user_status(cloud_user_id)
    sender.reply(f"""=====绑定成功=====
🗯️ 云端用户: {cloud_user_id}
{user_status}
------------------
发送"云端市场"进行授权
发送"云端查询"查询授权""")
    return

def handle_unbind_account(sender):
    local_user_id = sender.getUserID()
    binding_bucket = "yuhua_sqzs_user"
    current_binding = middleware.bucketGet(binding_bucket, local_user_id)
    if not current_binding:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 云端绑定 绑定账号
==================""")
        return
    user_status = _get_user_status(current_binding)
    prompt_confirm = f"""=====云端解绑=====
🗯️ 云端用户: {current_binding}
{user_status}
------------------
回复"确认"继续
回复"q"退出"""
    sender.reply(prompt_confirm)
    confirm_input = sender.input(60000, 0, False)
    if not confirm_input:
        sender.reply("❌ 输入超时")
        return
    if str(confirm_input).lower() != '确认':
        sender.reply("✅ 已取消解绑操作")
        return
    try:
        middleware.bucketDel(binding_bucket, local_user_id)
    except Exception:
        pass
    sender.reply(f"""=====云端解绑=====
🗯️ 云端用户: {current_binding}   
✨ 操作结果: 已成功解绑该云账号
==================""")
    return

def handle_market_query(sender):
    local_user_id = sender.getUserID()
    binding_bucket = "yuhua_sqzs_user"
    cloud_user_id = middleware.bucketGet(binding_bucket, local_user_id)
    if not cloud_user_id:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 云端绑定 绑定账号
==================""")
        return
    try:
        response = _autman_api_request(sender, "get", "/shelf", timeout=10)
        if not response:
            sender.reply("🚫 访问云端市场失败，请检查网络或插件权限")
            return
        data = response.json()
        if data.get("code") != 200:
            sender.reply(f"🚫 查询失败: {data.get('message', '未知错误')}")
            return
        plugins = data.get("data", [])
        public_plugins = [p for p in plugins if p.get("public")]
        if not public_plugins:
            sender.reply("❌ 云端市场暂未上架插件")
            return
        coins_str = middleware.bucketGet("autMarketCoins", cloud_user_id) or "0"
        cloud_coins = int(coins_str) if coins_str.isdigit() else 0
        cloud_plugins_str = middleware.bucketGet("autMarketBoughts", cloud_user_id) or ""
        cloud_plugins_list = [p.strip() for p in cloud_plugins_str.split(',') if p.strip()]
        user_status = _get_user_status(cloud_user_id)
        is_whitelist = "白名单" in user_status
        reply_parts = [f"=====云端市场=====\n🗯️ 云端用户: {cloud_user_id}\n💰 云端云币: {cloud_coins}\n{user_status}\n------------------"]
        for i, plugin in enumerate(public_plugins, 1):
            title = plugin.get("title", "无标题插件")
            version = plugin.get("version", "未知")
            price = Decimal(str(plugin.get("price", 0))).quantize(Decimal("0.00"))
            status_icon = "✅" if title in cloud_plugins_list else "❌"
            if is_whitelist:
                price_str = "免费"
            else:
                price_str = "免费" if price <= 0 else f"售价{price}元"
            reply_parts.append(f"[{i}] {title} v{version}\n    {status_icon} {price_str}")
        reply_parts.append("------------------\n回复数字选择\n回复\"q\"退出\n==================")
        sender.reply("\n".join(reply_parts))
        choice_str = sender.input(60000, 0, False)
        if not choice_str:
            sender.reply("❌ 输入超时")
            return
        if str(choice_str).lower() == 'q':
            sender.reply("✅ 已退出操作")
            return
        try:
            selected_plugin = public_plugins[int(choice_str) - 1]
        except (ValueError, IndexError):
            sender.reply("❌ 无效的选择")
            return
        sender.reply("=====操作列表=====\n[1] 授权插件\n[2] 插件详情\n[3] 插件分发\n------------------\n回复数字选择\n回复\"q\"退出")
        action_choice = sender.input(60000, 0, False)
        if not action_choice:
            sender.reply("❌ 输入超时")
            return
        if str(action_choice).lower() == 'q':
            sender.reply("✅ 已退出操作")
            return
        plugin_title = selected_plugin.get("title")
        if action_choice == '1':
            if "黑名单" in user_status:
                sender.reply(f"""=====云端授权=====
🗯️ 云端用户: {cloud_user_id}
💥 云端插件: {plugin_title}
✨ 操作结果: 黑名单用户禁止授权
==================""")
                return
            if plugin_title in cloud_plugins_list:
                sender.reply(f"=====云端授权=====\n🗯️ 云端用户: {cloud_user_id}\n💥 云端插件: {plugin_title}\n✨ 操作结果: 已存在该插件授权\n==================")
                return
            plugin_price = Decimal(str(selected_plugin.get("price", 0))).quantize(Decimal("0.00"))
            if plugin_price <= 0 or "白名单" in user_status:
                current_plugins_str = middleware.bucketGet("autMarketBoughts", cloud_user_id) or ""
                new_plugins_str = f"{current_plugins_str},{plugin_title}".strip(',')
                middleware.bucketSet("autMarketBoughts", cloud_user_id, new_plugins_str)
                sender.reply(f"=====云端授权=====\n🗯️ 云端用户: {cloud_user_id}\n💥 云端插件: {plugin_title}\n✨ 操作结果: 成功授权插件\n==================")
                return
            qrcode_url = middleware.bucketGet("autMarketCfgs", "qrcode")
            if not qrcode_url:
                sender.reply("🚫 管理员未配置自建市场收款码")
                return
            pay_msg = f"""=====扫码支付=====
🗯️ 云端用户: {cloud_user_id}
💥 云端插件: {plugin_title}
💰 支付金额: {plugin_price:.2f}元
------------------
请在120秒内完成
回复"q"取消"""
            sender.reply(pay_msg)
            sender.replyImage(qrcode_url)
            payment_result = None
            try:
                payment_result = sender.waitPay("q", 120 * 1000)
            except Exception as e:
                error_str = str(e).lower()
                if "timeout" in error_str or "timed out" in error_str:
                    sender.reply("❌ 支付超时")
                else:
                    sender.reply(f"""=====支付异常=====
❌ 等待支付时发生错误
------------------
⚠️ 错误: {str(e)[:50]}
==================""")
                return
            if not payment_result:
                sender.reply("❌ 支付超时")
                return
            if str(payment_result).lower() == 'q':
                sender.reply("✅ 已取消支付")
                return
            try:
                payment_data = json.loads(payment_result) if isinstance(payment_result, str) else payment_result
                raw_paid_money = payment_data.get('Money', payment_data.get('money', 0))
                paid_money = Decimal(f"{raw_paid_money:.2f}")
                if paid_money < plugin_price:
                    sender.reply(f"=====支付失败=====\n❌ 支付金额不足\n💰 应付: {plugin_price:.2f}元\n💵 实付: {paid_money}元\n==================")
                    return
            except Exception as e:
                sender.reply(f"""=====支付异常=====
❌ 支付验证失败
------------------
⚠️ 错误: {str(e)[:50]}
==================""")
                return
            current_plugins_str = middleware.bucketGet("autMarketBoughts", cloud_user_id) or ""
            new_plugins_str = f"{current_plugins_str},{plugin_title}".strip(',')
            middleware.bucketSet("autMarketBoughts", cloud_user_id, new_plugins_str)
            details_value = f"{cloud_user_id},{plugin_title},{plugin_price}"
            middleware.bucketSet("autMarketBoughtDetails", str(int(time.time())), details_value)
            sender.reply(f"""=====云端授权=====
🗯️ 云端用户: {cloud_user_id}
💥 云端插件: {plugin_title}
✨ 操作结果: 成功授权插件
==================""")
        elif action_choice == '2':
            title = selected_plugin.get("title", "未知")
            language = selected_plugin.get("language", "未知")
            version = selected_plugin.get("version", "未知")
            price = Decimal(str(selected_plugin.get("price", "0"))).quantize(Decimal("0.00"))
            description = selected_plugin.get("description", "")
            image_url = None
            img_match = re.search(r'<img src="([^"]+)">', description)
            if img_match:
                image_url = img_match.group(1)
                description = description.replace(img_match.group(0), "")
            description = description.replace("<br>", "\n")
            description = re.sub(r'<[^>]+>', '', description).strip()
            details_text = f"""名称：{title}
语言：{language}
版本：{version}
价格：{price}
描述：
{description}"""
            if image_url:
                final_reply = f"{details_text}\n[CQ:image,file={image_url}]"
                sender.reply(final_reply)
            else:
                sender.reply(details_text)
        elif action_choice == '3':
            handle_plugin_distribution(sender, selected_plugin, cloud_user_id)
        else:
            sender.reply("❌ 无效的选择")
    except Exception as e:
        sender.reply(f"🚫 处理云端市场数据时发生未知错误: {e}")
    return

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

def _build_distribution_voucher(cloud_user_id, plugin_language, admin_user, plugin_title, original_filename_base):
    enc_cloud_user = _encrypt_distribution_cloud_user(cloud_user_id)
    if plugin_language == "es5":
        target_bucket = "plugins"
        target_name = f"{admin_user}:{plugin_title}.js"
    else:
        target_bucket = "plugins_script"
        target_name = f"{admin_user}:{original_filename_base}"
    return f"{enc_cloud_user}-{target_bucket}-{target_name}"

def _create_distribution_link(voucher, target_bucket, target_name, encrypted_content):
    distribution_token = f"d_{uuid.uuid4().hex[:16]}"
    distribution_url = "http://yuhualhh.250666.xyz/api/plugin_receive.php"
    payload = {
        "voucher": voucher,
        "enc_cloud_user": voucher.split('-', 1)[0],
        "target_bucket": target_bucket,
        "target_name": target_name,
        "plugin_text": encrypted_content
    }
    headers = {
        "X-API-Key": "YuhuaReceiveApi888",
        "Content-Type": "application/json"
    }
    response = _make_request(
        "post",
        f"{distribution_url}?action=init_session&token={distribution_token}",
        json=payload,
        headers=headers,
        timeout=15
    )
    if response and response.status_code == 200:
        try:
            data = response.json()
            if data.get("code") == 0:
                return f"{distribution_url}?token={distribution_token}"
        except Exception:
            pass
    return None

def handle_plugin_distribution(sender, selected_plugin, cloud_user_id):
    plugin_title = selected_plugin.get("title")
    blacklist_str = middleware.bucketGet("autMarketCfgs", "blacklist") or ""
    if cloud_user_id in [uid.strip() for uid in blacklist_str.split(',')]:
        sender.reply(f"""=====插件分发=====
🗯️ 云端用户: {cloud_user_id}
✨ 操作结果: 黑名单用户禁止操作
==================""")
        return
    cloud_plugins_str = middleware.bucketGet("autMarketBoughts", cloud_user_id) or ""
    cloud_plugins_list = [p.strip() for p in cloud_plugins_str.split(',') if p.strip()]
    plugin_price = Decimal(str(selected_plugin.get("price", 0))).quantize(Decimal("0.00"))
    if plugin_price > 0 and plugin_title not in cloud_plugins_list:
        sender.reply(f"""=====插件分发=====
🗯️ 云端用户: {cloud_user_id}
✨ 操作结果: 不存在该插件授权
==================""")
        return
    plugin_path = selected_plugin.get("plugin_path")
    try:
        with open(plugin_path, 'r', encoding='utf-8') as f:
            plugin_content = f.read()
    except Exception as e:
        sender.reply(f"🚫 读取插件源文件失败: {e}")
        return
    from urllib.parse import quote
    plugin_language = selected_plugin.get("language", "python")
    admin_user = sender.bucketGet("cloud", "username") or "作者订阅源"
    payload = {
    "content": plugin_content,
    "key": cloud_user_id,
    "title": quote(plugin_title),
    "author": admin_user
}
    headers = { 'Content-Type': 'application/json' }
    try:
        local_dispatch_str = middleware.bucketGet("yuhua_sqzs", "local_dispatch")
        local_dispatch = str(local_dispatch_str).strip().lower() in ["true", "1", "on", "yes"]
        
        if local_dispatch:
            api_response = _autman_api_request(sender, "post", "/js/encrypt", headers=headers, json=payload, timeout=20)
        else:
            api_response = _make_request("post", "https://fandai.250666.xyz/api/encrypt_api.php", headers=headers, json=payload, timeout=20)
            
        if not api_response:
            sender.reply("🚫 插件分发失败，请检查网络或插件权限")
            return
        if api_response.status_code == 200:
            response_data = api_response.json()
            if response_data.get("code") == 200 and "data" in response_data:
                encrypted_content = response_data["data"]
                original_filename_base = os.path.basename(plugin_path)
                voucher = _build_distribution_voucher(cloud_user_id, plugin_language, admin_user, plugin_title, original_filename_base)
                if plugin_language == "es5":
                    target_bucket = "plugins"
                    target_key = f"{admin_user}:{plugin_title}"
                    target_name = f"{admin_user}:{plugin_title}.js"
                else:
                    target_bucket = "plugins_script"
                    target_key = f"{admin_user}:{original_filename_base}"
                    target_name = f"{admin_user}:{original_filename_base}"
                distribution_link = _create_distribution_link(voucher, target_bucket, target_name, encrypted_content)
                if not distribution_link:
                    sender.reply("🚫 插件分发失败，生成分发链接失败")
                    return
                sender.reply(f"分发凭证: {voucher}")
                sender.reply(f"分发链接: {distribution_link}")
                auto_usage_prompt = f"""=====自动导入教程=====
①请在5分钟内复制分发凭证与分发链接
②添加订阅源yuhualhh，安装『分发接收助手』插件，授予权限后发指令『分发接收』使用
❸若订阅源yuhualhh离线，请扫码添加分发Bot获取『分发接收助手』插件手动导入后使用
[CQ:image,file=https://gcore.jsdelivr.net/gh/lhz03/img@8fff3e65234512e046acfa76486fb62690f88c58/2026/05/07/7997b99ec4e6a8ae1d3ea95c9a137ea2.png]
=================="""
                manual_usage_prompt = f"""=====手动导入教程=====
❶请在5分钟内打开分发链接并复制全部分发数据
❷进入奥特曼后台-本地开发-数据管理，左侧搜索"{target_bucket}"并点击
❸右侧搜索"{target_key}"，若不存在记录，则点击"新增行”，在Key输入框填"{target_key}"，在Value输入框填操作❶复制的内容，点击保存并重启奥特曼。若存在记录，则替换Value输入框内容点击保存并重启奥特曼
❹重启后前往“应用市场-我的”找到插件并使用
=================="""
                sender.reply(auto_usage_prompt)
                sender.reply(manual_usage_prompt)
            else:
                sender.reply(f"🚫 插件分发失败，API返回逻辑错误: {response_data.get('message', '未知错误')}")
        else:
            sender.reply(f"🚫 插件分发失败，API返回错误: {api_response.status_code} - {api_response.text}")
    except Exception as e:
        sender.reply(f"🚫 插件分发时发生异常: {e}")
    return

def handle_grant_authorization(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    prompt_user = """=====云端授权=====
请输入目标云账号
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    user_id_input = sender.input(60000, 0, False)
    if not user_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(user_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    user_id = str(user_id_input).strip()
    if not user_id:
        sender.reply("🚫 目标云账号不能为空")
        return
    try:
        response = _autman_api_request(sender, "get", "/shelf", timeout=10)
        if not response:
            sender.reply("🚫 访问云端市场失败，请检查网络或插件权限")
            return
        data = response.json()
        if data.get("code") != 200:
            sender.reply("🚫 访问云端市场失败，请稍后重试")
            return
        all_plugins = data.get("data", [])
        if not all_plugins:
            sender.reply("❌ 云端市场没有任何插件可供授权")
            return
        boughts_bucket = "autMarketBoughts"
        current_plugins_str = middleware.bucketGet(boughts_bucket, user_id) or ""
        current_plugins_list = [p.strip() for p in current_plugins_str.split(',') if p.strip()]
        user_status = _get_user_status(user_id)
        reply_parts = [f"=====云端授权=====\n🗯️ 云端用户: {user_id}\n{user_status}\n------------------"]
        for i, plugin in enumerate(all_plugins, 1):
            title = plugin.get("title", "无标题插件")
            version = plugin.get("version", "未知")
            price = Decimal(str(plugin.get("price", 0))).quantize(Decimal("0.00"))
            status_icon = "✅" if title in current_plugins_list else "❌"
            price_str = "免费" if price <= 0 else f"售价{price}元"
            reply_parts.append(f"[{i}] {title} v{version}\n    {status_icon} {price_str}")
        reply_parts.append("------------------\n回复数字选择\n回复\"q\"退出\n==================")
        sender.reply("\n".join(reply_parts))
        choice_str = sender.input(60000, 0, False)
        if not choice_str:
            sender.reply("❌ 输入超时")
            return
        if str(choice_str).lower() == 'q':
            sender.reply("✅ 已退出操作")
            return
        try:
            selected_plugin = all_plugins[int(choice_str) - 1]
            plugin_name = selected_plugin.get("title")
        except (ValueError, IndexError):
            sender.reply("❌ 无效的选择")
            return
        if plugin_name in current_plugins_list:
            sender.reply(f"""=====云端授权=====
🗯️ 云端用户: {user_id}
💥 云端插件: {plugin_name}
✨ 操作结果: 已存在该插件授权
==================""")
            return
        current_plugins_list.append(plugin_name)
        middleware.bucketSet(boughts_bucket, user_id, ",".join(current_plugins_list))
        details_value = f"{user_id},{plugin_name},0"
        middleware.bucketSet("autMarketBoughtDetails", str(int(time.time())), details_value)
        sender.reply(f"""=====云端授权=====
🗯️ 云端用户: {user_id}
💥 云端插件: {plugin_name}
✨ 操作结果: 成功授权插件
==================""")
    except Exception as e:
        sender.reply(f"🚫 处理授权时发生未知错误: {e}")
    return

def handle_query_authorization(sender):
    local_user_id = sender.getUserID()
    binding_bucket = "yuhua_sqzs_user"
    cloud_user_id = middleware.bucketGet(binding_bucket, local_user_id)
    if not cloud_user_id:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 云端绑定 绑定账号
==================""")
        return
    coins_str = middleware.bucketGet("autMarketCoins", cloud_user_id) or "0"
    cloud_coins = int(coins_str) if coins_str.isdigit() else 0
    plugins_str = middleware.bucketGet("autMarketBoughts", cloud_user_id) or ""
    plugins_list = [p.strip() for p in plugins_str.split(',') if p.strip()]
    plugins_display_str = ", ".join(plugins_list) if plugins_list else "无"
    user_status = _get_user_status(cloud_user_id)
    reply_found = f"""=====云端查询=====
🤪 本地用户: {local_user_id}
🗯️ 云端用户: {cloud_user_id}
💰 云端云币: {cloud_coins}
{user_status}
💥 云端插件: {plugins_display_str}
=================="""
    sender.reply(reply_found)
    return

def handle_revoke_authorization(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    prompt_user = """=====云端收权=====
请输入目标云账号
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    user_id_input = sender.input(60000, 0, False)
    if not user_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(user_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    user_id = str(user_id_input).strip()
    if not user_id:
        sender.reply("🚫 目标云账号不能为空")
        return
    try:
        response = _autman_api_request(sender, "get", "/shelf", timeout=10)
        if not response:
            sender.reply("🚫 访问云端市场失败，请检查网络或插件权限")
            return
        data = response.json()
        if data.get("code") != 200:
            sender.reply("🚫 访问云端市场失败，请稍后重试")
            return
        all_plugins = data.get("data", [])
        if not all_plugins:
            sender.reply("❌ 云端市场没有任何插件可供操作")
            return
        boughts_bucket = "autMarketBoughts"
        details_bucket = "autMarketBoughtDetails"
        current_plugins_str = middleware.bucketGet(boughts_bucket, user_id) or ""
        current_plugins_list = [p.strip() for p in current_plugins_str.split(',') if p.strip()]
        user_status = _get_user_status(user_id)
        reply_parts = [f"=====云端收权=====\n🗯️ 云端用户: {user_id}\n{user_status}\n------------------"]
        for i, plugin in enumerate(all_plugins, 1):
            title = plugin.get("title", "无标题插件")
            version = plugin.get("version", "未知")
            price = Decimal(str(plugin.get("price", 0))).quantize(Decimal("0.00"))
            status_icon = "✅" if title in current_plugins_list else "❌"
            price_str = "免费" if price <= 0 else f"售价{price}元"
            reply_parts.append(f"[{i}] {title} v{version}\n    {status_icon} {price_str}")
        reply_parts.append("------------------\n回复数字选择\n回复\"q\"退出\n==================")
        sender.reply("\n".join(reply_parts))
        choice_str = sender.input(60000, 0, False)
        if not choice_str:
            sender.reply("❌ 输入超时")
            return
        if str(choice_str).lower() == 'q':
            sender.reply("✅ 已退出操作")
            return
        try:
            selected_plugin = all_plugins[int(choice_str) - 1]
            plugin_name = selected_plugin.get("title")
        except (ValueError, IndexError):
            sender.reply("❌ 无效的选择")
            return
        if plugin_name not in current_plugins_list:
            result_msg = "该用户未授权此插件"
        else:
            current_plugins_list.remove(plugin_name)
            middleware.bucketSet(boughts_bucket, user_id, ",".join(current_plugins_list))
            all_details = middleware.bucketAll(details_bucket)
            if all_details:
                for transaction_id, details_value in all_details.items():
                    try:
                        parts = details_value.split(',')
                        if len(parts) >= 2 and parts[0] == user_id and parts[1] == plugin_name:
                            middleware.bucketDel(details_bucket, transaction_id)
                    except:
                        continue
            result_msg = "成功取消该插件授权"
        reply = f"""=====授权收权=====
🗯️ 云端用户: {user_id}
💥 云端插件: {plugin_name}
✨ 操作结果: {result_msg}
=================="""
        sender.reply(reply)
    except Exception as e:
        sender.reply(f"🚫 处理收权时发生未知错误: {e}")
    return

def _get_autman_cookie(sender):
    cookie = sender.bucketGet("yuhua_sqzs", "autMan")
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
                middleware.bucketSet("yuhua_sqzs", "autMan", cookie_value)
                return cookie_value
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None

def _handle_list_management(sender, action, list_type):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    if list_type == "blacklist":
        bucket_key, title_verb, noun = "blacklist", "加黑", "黑名单"
    elif list_type == "whitelist":
        bucket_key, title_verb, noun = "testers", "加白", "白名单"
    else:
        return
    action_verb = "删除" if action == "remove" else title_verb
    title = f"授权{action_verb}"
    prompt_user = f"""====={title}=====
请输入目标云账号
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    user_id_input = sender.input(60000, 0, False)
    if not user_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(user_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    user_id = str(user_id_input).strip()
    if not user_id:
        sender.reply("🚫 目标云账号不能为空")
        return
    bucket_name = "autMarketCfgs"
    current_list_str = middleware.bucketGet(bucket_name, bucket_key) or ""
    current_list = [uid.strip() for uid in current_list_str.split(',') if uid.strip()]
    result_msg = ""
    if action == "add":
        if user_id in current_list:
            result_msg = f"已存在于{noun}"
        else:
            current_list.append(user_id)
            middleware.bucketSet(bucket_name, bucket_key, ",".join(current_list))
            result_msg = f"成功加入{noun}"
    elif action == "remove":
        if user_id not in current_list:
            result_msg = f"未存在于{noun}"
        else:
            current_list.remove(user_id)
            middleware.bucketSet(bucket_name, bucket_key, ",".join(current_list))
            result_msg = f"成功移出{noun}"
    sender.reply(f"""====={title}=====
🗯️ 云端用户: {user_id}
✨ 操作结果: {result_msg}
==================""")
    return

def _handle_modify_coins(sender, operation):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    if operation == "add":
        title, prompt_verb, reply_label = "云端加币", "增加", "➕ 增加云币"
    elif operation == "subtract":
        title, prompt_verb, reply_label = "云端减币", "扣除", "➖ 扣除云币"
    else:
        return
    prompt_user = f"""====={title}=====
请输入目标云账号
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    user_id_input = sender.input(60000, 0, False)
    if not user_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(user_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    user_id = str(user_id_input).strip()
    if not user_id:
        sender.reply("🚫 目标云账号不能为空")
        return
    prompt_amount = f"""====={title}=====
请输入要{prompt_verb}的云币数量
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_amount)
    amount_input = sender.input(60000, 0, False)
    if not amount_input:
        sender.reply("❌ 输入超时")
        return
    if str(amount_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    try:
        amount = int(str(amount_input).strip())
        if amount <= 0:
            sender.reply(f"🚫 {prompt_verb}的数量必须为正整数")
            return
    except ValueError:
        sender.reply("🚫 请输入有效的数字")
        return
    bucket_name = "autMarketCoins"
    coins_str = middleware.bucketGet(bucket_name, user_id) or "0"
    current_coins = int(coins_str) if coins_str.isdigit() else 0
    new_coins = current_coins + amount if operation == "add" else current_coins - amount
    middleware.bucketSet(bucket_name, user_id, str(new_coins))
    sender.reply(f"""====={title}=====
🗯️ 云端用户: {user_id}
{reply_label}: {amount}
💰 云端云币: {new_coins}
==================""")
    return

def handle_admin_query_user(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    prompt_user = """=====云端查户=====
请输入云账号或用户ID
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    user_id_input_str = sender.input(60000, 0, False)
    if not user_id_input_str:
        sender.reply("❌ 输入超时")
        return
    user_id_input = str(user_id_input_str).strip()
    if user_id_input.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    if not user_id_input:
        sender.reply("🚫 云账号或用户ID不能为空")
        return
    binding_bucket = "yuhua_sqzs_user"
    cloud_user_id = middleware.bucketGet(binding_bucket, user_id_input)
    local_user_id_display = user_id_input
    if not cloud_user_id:
        cloud_user_id = user_id_input
        all_bindings = middleware.bucketAll(binding_bucket)
        found_local_id = "未绑定"
        if all_bindings:
            for local_id, bound_cloud_id in all_bindings.items():
                if bound_cloud_id == cloud_user_id:
                    found_local_id = local_id
                    break
        local_user_id_display = found_local_id
    coins_str = middleware.bucketGet("autMarketCoins", cloud_user_id) or "0"
    cloud_coins = int(coins_str) if coins_str.isdigit() else 0
    plugins_str = middleware.bucketGet("autMarketBoughts", cloud_user_id) or ""
    plugins_list = [p.strip() for p in plugins_str.split(',') if p.strip()]
    plugins_display_str = ", ".join(plugins_list) if plugins_list else "无"
    user_status = _get_user_status(cloud_user_id)
    reply_found = f"""=====云端查询=====
🤪 本地用户: {local_user_id_display}
🗯️ 云端用户: {cloud_user_id}
💰 云端云币: {cloud_coins}
{user_status}
💥 云端插件: {plugins_display_str}
=================="""
    sender.reply(reply_found)
    return
    
 
def handle_admin_distribution(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    prompt_user = """=====云端分发=====
请输入目标云账号
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    cloud_user_id_input = sender.input(60000, 0, False)
    if not cloud_user_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(cloud_user_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    cloud_user_id = str(cloud_user_id_input).strip()
    if not cloud_user_id:
        sender.reply("🚫 目标云账号不能为空")
        return
    try:
        response = _autman_api_request(sender, "get", "/shelf", timeout=10)
        if not response:
            sender.reply("🚫 访问云端市场失败，请检查网络或插件权限")
            return
        data = response.json()
        if data.get("code") != 200:
            sender.reply(f"🚫 查询失败: {data.get('message', '未知错误')}")
            return
        all_plugins = data.get("data",[])
        if not all_plugins:
            sender.reply("❌ 云端市场没有任何插件")
            return
        coins_str = middleware.bucketGet("autMarketCoins", cloud_user_id) or "0"
        cloud_coins = int(coins_str) if coins_str.isdigit() else 0
        cloud_plugins_str = middleware.bucketGet("autMarketBoughts", cloud_user_id) or ""
        cloud_plugins_list =[p.strip() for p in cloud_plugins_str.split(',') if p.strip()]
        user_status = _get_user_status(cloud_user_id)
        reply_parts =[f"=====云端分发=====\n🗯️ 云端用户: {cloud_user_id}\n💰 云端云币: {cloud_coins}\n{user_status}\n------------------"]
        for i, plugin in enumerate(all_plugins, 1):
            title = plugin.get("title", "无标题插件")
            version = plugin.get("version", "未知")
            price = Decimal(str(plugin.get("price", 0))).quantize(Decimal("0.00"))
            status_icon = "✅" if title in cloud_plugins_list else "❌"
            price_str = "免费" if price <= 0 else f"售价{price}元"
            reply_parts.append(f"[{i}] {title} v{version}\n    {status_icon} {price_str}")
        reply_parts.append("------------------\n回复数字选择\n回复\"q\"退出\n==================")
        sender.reply("\n".join(reply_parts))
        choice_str = sender.input(60000, 0, False)
        if not choice_str:
            sender.reply("❌ 输入超时")
            return
        if str(choice_str).lower() == 'q':
            sender.reply("✅ 已退出操作")
            return
        try:
            selected_plugin = all_plugins[int(choice_str) - 1]
        except (ValueError, IndexError):
            sender.reply("❌ 无效的选择")
            return
        plugin_title = selected_plugin.get("title")
        plugin_path = selected_plugin.get("plugin_path")
        try:
            with open(plugin_path, 'r', encoding='utf-8') as f:
                plugin_content = f.read()
        except Exception as e:
            sender.reply(f"🚫 读取插件源文件失败: {e}")
            return
        from urllib.parse import quote
        plugin_language = selected_plugin.get("language", "python")
        admin_user = sender.bucketGet("cloud", "username") or "作者订阅源"
        payload = {
    "content": plugin_content,
    "key": cloud_user_id,
    "title": quote(plugin_title),
    "author": admin_user
}
        headers = { 'Content-Type': 'application/json' }
        
        local_dispatch_str = middleware.bucketGet("yuhua_sqzs", "local_dispatch")
        local_dispatch = str(local_dispatch_str).strip().lower() in ["true", "1", "on", "yes"]
        
        if local_dispatch:
            api_response = _autman_api_request(sender, "post", "/js/encrypt", headers=headers, json=payload, timeout=20)
        else:
            api_response = _make_request("post", "https://fandai.250666.xyz/api/encrypt_api.php", headers=headers, json=payload, timeout=20)
            
        if not api_response:
            sender.reply("🚫 插件分发失败，请检查网络或插件权限")
            return
        if api_response.status_code == 200:
            response_data = api_response.json()
            if response_data.get("code") == 200 and "data" in response_data:
                encrypted_content = response_data["data"]
                original_filename_base = os.path.basename(plugin_path)
                voucher = _build_distribution_voucher(cloud_user_id, plugin_language, admin_user, plugin_title, original_filename_base)
                if plugin_language == "es5":
                    target_bucket = "plugins"
                    target_key = f"{admin_user}:{plugin_title}"
                    target_name = f"{admin_user}:{plugin_title}.js"
                else:
                    target_bucket = "plugins_script"
                    target_key = f"{admin_user}:{original_filename_base}"
                    target_name = f"{admin_user}:{original_filename_base}"
                distribution_link = _create_distribution_link(voucher, target_bucket, target_name, encrypted_content)
                if not distribution_link:
                    sender.reply("🚫 插件分发失败，生成分发链接失败")
                    return
                sender.reply(f"分发凭证: {voucher}")
                sender.reply(f"分发链接: {distribution_link}")
                auto_usage_prompt = f"""=====自动导入教程=====
①请在5分钟内复制分发凭证与分发链接
②添加订阅源yuhualhh，安装『分发接收助手』插件，授予权限后发指令『分发接收』使用
❸若订阅源yuhualhh离线，请扫码添加分发Bot获取『分发接收助手』插件手动导入后使用
[CQ:image,file=https://gcore.jsdelivr.net/gh/lhz03/img@8fff3e65234512e046acfa76486fb62690f88c58/2026/05/07/7997b99ec4e6a8ae1d3ea95c9a137ea2.png]
=================="""
                manual_usage_prompt = f"""=====手动导入教程=====
❶请在5分钟内打开分发链接并复制全部分发数据
❷进入奥特曼后台-本地开发-数据管理，左侧搜索"{target_bucket}"并点击
❸右侧搜索"{target_key}"，若不存在记录，则点击"新增行”，在Key输入框填"{target_key}"，在Value输入框填操作❶复制的内容，点击保存并重启奥特曼。若存在记录，则替换Value输入框内容点击保存并重启奥特曼
❹重启后前往“应用市场-我的”找到插件并使用
=================="""
                sender.reply(auto_usage_prompt)
                sender.reply(manual_usage_prompt)
            else:
                sender.reply(f"🚫 插件分发失败，API返回逻辑错误: {response_data.get('message', '未知错误')}")
        else:
            sender.reply(f"🚫 插件分发失败，API返回错误: {api_response.status_code} - {api_response.text}")
    except Exception as e:
        sender.reply(f"🚫 插件分发时发生异常: {e}")
    return
  

def _collect_and_upload_cloud(sender, triggered_by='manual'):
    if not sender.isAdmin():
        return False, '您没有权限执行此操作'

    cloud_user = _get_cloud_username(sender)
    if not cloud_user:
        return False, '未配置云端账号'

    # ===== 采集数据 =====
    start_collect = time.time()

    try:
        response = _autman_api_request(sender, 'get', '/shelf', timeout=10)
        if not response or response.json().get('code') != 200:
            return False, '获取插件列表失败'
        all_plugins = response.json().get('data', [])
        public_plugins = [p for p in all_plugins if str(p.get('public')).lower() == 'true']
    except Exception as e:
        return False, f'采集异常: {str(e)[:120]}'

    plugin_count = len(public_plugins)
    collect_time = round(time.time() - start_collect, 2)

    # 获取公告/管理/机器信息
    ads_text = str(sender.bucketGet('autMarketCfgs', 'ads') or '').strip()
    admin_text = str(sender.bucketGet('autMarketCfgs', 'contact_admin') or '').strip()
    machine_text = str(sender.bucketGet('autMarketCfgs', 'contact_bot') or '').strip()

    # ===== 标准化插件数据 =====
    normalized_plugins = []
    for p in public_plugins:
        normalized_plugins.append({
            'title': str(p.get('title') or '').strip(),
            'language': str(p.get('language') or '').strip(),
            'version': str(p.get('version') or '').strip(),
            'price': float(p.get('price') or 0),
            'description': str(p.get('description') or '').strip(),
            'icon': str(p.get('icon') or '').strip(),
            'image_url': '',
            'plugin_path': str(p.get('plugin_path') or '').strip(),
            'cron': str(p.get('cron') or '').strip(),
            'public': bool(p.get('public')),
            'open_source': bool(p.get('open_source')),
            'platform': p.get('platform') if isinstance(p.get('platform'), list) else [],
            'params': p.get('params') if isinstance(p.get('params'), list) else [],
            'rules': p.get('rules') if isinstance(p.get('rules'), list) else [],
        })

    source = {
        'author': cloud_user,
        'name': cloud_user,
        'id': 0,
        'token': '',
        'disable': False,
        'default': False,
        'pinned': 0,
        'position': 0,
        'is_online': False,
        'plugin_total': plugin_count,
        'status_note': 'ok',
        'collect_complete': True,
        'admin_text': admin_text,
        'machine_text': machine_text,
        'announcement_text': ads_text,
        'ads_collected': True,
        'collected_at': int(time.time()),
        'plugins': normalized_plugins,
        'source_id': 0,
    }

    # ===== 上传到后端 =====
    start_upload = time.time()

    payload = {
        'node_id': _build_node_id(sender),
        'cloud_user_id': cloud_user,
        'collector_version': '1.0.0',
        'collected_at': int(time.time()),
        'meta': {
            'triggered_by': triggered_by,
            'source': 'cloud_market_assistant',
        },
        'sources': [source],
    }

    data, err = _backend_request('post', 'collect', payload=payload, timeout=REMOTE_TIMEOUT)
    upload_time = round(time.time() - start_upload, 2)

    upload_result = '成功' if not err else '失败'

    summary = (
        f"=====云端采集=====\n"
        f"🗯 云端账号: {cloud_user}\n"
        f"📦 采集数据: {plugin_count}\n"
        f"🕑 采集耗时: {collect_time}秒\n"
        f"💥 上传结果: {upload_result}\n"
        f"🕑 上传耗时: {upload_time}秒\n"
        f"=================="
    )

    if err:
        return False, summary
    return True, summary

def _handle_cloud_collect(sender):
    if not sender.isAdmin():
        sender.reply('🚫 您没有权限执行此操作')
        return
    sender.reply('⏳ 正在执行...')
    ok, msg = _collect_and_upload_cloud(sender, triggered_by='manual')
    sender.reply(msg if ok else f'❌ {msg}')

def handle_notification_settings(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    sender.reply("正在运行...")
    check_plugin_updates_and_notify(sender)
    sender.reply("✅ 云端监控执行完毕")     

def _format_plugin_details_for_push(plugin_data, old_plugin_data=None):
    title = plugin_data.get("title", "未知")
    language = plugin_data.get("language", "未知")
    if old_plugin_data:
        version_str = f"{old_plugin_data.get('version', 'N/A')} → {plugin_data.get('version', 'N/A')}"
    else:
        version_str = plugin_data.get("version", "未知")
    price = Decimal(str(plugin_data.get("price", "0"))).quantize(Decimal("0.00"))
    description = plugin_data.get("description", "")
    image_url = None
    img_match = re.search(r'<img src="([^"]+)">', description)
    if img_match:
        image_url = img_match.group(1)
        description = description.replace(img_match.group(0), "")
    description = description.replace("<br>", "\n")
    description = re.sub(r'<[^>]+>', '', description).strip()
    text_part = f"""名称：{title}
语言：{language}
版本：{version_str}
价格：{price}
描述：
{description}"""
    return text_part, image_url

def check_plugin_updates_and_notify(sender):
    data_bucket = "yuhua_sqzs"
    group_push = middleware.bucketGet(data_bucket, "group_push")
    group_ids_str = middleware.bucketGet(data_bucket, "group_id") or ""
    user_push = middleware.bucketGet(data_bucket, "user_push")

    group_push_enabled = str(group_push).strip().lower() in ["true", "1", "on", "yes"]
    user_push_enabled = str(user_push).strip().lower() in ["true", "1", "on", "yes"]

    if not group_push_enabled and not user_push_enabled:
        return

    try:
        response = _autman_api_request(sender, "get", "/shelf", timeout=10)
        if not response or response.json().get("code") != 200:
            return
        all_plugins = response.json().get("data", [])
        current_plugins = [p for p in all_plugins if str(p.get("public")).lower() == 'true']
    except Exception:
        return

    snapshot_key = "last_plugins_snapshot"
    previous_plugins_str = middleware.bucketGet(data_bucket, snapshot_key)
    if not previous_plugins_str:
        middleware.bucketSet(data_bucket, snapshot_key, json.dumps(current_plugins))
        return

    previous_plugins = json.loads(previous_plugins_str)
    previous_map = {p.get("title"): p for p in previous_plugins}
    current_map = {p.get("title"): p for p in current_plugins}
    changes = {"added": [], "updated": [], "removed": [], "downgraded": []}

    for title, plugin in current_map.items():
        if title not in previous_map:
            changes["added"].append(plugin)
        else:
            prev_plugin = previous_map[title]
            prev_version = prev_plugin.get("version", "0.0.0")
            curr_version = plugin.get("version", "0.0.0")
            comp = compare_versions(curr_version, prev_version)
            if comp > 0:
                changes["updated"].append((prev_plugin, plugin))
            elif comp < 0:
                changes["downgraded"].append((prev_plugin, plugin))

    for title in previous_map:
        if title not in current_map:
            changes["removed"].append(previous_map[title])

    has_changes = any(changes.values())

    def build_details(plugin_list, is_update=False):
        details = []
        for item in plugin_list:
            if is_update:
                prev_p, new_p = item
                text, img_url = _format_plugin_details_for_push(new_p, old_plugin_data=prev_p)
            else:
                text, img_url = _format_plugin_details_for_push(item)
            full_detail = text
            if img_url:
                full_detail += f"\n[CQ:image,file={img_url}]"
            details.append(full_detail)
        return "\n\n".join(details)

    if has_changes and group_push_enabled and group_ids_str:
        message_parts = []
        if changes["added"]:
            message_parts.append(f"✨ 插件上新:\n\n{build_details(changes['added'])}")
        if changes["updated"]:
            message_parts.append(f"🎉 插件更新:\n\n{build_details(changes['updated'], is_update=True)}")
        if changes["removed"]:
            message_parts.append(f"🔆 插件下架:\n\n{build_details(changes['removed'])}")
        if changes["downgraded"]:
            message_parts.append(f"💥 版本回退:\n\n{build_details(changes['downgraded'], is_update=True)}")
        final_message = "\n\n\n".join(message_parts)
        group_list = [gid.strip() for gid in group_ids_str.split(',') if gid.strip()]
        for group_id in group_list:
            _send_multi_platform_push_to_group(group_id, final_message)

    plugins_with_version_changes = changes["updated"] + changes["downgraded"]
    if plugins_with_version_changes and user_push_enabled:
        blacklist_str = middleware.bucketGet("autMarketCfgs", "blacklist") or ""
        blacklist = {uid.strip() for uid in blacklist_str.split(',') if uid.strip()}
        all_bought_data = middleware.bucketAll("autMarketBoughts")
        plugin_to_users_map = {}

        for cloud_user, plugins_str in all_bought_data.items():
            for plugin_title in plugins_str.split(','):
                plugin_title = plugin_title.strip()
                if plugin_title:
                    plugin_to_users_map.setdefault(plugin_title, []).append(cloud_user)

        cloud_to_local_map = {v: k for k, v in (middleware.bucketAll("yuhua_sqzs_user") or {}).items()}
        user_notifications = {}

        for prev_plugin, new_plugin in plugins_with_version_changes:
            plugin_title = new_plugin.get("title")
            if not plugin_title:
                continue
            change_type = "updated" if (prev_plugin, new_plugin) in changes["updated"] else "downgraded"
            authorized_users = plugin_to_users_map.get(plugin_title, [])
            for cloud_user in authorized_users:
                if cloud_user in blacklist:
                    continue
                local_user = cloud_to_local_map.get(cloud_user)
                if local_user:
                    user_notifications.setdefault(local_user, {})
                    user_notifications[local_user].setdefault(change_type, [])
                    user_notifications[local_user][change_type].append((prev_plugin, new_plugin))

        for local_user, changes_for_user in user_notifications.items():
            message_parts = []
            if "updated" in changes_for_user and changes_for_user["updated"]:
                message_parts.append(f"🎉 插件更新:\n\n{build_details(changes_for_user['updated'], is_update=True)}")
            if "downgraded" in changes_for_user and changes_for_user["downgraded"]:
                message_parts.append(f"💥 版本回退:\n\n{build_details(changes_for_user['downgraded'], is_update=True)}")
            if message_parts:
                final_user_message = "\n\n\n".join(message_parts)
                _send_multi_platform_push_to_user(local_user, final_user_message)

    if has_changes:
        middleware.bucketSet(data_bucket, snapshot_key, json.dumps(current_plugins))

    aut_login_data = middleware.bucketAll("autLogin")
    if aut_login_data:
        for key in list(aut_login_data.keys()):
            try:
                middleware.bucketDel("autLogin", key)
            except Exception:
                pass

def compare_versions(v1, v2):
    parts1 = list(map(int, v1.split('.')))
    parts2 = list(map(int, v2.split('.')))
    len1, len2 = len(parts1), len(parts2)
    for i in range(max(len1, len2)):
        p1 = parts1[i] if i < len1 else 0
        p2 = parts2[i] if i < len2 else 0
        if p1 > p2:
            return 1
        if p1 < p2:
            return -1
    return 0

def handle_check_updates(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    sender.reply("正在运行...")
    check_plugin_updates_and_notify(sender)
    sender.reply("✅ 云端监控执行完毕")

def handle_market_record(sender):
    if not sender.isAdmin():
        sender.reply("🚫 您没有权限执行此操作")
        return
    try:
        cloud_account = sender.bucketGet("cloud", "username") or "未知"
        response = _autman_api_request(sender, "post", "/market/record", timeout=15)
        if not response:
            sender.reply("🚫 备案请求失败，请检查网络或插件权限")
            return
        data = response.json()
        if data.get("code") == 200:
            message = data.get("message")
            if message is None:
                message = "操作成功（服务器未返回具体信息）"
            sender.reply(f"""=====云端备案=====
☁️ 云端账号: {cloud_account}
✨ 操作结果: {message}
==================""")
        else:
            message = data.get("message")
            if message is None:
                message = f"未知错误（状态码: {data.get('code', '未知')}）"
            sender.reply(f"""=====云端备案=====
☁️ 云端账号: {cloud_account}
✨ 操作结果: {message}
==================""")
    except Exception as e:
        sender.reply(f"🚫 执行备案时发生未知错误: {e}")
    return

def _perform_maintenance_check() -> bool:
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
    import os, base64, hashlib, json
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
    except Exception as e:
        pass
    return live_status


def handle_add_coins(sender): _handle_modify_coins(sender, "add")
def handle_subtract_coins(sender): _handle_modify_coins(sender, "subtract")
def handle_blacklist_add(sender): _handle_list_management(sender, "add", "blacklist")
def handle_blacklist_remove(sender): _handle_list_management(sender, "remove", "blacklist")
def handle_whitelist_add(sender): _handle_list_management(sender, "add", "whitelist")
def handle_whitelist_remove(sender): _handle_list_management(sender, "remove", "whitelist")

def handle_recharge_coins(sender):
    local_user_id = sender.getUserID()
    binding_bucket = "yuhua_sqzs_user"
    cloud_user_id = middleware.bucketGet(binding_bucket, local_user_id)
    
    # 1. 校验是否绑定云账号
    if not cloud_user_id:
        sender.reply("""=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 云端绑定 绑定账号
==================""")
        return

    # 2. 从数据桶获取静态收款码
    qrcode_url = middleware.bucketGet("autMarketCfgs", "qrcode")
    if not qrcode_url:
        sender.reply("💡 请联系管理员前往 插件市场-自建市场配置 配置收款码")
        return

    # 3. 询问充值金额
    sender.reply("""=====云端充币=====
请输入充值金额(元)
------------------
回复数字设置
回复"q"退出""")
    
    amount_input = sender.input(60000, 0, False)
    if not amount_input:
        sender.reply("❌ 输入超时")
        return
    if str(amount_input).lower() == 'q':
        sender.reply("✅ 已取消操作")
        return

    try:
        amount = round(float(str(amount_input).strip()), 2)
        if amount <= 0:
            raise ValueError
    except:
        sender.reply("❌ 充值金额输入无效")
        return

    # 提前计算云币数量 (按照 1元=100云币 的汇率换算并防止精度丢失)
    coins_to_add = int(round(amount * 100))

    # 4. 下发收款码并挂起等待支付，展示将获得的云币
    pay_msg = f"""=====扫码支付=====
🗯️ 云端用户: {cloud_user_id}
💰 充值金额: {amount}元
🎯 获得云币: {coins_to_add}
------------------
请在120秒内完成支付
回复"q"取消"""
    
    sender.reply(pay_msg)
    sender.replyImage(qrcode_url)

    try:
        payment_result = sender.waitPay("q", 120 * 1000)
    except Exception as e:
        error_str = str(e).lower()
        if "timeout" in error_str or "timed out" in error_str:
            sender.reply("❌ 支付超时")
        else:
            sender.reply(f"""=====支付异常=====
❌ 等待支付时发生错误
------------------
⚠️ 错误: {str(e)[:50]}
==================""")
        return

    # 5. 回调结果处理
    if not payment_result:
        sender.reply("❌ 支付超时")
        return
    if str(payment_result).lower() == 'q':
        sender.reply("✅ 已取消支付")
        return

    # 6. 金额严谨校验 (防一分钱白嫖)
    try:
        payment_data = json.loads(payment_result) if isinstance(payment_result, str) else payment_result
        # 兼容不同监控插件的大写 Money 或小写 money 字段
        raw_paid_money = payment_data.get('Money', payment_data.get('money', 0))
        paid_money = Decimal(f"{raw_paid_money:.2f}")
        
        if paid_money < Decimal(f"{amount:.2f}"):
            sender.reply(f"""=====支付失败=====
❌ 支付金额不足
💰 应付: {amount:.2f}元
💵 实付: {paid_money}元
==================""")
            return
    except Exception as e:
        sender.reply(f"""=====支付异常=====
❌ 支付验证失败
------------------
⚠️ 错误: {str(e)[:50]}
==================""")
        return

    # 7. 支付成功，结算云币
    bucket_name = "autMarketCoins"
    coins_str = middleware.bucketGet(bucket_name, cloud_user_id) or "0"
    current_coins = int(coins_str) if coins_str.isdigit() else 0
    new_coins = current_coins + coins_to_add
    
    # 写入数据桶
    middleware.bucketSet(bucket_name, cloud_user_id, str(new_coins))

    sender.reply(f"""=====充值成功=====
🗯️ 云端用户: {cloud_user_id}
💰 充值金额: {amount}元
➕ 获得云币: {coins_to_add}
💎 当前云币: {new_coins}
==================""")

def handle_cloud_coffee(sender):
    prompt_user = """=====云端咖啡=====
请输入目标云账号
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_user)
    user_id_input = sender.input(60000, 0, False)
    if not user_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(user_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    user = str(user_id_input).strip()
    if not user:
        sender.reply("🚫 目标云账号不能为空")
        return

    prompt_machine = """=====云端咖啡=====
请输入目标机器码
-----------------
请在60秒内完成
输入"q"退出"""
    sender.reply(prompt_machine)
    machine_id_input = sender.input(60000, 0, False)
    if not machine_id_input:
        sender.reply("❌ 输入超时")
        return
    if str(machine_id_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    machineid = str(machine_id_input).strip()
    if not machineid:
        sender.reply("🚫 目标机器码不能为空")
        return

    prompt_menu = f"""=====云端咖啡=====
🗯️ 目标账号: {user}
🔆 目标机码: {machineid}
🎨 温馨提示: 仅适用于奥特曼4.5.1及以下版本
------------------
[1] autMan本地版
    ✨ 十年授权
[2] autApp本地版
    ✨ 十年授权
[3] autMan+autApp本地版
    ✨ 十年授权
------------------
回复数字选择
回复"q"退出
=================="""
    sender.reply(prompt_menu)
    choice_input = sender.input(60000, 0, False)
    if not choice_input:
        sender.reply("❌ 输入超时")
        return
    if str(choice_input).lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    
    choice = str(choice_input).strip()
    if choice not in ['1', '2', '3']:
        sender.reply("❌ 无效的选择")
        return

    if choice in ['1', '3']:
        url_man = f"http://coffee.250666.xyz/plugin/coffee?user={user}&machineid={machineid}"
        res_man = _make_request("get", url_man, timeout=15)
        if res_man is not None:
            try:
                data_man = res_man.json()
                if data_man.get("code") == 200:
                    sender.reply(f"🎉autMan本地版授权码\n\n{data_man.get('data')}")
                else:
                    sender.reply(f"❌ 获取autMan授权码失败: {data_man.get('message', res_man.text)}")
            except Exception:
                sender.reply(f"❌ 获取autMan授权码失败: {res_man.text}")
        else:
            sender.reply("❌ 请求autMan授权码接口失败")

    if choice in ['2', '3']:
        url_app = f"http://coffee.250666.xyz/plugin/coffeeApp2920?user={user}&machineid={machineid}"
        res_app = _make_request("get", url_app, timeout=15)
        if res_app is not None:
            try:
                data_app = res_app.json()
                if data_app.get("code") == 200:
                    sender.reply(f"🎉autApp本地版授权码\n\n{data_app.get('data')}")
                else:
                    sender.reply(f"❌ 获取autApp授权码失败: {data_app.get('message', res_app.text)}")
            except Exception:
                sender.reply(f"❌ 获取autApp授权码失败: {res_app.text}")
        else:
            sender.reply("❌ 请求autApp授权码接口失败")
    return

def _upload_heartbeat(sender):
    cloud_user = _get_cloud_username(sender)
    if not cloud_user:
        return
    payload = {
        'node_id': _build_node_id(sender),
        'cloud_user_id': cloud_user,
        'heartbeat_at': int(time.time()),
    }
    try:
        url = f'{SUBHUB_BACKEND_URL}?action={quote("heartbeat")}'
        headers = {
            'X-API-Key': SUBHUB_BACKEND_KEY,
            'Content-Type': 'application/json',
        }
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        _make_request('post', url, headers=headers, data=body, timeout=15)
    except Exception:
        pass

def main():
    sender_id = middleware.getSenderID()
    sender = middleware.Sender(sender_id)
    msg = sender.getMessage().strip()
    imtype = sender.getImtype()
    if not check_maintenance_page():
        sender.reply("❌ 服务端无法连通, 插件停止运行")
        return
    if imtype == 'fake':
        _upload_heartbeat(sender)
        check_plugin_updates_and_notify(sender)
        cloud_collect_enabled = str(middleware.bucketGet('yuhua_sqzs', 'cloud_collect') or '').strip().lower() in ['true', '1', 'on', 'yes']
        if cloud_collect_enabled:
            ok, msg = _collect_and_upload_cloud(sender, triggered_by='fake')
            try:
                middleware.notifyMasters(msg if ok else f'❌ {msg}')
            except Exception:
                pass
        return
    if msg == "云端助手":
        sender.reply("""
        
请回复以下指令：
云端绑定
云端解绑
云端市场
云端查询
云端充币
云端加币
云端减币
云端查户
云端分发
云端授权
云端收权
云端加白
云端删白
云端加黑
云端删黑
云端备案
云端动态
云端采集""")    
        return    
    if msg == "云端绑定":
        handle_bind_account(sender)
        return
    elif msg == "云端解绑":
        handle_unbind_account(sender)
        return
    elif msg == "云端查询":
        handle_query_authorization(sender)
        return
    elif msg == "云端市场":
        _upload_heartbeat(sender)
        handle_market_query(sender)
        return
    elif msg == "云端授权":
        handle_grant_authorization(sender)
        return
    elif msg == "云端加黑":
        handle_blacklist_add(sender)
        return
    elif msg == "云端删黑":
        handle_blacklist_remove(sender)
        return
    elif msg == "云端加白":
        handle_whitelist_add(sender)
        return
    elif msg == "云端删白":
        handle_whitelist_remove(sender)
        return
    elif msg == "云端加币":
        handle_add_coins(sender)
        return
    elif msg == "云端减币":
        handle_subtract_coins(sender)
        return
    elif msg == "云端充币":
        handle_recharge_coins(sender)
        return
    elif msg == "云端收权":
        handle_revoke_authorization(sender)
        return
    elif msg == "云端分发":
        handle_admin_distribution(sender)
        return
    elif msg == "云端查户":
        handle_admin_query_user(sender)
        return
    elif msg == "云端动态":
        handle_notification_settings(sender)
        return
    elif msg == "云端监控":
        handle_check_updates(sender)
        return
    elif msg == "云端备案":
        handle_market_record(sender)
        return
    elif msg == "云端咖啡":
        handle_cloud_coffee(sender)
        return
    elif msg == "云端采集":
        _handle_cloud_collect(sender)
        return
if __name__ == "__main__":
    main()