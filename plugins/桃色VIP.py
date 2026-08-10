#[title: 桃色VIP]
#[language: python]
#[class: 工具类]
#[service: 2993959969] 售后联系方式
#[author: rujingxianghai] 作者
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^桃色登录$|^登录桃色$|^桃色查询$|^桃色管理$|^桃色运行$|^桃色一键运行$|^桃色刷新$|^刷新桃色$|^桃色授权$|^桃色检测$|^桃色教程$] 匹配规则
#[cron: 18 8 * * *] cron定时
#[priority: 0] 优先级
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: https://y.gtimg.cn/music/photo_new/T053M0000011Juce2IQQ8j.jpg]图标链接地址
#[version: 1.4.0]版本号
#[public: true] 是否发布
#[price: 5.88] 上架价格
#[description: 指令：桃色登录|登录桃色|桃色查询|桃色管理|桃色运行|桃色一键运行|桃色刷新|刷新桃色|桃色授权|桃色检测|桃色教程<br>桃色VIP登录插件，内置脚本<br>积分兑实物，雨伞及各类用品<br>更新日志：<br>1.0.0：初版，计划任务自行定时"桃色一键运行"(先刷新SSID，再运行任务)<br>1.0.2：新增易支付对接<br>1.2.0：新增检测功能(提前天数提醒+过期清理)，管理员授权改为按天数授权，新增定时任务自动检测<br>1.3.0：新增桃色教程指令，优化码支付二维码生成方式<br>1.4.0：重构支付模块使用vorto_utils统一支付，移除插件级支付配置] 使用方法尽量写具体

import json
import requests
import time
import random
import string
from datetime import datetime, timedelta
import middleware
import vorto_utils

# ========== Init ==========
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_taose_user', key=userid)

# [param: {"required":true,"key":"s_taose.Vipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_taose.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_taose.wxpusher_uids","bool":false,"placeholder":"UID_xxx,UID_yyy","name":"WxPusher推送UID，多个用英文逗号分隔","desc":"扫码关注：https://img-upload.vorto.cc/a2f034a9cb69badfe18e364d32be70ea.png"}]
# [param: {"required":false,"key":"s_taose.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_taose.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]

PLUGIN_CONFIG = {'bucket': 's_taose', 'coin_key': 'dd_sign_points', 'name': '桃色VIP'}

# ========== Common Headers ==========
def _get_headers(cookies=''):
    """Build common request headers for taose API"""
    return {
        "Host": "wxapp.lllac.com",
        "Connection": "keep-alive",
        "charset": "utf-8",
        "cookie": cookies,
        "User-Agent": "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300473 MMWEBSDK/20240404 MMWEBID/1429 MicroMessenger/8.0.49.2600(0x2800313D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android",
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip,compress,br,deflate",
        "Referer": "https://servicewechat.com/wxa11d535651f0f097/58/page-frame.html"
    }

# ========== WxPusher Push ==========
def push_notification(title, content):
    """Push notification via WxPusher"""
    WXPUSHER_APP_TOKEN = 'AT_v7dTqxoP9PqVeosNzy2RrWZxmKIm5x4q'
    WXPUSHER_UIDS = middleware.bucketGet('s_taose', 'wxpusher_uids') or ''

    if not WXPUSHER_APP_TOKEN or not WXPUSHER_UIDS:
        print("未配置WxPusher推送参数，跳过推送")
        return False

    try:
        uid_list = [uid.strip() for uid in WXPUSHER_UIDS.split(',') if uid.strip()]
        data = {
            "appToken": WXPUSHER_APP_TOKEN,
            "content": content,
            "summary": title,
            "contentType": 2,
            "uids": uid_list
        }
        response = requests.post("http://wxpusher.zjiecode.com/api/send/message", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return True
            print(f"推送失败：{result.get('msg', '未知错误')}")
        return False
    except Exception as e:
        print(f"推送异常：{str(e)}")
        return False


def push_task_statistics(stats_data):
    """Push task statistics with HTML table"""
    if not stats_data:
        return False

    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    current_day = datetime.now().strftime("%Y年%m月%d日")

    push_content = f"""
    <div style="font-family: 'Microsoft YaHei', Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); overflow: hidden;">
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 20px; text-align: center;">
            <h2 style="margin: 0; font-size: 24px; font-weight: bold;">🍑 桃色VIP</h2>
        </div>
        <div style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); padding: 20px; margin: 15px; border-radius: 10px;">
            <h3 style="margin: 0 0 15px 0; text-align: center; color: white; font-size: 20px;">今日统计</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                <div style="flex: 1; min-width: 120px; background: rgba(255,255,255,0.95); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #666; font-size: 14px; margin-bottom: 5px;">运行账号数</div>
                    <div style="font-size: 24px; font-weight: bold; color: #f5576c;">{len(stats_data['account_details'])}个</div>
                </div>
                <div style="flex: 1; min-width: 120px; background: rgba(255,255,255,0.95); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="color: #666; font-size: 14px; margin-bottom: 5px;">成功执行</div>
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">{stats_data['success_count']}个</div>
                </div>
            </div>
        </div>
        <div style="padding: 0 15px 15px 15px;">
            <h3 style="text-align: center; color: #333; font-size: 18px; margin-bottom: 15px;">账号明细</h3>
            <table style="width: 100%; border-collapse: collapse; background: #fff;">
                <thead>
                    <tr style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">序号</th>
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">账号</th>
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">执行状态</th>
                        <th style="padding: 12px 8px; text-align: center; color: white; font-size: 14px; border: 1px solid #ddd;">豆子</th>
                    </tr>
                </thead>
                <tbody>
    """

    for idx, account in enumerate(stats_data['account_details'], 1):
        status_color = '#28a745' if account['status'] == '成功' else '#e74c3c'
        push_content += f"""
                    <tr style="background: #f8f9fa;">
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px;">{idx}</td>
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px;">{account['account']}</td>
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px; color: {status_color}; font-weight: bold;">{account['status']}</td>
                        <td style="padding: 10px 8px; text-align: center; border: 1px solid #ddd; font-size: 13px;">{account['dou']}</td>
                    </tr>
        """

    push_content += f"""
                    <tr style="background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); font-weight: bold;">
                        <td colspan="2" style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-size: 14px;">总计</td>
                        <td style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-size: 14px; color: #28a745;">成功{stats_data['success_count']}个</td>
                        <td style="padding: 12px 8px; text-align: center; border: 1px solid #ddd; font-size: 14px;">-</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div style="display: flex; justify-content: center; align-items: center; background: #f8f9fa; padding: 15px; color: #6c757d; font-size: 12px; border-top: 1px solid #dee2e6;">
            <p style="margin: 0;">🍑 桃色VIP任务系统<br>统计时间: {current_time}</p>
        </div>
    </div>
    """

    return push_notification(f"🍑 桃色VIP {current_day}", push_content)


# ========== Taose API ==========
def login_with_account(username, password, skip_auth=False):
    """Login with username and password, save token"""
    try:
        session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

        response = requests.post(
            "https://wxapp.lllac.com/xqw/login.php",
            data={"act": "login", "u_name": username, "u_pass": password, "session_id": session_id},
            headers=_get_headers(f"SSID={session_id}")
        )

        if response.status_code != 200:
            raise Exception("登录请求失败")

        result = response.json()
        if result.get('error') != 0:
            raise Exception(result.get('msg', '登录失败'))

        sender.reply(f"✅ 账号 {username} 登录成功，正在获取用户信息...")

        # Save password separately
        middleware.bucketSet('s_taose_pwd', username, password)

        # Update user account list
        global uservalue
        accounts = eval(uservalue or '[]')
        if username not in accounts:
            accounts.append(username)
            middleware.bucketSet('s_taose_user', userid, str(accounts))
            uservalue = str(accounts)

        # Save token: username#password#SSID=xxx
        middleware.bucketSet('s_taose_token', username, f"{username}#{password}#SSID={session_id}")

        return process_login(f"SSID={session_id}", username, skip_auth)

    except Exception as e:
        sender.reply(f"❌ 登录失败: {str(e)}")
        return False


def get_user_info(cookies):
    """Get user info from taose API"""
    try:
        response = requests.get(
            "https://wxapp.lllac.com/xqw/user_home_v2.php?act=home&channel=tsvip&qudao=normal&cid_most=&gid_most=&version=30&od_count=",
            headers=_get_headers(cookies)
        )

        if response.status_code != 200:
            raise Exception("获取用户信息失败")

        result = response.json()
        if result.get('error') != 0:
            raise Exception(result.get('msg', '获取用户信息失败'))

        return {
            'username': result.get('user_name', '未知'),
            'rank': result.get('user_rank', '未知'),
            'point': result.get('user_point', '0'),
            'dou': result.get('user_dou', '0'),
            'next_rank': result.get('next_rank', '未知'),
            'next_point': result.get('next_point', '0'),
            'bar': result.get('bar', '0')
        }
    except Exception as e:
        raise Exception(f"获取用户信息失败: {str(e)}")


def sign_account(cookies):
    """Sign in for a single account"""
    try:
        ssid = cookies.split('=')[1] if '=' in cookies else cookies
        response = requests.get(
            f"https://wxapp.lllac.com/xqw/user_mall.php?act=signToday&ssid={ssid}&spm=x.user",
            headers=_get_headers(cookies)
        )

        if response.status_code != 200:
            raise Exception("签到请求失败")

        return response.json()
    except Exception as e:
        raise Exception(f"签到失败: {str(e)}")


def refresh_account_ssid(account):
    """Refresh SSID for a single account by re-login"""
    try:
        cookie_str = middleware.bucketGet('s_taose_token', account)
        if not cookie_str:
            return f"❌ 账号 {account} 未找到登录信息"

        parts = cookie_str.split('#')
        if len(parts) < 2:
            return f"❌ 账号 {account} 登录信息不完整"

        username, password = parts[0], parts[1]
        session_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

        response = requests.post(
            "https://wxapp.lllac.com/xqw/login.php",
            data={"act": "login", "u_name": username, "u_pass": password, "session_id": session_id},
            headers=_get_headers(f"SSID={session_id}")
        )

        if response.status_code != 200:
            return f"❌ 账号 {account} 刷新SSID失败: 请求错误"

        result = response.json()
        if result.get('error') != 0:
            return f"❌ 账号 {account} 刷新SSID失败: {result.get('msg', '登录失败')}"

        middleware.bucketSet('s_taose_token', account, f"{username}#{password}#SSID={session_id}")
        return f"✅ 账号 {account} SSID已更新"

    except Exception as e:
        return f"❌ 账号 {account} 刷新SSID失败: {str(e)}"


def _get_cookies(account):
    """Extract cookies from stored token string"""
    cookie_str = middleware.bucketGet('s_taose_token', account)
    if not cookie_str:
        return None
    parts = cookie_str.split('#')
    return parts[2] if len(parts) >= 3 else cookie_str


# ========== Login Flow ==========
def login():
    """Login flow with existing account selection or new account"""
    try:
        global uservalue
        uservalue = middleware.bucketGet(bucket='s_taose_user', key=userid)
        accounts = eval(uservalue or '[]')

        if accounts:
            account_list = "=====已绑定账号====="
            for i, account in enumerate(accounts, 1):
                auth_time = middleware.bucketGet('s_taose_auth', account) or '未授权'
                account_list += f"\n[{i}] {account} ({auth_time})"
            account_list += "\n=================\n选择序号刷新SSID\n输入账号进行登录\n回复\"q\"退出"

            sender.reply(account_list)
            choice = sender.listen(60000)

            if not choice or choice == 'q':
                sender.reply("✅ 已退出登录流程")
                return

            try:
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    selected = accounts[index]
                    password = middleware.bucketGet('s_taose_pwd', selected)
                    if not password:
                        sender.reply("⚠️ 未找到该账号的密码记录，请重新输入密码:")
                        password = sender.listen(60000)
                        if not password or password == 'q':
                            sender.reply("✅ 已退出登录流程")
                            return
                    login_with_account(selected, password)
                    return
            except ValueError:
                pass

            # Treat input as username
            sender.reply("请输入密码:\n回复\"q\"退出")
            password = sender.listen(60000)
            if not password or password == 'q':
                sender.reply("✅ 已退出登录流程")
                return
            login_with_account(choice, password)
        else:
            sender.reply("请输入账号:\n回复\"q\"退出")
            username = sender.listen(60000)
            if not username or username == 'q':
                sender.reply("✅ 已退出登录流程")
                return

            sender.reply("请输入密码:\n回复\"q\"退出")
            password = sender.listen(60000)
            if not password or password == 'q':
                sender.reply("✅ 已退出登录流程")
                return

            login_with_account(username, password)
    except Exception as e:
        sender.reply(f"❌ 登录流程出错: {str(e)}")


def process_login(cookies, username, skip_auth=False):
    """Handle post-login: show info or trigger auth"""
    try:
        auth_time = middleware.bucketGet('s_taose_auth', username)
        current_date = str(datetime.now().date())
        is_authorized = auth_time and auth_time > current_date

        if skip_auth:
            return True
        elif is_authorized:
            sender.reply(
                f"=====登录成功=====\n"
                f"📱 账号: {username}\n"
                f"📅 授权到期: {auth_time}\n"
                f"✅ 账号已更新\n"
                f"=================="
            )
            return True
        else:
            return authorize_accounts([username])
    except Exception as e:
        sender.reply(f"❌ 处理登录失败: {str(e)}")
        return False


# ========== Query ==========
def query_taose():
    """Query account info for all bound accounts"""
    try:
        accounts = eval(uservalue or '[]')
        if not accounts:
            sender.reply("❌ 您还没有绑定桃色账号")
            return

        for account in accounts:
            cookies = _get_cookies(account)
            if not cookies:
                continue

            try:
                user_info = get_user_info(cookies)
                auth_time = middleware.bucketGet('s_taose_auth', account) or '未授权'
                sender.reply(
                    f"=====账号信息=====\n"
                    f"📱 账号: {vorto_utils.mask_account(account)}\n"
                    f"👤 昵称: {user_info['username']}\n"
                    f"🎖️ 等级: {user_info['rank']}\n"
                    f"📈 成长值: {user_info['point']}\n"
                    f"💰 豆子: {user_info['dou']}\n"
                    f"📅 到期: {auth_time}\n"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"❌ 账号 {vorto_utils.mask_account(account)} 查询失败: {str(e)}")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


# ========== Authorization (via vorto_utils) ==========
def authorize_accounts(selected_accounts):
    """Authorize accounts using vorto_utils unified payment"""
    try:
        Vipmoney = float(middleware.bucketGet('s_taose', 'Vipmoney') or '1')
        coin = int(middleware.bucketGet('s_taose', 'coin') or '0')

        sender.reply(
            f"✅ {len(selected_accounts)} 个账号待授权\n"
            f"=====设置授权时长=====\n"
            f"请输入授权月数(如:1)\n"
            f"回复\"q\"退出\n"
            f"=================="
        )
        months_input = sender.listen(60000)
        if not months_input or months_input == 'q':
            sender.reply("✅ 已取消")
            return False

        try:
            months = int(months_input)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return False
        except ValueError:
            sender.reply("❌ 请输入有效数字")
            return False

        total_money = Vipmoney * months * len(selected_accounts)

        # Free auth
        if Vipmoney <= 0:
            success = 0
            for acc in selected_accounts:
                new_expire = vorto_utils.calculate_auth_time('s_taose_auth', acc, months=months)
                middleware.bucketSet('s_taose_auth', acc, new_expire)
                success += 1
            sender.reply(
                f"=====授权成功=====\n"
                f"📱 账号数量: {success}/{len(selected_accounts)}\n"
                f"💰 价格: 免费\n"
                f"⏰ 时长: {months}月\n"
                f"==================")
            return True

        # Build payment options from vorto_utils
        pay_config = vorto_utils.get_pay_config()
        available = []
        if pay_config.get('qr_pay_switch'):
            available.append(("扫码支付", "qrcode"))
        if pay_config.get('ma_pay_switch'):
            pay_types = pay_config.get('pay_types', {})
            if not pay_types:
                sender.reply("⚠️ 未配置码支付方式，请联系管理员在Vorto初始化中填写")
            else:
                for pay_key, pay_name in pay_types.items():
                    available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
        if coin > 0:
            available.append(("积分兑换", "coin"))

        if not available:
            sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
            return False

        # Show payment selection
        pay_msg = (
            f"=====选择支付方式=====\n"
            f"💰 单价: {Vipmoney}元/月\n"
            f"⏰ 时长: {months}月\n"
            f"📱 账号: {len(selected_accounts)}个\n"
            f"💵 总价: {total_money}元\n"
            f"------------------"
        )
        for i, (name, _) in enumerate(available, 1):
            pay_msg += f"\n[{i}] {name}"
        pay_msg += "\n------------------\n回复数字选择\n回复\"q\"退出"

        sender.reply(pay_msg)
        pay_choice = sender.listen(60000)
        if not pay_choice or pay_choice == 'q':
            sender.reply("✅ 已退出支付流程")
            return False

        try:
            pay_idx = int(pay_choice) - 1
            if pay_idx < 0 or pay_idx >= len(available):
                sender.reply("❌ 无效的选择")
                return False
        except ValueError:
            sender.reply("❌ 无效的选择")
            return False

        pay_name, pay_type = available[pay_idx]
        paid = False

        if pay_type == "coin":
            # Coin payment
            total_coins = coin * months * len(selected_accounts)
            user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            if user_coins < total_coins:
                sender.reply(f"❌ 积分不足\n当前积分: {user_coins}\n所需积分: {total_coins}")
                return False

            sender.reply(
                f"=====积分授权确认=====\n"
                f"🎯 单价: {coin}积分/月\n"
                f"⏰ 时长: {months}月\n"
                f"📱 账号: {len(selected_accounts)}个\n"
                f"💰 总积分: {total_coins}\n"
                f"💰 当前积分: {user_coins}\n"
                f"------------------\n"
                f"回复\"y\"确认\n回复其他取消"
            )
            confirm = sender.listen(60000)
            if not confirm or confirm.lower() != 'y':
                sender.reply("✅ 已取消积分授权")
                return False

            middleware.bucketSet('dd_sign_points', userid, str(user_coins - total_coins))
            paid = True

        elif pay_type == "qrcode":
            # QR code payment
            paid = _process_qrcode_payment("桃色VIP授权", months, total_money)

        elif pay_type.startswith("mapay_"):
            # MaPay payment
            actual_pay_type = pay_type.replace("mapay_", "")
            paid = _process_mapay_payment("桃色VIP授权", months, total_money, actual_pay_type)

        if not paid:
            return False

        # Payment successful, set auth for all accounts
        success = 0
        for acc in selected_accounts:
            try:
                new_expire = vorto_utils.calculate_auth_time('s_taose_auth', acc, months=months)
                middleware.bucketSet('s_taose_auth', acc, new_expire)
                success += 1
            except Exception as e:
                sender.reply(f"账号 {acc} 授权失败: {str(e)}")

        sender.reply(
            f"=====授权成功=====\n"
            f"📱 账号数量: {success}/{len(selected_accounts)}\n"
            f"💳 支付方式: {pay_name}\n"
            f"⏰ 时长: {months}月\n"
            f"------------------\n"
            f"发送\"桃色查询\"查看账号详情"
        )
        return True

    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")
        return False


def _process_qrcode_payment(project, months, money):
    """QR code payment via vorto_utils config"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
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


def _process_mapay_payment(project, months, money, pay_type='alipay'):
    """MaPay payment via vorto_utils"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config.get('ma_pay_switch'):
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        out_trade_no = f"TAOSE{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
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


# ========== Run Tasks ==========
def run_account(account):
    """Run sign-in task for a single account"""
    try:
        cookies = _get_cookies(account)
        if not cookies:
            return f"❌ 账号 {account} 未找到登录信息"

        user_info = get_user_info(cookies)
        if not user_info:
            return f"❌ 账号 {account} 获取用户信息失败"

        sign_result = sign_account(cookies)

        sign_status = "✅ 签到成功"
        sign_reward = ""
        if sign_result.get('error') == 0:
            if sign_result.get('msg') == '今日已签到':
                sign_status = "⏰ 今日已签到"
            else:
                if sign_result.get('day'):
                    sign_reward = f"\n📅 已签到: {sign_result.get('day')}天"

        return (
            f"===== 运行结果 =====\n"
            f"📱 账号: {vorto_utils.mask_account(account)}\n"
            f"💰 豆子: {user_info['dou']}\n"
            f"{sign_status}{sign_reward}\n"
            f"================="
        )
    except Exception as e:
        return f"❌ 账号 {account} 运行失败: {str(e)}"


def run_user_accounts():
    """Run tasks for user's bound accounts (with selection)"""
    try:
        accounts = eval(uservalue or '[]')
        if not accounts:
            return "❌ 您还没有绑定桃色账号"

        account_list = "=====账号列表=====\n[0] 全部账号\n"
        for i, account in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_taose_auth', account) or '未授权'
            account_list += f"[{i}] {vorto_utils.mask_account(account)} ({auth_time})\n"
        account_list += "------------------\n请选择要运行的账号\n多账号逗号分隔\n回复\"q\"退出"

        sender.reply(account_list)
        choice = sender.listen(60000)

        if not choice or choice == 'q':
            return "✅ 已退出运行流程"

        selected = []
        if choice == '0':
            selected = accounts[:]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                for idx in indices:
                    if 0 <= idx < len(accounts):
                        selected.append(accounts[idx])
            except ValueError:
                return "❌ 无效的选择格式"

        if not selected:
            return "❌ 未选择有效账号"

        for account in selected:
            auth_time = middleware.bucketGet('s_taose_auth', account)
            if auth_time and auth_time > str(datetime.now().date()):
                sender.reply(run_account(account))
            else:
                sender.reply(f"❌ 账号 {vorto_utils.mask_account(account)} 未授权或已过期")

    except Exception as e:
        return f"❌ 运行失败: {str(e)}"


def refresh_all_ssids():
    """Refresh SSID for all authorized accounts"""
    try:
        auth_accounts = []
        all_users = middleware.bucketAllKeys('s_taose_user')

        for uid in all_users:
            user_accounts = eval(middleware.bucketGet('s_taose_user', uid) or '[]')
            for account in user_accounts:
                auth_time = middleware.bucketGet('s_taose_auth', account)
                if auth_time and auth_time > str(datetime.now().date()):
                    auth_accounts.append(account)

        if not auth_accounts:
            return "⚠️ 未找到任何已授权账号"

        success_count = sum(1 for acc in auth_accounts if "✅" in refresh_account_ssid(acc))
        return f"✅ 已刷新 {success_count}/{len(auth_accounts)} 个账号的SSID"

    except Exception as e:
        return f"❌ 刷新SSID失败: {str(e)}"


def run_all_accounts():
    """Admin: run all authorized accounts with stats push"""
    try:
        refresh_result = refresh_all_ssids()
        sender.reply(f"正在刷新所有账号SSID...\n{refresh_result}")

        all_users = middleware.bucketAllKeys('s_taose_user')
        if not all_users:
            sender.reply("❌ 未找到任何用户")
            return

        sender.reply("开始运行所有已授权账号...")

        stats_data = {'account_details': [], 'success_count': 0, 'fail_count': 0}

        for uid in all_users:
            user_accounts = eval(middleware.bucketGet('s_taose_user', uid) or '[]')
            for account in user_accounts:
                auth_time = middleware.bucketGet('s_taose_auth', account)
                if not (auth_time and auth_time > str(datetime.now().date())):
                    continue

                try:
                    cookies = _get_cookies(account)
                    if not cookies:
                        raise Exception("无登录信息")

                    user_info = get_user_info(cookies)
                    if not user_info:
                        raise Exception("获取信息失败")

                    sign_account(cookies)
                    stats_data['account_details'].append({
                        'account': vorto_utils.mask_account(account),
                        'status': '成功',
                        'dou': user_info.get('dou', '0')
                    })
                    stats_data['success_count'] += 1
                    sender.reply(run_account(account))
                except Exception as e:
                    stats_data['account_details'].append({
                        'account': vorto_utils.mask_account(account),
                        'status': '失败',
                        'dou': '0'
                    })
                    stats_data['fail_count'] += 1
                    sender.reply(f"❌ 账号 {account} 运行失败: {str(e)}")

        sender.reply("✅ 所有账号运行完成")

        if stats_data['account_details']:
            push_task_statistics(stats_data)

    except Exception as e:
        sender.reply(f"❌ 运行失败: {str(e)}")


def refresh_user_accounts():
    """User: refresh SSID for bound accounts (with selection)"""
    try:
        accounts = eval(uservalue or '[]')
        if not accounts:
            return "❌ 您还没有绑定桃色账号"

        account_list = "=====账号列表=====\n[0] 全部账号\n"
        for i, account in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_taose_auth', account) or '未授权'
            account_list += f"[{i}] {vorto_utils.mask_account(account)} ({auth_time})\n"
        account_list += "------------------\n请选择要刷新SSID的账号\n多账号逗号分隔\n回复\"q\"退出"

        sender.reply(account_list)
        choice = sender.listen(60000)

        if not choice or choice == 'q':
            return "✅ 已退出刷新流程"

        selected = []
        if choice == '0':
            selected = accounts[:]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                for idx in indices:
                    if 0 <= idx < len(accounts):
                        selected.append(accounts[idx])
            except ValueError:
                return "❌ 无效的选择格式"

        if not selected:
            return "❌ 未选择有效账号"

        sender.reply("开始刷新账号SSID...")
        for account in selected:
            sender.reply(refresh_account_ssid(account))

        return "✅ SSID刷新完成"

    except Exception as e:
        return f"❌ 刷新失败: {str(e)}"


# ========== Manage ==========
def manage_taose():
    """Account management: authorize / delete / run"""
    try:
        accounts = eval(uservalue or '[]')
        if not accounts:
            sender.reply("❌ 您还没有绑定桃色账号")
            return

        sender.reply(
            "=====管理选项=====\n"
            "[1] 账号授权\n"
            "[2] 账号删除\n"
            "[3] 运行账号\n"
            "------------------\n"
            "回复数字选择操作\n"
            "回复\"q\"退出"
        )
        option = sender.listen(60000)

        if not option or option == 'q':
            sender.reply("✅ 已退出管理流程")
            return

        if option not in ['1', '2', '3']:
            sender.reply("❌ 无效的选择")
            return

        action_name = {'1': '授权', '2': '删除', '3': '运行'}[option]

        # Show account list
        account_list = "=====账号列表=====\n[0] 全部账号"
        for i, account in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_taose_auth', account) or '未授权'
            account_list += f"\n[{i}] {vorto_utils.mask_account(account)} ({auth_time})"
        account_list += f"\n------------------\n请选择要{action_name}的账号\n多账号逗号分隔\n回复\"q\"退出"

        sender.reply(account_list)
        choice = sender.listen(60000)

        if not choice or choice == 'q':
            sender.reply("✅ 已退出管理流程")
            return

        selected = []
        if choice == '0':
            selected = accounts[:]
        else:
            try:
                indices = [int(x.strip()) - 1 for x in choice.split(',')]
                for idx in indices:
                    if 0 <= idx < len(accounts):
                        selected.append(accounts[idx])
            except ValueError:
                sender.reply("❌ 无效的选择格式")
                return

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        if option == '1':
            authorize_accounts(selected)

        elif option == '2':
            confirm_msg = "=====删除确认=====\n即将删除以下账号:\n"
            for acc in selected:
                auth_time = middleware.bucketGet('s_taose_auth', acc) or '未授权'
                confirm_msg += f"- {vorto_utils.mask_account(acc)} ({auth_time})\n"
            confirm_msg += "------------------\n⚠️ 数据及授权无法恢复\n回复\"y\"确认删除"

            sender.reply(confirm_msg)
            confirm = sender.listen(60000)

            if not confirm or confirm.lower() != 'y':
                sender.reply("✅ 已取消删除")
                return

            success = 0
            for acc in selected:
                try:
                    accounts.remove(acc)
                    middleware.bucketSet('s_taose_token', acc, '')
                    middleware.bucketSet('s_taose_auth', acc, '')
                    middleware.bucketDel('s_taose_pwd', acc)
                    success += 1
                except:
                    continue

            if accounts:
                middleware.bucketSet('s_taose_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_taose_user', userid)

            sender.reply(f"✅ 已成功删除 {success}/{len(selected)} 个账号")

        else:
            for acc in selected:
                auth_time = middleware.bucketGet('s_taose_auth', acc)
                if auth_time and auth_time > str(datetime.now().date()):
                    sender.reply(run_account(acc))
                else:
                    sender.reply(f"❌ 账号 {vorto_utils.mask_account(acc)} 未授权或已过期")

    except Exception as e:
        sender.reply(f"❌ 管理失败: {str(e)}")


# ========== Admin Auth (via vorto_utils) ==========
def ks_auth():
    """Admin authorization by days"""
    if not sender.isAdmin():
        sender.reply("❌ 该指令仅管理员可用")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    choice = sender.listen(60000)
    if not choice or choice == 'q':
        sender.reply("✅ 已退出管理员授权")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(sender, 's_taose_user', 's_taose_auth', 's_taose_token')
    elif choice == '2':
        vorto_utils.admin_auth_by_user(sender, 's_taose_user', 's_taose_auth', 's_taose_token')
    else:
        sender.reply("❌ 无效的选择")


# ========== Auth Check (custom: also cleans s_taose_pwd) ==========
def _cleanup_account(account):
    """Extra cleanup when account expires: remove password"""
    middleware.bucketDel('s_taose_pwd', account)


def check_auth_status():
    """Check auth status with notifications and cleanup (custom for pwd bucket)"""
    notify = middleware.bucketGet('s_taose', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"

    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_taose_user')
    if not all_users:
        return "❌ 没有用户"

    notify_days = int(middleware.bucketGet('s_taose', 'notify_days') or '3')
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0

    for uid in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_taose_user', uid) or '[]')
            to_notify = []
            to_clean = []

            for acc in accounts:
                auth_time_str = middleware.bucketGet('s_taose_auth', acc)

                if not auth_time_str:
                    to_clean.append({'account': acc, 'auth_time': '未授权', 'days_left': 0})
                    continue

                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days

                    if days_left <= 0:
                        to_clean.append({'account': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        to_notify.append({'account': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                except:
                    to_clean.append({'account': acc, 'auth_time': auth_time_str, 'days_left': 0})

            total += len(accounts)

            if to_clean:
                for item in to_clean:
                    acc = item['account']
                    middleware.bucketDel('s_taose_token', acc)
                    middleware.bucketDel('s_taose_pwd', acc)
                    if acc in accounts:
                        accounts.remove(acc)
                    middleware.bucketDel('s_taose_auth', acc)
                    cleaned += 1

                if accounts:
                    middleware.bucketSet('s_taose_user', uid, str(accounts))
                else:
                    middleware.bucketDel('s_taose_user', uid)

            if to_notify:
                notify_list = "\n".join([
                    f"📱 {vorto_utils.mask_account(a['account'])} 剩余{a['days_left']}天({a['auth_time']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====桃色VIP账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"桃色管理\"续费\n"
                    f"=================="
                )
                for ch in channels:
                    try:
                        middleware.push(imType=ch, groupCode='', userID=uid, title="", content=msg)
                        notified += 1
                    except:
                        pass
        except:
            pass

    return f"✅ 检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"


# ========== Tutorial ==========
def show_tutorial():
    """Show plugin tutorial"""
    sender.reply(
        "=====桃色VIP教程=====\n"
        "📱 用户指令:\n"
        "• 桃色登录 - 绑定桃色账号\n"
        "• 桃色查询 - 查询账号状态和豆子信息\n"
        "• 桃色管理 - 授权/删除账号\n"
        "• 桃色运行 - 运行已授权账号任务\n"
        "• 桃色刷新 - 刷新账号SSID\n"
        "• 桃色教程 - 查看本教程\n"
        "------------------\n"
        "🔧 管理员指令:\n"
        "• 桃色授权 - 管理员按天数授权\n"
        "• 桃色检测 - 检测过期账号并清理\n"
        "• 桃色一键运行 - 运行所有用户任务\n"
        "------------------\n"
        "💡 登录说明:\n"
        "📝 输入账号和密码进行登录\n"
        "📝 支持选择已绑定账号刷新SSID\n"
        "------------------\n"
        "📝 账号获取方式:\n"
        "入口：#小程序://桃色VIP/xxxxx\n"
        "注：打开小程序，用微信登录\n"
        "然后在个人中心设置密码\n"
        "这个修改密码入口时有时无，只有自己多试一下，不行就注销再试\n"
        "=================="
    )


# ========== Main ==========
def main():
    """Main entry point"""
    try:
        msg = sender.getMessage()

        if '桃色教程' in msg:
            show_tutorial()
        elif '桃色查询' in msg:
            query_taose()
        elif '桃色管理' in msg:
            manage_taose()
        elif '桃色登录' in msg or '登录桃色' in msg:
            login()
        elif '桃色运行' in msg:
            result = run_user_accounts()
            if result:
                sender.reply(result)
        elif '桃色一键运行' in msg:
            if not sender.isAdmin():
                sender.reply("❌ 该指令仅管理员可用")
                return
            run_all_accounts()
        elif '桃色刷新' in msg or '刷新桃色' in msg:
            result = refresh_user_accounts()
            if result:
                sender.reply(result)
        elif '桃色授权' in msg:
            ks_auth()
        elif '桃色检测' in msg:
            if not sender.isAdmin():
                sender.reply("❌ 仅限管理员")
                return
            sender.reply("🔍 正在检测...")
            sender.reply(check_auth_status())
        elif sender.getImtype() == 'fake':
            try:
                middleware.notifyMasters(check_auth_status())
            except:
                pass
        else:
            sender.setContinue()

    except Exception as e:
        sender.reply(f"❌ 运行出错: {str(e)}")

if __name__ == "__main__":
    main()
