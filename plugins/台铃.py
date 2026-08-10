# [title:台铃]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: 1603960061]
# [rule: ^台铃(登录|登陆|查询|管理|授权|清理|教程|上传|上传青龙|上传呆呆|运行|菜单)$]
# [cron: ]
# [priority: 99]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://example.com/icon.png]
# [version: 1.2.1]
# [public: true]
# [price: 6.66]
# [admin: false]
# [param: {"required":false,"key":"G_TLG.price","bool":false,"placeholder":"0.88","value":"0.88","name":"月费价格","desc":"每个账号每月的授权价格"}]
# [param: {"required":false,"key":"G_TLG.points_per_month","bool":false,"placeholder":"100","value":"100","name":"积分/月","desc":"每个账号每月所需积分数量"}]
# [param: {"required":false,"key":"G_TLG.use_daidai","bool":true,"name":"使用呆呆面板","desc":"勾选=上传呆呆面板，不勾选=上传青龙面板(默认)"}]
# [param: {"required":false,"key":"G_TLG.ql_config","bool":false,"placeholder":"http://ip:5700丨client_id丨client_secret","name":"青龙面板配置","desc":"青龙面板配置，格式：地址丨ID丨密钥"}]
# [param: {"required":false,"key":"G_TLG.ql_envname","bool":false,"placeholder":"G_TLG_TOKEN","value":"G_TLG_TOKEN","name":"环境变量名","desc":"推送到青龙的环境变量名称"}]
# [param: {"required":false,"key":"G_TLG.daidai_config","bool":false,"placeholder":"格式:http://呆呆地址丨app_key丨app_secret","name":"呆呆面板配置","desc":"呆呆面板配置信息，用丨分隔"}]
# [param: {"required":false,"key":"G_TLG.daidai_group","bool":false,"placeholder":"台铃","name":"呆呆分组","desc":"呆呆面板环境变量分组名称"}]
# [param: {"required":false,"key":"dd_sign_config.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款码(全局)","desc":"微信赞赏码/收款码链接"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_switch","bool":true,"name":"码支付开关(全局)","desc":"勾选启用码支付功能"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_gateway","bool":false,"placeholder":"https://pay.example.com","name":"码支付网关(全局)","desc":"支付网关地址"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_pid","bool":false,"placeholder":"10006","name":"商户ID(全局)","desc":"支付平台的商户ID"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_key","bool":false,"placeholder":"your_key","name":"商户密钥(全局)","desc":"支付平台的商户密钥"}]
# [param: {"required":false,"key":"dd_sign_config.pay_types","bool":false,"placeholder":"alipay,wxpay","name":"支付方式(全局)","desc":"支付方式，多个用英文逗号隔开"}]
# [description: vx小程序【台铃】签到插件<br>适配：青龙/呆呆面板、支持 authorization 绑定、签到与每日任务、自助支付授权与统一运行<br><br>指令：<br>台铃登录：绑定或更新 authorization（支持多号换行，格式：备注#authorization 或 备注#authorization#client_id）<br>台铃查询：查询签到状态与任务进度<br>台铃管理：账号授权(支付)、上传、删除与批量操作<br>台铃教程：查看 authorization 提交说明<br>台铃授权：管理员批量授权<br>台铃上传：手动选择目标批量上传已授权账号<br>台铃上传青龙：强制上传到青龙<br>台铃上传呆呆：强制上传到呆呆面板<br>台铃清理：清理失效或过期账号<br>更新：1.1.0 新增支付授权与统一返回模板<br>脚本地址QQ群:280458673]

import json
import time
import re
import uuid
import random
import string
import hashlib
import base64
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

import requests
import urllib3

try:
    from autman_huawei import QingLongClient, DadaiPanelClient, MaPayClient, generate_qrcode_url, get_pay_config
except ImportError:
    QingLongClient = None
    DadaiPanelClient = None
    MaPayClient = None
    generate_qrcode_url = None
    get_pay_config = None

try:
    import middleware
except ImportError:
    from types import SimpleNamespace

    class _DummySender:
        def __init__(self, *_args, **_kwargs):
            pass

        def getUserID(self):
            return "debug-user"

        def getMessage(self):
            return ""

        def reply(self, msg):
            print(msg)

        def input(self, *_args, **_kwargs):
            return input().strip()

        def isAdmin(self):
            return True

        def replyImage(self, image):
            print(image)

        def waitPay(self, *_args, **_kwargs):
            return ""

        def listen(self, *_args, **_kwargs):
            return ""

        def setContinue(self):
            pass

    middleware = SimpleNamespace(
        getSenderID=lambda: "debug",
        Sender=_DummySender,
        bucketGet=lambda bucket, key: "",
        bucketSet=lambda bucket, key, value: None,
        push=lambda *args, **kwargs: None,
    )

warnings = __import__('warnings')
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

AES_Cipher = None
PKCS1_v1_5 = None
RSA = None
pad = None

try:
    from Crypto.Cipher import AES as AES_Cipher, PKCS1_v1_5
    from Crypto.PublicKey import RSA
    from Crypto.Util.Padding import pad
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

PROJECT_NAME = "台铃"
PROJECT_ALIAS = "tailg"
BUCKET_USER = "G_TLG_user"
BUCKET_TOKEN = "G_TLG_token"
BUCKET_AUTH = "G_TLG_auth"
BUCKET_CONFIG = "G_TLG"
BUCKET_REMARK = "G_TLG_remark"
BUCKET_APP_USER = "G_TLG_app_user"

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

BASE_URL = "https://www.tailgdd.com/v1/api/shop/app/integral/sign"
TASK_URL = "https://www.tailgdd.com/v1/api/shop/app/integral/user"
SOCIAL_URL = "https://www.tailgdd.com/v8/social/app"
AUTH_URL = "https://www.tailgdd.com/v8/auth/login"
RSA_PUB_KEY_B64 = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+8L8XYhymaIuORzzlT+/mn76PuK1ixqkaOsCuw1zj6V/gOXD2i8NNOh4RrllCuNe6PSGttlmIKRlGS48pk1YctNzxDOdm17pngBWTx78p21ZR6q9AGiga/gYpcKLE5Eni7F/MBp4fqJUUbrAnyFgbYP2pTWm2lAeBxWmXRWyEvwIDAQAB"
DEFAULT_CLIENT_ID = "63baf6871f7aee49dbe800e7672b2bec"
TENANT_ID = "000000"

TASK_MAP = {
    "like_comment_trend": "每日点赞",
    "trend_share": "每日分享",
    "social_view": "社区浏览",
    "product_view": "商品浏览",
    "product_add_cart": "商品加购",
}


def bucket_get(bucket: str, key: str, default: str = "") -> str:
    value = middleware.bucketGet(bucket=bucket, key=key)
    return default if value is None else value


def bucket_set(bucket: str, key: str, value: str):
    middleware.bucketSet(bucket, key, value)


def get_user_accounts(user_id: str = None) -> list:
    if not user_id:
        user_id = userid
    data = bucket_get(BUCKET_USER, user_id)
    return [p.strip() for p in data.split(',') if p.strip()]


def save_user_accounts(accounts: list, user_id: str = None):
    if not user_id:
        user_id = userid
    bucket_set(BUCKET_USER, user_id, ','.join(accounts))


def get_token_data(account_id: str) -> dict:
    data = bucket_get(BUCKET_TOKEN, account_id)
    if not data:
        return {}
    parts = data.split('#')
    part_count = len(parts)
    if part_count >= 2:
        last_part = parts[part_count - 1]
        return {
            'authorization': '#'.join(parts[:part_count - 1]),
            'client_id': last_part,
            'has_client_id': True,
        }
    return {
        'authorization': data,
        'client_id': DEFAULT_CLIENT_ID,
        'has_client_id': False,
    }


def save_token_data(account_id: str, authorization: str, client_id: str = ""):
    value = f"{authorization}#{client_id}" if client_id else authorization
    bucket_set(BUCKET_TOKEN, account_id, value)


def get_auth_expire(account_id: str) -> str:
    return bucket_get(BUCKET_AUTH, account_id)


def save_auth_expire(account_id: str, expire_date: str):
    bucket_set(BUCKET_AUTH, account_id, expire_date)


def is_authorized(account_id: str) -> bool:
    expire = get_auth_expire(account_id)
    if not expire:
        return False
    try:
        return datetime.strptime(expire, '%Y-%m-%d').date() >= datetime.now().date()
    except:
        return False


def get_remark(account_id: str) -> str:
    return bucket_get(BUCKET_REMARK, account_id)


def save_remark(account_id: str, remark: str):
    bucket_set(BUCKET_REMARK, account_id, remark)


def get_bind_time(account_id: str) -> str:
    return bucket_get(BUCKET_AUTH, f"{account_id}_bind_time")


def save_bind_time(account_id: str, t: str = None):
    t = t or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    bucket_set(BUCKET_AUTH, f"{account_id}_bind_time", t)


def get_app_user_id(account_id: str) -> str:
    return bucket_get(BUCKET_APP_USER, account_id)


def save_app_user_id(account_id: str, app_user_id: str):
    bucket_set(BUCKET_APP_USER, account_id, str(app_user_id or ""))


def remove_account_record(account_id: str, user_id: str = None):
    if not user_id:
        user_id = userid
    accounts = get_user_accounts(user_id)
    if account_id in accounts:
        accounts.remove(account_id)
        save_user_accounts(accounts, user_id)
    bucket_set(BUCKET_TOKEN, account_id, '')
    bucket_set(BUCKET_AUTH, account_id, '')
    bucket_set(BUCKET_AUTH, f"{account_id}_bind_time", '')
    bucket_set(BUCKET_REMARK, account_id, '')
    bucket_set(BUCKET_APP_USER, account_id, '')


def find_existing_account_for_login(accounts: List[str], app_user_id: str, remark: str, client_id: str) -> str:
    normalized_user_id = str(app_user_id or "").strip()
    if normalized_user_id:
        for account_id in accounts:
            if get_app_user_id(account_id) == normalized_user_id:
                return account_id

    normalized_remark = str(remark or "").strip()
    normalized_client_id = str(client_id or DEFAULT_CLIENT_ID).strip() or DEFAULT_CLIENT_ID
    candidates = []
    if normalized_remark:
        for account_id in accounts:
            if (get_remark(account_id) or "").strip() != normalized_remark:
                continue
            token_data = get_token_data(account_id)
            stored_client_id = str(token_data.get("client_id") or DEFAULT_CLIENT_ID).strip() or DEFAULT_CLIENT_ID
            if stored_client_id == normalized_client_id:
                candidates.append(account_id)
    if len(candidates) == 1:
        return candidates[0]
    return ""


def add_account(account_id: str, user_id: str = None):
    if not user_id:
        user_id = userid
    accounts = get_user_accounts(user_id)
    if account_id not in accounts:
        accounts.append(account_id)
        save_user_accounts(accounts, user_id)


def del_account(account_id: str, user_id: str = None, ql_config: str = '', ql_envname: str = ''):
    if not user_id:
        user_id = userid
    if ql_config and ql_envname:
        delete_from_qinglong(account_id, ql_config, ql_envname)
    remove_account_record(account_id, user_id)


def get_config() -> dict:
    use_daidai_raw = bucket_get(BUCKET_CONFIG, 'use_daidai')
    if isinstance(use_daidai_raw, bool):
        use_daidai = use_daidai_raw
    elif use_daidai_raw is None:
        use_daidai = False
    else:
        use_daidai = str(use_daidai_raw).lower() == 'true'

    pay_config = get_pay_config() if get_pay_config else {}
    pay_types = pay_config.get('pay_types') if isinstance(pay_config.get('pay_types'), dict) else {}
    if not pay_types:
        pay_types = parse_pay_types(bucket_get('dd_sign_config', 'pay_types') or bucket_get('dd_sign_config', 'ma_pay_type'))
    ma_pay_client = MaPayClient() if MaPayClient else None

    return {
        'admin_users': bucket_get(BUCKET_CONFIG, 'admin_users') or '',
        'submission_limit': int(bucket_get(BUCKET_CONFIG, 'submission_limit') or '20'),
        'default_client_id': bucket_get(BUCKET_CONFIG, 'default_client_id') or DEFAULT_CLIENT_ID,
        'price': safe_decimal(bucket_get(BUCKET_CONFIG, 'price'), '0'),
        'points_per_month': safe_decimal(bucket_get(BUCKET_CONFIG, 'points_per_month'), '0'),
        'run_interval_seconds': int(bucket_get(BUCKET_CONFIG, 'run_interval_seconds') or '3'),
        'use_daidai': use_daidai,
        'ql_config': bucket_get(BUCKET_CONFIG, 'ql_config') or '',
        'ql_envname': bucket_get(BUCKET_CONFIG, 'ql_envname') or 'G_TLG_TOKEN',
        'daidai_config': bucket_get(BUCKET_CONFIG, 'daidai_config') or '',
        'daidai_group': bucket_get(BUCKET_CONFIG, 'daidai_group') or PROJECT_NAME,
        'zsm': pay_config.get('zsm') or bucket_get('G_SKM', 'zsm') or bucket_get('dd_sign_config', 'zsm') or '',
        'ma_pay_switch': bool(pay_config.get('ma_pay_switch', False)),
        'pay_types': pay_types,
        'ma_pay_gateway': getattr(ma_pay_client, 'gateway', '') if ma_pay_client else '',
        'ma_pay_pid': getattr(ma_pay_client, 'pid', '') if ma_pay_client else '',
        'ma_pay_key': getattr(ma_pay_client, 'key', '') if ma_pay_client else '',
        'ma_pay_notify_url': getattr(ma_pay_client, 'notify_url', '') if ma_pay_client else '',
        'ma_pay_return_url': getattr(ma_pay_client, 'return_url', '') if ma_pay_client else '',
    }


def is_admin() -> bool:
    try:
        if sender.isAdmin():
            return True
    except:
        pass
    config = get_config()
    admin_list = [x.strip() for x in str(config.get('admin_users', '')).split(',') if x.strip()]
    return userid in admin_list


def get_all_users() -> list:
    try:
        return middleware.bucketAllKeys(bucket=BUCKET_USER) or []
    except:
        return []


def get_owner_of_account(account_id: str) -> str:
    for uid in get_all_users():
        if account_id in get_user_accounts(uid):
            return uid
    return ''


def safe_decimal(value: Any, default: str = '0') -> Decimal:
    try:
        return Decimal(str(value or default))
    except Exception:
        return Decimal(default)


def parse_pay_types(raw: str) -> Dict[str, str]:
    labels = {
        'alipay': '支付宝',
        'wxpay': '微信支付',
        'qqpay': 'QQ钱包',
    }
    result: Dict[str, str] = {}
    for item in str(raw or '').split(','):
        key = item.strip().lower()
        if key:
            result[key] = labels.get(key, key)
    return result


def is_client_id_candidate(text: str) -> bool:
    value = str(text or '').strip()
    value_len = len(value)
    return 16 <= value_len <= 64 and value.isalnum()


def stable_hash(text: str) -> str:
    return hashlib.md5(str(text).encode("utf-8")).hexdigest()


def mask(text: str, left: int = 6, right: int = 6) -> str:
    text = str(text or "")
    if len(text) <= left + right:
        return "***"
    return text[:left] + "..." + text[-right:]


def mask_phone(phone: str) -> str:
    if not phone or len(phone) < 7:
        return phone or "***"
    return f"{phone[:3]}****{phone[-4:]}"


def now_str() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def format_money(value: Decimal) -> str:
    return f"{safe_decimal(value):.2f}"


def get_user_points(user_id: str = None) -> Decimal:
    return safe_decimal(bucket_get('dd_sign_points', user_id or userid), '0')


def set_user_points(points: Decimal, user_id: str = None):
    bucket_set('dd_sign_points', user_id or userid, str(safe_decimal(points)))


def get_auth_status_text(account_id: str) -> str:
    expire = get_auth_expire(account_id)
    if is_authorized(account_id):
        return f"已授权｜{expire}"
    if expire:
        return f"已过期｜{expire}"
    return "未授权"


def format_target_label(account_ids: List[str]) -> str:
    if not account_ids:
        return "未选择账号"
    remarks = [(get_remark(acc) or acc) for acc in account_ids]
    if len(remarks) == 1:
        return remarks[0]
    return f"{remarks[0]} 等{len(remarks)}个账号"


def build_query_result_message(account_id: str, msg_lines: List[str], index: int = 1, total: int = 1) -> str:
    remark = get_remark(account_id) or account_id
    lines = ["=====台铃查询====="]
    if total > 1:
        lines.append(f"📍 账号序号: {index}/{total}")
    lines.append(f"🏷 备注: {remark}")
    lines.extend(msg_lines)
    lines.append(f"🛡 {get_auth_status_text(account_id)}")
    lines.append("================")
    return "\n".join(lines)


def build_next_sign_reward_line(reward_items: List[dict]) -> Optional[str]:
    pending = []
    for item in reward_items or []:
        try:
            target_day = int(item.get("signDay", 0) or 0)
        except Exception:
            target_day = 0
        try:
            remain = int(item.get("remain", 0) or 0)
        except Exception:
            remain = 0
        if target_day > 0 and remain > 0:
            pending.append((remain, target_day))
    if pending:
        pending.sort(key=lambda x: (x[0], x[1]))
        remain, target_day = pending[0]
        return f"连签{target_day}天: 还差{remain}天"
    return None


def get_mapay_client(config: dict):
    if MaPayClient is None:
        return None
    client = MaPayClient(
        gateway=config.get('ma_pay_gateway') or None,
        pid=config.get('ma_pay_pid') or None,
        key=config.get('ma_pay_key') or None,
        notify_url=config.get('ma_pay_notify_url') or None,
        return_url=config.get('ma_pay_return_url') or None,
    )
    return client if client.is_configured() else None


def extract_payment_info(payment_result: Any) -> dict:
    info = {"money": None, "status": -1, "is_canceled": False}
    raw = str(payment_result or "")
    for pattern in ['status":2', 'status=2', '已取消', 'cancel']:
        if pattern.lower() in raw.lower():
            info["is_canceled"] = True
            info["status"] = 2
            break
    try:
        if isinstance(payment_result, dict):
            info["money"] = float(payment_result.get('Money', 0) or payment_result.get('money', 0))
            if not info["is_canceled"]:
                info["status"] = 1
        elif "收款金额￥" in raw:
            info["money"] = float(raw.split("收款金额￥", 1)[1].split("\n", 1)[0])
            info["status"] = 1
    except Exception:
        pass
    return info


def verify_payment(info: dict, expected: Decimal) -> str:
    if info["money"] is None:
        return "failed"
    if info["is_canceled"] or info["status"] == 2:
        return "canceled"
    if abs(Decimal(str(info["money"])) - safe_decimal(expected)) > Decimal("0.01"):
        return "insufficient"
    return "success"


def poll_ma_pay_status(config: dict, out_trade_no: str, max_tries: int = 150) -> tuple:
    client = get_mapay_client(config)
    if not client:
        return False, '码支付配置不完整', None
    for _ in range(max_tries):
        result = client.check_order(out_trade_no)
        if not result.get('error') and result.get('code') == 1 and result.get('status') == 1:
            return True, '支付成功', result
        if hasattr(sender, 'listen'):
            listen_result = sender.listen(2000)
            if listen_result and str(listen_result).strip().lower() == 'q':
                return False, '用户取消', None
        else:
            time.sleep(2)
    return False, '查询超时', None


def prompt_months() -> Optional[int]:
    sender.reply("请输入授权月数（正整数）：\n回复 q 退出")
    raw = sender.input(60000, 1, False)
    if not raw or raw.lower() == 'q':
        sender.reply("✅ 已取消")
        return None
    try:
        months = int(raw.strip())
        if months <= 0:
            raise ValueError()
        return months
    except Exception:
        sender.reply("❌ 无效月数")
        return None


def qrcode_payment_flow(target_label: str, months: int, total_price: Decimal, account_count: int, config: dict) -> bool:
    zsm = config.get('zsm', '')
    if not zsm:
        sender.reply("❌ 未配置全局收款码(dd_sign_config.zsm)")
        return False
    sender.reply(
        f"=====微信扫码支付=====\n"
        f"📱 {target_label}\n"
        f"🎯 授权时长: {months}个月\n"
        f"📦 账号数量: {account_count}\n"
        f"💰 金额: ¥{format_money(total_price)}\n"
        f"请使用微信扫码支付，输入q取消"
    )
    if hasattr(sender, 'replyImage'):
        sender.replyImage(zsm)
    else:
        sender.reply(f"[CQ:image,file={zsm}]")
    if not hasattr(sender, 'waitPay'):
        sender.reply("❌ 当前环境不支持 waitPay")
        return False
    result = sender.waitPay(timeout=600000, exitcode='q')
    if result == 'q':
        sender.reply("✅ 已取消")
        return False
    status = verify_payment(extract_payment_info(result), total_price)
    if status == 'success':
        sender.reply("✅ 支付成功")
        return True
    if status == 'canceled':
        sender.reply("✅ 已取消")
        return False
    if status == 'insufficient':
        sender.reply("❌ 金额不足")
        return False
    sender.reply("❌ 支付失败")
    return False


def mapay_payment_flow(target_label: str, months: int, total_price: Decimal, account_count: int, config: dict) -> bool:
    client = get_mapay_client(config)
    if not client:
        sender.reply("❌ 码支付配置不完整")
        return False
    pay_type_names = config.get('pay_types') or {'alipay': '支付宝', 'wxpay': '微信支付', 'qqpay': 'QQ钱包'}
    pay_types = list(pay_type_names.keys()) or ['alipay']
    if len(pay_types) == 1:
        selected_type = pay_types[0]
    else:
        options = "\n".join([f"[{i + 1}] {pay_type_names.get(t, t)}" for i, t in enumerate(pay_types)])
        sender.reply(
            f"=====码支付=====\n"
            f"📱 {target_label}\n"
            f"🎯 授权时长: {months}个月\n"
            f"📦 账号数量: {account_count}\n"
            f"💰 金额: ¥{format_money(total_price)}\n"
            f"------------------\n{options}\n选择支付方式(q退出)："
        )
        choice = sender.input(120000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply("✅ 已取消")
            return False
        try:
            idx = int(choice.strip()) - 1
            if idx < 0 or idx >= len(pay_types):
                raise ValueError()
            selected_type = pay_types[idx]
        except Exception:
            sender.reply("❌ 无效选择")
            return False
    out_trade_no = f"TLG{int(time.time())}{random.randint(1000, 9999)}"
    result = client.create_order(
        float(total_price),
        selected_type,
        out_trade_no,
        f"{PROJECT_NAME}-{target_label}-{months}月授权",
        param=str(userid),
    )
    if result.get('error'):
        sender.reply(f"❌ 创建订单失败: {result.get('error')}")
        return False
    pay_url = result.get('pay_url', '')
    if not pay_url:
        sender.reply("❌ 获取支付链接失败")
        return False
    qrcode_url = generate_qrcode_url(pay_url) if generate_qrcode_url else ''
    if qrcode_url:
        sender.reply(
            f"=====支付宝支付=====\n"
            f"📱 {target_label}\n"
            f"🎯 授权时长: {months}个月\n"
            f"📦 账号数量: {account_count}\n"
            f"💰 金额: ¥{format_money(total_price)}\n"
            f"请使用【{pay_type_names.get(selected_type, selected_type)}】扫码支付，输入q取消:\n"
            f"[CQ:image,file={qrcode_url}]"
        )
    else:
        sender.reply(
            f"=====支付宝支付=====\n"
            f"📱 {target_label}\n"
            f"🎯 授权时长: {months}个月\n"
            f"📦 账号数量: {account_count}\n"
            f"💰 金额: ¥{format_money(total_price)}\n"
            f"请使用【{pay_type_names.get(selected_type, selected_type)}】打开链接：\n{pay_url}"
        )
    is_paid, msg, _ = poll_ma_pay_status(config, out_trade_no)
    if is_paid:
        sender.reply("✅ 支付成功")
        return True
    sender.reply(f"❌ 支付未完成: {msg}")
    return False


def complete_authorization(account_id: str, months: int, config: dict) -> tuple:
    today = datetime.now().date()
    base_date = today
    expire_str = get_auth_expire(account_id)
    if expire_str:
        try:
            current_expire = datetime.strptime(expire_str, '%Y-%m-%d').date()
            if current_expire > today:
                base_date = current_expire
        except Exception:
            pass
    new_expire = (base_date + timedelta(days=30 * months)).strftime('%Y-%m-%d')
    save_auth_expire(account_id, new_expire)
    sync_ok = sync_to_panel_target(account_id, config)
    return True, sync_ok, new_expire


def apply_authorization(account_ids: List[str], months: int, config: dict) -> tuple:
    success_count = 0
    sync_count = 0
    latest_expire = ''
    for account_id in account_ids:
        success, sync_ok, expire = complete_authorization(account_id, months, config)
        if success:
            success_count += 1
            latest_expire = expire
        if sync_ok:
            sync_count += 1
    return success_count, sync_count, latest_expire


def batch_auth_pay(account_ids: List[str]) -> bool:
    if not account_ids:
        sender.reply("❌ 未选择账号")
        return False
    config = get_config()
    price = safe_decimal(config.get('price'), '0')
    points_per_month = safe_decimal(config.get('points_per_month'), '0')
    total_accounts = len(account_ids)
    target_label = format_target_label(account_ids)
    months = prompt_months()
    if not months:
        return False

    total_price = price * months * total_accounts
    total_points = points_per_month * months * total_accounts
    user_points = get_user_points()
    has_qrcode = bool(price > 0 and config.get('zsm'))
    has_mapay = bool(price > 0 and config.get('ma_pay_switch') and get_mapay_client(config))
    has_points = bool(points_per_month > 0)
    if not has_qrcode and not has_mapay and not has_points:
        sender.reply("❌ 未配置授权方式")
        return False

    options = []
    handlers = {}
    option_index = 1
    if has_qrcode:
        options.append(f"[{option_index}] 微信扫码 ¥{format_money(total_price)}")
        handlers[str(option_index)] = 'qrcode'
        option_index += 1
    if has_mapay:
        options.append(f"[{option_index}] 码支付 ¥{format_money(total_price)}")
        handlers[str(option_index)] = 'mapay'
        option_index += 1
    if has_points:
        options.append(f"[{option_index}] 积分 {total_points}")
        handlers[str(option_index)] = 'points'

    sender.reply(
        f"=====批量授权支付=====\n"
        f"📱 {target_label}\n"
        f"⏰ {months}月 × {total_accounts}账号\n"
        f"💰 ¥{format_money(total_price)} | {total_points}积分\n"
        f"当前积分: {user_points}\n"
        f"------------------\n"
        + "\n".join(options)
        + "\n回复选择，q取消"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return False
    action = handlers.get(choice.strip())
    if not action:
        sender.reply("❌ 无效选择")
        return False

    if action == 'qrcode':
        if not qrcode_payment_flow(target_label, months, total_price, total_accounts, config):
            return False
        pay_name = "微信扫码"
    elif action == 'mapay':
        if not mapay_payment_flow(target_label, months, total_price, total_accounts, config):
            return False
        pay_name = "码支付"
    else:
        if user_points < total_points:
            sender.reply(f"❌ 积分不足 {total_points}")
            return False
        sender.reply(f"确认扣除 {total_points} 积分？回复 Y 确认，q取消")
        confirm = sender.input(60000, 1, False)
        if not confirm or confirm.lower() == 'q':
            sender.reply("✅ 已取消")
            return False
        if confirm.strip().lower() != 'y':
            sender.reply("❌ 已取消")
            return False
        set_user_points(user_points - total_points)
        pay_name = "积分支付"

    success_count, sync_count, latest_expire = apply_authorization(account_ids, months, config)
    pn = get_panel_name(config)
    sync_msg = f"{sync_count}/{success_count}" if is_panel_configured(config) else "未配置"
    sender.reply(
        f"=====台铃授权完成=====\n"
        f"📦 账号数: {success_count}/{total_accounts}\n"
        f"💳 支付方式: {pay_name}\n"
        f"⏰ 时长: {months}个月\n"
        f"📅 到期: {latest_expire or '-'}\n"
        f"🔄 {pn}推送: {sync_msg}"
    )
    return True


def admin_batch_authorize(account_ids: List[str]) -> bool:
    if not account_ids:
        sender.reply("❌ 未选择账号")
        return False
    months = prompt_months()
    if not months:
        return False
    config = get_config()
    success_count, sync_count, latest_expire = apply_authorization(account_ids, months, config)
    pn = get_panel_name(config)
    sync_msg = f"{sync_count}/{success_count}" if is_panel_configured(config) else "未配置"
    sender.reply(
        f"=====台铃授权完成=====\n"
        f"📦 账号数: {success_count}/{len(account_ids)}\n"
        f"💳 支付方式: 管理员授权\n"
        f"⏰ 时长: {months}个月\n"
        f"📅 到期: {latest_expire or '-'}\n"
        f"🔄 {pn}推送: {sync_msg}"
    )
    return True


def get_random_ua() -> str:
    uas = [
        "Mozilla/5.0 (Linux; Android 16; 25102RKBEC Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/140.0.7339.207 Mobile Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1",
    ]
    return random.choice(uas)


def parse_selection(choice: str, max_index: int) -> Optional[list]:
    if not choice or not choice.strip():
        return None
    indices = set()
    try:
        for part in choice.strip().split(','):
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                s, e = map(lambda x: int(x.strip()), part.split('-'))
                if s < 1 or e < 1 or s > max_index or e > max_index or s > e:
                    return None
                indices.update(range(s - 1, e))
            else:
                n = int(part)
                if n < 1 or n > max_index:
                    return None
                indices.add(n - 1)
        return sorted(indices) if indices else None
    except:
        return None


def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": get_random_ua(),
        "Accept": "application/json, text/plain, */*",
        "content-type": "application/json;charset=UTF-8",
        "origin": "https://www.tailgdd.com",
        "referer": "https://www.tailgdd.com/travel/tailg-shop-h5/",
        "x-requested-with": "XMLHttpRequest",
    })
    return session


def get_dep_status() -> dict:
    raw = bucket_get(BUCKET_CONFIG, "crypto_dep_status", "") or ""
    try:
        data = json.loads(raw) if raw else {}
        return data if isinstance(data, dict) else {}
    except:
        return {}


def set_dep_status(success: bool, message: str = ""):
    bucket_set(BUCKET_CONFIG, "crypto_dep_status", json.dumps({
        "success": bool(success),
        "message": str(message or ""),
        "updated_at": now_str(),
    }, ensure_ascii=False))


def load_crypto_modules():
    global AES_Cipher, PKCS1_v1_5, RSA, pad, HAS_CRYPTO
    try:
        from Crypto.Cipher import AES as _AES_Cipher, PKCS1_v1_5 as _PKCS1_v1_5
        from Crypto.PublicKey import RSA as _RSA
        from Crypto.Util.Padding import pad as _pad
        AES_Cipher = _AES_Cipher
        PKCS1_v1_5 = _PKCS1_v1_5
        RSA = _RSA
        pad = _pad
        HAS_CRYPTO = True
        return True, "ok"
    except ImportError:
        HAS_CRYPTO = False
        return False, "import error"


def ensure_crypto_ready(notify: bool = False):
    ok, msg = load_crypto_modules()
    if ok:
        status = get_dep_status()
        if not status.get("success"):
            set_dep_status(True, "依赖已就绪")
        return True, "ok"

    if notify:
        sender.reply("检测到缺少依赖 `pycryptodome`，正在自动安装，首次使用仅执行一次...")

    try:
        proc = subprocess.run([sys.executable, "-m", "pip", "install", "pycryptodome"],
                              capture_output=True, text=True, timeout=180)
    except Exception as exc:
        set_dep_status(False, f"安装异常: {exc}")
        return False, f"安装异常: {exc}"

    ok, import_msg = load_crypto_modules()
    if proc.returncode == 0 and ok:
        set_dep_status(True, "pycryptodome 安装成功")
        if notify:
            sender.reply("依赖安装成功，后续将自动跳过安装步骤。")
        return True, "pycryptodome 安装成功"

    error_msg = (proc.stderr or proc.stdout or import_msg or "未知错误").strip()
    set_dep_status(False, error_msg[:500])
    return False, f"依赖安装失败: {error_msg[:200]}"


def get_bearer_token(session, smart_token: str, client_id: str):
    ok, dep_msg = ensure_crypto_ready(notify=True)
    if not ok:
        return None, dep_msg

    aes_key = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    aes_key_b64 = base64.b64encode(aes_key.encode()).decode()
    rsa_key = RSA.import_key(base64.b64decode(RSA_PUB_KEY_B64))
    cipher_rsa = PKCS1_v1_5.new(rsa_key)
    encrypted_key = cipher_rsa.encrypt(aes_key_b64.encode())
    encrypt_key_header = base64.b64encode(encrypted_key).decode()

    body_plain = json.dumps({
        "clientId": client_id,
        "grantType": "smartToken",
        "smartToken": smart_token,
        "tenantId": TENANT_ID,
    }, separators=(",", ":"))

    cipher_aes = AES_Cipher.new(aes_key.encode(), AES_Cipher.MODE_ECB)
    encrypted_body = base64.b64encode(cipher_aes.encrypt(pad(body_plain.encode(), AES_Cipher.block_size))).decode()

    session.headers["authorization"] = smart_token
    resp = session.post(AUTH_URL, data=encrypted_body, headers={
        "encrypt-key": encrypt_key_header,
        "content-type": "application/json; charset=utf-8",
    }).json()

    if resp.get("code") == 200:
        return f"Bearer {resp['data']['access_token']}", "ok"
    return None, resp.get("msg", "获取 Bearer Token 失败")


def verify_sign(session, auth: str, sign_date: str):
    session.headers["authorization"] = auth
    resp = session.post(f"{BASE_URL}/verifySign", json={"signDate": sign_date}).json()
    if resp.get("code") == 0:
        return True, resp.get("data", False), resp
    return False, None, resp


def save_sign(session, auth: str):
    session.headers["authorization"] = auth
    return session.post(f"{BASE_URL}/saveIntegralSignIn", json={}).json()


def get_sign_info(session, auth: str, sign_date: str, month_date: str):
    session.headers["authorization"] = auth
    return session.post(f"{BASE_URL}/getSign", json={"signDate": sign_date, "signMonthDate": month_date}).json()


def get_reward_info(session, auth: str, sign_date: str):
    session.headers["authorization"] = auth
    return session.post(f"{BASE_URL}/getProceedSignReward", json={"signDate": sign_date}).json()


def get_integral_user_summary(session, auth: str):
    session.headers["authorization"] = auth
    return session.post(f"{TASK_URL}/getIntegralUserSummary").json()


def list_tasks(session, auth: str):
    session.headers["authorization"] = auth
    resp = session.post(f"{TASK_URL}/listUserIntegralTask", json={"taskType": "1"}).json()
    if resp.get("code") == 0:
        return resp.get("data", []), resp
    return [], resp


def get_trends_list(session, auth: str, client_id: str):
    session.headers.update({"authorization": auth, "clientid": client_id, "client-origin": "h5"})
    resp = session.get(f"{SOCIAL_URL}/trends/recommend/list?pageNum=1&pageSize=10").json()
    if resp.get("code") == 200:
        return [item["id"] for item in resp.get("rows", []) if item.get("id")]
    return []


def get_product_list(session, auth: str):
    session.headers["authorization"] = auth
    resp = session.post("https://www.tailgdd.com/v1/api/shop/app/product/app/category/listProduct",
                        json={"productCategoryId": 1, "limit": 6}).json()
    if resp.get("code") == 0:
        products = []
        for cat in resp.get("data", []):
            for product in cat.get("products", []):
                products.append(product["id"])
        return products
    return []


def get_product_detail(session, auth: str, product_id: str):
    session.headers["authorization"] = auth
    resp = session.post("https://www.tailgdd.com/v1/api/shop/app/product/detail",
                        json={"id": str(product_id)}).json()
    if resp.get("code") == 0:
        data = resp.get("data") or {}
        skus = data.get("productSkus") or []
        if skus:
            return {"productId": data["id"], "productSkuNum": skus[0]["number"]}
    return None


def do_like(session, auth: str, client_id: str, trends_id: str):
    session.headers.update({"authorization": auth, "clientid": client_id, "client-origin": "h5"})
    return session.get(f"{SOCIAL_URL}/trends/like?trendsId={trends_id}&isLike=1").json()


def do_share(session, auth: str, client_id: str, trends_id: str):
    session.headers.update({"authorization": auth, "clientid": client_id, "client-origin": "h5"})
    return session.get(f"{SOCIAL_URL}/trends/share?trendsId={trends_id}").json()


def do_social_view(session, auth: str, client_id: str):
    session.headers.update({"authorization": auth, "clientid": client_id, "client-origin": "h5"})
    return session.post(f"{SOCIAL_URL}/task/completeTask", json={"taskType": "social_view"}).json()


def do_product_view(session, auth: str, product_id: str):
    session.headers["authorization"] = auth
    return session.post(f"{TASK_URL}/completeDailyTask",
                        json={"taskType": 1, "eventCode": "product_view", "businessId": str(product_id)}).json()


def do_add_cart(session, auth: str, product_id: str, sku_num: str):
    session.headers["authorization"] = auth
    return session.post("https://www.tailgdd.com/v1/api/shop/app/cart/setCart",
                        json={"quantity": 1, "productId": product_id, "productSkuNum": sku_num}).json()


def draw_award(session, auth: str, event_code: str):
    session.headers["authorization"] = auth
    return session.post(f"{TASK_URL}/drawEventAward", json={"taskType": 1, "eventCode": event_code}).json()


def parse_auth_input(text: str, default_client_id: str) -> Optional[dict]:
    raw = str(text or "").strip()
    if not raw:
        return None
    if "#" not in raw:
        return None
    parts = [x.strip() for x in raw.split("#")]
    remark = parts[0] if parts else ""
    auth = ""
    client_id = ""
    part_count = len(parts)
    if part_count == 2:
        auth = parts[1]
    elif part_count >= 3:
        last_part = parts[part_count - 1]
        if is_client_id_candidate(last_part):
            client_id = last_part
            auth = "#".join(parts[1:part_count - 1]).strip()
        else:
            auth = "#".join(parts[1:part_count]).strip()
    else:
        auth = "#".join(parts[1:]).strip()
    if not remark or not auth:
        return None
    return {
        "remark": remark,
        "authorization": auth,
        "client_id": client_id or default_client_id,
        "raw_client_id": client_id,
    }


def make_account_id(auth: str, client_id: str) -> str:
    return "tg_" + stable_hash(f"{auth}_{client_id}")[:16]


def query_single_account(payload: dict) -> tuple:
    auth = payload["authorization"]
    session = get_session()
    now = datetime.now(timezone(timedelta(hours=8)))
    sign_date = now.strftime("%Y-%m-%d")
    month_date = now.strftime("%Y-%m-01")
    lines = []

    ok, signed, resp = verify_sign(session, auth, sign_date)
    if not ok:
        return False, [f"查询签到状态失败: {resp.get('msg', '')}"]

    summary_resp = get_integral_user_summary(session, auth)
    if summary_resp.get("code") == 0:
        summary_data = summary_resp.get("data") or {}
        payload["_integral_summary"] = summary_data
        available_points = summary_data.get("availableTotalIntegral")
        if available_points is not None:
            lines.append(f"总积分:{available_points}")
    else:
        payload["_integral_summary"] = {}
        lines.append("总积分: 获取失败")

    lines.append(f"今日签到: {'已签到' if signed else '未签到'}")

    sign_resp = get_sign_info(session, auth, sign_date, month_date)
    if sign_resp.get("code") == 0:
        data = sign_resp.get("data") or {}
        sign_day = data.get("signDay", 0)
        lines.append(f"累计签到: {sign_day}天")

    reward_resp = get_reward_info(session, auth, sign_date)
    if reward_resp.get("code") == 0:
        reward_line = build_next_sign_reward_line((reward_resp.get("data") or {}).get("result", []))
        if reward_line:
            lines.append(reward_line)

    return True, lines


def run_single_account(payload: dict) -> tuple:
    auth = payload["authorization"]
    client_id = payload.get("client_id") or get_config().get('default_client_id', DEFAULT_CLIENT_ID)
    session = get_session()
    now = datetime.now(timezone(timedelta(hours=8)))
    sign_date = now.strftime("%Y-%m-%d")
    month_date = now.strftime("%Y-%m-01")
    lines = []

    ok, signed, resp = verify_sign(session, auth, sign_date)
    if not ok:
        return False, [f"查询签到状态失败: {resp.get('msg', '')}"]

    if signed:
        lines.append(f"今日({sign_date})已签到")
    else:
        save_resp = save_sign(session, auth)
        if save_resp.get("code") == 0 and save_resp.get("success"):
            data = save_resp.get("data") or {}
            lines.append(f"签到成功: {data.get('award_num', 0)} {data.get('awardName', '')}")
        else:
            lines.append(f"签到失败: {save_resp.get('msg', '')}")

    sign_resp = get_sign_info(session, auth, sign_date, month_date)
    if sign_resp.get("code") == 0:
        data = sign_resp.get("data") or {}
        sign_day = data.get("signDay", 0)
        signed_count = sum(1 for item in (data.get("signList") or []) if item.get("isSign") == "1")
        lines.append(f"本周期已签: {signed_count}天")
        lines.append(f"累计签到: {sign_day}天")

    tasks, task_resp = list_tasks(session, auth)
    if not tasks:
        lines.append(f"获取任务列表失败: {task_resp.get('msg', '')}")
        return True, lines

    todo = {}
    for task in tasks:
        code = task.get("eventCode", "")
        if code not in TASK_MAP or not task.get("taskStatus"):
            continue
        max_num = task.get("maxTaskDrawNum", 0)
        done_num = task.get("completeTaskDrawNum", 0)
        remaining = max_num - done_num
        if remaining > 0:
            todo[code] = {"remaining": remaining, "name": TASK_MAP[code]}
        else:
            lines.append(f"{TASK_MAP[code]}: 已完成 {done_num}/{max_num}")

    if not todo:
        lines.append("所有每日任务已完成")
        return True, lines

    bearer_auth = None
    if any(code in todo for code in ("like_comment_trend", "trend_share", "social_view")):
        bearer_auth, bearer_msg = get_bearer_token(session, auth, client_id)
        if not bearer_auth:
            lines.append(f"社区任务跳过: {bearer_msg}")

    trends_ids = []
    product_ids = []
    if bearer_auth and ("like_comment_trend" in todo or "trend_share" in todo):
        trends_ids = get_trends_list(session, bearer_auth, client_id)
        if not trends_ids:
            lines.append("帖子列表获取失败，跳过点赞/分享")

    if "product_view" in todo or "product_add_cart" in todo:
        product_ids = get_product_list(session, auth)
        if not product_ids:
            lines.append("商品列表获取失败，跳过商品任务")

    if "like_comment_trend" in todo and trends_ids and bearer_auth:
        for index in range(todo["like_comment_trend"]["remaining"]):
            resp = do_like(session, bearer_auth, client_id, trends_ids[index % len(trends_ids)])
            lines.append(f"每日点赞 {index + 1}: {'成功' if resp.get('code') == 200 else '失败 ' + str(resp.get('msg', ''))}")
            time.sleep(random.uniform(1, 2))

    if "trend_share" in todo and trends_ids and bearer_auth:
        for index in range(todo["trend_share"]["remaining"]):
            trends_id = trends_ids[index % len(trends_ids)]
            resp = do_share(session, bearer_auth, client_id, trends_id)
            if resp.get("code") == 200:
                draw_award(session, auth, "trend_share")
            lines.append(f"每日分享 {index + 1}: {'成功' if resp.get('code') == 200 else '失败 ' + str(resp.get('msg', ''))}")
            time.sleep(random.uniform(1, 2))

    if "social_view" in todo and bearer_auth:
        for index in range(todo["social_view"]["remaining"]):
            resp = do_social_view(session, bearer_auth, client_id)
            lines.append(f"社区浏览 {index + 1}: {'成功' if resp.get('code') == 200 else '失败 ' + str(resp.get('msg', ''))}")
            time.sleep(random.uniform(1, 2))

    if "product_view" in todo and product_ids:
        shuffled = random.sample(product_ids, min(len(product_ids), todo["product_view"]["remaining"] + 3))
        for index in range(todo["product_view"]["remaining"]):
            pid = shuffled[index % len(shuffled)]
            resp = do_product_view(session, auth, pid)
            lines.append(f"商品浏览 {index + 1}: {'成功' if resp.get('code') == 0 else '失败 ' + str(resp.get('msg', ''))}")
            time.sleep(random.uniform(1, 2))

    if "product_add_cart" in todo and product_ids:
        pid = random.choice(product_ids)
        detail = get_product_detail(session, auth, pid)
        if detail:
            resp = do_add_cart(session, auth, detail["productId"], detail["productSkuNum"])
            lines.append(f"商品加购: {'成功' if resp.get('code') == 0 else '失败 ' + str(resp.get('msg', ''))}")
        else:
            lines.append("商品加购: 获取SKU失败")

    return True, lines


def get_ql_client(ql_config: str, ql_envname: str):
    if not ql_config or not ql_envname or QingLongClient is None:
        return None
    client = QingLongClient(ql_envname, ql_config)
    return client if client.is_configured() else None


def get_dd_client(daidai_config: str, daidai_group: str):
    if not daidai_config or DadaiPanelClient is None:
        return None
    client = DadaiPanelClient(
        'G_TLG_TOKEN',
        daidai_config,
        project_name=PROJECT_NAME,
        group_key='daidai_group',
    )
    return client if client.is_configured() else None


def sync_to_panel_target(account_id: str, config: dict, target: str = None):
    if target is None:
        target = "daidai" if config.get('use_daidai') else "qinglong"

    token_data = get_token_data(account_id)
    if not token_data:
        return False

    expire = get_auth_expire(account_id) or datetime.now().strftime('%Y-%m-%d')
    remark = (get_remark(account_id) or account_id).replace("#", "-").strip() or account_id

    if target == "daidai":
        client = get_dd_client(config.get('daidai_config', ''), config.get('daidai_group', ''))
        if not client:
            return False
        env_value = f"{remark}#{token_data['authorization']}"
        if token_data.get('has_client_id') and token_data.get('client_id'):
            env_value = f"{env_value}#{token_data['client_id']}"
        return client.update_env(
            username=account_id,
            env_value=env_value,
            remark=f"{PROJECT_NAME}:{remark}|账号:{account_id}|到期:{expire}",
        )
    else:
        client = get_ql_client(config.get('ql_config', ''), config.get('ql_envname', 'G_TLG_TOKEN'))
        if not client:
            return False
        env_value = f"{remark}#{token_data['authorization']}"
        if token_data.get('has_client_id') and token_data.get('client_id'):
            env_value = f"{env_value}#{token_data['client_id']}"
        return client.update_env(
            username=account_id,
            env_value=env_value,
            remark=f"{PROJECT_NAME}:{remark}|账号:{account_id}|到期:{expire}",
        )


def delete_from_panel_target(account_id: str, config: dict, target: str = None) -> bool:
    if target is None:
        target = "daidai" if config.get('use_daidai') else "qinglong"
    if target == "daidai":
        return delete_from_daidai(account_id, config.get('daidai_config', ''))
    return delete_from_qinglong(account_id, config.get('ql_config', ''), config.get('ql_envname', 'G_TLG_TOKEN'))


def delete_from_qinglong(account_id: str, ql_config: str, ql_envname: str) -> bool:
    client = get_ql_client(ql_config, ql_envname)
    if not client:
        return False
    return client.delete_env(account_id)


def delete_from_daidai(account_id: str, daidai_config: str) -> bool:
    client = get_dd_client(daidai_config, '')
    if not client:
        return False
    return client.delete_env(account_id)


def get_panel_name(config: dict) -> str:
    return "呆呆" if config.get('use_daidai') else "青龙"


def is_panel_configured(config: dict) -> bool:
    if config.get('use_daidai'):
        return bool(config.get('daidai_config'))
    return bool(config.get('ql_config'))


def show_tutorial():
    sender.reply(
        f"=====台铃教程=====\n"
        f"1. 打开台铃APP或小程序，进入签到/积分页面\n"
        f"2. 抓包找到请求头里的 authorization\n"
        f"3. 给机器人发送：台铃登录\n"
        f"4. 按提示提交 备注#authorization 或 备注#authorization#client_id 即可\n"
        f"5. 登录后可在台铃管理中自助支付授权\n"
        f"\n"
        f"提交格式：\n"
        f"备注#authorization\n"
        f"备注#authorization#client_id\n"
        f"\n"
        f"可用命令：\n"
        f"台铃登录 - 绑定或更新 authorization\n"
        f"台铃查询 - 查询签到状态与任务进度\n"
        f"台铃管理 - 支付授权 / 上传 / 删除 / 批量操作\n"
        f"台铃授权 - 管理员批量授权入口\n"
        f"台铃上传 - 手动选择上传目标\n"
        f"台铃上传青龙 - 直接上传到青龙面板\n"
        f"台铃上传呆呆 - 直接上传到呆呆面板\n"
        f"台铃清理 - 清理过期或无效账号\n"
        f"台铃教程 - 查看本帮助"
    )


def show_login():
    sender.reply(
        f"=====台铃登录=====\n"
        f"请输入：备注#authorization 或 备注#authorization#client_id\n"
        f"支持换行批量\n"
        f"回复 q 退出"
    )


def handle_login():
    show_login()
    raw = sender.input(120000, 1, False)
    if not raw or raw.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    config = get_config()
    success_count, fail_count = 0, 0
    inherited_auth_count = 0
    auto_sync_candidates = 0
    auto_sync_success = 0
    auto_sync_fail = 0
    fail_list = []
    lines = raw.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue
        payload = parse_auth_input(line, config.get('default_client_id', DEFAULT_CLIENT_ID))
        if not payload:
            fail_count += 1
            fail_list.append(f"{line[:20]}... 格式错误")
            continue

        ok, msg_lines = query_single_account(payload)
        if not ok:
            fail_count += 1
            fail_list.append(f"{mask(payload['authorization'])[:10]} 校验失败: {msg_lines[0]}")
            continue

        effective_client_id = payload.get("client_id") or config.get('default_client_id', DEFAULT_CLIENT_ID)
        summary_data = payload.get("_integral_summary") or {}
        app_user_id = str(summary_data.get("userId") or "").strip()
        current_accounts = get_user_accounts()
        matched_account_id = find_existing_account_for_login(
            current_accounts,
            app_user_id,
            payload.get("remark", ""),
            effective_client_id,
        )
        account_id = make_account_id(payload["authorization"], effective_client_id)
        old_remark = get_remark(account_id)
        matched_remark = get_remark(matched_account_id) if matched_account_id and matched_account_id != account_id else ""
        matched_expire = get_auth_expire(matched_account_id) if matched_account_id and matched_account_id != account_id else ""
        default_remark = f"账号{len(current_accounts) + 1}"
        remark = (payload.get("remark") or old_remark or matched_remark or default_remark).strip() or default_remark

        save_token_data(account_id, payload["authorization"], payload.get("raw_client_id", ""))
        save_remark(account_id, remark)
        save_bind_time(account_id)
        save_app_user_id(account_id, app_user_id)
        if matched_expire and matched_account_id != account_id:
            save_auth_expire(account_id, matched_expire)
            inherited_auth_count += 1
        if matched_account_id and matched_account_id != account_id:
            remove_account_record(matched_account_id)
        add_account(account_id)
        if is_authorized(account_id):
            auto_sync_candidates += 1
            if is_panel_configured(config):
                sync_ok = sync_to_panel_target(account_id, config)
                if sync_ok:
                    auto_sync_success += 1
                    if matched_account_id and matched_account_id != account_id:
                        delete_from_panel_target(matched_account_id, config)
                else:
                    auto_sync_fail += 1
        success_count += 1

    result_lines = [
        "=====台铃登录完成=====",
        f"📨 提交数量: {success_count + fail_count}",
        f"✅ 成功: {success_count}",
        f"❌ 失败: {fail_count}",
        f"📦 当前绑定: {len(get_user_accounts())}个",
        "🔎 接口校验: 已完成",
    ]
    if inherited_auth_count:
        result_lines.append(f"♻️ 继承授权: {inherited_auth_count}")
    if auto_sync_candidates:
        pn = get_panel_name(config)
        if is_panel_configured(config):
            result_lines.append(f"🔄 自动同步{pn}: {auto_sync_success}/{auto_sync_candidates}")
            if auto_sync_fail:
                result_lines.append(f"❌ 同步失败: {auto_sync_fail}")
        else:
            result_lines.append(f"🔄 自动同步{pn}: 面板未配置")
    result_lines.append("您可以发送「台铃管理」查看详情")
    if fail_list:
        result_lines.append("------------------")
        result_lines.extend([f"❌ {item}" for item in fail_list])
    sender.reply("\n".join(result_lines))


def handle_query():
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前未绑定账号")
        return

    total = len(accounts)
    authed = sum(1 for a in accounts if is_authorized(a))

    lines = [f"=====台铃查询====="]
    lines.append(f"📦 绑定账号: {total}个")

    for i, acc in enumerate(accounts, 1):
        remark = get_remark(acc) or acc
        expire = get_auth_expire(acc)
        auth_status = f"已授权｜{expire}" if is_authorized(acc) else ("已过期｜" + expire if expire else "未授权")
        lines.append(f"[{i}] {remark}")
        lines.append(f"     状态: {auth_status}")

    lines.append(f"[0] 查询所有账号")
    lines.append("支持格式：1 或 1,3 或 2-4")
    lines.append("回复序号选择（q退出）")

    sender.reply("\n".join(lines))

    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    if choice.strip() == '0':
        selected = accounts[:]
    else:
        indices = parse_selection(choice.strip(), len(accounts))
        if indices is None:
            sender.reply("❌ 选择格式错误")
            return
        selected = [accounts[i] for i in indices]

    for i, account_id in enumerate(selected, 1):
        token_data = get_token_data(account_id)
        if not token_data:
            sender.reply(f"=====台铃查询=====\n账号数据异常")
            continue

        ok, msg_lines = query_single_account(token_data)
        sender.reply(build_query_result_message(account_id, msg_lines, i, len(selected)))


def handle_manage():
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前未绑定账号")
        return

    total = len(accounts)
    authed = sum(1 for a in accounts if is_authorized(a))
    lines = [f"=====台铃管理====="]
    lines.append(f"✅ 已授权: {authed}个")
    lines.append(f"⏳ 未授权: {total - authed}个")
    lines.append("---------------------------")

    for i, acc in enumerate(accounts, 1):
        remark = get_remark(acc) or acc
        expire = get_auth_expire(acc)
        auth_status = f"已授权｜{expire}" if is_authorized(acc) else ("已过期｜" + expire if expire else "未授权")
        lines.append(f"[{i}] {remark}")
        lines.append(f"     状态: {auth_status}")

    lines.append(f"[0] 所有账号授权（支付）")
    lines.append(f"[9998] 删除所有账号（删除）")
    lines.append(f"[9999] 未授权账号（授权）")
    lines.append("支持格式：1 或 1,3 或 2-4")
    lines.append("回复序号选择（q退出）")

    sender.reply("\n".join(lines))

    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    if choice.strip() == '9998':
        handle_delete_all()
        return
    elif choice.strip() == '9999':
        unauth = [a for a in accounts if not is_authorized(a)]
        if not unauth:
            sender.reply("❌ 当前没有未授权账号")
            return
        handle_batch_auth(unauth)
        return
    elif choice.strip() == '0':
        handle_batch_auth(accounts)
        return

    indices = parse_selection(choice.strip(), len(accounts))
    if indices is None:
        sender.reply("❌ 选择格式错误")
        return

    selected = [accounts[i] for i in indices]
    if len(selected) == 1:
        handle_single_manage(selected[0])
    else:
        handle_batch_menu(selected)


def handle_single_manage(account_id: str):
    remark = get_remark(account_id) or account_id
    expire = get_auth_expire(account_id)
    auth_str = f"已授权｜{expire}" if is_authorized(account_id) else ("已过期｜" + expire if expire else "未授权")
    config = get_config()
    pn = get_panel_name(config)
    panel_ok = is_panel_configured(config)

    lines = [f"=====台铃账号操作====="]
    lines.append(f"📦 数量: 1")
    lines.append(f"[1] 查询账号")
    lines.append(f"[2] 授权账号（支付）")
    lines.append(f"[3] 删除账号")
    lines.append(f"[4] 上传{pn}")
    lines.append("回复序号选择，回复 q 返回")

    sender.reply("\n".join(lines))

    c = sender.input(60000, 1, False)
    if not c or c.lower() == 'q':
        return

    if c == '1':
        token_data = get_token_data(account_id)
        if token_data:
            ok, msg_lines = query_single_account(token_data)
            sender.reply(build_query_result_message(account_id, msg_lines))
    elif c == '2':
        handle_batch_auth([account_id])
    elif c == '3':
        handle_delete_one(account_id)
    elif c == '4':
        pn = get_panel_name(config)
        ok = sync_to_panel_target(account_id, config)
        if ok:
            sender.reply(f"✅ 上传{pn}成功")
        else:
            sender.reply(f"❌ 上传{pn}失败" if is_panel_configured(config) else f"❌ {pn}未配置")


def handle_batch_menu(selected: list):
    config = get_config()
    pn = get_panel_name(config)
    panel_ok = is_panel_configured(config)

    lines = [f"=====台铃批量操作====="]
    lines.append(f"📦 数量: {len(selected)}")
    lines.append(f"[1] 查询账号")
    lines.append(f"[2] 授权账号（支付）")
    lines.append(f"[3] 删除账号")
    lines.append(f"[4] 上传{pn}")
    lines.append("回复序号选择，回复 q 返回")

    sender.reply("\n".join(lines))

    c = sender.input(60000, 1, False)
    if not c or c.lower() == 'q':
        return

    if c == '1':
        for i, acc in enumerate(selected, 1):
            token_data = get_token_data(acc)
            if token_data:
                ok, msg_lines = query_single_account(token_data)
                sender.reply(build_query_result_message(acc, msg_lines, i, len(selected)))
    elif c == '2':
        handle_batch_auth(selected)
    elif c == '3':
        for acc in selected:
            handle_delete_one(acc)
    elif c == '4':
        pn = get_panel_name(config)
        success, fail = 0, 0
        for acc in selected:
            if sync_to_panel_target(acc, config):
                success += 1
            else:
                fail += 1
        sender.reply(
            f"=====台铃上传完成=====\n"
            f"🎯 上传目标: {pn}\n"
            f"✅ 成功: {success}\n"
            f"❌ 失败: {fail}"
        )


def handle_delete_one(account_id: str):
    config = get_config()
    remark = get_remark(account_id) or account_id
    sender.reply(f"确认删除 {remark}？输入 1 确认，其他取消")
    c = sender.input(60000, 1, False)
    if not c or c != '1':
        sender.reply("✅ 已取消")
        return
    del_account(account_id, ql_config=config.get('ql_config', ''), ql_envname=config.get('ql_envname', 'G_TLG_TOKEN'))
    sender.reply(f"✅ 删除成功")


def handle_delete_all():
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前没有账号")
        return
    sender.reply(f"确认删除全部 {len(accounts)} 个账号？输入 1 确认，其他取消")
    c = sender.input(60000, 1, False)
    if not c or c != '1':
        sender.reply("✅ 已取消")
        return
    config = get_config()
    for acc in accounts:
        del_account(acc, ql_config=config.get('ql_config', ''), ql_envname=config.get('ql_envname', 'G_TLG_TOKEN'))
    sender.reply(f"✅ 删除成功，共移除 {len(accounts)} 个账号")


def handle_batch_auth(selected: list):
    batch_auth_pay(selected)


def handle_run():
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前未绑定账号")
        return

    lines = [f"=====台铃运行====="]
    for i, acc in enumerate(accounts, 1):
        remark = get_remark(acc) or acc
        lines.append(f"[{i}] {remark}")

    lines.append(f"[0] 运行所有账号")
    lines.append("支持格式：1 或 1,3 或 2-4")
    lines.append("回复序号选择（q退出）")

    sender.reply("\n".join(lines))

    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    if choice.strip() == '0':
        selected = accounts[:]
    else:
        indices = parse_selection(choice.strip(), len(accounts))
        if indices is None:
            sender.reply("❌ 选择格式错误")
            return
        selected = [accounts[i] for i in indices]

    config = get_config()
    sender.reply(f"开始运行，共 {len(selected)} 个账号")

    for i, account_id in enumerate(selected, 1):
        token_data = get_token_data(account_id)
        if not token_data:
            sender.reply(f"=====台铃运行=====\n账号数据异常")
            continue

        ok, msg_lines = run_single_account(token_data)
        remark = get_remark(account_id) or account_id

        result = [f"=====台铃运行====="]
        result.append(f"📍 账号序号: {i}/{len(selected)}")
        result.append(f"🏷 备注: {remark}")
        result.append(f"📌 状态: {'完成' if ok else '失败'}")
        for line in msg_lines:
            result.append(f"{line}")
        sender.reply("\n".join(result))

        if i < len(selected):
            time.sleep(config.get('run_interval_seconds', 3))


def handle_upload():
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前没有账号")
        return

    config = get_config()
    pn = get_panel_name(config)
    panel_ok = is_panel_configured(config)

    lines = [f"=====台铃上传目标====="]
    lines.append(f"⚙️ 默认上传: {pn}")
    lines.append(f"🧪 环境变量: {config.get('ql_envname', 'G_TLG_TOKEN')}")
    lines.append(f"🔄 青龙配置: {'已配置' if config.get('ql_config') else '未配置'}")
    lines.append(f"🔄 呆呆配置: {'已配置' if config.get('daidai_config') else '未配置'}")
    lines.append(f"[1] 默认面板（{pn}）")
    lines.append(f"[2] 青龙面板")
    lines.append(f"[3] 呆呆面板")
    lines.append(f"[4] 青龙+呆呆（双传）")
    lines.append("回复数字选择，回复 q 取消")

    sender.reply("\n".join(lines))

    c = sender.input(60000, 1, False)
    if not c or c.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    targets = []
    if c == '1':
        targets = [pn]
    elif c == '2':
        targets = ["qinglong"]
    elif c == '3':
        targets = ["daidai"]
    elif c == '4':
        targets = ["qinglong", "daidai"]
    else:
        sender.reply("❌ 无效选择")
        return

    if c in ('2', '3', '4') and not panel_ok:
        sender.reply("❌ 目标面板未配置")
        return

    success, fail, skip = 0, 0, 0
    for acc in accounts:
        if not is_authorized(acc):
            skip += 1
            continue
        for target in targets:
            if sync_to_panel_target(acc, config, target):
                success += 1
            else:
                fail += 1

    msg = (
        f"=====台铃上传完成=====\n"
        f"🎯 上传目标: {', '.join(targets)}\n"
        f"✅ 成功: {success}\n"
        f"📦 已授权总数: {sum(1 for a in accounts if is_authorized(a))}"
    )
    if skip:
        msg += f"\n⏭ 未授权跳过: {skip}"
    sender.reply(msg)


def handle_upload_ql():
    if not is_admin():
        sender.reply("❌ 仅管理员可用")
        return
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前没有账号")
        return

    config = get_config()
    success, fail, skip = 0, 0, 0
    for acc in accounts:
        if not is_authorized(acc):
            skip += 1
            continue
        if sync_to_panel_target(acc, config, "qinglong"):
            success += 1
        else:
            fail += 1

    sender.reply(
        f"=====台铃上传完成=====\n"
        f"🎯 上传目标: 青龙面板\n"
        f"✅ 成功: {success}\n"
        f"📦 已授权总数: {sum(1 for a in accounts if is_authorized(a))}"
        + (f"\n⏭ 未授权跳过: {skip}" if skip else "")
    )


def handle_upload_dd():
    if not is_admin():
        sender.reply("❌ 仅管理员可用")
        return
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前没有账号")
        return

    config = get_config()
    success, fail, skip = 0, 0, 0
    for acc in accounts:
        if not is_authorized(acc):
            skip += 1
            continue
        if sync_to_panel_target(acc, config, "daidai"):
            success += 1
        else:
            fail += 1

    sender.reply(
        f"=====台铃上传完成=====\n"
        f"🎯 上传目标: 呆呆面板\n"
        f"✅ 成功: {success}\n"
        f"📦 已授权总数: {sum(1 for a in accounts if is_authorized(a))}"
        + (f"\n⏭ 未授权跳过: {skip}" if skip else "")
    )


def handle_authorize():
    if not is_admin():
        sender.reply("❌ 仅管理员可用")
        return
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 当前没有已绑定账号")
        return

    lines = [f"=====台铃授权====="]
    for i, acc in enumerate(accounts, 1):
        remark = get_remark(acc) or acc
        expire = get_auth_expire(acc)
        auth_status = f"已授权｜{expire}" if is_authorized(acc) else ("已过期｜" + expire if expire else "未授权")
        lines.append(f"[{i}] {remark}")
        lines.append(f"     状态: {auth_status}")

    lines.append(f"[0] 所有账号授权")
    lines.append(f"[9999] 未授权账号授权")
    lines.append("支持格式：1 或 1,3 或 2-4")
    lines.append("回复序号选择（q退出）")

    sender.reply("\n".join(lines))

    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    if choice.strip() == '0':
        admin_batch_authorize(accounts)
    elif choice.strip() == '9999':
        unauth = [a for a in accounts if not is_authorized(a)]
        if not unauth:
            sender.reply("❌ 当前没有未授权账号")
            return
        admin_batch_authorize(unauth)
    else:
        indices = parse_selection(choice.strip(), len(accounts))
        if indices is None:
            sender.reply("❌ 选择格式错误")
            return
        admin_batch_authorize([accounts[i] for i in indices])


def handle_cleanup():
    if not is_admin():
        sender.reply("❌ 仅管理员可用")
        return

    users = get_all_users()
    if not users:
        sender.reply("❌ 无用户数据")
        return

    sender.reply("🔍 正在检查所有用户账号状态...")
    config = get_config()
    current_date = datetime.now().date()
    total_accounts, expired_count, warning_count, notified_users = 0, 0, 0, 0

    for uid in users:
        user_accounts = get_user_accounts(uid)
        if not user_accounts:
            continue
        expired_list, warning_list = [], []

        for acc in user_accounts:
            total_accounts += 1
            expire_str = get_auth_expire(acc)
            if not expire_str:
                expired_list.append((acc, "未授权"))
                continue
            try:
                expire_date = datetime.strptime(expire_str, '%Y-%m-%d').date()
                days_left = (expire_date - current_date).days
                if days_left < 0:
                    expired_list.append((acc, f"已过期{abs(days_left)}天"))
                elif days_left <= 3:
                    warning_list.append((acc, f"剩余{days_left}天"))
            except:
                expired_list.append((acc, "授权异常"))

        for acc, reason in expired_list:
            del_account(acc, ql_config=config.get('ql_config', ''), ql_envname=config.get('ql_envname', 'G_TLG_TOKEN'))
            expired_count += 1

        if warning_list:
            warning_count += len(warning_list)
            msgs = [f"❌ {get_remark(p) or p} {r}，请续费" for p, r in warning_list]
            notify_msg = f"=====台铃账号提醒=====\n" + "\n".join(msgs)
            try:
                middleware.push('wx', '', uid, '台铃账号状态提醒', notify_msg)
                notified_users += 1
            except:
                pass
            try:
                middleware.push('qq', '', uid, '台铃账号状态提醒', notify_msg)
                notified_users += 1
            except:
                pass

    sender.reply(
        f"=====台铃清理完成=====\n"
        f"👤 影响用户: {len(users)}\n"
        f"⚠️ 临期提醒: {warning_count}\n"
        f"📤 已推送用户: {notified_users}\n"
        f"📱 移除绑定: {expired_count}\n"
        f"🗑 全局删除: {expired_count}"
    )


def handle_menu():
    accounts = get_user_accounts()
    dep_status = get_dep_status()
    dep_tip = "已安装" if dep_status.get("success") else "首次运行时自动安装"
    config = get_config()
    pn = get_panel_name(config)

    lines = [
        f"╔═══ 台铃菜单 ═══╗",
        f"│ 当前管理员：{'是' if is_admin() else '否'}",
        f"│ 依赖状态：{dep_tip}",
        f"│ 默认面板：{pn}",
        f"│ 绑定账号：{len(accounts)}个",
        f"├───────────────┤",
        f"│ 用户命令",
        f"│ 1. 台铃登录  → 绑定 authorization",
        f"│ 2. 台铃查询  → 查询签到与任务状态",
        f"│ 3. 台铃管理  → 支付授权/上传/删除/批量",
        f"│ 4. 台铃运行  → 执行签到与每日任务",
        f"│ 5. 台铃教程  → 查看使用教程",
        f"├───────────────┤",
        f"│ 管理员命令",
        f"│ 6. 台铃授权    → 批量授权账号",
        f"│ 7. 台铃上传    → 选择目标上传",
        f"│ 8. 台铃上传青龙 → 直接上传青龙",
        f"│ 9. 台铃上传呆呆 → 直接上传呆呆",
        f"│ 10. 台铃清理   → 清理过期账号",
        f"╚═══════════════╝",
    ]
    sender.reply("\n".join(lines))


def main():
    try:
        msg = sender.getMessage().strip()
    except:
        msg = ""

    if re.match(rf'^(台铃|{PROJECT_ALIAS})(登录|登陆)$', msg, re.I):
        handle_login()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})查询$', msg, re.I):
        handle_query()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})管理$', msg, re.I):
        handle_manage()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})授权$', msg, re.I):
        handle_authorize()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})上传$', msg, re.I):
        handle_upload()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})上传青龙$', msg, re.I):
        handle_upload_ql()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})上传呆呆$', msg, re.I):
        handle_upload_dd()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})清理$', msg, re.I):
        handle_cleanup()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})教程$', msg, re.I):
        show_tutorial()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})运行$', msg, re.I):
        handle_run()
    elif re.match(rf'^(台铃|{PROJECT_ALIAS})菜单$', msg, re.I):
        handle_menu()
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
