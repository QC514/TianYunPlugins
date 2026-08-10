#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卡看插件 - 青龙面板对接版本
支持账号管理、授权控制、青龙同步
任务在青龙中执行，插件只负责账号管理
"""

# [disable: false]
# [title: 卡看]
# [platform: qq,wx,wxmp,tg]
# [price: 8.8]
# [service: QQ群1067957630]
# [rule: ^卡看(教程|登录|管理|查询|刷进度)$]
# [admin: false]
# [version: 1.0.1]
# [author: dandan8]
# [open_source: false]
# [icon: https://example.com/icon.png]
# [description: ]

import middleware
import requests
import json
import time
import random
import base64
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
from decimal import Decimal
from urllib.parse import quote, quote_plus, urlparse, parse_qs, unquote
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print('卡看助手 v1.0.0 加载中...')

# ==================== 插件参数配置 ====================
# [param: {"required":true,"key":"dd_kakan_config.Qinglong","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret","name":"青龙面板配置","desc":"青龙面板地址、应用ID、应用密钥，用中文丨分隔"}]
# [param: {"required":true,"key":"dd_kakan_config.env_name","bool":false,"placeholder":"kakan","name":"青龙变量名","desc":"青龙容器内卡看的环境变量名"}]
# [param: {"required":false,"key":"dd_kakan_config.coin_price","bool":false,"placeholder":"10","name":"积分授权价格","desc":"授权一天需要多少积分（整数）"}]
# [param: {"required":false,"key":"dd_kakan_config.money_price","bool":false,"placeholder":"0.5","name":"支付授权价格","desc":"授权一天需要多少元（单位：元），设为0或不填则关闭微信支付"}]
# [param: {"required":false,"key":"dd_kakan_config.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款码链接","desc":"微信/支付宝收款码图片链接"}]
# [param: {"required":false,"key":"dd_kakan_config.coin_bucket","bool":false,"placeholder":"dd_sign_points","name":"积分桶名称","desc":"存储用户积分的bucket名称"}]
# [param: {"required":false,"key":"dd_kakan_config.admin_ids","bool":false,"placeholder":"1580661262,admin_wx_id","name":"管理员ID列表","desc":"管理员ID，逗号分隔"}]
# [param: {"required":false,"key":"dd_kakan_config.proxy_url","bool":false,"placeholder":"https://service.ipzan.com/core-extract?num=1&no=xxx&secret=xxx","name":"代理提取链接","desc":"查询时使用的代理提取链接，不填则不使用代理"}]

# ==================== 初始化 ====================
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
username = sender.getUserName() or "未知用户"

# ==================== 常量配置 ====================
CANCEL_KEY = 'q'
TOKEN_CACHE_TIME = 23 * 3600
DEFAULT_COIN_BUCKET = 'dd_sign_points'

# ==================== API配置 ====================
RSA_PRIVATE_KEY_B64 = "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCWLxnotIP3pNK4Vb/MEvm205lz1gRyFuXS0Td1v2cDfkJibxwWBRGtkP5LjmhxH/6TuFaoKGrEqBKqpfNuMcOG8l6FRTO7XgqMr6QfCb47I/FHsg3j4UNGy8cMzA3Ei/PpM9SxeTImIclvJ7zBXlJZjQyZ8jMClEfm+AnzXb4dXJe/tjd+iLnms15+2T2HjOCI9+EsBdbtHZ482F/G+nO1OL7J2/MmEkwnjhm+WcXm3fu5MjXIUHBKL11vYMYSvIh0+w0xI85hDiuz1Q6lYS7AdIaEGWtA0wfGT0iYQNQc+cDU3Ev9PMyTowdfOeTcnfwq6+BkOcW0AwZOzPQA++8BAgMBAAECggEAK0X0FbCZy8vSqamPg5o+GJdcwls62bLOUtHUxJk7ce656wnv0kpwnw3Fr/ifEGVzIZY+ZeKLbRGumzwI6cnt+F6yrHzVnJnKuWHMjOLuTLUdCxb7WJtqGqaRupa7KtRWme3EzcRJlmIq29vbz+3BFauGI399gjM+iocSuuxaYLQBenDu0xlI2a3bYH4zxV8kJ4pKc4qu+jmM84csc/sFoGkEFOQ5im6TJubNQ+PVdHSpSAitR/E7Sq57Nyw5IFkbZxX5R0XequX8f4XDt6lOmg5dBu/mouBMEPhGvnbY/5YpD0TGTi1BcAWWbMDjqhHX6L0WV/e1bQqwlBK5faO8pwKBgQDTBYW5AJfLVRcv6UJNPD5U5+stDTy2FGdZaaEW+AytbPT6xkDl8MVoey6zV5G6gDn8wOGwhW3YoJCchwT34jCR9rYlhCIxRRX7aaRAzqyiXM7B3ZACLVSfaCkiPA/7tYAlReaKKOIRXRVlmRKy5KKvEHzqkIPAGc6Z/e2ZmgD3AwKBgQC2MfOUa29DAEc9s8QXwc0hvAIRgjPjTn/8KNUQyhwVSRb5Xj/GRuAMII4dUGsKR1DnME4CHixRZhjEJwTeS04BPb2Mgnu9s/Wl7A/pd+3lm8Qzux+uDmP6vmlJe4hsPfm5axPOCAMGI0gq5YM01GiRwPqYIpjuL7UrpXg5wmJQqwKBgFVSDElK5hT+aIukonwb+Y/W3Y2vpnZwNYE/ZjSlQmr0fPDQK/lMqmSeObmllHR11/xL+HSo3ksSUKYZKXcYa075E5iDnleReVvX0OOrLL3RDH/yF4Hp1idFtCv1YPkC37cyVg5SjWU736TeiWLvcp+Z6QfmOn73cENvGhxa2j0FAoGBAITLPaVE9PBZyJMRbnB+Ydwfo0ZNpzIa6i/JNxqopPVis2sIJeWHjQ9pvwtgrNPuDOqki4cBpP2jM5PseKDpNC61aG18QWKQQxAvUZ2yOuPqt4OY9MsxU+/TTvwvHM0AEv7xK5s0vbeAib4yUIJ1+s2ZYUz3ko2wmhT44vr+UhhHAoGBALeia7zaiLQWr5h+X+DQfIaMWX2FrFwx16UXxKPAlTSdrj0UGQDZsG9uk7KIMZVs/LFnasAhflWRwX6gYADssXyPGeeOSWkOk7fTSZduj7KXXKMQYIl5OQ9nnCaqJNVHh/7xt+0avU2DlcUSrjSFxeF4cd6tO/kWcnPlWqp9M9OB"

AES_KEY = b'5d5e2890a7e84598'
AES_IV = b'5d5e2890a7e84598'

BASE_URL = 'https://welfare-user.palmestore.com'
DURATION_URL = 'https://kakan-api.zhangyue.com'
WELFARE_URL = 'https://kakan-welfare.zhangyue.com'

# ==================== 工具函数 ====================
def format_number(num):
    """格式化数字，添加千分位"""
    return f"{num:,}"

def empower(current_auth: str, days: int) -> str:
    """计算授权到期时间（按天计算）"""
    today = datetime.datetime.now()
    
    if current_auth and current_auth not in ['未授权', '授权过期']:
        try:
            expire_date = datetime.datetime.strptime(current_auth, '%Y-%m-%d')
            if expire_date > today:
                new_expire = expire_date + datetime.timedelta(days=days)
            else:
                new_expire = today + datetime.timedelta(days=days)
        except:
            new_expire = today + datetime.timedelta(days=days)
    else:
        new_expire = today + datetime.timedelta(days=days)
    
    return new_expire.strftime('%Y-%m-%d')

# ==================== 签名管理器 ====================
class SignatureManager:
    """签名管理器"""
    _rsa_key = None
    
    X_SIG_VER = "v1.1"

    DEFAULT_HEADERS = {
        'X-AppId': 'zya3c0e0',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'Keep-Alive'
    }
    
    @staticmethod
    def generate_user_agent(device_info: dict, api_path: str = '', base_url: str = '') -> str:
        """根据设备信息生成User-Agent"""
        android_ver = device_info.get('p22', '15')
        device_model = device_info.get('p16', 'PHK110')
        build_id = device_info.get('build_id', 'AP3A.240617.008')
        
        if base_url in [DURATION_URL, WELFARE_URL] or api_path.startswith('/taiji_user/'):
            return f"Dalvik/2.1.0 (Linux; U; Android {android_ver}; {device_model} Build/{build_id})"
        
        channel = device_info.get('p2', '731006')
        app_id = device_info.get('p29', 'zya3c0e0')
        
        chrome_ver = f"{random.randint(80, 120)}.0.{random.randint(4000, 6000)}.{random.randint(100, 200)}"
        
        ua = (f"Mozilla/5.0 (Linux; Android {android_ver}; {device_model} Build/V417IR; wv) "
              f"AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_ver} "
              f"Mobile Safari/537.36 zyHybridVer/2.3.1 zyApp/kakan zyVersion/1.2.0.1 "
              f"zyChannel/{channel} zyAppid/{app_id}")
        return ua
    
    @classmethod
    def _get_rsa_key(cls):
        if cls._rsa_key is None:
            cls._rsa_key = RSA.import_key(base64.b64decode(RSA_PRIVATE_KEY_B64))
        return cls._rsa_key
    
    @staticmethod
    def aes_encrypt(plain_text: str) -> str:
        cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
        padded_data = pad(plain_text.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.urlsafe_b64encode(encrypted).decode('ascii').rstrip('=')
    
    @staticmethod
    def _timestamp_xor_key(timestamp):
        """从时间戳低4位生成 XOR 密钥（对应 native sub_A150）"""
        tmp = int(timestamp)
        key = []
        for _ in range(4):
            key.append(tmp % 10)
            tmp //= 10
        return key

    @classmethod
    def make_x_sig_sec(cls, env_info=None, timestamp=None):
        """动态生成 X-SIG-Sec（对应 native sub_A150）"""
        if timestamp is None:
            timestamp = cls.get_timestamp()
        obj = {}
        if env_info is not None:
            obj["ne"] = env_info
        obj["zy"] = "d0"
        plain = json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        key = cls._timestamp_xor_key(timestamp)
        raw = bytearray(b"\x00\x01")
        for i, b in enumerate(plain):
            raw.append(b ^ key[i & 3])
        return base64.b64encode(bytes(raw)).decode("ascii")

    @staticmethod
    def build_params_string(params: dict, for_signature: bool = True) -> str:
        """Java 兼容参数序列化（对应 convertMapToParams）"""
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        parts = []
        for k, v in sorted_params:
            if v is None or str(v).strip() == "":
                continue
            text = str(v)
            if for_signature:
                text = quote_plus(text, safe="*-._")
            if text.strip() == "":
                continue
            parts.append(f"{k}={text}")
        return "&".join(parts)

    @staticmethod
    def build_origin(post_body: str, query_params, path: str, timestamp: str) -> str:
        """构建签名原文（对应 MainProviderObj.getSignHeaders）"""
        if isinstance(query_params, str):
            query_string = query_params
        elif query_params:
            query_string = SignatureManager.build_params_string(query_params, for_signature=True)
        else:
            query_string = ""
        return f"{post_body or ''}&{query_string}&{path}&{timestamp}"

    @classmethod
    def generate_signature(cls, params: dict, timestamp: str, api_path: str, sig_sec: str) -> str:
        """生成 X-SIG-Sign"""
        params_str = cls.build_params_string(params, for_signature=True)
        origin = cls.build_origin(params_str, {}, api_path, timestamp)
        sign_input = origin.encode("utf-8") + b"&" + sig_sec.encode("utf-8")

        key = cls._get_rsa_key()
        h = SHA256.new(sign_input)
        signature = pkcs1_15.new(key).sign(h)
        return base64.b64encode(signature).decode('utf-8')
    
    @staticmethod
    def get_timestamp() -> str:
        return str(int(time.time() * 1000))

    @classmethod
    def get_base_url(cls, url: str) -> str:
        if url.startswith(BASE_URL):
            return BASE_URL
        elif url.startswith(WELFARE_URL):
            return WELFARE_URL
        return DURATION_URL

# ==================== 卡看API封装 ====================
class KaKanAPI:
    """卡看API封装"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def _send_request(self, method: str, url: str, params: dict = None, 
                     data: dict = None, extra_headers: dict = None, device_info: dict = None, proxy: dict = None) -> dict:
        base_url = SignatureManager.get_base_url(url)
        sign_path = url.replace(base_url, '')
        request_params = params or data or {}

        timestamp = SignatureManager.get_timestamp()
        sig_sec = SignatureManager.make_x_sig_sec("d0", timestamp)
        signature = SignatureManager.generate_signature(request_params, timestamp, sign_path, sig_sec)

        headers = SignatureManager.DEFAULT_HEADERS.copy()
        if device_info:
            headers['User-Agent'] = SignatureManager.generate_user_agent(device_info, sign_path, base_url)
        headers.update({
            'X-SIG-Sign': signature,
            'X-SIG-Alg': 'RSA-SHA256',
            'X-SIG-Timestamp': timestamp,
            'X-SIG-Ver': SignatureManager.X_SIG_VER,
            'X-SIG-Sec': sig_sec
        })
        if extra_headers:
            headers.update(extra_headers)

        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=request_params, headers=headers, timeout=20, verify=False, proxies=proxy)
            else:
                params_str = SignatureManager.build_params_string(request_params, for_signature=True)
                response = self.session.post(url, data=params_str, headers=headers, timeout=20, verify=False, proxies=proxy)

            return response.json()
        except Exception as e:
            print(f"API请求异常: {str(e)}")
            return {'code': -1, 'msg': str(e)}
    
    def _build_common_params(self, device_info: dict, session_info: dict = None) -> dict:
        params = {
            'p1': device_info.get('p1', ''),
            'p16': device_info.get('p16', ''),
            'p2': device_info.get('p2', '731001'),
            'p21': device_info.get('p21', '3'),
            'p22': device_info.get('p22', '13'),
            'p24': device_info.get('p24', '0'),
            'p25': device_info.get('p25', '12030'),
            'p28': device_info.get('p28', ''),
            'p29': device_info.get('p29', 'zya3c0e0'),
            'p3': device_info.get('p3', '101200017'),
            'p31': device_info.get('p31', ''),
            'p33': device_info.get('p33', 'com.zhangyue.app.shortplay.kakandj'),
            'p34': device_info.get('p34', 'navigationbar_is_min'),
            'p4': device_info.get('p4', '501617'),
            'p5': device_info.get('p5', '16'),
            'p7': device_info.get('p7', device_info.get('p28', '')),
            'p9': device_info.get('p9', '2'),
            'pc': device_info.get('pc', '10'),
            'zyeid': device_info.get('zyeid', '')
        }
        
        if session_info:
            params['usr'] = session_info.get('encrypt_user_id') or session_info.get('user_id', '')
            params['zysid'] = session_info.get('session_id', '')
        
        return params
    
    def send_sms_code(self, phone: str, device_info: dict) -> tuple:
        """发送短信验证码"""
        plain_data = json.dumps({'phone': phone}, separators=(',', ':'))
        encrypt_data = SignatureManager.aes_encrypt(plain_data)
        
        url = f"{DURATION_URL}/taiji_user/sms/sendSms"
        params = self._build_common_params(device_info)
        params.update({
            'app_id': 'zya3c0e0',
            'data': encrypt_data,
            'flag': '1',
            'usr': device_info.get('usr', ''),
            'zyeid': device_info.get('zyeid', '')
        })
        response = self._send_request('POST', url, params=params, device_info=device_info)
        
        if isinstance(response, dict) and response.get('code') == 0:
            body = response.get('body', {})
            remains = body.get('remains', '未知')
            interval = body.get('interval', '未知')
            return True, remains, interval
        else:
            error_msg = response.get('msg', '未知错误') if isinstance(response, dict) else str(response)
            return False, error_msg, None
    
    def login_by_phone(self, phone: str, code: str, device_info: dict) -> tuple:
        """手机号验证码登录"""
        plain_data = json.dumps({'phone': phone}, separators=(',', ':'))
        encrypt_data = SignatureManager.aes_encrypt(plain_data)
        
        url = f"{DURATION_URL}/taiji_user/login/loginByPhone"
        params = self._build_common_params(device_info)
        params.update({
            'app_id': 'zya3c0e0',
            'data': encrypt_data,
            'device_no': device_info.get('p1', ''),
            'p_code': code,
            'usr': device_info.get('usr', ''),
            'visitor_id': device_info.get('visitor_id', device_info.get('usr', '')),
            'zyeid': device_info.get('zyeid', '')
        })
        response = self._send_request('POST', url, params=params, device_info=device_info)
        
        if isinstance(response, dict) and response.get('code') == 0:
            user_info = response.get('body', {})
            return True, user_info
        else:
            error_msg = response.get('msg', '未知错误') if isinstance(response, dict) else str(response)
            return False, {'error': error_msg}
    
    def get_user_info(self, device_info: dict, session_info: dict, proxy: dict = None) -> tuple:
        """获取用户信息"""
        params = self._build_common_params(device_info, session_info)
        
        url = f"{BASE_URL}/api/user/info"
        response = self._send_request('GET', url, params=params, device_info=device_info, proxy=proxy)
        
        if isinstance(response, dict) and response.get('code') == 0:
            return True, response.get('body', {})
        return False, None
    
    def get_gold_account(self, device_info: dict, session_info: dict, proxy: dict = None) -> tuple:
        """获取金币账户信息"""
        params = self._build_common_params(device_info, session_info)
        params['gold_type'] = '3'
        
        url = f"{BASE_URL}/api/user/gold_account"
        response = self._send_request('GET', url, params=params, device_info=device_info, proxy=proxy)
        
        if isinstance(response, dict) and response.get('code') == 0:
            return True, response.get('body', {})
        return False, None
    
    def get_task_user_info(self, device_info: dict, session_info: dict, task_ids: str = '3119,3801,3014') -> tuple:
        """获取任务用户信息"""
        params = self._build_common_params(device_info, session_info)
        params['act_id'] = '1021'
        params['task_ids'] = task_ids
        
        url = f"{BASE_URL}/api/task/task/user_info/by_user"
        response = self._send_request('GET', url, params=params, device_info=device_info)
        
        if isinstance(response, dict) and response.get('code') == 0:
            return True, response.get('body', {})
        return False, None
    
    def get_bind_info(self, device_info: dict, session_info: dict) -> tuple:
        """获取绑定信息"""
        params = self._build_common_params(device_info, session_info)
        params['extract_type'] = '2'
        
        url = f"{BASE_URL}/api/user/withdraw/schedule"
        response = self._send_request('GET', url, params=params, device_info=device_info)
        
        if isinstance(response, dict) and response.get('code') == 0:
            body = response.get('body', {})
            bind_info = body.get('bind_info', {})
            return True, bind_info
        return False, None
    
    def receive_task(self, device_info: dict, session_info: dict, task_id: int, 
                     receive_type: str = '4', act_id: int = 1021, 
                     sub_task_id: str = None, proxy: dict = None) -> tuple:
        """领取任务奖励"""
        params = self._build_common_params(device_info, session_info)
        params['task_id'] = str(task_id)
        params['receive_type'] = receive_type
        params['act_id'] = str(act_id)
        if sub_task_id:
            params['sub_task_id'] = sub_task_id
        
        url = f"{BASE_URL}/api/task/task/receive"
        response = self._send_request('POST', url, params=params, device_info=device_info, proxy=proxy)
        
        if isinstance(response, dict) and response.get('code') == 0:
            return True, response.get('body', {})
        else:
            error_msg = response.get('msg', '未知错误') if isinstance(response, dict) else str(response)
            return False, {'error': error_msg}
    
    def complete_ad_task(self, device_info: dict, session_info: dict, task_type: int = 106) -> bool:
        """完成广告任务（攒进度）"""
        params = self._build_common_params(device_info, session_info)
        params['task_type'] = str(task_type)
        
        url = f"{BASE_URL}/api/task/done"
        response = self._send_request('POST', url, params=params, device_info=device_info)
        
        if isinstance(response, dict) and response.get('code') == 0:
            return True
        return False

# ==================== 设备管理器 ====================
class DeviceManager:
    """设备管理器"""
    
    DEVICE_MODELS = [
        ('PHK110', '15', 'OnePlus', 'PHK110'),
        ('PTP-AN70', '15', 'Huawei', '23117RK66C'),
        ('VOG-AL00', '12', 'Huawei', 'VOG-AL00'),
        ('ELE-AL00', '11', 'Huawei', 'ELE-AL00'),
        ('SEA-AL10', '10', 'Huawei', 'SEA-AL10'),
        ('PAR-AL00', '9', 'Huawei', 'PAR-AL00'),
        ('Redmi K50', '12', 'Xiaomi', '22041211AC'),
        ('Redmi Note 11', '11', 'Xiaomi', '2201117TI'),
        ('OPPO Find X', '11', 'OPPO', 'PAFM00'),
        ('vivo X80', '12', 'vivo', 'V2145A'),
        ('OnePlus 9', '11', 'OnePlus', 'LE2110'),
    ]
    
    NAV_PROPS = ['navigationbar_is_min', 'force_fsg_nav_bar', 'notch']
    
    @staticmethod
    def generate_shumei_id() -> str:
        p35_bytes = bytes([random.choice([0x06, 0x07])])
        p35_bytes += bytes([random.randint(0, 255) for _ in range(16)])
        p35_bytes += bytes([random.randint(0, 255) for _ in range(48)])
        return base64.b64encode(p35_bytes).decode('utf-8')
    
    @staticmethod
    def generate_p28() -> str:
        prefix = ''.join(random.choices('0123456789ABCDEF', k=32))
        suffix = ''.join(random.choices('0123456789abcdef', k=32))
        return prefix + suffix
    
    @staticmethod
    def generate_oaid() -> str:
        return ''.join(random.choices('0123456789abcdef', k=16))
    
    @staticmethod
    def generate_imei() -> str:
        return ''.join(random.choices('0123456789', k=15))
    
    @staticmethod
    def generate_android_id() -> str:
        return ''.join(random.choices('0123456789abcdef', k=16))
    
    @staticmethod
    def generate_device_info(url_params: dict = None, phone: str = None) -> dict:
        seed = ''.join(random.choices('0123456789abcdef', k=32))
        android_release = random.choice(["12", "13", "14"])
        model = random.choice(["Pixel6", "Pixel7", "Mi10", "V2241A", "PDEM30"])
        build_id = ''.join(random.choices('0123456789ABCDEF', k=8))
        oaid = ''.join(random.choices('0123456789abcdef', k=32))
        android_id = ''.join(random.choices('0123456789abcdef', k=16))
        visitor_id = "tj" + ''.join(random.choices('0123456789', k=16))
        p1 = str(int(time.time() * 1000)) + ''.join(random.choices('0123456789', k=6))

        device_info = {
            'p1': p1,
            'p16': model,
            'p31': android_id,
            'p28': oaid,
            'p2': '731001',
            'p21': '3',
            'p22': android_release,
            'p24': '0',
            'p25': '12030',
            'p29': 'zya3c0e0',
            'p3': '101200017',
            'p33': 'com.zhangyue.app.shortplay.kakandj',
            'p34': 'navigationbar_is_min',
            'p4': '501617',
            'p5': '16',
            'p7': oaid,
            'p9': '2',
            'pc': '10',
            'build_id': build_id,
            'brand': 'Google',
            'device': model,
            'model': model,
            'product': model.lower(),
            'manufacturer': 'Google',
            'android_version': android_release,
            'network_type': '3',
            'sim_type': '2',
            'device_info_prop': 'navigationbar_is_min',
            'lang': 'zh_CN',
            'timezone': 'Asia/Shanghai',
            'oaid': oaid,
            'android_id': android_id,
            'usr': visitor_id,
            'visitor_id': visitor_id,
            'zyeid': hashlib.md5(seed.encode('ascii')).hexdigest(),
            'user_agent': f"Dalvik/2.1.0 (Linux; U; Android {android_release}; {model} Build/{build_id})",
            'createTime': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if url_params:
            for key, value in url_params.items():
                device_info[key] = value
        
        if phone:
            if 'usr' not in device_info or not device_info.get('usr'):
                device_info['usr'] = visitor_id
            if 'zyeid' not in device_info or not device_info.get('zyeid'):
                device_info['zyeid'] = hashlib.md5(seed.encode('ascii')).hexdigest()
            if 'zysid' not in device_info or not device_info.get('zysid'):
                device_info['zysid'] = ''.join(random.choices('0123456789abcdef', k=32))
        
        return device_info
    
    @staticmethod
    def parse_url_params(url: str) -> dict:
        """从URL解析参数"""
        try:
            parsed = urlparse(url.strip())
            params = parse_qs(parsed.query)
            
            extracted = {}
            for key, values in params.items():
                extracted[key] = unquote(values[0])
            
            return extracted
        except:
            return {}

# ==================== 代理管理 ====================
_proxy_cache = {'proxy': None, 'expire_time': 0, 'info': '本地'}

def get_proxy(proxy_url: str) -> tuple:
    """
    获取代理配置
    返回: (proxy_dict, proxy_info)
    - proxy_dict: 代理字典，用于requests
    - proxy_info: 代理信息字符串，用于显示
    """
    global _proxy_cache
    
    if not proxy_url:
        return {}, '本地'
    
    if _proxy_cache['proxy'] and time.time() < _proxy_cache['expire_time']:
        return _proxy_cache['proxy'], _proxy_cache['info']
    
    try:
        response = requests.get(proxy_url, timeout=10)
        proxy_text = response.text.strip()
        
        if ':' in proxy_text:
            parts = proxy_text.split(':')
            if len(parts) >= 2:
                host = parts[0]
                port = parts[1]
                proxy = {
                    'http': f'http://{host}:{port}',
                    'https': f'http://{host}:{port}'
                }
                proxy_info = f"{host}:{port}"
                _proxy_cache['proxy'] = proxy
                _proxy_cache['expire_time'] = time.time() + 55
                _proxy_cache['info'] = proxy_info
                print(f"✅ 获取代理成功: {host}:{port}")
                return proxy, proxy_info
    except Exception as e:
        print(f"⚠️ 获取代理失败: {str(e)}")
    
    return {}, '本地'

# ==================== 插件配置获取 ====================
def get_plugin_config():
    """获取插件配置数据"""
    Qinglong = middleware.bucketGet(bucket='dd_kakan_config', key='Qinglong')
    env_name = middleware.bucketGet(bucket='dd_kakan_config', key='env_name') or 'kakan'
    coin_price = middleware.bucketGet(bucket='dd_kakan_config', key='coin_price')
    money_price = middleware.bucketGet(bucket='dd_kakan_config', key='money_price')
    zsm = middleware.bucketGet(bucket='dd_kakan_config', key='zsm')
    coin_bucket = middleware.bucketGet(bucket='dd_kakan_config', key='coin_bucket') or DEFAULT_COIN_BUCKET
    admin_ids_str = middleware.bucketGet(bucket='dd_kakan_config', key='admin_ids') or ''
    
    if not Qinglong:
        sender.reply("""==================
    配置错误
==================
❌ 未配置青龙信息
------------------
请在插件配置中填写:
Host丨ClientID丨ClientSecret
• 使用中文丨分隔
• 示例:
http://ql.example.com丨abcd丨1234
==================""")
        exit(0)
    
    qllist = Qinglong.split('丨')
    if len(qllist) != 3:
        sender.reply("""==================
    格式错误
==================
❌ 青龙配置格式错误
------------------
正确格式:
Host丨ClientID丨ClientSecret
==================""")
        exit(0)
    
    QLurl = qllist[0].strip()
    ClientID = qllist[1].strip()
    ClientSecret = qllist[2].strip()
    
    if not all([QLurl, ClientID, ClientSecret]):
        sender.reply("""==================
    参数错误
==================
❌ 青龙配置参数不完整
------------------
请确保以下参数都已填写:
• 青龙面板地址
• 应用ID(ClientID)
• 应用密钥(ClientSecret)
==================""")
        exit(0)
    
    if not QLurl.startswith(('http://', 'https://')):
        sender.reply(f"""==================
    地址错误
==================
❌ 青龙地址格式错误
------------------
当前地址: {QLurl}
正确格式:
• http://qinglong.example.com
• https://ql.example.com:5700
==================""")
        exit(0)
    
    coin_price = int(coin_price or '9999')
    
    try:
        money_price = Decimal(money_price or '0')
    except:
        money_price = Decimal('0')
    
    admin_ids = [aid.strip() for aid in admin_ids_str.split(',') if aid.strip()]
    
    proxy_url = middleware.bucketGet(bucket='dd_kakan_config', key='proxy_url') or ''
    
    wechat_enabled = money_price > 0 and zsm
    
    return QLurl, ClientID, ClientSecret, env_name, coin_price, money_price, zsm, coin_bucket, admin_ids, wechat_enabled, proxy_url

# ==================== 青龙API封装 ====================
class QingLongAPI:
    """青龙面板API封装类"""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url.rstrip('/')
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = None
        self.token_expire_time = 0
    
    def _get_token(self):
        """获取访问token（带缓存）"""
        try:
            if self.token and time.time() < self.token_expire_time:
                return self.token
            
            url = f"{self.base_url}/open/auth/token"
            params = {
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            if result.get('code') == 200:
                self.token = result['data']['token']
                self.token_expire_time = time.time() + TOKEN_CACHE_TIME
                return self.token
            else:
                print(f"获取token失败: {result.get('message', '未知错误')}")
                return None
        
        except Exception as e:
            print(f"获取token异常: {str(e)}")
            return None
    
    def _request(self, method: str, endpoint: str, data=None, params=None):
        """发送HTTP请求"""
        token = self._get_token()
        if not token:
            return None
        
        try:
            url = f"{self.base_url}/open/{endpoint}"
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = None
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, json=data, timeout=30)
            else:
                return None
            
            result = response.json()
            return result if result.get('code') == 200 else None
        
        except Exception as e:
            print(f"API请求异常: {str(e)}")
            return None
    
    def get_envs(self, search_value=None):
        """获取环境变量列表"""
        params = {}
        if search_value:
            params['searchValue'] = search_value
        
        result = self._request('GET', 'envs', params=params)
        if result and result.get('data'):
            return result['data']
        return []
    
    def find_env_by_remark(self, env_name: str, remark: str):
        """查找指定备注的环境变量"""
        envs = self.get_envs(search_value=env_name)
        for env in envs:
            if env.get('name') == env_name:
                remarks = env.get('remarks', '')
                if f'卡看:{remark}丨' in remarks or f'备注:{remark}' in remarks:
                    return env
        return None
    
    def add_env(self, name: str, value: str, remarks: str = '') -> bool:
        """添加环境变量"""
        data = [{
            'name': name,
            'value': value,
            'remarks': remarks
        }]
        result = self._request('POST', 'envs', data=data)
        return result is not None
    
    def update_env(self, env_id: int, name: str, value: str, remarks: str = '') -> bool:
        """更新环境变量"""
        data = {
            'id': env_id,
            'name': name,
            'value': value,
            'remarks': remarks
        }
        result = self._request('PUT', 'envs', data=data)
        return result is not None
    
    def delete_env(self, env_ids: list) -> bool:
        """删除环境变量"""
        result = self._request('DELETE', 'envs', data=env_ids)
        return result is not None
    
    def disable_env(self, env_ids: list) -> bool:
        """禁用环境变量"""
        result = self._request('PUT', 'envs/disable', data=env_ids)
        return result is not None
    
    def enable_env(self, env_ids: list) -> bool:
        """启用环境变量"""
        result = self._request('PUT', 'envs/enable', data=env_ids)
        return result is not None

# ==================== 账号数据管理函数 ====================
def get_user_accounts(user_id: str) -> list:
    """获取用户的账号备注列表"""
    uservalue = middleware.bucketGet(bucket='dd_kakan_user', key=user_id)
    if uservalue:
        try:
            return eval(uservalue)
        except:
            return []
    return []

def save_user_accounts(user_id: str, accounts: list):
    """保存用户账号列表"""
    if accounts:
        middleware.bucketSet(bucket='dd_kakan_user', key=user_id, value=str(accounts))
    else:
        middleware.bucketDel(bucket='dd_kakan_user', key=user_id)

def get_account_data(remark: str) -> dict:
    """获取账号数据"""
    data = middleware.bucketGet(bucket='dd_kakan_token', key=remark)
    if data:
        try:
            return json.loads(data)
        except:
            return None
    return None

def save_account_data(remark: str, value: dict):
    """保存账号数据"""
    middleware.bucketSet(bucket='dd_kakan_token', key=remark, value=json.dumps(value, ensure_ascii=False))

def delete_account_data(remark: str):
    """删除账号数据"""
    middleware.bucketDel(bucket='dd_kakan_token', key=remark)
    middleware.bucketDel(bucket='dd_kakan_auth', key=remark)

def get_account_auth(remark: str) -> str:
    """获取账号授权状态"""
    return middleware.bucketGet(bucket='dd_kakan_auth', key=remark) or '未授权'

def set_account_auth(remark: str, expire_date: str):
    """设置账号授权"""
    middleware.bucketSet(bucket='dd_kakan_auth', key=remark, value=expire_date)

def check_auth_status(expire_str: str):
    """检查授权状态（无宽限期）"""
    if expire_str in ['未授权', '授权过期']:
        return expire_str, False
    
    try:
        expire_date = datetime.datetime.strptime(expire_str, '%Y-%m-%d')
        today = datetime.datetime.now()
        
        if expire_date >= today:
            days_left = (expire_date - today).days
            return f"授权至{expire_str} (剩{days_left}天)", True
        else:
            return "授权过期", False
        
    except:
        return "未授权", False

def get_unique_remark(base_remark: str, user_id: str) -> str:
    """
    获取唯一的备注名
    如果备注已存在且属于其他用户，自动添加序号后缀
    """
    user_accounts = get_user_accounts(user_id)
    
    if base_remark not in user_accounts:
        existing_data = get_account_data(base_remark)
        if existing_data is None:
            return base_remark
    
    counter = 1
    while True:
        new_remark = f"{base_remark}_{counter}"
        if new_remark not in user_accounts:
            existing_data = get_account_data(new_remark)
            if existing_data is None:
                return new_remark
        counter += 1
        if counter > 100:
            return f"{base_remark}_{int(time.time())}"

# ==================== 青龙同步函数 ====================
def sync_to_qinglong(api: QingLongAPI, env_name: str, remark: str, account_data: dict, expire_date: str, user_id: str):
    """同步账号到青龙"""
    try:
        remarks = f"卡看:{remark}丨用户:{user_id}"
        if expire_date:
            remarks += f"丨到期:{expire_date}"
        remarks += "丨卡看管理"
        
        value = json.dumps(account_data, ensure_ascii=False)
        
        existing_env = api.find_env_by_remark(env_name, remark)
        
        if existing_env:
            env_id = existing_env.get('id')
            env_status = existing_env.get('status')
            
            success = api.update_env(env_id, env_name, value, remarks)
            
            if success and env_status != 0:
                api.enable_env([env_id])
                return {'success': True, 'action': '更新并启用'}
            
            return {'success': success, 'action': '更新'}
        else:
            success = api.add_env(env_name, value, remarks)
            return {'success': success, 'action': '添加'}
    
    except Exception as e:
        return {'success': False, 'message': str(e)}

def remove_from_qinglong(api: QingLongAPI, env_name: str, remark: str) -> bool:
    """从青龙删除账号"""
    try:
        existing_env = api.find_env_by_remark(env_name, remark)
        if existing_env:
            env_id = existing_env.get('id')
            return api.delete_env([env_id])
        return True
    except:
        return False

# ==================== 积分和支付函数 ====================
def get_user_coin(user_id: str, coin_bucket: str) -> int:
    """获取用户积分"""
    coin_str = middleware.bucketGet(bucket=coin_bucket, key=user_id) or '0'
    try:
        return int(coin_str)
    except:
        return 0

def deduct_user_coin(user_id: str, amount: int, coin_bucket: str) -> bool:
    """扣除用户积分"""
    current_coin = get_user_coin(user_id, coin_bucket)
    if current_coin < amount:
        return False
    
    new_coin = current_coin - amount
    middleware.bucketSet(bucket=coin_bucket, key=user_id, value=str(new_coin))
    return True

# ==================== 授权处理函数 ====================
def handle_authorize(remarks: list, api: QingLongAPI, env_name: str, coin_price: int,
                    money_price: Decimal, zsm: str, coin_bucket: str, wechat_enabled: bool):
    """处理授权（支持单条和批量）"""
    is_batch = len(remarks) > 1
    
    sender.reply(f"""====={'批量' if is_batch else ''}授权=====
📱 {'账号数量' if is_batch else '账号'}: {len(remarks)}个
------------------
📝 请输入授权天数
💡 示例: 30 (授权30天)
⚠️ 输入"q"退出
==================""")
    
    days_input = sender.input(120000, 5000, False)
    if not days_input or days_input.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    try:
        days = int(days_input)
        if days <= 0:
            sender.reply('❌ 天数必须大于0')
            return
    except:
        sender.reply('❌ 输入错误')
        return
    
    total_money = money_price * Decimal(days) * len(remarks)
    total_coin = coin_price * days * len(remarks)
    
    if wechat_enabled:
        pay_menu = f"""=====选择支付方式=====
📱 {'账号数量' if is_batch else '账号'}: {len(remarks)}个
⏰ 授权时长: {days}天
------------------
1️⃣ 微信支付
   💰 {total_money}元 {'(' + str(len(remarks)) + '个×' + str(days) + '天)' if is_batch else ''}

2️⃣ 积分支付
   🎯 {total_coin}积分 {'(' + str(len(remarks)) + '个×' + str(days) + '天)' if is_batch else ''}
   💫 当前积分: {get_user_coin(userid, coin_bucket)}

------------------
请选择支付方式（输入数字）
=================="""
        
        sender.reply(pay_menu)
        
        pay_choice = sender.input(60000, 5000, False)
        if not pay_choice:
            sender.reply('✅ 已取消操作')
            return
        
        payment_success = False
        
        if pay_choice == '1':
            sender.reply(f"""=====微信支付=====
💰 支付金额: {total_money}元
📱 {'账号数量' if is_batch else '账号'}: {len(remarks)}个
⏰ 授权时长: {days}天
------------------
请扫码支付后回复任意内容确认
==================""")
            sender.reply(f"[CQ:image,file={zsm}]")
            
            confirm = sender.input(300000, 5000, False)
            if confirm:
                payment_success = True
        
        elif pay_choice == '2':
            payment_success = handle_coin_payment(total_coin, coin_bucket, days, len(remarks), is_batch)
        
        else:
            sender.reply('❌ 无效选择')
            return
        
        if not payment_success:
            sender.reply('✅ 已取消支付')
            return
    
    else:
        payment_success = handle_coin_payment(total_coin, coin_bucket, days, len(remarks), is_batch)
        
        if not payment_success:
            return
    
    execute_authorization(remarks, api, env_name, days)

def handle_coin_payment(total_coin: int, coin_bucket: str, days: int, account_count: int, is_batch: bool) -> bool:
    """处理积分支付"""
    user_coin = get_user_coin(userid, coin_bucket)
    
    if user_coin < total_coin:
        sender.reply(f"""❌ 积分不足
------------------
当前积分: {user_coin}
需要积分: {total_coin}
==================""")
        return False
    
    sender.reply(f"""=====积分支付确认=====
💰 支付积分: {total_coin}
💫 当前积分: {user_coin}
💫 剩余积分: {user_coin - total_coin}
📱 账号数量: {account_count}个
⏰ 授权时长: {days}天
------------------
确认支付请回复【y】
取消请回复【n】
==================""")
    
    confirm = sender.input(60000, 5000, False)
    if not confirm or confirm.lower() != 'y':
        sender.reply('✅ 已取消支付')
        return False
    
    if deduct_user_coin(userid, total_coin, coin_bucket):
        new_coin = user_coin - total_coin
        sender.reply(f"""=====积分支付成功=====
✅ 已扣除积分: {total_coin}
💫 剩余积分: {new_coin}
==================""")
        return True
    else:
        sender.reply('❌ 积分扣除失败')
        return False

def execute_authorization(remarks: list, api: QingLongAPI, env_name: str, days: int):
    """执行授权"""
    is_batch = len(remarks) > 1
    
    if is_batch:
        sender.reply('🔄 正在批量授权...')
    
    success_count = 0
    fail_count = 0
    auth_results = []
    
    for remark in remarks:
        try:
            current_auth = get_account_auth(remark)
            expire_date = empower(current_auth, days)
            
            set_account_auth(remark, expire_date)
            
            account_data = get_account_data(remark)
            if account_data:
                result = sync_to_qinglong(api, env_name, remark, account_data, expire_date, userid)
                if result['success']:
                    existing_env = api.find_env_by_remark(env_name, remark)
                    if existing_env and existing_env.get('status') != 0:
                        api.enable_env([existing_env.get('id')])
                    success_count += 1
                    auth_results.append({"remark": remark, "expire": expire_date, "success": True})
                else:
                    fail_count += 1
                    auth_results.append({"remark": remark, "expire": expire_date, "success": False})
            else:
                fail_count += 1
                auth_results.append({"remark": remark, "expire": None, "success": False})
            
            time.sleep(0.3)
        
        except Exception as e:
            print(f"授权失败 {remark}: {e}")
            fail_count += 1
            auth_results.append({"remark": remark, "expire": None, "success": False})
    
    if is_batch:
        details = ""
        for result in auth_results:
            status = "✅" if result["success"] else "❌"
            expire_str = result["expire"] if result["expire"] else "失败"
            details += f"{status} {result['remark']}: {expire_str}\n"
        
        sender.reply(f"""=====批量授权完成=====
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
------------------
📋 账号详情:
{details}------------------
💡 已同步到青龙面板
==================""")
    else:
        if success_count > 0:
            sender.reply(f"""=====授权成功=====
✅ 账号: {remarks[0]}
📅 到期时间: {expire_date}
🎉 已同步到青龙面板
------------------
💡 青龙将自动执行任务
==================""")
        else:
            sender.reply("""❌ 授权失败
------------------
请稍后重试或联系管理员
==================""")

# ==================== 辅助函数 ====================
def parse_batch_selection(input_str: str, max_count: int) -> list:
    """
    解析批量选择输入
    支持格式: 1,3,5 或 1-5 或 0(全选)
    返回: 选中的索引列表(从0开始)
    """
    input_str = input_str.strip()
    
    if input_str == '0':
        return list(range(max_count))
    
    indices = set()
    
    if '-' in input_str and ',' not in input_str:
        try:
            parts = input_str.split('-')
            if len(parts) == 2:
                start = int(parts[0].strip())
                end = int(parts[1].strip())
                for i in range(start, end + 1):
                    if 1 <= i <= max_count:
                        indices.add(i - 1)
        except:
            pass
    else:
        try:
            for item in input_str.replace('，', ',').split(','):
                item = item.strip()
                if '-' in item:
                    parts = item.split('-')
                    if len(parts) == 2:
                        start = int(parts[0].strip())
                        end = int(parts[1].strip())
                        for i in range(start, end + 1):
                            if 1 <= i <= max_count:
                                indices.add(i - 1)
                elif item:
                    idx = int(item)
                    if 1 <= idx <= max_count:
                        indices.add(idx - 1)
        except:
            pass
    
    return sorted(list(indices))

# ==================== 命令处理函数 ====================
def cmd_help():
    """显示帮助教程"""
    QLurl, ClientID, ClientSecret, env_name, coin_price, money_price, zsm, coin_bucket, admin_ids, wechat_enabled, proxy_url = get_plugin_config()
    
    help_msg = """=====卡看教程=====
📱 用户指令:
• 卡看登录 - 短信验证码登录
• 卡看管理 - 管理授权
• 卡看查询 - 实时查询
• 卡看刷进度 - 攒钱罐提现（刷进度）
• 卡看教程 - 查看教程
------------------"""
    
    if userid in admin_ids:
        help_msg += """
🔧 管理员指令:
• 卡看管理 - 包含管理员面板
------------------"""
    
    help_msg += """
💡 登录方式（短信验证码）:
📝 格式: 手机号
📝 示例: 13800138000
(自动使用脱敏手机号作为备注)

⚠️ 建议私聊登录，保护账号安全
------------------
💰 功能说明:
• 账号管理和批量登录
• 授权管理（积分/微信支付）
• 实时查询账号状态和金币
• 自动同步账号到青龙面板
• 任务在青龙中执行，插件只负责账号管理
------------------
🎯 使用流程:
1. 发送"卡看登录"绑定账号
2. 发送"卡看管理"进行授权
3. 青龙自动执行任务
4. 发送"卡看查询"实时查看账号信息
------------------
🎯 授权说明:
• 授权价格: """ + str(coin_price) + """积分/天"""
    
    if wechat_enabled:
        help_msg += "\n• 微信支付: " + str(money_price) + "元/天"
    
    help_msg += """
------------------
⏰ 过期说明:
• 授权到期后需续费才能使用
• 到期后青龙任务立即停止
• 建议提前续费，避免服务中断
=================="""
    sender.reply(help_msg)

def mask_phone(phone: str) -> str:
    """手机号脱敏处理"""
    if len(phone) == 11:
        return f"{phone[:3]}****{phone[7:]}"
    return phone[:3] + "****" + phone[-4:] if len(phone) > 7 else phone

def cmd_login():
    """登录账号（短信验证码方式）"""
    sender.reply("""=====卡看登录=====

请输入手机号
示例: 13800138000
(将发送短信验证码)

💡 批量输入 (每行一个):
13800138000
13800138001

⚠️ 建议私聊登录，保护账号安全
⭐ 输入q退出操作
==================""")
    
    try:
        user_input = sender.input(180000, 1000, False)
    except Exception as e:
        print(f"[错误] input()调用失败: {str(e)}")
        user_input = sender.listen(180000)
    
    if not user_input:
        sender.reply('⏰ 输入超时!')
        return
    
    if user_input.lower() == 'q':
        sender.reply('✅ 已取消登录')
        return
    
    lines = [line.strip() for line in user_input.strip().split('\n') if line.strip()]
    
    if not lines:
        sender.reply("""❌ 未检测到有效手机号
------------------
请输入11位手机号
==================""")
        return
    
    time.sleep(0.5)
    for _ in range(min(len(lines) + 2, 10)):
        try:
            sender.recallMessage(1)
            time.sleep(0.1)
        except:
            break
    
    QLurl, ClientID, ClientSecret, env_name, coin_price, money_price, zsm, coin_bucket, admin_ids, wechat_enabled, proxy_url = get_plugin_config()
    
    success_list = []
    fail_list = []
    sms_pending = []
    
    for line in lines:
        phone = line.split("#", 1)[0].strip()
        if len(phone) == 11 and phone.startswith('1'):
            remark = mask_phone(phone)
            sms_pending.append({"remark": remark, "phone": phone, "display_name": remark})
        else:
            fail_list.append({"name": line[:11], "reason": "手机号格式错误"})
    
    if sms_pending:
        sender.reply(f"""检测到 {len(sms_pending)} 个手机号登录
将逐个发送验证码，请耐心等待...
==================""")
        
        kakan_api = KaKanAPI()
        
        for item in sms_pending:
            remark = item['remark']
            phone = item['phone']
            display_name = item.get('display_name', remark)
            
            device_info = DeviceManager.generate_device_info(phone=phone)
            
            sender.reply(f"📱 {display_name}: 正在发送验证码到 {mask_phone(phone)}...")
            
            success, result, interval = kakan_api.send_sms_code(phone, device_info)
            
            if success:
                sender.reply(f"""=====验证码已发送=====
📱 账号: {display_name}
📱 手机: {mask_phone(phone)}
⏰ 剩余次数: {result}
------------------
请在60秒内输入验证码
💡 直接输入验证码
⚠️ 输入q跳过此账号
==================""")
                
                try:
                    code_input = sender.input(60000, 5000, False)
                except:
                    code_input = None
                
                if not code_input or code_input.lower() == 'q':
                    fail_list.append({"name": display_name, "reason": "用户取消"})
                    continue
                
                code_parts = code_input.split('#', 1)
                if len(code_parts) == 2:
                    code = code_parts[1].strip()
                else:
                    code = code_input.strip()
                
                if not code or len(code) < 4:
                    fail_list.append({"name": display_name, "reason": "验证码格式错误"})
                    continue
                
                success, user_info = kakan_api.login_by_phone(phone, code, device_info)
                
                if success and user_info:
                    device_info['usr'] = user_info.get('user_id', device_info.get('usr', ''))
                    if 'zyeid' in user_info:
                        device_info['zyeid'] = user_info['zyeid']
                    
                    final_remark = get_unique_remark(remark, userid)
                    if final_remark != remark:
                        display_name = f"{final_remark} (原:{remark})"
                    remark = final_remark
                    
                    account_data = {
                        'user_id': user_info.get('user_id'),
                        'encrypt_user_id': user_info.get('encrypt_user_id'),
                        'session_id': user_info.get('session_id'),
                        'device_info': device_info,
                        'wechat_id': '',
                        'name': user_info.get('name', ''),
                        'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'login_type': 'sms'
                    }
                    
                    save_account_data(remark, account_data)
                    set_account_auth(remark, '未授权')
                    
                    user_accounts = get_user_accounts(userid)
                    if remark not in user_accounts:
                        user_accounts.append(remark)
                        save_user_accounts(userid, user_accounts)
                    
                    success_list.append({"name": display_name, "type": "短信登录", "user_id": user_info.get('user_id', '')[:8] + '...'})
                else:
                    error = user_info.get('error', '未知错误') if user_info else '登录失败'
                    fail_list.append({"name": display_name, "reason": error})
            else:
                fail_list.append({"name": display_name, "reason": f"发送验证码失败: {result}"})
    
    is_batch = len(lines) > 1
    msg = f"=====登录结果=====\n"
    msg += f"{'批量' if is_batch else ''}处理: {len(lines)}个账号\n"
    msg += f"✅ 成功: {len(success_list)}个\n"
    msg += f"❌ 失败: {len(fail_list)}个\n"
    msg += "==================\n\n"
    
    if success_list:
        msg += "✅ 成功账号:\n"
        for s in success_list:
            msg += f"• {s['name']} ({s['type']}) - {s['user_id']}\n"
        msg += "\n"
    
    if fail_list:
        msg += "❌ 失败账号:\n"
        for f in fail_list[:5]:
            msg += f"• {f['name']}: {f['reason']}\n"
        msg += "\n"
    
    msg += "🔒 已撤回您的隐私信息"
    
    sender.reply(msg)
    
    if success_list:
        sender.reply("""
是否立即进行授权？
[y] 立即授权
[n] 稍后授权
==================""")
        
        choice = sender.input(60000, 5000, False)
        if choice and choice.lower() == 'y':
            cmd_manage()
        else:
            sender.reply('✅ 已保存账号，稍后可发送"卡看管理"进行授权')

def cmd_manage():
    """管理账号"""
    user_accounts = get_user_accounts(userid)
    
    if not user_accounts:
        sender.reply("""📭 暂无绑定账号

💡 请先发送"卡看登录"绑定账号""")
        return
    
    QLurl, ClientID, ClientSecret, env_name, coin_price, money_price, zsm, coin_bucket, admin_ids, wechat_enabled, proxy_url = get_plugin_config()
    
    is_admin_user = userid in admin_ids
    
    message = '------------------\n功能选项:\n00、一键授权所有账号\n01、批量选择授权\n02、批量删除账号\n'
    if is_admin_user:
        message += '03、管理员面板\n'
    message += '==================\n'
    
    count = 1
    for remark in user_accounts:
        auth_status = get_account_auth(remark)
        status_display, is_valid = check_auth_status(auth_status)
        
        message += f"""[{count}] {remark}
    到期: {status_display}
"""
        count += 1
    
    sender.reply(f"""=====卡看管理=====
{message}------------------
📝 选择账号: 输入序号（多选用英文逗号分隔）
💡 示例: 1 或 1,3 或 1-3
⚠️ 输入"q"退出操作
==================""")
    
    choice = sender.input(120000, 5000, False)
    if not choice or choice.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    api = QingLongAPI(QLurl, ClientID, ClientSecret)
    
    if choice == '00':
        handle_authorize(user_accounts, api, env_name, coin_price, money_price, zsm, coin_bucket, wechat_enabled)
    elif choice == '01':
        handle_batch_select_authorize(user_accounts, api, env_name, coin_price, money_price, zsm, coin_bucket, wechat_enabled)
    elif choice == '02':
        handle_batch_delete(user_accounts, api, env_name)
    elif choice == '03' and is_admin_user:
        admin_panel(api, env_name, coin_price, money_price, zsm, coin_bucket, admin_ids, wechat_enabled)
    else:
        indices = parse_batch_selection(choice, len(user_accounts))
        if indices:
            if len(indices) == 1:
                handle_single_account(user_accounts[indices[0]], api, env_name, coin_price, money_price, zsm, coin_bucket, wechat_enabled)
            else:
                selected = [user_accounts[i] for i in indices]
                handle_authorize(selected, api, env_name, coin_price, money_price, zsm, coin_bucket, wechat_enabled)
        else:
            sender.reply('❌ 输入错误，请检查序号是否正确')

def handle_batch_select_authorize(user_accounts: list, api: QingLongAPI, env_name: str, 
                                   coin_price: int, money_price: Decimal, zsm: str, 
                                   coin_bucket: str, wechat_enabled: bool):
    """批量选择账号授权"""
    message = ""
    for idx, remark in enumerate(user_accounts, 1):
        auth_status = get_account_auth(remark)
        status_display, is_valid = check_auth_status(auth_status)
        status_icon = "✅" if is_valid else "❌"
        message += f"{idx}. {remark} {status_icon} {status_display}\n"
    
    sender.reply(f"""=====批量选择授权=====
{message}------------------
📝 请选择要授权的账号
💡 多选用英文逗号分隔: 1,3,5
💡 连续选择: 1-3
💡 输入"0"全选
⚠️ 输入"q"退出
==================""")
    
    choice = sender.input(120000, 5000, False)
    if not choice or choice.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    indices = parse_batch_selection(choice, len(user_accounts))
    
    if not indices:
        sender.reply('❌ 输入错误，请检查序号是否正确')
        return
    
    selected = [user_accounts[i] for i in indices]
    
    sender.reply(f"""=====已选择账号=====
📱 数量: {len(selected)}个
📋 账号: {', '.join(selected)}
------------------
确认选择请回复【y】
重新选择请回复【n】
==================""")
    
    confirm = sender.input(60000, 5000, False)
    if confirm and confirm.lower() == 'y':
        handle_authorize(selected, api, env_name, coin_price, money_price, zsm, coin_bucket, wechat_enabled)
    else:
        sender.reply('✅ 已取消操作')

def handle_single_account(remark: str, api: QingLongAPI, env_name: str, coin_price: int,
                          money_price: Decimal, zsm: str, coin_bucket: str, wechat_enabled: bool):
    """处理单个账号"""
    auth_status = get_account_auth(remark)
    status_display, is_valid = check_auth_status(auth_status)
    
    account_data = get_account_data(remark)
    login_type = account_data.get('login_type', '未知') if account_data else '未知'
    
    sender.reply(f"""=====账号详情=====
📱 备注: {remark}
🔐 授权: {status_display}
📝 登录方式: {login_type}
------------------
[1] 📅 授权账号
[2] 🔄 更新账号
[3] ❌ 删除账号

请选择操作序号
==================""")
    
    op_choice = sender.input(120000, 5000, False)
    if not op_choice or op_choice.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    if op_choice == '1':
        handle_authorize([remark], api, env_name, coin_price, money_price, zsm, coin_bucket, wechat_enabled)
    elif op_choice == '2':
        handle_update_account(remark, api, env_name)
    elif op_choice == '3':
        sender.reply("""=====删除确认=====
⚠️ 是否删除该账号?
------------------
[y] 确认删除
[n] 取消操作
==================""")
        
        confirm = sender.input(60000, 5000, False)
        if confirm and confirm.lower() == 'y':
            remove_from_qinglong(api, env_name, remark)
            delete_account_data(remark)
            
            user_accounts = get_user_accounts(userid)
            if remark in user_accounts:
                user_accounts.remove(remark)
                save_user_accounts(userid, user_accounts)
            
            sender.reply('✅ 账号已删除')
        else:
            sender.reply('✅ 已取消删除')

def handle_update_account(remark: str, api: QingLongAPI, env_name: str):
    """处理账号更新"""
    sender.reply(f"""=====更新账号=====
📱 账号备注: {remark}
------------------
请输入手机号:
示例: 13800138000
(将发送验证码)

⚠️ 输入"q"退出操作
⚠️ 建议私聊更新，保护账号安全
==================""")
    
    try:
        user_input = sender.input(120000, 1000, False)
    except Exception as e:
        print(f"[错误] input()调用失败: {str(e)}")
        user_input = sender.listen(120000)
    
    if not user_input:
        sender.reply('⏰ 输入超时!')
        return
    
    if user_input.lower() == 'q':
        sender.reply('✅ 已取消更新')
        return
    
    data = user_input.strip()
    
    time.sleep(0.5)
    for _ in range(3):
        try:
            sender.recallMessage(1)
            time.sleep(0.1)
        except:
            break
    
    if len(data) != 11 or not data.startswith('1'):
        sender.reply('❌ 手机号格式错误')
        return
    
    kakan_api = KaKanAPI()
    device_info = DeviceManager.generate_device_info(phone=data)
    
    sender.reply(f"📱 正在发送验证码到 {data}...")
    
    success, result, interval = kakan_api.send_sms_code(data, device_info)
    
    if success:
        sender.reply(f"""=====验证码已发送=====
📱 手机: {data}
⏰ 剩余次数: {result}
------------------
请在60秒内输入验证码
⚠️ 输入q取消操作
==================""")
        
        try:
            code_input = sender.input(60000, 5000, False)
        except:
            code_input = None
        
        if not code_input or code_input.lower() == 'q':
            sender.reply('✅ 已取消更新')
            return
        
        code = code_input.strip()
        
        if not code or len(code) < 4:
            sender.reply('❌ 验证码格式错误')
            return
        
        success, user_info = kakan_api.login_by_phone(data, code, device_info)
        
        if success and user_info:
            device_info['usr'] = user_info.get('user_id', device_info.get('usr', ''))
            if 'zyeid' in user_info:
                device_info['zyeid'] = user_info['zyeid']
            
            new_account_data = {
                'user_id': user_info.get('user_id'),
                'encrypt_user_id': user_info.get('encrypt_user_id'),
                'session_id': user_info.get('session_id'),
                'device_info': device_info,
                'wechat_id': '',
                'name': user_info.get('name', ''),
                'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'login_type': 'sms'
            }
            
            save_account_data(remark, new_account_data)
            
            auth_status = get_account_auth(remark)
            sync_success = True
            
            if auth_status not in ['未授权', '授权过期']:
                auth_status_checked, is_valid = check_auth_status(auth_status)
                if is_valid:
                    result = sync_to_qinglong(api, env_name, remark, new_account_data, auth_status, userid)
                    sync_success = result.get('success', False)
            
            if sync_success:
                sender.reply(f"""=====更新成功=====
✅ 账号信息已更新
📱 备注: {remark}
👤 用户: {user_info.get('name', '未知')}
------------------
🔒 已撤回您的隐私信息
==================""")
            else:
                sender.reply("""❌ 更新失败
------------------
本地数据已更新，但同步青龙失败
请稍后重试或联系管理员
==================""")
        else:
            error = user_info.get('error', '未知错误') if user_info else '登录失败'
            sender.reply(f'❌ 登录失败: {error}')
    else:
        sender.reply(f'❌ 发送验证码失败: {result}')

def handle_batch_delete(accounts: list, api: QingLongAPI, env_name: str):
    """批量删除账号"""
    message = ""
    for idx, remark in enumerate(accounts, 1):
        auth_status = get_account_auth(remark)
        status_display, is_valid = check_auth_status(auth_status)
        status_icon = "✅" if is_valid else "❌"
        message += f"{idx}. {remark} {status_icon} {status_display}\n"
    
    sender.reply(f"""=====批量删除账号=====
📱 共 {len(accounts)} 个账号
------------------
{message}------------------
📝 请选择要删除的账号
💡 多选用英文逗号分隔: 1,3,5
💡 连续选择: 1-3
💡 输入"0"全选
⚠️ 输入"q"退出
==================""")
    
    choice = sender.input(120000, 5000, False)
    if not choice or choice.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    indices = parse_batch_selection(choice, len(accounts))
    
    if not indices:
        sender.reply('❌ 输入错误，请检查序号是否正确')
        return
    
    selected = [accounts[i] for i in indices]
    
    sender.reply(f"""=====删除确认=====
⚠️ 危险操作警告！
------------------
📱 将删除 {len(selected)} 个账号:
{chr(10).join([f'• {remark}' for remark in selected])}
------------------
此操作将：
1. 删除青龙面板中的环境变量
2. 清除本地账号数据
3. 清除授权信息

⚠️ 此操作不可恢复！
------------------
确认删除请回复【y】
取消请回复【n】
==================""")
    
    confirm = sender.input(60000, 5000, False)
    if confirm and confirm.lower() == 'y':
        sender.reply('🔄 正在批量删除...')
        
        success_count = 0
        for remark in selected:
            try:
                remove_from_qinglong(api, env_name, remark)
                delete_account_data(remark)
                success_count += 1
            except:
                pass
        
        remaining_accounts = [a for a in accounts if a not in selected]
        save_user_accounts(userid, remaining_accounts)
        
        if remaining_accounts:
            sender.reply(f"""=====删除完成=====
✅ 成功删除: {success_count}/{len(selected)}个
------------------
📱 剩余账号: {len(remaining_accounts)}个
💡 可发送"卡看管理"继续管理
==================""")
        else:
            sender.reply(f"""=====删除完成=====
✅ 成功删除: {success_count}/{len(selected)}个
------------------
📭 您的所有账号已清空
💡 可发送"卡看登录"重新添加
==================""")
    else:
        sender.reply('✅ 已取消删除')

def admin_panel(api: QingLongAPI, env_name: str, coin_price: int, money_price: Decimal, 
                zsm: str, coin_bucket: str, admin_ids: list, wechat_enabled: bool):
    """管理员面板"""
    sender.reply("""=====卡看管理后台=====
👑 管理员模式

请选择操作:

00、批量授权 - 给所有用户批量开通/续费
01、指定用户授权 - 为指定用户的账号授权
02、账号检测 - 检测所有账号状态
03、数据清理 - 清理过期30天账号
04、青龙同步 - 手动同步至青龙面板

发送 q 退出
==================""")
    
    choice = sender.input(60000, 5000, False)
    if not choice or choice.lower() == 'q':
        return
    
    if choice == '00':
        admin_batch_authorize_all(api, env_name)
    elif choice == '01':
        admin_authorize_specific_user(api, env_name, coin_price, money_price, zsm, coin_bucket, wechat_enabled)
    elif choice == '02':
        admin_check_all()
    elif choice == '03':
        admin_cleanup(api, env_name)
    elif choice == '04':
        admin_sync_all(api, env_name)
    else:
        sender.reply('❌ 无效选择')

def admin_authorize_specific_user(api: QingLongAPI, env_name: str, coin_price: int, 
                                   money_price: Decimal, zsm: str, coin_bucket: str, wechat_enabled: bool):
    """管理员为指定用户授权"""
    sender.reply("""=====指定用户授权=====
📝 请输入用户ID
💡 示例: 12345678 或 wx_abc123
⚠️ 输入q退出
==================""")
    
    target_user_id = sender.input(120000, 5000, False)
    if not target_user_id or target_user_id.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    target_user_id = target_user_id.strip()
    
    user_accounts_str = middleware.bucketGet('dd_kakan_user', target_user_id)
    if not user_accounts_str:
        sender.reply(f"""❌ 未找到该用户的账号
------------------
用户ID: {target_user_id}
💡 请确认用户ID是否正确
==================""")
        return
    
    try:
        user_accounts = eval(user_accounts_str)
    except:
        sender.reply('❌ 用户数据解析失败')
        return
    
    if not user_accounts:
        sender.reply('❌ 该用户暂无绑定账号')
        return
    
    message = ""
    for idx, remark in enumerate(user_accounts, 1):
        auth_status = get_account_auth(remark)
        status_display, is_valid = check_auth_status(auth_status)
        status_icon = "✅" if is_valid else "❌"
        message += f"{idx}. {remark} {status_icon} {status_display}\n"
    
    sender.reply(f"""=====用户账号列表=====
用户ID: {target_user_id}
------------------
{message}------------------
📱 该用户共 {len(user_accounts)} 个账号

📝 请选择要授权的账号
💡 多选用英文逗号分隔: 1,3,5
💡 连续选择: 1-3
💡 输入"0"全选
⚠️ 输入q退出
==================""")
    
    choice = sender.input(120000, 5000, False)
    if not choice or choice.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    indices = parse_batch_selection(choice, len(user_accounts))
    
    if not indices:
        sender.reply('❌ 输入错误，请检查序号是否正确')
        return
    
    selected = [user_accounts[i] for i in indices]
    
    sender.reply(f"""=====已选择账号=====
📱 用户ID: {target_user_id}
📱 账号数量: {len(selected)}个
📋 账号: {', '.join(selected)}
------------------
📝 请输入授权天数
💡 示例: 30
⚠️ 输入q退出
==================""")
    
    days_input = sender.input(120000, 5000, False)
    if not days_input or days_input.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    try:
        days = int(days_input)
        if days <= 0:
            sender.reply('❌ 天数必须大于0')
            return
    except:
        sender.reply('❌ 输入错误，请输入数字')
        return
    
    total_money = money_price * Decimal(days) * len(selected)
    total_coin = coin_price * days * len(selected)
    
    if wechat_enabled:
        sender.reply(f"""=====支付确认=====
📱 用户ID: {target_user_id}
📱 账号数量: {len(selected)}个
⏰ 授权时长: {days}天
------------------
💰 微信支付: {total_money}元
🎯 积分支付: {total_coin}积分
💫 当前积分: {get_user_coin(userid, coin_bucket)}
------------------
1️⃣ 微信支付
2️⃣ 积分支付
⚠️ 输入q退出
==================""")
        
        pay_choice = sender.input(60000, 5000, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply('✅ 已取消操作')
            return
        
        payment_success = False
        
        if pay_choice == '1':
            sender.reply(f"""=====微信支付=====
💰 支付金额: {total_money}元
📱 账号数量: {len(selected)}个
⏰ 授权时长: {days}天
------------------
请扫码支付后回复任意内容确认
==================""")
            sender.reply(f"[CQ:image,file={zsm}]")
            
            confirm = sender.input(300000, 5000, False)
            if confirm:
                payment_success = True
        
        elif pay_choice == '2':
            payment_success = handle_coin_payment(total_coin, coin_bucket, days, len(selected), True)
        
        else:
            sender.reply('❌ 无效选择')
            return
        
        if not payment_success:
            sender.reply('✅ 已取消支付')
            return
    else:
        payment_success = handle_coin_payment(total_coin, coin_bucket, days, len(selected), True)
        if not payment_success:
            return
    
    sender.reply('🔄 正在授权...')
    success_count = 0
    fail_count = 0
    
    for remark in selected:
        try:
            current_auth = get_account_auth(remark)
            expire_date = empower(current_auth, days)
            
            set_account_auth(remark, expire_date)
            
            account_data = get_account_data(remark)
            if account_data:
                result = sync_to_qinglong(api, env_name, remark, account_data, expire_date, target_user_id)
                if result['success']:
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1
            
            time.sleep(0.3)
        except Exception as e:
            print(f"授权失败 {remark}: {e}")
            fail_count += 1
    
    sender.reply(f"""=====授权完成=====
📱 用户ID: {target_user_id}
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
⏰ 授权: {days}天
------------------
💡 已同步到青龙面板
==================""")

def admin_batch_authorize_all(api: QingLongAPI, env_name: str):
    """管理员批量授权所有用户"""
    users = middleware.bucketAllKeys('dd_kakan_user')
    if not users:
        sender.reply('❌ 未找到任何绑定的卡看账号')
        return
    
    total_accounts = 0
    for u in users:
        uservalue = middleware.bucketGet('dd_kakan_user', u)
        if uservalue:
            try:
                total_accounts += len(eval(uservalue))
            except:
                pass
    
    sender.reply(f"""=====批量授权所有用户=====
👥 用户数: {len(users)}个
📱 账号数: {total_accounts}个
------------------
请输入授权月数
回复"q"退出操作
==================""")
    
    months_input = sender.input(60000, 5000, False)
    if not months_input or months_input.lower() == 'q':
        sender.reply('✅ 已取消授权')
        return
    
    try:
        months = int(months_input)
        if months <= 0:
            sender.reply('❌ 月数必须大于0')
            return
    except:
        sender.reply('❌ 月数必须是数字!')
        return
    
    sender.reply('🔄 正在授权...')
    success_count = 0
    fail_count = 0
    
    for user in users:
        accountlist = middleware.bucketGet('dd_kakan_user', user)
        if not accountlist:
            continue
        try:
            accounts = eval(accountlist)
            for remark in accounts:
                try:
                    current_auth = get_account_auth(remark)
                    new_auth = empower(current_auth, months)
                    set_account_auth(remark, new_auth)
                    
                    account_data = get_account_data(remark)
                    if account_data:
                        sync_to_qinglong(api, env_name, remark, account_data, new_auth, user)
                    success_count += 1
                except:
                    fail_count += 1
        except:
            fail_count += 1
    
    sender.reply(f"""=====授权完成=====
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
⏰ 授权: {months}月
==================""")

def admin_check_all():
    """管理员检测所有账号"""
    users = middleware.bucketAllKeys('dd_kakan_user')
    if not users:
        sender.reply('❌ 未找到任何绑定的卡看账号')
        return
    
    sender.reply('🔍 正在检测所有账号...')
    normal_count = 0
    expired_count = 0
    unauthorized_count = 0
    today = datetime.datetime.now()
    
    for user in users:
        accountlist = middleware.bucketGet('dd_kakan_user', user)
        if not accountlist:
            continue
        try:
            accounts = eval(accountlist)
            for remark in accounts:
                auth_status = get_account_auth(remark) or '未授权'
                if auth_status == '未授权':
                    unauthorized_count += 1
                elif auth_status == '授权过期':
                    expired_count += 1
                else:
                    try:
                        expire_date = datetime.datetime.strptime(auth_status, '%Y-%m-%d')
                        if expire_date < today:
                            expired_count += 1
                        else:
                            normal_count += 1
                    except:
                        unauthorized_count += 1
        except:
            pass
    
    sender.reply(f"""=====检测结果汇总=====
✅ 正常: {normal_count}个
⏰ 过期: {expired_count}个
🔒 未授权: {unauthorized_count}个
==================""")

def admin_cleanup(api: QingLongAPI, env_name: str):
    """管理员清理过期账号"""
    users = middleware.bucketAllKeys('dd_kakan_user')
    if not users:
        sender.reply('❌ 未找到任何用户数据')
        return
    
    sender.reply('🔍 正在扫描过期账号...')
    expired_list = []
    today = datetime.datetime.now()
    
    for user in users:
        accountlist = middleware.bucketGet('dd_kakan_user', user)
        if not accountlist:
            continue
        try:
            accounts = eval(accountlist)
            for remark in accounts:
                auth_status = get_account_auth(remark) or '未授权'
                if auth_status not in ['未授权', '授权过期']:
                    try:
                        expire_date = datetime.datetime.strptime(auth_status, '%Y-%m-%d')
                        if (today - expire_date).days > 30:
                            expired_list.append({'user': user, 'remark': remark})
                    except:
                        pass
        except:
            pass
    
    if not expired_list:
        sender.reply('✅ 没有需要清理的过期账号')
        return
    
    sender.reply(f"""=====清理确认=====
⚠️ 发现 {len(expired_list)} 个过期超过30天的账号
此操作将删除青龙环境变量和本地数据

确认清理请回复【y】
取消请回复【n】
==================""")
    
    confirm = sender.input(30000, 5000, False)
    if confirm and confirm.lower() == 'y':
        sender.reply('🔄 正在清理...')
        success_count = 0
        
        for item in expired_list:
            try:
                existing_env = api.find_env_by_remark(env_name, item['remark'])
                if existing_env:
                    api.delete_env([existing_env.get('id')])
                
                delete_account_data(item['remark'])
                
                accountlist = middleware.bucketGet('dd_kakan_user', item['user'])
                if accountlist:
                    accounts = eval(accountlist)
                    if item['remark'] in accounts:
                        accounts.remove(item['remark'])
                        if accounts:
                            middleware.bucketSet('dd_kakan_user', item['user'], str(accounts))
                        else:
                            middleware.bucketDel('dd_kakan_user', item['user'])
                success_count += 1
            except:
                pass
        
        sender.reply(f"""=====清理完成=====
✅ 成功清理: {success_count}/{len(expired_list)}
==================""")
    else:
        sender.reply('✅ 已取消清理')

def admin_sync_all(api: QingLongAPI, env_name: str):
    """管理员同步所有账号到青龙"""
    sender.reply('🔄 正在同步账号到青龙面板...')
    
    users = middleware.bucketAllKeys('dd_kakan_user')
    if not users:
        sender.reply('❌ 未找到任何绑定的卡看账号')
        return
    
    total_count = 0
    success_count = 0
    fail_count = 0
    
    for user in users:
        accountlist = middleware.bucketGet('dd_kakan_user', user)
        if not accountlist:
            continue
        
        try:
            accounts = eval(accountlist)
            for remark in accounts:
                total_count += 1
                
                account_data = get_account_data(remark)
                if not account_data:
                    fail_count += 1
                    continue
                
                auth_status = get_account_auth(remark) or '未授权'
                
                try:
                    result = sync_to_qinglong(api, env_name, remark, account_data, auth_status, user)
                    if result.get('success'):
                        success_count += 1
                    else:
                        fail_count += 1
                except:
                    fail_count += 1
        except:
            pass
    
    sender.reply(f"""=====同步完成=====
📊 总计: {total_count}个账号
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
------------------
💡 提示：
• 成功同步的账号已更新到青龙
• 失败的账号请检查账号数据
==================""")

def cmd_query():
    """实时查询账号信息"""
    user_accounts = get_user_accounts(userid)
    
    if not user_accounts:
        sender.reply("""📭 暂无绑定账号

💡 请先发送"卡看登录"绑定账号""")
        return
    
    QLurl, ClientID, ClientSecret, env_name, coin_price, money_price, zsm, coin_bucket, admin_ids, wechat_enabled, proxy_url = get_plugin_config()
    
    api = QingLongAPI(QLurl, ClientID, ClientSecret)
    
    proxy, proxy_info = get_proxy(proxy_url)
    
    if len(user_accounts) > 1:
        message = ""
        for idx, remark in enumerate(user_accounts, 1):
            auth_status = get_account_auth(remark)
            status_display, is_valid = check_auth_status(auth_status)
            status_icon = "✅" if is_valid else "❌"
            message += f"{idx}. {remark} {status_icon}\n"
        
        sender.reply(f"""=====卡看查询=====
📱 共 {len(user_accounts)} 个账号
------------------
{message}------------------
📝 请选择要查询的账号
💡 多选用英文逗号分隔: 1,3,5
💡 连续选择: 1-3
💡 输入"0"查询全部
⚠️ 输入"q"退出
==================""")
        
        choice = sender.input(120000, 5000, False)
        if not choice or choice.lower() == 'q':
            sender.reply('✅ 已取消操作')
            return
        
        indices = parse_batch_selection(choice, len(user_accounts))
        
        if not indices:
            sender.reply('❌ 输入错误，请检查序号是否正确')
            return
        
        selected = [user_accounts[i] for i in indices]
    else:
        selected = user_accounts
    
    sender.reply(f"🔍 正在查询 {len(selected)} 个账号...\n请稍候...")
    results = []
    
    kakan_api = KaKanAPI()
    
    for remark in selected:
        account_data = get_account_data(remark)
        if not account_data:
            results.append(f"❌ {remark}: 账号数据丢失")
            continue
        
        device_info = account_data.get('device_info', {})
        session_info = {
            'user_id': account_data.get('user_id'),
            'encrypt_user_id': account_data.get('encrypt_user_id'),
            'session_id': account_data.get('session_id')
        }
        
        auth_status = get_account_auth(remark)
        status_display, is_valid = check_auth_status(auth_status)
        
        if not is_valid:
            results.append(f"""❌ {remark}: 授权已过期
🔐 {status_display}
💡 请发送"卡看管理"进行续费
   价格: {coin_price}积分/天
------------------
续费后将自动恢复：
• 查询功能
• 青龙自动任务""")
            continue
        
        success, user_info = kakan_api.get_user_info(device_info, session_info, proxy=proxy)
        
        if not success:
            results.append(f"❌ {remark}: Token已失效")
            continue
        
        success, gold_info = kakan_api.get_gold_account(device_info, session_info, proxy=proxy)
        
        info = f"📱 {remark}\n"
        
        expire_str = get_account_auth(remark)
        try:
            expire_date = datetime.datetime.strptime(expire_str, '%Y-%m-%d')
            days_left = (expire_date - datetime.datetime.now()).days
            info += f"🔐 授权至{expire_str} (剩{days_left}天)\n"
        except:
            info += f"🔐 {status_display}\n"
        
        if user_info:
            total_coin = user_info.get('total_coin', 0)
            total_cash = user_info.get('total_cash', 0)
            info += f"💰 金币: {format_number(total_coin)}\n"
            info += f"💵 余额: {total_cash}元\n"
        
        if gold_info:
            total_gold = gold_info.get('total_gold_num', 0)
            total_rmb = gold_info.get('total_rmb', '0')
            info += f"🎯 金币账户: {format_number(total_gold)} (约{total_rmb}元)\n"
        
        results.append(info)
    
    query_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    final_msg = f"=====查询结果=====\n{chr(10).join(results)}------------------\n🌐 代理: {proxy_info}\n⏰ 查询时间: {query_time}\n=================="
    sender.reply(final_msg)

# ==================== 刷进度任务 ====================
def execute_single_account_progress(kakan_api, remark, count, proxy):
    """执行单个账号的刷进度任务（攒钱罐提现）"""
    account_data = get_account_data(remark)
    if not account_data:
        return {'remark': remark, 'success': False, 'msg': '账号数据丢失'}
    
    device_info = account_data.get('device_info', {})
    session_info = {
        'user_id': account_data.get('user_id'),
        'encrypt_user_id': account_data.get('encrypt_user_id'),
        'session_id': account_data.get('session_id')
    }
    
    if not device_info:
        return {'remark': remark, 'success': False, 'msg': '设备信息丢失'}
    
    if not session_info.get('user_id') or not session_info.get('session_id'):
        return {'remark': remark, 'success': False, 'msg': '会话信息丢失'}
    
    auth_status = get_account_auth(remark)
    _, is_valid = check_auth_status(auth_status)
    if not is_valid:
        return {'remark': remark, 'success': False, 'msg': '授权已过期'}
    
    success_count = 0
    fail_count = 0
    last_error = None
    
    print(f"[{remark}] 开始执行攒钱罐提现任务，计划执行 {count} 次")
    
    for i in range(count):
        try:
            success, result = kakan_api.receive_task(
                device_info, 
                session_info, 
                task_id=3812,
                receive_type='4',
                act_id=1021,
                proxy=proxy
            )
            if success:
                success_count += 1
                print(f"[{remark}] 第{i+1}/{count}次成功")
            else:
                fail_count += 1
                error = result.get('error', '未知错误') if result else '未知错误'
                last_error = error
                print(f"[{remark}] 第{i+1}/{count}次失败: {error}")
            
            if i < count - 1:
                interval = random.uniform(2, 4)
                time.sleep(interval)
        except Exception as e:
            fail_count += 1
            last_error = str(e)
            print(f"[{remark}] 第{i+1}/{count}次异常: {str(e)}")
    
    print(f"[{remark}] 攒钱罐提现完成，成功: {success_count}，失败: {fail_count}")
    
    return {
        'remark': remark,
        'success': True,
        'success_count': success_count,
        'fail_count': fail_count,
        'total': count,
        'last_error': last_error
    }

def cmd_progress():
    """刷进度命令"""
    user_accounts = get_user_accounts(userid)
    
    if not user_accounts:
        sender.reply("""📭 暂无绑定账号

💡 请先发送"卡看登录"绑定账号""")
        return
    
    QLurl, ClientID, ClientSecret, env_name, coin_price, money_price, zsm, coin_bucket, admin_ids, wechat_enabled, proxy_url = get_plugin_config()
    
    valid_accounts = []
    for remark in user_accounts:
        auth_status = get_account_auth(remark)
        _, is_valid = check_auth_status(auth_status)
        if is_valid:
            valid_accounts.append(remark)
    
    if not valid_accounts:
        sender.reply("""❌ 没有已授权的账号

💡 请先发送"卡看管理"进行授权""")
        return
    
    if len(valid_accounts) > 1:
        message = f"""=====卡看刷进度=====
📱 已授权账号列表:
------------------
"""
        for idx, remark in enumerate(valid_accounts, 1):
            auth_status = get_account_auth(remark)
            _, is_valid = check_auth_status(auth_status)
            status = "✅" if is_valid else "❌"
            message += f"{idx}. {remark} {status}\n"
        
        message += f"""------------------
📝 请选择账号（多选用逗号分隔）
💡 输入"0"选择全部已授权账号
⚠️ 输入"q"退出
=================="""
        
        sender.reply(message)
        choice = sender.input(120000, 5000, False)
        
        if not choice or choice.lower() == 'q':
            sender.reply('✅ 已取消操作')
            return
        
        try:
            if choice.strip() == '0':
                selected = valid_accounts
            else:
                indices = [int(x.strip()) for x in choice.split(',')]
                selected = [valid_accounts[i-1] for i in indices if 1 <= i <= len(valid_accounts)]
                
                if not selected:
                    sender.reply('❌ 无有效选择')
                    return
        except:
            sender.reply('❌ 输入格式错误')
            return
    else:
        selected = valid_accounts
    
    sender.reply(f"""=====刷进度设置=====
📱 已选择 {len(selected)} 个账号
------------------
📝 请输入刷取次数 (1-100)
💡 推荐: 30-50次
⚠️ 输入"q"退出
==================""")
    
    count_input = sender.input(120000, 5000, False)
    
    if not count_input or count_input.lower() == 'q':
        sender.reply('✅ 已取消操作')
        return
    
    try:
        count = int(count_input)
        if count < 1 or count > 100:
            sender.reply('❌ 次数必须在1-100之间')
            return
    except:
        sender.reply('❌ 输入格式错误')
        return
    
    sender.reply(f"""=====确认执行=====
📱 账号数量: {len(selected)}个
🔄 刷取次数: {count}次/账号
------------------
确认执行请回复【y】
取消请回复【n】
==================""")
    
    confirm = sender.input(60000, 5000, False)
    if not confirm or confirm.lower() != 'y':
        sender.reply('✅ 已取消操作')
        return
    
    kakan_api = KaKanAPI()
    
    max_workers = 10
    total_accounts = len(selected)
    batch_num = (total_accounts + max_workers - 1) // max_workers
    
    all_results = []
    start_time = time.time()
    
    sender.reply(f"🔄 开始执行刷进度任务...\n📊 共 {total_accounts} 个账号，分 {batch_num} 批执行")
    
    for batch_idx in range(batch_num):
        batch_start = batch_idx * max_workers
        batch_end = min(batch_start + max_workers, total_accounts)
        batch_accounts = selected[batch_start:batch_end]
        
        batch_proxy, batch_proxy_info = get_proxy(proxy_url)
        
        sender.reply(f"📦 第 {batch_idx + 1}/{batch_num} 批: 账号 {batch_start + 1}-{batch_end}\n🌐 代理: {batch_proxy_info}")
        
        with ThreadPoolExecutor(max_workers=len(batch_accounts)) as executor:
            futures = {
                executor.submit(execute_single_account_progress, kakan_api, remark, count, batch_proxy): remark
                for remark in batch_accounts
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    all_results.append(result)
                    
                    if result['success']:
                        sender.reply(f"✅ {result['remark']}: 成功{result['success_count']}/{result['total']}次")
                    else:
                        sender.reply(f"❌ {result['remark']}: {result['msg']}")
                except Exception as e:
                    remark = futures[future]
                    all_results.append({'remark': remark, 'success': False, 'msg': str(e)})
                    sender.reply(f"❌ {remark}: 执行异常")
        
        if batch_idx < batch_num - 1:
            time.sleep(2)
    
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    
    success_accounts = sum(1 for r in all_results if r['success'])
    fail_accounts = sum(1 for r in all_results if not r['success'])
    
    total_success = sum(r.get('success_count', 0) for r in all_results if r['success'])
    total_fail = sum(r.get('fail_count', 0) for r in all_results if r['success'])
    
    sender.reply(f"""=====执行完成=====
✅ 成功账号: {success_accounts}个
❌ 失败账号: {fail_accounts}个
------------------
📊 总成功次数: {total_success}次
📊 总失败次数: {total_fail}次
⏰ 总耗时: {minutes}分{seconds}秒
💡 使用独立代理IP
==================""")

# ==================== 主程序入口 ====================
msg = sender.getMessage()

if '卡看教程' in msg:
    cmd_help()
elif '卡看登录' in msg:
    cmd_login()
elif '卡看查询' in msg:
    cmd_query()
elif '卡看管理' in msg:
    cmd_manage()
elif '卡看刷进度' in msg:
    cmd_progress()
else:
    sender.reply("❌ 未知指令\n💡 发送'卡看教程'查看使用说明")
