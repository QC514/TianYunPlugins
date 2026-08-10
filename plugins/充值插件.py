#[title: 充值插件]
#[language: python]
#[class: 工具类]
#[service: 2993959969] 售后联系方式
#[author: rujingxianghai] 作者
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^(充值|充币|购买白名单|甬派充值|甬派车位充值|进白名单群)$] 匹配规则
#[cron: 0 0 0 0 0] cron定时
#[priority: 99999] 优先级
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]
#[icon: ]
#[version: 1.1.0]
#[public: true]
#[price: 88.88]
#[description: 码支付充值积分，购买白名单插件<br>1.1.0：重构码支付，统一走vorto_utils]

# [param: {"required":true,"key":"s_recharge.whitelist_price","bool":false,"placeholder":"10","name":"白名单价格","desc":"购买白名单的价格(元)"}]
# [param: {"required":true,"key":"s_recharge.whitelist_count","bool":false,"placeholder":"100","name":"白名单数量","desc":"白名单最大数量"}]

import time
import json
import random
import requests
from datetime import datetime
import middleware
import vorto_utils

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

WHITELIST_CONFIG = {
    'price': float(middleware.bucketGet('s_recharge', 'whitelist_price') or '10'),
    'count': int(middleware.bucketGet('s_recharge', 'whitelist_count') or '100')
}

YP_PARKING_CONFIG = {
    'price_per_use': 1.50,
    'api_url': 'https://ypapi.vzvv.de'
}


# ==================== Common Payment Flow ====================

def _select_and_pay(project, amount, order_prefix):
    """Unified MaPay payment: select type -> create order -> poll result.
    Returns True if paid, False otherwise.
    """
    pay_config = vorto_utils.get_pay_config()
    if not pay_config['ma_pay_switch']:
        sender.reply("❌ 码支付未开启，请联系管理员在Vorto初始化中开启")
        return False

    pay_types = pay_config['pay_types']
    if not pay_types:
        sender.reply("❌ 未配置码支付方式，请联系管理员在Vorto初始化中填写")
        return False

    # Select payment type
    type_list = list(pay_types.items())
    if len(type_list) == 1:
        selected_key, selected_name = type_list[0]
    else:
        options = "\n".join([f"[{i+1}] {name}" for i, (_, name) in enumerate(type_list)])
        sender.reply(
            f"=====选择支付方式=====\n"
            f"💰 金额: {amount}元\n"
            f"------------------------\n"
            f"{options}\n"
            f"------------------------\n"
            f"回复数字选择，输入q取消"
        )
        choice = sender.input(60000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply("✅ 已取消")
            return False
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(type_list):
                selected_key, selected_name = type_list[idx]
            else:
                sender.reply("❌ 选择无效")
                return False
        except ValueError:
            sender.reply("❌ 输入无效")
            return False

    # Create order via MaPayClient
    out_trade_no = f"{order_prefix}{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"

    sender.reply(
        f"=====码支付信息=====\n"
        f"🎫 商品: {project}\n"
        f"💰 金额: {amount}元\n"
        f"💳 方式: {selected_name}\n"
        f"=================="
    )

    try:
        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(amount), selected_key, out_trade_no, f"{project}-{amount}", userid)

        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False

        pay_url = order.get('pay_url')
        qr_url = vorto_utils.generate_qrcode_url(pay_url)
        sender.replyImage(qr_url)
        sender.reply(f'💳 请使用【{selected_name}】扫码支付\n⏰ 5分钟内完成支付\n输入"q"可取消')

        start_time = time.time()
        timeout = 300

        while time.time() - start_time < timeout:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                sender.reply("✅ 支付成功！")
                return True

        sender.reply("❌ 支付超时")
        return False

    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False


# ==================== Coin & Whitelist Helpers ====================

def get_user_coins(username):
    """Get user's current coins"""
    coins = middleware.bucketGet('autMarketCoins', username)
    return int(coins) if coins else 0


def add_user_coins(username, amount):
    """Add coins to user"""
    current = get_user_coins(username)
    new_amount = current + amount
    middleware.bucketSet('autMarketCoins', username, str(new_amount))
    return new_amount


def get_whitelist():
    """Get whitelist"""
    testers = middleware.bucketGet('autMarketCfgs', 'testers') or ''
    return [name.strip() for name in testers.split(',') if name.strip()]


def add_to_whitelist(username):
    """Add user to whitelist"""
    testers = get_whitelist()
    if username not in testers:
        testers.append(username)
        middleware.bucketSet('autMarketCfgs', 'testers', ','.join(testers))
    return testers


# ==================== Parking Helpers ====================

def get_user_parking_usage(username):
    """Get user's remaining parking uses"""
    try:
        url = f"{YP_PARKING_CONFIG['api_url']}/dd_vip_info"
        response = requests.post(url, json={'username': username}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return result.get('data', {}).get('remaining_uses', 30)
        return 30
    except:
        return 30


def update_user_parking_usage(username, count):
    """Update user's parking uses"""
    try:
        url = f"{YP_PARKING_CONFIG['api_url']}/dd_vip_add"
        response = requests.post(url, json={'username': username, 'count': count}, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return True, result.get('data', {}).get('updated_uses', 30)
        return False, 30
    except:
        return False, 30


# ==================== Business Logic ====================

def handle_recharge():
    """Handle coin recharge"""
    sender.reply('请输入您的autman用户名:')
    autman_username = sender.input(60000, 1, False)
    if not autman_username:
        sender.reply('❌ 用户名不能为空')
        return

    sender.reply('请输入充值金额(元):')
    amount_str = sender.input(60000, 1, False)
    try:
        amount = round(float(amount_str), 2)
        if amount <= 0:
            sender.reply('❌ 充值金额必须大于0')
            return
    except ValueError:
        sender.reply('❌ 请输入有效的金额')
        return

    current_coins = get_user_coins(autman_username)
    will_get_coins = int(amount * 100)

    sender.reply(
        f"=====充值信息=====\n"
        f"用户名: {autman_username}\n"
        f"当前积分: {current_coins}\n"
        f"充值积分: {will_get_coins}\n"
        f"=================="
    )

    out_trade_no = f"AUT{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"

    if _select_and_pay(f"{autman_username}-积分充值-{will_get_coins}", amount, "AUT"):
        new_coins = add_user_coins(autman_username, will_get_coins)
        middleware.bucketSet('s_recharge_orders', out_trade_no, json.dumps({
            'user': userid,
            'autman_username': autman_username,
            'amount': amount,
            'coins': will_get_coins,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'success'
        }))
        sender.reply(
            f"=====充值成功=====\n"
            f"订单号: {out_trade_no}\n"
            f"用户名: {autman_username}\n"
            f"当前积分: {new_coins}\n"
            f"=================="
        )


def handle_whitelist_purchase():
    """Handle whitelist purchase"""
    current_testers = get_whitelist()
    if len(current_testers) >= WHITELIST_CONFIG['count']:
        sender.reply(f"❌ 白名单已满 {len(current_testers)}/{WHITELIST_CONFIG['count']}")
        return

    sender.reply('请输入您的autman用户名:')
    autman_username = sender.input(60000, 1, False)
    if not autman_username:
        sender.reply('❌ 用户名不能为空')
        return

    if autman_username in current_testers:
        sender.reply('您已在白名单中!')
        return

    price = WHITELIST_CONFIG['price']
    sender.reply(
        f"=====购买白名单=====\n"
        f"用户名: {autman_username}\n"
        f"白名单: {len(current_testers)}/{WHITELIST_CONFIG['count']}\n"
        f"价格: {price}元\n"
        f"=================="
    )

    out_trade_no = f"WL{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"

    if _select_and_pay(f"{autman_username}-购买白名单", price, "WL"):
        add_to_whitelist(autman_username)
        middleware.bucketSet('s_whitelist_orders', out_trade_no, json.dumps({
            'user': userid,
            'autman_username': autman_username,
            'amount': price,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'success'
        }))
        sender.reply(
            f"=====购买成功=====\n"
            f"订单号: {out_trade_no}\n"
            f"用户名: {autman_username}\n"
            f"请私聊管理员进入白名单群！\n"
            f"=================="
        )


def handle_yongpai_parking_recharge():
    """Handle parking recharge"""
    sender.reply(f'当前甬派车位价格：{YP_PARKING_CONFIG["price_per_use"]}/个\n请输入您的卡密:')
    autman_username = sender.input(60000, 1, False)
    if not autman_username:
        sender.reply('❌ 用户名不能为空')
        return

    current_usage = get_user_parking_usage(autman_username)

    sender.reply('请输入需要充值的次数:')
    count_str = sender.input(60000, 1, False)
    try:
        count = int(count_str)
        if count <= 0:
            sender.reply('❌ 充值次数必须大于0')
            return
    except ValueError:
        sender.reply('❌ 请输入有效的次数')
        return

    amount = round(count * YP_PARKING_CONFIG['price_per_use'], 2)

    sender.reply(
        f"=====甬派车位充值=====\n"
        f"用户名: {autman_username}\n"
        f"当前剩余: {current_usage}次\n"
        f"充值次数: {count}\n"
        f"支付金额: {amount}元\n"
        f"=================="
    )

    out_trade_no = f"YPC{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"

    if _select_and_pay(f"{autman_username}-甬派车位充值-{count}次", amount, "YPC"):
        update_success, new_count = update_user_parking_usage(autman_username, count)
        middleware.bucketSet('s_yongpai_parking_orders', out_trade_no, json.dumps({
            'user': userid,
            'autman_username': autman_username,
            'amount': amount,
            'count': count,
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'success'
        }))
        if update_success:
            sender.reply(
                f"=====充值成功=====\n"
                f"订单号: {out_trade_no}\n"
                f"用户名: {autman_username}\n"
                f"充值次数: {count}\n"
                f"当前剩余: {new_count}次\n"
                f"=================="
            )
        else:
            sender.reply(
                f"=====充值成功=====\n"
                f"订单号: {out_trade_no}\n"
                f"用户名: {autman_username}\n"
                f"充值次数: {count}\n"
                f"⚠️ 次数更新失败，请联系管理员\n"
                f"=================="
            )


# ==================== Main Entry ====================

message = sender.getMessage()

if message in ['充值', '充币']:
    handle_recharge()
elif message == '购买白名单':
    handle_whitelist_purchase()
elif message in ['甬派车位充值', '甬派充值']:
    handle_yongpai_parking_recharge()
elif message == '进白名单群':
    handle_whitelist_purchase()
else:
    sender.setContinue()
