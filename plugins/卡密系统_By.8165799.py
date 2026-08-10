#[pin:false]
#[public:true]
#[disable:false]
# [rule: ^(签到|卡密系统管理|积分查询|查询积分|充值积分|积分充值|DD_.*|R_.*|KMXT_.*|卡密:DD_.*|更新配置|积分明细|积分流水|补签)$]
# [cron: 0 0 0 * * *]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [author: 8165799]
# [title: 卡密系统]
# [icon: https://i.miji.bid/2025/06/27/4aff8aa2b4f09d0d3f3bd97379836265.png]
# [class: 工具类]
# [version: 6.2]
# [price: 0]
# [description: 签到获取积分,积分可用于兑换各类服务。命令:签到丨积分查询丨充值积分丨积分明细丨补签丨卡密系统管理(管理员)<br>支持卡密充值,收款码充值,易支付充值,支持积分管理,支持服务积分设置<br>v6.1更新：易支付丨多支付菜单丨微信开关丨单项目CK限制丨卡密明细查询]
# [param: {"required":true,"key":"dd_sign_config.sign","bool":true,"placeholder":"","name":"签到功能","desc":"勾选可签到，默认关闭，需要先关闭奥特曼自带的签到功能！(用户系统里面)"}]
# [param: {"required":true,"key":"dd_sign_config.signcoin","bool":false,"placeholder":"默认:1-5 填写例:1-5","name":"积分区间","desc":"用户每次签到的积分区间"}]
# [param: {"required":true,"key":"dd_sign_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_sign_config.rate","bool":false,"placeholder":"默认:100 填写例:100","name":"兑换比例","desc":"1元=多少积分"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后可使用码支付进行充值"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_gateway","bool":false,"placeholder":"https://pay.xxxxx.com/","name":"码支付网关","desc":"支付网关地址，例如: https://pay.xxxxx.com/"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_pid","bool":false,"placeholder":"1001","name":"商户ID","desc":"支付平台的商户ID"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_key","bool":false,"placeholder":"89unJUB8HZ54Hj7x4nUj56HN4nUzUJ8i","name":"商户密钥","desc":"支付平台的商户密钥"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_type","bool":false,"placeholder":"alipay,wxpay,qqpay","name":"支付方式","desc":"支付方式，多个用英文逗号隔开，不填默认使用收银台模式"}]
# [param: {"required":true,"key":"dd_sign_config.ma_pay_notify_url","bool":false,"placeholder":"https://your-domain.com/notify","name":"回调地址","desc":"支付成功回调地址，例如: https://your-domain.com/notify"}]
# [param: {"required":false,"key":"dd_sign_config.epay_switch","bool":true,"placeholder":"","name":"易支付功能","desc":"开启后可使用易支付进行充值（与码支付独立）"}]
# [param: {"required":false,"key":"dd_sign_config.epay_url","bool":false,"placeholder":"如 http://pay.xxx.com/","name":"易支付网关","desc":"易支付接口网关地址(需带http及结尾/)"}]
# [param: {"required":false,"key":"dd_sign_config.epay_pid","bool":false,"placeholder":"","name":"易支付商户ID","desc":"易支付的PID"}]
# [param: {"required":false,"key":"dd_sign_config.epay_key","bool":false,"placeholder":"","name":"易支付商户密钥","desc":"易支付的KEY密钥"}]
# [param: {"required":false,"key":"dd_sign_config.epay_alipay","bool":true,"name":"易支付支付宝","desc":"启用易支付支付宝通道收款"}]
# [param: {"required":false,"key":"dd_sign_config.epay_wxpay","bool":true,"name":"易支付微信","desc":"启用易支付微信通道收款"}]
# [param: {"required":false,"key":"dd_sign_config.epay_qqpay","bool":true,"name":"易支付QQ","desc":"启用易支付QQ通道收款"}]
# [param: {"required":false,"key":"dd_sign_config.wechat_qr_switch","bool":true,"placeholder":"","name":"微信收款码支付","desc":"开启后可在支付菜单中使用微信收款码充值（需先在收款方式中配置收款码链接）"}]
# [param: {"required":false,"key":"dd_sign_config.project_ck_limit","bool":false,"placeholder":"默认:30 填写例:30","name":"单项目CK上限","desc":"用户在每个项目下最多可拥有的CK数量，0=不限制，用于生成卡密时默认值"}]


# ============================================================
# 第一部分：导入依赖
# ============================================================
import hashlib
import json
import random
import re
import time
from datetime import datetime, timedelta
from urllib.parse import quote

import middleware
import requests


# ============================================================
# 第二部分：全局上下文（发送者信息）
# ============================================================
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
imtype = sender.getImtype()
username = sender.getUserName()


# ============================================================
# 第三部分：常量定义
# ============================================================

# --- 存储桶名称 ---
CONFIG_BUCKET = 'dd_sign_config'
SIGN_DATE_BUCKET = 'dd_sign_dates'
POINTS_BUCKET = 'dd_sign_points'
CARD_BUCKET = 'dd_sign_cards'
RECHARGE_BUCKET = 'dd_sign_recharge'
PAY_ORDERS_BUCKET = 'dd_sign_orders'
STREAK_BUCKET = 'dd_sign_streaks'
TX_LOG_BUCKET = 'dd_sign_txlog'
ADMIN_LOG_BUCKET = 'dd_sign_adminlog'
CK_LIMIT_BUCKET = 'dd_sign_ck_limits'

# --- 支付方式中文映射 ---
PAY_TYPE_NAMES = {
    'alipay': '支付宝',
    'wxpay': '微信支付',
    'qqpay': 'QQ钱包',
}

# --- 连续签到加成阶梯: {天数: 倍率} ---
STREAK_TIERS = {3: 1.2, 7: 1.5, 14: 2.0, 30: 3.0}

# --- 签到配置 ---
signswitch = middleware.bucketGet(bucket=CONFIG_BUCKET, key='sign') or 'false'
signcoin = middleware.bucketGet(bucket=CONFIG_BUCKET, key='signcoin') or '1-5'

# --- 插件积分配置（运行时动态加载） ---
PLUGIN_CONFIGS = {}

# --- 系统设置 ---
STREAK_ENABLED = (middleware.bucketGet(CONFIG_BUCKET, 'streak_enabled') or 'true') == 'true'

def _load_int_config(key, default):
    try:
        return int(middleware.bucketGet(CONFIG_BUCKET, key) or str(default))
    except (ValueError, TypeError):
        return default

MAKEUP_COST = _load_int_config('makeup_cost', 0)
DEFAULT_CK_LIMIT = _load_int_config('project_ck_limit', 30)

# --- 支付配置 ---
PAYMENT_CONFIG = {
    'zsm': middleware.bucketGet(CONFIG_BUCKET, 'zsm') or '',
    'rate': middleware.bucketGet(CONFIG_BUCKET, 'rate') or '100',
    'ma_pay_switch': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_switch') or 'false',
    'ma_pay_gateway': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_gateway') or '',
    'ma_pay_pid': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_pid') or '',
    'ma_pay_key': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_key') or '',
    'ma_pay_type': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_type') or 'alipay,wxpay,qqpay',
    'ma_pay_notify_url': middleware.bucketGet(CONFIG_BUCKET, 'ma_pay_notify_url') or '',
    'use_mapi': middleware.bucketGet(CONFIG_BUCKET, 'use_mapi') or 'true',
}
PAYMENT_CONFIG['pid'] = PAYMENT_CONFIG['ma_pay_pid']
PAYMENT_CONFIG['key'] = PAYMENT_CONFIG['ma_pay_key']
PAYMENT_CONFIG['gateway'] = PAYMENT_CONFIG['ma_pay_gateway']

# --- 易支付配置 ---
EPAY_CONFIG = {
    'epay_switch': middleware.bucketGet(CONFIG_BUCKET, 'epay_switch') or 'false',
    'epay_url': middleware.bucketGet(CONFIG_BUCKET, 'epay_url') or '',
    'epay_pid': middleware.bucketGet(CONFIG_BUCKET, 'epay_pid') or '',
    'epay_key': middleware.bucketGet(CONFIG_BUCKET, 'epay_key') or '',
    'epay_alipay': (middleware.bucketGet(CONFIG_BUCKET, 'epay_alipay') or 'true').lower() == 'true',
    'epay_wxpay': (middleware.bucketGet(CONFIG_BUCKET, 'epay_wxpay') or 'false').lower() == 'true',
    'epay_qqpay': (middleware.bucketGet(CONFIG_BUCKET, 'epay_qqpay') or 'false').lower() == 'true',
}

# --- 微信收款码开关 ---
WECHAT_QR_SWITCH = (middleware.bucketGet(CONFIG_BUCKET, 'wechat_qr_switch') or 'false').lower() == 'true'


# ============================================================
# 第四部分：通用工具函数
# ============================================================

def calculate_md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def http_request(url: str, data: dict = None, method: str = 'GET'):
    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        if method == 'POST' and data:
            response = requests.post(url, data=data, headers=headers, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        return response.text
    except Exception as e:
        print(f"HTTP请求错误: {str(e)}")
        return None


def extract_redirect_url(html_content: str):
    if not html_content:
        return None
    match = re.search(r'location\.href\s*=\s*[\'"]([^\'"]+)[\'"]', html_content)
    return match.group(1) if match else None


def generate_qrcode(url: str):
    try:
        encoded_url = quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception as e:
        print(f"生成二维码失败: {str(e)}")
        return None


def _get_rate() -> int:
    try:
        return int(PAYMENT_CONFIG['rate'])
    except (ValueError, TypeError):
        return 100


def _safe_parse_int(value: str, error_msg: str = '输入错误!'):
    try:
        return int(value)
    except (ValueError, TypeError):
        sender.reply(error_msg)
        return None


# ============================================================
# 第五部分：积分流水 & 管理员日志
# ============================================================

def log_transaction(uid: str, amount: int, tx_type: str, desc: str):
    """记录积分流水（每用户保留最近50条）"""
    try:
        existing = middleware.bucketGet(TX_LOG_BUCKET, uid)
        logs = json.loads(existing) if existing else []
    except (json.JSONDecodeError, TypeError):
        logs = []

    logs.append({
        'amount': amount,
        'type': tx_type,
        'desc': desc,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'balance': int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)
    })

    if len(logs) > 50:
        logs = logs[-50:]

    middleware.bucketSet(TX_LOG_BUCKET, uid, json.dumps(logs))


def log_admin_action(admin_id: str, action: str, detail: str):
    """记录管理员操作（全局保留最近100条）"""
    try:
        existing = middleware.bucketGet(ADMIN_LOG_BUCKET, 'logs')
        logs = json.loads(existing) if existing else []
    except (json.JSONDecodeError, TypeError):
        logs = []

    logs.append({
        'admin': admin_id,
        'action': action,
        'detail': detail,
        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    if len(logs) > 100:
        logs = logs[-100:]

    middleware.bucketSet(ADMIN_LOG_BUCKET, 'logs', json.dumps(logs))


# ============================================================
# 第六部分：积分操作（带流水记录）
# ============================================================

def get_user_points(uid: str) -> int:
    return int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)


def add_user_points(uid: str, points: int, channel: str = "", name: str = "") -> int:
    current = int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)
    new_balance = current + points
    middleware.bucketSet(POINTS_BUCKET, uid, str(new_balance))
    if channel:
        log_transaction(uid, points, channel, f"{channel} +{points}")
    return new_balance


def deduct_user_points(uid: str, points: int, channel: str = "", name: str = "") -> bool:
    current = int(middleware.bucketGet(POINTS_BUCKET, uid) or 0)
    if current < points:
        return False
    middleware.bucketSet(POINTS_BUCKET, uid, str(current - points))
    if channel:
        log_transaction(uid, -points, channel, f"{channel} -{points}")
    return True


def use_points(plugin_id: str, points: int) -> tuple:
    if plugin_id not in PLUGIN_CONFIGS:
        return False, "插件不存在"

    current = get_user_points(userid)
    if current < points:
        return False, f"积分不足\n当前积分:{current}\n需要积分:{points}"

    # CK数量限制检查（自动读插件账号桶，插件无需配合）
    ck_bucket = _get_plugin_ck_bucket(plugin_id)
    if ck_bucket:
        can_add, cur_ck, max_ck, ck_msg = check_project_ck_limit(userid, plugin_id)
        if not can_add:
            return False, ck_msg

    try:
        if deduct_user_points(userid, points, PLUGIN_CONFIGS[plugin_id]['name'], username):
            return True, f"扣除{points}积分成功\n当前积分:{get_user_points(userid)}"
        return False, "扣除积分失败"
    except Exception:
        return False, "扣除积分失败"


# ============================================================
# 第七部分：连续签到系统
# ============================================================

def _get_streak(uid: str) -> int:
    """获取用户连续签到天数"""
    try:
        data = middleware.bucketGet(STREAK_BUCKET, uid)
        return int(data) if data else 0
    except (ValueError, TypeError):
        return 0


def _set_streak(uid: str, count: int):
    middleware.bucketSet(STREAK_BUCKET, uid, str(count))


def _get_streak_multiplier(streak: int) -> float:
    """根据连签天数返回最高适用的倍率"""
    if not STREAK_ENABLED:
        return 1.0
    multiplier = 1.0
    for days, mult in sorted(STREAK_TIERS.items()):
        if streak >= days:
            multiplier = mult
    return multiplier


def _get_next_streak_tier(streak: int) -> tuple:
    """返回下一个加成阶梯 (天数, 倍率)，如果已是最高返回 None"""
    for days, mult in sorted(STREAK_TIERS.items()):
        if streak < days:
            return days, mult
    return None


def sign():
    today = str(datetime.now().date())
    yesterday = str((datetime.now() - timedelta(days=1)).date())
    lock_key = f'sign_lock_{userid}'

    if middleware.bucketGet(CONFIG_BUCKET, lock_key):
        sender.reply('操作太频繁，请稍后再试~')
        return

    middleware.bucketSet(CONFIG_BUCKET, lock_key, '1')
    try:
        last_sign = middleware.bucketGet(SIGN_DATE_BUCKET, userid)
        if last_sign == today:
            sender.reply('你好,你今日已经签到过了哦~')
            return

        # 计算连续签到
        streak = _get_streak(userid)
        if last_sign == yesterday:
            streak += 1
        else:
            streak = 1

        # 基础积分
        min_coin, max_coin = map(int, signcoin.split('-'))
        base_coins = random.randint(min_coin, max_coin)

        # 连签加成
        multiplier = _get_streak_multiplier(streak)
        coins = int(base_coins * multiplier)
        bonus = coins - base_coins

        # 更新数据
        current_coins = add_user_points(userid, coins, "签到", username)
        middleware.bucketSet(SIGN_DATE_BUCKET, userid, today)
        _set_streak(userid, streak)

        # 构建回复
        msg = f"•你好,{username}\n"
        if bonus > 0:
            msg += f"•签到成功,获得{coins}🌸(基础{base_coins}+连签加成{bonus})\n"
        else:
            msg += f"•签到成功,获得{coins}🌸\n"

        msg += f"•连续签到: {streak}天"
        if streak >= 3 and STREAK_ENABLED:
            msg += f" 🔥(当前{multiplier}倍加成)"
        msg += "\n"

        next_tier = _get_next_streak_tier(streak)
        if next_tier and STREAK_ENABLED:
            msg += f"•再签{next_tier[0] - streak}天可达{next_tier[1]}倍加成!\n"

        msg += (f"•你还有: {current_coins}🌸\n"
                f"•你可通过以下操作获取🌸\n"
                f"① 【签到】每日签到\n"
                f"② 【积分查询】查看可兑换服务\n"
                f"③ 【充值积分】充值获取积分\n"
                f"④ 【积分明细】查看积分流水\n"
                f"⑤ 【补签】补签昨日(消耗积分)")
        sender.reply(msg)
    except Exception as e:
        sender.reply(f'签到失败:{str(e)}')
    finally:
        middleware.bucketDel(CONFIG_BUCKET, lock_key)


# ============================================================
# 第八部分：补签功能
# ============================================================

def makeup_sign():
    """补签昨日签到"""
    if signswitch != 'true':
        sender.reply('签到功能未开启!')
        return

    today = str(datetime.now().date())
    yesterday = str((datetime.now() - timedelta(days=1)).date())

    last_sign = middleware.bucketGet(SIGN_DATE_BUCKET, userid)

    if last_sign == today:
        day_before = str((datetime.now() - timedelta(days=2)).date())
        prev_sign = middleware.bucketGet(SIGN_DATE_BUCKET, f'{userid}_prev')
        if prev_sign == yesterday:
            sender.reply('你昨天已经签过到了，无需补签!')
            return

    if last_sign == yesterday:
        sender.reply('你昨天已经签过到了，无需补签!')
        return

    # 计算补签费用
    min_coin, max_coin = map(int, signcoin.split('-'))
    if MAKEUP_COST > 0:
        cost = MAKEUP_COST
    else:
        cost = max_coin * 2

    current = get_user_points(userid)
    if current < cost:
        sender.reply(f'积分不足!\n补签费用: {cost}积分\n当前积分: {current}积分')
        return

    sender.reply(f"========补签确认========\n"
                 f"补签日期: {yesterday}\n"
                 f"补签费用: {cost}积分\n"
                 f"当前积分: {current}积分\n"
                 f"========================\n"
                 f"确认补签回复\"确认\",取消回复\"q\"")

    choice = sender.input(60000, 1, False)
    if choice != '确认':
        sender.reply('已取消补签')
        return

    if not deduct_user_points(userid, cost, "补签", username):
        sender.reply('扣费失败,积分不足!')
        return

    # 更新连续签到
    streak = _get_streak(userid)
    if last_sign == today:
        streak += 1
    else:
        middleware.bucketSet(SIGN_DATE_BUCKET, userid, yesterday)
        streak = max(streak, 1) + 1

    _set_streak(userid, streak)

    sender.reply(f"补签成功!\n"
                 f"补签日期: {yesterday}\n"
                 f"消耗积分: {cost}\n"
                 f"当前积分: {get_user_points(userid)}\n"
                 f"连续签到: {streak}天")


# ============================================================
# 第九部分：积分查询 & 积分明细
# ============================================================

def query_points():
    msg = f"=====积分查询=====\n💰 总积分: {get_user_points(userid)}\n"

    # 显示连签信息
    streak = _get_streak(userid)
    if streak > 0:
        mult = _get_streak_multiplier(streak)
        msg += f"🔥 连续签到: {streak}天"
        if mult > 1.0:
            msg += f"({mult}倍加成)"
        msg += "\n"

    msg += "🎯 可用项目: 全部项目"

    # 显示CK限制信息
    ck_limit_val = get_user_ck_limit(userid)
    if ck_limit_val > 0:
        msg += f"\n🔒 CK上限: {ck_limit_val}个/项目"
        for plugin_id, pconfig in PLUGIN_CONFIGS.items():
            ck_bucket = pconfig.get('ck_bucket', '')
            if not ck_bucket:
                continue
            info = get_project_ck_info(userid, plugin_id)
            if info['current'] > 0 or info['max'] > 0:
                msg += f"\n  • {pconfig.get('name', plugin_id)}: {info['current']}/{info['max']}个"

    msg += ("\n==================\n"
            "💡 发送\"充值积分\"可充值\n"
            "📋 发送\"积分明细\"查看流水\n"
            "==================")
    sender.reply(msg)


def query_transaction_log():
    """查询积分流水"""
    try:
        existing = middleware.bucketGet(TX_LOG_BUCKET, userid)
        logs = json.loads(existing) if existing else []
    except (json.JSONDecodeError, TypeError):
        logs = []

    if not logs:
        sender.reply('暂无积分记录!')
        return

    msg = f"=====积分明细=====\n💰 当前积分: {get_user_points(userid)}\n"
    recent = logs[-15:]
    for entry in reversed(recent):
        amount = entry.get('amount', 0)
        sign_char = '+' if amount >= 0 else ''
        msg += (f"\n[{entry.get('time', '?')}]\n"
                f"  {entry.get('type', '未知')} {sign_char}{amount} → 余额{entry.get('balance', '?')}")

    msg += f"\n\n(显示最近{len(recent)}条,共{len(logs)}条记录)"
    sender.reply(msg)


# ============================================================
# 第十部分：卡密管理（支持有效期）
# ============================================================

def generate_card(amount: int, expire_days: int = 0, ck_limit: int = None) -> str:
    """生成一张卡密,expire_days=0表示永不过期,ck_limit=None使用全局默认"""
    chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    card = 'DD_' + ''.join(random.choice(chars) for _ in range(12))
    if ck_limit is None:
        ck_limit = DEFAULT_CK_LIMIT
    card_data = {
        'amount': amount,
        'status': 'unused',
        'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'expire_time': int(time.time()) + expire_days * 86400 if expire_days > 0 else 0,
        'ck_limit': ck_limit,
    }
    middleware.bucketSet(CARD_BUCKET, card, json.dumps(card_data))
    return card


def _parse_card_data(card_raw):
    """解析卡密数据,兼容旧格式(纯数字)和新格式(JSON)"""
    if not card_raw or card_raw == 'False':
        return None

    # 新格式: JSON
    try:
        data = json.loads(card_raw)
        if isinstance(data, dict):
            return data
    except (json.JSONDecodeError, TypeError):
        pass

    # 旧格式: 纯数字面额
    try:
        amount = int(card_raw)
        if amount > 0:
            return {'amount': amount, 'status': 'unused', 'expire_time': 0}
    except (ValueError, TypeError):
        pass

    return None


def _is_card_expired(card_data: dict) -> bool:
    expire_time = card_data.get('expire_time', 0)
    return expire_time > 0 and time.time() > expire_time


def use_card(card: str) -> tuple:
    """使用卡密充值"""
    try:
        card_match = re.search(r'(?:卡密:)?(DD_[A-Z0-9]{12})', card)
        if not card_match:
            return False, '卡密格式错误!'

        card = card_match.group(1)
        card_raw = middleware.bucketGet(CARD_BUCKET, card)

        if not card_raw:
            return False, '卡密不存在!'

        card_data = _parse_card_data(card_raw)
        if card_data is None:
            return False, '卡密数据异常!'

        # 已使用
        if card_data.get('status') == 'used' or 'user' in card_data:
            used_by = card_data.get('user', '未知')
            used_time = card_data.get('time', '未知')
            return False, f'卡密已被{used_by}使用\n使用时间:{used_time}'

        # 已过期
        if _is_card_expired(card_data):
            expire_str = datetime.fromtimestamp(card_data['expire_time']).strftime("%Y-%m-%d %H:%M")
            return False, f'卡密已过期!\n过期时间: {expire_str}'

        amount = card_data.get('amount', 0)
        if amount <= 0:
            return False, '卡密面额错误!'

        current = add_user_points(userid, amount, "卡密充值", username)

        # 卡密附带的CK限制：写入用户项目限制表
        ck_limit_val = card_data.get('ck_limit', 0)
        if ck_limit_val > 0:
            existing_limit = middleware.bucketGet(CK_LIMIT_BUCKET, userid)
            try:
                user_limits = json.loads(existing_limit) if existing_limit else {}
            except (json.JSONDecodeError, TypeError):
                user_limits = {}
            user_limits['_default'] = max(user_limits.get('_default', 0), ck_limit_val)
            middleware.bucketSet(CK_LIMIT_BUCKET, userid, json.dumps(user_limits))

        use_info = {
            'user': userid,
            'username': username,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'amount': amount,
            'status': 'used',
            'card_code': card,
            'ck_limit': ck_limit_val,
        }
        middleware.bucketSet(CARD_BUCKET, card, json.dumps(use_info))
        return True, f'充值成功!\n获得积分:{amount}\n当前积分:{current}'

    except Exception as e:
        print(f"充值过程出错: {str(e)}")
        return False, f'充值失败: {str(e)}'


# ============================================================
# 第十一.五部分：CK限制 & 卡密明细
# ============================================================

def _parse_plugin_account_list(raw_value) -> list:
    """解析插件账号桶中的账号列表，兼容多种格式"""
    if not raw_value:
        return []
    raw = str(raw_value).strip()
    # Python列表格式: ['acc1', 'acc2']
    if raw.startswith('[') and raw.endswith(']'):
        try:
            import ast
            parsed = ast.literal_eval(raw)
            if isinstance(parsed, (list, tuple, set)):
                return [str(x) for x in parsed]
        except (ValueError, SyntaxError):
            pass
        # JSON格式
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(x) for x in parsed]
        except (json.JSONDecodeError, ValueError):
            pass
    # 单值
    return [raw]


def _get_plugin_ck_bucket(plugin_id: str) -> str:
    """获取插件的CK账号存储桶名，优先手动配置→缓存→自动发现"""
    if plugin_id not in PLUGIN_CONFIGS:
        return ''

    # 1. 手动配置了 ck_bucket → 直接用（空字符串=明确不限制）
    if 'ck_bucket' in PLUGIN_CONFIGS[plugin_id]:
        return PLUGIN_CONFIGS[plugin_id]['ck_bucket']

    # 2. 查缓存（含「未找到」标记 __none__）
    cache_key = f'_ck_disco_{plugin_id}'
    cached = middleware.bucketGet(CK_LIMIT_BUCKET, cache_key)
    if cached == '__none__':
        return ''
    if cached:
        return cached

    # 3. 自动发现：尝试常见命名模式
    cfg_bucket = PLUGIN_CONFIGS[plugin_id].get('bucket', '')
    candidates = []
    if cfg_bucket:
        candidates.append(f'{cfg_bucket}_user')
    candidates.extend([
        f'{plugin_id}_user',
        f'{plugin_id}user',
        f'dd_{plugin_id}_user',
    ])

    for bucket in candidates:
        try:
            keys = middleware.bucketAllKeys(bucket)
            if keys:
                middleware.bucketSet(CK_LIMIT_BUCKET, cache_key, bucket)
                return bucket
        except Exception:
            pass

    # 没找到，缓存「未找到」避免重复探测
    middleware.bucketSet(CK_LIMIT_BUCKET, cache_key, '__none__')
    return ''


def get_user_ck_limit(uid: str) -> int:
    """获取用户全局CK上限，0=不限制"""
    try:
        limits = json.loads(middleware.bucketGet(CK_LIMIT_BUCKET, uid) or '{}')
        return int(limits.get('_default', 0))
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0


def set_user_ck_limit(uid: str, max_count: int):
    """设置用户全局CK上限"""
    try:
        limits = json.loads(middleware.bucketGet(CK_LIMIT_BUCKET, uid) or '{}')
    except (json.JSONDecodeError, TypeError):
        limits = {}
    limits['_default'] = max_count
    middleware.bucketSet(CK_LIMIT_BUCKET, uid, json.dumps(limits))


def get_project_ck_info(uid: str, plugin_id: str) -> dict:
    """获取用户在指定项目的CK使用情况（直接读插件账号桶），返回 {max: int, current: int, bucket: str}"""
    ck_bucket = _get_plugin_ck_bucket(plugin_id)
    if not ck_bucket:
        return {'max': 0, 'current': 0, 'bucket': ''}
    raw = middleware.bucketGet(ck_bucket, uid)
    accounts = _parse_plugin_account_list(raw)
    max_limit = get_user_ck_limit(uid)
    return {
        'max': max_limit,
        'current': len(accounts),
        'bucket': ck_bucket,
    }


def check_project_ck_limit(uid: str, plugin_id: str) -> tuple:
    """检查用户是否可以在指定项目添加更多CK（直接读插件桶数CK，不用插件配合）。
    返回 (can_add: bool, current: int, max: int, msg: str)"""
    ck_bucket = _get_plugin_ck_bucket(plugin_id)
    if not ck_bucket:
        return True, 0, 0, '插件未配置CK桶(不限制)'
    raw = middleware.bucketGet(ck_bucket, uid)
    accounts = _parse_plugin_account_list(raw)
    current = len(accounts)
    max_limit = get_user_ck_limit(uid)
    if max_limit <= 0:
        return True, current, 0, '无限制'
    if current >= max_limit:
        return False, current, max_limit, f'已达到单项目CK上限({max_limit}个)，请联系管理员提升限制!'
    return True, current, max_limit, f'当前{current}/{max_limit}个'


def query_card_detail(card_code: str) -> str:
    """查询卡密详细信息：使用者、积分去向"""
    card_match = re.search(r'(?:卡密:)?(DD_[A-Z0-9]{12})', card_code)
    if card_match:
        card_code = card_match.group(1)

    card_raw = middleware.bucketGet(CARD_BUCKET, card_code)
    if not card_raw:
        return f'卡密 {card_code} 不存在!'

    card_data = _parse_card_data(card_raw)
    if card_data is None:
        return f'卡密 {card_code} 数据异常!'

    msg = f"=====卡密明细=====\n📋 卡密: {card_code}\n"

    # 面额与有效期
    amount = card_data.get('amount', '?')
    msg += f"💰 面额: {amount}积分\n"

    ck_limit = card_data.get('ck_limit', 0)
    if ck_limit > 0:
        msg += f"🔒 CK上限: {ck_limit}个/项目\n"

    create_time = card_data.get('create_time', '?')
    msg += f"📅 生成时间: {create_time}\n"

    expire_time = card_data.get('expire_time', 0)
    if expire_time > 0:
        expire_str = datetime.fromtimestamp(expire_time).strftime("%Y-%m-%d %H:%M")
        msg += f"⏰ 有效期至: {expire_str}\n"
    else:
        msg += "⏰ 有效期: 永久\n"

    # 使用状态
    status = card_data.get('status', 'unused')
    if status == 'used' or 'user' in card_data:
        used_user = card_data.get('user', '?')
        used_name = card_data.get('username', '?')
        used_time = card_data.get('time', '?')
        msg += f"\n👤 使用者: {used_name}({used_user})\n"
        msg += f"🕐 使用时间: {used_time}\n"
        msg += "📌 状态: 已使用\n"

        # 查找积分流水：该用户在使用时间之后的消费记录
        try:
            existing = middleware.bucketGet(TX_LOG_BUCKET, used_user)
            tx_logs = json.loads(existing) if existing else []
        except (json.JSONDecodeError, TypeError):
            tx_logs = []

        # 筛选使用时间之后非卡密充值的流水
        used_dt = None
        try:
            used_dt = datetime.strptime(used_time, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            pass

        spent_items = []
        for entry in tx_logs:
            entry_time_str = entry.get('time', '')
            try:
                entry_dt = datetime.strptime(entry_time_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                continue
            if used_dt and entry_dt < used_dt:
                continue
            tx_type = entry.get('type', '')
            if tx_type in ('卡密充值', '充值', '易支付充值', '码支付充值', '转入', '管理员调整'):
                continue
            spent_items.append(entry)

        if spent_items:
            msg += "\n💸 积分去向:\n"
            for item in spent_items[-20:]:
                amt = item.get('amount', 0)
                msg += (f"  [{item.get('time', '?')}] {item.get('type', '?')} "
                        f"{'+' if amt >= 0 else ''}{amt} → 余额{item.get('balance', '?')}\n")
            if len(spent_items) > 20:
                msg += f"  ...共{len(spent_items)}条消费记录\n"
        else:
            msg += "\n💸 积分去向: 暂无消费记录\n"

        # 显示当前CK使用情况
        try:
            limits = json.loads(middleware.bucketGet(CK_LIMIT_BUCKET, used_user) or '{}')
            if limits:
                msg += "\n📊 当前CK限制:\n"
                for key, val in limits.items():
                    if key == '_default':
                        msg += f"  全局上限: {val}个/项目\n"
        except (json.JSONDecodeError, TypeError):
            pass
    else:
        msg += "📌 状态: 未使用\n"

    msg += "=================="
    return msg


def query_user_cards(uid: str) -> str:
    """按用户QQ查询：使用了哪些卡密、总计获得积分、剩余积分"""
    current_points = get_user_points(uid)
    msg = f"=====用户 {uid} 卡密明细=====\n💰 当前剩余积分: {current_points}\n"

    # 遍历卡密桶查找该用户使用的卡密
    cards = middleware.bucketAllKeys(CARD_BUCKET)
    used_cards = []
    total_card_points = 0

    for card in cards:
        if not card.startswith('DD_'):
            continue
        card_raw = middleware.bucketGet(CARD_BUCKET, card)
        card_data = _parse_card_data(card_raw)
        if card_data is None:
            continue
        # 匹配使用者
        used_user = card_data.get('user', '')
        if str(used_user) != str(uid):
            continue
        used_time = card_data.get('time', '?')
        amount = card_data.get('amount', 0)
        total_card_points += amount
        used_cards.append((card, amount, used_time))

    if not used_cards:
        msg += "\n📭 该用户未使用过任何卡密"
        msg += "\n=================="
        return msg

    used_cards.sort(key=lambda x: x[2], reverse=True)

    msg += f"\n📋 已使用卡密: {len(used_cards)}张"
    msg += f"\n💳 卡密获得总计: {total_card_points}积分\n"
    msg += f"\n📜 卡密列表:\n"

    for card_code, amt, used_time in used_cards:
        msg += f"  [{used_time}] {card_code} +{amt}积分\n"

    # 也查一下积分流水中的消费汇总
    try:
        existing = middleware.bucketGet(TX_LOG_BUCKET, uid)
        tx_logs = json.loads(existing) if existing else []
    except (json.JSONDecodeError, TypeError):
        tx_logs = []

    total_spent = 0
    spend_by_project = {}
    for entry in tx_logs:
        tx_type = entry.get('type', '')
        amt = entry.get('amount', 0)
        # 只统计消费（负数），排除充值和转入
        if tx_type in ('卡密充值', '充值', '易支付充值', '码支付充值', '转入', '管理员调整'):
            continue
        if amt < 0:
            total_spent += abs(amt)
            spend_by_project[tx_type] = spend_by_project.get(tx_type, 0) + abs(amt)

    if total_spent > 0:
        msg += f"\n💸 累计消费: {total_spent}积分"
        if spend_by_project:
            msg += "\n  消费明细:"
            for proj, sp in sorted(spend_by_project.items(), key=lambda x: x[1], reverse=True):
                msg += f"\n    • {proj}: {sp}积分"

    msg += "\n=================="
    return msg


# ============================================================
# 第十二部分：系统管理 - 子功能
# ============================================================

def _admin_generate_cards():
    """管理 - 生成卡密"""
    sender.reply("请选择生成方式:\n1、单张生成\n2、批量生成\n=============\n回复序号,退出【q】！")
    subchoice = sender.input(120000, 1, False)

    if subchoice == 'q':
        return

    if subchoice in ('1', '2'):
        sender.reply('请输入卡密面额(积分):')
        amount = _safe_parse_int(sender.input(120000, 1, False), '面额必须是数字!')
        if amount is None: return
        if amount <= 0:
            sender.reply('面额必须大于0')
            return

        sender.reply('请输入有效期天数(0=永不过期):')
        expire_days = _safe_parse_int(sender.input(120000, 1, False), '天数必须是数字!')
        if expire_days is None: return
        if expire_days < 0:
            sender.reply('天数不能为负数')
            return

        sender.reply(f'请输入单项目CK上限(0=不限制, 默认{DEFAULT_CK_LIMIT}):')
        ck_limit_input = sender.input(120000, 1, False)
        if ck_limit_input == '' or ck_limit_input is None:
            ck_limit = DEFAULT_CK_LIMIT
        else:
            ck_limit = _safe_parse_int(ck_limit_input, 'CK上限必须是数字!')
            if ck_limit is None: return
            if ck_limit < 0:
                sender.reply('CK上限不能为负数')
                return

        expire_text = f"{expire_days}天后过期" if expire_days > 0 else "永不过期"
        ck_text = f"单项目上限{ck_limit}个" if ck_limit > 0 else "不限制CK数量"

        if subchoice == '1':
            card = generate_card(amount, expire_days, ck_limit)
            log_admin_action(userid, "生成卡密", f"面额{amount} {expire_text} {ck_text} 卡密:{card}")
            sender.reply(f'生成成功!\n卡密:{card}\n面额:{amount}积分\n有效期:{expire_text}\nCK限制:{ck_text}')
        else:
            sender.reply('请输入生成数量:')
            count = _safe_parse_int(sender.input(120000, 1, False), '数量必须是数字!')
            if count is None: return
            if count <= 0 or count > 100:
                sender.reply('数量必须在1-100之间')
                return

            cards = [generate_card(amount, expire_days, ck_limit) for _ in range(count)]
            log_admin_action(userid, "批量生成卡密", f"面额{amount} {expire_text} {ck_text} 数量{count}张")
            msg = f'批量生成成功!\n面额:{amount}积分\n数量:{count}张\n有效期:{expire_text}\nCK限制:{ck_text}\n\n卡密列表:\n'
            msg += '\n'.join(cards)
            sender.reply(msg)
    else:
        sender.reply('输入错误!')


def _admin_view_cards():
    """管理 - 查看卡密（分类查看+导出）"""
    sender.reply("========卡密管理========\n"
                 "1、查看未使用卡密\n"
                 "2、查看已使用卡密\n"
                 "3、查看已过期卡密\n"
                 "4、导出未使用卡密\n"
                 "5、查看全部卡密\n"
                 "======================\n回复序号,退出【q】！")
    subchoice = sender.input(120000, 1, False)

    if subchoice == 'q':
        return

    cards = middleware.bucketAllKeys(CARD_BUCKET)
    if not cards:
        sender.reply('暂无卡密!')
        return

    unused_cards = []
    used_cards = []
    expired_cards = []

    for card in cards:
        if not card.startswith('DD_'):
            continue
        card_raw = middleware.bucketGet(CARD_BUCKET, card)
        card_data = _parse_card_data(card_raw)
        if card_data is None:
            continue

        if card_data.get('status') == 'used' or 'user' in card_data:
            used_cards.append((card, card_data))
        elif _is_card_expired(card_data):
            expired_cards.append((card, card_data))
        else:
            unused_cards.append((card, card_data))

    def _format_expire(data):
        et = data.get('expire_time', 0)
        if et == 0:
            return '永久'
        return datetime.fromtimestamp(et).strftime("%Y-%m-%d %H:%M")

    if subchoice == '1':
        if not unused_cards:
            sender.reply('暂无未使用的卡密!')
            return
        msg = f'========未使用卡密({len(unused_cards)}张)========\n'
        for card, data in unused_cards:
            msg += f'卡密:{card}\n面额:{data.get("amount", "?")}积分\n有效期:{_format_expire(data)}\n\n'
        sender.reply(msg)

    elif subchoice == '2':
        if not used_cards:
            sender.reply('暂无已使用的卡密!')
            return
        msg = f'========已使用卡密({len(used_cards)}张)========\n'
        for card, data in used_cards:
            msg += (f'卡密:{card}\n面额:{data.get("amount", "?")}积分\n'
                    f'使用者:{data.get("user", "?")}\n使用时间:{data.get("time", "?")}\n\n')
        sender.reply(msg)

    elif subchoice == '3':
        if not expired_cards:
            sender.reply('暂无过期卡密!')
            return
        msg = f'========已过期卡密({len(expired_cards)}张)========\n'
        for card, data in expired_cards:
            msg += f'卡密:{card}\n面额:{data.get("amount", "?")}积分\n过期时间:{_format_expire(data)}\n\n'
        sender.reply(msg)

    elif subchoice == '4':
        if not unused_cards:
            sender.reply('暂无可导出的卡密!')
            return
        msg = f'===未使用卡密导出({len(unused_cards)}张)===\n'
        for card, data in unused_cards:
            msg += f'{card} | {data.get("amount", "?")}积分 | {_format_expire(data)}\n'
        sender.reply(msg)

    elif subchoice == '5':
        msg = (f'========卡密统计========\n'
               f'未使用: {len(unused_cards)}张\n'
               f'已使用: {len(used_cards)}张\n'
               f'已过期: {len(expired_cards)}张\n'
               f'总计: {len(unused_cards) + len(used_cards) + len(expired_cards)}张\n'
               f'========================\n')

        all_items = []
        for card, data in unused_cards:
            all_items.append(f'[未使用] {card} | {data.get("amount", "?")}积分 | {_format_expire(data)}')
        for card, data in expired_cards:
            all_items.append(f'[已过期] {card} | {data.get("amount", "?")}积分')
        for card, data in used_cards:
            all_items.append(f'[已使用] {card} | {data.get("amount", "?")}积分 | {data.get("user", "?")}')

        if len(all_items) > 30:
            msg += '\n'.join(all_items[:30])
            msg += f'\n...(仅显示前30条,共{len(all_items)}条)'
        else:
            msg += '\n'.join(all_items)
        sender.reply(msg)
    else:
        sender.reply('输入错误!')


def _admin_delete_card():
    """管理 - 删除卡密"""
    sender.reply('请输入要删除的卡密:')
    card = sender.input(120000, 1, False)
    if middleware.bucketDel(CARD_BUCKET, card):
        log_admin_action(userid, "删除卡密", f"卡密:{card}")
        sender.reply('删除成功!')
    else:
        sender.reply('卡密不存在!')


def _admin_cleanup_expired():
    """管理 - 清理过期卡密"""
    cards = middleware.bucketAllKeys(CARD_BUCKET)
    cleaned = 0
    for card in cards:
        if not card.startswith('DD_'):
            continue
        card_data = _parse_card_data(middleware.bucketGet(CARD_BUCKET, card))
        if card_data and card_data.get('status') != 'used' and 'user' not in card_data:
            if _is_card_expired(card_data):
                middleware.bucketDel(CARD_BUCKET, card)
                cleaned += 1

    log_admin_action(userid, "清理过期卡密", f"清理{cleaned}张")
    sender.reply(f'清理完成!\n已清理过期卡密: {cleaned}张')


def _admin_points_manage():
    """管理 - 积分管理"""
    sender.reply("========积分管理========\n1、查询用户积分\n2、修改用户积分\n"
                 "3、批量充值积分\n======================\n回复序号,退出【q】！")
    subchoice = sender.input(120000, 1, False)

    if subchoice == '1':
        sender.reply('请输入用户ID:')
        user_id = sender.input(120000, 1, False)
        pts = get_user_points(user_id)
        streak = _get_streak(user_id)
        msg = f"用户: {user_id}\n积分: {pts}\n连续签到: {streak}天"
        sender.reply(msg)

    elif subchoice == '2':
        sender.reply('请输入用户ID:')
        user_id = sender.input(120000, 1, False)
        current = get_user_points(user_id)
        sender.reply(f'该用户当前积分: {current}\n请输入积分数量(正数增加,负数扣除):')
        amount = _safe_parse_int(sender.input(120000, 1, False))
        if amount is None: return
        if amount < 0 and abs(amount) > current:
            sender.reply('积分不足,无法扣除!')
            return
        add_user_points(user_id, amount, "管理员调整", "")
        log_admin_action(userid, "修改用户积分", f"用户{user_id} {'+' if amount >= 0 else ''}{amount}积分")
        sender.reply(f'修改成功!\n用户: {user_id}\n调整: {"+"+str(amount) if amount>=0 else str(amount)}\n当前积分: {get_user_points(user_id)}')

    elif subchoice == '3':
        sender.reply('请输入充值金额:')
        amount = _safe_parse_int(sender.input(120000, 1, False))
        if amount is None: return
        if amount <= 0:
            sender.reply('金额必须大于0')
            return

        sender.reply('请输入用户ID列表(用逗号分隔):')
        users = sender.input(120000, 1, False).split(',')
        success = 0
        for user_id in users:
            user_id = user_id.strip()
            if user_id:
                add_user_points(user_id, amount, "批量充值", "")
                success += 1
        log_admin_action(userid, "批量充值积分", f"{success}个用户各充值{amount}积分")
        sender.reply(f'批量充值完成!\n成功:{success}\n失败:{len(users)-success}')


def _admin_payment_config():
    """管理 - 支付配置"""
    global WECHAT_QR_SWITCH
    msg = (f"========支付配置========\n当前配置:\n"
           f"赞赏码: {'已配置' if PAYMENT_CONFIG['zsm'] else '未配置'}\n"
           f"兑换比例: 1元={PAYMENT_CONFIG['rate']}积分\n"
           f"MAPI接口: {'已启用' if PAYMENT_CONFIG['use_mapi'] == 'true' else '已禁用'}\n"
           f"码支付商户ID: {PAYMENT_CONFIG['ma_pay_pid'] or '未设置'}\n"
           f"码支付网关: {PAYMENT_CONFIG['ma_pay_gateway'] or '未设置'}\n"
           f"码支付回调地址: {PAYMENT_CONFIG['ma_pay_notify_url'] or '未设置'}\n"
           f"---易支付---\n"
           f"易支付状态: {'已启用' if EPAY_CONFIG['epay_switch'] == 'true' else '已禁用'}\n"
           f"易支付网关: {EPAY_CONFIG['epay_url'] or '未设置'}\n"
           f"易支付商户ID: {EPAY_CONFIG['epay_pid'] or '未设置'}\n"
           f"---微信收款码---\n"
           f"微信收款码: {'已启用' if WECHAT_QR_SWITCH else '已禁用'}\n"
           f"收款码链接: {'已配置' if PAYMENT_CONFIG['zsm'] else '未配置'}\n\n"
           f"1、设置赞赏码\n2、设置兑换比例\n3、切换MAPI接口\n"
           f"4、设置码支付商户ID\n5、设置码支付密钥\n6、设置码支付网关\n"
           f"7、设置码支付回调地址\n"
           f"---易支付设置---\n"
           f"8、切换易支付开关\n9、设置易支付网关\n10、设置易支付商户ID\n"
           f"11、设置易支付密钥\n12、设置易支付通道\n"
           f"---微信收款码---\n"
           f"13、切换微信收款码开关\n"
           f"======================\n回复序号,退出【q】！")
    sender.reply(msg)
    subchoice = sender.input(120000, 1, False)

    if subchoice == '1':
        sender.reply('请发送赞赏码图片链接:')
        zsm = sender.input(120000, 1, False)
        middleware.bucketSet(CONFIG_BUCKET, 'zsm', zsm)
        PAYMENT_CONFIG['zsm'] = zsm
        log_admin_action(userid, "设置赞赏码", "更新赞赏码链接")
        sender.reply('设置成功!')

    elif subchoice == '2':
        sender.reply('请输入兑换比例(1元=?积分):')
        rate = _safe_parse_int(sender.input(120000, 1, False))
        if rate is None: return
        if rate <= 0:
            sender.reply('比例必须大于0')
            return
        middleware.bucketSet(CONFIG_BUCKET, 'rate', str(rate))
        PAYMENT_CONFIG['rate'] = str(rate)
        log_admin_action(userid, "设置兑换比例", f"1元={rate}积分")
        sender.reply('设置成功!')

    elif subchoice == '3':
        current = PAYMENT_CONFIG['use_mapi']
        new_value = 'false' if current == 'true' else 'true'
        middleware.bucketSet(CONFIG_BUCKET, 'use_mapi', new_value)
        PAYMENT_CONFIG['use_mapi'] = new_value
        log_admin_action(userid, "切换MAPI", f"{'启用' if new_value == 'true' else '禁用'}")
        sender.reply(f'MAPI接口已{"启用" if new_value == "true" else "禁用"}!')

    elif subchoice == '4':
        sender.reply('请输入码支付商户ID:')
        pid = sender.input(120000, 1, False)
        middleware.bucketSet(CONFIG_BUCKET, 'ma_pay_pid', pid)
        PAYMENT_CONFIG['ma_pay_pid'] = pid
        PAYMENT_CONFIG['pid'] = pid
        log_admin_action(userid, "设置商户ID", f"PID:{pid}")
        sender.reply('设置成功!')

    elif subchoice == '5':
        sender.reply('请输入码支付密钥:')
        key = sender.input(120000, 1, False)
        middleware.bucketSet(CONFIG_BUCKET, 'ma_pay_key', key)
        PAYMENT_CONFIG['ma_pay_key'] = key
        PAYMENT_CONFIG['key'] = key
        log_admin_action(userid, "设置商户密钥", "已更新密钥")
        sender.reply('设置成功!')

    elif subchoice == '6':
        sender.reply('请输入码支付网关地址(例如: https://pay.domain.com):')
        gateway = sender.input(120000, 1, False)
        middleware.bucketSet(CONFIG_BUCKET, 'ma_pay_gateway', gateway)
        PAYMENT_CONFIG['ma_pay_gateway'] = gateway
        PAYMENT_CONFIG['gateway'] = gateway
        log_admin_action(userid, "设置支付网关", f"网关:{gateway}")
        sender.reply('设置成功!')

    elif subchoice == '7':
        sender.reply('请输入码支付回调地址(例如: https://your-domain.com/notify):')
        notify_url = sender.input(120000, 1, False)
        if notify_url:
            middleware.bucketSet(CONFIG_BUCKET, 'ma_pay_notify_url', notify_url)
            PAYMENT_CONFIG['ma_pay_notify_url'] = notify_url
            log_admin_action(userid, "设置回调地址", f"URL:{notify_url}")
            sender.reply('设置成功!')
        else:
            sender.reply('回调地址不能为空!')

    elif subchoice == '8':
        current = EPAY_CONFIG['epay_switch']
        new_value = 'false' if current == 'true' else 'true'
        middleware.bucketSet(CONFIG_BUCKET, 'epay_switch', new_value)
        EPAY_CONFIG['epay_switch'] = new_value
        log_admin_action(userid, "切换易支付", f"{'启用' if new_value == 'true' else '禁用'}")
        sender.reply(f'易支付已{"启用" if new_value == "true" else "禁用"}!')

    elif subchoice == '9':
        sender.reply('请输入易支付网关地址(例如: http://pay.domain.com/):')
        epay_url = sender.input(120000, 1, False)
        middleware.bucketSet(CONFIG_BUCKET, 'epay_url', epay_url)
        EPAY_CONFIG['epay_url'] = epay_url
        log_admin_action(userid, "设置易支付网关", f"网关:{epay_url}")
        sender.reply('设置成功!')

    elif subchoice == '10':
        sender.reply('请输入易支付商户ID:')
        epay_pid = sender.input(120000, 1, False)
        middleware.bucketSet(CONFIG_BUCKET, 'epay_pid', epay_pid)
        EPAY_CONFIG['epay_pid'] = epay_pid
        log_admin_action(userid, "设置易支付PID", f"PID:{epay_pid}")
        sender.reply('设置成功!')

    elif subchoice == '11':
        sender.reply('请输入易支付密钥:')
        epay_key = sender.input(120000, 1, False)
        middleware.bucketSet(CONFIG_BUCKET, 'epay_key', epay_key)
        EPAY_CONFIG['epay_key'] = epay_key
        log_admin_action(userid, "设置易支付密钥", "已更新密钥")
        sender.reply('设置成功!')

    elif subchoice == '12':
        current_status = (f"支付宝: {'✓' if EPAY_CONFIG['epay_alipay'] else '✗'}  "
                         f"微信: {'✓' if EPAY_CONFIG['epay_wxpay'] else '✗'}  "
                         f"QQ: {'✓' if EPAY_CONFIG['epay_qqpay'] else '✗'}")
        sender.reply(f"当前易支付通道:\n{current_status}\n\n请输入要切换的通道(1=支付宝 2=微信 3=QQ):")
        ch = sender.input(120000, 1, False)
        if ch == '1':
            new_val = 'false' if EPAY_CONFIG['epay_alipay'] else 'true'
            middleware.bucketSet(CONFIG_BUCKET, 'epay_alipay', new_val)
            EPAY_CONFIG['epay_alipay'] = new_val == 'true'
            sender.reply(f'支付宝通道已{"开启" if EPAY_CONFIG["epay_alipay"] else "关闭"}!')
        elif ch == '2':
            new_val = 'false' if EPAY_CONFIG['epay_wxpay'] else 'true'
            middleware.bucketSet(CONFIG_BUCKET, 'epay_wxpay', new_val)
            EPAY_CONFIG['epay_wxpay'] = new_val == 'true'
            sender.reply(f'微信通道已{"开启" if EPAY_CONFIG["epay_wxpay"] else "关闭"}!')
        elif ch == '3':
            new_val = 'false' if EPAY_CONFIG['epay_qqpay'] else 'true'
            middleware.bucketSet(CONFIG_BUCKET, 'epay_qqpay', new_val)
            EPAY_CONFIG['epay_qqpay'] = new_val == 'true'
            sender.reply(f'QQ通道已{"开启" if EPAY_CONFIG["epay_qqpay"] else "关闭"}!')
        else:
            sender.reply('输入错误!')

    elif subchoice == '13':
        new_val = 'false' if WECHAT_QR_SWITCH else 'true'
        middleware.bucketSet(CONFIG_BUCKET, 'wechat_qr_switch', new_val)
        WECHAT_QR_SWITCH = new_val == 'true'
        log_admin_action(userid, "切换微信收款码", f"{'启用' if WECHAT_QR_SWITCH else '禁用'}")
        sender.reply(f'微信收款码已{"启用" if WECHAT_QR_SWITCH else "禁用"}!')

    else:
        sender.reply('输入错误!')


def _add_plugin_config(plugin_id: str, bucket: str, coin_key: str, name: str, ck_bucket: str = '') -> bool:
    if plugin_id in PLUGIN_CONFIGS:
        sender.reply(f'插件/服务ID [{plugin_id}] 已存在!')
        return False

    new_config = {'bucket': bucket, 'coin_key': coin_key, 'name': name}
    if ck_bucket:
        new_config['ck_bucket'] = ck_bucket
    try:
        custom_plugins = json.loads(middleware.bucketGet(CONFIG_BUCKET, 'custom_plugins') or '{}')
    except json.JSONDecodeError:
        custom_plugins = {}

    custom_plugins[plugin_id] = new_config
    try:
        middleware.bucketSet(CONFIG_BUCKET, 'custom_plugins', json.dumps(custom_plugins))
        PLUGIN_CONFIGS[plugin_id] = new_config
        return True
    except Exception as e:
        sender.reply(f'保存配置失败: {str(e)}')
        return False


def _admin_service_points():
    """管理 - 服务积分设置"""
    msg = "========服务积分设置========\n当前支持的服务:"

    service_list = []
    for idx, (service_id, config) in enumerate(PLUGIN_CONFIGS.items(), 1):
        service_list.append((str(idx), service_id, config['name']))
        ck_tag = ' 🔒' if config.get('ck_bucket') else ''
        msg += f"\n{idx}、{config['name']}{ck_tag}"

    msg += ("\n======================\n操作选项:\na、新增服务\nd、删除服务\n"
            "或输入序号修改积分\n退出请输入【q】")
    sender.reply(msg)

    service_map = {str(idx): service_id for idx, service_id, _ in service_list}
    subchoice = sender.input(120000, 1, False)

    if subchoice == 'q':
        return

    if subchoice == 'a':
        sender.reply("请按以下格式输入服务信息:\n服务ID,存储桶名,积分键名,显示名称\n"
                     "示例: myplugin,dd_myplugin,coin,我的插件")
        service_info = sender.input(120000, 1, False)
        try:
            service_id, bucket, coin_key, name = [x.strip() for x in service_info.split(',')]
            if _add_plugin_config(service_id, bucket, coin_key, name):
                log_admin_action(userid, "新增服务", f"{name}({service_id})")
                sender.reply(f'成功添加服务: {name}')
        except ValueError:
            sender.reply('输入格式错误!')

    elif subchoice == 'd':
        sender.reply('请输入要删除的服务序号:')
        del_idx = sender.input(120000, 1, False)
        if del_idx not in service_map:
            sender.reply('序号无效!')
            return

        service_id = service_map[del_idx]
        service_name = PLUGIN_CONFIGS[service_id]['name']

        try:
            custom_plugins = json.loads(middleware.bucketGet(CONFIG_BUCKET, 'custom_plugins') or '{}')
        except json.JSONDecodeError:
            custom_plugins = {}

        if service_id in custom_plugins:
            del custom_plugins[service_id]
            middleware.bucketSet(CONFIG_BUCKET, 'custom_plugins', json.dumps(custom_plugins))
            del PLUGIN_CONFIGS[service_id]
            log_admin_action(userid, "删除服务", f"{service_name}({service_id})")
            sender.reply(f'成功删除服务: {service_name}')
        else:
            sender.reply('该服务为系统内置,无法删除!')

    elif subchoice in service_map:
        service = service_map[subchoice]
        config = PLUGIN_CONFIGS[service]
        current = middleware.bucketGet(config['bucket'], config['coin_key']) or '未设置'
        current_ck = config.get('ck_bucket', '')
        sender.reply(f'当前{config["name"]}:\n需要积分: {current}\nCK限制桶: {current_ck or "未设置"}\n\n'
                     f'1、修改积分数量\n2、设置CK限制桶\n'
                     f'======================\n回复序号,退出【q】！')
        sub2 = sender.input(120000, 1, False)
        if sub2 == 'q':
            return
        if sub2 == '1':
            sender.reply('请输入新的积分数量:')
            new_coins = _safe_parse_int(sender.input(120000, 1, False))
            if new_coins is None: return
            if new_coins <= 0:
                sender.reply('积分必须大于0')
                return
            middleware.bucketSet(config['bucket'], config['coin_key'], str(new_coins))
            log_admin_action(userid, "修改服务积分", f"{config['name']}设为{new_coins}积分")
            sender.reply(f'设置成功!\n{config["name"]}现在需要{new_coins}积分')
        elif sub2 == '2':
            sender.reply(f'当前CK限制桶: {current_ck or "未设置"}\n请输入插件存储账号列表的桶名(如zhqd_user)，留空=不限制:')
            new_ck = sender.input(120000, 1, False)
            if new_ck is None:
                return
            new_ck = new_ck.strip()
            # 更新运行内存和持久化
            PLUGIN_CONFIGS[service]['ck_bucket'] = new_ck
            try:
                custom_plugins = json.loads(middleware.bucketGet(CONFIG_BUCKET, 'custom_plugins') or '{}')
            except json.JSONDecodeError:
                custom_plugins = {}
            if service in custom_plugins:
                custom_plugins[service]['ck_bucket'] = new_ck
                middleware.bucketSet(CONFIG_BUCKET, 'custom_plugins', json.dumps(custom_plugins))
            log_admin_action(userid, "设置CK桶", f"{config['name']} → {new_ck or '取消限制'}")
            sender.reply(f'设置成功!\n{config["name"]} CK限制桶: {new_ck or "不限制"}')
        else:
            sender.reply('输入错误!')
    else:
        sender.reply('输入错误!')


def _admin_add_plugin_config():
    """管理 - 添加插件积分配置"""
    sender.reply("========添加插件积分配置========\n"
                 "请按照以下格式输入插件配置信息:\n"
                 "插件ID,存储桶名,积分键名,显示名称,账号桶名(可选)\n\n"
                 "前4项必填，第5项账号桶名用于CK数量限制(不填则不限制)\n"
                 "示例: zhqd,dd_zhqd,coin,中航签到,zhqd_user\n"
                 "======================\n回复配置信息,退出【q】！")

    config_input = sender.input(120000, 1, False)
    if config_input == 'q':
        sender.reply('已退出')
        return

    try:
        parts = [x.strip() for x in config_input.split(',')]
        if len(parts) < 4:
            sender.reply('配置格式错误!\n请至少输入: 插件ID,存储桶名,积分键名,显示名称')
            return

        plugin_id, bucket, coin_key, name = parts[:4]
        ck_bucket = parts[4] if len(parts) >= 5 else ''
        if not all([plugin_id, bucket, coin_key, name]):
            sender.reply('前4项都不能为空!')
            return

        if _add_plugin_config(plugin_id, bucket, coin_key, name, ck_bucket):
            log_admin_action(userid, "添加插件配置", f"{name}({plugin_id}) ck桶:{ck_bucket or '无'}")
            ck_info = f"\nCK限制桶: {ck_bucket}" if ck_bucket else "\nCK限制: 未设置"
            sender.reply(f"添加成功!\n插件ID: {plugin_id}\n存储桶: {bucket}\n"
                         f"积分键名: {coin_key}\n显示名称: {name}{ck_info}\n\n"
                         f"提示: 新配置已生效,可以通过\"积分查询\"查看")
    except Exception as e:
        sender.reply(f'添加失败: {str(e)}\n请检查输入格式是否正确')


def _admin_ck_limits():
    """管理 - CK限制管理（直接读插件桶，无需插件配合）"""
    sender.reply("========CK限制管理========\n1、查询用户CK限制\n2、设置用户CK上限\n"
                 "3、查询用户某项目CK数\n4、查看已配置CK桶的插件\n"
                 "======================\n回复序号,退出【q】！")
    subchoice = sender.input(120000, 1, False)
    if subchoice == 'q':
        sender.reply('已退出')
        return

    if subchoice == '1':
        sender.reply('请输入用户ID:')
        uid = sender.input(120000, 1, False)
        default_limit = get_user_ck_limit(uid)
        msg = f"=====用户 {uid} CK限制=====\n全局上限: {default_limit if default_limit > 0 else '不限制'}个/项目\n"
        found = False
        for plugin_id, pconfig in PLUGIN_CONFIGS.items():
            ck_bucket = pconfig.get('ck_bucket', '')
            if not ck_bucket:
                continue
            info = get_project_ck_info(uid, plugin_id)
            msg += f"\n📦 {plugin_id}({pconfig.get('name', plugin_id)}): {info['current']}/{info['max'] if info['max'] > 0 else '不限'}个 (桶:{ck_bucket})"
            found = True
        if not found:
            msg += "\n暂无已配置CK桶的插件"
        sender.reply(msg)

    elif subchoice == '2':
        sender.reply('请输入用户ID:')
        uid = sender.input(120000, 1, False)
        cur = get_user_ck_limit(uid)
        sender.reply(f'当前全局上限: {cur if cur > 0 else "不限制"}\n请输入新上限(0=不限制):')
        new_max = _safe_parse_int(sender.input(120000, 1, False))
        if new_max is None: return
        if new_max < 0:
            sender.reply('上限不能为负数!')
            return
        set_user_ck_limit(uid, new_max)
        log_admin_action(userid, "设置CK上限", f"用户{uid} 上限→{new_max if new_max > 0 else '不限制'}")
        sender.reply(f'设置成功! 用户 {uid} CK上限: {new_max if new_max > 0 else "不限制"}个/项目')

    elif subchoice == '3':
        sender.reply('请输入用户ID:')
        uid = sender.input(120000, 1, False)
        sender.reply('请输入项目ID(如 zhqd):')
        pid = sender.input(120000, 1, False)
        info = get_project_ck_info(uid, pid)
        if not info.get('bucket'):
            sender.reply(f'项目 {pid} 未配置CK桶，无法统计!')
        else:
            sender.reply(f"用户 {uid}\n项目 {pid}\n存储桶: {info['bucket']}\n已用: {info['current']}个\n上限: {info['max'] if info['max'] > 0 else '不限制'}个")

    elif subchoice == '4':
        msg = "=====CK桶状态=====\n"
        found = False
        for plugin_id, pconfig in PLUGIN_CONFIGS.items():
            manual = pconfig.get('ck_bucket', None)
            # 获取实际生效的桶（含自动发现）
            actual = _get_plugin_ck_bucket(plugin_id)
            if manual:
                if manual:
                    msg += f"\n📦 {plugin_id}: {pconfig.get('name', plugin_id)} → 桶:{manual} (手动)"
                    found = True
                else:
                    msg += f"\n📦 {plugin_id}: {pconfig.get('name', plugin_id)} → 不限制 (手动关闭)"
                    found = True
            elif actual:
                msg += f"\n📦 {plugin_id}: {pconfig.get('name', plugin_id)} → 桶:{actual} (自动发现)"
                found = True
        if not found:
            msg += "\n暂无CK限制生效的插件"
        msg += "\n\n💡 自动发现无需手动配置，有CK数据即生效"
        msg += "\n手动配置：服务积分设置→编辑插件→设置CK桶"
        sender.reply(msg)
    else:
        sender.reply('输入错误!')


def _admin_card_detail():
    """管理 - 卡密明细查询"""
    sender.reply("========卡密明细查询========\n1、按卡密查询\n2、按用户QQ查询\n"
                 "======================\n回复序号,退出【q】！")
    subchoice = sender.input(120000, 1, False)
    if subchoice == 'q':
        sender.reply('已退出')
        return

    if subchoice == '1':
        sender.reply("请输入要查询的卡密(支持 DD_XXX 格式):")
        card_code = sender.input(120000, 1, False)
        if not card_code:
            return
        result = query_card_detail(card_code)
        sender.reply(result)

    elif subchoice == '2':
        sender.reply("请输入要查询的用户QQ/ID:")
        uid = sender.input(120000, 1, False)
        if not uid:
            return
        result = query_user_cards(uid.strip())
        sender.reply(result)

    else:
        sender.reply('输入错误!')


def _admin_release_lock():
    """管理 - 释放常规支付锁"""
    if middleware.bucketDel(CONFIG_BUCKET, 'recharge_lock'):
        log_admin_action(userid, "释放支付锁", "常规支付锁已释放")
        sender.reply('常规支付锁已释放!')
    else:
        sender.reply('当前没有常规支付锁!')


# ============================================================
# 第十三部分：管理统计面板
# ============================================================

def _admin_stats():
    """管理 - 统计面板"""
    # 用户统计
    all_point_keys = middleware.bucketAllKeys(POINTS_BUCKET)
    total_users = 0
    total_points = 0
    for key in all_point_keys:
        try:
            pts = int(middleware.bucketGet(POINTS_BUCKET, key) or 0)
            if pts > 0:
                total_users += 1
                total_points += pts
        except (ValueError, TypeError):
            continue

    # 今日签到
    today = str(datetime.now().date())
    sign_keys = middleware.bucketAllKeys(SIGN_DATE_BUCKET)
    today_signs = 0
    for key in sign_keys:
        if middleware.bucketGet(SIGN_DATE_BUCKET, key) == today:
            today_signs += 1

    # 卡密统计
    card_keys = middleware.bucketAllKeys(CARD_BUCKET)
    card_unused = 0
    card_used = 0
    card_expired = 0
    total_card_value = 0
    for card in card_keys:
        if not card.startswith('DD_'):
            continue
        card_data = _parse_card_data(middleware.bucketGet(CARD_BUCKET, card))
        if card_data is None:
            continue
        if card_data.get('status') == 'used' or 'user' in card_data:
            card_used += 1
        elif _is_card_expired(card_data):
            card_expired += 1
        else:
            card_unused += 1
            total_card_value += card_data.get('amount', 0)

    # 充值统计
    recharge_keys = middleware.bucketAllKeys(RECHARGE_BUCKET)
    total_recharge_count = 0
    total_recharge_amount = 0
    for key in recharge_keys:
        try:
            data = json.loads(middleware.bucketGet(RECHARGE_BUCKET, key))
            if data.get('status') == 'success':
                total_recharge_count += 1
                total_recharge_amount += float(data.get('amount', 0))
        except (json.JSONDecodeError, KeyError, TypeError):
            continue

    msg = (f"========管理统计面板========\n"
           f"📊 用户统计\n"
           f"  • 有积分用户数: {total_users}\n"
           f"  • 今日签到人数: {today_signs}\n"
           f"\n💰 积分统计\n"
           f"  • 流通积分总量: {total_points:,}\n"
           f"\n🎫 卡密统计\n"
           f"  • 未使用: {card_unused}张 (价值{total_card_value:,}积分)\n"
           f"  • 已使用: {card_used}张\n"
           f"  • 已过期: {card_expired}张\n"
           f"\n💳 充值统计\n"
           f"  • 成功充值: {total_recharge_count}笔\n"
           f"  • 充值总额: ¥{total_recharge_amount:.2f}\n"
           f"============================")
    sender.reply(msg)


# ============================================================
# 第十四部分：管理员操作日志
# ============================================================

def _admin_view_logs():
    """管理 - 查看操作日志"""
    try:
        existing = middleware.bucketGet(ADMIN_LOG_BUCKET, 'logs')
        logs = json.loads(existing) if existing else []
    except (json.JSONDecodeError, TypeError):
        logs = []

    if not logs:
        sender.reply('暂无操作日志!')
        return

    sender.reply(f"========操作日志========\n"
                 f"1、查看最近记录\n"
                 f"2、按管理员筛选\n"
                 f"3、清空日志\n"
                 f"======================\n回复序号,退出【q】！")
    subchoice = sender.input(120000, 1, False)

    if subchoice == 'q':
        return

    if subchoice == '1':
        recent = logs[-20:]
        msg = f'===最近操作日志({len(recent)}/{len(logs)}条)===\n'
        for entry in reversed(recent):
            msg += (f"\n[{entry.get('time', '?')}]\n"
                    f"管理员: {entry.get('admin', '?')}\n"
                    f"操作: {entry.get('action', '?')}\n"
                    f"详情: {entry.get('detail', '?')}\n"
                    f"─────────────────")
        sender.reply(msg)

    elif subchoice == '2':
        sender.reply('请输入管理员ID:')
        admin_id = sender.input(120000, 1, False)
        filtered = [e for e in logs if e.get('admin') == admin_id]
        if not filtered:
            sender.reply(f'未找到管理员 {admin_id} 的操作记录!')
            return
        recent = filtered[-15:]
        msg = f'===管理员{admin_id}的操作({len(recent)}/{len(filtered)}条)===\n'
        for entry in reversed(recent):
            msg += (f"\n[{entry.get('time', '?')}]\n"
                    f"操作: {entry.get('action', '?')}\n"
                    f"详情: {entry.get('detail', '?')}\n"
                    f"─────────────────")
        sender.reply(msg)

    elif subchoice == '3':
        sender.reply('确认清空所有操作日志？回复\"确认\"执行:')
        if sender.input(60000, 1, False) == '确认':
            middleware.bucketSet(ADMIN_LOG_BUCKET, 'logs', '[]')
            log_admin_action(userid, "清空日志", "清空了所有操作日志")
            sender.reply('操作日志已清空!')
        else:
            sender.reply('已取消')


# ============================================================
# 第十五部分：系统设置
# ============================================================

def _admin_system_settings():
    """管理 - 系统设置"""
    global MAKEUP_COST, STREAK_ENABLED

    streak_status = '开启' if STREAK_ENABLED else '关闭'
    msg = (f"========系统设置========\n"
           f"当前配置:\n"
           f"  • 补签费用: {'自动(签到上限x2)' if MAKEUP_COST == 0 else f'{MAKEUP_COST}积分'}\n"
           f"  • 连续签到加成: {streak_status}\n")

    if STREAK_ENABLED:
        for days, mult in sorted(STREAK_TIERS.items()):
            msg += f"    - {days}天: {mult}倍\n"

    msg += (f"\n1、设置补签费用\n"
            f"2、{'关闭' if STREAK_ENABLED else '开启'}连续签到加成\n"
            f"======================\n回复序号,退出【q】！")
    sender.reply(msg)

    subchoice = sender.input(120000, 1, False)

    if subchoice == '1':
        sender.reply('请输入补签费用(积分, 0=自动计算为签到上限x2):')
        cost = _safe_parse_int(sender.input(120000, 1, False))
        if cost is None: return
        if cost < 0:
            sender.reply('费用不能为负数!')
            return
        middleware.bucketSet(CONFIG_BUCKET, 'makeup_cost', str(cost))
        MAKEUP_COST = cost
        log_admin_action(userid, "设置补签费用", f"{'自动' if cost == 0 else f'{cost}积分'}")
        sender.reply(f'设置成功! 补签费用: {"自动(签到上限x2)" if cost == 0 else f"{cost}积分"}')

    elif subchoice == '2':
        new_val = 'false' if STREAK_ENABLED else 'true'
        middleware.bucketSet(CONFIG_BUCKET, 'streak_enabled', new_val)
        STREAK_ENABLED = new_val == 'true'
        log_admin_action(userid, "连续签到加成", f"{'开启' if STREAK_ENABLED else '关闭'}")
        sender.reply(f'连续签到加成已{"开启" if STREAK_ENABLED else "关闭"}!')


# ============================================================
# 第十六部分：系统管理入口
# ============================================================

ADMIN_HANDLERS = {
    '1': _admin_generate_cards,
    '2': _admin_view_cards,
    '3': _admin_delete_card,
    '4': _admin_points_manage,
    '5': None,  # 充值管理，需特殊处理
    '6': _admin_payment_config,
    '7': _admin_service_points,
    '8': _admin_add_plugin_config,
    '9': _admin_release_lock,
    '10': _admin_cleanup_expired,
    '11': _admin_stats,
    '12': _admin_view_logs,
    '13': _admin_system_settings,
    '14': _admin_ck_limits,
    '15': _admin_card_detail,
}


def system():
    """系统管理入口"""
    if not sender.isAdmin():
        sender.reply('您没有权限!')
        return

    sender.reply("========系统管理========\n"
                 "1、生成卡密\n2、查看卡密\n3、删除卡密\n4、积分管理\n"
                 "5、充值管理\n6、支付配置\n7、服务积分设置\n8、添加插件积分配置\n"
                 "9、释放常规支付锁\n"
                 "--- 扩展功能 ---\n"
                 "10、清理过期卡密\n11、管理统计\n12、操作日志\n13、系统设置\n"
                 "14、CK限制管理\n15、卡密明细查询\n"
                 "======================\n回复序号,退出【q】！")
    choice = sender.input(120000, 1, False)

    if choice == 'q':
        sender.reply('已退出')
        return

    if choice == '5':
        handle_recharge()
        return

    handler = ADMIN_HANDLERS.get(choice)
    if handler:
        handler()
    else:
        sender.reply('输入错误!')


# ============================================================
# 第十七部分：常规支付（赞赏码 / 收款码）
# ============================================================

def _parse_pay_result(ddzf: dict) -> tuple:
    try:
        if ddzf.get('Type') in ('微信赞赏', '微信收款'):
            paid_amount = float(ddzf.get('Money', 0))
            pay_time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
            payer_name = ddzf.get('FromName', '')
        elif ddzf.get('Money'):
            paid_amount = float(ddzf.get('Money', 0))
            pay_time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
            payer_name = ddzf.get('FromName', '')
        elif ddzf.get('money'):
            paid_amount = float(ddzf.get('money', 0))
            pay_time = ddzf.get('time', '').replace('T', ' ').split('.')[0]
            payer_name = ddzf.get('fromName', '')
        else:
            return None

        if not pay_time:
            pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if paid_amount <= 0:
            return None
        return paid_amount, pay_time, payer_name
    except (ValueError, TypeError):
        return None


def recharge():
    """充值积分 - 常规支付（使用支付锁）"""
    if not PAYMENT_CONFIG['zsm']:
        sender.reply('未配置赞赏码,请联系管理员!')
        return

    pay_lock_key = 'recharge_lock'
    lock_info = middleware.bucketGet(CONFIG_BUCKET, pay_lock_key)
    if lock_info:
        try:
            lock_data = json.loads(lock_info)
            if time.time() - lock_data['time'] < 120:
                sender.reply('当前有其他用户正在支付中，请稍后再试!')
                return
        except (json.JSONDecodeError, KeyError):
            pass

    lock_data = {'user': userid, 'time': int(time.time())}
    middleware.bucketSet(CONFIG_BUCKET, pay_lock_key, json.dumps(lock_data))

    rate = _get_rate()
    current = get_user_points(userid)
    sender.reply(f"========充值积分========\n当前积分: {current}🌸\n"
                 f"兑换比例: 1元 = {rate}积分\n======================")
    sender.replyImage(PAYMENT_CONFIG['zsm'])

    ddzf = sender.waitPay("q", 100 * 1000)

    try:
        if not ddzf or str(ddzf) == 'q':
            sender.reply('已取消支付')
            return

        try:
            if isinstance(ddzf, str):
                ddzf = json.loads(ddzf)
        except json.JSONDecodeError:
            sender.reply('支付结果解析失败，如果您已完成支付，请联系管理员')
            return

        result = _parse_pay_result(ddzf)
        if result is None:
            sender.reply('不支持的支付消息格式或金额无效')
            return

        paid_amount, pay_time, payer_name = result
        points = int(paid_amount * rate)
        recharge_id = f"R_{int(time.time())}_{userid}"

        add_user_points(userid, points, "充值", username)
        middleware.bucketSet(RECHARGE_BUCKET, recharge_id, json.dumps({
            'user': userid, 'amount': paid_amount, 'points': points,
            'paid_amount': paid_amount, 'time': int(time.time()),
            'pay_time': pay_time, 'payer_name': payer_name, 'status': 'success'
        }))

        msg = (f"=====充值成功=====\n订单号: {recharge_id}\n充值金额: {paid_amount}元\n"
               f"获得积分: {points}\n当前积分: {get_user_points(userid)}\n支付时间: {pay_time}")
        if payer_name:
            msg += f"\n支付用户: {payer_name}"
        sender.reply(msg)

    except Exception as e:
        sender.reply("处理支付结果时出错，如果您已完成支付，请联系管理员")
        print(f"支付处理错误: {str(e)}")
    finally:
        middleware.bucketDel(CONFIG_BUCKET, pay_lock_key)


def send_payment_message(amount):
    sender.reply(json.dumps({"type": "pay", "data": {"price": amount, "title": "积分充值", "payType": "wechat"}}))
    sender.reply(json.dumps({"type": "wxpay", "data": {"amount": amount, "desc": "积分充值"}}))
    sender.reply("请扫码赞赏,完成后发送赞赏金额:")
    sender.reply(PAYMENT_CONFIG['zsm'])


def check_recharge(recharge_id: str) -> str:
    data = middleware.bucketGet(RECHARGE_BUCKET, recharge_id)
    if not data:
        return '订单不存在'
    try:
        data = json.loads(data)
        status = {'pending': '待审核', 'success': '已完成', 'failed': '已取消'}.get(data['status'], '未知')
        return (f"充值详情:\n订单号: {recharge_id}\n充值金额: {data['amount']}元\n"
                f"可得积分: {data['points']}\n状态: {status}")
    except (json.JSONDecodeError, KeyError):
        return '查询失败'


def handle_recharge():
    """管理 - 充值管理（审核订单）"""
    if not sender.isAdmin():
        sender.reply('您没有权限!')
        return

    sender.reply("========充值管理========\n1、查看待审核\n2、审核通过\n"
                 "3、取消订单\n======================\n回复序号,退出【q】！")
    choice = sender.input(120000, 1, False)

    if choice == 'q':
        sender.reply('已退出')
        return

    if choice == '1':
        pending = []
        for key in middleware.bucketAllKeys(RECHARGE_BUCKET):
            try:
                data = json.loads(middleware.bucketGet(RECHARGE_BUCKET, key))
                if data['status'] == 'pending':
                    pending.append((key, data))
            except (json.JSONDecodeError, KeyError):
                continue

        if not pending:
            sender.reply('暂无待审核订单!')
            return

        msg = '========待审核========\n'
        for recharge_id, data in pending:
            msg += f"订单号: {recharge_id}\n用户: {data['user']}\n金额: {data['amount']}元\n积分: {data['points']}\n"
        sender.reply(msg)

    elif choice == '2':
        sender.reply('请输入订单号:')
        recharge_id = sender.input(120000, 1, False)
        try:
            data = json.loads(middleware.bucketGet(RECHARGE_BUCKET, recharge_id))
            if data['status'] != 'pending':
                sender.reply('订单状态错误!')
                return
            data['status'] = 'success'
            middleware.bucketSet(RECHARGE_BUCKET, recharge_id, json.dumps(data))
            add_user_points(data['user'], data['points'], "充值审核", "")
            log_admin_action(userid, "审核充值", f"订单{recharge_id}通过,{data['amount']}元")
            sender.reply('审核通过!')
            middleware.push('wx', '', data['user'], '',
                           f"充值成功!\n订单号: {recharge_id}\n充值金额: {data['amount']}元\n"
                           f"获得积分: {data['points']}\n当前积分: {get_user_points(data['user'])}")
        except (json.JSONDecodeError, KeyError):
            sender.reply('操作失败!')

    elif choice == '3':
        sender.reply('请输入订单号:')
        recharge_id = sender.input(120000, 1, False)
        try:
            data = json.loads(middleware.bucketGet(RECHARGE_BUCKET, recharge_id))
            if data['status'] != 'pending':
                sender.reply('订单状态错误!')
                return
            data['status'] = 'failed'
            middleware.bucketSet(RECHARGE_BUCKET, recharge_id, json.dumps(data))
            log_admin_action(userid, "取消充值", f"订单{recharge_id}取消")
            sender.reply('已取消订单!')
            middleware.push('wx', '', data['user'], '',
                           f"充值已取消!\n订单号: {recharge_id}\n充值金额: {data['amount']}元")
        except (json.JSONDecodeError, KeyError):
            sender.reply('操作失败!')
    else:
        sender.reply('输入错误!')


# ============================================================
# 第十八部分：易支付（EPay）
# ============================================================

def _build_epay_sign(params_dict: dict, key: str, exclude_keys=('sign', 'sign_type')) -> str:
    """构建易支付签名"""
    filtered = {k: v for k, v in params_dict.items() if k not in exclude_keys and v != ''}
    sorted_items = sorted(filtered.items(), key=lambda x: x[0])
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_items])
    return hashlib.md5((sign_str + key).encode('utf-8')).hexdigest().lower()


def _create_epay_qr(out_trade_no: str, channel: str, project_name: str, money_str: str) -> tuple:
    """创建易支付二维码，返回(二维码图片URL, 订单号)"""
    base_params = {
        'pid': str(EPAY_CONFIG['epay_pid']).strip(),
        'type': channel,
        'out_trade_no': out_trade_no,
        'name': project_name,
        'money': money_str,
        'notify_url': 'http://127.0.0.1/',
        'return_url': 'http://127.0.0.1/'
    }
    submit_sign = _build_epay_sign(base_params, EPAY_CONFIG['epay_key'])
    submit_params = dict(base_params)
    submit_params['sign'] = submit_sign
    submit_params['sign_type'] = 'MD5'

    qr_image_url = None
    try:
        mapi_params = dict(base_params)
        mapi_params['clientip'] = '127.0.0.1'
        mapi_sign = _build_epay_sign(mapi_params, EPAY_CONFIG['epay_key'])
        mapi_params['sign'] = mapi_sign
        mapi_params['sign_type'] = 'MD5'

        mapi_url = EPAY_CONFIG['epay_url'].rstrip('/') + '/mapi.php'
        resp = requests.post(mapi_url, data=mapi_params, timeout=15, verify=False)
        data = resp.json()
        if int(data.get('code', 0)) == 1:
            native_qr = data.get('qrcode', '') or data.get('payurl', '') or data.get('urlscheme', '')
            if native_qr:
                qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(native_qr, safe='')}"
    except Exception as e:
        print(f"易支付mapi异常: {e}")

    if not qr_image_url:
        raw_query = '&'.join(f'{k}={v}' for k, v in submit_params.items())
        pay_url = EPAY_CONFIG['epay_url'].rstrip('/') + '/submit.php?' + raw_query
        qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={quote(pay_url, safe='')}"

    return qr_image_url, out_trade_no


def epay_recharge() -> bool:
    """易支付充值积分流程，返回True表示已处理(含取消)，False表示回退到常规支付"""
    if not (EPAY_CONFIG['epay_url'] and EPAY_CONFIG['epay_pid'] and EPAY_CONFIG['epay_key']):
        sender.reply('易支付配置不完整，请联系管理员!')
        return False

    try:
        rate = _get_rate()
        sender.reply(f"\n积分比例：1元 = {rate}积分\n请输入要充值的金额(元)，输入q退出:")
        amount_str = sender.input(120000, 1, False)

        if not amount_str or amount_str.lower() == 'q':
            sender.reply('已取消充值')
            return True

        try:
            amount = float(amount_str)
            if amount <= 0:
                sender.reply('充值金额必须大于0')
                return True
        except ValueError:
            sender.reply('请输入有效的金额')
            return True

        amount = round(amount, 2)

        # 收集可用的支付通道
        channels = []
        if EPAY_CONFIG['epay_alipay']:
            channels.append(('alipay', '支付宝'))
        if EPAY_CONFIG['epay_wxpay']:
            channels.append(('wxpay', '微信支付'))
        if EPAY_CONFIG['epay_qqpay']:
            channels.append(('qqpay', 'QQ钱包'))

        if not channels:
            sender.reply('没有可用的支付通道，请联系管理员!')
            return False

        current_points = get_user_points(userid)
        will_get_points = int(amount * rate)

        if len(channels) == 1:
            selected_channel, selected_name = channels[0]
        else:
            channel_options = "\n".join([f"{i+1}. {name}" for i, (_, name) in enumerate(channels)])
            sender.reply(f"===== 充值信息 =====\n当前积分: {current_points}\n充值金额: {amount}元\n"
                         f"获得积分: {will_get_points}\n充值后总积分: {current_points + will_get_points}\n"
                         f"=======================\n请选择支付方式:\n{channel_options}\n\n"
                         f"请回复对应序号(1-{len(channels)})，或输入q取消:")

            choice = sender.input(120000, 1, False)
            if not choice or choice.lower() == 'q':
                sender.reply('已取消充值')
                return True
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(channels):
                    selected_channel, selected_name = channels[choice_idx]
                else:
                    sender.reply('选择无效，已取消充值')
                    return True
            except ValueError:
                sender.reply('输入无效，已取消充值')
                return True

        # 创建订单
        out_trade_no = f"KMXT_{int(time.time())}_{userid}_{random.randint(1000, 9999)}"
        formatted_money = f"{amount:.2f}"

        qr_image_url, _ = _create_epay_qr(out_trade_no, selected_channel, f"积分充值-{amount}元", formatted_money)

        sender.reply(f"=====等待支付=====\n💰 金额: {formatted_money}元\n💳 方式: {selected_name}\n"
                     f"📋 订单: {out_trade_no}\n获得积分: {will_get_points}\n"
                     f"------------------\n请在 180 秒内完成扫码支付\n回复\"q\"取消支付")
        sender.replyImage(qr_image_url)

        # 轮询支付状态
        start_time = time.time()
        paid = False
        query_url = f"{EPAY_CONFIG['epay_url'].rstrip('/')}/api.php?act=order&pid={EPAY_CONFIG['epay_pid']}&key={EPAY_CONFIG['epay_key']}&out_trade_no={out_trade_no}"

        while time.time() - start_time < 180:
            try:
                res = requests.get(query_url, timeout=5).json()
                if str(res.get('code')) == '1' and str(res.get('status')) == '1':
                    paid = True
                    break
            except Exception:
                pass

            cancel_check = sender.listen(3000)
            if cancel_check and str(cancel_check).strip().lower() == 'q':
                sender.reply('已取消支付')
                return True

        if paid:
            points = int(amount * rate)
            add_user_points(userid, points, "易支付充值", username)

            recharge_id = f"KMXT_{int(time.time())}_{userid}"
            middleware.bucketSet(RECHARGE_BUCKET, recharge_id, json.dumps({
                'user': userid, 'amount': amount, 'points': points,
                'paid_amount': amount, 'time': int(time.time()),
                'pay_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'success'
            }))

            sender.reply(f"=====充值成功=====\n订单号: {out_trade_no}\n充值金额: {amount}元\n"
                         f"获得积分: {points}\n当前积分: {get_user_points(userid)}\n================")
        else:
            sender.reply("支付超时，请重新发起充值。")

        return True

    except Exception as e:
        sender.reply(f'易支付充值异常: {str(e)}')
        return True


def _handle_recharge_menu():
    """充值积分入口：收集所有启用的支付方式，单个直接进，多个弹菜单选择"""
    pay_methods = []

    # 易支付：开关开启 + 三要素齐全
    epay_ready = (EPAY_CONFIG.get('epay_switch', 'false').lower() == 'true'
                  and EPAY_CONFIG.get('epay_url') and EPAY_CONFIG.get('epay_pid') and EPAY_CONFIG.get('epay_key'))
    if epay_ready:
        pay_methods.append(('epay', '易支付（支付宝/微信/QQ）'))

    # 码支付：开关开启 + 三要素齐全
    mapay_ready = (PAYMENT_CONFIG.get('ma_pay_switch', 'false').lower() == 'true'
                   and PAYMENT_CONFIG.get('ma_pay_gateway') and PAYMENT_CONFIG.get('ma_pay_pid') and PAYMENT_CONFIG.get('ma_pay_key'))
    if mapay_ready:
        pay_methods.append(('mapay', '码支付（支付宝/微信/QQ）'))

    # 微信收款码：开关开启 + 收款码已配置
    wechat_qr_ready = WECHAT_QR_SWITCH and bool(PAYMENT_CONFIG.get('zsm'))
    if wechat_qr_ready:
        pay_methods.append(('wechat_qr', '微信收款码'))

    if not pay_methods:
        sender.reply('暂无可用的支付方式，请联系管理员!')
        return

    if len(pay_methods) == 1:
        method_type = pay_methods[0][0]
    else:
        menu = "=====选择支付方式====="
        for i, (mtype, mname) in enumerate(pay_methods, 1):
            menu += f"\n{i}. {mname}"
        menu += "\n===================\n回复序号选择，q退出"
        sender.reply(menu)

        choice = sender.input(120000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply('已取消充值')
            return

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(pay_methods):
                method_type = pay_methods[idx][0]
            else:
                sender.reply('选择无效，已取消')
                return
        except ValueError:
            sender.reply('输入无效，已取消')
            return

    # 根据选择执行对应支付流程
    if method_type == 'epay':
        if not epay_recharge():
            if mapay_ready:
                if not ma_pay_recharge():
                    recharge()
            elif wechat_qr_ready:
                recharge()
            else:
                recharge()
    elif method_type == 'mapay':
        if not ma_pay_recharge():
            if wechat_qr_ready:
                recharge()
            else:
                recharge()
    elif method_type == 'wechat_qr':
        recharge()


# ============================================================
# 第十九部分：码支付（MaPay）
# ============================================================

class MaPayApi:

    def __init__(self, config: dict):
        self.config = config

    def _sign_params(self, params: dict) -> str:
        sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        return calculate_md5(sign_str + self.config['key']).lower()

    def create_payment(self, amount, out_trade_no: str, name: str,
                       user_id: str, pay_type: str = None, sitename: str = "") -> tuple:
        try:
            if pay_type is None:
                pay_types = [p.strip() for p in self.config.get('ma_pay_type', self.config.get('pay_type', '')).split(',') if p.strip()]
                pay_type = pay_types[0] if pay_types else "alipay"

            params = {
                'pid': self.config['pid'],
                'type': pay_type,
                'out_trade_no': out_trade_no,
                'name': name,
                'money': str(amount),
                'sitename': sitename,
                'param': user_id,
            }
            if self.config.get('ma_pay_notify_url'):
                params['notify_url'] = self.config['ma_pay_notify_url']

            params = {k: v for k, v in params.items() if v}
            params['sign'] = self._sign_params(params)
            params['sign_type'] = 'MD5'

            mapi_url = self.config['gateway'].rstrip('/') + '/mapi.php'
            response = requests.post(mapi_url, data=params,
                                     headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10)

            if response.status_code != 200:
                return False, None, f"创建支付订单失败，HTTP状态码: {response.status_code}"

            try:
                result = response.json()
            except (json.JSONDecodeError, ValueError):
                return False, None, "创建支付订单失败，返回数据格式错误"

            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')
            if code == 1:
                return True, result, msg
            return False, None, msg

        except Exception as e:
            return False, None, f"创建订单失败: {str(e)}"

    def query_order(self, out_trade_no: str = None, trade_no: str = None) -> tuple:
        try:
            query_url = self.config['gateway'].rstrip('/')
            if '/xpay/epay/api.php' not in query_url:
                query_url = f"{query_url}/xpay/epay/api.php"

            params = {"act": "order", "pid": self.config['pid'], "key": self.config['key']}
            if trade_no:
                params["trade_no"] = trade_no
            elif out_trade_no:
                params["out_trade_no"] = out_trade_no
            else:
                return False, None, "必须提供商户订单号或系统订单号"

            print(f"查询订单URL: {query_url}")
            print(f"查询参数: {params}")

            response = requests.get(query_url, params=params, timeout=10)
            print(f"响应状态码: {response.status_code}")

            if response.status_code != 200:
                return False, None, f"查询订单失败，HTTP状态码: {response.status_code}"

            try:
                result = response.json()
            except (json.JSONDecodeError, ValueError):
                return False, None, f"查询订单失败，返回数据格式错误: {response.text[:200]}"

            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')
            if code == 1:
                if result.get('status') == 1:
                    return True, result, "支付成功"
                return True, result, "订单未支付"
            return False, None, msg

        except Exception as e:
            return False, None, f"查询订单异常: {str(e)}"


def _poll_mapi_payment_status(out_trade_no: str, max_tries: int = 30) -> tuple:
    ma_pay_api = MaPayApi(PAYMENT_CONFIG)

    for _ in range(max_tries):
        try:
            success, data, msg = ma_pay_api.query_order(out_trade_no=out_trade_no)
            if success and isinstance(data, dict) and data.get('status') == 1:
                return True, "支付成功", data

            result = sender.listen(5000)
            if result == 'q':
                return False, "用户取消查询", None
        except Exception as e:
            print(f"查询订单状态出错: {str(e)}")

    return False, "查询超时，订单可能尚未支付", None


def ma_pay_recharge() -> bool:
    if not (PAYMENT_CONFIG['ma_pay_gateway'] and PAYMENT_CONFIG['ma_pay_pid'] and PAYMENT_CONFIG['ma_pay_key']):
        sender.reply('码支付配置不完整，请联系管理员!')
        return False

    PAYMENT_CONFIG['pid'] = PAYMENT_CONFIG['ma_pay_pid']
    PAYMENT_CONFIG['key'] = PAYMENT_CONFIG['ma_pay_key']
    PAYMENT_CONFIG['gateway'] = PAYMENT_CONFIG['ma_pay_gateway']

    try:
        rate = _get_rate()

        sender.reply(f"\n积分比例：1元 = {rate}积分\n请输入要充值的金额(元)，输入q退出:")
        amount_str = sender.input(120000, 1, False)

        if amount_str.lower() == 'q':
            sender.reply('已取消充值')
            return True

        try:
            amount = float(amount_str)
            if amount <= 0:
                sender.reply('充值金额必须大于0')
                return True
        except ValueError:
            sender.reply('请输入有效的金额')
            return True

        amount = round(amount, 2)
        out_trade_no = f"MP{int(time.time())}{userid}"

        pay_types_str = PAYMENT_CONFIG['ma_pay_type'].strip() or "alipay,wxpay,qqpay"
        pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]

        current_points = get_user_points(userid)
        will_get_points = int(amount * rate)
        total_after = current_points + will_get_points

        if len(pay_types) == 1:
            selected_type = pay_types[0]
            sender.reply(f"===== 充值信息 =====\n当前积分: {current_points}\n"
                         f"充值金额: {amount}元\n充值后总积分: {total_after}")
        else:
            pay_options_text = "\n".join([f"{i+1}. {PAY_TYPE_NAMES.get(t, t)}" for i, t in enumerate(pay_types)])
            sender.reply(f"===== 充值信息 =====\n当前积分: {current_points}\n充值积分: {will_get_points}\n"
                         f"充值后总积分: {total_after}\n=======================\n请选择支付方式:\n"
                         f"{pay_options_text}\n\n请回复对应序号(1-{len(pay_types)})，或输入q取消:")

            choice = sender.input(120000, 1, False)
            if choice.lower() == 'q':
                sender.reply('已取消充值')
                return True
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(pay_types):
                    selected_type = pay_types[choice_idx]
                else:
                    sender.reply('选择无效，已取消充值')
                    return True
            except ValueError:
                sender.reply('输入无效，已取消充值')
                return True

        print(f"当前配置信息：\ngateway: {PAYMENT_CONFIG['gateway']}\npid: {PAYMENT_CONFIG['pid']}\n"
              f"key: {PAYMENT_CONFIG['key'][:4]}****\npay_type: {selected_type}\n"
              f"使用查询订单状态判断支付结果（不依赖回调）")

        ma_pay_api = MaPayApi(PAYMENT_CONFIG)
        try:
            success, result, msg = ma_pay_api.create_payment(
                amount=amount, out_trade_no=out_trade_no,
                name=f"{senderID}-积分充值-{str(amount)}",
                user_id=userid, pay_type=selected_type)
        except Exception as e:
            sender.reply(f'创建订单时出错: {str(e)}')
            return True

        if not success:
            if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                sender.reply(f'码支付暂不可用({msg})，切换到默认收款方式')
                return False
            sender.reply(f'创建订单失败: {msg}')
            return True

        payurl = result.get('payurl', '')
        if not payurl:
            sender.reply('获取支付链接失败')
            return True

        selected_type_name = PAY_TYPE_NAMES.get(selected_type, selected_type)
        qrcode_api_url = generate_qrcode(payurl)
        if qrcode_api_url:
            extra = '\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！' if selected_type == "qqpay" else ''
            sender.reply(f'请使用【{selected_type_name}】扫描下方二维码完成支付，'
                         f'支付过程中输入"q"可取消支付:{extra}\n[CQ:image,file={qrcode_api_url}]')
        else:
            sender.reply(f"二维码生成失败，请使用【{selected_type_name}】打开链接：\n{payurl}")

        is_paid, msg, data = _poll_mapi_payment_status(out_trade_no)

        if is_paid:
            points = int(amount * rate)
            add_user_points(userid, points, "码支付充值", username)

            recharge_id = f"MP_{int(time.time())}_{userid}"
            middleware.bucketSet(RECHARGE_BUCKET, recharge_id, json.dumps({
                'user': userid, 'amount': amount, 'points': points,
                'paid_amount': amount, 'time': int(time.time()),
                'pay_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'success'
            }))

            sender.reply(f"=====充值成功=====\n订单号: {out_trade_no}\n充值金额: {amount}元\n"
                         f"获得积分: {points}\n当前积分: {get_user_points(userid)}\n================")
        else:
            sender.reply(f"支付未完成: {msg}")

        return True

    except Exception as e:
        sender.reply(f'创建订单失败: {str(e)}')
        return True


# ============================================================
# 第二十部分：初始化 & 主逻辑入口
# ============================================================

# 加载自定义插件配置
try:
    _custom_plugins = json.loads(middleware.bucketGet(CONFIG_BUCKET, 'custom_plugins') or '{}')
    PLUGIN_CONFIGS.update(_custom_plugins)
except Exception:
    pass

# --- 消息路由 ---
message = sender.getMessage()

if message == '签到' and signswitch == 'true':
    sign()

elif message == '卡密系统管理':
    system()

elif message in ('积分查询', '查询积分'):
    query_points()

elif message in ('积分明细', '积分流水'):
    query_transaction_log()

elif message == '补签':
    makeup_sign()

elif 'DD_' in message:
    success, msg = use_card(message)
    sender.reply(msg)

elif imtype == 'fake':
    for key in middleware.bucketAllKeys('dd_state'):
        middleware.bucketDel('dd_state', key)

elif message in ('充值积分', '积分充值'):
    _handle_recharge_menu()

elif message.startswith('R_') or message.startswith('KMXT_'):
    msg = check_recharge(message)
    sender.reply(msg)

else:
    sender.setContinue()
