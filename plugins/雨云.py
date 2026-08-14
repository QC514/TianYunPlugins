# [author: qingyun]
# [language: python]
# [class: 工具类]
# [service: 68025408]
# [rule: ^(雨云|雨云..|..雨云)$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 8,18 * * *]
# [public: true]
# [title: 雨云]
# [open_source: false]
# [class: 工具类]
# [version: 1.0.0]
# [price: 0]
# [admin: false]
# [icon: https://www.rainyun.com/img/logo.d193755d.png]
# [description: 雨云账号管理插件。<br>1. 指令：雨云登录、查询、管理、授权、清理、教程。<br>2. 用户提交 账号#密码，支持批量。<br>3. 登录校验后同步青龙变量(dw_yy)。<br>4. 授权支付接入清蕴支付统一收银台；保留脚本代理/滑块/签到能力；定时检测到期提醒。]

# [param: {"required":true,"key":"rainyun.ql_config","bool":false,"placeholder":"http://地址:端口丨ClientID丨ClientSecret","name":"对接青龙","desc":"青龙地址丨ClientID丨ClientSecret"}]
# [param: {"required":true,"key":"rainyun.osname","bool":false,"placeholder":"默认:dw_yy","name":"系统变量名","desc":"青龙环境变量名(默认为dw_yy)"}]
# [param: {"required":true,"key":"rainyun.zsVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"授权价格","desc":"单账号授权每月价格，单位为元"}]
# [param: {"required":false,"key":"rainyun.enable_proxy","bool":true,"name":"启用代理","desc":"是否为雨云接口启用代理"}]
# [param: {"required":false,"key":"rainyun.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"返回单个代理地址的接口"}]
# [param: {"required":false,"key":"rainyun.verify_token","bool":false,"placeholder":"2captcha clientKey","name":"滑块Token","desc":"对应脚本VERIFY_TOKEN，用于签到滑块验证"}]
# [param: {"required":false,"key":"rainyun.invite_url","bool":false,"placeholder":"https://www.rainyun.com/MTA4NzA0_","name":"推广链接","desc":"雨云推广/注册链接"}]

import hashlib
import json
import logging
import random
import re
import time
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation

import middleware
import qingyun_payment
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rainyun_plugin")

SCRIPT_NAME = "雨云"
BUCKET_PREFIX = "rainyun"
QL_ENV_NAME = middleware.bucketGet(BUCKET_PREFIX, "osname") or "dw_yy"
REQUEST_TIMEOUT = 30

sender_id = middleware.getSenderID()
sender = middleware.Sender(sender_id)
user_id = sender.getUserID()


class PluginError(RuntimeError):
    """插件运行过程中可直接展示给用户的错误。"""


def mask_account(account):
    """隐藏账号敏感信息（手机号/邮箱/长ID）。"""
    account = str(account or "")
    if re.fullmatch(r"1\d{10}", account):
        return account[:3] + "****" + account[-4:]
    if "@" in account:
        name, domain = account.split("@", 1)
        if len(name) <= 2:
            return name[:1] + "***@" + domain
        return name[:2] + "***@" + domain
    if len(account) > 8:
        return account[:3] + "****" + account[-3:]
    return account


def encrypt_token(token):
    # 不加密，明文存储
    return str(token or "")


def decrypt_token(encrypted_token):
    # 不解密，明文读取
    return str(encrypted_token or "")


# ===================== 数据层（对齐芳华四桶） =====================

def get_display_name(account_id):
    """获取账号的显示名（优先使用绑定的登录账号，否则回退到 account_id）。"""
    account_id = str(account_id or "").strip()
    acct = middleware.bucketGet(f"{BUCKET_PREFIX}_acct", account_id)
    return str(acct or account_id)


def get_account_token(account_id):
    """读取账号绑定的雨云 Token（JSON 形式 csrf/cookie/user/pwd）。"""
    account_id = str(account_id or "").strip()
    if not account_id:
        return ""
    raw = str(middleware.bucketGet(f"{BUCKET_PREFIX}_token", account_id) or "")
    if not raw:
        return ""
    return decrypt_token(raw) if raw else ""


def save_account_token(account_id, token):
    """保存账号的雨云 Token（明文存储）。"""
    account_id = str(account_id or "").strip()
    token = str(token or "").strip()
    if not token:
        raise PluginError("保存失败：Token 为空")
    middleware.bucketSet(f"{BUCKET_PREFIX}_token", account_id, encrypt_token(token))


def get_user_accounts():
    """读取当前用户绑定的账号 ID 列表。"""
    raw = middleware.bucketGet(f"{BUCKET_PREFIX}_user", user_id) or "[]"
    try:
        result = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        result = []
    return [str(p) for p in result] if isinstance(result, list) else []


def save_user_accounts(accounts):
    """保存当前用户绑定的账号 ID 列表。"""
    middleware.bucketSet(
        f"{BUCKET_PREFIX}_user",
        user_id,
        json.dumps(accounts, ensure_ascii=False),
    )


def get_auth_time(account_id):
    """读取账号授权到期日期。"""
    return str(middleware.bucketGet(f"{BUCKET_PREFIX}_auth", account_id) or "")


def is_authorized(account_id):
    """判断账号授权是否仍在有效期内。"""
    auth_time = get_auth_time(account_id)
    return bool(auth_time and auth_time > str(datetime.now().date()))


def calculate_auth_time(account_id, days):
    """从当前日期或现有到期日期继续累加授权天数。"""
    today = datetime.now().date()
    auth_time = get_auth_time(account_id)
    start_date = today
    if auth_time:
        try:
            current_expiry = datetime.strptime(auth_time, "%Y-%m-%d").date()
            if current_expiry > today:
                start_date = current_expiry
        except ValueError:
            pass
    if days < 0 and (start_date + timedelta(days=days)) < today:
        return str(today)
    return str(start_date + timedelta(days=days))


def get_config(key, default=None):
    """读取插件配置桶值。"""
    raw = middleware.bucketGet(BUCKET_PREFIX, key)
    return raw if raw is not None else default


def is_proxy_enabled():
    return str(get_config("enable_proxy", "false") or "false").lower() in {"true", "1", "yes"}


def get_payment_config():
    """读取并校验授权价格（元/月）。"""
    try:
        price = Decimal(str(get_config("zsVipmoney", "0") or "0"))
    except (InvalidOperation, ValueError) as exc:
        raise PluginError(f"授权价格配置错误：{exc}") from exc
    return price


def get_verify_token():
    return get_config("verify_token") or ""


def get_invite_url():
    return get_config("invite_url") or "https://www.rainyun.com/MTA4NzA0_"


# ===================== 青龙对接（对齐芳华） =====================
def parse_qinglong_config():
    """读取并校验青龙连接配置。"""
    config = get_config("ql_config")
    if not config:
        raise PluginError("未配置青龙连接")
    parts = [value.strip() for value in re.split(r"[丨|]", config) if value.strip()]
    if len(parts) != 3:
        raise PluginError("青龙配置格式应为 地址丨ClientID丨ClientSecret")
    url, client_id, client_secret = parts
    return url.rstrip("/"), client_id, client_secret


def get_qinglong_token(url, client_id, client_secret):
    """获取青龙开放接口访问令牌。"""
    response = requests.get(
        f"{url}/open/auth/token",
        params={"client_id": client_id, "client_secret": client_secret},
        timeout=15,
        verify=False,
    )
    data = response.json()
    token = data.get("data", {}).get("token") if isinstance(data, dict) else None
    if not token:
        raise PluginError("获取青龙访问令牌失败")
    return str(token)


def qinglong_context():
    """构造青龙地址和认证请求头。"""
    url, client_id, client_secret = parse_qinglong_config()
    token = get_qinglong_token(url, client_id, client_secret)
    return url, {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_qinglong_envs(url, headers):
    """获取青龙环境变量列表。"""
    response = requests.get(f"{url}/open/envs", headers=headers, timeout=15, verify=False)
    data = response.json().get("data", [])
    return data if isinstance(data, list) else []


def get_env_id(env):
    """兼容不同青龙版本的环境变量编号字段。"""
    return env.get("id", env.get("_id"))


def submit_to_qinglong(account_id, owner_id, token=""):
    """按模板格式新增或更新单个账号的青龙环境变量（值为 账号#密码）。"""
    account_id = str(account_id)
    login_name = middleware.bucketGet(f"{BUCKET_PREFIX}_acct", account_id) or ""
    password_enc = middleware.bucketGet(f"{BUCKET_PREFIX}_pwd", account_id) or ""
    password = decrypt_token(password_enc) if password_enc else ""
    if login_name and password:
        ql_value = f"{login_name}#{password}"
    else:
        ql_value = str(token or get_account_token(account_id))
        if not ql_value:
            raise PluginError("未找到可用凭证，请先登录")

    url, headers = qinglong_context()
    envs = get_qinglong_envs(url, headers)
    # 提取待提交值的账号部分（# 前面），用于值匹配
    match_account = ql_value.split("#", 1)[0].strip() if "#" in ql_value else ql_value.strip()

    target_env = None
    for env in envs:
        # 第一步：用变量名查找
        if env.get("name") != QL_ENV_NAME:
            continue
        # 第二步：用值匹配（账号部分相同即视为同一变量）
        env_value = str(env.get("value", ""))
        env_account = env_value.split("#", 1)[0].strip() if "#" in env_value else env_value.strip()
        if match_account and env_account == match_account:
            target_env = env
            break

    auth_time = get_auth_time(account_id) or "未授权"
    safe_id = mask_account(get_display_name(account_id))
    remarks_parts = [f"雨云:{safe_id}", f"到期:{auth_time}", f"用户:{owner_id}", f"ID:{account_id}", "雨云提交"]
    remarks = "丨".join(remarks_parts)
    data = {"name": QL_ENV_NAME, "value": ql_value, "remarks": remarks}
    env_id = get_env_id(target_env) if target_env else None
    if env_id is not None:
        put_data = dict(data, id=env_id)
        try:
            response_data = _ql_request("PUT", f"{url}/open/envs", headers, put_data)
        except PluginError as exc:
            if "Validation" not in str(exc):
                raise
            logger.warning("青龙 PUT 更新失败，回退到 POST 新建: %s", exc)
            try:
                requests.delete(f"{url}/open/envs", headers=headers, json=[env_id], timeout=15, verify=False)
            except Exception:
                pass
            response_data = _ql_request("POST", f"{url}/open/envs", headers, [data])
    else:
        response_data = _ql_request("POST", f"{url}/open/envs", headers, [data])
    new_envs = response_data.get("data", []) if isinstance(response_data, dict) else []
    if isinstance(new_envs, list) and new_envs:
        env_id = get_env_id(new_envs[0])
    return True


def _ql_request(method, url, headers, json_body, timeout=15):
    """发送青龙请求并校验响应，失败时附带 HTTP 状态码与原始响应便于定位 Validation error。"""
    try:
        response = requests.request(method, url, headers=headers, json=json_body, timeout=timeout, verify=False)
    except requests.RequestException as exc:
        raise PluginError(f"青龙请求异常({method} {url}): {exc}")
    try:
        response_data = response.json()
    except ValueError:
        raise PluginError(f"青龙响应非JSON({response.status_code}): {(response.text or "")[:120]}")
    if isinstance(response_data, dict) and response_data.get("code") not in (None, 0, 200):
        raw_msg = response_data.get("message") or response_data.get("msg") or "提交青龙失败"
        raise PluginError(f"{raw_msg}(HTTP {response.status_code}, 响应: {str(response_data)[:200]})")
    return response_data


def delete_qinglong_env(account_id):
    """按账号备注查找并删除对应青龙环境变量。"""
    account_id = str(account_id)
    url, headers = qinglong_context()
    ids_to_delete = []
    for env in get_qinglong_envs(url, headers):
        if env.get("name") != QL_ENV_NAME:
            continue
        remarks = str(env.get("remarks", ""))
        if account_id in remarks or f"ID:{account_id}" in remarks:
            env_id = get_env_id(env)
            if env_id is not None:
                ids_to_delete.append(env_id)
    if ids_to_delete:
        requests.delete(f"{url}/open/envs", headers=headers, json=ids_to_delete, timeout=15, verify=False)
    return True


# ===================== 雨云 API 客户端 =====================
class RainyunClient:
    """雨云 API 客户端：登录/查询/签到逻辑来自签到脚本，适配插件账密存储。"""

    BASE_URL = "https://api.v2.rainyun.com"

    def __init__(self, credential="", account_id=None):
        self.credential = self.normalize_credential(credential)
        self.username, self.password = self.parse_credential(self.credential)
        self.account_id = str(account_id) if account_id else ""
        self.session = requests.Session()
        self.csrf_token = ""
        self.cookie = ""
        self.proxies = None
        self.nickname = ""
        self.user_id = ""
        self.email = ""
        self.points = 0
        self.last_ip = ""
        self.last_login_area = ""
        self.score = "0"
        self.app_token = ""
        self.mobile = self.username
        if self.credential.startswith("{") or (self.credential and not self.password):
            self._load_token(self.credential)
        self._set_proxy()
        self._update_headers()

    @staticmethod
    def normalize_credential(raw):
        return str(raw or "").strip().strip('"').strip("'").replace("\r", "").replace("\n", "")

    @staticmethod
    def parse_credential(raw):
        raw = str(raw or "").strip()
        if not raw or raw.startswith("{"):
            return "", ""
        if "#" not in raw:
            return "", ""
        parts = [p.strip() for p in raw.split("#") if p.strip()]
        if len(parts) == 2:
            return parts[0], parts[1]
        return "", ""

    def _load_token(self, token):
        try:
            raw = str(token or "").strip()
            if raw.startswith("{"):
                data = json.loads(raw)
                self.csrf_token = data.get("csrf") or data.get("csrf_token") or ""
                self.cookie = data.get("cookie") or ""
                if data.get("username"):
                    self.username = str(data.get("username"))
                    self.mobile = self.username
                if data.get("password"):
                    self.password = str(data.get("password"))
            else:
                self.cookie = raw
        except Exception:
            self.cookie = str(token or "")

    def export_token(self):
        data = {"csrf": self.csrf_token or "", "cookie": self.cookie or ""}
        if self.username:
            data["username"] = self.username
        if self.password:
            data["password"] = self.password
        return json.dumps(data, ensure_ascii=False)

    def _update_headers(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Origin": "https://app.rainyun.com",
            "Referer": "https://app.rainyun.com/",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        if self.csrf_token:
            self.headers["x-csrf-token"] = self.csrf_token
            self.headers["X-CSRF-Token"] = self.csrf_token
        if self.cookie:
            self.headers["Cookie"] = self.cookie

    def _set_proxy(self):
        self.proxies = None
        if not is_proxy_enabled():
            return
        proxy_api = get_config("proxy_pool_url")
        if not proxy_api:
            return
        try:
            res = requests.get(proxy_api, timeout=8, verify=False)
            proxy = (res.text or "").strip()
            match = re.search(r"(?:https?://)?(?:[\w.-]+:[\w.-]+@)?\d+\.\d+\.\d+\.\d+:\d+", proxy)
            if match:
                proxy = match.group(0)
            if not proxy:
                return
            if not proxy.startswith(("http://", "https://")):
                proxy = "http://" + proxy
            self.proxies = {"http": proxy, "https": proxy}
            self.session.proxies.update(self.proxies)
            logger.info("已启用代理: %s" % proxy)
        except Exception as e:
            logger.warning("获取代理失败: %s" % e)

    def _fetch_one_proxy(self):
        """从代理池拉取一个新代理地址，返回标准化的 proxies dict 或 None。"""
        proxy_api = get_config("proxy_pool_url")
        if not proxy_api:
            return None
        res = requests.get(proxy_api, timeout=8, verify=False)
        proxy = (res.text or "").strip()
        match = re.search(r"(?:https?://)?(?:[\w.-]+:[\w.-]+@)?\d+\.\d+\.\d+\.\d+:\d+", proxy)
        if match:
            proxy = match.group(0)
        if not proxy:
            return None
        if not proxy.startswith(("http://", "https://")):
            proxy = "http://" + proxy
        return {"http": proxy, "https": proxy}

    def _refresh_proxy(self):
        """切换到代理池中的新代理；失败则清空代理走直连。"""
        if not is_proxy_enabled():
            self.proxies = None
            self.session.proxies.clear()
            return False
        for _ in range(3):
            try:
                new_proxies = self._fetch_one_proxy()
                if new_proxies:
                    self.proxies = new_proxies
                    self.session.proxies.update(new_proxies)
                    logger.info("已切换代理: %s" % new_proxies["http"])
                    return True
            except Exception as e:
                logger.warning("切换代理失败: %s" % e)
            time.sleep(1)
        logger.warning("连续多次切换代理失败，回退直连")
        self.proxies = None
        self.session.proxies.clear()
        return False

    @staticmethod
    def _is_proxy_or_network_error(err):
        """判断异常是否为代理/网络类错误（应切换 IP 后重试）。"""
        msg = str(err).lower()
        keywords = (
            "proxy",
            "tunnel",
            "max retries exceeded",
            "proxyerror",
            "proxy authentication",
            "643",
            "407",
            "connection",
            "timeout",
            "connectionerror",
            "ssl",
        )
        return any(kw in msg for kw in keywords)

    def get_slide_verify(self):
        token = get_verify_token()
        if not token:
            logger.error("未配置 rainyun.verify_token")
            return "", ""
        data = {
            "clientKey": token,
            "task": {
                "type": "TencentTaskProxyless",
                "appId": "2039519451",
                "websiteURL": "https://www.rainyun.com/",
            },
        }
        task_id = ""
        try:
            r = self.session.post(
                "https://api.2captcha.com/createTask",
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=20,
            )
            result = r.json()
            if result.get("errorId") == 0:
                task_id = result.get("taskId")
                logger.info("创建滑块任务成功 taskId=%s" % task_id)
            else:
                logger.error("创建滑块任务失败: %s" % result)
                return "", ""
        except Exception as e:
            logger.error("创建滑块任务异常: %s" % e)
            return "", ""
        for i in range(12):
            try:
                time.sleep(10)
                r = self.session.post(
                    "https://api.2captcha.com/getTaskResult",
                    headers={"Content-Type": "application/json"},
                    json={"clientKey": token, "taskId": task_id},
                    timeout=20,
                )
                result = r.json()
                if result.get("status") == "ready" and result.get("errorId") == 0:
                    solution = result.get("solution") or {}
                    if solution.get("ticket") and solution.get("randstr"):
                        return solution.get("ticket"), solution.get("randstr")
            except Exception as e:
                logger.error("第%s次验证码获取失败: %s" % (i + 1, e))
        return "", ""

    def login(self, username=None, password=None, allow_captcha=True):
        username = username or self.username
        password = password or self.password
        if not username or not password:
            raise RuntimeError("账号或密码为空")

        # 恢复为字符串，因为强转整形会导致 "输入参数无效" 报错
        field_val = username

        payload = {"field": field_val, "password": password}
        last_msg = "登录失败"
        max_attempts = 5 if is_proxy_enabled() else 3
        last_exc = None
        for i in range(1, max_attempts + 1):
            try:
                r = self.session.post(
                    self.BASE_URL + "/user/login",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    proxies=self.proxies,
                    timeout=15,
                )
                res_data = {}
                try:
                    res_data = r.json()
                except Exception:
                    pass
                need_captcha = False
                if r.status_code == 400 and (
                        res_data.get("code") in (10004, 30001)
                        or "验证" in str(res_data.get("message", ""))
                ):
                    need_captcha = True
                if need_captcha and allow_captcha:
                    ticket, randstr = self.get_slide_verify()
                    if not ticket:
                        raise RuntimeError("触发滑块验证但获取票据失败")
                    payload = {
                        "field": field_val,
                        "password": password,
                        "vticket": ticket,
                        "vrandstr": randstr,
                    }
                    r = self.session.post(
                        self.BASE_URL + "/user/login",
                        headers={"Content-Type": "application/json"},
                        json=payload,
                        proxies=self.proxies,
                        timeout=15,
                    )
                    try:
                        res_data = r.json()
                    except Exception:
                        res_data = {}
                cookie_dict = r.cookies.get_dict() if r is not None else {}
                csrf = cookie_dict.get("X-CSRF-Token") or r.cookies.get("X-CSRF-Token")
                if not csrf:
                    raw_cookies = r.headers.get("Set-Cookie", "") or ""
                    m = re.search(r"X-CSRF-Token=([^;]+)", raw_cookies)
                    if m:
                        csrf = m.group(1)
                cookie_parts = []
                if "rain-session" in cookie_dict:
                    cookie_parts.append("rain-session=%s" % cookie_dict["rain-session"])
                if not cookie_parts:
                    raw_cookies = r.headers.get("Set-Cookie", "") or ""
                    m = re.search(r"(rain-session=[^;]+)", raw_cookies)
                    if m:
                        cookie_parts.append(m.group(1))
                ok_http = r.status_code == 200
                ok_code = res_data.get("code") in (200, 0, None) or bool(csrf)
                if ok_http and ok_code and csrf:
                    self.csrf_token = csrf
                    if cookie_parts:
                        self.cookie = "; ".join(cookie_parts)
                    else:
                        self.cookie = "; ".join(["%s=%s" % (k, v) for k, v in cookie_dict.items()])
                    self.username = username
                    self.password = password
                    self.mobile = username
                    self.app_token = self.export_token()
                    self._update_headers()
                    return self.app_token
                last_msg = res_data.get("message") or res_data.get("msg") or ("HTTP %s" % r.status_code)
                logger.info("第%s次登录失败: %s" % (i, last_msg))
            except Exception as e:
                last_msg = str(e)
                last_exc = e
                logger.error("第%s次登录失败: %s" % (i, e))

            if i < max_attempts:
                # 代理/网络类错误：切换 IP 后重试
                check_err = last_exc if last_exc is not None else last_msg
                if self._is_proxy_or_network_error(check_err):
                    logger.warning("检测到代理/网络错误，尝试切换代理")
                    self._refresh_proxy()
                    last_exc = None
                time.sleep(2)

        raise RuntimeError(last_msg)

    def silent_relogin(self):
        username = self.username
        password = self.password
        if self.account_id:
            username = middleware.bucketGet(f"{BUCKET_PREFIX}_acct", self.account_id) or username
            pwd_enc = middleware.bucketGet(f"{BUCKET_PREFIX}_pwd", self.account_id) or ""
            if pwd_enc:
                password = decrypt_token(pwd_enc)
        if not username or not password:
            return False
        try:
            self.login(username, password)
            if self.account_id:
                save_account_token(self.account_id, self.export_token())
                try:
                    middleware.bucketSet(f"{BUCKET_PREFIX}_acct", self.account_id, username)
                    middleware.bucketSet(f"{BUCKET_PREFIX}_pwd", self.account_id, encrypt_token(password))
                except Exception:
                    pass
            return True
        except Exception as e:
            logger.warning("静默重登失败: %s" % e)
            return False

    def _request(self, method, url, **kwargs):
        self._update_headers()
        kwargs.setdefault("timeout", REQUEST_TIMEOUT)
        if self.proxies:
            kwargs.setdefault("proxies", self.proxies)
        headers = dict(self.headers)
        headers.update(kwargs.pop("headers", {}) or {})
        for attempt in range(2):
            res = self.session.request(method, url, headers=headers, **kwargs)
            need_relogin = False
            if res.status_code in (401, 403):
                need_relogin = True
            else:
                try:
                    data = res.json()
                    code = data.get("code")
                    msg = str(data.get("message") or data.get("msg") or "")
                    if code in (30002, 401, 403) or "login" in msg.lower() or "登录" in msg or "session" in msg.lower():
                        need_relogin = True
                except Exception:
                    pass
            if need_relogin and attempt == 0 and self.silent_relogin():
                self._update_headers()
                headers = dict(self.headers)
                continue
            return res
        return None

    def refresh_profile(self):
        if not self.csrf_token and self.username and self.password:
            self.login()
        if not self.csrf_token:
            raise RuntimeError("未获取到csrf_token")
        r = self._request("GET", self.BASE_URL + "/user/?no_cache=false")
        data = r.json() if r is not None else {}
        if data.get("code") != 200:
            if self.username and self.password and self.silent_relogin():
                r = self._request("GET", self.BASE_URL + "/user/?no_cache=false")
                data = r.json() if r is not None else {}
        if data.get("code") != 200:
            raise RuntimeError(data.get("message") or data.get("msg") or "获取用户信息失败")
        d = data.get("data") or {}
        self.nickname = str(d.get("Name") or d.get("name") or self.username or "")
        self.email = str(d.get("Email") or d.get("email") or "")
        self.points = d.get("Points") if d.get("Points") is not None else d.get("points", 0)
        self.score = str(self.points)
        self.last_ip = str(d.get("LastIP") or d.get("last_ip") or "")
        self.last_login_area = str(d.get("LastLoginArea") or d.get("last_login_area") or "")
        self.user_id = str(
            d.get("ID") or d.get("Id") or d.get("Uid") or d.get("uid") or d.get("UserID") or self.user_id or ""
        )
        self.mobile = self.username or self.mobile
        self.app_token = self.export_token()
        return data

    def get_info(self):
        try:
            self.refresh_profile()
            msg = "积分: %s | 邮箱: %s | IP: %s | 地区: %s" % (
                self.score,
                self.email or "-",
                self.last_ip or "-",
                self.last_login_area or "-",
            )
            return True, True, self.score, msg
        except Exception as e:
            return False, False, 0, str(e)

    def check_info(self):
        if self.username and self.password and not self.csrf_token:
            self.login()
        self.refresh_profile()
        acc_key = str(self.user_id or "").strip()
        if not acc_key:
            acc_key = hashlib.md5(str(self.username or self.credential).encode()).hexdigest()[:16]
        self.uid = acc_key
        final_token = self.export_token()
        self.app_token = final_token
        return {
            "nickname": self.nickname or self.username or "未知用户",
            "final_token": final_token,
            "acc_key": acc_key,
            "aliases": [x for x in [self.username, self.email, self.user_id] if x],
            "mobile": self.username or "",
            "score": self.score,
            "email": self.email,
            "points": self.points,
            "last_ip": self.last_ip,
            "last_login_area": self.last_login_area,
        }

    def check_sign_in(self):
        if not self.csrf_token:
            return None
        try:
            r = self._request("GET", self.BASE_URL + "/user/reward/tasks")
            data = r.json() if r is not None else {}
            for task in data.get("data") or []:
                if task.get("Name") == "每日签到":
                    return task.get("Status") == 2
            return False
        except Exception as e:
            logger.error("检查签到状态失败: %s" % e)
            return None

    def sign_in(self, ticket, randstr):
        if not self.csrf_token:
            return False, "未获取到csrf_token"
        try:
            r = self._request(
                "POST",
                self.BASE_URL + "/user/reward/tasks",
                json={
                    "task_name": "每日签到",
                    "verifyCode": "",
                    "vticket": ticket,
                    "vrandstr": randstr,
                },
            )
            ret = r.json() if r is not None else {}
            if ret.get("code") == 30011:
                return False, "今日已签到"
            return ret.get("code") == 200, ret.get("message") or ret.get("msg") or "未知错误"
        except Exception as e:
            return False, str(e)

    def run_daily_tasks(self, display_name=""):
        sign_status = "未知"
        try:
            signed = self.check_sign_in()
            if signed is True:
                sign_status = "今日已签到"
            elif signed is False:
                time.sleep(random.randint(1, 3))
                ticket, randstr = self.get_slide_verify()
                if not ticket:
                    sign_status = "验证失败"
                else:
                    ok, msg = self.sign_in(ticket, randstr)
                    sign_status = "签到成功" if ok else msg
            else:
                sign_status = "检查签到失败"
        except Exception as e:
            sign_status = "签到异常: %s" % e
        try:
            self.refresh_profile()
        except Exception:
            pass
        name = display_name or self.nickname or self.username or "未知"
        return (
            "=======运行结果=======\n"
            "📱【账号】%s\n"
            "📧【邮箱】%s\n"
            "📝【签到】%s\n"
            "💰【积分】%s\n"
            "🌐【IP】%s\n"
            "📍【地区】%s\n"
        ) % (
            mask_account(name),
            mask_account(self.email or "-"),
            sign_status,
            self.score,
            self.last_ip or "-",
            self.last_login_area or "-",
        )


# ===================== 业务逻辑 =====================
def parse_bind_input_line(line):
    """解析一行 账号#密码，返回 (client, remark)。"""
    raw = str(line or "").strip()
    if not raw:
        raise PluginError("内容为空")
    parts = [p.strip() for p in raw.split("#") if p.strip()]
    if len(parts) != 2:
        raise PluginError("格式错误，正确格式：账号#密码")
    client = RainyunClient(f"{parts[0]}#{parts[1]}")
    if not client.username or not client.password:
        raise PluginError("格式错误，正确格式：账号#密码")
    return client, ""


def get_user_input(timeout=60):
    """获取用户回复输入，q/退出 返回 'q'。"""
    try:
        response = sender.listen(timeout * 1000)
        if not response:
            return None
        response = str(response).strip()
        if response.lower() in ["q", "quit", "exit", "退出", "cancel"]:
            return "q"
        return response
    except Exception:
        return None


def process_payment(months, account_count=1):
    """接入清蕴支付统一收银台。"""
    try:
        months = int(months)
        account_count = int(account_count)
    except (TypeError, ValueError):
        sender.reply("❌ 授权参数无效")
        return False
    if months <= 0 or account_count <= 0:
        sender.reply("❌ 授权月数/账号数必须大于0")
        return False

    try:
        money = (Decimal(months) * Decimal(account_count) * get_payment_config()).quantize(Decimal("0.01"))
        amount = float(money)
    except Exception:
        sender.reply("❌ 支付金额无效")
        return False

    if amount <= 0:
        return True

    days = months * 30
    header_extra = (
        f"🎫 商品: 雨云代挂授权\n"
        f"📅 时长: {months}个月({days}天)\n"
        f"👥 账号数: {account_count}"
    )
    try:
        pay_res = qingyun_payment.QingyunCompletePayment.start_checkout(
            sender=sender,
            amount=amount,
            title="雨云授权",
            order_name=f"雨云授权_{months}M_{account_count}A",
            user_id=str(user_id),
            header_extra=header_extra,
        )
    except Exception as e:
        logger.error(f"清蕴支付调用失败: {e}")
        sender.reply(f"❌ 支付模块异常: {e}")
        return False

    if not isinstance(pay_res, dict) or pay_res.get("code") != 0:
        return False

    try:
        paid_money = float(pay_res.get("paid_money", amount) or amount)
    except Exception:
        paid_money = amount

    if paid_money + 1e-6 < amount:
        sender.reply(
            "=======支付失败=======\n"
            "❌ 支付金额不足\n"
            "------------------\n"
            f"💰【应付】{amount}元\n"
            f"💵【实付】{paid_money}元\n"
        )
        return False
    return True


def authorize_accounts(accounts, months=None):
    """为一个或多个账号完成付款、写入授权日期并提交青龙。"""
    if not accounts:
        return
    if months is None:
        sender.reply("请输入授权月数，例如 1；回复 q 退出")
        months_text = get_user_input(timeout=60)
        if not months_text or months_text.lower() == "q":
            sender.reply("✅ 已取消授权")
            return
        try:
            months = int(months_text)
            if months <= 0:
                raise ValueError
        except (TypeError, ValueError):
            sender.reply("❌ 授权月数必须是正整数")
            return

    count = len(accounts)
    total_money = (Decimal(months) * get_payment_config() * count).quantize(Decimal("0.01"))
    sender.reply(
        f"=======授权确认=======\n"
        f"👥【账号数量】{count}个\n"
        f"📅【授权时长】{months}个月\n"
        f"💰【总需金额】{total_money}元\n"
        f"------------------\n"
        f"即将进入清蕴支付收银台\n"
        f"回复 y 继续，q 取消"
    )
    confirm = get_user_input(timeout=60)
    if not confirm or confirm.lower() != "y":
        sender.reply("✅ 已取消批量授权")
        return

    if not process_payment(months, account_count=count):
        return

    sender.reply(f"🚀 支付成功，正在处理 {count} 个账号...")
    days = months * 30
    success_count = 0
    errors = []
    for account_id in accounts:
        account_id = str(account_id)
        try:
            token = get_account_token(account_id)
            auth_time = calculate_auth_time(account_id, days)
            middleware.bucketSet(f"{BUCKET_PREFIX}_auth", account_id, auth_time)
            if token:
                submit_to_qinglong(account_id, user_id, token)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_account(get_display_name(account_id))}：{exc}")

    report = (
        "=======授权完成=======\n"
        f"📅【授权】{months} 个月\n"
        f"✅【成功】{success_count} 个账号\n"
        f"❌【失败】{len(errors)} 个账号"
    )
    if errors:
        report += "\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)



def batch_login():
    """账密批量登录：输入 账号#密码（换行分隔），登录校验后保存 Token。"""
    invite = get_invite_url()
    sender.reply(
        "=======雨云登录=======\n"
        "请直接发送数据，格式如下(一行一个)：\n"
        "账号#密码\n"
        "------------------\n"
        f"注册: {invite}\n"
        "支持批量登录(换行分隔)\n"
        '回复"q"退出操作\n'
    )

    input_str = get_user_input(timeout=180)
    if not input_str or input_str.lower() == "q":
        sender.reply("✅ 已退出")
        return

    token_lines = [line.strip() for line in str(input_str).replace("\r", "\n").split("\n") if line.strip()]
    if not token_lines:
        sender.reply("内容为空")
        return

    sender.reply("正在处理 %s 个账号，请稍候..." % len(token_lines))
    bind_stats = {"success": 0, "fail": 0, "new": 0, "update": 0}
    fail_msgs = []

    for line in token_lines:
        try:
            client, _ = parse_bind_input_line(line)
            info_res = client.check_info()
            acc_id = info_res["acc_key"]
            final_token = info_res["final_token"]
            nick = info_res["nickname"]

            # 保存账密，供面板变量与静默重登
            try:
                middleware.bucketSet(f"{BUCKET_PREFIX}_acct", acc_id, client.username)
                middleware.bucketSet(f"{BUCKET_PREFIX}_pwd", acc_id, encrypt_token(client.password))
                # 存储用户手机号/邮箱/ID（优先手机号，其次邮箱，最后ID）
                phone_info = client.mobile or info_res.get("mobile") or info_res.get("email") or acc_id
                middleware.bucketSet(f"{BUCKET_PREFIX}_phone", acc_id, phone_info)
            except Exception:
                pass

            save_account_token(acc_id, final_token)
            current_accounts = get_user_accounts()
            if acc_id in current_accounts:
                status = "更新成功"
                bind_stats["update"] += 1
            else:
                current_accounts.append(acc_id)
                save_user_accounts(current_accounts)
                status = "登录成功"
                bind_stats["new"] += 1
            bind_stats["success"] += 1

            if is_authorized(acc_id):
                submit_to_qinglong(acc_id, user_id, final_token)
                status += "，已同步青龙"
            else:
                status += "，账号未授权，暂未提交青龙"

            if len(token_lines) == 1:
                sender.reply(
                    "=======账号更新=======\n"
                    f"📱【账号】{mask_account(nick)}\n"
                    f"🆔【ID】{mask_account(get_display_name(acc_id))}\n"
                    f"✅【状态】{status}\n"
                )
        except Exception as ex:
            bind_stats["fail"] += 1
            fail_msgs.append(str(ex)[:50])
            if len(token_lines) == 1:
                sender.reply("登录处理失败: %s" % str(ex))
            import traceback
            traceback.print_exc()

    if len(token_lines) > 1:
        fail_text = ""
        if fail_msgs:
            fail_text = "\n失败原因: " + "；".join(list(dict.fromkeys(fail_msgs))[:3])
        sender.reply(
            "=======登录汇总=======\n"
            f"✅【成功】{bind_stats['success']} 个\n"
            f"🆕【新增】{bind_stats['new']} 个\n"
            f"🔄【更新】{bind_stats['update']} 个\n"
            f"❌【失败】{bind_stats['fail']} 个{fail_text}\n"
        )

def query_single(account_id):
    """查询单个雨云账号信息。"""
    account_id = str(account_id)
    auth_time = get_auth_time(account_id)
    today = str(datetime.now().date())
    if not auth_time:
        auth_time = "无"
    elif auth_time >= today:
        pass  # 有效授权

    token = get_account_token(account_id)
    live = "未知"
    points = "-"
    sign_status = "未知"
    region = "未知"
    extra = ""
    display_name = get_display_name(account_id)
    if not token:
        live = "无凭证"
    else:
        try:
            client = RainyunClient(token, account_id=account_id)
            acct = middleware.bucketGet(f"{BUCKET_PREFIX}_acct", account_id) or ""
            pwd_enc = middleware.bucketGet(f"{BUCKET_PREFIX}_pwd", account_id) or ""
            if acct:
                client.username = acct
                client.mobile = acct
            if pwd_enc:
                client.password = decrypt_token(pwd_enc)

            ok, valid, score, msg = client.get_info()
            if ok and valid:
                live = "存活"
                points = score

                signed = client.check_sign_in()
                if signed is True:
                    sign_status = "今日已签"
                elif signed is False:
                    sign_status = "今日未签"
                else:
                    sign_status = "未知状态"

                region = client.last_login_area or "未知"

                new_acct = client.username or client.email or client.mobile
                if new_acct and new_acct != account_id:
                    middleware.bucketSet(f"{BUCKET_PREFIX}_acct", account_id, new_acct)
                    display_name = new_acct

                # 同步用户手机号/邮箱/ID
                phone_info = client.mobile or client.email or client.user_id or account_id
                try:
                    middleware.bucketSet(f"{BUCKET_PREFIX}_phone", account_id, phone_info)
                except Exception:
                    pass
            else:
                live = "失效"
                extra = msg
        except Exception as e:
            live = "异常"
            extra = str(e)

    if live == "存活":
        return (
            "=======账号查询=======\n"
            "📱【账号】%s\n"
            "💰【积分】%s\n"
            "📝【签到】%s\n"
            "📍【登录地区】%s\n"
            "⏰【授权到期】%s\n"
        ) % (
            mask_account(display_name),
            points,
            sign_status,
            region,
            auth_time,
        )
    else:
        return (
            "=======账号查询=======\n"
            "📱【账号】%s\n"
            "🔴【状态】%s\n"
            "⏰【授权到期】%s\n"
            "⚠️【详情】%s\n"
        ) % (
            mask_account(display_name),
            live,
            auth_time,
            extra or "-",
        )


def query():
    """查询一个或全部已绑定雨云账号。"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 未绑定账号，请先发送“雨云登录”")
        return

    total_count = len(accounts)
    menu = "=======雨云查询=======\n[0] 全选"
    for i, acc in enumerate(accounts, 1):
        menu += f"\n[{i}] {mask_account(get_display_name(acc))}"
    menu += "\n------------------\n支持单选/多选/区间，如 1,2 或 3-6\n回复q退出"
    sender.reply(menu)

    sel = get_user_input(timeout=60)
    if not sel or sel.lower() == "q":
        sender.reply("✅ 已退出")
        return

    if sel.strip() == "0":
        target = accounts
    else:
        selected_idxs, invalid_parts = parse_index_selection(sel, total_count, allow_all=False)
        target = [accounts[idx - 1] for idx in selected_idxs]
        if not target:
            sender.reply("❌ 请输入有效序号，例如 1,2 或 3-6")
            return
        if invalid_parts:
            sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")

    sender.reply(f"🚀 正在查询 {len(target)} 个账号，请稍候...")
    for account_id in target:
        sender.reply(query_single(account_id))


def parse_index_selection(text, total_count, allow_all=True):
    """解析 1,2 或 3-6 形式的序号选择。"""
    try:
        if text is None:
            return [], []
        raw = str(text).strip()
        if not raw:
            return [], []
        if allow_all and raw.lower() in ["a", "all", "全部", "全选"]:
            return list(range(1, total_count + 1)), []
        selected = []
        invalid = []
        parts = re.split(r"[,\s，、;；]+", raw)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            range_match = re.match(r"^(\d+)\s*(?:-|~|到|至)\s*(\d+)$", part)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                if start > end:
                    start, end = end, start
                start = max(1, start)
                end = min(total_count, end)
                if start <= end:
                    selected.extend(range(start, end + 1))
                else:
                    invalid.append(part)
                continue
            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= total_count:
                    selected.append(idx)
                else:
                    invalid.append(part)
                continue
            invalid.append(part)
        return list(dict.fromkeys(selected)), invalid
    except Exception:
        return [], [str(text)]


def delete_account(account_id):
    """删除插件中的账号并同步删除青龙变量。"""
    account_id = str(account_id)
    try:
        delete_qinglong_env(account_id)
    except Exception:
        pass
    middleware.bucketDel(f"{BUCKET_PREFIX}_token", account_id)
    middleware.bucketDel(f"{BUCKET_PREFIX}_auth", account_id)
    middleware.bucketDel(f"{BUCKET_PREFIX}_acct", account_id)
    middleware.bucketDel(f"{BUCKET_PREFIX}_pwd", account_id)
    middleware.bucketDel(f"{BUCKET_PREFIX}_phone", account_id)
    accounts = [a for a in get_user_accounts() if a != account_id]
    save_user_accounts(accounts)
    sender.reply(f"✅ {mask_account(get_display_name(account_id))} 已删除")


def manage_accounts():
    """显示包含批量操作和授权状态的账号管理菜单。"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 未绑定账号，请先发送“雨云登录”")
        return
    menu = (
        "=======账号列表=======\n"
        "📦 批量操作:\n"
        "[00] 授权全部账号\n"
        "[01] 删除全部账号\n"
        "------------------\n"
        "📋 账号列表:"
    )
    for index, account_id in enumerate(accounts, 1):
        auth_time = get_auth_time(account_id)
        if is_authorized(account_id):
            menu += (
                f"\n[{index}] {mask_account(get_display_name(account_id))}\n"
                "    ✅ 已授权\n"
                f"    ⏰【授权到期】{auth_time}"
            )
        else:
            status = "授权已过期" if auth_time else "未授权"
            menu += f"\n[{index}] {mask_account(get_display_name(account_id))}\n    ❌ {status}"
            if auth_time:
                menu += f"\n    ⏰【授权到期】{auth_time}"
    menu += "\n------------------\n回复数字选择账号\n回复'q'退出"
    sender.reply(menu)
    choice = get_user_input(timeout=60)
    if not choice or choice.lower() == "q":
        sender.reply("✅ 已退出")
        return
    try:
        if choice == "00":
            authorize_accounts(accounts)
        elif choice == "01":
            for account_id in list(accounts):
                delete_account(account_id)
            sender.reply("✅ 已删除全部账号")
        else:
            if not choice.isdigit() or not 1 <= int(choice) <= len(accounts):
                sender.reply("❌ 无效的账号序号")
                return
            show_account_menu(accounts[int(choice) - 1])
    except Exception as exc:
        sender.reply(f"❌ 操作失败：{exc}")


def show_account_menu(account_id):
    """显示单个账号的授权与管理操作。"""
    account_id = str(account_id)
    auth_time = get_auth_time(account_id)
    authorized = is_authorized(account_id)
    auth_status = "✅ 已授权" if authorized else "❌ 未授权"
    auth_info = f"\n    ⏰【授权到期】{auth_time}" if auth_time else ""
    sender.reply(
        "=======账号操作=======\n"
        f"📱【账号】{mask_account(get_display_name(account_id))}\n"
        f"🔐【状态】{auth_status}{auth_info}\n"
        "------------------\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 重新提交青龙\n"
        "[4] 每日签到\n"
        "------------------\n"
        "回复数字选择操作\n"
        '回复"q"退出'
    )
    action = get_user_input(timeout=60)
    if not action or action.lower() == "q":
        sender.reply("✅ 已退出")
        return
    try:
        if action == "1":
            authorize_accounts([account_id])
        elif action == "2":
            sender.reply("确认删除请回复【y】")
            if get_user_input(timeout=60) == "y":
                delete_account(account_id)
        elif action == "3":
            token = get_account_token(account_id)
            if not token:
                sender.reply("❌ 未找到 Token，请先登录")
                return
            submit_to_qinglong(account_id, user_id, token)
            sender.reply("✅ 已重新提交青龙")
        elif action == "4":
            token = get_account_token(account_id)
            if not token:
                sender.reply("❌ 未找到 Token，请先登录")
                return
            client = RainyunClient(token, account_id=account_id)
            acct = middleware.bucketGet(f"{BUCKET_PREFIX}_acct", account_id) or ""
            pwd_enc = middleware.bucketGet(f"{BUCKET_PREFIX}_pwd", account_id) or ""
            if acct:
                client.username = acct
                client.mobile = acct
            if pwd_enc:
                client.password = decrypt_token(pwd_enc)
            sender.reply(client.run_daily_tasks())
        else:
            sender.reply("❌ 无效的操作")
    except Exception as exc:
        sender.reply(f"❌ 操作失败：{exc}")


def parse_stored_accounts(owner_id):
    """读取指定插件用户绑定的账号列表。"""
    raw = middleware.bucketGet(f"{BUCKET_PREFIX}_user", owner_id) or "[]"
    try:
        accounts = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return []
    return [str(p) for p in accounts] if isinstance(accounts, list) else []


def grant_accounts(owner_id, accounts, days):
    """管理员免支付授权账号，并立即更新青龙环境变量。"""
    success_count = 0
    errors = []
    for account_id in accounts:
        account_id = str(account_id)
        token = get_account_token(account_id)
        if not token:
            errors.append(f"{mask_account(get_display_name(account_id))}：未找到 Token，请先登录")
            continue
        auth_time = calculate_auth_time(account_id, days)
        middleware.bucketSet(f"{BUCKET_PREFIX}_auth", account_id, auth_time)
        try:
            submit_to_qinglong(account_id, owner_id, token)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_account(get_display_name(account_id))}：提交青龙失败，{exc}")
    return success_count, errors


def admin_auth_all_users():
    """管理员为全部插件用户的全部账号统一增加授权天数。"""
    sender.reply(
        "=======批量授权=======\n"
        "请输入授权天数(正数增加，负数如-10扣除)\n"
        "------------------\n"
        "回复数字设置天数\n"
        "回复 q 退出"
    )
    days_text = get_user_input(timeout=60)
    if not days_text or days_text.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    try:
        days = int(days_text)
    except (TypeError, ValueError):
        sender.reply("❌ 天数必须是整数")
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
        "=======授权完成=======\n"
        f"👥【用户】{user_count} 个\n"
        f"✅【成功】{success_count} 个账号\n"
        f"❌【失败】{len(errors)} 个账号\n"
        f"📅【授权】{days} 天"
    )
    if errors:
        report += "\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)


def admin_auth_specific_user():
    """管理员为指定插件用户的全部或单个账号授权。"""
    sender.reply(
        "=======指定授权=======\n"
        "请输入用户ID\n"
        "------------------\n"
        "回复 q 退出"
    )
    owner_id = get_user_input(timeout=60)
    if not owner_id or owner_id.lower() == "q":
        sender.reply("✅ 已退出")
        return
    accounts = parse_stored_accounts(owner_id)
    if not accounts:
        sender.reply("❌ 未找到该用户的账号")
        return
    menu = (
        "=======账号列表=======\n"
        "[00] 授权全部账号\n"
        "------------------"
    )
    for index, account_id in enumerate(accounts, 1):
        auth_time = get_auth_time(account_id)
        status = "✅ 已授权" if is_authorized(account_id) else "❌ 未授权"
        menu += f"\n[{index}] {mask_account(get_display_name(account_id))}\n    {status}"
        if auth_time:
            menu += f"\n    ⏰【授权到期】{auth_time}"
    menu += "\n------------------\n回复数字选择账号\n回复 q 退出"
    sender.reply(menu)
    choice = get_user_input(timeout=60)
    if not choice or choice.lower() == "q":
        sender.reply("✅ 已退出")
        return
    if choice == "00":
        selected_accounts = accounts
    elif choice.isdigit() and 1 <= int(choice) <= len(accounts):
        selected_accounts = [accounts[int(choice) - 1]]
    else:
        sender.reply("❌ 无效的账号序号")
        return
    sender.reply("请输入授权天数，例如 30")
    days_text = get_user_input(timeout=60)
    try:
        days = int(days_text)
    except (TypeError, ValueError):
        sender.reply("❌ 天数必须是整数")
        return
    success_count, errors = grant_accounts(owner_id, selected_accounts, days)
    report = f"✅ 已授权 {success_count} 个账号 {days} 天"
    if errors:
        report += f"\n失败：{len(errors)} 个\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)


def update_all_qinglong_envs():
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
        for account_id in accounts:
            account_count += 1
            if not is_authorized(account_id):
                continue
            token = get_account_token(account_id)
            if not token:
                errors.append(f"{mask_account(get_display_name(account_id))}：未找到 Token，请先登录")
                continue
            try:
                submit_to_qinglong(account_id, owner_id, token)
                success_count += 1
            except Exception as exc:
                errors.append(f"{mask_account(get_display_name(account_id))}：{exc}")
    sender.reply(
        "=======更新青龙=======\n"
        f"👥【用户】{user_count} 个\n"
        f"📱【账号】{account_count} 个\n"
        f"✅【成功】{success_count} 个\n"
        f"❌【失败】{len(errors)} 个"
    )


def admin_auth():
    """显示管理员授权功能菜单。"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    sender.reply(
        "=======授权管理=======\n"
        "[1] 一键授权所有用户\n"
        "[2] 指定用户授权\n"
        "[3] 更新青龙环境变量\n"
        "------------------\n"
        "回复数字选择功能\n"
        "回复 q 退出"
    )
    choice = get_user_input(timeout=60)
    if not choice or choice.lower() == "q":
        sender.reply("✅ 已退出")
        return
    if choice == "1":
        admin_auth_all_users()
    elif choice == "2":
        admin_auth_specific_user()
    elif choice == "3":
        update_all_qinglong_envs()
    else:
        sender.reply("❌ 无效的选择")


def cron_check():
    """定时清理过期环境变量，并刷新有效账号的青龙数据。"""
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}_user"):
        raw = middleware.bucketGet(f"{BUCKET_PREFIX}_user", owner_id) or "[]"
        try:
            accounts = json.loads(raw)
        except (TypeError, json.JSONDecodeError):
            continue
        for account_id in accounts if isinstance(accounts, list) else []:
            account_id = str(account_id)
            token = get_account_token(account_id)
            if not token:
                continue
            auth_time = get_auth_time(account_id)
            if not is_authorized(account_id):
                if auth_time:
                    try:
                        delete_qinglong_env(account_id)
                    except Exception:
                        pass
                    notification = (
                        f"=======到期通知=======\n"
                        f"📦【项目】{SCRIPT_NAME}\n"
                        f"📱【账号】{get_display_name(account_id)}\n"
                        f"📢【消息】授权已于 {auth_time} 到期，青龙变量已清理"
                    )
                    for platform in ("qq", "wx", "tg", "qx", "ipad"):
                        try:
                            middleware.push(platform, "", owner_id, "", notification)
                        except Exception:
                            pass
                continue


def clean_expired_accounts():
    """管理员清理授权已过期的账号和青龙环境变量。"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    cleaned_count = 0
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}_user"):
        accounts = parse_stored_accounts(owner_id)
        valid_accounts = []
        for account_id in accounts:
            account_id = str(account_id)
            auth_time = get_auth_time(account_id)
            if auth_time and not is_authorized(account_id):
                try:
                    delete_qinglong_env(account_id)
                except Exception:
                    pass
                middleware.bucketDel(f"{BUCKET_PREFIX}_token", account_id)
                middleware.bucketDel(f"{BUCKET_PREFIX}_auth", account_id)
                middleware.bucketDel(f"{BUCKET_PREFIX}_acct", account_id)
                middleware.bucketDel(f"{BUCKET_PREFIX}_pwd", account_id)
                middleware.bucketDel(f"{BUCKET_PREFIX}_phone", account_id)
                cleaned_count += 1
            else:
                valid_accounts.append(account_id)
        if valid_accounts:
            middleware.bucketSet(
                f"{BUCKET_PREFIX}_user",
                owner_id,
                json.dumps(valid_accounts, ensure_ascii=False),
            )
        else:
            middleware.bucketDel(f"{BUCKET_PREFIX}_user", owner_id)
    sender.reply(f"✅ 已清理 {cleaned_count} 个过期账号")


def notify_authorized_users():
    """管理员向所有授权用户发送通知。"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    content = ""
    match = re.search(r"^\s*((?:雨云)(?:广播|通知))\s*(.*)$", str(sender.getMessage() or ""), re.S)
    if match:
        content = match.group(2).strip()
    if not content:
        sender.reply("❌ 请输入通知内容，例如：雨云通知 系统维护中")
        return
    sender.reply("⏳ 正在扫描授权用户并发送通知...")
    success_count = 0
    fail_count = 0
    today = str(datetime.now().date())
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}_user"):
        accounts = parse_stored_accounts(owner_id)
        has_auth = False
        for acc in accounts:
            auth_time = get_auth_time(str(acc))
            if auth_time and auth_time >= today:
                has_auth = True
                break
        if has_auth:
            try:
                middleware.push("", "", str(owner_id), "雨云管理员通知", f"📢 【雨云管理员通知】\n\n{content}")
                success_count += 1
                time.sleep(0.3)
            except Exception as e:
                fail_count += 1
                logger.warning(f"通知发送失败 {owner_id}: {e}")
    sender.reply(f"✅【通知完成】\n⚠️【发送失败】{fail_count} 人\n📢【已送达】{success_count} 人")


def tutorial():
    """显示插件使用教程。"""
    sender.reply(
        f"注册链接：{get_invite_url()}\n"
        "=======雨云教程=======\n"
        "1. 注册下载：点击上方链接注册雨云\n"
        '2. 账密登录：发送"雨云登录"，输入 账号#密码 获取 Token\n'
        '3. 授权代挂：在"雨云管理"中选择账号授权，走清蕴支付收银台\n'
        "4. 授权费用：按插件配置的月价计费\n"
        "5. 自动签到：管理菜单支持每日签到（需配置 2captcha 滑块 Token）\n"
    )
    sender.reply(
        "=======可用指令=======\n"
        "雨云教程：查看注册和使用教程\n"
        "雨云登录：账密登录并绑定 Token\n"
        "雨云查询：查询积分、邮箱、IP、地区\n"
        "雨云管理：授权、同步或删除账号\n"
        "--------------------\n"
        "管理员指令：雨云授权、雨云清理、雨云通知\n"
    )


def main():
    """根据消息内容分发插件指令。"""
    message = str(sender.getMessage() or "").strip()
    if re.match(r"^(雨云)(通知|广播)\s*", message):
        notify_authorized_users()
    elif "登录" in message or "登陆" in message or "上车" in message:
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
        imtype = str(sender.getImtype() or "").lower()
        msg = str(sender.getMessage() or "").strip().lower()
        if imtype == "fake" and not msg:
            cron_check()
        elif imtype == "cron" or msg in ["", "cron", "定时任务"]:
            cron_check()
        else:
            main()
    except Exception as exc:
        sender.reply(f"❌ 运行出错：{exc}")
