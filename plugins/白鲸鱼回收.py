# [title: 白鲸鱼回收]
# [language: python]
# [class: 工具类]
# [service: 2993959969] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(白鲸鱼|bjy)(登录|登陆)$|^登(录|陆)(白鲸鱼|bjy)$|^(白鲸鱼|bjy)(查询|管理|教程)$|^(查询|管理)(白鲸鱼|bjy)$|^白鲸鱼授权$|^白鲸鱼检测$]
# [cron: 30 7 * * *] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用平台
# [open_source: false]
# [icon: https://img-upload.vorto.cc/beb5a0d45aa58e08348e1e4076fa419e.jpg]
# [version: 1.3.0]
# [public:true]
# [price: 88.88]
# [description: 白鲸鱼回收，每日签到答题领鲸鱼币<br>指令：白鲸鱼登录、管理、查询、授权、教程<br>更新日志：<br>1.3.0：重构为vorto_utils规范，支持呆呆面板切换，支付配置统一到Vorto初始化<br>1.2.0：新增教程指令，优化码支付二维码生成方式<br>1.1.0：检测逻辑改为提前天数判断，管理员授权改为按天数授权，完善定时任务<br>1.0.0：初始版本，支持登录、查询、管理、授权、检测]

import os
import json
import time
import hashlib
import random
import base64
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
import middleware
import vorto_utils

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_bjy_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_bjy', 'coin_key': 'dd_sign_points', 'name': '白鲸鱼'}
BJY_KEY = "1f70a57fdf4061a7"
BJY_SECRET = "eBRaFLkuJ5"

# [param: {"required":false,"key":"s_bjy.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_bjy.use_dumbpanel","bool":true,"placeholder":"","name":"使用DumbPanel","desc":"勾选使用DumbPanel面板，不勾选使用青龙面板"}]
# [param: {"required":true,"key":"s_bjy.osname","bool":false,"placeholder":"例:S_BJYHS","name":"青龙变量名","desc":"青龙容器内白鲸鱼的变量名"}]
# [param: {"required":true,"key":"s_bjy.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":false,"key":"s_bjy.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"s_bjy.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_bjy.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]


def get_user_content():
    osname = middleware.bucketGet('s_bjy', 'osname') or 'S_BJYHS'
    qlname = middleware.bucketGet('s_bjy', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_bjy', 'Vipmoney') or '1')
    coin = int(middleware.bucketGet('s_bjy', 'coin') or '0')
    return osname, qlname, Vipmoney, coin


# ==================== Panel Client ====================

def _get_ql_client():
    """Get panel client, auto-switch between QingLong and DumbPanel"""
    osname = middleware.bucketGet('s_bjy', 'osname') or 'S_BJYHS'
    qlname = middleware.bucketGet('s_bjy', 'qlname') or ''
    use_dp = str(middleware.bucketGet('s_bjy', 'use_dumbpanel') or '').lower() == 'true'

    if use_dp:
        return vorto_utils.DumbPanelClient(osname, qlname) if qlname else vorto_utils.DumbPanelClient(osname)
    else:
        return vorto_utils.QingLongClient(osname, qlname) if qlname else vorto_utils.QingLongClient(osname)


def update_ql_env(account, account_info):
    """Update panel env variable"""
    username = account_info.get('username', '')
    password = account_info.get('password', '')
    if not username or not password:
        return False
    env_value = f"{username}#{password}"
    auth_time = middleware.bucketGet('s_bjy_auth', account) or '未授权'
    ql = _get_ql_client()
    return ql.update_env(account, env_value, f"白鲸鱼:{vorto_utils.mask_account(account)}|到期:{auth_time}")


def delete_ql_env(account):
    """Delete panel env variable"""
    ql = _get_ql_client()
    return ql.delete_env(account)


# ==================== BJY API ====================

def generate_md5_sign(params, secret):
    sorted_dict = sorted(params.items())
    str_to_sign = urlencode(sorted_dict, doseq=True) + secret
    return hashlib.md5(str_to_sign.encode('utf-8')).hexdigest()


def bjy_login(username, password):
    url = "https://www.52bjy.com/api/app/member.php"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = {
        'action': "login",
        'username': username,
        'password': password,
        'app': "self",
        'sign': ""
    }
    try:
        response = requests.post(url, data=params, headers=headers, timeout=10).json()
        if response.get('code') == 200 and response.get('is_success'):
            return True, response['data']['token'], response['data'].get('passport', '')
        return False, None, response.get('message', '未知错误')
    except Exception as e:
        return False, None, str(e)


def bjy_userinfo(username, auth):
    url = "https://www.52bjy.com/api/app/user.php"
    headers = {
        'User-Agent': "Mozilla/5.0",
        'content-type': "application/json"
    }
    params = {
        'action': "userinfo",
        'app': "self",
        'appkey': BJY_KEY,
        'auth': auth,
        'is_pop': "0",
        'username': username,
        'version': "2"
    }
    params['sign'] = generate_md5_sign(params, BJY_SECRET)
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10).json()
        if response.get('is_success'):
            return True, response['data']
        return False, response.get('message', '获取失败')
    except Exception as e:
        return False, str(e)


def bjy_creditrecord(username, auth):
    """Get whale coin records"""
    url = "https://www.52bjy.com/api/app/user.php"
    headers = {
        'User-Agent': "Mozilla/5.0",
        'content-type': "application/json"
    }
    now = datetime.now()
    params = {
        'action': "creditrecord",
        'auth': auth,
        'month': str(now.month),
        'page': "1",
        'type': "0",
        'username': username,
        'year': str(now.year)
    }
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10).json()
        if response.get('is_success'):
            return True, response.get('data', [])
        return False, response.get('message', '获取失败')
    except Exception as e:
        return False, str(e)


# ==================== User Functions ====================

def bind_account():
    sender.reply(
        "=====白鲸鱼登录=====\n"
        "支持批量登录，格式如下:\n"
        "账号#密码\n"
        "（多账号换行分隔）\n"
        "------------------\n"
        "回复\"q\"退出操作\n"
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("⏰ 操作超时")
        return
    if input_text.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
    account_list = []
    for line in lines:
        if '#' in line:
            parts = line.split('#', 1)
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                account_list.append({
                    'username': parts[0].strip(),
                    'password': parts[1].strip()
                })

    if not account_list:
        sender.reply("❌ 未检测到有效账号\n格式: 账号#密码")
        return

    sender.reply(f"🔄 正在登录 {len(account_list)} 个账号...")

    success_count = 0
    fail_count = 0
    success_accounts = []

    for acc in account_list:
        username = acc['username']
        password = acc['password']

        try:
            success, token, result = bjy_login(username, password)
            if not success:
                sender.reply(f"❌ {vorto_utils.mask_account(username)} 登录失败: {result}")
                fail_count += 1
                continue

            current_value = middleware.bucketGet('s_bjy_user', userid)
            if not current_value:
                middleware.bucketSet('s_bjy_user', userid, str([username]))
            else:
                accounts = eval(current_value)
                if username not in accounts:
                    accounts.append(username)
                    middleware.bucketSet('s_bjy_user', userid, str(accounts))

            account_info = {"username": username, "password": password}
            middleware.bucketSet('s_bjy_token', username, json.dumps(account_info))

            success_count += 1
            success_accounts.append({'username': username, 'info': account_info})
            sender.reply(f"✅ {vorto_utils.mask_account(username)} 登录成功")

        except Exception as e:
            sender.reply(f"❌ {vorto_utils.mask_account(username)} 异常: {str(e)}")
            fail_count += 1

    sender.reply(
        f"=====登录完成=====\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"=================="
    )

    if success_accounts:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        need_auth = []
        for acc in success_accounts:
            username = acc['username']
            accountVip = middleware.bucketGet('s_bjy_auth', username)
            if accountVip and accountVip > dqsj:
                sender.reply(f"📱 {vorto_utils.mask_account(username)} 已授权，到期: {accountVip}")
                update_ql_env(username, acc['info'])
            else:
                need_auth.append(acc)

        if need_auth:
            sender.reply(f"\n📋 {len(need_auth)} 个账号需要授权")
            authorize_multiple_accounts([acc['username'] for acc in need_auth])


def query_accounts():
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 白鲸鱼登录 绑定\n==================")
        return

    accounts = eval(uservalue)
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_bjy_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{vorto_utils.mask_account(username)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    try:
        if choice == '0':
            selected = accounts.copy()
        else:
            selected = [
                accounts[int(idx.strip()) - 1]
                for idx in choice.split(',')
                if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
            ]

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        sender.reply(f"✅ 已选择 {len(selected)} 个账号，正在查询...")
        for i, username in enumerate(selected, 1):
            try:
                account_info = json.loads(middleware.bucketGet('s_bjy_token', username))
                auth_time = middleware.bucketGet('s_bjy_auth', username)
                if auth_time and auth_time >= str(datetime.now().date()):
                    auth_status = '已授权'
                else:
                    auth_status = '未授权'

                login_success, token, _ = bjy_login(username, account_info.get('password', ''))
                user_info_text = ""
                record_text = ""
                if login_success:
                    info_success, user_data = bjy_userinfo(username, token)
                    if info_success:
                        user_info_text = (
                            f"\n💰 鲸鱼币: {user_data.get('credit', 0)}"
                            f"\n💵 可兑换: {user_data.get('credit_to_cash', '')}"
                            f"\n👑 会员: {user_data.get('vip_name', '')}"
                        )

                    record_success, records = bjy_creditrecord(username, token)
                    if record_success and records:
                        for idx, rec in enumerate(records[:5]):
                            amount = rec.get('amount', '0')
                            addtime = rec.get('addtime', '')
                            record_text += f"\n💰 +{amount}币 {addtime}"

                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 账号: {vorto_utils.mask_account(username)}\n"
                    f"🏷 状态: {auth_status}\n"
                    f"📅 到期: {auth_time or '未授权'}{user_info_text}\n"
                    f"=================="
                    f"{record_text}\n"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"=====查询失败=====\n❌ 错误: {str(e)}\n==================")

        sender.reply("✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


def manage_account():
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

    accounts = eval(uservalue)
    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交青龙\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    # Build account selection list
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_bjy_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{vorto_utils.mask_account(username)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    if account_choice == '0':
        selected = accounts.copy()
    else:
        selected = [
            accounts[int(idx.strip()) - 1]
            for idx in account_choice.split(',')
            if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
        ]

    if not selected:
        sender.reply("❌ 未选择有效账号")
        return

    sender.reply(f"✅ 已选择 {len(selected)} 个账号")

    if choice == '1':
        authorize_multiple_accounts(selected)
    elif choice == '2':
        sender.reply("=====确认删除=====\n⚠️ 此操作不可恢复\n回复 y 确认删除\n==================")
        if sender.input(120000, 1, False).lower() == 'y':
            for username in selected:
                if username in accounts:
                    accounts.remove(username)
                middleware.bucketDel('s_bjy_token', username)
                middleware.bucketDel('s_bjy_auth', username)
                delete_ql_env(username)

            if accounts:
                middleware.bucketSet('s_bjy_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_bjy_user', userid)
            sender.reply(f"✅ 已删除 {len(selected)} 个账号")
        else:
            sender.reply("✅ 已取消")
    elif choice == '3':
        success = 0
        for username in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_bjy_token', username))
                auth_time = middleware.bucketGet('s_bjy_auth', username)
                if auth_time and auth_time >= str(datetime.now().date()):
                    if update_ql_env(username, account_info):
                        success += 1
            except:
                pass
        sender.reply(
            f"=====提交结果=====\n"
            f"✅ 成功: {success}个\n"
            f"❌ 失败: {len(selected) - success}个\n"
            f"=================="
        )


# ==================== Payment & Authorization ====================

def authorize_multiple_accounts(usernames):
    account_infos = []
    for username in usernames:
        try:
            account_infos.append({
                'username': username,
                'info': json.loads(middleware.bucketGet('s_bjy_token', username))
            })
        except:
            pass

    if not account_infos:
        sender.reply("❌ 没有有效账号")
        return

    sender.reply(
        f"✅ {len(account_infos)} 个有效账号\n"
        f"=====设置授权时长=====\n"
        f"请输入授权月数(如:1)\n"
        f"回复\"q\"退出\n"
        f"=================="
    )
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return

        Vipmoney = float(middleware.bucketGet('s_bjy', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_bjy', 'coin') or '0')

        # Build available payment methods via vorto_utils
        pay_config = vorto_utils.get_pay_config()
        pay_types = pay_config.get('pay_types', {})

        available = []
        if pay_config.get('qr_pay_switch'):
            available.append(("扫码支付", "qrcode"))
        if pay_config.get('ma_pay_switch'):
            if not pay_types:
                sender.reply("⚠️ 未配置码支付方式，请联系管理员在Vorto初始化中填写")
            else:
                for pay_key, pay_name in pay_types.items():
                    available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))

        if coin > 0:
            available.append(("积分兑换", "coin"))

        if not available:
            sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
            return

        # Select payment method
        if len(available) == 1:
            payment_name, payment_type = available[0]
        else:
            menu = (
                f"=====选择支付方式=====\n"
                f"📊 账号: {len(account_infos)}个\n"
                f"⏰ 时长: {months}月\n"
                f"💰 金额: {total_money}元\n"
                f"------------------------"
            )
            for i, (name, _) in enumerate(available, 1):
                menu += f"\n[{i}] {name}"
            menu += "\n------------------------\n回复数字选择\n=================="
            sender.reply(menu)

            pay_choice = sender.input(120000, 1, False)
            if not pay_choice or pay_choice.lower() == 'q':
                sender.reply("✅ 已取消")
                return

            pay_idx = int(pay_choice) - 1
            if 0 <= pay_idx < len(available):
                payment_name, payment_type = available[pay_idx]
            else:
                sender.reply("❌ 无效选择")
                return

        # Execute payment
        if payment_type == 'coin':
            for acc in account_infos:
                _process_coin_payment(acc['username'], acc['info'], months, coin)
        elif payment_type.startswith('mapay_'):
            if _handle_mapay_order(PLUGIN_CONFIG['name'], months, total_money, payment_type.replace('mapay_', '')):
                for acc in account_infos:
                    _process_auth(acc['username'], acc['info'], months)
        elif payment_type == 'qrcode':
            if _handle_qrcode_payment(PLUGIN_CONFIG['name'], months, total_money):
                for acc in account_infos:
                    _process_auth(acc['username'], acc['info'], months)
    except ValueError:
        sender.reply("❌ 请输入有效数字")


def _process_auth(username, account_info, months):
    """Wrapper for vorto_utils authorization"""
    return vorto_utils.process_authorization(
        sender, 's_bjy_auth', username, account_info, months,
        update_ql_callback=update_ql_env
    )


def _process_coin_payment(username, account_info, months, coin):
    """Wrapper for vorto_utils coin payment"""
    return vorto_utils.process_coin_payment(
        sender, userid, 's_bjy_auth', username, account_info,
        months=months, coin_per_month=coin,
        auth_callback=lambda acc, info, m: vorto_utils.process_authorization(
            sender, 's_bjy_auth', acc, info, m, update_ql_callback=update_ql_env
        )
    )


def _handle_qrcode_payment(project, months, money):
    """QR code payment via vorto_utils config"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config.get('zsm', '')
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员在Vorto初始化中配置')
        return False

    sender.reply(
        f"======扫码支付======\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)

    ddzf = sender.waitPay("q", 300000)
    if str(ddzf) == 'q':
        sender.reply('✅ 已取消')
        return False

    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
        if float(ddzf.get('Money') or ddzf.get('money', 0)) >= float(money):
            return True
        sender.reply("❌ 支付金额不足")
        return False
    except:
        sender.reply("❌ 支付验证失败")
        return False


def _handle_mapay_order(project, months, money, pay_type='alipay'):
    """MaPay order via vorto_utils"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config.get('ma_pay_switch'):
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        amount = round(float(money), 2)
        out_trade_no = f"BJY{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config.get('pay_types', {}).get(pay_type, '支付宝')

        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {amount}元\n"
            f"💳 方式: {pay_type_name}\n"
            f"=================="
        )

        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(amount, pay_type, out_trade_no, f"{project}-{amount}", userid)

        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False

        pay_url = order.get('pay_url')
        qr_url = vorto_utils.generate_qrcode_url(pay_url)
        sender.replyImage(qr_url)
        sender.reply(f'💳 请使用【{pay_type_name}】扫码支付\n⏰ 5分钟内完成支付\n输入"q"可取消')

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


# ==================== Admin Functions ====================

def ks_auth():
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理员授权")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(
            sender, 's_bjy_user', 's_bjy_auth', 's_bjy_token',
            update_ql_callback=update_ql_env
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender, 's_bjy_user', 's_bjy_auth', 's_bjy_token',
            update_ql_callback=update_ql_env
        )
    else:
        sender.reply("❌ 无效的选择")


# ==================== Tutorial ====================

def show_tutorial():
    tutorial = """
=====白鲸鱼回收教程=====
📱 用户指令:
• 白鲸鱼登录 - 绑定白鲸鱼账号
• 白鲸鱼查询 - 查询账号状态和鲸鱼币信息
• 白鲸鱼管理 - 授权/删除/提交青龙
• 白鲸鱼教程 - 查看本教程
------------------
🔧 管理员指令:
• 白鲸鱼授权 - 管理员按天数授权
• 白鲸鱼检测 - 检测过期账号并清理
------------------
💡 登录说明:
📝 格式: 账号#密码
📝 支持批量登录，多账号换行分隔
------------------
📝 账号获取方式:
入口：白鲸鱼回收APP
==================
"""
    sender.reply(tutorial.strip())


# ==================== Main Entry ====================

def main():
    msg = sender.getMessage()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '教程' in msg and ('白鲸鱼' in msg or 'bjy' in msg.lower()):
        show_tutorial()
    elif '查询' in msg and ('白鲸鱼' in msg or 'bjy' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('白鲸鱼' in msg or 'bjy' in msg.lower()):
        manage_account()
    elif '白鲸鱼授权' in msg:
        ks_auth()
    elif '白鲸鱼检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        result = vorto_utils.check_auth_status(
            's_bjy', 's_bjy_user', 's_bjy_auth', 's_bjy_token',
            '白鲸鱼', delete_ql_callback=delete_ql_env
        )
        sender.reply(result)
    elif sender.getImtype() == 'fake':
        # Cron task - check and clean expired accounts
        try:
            result = vorto_utils.check_auth_status(
                's_bjy', 's_bjy_user', 's_bjy_auth', 's_bjy_token',
                '白鲸鱼', delete_ql_callback=delete_ql_env
            )
            middleware.notifyMasters(result)
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
