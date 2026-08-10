# [rule: ^(壹品仓|ypc)(登录|登陆)$|^登(录|陆)(壹品仓|ypc)$|^(壹品仓|ypc)(查询|管理)$|^(查询|管理)(壹品仓|ypc)$|^壹品仓授权$|^壹品仓教程$|^壹品仓一键运行$|^壹品仓签到$|^壹品仓清理$]
# [disable:false]
# [platform: qq,wx]
# [cron: 0 8 * * *]
# [public:true]
# [title:壹品仓]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: 1603960061]
# [open_source: false]
# [version: 1.2.1]
# [price: 38.88]
# [admin: false]
# [icon: https://tg.96218.xyz/file/BQACAgUAAxkDAAIG_mmxCTjoSpkpvhpHLZ64nnYxoloeAAIVHgACZNKIVVmXCAF9vuQQOgQ.png]
# [description: APP【壹品仓】插件<br>功能：短信登录、账号管理、授权、查询、签到、清理<br>指令：壹品仓登录/管理/查询/授权/签到/清理/教程/一键运行]

# [param: {"required":false,"key":"G_YPC.price","name":"月费价格","placeholder":"0.88","value":"0.88","desc":"一个账号每月的价格"}]
# [param: {"required":false,"key":"G_SKM.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款码(全局)","desc":"微信赞赏码/收款码链接"}]
# [param: {"required":false,"key":"G_YPC.coin","name":"积分/月","placeholder":"100","value":"100","desc":"一个账号每月所需积分数量"}]
# [param: {"required":false,"key":"G_YPC.proxy_api","name":"代理API","placeholder":"http://example.com/getip","desc":"获取代理IP的接口地址"}]

import base64
import hashlib
import importlib
import json
import random
import re
import threading
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA

middleware = importlib.import_module("middleware")

BUCKET_USER = "G_YPC_user"
BUCKET_TOKEN = "G_YPC_token"
BUCKET_AUTH = "G_YPC_auth"
BUCKET_CONFIG = "G_YPC"

DEFAULT_URL_PATH = "/api/v1/message/sms2"
LOGIN_URL_PATH = "/api/v1/user/login/fast2"
TIME_URL_PATH = "/api/v1/appInit/time"
DEFAULT_HEADERS = {
    "device": "android",
    "version": "5.8.10",
    "v_code": "32708351",
    "channel": "developer-default",
    "systemversion": "Xiaomi|Redmi K20 Pro|14",
    "sysversion": "34",
    "content-type": "application/json; charset=UTF-8",
    "accept-encoding": "gzip",
    "user-agent": "okhttp/4.9.0",
}
DEFAULT_BODY = {"type": "3", "tel": ""}
DEFAULT_HOST = "api.shanghaicang.com.cn"
SIGN_KEY = "base64:qc93zphetnxh2swb/deosb0zuwhhwhwhiu61zdapvdnojkoye="
RSA_PUBLIC_KEY_BASE64 = (
    "MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAxHtZ1EY7AQT2LwzKfI/"
    "iWFX/zPxSbi7uqQ3n+8Cwz/YmXYtw2IoSPpzfff+Qhd7SqSqIqnpuB+bg+2nVsDxBL"
    "ZPMC97vtlbaxRRoYZm7r+d3HzwysuT714InkVIFuqn1+DCwrYN5/ktXJAvfIhteHM1"
    "Y4TKfh40tPnTUKm9z8LJL0e9+I32lTJ4ZBurfO/Iv048veGVtJevGXHzq2cTxSxRHn"
    "9ulMuUOJPzmlw04x6uGSFnpB37JW+LVi9kt1FbE/vkaPFPXSehmq7oJiJ5YqXiegBP"
    "EgKuCsfq5FIg2bi1FeX+zWc7ZnQJuU40urw3wGuUD2O9l9dGqjufqvsURUh6vMuJPs"
    "wXo402e7c2y2mnTrOW6ZT1J2bXPRxvOEYQVhN7mX2eLOX9naw4yZ7dF4r3h7P5avyh"
    "r+E5JIbkNuk/XWLRJHWe0wNqPDbOfWcuPjoWmsJjcQoLIRwvUYeqWh9SigMjv+QQvF"
    "itoV37l52WRLBpW8ZdoMvoQg9DulvS/TmzK9VhzwmiV+26rkZZQussb7uilsmGvn0a"
    "ijbqwU2knvwBaAXlBdMgHtd6LDlj7WHBpXd61z/tH13IIv5vkVuo8aGZS5/35twTN7"
    "pt0Eko9c7axc1ujpCjSz/F/XqaDGe2ddPgNtxHO/0cAmxXYQXpL4rSvdAigOuNHJOR"
    "Vqw0CAwEAAQ=="
)
SIGN_SECRET_KEY = "base64:qC93ZPHeTNxh2SwB/DeOSb0zUwhHWHWHiU61ZDAPvdnOjkOYE="
SIGN_NONSTR = "oS5rZW8u6YkPihWM"
SIGN_DEVICE = "h5"
SIGN_TOUCHID = "h5"
SIGN_VERSION = "5.6.0"
SIGN_DEVICE_NO = "19E99BD9-B24E-4D82-8451-147D22E9545C"
SIGN_IN_URL = (
    "https://ypc-services.shanghaicang.com.cn/activity-service/sign-in/confirm"
)
SIGN_HEAD_DATA_URL = (
    "https://ypc-services.shanghaicang.com.cn/activity-service/sign-in/head/data"
)
SIGN_HEAD_DATA_NONSTR = "pPqkLVmEokfJGbSd"

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

proxy_url = middleware.bucketGet(bucket=BUCKET_CONFIG, key="proxy_api") or ""
IS_PROXY = bool(proxy_url)
proxy_cache = {}
proxy_lock = threading.Lock()


def log(level: str, msg: str, account: Optional[str] = None) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = f"[{level}] {timestamp}"
    if account:
        prefix += f" [{mask_phone(account)}]"
    print(f"{prefix} {msg}")


def mask_phone(phone: str) -> str:
    if not phone or len(phone) < 7:
        return phone or "***"
    return f"{phone[:3]}****{phone[-4:]}"


def reply_error(msg: str, detail: Optional[str] = None) -> None:
    response = f"❌ {msg}"
    if detail:
        response += f"\n详情: {detail}"
    sender.reply(response)


def reply_success(msg: str, data: Optional[Dict[str, Any]] = None) -> None:
    response = f"✅ {msg}"
    if data:
        for k, v in data.items():
            response += f"\n{k}: {v}"
    sender.reply(response)


def render_block(title: str, lines: List[str]) -> str:
    content = [f"====={title}====="]
    content.extend(lines)
    content.append("====================")
    return "\n".join(content)


def count_authorized_accounts(phones: List[str]) -> int:
    return sum(1 for phone in phones if is_authorized(phone))


def get_user_phones(user_id: Optional[str] = None) -> List[str]:
    if not user_id:
        user_id = userid
    data = middleware.bucketGet(BUCKET_USER, user_id) or ""
    return [p.strip() for p in data.split(",") if p.strip()]


def save_user_phones(phones: List[str], user_id: Optional[str] = None) -> None:
    if not user_id:
        user_id = userid
    middleware.bucketSet(BUCKET_USER, user_id, ",".join(phones))


def add_account(phone: str, user_id: Optional[str] = None) -> None:
    phones = get_user_phones(user_id)
    if phone not in phones:
        phones.append(phone)
        save_user_phones(phones, user_id)


def get_token(phone: str) -> Dict[str, str]:
    data = middleware.bucketGet(BUCKET_TOKEN, phone) or ""
    if not data:
        return {}
    parts = data.split("#")
    if len(parts) >= 3:
        return {"userId": parts[0], "token": parts[1], "refreshToken": parts[2]}
    return {}


def save_token(phone: str, userId: str, token: str, refreshToken: str) -> None:
    middleware.bucketSet(BUCKET_TOKEN, phone, f"{userId}#{token}#{refreshToken}")


def get_auth(phone: str) -> str:
    return middleware.bucketGet(BUCKET_AUTH, phone) or ""


def save_auth(phone: str, expire_date: str) -> None:
    middleware.bucketSet(BUCKET_AUTH, phone, expire_date)


def is_authorized(phone: str) -> bool:
    expire = get_auth(phone)
    if not expire:
        return False
    try:
        return datetime.strptime(expire, "%Y-%m-%d").date() >= datetime.now().date()
    except Exception:
        return False


def del_account(phone: str, user_id: Optional[str] = None) -> None:
    if not user_id:
        user_id = userid
    phones = get_user_phones(user_id)
    if phone in phones:
        phones.remove(phone)
        if phones:
            save_user_phones(phones, user_id)
        else:
            middleware.bucketDel(BUCKET_USER, user_id)
    middleware.bucketDel(BUCKET_TOKEN, phone)
    middleware.bucketDel(BUCKET_AUTH, phone)


def get_config() -> Dict[str, Any]:
    ma_pay_switch_raw = (
        middleware.bucketGet("dd_sign_config", "ma_pay_switch") or "false"
    )
    if isinstance(ma_pay_switch_raw, bool):
        ma_pay_switch = ma_pay_switch_raw
    elif ma_pay_switch_raw is None:
        ma_pay_switch = False
    else:
        ma_pay_switch = str(ma_pay_switch_raw).lower() == "true"
    return {
        "price": Decimal(middleware.bucketGet(BUCKET_CONFIG, "price") or "0"),
        "coin": middleware.bucketGet(BUCKET_CONFIG, "coin") or "",
        "zsm": middleware.bucketGet("G_SKM", "zsm") or "",
        "proxy_api": middleware.bucketGet(BUCKET_CONFIG, "proxy_api") or "",
        "ma_pay_switch": ma_pay_switch,
        "ma_pay_gateway": middleware.bucketGet("dd_sign_config", "ma_pay_gateway")
        or "",
        "ma_pay_pid": middleware.bucketGet("dd_sign_config", "ma_pay_pid") or "",
        "ma_pay_key": middleware.bucketGet("dd_sign_config", "ma_pay_key") or "",
        "ma_pay_type": middleware.bucketGet("dd_sign_config", "ma_pay_type")
        or "alipay,wxpay",
        "ma_pay_notify_url": middleware.bucketGet("dd_sign_config", "ma_pay_notify_url")
        or "",
    }


def get_proxy(
    force_new: bool = False, account_key: Optional[str] = None
) -> Optional[Dict[str, str]]:
    if not IS_PROXY or not proxy_url:
        return None
    if account_key and not force_new:
        with proxy_lock:
            if account_key in proxy_cache:
                return proxy_cache[account_key]
    try:
        response = requests.get(proxy_url, timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            if "请先添加白名单" in ip or not ip:
                log("WARNING", "代理服务异常")
                return None
            proxies = {"http": f"http://{ip}", "https": f"http://{ip}"}
            if account_key:
                with proxy_lock:
                    proxy_cache[account_key] = proxies
            return proxies
    except Exception as exc:
        log("ERROR", f"获取代理失败: {exc}")
    return None


def safe_request(method: str, url: str, **kwargs) -> Optional[Dict[str, Any]]:
    kwargs.setdefault("timeout", 15)
    kwargs.setdefault("verify", False)
    proxy = get_proxy()
    if proxy:
        kwargs["proxies"] = proxy
    try:
        resp = requests.request(method, url, **kwargs)
        return resp.json()
    except requests.Timeout:
        log("ERROR", f"请求超时: {url}")
    except requests.RequestException as exc:
        log("ERROR", f"请求失败: {exc}")
    except json.JSONDecodeError:
        log("ERROR", "JSON解析失败")
    return None


def _load_json_value(value: str) -> object:
    return json.loads(value)


def _normalize_json_object(payload: object) -> Dict[str, Any]:
    if isinstance(payload, dict):
        normalized = {}
        for key, val in payload.items():
            normalized[str(key)] = val
        return normalized
    return {"raw": str(payload)}


def _encrypt_phone(phone: str) -> str:
    public_key_bytes = base64.b64decode(RSA_PUBLIC_KEY_BASE64)
    public_key = RSA.import_key(public_key_bytes)
    cipher = PKCS1_v1_5.new(public_key)
    encrypted = cipher.encrypt(phone.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")


def _build_sign(params: Dict[str, str]) -> str:
    parts = [f"{key}={params[key]}" for key in sorted(params.keys())]
    joined = "￥".join(parts)
    sorted_parts = sorted(joined.split("￥"))
    joined_amp = "&".join(sorted_parts)
    text_with_key = f"{joined_amp}{SIGN_SECRET_KEY}"
    return hashlib.md5(text_with_key.encode("utf-8")).hexdigest()


def sign_in_by_token(token: str) -> Dict[str, Any]:
    if not token:
        return {"ok": False, "msg": "token为空"}
    timestamp = str(int(time.time()))
    biz_data = {"signInAt": "", "type": 0, "deviceNo": SIGN_DEVICE_NO}
    request_params = {
        "version": SIGN_VERSION,
        "token": token,
        "device": SIGN_DEVICE,
        "timestamp": timestamp,
        "touchid": SIGN_TOUCHID,
        "nonstr": SIGN_NONSTR,
        "bizData": json.dumps(biz_data, separators=(",", ":")),
    }
    request_params["sign"] = _build_sign(request_params)
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 YPCAPPUserAgent YPCAPPUserAgent",
        "Content-Type": "application/json",
        "timeStamp": timestamp,
        "touchid": SIGN_TOUCHID,
        "token": token,
        "device": SIGN_DEVICE,
    }
    res = safe_request("post", SIGN_IN_URL, json=request_params, headers=headers)
    if not isinstance(res, dict):
        return {"ok": False, "msg": "请求失败"}
    if res.get("code") == 200:
        return {"ok": True, "msg": "签到成功"}
    return {"ok": False, "msg": f"签到失败：{res.get('msg', '未知错误')}"}


def get_sign_head_data(token: str) -> Dict[str, Any]:
    if not token:
        return {"ok": False, "msg": "token为空"}
    timestamp = str(int(time.time()))
    request_params = {
        "version": SIGN_VERSION,
        "token": token,
        "device": SIGN_DEVICE,
        "timestamp": timestamp,
        "touchid": SIGN_TOUCHID,
        "nonstr": SIGN_HEAD_DATA_NONSTR,
        "bizData": "{}",
    }
    request_params["sign"] = _build_sign(request_params)
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Redmi K20 Pro Build/UKQ1.240624.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 YPCAPPUserAgent",
        "Content-Type": "application/json",
        "timeStamp": timestamp,
        "touchid": SIGN_TOUCHID,
        "token": token,
        "device": SIGN_DEVICE,
        "Accept": "*/*",
        "Origin": "https://ypch5.shanghaicang.com.cn",
        "Referer": "https://ypch5.shanghaicang.com.cn/",
        "X-Requested-With": "com.ypcang.android.shop",
    }
    res = safe_request("post", SIGN_HEAD_DATA_URL, json=request_params, headers=headers)
    if not isinstance(res, dict):
        return {"ok": False, "msg": "查询失败"}
    data = res.get("data")
    if res.get("code") == 200 and isinstance(data, dict):
        return {"ok": True, "data": data}
    return {"ok": False, "msg": str(res.get("msg") or "查询失败")}


def _is_signed_status(status: Any) -> bool:
    return str(status) in {"1", "2"}


def get_continuous_sign_days(data: Dict[str, Any]) -> int:
    last_month_calendar = data.get("lastMonthCalendar")
    current_calendar = data.get("calendar")
    if not isinstance(last_month_calendar, list):
        last_month_calendar = []
    if not isinstance(current_calendar, list):
        current_calendar = []

    previous_entries = [item for item in last_month_calendar if isinstance(item, dict)]
    current_entries = [item for item in current_calendar if isinstance(item, dict)]
    combined = previous_entries + current_entries
    if not combined:
        return 0

    today_offset = None
    for idx, item in enumerate(current_entries):
        if str(item.get("day") or "") == "今天":
            today_offset = idx
            break

    if today_offset is None:
        anchor = len(combined) - 1
    else:
        today_index = len(previous_entries) + today_offset
        today_item = combined[today_index]
        if _is_signed_status(today_item.get("signStatus")) or str(data.get("isSignIn")) == "1":
            anchor = today_index
        else:
            anchor = today_index - 1

    if anchor < 0:
        return 0

    days = 0
    for idx in range(anchor, -1, -1):
        item = combined[idx]
        if _is_signed_status(item.get("signStatus")):
            days += 1
            continue
        break
    return days


def _build_time_sign(touchid: str, timestamp: str) -> str:
    sign_content = (
        f"device=android&key={SIGN_KEY}&timestamp={timestamp}&touchid={touchid}"
    )
    return hashlib.md5(sign_content.encode("utf-8")).hexdigest()


def _fetch_server_time(host: str, headers: Dict[str, str]) -> str:
    touchid = headers.get("touchid", DEFAULT_HEADERS.get("touchid", ""))
    local_timestamp = str(int(time.time()))
    sign = _build_time_sign(touchid, local_timestamp)
    url = f"https://{host}{TIME_URL_PATH}?sign={sign}&timestamp={local_timestamp}"
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    payload = _load_json_value(response.text)
    data = payload.get("data") if isinstance(payload, dict) else None
    server_time = data.get("time") if isinstance(data, dict) else None
    if isinstance(server_time, int):
        return str(server_time)
    if isinstance(server_time, str) and server_time.isdigit():
        return server_time
    return local_timestamp


def _build_sms_sign(
    encrypted_tel: str, touchid: str, timestamp: str, sms_type: str
) -> str:
    sign_tel = encrypted_tel.lower()
    sign_content = (
        "device=android"
        f"&key={SIGN_KEY}"
        f"&tel={sign_tel}"
        f"&timestamp={timestamp}"
        f"&touchid={touchid}"
        f"&type={sms_type}"
    )
    return hashlib.md5(sign_content.encode("utf-8")).hexdigest()


def _build_login_sign(
    encrypted_tel: str, code: str, touchid: str, timestamp: str
) -> str:
    sign_tel = encrypted_tel.lower()
    sign_content = (
        f"code={code}"
        "&device=android"
        f"&key={SIGN_KEY}"
        f"&tel={sign_tel}"
        f"&timestamp={timestamp}"
        f"&touchid={touchid}"
    )
    return hashlib.md5(sign_content.encode("utf-8")).hexdigest()


def _build_sms_url_path(
    encrypted_tel: str, headers: Dict[str, str], sms_type: str
) -> str:
    timestamp = _fetch_server_time(DEFAULT_HOST, headers)
    touchid = headers.get("touchid", DEFAULT_HEADERS.get("touchid", ""))
    sign = _build_sms_sign(encrypted_tel, touchid, timestamp, sms_type)
    return f"{DEFAULT_URL_PATH}?sign={sign}&timestamp={timestamp}"


def _build_login_url_path(
    encrypted_tel: str, code: str, headers: Dict[str, str]
) -> str:
    timestamp = _fetch_server_time(DEFAULT_HOST, headers)
    touchid = headers.get("touchid", DEFAULT_HEADERS.get("touchid", ""))
    sign = _build_login_sign(encrypted_tel, code, touchid, timestamp)
    return f"{LOGIN_URL_PATH}?sign={sign}&timestamp={timestamp}"


def send_sms_code(
    url_path: str, host: str, headers: Dict[str, str], body: Dict[str, Any]
) -> Dict[str, Any]:
    url = f"https://{host}{url_path}"
    response = requests.post(url, headers=headers, json=body, timeout=15)
    response.raise_for_status()
    payload = _load_json_value(response.text)
    return _normalize_json_object(payload)


def login_by_sms(phone: str, code: str) -> Dict[str, Any]:
    headers = build_device_headers()
    body = _normalize_json_object(DEFAULT_BODY)
    encrypted_tel = _encrypt_phone(phone)
    body["tel"] = encrypted_tel
    sms_type = str(body.get("type", "3"))
    sms_path = _build_sms_url_path(encrypted_tel, headers, sms_type)
    send_sms_code(sms_path, DEFAULT_HOST, headers, body)
    login_body = {"tel": encrypted_tel, "code": code}
    login_path = _build_login_url_path(encrypted_tel, code, headers)
    return send_sms_code(login_path, DEFAULT_HOST, headers, login_body)


def extract_login_token(payload: Dict[str, Any]) -> Dict[str, str]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if not isinstance(data, dict):
        return {}
    token = data.get("token") or data.get("accessToken") or ""
    refresh_token = data.get("refreshToken") or ""
    user_id = data.get("userId") or data.get("user_id") or data.get("uid") or ""
    if token:
        return {
            "userId": str(user_id),
            "token": str(token),
            "refreshToken": str(refresh_token),
        }
    return {}


def parse_selection(choice: str, max_index: int) -> Optional[List[int]]:
    if not choice or not choice.strip():
        return None
    indices = set()
    try:
        for part in choice.strip().split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start, end = map(lambda x: int(x.strip()), part.split("-"))
                if (
                    start < 1
                    or end < 1
                    or start > max_index
                    or end > max_index
                    or start > end
                ):
                    return None
                indices.update(range(start - 1, end))
            else:
                n = int(part)
                if n < 1 or n > max_index:
                    return None
                indices.add(n - 1)
        return sorted(indices) if indices else None
    except Exception:
        return None


def format_account_list(accounts: List[str]) -> str:
    if not accounts:
        return "暂无绑定账号"
    lines = []
    for i, phone in enumerate(accounts, 1):
        status = "✅" if is_authorized(phone) else "❌"
        auth_msg = get_auth(phone) or "未授权"
        lines.append(f"[{i}] {status} {mask_phone(phone)} | {auth_msg}")
    return "\n".join(lines)


def sign_in_accounts(phones: List[str]) -> None:
    if not phones:
        reply_error("暂无账号")
        return
    ok = 0
    fail = 0
    lines = []
    for idx, phone in enumerate(phones, 1):
        if idx % 5 == 0 or idx == len(phones):
            sender.reply(f"🔄 正在签到 {idx}/{len(phones)} ...")
        if not is_authorized(phone):
            fail += 1
            lines.append(f"❌ [{idx}] {mask_phone(phone)} 未授权或已到期")
            continue
        token_data = get_token(phone)
        token = token_data.get("token", "") if token_data else ""
        if not token:
            fail += 1
            lines.append(f"❌ [{idx}] {mask_phone(phone)} token为空")
            continue
        res = sign_in_by_token(token)
        if res.get("ok"):
            ok += 1
            lines.append(f"✅ [{idx}] {mask_phone(phone)} {res.get('msg')}")
        else:
            fail += 1
            lines.append(f"❌ [{idx}] {mask_phone(phone)} {res.get('msg')}")
    sender.reply(
        render_block(
            "壹品仓签到",
            [
                f"📥 账号总数: {len(phones)}",
                f"✅ 成功: {ok}",
                f"❌ 失败: {fail}",
                "--------------------",
                *lines,
            ],
        )
    )


def get_random_device() -> Dict[str, str]:
    """生成随机设备信息"""
    brands = ["Xiaomi", "OPPO", "vivo", "Huawei", "Samsung", "OnePlus", "Realme"]
    models = {
        "Xiaomi": ["Redmi K20 Pro", "Redmi Note 11", "Mi 11", "Redmi K40", "Mi 10"],
        "OPPO": ["Reno7", "Find X5", "A96", "Reno8 Pro", "K10"],
        "vivo": ["X80", "S15", "iQOO 9", "Y76s", "X70 Pro"],
        "Huawei": ["Mate 40", "P50", "nova 9", "Mate 50", "P40"],
        "Samsung": ["Galaxy S22", "Galaxy A53", "Galaxy S21", "Galaxy Note20"],
        "OnePlus": ["OnePlus 10 Pro", "OnePlus 9RT", "OnePlus Nord 2"],
        "Realme": ["GT Neo3", "GT2 Pro", "Q5 Pro", "GT Master"],
    }
    android_versions = ["12", "13", "14"]

    brand = random.choice(brands)
    model = random.choice(models[brand])
    android_ver = random.choice(android_versions)

    return {
        "brand": brand,
        "model": model,
        "android": android_ver,
        "sysmodel": f"{brand}|{model}|{android_ver}",
        "systemversion": f"{brand}|{model}|{android_ver}",
    }


def get_random_ua() -> str:
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1",
    ]
    return random.choice(uas)


def build_device_headers() -> Dict[str, str]:
    """构建随机设备请求头"""
    touchid = "".join(random.choices("0123456789abcdef", k=16))
    androidid = "".join(random.choices("0123456789abcdef", k=16))
    device_info = get_random_device()

    headers = DEFAULT_HEADERS.copy()
    headers["touchid"] = touchid
    headers["androidid"] = androidid
    headers["sysmodel"] = device_info["sysmodel"]
    headers["systemversion"] = device_info["systemversion"]
    headers["user-agent"] = get_random_ua()
    return headers


def request_sms_code(phone: str) -> bool:
    headers = build_device_headers()
    body = _normalize_json_object(DEFAULT_BODY)
    encrypted_tel = _encrypt_phone(phone)
    body["tel"] = encrypted_tel
    sms_type = str(body.get("type", "3"))
    sms_path = _build_sms_url_path(encrypted_tel, headers, sms_type)
    result = send_sms_code(sms_path, DEFAULT_HOST, headers, body)
    return bool(result)


def process_login() -> None:
    sender.reply(
        render_block(
            "壹品仓登录",
            [
                "请输入手机号(11位)",
                "回复 q 退出",
            ],
        )
    )
    phone = sender.input(120000, 1, False)
    if not phone or phone.lower() == "q":
        sender.reply("✅ 已取消")
        return
    phone = phone.strip()
    if not re.match(r"^1\d{10}$", phone):
        reply_error("手机号格式错误")
        return
    try:
        request_sms_code(phone)
    except Exception as exc:
        reply_error("短信发送失败", str(exc))
        return
    sender.reply(
        render_block(
            "壹品仓登录",
            [
                f"📱 手机号: {mask_phone(phone)}",
                "请输入短信验证码(6位)",
                "回复 q 退出",
            ],
        )
    )
    code = sender.input(120000, 1, False)
    if not code or code.lower() == "q":
        sender.reply("✅ 已取消")
        return
    code = code.strip()
    if not code.isdigit() or len(code) != 6:
        reply_error("验证码格式错误")
        return
    try:
        result = login_by_sms(phone, code)
    except Exception as exc:
        reply_error("登录失败", str(exc))
        return
    token_data = extract_login_token(result)
    if not token_data:
        reply_error("登录失败", json.dumps(result, ensure_ascii=False))
        return
    save_token(
        phone,
        token_data.get("userId", ""),
        token_data.get("token", ""),
        token_data.get("refreshToken", ""),
    )
    add_account(phone)
    bound_count = len(get_user_phones())
    sender.reply(
        render_block(
            "壹品仓登录",
            [
                "📥 提交数量: 1",
                "✅ 成功: 1",
                "❌ 失败: 0",
                f"📱 当前绑定: {bound_count}个",
                f"📌 本次绑定: {mask_phone(phone)}",
                "发送「壹品仓管理」进行授权",
            ],
        )
    )


def authorize_accounts(phones: List[str]) -> bool:
    config = get_config()
    if not phones:
        reply_error("未选择账号")
        return False
    price = config.get("price", Decimal("0"))
    coin_price = config.get("coin", "")
    zsm = config.get("zsm", "")
    user_coin = Decimal(middleware.bucketGet("dd_sign_points", userid) or "0")
    has_pay = bool(price and zsm)
    has_coin = bool(coin_price)
    if not has_pay and not has_coin:
        reply_error("未配置授权方式")
        return False
    account_count = len(phones)
    phone_display = mask_phone(phones[0]) + (
        f" 等{account_count}个" if account_count > 1 else ""
    )
    sender.reply(
        render_block(
            "壹品仓授权",
            [
                f"📱 账号数: {account_count}",
                f"📌 目标账号: {phone_display}",
                "请输入授权月数(1-12)",
                '回复 "q" 退出',
            ],
        )
    )
    m = sender.listen(60000)
    if not m or m.strip().lower() == "q":
        sender.reply("✅ 已取消")
        return False
    try:
        months = int(m.strip())
        if not (1 <= months <= 12):
            raise ValueError()
    except Exception:
        reply_error("无效月数")
        return False
    total_price = price * months * account_count
    total_coin = (
        Decimal(coin_price) * months * account_count if coin_price else Decimal("0")
    )
    options = []
    handlers = {}
    opt_num = 1
    if has_pay:
        options.append(f"[{opt_num}] 微信扫码 ¥{total_price}")
        handlers[str(opt_num)] = "pay"
        opt_num += 1
    if has_coin:
        options.append(f"[{opt_num}] 积分 {total_coin}")
        handlers[str(opt_num)] = "coin"
    sender.reply(
        render_block(
            "壹品仓授权方式",
            [
                f"📱 账号数: {account_count}",
                f"⏰ 时长: {months}个月",
                f"💰 现金: ¥{total_price}",
                f"🪙 积分: {total_coin}",
                f"📊 当前积分: {user_coin}",
                *options,
                '回复序号选择，回复 "q" 取消',
            ],
        )
    )
    c = sender.listen(60000)
    if not c or c.strip().lower() == "q":
        sender.reply("✅ 已取消")
        return False
    c = c.strip()
    if c not in handlers:
        reply_error("无效选择")
        return False
    if handlers[c] == "pay":
        sender.reply(
            render_block(
                "壹品仓扫码支付",
                [
                    f"💰 支付金额: ¥{total_price}",
                    f"📱 账号数: {account_count}",
                    "请扫码支付",
                    '回复 "q" 取消',
                ],
            )
        )
        sender.replyImage(zsm)
        result = sender.waitPay(timeout=600000, exitcode="q")
        if result == "q":
            sender.reply("❌ 已取消")
            return False
        info = extract_payment_info(result)
        status = verify_payment(info, total_price)
        if status != "success":
            reply_error("支付失败")
            return False
    else:
        if user_coin < total_coin:
            reply_error("积分不足")
            return False
        sender.reply(f"确认扣除{total_coin}积分？回复Y确认")
        cf = sender.listen(60000)
        if not cf or cf.strip().lower() != "y":
            sender.reply("✅ 已取消")
            return False
        middleware.bucketSet("dd_sign_points", userid, str(user_coin - total_coin))
    expire = ""
    for phone in phones:
        current = get_auth(phone)
        base = (
            datetime.strptime(current, "%Y-%m-%d").date()
            if current and is_authorized(phone)
            else datetime.now().date()
        )
        expire = (base + timedelta(days=30 * months)).strftime("%Y-%m-%d")
        save_auth(phone, expire)
    sender.reply(
        render_block(
            "壹品仓授权完成",
            [
                f"📱 账号数: {len(phones)}",
                f"⏰ 时长: {months}个月",
                f"✅ 授权成功: {len(phones)}",
                f"📅 到期时间: {expire}",
            ],
        )
    )
    return True


def extract_payment_info(payment_result: Any) -> Dict[str, Any]:
    info: Dict[str, Any] = {"money": None, "status": -1.0, "is_canceled": False}
    raw = str(payment_result)
    for p in ['status":2', "status=2", "已取消", "cancel"]:
        if p.lower() in raw.lower():
            info["is_canceled"] = True
            info["status"] = 2
            break
    try:
        if isinstance(payment_result, dict):
            info["money"] = float(
                payment_result.get("Money", 0) or payment_result.get("money", 0)
            )
            if not info["is_canceled"]:
                info["status"] = 1.0
        elif "收款金额￥" in raw:
            info["money"] = float(raw.split("收款金额￥")[1].split("\n")[0])
            info["status"] = 1.0
    except Exception:
        pass
    return info


def verify_payment(info: Dict[str, Any], expected: Decimal) -> str:
    if info["money"] is None:
        return "failed"
    if info["is_canceled"] or info["status"] == 2:
        return "canceled"
    if abs(Decimal(str(info["money"])) - expected) > Decimal("0.01"):
        return "insufficient"
    return "success"


def process_manage() -> None:
    phones = get_user_phones()
    if not phones:
        reply_error("暂无账号，请先登录")
        return
    authorized_count = count_authorized_accounts(phones)
    unauthorized_count = len(phones) - authorized_count
    user_coin = middleware.bucketGet("dd_sign_points", userid) or "0"
    menu = (
        "=====壹品仓管理=====\n"
        f"📱 绑定账号: {len(phones)}个\n"
        f"✅ 已授权: {authorized_count}个\n"
        f"⏰ 未授权: {unauthorized_count}个\n"
        f"📊 当前积分: {user_coin}\n"
        "--------------------\n"
        f"{format_account_list(phones)}\n"
        "--------------------\n"
        "[序号] 选择指定账号授权\n"
        "[0] 所有账号授权\n"
        "[00] 未授权账号授权\n"
        "[d] 删除账号\n"
        "支持格式: 1 或 1,3 或 2-4\n"
        "回复序号选择(q退出)\n"
        "===================="
    )
    sender.reply(menu)
    c = sender.input(60000, 1, False)
    if not c or c.lower() == "q":
        sender.reply("✅ 已取消")
        return
    c = c.strip().lower()
    config = get_config()
    if c == "0":
        authorize_accounts(phones)
        return
    if c == "00":
        selected = [p for p in phones if not is_authorized(p)]
        authorize_accounts(selected)
        return
    if c == "d":
        sender.reply("请输入要删除的账号序号(如 1,3-5)，回复q退出")
        d = sender.input(60000, 1, False)
        if not d or d.lower() == "q":
            sender.reply("✅ 已取消")
            return
        indices = parse_selection(d, len(phones))
        if indices is None:
            reply_error("格式错误")
            return
        for idx in sorted(indices, reverse=True):
            del_account(phones[idx], userid)
        sender.reply("✅ 删除完成")
        return
    indices = parse_selection(c, len(phones))
    if indices is None:
        reply_error("格式错误")
        return
    selected = [phones[i] for i in indices]
    authorize_accounts(selected)


def process_query() -> None:
    phones = get_user_phones()
    if not phones:
        reply_error("暂无账号")
        return
    lines = [f"📱 绑定账号: {len(phones)}个", "--------------------"]
    for i, phone in enumerate(phones, 1):
        token_data = get_token(phone)
        token = token_data.get("token", "") if token_data else ""
        if not token:
            lines.append(f"[{i}] {mask_phone(phone)}")
            lines.append("    ❌ 查询失败: token为空")
            continue

        result = get_sign_head_data(token)
        if not result.get("ok"):
            lines.append(f"[{i}] {mask_phone(phone)}")
            lines.append(f"    ❌ 查询失败: {result.get('msg', '查询失败')}")
            continue

        data = result.get("data")
        if not isinstance(data, dict):
            lines.append(f"[{i}] {mask_phone(phone)}")
            lines.append("    ❌ 查询失败: 返回数据异常")
            continue

        days = get_continuous_sign_days(data)
        today_status = "今日已签到" if str(data.get("isSignIn")) == "1" else "今日未签到"
        month_acc_days = data.get("monthAccDays", 0)
        year_acc_days = data.get("yearAccDays", 0)
        lines.append(f"[{i}] {mask_phone(phone)}")
        lines.append(f"    🔥 连续签到: {days}天")
        lines.append(f"    📅 本月累计: {month_acc_days}天")
        lines.append(f"    📆 本年累计: {year_acc_days}天")
        lines.append(f"    ✅ 今日状态: {today_status}")
    sender.reply(render_block("壹品仓查询", lines))


def process_authorize_admin() -> None:
    if not sender.isAdmin():
        reply_error("无管理员权限")
        return
    phones = get_user_phones()
    if not phones:
        reply_error("暂无账号")
        return
    authorize_accounts(phones)


def process_sign_in() -> None:
    phones = get_user_phones()
    if not phones:
        reply_error("暂无账号")
        return
    sign_in_accounts(phones)


def process_clean() -> None:
    if not sender.isAdmin():
        reply_error("无管理员权限")
        return
    try:
        users = middleware.bucketAllKeys(bucket=BUCKET_USER) or []
    except Exception:
        users = []
    if not users:
        reply_error("无用户数据")
        return
    sender.reply(
        render_block(
            "壹品仓清理",
            [
                "🔍 正在检查所有用户账号状态...",
            ],
        )
    )
    current_date = datetime.now().date()
    total_accounts = warning_count = notified_users = 0
    unauth_count = expired_count = auth_error_count = deleted_count = 0
    for uid in users:
        phones = get_user_phones(uid)
        if not phones:
            continue
        expired_phones = []
        warning_phones = []
        for phone in phones:
            total_accounts += 1
            expire_str = get_auth(phone)
            if not expire_str:
                expired_phones.append((phone, "unauth", "未授权"))
                continue
            try:
                expire_date = datetime.strptime(expire_str, "%Y-%m-%d").date()
                days_left = (expire_date - current_date).days
                if days_left < 0:
                    expired_phones.append(
                        (phone, "expired", f"已过期{abs(days_left)}天")
                    )
                elif days_left <= 3:
                    warning_phones.append((phone, f"剩余{days_left}天"))
            except Exception:
                expired_phones.append((phone, "error", "授权异常"))
        for phone, reason, _ in expired_phones:
            del_account(phone, uid)
            deleted_count += 1
            if reason == "unauth":
                unauth_count += 1
            elif reason == "expired":
                expired_count += 1
            else:
                auth_error_count += 1
        if warning_phones:
            warning_count += len(warning_phones)
            account_msgs = [
                f"📱 {mask_phone(p)}\n❌ 授权即将过期({r})，请续费"
                for p, r in warning_phones
            ]
            notify_msg = (
                "=====壹品仓账号通知=====\n"
                + "\n-------------------\n".join(account_msgs)
                + "\n===================="
            )
            push_ok = False
            try:
                middleware.push("wx", "", uid, "账号状态提醒", notify_msg)
                push_ok = True
            except Exception:
                pass
            try:
                middleware.push("qq", "", uid, "账号状态提醒", notify_msg)
                push_ok = True
            except Exception:
                pass
            if push_ok:
                notified_users += 1
    sender.reply(
        render_block(
            "壹品仓清理完成",
            [
                f"👥 影响用户: {len(users)}",
                f"📱 检查账号: {total_accounts}",
                f"🗑️ 移除绑定: {deleted_count}",
                f"❌ 未授权清理: {unauth_count}",
                f"⏰ 过期清理: {expired_count}",
                f"🚫 授权异常清理: {auth_error_count}",
                f"⚠️ 临期提醒: {warning_count}",
                f"📤 已推送用户: {notified_users}",
            ],
        )
    )


def show_tutorial() -> None:
    sender.reply(
        render_block(
            "壹品仓教程",
            [
                "1. 发送【壹品仓登录】绑定账号",
                "2. 发送【壹品仓管理】进行授权或删除",
                "3. 发送【壹品仓查询】查看签到数据",
                "4. 发送【壹品仓签到】执行签到",
                "5. 管理员可用【壹品仓清理】",
                "可用指令: 壹品仓登录 / 壹品仓查询 / 壹品仓管理 / 壹品仓签到 / 壹品仓授权 / 壹品仓清理 / 壹品仓教程",
            ],
        )
    )


def run_tasks() -> None:
    """一键运行：遍历所有用户，对所有已授权且未到期的账号执行签到"""
    admin_id = middleware.bucketGet("G_YPC", "admin_id") or "1603960061"
    try:
        all_user_ids = middleware.bucketAllKeys(bucket=BUCKET_USER) or []
    except Exception:
        all_user_ids = []
    if not all_user_ids:
        sender.reply("❌ 暂无用户数据")
        return
    all_authorized_phones = []
    user_count = 0
    for uid in all_user_ids:
        phones = get_user_phones(uid)
        authorized = [p for p in phones if is_authorized(p)]
        if authorized:
            user_count += 1
            all_authorized_phones.extend(authorized)
    if not all_authorized_phones:
        sender.reply("❌ 暂无已授权且未到期的账号")
        return
    sender.reply(
        render_block(
            "壹品仓一键运行",
            [
                f"👥 涉及用户: {user_count}",
                f"📱 授权账号: {len(all_authorized_phones)}",
                "🔄 开始批量签到...",
            ],
        )
    )
    sign_in_accounts(all_authorized_phones)


def main() -> None:
    try:
        msg = sender.getMessage().strip()
    except Exception:
        msg = ""
    if re.match(r"^(壹品仓|ypc)(登录|登陆)$|^登(录|陆)(壹品仓|ypc)$", msg):
        process_login()
    elif re.match(r"^(壹品仓|ypc)(查询|管理)$|^(查询|管理)(壹品仓|ypc)$", msg):
        process_manage() if "管理" in msg else process_query()
    elif "授权" in msg:
        process_authorize_admin()
    elif "清理" in msg:
        process_clean()
    elif "教程" in msg:
        show_tutorial()
    elif "签到" in msg:
        process_sign_in()
    elif "一键运行" in msg:
        run_tasks()
    else:
        sender.setContinue()


main()
