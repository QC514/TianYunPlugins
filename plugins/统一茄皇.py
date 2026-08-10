# [title: 统一茄皇]
# [language: python]
# [class: 工具类]
# [service: 2993959969] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(茄皇|qh)(登录|登陆)$|^登(录|陆)(茄皇|qh)$|^(茄皇|qh)(查询|管理|教程)$|^(查询|管理)(茄皇|qh)$|^茄皇授权$|^茄皇检测$]
# [cron: 18 9 * * *] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用平台
# [open_source: false]
# [icon: https://img-upload.vorto.cc/beb5a0d45aa58e08348e1e4076fa419e.jpg]
# [version: 1.4]
# [public:true]
# [price: 3.88]
# [description: 统一梦时代茄皇的家，每日签到浇水领奖励<br>指令：茄皇登录、管理、查询、授权、教程<br>1.1.0：重构，支付/授权/管理统一走vorto_utils<br>1.0.5：适配新版<br>1.0.4：适配新版活动<br>1.0.3：新增茄皇教程指令、优化码支付二维码生成方式]

import json
import time
import random
import requests
from datetime import datetime
import middleware
import vorto_utils

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_qh_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_qh', 'coin_key': 'dd_sign_points', 'name': '茄皇的家'}

# [param: {"required":false,"key":"s_qh.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_qh.use_dumbpanel","bool":true,"placeholder":"","name":"使用DumbPanel","desc":"勾选使用DumbPanel面板，不勾选使用青龙面板"}]
# [param: {"required":true,"key":"s_qh.osname","bool":false,"placeholder":"例:S_TYQH","name":"青龙变量名","desc":"青龙容器内茄皇的变量名"}]
# [param: {"required":true,"key":"s_qh.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_qh.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_qh.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_qh.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]


# ==================== Panel Operations ====================

def _get_ql_client():
    """Get panel client based on config switch"""
    osname = middleware.bucketGet('s_qh', 'osname') or 'S_TYQH'
    qlname = middleware.bucketGet('s_qh', 'qlname') or ''
    use_dp = str(middleware.bucketGet('s_qh', 'use_dumbpanel') or '').lower() == 'true'

    if use_dp:
        return vorto_utils.DumbPanelClient(osname, qlname) if qlname else vorto_utils.DumbPanelClient(osname)
    else:
        return vorto_utils.QingLongClient(osname, qlname) if qlname else vorto_utils.QingLongClient(osname)


def update_ql_env(wid, account_info):
    """Update panel env variable, format: wid#phone"""
    wid_value = account_info.get('wid', '')
    phone_value = account_info.get('phone', '')
    if not wid_value or not phone_value:
        return False
    env_value = f"{wid_value}#{phone_value}"
    auth_time = middleware.bucketGet('s_qh_auth', wid) or '未授权'
    ql = _get_ql_client()
    return ql.update_env(wid, env_value, f"茄皇:{vorto_utils.mask_account(wid)}|到期:{auth_time}")


def delete_ql_env(wid):
    """Delete panel env variable"""
    ql = _get_ql_client()
    return ql.delete_env(wid)


# ==================== QH API ====================

def qh_login(wid, phone):
    """Login to QH, returns (success, token, user_data_or_error)"""
    url = "https://api.zhumanito.cn/api/login"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254162e) XWEB/18163 miniProgram/wx532ecb3bdaaf92f9",
        'Content-Type': "application/json;charset=UTF-8",
        'origin': 'https://h5.zhumanito.cn',
        'referer': 'https://h5.zhumanito.cn/'
    }
    payload = {"wid": wid, "wm_phone": phone}
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=10).json()
        if 'data' in response and 'token' in response['data'] and 'user' in response['data']:
            return True, response['data']['token'], response['data']['user']
        return False, None, response.get('msg', '登录失败')
    except Exception as e:
        return False, None, str(e)


# ==================== User Functions ====================

def bind_account():
    """Bindaccounts - wid#phone format"""
    sender.reply(
        "=====茄皇登录=====\n"
        "支持批量登录，格式如下:\n"
        "wid#phone（多账号换行分隔）\n"
        "------------------\n"
        "例如: 11281234567#13345678900\n"
        "------------------\n"
        "💡 wid获取方式:小程序\"统一梦时代\"\n"
        "1.抓包搜索 \"wid\"或登录时抓login接口\n"
        "2.个人中心授权后点头像，复制\"客户编号\"\n"
        "------------------\n"
        "回复\"q\"退出操作\n"
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("操作超时")
        return
    if input_text.lower() == 'q':
        sender.reply("已取消")
        return

    lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
    account_list = []
    for line in lines:
        if '#' in line:
            parts = line.split('#')
            if len(parts) == 2 and len(parts[0]) > 5 and len(parts[1]) >= 7:
                account_list.append({'wid': parts[0].strip(), 'phone': parts[1].strip()})

    if not account_list:
        sender.reply("未检测到有效账号，格式应为 wid#phone")
        return

    sender.reply(f"正在登录 {len(account_list)} 个账号...")

    success_count = 0
    fail_count = 0
    success_accounts = []

    for idx, acc in enumerate(account_list):
        if idx > 0:
            time.sleep(2)
        wid = acc['wid']
        phone = acc['phone']
        try:
            success, token, result = qh_login(wid, phone)
            if not success:
                sender.reply(f"{vorto_utils.mask_account(wid)} 登录失败: {result}")
                fail_count += 1
                continue

            # Save account to user list
            current_value = middleware.bucketGet('s_qh_user', userid)
            if not current_value:
                middleware.bucketSet('s_qh_user', userid, str([wid]))
            else:
                accounts = eval(current_value)
                if wid not in accounts:
                    accounts.append(wid)
                    middleware.bucketSet('s_qh_user', userid, str(accounts))

            # Save wid+phone info
            account_info = {"wid": wid, "phone": phone}
            middleware.bucketSet('s_qh_token', wid, json.dumps(account_info))

            success_count += 1
            success_accounts.append({'wid': wid, 'phone': phone, 'info': account_info})
            sender.reply(f"{vorto_utils.mask_account(wid)} 登录成功")

        except Exception as e:
            sender.reply(f"{vorto_utils.mask_account(wid)} 异常: {str(e)}")
            fail_count += 1

    sender.reply(
        f"=====登录完成=====\n"
        f"成功: {success_count}个\n"
        f"失败: {fail_count}个\n"
        f"=================="
    )

    # Check auth status and trigger authorization for unauthed accounts
    if success_accounts:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        need_auth = []
        for acc in success_accounts:
            wid = acc['wid']
            accountVip = middleware.bucketGet('s_qh_auth', wid)
            if accountVip and accountVip > dqsj:
                sender.reply(f"{vorto_utils.mask_account(wid)} 已授权，到期: {accountVip}")
                update_ql_env(wid, acc['info'])
            else:
                need_auth.append(acc)

        if need_auth:
            sender.reply(f"\n{len(need_auth)} 个账号需要授权")
            authorize_accounts([acc['wid'] for acc in need_auth])


def query_accounts():
    """Query account info"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 茄皇登录 绑定\n==================")
        return

    accounts = eval(uservalue)
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, wid in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_qh_auth', wid)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{vorto_utils.mask_account(wid)}({auth_status})"
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
        for i, wid in enumerate(selected, 1):
            if i > 1:
                time.sleep(2)
            try:
                auth_time = middleware.bucketGet('s_qh_auth', wid)
                auth_status = '已授权' if auth_time and auth_time >= str(datetime.now().date()) else '未授权'

                # Try to login and fetch user resources
                user_info_text = ""
                account_info_str = middleware.bucketGet('s_qh_token', wid)
                if account_info_str:
                    try:
                        account_info = json.loads(account_info_str)
                        phone = account_info.get('phone', '')
                        if phone:
                            login_success, token, user_data = qh_login(wid, phone)
                            if login_success and isinstance(user_data, dict):
                                user_info_text = (
                                    f"\n💧 水滴: {user_data.get('water_num', 0)}"
                                    f"\n☀️ 阳光: {user_data.get('sun_num', 0)}"
                                    f"\n🌱 种子: {user_data.get('seed_num', 0)}"
                                    f"\n🍎 果实: {user_data.get('fruit_num', 0)}"
                                )
                    except:
                        pass

                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 账号: {vorto_utils.mask_account(wid)}\n"
                    f"🏷 状态: {auth_status}\n"
                    f"📅 到期: {auth_time or '未授权'}{user_info_text}\n"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"=====查询失败=====\n❌ 错误: {str(e)}\n==================")

        sender.reply("✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


def manage_account():
    """Manage accounts - authorize/delete/submit to panel"""
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

    # Show account selection list
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, wid in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_qh_auth', wid)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{vorto_utils.mask_account(wid)}({auth_status})"
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
        authorize_accounts(selected)
    elif choice == '2':
        sender.reply("=====确认删除=====\n⚠️ 此操作不可恢复\n回复 y 确认删除\n==================")
        confirm = sender.input(120000, 1, False)
        if confirm and confirm.lower() == 'y':
            for wid in selected:
                if wid in accounts:
                    accounts.remove(wid)
                middleware.bucketDel('s_qh_token', wid)
                middleware.bucketDel('s_qh_auth', wid)
                delete_ql_env(wid)

            if accounts:
                middleware.bucketSet('s_qh_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_qh_user', userid)
            sender.reply(f"✅ 已删除 {len(selected)} 个账号")
        else:
            sender.reply("✅ 已取消")
    elif choice == '3':
        success = 0
        for wid in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_qh_token', wid))
                auth_time = middleware.bucketGet('s_qh_auth', wid)
                if auth_time and auth_time >= str(datetime.now().date()):
                    if update_ql_env(wid, account_info):
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

def authorize_accounts(wids):
    """Unified authorization flow with payment selection"""
    account_infos = []
    for wid in wids:
        try:
            account_infos.append({
                'wid': wid,
                'info': json.loads(middleware.bucketGet('s_qh_token', wid))
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
    months_input = sender.input(120000, 1, False)
    if not months_input or months_input.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        months = int(months_input)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return

        Vipmoney = float(middleware.bucketGet('s_qh', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_qh', 'coin') or '0')

        # Build available payment methods from Vorto config
        pay_config = vorto_utils.get_pay_config()
        available = []

        if pay_config['qr_pay_switch']:
            available.append(("扫码支付", "qrcode"))
        if pay_config['ma_pay_switch']:
            pay_types = pay_config['pay_types']
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

        # Execute payment and authorize
        if payment_type == 'coin':
            for acc in account_infos:
                vorto_utils.process_coin_payment(
                    sender, userid, 's_qh_auth', acc['wid'], acc['info'],
                    months=months, coin_per_month=coin,
                    auth_callback=lambda a, info, m: vorto_utils.process_authorization(
                        sender, 's_qh_auth', a, info, m, update_ql_callback=update_ql_env
                    )
                )
        elif payment_type.startswith('mapay_'):
            if _process_mapay_payment(PLUGIN_CONFIG['name'], months, total_money, payment_type.replace('mapay_', '')):
                for acc in account_infos:
                    vorto_utils.process_authorization(
                        sender, 's_qh_auth', acc['wid'], acc['info'], months,
                        update_ql_callback=update_ql_env
                    )
        elif payment_type == 'qrcode':
            if _process_qrcode_payment(PLUGIN_CONFIG['name'], months, total_money):
                for acc in account_infos:
                    vorto_utils.process_authorization(
                        sender, 's_qh_auth', acc['wid'], acc['info'], months,
                        update_ql_callback=update_ql_env
                    )
    except ValueError:
        sender.reply("❌ 请输入有效数字")


def _process_qrcode_payment(project, months, money):
    """QR code payment via Vorto config"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config['zsm']
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
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


def _process_mapay_payment(project, months, money, pay_type='alipay'):
    """MaPay payment via vorto_utils.MaPayClient"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config['ma_pay_switch']:
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        out_trade_no = f"QH{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config['pay_types'].get(pay_type, '支付宝')

        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"💳 方式: {pay_type_name}\n"
            f"=================="
        )

        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)

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
    """Admin authorization via vorto_utils"""
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
        sender.reply("✅ 已退出")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(
            sender, 's_qh_user', 's_qh_auth', 's_qh_token',
            update_ql_callback=update_ql_env
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender, 's_qh_user', 's_qh_auth', 's_qh_token',
            update_ql_callback=update_ql_env
        )
    else:
        sender.reply("❌ 无效选择")


# ==================== Tutorial ====================

def show_tutorial():
    """Show usage tutorial"""
    sender.reply(
        "=====茄皇教程=====\n"
        "用户指令:\n"
        "• 茄皇登录 - 批量绑定茄皇账号\n"
        "• 茄皇查询 - 查询账号状态和资源信息\n"
        "• 茄皇管理 - 授权/删除/提交青龙\n"
        "• 茄皇教程 - 查看本教程\n"
        "------------------\n"
        "管理员指令:\n"
        "• 茄皇授权 - 管理员按天数授权\n"
        "• 茄皇检测 - 检测过期账号并清理\n"
        "------------------\n"
        "登录格式:\n"
        "wid#phone（每行一个账号）\n"
        "例如: 11287477859#18150271020\n"
        "------------------\n"
        "wid获取方式:\n"
        "入口：小程序\"统一梦时代\"\n"
        "个人中心授权后点头像，复制\"客户编号\"\n"
        "------------------\n"
        "功能说明:\n"
        "• 账号绑定: 保存wid和phone到系统\n"
        "• 状态查询: 查看水滴/阳光/种子/果实等\n"
        "• 授权管理: 付费使用插件功能\n"
        "• 青龙提交: 自动提交到青龙容器\n"
        "• 过期检测: 自动清理过期账号\n"
        "------------------\n"
        "使用流程:\n"
        "1. 发送\"茄皇登录\"绑定账号\n"
        "2. 发送\"茄皇查询\"查看账号状态\n"
        "3. 发送\"茄皇管理\"选择授权账号\n"
        "4. 选择授权时长并完成支付\n"
        "5. 系统自动提交到青龙容器\n"
        "6. 等待定时任务自动执行签到\n"
        "=================="
    )


# ==================== Main Entry ====================

def main():
    """Main entry point"""
    msg = sender.getMessage()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('茄皇' in msg or 'qh' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('茄皇' in msg or 'qh' in msg.lower()):
        manage_account()
    elif '教程' in msg and ('茄皇' in msg or 'qh' in msg.lower()):
        show_tutorial()
    elif '茄皇授权' in msg:
        ks_auth()
    elif '茄皇检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        result = vorto_utils.check_auth_status(
            's_qh', 's_qh_user', 's_qh_auth', 's_qh_token',
            '茄皇的家', delete_ql_callback=delete_ql_env
        )
        sender.reply(result)
    # Cron task - auto check and clean expired accounts
    elif sender.getImtype() == 'fake':
        try:
            result = vorto_utils.check_auth_status(
                's_qh', 's_qh_user', 's_qh_auth', 's_qh_token',
                '茄皇的家', delete_ql_callback=delete_ql_env
            )
            middleware.notifyMasters(result)
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
