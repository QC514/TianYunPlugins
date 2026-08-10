# [rule: ^(潇洒|潇洒桐庐)(登录|登陆)$|^登(录|陆)(潇洒|潇洒桐庐)$|^(潇洒|潇洒桐庐)(查询|管理)$|^(查询|管理)(潇洒|潇洒桐庐)$|^潇洒清理$|^潇洒授权$|^潇洒教程$|^潇洒通知 ?(.*)$|^清理潇洒$|^潇洒广播 ?(.*)$]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 10 * * *]
# [public: true]
# [title: 潇洒桐庐]
# [open_source: false]
# [class: 工具类]
# [version: 1.1]
# [price: 18.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 潇洒桐庐代挂提交<br>1. 指令：潇洒登录、潇洒管理、潇洒查询、潇洒授权<br>2. 采用账号#密码登录，日0.2-0.5秒到<br>3.  售后联系：QQ 8165799，售后群1003974618 br>]
import os
import re
import ast
import json
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal
import requests
import time
import hashlib
import logging
import base64
import ssl
import warnings
import random
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    from Crypto.Cipher import PKCS1_v1_5
    from Crypto.PublicKey import RSA
except ImportError:
    logging.error("缺少 pycryptodome 库，请执行 pip install pycryptodome")

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('xiaosa_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())
usermessage = sender.getMessage()

_RUNTIME_BUCKET = "plugin_push_runtime"
_RUNTIME_KEY = "潇洒桐庐"
try:
    current_imtype = str(sender.getImtype() or "")
except:
    current_imtype = ""
if current_imtype and current_imtype.lower() not in ["fake", "cron"]:
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_sender", str(senderID))
    except: pass
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype", current_imtype)
    except: pass

# ===================== 插件配置参数 =====================
# [param: {"required":true,"key":"dd_xiaosa.panel_type","bool":false,"placeholder":"qinglong/daidai","name":"对接面板类型","desc":"qinglong=青龙面板 daidai=呆呆面板"}]
# [param: {"required":true,"key":"dd_xiaosa.dd_xiaosa_qlname","bool":false,"placeholder":"Host丨ClientID/AppKey丨Secret","name":"对接系统配置","desc":"青龙:URL丨ID丨Secret 呆呆:URL丨Key丨Secret"}]
# [param: {"required":true,"key":"dd_xiaosa.dd_xiaosa_osname","bool":false,"placeholder":"默认:xiaosa","name":"系统变量名","desc":"系统容器内变量名(默认为xiaosa)"}]
# [param: {"required":false,"key":"dd_xiaosa.epay_alipay","bool":true,"name":"易支付支付宝","desc":"启用易支付支付宝通道收款"}]
# [param: {"required":false,"key":"dd_xiaosa.epay_wxpay","bool":true,"name":"易支付微信","desc":"启用易支付微信通道收款"}]
# [param: {"required":false,"key":"dd_xiaosa.epay_qqpay","bool":true,"name":"易支付QQ","desc":"启用易支付QQ通道收款"}]
# [param: {"required":false,"key":"dd_xiaosa.epay_url","bool":false,"placeholder":"如 http://pay.xxx.com/","name":"易支付网关","desc":"易支付接口网关地址(需带http及结尾/)"}]
# [param: {"required":false,"key":"dd_xiaosa.epay_pid","bool":false,"placeholder":"","name":"易支付商户ID","desc":"易支付的PID"}]
# [param: {"required":false,"key":"dd_xiaosa.epay_key","bool":false,"placeholder":"","name":"易支付商户密钥","desc":"易支付的KEY密钥"}]
# [param: {"required":false,"key":"dd_xiaosa.enable_zsm","bool":true,"name":"个人微信收款","desc":"在支付菜单中增加个人微信收款码方式"}]
# [param: {"required":false,"key":"dd_xiaosa.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"微信收款码链接","desc":"填写个人微信收款码直链，不填则不开启"}]
# [param: {"required":true,"key":"dd_xiaosa.zsVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_xiaosa.zscoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":true,"key":"dd_xiaosa.enable_proxy","bool":true,"name":"启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_xiaosa.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_xiaosa.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"dd_xiaosa.enable_remark","bool":true,"name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"dd_xiaosa.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]

def getusercontent():
    """获取插件完整配置"""
    panel_type = middleware.bucketGet('dd_xiaosa', 'panel_type') or 'qinglong'
    panel_type = panel_type.lower()
    
    env_qlconfig = middleware.bucketGet('dd_xiaosa', 'dd_xiaosa_qlname') or ''
    env_name = middleware.bucketGet('dd_xiaosa', 'dd_xiaosa_osname') or 'xiaosa'
    
    if not env_qlconfig:
        sender.reply("❌ 配置错误：请在插件配置中填写【对接系统配置】(面板信息)。")
        exit(0)
    
    dd_managecommand = middleware.bucketGet('dd_xiaosa', 'dd_managecommand') or '潇洒管理'
    dd_querycommand = middleware.bucketGet('dd_xiaosa', 'dd_querycommand') or '潇洒查询'
    dd_signcommand = middleware.bucketGet('dd_xiaosa', 'dd_signcommand') or '潇洒登录'
    
    enable_proxy = (middleware.bucketGet('dd_xiaosa', 'enable_proxy') or 'false').lower() == 'true'
    proxy_pool_url = middleware.bucketGet('dd_xiaosa', 'proxy_pool_url') or ''
    points_bucket = middleware.bucketGet('dd_xiaosa', 'points_bucket') or 'dd_sign_points'
    enable_remark = (middleware.bucketGet('dd_xiaosa', 'enable_remark') or 'false').lower() == 'true'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    zsVipmoney = Decimal(middleware.bucketGet('dd_xiaosa', 'zsVipmoney') or '0')
    zscoin = int(middleware.bucketGet('dd_xiaosa', 'zscoin') or '0')
    reminder_days = int(middleware.bucketGet('dd_xiaosa', 'reminder_days') or '2')
    
    # 个人微信收款配置
    enable_zsm = (middleware.bucketGet('dd_xiaosa', 'enable_zsm') or 'false').lower() == 'true'
    zsm = middleware.bucketGet('dd_xiaosa', 'zsm') or ''
    
    # 易支付配置提取
    epay_url = middleware.bucketGet('dd_xiaosa', 'epay_url') or ''
    epay_pid = middleware.bucketGet('dd_xiaosa', 'epay_pid') or ''
    epay_key = middleware.bucketGet('dd_xiaosa', 'epay_key') or ''
    epay_alipay = (middleware.bucketGet('dd_xiaosa', 'epay_alipay') or 'true').lower() == 'true'
    epay_wxpay = (middleware.bucketGet('dd_xiaosa', 'epay_wxpay') or 'false').lower() == 'true'
    epay_qqpay = (middleware.bucketGet('dd_xiaosa', 'epay_qqpay') or 'false').lower() == 'true'

    return {
        'panel_type': panel_type,
        'env_name': env_name,
        'env_qlconfig': env_qlconfig,
        'dd_managecommand': dd_managecommand,
        'dd_querycommand': dd_querycommand,
        'dd_signcommand': dd_signcommand,
        'randommanagecommand': randommanagecommand,
        'randomquerycommand': randomquerycommand,
        'randomsigncommand': randomsigncommand,
        'enable_zsm': enable_zsm,
        'zsm': zsm,
        'enable_proxy': enable_proxy,
        'proxy_pool_url': proxy_pool_url,
        'points_bucket': points_bucket,
        'enable_remark': enable_remark,
        'zsVipmoney': zsVipmoney,
        'zscoin': zscoin,
        'reminder_days': reminder_days,
        'epay_url': epay_url,
        'epay_pid': epay_pid,
        'epay_key': epay_key,
        'epay_alipay': epay_alipay,
        'epay_wxpay': epay_wxpay,
        'epay_qqpay': epay_qqpay
    }

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
        for owner in middleware.bucketAllKeys(bucket='dd_xiaosa_user'):
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

def send_user_notice(user_id, msg, title="潇洒桐庐通知"):
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

# ===================== 辅助工具函数 =====================
def empower(empowertime, days):
    """计算授权到期日期。days为负数时做边界保护，最早不早于今天"""
    try:
        today_date = datetime.now().date()
        if not empowertime or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            delayed_date = empower_date + timedelta(days=days)
        # 边界保护：扣减时间后不允许早于今天（避免直接变成过期被清理）
        if days < 0 and delayed_date < today_date:
            delayed_date = today_date
        return str(delayed_date)
    except Exception as e:
        logger.error(f"授权时间计算失败: {e}")
        raise Exception(f"授权时间计算失败: {e}")

def _build_epay_sign(params_dict, key, exclude_keys=('sign', 'sign_type')):
    """易支付 MD5 V1 标准签名：排除 sign/sign_type 和空值，按 ASCII 升序拼接 + KEY"""
    filtered = {k: v for k, v in params_dict.items() if k not in exclude_keys and v != ''}
    sorted_items = sorted(filtered.items(), key=lambda x: x[0])
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_items])
    sign = hashlib.md5((sign_str + key).encode('utf-8')).hexdigest().lower()
    return sign

def _create_epay_qr(out_trade_no, channel, project_name, money_str):
    """创建易支付二维码：优先 mapi.php 原生二维码，fallback 到 submit.php 链接"""
    base_params = {
        'pid': str(config['epay_pid']).strip(),
        'type': channel,
        'out_trade_no': out_trade_no,
        'name': project_name,
        'money': money_str,
        'notify_url': 'http://127.0.0.1/',
        'return_url': 'http://127.0.0.1/'
    }
    # submit.php 用签名（不含 clientip）
    submit_sign = _build_epay_sign(base_params, config['epay_key'])
    submit_params = dict(base_params)
    submit_params['sign'] = submit_sign
    submit_params['sign_type'] = 'MD5'

    # 优先 mapi.php
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
        logger.info(f"mapi.php响应: {data}")
        if int(data.get('code', 0)) == 1:
            native_qr = data.get('qrcode', '') or data.get('payurl', '') or data.get('urlscheme', '')
            if native_qr:
                qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(native_qr, safe='')}"
        else:
            logger.warning(f"mapi失败: {data.get('msg', '')}")
    except Exception as e:
        logger.warning(f"mapi异常: {e}")

    # Fallback: submit.php
    if not qr_image_url:
        raw_query = '&'.join(f'{k}={v}' for k, v in submit_params.items())
        pay_url = config['epay_url'].rstrip('/') + '/submit.php?' + raw_query
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(pay_url, safe='')}"

    return qr_image_url, out_trade_no

def encrypt_token(token):
    try:
        return base64.b64encode(token.encode()).decode()
    except:
        return token

def decrypt_token(encrypted_token):
    try:
        return base64.b64decode(encrypted_token.encode()).decode()
    except:
        return encrypted_token

# ===================== 核心逻辑类 (潇洒桐庐同步重构版) =====================
class XiaoSaClient:
    def __init__(self, ck_str):
        self.ck_str = ck_str.strip()
        parts = self.ck_str.split('#')
        self.mobile = parts[0].strip()
        self.password = parts[1].strip() if len(parts) > 1 else ""
        
        self.code = None
        self.session_id = None
        self.account_id = None
        self.username = None
        self.wxopenid = None
        self.cnum = 0 
        self.points = 0
        self.ua = self._get_fixed_ua()
        
        # 代理功能同步
        self.proxy = None
        if config['enable_proxy'] and config['proxy_pool_url']:
            self._fetch_proxy()

    def _get_fixed_ua(self):
        """保持固定特征UA，防风控"""
        seed_str = f"xiaosa_{self.mobile}"
        seed = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)
        random.seed(seed)
        
        models = ["Xiaomi MI 8 Lite", "Xiaomi 13 Pro", "V2359A", "OPPO R11", "HUAWEI Mate 40 Pro", "vivo X90"]
        os_ver = random.randint(10, 14)
        model = random.choice(models)
        chrome_ver = f"{random.randint(80, 116)}.0.{random.randint(1000, 5000)}.138"
        
        random.seed() 
        return f"Mozilla/5.0 (Linux; Android {os_ver}; {model} Build/QKQ1.190910.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_ver} Mobile Safari/537.36;xsb_xiaosatonglu;xsb_xiaosatonglu;1.0.60;native_app;6.5.1"

    def _fetch_proxy(self):
        """同步获取代理"""
        try:
            resp = requests.get(config['proxy_pool_url'], timeout=5)
            res_text = resp.text.strip()
            new_proxy = None
            try:
                res_json = json.loads(res_text)
                if "proxy" in res_json and res_json["proxy"]:
                    new_proxy = f"http://{res_json['proxy']}"
            except:
                match = re.search(r'(\d+\.\d+\.\d+\.\d+:\d+)', res_text)
                if match:
                    new_proxy = f"http://{match.group(1)}"
            
            if new_proxy:
                self.proxy = {"http": new_proxy, "https": new_proxy}
        except Exception as e:
            logger.error(f"获取代理失败: {e}")

    def get_uuid(self):
        return str(uuid.uuid4())

    def sha256_encrypt(self, text):
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def rsa_encrypt(self, text):
        public_key = (
            "-----BEGIN PUBLIC KEY-----\n"
            "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB\n"
            "-----END PUBLIC KEY-----"
        )
        rsakey = RSA.importKey(public_key)
        cipher = PKCS1_v1_5.new(rsakey)
        cipher_text = base64.b64encode(cipher.encrypt(text.encode('utf-8')))
        return cipher_text.decode('utf-8')

    def get_headers(self):
        return {
            'Host': 'wxapi.hoolo.tv',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': self.ua,
            'Origin': 'https://tp.hoolo.tv',
            'X-Requested-With': 'com.chinamcloud.wangjie.b87d8fb20e29a0328c6e21045e8b500e',
            'Referer': 'https://tp.hoolo.tv/h5/tlread/index.html',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }

    def _sync_request(self, method, url, **kwargs):
        """带有双重状态返回的同步请求包装器，返回 (网络是否通畅, 数据)"""
        if self.proxy:
            kwargs['proxies'] = self.proxy
            
        try:
            resp = requests.request(method, url, timeout=15, verify=False, **kwargs)
            text = resp.text
            try:
                return True, json.loads(text)
            except json.JSONDecodeError:
                match = re.search(r'\((.+)\)', text)
                if match:
                    return True, json.loads(match.group(1))
                return True, text
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return False, None

    def vapp_request(self, method, path, query="", body=""):
        req_id = self.get_uuid()
        timestamp = str(int(time.time() * 1000))
        s = f"{path}&&{self.session_id or ''}&&{req_id}&&{timestamp}&&FR*r!isE5W&&59"
        sign = self.sha256_encrypt(s)
        
        headers = {
            'X-SESSION-ID': self.session_id or "",
            'X-REQUEST-ID': req_id,
            'X-TIMESTAMP': timestamp,
            'X-SIGNATURE': sign,
            'X-TENANT-ID': '59',
            'User-Agent': self.ua,
            'Host': 'vapp.tmuyun.com'
        }
        if method == "POST":
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            
        url = f"https://vapp.tmuyun.com{path}"
        if query:
            url += f"?{query}"
            
        return self._sync_request(method, url, headers=headers, data=body)

    def login_sequence(self):
        """执行完整登录链，返回: (网络请求是否成功, 登录是否成功, 提示信息)"""
        if not self.password:
            return True, False, "密码为空"

        # 1. Get Code
        url_code = "https://passport.tmuyun.com/web/oauth/credential_auth"
        headers_code = {
            'Host': 'passport.tmuyun.com',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': self.ua
        }
        encoded_pwd = urllib.parse.quote(self.rsa_encrypt(self.password))
        body_code = f"client_id=10017&password={encoded_pwd}&phone_number={self.mobile}"
        
        net_ok, res_code = self._sync_request("POST", url_code, headers=headers_code, data=body_code)
        if not net_ok: 
            return False, False, "网络请求超时或异常"

        if res_code and isinstance(res_code, dict) and str(res_code.get("code")) == "0":
            try:
                self.code = res_code.get('data', {}).get('authorization_code', {}).get('code')
            except:
                return True, False, "Code提取异常"
        else:
            return True, False, "账号密码错误或获取Code失败"

        # 2. Login
        req_id = self.get_uuid()
        timestamp = str(int(time.time() * 1000))
        # 必须使用与原始源码完全一致的固定签名串进行Login
        s = f"/api/zbtxz/login&&6565886da95d5a47f651317f&&{req_id}&&{timestamp}&&FR*r!isE5W&&59"
        sign = self.sha256_encrypt(s)
        
        url_login = "https://vapp.tmuyun.com/api/zbtxz/login"
        headers_login = {
            'X-SESSION-ID': '6565886da95d5a47f651317f',
            'X-REQUEST-ID': req_id,
            'X-TIMESTAMP': timestamp,
            'X-SIGNATURE': sign,
            'X-TENANT-ID': '59',
            'User-Agent': self.ua,
            'Host': 'vapp.tmuyun.com',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        body_login = f"check_token=&code={self.code}&token=&type=-1&union_id="
        
        net_ok, res_login = self._sync_request("POST", url_login, headers=headers_login, data=body_login)
        if not net_ok: 
            return False, False, "网络请求超时或异常"

        if res_login and isinstance(res_login, dict) and str(res_login.get("code")) == "0":
            try:
                data = res_login.get('data', {})
                self.session_id = data.get('session', {}).get('id')
                self.account_id = data.get('session', {}).get('account_id')
                self.username = data.get('account', {}).get('nick_name')
            except:
                return True, False, "会话提取异常"
        else:
            return True, False, "登录验证失败"

        return True, True, "登录成功"

    def fetch_user_data(self):
        """获取微信信息和抽奖次数、积分"""
        # 获取抽奖信息
        if self.account_id:
            safe_username = urllib.parse.quote(self.username) if self.username else ""
            url = f"https://wxapi.hoolo.tv/event/dtqp/index.php?s=/home/TmApi/getUserInformation&accountId={self.account_id}&username={safe_username}&type=jsonp"
            net_ok, res = self._sync_request("GET", url, headers=self.get_headers())
            
            if net_ok and isinstance(res, dict) and str(res.get("code")) == "0":
                data = res.get('data')
                if isinstance(data, dict):
                    self.wxopenid = data.get('userid')
                    self.cnum = int(data.get('cnum', 0))

        # 获取APP总积分
        net_ok, acc_resp = self.vapp_request("GET", "/api/user_mumber/account_detail")
        if net_ok and isinstance(acc_resp, dict) and str(acc_resp.get("code")) == "0":
            self.points = acc_resp.get("data", {}).get("rst", {}).get("total_integral", 0)

    def verify_ck(self):
        """测试存活状态，返回是否认为存活（排除网络波动导致的误判）"""
        net_ok, auth_ok, msg = self.login_sequence()
        # 若因网络超时断开连接，为防止误删账号，默认视为存活
        if not net_ok:
            return True
        return auth_ok

    def check_info(self):
        """校验登录信息，提取并组装最终结果"""
        net_ok, auth_ok, msg = self.login_sequence()
        if not net_ok:
            raise Exception("网络异常或超时，请稍后再试")
        if not auth_ok:
            raise Exception(f"校验失败: {msg}")
            
        self.fetch_user_data()

        safe_phone = self.mobile[:3] + "****" + self.mobile[-3:] if len(self.mobile) > 6 else self.mobile
        nickname = self.username if self.username else f"潇洒_{safe_phone}"
                
        return {
            "nickname": nickname,
            "phone": self.mobile,
            "cnum": self.cnum,
            "points": self.points,
            "acc_key": self.mobile,
            "final_token": self.ck_str
        }

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='dd_xiaosa_remarks', key=f'{user_id}_{account_id}')
            return str(remark_data) if remark_data else ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = str(remark).strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='dd_xiaosa_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
                return remark_clean
            return ""
        except: return ""
    
    @staticmethod
    def get_all_remarks(user_id):
        try:
            accounts = AccountManager.get_accounts(user_id)
            remarks = {}
            for account in accounts:
                remark = RemarkManager.get_account_remark(user_id, account)
                if remark: remarks[str(account)] = remark
            return remarks
        except: return {}
    
    @staticmethod
    def delete_account_remark(user_id, account_id):
        try:
            middleware.bucketDel(bucket='dd_xiaosa_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket='dd_xiaosa_user', key=str(user_id))
            if not value: return []
            if value.startswith('[') and value.endswith(']'):
                try:
                    accounts = ast.literal_eval(value)
                    if isinstance(accounts, (list, tuple, set)):
                        return [str(x) for x in list(dict.fromkeys(accounts))]
                except: pass
            return [str(value)]
        except: return []

    @staticmethod
    def add_account(user_id, account):
        try:
            account = str(account)
            accounts = AccountManager.get_accounts(user_id)
            if account not in accounts:
                accounts.append(account)
                middleware.bucketSet(bucket='dd_xiaosa_user', key=str(user_id), value=str(accounts))
                return True
            return False
        except: return False
    
    @staticmethod
    def remove_account(user_id, account):
        try:
            account = str(account)
            accounts = AccountManager.get_accounts(user_id)
            if account in accounts:
                accounts.remove(account)
                if accounts:
                    middleware.bucketSet(bucket='dd_xiaosa_user', key=str(user_id), value=str(accounts))
                else:
                    middleware.bucketDel(bucket='dd_xiaosa_user', key=str(user_id))
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(account, token):
        try:
            encrypted_token = encrypt_token(str(token))
            middleware.bucketSet(bucket='dd_xiaosa_token', key=str(account), value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_token(account):
        try:
            enc = middleware.bucketGet(bucket='dd_xiaosa_token', key=str(account))
            return decrypt_token(enc) if enc else None
        except: return None

    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket='dd_xiaosa_user')
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts: user_list.append(str(user))
            return user_list
        except: return []

# ===================== 系统对接模块(青龙/呆呆动态适配) =====================
class SystemAPI:
    def __init__(self):
        self.enabled = False
        self.panel_type = config.get('panel_type', 'qinglong')
        ql_config = config['env_qlconfig']
        try:
            if not ql_config: raise ValueError("对接配置为空")
            qllist = ql_config.split('丨')
            if len(qllist) != 3: raise ValueError("对接配置格式错误")
            self.QLurl = qllist[0].strip().rstrip('/')
            self.ClientID = qllist[1].strip()
            self.ClientSecret = qllist[2].strip()
            
            if self.panel_type == 'daidai':
                self.access_token = self._get_daidai_token()
            else:
                self.qltoken = self._get_ql_token()
            self.enabled = True
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
    
    def _get_ql_token(self):
        try:
            url = f"{self.QLurl}/open/auth/token?client_id={self.ClientID}&client_secret={self.ClientSecret}"
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()['data']['token']
            raise Exception("获取青龙Token失败")
        except Exception as e: raise

    def _get_daidai_token(self):
        try:
            url = f"{self.QLurl}/api/open-api/token"
            data = {"app_key": self.ClientID, "app_secret": self.ClientSecret}
            response = requests.post(url, json=data, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()['data']['access_token']
            raise Exception("获取呆呆Token失败")
        except Exception as e: raise
    
    def get_all_envs(self):
        if not self.enabled: return []
        try:
            if self.panel_type == 'daidai':
                url = f"{self.QLurl}/api/envs?keyword={config['env_name']}&page_size=9999"
                headers = {"Authorization": f"Bearer {self.access_token}", "accept": "application/json"}
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                if response.status_code == 200: 
                    return response.json().get('data', [])
                return []
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "accept": "application/json"}
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                if response.status_code == 200: 
                    return response.json()['data']
                return []
        except: return []
   
    def find_env(self, phone, token=None):
        if not self.enabled: return None
        phone = str(phone)
        try:
            envs = self.get_all_envs()
            for env in envs:
                if env.get('name') != config['env_name']: continue
                
                env_id = env.get('id') if env.get('id') is not None else env.get('_id')
                
                if env.get('remarks') and f'ID:{phone}' in env.get('remarks'): 
                    return env_id
                    
                if env.get('remarks') and phone in env.get('remarks'):
                    return env_id
                    
                if token and env.get('value'):
                    env_val = env.get('value').strip()
                    input_val = str(token).strip()
                    if input_val in env_val:
                        return env_id
                    
            return None
        except: return None
    
    def delete_env(self, phone):
        if not self.enabled: return False
        phone = str(phone)
        try:
            env_id = self.find_env(phone)
            if env_id is None: return False
            if self.panel_type == 'daidai':
                url = f"{self.QLurl}/api/envs/{env_id}"
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                requests.delete(url, headers=headers, timeout=10, verify=False)
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                requests.delete(url, headers=headers, json=[env_id], timeout=10, verify=False)
            return True
        except: return False
    
    def sync_env(self, token, phone, remark="", auth_time="", owner_user_id=None):
        if not self.enabled: return False
        phone = str(phone)
        try:
            env_id = self.find_env(phone, token)
            
            ql_value = f"{token}"
            
            safe_phone = phone[:3] + "****" + phone[-3:] if len(phone) > 6 else phone
            remarks_parts = [f'潇洒:{safe_phone}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{phone}', '潇洒一下提交'])
            final_remark = '丨'.join(remarks_parts)

            if self.panel_type == 'daidai':
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                if env_id is not None:
                    url = f"{self.QLurl}/api/envs/{env_id}"
                    data = {"name": config['env_name'], "value": ql_value, "remarks": final_remark}
                    res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code == 200:
                        try: requests.put(f"{self.QLurl}/api/envs/{env_id}/enable", headers=headers, timeout=5, verify=False)
                        except: pass
                    else: return False
                else:
                    url = f"{self.QLurl}/api/envs"
                    data = {"name": config['env_name'], "value": ql_value, "remarks": final_remark}
                    res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code != 200: return False
            else:
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                url = f"{self.QLurl}/open/envs"
                if env_id is not None:
                    data = {"value": ql_value, "name": config['env_name'], "remarks": final_remark}
                    if isinstance(env_id, int) or str(env_id).isdigit():
                        data["id"] = env_id
                    else:
                        data["_id"] = env_id
                        
                    res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code == 200:
                        try: requests.put(f"{self.QLurl}/open/envs/enable", headers=headers, json=[env_id], timeout=5, verify=False)
                        except: pass
                    else: return False
                else:
                    data = [{"value": ql_value, "name": config['env_name'], "remarks": final_remark}]
                    res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code != 200: return False
            return True
        except Exception as e: 
            logger.error(f"Sync Env Error: {e}")
            return False

# 初始化系统API
try:
    sys_api = SystemAPI()
    if not sys_api.enabled and sender.getImtype() != 'fake':
        sender.reply("⚠️ 系统API初始化失败，青龙/呆呆同步功能不可用，请检查配置。")
except:
    sys_api = type('obj', (object,), {'enabled': False, 'sync_env': lambda *a, **k: None, 'delete_env': lambda *a, **k: None})()
    if sender.getImtype() != 'fake':
        sender.reply("⚠️ 系统API初始化异常，青龙/呆呆同步功能不可用，请检查配置。")

# ===================== 功能逻辑 =====================

def process_single_account_query(account, index, total_count, account_remarks):
    try:
        account = str(account)
        full_token = AccountManager.get_token(account)
        if not full_token: full_token = ""
        
        accountVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        if not accountVip:
            auth_time = "无"
        elif accountVip <= today_time:
            auth_time = f"{accountVip} (已过期)"
        else:
            auth_time = accountVip

        safe_display = account[:3] + "****" + account[-3:] if len(account) > 6 else account
        remark_display = f" [{remark}]" if remark else ""

        if accountVip and accountVip > today_time:
            try:
                if not full_token or '#' not in full_token:
                    raise Exception("凭证格式异常，需为 手机号#密码")
                
                client = XiaoSaClient(full_token)
                info = client.check_info()
                nickname = info.get("nickname", safe_display)
                cnum = info.get("cnum", 0)
                points = info.get("points", 0)
                
                status_text = f"💰 当前积分: {points}\n🎁 抽奖次数: {cnum}次"
                
                account_info = f"""
=====潇洒桐庐详情=====
🚀 平台: 潇洒桐庐APP
👤 账号: {nickname}{remark_display}
{status_text}
🎯 今日进度: 自动挂机中
⏰ 授权到期: {auth_time}"""
                return account_info.strip()
            except Exception as e:
                return f"""
=====潇洒查询异常=====
📱 账号: {safe_display}
❌ 错误: {str(e)[:50]}
=================="""
        else:
            return f"""
=====潇洒桐庐状态=====
📝 备注: {remark if remark else "账号"+str(index)}
📱 账号: {safe_display}
🔐 授权: {'⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')}
⏰ 到期: {auth_time}
=================="""
    except Exception as e:
        return None

def cxs():
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
        today_time = str(datetime.now().date())

        menu = "=====潇洒桐庐查询====="
        for i, acc in enumerate(accounts, 1):
            acc = str(acc)
            remark = account_remarks.get(acc, "") if config['enable_remark'] else ""
            safe_acc = acc[:3] + "****" + acc[-3:] if len(acc) > 6 else acc
            vip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=acc)
            if not vip:
                vip_tag = '⚠️未授权'
            elif vip < today_time:
                vip_tag = '❌已过期'
            else:
                vip_tag = f'✅{vip}'
            remark_disp = f" [{remark}]" if remark else ""
            menu += f"\n[{i}] {safe_acc}{remark_disp} {vip_tag}"
        menu += f"\n------------------\n[a] 查询全部\n回复数字多选(如1,2)单独查询\n回复q退出\n=================="
        sender.reply(menu)

        sel = get_user_input(timeout=60)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已退出")
            return

        if sel.lower() == 'a':
            target_accounts = list(enumerate(accounts, 1))
        else:
            target_accounts = []
            parts = re.split(r'[,\s，]+', sel.strip())
            for p in parts:
                if p.isdigit():
                    idx = int(p)
                    if 1 <= idx <= total_count:
                        target_accounts.append((idx, accounts[idx - 1]))
            # 去重
            target_accounts = list(dict.fromkeys(target_accounts))
            
            if not target_accounts:
                sender.reply("❌ 请输入有效数字或 a")
                return

        sender.reply(f"🚀 正在查询 {len(target_accounts)} 个账号，请稍候...")
        max_workers = min(10, len(target_accounts))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_account = {}
            for index, account in target_accounts:
                future = executor.submit(process_single_account_query, account, index, total_count, account_remarks)
                future_to_account[future] = account

            for future in as_completed(future_to_account):
                result_msg = future.result()
                if result_msg: sender.reply(result_msg)

    except Exception as e:
        logger.error(f"批量查询失败: {e}")
        sender.reply(f"❌ 查询失败: {e}")

def notify_authorized_users():
    if not sender.isAdmin():
        sender.reply("❌ 只有管理员可以使用此功能")
        return
    
    content = ""
    match = re.search(r'(潇洒广播|潇洒通知) ?(.*)', usermessage)
    if match:
        content = match.group(2).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：潇洒通知 系统维护中")
        return
        
    sender.reply("⏳ 正在扫描授权用户并发送通知...")
    
    try:
        all_users = AccountManager.get_all_users()
        success_count = 0
        today = str(datetime.now().date())
        
        for uid in all_users:
            user_accounts = AccountManager.get_accounts(uid)
            has_auth = False
            for acc in user_accounts:
                vip_date = middleware.bucketGet(bucket='dd_xiaosa_auth', key=str(acc))
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                try:
                    send_user_notice(uid, f"📢 【潇洒管理员通知】\n\n{content}")
                    success_count += 1
                    time.sleep(0.3)
                except: pass
        
        sender.reply(f"✅ 通知完成\n📢 已送达: {success_count} 人")
        
    except Exception as e:
        sender.reply(f"❌ 通知异常: {e}")

def get_user_input(timeout=60):
    try:
        response = sender.listen(timeout * 1000)
        if not response: return None
        response = response.strip()
        if response.lower() in ['q', 'quit', 'exit', '退出', 'cancel']: return 'q'
        return response
    except: return None

def bindaccount():
    try:
        remark = ""
        if config['enable_remark']:
            sender.reply("""
=====账号备注设置=====
🎯 请输入账号备注名
(批量提交时此备注将应用到所有账号)
------------------
回复备注名继续
回复"n"跳过备注
回复"q"退出操作
==================""")
            remark_input = get_user_input(timeout=120)
            if remark_input == 'q':
                sender.reply("✅ 已取消")
                return
            elif remark_input != 'n' and remark_input:
                remark = remark_input.strip()[:20]
        
        sender.reply(f"""
=====潇洒桐庐 登录=====
当前模式: 🌐 提交至面板
------------------
👉 请直接发送账号密码
格式要求：手机号#密码
(例如：13800138000#abc123456)
------------------
支持批量提交，一行一个
⚠️ 绑定后根据手机号无损覆盖旧数据，不会重复!
------------------
回复"q"退出操作
==================""")
        
        input_str = get_user_input(timeout=120)
        if not input_str or input_str.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        token_lines = []
        raw_lines = [line.strip() for line in input_str.split('\n') if line.strip()]
        for line in raw_lines:
            token_lines.append(line.strip())
        
        if not token_lines:
            sender.reply("❌ 内容为空")
            return

        sender.reply(f"⏳ 正在处理 {len(token_lines)} 个账号，请稍候...")
        
        for line in token_lines:
            try:
                val = line.strip()
                if '#' not in val:
                    sender.reply(f"❌ 格式错误: 缺少#号分隔符，请检查：{val}")
                    continue
                
                client = XiaoSaClient(val)
                info_res = client.check_info()
                
                nick = info_res['nickname']
                final_token_str = info_res['final_token']
                acc_id = info_res['acc_key']
                
                process_account_binding(final_token_str, acc_id, nick, remark) 
            except Exception as ex:
                sender.reply(f"❌ 登录处理失败: {str(ex)}")
            
    except Exception as e:
        logger.error(f"绑定失败: {e}")
        sender.reply(f"❌ 绑定失败: {e}")

def process_account_binding(full_token, unique_id, nickname, remark=""):
    try:
        account = str(unique_id)
        
        accountVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=account)
        today_time = str(datetime.now().date())
        
        is_authorized = False
        if accountVip and accountVip >= today_time:
            is_authorized = True
            auth_status = f'✅ 已授权 ({accountVip})'
            next_step = f'发送 {config["randommanagecommand"]} 可管理账号'
        else:
            auth_status = '⚠️ 未授权'
            next_step = f'发送 {config["randommanagecommand"]} 进行授权'
        
        remark_info = f"\n📝 备注: {remark}" if remark else ""
        safe_display = account[:3] + "****" + account[-3:] if len(account) > 6 else account

        is_new = AccountManager.add_account(userid, account)
        if is_new:
            try: middleware.bucketSet(bucket='dd_xiaosa_bind_date', key=account, value=str(datetime.now().date()))
            except: pass
        AccountManager.update_account_token(account, full_token)
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account, remark)
        
        ql_msg = ""
        if is_authorized:
            if sys_api.sync_env(full_token, account, remark, accountVip):
                ql_msg = "\n🌐 状态: ✅ 系统已同步更新"
            else:
                ql_msg = "\n🌐 状态: ❌ 系统同步失败"
        else:
            ql_msg = "\n🌐 状态: ⏸️ 未授权暂不同步"

        sender.reply(f"""
=====潇洒账号更新=====
✅ 处理成功!
👤 用户: {nickname}
📱 账号: {safe_display}{remark_info}
🔐 授权: {auth_status}{ql_msg}
⏰ 下一步操作: 
   {next_step}
==================""")
            
    except Exception as e:
        logger.error(f"入库异常: {e}")
        sender.reply(f"❌ 入库异常: {e}")

# ===================== 支付与管理 =====================
def xy_manage():
    accounts = AccountManager.get_accounts(userid)
    if not accounts:
        sender.reply(f"❌ 未找到账号，请发送 {config['randomsigncommand']} 绑定")
        return
    
    account_remarks = RemarkManager.get_all_remarks(userid) if config['enable_remark'] else {}
    count = len(accounts)
    account_list = "======我的潇洒桐庐账号====="
    today_time = str(datetime.now().date())
    
    for i, account in enumerate(accounts, 1):
        account = str(account)
        accountVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=account)
        if not accountVip: vip_status = '⚠️ 未授权'
        elif accountVip < today_time: vip_status = '❌ 已过期'
        else: vip_status = f'✅ {accountVip}'
        
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        remark_display = f" - {remark}" if remark else ""
        
        safe_display = account[:3] + "****" + account[-3:] if len(account) > 6 else account
        
        account_list += f"\n------------------\n[{i}] 账号: {safe_display}{remark_display}\n🔐 授权: {vip_status}"
        
    account_list += "\n------------------\n[b] 批量授权\n[d] 批量删除\n[q] 退出管理\n提示: 可回复如1,2进行多选单独管理\n=================="
    sender.reply(account_list)
    
    response = get_user_input()
    if not response or response.lower() == 'q':
        sender.reply('✅ 已退出')
        return
    
    if response.lower() == 'b':
        batch_auth_flow(accounts, account_remarks)
        return
    elif response.lower() == 'd':
        batch_delete_flow(accounts)
        return
    
    # 智能解析多选
    parts = re.split(r'[,\s，]+', response.strip())
    selected_idxs = []
    for p in parts:
        if p.isdigit():
            idx = int(p)
            if 1 <= idx <= count:
                selected_idxs.append(idx)
    
    # 去重
    selected_idxs = list(dict.fromkeys(selected_idxs))
    
    if len(selected_idxs) == 1:
        manage_single_account(str(accounts[selected_idxs[0] - 1]), account_remarks)
    elif len(selected_idxs) > 1:
        selected_accs = [str(accounts[i - 1]) for i in selected_idxs]
        manage_multiple_accounts(selected_accs, account_remarks)
    else:
        sender.reply('❌ 序号无效或格式错误')

def manage_multiple_accounts(selected_accs, account_remarks):
    sender.reply(f"""=====批量管理=====
已选择 {len(selected_accs)} 个账号
------------------
[1] 批量授权
[2] 批量删除
------------------
回复数字选择，Q退出
==================""")
    sel = get_user_input()
    if sel == '1':
        batch_auth_selected(selected_accs, account_remarks)
    elif sel == '2':
        batch_delete_selected(selected_accs)
    elif sel and sel.lower() == 'q':
        sender.reply("✅ 已退出")

def batch_auth_flow(all_accounts, account_remarks):
    sender.reply("""=====选择授权账号=====
请输入要授权的账号序号
(回复 a 全选，多选如 1,2)
回复 Q 退出
==================""")
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    if sel.lower() == 'a':
        batch_auth_selected(all_accounts, account_remarks)
    else:
        parts = re.split(r'[,\s，]+', sel.strip())
        selected_accs = []
        for p in parts:
            if p.isdigit():
                idx = int(p)
                if 1 <= idx <= len(all_accounts):
                    selected_accs.append(str(all_accounts[idx-1]))
        selected_accs = list(dict.fromkeys(selected_accs))
        if selected_accs:
            batch_auth_selected(selected_accs, account_remarks)
        else:
            sender.reply("❌ 无效的序号")

def batch_delete_flow(all_accounts):
    sender.reply("""=====选择删除账号=====
请输入要删除的账号序号
(回复 a 全选，多选如 1,2)
回复 Q 退出
==================""")
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    if sel.lower() == 'a':
        batch_delete_selected(all_accounts)
    else:
        parts = re.split(r'[,\s，]+', sel.strip())
        selected_accs = []
        for p in parts:
            if p.isdigit():
                idx = int(p)
                if 1 <= idx <= len(all_accounts):
                    selected_accs.append(str(all_accounts[idx-1]))
        selected_accs = list(dict.fromkeys(selected_accs))
        if selected_accs:
            batch_delete_selected(selected_accs)
        else:
            sender.reply("❌ 无效的序号")

def manage_single_account(account, account_remarks):
    try:
        account = str(account)
        token = AccountManager.get_token(account)
        if not token: token = ""
        accountVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        safe_display = account[:3] + "****" + account[-3:] if len(account) > 6 else account
        
        menu_items = """
[1] 授权账号
[2] 删除账号
[3] 修改备注"""
            
        sender.reply(f"""
=====账号详情=====
📱 账号: {safe_display}
📝 备注: {remark}
🔐 授权: {vip_status}
=================={menu_items}
------------------
回复数字选择，Q退出
==================""")
        
        choice = get_user_input()
        if not choice or choice == 'q': return
        
        if choice == '1':
            sender.reply("请输入授权月数(如:1)，Q退出")
            months_str = get_user_input()
            if not months_str or months_str == 'q': return
            try:
                months = int(months_str)
                if months <= 0: raise ValueError
            except:
                sender.reply("❌ 数字无效")
                return
            
            if process_payment(months, accountVip, token, account, remark):
                try:
                    days = months * 30
                    new_auth_time = empower(accountVip, days)
                    try: middleware.bucketSet(bucket='dd_xiaosa_auth', key=account, value=new_auth_time)
                    except: pass

                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('dd_xiaosa_remind_log', remind_key)
                        except: pass

                    if token:
                        sys_api.sync_env(token, account, remark, new_auth_time)
                        sender.reply("🔄 授权成功并同步到系统！")
                    else:
                        sender.reply("✅ 授权成功")

                    money = Decimal(months) * config['zsVipmoney']
                    sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")
                except Exception as ex:
                    sender.reply(f"❌ 授权后续写入异常: {ex}")

        elif choice == '2':
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                try:
                    AccountManager.remove_account(userid, account)
                    try: middleware.bucketDel(bucket='dd_xiaosa_token', key=account)
                    except: pass
                    try: middleware.bucketDel(bucket='dd_xiaosa_auth', key=account)
                    except: pass
                    if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                    sys_api.delete_env(account)
                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('dd_xiaosa_remind_log', remind_key)
                        except: pass
                    sender.reply("✅ 删除成功")
                except Exception as ex:
                    sender.reply(f"❌ 删除异常: {ex}")

        elif choice == '3':
             sender.reply("请输入新备注:")
             new_remark = get_user_input()
             if new_remark and new_remark != 'q':
                 RemarkManager.set_account_remark(userid, account, new_remark)
                 if token:
                     sys_api.sync_env(token, account, new_remark, accountVip)
                 sender.reply("✅ 备注更新成功")

    except Exception as e:
        sender.reply(f"操作失败: {e}")

def process_payment(months, accountVip, token, account, remark=""):
    money = Decimal(months) * config['zsVipmoney']
    points_needed = config['zscoin'] * months
    user_points = int(middleware.bucketGet(config['points_bucket'], userid) or '0')
    
    options = []
    idx = 1
    
    # 积分支付
    if config['zscoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': points_needed, 'curr': user_points})
        idx += 1
        
    # 原生易支付接口
    if config['epay_url'] and config['epay_pid'] and config['epay_key']:
        if config['epay_alipay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'alipay', 'name': '支付宝', 'amount': money})
            idx += 1
        if config['epay_wxpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'wxpay', 'name': '微信支付', 'amount': money})
            idx += 1
        if config['epay_qqpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'qqpay', 'name': 'QQ钱包', 'amount': money})
            idx += 1

    # 个人微信收款直接弹图
    if config['enable_zsm'] and config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '个人微信收款', 'amount': money})
        idx += 1
    
    if not options:
        sender.reply("❌ 未配置任何支付方式，请联系管理员")
        return False

    msg = "=====选择支付方式====="
    for opt in options:
        amount_str = f"{opt['amount']}积分" if opt['type'] == 'pt' else f"{opt['amount']}元"
        suffix = f" (当前拥有: {opt['curr']})" if opt['type'] == 'pt' else ""
        msg += f"\n[{opt['id']}] {opt['name']} ({amount_str}){suffix}"
    msg += "\n回复数字选择，Q退出"
    sender.reply(msg)
    
    sel = get_user_input()
    if not sel or sel == 'q': return False

    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError

        if opt['type'] == 'epay':
            out_trade_no = f"XIAOSA_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
            formatted_money = f"{float(opt['amount']):.2f}"
            channel_name = "支付宝" if opt['channel'] == 'alipay' else ("微信支付" if opt['channel'] == 'wxpay' else "QQ钱包")
            
            qr_image_url, _ = _create_epay_qr(out_trade_no, opt['channel'], f"Auth_{months}M", formatted_money)
            
            sender.reply(f"=====等待支付=====\n💰 金额: {formatted_money}元\n💳 方式: {channel_name}\n📋 订单: {out_trade_no}\n------------------\n请在 180 秒内完成扫码支付 (完成后自动授权)\n回复\"q\"取消支付")
            sender.replyImage(qr_image_url)
            
            # 开启异步静默轮询查单
            start_time = time.time()
            paid = False
            query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
            
            while time.time() - start_time < 180:
                try:
                    res = requests.get(query_url, timeout=5).json()
                    if str(res.get('code')) == '1' and str(res.get('status')) == '1':
                        paid = True
                        break
                except:
                    pass
                
                cancel_check = sender.listen(3000)
                if cancel_check and cancel_check.lower() == 'q':
                    sender.reply("✅ 已取消支付")
                    return False
                
            if paid:
                return True
            else:
                sender.reply("❌ 支付超时，请重新发起。")
                return False

        elif opt['type'] == 'wx':
            if sender.atWaitPay():
                sender.reply("⚠️ 当前有人支付中")
                return False
            
            out_trade_no = f"WX_{int(time.time())}_{random.randint(100,999)}"
            sender.reply(f"=====等待支付=====\n💰 金额: {opt['amount']}元\n💳 方式: 个人微信收款\n📋 订单: {out_trade_no}\n------------------\n请在 60 秒内完成扫码支付 (完成后自动授权)\n回复\"q\"取消支付")
            sender.replyImage(config['zsm'])
            
            res = sender.waitPay("q", 60000)
            if str(res) == 'q': return False
            
            try:
                if isinstance(res, dict):
                    if res.get('Type') == '微信赞赏':
                        Money = float(res.get('Money', 0))
                        From = res.get('FromName', '')
                    elif res.get('Type') == '微信收款':
                        Money = float(res.get('Money', 0))
                        From = res.get('FromName', '')
                    elif res.get('Money'):
                        Money = float(res.get('Money', 0))
                        From = res.get('FromName', '')
                    elif res.get('money'):
                        Money = float(res.get('money', 0))
                        From = res.get('fromName', '')
                    else:
                        sender.reply('❌ 不支持的支付消息格式')
                        return False
                else:
                    try:
                        res_json = json.loads(res)
                        Money = float(res_json.get('Money', res_json.get('money', 0)))
                        From = res_json.get('FromName', res_json.get('fromName', ''))
                    except:
                        sender.reply("❌ 无法解析支付结果")
                        return False
                    
                if float(Money) >= float(money):
                    return True
                else:
                    sender.reply(f"=====支付金额错误=====\n💰 应付: {money}元\n💳 实付: {Money}元\n👤 付款人: {From}\n❗ 请联系管理员处理退款！")
                    return False
            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                return False

        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply("❌ 积分不足")
                return False
            sender.reply("确认支付回复【y】")
            if get_user_input() == 'y':
                new_pt = int(opt['curr']) - int(opt['amount'])
                try:
                    middleware.bucketSet(config['points_bucket'], userid, str(new_pt))
                except Exception as e:
                    sender.reply(f"❌ 扣除积分失败: {e}")
                    return False
                return True
            return False

    except:
        sender.reply("❌ 支付异常")
        return False

def batch_auth_selected(accounts, account_remarks):
    sender.reply("请输入授权月数，Q退出")
    m = get_user_input()
    if not m or not m.isdigit(): return
    months = int(m)
    if months <= 0: return
    
    count = len(accounts)
    total_money = Decimal(months) * config['zsVipmoney'] * count
    total_points = config['zscoin'] * months * count
    user_points = int(middleware.bucketGet(config['points_bucket'], userid) or '0')

    options = []
    idx = 1
    
    if config['zscoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': total_points, 'curr': user_points})
        idx += 1
        
    if config['epay_url'] and config['epay_pid'] and config['epay_key']:
        if config['epay_alipay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'alipay', 'name': '支付宝', 'amount': total_money})
            idx += 1
        if config['epay_wxpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'wxpay', 'name': '微信支付', 'amount': total_money})
            idx += 1
        if config['epay_qqpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'qqpay', 'name': 'QQ钱包', 'amount': total_money})
            idx += 1

    if config['enable_zsm'] and config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '个人微信收款', 'amount': total_money})
        idx += 1

    if not options:
        sender.reply("❌ 未配置任何支付方式")
        return

    msg = f"=====批量授权确认=====\n👥 账号数量: {count}个\n📅 授权时长: {months}个月\n💰 总需金额: {total_money}元\n💎 总需积分: {total_points}\n------------------"
    for opt in options:
        amount_str = f"{opt['amount']}积分" if opt['type'] == 'pt' else f"{opt['amount']}元"
        suffix = f" (当前: {opt['curr']})" if opt['type'] == 'pt' else ""
        msg += f"\n[{opt['id']}] {opt['name']} ({amount_str}){suffix}"
    msg += "\n------------------\n回复数字选择，Q退出"
    sender.reply(msg)

    sel = get_user_input()
    if not sel or sel == 'q': return

    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError
        
        if opt['type'] == 'epay':
            out_trade_no = f"XIAOSA_BATCH_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
            formatted_money = f"{float(opt['amount']):.2f}"
            channel_name = "支付宝" if opt['channel'] == 'alipay' else ("微信支付" if opt['channel'] == 'wxpay' else "QQ钱包")
            
            qr_image_url, _ = _create_epay_qr(out_trade_no, opt['channel'], f"Batch_{count}_{months}M", formatted_money)
            
            sender.reply(f"=====等待支付=====\n💰 金额: {formatted_money}元\n💳 方式: {channel_name}\n📋 订单: {out_trade_no}\n------------------\n请在 180 秒内完成扫码支付 (完成后自动批量授权)\n回复\"q\"取消支付")
            sender.replyImage(qr_image_url)
            
            start_time = time.time()
            paid = False
            query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
            
            while time.time() - start_time < 180:
                try:
                    res = requests.get(query_url, timeout=5).json()
                    if str(res.get('code')) == '1' and str(res.get('status')) == '1':
                        paid = True
                        break
                except:
                    pass
                
                cancel_check = sender.listen(3000)
                if cancel_check and cancel_check.lower() == 'q':
                    sender.reply("✅ 已取消支付")
                    return
                
            if not paid:
                sender.reply("❌ 支付超时，请重新发起。")
                return

        elif opt['type'] == 'wx':
            if sender.atWaitPay(): 
                sender.reply("⚠️ 当前有人支付中")
                return
            
            out_trade_no = f"WX_{int(time.time())}_{random.randint(100,999)}"
            sender.reply(f"=====等待支付=====\n💰 金额: {opt['amount']}元\n💳 方式: 个人微信收款\n📋 订单: {out_trade_no}\n------------------\n请在 60 秒内完成扫码支付 (完成后自动授权)\n回复\"q\"取消支付")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            if str(res) == 'q': return
            
            try:
                if isinstance(res, dict):
                    Money = float(res.get('Money', res.get('money', 0)))
                    From = res.get('FromName', res.get('fromName', ''))
                else:
                    res_json = json.loads(res)
                    Money = float(res_json.get('Money', res_json.get('money', 0)))
                    From = res_json.get('FromName', res_json.get('fromName', ''))
                    
                if float(Money) < float(opt['amount']):
                    sender.reply(f"=====支付金额错误=====\n💰 应付: {opt['amount']}元\n💳 实付: {Money}元\n👤 付款人: {From}\n❗ 请联系管理员处理退款！")
                    return
            except:
                sender.reply("❌ 处理支付结果时出错")
                return
        
        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply(f"❌ 积分不足，需要 {opt['amount']}，当前 {opt['curr']}")
                return
            sender.reply(f"确认消耗 {opt['amount']} 积分？回复【y】")
            if get_user_input() != 'y': return
            new_pt = int(opt['curr']) - int(opt['amount'])
            try: middleware.bucketSet(config['points_bucket'], userid, str(new_pt))
            except Exception as e:
                sender.reply(f"❌ 积分扣除异常: {e}")
                return

    except Exception:
        sender.reply("❌ 输入错误或支付取消")
        return

    sender.reply(f"🚀 支付成功，正在处理 {count} 个账号...")
    for account in accounts:
        try:
            account = str(account)
            accountVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=account)
            new_date = empower(accountVip, months*30)
            try: middleware.bucketSet('dd_xiaosa_auth', account, new_date)
            except: pass

            token = AccountManager.get_token(account)
            curr_remark = account_remarks.get(account, "") if account_remarks else ""

            if token:
                sys_api.sync_env(token, account, curr_remark, new_date)

            today_date = datetime.now().date()
            for d in range(config['reminder_days'] + 1):
                remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                try: middleware.bucketDel('dd_xiaosa_remind_log', remind_key)
                except: pass
        except: pass

    sender.reply("✅ 批量授权完成")

def batch_delete_selected(accounts):
    sender.reply(f"已选择 {len(accounts)} 个账号，确认删除请回复【确认删除】")
    if get_user_input() == "确认删除":
        today_date = datetime.now().date()
        for account in accounts:
            try:
                 account = str(account)
                 AccountManager.remove_account(userid, account)
                 try: middleware.bucketDel(bucket='dd_xiaosa_token', key=account)
                 except: pass
                 try: middleware.bucketDel(bucket='dd_xiaosa_auth', key=account)
                 except: pass
                 if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                 sys_api.delete_env(account)
                 for d in range(config['reminder_days'] + 1):
                     remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                     try: middleware.bucketDel('dd_xiaosa_remind_log', remind_key)
                     except: pass
            except: pass
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts():
    users = middleware.bucketAllKeys(bucket='dd_xiaosa_user')
    if not users:
        if sender.isAdmin() and usermessage in ['潇洒清理', '清理潇洒']:
            sender.reply("=====执行结果=====\n📭 暂无用户数据")
        return

    if sender.isAdmin() and usermessage in ['潇洒清理', '清理潇洒']:
        sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n⚙️ 提醒天数: {config['reminder_days']}天\n⏳ 处理中...")

    cleaned_count = 0
    reminded_count = 0
    ck_expired_count = 0
    today_date = datetime.now().date()
    reminder_days_cfg = config['reminder_days']

    for user in users:
        try:
            accounts = AccountManager.get_accounts(user)
            if not accounts: continue
            
            valid_accounts = []
            user_has_change = False
            
            try:
                user_sender = middleware.Sender(str(user))
            except: continue

            for account in accounts:
                account = str(account)
                accountVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=account)
                
                if not accountVip:
                    valid_accounts.append(account)
                    continue
                else:
                    try:
                        expiration_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                        expiration_str = accountVip
                    except:
                        expiration_date = today_date - timedelta(days=1)
                        expiration_str = "日期错误"

                days_diff = (expiration_date - today_date).days

                # ================= 凭证有效性验证 =================
                if days_diff >= 0:
                    valid_accounts.append(account)
                    
                    full_token = AccountManager.get_token(account)
                    is_ck_valid = True
                    
                    if full_token and '#' in full_token:
                        client = XiaoSaClient(full_token)
                        time.sleep(random.uniform(0.5, 1.5))
                        is_ck_valid = client.verify_ck()
                        
                        if not is_ck_valid:
                            ck_remind_key = f"ck_die_{user}_{account}_{today_date}"
                            has_ck_reminded = middleware.bucketGet('dd_xiaosa_remind_log', ck_remind_key)
                            
                            if not has_ck_reminded:
                                safe_display = account[:3] + "****" + account[-3:] if len(account) > 6 else account
                                msg = f"""=====⚠️ 登录失效提醒=====
您的潇洒桐庐账号已失效！
📱 账号: {safe_display}
📅 授权到期: {expiration_str}
------------------
系统检测到该账号可能已被改密或验证失败。
为保证挂机收益，请重新发送【{config['randomsigncommand']}】更新！
=================="""
                                send_user_notice(user, msg)
                                try: middleware.bucketSet('dd_xiaosa_remind_log', ck_remind_key, "1")
                                except: pass
                                ck_expired_count += 1
                    
                    if is_ck_valid and 0 <= days_diff <= reminder_days_cfg:
                        remind_key = f"{user}_{account}_{today_date}"
                        has_reminded = middleware.bucketGet('dd_xiaosa_remind_log', remind_key)
                        
                        if not has_reminded:
                            safe_display = account[:3] + "****" + account[-3:] if len(account) > 6 else account
                            msg = f"""=====⏰ 到期提醒=====
您的潇洒桐庐账号授权即将到期！
📱 账号: {safe_display}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                            send_user_notice(user, msg)
                            try: middleware.bucketSet('dd_xiaosa_remind_log', remind_key, "1")
                            except: pass
                            reminded_count += 1
                    continue

                # ================= 完全过期清理 =================
                if days_diff < 0:
                    try:
                        sys_api.delete_env(account)
                        try: middleware.bucketDel(bucket='dd_xiaosa_token', key=account)
                        except: pass
                        try: middleware.bucketDel(bucket='dd_xiaosa_auth', key=account)
                        except: pass
                        if config['enable_remark']:
                            RemarkManager.delete_account_remark(user, account)
                    except: pass
                    
                    safe_display = account[:3] + "****" + account[-3:] if len(account) > 6 else account
                    clean_msg = f"""=====🗑️ 过期清理通知=====
您的账号授权已过期并清理。
📱 账号: {safe_display}
📅 到期: {expiration_str}
------------------
相关配置已失效移除。
如需继续使用，请重新登录并授权。
=================="""
                    send_user_notice(user, clean_msg)
                    cleaned_count += 1
                    user_has_change = True

            if user_has_change:
                if valid_accounts:
                    try: middleware.bucketSet(bucket='dd_xiaosa_user', key=str(user), value=str(valid_accounts))
                    except: pass
                else:
                    try: middleware.bucketDel(bucket='dd_xiaosa_user', key=str(user))
                    except: pass

        except Exception as e:
            continue

    if sender.isAdmin() and usermessage in ['潇洒清理', '清理潇洒']:
        sender.reply(f"=====维护完成=====\n✅ 已清理过期: {cleaned_count}个\n📢 授权提醒: {reminded_count}个\n⚠️ 登录失效通知: {ck_expired_count}个\n==================")

def admin_auth_options():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足\n只有管理员可以执行授权操作")
        return
    
    sender.reply("""=====授权管理=====

[1] 一键授权所有用户
[2] 指定用户授权 (支持加减时间)

------------------
回复数字选择功能
回复"q"退出
==================""")
    choice = get_user_input(timeout=60)
    if choice is None or choice.lower() == 'q':
        sender.reply("✅ 已退出授权管理")
        return
    
    if choice == '1':
        admin_auth_all_users()
    elif choice == '2':
        admin_auth_specific_user()
    else:
        sender.reply("❌ 请输入有效的选项 (1或2)")

def admin_auth_all_users():
    all_users = AccountManager.get_all_users()
    if not all_users:
        sender.reply("📭 暂无绑定账号的用户")
        return
        
    sender.reply("请输入授权天数(正数增加，负数如 -10 扣除):\n回复q退出")
    days_str = get_user_input()
    if not days_str or days_str.lower() == 'q': return
    try:
        days = int(days_str)
    except:
        sender.reply("❌ 无效天数")
        return
        
    sender.reply(f"⚠️ 即将为所有用户的所有账号改变 {days} 天期限。\n确认请回复【确认授权】")
    if get_user_input() != "确认授权":
        sender.reply("✅ 已取消操作")
        return
        
    success = 0
    sender.reply("⏳ 开始批量授权，请稍候...")
    for user in all_users:
        accounts = AccountManager.get_accounts(user)
        for account in accounts:
            try:
                account = str(account)
                accVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=account)
                new_vip = empower(accVip, days)
                try: middleware.bucketSet(bucket='dd_xiaosa_auth', key=account, value=new_vip)
                except: pass
                
                token = AccountManager.get_token(account)
                remark = RemarkManager.get_account_remark(user, account) if config['enable_remark'] else ""
                
                if token:
                    sys_api.sync_env(token, account, remark, new_vip)
                success += 1
            except: pass
    sender.reply(f"✅ 一键授权完成！成功处理 {success} 个账号。")

def admin_auth_specific_user():
    sender.reply("请输入该用户的奥特曼用户标识(QQ号或微信wxid):\n回复q退出")
    target_qq = get_user_input()
    if not target_qq or target_qq.lower() == 'q': return
    target_qq = target_qq.strip()
        
    target_accounts = AccountManager.get_accounts(target_qq)
    if not target_accounts:
        sender.reply(f"❌ 用户 {target_qq} 未绑定任何账号")
        return
        
    account_remarks = RemarkManager.get_all_remarks(target_qq) if config['enable_remark'] else {}
    
    msg = f"=====用户 {target_qq} 的账号====="
    for i, acc in enumerate(target_accounts, 1):
        acc = str(acc)
        accVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=acc)
        vip_st = '未授权' if not accVip else f"已授权({accVip})"
        rem = account_remarks.get(acc, "")
        rem_disp = f" - {rem}" if rem else ""
        safe_acc = acc[:3] + "****" + acc[-3:] if len(acc) > 6 else acc
        msg += f"\n[{i}] {safe_acc}{rem_disp} - {vip_st}"
    msg += "\n------------------\n回复数字选择账号\n回复 a 操作所有账号\n回复 q 退出\n=================="
    sender.reply(msg)
    
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    if sel.lower() == 'a':
        sender.reply("请输入改变的天数(正数增加，负数如 -10 扣除):")
        d_str = get_user_input()
        if not d_str: return
        try: days = int(d_str)
        except: return sender.reply("❌ 无效天数")
        
        for acc in target_accounts:
            try:
                acc = str(acc)
                accVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=acc)
                new_vip = empower(accVip, days)
                try: middleware.bucketSet(bucket='dd_xiaosa_auth', key=acc, value=new_vip)
                except: pass
                
                token = AccountManager.get_token(acc)
                remark = account_remarks.get(acc, "")
                if token:
                    sys_api.sync_env(token, acc, remark, new_vip)
            except: pass
        sender.reply(f"✅ 已操作该用户下所有账号 {days} 天")
        
    else:
        try:
            idx = int(sel) - 1
            if idx < 0 or idx >= len(target_accounts): raise ValueError
            acc = str(target_accounts[idx])
        except: return sender.reply("❌ 序号无效")
        
        safe_acc = acc[:3] + "****" + acc[-3:] if len(acc) > 6 else acc
        sender.reply(f"目标账号: {safe_acc}\n请输入改变的天数(正数增加，负数如 -10 扣除):")
        d_str = get_user_input()
        if not d_str: return
        try: days = int(d_str)
        except: return sender.reply("❌ 无效天数")
        
        accVip = middleware.bucketGet(bucket='dd_xiaosa_auth', key=acc)
        new_vip = empower(accVip, days)
        try: middleware.bucketSet(bucket='dd_xiaosa_auth', key=acc, value=new_vip)
        except: pass
        
        token = AccountManager.get_token(acc)
        remark = account_remarks.get(acc, "")
        if token:
            sys_api.sync_env(token, acc, remark, new_vip)
        sender.reply(f"✅ 已为账号 {safe_acc}操作 {days} 天\n⏰ 最新到期时间: {new_vip}")

def show_tutorial():
    panel_name = '青龙' if config['panel_type'] == 'qinglong' else '呆呆'
    sender.reply(f"""
=====潇洒桐庐插件教程=====
当前模式: 🌐 提交至{panel_name}面板

1️⃣ {config['randomsigncommand']}
   发送 手机号#密码 系统自动加密并覆盖更新。

2️⃣ {config['randomquerycommand']}
   查询存活状态/当前积分/抽奖次数(支持1,2多选)。

3️⃣ {config['randommanagecommand']}
   全新支付接口，极简扫码无需挂机，付完全自动回调开通。

4️⃣ 潇洒清理 / 潇洒授权 / 潇洒广播
   自动/强制管理与消息分发。
   
💡 注意：本插件依赖 pycryptodome 库用于密码加密，请确保运行环境已执行：pip install pycryptodome
==================""")

# ===================== 主入口 =====================
try:
    if sender.getImtype() == 'fake':
        clean_expired_accounts()
    
    elif re.search(r'(通知|广播)', usermessage or ''):
        notify_authorized_users()
    elif re.search(r'(通知|广播)', usermessage or ''):
        notify_authorized_users()
    elif '登录' in usermessage or '登陆' in usermessage:
        bindaccount()
    elif '管理' in usermessage:
       xy_manage()
    elif '查询' in usermessage:
        cxs()
    elif usermessage in ['潇洒清理', '清理潇洒']:
        clean_expired_accounts()
    elif '广播' in usermessage or '通知' in usermessage:
        notify_authorized_users()
    elif '授权' in usermessage:
        admin_auth_options()
    elif '教程' in usermessage:
        show_tutorial()

except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")
