# [pin:true]
# [author: yueiqiu4523]
# [title: 和合天台]
# [language: python]
# [class: 工具类]
# [service: 3116835832] 售后联系方式
# [disable:false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^^和合天台登录$|^和合天台登陆$|^登陆和合天台$|^登录和合天台$|^和合天台查询$|^查询和合天台$|^和合天台管理$|^和合天台教程$|^和合天台清理$|^和合天台授权$|^和合天台签到$|^和合天台中奖推送$|^和合天台一键运行$]
# [cron: 0 8 * * *] cron定时，支持5位域和6位域
# [priority: 55] 优先级，数字越大表示优先级越高
# [platform: all] 适用的平台
# [open_source: false]是否开源
# [icon: https://www.yili.com/static/images/logo.png]图标链接
# [version: 1.6.1]版本号
#[public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 8.88] 上架价格
# [description: 和合天台APP插件📱插件群过年送插件：833593655<br>支持签到、阅读、评论、分享、发帖及抽奖<br>1.使用手机号+密码登录<br>2.支持积分查询、每日任务执行<br>3.支持抽奖功能<br>4.更新了和合天台的查询显示支持，查询总额和提多少和还有多少没提<br>5.新增中奖通知定时推送<br>6.新增自动提现和提现门槛设置]

# [param: {"required":true,"key":"JQB.hhtt.zsm","bool":false,"placeholder":"收款码地址","name":"收款码地址","desc":"赞赏码或收款码地址"}]
# [param: {"required":true,"key":"JQB.hhtt.ql_host","bool":false,"placeholder":"http://127.0.0.1:5700","name":"青龙地址","desc":""}]
# [param: {"required":true,"key":"JQB.hhtt.ql_client_id","bool":false,"placeholder":"","name":"青龙应用ID","desc":""}]
# [param: {"required":true,"key":"JQB.hhtt.ql_client_secret","bool":false,"placeholder":"","name":"青龙应用密钥","desc":""}]
# [param: {"required":true,"key":"JQB.hhtt.var_name","bool":false,"placeholder":"hhtt","name":"环境变量名","desc":"青龙容器内的变量名"}]
# [param: {"required":true,"key":"JQB.hhtt.price","bool":false,"placeholder":"1","name":"上车价格","desc":"上车价格(单位:元)/30天"}]
# [param: {"required":true,"key":"JQB.hhtt.coin","bool":false,"placeholder":"0","name":"积分开通","desc":"授权一个月的积分"}]
# [param: {"required":true,"key":"JQB.hhtt.coin_bucket","bool":false,"placeholder":"dd_sign_points","name":"积分数据桶","desc":""}]
# [param: {"required":true,"key":"JQB.hhtt.proxy_pool","bool":false,"placeholder":"http://代理池API","name":"代理池地址","desc":""}]
# [param: {"required":false,"key":"JQB.hhtt.link","bool":false,"placeholder":"https://act.tmlyun.com/lottery/?q=...","name":"抽奖链接","desc":"和合天台抽奖链接，每月更新"}]
# [param: {"required":false,"key":"JQB.hhtt.withdraw_threshold","bool":false,"placeholder":"2","name":"提现门槛","desc":"余额大于等于该值时自动提现(元)"}]

import re
from datetime import datetime, timedelta
import middleware
import urllib.parse
import urllib3
from decimal import Decimal
import requests
import time
import json
import hashlib
import uuid
import asyncio
import aiohttp
from functools import lru_cache
import traceback
import random
import base64
import sys
import os
from typing import Optional, Dict, Tuple, List, Any
from urllib.parse import quote, unquote, urlparse, parse_qs

# 尝试导入Crypto模块
try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# 禁用SSL警告
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 代理配置
MAX_RETRIES = 3
IS_PROXY = False
PROXY_API = middleware.bucketGet('JQB.hhtt', 'proxy_pool') or "http://代理池API"
proxy = None

# 提现门槛（全局配置）
WITHDRAW_THRESHOLD = float(middleware.bucketGet('JQB.hhtt', 'withdraw_threshold') or '2')

def mask_phone(phone):
    """将手机号打码显示，如：138****8888"""
    if len(phone) != 11:
        return phone  # 如果不是11位手机号，原样返回
    return phone[:3] + '****' + phone[7:]

def update_proxy():
    """更新代理IP地址"""
    global proxy
    try:
        if not IS_PROXY:
            proxy = None
            return
        response = requests.get(PROXY_API, timeout=10)
        ip = response.text.strip()
        proxy = {'http': ip, 'https': ip}
    except Exception as e:
        print(f"代理获取失败: {str(e)}")
        proxy = None

def _send_request(method, url, **kwargs):
    """带代理重试的请求方法"""
    global proxy
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            if IS_PROXY and not proxy:
                update_proxy()
            kwargs['timeout'] = kwargs.get('timeout', 15)
            kwargs['verify'] = False  # 忽略SSL验证
            response = requests.request(
                method=method,
                url=url,
                proxies=proxy if IS_PROXY and proxy else None,
                **kwargs
            )
            response.raise_for_status()
            return response
        except (requests.exceptions.ProxyError, requests.exceptions.Timeout) as e:
            print(f"代理异常: {str(e)}")
            if IS_PROXY:
                update_proxy()
                attempts += 1
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}")
            attempts += 1
            if attempts == MAX_RETRIES:
                raise

# ========================= 和合天台专用类 =========================

class SecurityProvider:
    PUB_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXi
zPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXF
c+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlT
HMlluw4ZYmnOwg+thwIDAQAB
-----END PUBLIC KEY-----"""

    @staticmethod
    def rsa_encrypt(content: str) -> str:
        if not CRYPTO_AVAILABLE:
            raise ImportError("Crypto模块未安装，请安装pycryptodome库")
        try:
            rsa_key = RSA.import_key(SecurityProvider.PUB_KEY_PEM)
            cipher = PKCS1_v1_5.new(rsa_key)
            encrypted_bytes = cipher.encrypt(content.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            print(f"加密过程发生错误: {e}")
            return ""

    @staticmethod
    def generate_signature(path: str, session_id: str, req_id: str, timestamp: str) -> str:
        clean_path = path.split('?')[0] if '?' in path else path
        raw_str = f"{clean_path}&&{session_id}&&{req_id}&&{timestamp}&&FR*r!isE5W&&5"
        return hashlib.sha256(raw_str.encode()).hexdigest()

    @staticmethod
    def deterministic_uuid(seed_key: str) -> str:
        m = hashlib.md5(seed_key.encode()).hexdigest()
        s = hashlib.sha256(seed_key.encode()).hexdigest()
        return f"00000000-{s[8:12]}-{s[20:24]}-ffff-{m[16:28]}"

class DeviceManager:
    POOLS = {
        0: ("xiaomi", ["23116PN5BC", "23127PN0CC", "24030PN60C", "23113RKC6C", "2311DRK48C"]),
        1: ("samsung", ["SM-S9280", "SM-S9210", "SM-S9180", "SM-F9460", "SM-S7110"]),
        2: ("huawei", ["ALN-AL00", "ALN-AL80", "HBP-AL00", "ALT-AL10", "BRA-AL00"]),
        3: ("oppo", ["PHY110", "PHZ110", "PJH110", "PJD110", "PHN110"]),
        4: ("vivo", ["V2309A", "V2324A", "V2307A", "V2337A", "V2302A"]),
        5: ("oneplus", ["PJD110", "PJE110", "PHP110", "PHB110", "PHK110"]),
    }

    @classmethod
    def get_ua(cls, phone: str) -> str:
        seed_int = int(hashlib.md5(phone.encode()).hexdigest()[:8], 16)
        uuid_val = SecurityProvider.deterministic_uuid(phone)

        last_num = int(phone[-1]) if phone[-1].isdigit() else 0
        brand_idx = last_num % len(cls.POOLS)
        brand_name, model_list = cls.POOLS[brand_idx]

        if len(phone) >= 6:
            mid_idx = int(phone[len(phone) // 2])
        else:
            mid_idx = seed_int

        model_idx = mid_idx % len(model_list)
        device_model = model_list[model_idx]

        phone_sum = sum(int(c) for c in phone if c.isdigit())
        if phone_sum % 10 < 2:
            os_sys = "iOS"
            ver_list = ["17.4.1", "17.3", "16.7.2", "18.0", "17.5"]
            ios_list = ["iPhone16,2", "iPhone15,3", "iPhone15,2", "iPhone14,3", "iPhone13,4"]
            device_model = ios_list[mid_idx % len(ios_list)]
            brand_name = "apple"
        else:
            os_sys = "Android"
            ver_list = ["14", "13", "12", "11", "15"]

        ver_offset = int(phone[-2:]) if len(phone) >= 2 else 0
        ver_idx = (seed_int + ver_offset) % len(ver_list)
        os_ver = ver_list[ver_idx]

        return f"4.5.6;{uuid_val};{device_model};{os_sys};{os_ver};{brand_name.lower()};6.8.0"

class SkyTClient:
    HOST = "vapp.tmuyun.com"
    AUTH_HOST = "passport.tmuyun.com"
    ACT_HOST = "act.tmlyun.com"
    MY_HOST = "my.tmlyun.com"  # 新增：我的钱包主机
    HITOKOTO_API = "https://v1.hitokoto.cn/"

    def __init__(self, raw_data: str):
        parts = raw_data.split("#")
        self.phone = parts[0]
        self.pwd = parts[1]
        self.masked_phone = mask_phone(self.phone)

        # 获取抽奖链接
        raw_q = ""
        if len(parts) >= 3:
            raw_q = parts[2]
        else:
            # 从配置获取全局抽奖链接
            raw_q = middleware.bucketGet('JQB.hhtt', 'link') or ""

        if raw_q:
            self.q = unquote(raw_q.replace("https://act.tmlyun.com/lottery/?q=", ""))
        else:
            self.q = ""

        self.ua = DeviceManager.get_ua(self.phone)
        self.sess = requests.Session()
        self.proxy_dict = None

        self.session_id = ""
        self.account_id = ""
        self.lottery_token = ""
        self.equity_token_cache = ""
        self.alipay_balance = 0.0
        self.y_token = ""

        # 提现开关（从账号存储中读取，由外部传入）
        self.withdraw_enabled = False  # 默认关闭，外部设置

    def _refresh_proxy(self):
        if not IS_PROXY or not PROXY_API:
            return
        try:
            response = requests.get(PROXY_API, timeout=5)
            ip = response.text.strip()
            if ":" in ip:
                self.proxy_dict = {"http": ip, "https": ip}
        except Exception:
            self.proxy_dict = None

    def _api_call(self, method: str, url: str, headers: Dict = None, data: Any = None, is_json: bool = False, params: Dict = None) -> Dict:
        attempts = 0
        while attempts < MAX_RETRIES:
            try:
                if IS_PROXY and not self.proxy_dict:
                    self._refresh_proxy()

                req_args = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                    "timeout": 15,
                    "proxies": self.proxy_dict,
                    "verify": False
                }

                if is_json:
                    req_args["json"] = data
                else:
                    req_args["data"] = data

                if params:
                    req_args["params"] = params

                resp = self.sess.request(**req_args)
                resp.raise_for_status()
                return resp.json()

            except Exception as e:
                attempts += 1
                print(f"[{self.masked_phone}] 请求失败 (重试 {attempts}): {str(e)}")
                if IS_PROXY:
                    time.sleep(1)
                    self._refresh_proxy()
        raise Exception("网络连接失败")

    def _build_headers(self, path: str, content_type: str = None) -> Dict:
        req_id = str(uuid.uuid4())
        ts = str(int(time.time() * 1000))
        sign = SecurityProvider.generate_signature(path, self.session_id, req_id, ts)

        h = {
            "User-Agent": self.ua,
            "Host": self.HOST,
            "X-TENANT-ID": "5",
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": req_id,
            "X-TIMESTAMP": ts,
            "X-SIGNATURE": sign,
            "X-ACCOUNT-ID": self.account_id,
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip"
        }
        if content_type:
            h["Content-Type"] = content_type
        return h

    # ---------- 修复点：添加备用一言接口 ----------
    def fetch_comment_text(self) -> Tuple[str, str]:
        try:
            params = {
                "c": ["d", "i"],
                "encode": "json",
                "charset": "utf-8"
            }
            r = requests.get(self.HITOKOTO_API, params=params, verify=False, timeout=3)
            if r.status_code == 200:
                data = r.json()
                content = data.get("hitokoto", "")
                source = data.get("from", "") or data.get("from_who", "") or "随笔"

                if content:
                    return source, content
        except Exception as e:
            print(f"一言接口请求异常: {e}，尝试使用备用接口")

            # 备用接口
            try:
                backup_url = "http://api.yviii.com/yiyan/yi.php/?syz=js&charset=utf-8"
                r2 = requests.get(backup_url, verify=False, timeout=5)
                if r2.status_code == 200:
                    # 使用正则匹配解析返回数据：function hiyi(){document.write('内容');}
                    match = re.search(r"document\.write\('(.*?)'\);?", r2.text)
                    if match:
                        content = match.group(1)
                        return "佚名", content
            except Exception as e2:
                print(f"备用一言接口请求也异常: {e2}")

        fallback_quotes = [
            ("佚名", "俯仰不愧天地，褒贬自有春秋。"),
            ("佚名", "相思本是无凭语，莫向花笺费泪行"),
            ("随感", "庭院深深深几许，杨柳堆烟，帘幕无重数")
        ]
        return random.choice(fallback_quotes)

    def execute_login(self) -> bool:
        try:
            # 初始化session
            path_init = "/api/account/init"
            res = self._api_call("POST", f"https://{self.HOST}{path_init}",
                                 headers=self._build_headers(path_init,
                                                             "application/x-www-form-urlencoded;charset=utf-8"))
            self.session_id = (res.get("data") or {}).get("session", {}).get("id", "")

            # 密码加密
            enc_pwd = SecurityProvider.rsa_encrypt(self.pwd)
            cred_req_id = str(uuid.uuid4())
            cred_ts = str(int(time.time() * 1000))
            cred_path = "/web/oauth/credential_auth"
            cred_sign = SecurityProvider.generate_signature(cred_path, self.session_id, cred_req_id, cred_ts)

            auth_payload = {
                "client_id": "10",
                "password": enc_pwd,
                "phone_number": self.phone
            }
            auth_headers = {
                "User-Agent": self.ua,
                "X-REQUEST-ID": cred_req_id,
                "X-SIGNATURE": cred_sign,
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Host": self.AUTH_HOST
            }

            auth_res = self._api_call("POST", f"https://{self.AUTH_HOST}{cred_path}",
                                      headers=auth_headers, data=auth_payload)
            code = (auth_res.get("data") or {}).get("authorization_code", {}).get("code", "")

            # 登录
            login_path = "/api/zbtxz/login"
            login_body = f"check_token=&code={code}&token=&type=-1&union_id="
            login_res = self._api_call("POST", f"https://{self.HOST}{login_path}",
                                       headers=self._build_headers(login_path,
                                                                   "application/x-www-form-urlencoded;charset=utf-8"),
                                       data=login_body)

            if login_res.get("code") == 0:
                sess_data = (login_res.get("data") or {}).get("session", {})
                self.session_id = sess_data.get("id")
                self.account_id = sess_data.get("account_id")
                return True
            else:
                return False
        except Exception as e:
            print(f"[{self.masked_phone}] 登录过程异常: {str(e)}")
            return False

    def query_integral(self) -> Tuple[bool, int, str]:
        """查询积分"""
        try:
            my_path = "/api/user_mumber/numberCenter?is_new=1"
            my_res = self._api_call("GET", f"https://{self.HOST}{my_path}", headers=self._build_headers(my_path))

            if my_res.get("code") == 0:
                data = my_res.get("data", {}).get("rst", {})
                total_integral = data.get("total_integral", 0)
                return True, total_integral, "查询成功"
            else:
                return False, 0, my_res.get("message", "查询失败")
        except Exception as e:
            return False, 0, f"查询异常: {str(e)}"

    # ---------- 抽奖登录 ----------
    def _lottery_login(self) -> bool:
        """登录抽奖系统，获取lottery_token，成功返回True"""
        try:
            if not self.q:
                return False

            l_url = f"https://{self.ACT_HOST}/activity-api/lottery/api/auth/userLogin"
            l_req_id = str(uuid.uuid4())
            l_payload = {
                "q": self.q, "accountId": self.account_id,
                "sessionId": self.session_id, "tenantCode": "xsb_tiantai"
            }
            l_headers = {
                'Content-Type': "application/json", 'X-REQUEST-ID': l_req_id,
                'X-Requested-With': "com.zjonline.tiantai"
            }

            res = self._api_call("POST", l_url, headers=l_headers, data=l_payload, is_json=True)

            if res.get("code") == 0:
                login_data = res.get("data") or {}
                self.lottery_token = login_data.get("token", "")
                return bool(self.lottery_token)
            else:
                print(f"[{self.masked_phone}] 抽奖系统登录失败: {res.get('message')}")
                return False
        except Exception as e:
            print(f"[{self.masked_phone}] 抽奖登录异常: {str(e)}")
            return False

    # ---------- 钱包相关方法（移植自3.2版本） ----------
    def get_jump_u_param(self) -> str:
        """获取钱包跳转所需的u参数"""
        try:
            url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/accountPrizeRecord/jumpEquityWallet"
            headers = {
                'Authorization': self.lottery_token,
                'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai",
                'User-Agent': self.ua
            }
            res = self._api_call("GET", url, headers=headers)
            if res.get("code") == 0:
                data_url = res.get("data", "")
                if data_url:
                    parsed = urlparse(data_url)
                    query = parse_qs(parsed.query)
                    return query.get('u', [''])[0]
            return ""
        except Exception as e:
            print(f"[{self.masked_phone}] 获取跳转参数异常: {e}")
            return ""

    def get_equity_token(self) -> str:
        """使用u参数换取equity token"""
        if self.equity_token_cache:
            return self.equity_token_cache
        try:
            u_val = self.get_jump_u_param()
            if not u_val:
                print(f"[{self.masked_phone}] 未能获取到u参数，跳过钱包鉴权")
                return ""

            url = f"https://{self.MY_HOST}/equity-api/user/auth/userLogin"
            headers = {
                'Content-Type': "application/json",
                'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai",
                "User-Agent": self.ua,
            }
            payload = {
                "u": u_val,
                "accountId": self.account_id,
                "sessionId": self.session_id
            }
            res = self._api_call("POST", url, headers=headers, data=payload, is_json=True)
            if res.get("code") == 0:
                data = res.get("data") or {}
                token = data.get("token", "")
                if "yToken" in data:
                    self.y_token = data.get("yToken", "")
                if token:
                    self.equity_token_cache = token
                    return token
            print(f"[{self.masked_phone}] 获取钱包鉴权失败: {res.get('message')}")
            return ""
        except Exception as e:
            print(f"[{self.masked_phone}] 获取钱包鉴权异常: {e}")
            return ""

    def get_wallet_info(self) -> Dict[str, float]:
        """
        查询钱包余额，返回字典：
        {
            "total": 累计总额,
            "withdrawn": 已提现,
            "balance": 当前余额
        }
        失败返回空字典
        """
        try:
            token = self.get_equity_token()
            if not token:
                token = self.lottery_token
            if not token:
                return {}

            device_id = SecurityProvider.deterministic_uuid(self.phone)
            url = f"https://{self.MY_HOST}/equity-api/redBag/getWalletInfo?device={device_id}"
            headers = {
                "User-Agent": self.ua,
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "com.zjonline.tiantai",
                "X-REQUEST-ID": str(uuid.uuid4()),
                "Authorization": token
            }
            res = self._api_call("GET", url, headers=headers)

            if res.get("code") == 0:
                data_list = res.get("data", [])
                if data_list and isinstance(data_list, list):
                    info = data_list[0]
                    total = info.get("totalPrice", 0)
                    withdrawn = info.get("totalTransPrice", 0)
                    balance = info.get("aliPayTotalPrice", 0)
                    # 保存余额用于提现
                    self.alipay_balance = float(balance) if balance else 0.0
                    if info.get("yToken"):
                        self.y_token = info.get("yToken", "")
                    return {
                        "total": float(total),
                        "withdrawn": float(withdrawn),
                        "balance": float(balance)
                    }
            return {}
        except Exception as e:
            print(f"[{self.masked_phone}] 查询余额失败: {e}")
            return {}

    def do_withdraw(self) -> str:
        """执行提现"""
        if not self.withdraw_enabled:
            return "未开启自动提现"
        if self.alipay_balance < WITHDRAW_THRESHOLD:
            return f"余额 {self.alipay_balance} 未达门槛({WITHDRAW_THRESHOLD}元)"

        try:
            token = self.equity_token_cache
            if not token:
                token = self.get_equity_token()
            if not token:
                token = self.lottery_token
            if not token:
                return "鉴权失败无法提现"

            device_id = SecurityProvider.deterministic_uuid(self.phone)
            url = f"https://{self.MY_HOST}/equity-api/redBag/createTrans"

            req_id = f"{random.randint(1000, 9999)}{str(random.random())[1:]}|{int(time.time()*1000)}"

            headers = {
                "User-Agent": self.ua,
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "com.zjonline.tiantai",
                "X-REQUEST-ID": req_id,
                "Authorization": token
            }

            params = {
                "price": str(self.alipay_balance),
                "fundsChannelType": "0",
                "yToken": self.y_token,
                "deviceId": device_id
            }

            res = self._api_call("GET", url, headers=headers, params=params)

            if res.get("code") == 0:
                print(f"[{self.masked_phone}] 发起提现 {self.alipay_balance}元 成功!")
                return f"成功发起提现 {self.alipay_balance}元"
            else:
                msg = res.get('message', '未知原因')
                print(f"[{self.masked_phone}] 提现请求失败: {msg}")
                return f"提现失败: {msg}"
        except Exception as e:
            print(f"[{self.masked_phone}] 提现模块异常: {e}")
            return "提现请求异常"

    # ---------- 抽奖和提现整合 ----------
    def _run_lottery_enhanced(self) -> str:
        """
        执行抽奖（含多次抽奖、钱包查询、自动提现）
        返回格式化的结果字符串
        """
        try:
            if not self.q:
                print(f"[{self.masked_phone}] ⏩ 跳过抽奖 (未配置抽奖链接)")
                return "⏩ 未配置抽奖链接"

            time.sleep(random.uniform(2, 5))
            print(f"[{self.masked_phone}] ------ 开始检查抽奖 ------")

            # 抽奖系统登录
            l_url = f"https://{self.ACT_HOST}/activity-api/lottery/api/auth/userLogin"
            l_req_id = str(uuid.uuid4())
            l_payload = {
                "q": self.q, "accountId": self.account_id,
                "sessionId": self.session_id, "tenantCode": "xsb_tiantai"
            }
            l_headers = {
                'Content-Type': "application/json", 'X-REQUEST-ID': l_req_id,
                'X-Requested-With': "com.zjonline.tiantai"
            }

            res = self._api_call("POST", l_url, headers=l_headers, data=l_payload, is_json=True)

            third_id = 0
            if res.get("code") == 0:
                login_data = res.get("data") or {}
                self.lottery_token = login_data.get("token", "")
                third_id = login_data.get("thirdId", 0)
            else:
                return f"🔴 抽奖系统登录失败: {res.get('message', '未知错误')}"

            if not self.lottery_token:
                return "⚠️ Token获取为空，跳过抽奖"

            if not third_id:
                return "⚠️ 未找到有效活动ID(thirdId)，请检查抽奖链接"

            target_aid = third_id
            current_prize_version = self._get_prize_version(target_aid)
            print(f"[{self.masked_phone}] ℹ️ 当前活动ID: {target_aid}, PrizeVersion: {current_prize_version}")

            auth_headers = {
                'Authorization': self.lottery_token, 'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai", 'Sec-Fetch-Site': "same-origin", 'Sec-Fetch-Mode': "cors"
            }

            chk_url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/frontPageNum?activityId={target_aid}"
            chk_res = self._api_call("GET", chk_url, headers=auth_headers)
            remain = (chk_res.get("data") or {}).get("remainPrizeNum", 0)

            lottery_msgs = []
            if remain > 0:
                print(f"[{self.masked_phone}] 🎰 剩余抽奖次数: {remain}")
                for i in range(remain):
                    print(f"[{self.masked_phone}] ⏳ 正在进行第 {i+1}/{remain} 次抽奖...")
                    draw_url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/userActivityLottery"
                    draw_payload = {
                        "activityId": target_aid,
                        "clientId": self.ua.split(";")[1],
                        "prizeVersion": current_prize_version
                    }
                    draw_headers = {'Content-Type': "application/json", 'Authorization': self.lottery_token}

                    draw_res = self._api_call("POST", draw_url, headers=draw_headers, data=draw_payload, is_json=True)

                    if draw_res.get("code") == 0:
                        data_res = draw_res.get('data') or {}
                        is_prize = data_res.get('isPrize', 0)
                        prize_name = data_res.get('prizeName', '未知')
                        if str(is_prize) == "1" or is_prize is True or is_prize == 1:
                            line = f"🎁 第{i+1}次: 中奖 {prize_name}"
                        else:
                            line = f"💨 第{i+1}次: 未中奖"
                        lottery_msgs.append(line)
                    else:
                        lottery_msgs.append(f"⚠️ 第{i+1}次: 请求失败")
                    time.sleep(3)
            else:
                lottery_msgs.append("❌ 今日无剩余抽奖次数")

            # 查询钱包余额
            wallet_info = self.get_wallet_info()
            if wallet_info:
                wallet_line = f"💰 累计: {wallet_info['total']:.2f}元 | 提现: {wallet_info['withdrawn']:.2f}元 | 余额: {wallet_info['balance']:.2f}元"
                lottery_msgs.append(wallet_line)
            else:
                lottery_msgs.append("⚠️ 未查询到余额信息")

            # 自动提现
            withdraw_msg = ""
            if self.withdraw_enabled:
                if self.alipay_balance >= WITHDRAW_THRESHOLD:
                    withdraw_msg = self.do_withdraw()
                else:
                    withdraw_msg = f"余额未达提现门槛 ({self.alipay_balance}/{WITHDRAW_THRESHOLD}元)"
                lottery_msgs.append(f"💸 提现状态: {withdraw_msg}")
            else:
                lottery_msgs.append("💸 提现状态: 未开启自动提现")

            return "\n".join(lottery_msgs)

        except Exception as e:
            print(f"[{self.masked_phone}] ❌ 抽奖模块异常: {e}")
            return f"❌ 抽奖异常: {str(e)}"

    def _get_prize_version(self, activity_id: int) -> int:
        try:
            client_id = self.ua.split(";")[1]
            url = f"https://{self.ACT_HOST}/activity-api/lottery/h5/activity/lottery/frontPage?activityId={activity_id}&clientId={client_id}"
            headers = {
                'Authorization': self.lottery_token,
                'X-REQUEST-ID': str(uuid.uuid4()),
                'X-Requested-With': "com.zjonline.tiantai",
                'User-Agent': self.ua
            }
            res = self._api_call("GET", url, headers=headers)
            if res.get("code") == 0:
                data = res.get("data") or {}
                version = data.get("prizeVersion")
                if version is not None:
                    return int(version)
            return 2
        except Exception as e:
            print(f"[{self.masked_phone}] 获取prizeVersion失败，使用默认值2: {e}")
            return 2

    # ==================== 增强版每日任务 ====================
    def run_daily_tasks(self) -> Dict:
        """
        执行每日任务（签到、阅读、点赞、评论、分享、发帖、抽奖、提现）
        返回结果字典：
        {
            "sign": bool,
            "sign_score": int,
            "tasks_completed": int,
            "total_integral": int,
            "lottery_result": str   # 抽奖结果汇总（含钱包信息、提现状态）
        }
        """
        result = {
            "sign": False,
            "sign_score": 0,
            "tasks_completed": 0,
            "total_integral": 0,
            "lottery_result": ""
        }

        try:
            # ---------- 签到 ----------
            s_path = "/api/user_mumber/sign"
            s_res = self._api_call("GET", f"https://{self.HOST}{s_path}", headers=self._build_headers(s_path))
            if s_res.get("code") == 0:
                result["sign"] = True
                result["sign_score"] = (s_res.get("data") or {}).get("signIntegral", 0)
                print(f"[{self.masked_phone}] ✨ 签到成功: +{result['sign_score']} 分")
            else:
                print(f"[{self.masked_phone}] ⚠️ 签到反馈: {s_res.get('message')}")
            time.sleep(random.uniform(2, 4))

            # ---------- 通用任务上报（日常任务）----------
            t_path = "/api/user_mumber/doTask"
            self._api_call("POST", f"https://{self.HOST}{t_path}",
                           headers=self._build_headers(t_path, "application/x-www-form-urlencoded;charset=utf-8"),
                           data="memberType=6&member_type=6")
            time.sleep(random.uniform(2, 4))

            # ---------- 获取文章列表 ----------
            l_path = "/api/article/channel_list?channel_id=5bf216941b011b0880b6e49f&isDiFangHao=false&is_new=true&list_count=0&size=40"
            art_res = self._api_call("GET", f"https://{self.HOST}{l_path}", headers=self._build_headers(l_path))
            art_list = (art_res.get("data") or {}).get("article_list", []) or []
            art_ids = [i.get("id") for i in art_list]
            random.shuffle(art_ids)

            # ---------- 获取帖子列表 ----------
            bbs_path = "/api/bbs/api/post/list?categoryId=504"
            bbs_res = self._api_call("GET", f"https://{self.HOST}{bbs_path}", headers=self._build_headers(bbs_path))
            bbs_list = (bbs_res.get("data") or {}).get("records", []) or []
            bbs_ids = [i.get("id") for i in bbs_list]
            random.shuffle(bbs_ids)

            print(f"[{self.masked_phone}] 📋 获取到文章 {len(art_ids)} 篇, 帖子 {len(bbs_ids)} 个")

            completed_count = 0
            # 执行5个任务（文章和帖子交替）
            for i in range(5):
                if i < len(art_ids):
                    aid = art_ids[i]
                    # 阅读文章
                    r_path = f"/api/article/detail?id={aid}"
                    self._api_call("GET", f"https://{self.HOST}{r_path}", headers=self._build_headers(r_path))
                    time.sleep(random.uniform(8, 12))

                    # 点赞
                    lk_path = "/api/favorite/like"
                    self._api_call("POST", f"https://{self.HOST}{lk_path}",
                                   headers=self._build_headers(lk_path,
                                                               "application/x-www-form-urlencoded;charset=utf-8"),
                                   data=f"action=true&id={aid}")
                    time.sleep(random.uniform(2, 4))

                    # 评论
                    _, c_txt = self.fetch_comment_text()
                    c_path = "/api/comment/create/v2"
                    self._api_call("POST", f"https://{self.HOST}{c_path}",
                                   headers=self._build_headers(c_path, "application/json;charset=utf-8"),
                                   data={"channel_article_id": aid, "content": c_txt}, is_json=True)
                    time.sleep(random.uniform(3, 5))

                    # 上报任务（阅读/分享）
                    task_res = self._api_call("POST", f"https://{self.HOST}{t_path}",
                                              headers=self._build_headers(t_path,
                                                                          "application/x-www-form-urlencoded;charset=utf-8"),
                                              data=f"memberType=3&member_type=3&target_id={aid}")
                    if task_res.get("code") == 0:
                        completed_count += 1
                        print(f"[{self.masked_phone}] 📖 文章 {i+1}/5: 完成")
                    else:
                        print(f"[{self.masked_phone}] ⚠️ 文章 {i+1}/5: 上报失败 ({task_res.get('message')})")
                    time.sleep(random.uniform(2, 4))

                if i < len(bbs_ids):
                    bid = bbs_ids[i]
                    # 修复点：修改点赞帖子接口路径为 /h5/zan，并处理返回结果
                    zan_base_path = "/api/bbs/api/post/h5/zan"

                    zan_res_0 = self._api_call("GET", f"https://{self.HOST}{zan_base_path}?id={bid}&status=0",
                                               headers=self._build_headers(zan_base_path))
                    if zan_res_0.get("code") == 0:
                        print(f"[{self.masked_phone}] 🔄 帖子 {i+1}/5: 取消点赞成功")
                    else:
                        print(f"[{self.masked_phone}] ⚠️ 帖子 {i+1}/5: 取消点赞失败 ({zan_res_0.get('message')})")
                    time.sleep(0.5)

                    zan_res_1 = self._api_call("GET", f"https://{self.HOST}{zan_base_path}?id={bid}&status=1",
                                               headers=self._build_headers(zan_base_path))
                    if zan_res_1.get("code") == 0:
                        print(f"[{self.masked_phone}] 👍 帖子 {i+1}/5: 点赞成功")
                    else:
                        print(f"[{self.masked_phone}] ⚠️ 帖子 {i+1}/5: 点赞失败 ({zan_res_1.get('message')})")
                    time.sleep(random.uniform(2, 4))

                    # 分享
                    self._api_call("GET", f"https://{self.HOST}/api/bbs/api/post/share?id={bid}",
                                   headers=self._build_headers("/api/bbs/api/post/share"))
                    time.sleep(random.uniform(2, 4))

                    # 评论（论坛回复）
                    _, c_txt = self.fetch_comment_text()
                    rep_path = "/api/bbs/api/reply/edit"
                    self._api_call("POST", f"https://{self.HOST}{rep_path}",
                                   headers=self._build_headers(rep_path,
                                                               "application/x-www-form-urlencoded;charset=utf-8"),
                                   data=f"content={quote(c_txt)}&postId={bid}")
                    completed_count += 1
                    print(f"[{self.masked_phone}] 💬 帖子 {i+1}/5: 完成")
                    time.sleep(random.uniform(3, 6))

            # ---------- 发帖（灌水）---------- 可选，默认关闭（保留但注释）
            # for j in range(2):
            #     _, c_txt = self.fetch_comment_text()
            #     html_content = quote(f'<p style="margin:0px">{c_txt}</p>\n')
            #     pub_path = "/api/bbs/api/post/save"
            #     pub_res = self._api_call("POST", f"https://{self.HOST}{pub_path}",
            #                              headers=self._build_headers(pub_path,
            #                                                          "application/x-www-form-urlencoded;charset=utf-8"),
            #                              data=f"auditStatus=0&categoryId=505&content={html_content}&postType=4&subjectId=227466&topicTitleList=&videoTime=0")
            #     if pub_res.get("code") == 0:
            #         print(f"[{self.masked_phone}] 🖊️ 灌水发帖 {j+1}/2 成功")
            #     else:
            #         print(f"[{self.masked_phone}] ⚠️ 发帖失败: {pub_res.get('message')}")
            #     time.sleep(random.uniform(8, 15))

            result["tasks_completed"] = completed_count

            # 查询最终积分
            success, total_integral, msg = self.query_integral()
            if success:
                result["total_integral"] = total_integral

            # ---------- 执行抽奖模块（包含提现） ----------
            lottery_str = self._run_lottery_enhanced()
            result["lottery_result"] = lottery_str

        except Exception as e:
            print(f"[{self.masked_phone}] 任务执行异常: {str(e)}")
            result["lottery_result"] = f"❌ 任务异常: {str(e)}"

        return result

    # 保留原抽奖方法用于兼容
    def run_lottery(self) -> Tuple[bool, str]:
        result_str = self._run_lottery_enhanced()
        if "❌" in result_str or "⚠️" in result_str or "🔴" in result_str:
            return False, result_str
        return True, result_str

# ========================= 主要功能函数 =========================

def login(account_name, password):
    """验证和合天台账号"""
    try:
        if not account_name or not password:
            return "账号或密码不能为空", None

        client = SkyTClient(f"{account_name}#{password}")
        if client.execute_login():
            return f"{mask_phone(account_name)}", password
        else:
            return "登录失败: 账号或密码错误", None
    except Exception as e:
        return f"登录异常: {str(e)}", None

def bind(sender):
    """绑定和合天台账号 - 多行输入格式"""
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.hhtt.user', key=userid)

    sender.reply(
        """=====和合天台登录=====
📝 请输入登录参数:手机号#密码[#提现开关]
说明: 支持批量，一个账号一行
示例：
    13888888888#password123#true
    13999999999#password456#false
=====================
⭐ 输入q退出操作"""
    )

    # 获取多行输入
    input_text = sender.input(120000, 10, True).strip()
    if not input_text or input_text.lower() == 'q':
        sender.reply('已取消操作')
        return

    accounts = []
    success_count = 0
    fail_count = 0

    # 解析多行输入
    lines = input_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 解析手机号和密码和提现开关
        if '#' not in line:
            sender.reply(f"❌ 格式错误: {line} (缺少#分隔符)")
            fail_count += 1
            continue

        parts = line.split('#', 3)  # 最多分4部分
        if len(parts) < 2:
            sender.reply(f"❌ 格式错误: {line} (缺少密码)")
            fail_count += 1
            continue

        phone = parts[0].strip()
        password = parts[1].strip()
        lottery_link = parts[2].strip() if len(parts) > 2 else ""
        withdraw_switch = parts[3].strip() if len(parts) > 3 else ""

        if not re.match(r'^1[3-9]\d{9}$', phone):
            sender.reply(f"❌ 手机号格式错误: {phone}")
            fail_count += 1
            continue

        # 验证账号
        username, valid_password = login(phone, password)
        if not valid_password:
            sender.reply(f'{username}')
            fail_count += 1
            continue

        try:
            # 解析提现开关
            withdraw_enabled = True  # 默认开启
            if withdraw_switch.lower() in ['false', '0', '否', 'off']:
                withdraw_enabled = False
            elif withdraw_switch.lower() in ['true', '1', '是', 'on']:
                withdraw_enabled = True

            # 保存账号信息
            account_data = {
                'password': valid_password,
                'account_name': phone,
                'lottery_link': lottery_link,
                'withdraw_enabled': withdraw_enabled
            }
            middleware.bucketSet('JQB.hhtt.account', phone, json.dumps(account_data))

            # 添加到用户账号列表
            if phone not in accounts:
                accounts.append(phone)
                success_count += 1
        except Exception as e:
            sender.reply(f"❌ 保存失败: {phone} - {str(e)}")
            fail_count += 1

    # 更新用户账号列表
    if accounts:
        existing_accounts = eval(uservalue or '[]')
        for account in accounts:
            if account not in existing_accounts:
                existing_accounts.append(account)
        middleware.bucketSet('JQB.hhtt.user', userid, str(existing_accounts))

    # 返回结果
    result_msg = f"""=====绑定结果=====
✅ 成功绑定: {success_count}个账号
❌ 失败绑定: {fail_count}个账号
------------------
发送"和合天台查询"查看状态
发送"和合天台管理"管理账号
====================="""
    sender.reply(result_msg)

def query_balance(account_name):
    """
    查询和合天台账户积分和钱包余额
    返回: (积分, 总额, 提现, 余额, 提现开关, 中奖记录列表, 消息)
    如果失败，积分返回错误字符串，其余为0
    """
    try:
        account_data = middleware.bucketGet('JQB.hhtt.account', account_name)
        if not account_data:
            return "账号信息不存在", 0, 0, 0, False, [], "账号信息不存在"

        account_info = json.loads(account_data)
        password = account_info.get('password')
        lottery_link = account_info.get('lottery_link', '')
        withdraw_enabled = account_info.get('withdraw_enabled', True)  # 默认开启

        if not password:
            return "账号信息不完整", 0, 0, 0, False, [], "账号信息不完整"

        # 构建客户端
        client_data = f"{account_name}#{password}"
        if lottery_link:
            client_data += f"#{lottery_link}"

        client = SkyTClient(client_data)

        # 登录
        if not client.execute_login():
            return "登录失败", 0, 0, 0, withdraw_enabled, [], "登录失败"

        # 查询积分
        success, integral, msg = client.query_integral()
        if not success:
            return f"查询积分失败: {msg}", 0, 0, 0, withdraw_enabled, [], msg

        # 初始化余额数据
        total_price = 0.0
        withdrawn_price = 0.0
        balance_price = 0.0

        # 如果有抽奖链接，尝试获取钱包余额
        if lottery_link or middleware.bucketGet('JQB.hhtt', 'link'):
            if client._lottery_login():  # 先登录抽奖系统获取lottery_token
                wallet_info = client.get_wallet_info()
                if wallet_info:
                    total_price = wallet_info.get("total", 0.0)
                    withdrawn_price = wallet_info.get("withdrawn", 0.0)
                    balance_price = wallet_info.get("balance", 0.0)

        return integral, total_price, withdrawn_price, balance_price, withdraw_enabled, [], "成功"

    except Exception as e:
        return f"查询异常: {str(e)}", 0, 0, 0, False, [], str(e)

def query(sender):
    """查询账号信息（积分+钱包余额+提现状态）"""
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.hhtt.user', key=userid)
    today_date = datetime.now().date()
    today_time = str(today_date)

    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply(
            """\n=====和合天台账号查询=====
❌ 未找到任何账号
------------------
💡 发送"和合天台登录"绑定账号
==================="""
        )
        return

    if len(accounts) > 1:
        menu = """=====请选择查询账号=====
[0] 查询全部账号
"""
        for idx, acc in enumerate(accounts, 1):
            menu += f"[{idx}] {mask_phone(acc)}\n"
        menu += "=======================\n⚠️ 请回复数字序号(输入q退出)"
        sender.reply(menu)

        choice = sender.input(30000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply('已取消查询')
            return

        if choice == '0':
            target_accounts = accounts
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    target_accounts = [accounts[index]]
                else:
                    sender.reply('选择超出范围，已取消查询')
                    return
            except:
                sender.reply('格式错误，已取消查询')
                return
    else:
        target_accounts = accounts

    for account in target_accounts:
        try:
            # 查询授权状态
            account_auth = middleware.bucketGet('JQB.hhtt.auth', account)
            auth_status = f"⏰ 授权到期: {account_auth}" if account_auth and account_auth >= today_time else "❌ 未授权"

            # 查询积分和余额
            total_balance, total_price, withdrawn_price, balance_price, withdraw_enabled, win_records, msg = query_balance(account)
            if isinstance(total_balance, str):  # 如果返回的是错误消息
                sender.reply(f'【{mask_phone(account)}】{total_balance}')
                continue

            # 格式化输出
            withdraw_status = "✅ 已经开启自动提现" if withdraw_enabled else "✖️ 未开启自动提现"
            reply_msg = f"""=====账号详情=====
📱 账号: {mask_phone(account)}
{auth_status}
💮 当前积分: {total_balance}分💮
🎁 总额: {total_price:.2f}元 
🧧提米: {withdrawn_price:.2f}元
🧧当前余额: {balance_price:.2f}元
{withdraw_status}
==================="""
            sender.reply(reply_msg)

        except Exception as e:
            sender.reply(f'【{mask_phone(account)}】查询出错: {str(e)}')

def sign_in(sender):
    """和合天台签到和任务（增强版，包含提现）"""
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.hhtt.user', key=userid)
    today_date = datetime.now().date()
    today_time = str(today_date)

    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply('❌ 未绑定任何账号')
        return

    for account in accounts:
        try:
            # 检查授权状态
            auth = middleware.bucketGet('JQB.hhtt.auth', account)
            if not auth or auth < today_time:
                sender.reply(f'【{mask_phone(account)}】未授权，无法签到')
                continue

            # 获取账号信息
            account_data = middleware.bucketGet('JQB.hhtt.account', account)
            if not account_data:
                sender.reply(f'【{mask_phone(account)}】账号信息不存在')
                continue

            account_info = json.loads(account_data)
            password = account_info.get('password')
            lottery_link = account_info.get('lottery_link', '')
            withdraw_enabled = account_info.get('withdraw_enabled', True)

            if not password:
                sender.reply(f'【{mask_phone(account)}】账号信息不完整')
                continue

            # 构建客户端
            client_data = f"{account}#{password}"
            if lottery_link:
                client_data += f"#{lottery_link}"

            client = SkyTClient(client_data)
            client.withdraw_enabled = withdraw_enabled  # 设置提现开关

            # 登录
            if not client.execute_login():
                sender.reply(f"【{mask_phone(account)}】登录失败")
                continue

            sender.reply(f"【{mask_phone(account)}】开始执行每日任务...")

            # 执行增强版每日任务（包含抽奖和提现）
            task_result = client.run_daily_tasks()

            # 构建结果消息
            result_msg = f"""【{mask_phone(account)}】任务完成
✅ 签到: {'成功' if task_result['sign'] else '失败'} (+{task_result['sign_score']}分)
✅ 任务完成数: {task_result['tasks_completed']}/5
✅ 当前总积分: {task_result['total_integral']}"""

            if task_result['lottery_result']:
                result_msg += f"\n🎰 抽奖结果:\n{task_result['lottery_result']}"

            sender.reply(result_msg)

        except Exception as e:
            sender.reply(f'【{mask_phone(account)}】执行失败: {str(e)}')

def format_recent_wins(win_records):
    """格式化最近中奖记录（保留，但查询时不使用）"""
    if not win_records:
        return "🎁 最近3天抽奖记录: 暂无抽奖记录"

    result_lines = []
    for i, record in enumerate(win_records[:3], 1):
        date = record.get("date", "未知日期")
        amount = record.get("amount", 0)
        amount_str = f"{amount:.2f}" if isinstance(amount, float) else str(amount)
        result_lines.append(f"{date}: {amount_str}元")

    if result_lines:
        return "🎁 最近3天抽奖记录:\n" + "\n".join(result_lines)
    else:
        return "🎁 最近3天抽奖记录: 暂无抽奖记录"

# ========================= 新增中奖通知功能 =========================

def get_hhtt_account_summary(account):
    """
    获取和合天台账号摘要信息
    返回: (masked_phone, auth_time, withdrawn, balance, error)
    如果出错，error不为None，其他为None
    """
    try:
        # 获取授权到期时间
        auth_time = middleware.bucketGet('JQB.hhtt.auth', account)
        if not auth_time:
            auth_time = "未授权"

        # 查询钱包信息
        integral, total_price, withdrawn_price, balance_price, withdraw_enabled, win_records, msg = query_balance(account)
        if isinstance(integral, str):
            return None, None, None, None, f"查询失败: {integral}"

        masked = mask_phone(account)
        return masked, auth_time, withdrawn_price, balance_price, None
    except Exception as e:
        return None, None, None, None, str(e)

def send_hhtt_notification(user_id, masked_phone, auth_time, withdrawn, balance):
    """
    向指定用户发送和合天台中奖通知
    优先使用 middleware.Push，失败则尝试其他方式
    """
    msg = f"""=====和合天台中奖通知详情=====
📱 账号: {masked_phone}
⏰ 授权到期: {auth_time}
🧧提米: {withdrawn:.2f}元
🧧当前余额: {balance:.2f}元
💮 快快速去app手动领取吧！
==================="""

    # 判断是否在定时模式（无senderID）
    is_cron = (middleware.getSenderID() == "")

    # 尝试使用 middleware.Push
    push_func = None
    if hasattr(middleware, 'Push'):
        push_func = middleware.Push
    elif hasattr(middleware, 'push'):
        push_func = middleware.push

    if push_func:
        imTypes = ['qq', 'wb', 'tg', 'mp']  # 常用媒介
        last_exception = None
        for imType in imTypes:
            try:
                push_func(imType, '', user_id, '和合天台中奖通知', msg)
                print(f"向用户 {user_id} 使用 push imType={imType} 发送成功")
                return True, None
            except Exception as e:
                last_exception = e
                print(f"push imType={imType} 失败: {e}")
                continue
        # 所有push尝试失败，如果是定时模式，不再尝试Sender
        if is_cron:
            return False, f"所有 push 尝试失败，定时模式下不回退: {last_exception}"
        # 否则回退到Sender
    else:
        # 如果没有push函数，直接回退到Sender
        if is_cron:
            return False, "middleware.Push 不可用，且处于定时模式，无法推送"

    # 回退到多前缀 Sender（仅当非定时模式）
    prefixes = [
        "qqindiv",  # QQ个人
        "qq",       # QQ简称
        "qqprivate",# 备用
        "tgindiv",  # Telegram个人
        "tg",       # Telegram简称
        "wbindiv",  # 内置微信个人
        "wb",       # 内置微信简称
    ]
    last_error = None
    for prefix in prefixes:
        target = f"{prefix}:{user_id}"
        try:
            s = middleware.Sender(middleware.getSenderID())
            s.reply(msg)
            print(f"向用户 {user_id} 使用 Sender {target} 发送成功")
            return True, None
        except Exception as e:
            last_error = str(e)
            print(f"尝试 {target} 失败: {last_error}")
            continue
    return False, f"所有发送方式失败，最后错误: {last_error}"

def hhtt_scheduled_push(return_report=False):
    """
    定时任务：遍历所有用户，对每个账号推送提现和余额信息
    如果 return_report=True，则返回一个字典，包含每个用户的推送结果
    """
    print("========== 开始执行和合天台中奖推送任务 ==========")

    # 立即通知管理员开始执行
    if not return_report and middleware.getSenderID() == "":
        middleware.notifyMasters("【和合天台定时】开始执行中奖推送", [])

    users = middleware.bucketAllKeys('JQB.hhtt.user')
    if not users:
        msg = "【和合天台定时】未找到任何绑定用户"
        print(msg)
        if not return_report and middleware.getSenderID() == "":
            middleware.notifyMasters(msg, [])
        return {} if return_report else None

    print(f"找到 {len(users)} 个用户: {users}")
    report = {}

    for user in users:
        print(f"处理用户: {user}")
        accounts_str = middleware.bucketGet('JQB.hhtt.user', user)
        if not accounts_str:
            print(f"用户 {user} 无账号列表")
            continue
        try:
            accounts = eval(accounts_str)
        except Exception as e:
            print(f"解析用户 {user} 账号列表失败: {e}")
            continue

        print(f"用户 {user} 有 {len(accounts)} 个账号")
        user_report = []

        for account in accounts:
            print(f"  处理账号: {account}")
            try:
                masked, auth_time, withdrawn, balance, error = get_hhtt_account_summary(account)
                if error:
                    print(f"    账号 {account} 获取摘要失败: {error}")
                    user_report.append({
                        'account': account,
                        'masked': mask_phone(account),
                        'status': 'fail',
                        'reason': error
                    })
                    continue

                print(f"    账号 {account} 提现: {withdrawn}, 余额: {balance}")
                success, send_error = send_hhtt_notification(user, masked, auth_time, withdrawn, balance)
                if success:
                    user_report.append({
                        'account': account,
                        'masked': masked,
                        'status': 'success',
                        'withdrawn': withdrawn,
                        'balance': balance
                    })
                else:
                    user_report.append({
                        'account': account,
                        'masked': masked,
                        'status': 'fail',
                        'reason': send_error
                    })
                time.sleep(random.uniform(2, 4))  # 避免请求过快
            except Exception as e:
                print(f"    处理账号 {account} 异常: {e}")
                traceback.print_exc()
                user_report.append({
                    'account': account,
                    'masked': mask_phone(account),
                    'status': 'fail',
                    'reason': str(e)
                })
                continue

        if user_report:
            report[user] = user_report

    # 统计总数
    total_success = sum(1 for entries in report.values() for e in entries if e['status'] == 'success')
    total_fail = sum(1 for entries in report.values() for e in entries if e['status'] == 'fail')

    summary = f"【和合天台定时】推送完成：成功{total_success}，失败{total_fail}"
    print(summary)

    # 定时模式下，无论成功与否都通知管理员
    if not return_report and middleware.getSenderID() == "":
        if total_fail > 0:
            fail_details = []
            for user, entries in report.items():
                for e in entries:
                    if e['status'] == 'fail':
                        fail_details.append(f"{e['masked']}: {e['reason']}")
            if fail_details:
                summary += "\n失败详情：" + "\n".join(fail_details[:5])
        middleware.notifyMasters(summary, [])

    if return_report:
        return report
    return None

def prize_push_command(sender):
    """管理员手动触发和合天台中奖推送"""
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        return
    sender.reply("⏰ 开始执行和合天台中奖推送，请稍候...")
    report = hhtt_scheduled_push(return_report=True)
    if not report:
        sender.reply("❌ 没有可推送的用户或账号。")
        return

    # 构建详细报告
    total_success = 0
    total_fail = 0
    report_lines = ["📊 和合天台中奖推送执行结果："]
    for user, entries in report.items():
        user_success = sum(1 for e in entries if e['status'] == 'success')
        user_fail = sum(1 for e in entries if e['status'] == 'fail')
        total_success += user_success
        total_fail += user_fail
        report_lines.append(f"\n用户 {mask_phone(user)}：")
        for e in entries:
            if e['status'] == 'success':
                report_lines.append(f"  ✅ {e['masked']} 发送成功（提现 {e['withdrawn']:.2f}元，余额 {e['balance']:.2f}元）")
            elif e['status'] == 'fail':
                report_lines.append(f"  ❌ {e['masked']} 发送失败：{e['reason']}")
    report_lines.append(f"\n总计：成功 {total_success}，失败 {total_fail}")
    sender.reply("\n".join(report_lines))

# ========================= 新增：管理员一键运行所有账号 =========================

def admin_run_all_users_tasks(sender):
    """管理员一键运行所有用户的所有账号（执行每日任务）"""
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        return

    today_date = datetime.now().date()
    today_time = str(today_date)

    # 获取所有用户
    users = middleware.bucketAllKeys('JQB.hhtt.user')
    if not users:
        sender.reply("❌ 未找到任何绑定用户")
        return

    # 收集所有账号
    all_accounts = []
    account_owner = {}  # 记录每个账号所属用户，用于显示
    for user in users:
        accounts_str = middleware.bucketGet('JQB.hhtt.user', user)
        if not accounts_str:
            continue
        try:
            accounts = eval(accounts_str)
            for acc in accounts:
                all_accounts.append(acc)
                account_owner[acc] = user
        except:
            continue

    total_accounts = len(all_accounts)
    if total_accounts == 0:
        sender.reply("❌ 未找到任何有效账号")
        return

    sender.reply(f"🚀 管理员一键运行开始，共 {len(users)} 个用户，{total_accounts} 个账号...")

    success_count = 0
    fail_count = 0
    unauthorized_count = 0
    details = []  # 存储每个账号的执行结果摘要

    for idx, account in enumerate(all_accounts, 1):
        try:
            # 检查授权
            auth = middleware.bucketGet('JQB.hhtt.auth', account)
            if not auth or auth < today_time:
                details.append(f"❌ 【{mask_phone(account)}】未授权，跳过")
                unauthorized_count += 1
                continue

            # 获取账号信息
            account_data = middleware.bucketGet('JQB.hhtt.account', account)
            if not account_data:
                details.append(f"❌ 【{mask_phone(account)}】账号信息不存在，跳过")
                fail_count += 1
                continue

            account_info = json.loads(account_data)
            password = account_info.get('password')
            lottery_link = account_info.get('lottery_link', '')
            withdraw_enabled = account_info.get('withdraw_enabled', True)

            if not password:
                details.append(f"❌ 【{mask_phone(account)}】账号信息不完整，跳过")
                fail_count += 1
                continue

            # 发送进度
            progress_msg = f"📊 进度 {idx}/{total_accounts} | 账号: {mask_phone(account)}"
            sender.reply(progress_msg)

            # 构建客户端并执行任务
            client_data = f"{account}#{password}"
            if lottery_link:
                client_data += f"#{lottery_link}"
            client = SkyTClient(client_data)
            client.withdraw_enabled = withdraw_enabled

            if not client.execute_login():
                details.append(f"❌ 【{mask_phone(account)}】登录失败")
                fail_count += 1
                continue

            task_result = client.run_daily_tasks()

            # 格式化结果
            result_line = f"【{mask_phone(account)}】任务完成 | 签到:{'✅' if task_result['sign'] else '❌'}(+{task_result['sign_score']}) | 任务:{task_result['tasks_completed']}/5 | 积分:{task_result['total_integral']}"
            if task_result['lottery_result']:
                # 只取第一行作为摘要，避免刷屏
                lottery_summary = task_result['lottery_result'].split('\n')[0]
                result_line += f" | 抽奖:{lottery_summary}"
            details.append(f"✅ {result_line}")
            success_count += 1

            # 适当延时，避免请求过快
            time.sleep(random.uniform(2, 4))

        except Exception as e:
            details.append(f"❌ 【{mask_phone(account)}】执行异常: {str(e)}")
            fail_count += 1

    # 汇总报告
    summary = f"""=====管理员一键运行完成=====
📊 用户总数: {len(users)}个
📊 账号总数: {total_accounts}个
✅ 成功执行: {success_count}个
❌ 执行失败: {fail_count}个
🔒 未授权跳过: {unauthorized_count}个
⏰ 完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
===================="""

    # 发送详细结果（如果太多，只发送部分）
    if len(details) > 20:
        detail_msg = "\n".join(details[:20]) + f"\n……共 {len(details)} 条详情，仅显示前20条"
    else:
        detail_msg = "\n".join(details)

    sender.reply(summary)
    if detail_msg:
        sender.reply(detail_msg)

# ========================= 以下函数保持原样，只需修改bucket名称 =========================

def add_to_qinglong(ql_host, ql_token, env_data):
    """添加变量到青龙并返回环境变量ID"""
    try:
        url = f"{ql_host}open/envs"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }

        # 检查是否已存在
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return None

        envs = response.json().get('data', [])
        exists_id = None
        for env in envs:
            if env.get('name') == env_data['name'] and env_data['remarks'] in env.get('remarks', ''):
                exists_id = env.get('id')
                break

        if exists_id:
            # 更新现有变量
            env_data['id'] = exists_id
            response = requests.put(url, headers=headers, json=env_data)
            if response.status_code == 200:
                return exists_id
        else:
            # 新增变量
            response = requests.post(url, headers=headers, json=[env_data])
            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get('data') and len(resp_data['data']) > 0:
                    return resp_data['data'][0]['id']

        return None

    except Exception as e:
        print(f"青龙操作失败: {str(e)}")
        return None

def delete_qinglong_env(ql_host, ql_token, env_id):
    """删除青龙环境变量"""
    try:
        if not env_id:
            return False

        url = f"{ql_host}open/envs"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        data = [int(env_id)]

        response = requests.delete(url, headers=headers, json=data)
        return response.status_code == 200

    except Exception as e:
        print(f"删除青龙变量失败: {str(e)}")
        return False

def get_ql_token(ql_host, client_id, client_secret):
    """获取青龙token"""
    try:
        url = f"{ql_host}open/auth/token?client_id={client_id}&client_secret={client_secret}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json().get('data', {}).get('token')
    except Exception as e:
        print(f"获取青龙token失败: {str(e)}")
    return None

def manage_accounts(sender):
    """管理账号"""
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.hhtt.user', key=userid)

    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply("""=====账号管理=====
❌ 未找到任何账号
------------------
💡 发送"和合天台登录"绑定账号
===================""")
        return

    menu = """=====账号管理=====
[1] 授权所有账号
[2] 删除账号
[3] 选择账号授权
[4] 是否开启余额自动提现
------------------
请回复数字选择操作"""
    sender.reply(menu)

    choice = sender.input(30000, 1, False)
    if not choice:
        return sender.reply('操作超时')

    if choice == '1':
        # 授权所有账号
        authorize_accounts(sender, accounts)
    elif choice == '2':
        delete_account(sender)
    elif choice == '3':
        select_accounts_authorize(sender, accounts)
    elif choice == '4':
        toggle_withdraw_switch(sender, accounts)
    else:
        sender.reply('无效的选择')

def toggle_withdraw_switch(sender, accounts):
    """切换账号的自动提现开关"""
    if not accounts:
        return sender.reply('❌ 无账号可操作')

    # 显示账号列表
    menu = "=====选择要设置提现开关的账号=====\n"
    for idx, acc in enumerate(accounts, 1):
        # 获取当前状态
        account_data = middleware.bucketGet('JQB.hhtt.account', acc)
        if account_data:
            info = json.loads(account_data)
            status = info.get('withdraw_enabled', True)
            status_str = "✅开启" if status else "❌关闭"
        else:
            status_str = "❓未知"
        menu += f"[{idx}] {mask_phone(acc)} 当前状态: {status_str}\n"
    menu += "=======================\n⚠️ 回复数字序号(多个用逗号分隔, 输入q退出)"
    sender.reply(menu)

    choice_str = sender.input(30000, 1, False)
    if not choice_str or choice_str.lower() == 'q':
        return sender.reply('已取消操作')

    try:
        # 解析用户选择的账号
        selected_indexes = [int(idx.strip()) for idx in choice_str.split(',')]
        selected_accounts = []

        for idx in selected_indexes:
            if 1 <= idx <= len(accounts):
                selected_accounts.append(accounts[idx-1])
            else:
                sender.reply(f"❌ 无效的序号: {idx}，已跳过")

        if not selected_accounts:
            return sender.reply('❌ 未选择有效账号')

        # 询问开启还是关闭
        sender.reply("请选择操作:\n[1] 开启自动提现\n[2] 关闭自动提现")
        op_choice = sender.input(30000, 1, False)
        if not op_choice or op_choice not in ['1', '2']:
            return sender.reply('已取消')

        enable = (op_choice == '1')

        # 更新每个账号
        updated = 0
        for account in selected_accounts:
            account_data = middleware.bucketGet('JQB.hhtt.account', account)
            if account_data:
                info = json.loads(account_data)
                info['withdraw_enabled'] = enable
                middleware.bucketSet('JQB.hhtt.account', account, json.dumps(info))
                updated += 1
            else:
                sender.reply(f"⚠️ 账号 {mask_phone(account)} 信息不存在，跳过")

        sender.reply(f"✅ 已为 {updated} 个账号设置提现开关为 {'开启' if enable else '关闭'}")

    except Exception as e:
        sender.reply(f'❌ 操作失败: {str(e)}')

def delete_account(sender):
    """删除账号（包括青龙环境变量）"""
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.hhtt.user', key=userid)

    accounts = eval(uservalue or '[]')
    if not accounts:
        return sender.reply('❌ 无账号可删除')

    if len(accounts) > 1:
        menu = "=====选择要删除的账号=====\n"
        for idx, acc in enumerate(accounts, 1):
            menu += f"[{idx}] {mask_phone(acc)}\n"
        menu += "=======================\n⚠️ 回复数字序号(输入q退出)"
        sender.reply(menu)

        choice = sender.input(30000, 1, False)
        if not choice or choice.lower() == 'q':
            return sender.reply('已取消')

        try:
            index = int(choice) - 1
            if 0 <= index < len(accounts):
                account = accounts[index]

                # 显示确认信息
                confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
📱 账号: {mask_phone(account)}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                sender.reply(confirm_msg)

                # 获取确认
                confirm = sender.input(30000, 1, False)
                if confirm.lower() != 'y':
                    return sender.reply('✅ 已取消删除操作')

                # 获取青龙配置
                ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')

                # 删除青龙环境变量
                if ql_host and ql_client_id and ql_client_secret:
                    if not ql_host.endswith('/'):
                        ql_host += '/'
                    ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)
                    if ql_token:
                        env_id = middleware.bucketGet('JQB.hhtt.env_id', account)
                        if env_id:
                            delete_qinglong_env(ql_host, ql_token, env_id)

                # 删除本地存储
                middleware.bucketDel('JQB.hhtt.account', account)
                middleware.bucketDel('JQB.hhtt.auth', account)
                middleware.bucketDel('JQB.hhtt.env_id', account)

                accounts.pop(index)
                middleware.bucketSet('JQB.hhtt.user', userid, str(accounts))
                sender.reply(f'✅ 已删除账号: {mask_phone(account)}')
            else:
                sender.reply('选择超出范围')
        except:
            sender.reply('输入错误')
    else:
        account = accounts[0]

        # 显示确认信息
        confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
📱 账号: {mask_phone(account)}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
        sender.reply(confirm_msg)

        # 获取确认
        confirm = sender.input(30000, 1, False)
        if confirm.lower() != 'y':
            return sender.reply('✅ 已取消删除操作')

        # 获取青龙配置
        ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
        ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
        ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')

        # 删除青龙环境变量
        if ql_host and ql_client_id and ql_client_secret:
            if not ql_host.endswith('/'):
                ql_host += '/'
            ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)
            if ql_token:
                env_id = middleware.bucketGet('JQB.hhtt.env_id', account)
                if env_id:
                    delete_qinglong_env(ql_host, ql_token, env_id)

        # 删除本地存储
        middleware.bucketDel('JQB.hhtt.account', account)
        middleware.bucketDel('JQB.hhtt.auth', account)
        middleware.bucketDel('JQB.hhtt.env_id', account)
        middleware.bucketSet('JQB.hhtt.user', userid, '[]')
        sender.reply(f'✅ 已删除账号: {mask_phone(account)}')

def authorize_accounts(sender, accounts):
    """授权所有账号"""
    if not accounts:
        return sender.reply('❌ 无账号可授权')

    # 显示所有账号
    account_list = "\n".join([f"  - {mask_phone(acc)}" for acc in accounts])
    sender.reply(f"""=====即将授权以下账号=====
{account_list}
------------------""")

    coin_bucket = middleware.bucketGet('JQB.hhtt', 'coin_bucket') or 'dd_sign_points'
    coin_price = int(middleware.bucketGet('JQB.hhtt', 'coin') or '0')
    price = Decimal(middleware.bucketGet('JQB.hhtt', 'price') or '1')

    menu = f"""=====授权方式选择=====
[1] 微信支付 ({price}元/账号/月)
[2] 积分支付 ({coin_price}积分/账号/月)
------------------
请回复数字选择方式"""
    sender.reply(menu)

    choice = sender.input(30000, 1, False)
    if not choice or choice not in ['1', '2']:
        return sender.reply('已取消')

    sender.reply("请输入授权月数:")
    months = sender.input(30000, 1, False)
    if not months:
        return sender.reply('输入超时')

    try:
        months = int(months)
        if months <= 0:
            return sender.reply('月数必须大于0')

        # 在支付成功后处理青龙配置
        ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
        ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
        ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
        var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
        ql_token = None

        if ql_host and ql_client_id and ql_client_secret:
            if not ql_host.endswith('/'):
                ql_host += '/'
            ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

        if choice == '1':
            amount = price * months * len(accounts)
            if process_payment(amount, months * 30, sender):
                for account in accounts:
                    auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                    middleware.bucketSet('JQB.hhtt.auth', account, auth_time)

                    # 只有在授权后才提交到青龙
                    if ql_token:
                        account_data = middleware.bucketGet('JQB.hhtt.account', account)
                        if account_data:
                            account_info = json.loads(account_data)
                            password = account_info.get('password')

                            if password:
                                remarks = f"和合天台账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                                env_data = {
                                    "name": var_name,
                                    "value": f"{account}#{password}",
                                    "remarks": remarks
                                }
                                env_id = add_to_qinglong(ql_host, ql_token, env_data)
                                if env_id:
                                    middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))

                sender.reply(f'✅ 已授权 {len(accounts)} 个账号 {months} 个月')
        elif choice == '2':
            user_coin = Decimal(middleware.bucketGet(coin_bucket, sender.getUserID()) or '0')
            need_coin = coin_price * months * len(accounts)
            if user_coin < need_coin:
                return sender.reply(f'❌ 积分不足，需要{need_coin}，当前有{user_coin}')

            new_coin = user_coin - need_coin
            middleware.bucketSet(coin_bucket, sender.getUserID(), str(new_coin))
            for account in accounts:
                auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                middleware.bucketSet('JQB.hhtt.auth', account, auth_time)

                if ql_token:
                    account_data = middleware.bucketGet('JQB.hhtt.account', account)
                    if account_data:
                        account_info = json.loads(account_data)
                        password = account_info.get('password')

                        if password:
                            remarks = f"和合天台账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                            env_data = {
                                "name": var_name,
                                "value": f"{account}#{password}",
                                "remarks": remarks
                            }
                            env_id = add_to_qinglong(ql_host, ql_token, env_data)
                            if env_id:
                                middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))

            sender.reply(
                f"""✅ 已用 {need_coin} 积分授权 {len(accounts)} 个账号 {months} 个月
剩余积分: {new_coin}"""
            )

    except Exception as e:
        sender.reply(f'❌ 授权失败: {str(e)}')

def select_accounts_authorize(sender, accounts):
    """选择特定账号进行授权"""
    if not accounts:
        return sender.reply('❌ 无账号可授权')

    # 显示账号列表
    menu = "=====选择要授权的账号=====\n"
    for idx, acc in enumerate(accounts, 1):
        menu += f"[{idx}] {mask_phone(acc)}\n"
    menu += "=======================\n⚠️ 回复数字序号(多个用逗号分隔, 输入q退出)"
    sender.reply(menu)

    choice_str = sender.input(30000, 1, False)
    if not choice_str or choice_str.lower() == 'q':
        return sender.reply('已取消授权操作')

    try:
        # 解析用户选择的账号
        selected_indexes = [int(idx.strip()) for idx in choice_str.split(',')]
        selected_accounts = []

        for idx in selected_indexes:
            if 1 <= idx <= len(accounts):
                selected_accounts.append(accounts[idx-1])
            else:
                sender.reply(f"❌ 无效的序号: {idx}，已跳过")

        if not selected_accounts:
            return sender.reply('❌ 未选择有效账号')

        # 显示选择的账号
        account_list = "\n".join([f"  - {mask_phone(acc)}" for acc in selected_accounts])
        sender.reply(f"""=====已选择以下账号=====
{account_list}
------------------""")

        # 进行授权操作
        authorize_selected_accounts(sender, selected_accounts)

    except Exception as e:
        sender.reply(f'❌ 选择失败: {str(e)}')

def authorize_selected_accounts(sender, selected_accounts):
    """授权选定的账号"""
    coin_bucket = middleware.bucketGet('JQB.hhtt', 'coin_bucket') or 'dd_sign_points'
    coin_price = int(middleware.bucketGet('JQB.hhtt', 'coin') or '0')
    price = Decimal(middleware.bucketGet('JQB.hhtt', 'price') or '1')

    menu = f"""=====授权方式选择=====
[1] 微信支付 ({price}元/账号/月)
[2] 积分支付 ({coin_price}积分/账号/月)
------------------
请回复数字选择方式"""
    sender.reply(menu)

    choice = sender.input(30000, 1, False)
    if not choice or choice not in ['1', '2']:
        return sender.reply('已取消')

    sender.reply("请输入授权月数:")
    months = sender.input(30000, 1, False)
    if not months:
        return sender.reply('输入超时')

    try:
        months = int(months)
        if months <= 0:
            return sender.reply('月数必须大于0')

        # 在支付成功后处理青龙配置
        ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
        ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
        ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
        var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
        ql_token = None

        if ql_host and ql_client_id and ql_client_secret:
            if not ql_host.endswith('/'):
                ql_host += '/'
            ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

        if choice == '1':
            amount = price * months * len(selected_accounts)
            if process_payment(amount, months * 30, sender):
                for account in selected_accounts:
                    auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                    middleware.bucketSet('JQB.hhtt.auth', account, auth_time)

                    if ql_token:
                        account_data = middleware.bucketGet('JQB.hhtt.account', account)
                        if account_data:
                            account_info = json.loads(account_data)
                            password = account_info.get('password')

                            if password:
                                remarks = f"和合天台账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                                env_data = {
                                    "name": var_name,
                                    "value": f"{account}#{password}",
                                    "remarks": remarks
                                }
                                env_id = add_to_qinglong(ql_host, ql_token, env_data)
                                if env_id:
                                    middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))

                sender.reply(f'✅ 已授权 {len(selected_accounts)} 个账号 {months} 个月')
        elif choice == '2':
            user_coin = Decimal(middleware.bucketGet(coin_bucket, sender.getUserID()) or '0')
            need_coin = coin_price * months * len(selected_accounts)
            if user_coin < need_coin:
                return sender.reply(f'❌ 积分不足，需要{need_coin}，当前有{user_coin}')

            new_coin = user_coin - need_coin
            middleware.bucketSet(coin_bucket, sender.getUserID(), str(new_coin))
            for account in selected_accounts:
                auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                middleware.bucketSet('JQB.hhtt.auth', account, auth_time)

                if ql_token:
                    account_data = middleware.bucketGet('JQB.hhtt.account', account)
                    if account_data:
                        account_info = json.loads(account_data)
                        password = account_info.get('password')

                        if password:
                            remarks = f"和合天台账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                            env_data = {
                                "name": var_name,
                                "value": f"{account}#{password}",
                                "remarks": remarks
                            }
                            env_id = add_to_qinglong(ql_host, ql_token, env_data)
                            if env_id:
                                middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))

            sender.reply(
                f"""✅ 已用 {need_coin} 积分授权 {len(selected_accounts)} 个账号 {months} 个月
剩余积分: {new_coin}"""
            )

    except Exception as e:
        sender.reply(f'❌ 授权失败: {str(e)}')

def process_payment(amount, days, sender):
    """处理支付"""
    zsm = middleware.bucketGet('JQB.hhtt', 'zsm')
    if not zsm:
        sender.reply("❌ 未配置收款码")
        return False

    if sender.atWaitPay():
        sender.reply('当前有人正在支付,请稍后再试！')
        return False

    pay_msg = f"""=====微信扫码支付====
🎫 商品: 和合天台授权
🕛 时长: {days}天
💮 金额: {amount}灵石💮
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)
    sender.replyImage(zsm)
    result = sender.waitPay("q",100000)

    if not result:
        sender.reply("❌ 支付超时")
        return False
    elif result == 'q':
        sender.reply("✅ 已取消支付")
        return False

    try:
        if isinstance(result, str):
            result = json.loads(result)

        paid_amount = Decimal(str(result.get('money') or result.get('Money') or 0))
        if paid_amount >= amount:
            return True
        else:
            sender.reply(f"❌ 支付金额不足，应付: {amount}元，实付: {paid_amount}元")
            return False
    except Exception as e:
        sender.reply(f"❌ 支付验证失败: {str(e)}")
        return False

def tutorial(sender):
    """显示使用教程"""
    sender.reply("""=====和合天台教程=====
🌟 核心功能指令:
1. 和合天台登录 - 绑定账号(手机号#密码[#提现开关])
2. 和合天台查询 - 查看当前积分、钱包总额、提现和余额及提现状态
3. 和合天台签到 - 执行每日任务和抽奖(含自动提现)
4. 和合天台管理 - 账号管理功能(含提现开关设置)
5. 和合天台中奖通知 - 管理员手动推送账户状态通知
6. 和合天台一键运行 - 管理员执行全服所有账号任务

⚙️ 授权说明:
1. 支持微信支付和积分支付
2. 授权后解锁全部功能
3. 自动同步到青龙面板

📋 每日任务包括:
1. 签到
2. 阅读文章(5篇)
3. 点赞评论(5次)
4. 点赞分享(5次)
5. 发帖(2篇) - 默认关闭防封号
6. 抽奖(如有抽奖链接)
7. 自动提现(可开关，门槛默认2元)

📊 查询功能:
1. 显示当前积分
2. 显示授权到期时间
3. 显示钱包总额、提现金额和当前余额（需配置抽奖链接）
4. 显示自动提现开关状态

⚠️ 注意事项:
1. 使用手机号+密码登录
2. 抽奖链接每月更新，可在APP中获取
3. 每日任务约可获得0.15元
4. 提现门槛可在插件配置中修改(withdraw_threshold)
=====================""")

def hhtt_auth(sender):
    """和合天台授权功能（管理员专用）"""
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        return

    # 定义今天日期和时间
    today_date = datetime.now().date()
    today_time = str(today_date)

    sender.reply(
        "=====和合天台授权管理=====\n"
        "  [1] 📱 一键授权所有用户\n" 
        "  [2] 👤 单独授权用户\n"
        "  [3] ⏰ 修改授权时间\n"
        "  [4] 🗑️ 删除用户账号\n"
        "-------------------\n"
        "⚠️ 输入q退出操作\n"
        "=================="
    )
    choice = sender.input(60000, 1, False)

    if choice == 'q' or choice == 'Q':
        sender.reply("✅ 已取消操作")
        return
    elif choice == '':
        sender.reply('⏰ 输入超时!')
        return
    elif choice == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('JQB.hhtt.user')
        if not users:
            sender.reply("❌ 未找到任何绑定的和合天台账号")
            return

        sender.reply('📝 请输入要给所有用户授权的月数！\n⚠️ 输入"q"退出操作')
        months = sender.input(60000, 1, False)
        if months == 'q' or months == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif months == '':
            sender.reply('⏰ 输入超时!')
            return

        try:
            months = int(months)
            success_count = 0
            # 获取青龙配置
            ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
            ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
            ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
            var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
            ql_token = None

            if ql_host and ql_client_id and ql_client_secret:
                if not ql_host.endswith('/'):
                    ql_host += '/'
                ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

            for user in users:
                accountlist = middleware.bucketGet('JQB.hhtt.user', user)
                if not accountlist or accountlist == '[]':
                    continue

                accounts = eval(accountlist)
                for account in accounts:
                    try:
                        account_data = middleware.bucketGet('JQB.hhtt.account', account)
                        if not account_data:
                            continue

                        # 更新授权时间
                        auth = middleware.bucketGet('JQB.hhtt.auth', account)
                        if not auth or auth < today_time:
                            auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                        else:
                            auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')

                        middleware.bucketSet('JQB.hhtt.auth', account, auth_time)

                        # 更新青龙变量（只保存手机号和密码）
                        if ql_token:
                            account_info = json.loads(account_data)
                            password = account_info.get('password')

                            if password:
                                remarks = f"和合天台账号{mask_phone(account)}丨用户:{user}丨授权时间:{auth_time}"
                                env_data = {
                                    "name": var_name,
                                    "value": f"{account}#{password}",
                                    "remarks": remarks
                                }
                                env_id = add_to_qinglong(ql_host, ql_token, env_data)
                                if env_id:
                                    middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))
                        success_count += 1
                    except:
                        continue

            msg = f"""
=====一键授权完成=====
✅ 成功授权: {success_count}个账号
⏰ 授权月数: {months}月
=================="""
            sender.reply(msg)

        except ValueError:
            sender.reply('❌ 输入的月数无效!')
            return

    elif choice == '2':
        # 单独授权用户
        sender.reply('📝 请输入需要授权的用户ID\n💡 通过给机器人发送"myuid"获得\n⚠️ 输入"q"退出操作')
        user_id = sender.input(60000, 1, False)
        if user_id == 'q' or user_id == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif user_id == '':
            sender.reply('⏰ 输入超时!')
            return

        accountlist = middleware.bucketGet('JQB.hhtt.user', user_id)
        if not accountlist or accountlist == '[]':
            sender.reply(f"❌ 未找到用户 {user_id} 的和合天台账号信息!")
            return

        accounts = eval(accountlist)
        n = 0
        msg = '=====用户账号列表=====\n'
        msg += '0、授权所有账号\n==================\n'

        for account in accounts:
            n += 1
            auth = middleware.bucketGet('JQB.hhtt.auth', account)
            if not auth:
                auth_status = '未授权'
            elif auth < today_time:
                auth_status = '授权过期'
            else:
                auth_status = f'到期: {auth}'
            msg += f'{n}、账号:{mask_phone(account)}\n授权状态: {auth_status}\n==================\n'

        msg += f'📝 回复序号选择账号\n⚠️ 输入"q"退出操作'
        sender.reply(msg)
        choice = sender.input(60000, 1, False)

        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif choice == '':
            sender.reply('⏰ 输入超时!')
            return

        if choice == '0':
            # 授权该用户的所有账号
            sender.reply('📝 请输入授权月数\n⚠️ 输入"q"退出操作')
            months = sender.input(60000, 1, False)

            if months == 'q' or months == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif months == '':
                sender.reply('⏰ 输入超时!')
                return

            try:
                months = int(months)
                success_count = 0
                # 获取青龙配置
                ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
                var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
                ql_token = None

                if ql_host and ql_client_id and ql_client_secret:
                    if not ql_host.endswith('/'):
                        ql_host += '/'
                    ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

                for account in accounts:
                    try:
                        account_data = middleware.bucketGet('JQB.hhtt.account', account)
                        if not account_data:
                            continue

                        # 更新授权时间
                        auth = middleware.bucketGet('JQB.hhtt.auth', account)
                        if not auth or auth < today_time:
                            auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                        else:
                            auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')

                        middleware.bucketSet('JQB.hhtt.auth', account, auth_time)

                        # 更新青龙变量（只保存手机号和密码）
                        if ql_token:
                            account_info = json.loads(account_data)
                            password = account_info.get('password')

                            if password:
                                remarks = f"和合天台账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{auth_time}"
                                env_data = {
                                    "name": var_name,
                                    "value": f"{account}#{password}",
                                    "remarks": remarks
                                }
                                env_id = add_to_qinglong(ql_host, ql_token, env_data)
                                if env_id:
                                    middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))
                        success_count += 1
                    except:
                        continue

                msg = f"""
=====批量授权完成=====
✅ 成功授权: {success_count}个账号
⏰ 授权月数: {months}月
=================="""
                sender.reply(msg)

            except ValueError:
                sender.reply('❌ 输入的月数无效!')
                return

        elif 1 <= int(choice) <= len(accounts):
            # 授权单个账号
            account = accounts[int(choice)-1]
            sender.reply('📝 请输入授权月数\n⚠️ 输入"q"退出操作')
            months = sender.input(60000, 1, False)

            if months == 'q' or months == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif months == '':
                sender.reply('⏰ 输入超时!')
                return

            try:
                months = int(months)
                account_data = middleware.bucketGet('JQB.hhtt.account', account)

                if not account_data:
                    sender.reply("❌ 未找到账号信息!")
                    return

                # 更新授权时间
                auth = middleware.bucketGet('JQB.hhtt.auth', account)
                if not auth or auth < today_time:
                    auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                else:
                    auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')

                middleware.bucketSet('JQB.hhtt.auth', account, auth_time)

                # 更新青龙变量（只保存手机号和密码）
                ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
                var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
                ql_token = None

                if ql_host and ql_client_id and ql_client_secret:
                    if not ql_host.endswith('/'):
                        ql_host += '/'
                    ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)
                    if ql_token:
                        account_info = json.loads(account_data)
                        password = account_info.get('password')

                        if password:
                            remarks = f"和合天台账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{auth_time}"
                            env_data = {
                                "name": var_name,
                                "value": f"{account}#{password}",
                                "remarks": remarks
                            }
                            env_id = add_to_qinglong(ql_host, ql_token, env_data)
                            if env_id:
                                middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))

                msg = f"""
=====授权成功=====
✅ 账号: {mask_phone(account)}
⏰ 授权月数: {months}月
🕛 到期时间: {auth_time}
=================="""
                sender.reply(msg)

            except ValueError:
                sender.reply('❌ 输入的月数无效!')
                return
        else:
            sender.reply('❌ 输入的序号无效!')
            return
    elif choice == '3':
        # 修改授权时间
        sender.reply(
            "=====修改授权时间=====\n"
            "  [1] 📱 修改所有用户\n"
            "  [2] 👤 修改单独用户\n"
            "-------------------\n"
            "⚠️ 输入q退出操作\n"
            "==================="
        )
        sub_choice = sender.input(60000, 1, False)

        if sub_choice == 'q' or sub_choice == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif sub_choice == '':
            sender.reply('⏰ 输入超时!')
            return
        elif sub_choice == '1':
            users = middleware.bucketAllKeys('JQB.hhtt.user')
            if not users:
                sender.reply("❌ 未找到任何绑定的和合天台账号")
                return

            sender.reply('📝 请输入要调整的天数:\n➕ 正数增加天数\n➖ 负数减少天数\n💡 例如: 100 或 -100\n⚠️ 输入"q"退出操作')
            days = sender.input(60000, 1, False)
            if days == 'q' or days == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif days == '':
                sender.reply('⏰ 输入超时!')
                return

            try:
                days = int(days)
                total_success = 0

                # 获取青龙配置
                ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
                var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
                ql_token = None

                if ql_host and ql_client_id and ql_client_secret:
                    if not ql_host.endswith('/'):
                        ql_host += '/'
                    ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

                for user in users:
                    accountlist = middleware.bucketGet('JQB.hhtt.user', user)
                    if not accountlist or accountlist == '[]':
                        continue

                    accounts = eval(accountlist)
                    for account in accounts:
                        try:
                            auth = middleware.bucketGet('JQB.hhtt.auth', account)
                            account_data = middleware.bucketGet('JQB.hhtt.account', account)

                            if not account_data or not auth:
                                continue

                            if auth == '未授权' or auth < today_time:
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(auth, "%Y-%m-%d").date()

                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('JQB.hhtt.auth', account, str(new_date))

                            # 更新青龙变量（只保存手机号和密码）
                            if ql_token:
                                account_info = json.loads(account_data)
                                password = account_info.get('password')

                                if password:
                                    remarks = f"和合天台账号{mask_phone(account)}丨用户:{user}丨授权时间:{new_date}"
                                    env_data = {
                                        "name": var_name,
                                        "value": f"{account}#{password}",
                                        "remarks": remarks
                                    }
                                    env_id = add_to_qinglong(ql_host, ql_token, env_data)
                                    if env_id:
                                        middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))
                            total_success += 1
                        except:
                            continue

                msg = f"""
=====批量修改完成=====
✅ 成功修改: {total_success}个账号
⏰ 调整天数: {days}天
=================="""
                sender.reply(msg)

            except ValueError:
                sender.reply('❌ 输入的天数无效!')
                return

        elif sub_choice == '2':
            # 修改单独用户
            sender.reply('📝 请输入需要修改的用户ID\n💡 通过给机器人发送"myuid"获得\n⚠️ 输入"q"退出操作')
            user_id = sender.input(60000, 1, False)
            if user_id == 'q' or user_id == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif user_id == '':
                sender.reply('⏰ 输入超时!')
                return

            accountlist = middleware.bucketGet('JQB.hhtt.user', user_id)
            if not accountlist or accountlist == '[]':
                sender.reply(f"❌ 未找到用户 {user_id} 的和合天台账号信息!")
                return

            accounts = eval(accountlist)
            n = 0
            msg = '=====用户账号列表=====\n'
            msg += '0、修改所有账号\n==================\n'

            for account in accounts:
                n += 1
                auth = middleware.bucketGet('JQB.hhtt.auth', account)
                if not auth:
                    auth_status = '未授权'
                elif auth < today_time:
                    auth_status = '授权过期'
                else:
                    auth_status = f'到期: {auth}'
                msg += f'{n}、账号:{mask_phone(account)}\n授权状态: {auth_status}\n==================\n'

            msg += f'📝 回复序号选择账号\n⚠️ 输入"q"退出操作'
            sender.reply(msg)
            choice = sender.input(60000, 1, False)

            if choice == 'q' or choice == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif choice == '':
                sender.reply('⏰ 输入超时!')
                return

            if choice == '0':
                # 修改该用户的所有账号
                sender.reply('📝 请输入要调整的天数:\n➕ 正数增加天数\n➖ 负数减少天数\n💡 例如: 100 或 -100\n⚠️ 输入"q"退出操作')
                days = sender.input(60000, 1, False)

                if days == 'q' or days == 'Q':
                    sender.reply("✅ 已取消操作")
                    return
                elif days == '':
                    sender.reply('⏰ 输入超时!')
                    return

                try:
                    days = int(days)
                    success_count = 0

                    # 获取青龙配置
                    ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                    ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                    ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
                    var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
                    ql_token = None

                    if ql_host and ql_client_id and ql_client_secret:
                        if not ql_host.endswith('/'):
                            ql_host += '/'
                        ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

                    for account in accounts:
                        try:
                            auth = middleware.bucketGet('JQB.hhtt.auth', account)
                            account_data = middleware.bucketGet('JQB.hhtt.account', account)

                            if not account_data or not auth:
                                continue

                            if auth == '未授权' or auth < today_time:
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(auth, "%Y-%m-%d").date()

                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('JQB.hhtt.auth', account, str(new_date))

                            # 更新青龙变量（只保存手机号和密码）
                            if ql_token:
                                account_info = json.loads(account_data)
                                password = account_info.get('password')

                                if password:
                                    remarks = f"和合天台账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{new_date}"
                                    env_data = {
                                        "name": var_name,
                                        "value": f"{account}#{password}",
                                        "remarks": remarks
                                    }
                                    env_id = add_to_qinglong(ql_host, ql_token, env_data)
                                    if env_id:
                                        middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))
                            success_count += 1
                        except:
                            continue

                    msg = f"""
=====批量修改完成=====
✅ 成功修改: {success_count}个账号
⏰ 调整天数: {days}天
=================="""
                    sender.reply(msg)

                except ValueError:
                    sender.reply('❌ 输入的天数无效!')
                    return

            elif 1 <= int(choice) <= len(accounts):
                # 修改单个账号
                account = accounts[int(choice)-1]
                sender.reply('📝 请输入要调整的天数:\n➕ 正数增加天数\n➖ 负数减少天数\n💡 例如: 100 或 -100\n⚠️ 输入"q"退出操作')
                days = sender.input(60000, 1, False)

                if days == 'q' or days == 'Q':
                    sender.reply("✅ 已取消操作")
                    return
                elif days == '':
                    sender.reply('⏰ 输入超时!')
                    return

                try:
                    days = int(days)
                    auth = middleware.bucketGet('JQB.hhtt.auth', account)
                    account_data = middleware.bucketGet('JQB.hhtt.account', account)

                    if not account_data or not auth:
                        sender.reply("❌ 未找到账号信息!")
                        return

                    if auth == '未授权' or auth < today_time:
                        current_date = today_date
                    else:
                        current_date = datetime.strptime(auth, "%Y-%m-%d").date()

                    new_date = current_date + timedelta(days=days)
                    middleware.bucketSet('JQB.hhtt.auth', account, str(new_date))

                    # 更新青龙变量（只保存手机号和密码）
                    ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                    ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                    ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
                    var_name = middleware.bucketGet('JQB.hhtt', 'var_name') or 'hhtt'
                    ql_token = None

                    if ql_host and ql_client_id and ql_client_secret:
                        if not ql_host.endswith('/'):
                            ql_host += '/'
                        ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)
                        if ql_token:
                            account_info = json.loads(account_data)
                            password = account_info.get('password')

                            if password:
                                remarks = f"和合天台账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{new_date}"
                                env_data = {
                                    "name": var_name,
                                    "value": f"{account}#{password}",
                                    "remarks": remarks
                                }
                                env_id = add_to_qinglong(ql_host, ql_token, env_data)
                                if env_id:
                                    middleware.bucketSet('JQB.hhtt.env_id', account, str(env_id))

                    msg = f"""
=====修改成功=====
✅ 账号: {mask_phone(account)}
⏰ 调整天数: {days}天
🕛 新到期时间: {new_date}
=================="""
                    sender.reply(msg)

                except ValueError:
                    sender.reply('❌ 输入的天数无效!')
                    return
            else:
                sender.reply('❌ 输入的序号无效!')
                return
        else:
            sender.reply('❌ 输入的选项无效!')
            return
    elif choice == '4':
        # 管理员删除用户账号
        users = middleware.bucketAllKeys('JQB.hhtt.user')
        if not users:
            return sender.reply("❌ 没有可删除的用户账号")

        # 显示用户列表
        menu = "=====选择要删除的用户=====\n"
        for idx, user in enumerate(users, 1):
            accounts = eval(middleware.bucketGet('JQB.hhtt.user', user) or [])
            menu += f"[{idx}] 用户ID: {user} (账号数: {len(accounts)})\n"
        menu += "=======================\n⚠️ 回复数字序号(输入q退出)"
        sender.reply(menu)

        choice = sender.input(60000, 1, False)
        if not choice or choice.lower() == 'q':
            return sender.reply('已取消操作')

        try:
            index = int(choice) - 1
            if 0 <= index < len(users):
                user_id = users[index]

                # 获取该用户的所有账号
                accounts = eval(middleware.bucketGet('JQB.hhtt.user', user_id) or [])

                # 显示该用户的账号列表
                menu = "=====用户账号列表=====\n"
                menu += "0、删除所有账号\n==================\n"
                for idx, account in enumerate(accounts, 1):
                    auth = middleware.bucketGet('JQB.hhtt.auth', account)
                    if not auth:
                        auth_status = '未授权'
                    elif auth < today_time:
                        auth_status = '授权过期'
                    else:
                        auth_status = f'到期: {auth}'
                    menu += f"{idx}、账号: {mask_phone(account)}\n授权状态: {auth_status}\n==================\n"
                menu += "📝 回复序号选择账号\n⚠️ 输入'q'退出操作"
                sender.reply(menu)

                # 获取管理员选择
                acc_choice = sender.input(60000, 1, False)
                if not acc_choice or acc_choice.lower() == 'q':
                    return sender.reply('已取消操作')

                if acc_choice == '0':
                    # 删除所有账号
                    confirm_msg = f"""=====⚠️警告⚠️=====
即将删除用户ID: {user_id} 的所有账号
账号列表:
{", ".join([mask_phone(acc) for acc in accounts])}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                    sender.reply(confirm_msg)

                    confirm = sender.input(60000, 1, False)
                    if confirm.lower() != 'y':
                        return sender.reply('✅ 已取消删除操作')

                    # 获取青龙配置
                    ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                    ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                    ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
                    ql_token = None

                    if ql_host and ql_client_id and ql_client_secret:
                        if not ql_host.endswith('/'):
                            ql_host += '/'
                        ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

                    # 删除所有账号及环境变量
                    deleted_count = 0
                    for account in accounts:
                        try:
                            # 删除青龙环境变量
                            if ql_token:
                                env_id = middleware.bucketGet('JQB.hhtt.env_id', account)
                                if env_id:
                                    delete_qinglong_env(ql_host, ql_token, env_id)

                            # 删除本地存储
                            middleware.bucketDel('JQB.hhtt.account', account)
                            middleware.bucketDel('JQB.hhtt.auth', account)
                            middleware.bucketDel('JQB.hhtt.env_id', account)
                            deleted_count += 1
                        except:
                            continue

                    # 删除用户记录
                    middleware.bucketDel('JQB.hhtt.user', user_id)

                    sender.reply(f"✅ 已删除用户 {user_id} 的 {deleted_count} 个账号")

                elif acc_choice.isdigit() and 1 <= int(acc_choice) <= len(accounts):
                    # 删除单个账号
                    acc_index = int(acc_choice) - 1
                    account = accounts[acc_index]

                    confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
📱 账号: {mask_phone(account)}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                    sender.reply(confirm_msg)

                    confirm = sender.input(60000, 1, False)
                    if confirm.lower() != 'y':
                        return sender.reply('✅ 已取消删除操作')

                    # 获取青龙配置
                    ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
                    ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
                    ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')

                    # 删除青龙环境变量
                    if ql_host and ql_client_id and ql_client_secret:
                        if not ql_host.endswith('/'):
                            ql_host += '/'
                        ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)
                        if ql_token:
                            env_id = middleware.bucketGet('JQB.hhtt.env_id', account)
                            if env_id:
                                delete_qinglong_env(ql_host, ql_token, env_id)

                    # 删除本地存储
                    middleware.bucketDel('JQB.hhtt.account', account)
                    middleware.bucketDel('JQB.hhtt.auth', account)
                    middleware.bucketDel('JQB.hhtt.env_id', account)

                    # 更新用户账号列表
                    accounts.pop(acc_index)
                    if accounts:
                        middleware.bucketSet('JQB.hhtt.user', user_id, str(accounts))
                    else:
                        middleware.bucketDel('JQB.hhtt.user', user_id)

                    sender.reply(f"✅ 已删除账号: {mask_phone(account)}")
                else:
                    sender.reply('❌ 输入的序号无效!')
            else:
                sender.reply('❌ 选择超出范围')
        except:
            sender.reply('❌ 输入错误')
    else:
        sender.reply('❌ 输入的选项无效!')

def main():
    """主入口"""
    try:
        # 初始化sender对象
        senderID = middleware.getSenderID()
        sender = middleware.Sender(senderID)
        message = sender.getMessage().strip().lower()

        if '登录' in message:
            bind(sender)
        elif '查询' in message:
            query(sender)
        elif '签到' in message:
            sign_in(sender)
        elif '管理' in message:
            manage_accounts(sender)
        elif '教程' in message or '帮助' in message:
            tutorial(sender)
        elif message == '和合天台清理' and sender.isAdmin():
            clean_expired(sender)
        elif message == '和合天台授权' and sender.isAdmin():
            hhtt_auth(sender)
        elif message in ['和合天台中奖通知', '和合天台中奖推送']:
            prize_push_command(sender)
        elif message == '和合天台一键运行' and sender.isAdmin():
            admin_run_all_users_tasks(sender)
        else:
            sender.reply("""指令未识别，可用指令:
和合天台登录 - 绑定账号
和合天台查询 - 查看积分和抽奖记录及提现状态
和合天台签到 - 执行任务（含提现）
和合天台管理 - 账号管理（含提现开关）
和合天台教程 - 使用说明
和合天台中奖通知 - 管理员手动推送账户状态通知
和合天台一键运行 - 管理员运行全服所有账号任务""")
    except Exception as e:
        traceback.print_exc()
        # 尝试发送错误消息
        try:
            senderID = middleware.getSenderID()
            if senderID:
                sender = middleware.Sender(senderID)
                sender.reply(f"❌ 插件运行出错: {str(e)}")
        except:
            pass

def clean_expired(sender):
    """清理过期账号（包括青龙环境变量）"""
    if not sender.isAdmin():
        return sender.reply("❌ 需要管理员权限")

    today_date = datetime.now().date()
    today_time = str(today_date)

    users = middleware.bucketAllKeys('JQB.hhtt.user')
    cleaned = 0

    # 获取青龙配置
    ql_host = middleware.bucketGet('JQB.hhtt', 'ql_host')
    ql_client_id = middleware.bucketGet('JQB.hhtt', 'ql_client_id')
    ql_client_secret = middleware.bucketGet('JQB.hhtt', 'ql_client_secret')
    ql_token = None

    if ql_host and ql_client_id and ql_client_secret:
        if not ql_host.endswith('/'):
            ql_host += '/'
        ql_token = get_ql_token(ql_host, ql_client_id, ql_client_secret)

    for user in users:
        accounts = eval(middleware.bucketGet('JQB.hhtt.user', user) or [])
        valid = []

        for account in accounts:
            auth = middleware.bucketGet('JQB.hhtt.auth', account)
            if not auth or auth < today_time:
                # 删除青龙环境变量
                if ql_token:
                    env_id = middleware.bucketGet('JQB.hhtt.env_id', account)
                    if env_id:
                        delete_qinglong_env(ql_host, ql_token, env_id)

                # 删除过期账号
                middleware.bucketDel('JQB.hhtt.account', account)
                middleware.bucketDel('JQB.hhtt.auth', account)
                middleware.bucketDel('JQB.hhtt.env_id', account)
                cleaned += 1
            else:
                valid.append(account)

        if valid:
            middleware.bucketSet('JQB.hhtt.user', user, str(valid))
        else:
            middleware.bucketDel('JQB.hhtt.user', user)

    sender.reply(f"✅ 已清理 {cleaned} 个过期账号")

if __name__ == "__main__":
    try:
        # 检测是否是定时任务
        if middleware.getSenderID() == "":
            # 定时任务模式：每天8点执行中奖推送
            hhtt_scheduled_push(return_report=False)
        else:
            # 用户交互模式
            main()
    except Exception as e:
        traceback.print_exc()
        # 尝试发送错误消息
        try:
            senderID = middleware.getSenderID()
            if senderID:
                sender = middleware.Sender(senderID)
                sender.reply(f"❌ 插件运行出错: {str(e)}")
        except:
            pass