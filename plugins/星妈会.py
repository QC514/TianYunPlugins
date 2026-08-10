#[disable:true]
# [title:星妈会]
# [language: python]
# [class: 工具类]
# [author: sky2022]
# [service: 2661320550]
# [rule: ^星妈会(登录|登陆|查询|管理|一键运行|后台|教程)$|^(登录|登陆|查询|管理)星妈会$]
# [cron: 0 8,15 * * *]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://tg.96218.xyz/file/BQACAgUAAxkDAAIHCmm-LiuIplV2-MijHZDPMGWzMIqcAAIzHAACNG7wVX3FrlyGxlWhOgQ.png]
# [version: 1.0.3]
# [public: true]
# [price: 12.88]
# [admin: false]
# [description: 此插件出自徒弟：huawei。<br>合并版【星妈会】插件，内置飞鹤项目与星妈会项目，插件内置运行。<br>登录格式固定为“飞鹤token#authorization”，左侧留空表示只绑定星妈会，右侧留空表示只绑定飞鹤。<br>指令：星妈会登录、星妈会查询、星妈会管理、星妈会一键运行、星妈会后台、星妈会教程。<br>定时任务：每天8点和15点自动检测授权过期并推送通知。<br>V1.0.3:新增定时检测推送，每天8点/15点自动检测授权到期状态并通知用户。]
# [param: {"required":false,"key":"dd_xmyx_config.price","bool":false,"name":"上车价格","placeholder":"例:0.88,填0为免费","value":"0.88","desc":"单个账号每月授权价格，按月数和账号数量累计"}]
# [param: {"required":false,"key":"dd_xmyx_config.points_per_month","bool":false,"name":"积分开通","placeholder":"例:100,填0为关闭积分支付","value":"100","desc":"单个账号每月消耗积分，按月数和账号数量累计"}]
# [param: {"required":false,"key":"dd_xmyx_config.zsm","bool":false,"name":"收款方式","placeholder":"http://example.com/pay.jpg","desc":"微信收款码或赞赏码链接；为空时回退读取全局收款配置"}]
# [param: {"required":false,"key":"dd_xmyx_config.use_ma_pay","bool":true,"name":"使用码支付","desc":"是否使用码支付系统，开启后将使用卡密系统中的全局码支付配置"}]

import hashlib
import json
import re
import time
import random
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from urllib.parse import quote as url_quote

import middleware
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PROJECT_NAME = "星妈会"
BUCKET_USER = "dd_xmyx_user"
BUCKET_TOKEN = "dd_xmyx_token"
BUCKET_AUTH = "dd_xmyx_auth"
BUCKET_CONFIG = "dd_xmyx_config"
MOMCLUB_BASE_URL = "https://momclub.feihe.com/capis/c"
FEIHE_API_APP_ID = "xmyx"
PAY_TIMEOUT = 600000
PAY_POLL_TIMES = 60
PAY_POLL_INTERVAL_MS = 5000

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()


def ensure_bucket_tuple(bucket_or_buckets):
    if not bucket_or_buckets:
        return tuple()
    if isinstance(bucket_or_buckets, (list, tuple, set)):
        return tuple(item for item in bucket_or_buckets if item)
    return (bucket_or_buckets,)


def has_bucket_value(value):
    return value is not None and str(value).strip() != ""


def bucket_get_first(primary_bucket, key, legacy_buckets=None, default=""):
    value = middleware.bucketGet(primary_bucket, key)
    if has_bucket_value(value):
        return value
    return default


def bucket_set_primary(primary_bucket, key, value):
    middleware.bucketSet(primary_bucket, key, value)


def bucket_del_all(primary_bucket, key, legacy_buckets=None):
    middleware.bucketDel(primary_bucket, key)


def bucket_all_keys_merged(primary_bucket, legacy_buckets=None):
    merged = []
    for bucket_name in (primary_bucket,):
        for item in middleware.bucketAllKeys(bucket_name) or []:
            if item not in merged:
                merged.append(item)
    return merged


def parse_bucket_phone_list(raw):
    text = str(raw or "").strip()
    if not text:
        return []
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
        if isinstance(data, str):
            text = data
    except Exception:
        pass
    phones = []
    for part in str(text).replace("\r\n", "\n").replace("&", ",").split(","):
        current = str(part).strip()
        if current:
            phones.append(current)
    return list(dict.fromkeys(phones))


FEIHE_API_APP_KEY = str(bucket_get_first(BUCKET_CONFIG, "appKey") or "").strip() or "TwUQ01lKS1Km5zlV2f7amsZc5EQYkTbv"

def generate_qrcode_url(content):
    encoded = url_quote(str(content or ""))
    return "https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={}".format(encoded)


def get_pay_config():
    raw_types = (
        middleware.bucketGet("dd_sign_config", "pay_types")
        or middleware.bucketGet("dd_sign_config", "ma_pay_type")
        or ""
    )
    pay_types = parse_pay_types(raw_types)
    config = {
        "zsm": str(middleware.bucketGet("dd_sign_config", "zsm") or "").strip(),
        "ma_pay_switch": parse_bool(middleware.bucketGet("dd_sign_config", "ma_pay_switch") or "false"),
        "gateway": str(middleware.bucketGet("dd_sign_config", "ma_pay_gateway") or "").strip(),
        "pid": str(middleware.bucketGet("dd_sign_config", "ma_pay_pid") or "").strip(),
        "key": str(middleware.bucketGet("dd_sign_config", "ma_pay_key") or "").strip(),
        "type": str(middleware.bucketGet("dd_sign_config", "ma_pay_type") or "").strip(),
        "notify_url": str(middleware.bucketGet("dd_sign_config", "ma_pay_notify_url") or "").strip(),
        "return_url": str(middleware.bucketGet("dd_sign_config", "ma_pay_return_url") or "").strip(),
        "pay_types": pay_types,
    }
    config["ma_pay_ready"] = bool(
        config["ma_pay_switch"]
        and config["gateway"]
        and config["pid"]
        and config["key"]
        and (config["type"] or config["pay_types"])
    )
    return config


class MaPayClient:
    def __init__(self):
        self.last_error = ""
        self.config = get_pay_config()

    @staticmethod
    def _normalize_gateway(gateway):
        return str(gateway or "").strip().rstrip("/")

    def is_configured(self):
        self.config = get_pay_config()
        if not self.config.get("ma_pay_switch"):
            self.last_error = "未开启全局码支付"
            return False
        if not self.config.get("ma_pay_ready"):
            self.last_error = "全局码支付配置不完整"
            return False
        self.last_error = ""
        return True

    def _get_default_pay_type(self):
        pay_type = str(self.config.get("type") or "").split(",")[0].strip()
        if pay_type:
            return pay_type
        pay_types = self.config.get("pay_types") or {}
        return next(iter(pay_types.keys()), "")

    def _build_mapi_url(self):
        gateway = self._normalize_gateway(self.config.get("gateway"))
        if gateway.endswith("/mapi.php"):
            return gateway
        return "{}/mapi.php".format(gateway)

    def _build_query_url(self):
        gateway = self._normalize_gateway(self.config.get("gateway"))
        if gateway.endswith("/mapi.php"):
            gateway = gateway[:-9]
        if gateway.endswith("/xpay/epay/api.php"):
            return gateway
        return "{}/xpay/epay/api.php".format(gateway)

    def create_order(self, amount, pay_type_key, out_trade_no, subject, attach_value=""):
        if not self.is_configured():
            return {"error": self.last_error}
        pay_type = str(pay_type_key or self._get_default_pay_type()).strip()
        if not pay_type:
            return {"error": "未获取到支付方式"}
        params = {
            "pid": self.config["pid"],
            "type": pay_type,
            "out_trade_no": out_trade_no,
            "name": subject,
            "money": "{:.2f}".format(float(amount)),
            "notify_url": self.config.get("notify_url"),
            "return_url": self.config.get("return_url"),
            "param": str(attach_value or "").strip(),
        }
        params = {key: value for key, value in params.items() if str(value or "").strip()}
        sorted_params = sorted(params.items(), key=lambda item: item[0])
        sign_str = "&".join(["{}={}".format(key, value) for key, value in sorted_params])
        params["sign"] = hashlib.md5((sign_str + self.config["key"]).encode("utf-8")).hexdigest().lower()
        params["sign_type"] = "MD5"
        try:
            response = requests.post(
                self._build_mapi_url(),
                data=params,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
        except Exception as exc:
            self.last_error = "创建支付订单失败: {}".format(exc)
            return {"error": self.last_error}
        if response.status_code != 200:
            self.last_error = "创建支付订单失败，HTTP状态码 {}".format(response.status_code)
            return {"error": self.last_error}
        try:
            result = response.json()
        except Exception:
            self.last_error = "创建支付订单失败，返回数据格式错误"
            return {"error": self.last_error}
        code = str(result.get("code") or "").strip()
        msg = str(result.get("msg") or "未知状态").strip()
        if code not in ("1", "200"):
            self.last_error = msg or "创建支付订单失败"
            return {"error": self.last_error, "raw": result}
        pay_url = str(result.get("payurl") or result.get("pay_url") or "").strip()
        if not pay_url:
            self.last_error = "未获取到支付链接"
            return {"error": self.last_error, "raw": result}
        self.last_error = ""
        return {"pay_url": pay_url, "raw": result}

    def is_paid(self, out_trade_no):
        if not self.is_configured():
            return False
        try:
            response = requests.get(
                self._build_query_url(),
                params={
                    "act": "order",
                    "pid": self.config["pid"],
                    "key": self.config["key"],
                    "out_trade_no": out_trade_no,
                },
                timeout=10,
            )
            result = response.json()
        except Exception as exc:
            self.last_error = "查询支付状态失败: {}".format(exc)
            return False
        code = str(result.get("code") or "").strip()
        status = str(result.get("status") or "").strip()
        paid = code in ("1", "200") and status == "1"
        if not paid:
            self.last_error = str(result.get("msg") or "").strip()
        else:
            self.last_error = ""
        return paid


class MomClubClient:
    def __init__(self, authorization):
        self.authorization = str(authorization or "").strip()
        self.phone = None
        self.nickname = None
        self.user_label = "未登录"

    def _headers(self):
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541022) XWEB/16467",
            "authorization": self.authorization,
            "content-type": "application/json",
            "locale": "zh_CN",
            "referer": "https://servicewechat.com/wxc83b55d61c7fc51d/75/page-frame.html",
        }

    def _update_user_label(self):
        self.user_label = mask_phone(self.phone) or self.nickname or "未命名账号"

    def get_member_info(self):
        if not self.authorization:
            return None
        try:
            response = requests.get(
                "{}/user/memberInfo".format(MOMCLUB_BASE_URL),
                headers=self._headers(),
                timeout=(5, 20),
                verify=False,
            )
            result = response.json()
            data = result.get("data")
            if result.get("success") and data:
                self.phone = str(data.get("mobile") or data.get("phone") or "").strip() or self.phone
                self.nickname = str(data.get("nickname") or data.get("name") or "").strip() or self.nickname
                self._update_user_label()
                return data
        except Exception:
            return None
        return None

    def get_todo_list(self):
        if not self.authorization:
            return None
        try:
            response = requests.get(
                "{}/activity/todo/list".format(MOMCLUB_BASE_URL),
                headers=self._headers(),
                params={"mockTime": int(time.time() * 1000)},
                timeout=(5, 20),
                verify=False,
            )
            result = response.json()
            data = result.get("data")
            if result.get("success") and data:
                return data
        except Exception:
            return None
        return None

    def checkin(self, checkin_data):
        try:
            activity_id = checkin_data.get("id")
            extra = checkin_data.get("checkInExtra", {}) or {}
            join_record = extra.get("joinRecord", []) or []
            today_record = next((record for record in join_record if record.get("today")), None)

            if today_record and today_record.get("joined"):
                return {"success": True, "credits": today_record.get("credits", 0), "already_done": True}

            payload = {"activityId": activity_id, "mockTime": int(time.time() * 1000)}
            response = requests.post(
                "{}/activity/todo/checkIn".format(MOMCLUB_BASE_URL),
                headers=self._headers(),
                json=payload,
                timeout=(5, 30),
                verify=False,
            )
            result = response.json()
            if result.get("success"):
                return {"success": True, "credits": result.get("data", {}).get("credits", 0), "already_done": False}
            return {"success": False, "message": result.get("message") or result.get("msg") or "签到失败"}
        except Exception as exc:
            return {"success": False, "message": str(exc)}

    def complete_task(self, task):
        task_name = task.get("name", "未知任务")
        try:
            activity_id = task.get("id")
            extra = task.get("taskTodoExtra", {}) or {}
            credits = extra.get("credits", 0)
            payload = {"activityId": activity_id, "mockTime": int(time.time() * 1000)}

            receive_response = requests.post(
                "{}/activity/todo/receive".format(MOMCLUB_BASE_URL),
                headers=self._headers(),
                json=payload,
                timeout=(5, 30),
                verify=False,
            )
            receive_result = receive_response.json()
            if not receive_result.get("success"):
                return {"success": False, "message": receive_result.get("message") or "{} 领取失败".format(task_name)}

            time.sleep(random.randint(3, 6))
            payload["mockTime"] = int(time.time() * 1000)
            complete_response = requests.post(
                "{}/activity/todo/complete".format(MOMCLUB_BASE_URL),
                headers=self._headers(),
                json=payload,
                timeout=(5, 30),
                verify=False,
            )
            complete_result = complete_response.json()
            if complete_result.get("success"):
                return {"success": True, "task_name": task_name, "credits": credits}
            return {"success": False, "message": complete_result.get("message") or "{} 完成失败".format(task_name)}
        except Exception as exc:
            return {"success": False, "message": "{} 异常: {}".format(task_name, exc)}

    def run_all_tasks(self):
        completed = 0
        messages = []
        todo_data = self.get_todo_list()
        if not todo_data:
            return {"completed": 0, "messages": ["任务列表获取失败"]}

        checkin_data = todo_data.get("checkInTodo")
        if checkin_data:
            checkin_result = self.checkin(checkin_data)
            if checkin_result.get("success"):
                completed += 1
                if checkin_result.get("already_done"):
                    messages.append("今日已签到")
                else:
                    messages.append("签到成功(+{}积分)".format(checkin_result.get("credits", 0)))
            else:
                messages.append("签到失败: {}".format(checkin_result.get("message") or "未知错误"))
            time.sleep(random.randint(1, 3))

        skip_types = {"Perfect", "AddQw", "FirstOrder"}
        for task in todo_data.get("taskTodo", []) or []:
            extra = task.get("taskTodoExtra", {}) or {}
            task_type = extra.get("type", "")
            task_name = task.get("name", "未知任务")
            status = extra.get("status", "")
            complete_count = extra.get("completeCount", 0)
            complete_limit = extra.get("completeLimit", 1)

            if task_type in skip_types:
                messages.append("跳过任务: {}".format(task_name))
                continue
            if status == "3" or complete_count >= complete_limit:
                messages.append("任务已完成: {}".format(task_name))
                continue

            task_result = self.complete_task(task)
            if task_result.get("success"):
                completed += 1
                messages.append("任务完成: {} (+{}积分)".format(task_name, task_result.get("credits", 0)))
            else:
                messages.append("任务失败: {}".format(task_result.get("message") or task_name))
            time.sleep(random.randint(2, 4))

        return {"completed": completed, "messages": messages}


class FeiHeAuto:
    def __init__(self, access_token):
        self.token = str(access_token or "").strip()
        self.headers = {
            "Host": "www.feihevip.com",
            "token": self.token,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302b) NetType/4G Language/zh_CN",
            "Referer": "https://servicewechat.com/wx4205ec55b793245e/215/page-frame.html",
            "fhAppid": FEIHE_API_APP_ID,
            "source": "1",
        }

    def get_timestamp(self):
        return int(str(int(time.time() * 1000))[:10])

    def get_nonce(self, config=None):
        config = config or {}
        length = config.get("length", 16)
        use_numeric = config.get("numeric", True)
        use_letters = config.get("letters", True)
        use_special = config.get("special", False)
        exclude = config.get("exclude", []) if isinstance(config.get("exclude", []), list) else []
        char_pool = ""
        if use_numeric:
            char_pool += "0123456789"
        if use_letters:
            char_pool += "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if use_special:
            char_pool += "!$%^&*()_+|~-=`{}[]:;<>?,./"
        for excluded_char in exclude:
            char_pool = char_pool.replace(excluded_char, "")
        result = ""
        for _ in range(length):
            result += random.choice(char_pool)
        return result

    def get_signature(self):
        fh_nonce_str = self.get_nonce({"length": 16})
        fh_timestamp = self.get_timestamp()
        sign_string = "fhAppid{}fhNonceStr{}fhTimestamp{}{}{}".format(
            FEIHE_API_APP_ID,
            fh_nonce_str,
            fh_timestamp,
            "{}",
            FEIHE_API_APP_KEY,
        )
        return {
            "fhNonceStr": fh_nonce_str,
            "fhTimestamp": str(fh_timestamp),
            "fhSign": hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper(),
        }

    def get_refresh_signature(self):
        fh_nonce_str = self.get_nonce({"length": 16})
        fh_timestamp = self.get_timestamp()
        sign_string = "fhAppidxmhfhNonceStr{}fhTimestamp{}98d9fe9b613a479dbcb111ca261e3ce1".format(
            fh_nonce_str,
            fh_timestamp,
        )
        return {
            "fhNonceStr": fh_nonce_str,
            "fhTimestamp": str(fh_timestamp),
            "fhSign": hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper(),
        }

    def get_user_info(self):
        try:
            signature = self.get_signature()
            response = requests.post(
                "https://www.feihevip.com/api/starMember/getMemberInfo",
                headers={**self.headers, **signature},
                json={},
                timeout=(5, 30),
            )
            result = response.json()
            if result.get("code") == "200" and result.get("data"):
                return result.get("data")
        except Exception:
            return None
        return None

    def get_task_list(self):
        for _ in range(3):
            try:
                signature = self.get_signature()
                response = requests.get(
                    "https://www.feihevip.com/api/member/signin/getTaskList",
                    headers={**self.headers, **signature},
                    json={},
                    timeout=(5, 30),
                )
                result = response.json()
                if result.get("code") == "200" and len(result.get("data", [])) > 0:
                    return result["data"]
            except Exception:
                pass
            time.sleep(2)
        return []

    def signin(self):
        for _ in range(3):
            try:
                signature = self.get_signature()
                response = requests.post(
                    "https://www.feihevip.com/api/member/signin/sign",
                    headers={**self.headers, **signature},
                    json={},
                    timeout=(5, 30),
                )
                result = response.json()
                if result.get("code") == "200":
                    return True
            except Exception:
                pass
            time.sleep(2)
        return False

    def tofinish(self, task_type):
        for _ in range(2):
            try:
                signature = self.get_signature()
                response = requests.get(
                    "https://www.feihevip.com/api/member/signin/tofinish?taskType={}".format(task_type),
                    headers={**self.headers, **signature},
                    json={},
                    timeout=(5, 30),
                )
                result = response.json()
                if result.get("code") == "200":
                    return True
            except Exception:
                pass
            time.sleep(2)
        return False

    def complete_task(self, task_type):
        for _ in range(3):
            try:
                signature = self.get_signature()
                response = requests.get(
                    "https://www.feihevip.com/api/member/signin/completeTask?taskType={}".format(task_type),
                    headers={**self.headers, **signature},
                    json={},
                    timeout=(5, 30),
                )
                result = response.json()
                if result.get("code") == "200":
                    return True
            except Exception:
                pass
            time.sleep(2)
        return False

    def refresh_token(self):
        try:
            signature = self.get_refresh_signature()
            response = requests.get(
                "https://mom.feihe.com/program/token/refreshToken",
                headers={
                    "Host": "mom.feihe.com",
                    "token": self.token,
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302b) NetType/4G Language/zh_CN",
                    "Referer": "https://servicewechat.com/wx4205ec55b793245e/215/page-frame.html",
                    "fhAppid": "xmh",
                    "source": "1",
                    **signature,
                },
                timeout=(5, 30),
            )
            result = response.json()
            new_token = result.get("data")
            if new_token:
                self.token = str(new_token).strip()
                self.headers["token"] = self.token
                return self.token
        except Exception:
            return None
        return None


def run_feihe_task_list(task_list, client):
    completed = 0
    for task in task_list or []:
        task_name = str(task.get("taskName") or "").strip()
        task_type = str(task.get("taskType") or "").strip()
        if not task_name or not task_type:
            continue
        if re.search(r"购买任意商品", task_name):
            continue
        client.tofinish(task_type)
        time.sleep(random.randint(2, 5))
        if client.complete_task(task_type):
            completed += 1
        time.sleep(1)
        time.sleep(random.randint(3, 6))
    return completed


def fetch_feihe_snapshot(access_token):
    client = FeiHeAuto(access_token)
    try:
        client.refresh_token()
    except Exception:
        pass
    user_info = client.get_user_info()
    if not user_info:
        return None
    base_info = user_info.get("baseInfo") or {}
    member_points = user_info.get("memberPoints") or {}
    phone = str(base_info.get("mobile") or base_info.get("fullName") or base_info.get("openId") or "").strip()
    if not phone:
        return None
    return {
        "phone": phone,
        "display_name": sanitize_text(base_info.get("nickName") or mask_phone(phone)),
        "points": member_points.get("scoreBalance", 0),
        "grade_name": sanitize_text(base_info.get("memberLevelName") or user_info.get("memberLevelName") or "飞鹤会员"),
        "new_token": client.token,
    }


def run_feihe_account(access_token):
    client = FeiHeAuto(access_token)
    user_info_before = client.get_user_info() or {}
    if not user_info_before:
        return {
            "success": False,
            "sign_success": False,
            "completed_tasks": 0,
            "earned_points": 0,
            "points_before": 0,
            "points_after": 0,
            "new_token": "",
        }
    member_points_before = user_info_before.get("memberPoints") or {}
    score_before = safe_int(member_points_before.get("scoreBalance") or 0, 0)
    sign_success = client.signin()
    task_list = client.get_task_list() or []
    completed_tasks = run_feihe_task_list(task_list, client) if task_list else 0
    new_token = client.refresh_token() or ""
    time.sleep(1)
    user_info_after = client.get_user_info() or {}
    member_points_after = user_info_after.get("memberPoints") or {}
    score_after = safe_int(member_points_after.get("scoreBalance"), score_before)
    return {
        "success": bool(sign_success or completed_tasks > 0 or score_after >= score_before),
        "sign_success": sign_success,
        "completed_tasks": completed_tasks,
        "earned_points": max(0, score_after - score_before),
        "points_before": score_before,
        "points_after": score_after,
        "new_token": new_token,
    }


def run_momclub_account(authorization):
    client = MomClubClient(authorization)
    member_info_before = client.get_member_info()
    if not member_info_before:
        return {"success": False, "message": "authorization 无效或已过期", "earned_points": 0, "completed_tasks": 0}

    points_before = safe_int(member_info_before.get("points") or 0, 0)
    run_result = client.run_all_tasks()
    time.sleep(2)
    member_info_after = client.get_member_info() or member_info_before
    points_after = safe_int(member_info_after.get("points") or points_before, points_before)
    return {
        "success": True,
        "earned_points": max(0, points_after - points_before),
        "completed_tasks": safe_int(run_result.get("completed") or 0, 0),
        "messages": run_result.get("messages") or [],
        "points_before": points_before,
        "points_after": points_after,
    }


def parse_bool(value):
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() == "true"


def safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def parse_decimal(value, default_value="0"):
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        return Decimal(default_value)


def format_money(amount):
    if not isinstance(amount, Decimal):
        amount = parse_decimal(amount, "0")
    return "{:.2f}".format(amount)


def sanitize_text(value):
    text = str(value or "").strip()
    return text.replace("#", "-").replace("|", "-").replace("丨", "-").replace("\r", " ").replace("\n", " ")


def mask_phone(phone):
    phone = str(phone or "").strip()
    if len(phone) < 7:
        return phone
    return "{}****{}".format(phone[:3], phone[-4:])


def today_date():
    return datetime.now().date()


def parse_date(date_str):
    try:
        return datetime.strptime(str(date_str), "%Y-%m-%d").date()
    except Exception:
        return None


def read_input(prompt="", timeout=120000):
    if prompt:
        sender.reply(prompt)
    value = sender.input(timeout, 1, False)
    if value is None:
        return None
    text = str(value).strip()
    if text.lower() == "q":
        return None
    return text


def get_user_phones(user_id=None):
    user_id = user_id or userid
    raw = middleware.bucketGet(BUCKET_USER, user_id) or ""
    return parse_bucket_phone_list(raw)


def save_user_phones(phones, user_id=None):
    user_id = user_id or userid
    normalized = [str(phone).strip() for phone in phones if str(phone).strip()]
    normalized = list(dict.fromkeys(normalized))
    if normalized:
        bucket_set_primary(BUCKET_USER, user_id, ",".join(normalized))
    else:
        bucket_del_all(BUCKET_USER, user_id)


def add_user_phone(phone, user_id=None):
    phones = get_user_phones(user_id)
    if phone not in phones:
        phones.append(phone)
        save_user_phones(phones, user_id)


def remove_user_phone(phone, user_id=None):
    phones = get_user_phones(user_id)
    if phone in phones:
        phones.remove(phone)
        save_user_phones(phones, user_id)


def get_token_info(phone):
    raw = bucket_get_first(BUCKET_TOKEN, phone) or ""
    parts = str(raw).split("#", 1)
    feihe_token = str(parts[0] if len(parts) > 0 else "").strip()
    authorization = str(parts[1] if len(parts) > 1 else "").strip()
    return {
        "feihe_token": feihe_token,
        "authorization": authorization,
        "display_name": mask_phone(phone),
    }


def save_project_tokens(phone, feihe_token=None, authorization=None):
    current = get_token_info(phone)
    new_feihe_token = str(current.get("feihe_token") or "").strip()
    new_authorization = str(current.get("authorization") or "").strip()
    if feihe_token is not None:
        new_feihe_token = str(feihe_token or "").strip()
    if authorization is not None:
        new_authorization = str(authorization or "").strip()
    if not new_feihe_token and not new_authorization:
        bucket_del_all(BUCKET_TOKEN, phone)
        return
    bucket_set_primary(BUCKET_TOKEN, phone, "{}#{}".format(new_feihe_token, new_authorization))


def get_auth(phone):
    return str(bucket_get_first(BUCKET_AUTH, phone) or "").strip()


def save_auth(phone, expire_date):
    bucket_set_primary(BUCKET_AUTH, phone, str(expire_date))


def is_authorized(phone):
    expire_date = parse_date(get_auth(phone))
    return bool(expire_date and expire_date >= today_date())


def get_owner_of_phone(phone):
    users = bucket_all_keys_merged(BUCKET_USER) or []
    for user_id in users:
        if phone in get_user_phones(user_id):
            return user_id
    return None


def get_feihe_token(phone):
    return str(get_token_info(phone).get("feihe_token") or "").strip()


def save_feihe_token(phone, access_token):
    save_project_tokens(phone, feihe_token=access_token)


def get_today_earned(phone):
    key = "{}_{}".format(phone, today_date().strftime("%Y%m%d"))
    return safe_int(middleware.bucketGet("dd_xmyx_daily", key) or 0, 0)


def add_today_earned(phone, points):
    if points <= 0:
        return
    key = "{}_{}".format(phone, today_date().strftime("%Y%m%d"))
    current = get_today_earned(phone)
    middleware.bucketSet("dd_xmyx_daily", key, str(current + points))


def has_project_binding(phone, project_name):
    project = str(project_name or "").strip().lower()
    token_info = get_token_info(phone)
    if project == "feihe":
        return bool(str(token_info.get("feihe_token") or "").strip())
    if project == "momclub":
        return bool(str(token_info.get("authorization") or "").strip())
    return False


def parse_pay_types(raw_value):
    result = {}
    default_names = {"alipay": "支付宝", "wxpay": "微信支付", "qqpay": "QQ钱包"}
    for item in str(raw_value or "").split(","):
        current = item.strip()
        if not current:
            continue
        if ":" in current:
            key, name = current.split(":", 1)
            key = key.strip()
            if key:
                result[key] = name.strip() or default_names.get(key, key)
        else:
            result[current] = default_names.get(current, current)
    return result


def get_config():
    payment_config = get_pay_config()
    pay_types = payment_config.get("pay_types") or {}
    zsm = str(middleware.bucketGet(BUCKET_CONFIG, "zsm") or payment_config.get("zsm") or "").strip()
    return {
        "price": parse_decimal(middleware.bucketGet(BUCKET_CONFIG, "price") or "0.88", "0.88"),
        "points_per_month": safe_int(middleware.bucketGet(BUCKET_CONFIG, "points_per_month") or 100, 100),
        "zsm": zsm,
        "use_ma_pay": parse_bool(middleware.bucketGet(BUCKET_CONFIG, "use_ma_pay") or "false"),
        "ma_pay_switch": parse_bool(payment_config.get("ma_pay_switch") or middleware.bucketGet("dd_sign_config", "ma_pay_switch") or "false"),
        "ma_pay_ready": bool(payment_config.get("ma_pay_ready")),
        "pay_types": pay_types,
    }


def parse_bind_line(raw_text):
    text = str(raw_text or "").strip()
    if not text:
        return None
    if "#" in text:
        feihe_token, authorization = text.split("#", 1)
        feihe_token = feihe_token.strip()
        authorization = authorization.strip()
        if not feihe_token and not authorization:
            return None
        return {
            "project": "combined",
            "feihe_token": feihe_token,
            "authorization": authorization,
        }
    return {"project": "auto", "credential": text}


def is_valid_bind_item(item):
    if not item:
        return False
    if str(item.get("project") or "").strip().lower() == "combined":
        return bool(str(item.get("feihe_token") or "").strip() or str(item.get("authorization") or "").strip())
    return bool(str(item.get("credential") or "").strip())


def parse_bind_inputs(raw_text):
    items = []
    for line in str(raw_text or "").splitlines():
        item = parse_bind_line(line)
        if is_valid_bind_item(item):
            items.append(item)
    if not items:
        item = parse_bind_line(raw_text)
        if is_valid_bind_item(item):
            items.append(item)

    unique_items = []
    seen = set()
    for item in items:
        key = (
            item.get("project"),
            item.get("credential"),
            item.get("feihe_token"),
            item.get("authorization"),
        )
        if key in seen:
            continue
        seen.add(key)
        unique_items.append(item)
    return unique_items


def fetch_momclub_snapshot(authorization):
    member_info = MomClubClient(authorization).get_member_info()
    if not member_info:
        return None
    phone = str(member_info.get("mobile") or member_info.get("phone") or "").strip()
    if not phone:
        return None
    return {
        "member_id": str(member_info.get("memberId") or member_info.get("id") or member_info.get("userId") or phone),
        "phone": phone,
        "grade_name": sanitize_text(member_info.get("gradeName") or "未知等级"),
        "points": member_info.get("points", 0),
    }


def bind_or_update_momclub_account(raw_text, old_phone=None):
    authorization = str(raw_text or "").strip()
    if not authorization:
        return False, "请输入 authorization"
    snapshot = fetch_momclub_snapshot(authorization)
    if not snapshot:
        return False, "authorization 无效或已过期，请重新抓包"
    phone = snapshot["phone"]
    existing_owner = get_owner_of_phone(phone)
    if existing_owner and existing_owner != userid:
        if not old_phone or phone != old_phone:
            return False, "该账号已被其他用户绑定，请联系管理员处理"
    if old_phone and old_phone != phone:
        old_auth = get_auth(old_phone)
        old_feihe_token = get_feihe_token(old_phone)
        bucket_del_all(BUCKET_TOKEN, old_phone)
        bucket_del_all(BUCKET_AUTH, old_phone)
        remove_user_phone(old_phone, userid)
        if old_auth and not get_auth(phone):
            save_auth(phone, old_auth)
        if old_feihe_token and not get_feihe_token(phone):
            save_feihe_token(phone, old_feihe_token)
    display_name = mask_phone(phone)
    existed = has_project_binding(phone, "momclub")
    save_project_tokens(phone, authorization=authorization)
    add_user_phone(phone, userid)
    return True, {
        "phone": phone,
        "display_name": display_name,
        "grade_name": snapshot["grade_name"],
        "points": snapshot["points"],
        "existed": existed,
        "sync_message": "",
    }


def bind_or_update_feihe_account(raw_text, old_phone=None):
    access_token = str(raw_text or "").strip()
    if not access_token:
        return False, "请输入飞鹤 access_token"
    snapshot = fetch_feihe_snapshot(access_token)
    if not snapshot:
        return False, "飞鹤 access_token 无效或已过期"
    phone = snapshot["phone"]
    existing_owner = get_owner_of_phone(phone)
    if existing_owner and existing_owner != userid:
        return False, "该账号已被其他用户绑定，请联系管理员处理"
    if old_phone and phone != old_phone:
        old_token_info = get_token_info(old_phone)
        old_auth = old_token_info.get("authorization") or ""
        old_expire = get_auth(old_phone)
        bucket_del_all(BUCKET_TOKEN, old_phone)
        bucket_del_all(BUCKET_AUTH, old_phone)
        remove_user_phone(old_phone, userid)
        if old_auth and not get_token_info(phone).get("authorization"):
            save_project_tokens(phone, authorization=old_auth)
        if old_expire and not get_auth(phone):
            save_auth(phone, old_expire)
    existed = bool(get_feihe_token(phone))
    save_feihe_token(phone, snapshot.get("new_token") or access_token)
    add_user_phone(phone, userid)
    return True, {
        "phone": phone,
        "display_name": snapshot["display_name"] or mask_phone(phone),
        "grade_name": snapshot["grade_name"],
        "points": snapshot["points"],
        "existed": existed,
        "sync_message": "",
    }


def bind_combined_account(feihe_token, authorization, old_phone=None):
    feihe_token = str(feihe_token or "").strip()
    authorization = str(authorization or "").strip()
    if not feihe_token and not authorization:
        return False, "未提供有效的飞鹤 token 或星妈会 authorization"

    feihe_snapshot = fetch_feihe_snapshot(feihe_token) if feihe_token else None
    if feihe_token and not feihe_snapshot:
        return False, "飞鹤 access_token 无效或已过期"

    momclub_snapshot = fetch_momclub_snapshot(authorization) if authorization else None
    if authorization and not momclub_snapshot:
        return False, "星妈会 authorization 无效或已过期"

    phones = [item["phone"] for item in (feihe_snapshot, momclub_snapshot) if item]
    if not phones:
        return False, "未识别到有效账号"
    if len(set(phones)) > 1:
        return False, "飞鹤和星妈会凭证对应的手机号不一致，无法合并绑定"

    phone = phones[0]
    existing_owner = get_owner_of_phone(phone)
    if existing_owner and existing_owner != userid:
        return False, "该账号已被其他用户绑定，请联系管理员处理"

    existed = bool(get_feihe_token(phone) or get_token_info(phone).get("authorization"))
    if old_phone and old_phone != phone:
        old_expire = get_auth(old_phone)
        bucket_del_all(BUCKET_TOKEN, old_phone)
        bucket_del_all(BUCKET_AUTH, old_phone)
        remove_user_phone(old_phone, userid)
        if old_expire and not get_auth(phone):
            save_auth(phone, old_expire)

    effective_feihe_token = (feihe_snapshot.get("new_token") if feihe_snapshot else None) or feihe_token or None
    save_project_tokens(phone, feihe_token=effective_feihe_token, authorization=authorization or None)
    add_user_phone(phone, userid)

    grade_name = "未知"
    points = 0
    if momclub_snapshot:
        grade_name = momclub_snapshot["grade_name"]
        points = momclub_snapshot["points"]
    elif feihe_snapshot:
        grade_name = feihe_snapshot["grade_name"]
        points = feihe_snapshot["points"]

    return True, {
        "phone": phone,
        "display_name": mask_phone(phone),
        "grade_name": grade_name,
        "points": points,
        "existed": existed,
        "sync_message": "",
    }


def bind_project_item(item, old_phone=None):
    project = str(item.get("project") or "auto").strip().lower()
    credential = str(item.get("credential") or "").strip()
    if project == "combined":
        ok, result = bind_combined_account(item.get("feihe_token"), item.get("authorization"), old_phone=old_phone)
        feihe_token = str(item.get("feihe_token") or "").strip()
        authorization = str(item.get("authorization") or "").strip()
        if feihe_token and authorization:
            project_name = "飞鹤+星妈会"
        elif feihe_token:
            project_name = "飞鹤"
        else:
            project_name = "星妈会"
        return ok, result, project_name

    if not credential:
        return False, "未提供有效凭证", ""

    if project == "momclub":
        ok, result = bind_or_update_momclub_account(credential, old_phone=old_phone)
        return ok, result, "星妈会"
    if project == "feihe":
        ok, result = bind_or_update_feihe_account(credential, old_phone=old_phone)
        return ok, result, "飞鹤"

    ok, result = bind_or_update_momclub_account(credential, old_phone=old_phone)
    if ok:
        return True, result, "星妈会"
    ok, feihe_result = bind_or_update_feihe_account(credential, old_phone=old_phone)
    if ok:
        return True, feihe_result, "飞鹤"
    return False, "未识别到有效的星妈会 authorization 或飞鹤 token", ""


def get_user_points(user_id=None):
    user_id = user_id or userid
    sign_coin = safe_int(middleware.bucketGet("dd_sign_coin", user_id) or 0, 0)
    sign_points = safe_int(middleware.bucketGet("dd_sign_points", user_id) or 0, 0)
    return {"dd_sign_coin": sign_coin, "dd_sign_points": sign_points, "total": sign_coin + sign_points}


def save_user_points(user_id, sign_coin, sign_points):
    middleware.bucketSet("dd_sign_coin", user_id, str(sign_coin))
    middleware.bucketSet("dd_sign_points", user_id, str(sign_points))


def deduct_user_points(user_id, required_points):
    points = get_user_points(user_id)
    if points["total"] < required_points:
        return False, points["total"]
    sign_coin = points["dd_sign_coin"]
    sign_points = points["dd_sign_points"]
    if sign_coin >= required_points:
        sign_coin -= required_points
    else:
        remain = required_points - sign_coin
        sign_coin = 0
        sign_points -= remain
    save_user_points(user_id, sign_coin, sign_points)
    return True, sign_coin + sign_points


def parse_payment_result(raw_data):
    money = None
    pay_time = ""
    from_name = ""
    try:
        if isinstance(raw_data, dict):
            if raw_data.get("Type") in ("微信赞赏", "微信收款"):
                money = float(raw_data.get("Money", 0))
                pay_time = str(raw_data.get("Time", "")).split(".")[0].replace("T", " ")
                from_name = raw_data.get("FromName", "")
            elif raw_data.get("type") in ("微信赞赏", "微信收款"):
                money = float(raw_data.get("money", 0))
                pay_time = str(raw_data.get("time", "")).split(".")[0].replace("T", " ")
                from_name = raw_data.get("from_name", "")
            elif raw_data.get("Money"):
                money = float(raw_data.get("Money", 0))
                pay_time = str(raw_data.get("Time", "")).split(".")[0].replace("T", " ")
                from_name = raw_data.get("FromName", "")
        else:
            text = str(raw_data or "")
            try:
                return parse_payment_result(json.loads(text))
            except Exception:
                money_match = re.search(r"收款金额[￥¥]?([0-9.]+)", text)
                time_match = re.search(r"到账时间[:：]?\s*([0-9:\- ]+)", text)
                if money_match:
                    money = float(money_match.group(1))
                if time_match:
                    pay_time = time_match.group(1).strip()
    except Exception:
        return None, "", ""
    return money, pay_time, from_name


def choose_ma_pay_type(config):
    items = list((config["pay_types"] or {}).items())
    if not items:
        return None, None
    if len(items) == 1:
        return items[0]
    lines = ["=====选择码支付方式====="]
    for index, item in enumerate(items, 1):
        lines.append("[{}] {}".format(index, item[1]))
    lines.append("回复序号选择，回复 q 取消")
    lines.append("==================")
    choice = read_input("\n".join(lines))
    if not choice or not choice.isdigit():
        return None, None
    idx = int(choice) - 1
    if idx < 0 or idx >= len(items):
        return None, None
    return items[idx]


def wechat_payment_flow(display_name, months, amount, config):
    sender.reply(
        "=====微信扫码支付=====\n"
        "👤 账号: {}\n⏰ 授权时长: {}个月\n💰 金额: ¥{}\n"
        "------------------\n请扫码完成支付\n回复 q 取消\n==================".format(display_name, months, format_money(amount))
    )
    try:
        sender.replyImage(config["zsm"])
    except Exception:
        sender.reply("❌ 收款码发送失败，请检查 dd_xmyx_config.zsm 或全局 dd_sign_config.zsm 配置")
        return False
    payment_result = sender.waitPay(timeout=PAY_TIMEOUT, exitcode="q")
    if payment_result == "q":
        sender.reply("✅ 已取消支付")
        return False
    money, pay_time, from_name = parse_payment_result(payment_result)
    if money is None:
        sender.reply("❌ 无法识别支付结果，请联系管理员核对")
        return False
    if Decimal(str(money)) >= amount:
        sender.reply("✅ 支付成功\n💰 实付: ¥{}\n⏰ 时间: {}\n{}".format(money, pay_time or "未知", "👤 付款人: {}".format(from_name) if from_name else ""))
        return True
    sender.reply("❌ 支付金额不足，应付 ¥{}，实付 ¥{}".format(format_money(amount), money))
    return False


def ma_payment_flow(display_name, months, amount, config):
    pay_type_key, pay_type_name = choose_ma_pay_type(config)
    if not pay_type_key:
        sender.reply("✅ 已取消码支付")
        return False
    client = MaPayClient()
    if not client.is_configured():
        sender.reply("❌ 码支付配置不完整，请检查卡密系统中的全局码支付配置")
        return False
    out_trade_no = "XMH{}{}".format(int(time.time()), str(userid)[-4:])
    subject = "{}授权-{}".format(PROJECT_NAME, sanitize_text(display_name)[:18])
    order_result = client.create_order(float(amount), pay_type_key, out_trade_no, subject, str(userid))
    if order_result.get("error"):
        sender.reply("❌ 创建码支付订单失败: {}".format(order_result["error"]))
        return False
    pay_url = order_result.get("pay_url") or ""
    if not pay_url:
        sender.reply("❌ 未获取到码支付链接")
        return False
    try:
        sender.replyImage(generate_qrcode_url(pay_url))
    except Exception:
        sender.reply("二维码发送失败，请打开下方链接完成支付：\n{}".format(pay_url))
    sender.reply("=====码支付=====\n👤 账号: {}\n⏰ 授权: {}个月\n💰 金额: ¥{}\n💳 方式: {}\n回复 q 取消\n==================".format(display_name, months, format_money(amount), pay_type_name))
    for _ in range(PAY_POLL_TIMES):
        result = sender.listen(PAY_POLL_INTERVAL_MS)
        if str(result).strip().lower() == "q":
            sender.reply("✅ 已取消支付")
            return False
        if client.is_paid(out_trade_no):
            sender.reply("✅ 码支付成功，已完成 {} 支付".format(pay_type_name))
            return True
    sender.reply("❌ 支付超时，请重新发起")
    return False


def format_target_label(target_label):
    text = str(target_label or "").strip()
    if text.isdigit():
        return mask_phone(text)
    return text or "账号"


def point_payment_flow(target_label, months, required_points):
    if required_points <= 0:
        return True
    target_name = format_target_label(target_label)
    current_points = get_user_points(userid)
    if current_points["total"] < required_points:
        sender.reply("❌ 积分不足，需要 {}，当前 {}".format(required_points, current_points["total"]))
        return False
    confirm = read_input("=====积分支付确认=====\n📱 账号: {}\n⏰ 时长: {}个月\n🎯 扣除: {}积分\n📊 剩余: {}积分\n回复 y 确认，回复 q 取消\n==================".format(target_name, months, required_points, current_points["total"] - required_points), 60000)
    if not confirm or confirm.lower() != "y":
        sender.reply("✅ 已取消积分支付")
        return False
    ok, remain_points = deduct_user_points(userid, required_points)
    if not ok:
        sender.reply("❌ 积分扣减失败")
        return False
    transaction = {
        "userid": userid,
        "phone": target_name,
        "months": months,
        "points": required_points,
        "balance": remain_points,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "{}授权".format(PROJECT_NAME),
    }
    middleware.bucketSet("dd_sign_transactions", "tx_{}".format(int(time.time() * 1000)), json.dumps(transaction, ensure_ascii=False))
    sender.reply("✅ 积分支付成功，剩余 {} 积分".format(remain_points))
    return True


def handle_authorize_payment(target_label, months, account_count=1):
    config = get_config()
    display_name = format_target_label(target_label)
    amount = config["price"] * Decimal(months) * Decimal(account_count)
    required_points = config["points_per_month"] * months * account_count
    ma_pay_enabled = config["use_ma_pay"] and config["ma_pay_switch"] and config["ma_pay_ready"] and config["pay_types"]
    if amount <= 0 and required_points <= 0:
        return True
    options = []
    option_map = {}
    if config["zsm"] and not ma_pay_enabled:
        option_map["1"] = "wechat"
        options.append("[1] 微信收款码  ¥{}".format(format_money(amount)))
    next_index = len(option_map) + 1
    if ma_pay_enabled:
        option_map[str(next_index)] = "ma"
        options.append("[{}] 码支付  ¥{}".format(next_index, format_money(amount)))
        next_index += 1
    if required_points > 0:
        option_map[str(next_index)] = "points"
        options.append("[{}] 积分支付  {}积分".format(next_index, required_points))
    if not option_map:
        sender.reply("❌ 未配置任何可用支付方式")
        return False
    choice = read_input("=====选择支付方式=====\n👤 账号: {}\n⏰ 时长: {}个月\n💰 金额: ¥{}\n🎯 积分: {}积分\n------------------\n{}\n回复序号选择，回复 q 取消\n==================".format(display_name, months, format_money(amount), required_points, "\n".join(options)))
    if not choice:
        sender.reply("✅ 已取消授权")
        return False
    selected = option_map.get(choice)
    if selected == "wechat":
        return wechat_payment_flow(display_name, months, amount, config)
    if selected == "ma":
        return ma_payment_flow(display_name, months, amount, config)
    if selected == "points":
        return point_payment_flow(display_name, months, required_points)
    sender.reply("❌ 无效选择")
    return False


def complete_authorization(phone, months, owner_userid=None):
    owner_userid = owner_userid or userid
    current_expire = parse_date(get_auth(phone))
    renew_type = "新授权"
    if current_expire and current_expire >= today_date():
        expire_date = current_expire + timedelta(days=months * 30)
        renew_type = "续费"
    else:
        expire_date = today_date() + timedelta(days=months * 30)
    expire_text = expire_date.strftime("%Y-%m-%d")
    save_auth(phone, expire_text)
    return {"expire_date": expire_text, "renew_type": renew_type}


def authorize_single_account(phone, owner_userid=None, free_mode=False):
    if not has_project_binding(phone, "feihe") and not has_project_binding(phone, "momclub"):
        sender.reply("❌ 当前账号未绑定任何项目数据，请先重新登录绑定")
        return
    token_info = get_token_info(phone)
    display_name = token_info.get("display_name") or mask_phone(phone)
    points = get_user_points(userid)
    identity_text = "\n".join(build_account_identity_lines(display_name, phone))
    months_text = read_input("=====账号授权=====\n{}\n📊 当前积分: {}\n------------------\n请输入授权月数 (1-12)\n回复 q 取消\n==================".format(identity_text, points["total"]))
    if not months_text:
        sender.reply("✅ 已取消授权")
        return
    if not months_text.isdigit() or not (1 <= int(months_text) <= 12):
        sender.reply("❌ 月数必须为 1-12 之间的整数")
        return
    months = int(months_text)
    if not free_mode and not handle_authorize_payment(display_name, months, 1):
        return
    result = complete_authorization(phone, months, owner_userid)
    sender.reply("✅ {}成功\n{}\n📅 到期: {}".format(result["renew_type"], identity_text, result["expire_date"]))


def bind_account():
    raw_text = read_input(
        "=====星妈会登录=====\n"
        "支持绑定【星妈会】和【飞鹤】两个项目\n"
        "------------------\n"
        "提交方式：\n"
        "1. 同时绑定两个项目：飞鹤token#authorization\n"
        "2. 仅绑定飞鹤：飞鹤token#\n"
        "3. 仅绑定星妈会：#authorization\n"
        "4. 批量提交时每行一条，统一使用以上格式\n"
        "------------------\n"
        "回复 q 取消\n"
        "=================="
    )
    if not raw_text:
        sender.reply("✅ 已取消绑定")
        return
    bind_items = parse_bind_inputs(raw_text)
    if not bind_items:
        sender.reply("❌ 请输入有效的【飞鹤token#authorization】格式")
        return
    if len(bind_items) == 1:
        ok, result, project_name = bind_project_item(bind_items[0])
        if not ok:
            sender.reply("❌ {}".format(result))
            return
        sender.reply(
            "✅ {}{}成功\n👤 项目: {}\n📱 手机: {}\n🎖 等级: {}\n🎁 积分: {}\n{}".format(
                project_name,
                "更新" if result["existed"] else "绑定",
                project_name,
                mask_phone(result["phone"]),
                result["grade_name"],
                result["points"],
                result["sync_message"] or "可前往【星妈会管理】继续完善账号",
            )
        )
        return

    success_items = []
    fail_items = []
    for index, item in enumerate(bind_items, 1):
        ok, result, project_name = bind_project_item(item)
        if ok:
            success_items.append({
                "index": index,
                "project": project_name,
                "phone": mask_phone(result["phone"]),
                "action": "更新成功" if result["existed"] else "绑定成功",
            })
        else:
            fail_items.append({
                "index": index,
                "reason": result,
            })
    lines = [
        "=====批量登录完成=====",
        "✅ 成功: {}".format(len(success_items)),
        "❌ 失败: {}".format(len(fail_items)),
        "------------------",
    ]
    for item in success_items:
        lines.append("[{}] [{}] {} {}".format(item["index"], item["project"], item["phone"], item["action"]))
    for item in fail_items:
        lines.append("[{}] 失败: {}".format(item["index"], item["reason"]))
    lines.append("==================")
    sender.reply("\n".join(lines))


def get_momclub_summary(phone):
    token_info = get_token_info(phone)
    authorization = str(token_info.get("authorization") or "").strip()
    if not authorization:
        return {
            "bound": False,
            "display_name": mask_phone(phone),
            "grade_name": "未绑定",
            "points": "未绑定",
            "pending_tasks": "-",
            "token_status": "未绑定",
        }
    client = MomClubClient(authorization)
    member_info = client.get_member_info()
    todo_data = client.get_todo_list()
    pending_tasks = "-"
    if todo_data:
        pending_tasks = 0
        for task in todo_data.get("taskTodo", []) or []:
            extra = task.get("taskTodoExtra") or {}
            if extra.get("status") == "3":
                continue
            if extra.get("completeCount", 0) >= extra.get("completeLimit", 1):
                continue
            pending_tasks += 1
    return {
        "bound": True,
        "display_name": token_info.get("display_name") or mask_phone(phone),
        "grade_name": member_info.get("gradeName") if member_info else "未知",
        "points": member_info.get("points") if member_info else "未知",
        "pending_tasks": pending_tasks,
        "token_status": "正常" if member_info else "可能失效",
    }


def get_feihe_summary(phone):
    access_token = get_feihe_token(phone)
    if not access_token:
        return {
            "bound": False,
            "display_name": mask_phone(phone),
            "grade_name": "未绑定",
            "points": "未绑定",
            "token_status": "未绑定",
        }
    snapshot = fetch_feihe_snapshot(access_token)
    if not snapshot:
        return {
            "bound": True,
            "display_name": mask_phone(phone),
            "grade_name": "未知",
            "points": "未知",
            "token_status": "可能失效",
        }
    new_token = snapshot.get("new_token")
    if new_token and new_token != access_token:
        save_feihe_token(phone, new_token)
    return {
        "bound": True,
        "display_name": snapshot["display_name"] or mask_phone(phone),
        "grade_name": snapshot["grade_name"],
        "points": snapshot["points"],
        "token_status": "正常",
    }


def format_project_binding_text(feihe_bound, momclub_bound):
    return "飞鹤{} ｜ 星妈会{}".format("✅" if feihe_bound else "❌", "✅" if momclub_bound else "❌")


def build_account_identity_lines(display_name, phone, single_label="📱 账号", account_label="👤 账号", phone_label="📱 手机"):
    display_text = str(display_name or "").strip() or mask_phone(phone)
    phone_text = mask_phone(phone)
    if display_text == phone_text:
        return ["{}: {}".format(single_label, phone_text)]
    return [
        "{}: {}".format(account_label, display_text),
        "{}: {}".format(phone_label, phone_text),
    ]


def get_auth_display(phone):
    expire_text = get_auth(phone) or ""
    if not expire_text:
        return "未授权", "未授权"
    if is_authorized(phone):
        return "已授权", "到期 {}".format(expire_text)
    return "已过期", "已过期 {}".format(expire_text)


def get_account_summary(phone):
    momclub_summary = get_momclub_summary(phone)
    feihe_summary = get_feihe_summary(phone)
    auth_state, auth_text = get_auth_display(phone)
    return {
        "display_name": momclub_summary.get("display_name") or feihe_summary.get("display_name") or mask_phone(phone),
        "phone": mask_phone(phone),
        "auth_state": auth_state,
        "auth_text": auth_text,
        "momclub": momclub_summary,
        "feihe": feihe_summary,
        "projects_text": format_project_binding_text(feihe_summary.get("bound"), momclub_summary.get("bound")),
    }


def get_manage_account_rows():
    rows = []
    for phone in get_user_phones():
        momclub_bound = has_project_binding(phone, "momclub")
        feihe_bound = has_project_binding(phone, "feihe")
        status_text, expire_text = get_auth_display(phone)
        rows.append({
            "phone": phone,
            "display_phone": mask_phone(phone),
            "status_text": status_text,
            "expire_text": expire_text,
            "project_text": format_project_binding_text(feihe_bound, momclub_bound),
        })
    return rows


def get_pending_authorization_phones(phones=None):
    source = phones if phones is not None else get_user_phones()
    return [phone for phone in source if not is_authorized(phone)]


def build_manage_accounts_message():
    rows = get_manage_account_rows()
    points = get_user_points(userid)
    authorized_count = sum(1 for row in rows if row["status_text"] == "已授权")
    lines = [
        "=====账号管理=====",
        "📦 绑定账号: {}个".format(len(rows)),
        "🔐 已授权: {}个".format(authorized_count),
        "💠 当前积分: {}".format(points["total"]),
        "------------------",
    ]
    for index, row in enumerate(rows, 1):
        lines.append("【{}】📱 {}".format(index, row["display_phone"]))
        lines.append("├ 绑定: {}".format(row["project_text"]))
        lines.append("└ 授权: {}".format(row["expire_text"]))
    lines.extend([
        "------------------",
        "快捷操作:",
        "[0] 批量授权全部账号",
        "[9999] 授权未授权账号",
        "[9998] 删除全部账号",
        "------------------",
        "回复序号操作，q 退出",
        "==================",
    ])
    return "\n".join(lines)


def batch_authorize_accounts(phones, title):
    phones = list(dict.fromkeys([phone for phone in phones if phone]))
    if not phones:
        sender.reply("❌ 没有可授权的账号")
        return
    points = get_user_points(userid)
    months_text = read_input("=====批量账号授权=====\n📱 目标: {}\n📦 数量: {}个\n📊 当前积分: {}\n------------------\n请输入授权月数 (1-12)\n回复 q 取消\n==================".format(title, len(phones), points["total"]))
    if not months_text:
        sender.reply("✅ 已取消授权")
        return
    if not months_text.isdigit() or not (1 <= int(months_text) <= 12):
        sender.reply("❌ 月数必须为 1-12 之间的整数")
        return
    months = int(months_text)
    if not handle_authorize_payment("{}（{}个）".format(title, len(phones)), months, len(phones)):
        return
    total_success = 0
    total_sync_fail = 0
    for phone in phones:
        result = complete_authorization(phone, months, userid)
        total_success += 1
    sender.reply("=====授权完成=====\n📱 目标: {}\n✅ 授权成功: {}\n📅 授权月数: {}个月\n==================".format(title, total_success, months))


def query_accounts():
    phones = get_user_phones()
    if not phones:
        sender.reply("❌ 您还没有绑定任何账号，请先发送【星妈会登录】")
        return
    lines = [
        "=====星妈会查询=====",
        "📦 账号: {}个 ｜ 🔐 已授权: {}个".format(
            len(phones),
            sum(1 for phone in phones if is_authorized(phone)),
        ),
        "------------------",
    ]
    for index, phone in enumerate(phones, 1):
        summary = get_account_summary(phone)
        momclub = summary["momclub"]
        feihe = summary["feihe"]
        points = feihe.get("points") if feihe.get("bound") and feihe.get("points") not in ("未绑定", "未知") else momclub.get("points")
        today_earned = get_today_earned(phone)
        pending = momclub.get("pending_tasks", "-") if momclub.get("bound") else "-"
        lines.append("【{}】{} {}".format(index, summary["phone"], summary["projects_text"]))
        lines.append("├ 授权: {} ｜ 积分: {}".format(summary["auth_text"], points))
        lines.append("└ 今日: +{} ｜ 待做: {}".format(today_earned, pending))
        if index != len(phones):
            lines.append("------------------")
    lines.append("==================")
    sender.reply("\n".join(lines))


def choose_account():
    phones = get_user_phones()
    if not phones:
        sender.reply("❌ 您还没有绑定任何账号")
        return None
    lines = ["=====选择账号====="]
    for index, phone in enumerate(phones, 1):
        lines.append("[{}] {} ({})".format(index, mask_phone(phone), get_auth(phone) or "未授权"))
    lines.append("回复序号选择，回复 q 取消")
    lines.append("==================")
    choice = read_input("\n".join(lines))
    if not choice or not choice.isdigit():
        return None
    idx = int(choice) - 1
    return phones[idx] if 0 <= idx < len(phones) else None


def update_momclub_token(phone):
    raw_text = read_input("=====更新星妈会 authorization=====\n请输入新的 authorization\n\n回复 q 取消\n==================")
    if not raw_text:
        sender.reply("✅ 已取消更新")
        return
    ok, result = bind_or_update_momclub_account(raw_text, old_phone=phone)
    if not ok:
        sender.reply("❌ {}".format(result))
        return
    sender.reply("✅ 星妈会 authorization 已更新\n{}\n🎖 等级: {}\n🎁 积分: {}\n{}".format("\n".join(build_account_identity_lines(result["display_name"], result["phone"])), result["grade_name"], result["points"], result["sync_message"] or ""))


def update_feihe_token(phone):
    raw_text = read_input("=====更新飞鹤 access_token=====\n请输入新的 access_token\n\n回复 q 取消\n==================")
    if not raw_text:
        sender.reply("✅ 已取消更新")
        return
    ok, result = bind_or_update_feihe_account(raw_text, old_phone=phone)
    if not ok:
        sender.reply("❌ {}".format(result))
        return
    sender.reply("✅ 飞鹤 token 已更新\n{}\n🎖 等级: {}\n🎁 积分: {}\n{}".format("\n".join(build_account_identity_lines(result["display_name"], result["phone"])), result["grade_name"], result["points"], result.get("sync_message") or ""))


def delete_single_account(phone):
    confirm = read_input("=====删除账号确认=====\n📱 手机: {}\n回复 y 确认删除，回复 q 取消\n==================".format(mask_phone(phone)), 60000)
    if not confirm or confirm.lower() != "y":
        sender.reply("✅ 已取消删除")
        return
    bucket_del_all(BUCKET_TOKEN, phone)
    bucket_del_all(BUCKET_AUTH, phone)
    remove_user_phone(phone, userid)
    sender.reply("✅ 账号已删除")


def delete_all_accounts():
    phones = get_user_phones()
    if not phones:
        sender.reply("❌ 没有可删除的账号")
        return
    confirm = read_input("=====删除全部账号=====\n共 {} 个账号\n回复 y 确认，回复 q 取消\n==================".format(len(phones)), 60000)
    if not confirm or confirm.lower() != "y":
        sender.reply("✅ 已取消删除全部账号")
        return
    for phone in list(phones):
        bucket_del_all(BUCKET_TOKEN, phone)
        bucket_del_all(BUCKET_AUTH, phone)
        remove_user_phone(phone, userid)
    sender.reply("✅ 已删除全部账号")


def execute_account_projects(phone):
    result = {
        "phone": phone,
        "display_phone": mask_phone(phone),
        "projects": [],
        "earned_points": 0,
        "success": False,
    }

    feihe_token = get_feihe_token(phone)
    if feihe_token:
        feihe_result = run_feihe_account(feihe_token)
        if feihe_result.get("new_token"):
            save_feihe_token(phone, feihe_result.get("new_token"))
        result["projects"].append({
            "name": "飞鹤",
            "success": feihe_result.get("success", False),
            "earned_points": feihe_result.get("earned_points", 0),
            "detail": "签到{}，任务{}个，积分 +{}".format(
                "成功" if feihe_result.get("sign_success") else "失败",
                feihe_result.get("completed_tasks", 0),
                feihe_result.get("earned_points", 0),
            ),
        })
        result["earned_points"] += safe_int(feihe_result.get("earned_points", 0), 0)

    token_info = get_token_info(phone)
    authorization = str(token_info.get("authorization") or "").strip()
    if authorization:
        momclub_result = run_momclub_account(authorization)
        result["projects"].append({
            "name": "星妈会",
            "success": momclub_result.get("success", False),
            "earned_points": momclub_result.get("earned_points", 0),
            "detail": "完成任务{}个，积分 +{}".format(
                momclub_result.get("completed_tasks", 0),
                momclub_result.get("earned_points", 0),
            ),
        })
        result["earned_points"] += safe_int(momclub_result.get("earned_points", 0), 0)

    result["success"] = any(project.get("success") for project in result["projects"])
    if result["earned_points"] > 0:
        add_today_earned(phone, result["earned_points"])
    return result


def run_single_account(phone):
    if not is_authorized(phone):
        sender.reply("❌ 当前账号未授权，无法执行任务")
        return
    if not has_project_binding(phone, "feihe") and not has_project_binding(phone, "momclub"):
        sender.reply("❌ 当前账号未绑定任何项目数据")
        return

    sender.reply("⏳ 正在执行账号任务，请稍候...")
    run_result = execute_account_projects(phone)
    if not run_result["projects"]:
        sender.reply("❌ 当前账号没有可执行的项目")
        return

    lines = [
        "=====运行完成=====",
        "📱 手机: {}".format(run_result["display_phone"]),
        "💰 总收益: {} 积分".format(run_result["earned_points"]),
        "------------------",
    ]
    for item in run_result["projects"]:
        lines.append("• {}: {}".format(item["name"], item["detail"]))
    lines.append("==================")
    sender.reply("\n".join(lines))


def get_all_authorized_phones():
    users = bucket_all_keys_merged(BUCKET_USER) or []
    authorized_phones = []
    seen = set()
    for uid in users:
        for phone in get_user_phones(uid):
            if phone not in seen and is_authorized(phone):
                authorized_phones.append(phone)
                seen.add(phone)
    return authorized_phones


def run_all_accounts():
    is_admin = sender.isAdmin()
    if is_admin:
        authorized_phones = get_all_authorized_phones()
    else:
        authorized_phones = [phone for phone in get_user_phones() if is_authorized(phone)]

    if not authorized_phones:
        sender.reply("❌ 没有已授权的账号")
        return

    mode_text = "【管理员模式·全部账号】" if is_admin else "【个人模式】"
    sender.reply("⏳ {}开始一键运行，共 {} 个已授权账号，请耐心等待...".format(mode_text, len(authorized_phones)))

    total_earned = 0
    success_count = 0
    fail_count = 0
    detail_lines = []

    for phone in authorized_phones:
        if not has_project_binding(phone, "feihe") and not has_project_binding(phone, "momclub"):
            fail_count += 1
            detail_lines.append("• {}：未绑定任何项目".format(mask_phone(phone)))
            continue
        run_result = execute_account_projects(phone)
        total_earned += run_result["earned_points"]
        if run_result["success"]:
            success_count += 1
        else:
            fail_count += 1
        project_labels = []
        for item in run_result["projects"]:
            project_labels.append("{}(+{})".format(item["name"], item["earned_points"]))
        detail_lines.append("• {}：{}".format(run_result["display_phone"], " / ".join(project_labels) or "无可执行项目"))
        time.sleep(random.randint(2, 5))

    sender.reply(
        "=====星妈会一键运行=====\n"
        "✅ 成功账号: {}\n"
        "❌ 失败账号: {}\n"
        "💰 总收益: {} 积分\n"
        "------------------\n"
        "{}\n"
        "==================".format(success_count, fail_count, total_earned, "\n".join(detail_lines))
    )


def manage_accounts():
    phones = get_user_phones()
    if not phones:
        sender.reply("❌ 您还没有绑定任何账号，请先发送【星妈会登录】")
        return
    choice = read_input(build_manage_accounts_message())
    if not choice:
        sender.reply("✅ 已退出管理")
        return
    if choice == "0":
        batch_authorize_accounts(phones, "所有账号")
        return
    if choice == "9998":
        delete_all_accounts()
        return
    if choice == "9999":
        pending_phones = get_pending_authorization_phones(phones)
        if not pending_phones:
            sender.reply("✅ 当前没有未授权账号")
            return
        batch_authorize_accounts(pending_phones, "未授权账号")
        return
    if not choice.isdigit():
        sender.reply("❌ 无效选择")
        return
    index = int(choice) - 1
    if index < 0 or index >= len(phones):
        sender.reply("❌ 无效选择")
        return
    phone = phones[index]
    token_info = get_token_info(phone)
    feihe_bound = has_project_binding(phone, "feihe")
    momclub_bound = has_project_binding(phone, "momclub")
    identity_text = "\n".join(build_account_identity_lines(token_info.get("display_name") or mask_phone(phone), phone))
    action = read_input(
        "=====账号操作=====\n"
        "{}\n"
        "🧩 项目: 飞鹤{} / 星妈会{}\n"
        "[1] 授权账号\n"
        "[2] {}星妈会 authorization\n"
        "[3] {}飞鹤 token\n"
        "[4] 运行该账号\n"
        "[5] 删除账号\n"
        "回复序号选择，回复 q 返回\n"
        "==================".format(
            identity_text,
            "✅" if feihe_bound else "❌",
            "✅" if momclub_bound else "❌",
            "更新" if momclub_bound else "绑定",
            "更新" if feihe_bound else "绑定",
        )
    )
    if not action:
        sender.reply("✅ 已返回")
        return
    if action == "1":
        authorize_single_account(phone)
    elif action == "2":
        update_momclub_token(phone)
    elif action == "3":
        update_feihe_token(phone)
    elif action == "4":
        run_single_account(phone)
    elif action == "5":
        delete_single_account(phone)
    else:
        sender.reply("❌ 无效选择")


def admin_authorize():
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限")
        return
    choice = read_input("=====星妈会管理员授权=====\n[1] 单独授权用户\n[2] 一键授权全部用户\n回复序号选择，回复 q 取消\n==================")
    if not choice:
        sender.reply("✅ 已取消管理员授权")
        return
    users = bucket_all_keys_merged(BUCKET_USER) or []
    if not users:
        sender.reply("❌ 当前没有任何绑定用户")
        return
    months_text = read_input("请输入授权月数 (1-12)，回复 q 取消")
    if not months_text or not months_text.isdigit() or not (1 <= int(months_text) <= 12):
        sender.reply("❌ 月数必须为 1-12 之间的整数")
        return
    months = int(months_text)
    total_success = 0
    if choice == "1":
        target_userid = read_input("请输入目标用户ID，回复 q 取消")
        if not target_userid:
            sender.reply("✅ 已取消操作")
            return
        phones = get_user_phones(target_userid)
        if not phones:
            sender.reply("❌ 该用户没有绑定任何账号")
            return
        for phone in phones:
            result = complete_authorization(phone, months, target_userid)
            total_success += 1
    elif choice == "2":
        for target_userid in users:
            for phone in get_user_phones(target_userid):
                result = complete_authorization(phone, months, target_userid)
                total_success += 1
    else:
        sender.reply("❌ 无效选择")
        return
    sender.reply("=====授权完成=====\n✅ 授权成功: {}\n==================".format(total_success))


def admin_backend():
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限")
        return

    choice = read_input(
        "=====星妈会后台=====\n"
        "[1] 授权管理\n"
        "[2] 清理账号\n"
        "回复序号选择，回复 q 取消\n"
        "==================",
        60000,
    )
    if not choice:
        sender.reply("✅ 已退出后台")
        return
    if choice == "1":
        admin_authorize()
        return
    if choice == "2":
        clean_accounts()
        return
    sender.reply("❌ 无效选择")


def clean_accounts():
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限")
        return
    users = bucket_all_keys_merged(BUCKET_USER) or []
    if not users:
        sender.reply("❌ 当前没有任何绑定用户")
        return
    cleaned_count = 0
    kept_count = 0
    for user_id in users:
        valid_phones = []
        for phone in get_user_phones(user_id):
            if (has_project_binding(phone, "feihe") or has_project_binding(phone, "momclub")) and is_authorized(phone):
                valid_phones.append(phone)
                kept_count += 1
                continue
            bucket_del_all(BUCKET_TOKEN, phone)
            bucket_del_all(BUCKET_AUTH, phone)
            cleaned_count += 1
        save_user_phones(valid_phones, user_id)
    sender.reply("=====清理完成=====\n✅ 保留账号: {}\n🧹 清理账号: {}\n==================".format(kept_count, cleaned_count))


def show_tutorial():
    sender.reply(
        "=====星妈会教程=====\n"
        "📌 登录格式\n"
        "飞鹤+星妈会：access_token#authorization\n"
        "仅飞鹤：access_token\n"
        "仅星妈会：authorization\n"
        "批量提交：每行一条\n"
        "------------------\n"
        "📌 常用指令\n"
        "星妈会登录：绑定或更新凭证\n"
        "星妈会查询：查看绑定、积分、授权\n"
        "星妈会管理：单账号授权/更新/删除/运行\n"
        "星妈会一键运行：运行全部已授权账号\n"
        "星妈会后台：管理员授权和清理\n"
        "------------------\n"
        "📌 抓包说明\n"
        "星妈会 #小程序://星妈会/BhVspEnnMsRvDgz\n"
        "飞鹤  #小程序://飞鹤丨北纬47度好物/QTaS9v3oLMMGxpx\n"
        "=================="
    )


def cron_run_all():
    authorized_phones = get_all_authorized_phones()
    if not authorized_phones:
        return
    total_earned = 0
    success_count = 0
    fail_count = 0
    detail_lines = []
    for phone in authorized_phones:
        if not has_project_binding(phone, "feihe") and not has_project_binding(phone, "momclub"):
            fail_count += 1
            detail_lines.append("• {}：未绑定任何项目".format(mask_phone(phone)))
            continue
        run_result = execute_account_projects(phone)
        total_earned += run_result["earned_points"]
        if run_result["success"]:
            success_count += 1
        else:
            fail_count += 1
        project_labels = []
        for item in run_result["projects"]:
            project_labels.append("{}(+{})".format(item["name"], item["earned_points"]))
        detail_lines.append("• {}：{}".format(run_result["display_phone"], " / ".join(project_labels) or "无可执行项目"))
        time.sleep(random.randint(2, 5))
    sender.reply(
        "=====星妈会定时任务=====\n"
        "⏰ 时间: {}\n"
        "✅ 成功: {}\n"
        "❌ 失败: {}\n"
        "💰 总收益: {} 积分\n"
        "------------------\n"
        "{}\n"
        "==================".format(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            success_count,
            fail_count,
            total_earned,
            "\n".join(detail_lines),
        )
    )


def xmyx_cron_check():
    """定时检测授权过期推送"""
    users = bucket_all_keys_merged(BUCKET_USER) or []
    today = str(today_date())
    for uid in users:
        try:
            phones = get_user_phones(uid)
            for phone in phones:
                try:
                    auth_expire = get_auth(phone)
                    display_phone = mask_phone(phone)
                    if not auth_expire or auth_expire <= today:
                        push_msg = f"""
=====星妈会账号通知=====
📱 账号: {display_phone}
⏰ 定时检测提醒
------------------
❌ 授权已过期
💡 请及时续费授权
=================="""
                        for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                            try:
                                middleware.push(platform, '', uid, '', push_msg)
                            except:
                                pass
                    else:
                        try:
                            expire_date = datetime.strptime(auth_expire, '%Y-%m-%d').date()
                            days_left = (expire_date - datetime.now().date()).days
                            if days_left <= 3:
                                push_msg = f"""
=====星妈会账号通知=====
📱 账号: {display_phone}
⏰ 定时检测提醒
------------------
⚠️ 授权即将到期
📅 到期时间: {auth_expire}
⏳ 剩余天数: {days_left}天
💡 请及时续费授权
=================="""
                                for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                                    try:
                                        middleware.push(platform, '', uid, '', push_msg)
                                    except:
                                        pass
                        except:
                            pass
                except:
                    continue
        except:
            continue


try:
    usermessage = sender.getMessage()
except AttributeError:
    usermessage = ""

try:
    imtype = sender.getImtype()
except AttributeError:
    imtype = ""

if imtype == 'fake':
    xmyx_cron_check()
elif not usermessage:
    cron_run_all()
elif re.search(r"星妈会登录", usermessage):
    bind_account()
elif re.search(r"星妈会管理", usermessage):
    manage_accounts()
elif re.search(r"星妈会查询", usermessage):
    query_accounts()
elif re.search(r"星妈会一键运行", usermessage):
    run_all_accounts()
elif re.search(r"星妈会教程", usermessage):
    show_tutorial()
elif re.search(r"星妈会后台$", usermessage):
    admin_backend()
else:
    sender.setContinue()
