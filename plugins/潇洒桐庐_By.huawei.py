# [title:潇洒桐庐]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: 1603960061]
# [disable:false]
# [admin: false]
# [rule: ^(潇洒桐庐|xstl)(登录|登陆|查询|管理|授权|清理|上传|上传青龙|上传呆呆)$|^(登录|登陆|查询|管理)(潇洒桐庐|xstl)$]
# [cron: 30 8 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://ts1.tc.mm.bing.net/th/id/OIP-C.s-Mk0xSwW7v2FGeSs2py2AAAAA?w=108&h=108&c=1&bgcl=653ae7&r=0&o=7&dpr=1.5&pid=ImgRC&rm=3]
# [version: 1.1.0]
# [public:true]
# [price: 18.88]
# [description: 潇洒桐庐 AutoMan 插件，支持手机号密码登录、账号查询、授权管理、青龙/呆呆同步、到期提醒<br>指令：潇洒桐庐登录、潇洒桐庐查询、潇洒桐庐管理、潇洒桐庐教程、潇洒桐庐授权、潇洒桐庐上传、潇洒桐庐上传青龙、潇洒桐庐上传呆呆、潇洒桐庐清理<br>安装依赖;autman-huawei]
# [param: {"required":false,"key":"G_XSTL.price","bool":false,"placeholder":"0.88","value":"0.88","name":"授权价格","desc":"单个账号每月授权价格，单位元"}]
# [param: {"required":false,"key":"G_XSTL.coin","bool":false,"placeholder":"100","value":"100","name":"积分/月","desc":"单个账号每月需要的积分，不填或填0则关闭积分支付"}]
# [param: {"required":false,"key":"G_XSTL.ql_config","bool":false,"placeholder":"http://ip:5700丨client_id丨client_secret","name":"青龙配置","desc":"青龙面板配置，格式：地址丨ClientID丨ClientSecret"}]
# [param: {"required":false,"key":"G_XSTL.ql_envname","bool":false,"placeholder":"G_XSTL_TOKEN","value":"G_XSTL_TOKEN","name":"环境变量名","desc":"推送到青龙/呆呆面板的环境变量名称"}]
# [param: {"required":false,"key":"G_XSTL.use_daidai","bool":true,"name":"默认同步呆呆","desc":"勾选后默认同步到呆呆面板，否则默认同步到青龙"}]
# [param: {"required":false,"key":"G_XSTL.daidai_config","bool":false,"placeholder":"http://ip:8080丨app_key丨app_secret","name":"呆呆配置","desc":"呆呆面板配置，格式：地址丨AppKey丨AppSecret"}]
# [param: {"required":false,"key":"G_XSTL.daidai_group","bool":false,"placeholder":"潇洒桐庐","value":"潇洒桐庐","name":"呆呆分组","desc":"呆呆面板变量分组名称，不填默认使用项目名"}]
# [param: {"required":false,"key":"G_XSTL.proxy_api","bool":false,"placeholder":"http://example.com/getip","name":"代理API","desc":"登录和查询时使用的代理API或固定代理地址，可选"}]
# [param: {"required":false,"key":"dd_sign_config.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款码(全局)","desc":"微信赞赏码/收款码链接"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_switch","bool":true,"name":"码支付开关(全局)","desc":"勾选启用全局码支付"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_gateway","bool":false,"placeholder":"https://demopay.9999.blue/","name":"码支付网关(全局)","desc":"码支付网关地址"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_pid","bool":false,"placeholder":"10006","name":"商户ID(全局)","desc":"码支付商户ID"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_key","bool":false,"placeholder":"FwzZNeOdNAD5FHm1PDsT","name":"商户密钥(全局)","desc":"码支付商户密钥"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_type","bool":false,"placeholder":"alipay,wxpay","value":"alipay,wxpay","name":"支付方式(全局)","desc":"多个方式用英文逗号分隔，如 alipay,wxpay"}]

import base64
import json
import os
import re
import time
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.parse import urlparse

import middleware
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    from autman_huawei import DadaiPanelClient, MaPayClient, QingLongClient, generate_qrcode_url, get_pay_config
except ImportError:
    DadaiPanelClient = None
    MaPayClient = None
    QingLongClient = None
    generate_qrcode_url = None

    def get_pay_config():
        return {}


senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())

PROJECT_NAME = "潇洒桐庐"
BUCKET_USER = "G_XSTL_user"
BUCKET_TOKEN = "G_XSTL_token"
BUCKET_AUTH = "G_XSTL_auth"
BUCKET_CONFIG = "G_XSTL"
DEFAULT_ENV_NAME = "G_XSTL_TOKEN"

PASSPORT_URL = "https://passport.tmuyun.com/web/oauth/credential_auth"
MAIN_API_BASE = "https://vapp.tmuyun.com"
ACTIVITY_API_BASE = "https://wxapi.hoolo.tv/event/dtqp/index.php"
CLIENT_ID = "10017"
TENANT_ID = "59"
LOGIN_GUEST_SESSION_ID = "6565886da95d5a47f651317f"
SIGNATURE_SALT = "FR*r!isE5W"
APP_USER_AGENT = "1.1.9;00000000-67f7-45bf-ffff-ffffa7397b83;Xiaomi MI 8 Lite;Android;10;Release"
WEBVIEW_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 "
    "Mobile Safari/537.36;xsb_xiaosatonglu;xsb_xiaosatonglu;1.0.60;native_app;6.5.1"
)
RSA_MODULUS_B64URL = "-lzu3vWHgDrPnBasGuxEyfll4sz6kHl7-vIub6sPaRURLK6ogU0XIO8AdESKd6yZA6WnlSS7GamJuU1uxVsf4jolxXPswj72ima4nNnVwsNuxL5R-a6vs8CDwwCRxgH559Z5kB-8EdzwmrRCG_Kc-RhZUxzJZbsOGWJpzsIPrYc"
RSA_EXPONENT = 65537
PAY_TIMEOUT = 300000
PAY_POLL_TIMES = 60
PAY_POLL_INTERVAL_MS = 5000
DEFAULT_PAY_TYPE_NAMES = {"alipay": "支付宝", "wxpay": "微信支付", "qqpay": "QQ钱包"}


def sanitize_text(value, max_len=64):
    text = str(value or "").replace("\r", " ").replace("\n", " ").replace("|", " ").replace("#", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text[:max_len] if max_len and len(text) > max_len else text


def safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def safe_decimal(value, default="0"):
    try:
        return Decimal(str(value).strip() or default)
    except Exception:
        return Decimal(default)


def parse_bool(value):
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on", "是", "开", "开启"}


def format_money(value):
    amount = safe_decimal(value, "0")
    text = "{:.2f}".format(amount)
    return text.rstrip("0").rstrip(".") if "." in text else text


def today_date():
    return datetime.now().date()


def parse_date(value):
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except Exception:
        return None


def mask_phone(phone):
    text = str(phone or "").strip()
    return f"{text[:3]}****{text[-4:]}" if re.fullmatch(r"1[3-9]\d{9}", text) else text


def dedup_list(items):
    result = []
    seen = set()
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        result.append(text)
        seen.add(text)
    return result


def encode_text_blob(text):
    return base64.urlsafe_b64encode(str(text or "").encode("utf-8")).decode("utf-8").rstrip("=")


def decode_text_blob(text):
    raw_text = str(text or "").strip()
    if not raw_text:
        return ""
    try:
        padded = raw_text + "=" * ((4 - len(raw_text) % 4) % 4)
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", "ignore")
    except Exception:
        return ""


def read_input(prompt, timeout=60000, cancel_text=""):
    sender.reply(prompt)
    value = sender.input(timeout, 1, False)
    if value is None:
        if cancel_text:
            sender.reply(cancel_text)
        return ""
    text = str(value).strip()
    if not text or text.lower() == "q":
        if cancel_text:
            sender.reply(cancel_text)
        return ""
    return text


def prompt_months():
    raw = read_input("请输入授权月数（1-12，回复 q 取消）：", 120000)
    if raw.isdigit() and 1 <= int(raw) <= 12:
        return int(raw)
    if raw:
        sender.reply("❌ 月数必须为 1-12 的整数")
    return 0


def parse_selection(choice, max_index):
    if not choice or not choice.strip():
        return None
    indices = set()
    try:
        for part in choice.strip().split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                start_text, end_text = part.split("-", 1)
                start = int(start_text.strip())
                end = int(end_text.strip())
                if start < 1 or end < 1 or start > max_index or end > max_index or start > end:
                    return None
                indices.update(range(start - 1, end))
            else:
                value = int(part)
                if value < 1 or value > max_index:
                    return None
                indices.add(value - 1)
        return sorted(indices) if indices else None
    except Exception:
        return None


def parse_pay_types(raw_value):
    result = {}
    if isinstance(raw_value, dict):
        for key, value in raw_value.items():
            pay_key = str(key or "").strip().lower()
            if pay_key:
                result[pay_key] = sanitize_text(value or DEFAULT_PAY_TYPE_NAMES.get(pay_key, pay_key), 16)
        return result
    for item in re.split(r"[,|/ ]+", str(raw_value or "").strip()):
        pay_key = item.strip().lower()
        if pay_key:
            result[pay_key] = DEFAULT_PAY_TYPE_NAMES.get(pay_key, pay_key)
    return result


def build_proxy_dict(proxy_value):
    text = str(proxy_value or "").strip().strip('"').strip("'")
    if not text:
        return None
    if "://" not in text:
        text = f"http://{text}"
    parsed = urlparse(text)
    if not parsed.hostname or not parsed.port:
        return None
    return {"http": text, "https": text}


def get_proxy():
    proxy_api = str(middleware.bucketGet(BUCKET_CONFIG, "proxy_api") or "").strip()
    if not proxy_api:
        return None
    if build_proxy_dict(proxy_api):
        return build_proxy_dict(proxy_api)
    try:
        response = requests.get(proxy_api, timeout=8, verify=False)
        return build_proxy_dict(response.text) if response.status_code == 200 else None
    except Exception:
        return None


def request_payload(method, url, headers=None, params=None, data=None):
    kwargs = {"headers": headers or {}, "params": params or None, "timeout": 20, "verify": False}
    if data is not None:
        kwargs["data"] = data
    proxy = get_proxy()
    if proxy:
        kwargs["proxies"] = proxy
    response = requests.request(method.upper(), url, **kwargs)
    response.raise_for_status()
    text = response.text.strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except Exception:
        match = re.search(r"^[^(]+\((.*)\)\s*$", text, re.S)
        if match:
            return json.loads(match.group(1))
    raise RuntimeError(f"接口返回无法解析: {text[:200]}")


def base64url_to_int(value):
    padded = value + "=" * ((4 - len(value) % 4) % 4)
    return int.from_bytes(base64.urlsafe_b64decode(padded.encode("utf-8")), "big")


RSA_MODULUS = base64url_to_int(RSA_MODULUS_B64URL)


def random_nonzero_bytes(size):
    output = bytearray()
    while len(output) < size:
        chunk = os.urandom(size - len(output))
        for item in chunk:
            if item != 0:
                output.append(item)
            if len(output) >= size:
                break
    return bytes(output)


def rsa_encrypt_password(password):
    message = str(password or "").encode("utf-8")
    key_size = (RSA_MODULUS.bit_length() + 7) // 8
    if len(message) > key_size - 11:
        raise ValueError("密码长度超出 RSA 加密限制")
    padding_size = key_size - len(message) - 3
    padded = b"\x00\x02" + random_nonzero_bytes(padding_size) + b"\x00" + message
    cipher_int = pow(int.from_bytes(padded, "big"), RSA_EXPONENT, RSA_MODULUS)
    return base64.b64encode(cipher_int.to_bytes(key_size, "big")).decode("utf-8")


def sha256_hex(value):
    import hashlib
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()


def build_signature(path, session_id, request_id, timestamp_ms):
    return sha256_hex(f"{path}&&{session_id}&&{request_id}&&{timestamp_ms}&&{SIGNATURE_SALT}&&{TENANT_ID}")


class XiaoSaTongLuClient:
    def get_code(self, phone, password):
        payload = request_payload(
            "POST",
            PASSPORT_URL,
            headers={
                "Host": "passport.tmuyun.com",
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept-Encoding": "gzip, deflate, br",
            },
            data={
                "client_id": CLIENT_ID,
                "password": rsa_encrypt_password(password),
                "phone_number": phone,
            },
        )
        if str(payload.get("code")) == "0":
            return str((payload.get("data") or {}).get("authorization_code", {}).get("code") or "").strip()
        raise RuntimeError(str(payload.get("message") or payload.get("msg") or "获取登录 code 失败"))

    def login(self, code):
        path = "/api/zbtxz/login"
        request_id = str(uuid.uuid4())
        timestamp_ms = str(int(time.time() * 1000))
        payload = request_payload(
            "POST",
            f"{MAIN_API_BASE}{path}",
            headers={
                "X-SESSION-ID": LOGIN_GUEST_SESSION_ID,
                "X-REQUEST-ID": request_id,
                "X-TIMESTAMP": timestamp_ms,
                "X-SIGNATURE": build_signature(path, LOGIN_GUEST_SESSION_ID, request_id, timestamp_ms),
                "X-TENANT-ID": TENANT_ID,
                "User-Agent": APP_USER_AGENT,
                "Cache-Control": "no-cache",
                "Host": "vapp.tmuyun.com",
                "Connection": "Keep-Alive",
            },
            data={
                "check_token": "",
                "code": code,
                "token": "",
                "type": "-1",
                "union_id": "",
            },
        )
        if str(payload.get("code")) != "0":
            raise RuntimeError(str(payload.get("message") or payload.get("msg") or "登录失败"))
        session_data = (payload.get("data") or {}).get("session") or {}
        account_data = (payload.get("data") or {}).get("account") or {}
        session_id = str(session_data.get("id") or "").strip()
        account_id = str(session_data.get("account_id") or "").strip()
        nick_name = str(account_data.get("nick_name") or "").strip()
        if not session_id or not account_id:
            raise RuntimeError("登录成功但缺少 session_id/account_id")
        return {"session_id": session_id, "account_id": account_id, "nick_name": nick_name}

    def fetch_activity_user(self, account_id, username):
        payload = request_payload(
            "GET",
            ACTIVITY_API_BASE,
            headers={
                "Host": "wxapi.hoolo.tv",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "User-Agent": WEBVIEW_USER_AGENT,
                "Origin": "https://tp.hoolo.tv",
                "X-Requested-With": "com.chinamcloud.wangjie.b87d8fb20e29a0328c6e21045e8b500e",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://tp.hoolo.tv/h5/tlread/index.html",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            },
            params={
                "s": "/home/TmApi/getUserInformation",
                "accountId": account_id,
                "username": username,
                "type": "jsonp",
            },
        )
        data = payload.get("data") if isinstance(payload.get("data"), dict) else {}
        return str(data.get("userid") or "").strip()

    def fetch_prize_records_with_debug(self, wx_open_id, limit=5):
        import random

        callback_prefix = f"jQuery{random.randint(10 ** 21, 10 ** 22 - 1)}_{int(time.time() * 1000)}"
        timestamp = str(int(time.time() * 1000))
        headers = {
            "Host": "wxapi.hoolo.tv",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 14; Redmi K20 Pro Build/UKQ1.240624.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36;xsb_xiaosatonglu;xsb_xiaosatonglu;1.0.90;native_app;7.3.2",
            "X-Requested-With": "com.chinamcloud.wangjie.b87d8fb20e29a0328c6e21045e8b500e",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Dest": "script",
            "Referer": "https://tp.hoolo.tv/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        params = {
            "s": "home/ChoujiangNew/getUserCj",
            "callback": callback_prefix,
            "openid": wx_open_id,
            "type_id": "122",
            "_": timestamp,
        }
        payload = request_payload(
            "GET",
            ACTIVITY_API_BASE,
            headers=headers,
            params=params,
        )
        code = str(payload.get("code", ""))
        raw_records = payload.get("msg") or []
        print(f"[中奖记录调试] wx_open_id={wx_open_id}, code={code}, raw_records={raw_records}")
        if code == "-1":
            return [], ""
        if code != "1":
            return [], f"接口返回code={code}, msg={payload.get('msg')}"
        if not isinstance(raw_records, list):
            return [], "接口返回数据格式异常"
        result = []
        for record in raw_records[:limit]:
            if not isinstance(record, dict):
                continue
            result.append({
                "prize_name": str(record.get("prize_name") or "").strip(),
                "code": str(record.get("code") or "").strip(),
                "remark": str(record.get("remark") or "").strip(),
                "create_time": str(record.get("create_time") or "").strip(),
            })
        return result, ""

    def fetch_prize_records_by_account_id(self, account_id, limit=5):
        import random

        callback_prefix = f"jQuery{random.randint(10 ** 21, 10 ** 22 - 1)}_{int(time.time() * 1000)}"
        timestamp = str(int(time.time() * 1000))
        headers = {
            "Host": "wxapi.hoolo.tv",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Lite Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.138 Mobile Safari/537.36;xsb_xiaosatonglu;xsb_xiaosatonglu;1.0.60;native_app;6.5.1",
            "X-Requested-With": "com.chinamcloud.wangjie.b87d8fb20e29a0328c6e21045e8b500e",
            "Referer": "https://tp.hoolo.tv/h5/tlread/index.html",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        params = {
            "s": "/home/ChoujiangNew/getUserCj",
            "callback": callback_prefix,
            "accountId": account_id,
            "type_id": "122",
            "_": timestamp,
        }
        payload = request_payload(
            "GET",
            ACTIVITY_API_BASE,
            headers=headers,
            params=params,
        )
        print(f"[中奖记录调试-accountId] account_id={account_id}, payload={payload}")
        code = str(payload.get("code", ""))
        raw_records = payload.get("msg") or []
        if code == "-1":
            return [], ""
        if code != "1":
            return [], f"接口返回code={code}, msg={payload.get('msg')}"
        result = []
        for record in (raw_records if isinstance(raw_records, list) else []):
            if not isinstance(record, dict):
                continue
            result.append({
                "prize_name": str(record.get("prize_name") or "").strip(),
                "code": str(record.get("code") or "").strip(),
                "remark": str(record.get("remark") or "").strip(),
                "create_time": str(record.get("create_time") or "").strip(),
            })
        return result, ""

    def probe(self, phone, password):
        code = self.get_code(phone, password)
        login_data = self.login(code)
        # account_id 就是中奖接口需要的 openid
        wx_open_id = login_data["account_id"]
        return {
            "display_name": sanitize_text(login_data["nick_name"] or phone, 32) or mask_phone(phone),
            "account_id": login_data["account_id"],
            "session_id": login_data["session_id"],
            "wx_open_id": wx_open_id,
            "wx_bound": bool(wx_open_id),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def get_config():
    pay_config = get_pay_config() if callable(get_pay_config) else {}
    pay_types = parse_pay_types(pay_config.get("pay_types") if isinstance(pay_config, dict) else {})
    if not pay_types:
        pay_types = parse_pay_types(
            middleware.bucketGet("dd_sign_config", "ma_pay_type")
            or middleware.bucketGet("dd_sign_config", "pay_types")
            or "alipay,wxpay"
        )
    zsm = str((pay_config.get("zsm") if isinstance(pay_config, dict) else "") or "").strip()
    if not zsm:
        zsm = str(middleware.bucketGet("dd_sign_config", "zsm") or middleware.bucketGet("G_SKM", "zsm") or "").strip()
    ma_pay_switch_raw = pay_config.get("ma_pay_switch") if isinstance(pay_config, dict) else None
    if ma_pay_switch_raw in (None, ""):
        ma_pay_switch_raw = middleware.bucketGet("dd_sign_config", "ma_pay_switch") or "false"
    return {
        "price": safe_decimal(middleware.bucketGet(BUCKET_CONFIG, "price") or "0.88", "0.88"),
        "coin": safe_int(middleware.bucketGet(BUCKET_CONFIG, "coin") or "0", 0),
        "ql_config": str(middleware.bucketGet(BUCKET_CONFIG, "ql_config") or "").strip(),
        "ql_envname": str(middleware.bucketGet(BUCKET_CONFIG, "ql_envname") or DEFAULT_ENV_NAME).strip() or DEFAULT_ENV_NAME,
        "use_daidai": parse_bool(middleware.bucketGet(BUCKET_CONFIG, "use_daidai") or "false"),
        "daidai_config": str(middleware.bucketGet(BUCKET_CONFIG, "daidai_config") or "").strip(),
        "daidai_group": str(middleware.bucketGet(BUCKET_CONFIG, "daidai_group") or PROJECT_NAME).strip() or PROJECT_NAME,
        "zsm": zsm,
        "ma_pay_switch": parse_bool(ma_pay_switch_raw),
        "pay_types": pay_types,
    }


def get_user_phones(user_id=None):
    current_user = str(user_id or userid)
    raw = middleware.bucketGet(BUCKET_USER, current_user) or ""
    return dedup_list([item.strip() for item in str(raw).split(",") if item.strip()])


def save_user_phones(phones, user_id=None):
    current_user = str(user_id or userid)
    normalized = dedup_list(phones)
    if normalized:
        middleware.bucketSet(BUCKET_USER, current_user, ",".join(normalized))
    else:
        middleware.bucketDel(BUCKET_USER, current_user)


def add_user_phone(phone, user_id=None):
    current = get_user_phones(user_id)
    if phone not in current:
        current.append(phone)
        save_user_phones(current, user_id)


def remove_user_phone(phone, user_id=None):
    current = [item for item in get_user_phones(user_id) if item != phone]
    save_user_phones(current, user_id)


def get_all_user_ids():
    try:
        return [str(item) for item in (middleware.bucketAllKeys(BUCKET_USER) or []) if str(item).strip()]
    except Exception:
        return []


def get_owner_of_phone(phone):
    for current_user in get_all_user_ids():
        if phone in get_user_phones(current_user):
            return str(current_user)
    return ""


def phone_used_by_other_users(phone, exclude_uid=None):
    for current_user in get_all_user_ids():
        if exclude_uid and str(current_user) == str(exclude_uid):
            continue
        if phone in get_user_phones(current_user):
            return True
    return False


def get_token_info(phone):
    raw = middleware.bucketGet(BUCKET_TOKEN, phone) or ""
    parts = str(raw).split("#")
    if len(parts) < 6:
        return {}
    return {
        "password": decode_text_blob(parts[0]),
        "display_name": parts[1].strip(),
        "account_id": parts[2].strip(),
        "session_id": parts[3].strip(),
        "wx_open_id": parts[4].strip(),
        "updated_at": parts[5].strip(),
    }


def save_token_info(phone, password, display_name, account_id, session_id, wx_open_id="", updated_at=""):
    middleware.bucketSet(
        BUCKET_TOKEN,
        phone,
        "#".join([
            encode_text_blob(password),
            sanitize_text(display_name, 32) or mask_phone(phone),
            str(account_id or "").strip(),
            str(session_id or "").strip(),
            str(wx_open_id or "").strip(),
            str(updated_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")).strip(),
        ]),
    )


def get_auth(phone):
    return str(middleware.bucketGet(BUCKET_AUTH, phone) or "").strip()


def save_auth(phone, expire_date):
    middleware.bucketSet(BUCKET_AUTH, phone, str(expire_date))


def is_authorized(phone):
    expire_date = parse_date(get_auth(phone))
    return bool(expire_date and expire_date >= today_date())


def get_auth_status_label(phone):
    expire_text = get_auth(phone)
    if not expire_text:
        return "未授权"
    expire_date = parse_date(expire_text)
    if not expire_date:
        return "授权异常"
    return "已授权" if expire_date >= today_date() else "已过期"


def build_env_value(phone, token_info):
    return f"{phone}#{token_info.get('password', '')}"


def build_env_remark(phone, owner_userid, expire_date, display_name):
    return "{}:{}|用户:{}|到期:{}|账号:{}".format(
        PROJECT_NAME,
        phone,
        owner_userid,
        expire_date,
        sanitize_text(display_name, 32) or mask_phone(phone),
    )


def resolve_panel_target(config=None, force_target=None):
    config = config or get_config()
    target = str(force_target or "").strip().lower()
    if target in {"qinglong", "daidai", "both"}:
        return target
    return "daidai" if config.get("use_daidai") else "qinglong"


def get_panel_target_name(target):
    return "呆呆面板" if target == "daidai" else "青龙/呆呆面板" if target == "both" else "青龙面板"


def get_panel_client(config=None, force_target=None):
    config = config or get_config()
    target = resolve_panel_target(config, force_target)
    if target == "daidai":
        if DadaiPanelClient is None:
            return None, "未安装 autman_huawei 模块，无法同步呆呆面板"
        client = DadaiPanelClient(
            os_var_name=config["ql_envname"],
            daidai_config_str=config["daidai_config"],
            config_bucket=BUCKET_CONFIG,
            config_key="daidai_config",
            env_name_key="ql_envname",
            group=config["daidai_group"],
            group_key="daidai_group",
            project_name=PROJECT_NAME,
        )
        if not client.is_configured():
            return None, f"未配置呆呆面板，请填写 {BUCKET_CONFIG}.daidai_config"
        if not client.get_token():
            return None, f"呆呆面板认证失败：{getattr(client, 'last_error', '') or '请检查 AppKey / AppSecret'}"
        return client, ""

    if QingLongClient is None:
        return None, "未安装 autman_huawei 模块，无法同步青龙"
    client = QingLongClient(
        os_var_name=config["ql_envname"],
        ql_config_str=config["ql_config"],
        config_bucket=BUCKET_CONFIG,
        config_key="ql_config",
        env_name_key="ql_envname",
    )
    if not client.is_configured():
        return None, f"未配置青龙，请填写 {BUCKET_CONFIG}.ql_config"
    if not client.get_token():
        return None, "青龙认证失败，请检查地址和 Client 信息"
    return client, ""


def sync_account_to_panel(phone, owner_userid=None, force_target=None):
    owner_userid = str(owner_userid or get_owner_of_phone(phone) or userid)
    token_info = get_token_info(phone)
    if not token_info:
        return False, "未找到本地账号数据"
    expire_date = get_auth(phone)
    if not expire_date:
        return False, "账号未授权，无法同步"
    config = get_config()
    target = resolve_panel_target(config, force_target)
    client, msg = get_panel_client(config, target)
    if not client:
        return False, msg
    env_value = build_env_value(phone, token_info)
    remark = build_env_remark(phone, owner_userid, expire_date, token_info.get("display_name") or mask_phone(phone))
    ok = client.update_env(username=phone, env_value=env_value, remark=remark, project_name=PROJECT_NAME) if target == "daidai" else client.update_env(username=phone, env_value=env_value, remark=remark)
    if ok:
        return True, f"已同步到{get_panel_target_name(target)}变量 {config['ql_envname']}"
    return False, "{}同步失败{}".format(get_panel_target_name(target), f"：{getattr(client, 'last_error', '')}" if target == "daidai" and getattr(client, "last_error", "") else "")


def delete_account_from_panel(phone, force_target=None):
    config = get_config()
    target = resolve_panel_target(config, force_target)
    if target == "both":
        messages = []
        for sub_target in ("qinglong", "daidai"):
            client, msg = get_panel_client(config, sub_target)
            if not client:
                messages.append(msg)
                continue
            messages.append(f"{get_panel_target_name(sub_target)}已删除" if client.delete_env(phone) else f"{get_panel_target_name(sub_target)}删除失败")
        return True, "；".join(messages)
    client, msg = get_panel_client(config, target)
    if not client:
        return False, msg
    return (True, f"已从{get_panel_target_name(target)}删除变量") if client.delete_env(phone) else (False, f"{get_panel_target_name(target)}删除失败")


def delete_local_account(phone, user_id=None):
    current_user = str(user_id or get_owner_of_phone(phone) or userid)
    middleware.bucketDel(BUCKET_TOKEN, phone)
    middleware.bucketDel(BUCKET_AUTH, phone)
    remove_user_phone(phone, current_user)


def get_user_points(user_id=None):
    current_user = str(user_id or userid)
    return {
        "dd_sign_coin": safe_int(middleware.bucketGet("dd_sign_coin", current_user) or 0, 0),
        "dd_sign_points": safe_int(middleware.bucketGet("dd_sign_points", current_user) or 0, 0),
        "total": safe_int(middleware.bucketGet("dd_sign_coin", current_user) or 0, 0) + safe_int(middleware.bucketGet("dd_sign_points", current_user) or 0, 0),
    }


def save_user_points(user_id, sign_coin, sign_points):
    middleware.bucketSet("dd_sign_coin", str(user_id), str(sign_coin))
    middleware.bucketSet("dd_sign_points", str(user_id), str(sign_points))


def deduct_user_points(user_id, required_points):
    points = get_user_points(user_id)
    if points["total"] < required_points:
        return False, points["total"]
    remain_coin = points["dd_sign_coin"]
    remain_points = points["dd_sign_points"]
    if remain_coin >= required_points:
        remain_coin -= required_points
    else:
        remain_points -= required_points - remain_coin
        remain_coin = 0
    save_user_points(user_id, remain_coin, remain_points)
    return True, remain_coin + remain_points


def parse_waitpay_amount(result):
    if result is None:
        return Decimal("0")
    if isinstance(result, dict):
        return safe_decimal(result.get("Money") if result.get("Money") is not None else result.get("money"), "0")
    text = str(result).strip()
    try:
        return parse_waitpay_amount(json.loads(text))
    except Exception:
        if "收款金额￥" in text:
            try:
                return safe_decimal(text.split("收款金额￥", 1)[1].splitlines()[0].strip(), "0")
            except Exception:
                return Decimal("0")
    return Decimal("0")


def choose_ma_pay_type(config):
    items = list((config.get("pay_types") or {}).items())
    if not items:
        return None, None
    if len(items) == 1:
        return items[0]
    lines = ["=====选择码支付方式====="]
    for index, item in enumerate(items, 1):
        lines.append(f"[{index}] {item[1]}")
    lines.append('回复序号选择，回复 "q" 取消')
    lines.append("==================")
    choice = read_input("\n".join(lines), 120000)
    if not choice or not choice.isdigit():
        return None, None
    idx = int(choice) - 1
    return items[idx] if 0 <= idx < len(items) else (None, None)


def process_qrcode_payment(total_price):
    config = get_config()
    if total_price <= 0:
        return True
    if not config["zsm"]:
        sender.reply("❌ 未配置收款码，请联系管理员")
        return False
    sender.reply(f"=====扫码支付=====\n💰 金额: {format_money(total_price)} 元\n请使用微信扫码支付\n回复 q 可取消")
    sender.replyImage(config["zsm"])
    payment_result = sender.waitPay(timeout=PAY_TIMEOUT, exitcode="q")
    if str(payment_result).strip().lower() == "q":
        sender.reply("✅ 已取消支付")
        return False
    paid_amount = parse_waitpay_amount(payment_result)
    if paid_amount + Decimal("0.01") < total_price:
        sender.reply(f"❌ 支付金额不足\n应付: {format_money(total_price)} 元\n实付: {format_money(paid_amount)} 元")
        return False
    sender.reply("✅ 支付成功")
    return True


def ma_payment_flow(target_label, months, amount, config):
    if amount <= 0:
        return True
    if MaPayClient is None:
        sender.reply("❌ 未安装 autman_huawei 模块，无法使用码支付")
        return False
    pay_type_key, pay_type_name = choose_ma_pay_type(config)
    if not pay_type_key:
        sender.reply("✅ 已取消码支付")
        return False
    client = MaPayClient()
    if not client.is_configured():
        sender.reply("❌ 码支付配置不完整，请检查 dd_sign_config")
        return False
    out_trade_no = f"XSTL{int(time.time())}{str(userid)[-4:]}"
    subject = f"{PROJECT_NAME}授权-{sanitize_text(target_label, 18)}"
    order_result = client.create_order(float(amount), pay_type_key, out_trade_no, subject, str(userid))
    if order_result.get("error"):
        sender.reply(f"❌ 创建码支付订单失败: {order_result['error']}")
        return False
    pay_url = order_result.get("pay_url") or ""
    if not pay_url:
        sender.reply("❌ 未获取到码支付链接")
        return False
    qr_url = generate_qrcode_url(pay_url) if generate_qrcode_url else ""
    if qr_url:
        try:
            sender.replyImage(qr_url)
        except Exception:
            sender.reply(f"二维码发送失败，请打开下方链接完成支付：\n{pay_url}")
    sender.reply(f"=====码支付=====\n👁 账号: {target_label}\n⏰ 授权: {months}个月\n💰 金额: ¥{format_money(amount)}\n💳 方式: {pay_type_name}\n回复 q 取消")
    for _ in range(PAY_POLL_TIMES):
        result = sender.listen(PAY_POLL_INTERVAL_MS)
        if str(result).strip().lower() == "q":
            sender.reply("✅ 已取消支付")
            return False
        if client.is_paid(out_trade_no):
            sender.reply(f"✅ 码支付成功，已完成 {pay_type_name} 支付")
            return True
    sender.reply("❌ 支付超时，请重新发起")
    return False


def point_payment_flow(target_label, months, required_points):
    if required_points <= 0:
        return True
    current_points = get_user_points(userid)
    if current_points["total"] < required_points:
        sender.reply(f"❌ 积分不足，需要 {required_points}，当前 {current_points['total']}")
        return False
    confirm = read_input(f"=====积分支付确认=====\n📱 目标: {target_label}\n⏰ 时长: {months}个月\n🎟 扣除: {required_points}积分\n📊 支付后剩余: {current_points['total'] - required_points}积分\n回复 y 确认，回复 q 取消", 60000)
    if not confirm or confirm.lower() != "y":
        sender.reply("✅ 已取消积分支付")
        return False
    ok, remain_points = deduct_user_points(userid, required_points)
    if not ok:
        sender.reply("❌ 积分扣减失败")
        return False
    sender.reply(f"✅ 积分支付成功，剩余 {remain_points} 积分")
    return True


def handle_authorize_payment(target_label, months, account_count=1):
    config = get_config()
    total_price = config["price"] * Decimal(months) * Decimal(account_count)
    total_coin = config["coin"] * months * account_count
    if total_price <= 0 and total_coin <= 0:
        return True
    options = []
    handlers = {}
    idx = 1
    if total_price > 0 and config.get("zsm"):
        options.append(f"[{idx}] 微信收款码 ￥{format_money(total_price)}")
        handlers[str(idx)] = "wechat"
        idx += 1
    if total_price > 0 and config.get("ma_pay_switch") and config.get("pay_types"):
        options.append(f"[{idx}] 码支付 ￥{format_money(total_price)}")
        handlers[str(idx)] = "ma"
        idx += 1
    if total_coin > 0:
        options.append(f"[{idx}] 积分支付 {total_coin}")
        handlers[str(idx)] = "coin"
    choice = read_input("=====选择授权方式=====\n" + f"📱 目标: {target_label}\n⏰ 时长: {months}个月\n💰 金额: {format_money(total_price)} 元\n🎟 积分: {total_coin}\n------------------\n" + "\n".join(options) + "\n回复数字选择，回复 q 退出", 120000)
    if not choice:
        sender.reply("✅ 已取消授权")
        return False
    selected = handlers.get(choice)
    if selected == "wechat":
        return process_qrcode_payment(total_price)
    if selected == "ma":
        return ma_payment_flow(target_label, months, total_price, config)
    if selected == "coin":
        return point_payment_flow(target_label, months, total_coin)
    sender.reply("❌ 无效选择")
    return False
def calc_new_expire(months, current_expire=None):
    base_date = current_expire if current_expire and current_expire >= today_date() else today_date()
    return base_date + timedelta(days=int(months) * 30)


def handle_authorize_payment(target_label, months, account_count=1):
    config = get_config()
    total_price = config["price"] * Decimal(months) * Decimal(account_count)
    total_coin = config["coin"] * months * account_count
    if total_price <= 0 and total_coin <= 0:
        return True
    options = []
    handlers = {}
    idx = 1
    if total_price > 0 and config.get("zsm"):
        options.append(f"[{idx}] 微信收款码 ￥{format_money(total_price)}")
        handlers[str(idx)] = "wechat"
        idx += 1
    if total_price > 0 and config.get("ma_pay_switch") and config.get("pay_types"):
        options.append(f"[{idx}] 码支付 ￥{format_money(total_price)}")
        handlers[str(idx)] = "ma"
        idx += 1
    if total_coin > 0:
        options.append(f"[{idx}] 积分支付 {total_coin}")
        handlers[str(idx)] = "coin"
    if not handlers:
        sender.reply("❌ 未配置任何可用支付方式")
        return False
    choice = read_input(
        "=====选择授权方式=====\n"
        f"📫 目标: {target_label}\n"
        f"⏳ 时长: {months}个月\n"
        f"💵 金额: {format_money(total_price)} 元\n"
        f"🪙 积分: {total_coin}\n"
        "------------------\n"
        + "\n".join(options)
        + "\n回复数字选择，回复 q 退出",
        120000,
    )
    if not choice:
        sender.reply("✅ 已取消授权")
        return False
    selected = handlers.get(choice)
    if selected == "wechat":
        return process_qrcode_payment(total_price)
    if selected == "ma":
        return ma_payment_flow(target_label, months, total_price, config)
    if selected == "coin":
        return point_payment_flow(target_label, months, total_coin)
    sender.reply("❌ 无效选择")
    return False


def complete_authorization(phone, months, owner_userid=None, force_target=None):
    owner_userid = str(owner_userid or get_owner_of_phone(phone) or userid)
    current_expire = parse_date(get_auth(phone))
    renew_type = "续费" if current_expire and current_expire >= today_date() else "新授权"
    expire_date = calc_new_expire(months, current_expire)
    expire_text = expire_date.strftime("%Y-%m-%d")
    save_auth(phone, expire_text)
    sync_ok, sync_msg = sync_account_to_panel(phone, owner_userid, force_target=force_target)
    return {
        "phone": phone,
        "expire_date": expire_text,
        "renew_type": renew_type,
        "sync_ok": sync_ok,
        "sync_msg": sync_msg,
    }


def push_account_notification(target_uid, phone, content):
    token_info = get_token_info(phone)
    display_name = token_info.get("display_name") or mask_phone(phone)
    push_msg = (
        "=====潇洒桐庐账号通知=====\n"
        f"📫 账号: {display_name}\n"
        f"📱 手机: {mask_phone(phone)}\n"
        f"{content}\n"
        "======================"
    )
    pushed = False
    for platform in ["wb", "tg", "qq", "qb", "wx"]:
        try:
            middleware.push(platform, "", str(target_uid), "", push_msg)
            pushed = True
        except Exception:
            pass
    return pushed


def build_expired_auth_notification(expire_text):
    return (
        "⚠️ 授权已过期\n"
        "------------------\n"
        f"📆 到期时间: {expire_text}\n"
        "🔔 请及时续费授权"
    )


def build_expiring_auth_notification(expire_text, days_left):
    remind_text = "今天到期" if days_left == 0 else f"剩余{days_left}天"
    return (
        "⚠️ 授权即将到期\n"
        "------------------\n"
        f"📆 到期时间: {expire_text}\n"
        f"⏰ 到期提醒: {remind_text}\n"
        "🔔 请及时续费授权"
    )


def push_auth_status_notifications():
    for current_user in get_all_user_ids():
        for phone in dedup_list(get_user_phones(current_user)):
            expire_text = str(get_auth(phone) or "").strip()
            expire_date = parse_date(expire_text)
            if not expire_date:
                continue
            days_left = (expire_date - today_date()).days
            if days_left < 0:
                content = build_expired_auth_notification(expire_text)
            elif days_left <= 3:
                content = build_expiring_auth_notification(expire_text, days_left)
            else:
                continue
            push_account_notification(current_user, phone, content)


def parse_bind_lines(raw_text):
    items = []
    errors = []
    seen = set()
    lines = str(raw_text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for index, line in enumerate(lines, 1):
        text = str(line or "").strip()
        if not text:
            continue
        if "#" not in text:
            errors.append(f"[{index}] 格式错误，请使用 手机号#密码")
            continue
        phone, password = text.split("#", 1)
        phone = str(phone or "").strip()
        password = str(password or "").strip()
        if not re.fullmatch(r"1[3-9]\d{9}", phone):
            errors.append(f"[{index}] 手机号格式错误: {phone}")
            continue
        if not password:
            errors.append(f"[{index}] 密码不能为空")
            continue
        if phone in seen:
            continue
        items.append({"phone": phone, "password": password})
        seen.add(phone)
    return items, errors


def bind_single_account(phone, password, old_phone=None):
    phone = str(phone or "").strip()
    password = str(password or "").strip()
    old_phone = str(old_phone or "").strip()
    if not re.fullmatch(r"1[3-9]\d{9}", phone):
        return False, "手机号格式错误"
    if not password:
        return False, "密码不能为空"
    if old_phone and old_phone != phone:
        return False, "更新账号时请保持手机号一致，新号请直接使用登录指令"
    owner_user = get_owner_of_phone(phone)
    existed_before = bool(get_token_info(phone))
    if owner_user and owner_user != userid and phone != old_phone:
        return False, "该账号已被其他用户绑定"
    try:
        probe_data = XiaoSaTongLuClient().probe(phone, password)
    except Exception as exc:
        return False, sanitize_text(exc, 120) or "登录验证失败"
    save_token_info(
        phone,
        password,
        probe_data.get("display_name") or mask_phone(phone),
        probe_data.get("account_id") or "",
        probe_data.get("session_id") or "",
        probe_data.get("wx_open_id") or "",
        probe_data.get("updated_at") or "",
    )
    add_user_phone(phone, userid)
    sync_message = ""
    if is_authorized(phone):
        _, sync_message = sync_account_to_panel(phone, userid)
    return True, {
        "phone": phone,
        "display_name": probe_data.get("display_name") or mask_phone(phone),
        "wx_bound": bool(probe_data.get("wx_bound")),
        "wx_open_id": probe_data.get("wx_open_id") or "",
        "updated_at": probe_data.get("updated_at") or "",
        "sync_message": sync_message,
        "existed": existed_before or bool(old_phone),
    }


def bind_account():
    raw_text = read_input(
        "=====潇洒桐庐登录=====\n"
        "请输入: 手机号#密码\n"
        "支持多号换行批量提交\n"
        "仅支持 # 分隔，不兼容 &\n"
        "回复 q 取消\n=================="
    )
    if not raw_text:
        sender.reply("✅ 已取消登录")
        return
    items, errors = parse_bind_lines(raw_text)
    if not items:
        sender.reply("❌ 未识别到有效账号\n" + ("\n".join(errors[:5]) if errors else ""))
        return
    success_items = []
    fail_items = list(errors)
    for index, item in enumerate(items, 1):
        ok, result = bind_single_account(item["phone"], item["password"])
        if ok:
            success_items.append(
                f"[{index}] {result['display_name']} | 微信活动: {'已绑定' if result['wx_bound'] else '未绑定'}"
            )
        else:
            fail_items.append(f"[{index}] {mask_phone(item['phone'])} | {result}")
    lines = [
        "=====登录结果=====",
        f"✅ 成功: {len(success_items)}",
        f"❌ 失败: {len(fail_items)}",
        "------------------",
    ]
    lines.extend(success_items)
    lines.extend(fail_items)
    lines.append("==================")
    sender.reply("\n".join(lines))


def probe_account_status(phone, refresh_live=True):
    token_info = get_token_info(phone)
    status = {
        "phone": phone,
        "display_name": token_info.get("display_name") or mask_phone(phone),
        "account_id": token_info.get("account_id") or "",
        "session_id": token_info.get("session_id") or "",
        "wx_open_id": token_info.get("wx_open_id") or "",
        "wx_bound": bool(token_info.get("wx_open_id")),
        "updated_at": token_info.get("updated_at") or "",
        "expire_text": get_auth(phone) or "",
        "auth_status": get_auth_status_label(phone),
        "login_ok": None,
        "error_message": "",
        "prize_records": [],
        "prize_fetch_error": "",
    }
    password = token_info.get("password") or ""
    if not token_info:
        status["login_ok"] = False
        status["error_message"] = "未找到本地账号数据"
        return status
    if not password:
        status["login_ok"] = False
        status["error_message"] = "本地密码缺失，请重新登录"
        return status
    if not refresh_live:
        return status
    try:
        client = XiaoSaTongLuClient()
        probe_data = client.probe(phone, password)
        save_token_info(
            phone,
            password,
            probe_data.get("display_name") or status["display_name"],
            probe_data.get("account_id") or status["account_id"],
            probe_data.get("session_id") or status["session_id"],
            probe_data.get("wx_open_id") or "",
            probe_data.get("updated_at") or "",
        )
        status.update({
            "display_name": probe_data.get("display_name") or status["display_name"],
            "account_id": probe_data.get("account_id") or status["account_id"],
            "session_id": probe_data.get("session_id") or status["session_id"],
            "wx_open_id": probe_data.get("wx_open_id") or "",
            "wx_bound": bool(probe_data.get("wx_bound")),
            "updated_at": probe_data.get("updated_at") or status["updated_at"],
            "login_ok": True,
            "error_message": "",
        })
        if status["wx_open_id"]:
            try:
                records, fetch_error = client.fetch_prize_records_with_debug(status["wx_open_id"], limit=5)
                status["prize_records"] = records
                status["prize_fetch_error"] = fetch_error
            except Exception as fetch_exc:
                status["prize_records"] = []
                status["prize_fetch_error"] = sanitize_text(fetch_exc, 120) or "获取中奖记录异常"
    except Exception as exc:
        status["login_ok"] = False
        status["error_message"] = sanitize_text(exc, 120) or "登录校验失败"
    return status


def build_query_message(status):
    prize_emoji = {"红包0.5": "🧧", "红包1": "🧧", "红包": "🧧"}
    lines = [
        "=====潇洒桐庐账号=====",
        f"📫 账号: {status.get('display_name') or mask_phone(status.get('phone'))}",
        f"📱 手机: {mask_phone(status.get('phone'))}",
        f"📌 授权: {status.get('auth_status') or '未知'}",
        f"📆 到期: {status.get('expire_text') or '未授权'}",
        f"🛰 微信活动: {'已绑定' if status.get('wx_bound') else '未绑定'}",
    ]
    if status.get("updated_at"):
        lines.append(f"🕒 最近更新: {status['updated_at']}")
    if status.get("login_ok") is True:
        lines.append("✅ 登录校验: 正常")
    elif status.get("login_ok") is False:
        lines.append(f"❌ 登录校验: {status.get('error_message') or '失败'}")
    else:
        lines.append("ℹ️ 登录校验: 未执行")

    prize_records = status.get("prize_records") or []
    prize_fetch_error = status.get("prize_fetch_error") or ""
    if prize_records:
        lines.append("--------------------")
        lines.append(f"🎁 最近中奖记录 (共{len(prize_records)}笔):")
        for idx, rec in enumerate(prize_records, 1):
            prize_name = rec.get("prize_name") or "未知"
            create_time = rec.get("create_time") or ""
            code = rec.get("code") or ""
            remark = rec.get("remark") or ""
            if create_time:
                try:
                    dt = datetime.strptime(create_time, "%Y-%m-%d %H:%M:%S")
                    time_str = dt.strftime("%m-%d %H:%M")
                except Exception:
                    time_str = create_time
            else:
                time_str = ""
            emoji = prize_emoji.get(prize_name, "🎉")
            status_tag = ""
            if remark == "ACCEPTED":
                status_tag = " [已领取]"
            elif remark:
                status_tag = f" [{remark}]"
            code_short = code[-8:] if code else ""
            if time_str:
                lines.append(f"  {emoji}{prize_name}{status_tag} | {time_str} | {code_short}")
            else:
                lines.append(f"  {emoji}{prize_name}{status_tag} | {code_short}")
    elif prize_fetch_error:
        lines.append("--------------------")
        lines.append(f"🎁 中奖记录: 获取失败 {prize_fetch_error}")
    elif status.get("wx_bound"):
        lines.append("--------------------")
        lines.append("🎁 中奖记录: 暂无记录")

    if not status.get("wx_bound"):
        lines.append("🔔 未获取到活动用户信息，可能还没有在活动页完成微信绑定")
    lines.append("==================")
    return "\n".join(lines)


def select_phones(phones, title, allow_all=True):
    phones = dedup_list(phones)
    if not phones:
        return []
    if len(phones) == 1:
        return list(phones)
    lines = [f"====={title}====="]
    if allow_all:
        lines.append("[0] 全部账号")
    for index, phone in enumerate(phones, 1):
        info = get_token_info(phone)
        lines.append(
            f"[{index}] {(info.get('display_name') or mask_phone(phone))} | "
            f"{get_auth_status_label(phone)} | {get_auth(phone) or '未授权'}"
        )
    lines.append("支持格式: 1 或 1,2 或 1-3")
    lines.append("回复 q 取消")
    lines.append("==================")
    choice = read_input("\n".join(lines), 120000)
    if not choice:
        return []
    if allow_all and choice == "0":
        return list(phones)
    indices = parse_selection(choice, len(phones))
    if not indices:
        sender.reply("❌ 无效选择")
        return []
    return [phones[index] for index in indices]


def query_accounts():
    phones = get_user_phones()
    if not phones:
        sender.reply("❌ 您还没有绑定任何账号，请先发送“潇洒桐庐登录”")
        return
    selected = select_phones(phones, "选择查询账号", allow_all=True)
    if not selected:
        sender.reply("✅ 已取消查询")
        return
    for phone in selected:
        sender.reply(build_query_message(probe_account_status(phone, refresh_live=True)))


def get_pending_authorization_phones(phones=None):
    source = phones if phones is not None else get_user_phones()
    return [phone for phone in dedup_list(source) if not is_authorized(phone)]


def build_manage_accounts_message():
    phones = get_user_phones()
    points = get_user_points(userid)
    lines = [
        "=====账号管理=====",
        f"📝 绑定账号: {len(phones)}个",
        f"🪙 当前积分: {points['total']}",
        "--------------------",
    ]
    for index, phone in enumerate(phones, 1):
        info = get_token_info(phone)
        lines.append(
            f"[{index}] {(info.get('display_name') or mask_phone(phone))} | "
            f"{get_auth_status_label(phone)} | {get_auth(phone) or '未授权'}"
        )
    lines.extend([
        "--------------------",
        "[0] 全部账号授权（支付）",
        "[9997] 同步已授权账号",
        "[9998] 删除全部账号",
        "[9999] 未授权账号授权（支付）",
        "支持格式: 1 或 1,2 或 1-3",
        "回复 q 退出",
        "====================",
    ])
    return "\n".join(lines)


def apply_authorization(phone, months, owner_userid=None, force_target=None):
    return complete_authorization(phone, months, owner_userid=owner_userid, force_target=force_target)


def handle_authorize_phones(phones, owner_userid=None, free_mode=False, title="选中账号"):
    phones = dedup_list(phones)
    if not phones:
        sender.reply("❌ 没有可授权的账号")
        return
    months = prompt_months()
    if not months:
        return
    if not free_mode and not handle_authorize_payment(title, months, len(phones)):
        return
    success_count = 0
    sync_fail_count = 0
    expire_samples = []
    for phone in phones:
        result = apply_authorization(phone, months, owner_userid=owner_userid, force_target=None)
        success_count += 1
        if not result["sync_ok"]:
            sync_fail_count += 1
        if len(expire_samples) < 3:
            expire_samples.append(f"{mask_phone(phone)}->{result['expire_date']}")
    lines = [
        "=====授权完成=====",
        f"📫 目标: {title}",
        f"✅ 成功: {success_count}",
        f"🚫 同步失败: {sync_fail_count}",
        f"📆 时长: {months}个月",
    ]
    if expire_samples:
        lines.append("📌 示例: " + " | ".join(expire_samples))
    lines.append("==================")
    sender.reply("\n".join(lines))


def sync_phones(phones, force_target=None, owner_userid=None):
    phones = dedup_list(phones)
    if not phones:
        sender.reply("❌ 没有可同步的账号")
        return
    config = get_config()
    target = resolve_panel_target(config, force_target)
    target_name = get_panel_target_name(target)
    success_count = 0
    skip_count = 0
    fail_count = 0
    for phone in phones:
        if not is_authorized(phone):
            skip_count += 1
            continue
        ok, _ = sync_account_to_panel(phone, owner_userid or get_owner_of_phone(phone) or userid, force_target=target)
        if ok:
            success_count += 1
        else:
            fail_count += 1
    sender.reply(
        "=====同步完成=====\n"
        f"🚀 目标: {target_name}\n"
        f"✅ 成功: {success_count}\n"
        f"⏰ 跳过未授权: {skip_count}\n"
        f"❌ 失败: {fail_count}\n"
        "=================="
    )


def delete_phones(phones, force_target="both", show_reply=True):
    phones = dedup_list(phones)
    if not phones:
        if show_reply:
            sender.reply("❌ 没有可删除的账号")
        return {"deleted": 0, "panel_fail": 0}
    deleted = 0
    panel_fail = 0
    for phone in phones:
        ok, _ = delete_account_from_panel(phone, force_target=force_target)
        if not ok:
            panel_fail += 1
        delete_local_account(phone, get_owner_of_phone(phone) or userid)
        deleted += 1
    result = {"deleted": deleted, "panel_fail": panel_fail}
    if show_reply:
        sender.reply(
            "=====删除完成=====\n"
            f"🗑 已删除: {deleted}\n"
            f"🚫 面板删除失败: {panel_fail}\n"
            "=================="
        )
    return result


def manage_accounts():
    phones = get_user_phones()
    if not phones:
        sender.reply("❌ 您还没有绑定任何账号，请先发送“潇洒桐庐登录”")
        return
    choice = read_input(build_manage_accounts_message(), 120000)
    if not choice:
        sender.reply("✅ 已退出管理")
        return
    if choice == "0":
        handle_authorize_phones(phones, owner_userid=userid, title="全部账号")
        return
    if choice == "9997":
        sync_phones(phones, owner_userid=userid)
        return
    if choice == "9998":
        confirm = read_input(
            f"=====删除全部账号=====\n共 {len(phones)} 个账号\n回复 y 确认，回复 q 取消\n==================",
            60000,
        )
        if confirm and confirm.lower() == "y":
            delete_phones(phones, force_target="both", show_reply=True)
        else:
            sender.reply("✅ 已取消删除")
        return
    if choice == "9999":
        pending = get_pending_authorization_phones(phones)
        if not pending:
            sender.reply("✅ 当前没有未授权账号")
            return
        handle_authorize_phones(pending, owner_userid=userid, title="未授权账号")
        return

    indices = parse_selection(choice, len(phones))
    if not indices:
        sender.reply("❌ 无效选择")
        return
    selected = [phones[index] for index in indices]
    if len(selected) == 1:
        phone = selected[0]
        display_name = get_token_info(phone).get("display_name") or mask_phone(phone)
        action = read_input(
            "=====账号操作=====\n"
            f"📫 账号: {display_name}\n"
            f"📆 到期: {get_auth(phone) or '未授权'}\n"
            "[1] 授权账号\n"
            "[2] 更新密码\n"
            "[3] 删除账号\n"
            "[4] 上传默认面板\n"
            "[5] 上传青龙\n"
            "[6] 上传呆呆\n"
            "[7] 查询状态\n"
            "回复 q 返回\n==================",
            120000,
        )
        if not action:
            sender.reply("✅ 已返回")
            return
        if action == "1":
            handle_authorize_phones([phone], owner_userid=userid, title=display_name)
        elif action == "2":
            raw = read_input(
                f"请输入新的账号信息，格式必须为 {phone}#密码\n回复 q 取消",
                120000,
            )
            if not raw:
                sender.reply("✅ 已取消更新")
                return
            items, errors = parse_bind_lines(raw)
            if errors:
                sender.reply("❌ " + "；".join(errors[:3]))
                return
            if len(items) != 1 or items[0]["phone"] != phone:
                sender.reply("❌ 更新密码时必须提交当前手机号对应的 手机号#密码")
                return
            ok, result = bind_single_account(phone, items[0]["password"], old_phone=phone)
            if ok:
                sender.reply(
                    "✅ 更新成功\n"
                    f"📫 账号: {result['display_name']}\n"
                    f"🛰 微信活动: {'已绑定' if result['wx_bound'] else '未绑定'}\n"
                    f"{result['sync_message'] or ''}"
                )
            else:
                sender.reply(f"❌ 更新失败: {result}")
        elif action == "3":
            confirm = read_input(
                f"确认删除 {display_name} 吗？回复 y 确认，回复 q 取消",
                60000,
            )
            if confirm and confirm.lower() == "y":
                delete_phones([phone], force_target="both", show_reply=True)
            else:
                sender.reply("✅ 已取消删除")
        elif action == "4":
            sync_phones([phone], force_target=None, owner_userid=userid)
        elif action == "5":
            sync_phones([phone], force_target="qinglong", owner_userid=userid)
        elif action == "6":
            sync_phones([phone], force_target="daidai", owner_userid=userid)
        elif action == "7":
            sender.reply(build_query_message(probe_account_status(phone, refresh_live=True)))
        else:
            sender.reply("❌ 无效选择")
        return

    action = read_input(
        "=====批量操作=====\n"
        f"已选 {len(selected)} 个账号\n"
        "[1] 批量授权\n"
        "[2] 批量删除\n"
        "[3] 上传默认面板\n"
        "[4] 上传青龙\n"
        "[5] 上传呆呆\n"
        "[6] 查询状态\n"
        "回复 q 返回\n==================",
        120000,
    )
    if not action:
        sender.reply("✅ 已返回")
        return
    if action == "1":
        handle_authorize_phones(selected, owner_userid=userid, title=f"选中账号({len(selected)}个)")
    elif action == "2":
        confirm = read_input(
            f"确认删除这 {len(selected)} 个账号吗？回复 y 确认，回复 q 取消",
            60000,
        )
        if confirm and confirm.lower() == "y":
            delete_phones(selected, force_target="both", show_reply=True)
        else:
            sender.reply("✅ 已取消删除")
    elif action == "3":
        sync_phones(selected, force_target=None, owner_userid=userid)
    elif action == "4":
        sync_phones(selected, force_target="qinglong", owner_userid=userid)
    elif action == "5":
        sync_phones(selected, force_target="daidai", owner_userid=userid)
    elif action == "6":
        for phone in selected:
            sender.reply(build_query_message(probe_account_status(phone, refresh_live=True)))
    else:
        sender.reply("❌ 无效选择")


def collect_all_phones():
    phones = []
    for current_user in get_all_user_ids():
        phones.extend(get_user_phones(current_user))
    return dedup_list(phones)


def admin_authorize():
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限")
        return
    choice = read_input(
        "=====管理员授权=====\n"
        "[1] 指定用户授权\n"
        "[2] 全部用户授权\n"
        "[3] 全部未授权账号\n"
        "回复 q 取消\n==================",
        120000,
    )
    if not choice:
        sender.reply("✅ 已取消管理员授权")
        return
    if choice == "1":
        target_userid = read_input("请输入目标用户ID，回复 q 取消：", 120000)
        if not target_userid:
            sender.reply("✅ 已取消管理员授权")
            return
        phones = get_user_phones(target_userid)
        if not phones:
            sender.reply("❌ 该用户没有绑定任何账号")
            return
        selected = select_phones(phones, f"选择 {target_userid} 的账号", allow_all=True)
        if not selected:
            sender.reply("✅ 已取消管理员授权")
            return
        handle_authorize_phones(selected, owner_userid=target_userid, free_mode=True, title=f"用户{target_userid}账号")
        return
    if choice == "2":
        phones = collect_all_phones()
        if not phones:
            sender.reply("❌ 当前没有任何绑定账号")
            return
        handle_authorize_phones(phones, owner_userid=None, free_mode=True, title=f"全部用户账号({len(phones)}个)")
        return
    if choice == "3":
        phones = get_pending_authorization_phones(collect_all_phones())
        if not phones:
            sender.reply("✅ 当前没有未授权账号")
            return
        handle_authorize_phones(phones, owner_userid=None, free_mode=True, title=f"全部未授权账号({len(phones)}个)")
        return
    sender.reply("❌ 无效选择")


def cmd_upload(force_target=None):
    current_phones = get_user_phones(userid)
    if not sender.isAdmin():
        if not current_phones:
            sender.reply("❌ 您还没有绑定任何账号")
            return
        sync_phones(current_phones, force_target=force_target, owner_userid=userid)
        return
    choice = read_input(
        "=====上传账号=====\n"
        "[1] 上传我的已授权账号\n"
        "[2] 上传全部用户已授权账号\n"
        "回复 q 取消\n==================",
        120000,
    )
    if not choice:
        sender.reply("✅ 已取消上传")
        return
    if choice == "1":
        if not current_phones:
            sender.reply("❌ 您还没有绑定任何账号")
            return
        sync_phones(current_phones, force_target=force_target, owner_userid=userid)
        return
    if choice == "2":
        phones = collect_all_phones()
        if not phones:
            sender.reply("❌ 当前没有任何绑定账号")
            return
        sync_phones(phones, force_target=force_target, owner_userid=None)
        return
    sender.reply("❌ 无效选择")


def clean_accounts():
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限")
        return
    users = get_all_user_ids()
    if not users:
        sender.reply("❌ 当前没有任何绑定用户")
        return

    kept_count = 0
    cleaned_count = 0
    expired_count = 0
    invalid_count = 0
    warning_count = 0
    notified_users = set()

    for current_user in users:
        remain_phones = []
        for phone in dedup_list(get_user_phones(current_user)):
            token_info = get_token_info(phone)
            if not token_info or not token_info.get("password"):
                delete_phones([phone], force_target="both", show_reply=False)
                cleaned_count += 1
                invalid_count += 1
                continue

            expire_text = str(get_auth(phone) or "").strip()
            expire_date = parse_date(expire_text)
            if expire_date:
                days_left = (expire_date - today_date()).days
                if days_left < 0:
                    if push_account_notification(current_user, phone, build_expired_auth_notification(expire_text)):
                        notified_users.add(str(current_user))
                elif days_left <= 3:
                    warning_count += 1
                    if push_account_notification(current_user, phone, build_expiring_auth_notification(expire_text, days_left)):
                        notified_users.add(str(current_user))

            if not is_authorized(phone):
                delete_phones([phone], force_target="both", show_reply=False)
                cleaned_count += 1
                expired_count += 1
                continue

            status = probe_account_status(phone, refresh_live=True)
            if not status.get("login_ok"):
                delete_phones([phone], force_target="both", show_reply=False)
                cleaned_count += 1
                invalid_count += 1
                continue

            remain_phones.append(phone)
            kept_count += 1

        save_user_phones(remain_phones, current_user)

    sender.reply(
        "=====清理完成=====\n"
        f"✅ 保留账号: {kept_count}\n"
        f"🧹 清理账号: {cleaned_count}\n"
        f"⚠️ 临期提醒: {warning_count}\n"
        f"📨 已推送用户: {len(notified_users)}\n"
        f"⌛ 过期清理: {expired_count}\n"
        f"📵 失效清理: {invalid_count}\n"
        "=================="
    )


def show_tutorial():
    sender.reply(
        "===========潇洒桐庐教程===========\n"
        "1. 发送“潇洒桐庐登录”\n"
        "2. 按格式提交: 手机号#密码\n"
        "3. 支持多号换行批量提交\n"
        "4. 只认 #，不兼容 手机号&密码\n"
        "5. 登录时会实时校验账号，并尝试获取活动用户信息\n"
        "6. 授权后会同步到面板变量 G_XSTL_TOKEN，内容固定为 手机号#密码\n"
        "7. 上传命令严格区分目标:\n"
        "   潇洒桐庐上传青龙 -> 只上传青龙\n"
        "   潇洒桐庐上传呆呆 -> 只上传呆呆\n"
        "8. 每天 fake 定时会推送即将到期/已过期提醒\n"
        "\n可用命令:\n"
        "潇洒桐庐登录\n"
        "潇洒桐庐查询\n"
        "潇洒桐庐管理\n"
        "潇洒桐庐授权\n"
        "潇洒桐庐上传\n"
        "潇洒桐庐上传青龙\n"
        "潇洒桐庐上传呆呆\n"
        "潇洒桐庐清理\n"
        "潇洒桐庐教程\n"
        "=============================="
    )


try:
    imtype = str(sender.getImtype() or "").strip().lower()
except Exception:
    imtype = ""

try:
    usermessage = str(sender.getMessage() or "").strip()
except Exception:
    usermessage = ""

if imtype == "fake":
    push_auth_status_notifications()
elif re.search(r"^(潇洒桐庐|xstl)(登录|登陆)$|^(登录|登陆)(潇洒桐庐|xstl)$", usermessage):
    bind_account()
elif re.search(r"^(潇洒桐庐|xstl)管理$|^管理(潇洒桐庐|xstl)$", usermessage):
    manage_accounts()
elif re.search(r"^(潇洒桐庐|xstl)查询$|^查询(潇洒桐庐|xstl)$", usermessage):
    query_accounts()
elif re.search(r"^(潇洒桐庐|xstl)教程$|^教程(潇洒桐庐|xstl)$", usermessage):
    show_tutorial()
elif re.search(r"^(潇洒桐庐|xstl)授权$|^授权(潇洒桐庐|xstl)$", usermessage):
    admin_authorize()
elif re.search(r"^(潇洒桐庐|xstl)上传青龙$|^上传青龙(潇洒桐庐|xstl)$", usermessage):
    cmd_upload(force_target="qinglong")
elif re.search(r"^(潇洒桐庐|xstl)上传呆呆$|^上传呆呆(潇洒桐庐|xstl)$", usermessage):
    cmd_upload(force_target="daidai")
elif re.search(r"^(潇洒桐庐|xstl)上传$|^上传(潇洒桐庐|xstl)$", usermessage):
    cmd_upload(force_target=None)
elif re.search(r"^(潇洒桐庐|xstl)清理$|^清理(潇洒桐庐|xstl)$", usermessage):
    clean_accounts()
else:
    sender.setContinue()
