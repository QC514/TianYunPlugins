# -*- coding: utf-8 -*-
# [rule: ^(速看)(登录|登陆)$|^登(录|陆)(速看)$|^(速看)(查询|管理)$|^(查询|管理)(速看)$|^速看清理$|^速看授权$|^速看教程$|^清理速看$|^速看广播 ?(.*)$|^速看通知 ?(.*)$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 56 9,19 * * *]
# [public: true]
# [title: 速看小说带短信]
# [open_source: false]
# [class: 工具类]
# [version: 3.6]
# [price: 28.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 速看小说代挂提交插件，支持抓包完整URL整段提交和短信登录<br>1. 严格执行整段提交：用户发送的完整URL直接存入青龙，不进行任何参数分割或重组。<br>2. 修复因缺失签名参数导致的脚本运行失败问题。<br> 3.购插件送脚本，脚本在售后群1003974618。<br>]

import re
import ast
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal
import requests
import time
import json
import hashlib
import logging
import base64
import ssl
import warnings
import random
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('su_kan')

# 请求超时配置
REQUEST_TIMEOUT = 30  # 常规请求超时

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

SK_DEVICE_CONFIG = {
    "device": "V2359A",
    "firm": "vivo",
    "channelId": "801002",
    "versionId": "80002056",
    "p2": "801002",
    "p3": "80002056",
    "p4": "501656",
    "p5": "19",
    "p9": "0",
    "p16": "V2359A",
    "p21": "99",
    "p22": "14",
    "p25": "80002056",
    "p26": "34",
    "p29": "zycb1bdb",
    "p33": "com.chaozh.xincao.only.sk",
    "p34": "vivo",
    "p36": "a",
    "d1": "8.0.2",
    "pc": "10",
    "rgt": "7",
}

SK_SMS_DEVICE_CONFIG = {
    "device": "Redmi Note 11",
    "firm": "Xiaomi",
    "channelId": "731001",
    "versionId": "101200017",
    "p2": "731001",
    "p3": "101200017",
    "p4": "501617",
    "p5": "16",
    "p9": "2",
    "p16": "Redmi Note 11",
    "p21": "3",
    "p22": "11",
    "p25": "12030",
    "p26": "36",
    "p29": "zya3c0e0",
    "p33": "com.zhangyue.app.shortplay.kakandj",
    "p34": "navigationbar_is_min",
    "p36": "a",
    "d1": "8.0.2",
    "pc": "10",
    "rgt": "7",
}

SK_DEVICE_PROFILES = [
    dict(SK_DEVICE_CONFIG),
    {
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
    },
    {
        "device": "M2007J3SC",
        "firm": "Xiaomi",
        "channelId": "801004",
        "versionId": "80002056",
        "p2": "801004",
        "p3": "80002056",
        "p4": "501656",
        "p5": "19",
        "p9": "0",
        "p16": "M2007J3SC",
        "p21": "99",
        "p22": "12",
        "p25": "80002056",
        "p26": "34",
        "p29": "zycb1bdb",
        "p33": "com.chaozh.xincao.only.sk",
        "p34": "Xiaomi",
        "p36": "a",
        "d1": "8.0.2",
        "pc": "10",
        "rgt": "7",
    },
]

SK_SMS_DEVICE_PROFILES = [
    dict(SK_SMS_DEVICE_CONFIG),
]

SK_API_BASE = "https://dj.palmestore.com"
SK_API_SEND_SMS = f"{SK_API_BASE}/dj_user/out/sms/sendSms/V2"
SK_API_LOGIN = f"{SK_API_BASE}/dj_user/out/login/loginByPhoneV3"

senderID = middleware.getSenderID()
# 创建发送者
sender = middleware.Sender(senderID)
# 获取发送者QQ号
userid = sender.getUserID()
# 获取用户的消息内容（提前获取）
usermessage = sender.getMessage()  # 这里提前获取

_RUNTIME_BUCKET = "plugin_push_runtime"
_RUNTIME_KEY = "速看"
try:
    current_imtype = str(sender.getImtype() or "")
except:
    current_imtype = ""
if current_imtype and current_imtype.lower() not in ["fake", "cron"]:
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_sender", str(senderID))
    except: pass
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype", current_imtype)
    except: pass


# [param: {"required":true,"key":"dd_sk.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_sk.dd_sk_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接系统","desc":"你的变量需要添加到的系统容器？参数用丨分割，这个符号是中文的竖(直接复制)"}]
# [param: {"required":true,"key":"dd_sk.dd_sk_osname","bool":false,"placeholder":"必填项,例:S_SUKAN","name":"提交到系统的变量名","desc":"系统容器内速看的变量名(默认为S_SUKAN)"}]
# [param: {"required":true,"key":"dd_sk.skVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_sk.skcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"dd_sk.show_point_status","bool":true,"placeholder":"","name":"显示积分状态","desc":"是否在查询结果中显示积分状态判断"}]
# [param: {"required":true,"key":"dd_sk.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# [param: {"required":false,"key":"dd_sk.epay_alipay","bool":true,"name":"易支付支付宝","desc":"启用易支付支付宝通道收款"}]
# [param: {"required":false,"key":"dd_sk.epay_wxpay","bool":true,"name":"易支付微信","desc":"启用易支付微信通道收款"}]
# [param: {"required":false,"key":"dd_sk.epay_qqpay","bool":true,"name":"易支付QQ","desc":"启用易支付QQ通道收款"}]
# [param: {"required":false,"key":"dd_sk.epay_url","bool":false,"placeholder":"如 http://pay.xxx.com/","name":"易支付网关","desc":"易支付接口网关地址(需带http及结尾/)"}]
# [param: {"required":false,"key":"dd_sk.epay_pid","bool":false,"placeholder":"","name":"易支付商户ID","desc":"易支付的PID"}]
# [param: {"required":false,"key":"dd_sk.epay_key","bool":false,"placeholder":"","name":"易支付商户密钥","desc":"易支付的KEY密钥"}]
# [param: {"required":true,"key":"dd_sk.enable_proxy","bool":true,"placeholder":"True/False","name":"是否启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_sk.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_sk.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称，默认dd_sign_points"}]
# [param: {"required":true,"key":"dd_sk.enable_remark","bool":true,"placeholder":"True/False","name":"启用备注功能","desc":"是否启用账号备注功能，启用后用户可以为账号设置备注名"}]
# [param: {"required":true,"key":"dd_sk.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知（建议设置2天，用户不续费到期自动清理）"}]

def getusercontent():
    """获取插件完整配置"""
    # 这里的 bucket 全部替换为 dd_sk 开头，实现数据隔离
    dd_sk_osname = middleware.bucketGet('dd_sk', 'dd_sk_osname') or 'S_SUKAN'
    dd_sk_qlname = middleware.bucketGet('dd_sk', 'dd_sk_qlname') or ''
    dd_managecommand = middleware.bucketGet('dd_sk', 'dd_managecommand') or '速看管理'
    dd_querycommand = middleware.bucketGet('dd_sk', 'dd_querycommand') or '速看查询'
    dd_signcommand = middleware.bucketGet('dd_sk', 'dd_signcommand') or '速看登录'
    zsm = middleware.bucketGet('dd_sk', 'zsm') or ''
    
    # 获取代理配置
    enable_proxy = middleware.bucketGet('dd_sk', 'enable_proxy') or 'false'
    enable_proxy = enable_proxy.lower() == 'true'
    proxy_pool_url = middleware.bucketGet('dd_sk', 'proxy_pool_url') or ''
    
    # 获取积分桶配置
    points_bucket = middleware.bucketGet('dd_sk', 'points_bucket') or 'dd_sign_points'
    
    # 获取备注功能配置
    enable_remark = middleware.bucketGet('dd_sk', 'enable_remark') or 'false'
    enable_remark = enable_remark.lower() == 'true'
    
    # 生成随机指令
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    # 获取价格配置
    try:
        skVipmoney = Decimal(middleware.bucketGet('dd_sk', 'skVipmoney') or '1')
    except:
        skVipmoney = Decimal('1')
        
    try:
        skcoin = int(middleware.bucketGet('dd_sk', 'skcoin') or '0')
    except:
        skcoin = 0
    
    # 获取是否显示积分状态的配置
    show_point_status = middleware.bucketGet('dd_sk', 'show_point_status') or 'false'
    show_point_status = show_point_status.lower() == 'true'
    
    # 获取是否使用码支付的配置
    use_ma_pay = middleware.bucketGet('dd_sk', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'

    epay_url = middleware.bucketGet('dd_sk', 'epay_url') or ''
    epay_pid = middleware.bucketGet('dd_sk', 'epay_pid') or ''
    epay_key = middleware.bucketGet('dd_sk', 'epay_key') or ''
    epay_alipay = (middleware.bucketGet('dd_sk', 'epay_alipay') or 'true').lower() == 'true'
    epay_wxpay = (middleware.bucketGet('dd_sk', 'epay_wxpay') or 'false').lower() == 'true'
    epay_qqpay = (middleware.bucketGet('dd_sk', 'epay_qqpay') or 'false').lower() == 'true'
    
    # 获取提醒天数配置
    try:
        reminder_days = int(middleware.bucketGet('dd_sk', 'reminder_days') or '2')
    except:
        reminder_days = 2

    # 验证必要配置
    if not dd_sk_qlname:
        sender.reply("❌ 对接系统配置未设置")
        exit(0)
    
    if not dd_sk_osname:
        sender.reply("❌ 变量名称未设置")
        exit(0)
    
    return {
        'dd_sk_osname': dd_sk_osname,
        'dd_sk_qlname': dd_sk_qlname,
        'dd_managecommand': dd_managecommand,
        'dd_querycommand': dd_querycommand,
        'dd_signcommand': dd_signcommand,
        'randommanagecommand': randommanagecommand,
        'randomquerycommand': randomquerycommand,
        'randomsigncommand': randomsigncommand,
        'zsm': zsm,
        'enable_proxy': enable_proxy,
        'proxy_pool_url': proxy_pool_url,
        'points_bucket': points_bucket,
        'enable_remark': enable_remark,
        'skVipmoney': skVipmoney,
        'skcoin': skcoin,
        'show_point_status': show_point_status,
        'use_ma_pay': use_ma_pay,
        'epay_url': epay_url,
        'epay_pid': epay_pid,
        'epay_key': epay_key,
        'epay_alipay': epay_alipay,
        'epay_wxpay': epay_wxpay,
        'epay_qqpay': epay_qqpay,
        'reminder_days': reminder_days
    }

# 获取全局配置
config = getusercontent()

def get_owner_user_id(account, fallback_userid=None):
    account = str(account or "")
    try:
        if fallback_userid and account in [str(x) for x in AccountManager.get_accounts(str(fallback_userid))]:
            return str(fallback_userid)
    except:
        pass
    try:
        for frame_info in __import__('inspect').stack()[1:6]:
            local_vars = frame_info.frame.f_locals
            for key in ['owner_user_id', 'target_userid', 'target_qq', 'target_user', 'user', 'uid']:
                candidate = local_vars.get(key)
                if not candidate:
                    continue
                candidate = str(candidate)
                try:
                    if account in [str(x) for x in AccountManager.get_accounts(candidate)]:
                        return candidate
                except:
                    pass
    except:
        pass
    try:
        for owner in middleware.bucketAllKeys(bucket='dd_sk_user'):
            try:
                if account in [str(x) for x in AccountManager.get_accounts(owner)]:
                    return str(owner)
            except:
                pass
    except:
        pass
    try:
        if not sender.isAdmin() and str(userid):
            return str(userid)
    except:
        pass
    return 

def send_user_notice(user_id, msg, title="速看小说通知"):
    user_id = str(user_id or "").strip()
    if not user_id:
        return False
    imtype = ""
    try:
        imtype = str(sender.getImtype() or "")
    except:
        pass
    if not imtype or imtype.lower() in ["fake", "cron"]:
        imtype = middleware.bucketGet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype") or ""
    try:
        if imtype:
            middleware.Push(imtype, "", user_id, title, msg)
            return True
    except Exception as e:
        logger.warning(f"Push发送失败 {user_id}: {e}")
    return False

def safe_send_message(user_id, msg, log_context=""):
    ok = send_user_notice(user_id, msg)
    if not ok:
        logger.warning(f"消息发送失败 {log_context}")
    return ok


def extract_sukan_device_profile(full_data):
    try:
        text = str(full_data or "").strip()
        if not text:
            return {}
        query_str = text.split('?', 1)[1] if '?' in text else text
        params = dict(urllib.parse.parse_qsl(query_str))
        profile = {
            "device": params.get("p16") or params.get("device") or "",
            "firm": params.get("firm") or params.get("p34") or "",
            "channelId": params.get("p2") or "",
            "versionId": params.get("p3") or "",
            "p2": params.get("p2") or "",
            "p3": params.get("p3") or "",
            "p4": params.get("p4") or "",
            "p5": params.get("p5") or "",
            "p9": params.get("p9") or "",
            "p16": params.get("p16") or "",
            "p21": params.get("p21") or "",
            "p22": params.get("p22") or "",
            "p25": params.get("p25") or "",
            "p26": params.get("p26") or "",
            "p29": params.get("p29") or "",
            "p33": params.get("p33") or "",
            "p34": params.get("p34") or "",
            "p36": params.get("p36") or "",
            "d1": params.get("d1") or "",
            "pc": params.get("pc") or "",
            "rgt": params.get("rgt") or "",
        }
        return {k: v for k, v in profile.items() if str(v).strip()}
    except Exception as e:
        logger.warning(f"提取速看设备画像失败: {e}")
        return {}


def save_sukan_device_profile(full_data):
    profile = extract_sukan_device_profile(full_data)
    if not profile:
        return
    try:
        merged = dict(SK_DEVICE_CONFIG)
        merged.update(profile)
        middleware.bucketSet('dd_sk_runtime', 'sms_device_profile', json.dumps(merged, ensure_ascii=False))
        logger.info(f"已保存速看设备画像: {merged.get('device')} / {merged.get('channelId')}")
    except Exception as e:
        logger.warning(f"保存速看设备画像失败: {e}")


def is_sukan_sms_profile(profile):
    if not isinstance(profile, dict):
        return False
    return (
        profile.get("p2") == "731001"
        or profile.get("p3") == "101200017"
        or profile.get("p29") == "zya3c0e0"
        or profile.get("p33") == "com.zhangyue.app.shortplay.kakandj"
    )


def get_sukan_sms_device_profile():
    try:
        saved = middleware.bucketGet('dd_sk_runtime', 'sms_device_profile')
        data = safe_json_loads(saved, {})
        merged = dict(SK_SMS_DEVICE_CONFIG)
        if is_sukan_sms_profile(data):
            merged.update({k: v for k, v in data.items() if str(v).strip()})
        return merged
    except Exception:
        return dict(SK_SMS_DEVICE_CONFIG)


def get_sukan_sms_device_profiles():
    profiles = []
    learned = get_sukan_sms_device_profile()
    if learned:
        profiles.append(learned)
    for profile in SK_SMS_DEVICE_PROFILES:
        candidate = dict(profile)
        if not any(candidate == existing for existing in profiles):
            profiles.append(candidate)
    return profiles


def rsa_encrypt(data):
    if not CRYPTO_AVAILABLE:
        return ""
    key = RSA.import_key(RSA_PUBLIC_KEY)
    cipher = Cipher_PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def rsa_sign(data):
    if not CRYPTO_AVAILABLE:
        return ""
    key = RSA.import_key(RSA_PRIVATE_KEY)
    h = SHA.new(data.encode('utf-8'))
    signer = Signature_PKCS1_v1_5.new(key)
    signature = signer.sign(h)
    return base64.b64encode(signature).decode('utf-8')


def des_encrypt(data, key):
    if not CRYPTO_AVAILABLE:
        return ""
    key_bytes = key.encode('utf-8')[:8].ljust(8, b'\0')
    cipher = DES.new(key_bytes, DES.MODE_CBC, key_bytes)
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), DES.block_size))
    return base64.b64encode(encrypted).decode('utf-8')


def generate_des_key():
    return ''.join([str(random.randint(0, 9)) for _ in range(8)])


def generate_pinfo(phone, code):
    des_key = generate_des_key()
    encrypted_des_key = rsa_encrypt(des_key)
    data_json = json.dumps({"phone": phone, "pCode": code}, separators=(',', ':'))
    encrypted_data = des_encrypt(data_json, des_key)
    pinfo = json.dumps({
        "DesKey": encrypted_des_key,
        "Data": encrypted_data
    }, separators=(',', ':'))
    return pinfo, encrypted_des_key


def generate_sign_content(params):
    sorted_keys = sorted(params.keys())
    return "&".join([f"{k}={params[k]}" for k in sorted_keys if params[k] != ""])


class SukanSMSLoginAPI:
    def __init__(self):
        self.device_config = get_sukan_sms_device_profile()
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers.update({
            'User-Agent': f"Dalvik/2.1.0 (Linux; U; Android {self.device_config.get('p22', '14')}; {self.device_config.get('device', 'V2359A')} Build/BP2A.250605.015)",
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip',
        })
        self.zyeid = str(uuid.uuid4())
        self.imei = "____" + uuid.uuid4().hex[:16]
        self.p7 = "__" + uuid.uuid4().hex[:16]
        self.p28 = uuid.uuid4().hex.upper() + uuid.uuid4().hex[:32]
        self.guest_usr = f"j{int(time.time())}{random.randint(100, 999)}"
        self.p1 = ""
        self.usr = self.guest_usr
        self.ku = self.guest_usr
        self.kt = ""
        self.p35 = ""

    def get_base_params(self):
        current_usr = self.ku or self.usr or self.guest_usr
        return {
            "zyeid": self.zyeid,
            "usr": current_usr,
            "rgt": self.device_config["rgt"],
            "p1": self.p1,
            "ku": current_usr,
            "pc": self.device_config["pc"],
            "p2": self.device_config["p2"],
            "p3": self.device_config["p3"],
            "p4": self.device_config["p4"],
            "p5": self.device_config["p5"],
            "p7": self.p7,
            "p9": self.device_config["p9"],
            "p12": "",
            "p16": self.device_config["p16"],
            "p21": self.device_config["p21"],
            "p22": self.device_config["p22"],
            "p25": self.device_config["p25"],
            "p26": self.device_config["p26"],
            "p28": self.p28,
            "p29": self.device_config["p29"],
            "p30": "",
            "p31": self.p7,
            "p33": self.device_config["p33"],
            "p34": self.device_config["p34"],
            "p36": self.device_config["p36"],
            "firm": self.device_config["firm"],
            "d1": self.device_config["d1"],
        }

    def send_sms(self, phone):
        timestamp = str(int(time.time() * 1000))
        encrypted_phone = rsa_encrypt(phone)
        sign_params = {
            "channelId": self.device_config["channelId"],
            "device": self.device_config["device"],
            "flag": "1",
            "imei": self.imei,
            "phone": encrypted_phone,
            "sendType": "0",
            "times": "1",
            "timestamp": timestamp,
            "versionId": self.device_config["versionId"],
        }
        sign = rsa_sign(generate_sign_content(sign_params))
        url = f"{SK_API_SEND_SMS}?{urllib.parse.urlencode(self.get_base_params())}"
        data = {
            "versionId": self.device_config["versionId"],
            "device": self.device_config["device"],
            "flag": "1",
            "imei": self.imei,
            "sign": sign,
            "timestamp": timestamp,
            "phone": encrypted_phone,
            "times": "1",
            "sendType": "0",
            "channelId": self.device_config["channelId"],
        }
        response = self.session.post(url, data=data, timeout=30)
        result = response.json()
        if result.get("code") == 0 or result.get("msg") == "success":
            return True, "验证码发送成功"
        logger.warning(f"速看短信发送失败: {result}")
        return False, result.get("msg", "未知错误")

    def login(self, phone, code):
        timestamp = str(int(time.time() * 1000))
        encrypted_phone = rsa_encrypt(phone)
        pinfo, encrypted_des_key = generate_pinfo(phone, code)
        sign_params = {
            "channelId": self.device_config["channelId"],
            "device": self.device_config["device"],
            "imei": self.imei,
            "phone": encrypted_phone,
            "timestamp": timestamp,
            "versionId": self.device_config["versionId"],
        }
        sign = rsa_sign(generate_sign_content(sign_params))
        url_params = self.get_base_params()
        url_params["p35"] = encrypted_des_key
        url = f"{SK_API_LOGIN}?{urllib.parse.urlencode(url_params)}"
        data = {
            "smboxid": encrypted_des_key,
            "versionId": self.device_config["versionId"],
            "device": self.device_config["device"],
            "userName": url_params.get("usr", ""),
            "imei": self.imei,
            "sign": sign,
            "timestamp": timestamp,
            "pInfo": pinfo,
            "phone": encrypted_phone,
            "utdId": self.p1 or "",
            "loginSource": "我的_马上登录",
            "channelId": self.device_config["channelId"],
        }
        response = self.session.post(url, data=data, timeout=30)
        result = response.json()
        if result.get("code") == 0:
            body = result.get("body", {})
            self.kt = body.get("token", "") or body.get("kt", "")
            self.p1 = body.get("utdId", "") or body.get("signUser", "") or body.get("p1", "")
            self.usr = body.get("userName", "") or body.get("usr", "")
            self.ku = body.get("signUser", "") or body.get("ku", "") or self.usr
            self.p35 = encrypted_des_key
            return True, body, "登录成功"
        logger.warning(f"速看短信登录失败: {result}")
        return False, None, result.get("msg", "未知错误")

    def generate_welfare_url(self):
        if not self.kt:
            return ""
        task_profile = dict(SK_DEVICE_CONFIG)
        task_profile["p16"] = self.device_config.get("p16") or self.device_config.get("device") or task_profile["p16"]
        task_profile["p22"] = self.device_config.get("p22") or task_profile["p22"]
        task_profile["p34"] = self.device_config.get("firm") or self.device_config.get("p34") or task_profile["p34"]
        task_profile["firm"] = self.device_config.get("firm") or self.device_config.get("p34") or task_profile["firm"]
        params = {
            "zyeid": self.zyeid,
            "rgt": task_profile["rgt"],
            "p1": self.p1,
            "kt": self.kt,
            "source": "welfare",
            "showContentInStatusBar": "1",
            "ecpmMix": "0.0",
            "ecpmVideo": "0.0",
            "mcTacid": "",
            "pc": task_profile["pc"],
            "p2": task_profile["p2"],
            "p3": task_profile["p3"],
            "p4": task_profile["p4"],
            "p5": task_profile["p5"],
            "p7": self.p7,
            "p9": task_profile["p9"],
            "p12": "",
            "p16": task_profile["p16"],
            "p21": task_profile["p21"],
            "p22": task_profile["p22"],
            "p25": task_profile["p25"],
            "p26": task_profile["p26"],
            "p28": self.p28,
            "p29": task_profile["p29"],
            "p30": "",
            "p31": self.p7,
            "p33": task_profile["p33"],
            "p34": task_profile["p34"],
            "p36": task_profile["p36"],
            "firm": task_profile["firm"],
            "d1": task_profile["d1"],
            "pca": "channel-visit",
            "p35": self.p35,
            "usr": self.ku,
            "ku": self.ku,
        }
        base_url = "https://welfare-user.palmestore.com/sukanread/welfare-package/sudu/welfare.html"
        return f"{base_url}?{urllib.parse.urlencode(params)}"


# ===================== 授权时间计算函数（按天计算） =====================
def empower(empowertime, days):
    """授权时间计算 - 按天计算"""
    try:
        today_date = datetime.now().date()
        if len(empowertime) == 0 or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
            delayed_date = empower_date + timedelta(days=days)
            delayed_date = delayed_date.date()
        else:
            raise Exception('时间计算出错！')
        return str(delayed_date)
    except Exception as e:
        logger.error("授权时间计算失败: " + str(e))
        raise Exception("授权时间计算失败: " + str(e))

def _build_epay_sign(params_dict, key, exclude_keys=('sign', 'sign_type')):
    filtered = {k: v for k, v in params_dict.items() if k not in exclude_keys and v != ''}
    sorted_items = sorted(filtered.items(), key=lambda x: x[0])
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_items])
    return hashlib.md5((sign_str + key).encode('utf-8')).hexdigest().lower()

def _create_epay_qr(out_trade_no, channel, project_name, money_str):
    base_params = {
        'pid': str(config['epay_pid']).strip(),
        'type': channel,
        'out_trade_no': out_trade_no,
        'name': project_name,
        'money': money_str,
        'notify_url': 'http://127.0.0.1/',
        'return_url': 'http://127.0.0.1/'
    }
    submit_sign = _build_epay_sign(base_params, config['epay_key'])
    submit_params = dict(base_params)
    submit_params['sign'] = submit_sign
    submit_params['sign_type'] = 'MD5'

    qr_image_url = None
    try:
        mapi_params = dict(base_params)
        mapi_params['clientip'] = '127.0.0.1'
        mapi_sign = _build_epay_sign(mapi_params, config['epay_key'])
        mapi_params['sign'] = mapi_sign
        mapi_params['sign_type'] = 'MD5'

        mapi_url = config['epay_url'].rstrip('/') + '/mapi.php'
        resp = requests.post(mapi_url, data=mapi_params, timeout=15, verify=False)
        data = resp.json()
        if int(data.get('code', 0)) == 1:
            native_qr = data.get('qrcode', '') or data.get('payurl', '') or data.get('urlscheme', '')
            if native_qr:
                qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(native_qr, safe='')}"
    except Exception as e:
        logger.warning(f"易支付mapi异常: {e}")

    if not qr_image_url:
        raw_query = '&'.join(f'{k}={v}' for k, v in submit_params.items())
        pay_url = config['epay_url'].rstrip('/') + '/submit.php?' + raw_query
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(pay_url, safe='')}"

    return qr_image_url, out_trade_no

def process_epay_pay(amount, months, channel, order_prefix="SK"):
    try:
        out_trade_no = f"{order_prefix}_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
        formatted_money = f"{float(amount):.2f}"
        channel_name = "支付宝" if channel == 'alipay' else ("微信支付" if channel == 'wxpay' else "QQ钱包")
        qr_image_url, _ = _create_epay_qr(out_trade_no, channel, f"速看授权-{months}M", formatted_money)

        sender.reply(f"=====等待支付=====\n💰 金额: {formatted_money}元\n💳 方式: {channel_name}\n📋 订单: {out_trade_no}\n------------------\n请在 180 秒内完成扫码支付\n回复\"q\"取消支付")
        sender.replyImage(qr_image_url)

        query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
        cancel_event = threading.Event()
        paid_event = threading.Event()

        def _poll_order():
            while not cancel_event.is_set() and time.time() - start_time < 180:
                try:
                    res = requests.get(query_url, timeout=5).json()
                    if str(res.get('code')) == '1' and str(res.get('status')) == '1':
                        paid_event.set()
                        return
                except Exception:
                    pass
                time.sleep(2)

        start_time = time.time()
        poll_thread = threading.Thread(target=_poll_order, daemon=True)
        poll_thread.start()

        while time.time() - start_time < 180:
            if paid_event.is_set():
                cancel_event.set()
                return True

            cancel_check = sender.listen(1000)
            if cancel_check:
                cancel_text = str(cancel_check).strip().lower()
                if cancel_text in ['q', 'quit', 'exit', '退出', 'cancel', '取消']:
                    cancel_event.set()
                    sender.reply("✅ 已取消支付")
                    return False

        cancel_event.set()
        if paid_event.is_set():
            return True
        sender.reply("❌ 支付超时，请重新发起。")
        return False
    except Exception as e:
        logger.error(f"易支付处理失败: {e}")
        sender.reply(f"❌ 易支付异常: {e}")
        return False


# ===================== 代理管理器 =====================
class ProxyManager:
    """代理管理器"""
    
    def __init__(self, enable_proxy=False, proxy_pool_url=''):
        self.enable_proxy = enable_proxy
        self.proxy_pool_url = proxy_pool_url
        self.current_proxy = None
        self.last_fetch_time = 0
        self.proxy_cache_time = 300  # 代理缓存5分钟
        
    def get_proxy(self):
        """获取代理"""
        if not self.enable_proxy or not self.proxy_pool_url:
            return None
            
        # 检查缓存是否过期
        current_time = time.time()
        if self.current_proxy and (current_time - self.last_fetch_time) < self.proxy_cache_time:
            return self.current_proxy
            
        try:
            # 从代理池获取代理
            logger.info("从代理池获取代理: " + self.proxy_pool_url)
            response = requests.get(self.proxy_pool_url, timeout=10)
            
            if response.status_code == 200:
                proxy_data = response.json()
                
                # 支持不同格式的代理池响应
                if isinstance(proxy_data, dict):
                    proxy = proxy_data.get('proxy')
                    if proxy:
                        self.current_proxy = proxy
                        self.last_fetch_time = current_time
                        logger.info("获取代理成功: " + proxy)
                        return proxy
                    
                    http_proxy = proxy_data.get('http') or proxy_data.get('https')
                    if http_proxy:
                        self.current_proxy = http_proxy
                        self.last_fetch_time = current_time
                        logger.info("获取代理成功: " + http_proxy)
                        return http_proxy
                
                elif isinstance(proxy_data, str):
                    self.current_proxy = proxy_data
                    self.last_fetch_time = current_time
                    logger.info("获取代理成功: " + proxy_data)
                    return proxy_data
                
                elif isinstance(proxy_data, list) and proxy_data:
                    proxy = proxy_data[0]
                    self.current_proxy = proxy
                    self.last_fetch_time = current_time
                    logger.info("获取代理成功: " + proxy)
                    return proxy
                
                logger.warning("代理池返回格式不支持: " + str(proxy_data))
                return None
                
        except Exception as e:
            logger.error("获取代理失败: " + str(e))
            return None
    
    def rotate_proxy(self):
        """强制更换代理"""
        self.current_proxy = None
        self.last_fetch_time = 0
        return self.get_proxy()
    
    def get_proxy_dict(self):
        """获取requests格式的代理字典"""
        proxy = self.get_proxy()
        if not proxy:
            return None
        
        return {
            'http': proxy,
            'https': proxy
        }


# ===================== 备注管理器 =====================
class RemarkManager:
    """账号备注管理器"""
    
    @staticmethod
    def get_account_remark(user_id, account_id):
        """获取账号备注"""
        try:
            remark_data = middleware.bucketGet(bucket='dd_sk_remarks', key=f'{user_id}_{account_id}')
            if remark_data:
                return remark_data
            return ""
        except Exception as e:
            logger.error("获取备注失败: " + str(user_id) + " - " + str(account_id) + " - " + str(e))
            return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        """设置账号备注"""
        try:
            remark_clean = remark.strip()[:20]  # 限制20字符
            if remark_clean:
                middleware.bucketSet(bucket='dd_sk_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
                logger.info("设置备注: " + str(user_id) + " - " + str(account_id) + " - " + remark_clean)
                return remark_clean
            return ""
        except Exception as e:
            logger.error("设置备注失败: " + str(user_id) + " - " + str(account_id) + " - " + str(e))
            return ""
    
    @staticmethod
    def get_all_remarks(user_id):
        """获取用户所有账号的备注"""
        try:
            accounts = AccountManager.get_accounts(user_id)
            remarks = {}
            for account in accounts:
                remark = RemarkManager.get_account_remark(user_id, account)
                if remark:
                    remarks[account] = remark
            return remarks
        except Exception as e:
            logger.error("获取所有备注失败: " + str(user_id) + " - " + str(e))
            return {}
    
    @staticmethod
    def delete_account_remark(user_id, account_id):
        """删除账号备注"""
        try:
            middleware.bucketDel(bucket='dd_sk_remarks', key=f'{user_id}_{account_id}')
            logger.info("删除备注: " + str(user_id) + " - " + str(account_id))
            return True
        except Exception as e:
            logger.error("删除备注失败: " + str(user_id) + " - " + str(account_id) + " - " + str(e))
            return False


# ===================== 安全请求包装 =====================
def safe_request(method, url, **kwargs):
    """安全的请求包装函数，支持代理"""
    try:
        if 'timeout' not in kwargs:
            kwargs['timeout'] = REQUEST_TIMEOUT
            
        if 'verify' not in kwargs:
             kwargs['verify'] = False 
        
        # 添加代理支持
        if config['enable_proxy'] and config['proxy_pool_url']:
            proxy_manager = ProxyManager(enable_proxy=True, proxy_pool_url=config['proxy_pool_url'])
            proxies = proxy_manager.get_proxy_dict()
            if proxies:
                kwargs['proxies'] = proxies
                logger.debug("使用代理请求: " + str(proxies))
        
        logger.debug("发送请求: " + method + " " + url)
        response = requests.request(method, url, **kwargs)
        
        if response.status_code >= 400:
            logger.error("请求失败: " + url + " - 状态码: " + str(response.status_code))
            if response.status_code in [403, 407, 408, 429] and config['enable_proxy']:
                logger.info("代理可能失效，尝试更换代理重试...")
                proxy_manager = ProxyManager(enable_proxy=True, proxy_pool_url=config['proxy_pool_url'])
                proxy_manager.rotate_proxy()
                proxies = proxy_manager.get_proxy_dict()
                if proxies:
                    kwargs['proxies'] = proxies
                    
                    try:
                        logger.info("使用新代理重试请求")
                        response = requests.request(method, url, **kwargs)
                        if response.status_code >= 400:
                            raise Exception("请求失败，状态码: " + str(response.status_code))
                    except Exception as retry_e:
                        raise Exception("代理重试失败: " + str(retry_e))
            else:
                     raise Exception("请求失败，状态码: " + str(response.status_code))
            
        return response
    except requests.exceptions.Timeout:
        logger.error("请求超时: " + url)
        raise Exception("请求超时: " + url)
    except requests.exceptions.SSLError as e:
        logger.error("SSL错误: " + url + " - " + str(e))
        try:
            logger.warning("尝试跳过SSL验证: " + url)
            kwargs['verify'] = False
            response = requests.request(method, url, **kwargs)
            return response
        except Exception as retry_e:
            raise Exception("SSL验证失败: " + str(e))
    except requests.exceptions.RequestException as e:
        logger.error("请求失败: " + url + " - " + str(e))
        raise Exception("请求失败: " + str(e))
    except Exception as e:
        logger.error("请求异常: " + url + " - " + str(e))
        raise Exception("请求异常: " + str(e))


# ===================== Token/密码 安全处理 =====================
def encrypt_token(token):
    """简单加密Token (这里用于加密凭证)"""
    try:
        return base64.b64encode(token.encode()).decode()
    except:
        return token

def decrypt_token(encrypted_token):
    """解密Token (这里用于解密凭证)"""
    try:
        return base64.b64decode(encrypted_token.encode()).decode()
    except:
        return encrypted_token


def safe_json_loads(raw, default=None):
    try:
        return json.loads(raw) if raw else (default if default is not None else {})
    except:
        return default if default is not None else {}


def detect_phone_candidates(*values):
    candidates = []
    for value in values:
        if value is None:
            continue
        text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        for phone in re.findall(r'(?<!\d)1[3-9]\d{9}(?!\d)', text):
            if phone not in candidates:
                candidates.append(phone)
    return candidates


def get_account_meta(account_key):
    return safe_json_loads(middleware.bucketGet(bucket='dd_sk_meta', key=str(account_key)), {})


def set_account_meta(account_key, meta):
    try:
        merged = get_account_meta(account_key)
        merged.update({k: v for k, v in (meta or {}).items() if v not in [None, ""]})
        middleware.bucketSet(bucket='dd_sk_meta', key=str(account_key), value=json.dumps(merged, ensure_ascii=False))
        return merged
    except Exception as e:
        logger.error(f"保存账号元信息失败 {account_key}: {e}")
        return meta or {}


def remove_account_meta(account_key):
    try:
        middleware.bucketDel(bucket='dd_sk_meta', key=str(account_key))
    except:
        pass


def find_account_by_phone(user_id, phone):
    phone = str(phone or "").strip()
    if not phone:
        return None
    for account in AccountManager.get_accounts(user_id):
        meta = get_account_meta(account)
        if str(meta.get('phone') or "").strip() == phone:
            return str(account)
        if str(account).strip() == phone:
            return str(account)
    return None


def migrate_account_binding_if_needed(user_id, old_account_key, new_account_key):
    old_account_key = str(old_account_key or "").strip()
    new_account_key = str(new_account_key or "").strip()
    if not old_account_key or not new_account_key or old_account_key == new_account_key:
        return
    try:
        old_token = middleware.bucketGet(bucket='dd_sk_token', key=old_account_key)
        new_token = middleware.bucketGet(bucket='dd_sk_token', key=new_account_key)
        if old_token and not new_token:
            middleware.bucketSet(bucket='dd_sk_token', key=new_account_key, value=old_token)

        old_auth = middleware.bucketGet(bucket='dd_sk_auth', key=old_account_key)
        new_auth = middleware.bucketGet(bucket='dd_sk_auth', key=new_account_key)
        if old_auth and not new_auth:
            middleware.bucketSet(bucket='dd_sk_auth', key=new_account_key, value=old_auth)

        old_remark = middleware.bucketGet(bucket='dd_sk_remarks', key=f'{user_id}_{old_account_key}')
        new_remark = middleware.bucketGet(bucket='dd_sk_remarks', key=f'{user_id}_{new_account_key}')
        if old_remark and not new_remark:
            middleware.bucketSet(bucket='dd_sk_remarks', key=f'{user_id}_{new_account_key}', value=old_remark)

        old_meta = get_account_meta(old_account_key)
        if old_meta:
            merged = dict(old_meta)
            merged.setdefault("migrated_from", old_account_key)
            set_account_meta(new_account_key, merged)

        AccountManager.remove_account(user_id, old_account_key)
        middleware.bucketDel(bucket='dd_sk_token', key=old_account_key)
        middleware.bucketDel(bucket='dd_sk_auth', key=old_account_key)
        middleware.bucketDel(bucket='dd_sk_remarks', key=f'{user_id}_{old_account_key}')
        remove_account_meta(old_account_key)

        try:
            remove_account_env_from_system(old_account_key)
        except Exception:
            pass

        logger.info(f"账号已合并迁移: {old_account_key} -> {new_account_key}")
    except Exception as e:
        logger.error(f"账号迁移失败 {old_account_key} -> {new_account_key}: {e}")


# ===================== 账号管理类 =====================
class AccountManager:
    """账号管理类"""
    
    @staticmethod
    def get_accounts(user_id):
        """获取用户账号列表"""
        try:
            # 桶名改为 dd_sk_user
            value = middleware.bucketGet(bucket='dd_sk_user', key=user_id)
            if not value:
                return []
            
            if value.startswith('[') and value.endswith(']'):
                try:
                    accounts = ast.literal_eval(value)
                    if isinstance(accounts, (list, tuple, set)):
                        accounts = [str(x) for x in list(dict.fromkeys(accounts))]
                        return accounts
                except:
                    pass
            return [str(value)]
        except Exception as e:
            logger.error("获取账号列表失败: " + str(user_id) + " - " + str(e))
            return []
    
    @staticmethod
    def add_account(user_id, account):
        """添加账号（去重）"""
        try:
            accounts = AccountManager.get_accounts(user_id)
            if account not in accounts:
                accounts.append(account)
                middleware.bucketSet(bucket='dd_sk_user', key=user_id, value=str(accounts))
                logger.info("用户 " + str(user_id) + " 添加账号: " + account)
            return True
        except Exception as e:
            logger.error("添加账号失败: " + str(user_id) + " - " + account + " - " + str(e))
            return False
    
    @staticmethod
    def remove_account(user_id, account):
        """移除账号"""
        try:
            accounts = AccountManager.get_accounts(user_id)
            if account in accounts:
                accounts.remove(account)
                if accounts:
                    middleware.bucketSet(bucket='dd_sk_user', key=user_id, value=str(accounts))
                else:
                    middleware.bucketDel(bucket='dd_sk_user', key=user_id)
                logger.info("用户 " + str(user_id) + " 移除账号: " + account)
                return True
            return False
        except Exception as e:
            logger.error("移除账号失败: " + str(user_id) + " - " + account + " - " + str(e))
            return False
    
    @staticmethod
    def update_account_credentials(account_key, full_credential):
        """更新账号的凭证 (Token/URL)"""
        try:
            # 存储在 dd_sk_token 桶
            encrypted = encrypt_token(full_credential)
            middleware.bucketSet(bucket='dd_sk_token', key=account_key, value=encrypted)
            return True
        except Exception as e:
            logger.error("更新凭证失败: " + str(e))
            return False
    
    @staticmethod
    def get_all_users():
        """获取所有绑定了速看账号的用户"""
        try:
            users = middleware.bucketAllKeys(bucket='dd_sk_user')
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts:
                    user_list.append(user)
            return user_list
        except Exception as e:
            logger.error("获取用户列表失败: " + str(e))
            return []


# ===================== 系统对接相关（原青龙） =====================
class QingLongAPI:
    """系统对接API封装"""
    
    def __init__(self):
        ql_config = config['dd_sk_qlname']
        try:
            if not ql_config:
                raise ValueError("对接配置为空")
                
            qllist = ql_config.split('丨')
            if len(qllist) != 3:
                raise ValueError("对接配置格式错误，应使用'丨'分隔")
                
            self.QLurl = qllist[0].strip()
            self.ClientID = qllist[1].strip()
            self.ClientSecret = qllist[2].strip()
            
            if not all([self.QLurl, self.ClientID, self.ClientSecret]):
                raise ValueError("对接配置参数不完整")
                
            if not self.QLurl.startswith(('http://', 'https://')):
                raise ValueError("对接地址格式错误，必须以http://或https://开头")
            
            self.qltoken = self._get_token()
        
        except Exception as e:
            logger.error("系统初始化失败: " + str(e))
            raise
    
    def _get_token(self):
        """获取系统Token"""
        try:
            url = self.QLurl + '/open/auth/token?client_id=' + self.ClientID + '&client_secret=' + self.ClientSecret
            response = safe_request("GET", url, timeout=REQUEST_TIMEOUT)
            
            if response.status_code != 200:
                raise Exception("对接API请求失败，状态码: " + str(response.status_code))
                
            result = response.json()
            token_data = result.get('data', {})
            if "token" in token_data:
                return token_data['token']
            else:
                raise Exception("获取Token失败")
                
        except Exception as e:
            logger.error("获取系统Token失败: " + str(e))
            raise
    
    def get_all_envs(self):
        """获取所有环境变量"""
        try:
            url = self.QLurl + "/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + self.qltoken,
                "accept": "application/json"
            }
            response = safe_request("GET", url, headers=headers)
            result = response.json()
            
            if result.get('code') == 200:
                return result.get('data', [])
            else:
                raise Exception("获取变量失败: " + str(result.get('message')))
                
        except Exception as e:
            logger.error("获取系统变量失败: " + str(e))
            raise

    @staticmethod
    def _get_env_identity(env_ref):
        """兼容青龙不同版本的 id / _id 字段"""
        if not env_ref:
            return None, None

        if isinstance(env_ref, dict):
            if env_ref.get('id') is not None:
                return 'id', env_ref.get('id')
            if env_ref.get('_id') is not None:
                return '_id', env_ref.get('_id')

        return 'id', env_ref
    
    def find_env_by_account(self, value_snippet, user_id=None):
        """
        根据Token片段或用户ID查找环境变量
        优先匹配用户ID(ID:xxxxx)防止变量重复
        """
        try:
            envs = self.get_all_envs()
            # 这里的value_snippet可能是 token 或 zyeid 的一部分
            target_val = f"{value_snippet}" 
            target_uid_str = f"ID:{user_id}" if user_id else None
            
            for env in envs:
                if env.get('name') != config['dd_sk_osname']:
                    continue
                
                # 1. 优先匹配备注中的 ID
                remarks = env.get('remarks', '')
                if target_uid_str and remarks and target_uid_str in remarks:
                    return env

                # 2. 其次匹配 Value (如果value包含了zyeid)
                current_value = env.get('value', '')
                if user_id and str(user_id) in current_value:
                    return env
            
            return None
        except Exception as e:
            logger.error("查找系统变量失败: " + str(e))
            return None
    
    def delete_env(self, env_id):
        """删除环境变量"""
        _, env_value = self._get_env_identity(env_id)
        if not env_value:
            return False
            
        try:
            url = self.QLurl + "/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + self.qltoken,
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            data = [env_value]
            response = safe_request("DELETE", url, headers=headers, json=data)
            return response.status_code == 200
        except Exception as e:
            logger.error("删除系统变量失败: " + str(e))
            return False
    
    def add_env(self, full_value, user_id, nickname, remark="", auth_time="", owner_user_id=None):
        """添加环境变量"""
        try:
            url = self.QLurl + "/open/envs"
            # 关键：这里直接使用全量的 full_value (URL)
            value = full_value
            
            # 构建备注信息
            remarks_parts = [f'速看:{nickname}']
            
            if auth_time:
                remarks_parts.append(f'到期:{auth_time}')
            else:
                remarks_parts.append('到期:未授权')

            if remark:
                remarks_parts.append(f'备注:{remark}')
            
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{user_id}', '速看管理'])
            
            data = [{
                "value": value,
                "name": config['dd_sk_osname'],
                "remarks": '丨'.join(remarks_parts)
            }]
            
            headers = {
                "Authorization": "Bearer " + self.qltoken,
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            
            response = safe_request("POST", url, headers=headers, json=data)
            
            if response.status_code != 200:
                raise Exception("请求失败，状态码: " + str(response.status_code))
                
            result = response.json()
            if result.get('code') != 200:
                raise Exception("系统返回错误: " + str(result.get('message')))
                
            return True
        except Exception as e:
            logger.error("添加系统变量失败: " + str(e))
            raise
    
    def update_env(self, env_id, full_value, user_id, nickname, remark="", auth_time="", owner_user_id=None):
        """更新环境变量"""
        try:
            env_field, env_value = self._get_env_identity(env_id)
            if not env_value:
                raise Exception("系统变量ID为空")

            url = self.QLurl + "/open/envs"
            # 关键：这里直接使用全量的 full_value (URL)
            value = full_value
            
            # 构建备注信息
            remarks_parts = [f'速看:{nickname}']
            
            if auth_time:
                remarks_parts.append(f'到期:{auth_time}')
            else:
                remarks_parts.append('到期:未授权')
            
            if remark:
                remarks_parts.append(f'备注:{remark}')
            
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{user_id}', '速看管理'])
            
            data = {
                "value": value,
                "name": config['dd_sk_osname'],
                "remarks": '丨'.join(remarks_parts)
            }
            data[env_field] = env_value
            
            headers = {
                "Authorization": "Bearer" + ' ' + self.qltoken,
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            
            response = safe_request("PUT", url, headers=headers, data=json.dumps(data))
            
            if response.status_code != 200:
                raise Exception("更新失败，状态码: " + str(response.status_code))
                
            return True
        except Exception as e:
            logger.error("更新系统变量失败: " + str(e))
            raise

# 初始化系统API
try:
    ql_api = QingLongAPI()
except Exception as e:
    sender.reply("❌ 系统连接失败: " + str(e))
    exit(0)


def parse_auth_date(auth_time):
    """解析授权日期字符串"""
    if not auth_time:
        return None

    try:
        return datetime.strptime(auth_time, "%Y-%m-%d").date()
    except Exception:
        return None


def get_account_auth_status(account_key):
    """返回账号授权状态"""
    auth_time = middleware.bucketGet(bucket='dd_sk_auth', key=account_key) or ""
    auth_date = parse_auth_date(auth_time)
    today_date = datetime.now().date()
    is_authorized = auth_date is not None and auth_date >= today_date
    return auth_time, auth_date, is_authorized


def remove_account_env_from_system(account_key):
    """按账号ID兜底删除青龙变量"""
    env_ref = ql_api.find_env_by_account(account_key, account_key)
    if not env_ref:
        return False
    return ql_api.delete_env(env_ref)


def sync_account_env(account_key, full_cred, nickname, remark=""):
    """根据授权状态决定是否同步到青龙"""
    auth_time, _, is_authorized = get_account_auth_status(account_key)
    env_ref = ql_api.find_env_by_account(account_key, account_key)

    if not is_authorized:
        if env_ref:
            ql_api.delete_env(env_ref)
            return 'removed'
        return 'local_only'

    if not full_cred:
        raise Exception(f"账号 {account_key} 凭证不存在，无法同步到系统")

    if env_ref:
        ql_api.update_env(env_ref, full_cred, account_key, nickname, remark, auth_time)
        return 'updated'

    ql_api.add_env(full_cred, account_key, nickname, remark, auth_time)
    return 'added'


def parse_sukan_env_remarks(remarks):
    """解析速看青龙备注中的关键字段"""
    if not remarks:
        return {}

    info = {}
    for part in remarks.split('丨'):
        part = part.strip()
        if not part or ':' not in part:
            continue
        key, value = part.split(':', 1)
        info[key.strip()] = value.strip()
    return info


def clean_expired_envs_from_qinglong(today_date):
    """兜底清理青龙中已过期的速看变量，防止本地账密缺失导致残留"""
    cleaned_count = 0

    try:
        envs = ql_api.get_all_envs()
    except Exception as e:
        logger.error(f"获取青龙变量列表失败，无法执行兜底清理: {str(e)}")
        return 0

    for env in envs:
        try:
            if env.get('name') != config['dd_sk_osname']:
                continue

            remarks = env.get('remarks', '') or ''
            is_sukan_env = ('速看管理' in remarks) or ('速看:' in remarks and '到期:' in remarks)
            if not is_sukan_env:
                continue

            info = parse_sukan_env_remarks(remarks)
            expire_str = info.get('到期', '')
            if not expire_str or expire_str == '未授权':
                continue

            expire_date = parse_auth_date(expire_str)
            if not expire_date or expire_date >= today_date:
                continue

            if ql_api.delete_env(env):
                cleaned_count += 1
                account_key = info.get('ID', '')
                if account_key:
                    middleware.bucketDel(bucket='dd_sk_token', key=account_key)
                    middleware.bucketDel(bucket='dd_sk_auth', key=account_key)
                logger.info(f"青龙兜底清理已过期变量成功: {account_key or remarks}")
            else:
                logger.error(f"青龙兜底清理已过期变量失败: {remarks}")
        except Exception as e:
            logger.error(f"处理青龙速看变量兜底清理失败: {str(e)}")

    return cleaned_count


# ===================== 速看核心类 (全参透传版) =====================
class NN: 
    """速看(SuKan) 核心类"""
    def __init__(self, full_data=""):
        self.full_data = full_data.strip()
        self.kt = ""
        self.zyeid = ""
        self.user_id = None
        self.nickname = "速看用户"
        self.user_url = 'https://welfare-user.palmestore.com' # 用户信息用
        self.proxy_manager = ProxyManager(config['enable_proxy'], config['proxy_pool_url'])
        self.request_params = {} # 存储解析后的完整参数
        
        # 尝试解析
        self.parse_input()
        
    def getRandomUA(self):
        """参考脚本生成随机UA"""
        try:
            androidVersions = ['10', '11', '12', '13']
            models = ['M2007J3SC', 'M2012K11C', '22041211AC', '23049RAD8C', 'V2055A', 'V2185A', 'PCDM10', 'PDEM30', 'Redmi K40', 'Mi 10']
            model = random.choice(models)
            androidVer = random.choice(androidVersions)
            buildId = 'SP1A.' + str(random.randint(100000, 999999)) + '.0' + str(random.randint(10, 99))
            return f"Mozilla/5.0 (Linux; Android {androidVer}; {model} Build/{buildId}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{random.randint(90, 99)}.0.4951.61 Safari/537.36 zyApp/SuKanRead zyVersion/8.0.2 zyChannel/801004"
        except:
            return "Mozilla/5.0 (Linux; Android 12; M2007J3SC Build/SP1A.123456.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/99.0.4951.61 Safari/537.36 zyApp/SuKanRead zyVersion/8.0.2 zyChannel/801004"

    def parse_input(self):
        """解析抓包数据 - 提取完整参数，不做任何阉割"""
        if not self.full_data: return
        
        try:
            query_str = ""
            # 1. 如果是URL，提取QueryString
            if '?' in self.full_data:
                query_str = self.full_data.split('?', 1)[1]
            else:
                # 假设用户发来的本身就是QueryString（不带https头）
                query_str = self.full_data
            
            # 2. 将参数解析为字典，仅用于登录校验和提取ID
            # 实际存储时，我们将使用原始的 query_str 或者是 包含https的 full_data (取决于用户输入)
            # 用户要求 "整段链接提交"，所以最终存储 self.full_data
            
            params_list = urllib.parse.parse_qsl(query_str)
            self.request_params = dict(params_list)
            
            # 3. 提取核心ID用于标识用户 (zyeid 是唯一标识)
            self.kt = self.request_params.get('kt') or self.request_params.get('token')
            self.zyeid = self.request_params.get('zyeid') or self.request_params.get('zyeId')
            
            # 兼容 JSON (虽然可能用不到，保留逻辑完整性)
            if not self.kt and self.full_data.startswith('{'):
                try:
                    json_data = json.loads(self.full_data)
                    body = json_data.get('body', {})
                    self.kt = body.get('token') or body.get('kt')
                    self.zyeid = body.get('zyeid') or body.get('zyeId')
                    # 构造最简串，这种情况下可能会丢AppId，但没办法
                    self.request_params = {'kt': self.kt, 'zyeid': self.zyeid, 'source': 'welfare'}
                except: pass
                
        except Exception as e:
            logger.error(f"参数解析失败: {e}")
            
        if self.zyeid:
            self.user_id = self.zyeid

    def get_headers(self):
        """获取速看专用Header"""
        return {
            'Host': 'welfare-user.palmestore.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://welfare-user.palmestore.com',
            'X-Requested-With': 'com.chaozh.xincao.only.sk',
            'Referer': 'https://welfare-user.palmestore.com/sukanread/welfare-package/sudu/welfare.html',
            'User-Agent': self.getRandomUA()
        }

    def user_info(self):
        """获取用户信息 (全参校验)"""
        try:
            if not self.kt or not self.zyeid:
                return None
            
            url = f"{self.user_url}/api/user/info"
            
            # 核心：使用解析出的【完整参数字典】发起请求
            # 这样请求时会带上 p1...p36, sign, timestamp 等所有校验参数
            params = self.request_params
            
            # 确保 source 存在
            if 'source' not in params:
                params['source'] = 'welfare'
            
            headers = self.get_headers()
            proxies = self.proxy_manager.get_proxy_dict() if config['enable_proxy'] else None
            
            res = safe_request("GET", url, headers=headers, params=params, proxies=proxies, timeout=10)
            
            try:
                rj = res.json()
            except:
                return None
            
            if str(rj.get('code')) == '0':
                body = rj.get('body', {})
                total_coin = body.get('total_coin', 0)
                phone_candidates = detect_phone_candidates(body, self.full_data)
                phone = phone_candidates[0] if phone_candidates else ""
                
                return {
                    "nickname": "速看用户", 
                    "coin": total_coin, 
                    "money": 0,
                    "user_id": self.zyeid,
                    "phone": phone,
                    "zyeid": self.zyeid,
                    # 核心修改：直接返回用户提交的【整段链接】
                    "token": self.full_data 
                }
            return None
                
        except Exception as e:
            logger.error(f"速看验证失败: {e}")
            return None

# ===================== 辅助函数 =====================

def nn_session_ids(input_str):
    """验证速看数据有效性"""
    try:
        logger.info(f"验证速看数据: {input_str[:30]}...")
        nn = NN(input_str)
        info = nn.user_info()
        
        if info:
            logger.info("账号验证成功: " + str(info['user_id']))
            # 核心：返回 提交给青龙的【整段链接】, 唯一ID, 用户ID, 昵称
            submission_str = info['token']
            return {
                "submission_str": submission_str,
                "device_id": info.get('zyeid') or info['user_id'],
                "user_id": info['user_id'],
                "nickname": info['nickname'],
                "phone": info.get('phone', ''),
                "zyeid": info.get('zyeid') or info['user_id'],
            }
        else:
            sender.reply('❌ 验证失败：链接可能已过期或签名无效')
            exit(0)
    except Exception as e:
        logger.error("账号验证失败: " + str(e))
        sender.reply("❌ 验证账号失败: " + str(e))
        exit(0)


def cx(full_credential):
    """速看查询功能"""
    try:
        # full_credential 现在是【整段链接】
        # 直接透传给 NN 类进行全参请求，这样查询就能通过校验了
        nn = NN(full_credential)
        info = nn.user_info()
        
        if not info:
            # 如果查询失败（比如参数过期），返回一个提示状态
            return {
                "nickname": "速看用户",
                "coin": "❓失效需更新", 
                "money": 0 
            }
        
        return {
            "nickname": info.get("nickname", "未知用户"),
            "coin": info.get("coin", 0),
            "money": 0 
        }
        
    except Exception as e:
        logger.error("速看查询失败: " + str(e))
        return None

def process_single_account(account_key, index, total_count, account_remarks):
    """处理单个账号查询"""
    try:
        enc_cred = middleware.bucketGet(bucket='dd_sk_token', key=f'{account_key}')
        full = decrypt_token(enc_cred) if enc_cred else None
        
        accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=f'{account_key}')
        
        remark = ""
        remark_display = ""
        if config['enable_remark']:
            remark = account_remarks.get(account_key, "")
            remark_display = f"\n📝 备注: {remark}" if remark else ""
        
        today_time = str(datetime.now().date())
        if not accountVip:
            auth_status = "⚠️ 未授权"
            auth_time = "无"
        elif accountVip <= today_time:
            auth_status = "❌ 已过期"
            auth_time = accountVip
        else:
            auth_status = "✅ 已授权"
            auth_time = accountVip
        
        if accountVip and accountVip > today_time and full:
            try:
                data = cx(full)
                
                if not data:
                    return None
                
                point_status_info = ""
                if config['show_point_status']:
                    point_status_info = f"\n📊 状态: {'✅ 有效' if data['coin'] != '❓失效需更新' else '❌ 需更新'}"
                
                account_info = f"""
=====速看账号详情({index}/{total_count})=====
🔑 ID: {account_key}{remark_display}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
💰 当前金币: {data['coin']}{point_status_info}
=================="""
                return account_info
        
            except Exception as e:
                logger.error("账号 " + account_key + " 查询失败: " + str(e))
            
            return f"""
=====速看查询失败=====
🔑 ID: {account_key}
❌ 错误: {str(e)[:50]}...
=================="""
        else:
            logger.warning("账号 " + account_key + " 未授权或凭证无效")
            return f"""
=====速看授权过期=====
🔑 ID: {account_key}{remark_display}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
=================="""
    except Exception as e:
        logger.error(f"处理账号 {account_key} 失败: {str(e)}")
        return None

def cxs():
    """速看批量查询"""
    try:
        accounts = AccountManager.get_accounts(userid)
        
        if not accounts:
            sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {config['randomsigncommand']} 绑定
==================""")
            return
        
        account_remarks = {}
        if config['enable_remark']:
            account_remarks = RemarkManager.get_all_remarks(userid)
    
        total_count = len(accounts)
        logger.info("用户 " + str(userid) + " 开始批量查询 " + str(total_count) + " 个账号")
    
        sender.reply(f"🚀 正在并发查询 {total_count} 个账号，请稍候...")

        max_workers = min(10, total_count)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_account = {}
            for index, account in enumerate(accounts, 1):
                future = executor.submit(process_single_account, account, index, total_count, account_remarks)
                future_to_account[future] = account

            for future in as_completed(future_to_account):
                result_msg = future.result()
                if result_msg:
                    sender.reply(result_msg)
                
    except Exception as e:
        logger.error("批量查询失败: " + str(e))
        sender.reply(f"""
=====查询系统错误=====
❌ 批量查询失败
错误: {str(e)}
==================""")


def get_user_input(timeout=60):
    """获取用户输入"""
    try:
        logger.info("等待用户输入，超时: " + str(timeout) + "秒")
        response = sender.listen(timeout * 1000)
        
        if response is None or response == '':
            logger.warning("用户输入超时或为空")
            return None
            
        response = response.strip()
        logger.info("收到用户输入: " + response)
        
        if response.lower() in ['q', 'quit', 'exit', '退出', 'cancel']:
            return 'q'
        
        return response
        
    except Exception as e:
        logger.error("获取用户输入失败: " + str(e))
        return None


# ===================== 绑定账号功能 =====================
def bindaccount():
    """绑定速看账号 - 支持CK登录和短信登录"""
    try:
        logger.info("用户 " + str(userid) + " 开始绑定账号")
 
        # 备注设置
        remark = ""
        if config['enable_remark']:
            remark_guide = """
=====账号备注设置=====
🎯 请输入账号备注名
------------------
例如: 我的主账号、备用账号等
(可选，最多20个字符)
------------------
回复备注名继续
回复"n"跳过备注
回复"q"退出操作
=================="""
            sender.reply(remark_guide)
            
            remark_input = get_user_input(timeout=120)
            if remark_input is None:
                sender.reply("⏰ 操作超时，已退出")
                return
            elif remark_input.lower() == 'q':
                sender.reply("✅ 已取消登录")
                return
            elif remark_input.lower() != 'n':
                remark = remark_input.strip()[:20]
                logger.info("用户设置备注: " + remark)

        sender.reply("""
=====速看登录=====
[1] CK登录
[2] 短信登录
------------------
回复对应数字继续
回复"q"退出
==================""")

        login_type = get_user_input(timeout=120)
        if not login_type or login_type == 'q':
            sender.reply("✅ 已退出")
            return

        if login_type.strip() == '1':
            sender.reply("""
=====CK登录=====
请发送抓包的【整段链接】
------------------
包含 https://... 和所有参数
不要删减任何内容
------------------
直接发送数据即可
回复"q"退出
==================""")

            instr = get_user_input(180)
            if not instr or instr == 'q':
                sender.reply("✅ 已退出")
                return

            try:
                login_info = nn_session_ids(instr)
                if login_info and login_info.get("submission_str") and login_info.get("user_id"):
                    save_sukan_device_profile(login_info["submission_str"])
                    process_account_binding(
                        login_info["submission_str"],
                        login_info["device_id"],
                        login_info["user_id"],
                        login_info["nickname"],
                        remark,
                        phone=login_info.get("phone", ""),
                        login_type="ck"
                    )
            except Exception as e:
                sender.reply(f"❌ 验证失败: {e}")
            return

        if login_type.strip() == '2':
            if not CRYPTO_AVAILABLE:
                sender.reply("❌ 当前环境缺少 pycryptodome，无法使用短信登录")
                return

            sender.reply("""
=====短信登录=====
📱 请输入手机号
------------------
回复"q"退出
==================""")
            phone = get_user_input(timeout=120)
            if not phone or phone == 'q':
                sender.reply("✅ 已退出")
                return

            phone = str(phone).strip()
            if not phone.isdigit() or len(phone) != 11:
                sender.reply("❌ 手机号格式错误，请输入11位手机号")
                return

            sender.reply(f"🔄 正在发送验证码到 {phone[:3]}****{phone[7:]}...")
            api = SukanSMSLoginAPI()
            sms_ok, sms_msg = api.send_sms(phone)
            if not sms_ok:
                sender.reply(f"❌ 发送验证码失败: {sms_msg}")
                return

            sender.reply("""
=====短信登录=====
✅ 验证码已发送
📱 请输入验证码
------------------
回复"q"退出
==================""")
            code = get_user_input(timeout=120)
            if not code or code == 'q':
                sender.reply("✅ 已退出")
                return

            sender.reply("🔄 正在登录并生成CK，请稍候...")
            login_ok, _, login_msg = api.login(phone, str(code).strip())
            if not login_ok:
                sender.reply(f"❌ 登录失败: {login_msg}")
                return

            welfare_url = api.generate_welfare_url()
            if not welfare_url:
                sender.reply("❌ 短信登录成功，但生成CK失败")
                return

            save_sukan_device_profile(welfare_url)
            process_account_binding(
                welfare_url,
                api.zyeid,
                api.zyeid,
                "速看用户",
                remark,
                phone=phone,
                login_type="sms"
            )
            return

        sender.reply("❌ 无效选择，请输入 1 或 2")
            
    except Exception as e:
        logger.error("绑定账号失败: " + str(e))
        sender.reply("❌ 绑定失败: " + str(e))


def process_account_binding(submission_str, device_id, user_id, nickname, remark="", phone="", login_type="ck"):
    """处理账号绑定逻辑"""
    account_key = str(phone or user_id).strip() # 优先使用手机号归一化，兼容旧zyeid
    full_cred = submission_str # 存入完整的 Query String (包含所有p参数)
    
    try:
        old_account_key = None
        if phone:
            old_account_key = find_account_by_phone(userid, phone)
            if not old_account_key and str(user_id) != account_key:
                old_account_key = str(user_id)
        elif str(user_id) != account_key:
            old_account_key = str(user_id)

        if old_account_key and old_account_key != account_key:
            migrate_account_binding_if_needed(userid, old_account_key, account_key)

        vip, _, is_authorized = get_account_auth_status(account_key)

        if is_authorized:
            auth_status = f'✅ 已授权 ({vip})'
            next_step = f'发送 {config["randommanagecommand"]} 可管理账号'
        else:
            auth_status = '⚠️ 未授权'
            next_step = f'发送 {config["randommanagecommand"]} 进行授权以自动激活'
        
        remark_info = f"\n📝 备注: {remark}" if remark else ""
        
        exists = account_key in AccountManager.get_accounts(userid)
        if exists:
            AccountManager.update_account_credentials(account_key, full_cred)
            logger.info("更新已存在账号的凭证: " + account_key)
        else:
            AccountManager.add_account(userid, account_key)
            enc = encrypt_token(full_cred)
            middleware.bucketSet(bucket='dd_sk_token', key=account_key, value=enc)
            logger.info("添加新账号: " + account_key)

        set_account_meta(account_key, {
            "phone": str(phone or "").strip(),
            "zyeid": str(user_id or "").strip(),
            "device_id": str(device_id or "").strip(),
            "login_type": str(login_type or "ck").strip(),
            "last_login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account_key, remark)
        
        ql_msg = ""
        try:
            sync_result = sync_account_env(account_key, full_cred, nickname, remark)
            if sync_result == 'updated':
                ql_msg = "\n🔄 状态: ✅ 已同步到系统"
            elif sync_result == 'added':
                ql_msg = "\n🔄 状态: ✅ 已添加到系统"
            elif sync_result == 'removed':
                ql_msg = "\n🔄 状态: ⏸️ 未授权，已从系统移除，仅保留本地"
            else:
                ql_msg = "\n🔄 状态: ⏸️ 未授权，仅保留本地"
        except Exception as e:
            logger.error("更新系统变量失败: " + str(e))
            ql_msg = "\n🔄 状态: ❌ 系统同步失败"
        
        success_msg = f"""
=====速看账号绑定=====
✅ 绑定成功!
🔑 ID: {account_key}{remark_info}
🔐 授权: {auth_status}{ql_msg}
⏰ 下一步操作: 
   {next_step}
=================="""
        
        sender.reply(success_msg)
        logger.info(f"用户 {userid} 绑定账号成功: {account_key}, 备注: {remark}")
        
    except Exception as e:
        logger.error("处理账号绑定失败: " + str(e))
        raise


# ===================== 支付处理函数 =====================
def process_payment(project, months, accountVip, full_credential, nickname, account_key, remark=""):
    """处理支付流程"""
    try:
        zsm = config['zsm']
        use_ma_pay = config['use_ma_pay']
        
        ma_pay_enabled = False
        if use_ma_pay:
            ma_pay_config = {
                'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
                'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
                'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
                'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            }
            if ma_pay_config['switch'].lower() == 'true' and all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                ma_pay_enabled = True
        
        epay_enabled = bool(config['epay_url'] and config['epay_pid'] and config['epay_key'])

        if not zsm and not ma_pay_enabled and not epay_enabled and config['skcoin'] <= 0:
            sender.reply('❌ 未配置任何支付方式,请联系管理员!')
            return False
        
        money = Decimal(months) * config['skVipmoney']
        points_needed = config['skcoin'] * months
        user_points = middleware.bucketGet(config['points_bucket'], userid) or '0'
        
        options = []
        option_counter = 1
        
        if zsm:
            options.append({
                'id': option_counter,
                'type': 'wechat',
                'name': '微信支付',
                'amount': money,
                'unit': '元',
                'months': months
            })
            option_counter += 1
        
        if ma_pay_enabled:
            options.append({
                'id': option_counter,
                'type': 'mapay',
                'name': '码支付',
                'amount': money,
                'unit': '元',
                'months': months,
                'config': ma_pay_config
            })
            option_counter += 1

        if epay_enabled:
            if config['epay_alipay']:
                options.append({'id': option_counter, 'type': 'epay', 'channel': 'alipay', 'name': '易支付支付宝', 'amount': money, 'unit': '元', 'months': months})
                option_counter += 1
            if config['epay_wxpay']:
                options.append({'id': option_counter, 'type': 'epay', 'channel': 'wxpay', 'name': '易支付微信', 'amount': money, 'unit': '元', 'months': months})
                option_counter += 1
            if config['epay_qqpay']:
                options.append({'id': option_counter, 'type': 'epay', 'channel': 'qqpay', 'name': '易支付QQ', 'amount': money, 'unit': '元', 'months': months})
                option_counter += 1
        
        if config['skcoin'] > 0:
            options.append({
                'id': option_counter,
                'type': 'points',
                'name': '积分支付',
                'amount': points_needed,
                'unit': '积分',
                'months': months,
                'user_points': user_points
            })
        
        pay_menu = """
=====选择支付方式====="""
        
        for option in options:
            if option['type'] == 'points':
                pay_menu += f"""
{option['id']}️⃣ {option['name']}
   🎯 {option['amount']}{option['unit']}/{option['months']}月
   💫 当前积分: {option['user_points']}"""
            else:
                pay_menu += f"""
{option['id']}️⃣ {option['name']}
   💰 {option['amount']}{option['unit']}/{option['months']}月"""
        
        pay_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""
        
        sender.reply(pay_menu)
        
        choice = get_user_input(timeout=60000)
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消支付")
            return False
        
        try:
            choice_num = int(choice)
            selected_option = None
            for option in options:
                if option['id'] == choice_num:
                    selected_option = option
                    break
            
            if not selected_option:
                sender.reply("❌ 无效的选择")
                return False
            
            payment_success = False
            if selected_option['type'] == 'wechat':
                payment_success = process_wechat_pay(project, selected_option['amount'], selected_option['months'])
            elif selected_option['type'] == 'mapay':
                payment_success = process_mapay_pay(project, selected_option['amount'], selected_option['months'], selected_option['config'])
            elif selected_option['type'] == 'epay':
                payment_success = process_epay_pay(selected_option['amount'], selected_option['months'], selected_option['channel'])
            elif selected_option['type'] == 'points':
                payment_success = process_points_pay(selected_option['amount'], selected_option['months'])
            
            if payment_success:
                days = months * 30
                new_time = empower(accountVip, days)
                middleware.bucketSet(bucket='dd_sk_auth', key=account_key, value=new_time)
                
                if full_credential:
                    try:
                        sync_account_env(account_key, full_credential, nickname, remark)
                    except Exception:
                        pass
                
                sender.reply(f"授权成功: {new_time}")
                return True
            return False
            
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return False
            
    except Exception as e:
        logger.error("支付处理失败: " + str(e))
        sender.reply(f"""
==================
    系统错误
==================
❌ 支付处理异常
------------------
错误信息: {str(e)}
==================""")
        return False


def process_wechat_pay(project, amount, months):
    """处理微信支付"""
    try:
        if sender.atWaitPay():
            sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
            return False
        
        pay_msg = f"""
=====微信扫码支付====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
        sender.reply(pay_msg)
        sender.replyImage(config['zsm'])
        
        payment_result = sender.waitPay("q", 100 * 1000)
        
        if str(payment_result) == 'q':
            sender.reply('✅ 已取消支付')
            return False
        
        money_received = 0
        payer = ""
        
        if isinstance(payment_result, dict):
            if payment_result.get('Type') in ['微信赞赏', '微信收款']:
                money_received = float(payment_result.get('Money', 0))
                payer = payment_result.get('FromName', '')
            elif payment_result.get('Money'):
                money_received = float(payment_result.get('Money', 0))
                payer = payment_result.get('FromName', '')
            elif payment_result.get('money'):
                money_received = float(payment_result.get('money', 0))
                payer = payment_result.get('fromName', '')
        else:
            try:
                result_data = json.loads(payment_result)
                if result_data.get('Type') in ['微信赞赏', '微信收款']:
                    money_received = float(result_data.get('Money', 0))
                    payer = result_data.get('FromName', '')
                else:
                    money_received = float(result_data.get('Money', 0))
                    payer = result_data.get('FromName', '')
            except:
                sender.reply("❌ 无法解析支付结果")
                return False
        
        if money_received >= float(amount):
            return True
        else:
            sender.reply(f"""
=====支付金额错误=====
💰 应付: {amount}元
💳 实付: {money_received}元
{f'👤 付款人: {payer}' if payer else ''}

❗ 请联系管理员处理退款！
==================""")
            return False
            
    except Exception as e:
        logger.error("微信支付失败: " + str(e))
        sender.reply("❌ 支付失败: " + str(e))
        return False


def process_mapay_pay(project, amount, months, ma_pay_config):
    """处理码支付"""
    try:
        out_trade_no = f"SK_{int(time.time())}{userid}"
        
        params = {
            'pid': ma_pay_config['pid'],
            'type': 'alipay',
            'out_trade_no': out_trade_no,
            'name': f"速看授权-{months}个月",
            'money': str(amount),
            'notify_url': '',
            'return_url': '',
            'param': userid
        }
        
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
        
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        
        gateway = ma_pay_config['gateway']
        if not gateway.endswith('/'):
            gateway += '/'
        submit_url = gateway + 'submit.php'
        
        response = requests.post(submit_url, data=params, timeout=30)
        
        if 'location.href' in response.text:
            match = re.search(r'location\.href\s*=\s*[\'"](.*?)[\'"]', response.text)
            if match:
                pay_url = match.group(1)
                if not pay_url.startswith('http'):
                    pay_url = gateway + pay_url
                    
                sender.reply(f"""
=====码支付=====
🎫 商品: {project}
💰 金额: {amount}元
⏰ 有效期: 5分钟
------------------
请点击链接完成支付:
{pay_url}
==================""")
                sender.reply("⚠️ 请完成支付后联系管理员确认")
                return True
        
        sender.reply("❌ 创建支付订单失败!")
        return False
        
    except Exception as e:
        logger.error("码支付失败: " + str(e))
        sender.reply("❌ 支付失败: " + str(e))
        return False


def process_points_pay(points_needed, months):
    """处理积分支付"""
    try:
        user_points = int(middleware.bucketGet(config['points_bucket'], userid) or '0')
        
        if user_points < points_needed:
            sender.reply(f"""
==================
    积分不足
==================
👤 当前积分: {user_points}
📍 需要积分: {points_needed}
==================""")
            return False
        
        confirm_msg = f"""
==================
    积分支付确认
==================
💫 消耗积分: {points_needed}
⏰ 授权时长: {months}月
------------------
确认请回复【y】
取消请回复【n】
=================="""
        sender.reply(confirm_msg)
        
        yesorno = get_user_input(timeout=120000)
        if yesorno and yesorno.lower() in ['y', '是', 'yes']:
            new_balance = user_points - points_needed
            middleware.bucketSet(config['points_bucket'], userid, str(new_balance))
            logger.info(f"用户 {userid} 消耗积分 {points_needed}，剩余 {new_balance}")
            return True
        else:
            sender.reply("✅ 已取消支付")
            return False
            
    except Exception as e:
        logger.error("积分支付失败: " + str(e))
        sender.reply("❌ 积分支付失败: " + str(e))
        return False


# ===================== 速看账号管理 =====================
def xy_manage():
    """速看账号管理"""
    accounts = AccountManager.get_accounts(userid)
    
    if not accounts:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {config['randomsigncommand']} 绑定
==================""")
        return
    
    account_remarks = {}
    if config['enable_remark']:
        account_remarks = RemarkManager.get_all_remarks(userid)
    
    count = 1
    account_list = """
======我的速看账号====="""
    today_time = str(datetime.now().date())
    
    try:
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=f'{account}')
            if not accountVip:
                vip_status = '⚠️ 未授权'
            elif accountVip < today_time:
                vip_status = '❌ 已过期'
            else:
                vip_status = f'✅ {accountVip}'
            
            remark = ""
            if config['enable_remark']:
                remark = account_remarks.get(account, "")
            remark_display = f" - {remark}" if remark else ""
            
            account_list += f"""
------------------
[{count}] 账号信息
🔑 ID: {account}{remark_display}
🔐 授权: {vip_status}"""
            count += 1
        
        account_list += """
------------------
[b] 批量授权所有账号
[d] 批量删除所有账号
[q] 退出管理
=================="""
        
        sender.reply(account_list)
        
        response = get_user_input(timeout=60)
        if response is None:
            sender.reply('⏰ 操作超时,已退出')
            return
        elif response == 'q':
            sender.reply('✅ 已退出管理')
            return
        
        if response.lower() == 'b':
            batch_auth_all_accounts(accounts, account_remarks)
            return
        elif response.lower() == 'd':
            batch_delete_all_accounts(accounts)
            return
        
        try:
            choice_num = int(response)
            if choice_num < 1 or choice_num >= count:
                sender.reply('❌ 输入的序号无效')
                return
        except ValueError:
            sender.reply('❌ 输入必须是数字')
            return
        
        manage_single_account(accounts[choice_num - 1], account_remarks)
            
    except Exception as e:
        logger.error("账号管理失败: " + str(e))
        sender.reply(f"""
=====账号处理错误=====
❌ 账号列表处理失败
⚠️ 错误: {str(e)}
==================""")


def manage_single_account(account, account_remarks):
    """管理单个账号"""
    try:
        encrypted_cred = middleware.bucketGet(bucket='dd_sk_token', key=f'{account}')
        full_cred = decrypt_token(encrypted_cred) if encrypted_cred else ""
        
        accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=f'{account}')
        
        remark = ""
        if config['enable_remark']:
            remark = account_remarks.get(account, "")
        
        today_time = str(datetime.now().date())
        
        if not accountVip:
            vip_status = '⚠️ 未授权'
        elif accountVip < today_time:
            vip_status = '❌ 已过期'
        else:
            vip_status = f'✅ {accountVip}'
        
        remark_info = f"\n📝 备注: {remark}" if remark else ""
        
        account_info = f"""
=====账号详情=====
🔑 ID: {account}{remark_info}
🔐 授权: {vip_status}
=================="""
        sender.reply(account_info)

        menu_options = []
        option_counter = 1
        
        menu_options.append(f"[{option_counter}] 授权账号")
        option_counter += 1
        
        menu_options.append(f"[{option_counter}] 删除账号")
        option_counter += 1
        
        if config['enable_remark']:
            menu_options.append(f"[{option_counter}] 修改备注")
            option_counter += 1
        
        menu = "=====账号管理=====\n" + "\n".join(menu_options)
        menu += """
------------------
回复数字选择功能
回复"q"退出操作
=================="""
        sender.reply(menu)
        
        choice_response = get_user_input(timeout=60)
        if choice_response is None:
            sender.reply('⏰ 操作超时,已退出')
            return
        elif choice_response == 'q':
            sender.reply('✅ 已退出管理')
            return
        
        try:
            choice_num = int(choice_response)
        except ValueError:
            sender.reply('❌ 输入必须是数字')
            return
        
        actual_option_index = 1
        
        # 1. 授权账号
        if choice_num == actual_option_index:
            auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
            sender.reply(auth_guide)
            
            mes_response = get_user_input(timeout=60)
            if mes_response is None:
                sender.reply('⏰ 操作超时,已退出')
                return
            elif mes_response.lower() == 'q':
                sender.reply('✅ 已退出管理')
                return
            
            try:
                months = int(mes_response)
                if months <= 0 or months > 999:
                    sender.reply('❌ 请输入1-999之间的数字')
                    return
            except ValueError:
                sender.reply('❌ 请输入有效的数字')
                return
            
            payment_result = process_payment(
                project='速看授权',
                months=months,
                accountVip=accountVip,
                full_credential=full_cred,
                nickname=f"用户{account}",
                account_key=account,
                remark=remark
            )
            
            if payment_result:
                days = months * 30
                new_auth_time = empower(empowertime=accountVip, days=days)
                middleware.bucketSet(bucket='dd_sk_auth', key=f'{account}', value=new_auth_time)
                
                # 核心：授权成功后，同步到系统
                if full_cred:
                    try:
                        sync_account_env(account, full_cred, f"用户{account}", remark if config['enable_remark'] else "")
                        sender.reply("🔄 授权成功，已同步到系统！")
                    except Exception as e:
                        logger.error("更新系统变量失败: " + str(e))
                        sender.reply(f"""
=====系统更新失败=====
⚠️ 授权成功但系统数据更新失败
错误: {str(e)}
==================""")
                
                money = Decimal(months) * config['skVipmoney']
                result_msg = f"""
=====订单完成=====
🎈 名称: 速看授权
🎉 数量: {months}个月 ({days}天)
💰 金额: {money}元
📅 到期: {new_auth_time}
==================""" 
                sender.reply(result_msg)
                logger.info(f"用户 {userid} 授权成功: {account} - {months}个月({days}天)")
            return
            
        actual_option_index += 1
        
        # 2. 删除账号
        if choice_num == actual_option_index:
            confirm_msg = """
=====警告=====
确定要删除该账号吗？
此操作不可恢复！
------------------
[y] 确认删除
[n] 取消操作
=================="""
            sender.reply(confirm_msg)
            
            yesorno_response = get_user_input(timeout=60)
            if yesorno_response is None:
                sender.reply('⏰ 操作超时,已退出')
                return
            elif yesorno_response.lower() in ['y', '是', 'yes']:
                AccountManager.remove_account(userid, account)
                remove_account_env_from_system(account)
                
                middleware.bucketDel(bucket='dd_sk_token', key=account)
                middleware.bucketDel(bucket='dd_sk_auth', key=account)
                
                if config['enable_remark']:
                    RemarkManager.delete_account_remark(userid, account)
                
                sender.reply('✅ 账号删除成功!')
                logger.info(f"用户 {userid} 删除账号: {account}")
            else:
                sender.reply('✅ 已取消删除')
            return
            
        actual_option_index += 1
        
        # 3. 修改备注
        if config['enable_remark'] and choice_num == actual_option_index:
            current_remark = remark or "无"
            sender.reply(f"""
=====修改备注=====
当前备注: {current_remark}
------------------
请输入新的备注名
(最多20个字符，回复"n"清空备注)
回复"q"取消操作
==================""")
            
            new_remark_input = get_user_input(timeout=60)
            if new_remark_input is None:
                sender.reply('⏰ 操作超时,已退出')
                return
            elif new_remark_input.lower() == 'q':
                sender.reply('✅ 已取消修改')
                return
            elif new_remark_input.lower() == 'n':
                RemarkManager.delete_account_remark(userid, account)
                if full_cred:
                    try:
                        sync_account_env(account, full_cred, f"用户{account}", "")
                    except Exception as e:
                        logger.error("更新系统变量失败: " + str(e))
                sender.reply('✅ 备注已清空')
                return
            else:
                new_remark = new_remark_input.strip()[:20]
                RemarkManager.set_account_remark(userid, account, new_remark)
                if full_cred:
                    try:
                        sync_account_env(account, full_cred, f"用户{account}", new_remark)
                    except Exception as e:
                        logger.error("更新系统变量失败: " + str(e))
                sender.reply(f'✅ 备注已更新为: {new_remark}')
                return
        
        sender.reply("❌ 无效的选择")
            
    except Exception as e:
        logger.error("账号管理失败: " + str(e))
        sender.reply(f"""
=====账号处理错误=====
❌ 账号管理失败
⚠️ 错误: {str(e)}
==================""")


def batch_auth_all_accounts(accounts, account_remarks):
    """批量授权所有账号"""
    try:
        sender.reply("""
=====批量授权=====
请输入授权月数(如:1)
------------------
注意: 所有账号将统一授权相同月数
------------------
回复数字设置月数
回复"q"退出操作
==================""")
        
        mes_response = get_user_input(timeout=60)
        if mes_response is None:
            sender.reply('⏰ 操作超时,已退出')
            return
        elif mes_response.lower() == 'q':
            sender.reply('✅ 已退出操作')
            return
        
        try:
            months = int(mes_response)
            if months <= 0 or months > 999:
                sender.reply('❌ 请输入1-999之间的数字')
                return
        except ValueError:
            sender.reply('❌ 请输入有效的数字')
            return
        
        total_amount = Decimal(months) * config['skVipmoney'] * len(accounts)
        total_points_needed = config['skcoin'] * months * len(accounts)
        user_points = middleware.bucketGet(config['points_bucket'], userid) or '0'
        
        zsm = config['zsm']
        use_ma_pay = config['use_ma_pay']
        
        ma_pay_enabled = False
        if use_ma_pay:
            ma_pay_config = {
                'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
                'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
                'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
                'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            }
            if ma_pay_config['switch'].lower() == 'true' and all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                ma_pay_enabled = True
        
        epay_enabled = bool(config['epay_url'] and config['epay_pid'] and config['epay_key'])

        if not zsm and not ma_pay_enabled and not epay_enabled and config['skcoin'] <= 0:
            sender.reply('❌ 未配置任何支付方式,请联系管理员!')
            return
        
        options = []
        option_counter = 1
        
        if zsm:
            options.append({
                'id': option_counter,
                'type': 'wechat',
                'name': '微信支付',
                'amount': total_amount,
                'unit': '元',
                'months': months,
                'account_count': len(accounts)
            })
            option_counter += 1
        
        if ma_pay_enabled:
            options.append({
                'id': option_counter,
                'type': 'mapay',
                'name': '码支付',
                'amount': total_amount,
                'unit': '元',
                'months': months,
                'account_count': len(accounts),
                'config': ma_pay_config
            })
            option_counter += 1

        if epay_enabled:
            if config['epay_alipay']:
                options.append({'id': option_counter, 'type': 'epay', 'channel': 'alipay', 'name': '易支付支付宝', 'amount': total_amount, 'unit': '元', 'months': months, 'account_count': len(accounts)})
                option_counter += 1
            if config['epay_wxpay']:
                options.append({'id': option_counter, 'type': 'epay', 'channel': 'wxpay', 'name': '易支付微信', 'amount': total_amount, 'unit': '元', 'months': months, 'account_count': len(accounts)})
                option_counter += 1
            if config['epay_qqpay']:
                options.append({'id': option_counter, 'type': 'epay', 'channel': 'qqpay', 'name': '易支付QQ', 'amount': total_amount, 'unit': '元', 'months': months, 'account_count': len(accounts)})
                option_counter += 1
        
        if config['skcoin'] > 0:
            options.append({
                'id': option_counter,
                'type': 'points',
                'name': '积分支付',
                'amount': total_points_needed,
                'unit': '积分',
                'months': months,
                'account_count': len(accounts),
                'user_points': user_points
            })
        
        pay_menu = f"""
=====批量授权支付=====
📊 操作信息:
• 账号数量: {len(accounts)}个
• 授权时长: {months}个月
• 单个价格: {config['skVipmoney']}元/月
• 单个积分: {config['skcoin']}积分/月
------------------
请选择支付方式:"""
        
        for option in options:
            if option['type'] == 'points':
                pay_menu += f"""
{option['id']}️⃣ {option['name']}
   🎯 需要积分: {option['amount']}{option['unit']}
   💫 当前积分: {option['user_points']}
   📊 账号数量: {option['account_count']}个"""
            else:
                pay_menu += f"""
{option['id']}️⃣ {option['name']}
   💰 支付金额: {option['amount']}{option['unit']}
   📊 账号数量: {option['account_count']}个"""
        
        pay_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""
        
        sender.reply(pay_menu)
        
        choice = get_user_input(timeout=60000)
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消支付")
            return
        
        try:
            choice_num = int(choice)
            selected_option = None
            for option in options:
                if option['id'] == choice_num:
                    selected_option = option
                    break
            
            if not selected_option:
                sender.reply("❌ 无效的选择")
                return
            
            payment_result = False
            if selected_option['type'] == 'wechat':
                payment_result = process_batch_wechat_pay(total_amount, months, len(accounts))
            elif selected_option['type'] == 'mapay':
                payment_result = process_batch_mapay_pay(total_amount, months, len(accounts), selected_option['config'])
            elif selected_option['type'] == 'epay':
                payment_result = process_epay_pay(total_amount, months, selected_option['channel'], "SK_BATCH")
            elif selected_option['type'] == 'points':
                payment_result = process_batch_points_pay(total_points_needed, months, len(accounts), int(user_points))
            
            if not payment_result:
                return
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
        
        success_count = 0
        fail_count = 0
        
        sender.reply(f"⏳ 开始批量授权 {len(accounts)} 个账号...")
        
        for account in accounts:
            try:
                encrypted_cred = middleware.bucketGet(bucket='dd_sk_token', key=account)
                full_cred = decrypt_token(encrypted_cred) if encrypted_cred else ""
                
                if not full_cred:
                    logger.warning(f"账号 {account} 凭证不存在")
                    fail_count += 1
                    continue
                
                accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                days = months * 30
                new_auth_time = empower(empowertime=accountVip, days=days)
                
                middleware.bucketSet(bucket='dd_sk_auth', key=account, value=new_auth_time)
                
                # 批量同步到系统
                try:
                    remark = ""
                    if config['enable_remark']:
                        remark = account_remarks.get(account, "")
                    sync_account_env(account, full_cred, f"用户{account}", remark)
                except Exception as e:
                    logger.error(f"更新系统变量失败: {account} - {str(e)}")
                
                success_count += 1
                logger.info(f"批量授权成功: {account} - {months}个月({days}天)")
                
            except Exception as e:
                logger.error(f"批量授权失败: {account} - {str(e)}")
                fail_count += 1
        
        sender.reply(f"""
=====批量授权完成=====
📊 账号总数: {len(accounts)}个
✅ 成功授权: {success_count}个
❌ 授权失败: {fail_count}个
📅 授权时长: {months}个月 ({days}天)
------------------
{'⚠️ 注意: 部分账号授权失败，请检查账号凭证是否有效' if fail_count > 0 else '🎉 所有账号授权成功!'}
==================""")
        
    except Exception as e:
        logger.error(f"批量授权失败: {str(e)}")
        sender.reply(f"""
=====批量授权错误=====
❌ 批量授权过程出错
⚠️ 错误: {str(e)}
==================""")
        return


def process_batch_wechat_pay(amount, months, account_count):
    """处理批量授权的微信支付"""
    try:
        if sender.atWaitPay():
            sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
            return False
        
        pay_msg = f"""
=====微信扫码支付====
🎫 商品: 速看批量授权
📊 账号数量: {account_count}个
📅 时长: {months}月/个
💰 总金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
        sender.reply(pay_msg)
        sender.replyImage(config['zsm'])
        
        payment_result = sender.waitPay("q", 100 * 1000)
        
        if str(payment_result) == 'q':
            sender.reply('✅ 已取消支付')
            return False
        
        money_received = 0
        payer = ""
        
        if isinstance(payment_result, dict):
            if payment_result.get('Type') in ['微信赞赏', '微信收款']:
                money_received = float(payment_result.get('Money', 0))
                payer = payment_result.get('FromName', '')
            elif payment_result.get('Money'):
                money_received = float(payment_result.get('Money', 0))
                payer = payment_result.get('FromName', '')
            elif payment_result.get('money'):
                money_received = float(payment_result.get('money', 0))
                payer = payment_result.get('fromName', '')
        else:
            try:
                result_data = json.loads(payment_result)
                if result_data.get('Type') in ['微信赞赏', '微信收款']:
                    money_received = float(result_data.get('Money', 0))
                    payer = result_data.get('FromName', '')
                else:
                    money_received = float(result_data.get('Money', 0))
                    payer = result_data.get('FromName', '')
            except:
                sender.reply("❌ 无法解析支付结果")
                return False
        
        if money_received >= float(amount):
            sender.reply(f"""
=====支付成功=====
💰 支付金额: {money_received}元
👤 付款人: {payer}
✅ 开始批量授权...
==================""")
            return True
        else:
            sender.reply(f"""
=====支付金额错误=====
💰 应付: {amount}元
💳 实付: {money_received}元
{f'👤 付款人: {payer}' if payer else ''}

❗ 请联系管理员处理退款！
==================""")
            return False
            
    except Exception as e:
        logger.error(f"批量授权微信支付失败: {str(e)}")
        sender.reply(f"❌ 支付失败: {str(e)}")
        return False


def process_batch_mapay_pay(amount, months, account_count, ma_pay_config):
    """处理批量授权的码支付"""
    try:
        out_trade_no = f"SK_BATCH_{int(time.time())}{userid}"
        
        params = {
            'pid': ma_pay_config['pid'],
            'type': 'alipay',
            'out_trade_no': out_trade_no,
            'name': f"速看批量授权-{account_count}个账号-{months}个月",
            'money': str(amount),
            'notify_url': '',
            'return_url': '',
            'param': userid
        }
        
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
        
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        
        gateway = ma_pay_config['gateway']
        if not gateway.endswith('/'):
            gateway += '/'
        submit_url = gateway + 'submit.php'
        
        response = requests.post(submit_url, data=params, timeout=30)
        
        if 'location.href' in response.text:
            match = re.search(r'location\.href\s*=\s*[\'"](.*?)[\'"]', response.text)
            if match:
                pay_url = match.group(1)
                if not pay_url.startswith('http'):
                    pay_url = gateway + pay_url
                    
                sender.reply(f"""
=====码支付=====
🎫 商品: 速看批量授权
📊 账号数量: {account_count}个
📅 时长: {months}月/个
💰 总金额: {amount}元
⏰ 有效期: 5分钟
------------------
请点击链接完成支付:
{pay_url}
==================""")
                sender.reply("⚠️ 请完成支付后联系管理员确认")
                return True
        
        sender.reply("❌ 创建支付订单失败!")
        return False
        
    except Exception as e:
        logger.error(f"批量授权码支付失败: {str(e)}")
        sender.reply(f"❌ 支付失败: {str(e)}")
        return False


def process_batch_points_pay(points_needed, months, account_count, user_points):
    """处理批量授权的积分支付"""
    try:
        if user_points < points_needed:
            sender.reply(f"""
==================
    积分不足
==================
👤 当前积分: {user_points}
📍 需要积分: {points_needed}
📊 账号数量: {account_count}个
📅 时长: {months}月/个
==================""")
            return False
        
        confirm_msg = f"""
==================
    积分支付确认
==================
💫 消耗积分: {points_needed}
📊 账号数量: {account_count}个
📅 时长: {months}月/个
------------------
确认请回复【y】
取消请回复【n】
=================="""
        sender.reply(confirm_msg)
        
        yesorno = get_user_input(timeout=120000)
        if yesorno and yesorno.lower() in ['y', '是', 'yes']:
            new_balance = user_points - points_needed
            middleware.bucketSet(config['points_bucket'], userid, str(new_balance))
            logger.info(f"用户 {userid} 批量授权消耗积分 {points_needed}，剩余 {new_balance}")
            sender.reply(f"""
=====积分支付成功=====
💫 消耗积分: {points_needed}
📊 剩余积分: {new_balance}
✅ 开始批量授权...
==================""")
            return True
        else:
            sender.reply("✅ 已取消支付")
            return False
            
    except Exception as e:
        logger.error(f"批量授权积分支付失败: {str(e)}")
        sender.reply(f"❌ 积分支付失败: {str(e)}")
        return False


def batch_delete_all_accounts(accounts):
    """批量删除所有账号"""
    try:
        sender.reply(f"""
=====批量删除警告=====
⚠️ 危险操作警告!
------------------
📊 操作影响: {len(accounts)}个账号
❌ 此操作将永久删除:
   • 所有账号绑定
   • 所有授权信息
   • 所有账号凭证
   • 所有备注信息
   • 所有系统数据
------------------
此操作不可恢复!
------------------
确认请回复【确认删除】
取消请回复其他内容
==================""")
        
        confirm = get_user_input(timeout=60)
        if confirm != "确认删除":
            sender.reply('✅ 已取消批量删除')
            return
        
        success_count = 0
        fail_count = 0
        
        sender.reply(f"⏳ 开始批量删除 {len(accounts)} 个账号...")
        
        for account in accounts:
            try:
                remove_account_env_from_system(account)
                
                middleware.bucketDel(bucket='dd_sk_token', key=account)
                middleware.bucketDel(bucket='dd_sk_auth', key=account)
                
                if config['enable_remark']:
                    RemarkManager.delete_account_remark(userid, account)
                
                success_count += 1
                logger.info(f"批量删除成功: {account}")
                
            except Exception as e:
                logger.error(f"批量删除失败: {account} - {str(e)}")
                fail_count += 1
        
        middleware.bucketDel(bucket='dd_sk_user', key=userid)
        
        sender.reply(f"""
=====批量删除完成=====
📊 账号总数: {len(accounts)}个
✅ 成功删除: {success_count}个
❌ 删除失败: {fail_count}个
------------------
{'⚠️ 注意: 部分账号删除失败' if fail_count > 0 else '🗑️ 所有账号已成功删除!'}
------------------
💡 提示: 如需重新绑定，请使用 {config['randomsigncommand']}
==================""")
        
    except Exception as e:
        logger.error(f"批量删除失败: {str(e)}")
        sender.reply(f"""
=====批量删除错误=====
❌ 批量删除过程出错
⚠️ 错误: {str(e)}
==================""")
        return


# ===================== 管理员授权功能（按天计算） =====================
def admin_auth_options():
    """管理员授权选项菜单"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 您没有权限执行此操作
只有管理员可以执行授权操作
==================""")
        exit(0)
    
    try:
        sender.reply("""
=====速看管理员管理=====

[1] 一键授权所有用户
[2] 指定用户授权
[3] 数据总览
[4] 用户账号预览
[5] 反查账号归属
[6] 同步面板变量
[7] 执行维护清理

------------------
回复数字选择功能
回复"q"退出
==================""")
        
        choice = get_user_input(timeout=60)
        if choice is None:
            sender.reply("⏰ 操作超时，已退出")
            return
        elif choice.lower() == 'q':
            sender.reply("✅ 已退出授权管理")
            return
        
        if choice == '1':
            admin_auth_all_users()
        elif choice == '2':
            admin_auth_specific_user()
        elif choice == '3':
            admin_overview()
        elif choice == '4':
            admin_user_ck_preview()
        elif choice == '5':
            admin_find_account()
        elif choice == '6':
            admin_sync_panel()
        elif choice == '7':
            clean_expired_accounts(force_report=True, clean_invalid=True)
        else:
            sender.reply("❌ 请输入有效的选项 (1-7)")
        
    except Exception as e:
        logger.error(f"管理员授权选项处理失败: {str(e)}")
        sender.reply(f"❌ 操作失败: {str(e)}")


def collect_admin_stats():
    stats = {
        "users": 0, "accounts": 0, "authorized": 0, "unauthorized": 0,
        "expired": 0, "expiring": 0, "no_token": 0
    }
    today = datetime.now().date()
    users = AccountManager.get_all_users()
    stats["users"] = len(users)
    for user in users:
        for account in AccountManager.get_accounts(user):
            try:
                stats["accounts"] += 1
                if not middleware.bucketGet(bucket='dd_sk_token', key=account):
                    stats["no_token"] += 1
                vip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                if not vip:
                    stats["unauthorized"] += 1
                    continue
                try:
                    vip_date = datetime.strptime(str(vip), "%Y-%m-%d").date()
                except Exception:
                    stats["expired"] += 1
                    continue
                if vip_date < today:
                    stats["expired"] += 1
                else:
                    stats["authorized"] += 1
                    if (vip_date - today).days <= config['reminder_days']:
                        stats["expiring"] += 1
            except Exception:
                pass
    return stats

def admin_overview():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return
    sender.reply("⏳ 正在统计数据，请稍候...")
    stats = collect_admin_stats()
    sender.reply(f"""=====速看数据总览=====
👥 用户数: {stats['users']}
📦 账号数: {stats['accounts']}
✅ 授权中: {stats['authorized']}
⚠️ 未授权: {stats['unauthorized']}
❌ 已过期: {stats['expired']}
⏰ 即将到期: {stats['expiring']}
🔑 缺少配置: {stats['no_token']}
==================""")

def send_long_admin_message(title, lines, footer="==================", max_len=1500):
    if not lines:
        sender.reply(f"{title}\n📭 暂无数据\n{footer}")
        return
    chunks = []
    current = title
    for line in lines:
        add_text = "\n" + line
        if len(current) + len(add_text) + len(footer) + 20 > max_len and current != title:
            chunks.append(current)
            current = title
        current += add_text
    chunks.append(current)
    for idx, chunk in enumerate(chunks, 1):
        page_tip = f"\n-----第 {idx}/{len(chunks)} 段-----" if len(chunks) > 1 else ""
        sender.reply(f"{chunk}{page_tip}\n{footer}")
        time.sleep(0.2)

def admin_user_ck_preview():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return
    sender.reply("⏳ 正在生成用户账号预览，请稍候...")
    today = datetime.now().date()
    rows = []
    total_accounts = 0
    for user in AccountManager.get_all_users():
        try:
            accounts = AccountManager.get_accounts(user)
            if not accounts:
                continue
            auth_count = unauth_count = expired_count = expiring_count = no_token_count = 0
            for account in accounts:
                total_accounts += 1
                if not middleware.bucketGet(bucket='dd_sk_token', key=account):
                    no_token_count += 1
                vip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                if not vip:
                    unauth_count += 1
                    continue
                try:
                    vip_date = datetime.strptime(str(vip), "%Y-%m-%d").date()
                except Exception:
                    expired_count += 1
                    continue
                if vip_date < today:
                    expired_count += 1
                else:
                    auth_count += 1
                    if (vip_date - today).days <= config['reminder_days']:
                        expiring_count += 1
            rows.append({
                "user": str(user), "count": len(accounts), "auth": auth_count,
                "unauth": unauth_count, "expired": expired_count,
                "expiring": expiring_count, "no_token": no_token_count
            })
        except Exception:
            pass
    rows.sort(key=lambda x: x["count"], reverse=True)
    lines = [f"👥 用户数: {len(rows)}  📦 账号总数: {total_accounts}", "------------------"]
    for i, row in enumerate(rows, 1):
        extra = []
        if row["unauth"]: extra.append(f"未授权{row['unauth']}")
        if row["expired"]: extra.append(f"过期{row['expired']}")
        if row["expiring"]: extra.append(f"临期{row['expiring']}")
        if row["no_token"]: extra.append(f"缺配置{row['no_token']}")
        extra_text = f" ({' / '.join(extra)})" if extra else ""
        lines.append(f"[{i}] 用户: {row['user']}\n账号: {row['count']} 个  授权: {row['auth']} 个{extra_text}")
    send_long_admin_message("=====用户账号预览=====", lines)

def admin_find_account():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return
    sender.reply("""=====反查账号归属=====
请输入账号ID/备注/用户ID
回复 q 退出
==================""")
    keyword = get_user_input(timeout=60)
    if not keyword or keyword.lower() == 'q':
        return
    keyword = keyword.strip()
    matches = []
    for user in AccountManager.get_all_users():
        user_match = keyword in str(user)
        remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
        for account in AccountManager.get_accounts(user):
            try:
                remark = remarks.get(account, "")
                vip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                vip_st = '未授权' if not vip else str(vip)
                if user_match or keyword in str(account) or (remark and keyword in remark):
                    remark_text = f"\n📝 备注: {remark}" if remark else ""
                    matches.append(f"👤 用户: {user}\n🔑 账号: {account}{remark_text}\n🔐 授权: {vip_st}")
            except Exception:
                pass
    if not matches:
        sender.reply("❌ 未找到匹配账号")
        return
    msg = f"=====反查结果=====\n共找到 {len(matches)} 条"
    for item in matches[:10]:
        msg += f"\n------------------\n{item}"
    if len(matches) > 10:
        msg += f"\n------------------\n仅显示前10条，共 {len(matches)} 条"
    msg += "\n=================="
    sender.reply(msg)

def admin_sync_panel():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return
    sender.reply("""=====同步面板变量=====
[1] 同步所有授权账号
[2] 同步指定用户账号
------------------
回复数字选择，Q退出
==================""")
    choice = get_user_input(timeout=60)
    if not choice or choice.lower() == 'q':
        return
    if choice == '1':
        users = AccountManager.get_all_users()
        sender.reply("⚠️ 即将同步所有授权账号。\n确认请回复【确认同步】")
        if get_user_input(timeout=60) != "确认同步":
            sender.reply("✅ 已取消同步")
            return
    elif choice == '2':
        sender.reply("请输入用户ID，回复 q 退出")
        target_user = get_user_input(timeout=60)
        if not target_user or target_user.lower() == 'q':
            return
        users = [target_user.strip()]
    else:
        sender.reply("❌ 请输入有效选项")
        return

    today = str(datetime.now().date())
    success = skipped = failed = 0
    sender.reply("⏳ 正在同步，请稍候...")
    for user in users:
        remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
        for account in AccountManager.get_accounts(user):
            try:
                vip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                enc = middleware.bucketGet(bucket='dd_sk_token', key=account)
                full_cred = decrypt_token(enc) if enc else ""
                if not vip or vip < today or not full_cred:
                    skipped += 1
                    continue
                remark = remarks.get(account, "")
                sync_account_env(account, full_cred, f"用户{account}", remark)
                success += 1
            except Exception:
                failed += 1
    sender.reply(f"""=====同步完成=====
✅ 成功: {success}
⏭️ 跳过: {skipped}
❌ 失败: {failed}
==================""")


def admin_auth_all_users():
    """一键授权所有用户的所有账号"""
    try:
        all_users = AccountManager.get_all_users()
        
        if not all_users:
            sender.reply("""
=====用户统计=====
📭 暂无绑定账号的用户
==================""")
            return
        
        total_users = len(all_users)
        total_accounts = 0
        
        for user in all_users:
            accounts = AccountManager.get_accounts(user)
            total_accounts += len(accounts)
        
        sender.reply(f"""
=====用户统计=====
👥 绑定用户数: {total_users}人
🔑 总账号数: {total_accounts}个
==================""")
        
        sender.reply("""
=====设置授权时长=====
请输入授权天数(如:30)
------------------
注意: 所有用户的所有账号
将统一授权相同天数
------------------
回复数字设置天数
回复"q"退出操作
==================""")
        
        days_response = get_user_input(timeout=60)
        if days_response is None:
            sender.reply('⏰ 操作超时,已退出')
            return
        elif days_response.lower() == 'q':
            sender.reply('✅ 已退出操作')
            return
        
        try:
            days = int(days_response)
            if days <= 0 or days > 9999:
                sender.reply('❌ 请输入1-9999之间的数字')
                return
        except ValueError:
            sender.reply('❌ 请输入有效的数字')
            return
        
        sender.reply(f"""
=====操作确认=====
⚠️ 即将执行一键授权
------------------
目标: 所有用户的所有账号
数量: {total_users}用户, {total_accounts}账号
时长: {days}天
------------------
确认请回复【确认授权】
取消请回复其他内容
==================""")
        
        confirm = get_user_input(timeout=60)
        if confirm != "确认授权":
            sender.reply('✅ 已取消操作')
            return
        
        sender.reply(f"⏳ 开始一键授权，共 {total_users} 个用户，{total_accounts} 个账号...")
        
        success_users = 0
        success_accounts = 0
        fail_accounts = 0
        
        for user_id in all_users:
            try:
                accounts = AccountManager.get_accounts(user_id)
                user_success = 0
                
                for account in accounts:
                    try:
                        encrypted_cred = middleware.bucketGet(bucket='dd_sk_token', key=account)
                        full_cred = decrypt_token(encrypted_cred) if encrypted_cred else ""
                        
                        if not full_cred:
                            logger.warning(f"账号 {account} 凭证不存在")
                            fail_accounts += 1
                            continue
                        
                        accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                        new_auth_time = empower(empowertime=accountVip, days=days)
                        
                        middleware.bucketSet(bucket='dd_sk_auth', key=account, value=new_auth_time)
                        
                        try:
                            remark = ""
                            if config['enable_remark']:
                                remark_data = middleware.bucketGet(bucket='dd_sk_remarks', key=f'{user_id}_{account}')
                                if remark_data:
                                    remark = remark_data
                            sync_account_env(account, full_cred, f"用户{account}", remark)
                        except Exception as e:
                            logger.error(f"更新系统变量失败: {account} - {str(e)}")
                        
                        success_accounts += 1
                        user_success += 1
                        logger.info(f"用户 {user_id} 账号 {account} 授权成功 - {days}天")
                        
                    except Exception as e:
                        logger.error(f"账号 {account} 授权失败: {str(e)}")
                        fail_accounts += 1
                
                if user_success > 0:
                    success_users += 1
                    
            except Exception as e:
                logger.error(f"处理用户 {user_id} 失败: {str(e)}")
                continue
        
        sender.reply(f"""
=====一键授权完成=====
📊 用户统计:
• 用户总数: {total_users}人
• 成功用户: {success_users}人
• 失败用户: {total_users - success_users}人

📊 账号统计:
• 账号总数: {total_accounts}个
• 成功授权: {success_accounts}个
• 授权失败: {fail_accounts}个
• 授权时长: {days}天
------------------
{'⚠️ 注意: 部分账号授权失败' if fail_accounts > 0 else '🎉 所有账号授权成功!'}
==================""")
        
    except Exception as e:
        logger.error(f"一键授权失败: {str(e)}")
        sender.reply(f"""
=====一键授权错误=====
❌ 一键授权过程出错
⚠️ 错误: {str(e)}
==================""")
        return


def admin_auth_specific_user():
    """管理员给指定QQ用户授权"""
    try:
        sender.reply("""
=====指定用户授权=====
请回复要授权的QQ号
------------------
格式: 纯数字QQ号
例: 123456789
------------------
回复"q"退出操作
==================""")
        
        target_qq = get_user_input(timeout=60)
        if target_qq is None:
            sender.reply("⏰ 操作超时，已退出")
            return
        elif target_qq.lower() == 'q':
            sender.reply("✅ 已退出操作")
            return
        
        if not target_qq.isdigit():
            sender.reply("""
=====格式错误=====
❌ QQ号必须是纯数字
请重新输入
==================""")
            return
        
        target_qq = str(target_qq)
        target_accounts = AccountManager.get_accounts(target_qq)
        
        if not target_accounts:
            sender.reply(f"""
=====账号信息=====
❌ QQ用户 {target_qq} 未绑定任何账号
请让用户先使用 {config['randomsigncommand']} 绑定账号
==================""")
            return
        
        account_remarks = {}
        if config['enable_remark']:
            account_remarks = RemarkManager.get_all_remarks(target_qq)
        
        today_time = str(datetime.now().date())
        account_list = f"""
=====QQ用户 {target_qq} 的账号====="""
        
        for i, account in enumerate(target_accounts, 1):
            accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
            if not accountVip:
                vip_status = '未授权'
            elif accountVip < today_time:
                vip_status = f'已过期({accountVip})'
            else:
                vip_status = f'已授权({accountVip})'
            
            remark = account_remarks.get(account, "")
            remark_display = f" - {remark}" if remark else ""
            account_list += f"""
[{i}] {account}{remark_display} - {vip_status}"""
        
        account_list += """
------------------
回复数字选择账号
回复"a"授权所有账号
回复"q"退出操作
=================="""
        
        sender.reply(account_list)
        
        account_choice = get_user_input(timeout=60)
        
        if account_choice is None:
            sender.reply("⏰ 操作超时，已退出")
            return
        elif account_choice.lower() == 'q':
            sender.reply("✅ 已退出操作")
            return
        
        if account_choice.lower() == 'a':
            sender.reply("""
=====批量授权=====
请输入授权天数(如:30)
------------------
回复数字设置天数
回复"q"退出操作
==================""")
            
            days_response = get_user_input(timeout=60)
            if days_response is None:
                sender.reply('⏰ 操作超时,已退出')
                return
            elif days_response.lower() == 'q':
                sender.reply('✅ 已退出操作')
                return
            
            try:
                days = int(days_response)
                if days <= 0 or days > 9999:
                    sender.reply('❌ 请输入1-999之间的数字')
                    return
            except ValueError:
                sender.reply('❌ 请输入有效的数字')
                return
            
            success_count = 0
            for account in target_accounts:
                try:
                    encrypted_cred = middleware.bucketGet(bucket='dd_sk_token', key=account)
                    full_cred = decrypt_token(encrypted_cred) if encrypted_cred else ""
                    
                    if full_cred:
                        accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                        new_vip = empower(empowertime=accountVip, days=days)
                        
                        middleware.bucketSet(bucket='dd_sk_auth', key=account, value=new_vip)
                        
                        try:
                            remark = ""
                            if config['enable_remark']:
                                remark = account_remarks.get(account, "")
                            sync_account_env(account, full_cred, f"用户{account}", remark)
                        except Exception as e:
                            logger.error(f"更新系统变量失败: {str(e)}")
                        
                        success_count += 1
                        logger.info(f"管理员给QQ用户 {target_qq} 授权账号 {account} - {days}天")
                except Exception as e:
                    logger.error(f"授权账号 {account} 失败: {str(e)}")
                    continue
            
            sender.reply(f"""
=====批量授权完成=====
✅ 成功授权: {success_count}/{len(target_accounts)}个账号
📅 授权时长: {days}天
👤 目标用户: QQ {target_qq}
==================""")
            
        else:
            try:
                account_index = int(account_choice) - 1
                if account_index < 0 or account_index >= len(target_accounts):
                    sender.reply("❌ 请输入有效的序号")
                    return

                account = target_accounts[account_index]
                
                remark = ""
                remark_display = ""
                if config['enable_remark']:
                    remark = account_remarks.get(account, "")
                    remark_display = f" - {remark}" if remark else ""
                
                sender.reply(f"""
=====授权账号=====
目标账号: {account}{remark_display}
目标用户: QQ {target_qq}
------------------
请输入授权天数(如:30)
回复数字设置天数
回复"q"退出操作
==================""")
                
                days_response = get_user_input(timeout=60)
                if days_response is None:
                    sender.reply('⏰ 操作超时,已退出')
                    return
                elif days_response.lower() == 'q':
                    sender.reply('✅ 已退出操作')
                    return
                
                try:
                    days = int(days_response)
                    if days <= 0 or days > 9999:
                        sender.reply('❌ 请输入1-999之间的数字')
                        return
                except ValueError:
                    sender.reply('❌ 请输入有效的数字')
                    return
                
                encrypted_cred = middleware.bucketGet(bucket='dd_sk_token', key=account)
                full_cred = decrypt_token(encrypted_cred) if encrypted_cred else ""
                
                if not full_cred:
                    sender.reply(f"""
=====授权失败=====
❌ 账号 {account} 未找到凭证
请让用户重新绑定账号
==================""")
                    return
                
                accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                new_vip = empower(empowertime=accountVip, days=days)
                
                middleware.bucketSet(bucket='dd_sk_auth', key=account, value=new_vip)
                
                try:
                    remark = ""
                    if config['enable_remark']:
                        remark = account_remarks.get(account, "")
                    sync_account_env(account, full_cred, f"用户{account}", remark)
                except Exception as e:
                    logger.error(f"更新系统变量失败: {str(e)}")
                    sender.reply(f"""
=====系统更新失败=====
⚠️ 授权成功但系统数据更新失败
错误: {str(e)}
==================""")
                
                sender.reply(f"""
=====授权成功=====
✅ 授权完成!
👤 目标用户: QQ {target_qq}
🔑 目标账号: {account}{remark_display}
📅 授权时长: {days}天
⏰ 到期时间: {new_vip}
==================""")
                logger.info(f"管理员给QQ用户 {target_qq} 授权账号 {account} - {days}天")
                
            except ValueError:
                sender.reply("❌ 请输入有效的序号")
                return

    except Exception as e:
        logger.error(f"管理员授权失败: {str(e)}")
        sender.reply(f"""
=====授权失败=====
❌ 授权过程出错
错误: {str(e)}
==================""")
        return


def clean_expired_accounts(force_report=False, clean_invalid=False):
    """定时任务：过期提醒与清理"""
    # 无论是定时任务自动调用，还是管理员手动触发，都执行这套逻辑。
    
    users = middleware.bucketAllKeys(bucket='dd_sk_user')
    manual_run = force_report or (usermessage in ['速看清理', '清理速看'])
    clean_invalid = clean_invalid or manual_run

    # 如果是管理员手动触发，提示一下
    if sender.isAdmin() and manual_run:
        sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n⚙️ 提醒天数: {config['reminder_days']}天\n🧹 附加检查: 青龙残留变量\n🗑️ 手动清理: 未授权/缺配置账号\n⏳ 处理中...")

    cleaned_count = 0
    invalid_cleaned_count = 0
    reminded_count = 0
    today_date = datetime.now().date()
    reminder_days_cfg = config['reminder_days']

    for user in users:
        try:
            accounts = AccountManager.get_accounts(user)
            if not accounts:
                continue
            
            valid_accounts = []
            user_has_change = False
            
            # 为当前循环的用户创建一个临时的发送者对象，用于发送通知
            try:
                user_sender = middleware.Sender(user)
            except:
                logger.error(f"无法创建用户 {user} 的发送对象")
                continue

            for account in accounts:
                accountVip = middleware.bucketGet(bucket='dd_sk_auth', key=account)
                encrypted_cred = middleware.bucketGet(bucket='dd_sk_token', key=account)
                
                if clean_invalid and (not accountVip or not encrypted_cred):
                    try:
                        remove_account_env_from_system(account)
                    except Exception as e:
                        logger.error(f"移除无效账号系统残留失败: {account} - {str(e)}")
                    try:
                        middleware.bucketDel(bucket='dd_sk_token', key=account)
                    except Exception:
                        pass
                    try:
                        middleware.bucketDel(bucket='dd_sk_auth', key=account)
                    except Exception:
                        pass
                    if config['enable_remark']:
                        RemarkManager.delete_account_remark(user, account)
                    invalid_cleaned_count += 1
                    user_has_change = True
                    logger.info(f"手动清理未授权/缺配置账号: {user} - {account}")
                    continue
                
                # 未授权账号仅保留在本地，同时兜底移除系统残留变量
                if not accountVip:
                    valid_accounts.append(account)
                    try:
                        remove_account_env_from_system(account)
                    except Exception as e:
                        logger.error(f"移除未授权账号系统残留失败: {account} - {str(e)}")
                    continue
                else:
                    try:
                        expiration_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                        expiration_str = accountVip
                    except Exception:
                        valid_accounts.append(account)
                        try:
                            remove_account_env_from_system(account)
                        except Exception as e:
                            logger.error(f"移除异常授权账号系统残留失败: {account} - {str(e)}")
                        logger.warning(f"账号授权日期格式异常，暂仅保留本地: {account} - {accountVip}")
                        continue

                days_diff = (expiration_date - today_date).days

                # === 逻辑分支 1: 正常期内 ===
                if days_diff > reminder_days_cfg:
                    valid_accounts.append(account)
                    continue
                
                # === 逻辑分支 2: 提醒期 (例如剩余 0, 1, 2 天) ===
                if 0 <= days_diff <= reminder_days_cfg:
                    valid_accounts.append(account) # 账号还没过期，保留
                    
                    # 检查今天是否已经提醒过，避免定时任务频繁跑的时候重复发消息
                    remind_key = f"{user}_{account}_{today_date}"
                    has_reminded = middleware.bucketGet('dd_sk_remind_log', remind_key)
                    
                    if not has_reminded:
                        msg = f"""
=====⏰ 到期提醒=====
您的速看授权即将到期！
🔑 ID: {account}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
过期后账号将自动清理。
发送 {config['randommanagecommand']} 进行续费
=================="""
                        send_user_notice(user, msg)
                        middleware.bucketSet('dd_sk_remind_log', remind_key, "1")
                        reminded_count += 1
                        logger.info(f"发送提醒: {user} - {account} - 剩余 {days_diff} 天")
                    continue

                # === 逻辑分支 3: 已过期 (days_diff < 0) ===
                if days_diff < 0:
                    # 执行清理逻辑
                    try:
                        remove_account_env_from_system(account)
                        logger.info(f"系统数据已删除: {account}")
                    except Exception as e:
                        logger.error(f"删除系统变量失败: {str(e)}")
                    
                    middleware.bucketDel(bucket='dd_sk_token', key=account)
                    middleware.bucketDel(bucket='dd_sk_auth', key=account)
                    if config['enable_remark']:
                        RemarkManager.delete_account_remark(user, account)
                    
                    # 发送清理通知
                    clean_msg = f"""
=====🗑️ 过期清理通知=====
您的账号授权已过期并清理。
🔑 ID: {account}
📅 到期: {expiration_str}
------------------
相关配置已从系统中移除。
如需继续使用，请重新登录并授权。
=================="""
                    send_user_notice(user, clean_msg)
                    cleaned_count += 1
                    user_has_change = True
                    logger.info(f"账号已清理通知: {user} - {account}")

            # 如果用户账号列表有变动（有被清理的），更新用户的账号列表
            if user_has_change:
                if valid_accounts:
                    middleware.bucketSet(bucket='dd_sk_user', key=user, value=str(valid_accounts))
                else:
                    middleware.bucketDel(bucket='dd_sk_user', key=user)

        except Exception as e:
            logger.error(f"维护任务处理用户 {user} 失败: {str(e)}")
            continue

    # 本地账号清理后，再兜底扫描一次青龙残留
    cleaned_count += clean_expired_envs_from_qinglong(today_date)

    if sender.isAdmin() and manual_run:
        sender.reply(f"""
=====维护完成=====
✅ 已清理过期: {cleaned_count}个
🗑️ 清理未授权/缺配置: {invalid_cleaned_count}个
📢 发送提醒: {reminded_count}个
==================""")


def admin_broadcast():
    """管理员公告广播"""
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return

    sender.reply("""
=====全员广播=====
请输入要发送的公告内容
------------------
消息将发送给所有绑定用户
------------------
回复"q"退出
==================""")

    content = get_user_input(timeout=120)
    if content is None or content.lower() == 'q':
        sender.reply("✅ 已取消广播")
        return

    sender.reply(f"""
=====确认发送=====
⚠️ 即将向所有用户发送消息
------------------
内容预览:
{content[:50]}...
------------------
确认请回复【确认发送】
取消请回复其他内容
==================""")

    confirm = get_user_input(timeout=60)
    if confirm != "确认发送":
        sender.reply("✅ 已取消发送")
        return

    all_users = AccountManager.get_all_users()
    if not all_users:
        sender.reply("📭 暂无用户")
        return

    sender.reply(f"⏳ 开始广播，目标用户数: {len(all_users)}")
    success = 0
    fail = 0

    for user in all_users:
        try:
            user_sender = middleware.Sender(user)
            send_user_notice(user, f"【速看公告】\n{content}")
            success += 1
            # 简单的防风控延时
            time.sleep(1)
        except Exception as e:
            logger.error(f"广播失败 {user}: {e}")
            fail += 1

    sender.reply(f"""
=====广播完成=====
✅ 成功发送: {success}人
❌ 发送失败: {fail}人
==================""")


def show_tutorial():
    """显示速看插件使用教程"""
    tutorial = f"""
=====速看插件教程=====
🔰 基础功能指令:
------------------
1️⃣ {config['randomsigncommand']}
• 绑定速看账号
• 支持抓包 URL/JSON 整段提交
• {'支持设置账号备注' if config['enable_remark'] else '不支持备注功能'}

2️⃣ {config['randomquerycommand']}
• 查看账号状态
• {'显示账号备注' if config['enable_remark'] else ''}

3️⃣ {config['randommanagecommand']}
• 管理已绑定账号
• 授权账号/删除账号{'/修改备注' if config['enable_remark'] else ''}
• 批量授权/批量删除
• 支持多种支付方式

🔧 管理员功能:
------------------
• 速看授权: 管理员授权功能（一键授权/指定用户）【按天计算】
• 速看清理: 执行过期维护（提醒 + 清理）
• 速看广播: 向所有用户发送公告消息

🔄 自动化维护:
------------------
• 系统会每天自动检查账号状态
• 到期前{config['reminder_days']}天开始发送续费提醒
• 过期后自动清理系统数据并通知用户

⚠️ 注意事项:
------------------
1. 绑定账号未授权时，不会同步到系统
2. 授权成功后自动同步变量(S_SUKAN)
3. 批量删除操作不可恢复
=================="""
    sender.reply(tutorial)


# ===================== 主逻辑 =====================
try:
    logger.info(f"速看插件启动 - 用户: {userid}, 消息: {usermessage}")
    
    # 输出配置状态
    logger.info(f"积分桶配置: {config['points_bucket']}")
    if config['enable_proxy']:
        logger.info(f"代理功能已启用，代理池地址: {config['proxy_pool_url']}")
    else:
        logger.info("代理功能未启用")
    
    if config['enable_remark']:
        logger.info("备注功能已启用")
    else:
        logger.info("备注功能未启用")
    
    # 处理指令
    if '登录' in usermessage or '登陆' in usermessage:
        bindaccount()
    elif '管理' in usermessage:
        xy_manage()
    elif '查询' in usermessage:
        cxs()
    elif usermessage in ['速看清理', '清理速看']:
        clean_expired_accounts(force_report=True, clean_invalid=True)
    elif usermessage == '速看授权':
        admin_auth_options()
    elif usermessage == '速看广播':
        admin_broadcast()
    elif usermessage == '速看教程':
        show_tutorial()
    elif sender.getImtype() == 'fake':
        # 定时任务触发
        logger.info("定时任务执行 - 开始维护过期账号")
        clean_expired_accounts()
        
except Exception as e:
    logger.error(f"主逻辑执行失败: " + str(e))
    sender.reply(f"""
=====系统错误=====
❌ 插件执行失败
------------------
错误信息: {str(e)}
请稍后重试或联系管理员
==================""")

logger.info(f"速看插件执行完成 - 用户: {userid}")
