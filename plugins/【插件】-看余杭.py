# [rule: ^看余杭登录$|^看余杭绑定$|^看余杭管理$|^看余杭查询$|^看余杭授权$|^看余杭教程$|^看余杭中奖记录$]
# [disable:false]
# [platform: qq,wx]
# [public:true]
# [title: 【插件】-看余杭]
# [open_source: false]
# [class: 工具类]
# [version: 1.2.2]
# [price: 6.6]
# [admin: false]
# [icon: https://i.mji.rip/2025/07/11/c15f6ee61d307572a981010a53fbb572.png]  # 替换为实际图标URL
# [author: huawei]
# [service: 1603960061]
# [description: 看余杭APP插件<br>适配呆呆积分支付<br><br>指令：<br>看余杭登录：绑定账号<br>看余杭管理：账号管理与授权<br>看余杭查询：查询状态<br>看余杭授权：管理员授权操作<br>看余杭教程：使用指南]

# 插件参数配置
# [param: {"required":false,"key":"G_kyh_config.zsm","name":"收款码","placeholder":"http://example.com/pay.jpg"}]
# [param: {"required":false,"key":"G_kyh_config.price","name":"月费价格","placeholder":"0.88"}]
# [param: {"required":false,"key":"G_kyh_config.points_per_month","name":"积分/月","placeholder":"100","value":"100","desc":"一个账号每月所需积分数量"}]
# [param: {"required":false,"key":"G_kyh_config.ql_config","name":"青龙配置","placeholder":"http://ip:port丨ClientID丨ClientSecret"}]
# [param: {"required":false,"key":"G_kyh_config.ql_envname","name":"变量名称","placeholder":"G_kyh","value":"G_kyh"}]

import requests
import json
import time
import hashlib
import uuid
import re
from datetime import datetime, timedelta
import middleware

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()


def get_config():
    """动态获取插件配置"""
    try:
        ql_config = middleware.bucketGet(bucket="G_kyh_config", key="ql_config") or ""
        ql_envname = (
            middleware.bucketGet(bucket="G_kyh_config", key="ql_envname") or "G_kyh"
        )
        price_str = middleware.bucketGet(bucket="G_kyh_config", key="price") or "0.88"
        price = float(price_str) if price_str.replace(".", "", 1).isdigit() else 0.88
        zsm = middleware.bucketGet(bucket="G_kyh_config", key="zsm") or ""
        points_per_month_str = (
            middleware.bucketGet(bucket="G_kyh_config", key="points_per_month") or "100"
        )
        points_per_month = (
            int(points_per_month_str) if points_per_month_str.isdigit() else 100
        )

        return {
            "ql_config": ql_config,
            "ql_envname": ql_envname,
            "price": price,
            "zsm": zsm,
            "points_per_month": points_per_month,
        }
    except Exception as e:
        sender.reply(f"❌ 配置获取失败: {str(e)}")
        return {
            "ql_config": "",
            "ql_envname": "G_kyh",
            "price": 0.88,
            "zsm": "",
            "points_per_month": 100,
        }


def get_user_points(user_id=None):
    """获取用户积分"""
    if not user_id:
        user_id = userid

    # 从图片数据结构获取积分
    points = middleware.bucketGet("dd_sign_coin", user_id) or "0"
    user_points = middleware.bucketGet("dd_sign_points", user_id) or "0"

    # 如果查询不到积分，尝试从带sign前缀的key获取
    if points == "0":
        sign_key = f"sign_{user_id}"
        sign_points = middleware.bucketGet("dd_sign_coin", sign_key)
        if sign_points:
            points = sign_points

    result_points = {
        "dd_sign_coin": int(points),
        "dd_sign_points": int(user_points),
        "total": int(points) + int(user_points),
    }

    return result_points


def set_user_points(user_id, points):
    """设置用户积分"""
    middleware.bucketSet("dd_sign_coin", user_id, str(points["dd_sign_coin"]))
    middleware.bucketSet("dd_sign_points", user_id, str(points["dd_sign_points"]))

    # 同时更新带sign_前缀的key
    sign_key = f"sign_{user_id}"
    middleware.bucketSet("dd_sign_coin", sign_key, str(points["dd_sign_coin"]))
    return True


def query_user_points():
    """查询用户积分"""
    points = get_user_points()
    config = get_config()

    sender.reply(
        f"📊 您的当前积分: {points['total']}\n"
        f"💰 每账号每月积分: {config['points_per_month']}\n"
        f"👉 联系管理员可充值积分"
    )


def parse_payment_result(raw_data):
    """解析支付结果"""
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


def update_qinglong_env(token, account_info):
    """更新青龙面板环境变量"""
    config = get_config()
    if not config["ql_config"]:
        return False

    try:
        # 解析青龙配置
        ql_url, client_id, client_secret = config["ql_config"].split("丨")

        # 1. 获取token
        auth_url = f"{ql_url}/open/auth/token"
        auth_params = {"client_id": client_id, "client_secret": client_secret}
        auth_resp = requests.get(auth_url, params=auth_params)
        if auth_resp.status_code != 200:
            return False

        ql_token = auth_resp.json()["data"]["token"]

        # 2. 查找已存在的变量
        headers = {"Authorization": f"Bearer {ql_token}"}
        env_url = f"{ql_url}/open/envs"
        env_resp = requests.get(env_url, headers=headers)

        if env_resp.status_code != 200:
            return False

        envs = env_resp.json()["data"]
        env_name = config["ql_envname"]
        matching_env = None

        # 查找是否存在相同手机号的变量
        phone = account_info["phone"]
        for env in envs:
            if env["name"] == env_name:
                # 检查备注中是否包含相同的手机号
                if env.get("remarks") and f"看余杭：{phone}" in env["remarks"]:
                    matching_env = env
                    break

        # 构建备注信息
        expire_date = (
            account_info["auth_status"]["expire_time"]
            if account_info["auth_status"]["is_authorized"]
            else "未授权"
        )
        remarks = f"看余杭：{account_info['phone']} | 微信：{account_info['wx_id']} | 到期时间：{expire_date}"

        # 构建变量值格式: 备注#TOKEN#UID#DEVICEID (备注=手机号) - 适配看余杭脚本
        uid = account_info.get("uid", "")
        device_id = account_info.get("device_id", "")
        env_value = f"{account_info['phone']}#{token}#{uid}#{device_id}"

        if matching_env:
            # 更新已存在的变量
            update_data = {
                "id": matching_env["id"],
                "name": env_name,
                "value": env_value,
                "remarks": remarks,
            }
            requests.put(env_url, headers=headers, json=update_data)
        else:
            # 创建新变量
            create_data = [{"name": env_name, "value": env_value, "remarks": remarks}]
            requests.post(env_url, headers=headers, json=create_data)

        return True
    except Exception as e:
        print(f"更新青龙变量失败: {str(e)}")
        return False


def point_payment_flow(account_id, months, required_points, phone):
    """积分支付处理"""
    user_points = get_user_points()

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

    # 优先扣除签到积分
    sign_coin = user_points["dd_sign_coin"]
    sign_points = user_points["dd_sign_points"]

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

    # 扣除积分
    set_user_points(userid, result_points)

    # 记录交易
    transaction_data = {
        "userid": userid,
        "account_id": account_id,
        "months": months,
        "points": required_points,
        "balance": sign_points + sign_coin,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "看余杭授权",
    }
    middleware.bucketSet(
        "dd_sign_transactions", f"tx_{int(time.time())}", json.dumps(transaction_data)
    )

    sender.reply(
        f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {sign_points + sign_coin}"
    )
    return True


def wechat_payment_flow(account_id, months, amount, config, phone):
    """微信支付处理"""
    sender.reply(f"""
=====微信扫码支付=====
📱 手机号: {phone}
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


def authorize_account(account_id):
    """授权账号并处理支付"""
    # 获取账号数据
    account_data = middleware.bucketGet("G_kyh_accounts", account_id)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return

    account_info = json.loads(account_data)
    phone = account_info["phone"]
    token = account_info["token"]

    if not token:
        sender.reply("❌ 账号token无效")
        return

    config = get_config()
    current_points = get_user_points()

    sender.reply(f"""
您正在授权账号: {account_id}
📱 手机号: {phone}
📊 当前积分: {current_points["total"]}

请输入授权月数 (1-12):""")

    months = sender.input(120000, 1, False)
    if not months.isdigit() or int(months) < 1 or int(months) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return

    months = int(months)
    total_price = config["price"] * months
    required_points = config["points_per_month"] * months

    pay_menu = f"""
=====看余杭授权支付=====
📱 手机号: {phone}
🎯 授权时长: {months}个月
💰 金额: ¥{total_price:.2f}
📊 积分支付: {required_points}积分（当前积分: {current_points["total"]}）
------------------
[1] 微信支付
[2] 积分支付
回复数字选择支付方式，回复q取消
==================="""

    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False)

    payment_success = False
    if pay_choice == "1" and config["zsm"]:
        payment_success = wechat_payment_flow(
            account_id, months, total_price, config, phone
        )
    elif pay_choice == "2":
        payment_success = point_payment_flow(account_id, months, required_points, phone)
    elif pay_choice.lower() == "q":
        sender.reply("✅ 已取消授权")
        return
    else:
        sender.reply("❌ 无效支付方式")
        return

    if payment_success:
        # 计算新的到期时间
        new_expire_time = None
        if (
            account_info["auth_status"]["is_authorized"]
            and account_info["auth_status"]["expire_time"]
        ):
            try:
                current_expire = datetime.strptime(
                    account_info["auth_status"]["expire_time"], "%Y-%m-%d"
                )
                # 如果当前授权未过期，则从到期时间开始计算新的到期时间
                if current_expire.date() >= datetime.now().date():
                    new_expire_time = current_expire + timedelta(days=months * 30)
                else:
                    # 已过期，从今天开始计算
                    new_expire_time = datetime.now() + timedelta(days=months * 30)
            except:
                # 日期格式错误，从今天开始计算
                new_expire_time = datetime.now() + timedelta(days=months * 30)
        else:
            # 未授权，从今天开始计算
            new_expire_time = datetime.now() + timedelta(days=months * 30)

        # 更新授权状态
        account_info["auth_status"] = {
            "is_authorized": True,
            "expire_time": str(new_expire_time.date()),
            "last_auth_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 保存更新后的账号数据
        middleware.bucketSet("G_kyh_accounts", account_id, json.dumps(account_info))

        # 更新青龙面板
        if update_qinglong_env(token, account_info):
            sender.reply(f"""
✅ 授权成功！
📅 到期时间: {new_expire_time.date()}
🤖 已同步到青龙面板
""")
        else:
            sender.reply(f"""
✅ 授权成功！
📅 到期时间: {new_expire_time.date()}
❗ 青龙面板同步失败
""")


class KanYuhangClient:
    def __init__(self, mobile_phone=None):
        self.mobile_phone = mobile_phone
        self.base_url = "https://app.eyh.cn/gateway/api"
        self.headers = {
            "User-Agent": "kan yu hang/5.2.6 (iPhone; iOS 17.6; Scale/3.00)",
            "Content-Type": "application/json",
            "Accept-Language": "zh-Hans-CN;q=1",
        }
        # 使用固定的设备ID
        self.equipment_id = "8765B063-3A14-4B96-A305-46906482D5A5"
        self.device_id = "000000"
        # 使用固定的gtCid
        self.gt_cid = "fbb032d8742f3db47d4274098811fd0a"

    def send_login_code(self):
        """发送登录验证码"""
        url = self.base_url

        payload = {
            "api": "v2/login/sendLoginCode",
            "data": {"mobilePhone": self.mobile_phone},
            "traceId": self._generate_trace_id(),
            "userDevice": {
                "device": "ios",
                "equipmentId": self.equipment_id,
                "deviceId": self.device_id,
                "os": "17.6",
                "deviceType": "iPhone15,4",
                "clientVersion": "5.2.6",
                "gtCid": self.gt_cid,
                "deviceBrand": "iphone",
            },
            "token": "",
            "service": "core",
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            if result["code"] == "0":
                return result["data"], self.equipment_id
            return None, None
        except Exception as e:
            print(f"发送验证码失败: {str(e)}")
            return None, None

    def verify_code(self, serial_num, code, equipment_id):
        """验证登录码"""
        url = self.base_url

        payload = {
            "api": "v2/login/codeLogin",
            "data": {"serialNum": serial_num, "code": code},
            "traceId": self._generate_trace_id(),
            "userDevice": {
                "device": "ios",
                "equipmentId": equipment_id,
                "deviceId": "000000",
                "os": "17.6",
                "deviceType": "iPhone15,4",
                "clientVersion": "5.2.6",
                "gtCid": self.gt_cid,
                "deviceBrand": "iphone",
            },
            "token": "",
            "service": "core",
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            if result["code"] == "0":
                return result["data"]
            return None
        except Exception as e:
            print(f"验证码验证失败: {str(e)}")
            return None

    def _generate_trace_id(self, length=10):
        """生成随机traceId"""
        timestamp = str(int(time.time()))
        random_str = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:length]
        return f"{random_str}{timestamp}"

    def query_lottery_records(self, token, uid):
        """查询中奖记录"""
        data = {
            "api": "lottery/queryActivityAwardRecordList",
            "data": {"uid": uid},
            "traceId": self._generate_trace_id(),
            "userDevice": {
                "device": "ios",
                "equipmentId": self.equipment_id,
                "deviceId": self.device_id,
                "os": "17.6",
                "deviceType": "iPhone15,4",
                "clientVersion": "5.2.6",
                "gtCid": self.gt_cid,
                "deviceBrand": "iphone",
            },
            "token": token,
            "service": "media",
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "0":
                    return result.get("data", [])
            return []
        except Exception as e:
            print(f"查询中奖记录失败: {str(e)}")
            return []


def get_user_accounts(user_id=None):
    """获取用户账号列表"""
    if user_id is None:
        user_id = sender.getUserID()

    uservalue = middleware.bucketGet("G_kyh_user", user_id) or "[]"
    try:
        return json.loads(uservalue)
    except:
        return []


def bind_account():
    """看余杭登录绑定"""
    sender.reply("""
=====看余杭登录=====
请输入手机号:
------------------
回复「q」退出绑定
==================""")

    phone = sender.input(60000, 1, False)
    if phone.lower() == "q":
        return

    if not re.match(r"^1[3-9]\d{9}$", phone):
        sender.reply("❌ 手机号格式错误")
        return

    client = KanYuhangClient(phone)
    serial_num, equipment_id = client.send_login_code()

    if not serial_num or not equipment_id:
        sender.reply("❌ 验证码发送失败")
        return

    sender.reply("✅ 验证码已发送，请输入验证码:")
    verify_code = sender.input(300000, 1, False)

    if not verify_code.isdigit():
        sender.reply("❌ 验证码格式错误")
        return

    login_data = client.verify_code(serial_num, verify_code, equipment_id)
    if not login_data:
        sender.reply("❌ 验证失败")
        return

    # 解析登录返回数据，提取token
    if isinstance(login_data, dict):
        token = login_data.get("token", "")
    else:
        token = login_data

    # 通过任务列表接口获取 lotteryActivityUid 作为抽奖uid
    uid = ""
    try:
        uid_payload = {
            "api": "spreadActivity/getAppUserSpreadActivity",
            "data": {},
            "traceId": client._generate_trace_id(),
            "userDevice": {
                "device": "ios",
                "equipmentId": equipment_id,
                "deviceId": "000000",
                "os": "17.6",
                "deviceType": "iPhone15,4",
                "clientVersion": "5.2.6",
                "gtCid": client.gt_cid,
                "deviceBrand": "iphone",
            },
            "token": token,
            "service": "media",
        }
        uid_resp = requests.post(client.base_url, headers=client.headers, json=uid_payload, timeout=15)
        if uid_resp.status_code == 200:
            uid_result = uid_resp.json()
            uid = uid_result.get("data", {}).get("lotteryActivityUid", "")
            if uid:
                print(f"✅ 获取到抽奖UID: {uid}")
            else:
                print("⚠️ 未获取到 lotteryActivityUid")
    except Exception as e:
        print(f"⚠️ 获取UID异常: {e}")

    # 生成账号ID
    account_id = f"kyh_{hashlib.md5(phone.encode()).hexdigest()[:10]}"

    # 检查是否已存在该账号（同手机号重新登录）
    existing_data = middleware.bucketGet("G_kyh_accounts", account_id)
    if existing_data:
        # 已存在，保留原有授权状态，只更新 token/uid/device_id
        existing_info = json.loads(existing_data)
        existing_info["token"] = token
        existing_info["uid"] = uid
        existing_info["device_id"] = equipment_id
        existing_info["wx_id"] = sender.getUserID()
        user_data = existing_info
        is_relogin = True
    else:
        # 新账号
        user_data = {
            "userid": sender.getUserID(),
            "phone": phone,
            "token": token,
            "uid": uid,
            "device_id": equipment_id,
            "wx_id": sender.getUserID(),
            "bind_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "auth_status": {
                "is_authorized": False,
                "expire_time": None,
                "last_auth_time": None,
            },
        }
        is_relogin = False

    # 存储用户数据
    middleware.bucketSet("G_kyh_accounts", account_id, json.dumps(user_data))

    # 更新用户账号列表
    accounts = get_user_accounts()
    if account_id not in accounts:
        accounts.append(account_id)
        middleware.bucketSet("G_kyh_user", userid, json.dumps(accounts))

    # 如果已授权，自动同步到青龙面板
    auth_status = user_data["auth_status"]
    ql_synced = False
    if auth_status["is_authorized"]:
        ql_synced = update_qinglong_env(token, user_data)

    # 构建回复
    if is_relogin:
        auth_info = ""
        if auth_status["is_authorized"]:
            auth_info = f"\n🔑 授权状态: ✅ 已授权（到期: {auth_status['expire_time']}）"
            auth_info += f"\n🤖 青龙同步: {'✅ 已同步' if ql_synced else '❌ 同步失败'}"
        else:
            auth_info = "\n🔑 授权状态: ❌ 未授权"

        sender.reply(f"""
✅ 重新登录成功（Token已更新）
📱 账号: {account_id}
📱 手机号: {phone}{auth_info}

发送「看余杭管理」进行账号管理""")
    else:
        sender.reply(f"""
✅ 登录成功
📱 账号: {account_id}
📱 手机号: {phone}
👤 微信ID: {user_data["wx_id"]}

发送「看余杭管理」进行账号授权""")


def manage_accounts():
    """看余杭账号管理"""
    accounts = get_user_accounts()

    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先绑定")
        return

    # 构建账号列表
    account_list = []
    for i, account_id in enumerate(accounts, 1):
        account_data = middleware.bucketGet("G_kyh_accounts", account_id)
        if account_data:
            account_info = json.loads(account_data)
            phone = account_info["phone"]
            auth_status = account_info["auth_status"]

            if auth_status["is_authorized"]:
                status = f"✅ 已授权（到期: {auth_status['expire_time']}）"
            else:
                status = "❌ 未授权"

            account_list.append(f"[{i}] {phone} {status}")
        else:
            account_list.append(f"[{i}] 数据异常")

    account_list_str = "\n".join(account_list)

    sender.reply(f"""
=====看余杭账号管理=====
🔢 绑定账号: {len(accounts)}个
-------------------------
{account_list_str}
------------------
回复序号选择操作（q退出）
===================""")

    choice = sender.input(60000, 1, False)
    if choice.lower() == "q":
        return

    if not choice.isdigit():
        sender.reply("❌ 输入无效")
        return

    idx = int(choice) - 1
    if idx < 0 or idx >= len(accounts):
        sender.reply("❌ 序号无效")
        return

    selected_account = accounts[idx]
    account_data = middleware.bucketGet("G_kyh_accounts", selected_account)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return

    account_info = json.loads(account_data)

    sender.reply(f"""
已选择账号: {account_info["phone"]}
[1] 授权账号
[2] 删除账号
[3] 查看账号信息
------------------
请回复对应数字：""")

    op = sender.input(60000, 1, False)

    if op == "1":
        authorize_account(selected_account)
    elif op == "2":
        delete_account(selected_account)
    elif op == "3":
        show_account_info(selected_account)
    else:
        sender.reply("❌ 无效选择")


def show_account_info(account_id):
    """显示账号详细信息"""
    account_data = middleware.bucketGet("G_kyh_accounts", account_id)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return

    account_info = json.loads(account_data)
    auth_status = account_info["auth_status"]

    auth_info = "未授权"
    if auth_status["is_authorized"]:
        auth_info = f"已授权（到期: {auth_status['expire_time']}）"

    sender.reply(f"""
=====账号详情=====
📱 手机号: {account_info["phone"]}
👤 微信ID: {account_info["wx_id"]}
🔑 授权状态: {auth_info}
⏰ 绑定时间: {account_info["bind_time"]}
==================""")


def delete_account(account_id):
    """删除账号"""
    accounts = get_user_accounts()

    sender.reply(f"""
=====删除账号确认=====
确认删除账号 {account_id} 吗？
请回复 [Y] 确认
回复 [N] 取消
==================""")

    confirm = sender.input(60000, 1, False).strip().lower()
    if confirm != "y":
        sender.reply("✅ 已取消删除")
        return

    try:
        # 删除账号数据
        middleware.bucketDel("G_kyh_accounts", account_id)

        if account_id in accounts:
            accounts.remove(account_id)
            if accounts:
                middleware.bucketSet("G_kyh_user", userid, json.dumps(accounts))
            else:
                middleware.bucketDel("G_kyh_user", userid)

        sender.reply("✅ 账号删除成功")
    except Exception as e:
        sender.reply(f"❌ 删除失败: {str(e)}")


def show_tutorial():
    """显示使用教程"""
    sender.reply(
        "=====使用教程=====\n"
        "1. 「看余杭登录」绑定账号\n"
        "2. 「看余杭管理」管理已绑定账号\n"
        "3. 「看余杭查询」查看账号状态\n"
        "===================="
    )


def admin_authorize():
    """管理员授权指令"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限！")
        return

    sender.reply("""
=====管理员授权操作=====
[1] 指定用户授权
[2] 批量授权所有用户
[9999] 指定用户未授权账号授权
------------------
请回复对应数字：""")

    choice = sender.input(60000, 1, False)

    if choice == "1":
        # 指定用户授权
        sender.reply("请输入用户微信ID:")
        target_userid = sender.input(60000, 1, False)

        # 获取用户的账号列表
        accounts = get_user_accounts(target_userid)
        if not accounts:
            sender.reply(f"❌ 未找到用户 {target_userid} 的账号")
            return

        # 显示账号列表
        account_list = []
        for i, account_id in enumerate(accounts, 1):
            account_data = middleware.bucketGet("G_kyh_accounts", account_id)
            if account_data:
                account_info = json.loads(account_data)
                phone = account_info["phone"]
                auth_status = account_info["auth_status"]
                status = "已授权" if auth_status["is_authorized"] else "未授权"
                expire_time = auth_status["expire_time"] or "无"
                account_list.append(
                    f"[{i}] 手机号: {phone} | 状态: {status} | 到期时间: {expire_time}"
                )
            else:
                account_list.append(f"[{i}] 数据异常")

        account_list_str = "\n".join(account_list)
        sender.reply(f"""
=====用户账号列表=====
用户ID: {target_userid}
{account_list_str}
------------------
[0] 授权所有账号
或回复序号选择单个账号
===================""")

        choice = sender.input(60000, 1, False)
        if not choice.isdigit():
            sender.reply("❌ 输入无效")
            return

        sender.reply("请输入授权月数 (1-12):")
        months = sender.input(60000, 1, False)
        if not months.isdigit() or int(months) < 1 or int(months) > 12:
            sender.reply("❌ 月数必须为1-12之间的整数")
            return

        months = int(months)
        success_count = 0

        if choice == "0":
            # 授权所有账号
            for account_id in accounts:
                if admin_authorize_account(account_id, months, target_userid):
                    success_count += 1

            sender.reply(
                f"✅ 批量授权完成！成功授权 {success_count}/{len(accounts)} 个账号"
            )
        else:
            # 授权单个账号
            idx = int(choice) - 1
            if idx < 0 or idx >= len(accounts):
                sender.reply("❌ 序号无效")
                return

            if admin_authorize_account(accounts[idx], months, target_userid):
                sender.reply("✅ 授权成功！")
            else:
                sender.reply("❌ 授权失败！")

    elif choice == "2":
        # 批量授权所有用户
        sender.reply("请输入授权月数 (1-12):")
        months = sender.input(60000, 1, False)
        if not months.isdigit() or int(months) < 1 or int(months) > 12:
            sender.reply("❌ 月数必须为1-12之间的整数")
            return

        months = int(months)
        success_count = 0
        total_count = 0

        # 获取所有用户
        users = middleware.bucketAllKeys("G_kyh_user")
        if not users:
            sender.reply("❌ 未找到任何用户")
            return

        for user_id in users:
            accounts = get_user_accounts(user_id)
            for account_id in accounts:
                total_count += 1
                if admin_authorize_account(account_id, months, user_id):
                    success_count += 1

        sender.reply(f"✅ 批量授权完成！成功授权 {success_count}/{total_count} 个账号")

    elif choice == "9999":
        # 指定用户未授权账号授权
        sender.reply("请输入用户微信ID:")
        target_userid = sender.input(60000, 1, False)

        # 获取用户的账号列表
        accounts = get_user_accounts(target_userid)
        if not accounts:
            sender.reply(f"❌ 未找到用户 {target_userid} 的账号")
            return

        # 收集未授权账号
        unauthorized_accounts = []
        for account_id in accounts:
            account_data = middleware.bucketGet("G_kyh_accounts", account_id)
            if account_data:
                account_info = json.loads(account_data)
                # 检查是否未授权或授权已过期
                is_unauthorized = True
                if (
                    account_info["auth_status"]["is_authorized"]
                    and account_info["auth_status"]["expire_time"]
                ):
                    try:
                        expire_time = datetime.strptime(
                            account_info["auth_status"]["expire_time"], "%Y-%m-%d"
                        )
                        if expire_time.date() >= datetime.now().date():
                            is_unauthorized = False
                    except:
                        pass

                if is_unauthorized:
                    unauthorized_accounts.append((account_id, account_info["phone"]))

        if not unauthorized_accounts:
            sender.reply(f"✅ 用户 {target_userid} 没有未授权的账号")
            return

        # 显示未授权账号列表
        account_list = [
            f"[{i + 1}] 手机号: {phone}"
            for i, (_, phone) in enumerate(unauthorized_accounts)
        ]
        account_list_str = "\n".join(account_list)

        sender.reply(f"""
=====未授权账号列表=====
用户ID: {target_userid}
共找到 {len(unauthorized_accounts)} 个未授权账号：
{account_list_str}
------------------
请输入授权月数 (1-12):""")

        months = sender.input(60000, 1, False)
        if not months.isdigit() or int(months) < 1 or int(months) > 12:
            sender.reply("❌ 月数必须为1-12之间的整数")
            return

        months = int(months)
        success_count = 0

        # 开始授权
        for account_id, _ in unauthorized_accounts:
            if admin_authorize_account(account_id, months, target_userid):
                success_count += 1

        sender.reply(f"""
✅ 未授权账号批量授权完成！
授权成功: {success_count}/{len(unauthorized_accounts)} 个账号""")

    else:
        sender.reply("❌ 无效选择")


def admin_authorize_account(account_id, months, user_id):
    """管理员授权账号"""
    try:
        # 获取账号数据
        account_data = middleware.bucketGet("G_kyh_accounts", account_id)
        if not account_data:
            return False

        account_info = json.loads(account_data)

        # 计算新的到期时间
        new_expire_time = None
        if (
            account_info["auth_status"]["is_authorized"]
            and account_info["auth_status"]["expire_time"]
        ):
            try:
                current_expire = datetime.strptime(
                    account_info["auth_status"]["expire_time"], "%Y-%m-%d"
                )
                # 如果当前授权未过期，则从到期时间开始计算新的到期时间
                if current_expire.date() >= datetime.now().date():
                    new_expire_time = current_expire + timedelta(days=months * 30)
                else:
                    # 已过期，从今天开始计算
                    new_expire_time = datetime.now() + timedelta(days=months * 30)
            except:
                # 日期格式错误，从今天开始计算
                new_expire_time = datetime.now() + timedelta(days=months * 30)
        else:
            # 未授权，从今天开始计算
            new_expire_time = datetime.now() + timedelta(days=months * 30)

        # 更新授权状态
        account_info["auth_status"] = {
            "is_authorized": True,
            "expire_time": str(new_expire_time.date()),
            "last_auth_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 保存更新后的账号数据
        middleware.bucketSet("G_kyh_accounts", account_id, json.dumps(account_info))

        # 更新青龙面板
        if update_qinglong_env(account_info["token"], account_info):
            # 记录管理员操作日志
            log_data = {
                "admin_id": sender.getUserID(),
                "user_id": user_id,
                "account_id": account_id,
                "phone": account_info["phone"],
                "months": months,
                "expire_time": str(new_expire_time.date()),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            middleware.bucketSet(
                "G_kyh_admin_logs", f"log_{int(time.time())}", json.dumps(log_data)
            )
            return True

        return False
    except Exception as e:
        print(f"管理员授权失败: {str(e)}")
        return False


def query_lottery_records():
    """查询中奖记录"""
    accounts = get_user_accounts()
    if not accounts:
        sender.reply("❌ 您还没有绑定看余杭账号，请先使用「看余杭登录」进行绑定")
        return

    # 遍历所有账号查询中奖记录
    for account_id in accounts:
        account_data = middleware.bucketGet("G_kyh_accounts", account_id)
        if not account_data:
            continue

        account_info = json.loads(account_data)
        token = account_info.get("token")
        phone = account_info.get("phone")

        if not token or not phone:
            continue

        # 使用token调用中奖记录接口
        client = KanYuhangClient()
        try:
            # 构造获取中奖记录的请求
            data = {
                "api": "lottery/queryActivityAwardRecordList",
                "data": {
                    "uid": "30a7f9016d224fc2a8367200cbbab62a"  # 使用固定的uid
                },
                "traceId": client._generate_trace_id(),
                "userDevice": {
                    "device": "ios",
                    "equipmentId": "8765B063-3A14-4B96-A305-46906482D5A5",  # 使用固定的equipmentId
                    "deviceId": "000000",
                    "os": "17.6",
                    "deviceType": "iPhone15,4",
                    "clientVersion": "5.2.6",
                    "gtCid": "fbb032d8742f3db47d4274098811fd0a",  # 使用固定的gtCid
                    "deviceBrand": "iphone",
                },
                "token": token,
                "service": "media",
            }

            # 添加请求头
            headers = {
                "User-Agent": "kan yu hang/5.2.6 (iPhone; iOS 17.6; Scale/3.00)",
                "Content-Type": "application/json",
                "Accept-Language": "zh-Hans-CN;q=1",
                "Connection": "keep-alive",
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br",
            }

            response = requests.post(client.base_url, headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == "0":
                    records = result.get("data", [])

                    if not records:
                        sender.reply(f"📱 账号 {phone}\n暂无中奖记录")
                        continue

                    # 格式化中奖记录
                    msg = f"📱 账号 {phone} 中奖记录：\n"
                    msg += "-" * 30 + "\n"

                    total_amount = 0  # 累计中奖金额

                    for record in records[:10]:  # 只显示最近10条记录
                        send_date = datetime.fromtimestamp(
                            record["sendDate"] / 1000
                        ).strftime("%Y-%m-%d %H:%M:%S")
                        description = record["description"]
                        status = "已发放" if record["status"] == 2 else "待发放"

                        # 提取金额
                        try:
                            amount = float(description.split("元")[0])
                            total_amount += amount
                        except:
                            pass

                        msg += f"🎁 {description}\n"
                        msg += f"⏰ {send_date}\n"
                        msg += f"📋 状态：{status}\n"
                        msg += "-" * 30 + "\n"

                    # 添加累计金额信息
                    msg += f"\n💰 累计中奖：{total_amount:.2f}元"

                    sender.reply(msg.strip())
                else:
                    sender.reply(
                        f"❌ 账号 {phone} 获取中奖记录失败: {result.get('message', '未知错误')}"
                    )
            else:
                sender.reply(f"❌ 账号 {phone} 请求失败: HTTP {response.status_code}")
        except Exception as e:
            sender.reply(f"❌ 账号 {phone} 查询出错: {str(e)}")
            print(f"Error querying lottery records: {str(e)}")


try:
    usermessage = sender.getMessage()
    if re.search(r"看余杭登录|看余杭绑定", usermessage):
        bind_account()
    elif re.search(r"看余杭管理", usermessage):
        manage_accounts()
    elif re.search(r"看余杭查询", usermessage):
        query_lottery_records()
    elif re.search(r"看余杭教程", usermessage):
        show_tutorial()
    elif re.search(r"看余杭授权", usermessage):
        admin_authorize()
    elif re.search(r"看余杭中奖记录", usermessage):
        query_lottery_records()
    else:
        sender.setContinue()
except Exception as e:
    sender.reply(f"❌ 处理出错: {str(e)}")
    print(f"Error: {str(e)}")
