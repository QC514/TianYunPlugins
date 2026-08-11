# [author: qingyun]
# [title: 茄皇]
# [language: python]
# [class: 工具类]
# [service: 68025408]
# [disable: false]
# [admin: false]
# [rule: ^茄皇(.*)|(.*)茄皇$]
# [cron: 25 10 * * *]
# [priority: 99999999]
# [platform: all]
# [open_source: false]
# [version: 1.1.0]
# [public: false]
# [price: 0]
# [description: 茄皇五期账号管理插件。账号格式为 wid，支持批量登录验证、账号查询、统一收银台授权、账号管理、提交青龙和立即执行。执行保留签到、浏览、分享、好友能量收取、能量使用和结果通知全部功能。<br>指令：茄皇（登录|查询|执行|管理|教程）。<br>青龙环境变量固定为 QH，wid、所属用户和授权时间写入备注。<br>1.1.0更新：授权支付接入清蕴统一收银台（参考饿了么/幸运星/太平洋）。]

# [param: {"required":true,"key":"qingyun.qh.ql_config","bool":false,"placeholder":"http://地址:端口丨ClientID丨ClientSecret","name":"对接青龙","desc":"青龙地址丨ClientID丨ClientSecret"}]
# [param: {"required":false,"key":"qingyun.qh.price","bool":false,"placeholder":"1","name":"授权价格","desc":"单账号授权30天的价格，单位为元"}]
# [param: {"required":false,"key":"qingyun.qh.is_proxy","bool":true,"placeholder":"","name":"启用代理","desc":"是否为茄皇接口启用代理"}]
# [param: {"required":false,"key":"qingyun.qh.proxy_pool","bool":false,"placeholder":"http://代理池接口","name":"代理池地址","desc":"返回单个代理地址的接口"}]
# [param: {"required":false,"key":"qingyun.qh.tutorial_image","bool":false,"placeholder":"http://地址/教程图片.jpg","name":"教程图片","desc":"茄皇教程中发送的活动入口或操作图片"}]

"""统一快乐星球茄皇五期 AutMan 账号管理与任务插件。"""

import base64
import json
import os
import random
import re
import time
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation, ROUND_UP
from typing import Any

import middleware
import qingyun_payment
import requests
import urllib3

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    CRYPTO_BACKEND = "cryptography"
except ImportError:
    try:
        from Crypto.Cipher import AES, PKCS1_OAEP
        from Crypto.Hash import SHA256
        from Crypto.PublicKey import RSA

        CRYPTO_BACKEND = "pycryptodome"
    except ImportError:
        CRYPTO_BACKEND = None


SCRIPT_NAME = "茄皇"
FULL_SCRIPT_NAME = "统一茄皇五期"
BUCKET_PREFIX = "qingyun.qh"
QL_ENV_NAME = "QH"
BASE_URL = "https://farmgames.ioutu.cn"
MAX_RETRIES = 3
SUPPORTED_TASK_TYPES = {"SIGN", "BROWSE", "SHARE"}
FRIEND_TASK_TYPE = "FRIEND_STEAL_ENERGY"
FRIEND_STATUS_CLAIMABLE = "0"
PUBLIC_KEY = (
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA70sK419vy3MabW3lEGlk"
    "7Zh1u78OdnVlioVazp5Y46eBh+/TDqo/wZ9VrQ/4MmAtoP0vJ2vmwP5gqO3WPoj"
    "b07WddXfF1eU+5M+Rj3s0eSRrvZvBcGZ3qK0dOgZJScK66IDQazt/c4xqhDcsI"
    "tIyNRahUqB/IKc6E80GZJvMvFtZVSCseAXC0mAJXhi1AdUOlP+3Pv0fiUVejTJp"
    "1j7LBNWJ7Z5/8mRcclQH0vmxsdYsaV3qZiJ2d/CfNoKcwmI2IWmeZy8NP5U8Hn"
    "0AsxPEwjdHoEqG/iy/SoA46TZL+RLtWqUSHXpaKR/VFN0rbl25SE91X8FTfLqyD"
    "8LfGMCwRQIDAQAB"
)
USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 26_5_2 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.75(0x18004b42) NetType/WIFI Language/zh_CN "
    "miniProgram/wx532ecb3bdaaf92f9"
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sender_id = middleware.getSenderID()
sender = middleware.Sender(sender_id)
user_id = sender.getUserID()


class PluginError(RuntimeError):
    """插件运行过程中可直接展示给用户的错误。"""


def mask_wid(wid: str) -> str:
    """隐藏 wid 中间内容。"""
    if len(wid) <= 7:
        return wid
    return wid[:3] + "****" + wid[-4:]


def parse_accounts(text: str) -> list[str]:
    """解析换行或 & 分隔的 wid。"""
    accounts = []
    for value in re.split(r"[&\r\n]+", text or ""):
        wid = value.strip()
        if not wid:
            continue
        if "#" in wid:
            raise PluginError(f"账号格式错误：{wid}，正确格式仅为 wid")
        accounts.append(wid)
    return accounts


def get_user_accounts() -> list[str]:
    raw = middleware.bucketGet(f"{BUCKET_PREFIX}.user", user_id) or "[]"
    try:
        result = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        result = []
    return [str(value) for value in result] if isinstance(result, list) else []


def save_user_accounts(accounts: list[str]) -> None:
    middleware.bucketSet(
        f"{BUCKET_PREFIX}.user",
        user_id,
        json.dumps(accounts, ensure_ascii=False),
    )


def get_proxy() -> dict[str, str] | None:
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
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            kwargs.setdefault("timeout", 30)
            kwargs.setdefault("verify", False)
            if "proxies" not in kwargs:
                kwargs["proxies"] = get_proxy()
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(1)
    raise PluginError(f"请求失败：{last_error}")


def encrypt_payload(payload: dict[str, Any]) -> dict[str, str]:
    """按官方 H5 规则执行 RSA-OAEP-SHA256 + AES-256-GCM 加密。"""
    if CRYPTO_BACKEND is None:
        raise PluginError("缺少加密依赖，请安装 cryptography")
    plaintext = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
    aes_key = os.urandom(32)
    iv = os.urandom(12)
    public_key_der = base64.b64decode(PUBLIC_KEY)
    if CRYPTO_BACKEND == "cryptography":
        public_key = serialization.load_der_public_key(public_key_der)
        encrypted_data = AESGCM(aes_key).encrypt(iv, plaintext, None)
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    else:
        cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        encrypted_data = ciphertext + tag
        public_key = RSA.import_key(public_key_der)
        encrypted_key = PKCS1_OAEP.new(public_key, hashAlgo=SHA256).encrypt(aes_key)
    return {
        "data": base64.b64encode(encrypted_data).decode(),
        "key": base64.b64encode(encrypted_key).decode(),
        "iv": base64.b64encode(iv).decode(),
    }


class TomatoClient:
    """茄皇五期接口客户端。"""

    def __init__(self, wid: str):
        self.wid = wid
        self.tomato_user_id: Any = None
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Content-Type": "application/json",
                "Origin": BASE_URL,
                "Referer": f"{BASE_URL}/?wid={wid}",
            }
        )
        proxies = get_proxy()
        if proxies:
            self.session.proxies.update(proxies)

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        encrypted: bool = True,
        retry: int = 2,
    ) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        for attempt in range(retry + 1):
            kwargs: dict[str, Any] = {"timeout": 20, "verify": False}
            if payload:
                kwargs["json"] = encrypt_payload(payload) if encrypted else payload
                if encrypted:
                    kwargs["headers"] = {"X-Request-Encrypted": "true"}
            try:
                response = self.session.request(method, url, **kwargs)
                if response.status_code == 429 and attempt < retry:
                    wait = response.headers.get("Retry-After", "2")
                    time.sleep(max(1.0, float(wait)) + attempt)
                    continue
                response.raise_for_status()
                result = response.json()
            except (requests.RequestException, ValueError) as exc:
                if attempt < retry:
                    time.sleep(1.5 + attempt)
                    continue
                raise PluginError(f"接口请求失败：{exc}") from exc
            msg = str(result.get("msg", ""))
            if result.get("code") == 200:
                return result
            if attempt < retry and ("频繁" in msg or "稍后" in msg):
                time.sleep(2.5 + attempt * 1.5)
                continue
            raise PluginError(msg or f"接口返回 code={result.get('code')}")
        raise PluginError("请求重试后仍未成功")

    def login(self) -> dict[str, Any]:
        result = self.request(
            "POST",
            "/api/web/open/tomato/login",
            {"shareTomatoUserId": None, "wid": self.wid, "queryCardStatus": True},
        )
        data = result.get("data") or {}
        token = data.get("token")
        if not token:
            raise PluginError("登录响应中没有 token")
        self.session.headers["Authorization"] = token
        self.tomato_user_id = data.get("tomatoUserId")
        return data

    def home(self) -> dict[str, Any]:
        return self.request("GET", "/api/web/member/tomato/home").get("data") or {}

    def tasks(self) -> list[dict[str, Any]]:
        return self.request("GET", "/api/web/member/tomato/tasks").get("data") or []

    def complete_task(self, task: dict[str, Any]) -> dict[str, Any]:
        task_type = task.get("taskType")
        payload = {"taskType": task_type}
        if task_type != "SHARE":
            payload["browseTarget"] = task.get("browseTarget") or ""
        elif self.tomato_user_id:
            try:
                self.request(
                    "POST",
                    "/api/web/member/tomato/miniprogram/qrcode/create",
                    {
                        "page": "packages/wm-cloud-qiehuang/home/index",
                        "scene": str(self.tomato_user_id),
                    },
                )
            except Exception:
                pass
        return self.request(
            "POST", "/api/web/member/tomato/tasks/complete", payload
        ).get("data") or {}

    def friends(self, page_size: int = 20) -> list[dict[str, Any]]:
        friends = []
        page_num = 1
        while True:
            result = self.request(
                "GET",
                f"/api/web/member/tomato/friends?pageNum={page_num}&pageSize={page_size}",
            )
            rows = result.get("rows") or []
            friends.extend(rows)
            total = int(result.get("total") or 0)
            if not rows or (total and len(friends) >= total) or len(rows) < page_size:
                break
            page_num += 1
        return friends

    def friend_home(self, friend_user_id: Any) -> dict[str, Any]:
        return self.request(
            "GET", f"/api/web/member/tomato/friends/{friend_user_id}/home"
        ).get("data") or {}

    def steal_friend_energy(self, friend_user_id: Any) -> Any:
        return self.request(
            "POST",
            "/api/web/member/tomato/friends/steal",
            {"friendTomatoUserId": friend_user_id},
        ).get("data")

    def use_energy(self) -> dict[str, Any]:
        return self.request(
            "POST", "/api/web/member/tomato/energy/use", encrypted=False
        ).get("data") or {}


def login_account(wid: str) -> tuple[TomatoClient, dict[str, Any]]:
    client = TomatoClient(wid)
    return client, client.login()


def home_line(data: dict[str, Any], prefix: str = "当前状态") -> str:
    return (
        f"{prefix}：能量 {data.get('energyBalance', 0)}，"
        f"番茄 {data.get('tomatoBalance', 0)}，"
        f"{data.get('stageName', '未知阶段')} "
        f"{data.get('currentExp', 0)}/{data.get('stageRequiredExp', 0)}"
    )


def query_account_details(wid: str) -> dict[str, Any]:
    client, login_data = login_account(wid)
    home = client.home()
    tasks = client.tasks()
    completed = sum(str(task.get("completed")) == "1" for task in tasks)
    return {
        "wid": wid,
        "昵称": login_data.get("nickName") or "未设置昵称",
        "能量": home.get("energyBalance", 0),
        "番茄": home.get("tomatoBalance", 0),
        "阶段": home.get("stageName", "未知阶段"),
        "经验": f"{home.get('currentExp', 0)}/{home.get('stageRequiredExp', 0)}",
        "任务": f"{completed}/{len(tasks)}",
    }


def run_account(wid: str) -> list[str]:
    """执行原茄皇脚本的全部任务。"""
    logs = [f"账号：{mask_wid(wid)}"]
    client, login_data = login_account(wid)
    logs.append(f"登录成功：{login_data.get('nickName') or '未设置昵称'}")
    home = client.home()
    logs.append(home_line(home))
    completed = 0
    skipped = 0
    friend_task = None
    for task in client.tasks():
        name = task.get("taskName") or task.get("taskCode") or "未知任务"
        task_type = task.get("taskType")
        if task_type == FRIEND_TASK_TYPE:
            friend_task = task
            if str(task.get("completed")) == "1":
                logs.append(f"任务已完成：{name}")
            continue
        if str(task.get("completed")) == "1":
            logs.append(f"任务已完成：{name}")
            continue
        if task_type not in SUPPORTED_TASK_TYPES:
            skipped += 1
            logs.append(f"跳过任务：{name}（需在小程序内操作）")
            continue
        try:
            result = client.complete_task(task)
            reward = result.get("rewardText") or task.get("rewardText") or "已领取"
            logs.append(f"任务完成：{name}，{reward}")
            completed += 1
        except Exception as exc:
            logs.append(f"任务失败：{name}，{exc}")
        time.sleep(random.uniform(2.5, 3.5))

    try:
        claimable = [
            friend
            for friend in client.friends()
            if str(friend.get("friendStatus")) == FRIEND_STATUS_CLAIMABLE
            and friend.get("friendTomatoUserId")
        ]
        stolen_count = stolen_energy = failed_count = 0
        for friend in claimable:
            friend_user_id = friend["friendTomatoUserId"]
            try:
                friend_home = client.friend_home(friend_user_id)
                amount = int(friend_home.get("stealAmount") or 0)
                if str(friend_home.get("canSteal")) != "1" or amount <= 0:
                    continue
                client.steal_friend_energy(friend_user_id)
                stolen_count += 1
                stolen_energy += amount
            except Exception:
                failed_count += 1
            time.sleep(random.uniform(1.5, 2.5))
        if stolen_count:
            detail = f"好友能量：成功收取 {stolen_count} 位，共 {stolen_energy} 能量"
            if failed_count:
                detail += f"，失败 {failed_count} 位"
            logs.append(detail)
            if friend_task and str(friend_task.get("completed")) != "1":
                completed += 1
        elif failed_count:
            logs.append(f"好友能量：收取失败 {failed_count} 位")
        else:
            logs.append("好友能量：暂无可收取能量")
    except Exception as exc:
        logs.append(f"好友能量失败：{exc}")

    home = client.home()
    logs.append(home_line(home, "任务后状态"))
    energy = int(home.get("energyBalance") or 0)
    if energy > 0:
        before_tomato = int(home.get("tomatoBalance") or 0)
        try:
            grown = client.use_energy()
            after_tomato = int(grown.get("tomatoBalance") or 0)
            gained = int(grown.get("gainedTomatoAmount") or 0)
            if not gained:
                gained = max(0, after_tomato - before_tomato)
            logs.append(
                f"使用能量：消耗 {grown.get('usedEnergyAmount', energy)}，"
                f"成长到 {grown.get('stageName', '未知阶段')} "
                f"{grown.get('currentExp', 0)}/{grown.get('stageRequiredExp', 0)}，"
                f"获得番茄 {gained}"
            )
            home = grown
        except Exception as exc:
            logs.append(f"使用能量失败：{exc}")
    else:
        logs.append("使用能量：当前没有可用能量")
    logs.append(home_line(home, "最终状态"))
    logs.append(f"本次完成任务 {completed} 个，跳过 {skipped} 个")
    return logs


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
    url, client_id, client_secret = parse_qinglong_config()
    token = get_qinglong_token(url, client_id, client_secret)
    return url, {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_qinglong_envs(url: str, headers: dict[str, str]) -> list[dict[str, Any]]:
    response = send_request("GET", f"{url}/open/envs", headers=headers)
    data = response.json().get("data", [])
    return data if isinstance(data, list) else []


def get_env_id(env: dict[str, Any]) -> Any:
    return env.get("id", env.get("_id"))


def submit_to_qinglong(wid: str, owner_id: str) -> bool:
    """新增或更新单个 wid 对应的 QH 环境变量。"""
    url, headers = qinglong_context()
    envs = get_qinglong_envs(url, headers)
    target_env = None
    for env in envs:
        if env.get("name") != QL_ENV_NAME:
            continue
        remarks = str(env.get("remarks", ""))
        if f"账号:{wid}丨" in remarks or str(env.get("value", "")) == wid:
            target_env = env
            break
    auth_time = middleware.bucketGet(f"{BUCKET_PREFIX}.auth", wid) or "未授权"
    remarks = f"{FULL_SCRIPT_NAME}账号:{wid}丨用户:{owner_id}丨授权时间:{auth_time}"
    data: dict[str, Any] = {"name": QL_ENV_NAME, "value": wid, "remarks": remarks}
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
            middleware.bucketSet(f"{BUCKET_PREFIX}.env_id", wid, str(env_id))
    return True


def delete_qinglong_env(wid: str) -> bool:
    """按 wid 删除对应青龙环境变量。"""
    url, headers = qinglong_context()
    ids_to_delete = []
    for env in get_qinglong_envs(url, headers):
        if env.get("name") != QL_ENV_NAME:
            continue
        remarks = str(env.get("remarks", ""))
        if f"账号:{wid}丨" in remarks or str(env.get("value", "")) == wid:
            env_id = get_env_id(env)
            if env_id is not None:
                ids_to_delete.append(env_id)
    if ids_to_delete:
        send_request("DELETE", f"{url}/open/envs", headers=headers, json=ids_to_delete)
    middleware.bucketDel(f"{BUCKET_PREFIX}.env_id", wid)
    return True


def get_auth_time(wid: str) -> str:
    return str(middleware.bucketGet(f"{BUCKET_PREFIX}.auth", wid) or "")


def is_authorized(wid: str) -> bool:
    auth_time = get_auth_time(wid)
    return bool(auth_time and auth_time > str(datetime.now().date()))


def calculate_auth_time(wid: str, days: int) -> str:
    today = datetime.now().date()
    auth_time = get_auth_time(wid)
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
    """读取单账号 30 天授权价格。"""
    try:
        price = Decimal(str(middleware.bucketGet(BUCKET_PREFIX, "price") or "1"))
        if price < 0:
            raise ValueError("授权价格不能为负数")
    except (InvalidOperation, ValueError) as exc:
        raise PluginError(f"授权价格配置错误：{exc}") from exc
    return price


def process_payment(amount: Decimal, days: int, account_count: int = 1) -> bool:
    """接入清蕴统一收银台完成授权支付。"""
    try:
        pay_amount = float(Decimal(str(amount)).quantize(Decimal("0.01"), rounding=ROUND_UP))
    except (InvalidOperation, ValueError, TypeError):
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
    except (TypeError, ValueError):
        paid_money = pay_amount

    # 宽松校验：实付不低于应付（账单偏移等场景由支付插件内部处理）
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
    """为一个或多个账号付款、授权并提交青龙。"""
    if not accounts:
        return
    try:
        price = get_payment_config()
    except PluginError as exc:
        sender.reply(f"❌ {exc}")
        return

    if price == 0:
        sender.reply("请输入授权天数，例如 30；回复 q 退出")
    else:
        sender.reply(f"请输入授权天数（{price}元/30天），例如 30；回复 q 退出")
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

    amount = (price * Decimal(days) / Decimal(30) * len(accounts)).quantize(
        Decimal("0.01"), rounding=ROUND_UP
    )
    if amount > 0 and not process_payment(amount, days, account_count=len(accounts)):
        return

    payment_text = (
        f"支付 {amount} 元，授权 {days} 天" if amount > 0 else f"免费授权 {days} 天"
    )

    success_count = 0
    errors = []
    for wid in accounts:
        stored_wid = middleware.bucketGet(f"{BUCKET_PREFIX}.token", wid)
        if not stored_wid:
            errors.append(f"{mask_wid(wid)}：未找到账号")
            continue
        auth_time = calculate_auth_time(wid, days)
        middleware.bucketSet(f"{BUCKET_PREFIX}.auth", wid, auth_time)
        try:
            submit_to_qinglong(str(stored_wid), user_id)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_wid(wid)}：提交青龙失败，{exc}")
    report = (
        "=====授权完成=====\n"
        f"{payment_text}\n成功：{success_count} 个账号\n失败：{len(errors)} 个账号"
    )
    if errors:
        report += "\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)


def show_ck(wid: str) -> None:
    stored_wid = middleware.bucketGet(f"{BUCKET_PREFIX}.token", wid)
    if stored_wid:
        sender.reply(
            f"====={FULL_SCRIPT_NAME}账号ck=====\n"
            f"账号：{mask_wid(wid)}\nCK：{stored_wid}\n===================="
        )
    else:
        sender.reply(f"❌ {mask_wid(wid)} 未绑定ck")


def batch_login() -> None:
    """交互式接收 wid，验证后保存，已授权账号同步青龙。"""
    sender.reply(
        "=====茄皇登录=====\n请输入 wid\n"
        "支持多账号，每行一个，也可使用 & 分隔\n回复 q 退出"
    )
    user_input = sender.input(120000, 1, False)
    if not user_input:
        sender.reply("❌ 输入超时")
        return
    if user_input.strip().lower() == "q":
        sender.reply("✅ 已取消登录")
        return
    try:
        pending_accounts = parse_accounts(user_input)
    except PluginError as exc:
        sender.reply(f"❌ {exc}")
        return
    if not pending_accounts:
        sender.reply("❌ 未检测到有效账号")
        return
    current_accounts = get_user_accounts()
    success_count = added_count = updated_count = 0
    errors = []
    for index, wid in enumerate(pending_accounts, 1):
        try:
            login_account(wid)
            middleware.bucketSet(f"{BUCKET_PREFIX}.token", wid, wid)
            if wid in current_accounts:
                updated_count += 1
                status = "更新成功"
            else:
                current_accounts.append(wid)
                added_count += 1
                status = "登录成功"
            save_user_accounts(current_accounts)
            if is_authorized(wid):
                submit_to_qinglong(wid, user_id)
            else:
                status += "，账号未授权，暂未提交青龙"
            success_count += 1
            sender.reply(f"[{index}/{len(pending_accounts)}] ✅ {mask_wid(wid)} {status}")
        except Exception as exc:
            errors.append(f"{mask_wid(wid)}：{exc}")
            sender.reply(f"[{index}/{len(pending_accounts)}] ❌ {mask_wid(wid)} 处理失败")
        if index < len(pending_accounts):
            time.sleep(1)
    report = (
        "=====登录完成=====\n"
        f"成功：{success_count} 个\n新增：{added_count} 个\n"
        f"更新：{updated_count} 个\n失败：{len(errors)} 个"
    )
    if errors:
        report += "\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)


def select_accounts(title: str) -> list[str]:
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 未绑定账号，请先发送“茄皇登录”")
        return []
    if len(accounts) == 1:
        return accounts
    menu = f"====={title}=====\n[0] 全部账号\n------------------\n"
    for index, wid in enumerate(accounts, 1):
        menu += f"[{index}] {mask_wid(wid)}\n"
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
    """查询一个或全部已绑定茄皇账号。"""
    for wid in select_accounts("茄皇查询"):
        auth_time = get_auth_time(wid)
        if not auth_time:
            sender.reply(f"❌ {mask_wid(wid)} 账号未授权")
            continue
        if not is_authorized(wid):
            sender.reply(f"❌ {mask_wid(wid)} 授权已过期：{auth_time}")
            continue
        stored_wid = middleware.bucketGet(f"{BUCKET_PREFIX}.token", wid)
        if not stored_wid:
            sender.reply(f"❌ {mask_wid(wid)} 未找到账号")
            continue
        try:
            details = query_account_details(str(stored_wid))
            sender.reply(
                f"====={FULL_SCRIPT_NAME}详情=====\n"
                f"账号：{mask_wid(details['wid'])}\n"
                f"昵称：{details['昵称']}\n"
                f"能量：{details['能量']}\n"
                f"番茄：{details['番茄']}\n"
                f"阶段：{details['阶段']}\n"
                f"经验：{details['经验']}\n"
                f"任务：{details['任务']}\n"
                f"授权到期：{auth_time}\n=================="
            )
        except Exception as exc:
            sender.reply(f"❌ {mask_wid(wid)} 查询失败：{exc}")


def execute() -> None:
    """手动执行一个或全部已授权账号的完整任务。"""
    for wid in select_accounts("茄皇执行"):
        auth_time = get_auth_time(wid)
        if not is_authorized(wid):
            status = f"授权已过期：{auth_time}" if auth_time else "账号未授权"
            sender.reply(f"❌ {mask_wid(wid)} {status}")
            continue
        try:
            logs = run_account(wid)
            sender.reply(f"====={FULL_SCRIPT_NAME}=====\n" + "\n".join(logs))
        except Exception as exc:
            sender.reply(f"❌ {mask_wid(wid)} 执行失败：{exc}")


def delete_account(wid: str) -> None:
    """删除插件账号并同步删除青龙变量。"""
    delete_qinglong_env(wid)
    middleware.bucketDel(f"{BUCKET_PREFIX}.token", wid)
    middleware.bucketDel(f"{BUCKET_PREFIX}.auth", wid)
    middleware.bucketDel(f"{BUCKET_PREFIX}.env_id", wid)
    save_user_accounts([account for account in get_user_accounts() if account != wid])
    sender.reply(f"✅ {mask_wid(wid)} 已删除")


def manage_accounts() -> None:
    """显示批量操作和授权状态。"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 未绑定账号，请先发送“茄皇登录”")
        return
    menu = (
        "=====账号列表=====\n批量操作:\n"
        "[00] 授权全部账号\n[01] 删除全部账号\n"
        "[02] 查看全部账号ck\n[03] 执行全部账号\n"
        "------------------\n账号列表:"
    )
    for index, wid in enumerate(accounts, 1):
        auth_time = get_auth_time(wid)
        if is_authorized(wid):
            menu += f"\n[{index}] {mask_wid(wid)}\n    ✅ 已授权\n    授权到期: {auth_time}"
        else:
            status = "授权已过期" if auth_time else "未授权"
            menu += f"\n[{index}] {mask_wid(wid)}\n    ❌ {status}"
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
            for wid in list(accounts):
                delete_account(wid)
            sender.reply("✅ 已删除全部账号")
        elif choice == "02":
            for wid in accounts:
                show_ck(wid)
        elif choice == "03":
            for wid in accounts:
                if is_authorized(wid):
                    sender.reply(f"====={mask_wid(wid)}=====\n" + "\n".join(run_account(wid)))
        else:
            if not choice.isdigit() or not 1 <= int(choice) <= len(accounts):
                sender.reply("❌ 无效的账号序号")
                return
            show_account_menu(accounts[int(choice) - 1])
    except Exception as exc:
        sender.reply(f"❌ 操作失败：{exc}")


def show_account_menu(wid: str) -> None:
    auth_time = get_auth_time(wid)
    auth_status = "✅ 已授权" if is_authorized(wid) else "❌ 未授权"
    auth_info = f"\n    到期: {auth_time}" if auth_time else ""
    sender.reply(
        "=====账号操作=====\n"
        f"账号: {mask_wid(wid)}\n状态: {auth_status}{auth_info}\n"
        "------------------\n[1] 授权账号\n[2] 删除账号\n"
        "[3] 查看账号ck\n[4] 重新提交青龙\n[5] 立即执行\n"
        "------------------\n回复数字选择操作\n回复\"q\"退出"
    )
    action = sender.input(60000, 1, False)
    if not action or action.lower() == "q":
        return
    try:
        if action == "1":
            authorize_accounts([wid])
        elif action == "2":
            delete_account(wid)
        elif action == "3":
            show_ck(wid)
        elif action == "4":
            if not is_authorized(wid):
                sender.reply("❌ 账号未授权或授权已过期")
                return
            login_account(wid)
            submit_to_qinglong(wid, user_id)
            sender.reply("✅ 已重新提交青龙")
        elif action == "5":
            if not is_authorized(wid):
                sender.reply("❌ 账号未授权或授权已过期")
                return
            sender.reply(f"====={FULL_SCRIPT_NAME}=====\n" + "\n".join(run_account(wid)))
        else:
            sender.reply("❌ 无效的操作")
    except Exception as exc:
        sender.reply(f"❌ 操作失败：{exc}")


def push_notification(owner_id: str, message: str) -> None:
    """向芳华模板支持的所有平台推送通知。"""
    for platform in ("qq", "wx", "tg", "qx", "ipad"):
        try:
            middleware.push(platform, "", owner_id, "", message)
        except Exception:
            pass


def cron_check() -> None:
    """清理过期变量，执行有效账号任务并刷新青龙数据。"""
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}.user"):
        accounts = parse_stored_accounts(owner_id)
        for wid in accounts:
            stored_wid = middleware.bucketGet(f"{BUCKET_PREFIX}.token", wid)
            if not stored_wid:
                continue
            auth_time = get_auth_time(wid)
            if not is_authorized(wid):
                if auth_time:
                    try:
                        delete_qinglong_env(wid)
                    except Exception:
                        pass
                    push_notification(
                        owner_id,
                        f"====={FULL_SCRIPT_NAME}账号通知=====\n"
                        f"账号：{mask_wid(wid)}\n"
                        f"消息：授权已于 {auth_time} 到期，青龙变量已清理",
                    )
                continue


def grant_accounts(owner_id: str, accounts: list[str], days: int) -> tuple[int, list[str]]:
    success_count = 0
    errors = []
    for wid in accounts:
        stored_wid = middleware.bucketGet(f"{BUCKET_PREFIX}.token", wid)
        if not stored_wid:
            errors.append(f"{mask_wid(wid)}：未找到账号")
            continue
        try:
            login_account(str(stored_wid))
            auth_time = calculate_auth_time(wid, days)
            middleware.bucketSet(f"{BUCKET_PREFIX}.auth", wid, auth_time)
            submit_to_qinglong(str(stored_wid), owner_id)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_wid(wid)}：授权失败，{exc}")
    return success_count, errors


def set_accounts_auth_date(
    owner_id: str,
    accounts: list[str],
    auth_time: str,
) -> tuple[int, list[str]]:
    try:
        datetime.strptime(auth_time, "%Y-%m-%d")
    except ValueError as exc:
        raise PluginError("授权日期格式应为 YYYY-MM-DD") from exc
    success_count = 0
    errors = []
    for wid in accounts:
        stored_wid = middleware.bucketGet(f"{BUCKET_PREFIX}.token", wid)
        if not stored_wid:
            errors.append(f"{mask_wid(wid)}：未找到账号")
            continue
        middleware.bucketSet(f"{BUCKET_PREFIX}.auth", wid, auth_time)
        try:
            submit_to_qinglong(str(stored_wid), owner_id)
            success_count += 1
        except Exception as exc:
            errors.append(f"{mask_wid(wid)}：同步失败，{exc}")
    return success_count, errors


def parse_stored_accounts(owner_id: str) -> list[str]:
    raw = middleware.bucketGet(f"{BUCKET_PREFIX}.user", owner_id) or "[]"
    try:
        accounts = json.loads(raw)
    except (TypeError, json.JSONDecodeError):
        return []
    return [str(wid) for wid in accounts] if isinstance(accounts, list) else []


def admin_auth_all_users() -> None:
    sender.reply(
        "=====批量授权=====\n请输入授权天数\n"
        "------------------\n回复数字设置天数\n回复 q 退出"
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
    success_count = user_count = 0
    errors = []
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}.user"):
        accounts = parse_stored_accounts(owner_id)
        if not accounts:
            continue
        user_count += 1
        current_success, current_errors = grant_accounts(owner_id, accounts, days)
        success_count += current_success
        errors.extend(current_errors)
    report = (
        "=====授权完成=====\n"
        f"用户：{user_count} 个\n成功：{success_count} 个账号\n"
        f"失败：{len(errors)} 个账号\n授权：{days} 天"
    )
    if errors:
        report += "\n------------------\n" + "\n".join(errors[:5])
    sender.reply(report)


def admin_auth_specific_user() -> None:
    sender.reply("=====指定授权=====\n请输入用户ID\n------------------\n回复 q 退出")
    owner_id = sender.input(60000, 1, False)
    if not owner_id or owner_id.lower() == "q":
        return
    accounts = parse_stored_accounts(owner_id)
    if not accounts:
        sender.reply("❌ 未找到该用户的账号")
        return
    menu = (
        "=====账号列表=====\n[00] 授权全部账号\n"
        "[01] 修改全部账号授权日期\n------------------"
    )
    for index, wid in enumerate(accounts, 1):
        auth_time = get_auth_time(wid)
        status = "✅ 已授权" if is_authorized(wid) else "❌ 未授权"
        menu += f"\n[{index}] {mask_wid(wid)}\n    {status}"
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
    user_count = account_count = success_count = 0
    errors = []
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}.user"):
        accounts = parse_stored_accounts(owner_id)
        if not accounts:
            continue
        user_count += 1
        for wid in accounts:
            account_count += 1
            if not is_authorized(wid):
                continue
            stored_wid = middleware.bucketGet(f"{BUCKET_PREFIX}.token", wid)
            if not stored_wid:
                errors.append(f"{mask_wid(wid)}：未找到账号")
                continue
            try:
                submit_to_qinglong(str(stored_wid), owner_id)
                success_count += 1
            except Exception as exc:
                errors.append(f"{mask_wid(wid)}：{exc}")
    sender.reply(
        "=====更新青龙完成=====\n"
        f"用户：{user_count} 个\n账号：{account_count} 个\n"
        f"成功：{success_count} 个\n失败：{len(errors)} 个"
    )


def admin_auth() -> None:
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    sender.reply(
        "=====授权管理=====\n[1] 一键授权所有用户\n"
        "[2] 指定用户授权\n[3] 更新青龙环境变量\n"
        "------------------\n回复数字选择功能\n回复 q 退出"
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
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    cleaned_count = 0
    for owner_id in middleware.bucketAllKeys(f"{BUCKET_PREFIX}.user"):
        accounts = parse_stored_accounts(owner_id)
        valid_accounts = []
        for wid in accounts:
            auth_time = get_auth_time(wid)
            if auth_time and not is_authorized(wid):
                try:
                    delete_qinglong_env(wid)
                except Exception:
                    pass
                middleware.bucketDel(f"{BUCKET_PREFIX}.token", wid)
                middleware.bucketDel(f"{BUCKET_PREFIX}.auth", wid)
                middleware.bucketDel(f"{BUCKET_PREFIX}.env_id", wid)
                cleaned_count += 1
            else:
                valid_accounts.append(wid)
        if valid_accounts:
            middleware.bucketSet(
                f"{BUCKET_PREFIX}.user",
                owner_id,
                json.dumps(valid_accounts, ensure_ascii=False),
            )
        else:
            middleware.bucketDel(f"{BUCKET_PREFIX}.user", owner_id)
    sender.reply(f"✅ 已清理 {cleaned_count} 个过期账号")


def tutorial() -> None:
    sender.reply(
        f"====={FULL_SCRIPT_NAME}教程=====\n"
        "1. 扫码进入小程序-个人中心-客户编号就是wid\n"
        "2. 发送“茄皇登录”，按 wid 格式绑定\n"
        "3. 授权后会自动写入青龙 QH 环境变量\n"
        "4. 发送“茄皇执行”可立即运行全部任务\n"
        "5. 授权费用：1元/月或 300积分/月\n"
        "6. 项目收益：几个月可以兑换泡面\n"
        "===================="
    )
    tutorial_image = middleware.bucketGet(BUCKET_PREFIX, "tutorial_image")
    if tutorial_image:
        sender.replyImage(str(tutorial_image))
    sender.reply(
        "=====茄皇可用指令=====\n"
        "茄皇教程：查看使用教程\n"
        "茄皇登录：验证并绑定账号\n"
        "茄皇查询：查询能量、番茄、阶段和任务\n"
        "茄皇执行：执行签到、任务、好友能量和能量使用\n"
        "茄皇管理：授权、查看 CK、同步或删除账号\n"
        "--------------------\n管理员指令：茄皇授权、茄皇清理\n"
        "===================="
    )


def main() -> None:
    message = sender.getMessage()
    if "登录" in message or "登陆" in message or "上车" in message:
        batch_login()
    elif "查询" in message:
        query()
    elif "执行" in message or "运行" in message:
        execute()
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
