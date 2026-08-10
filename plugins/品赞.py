# [rule: ^(品赞|pz)(登录|登陆)$|^登(录|陆)(品赞|pz)$|^(品赞|pz)(查询|管理)$|^(查询|管理)(品赞|pz)$|^品赞清理$|^品赞授权$|^品赞教程$|^品赞任务运行$|^品赞加白$|^品赞删除$|^品赞自动加白$]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 0 8 * * 1]
# [public: true]
# [title: 品赞]
# [icon: https://img.cdn1.vip/i/69e0f096d26ae_1776349334.webp]
# [class: 工具类]
# [version: 1.4.1]
# [price: 8.88]
# [admin: false]
# [author: sky2022]
# [service: 2661320550]
# [description: 介绍：品赞代理自动签到插件<br>支持自动签到、用户ID查询、账号管理<br>登录格式：手机号#密码#备注<br>指令：品赞登录、品赞管理、品赞查询、品赞任务运行、品赞加白、品赞删除、品赞清理、品赞授权<br>每周一自动执行签到任务，无需手动操作<br><br>📝 更新日志<br>v1.4.1：修复品赞自动加白获取公网IP接口失效问题<br>v1.4：整体重构代码结构，提升可维护性；加白指令支持管理员自动获取IP；新增品赞自动加白指令]

# [param: {"required":true,"key":"dd_pz.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_pz.pzVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_pz.pzcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"dd_pz.superior_account","bool":false,"placeholder":"例:18888888888#qazwsx123","name":"上级账号","desc":"填写上级账号信息，格式：账号#密码，用于判断下级关系"}]
# [param: {"required":false,"key":"dd_pz.free_proxy","bool":true,"placeholder":"不填为关闭","name":"下级免费代挂","desc":"是否开启下级免费代挂功能"}]
# [param: {"required":false,"key":"dd_pz.use_ma_pay","bool":true,"placeholder":"false","name":"启用码支付","desc":"开启后默认使用码支付+积分支付，并隐藏微信支付"}]

import re
import middleware
import json
import base64
import random
import string
import requests
import urllib3
import time
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from Crypto.Cipher import AES
from binascii import hexlify

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_pz_user', key=userid)

# ==================== 配置读取 ====================

def getusercontent():
    pzVipmoney = float(middleware.bucketGet('dd_pz', 'pzVipmoney') or '1')
    pzcoin = int(middleware.bucketGet('dd_pz', 'pzcoin') or '0')
    superior_account = middleware.bucketGet('dd_pz', 'superior_account') or ''
    free_proxy = (middleware.bucketGet('dd_pz', 'free_proxy') or 'false').lower() == 'true'
    use_ma_pay = (middleware.bucketGet('dd_pz', 'use_ma_pay') or 'false').lower() == 'true'
    return pzVipmoney, pzcoin, superior_account, free_proxy, use_ma_pay

# ==================== 通用工具 ====================

def mask_phone(phone):
    return phone[:3] + "****" + phone[7:]

def parse_accounts(raw):
    """安全解析账号列表字符串"""
    if not raw:
        return []
    try:
        result = eval(raw)
        return list(result) if isinstance(result, (list, tuple, set)) else []
    except Exception:
        return []

def parse_token_info(token_info):
    """解析 token_info 字符串，返回 (phone, password, remark, token)"""
    if '|' in token_info:
        account_info, token = token_info.split('|', 1)
    else:
        account_info, token = token_info, None
    parts = account_info.split('#')
    if len(parts) != 3:
        return None, None, None, None
    return parts[0], parts[1], parts[2], token

def parse_batch_selection(input_str, max_count):
    """解析批量选择输入，支持逗号分隔和范围，返回 (valid_indices, invalid_indices)"""
    selected = []
    for part in input_str.split(','):
        part = part.strip()
        if '-' in part:
            a, b = part.split('-', 1)
            start, end = int(a.strip()), int(b.strip())
            if start <= end and start >= 1:
                selected.extend(range(start, end + 1))
        else:
            selected.append(int(part))
    selected = sorted(set(selected))
    valid = [i for i in selected if 1 <= i <= max_count]
    invalid = [i for i in selected if not (1 <= i <= max_count)]
    return valid, invalid

def ValueErrors(value, count):
    try:
        value = int(value)
        if value > count or value == 0:
            sender.reply(f"=====输入无效=====\n❌ 请输入 1-{count} 之间的数字\n==================")
            exit(0)
        return value
    except ValueError:
        sender.reply("=====输入无效=====\n❌ 请输入正确的数字\n==================")
        exit(0)

# ==================== 品赞 API ====================

PZ_BASE = "https://service.ipzan.com"
PZ_HEADERS_BASE = {
    'Content-Type': 'application/json',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Host': 'service.ipzan.com',
}

def _pz_ua():
    models = ['Xiaomi', 'Samsung Galaxy', 'Huawei', 'OPPO', 'Vivo']
    versions = ['10', '11', '12', '13']
    m, v = random.choice(models), random.choice(versions)
    build = f"Build/SP1A.{random.randint(210812,230812)}.{random.randint(1,999)}"
    return (f"Mozilla/5.0 (Linux; Android {v}; {m} {build}; wv) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Version/4.0 Chrome/{random.randint(100,120)}.0."
            f"{random.randint(1000,9999)}.{random.randint(100,999)} Mobile Safari/537.36 "
            f"MicroMessenger/8.0.41.2441(0x28002951)")

def _pz_encode(phone, password):
    encoded = base64.b64encode(f"{phone}QWERIPZAN1290QWER{password}".encode()).decode()
    rand = ''.join(random.choices(string.hexdigits, k=400))
    return (rand[:100] + encoded[:8] + rand[100:200] +
            encoded[8:20] + rand[200:300] + encoded[20:] + rand[300:400])

def pz_do_login(phone, password):
    """登录，返回 (success, message, token)"""
    try:
        headers = {**PZ_HEADERS_BASE, 'User-Agent': _pz_ua()}
        resp = requests.post(
            f"{PZ_BASE}/users-login",
            json={"account": _pz_encode(phone, password), "source": "ipzan-home-one"},
            headers=headers, timeout=30, verify=False
        )
        result = resp.json()
        if result.get('code') == 0:
            token = result.get('data', {}).get('token', '')
            return (True, "登录成功", token) if token else (False, "获取token失败", None)
        return False, result.get('message', '未知错误'), None
    except Exception as e:
        return False, f"登录异常: {str(e)}", None

def _pz_session(token):
    """构建带 token 的 session"""
    s = requests.Session()
    s.verify = False
    s.headers.update({**PZ_HEADERS_BASE, 'User-Agent': _pz_ua(), 'authorization': f'Bearer {token}'})
    return s

def _ensure_token(token_info):
    """确保 token 有效，过期则重新登录；返回 (phone, password, remark, token, new_token_info)"""
    phone, password, remark, token = parse_token_info(token_info)
    if not phone:
        return None, None, None, None, None
    if not token:
        ok, _, token = pz_do_login(phone, password)
        if not ok:
            return phone, password, remark, None, None
        new_info = f"{phone}#{password}#{remark}|{token}"
        middleware.bucketSet(bucket='dd_pz_token', key=phone, value=new_info)
        return phone, password, remark, token, new_info
    return phone, password, remark, token, token_info

def pz_checkin(token_info):
    """执行签到，返回 (success, message, new_token_info)"""
    phone, password, remark, token, token_info = _ensure_token(token_info)
    if not token:
        return False, "获取token失败", token_info
    s = _pz_session(token)
    try:
        r = s.get(f"{PZ_BASE}/home/userWallet-receive", timeout=30)
        result = r.json()
        if result.get('code') == 0:
            return True, "签到成功", token_info
        msg = result.get('message', '未知错误')
        if '登录已过期' in msg or '未登录' in msg:
            ok, _, new_token = pz_do_login(phone, password)
            if ok:
                new_info = f"{phone}#{password}#{remark}|{new_token}"
                middleware.bucketSet(bucket='dd_pz_token', key=phone, value=new_info)
                r2 = _pz_session(new_token).get(f"{PZ_BASE}/home/userWallet-receive", timeout=30)
                r2j = r2.json()
                if r2j.get('code') == 0:
                    return True, "签到成功(已自动重登)", new_info
                return False, r2j.get('message', '重登后签到失败'), new_info
            return False, f"重新登录失败: {new_token}", token_info
        return False, f"签到失败: {msg}", token_info
    except Exception as e:
        return False, f"签到异常: {str(e)}", token_info

def pz_query_info(token_info):
    """查询用户信息，返回 (success, message, user_id, popularize_id, balance)"""
    phone, password, remark, token, token_info = _ensure_token(token_info)
    if not token:
        return False, "获取token失败", None, None, None
    s = _pz_session(token)
    try:
        r = s.get(f"{PZ_BASE}/home/users-find", timeout=30)
        result = r.json()
        if result.get('code') != 0:
            return False, result.get('message', ''), None, None, None
        data = result.get('data', {})
        user_id = data.get('user_id', '')
        popularize_id = data.get('popularize_id', '')

        r2 = s.get(f"{PZ_BASE}/home/userWallet-find", timeout=30)
        r2j = r2.json()
        if r2j.get('code') != 0:
            return False, r2j.get('message', ''), None, None, None
        balance = r2j.get('data', {}).get('balance', 0)
        return True, "查询成功", user_id, popularize_id, balance
    except Exception as e:
        return False, f"查询异常: {str(e)}", None, None, None

def pz_query_subordinates(token_info):
    """查询下级列表，返回 (success, message, list)"""
    phone, password, remark, token, token_info = _ensure_token(token_info)
    if not token:
        return False, "获取token失败", None
    try:
        r = _pz_session(token).get(f"{PZ_BASE}/home/popularize-list", timeout=30)
        result = r.json()
        if result.get('code') != 0:
            return False, result.get('message', ''), None
        return True, "查询成功", result.get('data', [])
    except Exception as e:
        return False, f"查询异常: {str(e)}", None

def pz_get_superior_subordinates():
    """登录上级账号并获取其下级列表，返回 (success, message, list)"""
    cfg = middleware.bucketGet('dd_pz', 'superior_account') or ''
    if not cfg or '#' not in cfg:
        return False, "未配置上级账号", None
    sup_phone, sup_pass = cfg.split('#', 1)
    if not sup_phone or not sup_pass:
        return False, "上级账号配置不完整", None
    ok, msg, token = pz_do_login(sup_phone, sup_pass)
    if not ok:
        return False, f"上级登录失败: {msg}", None
    try:
        r = _pz_session(token).get(f"{PZ_BASE}/home/popularize-list", timeout=30)
        result = r.json()
        if result.get('code') != 0:
            return False, result.get('message', ''), None
        return True, "获取成功", result.get('data', [])
    except Exception as e:
        return False, f"获取异常: {str(e)}", None

def _is_subordinate(user_id):
    """判断 user_id 是否在上级下级列表中"""
    if not user_id:
        return False
    ok, _, subs = pz_get_superior_subordinates()
    if not ok or not subs:
        return False
    return any(s.get('invitees_id') == user_id for s in subs)

# ==================== 支付相关 ====================

def _get_ma_pay_config():
    if not use_ma_pay:
        return None
    cfg = {
        'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
        'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
        'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
        'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
        'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
        'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
        'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url'),
    }
    if cfg['switch'].lower() != 'true' or not all([cfg['gateway'], cfg['pid'], cfg['key']]):
        return None
    return cfg

def _parse_wechat_pay_result(pay_result):
    try:
        if isinstance(pay_result, dict):
            money = pay_result.get('Money') or pay_result.get('money')
            name = pay_result.get('FromName') or pay_result.get('fromName', '')
            return float(money), name
        if isinstance(pay_result, str):
            pay_json = json.loads(pay_result)
            money = pay_json.get('Money') or pay_json.get('money', 0)
            name = pay_json.get('FromName') or pay_json.get('fromName', '')
            return float(money), name
    except Exception:
        pass
    return None, None

def process_payment(months, account_count=1):
    """统一支付入口，返回 (success, pay_type)"""
    total_money = Decimal(str(pzVipmoney)) * Decimal(str(months)) * Decimal(str(account_count))
    total_coins = pzcoin * months * account_count
    user_points = int(middleware.bucketGet('dd_sign_points', str(userid)) or '0')

    ma_cfg = _get_ma_pay_config()
    zsm = middleware.bucketGet('dd_pz', 'zsm') or ''

    show_wechat = bool(zsm) and not use_ma_pay
    show_ma = use_ma_pay and bool(ma_cfg)
    show_coin = pzcoin > 0

    if float(total_money) == 0:
        return True, '免费授权'
    if not show_wechat and not show_ma and not show_coin:
        sender.reply("❌ 未配置可用收款方式,请联系管理员")
        return False, ''

    options, num = {}, 1
    menu = "=====选择支付方式====="
    if show_wechat:
        menu += f"\n{num}️⃣ 微信支付\n   💰 {total_money}元"
        options[str(num)] = 'wechat'; num += 1
    if show_ma:
        menu += f"\n{num}️⃣ 码支付\n   💰 {total_money}元"
        options[str(num)] = 'ma'; num += 1
    if show_coin:
        menu += f"\n{num}️⃣ 积分支付\n   🎯 {total_coins}积分 (当前:{user_points})"
        options[str(num)] = 'coin'
    menu += "\n------------------\n回复序号选择，回复q退出\n=================="
    sender.reply(menu)

    choice = sender.input(60000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消支付")
        return False, ''
    pay_type = options.get(str(choice))
    if not pay_type:
        sender.reply("❌ 输入无效")
        return False, ''

    if pay_type == 'coin':
        if user_points < total_coins:
            sender.reply(f"❌ 积分不足\n当前:{user_points}\n需要:{total_coins}")
            return False, ''
        sender.reply(f"=====积分支付确认=====\n💫 消耗:{total_coins}\n💰 剩余:{user_points - total_coins}\n------------------\n确认请回复 y\n==================")
        if (sender.input(60000, 1, False) or '').lower() != 'y':
            sender.reply("✅ 已取消支付")
            return False, ''
        middleware.bucketSet('dd_sign_points', str(userid), str(user_points - total_coins))
        return True, '积分支付'

    if pay_type == 'wechat':
        if sender.atWaitPay():
            sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
            return False, ''
        sender.reply(f"=====微信扫码支付====\n🎫 商品: 品赞授权\n💰 金额: {total_money}元\n------------------\n请使用微信扫码支付\n回复\"q\"取消支付\n==================")
        sender.replyImage(zsm)
        pay_result = sender.waitPay("q", 100 * 1000)
        if str(pay_result) == 'q':
            sender.reply('✅ 已取消支付')
            return False, ''
        money, from_name = _parse_wechat_pay_result(pay_result)
        if money is None:
            sender.reply('❌ 无法解析支付结果')
            return False, ''
        if float(money) < float(total_money):
            sender.reply(f"=====支付金额错误=====\n💰 应付:{total_money}元\n💳 实付:{money}元\n❗ 请联系管理员处理退款！\n==================")
            return False, ''
        return True, '微信支付'

    if pay_type == 'ma':
        out_trade_no = f"PZ{int(time.time())}{userid}"
        params = {k: v for k, v in {
            'pid': ma_cfg['pid'],
            'type': (ma_cfg.get('type') or 'alipay').split(',')[0],
            'out_trade_no': out_trade_no,
            'name': f"{senderID}-品赞授权-{total_money}",
            'money': str(total_money),
            'param': userid,
            'notify_url': ma_cfg.get('notify_url'),
            'return_url': ma_cfg.get('return_url'),
        }.items() if v}
        sorted_p = sorted(params.items())
        sign = hashlib.md5(("&".join(f"{k}={v}" for k, v in sorted_p) + ma_cfg['key']).encode()).hexdigest()
        params['sign'], params['sign_type'] = sign, 'MD5'
        gateway = ma_cfg['gateway'].rstrip('/')
        try:
            r = requests.post(gateway + '/mapi.php', data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10)
            result = r.json()
        except Exception as e:
            sender.reply(f"❌ 创建订单失败: {str(e)}")
            return False, ''
        if result.get('code') != 1:
            sender.reply(f"❌ 创建订单失败: {result.get('msg', '未知错误')}")
            return False, ''
        pay_url = result.get('payurl', '')
        if not pay_url:
            sender.reply("❌ 未获取到支付链接")
            return False, ''
        sender.reply(f"=====码支付=====\n🎫 品赞授权\n💰 {total_money}元\n⏰ 有效期:5分钟\n------------------\n{pay_url}\n💡 输入\"q\"可取消\n=================")
        check_url = gateway
        if '/xpay/epay/api.php' not in check_url:
            check_url = f"{check_url}/xpay/epay/api.php"
        for _ in range(60):
            inp = sender.listen(5000)
            if inp in ['q', 'Q']:
                sender.reply("✅ 已取消支付")
                return False, ''
            try:
                cr = requests.get(check_url, params={'act': 'order', 'pid': ma_cfg['pid'], 'key': ma_cfg['key'], 'out_trade_no': out_trade_no}, timeout=10)
                if cr.json().get('code') == 1 and cr.json().get('status') == 1:
                    return True, '码支付'
            except Exception:
                continue
        sender.reply("❌ 支付超时,请重新发起支付!")
        return False, ''

    return False, ''

# ==================== 授权写入 ====================

def _grant_auth(account, months):
    """写入授权到期时间，返回到期日期字符串"""
    expire = datetime.now() + timedelta(days=30 * months)
    expire_str = expire.strftime('%Y-%m-%d')
    middleware.bucketSet(bucket='dd_pz_auth', key=account, value=expire_str)
    return expire_str

def pz_auth_single(account, phone_masked, months):
    ok, pay_type = process_payment(months, 1)
    if not ok:
        return
    expire_str = _grant_auth(account, months)
    sender.reply(f"=====授权成功=====\n📱 账号: {phone_masked}\n⏰ 授权时长: {months}个月\n💳 支付方式: {pay_type}\n📅 到期时间: {expire_str}\n==================")

def pz_auth_batch(batch_accounts, months):
    ok, pay_type = process_payment(months, len(batch_accounts))
    if not ok:
        return
    success, fail = 0, 0
    expire_str = ''
    for item in batch_accounts:
        try:
            expire_str = _grant_auth(item['account'], months)
            success += 1
        except Exception:
            fail += 1
    sender.reply(f"=====批量授权完成=====\n✅ 成功: {success}个\n❌ 失败: {fail}个\n⏰ 授权时长: {months}个月\n💳 支付方式: {pay_type}\n📅 到期时间: {expire_str}\n==================")

# ==================== 账号管理逻辑 ====================

def _get_vip_status(account):
    accountVip = middleware.bucketGet(bucket='dd_pz_auth', key=account) or ''
    if not accountVip:
        return '⚠️ 未授权', accountVip
    if accountVip < today_time:
        return '❌ 已过期', accountVip
    return f'✅ {accountVip}', accountVip

def _build_display_accounts(accounts):
    display = []
    for acc in accounts:
        status, vip = _get_vip_status(acc)
        display.append({'account': acc, 'vip_status': status, 'vip_date': vip})
    display.sort(key=lambda x: x['vip_date'] if x['vip_date'] > today_time else '0000', reverse=True)
    return display

def _pick_accounts_for_whitelist(action_name):
    """通用：展示账号列表让用户选一个，返回 (phone, password, remark, token) 或 None"""
    accounts = parse_accounts(uservalue)
    display = []
    for acc in accounts:
        ti = middleware.bucketGet(bucket='dd_pz_token', key=acc)
        if not ti:
            continue
        phone, pwd, remark, token = parse_token_info(ti)
        if phone:
            display.append({'phone': phone, 'password': pwd, 'remark': remark, 'token': token, 'token_info': ti, 'acc': acc})

    if not display:
        sender.reply("❌ 未找到可用账号，请先登录绑定")
        return None

    msg = f"====={action_name}账号列表====="
    for i, item in enumerate(display, 1):
        msg += f"\n[{i}] 账号: {mask_phone(item['phone'])}  备注: {item['remark']}"
    msg += "\n------------------\n请输入序号选择账号，回复q退出\n=================="
    sender.reply(msg)

    inp = sender.input(120000, 1, False)
    if not inp or inp.lower() == 'q':
        sender.reply("✅ 已取消")
        return None
    try:
        idx = int(inp)
        if not (1 <= idx <= len(display)):
            sender.reply("❌ 序号无效")
            return None
    except Exception:
        sender.reply("❌ 请输入有效序号")
        return None
    return display[idx - 1]

# ==================== 功能模块 ====================

def pz_login():
    sender.reply("""=====品赞账号登录=====
请按以下格式输入账号信息:
手机号#密码#备注

🔰 支持批量登录，一行一个账号
示例:
13812345678#123456#账号1
13912345678#123456#账号2
------------------
回复"q"退出操作
==================""")
    raw = sender.input(120000, 1, False)
    if not raw:
        sender.reply("⏰ 操作超时,已退出"); exit(0)
    if raw.lower() == 'q':
        sender.reply("✅ 已取消登录"); exit(0)

    lines = [l.strip() for l in raw.strip().split('\n') if l.strip()]
    accounts = parse_accounts(uservalue)
    success_count, fail_count = 0, 0
    last_phone = None

    for line in lines:
        parts = line.split('#')
        if len(parts) != 3:
            fail_count += 1; continue
        phone, password, remark = parts
        if not re.match(r'^1[3-9]\d{9}$', phone):
            fail_count += 1; continue
        ok, _, token = pz_do_login(phone, password)
        if ok and token:
            ti = f"{line}|{token}"
            middleware.bucketSet(bucket='dd_pz_token', key=phone, value=ti)
            if phone not in accounts:
                accounts.append(phone)
            success_count += 1
            last_phone = phone
        else:
            fail_count += 1

    if accounts:
        middleware.bucketSet(bucket='dd_pz_user', key=userid, value=str(list(dict.fromkeys(accounts))))

    if len(lines) > 1:
        sender.reply(f"=====批量登录结果=====\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个\n==================")
        exit(0)

    if success_count == 1:
        vip_status, _ = _get_vip_status(last_phone)
        sender.reply(f"=====品赞账号绑定=====\n📱 绑定账号: {mask_phone(last_phone)}\n🔐 授权状态: {vip_status}\n==================")
    else:
        sender.reply("=====登录失败=====\n❌ 账号登录失败，请检查账号密码\n==================")

def pz_manage():
    accounts = parse_accounts(uservalue)
    if not accounts:
        sender.reply(f"=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 品赞登录 绑定\n=================="); return

    display = _build_display_accounts(accounts)
    page_size, current_page = 10, 1
    total_pages = max(1, (len(display) + page_size - 1) // page_size)

    while True:
        s_idx = (current_page - 1) * page_size
        e_idx = min(s_idx + page_size, len(display))
        page_items = display[s_idx:e_idx]

        msg = f"======我的品赞账号=====\n📄 第{current_page}/{total_pages}页\n[0] 批量授权模式"
        for i, item in enumerate(page_items, s_idx + 1):
            msg += f"\n------------------\n[{i}] 账号信息\n📱 账号: {mask_phone(item['account'])}\n🔐 授权: {item['vip_status']}"
        msg += "\n------------------"
        if total_pages > 1:
            msg += "\n[n] 下一页\n[p] 上一页"
        msg += "\n[q] 退出操作\n------------------\n请输入序号选择账号\n=================="
        sender.reply(msg)

        inp = sender.input(120000, 1, False)
        if inp is None or inp.lower() == 'timeout':
            sender.reply('⏰ 操作超时,已退出'); exit(0)
        if inp.lower() == 'q':
            sender.reply('✅ 已退出管理'); exit(0)
        if inp.lower() == 'n' and current_page < total_pages:
            current_page += 1; continue
        if inp.lower() == 'p' and current_page > 1:
            current_page -= 1; continue

        if inp == '0':
            sender.reply("=====批量授权模式=====\n请输入要授权的账号序号\n支持: 单个:1 多个:1,3,5 范围:1-5\n回复\"q\"退出\n==================")
            batch_inp = sender.input(120000, 1, False)
            if not batch_inp or batch_inp.lower() == 'q':
                continue
            try:
                valid, invalid = parse_batch_selection(batch_inp, len(display))
                if invalid:
                    sender.reply(f'❌ 以下序号无效已忽略: {",".join(map(str,invalid))}')
                if not valid:
                    sender.reply('❌ 未选择有效账号序号'); continue
            except ValueError as e:
                sender.reply(f'❌ {str(e)}'); continue

            sender.reply(f"=====设置授权时长=====\n请输入授权月数(如:1)\n回复\"q\"退出\n==================")
            mes_inp = sender.input(120000, 1, False)
            if not mes_inp or mes_inp.lower() == 'q':
                continue
            months = ValueErrors(mes_inp, 999)
            batch_accs = [{'account': display[i-1]['account'], 'phone': mask_phone(display[i-1]['account'])} for i in valid]
            pz_auth_batch(batch_accs, months)
            break

        try:
            me = int(inp)
            if not (1 <= me <= len(display)):
                sender.reply('❌ 序号无效'); continue
        except ValueError:
            sender.reply('❌ 请输入有效数字'); continue

        sel = display[me - 1]
        acc = sel['account']
        masked = mask_phone(acc)
        ti = middleware.bucketGet(bucket='dd_pz_token', key=acc) or ''
        sender.reply(f"=====账号详情=====\n📱 账号: {masked}\n🔐 授权: {sel['vip_status']}\n------------------\n[1] 授权账号\n[2] 删除账号\n[q] 返回上级\n------------------\n请选择操作\n==================")

        choice = sender.input(120000, 1, False)
        if not choice or choice.lower() == 'timeout':
            sender.reply('⏰ 操作超时,已退出'); exit(0)
        if choice.lower() == 'q':
            continue
        if choice == '1':
            sender.reply("=====设置授权时长=====\n请输入授权月数(如:1)\n回复\"q\"退出\n==================")
            mes_inp = sender.input(120000, 1, False)
            if not mes_inp or mes_inp.lower() == 'q':
                continue
            months = ValueErrors(mes_inp, 999)
            pz_auth_single(acc, masked, months)
            break
        elif choice == '2':
            sender.reply(f"=====确认删除=====\n📱 账号: {masked}\n⚠️ 删除后将无法恢复\n确认删除请回复: y\n==================")
            if (sender.input(120000, 1, False) or '').lower() == 'y':
                middleware.bucketDel(bucket='dd_pz_token', key=acc)
                middleware.bucketDel(bucket='dd_pz_auth', key=acc)
                accounts = [a for a in accounts if a != acc]
                middleware.bucketSet(bucket='dd_pz_user', key=userid, value=str(accounts))
                sender.reply(f"=====删除成功=====\n📱 账号: {masked}\n✅ 已从系统中删除\n==================")
                break
            else:
                sender.reply('✅ 已取消删除')
        else:
            sender.reply('❌ 无效的选择')

def pz_query():
    accounts = parse_accounts(uservalue)
    if not accounts:
        sender.reply(f"=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 品赞登录 绑定\n=================="); return

    msg = "=====品赞账号查询====="
    for i, acc in enumerate(accounts, 1):
        ti = middleware.bucketGet(bucket='dd_pz_token', key=acc) or ''
        vip_status, _ = _get_vip_status(acc)
        if not ti:
            msg += f"\n📱 账号{i}: {acc}\n🔐 状态: 未登录\n------------------"; continue
        phone, _, remark, _ = parse_token_info(ti)
        if not phone:
            msg += f"\n📱 账号{i}: {acc}\n🔐 状态: 数据异常\n------------------"; continue
        ok, _, user_id, popularize_id, balance = pz_query_info(ti)
        msg += f"\n📱 账号{i}: {mask_phone(phone)} ({remark})\n🔐 授权: {vip_status}"
        if ok:
            msg += f"\n🆔 用户ID: {user_id}\n🎫 邀请码ID: {popularize_id}\n💰 金币: {balance}"
        else:
            msg += f"\n⚠️ 信息查询失败"
        msg += "\n------------------"
    msg += "\n=================="
    sender.reply(msg)

def execute_tasks():
    """手动/定时任务执行（遍历当前用户账号）"""
    accounts = parse_accounts(uservalue)
    if not accounts:
        return "未绑定任何账号"

    results = []
    success_count, fail_count = 0, 0

    for acc in accounts:
        ti = middleware.bucketGet(bucket='dd_pz_token', key=acc)
        if not ti:
            results.append(f"账号 {acc}: 未找到登录信息")
            fail_count += 1; continue

        accountVip = middleware.bucketGet(bucket='dd_pz_auth', key=acc) or ''
        is_auth = bool(accountVip) and accountVip >= today_time

        # 判断是否为下级（免费执行）
        sub_flag = False
        if not is_auth:
            phone, _, _, _ = parse_token_info(ti)
            if phone:
                ok_q, _, uid, _, _ = pz_query_info(ti)
                if ok_q and uid:
                    sub_flag = _is_subordinate(uid)

        if not is_auth and not sub_flag:
            results.append(f"账号 {acc}: 未授权，跳过")
            fail_count += 1; continue

        ok, msg, _ = pz_checkin(ti)
        tag = " (下级免费)" if sub_flag else ""
        if ok:
            results.append(f"账号 {acc}: ✓ {msg}{tag}")
            success_count += 1
        else:
            results.append(f"账号 {acc}: ✗ {msg}{tag}")
            fail_count += 1
        time.sleep(1)

    result_msg = f"=====任务执行结果=====\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个\n------------------"
    for r in results:
        result_msg += f"\n{r}"
    result_msg += "\n=================="
    return result_msg

def clean_expired_accounts():
    users = middleware.bucketAllKeys(bucket='dd_pz_user')
    cleaned = 0
    for user in users:
        raw = middleware.bucketGet(bucket='dd_pz_user', key=user)
        if not raw:
            continue
        accs = parse_accounts(raw)
        valid = []
        for acc in accs:
            vip = middleware.bucketGet(bucket='dd_pz_auth', key=acc) or ''
            if vip and vip >= today_time:
                valid.append(acc)
            else:
                middleware.bucketDel(bucket='dd_pz_token', key=acc)
                middleware.bucketDel(bucket='dd_pz_auth', key=acc)
                cleaned += 1
        if valid:
            middleware.bucketSet(bucket='dd_pz_user', key=user, value=str(valid))
        else:
            middleware.bucketDel(bucket='dd_pz_user', key=user)
    sender.reply(f"=====清理完成=====\n🧹 已清理 {cleaned} 个过期账号\n==================")

def show_tutorial():
    sender.reply("""=====品赞代理教程=====
📖 使用说明:
1. 发送"品赞登录"绑定账号
2. 发送"品赞管理"授权账号
3. 发送"品赞查询"查询账号信息
4. 发送"品赞任务运行"执行签到任务
5. 发送"品赞加白"手动输入IP加白
6. 发送"品赞删除"删除白名单IP
7. 管理员发送"品赞清理"清理过期账号
8. 管理员发送"品赞授权"授权账号

🔰 账号格式: 手机号#密码#备注

⚠️ 注意事项:
• 每周一自动执行签到任务
• 下级账号可免费执行任务
• Token过期后自动重新登录
==================""")

# ==================== 管理员授权 ====================

def _get_all_accounts_by_user():
    users = middleware.bucketAllKeys(bucket='dd_pz_user')
    result = {}
    for user in users or []:
        raw = middleware.bucketGet(bucket='dd_pz_user', key=user)
        accs = parse_accounts(raw)
        acc_list = []
        for acc in accs:
            ti = middleware.bucketGet(bucket='dd_pz_token', key=acc)
            if not ti:
                continue
            phone, _, remark, _ = parse_token_info(ti)
            if not phone:
                continue
            vip = middleware.bucketGet(bucket='dd_pz_auth', key=acc) or ''
            auth_ok = vip >= today_time if vip else False
            acc_list.append({
                'account': acc, 'phone': phone, 'remark': remark,
                'auth_status': '✅' if auth_ok else '❌',
                'expire_info': f"到期:{vip}" if vip else "无",
            })
        if acc_list:
            result[user] = acc_list
    return result

def _input_months():
    sender.reply("请输入授权时长（月数）：\n------------------\n回复\"q\"退出操作\n==================")
    inp = sender.input(120000, 1, False)
    if not inp or inp.lower() == 'q':
        sender.reply("✅ 已取消授权"); return None
    try:
        m = int(inp)
        if m <= 0:
            sender.reply("❌ 请输入大于0的月数"); return None
        return m
    except ValueError:
        sender.reply("❌ 请输入有效数字"); return None

def _do_auth_items(items, months):
    success, fail, lines = 0, 0, []
    for item in items:
        try:
            expire_str = _grant_auth(item['account'], months)
            lines.append(f"✅ {mask_phone(item['phone'])}({item['remark']}) 授权至 {expire_str}")
            success += 1
        except Exception as e:
            lines.append(f"❌ {mask_phone(item['phone'])} 授权失败: {str(e)}")
            fail += 1
    msg = f"=====授权结果=====\n✅ 成功: {success}  ❌ 失败: {fail}\n⏰ 授权时长: {months}个月\n------------------"
    for l in lines:
        msg += f"\n{l}"
    msg += "\n=================="
    sender.reply(msg)

def pz_admin_auth():
    if not hasattr(sender, 'isAdmin') or not sender.isAdmin():
        sender.reply("❌ 仅管理员可用该指令"); return

    user_accounts = _get_all_accounts_by_user()
    if not user_accounts:
        sender.reply("❌ 当前没有任何用户绑定账号"); return

    sender.reply("=====品赞授权(管理员)=====\n[1] 全部授权\n[2] 指定授权\n------------------\n回复序号，回复q退出\n==================")
    mode = sender.input(120000, 1, False)
    if not mode or mode.lower() == 'q':
        sender.reply("✅ 已取消授权"); return

    if mode == '1':
        all_accs = [item for lst in user_accounts.values() for item in lst]
        months = _input_months()
        if months:
            _do_auth_items(all_accs, months)
    elif mode == '2':
        sender.reply("请输入用户ID：\n------------------\n回复\"q\"退出\n==================")
        uid_inp = sender.input(120000, 1, False)
        if not uid_inp or uid_inp.lower() == 'q':
            sender.reply("✅ 已取消授权"); return
        uid_inp = uid_inp.strip()
        if uid_inp not in user_accounts:
            sender.reply(f"❌ 未找到用户ID: {uid_inp}"); return
        acc_list = user_accounts[uid_inp]
        msg = f"=====用户 {uid_inp} 的账号=====\n[0] 全部账号"
        for i, item in enumerate(acc_list, 1):
            msg += f"\n[{i}] {mask_phone(item['phone'])} | {item['remark']} | {item['auth_status']} | {item['expire_info']}"
        msg += "\n------------------\n输入0或序号（支持多选如:1,3），回复q退出\n=================="
        sender.reply(msg)
        acc_inp = sender.input(120000, 1, False)
        if not acc_inp or acc_inp.lower() == 'q':
            sender.reply("✅ 已取消授权"); return
        if acc_inp.strip() == '0':
            to_auth = acc_list
        else:
            try:
                valid, _ = parse_batch_selection(acc_inp, len(acc_list))
                to_auth = [acc_list[i - 1] for i in valid]
            except ValueError as e:
                sender.reply(f"❌ {str(e)}"); return
        months = _input_months()
        if months:
            _do_auth_items(to_auth, months)
    else:
        sender.reply("❌ 请输入1或2")

# ==================== 加白 / 删除白名单 ====================

def _get_pz_token_or_relogin(token_info, phone, password, remark):
    """获取签名密钥时若token过期则自动重登，返回 (headers, token, new_token_info)"""
    _, _, _, token = parse_token_info(token_info)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
    }
    return headers, token, token_info

def _refresh_token_if_needed(resp_json, phone, password, remark, acc):
    """检测登录过期并重新登录，返回 (ok, new_token, new_token_info)"""
    msg = resp_json.get('message', '')
    if '登录已过期' in msg or '未登录' in msg or 'token' in msg.lower():
        sender.reply("⚠️ 登录已过期，正在自动重新登录...")
        ok, _, new_token = pz_do_login(phone, password)
        if ok and new_token:
            new_info = f"{phone}#{password}#{remark}|{new_token}"
            middleware.bucketSet(bucket='dd_pz_token', key=acc, value=new_info)
            sender.reply("✅ 重新登录成功，继续执行...")
            return True, new_token, new_info
        sender.reply(f"❌ 重新登录失败")
        return False, None, None
    return False, None, None

def _do_whitelist_for_account(item, ip):
    """对单个账号执行加白，返回 (success, message)"""
    phone, password, remark, token, token_info = item['phone'], item['password'], item['remark'], item['token'], item['token_info']
    acc = item['acc']
    if not token:
        return False, "未保存token，请重新登录"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
    }

    try:
        resp = requests.post(f'{PZ_BASE}/home/users-get-user-aes', headers=headers, timeout=10)
        aes_data = resp.json()
        if aes_data.get('code') != 0:
            need_relogin, new_token, new_info = _refresh_token_if_needed(aes_data, phone, password, remark, acc)
            if not need_relogin:
                return False, f"获取签名密钥失败: {aes_data.get('message')}"
            token = new_token
            headers['Authorization'] = f'Bearer {token}'
            resp = requests.post(f'{PZ_BASE}/home/users-get-user-aes', headers=headers, timeout=10)
            aes_data = resp.json()
            if aes_data.get('code') != 0:
                return False, "重登后仍无法获取签名密钥"
        sign_key = aes_data['data']
    except Exception as e:
        return False, f"获取签名密钥异常: {str(e)}"

    try:
        resp = requests.get(f'{PZ_BASE}/home/userProduct-list?page=1&size=10', headers=headers, timeout=10)
        prod_data = resp.json()
        if prod_data.get('code') != 0 or not prod_data.get('data', {}).get('content'):
            return False, f"获取套餐信息失败: {prod_data.get('message')}"
        prod = prod_data['data']['content'][0]
        no = prod['no']
        status_type = prod['status_type'][:15].lower()
    except Exception as e:
        return False, f"获取套餐信息异常: {str(e)}"

    try:
        cipher = AES.new(sign_key.encode('utf-8'), AES.MODE_ECB)
        timestamp = int(time.time())
        data = f"{password}:{status_type}:{timestamp}".encode('utf-8')
        pad_len = 16 - (len(data) % 16)
        data += bytes([pad_len] * pad_len)
        sign = hexlify(cipher.encrypt(data)).decode('utf-8')
        resp = requests.post(f'{PZ_BASE}/whiteList-add', data={'no': no, 'ip': ip, 'sign': sign}, timeout=10)
        result = resp.json()
        if result.get('code') == 0:
            return True, f"加白成功，IP：{ip}"
        return False, f"加白失败：{result.get('message')}"
    except Exception as e:
        return False, f"加白请求异常：{str(e)}"


def pz_admin_add_whitelist():
    item = _pick_accounts_for_whitelist("品赞加白")
    if not item:
        return

    # 获取IP：使用 ipinfo.io/ip 获取当前公网IP，替换原来失效的接口
    is_admin = hasattr(sender, 'isAdmin') and sender.isAdmin()
    if is_admin:
        try:
            ip_resp = requests.get('https://ipinfo.io/ip', timeout=10)
            ip = ip_resp.text.strip()
            if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                raise ValueError(f"获取到的IP格式异常: {ip}")
            sender.reply(f"🔍 自动获取本机IP: {ip}\n正在为您加白...")
        except Exception as e:
            sender.reply(f"❌ 自动获取IP失败: {str(e)}\n请手动输入IP地址：\n------------------\n回复\"q\"退出\n==================")
            ip_inp = sender.input(120000, 1, False)
            if not ip_inp or ip_inp.lower() == 'q':
                sender.reply("✅ 已取消加白"); return
            ip = ip_inp.strip()
            if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
                sender.reply("❌ IP格式不正确，请输入正确的IPv4地址（如：1.2.3.4）"); return
    else:
        sender.reply("请输入要加白的IP地址：\n------------------\n回复\"q\"退出\n==================")
        ip_inp = sender.input(120000, 1, False)
        if not ip_inp or ip_inp.lower() == 'q':
            sender.reply("✅ 已取消加白"); return
        ip = ip_inp.strip()
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            sender.reply("❌ IP格式不正确，请输入正确的IPv4地址（如：1.2.3.4）"); return

    ok, msg = _do_whitelist_for_account(item, ip)
    phone = item['phone']
    if ok:
        sender.reply(f"✅ 加白成功！账号：{mask_phone(phone)}，IP：{ip}")
    else:
        sender.reply(f"❌ {msg}")


def pz_auto_whitelist():
    """管理员自动加白：自动获取公网IP，为管理员名下所有账号批量加白"""
    if not (hasattr(sender, 'isAdmin') and sender.isAdmin()):
        sender.reply("❌ 仅管理员可使用品赞自动加白指令"); return

    accounts = parse_accounts(uservalue)
    if not accounts:
        sender.reply("❌ 未找到任何账号，请先登录绑定"); return

    # 获取公网IP：使用 ipinfo.io/ip 获取当前公网IP，替换原来失效的接口
    try:
        ip_resp = requests.get('https://ipinfo.io/ip', timeout=10)
        ip = ip_resp.text.strip()
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            raise ValueError(f"IP格式异常: {ip}")
    except Exception as e:
        sender.reply(f"❌ 自动获取公网IP失败: {str(e)}\n请检查网络连接"); return

    sender.reply(f"🔍 本机公网IP: {ip}\n开始为 {len(accounts)} 个账号批量加白...")

    success_count, fail_count, results = 0, 0, []
    for acc in accounts:
        ti = middleware.bucketGet(bucket='dd_pz_token', key=acc)
        if not ti:
            results.append(f"❌ {acc[:3]}****{acc[7:]}: 未找到登录信息")
            fail_count += 1; continue
        phone, password, remark, token = parse_token_info(ti)
        if not phone:
            results.append(f"❌ {acc[:3]}****{acc[7:]}: 数据异常")
            fail_count += 1; continue
        item = {'phone': phone, 'password': password, 'remark': remark, 'token': token, 'token_info': ti, 'acc': acc}
        ok, msg = _do_whitelist_for_account(item, ip)
        if ok:
            results.append(f"✅ {mask_phone(phone)}: {msg}")
            success_count += 1
        else:
            results.append(f"❌ {mask_phone(phone)}: {msg}")
            fail_count += 1
        time.sleep(0.5)

    result_msg = f"=====自动加白结果=====\n🌐 IP: {ip}\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个\n------------------"
    for r in results:
        result_msg += f"\n{r}"
    result_msg += "\n=================="
    sender.reply(result_msg)

def pz_delete_whitelist():
    item = _pick_accounts_for_whitelist("品赞删除白名单")
    if not item:
        return
    phone, password, remark, token, token_info = item['phone'], item['password'], item['remark'], item['token'], item['token_info']
    acc = item['acc']
    if not token:
        sender.reply("❌ 该账号未保存token，请重新登录"); return

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Authorization': f'Bearer {token}',
    }

    # 获取用户ID
    ok_q, msg_q, user_id, _, _ = pz_query_info(token_info)
    if not ok_q:
        need_relogin, new_token, new_info = _refresh_token_if_needed({'message': msg_q}, phone, password, remark, acc)
        if need_relogin:
            token, token_info = new_token, new_info
            headers['Authorization'] = f'Bearer {token}'
            ok_q, msg_q, user_id, _, _ = pz_query_info(token_info)
        if not ok_q:
            sender.reply(f"❌ 获取用户信息失败: {msg_q}"); return

    # 获取套餐
    try:
        resp = requests.get(f'{PZ_BASE}/home/userProduct-list?page=1&size=10', headers=headers, timeout=10)
        prod_data = resp.json()
        if prod_data.get('code') != 0:
            need_relogin, new_token, new_info = _refresh_token_if_needed(prod_data, phone, password, remark, acc)
            if need_relogin:
                token, token_info = new_token, new_info
                headers['Authorization'] = f'Bearer {token}'
                resp = requests.get(f'{PZ_BASE}/home/userProduct-list?page=1&size=10', headers=headers, timeout=10)
                prod_data = resp.json()
            if prod_data.get('code') != 0 or not prod_data.get('data', {}).get('content'):
                sender.reply(f"❌ 获取套餐信息失败: {prod_data.get('message')}"); return
        if not prod_data.get('data', {}).get('content'):
            sender.reply("❌ 未找到套餐信息"); return
        no = prod_data['data']['content'][0]['no']
    except Exception as e:
        sender.reply(f"❌ 获取套餐信息异常: {str(e)}"); return

    # 获取白名单列表
    try:
        resp = requests.get(f'{PZ_BASE}/whiteList-get?no={no}&userId={user_id}', headers=headers, timeout=10)
        wl_data = resp.json()
        if wl_data.get('code') != 0:
            sender.reply(f"❌ 获取白名单列表失败: {wl_data.get('message')}"); return
        wl_list = wl_data.get('data', [])
        if not wl_list:
            sender.reply("❌ 当前账号没有白名单IP"); return
    except Exception as e:
        sender.reply(f"❌ 获取白名单列表异常: {str(e)}"); return

    ip_msg = f"=====白名单IP列表=====\n📱 账号: {mask_phone(phone)}"
    for i, item_w in enumerate(wl_list, 1):
        ip_msg += f"\n[{i}] IP: {item_w.get('id', '')}"
    ip_msg += "\n------------------\n请输入要删除的IP序号（支持多选如:1,3），回复q退出\n=================="
    sender.reply(ip_msg)

    ip_inp = sender.input(120000, 1, False)
    if not ip_inp or ip_inp.lower() == 'q':
        sender.reply("✅ 已取消删除"); return
    try:
        valid, _ = parse_batch_selection(ip_inp, len(wl_list))
    except ValueError as e:
        sender.reply(f"❌ {str(e)}"); return
    if not valid:
        sender.reply("❌ 未选择有效序号"); return

    del_headers = {**headers, 'Content-Type': 'application/json;charset=UTF-8'}
    success, fail, results = 0, 0, []
    for sel_i in valid:
        del_ip = wl_list[sel_i - 1].get('id', '')
        try:
            resp = requests.delete(f'{PZ_BASE}/whiteList-del', headers=del_headers,
                                   json={'ip': del_ip, 'no': no, 'userId': user_id}, timeout=10)
            result = resp.json()
            if result.get('code') == 0:
                results.append(f"✅ {del_ip} 删除成功"); success += 1
            else:
                results.append(f"❌ {del_ip} 删除失败: {result.get('message')}"); fail += 1
        except Exception as e:
            results.append(f"❌ {del_ip} 删除异常: {str(e)}"); fail += 1

    msg = f"=====白名单删除结果=====\n📱 账号: {mask_phone(phone)}\n✅ 成功:{success} ❌ 失败:{fail}\n------------------"
    for r in results:
        msg += f"\n{r}"
    msg += "\n=================="
    sender.reply(msg)

# ==================== 定时任务 ====================

def _push(user, message):
    try:
        middleware.Sender(user).reply(message)
    except Exception as e:
        print(f"推送失败: {str(e)}")

def run_cron():
    """定时任务：遍历所有用户执行签到"""
    all_users = middleware.bucketAllKeys(bucket='dd_pz_user')
    for user in all_users or []:
        raw = middleware.bucketGet(bucket='dd_pz_user', key=user)
        accs = parse_accounts(raw)
        for acc in accs:
            ti = middleware.bucketGet(bucket='dd_pz_token', key=acc)
            if not ti:
                continue
            phone, _, _, _ = parse_token_info(ti)
            accountVip = middleware.bucketGet(bucket='dd_pz_auth', key=acc) or ''
            is_auth = bool(accountVip) and accountVip >= today_time

            # 判断是否下级
            sub_flag = False
            if not is_auth and phone:
                ok_q, _, uid, _, _ = pz_query_info(ti)
                if ok_q and uid:
                    sub_flag = _is_subordinate(uid)

            if is_auth or sub_flag:
                ok, msg, _ = pz_checkin(ti)
                tag = " (下级免费)" if sub_flag else ""
                if ok:
                    _push(user, f"✅ 品赞签到成功{tag}\n📱 账号: {acc[:3]}****{acc[7:]}")
                else:
                    _push(user, f"⚠️ 品赞签到失败{tag}\n❌ {msg}\n💡 请检查账号状态")
            else:
                ok_q, _, uid, _, balance = pz_query_info(ti)
                if ok_q:
                    _push(user, f"📊 品赞账号信息\n🆔 用户ID: {uid}\n💰 金币: {balance}\n⚠️ 账号未授权，无法签到")
                else:
                    _push(user, "⚠️ 品赞账号异常\n❌ 无法获取账号信息")
            time.sleep(2)

# ==================== 主程序入口 ====================

pzVipmoney, pzcoin, superior_account, free_proxy, use_ma_pay = getusercontent()
today_time = str(datetime.now().date())
usermessage = sender.getMessage()
imtype = sender.getImtype()

if '登录' in usermessage or '登陆' in usermessage:
    pz_login()
elif '管理' in usermessage:
    pz_manage()
elif '查询' in usermessage:
    pz_query()
elif '任务' in usermessage:
    sender.reply(execute_tasks())
elif usermessage == '品赞清理':
    clean_expired_accounts()
elif usermessage == '品赞教程':
    show_tutorial()
elif usermessage == '品赞自动加白':
    pz_auto_whitelist()
elif '品赞加白' in usermessage:
    pz_admin_add_whitelist()
elif '品赞删除' in usermessage:
    pz_delete_whitelist()
elif usermessage == '品赞授权':
    pz_admin_auth()
elif imtype == 'fake':
    run_cron()
else:
    sender.setContinue()
