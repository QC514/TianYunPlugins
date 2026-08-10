# [rule: ^(和合)(登录|登陆)$|^登(录|陆)(和合)$|^(和合)(查询|管理)$|^(查询|管理)(和合)$|^和合清理$|^和合授权$|^和合教程$|^清理和合$|^和合通知 ?(.*)$|^和合广播 ?(.*)$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 56 9,19 * * *]
# [public: true]
# [title: 和合天台]
# [open_source: false]
# [class: 工具类]
# [version: 2.8]
# [price: 28.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 和合天台代挂提交插件。<br>v2.3修复清理授权功能：新增全局抽奖Q值和免Q值登录开关。2.5修复查询错误问题,2.8新增批量登录<br>指令：和合登录、和合管理、和合查询、和合授权<br> 购插件送脚本，脚本在售后群1003974618。📞 售后联系：QQ 8165799<br>]

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
# 需要安装 pycryptodome 库
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('hhtt_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())
usermessage = sender.getMessage()

MAINTENANCE_CK_MAX_WORKERS = 8

# ===================== 奥特曼通用数据桶护栏 =====================
PLUGIN_NAME = "和合天台插件"
PLUGIN_NAMESPACE = "dd_hhtt"
PLUGIN_ID = "dd_hhtt:和合天台:v2"

PLUGIN_BUCKET_SUFFIXES = [
    "user",
    "token",
    "auth",
    "remarks",
    "bind_date",
    "remind_log",
    "runtime",
    "sender",
    "imtype",
]

PLUGIN_FOREIGN_BUCKETS = []
PLUGIN_SHARED_BUCKETS = ["dd_sign_points"]
PLUGIN_AUTO_NAMESPACE = False
PLUGIN_NAMESPACE_CANDIDATES = 50


def build_plugin_buckets(namespace, suffixes):
    return [f"{namespace}_{suffix}" for suffix in suffixes]


def plugin_bucket(suffix):
    return f"{PLUGIN_RUNTIME_NAMESPACE}_{suffix}"


def build_namespace_candidates(base_namespace, max_number=50):
    candidates = [base_namespace]
    candidates.extend(f"{base_namespace}{idx}" for idx in range(1, max_number + 1))
    candidates.extend(f"{base_namespace}{ch}" for ch in "abcdefghijklmnopqrstuvwxyz")
    return candidates


def _bucket_has_any_key(bucket_name):
    try:
        return bool(middleware.bucketAllKeys(bucket=bucket_name))
    except Exception:
        return False


def assert_automan_bucket_namespace_safe(
    plugin_name,
    namespace,
    plugin_id,
    bucket_suffixes,
    foreign_buckets=None,
    shared_buckets=None,
):
    """奥特曼框架通用桶护栏：避免模板插件串库写错账号、token、授权。"""
    namespace = str(namespace or "").strip()
    plugin_id = str(plugin_id or "").strip()
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{2,30}", namespace):
        sender.reply(
            f"❌ {plugin_name} 已停止运行：插件命名空间不合法。\n"
            "命名空间只能使用字母、数字、下划线，且必须以字母开头。"
        )
        exit(0)

    foreign_buckets = [str(x).strip() for x in (foreign_buckets or []) if str(x).strip()]
    shared_buckets = set(str(x).strip() for x in (shared_buckets or []) if str(x).strip())
    guard_key = "namespace_owner"

    duplicated_suffixes = sorted({suffix for suffix in bucket_suffixes if bucket_suffixes.count(suffix) > 1})
    if duplicated_suffixes:
        sender.reply(
            f"❌ {plugin_name} 已停止运行：模板内数据桶后缀重复。\n"
            "重复后缀: " + "、".join(duplicated_suffixes)
        )
        exit(0)

    candidates = build_namespace_candidates(namespace, PLUGIN_NAMESPACE_CANDIDATES) if PLUGIN_AUTO_NAMESPACE else [namespace]
    blocked_notes = []
    for candidate in candidates:
        data_buckets = build_plugin_buckets(candidate, bucket_suffixes)
        guard_bucket = f"{candidate}_guard"

        shared_conflicts = sorted(set(data_buckets) & shared_buckets)
        if shared_conflicts:
            sender.reply(
                f"❌ {plugin_name} 已停止运行：独占数据桶不能使用共享积分桶名称。\n"
                "冲突桶: " + "、".join(shared_conflicts)
            )
            exit(0)

        foreign_conflicts = sorted(set(data_buckets) & set(foreign_buckets))
        if foreign_conflicts:
            blocked_notes.append(f"{candidate}: 与已声明其他插件桶重复")
            continue

        try:
            owner = middleware.bucketGet(bucket=guard_bucket, key=guard_key)
        except Exception:
            owner = ""
        if owner:
            if str(owner) == plugin_id:
                return candidate
            logger.warning(f"{plugin_name} 检测到旧护栏标记不匹配({owner})，继续使用原数据桶 {candidate}")
            return candidate

        occupied = [bucket for bucket in data_buckets if _bucket_has_any_key(bucket)]
        if occupied:
            if candidate == namespace:
                try:
                    middleware.bucketSet(bucket=guard_bucket, key=guard_key, value=plugin_id)
                    logger.info(f"{plugin_name} 继续使用旧版数据桶: {','.join(occupied[:3])}")
                    return candidate
                except Exception as e:
                    logger.warning(f"{plugin_name} 旧版数据桶护栏写入失败({e})，继续使用原数据桶 {candidate}")
                    return candidate
            blocked_notes.append(f"{candidate}: 已有数据({','.join(occupied[:3])})")
            continue

        try:
            middleware.bucketSet(bucket=guard_bucket, key=guard_key, value=plugin_id)
            return candidate
        except Exception as e:
            logger.warning(f"{plugin_name} 护栏初始化失败({e})，继续使用原数据桶 {candidate}")
            return candidate

    detail = "\n".join(blocked_notes[:8]) if blocked_notes else "没有可用命名空间"
    sender.reply(
        f"❌ {plugin_name} 已停止运行：无法自动找到可用数据桶前缀。\n"
        "为避免账号、授权、token 数据错乱，本次不会写入任何数据。\n"
        f"{detail}"
    )
    exit(0)


PLUGIN_RUNTIME_NAMESPACE = assert_automan_bucket_namespace_safe(
    PLUGIN_NAME,
    PLUGIN_NAMESPACE,
    PLUGIN_ID,
    PLUGIN_BUCKET_SUFFIXES,
    foreign_buckets=PLUGIN_FOREIGN_BUCKETS,
    shared_buckets=PLUGIN_SHARED_BUCKETS,
)

try:
    middleware.bucketSet(bucket=plugin_bucket('sender'), key=userid, value=str(senderID))
    middleware.bucketSet(bucket=plugin_bucket('imtype'), key=userid, value=str(sender.getImtype()))
except:
    pass

# [param: {"required":true,"key":"dd_hhtt.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_hhtt.panel_type","bool":false,"placeholder":"qinglong/daidai","name":"对接面板类型","desc":"qinglong=青龙面板 daidai=呆呆面板"}]
# [param: {"required":true,"key":"dd_hhtt.dd_hhtt_qlname","bool":false,"placeholder":"Host丨ClientID/AppKey丨Secret","name":"设置对接系统","desc":"青龙:URL丨ID丨Secret 呆呆:URL丨Key丨Secret"}]
# [param: {"required":true,"key":"dd_hhtt.dd_hhtt_osname","bool":false,"placeholder":"必填项,例:ty_hhtt","name":"提交到系统的变量名","desc":"系统容器内和合的变量名(默认为ty_hhtt)"}]
# [param: {"required":true,"key":"dd_hhtt.hhttVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_hhtt.hhttcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"dd_hhtt.show_point_status","bool":true,"placeholder":"","name":"显示钱包状态","desc":"是否在查询结果中显示钱包金额"}]
# [param: {"required":true,"key":"dd_hhtt.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统"}]
# [param: {"required":true,"key":"dd_hhtt.enable_proxy","bool":true,"placeholder":"True/False","name":"是否启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_hhtt.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_hhtt.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"dd_hhtt.enable_remark","bool":true,"placeholder":"True/False","name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"dd_hhtt.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]
# [param: {"required":false,"key":"dd_hhtt.global_q","bool":false,"placeholder":"例:https://act.tmlyun.com...","name":"全局抽奖Q值","desc":"填写本月最新Q值(解决活动下架)"}]
# [param: {"required":false,"key":"dd_hhtt.require_q_link","bool":true,"placeholder":"True/False","name":"登录需要Q值","desc":"开启则需手机密码Q,关闭只需手机密码"}]
# [param: {"required":false,"key":"dd_hhtt.admin_notify_ids","bool":false,"placeholder":"例:123456|654321","name":"管理员汇总接收QQ","desc":"每日自动检测汇总的接收人QQ，多个用|或,分隔"}]
# [param: {"required":false,"key":"dd_hhtt.epay_alipay","bool":true,"name":"易支付支付宝","desc":"启用易支付支付宝通道收款"}]
# [param: {"required":false,"key":"dd_hhtt.epay_wxpay","bool":true,"name":"易支付微信","desc":"启用易支付微信通道收款"}]
# [param: {"required":false,"key":"dd_hhtt.epay_qqpay","bool":true,"name":"易支付QQ","desc":"启用易支付QQ通道收款"}]
# [param: {"required":false,"key":"dd_hhtt.epay_url","bool":false,"placeholder":"如:http://pay.xxx.com/","name":"易支付网关","desc":"易支付接口网关地址(需带http及结尾/)"}]
# [param: {"required":false,"key":"dd_hhtt.epay_pid","bool":false,"placeholder":"","name":"易支付商户ID","desc":"易支付的PID"}]
# [param: {"required":false,"key":"dd_hhtt.epay_key","bool":false,"placeholder":"","name":"易支付商户密钥","desc":"易支付的KEY密钥"}]

def getusercontent():
    """获取插件完整配置"""
    panel_type = (middleware.bucketGet('dd_hhtt', 'panel_type') or 'qinglong').lower()
    dd_hhtt_osname = middleware.bucketGet('dd_hhtt', 'dd_hhtt_osname') or 'ty_hhtt'
    dd_hhtt_qlname = middleware.bucketGet('dd_hhtt', 'dd_hhtt_qlname') or ''
    dd_managecommand = middleware.bucketGet('dd_hhtt', 'dd_managecommand') or '和合管理'
    dd_querycommand = middleware.bucketGet('dd_hhtt', 'dd_querycommand') or '和合查询'
    dd_signcommand = middleware.bucketGet('dd_hhtt', 'dd_signcommand') or '和合登录'
    zsm = middleware.bucketGet('dd_hhtt', 'zsm') or ''
    
    global_q = middleware.bucketGet('dd_hhtt', 'global_q') or ''
    require_q_link = middleware.bucketGet('dd_hhtt', 'require_q_link') or 'false'
    require_q_link = require_q_link.lower() == 'true'

    enable_proxy = middleware.bucketGet('dd_hhtt', 'enable_proxy') or 'false'
    enable_proxy = enable_proxy.lower() == 'true'
    
    proxy_pool_url = middleware.bucketGet('dd_hhtt', 'proxy_pool_url') or ''
    
    points_bucket = middleware.bucketGet('dd_hhtt', 'points_bucket') or 'dd_sign_points'
    
    enable_remark = middleware.bucketGet('dd_hhtt', 'enable_remark') or 'false'
    enable_remark = enable_remark.lower() == 'true'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    xyVipmoney = Decimal(middleware.bucketGet('dd_hhtt', 'hhttVipmoney') or '1')
    xycoin = int(middleware.bucketGet('dd_hhtt', 'hhttcoin') or '0')
    
    show_point_status = middleware.bucketGet('dd_hhtt', 'show_point_status') or 'false'
    show_point_status = show_point_status.lower() == 'true'
    
    use_ma_pay = middleware.bucketGet('dd_hhtt', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    reminder_days = int(middleware.bucketGet('dd_hhtt', 'reminder_days') or '2')
    admin_notify_ids = middleware.bucketGet('dd_hhtt', 'admin_notify_ids') or ''
    epay_url = middleware.bucketGet('dd_hhtt', 'epay_url') or ''
    epay_pid = middleware.bucketGet('dd_hhtt', 'epay_pid') or ''
    epay_key = middleware.bucketGet('dd_hhtt', 'epay_key') or ''
    epay_alipay = (middleware.bucketGet('dd_hhtt', 'epay_alipay') or 'true').lower() == 'true'
    epay_wxpay = (middleware.bucketGet('dd_hhtt', 'epay_wxpay') or 'false').lower() == 'true'
    epay_qqpay = (middleware.bucketGet('dd_hhtt', 'epay_qqpay') or 'false').lower() == 'true'

    if not dd_hhtt_qlname:
        sender.reply("❌ 对接系统配置未设置")
        exit(0)
    
    if not dd_hhtt_osname:
        sender.reply("❌ 变量名称未设置")
        exit(0)
    
    return {
        'dd_hhtt_osname': dd_hhtt_osname,
        'dd_hhtt_qlname': dd_hhtt_qlname,
        'panel_type': panel_type,
        'dd_managecommand': dd_managecommand,
        'dd_querycommand': dd_querycommand,
        'dd_signcommand': dd_signcommand,
        'randommanagecommand': randommanagecommand,
        'randomquerycommand': randomquerycommand,
        'randomsigncommand': randomsigncommand,
        'zsm': zsm,
        'global_q': global_q,
        'require_q_link': require_q_link,
        'enable_proxy': enable_proxy,
        'proxy_pool_url': proxy_pool_url,
        'points_bucket': points_bucket,
        'enable_remark': enable_remark,
        'xyVipmoney': xyVipmoney,
        'xycoin': xycoin,
        'show_point_status': show_point_status,
        'use_ma_pay': use_ma_pay,
        'reminder_days': reminder_days,
        'admin_notify_ids': admin_notify_ids,
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
        for owner in middleware.bucketAllKeys(bucket=plugin_bucket('user')):
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

def send_user_notice(user_id, msg, title="和合天台通知"):
    try:
        imtype = middleware.bucketGet(bucket=plugin_bucket('imtype'), key=str(user_id)) or sender.getImtype()
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
        saved_sender = middleware.bucketGet(bucket=plugin_bucket('sender'), key=str(user_id))
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
    ok, err = send_user_notice(user_id, msg, "和合提醒")
    if not ok:
        logger.warning(f"消息发送失败 {log_context}: {err}")
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
            except Exception as e:
                logger.warning(f"框架管理员推送失败: {e}")
        except Exception as e:
            logger.warning(f"框架管理员推送失败: {e}")
    return False

def send_daily_admin_report(report_data, force_send=False, notify_status=False):
    report_date = str(report_data.get('report_date') or datetime.now().date())
    report_key = f"daily_admin_report_{report_date}"
    if not force_send and middleware.bucketGet(plugin_bucket('runtime'), report_key):
        if notify_status:
            sender.reply("ℹ️ 今日管理员汇总已发送过，如需重发请再次手动清理。")
        return False

    msg = (
        "=====和合维护完成=====\n"
        f"✅ 检测完成，共 {report_data.get('scanned_accounts', 0)} 个账号\n"
        f"📢 通知发送: {report_data.get('sent_notifications', 0)} 条\n"
        f"⚠️ CK失效通知: {report_data.get('ck_expired_count', 0)} 个\n"
        f"🧹 未授权面板清理: {report_data.get('unauth_panel_cleaned_count', 0)} 个\n"
        f"🗑️ 清理过期: {report_data.get('cleaned_count', 0)} 个\n"
        "=================="
    )

    if send_message_to_framework_admins(msg):
        try:
            middleware.bucketSet(plugin_bucket('runtime'), report_key, "framework")
        except Exception:
            pass
        if notify_status:
            sender.reply("✅ 管理员汇总已发送（框架自动管理员）")
        return True
    if notify_status:
        sender.reply("❌ 管理员汇总发送失败：框架自动管理员推送未成功，请检查奥特曼默认管理员配置。")
    return False

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
    candidates = get_points_bucket_candidates()
    return 0, (candidates[0] if candidates else str(config.get('points_bucket') or 'dd_sign_points'))

def set_user_points(points, bucket=None):
    candidates = get_points_bucket_candidates()
    target_bucket = bucket or (candidates[0] if candidates else str(config.get('points_bucket') or 'dd_sign_points'))
    middleware.bucketSet(target_bucket, userid, str(points))

def is_cron_trigger():
    imtype = ""
    try:
        imtype = str(sender.getImtype() or "").lower()
    except:
        pass
    msg = str(usermessage or "").strip().lower()
    return imtype in ["fake", "cron"] or msg in ["", "cron", "定时任务"]

def mask_account(account):
    account = str(account or "")
    if len(account) >= 11 and account.isdigit():
        return account[:3] + "****" + account[-4:]
    if len(account) > 6:
        return account[:3] + "****" + account[-3:]
    return account

def get_account_display(account, remark=""):
    account_display = mask_account(account)
    remark = str(remark or "").strip()
    return f"{account_display} - {remark}" if remark else account_display

def generate_ua_from_phone(phone_number: str) -> str:
    """根据手机号生成固定UA字符串"""
    version = "4.5.6"
    seed_value = int(hashlib.md5(phone_number.encode()).hexdigest()[:8], 16)
    random.seed(seed_value)

    def generate_deterministic_uuid(phone: str):
        md5_hash = hashlib.md5(phone.encode()).hexdigest()
        sha_hash = hashlib.sha256(phone.encode()).hexdigest()
        part1 = "00000000"
        part2 = sha_hash[8:12]
        part3 = sha_hash[20:24]
        part4 = "ffff"
        part5 = md5_hash[16:28]
        return f"{part1}-{part2}-{part3}-{part4}-{part5}"

    uuid_str = generate_deterministic_uuid(phone_number)

    device_pools = {
        0: ("xiaomi", ["22081212C", "2210132C", "23013RK75C", "2201122C", "2211133G"]),
        1: ("samsung", ["SM-G998B", "SM-S901E", "SM-F721B", "SM-A736B", "SM-M336B"]),
        2: ("huawei", ["NOH-AN00", "LIO-AL00", "TET-AN00", "ANA-AN00", "JAD-AL50"]),
        3: ("oppo", ["CPH2207", "CPH2419", "CPH2487", "PFFM10", "PHQ110"]),
        4: ("vivo", ["V2244A", "V2218A", "V2217A", "V2220A", "V2232A"]),
        5: ("oneplus", ["NE2210", "CPH2417", "KB2000", "LE2120", "GM1910"]),
    }

    last_digit = int(phone_number[-1]) if phone_number[-1].isdigit() else 0
    brand_idx = last_digit % len(device_pools)
    brand, models = device_pools[brand_idx]

    if len(phone_number) >= 6:
        mid_digit = int(phone_number[len(phone_number) // 2]) % len(models)
    else:
        mid_digit = seed_value % len(models)

    device_model = models[mid_digit]
    phone_sum = sum(int(c) for c in phone_number if c.isdigit())
    if phone_sum % 10 < 2:
        os_type = "iOS"
        os_versions = ["17.0", "16.6", "15.7", "14.8", "13.5"]
        ios_models = ["iPhone15,2", "iPhone14,2", "iPhone13,2", "iPhone12,8", "iPhone11,8"]
        device_model = ios_models[mid_digit % len(ios_models)]
        brand = "apple"
    else:
        os_type = "Android"
        os_versions = ["13", "12", "11", "10", "9", "14"]

    version_idx = (seed_value + int(phone_number[-2:]) if len(phone_number) >= 2 else seed_value) % len(os_versions)
    os_version = os_versions[version_idx]
    app_version = "6.8.0"
    brand_lower = brand.lower()
    ua_string = f"{version};{uuid_str};{device_model};{os_type};{os_version};{brand_lower};{app_version}"
    random.seed()
    return ua_string

def empower(empowertime, days):
    """授权时间计算"""
    try:
        today_date = datetime.now().date()
        if not empowertime or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            delayed_date = empower_date + timedelta(days=days)
        else:
            raise Exception('时间计算出错！')
        if days < 0 and delayed_date < today_date:
            delayed_date = today_date
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

# ===================== 核心逻辑类 =====================
class HeHeTianTai:
    def __init__(self, phone, password, q):
        self.url = "vapp.tmuyun.com"
        # 1. 修复：初始化Session，确保全程TCP连接复用
        self.session = requests.Session()
        self.session_id = ""
        self.account_id = ""
        self.request_id = ""
        self.t = ""
        self.signature = ""
        self.phone = phone
        self.password = password
        
        # ==== 修复：全局Q值覆盖逻辑 ====
        latest_q = config.get('global_q', '')
        if latest_q:
            self.q = unquote(latest_q.replace("https://act.tmlyun.com/lottery/?q=", ""))
        elif q:
            self.q = unquote(q.replace("https://act.tmlyun.com/lottery/?q=", ""))
        else:
            self.q = ""
        # ================================
        
        self.token = ""
        self.u = ""
        self.ua = generate_ua_from_phone(self.phone)
        self.price = 0
        self.totalPrice = 0
        self.last_error = "" # 记录具体错误信息
        
        # 代理支持
        if config['enable_proxy'] and config['proxy_pool_url']:
            try:
                res = requests.get(config['proxy_pool_url'], timeout=5)
                if res.status_code == 200:
                    proxy_ip = res.text.strip()
                    if "{" in proxy_ip:
                        try:
                            json_data = res.json()
                            proxy_ip = json_data.get('proxy') or json_data.get('http') or list(json_data.values())[0]
                        except: pass
                    if proxy_ip and ":" in proxy_ip:
                        self.session.proxies.update({'http': proxy_ip, 'https': proxy_ip})
            except: pass
        
    def _safe_json(self, response):
        try:
            return response.json()
        except ValueError:
            return {"code": -1, "message": f"返回异常(HTTP状态: {response.status_code})"}

    def get_sign(self, path, e=None, d=None, t=None):
        """生成签名"""
        if e is None: e = self.session_id
        if d is None: d = self.request_id
        if t is None: t = self.t
        if '?' in path: l = path.split('?')[0]
        else: l = path
        sign_str = f"{l}&&{e}&&{d}&&{t}&&FR*r!isE5W&&5"
        self.signature = hashlib.sha256(sign_str.encode()).hexdigest()
        
    def g(self, path):
        """GET请求"""
        self.request_id = str(uuid.uuid4())
        self.t = str(int(time.time() * 1000))
        self.get_sign(path)
        
        headers = {
            "User-Agent": self.ua,
            "Host": self.url,
            'Cache-Control': "no-cache",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            "X-TENANT-ID": "5",
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": self.request_id,
            "X-TIMESTAMP": self.t,
            "X-SIGNATURE": self.signature,
            "X-ACCOUNT-ID": self.account_id,
        }
        # 使用 self.session 保持连接
        response = self.session.get(
            f"https://{self.url}{path}",
            headers=headers,
            verify=False,
            timeout=15
        )
        return self._safe_json(response)
    
    def p(self, path, data=""):
        """POST请求"""
        self.request_id = str(uuid.uuid4())
        self.t = str(int(time.time() * 1000))
        self.get_sign(path)
        
        headers = {
            "User-Agent": self.ua,
            "Host": self.url,
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": self.request_id,
            "X-TIMESTAMP": self.t,
            "X-SIGNATURE": self.signature,
            "X-ACCOUNT-ID": self.account_id,
            "X-TENANT-ID": "5",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cache-Control": "no-cache"
        }
        # 使用 self.session 保持连接
        response = self.session.post(
            f"https://{self.url}{path}",
            headers=headers,
            data=data,
            verify=False,
            timeout=15
        )
        return self._safe_json(response)
    
    def rsa_encrypt(self, password, public_key_pem):
        """RSA加密密码"""
        rsa_key = RSA.import_key(public_key_pem)
        cipher = PKCS1_v1_5.new(rsa_key)
        encrypted = cipher.encrypt(password.encode())
        return base64.b64encode(encrypted).decode()
    
    def login(self):
        """登录流程"""
        try:
            # 初始化
            init_data = self.p("/api/account/init", "")
            self.session_id = init_data.get("data", {}).get("session", {}).get("id", "")
            
            # 公钥
            public_key = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXi
zPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXF
c+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlT
HMlluw4ZYmnOwg+thwIDAQAB
-----END PUBLIC KEY-----"""
            
            encrypted_pwd = self.rsa_encrypt(self.password, public_key)
            
            # 请求授权码
            d = str(uuid.uuid4())
            t = str(int(time.time() * 1000))
            l = "/web/oauth/credential_auth"
            sign_str = f"{l}&&{self.session_id}&&{d}&&{t}&&FR*r!isE5W&&5"
            s = hashlib.sha256(sign_str.encode()).hexdigest()
            
            auth_data = {
                "client_id": "10",
                "password": encrypted_pwd,
                "phone_number": self.phone
            }
            
            headers = {
                "User-Agent": self.ua,
                "X-REQUEST-ID": d,
                "X-SIGNATURE": s,
                "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Host": "passport.tmuyun.com"
            }
            
            # 2. 修复：这里原来是用 requests.post，导致session中断。现在改为 self.session.post
            response = self.session.post(
                "https://passport.tmuyun.com/web/oauth/credential_auth",
                headers=headers,
                data=auth_data,
                verify=False,
                timeout=15
            )
            
            code_data = self._safe_json(response)
            if code_data.get("code") != 0:
                self.last_error = f"账号认证失败: {code_data.get('message')}"
                return code_data
            
            code = code_data.get("data", {}).get("authorization_code", {}).get("code", "")
            
            # 登录
            login_data = self.p(
                "/api/zbtxz/login",
                f"check_token=&code={code}&token=&type=-1&union_id="
            )
            
            self.session_id = login_data.get("data", {}).get("session", {}).get("id", "")
            self.account_id = login_data.get("data", {}).get("session", {}).get("account_id", "")
            return login_data
        except Exception as e:
            logger.error(f"登录异常: {e}")
            self.last_error = f"登录异常: {str(e)}"
            return {"code": -1, "message": str(e)}

    def get_u(self):
        try:
            url = "https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/accountPrizeRecord/jumpEquityWallet"
            headers = {
                'User-Agent': self.ua,
                'Authorization': self.token,
                'X-REQUEST-ID': self.request_id,
            }
            # 使用 session
            response = self.session.get(url, headers=headers, verify=False, timeout=10)
            if self._safe_json(response).get("code") == 0:
                self.u = unquote(self._safe_json(response).get("data", {}).split("u=")[1].split("&")[0])
                return True
            self.last_error = f"获取U值失败: {self._safe_json(response).get('message')}"
            return False
        except Exception as e:
            self.last_error = f"获取U值异常: {str(e)}"
            return False

    def lottery_login(self):
        try:
            url = "https://act.tmlyun.com/activity-api/lottery/api/auth/userLogin"
            self.request_id = str(uuid.uuid4())
            payload = {
                "q": self.q,
                "accountId": self.account_id,
                "sessionId": self.session_id,
                "tenantCode": "xsb_tiantai"
            }
            headers = {
                'Content-Type': "application/json",
                'X-REQUEST-ID': self.request_id,
                'X-Requested-With': "com.zjonline.tiantai",
            }
            # 使用 session
            response = self.session.post(url, data=json.dumps(payload), headers=headers, verify=False, timeout=10)
            if self._safe_json(response).get("code") == 0:
                self.token = self._safe_json(response).get("data", {}).get("token", "")
                return True
            self.last_error = f"抽奖登录失败: {self._safe_json(response).get('message')}"
            return False
        except Exception as e:
            self.last_error = f"抽奖登录异常: {str(e)}"
            return False

    def query_login(self):
        try:
            url = "https://my.tmlyun.com/equity-api/user/auth/userLogin"
            self.t = str(int(time.time() * 1000))
            random_float = random.uniform(1000, 9999)
            self.request_id = f"{random_float:.12f}|{self.t}"
            payload = {
                "u": self.u,
                "accountId": self.account_id,
                "sessionId": self.session_id,
            }
            headers = {
                'Content-Type': "application/json",
                'X-REQUEST-ID': self.request_id,
                'X-Requested-With': "com.zjonline.tiantai",
            }
            # 使用 session
            response = self.session.post(url, data=json.dumps(payload), headers=headers, verify=False, timeout=10)
            if self._safe_json(response).get("code") == 0:
                self.token = self._safe_json(response).get("data", {}).get("token", "")
                return True
            self.last_error = f"钱包登录失败: {self._safe_json(response).get('message')}"
            return False
        except: return False

    def get_wallet_info(self):
        try:
            self.t = str(int(time.time() * 1000))
            random_float = random.uniform(1000, 9999)
            self.request_id = f"{random_float:.12f}|{self.t}"
            url = "https://my.tmlyun.com/equity-api/redBag/getWalletInfo"
            params = {'device': self.ua.split(";")[1]}
            headers = {
                'User-Agent': self.ua,
                'X-REQUEST-ID': self.request_id,
                'Accept': "application/json, text/plain, */*",
                'Authorization': self.token,
            }
            # 使用 session
            response = self.session.get(url, params=params, headers=headers, verify=False, timeout=10)
            if self._safe_json(response).get("code") == 0:
                self.price = self._safe_json(response).get("data", {})[0].get("aliPayTotalPrice", 0)
                self.totalPrice = self._safe_json(response).get("data", {})[0].get("totalTransPrice", 0)
                return True
            self.last_error = f"获取钱包失败: {self._safe_json(response).get('message')}"
            return False
        except: return False

    def query_wallet_records(self):
        """新增：查询钱包流水记录"""
        try:
            url = "https://my.tmlyun.com/equity-api/redBag/pageWalletDetail"
            params = {
                'current': "1",
                'pageSize': "5",
                'fundsChannelType': "0"
            }
            self.t = str(int(time.time() * 1000))
            self.request_id = f"{random.uniform(1000, 9999):.12f}|{self.t}"
            headers = {
                'X-REQUEST-ID': self.request_id,
                'Authorization': self.token,
            }
            # 使用 session
            response = self.session.get(url, params=params, headers=headers, verify=False, timeout=10)
            
            if self._safe_json(response).get("code") == 0:
                data = self._safe_json(response).get("data", [])
                records = []
                for item in data:
                    # 格式化: 时间[金额][状态]
                    status_desc = "阅读红包" if item.get('type', 0) == 0 else (item.get('statusDesc', '未知') or "未知")
                    record_str = f"{item.get('createdAt', '')}[{item.get('price', 0)}][{status_desc}]"
                    records.append(record_str)
                return records
            return []
        except: return []

    def check_info(self):
        """执行全套查询逻辑"""
        try:
            # 1. 登录
            login_result = self.login()
            if login_result.get("code") != 0:
                return None
            
            nick_name = login_result['data']['account']['nick_name']
            
            # 2. 获取积分
            integral_data = self.g("/api/user_mumber/numberCenter?is_new=1")
            total_integral = integral_data.get("data", {}).get("rst", {}).get("total_integral", 0)
            
            # 3. 获取钱包及流水
            wallet_info = {"price": 0, "totalPrice": 0, "valid": False, "records": []}
            if self.q:
                # 嵌套判断，只要一步失败就返回，此时 last_error 已被设置
                if not self.lottery_login(): return None
                if not self.get_u(): return None
                if not self.query_login(): return None
                if not self.get_wallet_info(): return None
                
                wallet_info["price"] = self.price
                wallet_info["totalPrice"] = self.totalPrice
                wallet_info["valid"] = True
                # 获取记录
                wallet_info["records"] = self.query_wallet_records()

            return {
                "nickname": nick_name,
                "integral": total_integral,
                "wallet": wallet_info
            }
        except Exception as e:
            logger.error(f"查询出错: {e}")
            if not self.last_error:
                self.last_error = f"未知异常: {str(e)}"
            return None

# ===================== 管理器类 =====================
class RemarkManager:
    """账号备注管理器"""
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket=plugin_bucket('remarks'), key=f'{user_id}_{account_id}')
            if remark_data: return remark_data
            return ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = remark.strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket=plugin_bucket('remarks'), key=f'{user_id}_{account_id}', value=remark_clean)
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
                if remark: remarks[account] = remark
            return remarks
        except: return {}
    
    @staticmethod
    def delete_account_remark(user_id, account_id):
        try:
            middleware.bucketDel(bucket=plugin_bucket('remarks'), key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    """账号管理类"""
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket=plugin_bucket('user'), key=str(user_id))
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
            user_id = str(user_id)
            account = str(account)
            accounts = AccountManager.get_accounts(user_id)
            if account not in accounts:
                accounts.append(account)
                middleware.bucketSet(bucket=plugin_bucket('user'), key=user_id, value=str(accounts))
                return True
            return False
        except: return False
    
    @staticmethod
    def remove_account(user_id, account):
        try:
            user_id = str(user_id)
            account = str(account)
            accounts = AccountManager.get_accounts(user_id)
            if account in accounts:
                accounts.remove(account)
                if accounts:
                    middleware.bucketSet(bucket=plugin_bucket('user'), key=user_id, value=str(accounts))
                else:
                    middleware.bucketDel(bucket=plugin_bucket('user'), key=user_id)
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(user_id, account, token):
        try:
            encrypted_token = encrypt_token(str(token))
            middleware.bucketSet(bucket=plugin_bucket('token'), key=str(account), value=encrypted_token)
            return True
        except: return False

    @staticmethod
    def get_token(account):
        try:
            encrypted_token = middleware.bucketGet(bucket=plugin_bucket('token'), key=str(account))
            return decrypt_token(encrypted_token) if encrypted_token else ""
        except:
            return ""
    
    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket=plugin_bucket('user'))
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts: user_list.append(user)
            return user_list
        except: return []

class QingLongAPI:
    """系统对接API封装，兼容青龙/呆呆两种面板。"""
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
            if not all([self.QLurl, self.ClientID, self.ClientSecret]): raise ValueError("配置不完整")
            if self.panel_type == 'daidai':
                self.access_token = self._get_daidai_token()
            else:
                self.qltoken = self._get_token()
            self.enabled = True
        except Exception as e:
            logger.error("系统初始化失败: " + str(e))
            self.init_error = str(e)
    
    def _get_token(self):
        try:
            url = f"{self.QLurl}/open/auth/token?client_id={self.ClientID}&client_secret={self.ClientSecret}"
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()['data']['token']
            raise Exception("获取Token失败")
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
                if response.status_code == 200: return response.json().get('data', [])
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "accept": "application/json"}
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                if response.status_code == 200: return response.json()['data']
            return []
        except: return []
    
    def find_env_by_account(self, account, token=None):
        try:
            for env in self.get_all_envs():
                if env.get('name') != config['dd_hhtt_osname']: continue
                env_id = env.get('id') if env.get('id') is not None else env.get('_id')
                env_value = str(env.get('value') or '').strip()
                env_remarks = str(env.get('remarks') or env.get('remark') or '')
                if token and str(token).strip() in env_value: return env_id
                if env_remarks and str(account) in env_remarks: return env_id
            return None
        except: return None
    
    def delete_env(self, env_id):
        if not self.enabled or not env_id: return False
        try:
            if self.panel_type == 'daidai':
                url = f"{self.QLurl}/api/envs/{env_id}"
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                res = requests.delete(url, headers=headers, timeout=10, verify=False)
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                res = requests.delete(url, headers=headers, json=[env_id], timeout=10, verify=False)
            return res.status_code == 200
        except: return False

    def delete_env_by_account(self, account, token=None):
        try:
            env_id = self.find_env_by_account(account, token)
            if env_id:
                return self.delete_env(env_id)
            return False
        except:
            return False

    def sync_env(self, token, account, remark="", auth_time="", owner_user_id=None):
        if not self.enabled: return False
        try:
            env_id = self.find_env_by_account(account, token)
            if env_id:
                return self.update_env(env_id, token, account, account, remark, auth_time, owner_user_id)
            return self.add_env(token, account, account, remark, auth_time, owner_user_id)
        except:
            return False
    
    def add_env(self, token, account, phone, remark="", auth_time="", owner_user_id=None):
        if not self.enabled: return False
        try:
            phone_display = phone[:3] + '*' * 4 + phone[7:] if len(phone) >= 11 else phone
            remarks_parts = [f'和合:{account}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            owner_user = get_owner_user_id(account, owner_user_id)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'手机:{phone_display}', '和合管理'])

            if self.panel_type == 'daidai':
                url = f"{self.QLurl}/api/envs"
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                data = {"value": token, "name": config['dd_hhtt_osname'], "remarks": '丨'.join(remarks_parts)}
                res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                data = [{"value": token, "name": config['dd_hhtt_osname'], "remarks": '丨'.join(remarks_parts)}]
                res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
            return res.status_code == 200
        except: return False
    
    def update_env(self, env_id, token, account, phone, remark="", auth_time="", owner_user_id=None):
        if not self.enabled: return False
        try:
            phone_display = phone[:3] + '*' * 4 + phone[7:] if len(phone) >= 11 else phone
            remarks_parts = [f'和合:{account}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            owner_user = get_owner_user_id(account, owner_user_id)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'手机:{phone_display}', '和合管理'])

            if self.panel_type == 'daidai':
                url = f"{self.QLurl}/api/envs/{env_id}"
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                data = {"value": token, "name": config['dd_hhtt_osname'], "remarks": '丨'.join(remarks_parts)}
                res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                if res.status_code == 200:
                    try: requests.put(f"{self.QLurl}/api/envs/{env_id}/enable", headers=headers, timeout=5, verify=False)
                    except: pass
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                data = {"value": token, "name": config['dd_hhtt_osname'], "remarks": '丨'.join(remarks_parts)}
                if isinstance(env_id, int) or str(env_id).isdigit():
                    data["id"] = env_id
                else:
                    data["_id"] = env_id
                res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                if res.status_code == 200:
                    try: requests.put(f"{self.QLurl}/open/envs/enable", headers=headers, json=[env_id], timeout=5, verify=False)
                    except: pass
            return res.status_code == 200
        except: return False

try:
    ql_api = QingLongAPI()
    if not ql_api.enabled and sender.getImtype() != 'fake':
        sender.reply("⚠️ 系统API初始化失败，青龙/呆呆同步功能不可用，请检查配置。")
except Exception:
    ql_api = type('obj', (object,), {
        'enabled': False,
        'sync_env': lambda *a, **k: False,
        'delete_env': lambda *a, **k: False,
        'delete_env_by_account': lambda *a, **k: False,
        'find_env_by_account': lambda *a, **k: None,
        'update_env': lambda *a, **k: False,
        'add_env': lambda *a, **k: False,
    })()
    if sender.getImtype() != 'fake':
        sender.reply("⚠️ 系统API初始化异常，青龙/呆呆同步功能不可用，请检查配置。")

# ===================== 功能逻辑 =====================

def process_single_account(account, index, total_count, account_remarks):
    """处理单个账号查询"""
    try:
        account_display = mask_account(account)
        token_data = middleware.bucketGet(bucket=plugin_bucket('token'), key=f'{account}')
        if token_data:
            full_token = decrypt_token(token_data)
        else:
            full_token = None
        
        accountVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=f'{account}')
        
        remark = ""
        if config['enable_remark']:
            remark = account_remarks.get(account, "")
        
        today_time = str(datetime.now().date())
        if not accountVip:
            auth_time = "无"
        elif accountVip <= today_time:
            auth_time = f"{accountVip} (已过期)"
        else:
            auth_time = accountVip
        
        if accountVip and accountVip > today_time and full_token:
            try:
                # 解析 Token: 手机#密码#q 或 手机#密码
                parts = full_token.split('#')
                if len(parts) >= 2:
                    phone, pwd = parts[0], parts[1]
                    q = parts[2] if len(parts) >= 3 else ""
                    
                    if q and "http" in q and "q=" not in q:
                        return f"""
=====配置错误提醒=====
📝 备注: {remark if remark else account_display}
🔑 账号: {account_display}
❌ 错误: 检测到您上传的是[邀请链接]而非[抽奖链接]
💡 解决: Q值无效，请重新发送 [{config['randomsigncommand']}] 录入正确格式
=================="""

                    client = HeHeTianTai(phone, pwd, q)
                    info = client.check_info()
                    
                    if not info:
                        # 3. 修复：返回具体的错误原因，不再只有“失败”两个字
                        error_reason = client.last_error if client.last_error else "未知连接错误"
                        raise Exception(error_reason)
                    
                    # 格式化记录
                    recs = info['wallet'].get('records', [])
                    rec_str = "\n".join(recs) if recs else "暂无记录"
                    
                    account_info = f"""
📝 【备注名称】 : {remark if remark else account_display}
📛 【用户昵称】 : {info['nickname']}
🏆 【当前积分】 : {info['integral']}
💵 【当前余额】 : {info['wallet']['price']}
💴 【累计提现】 : {info['wallet']['totalPrice']}
⏰ 【授权时间】 : {auth_time}
------------------------------
🎁 最近 5 次钱包记录:
{rec_str}
"""
                    return account_info.strip()
                else:
                    return f"❌ 账号 {account_display} 格式错误"
            except Exception as e:
                # 显示具体错误内容
                return f"""
=====和合查询失败=====
🔑 账号: {account_display}
❌ 原因: {str(e)[:50]}...
=================="""
        else:
            return f"""
📝 【备注名称】 : {remark if remark else account_display}
🔑 【登录账号】 : {account_display}
🔐 【授权状态】 : {'⚠️ 未授权' if not accountVip else '❌ 已过期'}
⏰ 【授权时间】 : {auth_time}
"""
    except Exception as e:
        return None

def cxs():
    """批量查询"""
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
        menu = "=====和合查询====="
        for i, acc in enumerate(accounts, 1):
            acc = str(acc)
            remark = account_remarks.get(acc, "") if config['enable_remark'] else ""
            vip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=acc)
            if not vip:
                vip_tag = '⚠️未授权'
            elif vip < today_time:
                vip_tag = '❌已过期'
            else:
                vip_tag = f'✅{vip}'
            remark_disp = f" [{remark}]" if remark else ""
            menu += f"\n[{i}] {mask_account(acc)}{remark_disp} {vip_tag}"
        menu += "\n------------------\n[a] 查询全部\n支持单选/多选/区间，如 1,2 或 3-6\n回复q退出\n=================="
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
        
        sender.reply(f"🚀 正在并发查询 {len(target_accounts)} 个账号，请稍候...")

        max_workers = min(10, len(target_accounts))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_account = {}
            for index, account in target_accounts:
                future = executor.submit(process_single_account, account, index, total_count, account_remarks)
                future_to_account[future] = account

            for future in as_completed(future_to_account):
                result_msg = future.result()
                if result_msg: sender.reply(result_msg)
                
    except Exception as e:
        logger.error("批量查询失败: " + str(e))
        sender.reply("❌ 查询失败: " + str(e))

def get_user_input(timeout=60):
    """获取用户输入"""
    try:
        response = sender.listen(timeout * 1000)
        if not response: return None
        response = response.strip()
        if response.lower() in ['q', 'quit', 'exit', '退出', 'cancel']: return 'q'
        return response
    except: return None

def listen_payment_cancel(interval_ms=500):
    """支付等待期间短轮询取消指令，避免长时间占用后续菜单输入。"""
    try:
        msg = sender.listen(interval_ms)
        if not msg:
            return False
        msg = str(msg).strip().lower()
        return msg in ['q', 'quit', 'exit', '退出', 'cancel', '取消']
    except:
        return False

def is_cancel_input(value):
    try:
        return str(value).strip().lower() in ['q', 'quit', 'exit', '退出', 'cancel', '取消']
    except:
        return False

def cancel_payment_reply():
    sender.reply("✅ 已取消支付")

def parse_waitpay_result(res):
    try:
        if isinstance(res, dict):
            money = res.get('Money', res.get('money', 0))
            payer = res.get('FromName', res.get('fromName', ''))
        else:
            data = json.loads(str(res))
            money = data.get('Money', data.get('money', 0))
            payer = data.get('FromName', data.get('fromName', ''))
        return float(money or 0), payer
    except:
        return None, ""

def validate_wx_payment(res, expected_amount):
    if is_cancel_input(res):
        cancel_payment_reply()
        return False
    if not res:
        sender.reply("❌ 支付超时，请重新发起。")
        return False
    money, payer = parse_waitpay_result(res)
    if money is None:
        sender.reply("❌ 无法解析支付结果，请联系管理员核对")
        return False
    if float(money) >= float(expected_amount):
        return True
    sender.reply(f"=====支付金额错误=====\n💰 应付: {expected_amount}元\n💳 实付: {money}元\n👤 付款人: {payer}\n❗ 请联系管理员处理退款！")
    return False

def wait_epay_result(query_url, timeout_seconds=180, check_interval=3):
    """等待易支付结果；优先监听取消，避免查单请求长时间占用用户输入。"""
    start_time = time.time()
    next_query_time = 0
    while time.time() - start_time < timeout_seconds:
        if listen_payment_cancel(500):
            cancel_payment_reply()
            return "cancel"

        now = time.time()
        if now < next_query_time:
            continue

        next_query_time = now + check_interval
        try:
            res = requests.get(query_url, timeout=1).json()
            if str(res.get('code')) == '1' and str(res.get('status')) == '1':
                return "paid"
        except:
            pass
    return "timeout"

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

def split_login_entries(input_text):
    """解析批量登录输入，支持换行、&、中文逗号等分隔。"""
    text = str(input_text or "").strip()
    if not text:
        return []
    parts = re.split(r'[\r\n&]+', text)
    entries = []
    for part in parts:
        item = str(part or "").strip().strip('，,；;')
        if item:
            entries.append(item)
    return entries

def validate_login_entry(entry, require_q_link=False):
    """校验单条登录数据，返回(ok, phone, pwd, q, error_message)。"""
    parts = [str(x).strip() for x in str(entry or "").split('#')]
    if require_q_link:
        if len(parts) < 3:
            return False, "", "", "", "❌ 格式错误，请按照 手机号#密码#Q值的分享链接 格式输入"
        phone, pwd = parts[0], parts[1]
        q = '#'.join(parts[2:]).strip()
        if "q=" not in q:
            return False, phone, pwd, q, (
                "❌ Q值链接错误！\n"
                "请提交包含 [q=] 的抽奖链接\n"
                "通常格式为: https://act.tmlyun.com/lottery/?q=xxxx"
            )
        return True, phone, pwd, q, ""
    if len(parts) < 2:
        return False, "", "", "", "❌ 格式错误，请按照 手机号#密码 格式输入"
    phone, pwd = parts[0], parts[1]
    return True, phone, pwd, "", ""

def execute_single_bind(entry, remark=""):
    """执行单个账号登录并绑定，返回结果字典。"""
    require_q_link = config.get('require_q_link', False)
    ok, phone, pwd, q, error_msg = validate_login_entry(entry, require_q_link=require_q_link)
    if not ok:
        return {"success": False, "phone": phone, "message": error_msg}

    client = HeHeTianTai(phone, pwd, q)
    login_res = client.login()
    if login_res.get("code") != 0:
        return {
            "success": False,
            "phone": phone,
            "message": f"❌ 登录失败: {login_res.get('message', '未知错误')}"
        }

    nick = login_res['data']['account']['nick_name']
    bind_msg = process_account_binding(entry, phone, nick, remark, reply=False)
    return {
        "success": True,
        "phone": phone,
        "nickname": nick,
        "message": bind_msg
    }

def bindaccount():
    """绑定账号"""
    try:
        remark = ""
        if config['enable_remark']:
            sender.reply("""
=====账号备注设置=====
🎯 请输入账号备注名
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

        if config.get('require_q_link', False):
            sender.reply("""
=====和合账号登录=====
请输入格式：
手机号#密码#带q值的分享链接
支持批量：一行一个，或用 & 分隔
------------------
例如: 13800000000#123456#https://act.tmlyun.com...
例如: 13800000000#123456#https://act.tmlyun.com...&13900000000#654321#https://act.tmlyun.com...
------------------
回复"q"退出操作
==================""")
        else:
            sender.reply("""
=====和合账号登录=====
请输入格式：
手机号#密码
支持批量：一行一个，或用 & 分隔
------------------
例如: 13800000000#123456
例如: 13800000000#123456&13900000000#654321
------------------
回复"q"退出操作
==================""")
        
        input_str = get_user_input(timeout=120)
        if not input_str or input_str == 'q':
            sender.reply("✅ 已取消")
            return

        entries = split_login_entries(input_str)
        if not entries:
            sender.reply("❌ 未识别到有效账号数据")
            return

        if len(entries) == 1:
            sender.reply("⏳ 正在登录验证中，请稍候...")
            result = execute_single_bind(entries[0], remark=remark)
            if result["success"]:
                sender.reply(result["message"])
            else:
                sender.reply(result["message"])
            return

        sender.reply(f"⏳ 检测到 {len(entries)} 个账号，正在批量登录验证，请稍候...")
        success_count = 0
        fail_msgs = []
        success_preview = []

        for idx, entry in enumerate(entries, 1):
            result = execute_single_bind(entry, remark=remark)
            account_tip = mask_account(result.get("phone") or f"第{idx}个账号")
            if result["success"]:
                success_count += 1
                success_preview.append(f"{idx}. {account_tip}")
            else:
                fail_msgs.append(f"{idx}. {account_tip} {result['message'].replace(chr(10), ' ')}")

        msg_lines = [
            "=====批量登录结果=====",
            f"总数量: {len(entries)}",
            f"成功: {success_count}",
            f"失败: {len(fail_msgs)}",
        ]
        if success_preview:
            msg_lines.append("------------------")
            msg_lines.append("✅ 成功账号:")
            msg_lines.extend(success_preview[:15])
            if len(success_preview) > 15:
                msg_lines.append(f"... 另有 {len(success_preview) - 15} 个成功账号")
        if fail_msgs:
            msg_lines.append("------------------")
            msg_lines.append("❌ 失败账号:")
            msg_lines.extend(fail_msgs[:15])
            if len(fail_msgs) > 15:
                msg_lines.append(f"... 另有 {len(fail_msgs) - 15} 个失败账号")
        if success_count:
            msg_lines.append("------------------")
            msg_lines.append(f"下一步可发送 {config['randommanagecommand']} 进行授权或管理")
        msg_lines.append("==================")
        sender.reply("\n".join(msg_lines))
            
    except Exception as e:
        logger.error("绑定失败: " + str(e))
        sender.reply("❌ 绑定失败: " + str(e))

def process_account_binding(full_token, phone, nickname, remark="", reply=True):
    """处理绑定入库"""
    try:
        account = phone
        accountVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=account)
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
        
        existing_accounts = AccountManager.get_accounts(userid)
        if account in existing_accounts:
            AccountManager.update_account_token(userid, account, full_token)
        else:
            AccountManager.add_account(userid, account)
            encrypted_token = encrypt_token(full_token)
            middleware.bucketSet(bucket=plugin_bucket('token'), key=account, value=encrypted_token)
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account, remark)
        
        ql_msg = ""
        if is_authorized:
            try:
                qlid = ql_api.find_env_by_account(account, full_token)
                if qlid:
                    ql_api.update_env(qlid, full_token, account, phone, remark, auth_time=accountVip)
                else:
                    ql_api.add_env(full_token, account, phone, remark, auth_time=accountVip)
                ql_msg = "\n🔄 状态: ✅ 已同步到系统"
            except:
                ql_msg = "\n🔄 状态: ❌ 系统同步失败"
        else:
            ql_msg = "\n🔄 状态: ⏸️ 未授权，暂不提交"
        
        message = f"""
=====和合账号绑定=====
✅ 绑定成功!
👤 用户: {nickname}
🔑 账号: {mask_account(phone)}{remark_info}
🔐 授权: {auth_status}{ql_msg}
⏰ 下一步操作: 
   {next_step}
=================="""
        if reply:
            sender.reply(message)
        return message
    except Exception as e:
        err = f"绑定处理异常: {str(e)}"
        if reply:
            sender.reply(err)
        return err

# ===================== 支付与管理 =====================
def xy_manage():
    accounts = AccountManager.get_accounts(userid)
    if not accounts:
        sender.reply(f"❌ 未找到账号，请发送 {config['randomsigncommand']} 绑定")
        return
    
    account_remarks = RemarkManager.get_all_remarks(userid) if config['enable_remark'] else {}
    count = len(accounts)
    account_list = "======我的和合账号====="
    today_time = str(datetime.now().date())

    for i, account in enumerate(accounts, 1):
        account = str(account)
        accountVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=f'{account}')
        if not accountVip: vip_status = '⚠️ 未授权'
        elif accountVip < today_time: vip_status = '❌ 已过期'
        else: vip_status = f'✅ {accountVip}'
        
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        account_display = get_account_display(account, remark)
        
        account_list += f"\n------------------\n[{i}] 账号: {account_display}\n🔐 授权: {vip_status}"
        
    account_list += "\n------------------\n[b] 批量授权\n[d] 批量删除\n[q] 退出管理\n提示: 可回复 1,2 或 3-6 多选管理\n=================="
    sender.reply(account_list)
    
    response = get_user_input()
    if not response or response == 'q':
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
    if not sel or sel.lower() == 'q':
        return
    
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
    if not sel or sel.lower() == 'q':
        return
    
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
        encrypted_token = middleware.bucketGet(bucket=plugin_bucket('token'), key=f'{account}')
        token = decrypt_token(encrypted_token) if encrypted_token else ""
        accountVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=f'{account}')
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        sender.reply(f"""
=====账号详情=====
🔑 账号: {mask_account(account)}
📝 备注: {remark}
🔐 授权: {vip_status}
==================
[1] 授权账号
[2] 删除账号
[3] 修改备注
------------------
回复数字选择，Q退出
==================""")
        
        choice = get_user_input()
        if not choice or choice == 'q': return
        
        if choice == '1': # 授权
            sender.reply("请输入授权月数(如:1)，Q退出")
            months_str = get_user_input()
            if not months_str or months_str == 'q': return
            try:
                months = int(months_str)
                if months <= 0: raise ValueError
            except:
                sender.reply("❌ 数字无效")
                return
            
            if process_payment('和合授权', months, accountVip, token, account, account, account, remark):
                days = months * 30
                new_auth_time = empower(accountVip, days)
                middleware.bucketSet(bucket=plugin_bucket('auth'), key=f'{account}', value=new_auth_time)
                
                if token:
                    try:
                        qlid = ql_api.find_env_by_account(account, token)
                        if qlid: ql_api.update_env(qlid, token, account, account, remark, new_auth_time)
                        else: ql_api.add_env(token, account, account, remark, new_auth_time)
                        sender.reply("🔄 授权成功并同步到系统！")
                    except: sender.reply("⚠️ 授权成功但系统同步失败")
                
                money = Decimal(months) * config['xyVipmoney']
                sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")

        elif choice == '2': # 删除
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                AccountManager.remove_account(userid, account)
                qlid = ql_api.find_env_by_account(account, token)
                if qlid: ql_api.delete_env(qlid)
                middleware.bucketDel(bucket=plugin_bucket('token'), key=account)
                middleware.bucketDel(bucket=plugin_bucket('auth'), key=account)
                if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                sender.reply("✅ 删除成功")

        elif choice == '3': # 备注
             sender.reply("请输入新备注:")
             new_remark = get_user_input()
             if new_remark and new_remark != 'q':
                 RemarkManager.set_account_remark(userid, account, new_remark)
                 if token:
                     qlid = ql_api.find_env_by_account(account, token)
                     if qlid: ql_api.update_env(qlid, token, account, account, new_remark, accountVip)
                 sender.reply("✅ 备注更新成功")

    except Exception as e:
        sender.reply(f"操作失败: {e}")

def process_payment(project, months, accountVip, token, phone, account, yt_account, remark=""):
    """支付处理"""
    money = Decimal(months) * config['xyVipmoney']
    points_needed = config['xycoin'] * months
    user_points, points_bucket = get_user_points()
    
    options = []
    idx = 1
    if config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '微信支付', 'amount': money})
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
    if not sel or sel == 'q':
        cancel_payment_reply()
        return False
    
    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError
        
        if opt['type'] == 'wx':
            if sender.atWaitPay(): 
                sender.reply("⚠️ 当前有人支付中")
                return False
            out_trade_no = f"WX_{int(time.time())}_{random.randint(100,999)}"
            sender.reply(f"=====等待支付=====\n💰 金额: {opt['amount']}元\n💳 方式: 微信收款\n📋 订单: {out_trade_no}\n------------------\n请在 60 秒内完成扫码支付\n回复\"q\"取消支付")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            return validate_wx_payment(res, opt['amount'])
            
        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply("❌ 积分不足")
                return False
            sender.reply("确认支付回复【y】")
            confirm = get_user_input()
            if is_cancel_input(confirm) or not confirm:
                cancel_payment_reply()
                return False
            if confirm == 'y':
                new_pt = int(opt['curr']) - int(opt['amount'])
                set_user_points(new_pt, points_bucket)
                return True
            sender.reply("✅ 已取消支付")
            return False

        elif opt['type'] == 'epay':
            out_trade_no = f"HHTT_EPAY_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
            formatted_money = f"{float(opt['amount']):.2f}"
            channel_name = "支付宝" if opt['channel'] == 'alipay' else ("微信支付" if opt['channel'] == 'wxpay' else "QQ钱包")
            qr_image_url, _ = _create_epay_qr(out_trade_no, opt['channel'], f"和合授权-{months}月", formatted_money)
            sender.reply(f"=====等待支付=====\n💰 金额: {formatted_money}元\n💳 方式: {channel_name}\n📋 订单: {out_trade_no}\n------------------\n请在 180 秒内完成扫码支付\n回复\"q\"取消支付")
            sender.replyImage(qr_image_url)
            query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
            pay_result = wait_epay_result(query_url, timeout_seconds=180, check_interval=3)
            if pay_result == "paid":
                return True
            if pay_result == "cancel":
                return False
            sender.reply("❌ 支付超时，请重新发起。")
            return False
            
        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"HHTT{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"和合授权-{months}月",
                'money': str(opt['amount']),
                'notify_url': '', 'return_url': '', 'param': userid
            }
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + conf['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            url = conf['gateway'].rstrip('/') + '/submit.php'
            res = requests.post(url, data=params, timeout=5)
            if 'http' in res.text:
                 sender.reply("请完成支付后联系管理员；如需取消请回复 q")
                 if listen_payment_cancel(5000):
                     cancel_payment_reply()
                     return False
                 return False
            return False

    except Exception as e:
        logger.error(f"支付异常: {e}")
        sender.reply("❌ 支付异常")
        return False

def batch_auth_selected(accounts, account_remarks):
    sender.reply(f"已选择 {len(accounts)} 个账号\n请输入授权月数，Q退出")
    m = get_user_input()
    if not m or not m.isdigit(): return
    months = int(m)
    if months <= 0: return
    
    count = len(accounts)
    total_money = Decimal(months) * config['xyVipmoney'] * count
    total_points = config['xycoin'] * months * count
    user_points, points_bucket = get_user_points()

    options = []
    idx = 1
    if config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '微信支付', 'amount': total_money})
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
    if not sel or sel == 'q':
        cancel_payment_reply()
        return

    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError

        if opt['type'] == 'wx':
            if sender.atWaitPay(): 
                sender.reply("⚠️ 当前有人支付中")
                return
            out_trade_no = f"WX_BATCH_{int(time.time())}_{random.randint(100,999)}"
            sender.reply(f"=====等待支付=====\n💰 金额: {opt['amount']}元\n💳 方式: 微信收款\n📋 订单: {out_trade_no}\n------------------\n请在 60 秒内完成扫码支付\n回复\"q\"取消支付")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            if not validate_wx_payment(res, opt['amount']):
                return
        
        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply(f"❌ 积分不足，需要 {opt['amount']}，当前 {opt['curr']}")
                return
            sender.reply(f"确认消耗 {opt['amount']} 积分？回复【y】")
            confirm = get_user_input()
            if is_cancel_input(confirm) or not confirm:
                cancel_payment_reply()
                return
            if confirm != 'y':
                sender.reply("✅ 已取消支付")
                return
            new_pt = int(opt['curr']) - int(opt['amount'])
            set_user_points(new_pt, points_bucket)

        elif opt['type'] == 'epay':
            out_trade_no = f"HHTT_BATCH_EPAY_{int(time.time())}_{userid}_{random.randint(1000,9999)}"
            formatted_money = f"{float(opt['amount']):.2f}"
            channel_name = "支付宝" if opt['channel'] == 'alipay' else ("微信支付" if opt['channel'] == 'wxpay' else "QQ钱包")
            qr_image_url, _ = _create_epay_qr(out_trade_no, opt['channel'], f"和合批量-{count}号-{months}月", formatted_money)
            sender.reply(f"=====等待支付=====\n💰 金额: {formatted_money}元\n💳 方式: {channel_name}\n📋 订单: {out_trade_no}\n------------------\n请在 180 秒内完成扫码支付\n回复\"q\"取消支付")
            sender.replyImage(qr_image_url)
            query_url = f"{config['epay_url'].rstrip('/')}/api.php?act=order&pid={config['epay_pid']}&key={config['epay_key']}&out_trade_no={out_trade_no}"
            pay_result = wait_epay_result(query_url, timeout_seconds=180, check_interval=3)
            if pay_result == "cancel":
                return
            if pay_result != "paid":
                sender.reply("❌ 支付超时，请重新发起。")
                return

        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"HHTT_BATCH_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"和合批量-{count}号-{months}月",
                'money': str(opt['amount']),
                'notify_url': '', 'return_url': '', 'param': userid
            }
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + conf['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            url = conf['gateway'].rstrip('/') + '/submit.php'
            res = requests.post(url, data=params, timeout=5)
            if 'http' in res.text:
                sender.reply("请完成支付后联系管理员；如需取消请回复 q")
                if listen_payment_cancel(5000):
                    cancel_payment_reply()
                    return
                return
            else:
                 sender.reply("❌ 创建订单失败")
                 return

    except Exception:
        sender.reply("❌ 输入错误或支付取消")
        return

    sender.reply(f"🚀 支付成功，正在处理 {count} 个账号...")
    for account in accounts:
        try:
            accountVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=account)
            new_date = empower(accountVip, months*30)
            middleware.bucketSet(plugin_bucket('auth'), account, new_date)
            
            encrypted_token = middleware.bucketGet(bucket=plugin_bucket('token'), key=account)
            token = decrypt_token(encrypted_token) if encrypted_token else None
            
            curr_remark = account_remarks.get(account, "") if account_remarks else ""
            
            if token:
                 try:
                     qid = ql_api.find_env_by_account(account, token)
                     if qid: ql_api.update_env(qid, token, account, account, curr_remark, new_date)
                     else: ql_api.add_env(token, account, account, curr_remark, new_date)
                 except: pass
        except: pass
    
    sender.reply("✅ 批量授权完成")

def batch_auth_all_accounts(accounts, account_remarks):
    return batch_auth_flow(accounts, account_remarks)

def batch_delete_selected(accounts):
    preview = []
    for account in accounts[:5]:
        preview.append(str(account))
    more = f"\n...等 {len(accounts)} 个账号" if len(accounts) > 5 else ""
    sender.reply(f"=====确认批量删除=====\n已选择 {len(accounts)} 个账号\n{chr(10).join(preview)}{more}\n------------------\n确认删除请回复【确认删除】\n回复 q 取消\n==================")
    if get_user_input() != "确认删除":
        sender.reply("✅ 已取消删除")
        return

    today_date = datetime.now().date()
    for account in accounts:
        try:
            account = str(account)
            token = AccountManager.get_token(account)
            ql_api.delete_env_by_account(account, token)
            AccountManager.remove_account(userid, account)
            try: middleware.bucketDel(bucket=plugin_bucket('token'), key=account)
            except: pass
            try: middleware.bucketDel(bucket=plugin_bucket('auth'), key=account)
            except: pass
            if config['enable_remark']:
                RemarkManager.delete_account_remark(userid, account)
            for d in range(config['reminder_days'] + 1):
                remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                try: middleware.bucketDel(plugin_bucket('remind_log'), remind_key)
                except: pass
        except Exception as e:
            logger.warning(f"批量删除账号失败 {account}: {e}")
    sender.reply("✅ 批量删除完成")

def batch_delete_all_accounts(accounts):
    sender.reply("确认删除回复【确认删除】")
    if get_user_input() == "确认删除":
        for account in accounts:
             encrypted_token = middleware.bucketGet(bucket=plugin_bucket('token'), key=account)
             token = decrypt_token(encrypted_token) if encrypted_token else None
             qlid = ql_api.find_env_by_account(account, token)
             if qlid: ql_api.delete_env(qlid)
             middleware.bucketDel(bucket=plugin_bucket('token'), key=account)
             middleware.bucketDel(bucket=plugin_bucket('auth'), key=account)
             if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
        middleware.bucketDel(bucket=plugin_bucket('user'), key=userid)
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts(force_report=False):
    """清理过期账号并处理到期提醒"""
    try:
        users = AccountManager.get_all_users()
        if not users:
            if sender.isAdmin() and (force_report or usermessage in ['和合清理', '清理和合']):
                sender.reply("=====执行结果=====\n📭 暂无用户数据")
            return {
                "report_date": str(datetime.now().date()),
                "scanned_users": 0,
                "scanned_accounts": 0,
                "sent_notifications": 0,
                "ck_expired_count": 0,
                "unauth_panel_cleaned_count": 0,
                "cleaned_count": 0,
                "reminded_count": 0,
            }

        if sender.isAdmin() and (force_report or usermessage in ['和合清理', '清理和合']):
            sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n⚙️ 提醒天数: {config['reminder_days']}天\n⏳ 处理中...")

        scanned_accounts = 0
        cleaned_count = 0
        reminded_count = 0
        unauth_panel_cleaned_count = 0
        today_date = datetime.now().date()
        
        for user in users:
            try:
                user_sender = middleware.Sender(str(user))
                valid_accounts = []
                user_has_change = False
                for account in AccountManager.get_accounts(user):
                    account = str(account)
                    scanned_accounts += 1
                    accountVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=account)
                    if not accountVip:
                        token = AccountManager.get_token(account)
                        try:
                            if ql_api.delete_env_by_account(account, token):
                                unauth_panel_cleaned_count += 1
                        except Exception as e:
                            logger.warning(f"未授权账号面板清理失败 {account}: {e}")
                        valid_accounts.append(account)
                        continue

                    try:
                        expiration_date = datetime.strptime(str(accountVip), "%Y-%m-%d").date()
                        expiration_str = str(accountVip)
                    except:
                        expiration_date = today_date - timedelta(days=1)
                        expiration_str = "日期错误"

                    days_diff = (expiration_date - today_date).days
                    if days_diff >= 0:
                        valid_accounts.append(account)
                        if days_diff <= config['reminder_days']:
                            remind_key = f"{user}_{account}_{today_date}"
                            if not middleware.bucketGet(plugin_bucket('remind_log'), remind_key):
                                msg = f"""=====⏰ 到期提醒=====
您的和合账号授权即将到期！
🔑 账号: {mask_account(account)}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                                if safe_send_message(user, msg, f"到期提醒 {user}-{account}"):
                                    try: middleware.bucketSet(plugin_bucket('remind_log'), remind_key, "1")
                                    except: pass
                                    reminded_count += 1
                        continue

                    token = AccountManager.get_token(account)
                    ql_api.delete_env_by_account(account, token)
                    try: middleware.bucketDel(bucket=plugin_bucket('token'), key=account)
                    except: pass
                    try: middleware.bucketDel(bucket=plugin_bucket('auth'), key=account)
                    except: pass
                    if config['enable_remark']:
                        RemarkManager.delete_account_remark(user, account)
                    clean_msg = f"""=====🗑️ 过期清理通知=====
您的和合账号授权已过期并清理。
🔑 账号: {mask_account(account)}
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
                        try: middleware.bucketSet(bucket=plugin_bucket('user'), key=str(user), value=str(valid_accounts))
                        except: pass
                    else:
                        try: middleware.bucketDel(bucket=plugin_bucket('user'), key=str(user))
                        except: pass
            except Exception as e:
                logger.warning(f"维护用户失败 {user}: {e}")

        if sender.isAdmin() and (force_report or usermessage in ['和合清理', '清理和合']):
            sender.reply(
                f"=====和合维护完成=====\n"
                f"✅ 检测完成，共 {scanned_accounts} 个账号\n"
                f"📢 授权提醒: {reminded_count} 个\n"
                f"🧹 未授权面板清理: {unauth_panel_cleaned_count} 个\n"
                f"🗑️ 清理过期: {cleaned_count} 个\n"
                f"=================="
            )

        return {
            "report_date": str(today_date),
            "scanned_users": len(users),
            "scanned_accounts": scanned_accounts,
            "sent_notifications": reminded_count + cleaned_count,
            "ck_expired_count": 0,
            "unauth_panel_cleaned_count": unauth_panel_cleaned_count,
            "cleaned_count": cleaned_count,
            "reminded_count": reminded_count,
        }
            
    except Exception as e:
        logger.error(f"清理任务执行异常: {e}")
        if usermessage in ['和合清理', '清理和合'] or force_report:
            sender.reply(f"❌ 清理过程发生异常: {str(e)}")
        return {
            "report_date": str(datetime.now().date()),
            "scanned_users": 0,
            "scanned_accounts": 0,
            "sent_notifications": 0,
            "ck_expired_count": 0,
            "unauth_panel_cleaned_count": 0,
            "cleaned_count": 0,
            "reminded_count": 0,
        }

def admin_auth_options():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足\n只有管理员可以执行授权操作")
        return

    sender.reply("""=====和合管理员管理=====

[1] 一键授权所有用户
[2] 指定用户授权 (支持加减时间)
[3] 数据总览
[4] 用户CK预览
[5] 反查账号归属
[6] 同步面板变量(已撤销)
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
        sender.reply("⚠️ 同步面板变量功能已撤销，避免面板备注/归属覆盖本地账号数据。")
    elif choice == '7':
        report_data = clean_expired_accounts(force_report=True)
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
                if not AccountManager.get_token(account):
                    stats["no_token"] += 1
                vip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=account)
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
    sender.reply(f"""=====和合数据总览=====
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
    total_parts = len(chunks)
    for part, chunk in enumerate(chunks, 1):
        page_tip = f"\n-----第 {part}/{total_parts} 段-----" if total_parts > 1 else ""
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
                vip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=account)
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
    lines = [f"👥 用户数: {len(rows)}  📦 CK总数: {total_accounts}", "------------------"]
    for i, row in enumerate(rows, 1):
        extra = []
        if row["unauth"]:
            extra.append(f"未授权{row['unauth']}")
        if row["expired"]:
            extra.append(f"过期{row['expired']}")
        if row["expiring"]:
            extra.append(f"临期{row['expiring']}")
        if row["no_token"]:
            extra.append(f"缺CK{row['no_token']}")
        extra_text = f" ({' / '.join(extra)})" if extra else ""
        lines.append(f"[{i}] 用户: {row['user']}\nCK: {row['count']} 个  授权: {row['auth']} 个{extra_text}")

    send_long_admin_message("=====用户CK预览=====", lines)

def admin_find_account():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足")
        return
    sender.reply("""=====反查账号归属=====
请输入账号/备注/用户ID
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
                vip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=account)
                vip_st = '未授权' if not vip else str(vip)
                if user_match or keyword in account or (remark and keyword in remark):
                    remark_text = f"\n📝 备注: {remark}" if remark else ""
                    matches.append(f"👤 用户: {user}\n🔑 账号: {mask_account(account)}{remark_text}\n🔐 授权: {vip_st}")
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
    sender.reply("⚠️ 同步面板变量功能已撤销，避免面板备注/归属覆盖本地账号数据。")

def admin_auth_all_users():
    all_users = AccountManager.get_all_users()
    if not all_users:
        sender.reply("📭 暂无绑定账号的用户")
        return

    sender.reply("请输入授权天数(正数增加，负数如 -10 扣除):\n回复q退出")
    days_str = get_user_input()
    if not days_str or days_str.lower() == 'q':
        return
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
        remarks = RemarkManager.get_all_remarks(user) if config['enable_remark'] else {}
        for account in AccountManager.get_accounts(user):
            try:
                account = str(account)
                accVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=account)
                new_vip = empower(accVip, days)
                middleware.bucketSet(bucket=plugin_bucket('auth'), key=account, value=new_vip)
                token = AccountManager.get_token(account)
                remark = remarks.get(account, "")
                if token:
                    ql_api.sync_env(token, account, remark, new_vip)
                success += 1
            except:
                pass
    sender.reply(f"✅ 一键授权完成！成功处理 {success} 个账号。")

def admin_auth_specific_user():
    sender.reply("请输入该用户的奥特曼用户标识(QQ号或微信wxid):\n回复q退出")
    target_qq = get_user_input()
    if not target_qq or target_qq.lower() == 'q':
        return
    target_qq = target_qq.strip()

    target_accounts = AccountManager.get_accounts(target_qq)
    if not target_accounts:
        sender.reply(f"❌ 用户 {target_qq} 未绑定任何账号")
        return

    account_remarks = RemarkManager.get_all_remarks(target_qq) if config['enable_remark'] else {}
    msg = f"=====用户 {target_qq} 的账号====="
    for i, acc in enumerate(target_accounts, 1):
        acc = str(acc)
        accVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=acc)
        vip_st = '未授权' if not accVip else f"已授权({accVip})"
        rem = account_remarks.get(acc, "")
        rem_disp = f" - {rem}" if rem else ""
        msg += f"\n[{i}] {mask_account(acc)}{rem_disp} - {vip_st}"
    msg += "\n------------------\n回复 a 操作所有账号\n支持单选/多选/区间，如 1,2 或 3-6\n回复 q 退出\n=================="
    sender.reply(msg)

    sel = get_user_input()
    if not sel or sel.lower() == 'q':
        return

    selected_idxs, invalid_parts = parse_index_selection(sel, len(target_accounts), allow_all=True)
    selected_accs = pick_accounts_by_indexes(target_accounts, selected_idxs)
    if not selected_accs:
        sender.reply("❌ 序号无效，请回复如 1,2 或 3-6")
        return
    if invalid_parts:
        sender.reply(f"⚠️ 已忽略无效内容: {','.join(invalid_parts[:5])}")

    sender.reply(f"已选择 {len(selected_accs)} 个账号\n请输入改变的天数(正数增加，负数如 -10 扣除):")
    d_str = get_user_input()
    if not d_str:
        return
    try:
        days = int(d_str)
    except:
        sender.reply("❌ 无效天数")
        return

    success = 0
    latest_dates = []
    for acc in selected_accs:
        try:
            acc = str(acc)
            accVip = middleware.bucketGet(bucket=plugin_bucket('auth'), key=acc)
            new_vip = empower(accVip, days)
            middleware.bucketSet(bucket=plugin_bucket('auth'), key=acc, value=new_vip)
            token = AccountManager.get_token(acc)
            remark = account_remarks.get(acc, "")
            if token:
                ql_api.sync_env(token, acc, remark, new_vip)
            success += 1
            latest_dates.append(new_vip)
        except:
            pass

    date_tip = latest_dates[0] if latest_dates and len(set(latest_dates)) == 1 else "多个日期"
    sender.reply(f"✅ 已操作 {success} 个账号 {days} 天\n⏰ 最新到期: {date_tip}")

def notify_authorized_users():
    if not sender.isAdmin():
        sender.reply("❌ 只有管理员可以使用此功能")
        return

    content = ""
    match = re.search(r'(和合广播|和合通知) ?(.*)', usermessage)
    if match:
        content = match.group(2).strip()

    if not content:
        sender.reply("❌ 请输入通知内容，例如：和合通知 系统维护中")
        return

    sender.reply("⏳ 正在扫描授权用户并发送通知...")
    try:
        all_users = AccountManager.get_all_users()
        success_count = 0
        today = str(datetime.now().date())
        for uid in all_users:
            has_auth = False
            for acc in AccountManager.get_accounts(uid):
                vip_date = middleware.bucketGet(bucket=plugin_bucket('auth'), key=str(acc))
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            if has_auth:
                try:
                    ok, _ = send_user_notice(uid, f"📢 【和合管理员通知】\n\n{content}", "和合管理员通知")
                    if ok:
                        success_count += 1
                    time.sleep(0.3)
                except:
                    pass
        sender.reply(f"✅ 通知完成\n📢 已送达: {success_count} 人")
    except Exception as e:
        sender.reply(f"❌ 通知异常: {e}")

def show_tutorial():
    panel_name = '青龙' if config.get('panel_type') == 'qinglong' else '呆呆'
    sender.reply(f"""
=====和合插件教程=====
当前模式: 🌐 提交至{panel_name}面板

1️⃣ {config['randomsigncommand']}
   输入：手机号#密码#Q值
   自动RSA加密登录并同步系统

2️⃣ {config['randomquerycommand']}
   查询积分与余额(支持单选/多选/区间)

3️⃣ {config['randommanagecommand']}
   续费授权、删除账号、批量管理

4️⃣ 和合授权
   管理员总管理：授权、总览、CK预览、反查、同步、清理。

⚠️ 变量名: {config['dd_hhtt_osname']}
==================""")

# ===================== 主入口 =====================
try:
    command_text = str(usermessage or '')
    if re.search(r'(通知|广播)', command_text):
        notify_authorized_users()
    elif '登录' in command_text or '登陆' in command_text:
        bindaccount()
    elif '管理' in command_text:
        xy_manage()
    elif '查询' in command_text:
        cxs()
    elif command_text in ['和合清理', '清理和合']:
        report_data = clean_expired_accounts(force_report=True)
        send_daily_admin_report(report_data, force_send=True, notify_status=True)
    elif command_text == '和合授权':
        admin_auth_options()
    elif command_text == '和合教程':
        show_tutorial()
    elif command_text.startswith('和合通知') or command_text.startswith('和合广播'):
        notify_authorized_users()
    elif is_cron_trigger():
        report_data = clean_expired_accounts()
        send_daily_admin_report(report_data)
except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")

