# [title: 牛卡福司机]
# [language: python]
# [class: 工具类]
# [service: 203066880]
# [author: rujingxianghai]
# [rule: ^(牛卡福|nkf)(登录|登陆)$|^登(录|陆)(牛卡福|nkf)$|^(牛卡福|nkf)(查询|管理|授权|检测|教程|一键更新)$]
# [cron: 0 8 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://img.xxkx.de/file/eYvOjFXl.jpg]
# [version: 3.5]
# [public: true]
# [price: 8.88]
# [description: 牛卡福插件v3【使用vorto_utils模块重构】【兼容青龙与呆呆面板】<br>短信验证码登录 + 滑块识别<br>指令：登录、管理、查询、授权、教程、一键更新]

# [param: {"required":false,"key":"s_nkfsj.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数（兼容青龙与呆呆面板），不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_nkfsj.use_dumbpanel","bool":true,"placeholder":"","name":"使用DumbPanel","desc":"勾选使用DumbPanel面板，不勾选使用青龙面板"}]
# [param: {"required":false,"key":"s_nkfsj.panel_group","bool":false,"placeholder":"例:顺丰","name":"DumbPanel分组","desc":"填写后新增/更新变量时同步写入group字段，留空则不处理"}]
# [param: {"required":true,"key":"s_nkfsj.osname","bool":false,"placeholder":"例:S_NKF","name":"青龙变量名","desc":"青龙容器内的变量名"}]
# [param: {"required":true,"key":"s_nkfsj.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_nkfsj.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_nkfsj.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_nkfsj.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]
# [param: {"required":false,"key":"s_nkfsj.proxy_url","bool":false,"placeholder":"API地址或ip:port","name":"代理地址","desc":"登录请求代理，支持两种模式：1)API形式(http开头的URL，GET请求返回ip:port文本) 2)代理池形式(直接填写ip:port)"}]

# 账号变量格式：NKFSJ=手机号#密码#deviceid#device_name

import os
import json
import time
import hashlib
import random
import string
import requests
import base64
import uuid
from datetime import datetime, timedelta
from urllib.parse import quote as url_quote
import sys

# 导入 vorto_utils 模块
import vorto_utils
from vorto_utils import (
    mask_account,
    process_authorization,
    process_coin_payment,
    check_auth_status,
    admin_auth_all_accounts,
    admin_auth_by_user,
)

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import PKCS1_v1_5

import middleware

# 滑块识别API地址
SLIDER_API_URL = "https://slider-verification.vzvv.de/solve"


# ==================== 代理工具函数 ====================
def get_proxy_config():
    """获取代理配置，返回 proxies 字典或 None"""
    proxy_url = middleware.bucketGet('s_nkfsj', 'proxy_url') or ''
    proxy_url = proxy_url.strip()
    if not proxy_url:
        return None

    try:
        if proxy_url.lower().startswith('http'):
            # API形式：GET请求获取代理IP
            resp = requests.get(proxy_url, timeout=10)
            proxy_text = resp.text.strip()
            # 返回的格式为 ip:port
            if not proxy_text or ':' not in proxy_text:
                print(f"代理API返回格式异常: {proxy_text}")
                return None
            # 取第一行（有些API可能返回多行）
            proxy_ip_port = proxy_text.splitlines()[0].strip()
            proxy_addr = f"http://{proxy_ip_port}"
        else:
            # 代理池形式：直接填写 ip:port
            if ':' not in proxy_url:
                print(f"代理地址格式异常: {proxy_url}")
                return None
            proxy_addr = f"http://{proxy_url}"

        proxies = {
            'http': proxy_addr,
            'https': proxy_addr
        }
        print(f"使用代理: {proxy_addr}")
        return proxies
    except Exception as e:
        print(f"获取代理失败: {e}")
        return None


# ==================== 初始化 ====================
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_nkfsj_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_nkfsj', 'coin_key': 'dd_sign_points', 'name': '牛卡福司机'}


# ==================== 随机设备名称 ====================
DEVICE_MODELS = [
    # 小米系列
    "Xiaomi 14 Ultra", "Xiaomi 14 Pro", "Xiaomi 14", "Xiaomi 13 Ultra", "Xiaomi 13 Pro",
    "Xiaomi 12S Ultra", "Xiaomi 12 Pro", "Redmi K70 Pro", "Redmi K60 Pro", "Redmi Note 13 Pro",
    # 华为系列
    "HUAWEI Mate 60 Pro", "HUAWEI Mate 60", "HUAWEI P60 Pro", "HUAWEI nova 12 Ultra",
    # OPPO系列
    "OPPO Find X7 Ultra", "OPPO Find X6 Pro", "OPPO Reno11 Pro", "OPPO A3 Pro",
    # vivo系列
    "vivo X100 Pro", "vivo X100", "vivo X90 Pro+", "vivo S18 Pro", "iQOO 12 Pro",
    # 荣耀系列
    "HONOR Magic6 Pro", "HONOR Magic5 Pro", "HONOR 100 Pro", "HONOR X50",
    # 一加系列
    "OnePlus 12", "OnePlus 11", "OnePlus Ace 3",
    # 三星系列
    "Samsung Galaxy S24 Ultra", "Samsung Galaxy S24+", "Samsung Galaxy S23 Ultra",
    # 真我系列
    "realme GT5 Pro", "realme GT Neo5", "realme 12 Pro+",
]

def generate_random_device_name():
    """生成随机设备名称"""
    return random.choice(DEVICE_MODELS)


# ==================== 工具函数 ====================
def format_red_envelope_details(records, limit=5):
    """格式化红包明细"""
    if not records:
        return ""

    lines = [f"🧧 红包明细(前{limit}条):"]
    for record in records[:limit]:
        raw_amount = record.get('rewardAmount')
        try:
            amount = f"{float(raw_amount):.2f}"
        except Exception:
            amount = "0.00"

        create_time = record.get('createTime')
        win_date = '未知日期'
        try:
            ts = int(str(create_time))
            if ts > 10 ** 12:
                ts = ts / 1000
            win_date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        except Exception:
            pass

        status_desc = str(record.get('rewardStatusDesc') or '')
        status_raw = str(record.get('rewardStatus') or '')
        arrival_status = '已到' if ('已到账' in status_desc or status_raw == 'DISTRIBUTED') else '未到'

        lines.append(f"🧧 {amount} {win_date} {arrival_status}")

    return "\n".join(lines)



# ==================== 牛卡福API类 ====================
class NucarfAPI:
    """牛卡福司机端API"""

    # X坐标偏移量（OpenCV识别结果需要+3）
    X_OFFSET = 3

    # RSA 私钥（用于签名）
    RSA_PRIVATE_KEY = """MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQClbxKSzi6QV1xjfveX1XZtDMKyzIFJOksxZ42LUY/N/Z1o08NqaoqbwhH8EOA63o98ytoZYLemWALQqRsBcxJMB1Xd+c9+EUhQD7rKp4TPE/fViHzGm32X+BScpfXjuHHP1nijmxftMf7NJfyop1TB0rxBQZWOnFwwPjN3HD6RRuK9ULMKeK1Zxa17mGr0GDqFQ9LXNlp/Mz0/eEWiN2+bEumQaIP5Uet5Yz6dOPSyCLuETpKr50iqtKJF5kn3DTCoyIDOb34bGK1jGZTQcZklRAIUTXP/v480w9GGFyhuZQ21MNZCm8+aUZOmtP60nhXhFKPLjH8ydCpEFbuw3j3jAgMBAAECggEAfZVBzjvCUURgGA+MOLCMw9+J9V0VT9d2uTxY0MfLmJ3L3oXStHfIXNEIAgd1kHrfBeafheBLyXTKPkgA/iqyWxC+eFFo19SaxlwKekiMov4PhwOjZMkooDJswzWg4YtkqlevINNdaGwpduY9VHIh/zjQO+FjfOzpdp3hR6wjOvgSEn9do7q2MPyf+maFe57wvc5rfafCqzQeSZUI7YGRM4tc8uaOsJEnrd/PDqW53wGFs+cyH4NRdXvN/EQtKmTHTGhArCglUB5XT8lwQ/RlENgIEqbA8gCA28dreTrXuccpP4XQxZyjApilkrptXIZVaK97QzHZGdPUmrv/4aWN0QKBgQDUTlldgfpDn1maRgG4lc1eI9uecs7IxH9s/I2JpnXd5ifMSiCoPSv+LnZLV8hiZ4VwXDQ7PeX+Cfd8d3piH37HzqMMXuJhdgbo8OZNLCuo+NMvLcvGGHN4qWHybwM4KPIBFzCLkZsN6FyEbQ0meAcwqU+qTuwCbBsUztCIJkmnlwKBgQDHezH+paXPIalwIss8OL88G5gYLDJMi5A/tYlQEH2pmQaRxcDThD7pzxIOdXyMTDQrUV30zZMLX1nJUQ94fu0yC0UN6P8aUUx5B5ZVuTkkAVrjVRWCBE/J3ySe25oX1BWeP4KCD/m+tEuRjzgEabq1wjniwoKui8OjrD6CO0xFlQKBgDwyMth2gBUoW2mIq/hAUUh99klI2CTIwjCOszryPb07AtHDutq47X5Wgif+rcxo+cbP/edGN639+XQLFGI59+KDTmu1g46Kvo7Rrxr2iTKRyp835u02BZeSvzjUDR+hTGzOvG72S/Z3ibPqj632nmNHvlTVp8lQCaWutiXEZWHlAoGBAJarwcZincvG1DFDxph1EFS5TvcrIs7YN5s3ZkDYQ+I/GEwwvwXEhLSbWDsdmHZr9JenfL00LVXQroO1u2a7EDPVeVIZY94f/BAKoA2dusAsWdcN5BHxacbDyehHXKuU4MNHmy7cHDpj+hQ2xgvnRESXMJvLaWOnY50Ts58wZNrFAoGBAJ5528sPkk95GdM+T1ykX6rDDHG+MWTWQ6kMLyES8sHYnUxcL9ihHKtokriMrBjfkLfCfTXr6piaupGljJQDHc6FeSTRcvxigMw4fzfbW+dlz8ZWetIxN1tBwbVPH9LcwLdsdOhPiojfxoUdNdYPXTYb7lSwqCJwVqcDFJr2n2RD"""

    # AES 密钥和 IV
    AES_KEY = "ef4d4f8e73cc1b84"
    AES_IV = "1234567812345678"

    def __init__(self, device_id=None, device_name=None, use_proxy=False):
        self.base_url = "https://unify-driver.nucarf.net/api"
        self.activity_base_url = "https://driver-activity.nucarf.net/api"
        self.device_id = device_id or self.generate_device_id()
        self.device_name = device_name or generate_random_device_name()
        self.token = None
        self.unify_id = None
        self.proxies = get_proxy_config() if use_proxy else None

    def generate_device_id(self):
        """生成随机设备ID"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

    def get_headers(self, use_encrypt=False):
        """获取请求头"""
        common_headers_dict = {
            "ip": "192.168.124.153",
            "deviceid": self.device_id,
            "uid": "",
            "platform": "android",
            "appid": "com.nucarf.member",
            "ver": "5.9.0",
            "lon": 116.397499,
            "lat": 39.908722,
            "network": "wifi",
            "session_id": str(uuid.uuid4()),
            "channel": "xiaomi",
            "url": "",
            "imei": self.device_id,
            "identity": "0",
            "user_agent": "Dalvik/2.1.0 (Linux; U; Android 16; 2210132C Build/BP2A.250605.031.A3)"
        }

        headers = {
            'User-Agent': 'okhttp/3.14.9',
            'Accept-Encoding': 'gzip',
            'common-headers': json.dumps(common_headers_dict, separators=(',', ':')),
            'x-access-token': self.token or '',
            'x-request-id': str(uuid.uuid4()),
            'x-access-token-d': '',
            'token': self.token or '',
            'x-apptype': 'APP',
            'x-appversion': '5.9.0',
            'x-device-id': self.device_id,
            'x-device-type': 'ANDROID',
            'x-device-name': self.device_name,
            'x-device-ip': '192.168.124.153',
            'x-driver-id': '',
            'x-term-id': '24427455',
            'x-driver-unifyid': self.unify_id or '',
            'content-type': 'application/json; charset=UTF-8',
            'Cookie': ''
        }

        if use_encrypt:
            headers['x-app-encrypt'] = 'encryptedData'

        return headers

    def get_simple_headers(self):
        """获取简单请求头（用于密码登录后的接口）"""
        return {
            "X-Request-Id": str(uuid.uuid4()),
            "X-AppType": "APP",
            "X-Device-Id": self.device_id,
            "X-Device-Name": self.device_name,
            "X-Device-Type": "ANDROID",
            "X-AppVersion": "5.9.0",
            "X-Driver-UnifyId": self.unify_id or '',
            "X-Access-Token": self.token or ''
        }

    def encrypt_data_cbc(self, data):
        """使用AES/CBC加密数据（URL-safe Base64）"""
        key = self.AES_KEY.encode('utf-8')
        iv = self.AES_IV.encode('utf-8')

        cipher = AES.new(key, AES.MODE_CBC, iv)
        json_data = json.dumps(data, separators=(',', ':'))
        padded_data = pad(json_data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)

        encrypted_base64 = base64.b64encode(encrypted).decode('utf-8')
        return encrypted_base64.replace('+', '-').replace('/', '_').replace('=', '')

    def decrypt_data_cbc(self, encrypted_str):
        """使用AES/CBC解密数据（URL-safe Base64）"""
        try:
            key = self.AES_KEY.encode('utf-8')
            iv = self.AES_IV.encode('utf-8')

            b64_str = encrypted_str.replace('-', '+').replace('_', '/')
            padding_needed = 4 - (len(b64_str) % 4)
            if padding_needed != 4:
                b64_str += '=' * padding_needed

            encrypted_bytes = base64.b64decode(b64_str)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
            return json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            print(f"解密失败: {e}")
            return None

    def generate_sign(self, data_md5):
        """生成 RSA 签名"""
        try:
            private_key = RSA.import_key(base64.b64decode(self.RSA_PRIVATE_KEY))
            h = SHA256.new(data_md5.encode('utf-8'))
            signature = pkcs1_15.new(private_key).sign(h)
            signature_base64 = base64.b64encode(signature).decode('utf-8')
            timestamp = int(time.time() * 1000)
            return f"{signature_base64}_{timestamp}"
        except Exception as e:
            print(f"生成签名失败: {e}")
            return None

    def encrypt_aes_ecb(self, data, key):
        """AES ECB PKCS7 加密（标准Base64）"""
        try:
            key_bytes = key.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_ECB)
            padded_data = pad(data.encode('utf-8'), AES.block_size)
            encrypted = cipher.encrypt(padded_data)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"AES加密异常: {e}")
            return None

    def get_captcha(self):
        """获取滑块验证码"""
        url = f"{self.base_url}/driver/captcha/getCaptcha"
        payload = {
            "clientUid": self.device_id,
            "captchaType": "blockPuzzle",
            "ts": str(int(time.time() * 1000))
        }

        try:
            response = requests.post(url, headers=self.get_headers(), json=payload, proxies=self.proxies, timeout=30)
            result = response.json()
            if result.get('code') == 200:
                return result.get('data')
            return None
        except Exception as e:
            print(f"获取验证码异常: {e}")
            return None

    def solve_captcha(self, bg_base64, slide_base64):
        """使用远程API识别滑块验证码"""
        try:
            resp = requests.post(SLIDER_API_URL, json={
                "bg": bg_base64,
                "slide": slide_base64,
                "offset": self.X_OFFSET
            }, timeout=30, proxies=self.proxies)
            result = resp.json()
            if result.get('success'):
                x = result['data']['x']
                print(f"滑块识别成功: x={x}, 置信度={result['data'].get('confidence', 'N/A')}")
                return x
            else:
                print(f"滑块识别失败: {result.get('error')}")
                return None
        except Exception as e:
            print(f"滑块识别API调用异常: {e}")
            return None

    def check_captcha(self, token, x_pos, secret_key):
        """验证滑块验证码"""
        url = f"{self.base_url}/driver/captcha/checkCaptcha"

        point_data = {"x": float(x_pos), "y": 5.0}
        point_json_str = json.dumps(point_data, separators=(',', ':'))

        encrypted_point_json = self.encrypt_aes_ecb(point_json_str, secret_key)
        if not encrypted_point_json:
            return None

        payload = {
            "clientUid": self.device_id,
            "pointJson": encrypted_point_json,
            "captchaType": "blockPuzzle",
            "token": token
        }

        try:
            response = requests.post(url, headers=self.get_headers(), json=payload, proxies=self.proxies, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                verification_raw = f"{token}---{point_json_str}"
                return self.encrypt_aes_ecb(verification_raw, secret_key)
            return None
        except Exception as e:
            print(f"验证异常: {e}")
            return None

    def send_sms_code(self, mobile, captcha_verification=""):
        """发送短信验证码"""
        url = f"{self.base_url}/driver/app/common/sendSmsCode"

        data = {
            "captchaSource": "1",
            "captchaVerification": captcha_verification,
            "clientUid": self.device_id,
            "codeType": "LOGIN",
            "mobile": mobile
        }

        encrypted_data = self.encrypt_data_cbc(data)
        payload = {"encryptedData": encrypted_data}

        data_md5 = hashlib.md5(encrypted_data.encode('utf-8')).hexdigest()
        sign = self.generate_sign(data_md5)

        headers = self.get_headers(use_encrypt=True)
        headers['sign'] = sign

        try:
            response = requests.post(url, headers=headers, json=payload, proxies=self.proxies, timeout=30)
            return response.json()
        except Exception as e:
            print(f"发送短信异常: {e}")
            return None

    def login_with_sms(self, mobile, sms_code):
        """使用短信验证码登录"""
        url = f"{self.base_url}/driver/app/auth/login"

        data = {
            "deviceIp": "192.168.124.153",
            "deviceType": "ANDROID",
            "loginType": "MOBILE_CODE",
            "username": mobile,
            "verificationCode": sms_code
        }

        encrypted_data = self.encrypt_data_cbc(data)
        payload = {"encryptedData": encrypted_data}

        data_md5 = hashlib.md5(encrypted_data.encode('utf-8')).hexdigest()
        sign = self.generate_sign(data_md5)

        headers = self.get_headers(use_encrypt=True)
        headers['sign'] = sign

        try:
            response = requests.post(url, headers=headers, json=payload, proxies=self.proxies, timeout=30)
            result = response.json()

            if result.get('code') == 200:
                data = result.get('data')
                if isinstance(data, str):
                    data = self.decrypt_data_cbc(data)

                if data:
                    self.token = data.get('token')
                    self.unify_id = data.get('unifyId')
                    return True, data, "登录成功"

            return False, None, result.get('message', '登录失败')
        except Exception as e:
            return False, None, str(e)

    def get_pub_key(self):
        """获取 RSA 公钥"""
        url = f"{self.base_url}/driver/app/unify/common/getPubKey"
        try:
            response = requests.get(url, proxies=self.proxies, timeout=30)
            data = response.json()
            if data['code'] == 200:
                return data['data']['pubKeyId'], data['data']['pubKey']
            return None, None
        except Exception as e:
            print(f"获取公钥异常: {e}")
            return None, None

    def encrypt_password(self, password, pub_key_pem):
        """使用 RSA 公钥加密密码"""
        try:
            key = RSA.importKey(pub_key_pem)
            cipher = PKCS1_v1_5.new(key)
            ciphertext = cipher.encrypt(password.encode('utf-8'))
            return base64.b64encode(ciphertext).decode('utf-8')
        except Exception:
            return None

    def set_password(self, password):
        """设置登录密码（首次设置）"""
        pub_key_id, pub_key = self.get_pub_key()
        if not pub_key:
            return False, "获取公钥失败"

        encrypted_password = self.encrypt_password(password, pub_key)
        if not encrypted_password:
            return False, "密码加密失败"

        url = f"{self.base_url}/driver/app/user/v2/setPassword"
        payload = {
            "password": encrypted_password,
            "pubKeyId": pub_key_id,
            "oldPassword": "NEW_SET_PASSWORD",
            "destroyAllToken": True,
            "setPwdType": "NEW_SET_PASSWORD",
            "force": True
        }

        try:
            response = requests.post(url, headers=self.get_headers(), json=payload, proxies=self.proxies, timeout=30)
            result = response.json()
            if result.get('code') == 200:
                return True, result.get('data', '密码设置成功')
            else:
                return False, result.get('message', '设置密码失败')
        except Exception as e:
            return False, str(e)

    def login_with_password(self, username, password):
        """账密登录"""
        pub_key_id, pub_key = self.get_pub_key()
        if not pub_key:
            return False, None, "获取公钥失败"

        encrypted_password = self.encrypt_password(password, pub_key)
        if not encrypted_password:
            return False, None, "密码加密失败"

        url = f"{self.base_url}/driver/app/auth/login"
        headers = {
            "x-request-id": str(uuid.uuid4()),
            "x-apptype": "APP",
            "x-appversion": "5.9.0",
            "x-device-id": self.device_id,
            "x-device-type": "ANDROID",
            "x-device-name": self.device_name,
            "Content-Type": "application/json"
        }
        payload = {
            "deviceIp": "192.168.124.153",
            "deviceType": "ANDROID",
            "loginType": "MOBILE_PASSWORD",
            "pubKeyId": pub_key_id,
            "username": username,
            "verificationCode": encrypted_password
        }

        try:
            response = requests.post(url, headers=headers, json=payload, proxies=self.proxies, timeout=30)
            data = response.json()
            if data['code'] == 200:
                self.token = data['data']['token']
                self.unify_id = data['data']['unifyId']
                return True, data['data'], "登录成功"
            else:
                return False, None, data.get('message', '登录失败')
        except Exception as e:
            return False, None, str(e)

    def get_points_info(self):
        """获取积分信息"""
        if not self.token or not self.unify_id:
            return None

        url = f"{self.base_url}/points/account/getAccountInfo"
        payload = {
            "unifyId": self.unify_id,
            "platformType": "NUCARF_DRIVER"
        }

        try:
            response = requests.post(url, headers=self.get_simple_headers(), json=payload, proxies=self.proxies, timeout=30)
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                return data['data'].get('totalPoints', '0')
            return None
        except Exception as e:
            print(f"获取积分异常: {e}")
            return None

    def get_wallet_balance(self):
        """获取钱包余额"""
        if not self.token or not self.unify_id:
            return None

        url = f"{self.base_url}/driver/app/middle/wallet/entrance"

        try:
            response = requests.get(url, headers=self.get_simple_headers(), proxies=self.proxies, timeout=30)
            data = response.json()
            if data.get('code') == 200 and data.get('data'):
                return data['data'].get('walletBalance', '0')
            return None
        except Exception as e:
            print(f"获取余额异常: {e}")
            return None

    def get_red_envelope_records(self, page_no=1, page_size=10):
        """获取红包中奖记录并扁平化返回"""
        if not self.token or not self.unify_id:
            return []

        url = f"{self.activity_base_url}/driver/app/unify/activity/instantgrab/myWinningRecordByActivity"
        payload = {
            "pageNo": page_no,
            "pageSize": page_size
        }

        headers = self.get_simple_headers()
        headers['Content-Type'] = 'application/json'

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15, proxies=self.proxies)
            data = response.json()
            if data.get('code') != 200:
                return []

            activity_list = data.get('data') or []
            records = []
            for activity in activity_list:
                for record in (activity.get('recordList') or []):
                    records.append(record)
            return records
        except Exception as e:
            print(f"获取红包明细异常: {e}")
            return []


# ==================== 青龙操作 (使用 vorto_utils) ====================
def _get_ql_client():
    """获取面板客户端，根据开关决定使用青龙或DumbPanel"""
    osname = middleware.bucketGet('s_nkfsj', 'osname') or 'S_NKF'
    qlname = middleware.bucketGet('s_nkfsj', 'qlname') or ''
    use_dp = str(middleware.bucketGet('s_nkfsj', 'use_dumbpanel') or '').lower() == 'true'

    if use_dp:
        if qlname:
            return vorto_utils.DumbPanelClient(osname, qlname)
        return vorto_utils.DumbPanelClient(osname)
    else:
        if qlname:
            return vorto_utils.QingLongClient(osname, qlname)
        return vorto_utils.QingLongClient(osname)


def _normalize_panel_account_info(username, account_info):
    """兼容字符串/字典两种账号信息，统一提取面板同步所需字段。"""
    if isinstance(account_info, str):
        raw = account_info.strip()
        if not raw:
            return '', '', ''
        if raw.startswith('{'):
            try:
                account_info = json.loads(raw)
            except Exception:
                return '', '', ''
        else:
            parts = raw.split('#')
            if len(parts) >= 3:
                return parts[0].strip() or username, parts[1].strip(), parts[2].strip()
            return username, '', ''

    if not isinstance(account_info, dict):
        return '', '', ''

    phone = (
        account_info.get('phone')
        or account_info.get('mobile')
        or account_info.get('username')
        or username
    )
    token = account_info.get('token') or account_info.get('accessToken') or ''
    unify_id = account_info.get('unifyId') or account_info.get('unify_id') or ''
    return str(phone).strip(), str(token).strip(), str(unify_id).strip()


def update_ql_env(username, account_info):
    """更新青龙环境变量"""
    phone, token, unify_id = _normalize_panel_account_info(username, account_info)
    if not phone or not token or not unify_id:
        return False
    env_value = f"{phone}#{token}#{unify_id}"
    auth_time = middleware.bucketGet('s_nkfsj_auth', username) or '未授权'
    panel_group = (middleware.bucketGet('s_nkfsj', 'panel_group') or '').strip()
    ql = _get_ql_client()
    return ql.update_env(
        username,
        env_value,
        f"牛卡福司机:{username}|到期:{auth_time}",
        group=panel_group,
    )


def delete_ql_env(username):
    """删除青龙环境变量"""
    ql = _get_ql_client()
    return ql.delete_env(username)


# ==================== 登录功能 ====================
def bind_account():
    """绑定账号 - 短信验证码登录"""
    sender.reply(
        "=====牛卡福登录=====\n"
        "📱 请输入手机号:\n"
        "------------------\n"
        "回复\"q\"退出操作\n"
        "=================="
    )

    mobile = sender.input(120000, 1, False)
    if not mobile:
        sender.reply("⏰ 操作超时")
        return
    if mobile.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    if not mobile.isdigit() or len(mobile) != 11:
        sender.reply("❌ 手机号格式错误，请输入11位手机号")
        return

    api = NucarfAPI(use_proxy=True)

    sender.reply("🔄 正在发送验证码...")

    # 尝试发送短信
    res = api.send_sms_code(mobile)

    if not res:
        sender.reply("❌ 请求失败，请稍后重试")
        return

    # 需要滑块验证
    if res.get('code') == 4001:
        captcha_data = api.get_captcha()
        if not captcha_data:
            sender.reply("❌ 获取验证码失败")
            return

        token = captcha_data.get('token')
        secret_key = captcha_data.get('secretKey')

        x_pos = api.solve_captcha(
            captcha_data.get('originalImageBase64'),
            captcha_data.get('jigsawImageBase64')
        )

        if x_pos is None:
            sender.reply("❌ 滑块识别失败")
            return

        captcha_verification = api.check_captcha(token, x_pos, secret_key)

        if not captcha_verification:
            sender.reply("❌ 滑块验证失败")
            return

        res = api.send_sms_code(mobile, captcha_verification)

        if not res or res.get('code') != 200:
            fail_msg = (res or {}).get('message', '未知错误')
            sender.reply(f"❌ 发送验证码失败: {fail_msg}")
            return

    elif res.get('code') != 200:
        sender.reply(f"❌ 发送验证码失败: {res.get('message', '未知错误')}")
        return

    sender.reply(
        "✅ 验证码已发送\n"
        "📲 请输入短信验证码:\n"
        "------------------\n"
        "回复\"q\"退出\n"
        "=================="
    )

    sms_code = sender.input(120000, 1, False)
    if not sms_code:
        sender.reply("⏰ 操作超时")
        return
    if sms_code.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    sender.reply("🔄 正在登录...")

    success, login_data, msg = api.login_with_sms(mobile, sms_code)

    if not success:
        sender.reply(f"❌ 登录失败: {msg}")
        return

    sender.reply(
        f"✅ 短信登录成功！\n"
        f"📱 手机号: {mask_account(mobile)}\n"
        f"------------------\n"
        f"🔐 是否已设置登录密码？\n"
        f"已设置 → 直接输入密码\n"
        f"需设置 → 回复 y\n"
        f"回复 q 退出\n"
        f"=================="
    )

    pwd_input = sender.input(120000, 1, False)
    if not pwd_input:
        sender.reply("⏰ 操作超时")
        return
    if pwd_input.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    if pwd_input.lower() == 'y':
        # 需要设置密码
        sender.reply(
            "🔐 请输入要设置的登录密码：\n"
            "（用于后续脚本自动登录）\n"
            "------------------\n"
            "回复\"q\"退出\n"
            "=================="
        )

        password = sender.input(120000, 1, False)
        if not password:
            sender.reply("⏰ 操作超时")
            return
        if password.lower() == 'q':
            sender.reply("✅ 已取消")
            return

        sender.reply("🔄 正在设置密码...")

        # 使用当前登录的token设置密码
        set_success, set_msg = api.set_password(password)
        if not set_success:
            sender.reply(f"❌ 设置密码失败: {set_msg}")
            return

        sender.reply(f"✅ 密码设置成功！")
    else:
        # 用户直接输入了密码
        password = pwd_input

    # 验证密码是否可用
    sender.reply("🔄 正在验证密码...")

    # 使用相同的device_id和device_name验证密码
    verify_api = NucarfAPI(api.device_id, api.device_name, use_proxy=True)
    pwd_success, pwd_data, pwd_msg = verify_api.login_with_password(mobile, password)

    if not pwd_success:
        sender.reply(f"❌ 密码验证失败: {pwd_msg}\n请确保输入的是正确的登录密码")
        return

    # 保存账号到用户列表
    current_value = middleware.bucketGet('s_nkfsj_user', userid)
    if not current_value:
        middleware.bucketSet('s_nkfsj_user', userid, str([mobile]))
    else:
        accounts = eval(current_value)
        if mobile not in accounts:
            accounts.append(mobile)
            middleware.bucketSet('s_nkfsj_user', userid, str(accounts))

    # 保存账号信息 - 包含密码用于一键更新，token/unifyId用于上传青龙
    account_info = {
        "phone": mobile,
        "password": password,
        "device_id": verify_api.device_id,
        "device_name": verify_api.device_name,
        "token": verify_api.token,
        "unifyId": verify_api.unify_id
    }
    middleware.bucketSet('s_nkfsj_token', mobile, json.dumps(account_info))

    sender.reply(
        f"=====绑定成功=====\n"
        f"📱 账号: {mask_account(mobile)}\n"
        f"🔑 设备ID: {verify_api.device_id[:8]}...\n"
        f"📱 设备名: {verify_api.device_name}\n"
        f"=================="
    )

    # 检查授权状态
    dqsj = datetime.now().strftime("%Y-%m-%d")
    accountVip = middleware.bucketGet('s_nkfsj_auth', mobile)

    if accountVip and accountVip >= dqsj:
        sender.reply(f"📱 {mask_account(mobile)} 已授权，到期: {accountVip}")
        update_ql_env(mobile, account_info)
    else:
        sender.reply(f"\n📋 账号需要授权，发送\"牛卡福管理\"进行授权")


# ==================== 查询功能 ====================
def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply(f"=====未绑定账号=====\n❌ 未找到账号\n💡 发送 牛卡福登录 绑定\n==================")
        return

    accounts = eval(uservalue)
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_nkfsj_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(username)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    try:
        if choice == '0':
            selected = accounts.copy()
        else:
            selected = [
                accounts[int(idx.strip()) - 1]
                for idx in choice.split(',')
                if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
            ]

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        sender.reply(f"✅ 已选择 {len(selected)} 个账号，正在查询...")

        for i, username in enumerate(selected, 1):
            try:
                account_info = json.loads(middleware.bucketGet('s_nkfsj_token', username))
                auth_time = middleware.bucketGet('s_nkfsj_auth', username)

                if auth_time and auth_time >= str(datetime.now().date()):
                    auth_status = '已授权'
                else:
                    auth_status = '未授权'

                # 使用账密登录获取最新token查询
                api = NucarfAPI(
                    account_info.get('device_id'),
                    account_info.get('device_name'),
                    use_proxy=True
                )
                login_success, _, login_msg = api.login_with_password(
                    account_info.get('phone'),
                    account_info.get('password')
                )

                points = "N/A"
                balance = "N/A"
                red_envelope_text = ""
                login_status = "✓" if login_success else "✗"

                if login_success:
                    points = api.get_points_info() or "N/A"
                    balance = api.get_wallet_balance() or "N/A"
                    red_records = api.get_red_envelope_records(page_no=1, page_size=10)
                    red_envelope_text = format_red_envelope_details(red_records, limit=5)

                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 账号: {mask_account(username)}\n"
                    f"🏷 授权: {auth_status}\n"
                    f"📅 到期: {auth_time or '未授权'}\n"
                    f"💰 积分: {points}\n"
                    f"💵 余额: {balance} 元\n"
                    f"{red_envelope_text + chr(10) if red_envelope_text else ''}"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"=====查询失败=====\n❌ 错误: {str(e)}\n==================")

        sender.reply(f"✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


# ==================== 管理功能 ====================
def manage_account():
    """管理账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

    accounts = eval(uservalue)
    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交青龙\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_nkfsj_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(username)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    if account_choice == '0':
        selected = accounts.copy()
    else:
        selected = [
            accounts[int(idx.strip()) - 1]
            for idx in account_choice.split(',')
            if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
        ]

    if not selected:
        sender.reply("❌ 未选择有效账号")
        return

    sender.reply(f"✅ 已选择 {len(selected)} 个账号")

    if choice == '1':
        authorize_multiple_accounts(selected)
    elif choice == '2':
        sender.reply("=====确认删除=====\n⚠️ 此操作不可恢复\n回复 y 确认删除\n==================")
        if sender.input(120000, 1, False).lower() == 'y':
            for username in selected:
                if username in accounts:
                    accounts.remove(username)
                middleware.bucketDel('s_nkfsj_token', username)
                middleware.bucketDel('s_nkfsj_auth', username)
                delete_ql_env(username)

            if accounts:
                middleware.bucketSet('s_nkfsj_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_nkfsj_user', userid)
            sender.reply(f"✅ 已删除 {len(selected)} 个账号")
        else:
            sender.reply("✅ 已取消")
    elif choice == '3':
        success = 0
        for username in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_nkfsj_token', username))
                auth_time = middleware.bucketGet('s_nkfsj_auth', username)
                if auth_time and auth_time >= str(datetime.now().date()):
                    if update_ql_env(username, account_info):
                        success += 1
            except:
                pass
        sender.reply(
            f"=====提交结果=====\n"
            f"✅ 成功: {success}个\n"
            f"❌ 失败: {len(selected) - success}个\n"
            f"=================="
        )


def authorize_multiple_accounts(usernames):
    """批量授权账号 - 使用 vorto_utils"""
    account_infos = []
    for username in usernames:
        try:
            account_infos.append({
                'username': username,
                'info': json.loads(middleware.bucketGet('s_nkfsj_token', username))
            })
        except:
            pass

    if not account_infos:
        sender.reply("❌ 没有有效账号")
        return

    sender.reply(
        f"✅ {len(account_infos)} 个有效账号\n"
        f"=====设置授权时长=====\n"
        f"请输入授权月数(如:1)\n"
        f"回复\"q\"退出\n"
        f"=================="
    )
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return

        Vipmoney = float(middleware.bucketGet('s_nkfsj', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_nkfsj', 'coin') or '0')
        pay_config = vorto_utils.get_pay_config()
        pay_types = pay_config['pay_types']

        available = []
        if pay_config['qr_pay_switch']:
            available.append(("扫码支付", "qrcode"))
        if pay_config['ma_pay_switch']:
            if not pay_types:
                sender.reply("⚠️ 未配置码支付方式，请联系管理员在Vorto初始化中填写")
            else:
                for pay_key, pay_name in pay_types.items():
                    available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
        if coin > 0:
            available.append(("积分兑换", "coin"))

        menu = (
            f"=====选择支付方式=====\n"
            f"📊 账号: {len(account_infos)}个\n"
            f"⏰ 时长: {months}月\n"
            f"💰 金额: {total_money}元\n"
            f"------------------------"
        )
        for i, (name, _) in enumerate(available, 1):
            menu += f"\n[{i}] {name}"
        menu += "\n------------------------\n回复数字选择\n=================="
        sender.reply(menu)

        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply("✅ 已取消")
            return

        try:
            pay_idx = int(pay_choice) - 1
            if 0 <= pay_idx < len(available):
                payment_name, payment_type = available[pay_idx]
            else:
                sender.reply("❌ 无效选择")
                return
        except:
            sender.reply("❌ 请输入有效数字")
            return

        # 使用 vorto_utils 的 process_coin_payment 处理积分支付
        if payment_type == 'coin':
            for acc in account_infos:
                process_coin_payment(
                    sender, userid, 's_nkfsj_auth', acc['username'], acc['info'],
                    months, coin, lambda u, ai, m: process_authorization(
                        sender, 's_nkfsj_auth', u, ai, m, update_ql_callback=update_ql_env
                    )
                )
        elif payment_type == 'qrcode':
            if process_qrcode_payment(PLUGIN_CONFIG['name'], months, total_money):
                for acc in account_infos:
                    process_authorization(
                        sender, 's_nkfsj_auth', acc['username'], acc['info'], months,
                        update_ql_callback=update_ql_env
                    )
        elif payment_type.startswith('mapay_'):
            actual_pay_type = payment_type.replace('mapay_', '')
            if process_mapay_payment(PLUGIN_CONFIG['name'], months, total_money, actual_pay_type):
                for acc in account_infos:
                    process_authorization(
                        sender, 's_nkfsj_auth', acc['username'], acc['info'], months,
                        update_ql_callback=update_ql_env
                    )
    except ValueError:
        sender.reply("❌ 请输入有效数字")


# ==================== 码支付操作 (使用 vorto_utils) ====================
def process_mapay_payment(project, months, money, pay_type='alipay'):
    """码支付处理 (AUT格式)"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config['ma_pay_switch']:
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        out_trade_no = f"nkfsj_{int(time.time())}_{random.randint(1000, 9999)}"
        pay_type_name = pay_config['pay_types'].get(pay_type, '支付宝')

        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"💳 方式: {pay_type_name}\n"
            f"=================="
        )

        mapay = vorto_utils.MaPayClient()

        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)

        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False

        trade_no = order.get('trade_no')
        pay_url = order.get('pay_url')

        qr_url = vorto_utils.generate_qrcode_url(pay_url)
        sender.replyImage(qr_url)
        sender.reply(f'💳 请使用【{pay_type_name}】扫码支付\n⏰ 5分钟内完成支付\n输入"q"可取消')

        start_time = time.time()
        timeout = 300

        while time.time() - start_time < timeout:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                return True

        sender.reply("❌ 支付超时")
        return False

    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False


def process_qrcode_payment(project, months, money):
    """收款码支付处理 - 使用waitPay (AUT格式)"""
    if float(money) == 0:
        return True

    try:
        pay_config = vorto_utils.get_pay_config()
        zsm = pay_config['zsm']
        if not zsm:
            sender.reply("❌ 未配置收款码，请联系管理员")
            return False

        sender.reply(
            f"======扫码支付======\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"=================="
        )

        # 发送收款码
        sender.replyImage(zsm)

        # 使用AUT的waitPay等待支付确认
        ddzf = sender.waitPay("q", 300000)  # 5分钟超时

        if str(ddzf) == 'q':
            sender.reply('✅ 已取消')
            return False

        try:
            if isinstance(ddzf, str):
                ddzf = json.loads(ddzf)
            if float(ddzf.get('Money') or ddzf.get('money', 0)) >= float(money):
                return True
            sender.reply("❌ 支付金额不足")
            return False
        except:
            sender.reply("❌ 支付验证失败")
            return False

    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")


# ==================== 管理员功能 (使用 vorto_utils) ====================
def ks_auth():
    """管理员授权菜单 - 使用 vorto_utils"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理员授权")
        return

    if choice == '1':
        admin_auth_all_accounts(sender, 's_nkfsj_user', 's_nkfsj_auth', 's_nkfsj_token', update_ql_env)
    elif choice == '2':
        admin_auth_by_user(sender, 's_nkfsj_user', 's_nkfsj_auth', 's_nkfsj_token', update_ql_env)
    else:
        sender.reply("❌ 无效的选择")


def batch_update_tokens():
    """一键更新所有已授权且有密码账号的token和unifyId到青龙变量"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return

    try:
        all_users = middleware.bucketAllKeys('s_nkfsj_user')
        if not all_users:
            sender.reply("❌ 没有找到任何用户(bucketAllKeys返回空)")
            return

        # 确保 all_users 是列表（bucketAllKeys 可能返回逗号分隔的字符串）
        if isinstance(all_users, str):
            all_users = [k.strip() for k in all_users.split(',') if k.strip()]

        total_accounts = 0
        success_count = 0
        fail_count = 0
        skip_no_password = 0
        skip_not_auth = 0

        current_date = str(datetime.now().date())

        # 收集所有需要更新的账号（仅已授权且有密码的）
        accounts_to_update = []
        for raw_user_id in all_users:
            # 确保 user_id 是字符串并去除多余空白
            user_id = str(raw_user_id).strip()
            user_accounts_str = middleware.bucketGet('s_nkfsj_user', user_id)

            if not user_accounts_str:
                sender.reply(f"⚠️ 用户 {user_id[:8]}... 数据为空(key={repr(raw_user_id)})")
                continue
            try:
                accounts = eval(user_accounts_str)
            except Exception as e:
                sender.reply(f"⚠️ 用户 {user_id[:8]}... 解析失败: {str(e)[:30]}")
                continue
            if not isinstance(accounts, list):
                sender.reply(f"⚠️ 用户 {user_id[:8]}... 格式错误: {type(accounts)}")
                continue

            for phone in accounts:
                token_data = middleware.bucketGet('s_nkfsj_token', phone)
                if not token_data:
                    skip_no_password += 1
                    continue

                try:
                    account_info = json.loads(token_data)
                except Exception:
                    skip_no_password += 1
                    continue

                auth_time = middleware.bucketGet('s_nkfsj_auth', phone)

                # 检查授权状态（必须已授权且未过期）
                if not auth_time or auth_time < current_date:
                    skip_not_auth += 1
                    continue

                # 检查是否有密码（有密码才能自动登录更新token）
                if not account_info.get('password'):
                    skip_no_password += 1
                    continue

                accounts_to_update.append({
                    'phone': phone,
                    'account_info': account_info
                })
                total_accounts += 1

        if not accounts_to_update:
            sender.reply(
                f"❌ 没有找到符合条件的账号\n"
                f"⏭️ 跳过: {skip_not_auth} 个(未授权/已过期)\n"
                f"⏭️ 跳过: {skip_no_password} 个(无密码/无数据)"
            )
            return

        sender.reply(
            f"📊 找到 {total_accounts} 个已授权账号，开始更新...\n"
            f"⏭️ 跳过: {skip_not_auth} 个(未授权/已过期)"
        )

        for acc in accounts_to_update:
            phone = acc['phone']
            account_info = acc['account_info']

            try:
                # 使用账密登录获取新token
                api = NucarfAPI(
                    account_info.get('device_id'),
                    account_info.get('device_name'),
                    use_proxy=True
                )
                login_success, _, login_msg = api.login_with_password(
                    phone,
                    account_info.get('password')
                )

                if not login_success:
                    sender.reply(f"❌ {mask_account(phone)} 登录失败: {login_msg}")
                    fail_count += 1
                    continue

                # 更新account_info中的token和unifyId
                account_info['token'] = api.token
                account_info['unifyId'] = api.unify_id

                # 保存更新后的账号信息
                middleware.bucketSet('s_nkfsj_token', phone, json.dumps(account_info))

                # 已授权账号直接同步到青龙
                if not update_ql_env(phone, account_info):
                    sender.reply(f"⚠️ {mask_account(phone)} Token更新成功，但青龙同步失败")

                success_count += 1

            except Exception as e:
                sender.reply(f"❌ {mask_account(phone)} 更新异常: {str(e)}")
                fail_count += 1

        sender.reply(
            f"=====更新完成=====\n"
            f"✅ 成功: {success_count} 个\n"
            f"❌ 失败: {fail_count} 个\n"
            f"⏭️ 跳过: {skip_not_auth} 个(未授权/已过期)\n"
            f"⏭️ 跳过: {skip_no_password} 个(无密码)\n"
            f"=================="
        )

    except Exception as e:
        sender.reply(f"❌ 一键更新失败: {str(e)}")


def show_tutorial():
    """显示插件使用教程"""
    tutorial = """
=====牛卡福司机教程=====
📱 用户指令:
• 牛卡福登录 - 短信验证码登录绑定账号
• 牛卡福查询 - 查询账号状态、积分、余额
• 牛卡福管理 - 授权/删除/提交青龙
• 牛卡福教程 - 查看本教程
------------------
🔧 管理员指令:
• 牛卡福授权 - 管理员按天数授权
• 牛卡福检测 - 检测过期账号并清理
• 牛卡福一键更新 - 更新所有账号Token到青龙
------------------
💡 登录说明:
📝 使用短信验证码登录
📝 登录后设置密码用于一键更新Token
📝 青龙变量格式: 手机号#token#unifyId
------------------
📋 功能说明:
🎁 支持抢红包脚本
💰 查询显示积分和余额
==================
"""
    sender.reply(tutorial.strip())


# ==================== 主入口 ====================
def main():
    """主入口"""
    msg = sender.getMessage()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '教程' in msg and ('牛卡福' in msg or 'nkf' in msg.lower()):
        show_tutorial()
    elif '查询' in msg and ('牛卡福' in msg or 'nkf' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('牛卡福' in msg or 'nkf' in msg.lower()):
        manage_account()
    elif '牛卡福授权' in msg or 'nkf授权' in msg.lower():
        ks_auth()
    elif '牛卡福一键更新' in msg or 'nkf一键更新' in msg.lower():
        batch_update_tokens()
    elif '牛卡福检测' in msg or 'nkf检测' in msg.lower():
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        # 使用 vorto_utils 的 check_auth_status
        result = check_auth_status('s_nkfsj', 's_nkfsj_user', 's_nkfsj_auth', 's_nkfsj_token', '牛卡福', delete_ql_callback=delete_ql_env)
        sender.reply(result)
    # 定时任务
    elif sender.getImtype() == 'fake':
        try:
            result = check_auth_status('s_nkfsj', 's_nkfsj_user', 's_nkfsj_auth', 's_nkfsj_token', '牛卡福', delete_ql_callback=delete_ql_env)
            middleware.notifyMasters(result)
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
