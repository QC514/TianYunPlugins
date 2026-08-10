# -*- coding: utf-8 -*-
# [rule: ^(某手极速版)(登录|登陆)$|^登(录|陆)(某手极速版)$|^(某手极速版)(查询|管理|收益|结算)$|^(查询|管理)(某手极速版)$|^收益汇总$|^某手极速版清理$|^某手极速版授权$|^某手极速版教程$|^某手极速版通知 ?(.*)$|^清理某手极速版$|^某手极速版广播 ?(.*)$|^ks(login|query|manage|settle)$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 10,22 * * *]
# [public: true]
# [title: 某手极速版管理]
# [open_source: false]
# [class: 工具类]
# [version: 1.5]
# [price: 88.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 某手极速版代挂提交<br>1. 指令：某手极速版登录、某手极速版管理、某手极速版查询、某手极速版授权<br>2. 采用备注#ck格式登录，支持带备注提交。<br>3. 支持查询接口实时获取签到金币和账号存活状态。<br>4. 售后群1003974618。 售后联系：QQ 8165799<br>]

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
import logging
import base64
import ssl
import warnings
import random
import traceback
import uuid
import json
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
logger = logging.getLogger('ks_nebula_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 
MAINTENANCE_CK_MAX_WORKERS = 8

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())
usermessage = sender.getMessage()

try:
    middleware.bucketSet(bucket='ks_nebula_sender', key=userid, value=str(senderID))
    middleware.bucketSet(bucket='ks_nebula_imtype', key=userid, value=str(sender.getImtype()))
except:
    pass

# ===================== 插件配置参数 =====================
# [param: {"required":true,"key":"ks_nebula.panel_type","bool":false,"placeholder":"qinglong/daidai","name":"对接面板类型","desc":"qinglong=青龙面板 daidai=呆呆面板"}]
# [param: {"required":true,"key":"ks_nebula.ks_nebula_qlname","bool":false,"placeholder":"Host丨ClientID/AppKey丨Secret","name":"对接系统配置","desc":"青龙:URL丨ID丨Secret 呆呆:URL丨Key丨Secret"}]
# [param: {"required":true,"key":"ks_nebula.ks_nebula_osname","bool":false,"placeholder":"默认:ksck","name":"系统变量名","desc":"系统容器内变量名(默认为ksck)"}]
# [param: {"required":false,"key":"ks_nebula.epay_alipay","bool":true,"name":"易支付支付宝","desc":"启用易支付支付宝通道收款"}]
# [param: {"required":false,"key":"ks_nebula.epay_wxpay","bool":true,"name":"易支付微信","desc":"启用易支付微信通道收款"}]
# [param: {"required":false,"key":"ks_nebula.epay_qqpay","bool":true,"name":"易支付QQ","desc":"启用易支付QQ通道收款"}]
# [param: {"required":false,"key":"ks_nebula.epay_url","bool":false,"placeholder":"如 http://pay.xxx.com/","name":"易支付网关","desc":"易支付接口网关地址(需带http及结尾/)"}]
# [param: {"required":false,"key":"ks_nebula.epay_pid","bool":false,"placeholder":"","name":"易支付商户ID","desc":"易支付的PID"}]
# [param: {"required":false,"key":"ks_nebula.epay_key","bool":false,"placeholder":"","name":"易支付商户密钥","desc":"易支付的KEY密钥"}]
# [param: {"required":false,"key":"ks_nebula.enable_zsm","bool":true,"name":"个人微信收款","desc":"在支付菜单中增加个人微信收款码方式"}]
# [param: {"required":false,"key":"ks_nebula.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"微信收款码链接","desc":"填写个人微信收款码直链，不填则不开启"}]
# [param: {"required":true,"key":"ks_nebula.ksVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"ks_nebula.kscoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":true,"key":"ks_nebula.enable_proxy","bool":true,"name":"启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"ks_nebula.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"ks_nebula.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"ks_nebula.enable_remark","bool":true,"name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"ks_nebula.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]
# [param: {"required":false,"key":"ks_nebula.enable_revenue_push","bool":true,"name":"收益结算推送","desc":"每天22点自动查询收益并推送管理员和用户"}]
# [param: {"required":false,"key":"ks_nebula.revenue_share_percent","bool":false,"placeholder":"例:50","name":"平台分成比例","desc":"按今日新增金币折算后平台分成百分比"}]
# [param: {"required":false,"key":"ks_nebula.coin_per_yuan","bool":false,"placeholder":"默认10000","name":"金币兑元比例","desc":"多少金币折算1元，用于结账提示"}]

def getusercontent():
    """获取插件完整配置"""
    panel_type = middleware.bucketGet('ks_nebula', 'panel_type') or 'qinglong'
    panel_type = panel_type.lower()
    
    env_qlconfig = middleware.bucketGet('ks_nebula', 'ks_nebula_qlname') or ''
    env_name = middleware.bucketGet('ks_nebula', 'ks_nebula_osname') or 'ksck'
    
    if not env_qlconfig:
        sender.reply("❌ 配置错误：请在插件配置中填写【对接系统配置】(面板信息)。")
        exit(0)
    
    ks_managecommand = middleware.bucketGet('ks_nebula', 'ks_managecommand') or '某手极速版管理'
    ks_querycommand = middleware.bucketGet('ks_nebula', 'ks_querycommand') or '某手极速版查询'
    ks_signcommand = middleware.bucketGet('ks_nebula', 'ks_signcommand') or '某手极速版登录'
    
    enable_proxy = (middleware.bucketGet('ks_nebula', 'enable_proxy') or 'false').lower() == 'true'
    proxy_pool_url = middleware.bucketGet('ks_nebula', 'proxy_pool_url') or ''
    points_bucket = middleware.bucketGet('ks_nebula', 'points_bucket') or 'dd_sign_points'
    enable_remark = (middleware.bucketGet('ks_nebula', 'enable_remark') or 'false').lower() == 'true'
    
    randommanagecommand = ks_managecommand
    randomquerycommand = ks_querycommand
    randomsigncommand = ks_signcommand
    
    ksVipmoney = Decimal(middleware.bucketGet('ks_nebula', 'ksVipmoney') or '0')
    kscoin = int(middleware.bucketGet('ks_nebula', 'kscoin') or '0')
    reminder_days = int(middleware.bucketGet('ks_nebula', 'reminder_days') or '2')
    enable_revenue_push = (middleware.bucketGet('ks_nebula', 'enable_revenue_push') or 'true').lower() == 'true'
    revenue_share_percent = int(middleware.bucketGet('ks_nebula', 'revenue_share_percent') or '50')
    coin_per_yuan = int(middleware.bucketGet('ks_nebula', 'coin_per_yuan') or '10000')
    
    # 个人微信收款配置
    enable_zsm = (middleware.bucketGet('ks_nebula', 'enable_zsm') or 'false').lower() == 'true'
    zsm = middleware.bucketGet('ks_nebula', 'zsm') or ''
    
    # 易支付配置提取
    epay_url = middleware.bucketGet('ks_nebula', 'epay_url') or ''
    epay_pid = middleware.bucketGet('ks_nebula', 'epay_pid') or ''
    epay_key = middleware.bucketGet('ks_nebula', 'epay_key') or ''
    epay_alipay = (middleware.bucketGet('ks_nebula', 'epay_alipay') or 'true').lower() == 'true'
    epay_wxpay = (middleware.bucketGet('ks_nebula', 'epay_wxpay') or 'false').lower() == 'true'
    epay_qqpay = (middleware.bucketGet('ks_nebula', 'epay_qqpay') or 'false').lower() == 'true'

    return {
        'panel_type': panel_type,
        'env_name': env_name,
        'env_qlconfig': env_qlconfig,
        'ks_managecommand': ks_managecommand,
        'ks_querycommand': ks_querycommand,
        'ks_signcommand': ks_signcommand,
        'randommanagecommand': randommanagecommand,
        'randomquerycommand': randomquerycommand,
        'randomsigncommand': randomsigncommand,
        'enable_zsm': enable_zsm,
        'zsm': zsm,
        'enable_proxy': enable_proxy,
        'proxy_pool_url': proxy_pool_url,
        'points_bucket': points_bucket,
        'enable_remark': enable_remark,
        'ksVipmoney': ksVipmoney,
        'kscoin': kscoin,
        'reminder_days': reminder_days,
        'enable_revenue_push': enable_revenue_push,
        'revenue_share_percent': max(0, min(100, revenue_share_percent)),
        'coin_per_yuan': coin_per_yuan if coin_per_yuan > 0 else 10000,
        'epay_url': epay_url,
        'epay_pid': epay_pid,
        'epay_key': epay_key,
        'epay_alipay': epay_alipay,
        'epay_wxpay': epay_wxpay,
        'epay_qqpay': epay_qqpay
    }

config = getusercontent()

# ===================== 辅助工具函数 =====================
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
        for owner in middleware.bucketAllKeys(bucket='ks_nebula_user'):
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
    return ""

def send_message_to_framework_admins(msg):
    """
    优先走奥特曼框架原生管理员推送。
    某些框架支持 notifyMasters(msg) 自动发给管理员。
    """
    notify_func = getattr(middleware, 'notifyMasters', None)
    if not callable(notify_func):
        return False

    tried = [
        ("auto_none", None),
        ("auto_empty_list", []),
    ]

    for mode, arg in tried:
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
    if not force_send and middleware.bucketGet('ks_nebula_runtime', report_key):
        if notify_status:
            sender.reply("ℹ️ 今日管理员汇总已发送过，如需重发请明天自动发送或再次手动清理。")
        return False

    msg = (
        "=====某手极速版维护完成=====\n"
        f"✅ 检测完成，共 {report_data.get('scanned_accounts', 0)} 个账号\n"
        f"📣 发送通知: {report_data.get('sent_notifications', 0)} 条\n"
        f"⚠️ CK失效通知: {report_data.get('ck_expired_count', 0)} 个\n"
        f"🗑️ 清理过期: {report_data.get('cleaned_count', 0)} 个\n"
        "=================="
    )

    framework_sent = send_message_to_framework_admins(msg)
    if framework_sent:
        try:
            middleware.bucketSet('ks_nebula_runtime', report_key, "framework")
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
    # 某手极速版 CK 查询接口受风控影响可能误判。为避免误推用户，默认不做 CK 失效推送。
    return {}

def send_user_notice(user_id, msg, title="某手极速版通知"):
    try:
        imtype = middleware.bucketGet(bucket='ks_nebula_imtype', key=str(user_id)) or sender.getImtype()
    except:
        imtype = sender.getImtype()

    push_targets = [
        (imtype, "", str(user_id)),
        (sender.getImtype(), "", str(user_id)),
    ]
    last_error = "未知错误"
    for im_type, group_code, target_user in list(dict.fromkeys(push_targets)):
        for func_name in ['Push', 'push']:
            push_func = getattr(middleware, func_name, None)
            if not callable(push_func):
                continue
            try:
                push_func(str(im_type), str(group_code), str(target_user), title, msg)
                return True, ""
            except Exception as e:
                last_error = f"{func_name}({im_type},{target_user}): {str(e) or e.__class__.__name__}"

    targets = []
    try:
        saved_sender = middleware.bucketGet(bucket='ks_nebula_sender', key=str(user_id))
        if saved_sender:
            targets.append(str(saved_sender))
    except:
        pass
    targets.append(str(user_id))

    method_names = ['Reply', 'reply', 'ReplyMarkdown', 'replyMarkdown', 'send', 'replyText', 'sendText', 'push', 'sendMsg', 'sendMessage']
    for target in list(dict.fromkeys(targets)):
        try:
            target_sender = middleware.Sender(target)
        except Exception as e:
            last_error = f"Sender({target})初始化失败: {str(e) or e.__class__.__name__}"
            continue

        tried_methods = []
        for method_name in method_names:
            method = getattr(target_sender, method_name, None)
            if not callable(method):
                continue
            tried_methods.append(method_name)
            try:
                method(msg)
                return True, ""
            except Exception as e:
                last_error = f"{method_name}: {str(e) or e.__class__.__name__}"

        if not tried_methods:
            available = [name for name in dir(target_sender) if not name.startswith('_')]
            last_error = "无可用发送方法，可用方法: " + ",".join(available[:12])
    return False, last_error

def safe_send_message(user_id, msg, log_context=""):
    ok, err = send_user_notice(user_id, msg, "某手极速版提醒")
    if not ok:
        logger.warning(f"消息发送失败 {log_context}: {err}")
    return ok

def safe_int_value(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(str(value)))
    except Exception:
        return default

def safe_decimal_value(value, default="0"):
    try:
        if value is None or value == "":
            return Decimal(str(default))
        return Decimal(str(value))
    except Exception:
        return Decimal(str(default))

def format_yuan_from_coin(coin):
    return f"{Decimal(int(coin)) / Decimal(config.get('coin_per_yuan', 10000)):.2f}"

def format_yuan(value):
    return f"{safe_decimal_value(value):.2f}"

def calc_coin_cash(coin):
    return Decimal(safe_int_value(coin)) / Decimal(config.get('coin_per_yuan', 10000))

def calc_platform_due(coin, share_percent=None):
    share_percent = safe_int_value(config.get('revenue_share_percent'), 50) if share_percent is None else safe_int_value(share_percent)
    return calc_coin_cash(coin) * Decimal(share_percent) / Decimal(100)

def get_revenue_snapshot(account, date_text=None):
    date_text = str(date_text or datetime.now().date())
    raw = middleware.bucketGet('ks_nebula_revenue', f"{date_text}_{account}") or ""
    if not raw:
        return {}
    try:
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}

def get_today_revenue_snapshot(account):
    return get_revenue_snapshot(account, str(datetime.now().date()))

def get_recent_dates(days=5):
    today = datetime.now().date()
    return [str(today - timedelta(days=i)) for i in range(days - 1, -1, -1)]

def get_previous_revenue_snapshot(account, days_back=7):
    today = datetime.now().date()
    for offset in range(1, days_back + 1):
        snap = get_revenue_snapshot(account, str(today - timedelta(days=offset)))
        if snap:
            return snap
    return {}

def build_recent_revenue_text(account, days=5):
    parts = []
    for date_text in get_recent_dates(days):
        snap = get_revenue_snapshot(account, date_text)
        if not snap:
            parts.append(f"{date_text[5:]}:-")
            continue
        cash = safe_decimal_value(snap.get("today_cash"))
        drop = safe_decimal_value(snap.get("balance_drop")) + safe_decimal_value(snap.get("cross_day_balance_drop"))
        item = f"{date_text[5:]}:{format_yuan(cash)}"
        if drop > 0:
            item += f"(提{format_yuan(drop)})"
        parts.append(item)
    return " ".join(parts)

def save_revenue_snapshot(user_id, account, coin_balance, remark="", nickname="", is_final=False, cash_balance="0", total_cash="0"):
    today = str(datetime.now().date())
    coin_balance = safe_int_value(coin_balance)
    cash_balance_dec = safe_decimal_value(cash_balance)
    total_cash_dec = safe_decimal_value(total_cash)
    key = f"{today}_{account}"
    data = get_today_revenue_snapshot(account)
    if not data:
        prev_data = get_previous_revenue_snapshot(account)
        prev_balance = safe_decimal_value(prev_data.get("last_cash_balance"), cash_balance_dec) if prev_data else cash_balance_dec
        cross_day_drop = prev_balance - cash_balance_dec
        data = {
            "date": today,
            "user": str(user_id),
            "account": str(account),
            "remark": str(remark or ""),
            "nickname": str(nickname or ""),
            "start_coin": coin_balance,
            "min_coin": coin_balance,
            "last_coin": coin_balance,
            "max_coin": coin_balance,
            "start_cash_balance": str(cash_balance_dec),
            "min_cash_balance": str(cash_balance_dec),
            "last_cash_balance": str(cash_balance_dec),
            "max_cash_balance": str(cash_balance_dec),
            "start_total_cash": str(total_cash_dec),
            "last_total_cash": str(total_cash_dec),
            "prev_cash_balance": str(prev_balance),
            "cross_day_balance_drop": str(cross_day_drop if cross_day_drop > 0 else Decimal("0")),
            "query_count": 0,
        }
    else:
        # 兼容旧版当天快照：旧数据没有累计收益/余额字段时，不能把累计收益全算成今日流水。
        if "start_total_cash" not in data:
            data["start_total_cash"] = str(total_cash_dec)
        if "last_total_cash" not in data:
            data["last_total_cash"] = str(total_cash_dec)
        if "start_cash_balance" not in data:
            data["start_cash_balance"] = str(cash_balance_dec)
        if "last_cash_balance" not in data:
            data["last_cash_balance"] = str(cash_balance_dec)
        if "max_cash_balance" not in data:
            data["max_cash_balance"] = str(cash_balance_dec)
        if "min_cash_balance" not in data:
            data["min_cash_balance"] = str(cash_balance_dec)
        if "cross_day_balance_drop" not in data:
            prev_data = get_previous_revenue_snapshot(account)
            prev_balance = safe_decimal_value(prev_data.get("last_cash_balance"), cash_balance_dec) if prev_data else cash_balance_dec
            cross_day_drop = prev_balance - cash_balance_dec
            data["prev_cash_balance"] = str(prev_balance)
            data["cross_day_balance_drop"] = str(cross_day_drop if cross_day_drop > 0 else Decimal("0"))

    data["user"] = str(user_id)
    data["account"] = str(account)
    if remark:
        data["remark"] = str(remark)
    if nickname:
        data["nickname"] = str(nickname)
    data["last_coin"] = coin_balance
    data["max_coin"] = max(safe_int_value(data.get("max_coin")), coin_balance)
    data["min_coin"] = min(safe_int_value(data.get("min_coin"), coin_balance), coin_balance)
    data["today_coin"] = max(0, coin_balance - safe_int_value(data.get("start_coin")))
    old_max_balance = safe_decimal_value(data.get("max_cash_balance"), cash_balance_dec)
    old_min_balance = safe_decimal_value(data.get("min_cash_balance"), cash_balance_dec)
    data["last_cash_balance"] = str(cash_balance_dec)
    data["max_cash_balance"] = str(max(old_max_balance, cash_balance_dec))
    data["min_cash_balance"] = str(min(old_min_balance, cash_balance_dec))
    data["last_total_cash"] = str(total_cash_dec)
    today_cash = total_cash_dec - safe_decimal_value(data.get("start_total_cash"))
    data["today_cash"] = str(today_cash if today_cash > 0 else Decimal("0"))
    balance_drop = safe_decimal_value(data.get("max_cash_balance")) - cash_balance_dec
    data["balance_drop"] = str(balance_drop if balance_drop > 0 else Decimal("0"))
    data["query_count"] = safe_int_value(data.get("query_count")) + 1
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if is_final:
        data["final"] = True
        data["final_at"] = data["updated_at"]
    middleware.bucketSet('ks_nebula_revenue', key, json.dumps(data, ensure_ascii=False))
    return data

def parse_panel_ks_remark(remarks):
    try:
        remarks = str(remarks or '')
        user_match = re.search(r'用户[:：]\s*([^丨|\s]+)', remarks)
        id_match = re.search(r'ID[:：]\s*([^丨|\s]+)', remarks)
        date_match = re.search(r'到期[:：]\s*(\d{4}-\d{2}-\d{2})', remarks)
        if not user_match or not id_match or not date_match:
            return None
        return {
            'user': user_match.group(1).strip(),
            'account': id_match.group(1).strip(),
            'auth_date': date_match.group(1).strip()
        }
    except:
        return None

def normalize_panel_token_value(value, account_id=""):
    parts = [p.strip() for p in str(value or '').split('#') if p.strip()]
    account_id = str(account_id or '').strip()
    if len(parts) >= 4:
        return '#'.join(parts[-3:])
    if len(parts) == 3:
        if account_id and parts[1] == account_id:
            return '#'.join(parts[1:])
        return '#'.join(parts)
    if len(parts) == 2:
        return '#'.join(parts)
    return str(value or '').strip()

def build_panel_env_value(token, remark=""):
    token = str(token or "").strip()
    remark = str(remark or "").strip()
    if not remark:
        return token

    parts = [p.strip() for p in token.split('#') if p.strip()]
    if not parts:
        return token

    if 'kuaishou.api_st=' in token or 'kpn=' in token or ('=' in token and token.count(';') >= 2):
        if token.startswith(f"{remark}#"):
            return token
        return f"{remark}#{token}"

    cookie_idx = -1
    for idx, part in enumerate(parts):
        if 'kuaishou.api_st=' in part or 'kpn=' in part or ('=' in part and part.count(';') >= 2):
            cookie_idx = idx
            break

    if cookie_idx >= 0:
        tail = parts[cookie_idx + 1:]
        if tail:
            return '#'.join([remark, parts[cookie_idx]] + tail[:1])
        return f"{remark}#{parts[cookie_idx]}"

    if token.startswith(f"{remark}#"):
        return token
    return f"{remark}#{token}"

def parse_ks_submission_line(line, default_remark=""):
    line = str(line or "").strip()
    default_remark = str(default_remark or "").strip()
    if not line:
        return "", "", "内容为空"

    first_hash = line.find('#')
    if first_hash > 0:
        head = line[:first_hash].strip()
        rest = line[first_hash + 1:].strip()
        if rest and ('kuaishou.api_st=' in rest or 'kpn=' in rest or ('=' in rest and rest.count(';') >= 2)):
            return rest, head or default_remark, ""

    if 'kuaishou.api_st=' in line or 'kpn=' in line or ('=' in line and line.count(';') >= 2):
        return line, default_remark, ""

    parts = [p.strip() for p in line.split('#') if p.strip()]
    cookie_idx = -1
    for idx, part in enumerate(parts):
        if 'kuaishou.api_st=' in part or 'kpn=' in part or ('=' in part and part.count(';') >= 2):
            cookie_idx = idx
            break

    if cookie_idx < 0:
        return "", default_remark, "未识别到快手 CK"

    ck = parts[cookie_idx]
    tail = parts[cookie_idx + 1:]
    salt = tail[0] if tail else ""
    remark = default_remark
    if cookie_idx > 0:
        remark = parts[0]
    elif len(tail) >= 2:
        remark = tail[1]
    token = f"{ck}#{salt}" if salt else ck
    return token, remark, ""

def validate_ks_token(token):
    client = ksckClient(token)
    cookie_map = client.cookie_map or {}
    missing = []
    if not cookie_map.get("kuaishou.api_st"):
        missing.append("kuaishou.api_st")
    if not cookie_map.get("ud"):
        missing.append("ud")
    if not cookie_map.get("kpn"):
        missing.append("kpn")
    if missing:
        return False, "CK缺少必要参数: " + ",".join(missing)
    return True, ""

def sync_local_auth_from_panel():
    """以青龙/呆呆备注为兜底，修复本地 ks_nebula_user/auth/token 授权桶缺失。"""
    logger.info("面板反向同步本地归属已禁用，跳过以保护本地数据")
    return {'scanned': 0, 'synced': 0, 'failed': 0, 'disabled': True}
    stats = {'scanned': 0, 'synced': 0}
    logger.info("某手极速版面板变量反向回写已禁用，跳过同步本地归属表")
    return stats
    try:
        if not getattr(sys_api, 'enabled', False):
            return stats
        for env in sys_api.get_all_envs():
            if env.get('name') != config['env_name']:
                continue
            stats['scanned'] += 1
            info = parse_panel_ks_remark(env.get('remarks') or env.get('remark') or '')
            if not info:
                continue
            AccountManager.add_account(info['user'], info['account'])
            middleware.bucketSet(bucket='ks_nebula_auth', key=info['account'], value=info['auth_date'])
            token_value = normalize_panel_token_value(env.get('value'), info['account'])
            if token_value:
                AccountManager.update_account_token(info['account'], token_value)
            stats['synced'] += 1
    except Exception as e:
        logger.warning(f"某手极速版面板授权回写本地失败: {e}")
    return stats

def mask_account(account):
    account = str(account)
    return account[:3] + "****" + account[-3:] if len(account) > 6 else account

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

def is_cron_trigger():
    imtype = ""
    try:
        imtype = str(sender.getImtype() or "").lower()
    except:
        pass
    msg = str(usermessage or "").strip().lower()
    return imtype in ["fake", "cron"] or msg in ["", "cron", "定时任务"]

def is_revenue_cron_time():
    msg = str(usermessage or "").strip()
    if msg in ["收益汇总", "某手极速版收益", "某手极速版结算"]:
        return True
    return datetime.now().hour == 22

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

def parse_ks_cookie(cookie_text):
    data = {}
    for seg in str(cookie_text or "").split(';'):
        if '=' not in seg:
            continue
        key, value = seg.split('=', 1)
        key = key.strip()
        value = value.strip()
        if key:
            data[key] = value
    return data

# ===================== 核心逻辑类 (某手极速版ksck) =====================
class ksckClient:
    def __init__(self, token_str):
        self.token = token_str.strip()
        self.cookie = ""
        self.salt = ""
        self.remark_from_token = ""
        self.cookie_map = {}
        self.uid = ""
        self.uid_type = "ud"
        self.aliases = []
        self._parse_token()

    def _looks_like_cookie(self, text):
        text = str(text or "")
        return "kuaishou.api_st=" in text or "kpn=" in text or ("=" in text and text.count(";") >= 2)

    def _parse_token(self):
        first_hash = self.token.find('#')
        if first_hash > 0:
            head = self.token[:first_hash].strip()
            rest = self.token[first_hash + 1:].strip()
            if rest and self._looks_like_cookie(rest):
                self.remark_from_token = head
                self.cookie = rest
                self.cookie_map = parse_ks_cookie(self.cookie)
                self.uid = (
                    self.cookie_map.get("ud")
                    or self.cookie_map.get("userId")
                    or self.cookie_map.get("did")
                    or self.legacy_key()
                )
                if self.uid == self.legacy_key():
                    self.uid_type = "token_md5"
                for key in ["ud", "did", "oDid", "egid"]:
                    value = self.cookie_map.get(key)
                    if value and value != self.uid:
                        self.aliases.append(value)
                return

        if self._looks_like_cookie(self.token):
            self.cookie = self.token
            self.cookie_map = parse_ks_cookie(self.cookie)
            self.uid = (
                self.cookie_map.get("ud")
                or self.cookie_map.get("userId")
                or self.cookie_map.get("did")
                or self.legacy_key()
            )
            if self.uid == self.legacy_key():
                self.uid_type = "token_md5"
            for key in ["ud", "did", "oDid", "egid"]:
                value = self.cookie_map.get(key)
                if value and value != self.uid:
                    self.aliases.append(value)
            return

        parts = [p.strip() for p in self.token.split('#') if p.strip()]
        cookie_idx = -1
        for idx, part in enumerate(parts):
            if self._looks_like_cookie(part):
                cookie_idx = idx
                break

        if cookie_idx >= 0:
            self.cookie = parts[cookie_idx]
            if cookie_idx > 0:
                self.remark_from_token = parts[0]
            tail = parts[cookie_idx + 1:]
            self.salt = tail[0] if tail else ""
            if len(tail) >= 2 and not self.remark_from_token:
                self.remark_from_token = tail[1]
        else:
            self.cookie = parts[0] if parts else self.token
            self.salt = parts[1] if len(parts) > 1 else ""
            self.remark_from_token = parts[2] if len(parts) > 2 else ""

        self.cookie_map = parse_ks_cookie(self.cookie)
        self.uid = (
            self.cookie_map.get("ud")
            or self.cookie_map.get("userId")
            or self.cookie_map.get("did")
            or self.legacy_key()
        )
        if self.uid == self.legacy_key():
            self.uid_type = "token_md5"
        for key in ["ud", "did", "oDid", "egid"]:
            value = self.cookie_map.get(key)
            if value and value != self.uid:
                self.aliases.append(value)

    def _get_proxy(self):
        if not config.get('enable_proxy') or not config.get('proxy_pool_url'):
            return None
        try:
            res = requests.get(config['proxy_pool_url'], timeout=8, verify=False)
            text = res.text.strip()
            match = re.search(r'(?:https?://)?\d+\.\d+\.\d+\.\d+:\d+', text)
            if match:
                proxy = match.group(0)
                if not proxy.startswith(('http://', 'https://')):
                    proxy = f"http://{proxy}"
                return proxy
        except Exception as e:
            logger.warning(f"某手极速版查询获取代理失败: {e}")
        return None

    def _http_json(self, method, url, body=None, timeout=25, max_retries=3, headers=None):
        payload = body
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        elif payload is not None:
            payload = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

        last_exc = None
        for attempt in range(1, max_retries + 1):
            req = Request(url=url, data=payload, method=method.upper())
            request_headers = headers or {}
            for key, value in request_headers.items():
                req.add_header(key, value)

            proxy = self._get_proxy()
            opener = build_opener(ProxyHandler({'http': proxy, 'https': proxy})) if proxy else build_opener()

            try:
                with opener.open(req, timeout=timeout) as response:
                    raw = response.read()
                    if response.headers.get("Content-Encoding", "").lower() == "gzip":
                        raw = gzip.decompress(raw)
                    text = raw.decode("utf-8", errors="replace")
                    return json.loads(text)
            except HTTPError as e:
                last_exc = e
                if attempt < max_retries and e.code in [500, 502, 503, 504]:
                    time.sleep(2)
                    continue
                try:
                    raw = e.read()
                    if e.headers.get("Content-Encoding", "").lower() == "gzip":
                        raw = gzip.decompress(raw)
                    text = raw.decode("utf-8", errors="replace")
                except:
                    text = str(e)
                raise RuntimeError(f"HTTP {e.code}: {text[:120]}") from e
            except (URLError, TimeoutError, json.JSONDecodeError, Exception) as e:
                last_exc = e
                if attempt < max_retries:
                    time.sleep(2)
                    continue
                raise RuntimeError(str(e)) from e

        raise RuntimeError(str(last_exc) if last_exc else "请求失败")

    def legacy_key(self):
        return hashlib.md5(self.token.encode()).hexdigest()[:8]

    def get_info(self):
        """返回: (网络请求是否成功, CK是否有效, 查询数值, 提示信息)"""
        try:
            if not self.cookie or "kuaishou.api_st=" not in self.cookie:
                return True, False, 0, "CK缺少 kuaishou.api_st"

            headers = {
                "Host": "nebula.kuaishou.com",
                "Connection": "keep-alive",
                "User-Agent": "Mozilla/5.0 (Linux; Android 10; MI 8 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.101 Mobile Safari/537.36 Yoda/3.2.16-rc4 ksNebula/13.7.20.10468",
                "Accept": "*/*",
                "X-Requested-With": "com.kuaishou.nebula",
                "Cookie": self.cookie,
            }
            result = self._http_json(
                "GET",
                "https://nebula.kuaishou.com/rest/n/nebula/account/overview",
                headers=headers,
            )

            if result.get("result") != 1:
                msg = result.get("error_msg") or result.get("message") or "账号详情获取失败"
                return True, False, 0, msg

            data = result.get("data") or {}
            coin_balance = self.safe_int(data.get("coinBalance", 0))
            cash_balance = data.get("cashBalance", "0")
            total_cash = self.format_money(data.get("accumulativeAmount", "0"))
            nickname = data.get("nickname") or self.remark_from_token or self.uid
            msg = (
                f"✅ CK有效\n"
                f"👤 昵称: {nickname}\n"
                f"💰 金币: {coin_balance} ({coin_balance / 10000:.2f}元)\n"
                f"💵 余额: {cash_balance}元\n"
                f"💎 累计收益: {total_cash}元"
            )
            extra = {
                "nickname": nickname,
                "coin_balance": coin_balance,
                "cash_balance": str(cash_balance),
                "total_cash": str(total_cash),
            }
            return True, True, coin_balance, msg, extra
        except Exception as e:
            # 网络异常时默认视为有效，避免误判剔除
            return False, True, 0, str(e)

    def safe_int(self, value):
        try:
            if value is None or value == "":
                return 0
            return int(float(str(value)))
        except Exception:
            return 0

    def format_money(self, value):
        try:
            return f"{Decimal(str(value)):.2f}"
        except Exception:
            return str(value)

    def verify_ck(self):
        info_result = self.get_info()
        net_ok, is_valid = info_result[0], info_result[1]
        if net_ok and not is_valid:
            return False
        return True

    def check_info(self):
        if not self.uid:
            self.uid = self.legacy_key()
            self.uid_type = "token_md5"

        safe_id = self.uid[:3] + "****" + self.uid[-3:] if len(self.uid) > 6 else self.uid
        nickname = self.remark_from_token or f"某手极速版_{safe_id}"
        final_token = f"{self.cookie}#{self.salt}" if self.salt else self.cookie
                
        return {
            "nickname": nickname,
            "phone": self.uid, # 沿用原版字段名保持兼容
            "acc_key": self.uid,
            "acc_type": self.uid_type,
            "aliases": self.aliases,
            "legacy_key": self.legacy_key(),
            "final_token": final_token
        }

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='ks_nebula_remarks', key=f'{user_id}_{account_id}')
            return str(remark_data) if remark_data else ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = str(remark).strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='ks_nebula_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
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
            middleware.bucketDel(bucket='ks_nebula_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket='ks_nebula_user', key=str(user_id))
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
                middleware.bucketSet(bucket='ks_nebula_user', key=str(user_id), value=str(accounts))
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
                    middleware.bucketSet(bucket='ks_nebula_user', key=str(user_id), value=str(accounts))
                else:
                    middleware.bucketDel(bucket='ks_nebula_user', key=str(user_id))
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(account, token):
        try:
            encrypted_token = encrypt_token(str(token))
            middleware.bucketSet(bucket='ks_nebula_token', key=str(account), value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_token(account):
        try:
            enc = middleware.bucketGet(bucket='ks_nebula_token', key=str(account))
            return decrypt_token(enc) if enc else None
        except: return None

    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket='ks_nebula_user')
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

            old_vip = middleware.bucketGet(bucket='ks_nebula_auth', key=old_account)
            new_vip = middleware.bucketGet(bucket='ks_nebula_auth', key=new_account)
            if old_vip and (not new_vip or str(old_vip) > str(new_vip)):
                middleware.bucketSet(bucket='ks_nebula_auth', key=new_account, value=old_vip)

            old_bind_date = middleware.bucketGet(bucket='ks_nebula_bind_date', key=old_account)
            if old_bind_date and not middleware.bucketGet(bucket='ks_nebula_bind_date', key=new_account):
                middleware.bucketSet(bucket='ks_nebula_bind_date', key=new_account, value=old_bind_date)

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
            middleware.bucketSet(bucket='ks_nebula_user', key=str(user_id), value=str(new_accounts))

            AccountManager.update_account_token(new_account, new_token)
            try: middleware.bucketDel(bucket='ks_nebula_token', key=old_account)
            except: pass
            try: middleware.bucketDel(bucket='ks_nebula_auth', key=old_account)
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

                old_client = ksckClient(old_token)
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
            raise Exception(f"获取青龙Token失败 HTTP {response.status_code}: {response.text[:120]}")
        except Exception as e: raise

    def _get_daidai_token(self):
        try:
            url = f"{self.QLurl}/api/open-api/token"
            data = {"app_key": self.ClientID, "app_secret": self.ClientSecret}
            response = requests.post(url, json=data, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()['data']['access_token']
            raise Exception(f"获取呆呆Token失败 HTTP {response.status_code}: {response.text[:120]}")
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

    def find_env_ids(self, phone, token=None):
        if not self.enabled: return []
        phone = str(phone)
        token = str(token or "").strip()
        try:
            envs = self.get_all_envs()
            matched_ids = []
            matched_set = set()
            for env in envs:
                if env.get('name') != config['env_name']:
                    continue

                env_id = env.get('id') if env.get('id') is not None else env.get('_id')
                if env_id is None:
                    continue

                env_remarks = str(env.get('remarks') or '')
                env_value = str(env.get('value') or '').strip()
                is_match = False

                if env_remarks and f'ID:{phone}' in env_remarks:
                    is_match = True
                elif env_remarks and phone in env_remarks:
                    is_match = True
                elif token and env_value and token in env_value:
                    is_match = True

                if is_match:
                    env_id_key = str(env_id)
                    if env_id_key not in matched_set:
                        matched_set.add(env_id_key)
                        matched_ids.append(env_id)

            return matched_ids
        except:
            return []
    
    def delete_env(self, phone, token=None):
        if not self.enabled: return False
        phone = str(phone)
        try:
            env_ids = self.find_env_ids(phone, token)
            if not env_ids:
                env_id = self.find_env(phone, token)
                if env_id is not None:
                    env_ids = [env_id]
            if not env_ids:
                return False

            if self.panel_type == 'daidai':
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                success = False
                for env_id in env_ids:
                    url = f"{self.QLurl}/api/envs/{env_id}"
                    res = requests.delete(url, headers=headers, timeout=10, verify=False)
                    if res.status_code == 200:
                        success = True
                return success
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                res = requests.delete(url, headers=headers, json=env_ids, timeout=10, verify=False)
                return res.status_code == 200
        except: return False
    
    def sync_env(self, token, phone, remark="", auth_time="", owner_user_id=None):
        if not self.enabled: return False
        phone = str(phone)
        try:
            token_ok, token_error = validate_ks_token(token)
            if not token_ok:
                logger.warning(f"跳过同步不完整CK: account={phone} error={token_error}")
                return False

            env_id = self.find_env(phone, token)
            
            # 环境变量按脚本格式保存为 备注#ck 或 备注#ck#salt。
            ql_value = build_panel_env_value(token, remark)
            
            safe_phone = phone[:3] + "****" + phone[-3:] if len(phone) > 6 else phone
            remarks_parts = [f'某手极速版:{safe_phone}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            
            owner_user = get_owner_user_id(phone, owner_user_id)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{phone}', '某手极速版提交'])
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
        
        accountVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
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
                
                client = ksckClient(full_token)
                info = client.check_info()
                nickname = account_display
                
                # 请求API实时测活与查询签到金币
                info_result = client.get_info()
                net_ok, is_valid, money, msg = info_result[:4]
                extra = info_result[4] if len(info_result) > 4 and isinstance(info_result[4], dict) else {}
                if net_ok and not is_valid:
                    status_text = f"⚠️ 账号登录失败: {msg}"
                elif not net_ok:
                    status_text = f"⚠️ 网络查询异常: {str(msg)[:50]}"
                else:
                    snapshot = save_revenue_snapshot(
                        get_owner_user_id(account, userid) or userid,
                        account,
                        extra.get("coin_balance", money),
                        remark,
                        extra.get("nickname", ""),
                        cash_balance=extra.get("cash_balance", "0"),
                        total_cash=extra.get("total_cash", "0")
                    )
                    today_coin = safe_int_value(snapshot.get("today_coin"))
                    status_text = f"💰 查询数值: {money}\n{msg}"
                    if today_coin > 0:
                        status_text += f"\n📈 今日新增: {today_coin}金币 ≈ {format_yuan_from_coin(today_coin)}元"
                
                account_info = f"""
=====某手极速版详情=====
🚀 平台: 某手极速版
👤 账号: {nickname}
{status_text}
🎯 今日进度: 自动挂机中
⏰ 授权到期: {auth_time}"""
                return account_info.strip()
            except Exception as e:
                return f"""
=====某手极速版查询异常=====
📱 账号: {account_display}
❌ 错误: {str(e)[:50]}
=================="""
        else:
            return f"""
=====某手极速版状态=====
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

        menu = "=====某手极速版查询====="
        for i, acc in enumerate(accounts, 1):
            acc = str(acc)
            remark = account_remarks.get(acc, "") if config['enable_remark'] else ""
            safe_acc = mask_account(acc)
            account_display = get_account_display(acc, remark)
            vip = middleware.bucketGet(bucket='ks_nebula_auth', key=acc)
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

def collect_revenue_account(user, account, account_remarks, is_final=False):
    account = str(account)
    token = AccountManager.get_token(account) or ""
    remark = account_remarks.get(account, "") if account_remarks else ""
    if not token:
        return {"ok": False, "user": str(user), "account": account, "remark": remark, "error": "凭证为空"}
    accountVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
    today = str(datetime.now().date())
    if not accountVip or accountVip <= today:
        return {"ok": False, "user": str(user), "account": account, "remark": remark, "error": "未授权或已过期"}
    try:
        client = ksckClient(token)
        info_result = client.get_info()
        net_ok, is_valid, money, msg = info_result[:4]
        extra = info_result[4] if len(info_result) > 4 and isinstance(info_result[4], dict) else {}
        if net_ok and not is_valid:
            return {"ok": False, "user": str(user), "account": account, "remark": remark, "error": str(msg)[:60]}
        if not net_ok:
            return {"ok": False, "user": str(user), "account": account, "remark": remark, "error": f"网络异常:{str(msg)[:50]}"}
        snapshot = save_revenue_snapshot(
            user,
            account,
            extra.get("coin_balance", money),
            remark,
            extra.get("nickname", ""),
            cash_balance=extra.get("cash_balance", "0"),
            total_cash=extra.get("total_cash", "0"),
            is_final=is_final
        )
        return {
            "ok": True,
            "user": str(user),
            "account": account,
            "remark": remark,
            "nickname": extra.get("nickname", ""),
            "coin_balance": safe_int_value(extra.get("coin_balance", money)),
            "today_coin": safe_int_value(snapshot.get("today_coin")),
            "today_cash": str(snapshot.get("today_cash", "0")),
            "balance_drop": str(snapshot.get("balance_drop", "0")),
            "cross_day_balance_drop": str(snapshot.get("cross_day_balance_drop", "0")),
            "start_cash_balance": str(snapshot.get("start_cash_balance", "0")),
            "last_cash_balance": str(snapshot.get("last_cash_balance", "0")),
            "start_total_cash": str(snapshot.get("start_total_cash", "0")),
            "last_total_cash": str(snapshot.get("last_total_cash", "0")),
            "recent_text": build_recent_revenue_text(account, 5),
            "start_coin": safe_int_value(snapshot.get("start_coin")),
            "last_coin": safe_int_value(snapshot.get("last_coin")),
            "query_count": safe_int_value(snapshot.get("query_count")),
        }
    except Exception as e:
        return {"ok": False, "user": str(user), "account": account, "remark": remark, "error": str(e)[:60]}

def send_admin_revenue_report(msg, notify_status=False):
    max_len = 1500
    chunks = []
    current = ""
    for line in str(msg or "").splitlines():
        add = line if not current else "\n" + line
        if current and len(current) + len(add) > max_len:
            chunks.append(current)
            current = line
        else:
            current += add
    if current:
        chunks.append(current)

    sent_any = False
    for idx, chunk in enumerate(chunks, 1):
        if len(chunks) > 1:
            chunk = f"{chunk}\n-----第 {idx}/{len(chunks)} 段-----"
        if send_message_to_framework_admins(chunk):
            sent_any = True
            time.sleep(0.2)
        elif notify_status:
            sender.reply(chunk)
            sent_any = True
    return sent_any

def send_revenue_summary(force_send=False, notify_status=False):
    if not config.get('enable_revenue_push', True):
        if notify_status:
            sender.reply("ℹ️ 收益结算推送未启用。")
        return False

    today = str(datetime.now().date())
    report_key = f"revenue_report_{today}"
    if not force_send and middleware.bucketGet('ks_nebula_runtime', report_key):
        if notify_status:
            sender.reply("ℹ️ 今日收益汇总已发送过。")
        return False

    users = AccountManager.get_all_users()
    rows = []
    failed_rows = []
    for user in users:
        remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
        for account in AccountManager.get_accounts(user):
            result = collect_revenue_account(user, account, remarks, is_final=True)
            if result.get("ok"):
                rows.append(result)
            else:
                failed_rows.append(result)

    rows.sort(key=lambda x: safe_int_value(x.get("today_coin")), reverse=True)
    total_coin = sum(safe_int_value(row.get("today_coin")) for row in rows)
    share_percent = safe_int_value(config.get('revenue_share_percent'), 50)
    total_cash = calc_coin_cash(total_coin)
    platform_cash = calc_platform_due(total_coin, share_percent)
    user_cash = total_cash - platform_cash
    all_account_count = len(rows) + len(failed_rows)

    lines = [
        "=====某手极速版收益汇总=====",
        f"日期: {today}",
        f"用户数: {len(users)}  账号数: {all_account_count}  异常: {len(failed_rows)}",
        f"今日总积分: {total_coin}",
        f"折合总额: {format_yuan(total_cash)}元",
        f"平台{share_percent}%应收: {format_yuan(platform_cash)}元",
        f"用户留存参考: {format_yuan(user_cash)}元",
        "------------------"
    ]
    for row in rows:
        display = row.get("remark") or row.get("nickname") or mask_account(row.get("account", ""))
        coin = safe_int_value(row.get("today_coin"))
        coin_cash = calc_coin_cash(coin)
        due_cash = calc_platform_due(coin, share_percent)
        lines.append(
            f"用户:{row.get('user')}  号:{display}  今日积分:{coin}  "
            f"折合:{format_yuan(coin_cash)}元  应收:{format_yuan(due_cash)}元"
        )
    if failed_rows:
        lines.append("-----异常账号-----")
        for row in failed_rows:
            display = row.get("remark") or mask_account(row.get("account", ""))
            lines.append(f"用户:{row.get('user')}  号:{display}  异常:{row.get('error', '未知')}")
    lines.append("==================")

    admin_msg = "\n".join(lines)
    admin_sent = send_admin_revenue_report(admin_msg, notify_status=notify_status)
    if not admin_sent and notify_status:
        sender.reply("❌ 管理员收益汇总推送失败，请检查框架管理员推送配置。")

    user_groups = {}
    for row in rows:
        user_groups.setdefault(row.get("user"), []).append(row)
    for row in failed_rows:
        user_groups.setdefault(row.get("user"), []).append(row)
    for user in users:
        user_groups.setdefault(str(user), [])

    pushed_users = 0
    for user, user_rows in user_groups.items():
        user_total_coin = sum(safe_int_value(x.get("today_coin")) for x in user_rows if x.get("ok"))
        user_total_cash = calc_coin_cash(user_total_coin)
        user_due_cash = calc_platform_due(user_total_coin, share_percent)
        user_keep_cash = user_total_cash - user_due_cash
        detail_lines = [
            "=====某手极速版收益提醒=====",
            f"日期: {today}",
            f"账号数: {len(user_rows)}",
            f"今日总积分: {user_total_coin}",
            f"折合总额: {format_yuan(user_total_cash)}元",
            f"平台{share_percent}%应结: {format_yuan(user_due_cash)}元",
            f"你留存参考: {format_yuan(user_keep_cash)}元",
            "------------------"
        ]
        if not user_rows:
            detail_lines.append("今日暂无账号数据。")
        for row in user_rows[:12]:
            display = row.get("remark") or row.get("nickname") or mask_account(row.get("account", ""))
            if row.get("ok"):
                coin = safe_int_value(row.get('today_coin'))
                detail_lines.append(f"{display}: {coin}积分，应结{format_yuan(calc_platform_due(coin, share_percent))}元")
            else:
                detail_lines.append(f"{display}: 查询异常({row.get('error', '未知')})")
        if len(user_rows) > 12:
            detail_lines.append(f"...共{len(user_rows)}个账号")
        if user_due_cash > 0:
            detail_lines.append("请主动联系管理员结账，避免影响后续代挂。")
        else:
            detail_lines.append("今日暂无新增收益。")
        detail_lines.append("==================")
        if safe_send_message(user, "\n".join(detail_lines), f"收益结算提醒 {user}"):
            pushed_users += 1

    if users and admin_sent and pushed_users >= len(users):
        try:
            middleware.bucketSet('ks_nebula_runtime', report_key, f"admin={int(bool(admin_sent))};users={pushed_users}/{len(users)}")
        except Exception:
            pass
    else:
        try:
            middleware.bucketSet('ks_nebula_runtime', f"{report_key}_last", f"admin={int(bool(admin_sent))};users={pushed_users}/{len(users)}")
        except Exception:
            pass
    if notify_status:
        sender.reply(f"✅ 收益汇总完成：用户 {len(users)} 个，账号 {all_account_count} 个，用户推送 {pushed_users} 个，应收 {format_yuan(platform_cash)} 元。")
    return True

def notify_authorized_users():
    if not sender.isAdmin():
        sender.reply("❌ 只有管理员可以使用此功能")
        return
    
    content = ""
    match = re.search(r'^\s*(某手极速版广播|某手极速版通知)\s*(.*)$', usermessage, re.S)
    if match:
        content = match.group(2).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：某手极速版通知 系统维护中")
        return
        
    sender.reply("⏳ 正在扫描授权用户并发送通知...")
    
    try:
        panel_sync = sync_local_auth_from_panel()
        all_users = AccountManager.get_all_users()
        success_count = 0
        fail_count = 0
        today = str(datetime.now().date())
        
        for uid in all_users:
            user_accounts = AccountManager.get_accounts(uid)
            has_auth = False
            for acc in user_accounts:
                vip_date = middleware.bucketGet(bucket='ks_nebula_auth', key=str(acc))
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                ok, err = send_user_notice(uid, f"📢 【某手极速版管理员通知】\n\n{content}", "某手极速版管理员通知")
                if ok:
                    success_count += 1
                    time.sleep(0.3)
                else:
                    fail_count += 1
                    logger.warning(f"某手极速版管理员通知发送失败 {uid}: {err}")
        
        sender.reply(f"✅ 通知完成\n🔄 面板回写: {panel_sync['synced']} 个账号\n⚠️ 发送失败: {fail_count} 人\n📢 已送达: {success_count} 人")
        
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
=====某手极速版 登录=====
当前模式: 🌐 提交至面板
------------------
👉 请直接发送账号配置，格式如下(一行一个)：
备注#一键获取的ck
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
                line_val = line.strip()
                final_token_str, line_remark, parse_error = parse_ks_submission_line(line_val, remark)
                if parse_error:
                    bind_stats["fail"] += 1
                    fail_msgs.append(f"格式错误: {parse_error}")
                    if len(token_lines) == 1:
                        sender.reply("❌ 格式错误: 未识别到快手 CK，请使用 备注#ck。")
                    continue

                token_ok, token_error = validate_ks_token(final_token_str)
                if not token_ok:
                    bind_stats["fail"] += 1
                    fail_msgs.append(token_error)
                    if len(token_lines) == 1:
                        sender.reply(f"❌ CK不完整：{token_error}\n请重新抓取完整 CK 后按 备注#ck 提交。")
                    continue
                
                client = ksckClient(final_token_str)
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
            sender.reply(f"""=====某手极速版登录汇总=====
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
        migrated_from = ""
        existing_accounts = AccountManager.get_accounts(userid)
        # 快手设备字段经常复用，不能用 did/oDid/egid 自动承接旧账号，否则会把多个号合并成一个号。
        try:
            middleware.bucketSet(bucket='ks_nebula_sender', key=str(userid), value=str(senderID))
            middleware.bucketSet(bucket='ks_nebula_imtype', key=str(userid), value=str(sender.getImtype()))
            middleware.bucketSet(bucket='ks_nebula_contact_time', key=str(userid), value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        except Exception:
            pass
        
        accountVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
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
            try: middleware.bucketSet(bucket='ks_nebula_bind_date', key=account, value=str(datetime.now().date()))
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
=====某手极速版账号更新=====
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
    account_list = "======我的某手极速版账号====="
    today_time = str(datetime.now().date())
    
    for i, account in enumerate(accounts, 1):
        account = str(account)
        accountVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
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
        accountVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
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
                    try: middleware.bucketSet(bucket='ks_nebula_auth', key=account, value=new_auth_time)
                    except: pass

                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('ks_nebula_remind_log', remind_key)
                        except: pass

                    if token:
                        sys_api.sync_env(token, account, remark, new_auth_time)
                        sender.reply("🔄 授权成功并同步到系统！")
                    else:
                        sender.reply("✅ 授权成功")

                    money = Decimal(months) * config['ksVipmoney']
                    sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")
                except Exception as ex:
                    sender.reply(f"❌ 授权后续写入异常: {ex}")

        elif choice == '2':
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                try:
                    AccountManager.remove_account(userid, account)
                    try: middleware.bucketDel(bucket='ks_nebula_token', key=account)
                    except: pass
                    try: middleware.bucketDel(bucket='ks_nebula_auth', key=account)
                    except: pass
                    if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                    sys_api.delete_env(account, token)
                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel('ks_nebula_remind_log', remind_key)
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
    money = Decimal(months) * config['ksVipmoney']
    points_needed = config['kscoin'] * months
    user_points, points_bucket = get_user_points()
    
    options = []
    idx = 1
    
    if config['kscoin'] > 0:
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
            out_trade_no = f"ZSP_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
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
    total_money = Decimal(months) * config['ksVipmoney'] * count
    total_points = config['kscoin'] * months * count
    user_points, points_bucket = get_user_points()

    options = []
    idx = 1
    
    if config['kscoin'] > 0:
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
            out_trade_no = f"ZSP_BATCH_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
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
            accountVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
            new_date = empower(accountVip, months*30)
            try: middleware.bucketSet('ks_nebula_auth', account, new_date)
            except: pass

            token = AccountManager.get_token(account)
            curr_remark = account_remarks.get(account, "") if account_remarks else ""

            if token:
                sys_api.sync_env(token, account, curr_remark, new_date, owner_user_id=userid)

            today_date = datetime.now().date()
            for d in range(config['reminder_days'] + 1):
                remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                try: middleware.bucketDel('ks_nebula_remind_log', remind_key)
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
                 token = AccountManager.get_token(account)
                 try: middleware.bucketDel(bucket='ks_nebula_token', key=account)
                 except: pass
                 try: middleware.bucketDel(bucket='ks_nebula_auth', key=account)
                 except: pass
                 if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                 sys_api.delete_env(account, token)
                 for d in range(config['reminder_days'] + 1):
                     remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                     try: middleware.bucketDel('ks_nebula_remind_log', remind_key)
                     except: pass
            except: pass
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts(force_report=False):
    panel_sync = sync_local_auth_from_panel()
    users = middleware.bucketAllKeys(bucket='ks_nebula_user')
    if not users:
        if sender.isAdmin() and (force_report or usermessage in ['某手极速版清理', '清理某手极速版']):
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

    if sender.isAdmin() and (force_report or usermessage in ['某手极速版清理', '清理某手极速版']):
        sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n🔄 面板回写: {panel_sync['synced']}个账号\n⚙️ 提醒天数: {config['reminder_days']}天\n⏳ 处理中...")

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
            
            account_contexts = []

            for account in accounts:
                account = str(account)
                scanned_accounts += 1
                accountVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
                
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
                        # 日期格式异常时视为有效（设遥远未来），避免误删账号
                        logger.warning(f"VIP日期解析失败，保留账号: user={user} account={account} vip={accountVip}")
                        expiration_date = today_date + timedelta(days=3650)
                        expiration_str = f"{accountVip}(格式异常)"

                days_diff = (expiration_date - today_date).days
                full_token = AccountManager.get_token(account) or ""

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
                "accounts": account_contexts,
            })

        except Exception:
            continue

    ck_verify_result = batch_verify_account_ck(ck_verify_tasks)

    for context in user_contexts:
        try:
            user = context["user"]
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
                    # 某手极速版暂不做 CK 失效提醒，避免接口不稳定导致误推。
                    is_ck_valid = True
                    
                    if is_ck_valid and 0 <= days_diff <= reminder_days_cfg:
                        remind_key = f"{user}_{account}_{today_date}"
                        has_reminded = middleware.bucketGet('ks_nebula_remind_log', remind_key)
                        
                        if not has_reminded:
                            account_display = get_account_display(account, account_remarks.get(account, ""))
                            msg = f"""=====⏰ 到期提醒=====
您的某手极速版账号授权即将到期！
📱 账号: {account_display}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                            if safe_send_message(user, msg, f"到期提醒 {user}-{account}"):
                                try: middleware.bucketSet('ks_nebula_remind_log', remind_key, "1")
                                except: pass
                                reminded_count += 1
                    continue

                if days_diff < 0:
                    try:
                        sys_api.delete_env(account, account_item.get("full_token"))
                        try: middleware.bucketDel(bucket='ks_nebula_token', key=account)
                        except: pass
                        try: middleware.bucketDel(bucket='ks_nebula_auth', key=account)
                        except: pass
                        if config['enable_remark']:
                            RemarkManager.delete_account_remark(user, account)
                    except: pass
                    
                    account_display = get_account_display(account, account_remarks.get(account, ""))
                    clean_msg = f"""=====🗑️ 过期清理通知=====
您的某手极速版账号授权已过期并清理。
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
                    try: middleware.bucketSet(bucket='ks_nebula_user', key=str(user), value=str(valid_accounts))
                    except: pass
                else:
                    try: middleware.bucketDel(bucket='ks_nebula_user', key=str(user))
                    except: pass

        except Exception:
            continue

    if sender.isAdmin() and (force_report or usermessage in ['某手极速版清理', '清理某手极速版']):
        sender.reply(
            f"=====某手极速版维护完成=====\n"
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
    
    sender.reply("""=====某手极速版管理员管理=====

[1] 一键授权所有用户
[2] 指定用户授权 (支持加减时间)
[3] 数据总览
[4] 用户CK预览
[5] 反查账号归属
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
        sender.reply("⚠️ 同步面板变量功能已撤销，避免面板备注反向覆盖本地账号归属。")
    elif choice == '7':
        try:
            report_data = clean_expired_accounts(force_report=True)
        except Exception:
            logger.error(f"管理员手动维护清理异常: {traceback.format_exc()}")
            report_data = {
                "report_date": str(datetime.now().date()),
                "scanned_users": 0, "scanned_accounts": 0,
                "sent_notifications": 0, "cleaned_count": 0,
                "reminded_count": 0, "ck_expired_count": 0,
            }
        send_daily_admin_report(report_data, force_send=True, notify_status=True)
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
                vip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
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
    sender.reply(f"""=====某手极速版数据总览=====
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
    sender.reply("⏳ 正在生成用户配置预览，请稍候...")

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
                vip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
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

    send_long_admin_message("=====用户配置预览=====", lines)

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
                vip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
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
    sender.reply("⚠️ 同步面板变量功能已撤销，避免面板备注反向覆盖本地账号归属。")
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
        total_accounts = sum(len(AccountManager.get_accounts(u)) for u in users)
        if len(users) <= 1 and total_accounts > 5:
            sender.reply(
                "⚠️ 已拦截同步所有授权账号。\n"
                f"当前本地归属表异常：用户数 {len(users)}，账号数 {total_accounts}。\n"
                "这通常表示账号被集中到了管理员名下，继续同步会覆盖面板归属备注。\n"
                "请先恢复 ks_nebula_user 归属表，或使用 [2] 同步指定用户账号。"
            )
            return
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
                vip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
                token = AccountManager.get_token(account)
                if not vip or vip < today or not token:
                    skipped += 1
                    continue
                remark = remarks.get(account, "")
                if sys_api.sync_env(token, account, remark, vip, owner_user_id=user):
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
                accVip = middleware.bucketGet(bucket='ks_nebula_auth', key=account)
                new_vip = empower(accVip, days)
                try: middleware.bucketSet(bucket='ks_nebula_auth', key=account, value=new_vip)
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
        accVip = middleware.bucketGet(bucket='ks_nebula_auth', key=acc)
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
        accVip = middleware.bucketGet(bucket='ks_nebula_auth', key=acc)
        new_vip = empower(accVip, days)
        try: middleware.bucketSet(bucket='ks_nebula_auth', key=acc, value=new_vip)
        except: pass
        
        token = AccountManager.get_token(acc)
        remark = account_remarks.get(acc, "")
        if token:
            sys_api.sync_env(token, acc, remark, new_vip, owner_user_id=target_qq)
        success += 1
        latest_dates.append(new_vip)

    date_tip = latest_dates[0] if len(set(latest_dates)) == 1 else "多个日期"
    sender.reply(f"✅ 已操作 {success} 个账号 {days} 天\n⏰ 最新到期: {date_tip}")

def show_tutorial():
    panel_name = '青龙' if config['panel_type'] == 'qinglong' else '呆呆'
    sender.reply(f"""
=====某手极速版管理插件教程=====
当前模式: 🌐 提交至{panel_name}面板

1️⃣ {config['randomsigncommand']}
   发送某手极速版CK自动覆盖更新。

2️⃣ {config['randomquerycommand']}
   查询存活状态与当前签到金币(支持1,2多选)。

3️⃣ {config['randommanagecommand']}
   全新支付接口，极简扫码无需挂机，付完全自动回调开通。

4️⃣ 某手极速版授权
   管理员总管理：授权、总览、配置预览、反查、同步、清理。

5️⃣ 某手极速版清理 / 某手极速版广播
   自动维护与消息分发。
==================""")

# ===================== 主入口 =====================
try:
    command = usermessage.strip()

    if is_cron_trigger():
        if is_revenue_cron_time():
            try:
                send_revenue_summary()
            except Exception:
                logger.error(f"定时收益汇总异常: {traceback.format_exc()}")
        else:
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

    elif re.match(r'^某手极速版(通知|广播)\s*', command):
        notify_authorized_users()
    elif command in ['某手极速版登录', '某手极速版登陆', '登录某手极速版', '登陆某手极速版', 'kslogin']:
        bindaccount()
    elif command in ['某手极速版管理', '管理某手极速版', 'ksmanage']:
        xy_manage()
    elif command in ['某手极速版查询', '查询某手极速版', 'ksquery']:
        cxs()
    elif command in ['某手极速版清理', '清理某手极速版']:
        try:
            report_data = clean_expired_accounts()
        except Exception:
            logger.error(f"手动维护清理异常: {traceback.format_exc()}")
            report_data = {
                "report_date": str(datetime.now().date()),
                "scanned_users": 0, "scanned_accounts": 0,
                "sent_notifications": 0, "cleaned_count": 0,
                "reminded_count": 0, "ck_expired_count": 0,
            }
        send_daily_admin_report(report_data, force_send=True, notify_status=True)
    elif command in ['某手极速版收益', '某手极速版结算', '收益汇总', 'kssettle']:
        if not sender.isAdmin():
            sender.reply("❌ 只有管理员可以手动执行收益汇总")
        else:
            send_revenue_summary(force_send=True, notify_status=True)
    elif command == '某手极速版授权':
        admin_auth_options()
    elif command == '某手极速版教程':
        show_tutorial()

except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")



