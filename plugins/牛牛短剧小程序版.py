# [rule: ^(小牛牛)(登录|登陆)$|^登(录|陆)(小牛牛)$|^(小牛牛)(查询|管理)$|^(查询|管理)(小牛牛)$|^小牛牛清理$|^小牛牛授权$|^小牛牛教程$|^小牛牛通知 ?(.*)$|^清理小牛牛$|^小牛牛广播 ?(.*)$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 10 */5 * *]
# [public: true]
# [title: 牛牛短剧小程序版]
# [open_source: false]
# [class: 工具类]
# [version: 1.4]
# [price: 25.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 小牛牛提交计费版 <br>1. 指令：小牛牛登录、小牛牛管理、小牛牛查询、小牛牛授权 1.2修复部分号更新ck新增账号bug <br>2. 支持批量登录，仅需token即可登录。<br>3. 售后群1003974618。 售后联系：QQ 8165799<br>]

import re
import ast
from datetime import datetime, timedelta
import middleware
import urllib.parse
from urllib.parse import unquote, quote
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
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('xnn_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 
MAINTENANCE_CK_MAX_WORKERS = 8

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())
usermessage = sender.getMessage()

_RUNTIME_BUCKET = "plugin_push_runtime"
_RUNTIME_KEY = "牛牛短剧小程序版"
try:
    current_imtype = str(sender.getImtype() or "")
except:
    current_imtype = ""
if current_imtype and current_imtype.lower() not in ["fake", "cron"]:
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_sender", str(senderID))
    except: pass
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype", current_imtype)
    except: pass
    if userid and userid.lower() not in ["none", "null"]:
        try: middleware.bucketSet(bucket="dd_xnn_sender", key=userid, value=str(senderID))
        except: pass
        try: middleware.bucketSet(bucket="dd_xnn_imtype", key=userid, value=current_imtype)
        except: pass

# ===================== 插件配置参数 =====================
# [param: {"required":true,"key":"dd_xnn.panel_type","bool":false,"placeholder":"qinglong/daidai","name":"对接面板类型","desc":"qinglong=青龙面板 daidai=呆呆面板"}]
# [param: {"required":true,"key":"dd_xnn.dd_xnn_qlname","bool":false,"placeholder":"Host丨ClientID/AppKey丨Secret","name":"对接系统配置","desc":"青龙:URL丨ID丨Secret 呆呆:URL丨Key丨Secret"}]
# [param: {"required":true,"key":"dd_xnn.dd_xnn_osname","bool":false,"placeholder":"默认:niuniuTOKENS","name":"系统变量名","desc":"系统容器内变量名(默认为niuniuTOKENS)"}]
# [param: {"required":false,"key":"dd_xnn.epay_alipay","bool":true,"name":"易支付支付宝","desc":"启用易支付支付宝通道收款"}]
# [param: {"required":false,"key":"dd_xnn.epay_wxpay","bool":true,"name":"易支付微信","desc":"启用易支付微信通道收款"}]
# [param: {"required":false,"key":"dd_xnn.epay_qqpay","bool":true,"name":"易支付QQ","desc":"启用易支付QQ通道收款"}]
# [param: {"required":false,"key":"dd_xnn.epay_url","bool":false,"placeholder":"如 http://pay.xxx.com/","name":"易支付网关","desc":"易支付接口网关地址(需带http及结尾/)"}]
# [param: {"required":false,"key":"dd_xnn.epay_pid","bool":false,"placeholder":"","name":"易支付商户ID","desc":"易支付的PID"}]
# [param: {"required":false,"key":"dd_xnn.epay_key","bool":false,"placeholder":"","name":"易支付商户密钥","desc":"易支付的KEY密钥"}]
# [param: {"required":true,"key":"dd_xnn.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_xnn.hhttVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_xnn.hhttcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"dd_xnn.show_point_status","bool":true,"placeholder":"","name":"显示钱包状态","desc":"是否在查询结果中显示钱包金额"}]
# [param: {"required":true,"key":"dd_xnn.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统"}]
# [param: {"required":true,"key":"dd_xnn.enable_proxy","bool":true,"placeholder":"True/False","name":"是否启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_xnn.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_xnn.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"dd_xnn.enable_remark","bool":true,"placeholder":"True/False","name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"dd_xnn.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]

def getusercontent():
    """获取插件完整配置"""
    panel_type = middleware.bucketGet('dd_xnn', 'panel_type') or 'qinglong'
    panel_type = panel_type.lower()
    
    dd_hhtt_qlname = middleware.bucketGet('dd_xnn', 'dd_xnn_qlname') or ''
    dd_hhtt_osname = middleware.bucketGet('dd_xnn', 'dd_xnn_osname') or 'niuniuTOKENS'
    
    if not dd_hhtt_qlname:
        sender.reply("❌ 配置错误：请在插件配置中填写【对接系统配置】(面板信息)。")
        exit(0)
    
    dd_managecommand = middleware.bucketGet('dd_xnn', 'dd_managecommand') or '小牛牛管理'
    dd_querycommand = middleware.bucketGet('dd_xnn', 'dd_querycommand') or '小牛牛查询'
    dd_signcommand = middleware.bucketGet('dd_xnn', 'dd_signcommand') or '小牛牛登录'
    zsm = middleware.bucketGet('dd_xnn', 'zsm') or ''
    
    enable_proxy = middleware.bucketGet('dd_xnn', 'enable_proxy') or 'false'
    enable_proxy = enable_proxy.lower() == 'true'
    proxy_pool_url = middleware.bucketGet('dd_xnn', 'proxy_pool_url') or ''
    
    points_bucket = middleware.bucketGet('dd_xnn', 'points_bucket') or 'dd_sign_points'
    
    enable_remark = middleware.bucketGet('dd_xnn', 'enable_remark') or 'false'
    enable_remark = enable_remark.lower() == 'true'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    xyVipmoney = Decimal(middleware.bucketGet('dd_xnn', 'hhttVipmoney') or '0')
    xycoin = int(middleware.bucketGet('dd_xnn', 'hhttcoin') or '0')
    
    show_point_status = middleware.bucketGet('dd_xnn', 'show_point_status') or 'false'
    show_point_status = show_point_status.lower() == 'true'
    
    use_ma_pay = middleware.bucketGet('dd_xnn', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'

    epay_url = middleware.bucketGet('dd_xnn', 'epay_url') or ''
    epay_pid = middleware.bucketGet('dd_xnn', 'epay_pid') or ''
    epay_key = middleware.bucketGet('dd_xnn', 'epay_key') or ''
    epay_alipay = (middleware.bucketGet('dd_xnn', 'epay_alipay') or 'true').lower() == 'true'
    epay_wxpay = (middleware.bucketGet('dd_xnn', 'epay_wxpay') or 'false').lower() == 'true'
    epay_qqpay = (middleware.bucketGet('dd_xnn', 'epay_qqpay') or 'false').lower() == 'true'
    
    reminder_days = int(middleware.bucketGet('dd_xnn', 'reminder_days') or '2')

    return {
        'panel_type': panel_type,
        'dd_hhtt_osname': dd_hhtt_osname,
        'dd_hhtt_qlname': dd_hhtt_qlname,
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
        'xyVipmoney': xyVipmoney,
        'xycoin': xycoin,
        'show_point_status': show_point_status,
        'use_ma_pay': use_ma_pay,
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
        for owner in middleware.bucketAllKeys(bucket='dd_xnn_user'):
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

def send_user_notice(user_id, msg, title="牛牛短剧小程序版通知", preferred_imtypes=None):
    user_id = str(user_id or "").strip()
    if not user_id:
        return False

    imtype_candidates = []
    for item in preferred_imtypes or []:
        item = str(item or "").strip()
        if item:
            imtype_candidates.append(item)
    try:
        imtype_candidates.append(str(middleware.bucketGet(bucket="dd_xnn_imtype", key=user_id) or ""))
    except:
        pass
    try:
        imtype_candidates.append(str(sender.getImtype() or ""))
    except:
        pass
    try:
        imtype_candidates.append(str(middleware.bucketGet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype") or ""))
    except:
        pass
    if user_id.isdigit():
        imtype_candidates.extend(["qq", "qb"])

    last_error = ""
    valid_imtypes = [x for x in imtype_candidates if x and x.lower() not in ["fake", "cron"]]
    for imtype in list(dict.fromkeys(valid_imtypes)):
        for func_name in ["Push", "push"]:
            push_func = getattr(middleware, func_name, None)
            if not callable(push_func):
                continue
            try:
                push_func(imtype, "", user_id, title, msg)
                try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype", imtype)
                except: pass
                return True
            except Exception as e:
                last_error = f"{func_name}({imtype},{user_id}): {str(e) or e.__class__.__name__}"
                logger.warning(f"Push发送失败 {user_id}: {last_error}")

    targets = []
    try:
        saved_sender = middleware.bucketGet(bucket="dd_xnn_sender", key=user_id)
        if saved_sender:
            targets.append(str(saved_sender))
    except:
        pass
    try:
        runtime_sender = middleware.bucketGet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_sender")
        if runtime_sender:
            targets.append(str(runtime_sender))
    except:
        pass
    targets.append(user_id)

    method_names = ["Reply", "reply", "ReplyMarkdown", "replyMarkdown", "send", "replyText", "sendText", "sendMsg", "sendMessage"]
    for target in list(dict.fromkeys([x for x in targets if x])):
        try:
            target_sender = middleware.Sender(target)
        except Exception as e:
            last_error = f"Sender({target})初始化失败: {str(e) or e.__class__.__name__}"
            continue
        for method_name in method_names:
            method = getattr(target_sender, method_name, None)
            if not callable(method):
                continue
            try:
                method(msg)
                return True
            except Exception as e:
                last_error = f"{method_name}: {str(e) or e.__class__.__name__}"

    if last_error:
        logger.warning(f"消息发送失败 {user_id}: {last_error}")
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
    for arg in [None, []]:
        try:
            if arg is None:
                notify_func(msg)
            else:
                notify_func(msg, arg)
            return True
        except TypeError:
            try:
                notify_func(msg)
                return True
            except:
                pass
        except Exception as e:
            logger.warning(f"框架管理员推送失败: {e}")
    return False

def send_daily_admin_report(report_data, force_send=False, notify_status=False):
    report_date = str(report_data.get('report_date') or datetime.now().date())
    report_key = f"daily_admin_report_{report_date}"
    if not force_send and middleware.bucketGet('dd_xnn_runtime', report_key):
        if notify_status:
            sender.reply("ℹ️ 今日管理员汇总已发送过。")
        return False

    msg = (
        "=====小牛牛维护完成=====\n"
        f"✅ 检测完成，共 {report_data.get('scanned_accounts', 0)} 个账号\n"
        f"🌐 面板变量: {report_data.get('panel_scanned_accounts', 0)} 个\n"
        f"📣 发送通知: {report_data.get('sent_notifications', 0)} 条\n"
        f"⚠️ CK失效通知: {report_data.get('ck_expired_count', 0)} 个\n"
        f"🗑️ 清理过期: {report_data.get('cleaned_count', 0)} 个\n"
        "=================="
    )

    if send_message_to_framework_admins(msg):
        try: middleware.bucketSet('dd_xnn_runtime', report_key, "framework")
        except: pass
        if notify_status:
            sender.reply("✅ 管理员汇总已发送（框架自动管理员）")
        return True
    if notify_status:
        sender.reply("❌ 管理员汇总发送失败，请检查框架默认管理员配置。")
    return False

def empower(empowertime, days):
    try:
        today_date = datetime.now().date()
        if not empowertime or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            delayed_date = empower_date + timedelta(days=days)
        return str(delayed_date)
    except Exception as e:
        logger.error(f"授权时间计算失败: {e}")
        raise Exception(f"授权时间计算失败: {e}")

def get_safe_account(account):
    acc_str = str(account)
    if len(acc_str) == 11 and acc_str.isdigit():
        return acc_str[:3] + "****" + acc_str[-4:]
    return acc_str

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

def batch_verify_account_ck(tasks, max_workers=MAINTENANCE_CK_MAX_WORKERS):
    if not tasks:
        return {}

    result_map = {}
    worker_count = min(max_workers, len(tasks))

    def _verify_one(task):
        if isinstance(task, dict):
            user = task.get('user', '')
            account = task.get('account', '')
            token = task.get('token', '')
            source = task.get('source', 'local')
        else:
            user, account, token = task
            source = 'local'
        token_hash = hashlib.md5(str(token or '').encode()).hexdigest() if token else f"{source}_{user}_{account}"
        if not token:
            return (source, user, account, token_hash, True)
        try:
            time.sleep(random.uniform(0.1, 0.35))
            client = XiaoNiuClient(token)
            return (source, user, account, token_hash, client.verify_ck())
        except Exception as e:
            logger.warning(f"CK校验异常，按有效处理: {user}-{account} - {e}")
            return (source, user, account, token_hash, True)

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(_verify_one, task) for task in tasks]
        for future in as_completed(futures):
            try:
                source, user, account, token_hash, is_valid = future.result()
                result_map[(str(source), str(user), str(account), str(token_hash))] = is_valid
                result_map[(str(user), str(account))] = is_valid
            except Exception as e:
                logger.warning(f"CK校验结果读取失败: {e}")
    return result_map

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
    submit_params = dict(base_params)
    submit_params['sign'] = _build_epay_sign(base_params, config['epay_key'])
    submit_params['sign_type'] = 'MD5'

    try:
        mapi_params = dict(base_params)
        mapi_params['clientip'] = '127.0.0.1'
        mapi_params['sign'] = _build_epay_sign(mapi_params, config['epay_key'])
        mapi_params['sign_type'] = 'MD5'
        resp = requests.post(config['epay_url'].rstrip('/') + '/mapi.php', data=mapi_params, timeout=15, verify=False)
        data = resp.json()
        if int(data.get('code', 0)) == 1:
            native_qr = data.get('qrcode', '') or data.get('payurl', '') or data.get('urlscheme', '')
            if native_qr:
                return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(native_qr, safe='')}", native_qr
    except Exception as e:
        logger.warning(f"易支付mapi创建失败，使用submit链接: {e}")

    raw_query = urllib.parse.urlencode(submit_params)
    pay_url = config['epay_url'].rstrip('/') + '/submit.php?' + raw_query
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(pay_url, safe='')}", pay_url

def parse_index_selection(text, total_count, allow_all=True):
    text = str(text or "").strip().lower()
    if allow_all and text == 'a':
        return list(range(1, total_count + 1)), []
    selected = []
    invalid = []
    for part in re.split(r'[,，\\s]+', text):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                start, end = [int(x.strip()) for x in part.split('-', 1)]
                if start > end:
                    start, end = end, start
                for idx in range(start, end + 1):
                    if 1 <= idx <= total_count:
                        selected.append(idx)
                    else:
                        invalid.append(str(idx))
            except:
                invalid.append(part)
        else:
            try:
                idx = int(part)
                if 1 <= idx <= total_count:
                    selected.append(idx)
                else:
                    invalid.append(part)
            except:
                invalid.append(part)
    return list(dict.fromkeys(selected)), invalid

def pick_accounts_by_indexes(accounts, indexes):
    result = []
    for idx in indexes:
        try:
            result.append(accounts[idx - 1])
        except:
            pass
    return result

def parse_panel_xnn_remark(remarks):
    try:
        remarks = str(remarks or '')
        user_match = re.search(r'用户[:：]\s*([^丨|\s]+)', remarks)
        id_match = re.search(r'ID[:：]\s*([^丨|\s]+)', remarks)
        date_match = re.search(r'到期[:：]\s*(\d{4}-\d{2}-\d{2})', remarks)
        remark_match = re.search(r'备注[:：]\s*([^丨|]+)', remarks)
        return {
            'user': user_match.group(1).strip() if user_match else '',
            'account': id_match.group(1).strip() if id_match else '',
            'auth_date': date_match.group(1).strip() if date_match else '',
            'remark': remark_match.group(1).strip() if remark_match else ''
        }
    except:
        return {'user': '', 'account': '', 'auth_date': '', 'remark': ''}

def split_env_tokens(value):
    value = str(value or '').strip()
    if not value:
        return []
    tokens = [x.strip() for x in re.split(r'[\n&@]', value) if x.strip()]
    return list(dict.fromkeys(tokens))

def find_local_account_by_token(token):
    token = str(token or '').strip()
    if not token:
        return '', ''
    for owner in AccountManager.get_all_users():
        try:
            for account in AccountManager.get_accounts(owner):
                local_token = AccountManager.get_token(account)
                if local_token and str(local_token).strip() == token:
                    return str(owner), str(account)
        except:
            continue
    return '', ''

def collect_panel_ck_tasks():
    tasks = []
    if not getattr(sys_api, 'enabled', False):
        return tasks
    try:
        envs = sys_api.get_all_envs()
    except Exception as e:
        logger.warning(f"读取面板变量失败: {e}")
        return tasks

    seen = set()
    for env in envs:
        try:
            if env.get('name') != config['dd_hhtt_osname']:
                continue
            value = env.get('value') or ''
            remarks = env.get('remarks') or env.get('remark') or ''
            parsed = parse_panel_xnn_remark(remarks)
            tokens = split_env_tokens(value)
            for idx, token in enumerate(tokens, 1):
                owner = parsed.get('user') or ''
                account = parsed.get('account') or ''
                if not owner or not account:
                    local_owner, local_account = find_local_account_by_token(token)
                    owner = owner or local_owner
                    account = account or local_account
                if not account:
                    account = hashlib.md5(token.encode()).hexdigest()[:12]
                task_key = hashlib.md5(token.encode()).hexdigest()
                dedupe = (task_key, owner, account)
                if dedupe in seen:
                    continue
                seen.add(dedupe)
                tasks.append({
                    'source': 'panel',
                    'user': str(owner or ''),
                    'account': str(account),
                    'token': token,
                    'auth_date': parsed.get('auth_date') or '',
                    'remarks': remarks,
                    'env_id': env.get('id') if env.get('id') is not None else env.get('_id'),
                    'index': idx
                })
        except Exception as e:
            logger.warning(f"解析面板变量失败: {e}")
    return tasks

# ===================== 核心逻辑类 (小牛牛专属) =====================
class XiaoNiuClient:
    def __init__(self, token_str):
        self.token = unquote(token_str.strip())
        self.base_url = "https://api.tianjinzhitongdaohe.com"
        
        self.headers = {
            "Host": "api.tianjinzhitongdaohe.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; M2012K11AC Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.40.2420(0x28002851) NetType/WIFI Language/zh_CN miniProgram/wxcb95401f250e9a53",
            "xweb_xhr": "1",
            "token": self.token,
            "Accept": "*/*",
            "Referer": "https://servicewechat.com/wxcb95401f250e9a53/19/page-frame.html",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9"
        }

    def _get_proxies(self):
        proxies = None
        if config['enable_proxy'] and config['proxy_pool_url']:
            try:
                res = requests.get(config['proxy_pool_url'], timeout=3)
                if res.status_code == 200:
                    proxy_ip = res.text.strip()
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', proxy_ip)
                    if match:
                        proxy_ip = match.group(1)
                        proxies = {'http': f"http://{proxy_ip}", 'https': f"http://{proxy_ip}"}
            except Exception as e:
                logger.warning(f"代理获取失败: {e}")
        return proxies

    def check_info(self):
        """校验登录信息，调用接口组装最终结果"""
        proxies = self._get_proxies()
        
        # 1. 查用户信息和手机号（智能获取手机号做为主键）
        user_url = f"{self.base_url}/sqx_fast/app/user/selectUserById"
        try:
            res_user = requests.get(user_url, headers=self.headers, verify=False, proxies=proxies, timeout=10)
            rj_user = res_user.json()
            if rj_user.get("code") != 0:
                raise Exception(rj_user.get("msg", "Token无效或已过期"))
            
            data = rj_user.get("data", {})
            phone = data.get("phone", "")
            if not phone:
                uid = str(data.get("id") or data.get("userId") or "")
                if uid:
                    phone = f"UID_{uid}"
                else:
                    phone = hashlib.md5(self.token.encode()).hexdigest()[:11]
                
            day_num = data.get("lookDayVideoNum")
            ok_num = data.get("okLookVideoNum")
            watched_today = 0
            if day_num is not None: watched_today = int(day_num)
            elif ok_num is not None: watched_today = int(ok_num)
            
        except Exception as e:
            raise Exception(f"验证失败: {str(e)}")
            
        # 2. 查金币
        gold_url = f"{self.base_url}/sqx_fast/app/integral/selectByUserId"
        gold = 0
        try:
            res_gold = requests.get(gold_url, headers=self.headers, verify=False, proxies=proxies, timeout=10)
            rj_gold = res_gold.json()
            if rj_gold.get("code") == 0:
                gold = rj_gold.get("data", {}).get("integralNum", 0)
        except:
            pass

        safe_phone = get_safe_account(phone)
                
        return {
            "nickname": f"小牛牛_{safe_phone}",
            "phone": phone,
            "gold": gold,
            "watched_today": watched_today,
            "acc_key": phone,
            "final_token": self.token
        }

    def verify_ck(self):
        try:
            self.check_info()
            return True
        except Exception as e:
            err = str(e)
            if any(key in err for key in ["token失效", "重新登录", "Token无效", "已过期", "无效", "失效", "验证失败"]):
                return False
            logger.warning(f"小牛牛CK校验异常，暂按有效处理: {err}")
            return True

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='dd_xnn_remarks', key=f'{user_id}_{account_id}')
            return str(remark_data) if remark_data else ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = str(remark).strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='dd_xnn_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
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
            middleware.bucketDel(bucket='dd_xnn_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket='dd_xnn_user', key=str(user_id))
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
                middleware.bucketSet(bucket='dd_xnn_user', key=str(user_id), value=str(accounts))
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
                    middleware.bucketSet(bucket='dd_xnn_user', key=str(user_id), value=str(accounts))
                else:
                    middleware.bucketDel(bucket='dd_xnn_user', key=str(user_id))
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(account, token):
        try:
            encrypted_token = encrypt_token(str(token))
            middleware.bucketSet(bucket='dd_xnn_token', key=str(account), value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_token(account):
        try:
            enc = middleware.bucketGet(bucket='dd_xnn_token', key=str(account))
            return decrypt_token(enc) if enc else None
        except: return None

    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket='dd_xnn_user')
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
        ql_config = config['dd_hhtt_qlname']
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
                url = f"{self.QLurl}/api/envs?keyword={config['dd_hhtt_osname']}&page_size=9999"
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
                if env.get('name') != config['dd_hhtt_osname']: continue
                
                # 兼容青龙新旧版本的 ID 类型
                env_id = env.get('id') if env.get('id') is not None else env.get('_id')
                
                # 1. 核心嗅探：精准匹配藏在备注里的完整手机号 ID 锚点
                if env.get('remarks') and f'ID:{phone}' in env.get('remarks'): 
                    return env_id
                    
                # 2. 降级嗅探：如果没找到精确的 ID 锚点（可能是历史测试号），去模糊匹配备注里是否包含该手机号
                if env.get('remarks') and phone in env.get('remarks'):
                    return env_id
                    
                # 3. 最终嗅探：如果连手机号都没找到，去精确匹配旧的 Token（value），证明就是这个变量
                if token and env.get('value'):
                    env_val = env.get('value').strip()
                    input_val = str(token).strip()
                    if env_val == input_val:
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
            
            # 安全脱敏显示备注
            safe_phone = get_safe_account(phone)
            remarks_parts = [f'小牛牛:{safe_phone}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            
            # 埋入隐藏的 ID:手机号 锚点供续费时精准定位
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{phone}', '小牛牛提交'])
            final_remark = '丨'.join(remarks_parts)

            if self.panel_type == 'daidai':
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                if env_id is not None:
                    # 使用f-string绝对隔离int拼接问题
                    url = f"{self.QLurl}/api/envs/{env_id}"
                    data = {"name": config['dd_hhtt_osname'], "value": token, "remarks": final_remark}
                    res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code == 200:
                        try: requests.put(f"{self.QLurl}/api/envs/{env_id}/enable", headers=headers, timeout=5, verify=False)
                        except: pass
                    else: return False
                else:
                    url = f"{self.QLurl}/api/envs"
                    data = {"name": config['dd_hhtt_osname'], "value": token, "remarks": final_remark}
                    res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code != 200: return False
            else:
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                url = f"{self.QLurl}/open/envs"
                if env_id is not None:
                    data = {"value": token, "name": config['dd_hhtt_osname'], "remarks": final_remark}
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
                    data = [{"value": token, "name": config['dd_hhtt_osname'], "remarks": final_remark}]
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
        
        accountVip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        if not accountVip:
            auth_time = "无"
        elif accountVip <= today_time:
            auth_time = f"{accountVip} (已过期)"
        else:
            auth_time = accountVip

        safe_display = get_safe_account(account)
        remark_display = f" [{remark}]" if remark else ""

        if accountVip and accountVip > today_time:
            try:
                if not full_token or len(full_token) < 10:
                    raise Exception("凭证异常或为空")
                
                client = XiaoNiuClient(full_token)
                info = client.check_info()
                
                nickname = info.get("nickname", safe_display)
                gold = info.get("gold", "0")
                watched_today = info.get("watched_today", "未知")
                
                account_info = f"""
=====小牛牛详情=====
🚀 小程序: 小牛牛优选 (天津志同道合)
👤 账号: {nickname}{remark_display}
💰 当前金币: {gold}
🎬 视频进度: {watched_today}/20
⏰ 授权到期: {auth_time}"""
                return account_info.strip()
            except Exception as e:
                return f"""
=====小牛牛查询异常=====
📱 账号: {safe_display}
❌ 错误: {str(e)[:50]}
=================="""
        else:
            return f"""
=====小牛牛状态=====
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

        menu = "=====小牛牛查询====="
        for i, acc in enumerate(accounts, 1):
            acc = str(acc)
            remark = account_remarks.get(acc, "") if config['enable_remark'] else ""
            safe_acc = get_safe_account(acc)
            vip = middleware.bucketGet(bucket='dd_xnn_auth', key=acc)
            if not vip:
                vip_tag = '⚠️未授权'
            elif vip < today_time:
                vip_tag = '❌已过期'
            else:
                vip_tag = f'✅{vip}'
            remark_disp = f" [{remark}]" if remark else ""
            menu += f"\n[{i}] {safe_acc}{remark_disp} {vip_tag}"
        menu += f"\n------------------\n[a] 查询全部\n支持单选/多选/区间，如 1,2 或 3-6\n回复q退出\n=================="
        sender.reply(menu)

        sel = get_user_input(timeout=60)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已退出")
            return

        if sel.lower() == 'a':
            target_accounts = list(enumerate(accounts, 1))
        else:
            selected_idxs, invalid_parts = parse_index_selection(sel, total_count, allow_all=True)
            if not selected_idxs:
                sender.reply("❌ 序号无效，请回复如 1,2 或 3-6")
                return
            if invalid_parts:
                sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")
            target_accounts = [(idx, accounts[idx - 1]) for idx in selected_idxs]

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
    match = re.search(r'(小牛牛广播|小牛牛通知) ?(.*)', usermessage)
    if match:
        content = match.group(2).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：小牛牛通知 系统维护中")
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
                vip_date = middleware.bucketGet(bucket='dd_xnn_auth', key=str(acc))
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                try:
                    send_user_notice(uid, f"📢 【小牛牛管理员通知】\n\n{content}")
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
=====小牛牛 登录=====
当前模式: 🌐 提交至面板
------------------
👉 请按格式发送抓包数据 (Token)：
------------------
支持批量提交，一行一个
系统将尽力自动匹配旧号实现无损继承授权!
(可直接复制带星号旧账号升级：旧号#新Token)
(示例：10f****ab84#eyJhbG...)
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
        
        # 获取用户已有账号以供智能匹配
        existing_accounts = AccountManager.get_accounts(userid)
        hash_accounts = [acc for acc in existing_accounts if not (acc.isdigit() and len(acc) == 11)]

        for line in token_lines:
            try:
                token_val = line.strip()
                explicit_old_id = None
                if '#' in line:
                    parts = line.split('#', 1)
                    explicit_old_id = parts[0].strip()
                    token_val = parts[1].strip() # 兼容带有老格式的输入
                
                if len(token_val) < 10:
                    sender.reply(f"❌ 格式错误: {line[:15]}... (请输入有效的Token)")
                    continue
                
                # 支持用户直接从面板复制带星号的脱敏账号进行匹配
                if explicit_old_id and '*' in explicit_old_id:
                    matched_accs = [acc for acc in existing_accounts if get_safe_account(acc) == explicit_old_id]
                    if matched_accs:
                        explicit_old_id = matched_accs[0]

                client = XiaoNiuClient(token_val)
                info_res = client.check_info()
                
                nick = info_res['nickname']
                final_token_str = info_res['final_token']
                new_acc_id = str(info_res['acc_key'])
                
                old_acc_id = explicit_old_id
                if not old_acc_id and len(hash_accounts) == 1 and new_acc_id not in existing_accounts:
                    old_acc_id = hash_accounts[0]

                # 核心：无损迁移授权数据到真实的新账号ID上
                if old_acc_id and old_acc_id in existing_accounts and old_acc_id != new_acc_id:
                    accountVip = middleware.bucketGet(bucket='dd_xnn_auth', key=str(old_acc_id))
                    old_remark = RemarkManager.get_account_remark(userid, old_acc_id) if config['enable_remark'] else ""
                    
                    if accountVip:
                        # 转移数据至新账号
                        middleware.bucketSet(bucket='dd_xnn_auth', key=str(new_acc_id), value=str(accountVip))
                        if config['enable_remark'] and old_remark:
                            RemarkManager.set_account_remark(userid, new_acc_id, old_remark)
                        
                        # 清理旧哈希账号的残留痕迹
                        AccountManager.remove_account(userid, old_acc_id)
                        try: middleware.bucketDel(bucket='dd_xnn_token', key=str(old_acc_id))
                        except: pass
                        try: middleware.bucketDel(bucket='dd_xnn_auth', key=str(old_acc_id))
                        except: pass
                        if config['enable_remark']:
                            RemarkManager.delete_account_remark(userid, old_acc_id)
                        sys_api.delete_env(old_acc_id)
                        
                        o_safe = get_safe_account(old_acc_id)
                        n_safe = get_safe_account(new_acc_id)
                        sender.reply(f"🔄 [身份升级] 发现更稳定的账号主体！已安全将旧身份 [{o_safe}] 的授权平滑转移至 [{n_safe}]")
                
                process_account_binding(final_token_str, new_acc_id, nick, remark) 
            except Exception as ex:
                sender.reply(f"❌ 登录失败 ({line[:15]}...): {str(ex)}")
            
    except Exception as e:
        logger.error(f"绑定失败: {e}")
        sender.reply(f"❌ 绑定失败: {e}")

def process_account_binding(full_token, unique_id, nickname, remark=""):
    try:
        account = str(unique_id)
        
        accountVip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
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
        safe_display = get_safe_account(account)

        is_new = AccountManager.add_account(userid, account)
        if is_new:
            try: middleware.bucketSet(bucket='dd_xnn_bind_date', key=account, value=str(datetime.now().date()))
            except: pass
        AccountManager.update_account_token(account, full_token)
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account, remark)
        
        ql_msg = ""
        if is_authorized:
            if sys_api.sync_env(full_token, account, remark, accountVip, owner_user_id=userid):
                ql_msg = "\n🌐 状态: ✅ 系统已同步更新"
            else:
                ql_msg = "\n🌐 状态: ❌ 系统同步失败"
        else:
            ql_msg = "\n🌐 状态: ⏸️ 未授权暂不同步"

        sender.reply(f"""
=====小牛牛账号更新=====
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
    count = 1
    account_list = "======我的小牛牛账号====="
    today_time = str(datetime.now().date())
    
    for account in accounts:
        account = str(account)
        accountVip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
        if not accountVip: vip_status = '⚠️ 未授权'
        elif accountVip < today_time: vip_status = '❌ 已过期'
        else: vip_status = f'✅ {accountVip}'
        
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        remark_display = f" - {remark}" if remark else ""
        
        safe_display = get_safe_account(account)
        
        account_list += f"\n------------------\n[{count}] 账号: {safe_display}{remark_display}\n🔐 授权: {vip_status}"
        count += 1
        
    account_list += "\n------------------\n[b] 批量授权\n[d] 批量删除\n[q] 退出管理\n=================="
    sender.reply(account_list)
    
    response = get_user_input()
    if not response or response == 'q':
        sender.reply('✅ 已退出')
        return
    
    if response.lower() == 'b':
        batch_auth_all_accounts(accounts, account_remarks)
        return
    elif response.lower() == 'd':
        batch_delete_all_accounts(accounts)
        return
    
    try:
        choice_num = int(response)
        if 1 <= choice_num < count:
            manage_single_account(str(accounts[choice_num - 1]), account_remarks)
        else:
            sender.reply('❌ 序号无效')
    except:
        sender.reply('❌ 输入必须是数字')

def manage_single_account(account, account_remarks):
    try:
        account = str(account)
        token = AccountManager.get_token(account)
        if not token: token = ""
        accountVip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        safe_display = get_safe_account(account)
        
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
            
            if process_payment('小牛牛授权', months, accountVip, token, account, remark):
                try:
                    days = months * 30
                    new_auth_time = empower(accountVip, days)
                    try: middleware.bucketSet(bucket='dd_xnn_auth', key=account, value=new_auth_time)
                    except: pass

                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('dd_xnn_remind_log', remind_key)
                        except: pass

                    if token:
                        sys_api.sync_env(token, account, remark, new_auth_time, owner_user_id=userid)
                        sender.reply("🔄 授权成功并同步到系统！")
                    else:
                        sender.reply("✅ 授权成功")

                    money = Decimal(months) * config['xyVipmoney']
                    sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")
                except Exception as ex:
                    sender.reply(f"❌ 授权后续写入异常: {ex}")

        elif choice == '2':
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                try:
                    AccountManager.remove_account(userid, account)
                    try: middleware.bucketDel(bucket='dd_xnn_token', key=account)
                    except: pass
                    try: middleware.bucketDel(bucket='dd_xnn_auth', key=account)
                    except: pass
                    if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                    sys_api.delete_env(account)
                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('dd_xnn_remind_log', remind_key)
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
                     sys_api.sync_env(token, account, new_remark, accountVip, owner_user_id=userid)
                 sender.reply("✅ 备注更新成功")

    except Exception as e:
        sender.reply(f"操作失败: {e}")

def process_payment(project, months, accountVip, token, account, remark=""):
    money = Decimal(months) * config['xyVipmoney']
    points_needed = config['xycoin'] * months
    user_points = int(middleware.bucketGet(config['points_bucket'], userid) or '0')
    
    options = []
    idx = 1
    if config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '微信支付', 'amount': money})
        idx += 1
    if config['use_ma_pay']:
        ma_conf = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch'),
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key')
        }
        if ma_conf['switch'] == 'true':
            options.append({'id': idx, 'type': 'ma', 'name': '码支付', 'amount': money, 'conf': ma_conf})
            idx += 1
    if config['epay_url'] and config['epay_pid'] and config['epay_key']:
        if config['epay_alipay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'alipay', 'name': '易支付支付宝', 'amount': money})
            idx += 1
        if config['epay_wxpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'wxpay', 'name': '易支付微信', 'amount': money})
            idx += 1
        if config['epay_qqpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'qqpay', 'name': '易支付QQ钱包', 'amount': money})
            idx += 1
    if config['xycoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': points_needed, 'curr': user_points})
    
    if not options:
        sender.reply("❌ 未配置支付方式")
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

        if opt['type'] == 'wx':
            if sender.atWaitPay():
                sender.reply("⚠️ 当前有人支付中")
                return False
            sender.reply(f"=====微信扫码=====\n金额: {opt['amount']}元")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            if str(res) == 'q': return False
            return True
        elif opt['type'] == 'epay':
            formatted_money = f"{Decimal(opt['amount']):.2f}"
            out_trade_no = f"XNN_{userid}_{account}_{int(time.time())}"
            qr_image_url, pay_url = _create_epay_qr(out_trade_no, opt['channel'], f"小牛牛授权-{months}月", formatted_money)
            sender.reply(f"""=====易支付订单=====
🎫 商品: 小牛牛授权-{months}月
💰 金额: {formatted_money}元
💳 通道: {opt['name']}
------------------
请扫码支付，系统将自动查询支付状态
==================""")
            try: sender.replyImage(qr_image_url)
            except: sender.reply(f"支付链接: {pay_url}")

            query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
            for _ in range(20):
                time.sleep(3)
                try:
                    order_res = requests.get(query_url, timeout=10, verify=False).json()
                    status = str(order_res.get('status') or order_res.get('trade_status') or '')
                    if status in ['1', 'TRADE_SUCCESS', 'success', 'paid']:
                        sender.reply("✅ 易支付订单已支付")
                        return True
                except Exception as e:
                    logger.warning(f"易支付查单异常: {e}")
            sender.reply("⚠️ 未检测到支付完成，请稍后重试或联系管理员核对订单")
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

        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"XNN_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"小牛牛授权-{months}月",
                'money': str(opt['amount']),
                'notify_url': '', 'return_url': '', 'param': userid
            }
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + conf['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            url = conf['gateway'].rstrip('/') + '/submit.php'
            res = requests.post(url, data=params, timeout=10)
            if 'http' in res.text:
                sender.reply("请完成支付后联系管理员手动授权")
            else:
                sender.reply("❌ 创建订单失败")
            return False

    except:
        sender.reply("❌ 支付异常")
        return False

def batch_auth_all_accounts(accounts, account_remarks):
    sender.reply("请输入授权月数，Q退出")
    m = get_user_input()
    if not m or not m.isdigit(): return
    months = int(m)
    if months <= 0: return
    
    count = len(accounts)
    total_money = Decimal(months) * config['xyVipmoney'] * count
    total_points = config['xycoin'] * months * count
    user_points = int(middleware.bucketGet(config['points_bucket'], userid) or '0')

    options = []
    idx = 1
    if config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '微信支付', 'amount': total_money})
        idx += 1
    if config['use_ma_pay']:
        ma_conf = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch'),
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key')
        }
        if ma_conf['switch'] == 'true':
            options.append({'id': idx, 'type': 'ma', 'name': '码支付', 'amount': total_money, 'conf': ma_conf})
            idx += 1
    if config['epay_url'] and config['epay_pid'] and config['epay_key']:
        if config['epay_alipay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'alipay', 'name': '易支付支付宝', 'amount': total_money})
            idx += 1
        if config['epay_wxpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'wxpay', 'name': '易支付微信', 'amount': total_money})
            idx += 1
        if config['epay_qqpay']:
            options.append({'id': idx, 'type': 'epay', 'channel': 'qqpay', 'name': '易支付QQ钱包', 'amount': total_money})
            idx += 1
    
    if config['xycoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': total_points, 'curr': user_points})

    if not options:
        sender.reply("❌ 未配置支付方式")
        return

    msg = f"=====批量授权确认=====\n👥 账号数量: {count}个\n📅 授权时长: {months}个月\n💰 总需金额: {total_money}元\n💎 总需积分: {total_points}"
    msg += "\n------------------"
    for opt in options:
        amount_str = f"{opt['amount']}积分" if opt['type'] == 'pt' else f"{opt['amount']}元"
        suffix = f" (当前: {opt['curr']})" if opt['type'] == 'pt' else ""
        msg += f"\n[{opt['id']}] {opt['name']} ({amount_str}){suffix}"
    msg += "\n------------------\n回复数字选择，Q退出\n=================="
    sender.reply(msg)

    sel = get_user_input()
    if not sel or sel == 'q': return

    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError

        if opt['type'] == 'wx':
            if sender.atWaitPay(): 
                sender.reply("⚠️ 当前有人支付中")
                return
            sender.reply(f"=====微信扫码=====\n金额: {opt['amount']}元")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            if str(res) == 'q': return

        elif opt['type'] == 'epay':
            formatted_money = f"{Decimal(opt['amount']):.2f}"
            out_trade_no = f"XNN_BATCH_{userid}_{int(time.time())}"
            qr_image_url, pay_url = _create_epay_qr(out_trade_no, opt['channel'], f"小牛牛批量-{count}号-{months}月", formatted_money)
            sender.reply(f"""=====易支付订单=====
🎫 商品: 小牛牛批量授权
👥 账号数量: {count}个
💰 金额: {formatted_money}元
💳 通道: {opt['name']}
------------------
请扫码支付，系统将自动查询支付状态
==================""")
            try: sender.replyImage(qr_image_url)
            except: sender.reply(f"支付链接: {pay_url}")

            query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
            paid = False
            for _ in range(20):
                time.sleep(3)
                try:
                    order_res = requests.get(query_url, timeout=10, verify=False).json()
                    status = str(order_res.get('status') or order_res.get('trade_status') or '')
                    if status in ['1', 'TRADE_SUCCESS', 'success', 'paid']:
                        paid = True
                        break
                except Exception as e:
                    logger.warning(f"易支付查单异常: {e}")
            if not paid:
                sender.reply("⚠️ 未检测到支付完成，请稍后重试或联系管理员核对订单")
                return
            sender.reply("✅ 易支付订单已支付")
        
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

        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"XNN_BATCH_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"小牛牛批量-{count}号-{months}月",
                'money': str(opt['amount']),
                'notify_url': '', 'return_url': '', 'param': userid
            }
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + conf['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            url = conf['gateway'].rstrip('/') + '/submit.php'
            res = requests.post(url, data=params, timeout=10)
            if 'http' in res.text:
                sender.reply("请完成支付后联系管理员")
            else:
                sender.reply("❌ 创建订单失败")
            return

    except Exception:
        sender.reply("❌ 输入错误或支付取消")
        return

    sender.reply(f"🚀 支付成功，正在处理 {count} 个账号...")
    for account in accounts:
        try:
            account = str(account)
            accountVip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
            new_date = empower(accountVip, months*30)
            try: middleware.bucketSet('dd_xnn_auth', account, new_date)
            except: pass

            token = AccountManager.get_token(account)
            curr_remark = account_remarks.get(account, "") if account_remarks else ""

            if token:
                sys_api.sync_env(token, account, curr_remark, new_date, owner_user_id=userid)

            today_date = datetime.now().date()
            for d in range(config['reminder_days'] + 1):
                remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                try: middleware.bucketDel('dd_xnn_remind_log', remind_key)
                except: pass
        except: pass

    sender.reply("✅ 批量授权完成")

def batch_delete_all_accounts(accounts):
    sender.reply("确认删除回复【确认删除】")
    if get_user_input() == "确认删除":
        today_date = datetime.now().date()
        for account in accounts:
            try:
                 account = str(account)
                 AccountManager.remove_account(userid, account)
                 try: middleware.bucketDel(bucket='dd_xnn_token', key=account)
                 except: pass
                 try: middleware.bucketDel(bucket='dd_xnn_auth', key=account)
                 except: pass
                 if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                 sys_api.delete_env(account)
                 for d in range(config['reminder_days'] + 1):
                     remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                     try: middleware.bucketDel('dd_xnn_remind_log', remind_key)
                     except: pass
            except: pass
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts(force_report=False):
    users = middleware.bucketAllKeys(bucket='dd_xnn_user')
    if not users:
        if sender.isAdmin() and (force_report or usermessage in ['小牛牛清理', '清理小牛牛']):
            sender.reply("=====执行结果=====\n📭 暂无用户数据")
        return {
            "report_date": str(datetime.now().date()),
            "scanned_users": 0, "scanned_accounts": 0,
            "sent_notifications": 0, "cleaned_count": 0,
            "reminded_count": 0, "ck_expired_count": 0,
        }

    if sender.isAdmin() and (force_report or usermessage in ['小牛牛清理', '清理小牛牛']):
        sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n⚙️ 提醒天数: {config['reminder_days']}天\n⏳ 处理中...")

    cleaned_count = 0
    reminded_count = 0
    ck_expired_count = 0
    scanned_accounts = 0
    today_date = datetime.now().date()
    reminder_days_cfg = config['reminder_days']
    user_account_meta = {}
    ck_verify_tasks = []
    panel_ck_tasks = collect_panel_ck_tasks()

    for user in users:
        try:
            accounts = AccountManager.get_accounts(user)
            for account in accounts:
                account = str(account)
                scanned_accounts += 1
                accountVip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
                if not accountVip:
                    expiration_date = None
                    expiration_str = "未授权"
                    days_diff = None
                else:
                    try:
                        expiration_date = datetime.strptime(str(accountVip), "%Y-%m-%d").date()
                        expiration_str = str(accountVip)
                    except:
                        expiration_date = today_date - timedelta(days=1)
                        expiration_str = "日期错误"
                    days_diff = (expiration_date - today_date).days

                token = AccountManager.get_token(account)
                user_account_meta[(str(user), account)] = {
                    "accountVip": accountVip,
                    "expiration_str": expiration_str,
                    "days_diff": days_diff,
                    "token": token,
                    "token_hash": hashlib.md5(str(token or '').encode()).hexdigest() if token else '',
                }
                if token and days_diff is not None and days_diff >= 0:
                    ck_verify_tasks.append((str(user), account, token))
        except Exception as e:
            logger.warning(f"维护预扫描用户失败 {user}: {e}")

    ck_verify_tasks.extend(panel_ck_tasks)
    ck_verify_result = batch_verify_account_ck(ck_verify_tasks)
    panel_unmapped_invalid = []

    for task in panel_ck_tasks:
        try:
            token_hash = hashlib.md5(str(task.get('token') or '').encode()).hexdigest()
            result_key = ('panel', str(task.get('user') or ''), str(task.get('account') or ''), token_hash)
            if ck_verify_result.get(result_key) is not False:
                continue

            owner = str(task.get('user') or '').strip()
            account = str(task.get('account') or '').strip()
            auth_date = str(task.get('auth_date') or '未知')
            safe_disp = get_safe_account(account)
            check_fail_key = f"panel_{owner}_{account}_{token_hash}_ck_fail_{today_date}"
            has_notified_fail = middleware.bucketGet('dd_xnn_remind_log', check_fail_key)
            if has_notified_fail:
                continue

            msg = f"""=====⚠️ CK失效提醒=====
您的小牛牛账号登录凭证已失效！
📱 账号: {safe_disp}
📅 授权到期: {auth_date}
------------------
面板变量已检测到需要重新登录。
请发送 {config['randomsigncommand']} 更新Token，避免脚本继续空跑。
=================="""

            sent = False
            if owner:
                sent = safe_send_message(owner, msg, f"面板CK失效通知 {owner}-{account}")
            if sent:
                try: middleware.bucketSet('dd_xnn_remind_log', check_fail_key, "1")
                except: pass
            else:
                panel_unmapped_invalid.append(f"用户:{owner or '未识别'} 账号:{safe_disp} env:{task.get('env_id')}")
                logger.warning(f"面板CK失效但推送失败/无归属: owner={owner}, account={account}, env={task.get('env_id')}")
            ck_expired_count += 1
        except Exception as e:
            logger.warning(f"处理面板CK失效通知失败: {e}")

    if panel_unmapped_invalid:
        admin_msg = "=====小牛牛面板CK失效未送达=====\n" + "\n".join(panel_unmapped_invalid[:20])
        if len(panel_unmapped_invalid) > 20:
            admin_msg += f"\n...其余 {len(panel_unmapped_invalid) - 20} 条省略"
        admin_msg += "\n请检查面板备注是否包含 用户: 和 ID:\n=================="
        send_message_to_framework_admins(admin_msg)

    for user in users:
        try:
            accounts = AccountManager.get_accounts(user)
            if not accounts:
                continue
            valid_accounts = []
            user_has_change = False

            for account in accounts:
                account = str(account)
                meta = user_account_meta.get((str(user), account), {})
                days_diff = meta.get("days_diff")
                expiration_str = meta.get("expiration_str", "未知")
                token_hash = meta.get("token_hash") or ''

                if days_diff is None:
                    valid_accounts.append(account)
                    continue

                local_result_key = ('local', str(user), account, token_hash)
                local_ck_invalid = ck_verify_result.get(local_result_key) is False if token_hash else ck_verify_result.get((str(user), account)) is False
                if days_diff >= 0 and local_ck_invalid:
                    check_fail_key = f"{user}_{account}_ck_fail_{today_date}"
                    has_notified_fail = middleware.bucketGet('dd_xnn_remind_log', check_fail_key)
                    if not has_notified_fail:
                        safe_disp = get_safe_account(account)
                        msg = f"""=====⚠️ CK失效提醒=====
您的小牛牛账号登录凭证已失效！
📱 账号: {safe_disp}
📅 授权到期: {expiration_str}
------------------
脚本已检测到账号需要重新登录。
请发送 {config['randomsigncommand']} 更新Token，避免继续空跑任务。
=================="""
                        if safe_send_message(user, msg, f"CK失效通知 {user}-{account}"):
                            try: middleware.bucketSet('dd_xnn_remind_log', check_fail_key, "1")
                            except: pass
                            ck_expired_count += 1

                if days_diff > reminder_days_cfg:
                    valid_accounts.append(account)
                    continue

                if 0 <= days_diff <= reminder_days_cfg:
                    valid_accounts.append(account)
                    remind_key = f"{user}_{account}_{today_date}"
                    has_reminded = middleware.bucketGet('dd_xnn_remind_log', remind_key)
                    if not has_reminded:
                        safe_display = get_safe_account(account)
                        msg = f"""=====⏰ 到期提醒=====
您的小牛牛账号授权即将到期！
📱 账号: {safe_display}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                        if safe_send_message(user, msg, f"到期提醒 {user}-{account}"):
                            try: middleware.bucketSet('dd_xnn_remind_log', remind_key, "1")
                            except: pass
                            reminded_count += 1
                    continue

                if days_diff < 0:
                    try:
                        sys_api.delete_env(account)
                        try: middleware.bucketDel(bucket='dd_xnn_token', key=account)
                        except: pass
                        try: middleware.bucketDel(bucket='dd_xnn_auth', key=account)
                        except: pass
                        if config['enable_remark']:
                            RemarkManager.delete_account_remark(user, account)
                    except Exception as e:
                        logger.warning(f"过期账号清理异常 {user}-{account}: {e}")

                    safe_display = get_safe_account(account)
                    clean_msg = f"""=====🗑️ 过期清理通知=====
您的账号授权已过期并清理。
📱 账号: {safe_display}
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
                    try: middleware.bucketSet(bucket='dd_xnn_user', key=str(user), value=str(valid_accounts))
                    except: pass
                else:
                    try: middleware.bucketDel(bucket='dd_xnn_user', key=str(user))
                    except: pass

        except Exception as e:
            logger.warning(f"维护任务处理用户失败 {user}: {e}")
            continue

    if sender.isAdmin() and (force_report or usermessage in ['小牛牛清理', '清理小牛牛']):
        sender.reply(
            f"=====维护完成=====\n"
            f"✅ 本地检测: {scanned_accounts}个\n"
            f"🌐 面板检测: {len(panel_ck_tasks)}个\n"
            f"📢 授权提醒: {reminded_count}个\n"
            f"⚠️ CK失效通知: {ck_expired_count}个\n"
            f"🗑️ 已清理过期: {cleaned_count}个\n"
            f"=================="
        )

    return {
        "report_date": str(today_date),
        "scanned_users": len(users),
        "scanned_accounts": scanned_accounts + len(panel_ck_tasks),
        "panel_scanned_accounts": len(panel_ck_tasks),
        "sent_notifications": reminded_count + ck_expired_count + cleaned_count,
        "cleaned_count": cleaned_count,
        "reminded_count": reminded_count,
        "ck_expired_count": ck_expired_count,
    }

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
                if not AccountManager.get_token(account):
                    stats["no_token"] += 1
                vip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
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
    sender.reply(f"""=====小牛牛数据总览=====
👥 用户数: {stats['users']}
📦 账号数: {stats['accounts']}
✅ 授权中: {stats['authorized']}
⚠️ 未授权: {stats['unauthorized']}
❌ 已过期: {stats['expired']}
⏰ 即将到期: {stats['expiring']}
🔑 缺少CK: {stats['no_token']}
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
    sender.reply("⏳ 正在生成用户CK预览，请稍候...")

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
                vip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
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
                "user": str(user), "count": len(accounts), "auth": auth_count,
                "unauth": unauth_count, "expired": expired_count,
                "expiring": expiring_count, "no_token": no_token_count
            })
        except:
            pass

    rows.sort(key=lambda x: x["count"], reverse=True)
    lines = [f"👥 用户数: {len(rows)}  📦 CK总数: {total_accounts}", "------------------"]
    for i, row in enumerate(rows, 1):
        extra = []
        if row["unauth"]: extra.append(f"未授权{row['unauth']}")
        if row["expired"]: extra.append(f"过期{row['expired']}")
        if row["expiring"]: extra.append(f"临期{row['expiring']}")
        if row["no_token"]: extra.append(f"缺CK{row['no_token']}")
        extra_text = f" ({' / '.join(extra)})" if extra else ""
        lines.append(f"[{i}] 用户: {row['user']}\nCK: {row['count']} 个  授权: {row['auth']} 个{extra_text}")

    send_long_admin_message("=====用户CK预览=====", lines)

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
    if not keyword or keyword.lower() == 'q':
        return
    keyword = keyword.strip()

    matches = []
    for user in AccountManager.get_all_users():
        user_match = keyword in str(user)
        remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
        for account in AccountManager.get_accounts(user):
            try:
                account = str(account)
                remark = remarks.get(account, "")
                safe_acc = get_safe_account(account)
                vip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
                vip_st = '未授权' if not vip else str(vip)
                if user_match or keyword in account or keyword in safe_acc or (remark and keyword in remark):
                    remark_text = f"\n📝 备注: {remark}" if remark else ""
                    matches.append(f"👤 用户: {user}\n📱 账号: {safe_acc}{remark_text}\n🔐 授权: {vip_st}")
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
    sender.reply("⚠️ 同步面板变量功能已撤销，避免面板备注反向覆盖本地账号归属。")
    return

def admin_auth_options():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足\n只有管理员可以执行授权操作")
        return
    
    sender.reply("""=====小牛牛管理员管理=====

[1] 一键授权所有用户
[2] 指定用户授权 (支持加减时间)
[3] 数据总览
[4] 用户CK预览
[5] 反查账号归属
[6] 同步面板变量(已禁用)
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
        report_data = clean_expired_accounts(force_report=True)
        send_daily_admin_report(report_data, force_send=True, notify_status=True)
    else:
        sender.reply("❌ 请输入有效的选项 (1-7)")

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
                accVip = middleware.bucketGet(bucket='dd_xnn_auth', key=account)
                new_vip = empower(accVip, days)
                try: middleware.bucketSet(bucket='dd_xnn_auth', key=account, value=new_vip)
                except: pass
                
                token = AccountManager.get_token(account)
                remark = RemarkManager.get_account_remark(user, account) if config['enable_remark'] else ""
                
                if token:
                    sys_api.sync_env(token, account, remark, new_vip, owner_user_id=user)
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
        accVip = middleware.bucketGet(bucket='dd_xnn_auth', key=acc)
        vip_st = '未授权' if not accVip else f"已授权({accVip})"
        rem = account_remarks.get(acc, "")
        rem_disp = f" - {rem}" if rem else ""
        safe_acc = get_safe_account(acc)
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
                accVip = middleware.bucketGet(bucket='dd_xnn_auth', key=acc)
                new_vip = empower(accVip, days)
                try: middleware.bucketSet(bucket='dd_xnn_auth', key=acc, value=new_vip)
                except: pass
                
                token = AccountManager.get_token(acc)
                remark = account_remarks.get(acc, "")
                if token:
                    sys_api.sync_env(token, acc, remark, new_vip, owner_user_id=target_qq)
            except: pass
        sender.reply(f"✅ 已操作该用户下所有账号 {days} 天")
        
    else:
        try:
            idx = int(sel) - 1
            if idx < 0 or idx >= len(target_accounts): raise ValueError
            acc = str(target_accounts[idx])
        except: return sender.reply("❌ 序号无效")
        
        safe_acc = get_safe_account(acc)
        sender.reply(f"目标账号: {safe_acc}\n请输入改变的天数(正数增加，负数如 -10 扣除):")
        d_str = get_user_input()
        if not d_str: return
        try: days = int(d_str)
        except: return sender.reply("❌ 无效天数")
        
        accVip = middleware.bucketGet(bucket='dd_xnn_auth', key=acc)
        new_vip = empower(accVip, days)
        try: middleware.bucketSet(bucket='dd_xnn_auth', key=acc, value=new_vip)
        except: pass
        
        token = AccountManager.get_token(acc)
        remark = account_remarks.get(acc, "")
        if token:
            sys_api.sync_env(token, acc, remark, new_vip, owner_user_id=target_qq)
        sender.reply(f"✅ 已为账号 {safe_acc} 操作 {days} 天\n⏰ 最新到期时间: {new_vip}")

def show_tutorial():
    panel_name = '青龙' if config['panel_type'] == 'qinglong' else '呆呆'
    sender.reply(f"""
=====小牛牛插件教程=====
当前模式: 🌐 提交至{panel_name}面板

1️⃣ {config['randomsigncommand']}
   直接发 Token 给我就行！系统会自动拉取手机号，以后怎么换CK都能完美无缝续期。

2️⃣ {config['randomquerycommand']}
   实时查询账号存活状态与当前金币和视频进度。

3️⃣ {config['randommanagecommand']}
   续费、删除、修改备注。

4️⃣ 小牛牛清理 / 小牛牛授权 / 小牛牛广播
   清理过期并同步删除系统变量；
   管理员进行全局或个人独立授权(支持加减天数)；
   系统管理员向所有已授权用户发送广播通知。
==================""")

# ===================== 主入口 =====================
try:
    if sender.getImtype() == 'fake':
        try:
            report_data = clean_expired_accounts()
        except Exception:
            logger.error(f"定时维护清理异常: {traceback.format_exc()}")
            report_data = {
                "report_date": str(datetime.now().date()),
                "scanned_users": 0, "scanned_accounts": 0,
                "sent_notifications": 0, "cleaned_count": 0,
                "reminded_count": 0, "ck_expired_count": 0,
            }
        send_daily_admin_report(report_data)
    
    elif re.search(r'(通知|广播)', usermessage or ''):
        notify_authorized_users()
    elif '登录' in usermessage or '登陆' in usermessage:
        bindaccount()
    elif '管理' in usermessage:
       xy_manage()
    elif '查询' in usermessage:
        cxs()
    elif usermessage in ['小牛牛清理', '清理小牛牛']:
        try:
            report_data = clean_expired_accounts(force_report=True)
        except Exception:
            logger.error(f"手动维护清理异常: {traceback.format_exc()}")
            report_data = {
                "report_date": str(datetime.now().date()),
                "scanned_users": 0, "scanned_accounts": 0,
                "sent_notifications": 0, "cleaned_count": 0,
                "reminded_count": 0, "ck_expired_count": 0,
            }
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
