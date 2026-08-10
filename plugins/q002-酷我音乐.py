# [pin:true]
# [author: yueiqiu4523]
# [title: q002-酷我音乐]
# [language: python]
# [class: 工具类]
# [service: 3116835832] 售后联系方式
# [disable:true] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^^酷我登录$|^酷我登陆$|^登陆酷我$|^登录酷我$|^酷我查询$|^查询酷我$|^酷我管理$|^管理酷我$|^酷我清理$|^酷我授权$]
# [cron: ] 无自动任务
# [priority: 55] 优先级，数字越大表示优先级越高
# [platform: all] 适用的平台
# [open_source: false]是否开源
# [icon: https://www.kuwo.cn/favicon.ico]图标链接
# [version: 1.1.0]版本号
# [public:true] 是否发布？
# [price: 1] 上架价格
# [description: 酷我插件<br>本插件全程用国产ai豆包完成，ai练习内容仅限参考，请仔细甄别<br>1.支持查询金币功能<br>2.手机号+密码即可上传到青龙/呆呆面板]

# [param: {"required":true,"key":"JQB.kw.zsm","bool":false,"placeholder":"收款码地址","name":"收款码地址","desc":"赞赏码或收款码地址"}]
# [param: {"required":false,"key":"JQB.kw.panel_config","bool":false,"placeholder":"http://面板地址丨AppKey丨AppSecret","name":"面板配置","desc":"支持青龙/呆呆面板格式：Host丨AppKey丨AppSecret 使用中文竖线丨分隔"}]
# [param: {"required":true,"key":"JQB.kw.var_name","bool":false,"placeholder":"kwyy","name":"环境变量名","desc":"面板内的环境变量名，如 kwyy"}]
# [param: {"required":true,"key":"JQB.kw.price","bool":false,"placeholder":"1","name":"上车价格","desc":"上车价格(单位:元)/30天"}]
# [param: {"required":true,"key":"JQB.kw.coin","bool":false,"placeholder":"0","name":"积分开通","desc":"授权一个月的积分"}]
# [param: {"required":true,"key":"JQB.kw.coin_bucket","bool":false,"placeholder":"dd_sign_points","name":"积分数据桶","desc":""}]
# [param: {"required":false,"key":"JQB.kw.proxy_pool","bool":false,"placeholder":"http://代理池API","name":"代理池地址","desc":""}]

import re
import base64
import random
import string
import uuid
from urllib.parse import quote
import time
import requests
import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib3
from datetime import datetime, timedelta
import json
import traceback
import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List

import middleware

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ================= 酷我音乐常量与配置 =================
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
IS_PROXY = False
PROXY_API = middleware.bucketGet('JQB.kw', 'proxy_pool') or "http://代理池API"
proxy = None

# 加密相关静态数组（从原酷我脚本复制）
static_c = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536, 131072, 262144, 524288, 1048576, 2097152, 4194304, 8388608, 16777216, 33554432, 67108864, 134217728, 268435456, 536870912, 1073741824, 2147483648, 4294967296, 8589934592, 17179869184, 34359738368, 68719476736, 137438953472, 274877906944, 549755813888, 1099511627776, 2199023255552, 4398046511104, 8796093022208, 17592186044416, 35184372088832, 70368744177664, 140737488355328, 281474976710656, 562949953421312, 1125899906842624, 2251799813685248, 4503599627370496, 9007199254740992, 18014398509481984, 36028797018963968, 72057594037927936, 144115188075855872, 288230376151711744, 576460752303423488, 1152921504606846976, 2305843009213693952, 4611686018427387904, -9223372036854775808]
static_i = [56, 48, 40, 32, 24, 16, 8, 0, 57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 60, 52, 44, 36, 28, 20, 12, 4, 27, 19, 11, 3]
static_e = [31, 0, 1, 2, 3, 4, -1, -1, 3, 4, 5, 6, 7, 8, -1, -1, 7, 8, 9, 10, 11, 12, -1, -1, 11, 12, 13, 14, 15, 16, -1, -1, 15, 16, 17, 18, 19, 20, -1, -1, 19, 20, 21, 22, 23, 24, -1, -1, 23, 24, 25, 26, 27, 28, -1, -1, 27, 28, 29, 30, 31, 30, -1, -1]
static_l = [0, 1048577, 3145731]
static_g = [15, 6, 19, 20, 28, 11, 27, 16, 0, 14, 22, 25, 4, 17, 30, 9, 1, 7, 23, 13, 31, 26, 2, 8, 18, 12, 29, 5, 21, 10, 3, 24]
static_f = [[14, 4, 3, 15, 2, 13, 5, 3, 13, 14, 6, 9, 11, 2, 0, 5, 4, 1, 10, 12, 15, 6, 9, 10, 1, 8, 12, 7, 8, 11, 7, 0, 0, 15, 10, 5, 14, 4, 9, 10, 7, 8, 12, 3, 13, 1, 3, 6, 15, 12, 6, 11, 2, 9, 5, 0, 4, 2, 11, 14, 1, 7, 8, 13], [15, 0, 9, 5, 6, 10, 12, 9, 8, 7, 2, 12, 3, 13, 5, 2, 1, 14, 7, 8, 11, 4, 0, 3, 14, 11, 13, 6, 4, 1, 10, 15, 3, 13, 12, 11, 15, 3, 6, 0, 4, 10, 1, 7, 8, 4, 11, 14, 13, 8, 0, 6, 2, 15, 9, 5, 7, 1, 10, 12, 14, 2, 5, 9], [10, 13, 1, 11, 6, 8, 11, 5, 9, 4, 12, 2, 15, 3, 2, 14, 0, 6, 13, 1, 3, 15, 4, 10, 14, 9, 7, 12, 5, 0, 8, 7, 13, 1, 2, 4, 3, 6, 12, 11, 0, 13, 5, 14, 6, 8, 15, 2, 7, 10, 8, 15, 4, 9, 11, 5, 9, 0, 14, 3, 10, 7, 1, 12], [7, 10, 1, 15, 0, 12, 11, 5, 14, 9, 8, 3, 9, 7, 4, 8, 13, 6, 2, 1, 6, 11, 12, 2, 3, 0, 5, 14, 10, 13, 15, 4, 13, 3, 4, 9, 6, 10, 1, 12, 11, 0, 2, 5, 0, 13, 14, 2, 8, 15, 7, 4, 15, 1, 10, 7, 5, 6, 12, 11, 3, 8, 9, 14], [2, 4, 8, 15, 7, 10, 13, 6, 4, 1, 3, 12, 11, 7, 14, 0, 12, 2, 5, 9, 10, 13, 0, 3, 1, 11, 15, 5, 6, 8, 9, 14, 14, 11, 5, 6, 4, 1, 3, 10, 2, 12, 15, 0, 13, 2, 8, 5, 11, 8, 0, 15, 7, 14, 9, 4, 12, 7, 10, 9, 1, 13, 6, 3], [12, 9, 0, 7, 9, 2, 14, 1, 10, 15, 3, 4, 6, 12, 5, 11, 1, 14, 13, 0, 2, 8, 7, 13, 15, 5, 4, 10, 8, 3, 11, 6, 10, 4, 6, 11, 7, 9, 0, 6, 4, 2, 13, 1, 9, 15, 3, 8, 15, 3, 1, 14, 12, 5, 11, 0, 2, 12, 14, 7, 5, 10, 8, 13], [4, 1, 3, 10, 15, 12, 5, 0, 2, 11, 9, 6, 8, 7, 6, 9, 11, 4, 12, 15, 0, 3, 10, 5, 14, 13, 7, 8, 13, 14, 1, 2, 13, 6, 14, 9, 4, 1, 2, 14, 11, 13, 5, 0, 1, 10, 8, 3, 0, 11, 3, 5, 9, 4, 15, 2, 7, 8, 12, 15, 10, 7, 6, 12], [13, 7, 10, 0, 6, 9, 5, 15, 8, 4, 3, 10, 11, 14, 12, 5, 2, 11, 9, 6, 15, 12, 0, 3, 4, 1, 14, 13, 1, 2, 7, 8, 1, 2, 12, 15, 10, 4, 0, 3, 13, 14, 6, 9, 7, 8, 9, 6, 15, 1, 5, 12, 3, 10, 14, 5, 8, 7, 11, 0, 4, 13, 2, 11]]
static_h = [39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61, 29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25, 32, 0, 40, 8, 48, 16, 56, 24]
static_d = [57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7, 56, 48, 40, 32, 24, 16, 8, 0, 58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6]
static_k = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
static_j = [13, 16, 10, 23, 0, 4, -1, -1, 2, 27, 14, 5, 20, 9, -1, -1, 22, 18, 11, 3, 25, 7, -1, -1, 15, 6, 26, 19, 12, 1, -1, -1, 40, 51, 30, 36, 46, 54, -1, -1, 29, 39, 50, 44, 32, 47, -1, -1, 43, 48, 38, 55, 33, 52, -1, -1, 45, 41, 49, 35, 28, 31, -1, -1]

# ================= 酷我加密函数 =================
def func_a1(iArr, i2, j2):
    j3 = 0
    for i3 in range(i2):
        if iArr[i3] >= 0:
            jArr = static_c
            if (jArr[iArr[i3]] & j2) != 0:
                j3 |= jArr[i3]
    return j3

def func_a2(j2, jArr, i2):
    a2 = func_a1(static_i, 56, j2)
    for i3 in range(16):
        jArr2 = static_l
        iArr = static_k
        a2 = ((a2 & ~jArr2[iArr[i3]]) >> iArr[i3]) | ((jArr2[iArr[i3]] & a2) << (28 - iArr[i3]))
        jArr[i3] = func_a1(static_j, 64, a2)
    if i2 == 1:
        for i4 in range(8):
            j3 = jArr[i4]
            i5 = 15 - i4
            jArr[i4] = jArr[i5]
            jArr[i5] = j3

def func_a3(jArr, j2):
    p = [0] * 2
    q = [0] * 8
    m = func_a1(static_d, 64, j2)
    iArr = p
    j3 = m
    iArr[0] = int(j3 & 4294967295)
    iArr[1] = int((j3 & -4294967296) >> 32)
    for i2 in range(16):
        o = iArr[1]
        o = func_a1(static_e, 64, o)
        o ^= jArr[i2]
        for i3 in range(8):
            q[i3] = int((o >> (i3 * 8)) & 255)
        r = 0
        i4 = 7
        while True:
            t = i4
            i5 = t
            if i5 >= 0:
                i6 = r
                i6 <<= 4
                if i6 > 2147483647:
                    i6 = -4294967296 + i6
                i6 |= static_f[i5][q[i5]]
                r = i6
                i4 = i5 - 1
            else:
                break
        o = r
        o = func_a1(static_g, 32, o)
        iArr2 = p
        n = iArr2[0]
        iArr2[0] = iArr2[1]
        xor_val = n ^ o
        if -2147483648 < xor_val < 2147483647:
            iArr2[1] = int(xor_val)
            continue
        if xor_val >= 2147483647:
            iArr2[1] = xor_val - 4294967296
        else:
            iArr2[1] = xor_val + 4294967296
    iArr3 = p
    s = iArr3[0]
    iArr3[0] = iArr3[1]
    iArr3[1] = s
    m = ((iArr3[1] << 32) & -4294967296) | (4294967295 & iArr3[0])
    m = func_a1(static_h, 64, m)
    return m

def generate_q(bArr, bArr2):
    length = len(bArr)
    jArr = [0] * 16
    j2 = 0
    j3 = 0
    for i3 in range(8):
        j3 |= bArr2[i3] << (i3 * 8)
    func_a2(j3, jArr, 0)
    i4 = length // 8
    jArr2 = [0] * i4
    for i5 in range(i4):
        for i6 in range(8):
            jArr2[i5] = jArr2[i5] | ((bArr[i5 * 8 + i6] & 255) << (i6 * 8))
    jArr3 = [0] * (((i4 + 1) * 8 + 1) // 8)
    for i7 in range(i4):
        jArr3[i7] = func_a3(jArr, jArr2[i7])
    i8 = length % 8
    i9 = i4 * 8
    i10 = length - i9
    r12 = [None] * i10
    r12[0:i10] = bArr[i9:i9 + i10]
    for i11 in range(i8):
        j2 |= (r12[i11] & 255) << (i11 * 8)
    jArr3[i4] = func_a3(jArr, j2)
    bArr3 = [None] * (len(jArr3) * 8)
    i12 = 0
    i13 = 0
    while i12 < len(jArr3):
        i14 = i13
        for i15 in range(8):
            bArr3[i14] = 255 & (jArr3[i12] >> (i15 * 8))
            i14 += 1
        i12 += 1
        i13 = i14
    return base64.b64encode(bytearray(bArr3)).decode()

def create_sx():
    timestamp = int(time.time() * 1000)
    combined_string = str(timestamp) + '12345678'
    result = combined_string[:8]
    return result

def encrypt_devid(dev_id):
    padded_id = dev_id.ljust(16, '0')[:16]
    return base64.b64encode(padded_id.encode()).decode()

def get_q(username, password):
    dev_id = ''.join([random.choice(string.digits) for _ in range(10)])
    dev_name = '安卓设备'
    devType = 'arr'
    data = f"username={quote(username)}&password={quote(base64.b64encode(password.encode()).decode())}&dev_id={dev_id}&user={str(uuid.uuid4()).replace('-', '')}&dev_name={quote(dev_name)}&urlencode=0&src=kwplayer_ar11.1.4.1_40.apk&devResolution=720*1080&&from=android&devType={devType}&sx={create_sx()}&version=11.1.4.1"
    q_value = generate_q(data.encode('UTF-8'), 'kwks&@69'.encode('UTF-8'))
    encrypted_dev_id = encrypt_devid(dev_id)
    return q_value, encrypted_dev_id

def encrypt_phone(phone):
    """加密手机号用于请求参数"""
    key = b'ysiVkLJHHnvMWCHq'
    iv = b'ichYooX+Mb1gRetP'
    if isinstance(phone, str):
        phone = phone.encode('utf-8')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_plaintext = pad(phone, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    ciphertext_base64 = base64.b64encode(ciphertext).decode('utf-8')
    return ciphertext_base64

def decrypt_phone(encrypted_phone):
    """解密手机号（存储用）"""
    key = b'ysiVkLJHHnvMWCHq'
    iv = b'ichYooX+Mb1gRetP'
    aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
    encrypted_data = base64.b64decode(encrypted_phone)
    decrypted_data = unpad(aes.decrypt(encrypted_data), AES.block_size, style='pkcs7')
    return decrypted_data.decode('UTF-8')

# ================= 酷我核心类 =================
class KWBot:
    def __init__(self, name: str, phone: str, password: str):
        self.name = name          # 显示名称（手机号掩码）
        self.phone = phone
        self.password = password
        self.logs: List[str] = []
        self.login_uid: Optional[str] = None
        self.login_sid: Optional[str] = None
        self.app_uid: Optional[str] = None
        self.encrypted_dev_id: Optional[str] = None

    def log(self, message: str):
        formatted_msg = f"[{self.name}] {message}"
        print(formatted_msg)
        self.logs.append(formatted_msg)

    def login(self) -> bool:
        """登录并获取凭证"""
        try:
            q, encrypted_dev_id = get_q(self.phone, self.password)
            url = 'http://ar.i.kuwo.cn/US_NEW/kuwo/login_kw'
            headers = {
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; MI 8 MIUI/V12.5.2.0.QEACNXM)',
                'Accept': '*/*',
                'Host': 'ar.i.kuwo.cn',
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'gzip',
            }
            params = {'f': 'ar', 'q': q}
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT, verify=False)
            set_cookie = response.headers.get('Set-Cookie', '')
            username_match = re.search(r'uname3=([^;]+)', set_cookie)
            sid_match = re.search(r'websid=([^;]+)', set_cookie)
            uid_match = re.search(r'userid=([^;]+)', set_cookie)
            account_match = re.search(r't3kwid=([^;]+)', set_cookie)
            if all([username_match, sid_match, uid_match, account_match]):
                self.login_uid = uid_match.group(1)
                self.login_sid = sid_match.group(1)
                self.app_uid = account_match.group(1)
                self.encrypted_dev_id = encrypted_dev_id
                return True
            self.log("登录失败: Cookie解析失败")
            return False
        except Exception as e:
            self.log(f"登录异常: {str(e)}")
            return False

    def query_user_asset(self) -> Optional[int]:
        """查询剩余金币，失败返回None"""
        if not self.login_uid:
            if not self.login():
                return None
        params = {'loginUid': self.login_uid, 'loginSid': self.login_sid, 'appUid': self.app_uid}
        try:
            url = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/earningUserSignList'
            headers = {
                'Host': 'integralapi.kuwo.cn',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36/ kuwopage',
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'cn.kuwo.player',
                'Referer': 'https://h5app.kuwo.cn/',
            }
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT, verify=False)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})
                    if isinstance(data, dict):
                        return data.get('remainScore', 0)
            return None
        except Exception as e:
            self.log(f"查询资产失败: {str(e)}")
            return None

    def query_sign_status(self) -> Optional[bool]:
        """查询今日是否已签到，返回True已签到，False未签到，None失败"""
        if not self.login_uid:
            if not self.login():
                return None
        params = {'loginUid': self.login_uid, 'loginSid': self.login_sid, 'appUid': self.app_uid}
        try:
            url = 'https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/newUserSignList'
            headers = {
                'Host': 'integralapi.kuwo.cn',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 4a Build/TQ3A.230805.001.S2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/134.0.6998.135 Mobile Safari/537.36/ kuwopage',
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'cn.kuwo.player',
                'Referer': 'https://h5app.kuwo.cn/',
            }
            response = requests.get(url, headers=headers, params=params, timeout=REQUEST_TIMEOUT, verify=False)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    data = result.get('data', {})
                    if isinstance(data, dict):
                        is_sign = data.get('isSign')
                        if is_sign in [True, 1, '1', 'true']:
                            return True
                        else:
                            return False
            return None
        except Exception as e:
            self.log(f"查询签到状态失败: {str(e)}")
            return None

    def get_full_info(self) -> Dict[str, Any]:
        """获取完整信息（金币、签到状态）"""
        if not self.login():
            return {"success": False, "msg": "登录失败，请检查手机号和密码"}

        score = self.query_user_asset()
        sign_status = self.query_sign_status()
        if score is None or sign_status is None:
            return {"success": False, "msg": "获取数据失败，请检查账号状态"}

        return {
            "success": True,
            "phone": self.phone,
            "score": score,
            "sign_status": "✅ 今日已签到" if sign_status else "❌ 今日未签到"
        }

# ================= 面板配置获取（与天机观相同） =================
def get_panel_config():
    config_str = middleware.bucketGet('JQB.kw', 'panel_config')
    if config_str and '丨' in config_str:
        parts = config_str.split('丨', 2)
        if len(parts) == 3:
            host = parts[0].strip()
            app_key = parts[1].strip()
            app_secret = parts[2].strip()
            if host and app_key and app_secret:
                return host, app_key, app_secret
    host = middleware.bucketGet('JQB.kw', 'ql_host')
    client_id = middleware.bucketGet('JQB.kw', 'ql_client_id')
    client_secret = middleware.bucketGet('JQB.kw', 'ql_client_secret')
    if host and client_id and client_secret:
        print("警告: 使用旧的青龙配置，建议迁移到新的 panel_config 格式(Host丨AppKey丨AppSecret)")
        return host, client_id, client_secret
    return None, None, None

def get_qinglong_token(host, app_key, app_secret):
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}open/auth/token?client_id={app_key}&client_secret={app_secret}"
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('token')
    except Exception as e:
        print(f"获取青龙token失败: {str(e)}")
    return None

def add_to_qinglong(host, token, env_data):
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}open/envs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code != 200:
            return None
        envs = response.json().get('data', [])
        exists_id = None
        match = re.search(r'账号([^丨]+)丨用户:([^丨]+)', env_data['remarks'])
        account_phone_mask = match.group(1) if match else None
        user_id = match.group(2) if match else None

        for env in envs:
            if env.get('name') != env_data['name']:
                continue
            env_remarks = env.get('remarks', '')
            if account_phone_mask and user_id:
                if account_phone_mask in env_remarks and user_id in env_remarks:
                    exists_id = env.get('id')
                    break
            else:
                if env_data.get('remarks') in env_remarks:
                    exists_id = env.get('id')
                    break

        if exists_id:
            update_url = f"{host}open/envs"
            env_data['id'] = exists_id
            response = requests.put(update_url, headers=headers, json=env_data, verify=False)
            if 200 <= response.status_code < 300:
                return exists_id
        else:
            response = requests.post(url, headers=headers, json=[env_data], verify=False)
            if 200 <= response.status_code < 300:
                resp_data = response.json()
                if resp_data.get('data') and len(resp_data['data']) > 0:
                    return resp_data['data'][0]['id']
    except Exception as e:
        print(f"青龙添加环境变量失败: {str(e)}")
    return None

def delete_qinglong_env(host, token, env_id, remarks=None):
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}open/envs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = [int(env_id)]
        response = requests.delete(url, headers=headers, json=data, verify=False)
        if response.status_code == 404:
            print(f"青龙面板变量 {env_id} 不存在，视为删除成功")
            return True
        success = 200 <= response.status_code < 300
        if not success:
            print(f"删除青龙面板变量失败，状态码: {response.status_code}, 响应: {response.text}")
        return success
    except Exception as e:
        print(f"删除青龙环境变量失败: {str(e)}")
        return False

def get_daidai_token(host, app_key, app_secret):
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}api/open-api/token"
        headers = {"Content-Type": "application/json"}
        payload = {"app_key": app_key, "app_secret": app_secret}
        response = requests.post(url, json=payload, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("access_token")
    except Exception as e:
        print(f"获取呆呆token失败: {str(e)}")
    return None

def _daidai_request(method, host, token, url_suffix, **kwargs):
    if not host.endswith('/'):
        host += '/'
    full_url = host + url_suffix.lstrip('/')
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f"Bearer {token}"
    headers['Content-Type'] = 'application/json'
    resp = requests.request(method, full_url, headers=headers, timeout=10, verify=False, **kwargs)
    if resp.status_code == 401:
        new_token = get_daidai_token(host, *get_panel_config()[1:])
        if new_token:
            headers['Authorization'] = f"Bearer {new_token}"
            resp = requests.request(method, full_url, headers=headers, timeout=10, verify=False, **kwargs)
    return resp

def add_to_daidai(host, token, env_data):
    try:
        search_url = f"api/envs?keyword={env_data['name']}&page_size=100"
        search_resp = _daidai_request('GET', host, token, search_url)
        if search_resp.status_code != 200:
            return None
        search_result = search_resp.json()
        envs = search_result if isinstance(search_result, list) else search_result.get('data', [])

        match = re.search(r'账号([^丨]+)丨用户:([^丨]+)', env_data['remarks'])
        account_phone_mask = match.group(1) if match else None
        user_id = match.group(2) if match else None

        exists_id = None
        for env in envs:
            if env.get('name') != env_data['name']:
                continue
            env_remarks = env.get('remarks', '')
            if account_phone_mask and user_id:
                if account_phone_mask in env_remarks and user_id in env_remarks:
                    exists_id = env.get('id')
                    break
            else:
                if env_data.get('remarks') in env_remarks:
                    exists_id = env.get('id')
                    break

        data = env_data.copy()
        data['enabled'] = True
        data['group'] = "酷我音乐"

        if exists_id:
            update_url = f"api/envs/{exists_id}"
            update_resp = _daidai_request('PUT', host, token, update_url, json=data)
            if 200 <= update_resp.status_code < 300:
                return exists_id
        else:
            add_url = "api/envs"
            add_resp = _daidai_request('POST', host, token, add_url, json=data)
            if 200 <= add_resp.status_code < 300:
                resp_data = add_resp.json()
                return resp_data.get('data', {}).get('id')
    except Exception as e:
        print(f"呆呆添加环境变量失败: {str(e)}")
    return None

def delete_daidai_env(host, token, env_id, remarks=None):
    try:
        del_url = f"api/envs/{env_id}"
        del_resp = _daidai_request('DELETE', host, token, del_url)
        if del_resp.status_code == 404:
            print(f"呆呆面板变量 {env_id} 不存在，视为删除成功")
            return True
        if 200 <= del_resp.status_code < 300:
            print(f"删除呆呆面板变量 {env_id} 成功")
            return True

        if remarks and del_resp.status_code != 404:
            print(f"删除呆呆变量ID {env_id} 失败（状态码: {del_resp.status_code}），尝试通过备注搜索删除: {remarks}")
            search_url = f"api/envs?keyword={remarks}&page_size=100"
            search_resp = _daidai_request('GET', host, token, search_url)
            if search_resp.status_code == 200:
                search_result = search_resp.json()
                envs = search_result if isinstance(search_result, list) else search_result.get('data', [])
                for env in envs:
                    env_remarks = env.get('remarks', '')
                    if remarks in env_remarks:
                        del_url2 = f"api/envs/{env['id']}"
                        del_resp2 = _daidai_request('DELETE', host, token, del_url2)
                        if 200 <= del_resp2.status_code < 300:
                            print(f"通过备注搜索删除成功，ID: {env['id']}")
                            return True
                        else:
                            print(f"通过备注搜索删除失败，状态码: {del_resp2.status_code}, 响应: {del_resp2.text}")
            else:
                print(f"搜索环境变量失败，状态码: {search_resp.status_code}, 响应: {search_resp.text}")

        print(f"删除呆呆面板变量失败，状态码: {del_resp.status_code}, 响应: {del_resp.text}")
        return False
    except Exception as e:
        print(f"删除呆呆环境变量异常: {str(e)}")
        return False

def add_to_panel(env_data):
    host, app_key, app_secret = get_panel_config()
    if not host:
        return None
    ql_token = get_qinglong_token(host, app_key, app_secret)
    if ql_token:
        env_id = add_to_qinglong(host, ql_token, env_data)
        if env_id:
            return f"ql:{env_id}"
    dd_token = get_daidai_token(host, app_key, app_secret)
    if dd_token:
        env_id = add_to_daidai(host, dd_token, env_data)
        if env_id:
            return f"dd:{env_id}"
    return None

def delete_from_panel(env_id_with_prefix, remarks=None):
    if not env_id_with_prefix:
        return False
    parts = env_id_with_prefix.split(':', 1)
    if len(parts) != 2:
        return False
    panel_type, env_id = parts
    host, app_key, app_secret = get_panel_config()
    if not host:
        return False
    if panel_type == 'ql':
        token = get_qinglong_token(host, app_key, app_secret)
        if token:
            return delete_qinglong_env(host, token, env_id, remarks)
    elif panel_type == 'dd':
        token = get_daidai_token(host, app_key, app_secret)
        if token:
            return delete_daidai_env(host, token, env_id, remarks)
    return False

# ================= 辅助函数 =================
def mask_phone(phone: str) -> str:
    """手机号掩码显示"""
    if not phone or len(phone) != 11:
        return phone
    return phone[:3] + '****' + phone[7:]

def validate_account(phone: str, password: str) -> bool:
    """验证账号有效性"""
    bot = KWBot(name="测试", phone=phone, password=password)
    return bot.login()

# ================= 授权核心函数（支持跳过支付） =================
def authorize_single_account(sender, account_key: str, months: int, skip_payment: bool = False, userid_for_remark: str = None) -> bool:
    """
    对单个账号进行授权，延长授权时间，更新面板环境变量
    返回是否成功
    """
    try:
        today_date = datetime.now().date()
        today_time = str(today_date)
        auth = middleware.bucketGet('JQB.kw.auth', account_key)
        if not auth or auth < today_time:
            auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
        else:
            auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')

        middleware.bucketSet('JQB.kw.auth', account_key, auth_time)

        account_data = middleware.bucketGet('JQB.kw.account', account_key)
        if not account_data:
            return False
        acc_info = json.loads(account_data)
        phone = acc_info.get('phone')
        password = acc_info.get('password')
        if not phone or not password:
            return False

        display_name = mask_phone(phone)
        # 备注中的用户ID优先使用传入的，否则从账号关联的用户中查找（可能需要额外逻辑，这里简单使用调用者的userid）
        if userid_for_remark is None:
            # 尝试查找该账号所属的用户ID
            all_users = middleware.bucketAllKeys('JQB.kw.user')
            for uid in all_users:
                accounts_list = eval(middleware.bucketGet('JQB.kw.user', uid) or '[]')
                if account_key in accounts_list:
                    userid_for_remark = uid
                    break
        if userid_for_remark is None:
            userid_for_remark = "unknown"

        remarks = f"酷我账号{display_name}丨用户:{userid_for_remark}丨授权时间:{auth_time}"
        var_name = middleware.bucketGet('JQB.kw', 'var_name') or 'kwyy'
        env_data = {
            "name": var_name,
            "value": f"{phone}#{password}",
            "remarks": remarks
        }
        env_id_with_prefix = add_to_panel(env_data)
        if env_id_with_prefix:
            middleware.bucketSet('JQB.kw.env_id', account_key, env_id_with_prefix)
        return True
    except Exception as e:
        print(f"授权账号 {account_key} 失败: {str(e)}")
        return False

def authorize_accounts(sender, accounts, skip_payment=False):
    """
    对账号列表进行授权，skip_payment=True时跳过支付/积分扣除（管理员模式）
    """
    if not accounts:
        return sender.reply('❌ 无账号可授权')

    account_list = "\n".join([f"  - {mask_phone(acc)}" for acc in accounts])
    sender.reply(f"""=====即将授权以下账号=====
{account_list}
------------------""")

    coin_bucket = middleware.bucketGet('JQB.kw', 'coin_bucket') or 'dd_sign_points'
    coin_price = int(middleware.bucketGet('JQB.kw', 'coin') or '0')
    price = Decimal(middleware.bucketGet('JQB.kw', 'price') or '1')

    if skip_payment:
        # 管理员授权，直接输入月数
        sender.reply("请输入授权月数:")
        months = sender.input(30000, 1, False)
        if not months:
            return sender.reply('输入超时')
        try:
            months = int(months)
            if months <= 0:
                return sender.reply('月数必须大于0')
        except:
            return sender.reply('月数格式错误')
        success_count = 0
        for acc in accounts:
            if authorize_single_account(sender, acc, months, skip_payment=True):
                success_count += 1
        sender.reply(f'✅ 管理员授权完成，成功 {success_count}/{len(accounts)} 个账号，授权 {months} 个月')
        return

    # 普通用户授权流程
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

        if choice == '1':
            amount = price * months * len(accounts)
            if process_payment(amount, months * 30, sender):
                success_count = 0
                for acc in accounts:
                    if authorize_single_account(sender, acc, months, skip_payment=False):
                        success_count += 1
                sender.reply(f'✅ 已授权 {success_count}/{len(accounts)} 个账号 {months} 个月')
        elif choice == '2':
            user_coin = Decimal(middleware.bucketGet(coin_bucket, sender.getUserID()) or '0')
            need_coin = coin_price * months * len(accounts)
            if user_coin < need_coin:
                return sender.reply(f'❌ 积分不足，需要{need_coin}，当前有{user_coin}')
            new_coin = user_coin - need_coin
            middleware.bucketSet(coin_bucket, sender.getUserID(), str(new_coin))
            success_count = 0
            for acc in accounts:
                if authorize_single_account(sender, acc, months, skip_payment=False):
                    success_count += 1
            sender.reply(f'✅ 已用 {need_coin} 积分授权 {success_count}/{len(accounts)} 个账号 {months} 个月，剩余积分: {new_coin}')
    except Exception as e:
        sender.reply(f'❌ 授权失败: {str(e)}')

# ================= 管理员授权菜单功能 =================
def admin_auth_menu(sender):
    """管理员授权主菜单"""
    if not sender.isAdmin():
        return sender.reply("❌ 需要管理员权限")
    menu = """=====管理员授权管理=====
[1] 一键授权所有用户（所有账号）
[2] 指定用户授权
[3] 更新所有青龙环境变量
------------------
请回复数字选择功能
回复"q"退出"""
    sender.reply(menu)
    choice = sender.input(30000, 1, False)
    if not choice or choice.lower() == 'q':
        return sender.reply('已退出')
    if choice == '1':
        auth_all_users(sender)
    elif choice == '2':
        auth_specified_user(sender)
    elif choice == '3':
        update_all_env_vars(sender)
    else:
        sender.reply('无效选择')

def auth_all_users(sender):
    """一键授权所有用户的所有账号"""
    # 获取所有用户的账号列表（去重，一个账号可能属于多个用户？理论上只属于一个，但以防万一）
    all_accounts = set()
    users = middleware.bucketAllKeys('JQB.kw.user')
    if not users:
        return sender.reply('❌ 没有任何用户绑定账号')
    for uid in users:
        accounts = eval(middleware.bucketGet('JQB.kw.user', uid) or '[]')
        all_accounts.update(accounts)
    if not all_accounts:
        return sender.reply('❌ 未找到任何账号')
    sender.reply(f"找到 {len(all_accounts)} 个账号，将进行批量授权")
    sender.reply("请输入授权月数:")
    months = sender.input(30000, 1, False)
    if not months:
        return sender.reply('输入超时')
    try:
        months = int(months)
        if months <= 0:
            return sender.reply('月数必须大于0')
    except:
        return sender.reply('月数格式错误')
    success = 0
    for acc in all_accounts:
        if authorize_single_account(sender, acc, months, skip_payment=True):
            success += 1
    sender.reply(f'✅ 批量授权完成，成功 {success}/{len(all_accounts)} 个账号，授权 {months} 个月')

def auth_specified_user(sender):
    """指定用户授权"""
    sender.reply("请输入要授权的用户ID（可从日志或查询中获取）:")
    userid = sender.input(30000, 1, False)
    if not userid:
        return sender.reply('输入超时')
    accounts_str = middleware.bucketGet('JQB.kw.user', userid)
    if not accounts_str:
        return sender.reply(f'❌ 用户 {userid} 没有绑定任何账号')
    accounts = eval(accounts_str)
    if not accounts:
        return sender.reply(f'❌ 用户 {userid} 账号列表为空')
    # 显示账号供选择
    menu = "=====该用户的账号列表=====\n"
    for idx, acc in enumerate(accounts, 1):
        menu += f"[{idx}] {mask_phone(acc)}\n"
    menu += "=======================\n请回复数字序号选择（多个用逗号分隔），输入all选择全部，q取消"
    sender.reply(menu)
    choice_str = sender.input(30000, 1, False)
    if not choice_str or choice_str.lower() == 'q':
        return sender.reply('已取消')
    if choice_str.lower() == 'all':
        selected = accounts
    else:
        try:
            indexes = [int(x.strip()) for x in choice_str.split(',')]
            selected = []
            for idx in indexes:
                if 1 <= idx <= len(accounts):
                    selected.append(accounts[idx-1])
                else:
                    sender.reply(f'无效序号 {idx}，已跳过')
        except:
            return sender.reply('输入格式错误')
    if not selected:
        return sender.reply('未选择任何账号')
    sender.reply(f"已选择 {len(selected)} 个账号")
    sender.reply("请输入授权月数:")
    months = sender.input(30000, 1, False)
    if not months:
        return sender.reply('输入超时')
    try:
        months = int(months)
        if months <= 0:
            return sender.reply('月数必须大于0')
    except:
        return sender.reply('月数格式错误')
    success = 0
    for acc in selected:
        if authorize_single_account(sender, acc, months, skip_payment=True, userid_for_remark=userid):
            success += 1
    sender.reply(f'✅ 授权完成，成功 {success}/{len(selected)} 个账号，授权 {months} 个月')

def update_all_env_vars(sender):
    """更新所有已授权账号的青龙环境变量"""
    sender.reply("正在收集所有已授权账号...")
    # 获取所有有授权记录的账号（从auth桶中获取所有key）
    # 注意：auth桶的key是手机号，需要获取所有key
    # middleware可能不支持直接获取桶所有key，我们通过遍历用户来收集
    all_accounts = set()
    users = middleware.bucketAllKeys('JQB.kw.user')
    for uid in users:
        accounts = eval(middleware.bucketGet('JQB.kw.user', uid) or '[]')
        all_accounts.update(accounts)
    if not all_accounts:
        return sender.reply('❌ 未找到任何账号')
    sender.reply(f"找到 {len(all_accounts)} 个账号，开始更新环境变量...")
    success = 0
    for acc in all_accounts:
        # 检查是否有授权记录且未过期
        auth = middleware.bucketGet('JQB.kw.auth', acc)
        if not auth:
            continue
        today = datetime.now().date()
        if auth < str(today):
            continue
        # 重新同步面板
        account_data = middleware.bucketGet('JQB.kw.account', acc)
        if not account_data:
            continue
        acc_info = json.loads(account_data)
        phone = acc_info.get('phone')
        password = acc_info.get('password')
        if not phone or not password:
            continue
        display_name = mask_phone(phone)
        # 查找所属用户ID
        userid_for_remark = None
        for uid in users:
            acc_list = eval(middleware.bucketGet('JQB.kw.user', uid) or '[]')
            if acc in acc_list:
                userid_for_remark = uid
                break
        if userid_for_remark is None:
            userid_for_remark = "unknown"
        remarks = f"酷我账号{display_name}丨用户:{userid_for_remark}丨授权时间:{auth}"
        var_name = middleware.bucketGet('JQB.kw', 'var_name') or 'kwyy'
        env_data = {
            "name": var_name,
            "value": f"{phone}#{password}",
            "remarks": remarks
        }
        env_id = add_to_panel(env_data)
        if env_id:
            middleware.bucketSet('JQB.kw.env_id', acc, env_id)
            success += 1
    sender.reply(f'✅ 环境变量更新完成，成功更新 {success} 个账号')

# ================= 原有业务功能（保持兼容） =================
def bind(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.kw.user', key=userid)

    sender.reply(
        """=====酷我音乐登录=====
📝 请输入手机号和密码，格式: 手机号#密码
支持批量，一个账号一行
示例：
    13800138000#mypassword
=====================
⭐ 输入q退出操作"""
    )

    input_text = sender.input(120000, 10, True).strip()
    if not input_text or input_text.lower() == 'q':
        sender.reply('已取消操作')
        return

    accounts = []  # 存储 phone
    success_count = 0
    fail_count = 0

    lines = input_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if '#' not in line:
            sender.reply(f"❌ 格式错误: {line}，应为 手机号#密码")
            fail_count += 1
            continue
        parts = line.split('#', 1)
        phone = parts[0].strip()
        password = parts[1].strip()
        if not phone or not password:
            sender.reply(f"❌ 手机号或密码为空: {line}")
            fail_count += 1
            continue

        valid = validate_account(phone, password)
        if not valid:
            sender.reply(f"❌ 账号无效: {mask_phone(phone)}")
            fail_count += 1
            continue

        account_key = phone
        try:
            account_data = {
                'phone': phone,
                'password': password
            }
            middleware.bucketSet('JQB.kw.account', account_key, json.dumps(account_data))

            if account_key not in accounts:
                accounts.append(account_key)
                success_count += 1
        except Exception as e:
            sender.reply(f"❌ 保存失败: {mask_phone(phone)} - {str(e)}")
            fail_count += 1

    if accounts:
        existing_accounts = eval(uservalue or '[]')
        for acc in accounts:
            if acc not in existing_accounts:
                existing_accounts.append(acc)
        middleware.bucketSet('JQB.kw.user', userid, str(existing_accounts))

    result_msg = f"""=====绑定结果=====
✅ 成功绑定: {success_count}个账号
❌ 失败绑定: {fail_count}个账号
------------------
发送"酷我查询"查看状态
发送"酷我管理"管理账号
====================="""
    sender.reply(result_msg)

def query(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.kw.user', key=userid)
    today_date = datetime.now().date()
    today_time = str(today_date)

    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply(
            """\n=====酷我账号查询=====
❌ 未找到任何账号
------------------
💡 发送"酷我登录"绑定账号
==================="""
        )
        return

    # 构建账号选择菜单
    if len(accounts) > 1:
        menu = """=====请选择查询账号=====
[0] 查询全部账号
"""
        for idx, acc in enumerate(accounts, 1):
            display = mask_phone(acc)
            menu += f"[{idx}] {display}\n"
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

    for account_key in target_accounts:
        try:
            auth = middleware.bucketGet('JQB.kw.auth', account_key)
            auth_status = f"⏰ 授权到期: {auth}" if auth and auth >= today_time else "❌ 未授权"

            account_data = middleware.bucketGet('JQB.kw.account', account_key)
            if not account_data:
                sender.reply(f'【{mask_phone(account_key)}】账号信息不存在')
                continue

            acc_info = json.loads(account_data)
            phone = acc_info.get('phone')
            password = acc_info.get('password')
            if not phone or not password:
                sender.reply(f'【{mask_phone(account_key)}】手机号或密码不存在')
                continue

            display_name = mask_phone(phone)
            bot = KWBot(name=display_name, phone=phone, password=password)
            info = bot.get_full_info()

            lines = []
            lines.append(f"=====账号详情=====")
            lines.append(f"🔑 账号: {display_name}")
            lines.append(auth_status)
            if info.get("success"):
                lines.append(f"💰 剩余金币：{info.get('score', 0)}")
                lines.append(f"📅 {info.get('sign_status')}")
            else:
                lines.append(f"❌ 查询失败: {info.get('msg')}")
            lines.append("===================")

            sender.reply("\n".join(lines))

        except Exception as e:
            sender.reply(f'【{mask_phone(account_key)}】查询出错: {str(e)}')

def manage_accounts(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.kw.user', key=userid)

    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply("""=====账号管理=====
❌ 未找到任何账号
------------------
💡 发送"酷我登录"绑定账号
===================""")
        return

    menu = """=====账号管理=====
[1] 授权所有账号
[2] 删除账号
[3] 选择账号授权
------------------
请回复数字选择操作"""
    sender.reply(menu)

    choice = sender.input(30000, 1, False)
    if not choice:
        return sender.reply('操作超时')

    if choice == '1':
        authorize_accounts(sender, accounts, skip_payment=False)
    elif choice == '2':
        delete_account(sender)
    elif choice == '3':
        select_accounts_authorize(sender, accounts)
    else:
        sender.reply('无效的选择')

def delete_account(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.kw.user', key=userid)

    accounts = eval(uservalue or '[]')
    if not accounts:
        return sender.reply('❌ 无账号可删除')

    if len(accounts) > 1:
        menu = "=====选择要删除的账号=====\n"
        for idx, acc in enumerate(accounts, 1):
            display = mask_phone(acc)
            menu += f"[{idx}] {display}\n"
        menu += "=======================\n⚠️ 回复数字序号(输入q退出)"
        sender.reply(menu)

        choice = sender.input(30000, 1, False)
        if not choice or choice.lower() == 'q':
            return sender.reply('已取消')

        try:
            index = int(choice) - 1
            if 0 <= index < len(accounts):
                account_key = accounts[index]
                display_name = mask_phone(account_key)

                confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
🔑 账号: {display_name}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
================="""
                sender.reply(confirm_msg)

                confirm = sender.input(30000, 1, False)
                if confirm.lower() != 'y':
                    return sender.reply('✅ 已取消删除操作')

                remarks_identifier = f"酷我账号{display_name}丨用户:{userid}"
                env_id_with_prefix = middleware.bucketGet('JQB.kw.env_id', account_key)
                if env_id_with_prefix:
                    delete_from_panel(env_id_with_prefix, remarks=remarks_identifier)

                middleware.bucketDel('JQB.kw.account', account_key)
                middleware.bucketDel('JQB.kw.auth', account_key)
                middleware.bucketDel('JQB.kw.env_id', account_key)

                accounts.pop(index)
                middleware.bucketSet('JQB.kw.user', userid, str(accounts))
                sender.reply(f'✅ 已删除账号: {display_name}')
            else:
                sender.reply('选择超出范围')
        except:
            sender.reply('输入错误')
    else:
        account_key = accounts[0]
        display_name = mask_phone(account_key)

        confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
🔑 账号: {display_name}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
================="""
        sender.reply(confirm_msg)

        confirm = sender.input(30000, 1, False)
        if confirm.lower() != 'y':
            return sender.reply('✅ 已取消删除操作')

        remarks_identifier = f"酷我账号{display_name}丨用户:{userid}"
        env_id_with_prefix = middleware.bucketGet('JQB.kw.env_id', account_key)
        if env_id_with_prefix:
            delete_from_panel(env_id_with_prefix, remarks=remarks_identifier)

        middleware.bucketDel('JQB.kw.account', account_key)
        middleware.bucketDel('JQB.kw.auth', account_key)
        middleware.bucketDel('JQB.kw.env_id', account_key)
        middleware.bucketSet('JQB.kw.user', userid, '[]')
        sender.reply(f'✅ 已删除账号: {display_name}')

def select_accounts_authorize(sender, accounts):
    if not accounts:
        return sender.reply('❌ 无账号可授权')

    menu = "=====选择要授权的账号=====\n"
    for idx, acc in enumerate(accounts, 1):
        display = mask_phone(acc)
        menu += f"[{idx}] {display}\n"
    menu += "=======================\n⚠️ 回复数字序号(多个用逗号分隔, 输入q退出)"
    sender.reply(menu)

    choice_str = sender.input(30000, 1, False)
    if not choice_str or choice_str.lower() == 'q':
        return sender.reply('已取消授权操作')

    try:
        selected_indexes = [int(idx.strip()) for idx in choice_str.split(',')]
        selected_accounts = []

        for idx in selected_indexes:
            if 1 <= idx <= len(accounts):
                selected_accounts.append(accounts[idx-1])
            else:
                sender.reply(f"❌ 无效的序号: {idx}，已跳过")

        if not selected_accounts:
            return sender.reply('❌ 未选择有效账号')

        account_list = "\n".join([f"  - {mask_phone(acc)}" for acc in selected_accounts])
        sender.reply(f"""=====已选择以下账号=====
{account_list}
------------------""")

        authorize_accounts(sender, selected_accounts, skip_payment=False)

    except Exception as e:
        sender.reply(f'❌ 选择失败: {str(e)}')

def process_payment(amount, days, sender):
    zsm = middleware.bucketGet('JQB.kw', 'zsm')
    if not zsm:
        sender.reply("❌ 未配置收款码")
        return False

    if sender.atWaitPay():
        sender.reply('当前有人正在支付,请稍后再试！')
        return False

    pay_msg = f"""=====微信扫码支付====
🎫 商品: 酷我音乐授权
📅 时长: {days}天
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
================="""
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
    sender.reply("""=====酷我音乐教程=====
🌟 核心功能指令:
1. 酷我登录 - 绑定手机号#密码
2. 酷我查询 - 查看剩余金币和签到状态
3. 酷我管理 - 账号管理功能（授权、删除）
4. 酷我授权 - 管理员批量授权（仅管理员）

⚙️ 授权说明:
1. 支持微信支付和积分支付
2. 授权后解锁全部功能
3. 自动同步到青龙/呆呆面板

⚠️ 注意事项:
1. 密码明文存储，请妥善保管环境
2. 本插件不自动执行任何任务，仅提供查询
=====================""")

def clean_expired(sender):
    if not sender.isAdmin():
        return sender.reply("❌ 需要管理员权限")

    today_date = datetime.now().date()
    today_time = str(today_date)

    users = middleware.bucketAllKeys('JQB.kw.user')
    cleaned = 0

    for user in users:
        accounts = eval(middleware.bucketGet('JQB.kw.user', user) or [])
        valid = []

        for account_key in accounts:
            auth = middleware.bucketGet('JQB.kw.auth', account_key)
            if not auth or auth < today_time:
                display_name = mask_phone(account_key)
                remarks_identifier = f"酷我账号{display_name}丨用户:{user}"
                env_id_with_prefix = middleware.bucketGet('JQB.kw.env_id', account_key)
                if env_id_with_prefix:
                    delete_from_panel(env_id_with_prefix, remarks=remarks_identifier)

                middleware.bucketDel('JQB.kw.account', account_key)
                middleware.bucketDel('JQB.kw.auth', account_key)
                middleware.bucketDel('JQB.kw.env_id', account_key)
                cleaned += 1
            else:
                valid.append(account_key)

        if valid:
            middleware.bucketSet('JQB.kw.user', user, str(valid))
        else:
            middleware.bucketDel('JQB.kw.user', user)

    sender.reply(f"✅ 已清理 {cleaned} 个过期账号")

def main():
    try:
        senderID = middleware.getSenderID()
        sender = middleware.Sender(senderID)
        message = sender.getMessage().strip().lower()

        if '登录' in message:
            bind(sender)
        elif '查询' in message:
            query(sender)
        elif '管理' in message:
            manage_accounts(sender)
        elif '教程' in message or '帮助' in message:
            tutorial(sender)
        elif message == '酷我清理' and sender.isAdmin():
            clean_expired(sender)
        elif message == '酷我授权' and sender.isAdmin():
            admin_auth_menu(sender)
        else:
            sender.reply("""指令未识别，可用指令:
酷我登录 - 绑定手机号#密码
酷我查询 - 查看剩余金币和签到状态
酷我管理 - 账号管理
酷我教程 - 使用说明
酷我授权 - 管理员批量授权（仅管理员）""")
    except Exception as e:
        traceback.print_exc()
        try:
            senderID = middleware.getSenderID()
            if senderID:
                sender = middleware.Sender(senderID)
                sender.reply(f"❌ 插件运行出错: {str(e)}")
        except:
            pass

if __name__ == "__main__":
    try:
        if middleware.getSenderID() == "":
            pass
        else:
            main()
    except Exception as e:
        traceback.print_exc()
        try:
            senderID = middleware.getSenderID()
            if senderID:
                sender = middleware.Sender(senderID)
                sender.reply(f"❌ 插件运行出错: {str(e)}")
        except:
            pass