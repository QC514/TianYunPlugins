# [author: qingyun]
# [title: 芳华未来]
# [language: python]
# [class: 工具类]
# [service: 68025408]
# [disable: false]
# [admin: false]
# [rule: ^芳华(.*)|(.*)芳华$]
# [cron: 26 8,18 * * *]
# [priority: 1]
# [platform: all]
# [open_source: false]
# [version: 1.0.0]
# [public: false]
# [price: 0]
# [icon: https://i.mji.rip/2025/07/11/2350538ac014afbea48b64409bd5931c.png]
# [description: 芳华未来账号管理插件。支持短信验证码登录获取 AppToken、账号查询、清蕴支付授权、账号管理和提交青龙。查询显示昵称、手机号、签到状态、今日增加和当前芳华。<br>指令：芳华（登录|查询|管理|教程）。<br>青龙环境变量固定为 qingyun_fh，值为纯 Token；备注写入手机号、所属用户和授权时间。<br>1.2.3：删除明文请求旧逻辑，接口仅走加密协议。<br>1.2.2：修复 sendCode 因缺少 pycryptodome 走明文导致 401；补 cryptography 加密兜底。<br>1.2.1：移除密码登录与双 Token 缓存，统一短信登录纯 Token。]
# [param: {"required":true,"key":"qingyun_fanghua.ql_config","bool":false,"placeholder":"http://地址:端口丨ClientID丨ClientSecret","name":"对接青龙","desc":"青龙地址丨ClientID丨ClientSecret"}]
# [param: {"required":false,"key":"qingyun_fanghua.price","bool":false,"placeholder":"1","name":"授权价格","desc":"单账号授权30天的价格，单位为元"}]
# [param: {"required":false,"key":"qingyun_fanghua.is_proxy","bool":true,"placeholder":"","name":"启用代理","desc":"是否为芳华接口启用代理"}]
# [param: {"required":false,"key":"qingyun_fanghua.proxy_pool","bool":false,"placeholder":"http://代理池接口","name":"代理池地址","desc":"返回单个代理地址的接口"}]

"""芳华未来 AutMan 账号管理插件。"""

import base64
import hashlib
import json
import random
import re
import string
import time
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_UP
from typing import Any

import middleware
import requests
import urllib3

import qingyun_payment

try:
    from Crypto.Cipher import AES, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Util.Padding import pad, unpad

    CRYPTO_BACKEND = "pycryptodome"
except ImportError:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        from cryptography.hazmat.primitives.padding import PKCS7

        CRYPTO_BACKEND = "cryptography"
    except ImportError:
        CRYPTO_BACKEND = None


SCRIPT_NAME = "芳华"
FULL_SCRIPT_NAME = "芳华未来"
BUCKET_PREFIX = "qingyun_fanghua"
QL_ENV_NAME = "qingyun_fh"
API_BASE = "https://api.cdwjyyh.com"
MAX_RETRIES = 3
RSA_PUBLIC_KEY_B64 = (
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwVjN8e7S9Ygg2jzc+laQ"
    "EYD1YxSRppwUl1fEjfpV8CF/KvQ5IgTcyUYDe3O7/41+i7HjX2ZuwDXPOhhoVy6oD"
    "2e/NS/+XmUYLt9aEzo+erbq2+uxjwK93t0akM5C9xZDa4Ji0M5ICfZMx8pt56fTII"
    "i5m8C3s7fhh8RSVUp78XK054ZweW25Xe3tQICF6UuuqMAESfTGfhP591hEikbJTxU"
    "hXfRywjarlwziZyP9waZYu8D0QA7Z84xaDPU1h3kgxb6Gt5DUAdCOg0dMxuiC24gl"
    "nUET9yzHa3bIglZMMxpBiGI+B9jDYjKa03IF1NfsQn8eN1n+JlHyeMXtITrgqQIDAQAB"
)
APP_RSA_PRIVATE_KEY_B64 = (
    "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDBWM3x7tL1iCDa"
    "PNz6VpARgPVjFJGmnBSXV8SN+lXwIX8q9DkiBNzJRgN7c7v/jX6LseNfZm7ANc86G"
    "GhXLqgPZ781L/5eZRgu31oTOj56turb67GPAr3e3RqQzkL3FkNrgmLQzkgJ9kzHym"
    "3np9MgiLmbwLezt+GHxFJVSnvxcrTnhnB5bbld7e1AgIXpS66owARJ9MZ+E/n3WES"
    "KRslPFSFd9HLCNquXDOJnI/3Bpli7wPRADtnzjFoM9TWHeSDFvoa3kNQB0I6DR0zG"
    "6ILbiCWdQRP3LMdrdsiCVkwzGkGIYj4H2MNiMprTcgXU1+xCfx43Wf4mUfJ4xe0hO"
    "uCpAgMBAAECggEAdMfOnHJDuUmfjjF0xz/BhND/ZfjmgFuFlGPOtHKftYqF5MveNk"
    "35jRhcwhQFWTV9WaL4UobsHexiXhSf8QidObDQLK/wU9N759O/9B0Z38Tb1jll5Zsi"
    "U5n4kb4DdHpd/nGifbwahundNk9uUp1rSBtNAGZGjqZh8j8B+8IhWpOA1090lPiqc"
    "bnCMueSVF3VghNPAYBYE/VpS1zQnkx54FiS/ojvhZNmW9rSnXtci3fiQkLOg2GHI5"
    "ZTIxbFzOVb1F+TTGxtHcwOddOXz6DuaQmysXEmavcw7PrmeibWhc/JggBiBBcYLEU"
    "bnDdYIwnPmP+ymaQfxYUv+wQ/fjvgAQKBgQDqBGY8/pMTngWRnipAS0ciI2to17oo"
    "r1ovutAjMEEHXmHFeKVCh3NFkd0xscUF4wqqkZm8VdRz9QEANlfRgy/CRSPTHGxZc"
    "Bwjwdgr0f946XL5E2RGfNChWjECTSCxxHKktfuIrjDR1bkDIWwYgpGUncnAL8crn+"
    "Iosqlo4YeTSQKBgQDTgl+olhYL6rg3VeiNqbWi30w3+Xn8QOBNBnpKXBxdsUD/CBq"
    "IFyYJnvG3y2yqbNv0JwQijxC7o7VsF72eJYij3zYSufrsU6nIfilMMFpBIy5zJARiG"
    "Eev3ugbIQyE09BIeizxVmOsZ6exJFhej4UipTr7xTOqulmBVtjg8omCYQKBgEcDBL"
    "83hQvr5Ma2Vx3heflrBBnxdIUKCPT43FYBO4pv4n1YydUxYxJWW+fLiPzrU35E5oD"
    "XDrwNObuFwgpKo8Bw2JkkQ+Cz+2YCWYWamMppFMFuV/xnvatowfxvyR8IfL1sl6J3"
    "MUtLbnP7vWCGpoSRiPovxWGAh9FPvcacwVY5AoGAOjvfEo+gKk/JwJKKoNZlCB7q4"
    "U5y450JJKvv56FMvg8bkhwtEeMtueBlNPFxTcsDFEnZvZoeRUthnA09S9mRsWy3ep"
    "hyGbc/O9BglnWJo/2HwHPeMRP2SNnalf2XcMrQwePBlADxGHrBlOgo3IAva8aKYt9"
    "8xjjgg9fhhq3AZoECgYEA14vIL+vdzsvgIMT1mNRqpDOTNEh9STOFPI2qD+UR0GMcP"
    "yoqsMb6ySkgPw+Evrx3W+SZASAFDxTFcIWQ2Ok3ZKzq9nZMNbSerd+lQ7KUmunBOR"
    "VGatuE1etOWIeXl63G05Rz31ElZBxi03g9/FdPp5ImE+NFdpN3pOvjTddv7KM="
)
USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 16; 2509FPN0BC Build/BP2A.250605.031.A3; wv) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/140.0.7339.207 "
    "Mobile Safari/537.36 (Immersed/48.0) Html5Plus/1.0"
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sender_id = middleware.getSenderID()
sender = middleware.Sender(sender_id)
user_id = sender.getUserID()


class PluginError(RuntimeError):
    """插件运行过程中可直接展示给用户的错误。"""


class FanghuaCrypto:
    """实现芳华 App 使用的 AES/RSA 混合加密。"""

    def __init__(self) -> None:
        self.backend = CRYPTO_BACKEND
        self.public_key = None
        self.private_key = None
        if not self.backend:
            return
        try:
            public_der = base64.b64decode(RSA_PUBLIC_KEY_B64)
            private_der = base64.b64decode(APP_RSA_PRIVATE_KEY_B64)
            if self.backend == "pycryptodome":
                self.public_key = RSA.import_key(public_der)
                self.private_key = RSA.import_key(private_der)
            else:
                self.public_key = serialization.load_der_public_key(public_der)
                self.private_key = serialization.load_der_private_key(private_der, password=None)
        except Exception:
            self.backend = None
            self.public_key = None
            self.private_key = None

    @property
    def enabled(self) -> bool:
        return bool(self.backend and self.public_key is not None and self.private_key is not None)

    @staticmethod
    def _aes_key() -> str:
        return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))

    def _aes_encrypt(self, plaintext: str, aes_key: str) -> str:
        key = aes_key.encode("utf-8")
        raw = plaintext.encode("utf-8")
        if self.backend == "pycryptodome":
            cipher = AES.new(key, AES.MODE_CBC, key)
            encrypted = cipher.encrypt(pad(raw, AES.block_size))
        else:
            padder = PKCS7(128).padder()
            padded = padder.update(raw) + padder.finalize()
            encryptor = Cipher(algorithms.AES(key), modes.CBC(key)).encryptor()
            encrypted = encryptor.update(padded) + encryptor.finalize()
        return base64.b64encode(encrypted).decode("utf-8")

    def _aes_decrypt(self, ciphertext: str, aes_key: str) -> str:
        key = aes_key.encode("utf-8")
        raw = base64.b64decode(ciphertext)
        if self.backend == "pycryptodome":
            cipher = AES.new(key, AES.MODE_CBC, key)
            decrypted = unpad(cipher.decrypt(raw), AES.block_size)
        else:
            decryptor = Cipher(algorithms.AES(key), modes.CBC(key)).decryptor()
            padded = decryptor.update(raw) + decryptor.finalize()
            unpadder = PKCS7(128).unpadder()
            decrypted = unpadder.update(padded) + unpadder.finalize()
        return decrypted.decode("utf-8")

    def _sign(self, timestamp: int, aes_key: str) -> str:
        value = f"timestamp={timestamp}&aesKey={aes_key}".encode("utf-8")
        if self.backend == "pycryptodome":
            encrypted = PKCS1_v1_5.new(self.public_key).encrypt(value)
        else:
            encrypted = self.public_key.encrypt(value, asymmetric_padding.PKCS1v15())
        return base64.b64encode(encrypted).decode("utf-8")

    def encrypt_data(self, data: dict[str, Any], timestamp: int) -> tuple[str, str]:
        aes_key = self._aes_key()
        plaintext = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return self._aes_encrypt(plaintext, aes_key), self._sign(timestamp, aes_key)

    def decrypt_response(self, result: Any) -> Any:
        if not isinstance(result, dict):
            return result
        encrypted_key = result.get("encryptedKey")
        encrypted_data = result.get("encryptedData")
        if not encrypted_key or not encrypted_data or self.private_key is None:
            return result
        try:
            raw_key = base64.b64decode(encrypted_key)
            if self.backend == "pycryptodome":
                aes_key_bytes = PKCS1_v1_5.new(self.private_key).decrypt(raw_key, None)
            else:
                try:
                    aes_key_bytes = self.private_key.decrypt(raw_key, asymmetric_padding.PKCS1v15())
                except ValueError:
                    aes_key_bytes = None
            if not aes_key_bytes:
                return result
            plaintext = self._aes_decrypt(encrypted_data, aes_key_bytes.decode("utf-8"))
            return json.loads(plaintext)
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
            return result


fanghua_crypto = FanghuaCrypto()


def mask_phone(phone: str) -> str:
    """隐藏手机号中间四位。"""
    if len(phone) < 7:
        return phone
    return phone[:3] + "****" + phone[-4:]


def normalize_phone(phone: str) -> str:
    """清洗并校验手机号。"""
    phone = re.sub(r"\D", "", str(phone or ""))
    if not re.fullmatch(r"1\d{10}", phone):
        raise PluginError(f"手机号格式错误：{phone or '空'}")
    return phone


def is_app_token(value: str) -> bool:
    """粗略判断是否为可直接使用的 AppToken。"""
    value = str(value or "").strip()
    if not value:
        return False
    if "#" in value or " " in value:
        return False
    return len(value) >= 16


def extract_token_value(raw: str) -> str:
    """提取纯 AppToken。"""
    raw = str(raw or "").strip()
    return raw if is_app_token(raw) else ""


def get_account_token(phone: str) -> str:
    """读取账号绑定的 AppToken。"""
    phone = normalize_phone(phone)
    for bucket in (f"{BUCKET_PREFIX}_token", f"{BUCKET_PREFIX}_app_token"):
        token = extract_token_value(str(middleware.bucketGet(bucket, phone) or ""))
        if token:
            if bucket != f"{BUCKET_PREFIX}_token":
                # 旧双桶数据迁移到主桶
                middleware.bucketSet(f"{BUCKET_PREFIX}_token", phone, token)
                middleware.bucketDel(f"{BUCKET_PREFIX}_app_token", phone)
            return token
    return ""


def save_account_token(phone: str, app_token: str) -> None:
    """只保存一份纯 Token。"""
    phone = normalize_phone(phone)
    app_token = str(app_token or "").strip()
    if not app_token:
        raise PluginError("保存失败：Token 为空")
    if not is_app_token(app_token):
        raise PluginError("保存失败：Token 格式无效")
    middleware.bucketSet(f"{BUCKET_PREFIX}_token", phone, app_token)
    # 清理旧双桶残留
    middleware.bucketDel(f"{BUCKET_PREFIX}_app_token", phone)


def get_user_accounts() -> list[str]:
    """读取当前用户绑定的手机号列表。"""
    raw = middleware.bucketGet(f"{BUCKET_PREFIX}_user", user_id) or "[]"
    try:
        result = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        result = []
    return [str(parts) for parts in result] if isinstance(result, list) else []


def save_user_accounts(accounts: list[str]) -> None:
    """保存当前用户绑定的手机号列表。"""
    middleware.bucketSet(
        f"{BUCKET_PREFIX}_user",
        user_id,
        json.dumps(accounts, ensure_ascii=False),
    )


def get_proxy() -> dict[str, str] | None:
    """按插件配置获取一次代理。"""
    enabled = str(middleware.bucketGet(BUCKET_PREFIX, "is_proxy") or "false").lower()
    if enabled not in {"true", "1", "yes"}:
        return None
    proxy_api = middleware.bucketGet(BUCKET_PREFIX, "proxy_pool")
    if not proxy_api:
        raise PluginError("已启用代理，但未配置代理池地址")
    response = requests.get(proxy_api, timeout=15, verify=False)
    response.raise_for_status()
    proxy_url = response.text.strip()
    if not proxy_url:
        raise PluginError("代理池没有返回可用代理")
    return {"http": proxy_url, "https": proxy_url}


def send_request(method: str, url: str, **kwargs: Any) -> requests.Response:
    """发送带超时、代理和有限重试的网络请求。"""
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            kwargs.setdefault("timeout", 30)
            kwargs.setdefault("verify", False)
            if "proxies" not in kwargs:
                kwargs["proxies"] = get_proxy()
            response = requests.request(method, url, **kwargs)
            if response.status_code >= 400:
                detail = ""
                try:
                    payload = response.json()
                    if isinstance(payload, dict):
                        detail = str(payload.get("msg") or payload.get("message") or "")
                except Exception:
                    detail = (response.text or "").strip()[:120]
                message = f"{response.status_code} Client Error"
                if detail:
                    message += f"：{detail}"
                message += f" for url: {response.url}"
                raise requests.HTTPError(message, response=response)
            return response
        except requests.RequestException as exc:
            last_error = exc
            # 业务性 401/重复请求等无需盲目重试
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if status in {400, 401, 403, 404}:
                break
            if attempt < MAX_RETRIES:
                time.sleep(1)
    raise PluginError(f"请求失败：{last_error}")


def derive_device_id(phone: str) -> str:
    """为同一账号生成稳定的 App 设备标识。"""
    return hashlib.md5(f"fhwl_device_{phone}".encode()).hexdigest()


def derive_jpush_id(phone: str) -> str:
    """为同一账号生成稳定的极光推送注册标识。"""
    digest = hashlib.md5(f"fhwl_jpush_{phone}".encode()).hexdigest()
    return digest[:16] + "0100"


def fanghua_request(
    method: str,
    path: str,
    app_token: str = "",
    data: dict[str, Any] | None = None,
    query_params: dict[str, Any] | None = None,
    phone: str = "",
) -> Any:
    """按芳华 App 协议加密请求并解密响应。"""
    if not fanghua_crypto.enabled:
        raise PluginError(
            "芳华接口加密不可用：请安装 pycryptodome 或 cryptography 后重试"
        )

    method = method.upper()
    timestamp = int(time.time() * 1000)
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
        "AppPlatform": "android",
        "AppVersion": "1.8.1",
        "AppVersionCode": "1810",
        "AppToken": app_token,
        "Content-Type": "text/plain",
        "X-Api-Nonce": "".join(random.choices(string.ascii_lowercase + string.digits, k=10)),
        "X-Api-Timestamp": str(timestamp),
    }
    if phone:
        headers["X-Api-DeviceId"] = derive_device_id(phone)

    request_kwargs: dict[str, Any] = {"headers": headers}
    if method == "POST" and data is not None:
        encrypted_body, signature = fanghua_crypto.encrypt_data(data, timestamp)
        headers["X-Api-Sign"] = signature
        request_kwargs["data"] = encrypted_body
    elif method == "GET" and query_params is not None:
        encrypted_params, signature = fanghua_crypto.encrypt_data(query_params, timestamp)
        headers["X-Api-Sign"] = signature
        request_kwargs["params"] = {"data": encrypted_params}

    response = send_request(method, API_BASE + path, **request_kwargs)
    try:
        result = response.json()
    except ValueError as exc:
        raise PluginError(f"接口没有返回有效数据：{exc}") from exc

    result = fanghua_crypto.decrypt_response(result)
    if isinstance(result, dict) and result.get("code") == 401:
        raise PluginError(result.get("msg") or "账号身份验证失败")
    return result


def update_timestamp(user: dict[str, Any]) -> float:
    """将关联用户更新时间转换为可排序数值。"""
    raw = user.get("updateTime")
    if isinstance(raw, (int, float)):
        return float(raw)
    if isinstance(raw, str) and raw:
        if raw.isdigit():
            return float(raw)
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return float("-inf")


def build_sms_login_payload(phone: str, code: str = "") -> dict[str, Any]:
    """按 App 源码构造短信登录参数。

    逆向自 pages/auth/login.vue：
    - sendCode({ phone })
    - loginByPhone({ phone, code, jpushId, loginType: 2, source })
    source 对应 plus.runtime.channel，常见为 yyb。
    """
    payload: dict[str, Any] = {
        "phone": phone,
        "jpushId": derive_jpush_id(phone),
        "loginType": 2,
        "source": "yyb",
    }
    if code:
        payload["code"] = code
    return payload


def send_sms_code(phone: str) -> str:
    """官方协议发送短信验证码：POST /app/app/sendCode。"""
    phone = normalize_phone(phone)
    result = fanghua_request(
        "POST",
        "/app/app/sendCode",
        data={"phone": phone},
        phone=phone,
    )
    if isinstance(result, dict) and result.get("code") == 200:
        return str(result.get("msg") or "验证码已发送")
    reason = result.get("msg") if isinstance(result, dict) else result
    raise PluginError(f"发送验证码失败：{reason}")


def resolve_login_token(result: dict[str, Any], login_payload: dict[str, Any], phone: str) -> tuple[str, dict[str, Any]]:
    """从登录结果提取 Token；若返回 users 列表则走 loginByUserId。"""
    linked_users = result.get("users")
    if isinstance(linked_users, list) and linked_users:
        valid_users = [
            user for user in linked_users
            if isinstance(user, dict) and user.get("userId") is not None
        ]
        if not valid_users:
            raise PluginError("关联用户列表中没有有效用户")
        selected_user = max(valid_users, key=update_timestamp)
        second_payload = dict(login_payload)
        second_payload["userId"] = selected_user["userId"]
        result = fanghua_request(
            "POST",
            "/app/app/loginByUserId",
            data=second_payload,
            phone=phone,
        )
        if not isinstance(result, dict) or result.get("code") != 200:
            reason = result.get("msg") if isinstance(result, dict) else result
            raise PluginError(f"关联用户登录失败：{reason}")

    app_token = result.get("token")
    if not app_token and isinstance(result.get("data"), dict):
        app_token = result["data"].get("token")
    if not app_token:
        raise PluginError("登录成功，但响应中没有登录令牌")
    return str(app_token), result


def login_by_sms(phone: str, code: str) -> tuple[str, dict[str, Any]]:
    """官方协议短信登录：POST /app/app/loginByPhone。

    对应 App 源码：
    loginByPhone({
        phone, code, jpushId, loginType: 2, source
    })
    成功后保存 AppToken；若返回 users，再调用 loginByUserId。
    """
    phone = normalize_phone(phone)
    code = str(code or "").strip()
    if not re.fullmatch(r"\d{4,8}", code):
        raise PluginError("验证码格式错误")

    login_payload = build_sms_login_payload(phone, code)
    result = fanghua_request(
        "POST",
        "/app/app/loginByPhone",
        data=login_payload,
        phone=phone,
    )
    if not isinstance(result, dict) or result.get("code") != 200:
        reason = result.get("msg") if isinstance(result, dict) else result
        raise PluginError(f"短信登录失败：{reason}")
    return resolve_login_token(result, login_payload, phone)


def get_nested_value(data: Any, *fields: str) -> Any:
    """在嵌套数据中按字段优先级查找第一个有效值。"""
    for target_field in fields:
        found = _find_field(data, target_field)
        if found not in (None, ""):
            return found
    return None


def _find_field(data: Any, target_field: str) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            if str(key).casefold() == target_field.casefold() and value not in (None, ""):
                return value
        for value in data.values():
            found = _find_field(value, target_field)
            if found not in (None, ""):
                return found
    elif isinstance(data, list):
        for value in data:
            found = _find_field(value, target_field)
            if found not in (None, ""):
                return found
    return None


def response_list(data: Any) -> list[dict[str, Any]]:
    """从常见分页响应结构中提取列表。"""
    if not isinstance(data, dict):
        return []
    candidates = [data.get("list"), data.get("rows")]
    body = data.get("data")
    if isinstance(body, list):
        candidates.insert(0, body)
    elif isinstance(body, dict):
        candidates = [body.get("list"), body.get("rows")] + candidates
    for candidate in candidates:
        if isinstance(candidate, list):
            return [parts for parts in candidate if isinstance(parts, dict)]
    return []


def to_number(data: Any) -> float | None:
    """把整数、浮点数或数字字符串转换为数值。"""
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        return float(data)
    if isinstance(data, str):
        try:
            return float(data)
        except ValueError:
            return None
    return None


def extract_points(data: Any) -> int | None:
    """从钱包或积分响应中提取芳华币余额。"""
    raw = get_nested_value(
        data,
        "integral",
        "withdrawIntegral",
        "totalIntegral",
        "points",
    )
    number = to_number(raw)
    return int(number) if number is not None else None


def parse_log_time(data: Any) -> datetime | None:
    """将积分流水时间转换为本地时间。"""
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        timestamp = float(data)
        if timestamp > 10_000_000_000:
            timestamp /= 1000
        try:
            return datetime.fromtimestamp(timestamp)
        except (OSError, OverflowError, ValueError):
            return None
    if not isinstance(data, str) or not data.strip():
        return None
    text = data.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
        return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
    except ValueError:
        return None


def calculate_today_earned(
    records: list[dict[str, Any]],
) -> int | None:
    """统计今日新增积分，仅累加正向变动（签到、任务等），排除消耗使用。"""
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_earned = 0
    has_today = False
    for record in records:
        created_at = parse_log_time(
            get_nested_value(record, "createTime", "createdAt", "createDate", "logTime", "time")
        )
        if created_at is None or created_at < today_start:
            continue
        has_today = True
        change = to_number(get_nested_value(record, "integral"))
        if change is not None and change > 0:
            today_earned += int(change)
    return today_earned if has_today else None


def query_today_earned(
    app_token: str,
    phone: str,
    max_pages: int = 20,
) -> int | None:
    """分页读取流水，直到找到今天以前最近的一条记录。"""
    records: list[dict[str, Any]] = []
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    page_size = 50
    for page in range(1, max_pages + 1):
        response = fanghua_request(
            "GET",
            "/app/integral/getUserIntegralLogsList",
            app_token,
            query_params={"pageNum": page, "pageSize": page_size},
            phone=phone,
        )
        if not isinstance(response, dict) or response.get("code") != 200:
            reason = response.get("msg") if isinstance(response, dict) else response
            raise PluginError(f"积分流水查询失败：{reason}")
        batch = response_list(response)
        records.extend(batch)
        has_previous_record = any(
            (created_at := parse_log_time(get_nested_value(record, "createTime"))) is not None
            and created_at < today_start
            for record in batch
        )
        if has_previous_record or len(batch) < page_size:
            break
    return calculate_today_earned(records)


def get_valid_app_token(phone: str, raw_token: str = "") -> tuple[str, dict[str, Any]]:
    """优先复用已保存 Token；失效则提示重新短信登录。"""
    phone = normalize_phone(phone)
    candidates: list[str] = []
    for value in (raw_token, get_account_token(phone)):
        token = extract_token_value(str(value))
        if token and token not in candidates:
            candidates.append(token)

    last_error = "Token 无效"
    for token in candidates:
        try:
            profile = fanghua_request(
                "GET",
                "/app/user/getUserInfo",
                token,
                phone=phone,
            )
            if isinstance(profile, dict) and profile.get("code") == 200:
                save_account_token(phone, token)
                return token, profile
            last_error = profile.get("msg") if isinstance(profile, dict) else str(profile)
        except PluginError as exc:
            last_error = str(exc)

    raise PluginError(f"Token 已失效，请重新短信登录：{last_error}")


def query_account_details(phone: str, raw_token: str = "") -> dict[str, Any]:
    """复用有效 Token 查询账号当前信息。"""
    phone = normalize_phone(phone)
    app_token, profile = get_valid_app_token(phone, raw_token)
    profile_user_id = get_nested_value(profile, "userId")
    wallet = None
    if profile_user_id is not None:
        wallet = fanghua_request(
            "GET",
            f"/app/common/getWallet/{profile_user_id}",
            app_token,
            query_params={"userId": profile_user_id},
            phone=phone,
        )
    sign_info = fanghua_request(
        "GET",
        "/app/integral/getUserSign",
        app_token,
        query_params={},
        phone=phone,
    )
    nickname = get_nested_value(
        profile,
        "nickName",
        "nickname",
        "userName",
        "username",
        "name",
        "realName",
    )
    is_signed = get_nested_value(sign_info, "isDaySign")
    current_points = extract_points(profile)
    if current_points is None:
        current_points = extract_points(wallet)
    if current_points is None:
        current_points = extract_points(sign_info)
    today_earned = query_today_earned(app_token, phone)
    return {
        "昵称": nickname or "未知",
        "手机号": phone,
        "签到状态": "已签到" if is_signed in (1, True, "1") else "未签到",
        "今日增加": today_earned if today_earned is not None else "未知",
        "当前芳华": current_points,
    }


def parse_qinglong_config() -> tuple[str, str, str]:
    """读取并校验青龙连接配置。"""
    config = middleware.bucketGet(BUCKET_PREFIX, "ql_config")
    if not config:
        raise PluginError("未配置青龙连接")
    parts = [value.strip() for value in re.split(r"[丨|]", config) if value.strip()]
    if len(parts) != 3:
        raise PluginError("青龙配置格式应为 地址丨ClientID丨ClientSecret")
    url, client_id, client_secret = parts
    return url.rstrip("/"), client_id, client_secret


def get_qinglong_token(url: str, client_id: str, client_secret: str) -> str:
    """获取青龙开放接口访问令牌。"""
    response = send_request(
        "GET",
        f"{url}/open/auth/token",
        params={"client_id": client_id, "client_secret": client_secret},
    )
    data = response.json()
    token = data.get("data", {}).get("token") if isinstance(data, dict) else None
    if not token:
        raise PluginError("获取青龙访问令牌失败")
    return str(token)


def qinglong_context() -> tuple[str, dict[str, str]]:
    """构造青龙地址和认证请求头。"""
    url, client_id, client_secret = parse_qinglong_config()
    token = get_qinglong_token(url, client_id, client_secret)
    return url, {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_qinglong_envs(url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    """获取青龙环境变量列表。"""
    response = send_request("GET", f"{url}/open/envs", headers=headers)
    data = response.json().get("data", [])
    return data if isinstance(data, list) else []


def get_env_id(env: dict[str, Any]) -> Any:
    """兼容不同青龙版本的环境变量编号字段。"""
    return env.get("id", env.get("_id"))


def submit_to_qinglong(phone: str, owner_id: str, app_token: str = "") -> bool:
    """按模板格式新增或更新单个账号的青龙环境变量（值为纯 Token）。"""
    phone = normalize_phone(phone)
    token = str(app_token or "").strip() or get_account_token(phone)
    if not token:
        raise PluginError("未找到可用 Token，请先短信登录")
    url, headers = qinglong_context()
    envs = get_qinglong_envs(url, headers)
    target_env = None
    for env in envs:
        if env.get("name") != QL_ENV_NAME:
            continue
        remarks = str(env.get("remarks", ""))
        if phone in remarks:
            target_env = env
            break

    auth_time = middleware.bucketGet(f"{BUCKET_PREFIX}_auth", phone) or "未授权"
    remarks = f"{FULL_SCRIPT_NAME}账号:{phone}丨用户:{owner_id}丨授权时间:{auth_time}"
    data = {"name": QL_ENV_NAME, "value": token, "remarks": remarks}
    if target_env:
        data["id"] = get_env_id(target_env)
        response = send_request("PUT", f"{url}/open/envs", headers=headers, json=data)
    else:
        response = send_request("POST", f"{url}/open/envs", headers=headers, json=[data])
    response_data = response.json()
    if isinstance(response_data, dict) and response_data.get("code") not in (None, 0, 200):
        raise PluginError(response_data.get("message") or "提交青龙失败")
    new_envs = response_data.get("data", []) if isinstance(response_data, dict) else []
    if isinstance(new_envs, list) and new_envs:
        env_id = get_env_id(new_envs[0])
        if env_id is not None:
            middleware.bucketSet(f"{BUCKET_PREFIX}_env_id", phone, str(env_id))
    return True


def delete_qinglong_env(phone: str) -> bool:
    """按账号备注查找并删除对应青龙环境变量。"""
    url, headers = qinglong_context()
    ids_to_delete = []
    for env in get_qinglong_envs(url, headers):
        if env.get("name") != QL_ENV_NAME:
            continue
        if phone in str(env.get("remarks", "")):
            env_id = get_env_id(env)
            if env_id is not None:
                ids_to_delete.append(env_id)
    if ids_to_delete:
        send_request("DELETE", f"{url}/open/envs", headers=headers, json=ids_to_delete)
    middleware.bucketDel(f"{BUCKET_PREFIX}_env_id", phone)
    return True


def get_auth_time(phone: str) -> str:
    """读取账号授权到期日期。"""
    return str(middleware.bucketGet(f"{BUCKET_PREFIX}_auth", phone) or "")


def is_authorized(phone: str) -> bool:
    """判断账号授权是否仍在有效期内。"""
    auth_time = get_auth_time(phone)
    return bool(auth_time and auth_time > str(datetime.now().date()))


def calculate_auth_time(phone: str, days: int) -> str:
    """从当前日期或现有到期日期继续累加授权天数。"""
    today = datetime.now().date()
    auth_time = get_auth_time(phone)
    start_date = today
    if auth_time:
        try:
            current_expiry = datetime.strptime(auth_time, "%Y-%m-%d").date()
            if current_expiry > today:
                start_date = current_expiry
        except ValueError:
            pass
    return str(start_date + timedelta(days=days))


def get_payment_config() -> Decimal:
    """读取并校验授权价格。"""
    try:
        price = Decimal(str(middleware.bucketGet(BUCKET_PREFIX, "price") or "1"))
        if price < 0:
            raise ValueError("授权价格不能为负数")
    except (InvalidOperation, ValueError) as exc:
        raise PluginError(f"授权价格配置错误：{exc}") from exc
    return price


def process_payment(amount: Decimal, days: int, account_count: int = 1) -> bool:
    """接入清蕴支付统一收银台。"""
    try:
        pay_amount = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_UP))
    except Exception:
        sender.reply("❌ 支付金额无效")
        return False

    if pay_amount <= 0:
        return True

    header_extra = (
        f"🎫 商品: {FULL_SCRIPT_NAME}授权\n"
        f"📅 时长: {days}天\n"
        f"👥 账号数: {account_count}"
    )
    pay_res = qingyun_payment.QingyunCompletePayment.start_checkout(
        sender=sender,
        amount=pay_amount,
        title=f"{FULL_SCRIPT_NAME}授权",
        order_name=f"{FULL_SCRIPT_NAME}授权",
        user_id=str(user_id),
        header_extra=header_extra,
    )
    if not isinstance(pay_res, dict) or pay_res.get("code") != 0:
        return False

    try:
        paid_money = float(pay_res.get("paid_money", pay_amount) or pay_amount)
    except Exception:
        paid_money = pay_amount

    if paid_money + 1e-6 < pay_amount:
        sender.reply(
            "=====支付失败=====\n"
            "❌ 支付金额不足\n"
            "------------------\n"
            f"💰 应付: {pay_amount}元\n"
            f"💵 实付: {paid_money}元\n"
            "=================="
        )
        return False
    return True


def authorize_accounts(accounts: list[str]) -> None:
    """为一个或多个账号完成付款、写入授权日期并提交青龙。"""
    if not accounts:
        return
    sender.reply("请输入授权天数，例如 30；回复 q 退出")
    days_text = sender.input(60000, 1, False)
    if not days_text or days_text.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    try:
        days = int(days_text)
        if days <= 0:
            raise ValueError
    except ValueError:
        sender.reply("❌ 授权天数必须是正整数")
        return

    try:
        price = get_payment_config()
    except PluginError as exc:
        sender.reply(f"❌ {exc}")
        return

    amount = (price * Decimal(days) / Decimal(30) * len(accounts)).quantize(
        Decimal("0.01"), rounding=ROUND_UP
    )
    if not process_payment(amount, days, account_count=len(accounts)):
        return

    success_count = 0
    errors = []
    for phone in accounts:
        token = get_account_token(phone)
        if not token:
            errors.append(f"{mask_phone(phone)}：未找到 Token，请先短信登录")
            continue
        auth_time = calculate_auth_time(phone, days)
        middleware.bucketSet(f"{BUCKET_PREFIX}_auth", phone, auth_time)
        try:
            submit_to_qinglong(phone, user_id, token)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_phone(phone)}：提交青龙失败，{exc}")

    report = (
        "=====授权完成=====\n"
        f"支付 {amount} 元，授权 {days} 天\n"
        f"成功：{success_count} 个账号\n"
        f"失败：{len(errors)} 个账号"
    )
    if errors:
        report += "\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)


def show_ck(phone: str) -> None:
    """显示账号保存的 Token。"""
    token = get_account_token(phone)
    if token:
        sender.reply(
            "=====芳华未来账号Token=====\n"
            f"账号：{mask_phone(phone)}\n"
            f"Token：{token}\n"
            "===================="
        )
    else:
        sender.reply(f"❌ {mask_phone(phone)} 未绑定 Token")


def batch_login() -> None:
    """短信验证码登录：输入手机号 -> 发码 -> 输入验证码 -> 保存 Token。"""
    sender.reply(
        "=====芳华短信登录=====\n"
        "请输入手机号\n"
        "支持一次绑定一个账号\n"
        "回复 q 退出"
    )
    phone_text = sender.input(120000, 1, False)
    if not phone_text:
        sender.reply("❌ 输入超时")
        return
    if phone_text.strip().lower() == "q":
        sender.reply("✅ 已取消登录")
        return
    try:
        phone = normalize_phone(phone_text)
    except PluginError as exc:
        sender.reply(f"❌ {exc}")
        return

    try:
        message = send_sms_code(phone)
        sender.reply(f"✅ {message}\n请输入收到的短信验证码\n回复 q 退出")
    except Exception as exc:
        sender.reply(f"❌ 发送验证码失败：{exc}")
        return

    code_text = sender.input(180000, 1, False)
    if not code_text:
        sender.reply("❌ 输入超时")
        return
    if code_text.strip().lower() == "q":
        sender.reply("✅ 已取消登录")
        return

    try:
        app_token, _ = login_by_sms(phone, code_text.strip())
        save_account_token(phone, app_token)
        current_accounts = get_user_accounts()
        if phone in current_accounts:
            status = "更新成功"
        else:
            current_accounts.append(phone)
            save_user_accounts(current_accounts)
            status = "登录成功"
        if is_authorized(phone):
            submit_to_qinglong(phone, user_id, app_token)
            status += "，已同步青龙"
        else:
            status += "，账号未授权，暂未提交青龙"
        sender.reply(
            "=====登录完成=====\n"
            f"账号：{mask_phone(phone)}\n"
            f"状态：{status}\n"
            f"Token：{app_token[:12]}...\n"
            "=================="
        )
    except Exception as exc:
        sender.reply(f"❌ 登录失败：{exc}")


def select_accounts(title: str) -> list[str]:
    """显示账号选择菜单并返回选中的手机号列表。"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 未绑定账号，请先发送“芳华登录”")
        return []
    if len(accounts) == 1:
        return accounts
    menu = f"====={title}=====\n[0] 全部账号\n------------------\n"
    for index, phone in enumerate(accounts, 1):
        menu += f"[{index}] {mask_phone(phone)}\n"
    menu += "------------------\n回复数字选择，回复 q 退出"
    sender.reply(menu)
    choice = sender.input(30000, 1, False)
    if not choice or choice.lower() == "q":
        return []
    if not choice.isdigit():
        sender.reply("❌ 请输入数字序号")
        return []
    index = int(choice)
    if index == 0:
        return accounts
    if 1 <= index <= len(accounts):
        return [accounts[index - 1]]
    sender.reply("❌ 选择超出范围")
    return []


def query() -> None:
    """查询一个或全部已绑定芳华账号。"""
    for phone in select_accounts("芳华查询"):
        auth_time = get_auth_time(phone)
        if not auth_time:
            sender.reply(f"❌ {mask_phone(phone)} 账号未授权")
            continue
        if not is_authorized(phone):
            sender.reply(f"❌ {mask_phone(phone)} 授权已过期：{auth_time}")
            continue
        token = get_account_token(phone)
        if not token:
            sender.reply(f"❌ {mask_phone(phone)} 未找到 Token，请先短信登录")
            continue
        try:
            details = query_account_details(phone, token)
            sender.reply(
                "=====芳华未来详情=====\n"
                f"📱 账号：{mask_phone(details['手机号'])}\n"
                f"👤 昵称：{details['昵称']}\n"
                f"📅 签到：{details['签到状态']}\n"
                f"🎁 今日增加：{details['今日增加']}\n"
                f"💰 当前芳华：{details['当前芳华'] if details['当前芳华'] is not None else '未知'}\n"
                f"⏰ 授权到期：{auth_time}\n"
                "=================="
            )
        except Exception as exc:
            sender.reply(f"❌ {mask_phone(phone)} 查询失败：{exc}")


def delete_account(phone: str) -> None:
    """删除插件中的账号并同步删除青龙变量。"""
    delete_qinglong_env(phone)
    middleware.bucketDel(f"{BUCKET_PREFIX}_token", phone)
    middleware.bucketDel(f"{BUCKET_PREFIX}_app_token", phone)
    middleware.bucketDel(f"{BUCKET_PREFIX}_auth", phone)
    middleware.bucketDel(f"{BUCKET_PREFIX}_env_id", phone)
    accounts = [account for account in get_user_accounts() if account != phone]
    save_user_accounts(accounts)
    sender.reply(f"✅ {mask_phone(phone)} 已删除")


def manage_accounts() -> None:
    """显示包含批量操作和授权状态的账号管理菜单。"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 未绑定账号，请先发送“芳华登录”")
        return
    menu = (
        "=====账号列表=====\n"
        "批量操作:\n"
        "[00] 授权全部账号\n"
        "[01] 删除全部账号\n"
        "[02] 查看全部账号Token\n"
        "------------------\n"
        "账号列表:"
    )
    for index, phone in enumerate(accounts, 1):
        auth_time = get_auth_time(phone)
        if is_authorized(phone):
            menu += (
                f"\n[{index}] {mask_phone(phone)}\n"
                "    ✅ 已授权\n"
                f"    授权到期: {auth_time}"
            )
        else:
            status = "授权已过期" if auth_time else "未授权"
            menu += f"\n[{index}] {mask_phone(phone)}\n    ❌ {status}"
            if auth_time:
                menu += f"\n    授权到期: {auth_time}"
    menu += "\n------------------\n回复数字选择账号\n回复'q'退出"
    sender.reply(menu)
    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == "q":
        return
    try:
        if choice == "00":
            authorize_accounts(accounts)
        elif choice == "01":
            for phone in list(accounts):
                delete_account(phone)
            sender.reply("✅ 已删除全部账号")
        elif choice == "02":
            for phone in accounts:
                show_ck(phone)
        else:
            if not choice.isdigit() or not 1 <= int(choice) <= len(accounts):
                sender.reply("❌ 无效的账号序号")
                return
            show_account_menu(accounts[int(choice) - 1])
    except Exception as exc:
        sender.reply(f"❌ 操作失败：{exc}")


def show_account_menu(phone: str) -> None:
    """显示单个账号的授权与管理操作。"""
    auth_time = get_auth_time(phone)
    authorized = is_authorized(phone)
    auth_status = "✅ 已授权" if authorized else "❌ 未授权"
    auth_info = f"\n    到期: {auth_time}" if auth_time else ""
    sender.reply(
        "=====账号操作=====\n"
        f"📱 账号: {mask_phone(phone)}\n"
        f"🔐 状态: {auth_status}{auth_info}\n"
        "------------------\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 查看账号Token\n"
        "[4] 重新提交青龙\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    action = sender.input(60000, 1, False)
    if not action or action.lower() == "q":
        return
    try:
        if action == "1":
            authorize_accounts([phone])
        elif action == "2":
            delete_account(phone)
        elif action == "3":
            show_ck(phone)
        elif action == "4":
            if not is_authorized(phone):
                sender.reply("❌ 账号未授权或授权已过期")
                return
            token = get_account_token(phone)
            if not token:
                sender.reply("❌ 未找到 Token，请先短信登录")
                return
            # 校验 token 有效性后再提交
            valid_token, _ = get_valid_app_token(phone, token)
            submit_to_qinglong(phone, user_id, valid_token)
            sender.reply("✅ 已重新提交青龙")
        else:
            sender.reply("❌ 无效的操作")
    except Exception as exc:
        sender.reply(f"❌ 操作失败：{exc}")


def cron_check() -> None:
    """定时清理过期环境变量，并刷新有效账号的青龙数据。"""
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}_user"):
        raw = middleware.bucketGet(f"{BUCKET_PREFIX}_user", owner_id) or "[]"
        try:
            accounts = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue
        for phone in accounts if isinstance(accounts, list) else []:
            token = get_account_token(phone)
            if not token:
                continue
            auth_time = get_auth_time(phone)
            if not is_authorized(phone):
                if auth_time:
                    try:
                        delete_qinglong_env(phone)
                    except Exception:
                        pass
                    notification = (
                        f"====={FULL_SCRIPT_NAME}账号通知=====\n"
                        f"账号：{mask_phone(phone)}\n"
                        f"消息：授权已于 {auth_time} 到期，青龙变量已清理"
                    )
                    for platform in ("qq", "wx", "tg", "qx", "ipad"):
                        try:
                            middleware.push(platform, "", owner_id, "", notification)
                        except Exception:
                            pass
                continue


def grant_accounts(owner_id: str, accounts: list[str], days: int) -> tuple[int, list[str]]:
    """管理员免支付授权账号，并立即更新青龙环境变量。"""
    success_count = 0
    errors = []
    for phone in accounts:
        token = get_account_token(phone)
        if not token:
            errors.append(f"{mask_phone(phone)}：未找到 Token，请先短信登录")
            continue
        auth_time = calculate_auth_time(phone, days)
        middleware.bucketSet(f"{BUCKET_PREFIX}_auth", phone, auth_time)
        try:
            submit_to_qinglong(phone, owner_id, token)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_phone(phone)}：提交青龙失败，{exc}")
    return success_count, errors


def set_accounts_auth_date(
    owner_id: str,
    accounts: list[str],
    auth_time: str,
) -> tuple[int, list[str]]:
    """管理员把账号授权到期日期直接修改为指定日期。"""
    try:
        datetime.strptime(auth_time, "%Y-%m-%d")
    except ValueError as exc:
        raise PluginError("日期格式错误，应为 2030-02-16") from exc
    success_count = 0
    errors = []
    for phone in accounts:
        token = get_account_token(phone)
        if not token:
            errors.append(f"{mask_phone(phone)}：未找到 Token，请先短信登录")
            continue
        middleware.bucketSet(f"{BUCKET_PREFIX}_auth", phone, auth_time)
        try:
            submit_to_qinglong(phone, owner_id, token)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_phone(phone)}：提交青龙失败，{exc}")
    return success_count, errors


def parse_stored_accounts(owner_id: str) -> list[str]:
    """读取指定插件用户绑定的账号列表。"""
    raw = middleware.bucketGet(f"{BUCKET_PREFIX}_user", owner_id) or "[]"
    try:
        accounts = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return []
    return [str(phone) for phone in accounts] if isinstance(accounts, list) else []


def admin_auth_all_users() -> None:
    """管理员为全部插件用户的全部账号统一增加授权天数。"""
    sender.reply(
        "=====批量授权=====\n"
        "请输入授权天数\n"
        "------------------\n"
        "回复数字设置天数\n"
        "回复 q 退出"
    )
    days_text = sender.input(60000, 1, False)
    if not days_text or days_text.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    try:
        days = int(days_text)
        if days <= 0:
            raise ValueError
    except ValueError:
        sender.reply("❌ 授权天数必须是正整数")
        return
    success_count = 0
    errors = []
    user_count = 0
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}_user"):
        accounts = parse_stored_accounts(owner_id)
        if not accounts:
            continue
        user_count += 1
        current_success, current_errors = grant_accounts(owner_id, accounts, days)
        success_count += current_success
        errors.extend(current_errors)
    report = (
        "=====授权完成=====\n"
        f"用户：{user_count} 个\n"
        f"成功：{success_count} 个账号\n"
        f"失败：{len(errors)} 个账号\n"
        f"授权：{days} 天"
    )
    if errors:
        report += "\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)


def admin_auth_specific_user() -> None:
    """管理员为指定插件用户的全部或单个账号授权。"""
    sender.reply(
        "=====指定授权=====\n"
        "请输入用户ID\n"
        "------------------\n"
        "回复 q 退出"
    )
    owner_id = sender.input(60000, 1, False)
    if not owner_id or owner_id.lower() == "q":
        return
    accounts = parse_stored_accounts(owner_id)
    if not accounts:
        sender.reply("❌ 未找到该用户的账号")
        return
    menu = (
        "=====账号列表=====\n"
        "[00] 授权全部账号\n"
        "[01] 修改全部账号授权日期\n"
        "------------------"
    )
    for index, phone in enumerate(accounts, 1):
        auth_time = get_auth_time(phone)
        status = "✅ 已授权" if is_authorized(phone) else "❌ 未授权"
        menu += f"\n[{index}] {mask_phone(phone)}\n    {status}"
        if auth_time:
            menu += f"\n    授权到期: {auth_time}"
    menu += "\n------------------\n回复数字选择账号\n回复 q 退出"
    sender.reply(menu)
    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == "q":
        return
    if choice == "01":
        sender.reply("请输入新的授权日期，格式：2030-02-16")
        auth_time = sender.input(60000, 1, False)
        if not auth_time or auth_time.lower() == "q":
            return
        try:
            success_count, errors = set_accounts_auth_date(owner_id, accounts, auth_time)
        except PluginError as exc:
            sender.reply(f"❌ {exc}")
            return
        sender.reply(
            f"✅ 已修改 {success_count} 个账号，到期日期：{auth_time}"
            + (f"\n失败：{len(errors)} 个" if errors else "")
        )
        return
    if choice == "00":
        selected_accounts = accounts
    elif choice.isdigit() and 1 <= int(choice) <= len(accounts):
        selected_accounts = [accounts[int(choice) - 1]]
    else:
        sender.reply("❌ 无效的账号序号")
        return
    sender.reply("请输入授权天数，例如 30")
    days_text = sender.input(60000, 1, False)
    try:
        days = int(days_text)
        if days <= 0:
            raise ValueError
    except (TypeError, ValueError):
        sender.reply("❌ 授权天数必须是正整数")
        return
    success_count, errors = grant_accounts(owner_id, selected_accounts, days)
    sender.reply(
        f"✅ 已授权 {success_count} 个账号 {days} 天"
        + (f"\n失败：{len(errors)} 个" if errors else "")
    )


def update_all_qinglong_envs() -> None:
    """管理员把全部有效授权账号重新提交到青龙。"""
    user_count = 0
    account_count = 0
    success_count = 0
    errors = []
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}_user"):
        accounts = parse_stored_accounts(owner_id)
        if not accounts:
            continue
        user_count += 1
        for phone in accounts:
            account_count += 1
            if not is_authorized(phone):
                continue
            token = get_account_token(phone)
            if not token:
                errors.append(f"{mask_phone(phone)}：未找到 Token，请先短信登录")
                continue
            try:
                submit_to_qinglong(phone, owner_id, token)
                success_count += 1
            except Exception as exc:
                errors.append(f"{mask_phone(phone)}：{exc}")
    sender.reply(
        "=====更新青龙完成=====\n"
        f"用户：{user_count} 个\n"
        f"账号：{account_count} 个\n"
        f"成功：{success_count} 个\n"
        f"失败：{len(errors)} 个"
    )


def admin_auth() -> None:
    """显示管理员授权功能菜单。"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    sender.reply(
        "=====授权管理=====\n"
        "[1] 一键授权所有用户\n"
        "[2] 指定用户授权\n"
        "[3] 更新青龙环境变量\n"
        "------------------\n"
        "回复数字选择功能\n"
        "回复 q 退出"
    )
    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == "q":
        return
    if choice == "1":
        admin_auth_all_users()
    elif choice == "2":
        admin_auth_specific_user()
    elif choice == "3":
        update_all_qinglong_envs()
    else:
        sender.reply("❌ 无效的选择")


def clean_expired_accounts() -> None:
    """管理员清理授权已过期的账号和青龙环境变量。"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    cleaned_count = 0
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}_user"):
        accounts = parse_stored_accounts(owner_id)
        valid_accounts = []
        for phone in accounts:
            auth_time = get_auth_time(phone)
            if auth_time and not is_authorized(phone):
                try:
                    delete_qinglong_env(phone)
                except Exception:
                    pass
                middleware.bucketDel(f"{BUCKET_PREFIX}_token", phone)
                middleware.bucketDel(f"{BUCKET_PREFIX}_app_token", phone)
                middleware.bucketDel(f"{BUCKET_PREFIX}_auth", phone)
                middleware.bucketDel(f"{BUCKET_PREFIX}_env_id", phone)
                cleaned_count += 1
            else:
                valid_accounts.append(phone)
        if valid_accounts:
            middleware.bucketSet(
                f"{BUCKET_PREFIX}_user",
                owner_id,
                json.dumps(valid_accounts, ensure_ascii=False),
            )
        else:
            middleware.bucketDel(f"{BUCKET_PREFIX}_user", owner_id)
    sender.reply(f"✅ 已清理 {cleaned_count} 个过期账号")


def tutorial() -> None:
    """显示插件使用教程。"""
    sender.reply(
        "[CQ:image,file=http://m.k197.cn:29090/admin/images/gallery/芳华邀请码.jpg]"
        "=====芳华未来教程=====\n"
        "1. 注册下载：扫描上方二维码注册并下载 APP\n"
        "2. 短信登录：发送“芳华登录”，输入手机号和验证码获取 Token\n"
        "3. 授权代挂：在“芳华管理”中选择账号授权，走清蕴支付收银台\n"
        "4. 授权费用：按插件配置的月价计费（默认 1 元/30天）\n"
        "5. 项目收益：每日积分增长，可在 APP 兑换实物\n"
        "===================="
    )
    sender.reply(
        "=====芳华可用指令=====\n"
        "芳华教程：查看注册和使用教程\n"
        "芳华登录：短信验证码登录并绑定 Token\n"
        "芳华查询：查询签到、今日增加和当前芳华\n"
        "芳华管理：授权、查看 Token、同步或删除账号\n"
        "--------------------\n"
        "管理员指令：芳华授权、芳华清理\n"
        "===================="
    )


def main() -> None:
    """根据消息内容分发插件指令。"""
    message = sender.getMessage()
    if "登录" in message or "登陆" in message or "上车" in message:
        batch_login()
    elif "查询" in message:
        query()
    elif "管理" in message:
        manage_accounts()
    elif message == f"{SCRIPT_NAME}授权":
        admin_auth()
    elif message == f"{SCRIPT_NAME}清理":
        clean_expired_accounts()
    elif "教程" in message:
        tutorial()
    else:
        tutorial()


if __name__ == "__main__":
    try:
        if sender.getImtype() == "fake":
            cron_check()
        else:
            main()
    except Exception as exc:
        sender.reply(f"❌ 运行出错：{exc}")
