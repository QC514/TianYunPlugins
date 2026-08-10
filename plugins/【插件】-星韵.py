# [title: 【插件】-星韵]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: 1603960061] 售后联系方式
# [disable:false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^(星韵|xing yun)(登录|登陆)$|^登(录|陆)(星韵|xingyun)$|^(星韵|xingyun)(查询|管理)$|^(查询|管理)(星韵|xingyun)$|^清理星韵$|^星韵授权$|^星韵清理$|^星韵上传$]
# [priority: 0] 优先级，数字越大表示优先级越高
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [open_source: false]
# [icon: https://i.mji.rip/2025/07/11/2350538ac014afbea48b64409bd5931c.png]图标链接地址，请使用48像素的正方形图标，支持http和https
# [version: 1.0.0]版本号
# [public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 0] 上架价格
# [description: 星韵优选账号管理插件<br><br>指令：星韵登录、星韵管理、星韵查询、星韵授权(管理员)<br><br>功能：多账号管理、授权后自动同步青龙、支持积分/微信支付]

# 插件参数配置
# [param: {"required":false,"key":"G_SKM.zsm","name":"收款码(全局)","placeholder":"http://example.com/pay.jpg","desc":"微信赞赏码/收款码链接"}]
# [param: {"required":false,"key":"G_xy_config.price","name":"月费价格","placeholder":"0.88","value":"0.88"}]
# [param: {"required":false,"key":"G_xy_config.points_per_month","name":"积分/月","placeholder":"100","value":"100","desc":"一个账号每月所需积分数量"}]
# [param: {"required":false,"key":"G_xy_config.ql_config","name":"青龙配置","placeholder":"http://ip:5700丨client_id丨client_secret","desc":"青龙面板地址丨应用ID丨应用密钥"}]
# [param: {"required":false,"key":"G_xy_config.ql_envname","name":"环境变量名","placeholder":"G_XY_TOKEN","value":"G_XY_TOKEN","desc":"青龙环境变量名称"}]

from datetime import datetime, timedelta
import middleware
import time
import json
import re
import requests
import warnings

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# ==================== 常量配置 ====================
BASE_URL = "https://gzpengru.weimbo.com/api/index.php?ackey=GZYTAPPLET"

HEADERS = {
    "Host": "gzpengru.weimbo.com",
    "Connection": "keep-alive",
    "content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-G9810 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/116.0.5845.163 MicroMessenger/8.0.45.2400(0x28002B3D) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64",
    "Referer": "https://servicewechat.com/wxc86c9aecdb67f876/9/page-frame.html",
}

loginMessage = """
=====星韵优选登录=====
请输入您的Token
格式：备注#token 或 直接输入token
------------------
回复「q」退出绑定
=================="""

# 获取发起者数据
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()


# ==================== 公用方法 ====================
def mask_token(token):
    """将token进行脱敏处理"""
    if not token or len(token) < 10:
        return token
    return f"{token[:6]}****{token[-4:]}"


def get_config():
    """动态获取插件配置"""
    try:
        price_str = middleware.bucketGet(bucket="G_xy_config", key="price") or "0.88"
        price = float(price_str) if price_str.replace(".", "", 1).isdigit() else 0.88

        # 使用全局收款码（G_SKM为主，dd_sign_config为备）
        zsm = (
            middleware.bucketGet(bucket="G_SKM", key="zsm")
            or middleware.bucketGet(bucket="dd_sign_config", key="zsm")
            or ""
        )

        points_per_month_str = (
            middleware.bucketGet(bucket="G_xy_config", key="points_per_month") or "100"
        )
        points_per_month = (
            int(points_per_month_str) if points_per_month_str.isdigit() else 100
        )

        ql_config = middleware.bucketGet(bucket="G_xy_config", key="ql_config") or ""
        ql_envname = (
            middleware.bucketGet(bucket="G_xy_config", key="ql_envname") or "G_XY_TOKEN"
        )

        return {
            "price": price,
            "zsm": zsm,
            "points_per_month": points_per_month,
            "ql_config": ql_config,
            "ql_envname": ql_envname,
        }
    except Exception as e:
        sender.reply(f"❌ 配置获取失败: {str(e)}")
        return {
            "price": 0.88,
            "zsm": "",
            "points_per_month": 100,
            "ql_config": "",
            "ql_envname": "G_XY_TOKEN",
        }


def get_user_accounts(user_id=None):
    """获取用户账号列表"""
    target_userid = user_id if user_id else userid
    uservalue = middleware.bucketGet("G_xy_user", target_userid) or "[]"
    user_accounts = []

    if uservalue:
        try:
            accounts_list = json.loads(uservalue)
            if isinstance(accounts_list, list):
                user_accounts = accounts_list
            else:
                user_accounts = [str(accounts_list)]
        except json.JSONDecodeError:
            try:
                accounts_eval = eval(uservalue)
                if isinstance(accounts_eval, (list, tuple, set)):
                    user_accounts = list(accounts_eval)
                elif accounts_eval:
                    user_accounts = [str(accounts_eval)]
            except:
                user_accounts = []

    return [str(acc) for acc in user_accounts if acc]


def validate_token(token):
    """验证token是否有效，返回用户信息"""
    try:
        headers = {
            "Host": "gzpengru.weimbo.com",
            "Connection": "keep-alive",
            "3rdsession": token,
            "content-type": "application/json",
            "User-Agent": HEADERS["User-Agent"],
            "Referer": HEADERS["Referer"],
        }
        payload = {"action": "userInfoData"}
        response = requests.post(
            BASE_URL, headers=headers, json=payload, timeout=15, verify=False
        )
        data = response.json()
        if data and data.get("Status"):
            user_data = data.get("Data", {})
            return {
                "name": user_data.get("user", {}).get("name", "未知"),
                "jifen": user_data.get("u_money", {}).get("jifen", 0),
            }
    except Exception as e:
        print(f"验证token失败: {e}")
    return None


# ==================== 青龙对接函数 ====================
ql_token_cache = {}


def get_ql_token(host: str, client_id: str, client_secret: str) -> str:
    """获取青龙Token（带缓存）"""
    if host in ql_token_cache:
        return ql_token_cache[host]

    try:
        url = f"{host}/open/auth/token"
        params = {"client_id": client_id, "client_secret": client_secret}
        resp = requests.get(url, params=params, timeout=10, verify=False)
        data = resp.json()

        if data.get("code") == 200:
            token = data["data"]["token"]
            ql_token_cache[host] = token
            return token
    except Exception as e:
        print(f"[ERROR] 获取青龙Token失败: {e}")
    return ""


def add_or_update_ql_env(
    host: str, ql_token: str, env_name: str, value: str, remarks: str = ""
) -> bool:
    """添加或更新青龙环境变量"""
    if not host or not ql_token:
        return False

    headers = {
        "Authorization": f"Bearer {ql_token}",
        "Content-Type": "application/json",
    }

    try:
        # 搜索是否存在（通过value中的账号标识搜索）
        search_url = f"{host}/open/envs"
        resp = requests.get(
            search_url,
            headers=headers,
            params={"searchValue": env_name},
            timeout=10,
            verify=False,
        )
        envs = resp.json().get("data", [])

        # 从value中提取账号标识（格式：备注#token，取备注部分）
        account_id = value.split("#")[0] if "#" in value else value[:20]
        existing = None
        for e in envs:
            if e.get("name") == env_name:
                env_remarks = e.get("remarks", "")
                if f"星韵:{account_id}" in env_remarks:
                    existing = e
                    break

        if existing:
            # 更新
            update_url = f"{host}/open/envs"
            env_id = existing.get("id") or existing.get("_id")
            data = {"id": env_id, "name": env_name, "value": value, "remarks": remarks}
            requests.put(
                update_url, headers=headers, json=data, timeout=10, verify=False
            )
        else:
            # 新增
            add_url = f"{host}/open/envs"
            data = [{"name": env_name, "value": value, "remarks": remarks}]
            requests.post(add_url, headers=headers, json=data, timeout=10, verify=False)

        return True
    except Exception as e:
        print(f"[ERROR] 青龙操作失败: {e}")
    return False


def delete_ql_env(host: str, ql_token: str, env_name: str, account_id: str) -> bool:
    """删除青龙环境变量"""
    if not host or not ql_token:
        return False

    headers = {
        "Authorization": f"Bearer {ql_token}",
        "Content-Type": "application/json",
    }

    try:
        search_url = f"{host}/open/envs"
        resp = requests.get(
            search_url,
            headers=headers,
            params={"searchValue": env_name},
            timeout=10,
            verify=False,
        )
        envs = resp.json().get("data", [])

        for env in envs:
            if env.get("name") == env_name:
                env_remarks = env.get("remarks", "")
                if f"星韵:{account_id}" in env_remarks:
                    delete_url = f"{host}/open/envs"
                    env_id = env.get("id") or env.get("_id")
                    requests.delete(
                        delete_url,
                        headers=headers,
                        json=[env_id],
                        timeout=10,
                        verify=False,
                    )
                    return True
    except Exception as e:
        print(f"[ERROR] 删除青龙变量失败: {e}")
    return False


def sync_to_qinglong(account_id):
    """单个账号同步到青龙（授权后自动调用）"""
    config = get_config()
    ql_config_str = config.get("ql_config", "")
    ql_envname = config.get("ql_envname", "G_XY_TOKEN")

    if not ql_config_str:
        print(f"[INFO] 未配置青龙面板，跳过自动上传")
        return {"success": False, "reason": "未配置青龙"}

    # 解析青龙配置
    sep = "丨" if "丨" in ql_config_str else "|" if "|" in ql_config_str else None
    if not sep:
        return {"success": False, "reason": "青龙配置格式错误"}

    parts = ql_config_str.split(sep)
    if len(parts) != 3:
        return {"success": False, "reason": "青龙配置不完整"}

    host, client_id, client_secret = (
        parts[0].rstrip("/"),
        parts[1].strip(),
        parts[2].strip(),
    )

    # 获取青龙Token
    ql_token = get_ql_token(host, client_id, client_secret)
    if not ql_token:
        return {"success": False, "reason": "获取青龙Token失败"}

    # 获取账号token
    token = middleware.bucketGet("G_xy_token", account_id)
    if not token:
        return {"success": False, "reason": "账号Token不存在"}

    # 获取授权信息
    auth_data_str = middleware.bucketGet("G_xy_auth", account_id)
    expire_date = ""
    acc_userid = userid
    if auth_data_str:
        try:
            auth_data = json.loads(auth_data_str)
            expire_date = auth_data.get("expire_time", "")
            acc_userid = auth_data.get("userid", userid)
        except:
            pass

    # 构建环境变量值：备注#token
    env_value = f"{account_id}#{token}"

    # 构建备注
    remarks = f"星韵:{account_id}|用户:{acc_userid}|到期:{expire_date}"

    if add_or_update_ql_env(host, ql_token, ql_envname, env_value, remarks):
        return {"success": True, "reason": "上传成功"}
    else:
        return {"success": False, "reason": "上传失败"}


# ==================== 登录功能 ====================
def login():
    """用户登录"""
    sender.reply(loginMessage)
    user_input = sender.input(120000, 1, False)

    if user_input is None:
        sender.reply("⏰ 输入超时，已退出")
        return

    user_input = user_input.strip()

    if user_input.lower() == "q":
        sender.reply("✅ 已退出登录")
        return

    # 解析token格式：备注#token 或 直接token
    parts = user_input.split("#")
    if len(parts) >= 2:
        remark = parts[0]
        token = parts[1]
    else:
        remark = ""
        token = parts[0]

    # 验证token是否有效
    user_info = validate_token(token)
    if user_info:
        user_name = user_info.get("name", "")
        account_id = (
            remark if remark else user_name if user_name else f"用户_{int(time.time())}"
        )
        save_account_info(account_id, token)
    else:
        sender.reply(f"⚠️ token有误或者token过期了，请重新检查")
        return


def save_account_info(account_id, token):
    """保存账号信息"""
    accounts = get_user_accounts()

    if account_id not in accounts:
        accounts.append(account_id)
        middleware.bucketSet("G_xy_user", userid, json.dumps(accounts))

    middleware.bucketSet("G_xy_token", account_id, token)
    success_msg = f"""
=====登录成功=====
📱 账号: {account_id}
✅ 状态: 添加成功
------------------
发送"星韵管理"管理账号
发送"星韵查询"查询账号
💡 授权后自动同步青龙"""
    sender.reply(success_msg)


# ==================== 查询功能 ====================
def query_accounts():
    """查询所有账号"""
    today = str(datetime.now().date())
    accounts = get_user_accounts()

    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先使用「星韵登录」绑定")
        return

    account_info_list = []

    for account in accounts:
        account_info = query_accounts_for_item(account, today)
        if account_info:
            account_info_list.append(account_info)

    final_msg = "=====星韵账号信息汇总=====" + "".join(account_info_list) + "\n"
    sender.reply(final_msg)


def query_accounts_for_item(account, today):
    """获取单个账号信息"""
    token = middleware.bucketGet("G_xy_token", account)
    if not token:
        return None

    user_info = validate_token(token)
    if user_info:
        jifen = user_info.get("jifen", 0)
        user_name = user_info.get("name", "未知")

        auth_data_str = middleware.bucketGet("G_xy_auth", account)
        if not auth_data_str:
            auth_status = "授权: ❌ 未授权"
        else:
            try:
                auth_data = json.loads(auth_data_str)
                expire_date = auth_data.get("expire_time")
                auth_status = (
                    f"到期时间: {expire_date}"
                    if expire_date and expire_date > today
                    else "授权: ❌ 已过期"
                )
            except:
                auth_status = "授权: ❌ 数据异常"

        return f"""
📱 账号: {account}
👤 昵称: {user_name}
💰 积分: {jifen}
🔐 {auth_status}
=================="""
    else:
        return f"""
📱 账号: {account}
❌ 登录态异常，请重新抓取
=================="""


# ==================== 积分相关 ====================
def safe_int(value, default=0):
    """安全的整数转换"""
    if not value:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.isdigit():
        return int(value)
    return default


def get_user_points(target_userid=None):
    """获取用户积分值"""
    if not target_userid:
        target_userid = userid

    points = middleware.bucketGet("dd_sign_coin", target_userid) or "0"
    user_points = middleware.bucketGet("dd_sign_points", target_userid) or "0"

    result_points = {
        "dd_sign_coin": safe_int(points),
        "dd_sign_points": safe_int(user_points),
        "total": safe_int(points) + safe_int(user_points),
    }

    if points == "0":
        sign_key = f"sign_{target_userid}"
        sign_points = middleware.bucketGet("dd_sign_coin", sign_key)
        if sign_points:
            result_points["dd_sign_coin"] = safe_int(sign_points)
            result_points["total"] = safe_int(sign_points) + safe_int(user_points)

    return result_points


def set_user_points(target_userid, points):
    """设置用户积分"""
    middleware.bucketSet("dd_sign_coin", target_userid, str(points["dd_sign_coin"]))
    middleware.bucketSet("dd_sign_points", target_userid, str(points["dd_sign_points"]))

    sign_key = f"sign_{target_userid}"
    middleware.bucketSet("dd_sign_coin", sign_key, str(points["dd_sign_coin"]))
    return True


# ==================== 管理功能 ====================
def manage():
    """账号管理"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先绑定")
        return

    # 统计授权状态
    authorized_count = 0
    unauthorized_accounts = []
    for account_id in accounts:
        auth_data = middleware.bucketGet("G_xy_auth", key=account_id)
        if auth_data:
            try:
                auth_info = json.loads(auth_data)
                expire_date = auth_info.get("expire_time", "")
                if expire_date >= str(datetime.now().date()):
                    authorized_count += 1
                else:
                    unauthorized_accounts.append(account_id)
            except:
                unauthorized_accounts.append(account_id)
        else:
            unauthorized_accounts.append(account_id)

    # 构建账号列表
    account_list = []
    for i, account_id in enumerate(accounts, 1):
        auth_data = middleware.bucketGet("G_xy_auth", key=account_id)
        status = "✅"
        status_text = "已授权"
        if auth_data:
            try:
                auth_info = json.loads(auth_data)
                expire_date = auth_info.get("expire_time", "")
                if expire_date < str(datetime.now().date()):
                    status = "❌"
                    status_text = "已过期"
            except:
                status = "❌"
                status_text = "未授权"
        else:
            status = "❌"
            status_text = "未授权"

        account_list.append(f"[{i}] 📱 {account_id} {status}{status_text}")

    if accounts:
        account_list.append("\n[0] 所有账号授权（支付）")
    if unauthorized_accounts:
        account_list.append("[9999] 未授权账号批量授权（支付）")

    account_list_str = "\n".join(account_list)

    user_points = get_user_points()

    sender.reply(f"""
=====星韵账号管理=====
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
    if choice is None:
        sender.reply("⏰ 输入超时，已退出")
        return

    if choice.lower() == "q":
        sender.reply("已退出管理")
        return

    if choice == "0":
        sender.reply("您选择了所有账号授权")
        for account_id in accounts:
            authorize_account(account_id)
        return
    elif choice == "9999":
        sender.reply("您选择了未授权账号批量授权")
        for account_id in unauthorized_accounts:
            authorize_account(account_id)
        return
    elif not choice.isdigit():
        sender.reply("❌ 输入无效，请重新选择")
        manage()
        return

    selected_idx = int(choice) - 1
    if selected_idx < 0 or selected_idx >= len(accounts):
        sender.reply("❌ 序号无效，请重新选择")
        manage()
        return

    selected_account = accounts[selected_idx]
    sender.reply(f"你选择了账号: {selected_account}\n[1] 授权账号\n[2] 删除账号")
    op = sender.input(60000, 1, False)

    if op == "1":
        authorize_account(selected_account)
    elif op == "2":
        delete_account(selected_account)


# ==================== 授权功能 ====================
def authorize_account(account_id):
    """授权账号并处理支付"""
    config = get_config()

    access_token = middleware.bucketGet("G_xy_token", account_id)
    if not access_token:
        sender.reply("❌ 账号令牌无效，无法授权")
        return

    current_points = get_user_points()

    sender.reply(
        f"您正在授权账号: {account_id}\n📊 当前积分: {current_points['total']}\n\n请输入授权月数 (1-12):"
    )

    months = sender.input(120000, 1, False)

    if not months.isdigit() or int(months) < 1 or int(months) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return

    months = int(months)
    total_price = config["price"] * months
    required_points = config["points_per_month"] * months

    pay_menu = f"""
=====星韵优选授权支付=====
📱 账号: {account_id}
🎯 授权时长: {months}个月
💰 金额: ¥{total_price:.2f}
📊 积分支付: {required_points}积分（当前积分: {current_points["total"]}）
------------------
[1] 微信支付
[2] 积分支付
回复数字选择支付方式，回复q取消
=================="""
    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False)

    if pay_choice == "1" and config["zsm"]:
        payment_success = wechat_payment_flow(account_id, months, total_price, config)
    elif pay_choice == "2":
        payment_success = point_payment_flow(
            account_id, months, required_points, config
        )
    elif pay_choice.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    else:
        sender.reply("❌ 无效支付方式")
        return

    if payment_success:
        auth_result = complete_authorization(account_id, months)

        # 构建青龙同步状态提示
        ql_sync = auth_result.get("ql_sync", {})
        if ql_sync.get("success"):
            ql_msg = "🐉 青龙同步: ✅ 已自动上传"
        else:
            ql_reason = ql_sync.get("reason", "未知")
            ql_msg = f"🐉 青龙同步: ❌ {ql_reason}"

        sender.reply(
            f"✅ {auth_result['renew_type']}成功！\n"
            f"📅 到期日期: {auth_result['expire_date']}（{months}个月）\n"
            f"{ql_msg}"
        )


def wechat_payment_flow(account_id, months, amount, config):
    """微信支付处理"""
    sender.reply(f"""
=====微信扫码支付=====
📱 账号: {account_id}
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


def point_payment_flow(account_id, months, required_points, config):
    """积分支付处理"""
    user_points = get_user_points()
    sign_coin = user_points["dd_sign_coin"]
    sign_points = user_points["dd_sign_points"]

    if user_points["total"] < required_points:
        sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points["total"]}积分
请「联系管理员」充值积分
        """)
        return False

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

    if sign_coin >= required_points:
        sign_coin -= required_points
    else:
        remaining = required_points - sign_coin
        sign_coin = 0
        sign_points -= remaining

    result_points = {
        "dd_sign_coin": sign_coin,
        "dd_sign_points": sign_points,
    }

    new_points = sign_points + sign_coin
    set_user_points(userid, result_points)

    transaction_data = {
        "userid": userid,
        "account_id": account_id,
        "months": months,
        "points": required_points,
        "balance": new_points,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "星韵优选授权",
    }
    middleware.bucketSet(
        "dd_sign_transactions", f"tx_{int(time.time())}", json.dumps(transaction_data)
    )

    sender.reply(f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {new_points}")
    return True


def parse_payment_result(raw_data):
    """解析微信支付结果"""
    Money, Time, From = None, "", ""

    try:
        if isinstance(raw_data, dict):
            if raw_data.get("type") in ["微信赞赏", "微信收款"]:
                Money = float(raw_data.get("money", 0))
                Time = raw_data.get("time", "")
                From = raw_data.get("from_name", "")
            else:
                Money = float(raw_data.get("Money", 0))
                Time = raw_data.get("Time", "")
        else:
            try:
                data = json.loads(raw_data)
                if data.get("type") in ["微信赞赏", "微信收款"]:
                    Money = float(data.get("money", 0))
                    Time = data.get("time", "")
                    From = data.get("from_name", "")
            except:
                if "二维码赞赏到账" in raw_data:
                    try:
                        amount_str = raw_data.split("收款金额￥")[1].split("\n")[0]
                        time_str = raw_data.split("到账时间")[1].split("\n")[0].strip()
                        Money = float(amount_str)
                        Time = time_str
                    except:
                        pass
    except Exception as e:
        sender.reply(f"❌ 解析支付结果失败: {str(e)}")

    return Money, Time, From


def complete_authorization(account_id, months):
    """完成授权并记录"""
    existing_auth = middleware.bucketGet("G_xy_auth", account_id)

    new_expire_time = None
    renew_msg = "新授权"

    if existing_auth:
        try:
            auth_info = json.loads(existing_auth)
            try:
                expire_time = datetime.strptime(auth_info["expire_time"], "%Y-%m-%d")
            except:
                try:
                    expire_time = datetime.fromtimestamp(
                        float(auth_info["expire_time"])
                    )
                except:
                    expire_time = datetime.now()

            if expire_time.date() >= datetime.now().date():
                new_expire_time = expire_time + timedelta(days=months * 30)
                renew_msg = "续费"
            else:
                new_expire_time = datetime.now() + timedelta(days=months * 30)
                renew_msg = "新授权"
        except Exception as e:
            print(f"[WARN] 解析现有授权信息失败: {str(e)}")

    if not new_expire_time:
        new_expire_time = datetime.now() + timedelta(days=months * 30)
        renew_msg = "新授权"

    expire_date = new_expire_time.date().strftime("%Y-%m-%d")

    auth_data = {
        "userid": userid,
        "account_id": account_id,
        "expire_time": expire_date,
        "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "authorized_months": months,
        "is_renewal": renew_msg,
    }

    middleware.bucketSet(
        bucket="G_xy_auth", key=account_id, value=json.dumps(auth_data)
    )

    # 授权成功后自动上传青龙
    ql_result = sync_to_qinglong(account_id)

    return {"expire_date": expire_date, "renew_type": renew_msg, "ql_sync": ql_result}


def delete_account(account_id):
    """删除账号"""
    accounts = get_user_accounts()

    sender.reply(f"""
=====删除账号确认=====
确认删除账号 {account_id} 吗？
请回复 [Y] 确认
回复 [N] 取消
==================""")
    user_confirm = sender.input(120000, 1, False)

    if user_confirm is None:
        sender.reply("⏰ 输入超时，已退出")
        return

    if user_confirm.strip().lower() != "y":
        sender.reply("✅ 已取消删除操作")
        return

    try:
        # 先同步删除青龙变量
        config = get_config()
        ql_config_str = config.get("ql_config", "")
        if ql_config_str:
            sep = (
                "丨" if "丨" in ql_config_str else "|" if "|" in ql_config_str else None
            )
            if sep:
                parts = ql_config_str.split(sep)
                if len(parts) == 3:
                    host = parts[0].rstrip("/")
                    client_id = parts[1].strip()
                    client_secret = parts[2].strip()
                    ql_token = get_ql_token(host, client_id, client_secret)
                    if ql_token:
                        ql_envname = config.get("ql_envname", "G_XY_TOKEN")
                        delete_ql_env(host, ql_token, ql_envname, account_id)

        middleware.bucketDel(bucket="G_xy_token", key=account_id)
        middleware.bucketDel(bucket="G_xy_auth", key=account_id)

        if account_id in accounts:
            accounts.remove(account_id)
            if accounts:
                middleware.bucketSet(
                    bucket="G_xy_user", key=userid, value=json.dumps(accounts)
                )
            else:
                middleware.bucketDel(bucket="G_xy_user", key=userid)

        sender.reply("✅ 账号删除成功（已同步删除青龙变量）")

    except Exception as e:
        sender.reply(f"❌ 删除失败: {str(e)}")


# ==================== 上传青龙功能 ====================
def upload_to_qinglong():
    """上传Token到青龙面板"""
    if not sender.isAdmin():
        sender.reply("❌ 仅管理员可使用上传功能")
        return

    config = get_config()
    ql_config_str = config.get("ql_config", "")
    ql_envname = config.get("ql_envname", "G_XY_TOKEN")

    if not ql_config_str:
        sender.reply("❌ 未配置青龙面板，请在插件参数中配置")
        return

    # 解析青龙配置
    sep = "丨" if "丨" in ql_config_str else "|" if "|" in ql_config_str else None
    if not sep:
        sender.reply(
            "❌ 青龙配置格式错误，应为：http://ip:5700丨client_id丨client_secret"
        )
        return

    parts = ql_config_str.split(sep)
    if len(parts) != 3:
        sender.reply("❌ 青龙配置格式错误，需要3部分：地址丨ID丨密钥")
        return

    host, client_id, client_secret = (
        parts[0].rstrip("/"),
        parts[1].strip(),
        parts[2].strip(),
    )

    # 获取青龙Token
    ql_token = get_ql_token(host, client_id, client_secret)
    if not ql_token:
        sender.reply("❌ 获取青龙Token失败，请检查配置")
        return

    sender.reply("正在获取已授权账号...")

    # 收集已授权账号
    authorized_accounts = []
    auth_keys = middleware.bucketAllKeys(bucket="G_xy_auth") or []

    for account_id in auth_keys:
        auth_data_str = middleware.bucketGet("G_xy_auth", key=account_id)
        if not auth_data_str:
            continue

        try:
            auth_data = json.loads(auth_data_str)
            expire_date = auth_data.get("expire_time")

            if expire_date:
                try:
                    expire_date_obj = datetime.strptime(expire_date, "%Y-%m-%d").date()
                    if datetime.now().date() <= expire_date_obj:
                        authorized_accounts.append(
                            {
                                "account_id": account_id,
                                "expire_date": expire_date,
                                "userid": auth_data.get("userid", ""),
                            }
                        )
                except:
                    pass
        except:
            pass

    if not authorized_accounts:
        sender.reply("❌ 没有已授权的账号可上传")
        return

    sender.reply(f"找到 {len(authorized_accounts)} 个已授权账号，开始上传...")

    # 上传到青龙
    success_count = 0
    fail_count = 0

    for acc in authorized_accounts:
        account_id = acc["account_id"]
        expire_date = acc["expire_date"]
        acc_userid = acc["userid"]

        token = middleware.bucketGet("G_xy_token", account_id)
        if not token:
            fail_count += 1
            continue

        # 构建环境变量值：备注#token
        env_value = f"{account_id}#{token}"

        # 构建备注：星韵:account_id|用户:wxid|到期:YYYY-MM-DD
        remarks = f"星韵:{account_id}|用户:{acc_userid}|到期:{expire_date}"

        if add_or_update_ql_env(host, ql_token, ql_envname, env_value, remarks):
            success_count += 1
        else:
            fail_count += 1

    sender.reply(f"""
=====星韵上传完成=====
📊 已授权账号: {len(authorized_accounts)}个
✅ 上传成功: {success_count}个
❌ 上传失败: {fail_count}个
📋 变量名: {ql_envname}
------------------
💡 青龙脚本将自动读取变量执行任务
==================""")


# ==================== 管理员功能 ====================
def admin_authorize_account():
    """管理员授权"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限！")
        return

    sender.reply(
        "=====管理员授权操作=====\n"
        "[1] 一键授权所有用户\n"
        "[2] 单独授权用户\n"
        "回复数字选择操作\n"
        "===================="
    )
    choice = sender.input(60000, 1, False)

    if choice == "1":
        users = middleware.bucketAllKeys(bucket="G_xy_user")
        if not users:
            sender.reply("❌ 未找到任何绑定用户")
            return

        sender.reply("请输入授权月数 (1-12):")
        months = sender.input(120000, 1, False)
        if not months or not months.isdigit() or int(months) < 1 or int(months) > 12:
            sender.reply("❌ 月数必须为1-12之间的整数")
            return
        months = int(months)

        success_count = 0
        ql_success_count = 0
        for user in users:
            accounts = get_user_accounts(user)
            for account_id in accounts:
                try:
                    expire_time = datetime.now() + timedelta(days=months * 30)

                    auth_data = {
                        "userid": user,
                        "account_id": account_id,
                        "expire_time": str(expire_time.date()),
                        "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "authorized_months": months,
                        "payment_type": "管理员免费授权",
                    }

                    middleware.bucketSet(
                        bucket="G_xy_auth", key=account_id, value=json.dumps(auth_data)
                    )
                    success_count += 1

                    # 同步到青龙
                    ql_result = sync_to_qinglong(account_id)
                    if ql_result.get("success"):
                        ql_success_count += 1

                except Exception as e:
                    sender.reply(f"❌ 授权用户 {user} 失败: {str(e)}")

        sender.reply(
            f"✅ 一键授权完成！\n📊 成功授权: {success_count} 个账号\n🐉 青龙同步: {ql_success_count} 个"
        )

    elif choice == "2":
        sender.reply("请输入需要授权的用户ID:")
        target_userid = sender.input(120000, 1, False)
        if not target_userid:
            sender.reply("❌ 用户ID无效")
            return

        accounts = get_user_accounts(target_userid)
        if not accounts:
            sender.reply(f"❌ 用户 {target_userid} 未绑定任何星韵账号")
            return

        account_lines = []
        for i, account_id in enumerate(accounts, 1):
            account_lines.append(f"[{i}] {account_id}")

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
            sender.reply("请输入授权月数 (1-12):")
            months = sender.input(120000, 1, False)
            if (
                not months
                or not months.isdigit()
                or int(months) < 1
                or int(months) > 12
            ):
                sender.reply("❌ 月数必须为1-12之间的整数")
                return
            months = int(months)

            success_count = 0
            ql_success_count = 0
            for account_id in accounts:
                try:
                    expire_time = datetime.now() + timedelta(days=months * 30)

                    auth_data = {
                        "userid": target_userid,
                        "account_id": account_id,
                        "expire_time": str(expire_time.date()),
                        "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "authorized_months": months,
                        "payment_type": "管理员免费授权",
                    }

                    middleware.bucketSet(
                        bucket="G_xy_auth", key=account_id, value=json.dumps(auth_data)
                    )
                    success_count += 1

                    # 同步到青龙
                    ql_result = sync_to_qinglong(account_id)
                    if ql_result.get("success"):
                        ql_success_count += 1

                except Exception as e:
                    sender.reply(f"❌ 授权账号失败: {str(e)}")

            sender.reply(
                f"✅ 成功授权该用户所有账号（{success_count}个）\n🐉 青龙同步: {ql_success_count} 个"
            )

        elif account_choice and account_choice.isdigit():
            selected_idx = int(account_choice) - 1
            if selected_idx < 0 or selected_idx >= len(accounts):
                sender.reply("❌ 序号无效")
                return

            account_id = accounts[selected_idx]

            sender.reply(f"您选择了账号: {account_id}\n请输入授权月数 (1-12):")
            months = sender.input(120000, 1, False)
            if (
                not months
                or not months.isdigit()
                or int(months) < 1
                or int(months) > 12
            ):
                sender.reply("❌ 月数必须为1-12之间的整数")
                return
            months = int(months)

            expire_time = datetime.now() + timedelta(days=months * 30)

            auth_data = {
                "userid": target_userid,
                "account_id": account_id,
                "expire_time": str(expire_time.date()),
                "authorized_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "authorized_months": months,
                "payment_type": "管理员免费授权",
            }

            middleware.bucketSet(
                bucket="G_xy_auth", key=account_id, value=json.dumps(auth_data)
            )

            # 同步到青龙
            ql_result = sync_to_qinglong(account_id)
            ql_msg = (
                "✅ 已同步"
                if ql_result.get("success")
                else f"❌ {ql_result.get('reason', '失败')}"
            )

            sender.reply(
                f"✅ 授权成功！账号 {account_id} 已授权 {months}个月\n🐉 青龙同步: {ql_msg}"
            )

        else:
            sender.reply("❌ 无效选择")
    else:
        sender.reply("❌ 无效选择")


def clear_accounts():
    """清理账号数据"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 您没有绑定任何账号")
        return

    sender.reply(f"""
=====清理星韵数据=====
⚠️ 警告：此操作将清除您的所有星韵账号数据
当前绑定账号数：{len(accounts)}个
------------------
回复 [Y] 确认清理
回复 [N] 取消
==================""")

    confirm = sender.input(60000, 1, False).lower()
    if confirm != "y":
        sender.reply("✅ 已取消清理操作")
        return

    try:
        for account_id in accounts:
            middleware.bucketDel(bucket="G_xy_token", key=account_id)
            middleware.bucketDel(bucket="G_xy_auth", key=account_id)

        middleware.bucketDel(bucket="G_xy_user", key=userid)

        sender.reply(f"✅ 已清理 {len(accounts)} 个账号数据")
    except Exception as e:
        sender.reply(f"❌ 清理失败: {str(e)}")


# ==================== 主程序入口 ====================
try:
    usermessage = sender.getMessage()
except AttributeError:
    usermessage = ""

if re.search(r"星韵登录|星韵登陆", usermessage):
    login()
elif re.search(r"星韵管理", usermessage):
    manage()
elif re.search(r"星韵查询", usermessage):
    query_accounts()
elif re.search(r"星韵上传", usermessage):
    upload_to_qinglong()
elif re.search(r"星韵教程", usermessage):
    sender.reply(
        "=====星韵优选使用教程=====\n"
        "1. 「星韵登录」绑定账号\n"
        "   格式：备注#token 或 直接输入token\n"
        "2. 「星韵管理」进行账号授权\n"
        "   授权成功后自动同步到青龙面板\n"
        "3. 「星韵查询」查看账号状态\n"
        "4. 「星韵上传」手动上传到青龙(管理员)\n"
        "===================="
    )
elif re.search(r"星韵授权$", usermessage) and sender.isAdmin():
    admin_authorize_account()
elif re.search(r"清理星韵|星韵清理", usermessage):
    clear_accounts()
else:
    sender.setContinue()
