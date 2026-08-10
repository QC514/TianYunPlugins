# [rule: ^(爱海盐)(登录|登陆)$|^登(录|陆)(爱海盐)$|^(爱海盐)(查询|管理)$|^(查询|管理)(爱海盐)$|^爱海盐清理$|^爱海盐授权$|^爱海盐教程$|^爱海盐通知 ?(.*)$|^清理爱海盐$|^爱海盐广播 ?(.*)$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 11 * * *]
# [public: true]
# [title: 爱海盐]
# [open_source: false]
# [class: 工具类]
# [version: 1.3]
# [price: 18.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 爱海盐代挂提交<br>1. 指令：爱海盐登录、爱海盐管理、爱海盐查询、爱海盐授权<br>2. 采用手机号#密码配置登录，支持带备注提交。<br>3. 支持查询接口测活并读取当天抽奖与阅读记录。<br>4. 售后群1003974618。 售后联系：QQ 8165799<br>]

import re
import ast
from datetime import datetime, timedelta
import middleware
import urllib.parse
import gzip
from decimal import Decimal
import requests
import time
import hashlib
import hmac
import logging
import base64
import ssl
import warnings
import random
import traceback
import uuid
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.error import HTTPError, URLError
from urllib.request import Request, ProxyHandler, build_opener

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('aihaiyan_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 
MAINTENANCE_CK_MAX_WORKERS = 8

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())
usermessage = sender.getMessage()

_RUNTIME_BUCKET = "plugin_push_runtime"
_RUNTIME_KEY = "爱海盐"
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
# [param: {"required":true,"key":"aihaiyan.panel_type","bool":false,"placeholder":"qinglong/daidai","name":"对接面板类型","desc":"qinglong=青龙面板 daidai=呆呆面板"}]
# [param: {"required":true,"key":"aihaiyan.aihaiyan_qlname","bool":false,"placeholder":"Host丨ClientID/AppKey丨Secret","name":"对接系统配置","desc":"青龙:URL丨ID丨Secret 呆呆:URL丨Key丨Secret"}]
# [param: {"required":true,"key":"aihaiyan.aihaiyan_osname","bool":false,"placeholder":"默认:AiHaiYan","name":"系统变量名","desc":"系统容器内变量名(默认为AiHaiYan)"}]
# [param: {"required":false,"key":"aihaiyan.epay_alipay","bool":true,"name":"易支付支付宝","desc":"启用易支付支付宝通道收款"}]
# [param: {"required":false,"key":"aihaiyan.epay_wxpay","bool":true,"name":"易支付微信","desc":"启用易支付微信通道收款"}]
# [param: {"required":false,"key":"aihaiyan.epay_qqpay","bool":true,"name":"易支付QQ","desc":"启用易支付QQ通道收款"}]
# [param: {"required":false,"key":"aihaiyan.epay_url","bool":false,"placeholder":"如 http://pay.xxx.com/","name":"易支付网关","desc":"易支付接口网关地址(需带http及结尾/)"}]
# [param: {"required":false,"key":"aihaiyan.epay_pid","bool":false,"placeholder":"","name":"易支付商户ID","desc":"易支付的PID"}]
# [param: {"required":false,"key":"aihaiyan.epay_key","bool":false,"placeholder":"","name":"易支付商户密钥","desc":"易支付的KEY密钥"}]
# [param: {"required":false,"key":"aihaiyan.enable_zsm","bool":true,"name":"个人微信收款","desc":"在支付菜单中增加个人微信收款码方式"}]
# [param: {"required":false,"key":"aihaiyan.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"微信收款码链接","desc":"填写个人微信收款码直链，不填则不开启"}]
# [param: {"required":true,"key":"aihaiyan.zsVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"aihaiyan.zscoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":true,"key":"aihaiyan.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称，为了与铛铛互通建议填dd_sign_points"}]
# [param: {"required":true,"key":"aihaiyan.enable_remark","bool":true,"name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"aihaiyan.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]

def getusercontent():
    """获取插件完整配置"""
    panel_type = middleware.bucketGet('aihaiyan', 'panel_type') or 'qinglong'
    panel_type = panel_type.lower()
    
    env_qlconfig = middleware.bucketGet('aihaiyan', 'aihaiyan_qlname') or ''
    env_name = middleware.bucketGet('aihaiyan', 'aihaiyan_osname') or 'AiHaiYan'
    
    if not env_qlconfig:
        sender.reply("❌ 配置错误：请在插件配置中填写【对接系统配置】(面板信息)。")
        exit(0)
    
    ahy_managecommand = middleware.bucketGet('aihaiyan', 'ahy_managecommand') or '爱海盐管理'
    ahy_querycommand = middleware.bucketGet('aihaiyan', 'ahy_querycommand') or '爱海盐查询'
    ahy_signcommand = middleware.bucketGet('aihaiyan', 'ahy_signcommand') or '爱海盐登录'
    
    points_bucket = middleware.bucketGet('aihaiyan', 'points_bucket') or 'dd_sign_points'
    enable_remark = (middleware.bucketGet('aihaiyan', 'enable_remark') or 'false').lower() == 'true'
    
    randommanagecommand = ahy_managecommand
    randomquerycommand = ahy_querycommand
    randomsigncommand = ahy_signcommand
    
    zsVipmoney = Decimal(middleware.bucketGet('aihaiyan', 'zsVipmoney') or '0')
    zscoin = int(middleware.bucketGet('aihaiyan', 'zscoin') or '0')
    reminder_days = int(middleware.bucketGet('aihaiyan', 'reminder_days') or '2')
    
    # 个人微信收款配置
    enable_zsm = (middleware.bucketGet('aihaiyan', 'enable_zsm') or 'false').lower() == 'true'
    zsm = middleware.bucketGet('aihaiyan', 'zsm') or ''
    
    # 易支付配置提取
    epay_url = middleware.bucketGet('aihaiyan', 'epay_url') or ''
    epay_pid = middleware.bucketGet('aihaiyan', 'epay_pid') or ''
    epay_key = middleware.bucketGet('aihaiyan', 'epay_key') or ''
    epay_alipay = (middleware.bucketGet('aihaiyan', 'epay_alipay') or 'true').lower() == 'true'
    epay_wxpay = (middleware.bucketGet('aihaiyan', 'epay_wxpay') or 'false').lower() == 'true'
    epay_qqpay = (middleware.bucketGet('aihaiyan', 'epay_qqpay') or 'false').lower() == 'true'

    return {
        'panel_type': panel_type,
        'env_name': env_name,
        'env_qlconfig': env_qlconfig,
        'ahy_managecommand': ahy_managecommand,
        'ahy_querycommand': ahy_querycommand,
        'ahy_signcommand': ahy_signcommand,
        'randommanagecommand': randommanagecommand,
        'randomquerycommand': randomquerycommand,
        'randomsigncommand': randomsigncommand,
        'enable_zsm': enable_zsm,
        'zsm': zsm,
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

def send_user_notice(user_id, msg, title="爱海盐通知"):
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
def send_message_to_framework_admins(msg):
    notify_func = getattr(middleware, 'notifyMasters', None)
    if not callable(notify_func):
        return False
    for mode, arg in [("auto_none", None), ("auto_empty_list", [])]:
        try:
            if arg is None:
                notify_func(msg)
            else:
                notify_func(msg, arg)
            logger.info(f"框架管理员推送成功 mode={mode}")
            return True
        except TypeError:
            try:
                notify_func(msg)
                logger.info(f"框架管理员推送成功 mode={mode}->msg_only")
                return True
            except Exception as e:
                logger.warning(f"框架管理员推送失败 mode={mode}->msg_only: {e}")
        except Exception as e:
            logger.warning(f"框架管理员推送失败 mode={mode}: {e}")
    return False

def send_daily_admin_report(report_data, force_send=False, notify_status=False):
    report_date = str(report_data.get('report_date') or datetime.now().date())
    report_key = f"daily_admin_report_{report_date}"
    if not force_send and middleware.bucketGet('aihaiyan_runtime', report_key):
        if notify_status:
            sender.reply("ℹ️ 今日管理员汇总已发送过，如需重发请明天自动发送或再次手动清理。")
        return False

    msg = (
        "=====爱海盐维护完成=====\n"
        f"✅ 检测完成，共 {report_data.get('scanned_accounts', 0)} 个账号\n"
        f"📣 发送通知: {report_data.get('sent_notifications', 0)} 条\n"
        f"🗑️ 清理过期: {report_data.get('cleaned_count', 0)} 个\n"
        "=================="
    )

    if send_message_to_framework_admins(msg):
        try:
            middleware.bucketSet('aihaiyan_runtime', report_key, "framework")
        except Exception:
            pass
        if notify_status:
            sender.reply("✅ 管理员汇总已发送（框架自动管理员）")
        return True
    logger.info("框架管理员自动推送失败")
    if notify_status:
        sender.reply("❌ 管理员汇总发送失败：框架自动管理员推送未成功，请检查奥特曼默认管理员配置。")
    return False

def batch_verify_account_ck(tasks, max_workers=MAINTENANCE_CK_MAX_WORKERS):
    # 爱海盐是账密登录，改密后用户会自行重新提交；为避免误报，不做 CK 失效推送。
    return {}

    result_map = {}
    worker_count = min(max_workers, len(tasks))

    def _verify_one(task):
        user, account, token = task
        if not token:
            return (user, account, True)
        try:
            time.sleep(random.uniform(0.1, 0.35))
            client = AiHaiYanClient(token)
            return (user, account, client.verify_ck())
        except Exception as e:
            logger.warning(f"CK校验异常，按有效处理: {user}-{account} - {e}")
            return (user, account, True)

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_list = [executor.submit(_verify_one, task) for task in tasks]
        for future in as_completed(future_list):
            try:
                user, account, is_valid = future.result()
                result_map[(str(user), str(account))] = is_valid
            except Exception as e:
                logger.warning(f"并发CK校验结果读取失败: {e}")

    return result_map

def safe_send_message(user_id, msg, log_context=""):
    ok = send_user_notice(user_id, msg)
    if not ok:
        logger.warning(f"消息发送失败 {log_context}")
    return ok

def mask_account(account):
    account = str(account)
    return account[:3] + "****" + account[-3:] if len(account) >= 11 else account

def get_account_display(account, remark=""):
    remark = str(remark or "").strip()
    return remark if remark else mask_account(account)

def get_points_bucket_candidates():
    buckets = []
    configured_bucket = str(config.get('points_bucket') or '').strip()
    if configured_bucket and configured_bucket != 'dd_sign_points':
        buckets.append(configured_bucket)
    for bucket in ['dd_sign_points', configured_bucket]:
        bucket = str(bucket or '').strip()
        if bucket and bucket not in buckets:
            buckets.append(bucket)
    return buckets

def get_user_points():
    for bucket in get_points_bucket_candidates():
        try:
            value = middleware.bucketGet(bucket, userid)
            if value not in [None, '']:
                return int(value), bucket
        except:
            continue
    return 0, (get_points_bucket_candidates()[0] if get_points_bucket_candidates() else str(config.get('points_bucket') or 'dd_sign_points'))

def set_user_points(points, bucket=None):
    target_bucket = bucket or (get_points_bucket_candidates()[0] if get_points_bucket_candidates() else str(config.get('points_bucket') or 'dd_sign_points'))
    middleware.bucketSet(target_bucket, userid, str(points))

def parse_aihaiyan_credential(raw, default_remark=""):
    """支持：手机号#密码 / 备注#手机号#密码，密码中继续包含 # 时原样保留。"""
    text = str(raw or "").strip()
    if not text or "#" not in text:
        return "", "", "", "格式错误: 应为 手机号#密码"

    parts = [part.strip() for part in text.split("#")]
    if len(parts) >= 3 and re.fullmatch(r"\d{11}", parts[1] or ""):
        remark = parts[0] or default_remark
        phone = parts[1]
        password = "#".join(parts[2:]).strip()
    else:
        remark = default_remark
        phone, password = text.split("#", 1)
        phone = phone.strip()
        password = password.strip()

    if not re.fullmatch(r"\d{11}", phone or ""):
        return "", "", "", "格式错误: 手机号应为11位数字"
    if not password:
        return "", "", "", "格式错误: 密码为空"
    return phone, password, str(remark or "").strip()[:20], ""

def is_definitive_auth_failure(message):
    msg = str(message or "").lower()
    keywords = [
        "账号或密码", "密码错误", "用户名或密码", "手机号或密码",
        "credential", "invalid password", "invalid account", "unauthorized"
    ]
    return any(key.lower() in msg for key in keywords)

def get_lottery_record_paths():
    record_name = (
        os.getenv("AIHAIYAN_RECORD_FILE", "").strip()
        or middleware.bucketGet('aihaiyan', 'record_file')
        or "aihaiyan_lottery_record.json"
    )
    paths = []
    candidates = [
        record_name,
        os.path.abspath(record_name),
        f"/ql/data/scripts/{record_name}",
        f"/ql/scripts/{record_name}",
        f"../scripts/{record_name}",
    ]
    for path in candidates:
        path = str(path or "").strip()
        if path and path not in paths:
            paths.append(path)
    basename = os.path.basename(record_name)
    search_roots = [
        os.getcwd(),
        os.path.abspath("."),
        "/ql/data/scripts",
        "/ql/scripts",
        "../scripts",
    ]
    for root in search_roots:
        try:
            root = os.path.abspath(str(root))
            if not os.path.isdir(root):
                continue
            for current_root, dirs, files in os.walk(root):
                dirs[:] = [
                    d for d in dirs
                    if d not in {"node_modules", "__pycache__", ".git", ".vscode", "apk_analysis"}
                ]
                depth = os.path.relpath(current_root, root).count(os.sep)
                if depth >= 3:
                    dirs[:] = []
                if basename in files:
                    full_path = os.path.join(current_root, basename)
                    if full_path not in paths:
                        paths.append(full_path)
        except Exception:
            continue
    return paths

def normalize_prize_text(prize):
    text = str(prize or "").strip()
    if not text:
        return ""
    if "：" in text:
        text = text.split("：", 1)[1].strip()
    elif ":" in text:
        text = text.split(":", 1)[1].strip()
    return text

def get_today_prize_record(phone):
    today_key = time.strftime("%Y-%m-%d")
    phone = str(phone or "").strip()
    for path in get_lottery_record_paths():
        try:
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            today_data = data.get(today_key, {})
            if isinstance(today_data, dict):
                acc_data = today_data.get(phone)
                if not isinstance(acc_data, dict):
                    continue
                prizes = [str(x).strip() for x in (acc_data.get("prizes") or []) if str(x).strip()]
                if not prizes:
                    prizes = [
                        normalize_prize_text(x)
                        for x in (acc_data.get("lottery_results") or [])
                        if normalize_prize_text(x)
                    ]
                return {
                    "path": path,
                    "read_done": acc_data.get("read_done", 0),
                    "sign": acc_data.get("sign", ""),
                    "prizes": prizes,
                }
            if isinstance(today_data, list) and phone in today_data:
                return {"path": path, "read_done": 0, "sign": "", "prizes": []}
        except Exception as e:
            logger.warning(f"读取爱海盐抽奖记录失败 {path}: {e}")
            continue
    return None

def is_cron_trigger():
    imtype = ""
    try:
        imtype = str(sender.getImtype() or "").lower()
    except:
        pass
    msg = str(usermessage or "").strip().lower()
    return imtype in ["fake", "cron"] or msg in ["", "cron", "定时任务"]

def empower(empowertime, days):
    try:
        today_date = datetime.now().date()
        if not empowertime or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            delayed_date = empower_date + timedelta(days=days)
        if days < 0 and delayed_date < today_date:
            delayed_date = today_date
        return str(delayed_date)
    except Exception as e:
        logger.error(f"授权时间计算失败: {e}")
        raise Exception(f"授权时间计算失败: {e}")

def _build_epay_sign(params_dict, key, exclude_keys=('sign', 'sign_type')):
    filtered = {k: v for k, v in params_dict.items() if k not in exclude_keys and v != ''}
    sorted_items = sorted(filtered.items(), key=lambda x: x[0])
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_items])
    sign = hashlib.md5((sign_str + key).encode('utf-8')).hexdigest().lower()
    return sign

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
        logger.warning(f"mapi异常: {e}")

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

# ===================== 核心逻辑类 (爱海盐) =====================
CLIENT_ID = "10018"
PASSPORT_HOST = "https://passport.tmuyun.com"
VAPP_HOST = "https://vapp.tmuyun.com"
H5_API_HOST = "https://ya.iyunxh.com/api"
H5_API_FALLBACK_HOST = "https://yapi.y-h5.iyunxh.com/api"
H5_ORIGIN = "https://haiyan.y-h5.iyunxh.com"
TENANT_ID = "60"
AUTH_APPKEY = "0be39bb836a0d86aa76761af779aa93e"
H5_SIGN_SECRET = "2803cb8d50798c80b66ecd70da7e5fb1"
AIHAIYAN_PRIZE_ACTIVITY_ID = "d45e103026692d01667e08"
AIHAIYAN_PRIZE_MODULE_ID = "40602"
RSA_PUBLIC_KEY = (
    "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0"
    "RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB"
)

def now_ms():
    return int(time.time() * 1000)

def md5(value):
    return hashlib.md5(str(value).encode()).hexdigest()

def randstr(length=32):
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    return "".join(random.choice(chars) for _ in range(length))

def js_quote(value):
    value = str(value)
    return (
        urllib.parse.quote(value, safe="")
        .replace("+", "+")
        .replace("~", "%7E")
        .replace("!", "%21")
        .replace("'", "%27")
        .replace("(", "%28")
        .replace(")", "%29")
        .replace("*", "%2A")
    )

def form_string(params):
    return "&".join(f"{key}={js_quote(value)}" for key, value in params.items())

class AiHaiYanClient:
    def __init__(self, token_str):
        self.token = token_str.strip()
        self.phone = ""
        self.password = ""
        self.uid = ""
        self.aliases = []
        self.session = requests.Session()
        self.session_id = ""
        self.account_id = ""
        self.account_info = {}
        self.api_dt = ""
        self.access_token = ""
        self.access_user_id = "0"
        self.h5_api_host = H5_API_HOST
        self.app_ua = "Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36;xsb_aihaiyan;xsb_aihaiyan;3.0.61.0;native_app;6.12.0"
        self.common_ua = f"3.0.61.0;{uuid.uuid4()};Xiaomi M2011K2C;Android;11;Release;6.12.0"
        self._parse_token()

    def _parse_token(self):
        parts = self.token.split('#')
        if len(parts) >= 2:
            self.phone = parts[-2].strip()
            self.password = parts[-1].strip()
        else:
            self.phone = self.token
        self.uid = self.phone

    def _http_json(self, method, url, headers=None, body_str=None, timeout=10):
        payload = body_str.encode("utf-8") if body_str else None
        req = Request(url=url, data=payload, method=method.upper())
        if headers:
            for k, v in headers.items():
                req.add_header(k, v)
        opener = build_opener()
        with opener.open(req, timeout=timeout) as response:
            raw = response.read()
            if response.headers.get("Content-Encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw.decode("utf-8", errors="replace"))

    def rsa_encrypt_b64(self, value):
        from Crypto.Cipher import PKCS1_v1_5
        from Crypto.PublicKey import RSA
        key = RSA.import_key(base64.b64decode(RSA_PUBLIC_KEY))
        cipher = PKCS1_v1_5.new(key)
        return base64.b64encode(cipher.encrypt(value.encode())).decode()

    def login(self):
        try:
            # 引入依赖
            from Crypto.Cipher import PKCS1_v1_5
            from Crypto.PublicKey import RSA
        except ImportError:
            return False, "缺少依赖，请联系管理员执行: pip3 install pycryptodome"
            
        try:
            init_data = self.vapp_post("/api/account/init")
            self.session_id = (init_data or {}).get("data", {}).get("session", {}).get("id", "")
            if not self.session_id:
                return False, "获取session失败"

            # 1. /web/init
            init_res = self._requests_json(
                "GET",
                f"{PASSPORT_HOST}/web/init?client_id={CLIENT_ID}",
                headers={
                    "Connection": "Keep-Alive",
                    "Cache-Control": "no-cache",
                    "X-REQUEST-ID": str(uuid.uuid4()),
                    "Accept-Encoding": "gzip",
                    "user-agent": self.app_ua,
                },
            )
            
            signature_key = init_res.get("data", {}).get("client", {}).get("signature_key", "")
            if not signature_key:
                return False, "获取signature_key失败"

            # 2. /web/oauth/credential_auth
            encrypted_password = self.rsa_encrypt_b64(self.password)
            req_id = str(uuid.uuid4())
            sign_body = f"client_id={CLIENT_ID}&password={encrypted_password}&phone_number={self.phone}"
            sign_text = f"post%%/web/oauth/credential_auth?{sign_body}%%{req_id}%%"
            signature = hmac.new(signature_key.encode(), sign_text.encode(), hashlib.sha256).hexdigest()
            body = f"client_id={CLIENT_ID}&password={urllib.parse.quote(encrypted_password, safe='')}&phone_number={self.phone}"
            
            headers = {
                "X-REQUEST-ID": req_id,
                "X-SIGNATURE": signature,
                "Cache-Control": "no-cache",
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Accept-Encoding": "gzip",
                "user-agent": self.app_ua
            }
            
            auth = self._requests_json("POST", f"{PASSPORT_HOST}/web/oauth/credential_auth", headers=headers, data=body)
            if not auth or not auth.get("data"):
                return False, auth.get("message", "账号或密码错误")
            
            code = auth["data"]["authorization_code"]["code"]
            
            # 3. vapp login
            login_data = self.vapp_post("/api/zbtxz/login", f"check_token=&code={code}&token=&type=-1&union_id=")
            account_info = login_data.get("data", {}).get("account", {})
            session_info = login_data.get("data", {}).get("session", {})
            self.account_info = account_info
            self.session_id = session_info.get("id", self.session_id)
            self.account_id = str(session_info.get("account_id", "") or account_info.get("id", ""))
            if not self.session_id:
                return False, "登录未返回session"
            nickname = account_info.get("nick_name", f"用户_{self.phone[-4:]}")
            return True, nickname
        except (HTTPError, URLError, TimeoutError, requests.RequestException) as e:
            return None, f"网络异常: {e}"
        except Exception as e:
            return False, str(e)

    def _requests_json(self, method, url, headers=None, data=None, json_data=None, timeout=15):
        response = self.session.request(
            method.upper(),
            url,
            headers=headers or {},
            data=data,
            json=json_data,
            timeout=timeout,
            verify=False,
        )
        text = response.text
        if response.status_code >= 400:
            raise RuntimeError(f"HTTP {response.status_code}: {text[:120]}")
        return response.json()

    def h5_signature(self):
        nonce = randstr(32)
        timestamp = now_ms()
        signature = md5(f"haiyan{nonce}{timestamp}{H5_SIGN_SECRET}")
        return f"haiyan;{nonce};{timestamp};{signature}"

    def h5_headers(self, authed=True, json_body=False):
        headers = {
            "Connection": "keep-alive",
            "Access-T-Id-In": "69",
            "User-Agent": self.app_ua,
            "Access-Api-Unique-Token": "1",
            "Access-Api-Dt": self.api_dt or str(now_ms()),
            "Access-T-Id": "69",
            "Accept": "*/*",
            "Origin": H5_ORIGIN,
            "X-Requested-With": "com.hoge.android.app.haiyan",
            "Referer": H5_ORIGIN + "/",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        if authed:
            headers.update({
                "Access-User-Id": self.access_user_id,
                "Access-Api-Signature": self.h5_signature(),
                "Access-Wxclient-Type": "wx_app",
                "Access-Token": self.access_token,
            })
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def vapp_signature(self, path):
        req_id = str(uuid.uuid4())
        timestamp = str(now_ms())
        sign_path = path.split("?", 1)[0]
        raw = f"{sign_path}&&{self.session_id}&&{req_id}&&{timestamp}&&FR*r!isE5W&&{TENANT_ID}"
        return req_id, timestamp, hashlib.sha256(raw.encode()).hexdigest()

    def vapp_get(self, path):
        req_id, timestamp, signature = self.vapp_signature(path)
        headers = {
            "Connection": "Keep-Alive",
            "X-TIMESTAMP": timestamp,
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": req_id,
            "X-SIGNATURE": signature,
            "X-TENANT-ID": TENANT_ID,
            "X-ACCOUNT-ID": self.account_id,
            "Cache-Control": "no-cache",
            "Accept-Encoding": "gzip",
            "user-agent": self.common_ua,
        }
        return self._requests_json("GET", VAPP_HOST + path, headers=headers)

    def vapp_post(self, path, body=None):
        req_id, timestamp, signature = self.vapp_signature(path)
        headers = {
            "Connection": "Keep-Alive",
            "X-TIMESTAMP": timestamp,
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": req_id,
            "X-SIGNATURE": signature,
            "X-TENANT-ID": TENANT_ID,
            "X-ACCOUNT-ID": self.account_id,
            "Cache-Control": "no-cache",
            "Accept-Encoding": "gzip",
            "user-agent": self.common_ua,
        }
        if body is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        return self._requests_json("POST", VAPP_HOST + path, headers=headers, data=body)

    def h5_request(self, method, path, authed=True, json_body=False, json_data=None, data=None):
        hosts = []
        for host in [self.h5_api_host, H5_API_HOST, H5_API_FALLBACK_HOST]:
            if host and host not in hosts:
                hosts.append(host)
        last_error = None
        for host in hosts:
            try:
                result = self._requests_json(
                    method,
                    host + path,
                    headers=self.h5_headers(authed=authed, json_body=json_body),
                    data=data,
                    json_data=json_data,
                )
                self.h5_api_host = host
                return result
            except Exception as e:
                last_error = e
                continue
        raise last_error or RuntimeError("H5请求失败")

    def h5_get(self, path):
        return self.h5_request("GET", path)

    def find_buoy_id(self, pattern):
        data = self.vapp_get("/api/buoy/list")
        text = json.dumps(data or {}, ensure_ascii=False, separators=(",", ":"))
        match = re.search(pattern, text)
        return match.group(1) if match else ""

    def init_h5(self):
        if self.access_token and self.access_user_id != "0":
            return True
        if not self.session_id:
            return False

        dt = self.h5_request("GET", "/aosbase/_auth_dt", authed=False)
        dt_data = (dt or {}).get("data", "")
        self.api_dt = str(dt_data)[32:68]
        if not self.api_dt:
            return False

        account_info = self.account_info or {}
        payload = {
            "app_user_token": self.session_id,
            "appid": "haiyan",
            "noncestr": randstr(6),
            "phone": self.phone,
            "portrait_url": account_info.get("image_url", ""),
            "timestamp": str(int(time.time())),
            "user_id": account_info.get("id", self.account_id),
            "user_name": account_info.get("nick_name", ""),
            "wx_openid": "",
            "wx_unionid": "",
        }
        payload["signature"] = md5(form_string(payload) + f"&appkey={AUTH_APPKEY}")
        auth_user = self.h5_request("POST", "/aosbase/_auth_appuserinit", json_body=True, json_data=payload)
        auth_data = (auth_user or {}).get("data", {})
        self.access_token = auth_data.get("access_token", "")
        self.access_user_id = str(auth_data.get("data", {}).get("user_id", "0"))
        return bool(self.access_token and self.access_user_id != "0")

    def get_lottery_query_targets(self):
        if not self.init_h5():
            return []
        targets = []
        seen = set()

        def add_target(lottery_id, label):
            lottery_id = str(lottery_id or "").strip()
            if not lottery_id or lottery_id in seen:
                return
            seen.add(lottery_id)
            module_id = ""
            try:
                detail = self.h5_get(f"/aoslottery/_ac_detail?id={lottery_id}") or {}
                module_id = str((detail.get("data") or {}).get("m_id") or "")
            except Exception as e:
                logger.warning(f"获取爱海盐{label}详情失败: {e}")
            targets.append({
                "activity_id": lottery_id,
                "module_id": module_id or AIHAIYAN_PRIZE_MODULE_ID,
                "label": label,
            })

        try:
            study_id = self.find_buoy_id(r"/module-study/home/home\?hide_back=1&id=([a-zA-Z0-9]+)")
            if study_id:
                detail = self.h5_get(f"/aoslearnfoot/_ac_detail?id={study_id}") or {}
                other_set = (detail.get("data") or {}).get("other_set", "{}")
                lottery_id = json.loads(other_set or "{}").get("lottery", {}).get("id")
                add_target(lottery_id, "阅读抽奖")
        except Exception as e:
            logger.warning(f"动态获取阅读抽奖ID失败: {e}")

        try:
            sign_id = self.find_buoy_id(r"/module-signin/home/home\?hide_back=1&id=([a-zA-Z0-9]+)")
            if sign_id:
                detail = self.h5_get(f"/aossignin/_ac_detail?id={sign_id}") or {}
                text = json.dumps(detail or {}, ensure_ascii=False, separators=(",", ":"))
                match = re.search(r"/module-lottery/home/home\?hide_back=1&id=([a-zA-Z0-9]+)", text)
                if match:
                    add_target(match.group(1), "签到抽奖")
        except Exception as e:
            logger.warning(f"动态获取签到抽奖ID失败: {e}")

        if not targets:
            activity_id = middleware.bucketGet('aihaiyan', 'prize_activity_id') or AIHAIYAN_PRIZE_ACTIVITY_ID
            module_id = middleware.bucketGet('aihaiyan', 'prize_module_id') or AIHAIYAN_PRIZE_MODULE_ID
            targets.append({"activity_id": activity_id, "module_id": module_id, "label": "抽奖"})
        return targets

    def query_today_prizes(self):
        today = datetime.now().strftime("%Y-%m-%d")
        prizes = []
        errors = []
        targets = self.get_lottery_query_targets()
        if not targets:
            return None, "未获取到抽奖活动"
        for target in targets:
            try:
                path = (
                    f"/aoslottery/act_user"
                    f"?offset=0&count=50&activity_id={target['activity_id']}&module_id={target['module_id']}"
                )
                data = self.h5_get(path)
                if not isinstance(data, dict):
                    errors.append(f"{target['label']}响应异常")
                    continue
                rows = data.get("data") or []
                if not isinstance(rows, list):
                    errors.append(data.get("msg") or f"{target['label']}数据异常")
                    continue
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    created_at = str(row.get("created_at") or row.get("createdAt") or "")
                    if created_at and not created_at.startswith(today):
                        continue
                    title = str(row.get("title") or row.get("goods_title") or "").strip()
                    if not title:
                        value = str(row.get("value") or "").strip()
                        title = f"{value}积分" if value else ""
                    if title:
                        prizes.append(title)
            except Exception as e:
                errors.append(f"{target.get('label', '抽奖')}:{str(e)[:30]}")
        if errors and not prizes:
            return None, "；".join(errors[:2])
        return prizes, ""

    def verify_ck(self):
        success, msg = self.login()
        if success is None:
            return True
        if success:
            return True
        return not is_definitive_auth_failure(msg)

    def get_info(self):
        """调用API进行测活，并读取当天奖品列表。"""
        prize_record = get_today_prize_record(self.phone)
        if prize_record:
            prizes = prize_record.get("prizes") or []
            prize_str = "、".join(prizes) if prizes else "无"
            record_msg = f"✅ 青龙记录已匹配\n🎁 今日奖品: {prize_str}"
            return True, True, f"用户_{self.phone[-4:]}", record_msg

        success, result = self.login()
        if success is None:
            return False, True, "未知", result
        if success:
            record_msg = "✅ 登录验证成功"
            try:
                prizes, prize_err = self.query_today_prizes()
                if prizes is not None:
                    prize_str = "、".join(prizes) if prizes else "无"
                    record_msg += f"\n🎁 今日奖品: {prize_str}"
                else:
                    record_msg += f"\nℹ️ 今日奖品: 查询失败({str(prize_err)[:30]})"
            except Exception as e:
                prize_record = get_today_prize_record(self.phone)
                if prize_record:
                    prizes = prize_record.get("prizes") or []
                    prize_str = "、".join(prizes) if prizes else "无"
                    record_msg += f"\n🎁 今日奖品: {prize_str}"
                else:
                    record_msg += f"\nℹ️ 今日奖品: 查询异常({str(e)[:30]})"
            return True, True, result, record_msg
        else:
            return True, False, "未知", f"登录失败: {result}"

    def check_info(self):
        safe_phone = mask_account(self.phone)
        nickname = f"海盐_{safe_phone}"
        final_token = f"{self.phone}#{self.password}"
                
        return {
            "nickname": nickname,
            "phone": self.phone,
            "acc_key": self.phone,
            "acc_type": "phone",
            "aliases": [self.phone],
            "legacy_key": hashlib.md5(self.token.encode()).hexdigest()[:8],
            "final_token": final_token
        }

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='aihaiyan_remarks', key=f'{user_id}_{account_id}')
            return str(remark_data) if remark_data else ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = str(remark).strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='aihaiyan_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
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
            middleware.bucketDel(bucket='aihaiyan_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket='aihaiyan_user', key=str(user_id))
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
                middleware.bucketSet(bucket='aihaiyan_user', key=str(user_id), value=str(accounts))
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
                    middleware.bucketSet(bucket='aihaiyan_user', key=str(user_id), value=str(accounts))
                else:
                    middleware.bucketDel(bucket='aihaiyan_user', key=str(user_id))
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(account, token):
        try:
            encrypted_token = encrypt_token(str(token))
            middleware.bucketSet(bucket='aihaiyan_token', key=str(account), value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_token(account):
        try:
            enc = middleware.bucketGet(bucket='aihaiyan_token', key=str(account))
            return decrypt_token(enc) if enc else None
        except: return None

    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket='aihaiyan_user')
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts: user_list.append(str(user))
            return user_list
        except: return []

    @staticmethod
    def migrate_account(user_id, old_account, new_account, new_token, remark=""):
        try:
            old_account = str(old_account)
            new_account = str(new_account)
            if not old_account or not new_account or old_account == new_account:
                return False

            accounts = AccountManager.get_accounts(user_id)
            if old_account not in accounts:
                return False

            old_vip = middleware.bucketGet(bucket='aihaiyan_auth', key=old_account)
            new_vip = middleware.bucketGet(bucket='aihaiyan_auth', key=new_account)
            if old_vip and (not new_vip or str(old_vip) > str(new_vip)):
                middleware.bucketSet(bucket='aihaiyan_auth', key=new_account, value=old_vip)

            old_bind_date = middleware.bucketGet(bucket='aihaiyan_bind_date', key=old_account)
            if old_bind_date and not middleware.bucketGet(bucket='aihaiyan_bind_date', key=new_account):
                middleware.bucketSet(bucket='aihaiyan_bind_date', key=new_account, value=old_bind_date)

            if config['enable_remark']:
                old_remark = RemarkManager.get_account_remark(user_id, old_account)
                final_remark = remark or old_remark
                if final_remark:
                    RemarkManager.set_account_remark(user_id, new_account, final_remark)
                RemarkManager.delete_account_remark(user_id, old_account)

            new_accounts = []
            for acc in accounts:
                if acc == old_account:
                    acc = new_account
                if acc not in new_accounts:
                    new_accounts.append(acc)
            middleware.bucketSet(bucket='aihaiyan_user', key=str(user_id), value=str(new_accounts))

            AccountManager.update_account_token(new_account, new_token)
            try: middleware.bucketDel(bucket='aihaiyan_token', key=old_account)
            except: pass
            try: middleware.bucketDel(bucket='aihaiyan_auth', key=old_account)
            except: pass
            return True
        except Exception as e:
            logger.error(f"Account migrate failed: {e}")
            return False

    @staticmethod
    def find_migration_source(user_id, new_account, aliases=None, acc_type="", legacy_key=""):
        try:
            new_account = str(new_account)
            legacy_key = str(legacy_key or "")
            aliases = [str(x) for x in (aliases or []) if str(x)]

            new_ids = set(aliases)
            if acc_type != "token_md5":
                new_ids.add(new_account)
            if legacy_key:
                new_ids.discard(legacy_key)

            for old_account in AccountManager.get_accounts(user_id):
                old_account = str(old_account)
                if old_account == new_account:
                    continue
                if old_account in new_ids:
                    return old_account

                old_token = AccountManager.get_token(old_account)
                if not old_token:
                    continue

                old_client = AiHaiYanClient(old_token)
                old_info = old_client.check_info()
                old_ids = set(old_info.get('aliases', []))
                if old_info.get('acc_type') != "token_md5":
                    old_ids.add(str(old_info.get('acc_key', "")))
                old_legacy = str(old_info.get('legacy_key', ""))
                if old_legacy:
                    old_ids.discard(old_legacy)

                if new_ids and old_ids and (new_ids & old_ids):
                    return old_account
            return ""
        except Exception as e:
            logger.error(f"Find migration source failed: {e}")
            return ""

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
   
    def _env_id(self, env):
        return env.get('id') if env.get('id') is not None else env.get('_id')

    def _env_value_tokens(self, value):
        return [x.strip() for x in re.split(r'[&\n]+', str(value or '')) if x.strip()]

    def _is_aggregate_value(self, value):
        return len(self._env_value_tokens(value)) > 1

    def _phone_from_token(self, token):
        token = str(token or '').strip()
        return token.split('#', 1)[0].strip() if token else ''

    def _env_matches_account(self, env, phone='', token='', include_aggregate=False):
        value = str(env.get('value') or '').strip()
        remarks = str(env.get('remarks') or env.get('remark') or '')
        phone = str(phone or '').strip()
        token = str(token or '').strip()
        tokens = self._env_value_tokens(value)

        if not include_aggregate and len(tokens) > 1:
            return False
        if token and (value == token or (include_aggregate and token in tokens)):
            return True
        if phone:
            if len(tokens) <= 1 and self._phone_from_token(value) == phone:
                return True
            if f"账号:{phone}" in remarks or f"账号：{phone}" in remarks:
                return True
        return False

    def find_env(self, phone=None, token=None):
        """查找指定账号的独立面板变量，不再把多个账号聚合到一条变量。"""
        if not self.enabled: return None
        try:
            for env in self.get_all_envs():
                if env.get('name') != config['env_name']:
                    continue
                if self._env_matches_account(env, phone=phone, token=token):
                    return self._env_id(env)
            return None
        except: return None

    def _delete_env_id(self, env_id):
        if env_id is None:
            return False
        if self.panel_type == 'daidai':
            url = f"{self.QLurl}/api/envs/{env_id}"
            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
            requests.delete(url, headers=headers, timeout=10, verify=False)
        else:
            url = f"{self.QLurl}/open/envs"
            headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
            requests.delete(url, headers=headers, json=[env_id], timeout=10, verify=False)
        return True

    def _cleanup_duplicate_envs(self, keep_id=None):
        try:
            keep_id = str(keep_id) if keep_id is not None else ""
            for env in self.get_all_envs():
                if env.get('name') != config['env_name']:
                    continue
                env_id = self._env_id(env)
                if keep_id and str(env_id) == keep_id:
                    continue
                self._delete_env_id(env_id)
        except Exception as e:
            logger.warning(f"清理重复面板变量失败: {e}")

    def _cleanup_envs(self, active_items=None, delete_phones=None):
        active_items = active_items or {}
        delete_phones = {str(x) for x in (delete_phones or []) if str(x)}
        kept_phones = set()
        try:
            for env in self.get_all_envs():
                if env.get('name') != config['env_name']:
                    continue
                env_id = self._env_id(env)
                value = str(env.get('value') or '').strip()
                matched_phone = ''

                for phone, item in active_items.items():
                    if self._env_matches_account(env, phone=phone, token=item.get('token', '')):
                        matched_phone = str(phone)
                        break

                should_delete = False
                if self._is_aggregate_value(value):
                    should_delete = True
                elif any(self._env_matches_account(env, phone=phone, include_aggregate=True) for phone in delete_phones):
                    should_delete = True
                elif active_items and not matched_phone:
                    should_delete = True
                elif matched_phone:
                    if matched_phone in kept_phones:
                        should_delete = True
                    else:
                        kept_phones.add(matched_phone)
                elif not active_items and not delete_phones:
                    should_delete = True

                if should_delete:
                    self._delete_env_id(env_id)
        except Exception as e:
            logger.warning(f"清理面板变量失败: {e}")

    def _collect_env_items(self, extra=None, exclude_phone=""):
        today = str(datetime.now().date())
        items = {}
        exclude_phone = str(exclude_phone or "")
        for user in AccountManager.get_all_users():
            try:
                remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
                for account in AccountManager.get_accounts(user):
                    account = str(account)
                    if account == exclude_phone:
                        continue
                    vip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
                    token = AccountManager.get_token(account)
                    if not vip or str(vip) < today or not token:
                        continue
                    items[account] = {
                        "token": str(token).strip(),
                        "remark": remarks.get(account, ""),
                        "vip": str(vip),
                    }
            except Exception:
                continue

        if extra:
            phone = str(extra.get("phone") or "")
            token = str(extra.get("token") or "").strip()
            auth_time = str(extra.get("auth_time") or "")
            if phone and phone != exclude_phone and token and auth_time and auth_time >= today:
                items[phone] = {
                    "token": token,
                    "remark": str(extra.get("remark") or ""),
                    "vip": auth_time,
                }
        return items

    def _build_single_env_remark(self, phone, item):
        remark = str(item.get("remark") or "").strip()
        vip = str(item.get("vip") or "").strip()
        bits = [f"账号:{phone}"]
        if remark:
            bits.append(f"备注:{remark}")
        if vip:
            bits.append(f"到期:{vip}")
        bits.append(f"更新:{datetime.now().strftime('%m-%d %H:%M')}")
        bits.append("爱海盐提交")
        return "丨".join(bits)

    def _upsert_single_env(self, phone, item):
        ql_value = str(item.get("token") or "").strip()
        if not ql_value:
            return False, None
        final_remark = self._build_single_env_remark(phone, item)
        env_id = self.find_env(phone=phone, token=ql_value)
        if self.panel_type == 'daidai':
            headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
            if env_id is not None:
                url = f"{self.QLurl}/api/envs/{env_id}"
                data = {"name": config['env_name'], "value": ql_value, "remarks": final_remark}
                res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                if res.status_code == 200:
                    try: requests.put(f"{self.QLurl}/api/envs/{env_id}/enable", headers=headers, timeout=5, verify=False)
                    except: pass
                else: return False, env_id
            else:
                url = f"{self.QLurl}/api/envs"
                data = {"name": config['env_name'], "value": ql_value, "remarks": final_remark}
                res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                if res.status_code != 200: return False, env_id
                try:
                    env_id = self._env_id((res.json().get("data") or {}))
                except Exception:
                    env_id = self.find_env(phone=phone, token=ql_value)
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
                else: return False, env_id
            else:
                data = [{"value": ql_value, "name": config['env_name'], "remarks": final_remark}]
                res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                if res.status_code != 200: return False, env_id
                env_id = self.find_env(phone=phone, token=ql_value)
        return True, env_id

    def _sync_env_items(self, items):
        if not items:
            self._cleanup_envs()
            return True
        success = True
        for phone in sorted(items.keys()):
            ok, _ = self._upsert_single_env(phone, items[phone])
            if not ok:
                success = False
        if success:
            self._cleanup_envs(active_items=items)
        return success
    
    def delete_env(self, phone):
        if not self.enabled: return False
        phone = str(phone)
        try:
            items = self._collect_env_items(exclude_phone=phone)
            ok = self._sync_env_items(items)
            self._cleanup_envs(active_items=items, delete_phones=[phone])
            return ok
        except Exception as e:
            logger.error(f"Delete Env Error: {e}")
            return False
    
    def sync_env(self, token, phone, remark="", auth_time=""):
        if not self.enabled: return False
        phone = str(phone)
        try:
            items = self._collect_env_items({
                "phone": phone,
                "token": token,
                "remark": remark,
                "auth_time": auth_time,
            })
            if not items:
                return False
            return self._sync_env_items(items)
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
        
        accountVip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        if not accountVip:
            auth_time = "无"
        elif accountVip <= today_time:
            auth_time = f"{accountVip} (已过期)"
        else:
            auth_time = accountVip

        account_display = get_account_display(account, remark)

        if accountVip and accountVip > today_time:
            try:
                if not full_token or len(full_token) < 10:
                    raise Exception("凭证异常或为空")
                
                client = AiHaiYanClient(full_token)
                info = client.check_info()
                nickname = info.get("nickname", mask_account(account))
                
                # 请求API实时测活并读取本地抽奖记录
                net_ok, is_valid, user_nick, msg = client.get_info()
                if net_ok and not is_valid:
                    status_text = f"⚠️ 账号登录失败: {msg}"
                elif not net_ok:
                    status_text = f"⚠️ 网络查询异常: {str(msg)[:50]}"
                else:
                    status_text = f"✅ 当前登录: {user_nick}\n{msg}"
                
                account_info = f"""
=====爱海盐详情=====
🚀 平台: 爱海盐
👤 账号: {account_display}
{status_text}
🎯 今日进度: 自动挂机中
⏰ 授权到期: {auth_time}"""
                return account_info.strip()
            except Exception as e:
                return f"""
=====爱海盐查询异常=====
📱 账号: {account_display}
❌ 错误: {str(e)[:50]}
=================="""
        else:
            return f"""
=====爱海盐状态=====
📱 账号: {account_display}
📝 备注: {remark if remark else "无"}
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

        menu = "=====爱海盐查询====="
        for i, acc in enumerate(accounts, 1):
            acc = str(acc)
            remark = account_remarks.get(acc, "") if config['enable_remark'] else ""
            account_display = get_account_display(acc, remark)
            vip = middleware.bucketGet(bucket='aihaiyan_auth', key=acc)
            if not vip:
                vip_tag = '⚠️未授权'
            elif vip < today_time:
                vip_tag = '❌已过期'
            else:
                vip_tag = f'✅{vip}'
            menu += f"\n[{i}] {account_display} {vip_tag}"
        menu += f"\n------------------\n[a] 查询全部\n支持单选/多选/区间，如 1,2 或 3-6\n回复q退出\n=================="
        sender.reply(menu)

        sel = get_user_input(timeout=60)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已退出")
            return

        if sel.lower() == 'a':
            target_accounts = list(enumerate(accounts, 1))
        else:
            selected_idxs, invalid_parts = parse_index_selection(sel, total_count, allow_all=False)
            target_accounts = [(idx, accounts[idx - 1]) for idx in selected_idxs]
            
            if not target_accounts:
                sender.reply("❌ 请输入有效序号，例如 1,2 或 3-6")
                return
            if invalid_parts:
                sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")

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
    match = re.search(r'(爱海盐广播|爱海盐通知) ?(.*)', usermessage)
    if match:
        content = match.group(2).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：爱海盐通知 系统维护中")
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
                vip_date = middleware.bucketGet(bucket='aihaiyan_auth', key=str(acc))
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                try:
                    send_user_notice(uid, f"📢 【爱海盐管理员通知】\n\n{content}")
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

def parse_index_selection(text, total_count, allow_all=True):
    try:
        if text is None:
            return [], []
        raw = str(text).strip()
        if not raw:
            return [], []
        if allow_all and raw.lower() in ['a', 'all', '全部', '全选']:
            return list(range(1, total_count + 1)), []

        selected = []
        invalid = []
        parts = re.split(r'[,\s，、;；]+', raw)
        for part in parts:
            part = part.strip()
            if not part:
                continue

            range_match = re.match(r'^(\d+)\s*(?:-|~|到|至)\s*(\d+)$', part)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                if start > end:
                    start, end = end, start
                start = max(1, start)
                end = min(total_count, end)
                if start <= end:
                    selected.extend(range(start, end + 1))
                else:
                    invalid.append(part)
                continue

            if part.isdigit():
                idx = int(part)
                if 1 <= idx <= total_count:
                    selected.append(idx)
                else:
                    invalid.append(part)
                continue

            invalid.append(part)

        return list(dict.fromkeys(selected)), invalid
    except:
        return [], [str(text)]

def pick_accounts_by_indexes(accounts, indexes):
    return [str(accounts[i - 1]) for i in indexes if 1 <= i <= len(accounts)]

def selection_tip(action="选择"):
    return f"回复 a 全选\n支持单选/多选/区间，如 1,2 或 3-6 或 1,3-8,10\n回复 q 退出"

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
=====爱海盐 登录=====
当前模式: 🌐 提交至面板
------------------
👉 请直接发送账号配置，格式如下(一行一个)：
手机号#密码
或带备注:
备注#手机号#密码
------------------
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
        bind_stats = {"success": 0, "fail": 0, "new": 0, "update": 0, "migrate": 0}
        fail_msgs = []
        
        for line in token_lines:
            try:
                phone, pwd, line_remark, parse_err = parse_aihaiyan_credential(line, remark)
                if parse_err:
                    bind_stats["fail"] += 1
                    fail_msgs.append(parse_err)
                    if len(token_lines) == 1:
                        sender.reply(f"❌ {parse_err}")
                    continue

                final_token_str = f"{phone}#{pwd}"
                
                client = AiHaiYanClient(final_token_str)
                info_res = client.check_info()
                
                nick = info_res['nickname']
                final_token_str = info_res['final_token']
                acc_id = info_res['acc_key']
                aliases = info_res.get('aliases', [])
                acc_type = info_res.get('acc_type', '')
                legacy_key = info_res.get('legacy_key', '')
                
                bind_result = process_account_binding(final_token_str, acc_id, nick, line_remark, aliases, acc_type, legacy_key, silent=(len(token_lines) > 1))
                if bind_result.get("ok"):
                    bind_stats["success"] += 1
                    bind_stats[bind_result.get("action", "update")] += 1
                    if bind_result.get("migrated"):
                        bind_stats["migrate"] += 1
                else:
                    bind_stats["fail"] += 1
                    fail_msgs.append(bind_result.get("msg", "处理失败"))
            except Exception as ex:
                bind_stats["fail"] += 1
                fail_msgs.append(str(ex)[:30])
                if len(token_lines) == 1:
                    sender.reply(f"❌ 登录处理失败: {str(ex)}")

        if len(token_lines) > 1:
            fail_text = ""
            if fail_msgs:
                fail_text = "\n❌ 失败原因: " + "；".join(list(dict.fromkeys(fail_msgs))[:3])
            sender.reply(f"""=====爱海盐登录汇总=====
✅ 成功: {bind_stats['success']} 个
🆕 新增: {bind_stats['new']} 个
🔄 更新: {bind_stats['update']} 个
🔁 承接旧账号: {bind_stats['migrate']} 个
❌ 失败: {bind_stats['fail']} 个{fail_text}
==================""")
            
    except Exception as e:
        logger.error(f"绑定失败: {e}")
        sender.reply(f"❌ 绑定失败: {e}")

def process_account_binding(full_token, unique_id, nickname, remark="", aliases=None, acc_type="", legacy_key="", silent=False):
    try:
        account = str(unique_id)
        aliases = [str(x) for x in (aliases or []) if str(x) and str(x) != account]
        migrated_from = ""
        existing_accounts = AccountManager.get_accounts(userid)
        if account not in existing_accounts:
            old_account = AccountManager.find_migration_source(userid, account, aliases, acc_type, legacy_key)
            if old_account and AccountManager.migrate_account(userid, old_account, account, full_token, remark):
                migrated_from = old_account
        
        accountVip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
        today_time = str(datetime.now().date())
        
        is_authorized = False
        if accountVip and accountVip >= today_time:
            is_authorized = True
            auth_status = f'✅ 已授权 ({accountVip})'
            next_step = f'发送 {config["randommanagecommand"]} 可管理账号'
        else:
            auth_status = '⚠️ 未授权'
            next_step = f'发送 {config["randommanagecommand"]} 进行授权'
        
        if config['enable_remark'] and not remark:
            remark = RemarkManager.get_account_remark(userid, account)

        remark_info = f"\n📝 备注: {remark}" if remark else ""
        account_display = get_account_display(account, remark)

        is_new = AccountManager.add_account(userid, account)
        action = "new" if is_new else "update"
        if is_new:
            try: middleware.bucketSet(bucket='aihaiyan_bind_date', key=account, value=str(datetime.now().date()))
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

        migrate_msg = ""
        if migrated_from:
            old_safe = mask_account(migrated_from)
            migrate_msg = f"\n🔁 已承接旧账号: {old_safe}"

        if not silent:
            sender.reply(f"""
=====爱海盐账号更新=====
✅ 处理成功!
👤 用户: {nickname}
📱 账号: {account_display}{migrate_msg}{remark_info}
🔐 授权: {auth_status}{ql_msg}
⏰ 下一步操作: 
   {next_step}
==================""")
        return {"ok": True, "account": account, "action": action, "migrated": bool(migrated_from)}
            
    except Exception as e:
        logger.error(f"入库异常: {e}")
        if not silent:
            sender.reply(f"❌ 入库异常: {e}")
        return {"ok": False, "msg": str(e)}

# ===================== 支付与管理 =====================
def xy_manage():
    accounts = AccountManager.get_accounts(userid)
    if not accounts:
        sender.reply(f"❌ 未找到账号，请发送 {config['randomsigncommand']} 绑定")
        return
    
    account_remarks = RemarkManager.get_all_remarks(userid) if config['enable_remark'] else {}
    count = len(accounts)
    account_list = "======我的爱海盐账号====="
    today_time = str(datetime.now().date())
    
    for i, account in enumerate(accounts, 1):
        account = str(account)
        accountVip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
        if not accountVip: vip_status = '⚠️ 未授权'
        elif accountVip < today_time: vip_status = '❌ 已过期'
        else: vip_status = f'✅ {accountVip}'
        
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        account_display = get_account_display(account, remark)
        
        account_list += f"\n------------------\n[{i}] 账号: {account_display}\n🔐 授权: {vip_status}"
        
    account_list += "\n------------------\n[b] 批量授权\n[d] 批量删除\n[q] 退出管理\n提示: 可回复 1,2 或 3-6 多选管理\n=================="
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
    
    selected_idxs, invalid_parts = parse_index_selection(response, count, allow_all=False)
    if invalid_parts:
        sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")
    
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
    sender.reply(f"""=====选择授权账号=====
请输入要授权的账号序号
------------------
{selection_tip('授权')}
==================""")
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    selected_idxs, invalid_parts = parse_index_selection(sel, len(all_accounts), allow_all=True)
    selected_accs = pick_accounts_by_indexes(all_accounts, selected_idxs)
    if selected_accs:
        if invalid_parts:
            sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")
        batch_auth_selected(selected_accs, account_remarks)
    else:
        sender.reply("❌ 无效的序号，请回复如 1,2 或 3-6")

def batch_delete_flow(all_accounts):
    sender.reply(f"""=====选择删除账号=====
请输入要删除的账号序号
------------------
{selection_tip('删除')}
==================""")
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    selected_idxs, invalid_parts = parse_index_selection(sel, len(all_accounts), allow_all=True)
    selected_accs = pick_accounts_by_indexes(all_accounts, selected_idxs)
    if selected_accs:
        if invalid_parts:
            sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")
        batch_delete_selected(selected_accs)
    else:
        sender.reply("❌ 无效的序号，请回复如 1,2 或 3-6")

def manage_single_account(account, account_remarks):
    try:
        account = str(account)
        token = AccountManager.get_token(account)
        if not token: token = ""
        accountVip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        account_display = get_account_display(account, remark)
        
        menu_items = """
[1] 授权账号
[2] 删除账号
[3] 修改备注"""
            
        sender.reply(f"""
=====账号详情=====
📱 账号: {account_display}
📝 备注: {remark if remark else "无"}
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
                    try: middleware.bucketSet(bucket='aihaiyan_auth', key=account, value=new_auth_time)
                    except: pass

                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('aihaiyan_remind_log', remind_key)
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
                    try: middleware.bucketDel(bucket='aihaiyan_token', key=account)
                    except: pass
                    try: middleware.bucketDel(bucket='aihaiyan_auth', key=account)
                    except: pass
                    if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                    sys_api.delete_env(account)
                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('aihaiyan_remind_log', remind_key)
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
    user_points, points_bucket = get_user_points()
    
    options = []
    idx = 1
    
    if config['zscoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': points_needed, 'curr': user_points})
        idx += 1
        
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
            out_trade_no = f"AHY_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
            formatted_money = f"{float(opt['amount']):.2f}"
            channel_name = "支付宝" if opt['channel'] == 'alipay' else ("微信支付" if opt['channel'] == 'wxpay' else "QQ钱包")
            
            qr_image_url, _ = _create_epay_qr(out_trade_no, opt['channel'], f"Auth_{months}M", formatted_money)
            
            sender.reply(f"=====等待支付=====\n💰 金额: {formatted_money}元\n💳 方式: {channel_name}\n📋 订单: {out_trade_no}\n------------------\n请在 180 秒内完成扫码支付 (完成后自动授权)\n回复\"q\"取消支付")
            sender.replyImage(qr_image_url)
            
            start_time = time.time()
            paid = False
            query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
            logger.debug(f"查单URL: ...act=order&pid={config['epay_pid']}&key=***&out_trade_no={out_trade_no}")
            
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
                    set_user_points(new_pt, points_bucket)
                except Exception as e:
                    sender.reply(f"❌ 扣除积分失败: {e}")
                    return False
                return True
            return False

    except:
        sender.reply("❌ 支付异常")
        return False

def batch_auth_selected(accounts, account_remarks):
    sender.reply(f"已选择 {len(accounts)} 个账号\n请输入授权月数，Q退出")
    m = get_user_input()
    if not m or not m.isdigit(): return
    months = int(m)
    if months <= 0: return
    
    count = len(accounts)
    total_money = Decimal(months) * config['zsVipmoney'] * count
    total_points = config['zscoin'] * months * count
    user_points, points_bucket = get_user_points()

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
            out_trade_no = f"AHY_BATCH_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
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
            try: set_user_points(new_pt, points_bucket)
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
            accountVip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
            new_date = empower(accountVip, months*30)
            try: middleware.bucketSet('aihaiyan_auth', account, new_date)
            except: pass

            token = AccountManager.get_token(account)
            curr_remark = account_remarks.get(account, "") if account_remarks else ""

            if token:
                sys_api.sync_env(token, account, curr_remark, new_date)

            today_date = datetime.now().date()
            for d in range(config['reminder_days'] + 1):
                remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                try: middleware.bucketDel('aihaiyan_remind_log', remind_key)
                except: pass
        except: pass

    sender.reply("✅ 批量授权完成")

def batch_delete_selected(accounts):
    preview = []
    account_remarks = RemarkManager.get_all_remarks(userid) if config['enable_remark'] else {}
    for account in accounts[:5]:
        account = str(account)
        preview.append(get_account_display(account, account_remarks.get(account, "")))
    more = f"\n...等 {len(accounts)} 个账号" if len(accounts) > 5 else ""
    sender.reply(f"=====确认批量删除=====\n已选择 {len(accounts)} 个账号\n{chr(10).join(preview)}{more}\n------------------\n确认删除请回复【确认删除】\n回复 q 取消\n==================")
    if get_user_input() == "确认删除":
        today_date = datetime.now().date()
        for account in accounts:
            try:
                 account = str(account)
                 AccountManager.remove_account(userid, account)
                 try: middleware.bucketDel(bucket='aihaiyan_token', key=account)
                 except: pass
                 try: middleware.bucketDel(bucket='aihaiyan_auth', key=account)
                 except: pass
                 if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                 sys_api.delete_env(account)
                 for d in range(config['reminder_days'] + 1):
                     remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                     try: middleware.bucketDel('aihaiyan_remind_log', remind_key)
                     except: pass
            except: pass
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts(force_report=False):
    users = middleware.bucketAllKeys(bucket='aihaiyan_user')
    if not users:
        if sender.isAdmin() and (force_report or usermessage in ['爱海盐清理', '清理爱海盐']):
            sender.reply("=====执行结果=====\n📭 暂无用户数据")
        return {
            "report_date": str(datetime.now().date()),
            "scanned_users": 0,
            "scanned_accounts": 0,
            "sent_notifications": 0,
            "cleaned_count": 0,
            "reminded_count": 0,
            "ck_expired_count": 0,
        }

    if sender.isAdmin() and (force_report or usermessage in ['爱海盐清理', '清理爱海盐']):
        sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n⚙️ 提醒天数: {config['reminder_days']}天\n⏳ 处理中...")

    scanned_accounts = 0
    cleaned_count = 0
    reminded_count = 0
    ck_expired_count = 0
    today_date = datetime.now().date()
    reminder_days_cfg = config['reminder_days']
    user_contexts = []
    ck_verify_tasks = []

    for user in users:
        try:
            accounts = AccountManager.get_accounts(user)
            if not accounts: continue
            
            try:
                user_sender = middleware.Sender(str(user))
            except: continue

            account_contexts = []

            for account in accounts:
                account = str(account)
                scanned_accounts += 1
                accountVip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
                
                if not accountVip:
                    account_contexts.append({
                        "account": account,
                        "accountVip": accountVip,
                        "days_diff": None,
                        "expiration_str": "",
                        "full_token": "",
                    })
                    continue
                else:
                    try:
                        expiration_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                        expiration_str = accountVip
                    except:
                        expiration_date = today_date - timedelta(days=1)
                        expiration_str = "日期错误"

                days_diff = (expiration_date - today_date).days
                full_token = AccountManager.get_token(account) if days_diff >= 0 else ""

                account_contexts.append({
                    "account": account,
                    "accountVip": accountVip,
                    "days_diff": days_diff,
                    "expiration_str": expiration_str,
                    "full_token": full_token,
                })

                if days_diff >= 0 and full_token:
                    ck_verify_tasks.append((str(user), account, full_token))

            user_contexts.append({
                "user": str(user),
                "sender": user_sender,
                "accounts": account_contexts,
            })

        except Exception:
            continue

    ck_verify_result = batch_verify_account_ck(ck_verify_tasks)

    for context in user_contexts:
        try:
            user = context["user"]
            user_sender = context["sender"]
            valid_accounts = []
            user_has_change = False
            account_remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}

            for account_item in context["accounts"]:
                account = account_item["account"]
                accountVip = account_item["accountVip"]
                days_diff = account_item["days_diff"]
                expiration_str = account_item["expiration_str"]

                if not accountVip:
                    valid_accounts.append(account)
                    continue

                if days_diff >= 0:
                    valid_accounts.append(account)
                    
                    full_token = account_item["full_token"]
                    is_ck_valid = ck_verify_result.get((str(user), str(account)), True) if full_token else True
                    
                    if not is_ck_valid:
                        ck_remind_key = f"ck_die_{user}_{account}_{today_date}"
                        has_ck_reminded = middleware.bucketGet('aihaiyan_remind_log', ck_remind_key)
                        
                        if not has_ck_reminded:
                            account_display = get_account_display(account, account_remarks.get(account, ""))
                            msg = f"""=====⚠️ 配置失效提醒=====
您的爱海盐配置可能已失效！
📱 账号: {account_display}
📅 授权到期: {expiration_str}
------------------
系统检测到该账号无法正常登录。
为保证挂机收益，请重新提交正确的配置并发送【{config['randomsigncommand']}】更新！
=================="""
                            if safe_send_message(user, msg, f"配置失效提醒 {user}-{account}"):
                                try: middleware.bucketSet('aihaiyan_remind_log', ck_remind_key, "1")
                                except: pass
                                ck_expired_count += 1
                    
                    if is_ck_valid and 0 <= days_diff <= reminder_days_cfg:
                        remind_key = f"{user}_{account}_{today_date}"
                        has_reminded = middleware.bucketGet('aihaiyan_remind_log', remind_key)
                        
                        if not has_reminded:
                            account_display = get_account_display(account, account_remarks.get(account, ""))
                            msg = f"""=====⏰ 到期提醒=====
您的爱海盐账号授权即将到期！
📱 账号: {account_display}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                            if safe_send_message(user, msg, f"到期提醒 {user}-{account}"):
                                try: middleware.bucketSet('aihaiyan_remind_log', remind_key, "1")
                                except: pass
                                reminded_count += 1
                    continue

                if days_diff < 0:
                    try:
                        sys_api.delete_env(account)
                        try: middleware.bucketDel(bucket='aihaiyan_token', key=account)
                        except: pass
                        try: middleware.bucketDel(bucket='aihaiyan_auth', key=account)
                        except: pass
                        if config['enable_remark']:
                            RemarkManager.delete_account_remark(user, account)
                    except: pass
                    
                    account_display = get_account_display(account, account_remarks.get(account, ""))
                    clean_msg = f"""=====🗑️ 过期清理通知=====
您的爱海盐账号授权已过期并清理。
📱 账号: {account_display}
📅 到期: {expiration_str}
------------------
相关配置已失效移除。
如需继续使用，请重新登录并授权。
=================="""
                    safe_send_message(user, clean_msg, f"过期清理通知 {user}-{account}")
                    cleaned_count += 1
                    user_has_change = True

            if user_has_change:
                if valid_accounts:
                    try: middleware.bucketSet(bucket='aihaiyan_user', key=str(user), value=str(valid_accounts))
                    except: pass
                else:
                    try: middleware.bucketDel(bucket='aihaiyan_user', key=str(user))
                    except: pass

        except Exception:
            continue

    if sender.isAdmin() and (force_report or usermessage in ['爱海盐清理', '清理爱海盐']):
        sender.reply(
            f"=====爱海盐维护完成=====\n"
            f"✅ 检测完成，共 {scanned_accounts} 个账号\n"
            f"📢 授权提醒: {reminded_count} 个\n"
            f"⚠️ CK失效通知: {ck_expired_count} 个\n"
            f"🗑️ 清理过期: {cleaned_count} 个\n"
            f"=================="
        )

    return {
        "report_date": str(today_date),
        "scanned_users": len(users),
        "scanned_accounts": scanned_accounts,
        "sent_notifications": reminded_count + ck_expired_count + cleaned_count,
        "cleaned_count": cleaned_count,
        "reminded_count": reminded_count,
        "ck_expired_count": ck_expired_count,
    }

def admin_auth_options():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足\n只有管理员可以执行授权操作")
        return
    
    sender.reply("""=====爱海盐管理员管理=====

[1] 一键授权所有用户
[2] 指定用户授权 (支持加减时间)
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
    if choice is None or choice.lower() == 'q':
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
        clean_expired_accounts(force_report=True)
    else:
        sender.reply("❌ 请输入有效的选项 (1-7)")

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
                account = str(account)
                token = AccountManager.get_token(account)
                if not token:
                    stats["no_token"] += 1
                vip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
                if not vip:
                    stats["unauthorized"] += 1
                    continue
                try:
                    vip_date = datetime.strptime(str(vip), "%Y-%m-%d").date()
                except:
                    stats["expired"] += 1
                    continue
                if vip_date < today:
                    stats["expired"] += 1
                else:
                    stats["authorized"] += 1
                    if (vip_date - today).days <= config['reminder_days']:
                        stats["expiring"] += 1
            except:
                pass
    return stats

def admin_overview():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return
    sender.reply("⏳ 正在统计数据，请稍候...")
    stats = collect_admin_stats()
    sender.reply(f"""=====爱海盐数据总览=====
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
    part = 1
    total_parts = 1
    chunks = []
    current = title
    for line in lines:
        add_text = "\n" + line
        if len(current) + len(add_text) + len(footer) + 20 > max_len and current != title:
            chunks.append(current)
            current = title
        current += add_text
    chunks.append(current)
    total_parts = len(chunks)
    for chunk in chunks:
        page_tip = f"\n-----第 {part}/{total_parts} 段-----" if total_parts > 1 else ""
        sender.reply(f"{chunk}{page_tip}\n{footer}")
        part += 1
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
            auth_count = 0
            unauth_count = 0
            expired_count = 0
            expiring_count = 0
            no_token_count = 0

            for account in accounts:
                account = str(account)
                total_accounts += 1
                if not AccountManager.get_token(account):
                    no_token_count += 1
                vip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
                if not vip:
                    unauth_count += 1
                    continue
                try:
                    vip_date = datetime.strptime(str(vip), "%Y-%m-%d").date()
                except:
                    expired_count += 1
                    continue
                if vip_date < today:
                    expired_count += 1
                else:
                    auth_count += 1
                    if (vip_date - today).days <= config['reminder_days']:
                        expiring_count += 1

            rows.append({
                "user": str(user),
                "count": len(accounts),
                "auth": auth_count,
                "unauth": unauth_count,
                "expired": expired_count,
                "expiring": expiring_count,
                "no_token": no_token_count
            })
        except:
            pass

    rows.sort(key=lambda x: x["count"], reverse=True)
    lines = [f"👥 用户数: {len(rows)}  📦 账号总数: {total_accounts}", "------------------"]
    for i, row in enumerate(rows, 1):
        extra = []
        if row["unauth"]:
            extra.append(f"未授权{row['unauth']}")
        if row["expired"]:
            extra.append(f"过期{row['expired']}")
        if row["expiring"]:
            extra.append(f"临期{row['expiring']}")
        if row["no_token"]:
            extra.append(f"缺配置{row['no_token']}")
        extra_text = f" ({' / '.join(extra)})" if extra else ""
        lines.append(f"[{i}] 用户: {row['user']}\n配置: {row['count']} 个  授权: {row['auth']} 个{extra_text}")

    send_long_admin_message("=====用户账号预览=====", lines)

def admin_find_account():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return
    sender.reply("""=====反查账号归属=====
请输入账号尾号/备注/用户ID
例如: 893 或 小号 或 wxid
回复 q 退出
==================""")
    keyword = get_user_input()
    if not keyword or keyword.lower() == 'q': return
    keyword = keyword.strip()

    matches = []
    users = AccountManager.get_all_users()
    for user in users:
        if keyword in str(user):
            user_match = True
        else:
            user_match = False
        remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
        for account in AccountManager.get_accounts(user):
            try:
                account = str(account)
                remark = remarks.get(account, "")
                safe_acc = mask_account(account)
                account_display = get_account_display(account, remark)
                vip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
                vip_st = '未授权' if not vip else str(vip)
                if user_match or keyword in account or keyword in safe_acc or (remark and keyword in remark):
                    matches.append(f"👤 用户: {user}\n📱 账号: {account_display}\n🔐 授权: {vip_st}")
            except:
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
    choice = get_user_input()
    if not choice or choice.lower() == 'q': return

    users = []
    if choice == '1':
        users = AccountManager.get_all_users()
        sender.reply(f"⚠️ 即将同步所有授权账号。\n确认请回复【确认同步】")
        if get_user_input() != "确认同步":
            sender.reply("✅ 已取消同步")
            return
    elif choice == '2':
        sender.reply("请输入用户ID(QQ号或wxid)，回复q退出")
        target_user = get_user_input()
        if not target_user or target_user.lower() == 'q': return
        users = [target_user.strip()]
    else:
        sender.reply("❌ 请输入有效选项")
        return

    today = str(datetime.now().date())
    success = 0
    skipped = 0
    failed = 0
    sender.reply("⏳ 正在同步，请稍候...")
    for user in users:
        remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
        for account in AccountManager.get_accounts(user):
            try:
                account = str(account)
                vip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
                token = AccountManager.get_token(account)
                if not vip or vip < today or not token:
                    skipped += 1
                    continue
                remark = remarks.get(account, "")
                if sys_api.sync_env(token, account, remark, vip):
                    success += 1
                else:
                    failed += 1
            except:
                failed += 1

    sender.reply(f"""=====同步完成=====
✅ 成功: {success}
⏸️ 跳过: {skipped}
❌ 失败: {failed}
==================""")

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
                accVip = middleware.bucketGet(bucket='aihaiyan_auth', key=account)
                new_vip = empower(accVip, days)
                try: middleware.bucketSet(bucket='aihaiyan_auth', key=account, value=new_vip)
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
        accVip = middleware.bucketGet(bucket='aihaiyan_auth', key=acc)
        vip_st = '未授权' if not accVip else f"已授权({accVip})"
        rem = account_remarks.get(acc, "")
        account_display = get_account_display(acc, rem)
        msg += f"\n[{i}] {account_display} - {vip_st}"
    msg += "\n------------------\n回复 a 操作所有账号\n支持单选/多选/区间，如 1,2 或 3-6\n回复 q 退出\n=================="
    sender.reply(msg)
    
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    selected_idxs, invalid_parts = parse_index_selection(sel, len(target_accounts), allow_all=True)
    selected_accs = pick_accounts_by_indexes(target_accounts, selected_idxs)
    if not selected_accs:
        return sender.reply("❌ 序号无效，请回复如 1,2 或 3-6")
    if invalid_parts:
        sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")

    sender.reply(f"已选择 {len(selected_accs)} 个账号\n请输入改变的天数(正数增加，负数如 -10 扣除):")
    d_str = get_user_input()
    if not d_str: return
    try: days = int(d_str)
    except: return sender.reply("❌ 无效天数")

    success = 0
    latest_dates = []
    for acc in selected_accs:
        acc = str(acc)
        accVip = middleware.bucketGet(bucket='aihaiyan_auth', key=acc)
        new_vip = empower(accVip, days)
        try: middleware.bucketSet(bucket='aihaiyan_auth', key=acc, value=new_vip)
        except: pass
        
        token = AccountManager.get_token(acc)
        remark = account_remarks.get(acc, "")
        if token:
            sys_api.sync_env(token, acc, remark, new_vip)
        success += 1
        latest_dates.append(new_vip)

    date_tip = latest_dates[0] if len(set(latest_dates)) == 1 else "多个日期"
    sender.reply(f"✅ 已操作 {success} 个账号 {days} 天\n⏰ 最新到期: {date_tip}")

def show_tutorial():
    panel_name = '青龙' if config['panel_type'] == 'qinglong' else '呆呆'
    sender.reply(f"""
=====爱海盐管理插件教程=====
当前模式: 🌐 提交至{panel_name}面板

1️⃣ {config['randomsigncommand']}
   发送 手机号#密码 配置自动覆盖更新。

2️⃣ {config['randomquerycommand']}
   查询存活状态与当前脚本阅读/抽奖记录。

3️⃣ {config['randommanagecommand']}
   全新支付接口，极简扫码无需挂机，付完全自动回调开通。

4️⃣ 爱海盐授权
   管理员总管理：授权、总览、配置预览、反查、同步、清理。

5️⃣ 爱海盐清理 / 爱海盐广播
   自动维护与消息分发。
==================""")

# ===================== 主入口 =====================
try:
    if is_cron_trigger():
        report_data = clean_expired_accounts()
        send_daily_admin_report(report_data)
    
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
    elif usermessage in ['爱海盐清理', '清理爱海盐']:
        report_data = clean_expired_accounts()
        send_daily_admin_report(report_data, force_send=True, notify_status=True)
    elif '广播' in usermessage or '通知' in usermessage:
        notify_authorized_users()
    elif '授权' in usermessage:
        admin_auth_options()
    elif '教程' in usermessage:
        show_tutorial()

except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")
