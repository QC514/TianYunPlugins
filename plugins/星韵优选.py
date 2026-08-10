# [title: 星韵优选]
# [language: python]
# [class: 工具类]
# [service: 203066880] 售后联系
# [author: rujingxianghai] 作者
# [rule: ^(星韵|xyyx)(登录|登陆)$|^登(录|陆)(星韵|xyyx)$|^(星韵|xyyx)(查询|管理|授权|检测|教程)$|^(查询|管理)(星韵|xyyx)$]
# [cron: 18 9 * * *] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用平台
# [open_source: false]
# [icon: https://img-upload.vorto.cc/beb5a0d45aa58e08348e1e4076fa419e.jpg]
# [version: 1.1]
# [public: true]
# [price: 88.88]
# [description: 星韵优选小程序(日0.1)<br>活动入口：#小程序://星韵优选/kt8xm5WOSI0Z6ri<br>功能：打卡签到、视频任务<br>指令：星韵登录、星韵管理、星韵查询、星韵授权、星韵检测、星韵教程]

# [param: {"required":false,"key":"s_xyyx.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_xyyx.use_daipanel","bool":true,"placeholder":"","name":"使用呆呆面板","desc":"勾选使用呆呆面板，不勾选使用青龙面板"}]
# [param: {"required":false,"key":"s_xyyx.panel_group","bool":false,"placeholder":"例:星韵优选","name":"呆呆面板分组","desc":"填写后新增/更新变量时同步写入 group 字段，留空则不处理"}]
# [param: {"required":true,"key":"s_xyyx.osname","bool":false,"placeholder":"例:S_XYYX","name":"青龙变量名","desc":"青龙容器内的变量名","value":"S_XYYX"}]
# [param: {"required":true,"key":"s_xyyx.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月","value":"1"}]
# [param: {"required":false,"key":"s_xyyx.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_xyyx.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_xyyx.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒","value":"3"}]

import os
import json
import time
import hashlib
import random
import base64
import requests
from datetime import datetime, timedelta
import middleware
import vorto_utils
from vorto_utils import (
    mask_account,
    generate_qrcode_url,
    check_auth_status,
    admin_auth_all_accounts,
    admin_auth_by_user,
    calculate_auth_time,
    get_pay_config,
)

# ==================== 初始化 ====================
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_xyyx_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_xyyx', 'coin_key': 'dd_sign_points', 'name': '星韵优选'}


# ==================== 工具函数 ====================
def get_user_content():
    """获取插件配置"""
    osname = middleware.bucketGet('s_xyyx', 'osname') or 'S_XYYX'
    qlname = middleware.bucketGet('s_xyyx', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_xyyx', 'Vipmoney') or '1')
    coin = int(middleware.bucketGet('s_xyyx', 'coin') or '0')
    return osname, qlname, Vipmoney, coin


# ==================== 面板操作 ====================
def _get_ql_client():
    """获取面板客户端，根据开关决定使用青龙或呆呆面板"""
    osname = middleware.bucketGet('s_xyyx', 'osname') or 'S_XYYX'
    qlname = middleware.bucketGet('s_xyyx', 'qlname') or ''
    use_dp = str(middleware.bucketGet('s_xyyx', 'use_daipanel') or '').lower() == 'true'

    if use_dp:
        if qlname:
            return vorto_utils.DumbPanelClient(osname, qlname)
        return vorto_utils.DumbPanelClient(osname)
    else:
        if qlname:
            return vorto_utils.QingLongClient(osname, qlname)
        return vorto_utils.QingLongClient(osname)


def update_ql_env(account, account_info):
    """更新面板环境变量"""
    env_value = account_info.get('token', '')
    if not env_value:
        return False
    auth_time = middleware.bucketGet('s_xyyx_auth', account) or '未授权'
    panel_group = (middleware.bucketGet('s_xyyx', 'panel_group') or '').strip()
    ql = _get_ql_client()
    return ql.update_env(
        account,
        env_value,
        f"星韵优选:{mask_account(account)}|用户:{userid}|到期:{auth_time}",
        group=panel_group,
    )


def delete_ql_env(account):
    """删除面板环境变量"""
    ql = _get_ql_client()
    return ql.delete_env(account)


# ==================== Token验证 ====================
def verify_token(session_token):
    """验证3rdsession是否有效"""
    try:
        headers = {
            "Host": "gzpengru.weimbo.com",
            "Connection": "keep-alive",
            "3rdsession": session_token,
            "content-type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; M2012K11AC Build/TKQ1.220829.002; wv) AppleWebKit/537.36 MicroMessenger/8.0.45.2400",
            "Referer": "https://servicewechat.com/wxc86c9aecdb67f876/9/page-frame.html"
        }

        payload = {"action": "userInfoData"}
        response = requests.post(
            "https://gzpengru.weimbo.com/api/index.php?ackey=GZYTAPPLET",
            headers=headers,
            json=payload,
            timeout=10
        )

        data = response.json()
        if data and data.get("Status"):
            user_data = data.get("Data", {})
            user_info = user_data.get("user", {})
            user_name = user_info.get("name", "未知")
            user_id_str = user_info.get("id", "")
            user_id = user_id_str.replace("ID：", "").replace("ID:", "").strip() if user_id_str else ""
            jifen = user_data.get("u_money", {}).get("jifen", 0)
            return True, {"name": user_name, "jifen": jifen, "user_id": user_id}
        else:
            return False, {"error": data.get("Message", "Token无效")}
    except Exception as e:
        return False, {"error": str(e)}


# ==================== 绑定账号 ====================
def bind_account():
    """绑定账号"""
    sender.reply(
        "=====星韵优选登录=====\n"
        "请输入3rdsession凭证\n"
        "------------------\n"
        "支持批量登录(换行分隔)\n"
        "回复\"q\"退出\n"
        "=================="
    )

    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("⏰ 操作超时")
        return
    if input_text.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    success_count = 0
    fail_count = 0
    results = []

    for line in lines:
        session_token = line.strip()
        if not session_token:
            continue

        is_valid, info = verify_token(session_token)

        if is_valid:
            account_id = info.get('user_id', '')
            if not account_id:
                results.append(f"❌ 获取用户ID失败")
                fail_count += 1
                continue

            current_uservalue = middleware.bucketGet(bucket='s_xyyx_user', key=userid)
            user_accounts = []
            if current_uservalue:
                try:
                    user_accounts = eval(current_uservalue)
                except:
                    user_accounts = []

            if account_id not in user_accounts:
                user_accounts.append(account_id)

            middleware.bucketSet('s_xyyx_user', userid, str(user_accounts))

            token_info = {
                'token': session_token,
                'user_id': account_id,
                'name': info.get('name', '未知'),
                'jifen': info.get('jifen', 0),
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            middleware.bucketSet('s_xyyx_token', account_id, json.dumps(token_info, ensure_ascii=False))

            results.append(f"✅ ID:{account_id} {info.get('name', '未知')} 积分:{info.get('jifen', 0)}")
            success_count += 1
        else:
            results.append(f"❌ {info.get('error', '验证失败')}")
            fail_count += 1

    result_text = "\n".join(results[:10])
    if len(results) > 10:
        result_text += f"\n... 共{len(results)}条"

    sender.reply(
        f"=====登录完成=====\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"------------------\n"
        f"{result_text}\n"
        f"------------------\n"
        f"💡 发送\"星韵管理\"授权\n"
        f"=================="
    )


# ==================== 查询账号 ====================
def query_accounts():
    """查询账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 星韵登录 绑定\n==================")
        return

    try:
        accounts = eval(uservalue)
    except:
        sender.reply("❌ 账号数据异常")
        return

    if not accounts:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 星韵登录 绑定\n==================")
        return

    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, account in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_xyyx_auth', account)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'

        try:
            token_info = json.loads(middleware.bucketGet('s_xyyx_token', account) or '{}')
            name = token_info.get('name', '未知')
        except:
            name = '未知'

        account_list += f"\n[{i}] {name}({auth_status})"

    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    selected_accounts = []
    if choice == '0':
        selected_accounts = accounts
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
            for idx in indices:
                if 1 <= idx <= len(accounts):
                    selected_accounts.append(accounts[idx - 1])
        except:
            sender.reply("❌ 选择格式错误")
            return

    if not selected_accounts:
        sender.reply("❌ 未选择有效账号")
        return

    results = []
    for account in selected_accounts:
        try:
            token_info = json.loads(middleware.bucketGet('s_xyyx_token', account) or '{}')
            token = token_info.get('token', '')

            if not token:
                results.append(f"❌ {mask_account(account)} Token不存在")
                continue

            is_valid, info = verify_token(token)

            if is_valid:
                auth_time = middleware.bucketGet('s_xyyx_auth', account)
                if not auth_time:
                    auth_status = '未授权'
                elif auth_time < str(datetime.now().date()):
                    auth_status = '已过期'
                else:
                    auth_status = f'到期:{auth_time}'

                results.append(
                    f"📱 {info.get('name', '未知')}\n"
                    f"   积分: {info.get('jifen', 0)}\n"
                    f"   授权: {auth_status}"
                )

                token_info['name'] = info.get('name', token_info.get('name', '未知'))
                token_info['jifen'] = info.get('jifen', token_info.get('jifen', 0))
                token_info['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                middleware.bucketSet('s_xyyx_token', account, json.dumps(token_info, ensure_ascii=False))
            else:
                results.append(f"❌ {mask_account(account)} Token已失效")
        except Exception as e:
            results.append(f"❌ {mask_account(account)} 查询异常")

    result_text = "\n------------------\n".join(results)
    sender.reply(
        f"=====查询结果=====\n"
        f"------------------\n"
        f"{result_text}\n"
        f"=================="
    )


# ==================== 管理账号 ====================
def manage_account():
    """管理账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

    try:
        accounts = eval(uservalue)
    except:
        sender.reply("❌ 账号数据异常")
        return

    sender.reply(
        "=====星韵管理=====\n"
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

    if choice == '1':
        authorize_accounts(accounts)
    elif choice == '2':
        delete_accounts(accounts)
    elif choice == '3':
        submit_to_qinglong(accounts)
    else:
        sender.reply("❌ 无效选择")


def select_accounts_menu(accounts, action_name):
    """选择账号（通用）"""
    account_list = f"\n========选择{action_name}=======\n[0] 全部账号"
    for i, account in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_xyyx_auth', account)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'

        try:
            token_info = json.loads(middleware.bucketGet('s_xyyx_token', account) or '{}')
            name = token_info.get('name', '未知')
        except:
            name = '未知'

        account_list += f"\n[{i}] {name}({auth_status})"

    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        return None

    selected = []
    if choice == '0':
        selected = accounts
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',') if x.strip().isdigit()]
            for idx in indices:
                if 1 <= idx <= len(accounts):
                    selected.append(accounts[idx - 1])
        except:
            pass

    return selected


def authorize_accounts(accounts):
    """授权账号"""
    selected = select_accounts_menu(accounts, "授权账号")
    if not selected:
        sender.reply("✅ 已取消")
        return

    account_infos = []
    for account in selected:
        try:
            token_info = json.loads(middleware.bucketGet('s_xyyx_token', account) or '{}')
            if token_info.get('token'):
                account_infos.append({'account': account, 'info': token_info})
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
    except ValueError:
        sender.reply("❌ 请输入有效数字")
        return

    osname, qlname, Vipmoney, coin = get_user_content()
    total_money = len(account_infos) * months * Vipmoney

    # 构建支付选项（通过 vorto_utils 读取 Vorto初始化 配置）
    pay_config = get_pay_config()
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

    user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
    pay_menu = "=====选择支付方式=====\n"
    for i, (name, _) in enumerate(available, 1):
        if name == "积分兑换":
            pay_menu += f"[{i}] {name} (需要{coin * months * len(account_infos)}分，当前{user_coins}分)\n"
        else:
            pay_menu += f"[{i}] {name} (¥{total_money})\n"
    pay_menu += "------------------\n回复序号选择\n回复\"q\"取消\n=================="

    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False)

    if not pay_choice or pay_choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        pay_idx = int(pay_choice) - 1
        if pay_idx < 0 or pay_idx >= len(available):
            sender.reply("❌ 无效选择")
            return

        pay_name, pay_type = available[pay_idx]

        paid = False
        if pay_type == "coin":
            required_coins = coin * months * len(account_infos)
            if user_coins < required_coins:
                sender.reply(f"❌ 积分不足，需要{required_coins}分，当前{user_coins}分")
                return
            middleware.bucketSet('dd_sign_points', userid, str(user_coins - required_coins))
            paid = True
        elif pay_type == "qrcode":
            paid = process_qrcode_payment("星韵优选", months, total_money)
        elif pay_type.startswith("mapay_"):
            actual_type = pay_type.replace("mapay_", "")
            paid = process_mapay_payment("星韵优选", months, total_money, actual_type)

        if paid:
            success_list = []
            fail_list = []
            for acc_info in account_infos:
                try:
                    new_expire = calculate_auth_time('s_xyyx_auth', acc_info['account'], months=months)
                    middleware.bucketSet('s_xyyx_auth', acc_info['account'], new_expire)
                    update_ql_env(acc_info['account'], acc_info['info'])
                    success_list.append(f"{mask_account(acc_info['account'])} → {new_expire}")
                except Exception as e:
                    fail_list.append(f"{mask_account(acc_info['account'])} {str(e)}")

            result = "=====授权完成=====\n"
            result += f"✅ 成功: {len(success_list)}个\n"
            if success_list:
                result += '\n'.join(success_list) + '\n'
            if fail_list:
                result += f"❌ 失败: {len(fail_list)}个\n"
                result += '\n'.join(fail_list) + '\n'
            result += "=================="
            sender.reply(result)
        else:
            if pay_type == "coin":
                middleware.bucketSet('dd_sign_points', userid, str(user_coins))
    except:
        sender.reply("❌ 支付处理异常")


def delete_accounts(accounts):
    """删除账号"""
    selected = select_accounts_menu(accounts, "删除账号")
    if not selected:
        sender.reply("✅ 已取消")
        return

    sender.reply(f"⚠️ 确认删除 {len(selected)} 个账号?\n回复\"确认\"删除，其他取消")
    confirm = sender.input(60000, 1, False)

    if confirm != "确认":
        sender.reply("✅ 已取消")
        return

    success_count = 0
    for account in selected:
        try:
            delete_ql_env(account)
            middleware.bucketDel('s_xyyx_token', account)
            middleware.bucketDel('s_xyyx_auth', account)
            if account in accounts:
                accounts.remove(account)
            success_count += 1
        except:
            pass

    if accounts:
        middleware.bucketSet('s_xyyx_user', userid, str(accounts))
    else:
        middleware.bucketDel('s_xyyx_user', userid)

    sender.reply(f"✅ 删除完成，成功 {success_count} 个")


def submit_to_qinglong(accounts):
    """提交到青龙"""
    selected = select_accounts_menu(accounts, "提交青龙")
    if not selected:
        sender.reply("✅ 已取消")
        return

    valid_accounts = []
    for account in selected:
        auth_time = middleware.bucketGet('s_xyyx_auth', account)
        if auth_time and auth_time >= str(datetime.now().date()):
            try:
                token_info = json.loads(middleware.bucketGet('s_xyyx_token', account) or '{}')
                if token_info.get('token'):
                    valid_accounts.append({'account': account, 'info': token_info})
            except:
                pass

    if not valid_accounts:
        sender.reply("❌ 没有已授权且有效的账号")
        return

    success_count = 0
    for acc in valid_accounts:
        if update_ql_env(acc['account'], acc['info']):
            success_count += 1

    sender.reply(f"✅ 提交完成，成功 {success_count}/{len(valid_accounts)} 个")


# ==================== 支付功能 ====================
def process_qrcode_payment(project, months, money):
    """收款码支付"""
    if float(money) == 0:
        return True

    pay_config = get_pay_config()
    zsm = pay_config.get('zsm', '')
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


def process_mapay_payment(project, months, money, pay_type='alipay'):
    """码支付处理"""
    if float(money) == 0:
        return True

    pay_config = get_pay_config()
    if not pay_config.get('ma_pay_switch'):
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        out_trade_no = f"XYYX{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config.get('pay_types', {}).get(pay_type, '支付宝')

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
        qr_url = generate_qrcode_url(pay_url)
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


# ==================== 管理员功能 ====================
def ks_auth():
    """管理员授权"""
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
        admin_auth_all_accounts(
            sender, 's_xyyx_user', 's_xyyx_auth', 's_xyyx_token',
            update_ql_callback=update_ql_env
        )
    elif choice == '2':
        admin_auth_by_user(
            sender, 's_xyyx_user', 's_xyyx_auth', 's_xyyx_token',
            update_ql_callback=update_ql_env
        )
    else:
        sender.reply("❌ 无效的选择")


def show_tutorial():
    """显示教程"""
    sender.reply(
        "=====星韵优选教程=====\n"
        "📱 活动入口:\n"
        "#小程序://星韵优选/kt8xm5WOSI0Z6ri\n"
        "------------------\n"
        "用户指令:\n"
        "1. 星韵登录 - 绑定账号\n"
        "2. 星韵查询 - 查询积分和状态\n"
        "3. 星韵管理 - 授权、删除、提交面板\n"
        "4. 星韵教程 - 查看说明\n"
        "------------------\n"
        "管理员指令:\n"
        "1. 星韵授权 - 批量授权\n"
        "2. 星韵检测 - 检测过期并清理\n"
        "------------------\n"
        "绑定输入:\n"
        "3rdsession凭证\n"
        "支持换行批量绑定\n"
        "=================="
    )


# ==================== 主入口 ====================
def main():
    """主入口"""
    msg = sender.getMessage()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('星韵' in msg or 'xyyx' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('星韵' in msg or 'xyyx' in msg.lower()):
        manage_account()
    elif '教程' in msg and ('星韵' in msg or 'xyyx' in msg.lower()):
        show_tutorial()
    elif '星韵授权' in msg or 'xyyx授权' in msg.lower():
        ks_auth()
    elif '星韵检测' in msg or 'xyyx检测' in msg.lower():
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        result = check_auth_status(
            's_xyyx', 's_xyyx_user', 's_xyyx_auth', 's_xyyx_token',
            '星韵优选', delete_ql_callback=delete_ql_env
        )
        sender.reply(result)
    # 定时任务
    elif sender.getImtype() == 'fake':
        try:
            result = check_auth_status(
                's_xyyx', 's_xyyx_user', 's_xyyx_auth', 's_xyyx_token',
                '星韵优选', delete_ql_callback=delete_ql_env
            )
            middleware.notifyMasters(result)
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
