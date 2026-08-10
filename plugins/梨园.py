# [title: 梨园]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: 1603960061]
# [rule: ^(梨园|ly)(扫码|登录|登陆|查询|任务)$]
# [cron: 30 7 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://pp.myapp.com/ma_icon/0/icon_54559488_1733299697/256]
# [version: 1.2.2]
# [public: true]
# [admin: false]
# [disable: false]
# [description: 梨园行戏曲-金币任务自动化<br>功能：扫码登录、自动做任务、自动提现<br>指令：梨园扫码、梨园查询、梨园任务]
# [param: {"required":false,"key":"G_LYHXQ.proxy_api","name":"代理API","placeholder":"http://example.com/getip","desc":"代理API地址，留空直连"}]

import json
import re
import time
import uuid
import hashlib
import base64
from datetime import datetime
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

import middleware

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== 配置 ====================
BUCKET_USER = "G_LYHXQ_user"
BUCKET_TOKEN = "G_LYHXQ_token"
BUCKET_CONFIG = "G_LYHXQ"

APPID_APP = "wxe2e7e595988751cc"
APP_BUNDLEID = "uni.UNIA317E51"
FLY_BASE = "https://fly.daoran.tv"
AOP_BASE = "http://wechat.daoran.tv"
FLY_MD5 = "SkvyrWqK9QHTdCT12Rhxunjx+WwMTe9y4KwgeASFDhbYabRSPskR0Q=="
AOP_MD5 = "GYWmhK2MfuQtDc9Cj8Fbw9hGoJwQ+f3Wbn0R6KhfUJmoy+8Nz7xP1A=="
SIGN_AES_KEY = b"E5Up6N2RkuWyJc5@"
SIGN_AES_IV = b"z8eFg_b_CSG9~kU9"
APP_SHA1 = "2B8FA3EE98CA3F7270CC599DAB07CF413DE74ABF"
WX_UA = "Mozilla/5.0 (Linux; Android 14; Build/TP1A.220905.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 MicroMessenger/8.0.57.2820 WeChat/arm64"

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

import threading

# 代理配置
proxy_url = middleware.bucketGet(BUCKET_CONFIG, 'proxy_api') or ''
IS_PROXY = bool(proxy_url)
_proxy_cache = {}
_proxy_lock = threading.Lock()


def _extract_proxy(raw):
    """从各种格式中提取代理地址: 纯IP:端口、JSON、带协议头"""
    raw = str(raw or '').strip().strip('"').strip("'")
    if not raw:
        return ''
    if '\n' in raw:
        raw = next((l.strip() for l in raw.split('\n') if l.strip()), '')
    if raw.startswith('{'):
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                for key in ('proxy', 'data', 'result', 'ip_port', 'socks'):
                    val = data.get(key)
                    if val and isinstance(val, str):
                        return val.strip()
                    if val and isinstance(val, dict) and val.get('ip') and val.get('port'):
                        return f"{val['ip']}:{val['port']}"
                if data.get('ip') and data.get('port'):
                    return f"{data['ip']}:{data['port']}"
        except:
            pass
    return raw


def _build_proxy(raw):
    """构建代理dict，支持: 1.2.3.4:8080 / http://1.2.3.4:8080 / socks5://..."""
    ip = _extract_proxy(raw)
    if not ip or '白名单' in ip:
        return None
    if '://' not in ip:
        ip = f'http://{ip}'
    return {'http': ip, 'https': ip}


def _is_direct_proxy(source):
    """判断是固定代理还是API地址"""
    if not source:
        return False
    candidate = source if '://' in source else f'http://{source}'
    from urllib.parse import urlparse
    parsed = urlparse(candidate)
    return bool(parsed.hostname and parsed.port and parsed.path in ('', '/'))


def get_proxy(account_key="default") -> dict:
    if not IS_PROXY:
        return None
    with _proxy_lock:
        cached = _proxy_cache.get(account_key)
        if cached:
            return cached

    if _is_direct_proxy(proxy_url):
        proxy = _build_proxy(proxy_url)
    else:
        for attempt in range(3):
            try:
                r = requests.get(proxy_url, timeout=5, verify=False)
                if r.status_code != 200:
                    time.sleep(1)
                    continue
                proxy = _build_proxy(r.text)
                if proxy:
                    break
            except:
                time.sleep(1)
        else:
            return None

    if proxy:
        with _proxy_lock:
            _proxy_cache[account_key] = proxy
    return proxy


def reset_proxy(account_key="default"):
    with _proxy_lock:
        _proxy_cache.pop(account_key, None)


# ==================== 签名 ====================
def generate_sign():
    sha1_md5 = hashlib.md5(APP_SHA1.encode()).hexdigest()
    plaintext = f"daoransign_{sha1_md5}_{int(time.time())}"
    cipher = AES.new(SIGN_AES_KEY, AES.MODE_CBC, SIGN_AES_IV)
    return base64.b64encode(cipher.encrypt(pad(plaintext.encode(), 16))).decode()


# ==================== 账号存取 ====================
def get_user_members() -> list:
    data = middleware.bucketGet(BUCKET_USER, userid) or ""
    return [p.strip() for p in data.split(",") if p.strip()]


def save_user_members(members: list):
    middleware.bucketSet(BUCKET_USER, userid, ",".join(members))


def get_member_info(member_id: str) -> dict:
    data = middleware.bucketGet(BUCKET_TOKEN, member_id) or ""
    if not data:
        return {}
    parts = data.split("#")
    return {"memberId": parts[0], "nick": parts[1] if len(parts) > 1 else ""}


def save_member_info(member_id: str, nick: str):
    middleware.bucketSet(BUCKET_TOKEN, member_id, f"{member_id}#{nick}")


# ==================== 微信扫码 ====================
def wx_qr_get_uuid():
    try:
        resp = requests.get("https://open.weixin.qq.com/connect/app/qrconnect",
            params={"appid": APPID_APP, "bundleid": APP_BUNDLEID,
                    "scope": "snsapi_userinfo", "state": "lyhxcx", "pass_ticket": str(uuid.uuid4())},
            headers={"User-Agent": WX_UA, "Referer": "https://open.weixin.qq.com/"},
            timeout=15, verify=False)
        m = re.search(r'uuid\s*:\s*"(\w+)"', resp.text)
        return m.group(1) if m else None
    except:
        return None


def wx_qr_check_scan(uuid_str, last=""):
    try:
        params = {"uuid": uuid_str, "f": "url", "_": int(time.time() * 1000)}
        if last:
            params["last"] = last
        resp = requests.get("https://long.open.weixin.qq.com/connect/l/qrconnect",
            params=params, headers={"User-Agent": WX_UA, "Referer": "https://open.weixin.qq.com/"},
            timeout=5, verify=False)
        text = resp.text
        if "window.wx_errcode=405" in text:
            m = re.search(r"oauth\?code=([^&\"']+)", text) or re.search(r"wx_code='([^']+)'", text)
            if m:
                return {"status": "ok", "code": m.group(1)}
        elif "window.wx_errcode=402" in text:
            return {"status": "scanned"}
        elif "window.wx_errcode=408" in text:
            return {"status": "waiting"}
        elif "window.wx_errcode=404" in text:
            return {"status": "waiting"}
    except requests.exceptions.Timeout:
        pass
    except:
        pass
    return {"status": "waiting"}


def wx_qr_login():
    uuid_str = wx_qr_get_uuid()
    if not uuid_str:
        sender.reply("获取二维码失败，请重试")
        return None

    qr_url = f"https://open.weixin.qq.com/connect/qrcode/{uuid_str}"
    sender.reply(f"=====梨园行扫码登录=====\n请用微信扫描二维码:\n[CQ:image,file={qr_url}]\n3分钟内有效，发送 Q 取消等待")

    last = "408"
    scanned_notified = False
    deadline = time.time() + 180
    while time.time() < deadline:
        result = wx_qr_check_scan(uuid_str, last)
        if result["status"] == "ok":
            return result["code"]
        elif result["status"] == "scanned":
            if not scanned_notified:
                sender.reply("已扫码，请在微信上点确认...")
                scanned_notified = True
            last = "402"
        else:
            last = "408"
        try:
            user_msg = sender.waitInput(timeout=2)
            if user_msg and str(user_msg).strip().upper() == 'Q':
                sender.reply("已取消扫码")
                return None
        except:
            pass

    sender.reply("等待超时，请重新发送「梨园扫码」")
    return None


def login_app_with_code(code):
    sign_val = generate_sign()
    try:
        resp = requests.post(f"{FLY_BASE}/API_UBP/wx/app/userinfo",
            headers={"Content-Type": "application/json; charset=UTF-8", "User-Agent": "okhttp/3.12.10",
                     "md5": FLY_MD5, "sign": sign_val, "project": "lyhxcx", "item": "x5"},
            json={"client": "Mobile", "code": code, "devUid": f"autman_{int(time.time())}",
                  "ip": "127.0.0.1", "item": "x5", "needMemberId": True,
                  "project": "lyhxcx", "province": "100", "sign": sign_val},
            proxies=get_proxy(), verify=False, timeout=20)
        result = resp.json()
        if result.get("code") != 10000000:
            return None
        return {
            "memberId": result.get("memberId"),
            "nick": result.get("nickName") or "",
            "bindWX": result.get("bindWX", False),
        }
    except:
        return None


# ==================== 任务执行 ====================
def aop_request(path, member_id, extra=None):
    sign = generate_sign()
    data = {"userId": member_id, "sign": sign, "project": "lyhxcx", "item": "x5"}
    if extra:
        data.update(extra)
    for attempt in range(2):
        try:
            r = requests.post(f"{AOP_BASE}/API_AOP{path}",
                headers={"Content-Type": "application/json; charset=UTF-8", "User-Agent": "okhttp/3.12.10",
                         "md5": AOP_MD5, "sign": sign, "project": "lyhxcx", "item": "x5"},
                json=data, proxies=get_proxy(member_id), verify=False, timeout=15)
            return r.json()
        except:
            reset_proxy(member_id)
            if attempt == 0:
                continue
    return None


def run_tasks(member_id, nick):
    lines = []
    task_resp = aop_request("/act/coin/task/getDetail", member_id, {"actCode": "ott_coin"})
    if not task_resp or task_resp.get("code") != 10000000:
        return f"[{nick}] 获取任务失败"

    task_map = task_resp.get("taskMap", {})
    total_earned = 0
    type_names = {"type2": "签到", "type3": "听戏", "type4": "看视频", "type5": "看短视频", "type6": "广告任务", "type7": "邀请好友", "type1": "额外任务"}

    for type_key, task_info in task_map.items():
        task_type = task_info.get("taskType", 0)
        task_id = task_info.get("taskId", "")
        per_coins = task_info.get("perCoins", 0)
        today_coins = task_info.get("todayCoins", 0)
        max_coins = task_info.get("todayMaxCoins", 0)
        finish_flag = task_info.get("finishFlag", 0)
        task_name = type_names.get(type_key, f"任务{task_type}")

        if finish_flag == 1 or (max_coins > 0 and today_coins >= max_coins):
            lines.append(f"  {task_name}: 已完成({today_coins})")
            continue
        if task_type == 7:
            continue

        if task_type == 2:
            resp = aop_request("/act/coin/task/finish", member_id, {"actCode": "ott_coin", "taskType": task_type, "taskId": task_id})
            if resp and resp.get("result") == 0:
                total_earned += per_coins
                lines.append(f"  {task_name}: +{per_coins}")
            else:
                lines.append(f"  {task_name}: 失败")
            continue

        count = 0
        fail = 0
        max_count = min(50, (max_coins - today_coins) // per_coins + 1) if per_coins > 0 else 10
        sender.reply(f"🔄 {nick} | {task_name} 执行中...")
        while count < max_count and today_coins + (count * per_coins) < max_coins:
            resp = aop_request("/act/coin/task/finish", member_id, {"actCode": "ott_coin", "taskType": task_type, "taskId": task_id})
            if resp and resp.get("result") == 0:
                count += 1
                total_earned += per_coins
                fail = 0
            else:
                fail += 1
                if fail >= 3:
                    break
                time.sleep(0.3)
                continue
            time.sleep(0.1)
        lines.append(f"  {task_name}: +{count * per_coins}")

    # 重新检查未完成的任务，补跑一轮
    task_resp2 = aop_request("/act/coin/task/getDetail", member_id, {"actCode": "ott_coin"})
    if task_resp2 and task_resp2.get("code") == 10000000:
        task_map2 = task_resp2.get("taskMap", {})
        for type_key, task_info in task_map2.items():
            task_type = task_info.get("taskType", 0)
            task_id = task_info.get("taskId", "")
            per_coins = task_info.get("perCoins", 0)
            today_coins = task_info.get("todayCoins", 0)
            max_coins = task_info.get("todayMaxCoins", 0)
            finish_flag = task_info.get("finishFlag", 0)
            task_name = type_names.get(type_key, f"任务{task_type}")

            if finish_flag == 1 or (max_coins > 0 and today_coins >= max_coins) or task_type in (2, 7):
                continue

            remaining = max_coins - today_coins
            if remaining <= 0:
                continue

            count = 0
            fail = 0
            max_count = remaining // per_coins + 1 if per_coins > 0 else 0
            while count < max_count and today_coins + (count * per_coins) < max_coins:
                resp = aop_request("/act/coin/task/finish", member_id, {"actCode": "ott_coin", "taskType": task_type, "taskId": task_id})
                if resp and resp.get("result") == 0:
                    count += 1
                    total_earned += per_coins
                    fail = 0
                else:
                    fail += 1
                    if fail >= 3:
                        break
                    time.sleep(0.3)
                    continue
                time.sleep(0.1)
            if count > 0:
                lines.append(f"  {task_name}(补): +{count * per_coins}")

    # 提现
    cash_msg = do_cash_out(member_id)
    lines.append(f"  {cash_msg}")

    detail = aop_request("/act/coin/task/getDetail", member_id, {"actCode": "ott_coin"})
    current_coins = detail.get("coins", 0) if detail and detail.get("code") == 10000000 else 0

    return f"[{nick}]\n" + "\n".join(lines) + f"\n  本次+{total_earned} | 余额{current_coins}"


def do_cash_out(member_id):
    cash_resp = aop_request("/act/coin/task/cashCoins", member_id, {"actCode": "ott_coin"})
    tiers = cash_resp.get("coins", []) if cash_resp and cash_resp.get("code") == 10000000 else []

    detail = aop_request("/act/coin/task/getDetail", member_id, {"actCode": "ott_coin"})
    current_coins = detail.get("coins", 0) if detail else 0

    if current_coins < 1000:
        return f"提现: 金币不足(需1000, 当前{current_coins})"
    chosen = (current_coins // 1000) * 1000
    try:
        ad_sign = generate_sign()
        requests.get(f"{FLY_BASE}/API_UBP/xiaomi/ad/clickBack?oaid=37bba68be59bdb7a&pkg=uni.UNIA317E51&dataType=2",
            headers={"User-Agent": "okhttp/3.12.10", "md5": FLY_MD5, "sign": ad_sign, "project": "lyhxcx", "item": "x5"},
            verify=False, timeout=10)
    except:
        pass
    time.sleep(1)

    ex_resp = aop_request("/act/coin/task/exchange", member_id, {"actCode": "ott_coin", "useCoins": chosen})
    if ex_resp and ex_resp.get("result") == 0:
        return f"提现: {chosen}金币成功"
    ret = ex_resp.get("retMsg", "失败") if ex_resp else "失败"
    return f"提现: {ret}"


# ==================== 指令路由 ====================
def process_scan():
    sender.reply("正在获取微信登录二维码...")
    code = wx_qr_login()
    if not code:
        return

    sender.reply("✅ 扫码成功，正在登录...")
    info = login_app_with_code(code)
    if not info:
        sender.reply("❌ 登录失败")
        return

    member_id = info.get("memberId")
    nick = info.get("nick") or "用户"

    if not member_id:
        sender.reply("❌ 该微信号未注册梨园行戏曲APP\n请先在APP内微信登录一次注册")
        return

    save_member_info(member_id, nick)
    members = get_user_members()
    if member_id not in members:
        members.append(member_id)
        save_user_members(members)

    sender.reply(f"✅ 登录成功: {nick}\n正在执行任务...")
    result = run_tasks(member_id, nick)
    sender.reply(result)


def process_query():
    members = get_user_members()
    if not members:
        sender.reply("暂无绑定账号\n💡 发送「梨园扫码」登录")
        return

    lines = ["=====梨园行戏曲====="]
    for mid in members:
        info = get_member_info(mid)
        nick = info.get("nick", mid)
        resp = aop_request("/act/coin/task/getDetail", mid, {"actCode": "ott_coin"})
        coins = resp.get("coins", 0) if resp and resp.get("code") == 10000000 else "查询失败"
        lines.append(f"  {nick}: {coins}金币")
    lines.append("====================")
    sender.reply("\n".join(lines))


def process_task():
    members = get_user_members()
    if not members:
        sender.reply("暂无绑定账号\n💡 发送「梨园扫码」登录")
        return

    sender.reply(f"开始并发执行 {len(members)} 个账号的任务...")

    def _run(mid):
        info = get_member_info(mid)
        nick = info.get("nick", mid)
        return run_tasks(mid, nick)

    results = []
    with ThreadPoolExecutor(max_workers=len(members)) as executor:
        futures = {executor.submit(_run, mid): mid for mid in members}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(f"[{futures[future]}] 异常: {e}")

    sender.reply("=====梨园行任务报告=====\n" + "\n---\n".join(results) + "\n====================")


def main():
    try:
        msg = sender.getMessage().strip()
    except:
        msg = ""

    if re.match(r"^(梨园|ly)(扫码)$", msg):
        process_scan()
    elif re.match(r"^(梨园|ly)(查询)$", msg):
        process_query()
    elif re.match(r"^(梨园|ly)(任务|登录|登陆)$", msg):
        process_task()
    else:
        sender.setContinue()


main()
