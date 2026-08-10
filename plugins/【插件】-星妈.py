# [title: 【插件】-星妈]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: 1603960061] 售后联系方式
# [disable:false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^(星妈|xing ma)(登录|登陆)$|^登(录|陆)(星妈|xingma)$|^(星妈|xingma)(查询|管理)$|^(查询|管理)(星妈|xingma)$|^清理星妈$|^星妈一键运行$|^星妈授权$|^星妈清理$]
# [cron: 18 8,12,16 * * *] cron定时，支持5位域和6位域
# [priority: 0] 优先级，数字越大表示优先级越高
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [open_source: false]
# [icon: https://i.mji.rip/2025/07/11/2350538ac014afbea48b64409bd5931c.png]图标链接地址，请使用48像素的正方形图标，支持http和https
# [version: 1.2.0]版本号
# [public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 12.88] 上架价格
# [description: 🌟 星妈优选全自动积分管理插件 🌟<br><br>📱 <b>功能特色：</b><br>• 多账号批量管理，支持无限绑定<br>• 自动签到 + 自动完成每日任务<br>• 智能token刷新，无需手动维护<br>• 双重支付方式：积分支付 + 微信支付<br>• 实时积分查询，账号状态一目了然<br><br>💡 <b>核心指令：</b><br>🔐 星妈登录 - 快速绑定账号<br>📊 星妈查询 - 查看积分余额<br>⚙️ 星妈管理 - 账号授权管理<br>🚀 星妈一键运行 - 批量执行任务<br>👑 星妈授权 - 管理员批量授权<br><br>✨ 适配呆呆积分系统，支持积分自动扣费<br>🔄 版本1.0.0 稳定版，持续更新优化中]

# 插件参数配置
# [param: {"required":false,"key":"G_xmyx_config.zsm","name":"收款码","placeholder":"http://example.com/pay.jpg"}]
# [param: {"required":false,"key":"G_xmyx_config.price","name":"月费价格","placeholder":"0.88","value":"0.88"}]
# [param: {"required":false,"key":"G_xmyx_config.points_per_month","name":"积分/月","placeholder":"100","value":"100","desc":"一个账号每月所需积分数量"}]

from datetime import datetime, timedelta
import middleware
import time
import hashlib
import urllib.parse
import json
import re
import random
import uuid
import requests
from urllib.parse import urljoin

loginMessage = """
=====星妈优选登录=====
请输入您的access_token
支持批量登录，多个token用换行分隔
------------------
回复「q」退出绑定
=================="""


# 获取发起者数据
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

appid = "xmyx"
# 从配置桶读取密钥，若无则使用默认值（生产环境应配置）
appKey = (
    middleware.bucketGet(bucket="G_xmyx_config", key="appKey")
    or "TwUQ01lKS1Km5zlV2f7amsZc5EQYkTbv"
)

# publish 公用方法，就是不动产 *******************

"""隐藏手机号的辅助函数"""


def mask_phone(phone):
    """将手机号进行脱敏处理"""
    if not phone or len(phone) < 7:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"


def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value) if value and str(value).strip().isdigit() else default
    except (ValueError, TypeError) as e:
        print(f"[WARN] safe_int转换失败: {value}, error: {str(e)}")
        return default


"""获取插件客户基础配置"""


def get_config():
    """动态获取插件配置（添加每月积分费用参数）"""
    try:
        # 价格配置
        price_str = middleware.bucketGet(bucket="G_xmyx_config", key="price") or "0.88"
        price = float(price_str) if price_str.replace(".", "", 1).isdigit() else 0.88

        # 支付相关
        zsm = middleware.bucketGet(bucket="G_xmyx_config", key="zsm") or ""

        # 积分配置
        points_per_month_str = (
            middleware.bucketGet(bucket="G_xmyx_config", key="points_per_month")
            or "100"
        )
        points_per_month = (
            int(points_per_month_str) if points_per_month_str.isdigit() else 100
        )

        # 返回所有配置
        return {
            "price": price,
            "zsm": zsm,
            "points_per_month": points_per_month,  # 每月所需的积分数量
        }
    except Exception as e:
        sender.reply(f"❌ 配置获取失败: {str(e)}")
        return {"price": 0.88, "zsm": "", "points_per_month": 100}


""" 获取用户列表 输出用户列表[] """


def get_user_accounts(user_id=None):
    """获取用户账号列表（可指定用户ID）"""

    target_userid = user_id if user_id else userid
    uservalue = middleware.bucketGet("G_xmyx_user", target_userid) or "[]"
    user_accounts = []

    if uservalue:
        try:
            accounts_list = json.loads(uservalue)
            if isinstance(accounts_list, list):
                user_accounts = accounts_list
            else:
                user_accounts = [str(accounts_list)]
        except json.JSONDecodeError:
            # 安全处理：JSON解析失败时返回空列表，不使用eval
            print(
                f"[WARN] 账号数据JSON解析失败，数据: {uservalue[:50] if uservalue else 'None'}..."
            )
            user_accounts = []

    return [str(acc) for acc in user_accounts if acc]  # 确保过滤掉空值


"""星妈登录 - 支持批量登录"""


def login():
    sender.reply(loginMessage)
    user_input = sender.input(120000, 1, False).strip()

    if user_input.lower() == "q":
        return

    # 支持多种分隔符：换行、逗号、分号、空格
    # 先按换行分割，再处理每行可能的其他分隔符
    tokens = []
    lines = user_input.replace("\r\n", "\n").split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # 每行可能包含多个token（用逗号或分号分隔）
        for sep in [",", ";", "|"]:
            if sep in line:
                tokens.extend([t.strip() for t in line.split(sep) if t.strip()])
                break
        else:
            # 没有分隔符，整行就是一个token
            if line:
                tokens.append(line)

    # 去重
    tokens = list(dict.fromkeys(tokens))

    if not tokens:
        sender.reply("❌ 未检测到有效的token，请重新输入")
        return

    # 批量处理多个token
    success_count = 0
    fail_count = 0
    results = []

    sender.reply(f"🔄 正在验证 {len(tokens)} 个token，请稍候...")

    for i, access_token in enumerate(tokens, 1):
        try:
            # 验证token是否有效
            client = XingMaYouXuanAuto(access_token)
            userInfo = client.get_user_info()

            if userInfo:
                # 取手机号
                user = userInfo.get("baseInfo") or {}
                mobile = (
                    user.get("mobile") or user.get("fullName") or user.get("openId")
                )

                if mobile:
                    # 登录成功需要存入桶（静默模式）
                    save_account_info_silent(mobile, access_token)
                    success_count += 1
                    results.append(f"✅ [{i}] {mask_phone(mobile)} 登录成功")
                else:
                    fail_count += 1
                    results.append(f"❌ [{i}] 无法获取手机号")
            else:
                fail_count += 1
                # 显示token前6位便于识别
                token_hint = (
                    f"{access_token[:6]}..." if len(access_token) > 6 else access_token
                )
                results.append(f"❌ [{i}] {token_hint} token无效或过期")

            # 添加短暂延迟，避免请求过快
            if i < len(tokens):
                time.sleep(0.5)

        except Exception as e:
            fail_count += 1
            token_hint = (
                f"{access_token[:6]}..." if len(access_token) > 6 else access_token
            )
            results.append(f"❌ [{i}] {token_hint} 验证失败: {str(e)[:20]}")

    # 汇总结果
    result_msg = (
        f"""
=====批量登录结果=====
📊 总计: {len(tokens)} 个token
✅ 成功: {success_count} 个
❌ 失败: {fail_count} 个
------------------
"""
        + "\n".join(results)
        + """
------------------
发送"星妈管理"管理账号
发送"星妈查询"查询账号
=================="""
    )

    sender.reply(result_msg)


def save_account_info_silent(phone, token):
    """静默保存账号信息（不发送回复消息）"""
    accounts = get_user_accounts()

    if phone not in accounts:
        accounts.append(phone)
        middleware.bucketSet("G_xmyx_user", userid, json.dumps(accounts))

    # 保存token
    middleware.bucketSet("G_xmyx_token", phone, token)


"""登录成功存储到数据桶"""


def save_account_info(phone, token):
    """保存账号信息"""
    accounts = get_user_accounts()  # 已经是列表，不需要eval

    if phone not in accounts:
        accounts.append(phone)
        middleware.bucketSet("G_xmyx_user", userid, json.dumps(accounts))

    # 保存token
    middleware.bucketSet(f"G_xmyx_token", phone, token)
    success_msg = f"""
=====登录成功=====
📱 账号: {mask_phone(phone)}
✅ 状态: 添加成功
------------------
发送"星妈管理"管理账号
发送"星妈查询"查询账号"""
    sender.reply(success_msg)


"""星妈查询"""


def query_accounts():
    # 自定义查询逻辑
    today = str(datetime.now().date())
    accounts = get_user_accounts()
    account_info_list = []

    for account in accounts:
        account_info = query_accounts_for_item(account, today)
        if account_info:
            account_info_list.append(account_info)

    final_msg = "=====账号信息汇总=====" + "\n".join(account_info_list) + "\n"
    sender.reply(final_msg)
    pass


"""星妈查询单个"""


def query_accounts_for_item(account, today):
    """获取单个账号信息"""
    token = middleware.bucketGet(f"G_xmyx_token", account)
    if not token:
        return None

    client = XingMaYouXuanAuto(token)
    try:
        client.refresh_token()
    except Exception as e:
        print(f"[WARN] 查询前刷新token失败: {str(e)}")

    userInfo = client.get_user_info()
    user = {"scoreBalance": 0}
    if userInfo:
        user = userInfo.get("memberPoints")
        if not user:
            return None
        auth_data_str = middleware.bucketGet(f"G_xmyx_auth", account)
        # 增加空值检查
        if not auth_data_str:
            auth_status = "授权: ❌ 未授权"
        else:
            try:
                auth_data = json.loads(auth_data_str)
                expire_date = auth_data.get("expire_time")
                auth_status = (
                    f"到期时间: {expire_date}"
                    if expire_date and expire_date > today
                    else "授权: ❌ 未授权"
                )
            except Exception as e:
                print(f"[WARN] 查询单账号授权信息解析失败: {str(e)}")
                auth_status = "授权: ❌ 数据异常"
    else:
        auth_status = "❌ 登录态异常，请重新抓取"
        user["scoreBalance"] = 0

    return f"""
📱 账号: {mask_phone(account)}
💰 积分: {user.get("scoreBalance", "N/A")}
🔐 {auth_status}
=================="""


"""查询用户积分"""


def query_user_points(userid=None):
    """查询用户积分 - 根据图片数据结构适配"""
    if not userid:
        userid = sender.getUserID()

    # 从图片数据结构获取积分
    points = middleware.bucketGet("dd_sign_coin", userid) or "0"

    # 如果查询不到积分，尝试从带sign前缀的key获取（如sign_wxid_xxx）
    if points == "0":
        sign_key = f"sign_{userid}"
        sign_points = middleware.bucketGet("dd_sign_coin", sign_key)
        if sign_points:
            points = sign_points

    config = get_config()

    sender.reply(
        f"📊 您的当前积分: {points}\n"
        f"💰 每账号每月积分: {config['points_per_month']}\n"
        f"👉 联系管理员可充值积分"
    )


"""获取用户积分？"""


def get_user_points(userid=None):
    """获取用户积分值 - 适配呆呆积分数据结构"""
    if not userid:
        userid = sender.getUserID()

    # 优先尝试直接获取用户积分
    points = middleware.bucketGet("dd_sign_coin", userid) or "0"
    user_points = middleware.bucketGet("dd_sign_points", userid) or "0"

    print(f"====={userid}====")

    result_points = {
        "dd_sign_coin": safe_int(points),
        "dd_sign_points": safe_int(user_points),
        "total": safe_int(points) + safe_int(user_points),
    }
    print(f"========={safe_int(points) + safe_int(user_points)}=======")
    # 如果没找到，尝试带'sign_'前缀的key
    if points == "0":
        sign_key = f"sign_{userid}"
        sign_points = middleware.bucketGet("dd_sign_coin", sign_key)
        if sign_points:
            result_points["dd_sign_coin"] = safe_int(sign_points)
            result_points["total"] = safe_int(sign_points) + safe_int(user_points)

    return result_points


"""改用户积分"""


def set_user_points(userid, points):
    """设置用户积分 - 适配呆呆积分数据结构"""
    # 尝试更新主积分值
    middleware.bucketSet("dd_sign_coin", userid, str(points["dd_sign_coin"]))
    middleware.bucketSet("dd_sign_points", userid, str(points["dd_sign_points"]))

    # 尝试更新带'sign_'前缀的积分值
    sign_key = f"sign_{userid}"
    middleware.bucketSet("dd_sign_coin", sign_key, str(points["dd_sign_coin"]))
    return True


"""星妈管理"""


def manage():
    while True:
        accounts = get_user_accounts()  # 使用统一函数获取账号列表
        if not accounts:
            sender.reply("❌ 您尚未绑定任何账号，请先绑定")
            return

        # 统计授权状态（含过期检查）
        authorized_count = 0
        unauthorized_accounts = []
        for account_id in accounts:
            auth_data_str = middleware.bucketGet("G_xmyx_auth", key=account_id)
            is_authorized = False
            if auth_data_str:
                try:
                    auth_data = json.loads(auth_data_str)
                    expire_date = auth_data.get("expire_time", "")
                    if expire_date and expire_date >= str(datetime.now().date()):
                        is_authorized = True
                except Exception as e:
                    print(f"[WARN] 管理页统计授权状态解析失败: {str(e)}")

            if is_authorized:
                authorized_count += 1
            else:
                unauthorized_accounts.append(account_id)

        # 构建账号列表（只显示手机号）
        account_list = []
        for i, account_id in enumerate(accounts, 1):
            # 获取授权状态（含过期检查）
            auth_data_str = middleware.bucketGet("G_xmyx_auth", key=account_id)
            status = "❌"
            status_text = "未授权"
            if auth_data_str:
                try:
                    auth_data = json.loads(auth_data_str)
                    expire_date = auth_data.get("expire_time", "")
                    if expire_date and expire_date >= str(datetime.now().date()):
                        status = "✅"
                        status_text = f"已授权(到期:{expire_date})"
                    else:
                        status_text = f"已过期({expire_date})"
                except Exception as e:
                    print(f"[WARN] 管理页授权状态解析失败: {str(e)}")
                    status_text = "数据异常"

            # 直接显示手机号和授权状态
            account_list.append(
                f"[{i}] 📱 {mask_phone(account_id)} {status}{status_text}"
            )

        # 添加多账号选项
        if accounts:
            account_list.append("\n[0] 所有账号授权（支付）")
        if unauthorized_accounts:
            account_list.append("[9999] 没有授权的账号授权（支付）")

        account_list_str = "\n".join(account_list)

        # 显示用户积分
        user_points = get_user_points()

        print(f"===={user_points}")

        sender.reply(f"""
=====星妈账号管理=====
🔢 绑定账号: {len(accounts)}个
✅ 已授权: {authorized_count}个
❌ 未授权: {len(accounts) - authorized_count}个
📊 当前积分: {user_points["total"]}
-------------------------
{account_list_str}
------------------
回复序号选择操作（q退出）
===================""")

        choice = sender.input(60000, 1, False)
        if choice.lower() == "q":
            sender.reply("已退出管理")
            return

        if choice == "0":
            # 所有账号授权
            sender.reply("您选择了所有账号授权")
            batch_authorize_accounts(accounts, "所有账号")
            return
        elif choice == "9999":
            # 没有授权的账号授权
            sender.reply("您选择了没有授权的账号授权")
            for account_id in unauthorized_accounts:
                authorize_account(account_id)
            return
        elif not choice.isdigit():
            sender.reply("❌ 输入无效，请重新选择")
            continue

        selected_idx = int(choice) - 1
        if selected_idx < 0 or selected_idx >= len(accounts):
            sender.reply("❌ 序号无效，请重新选择")
            continue

        selected_account = accounts[selected_idx]
        sender.reply(
            f"你选择了账号: {mask_phone(selected_account)}\n[1] 授权账号\n[2] 删除账号"
        )
        op = sender.input(60000, 1, False)

        if op == "1":
            authorize_account(selected_account)
            return
        elif op == "2":
            delete_account(selected_account)
            return
        else:
            sender.reply("❌ 无效操作，请重新选择")
            continue


"""授权账号"""


def format_target_label(target_label):
    """格式化支付展示目标，手机号脱敏，其它批量标签原样显示"""
    target_text = str(target_label or "").strip()
    if not target_text:
        return "账号"
    return mask_phone(target_text) if target_text.isdigit() else target_text


def handle_authorize_payment(target_label, months, account_count=1):
    """统一处理单账号/批量授权付款"""
    config = get_config()
    current_points = get_user_points()
    display_name = format_target_label(target_label)
    total_price = config["price"] * months * account_count
    required_points = config["points_per_month"] * months * account_count

    if total_price <= 0 and required_points <= 0:
        return True

    option_lines = []
    option_map = {}

    if config["zsm"]:
        option_map["1"] = "wechat"
        option_lines.append(f"[1] 微信支付 ¥{total_price:.2f}")

    next_index = len(option_map) + 1
    if required_points > 0:
        option_map[str(next_index)] = "points"
        option_lines.append(f"[{next_index}] 积分支付 {required_points}积分")

    if not option_map:
        sender.reply("❌ 未配置可用的支付方式")
        return False

    account_count_line = (
        f"\n📦 授权账号: {account_count}个" if account_count > 1 else ""
    )
    pay_menu = f"""
=====星妈优选授权支付=====
📱 账号: {display_name}{account_count_line}
🎯 授权时长: {months}个月
💰 金额: ¥{total_price:.2f}
📊 积分支付: {required_points}积分（当前积分: {current_points["total"]}）
------------------
{chr(10).join(option_lines)}
回复数字选择支付方式，回复q取消
=================="""
    sender.reply(pay_menu)

    pay_choice = str(sender.input(120000, 1, False) or "").strip()
    if pay_choice.lower() == "q":
        sender.reply("✅ 已取消授权")
        return False

    selected = option_map.get(pay_choice)
    if selected == "wechat":
        return wechat_payment_flow(target_label, months, total_price, config, display_name)
    if selected == "points":
        return point_payment_flow(display_name, months, required_points, config)

    sender.reply("❌ 无效支付方式")
    return False


def authorize_account(account_id):
    """授权账号并处理支付 - 增加积分支付选项"""
    # 获取访问令牌
    access_token = middleware.bucketGet("G_xmyx_token", account_id)
    if not access_token:
        sender.reply("❌ 账号令牌无效，无法获取手机号")
        return

    formatted_phone = account_id

    # 获取当前用户积分 - 使用适配呆呆积分的方法
    current_points = get_user_points()

    # 优化显示
    sender.reply(
        f"您正在授权账号: {mask_phone(account_id)}\n📱 绑定手机: {mask_phone(formatted_phone)}\n📊 当前积分: {current_points['total']}\n\n请输入授权月数 (1-12):"
    )

    months = sender.input(120000, 1, False)

    if not months.isdigit() or int(months) < 1 or int(months) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return

    months = int(months)
    payment_success = handle_authorize_payment(formatted_phone, months, 1)
    if not payment_success:
        return

    # 获取授权结果（包含到期日期和续费类型）
    auth_result = complete_authorization(account_id, months, account_id)

    # 显示包含具体到期日期的成功信息
    sender.reply(
        f"✅ {auth_result['renew_type']}成功！星妈优选已加入定时任务\n"
        f"📅 到期日期: {auth_result['expire_date']}（{months}个月）"
    )


def batch_authorize_accounts(account_ids, title):
    """批量授权：统一输入月数并合并为一次支付"""
    account_ids = list(
        dict.fromkeys(
            [str(account_id).strip() for account_id in account_ids if str(account_id).strip()]
        )
    )
    if not account_ids:
        sender.reply("❌ 没有可授权的账号")
        return

    current_points = get_user_points()
    sender.reply(
        f"""
=====批量账号授权=====
📱 目标: {title}
📦 数量: {len(account_ids)}个
📊 当前积分: {current_points["total"]}
------------------
请输入授权月数 (1-12)
回复q取消
=================="""
    )
    months_text = str(sender.input(120000, 1, False) or "").strip()
    if months_text.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    if not months_text.isdigit() or int(months_text) < 1 or int(months_text) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return

    months = int(months_text)
    if not handle_authorize_payment(f"{title}（{len(account_ids)}个）", months, len(account_ids)):
        return

    success_count = 0
    renew_count = 0
    for account_id in account_ids:
        auth_result = complete_authorization(account_id, months, account_id)
        success_count += 1
        if auth_result.get("renew_type") == "续费":
            renew_count += 1

    sender.reply(
        f"""
=====批量授权完成=====
📱 目标: {title}
📦 授权成功: {success_count}个
🆕 新授权: {success_count - renew_count}个
🔄 续费: {renew_count}个
📅 授权月数: {months}个月
=================="""
    )


"""微信付款"""


def wechat_payment_flow(account_id, months, amount, config, phone):
    """微信支付处理（显示手机号）"""
    target_name = format_target_label(phone)
    sender.reply(f"""
=====微信扫码支付=====
📱 账号: {target_name}
🎯 授权时长: {months}个月
💰 金额: ¥{amount:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
    sender.replyImage(config["zsm"])

    payment_result = sender.waitPay(timeout=600000, exitcode="q")

    if payment_result == "q":
        sender.reply("✅ 支付已取消")
        return False

    Money, Time, From = parse_payment_result(payment_result)

    if Money is None:
        sender.reply("❌ 无法解析支付结果")
        return False

    if float(Money) >= float(amount):
        sender.reply(f"""
✅ 支付成功 ✅
💰 金额: ¥{Money}元
⏰ 时间: {Time}
{f"👤 付款人: {From}" if From else ""}
==================""")
        return True
    else:
        sender.reply(f"""
❌ 支付金额不足 ❌
应付: ¥{amount:.2f}元 
实付: ¥{Money}元
==================""")
        return False


"""积分付款"""


def point_payment_flow(account_id, months, required_points, config):
    """积分支付处理 - 适配呆呆积分结构"""
    # 获取积分余额 - 使用适配方法
    user_points = get_user_points()
    sign_coin = user_points["dd_sign_coin"]
    sign_points = user_points["dd_sign_points"]

    # 检查积分是否足够
    if user_points["total"] < required_points:
        sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points["total"]}积分
请「联系管理员」充值积分
        """)
        return False

    # 确认支付
    sender.reply(f"""
⚠ 确认使用积分支付吗？
📊 扣除: {required_points}积分
📈 剩余: {user_points["total"] - required_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消
    """)

    confirm = sender.input(60000, 1, False).lower()
    if confirm != "y":
        sender.reply("✅ 积分支付已取消")
        return False

        # 优先扣除签到积分
    if sign_coin >= required_points:
        sign_coin -= required_points
    else:
        # 签到积分不足，先扣完签到积分，剩余扣用户积分
        remaining = required_points - sign_coin
        sign_coin = 0
        sign_points -= remaining

    result_points = {
        "dd_sign_coin": sign_coin,
        "dd_sign_points": sign_points,
    }

    # 扣除积分 - 使用适配方法
    new_points = sign_points + sign_coin
    set_user_points(userid, result_points)

    # 记录交易流水
    transaction_data = {
        "userid": userid,
        "account_id": account_id,
        "months": months,
        "points": required_points,
        "balance": new_points,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "星妈优选授权",
    }
    tx_key = f"tx_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    middleware.bucketSet("dd_sign_transactions", tx_key, json.dumps(transaction_data))

    sender.reply(f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {new_points}")
    return True


"""付款结算"""


def parse_payment_result(raw_data):
    """解析微信支付结果（支持多种格式）"""
    Money, Time, From = None, "", ""

    try:
        if isinstance(raw_data, dict):
            # 处理字典格式
            if raw_data.get("type") in ["微信赞赏", "微信收款"]:
                Money = float(raw_data.get("money", 0))
                Time = raw_data.get("time", "")
                From = raw_data.get("from_name", "")
            else:
                Money = float(raw_data.get("Money", 0))
                Time = raw_data.get("Time", "")

        else:
            # 处理JSON字符串或文本格式
            try:
                data = json.loads(raw_data)
                if data.get("type") in ["微信赞赏", "微信收款"]:
                    Money = float(data.get("money", 0))
                    Time = data.get("time", "")
                    From = data.get("from_name", "")
            except Exception as e:
                print(f"[WARN] 解析支付结果JSON失败: {str(e)}")
                # 处理包含"二维码赞赏到账"的文本格式
                if "二维码赞赏到账" in raw_data:
                    try:
                        amount_str = raw_data.split("收款金额￥")[1].split("\n")[0]
                        time_str = raw_data.split("到账时间")[1].split("\n")[0].strip()
                        Money = float(amount_str)
                        Time = time_str
                    except Exception as e:
                        print(f"[WARN] 解析二维码赞赏到账文本失败: {str(e)}")

    except Exception as e:
        sender.reply(f"❌ 解析支付结果失败: {str(e)}")

    return Money, Time, From


"""完成授权"""


def complete_authorization(account_id, months, masked_phone):
    """记录授权时间并存储到数据桶 - 支持续费逻辑"""
    # 1. 尝试获取现有授权信息
    existing_auth = middleware.bucketGet("G_xmyx_auth", account_id)

    print(f"-----existing_auth ===={existing_auth}")

    # 2. 初始化时间变量
    new_expire_time = None
    renew_msg = "新授权"  # 默认为新授权

    # 3. 检查是否已有授权信息
    if existing_auth:
        try:
            auth_info = json.loads(existing_auth)
            # 尝试解析时间格式
            try:
                expire_time = datetime.strptime(auth_info["expire_time"], "%Y-%m-%d")
            except Exception as e:
                print(f"[WARN] 解析授权日期格式失败，尝试时间戳: {str(e)}")
                # 如果格式错误，尝试解析为时间戳
                try:
                    expire_time = datetime.fromtimestamp(
                        float(auth_info["expire_time"])
                    )
                except Exception as e:
                    print(f"[WARN] 解析授权时间戳失败，使用当前时间: {str(e)}")
                    # 所有解析失败则使用当前时间
                    expire_time = datetime.now()

            # 检查是否已经过期
            if expire_time.date() >= datetime.now().date():
                # 未过期，在原有基础上续费
                new_expire_time = expire_time + timedelta(days=months * 30)
                renew_msg = "续费"
            else:
                # 已过期，从当前时间开始计算
                new_expire_time = datetime.now() + timedelta(days=months * 30)
                renew_msg = "新授权"
        except Exception as e:
            print(f"[WARN] 解析现有授权信息失败: {str(e)}")

    # 4. 如果没有设置新时间，使用当前时间
    if not new_expire_time:
        new_expire_time = datetime.now() + timedelta(days=months * 30)
        renew_msg = "新授权"

    # 5. 格式化到期日期（年-月-日）
    expire_date = new_expire_time.date().strftime("%Y-%m-%d")

    # 6. 存储授权信息
    auth_data = {
        "userid": userid,
        "phone": masked_phone or "未知",
        "account_id": account_id,
        "expire_time": expire_date,
        "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "authorized_months": months,
        "is_renewal": (
            "续费" if renew_msg == "续费" else "新授权"
        ),  # 明确标记是续费还是新授权
    }

    middleware.bucketSet(
        bucket="G_xmyx_auth", key=account_id, value=json.dumps(auth_data)
    )

    # 返回带有续费类型和日期的信息
    return {"expire_date": expire_date, "renew_type": renew_msg}


"""删除账号"""


def delete_account(account_id):
    """删除账号"""
    accounts = get_user_accounts()  # 使用统一函数获取账号列表

    sender.reply(f"""
=====删除账号确认=====
确认删除账号 {mask_phone(account_id)} 吗？
请回复 [Y] 确认
回复 [N] 取消
==================""")
    user_confirm = sender.input(120000, 1, False).strip().lower()

    if user_confirm != "y":
        sender.reply("✅ 已取消删除操作")
        return

    try:
        middleware.bucketDel(bucket="G_xmyx_token", key=account_id)
        middleware.bucketDel(bucket="G_xmyx_auth", key=account_id)

        if account_id in accounts:
            accounts.remove(account_id)
            if accounts:
                middleware.bucketSet(
                    bucket="G_xmyx_user", key=userid, value=json.dumps(accounts)
                )
            else:
                middleware.bucketDel(bucket="G_xmyx_user", key=userid)

        sender.reply("✅ 账号删除成功")

    except Exception as e:
        sender.reply(f"❌ 删除失败: {str(e)}")


"""免费授权"""


def free_authorize_account(account_id, months, user_id, masked_phone):
    """免费授权账号（管理员功能）"""
    # 记录授权时间
    expire_time = datetime.now() + timedelta(days=months * 30)

    # 存储授权信息
    auth_data = {
        "userid": user_id,  # 使用管理员指定的用户ID
        "phone": masked_phone,
        "account_id": account_id,
        "expire_time": str(expire_time.date()),
        "payment_type": "管理员免费授权",  # 特殊标记
    }

    middleware.bucketSet(
        bucket="G_xmyx_auth", key=account_id, value=json.dumps(auth_data)
    )

    # 记录管理员操作日志
    admin_log = {
        "admin_id": sender.getUserID(),
        "user_id": user_id,
        "account_id": account_id,
        "months": months,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    middleware.bucketSet(
        "admin_za_auth_logs", f"admin_log_{int(time.time())}", json.dumps(admin_log)
    )


# 管理指令
def admin_authorize_account():
    """管理员指令：星妈授权"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限！")
        return

    # 第一步：选择操作类型
    sender.reply(
        "=====管理员授权操作=====\n"
        "[1] 一键授权所有用户\n"
        "[2] 单独授权用户\n"
        "回复数字选择操作\n"
        "===================="
    )
    choice = sender.input(60000, 1, False)

    if choice == "1":
        # 一键授权所有用户
        users = middleware.bucketAllKeys(bucket="G_xmyx_user")
        if not users:
            sender.reply("❌ 未找到任何绑定用户")
            return

        sender.reply("请输入授权月数 (1-12):")
        months = sender.input(120000, 1, False)
        if not months.isdigit() or int(months) < 1 or int(months) > 12:
            sender.reply("❌ 月数必须为1-12之间的整数")
            return
        months = int(months)

        success_count = 0
        for user in users:
            accounts = get_user_accounts(user)
            for account_id in accounts:
                try:
                    # 设置授权时间
                    expire_time = datetime.now() + timedelta(days=months * 30)

                    # 存储授权信息
                    auth_data = {
                        "userid": user,
                        "phone": account_id,
                        "account_id": account_id,
                        "expire_time": str(expire_time.date()),
                    }

                    middleware.bucketSet(
                        bucket="G_xmyx_auth",
                        key=account_id,
                        value=json.dumps(auth_data),
                    )
                    success_count += 1

                except Exception as e:
                    sender.reply(f"❌ 授权用户 {user} 失败: {str(e)}")

        sender.reply(f"✅ 一键授权完成！成功授权 {success_count} 个账号")

    elif choice == "2":
        # 单独授权用户
        sender.reply("请输入需要授权的用户ID:")
        target_userid = sender.input(120000, 1, False)
        if not target_userid:
            sender.reply("❌ 用户ID无效")
            return

        accounts = get_user_accounts(target_userid)
        if not accounts:
            sender.reply(f"❌ 用户 {target_userid} 未绑定任何星妈账号")
            return

        # 显示该用户的所有账号
        account_lines = []
        for i, account_id in enumerate(accounts, 1):
            account_lines.append(f"[{i}] {mask_phone(account_id)}")

        account_list = "\n".join(account_lines)

        sender.reply(
            "=====用户账号列表=====\n"
            f"用户ID: {target_userid}\n"
            f"账号列表:\n{account_list}\n"
            "------------------\n"
            "回复 [0] 授权全部账号\n"
            "回复序号授权单个账号\n"
            "===================="
        )

        account_choice = sender.input(120000, 1, False)
        if account_choice == "0":
            # 授权全部账号
            sender.reply("请输入授权月数 (1-12):")
            months = sender.input(120000, 1, False)
            if not months.isdigit() or int(months) < 1 or int(months) > 12:
                sender.reply("❌ 月数必须为1-12之间的整数")
                return
            months = int(months)

            success_count = 0
            for account_id in accounts:
                try:
                    expire_time = datetime.now() + timedelta(days=months * 30)

                    auth_data = {
                        "userid": target_userid,
                        "phone": account_id,
                        "account_id": account_id,
                        "expire_time": str(expire_time.date()),
                    }

                    middleware.bucketSet(
                        bucket="G_xmyx_auth",
                        key=account_id,
                        value=json.dumps(auth_data),
                    )
                    success_count += 1

                except Exception as e:
                    sender.reply(f"❌ 授权账号失败: {str(e)}")

            sender.reply(f"✅ 成功授权该用户所有账号（{success_count}个）")

        elif account_choice.isdigit():
            # 授权单个账号
            selected_idx = int(account_choice) - 1
            if selected_idx < 0 or selected_idx >= len(accounts):
                sender.reply("❌ 序号无效")
                return

            account_id = accounts[selected_idx]

            sender.reply(
                f"您选择了账号: {mask_phone(account_id)}\n请输入授权月数 (1-12):"
            )
            months = sender.input(120000, 1, False)
            if not months.isdigit() or int(months) < 1 or int(months) > 12:
                sender.reply("❌ 月数必须为1-12之间的整数")
                return
            months = int(months)

            expire_time = datetime.now() + timedelta(days=months * 30)

            auth_data = {
                "userid": target_userid,
                "phone": account_id,
                "account_id": account_id,
                "expire_time": str(expire_time.date()),
            }

            middleware.bucketSet(
                bucket="G_xmyx_auth", key=account_id, value=json.dumps(auth_data)
            )
            sender.reply(
                f"✅ 授权成功！账号 {mask_phone(account_id)} 已授权 {months}个月"
            )

        else:
            sender.reply("❌ 无效选择")
    else:
        sender.reply("❌ 无效选择")


"""一键运行"""


def xm_auto_run():
    # 1. 获取所有授权账号（从授权桶获取）
    authorized_accounts = []
    auth_keys = middleware.bucketAllKeys(bucket="G_xmyx_auth") or []
    print(f"-----{auth_keys}----")
    # 2. 检查授权是否有效
    for account_id in auth_keys:
        auth_data_str = middleware.bucketGet("G_xmyx_auth", key=account_id)
        if not auth_data_str:
            continue

        try:
            auth_data = json.loads(auth_data_str)
            expire_date = auth_data.get("expire_time")

            # 检查授权是否过期
            if expire_date:
                try:
                    expire_date = datetime.strptime(expire_date, "%Y-%m-%d").date()
                    # 只有不过期的才运行
                    if datetime.now().date() <= expire_date:
                        authorized_accounts.append(account_id)
                except Exception as e:
                    print(f"[WARN] 授权日期格式无效，跳过账号 {account_id}: {str(e)}")
        except Exception as e:
            print(f"[WARN] 授权信息格式错误，跳过账号 {account_id}: {str(e)}")

    if not authorized_accounts:
        sender.reply("❌ 没有已授权的账号")
        return

    # 3. 运行所有授权账号
    run_results = []
    skip_results = []  # 用于记录跳过的账号
    total_earned = 0

    """到了这里才是开始执行"""
    for account_id in authorized_accounts:
        # 运行已授权的单个账号任务
        access_token = middleware.bucketGet("G_xmyx_token", account_id)

        if not access_token:
            skip_results.append(account_id)
            continue

        # 使用新接口获取脱敏手机号
        client = XingMaYouXuanAuto(access_token)
        formatted_phone = mask_phone(account_id)

        # 记录执行前的积分
        userInfo_before = client.get_user_info() or {}
        member_points_before = userInfo_before.get("memberPoints", {})
        score_before = (
            member_points_before.get("scoreBalance", 0) if member_points_before else 0
        )

        print(f"=====当前手机号：{mask_phone(account_id)}=====")
        # 1. 签到
        sign_success = client.signin()
        sign_result = "✅" if sign_success else "❌"

        # 2. 执行任务, 获取任务
        taskList = client.get_task_list() or []
        task_count = len(taskList)
        if task_count > 0:
            run_task(taskList, client, account_id)
            task_result = f"✅完成{task_count}任务"
        else:
            task_result = "⏩无任务"

        # 刷新token
        try:
            client.refresh_token()
            # 刷新完token后等待1秒
            time.sleep(1)
        except Exception as e:
            print(f"刷新token失败，但不影响任务执行: {str(e)}")

        # 3. 获取用户信息和当前积分（用于计算收益差值）
        userInfo_after = client.get_user_info() or {}
        member_points_after = userInfo_after.get("memberPoints", {})
        score_after = (
            member_points_after.get("scoreBalance", 0) if member_points_after else 0
        )
        # 计算本次任务获得的积分（后-前）
        earned_this_run = max(0, score_after - score_before)
        total_earned += earned_this_run

        # 保存结果但不显示
        run_results.append(f"📱 {formatted_phone}: {sign_result}签到 | {task_result}")

    # 构建汇总报告 - 只显示简洁汇总信息，不包含详细结果
    success_count = len(run_results)
    skip_count = len(skip_results)

    result_msg = f"""🚀 星妈任务汇总 📊
====================
✅ 成功账号: {success_count}个
❌ 失败账号: {skip_count}个
💰 积分收益: {total_earned} 
===================="""

    sender.reply(result_msg)


def run_task(taskList, client, account_id):
    """执行任务列表中的所有任务"""
    if not taskList or not isinstance(taskList, list):
        print("没有可执行的任务或任务列表格式错误")
        return

    for task in taskList:
        try:
            # 检查任务数据是否完整
            if not task.get("taskName") or not task.get("taskType"):
                print(f"任务数据不完整: {task}")
                continue

            # 如果匹配到 "购买任意商品"，跳过这个任务（不执行）
            if re.search(r"购买任意商品", task.get("taskName", "")):
                print(f"跳过任务: {task.get('taskName')}")  # 可选：打印日志
                continue  # 跳过当前任务，继续下一个

            # 执行任务
            client.tofinish(task["taskName"], task["taskType"])

            # 添加延迟，模拟用户操作间隔，给任务执行留出时间
            wait_time = random.randint(2, 5)
            print(f"等待 {wait_time} 秒后完成任务...")
            time.sleep(wait_time)

            client.complete_task(task["taskName"], task["taskType"])

            # 任务完成后额外等待一下，防止请求过快
            time.sleep(1)

            # 任务之间添加随机间隔
            task_interval = random.randint(3, 6)
            print(f"任务间隔 {task_interval} 秒...")
            time.sleep(task_interval)

        except Exception as e:
            print(f"执行任务失败: {str(e)}, 任务: {task.get('taskName', '未知任务')}")
            continue


class XingMaYouXuanAuto:
    def __init__(self, assess_token):
        self.token = assess_token
        self.uservalue = get_user_accounts()

        self.headers = {
            "Host": "www.feihevip.com",
            "token": assess_token,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302b) NetType/4G Language/zh_CN",
            "Referer": "https://servicewechat.com/wx4205ec55b793245e/215/page-frame.html",
            "fhAppid": appid,
            "source": "1",
        }

    """"获取签名配置"""

    def get_signature(self):
        fh_nonce_str = self.getFhNonceStr({"length": 16})
        fh_timestamp = self.get_timestamp()
        data = "{}"
        sign_string = f"fhAppid{appid}fhNonceStr{fh_nonce_str}fhTimestamp{fh_timestamp}{data}{appKey}"
        return {
            "fhNonceStr": fh_nonce_str,
            "fhTimestamp": str(fh_timestamp),
            "fhSign": hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper(),
        }

    """获取刷新token的签名配置"""

    def get_signature2(self):
        fh_nonce_str = self.getFhNonceStr({"length": 16})
        fh_timestamp = self.get_timestamp()
        # 注意这里使用了不同的appid和appKey
        sign_string = f"fhAppidxmhfhNonceStr{fh_nonce_str}fhTimestamp{fh_timestamp}98d9fe9b613a479dbcb111ca261e3ce1"
        return {
            "fhNonceStr": fh_nonce_str,
            "fhTimestamp": str(fh_timestamp),
            "fhSign": hashlib.md5(sign_string.encode("utf-8")).hexdigest().upper(),
        }

    def get_timestamp(self):
        # 与JS的 Date.now() 保持一致，取前10位
        return int(str(int(time.time() * 1000))[:10])

    def getFhNonceStr(self, t=None):
        # 处理参数 t，确保和 JS 逻辑一致（默认值 + 类型检查）
        t = t or {}
        config = {
            "length": t.get("length"),
            "numeric": t["numeric"] if "numeric" in t else True,  # 默认 True
            "letters": t["letters"] if "letters" in t else True,  # 默认 True
            "special": t.get("special", False),  # 默认 False
            "exclude": t["exclude"]
            if "exclude" in t and isinstance(t["exclude"], list)
            else [],
        }

        length = config["length"]
        if length is None:
            return ""  # 如果未指定 length，返回空字符串（JS 原逻辑）

        # 生成字符池（完全对应 JS 逻辑）
        char_pool = ""
        if config["numeric"]:
            char_pool += "0123456789"
        if config["letters"]:
            char_pool += "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if config["special"]:
            char_pool += "!$%^&*()_+|~-=`{}[]:;<>?,./"

        # 移除排除的字符（严格对应 JS 的 replace 逻辑）
        for excluded_char in config["exclude"]:
            char_pool = char_pool.replace(excluded_char, "")

        # 生成随机字符串（完全对应 JS 的随机逻辑）
        result = ""
        for _ in range(length):
            r = random.randint(0, len(char_pool) - 1)
            result += char_pool[r]

        return result

    def get_user_info(self):
        try:
            signature = self.get_signature()
            _headers = {**self.headers, **signature}

            res = requests.post(
                url="https://www.feihevip.com/api/starMember/getMemberInfo",
                headers=_headers,
                json={},
                timeout=(5, 30),
            )
            res = res.json()

            if res is not None and res.get("code") == "200" and res.get("data"):
                data = res.get("data", {})
                return data
            else:
                print(f"⛔️ 查询用户信息失败! {res.get('msg')}\n")
        except Exception as e:
            self.ck_status = False
            print(f"⛔️ 查询用户信息失败! {e}")

    def complete_task(self, task_name, task_type):
        try:
            # 最多尝试3次
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    signature = self.get_signature()
                    res = requests.get(
                        url=f"https://www.feihevip.com/api/member/signin/completeTask?taskType={task_type}",
                        headers={**self.headers, **signature},
                        json={},
                        timeout=(5, 30),
                    )
                    res = res.json()
                    print(
                        f"[星妈]完成任务----{task_name}--- 尝试 {attempt}/{max_retries}"
                    )

                    if res.get("code") == "200":
                        if res.get("data"):
                            point = res["data"].get("awardSendPoints", 0)
                            print(f"✅ 完成任务: {task_name}, 获取积分: {point}分\n")
                        else:
                            print(f"✅ 任务: {task_name} 已完成，请勿重复执行\n")
                        return True
                    else:
                        print(
                            f"⚠️ 完成任务: {task_name} 失败! {res.get('msg')}，尝试 {attempt}/{max_retries}\n"
                        )
                        if attempt < max_retries:
                            # 延迟一段时间后重试
                            time.sleep(2)
                            continue
                        return False
                except Exception as e:
                    print(f"⚠️ 完成任务请求异常: {str(e)}，尝试 {attempt}/{max_retries}")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    raise e
            return False
        except Exception as e:
            self.ck_status = False
            print(f"⛔️ 完成任务{task_name}失败! {e}")
            return False

    def get_task_list(self):
        try:
            # 最多尝试3次
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    # 获取签名
                    signature = self.get_signature()
                    res = requests.get(
                        url="https://www.feihevip.com/api/member/signin/getTaskList",
                        headers={**self.headers, **signature},
                        json={},
                        timeout=(5, 30),
                    )
                    res = res.json()

                    if res.get("code") == "200" and len(res.get("data", [])) > 0:
                        print(f"✅ 成功获取 {len(res['data'])} 个任务")
                        return res["data"]
                    else:
                        if attempt < max_retries:
                            # 延迟一段时间后重试
                            time.sleep(2)
                            continue
                except Exception as e:
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    raise e
            return []
        except Exception as e:
            self.ck_status = False
            print(f"⛔️ 获取任务失败! {e}")
            return []

    def signin(self):
        try:
            # 最多尝试3次
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    signature = self.get_signature()
                    _header = {**self.headers, **signature}
                    # 使用正确的签到接口 - POST方法
                    res = requests.post(
                        url="https://www.feihevip.com/api/member/signin/sign",
                        headers=_header,
                        json={},
                        timeout=(5, 30),
                    )
                    print(f"[星妈]今日签到----{res}---")
                    res = res.json()

                    if res.get("code") == "200":
                        print(f"✅ 签到成功!\n")

                        # 获取签到积分信息
                        try:
                            info_res = requests.get(
                                url="https://www.feihevip.com/api/member/signin/getSignInfo?signType=1",
                                headers=_header,
                                json={},
                                timeout=(5, 30),
                            )
                            info_data = info_res.json()
                            print(f"签到结果{info_data}")
                            sign_pop = info_data.get("data", {}).get("signPop")
                            point = sign_pop[0]["signPoint"] if sign_pop else 0
                            print(f"✅ 签到获得积分: {point}分\n")
                        except Exception as e:
                            print(f"⚠️ 获取签到积分信息失败: {str(e)}")

                        return True
                    else:
                        msg = res.get("msg")
                        # print(f"⚠️ 签到失败: {msg}，尝试 {attempt}/{max_retries}")
                        if attempt < max_retries:
                            # 延迟一段时间后重试
                            time.sleep(2)
                            continue
                        return False
                except Exception as e:
                    # print(f"⚠️ 签到请求异常: {str(e)}，尝试 {attempt}/{max_retries}")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    raise e
            return False
        except Exception as e:
            self.ck_status = False
            print(f"⛔️ 执行任务今日签到失败! {e}")
            return False

    def tofinish(self, task_name, task_type):
        try:
            # 最多尝试3次
            max_retries = 2
            for attempt in range(1, max_retries + 1):
                try:
                    signature = self.get_signature()
                    res = requests.get(
                        url=f"https://www.feihevip.com/api/member/signin/tofinish?taskType={task_type}",
                        headers={**self.headers, **signature},
                        json={},
                        timeout=(5, 30),
                    )
                    res = res.json()

                    # print(f'[星妈]执行任务----{task_name}--- 尝试 {attempt}/{max_retries}')

                    if res.get("code") == "200":
                        print(f"🚀 开始执行任务: {task_name}\n")
                        return True
                    else:
                        # print(f"⚠️ 执行任务失败: {res.get('msg')}，尝试 {attempt}/{max_retries}\n")
                        if attempt < max_retries:
                            # 延迟一段时间后重试
                            time.sleep(2)
                            continue
                        return False
                except Exception as e:
                    # print(f"⚠️ 执行任务请求异常: {str(e)}，尝试 {attempt}/{max_retries}")
                    if attempt < max_retries:
                        time.sleep(2)
                        continue
                    raise e
            return False
        except Exception as e:
            self.ck_status = False
            print(f"⛔️ 执行任务{task_name}失败! {e}")
            return False

    """刷新token"""

    def refresh_token(self):
        try:
            signature = self.get_signature2()
            options = {
                "url": "https://mom.feihe.com/program/token/refreshToken",
                "type": "get",
                "headers": {
                    "Host": "mom.feihe.com",
                    "token": self.token,
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.48(0x1800302b) NetType/4G Language/zh_CN",
                    "Referer": "https://servicewechat.com/wx4205ec55b793245e/215/page-frame.html",
                    "fhAppid": "xmh",
                    "source": "1",
                    **signature,
                },
            }

            response = requests.get(
                options["url"], headers=options["headers"], timeout=(5, 30)
            )
            result = response.json()
            new_token = result.get("data")

            if new_token:
                self.token = new_token
                self.headers["token"] = new_token
                print("🎉 刷新 token 成功")
                return new_token

            print("⚠️ 刷新 token 失败，返回数据中无token")
            return None
        except Exception as e:
            print(f"⛔️ 刷新 Token 失败: {e}")
            return None


"""主程序运行"""
try:
    usermessage = sender.getMessage()
except AttributeError:
    usermessage = ""

if re.search(r"星妈登录", usermessage):
    login()
elif re.search(r"星妈管理", usermessage):
    manage()
elif re.search(r"星妈查询", usermessage):
    query_accounts()
elif re.search(r"星妈一键运行", usermessage):
    xm_auto_run()
elif re.search(r"星妈教程", usermessage):
    sender.reply(
        "=====使用教程=====\n"
        "1. 「星妈登录」绑定账号\n"
        "2. 「星妈管理」进行账号授权\n"
        "3. 「星妈一键运行」执行所有账号任务\n"
        "4. 「星妈查询」查看账号状态\n"
        "===================="
    )
elif re.search(r"我的星妈积分$", usermessage):
    query_user_points()
elif re.search(r"星妈授权$", usermessage) and sender.isAdmin():
    admin_authorize_account()
else:
    sender.setContinue()
