#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [title: 速看免费小说]
# [language: python]
# [class: 羊毛类]
# [service: 203066880]
# [author: rujingxianghai]
# [rule: ^(速看|sk|sukan)(登录|登陆)$|^登(录|陆)(速看|sk|sukan)$|^(速看|sk|sukan)(查询|管理|授权|检测|教程)$]
# [cron: 0 8 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://img.xxkx.de/file/S27MPofo.jpg]
# [version: 1.0.3]
# [public: true]
# [price: 8.88]
# [description: 速看免费小说刷币插件<br>指令：速看登录、速看管理、速看查询、速看授权、速看教程]

# [param: {"required":true,"key":"s_sukan.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"青龙容器参数用丨分割"}]
# [param: {"required":true,"key":"s_sukan.osname","bool":false,"placeholder":"例:S_SUKAN","name":"青龙变量名","desc":"青龙容器内的变量名，默认S_SUKAN"}]
# [param: {"required":true,"key":"s_sukan.zsm","bool":false,"placeholder":"http://xxx.jpg","name":"收款码链接","desc":"微信收款码链接"}]
# [param: {"required":true,"key":"s_sukan.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_sukan.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_sukan.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_sukan.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]
# [param: {"required":true,"key":"s_sukan.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付"}]

import os
import json
import time
import uuid
import base64
import random
import hashlib
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse, parse_qs
import middleware

try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5
    from Crypto.Cipher import DES
    from Crypto.Signature import PKCS1_v1_5 as Signature_PKCS1_v1_5
    from Crypto.Hash import SHA
    from Crypto.Util.Padding import pad
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

# ===================== 【初始化】=====================
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_sukan_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_sukan', 'coin_key': 'dd_sign_points', 'name': '速看免费小说'}
PAY_TYPE_NAMES = {'alipay': '支付宝', 'wxpay': '微信支付', 'qqpay': 'QQ钱包'}

# ===================== 【密钥配置】=====================
RSA_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDFxo8kt6ftwFZ5QSXuVUOrQvYp
4fLVQb3uK/sgYwuR0A+rYdp97UsrjVWGjUQBUhKvjhDcJ8MIY22FJ4y1m/qmbHAe
NytfuP1pSnb34MEFV5tGUNvozAX/teuVARBLrlk9lql3ipJFKj0LWuZa7eHhX26O
dyXDjuA+Xw0hkEuW2QIDAQAB
-----END PUBLIC KEY-----"""

RSA_PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAMXGjyS3p+3AVnlB
Je5VQ6tC9inh8tVBve4r+yBjC5HQD6th2n3tSyuNVYaNRAFSEq+OENwnwwhjbYUn
jLWb+qZscB43K1+4/WlKdvfgwQVXm0ZQ2+jMBf+165UBEEuuWT2WqXeKkkUqPQta
5lrt4eFfbo53JcOO4D5fDSGQS5bZAgMBAAECgYAor4I/AXEQXeLsKtTMxMmY77uI
Pi0gZdfWqUGOFhIJOw4eKZEzGp++I+MWPPVieCnT55vcTmm2zg13uP0fVykmukWq
ZszG/ZNpPKYleOqnZOqQj7O3au8Ywz18F/pqD++PsUzxRVeXxSOOwmjQ0D2Pe/9y
utz62pyiFGAzDsaI6QJBAMn8DeBT3AtcWuONdiHL3yC4NkGJDdyBbMOaWyvrcvUU
Zr13uS9mZO6pLTN6v9tkmPUdvYxcPTJ9wdGR7NcNPDsCQQD6qluGI2VAlz4s5UoD
nelFKrwDPeiruE3I6wsrasK6h37DsAE6OrQgx2dm4yH7ntJHUlJCZ5ay1EBNfEex
gQv7AkA1r2vUwxVKY7q4nqHWa8SbgrrRAmePw0qwVreC3erJHyoLk+XBpnqPQKIF
+8tAueU5yTTXOLD/WZOJazrDEf5/AkBpwG+Ggu5Xtrcbd8ynA/sDHElf0MGVmNbw
OgFnWs42pa1cX6fU6ilOXvIH3TFcF6A9SMS9kThpz9QlHJaek4P7AkAavQillA/w
nrha9GsK5UFmzmwNfkjLLW4psAUsXOsqFXWMoxTd0xWuSbuVOzERpbFMBl1VoZQm
D9BLSVOTNe+v
-----END PRIVATE KEY-----"""

# 设备参数配置
DEVICE_CONFIG = {
    "device": "PLQ110",
    "firm": "OnePlus",
    "channelId": "801001",
    "versionId": "80002056",
    "p2": "801001",
    "p3": "80002056",
    "p4": "501656",
    "p5": "19",
    "p9": "0",
    "p16": "PLQ110",
    "p21": "99",
    "p22": "16",
    "p25": "80002056",
    "p26": "36",
    "p29": "zycb1bdb",
    "p33": "com.chaozh.xincao.only.sk",
    "p34": "OnePlus",
    "p36": "a",
    "d1": "8.0.2",
    "pc": "10",
    "rgt": "7",
}

API_BASE = "https://dj.palmestore.com"
API_SEND_SMS = f"{API_BASE}/dj_user/out/sms/sendSms/V2"
API_LOGIN = f"{API_BASE}/dj_user/out/login/loginByPhoneV3"


# ===================== 【加密函数】=====================
def rsa_encrypt(data: str) -> str:
    """RSA公钥加密"""
    if not CRYPTO_AVAILABLE:
        return ""
    key = RSA.import_key(RSA_PUBLIC_KEY)
    cipher = Cipher_PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def rsa_sign(data: str) -> str:
    """RSA私钥签名 (SHA1WithRSA)"""
    if not CRYPTO_AVAILABLE:
        return ""
    key = RSA.import_key(RSA_PRIVATE_KEY)
    h = SHA.new(data.encode('utf-8'))
    signer = Signature_PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    return base64.b64encode(signature).decode('utf-8')


def des_encrypt(data: str, key: str) -> str:
    """DES/CBC/PKCS5Padding 加密"""
    if not CRYPTO_AVAILABLE:
        return ""
    key_bytes = key.encode('utf-8')[:8].ljust(8, b'\0')
    iv_bytes = key_bytes
    cipher = DES.new(key_bytes, DES.MODE_CBC, iv_bytes)
    padded_data = pad(data.encode('utf-8'), DES.block_size)
    encrypted = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted).decode('utf-8')


def generate_des_key() -> str:
    """生成8位随机数字作为DES密钥"""
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])


def generate_pinfo(phone: str, code: str):
    """生成pInfo参数"""
    des_key = generate_des_key()
    encrypted_des_key = rsa_encrypt(des_key)
    data_json = json.dumps({"phone": phone, "pCode": code}, separators=(',', ':'))
    encrypted_data = des_encrypt(data_json, des_key)
    pinfo = json.dumps({
        "DesKey": encrypted_des_key,
        "Data": encrypted_data
    }, separators=(',', ':'))
    return pinfo, encrypted_des_key


def generate_device_ids():
    """生成设备标识"""
    zyeid = str(uuid.uuid4())
    imei = "____" + uuid.uuid4().hex[:16]
    p7 = "__" + uuid.uuid4().hex[:16]
    p28 = uuid.uuid4().hex.upper() + uuid.uuid4().hex[:32]
    return zyeid, imei, p7, p28


def generate_sign_content(params):
    """生成签名内容字符串"""
    sorted_keys = sorted(params.keys())
    parts = [f"{k}={params[k]}" for k in sorted_keys if params[k]]
    return "&".join(parts)


# ===================== 【脱敏函数】=====================
def mask_account(account):
    """账号脱敏处理"""
    if not account or len(account) < 4:
        return account
    if account.isdigit() and len(account) == 11:
        return f"{account[:3]}****{account[7:]}"
    if len(account) <= 16:
        return f"{account[:4]}****{account[-4:]}"
    return f"{account[:8]}****{account[-8:]}"


# ===================== 【配置获取】=====================
def get_user_content():
    """获取插件配置"""
    osname = middleware.bucketGet('s_sukan', 'osname') or 'S_SUKAN'
    qlname = middleware.bucketGet('s_sukan', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_sukan', 'Vipmoney') or '1')
    coin = int(middleware.bucketGet('s_sukan', 'coin') or '0')
    return osname, qlname, Vipmoney, coin


# ===================== 【API请求】=====================
class SukanAPI:
    """速看API客户端"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 16; PLQ110 Build/BP2A.250605.015)',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip',
        })
        self.zyeid, self.imei, self.p7, self.p28 = generate_device_ids()
        self.p1 = ""
        self.usr = ""
        self.ku = ""
        self.kt = ""
        self.p35 = ""
    
    def get_base_params(self):
        """获取基础URL参数"""
        return {
            "zyeid": self.zyeid,
            "usr": self.ku or f"j{int(time.time())}",
            "rgt": DEVICE_CONFIG["rgt"],
            "p1": self.p1,
            "ku": self.ku or self.usr or f"j{int(time.time())}",
            "pc": DEVICE_CONFIG["pc"],
            "p2": DEVICE_CONFIG["p2"],
            "p3": DEVICE_CONFIG["p3"],
            "p4": DEVICE_CONFIG["p4"],
            "p5": DEVICE_CONFIG["p5"],
            "p7": self.p7,
            "p9": DEVICE_CONFIG["p9"],
            "p12": "",
            "p16": DEVICE_CONFIG["p16"],
            "p21": DEVICE_CONFIG["p21"],
            "p22": DEVICE_CONFIG["p22"],
            "p25": DEVICE_CONFIG["p25"],
            "p26": DEVICE_CONFIG["p26"],
            "p28": self.p28,
            "p29": DEVICE_CONFIG["p29"],
            "p30": "",
            "p31": self.p7,
            "p33": DEVICE_CONFIG["p33"],
            "p34": DEVICE_CONFIG["p34"],
            "p36": DEVICE_CONFIG["p36"],
            "firm": DEVICE_CONFIG["firm"],
            "d1": DEVICE_CONFIG["d1"],
        }
    
    def send_sms(self, phone: str):
        """发送验证码"""
        timestamp = str(int(time.time() * 1000))
        encrypted_phone = rsa_encrypt(phone)
        
        sign_params = {
            "channelId": DEVICE_CONFIG["channelId"],
            "device": DEVICE_CONFIG["device"],
            "flag": "1",
            "imei": self.imei,
            "phone": encrypted_phone,
            "sendType": "0",
            "times": "1",
            "timestamp": timestamp,
            "versionId": DEVICE_CONFIG["versionId"],
        }
        sign_content = generate_sign_content(sign_params)
        sign = rsa_sign(sign_content)
        
        url_params = self.get_base_params()
        url = f"{API_SEND_SMS}?{urlencode(url_params)}"
        
        post_data = {
            "versionId": DEVICE_CONFIG["versionId"],
            "device": DEVICE_CONFIG["device"],
            "flag": "1",
            "imei": self.imei,
            "sign": sign,
            "timestamp": timestamp,
            "phone": encrypted_phone,
            "times": "1",
            "sendType": "0",
            "channelId": DEVICE_CONFIG["channelId"],
        }
        
        try:
            response = self.session.post(url, data=post_data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0 or result.get("msg") == "success":
                return True, "验证码发送成功"
            else:
                return False, result.get('msg', '未知错误')
        except Exception as e:
            return False, str(e)
    
    def login(self, phone: str, code: str):
        """验证码登录"""
        timestamp = str(int(time.time() * 1000))
        encrypted_phone = rsa_encrypt(phone)
        pInfo, encrypted_des_key = generate_pinfo(phone, code)
        
        sign_params = {
            "channelId": DEVICE_CONFIG["channelId"],
            "device": DEVICE_CONFIG["device"],
            "imei": self.imei,
            "phone": encrypted_phone,
            "timestamp": timestamp,
            "versionId": DEVICE_CONFIG["versionId"],
        }
        sign_content = generate_sign_content(sign_params)
        sign = rsa_sign(sign_content)
        
        url_params = self.get_base_params()
        url_params["p35"] = encrypted_des_key
        url = f"{API_LOGIN}?{urlencode(url_params)}"
        
        post_data = {
            "smboxid": encrypted_des_key,
            "versionId": DEVICE_CONFIG["versionId"],
            "device": DEVICE_CONFIG["device"],
            "userName": url_params.get("usr", ""),
            "imei": self.imei,
            "sign": sign,
            "timestamp": timestamp,
            "pInfo": pInfo,
            "phone": encrypted_phone,
            "utdId": self.p1 or "",
            "loginSource": "我的_马上登录",
            "channelId": DEVICE_CONFIG["channelId"],
        }
        
        try:
            response = self.session.post(url, data=post_data, timeout=30)
            result = response.json()
            
            if result.get("code") == 0:
                body = result.get("body", {})
                self.kt = body.get("token", "") or body.get("kt", "")
                self.p1 = body.get("utdId", "") or body.get("signUser", "") or body.get("p1", "")
                self.usr = body.get("userName", "") or body.get("usr", "")
                self.ku = body.get("signUser", "") or body.get("ku", "") or self.usr
                self.p35 = encrypted_des_key
                return True, body, "登录成功"
            else:
                return False, None, result.get('msg', '未知错误')
        except Exception as e:
            return False, None, str(e)
    
    def generate_welfare_url(self):
        """生成刷币脚本所需的完整URL"""
        if not self.kt:
            return ""
        
        params = {
            "zyeid": self.zyeid,
            "rgt": DEVICE_CONFIG["rgt"],
            "p1": self.p1,
            "kt": self.kt,
            "source": "welfare",
            "showContentInStatusBar": "1",
            "ecpmMix": "0.0",
            "ecpmVideo": "0.0",
            "mcTacid": "",
            "pc": DEVICE_CONFIG["pc"],
            "p2": DEVICE_CONFIG["p2"],
            "p3": DEVICE_CONFIG["p3"],
            "p4": DEVICE_CONFIG["p4"],
            "p5": DEVICE_CONFIG["p5"],
            "p7": self.p7,
            "p9": DEVICE_CONFIG["p9"],
            "p12": "",
            "p16": DEVICE_CONFIG["p16"],
            "p21": DEVICE_CONFIG["p21"],
            "p22": DEVICE_CONFIG["p22"],
            "p25": DEVICE_CONFIG["p25"],
            "p26": DEVICE_CONFIG["p26"],
            "p28": self.p28,
            "p29": DEVICE_CONFIG["p29"],
            "p30": "",
            "p31": self.p7,
            "p33": DEVICE_CONFIG["p33"],
            "p34": DEVICE_CONFIG["p34"],
            "p36": DEVICE_CONFIG["p36"],
            "firm": DEVICE_CONFIG["firm"],
            "d1": DEVICE_CONFIG["d1"],
            "pca": "channel-visit",
            "p35": self.p35,
            "usr": self.ku,  # usr 应该使用加密值，和 ku 相同
            "ku": self.ku,
        }
        
        base_url = "https://welfare-user.palmestore.com/sukanread/welfare-package/sudu/welfare.html"
        return f"{base_url}?{urlencode(params)}"


# ===================== 【青龙操作】=====================
def get_ql_token(host, client_id, client_secret):
    """获取青龙token"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        resp = requests.get(url, timeout=10).json()
        if resp.get('code') == 200:
            return resp['data']['token']
        return None
    except:
        return None


def update_ql_env(phone, account_info):
    """更新青龙环境变量"""
    welfare_url = account_info.get('welfare_url', '')
    if not welfare_url:
        return False
    
    qlconfig = middleware.bucketGet('s_sukan', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        osname = middleware.bucketGet('s_sukan', 'osname') or 'S_SUKAN'
        auth_time = middleware.bucketGet('s_sukan_auth', phone) or '未授权'
        
        # 查找现有环境变量
        envs = requests.get(
            f'{host}/open/envs?searchValue={phone[:7]}',
            headers=headers, timeout=10
        ).json().get('data', [])
        env_id = next((e.get('id') for e in envs if e['name'] == osname and phone in e.get('remarks', '')), None)
        
        env_data = {
            'name': osname,
            'value': welfare_url,
            'remarks': f"速看：{phone}|到期:{auth_time}"
        }
        
        if env_id:
            env_data['id'] = env_id
            requests.put(f'{host}/open/envs', headers=headers, json=env_data, timeout=10)
            requests.put(f'{host}/open/envs/enable', headers=headers, json=[env_id], timeout=10)
        else:
            resp = requests.post(f'{host}/open/envs', headers=headers, json=[env_data], timeout=10).json()
            if resp.get('data'):
                new_id = resp['data'][0].get('_id') or resp['data'][0].get('id')
                if new_id:
                    requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id], timeout=10)
        return True
    except:
        return False


def delete_ql_env(phone):
    """删除青龙环境变量"""
    qlconfig = middleware.bucketGet('s_sukan', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        osname = middleware.bucketGet('s_sukan', 'osname') or 'S_SUKAN'
        envs = requests.get(f'{host}/open/envs', headers=headers, timeout=10).json().get('data', [])
        
        for env in envs:
            if env['name'] == osname and phone in env.get('remarks', ''):
                env_id = env.get('_id') or env.get('id')
                requests.delete(f'{host}/open/envs', headers=headers, json=[env_id], timeout=10)
                return True
        return False
    except:
        return False


# ===================== 【二维码生成】=====================
def generate_qrcode(url):
    """生成二维码图片"""
    QRCODE_API_URL = "https://qrcode.vorto.cn/api/qrcode/generate"
    QRCODE_API_KEY = "4jpC3Cgd0zA7Z3HTJ6aDfW9QjtzitDGI"
    
    try:
        response = requests.post(
            QRCODE_API_URL,
            json={"content": url},
            headers={"X-API-Key": QRCODE_API_KEY},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data', {}).get('url'):
                return result['data']['url']
    except:
        pass
    
    # 备用接口
    try:
        encoded_url = requests.utils.quote(url)
        return f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
    except:
        return None


# ===================== 【登录函数】=====================
def bind_account():
    """绑定账号"""
    if not CRYPTO_AVAILABLE:
        sender.reply(
            "=====环境错误=====\n"
            "❌ 缺少加密库\n"
            "💡 请安装: pip install pycryptodome\n"
            "=================="
        )
        return

    sender.reply(
        "=====速看登录=====\n"
        "[1] 短信登录\n"
        "[2] URL登录\n"
        "------------------\n"
        "URL格式: url#手机号\n"
        "回复\"q\"退出操作\n"
        "=================="
    )
    login_type = sender.input(120000, 1, False)
    if not login_type:
        sender.reply("⏰ 操作超时")
        return
    if login_type.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    # URL登录：格式 url#手机号（青龙仅提交原始url，手机号仅作为账号标识）
    if login_type.strip() == '2':
        sender.reply(
            "=====URL登录=====\n"
            "请输入: url#手机号\n"
            "示例: https://welfare-user.xxx/welfare.html?...#13800138000\n"
            "------------------\n"
            "回复\"q\"退出操作\n"
            "=================="
        )
        raw_input = sender.input(120000, 1, False)
        if not raw_input:
            sender.reply("⏰ 操作超时")
            return
        if raw_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return

        raw_input = raw_input.strip()
        if '#' not in raw_input:
            sender.reply("❌ 格式错误，请按 url#手机号 输入")
            return

        welfare_url, phone = raw_input.rsplit('#', 1)
        welfare_url = welfare_url.strip()
        phone = phone.strip()

        parsed = urlparse(welfare_url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            sender.reply("❌ URL格式错误，请输入完整http/https链接")
            return

        if not phone.isdigit() or len(phone) != 11:
            sender.reply("❌ 手机号格式错误，请输入11位手机号")
            return

        # 保存账号到用户列表
        current_value = middleware.bucketGet('s_sukan_user', userid)
        if not current_value:
            middleware.bucketSet('s_sukan_user', userid, str([phone]))
        else:
            accounts = eval(current_value)
            if phone not in accounts:
                accounts.append(phone)
                middleware.bucketSet('s_sukan_user', userid, str(accounts))

        # 保存账号信息（URL原样保存，手机号仅做账号标识）
        account_info = {
            "phone": phone,
            "welfare_url": welfare_url,
            "kt": "",
            "p1": "",
            "usr": "",
            "ku": "",
            "zyeid": "",
            "p7": "",
            "p28": "",
            "p35": "",
            "login_type": "url",
            "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        middleware.bucketSet('s_sukan_token', phone, json.dumps(account_info))

        sender.reply(f"✅ {mask_account(phone)} URL登录成功")

        # 检查授权状态
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_sukan_auth', phone)
        if accountVip and accountVip > dqsj:
            sender.reply(f"📱 已授权，到期: {accountVip}")
            update_ql_env(phone, account_info)
        else:
            sender.reply("📋 账号需要授权")
            authorize_multiple_accounts([phone])
        return

    if login_type.strip() != '1':
        sender.reply("❌ 无效选择")
        return

    sender.reply(
        "=====速看登录=====\n"
        "📱 请输入手机号:\n"
        "------------------\n"
        "回复\"q\"退出操作\n"
        "=================="
    )
    phone = sender.input(120000, 1, False)
    if not phone:
        sender.reply("⏰ 操作超时")
        return
    if phone.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    phone = phone.strip()
    if not phone.isdigit() or len(phone) != 11:
        sender.reply("❌ 手机号格式错误，请输入11位手机号")
        return
    
    # 发送验证码
    api = SukanAPI()
    sender.reply(f"🔄 正在发送验证码到 {mask_account(phone)}...")
    
    success, msg = api.send_sms(phone)
    if not success:
        sender.reply(f"❌ 发送验证码失败: {msg}")
        return
    
    sender.reply(
        f"✅ 验证码已发送\n"
        f"📱 请输入验证码:\n"
        f"------------------\n"
        f"回复\"q\"退出操作\n"
        f"=================="
    )
    code = sender.input(120000, 1, False)
    if not code:
        sender.reply("⏰ 操作超时")
        return
    if code.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    code = code.strip()
    sender.reply("🔄 正在登录...")
    
    success, body, msg = api.login(phone, code)
    if not success:
        sender.reply(f"❌ 登录失败: {msg}")
        return
    
    # 生成URL
    welfare_url = api.generate_welfare_url()
    if not welfare_url:
        sender.reply("❌ 生成URL失败")
        return
    
    # 保存账号到用户列表
    current_value = middleware.bucketGet('s_sukan_user', userid)
    if not current_value:
        middleware.bucketSet('s_sukan_user', userid, str([phone]))
    else:
        accounts = eval(current_value)
        if phone not in accounts:
            accounts.append(phone)
            middleware.bucketSet('s_sukan_user', userid, str(accounts))
    
    # 保存账号信息
    account_info = {
        "phone": phone,
        "welfare_url": welfare_url,
        "kt": api.kt,
        "p1": api.p1,
        "usr": api.usr,
        "ku": api.ku,
        "zyeid": api.zyeid,
        "p7": api.p7,
        "p28": api.p28,
        "p35": api.p35,
        "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    middleware.bucketSet('s_sukan_token', phone, json.dumps(account_info))
    
    sender.reply(f"✅ {mask_account(phone)} 登录成功")
    
    # 检查授权状态
    dqsj = datetime.now().strftime("%Y-%m-%d")
    accountVip = middleware.bucketGet('s_sukan_auth', phone)
    if accountVip and accountVip > dqsj:
        sender.reply(f"📱 已授权，到期: {accountVip}")
        update_ql_env(phone, account_info)
    else:
        sender.reply("📋 账号需要授权")
        authorize_multiple_accounts([phone])


# ===================== 【查询函数】=====================
def query_accounts():
    """查询账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 速看登录 绑定\n==================")
        return
    
    accounts = eval(uservalue)
    
    # 显示账号选择列表
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, phone in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_sukan_auth', phone)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(phone)}({auth_status})"
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
        
        for i, phone in enumerate(selected, 1):
            try:
                account_info = json.loads(middleware.bucketGet('s_sukan_token', phone) or '{}')
                auth_time = middleware.bucketGet('s_sukan_auth', phone)
                if auth_time and auth_time >= str(datetime.now().date()):
                    auth_status = '已授权'
                else:
                    auth_status = '未授权'
                
                login_time = account_info.get('login_time', '未知')
                
                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 账号: {mask_account(phone)}\n"
                    f"🏷 状态: {auth_status}\n"
                    f"📅 到期: {auth_time or '未授权'}\n"
                    f"🕐 登录: {login_time}\n"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"=====查询失败=====\n❌ 错误: {str(e)}\n==================")
        
        sender.reply(f"✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


# ===================== 【管理函数】=====================
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
    
    # 显示账号列表供选择
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, phone in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_sukan_auth', phone)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(phone)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    # 解析选择的账号
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
    
    # 执行操作
    if choice == '1':
        authorize_multiple_accounts(selected)
    elif choice == '2':
        sender.reply("=====确认删除=====\n⚠️ 此操作不可恢复\n回复 y 确认删除\n==================")
        if sender.input(120000, 1, False).lower() == 'y':
            for phone in selected:
                if phone in accounts:
                    accounts.remove(phone)
                middleware.bucketDel('s_sukan_token', phone)
                middleware.bucketDel('s_sukan_auth', phone)
                delete_ql_env(phone)
            
            if accounts:
                middleware.bucketSet('s_sukan_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_sukan_user', userid)
            sender.reply(f"✅ 已删除 {len(selected)} 个账号")
        else:
            sender.reply("✅ 已取消")
    elif choice == '3':
        success = 0
        for phone in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_sukan_token', phone))
                auth_time = middleware.bucketGet('s_sukan_auth', phone)
                if auth_time and auth_time >= str(datetime.now().date()):
                    if update_ql_env(phone, account_info):
                        success += 1
            except:
                pass
        sender.reply(
            f"=====提交结果=====\n"
            f"✅ 成功: {success}个\n"
            f"❌ 失败: {len(selected) - success}个\n"
            f"=================="
        )


# ===================== 【授权功能】=====================
def process_authorization(phone, account_info, months):
    """处理授权"""
    try:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_sukan_auth', phone)
        if accountVip and accountVip > dqsj:
            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        new_expire = (start_date + timedelta(days=30 * months)).strftime("%Y-%m-%d")
        middleware.bucketSet('s_sukan_auth', phone, new_expire)
        update_ql_env(phone, account_info)
        
        sender.reply(
            f"=====授权成功=====\n"
            f"📱 账号: {mask_account(phone)}\n"
            f"📅 到期: {new_expire}\n"
            f"=================="
        )
        return True
    except Exception as e:
        sender.reply(f"授权异常: {str(e)}")
        return False


def authorize_multiple_accounts(phones):
    """批量授权账号"""
    account_infos = []
    for phone in phones:
        try:
            account_infos.append({
                'phone': phone,
                'info': json.loads(middleware.bucketGet('s_sukan_token', phone))
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
        
        Vipmoney = float(middleware.bucketGet('s_sukan', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_sukan', 'coin') or '0')
        
        # 构建可用支付方式
        available = []
        ma_pay_switch = middleware.bucketGet('s_sukan', 'ma_pay_switch') or 'false'
        if ma_pay_switch.lower() == 'true' and middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'):
            for pt in (middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay').split(','):
                available.append((PAY_TYPE_NAMES.get(pt.strip(), pt.strip()), f"mapay_{pt.strip()}"))
        elif middleware.bucketGet('s_sukan', 'zsm'):
            available.append(("微信支付", "wxpay"))
        
        if coin > 0:
            available.append(("积分兑换", "coin"))
        
        if not available:
            sender.reply("❌ 未配置支付方式")
            return
        
        # 选择支付方式
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
        
        # 执行支付
        if payment_type == 'coin':
            for acc in account_infos:
                process_coin_payment(acc['phone'], acc['info'], months, coin)
        elif payment_type == 'wxpay':
            if pay_order(PLUGIN_CONFIG['name'], months, total_money):
                for acc in account_infos:
                    process_authorization(acc['phone'], acc['info'], months)
        elif payment_type.startswith('mapay_'):
            pay_type = payment_type.replace('mapay_', '')
            if handle_mapay_order(PLUGIN_CONFIG['name'], months, total_money, pay_type):
                for acc in account_infos:
                    process_authorization(acc['phone'], acc['info'], months)
    except ValueError:
        sender.reply("❌ 请输入有效数字")


# ===================== 【支付功能】=====================
def process_coin_payment(phone, account_info, months, coin):
    """积分支付"""
    try:
        required = months * coin
        user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
        
        if user_coins < required:
            sender.reply(
                f"=====积分不足=====\n"
                f"❌ 当前: {user_coins}\n"
                f"💰 需要: {required}\n"
                f"=================="
            )
            return False
        
        middleware.bucketSet('dd_sign_points', userid, str(user_coins - required))
        if process_authorization(phone, account_info, months):
            sender.reply(
                f"=====积分兑换成功=====\n"
                f"✅ 扣除: {required}\n"
                f"💰 剩余: {user_coins - required}\n"
                f"=================="
            )
            return True
        
        # 授权失败则退还积分
        middleware.bucketSet('dd_sign_points', userid, str(user_coins))
        return False
    except Exception as e:
        sender.reply(f"积分兑换异常: {str(e)}")
        return False


def pay_order(project, months, money):
    """收款码支付"""
    if float(money) == 0:
        return True
    
    zsm = middleware.bucketGet('s_sukan', 'zsm')
    if not zsm:
        sender.reply('❌ 未配置收款码')
        return False
    
    sender.reply(
        f"=====微信扫码支付====\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)
    
    ddzf = sender.waitPay("q", 100000)
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


def handle_mapay_order(project, months, money, pay_type=None):
    """码支付订单"""
    config = {
        'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
        'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
        'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
        'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or '',
        'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or ''
    }
    
    if not (config['gateway'] and config['pid'] and config['key']):
        sender.reply('❌ 码支付配置不完整')
        return False
    
    amount = round(float(money), 2)
    out_trade_no = f"SUKAN{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
    selected_type = pay_type or 'alipay'
    
    # 构建签名参数
    params = {
        'pid': config['pid'],
        'type': selected_type,
        'out_trade_no': out_trade_no,
        'notify_url': config['notify_url'],
        'return_url': config['return_url'],
        'name': f"{project}-{amount}",
        'money': str(amount),
        'param': userid
    }
    params = {k: v for k, v in params.items() if v}
    sign_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    params['sign'] = hashlib.md5((sign_str + config['key']).encode()).hexdigest().lower()
    params['sign_type'] = 'MD5'
    
    try:
        resp = requests.post(f"{config['gateway'].rstrip('/')}/mapi.php", data=params, timeout=10).json()
        if resp.get('code') != 1:
            sender.reply(f'❌ 创建订单失败: {resp.get("msg")}')
            return False
        
        trade_no = resp.get('trade_no')
        pay_url = f"{config['gateway'].rstrip('/')}/pay/{trade_no}"
        sender.reply(f'请使用【{PAY_TYPE_NAMES.get(selected_type, selected_type)}】扫描二维码完成支付:')
        qrcode_url = generate_qrcode(pay_url)
        if qrcode_url:
            sender.replyImage(qrcode_url)
        sender.reply('输入"q"可取消')
        
        # 轮询支付结果
        for _ in range(30):
            qresp = requests.get(
                f"{config['gateway'].rstrip('/')}/xpay/epay/api.php",
                params={'act': 'order', 'pid': config['pid'], 'key': config['key'], 'out_trade_no': out_trade_no},
                timeout=10
            ).json()
            if qresp.get('code') == 1 and qresp.get('status') == 1:
                return True
            if sender.listen(5000) == 'q':
                sender.reply("✅ 已取消")
                return False
        
        sender.reply("❌ 支付超时")
        return False
    except Exception as e:
        sender.reply(f'❌ 支付异常: {str(e)}')
        return False


# ===================== 【检测与清理】=====================
def check_auth_status():
    """检测授权状态"""
    notify = middleware.bucketGet('s_sukan', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"
    
    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_sukan_user')
    if not all_users:
        return "❌ 没有用户"
    
    notify_days = int(middleware.bucketGet('s_sukan', 'notify_days') or '3')
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0
    
    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_sukan_user', user_id) or '[]')
            to_notify = []
            to_clean = []
            
            for acc in accounts:
                auth_time_str = middleware.bucketGet('s_sukan_auth', acc)
                
                if not auth_time_str:
                    to_clean.append({'phone': acc, 'auth_time': '未授权', 'days_left': 0})
                    continue
                
                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days
                    
                    if days_left <= 0:
                        to_clean.append({'phone': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        to_notify.append({'phone': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                except:
                    to_clean.append({'phone': acc, 'auth_time': auth_time_str, 'days_left': 0})
            
            total += len(accounts)
            
            # 处理需要清理的账号
            if to_clean:
                for exp_acc in to_clean:
                    phone = exp_acc['phone']
                    delete_ql_env(phone)
                    middleware.bucketDel('s_sukan_token', phone)
                    if phone in accounts:
                        accounts.remove(phone)
                    middleware.bucketDel('s_sukan_auth', phone)
                    cleaned += 1
                
                if accounts:
                    middleware.bucketSet('s_sukan_user', user_id, str(accounts))
                else:
                    middleware.bucketDel('s_sukan_user', user_id)
            
            # 处理需要提醒的账号
            if to_notify:
                notify_list = "\n".join([
                    f"📱 {mask_account(a['phone'])} 剩余{a['days_left']}天({a['auth_time']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====速看账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"速看管理\"续费\n"
                    f"=================="
                )
                for ch in channels:
                    try:
                        middleware.push(imType=ch, groupCode='', userID=user_id, title="", content=msg)
                        notified += 1
                    except:
                        pass
        except:
            pass
    
    return f"✅ 检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"


# ===================== 【管理员功能】=====================
def calculate_auth_time_by_days(phone, days):
    """按天数计算授权时间"""
    try:
        current_auth = middleware.bucketGet('s_sukan_auth', phone)
        
        if current_auth and datetime.strptime(current_auth, "%Y-%m-%d").date() > datetime.now().date():
            base_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
        else:
            base_date = datetime.now().date()
        
        new_date = base_date + timedelta(days=int(days))
        return str(new_date)
    
    except Exception as e:
        raise Exception(f"计算授权时间失败: {str(e)}")


def ks_auth():
    """管理员授权（按天数）"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return
    
    sender.reply(
        "=====管理员授权=====\n"
        "[1] 批量授权所有用户\n"
        "[2] 单独授权指定用户\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    if choice == '1':
        # 批量授权所有用户
        all_users = [
            {'id': k, 'accounts': eval(middleware.bucketGet('s_sukan_user', k) or '[]')}
            for k in middleware.bucketAllKeys('s_sukan_user')
        ]
        if not all_users:
            sender.reply("❌ 无用户")
            return
        
        total_accs = sum(len(u['accounts']) for u in all_users)
        sender.reply(
            f"=====批量授权=====\n"
            f"👥 用户数: {len(all_users)}\n"
            f"📊 账号数: {total_accs}\n"
            f"请输入授权天数(正数增加/负数减少):\n"
            f"=================="
        )
        
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        try:
            days = int(days_input)
            action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
            
            sender.reply(
                f"=====确认授权=====\n"
                f"👥 用户数: {len(all_users)}\n"
                f"📊 账号数: {total_accs}\n"
                f"⏰ 操作: {action_text}\n"
                f"回复\"y\"确认\n"
                f"=================="
            )
            
            if sender.input(120000, 1, False).lower() != 'y':
                sender.reply("✅ 已取消")
                return
            
            success = 0
            fail = 0
            for u in all_users:
                for acc in u['accounts']:
                    try:
                        info = json.loads(middleware.bucketGet('s_sukan_token', acc))
                        new_auth_time = calculate_auth_time_by_days(acc, days)
                        middleware.bucketSet('s_sukan_auth', acc, new_auth_time)
                        update_ql_env(acc, info)
                        success += 1
                    except:
                        fail += 1
            
            sender.reply(
                f"=====授权结果=====\n"
                f"✅ 成功: {success} 个账号\n"
                f"❌ 失败: {fail} 个账号\n"
                f"⏰ 操作: {action_text}\n"
                f"=================="
            )
        except ValueError:
            sender.reply("❌ 无效的天数")
            return
    
    elif choice == '2':
        # 单独授权指定用户
        sender.reply(
            "=====按用户授权=====\n"
            "请输入用户ID:\n"
            "回复\"q\"退出"
        )
        
        target_id = sender.input(120000, 1, False)
        if not target_id or target_id.lower() == 'q':
            sender.reply("✅ 已退出")
            return
        
        accounts = eval(middleware.bucketGet('s_sukan_user', target_id) or '[]')
        if not accounts:
            sender.reply(f"❌ 用户 {target_id} 没有绑定任何账号")
            return
        
        account_list = f"=====用户 {target_id} 的账号=====\n[0] 选择全部账号\n"
        for i, acc in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_sukan_auth', acc) or '未授权'
            account_list += f"[{i}] {mask_account(acc)} - {auth_time}\n"
        account_list += "------------------\n支持多选，用逗号分隔\n回复\"q\"退出"
        sender.reply(account_list)
        
        account_choice = sender.input(120000, 1, False)
        if not account_choice or account_choice.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        selected = []
        if account_choice == '0':
            selected = accounts.copy()
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in account_choice.split(',') if idx.strip().isdigit()]
                for index in indices:
                    if 0 <= index < len(accounts):
                        selected.append(accounts[index])
            except:
                sender.reply("❌ 无效的选择格式")
                return
        
        if not selected:
            sender.reply("❌ 未选择任何账号")
            return
        
        sender.reply(
            f"已选择 {len(selected)} 个账号\n"
            f"请输入授权天数:\n"
            f"(正数增加天数，负数减少天数)\n"
            f"回复\"q\"退出"
        )
        
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        try:
            days = int(days_input)
            action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
            
            success = 0
            fail = 0
            for acc in selected:
                try:
                    info = json.loads(middleware.bucketGet('s_sukan_token', acc))
                    new_auth_time = calculate_auth_time_by_days(acc, days)
                    middleware.bucketSet('s_sukan_auth', acc, new_auth_time)
                    update_ql_env(acc, info)
                    success += 1
                except:
                    fail += 1
            
            sender.reply(
                f"=====授权结果=====\n"
                f"✅ 成功: {success} 个账号\n"
                f"❌ 失败: {fail} 个账号\n"
                f"⏰ 操作: {action_text}\n"
                f"=================="
            )
        except ValueError:
            sender.reply("❌ 无效的天数")


# ===================== 【教程函数】=====================
def show_tutorial():
    """显示插件使用教程"""
    tutorial = """
=====速看免费小说教程=====
📱 用户指令:
• 速看登录 - 绑定账号(短信登录或URL登录)
• 速看查询 - 查询账号状态
• 速看管理 - 授权/删除/提交青龙
• 速看教程 - 查看本教程
------------------
🔧 管理员指令:
• 速看授权 - 管理员按天数授权
• 速看检测 - 检测过期账号并清理
------------------
💡 登录说明:
📝 支持短信登录(手机号+验证码)
📝 支持URL登录，格式: url#手机号
📝 登录成功后生成刷币所需的URL
📝 URL登录时青龙变量仅提交url原文不变
📝 授权后自动提交到青龙容器
------------------
🔧 青龙配置:
📡 变量名: S_SUKAN (可自定义)
📡 容器: Host丨ClientID丨Secret
📡 脚本会在青龙定时执行刷币任务
==================
"""
    sender.reply(tutorial.strip())


# ===================== 【主入口】=====================
def main():
    """主入口"""
    msg = sender.getMessage()
    
    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('速看' in msg or 'sk' in msg.lower() or 'sukan' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('速看' in msg or 'sk' in msg.lower() or 'sukan' in msg.lower()):
        manage_account()
    elif '教程' in msg and ('速看' in msg or 'sk' in msg.lower() or 'sukan' in msg.lower()):
        show_tutorial()
    elif '速看授权' in msg or 'sk授权' in msg.lower() or 'sukan授权' in msg.lower():
        ks_auth()
    elif '速看检测' in msg or 'sk检测' in msg.lower() or 'sukan检测' in msg.lower():
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    # 定时任务
    elif sender.getImtype() == 'fake':
        try:
            middleware.notifyMasters(check_auth_status())
        except:
            pass
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
