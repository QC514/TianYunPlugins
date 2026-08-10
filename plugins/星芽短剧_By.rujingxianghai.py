# [title: 星芽短剧]
# [language: python]
# [class: 工具类]
# [service: 2993959969] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(星芽|xydj)(登录|登陆)$|^登(录|陆)(星芽|xydj)$|^(星芽|xydj)(查询|管理)$|^(查询|管理)(星芽|xydj)$|^星芽授权$|^星芽教程$|^星芽时长$|^星芽检测$|^星芽续期$]
# [cron: 0 0 0 0 0] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用平台
# [open_source: false]
# [icon: https://img-cf.885666.xyz/00ba8684fe6b55ef6cd1f255a50812d5.png]
# [version: 2.2]
# [public:true]
# [price: 12.88]
# [description: 星芽短剧现金毛，日0.5~1<br>指令：星芽登录、管理、查询、授权、教程<br>脚本及卡密进群获取<br>更新日志：<br>1.5：重构为vorto_utils规范，支持呆呆面板，支付配置统一到Vorto初始化<br>1.4：优化码支付二维码生成方式<br>1.3：检测逻辑改为提前天数提醒+到期自动清理，管理员授权改为按天数增减，完善定时任务]

import os
import json
import re
import time
import hashlib
import random
import string
import base64
import requests
import uuid
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import middleware
import vorto_utils
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_xydj_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_xydj', 'coin_key': 'dd_sign_points', 'name': '星芽'}

# API constants
ENCRYPT_KEY = "B@ecf920Od8A4df7"

# 线程锁（用于续期并发时线程安全的列表操作）
renew_lock = threading.Lock()

IP_CHECK_URLS = (
    'http://ip-api.com/json',
    'http://httpbin.org/ip',
    'https://api.ipify.org?format=json',
)

# [param: {"required":false,"key":"s_xydj.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_xydj.use_dumbpanel","bool":true,"placeholder":"","name":"使用DumbPanel","desc":"勾选使用DumbPanel面板，不勾选使用青龙面板"}]
# [param: {"required":true,"key":"s_xydj.osname","bool":false,"placeholder":"例:S_XYDJ","name":"青龙变量名","desc":"青龙容器内星芽的变量名"}]
# [param: {"required":true,"key":"s_xydj.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":false,"key":"s_xydj.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"s_xydj.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_xydj.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]
# [param: {"required":false,"key":"s_xydj.proxy_api","bool":false,"placeholder":"http://api.example.com/get_proxy","name":"代理API","desc":"星芽请求代理，支持代理API地址或直接代理地址(ip:port)，留空则直连"}]
# [param: {"required":false,"key":"s_xydj.renew_threads","bool":false,"placeholder":"3","name":"续期并发数","desc":"Token续期并发线程数，默认3"}]


def get_user_content():
    osname = middleware.bucketGet('s_xydj', 'osname') or 'S_XYDJ'
    qlname = middleware.bucketGet('s_xydj', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_xydj', 'Vipmoney') or '1')
    coin = int(middleware.bucketGet('s_xydj', 'coin') or '0')
    return osname, qlname, Vipmoney, coin


# ==================== Panel Client ====================

def _get_ql_client():
    """Get panel client, auto-switch between QingLong and DumbPanel"""
    osname = middleware.bucketGet('s_xydj', 'osname') or 'S_XYDJ'
    qlname = middleware.bucketGet('s_xydj', 'qlname') or ''
    use_dp = str(middleware.bucketGet('s_xydj', 'use_dumbpanel') or '').lower() == 'true'

    if use_dp:
        return vorto_utils.DumbPanelClient(osname, qlname) if qlname else vorto_utils.DumbPanelClient(osname)
    else:
        return vorto_utils.QingLongClient(osname, qlname) if qlname else vorto_utils.QingLongClient(osname)


def update_ql_env(account, account_info):
    """Update panel env variable"""
    token = account_info.get('token', '')
    device_id = account_info.get('device_id', '')
    if not token or not device_id:
        return False
    env_value = f"{token}#{device_id}"
    auth_time = middleware.bucketGet('s_xydj_auth', account) or '未授权'
    ql = _get_ql_client()
    return ql.update_env(account, env_value, f"星芽:{account}|到期:{auth_time}")


def delete_ql_env(account):
    """Delete panel env variable"""
    ql = _get_ql_client()
    return ql.delete_env(account)


# ==================== Crypto & Login Helpers ====================

def generate_random_base64(length=32):
    random_bytes = ''.join(random.choices(string.ascii_letters + string.digits, k=length)).encode()
    return base64.b64encode(random_bytes).decode()


def generate_signature(raw_str):
    try:
        return hashlib.md5(raw_str.encode(), usedforsecurity=True).hexdigest()
    except TypeError:
        return hashlib.md5(raw_str.encode()).hexdigest()


def generate_random_uuid():
    return str(uuid.uuid4())


def generate_random_device_id():
    return ''.join(random.choices('0123456789abcdef', k=32))


def encrypt_ecb_pkcs7(text, key=ENCRYPT_KEY):
    """ECB PKCS7 AES encryption"""
    try:
        key_bytes = key.encode('utf-8')
        if len(key_bytes) > 16:
            key_bytes = key_bytes[:16]
        elif len(key_bytes) < 16:
            key_bytes = key_bytes.ljust(16, b'\0')
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        padded_data = pad(text.encode('utf-8'), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        return None


# ==================== Proxy Helpers ====================

def _normalize_proxy_url(proxy_text):
    proxy_text = proxy_text.strip()
    if not proxy_text:
        return ''
    if '://' not in proxy_text:
        return f'http://{proxy_text}'
    return proxy_text


def _build_proxy_dict(proxy_text):
    proxy_url = _normalize_proxy_url(proxy_text)
    if not proxy_url:
        return None
    return {'http': proxy_url, 'https': proxy_url}


def _extract_proxy_text(response_text):
    content = response_text.strip()
    if not content:
        return ''
    for piece in re.split(r'[\r\n,|]+', content):
        candidate = piece.strip()
        if candidate:
            return candidate
    return ''


def fetch_proxy():
    proxy_source = (middleware.bucketGet('s_xydj', 'proxy_api') or '').strip()
    if not proxy_source:
        return None
    if '://' not in proxy_source and '/' not in proxy_source:
        return _build_proxy_dict(proxy_source)
    if re.match(r'^[a-zA-Z]+://[^/]+$', proxy_source):
        return _build_proxy_dict(proxy_source)
    try:
        response = requests.get(proxy_source, timeout=5, verify=False)
        response.raise_for_status()
    except Exception:
        return None
    proxy_text = _extract_proxy_text(response.text)
    if not proxy_text or '白名单' in proxy_text:
        return None
    return _build_proxy_dict(proxy_text)


def _test_proxy_alive(proxies):
    """验证代理是否可用，返回 True/False"""
    if not proxies:
        return True
    for check_url in IP_CHECK_URLS:
        try:
            resp = requests.get(check_url, proxies=proxies, timeout=8, verify=False)
            if resp.status_code == 200:
                return True
        except Exception:
            continue
    return False


def fetch_proxy_with_validation(max_attempts=3):
    """获取代理并验活，失败重试最多 max_attempts 次"""
    for _ in range(max_attempts):
        proxies = fetch_proxy()
        if not proxies:
            return None
        if _test_proxy_alive(proxies):
            return proxies
        time.sleep(0.5)
    return None


# ==================== XYDJ API ====================

def xydj_get_sign_info(token, device_id, proxies=None):
    """Get user sign info (cash balance, species/coins)"""
    headers = {
        "Host": "speciesweb.whjzjx.cn",
        "pragma": "no-cache",
        "cache-control": "no-cache",
        "authorization": token,
        "device_type": "PLQ110",
        "raw_channel": "default",
        "device_id": device_id,
        "device_platform": "android",
        "app_version": "3.9.4",
        "device_brand": "OnePlus",
        "os_version": "16",
        "user-agent": "Mozilla/5.0 (Linux; Android 16; PLQ110 Build/BP2A.250605.015; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/147.0.7727.137 Mobile Safari/537.36 _dsbridge",
        "origin": "https://h5static.xingya.com.cn",
        "x-requested-with": "com.jz.xydj",
    }
    try:
        api_url = f"https://speciesweb.whjzjx.cn/v1/sign/info?device_id={device_id}"
        response = requests.get(api_url, headers=headers, timeout=10, proxies=proxies)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == "ok" and "data" in result:
                return True, result["data"]
            elif result.get("code") == "1040401":
                return False, "Token已过期，需要重新登录"
            return False, result.get("msg", "获取失败")
        return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


def check_token_validity(username, account_info, proxies=None):
    """Check if account token is still valid"""
    token = account_info.get('token', '')
    device_id = account_info.get('device_id', '')
    if not token or not device_id:
        return False, "账号信息不完整"

    success, result = xydj_get_sign_info(token, device_id, proxies=proxies)
    if success:
        return True, "Token有效"
    return False, result


def add_viewing_duration(username, account_info, duration, proxies=None):
    """Add viewing duration for account"""
    token = account_info.get('token', '')
    device_id = account_info.get('device_id', '')
    user_id = account_info.get('user_id', '')

    if not token or not device_id:
        return False, "账号信息不完整，请重新登录"
    if not user_id:
        return False, "账号信息中缺少用户ID"

    headers = {
        "x-app-id": "7",
        "authorization": token,
        "platform": "1",
        "manufacturer": "OnePlus",
        "version_name": "3.9.4",
        "app_version": "3.9.4",
        "device_platform": "android",
        "device_type": "PLQ110",
        "device_brand": "OnePlus",
        "os_version": "16",
        "channel": "default",
        "raw_channel": "default",
        "uuid": f"randomUUID_{generate_random_uuid()}",
        "device_id": device_id,
        "content-type": "application/json; charset=utf-8"
    }

    current_timestamp = int(time.time() * 1000)
    request_body = [{
        "event_id": "action_episode_view",
        "page_id": "page_drama_detail",
        "eventType": "action",
        "event_type": "action",
        "timestamp": current_timestamp,
        "user_id": str(user_id),
        "login_status": True,
        "retry": 0,
        "device_id": device_id,
        "device_type": "OnePlus",
        "phone_version": "PLQ110",
        "os_type": 1,
        "os_name": "16",
        "version": "3.9.4",
        "package_name": "com.jz.xydj",
        "app_id": "7",
        "channel": "default",
        "raw_channel": "default",
        "font_scale": 1.0,
        "define_args": json.dumps({
            "page": "page_drama_detail",
            "theater_id": "4328",
            "theater_number": "1",
            "theater_duration": str(duration),
            "lock": "0",
            "complete": "0",
            "show_id": "7de1f4a3cfb04c93bb31c11f7e896ad8",
            "classification_id": "0",
            "position": "4",
            "entrance_scene": "0",
            "entrance": "5",
            "top_classification_id": "1",
            "top_classification_name": "剧场",
            "ab_id": "",
            "last_page": "page_drama_detail"
        })
    }]

    try:
        response = requests.post(
            "https://xingya-track.shytkjgs.com/receive",
            headers=headers, json=request_body, timeout=10, proxies=proxies
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == "ok":
                return True, f"成功增加 {duration} 秒观看时长"
            return False, f"增加时长失败: {result.get('msg', '未知错误')}"
        return False, f"请求失败，状态码: {response.status_code}"
    except Exception as e:
        return False, f"增加观看时长异常: {str(e)}"


# ==================== User Functions ====================

def bind_account():
    """Bind XYDJ account via SMS login"""
    sender.reply(
        "=====星芽登录=====\n"
        "请按照提示依次输入账号信息\n"
        "回复\"q\"随时退出操作\n"
        "=================="
    )

    sender.reply("请输入手机号（星芽登录账号）:")
    username = sender.input(120000, 1, False)
    if not username:
        sender.reply("⏰ 操作超时,已退出")
        return
    if username.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return

    if not username.isdigit() or len(username) != 11:
        sender.reply("=====格式错误=====\n❌ 手机号格式不正确\n请输入11位数字手机号\n==================")
        return

    proxies = fetch_proxy()
    random_uuid = generate_random_uuid()
    device_id = generate_random_device_id()
    current_timestamp = int(time.time())

    try:
        # Step 1: Get initial token for SMS
        jwt_header = {"alg": "HS256", "typ": "JWT"}
        jwt_payload = {
            "exp": current_timestamp + 86400,
            "UserId": 123413733,
            "register_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "is_mobile_bind": False,
            "d": device_id
        }

        request_body = {
            "device": device_id,
            "install_first_open": False,
            "first_install_time": current_timestamp * 1000,
            "last_update_time": current_timestamp * 1000,
            "report_link_url": "",
            "authorization": json.dumps(jwt_header) + json.dumps(jwt_payload),
            "timestamp": current_timestamp * 1000
        }

        encrypted_body = encrypt_ecb_pkcs7(json.dumps(request_body))

        headers = {
            "Host": "u.shytkjgs.com",
            "x-app-id": "7",
            "platform": "1",
            "manufacturer": "OnePlus",
            "version_name": "3.9.4",
            "app_version": "3.9.4",
            "device_platform": "android",
            "device_type": "PLQ110",
            "device_brand": "OnePlus",
            "os_version": "16",
            "uuid": f"randomUUID_{random_uuid}",
            "device_id": device_id,
            "content-type": "application/json; charset=utf-8",
            "user-agent": "okhttp/4.10.0"
        }

        response = requests.post(
            "https://u.shytkjgs.com/user/v3/account/login",
            headers=headers, data=encrypted_body, timeout=10, proxies=proxies
        )

        result = {}
        if response.status_code == 200:
            try:
                result = response.json()
            except:
                result = {"code": "error", "msg": "解析响应失败"}
        else:
            result = {"code": "error", "msg": f"请求失败，状态码: {response.status_code}"}

        if result.get("code") != "ok" or "data" not in result:
            sender.reply(f"=====获取验证码失败=====\n❌ 错误: {result.get('msg', '未知错误')}\n请手动发送验证码并输入\n==================")
            token = ""
        else:
            token = result["data"].get("token", "")

            # Send SMS
            try:
                sms_headers = {
                    "Host": "u.shytkjgs.com",
                    "x-app-id": "7",
                    "authorization": token,
                    "platform": "1",
                    "device_id": device_id,
                    "content-type": "application/json; charset=UTF-8",
                    "user-agent": "okhttp/4.10.0"
                }
                sms_response = requests.post(
                    "https://u.shytkjgs.com/user/v1/sms/code",
                    headers=sms_headers, json={"mobile": username}, timeout=10, proxies=proxies
                )
                if sms_response.status_code == 200 and sms_response.json().get("code") == "ok":
                    sender.reply("=====验证码已发送=====\n已向您的手机发送验证码\n==================")
                else:
                    sender.reply("=====发送验证码失败=====\n请手动获取验证码\n==================")
            except:
                sender.reply("=====发送验证码失败=====\n请手动获取验证码\n==================")

        # Step 2: Input verification code with retry
        max_retries = 3
        retry_count = 0
        final_token = None
        user_id = None

        while retry_count < max_retries:
            if retry_count > 0:
                sender.reply(
                    f"=====验证码错误=====\n❌ 验证码错误或已过期\n"
                    f"剩余重试次数: {max_retries - retry_count}\n"
                    f"请重新输入验证码\n回复\"q\"退出操作\n=================="
                )

            sender.reply("请输入收到的短信验证码:")
            code = sender.input(120000, 1, False)
            if not code:
                sender.reply("⏰ 操作超时,已退出")
                return
            if code.lower() == 'q':
                sender.reply("✅ 已取消登录")
                return

            if not code.isdigit():
                sender.reply("=====格式错误=====\n❌ 验证码格式不正确\n请输入数字验证码\n==================")
                retry_count += 1
                continue

            # Verify SMS code
            login_headers = {
                "Host": "u.shytkjgs.com",
                "x-app-id": "7",
                "authorization": token,
                "platform": "1",
                "manufacturer": "OnePlus",
                "version_name": "3.9.4",
                "device_type": "PLQ110",
                "device_id": device_id,
                "content-type": "application/x-www-form-urlencoded",
                "user-agent": "okhttp/4.10.0"
            }

            login_response = requests.post(
                "https://u.shytkjgs.com/user/v1/account/sms/login",
                headers=login_headers,
                data=f"mobile={username}&code={code}",
                timeout=10, proxies=proxies
            )

            login_result = {}
            if login_response.status_code == 200:
                try:
                    login_result = login_response.json()
                except:
                    login_result = {"code": "error", "msg": "解析登录响应失败"}
            else:
                login_result = {"code": "error", "msg": f"登录请求失败，状态码: {login_response.status_code}"}

            if login_result.get("code") != "ok" or "data" not in login_result:
                retry_count += 1
                if retry_count >= max_retries:
                    sender.reply(
                        f"=====验证失败=====\n❌ 错误: {login_result.get('msg', '验证码错误或已过期')}\n"
                        f"❌ 已达到最大重试次数\n=================="
                    )
                    return
                continue

            user_data = login_result.get("data", {})
            user_id = user_data.get("user_id", "")
            final_token = user_data.get("token", "")

            if not user_id or not final_token:
                sender.reply("=====登录异常=====\n❌ 错误: 未获取到用户信息\n==================")
                return
            break

        if not final_token:
            return

        # Step 3: Input remark
        sender.reply("请输入备注名称（用于区分不同账号）:")
        remark = sender.input(120000, 1, False)
        if not remark:
            sender.reply("⏰ 操作超时,已退出")
            return
        if remark.lower() == 'q':
            sender.reply("✅ 已取消登录")
            return

        # Save account
        if not uservalue:
            middleware.bucketSet('s_xydj_user', userid, str([username]))
        else:
            accounts = eval(uservalue)
            if username not in accounts:
                accounts.append(username)
                middleware.bucketSet('s_xydj_user', userid, str(accounts))

        account_info = {
            "username": username,
            "token": final_token,
            "device_id": device_id,
            "remark": remark,
            "user_id": user_id
        }
        middleware.bucketSet('s_xydj_token', username, json.dumps(account_info))

        sender.reply(
            f"=====绑定成功=====\n"
            f"👤 备注: {remark}\n"
            f"📱 手机号: {vorto_utils.mask_account(username)}\n"
            f"=================="
        )

        # Check auth status
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_xydj_auth', username)

        if accountVip and accountVip > dqsj:
            sender.reply(f"=====账号已授权=====\n📅 到期时间: {accountVip}\n正在更新账号信息...\n==================")
            if update_ql_env(username, account_info):
                sender.reply("✅ 账号信息更新成功")
            else:
                sender.reply("❌ 账号信息更新失败")
        else:
            sender.reply("=====账号未授权=====\n❌ 当前账号未授权或已过期\n即将进入授权流程...\n==================")
            authorize_multiple_accounts([username])

    except Exception as e:
        sender.reply(f"=====绑定异常=====\n❌ 错误: {str(e)}\n请重试或联系管理员\n==================")


def query_accounts():
    """Query account info"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 星芽登录 绑定\n==================")
        return

    accounts = eval(uservalue)
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        try:
            account_info = json.loads(middleware.bucketGet('s_xydj_token', username))
            remark = account_info.get('remark', username)
        except:
            remark = username
        auth_time = middleware.bucketGet('s_xydj_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{vorto_utils.mask_account(username)}({remark}, {auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    try:
        if choice == '0':
            selected = accounts.copy()
        else:
            selected = [
                accounts[int(idx.strip()) - 1]
                for idx in choice.split(',')
                if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
            ]

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        sender.reply(f"✅ 已选择 {len(selected)} 个账号，正在查询...")
        proxies = fetch_proxy()

        for i, username in enumerate(selected, 1):
            try:
                account_info = json.loads(middleware.bucketGet('s_xydj_token', username))
                token = account_info.get('token', '')
                device_id = account_info.get('device_id', '')
                remark = account_info.get('remark', username)

                auth_time = middleware.bucketGet('s_xydj_auth', username)
                auth_status = '已授权' if auth_time and auth_time >= str(datetime.now().date()) else '未授权'

                cash_remain = "未知"
                species = "未知"

                if token and device_id:
                    success, data = xydj_get_sign_info(token, device_id, proxies=proxies)
                    if success:
                        cash_remain = data.get("cash_remain", "未知")
                        species = data.get("species", "未知")

                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 手机号: {vorto_utils.mask_account(username)}\n"
                    f"👤 备注: {remark}\n"
                    f"🔐 授权状态: {auth_status}\n"
                    f"💰 现金余额: {cash_remain}元\n"
                    f"🪙 金币数量: {species}\n"
                    f"=================="
                )

                if i < len(selected) and len(selected) > 3:
                    time.sleep(0.5)

            except Exception as e:
                sender.reply(f"=====查询失败[{i}/{len(selected)}]=====\n📱 手机号: {vorto_utils.mask_account(username)}\n❌ 错误: {str(e)}\n==================")

        sender.reply("✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


def manage_account():
    """Account management"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

    accounts = eval(uservalue)
    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交青龙\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    # Build account selection list
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        try:
            account_info = json.loads(middleware.bucketGet('s_xydj_token', username))
            remark = account_info.get('remark', username)
        except:
            remark = username
        auth_time = middleware.bucketGet('s_xydj_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{vorto_utils.mask_account(username)}({remark}, {auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    if account_choice == '0':
        selected = accounts.copy()
    else:
        selected = [
            accounts[int(idx.strip()) - 1]
            for idx in account_choice.split(',')
            if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
        ]

    if not selected:
        sender.reply("❌ 未选择有效账号")
        return

    sender.reply(f"✅ 已选择 {len(selected)} 个账号")

    if choice == '1':
        authorize_multiple_accounts(selected)
    elif choice == '2':
        sender.reply("=====确认删除=====\n⚠️ 此操作不可恢复\n回复 y 确认删除\n==================")
        confirm = sender.input(120000, 1, False)
        if confirm and confirm.lower() == 'y':
            for username in selected:
                if username in accounts:
                    accounts.remove(username)
                middleware.bucketDel('s_xydj_token', username)
                middleware.bucketDel('s_xydj_auth', username)
                delete_ql_env(username)

            if accounts:
                middleware.bucketSet('s_xydj_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_xydj_user', userid)
            sender.reply(f"✅ 已删除 {len(selected)} 个账号")
        else:
            sender.reply("✅ 已取消")
    elif choice == '3':
        success = 0
        for username in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_xydj_token', username))
                auth_time = middleware.bucketGet('s_xydj_auth', username)
                if auth_time and auth_time >= str(datetime.now().date()):
                    if update_ql_env(username, account_info):
                        success += 1
            except:
                pass
        sender.reply(
            f"=====提交结果=====\n"
            f"✅ 成功: {success}个\n"
            f"❌ 失败: {len(selected) - success}个\n"
            f"💡 提示: 未授权账号无法提交\n"
            f"=================="
        )
    else:
        sender.reply("❌ 无效的选择")


# ==================== Payment & Authorization ====================

def authorize_multiple_accounts(usernames):
    """Authorize multiple accounts"""
    account_infos = []
    for username in usernames:
        try:
            account_infos.append({
                'username': username,
                'info': json.loads(middleware.bucketGet('s_xydj_token', username))
            })
        except:
            pass

    if not account_infos:
        sender.reply("❌ 没有有效账号")
        return

    sender.reply(
        f"✅ {len(account_infos)} 个有效账号\n"
        f"=====设置授权时长=====\n"
        f"请输入授权月数(如:1)\n"
        f"回复\"q\"退出\n"
        f"=================="
    )
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return

        Vipmoney = float(middleware.bucketGet('s_xydj', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_xydj', 'coin') or '0')

        # Build available payment methods via vorto_utils
        pay_config = vorto_utils.get_pay_config()
        pay_types = pay_config.get('pay_types', {})

        available = []
        if pay_config.get('qr_pay_switch'):
            available.append(("扫码支付", "qrcode"))
        if pay_config.get('ma_pay_switch'):
            if not pay_types:
                sender.reply("⚠️ 未配置码支付方式，请联系管理员在Vorto初始化中填写")
            else:
                for pay_key, pay_name in pay_types.items():
                    available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))

        if coin > 0:
            available.append(("积分兑换", "coin"))

        if not available:
            sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
            return

        # Select payment method
        if len(available) == 1:
            payment_name, payment_type = available[0]
        else:
            menu = (
                f"=====选择支付方式=====\n"
                f"📊 账号: {len(account_infos)}个\n"
                f"⏰ 时长: {months}月\n"
                f"💰 金额: {total_money}元\n"
                f"------------------------"
            )
            for i, (name, _) in enumerate(available, 1):
                menu += f"\n[{i}] {name}"
            menu += "\n------------------------\n回复数字选择\n=================="
            sender.reply(menu)

            pay_choice = sender.input(120000, 1, False)
            if not pay_choice or pay_choice.lower() == 'q':
                sender.reply("✅ 已取消")
                return

            pay_idx = int(pay_choice) - 1
            if 0 <= pay_idx < len(available):
                payment_name, payment_type = available[pay_idx]
            else:
                sender.reply("❌ 无效选择")
                return

        # Execute payment
        if payment_type == 'coin':
            for acc in account_infos:
                _process_coin_payment(acc['username'], acc['info'], months, coin)
        elif payment_type.startswith('mapay_'):
            if _handle_mapay_order(PLUGIN_CONFIG['name'], months, total_money, payment_type.replace('mapay_', '')):
                for acc in account_infos:
                    _process_auth(acc['username'], acc['info'], months)
        elif payment_type == 'qrcode':
            if _handle_qrcode_payment(PLUGIN_CONFIG['name'], months, total_money):
                for acc in account_infos:
                    _process_auth(acc['username'], acc['info'], months)
    except ValueError:
        sender.reply("❌ 请输入有效数字")


def _process_auth(username, account_info, months):
    """Wrapper for vorto_utils authorization"""
    return vorto_utils.process_authorization(
        sender, 's_xydj_auth', username, account_info, months,
        update_ql_callback=update_ql_env
    )


def _process_coin_payment(username, account_info, months, coin):
    """Wrapper for vorto_utils coin payment"""
    return vorto_utils.process_coin_payment(
        sender, userid, 's_xydj_auth', username, account_info,
        months=months, coin_per_month=coin,
        auth_callback=lambda acc, info, m: vorto_utils.process_authorization(
            sender, 's_xydj_auth', acc, info, m, update_ql_callback=update_ql_env
        )
    )


def _handle_qrcode_payment(project, months, money):
    """QR code payment via vorto_utils config"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config.get('zsm', '')
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员在Vorto初始化中配置')
        return False

    sender.reply(
        f"======扫码支付======\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)

    ddzf = sender.waitPay("q", 300000)
    if str(ddzf) == 'q':
        sender.reply('✅ 已取消')
        return False

    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
        if float(ddzf.get('Money') or ddzf.get('money', 0)) >= float(money):
            return True
        sender.reply("❌ 支付金额不足")
        return False
    except:
        sender.reply("❌ 支付验证失败")
        return False


def _handle_mapay_order(project, months, money, pay_type='alipay'):
    """MaPay order via vorto_utils"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config.get('ma_pay_switch'):
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        amount = round(float(money), 2)
        out_trade_no = f"XYDJ{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config.get('pay_types', {}).get(pay_type, '支付宝')

        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {amount}元\n"
            f"💳 方式: {pay_type_name}\n"
            f"=================="
        )

        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(amount, pay_type, out_trade_no, f"{project}-{amount}", userid)

        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False

        pay_url = order.get('pay_url')
        qr_url = vorto_utils.generate_qrcode_url(pay_url)
        sender.replyImage(qr_url)
        sender.reply(f'💳 请使用【{pay_type_name}】扫码支付\n⏰ 5分钟内完成支付\n输入"q"可取消')

        start_time = time.time()
        timeout = 300

        while time.time() - start_time < timeout:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                sender.reply("✅ 支付成功！")
                return True

        sender.reply("❌ 支付超时")
        return False

    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False


# ==================== Admin Functions ====================

def ks_auth():
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理员授权")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(
            sender, 's_xydj_user', 's_xydj_auth', 's_xydj_token',
            update_ql_callback=update_ql_env
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender, 's_xydj_user', 's_xydj_auth', 's_xydj_token',
            update_ql_callback=update_ql_env
        )
    else:
        sender.reply("❌ 无效的选择")


# ==================== View Duration ====================

def add_view_duration():
    """Handle add viewing duration feature"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 星芽登录 绑定\n==================")
        return

    accounts = eval(uservalue)
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        try:
            account_info = json.loads(middleware.bucketGet('s_xydj_token', username))
            remark = account_info.get('remark', username)
        except:
            remark = username
        auth_time = middleware.bucketGet('s_xydj_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{vorto_utils.mask_account(username)}({remark}, {auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    sender.reply(
        "=====设置观看时长=====\n"
        "请输入需要增加的观看时长(秒)\n"
        "例如: 3600 (代表1小时)\n"
        "回复\"q\"退出\n"
        "=================="
    )
    duration_input = sender.input(120000, 1, False)
    if not duration_input or duration_input.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    try:
        duration = int(duration_input)
        if duration <= 0:
            sender.reply("❌ 时长必须大于0")
            return

        if choice == '0':
            selected = accounts.copy()
        else:
            selected = [
                accounts[int(idx.strip()) - 1]
                for idx in choice.split(',')
                if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
            ]

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        sender.reply(f"✅ 已选择 {len(selected)} 个账号，准备增加观看时长...")
        proxies = fetch_proxy()

        success_count = 0
        for username in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_xydj_token', username))
                auth_time = middleware.bucketGet('s_xydj_auth', username)
                if not auth_time or auth_time < str(datetime.now().date()):
                    sender.reply(f"=====增加失败=====\n📱 手机号: {vorto_utils.mask_account(username)}\n❌ 状态: 账号未授权或已过期\n==================")
                    continue

                success, message = add_viewing_duration(username, account_info, duration, proxies=proxies)
                if success:
                    sender.reply(f"=====增加成功=====\n📱 手机号: {vorto_utils.mask_account(username)}\n✅ 状态: {message}\n==================")
                    success_count += 1
                else:
                    sender.reply(f"=====增加失败=====\n📱 手机号: {vorto_utils.mask_account(username)}\n❌ 错误: {message}\n==================")
            except Exception as e:
                sender.reply(f"=====增加异常=====\n📱 手机号: {vorto_utils.mask_account(username)}\n❌ 错误: {str(e)}\n==================")

        sender.reply(
            f"=====操作完成=====\n"
            f"📊 总账号: {len(selected)}个\n"
            f"✅ 成功: {success_count}个\n"
            f"❌ 失败: {len(selected) - success_count}个\n"
            f"⏱️ 增加时长: {duration}秒\n"
            f"=================="
        )
    except ValueError:
        sender.reply("❌ 请输入有效的数字")


# ==================== Token Renewal ====================

def _renew_single_token(username, account_info, auth_time, success_list, fail_list):
    """单个账号的Token续期（带独立代理 + 重试）"""
    token = account_info.get('token', '')
    device_id = account_info.get('device_id', '')
    if not token or not device_id:
        with renew_lock:
            fail_list.append(f"{vorto_utils.mask_account(username)} 账号信息不完整")
        return

    max_retries = 3
    last_error = ""

    for attempt in range(max_retries):
        proxies = fetch_proxy_with_validation()

        try:
            now_ms = int(time.time() * 1000)
            login_data = {
                "device": device_id,
                "package_name": "com.jz.xydj",
                "android_id": uuid.uuid4().hex[:16],
                "install_first_open": False,
                "first_install_time": now_ms - 86400000 * 30,
                "last_update_time": now_ms - 86400000 * 30,
                "report_link_url": "",
                "authorization": token,
                "timestamp": now_ms,
            }

            plaintext = json.dumps(login_data, ensure_ascii=False, separators=(",", ":"))
            encrypted_body = encrypt_ecb_pkcs7(plaintext)
            if not encrypted_body:
                with renew_lock:
                    fail_list.append(f"{vorto_utils.mask_account(username)} 加密失败")
                return

            headers = {
                "x-app-id": "7",
                "platform": "1",
                "manufacturer": "OnePlus",
                "version_name": "3.9.4",
                "app_version": "3.9.4",
                "device_platform": "android",
                "device_type": "PLQ110",
                "device_brand": "OnePlus",
                "os_version": "16",
                "channel": "default",
                "raw_channel": "default",
                "uuid": f"randomUUID_{generate_random_uuid()}",
                "device_id": device_id,
                "content-type": "application/json; charset=utf-8",
                "user-agent": "okhttp/4.10.0",
            }

            response = requests.post(
                "https://u.shytkjgs.com/user/v3/account/login",
                headers=headers,
                data=encrypted_body,
                timeout=10,
                proxies=proxies,
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "ok" and result.get("data", {}).get("token"):
                    new_token = result["data"]["token"]
                    account_info["token"] = new_token
                    if result["data"].get("user_id"):
                        account_info["user_id"] = result["data"]["user_id"]
                    middleware.bucketSet('s_xydj_token', username, json.dumps(account_info))
                    update_ql_env(username, account_info)
                    remark = account_info.get('remark', username)
                    with renew_lock:
                        success_list.append(f"{vorto_utils.mask_account(username)}({remark}) → {auth_time}")
                    return
                else:
                    last_error = result.get('msg', '未知错误')
                    break
            else:
                last_error = f"HTTP {response.status_code}"
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                break

        except (requests.exceptions.ProxyError,
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout) as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
        except Exception as e:
            last_error = str(e)
            break

    with renew_lock:
        fail_list.append(f"{vorto_utils.mask_account(username)} {last_error}")


def renew_all_tokens():
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return

    renew_threads = int(middleware.bucketGet('s_xydj', 'renew_threads') or '3')
    if renew_threads < 1:
        renew_threads = 1

    sender.reply(f"🔄 正在续期所有已授权账号的Token（并发: {renew_threads}）...")

    all_users = middleware.bucketAllKeys('s_xydj_user')
    if not all_users:
        sender.reply("❌ 没有用户数据")
        return

    current_date = str(datetime.now().date())
    success_list = []
    fail_list = []
    skip_count = 0
    tasks = []

    for uid in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_xydj_user', uid) or '[]')
            for username in accounts:
                auth_time = middleware.bucketGet('s_xydj_auth', username)
                if not auth_time or auth_time < current_date:
                    skip_count += 1
                    continue
                try:
                    account_info = json.loads(middleware.bucketGet('s_xydj_token', username) or '{}')
                    tasks.append((username, account_info, auth_time))
                except:
                    fail_list.append(f"{vorto_utils.mask_account(username)} 账号数据解析失败")
        except:
            pass

    if not tasks:
        sender.reply(f"⏭️ 没有需要续期的账号（跳过: {skip_count}个未授权/已过期）")
        return

    with ThreadPoolExecutor(max_workers=renew_threads) as executor:
        futures = []
        for username, account_info, auth_time in tasks:
            future = executor.submit(
                _renew_single_token, username, account_info, auth_time, success_list, fail_list
            )
            futures.append(future)
        for future in as_completed(futures):
            future.result()


    result_msg = "=====Token续期完成=====\n"
    result_msg += f"✅ 成功: {len(success_list)}个\n"
    if fail_list:
        result_msg += f"❌ 失败: {len(fail_list)}个\n"
    if skip_count:
        result_msg += f"⏭️ 跳过(未授权/已过期): {skip_count}个\n"
    result_msg += "=================="
    sender.reply(result_msg)


# ==================== Auth Check (custom with token validity) ====================

def check_auth_status():
    """Check auth status with token validity - custom version because we also check token validity"""
    notify = middleware.bucketGet('s_xydj', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"

    channels = [c.strip() for c in notify.split(',') if c.strip()]
    proxies = fetch_proxy()
    all_users = middleware.bucketAllKeys('s_xydj_user')
    if not all_users:
        return "❌ 没有用户"

    notify_days = int(middleware.bucketGet('s_xydj', 'notify_days') or '3')
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0

    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_xydj_user', user_id) or '[]')
            if not accounts:
                continue

            to_notify = []
            to_clean = []
            invalid_tokens = []

            for acc in accounts:
                total += 1

                remark = acc
                try:
                    account_info = json.loads(middleware.bucketGet('s_xydj_token', acc) or '{}')
                    if account_info:
                        remark = account_info.get('remark', acc)
                        is_valid, message = check_token_validity(acc, account_info, proxies=proxies)
                        if not is_valid:
                            invalid_tokens.append({'phone': acc, 'remark': remark, 'reason': message})
                except Exception as e:
                    invalid_tokens.append({'phone': acc, 'remark': remark, 'reason': f"检测异常: {str(e)}"})

                auth_time_str = middleware.bucketGet('s_xydj_auth', acc)
                if not auth_time_str:
                    to_clean.append({'phone': acc, 'remark': remark, 'auth_time': '未授权', 'days_left': 0})
                    continue

                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days

                    if days_left <= 0:
                        to_clean.append({'phone': acc, 'remark': remark, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        to_notify.append({'phone': acc, 'remark': remark, 'auth_time': auth_time_str, 'days_left': days_left})
                except:
                    to_clean.append({'phone': acc, 'remark': remark, 'auth_time': auth_time_str, 'days_left': 0})

            # Clean expired accounts
            if to_clean:
                for exp_acc in to_clean:
                    username = exp_acc['phone']
                    delete_ql_env(username)
                    middleware.bucketDel('s_xydj_token', username)
                    if username in accounts:
                        accounts.remove(username)
                    middleware.bucketDel('s_xydj_auth', username)
                    cleaned += 1

                if accounts:
                    middleware.bucketSet('s_xydj_user', user_id, str(accounts))
                else:
                    middleware.bucketDel('s_xydj_user', user_id)

            # Send notifications
            if to_notify or invalid_tokens:
                notify_msg = "=====星芽账号检测====="

                if to_notify:
                    notify_list = "\n".join([
                        f"📱 {vorto_utils.mask_account(a['phone'])}({a['remark']}) 剩余{a['days_left']}天({a['auth_time']})"
                        for a in to_notify
                    ])
                    notify_msg += f"\n⚠️ 即将过期:\n{notify_list}"

                if invalid_tokens:
                    invalid_list = "\n".join([
                        f"📱 {vorto_utils.mask_account(a['phone'])}({a['remark']}) {a['reason']}"
                        for a in invalid_tokens
                    ])
                    notify_msg += f"\n\n🔑 Token失效:\n{invalid_list}"

                notify_msg += "\n💡 发送\"星芽管理\"续费"
                notify_msg += "\n💡 发送\"星芽登录\"重新登录"
                notify_msg += "\n=================="

                for ch in channels:
                    try:
                        middleware.push(imType=ch, groupCode='', userID=user_id, title="", content=notify_msg)
                        notified += 1
                    except:
                        pass
        except:
            pass

    return f"✅ 星芽短剧检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"


# ==================== Tutorial ====================

def show_tutorial():
    tutorial = """
=====星芽使用教程=====
1. 基本功能:
  • 星芽登录: 绑定星芽账号
  • 星芽查询: 查询账号信息和积分
  • 星芽管理: 管理账号(授权/删除/提交青龙)
  • 星芽授权: 管理员专用授权功能
  • 星芽时长: 增加观看时长

2. 使用须知:
  • 账号需要先授权才能提交青龙
  • 支持扫码支付、码支付和积分兑换
  • 授权后可自动同步至青龙/DumbPanel

3. 如有问题请联系管理员
=================="""
    sender.reply(tutorial.strip())


# ==================== Main Entry ====================

def main():
    msg = sender.getMessage()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('星芽' in msg or 'xydj' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('星芽' in msg or 'xydj' in msg.lower()):
        manage_account()
    elif '星芽授权' in msg:
        ks_auth()
    elif '星芽教程' in msg:
        show_tutorial()
    elif '星芽时长' in msg:
        add_view_duration()
    elif '星芽续期' in msg:
        renew_all_tokens()
    elif '星芽检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测所有账号状态...")
        sender.reply(check_auth_status())
    elif sender.getImtype() == 'fake':
        try:
            middleware.notifyMasters(check_auth_status())
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
