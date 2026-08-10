# [title: dd_018_得间]
# [language: python]
# [open_source: false]
# [version: 1.0.1]
# [author: dandan8]
# [platform: qq,wx,tg,wxmp]
# [public: true]
# [price: 30.00]
# [service: QQ群1067957630]
# [rule: ^(得间|得间小说|dj)(教程|登录|查询|管理|授权|清理|统计|同步|检测)$]
# [cron: 0 9 * * *]
# [description: 得间免费小说账号登录、授权管理与青龙同步]
# [param: {"key":"dd_dejian_config.ql_config","name":"青龙面板配置","placeholder":"青龙地址丨应用ID丨应用密钥","desc":"用于同步 DD_DJ_COOKIE 环境变量"}]
# [param: {"key":"dd_dejian_config.ql_env_name","name":"青龙变量名","placeholder":"DD_DJ_COOKIE","desc":"默认 DD_DJ_COOKIE"}]
# [param: {"key":"dd_dejian_config.coin_price","name":"单账号每日积分","placeholder":"5","desc":"每个账号授权一天需要多少积分，0 表示免费授权"}]
# [param: {"key":"dd_dejian_config.coin_bucket","name":"积分数据桶","placeholder":"","desc":"开启积分授权时填写"}]
# [param: {"key":"dd_dejian_config.expire_notify_enabled","name":"到期提醒","placeholder":"true","desc":"true/false"}]
# [param: {"key":"dd_dejian_config.expire_notify_days","name":"提醒提前天数","placeholder":"3","desc":"默认 3"}]
# [param: {"key":"dd_dejian_config.proxy_api_url","name":"代理提取链接","placeholder":"","desc":"填写代理api链接(一次一条丨http/https丨txt格式丨白名单验证)，不填为禁用代理（建议填写无限代理池）"}]
# [param: {"key":"dd_dejian_config.sms_wait_timeout","name":"验证码等待秒","placeholder":"180","desc":"默认 180"}]
# [param: {"key":"dd_dejian_config.admin_ids","name":"管理员用户ID","placeholder":"","desc":"逗号分隔，sender.isAdmin() 仍然有效"}]

import base64
import hashlib
import json
import os
import random
import re
import string
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import quote, urlencode

import requests

try:
    import middleware
except Exception:
    middleware = None


PLUGIN_TITLE = "dd_018_得间"
PLUGIN_NAME = "得间免费小说"
ENV_NAME_DEFAULT = "DD_DJ_COOKIE"

BUCKET_CONFIG = "dd_dejian_config"
BUCKET_USER = "dd_dejian_user"
BUCKET_ACCOUNT = "dd_dejian_account"
BUCKET_SESSION = "dd_dejian_session"
BUCKET_AUTH = "dd_dejian_auth"
BUCKET_SYNC = "dd_dejian_sync"
BUCKET_NOTIFY = "dd_dejian_notify"
BUCKET_DEVICE = "dd_dejian_device"
BUCKET_AUDIT = "dd_dejian_audit"

SIGN_SERVER = os.environ.get("DJ_SIGN_SERVER", "http://43.143.43.159:2001/sign.php")
API_KEY = os.environ.get("DJ_API_KEY", "2026-06-18")
DJ_BASE = "https://dj.palmestore.com"
WELFARE_BASE = "https://welfare-dj.palmestore.com"


class PluginError(Exception):
    pass


def now_ts():
    return int(time.time())


def today():
    return time.strftime("%Y-%m-%d")


def now_text():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def safe_json_loads(raw, default=None):
    if raw is None or raw == "":
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(str(raw))
    except Exception:
        return default


def json_dumps(data):
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def bucket_get(bucket, key, default=""):
    if middleware is None:
        return default
    try:
        value = middleware.bucketGet(bucket, key)
        return default if value is None else value
    except Exception:
        return default


def bucket_set(bucket, key, value):
    if middleware is None:
        return False
    try:
        middleware.bucketSet(bucket, key, value)
        return True
    except Exception:
        return False


def bucket_del(bucket, key):
    if middleware is None:
        return False
    try:
        middleware.bucketDel(bucket, key)
        return True
    except Exception:
        return False


def bucket_keys(bucket):
    if middleware is None:
        return []
    try:
        keys = middleware.bucketAllKeys(bucket)
        if keys is None:
            return []
        if isinstance(keys, str):
            parsed = safe_json_loads(keys, None)
            if isinstance(parsed, list):
                return parsed
            return [k for k in keys.splitlines() if k.strip()]
        return list(keys)
    except Exception:
        return []


def bucket_get_json(bucket, key, default=None):
    return safe_json_loads(bucket_get(bucket, key, ""), default)


def bucket_set_json(bucket, key, value):
    return bucket_set(bucket, key, json_dumps(value))


def parse_int(value, default=0, minimum=None, maximum=None):
    try:
        n = int(str(value).strip())
    except Exception:
        n = default
    if minimum is not None:
        n = max(minimum, n)
    if maximum is not None:
        n = min(maximum, n)
    return n


def parse_bool(value, default=False):
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "y", "on", "开启")


def parse_decimal(value, default="0"):
    try:
        return Decimal(str(value or default).strip())
    except (InvalidOperation, ValueError):
        return Decimal(default)


def mask_text(text, keep=3):
    text = "" if text is None else str(text)
    if len(text) <= keep * 2:
        return text[:1] + "***" if text else ""
    return text[:keep] + "***" + text[-keep:]


def mask_phone(phone):
    phone = "" if phone is None else str(phone)
    if re.fullmatch(r"\d{11}", phone):
        return phone[:3] + "****" + phone[-4:]
    return mask_text(phone, 2)


def short_error(exc):
    text = str(exc)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer ***", text)
    text = re.sub(r"(kt|token|zyeid)=([^&\s]+)", r"\1=***", text, flags=re.I)
    text = re.sub(r"(sign|timestamp|phone|p1|p7|p31|p35)=([^&\s]+)", r"\1=***", text, flags=re.I)
    return text[:120]


def response_json(resp, label):
    try:
        data = resp.json()
    except Exception:
        text = (getattr(resp, "text", "") or "").strip()
        text = re.sub(r"Bearer\s+[A-Za-z0-9._\-]+", "Bearer ***", text)
        text = re.sub(r"(kt|token|zyeid|sign|timestamp)=([^&\s]+)", r"\1=***", text, flags=re.I)
        if not text:
            text = "<空响应>"
        raise PluginError("%s返回非JSON：HTTP %s，%s" % (label, getattr(resp, "status_code", "?"), text[:120]))
    if getattr(resp, "status_code", 200) >= 400:
        msg = data.get("msg") or data.get("message") or data.get("error") or data
        raise PluginError("%s请求失败：HTTP %s，%s" % (label, resp.status_code, msg))
    return data


def response_json_with_context(resp, label, context=""):
    try:
        return response_json(resp, label)
    except PluginError as exc:
        if context:
            raise PluginError("%s（%s）" % (str(exc), context))
        raise


def account_display(account):
    return mask_phone(account.get("phone") or account.get("remark") or account.get("usr") or account.get("account_key"))


def account_phone(account=None, session=None):
    account = account or {}
    session = session or {}
    for value in (account.get("phone"), session.get("phone"), account.get("remark")):
        value = str(value or "").strip()
        if value:
            return value
    return ""


def account_remark(account=None, session=None):
    return account_phone(account, session) or str((account or {}).get("usr") or (session or {}).get("usr") or "").strip()


def config_read_key(key, default=""):
    value = bucket_get(BUCKET_CONFIG, key, None)
    if value not in (None, ""):
        return value
    dotted = "%s.%s" % (BUCKET_CONFIG, key)
    value = bucket_get(BUCKET_CONFIG, dotted, None)
    if value not in (None, ""):
        return value
    if middleware is not None and hasattr(middleware, "getParam"):
        try:
            value = middleware.getParam(dotted)
            if value not in (None, ""):
                return value
        except Exception:
            pass
    return default


def parse_ql_config(raw):
    raw = (raw or "").strip()
    if not raw:
        return None
    parts = re.split(r"[丨|]", raw)
    parts = [p.strip() for p in parts]
    if len(parts) < 3 or not parts[0] or not parts[1] or not parts[2]:
        raise PluginError("青龙配置格式应为：青龙地址丨应用ID丨应用密钥")
    return {"url": parts[0].rstrip("/"), "client_id": parts[1], "client_secret": parts[2]}


def get_config():
    cfg = {
        "ql_config_raw": config_read_key("ql_config", ""),
        "env_name": config_read_key("ql_env_name", ENV_NAME_DEFAULT) or ENV_NAME_DEFAULT,
        "coin_price": parse_decimal(config_read_key("coin_price", "5")),
        "coin_bucket": config_read_key("coin_bucket", ""),
        "expire_notify_enabled": parse_bool(config_read_key("expire_notify_enabled", "true"), True),
        "expire_notify_days": parse_int(config_read_key("expire_notify_days", "3"), 3, 0, 30),
        "proxy_api_url": config_read_key("proxy_api_url", ""),
        "proxy_fail_limit": 3,
        "allow_direct_on_proxy_fail": False,
        "request_timeout": 15,
        "sms_wait_timeout": parse_int(config_read_key("sms_wait_timeout", "180"), 180, 30, 600),
        "ql_sync_only_authorized": True,
        "admin_ids": config_read_key("admin_ids", ""),
    }
    try:
        cfg["ql_config"] = parse_ql_config(cfg["ql_config_raw"])
    except PluginError:
        cfg["ql_config"] = None
    return cfg


def sender_reply(sender, text):
    try:
        sender.reply(str(text))
    except Exception:
        pass


def format_panel(title, lines):
    body = ["=====%s=====" % title]
    body.extend(lines)
    body.append("==================")
    return "\n".join(body)


def reply_panel(sender, title, lines):
    sender_reply(sender, format_panel(title, lines))


def sender_input(sender, timeout_seconds=180):
    timeout_ms = int(timeout_seconds) * 1000
    value = None
    try:
        value = sender.input(timeout_ms, 0, False)
    except TypeError:
        try:
            value = sender.listen(timeout_ms)
        except Exception:
            value = None
    except Exception:
        value = None
    if value is None:
        return ""
    return str(value).strip()


def get_user_id(sender):
    try:
        return str(sender.getUserID())
    except Exception:
        return ""


def is_admin_user(sender, cfg):
    try:
        if sender.isAdmin():
            return True
    except Exception:
        pass
    uid = get_user_id(sender)
    ids = [x.strip() for x in str(cfg.get("admin_ids") or "").split(",") if x.strip()]
    return uid in ids


def cloud_sign(data, cfg=None):
    session = requests.Session()
    session.trust_env = False
    resp = session.post(
        SIGN_SERVER,
        json=data,
        timeout=(cfg or {}).get("request_timeout", 30),
        headers={"Authorization": "Bearer %s" % API_KEY, "Content-Type": "application/json"},
    )
    result = response_json(resp, "签名服务")
    if result.get("code") != 0:
        raise PluginError("签名服务错误：%s" % result.get("msg"))
    return result.get("data") or {}


def rsa_sha1_sign_cloud(params, cfg=None):
    timestamp = str(int(time.time() * 1000))
    data = cloud_sign({"type": "rsa-sha1", "params": params, "timestamp": timestamp}, cfg)
    return data["sign"], data["timestamp"]


def rsa_encrypt_cloud(plaintext, cfg=None):
    data = cloud_sign({"type": "rsa-encrypt", "plaintext": plaintext}, cfg)
    return data["encrypted"]


DEVICE_LIBRARY = [
    {"p16": "22041219C", "p34": "Redmi", "firm": "Redmi", "d1": "5.5.9.2", "build": "SP1A.210812.016", "android": "12", "model": "Redmi Note 11T Pro"},
    {"p16": "2201117TG", "p34": "Redmi", "firm": "Redmi", "d1": "5.5.9.2", "build": "SKQ1.211006.001", "android": "12", "model": "Redmi Note 11 Pro"},
    {"p16": "M2104K10AC", "p34": "Redmi", "firm": "Redmi", "d1": "5.5.9.2", "build": "SP1A.210812.016", "android": "12", "model": "Redmi Note 10 Pro"},
    {"p16": "23127PN0CC", "p34": "Xiaomi", "firm": "Xiaomi", "d1": "5.5.9.2", "build": "TKQ1.221114.001", "android": "13", "model": "Xiaomi 14"},
    {"p16": "2304FPN6DC", "p34": "Xiaomi", "firm": "Xiaomi", "d1": "5.5.9.2", "build": "TKQ1.221114.001", "android": "13", "model": "Xiaomi 13"},
    {"p16": "2210132C", "p34": "Redmi", "firm": "Redmi", "d1": "5.5.9.2", "build": "SKQ1.221019.001", "android": "13", "model": "Redmi K60"},
    {"p16": "22081212C", "p34": "Redmi", "firm": "Redmi", "d1": "5.5.8.2", "build": "SKQ1.220821.001", "android": "12", "model": "Redmi K50"},
    {"p16": "PGKM10", "p34": "OPPO", "firm": "OPPO", "d1": "5.5.9.2", "build": "SP1A.210812.016", "android": "12", "model": "OPPO Reno8 Pro"},
    {"p16": "PHJ110", "p34": "OPPO", "firm": "OPPO", "d1": "5.5.9.2", "build": "TP1A.220905.001", "android": "13", "model": "OPPO A1 Pro"},
    {"p16": "PESM10", "p34": "OPPO", "firm": "OPPO", "d1": "5.5.8.2", "build": "SP1A.210812.016", "android": "12", "model": "OPPO Reno7"},
    {"p16": "RMX3700", "p34": "realme", "firm": "realme", "d1": "5.5.9.2", "build": "TP1A.220905.001", "android": "13", "model": "realme GT Neo5 SE"},
    {"p16": "V2254A", "p34": "vivo", "firm": "vivo", "d1": "5.5.9.2", "build": "TP1A.220624.014", "android": "13", "model": "vivo S16"},
    {"p16": "V2227A", "p34": "vivo", "firm": "vivo", "d1": "5.5.9.2", "build": "SP1A.210812.016", "android": "12", "model": "vivo S15"},
    {"p16": "V2241A", "p34": "vivo", "firm": "vivo", "d1": "5.5.9.2", "build": "TP1A.220624.014", "android": "13", "model": "vivo X90"},
    {"p16": "V2157A", "p34": "iQOO", "firm": "iQOO", "d1": "5.5.8.2", "build": "SP1A.210812.016", "android": "12", "model": "iQOO Neo6"},
    {"p16": "V2304A", "p34": "iQOO", "firm": "iQOO", "d1": "5.5.9.2", "build": "TKQ1.221114.001", "android": "13", "model": "iQOO 12"},
    {"p16": "SM-A5360", "p34": "Samsung", "firm": "Samsung", "d1": "5.5.9.2", "build": "SP1A.210812.016", "android": "12", "model": "Samsung Galaxy A53"},
    {"p16": "SM-S9110", "p34": "Samsung", "firm": "Samsung", "d1": "5.5.9.2", "build": "TP1A.220624.014", "android": "13", "model": "Samsung Galaxy S23"},
    {"p16": "ANY-AN00", "p34": "HONOR", "firm": "HONOR", "d1": "5.5.9.2", "build": "SP1A.210812.016", "android": "12", "model": "HONOR 70"},
    {"p16": "ALI-AN00", "p34": "HONOR", "firm": "HONOR", "d1": "5.5.9.2", "build": "TKQ1.221114.001", "android": "13", "model": "HONOR X50"},
]
APP_VERSIONS = ["5.5.9.2", "5.5.8.2", "5.5.7.2", "5.5.6.2", "5.5.5.2"]
DEVICE_PROFILE_BY_P16 = {item["p16"]: item for item in DEVICE_LIBRARY}


def gen_device_id():
    return hashlib.md5(uuid.uuid4().bytes).hexdigest()[:16]


def gen_p1():
    return str(int(time.time() * 1000)) + "".join(random.choices(string.digits, k=6))


def p7_encrypt(src):
    if not src:
        return "__"
    result = "__"
    for ch in str(src):
        if "0" <= ch <= "9":
            d = int(ch)
            result += str(((10 - d if d != 0 else 0) * 3) % 10)
        else:
            result += ch
    return result


def gen_smboxid():
    raw = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    return base64.b64encode(raw.encode()).decode()[:88]


def des_cbc_pkcs5_encrypt_base64(plaintext, key_bytes):
    raw = plaintext.encode()
    pad_len = 8 - len(raw) % 8
    padded = raw + bytes([pad_len] * pad_len)
    try:
        from Crypto.Cipher import DES
        return base64.b64encode(DES.new(key_bytes, DES.MODE_CBC, key_bytes).encrypt(padded)).decode()
    except Exception as crypto_exc:
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
            des_algorithm = getattr(algorithms, "DES", None)
            if des_algorithm is None:
                try:
                    from cryptography.hazmat.decrepit.ciphers import algorithms as decrepit_algorithms
                    des_algorithm = getattr(decrepit_algorithms, "DES", None)
                except Exception:
                    des_algorithm = None
            if des_algorithm is None:
                raise PluginError("缺少 DES 加密依赖，请安装 pycryptodome 或使用支持 DES 的 cryptography")
            cipher = Cipher(des_algorithm(key_bytes), modes.CBC(key_bytes))
            encryptor = cipher.encryptor()
            return base64.b64encode(encryptor.update(padded) + encryptor.finalize()).decode()
        except PluginError:
            raise
        except Exception as exc:
            raise PluginError("DES 加密失败：%s" % short_error(exc or crypto_exc))


def pick_device():
    device = random.choice(DEVICE_LIBRARY).copy()
    device["d1"] = random.choice(APP_VERSIONS)
    return device


def build_login_device_params(phone):
    device = pick_device()
    android_id = gen_device_id()
    p7_value = p7_encrypt(android_id)
    return {
        "zyeid": str(uuid.uuid4()), "usr": "", "ku": "", "kt": "",
        "pc": "10", "p1": p7_value, "p2": "124012", "p3": "25295056", "p4": "501656",
        "p5": "19", "p7": p7_value, "p9": "1", "p12": "",
        "p16": device["p16"], "p21": "99", "p22": "12", "p25": "25295256", "p26": "31",
        "p28": gen_device_id(), "p29": "zy4248ba", "p30": "",
        "p31": p7_value, "p33": "com.chaozh.iReader.dj",
        "p34": device["p34"], "firm": device["firm"], "d1": device["d1"], "rgt": "7",
        "_phone": phone, "_model": device["model"], "_build": device["build"], "_android": device["android"],
    }


def device_cache_key(phone):
    return hashlib.sha1(str(phone).encode("utf-8")).hexdigest()[:24]


def normalize_login_device_params(device_params):
    device_params = dict(device_params or {})
    p7_value = device_params.get("p7", "")
    if p7_value:
        if not str(device_params.get("p1", "")).startswith("__"):
            device_params["p1"] = p7_value
        if device_params.get("p31") != p7_value:
            device_params["p31"] = p7_value
    device_params.setdefault("zyeid", str(uuid.uuid4()))
    device_params.setdefault("usr", "")
    device_params.setdefault("ku", "")
    device_params.setdefault("kt", "")
    device_params.setdefault("rgt", "7")
    return device_params


def load_device_params(phone, cfg=None):
    if cfg is not None and cfg.get("_login_device_params"):
        return cfg["_login_device_params"]
    key = device_cache_key(phone)
    device_params = bucket_get_json(BUCKET_DEVICE, key, None)
    if not isinstance(device_params, dict):
        device_params = build_login_device_params(phone)
        bucket_set_json(BUCKET_DEVICE, key, device_params)
    else:
        normalized = normalize_login_device_params(device_params)
        if normalized != device_params:
            device_params = normalized
            bucket_set_json(BUCKET_DEVICE, key, device_params)
    if cfg is not None:
        cfg["_login_device_params"] = device_params
    return device_params


def build_native_ua_from_device(device_params):
    profile = DEVICE_PROFILE_BY_P16.get(device_params.get("p16", ""))
    android = device_params.get("_android") or (profile or {}).get("android") or "12"
    model = device_params.get("p16", "M2104K10AC")
    build = device_params.get("_build") or (profile or {}).get("build") or "SP1A.210812.016"
    return "Dalvik/2.1.0 (Linux; U; Android %s; %s Build/%s)" % (android, model, build)


def login_url_params(device):
    params = {k: v for k, v in (device or {}).items() if not k.startswith("_") and v is not None}
    return urlencode(params, quote_via=quote)


def fetch_proxy(cfg):
    url = (cfg.get("proxy_api_url") or "").strip()
    if not url:
        return None
    s = requests.Session()
    s.trust_env = False
    try:
        resp = s.get(url, timeout=10)
        text = resp.text.strip()
        data = safe_json_loads(text, None)
        proxy = ""
        if isinstance(data, dict):
            for key in ("proxy", "http", "https", "addr", "ipport", "server"):
                if data.get(key):
                    proxy = str(data[key]).strip()
                    break
            if not proxy and data.get("ip") and data.get("port"):
                proxy = "%s:%s" % (data["ip"], data["port"])
            if not proxy:
                for key in ("data", "result", "list"):
                    nested = data.get(key)
                    if isinstance(nested, list) and nested:
                        return normalize_proxy(str(nested[0]))
                    if isinstance(nested, dict):
                        for sub_key in ("proxy", "http", "https", "addr", "ipport", "server"):
                            if nested.get(sub_key):
                                return normalize_proxy(str(nested[sub_key]))
                        if nested.get("ip") and nested.get("port"):
                            return normalize_proxy("%s:%s" % (nested["ip"], nested["port"]))
        else:
            proxy = text.splitlines()[0] if text else ""
        return normalize_proxy(proxy)
    except Exception as exc:
        if cfg.get("allow_direct_on_proxy_fail"):
            return None
        raise PluginError("代理提取失败：%s" % short_error(exc))


def request_proxy(cfg):
    if "_fixed_proxy" in cfg:
        return cfg.get("_fixed_proxy")
    return fetch_proxy(cfg)


def normalize_proxy(proxy):
    proxy = (proxy or "").strip()
    if not proxy:
        return None
    if not proxy.startswith(("http://", "https://")):
        proxy = "http://" + proxy
    return {"http": proxy, "https": proxy}


def describe_network_error(exc):
    text = short_error(exc)
    raw = str(exc)
    if "ProxyError" in raw or "proxy" in raw.lower():
        return "代理连接失败：%s" % text
    if "NameResolutionError" in raw or "getaddrinfo" in raw:
        return "DNS解析失败：%s" % text
    if "ConnectTimeout" in raw or "ReadTimeout" in raw or "timed out" in raw.lower():
        return "请求超时：%s" % text
    if "SSLError" in raw or "CERTIFICATE" in raw:
        return "HTTPS证书或TLS连接失败：%s" % text
    if "ConnectionError" in raw or "Max retries exceeded" in raw:
        return "网络连接失败：%s" % text
    return text


def post_dj_with_proxy_fallback(url, data, timeout, headers, cfg, label):
    session = requests.Session()
    session.trust_env = False
    proxies = request_proxy(cfg)
    try:
        return session.post(url, data=data, timeout=timeout, headers=headers, proxies=proxies)
    except requests.RequestException as first_exc:
        if proxies:
            try:
                return session.post(url, data=data, timeout=timeout, headers=headers, proxies=None)
            except requests.RequestException as direct_exc:
                raise PluginError("%s失败：代理失败后直连仍失败；%s" % (label, describe_network_error(direct_exc)))
        raise PluginError("%s失败：%s" % (label, describe_network_error(first_exc)))


def send_sms(phone, cfg):
    device_params = load_device_params(phone, cfg)
    device = {k: v for k, v in device_params.items() if not k.startswith("_")}
    encrypted_phone = rsa_encrypt_cloud(phone, cfg)
    imei_val = device.get("p7", p7_encrypt(gen_device_id()))
    sign_params = {
        "channelId": "124012", "device": device["p16"], "flag": "1",
        "imei": imei_val, "phone": encrypted_phone,
        "sendType": "0", "times": "1", "versionId": "25295056",
    }
    sign, timestamp = rsa_sha1_sign_cloud(sign_params, cfg)
    body = {
        "phone": encrypted_phone, "device": device["p16"], "times": "1",
        "channelId": "124012", "versionId": "25295056", "imei": imei_val,
        "sendType": "0", "flag": "1", "sign": sign, "timestamp": timestamp,
    }
    ua = "Dalvik/2.1.0 (Linux; U; Android %s; %s Build/%s)" % (
        device_params.get("_android", "12"),
        device["p16"],
        device_params.get("_build", "SP1A.210812.016"),
    )
    resp = post_dj_with_proxy_fallback(
        DJ_BASE + "/dj_user/out/sms/sendSms/V2?" + login_url_params(device),
        body,
        cfg["request_timeout"],
        {"User-Agent": ua},
        cfg,
        "得间短信接口",
    )
    return response_json(resp, "得间短信接口")


def login_by_phone(phone, code, cfg):
    from Crypto.Cipher import DES as DES_Cipher
    from Crypto.Util.Padding import pad

    des_key_str = "".join(random.choices(string.digits, k=8))
    des_key_bytes = des_key_str.encode()[:8]

    cipher = DES_Cipher.new(des_key_bytes, DES_Cipher.MODE_CBC, iv=des_key_bytes)
    pcode_json = json.dumps({"phone": phone, "pCode": code})
    data_encrypted = base64.b64encode(cipher.encrypt(pad(pcode_json.encode(), 8))).decode()
    des_key_encrypted = rsa_encrypt_cloud(des_key_str, cfg)
    p_info = json.dumps({"DesKey": des_key_encrypted, "Data": data_encrypted})

    device_params = load_device_params(phone, cfg)
    device = {k: v for k, v in device_params.items() if not k.startswith("_")}
    encrypted_phone = rsa_encrypt_cloud(phone, cfg)
    sign_params = {
        "channelId": "124012", "device": device["p16"],
        "imei": device.get("p7", ""),
        "phone": encrypted_phone, "versionId": "25295056",
    }
    sign, timestamp = rsa_sha1_sign_cloud(sign_params, cfg)
    data = {
        "phone": encrypted_phone, "channelId": "124012", "versionId": "25295056",
        "device": device["p16"], "imei": device.get("p7", ""), "userName": phone,
        "pInfo": p_info, "utdId": device.get("p1", ""), "loginSource": "手动登录",
        "timestamp": timestamp, "sign": sign,
    }
    url_params = login_url_params(device)
    resp = post_dj_with_proxy_fallback(
        DJ_BASE + "/dj_user/out/login/loginByPhoneV3?" + url_params,
        data,
        cfg["request_timeout"],
        {"User-Agent": build_native_ua_from_device(device_params)},
        cfg,
        "得间登录接口",
    )
    result = response_json(resp, "得间登录接口")
    if result.get("code") != 0:
        raise PluginError(result.get("msg") or "登录失败")
    body = result.get("body") or {}
    usr = body.get("name") or body.get("userName") or body.get("usr") or ""
    token = body.get("token") or body.get("kt") or ""
    zyeid = body.get("zyeId") or body.get("zyeid") or body.get("zyeID") or ""
    if not usr or not token or not zyeid:
        raise PluginError("登录响应缺少账号、token 或 zyeid")
    session_device = {k: v for k, v in device_params.items() if k != "_phone"}
    session_device["p35"] = device.get("p35") or gen_smboxid()
    return {
        "phone": phone,
        "usr": usr,
        "ku": body.get("ku") or body.get("userName") or usr,
        "kt": token,
        "zyeid": zyeid,
        "authToken": body.get("authToken", ""),
        "uid": body.get("uid", ""),
        "signUser": body.get("signUser", ""),
        "regType": body.get("regType", ""),
        "usrMsg": body.get("usrMsg") or {},
        "login_time": now_ts(),
        "login_date": today(),
        "device": session_device,
        "login_body": body,
        "login_response": result,
    }


def make_account_key(session):
    session = normalize_session_data(session)
    phone = str(session.get("phone") or "").strip()
    if phone:
        return phone
    usr = str(session.get("usr") or "").strip()
    if usr:
        return usr
    raw = "%s:%s" % (session.get("phone", ""), session.get("kt", ""))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def get_user_account_keys(user_id):
    data = bucket_get_json(BUCKET_USER, str(user_id), [])
    return data if isinstance(data, list) else []


def save_user_account_keys(user_id, keys):
    clean = []
    for key in keys:
        if key and key not in clean:
            clean.append(key)
    return bucket_set_json(BUCKET_USER, str(user_id), clean)


def get_account(account_key):
    data = bucket_get_json(BUCKET_ACCOUNT, account_key, None)
    return data if isinstance(data, dict) else None


def normalize_session_data(session, phone_hint=""):
    if not isinstance(session, dict):
        return {}
    data = dict(session)
    login_response = data.get("login_response")
    login_body = data.get("login_body")
    raw_body = data.get("body")
    if not isinstance(login_body, dict):
        login_body = {}
    if isinstance(login_response, dict) and isinstance(login_response.get("body"), dict):
        login_body = dict(login_response["body"], **login_body)
    if isinstance(raw_body, dict):
        login_body = dict(login_body, **raw_body)
        if "login_response" not in data and ("code" in data or "msg" in data):
            data["login_response"] = {
                "code": data.get("code"),
                "msg": data.get("msg"),
                "body": raw_body,
            }
    if login_body:
        data["login_body"] = login_body
    if not data.get("phone") and re.fullmatch(r"\d{11}", str(phone_hint or "")):
        data["phone"] = str(phone_hint)
    if not data.get("phone") and isinstance(login_body.get("usrMsg"), dict):
        data["phone"] = login_body["usrMsg"].get("bindPhone", "")
    if not data.get("usr"):
        data["usr"] = data.get("name") or data.get("userName") or login_body.get("userName") or login_body.get("name") or ""
    if not data.get("ku"):
        data["ku"] = data.get("ku") or login_body.get("ku") or login_body.get("userName") or data.get("userName") or data.get("usr") or ""
    if not data.get("kt"):
        data["kt"] = data.get("token") or login_body.get("token") or ""
    if not data.get("zyeid"):
        data["zyeid"] = data.get("zyeId") or data.get("zyeID") or login_body.get("zyeId") or login_body.get("zyeid") or login_body.get("zyeID") or ""
    for key in ("authToken", "uid", "signUser", "regType", "usrMsg"):
        if not data.get(key) and login_body.get(key):
            data[key] = login_body.get(key)
    device = data.get("device")
    if isinstance(device, dict):
        normalized_device = dict(device)
        if data.get("p35") and not normalized_device.get("p35"):
            normalized_device["p35"] = data.get("p35")
        if not normalized_device.get("p35"):
            normalized_device["p35"] = gen_smboxid()
        profile = DEVICE_PROFILE_BY_P16.get(normalized_device.get("p16", ""))
        if profile:
            normalized_device.setdefault("_android", profile.get("android", ""))
            normalized_device.setdefault("_build", profile.get("build", ""))
            normalized_device.setdefault("_model", profile.get("model", ""))
        data["device"] = normalized_device
    return data


def get_session(account_key):
    data = bucket_get_json(BUCKET_SESSION, account_key, None)
    return normalize_session_data(data) if isinstance(data, dict) else None


def find_account_by_phone(phone):
    phone = str(phone or "").strip()
    if not phone:
        return "", None
    for key in bucket_keys(BUCKET_ACCOUNT):
        account = get_account(str(key))
        if account and account_phone(account) == phone:
            return str(key), account
    return "", None


def migrate_account_key(old_key, new_key):
    if not old_key or not new_key or str(old_key) == str(new_key):
        return
    account = get_account(old_key) or {}
    owner = str(account.get("owner_userid", ""))
    if owner:
        keys = [new_key if str(k) == str(old_key) else k for k in get_user_account_keys(owner)]
        save_user_account_keys(owner, keys)
    for bucket in (BUCKET_SESSION, BUCKET_AUTH, BUCKET_SYNC, BUCKET_NOTIFY):
        raw = bucket_get(bucket, old_key, None)
        if raw not in (None, ""):
            bucket_set(bucket, new_key, raw)
        bucket_del(bucket, old_key)
    bucket_del(BUCKET_ACCOUNT, old_key)


def save_account(user_id, session, source="sms"):
    session = normalize_session_data(session)
    missing = [key for key in ("phone", "usr", "kt", "zyeid") if not session.get(key)]
    if missing:
        raise PluginError("会话字段缺失：%s" % "、".join(missing))
    account_key = make_account_key(session)
    phone = str(session.get("phone") or "").strip()
    legacy_key, legacy_account = find_account_by_phone(phone)
    if legacy_account and str(legacy_account.get("owner_userid")) != str(user_id):
        raise PluginError("该手机号已绑定其他用户")
    if legacy_key and legacy_key != account_key:
        migrate_account_key(legacy_key, account_key)
    exists = get_account(account_key)
    if exists and str(exists.get("owner_userid")) != str(user_id):
        raise PluginError("该得间账号已绑定其他用户")
    remark = phone
    account = {
        "account_key": account_key,
        "owner_userid": str(user_id),
        "remark": remark,
        "phone": session.get("phone", ""),
        "usr": session.get("usr", ""),
        "ku": session.get("ku", session.get("usr", "")),
        "zyeid": session.get("zyeid", ""),
        "login_date": session.get("login_date", today()),
        "created_at": (exists or {}).get("created_at", now_ts()),
        "updated_at": now_ts(),
        "source": source,
    }
    bucket_set_json(BUCKET_ACCOUNT, account_key, account)
    bucket_set_json(BUCKET_SESSION, account_key, session)
    keys = get_user_account_keys(user_id)
    if account_key not in keys:
        keys.append(account_key)
    save_user_account_keys(user_id, keys)
    return account


def delete_account_local(account_key):
    account = get_account(account_key)
    owner = str((account or {}).get("owner_userid", ""))
    if owner:
        keys = [k for k in get_user_account_keys(owner) if k != account_key]
        save_user_account_keys(owner, keys)
    for bucket in (BUCKET_ACCOUNT, BUCKET_SESSION, BUCKET_AUTH, BUCKET_SYNC, BUCKET_NOTIFY):
        bucket_del(bucket, account_key)
    return True


def all_accounts():
    items = []
    for key in bucket_keys(BUCKET_ACCOUNT):
        account = get_account(str(key))
        if account:
            items.append(account)
    return items


def get_auth(account_key):
    data = bucket_get_json(BUCKET_AUTH, account_key, None)
    return data if isinstance(data, dict) else None


def auth_status(account_key):
    auth = get_auth(account_key)
    if not auth:
        return {"status": "none", "text": "未授权", "expire_date": "", "days_left": -1}
    status = auth.get("status", "active")
    expire_date = auth.get("expire_date", "")
    try:
        days_left = (datetime.strptime(expire_date, "%Y-%m-%d").date() - datetime.strptime(today(), "%Y-%m-%d").date()).days
    except Exception:
        days_left = -1
    if status != "active":
        return {"status": status, "text": "已停用" if status == "disabled" else "已过期", "expire_date": expire_date, "days_left": days_left}
    if days_left < 0:
        auth["status"] = "expired"
        auth["last_check_at"] = now_ts()
        bucket_set_json(BUCKET_AUTH, account_key, auth)
        return {"status": "expired", "text": "已过期", "expire_date": expire_date, "days_left": days_left}
    return {"status": "active", "text": "已授权", "expire_date": expire_date, "days_left": days_left}


def set_auth(account_key, days, source, granted_by):
    current = auth_status(account_key)
    base = datetime.strptime(today(), "%Y-%m-%d").date()
    if current["status"] == "active" and current.get("expire_date"):
        try:
            old = datetime.strptime(current["expire_date"], "%Y-%m-%d").date()
            if old > base:
                base = old
        except Exception:
            pass
    expire_date = (base + timedelta(days=max(1, int(days)))).strftime("%Y-%m-%d")
    data = {
        "status": "active",
        "expire_date": expire_date,
        "auth_days": int(days),
        "auth_source": source,
        "granted_by": str(granted_by),
        "granted_at": now_ts(),
        "last_check_at": now_ts(),
    }
    bucket_set_json(BUCKET_AUTH, account_key, data)
    return data


def build_env_value(account, session):
    remark = account_remark(account, session)
    return "%s#%s" % (remark, json_dumps(session))


def validate_qinglong_session(session):
    session = normalize_session_data(session)
    missing = [key for key in ("phone", "usr", "kt", "zyeid") if not session.get(key)]
    if missing:
        raise PluginError("会话字段缺失：%s" % "、".join(missing))
    return session


def build_remarks(account, auth, session=None):
    return "%s：%s|用户：%s|到期：%s|得间管理" % (
        PLUGIN_NAME,
        account_remark(account, session),
        account.get("owner_userid", ""),
        auth.get("expire_date", ""),
    )


def parse_env_id(env):
    return env.get("id") or env.get("_id")


class QingLongAPI:
    def __init__(self, cfg):
        if not cfg.get("ql_config"):
            raise PluginError("未配置青龙面板")
        self.base = cfg["ql_config"]["url"]
        self.client_id = cfg["ql_config"]["client_id"]
        self.client_secret = cfg["ql_config"]["client_secret"]
        self.timeout = cfg.get("request_timeout", 15)
        self.session = requests.Session()
        self.session.trust_env = False
        self.token = ""

    def request(self, method, path, **kwargs):
        if not self.token and not path.startswith("/open/auth/token"):
            self.get_token()
        headers = kwargs.pop("headers", {})
        if self.token:
            headers["Authorization"] = "Bearer %s" % self.token
        resp = self.session.request(method, self.base + path, timeout=self.timeout, headers=headers, **kwargs)
        data = response_json_with_context(resp, "青龙接口", "%s %s" % (method, path))
        if data.get("code") not in (0, 200, None) and data.get("data") is None:
            raise PluginError(data.get("message") or data.get("msg") or "青龙请求失败")
        return data

    def get_token(self):
        path = "/open/auth/token?client_id=%s&client_secret=%s" % (self.client_id, self.client_secret)
        data = self.request("GET", path)
        body = data.get("data") or {}
        self.token = body.get("token") or body.get("access_token") or ""
        if not self.token:
            raise PluginError("青龙 token 获取失败")
        return self.token

    def normalize_envs(self, data):
        body = data.get("data", data)
        if isinstance(body, dict):
            for key in ("data", "list", "envs"):
                if isinstance(body.get(key), list):
                    return body[key]
        if isinstance(body, list):
            return body
        return []

    def get_envs(self, search_value=""):
        params = {"searchValue": search_value} if search_value else {}
        return self.normalize_envs(self.request("GET", "/open/envs", params=params))

    def add_env(self, name, value, remarks):
        payload = [{"name": name, "value": value, "remarks": remarks}]
        data = self.request("POST", "/open/envs", json=payload)
        envs = self.normalize_envs(data)
        return envs[0] if envs else {}

    def update_env(self, env_id, name, value, remarks):
        attempts = []
        if env_id:
            attempts.append(("/open/envs", {"name": name, "value": value, "remarks": remarks, "id": env_id}))
            attempts.append(("/open/envs", {"name": name, "value": value, "remarks": remarks, "_id": env_id}))
            attempts.append(("/open/envs/%s" % env_id, {"name": name, "value": value, "remarks": remarks}))
        else:
            attempts.append(("/open/envs", {"name": name, "value": value, "remarks": remarks}))
        first_exc = None
        for path, payload in attempts:
            try:
                return self.request("PUT", path, json=payload)
            except PluginError as exc:
                if first_exc is None:
                    first_exc = exc
        raise first_exc or PluginError("青龙变量更新失败")

    def delete_env(self, env_id):
        return self.request("DELETE", "/open/envs", json=[env_id])

    def enable_env(self, env_id):
        return self.request("PUT", "/open/envs/enable", json=[env_id])

    def disable_env(self, env_id):
        return self.request("PUT", "/open/envs/disable", json=[env_id])


def env_matches_account(env, account, session, env_value):
    remarks = str(env.get("remarks") or "")
    value = str(env.get("value") or "")
    phone = account_phone(account, session)
    owner = str(account.get("owner_userid", ""))
    if phone and owner and phone in remarks and ("用户：%s" % owner) in remarks:
        return True
    if env_value and value == env_value:
        return True
    if phone and (phone in remarks or phone in value):
        return True
    return False


def find_env_for_account(ql, cfg, account, session, env_value):
    sync = bucket_get_json(BUCKET_SYNC, account["account_key"], {})
    env_id = (sync or {}).get("env_id")
    envs = ql.get_envs(cfg["env_name"])
    if env_id:
        for env in envs:
            if str(parse_env_id(env)) == str(env_id):
                return env
    for env in envs:
        if env.get("name") == cfg["env_name"] and env_matches_account(env, account, session, env_value):
            return env
    return None


def sync_to_qinglong(account_key, cfg):
    status = auth_status(account_key)
    if cfg.get("ql_sync_only_authorized") and status["status"] != "active":
        return disable_qinglong_account(account_key, cfg, "未授权或已过期")
    account = get_account(account_key)
    session = get_session(account_key)
    if not account or not session:
        raise PluginError("本地账号或会话缺失")
    session = validate_qinglong_session(session)
    ql = QingLongAPI(cfg)
    value = build_env_value(account, session)
    auth = get_auth(account_key) or {}
    remarks = build_remarks(account, auth, session)
    env = find_env_for_account(ql, cfg, account, session, value)
    if env:
        env_id = parse_env_id(env)
        ql.update_env(env_id, cfg["env_name"], value, remarks)
        try:
            ql.enable_env(env_id)
        except Exception:
            pass
        action = "updated"
    else:
        env = ql.add_env(cfg["env_name"], value, remarks)
        env_id = parse_env_id(env)
        action = "created"
    bucket_set_json(BUCKET_SYNC, account_key, {
        "env_name": cfg["env_name"],
        "env_id": str(env_id or ""),
        "remarks": remarks,
        "last_sync_at": now_ts(),
        "last_sync_status": "ok",
        "last_error": "",
    })
    return {"ok": True, "action": action, "env_id": str(env_id or "")}


def disable_qinglong_account(account_key, cfg, reason=""):
    account = get_account(account_key)
    session = get_session(account_key)
    if not account or not session or not cfg.get("ql_config"):
        return {"ok": True, "action": "skip", "reason": reason or "未配置青龙"}
    ql = QingLongAPI(cfg)
    value = build_env_value(account, session)
    env = find_env_for_account(ql, cfg, account, session, value)
    if not env:
        return {"ok": True, "action": "not_found"}
    env_id = parse_env_id(env)
    ql.disable_env(env_id)
    sync = bucket_get_json(BUCKET_SYNC, account_key, {}) or {}
    sync.update({"env_id": str(env_id), "last_sync_at": now_ts(), "last_sync_status": "disabled", "last_error": reason})
    bucket_set_json(BUCKET_SYNC, account_key, sync)
    return {"ok": True, "action": "disabled", "env_id": str(env_id)}


def remove_from_qinglong(account_key, cfg):
    account = get_account(account_key)
    session = get_session(account_key)
    if not account or not session or not cfg.get("ql_config"):
        return {"ok": True, "action": "skip", "reason": "未配置青龙或本地缺失"}
    ql = QingLongAPI(cfg)
    value = build_env_value(account, session)
    env = find_env_for_account(ql, cfg, account, session, value)
    if not env:
        return {"ok": True, "action": "not_found"}
    env_id = parse_env_id(env)
    ql.delete_env(env_id)
    return {"ok": True, "action": "deleted", "env_id": str(env_id)}


class DejianClient:
    def __init__(self, session_data, cfg):
        self.session_data = session_data
        self.cfg = cfg
        self.dev = self.build_device_params(session_data)
        self.session = requests.Session()
        self.session.trust_env = False

    def build_device_params(self, session_data):
        session_data = normalize_session_data(session_data)
        params = {}
        if isinstance(session_data.get("device"), dict):
            params.update(session_data["device"])
        params["usr"] = session_data.get("usr", "")
        params["ku"] = session_data.get("ku", session_data.get("usr", ""))
        params["kt"] = session_data.get("kt", "")
        params["zyeid"] = session_data.get("zyeid", "")
        params.setdefault("_android", "12")
        params.setdefault("_build", "SP1A.210812.016")
        return params

    def native_ua(self):
        return build_native_ua_from_device(self.dev)

    def webview_ua(self):
        p16 = self.dev.get("p16", "M2104K10AC")
        android_ver = self.dev.get("_android", "12")
        build_id = self.dev.get("_build", "SP1A.210812.016")
        d1 = self.dev.get("d1", "5.5.9.2")
        return (
            "Mozilla/5.0 (Linux; Android %s; %s Build/%s; wv) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
            "Chrome/96.0.4664.104 Mobile Safari/537.36 "
            "zyApp/dejian zyVersion/%s zyChannel/124012"
        ) % (android_ver, p16, build_id, d1)

    def common_params(self):
        data = {
            "source": "welfare", "showContentInStatusBar": "1",
            "ecpmMix": "0.0", "ecpmVideo": "0.0", "mcTacid": "16247", "pca": "channel-visit",
        }
        for key in ["zyeid", "usr", "rgt", "p1", "ku", "kt", "pc", "p2", "p3", "p4", "p5", "p7", "p9", "p12", "p16", "p21", "p22", "p25", "p26", "p28", "p29", "p30", "p31", "p33", "p34", "firm", "d1", "p35"]:
            data[key] = self.dev.get(key, "")
        return data

    def welfare_api(self, method, path, body=None):
        common = self.common_params()
        if body:
            common.update(body)
        body_str = urlencode(common) if method.upper() == "POST" else ""
        sign_data = cloud_sign({"type": "x-sign", "method": method, "path": path, "params": common, "body_str": body_str}, self.cfg)
        headers = {
            "X-Sign": sign_data["sign"], "X-Nonce": sign_data["nonce"],
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.webview_ua(), "Accept": "application/json, text/plain, */*",
            "Origin": "https://dj-h5.palmestore.com", "Referer": "https://dj-h5.palmestore.com/",
            "X-Requested-With": "com.chaozh.iReader.dj",
        }
        proxies = fetch_proxy(self.cfg)
        if method.upper() == "GET":
            resp = self.session.get(WELFARE_BASE + path, params=common, headers=headers, timeout=self.cfg["request_timeout"], proxies=proxies)
        else:
            resp = self.session.post(WELFARE_BASE + path, params=common, data=body_str, headers=headers, timeout=self.cfg["request_timeout"], proxies=proxies)
        return response_json(resp, "得间查询接口")

    def user_preview(self):
        return self.welfare_api("GET", "/welfare/web/task/user")

    def sign_status(self):
        try:
            data = self.welfare_api("GET", "/welfare/web/task/list")
            if data.get("code") != 0:
                return "未知"
            tasks = (data.get("body") or {}).get("task_info") or {}
            for task in tasks.values():
                if str(task.get("task_type", "")) != "1005":
                    continue
                detail_list = task.get("detail_list") or []
                today_signed = task.get("today_signed")
                if today_signed is True or str(today_signed).lower() == "true":
                    return "已签到"
                if today_signed is False or str(today_signed).lower() == "false":
                    return "未签到"
                today_detail = self._current_sign_detail(task, detail_list)
                if today_detail:
                    return self._sign_status_text(today_detail.get("sign_status"))

                done_status = self._safe_int(task.get("done_status"), -1)
                reward_status = self._safe_int(task.get("reward_status"), -1)
                if done_status >= 2 or reward_status == 2:
                    return "已签到"
                return "未知"
            return "未知"
        except Exception:
            return "未知"

    @staticmethod
    def _safe_int(value, default=0):
        try:
            return int(value)
        except Exception:
            try:
                return int(float(str(value)))
            except Exception:
                return default

    @staticmethod
    def _sign_status_text(status):
        status = DejianClient._safe_int(status, -1)
        if status == 3:
            return "已签到"
        if status == 1:
            return "未签到"
        return "未知"

    @staticmethod
    def _current_sign_detail(task, detail_list):
        detail = DejianClient._today_sign_detail(detail_list)
        if detail:
            return detail
        curr_day = DejianClient._safe_int((task or {}).get("curr_day"), -1)
        if curr_day >= 0:
            for item in detail_list or []:
                if isinstance(item, dict) and DejianClient._safe_int(item.get("days"), -2) == curr_day:
                    return item
        return None

    @staticmethod
    def _today_sign_detail(detail_list):
        today_values = {
            datetime.now().strftime("%Y%m%d"),
            datetime.now().strftime("%Y-%m-%d"),
            datetime.now().strftime("%Y/%m/%d"),
            datetime.now().strftime("%m-%d"),
            datetime.now().strftime("%m/%d"),
        }
        today_keys = ("is_today", "isToday", "today", "current", "current_day", "currentDay")
        date_keys = ("date", "day", "sign_date", "signDate", "sign_day", "signDay", "ymd")
        for detail in detail_list or []:
            if not isinstance(detail, dict):
                continue
            for key in today_keys:
                value = detail.get(key)
                if value in (True, 1, "1", "true", "True", "yes", "Y"):
                    return detail
            for key in date_keys:
                value = str(detail.get(key, "")).strip()
                if value and value in today_values:
                    return detail
        return None


def parse_selection(text, count):
    text = (text or "").strip().lower()
    if text == "q":
        return None
    if text == "0":
        return list(range(count))
    selected = []
    for part in re.split(r"[,，\s]+", text):
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            if not left.isdigit() or not right.isdigit():
                raise PluginError("选择格式错误")
            a, b = int(left), int(right)
            if a > b:
                a, b = b, a
            for n in range(a, b + 1):
                if 1 <= n <= count and n - 1 not in selected:
                    selected.append(n - 1)
        else:
            if not part.isdigit():
                raise PluginError("选择格式错误")
            n = int(part)
            if 1 <= n <= count and n - 1 not in selected:
                selected.append(n - 1)
    if not selected:
        raise PluginError("没有选中账号")
    return selected


def format_account_selector(accounts, title="请选择得间账号", all_text="全部账号"):
    lines = []
    for idx, account in enumerate(accounts, 1):
        status = auth_status(account["account_key"])
        sync = bucket_get_json(BUCKET_SYNC, account["account_key"], {}) or {}
        ql = "已同步" if sync.get("last_sync_status") == "ok" else ("失败" if sync.get("last_sync_status") == "fail" else "未同步")
        lines.extend([
            "[%d] %s" % (idx, account_display(account)),
            "账号：%s" % mask_text(account.get("usr", ""), 3),
            "状态：%s" % status["text"],
            "到期：%s" % (status.get("expire_date") or "-"),
            "青龙：%s" % ql,
        ])
    lines.extend([
        "------------------",
        "请发送账号序号",
        "输入 0 选择%s" % all_text,
        "支持 1、1,3、1-3",
        "输入 q 取消",
    ])
    return format_panel(title, lines)


def pick_accounts(sender, accounts, title="请选择得间账号", all_text="全部账号", timeout=180):
    if not accounts:
        sender_reply(sender, "没有可操作的得间账号")
        return []
    sender_reply(sender, format_account_selector(accounts, title, all_text))
    text = sender_input(sender, timeout)
    if text.lower() == "q":
        sender_reply(sender, "已取消")
        return []
    try:
        indexes = parse_selection(text, len(accounts))
        if indexes is None:
            sender_reply(sender, "已取消")
            return []
        return [accounts[i] for i in indexes]
    except PluginError as exc:
        sender_reply(sender, "选择失败：%s" % exc)
        return []


def user_accounts(user_id):
    accounts = []
    for key in get_user_account_keys(user_id):
        account = get_account(key)
        if account:
            accounts.append(account)
    return accounts


def show_help(sender, cfg, admin=False):
    if coin_price_int(cfg) == 0:
        coin_text = "免费授权"
    elif cfg.get("coin_bucket"):
        coin_text = "已开启，每账号每天 %d 积分" % coin_price_int(cfg)
    else:
        coin_text = "未配置积分桶"
    lines = [
        "得间教程  查看说明",
        "得间登录  手机号验证码登录",
        "得间查询  查看账号状态",
        "得间管理  删除/更新/同步账号",
        "得间授权  积分按天授权",
        "------------------",
        "青龙变量：%s" % cfg["env_name"],
        "积分授权：%s" % coin_text,
        "到期提醒：提前 %s 天" % cfg["expire_notify_days"],
    ]
    if admin:
        lines.extend([
            "------------------",
            "得间授权  管理员授权",
            "得间同步  重同步青龙",
            "得间检测  批量检测",
            "得间清理  清理过期",
            "得间统计  全局统计",
        ])
    reply_panel(sender, "📘 得间免费小说", lines)


def handle_login(sender, cfg):
    cfg = dict(cfg)
    user_id = get_user_id(sender)
    sender_reply(sender, format_panel("📲 得间登录", [
        "请发送得间手机号",
        "格式：手机号",
        "示例：13800000000",
        "输入 q 取消登录",
    ]))
    phone = sender_input(sender, cfg["sms_wait_timeout"])
    if phone.lower() == "q":
        sender_reply(sender, "已取消登录")
        return
    if not re.fullmatch(r"\d{11}", phone):
        sender_reply(sender, "手机号格式不正确")
        return
    if cfg.get("proxy_api_url"):
        try:
            cfg["_fixed_proxy"] = fetch_proxy(cfg)
        except Exception as exc:
            sender_reply(sender, "代理提取失败：%s" % short_error(exc))
            return
    try:
        result = send_sms(phone, cfg)
        if result.get("code") != 0:
            sender_reply(sender, "验证码发送失败：%s" % (result.get("msg") or result))
            return
    except Exception as exc:
        sender_reply(sender, "验证码发送失败：%s" % short_error(exc))
        return
    sender_reply(sender, format_panel("🔐 得间验证码", [
        "验证码已发送",
        "请发送短信验证码",
        "格式：4位数字验证码",
        "输入 q 取消登录",
    ]))
    code = sender_input(sender, cfg["sms_wait_timeout"])
    if code.lower() == "q":
        sender_reply(sender, "已取消登录")
        return
    if not re.fullmatch(r"\d{4,8}", code):
        sender_reply(sender, "验证码格式不正确")
        return
    try:
        session = login_by_phone(phone, code, cfg)
        account = save_account(user_id, session, "sms")
        status = auth_status(account["account_key"])
        ql_text = "授权后同步"
        if status["status"] == "active":
            try:
                sync_to_qinglong(account["account_key"], cfg)
                ql_text = "已同步"
            except Exception as exc:
                ql_text = "同步失败：%s" % short_error(exc)
        reply_panel(sender, "✅ 得间登录成功", [
            "账号：%s" % account_display(account),
            "授权：%s" % status["text"],
            "青龙：%s" % ql_text,
        ])
    except Exception as exc:
        sender_reply(sender, "登录失败：%s" % short_error(exc))


def build_query_card(account, cfg, index=None, total=None):
    status = auth_status(account["account_key"])
    sync = bucket_get_json(BUCKET_SYNC, account["account_key"], {}) or {}
    ql_text = "已同步" if sync.get("last_sync_status") == "ok" else ("失败：%s" % sync.get("last_error") if sync.get("last_sync_status") == "fail" else "未同步")
    coin = cash = sign = "未知"
    session = get_session(account["account_key"])
    if session:
        try:
            client = DejianClient(session, cfg)
            preview = client.user_preview()
            if preview.get("code") == 0:
                c = (preview.get("body") or {}).get("coin") or {}
                coin = c.get("coin_amount", "未知")
                cash = "%s元" % c.get("cash_amount", "未知")
            sign = client.sign_status()
        except Exception:
            pass
    title = "🔎 得间账号查询"
    if index is not None and total is not None:
        title = "🔎 得间账号查询 %d/%d" % (index, total)
    return format_panel(title, [
        "账号：%s" % account_display(account),
        "授权：%s" % status["text"],
        "青龙：%s" % ql_text,
        "金币：%s" % coin,
        "现金：%s" % cash,
        "签到状态：%s" % sign,
        "到期：%s%s" % (status.get("expire_date") or "-", "（剩余%s天）" % status["days_left"] if status["status"] == "active" else ""),
    ])


def handle_query(sender, cfg):
    accounts = user_accounts(get_user_id(sender))
    if not accounts:
        sender_reply(sender, "暂无得间账号，请先发送 得间登录")
        return
    if len(accounts) > 1:
        accounts = pick_accounts(sender, accounts, "请选择查询账号", "全部账号", cfg["sms_wait_timeout"])
        if not accounts:
            return
    total = len(accounts)
    for index, account in enumerate(accounts, 1):
        sender_reply(sender, build_query_card(account, cfg, index if total > 1 else None, total if total > 1 else None))
        if total > 1:
            time.sleep(0.3)


def handle_delete(sender, cfg, accounts):
    selected = pick_accounts(sender, accounts, "请选择删除账号", "全部账号", cfg["sms_wait_timeout"])
    if not selected:
        return
    sender_reply(sender, format_panel("🗑 确认删除", [
        "即将删除选中的得间账号",
        "会同时删除本地账号和青龙变量",
        "输入 y 确认删除",
        "输入其他内容取消",
    ]))
    if sender_input(sender, cfg["sms_wait_timeout"]).lower() != "y":
        sender_reply(sender, "已取消")
        return
    lines = []
    for account in selected:
        key = account["account_key"]
        try:
            ql = remove_from_qinglong(key, cfg)
            ql_text = ql.get("action", "ok")
        except Exception as exc:
            ql_text = "失败：%s" % short_error(exc)
        delete_account_local(key)
        lines.append("%s：本地已删，青龙%s" % (account_display(account), ql_text))
    reply_panel(sender, "🗑 删除结果", lines)


def handle_sync(sender, cfg, accounts):
    selected = pick_accounts(sender, accounts, "请选择提交青龙账号", "全部已授权账号", cfg["sms_wait_timeout"])
    if not selected:
        return
    lines = []
    for account in selected:
        key = account["account_key"]
        if auth_status(key)["status"] != "active":
            lines.append("%s：跳过，未授权或已过期" % account_display(account))
            continue
        try:
            result = sync_to_qinglong(key, cfg)
            lines.append("%s：成功 %s" % (account_display(account), result.get("action")))
        except Exception as exc:
            bucket_set_json(BUCKET_SYNC, key, {"last_sync_at": now_ts(), "last_sync_status": "fail", "last_error": short_error(exc)})
            lines.append("%s：失败 %s" % (account_display(account), short_error(exc)))
    reply_panel(sender, "📤 提交青龙结果", lines)


def coin_price_int(cfg):
    try:
        return max(int(cfg.get("coin_price", 0)), 0)
    except Exception:
        return 0


def get_user_coin(user_id, coin_bucket):
    return parse_int(bucket_get(coin_bucket, str(user_id), "0"), 0)


def set_user_coin(user_id, amount, coin_bucket):
    return bucket_set(coin_bucket, str(user_id), str(max(int(amount), 0)))


def deduct_user_coin(user_id, amount, coin_bucket):
    if amount <= 0:
        return True
    current = get_user_coin(user_id, coin_bucket)
    if current < amount:
        return False
    return set_user_coin(user_id, current - amount, coin_bucket)


def refund_user_coin(user_id, amount, coin_bucket):
    if amount <= 0:
        return True
    current = get_user_coin(user_id, coin_bucket)
    return set_user_coin(user_id, current + amount, coin_bucket)


def restore_auth(account_key, previous_auth):
    if previous_auth:
        bucket_set_json(BUCKET_AUTH, account_key, previous_auth)
    else:
        bucket_del(BUCKET_AUTH, account_key)


def authorize_accounts(sender, cfg, accounts, days, deduct_coin=False, source="coin"):
    days = parse_int(days, 0, 1, 3650)
    if days <= 0:
        raise PluginError("授权天数必须大于 0")
    if not accounts:
        raise PluginError("没有可授权账号")
    user_id = get_user_id(sender)
    price = coin_price_int(cfg)
    if deduct_coin and price > 0 and not cfg.get("coin_bucket"):
        raise PluginError("未配置积分桶名称")
    estimate_cost = len(accounts) * days * price if deduct_coin else 0
    if deduct_coin:
        current = get_user_coin(user_id, cfg["coin_bucket"])
        if current < estimate_cost:
            raise PluginError("积分不足：当前 %s，最多需要 %s" % (current, estimate_cost))

    success = []
    failed = []
    charged = 0
    for account in accounts:
        account_key = account["account_key"]
        account_cost = days * price if deduct_coin else 0
        paid = False
        previous_auth = get_auth(account_key)
        try:
            if deduct_coin and account_cost > 0:
                if not deduct_user_coin(user_id, account_cost, cfg["coin_bucket"]):
                    raise PluginError("积分不足或扣除失败")
                paid = True
                charged += account_cost
            auth = set_auth(account_key, days, source, user_id)
            try:
                sync_to_qinglong(account_key, cfg)
            except Exception:
                restore_auth(account_key, previous_auth)
                raise
            notify = bucket_get_json(BUCKET_NOTIFY, account_key, {}) or {}
            notify.pop("last_expire_notice", None)
            notify["updated_at"] = now_ts()
            bucket_set_json(BUCKET_NOTIFY, account_key, notify)
            success.append({
                "remark": account_display(account),
                "expire": auth.get("expire_date", ""),
                "cost": account_cost,
            })
        except Exception as exc:
            if paid:
                try:
                    refund_user_coin(user_id, account_cost, cfg["coin_bucket"])
                    charged -= account_cost
                except Exception:
                    failed.append({"remark": account_display(account), "reason": "%s；退款失败，请联系管理员" % short_error(exc)})
                    continue
            failed.append({"remark": account_display(account), "reason": short_error(exc)})

    lines = [
        "授权账号：%d 个" % len(accounts),
        "成功：%d 个" % len(success),
        "失败：%d 个" % len(failed),
        "授权天数：%d 天" % days,
        "扣除积分：%s" % (charged if deduct_coin else 0),
    ]
    if deduct_coin and price > 0 and cfg.get("coin_bucket"):
        lines.append("剩余积分：%s" % get_user_coin(user_id, cfg["coin_bucket"]))
    elif deduct_coin and price == 0:
        lines.append("免费授权：未扣积分")
    lines.append("------------------")
    for item in success:
        lines.append("%s：到期 %s，青龙已同步" % (item["remark"], item["expire"]))
    for item in failed:
        lines.append("%s：%s" % (item["remark"], item["reason"]))
    reply_panel(sender, "✅ 得间授权完成", lines)


def handle_user_authorize(sender, cfg):
    accounts = user_accounts(get_user_id(sender))
    if not accounts:
        sender_reply(sender, "你还没有绑定得间账号，请先发送 得间登录")
        return
    selected = pick_accounts(sender, accounts, "得间授权", "全部账号", cfg["sms_wait_timeout"])
    if not selected:
        return
    price = coin_price_int(cfg)
    sender_reply(sender, format_panel("✅ 得间授权", [
        "请发送授权天数",
        "账号数量：%d 个" % len(selected),
        "单价：每账号每天 %d 积分" % price,
        "格式：正整数，例如 30",
        "输入 q 取消授权",
    ]))
    text = sender_input(sender, cfg["sms_wait_timeout"])
    if text.lower() == "q":
        sender_reply(sender, "已取消授权")
        return
    days = parse_int(text, 0, 1, 3650)
    if days <= 0:
        sender_reply(sender, "天数必须大于 0")
        return
    cost = len(selected) * days * price
    current_coin = get_user_coin(get_user_id(sender), cfg["coin_bucket"]) if cfg.get("coin_bucket") else 0
    lines = [
        "账号数量：%d 个" % len(selected),
        "授权天数：%d 天" % days,
        "单价：%d 积分/账号/天" % price,
        "所需积分：%d" % cost,
    ]
    if price == 0:
        lines.append("当前积分：免费授权不扣积分")
    elif cfg.get("coin_bucket"):
        lines.append("当前积分：%d" % current_coin)
    else:
        lines.append("当前积分：未配置积分桶")
    lines.extend(["------------------", "输入 y 确认授权", "输入其他内容取消"])
    sender_reply(sender, format_panel("💳 确认授权", lines))
    confirm = sender_input(sender, cfg["sms_wait_timeout"]).lower()
    if confirm != "y":
        sender_reply(sender, "已取消授权")
        return
    if price > 0 and not cfg.get("coin_bucket"):
        sender_reply(sender, "积分桶未配置，无法扣费授权")
        return
    if current_coin < cost:
        sender_reply(sender, "积分不足")
        return
    try:
        authorize_accounts(sender, cfg, selected, days, deduct_coin=True, source="coin")
    except Exception as exc:
        sender_reply(sender, "授权失败：%s" % short_error(exc))


def handle_manage(sender, cfg):
    accounts = user_accounts(get_user_id(sender))
    if not accounts:
        sender_reply(sender, "暂无得间账号，请先发送 得间登录")
        return
    sender_reply(sender, format_panel("⚙️ 得间账号管理", [
        "1. 删除账号",
        "2. 更新登录",
        "3. 提交青龙",
        "4. 授权账号",
        "5. 到期提醒",
        "输入序号选择操作",
        "输入 q 退出管理",
    ]))
    choice = sender_input(sender, cfg["sms_wait_timeout"]).lower()
    if choice == "1":
        handle_delete(sender, cfg, accounts)
    elif choice == "2":
        sender_reply(sender, "更新登录请重新发送 得间登录，登录同一账号会覆盖旧会话")
    elif choice == "3":
        handle_sync(sender, cfg, accounts)
    elif choice == "4":
        handle_user_authorize(sender, cfg)
    elif choice == "5":
        selected = pick_accounts(sender, accounts, "请选择设置提醒账号", "全部账号", cfg["sms_wait_timeout"])
        for account in selected:
            notify = bucket_get_json(BUCKET_NOTIFY, account["account_key"], {}) or {}
            enabled = not parse_bool(notify.get("expire_notify", True), True)
            notify.update({"expire_notify": enabled, "notify_days": cfg["expire_notify_days"], "updated_at": now_ts()})
            bucket_set_json(BUCKET_NOTIFY, account["account_key"], notify)
        sender_reply(sender, "到期提醒开关已更新")
    else:
        sender_reply(sender, "已退出")


def list_all_user_ids():
    return [str(key) for key in bucket_keys(BUCKET_USER) if str(key).strip()]


def pick_user_for_admin(sender, cfg):
    users = list_all_user_ids()
    if not users:
        return ""
    lines = []
    for index, user_id in enumerate(users, 1):
        lines.append("[%d] 用户：%s  账号数：%d" % (index, user_id, len(user_accounts(user_id))))
    lines.extend(["------------------", "请发送用户序号", "输入 q 取消"])
    sender_reply(sender, format_panel("👤 选择用户", lines))
    raw = sender_input(sender, cfg["sms_wait_timeout"])
    if raw.lower() == "q":
        return ""
    indexes = parse_selection(raw, len(users))
    if indexes is None:
        return ""
    if len(indexes) != 1:
        raise PluginError("一次只能选择一个用户")
    return users[indexes[0]]


def handle_admin_authorize(sender, cfg):
    sender_reply(sender, format_panel("🛠 得间管理员授权", [
        "1. 给指定账号授权",
        "2. 选择用户后授权账号",
        "3. 一键授权所有用户",
        "------------------",
        "管理员授权不扣积分",
        "输入序号选择操作",
        "输入 q 取消授权",
    ]))
    choice = sender_input(sender, cfg["sms_wait_timeout"]).lower()
    if not choice or choice == "q":
        sender_reply(sender, "已取消授权")
        return
    accounts = []
    if choice == "1":
        accounts = pick_accounts(sender, all_accounts(), "选择账号", "全部账号", cfg["sms_wait_timeout"])
    elif choice == "2":
        try:
            selected_user = pick_user_for_admin(sender, cfg)
        except Exception as exc:
            sender_reply(sender, str(exc))
            return
        if not selected_user:
            sender_reply(sender, "已取消授权")
            return
        user_items = user_accounts(selected_user)
        if not user_items:
            sender_reply(sender, "该用户没有可授权账号")
            return
        accounts = pick_accounts(sender, user_items, "选择用户账号", "全部账号", cfg["sms_wait_timeout"])
    elif choice == "3":
        accounts = all_accounts()
    else:
        sender_reply(sender, "无效选择")
        return
    if not accounts:
        sender_reply(sender, "未找到可授权账号")
        return
    sender_reply(sender, format_panel("✅ 管理员授权", [
        "请发送授权天数",
        "账号数量：%d 个" % len(accounts),
        "管理员授权不扣积分",
        "格式：正整数，例如 30",
        "输入 q 取消授权",
    ]))
    text = sender_input(sender, cfg["sms_wait_timeout"])
    if text.lower() == "q":
        sender_reply(sender, "已取消授权")
        return
    days = parse_int(text, 0, 1, 3650)
    if days <= 0:
        sender_reply(sender, "授权天数不正确")
        return
    if choice == "3":
        sender_reply(sender, format_panel("⚠️ 最终确认", [
            "即将为全部 %d 个账号授权 %d 天" % (len(accounts), days),
            "管理员授权不扣积分",
            "输入 y 确认授权",
            "输入其他内容取消",
        ]))
        if sender_input(sender, cfg["sms_wait_timeout"]).lower() != "y":
            sender_reply(sender, "已取消授权")
            return
    try:
        authorize_accounts(sender, cfg, accounts, days, deduct_coin=False, source="admin")
    except Exception as exc:
        sender_reply(sender, "授权失败：%s" % short_error(exc))


def handle_admin_sync(sender, cfg):
    accounts = [a for a in all_accounts() if auth_status(a["account_key"])["status"] == "active"]
    if not accounts:
        sender_reply(sender, "没有已授权账号")
        return
    lines = []
    for account in accounts:
        try:
            result = sync_to_qinglong(account["account_key"], cfg)
            lines.append("%s：%s" % (account_display(account), result.get("action")))
        except Exception as exc:
            lines.append("%s：失败 %s" % (account_display(account), short_error(exc)))
    reply_panel(sender, "🔄 得间重同步", lines)


def handle_admin_check(sender, cfg):
    lines = []
    for account in all_accounts():
        key = account["account_key"]
        status = auth_status(key)
        session = get_session(key)
        sync = bucket_get_json(BUCKET_SYNC, key, {}) or {}
        lines.append("%s：授权%s，会话%s，青龙%s" % (
            account_display(account),
            status["text"],
            "正常" if session else "缺失",
            sync.get("last_sync_status", "未同步"),
        ))
    if not lines:
        lines.append("没有得间账号")
    reply_panel(sender, "🧪 得间检测", lines)


def handle_admin_cleanup(sender, cfg):
    sender_reply(sender, format_panel("🧹 得间清理", [
        "即将清理过期授权和缺失会话账号",
        "会处理本地数据和青龙变量",
        "输入 y 确认清理",
        "输入其他内容取消",
    ]))
    if sender_input(sender, cfg["sms_wait_timeout"]).lower() != "y":
        sender_reply(sender, "已取消")
        return
    lines = []
    for account in all_accounts():
        key = account["account_key"]
        status = auth_status(key)
        session = get_session(key)
        if status["status"] == "expired" or not session:
            try:
                ql = remove_from_qinglong(key, cfg)
                ql_text = ql.get("action")
            except Exception as exc:
                ql_text = "失败 %s" % short_error(exc)
            if not session:
                delete_account_local(key)
                local = "本地已删"
            else:
                disable_qinglong_account(key, cfg, "授权过期")
                local = "本地保留过期状态"
            lines.append("%s：%s，青龙%s" % (account_display(account), local, ql_text))
    if not lines:
        lines.append("没有需要清理的账号")
    reply_panel(sender, "🧹 得间清理", lines)


def handle_admin_stats(sender):
    accounts = all_accounts()
    users = set(str(a.get("owner_userid")) for a in accounts if a.get("owner_userid"))
    active = expired = none = ql_ok = ql_fail = 0
    last_sync = 0
    for account in accounts:
        st = auth_status(account["account_key"])["status"]
        if st == "active":
            active += 1
        elif st == "expired":
            expired += 1
        else:
            none += 1
        sync = bucket_get_json(BUCKET_SYNC, account["account_key"], {}) or {}
        if sync.get("last_sync_status") == "ok":
            ql_ok += 1
        elif sync.get("last_sync_status") == "fail":
            ql_fail += 1
        last_sync = max(last_sync, parse_int(sync.get("last_sync_at", 0), 0))
    reply_panel(sender, "📊 得间统计", [
        "用户数：%d" % len(users),
        "账号数：%d" % len(accounts),
        "已授权：%d" % active,
        "未授权/停用：%d" % none,
        "已过期：%d" % expired,
        "青龙成功：%d" % ql_ok,
        "青龙失败：%d" % ql_fail,
        "最近同步：%s" % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_sync)) if last_sync else "-"),
    ])


def handle_cron(sender, cfg):
    if not cfg.get("expire_notify_enabled"):
        return
    total = expiring = expired = ql_done = ql_fail = 0
    for account in all_accounts():
        total += 1
        key = account["account_key"]
        status = auth_status(key)
        if status["status"] == "expired":
            expired += 1
            try:
                disable_qinglong_account(key, cfg, "授权过期")
                ql_done += 1
            except Exception:
                ql_fail += 1
            continue
        if status["status"] == "active" and 0 <= status["days_left"] <= cfg["expire_notify_days"]:
            expiring += 1
            notify = bucket_get_json(BUCKET_NOTIFY, key, {}) or {}
            if notify.get("last_expire_notice") == today() or parse_bool(notify.get("expire_notify", True), True) is False:
                continue
            notify["last_expire_notice"] = today()
            notify["expire_notify"] = True
            notify["notify_days"] = cfg["expire_notify_days"]
            bucket_set_json(BUCKET_NOTIFY, key, notify)
    try:
        sender_reply(sender, "得间巡检：总账号%d，即将到期%d，已过期%d，青龙处理成功%d，失败%d" % (total, expiring, expired, ql_done, ql_fail))
    except Exception:
        pass


def route_message(sender, cfg):
    message = ""
    try:
        message = str(sender.getMessage()).strip()
    except Exception:
        pass
    action = re.sub(r"^(得间小说|得间|dj)", "", message, count=1, flags=re.I).strip()
    admin = is_admin_user(sender, cfg)
    if action in ("教程", ""):
        show_help(sender, cfg, admin)
    elif action == "登录":
        handle_login(sender, cfg)
    elif action == "查询":
        handle_query(sender, cfg)
    elif action == "管理":
        handle_manage(sender, cfg)
    elif action == "授权":
        if admin:
            handle_admin_authorize(sender, cfg)
        else:
            handle_user_authorize(sender, cfg)
    elif action == "同步":
        if not admin:
            sender_reply(sender, "无管理员权限")
        else:
            handle_admin_sync(sender, cfg)
    elif action == "检测":
        if not admin:
            sender_reply(sender, "无管理员权限")
        else:
            handle_admin_check(sender, cfg)
    elif action == "清理":
        if not admin:
            sender_reply(sender, "无管理员权限")
        else:
            handle_admin_cleanup(sender, cfg)
    elif action == "统计":
        if not admin:
            sender_reply(sender, "无管理员权限")
        else:
            handle_admin_stats(sender)
    else:
        show_help(sender, cfg, admin)


def main():
    if middleware is None:
        return
    sender_id = middleware.getSenderID()
    sender = middleware.Sender(sender_id)
    cfg = get_config()
    try:
        if sender.getImtype() == "fake":
            handle_cron(sender, cfg)
            return
    except Exception:
        pass
    route_message(sender, cfg)


if __name__ == "__main__":
    main()
