#[title: 顺易充（新）]
# [rule: ^(顺易充|syc)(登录|登陆|绑定|管理|查询|授权|运行|一键运行|清理|刷新|一键刷新)$]
# [disable:true]
# [platform: qq,wx]
# [public:true]
# [open_source: false]
# [class: 工具类]
# [version: 1.1.7]
# [price: 88]
# [admin: false]
# [icon: https://i.mji.rip/2025/07/11/5132e8c191f16ac574c0328105061ec4.jpeg]
# [author: huawei]
# [service: 1603960061]
# [description: 顺易充APP插件，支持短信登录、积分支付、账号管理、任务执行，账号token一键刷新，推荐使用 autman-huawei 模块重铸版<br>更新v1.1.7屏蔽视频任务，仅保留签到功能
# [param: {"required":false,"key":"G_SYC.zsm","name":"收款码","placeholder":"http://example.com/pay.jpg","desc":"微信赞赏码/收款码链接，不填则使用默认支付方式"}]
# [param: {"required":false,"key":"G_SYC.price","name":"月费价格","placeholder":"0.88","value":"0.88","desc":"单个账号每月授权价格"}]
# [param: {"required":false,"key":"G_SYC.points_per_month","name":"积分/月","placeholder":"100","value":"100","desc":"一个账号每月所需积分数量"}]
# [param: {"required":false,"key":"G_SYC.concurrent_count","name":"并发数量","placeholder":"3","value":"3","desc":"任务执行时的并发线程数量"}]
# [param: {"required":false,"key":"G_SYC.admin_ids","name":"管理员ID","placeholder":"wxid_xxx1,wxid_xxx2","desc":"多个管理员ID使用英文逗号分隔"}]
# [param: {"required":false,"key":"G_SYC.proxy_api","name":"代理API","placeholder":"http://user:pass@ip:port","desc":"填写代理接口或固定代理地址，不填则不启用代理"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_switch","bool":true,"name":"码支付开关(全局)","desc":"勾选启用码支付功能"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_gateway","bool":false,"placeholder":"https://pay.example.com","name":"码支付网关(全局)","desc":"支付网关地址"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_pid","bool":false,"placeholder":"10001","name":"商户ID(全局)","desc":"支付平台的商户ID"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_key","bool":false,"placeholder":"your_pay_key","name":"商户密钥(全局)","desc":"支付平台的商户密钥"}]
# [param: {"required":false,"key":"dd_sign_config.pay_types","bool":false,"placeholder":"alipay,wxpay,qqpay","value":"alipay,wxpay,qqpay","name":"支付方式(全局)","desc":"码支付方式，多个用英文逗号分隔"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_notify_url","bool":false,"placeholder":"https://example.com/notify","name":"回调地址(全局)","desc":"支付回调通知地址，可选"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_return_url","bool":false,"placeholder":"https://example.com/return","name":"返回地址(全局)","desc":"支付完成返回地址，可选"}]
import requests
import json
import time
import hashlib
import uuid
import re
import warnings
import random
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import middleware
from Crypto.Cipher import DES3
from Crypto.Util.Padding import pad
from urllib.parse import quote
import base64
try:
    from autman_huawei import MaPayClient, generate_qrcode_url, get_pay_config
except ImportError:
    MaPayClient = None
    generate_qrcode_url = None
    get_pay_config = None
try:
    from urllib3.exceptions import InsecureRequestWarning
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
except Exception:
    pass
class _FallbackSender:
    def getMessage(self):
        return ""
    def reply(self, *_args, **_kwargs):
        return None
    def input(self, *_args, **_kwargs):
        return None
    def replyImage(self, *_args, **_kwargs):
        return None
    def waitPay(self, *_args, **_kwargs):
        return "q"
    def listen(self, *_args, **_kwargs):
        return ""
    def isAdmin(self):
        return False
    def getUserID(self):
        return ""
    def setContinue(self):
        return None
try:
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
except Exception:
    senderID = ""
    sender = _FallbackSender()
    userid = ""

BUCKET_CONFIG = "G_SYC"
BUCKET_USER = "G_SYC_user"
BUCKET_TOKEN = "G_SYC_token"
BUCKET_AUTH = "G_SYC_AUT"
BUCKET_AUTH_STATE = "G_SYC_auth_state"
BUCKET_TOKEN_STATUS = "G_SYC_token_status"
BUCKET_RECORDS = "G_SYC_records"
DEFAULT_PAY_TYPE_NAMES = {
    "alipay": "支付宝",
    "wxpay": "微信支付",
    "qqpay": "QQ支付",
}
PAY_POLL_TIMES = 60
PAY_POLL_INTERVAL_MS = 5000

# 积分支付并发锁
_points_payment_lock = threading.Lock()


def get_bucket_config_value(key: str, default=""):
    try:
        value = middleware.bucketGet(bucket=BUCKET_CONFIG, key=key)
        return default if value in [None, ""] else value
    except Exception:
        return default


def parse_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def parse_pay_types(raw_value) -> dict:
    if isinstance(raw_value, dict):
        result = {}
        for key, name in raw_value.items():
            pay_key = str(key or "").strip()
            if not pay_key:
                continue
            pay_name = str(name or "").strip()
            result[pay_key] = pay_name or DEFAULT_PAY_TYPE_NAMES.get(pay_key, pay_key)
        return result
    text = str(raw_value or "").strip()
    if not text:
        return {}
    result = {}
    for item in re.split(r"[,，\n]+", text):
        piece = str(item or "").strip()
        if not piece:
            continue
        pay_key = piece
        pay_name = ""
        for sep in (":", "=", "|"):
            if sep in piece:
                pay_key, pay_name = piece.split(sep, 1)
                break
        pay_key = str(pay_key or "").strip()
        if not pay_key:
            continue
        pay_name = str(pay_name or "").strip()
        result[pay_key] = pay_name or DEFAULT_PAY_TYPE_NAMES.get(pay_key, pay_key)
    return result


def get_user_phones(user_id=None) -> list:
    if not user_id:
        user_id = userid
    try:
        phones_json = middleware.bucketGet(BUCKET_USER, user_id) or "[]"
        phones = json.loads(phones_json)
        if not isinstance(phones, list):
            return []
        return [str(phone).strip() for phone in phones if str(phone).strip()]
    except Exception:
        return []


def get_auth(phone: str) -> str:
    if not phone:
        return ""
    try:
        return middleware.bucketGet(BUCKET_AUTH, phone) or ""
    except Exception:
        return ""



def build_auth_status(phone: str) -> dict:
    expire_time = get_auth(phone)
    if not expire_time:
        return {"is_authorized": False, "expire_time": ""}
    try:
        expire_date = datetime.strptime(expire_time, "%Y-%m-%d").date()
        if expire_date < datetime.now().date():
            return {"is_authorized": False, "expire_time": ""}
        return {"is_authorized": True, "expire_time": expire_time}
    except Exception:
        return {"is_authorized": False, "expire_time": ""}



def is_authorized(phone: str) -> bool:
    return build_auth_status(phone).get("is_authorized", False)


def get_proxy_api() -> str:
    """获取代理API配置"""
    return get_bucket_config_value("proxy_api", "")
proxy_url = get_proxy_api()
IS_PROXY = bool(proxy_url)
if IS_PROXY:
    print(f"[INFO] 代理模式: 已启用")
    print(f"[INFO] 代理API: {proxy_url}")
else:
    print(f"[INFO] 代理模式: 未启用")
proxy_cache = {}
proxy_cache_time = {}
proxy_lock_dict = threading.Lock()
PROXY_CACHE_TTL = 300
def get_proxy(force_new=False, account_key=None):
    if not IS_PROXY or not proxy_url:
        return None
    current_time = time.time()
    if account_key and not force_new:
        with proxy_lock_dict:
            if account_key in proxy_cache:
                cache_time = proxy_cache_time.get(account_key, 0)
                if current_time - cache_time < PROXY_CACHE_TTL:
                    return proxy_cache[account_key]
                else:
                    del proxy_cache[account_key]
                    del proxy_cache_time[account_key]
    try:
        response = requests.get(proxy_url, timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            if "请先添加白名单" in ip:
                print(f"[WARNING] 代理服务异常：请先添加白名单")
                return None
            proxy_dict = {"http": ip, "https": ip}
            if account_key:
                with proxy_lock_dict:
                    expired_keys = [
                        k
                        for k, t in proxy_cache_time.items()
                        if current_time - t >= PROXY_CACHE_TTL
                    ]
                    for k in expired_keys:
                        proxy_cache.pop(k, None)
                        proxy_cache_time.pop(k, None)
                    proxy_cache[account_key] = proxy_dict
                    proxy_cache_time[account_key] = current_time
            print(f"[INFO] 获取代理成功: {ip}")
            return proxy_dict
        else:
            print(f"[WARNING] 代理API响应异常: {response.status_code}")
            return None
    except Exception as e:
        print(f"[WARNING] 获取代理失败: {str(e)}")
        return None
def request_with_retry(method, url, max_retries=3, account_key=None, **kwargs):
    if (
        "headers" in kwargs
        and kwargs["headers"]
        and "_account_key" in kwargs["headers"]
    ):
        if account_key is None:
            account_key = kwargs["headers"].get("_account_key")
        clean_headers = {
            k: v for k, v in kwargs["headers"].items() if k != "_account_key"
        }
        kwargs["headers"] = clean_headers
    current_proxy = None
    for attempt in range(max_retries):
        try:
            if IS_PROXY:
                if attempt == 0:
                    current_proxy = get_proxy(force_new=False, account_key=account_key)
                else:
                    current_proxy = get_proxy(force_new=True, account_key=account_key)
                if current_proxy:
                    kwargs["proxies"] = current_proxy
                else:
                    kwargs["proxies"] = None
            if method.upper() == "GET":
                response = requests.get(url, **kwargs)
            else:
                response = requests.post(url, **kwargs)
            return response
        except (
            requests.exceptions.ProxyError,
            requests.exceptions.ConnectionError,
        ) as e:
            print(f"[WARNING] 代理连接错误: {str(e)[:100]}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                print(f"[ERROR] 代理请求失败，已达最大重试次数")
                raise
        except requests.exceptions.Timeout:
            print(f"[WARNING] 请求超时")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                print(f"[ERROR] 请求超时，已达最大重试次数")
                raise
        except Exception as e:
            print(f"[ERROR] 请求异常: {str(e)[:100]}")
            raise
    return None
def get_random_region_pair() -> tuple:
    pairs = [
        ("0551", "340100"),
        ("025", "320100"),
        ("021", "310100"),
        ("010", "110100"),
        ("020", "440100"),
        ("0755", "440300"),
        ("0756", "440400"),
        ("0757", "440600"),
        ("0769", "441900"),
        ("0571", "330100"),
        ("0574", "330200"),
        ("0512", "320500"),
        ("0510", "320200"),
        ("028", "510100"),
        ("023", "500100"),
        ("029", "610100"),
        ("027", "420100"),
        ("0371", "410100"),
        ("0731", "430100"),
        ("0791", "360100"),
        ("0591", "350100"),
        ("0592", "350200"),
        ("0531", "370100"),
        ("0532", "370200"),
        ("024", "210100"),
        ("0411", "210200"),
        ("0431", "220100"),
        ("0451", "230100"),
        ("0871", "530100"),
        ("0851", "520100"),
        ("0771", "450100"),
        ("0898", "460100"),
        ("0899", "460200"),
        ("0351", "140100"),
        ("0311", "130100"),
        ("0553", "340200"),
        ("0519", "320400"),
        ("0518", "320700"),
        ("0710", "420600"),
    ]
    return random.choice(pairs)
def get_random_user_agent() -> str:
    ua_types = [
        lambda: f"okhttp/{random.choice(['4.9.0', '4.9.1', '4.9.3', '4.10.0', '4.11.0', '4.12.0'])}",
        lambda: f"CSPGCharge/{random.choice(['5.6.0', '5.7.0', '5.8.0'])} (iPhone; iOS {random.choice(['16.6', '17.0', '17.1', '17.6'])}; Scale/{random.choice(['2.00', '3.00'])})",
        lambda: f"Mozilla/5.0 (Linux; Android {random.randint(9, 14)}; {random.choice(['OPPO R9s', 'HUAWEI P30', 'Xiaomi MI 10', 'Samsung SM-G973F', 'vivo V2047A'])} Build/QP1A.{random.randint(190000, 210000)}.{random.randint(100, 999)}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{random.randint(90, 120)}.0.{random.randint(4000, 5000)}.{random.randint(100, 200)} Mobile Safari/537.36",
    ]
    return random.choice(ua_types)()
AD_HEADERS = {
    "Content-Type": "application/json; charset=utf-8",
    "Accept-Encoding": "gzip",
    "Token": "245DC3B3-A2D8-0993-9ECD-269B5F19B5BA",
}
AD_POSITION_PATTERNS = {
    "kuaishou_standard": "9253000",
    "kuaishou_premium": "9253002",
    "kuaishou_short": "925300",
}
VALID_ADV_ID = "b6286f0d6267aa82"
class AdSystemClient:
    def __init__(self):
        self.base_url = "https://api.wxcjgg.cn"
        self.session = requests.Session()
        self.session.headers.update(AD_HEADERS)
        self.session.headers["User-Agent"] = get_random_user_agent()
        self.adv_id = VALID_ADV_ID
        self.max_attempts = 10
    def generate_single_ad_position(self, user_id: str = "13397537") -> str:
        import random
        for attempt in range(self.max_attempts):
            try:
                pattern_type = random.choice(list(AD_POSITION_PATTERNS.keys()))
                pattern = AD_POSITION_PATTERNS[pattern_type]
                if pattern == "925300":
                    suffix = random.randint(0, 999)
                    candidate = f"{pattern}{suffix:03d}"
                else:
                    suffix = random.randint(0, 999)
                    candidate = f"{pattern}{suffix:03d}"
                if self.test_ad_position(candidate, user_id):
                    return candidate
                else:
                    time.sleep(0.1)
            except Exception as e:
                continue
        return None
    def test_ad_position(
        self,
        position: str,
        user_id: str = "13397537",
        device_id: str = "39a40068bc08bfe9",
    ) -> bool:
        try:
            request_data = {
                "cpm": "2000",
                "sdk_code": 30303,
                "system_name": "14",
                "dev_id": device_id,
                "ad_id": self.adv_id,
                "sdk_v": "a.3.3.3",
                "u_id": user_id,
                "app_v": "5.7.3",
                "system_version": 34,
                "plat": "ks",
                "app_id": "31123d906f8255c6",
                "r_id": str(uuid.uuid4()),
                "oaid": "",
                "p_id": position,
                "m_id": 0,
                "app_code": 5703,
            }
            response = self.session.post(
                f"{self.base_url}/rep/click", json=request_data, timeout=5
            )
            return response.text.strip() == "success"
        except Exception:
            return False
    def _generate_sign(self, data: dict) -> str:
        sign_str = f"{data['adv_id']}{data['request_id']}{data['timestamp']}{data['user_id']}36z6QhAXaCwD"
        return hashlib.md5(sign_str.encode("utf-8")).hexdigest()
    def send_rewards_callback(self, user_id: str, device_id: str) -> bool:
        try:
            extend_data = {
                "type": "1216",
                "loginChannel": "01",
                "taskNo": "20221231",
                "content": "顺易充192d96",
            }
            timestamp = int(time.time())
            request_id = str(uuid.uuid4())
            request_data = {
                "extend": json.dumps(extend_data, ensure_ascii=False),
                "user_id": user_id,
                "adv_id": self.adv_id,
                "request_id": request_id,
                "deviceId": device_id,
                "timestamp": timestamp,
            }
            request_data["sign"] = self._generate_sign(request_data)
            response = self.session.post(
                f"{self.base_url}/rewards/callback", json=request_data, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("code") == 0
        except Exception as e:
            return False
    def report_ad_click(self, position: str, user_id: str, device_id: str) -> bool:
        try:
            request_data = {
                "cpm": "2000",
                "sdk_code": 30303,
                "system_name": "14",
                "dev_id": device_id,
                "ad_id": self.adv_id,
                "sdk_v": "a.3.3.3",
                "u_id": user_id,
                "app_v": "5.7.3",
                "system_version": 34,
                "plat": "ks",
                "app_id": "31123d906f8255c6",
                "r_id": str(uuid.uuid4()),
                "oaid": "",
                "p_id": position,
                "m_id": 0,
                "app_code": 5703,
            }
            response = self.session.post(
                f"{self.base_url}/rep/click", json=request_data, timeout=10
            )
            return response.text.strip() == "success"
        except Exception:
            return False
def extract_user_id_from_token(token: str) -> str:
    try:
        if token.startswith("Bearer "):
            token = token[7:]
        parts = token.split(".")
        if len(parts) >= 2:
            payload = parts[1]
            missing_padding = len(payload) % 4
            if missing_padding:
                payload += "=" * (4 - missing_padding)
            decoded = base64.b64decode(payload)
            payload_data = json.loads(decoded.decode("utf-8"))
            for field in ["custId", "userId", "user_id", "id", "sub"]:
                if field in payload_data:
                    return str(payload_data[field])
    except Exception as e:
        print(f"    ⚠️ 从token提取用户ID失败: {e}")
    return "13397537"
def generate_device_id_from_phone(phone: str) -> str:
    try:
        phone_hash = hashlib.md5(phone.encode("utf-8")).hexdigest()
        return phone_hash[:16]
    except:
        return "39a40068bc08bfe9"
def complete_enhanced_video_task_plugin(headers, phone):
    try:
        config = get_config()
        video_count = config.get("video_count", 6)
        watch_time = config.get("watch_time", 25)
        ad_client = AdSystemClient()
        token = headers.get("authorization", "")
        user_id = extract_user_id_from_token(token)
        device_id = generate_device_id_from_phone(phone)
        account_key = headers.get("_account_key")  # 从 headers 提取账号标识
        url = "https://app.wodeev.com/bil-front/v2.0/activity/getWelfare"
        successful_claims = 0
        attempt_count = 0
        max_attempts = 10
        task_status_url = "https://app.wodeev.com/bil-front/v2.0/activity/getWelfareTask?taskNo=20221231"
        try:
            status_response = request_with_retry(
                "GET",
                task_status_url,
                headers=headers,
                timeout=10,
                verify=False,
                account_key=account_key,
            )
            status_data = status_response.json()
            if status_data.get("ret") == 200:
                task_list = status_data.get("taskList", [])
                for task in task_list:
                    if task.get("actType") == "1216":
                        reward_status = task.get("rewardStatus", "00")
                        status_text = {
                            "00": "可开始",
                            "01": "已完成，等待领取",
                            "02": "已领取完成",
                        }.get(reward_status, "未知状态")
                        if reward_status == "02":
                            return f"视频任务今日已完成 6/6", True
                        elif reward_status == "01":
                            claimed_count = (
                                0  # 初始化计数器，避免循环未执行时变量未定义
                            )
                            for direct_claim in range(video_count):
                                try:
                                    direct_payload = {
                                        "type": "1216",
                                        "taskNo": "20221231",
                                    }
                                    direct_resp = request_with_retry(
                                        "POST",
                                        url,
                                        headers=headers,
                                        json=direct_payload,
                                        timeout=10,
                                        verify=False,
                                        account_key=account_key,
                                    )
                                    direct_data = direct_resp.json()
                                    if direct_data.get("ret") == 200:
                                        claimed_count = direct_claim + 1
                                        time.sleep(2)
                                    else:
                                        break
                                except Exception:
                                    break
                            return (
                                f"视频任务直接领取完成 {min(claimed_count, video_count)}/{video_count}",
                                True,
                            )
                        break
        except Exception:
            pass
        while successful_claims < video_count and attempt_count < max_attempts:
            attempt_count += 1
            try:
                direct_payload = {"type": "1216", "taskNo": "20221231"}
                direct_resp = request_with_retry(
                    "POST",
                    url,
                    headers=headers,
                    json=direct_payload,
                    timeout=10,
                    verify=False,
                    account_key=account_key,
                )
                direct_data = direct_resp.json()
                if direct_data.get("ret") == 200:
                    successful_claims += 1
                    if successful_claims < video_count:
                        time.sleep(3)
                    continue
                elif "该用户已经存在完成的任务,请先领取" in direct_data.get("msg", ""):
                    successful_claims += 1
                    if successful_claims < video_count:
                        time.sleep(3)
                    continue
                watch_payload = {
                    "type": "1216",
                    "taskStage": "01",
                    "taskNo": "20221231",
                }
                watch_response = request_with_retry(
                    "POST",
                    url,
                    headers=headers,
                    json=watch_payload,
                    timeout=10,
                    verify=False,
                    account_key=account_key,
                )
                watch_data = watch_response.json()
                if watch_data.get("ret") == 200:
                    selected_position = ad_client.generate_single_ad_position(user_id)
                    if selected_position:
                        for i in range(watch_time):
                            if i == watch_time // 2:
                                ad_client.report_ad_click(
                                    selected_position, user_id, device_id
                                )
                            time.sleep(1)
                        ad_client.send_rewards_callback(user_id, device_id)
                    else:
                        time.sleep(watch_time)
                    for retry in range(3):
                        try:
                            reward_payload = {"type": "1216", "taskNo": "20221231"}
                            reward_response = request_with_retry(
                                "POST",
                                url,
                                headers=headers,
                                json=reward_payload,
                                timeout=10,
                                verify=False,
                                account_key=account_key,
                            )
                            reward_data = reward_response.json()
                            ret_code = reward_data.get("ret", "未知")
                            msg = reward_data.get("msg", "无返回信息")
                            if ret_code == 200:
                                successful_claims += 1
                                if successful_claims >= video_count:
                                    break
                                time.sleep(3)
                                break
                            elif ret_code == 400 and ("超过" in msg or "已完成" in msg):
                                successful_claims = video_count
                                break
                            elif "未找可领取" in msg and retry < 2:
                                time.sleep(5)
                                continue
                            else:
                                break
                        except Exception as e:
                            break
                else:
                    time.sleep(5)
            except Exception as e:
                time.sleep(5)
        return (
            f"完成视频任务 {successful_claims}/{video_count} (增强模式)",
            successful_claims > 0,
        )
    except Exception as e:
        return "视频任务异常", False
def get_task_headers():
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "content-type": "application/json;charset=utf-8",
        "loginchannel": "15",
        "client-version": "5.6.0",
        "accept-language": "zh-Hans-CN;q=1",
        "lang": "1",
        "x-client-code": "01",
    }
def get_config():
    try:
        price_str = get_bucket_config_value("price", "0.88")
        price = float(price_str) if price_str.replace(".", "", 1).isdigit() else 0.88
        payment_config = get_pay_config() if callable(get_pay_config) else {}
        if not isinstance(payment_config, dict):
            payment_config = {}
        pay_types = payment_config.get("pay_types") or {}
        if not pay_types:
            legacy_types = (
                middleware.bucketGet("dd_sign_config", "pay_types")
                or middleware.bucketGet("dd_sign_config", "ma_pay_type")
                or ""
            )
            pay_types = parse_pay_types(legacy_types)
        zsm = (
            get_bucket_config_value("zsm", "")
            or payment_config.get("zsm")
            or middleware.bucketGet("G_SKM", "zsm")
            or middleware.bucketGet("dd_sign_config", "zsm")
            or ""
        )
        points_per_month_str = get_bucket_config_value("points_per_month", "100")
        points_per_month = (
            int(points_per_month_str) if points_per_month_str.isdigit() else 100
        )
        concurrent_count_str = get_bucket_config_value("concurrent_count", "3")
        concurrent_count = (
            int(concurrent_count_str) if concurrent_count_str.isdigit() else 3
        )
        concurrent_count = max(1, min(concurrent_count, 10))
        admin_ids = get_bucket_config_value("admin_ids", "")
        ma_pay_switch = parse_bool(
            payment_config.get("ma_pay_switch")
            or middleware.bucketGet("dd_sign_config", "ma_pay_switch")
            or "false"
        )
        video_count = 6
        wait_time = 30
        watch_time = 25
        use_enhanced_ads = True
        return {
            "price": price,
            "zsm": zsm,
            "points_per_month": points_per_month,
            "video_count": video_count,
            "wait_time": wait_time,
            "watch_time": watch_time,
            "concurrent_count": concurrent_count,
            "use_enhanced_ads": use_enhanced_ads,
            "admin_ids": admin_ids,
            "ma_pay_switch": ma_pay_switch,
            "pay_types": pay_types,
        }
    except Exception as e:
        sender.reply(f"❌ 配置获取失败: {str(e)}")
        return {
            "price": 0.88,
            "zsm": "",
            "points_per_month": 100,
            "video_count": 6,
            "wait_time": 30,
            "watch_time": 25,
            "concurrent_count": 3,
            "use_enhanced_ads": True,
            "admin_ids": "",
            "ma_pay_switch": False,
            "pay_types": {},
        }
def is_syc_admin():
    if sender.isAdmin():
        return True
    admin_ids_str = get_bucket_config_value("admin_ids", "")
    if not admin_ids_str:
        return False
    admin_ids = [aid.strip() for aid in admin_ids_str.split(",") if aid.strip()]
    return userid in admin_ids
def parse_account_selection(choice_str: str, max_index: int) -> list:

    if not choice_str or not choice_str.strip():
        return None
    choice_str = choice_str.strip()
    selected_indices = set()
    try:
        parts = choice_str.split(",")
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                range_parts = part.split("-")
                if len(range_parts) != 2:
                    return None
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                if start < 1 or end < 1 or start > max_index or end > max_index:
                    return None
                if start > end:
                    return None
                for i in range(start - 1, end):
                    selected_indices.add(i)
            else:
                num = int(part)
                if num < 1 or num > max_index:
                    return None
                selected_indices.add(num - 1)
        return sorted(list(selected_indices))
    except (ValueError, AttributeError):
        return None
def md5_encrypt(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()
def triple_des_encrypt(data: str, key_base64: str) -> str:
    try:
        key_bytes = base64.b64decode(key_base64)
        cipher = DES3.new(key_bytes, DES3.MODE_ECB)
        data_bytes = data.encode("utf-8")
        padded_data = pad(data_bytes, DES3.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        print(f"❌ 3DES加密错误: {e}")
        return None
def build_signed_params(keyword: str, value: str) -> tuple:
    random_num = str(random.randint(100, 999))
    d0, d1, d2 = random_num[0], random_num[1], random_num[2]
    timestamp_ms = int(time.time() * 1000)
    raw = f"{d0}{keyword}{d1}{value}{d2}{timestamp_ms}{random_num}"
    md5_hash = md5_encrypt(raw)
    key_base64 = "+7+hkq4l97VMgGHTufKDEHzfH8FzQ0aw"
    sign = triple_des_encrypt(md5_hash, key_base64)
    timestamp = str(timestamp_ms) + random_num
    return timestamp, sign, raw, md5_hash
def send_sms_code(mobile: str) -> dict:
    """
    发送短信验证码
    Args:
        mobile: 手机号
    Returns:
        响应结果字典，失败返回None
    """
    try:
        account_key = f"acc_{mobile}"
        timestamp, encrypted, _, _ = build_signed_params("mobile", mobile)
        if not encrypted:
            return None
        sign_url_encoded = quote(encrypted)
        url = f"https://app.wodeev.com/cst-front/v2.0/sms?verifyType=05&mobile={mobile}&timestamp={timestamp}&sign={sign_url_encoded}&countryAreaTelCode=86"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": "Bearer",
            "client-version": "5.10.0",
            "lang": "1",
            "loginChannel": "07",
            "Origin": "https://www.wodeev.com",
            "Referer": "https://www.wodeev.com/",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "X-Requested-With": "com.longshine.nanwang.electric.charge",
        }
        print(f"[INFO] 发送短信验证码到: {mobile}")
        response = request_with_retry(
            "GET",
            url,
            headers=headers,
            timeout=30,
            verify=False,
            account_key=account_key,
        )
        if response.status_code == 200:
            result = response.json()
            print(f"[INFO] 短信API响应: {result}")
            if result and result.get("ret") == 200:
                print(f"[SUCCESS] 短信发送成功: {result.get('msg', '')}")
                return result
            else:
                print(
                    f"[ERROR] 短信发送失败: ret={result.get('ret')}, msg={result.get('msg')}"
                )
                return None
        else:
            print(f"[ERROR] 短信API请求失败: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"[ERROR] 发送短信异常: {str(e)}")
        return None
def login_with_sms_code(mobile: str, code: str) -> dict:
    try:
        time.sleep(random.uniform(1, 3))
        account_key = f"acc_{mobile}"
        url = "https://app.wodeev.com/cst-front/open/v3.0/login"
        city_code, province_code = get_random_region_pair()
        data = {
            "cityCode": city_code,
            "countryCode": "中国",
            "loginType": "02",
            "mobile": mobile,
            "verifyCode": code,
            "countryAreaTelCode": "86",
            "provinceCode": province_code,
            "rsaFlag": "1",
            "deviceId": "",
            "deviceModel": "Android",
            "systemVersion": "Android 13",
        }
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Authorization": "",
            "loginChannel": "07",
            "client-version": "5.10.0",
            "lang": "1",
            "User-Agent": "okhttp/4.9.0",
        }
        response = request_with_retry(
            "POST",
            url,
            json=data,
            headers=headers,
            verify=False,
            timeout=15,
            account_key=account_key,
        )
        if response.status_code != 200:
            return {
                "success": False,
                "message": f"登录HTTP异常: {response.status_code}",
                "token": "",
                "refreshToken": "",
                "custInfo": None,
            }
        if not response.text or response.text.strip() == "":
            return {
                "success": False,
                "message": "登录接口返回为空",
                "token": "",
                "refreshToken": "",
                "custInfo": None,
            }
        try:
            res_data = response.json()
        except json.JSONDecodeError:
            return {
                "success": False,
                "message": "登录接口返回非JSON",
                "token": "",
                "refreshToken": "",
                "custInfo": None,
            }
        if res_data.get("ret") == 200:
            return {
                "success": True,
                "message": "登录成功",
                "token": res_data.get("token", ""),
                "refreshToken": res_data.get("refreshToken", ""),
                "custInfo": res_data.get("custInfo"),
            }
        else:
            return {
                "success": False,
                "message": f"登录失败: {res_data.get('msg', '未知错误')}",
                "token": "",
                "refreshToken": "",
                "custInfo": None,
            }
    except Exception as e:
        return {
            "success": False,
            "message": f"登录异常: {str(e)}",
            "token": "",
            "refreshToken": "",
            "custInfo": None,
        }
def get_user_points(user_id=None):
    if not user_id:
        user_id = userid
    points = middleware.bucketGet("dd_sign_coin", user_id) or "0"
    user_points = middleware.bucketGet("dd_sign_points", user_id) or "0"
    try:
        dd_sign_coin = int(float(points))
    except:
        dd_sign_coin = 0
    try:
        dd_sign_points = int(float(user_points))
    except:
        dd_sign_points = 0
    return {
        "dd_sign_coin": dd_sign_coin,
        "dd_sign_points": dd_sign_points,
        "total": dd_sign_coin + dd_sign_points,
    }
def set_user_points(user_id, points):
    middleware.bucketSet("dd_sign_coin", user_id, str(points["dd_sign_coin"]))
    middleware.bucketSet("dd_sign_points", user_id, str(points["dd_sign_points"]))
def query_user_points():
    user_accounts = get_user_accounts()
    if not user_accounts:
        sender.reply("您还没有绑定任何顺易充账号\n请发送「顺易充登录」进行绑定")
        return
    results = []
    success_count = 0
    fail_count = 0
    for account_id, account in user_accounts.items():
        try:
            phone = account.get("phone")
            token = account.get("token", "")
            if not phone:
                results.append("❌ 账号信息不完整，跳过")
                fail_count += 1
                continue
            if not token:
                results.append(f"❌ 账号 {phone} 未保存账号，请重新绑定")
                fail_count += 1
                continue
            if not token.lower().startswith("bearer "):
                token = f"Bearer {token}"
            headers = get_task_headers()
            headers["authorization"] = token
            account_key = f"acc_{phone}"
            headers["_account_key"] = account_key  # 在headers中传递账号标识
            try:
                score_info = get_score_rank_task(headers)
                if score_info:
                    masked_phone = (
                        phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                    )
                    is_authorized = account.get("auth_status", {}).get(
                        "is_authorized", False
                    )
                    expire_time = account.get("auth_status", {}).get("expire_time", "")
                    auth_status = (
                        f"✅ 已授权 (到期: {expire_time})"
                        if is_authorized
                        else "❌ 未授权"
                    )
                    current_year = datetime.now().year
                    year_score = get_year_score_task(headers, current_year)
                    year_line = f"📝 {current_year}年积分: {year_score}\n" if year_score is not None else ""
                    results.append(
                        f"📱 账号: {masked_phone}\n"
                        f"🏆 总积分: {score_info['积分']}\n"
                        f"💰 可用积分: {score_info['可用积分']}\n"
                        f"{year_line}"
                        f"📝 状态: {auth_status}\n"
                        f"--------------------"
                    )
                    success_count += 1
                else:
                    results.append(f"❌ 账号 {phone} 获取积分失败，可能账号已过期")
                    fail_count += 1
            except Exception as e:
                results.append(f"❌ 账号 {phone} 获取积分异常: {str(e)}")
                fail_count += 1
        except Exception as e:
            results.append(f"❌ 账号 {account.get('phone', '未知')} 查询异常: {str(e)}")
            fail_count += 1
    summary = f"=====顺易充账号积分=====\n"
    summary += f"📱 查询账号: {len(user_accounts)}个\n"
    summary += f"✅ 成功: {success_count}个\n"
    summary += f"❌ 失败: {fail_count}个\n"
    summary += "====================\n\n"
    summary += "\n".join(results)
    sender.reply(summary)
def bind_account():
    bind_account_with_sms()
def bind_account_with_sms():
    print("[DEBUG] 进入bind_account_with_sms函数")
    sender.reply("请输入手机号：")
    phone = sender.input(60000, 1, False)
    print(f"[DEBUG] 接收到手机号: {phone}")
    if not phone:
        sender.reply("❌ 未收到手机号")
        return
    if isinstance(phone, str) and phone.strip().lower() == "q":
        sender.reply("✅ 已取消")
        return
    phone = phone.strip()
    if not re.match(r"^1[3-9]\d{9}$", phone):
        sender.reply("❌ 手机号格式不正确，请输入11位手机号")
        return
    print(f"[DEBUG] 准备发送短信到: {phone}")
    sms_result = send_sms_code(phone)
    print(f"[DEBUG] 短信发送结果: {sms_result}")
    if not sms_result:
        sender.reply("❌ 短信发送失败，请稍后重试")
        return
    sender.reply("✅ 短信发送成功！\n请输入收到的验证码（有效期3分钟）：")
    code = sender.input(180000, 1, False)
    if not code:
        sender.reply("❌ 验证码输入超时")
        return
    if code and str(code).strip().lower() == "q":
        sender.reply("✅ 已取消")
        return
    code = str(code).strip()
    if not code:
        sender.reply("❌ 验证码不能为空")
        return
    handle_phone_input_sms(phone, code)


def build_bind_success_message(phone, is_authorized=False):
    auth_msg = ",账号已授权" if is_authorized else ""
    masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
    return (
        f"✅ 账号绑定成功{auth_msg}！\n"
        f"📱 手机号: {masked_phone}\n"
        f"注意： 请使用APP进行充电，这样就不会掉线\n"
        f"注意： 请使用APP进行充电，这样就不会掉线\n"
        f"您可以发送「顺易充管理」查看账号详情"
    )


def update_single_account_token(account_id, phone, user_accounts):
    masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
    sender.reply(
        f"=====更新账号Token=====\n📱 账号: {masked_phone}\n正在发送验证码...\n===================="
    )
    sms_result = send_sms_code(phone)
    if not sms_result:
        sender.reply("❌ 短信发送失败，请稍后重试")
        return
    sender.reply("✅ 短信发送成功！\n请输入收到的验证码（有效期3分钟）：")
    code = sender.input(180000, 1, False)
    if not code:
        sender.reply("❌ 验证码输入超时")
        return
    if str(code) and str(code).strip().lower() == "q":
        sender.reply("✅ 已取消")
        return
    code = str(code).strip()
    if not code:
        sender.reply("❌ 验证码不能为空")
        return
    sender.reply("🔐 正在验证登录...")
    login_result = login_with_sms_code(phone, code)
    if login_result.get("success") and login_result.get("token"):
        token = login_result.get("token", "")
        refresh_token = login_result.get("refreshToken", "")
        cust_info = login_result.get("custInfo")
        if account_id in user_accounts:
            user_accounts[account_id]["token"] = token
            user_accounts[account_id]["refresh_token"] = refresh_token
            user_accounts[account_id]["cust_info"] = cust_info
            user_accounts[account_id]["updated_at"] = int(time.time())
            save_user_accounts(user_accounts)
            # 更新缓存状态
            cache_data = {
                "valid": True,
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            middleware.bucketSet(BUCKET_TOKEN_STATUS, phone, json.dumps(cache_data))
            is_authorized_now = user_accounts[account_id].get("auth_status", {}).get(
                "is_authorized", False
            )
            sender.reply(build_bind_success_message(phone, is_authorized_now))
        else:
            sender.reply("❌ 账号不存在")
    else:
        sender.reply(
            f"❌ 账号更新失败，请检查验证码是否正确或已过期\n"
            f"详情: {login_result.get('message', '未知错误')}"
        )
def batch_update_tokens(user_accounts):
    account_list = []
    for idx, (account_id, account) in enumerate(user_accounts.items(), 1):
        phone = account.get("phone", "未知")
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        token = account.get("token", "")
        cache_json = middleware.bucketGet(BUCKET_TOKEN_STATUS, phone) or "{}"
        try:
            cache_data = json.loads(cache_json)
            check_time_str = cache_data.get("check_time", "")
            if check_time_str:
                check_time = datetime.strptime(check_time_str, "%Y-%m-%d %H:%M:%S")
                hours_ago = (datetime.now() - check_time).total_seconds() / 3600
                if hours_ago < 24:
                    token_status = (
                        "正常: ✓" if cache_data.get("valid") else "重新登录: ❌"
                    )
                else:
                    token_status = "未检测: ?" if token else "重新登录: ❌"
            else:
                token_status = "未检测: ?" if token else "重新登录: ❌"
        except:
            token_status = "未检测: ?" if token else "重新登录: ❌"
        account_list.append((idx, account_id, phone, masked_phone, token_status))
    list_msg = "====账号更新====\n"
    for idx, _, _, masked_phone, token_status in account_list:
        expire_time = (
            user_accounts[list(user_accounts.keys())[idx - 1]]
            .get("auth_status", {})
            .get("expire_time", "")
        )
        expire_info = f"授权到期{expire_time}" if expire_time else "未授权"
        list_msg += f"[{idx}] 📱 {masked_phone} | {token_status}\n     {expire_info}\n"
    list_msg += "--------------------\n回复序号选择账号 (q退出)\n================="
    sender.reply(list_msg)
    success_count = 0
    fail_count = 0
    while True:
        choice = sender.input(120000, 1, False)
        if choice is None:
            sender.reply("⏰ 操作超时，已退出")
            break
        if str(choice).lower() == "q":
            sender.reply(
                f"✅ 已退出\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个"
            )
            break
        try:
            idx = int(choice)
            if idx < 1 or idx > len(account_list):
                sender.reply("❌ 序号无效，请重新输入")
                continue
            _, account_id, phone, masked_phone, _ = account_list[idx - 1]
            sender.reply(f"📱 正在更新: {masked_phone}")
            sms_result = send_sms_code(phone)
            if not sms_result:
                sender.reply("❌ 短信发送失败，请重新选择")
                fail_count += 1
                continue
            sender.reply("✅ 短信发送成功！\n请输入验证码（有效期3分钟）：")
            code = sender.input(180000, 1, False)
            if not code:
                sender.reply("❌ 验证码超时，请重新选择")
                fail_count += 1
                continue
            if str(code).lower() == "q":
                sender.reply(
                    f"✅ 已退出\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个"
                )
                break
            code = str(code).strip()
            if not code:
                sender.reply("❌ 验证码为空，请重新选择")
                fail_count += 1
                continue
            login_result = login_with_sms_code(phone, code)
            if login_result.get("success") and login_result.get("token"):
                token = login_result.get("token", "")
                refresh_token = login_result.get("refreshToken", "")
                cust_info = login_result.get("custInfo")
                user_accounts[account_id]["token"] = token
                user_accounts[account_id]["refresh_token"] = refresh_token
                user_accounts[account_id]["cust_info"] = cust_info
                user_accounts[account_id]["updated_at"] = int(time.time())
                save_user_accounts(user_accounts)
                cache_data = {
                    "valid": True,
                    "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
                middleware.bucketSet(
                    BUCKET_TOKEN_STATUS, phone, json.dumps(cache_data)
                )
                success_count += 1
                # 更新账号列表中的状态
                account_list[idx - 1] = (
                    idx,
                    account_id,
                    phone,
                    masked_phone,
                    "正常: ✓",
                )
                # 重新显示列表
                is_authorized_now = user_accounts[account_id].get("auth_status", {}).get(
                    "is_authorized", False
                )
                new_list_msg = (
                    f"{build_bind_success_message(phone, is_authorized_now)}\n\n"
                    "====账号更新====\n"
                )
                for i, _, _, m_phone, t_status in account_list:
                    exp_time = (
                        user_accounts[list(user_accounts.keys())[i - 1]]
                        .get("auth_status", {})
                        .get("expire_time", "")
                    )
                    exp_info = f"授权到期{exp_time}" if exp_time else "未授权"
                    new_list_msg += (
                        f"[{i}] 📱 {m_phone} | {t_status}\n     {exp_info}\n"
                    )
                new_list_msg += (
                    "--------------------\n回复序号选择账号 (q退出)\n================="
                )
                sender.reply(new_list_msg)
            else:
                sender.reply(
                    f"❌ {masked_phone} 更新失败：{login_result.get('message', '未知错误')}\n\n继续选择下一个账号或回复q退出"
                )
                fail_count += 1
        except ValueError:
            sender.reply("❌ 请输入数字")
def check_auth_validity(auth_status):
    if not auth_status:
        return False
    is_authorized = auth_status.get("is_authorized", False)
    if not is_authorized:
        return False
    expire_time = auth_status.get("expire_time", "")
    if not expire_time:
        return False
    try:
        expire_date = datetime.strptime(expire_time, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if expire_date < today:
            return False
        return True
    except:
        return False
def check_token_validity(token, phone):
    if not token:
        return False, "未保存账号"
    try:
        if not token.lower().startswith("bearer "):
            token = f"Bearer {token}"
        headers = get_task_headers()
        headers["authorization"] = token
        account_key = f"acc_{phone}"
        headers["_account_key"] = account_key  # 在headers中传递账号标识
        print(f"[INFO] 开始验证账号，账号: {phone[:3]}****{phone[-4:]}")
        print(f"[INFO] 代理状态: {'已启用' if IS_PROXY else '未启用'}")
        test_url = (
            "https://app.wodeev.com/bil-front/v2.0/accounts/myScoreRank?scoreType=02"
        )
        print(f"[INFO] 验证URL: {test_url}")
        response = request_with_retry(
            "GET",
            test_url,
            headers=headers,
            timeout=15,
            verify=False,
            account_key=account_key,
        )
        print(f"[INFO] 请求响应状态: {response.status_code if response else '无响应'}")
        if response and response.status_code == 200:
            try:
                data = response.json()
                print(
                    f"[INFO] 响应数据: ret={data.get('ret')}, msg={data.get('msg', '无消息')[:50]}"
                )
                if data.get("ret") == 200:
                    return True, "账号有效"
                else:
                    print(f"[INFO] 尝试备用验证接口...")
                    try:
                        backup_url = "https://app.wodeev.com/bil-front/v2.0/marketing/getScoreRankingShare"
                        backup_response = request_with_retry(
                            "GET",
                            backup_url,
                            headers=headers,
                            timeout=15,
                            verify=False,
                            account_key=account_key,
                        )
                        if backup_response and backup_response.status_code == 200:
                            backup_data = backup_response.json()
                            print(f"[INFO] 备用接口响应: ret={backup_data.get('ret')}")
                            if backup_data.get("ret") == 200:
                                return True, "账号有效"
                    except Exception as be:
                        print(f"[WARNING] 备用接口异常: {str(be)[:50]}")
                    return False, f"账号已过期 (ret={data.get('ret')})"
            except Exception as je:
                print(f"[ERROR] JSON解析失败: {str(je)}")
                return False, "响应格式错误"
        else:
            error_msg = f"网络请求失败"
            if response:
                error_msg += f" (HTTP {response.status_code})"
            print(f"[ERROR] {error_msg}")
            return False, error_msg
    except Exception as e:
        print(f"[ERROR] 账号验证异常: {str(e)}")
        return False, f"验证异常: {str(e)}"
def handle_phone_input_sms(phone, sms_code):
    if not re.match(r"^1[3-9]\d{9}$", phone):
        sender.reply("❌ 手机号格式不正确，请输入11位手机号")
        return
    sender.reply("🔐 正在验证登录...")
    login_result = login_with_sms_code(phone, sms_code)
    if login_result.get("success") and login_result.get("token"):
        token = login_result.get("token", "")
        refresh_token = login_result.get("refreshToken", "")
        cust_info = login_result.get("custInfo")
        user_accounts = get_user_accounts()
        existing_account_id = None
        existing_auth_status = None
        for acc_id, acc_info in user_accounts.items():
            if acc_info.get("phone") == phone:
                existing_account_id = acc_id
                existing_auth_status = acc_info.get("auth_status")
                break
        if not existing_auth_status or not existing_auth_status.get("is_authorized"):
            existing_auth_status = build_auth_status(phone)
            if existing_auth_status.get("is_authorized"):
                print(
                    f"[INFO] 从全局授权数据恢复授权状态: {phone}, 到期: {existing_auth_status.get('expire_time', '')}"
                )
        if existing_account_id:
            account_id = existing_account_id
        else:
            account_id = f"{phone}_{int(time.time())}"
        user_accounts[account_id] = {
            "phone": phone,
            "token": token,
            "refresh_token": refresh_token,
            "cust_info": cust_info,
            "updated_at": int(time.time()),
            "login_type": "sms",
            "auth_status": existing_auth_status
            or {"is_authorized": False, "expire_time": ""},
        }
        save_user_accounts(user_accounts)
        cache_data = {
            "valid": True,
            "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        middleware.bucketSet(BUCKET_TOKEN_STATUS, phone, json.dumps(cache_data))
        is_authorized_now = user_accounts[account_id]["auth_status"].get(
            "is_authorized", False
        )
        sender.reply(build_bind_success_message(phone, is_authorized_now))
    else:
        sender.reply(
            f"❌ 短信验证码登录失败，请检查验证码是否正确或已过期\n"
            f"详情: {login_result.get('message', '未知错误')}"
        )
def get_user_accounts(user_id=None):
    if not user_id:
        user_id = userid
    try:
        phones = get_user_phones(user_id)
        if not phones:
            return {}
        accounts = {}
        for phone in phones:
            token = middleware.bucketGet(BUCKET_TOKEN, phone) or ""
            refresh_token = ""
            cust_info = None
            updated_at = 0
            state_json = middleware.bucketGet(BUCKET_AUTH_STATE, phone) or "{}"
            try:
                state_data = json.loads(state_json)
                if isinstance(state_data, dict):
                    token = state_data.get("token") or token
                    refresh_token = state_data.get("refreshToken") or ""
                    cust_info = state_data.get("custInfo")
                    updated_at = state_data.get("updatedAt") or 0
            except Exception:
                pass
            accounts[phone] = {
                "phone": phone,
                "token": token,
                "refresh_token": refresh_token,
                "cust_info": cust_info,
                "updated_at": updated_at,
                "login_type": "sms",
                "auth_status": build_auth_status(phone),
            }
        return accounts
    except Exception:
        return {}
def save_user_accounts(accounts, user_id=None):
    if not user_id:
        user_id = userid
    try:
        # 获取旧的手机号列表,用于清理已删除账号的残留数据
        old_phones_json = middleware.bucketGet(BUCKET_USER, user_id) or "[]"
        try:
            old_phones = set(json.loads(old_phones_json))
        except:
            old_phones = set()

        phones = []
        for account_id, account_info in accounts.items():
            phone = account_info.get("phone")
            token = account_info.get("token")
            refresh_token = account_info.get("refresh_token") or ""
            cust_info = account_info.get("cust_info")
            updated_at = account_info.get("updated_at") or int(time.time())
            if phone:
                phones.append(phone)
                if token:
                    middleware.bucketSet(BUCKET_TOKEN, phone, token)
                auth_state = {
                    "token": token or "",
                    "refreshToken": refresh_token,
                    "custInfo": cust_info,
                    "updatedAt": updated_at,
                }
                middleware.bucketSet(
                    BUCKET_AUTH_STATE,
                    phone,
                    json.dumps(auth_state, ensure_ascii=False),
                )
                auth_status = account_info.get("auth_status", {})
                if auth_status.get("is_authorized"):
                    expire_time = auth_status.get("expire_time", "")
                    if expire_time:
                        middleware.bucketSet(BUCKET_AUTH, phone, expire_time)

        # 清理已删除账号的残留数据
        current_phones = set(phones)
        removed_phones = old_phones - current_phones
        for phone in removed_phones:
            try:
                middleware.bucketDel(BUCKET_TOKEN, phone)
            except:
                pass
            try:
                middleware.bucketDel(BUCKET_AUTH_STATE, phone)
            except:
                pass
            try:
                middleware.bucketDel(BUCKET_TOKEN_STATUS, phone)
            except:
                pass
            # 注意: BUCKET_AUTH 不在这里删除,因为授权是全局的

        # 更新或删除用户索引
        if phones:
            middleware.bucketSet(BUCKET_USER, user_id, json.dumps(phones))
        else:
            # 账号清空时删除用户索引
            try:
                middleware.bucketDel(BUCKET_USER, user_id)
            except:
                pass
    except Exception as e:
        print(f"[ERROR] 保存用户账号失败: {str(e)}")
        pass
def manage_accounts():
    user_accounts = get_user_accounts()
    if not user_accounts:
        sender.reply("您还没有绑定任何顺易充账号\n请发送「顺易充登录」进行绑定")
        return
    accounts_updated = False
    expired_phones = []
    for account_id, account in user_accounts.items():
        phone = account.get("phone", "")
        auth_status = build_auth_status(phone)
        if account.get("auth_status") != auth_status:
            user_accounts[account_id]["auth_status"] = auth_status
            accounts_updated = True
        if not auth_status.get("is_authorized") and get_auth(phone):
            expired_phones.append(phone)
    for phone in expired_phones:
        try:
            middleware.bucketDel(BUCKET_AUTH, phone)
            print(f"[INFO] 已清理过期授权记录: {phone}")
        except Exception as e:
            print(f"[WARNING] 清理过期授权记录失败 {phone}: {str(e)}")
    if accounts_updated:
        save_user_accounts(user_accounts)
    points = get_user_points()
    total_points = points["total"]
    authorized_count = 0
    unauthorized_count = 0
    unauthorized_accounts = []
    for account_id, account in user_accounts.items():
        auth_status = account.get("auth_status", {})
        if auth_status.get("is_authorized"):
            authorized_count += 1
        else:
            unauthorized_count += 1
            unauthorized_accounts.append(account_id)
    accounts_msg = "=====账号管理=====\n"
    accounts_msg += f"📱 绑定账号: {len(user_accounts)}个\n"
    accounts_msg += f" 已授权: {authorized_count}个\n"
    accounts_msg += f" 未授权: {unauthorized_count}个\n"
    accounts_msg += f"📊 当前积分: {total_points}\n"
    accounts_msg += "--------------------\n"
    accounts_msg += "📱 短信验证码登录\n"
    accounts_msg += "--------------------\n"
    for idx, (account_id, account) in enumerate(user_accounts.items(), 1):
        phone = account.get("phone", "未知")
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        auth_status = account.get("auth_status", {})
        expire_time = auth_status.get("expire_time", "")
        expire_info = f"授权到期{expire_time}" if expire_time else "未授权"
        accounts_msg += f"[{idx}] 📱 {masked_phone}\n     {expire_info}\n"
    accounts_msg += "[0] 所有账号授权 (支付)\n"
    accounts_msg += "[9997] 批量更新Token（更新）\n"
    accounts_msg += "[9998] 删除所有账号（删除）\n"
    accounts_msg += "[9999]未授权账号 (授权)\n"
    accounts_msg += "--------------------\n"
    accounts_msg += "回复序号选择操作 (q退出)\n"
    accounts_msg += "=================\n"
    sender.reply(accounts_msg)
    selection = sender.input(60000, 1, False)
    handle_account_selection(selection)
def delete_all_accounts():
    user_accounts = get_user_accounts()
    if not user_accounts:
        sender.reply("❌ 您还没有绑定任何顺易充账号")
        return
    account_count = len(user_accounts)
    accounts_list = []
    for account_id, account in user_accounts.items():
        phone = account.get("phone", "未知")
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else phone
        accounts_list.append(f"📱 {masked_phone}")
    confirmation_msg = f"""
⚠️ 危险操作确认 ⚠️
您即将删除名下的全部 {account_count} 个顺易充账号：
{chr(10).join(accounts_list)}
❗ 此操作不可撤销！
❗ 删除后需要重新绑定账号！
❗ 已授权的账号将失去授权状态！
确认删除请回复：确认删除全部账号
取消操作请回复：q
"""
    sender.reply(confirmation_msg)
    confirmation = sender.input(60000, 1, False)
    if confirmation is None:
        sender.reply("⏰ 操作超时，已取消删除")
        return
    if str(confirmation).lower() == "q":
        sender.reply("✅ 已取消删除操作")
        return
    if confirmation != "确认删除全部账号":
        sender.reply("❌ 确认信息不正确，已取消删除")
        return
    try:
        phones_to_delete = [
            acc.get("phone") for acc in user_accounts.values() if acc.get("phone")
        ]
        remove_authorized_accounts(phones_to_delete)
        middleware.bucketDel(BUCKET_USER, userid)
        delete_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        success_msg = f"""
✅ 删除成功！
已删除您名下的全部 {account_count} 个顺易充账号
📝 删除详情：
- 删除时间：{delete_time}
- 删除账号数：{account_count} 个
💡 如需重新使用，请发送「顺易充登录」重新绑定账号
"""
        sender.reply(success_msg)
    except Exception as e:
        sender.reply(f"❌ 删除操作失败：{str(e)}")
def handle_account_selection(selection):
    try:
        user_accounts = get_user_accounts()
        if not user_accounts:
            sender.reply("❌ 未找到您的账号信息")
            return
        account_ids = list(user_accounts.keys())
        unauthorized_ids = []
        for account_id, account in user_accounts.items():
            auth_status = account.get("auth_status", {})
            is_authorized = auth_status.get("is_authorized", False)
            if not is_authorized or not check_auth_validity(auth_status):
                unauthorized_ids.append(account_id)
        if str(selection).lower() == "q":
            sender.reply("✅ 已退出账号管理")
            return
        if selection is None:
            sender.reply("⏰ 操作超时")
            return
        try:
            selection = int(selection)
        except (ValueError, TypeError):
            sender.reply("❌ 输入无效，请输入数字")
            return
        if selection == 0:
            if not account_ids:
                sender.reply("❌ 没有找到可授权的账号")
                return
            sender.reply(f"您选择了授权所有账号，共 {len(account_ids)} 个账号")
            sender.reply("请输入授权月数（1-24月）：")
            auth_input = sender.input(60000, 1, False)
            if auth_input is None or not auth_input.strip():
                sender.reply("⏰ 输入超时或为空，已取消授权操作")
                return
            handle_auth_days(auth_input, account_ids)
        elif selection == 9997:
            batch_update_tokens(user_accounts)
        elif selection == 9998:
            delete_all_accounts()
        elif selection == 9999:
            if not unauthorized_ids:
                sender.reply("❌ 没有找到未授权的账号")
                return
            sender.reply(
                f"您选择了授权所有未授权账号，共 {len(unauthorized_ids)} 个账号"
            )
            sender.reply("请输入授权月数（1-24月）：")
            auth_input = sender.input(60000, 1, False)
            if auth_input is None or not auth_input.strip():
                sender.reply("⏰ 输入超时或为空，已取消授权操作")
                return
            handle_auth_days(auth_input, unauthorized_ids)
        elif 1 <= selection <= len(account_ids):
            selected_account_id = account_ids[selection - 1]
            selected_phone = user_accounts[selected_account_id].get("phone", "未知")
            sender.reply("""
请选择操作:
[0] 更新账号
[1] 授权账号
[2] 删除账号
[3] 运行任务
回复数字选择操作，回复q取消
""")
            operation = sender.input(60000, 1, False)
            if operation is None:
                sender.reply("⏰ 操作超时，已取消")
                return
            if operation == "0":
                update_single_account_token(
                    selected_account_id, selected_phone, user_accounts
                )
            elif operation == "1":
                sender.reply("请输入授权月数（1-24月）：")
                auth_input = sender.input(60000, 1, False)
                if auth_input is None or not auth_input.strip():
                    sender.reply("⏰ 输入超时或为空，已取消授权操作")
                    return
                handle_auth_days(auth_input, [selected_account_id])
            elif operation == "2":
                phone = user_accounts[selected_account_id].get("phone", "未知")
                sender.reply(
                    f"⚠️ 确认删除账号 {phone} 吗？此操作不可恢复！\n回复 [Y] 确认删除\n回复 [N] 取消"
                )
                confirm = sender.input(60000, 1, False)
                if confirm is None:
                    sender.reply("⏰ 操作超时，已取消删除")
                    return
                if str(confirm).lower() != "y":
                    sender.reply("✅ 已取消删除操作")
                    return
                if selected_account_id in user_accounts:
                    phone = user_accounts[selected_account_id].get("phone", "")
                    del user_accounts[selected_account_id]
                    save_user_accounts(user_accounts)
                    if phone:
                        remove_authorized_accounts([phone])
                    sender.reply(f"✅ 成功删除账号 {phone}")
                    if len(user_accounts) > 0:
                        manage_accounts()
                    else:
                        sender.reply("您已删除所有账号，可发送「顺易充登录」绑定新账号")
                else:
                    sender.reply("❌ 账号不存在")
            elif operation == "3":
                run_single_account_task(selected_account_id, user_accounts)
            elif str(operation).lower() == "q":
                sender.reply("✅ 已取消操作")
            else:
                sender.reply("❌ 无效的选择")
        else:
            sender.reply("❌ 无效的选择，请输入正确的序号")
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 账号操作异常: {error_details}")
        sender.reply(f"❌ 操作失败：{str(e)}\n请联系管理员查看日志")
def remove_authorized_accounts(phones):
    try:
        auth_records_json = middleware.bucketGet(BUCKET_RECORDS, "auth_current") or "{}"
        try:
            auth_records = json.loads(auth_records_json)
        except:
            auth_records = {}

        auth_records_updated = False
        for phone in phones:
            try:
                middleware.bucketDel(BUCKET_AUTH, phone)  # 删除授权信息
            except:
                pass
            try:
                middleware.bucketDel(BUCKET_TOKEN, phone)  # 删除token
            except:
                pass
            try:
                middleware.bucketDel(BUCKET_TOKEN_STATUS, phone)  # 删除token状态缓存
            except:
                pass
            try:
                middleware.bucketDel(BUCKET_AUTH_STATE, phone)
            except:
                pass
            if phone in auth_records:
                del auth_records[phone]
                auth_records_updated = True

        if auth_records_updated:
            middleware.bucketSet(
                BUCKET_RECORDS,
                "auth_current",
                json.dumps(auth_records, ensure_ascii=False),
            )
    except Exception as e:
        pass
def handle_auth_days(months_str, account_ids):
    try:
        if months_str is None:
            sender.reply("⏰ 输入超时，已取消授权操作")
            return
        actual_input_str = str(months_str).strip()
        if not actual_input_str:
            sender.reply("❌ 输入不能为空，请输入1-24之间的月数")
            return
        if actual_input_str.startswith("+"):
            actual_input_str = actual_input_str[1:]
        if actual_input_str.startswith("-"):
            sender.reply("❌ 普通用户只能增加授权时间，不支持减少操作")
            return
        try:
            months = int(actual_input_str)
        except ValueError:
            sender.reply("❌ 请输入有效的数字（1-24）")
            return
        if not (1 <= months <= 24):
            sender.reply("❌ 授权月数必须在1-24之间（最多2年）")
            return
        days = months * 30
        user_accounts = get_user_accounts()
        phone = "未知"
        if account_ids and account_ids[0] in user_accounts:
            phone = user_accounts[account_ids[0]].get("phone", "未知")
        points = get_user_points()
        config = get_config()
        points_needed = (
            len(account_ids) * months * int(config["points_per_month"])
        )  # 按月计算积分
        total_price = config["price"] * months * len(account_ids)  # 按月计算价格
        pay_options = []
        pay_handlers = {}
        option_index = 1
        if config.get("zsm"):
            pay_options.append(f"[{option_index}] 微信收款码支付")
            pay_handlers[str(option_index)] = (
                lambda account_ids=account_ids, days=days, total_price=total_price, config=config, phone=phone: wechat_payment_flow(
                    account_ids, days, total_price, config, phone
                )
            )
            option_index += 1
        pay_types = (
            dict(config.get("pay_types") or {}) if config.get("ma_pay_switch") else {}
        )
        for pay_key, raw_pay_name in pay_types.items():
            pay_name = (
                str(raw_pay_name or DEFAULT_PAY_TYPE_NAMES.get(pay_key, pay_key)).strip()
                or DEFAULT_PAY_TYPE_NAMES.get(pay_key, pay_key)
            )
            if config.get("zsm") and pay_key == "wxpay":
                pay_name = "微信码支付"
            pay_options.append(f"[{option_index}] {pay_name}")
            pay_handlers[str(option_index)] = (
                lambda pay_key=pay_key, pay_name=pay_name, account_ids=account_ids, days=days, total_price=total_price, config=config, phone=phone, months=months: ma_payment_flow(
                    account_ids,
                    days,
                    total_price,
                    config,
                    phone,
                    months,
                    pay_type_key=pay_key,
                    pay_type_name=pay_name,
                )
            )
            option_index += 1
        pay_options.append(f"[{option_index}] 积分支付")
        pay_handlers[str(option_index)] = (
            lambda account_ids=account_ids, days=days, points_needed=points_needed, phone=phone: point_payment_flow(
                account_ids, days, points_needed, phone
            )
        )
        time_unit = f"{int(months)}月"
        operation_type = "增加"
        pay_menu = f"""
=====顺易充授权支付=====
📱 手机号: {phone}{f" 等{len(account_ids)}个账号" if len(account_ids) > 1 else ""}
🎯 授权操作: {operation_type}{time_unit}
💰 金额: ¥{abs(total_price):.2f}
📊 积分支付: {abs(points_needed)}积分（当前积分: {points["total"]}）
------------------
{chr(10).join(pay_options)}
回复数字选择支付方式，回复q取消
==================="""
        sender.reply(pay_menu)
        pay_choice = sender.input(120000, 1, False)
        if str(pay_choice).lower() == "q":
            sender.reply("✅ 已取消授权")
            return
        elif pay_choice in pay_handlers:
            payment_success = pay_handlers[pay_choice]()
        else:
            sender.reply("❌ 无效支付方式")
            return
        if payment_success:
            authorized_count = 0
            current_time = datetime.now()
            global_authorized_accounts = get_authorized_accounts()
            authorized_phones = []
            expire_date = None  # 初始化 expire_date 避免可能未定义
            for account_id in account_ids:
                if account_id in user_accounts:
                    phone = user_accounts[account_id].get("phone", "")
                    existing_expire_date = None
                    is_expired = False
                    # 【修复】优先从全局授权数据获取（权威数据源）
                    if phone in global_authorized_accounts:
                        try:
                            global_expire_date_str = global_authorized_accounts[phone][
                                "expire_date"
                            ]
                            global_expire_time = datetime.strptime(
                                global_expire_date_str, "%Y-%m-%d"
                            )
                            existing_expire_date = global_expire_time
                            is_expired = global_expire_time.date() < current_time.date()
                        except:
                            pass
                    # 如果全局数据没有，再从用户账号数据获取
                    if existing_expire_date is None and user_accounts[account_id].get(
                        "auth_status", {}
                    ).get("is_authorized"):
                        try:
                            expire_time_str = user_accounts[account_id]["auth_status"][
                                "expire_time"
                            ]
                            expire_time = datetime.strptime(expire_time_str, "%Y-%m-%d")
                            existing_expire_date = expire_time
                            is_expired = expire_time.date() < current_time.date()
                        except:
                            pass
                    if existing_expire_date and not is_expired:
                        new_expire_date = existing_expire_date + timedelta(days=days)
                    else:
                        new_expire_date = current_time + timedelta(days=days)
                    expire_date = new_expire_date.strftime("%Y-%m-%d")
                    user_accounts[account_id]["auth_status"] = {
                        "is_authorized": True,
                        "expire_time": expire_date,
                        "auth_time": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "days": days,
                        "is_renewal": existing_expire_date is not None,
                    }
                    user_accounts[account_id]["wx_id"] = senderID
                    if phone:
                        authorized_phones.append(phone)
                        middleware.bucketSet(BUCKET_AUTH, phone, expire_date)
                    authorized_count += 1
            save_user_accounts(user_accounts)
            is_renewals = {}
            for account_id in account_ids:
                if account_id in user_accounts:
                    phone = user_accounts[account_id].get("phone", "")
                    if phone:
                        is_renewals[phone] = user_accounts[account_id][
                            "auth_status"
                        ].get("is_renewal", False)
            save_auth_record(authorized_phones, expire_date, days, is_renewals)
            sender.reply(
                f"✅ 授权成功\n"
                f"授权账号数: {authorized_count}\n"
                f"授权时长: {months}个月（{days}天）\n"
                f"到期时间: {expire_date}"
            )
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] 授权处理异常: {error_details}")
        sender.reply(f"❌ 授权处理失败：{str(e)}\n请联系管理员查看日志")


def choose_ma_pay_type(config) -> tuple:
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
    sender.reply("\n".join(lines))
    choice = sender.input(120000, 1, False)
    if not choice:
        sender.reply("⏰ 操作超时")
        return None, None
    choice = str(choice).strip().lower()
    if choice == "q" or not choice.isdigit():
        return None, None
    idx = int(choice) - 1
    if idx < 0 or idx >= len(items):
        return None, None
    return items[idx]


def format_target_label(target_label) -> str:
    text = str(target_label or "").strip()
    if re.fullmatch(r"1[3-9]\d{9}$", text):
        return text[:3] + "****" + text[-4:]
    return text or "账号"


def ma_payment_flow(
    account_ids, days, amount, config, phone, months, pay_type_key=None, pay_type_name=None
):
    if amount <= 0:
        return True
    if MaPayClient is None:
        sender.reply("❌ 未安装 autman_huawei 模块，无法使用码支付")
        return False
    if pay_type_key:
        pay_type_name = (
            str(
                pay_type_name
                or (config.get("pay_types") or {}).get(pay_type_key)
                or DEFAULT_PAY_TYPE_NAMES.get(pay_type_key, pay_type_key)
            ).strip()
            or DEFAULT_PAY_TYPE_NAMES.get(pay_type_key, pay_type_key)
        )
    else:
        pay_type_key, pay_type_name = choose_ma_pay_type(config)
        if not pay_type_key:
            sender.reply("✅ 已取消码支付")
            return False
    client = MaPayClient()
    if not client.is_configured():
        sender.reply("❌ 码支付配置不完整，请检查 dd_sign_config")
        return False
    display_name = phone
    if len(account_ids) > 1:
        display_name = f"{phone} 等{len(account_ids)}个账号"
    display_name = format_target_label(display_name)
    out_trade_no = f"SYC{int(time.time() * 1000)}{random.randint(100, 999)}"
    subject = f"顺易充授权-{display_name[:18]}"
    order_result = client.create_order(
        float(amount), pay_type_key, out_trade_no, subject, str(userid)
    )
    if order_result.get("error"):
        sender.reply(f"❌ 创建码支付订单失败: {order_result['error']}")
        return False
    pay_url = order_result.get("pay_url") or ""
    if not pay_url:
        sender.reply("❌ 未获取到码支付链接")
        return False
    sender.reply(
        f"=====码支付=====\n"
        f"📱 手机号: {display_name}\n"
        f"🎯 授权时长: {int(months)}个月（{days}天）\n"
        f"💰 金额: ¥{amount:.2f}\n"
        f"💳 方式: {pay_type_name}\n"
        f"------------------\n"
        f"请扫码支付，回复q取消\n"
        f"=================="
    )
    if callable(generate_qrcode_url):
        try:
            qrcode_url = generate_qrcode_url(pay_url)
            if qrcode_url:
                sender.replyImage(qrcode_url)
            else:
                sender.reply(f"请打开下方链接完成支付：\n{pay_url}")
        except Exception:
            sender.reply(f"二维码发送失败，请打开下方链接完成支付：\n{pay_url}")
    else:
        sender.reply(f"请打开下方链接完成支付：\n{pay_url}")
    for _ in range(PAY_POLL_TIMES):
        try:
            listen_result = sender.listen(PAY_POLL_INTERVAL_MS)
        except Exception:
            time.sleep(PAY_POLL_INTERVAL_MS / 1000)
            listen_result = ""
        if str(listen_result).strip().lower() == "q":
            sender.reply("✅ 已取消支付")
            return False
        if client.is_paid(out_trade_no):
            sender.reply(f"✅ 码支付成功，已完成 {pay_type_name}")
            return True
    sender.reply("❌ 支付超时，请重新发起")
    return False


def point_payment_flow(account_ids, days, required_points, phone):
    # 使用锁保护整个积分扣减流程,避免并发竞态
    with _points_payment_lock:
        user_points = get_user_points()
        if user_points["total"] < required_points:
            sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points["total"]}积分
请「联系管理员」充值积分
        """)
            return False
        sender.reply(f"""
⚠ 确认使用积分支付吗？
📊 扣除: {required_points}积分
📈 剩余: {user_points["total"] - required_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消
    """)
        confirm = sender.input(60000, 1, False)
        if confirm is None:
            sender.reply("⏰ 操作超时，已取消积分支付")
            return False
        if str(confirm).lower() != "y":
            sender.reply("✅ 积分支付已取消")
            return False
        # 用户确认后再次检查积分(锁内二次校验)
        current_points = get_user_points()
        if current_points["total"] < required_points:
            sender.reply(
                f"❌ 积分不足！当前积分: {current_points['total']}，需要: {required_points}"
            )
            return False
        sign_coin = current_points["dd_sign_coin"]
        sign_points = current_points["dd_sign_points"]
        if sign_coin >= required_points:
            sign_coin -= required_points
        else:
            remaining = required_points - sign_coin
            sign_coin = 0
            sign_points -= remaining
        sign_coin = max(0, sign_coin)
        sign_points = max(0, sign_points)
        result_points = {
            "dd_sign_coin": sign_coin,
            "dd_sign_points": sign_points,
        }
        set_user_points(userid, result_points)
        transaction_data = {
            "userid": userid,
            "account_ids": account_ids,
            "days": days,
            "points": required_points,
            "balance": sign_points + sign_coin,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "point_payment",
        }
        middleware.bucketSet(
            "dd_sign_transactions", f"tx_{int(time.time())}", json.dumps(transaction_data)
        )
        sender.reply(
            f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {sign_points + sign_coin}"
        )
        return True
def wechat_payment_flow(account_ids, days, amount, config, phone):
    zsm = config.get("zsm", "")
    if not zsm:
        sender.reply("❌ 管理员未配置收款码，无法使用微信支付")
        return False
    sender.reply(f"""
=====微信扫码支付=====
📱 手机号: {phone}{f" 等{len(account_ids)}个账号" if len(account_ids) > 1 else ""}
🎯 授权时长: {days}天
💰 金额: ¥{amount:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
    sender.replyImage(zsm)
    payment_result = sender.waitPay(timeout=600000, exitcode="q")
    if payment_result == "q":
        sender.reply("❌ 支付已取消")
        return False
    sender.reply("✅ 支付成功")
    return True
def save_authorized_accounts(phone_expire_data, expire_date=None):
    try:
        if isinstance(phone_expire_data, dict):
            items = phone_expire_data.items()
        else:
            items = ((phone, expire_date) for phone in phone_expire_data)
        for phone, current_expire_date in items:
            if not phone or not current_expire_date:
                continue
            middleware.bucketSet(BUCKET_AUTH, phone, current_expire_date)
    except Exception as e:
        pass
def save_auth_record(phones, expire_date, days, is_renewals=None):
    """只保留每个手机号的最终授权状态,不累积历史记录"""
    try:
        # 读取现有授权状态(按手机号索引)
        auth_records_json = middleware.bucketGet(BUCKET_RECORDS, "auth_current") or "{}"
        auth_records = json.loads(auth_records_json)

        # 更新或新增授权记录(覆盖式,只保留最终状态)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for phone in phones:
            # 如果expire_date是汇总字符串(如"phone1: 2025-01-01、phone2: 2025-01-02"),提取对应手机号的时间
            if isinstance(expire_date, str) and ":" in expire_date:
                # 尝试从汇总字符串中提取该手机号的到期时间
                phone_expire = expire_date
                for part in expire_date.split("、"):
                    if phone in part and ":" in part:
                        phone_expire = part.split(":")[-1].strip()
                        break
            else:
                phone_expire = expire_date

            auth_records[phone] = {
                "expire_date": phone_expire,
                "days": days,
                "auth_time": current_time,
                "wx_id": senderID,
                "user_id": userid,
            }

        middleware.bucketSet(BUCKET_RECORDS, "auth_current", json.dumps(auth_records, ensure_ascii=False))
        print(f"✅ 已更新授权状态(仅保留最终到期时间)")
    except Exception as e:
        print(f"❌ 保存授权记录失败: {str(e)}")
def refresh_access_token(refresh_token: str, account_key=None) -> dict:
    try:
        if not refresh_token:
            return {"success": False, "message": "refreshToken为空", "token": "", "refreshToken": ""}
        timestamp, sign, _, _ = build_signed_params("token", refresh_token)
        if not sign:
            return {"success": False, "message": "刷新签名生成失败", "token": "", "refreshToken": ""}
        payload = {"sign": sign, "refreshToken": refresh_token, "timestamp": timestamp}
        headers = {
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*",
            "Authorization": "",
            "client-version": "5.10.0",
            "loginChannel": "07",
            "lang": "1",
            "User-Agent": "okhttp/4.9.0",
        }
        url = "https://app.wodeev.com/cst-front/open/v2.0/refreshToken"
        response = request_with_retry("POST", url, json=payload, headers=headers, verify=False, timeout=15, account_key=account_key)
        if not response or response.status_code != 200:
            return {"success": False, "message": f"刷新HTTP异常: {response.status_code if response else '无响应'}", "token": "", "refreshToken": ""}
        try:
            res_data = response.json()
        except json.JSONDecodeError:
            return {"success": False, "message": "刷新接口返回非JSON", "token": "", "refreshToken": ""}
        if res_data.get("ret") == 200:
            return {"success": True, "message": "刷新成功", "token": res_data.get("token", ""), "refreshToken": res_data.get("refreshToken", ""), "response": res_data}
        return {"success": False, "message": f"刷新失败: {res_data.get('msg', '未知错误')}", "token": "", "refreshToken": "", "response": res_data}
    except Exception as e:
        return {"success": False, "message": f"刷新异常: {str(e)}", "token": "", "refreshToken": ""}


def user_refresh_tokens():
    user_accounts = get_user_accounts()
    if not user_accounts:
        sender.reply("❌ 您还没有绑定任何顺易充账号\n请发送「顺易充登录」进行绑定")
        return
    account_list = []
    for idx, (account_id, account) in enumerate(user_accounts.items(), 1):
        phone = account.get("phone", "未知")
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        refresh_token = account.get("refresh_token", "")
        cache_json = middleware.bucketGet(BUCKET_TOKEN_STATUS, phone) or "{}"
        try:
            cache_data = json.loads(cache_json)
            if cache_data.get("valid") is True:
                token_status = "正常: ✓"
            elif cache_data.get("valid") is False:
                token_status = "需刷新: ❌"
            else:
                token_status = "未检测: ?"
        except Exception:
            token_status = "未检测: ?"
        has_refresh = "有" if refresh_token else "无"
        account_list.append((idx, account_id, phone, masked_phone, token_status, has_refresh))
    list_msg = "====账号Token刷新====\n"
    for idx, _, _, masked_phone, token_status, has_refresh in account_list:
        list_msg += f"[{idx}] 📱 {masked_phone} | {token_status}\n"
    list_msg += "--------------------\n回复序号选择账号刷新 (q退出)\n================="
    sender.reply(list_msg)
    success_count = 0
    fail_count = 0
    while True:
        choice = sender.input(120000, 1, False)
        if choice is None:
            sender.reply("⏰ 操作超时，已退出")
            break
        if str(choice).lower() == "q":
            sender.reply(f"✅ 已退出\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个")
            break
        try:
            idx = int(choice)
            if idx < 1 or idx > len(account_list):
                sender.reply("❌ 序号无效，请重新输入")
                continue
            _, account_id, phone, masked_phone, _, has_refresh = account_list[idx - 1]
            if has_refresh == "无":
                sender.reply(f"❌ {masked_phone} 缺少refreshToken，无法刷新\n请重新短信登录该账号")
                fail_count += 1
                continue
            sender.reply(f"📱 正在刷新: {masked_phone}")
            refresh_token = user_accounts[account_id].get("refresh_token", "")
            account_key = f"acc_{phone}"
            refresh_result = refresh_access_token(refresh_token, account_key=account_key)
            if refresh_result.get("success") and refresh_result.get("token"):
                new_token = refresh_result.get("token", "")
                new_refresh_token = refresh_result.get("refreshToken") or refresh_token
                user_accounts[account_id]["token"] = new_token
                user_accounts[account_id]["refresh_token"] = new_refresh_token
                user_accounts[account_id]["updated_at"] = int(time.time())
                save_user_accounts(user_accounts)
                cache_data = {"valid": True, "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                middleware.bucketSet(BUCKET_TOKEN_STATUS, phone, json.dumps(cache_data))
                success_count += 1
                account_list[idx - 1] = (idx, account_id, phone, masked_phone, "正常: ✓", "有")
                new_list_msg = f"✅ {masked_phone} 刷新成功！\n\n====账号Token刷新====\n"
                for i, _, _, m_phone, t_status, h_refresh in account_list:
                    new_list_msg += f"[{i}] 📱 {m_phone} | {t_status}\n"
                new_list_msg += "--------------------\n回复序号选择账号刷新 (q退出)\n================="
                sender.reply(new_list_msg)
            else:
                sender.reply(f"❌ {masked_phone} 刷新失败：{refresh_result.get('message', '未知错误')}\n\n继续选择下一个账号或回复q退出")
                fail_count += 1
        except ValueError:
            sender.reply("❌ 请输入数字")


def admin_refresh_all_tokens():
    if not is_syc_admin():
        sender.reply("❌ 您没有顺易充管理员权限！")
        return
    sender.reply("🔍 正在扫描已授权且未过期的账号...")
    global_authorized_accounts = get_authorized_accounts()
    if not global_authorized_accounts:
        sender.reply("❌ 未找到任何授权账号")
        return
    current_time = datetime.now()
    target_accounts = []
    processed_phones = set()
    try:
        users = middleware.bucketAllKeys(bucket=BUCKET_USER) or []
    except Exception:
        users = []
    for user_id in users:
        try:
            user_phones_json = middleware.bucketGet(BUCKET_USER, user_id) or "[]"
            user_phones = json.loads(user_phones_json)
            for phone in user_phones:
                if not phone or phone in processed_phones:
                    continue
                if phone not in global_authorized_accounts:
                    continue
                expire_date_str = global_authorized_accounts[phone].get("expire_date", "")
                if not expire_date_str:
                    continue
                try:
                    expire_date = datetime.strptime(expire_date_str, "%Y-%m-%d")
                    if expire_date < current_time:
                        continue
                except Exception:
                    continue
                auth_state_json = middleware.bucketGet(BUCKET_AUTH_STATE, phone) or "{}"
                token = ""
                refresh_token = ""
                cust_info = None
                try:
                    auth_state = json.loads(auth_state_json)
                    token = auth_state.get("token", "")
                    refresh_token = auth_state.get("refreshToken", "")
                    cust_info = auth_state.get("custInfo")
                except Exception:
                    pass
                if not token:
                    token = middleware.bucketGet(BUCKET_TOKEN, phone) or ""
                target_accounts.append({"phone": phone, "token": token, "refresh_token": refresh_token, "cust_info": cust_info, "user_id": user_id})
                processed_phones.add(phone)
        except Exception:
            pass
    if not target_accounts:
        sender.reply("❌ 未找到已授权且未过期的账号")
        return
    has_refresh_accounts = [acc for acc in target_accounts if acc.get("refresh_token")]
    no_refresh_accounts = [acc for acc in target_accounts if not acc.get("refresh_token")]
    if not has_refresh_accounts:
        sender.reply(f"❌ 找到 {len(target_accounts)} 个已授权且未过期的账号，但都缺少refreshToken，无法刷新")
        return
    sender.reply(
        f"🔄 开始一键刷新全量账号Token\n"
        f"📱 已授权且未过期: {len(target_accounts)}个\n"
        f"✅ 有refreshToken: {len(has_refresh_accounts)}个\n"
        f"❌ 缺少refreshToken: {len(no_refresh_accounts)}个\n"
        f"正在刷新..."
    )
    success_count = 0
    fail_count = 0
    details = []
    failed_accounts_by_user = {}
    for idx, item in enumerate(has_refresh_accounts, 1):
        phone = item.get("phone", "")
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        refresh_token = item.get("refresh_token", "")
        account_key = f"acc_{phone}"
        sender.reply(f"[{idx}/{len(has_refresh_accounts)}] 正在刷新 {masked_phone}...")
        refresh_result = refresh_access_token(refresh_token, account_key=account_key)
        if refresh_result.get("success") and refresh_result.get("token"):
            new_token = refresh_result.get("token", "")
            new_refresh_token = refresh_result.get("refreshToken") or refresh_token
            state_data = {"token": new_token, "refreshToken": new_refresh_token, "custInfo": item.get("cust_info"), "updatedAt": int(time.time())}
            middleware.bucketSet(BUCKET_AUTH_STATE, phone, json.dumps(state_data, ensure_ascii=False))
            middleware.bucketSet(BUCKET_TOKEN, phone, new_token)
            cache_data = {"valid": True, "status": "正常: ✓", "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            middleware.bucketSet(BUCKET_TOKEN_STATUS, phone, json.dumps(cache_data, ensure_ascii=False))
            middleware.bucketSet("G_SYC_fail_count", phone, "0")
            success_count += 1
            details.append(f"✅ {masked_phone}：刷新成功")
        else:
            fail_count += 1
            fail_reason = refresh_result.get("message", "未知错误")
            details.append(f"❌ {masked_phone}：刷新失败（{fail_reason}）")
            cache_data = {"valid": False, "status": "需刷新: ❌", "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": fail_reason}
            middleware.bucketSet(BUCKET_TOKEN_STATUS, phone, json.dumps(cache_data, ensure_ascii=False))
            fail_count_str = middleware.bucketGet("G_SYC_fail_count", phone) or "0"
            try:
                current_fail_count = int(fail_count_str)
            except ValueError:
                current_fail_count = 0
            current_fail_count += 1
            middleware.bucketSet("G_SYC_fail_count", phone, str(current_fail_count))
            if current_fail_count >= 3:
                notify_user_id = item.get("user_id", "")
                if notify_user_id:
                    failed_accounts_by_user.setdefault(notify_user_id, []).append(
                        f"📱 账号: {masked_phone}\n📢 消息:\n❌ 连续{current_fail_count}次刷新失败，请重新登录\n注意：使用APP软件进行充电，就不会掉线了\n注意：使用APP软件进行充电，就不会掉线了\n----------------------------------"
                    )
    for item in no_refresh_accounts:
        phone = item.get("phone", "")
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        details.append(f"⚠️ {masked_phone}：缺少refreshToken，跳过")
        cache_data = {"valid": False, "status": "需刷新: ❌", "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "message": "缺少refreshToken"}
        middleware.bucketSet(BUCKET_TOKEN_STATUS, phone, json.dumps(cache_data, ensure_ascii=False))
        fail_count_str = middleware.bucketGet("G_SYC_fail_count", phone) or "0"
        try:
            current_fail_count = int(fail_count_str)
        except ValueError:
            current_fail_count = 0
        current_fail_count += 1
        middleware.bucketSet("G_SYC_fail_count", phone, str(current_fail_count))
        if current_fail_count >= 3:
            notify_user_id = item.get("user_id", "")
            if notify_user_id:
                failed_accounts_by_user.setdefault(notify_user_id, []).append(
                    f"📱 账号: {masked_phone}\n📢 消息:\n连续{current_fail_count}次缺少refreshToken，请在机器人重新登录\n注意：使用APP软件进行充电，就不会掉线了\n注意：使用APP软件进行充电，就不会掉线了\n----------------------------------"
                )
    notified_users = 0
    for notify_user_id, account_messages in failed_accounts_by_user.items():
        notify_msg = (
            "=====顺易充刷新失败通知=====\n"
            + "\n".join(account_messages)
            + "\n========================"
        )
        push_success = False
        try:
            middleware.push("wx", "", notify_user_id, "顺易充刷新失败通知", notify_msg)
            print(f"✅ 微信推送成功 {notify_user_id}")
            push_success = True
        except Exception as wx_err:
            print(f"⚠️ 微信推送失败 {notify_user_id}: {str(wx_err)[:50]}")
        try:
            middleware.push("qq", "", notify_user_id, "顺易充刷新失败通知", notify_msg)
            print(f"✅ QQ推送成功 {notify_user_id}")
            push_success = True
        except Exception as qq_err:
            print(f"⚠️ QQ推送失败 {notify_user_id}: {str(qq_err)[:50]}")
        if push_success:
            notified_users += 1
    summary = "=====顺易充一键刷新结果=====\n"
    summary += f"📱 已授权且未过期: {len(target_accounts)}个\n"
    summary += f"✅ 刷新成功: {success_count}个\n"
    summary += f"❌ 刷新失败: {fail_count}个\n"
    summary += f"⚠️ 缺少refreshToken: {len(no_refresh_accounts)}个\n"
    summary += f"📤 已推送用户: {notified_users}个\n"
    summary += "========================\n"
    if details:
        summary += "\n" + "\n".join(details)
    sender.reply(summary)


def get_authorized_accounts():
    try:
        all_phones = middleware.bucketAllKeys(BUCKET_AUTH)
        if not all_phones:
            return {}
        authorized_accounts = {}
        for phone in all_phones:
            expire_date = get_auth(phone)
            if expire_date:
                authorized_accounts[phone] = {
                    "expire_date": expire_date,
                    "is_authorized": is_authorized(phone),
                }
        return authorized_accounts
    except Exception as e:
        print(f"⚠️  获取授权账号失败: {str(e)}")
        return {}
def clean_expired_accounts():
    if not is_syc_admin():
        sender.reply("❌ 您没有顺易充管理员权限！")
        return
    sender.reply("🔍 正在检查过期账号...")
    authorized_accounts = get_authorized_accounts()
    if not authorized_accounts:
        sender.reply("❌ 全局授权数据为空")
        return
    expired_phones = []
    valid_count = 0
    for phone, info in authorized_accounts.items():
        if info.get("is_authorized"):
            valid_count += 1
        else:
            expired_phones.append(phone)
    if not expired_phones:
        sender.reply(f"✅ 检查完成\n当前有效账号: {valid_count}个\n无过期账号需要清理")
        return
    sender.reply(
        f"📊 统计结果:\n"
        f"有效账号: {valid_count}个\n"
        f"过期账号: {len(expired_phones)}个\n"
        f"数据大小: 约{len(str(authorized_accounts)) / 1024:.1f}KB\n"
        f"-------------------\n"
        f"🔄 开始自动清理过期账号..."
    )
    deleted_count = 0
    remove_authorized_accounts(expired_phones)
    deleted_count = len(expired_phones)
    remaining_count = valid_count
    sender.reply(
        f"✅ 清理完成！\n"
        f"删除过期账号: {deleted_count}/{len(expired_phones)}个\n"
        f"剩余有效账号: {remaining_count}个\n"
        f"清理内容: 授权记录、Token、Token状态"
    )
def admin_authorize_account():
    if not is_syc_admin():
        sender.reply("❌ 您没有顺易充管理员权限！")
        return
    sender.reply(
        "=====管理员授权操作=====\n"
        "[1] 一键授权所有用户\n"
        "[2] 单独授权用户\n"
        "回复数字选择操作\n"
        "===================="
    )
    choice = sender.input(60000, 1, False)
    if choice is None:
        sender.reply("感谢使用")
        return
    if choice == "1":
        try:
            users = middleware.bucketAllKeys(bucket=BUCKET_USER) or []
        except:
            users = []
        if not users:
            sender.reply("❌ 未找到任何绑定用户")
            return
        sender.reply(
            "请输入授权天数:\n+天数（延长时间，如 +30）\n-天数（减少时间，如 -10）\n直接输入数字（新授权，如 30）"
        )
        days_input = sender.input(120000, 1, False)
        if days_input is None:
            sender.reply("感谢使用")
            return
        days_input = days_input.strip()
        if not days_input:
            sender.reply("❌ 输入不能为空")
            return
        try:
            days = int(days_input)
            if abs(days) < 1 or abs(days) > 365:
                sender.reply("❌ 天数必须为1-365之间的整数")
                return
        except ValueError:
            sender.reply("❌ 天数必须为整数（支持+/-）")
            return
        success_count = 0
        all_authorized_phones = []
        phone_expire_dates = {}
        for user_id in users:
            user_accounts = get_user_accounts(user_id)
            current_time = datetime.now()
            global_authorized_accounts = get_authorized_accounts()
            authorized_phones = []
            for account_id, account_data in user_accounts.items():
                try:
                    phone = account_data.get("phone", "")
                    if not phone or phone == "未知":
                        continue
                    existing_expire_date = None
                    is_expired = False
                    if phone in global_authorized_accounts:
                        try:
                            global_expire_date_str = global_authorized_accounts[phone][
                                "expire_date"
                            ]
                            global_expire_time = datetime.strptime(
                                global_expire_date_str, "%Y-%m-%d"
                            )
                            existing_expire_date = global_expire_time
                            is_expired = global_expire_time.date() < current_time.date()
                        except:
                            pass
                    if existing_expire_date and not is_expired:
                        expire_date = (
                            existing_expire_date + timedelta(days=days)
                        ).strftime("%Y-%m-%d")
                    else:
                        expire_date = (current_time + timedelta(days=days)).strftime(
                            "%Y-%m-%d"
                        )
                    if phone and phone != "未知":
                        authorized_phones.append(phone)
                        all_authorized_phones.append(phone)
                        phone_expire_dates[phone] = expire_date
                    success_count += 1
                except Exception as e:
                    sender.reply(f"❌ 授权用户 {user_id} 失败: {str(e)}")
            if authorized_phones:
                save_authorized_accounts(
                    {phone: phone_expire_dates[phone] for phone in authorized_phones}
                )
        days_display = f"+{days}" if days > 0 else str(days)
        sender.reply(
            f"✅ 一键授权完成！\n授权账号数: {success_count}\n授权天数: {days_display}"
        )
    elif choice == "2":
        sender.reply("请输入需要授权的用户ID:")
        target_userid = sender.input(120000, 1, False)
        if target_userid is None:
            sender.reply("感谢使用")
            return
        if not target_userid:
            sender.reply("❌ 用户ID无效")
            return
        accounts = get_user_accounts(target_userid)
        if not accounts:
            sender.reply(f"❌ 用户 {target_userid} 未绑定任何顺易充账号")
            return
        account_lines = []
        account_ids = []
        for i, (account_id, account) in enumerate(accounts.items(), 1):
            phone = account.get("phone", "📱 未知手机号")
            account_lines.append(f"[{i}] {phone}")
            account_ids.append(account_id)
        account_list = "\n".join(account_lines)
        sender.reply(
            "=====用户账号列表=====\n"
            f"账号列表:\n{account_list}\n"
            "------------------\n"
            "回复 [0] 授权全部账号\n"
            "回复序号授权单个账号\n"
            "\n"
            "💡 批量选择示例:\n"
            "   范围选择: 3-6\n"
            "   多个选择: 1,4,6\n"
            "   混合选择: 1,3-5,8\n"
            "===================="
        )
        account_choice = sender.input(120000, 1, False)
        if account_choice is None:
            sender.reply("感谢使用")
            return
        to_authorize_ids = []
        if account_choice == "0":
            to_authorize_ids = account_ids
        else:
            selected_indices = parse_account_selection(account_choice, len(account_ids))
            if selected_indices is None:
                sender.reply(
                    "❌ 选择格式无效！请使用正确格式:\n单个: 3\n范围: 3-6\n多个: 1,4,6\n混合: 1,3-5,8"
                )
                return
            if not selected_indices:
                sender.reply("❌ 未选择任何账号")
                return
            to_authorize_ids = [account_ids[idx] for idx in selected_indices]
        sender.reply(
            "请输入授权天数:\n+天数（延长时间，如 +30）\n-天数（减少时间，如 -10）\n直接输入数字（新授权，如 30）"
        )
        days_input = sender.input(120000, 1, False)
        if days_input is None:
            sender.reply("感谢使用")
            return
        days_input = days_input.strip()
        if not days_input:
            sender.reply("❌ 输入不能为空")
            return
        try:
            days = int(days_input)
            if abs(days) < 1 or abs(days) > 365:
                sender.reply("❌ 天数必须为1-365之间的整数")
                return
        except ValueError:
            sender.reply("❌ 天数必须为整数（支持+/-）")
            return
        authorized_count = 0
        current_time = datetime.now()
        global_authorized_accounts = get_authorized_accounts()
        authorized_phones = []
        phone_expire_dates = {}
        for account_id in to_authorize_ids:
            if account_id in accounts:
                phone = accounts[account_id].get("phone", "")
                existing_expire_date = None
                is_expired = False
                # 【修复】优先从全局授权数据获取（权威数据源），与 handle_auth_days 保持一致
                if phone in global_authorized_accounts:
                    try:
                        global_expire_date_str = global_authorized_accounts[phone][
                            "expire_date"
                        ]
                        global_expire_time = datetime.strptime(
                            global_expire_date_str, "%Y-%m-%d"
                        )
                        existing_expire_date = global_expire_time
                        is_expired = global_expire_time.date() < current_time.date()
                    except:
                        pass
                # 如果全局数据没有，再从用户账号数据获取
                if existing_expire_date is None and accounts[account_id].get(
                    "auth_status", {}
                ).get("is_authorized"):
                    try:
                        expire_time_str = accounts[account_id]["auth_status"][
                            "expire_time"
                        ]
                        expire_time = datetime.strptime(expire_time_str, "%Y-%m-%d")
                        existing_expire_date = expire_time
                        is_expired = expire_time.date() < current_time.date()
                    except:
                        pass
                if existing_expire_date and not is_expired:
                    expire_date = (
                        existing_expire_date + timedelta(days=days)
                    ).strftime("%Y-%m-%d")
                else:
                    expire_date = (current_time + timedelta(days=days)).strftime(
                        "%Y-%m-%d"
                    )
                is_renewal = existing_expire_date is not None
                if phone and phone != "未知":
                    authorized_phones.append((phone, is_renewal))
                    phone_expire_dates[phone] = expire_date
                authorized_count += 1
        phones_only = [phone for phone, _ in authorized_phones]
        if phones_only:
            save_authorized_accounts(phone_expire_dates)
        is_renewals = {phone: is_renewal for phone, is_renewal in authorized_phones}
        if phones_only:
            expire_date_summary = "、".join(
                [f"{phone}: {phone_expire_dates[phone]}" for phone in phones_only]
            )
            save_auth_record(phones_only, expire_date_summary, days, is_renewals)
            days_display = f"+{days}" if days > 0 else str(days)
            sender.reply(
                f"✅ 管理员授权成功\n"
                f"授权账号数: {authorized_count}\n"
                f"授权天数: {days_display}\n"
                f"到期时间:\n{expire_date_summary}"
            )
        else:
            sender.reply("❌ 没有找到可授权的账号")
    else:
        sender.reply("❌ 无效选择")
def run_task_for_account(phone, token, account_id=None, user_id=None):
    try:
        if not token:
            return {
                "phone": phone,
                "masked_phone": phone[:3] + "****" + phone[-4:]
                if len(phone) == 11
                else phone,
                "success": False,
                "error": "Token为空",
                "details": [],
                "account_id": account_id,
                "user_id": user_id,
            }
        account_key = f"acc_{phone}"
        if not token.lower().startswith("bearer "):
            token = f"Bearer {token}"
        headers = get_task_headers()
        headers["authorization"] = token
        headers["_account_key"] = account_key  # 在headers中传递账号标识
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        result = {
            "phone": phone,
            "masked_phone": masked_phone,
            "success": False,
            "error": None,
            "details": [],
            "account_id": account_id,
            "user_id": user_id,
        }
        try:
            sign_result, sign_success = perform_daily_sign_in_task(headers)
            result["details"].append(sign_result)
        except Exception as e:
            error_msg = f"签到异常: {str(e)}"
            result["details"].append(f"❌ {error_msg}")
            result["error"] = error_msg
        try:
            available_tasks, _ = check_task_status_task(headers)
            if available_tasks:
                task_count = 0
                for task in available_tasks:
                    if task.get("type") != "1216":
                        try:
                            claim_result, success = claim_task_reward_task(
                                headers, task
                            )
                            if success:
                                task_count += 1
                            time.sleep(1)
                        except Exception as e:
                            result["details"].append(f"❌ 任务领取异常: {str(e)}")
                if task_count > 0:
                    result["details"].append(f"✅ 成功领取 {task_count} 个任务奖励")
        except Exception as e:
            error_msg = f"任务检查异常: {str(e)}"
            result["details"].append(f"❌ {error_msg}")
            if not result["error"]:
                result["error"] = error_msg
        # 视频任务已屏蔽，只保留签到
        # try:
        #     video_result, video_success = complete_enhanced_video_task_plugin(
        #         headers, phone
        #     )
        #     result["details"].append(f"✅ {video_result}")
        # except Exception as e:
        #     error_msg = f"视频任务异常: {str(e)}"
        #     result["details"].append(f"❌ {error_msg}")
        #     if not result["error"]:
        #         result["error"] = error_msg
        try:
            score_info = get_score_rank_task(headers)
            if score_info:
                result["details"].append(
                    f"🏆 积分: {score_info['积分']}"
                )
            else:
                result["details"].append("⚠️ 获取积分信息失败")
        except Exception as e:
            error_msg = f"获取积分异常: {str(e)}"
            result["details"].append(f"❌ {error_msg}")
            if not result["error"]:
                result["error"] = error_msg
        if (
            not result["error"]
            or len([d for d in result["details"] if d.startswith("✅")]) > 0
        ):
            result["success"] = True
        return result
    except Exception as e:
        return {
            "phone": phone,
            "masked_phone": phone[:3] + "****" + phone[-4:]
            if len(phone) == 11
            else phone,
            "success": False,
            "error": f"账号执行异常: {str(e)}",
            "details": [f"❌ 执行任务时发生异常: {str(e)}"],
            "account_id": account_id,
            "user_id": user_id,
        }
def execute_single_account(account_data, user_accounts_dict, lock):
    account_id, account = account_data
    result = {"success": False, "error": None, "masked_phone": "未知", "details": []}
    try:
        phone = account.get("phone")
        if not phone:
            result["error"] = "账号信息不完整，跳过"
            result["masked_phone"] = "未知"
            return result
        result["masked_phone"] = (
            phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        )
        current_user_id = account.get("user_id", userid)
        token = account.get("token", "")
        if not token:
            result["error"] = "未找到保存的token，请重新绑定账号"
            return result
        task_result = run_task_for_account(phone, token, account_id, current_user_id)
        result["success"] = task_result["success"]
        result["error"] = task_result["error"]
        result["details"] = task_result["details"]
        return result
    except Exception as e:
        result["error"] = f"执行异常: {str(e)}"
        return result
def run_user_tasks():
    config = get_config()
    concurrent_count = config.get("concurrent_count", 3)
    user_accounts = get_user_accounts()
    if not user_accounts:
        sender.reply("您还没有绑定任何顺易充账号，请先绑定账号")
        return
    valid_accounts = {}
    expired_token_accounts = []
    unauthorized_accounts = []
    for account_id, account in user_accounts.items():
        is_authorized = account.get("auth_status", {}).get("is_authorized", False)
        token = account.get("token", "")
        phone = account.get("phone", "")
        if not is_authorized or not check_auth_validity(account.get("auth_status", {})):
            unauthorized_accounts.append(phone)
            continue
        if not token:
            expired_token_accounts.append((phone, "未保存账号"))
            continue
        token_valid, token_msg = check_token_validity(token, phone)
        if token_valid:
            valid_accounts[account_id] = account
        else:
            expired_token_accounts.append((phone, token_msg))
    if unauthorized_accounts:
        sender.reply(f"⚠️ 发现 {len(unauthorized_accounts)} 个未授权账号，请先授权")
    if expired_token_accounts:
        expired_msg = "⚠️ 以下账号已过期，需要重新绑定：\n"
        for phone, reason in expired_token_accounts:
            masked_phone = (
                phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
            )
            expired_msg += f"📱 {masked_phone} - {reason}\n"
        expired_msg += "\n请发送「顺易充登录」重新绑定这些账号"
        sender.reply(expired_msg)
    if not valid_accounts:
        sender.reply("❌ 没有找到可运行的授权账号")
        return
    enhanced_status = "启用" if config.get("use_enhanced_ads", True) else "禁用"
    sender.reply(
        f"🔍 找到可运行的授权账号：{len(valid_accounts)}个\n⚙️ 并发数量：{concurrent_count}\n🚀 增强广告系统：{enhanced_status}\n\n开始执行任务..."
    )
    execute_tasks_for_accounts(valid_accounts, concurrent_count, config)
def execute_tasks_for_accounts(valid_accounts, concurrent_count, config):
    success_count = 0
    fail_count = 0
    successful_results = []
    failed_results = []
    lock = threading.Lock()
    user_accounts_dict = {}
    sender.reply(f"🚀 开始执行任务，共{len(valid_accounts)}个账号...")
    with ThreadPoolExecutor(max_workers=concurrent_count) as executor:
        future_to_account = {
            executor.submit(
                execute_single_account, (account_id, account), user_accounts_dict, lock
            ): (account_id, account)
            for account_id, account in valid_accounts.items()
        }
        completed_count = 0
        for future in as_completed(future_to_account):
            account_id, account = future_to_account[future]
            completed_count += 1
            try:
                result = future.result()
                if result["success"]:
                    success_count += 1
                    successful_results.append(
                        {
                            "masked_phone": result["masked_phone"],
                            "details": result["details"],
                        }
                    )
                else:
                    fail_count += 1
                    failed_results.append(
                        {
                            "masked_phone": result["masked_phone"],
                            "error": result["error"],
                            "phone": account.get("phone", "未知"),
                        }
                    )
                if (
                    completed_count % 10 == 0
                    or completed_count % max(1, len(valid_accounts) // 4) == 0
                ):
                    progress = int((completed_count / len(valid_accounts)) * 100)
                    sender.reply(
                        f"⏳ 进度: {completed_count}/{len(valid_accounts)} ({progress}%) | ✅{success_count} ❌{fail_count}"
                    )
            except Exception as e:
                fail_count += 1
                phone = account.get("phone", "未知")
                masked_phone = (
                    phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                )
                failed_results.append(
                    {
                        "masked_phone": masked_phone,
                        "error": f"任务执行异常: {str(e)}",
                        "phone": phone,
                    }
                )
    summary = f"=====顺易充任务完成=====\n"
    summary += f"📱 任务账号: {len(valid_accounts)}个\n"
    summary += f"⚙️ 并发数量: {concurrent_count}\n"
    summary += f"🚀 增强广告系统: {'启用' if config.get('use_enhanced_ads', True) else '禁用'}\n"
    summary += f"✅ 成功: {success_count}个\n"
    summary += f"❌ 失败: {fail_count}个\n"
    summary += "====================\n\n"
    if successful_results:
        summary += "✅ 成功账号详情:\n"
        for i, result in enumerate(successful_results, 1):
            summary += f"[{i}] 📱 {result['masked_phone']}\n"
            for detail in result["details"]:
                summary += f"    {detail}\n"
            summary += "--------------------\n"
        summary += "\n"
    if failed_results:
        summary += "❌ 失败账号详情:\n"
        for i, result in enumerate(failed_results, 1):
            summary += f"[{i}] 📱 {result['masked_phone']}\n"
            summary += f"    ❌ 错误: {result['error']}\n"
            summary += "--------------------\n"
        summary += "\n"
        failed_phones = [
            result["phone"] for result in failed_results if result["phone"] != "未知"
        ]
        if failed_phones:
            summary += f"📋 失败账号手机号: {', '.join(failed_phones)}\n"
    sender.reply(summary)
def run_single_account_task(account_id, user_accounts):
    if account_id not in user_accounts:
        sender.reply("❌ 账号不存在")
        return
    account = user_accounts[account_id]
    phone = account.get("phone", "")
    token = account.get("token", "")
    if not phone:
        sender.reply("❌ 账号信息不完整")
        return
    is_authorized = account.get("auth_status", {}).get("is_authorized", False)
    if not is_authorized or not check_auth_validity(account.get("auth_status", {})):
        sender.reply(f"❌ 账号 {phone} 未授权，请先授权后再运行任务")
        return
    if not token:
        sender.reply(f"❌ 账号 {phone} 未保存账号，请重新绑定账号")
        return
    sender.reply("🔍 正在验证账号状态...")
    token_valid, token_msg = check_token_validity(token, phone)
    if not token_valid:
        sender.reply(
            f"❌ Token验证失败: {token_msg}\n💡 请发送「顺易充登录」重新绑定账号"
        )
        return
    masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
    sender.reply(f"🚀 开始为账号 {masked_phone} 执行任务...")
    try:
        task_result = run_task_for_account(phone, token, account_id, userid)
        if task_result["success"]:
            success_msg = f"✅ 账号 {masked_phone} 任务完成！\n"
            success_msg += "详情:\n"
            for detail in task_result["details"]:
                success_msg += f"  {detail}\n"
            sender.reply(success_msg)
        else:
            fail_msg = f"❌ 账号 {masked_phone} 任务失败！\n"
            fail_msg += f"错误: {task_result['error']}\n"
            if task_result["details"]:
                fail_msg += "详情:\n"
                for detail in task_result["details"]:
                    fail_msg += f"  {detail}\n"
            sender.reply(fail_msg)
    except Exception as e:
        sender.reply(f"❌ 账号 {masked_phone} 任务执行异常: {str(e)}")
def run_all_tasks():
    config = get_config()
    concurrent_count = config.get("concurrent_count", 3)
    valid_accounts = {}
    is_admin = sender.isAdmin()
    if is_admin:
        try:
            users = middleware.bucketAllKeys(BUCKET_USER) or []
        except:
            users = []
        all_accounts = {}
        skipped_count = 0
        for user_id in users:
            try:
                phones = get_user_phones(user_id)
                for phone in phones:
                    auth_status = build_auth_status(phone)
                    if not auth_status.get("is_authorized"):
                        continue
                    token = middleware.bucketGet(BUCKET_TOKEN, phone) or ""
                    if not token:
                        print(f"⚠️ 跳过账号 {phone}: Token缺失")
                        skipped_count += 1
                        continue
                    token_valid, token_msg = check_token_validity(token, phone)
                    if not token_valid:
                        print(f"⚠️ 跳过账号 {phone}: {token_msg}")
                        skipped_count += 1
                        continue
                    account_id = f"{phone}_{uuid.uuid4().hex[:8]}"
                    all_accounts[account_id] = {
                        "phone": phone,
                        "token": token,
                        "user_id": user_id,
                        "auth_status": auth_status,
                    }
            except Exception as e:
                print(f"获取用户 {user_id} 的账号信息失败: {str(e)}")
        valid_accounts = all_accounts
        enhanced_status = "启用" if config.get("use_enhanced_ads", True) else "禁用"
        sender.reply(
            f"🔍 找到所有用户的授权账号：{len(valid_accounts)}个\n⚠️ 跳过Token失效账号：{skipped_count}个\n⚙️ 并发数量：{concurrent_count}\n🚀 增强广告系统：{enhanced_status}"
        )
    else:
        sender.reply(
            "❌ 非管理员用户请使用「顺易充运行」指令\n💡 该指令只运行您自己的已授权账号"
        )
        return
    if not valid_accounts:
        sender.reply(f"❌ 没有找到授权账号，请先授权账号")
        return
    execute_tasks_for_accounts(valid_accounts, concurrent_count, config)
def perform_daily_sign_in_task(headers):
    try:
        url = "https://app.wodeev.com/bil-front/v2.0/activity/getWelfare"
        payload = {"type": "1201", "taskNo": "20221231"}
        account_key = headers.get("_account_key")  # 从 headers 提取账号标识
        response = request_with_retry(
            "POST",
            url,
            headers=headers,
            json=payload,
            timeout=10,
            verify=False,
            account_key=account_key,
        )
        res_data = response.json()
        ret_code = res_data.get("ret", "未知")
        msg = res_data.get("msg", "无返回信息")
        if ret_code == 200 or ret_code == "200":
            if msg == "调用成功":
                return "✅ 签到成功", True
            else:
                return "✅ 签到成功", True
        elif ret_code == 400 or ret_code == "400":
            if "超过最大可领取次数" in msg:
                return "✅ 今日已签到", True
            else:
                return "❌ 签到失败: " + msg, False
        else:
            print(f"签到返回码: {ret_code}, 消息: {msg}")
            return "❌ 签到失败", False
    except Exception as e:
        return "❌ 签到异常: " + str(e), False
def check_task_status_task(headers):
    try:
        url = "https://app.wodeev.com/bil-front/v2.0/activity/queryWelfareList"
        account_key = headers.get("_account_key")  # 从 headers 提取账号标识
        response = request_with_retry(
            "GET",
            url,
            headers=headers,
            timeout=10,
            verify=False,
            account_key=account_key,
        )
        res_data = response.json()
        if res_data.get("ret") != 200 and res_data.get("ret") != "200":
            return [], False
        available_tasks = []
        task_list = res_data.get("data", {}).get("list", [])
        for task in task_list:
            status = task.get("status")
            if status == "0" or status == 0:
                available_tasks.append(task)
        return available_tasks, True
    except Exception as e:
        return [], False
def claim_task_reward_task(headers, task):
    try:
        task_type = task.get("type")
        task_no = task.get("taskNo")
        task_name = task.get("name", "未知任务")
        account_key = headers.get("_account_key")  # 从 headers 提取账号标识
        payload = {"type": task_type, "taskNo": task_no}
        url = "https://app.wodeev.com/bil-front/v2.0/activity/getWelfare"
        response = request_with_retry(
            "POST",
            url,
            headers=headers,
            json=payload,
            timeout=10,
            verify=False,
            account_key=account_key,
        )
        res_data = response.json()
        ret_code = res_data.get("ret", "未知")
        if ret_code == 200 or ret_code == "200":
            return True, True
        else:
            return False, False
    except Exception as e:
        return False, False
def get_score_rank_task(headers):
    try:
        account_key = headers.get("_account_key")
        url = "https://app.wodeev.com/bil-front/v2.0/accounts/myScoreRank?scoreType=02"
        response = request_with_retry(
            "GET",
            url,
            headers=headers,
            timeout=10,
            verify=False,
            account_key=account_key,
        )
        res_data = response.json()
        if res_data.get("ret") != 200 and res_data.get("ret") != "200":
            print(f"获取积分接口返回错误: {res_data.get('ret')} - {res_data.get('msg', '无错误信息')}")
            return None
        data = res_data.get("data", {})
        return {
            "积分": data.get("myScores", "0"),
            "可用积分": data.get("myAvailableScores", "0"),
            "排名": data.get("myRank", "未知"),
        }
    except Exception as e:
        print(f"获取积分信息异常: {str(e)}")
        return None
def get_year_score_task(headers, year=None):
    try:
        if year is None:
            year = datetime.now().year
        year_prefix = str(year)
        total_earned = 0
        page_num = 1
        max_pages = 20
        page_size = 100
        account_key = headers.get("_account_key")
        while page_num <= max_pages:
            url = f"https://app.wodeev.com/def-front/v2.0/accounts/pointsInfo?pageNum={page_num}&totalNum={page_size}"
            response = request_with_retry(
                "GET", url, headers=headers, timeout=10, verify=False, account_key=account_key,
            )
            data = response.json()
            if data.get("ret") != 200 and data.get("ret") != "200":
                break
            change_list = data.get("changeList", [])
            if not change_list:
                break
            found_older = False
            for record in change_list:
                record_time = record.get("time", "")
                if record_time < year_prefix:
                    found_older = True
                    break
                if record_time.startswith(year_prefix) and record.get("changeType") == "01":
                    try:
                        total_earned += int(float(record.get("points", "0")))
                    except:
                        pass
            if found_older or len(change_list) < page_size:
                break
            page_num += 1
        return str(total_earned)
    except Exception as e:
        print(f"获取{year}年积分异常: {str(e)}")
        return None
if __name__ == "__main__":
    try:
        command = sender.getMessage()
    except Exception:
        command = ""
    # 使用正则匹配支持 顺易充/syc 两种前缀
    cmd_match = re.match(
        r"^(顺易充|syc)(登录|登陆|绑定|管理|查询|授权|运行|一键运行|清理|刷新|一键刷新)$",
        command,
        re.IGNORECASE,
    )
    if cmd_match:
        action = cmd_match.group(2)
        if action in ["登录", "登陆", "绑定"]:
            bind_account()
        elif action == "管理":
            manage_accounts()
        elif action == "查询":
            query_user_points()
        elif action == "授权":
            if is_syc_admin():
                admin_authorize_account()
            else:
                sender.reply(
                    "❌ 您没有顺易充管理员权限，无法使用授权功能！\n请发送「顺易充管理」或「syc管理」管理您自己的账号"
                )
        elif action == "运行":
            run_user_tasks()
        elif action == "一键运行":
            run_all_tasks()
        elif action == "清理":
            if is_syc_admin():
                clean_expired_accounts()
            else:
                sender.reply("❌ 您没有顺易充管理员权限！")
        elif action == "刷新":
            user_refresh_tokens()
        elif action == "一键刷新":
            admin_refresh_all_tokens()
    else:
        sender.reply("未知指令，请发送「顺易充管理」或「syc管理」查看账号管理")
