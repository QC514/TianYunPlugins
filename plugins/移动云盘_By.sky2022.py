# [rule: ^移动云盘(登录|登陆)$|^(登录|登陆)移动云盘$|^移动云盘(管理|查询|教程|后台|同步|兑换|一键抢兑|停止抢兑)$]
# [disable:true]
# [cron: 32 9 * * *]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [public: true]
# [title: 移动云盘]
# [icon: https://img-2.sfcdn.org/2e2c0004b4d77a8f04d627a3a865866aa2f94bc4.png]
# [class: 羊毛类]
# [version: 1.1.1]
# [price: 15.88]
# [admin: false]
# [author: sky2022]
# [service: ]
# [description: 介绍：移动云盘账号管理插件，支持短信验证码登录/手动Token登录、授权管理、云朵兑换、一键抢兑、变量同步到青龙/呆呆面板<br>登录方式：发送"移动云盘登录"可选短信验证码登录或手动Token登录<br>提交格式：Authorization值#手机号<br>指令：移动云盘登录、移动云盘管理、移动云盘查询、移动云盘兑换、移动云盘一键抢兑、移动云盘停止抢兑、移动云盘教程、移动云盘后台<br>定时任务：❶插件自带定时每天9点检测授权过期并推送通知 ❷一键抢兑需管理员自行添加计划任务，指令填『移动云盘一键抢兑』定时填『57 9,11,15,19,23 * * *』勾选自处理<br>V1.1.0: 新增云朵兑换、一键抢兑、停止抢兑功能，支持自定义并发<br>V1.0.3: 简化提交格式，去除deviceId<br>V1.0.1: 新增短信验证码登录，自动获取设备指纹，优化数据存储格式<br>V1.0.0: 初始版本发布，支持青龙/呆呆面板对接]

# [param: {"required":true,"key":"dd_ydyp.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_ydyp.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":true,"key":"dd_ydyp.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":false,"key":"dd_ydyp.use_ma_pay","bool":true,"placeholder":"false","name":"启用码支付","desc":"开启后默认使用码支付+积分支付，并隐藏微信支付"}]
# [param: {"required":false,"key":"dd_ydyp.panel_group","bool":false,"placeholder":"例:移动云盘","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_ydyp.ydyp_osname","bool":false,"placeholder":"必填项,例:ydyp","name":"面板变量名","desc":"提交到面板中的移动云盘变量名，默认为ydyp"}]
# [param: {"required":true,"key":"dd_ydyp.ydypVipmoney","bool":false,"placeholder":"例:0.88,不填为0元(免费)","name":"上车价格","desc":"上车价格(单位:元)/月，填0则免费"}]
# [param: {"required":true,"key":"dd_ydyp.ydypcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数），不填或填0关闭积分支付"}]
# [param: {"required":false,"key":"dd_ydyp.bingfa","bool":false,"placeholder":"","name":"抢兑并发","desc":"一键抢兑时的并发数，不填默认20"}]

import re
import json
import time
import uuid
import base64
import hashlib
import random
import string
import socket
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from decimal import Decimal
import middleware

try:
    from Crypto.Cipher import AES as _AES, PKCS1_v1_5 as _PKCS1
    from Crypto.PublicKey import RSA as _RSA
    from Crypto.Util.Padding import pad as _pad, unpad as _unpad
    _HAS_CRYPTO = True
except ImportError:
    _HAS_CRYPTO = False


CHINA_TZ = timezone(timedelta(hours=8))
_time_offset = None
_offset_expiry = 0

def get_ntp_time():
    global _time_offset, _offset_expiry
    now = time.time()
    if _time_offset is None or now > _offset_expiry:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(2)
                s.sendto(b'\x1b' + 47 * b'\0', ('ntp.aliyun.com', 123))
                data, _ = s.recvfrom(1024)
                if data:
                    t = data[40:48]
                    secs = int.from_bytes(t[:4], 'big') - 2208988800
                    frac = int.from_bytes(t[4:], 'big')
                    ntp_time = secs + frac / 2**32
                    _time_offset = ntp_time - time.time()
                    _offset_expiry = time.time() + 600
        except (socket.timeout, OSError):
            if _time_offset is None:
                _time_offset = 0
            _offset_expiry = time.time() + 60
    return datetime.fromtimestamp(time.time() + _time_offset)

def get_china_time():
    return get_ntp_time().astimezone(CHINA_TZ)

def local_now():
    return get_china_time()


STOP_EXCHANGE = False


def fetch_device_id():
    url = "https://slw.h5cmpassport.com:9090/deviceprofile/v4"
    headers = {
        "Content-Type": "application/json;charset=utf-8",
        "Origin": "https://m.mcloud.139.com",
        "Referer": "https://m.mcloud.139.com/",
    }
    payload = {
        "appId": "default",
        "organization": "FXlyfmWg2AzwbrxDKSv5",
        "ep": "WydTnuOv+Rtg/Qj8Q4vnhSXJN4UHQPF2jjs+LVJkD3u8HXglndPAndOgrlmg2Q8q0FUQRZpN0N7e61ebhjw/Gba22ydgOMbBRfbSmKSnNWaACA+MzAX5Q4dd980zPqelMxGVzB3jkr1wGE6cVQkwWFq/xbdnkK/Sh6xrPDjYvho=",
        "data": "5b5f2054405d6155102ed35a134758f768e60b7c1ac7af66acb16871d78a099cbcbabb3fb5ebeefe6cbae063407fca585a343ce5bef4f4e4588df42ca8ae8a6504b3646066fd7dc46465a83d510fbb477ba72f7375db7cbcba9b712ec88d85fc8d410536b96ca644c8ca3afbca00e0084ad9709b93b86923bf1fadef48be3e888b52dd2775c180b5b8e7bae139fadf2944f73010be9704daa6f4cf596b4adccff7b5de84e45698b781d963b69fa8ec28e43083512ab5749ea05c4efce14945d647c9f33d6296750ff2ba59bff5b7fcf698ffa146b7fe7e5c405b13100818b53fd034d05edea63c8365d9113bc7d4c0652892fcae75cdb491ae0215fbd822b1877b209fc8c68710badc6915080b7b994fa4b86a8f7b37e929cecbd1c590ad7382beb3ae8b9cc56ed84e927cbe41d8b4b15bbeecc69f5463d402cc2732fe5b76ec201632afbc16228531a65c1810482e4eb48157bc8b23cd363c6809a3fd629e3520514c06a720616e1788fe10203f9ebfa1de24c66213e334e3a3b3ff8a8866b7aefd9b4f2c88d216f45b551d693433940569092f0c7aca25019dc2003e8eab1967ac1dc32b0912701b0abc17e0509bada0cf0fcbe3c5fb64f0d5c6f02303b1540829a301673da89f7460d00190bda07c9b82c263277066f8e7e91c4916f247f9d9fe295a46d16cd087cee865d9e50edeb8e88842c560b09f853b5f89d2d0c4ed160f5bc293f7c69ece9e2d64d7217857fd2d64d57bea1ccea1b52896bb9aaf2ec3baa2421bce8d011813a1b26f0acb3a3cf594298bd725f8da17717b965f85e46a52c758ed1e95218e06f7e96a9f13e4855a0bb4bcf8b5f571887ec58c7438e99f06562414bcb274038fe6ffc1b8991021e35866cef5010184e3fbbd49c19d6020315731e9e57b7cd6a1e8b33c97746a782f9b4a26696966f40324f1ff76d3d1d24bf544230438dc32ab26d6dc107adf9feac34ffbbaa8814cec674e9469de54a714273a47f4fd06561e611f6741a4f0362a3b8821b0c69a3a04ced876fbf1b5fdc58097b1d7087aa2c0df556f8a06288db8c306cda4525d91c0452a0d2747982bd70b31c6905d4e483e8519d4d605af776be2a81224e3a6cc0b6ec49ad2cdb434bd85b5079ff86f68bf5ebb41336f30ec84fe19fabbd10a4422a274a3749d70c6b39cf7cdc1eb0cb228abee2475d16c57635a332628727b76a1fac0b26bf7bbdf4c5b956261919e7d2bd67733656855503670d48fe3680d04b65aac48d99bd47aedb6091c0a6df53be5bd662c1130feb6b469578cb146e1ae004471641fbc028cc06b80cfcdc50f8231e58b4126ab750b1d02eb8ac417b53a5ae50846db9aeadf4f1c98e33228db5143cb3d928217b769eaf32d181320a0bee4805334c28a03995d925b52fda358d19c52e3838c243b8c7d3256337943705c1311526c290fad975b7d7ade4bbc9292dbd7b9c0314715ef3c785a720e674dc23538af333cc6ff541aea70086287a8b4407c66ce673c9a47268de014c876a3a6a577d501285f6f489e2519f51bf4feafe307333a9e077f613527bbe1ce632127df654588410f713bb4a61e050cae618e98cc9adbb77d9df95733449c06e62094f3cdaf2ba39f94223ed7ca63ea4dec37d7283bdd0d2015511e7e57212073a540b308b10d7f85de73865fc2ffbf05a85ae25a7b52f0292236ee75f738add8144c7b2767a2100451363a47c12dfb674bd3ee000fa41565e9fbc60440a629160a2d2a99ec23dccc6815f644a2dd1eb059ab8593d9b04b1b81f5e427570cfc06eba8456b68159e6886843bcf4374b02de2e5be8d900882f78a71c2f3819d2e9c45e64b5d006c7a5914d1482f01ed5c0cfb44c3543656e96b5d91b39cd667af4dc60f44752da28eda57d2453d26a099529a2a38c9b9b2f0a73a69445030321b0a87287f6469f4d585739cded2e79c66df9c949eb7b2b8a8ff78e80a88ca494f3410195e021ec5009f8cd29781f09d58e6f866102072f1cee202c6ce21d72795b47a0ab8464fa54836c36a28ff73828e7a39dd1203d5a051ac4cd22b4f8c9f1e4e9c42f0c85b101b1eb495c0a767697dccab920489fae867ff38c5f917aec269d0ac9a1d6005407db762349d77e990581e19b1912fc975a9cdd2",
        "os": "web",
        "encode": 5,
        "compress": 2,
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        result = resp.json()
        raw_id = result.get("detail", {}).get("deviceId", "")
        if raw_id:
            return True, "B" + raw_id
        return False, f"获取deviceId失败: {result}"
    except Exception as e:
        return False, f"获取deviceId异常: {str(e)}"


def get_or_fetch_device_id(account):
    return fetch_device_id()


class PluginFlowExit(BaseException):
    pass


def exit(code=0):
    raise PluginFlowExit(code)


def normalize_bucket_keys(keys_data):
    if not keys_data:
        return []
    if isinstance(keys_data, (list, tuple, set)):
        return [str(item).strip() for item in keys_data if str(item).strip()]
    if isinstance(keys_data, str):
        return [item.strip() for item in keys_data.split(",") if item.strip()]
    return [str(keys_data).strip()] if str(keys_data).strip() else []


UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22H71 MCloud/12.5.4'
MARKET_UA = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/22H71 MCloud/12.5.4 MCloudApp/12.5.4'
MARKET_ANDROID_UA = 'Mozilla/5.0 (Linux; Android 16; RMX5060 Build/BP2A.250605.015; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/149.0.7827.13 Mobile Safari/537.36 MCloudApp/12.5.4 AppLanguage/zh-CN'
MARKET_BASE_URL = 'https://m.mcloud.139.com'
MARKET_SOURCE_ID = '1097'
SLIDE_CAPTCHA_OCR_API = "http://ddddocr.250666.xyz/capcode"


def normalize_authorization(token):
    token = (token or '').strip()
    if token and not token.startswith('Basic '):
        return f'Basic {token}'
    return token


def generate_device_id():
    device_info = {
        'deviceId': uuid.uuid4().hex.upper(),
        'brand': 'Apple',
        'model': 'iPhone 16 Pro',
        'system': 'iOS 18.7',
        'timestamp': int(time.time() * 1000)
    }
    raw = json.dumps(device_info, ensure_ascii=False, separators=(',', ':'))
    return base64.b64encode(raw.encode('utf-8')).decode('utf-8')


def build_x_device_info(device_id):
    return f"wifi||8|12.5.4|Apple|iPhone 16 Pro|{device_id}||ios 18.7|||||"


# ============================================================
# 短信验证码登录
# ============================================================
_PUZZLE_AES_KEY = "CREATPUZZLE03F9A"
_ALPHANUMERIC = string.ascii_letters + string.digits
_BASE_URL_139 = "https://yun.139.com"
_USER_API_139 = "https://user-njs.yun.139.com/user"
_AAS_URL_139 = "https://aas.caiyun.feixin.10086.cn/tellin"

_APP_DEVICE_INFO_139 = "1|127.0.0.1|1|11.2.0|OnePlus|PJE110|AE6D70DEF09FD984865CBEF2D7F2F126|02-00-00-00-00-00|android 16|1264X2584|zh||||034|"
_APP_HEADERS_139 = {
    "User-Agent": "okhttp/4.12.0",
    "Accept-Encoding": "gzip",
    "x-NationCode": "+86",
    "x-NetType": "1",
    "x-DeviceInfo": _APP_DEVICE_INFO_139,
    "x-yun-client-info": _APP_DEVICE_INFO_139,
    "x-yun-app-channel": "10000023",
    "x-huawei-channelSrc": "10000023",
    "x-MM-Source": "034",
    "Accept-Language": "zh-CN",
    "x-SvcType": "1",
    "Content-Type": "application/xml; charset=UTF-8",
}

_COMMON_HEADERS_139 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://yun.139.com",
    "Referer": "https://yun.139.com/w/",
    "x-huawei-channelsrc": "10000034",
    "x-yun-app-channel": "10000034",
    "x-yun-channel-source": "10000034",
    "mcloud-channel": "1000101",
    "mcloud-client": "10701",
    "mcloud-version": "7.17.4",
    "mcloud-route": "001",
    "caller": "web",
    "x-m4c-caller": "PC",
    "x-m4c-src": "10002",
    "x-svctype": "1",
    "x-yun-svc-type": "1",
    "inner-hcy-router-https": "1",
    "x-inner-ntwk": "2",
    "x-yun-api-version": "v1",
    "cms-device": "default",
}

_DEVICE_PROFILE_URL = "https://slw.h5cmpassport.com:9090/deviceprofile/v4"
_DEVICE_PROFILE_PAYLOAD = {
    "appId": "default",
    "organization": "FXlyfmWg2AzwbrxDKSv5",
    "ep": "WydTnuOv+Rtg/Qj8Q4vnhSXJN4UHQPF2jjs+LVJkD3u8HXglndPAndOgrlmg2Q8q0FUQRZpN0N7e61ebhjw/Gba22ydgOMbBRfbSmKSnNWaACA+MzAX5Q4dd980zPqelMxGVzB3jkr1wGE6cVQkwWFq/xbdnkK/Sh6xrPDjYvho=",
    "data": "5b5f2054405d6155102ed35a134758f768e60b7c1ac7af66acb16871d78a099cbcbabb3fb5ebeefe6cbae063407fca585a343ce5bef4f4e4588df42ca8ae8a6504b3646066fd7dc46465a83d510fbb477ba72f7375db7cbcba9b712ec88d85fc8d410536b96ca644c8ca3afbca00e0084ad9709b93b86923bf1fadef48be3e888b52dd2775c180b5b8e7bae139fadf2944f73010be9704daa6f4cf596b4adccff7b5de84e45698b781d963b69fa8ec28e43083512ab5749ea05c4efce14945d647c9f33d6296750ff2ba59bff5b7fcf698ffa146b7fe7e5c405b13100818b53fd034d05edea63c8365d9113bc7d4c0652892fcae75cdb491ae0215fbd822b1877b209fc8c68710badc6915080b7b994fa4b86a8f7b37e929cecbd1c590ad7382beb3ae8b9cc56ed84e927cbe41d8b4b15bbeecc69f5463d402cc2732fe5b76ec201632afbc16228531a65c1810482e4eb48157bc8b23cd363c6809a3fd629e3520514c06a720616e1788fe10203f9ebfa1de24c66213e334e3a3b3ff8a8866b7aefd9b4f2c88d216f45b551d693433940569092f0c7aca25019dc2003e8eab1967ac1dc32b0912701b0abc17e0509bada0cf0fcbe3c5fb64f0d5c6f02303b1540829a301673da89f7460d00190bda07c9b82c263277066f8e7e91c4916f247f9d9fe295a46d16cd087cee865d9e50edeb8e88842c560b09f853b5f89d2d0c4ed160f5bc293f7c69ece9e2d64d7217857fd2d64d57bea1ccea1b52896bb9aaf2ec3baa2421bce8d011813a1b26f0acb3a3cf594298bd725f8da17717b965f85e46a52c758ed1e95218e06f7e96a9f13e4855a0bb4bcf8b5f571887ec58c7438e99f06562414bcb274038fe6ffc1b8991021e35866cef5010184e3fbbd49c19d6020315731e9e57b7cd6a1e8b33c97746a782f9b4a26696966f40324f1ff76d3d1d24bf544230438dc32ab26d6dc107adf9feac34ffbbaa8814cec674e9469de54a714273a47f4fd06561e611f6741a4f0362a3b8821b0c69a3a04ced876fbf1b5fdc58097b1d7087aa2c0df556f8a06288db8c306cda4525d91c0452a0d2747982bd70b31c6905d4e483e8519d4d605af776be2a81224e3a6cc0b6ec49ad2cdb434bd85b5079ff86f68bf5ebb41336f30ec84fe19fabbd10a4422a274a3749d70c6b39cf7cdc1eb0cb228abee2475d16c57635a332628727b76a1fac0b26bf7bbdf4c5b956261919e7d2bd67733656855503670d48fe3680d04b65aac48d99bd47aedb6091c0a6df53be5bd662c1130feb6b469578cb146e1ae004471641fbc028cc06b80cfcdc50f8231e58b4126ab750b1d02eb8ac417b53a5ae50846db9aeadf4f1c98e33228db5143cb3d928217b769eaf32d181320a0bee4805334c28a03995d925b52fda358d19c52e3838c243b8c7d3256337943705c1311526c290fad975b7d7ade4bbc9292dbd7b9c0314715ef3c785a720e674dc23538af333cc6ff541aea70086287a8b4407c66ce673c9a47268de014c876a3a6a577d501285f6f489e2519f51bf4feafe307333a9e077f613527bbe1ce632127df654588410f713bb4a61e050cae618e98cc9adbb77d9df95733449c06e62094f3cdaf2ba39f94223ed7ca63ea4dec37d7283bdd0d2015511e7e57212073a540b308b10d7f85de73865fc2ffbf05a85ae25a7b52f0292236ee75f738add8144c7b2767a2100451363a47c12dfb674bd3ee000fa41565e9fbc60440a629160a2d2a99ec23dccc6815f644a2dd1eb059ab8593d9b04b1b81f5e427570cfc06eba8456b68159e6886843bcf4374b02de2e5be8d900882f78a71c2f3819d2e9c45e64b5d006c7a5914d1482f01ed5c0cfb44c3543656e96b5d91b39cd667af4dc60f44752da28eda57d2453d26a099529a2a38c9b9b2f0a73a69445030321b0a87287f6469f4d585739cded2e79c66df9c949eb7b2b8a8ff78e80a88ca494f3410195e021ec5009f8cd29781f09d58e6f866102072f1cee202c6ce21d72795b47a0ab8464fa54836c36a28ff73828e7a39dd1203d5a051ac4cd22b4f8c9f1e4e9c42f0c85b101b1eb495c0a767697dccab920489fae867ff38c5f917aec269d0ac9a1d6005407db762349d77e990581e19b1912fc975a9cdd2",
    "os": "web",
    "encode": 5,
    "compress": 2,
}


def _rand_str(length=16):
    return "".join(random.choices(_ALPHANUMERIC, k=length))


def _puzzle_encrypt(plaintext, key=_PUZZLE_AES_KEY):
    iv_str = _rand_str(16)
    k = key.encode("utf-8")
    iv = iv_str.encode("utf-8")
    cipher = _AES.new(k, _AES.MODE_CBC, iv)
    ct = cipher.encrypt(_pad(plaintext.encode("utf-8"), 16))
    return base64.b64encode(iv + ct).decode()


def _puzzle_decrypt(ciphertext_b64, key=_PUZZLE_AES_KEY):
    raw = base64.b64decode(ciphertext_b64)
    k = key.encode("utf-8")
    cipher = _AES.new(k, _AES.MODE_CBC, raw[:16])
    return _unpad(cipher.decrypt(raw[16:]), 16).decode("utf-8")


def _aes_ecb_encrypt(plaintext, key):
    k = _AES.new(key.encode("utf-8"), _AES.MODE_ECB)
    ct = k.encrypt(_pad(plaintext.encode("utf-8"), 16))
    return base64.b64encode(ct).decode()


def _aes_ecb_decrypt(ciphertext_b64, key):
    k = _AES.new(key.encode("utf-8"), _AES.MODE_ECB)
    return _unpad(k.decrypt(base64.b64decode(ciphertext_b64)), 16).decode("utf-8")


def _rsa_encrypt(plaintext, public_key_b64):
    pub_key_der = base64.b64decode(public_key_b64)
    pub_key = _RSA.import_key(
        b"-----BEGIN PUBLIC KEY-----\n"
        + base64.b64encode(pub_key_der)
        + b"\n-----END PUBLIC KEY-----"
    )
    cipher = _PKCS1.new(pub_key)
    return base64.b64encode(cipher.encrypt(plaintext.encode("utf-8"))).decode()


def _make_sign(data, timestamp, rand_str):
    body_sorted = ""
    if data:
        body_json = json.dumps(data, separators=(",", ":"))
        encoded = urllib.parse.quote(body_json, safe="")
        body_sorted = "".join(sorted(encoded))
    r = hashlib.md5(base64.b64encode(body_sorted.encode()).decode().encode()).hexdigest()
    l = hashlib.md5(f"{timestamp}:{rand_str}".encode()).hexdigest()
    return hashlib.md5((r + l).encode()).hexdigest().upper()


def _fetch_device_id():
    resp = requests.post(
        _DEVICE_PROFILE_URL,
        json=_DEVICE_PROFILE_PAYLOAD,
        headers={
            "Content-Type": "application/json;charset=utf-8",
            "Origin": "https://m.mcloud.139.com",
            "Referer": "https://m.mcloud.139.com/",
        },
        timeout=15,
    )
    data = resp.json()
    raw_id = data.get("detail", {}).get("deviceId", "")
    if not raw_id:
        raise RuntimeError(f"获取设备指纹失败: {data}")
    return "B" + raw_id


def _sms_login_flow(phone, get_sms_code_cb):
    session = requests.Session()
    session.headers.update(_COMMON_HEADERS_139)
    visitor_id = _rand_str(32).lower()

    def _signed_post(url, payload, extra_headers=None):
        now = datetime.now(timezone(timedelta(hours=8)))
        ts = now.strftime("%Y-%m-%d %H:%M:%S")
        rand = _rand_str(16)
        sign = _make_sign(payload, ts, rand)
        headers = {
            "mcloud-sign": f"{ts},{rand},{sign}",
            "x-yun-client-info": f"||9|7.17.4|chrome|148.0.0.0|{visitor_id}||windows 10||zh-CN||||dW5kZWZpbmVk||",
            "x-deviceinfo": f"||9|7.17.4|chrome|148.0.0.0|{visitor_id}||windows 10||zh-CN|||",
        }
        if extra_headers:
            headers.update(extra_headers)
        return session.post(url, json=payload, headers=headers, timeout=15)

    def _app_post_xml(url, xml_body):
        headers = dict(_APP_HEADERS_139)
        headers["x-yun-uni"] = _rand_str(12)
        headers["x-ExpRoute-Code"] = f"routeCode={phone},type=10"
        resp = requests.post(url, data=xml_body.encode("utf-8"), headers=headers, timeout=15)
        return ET.fromstring(resp.text)

    xml_body = f"<root>\n   <account>{phone}</account>\n   <type>2</type>\n</root>"
    root = _app_post_xml(f"{_AAS_URL_139}/verfycode.do", xml_body)
    ret = root.findtext("return", "")
    if ret != "0":
        return {"success": False, "message": f"获取验证码失败: {root.findtext('desc', '')}"}
    sp = root.find("slidePuzzle")

    try:
        correct_x = _puzzle_decrypt(sp.findtext("puzzleLeft", ""))
    except Exception as e:
        return {"success": False, "message": f"验证码解析失败: {e}"}
    verfycode = _puzzle_encrypt(correct_x)

    rand = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=6))
    xml_body = (
        f"<root>\n"
        f"   <account><![CDATA[{phone}]]></account>\n"
        f"   <clientType>414</clientType>\n"
        f"   <mode>0</mode>\n"
        f"   <puzzleVerfycode>{verfycode}</puzzleVerfycode>\n"
        f"   <random><![CDATA[{rand}]]></random>\n"
        f"   <reqType>3</reqType>\n"
        f"</root>"
    )
    root = _app_post_xml(f"{_AAS_URL_139}/getDyncPasswd.do", xml_body)
    ret = root.findtext("return", "")
    if ret != "0":
        return {"success": False, "message": f"发送短信失败: {root.findtext('desc', '')}"}

    sms_code = get_sms_code_cb()
    if not sms_code:
        return {"success": False, "message": "未输入验证码"}

    aes_key = _rand_str(16)
    resp = _signed_post(f"{_BASE_URL_139}/orchestration/auth-rebuild/key/v1.0/getRsaPublicKey",
                        {"clientCode": "10701", "type": 1})
    rsa_data = resp.json()
    if not rsa_data.get("success"):
        return {"success": False, "message": f"获取RSA公钥失败: {rsa_data.get('message', '')}"}
    encrypted_aes_key = _rsa_encrypt(aes_key, rsa_data["data"]["publicKey"])

    login_inner = json.dumps({
        "dycPwd": sms_code, "loginStyle": "passSMS", "ifOpenAccount": "1",
        "clientEnv": "3", "setCookie": 0, "account": phone,
    }, separators=(",", ":"))
    login_payload = {
        "encryptMsg": _aes_ecb_encrypt(login_inner, aes_key),
        "clientId": "10701", "autoLogin": True, "returnToken": True,
    }
    resp = _signed_post(
        f"{_BASE_URL_139}/orchestration/auth-rebuild/permission/v1.0/login",
        login_payload,
        {"mcloud-cool-skey": encrypted_aes_key, "mcloud-skey": encrypted_aes_key},
    )
    login_result = resp.json()
    if not login_result.get("success") or not login_result.get("data"):
        return {"success": False, "message": f"登录失败: {login_result.get('message', '未知错误')}"}

    encrypted_resp = login_result["data"]
    if isinstance(encrypted_resp, str):
        try:
            login_result["data"] = json.loads(_aes_ecb_decrypt(encrypted_resp, aes_key))
        except Exception as e:
            return {"success": False, "message": f"解密响应失败: {e}"}

    auth_token = login_result["data"].get("authToken", "")
    if not auth_token:
        return {"success": False, "message": "登录成功但未获取到authToken"}

    return {"success": True, "phone": phone, "auth_token": auth_token}


def _extract_auth_token(authorization):
    auth = authorization.strip()
    if auth.startswith('Basic '):
        auth = auth[6:].strip()
    try:
        decoded = base64.b64decode(auth).decode('utf-8')
        if decoded.startswith('mobile:'):
            parts = decoded.split(':', 2)
            if len(parts) == 3:
                return parts[2]
    except Exception:
        pass
    return None


def build_panel_value(token_raw, phone):
    try:
        data = json.loads(token_raw)
        if isinstance(data, dict):
            p = data.get('phone', phone)
            auth_token = data.get('auth_token', '')
            if auth_token:
                auth_b64 = base64.b64encode(f"mobile:{p}:{auth_token}".encode()).decode()
                return f"Basic {auth_b64}#{p}"
    except (json.JSONDecodeError, ValueError, TypeError):
        pass
    return token_raw


_REFRESH_AES_KEY = 'c7lXOigXahPnTViq'


def _refresh_ydyp_token(phone, current_auth_token):
    if not _HAS_CRYPTO:
        return None
    authorization = f"Basic {base64.b64encode(f'mobile:{phone}:{current_auth_token}'.encode()).decode()}"
    encrypted_data = _aes_ecb_encrypt(
        json.dumps({"phoneNumber": phone}, separators=(",", ":")),
        _REFRESH_AES_KEY
    )
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_7 like Mac OS X) AppleWebKit/605.1.15 '
                      '(KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002f2c) NetType/WIFI '
                      'Language/zh_CN miniProgram/wx4e4ed37286c816c2',
        'x-yun-tid': str(uuid.uuid4()),
        'Authorization': authorization,
        'x-yun-api-version': 'v1',
        'x-yun-module-type': '100',
        'x-yun-op-type': '1',
        'x-yun-app-channel': '10214200',
        'x-yun-client-info': '||8||||||||||||',
        'hcy-cool-flag': '1',
    }
    try:
        resp = requests.post(
            'https://user-njs.yun.139.com/user/auth/refreshToken',
            json={'data': encrypted_data},
            headers=headers,
            timeout=15
        )
        data = resp.json()
        code = str(data.get('code', ''))
        is_ok = code in ('0', '00', '000', '0000') or data.get('success', False)
        if is_ok and isinstance(data.get('data'), dict):
            new_token = data['data'].get('token', '')
            if new_token:
                return new_token
    except Exception:
        pass
    return None


def _try_refresh_account(phone):
    if not _HAS_CRYPTO:
        return False, '当前环境不支持续期'
    token_raw = middleware.bucketGet('dd_ydyp_token', phone)
    if not token_raw:
        return False, '无Token数据'

    auth_token = None
    try:
        data = json.loads(token_raw)
        if isinstance(data, dict):
            auth_token = data.get('auth_token', '')
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    if not auth_token:
        auth_value = parse_token_value(token_raw, phone)
        auth_token = _extract_auth_token(auth_value)

    if not auth_token:
        return False, '无法提取auth_token'

    new_token = _refresh_ydyp_token(phone, auth_token)
    if not new_token:
        return False, 'Token续期失败，可能已失效'

    store_data = json.dumps({
        "phone": phone,
        "auth_token": new_token,
    }, ensure_ascii=False)
    middleware.bucketSet('dd_ydyp_token', phone, store_data)
    return True, '续期成功'


class YdypAPI:
    """移动云盘API查询"""

    def __init__(self, authorization, account, device_id=''):
        self.authorization = normalize_authorization(authorization)
        self.account = account
        self.session = requests.Session()
        self.jwt_token = None
        self.sso_token = None
        self.device_id = device_id if device_id else generate_device_id()
        self.x_device_info = build_x_device_info(self.device_id)
        self.market_headers = {}
        self.market_cookies = {}

    def _build_market_page_url(self):
        return f'{MARKET_BASE_URL}/portal/mobilecloud/index.html?path=newsignin&sourceid={MARKET_SOURCE_ID}&enableShare=1&token={self.sso_token or ""}&targetSourceId=001005'

    def _build_market_headers(self):
        headers = dict(self.market_headers)
        headers['Referer'] = self._build_market_page_url()
        headers['deviceId'] = self.device_id
        headers['x-DeviceInfo'] = self.x_device_info
        return headers

    def get_sso_token(self):
        sso_url = 'https://orches.yun.139.com/orchestration/auth-rebuild/token/v1.0/querySpecToken'
        headers = {
            'Authorization': self.authorization,
            'User-Agent': UA,
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'orches.yun.139.com'
        }
        payload = {"account": self.account, "toSourceId": "001005"}
        try:
            resp = self.session.post(sso_url, headers=headers, json=payload, timeout=15)
            data = resp.json()
            if data.get('success'):
                self.sso_token = data['data']['token']
                return self.sso_token
        except Exception:
            pass
        return None

    def get_jwt_token(self):
        token = self.get_sso_token()
        if not token:
            return False
        jwt_url = f"https://caiyun.feixin.10086.cn:7071/portal/auth/tyrzLogin.action?ssoToken={token}"
        headers = {
            'User-Agent': UA,
            'Accept': '*/*',
            'Host': 'caiyun.feixin.10086.cn:7071',
        }
        try:
            resp = self.session.post(jwt_url, headers=headers, timeout=15)
            data = resp.json()
            if data.get('code') == 0:
                self.jwt_token = data['result']['token']
                self.market_headers = {
                    'User-Agent': MARKET_UA,
                    'Accept': '*/*',
                    'jwtToken': self.jwt_token,
                    'X-Requested-With': 'com.chinamobile.mcloud',
                }
                self.market_cookies = {'jwtToken': self.jwt_token}
                return True
        except Exception:
            pass
        return False

    def query_cloud_info(self):
        """查询云朵信息：签到状态、云朵数量、待领取"""
        headers = self._build_market_headers()
        cookies = dict(self.market_cookies)
        try:
            resp = self.session.get(
                f'{MARKET_BASE_URL}/ycloud/signin/page/infoV3',
                params={'client': 'app'},
                headers=headers,
                cookies=cookies,
                timeout=15
            )
            data = resp.json()
            if data.get('code') == 0:
                result = data.get('result', {})
                today_sign = result.get('todaySignIn')
                if today_sign is None:
                    for day in result.get('cal') or []:
                        if day.get('t'):
                            today_sign = bool(day.get('s'))
                            break
                return {
                    'success': True,
                    'total': result.get('total', 0),
                    'toReceive': result.get('toReceive', 0),
                    'todaySignIn': today_sign,
                    'continuous': result.get('continuous', 0),
                }
            return {'success': False, 'message': data.get('msg', '未知错误')}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def query_prizes(self):
        """查询待领取奖品"""
        headers = {
            'User-Agent': UA,
            'Accept': '*/*',
            'Host': 'caiyun.feixin.10086.cn',
            'jwtToken': self.jwt_token,
        }
        cookies = {'jwtToken': self.jwt_token}
        timestamp = str(int(time.time() * 1000))
        try:
            resp = self.session.get(
                f"https://caiyun.feixin.10086.cn/market/prizeApi/checkPrize/getUserPrizeLogPage?currPage=1&pageSize=15&_={timestamp}",
                headers=headers,
                cookies=cookies,
                timeout=15
            )
            data = resp.json()
            prizes = []
            for item in (data.get('result', {}).get('result') or []):
                if item.get('flag') == 1:
                    prizes.append(item.get('prizeName', ''))
            return prizes
        except Exception:
            return []

    def query_full_info(self):
        """完整查询：Token有效性 + 签到 + 云朵 + 奖品"""
        if not self.get_jwt_token():
            return {'valid': False, 'message': 'Token已失效，请重新抓包绑定'}

        cloud_info = self.query_cloud_info()
        if not cloud_info.get('success'):
            return {'valid': True, 'cloud_error': cloud_info.get('message', '查询失败')}

        prizes = self.query_prizes()

        return {
            'valid': True,
            'total': cloud_info.get('total', 0),
            'toReceive': cloud_info.get('toReceive', 0),
            'todaySignIn': cloud_info.get('todaySignIn'),
            'continuous': cloud_info.get('continuous', 0),
            'prizes': prizes,
        }

    def query_exchange_list(self):
        """查询可兑换奖品列表"""
        headers = self._build_market_headers()
        cookies = dict(self.market_cookies)
        try:
            resp = self.session.get(
                f'{MARKET_BASE_URL}/ycloud/signin/page/exchangeList',
                headers=headers,
                cookies=cookies,
                timeout=15
            )
            data = resp.json()
            if data.get('code') == 0 and 'result' in data:
                all_prizes = []
                for _, arr in data['result'].items():
                    all_prizes.extend(arr)
                return {'success': True, 'prizes': [p for p in all_prizes if p.get('groupId') != 10]}
            return {'success': False, 'message': data.get('msg', '未知错误')}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def get_slide_puzzle_offset(self, device_id):
        """获取滑块验证码偏移量，失败时返回新版插件同款兜底值"""
        target_device_id = device_id
        if not target_device_id.startswith('B'):
            target_device_id = 'B' + target_device_id

        # 先向移动云盘接口拿滑块图和背景图，接口要求 deviceId 带 B 前缀。
        slide_headers = dict(self.market_headers)
        slide_headers.update({
            'Host': 'm.mcloud.139.com',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'deviceId': target_device_id,
            'appVersion': '12.5.4.0',
            'activityId': 'sign_in_3',
            'showLoading': 'true',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Android WebView";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'User-Agent': MARKET_ANDROID_UA,
            'Accept': '*/*',
            'Origin': 'https://m.mcloud.139.com',
            'X-Requested-With': 'com.chinamobile.mcloud',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': self._build_market_page_url(),
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7'
        })
        slide_cookies = dict(self.market_cookies)

        try:
            slide_resp = self.session.post(
                f'{MARKET_BASE_URL}/ycloud/auth-service/slide/getSlide',
                headers=slide_headers,
                cookies=slide_cookies,
                data={},
                timeout=15
            )
            slide_data = slide_resp.json()
            result = slide_data.get("result", {}) if slide_data.get("code") == 0 else {}
            puzzle_b64 = result.get("puzzle", "")
            picture_b64 = result.get("picture", "")
            if not puzzle_b64 or not picture_b64:
                return 257

            # 再把两张图交给 ddddocr 接口识别，接口异常时使用 257，保证 puzzleOffset 不为空。
            ocr_resp = requests.post(
                SLIDE_CAPTCHA_OCR_API,
                json={"slidingImage": puzzle_b64, "backImage": picture_b64, "simpleTarget": True},
                timeout=15
            )
            offset = int(float(ocr_resp.json().get("result", 257)))
            if offset <= 0:
                return 257
            return offset
        except Exception:
            return 257

    def do_exchange(self, prize_id, device_id):
        """执行兑换操作"""
        target_device_id = device_id
        if not target_device_id.startswith('B'):
            target_device_id = 'B' + target_device_id
        thumb_val = target_device_id[1:]

        exchange_headers = {
            'User-Agent': MARKET_ANDROID_UA,
            'Accept': '*/*',
            'jwtToken': self.jwt_token,
            'X-Requested-With': 'com.chinamobile.mcloud',
            'Host': 'm.mcloud.139.com',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'deviceId': target_device_id,
            'showLoading': 'true',
            'appVersion': '12.5.4.0',
            'activityId': 'sign_in_3',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua': '"Android WebView";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
            'sec-ch-ua-mobile': '?1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': self._build_market_page_url(),
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh,zh-CN;q=0.9,en-US;q=0.8,en;q=0.7',
        }

        exchange_cookies = dict(self.market_cookies)
        account_md5 = hashlib.md5(self.account.encode('utf-8')).hexdigest()
        exchange_cookies[f".thumbcache_{account_md5}"] = urllib.parse.quote(thumb_val)

        # 2026 年新版兑换接口要求携带滑块偏移 puzzleOffset，缺失会报“滑块验证参数不能为空”。
        puzzle_offset = self.get_slide_puzzle_offset(device_id)
        exc_url = f"https://m.mcloud.139.com/ycloud/signin/page/exchangeV2?prizeId={prize_id}&client=app&clientVersion=12.5.4&puzzleOffset={puzzle_offset}&smsCode="
        try:
            resp = self.session.get(exc_url, headers=exchange_headers, cookies=exchange_cookies, timeout=15)
            data = resp.json()
            if data.get("code") == 0:
                return {'success': True, 'message': '兑换成功'}
            msg = data.get("msg", "兑换失败")
            if "活动太火爆啦" in msg or "锁定失败" in msg:
                msg += "。请联系管理员检查设备标识"
            return {'success': False, 'message': msg}
        except Exception as e:
            return {'success': False, 'message': str(e)}


# 全局变量初始化
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_ydyp_user', key=userid)


def mask_phone(phone):
    if len(phone) >= 11:
        return phone[:3] + "****" + phone[-4:]
    return phone


def parse_token_value(token_raw, account):
    """解析存储的token值，返回 authorization
    兼容JSON新格式和旧字符串格式
    """
    try:
        data = json.loads(token_raw)
        if isinstance(data, dict) and data.get('auth_token'):
            p = data.get('phone', account)
            auth_token = data['auth_token']
            auth_b64 = base64.b64encode(f"mobile:{p}:{auth_token}".encode()).decode()
            return f"Basic {auth_b64}"
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    parts = token_raw.split('#')

    if len(parts) >= 2:
        if re.match(r'^1[3-9]\d{9}$', parts[-1].strip()):
            auth_value = '#'.join(parts[:-1])
        else:
            auth_value = '#'.join(parts[:-1])
    else:
        auth_value = token_raw

    return auth_value


def check_auth_status(account):
    today = str(datetime.now().date())
    auth_time = middleware.bucketGet('dd_ydyp_auth', account) or ''
    if not auth_time:
        return "未授权", "无"
    elif auth_time <= today:
        return "已过期", auth_time
    else:
        return "已授权", auth_time


def parse_accounts(uservalue):
    if not uservalue:
        return []
    try:
        cleaned = uservalue.strip('[]').strip()
        if cleaned:
            accounts = [acc.strip().strip("'\"") for acc in cleaned.split(',')]
            return [acc for acc in accounts if acc]
    except:
        pass
    return []


def validate_input(value, max_val, input_type="数字"):
    try:
        value = int(value)
        if value > max_val or value <= 0:
            sender.reply(f"❌ 请输入 1-{max_val} 之间的{input_type}")
            exit(0)
        return value
    except ValueError:
        sender.reply(f"❌ 请输入有效的{input_type}")
        exit(0)


def confirm_operation():
    response = sender.input(120000, 1, False)
    if response in ['Y', 'y', '是']:
        return True
    elif response in ['n', 'N', '否']:
        return False
    elif not response:
        sender.reply("⏰ 操作超时,已退出")
        exit(0)
    else:
        sender.reply("❌ 输入无效")
        exit(0)


def normalize_panel_type(panel_type_value):
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    return ''


def get_config():
    panel_type = normalize_panel_type(middleware.bucketGet('dd_ydyp', 'panel_type') or '')
    if not panel_type:
        sender.reply("=====配置错误=====\n❌ 对接面板类型填写无效\n请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai\n==================")
        exit(0)

    panel_config = (middleware.bucketGet('dd_ydyp', 'panel_config') or '').strip()

    return {
        'osname': middleware.bucketGet('dd_ydyp', 'ydyp_osname') or 'ydyp',
        'panel_config': panel_config,
        'price': Decimal(middleware.bucketGet('dd_ydyp', 'ydypVipmoney') or '0'),
        'coin': int(middleware.bucketGet('dd_ydyp', 'ydypcoin') or '0'),
        'use_daidai': panel_type == 'daidai',
        'panel_group': (middleware.bucketGet('dd_ydyp', 'panel_group') or '').strip(),
        'zsm': middleware.bucketGet('dd_ydyp', 'zsm') or '',
        'use_ma_pay': (middleware.bucketGet('dd_ydyp', 'use_ma_pay') or 'false').lower() == 'true',
    }


def generate_qrcode(url):
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception:
        return None

def send_qrcode_image(pay_sender, qrcode_url, pay_type):
    pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
    pay_type_name = pay_type_names.get(pay_type, pay_type)
    try:
        pay_sender.replyImage(qrcode_url)
        pay_sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付")
    except:
        pay_sender.reply(f'请使用【{pay_type_name}】扫描下方二维码完成支付:\n[CQ:image,file={qrcode_url}]')


class QingLongManager:
    def __init__(self):
        self.config = get_config()
        self.use_daidai = self.config.get('use_daidai', False)
        self.url, self.token = self._get_connection()

    def _get_connection(self):
        panel_config = self.config.get('panel_config', '')
        if not panel_config:
            sender.reply("=====配置错误=====\n❌ 未配置面板连接信息\n请填写对接面板配置\n==================")
            exit(0)

        parts = panel_config.split('丨')
        if len(parts) != 3:
            sender.reply(f"=====配置错误=====\n❌ 面板配置格式错误\n当前格式: {panel_config}\n正确格式: Host丨ID丨Secret\n==================")
            exit(0)

        url, key, secret = [p.strip() for p in parts]
        if not all([url, key, secret]):
            sender.reply("=====配置错误=====\n❌ 面板配置参数不完整\n==================")
            exit(0)

        if not url.startswith(('http://', 'https://')):
            sender.reply(f"=====配置错误=====\n❌ 面板地址格式错误: {url}\n==================")
            exit(0)

        if self.use_daidai:
            try:
                response = requests.post(f'{url}/api/open-api/token', json={"app_key": key, "app_secret": secret})
                if response.status_code == 200:
                    result = response.json()
                    access_token = result.get('data', {}).get('access_token')
                    if access_token:
                        return url, access_token
                sender.reply("=====配置错误=====\n❌ 获取呆呆面板Token失败\n==================")
                exit(0)
            except Exception as e:
                sender.reply(f"=====配置错误=====\n❌ 连接呆呆面板失败: {str(e)}\n==================")
                exit(0)
        else:
            try:
                token_url = f'{url}/open/auth/token?client_id={key}&client_secret={secret}'
                response = requests.get(token_url)
                if response.status_code == 200:
                    result = response.json()
                    if "token" in result.get('data', {}):
                        return url, result['data']['token']
                sender.reply("=====配置错误=====\n❌ 获取青龙Token失败\n==================")
                exit(0)
            except Exception as e:
                sender.reply(f"=====配置错误=====\n❌ 连接青龙失败: {str(e)}\n==================")
                exit(0)

    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

    def get_env_id(self, account):
        headers = self._get_headers()
        if self.use_daidai:
            params = {"keyword": str(account), "page_size": 100}
            response = requests.get(f"{self.url}/api/envs", headers=headers, params=params).json()
            data_list = response.get('data', [])
            if isinstance(data_list, list):
                for env in data_list:
                    if env.get('name') == self.config['osname'] and str(account) in (env.get('remarks') or ''):
                        return env['id']
            return None
        else:
            url = f"{self.url}/open/envs"
            response = requests.get(url, headers=headers).json()
            if response.get('code') == 200:
                for env in response.get('data', []):
                    if env.get('name') == self.config['osname'] and str(account) in (env.get('remarks') or ''):
                        return env['id']
            return None

    def add_or_update_env(self, account, value):
        value = build_panel_value(value, account)
        env_id = self.get_env_id(account)
        auth_time = middleware.bucketGet('dd_ydyp_auth', account) or str(datetime.now().date())

        data = {
            "value": value,
            "name": self.config['osname'],
            "remarks": f'移动云盘:{account}丨用户:{userid}丨到期:{auth_time}丨云盘管理'
        }

        headers = self._get_headers()

        if self.use_daidai:
            if self.config.get('panel_group'):
                data["group"] = self.config['panel_group']
            if env_id:
                requests.put(f"{self.url}/api/envs/{env_id}", headers=headers, json=data)
            else:
                requests.post(f"{self.url}/api/envs", headers=headers, json=data)
        else:
            if env_id:
                data["id"] = env_id
                requests.put(f"{self.url}/open/envs", headers=headers, json=data)
            else:
                requests.post(f"{self.url}/open/envs", headers=headers, json=[data])

    def delete_env(self, env_id):
        if env_id:
            headers = self._get_headers()
            if self.use_daidai:
                requests.delete(f"{self.url}/api/envs/{env_id}", headers=headers)
            else:
                requests.delete(f"{self.url}/open/envs", headers=headers, json=[env_id])


class PaymentHandler:
    def __init__(self):
        self.config = get_config()

    def _get_ma_pay_config(self):
        if not self.config.get('use_ma_pay'):
            return None
        cfg = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
            'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
            'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
        }
        if cfg['switch'].lower() != 'true' or not all([cfg['gateway'], cfg['pid'], cfg['key']]):
            return None
        return cfg

    def process_payment(self, months, accounts_count=1, account=None):
        self.config = get_config()
        total_money = Decimal(months) * self.config['price'] * accounts_count
        total_coins = self.config['coin'] * months * accounts_count
        ma_pay_config = self._get_ma_pay_config()
        show_wechat_pay = bool(self.config['zsm']) and not self.config['use_ma_pay']
        show_ma_pay = self.config['use_ma_pay'] and bool(ma_pay_config)
        show_coin_pay = self.config['coin'] > 0

        if not show_wechat_pay and not show_ma_pay and not show_coin_pay and float(total_money) > 0:
            sender.reply('❌ 未配置可用收款方式,请联系管理员!')
            return False

        if float(total_money) == 0:
            return self._process_free_auth(months, account)

        return self._show_payment_options(total_money, total_coins, accounts_count, months, account, ma_pay_config)

    def _process_free_auth(self, months, account=None):
        if account:
            current_auth = middleware.bucketGet('dd_ydyp_auth', account)
            current_time = datetime.now().strftime("%Y-%m-%d")
            if current_auth and current_auth > current_time:
                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
            else:
                auth_date = datetime.now()
            new_expiry = auth_date + timedelta(days=months * 30)
            return new_expiry.strftime("%Y-%m-%d"), 0, 0, "免费授权"
        else:
            current_date = datetime.now().date()
            new_expiry = current_date + timedelta(days=months * 30)
            return str(new_expiry), 0, 0, "免费授权"

    def _show_payment_options(self, total_money, total_coins, accounts_count, months, account=None, ma_pay_config=None):
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        show_wechat_pay = bool(self.config['zsm']) and not self.config['use_ma_pay']
        show_ma_pay = self.config['use_ma_pay'] and bool(ma_pay_config)

        options = [
            "=====选择支付方式====",
            "📦 订单信息:",
            f"   📱 账号数量: {accounts_count}个",
            f"   ⏰ 授权时长: {months}月",
            "",
            "💳 支付方式:"
        ]

        options_map = {}
        option_num = 1

        if show_wechat_pay:
            options.extend([
                f"   {option_num}️⃣ 微信支付",
                f"      💰 需支付: {total_money}元"
            ])
            options_map[str(option_num)] = 'wechat'
            option_num += 1

        if show_ma_pay:
            options.extend([
                f"   {option_num}️⃣ 码支付",
                f"      💰 需支付: {total_money}元"
            ])
            options_map[str(option_num)] = 'ma'
            option_num += 1

        if self.config['coin'] > 0:
            options.extend([
                f"   {option_num}️⃣ 积分支付",
                f"      🎯 需消耗: {total_coins}积分",
                f"      💫 当前余额: {usercoin}积分"
            ])
            options_map[str(option_num)] = 'coin'

        options.extend([
            "",
            "💡 请回复数字选择支付方式",
            "💡 回复'q'取消操作",
            "=================="
        ])

        sender.reply("\n".join(options))
        choice = sender.input(60000, 1, False)

        if choice == 'q':
            sender.reply("✅ 已取消支付")
            return False
        selected_pay = options_map.get(choice)
        if selected_pay == 'wechat' and show_wechat_pay:
            return self._process_wechat_pay(total_money, accounts_count, months, account)
        elif selected_pay == 'ma' and show_ma_pay:
            return self._process_ma_pay(total_money, months, account, ma_pay_config)
        elif selected_pay == 'coin' and self.config['coin'] > 0:
            return self._process_coin_pay(total_coins, usercoin, months, account)
        else:
            sender.reply("❌ 输入无效")
            return False

    def _process_wechat_pay(self, total_money, accounts_count, months, account=None):
        pay_msg = f"=====微信扫码支付====\n🎫 商品: 移动云盘授权\n📱 账号数量: {accounts_count}个\n📅 时长: {months}月\n💰 金额: {total_money}元\n请使用微信扫码支付\n回复'ok'确认已支付\n回复'q'取消支付\n=================="
        sender.reply(pay_msg)
        sender.replyImage(self.config['zsm'])

        while True:
            response = sender.input(300000, 1, False)
            if not response:
                sender.reply("⏰ 支付超时,已取消")
                return False
            if response.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if response.lower() == 'ok':
                break
            sender.reply("💡 请回复'ok'确认已支付，或回复'q'取消")

        if account:
            current_auth = middleware.bucketGet('dd_ydyp_auth', account)
            current_time = datetime.now().strftime("%Y-%m-%d")
            if current_auth and current_auth > current_time:
                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
            else:
                auth_date = datetime.now()
            new_expiry = (auth_date + timedelta(days=months * 30)).strftime("%Y-%m-%d")
        else:
            new_expiry = str(datetime.now().date() + timedelta(days=months * 30))

        return new_expiry, float(total_money), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "微信支付"

    def _process_ma_pay(self, total_money, months, account=None, ma_pay_config=None):
        if not ma_pay_config:
            sender.reply("❌ 码支付配置异常，请联系管理员")
            return False

        out_trade_no = f"ydyp_{userid}_{int(time.time())}"
        pay_types = [t.strip() for t in ma_pay_config['type'].split(',') if t.strip()]

        if len(pay_types) > 1:
            type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
            type_menu = "=====选择支付通道=====\n"
            for i, pt in enumerate(pay_types, 1):
                type_menu += f"[{i}] {type_names.get(pt, pt)}\n"
            type_menu += "------------------\n回复数字选择\n=================="
            sender.reply(type_menu)
            type_choice = sender.input(30000, 1, False)
            if not type_choice:
                sender.reply("⏰ 操作超时")
                return False
            try:
                pay_type = pay_types[int(type_choice) - 1]
            except (ValueError, IndexError):
                sender.reply("❌ 选择无效")
                return False
        else:
            pay_type = pay_types[0] if pay_types else 'alipay'

        params = {
            'pid': ma_pay_config['pid'],
            'type': pay_type,
            'out_trade_no': out_trade_no,
            'name': '移动云盘授权',
            'money': str(total_money),
            'notify_url': ma_pay_config['notify_url'],
            'return_url': ma_pay_config.get('return_url') or ma_pay_config['notify_url'],
            'param': userid
        }
        params = {k: v for k, v in params.items() if v}
        sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode('utf-8')).hexdigest().lower()
        params['sign'] = sign
        params['sign_type'] = 'MD5'

        gateway = ma_pay_config['gateway']
        if gateway.endswith('/'):
            gateway = gateway[:-1]
        mapi_url = f"{gateway}/mapi.php"

        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(mapi_url, data=params, headers=headers, timeout=10)

            if response.status_code != 200:
                sender.reply(f"❌ 创建支付订单失败，HTTP状态码: {response.status_code}")
                return False

            try:
                result = response.json()
            except:
                sender.reply("❌ 创建支付订单失败，返回数据格式错误")
                return False

            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')

            if code == 1:
                payurl = result.get('payurl', '')
                if not payurl:
                    sender.reply("❌ 未获取到支付链接")
                    return False

                qr_url = generate_qrcode(payurl)
                if qr_url:
                    sender.reply(f"=====码支付=====\n🎫 商品: 移动云盘授权\n💰 金额: {total_money}元\n⏰ 有效期: 5分钟\n==================")
                    send_qrcode_image(sender, qr_url, pay_type)
                else:
                    sender.reply(f"=====码支付=====\n🎫 商品: 移动云盘授权\n💰 金额: {total_money}元\n⏰ 有效期: 5分钟\n------------------\n二维码生成失败，请点击链接完成支付:\n{payurl}\n==================")
            else:
                if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                    sender.reply(f"❌ 码支付暂不可用({msg})")
                else:
                    sender.reply(f"❌ 创建订单失败: {msg}")
                return False
        except Exception as e:
            sender.reply(f"❌ 支付请求失败: {str(e)}")
            return False

        for _ in range(60):
            check_url = f"{gateway}/xpay/epay/api.php"
            check_params = {
                'act': 'order',
                'pid': ma_pay_config['pid'],
                'key': ma_pay_config['key'],
                'out_trade_no': out_trade_no
            }
            try:
                check_resp = requests.get(check_url, params=check_params, timeout=10)
                check_result = check_resp.json()
                if check_result.get('code') == 1 and check_result.get('status') == 1:
                    if account:
                        current_auth = middleware.bucketGet('dd_ydyp_auth', account)
                        current_time = datetime.now().strftime("%Y-%m-%d")
                        if current_auth and current_auth > current_time:
                            auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                        else:
                            auth_date = datetime.now()
                        new_expiry = (auth_date + timedelta(days=months * 30)).strftime("%Y-%m-%d")
                    else:
                        new_expiry = str(datetime.now().date() + timedelta(days=months * 30))
                    return new_expiry, float(total_money), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "码支付"
            except Exception as e:
                print(f"查询订单状态出错: {str(e)}")

            result = sender.listen(5000)
            if result == 'q' or result == 'Q':
                sender.reply("✅ 已取消支付")
                return False

        sender.reply("⏰ 支付超时，如已支付请联系管理员")
        return False

    def _process_coin_pay(self, total_coins, usercoin, months, account=None):
        if int(usercoin) < total_coins:
            sender.reply(f"=====积分不足=====\n👤 当前积分: {usercoin}\n📍 需要积分: {total_coins}\n==================")
            return False

        sender.reply(f"=====积分支付确认=====\n💫 消耗积分: {total_coins}\n⏰ 授权时长: {months}月\n确认请回复【y】\n取消请回复【n】\n==================")

        if confirm_operation():
            try:
                new_balance = int(usercoin) - total_coins
                middleware.bucketSet('dd_sign_points', userid, str(new_balance))

                if account:
                    current_auth = middleware.bucketGet('dd_ydyp_auth', account)
                    current_time = datetime.now().strftime("%Y-%m-%d")
                    if current_auth and current_auth > current_time:
                        auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                    else:
                        auth_date = datetime.now()
                    new_expiry = auth_date + timedelta(days=months * 30)
                    return new_expiry.strftime("%Y-%m-%d"), total_coins, new_balance, "积分支付"
                else:
                    current_date = datetime.now().date()
                    new_expiry = current_date + timedelta(days=months * 30)
                    return str(new_expiry), total_coins, new_balance, "积分支付"
            except Exception as e:
                sender.reply(f"❌ 积分支付处理失败: {str(e)}")
                return False
        else:
            sender.reply("✅ 已取消支付")
            return False


class YdypManager:
    def __init__(self):
        self.ql = None
        self.payment = PaymentHandler()

    def _get_ql(self):
        if self.ql is None:
            self.ql = QingLongManager()
        return self.ql

    def login_account(self):
        menu = "=====移动云盘账号绑定=====\n请选择绑定方式:\n[1] 手动Token登录\n[2] 短信验证码登录\n------------------\n回复数字选择\n回复'q'退出\n=================="
        sender.reply(menu)

        choice = sender.input(60000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply("✅ 已取消绑定")
            exit(0)

        if choice == '1':
            self._manual_login()
        elif choice == '2':
            self._sms_login()
        else:
            sender.reply("❌ 输入无效")

    def _sms_login(self):
        if not _HAS_CRYPTO:
            sender.reply("❌ 验证码登录需要pycryptodome库，当前环境不支持\n💡 请使用手动Token方式绑定")
            return

        sender.reply("=====短信验证码登录=====\n请输入手机号:\n==================")
        phone = sender.input(60000, 1, False)
        if not phone or phone.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        phone = phone.strip()
        if not re.match(r'^1[3-9]\d{9}$', phone):
            sender.reply("❌ 手机号格式不正确")
            return

        def _get_sms_code():
            sender.reply("✅ 短信已发送，请输入验证码:\n(回复'q'取消)")
            code = sender.input(120000, 1, False)
            if not code or code.lower() == 'q':
                return None
            return code.strip()

        result = _sms_login_flow(phone, _get_sms_code)

        if not result.get("success"):
            sender.reply(f"❌ {result.get('message', '登录失败')}")
            return

        auth_token = result["auth_token"]

        store_data = json.dumps({
            "phone": phone,
            "auth_token": auth_token,
        }, ensure_ascii=False)
        middleware.bucketSet('dd_ydyp_token', phone, store_data)

        accounts = parse_accounts(uservalue) or []
        if phone not in accounts:
            accounts.append(phone)
        middleware.bucketSet('dd_ydyp_user', userid, str(accounts))

        auth_status, auth_time = check_auth_status(phone)
        status_icon = "✅" if auth_status == "已授权" else "❌"
        next_step = '发送 移动云盘管理 可管理账号' if auth_status == "已授权" else '发送 移动云盘管理 可进行授权'
        sender.reply(f"=====登录成功=====\n📱 账号: {mask_phone(phone)}\n🔐 授权状态: {status_icon} {auth_status}\n⏰ 下一步: {next_step}\n==================")

    def _manual_login(self):
        guide = """=====手动Token登录=====
请按格式输入:
Authorization值#手机号

📝 获取方式:
1. 打开移动云盘APP，抓包 authTokenRefresh.do
2. 复制请求头中 Authorization 的值

💡 示例:
Basic xxxx#13812345678

🔰 支持批量绑定，一行一个账号
回复'q'退出操作
=================="""
        sender.reply(guide)

        account_info = sender.input(120000, 1, False)
        if not account_info or account_info.lower() == 'q':
            sender.reply("✅ 已取消绑定")
            exit(0)

        lines = account_info.strip().split('\n')
        success_count = 0
        fail_count = 0
        fail_phones = []
        accounts = parse_accounts(uservalue) or []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split('#')
            if len(parts) < 2:
                fail_count += 1
                continue

            phone = None

            if re.match(r'^1[3-9]\d{9}$', parts[-1].strip()):
                phone = parts[-1].strip()
                auth_value = '#'.join(parts[:-1])
            elif len(parts) >= 3 and re.match(r'^1[3-9]\d{9}$', parts[-2].strip()):
                phone = parts[-2].strip()
                auth_value = '#'.join(parts[:-2])
            else:
                fail_count += 1
                continue

            if not auth_value.strip():
                fail_count += 1
                continue

            api = YdypAPI(auth_value, phone)
            sso_token = api.get_sso_token()
            if not sso_token:
                fail_count += 1
                fail_phones.append(mask_phone(phone))
                continue

            raw_token = _extract_auth_token(auth_value)
            if raw_token:
                store_data = json.dumps({
                    "phone": phone,
                    "auth_token": raw_token,
                }, ensure_ascii=False)
            else:
                store_data = f"{auth_value}#{phone}"

            middleware.bucketSet('dd_ydyp_token', phone, store_data)
            if phone not in accounts:
                accounts.append(phone)
            success_count += 1

        if accounts:
            middleware.bucketSet('dd_ydyp_user', userid, str(accounts))

        if len(lines) > 1:
            msg = f"=====批量绑定结果=====\n✅ 成功: {success_count}个账号\n❌ 失败: {fail_count}个账号"
            if fail_phones:
                msg += f"\n\n⚠️ 验证失败账号:"
                for fp in fail_phones:
                    msg += f"\n   • {fp}"
                msg += "\n💡 请检查Authorization是否正确/过期"
            msg += "\n💡 发送 移动云盘管理 可管理账号\n=================="
            sender.reply(msg)
        elif success_count == 1:
            phone_result = None
            for line in lines:
                p = line.strip().split('#')
                if re.match(r'^1[3-9]\d{9}$', p[-1].strip()):
                    phone_result = p[-1].strip()
            if phone_result:
                auth_status, auth_time = check_auth_status(phone_result)
                status_icon = "✅" if auth_status == "已授权" else "❌"
                next_step = '发送 移动云盘管理 可管理账号' if auth_status == "已授权" else '发送 移动云盘管理 可进行授权'
                sender.reply(f"=====移动云盘账号绑定=====\n📱 绑定账号: {mask_phone(phone_result)}\n🔐 授权状态: {status_icon} {auth_status}\n⏰ 下一步: {next_step}\n==================")
            else:
                sender.reply("=====绑定成功=====\n✅ 账号已绑定\n💡 发送 移动云盘管理 可管理账号\n==================")
        else:
            msg = "=====绑定失败=====\n"
            if fail_phones:
                msg += f"❌ Token验证失败: {fail_phones[0]}\n💡 请检查Authorization是否正确或已过期"
            else:
                msg += "❌ 格式错误，请检查后重试\n正确格式: Authorization值#手机号"
            msg += "\n=================="
            sender.reply(msg)

    def manage_accounts(self):
        accounts = parse_accounts(uservalue)
        if not accounts:
            sender.reply("=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 移动云盘登录 绑定账号\n==================")
            return

        menu_items = ["=====移动云盘账号管理=====", "[0] 全部账号授权", "------------------"]

        for i, account in enumerate(accounts, 1):
            auth_status, auth_time = check_auth_status(account)
            vip_status = auth_time if auth_status == "已授权" else "未授权"
            menu_items.append(f"[{i}] 账号: {mask_phone(account)}")
            menu_items.append(f"    授权至: {vip_status}")
            menu_items.append("------------------")

        menu_items.append("[99] 删除所有账号")
        menu_items.extend(["------------------", "回复数字选择账号", "回复'q'退出", "=================="])
        sender.reply("\n".join(menu_items))

        choice = sender.input(120000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply('✅ 已退出管理')
            return

        if choice == '0':
            self._batch_authorize(accounts)
        elif choice == '99':
            self._delete_all_accounts(accounts)
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    self._single_account_operation(accounts[index])
                else:
                    sender.reply("❌ 无效的账号编号")
            except ValueError:
                sender.reply("❌ 请输入有效的数字")

    def _batch_authorize(self, accounts):
        need_auth = [acc for acc in accounts if check_auth_status(acc)[0] != "已授权"]
        if not need_auth:
            sender.reply("=====无需授权=====\n✅ 所有账号均已授权且未过期\n==================")
            return

        sender.reply(f"=====批量授权确认=====\n📊 待授权账号: {len(need_auth)}个\n📅 请输入授权月数(1-12):\n==================")
        months_input = sender.input(120000, 1, False)
        if not months_input:
            return

        months = validate_input(months_input, 12, "月数")
        result = self.payment.process_payment(months, len(need_auth))

        if result:
            new_expiry, amount, time_info, pay_type = result
            success_count = 0
            ql = self._get_ql()
            for account in need_auth:
                try:
                    middleware.bucketSet('dd_ydyp_auth', account, new_expiry)
                    token = middleware.bucketGet('dd_ydyp_token', account)
                    if token:
                        ql.add_or_update_env(account, token)
                        success_count += 1
                except Exception:
                    continue

            sender.reply(f"=====支付成功=====\n🎫 商品: 移动云盘批量授权\n✅ 成功: {success_count}/{len(need_auth)}个账号\n📅 到期时间: {new_expiry}\n💰 支付方式: {pay_type}\n==================")

    def _delete_all_accounts(self, accounts):
        sender.reply("=====危险操作=====\n⚠️ 即将删除所有绑定的账号\n此操作不可恢复！\n确认删除? (Y/N)\n==================")

        if confirm_operation():
            try:
                ql = self._get_ql()
                for account in accounts:
                    env_id = ql.get_env_id(account)
                    if env_id:
                        ql.delete_env(env_id)
                    middleware.bucketDel('dd_ydyp_token', account)
                    middleware.bucketDel('dd_ydyp_auth', account)

                middleware.bucketDel('dd_ydyp_user', userid)
                sender.reply("=====删除完成=====\n✅ 已删除所有账号信息\n💡 如需重新使用，请重新绑定账号\n==================")
            except Exception as e:
                sender.reply(f"删除失败: {str(e)}")
        else:
            sender.reply("✅ 已取消删除")

    def _single_account_operation(self, account):
        auth_status, auth_time = check_auth_status(account)
        vip_status = auth_time if auth_status == "已授权" else "未授权"
        menu = f"=====账号操作菜单=====\n📱 账号: {mask_phone(account)}\n📅 授权至: {vip_status}\n------------------\n[1] 授权续费\n[2] 删除账号\n[3] 同步到面板\n[4] 续期Token\n------------------\n回复数字选择操作\n回复'q'退出\n=================="
        sender.reply(menu)

        operation = sender.input(120000, 1, False)
        if not operation:
            return

        if operation == '1':
            self._authorize_single_account(account)
        elif operation == '2':
            self._delete_single_account(account)
        elif operation == '3':
            self._sync_single_account(account)
        elif operation == '4':
            self._refresh_single_account(account)
        else:
            sender.reply("❌ 无效的操作选项")

    def _authorize_single_account(self, account):
        sender.reply(f"=====账号授权=====\n📱 授权账号: {mask_phone(account)}\n请输入授权月数(1-12):\n==================")
        months_input = sender.input(120000, 1, False)
        if not months_input:
            return

        months = validate_input(months_input, 12, "月数")
        result = self.payment.process_payment(months, 1, account)

        if result:
            new_expiry, amount, time_info, pay_type = result
            middleware.bucketSet('dd_ydyp_auth', account, new_expiry)
            token = middleware.bucketGet('dd_ydyp_token', account)
            if token:
                ql = self._get_ql()
                ql.add_or_update_env(account, token)
            sender.reply(f"=====支付成功=====\n🎫 商品: 移动云盘授权\n📱 账号: {mask_phone(account)}\n📅 到期时间: {new_expiry}\n💰 支付方式: {pay_type}\n==================")

    def _delete_single_account(self, account):
        sender.reply(f"=====删除账号=====\n⚠️ 即将删除账号: {mask_phone(account)}\n此操作不可恢复！\n确认删除? (Y/N)\n==================")

        if confirm_operation():
            try:
                ql = self._get_ql()
                env_id = ql.get_env_id(account)
                if env_id:
                    ql.delete_env(env_id)

                middleware.bucketDel('dd_ydyp_token', account)
                middleware.bucketDel('dd_ydyp_auth', account)

                accounts = parse_accounts(uservalue)
                if account in accounts:
                    accounts.remove(account)
                if accounts:
                    middleware.bucketSet('dd_ydyp_user', userid, str(accounts))
                else:
                    middleware.bucketDel('dd_ydyp_user', userid)

                sender.reply(f"=====删除成功=====\n✅ 已删除账号: {mask_phone(account)}\n==================")
            except Exception as e:
                sender.reply(f"删除失败: {str(e)}")
        else:
            sender.reply("✅ 已取消删除")

    def _sync_single_account(self, account):
        auth_status, auth_time = check_auth_status(account)
        if auth_status != "已授权":
            sender.reply(f"=====同步失败=====\n📱 账号: {mask_phone(account)}\n❌ 账号未授权或已过期\n💡 请先进行授权\n==================")
            return

        token = middleware.bucketGet('dd_ydyp_token', account)
        if not token:
            sender.reply("❌ 账号信息不完整，请重新绑定")
            return

        try:
            ql = self._get_ql()
            ql.add_or_update_env(account, token)
            sender.reply(f"=====同步成功=====\n📱 账号: {mask_phone(account)}\n✅ 已同步到面板\n==================")
        except Exception as e:
            sender.reply(f"同步失败: {str(e)}")

    def _refresh_single_account(self, account):
        sender.reply(f"=====Token续期=====\n📱 账号: {mask_phone(account)}\n⏳ 正在续期...\n==================")
        success, msg = _try_refresh_account(account)
        if success:
            token = middleware.bucketGet('dd_ydyp_token', account)
            if token:
                try:
                    ql = self._get_ql()
                    ql.add_or_update_env(account, token)
                except Exception:
                    pass
            sender.reply(f"=====续期成功=====\n📱 账号: {mask_phone(account)}\n✅ Token已续期并同步到面板\n==================")
        else:
            sender.reply(f"=====续期失败=====\n📱 账号: {mask_phone(account)}\n❌ {msg}\n💡 请重新登录绑定\n==================")

    def query_accounts(self):
        accounts = parse_accounts(uservalue)
        if not accounts:
            sender.reply("=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 移动云盘登录 绑定账号\n==================")
            return

        for i, account in enumerate(accounts, 1):
            auth_status, auth_time = check_auth_status(account)

            if auth_status == "已授权":
                auth_display = auth_time
            else:
                auth_display = '❌ 已过期，请发"移动云盘管理"续费'

            token_raw = middleware.bucketGet('dd_ydyp_token', account)
            if not token_raw:
                info_msg = "=====================\n"
                info_msg += f"📱 账号: {mask_phone(account)}\n"
                info_msg += f"📅 授权到期: {auth_display}\n"
                info_msg += f"📈 账号检测: ❌ 凭证未绑定\n"
                info_msg += "====================="
                sender.reply(info_msg)
                continue

            auth_value = parse_token_value(token_raw, account)

            api = YdypAPI(auth_value, account)
            info = api.query_full_info()

            info_msg = "=====================\n"
            info_msg += f"📱 账号: {mask_phone(account)}\n"

            if not info.get('valid'):
                refreshed, refresh_msg = _try_refresh_account(account)
                if refreshed:
                    token_raw = middleware.bucketGet('dd_ydyp_token', account)
                    auth_value, device_id = parse_token_value(token_raw, account)
                    api = YdypAPI(auth_value, account, device_id)
                    info = api.query_full_info()
                    if info.get('valid'):
                        try:
                            ql = self._get_ql()
                            ql.add_or_update_env(account, token_raw)
                        except Exception:
                            pass
                        info_msg += f"📅 授权到期: {auth_display}\n"
                        info_msg += f"📈 账号检测: ✅ Token已自动续期\n"
                    else:
                        info_msg += f"📅 授权到期: {auth_display}\n"
                        info_msg += f"📈 账号检测: ❌ Token已失效(续期后仍无效)\n"
                        info_msg += f"💡 请重新登录绑定"
                        info_msg += "\n====================="
                        sender.reply(info_msg)
                        if i < len(accounts):
                            time.sleep(1)
                        continue
                else:
                    info_msg += f"📅 授权到期: {auth_display}\n"
                    info_msg += f"📈 账号检测: ❌ Token已失效(自动续期失败)\n"
                    info_msg += f"💡 请重新登录绑定"
                    info_msg += "\n====================="
                    sender.reply(info_msg)
                    if i < len(accounts):
                        time.sleep(1)
                    continue

            if info.get('cloud_error'):
                info_msg += f"📅 授权到期: {auth_display}\n"
                info_msg += f"📈 账号检测: ✅ Token有效\n"
                info_msg += f"☁️ 云朵查询: ❌ {info.get('cloud_error')}"
            else:
                today_sign = info.get('todaySignIn')
                sign_text = "✅ 已签到" if today_sign else "❌ 未签到"

                info_msg += f"📅 授权到期: {auth_display}\n"
                info_msg += f"📈 账号检测: ✅ 账号正常\n"
                info_msg += f"☁️ 云朵数量: {info.get('total', 0)}\n"
                info_msg += f"🎁 待领取: {info.get('toReceive', 0)}云朵\n"
                info_msg += f"🎯 今日签到: {sign_text}\n"
                info_msg += f"🔥 连续签到: {info.get('continuous', 0)}天"

                prizes = info.get('prizes', [])
                if prizes:
                    info_msg += f"\n🏆 待领取奖品: {', '.join(prizes)}"

            info_msg += "\n====================="
            sender.reply(info_msg)

            if i < len(accounts):
                time.sleep(1)



def sync_users():
    """同步已授权用户到面板"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)

    sender.reply("=====移动云盘同步=====\n⏳ 正在同步已授权用户到面板...\n==================")

    users = normalize_bucket_keys(middleware.bucketAllKeys('dd_ydyp_user'))
    if not users:
        sender.reply("=====同步结果=====\n❌ 未找到任何绑定用户\n==================")
        return

    try:
        ql = QingLongManager()
    except Exception:
        sender.reply("❌ 连接面板失败")
        return

    success_count = 0
    skip_count = 0
    fail_count = 0

    for user in users:
        accountlist = middleware.bucketGet('dd_ydyp_user', user)
        if not accountlist or accountlist == '{}':
            continue

        accounts = parse_accounts(accountlist)
        accounts = list(dict.fromkeys(accounts))

        for account in accounts:
            try:
                dqsj = str(datetime.now().date())
                accountVip = middleware.bucketGet('dd_ydyp_auth', account)
                token = middleware.bucketGet('dd_ydyp_token', account)

                if not accountVip or accountVip <= dqsj or not token:
                    skip_count += 1
                    continue

                ql.add_or_update_env(account, token)
                success_count += 1
            except Exception:
                fail_count += 1

    sender.reply(f"=====同步完成=====\n✅ 同步成功: {success_count}个账号\n⏭️ 跳过未授权: {skip_count}个账号\n❌ 同步失败: {fail_count}个账号\n==================")


def admin_backend():
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)

    menu = """=====移动云盘后台管理=====
[1] 云盘一键全部授权
[2] 云盘用户单独授权
[3] 云盘面板同步
[4] 云盘清理
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(menu)
    xz = sender.input(60000, 1, False)

    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出后台管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '1':
        _admin_auth_all()
    elif xz == '2':
        _admin_auth_single()
    elif xz == '3':
        _admin_sync_all()
    elif xz == '4':
        _admin_clean_expired()
    else:
        sender.reply("❌ 输入的选项无效!")


def _admin_auth_all():
    users = normalize_bucket_keys(middleware.bucketAllKeys('dd_ydyp_user'))
    if not users:
        sender.reply("❌ 未找到任何绑定的移动云盘账号")
        return

    sender.reply("=====请输入授权天数=====\n回复数字设置天数\n回复\"q\"退出操作\n==================")

    sjts = sender.input(60000, 1, False)
    if sjts == 'q' or sjts == 'Q':
        sender.reply("✅ 已取消授权")
        return
    elif sjts is None:
        sender.reply("⏰ 操作超时,已退出")
        return

    try:
        sjts = int(sjts)
    except:
        sender.reply("❌ 天数必须是数字!")
        return

    success_count = 0
    fail_count = 0

    try:
        ql = QingLongManager()
    except Exception:
        sender.reply("❌ 连接面板失败")
        return

    for user in users:
        accountlist = middleware.bucketGet('dd_ydyp_user', user)
        if not accountlist or accountlist == '{}':
            continue

        accounts = parse_accounts(accountlist)
        accounts = list(dict.fromkeys(accounts))

        for account in accounts:
            try:
                dqsj = datetime.now().strftime("%Y-%m-%d")
                accountVip = middleware.bucketGet('dd_ydyp_auth', account)
                token = middleware.bucketGet('dd_ydyp_token', account)

                if not token:
                    fail_count += 1
                    continue

                if accountVip and accountVip > dqsj:
                    sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                    new_sqsj = sqsj + timedelta(days=sjts)
                else:
                    new_sqsj = datetime.now() + timedelta(days=sjts)
                new_sqsj = new_sqsj.strftime("%Y-%m-%d")

                middleware.bucketSet('dd_ydyp_auth', account, new_sqsj)
                ql.add_or_update_env(account, token)
                success_count += 1
            except Exception:
                fail_count += 1

    sender.reply(f"=====授权完成=====\n✅ 成功授权: {success_count}个账号\n❌ 授权失败: {fail_count}个账号\n⏰ 授权天数: {sjts}天\n==================")


def _admin_auth_single():
    sender.reply("======账号授权======\n请输入需要授权的用户ID\n(发送myuid可获取ID)\n------------------\n回复\"q\"退出操作\n==================")

    myuid = sender.input(60000, 1, False)
    if myuid == 'q' or myuid == 'Q':
        sender.reply("✅ 已退出授权")
        return
    elif myuid is None:
        sender.reply("⏰ 操作超时,已退出")
        return

    accountlist = middleware.bucketGet('dd_ydyp_user', myuid)
    if not accountlist or accountlist == '' or accountlist == '{}':
        sender.reply(f"=====查询结果=====\n❌ 未找到 {myuid} 的账号信息\n==================")
        return

    accounts = parse_accounts(accountlist)
    if not accounts:
        sender.reply("=====数据错误=====\n❌ 账号数据格式异常\n==================")
        return

    accounts = list(dict.fromkeys(accounts))

    account_list = "=======账号列表=====\n[0] 授权所有账号\n------------------"
    for i, account in enumerate(accounts, 1):
        accountVip = middleware.bucketGet('dd_ydyp_auth', account)
        vip_status = accountVip if accountVip else '未授权'
        account_list += f"\n[{i}] 账号: {mask_phone(account)}\n    授权至: {vip_status}\n------------------"
    account_list += "\n回复数字选择账号\n回复'q'退出\n=================="
    sender.reply(account_list)

    xz = sender.input(60000, 1, False)
    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出授权")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return

    try:
        xz = int(xz)
        if xz < 0 or (xz > len(accounts) and xz != 0):
            sender.reply(f"=====输入错误=====\n❌ 请输入 0-{len(accounts)} 之间的数字\n==================")
            return
    except ValueError:
        sender.reply("=====输入错误=====\n❌ 请输入正确的数字\n==================")
        return

    sender.reply("=====设置授权天数=====\n请输入要授权的天数\n回复数字设置天数\n回复\"q\"退出操作\n==================")

    sjts = sender.input(60000, 1, False)
    if sjts == 'q' or sjts == 'Q':
        sender.reply("✅ 已取消授权")
        return
    elif sjts is None:
        sender.reply("⏰ 操作超时,已退出")
        return

    try:
        sjts = int(sjts)
        if sjts <= 0:
            sender.reply("❌ 授权天数必须大于0!")
            return
    except ValueError:
        sender.reply("❌ 天数必须是数字!")
        return

    target_accounts = accounts if xz == 0 else [accounts[xz - 1]]

    try:
        ql = QingLongManager()
    except Exception:
        sender.reply("❌ 连接面板失败")
        return

    success_count = 0
    fail_count = 0

    for account in target_accounts:
        try:
            dqsj = datetime.now().strftime("%Y-%m-%d")
            accountVip = middleware.bucketGet('dd_ydyp_auth', account)
            token = middleware.bucketGet('dd_ydyp_token', account)

            if not token:
                fail_count += 1
                continue

            if accountVip and accountVip > dqsj:
                sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                new_sqsj = sqsj + timedelta(days=sjts)
            else:
                new_sqsj = datetime.now() + timedelta(days=sjts)
            new_sqsj = new_sqsj.strftime("%Y-%m-%d")

            middleware.bucketSet('dd_ydyp_auth', account, new_sqsj)
            ql.add_or_update_env(account, token)
            success_count += 1
        except Exception:
            fail_count += 1

    sender.reply(f"=====授权完成=====\n✅ 成功授权: {success_count}个账号\n❌ 授权失败: {fail_count}个账号\n⏰ 授权天数: {sjts}天\n==================")


def _admin_sync_all():
    sender.reply("=====同步变量=====\n⏳ 正在扫描已授权账号...\n==================")

    users = normalize_bucket_keys(middleware.bucketAllKeys('dd_ydyp_user'))
    if not users:
        sender.reply("❌ 未找到任何绑定的移动云盘账号")
        return

    try:
        ql = QingLongManager()
    except Exception:
        sender.reply("❌ 连接面板失败")
        return

    success_count = 0
    skip_count = 0
    fail_count = 0

    for user in users:
        accountlist = middleware.bucketGet('dd_ydyp_user', user)
        if not accountlist or accountlist == '{}':
            continue

        accounts = parse_accounts(accountlist)
        accounts = list(dict.fromkeys(accounts))

        for account in accounts:
            try:
                dqsj = datetime.now().strftime("%Y-%m-%d")
                accountVip = middleware.bucketGet('dd_ydyp_auth', account)
                token = middleware.bucketGet('dd_ydyp_token', account)

                if not accountVip or accountVip <= dqsj or not token:
                    skip_count += 1
                    continue

                ql.add_or_update_env(account, token)
                success_count += 1
            except Exception:
                fail_count += 1

    sender.reply(f"=====同步完成=====\n✅ 成功同步: {success_count}个账号\n⏭️ 跳过未授权: {skip_count}个账号\n❌ 同步失败: {fail_count}个账号\n==================")


def _admin_clean_expired():
    users = normalize_bucket_keys(middleware.bucketAllKeys('dd_ydyp_user'))
    if not users:
        sender.reply("❌ 未找到任何绑定的移动云盘账号")
        return

    sender.reply(f"=====开始清理过期账号=====\n🔍 共找到: {len(users)}个用户\n⏳ 清理中请稍候...\n==================")

    cleaned_count = 0
    today = str(datetime.now().date())

    try:
        ql = QingLongManager()
    except Exception:
        sender.reply("❌ 连接面板失败")
        return

    for user in users:
        try:
            accountlist = middleware.bucketGet('dd_ydyp_user', user)
            if not accountlist or accountlist == '{}':
                continue

            accounts = parse_accounts(accountlist)
            accounts = list(dict.fromkeys(accounts))
            valid_accounts = []

            for account in accounts:
                accountVip = middleware.bucketGet('dd_ydyp_auth', account)

                if not accountVip or accountVip <= today:
                    try:
                        env_id = ql.get_env_id(account)
                        if env_id:
                            ql.delete_env(env_id)
                    except Exception:
                        pass

                    middleware.bucketDel('dd_ydyp_token', account)
                    middleware.bucketDel('dd_ydyp_auth', account)
                    cleaned_count += 1
                else:
                    valid_accounts.append(account)

            valid_accounts = list(dict.fromkeys(valid_accounts))

            if valid_accounts:
                middleware.bucketSet('dd_ydyp_user', user, str(valid_accounts))
            else:
                middleware.bucketDel('dd_ydyp_user', user)

        except Exception:
            continue

    sender.reply(f"=====清理完成=====\n✅ 已清理: {cleaned_count}个过期账号\n🧹 清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n==================")


def show_tutorial():
    tutorial = """=====移动云盘教程=====
📌 指令列表:
  移动云盘登录 - 绑定账号
  移动云盘管理 - 授权/删除/同步
  移动云盘查询 - 查看账号状态
  移动云盘兑换 - 云朵兑换奖品
  移动云盘一键抢兑 - 定时抢兑(管理员)
  移动云盘停止抢兑 - 停止抢兑(管理员)
  移动云盘后台 - 后台管理(管理员)
------------------
📌 绑定格式: Authorization值#手机号
  推荐使用短信验证码登录，无需抓包
------------------
📌 定时兑换:
  用户发送 移动云盘兑换 设置目标
  管理员添加计划任务自动执行
  建议定时: 57 9,11,15,19,23 * * *
=================="""
    sender.reply(tutorial)


def within_exchange_window():
    now = local_now()
    windows = [
        (23, 50, 0, 10),
        (9, 50, 10, 10),
        (11, 50, 12, 10),
        (15, 50, 16, 10),
        (19, 50, 20, 10),
    ]
    for sh, sm, eh, em in windows:
        start = now.replace(hour=sh, minute=sm, second=0, microsecond=0)
        end = now.replace(hour=eh, minute=em, second=0, microsecond=0)
        if sh > eh:
            if now >= start or now <= end:
                return True
        else:
            if start <= now <= end:
                return True
    return False


def exchange_entry_point():
    accounts = parse_accounts(uservalue)
    if not accounts:
        sender.reply("=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 移动云盘登录 绑定账号\n==================")
        return

    if len(accounts) == 1:
        show_exchange_menu(accounts[0])
        return

    menu_items = ["=====请选择账号====="]
    for i, account in enumerate(accounts, 1):
        auth_status, auth_time = check_auth_status(account)
        status_icon = "✅" if auth_status == "已授权" else "❌"
        menu_items.append(f"[{i}] 账号: {mask_phone(account)}")
        menu_items.append(f"    授权: {status_icon} {auth_time if auth_status == '已授权' else '未授权'}")
        menu_items.append("------------------")
    menu_items.extend(["回复数字选择", "回复'q'退出", "=================="])
    sender.reply("\n".join(menu_items))

    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    try:
        idx = int(choice)
        if 1 <= idx <= len(accounts):
            show_exchange_menu(accounts[idx - 1])
        else:
            sender.reply("❌ 无效的选择")
    except ValueError:
        sender.reply("❌ 无效的选择")


def show_exchange_menu(account):
    phone_mask = mask_phone(account)

    auth_status, auth_time = check_auth_status(account)
    if auth_status != "已授权":
        sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n❌ 授权已过期，无法进行兑换\n💡 请先进行授权\n==================")
        return

    token_raw = middleware.bucketGet('dd_ydyp_token', account)
    if not token_raw:
        sender.reply(f"❌ 账号 {phone_mask} 信息不完整，请重新绑定")
        return

    auth_value = parse_token_value(token_raw, account)
    api = YdypAPI(auth_value, account)

    if not api.get_jwt_token():
        refreshed, _ = _try_refresh_account(account)
        if refreshed:
            token_raw = middleware.bucketGet('dd_ydyp_token', account)
            auth_value = parse_token_value(token_raw, account)
            api = YdypAPI(auth_value, account)
            if not api.get_jwt_token():
                sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n❌ Token已失效，请重新登录绑定\n==================")
                return
        else:
            sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n❌ Token已失效，请重新登录绑定\n==================")
            return

    cloud_info = api.query_cloud_info()
    total_cloud = cloud_info.get('total', 0) if cloud_info.get('success') else 0

    exchange_result = api.query_exchange_list()
    if not exchange_result.get('success'):
        sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n❌ 获取奖品列表失败: {exchange_result.get('message', '')}\n==================")
        return

    all_prizes = exchange_result.get('prizes', [])
    if not all_prizes:
        sender.reply(f"=====移动云盘兑换=====\n📱 账号: {phone_mask}\n❌ 当前没有可兑换的奖品\n==================")
        return

    product_lines = []
    for i, product in enumerate(all_prizes, 1):
        prize_name = product.get('prizeName', '未知奖品')
        cost = product.get('pOrder', 0)
        stock_status = "✅" if product.get('dailyRemainderCount', 0) > 0 else "❌"
        product_lines.append(f"[{i}] {prize_name} | {cost}云朵 {stock_status}")

    prize_target = middleware.bucketGet('dd_ydyp_prize', account)
    prize_line = f"⏰ 定时兑换: {prize_target}" if prize_target else "⏰ 定时兑换: 未设置"

    msg = f"""=====移动云盘兑换=====
📱 账号: {phone_mask}
☁️ 云朵余额: {total_cloud}
{prize_line}
------------------
{chr(10).join(product_lines)}
------------------
回复序号选择奖品
回复'q'退出
=================="""
    sender.reply(msg)

    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return

    try:
        idx = int(choice)
        if not (1 <= idx <= len(all_prizes)):
            raise ValueError()
    except ValueError:
        sender.reply("❌ 请输入有效的序号")
        return

    selected = all_prizes[idx - 1]
    prize_name = selected.get('prizeName', '未知奖品')
    cost = selected.get("pOrder", 0)
    stock = "有库存" if selected.get('dailyRemainderCount', 0) > 0 else "已售罄"

    action_items = [
        f"=====已选择奖品=====",
        f"🎁 奖品: {prize_name}",
        f"☁️ 需要: {cost}云朵 | {stock}",
        f"------------------",
        f"[1] 立即兑换",
        f"[2] 设为定时兑换",
        f"[3] 清除定时兑换",
        f"------------------",
        f"回复数字选择操作",
        f"回复'q'退出",
        f"==================",
    ]
    sender.reply("\n".join(action_items))

    action = sender.input(60000, 1, False)
    if not action or action.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return

    if action == '1':
        if selected.get('dailyRemainderCount', 0) <= 0:
            sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n❌ 该奖品已无库存\n==================")
            return
        if total_cloud < cost:
            sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n❌ 云朵不足({total_cloud}/{cost})\n==================")
            return

        ok_dev, dev_id = get_or_fetch_device_id(account)
        if not ok_dev:
            sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n❌ {dev_id}\n==================")
            return

        result = api.do_exchange(selected.get("prizeId"), dev_id)
        if result.get('success'):
            sender.reply(f"=====兑换成功=====\n📱 账号: {phone_mask}\n🎁 奖品: {prize_name}\n🟢 结果: 兑换成功\n==================")
        else:
            sender.reply(f"=====兑换失败=====\n📱 账号: {phone_mask}\n🎁 奖品: {prize_name}\n❌ {result.get('message', '未知错误')}\n==================")

    elif action == '2':
        middleware.bucketSet('dd_ydyp_prize', account, prize_name)
        sender.reply(f"=====移动云盘兑换=====\n📱 账号: {phone_mask}\n✅ 定时兑换已设置: {prize_name}\n💡 到达整点时将自动兑换\n==================")

    elif action == '3':
        try:
            middleware.bucketDel('dd_ydyp_prize', account)
        except Exception:
            pass
        sender.reply(f"=====移动云盘兑换=====\n📱 账号: {phone_mask}\n✅ 定时兑换目标已清除\n==================")

    else:
        sender.reply("❌ 无效的操作选项")


def handle_yijian_qiangdui():
    global STOP_EXCHANGE
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return
    if STOP_EXCHANGE:
        sender.reply("❌ 抢兑已被手动停止")
        return
    if not within_exchange_window():
        sender.reply("❌ 当前时间不在 0/10/12/16/20 点前后10分钟范围内，无法执行抢兑")
        return

    now = local_now()
    possible_targets = [
        now.replace(hour=0, minute=0, second=0, microsecond=0),
        now.replace(hour=10, minute=0, second=0, microsecond=0),
        now.replace(hour=12, minute=0, second=0, microsecond=0),
        now.replace(hour=16, minute=0, second=0, microsecond=0),
        now.replace(hour=20, minute=0, second=0, microsecond=0),
    ]
    if now.hour >= 23:
        target_time = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        future_targets = [t for t in possible_targets if t > now]
        if not future_targets:
            target_time = min(possible_targets)
        else:
            target_time = min(future_targets, key=lambda t: t - now)

    all_keys = normalize_bucket_keys(middleware.bucketAllKeys('dd_ydyp_prize'))
    if not all_keys:
        sender.reply("=====移动云盘一键抢兑=====\n❌ 暂无账号设置定时兑换\n💡 用户需先发送 移动云盘兑换 设置目标\n==================")
        return

    owner_map = {}
    all_users = normalize_bucket_keys(middleware.bucketAllKeys('dd_ydyp_user'))
    for u in all_users:
        acc_list = parse_accounts(middleware.bucketGet('dd_ydyp_user', u) or '')
        for ac in acc_list:
            owner_map[ac] = u

    bingfa = int(middleware.bucketGet('dd_ydyp', 'bingfa') or '20')
    concurrency_data = []
    fail_reasons = []
    cleaned_count = 0

    for account in all_keys:
        if STOP_EXCHANGE:
            sender.reply("❌ 抢兑已被手动停止")
            return

        prize_name = middleware.bucketGet('dd_ydyp_prize', account)
        if not prize_name:
            try:
                middleware.bucketDel('dd_ydyp_prize', account)
            except Exception:
                pass
            cleaned_count += 1
            continue

        phone_mask = mask_phone(account)

        if account not in owner_map:
            try:
                middleware.bucketDel('dd_ydyp_prize', account)
            except Exception:
                pass
            cleaned_count += 1
            continue

        auth_time = middleware.bucketGet('dd_ydyp_auth', account)
        if not auth_time or auth_time <= str(datetime.now().date()):
            fail_reasons.append(f"【{phone_mask}】授权已过期")
            try:
                middleware.bucketDel('dd_ydyp_prize', account)
            except Exception:
                pass
            cleaned_count += 1
            continue

        token_raw = middleware.bucketGet('dd_ydyp_token', account)
        if not token_raw:
            fail_reasons.append(f"【{phone_mask}】Token不存在")
            continue

        auth_value = parse_token_value(token_raw, account)
        api = YdypAPI(auth_value, account)

        if not api.get_jwt_token():
            refreshed, _ = _try_refresh_account(account)
            if refreshed:
                token_raw = middleware.bucketGet('dd_ydyp_token', account)
                auth_value = parse_token_value(token_raw, account)
                api = YdypAPI(auth_value, account)
                if not api.get_jwt_token():
                    fail_reasons.append(f"【{phone_mask}】Token已失效(续期后仍无效)")
                    continue
            else:
                fail_reasons.append(f"【{phone_mask}】Token已失效")
                continue

        exchange_result = api.query_exchange_list()
        if not exchange_result.get('success'):
            fail_reasons.append(f"【{phone_mask}】获取奖品列表失败")
            continue

        found_pid = None
        cost = 9999999
        for p in exchange_result.get('prizes', []):
            if p.get("prizeName") == prize_name:
                found_pid = p.get("prizeId")
                cost = p.get("pOrder", 9999999)
                break

        if not found_pid:
            fail_reasons.append(f"【{phone_mask}】未找到奖品: {prize_name}")
            continue

        cloud_info = api.query_cloud_info()
        total_cloud = cloud_info.get('total', 0) if cloud_info.get('success') else 0
        if total_cloud < cost:
            fail_reasons.append(f"【{phone_mask}】云朵不足({total_cloud}/{cost})")
            continue

        ok_dev, dev_id = get_or_fetch_device_id(account)
        if not ok_dev:
            fail_reasons.append(f"【{phone_mask}】{dev_id}")
            continue

        concurrency_data.append((phone_mask, prize_name, found_pid, cost, api, owner_map.get(account, ""), account, dev_id))

    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    notice = f"""=====移动云盘一键抢兑=====
⏰ 当前时间: {now_str}
📊 抢兑账号: {len(concurrency_data)}个
⏰ 抢兑时间: {target_time.strftime('%H:%M:%S')}
=================="""
    sender.reply(notice)
    if cleaned_count > 0:
        sender.reply(f"🧹 已自动清理 {cleaned_count} 个无效账号的抢兑数据")
    if fail_reasons:
        sender.reply("=====以下账号跳过=====\n" + "\n".join(fail_reasons) + "\n==================")

    if not concurrency_data:
        sender.reply("❌ 无可执行的账号，本次抢兑结束")
        return

    diff = (target_time - local_now()).total_seconds()
    if diff > 0:
        time.sleep(diff)
    if STOP_EXCHANGE:
        sender.reply("❌ 抢兑已被手动停止")
        return

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def real_exchange(phone_mask, pname, pid, costnum, api_obj, user_id, account_id, dev_id):
        # 新版兑换每次都需要滑块参数，重试太密会拖慢抢兑并增加风控风险。
        for attempt in range(1, 6):
            if STOP_EXCHANGE:
                return (phone_mask, pname, False, "已被手动停止", user_id, account_id)
            result = api_obj.do_exchange(pid, dev_id)
            if result.get('success'):
                return (phone_mask, pname, True, f"兑换成功(第{attempt}次)", user_id, account_id)
            if attempt < 5:
                time.sleep(0.5)
        msg = result.get('message', '兑换失败') if result else "未知错误"
        return (phone_mask, pname, False, msg, user_id, account_id)

    futures_map = {}
    with ThreadPoolExecutor(max_workers=bingfa) as exe:
        for (pm, pn, pd, ct, api_obj, uid, acid, did) in concurrency_data:
            fut = exe.submit(real_exchange, pm, pn, pd, ct, api_obj, uid, acid, did)
            futures_map[fut] = pm
        results = []
        for fut in as_completed(futures_map):
            results.append(fut.result())

    succ_count = sum(1 for r in results if r[2])
    fail_count = sum(1 for r in results if not r[2])
    fail_msgs = [f"📱 账号: {r[0]}\n🎁 奖品: {r[1]}\n📈 结果: {r[3]}" for r in results if not r[2]]
    detail_fail = "\n".join(fail_msgs) if fail_msgs else "无"

    final_msg = f"""=====移动云盘抢兑结果=====
📊 总抢兑数: {len(results)}
✅ 抢兑成功: {succ_count}
❌ 抢兑失败: {fail_count}
------------------
失败详情:
{detail_fail}
=================="""
    sender.reply(final_msg)

    for (phone_mask, pname, ok, reason, user_id, account_id) in results:
        if ok:
            try:
                middleware.bucketDel('dd_ydyp_prize', account_id)
            except Exception:
                pass
        if user_id:
            status_str = "成功" if ok else reason
            push_text = f"""=====移动云盘通知=====
📱 账号: {phone_mask}
🎁 奖品: {pname}
📈 抢兑结果: {status_str}
=================="""
            for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                try:
                    middleware.push(platform, '', user_id, '', push_text)
                except Exception:
                    pass
        if not ok and any(kw in str(reason) for kw in ["非移动用户不可领奖", "超过每月兑换限制", "重复兑奖"]):
            try:
                middleware.bucketDel('dd_ydyp_prize', account_id)
            except Exception:
                pass


def stop_exchange():
    global STOP_EXCHANGE
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return
    STOP_EXCHANGE = True
    sender.reply("✅ 已停止移动云盘抢兑")


def cron_check_expired():
    users = normalize_bucket_keys(middleware.bucketAllKeys('dd_ydyp_user'))
    today = str(datetime.now().date())

    try:
        ql = QingLongManager()
    except Exception:
        ql = None

    for user in users:
        accountlist = middleware.bucketGet('dd_ydyp_user', user)
        if not accountlist:
            continue
        accounts = parse_accounts(accountlist)

        for account in accounts:
            try:
                auth_time = middleware.bucketGet('dd_ydyp_auth', account)
                phone = mask_phone(account)

                if not auth_time or auth_time <= today:
                    # 已过期：删除面板变量，但保留bucket数据（等管理员手动清理）
                    if ql:
                        try:
                            env_id = ql.get_env_id(account)
                            if env_id:
                                ql.delete_env(env_id)
                        except Exception:
                            pass

                    # 推送过期通知
                    push_msg = f"=====移动云盘通知=====\n📱 账号: {phone}\n❌ 授权已过期\n💡 请及时续费授权\n=================="
                    for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                        try:
                            middleware.push(platform, '', user, '', push_msg)
                        except:
                            pass
                else:
                    # 已授权：自动续期Token
                    refreshed, _ = _try_refresh_account(account)
                    if refreshed and ql:
                        try:
                            token = middleware.bucketGet('dd_ydyp_token', account)
                            if token:
                                ql.add_or_update_env(account, token)
                        except Exception:
                            pass

                    try:
                        expire_date = datetime.strptime(auth_time, '%Y-%m-%d').date()
                        days_left = (expire_date - datetime.now().date()).days
                        if days_left <= 3:
                            push_msg = f"=====移动云盘通知=====\n📱 账号: {phone}\n⚠️ 授权即将到期\n📅 到期时间: {auth_time}\n⏳ 剩余天数: {days_left}天\n💡 请及时续费授权\n=================="
                            for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                                try:
                                    middleware.push(platform, '', user, '', push_msg)
                                except:
                                    pass
                    except:
                        pass
            except:
                continue


def main():
    manager = YdypManager()
    message = sender.getMessage()
    imtype = sender.getImtype()

    if '一键抢兑' in message:
        handle_yijian_qiangdui()
    elif '停止抢兑' in message:
        stop_exchange()
    elif '登录' in message or '登陆' in message:
        manager.login_account()
    elif '兑换' in message:
        exchange_entry_point()
    elif '管理' in message:
        if uservalue:
            manager.manage_accounts()
        else:
            sender.reply("=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 移动云盘登录 绑定账号\n==================")
    elif '查询' in message:
        if uservalue:
            manager.query_accounts()
        else:
            sender.reply("=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 移动云盘登录 绑定账号\n==================")
    elif '教程' in message:
        show_tutorial()
    elif '后台' in message:
        admin_backend()
    elif '同步' in message:
        sync_users()
    elif imtype == 'fake':
        cron_check_expired()
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
