# [title: 【插件】-顺易充兑换]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: 1603960061]
# [rule: ^顺易充(时间|删除|修正|总结|库存|库存兑换|代理授权|代理|代理配置|代理查询)$]
# [priority: 0]
# [platform: qq,wx]
# [open_source: false]
# [icon: https://i.mji.rip/2025/07/11/5132e8c191f16ac574c0328105061ec4.jpeg]
# [version: 1.1.0]
# [public:true]
# [price: 18.88]
# [admin: false]
# [description: 顺易充时间调整、库存管理、账号运行]

# [param: {"required":false,"key":"G_SYC.agent_price","name":"代理月费价格","placeholder":"8.88"}]
# [param: {"required":false,"key":"G_SYC.agent_points_per_month","name":"代理积分/月","placeholder":"800","value":"800"}]

import json
import random
import requests
import threading
import middleware
from datetime import datetime, timedelta
from typing import Optional

BASE_URL = "https://app.wodeev.com"


def get_proxy_api() -> str:
    try:
        return middleware.bucketGet(bucket="G_SYC", key="proxy_api") or ""
    except:
        return ""


proxy_url = get_proxy_api()
IS_PROXY = bool(proxy_url)
proxy_cache = {}
proxy_lock = threading.Lock()


def get_proxy(force_new=False, account_key=None):
    """获取代理地址"""
    if not IS_PROXY or not proxy_url:
        return None
    if account_key and not force_new:
        with proxy_lock:
            if account_key in proxy_cache:
                return proxy_cache[account_key]
    try:
        resp = requests.get(proxy_url, timeout=5)
        if resp.status_code == 200:
            ip = resp.text.strip()
            if "请先添加白名单" in ip:
                return None
            proxy_dict = {"http": ip, "https": ip}
            if account_key:
                with proxy_lock:
                    proxy_cache[account_key] = proxy_dict
            return proxy_dict
        return None
    except:
        return None


def get_headers(token: str) -> dict:
    return {
        "authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0 (Linux; Android 14; Redmi K20 Pro Build/UKQ1.240624.001; wv) AppleWebKit/537.36",
        "accept": "application/json, text/plain, */*",
        "origin": "https://www.wodeev.com",
        "referer": "https://www.wodeev.com/",
        "lang": "1",
        "loginchannel": "01",
        "client-version": "5.5.2",
    }


def get_score_rank(token: str, account_key: str = None) -> Optional[dict]:
    """获取积分排名和可用积分"""
    url = f"{BASE_URL}/bil-front/v2.0/accounts/myScoreRank"
    try:
        proxies = get_proxy(account_key=account_key) if IS_PROXY else None
        resp = requests.get(
            url,
            headers=get_headers(token),
            params={"scoreType": "02"},
            timeout=10,
            proxies=proxies,
            verify=False,
        )
        data = resp.json()
        if data.get("ret") == 200:
            info = data.get("data", {})
            return {
                "my_scores": info.get("myScores"),
                "available_scores": info.get("myAvailableScores"),
                "rank": info.get("myRank"),
            }
        return None
    except:
        return None


def get_score_mall(token: str, account_key: str = None) -> Optional[list]:
    """获取积分商城商品列表"""
    url = f"{BASE_URL}/bil-front/v2.0/accounts/scoreMall"
    try:
        proxies = get_proxy(account_key=account_key) if IS_PROXY else None
        resp = requests.get(
            url,
            headers=get_headers(token),
            params={"pageNum": 1, "totalNum": 99},
            timeout=10,
            proxies=proxies,
            verify=False,
        )
        data = resp.json()
        if data.get("ret") == 200:
            return data.get("goodsList", [])
        return None
    except:
        return None


def exchange_goods(token: str, product_no: str, account_key: str = None) -> tuple:
    """兑换积分商品"""
    url = f"{BASE_URL}/bil-front/v2.0/exchange"
    headers = get_headers(token)
    headers["content-type"] = "application/json;charset=UTF-8"
    try:
        proxies = get_proxy(account_key=account_key) if IS_PROXY else None
        resp = requests.post(
            url,
            headers=headers,
            json={"productNo": product_no},
            timeout=10,
            proxies=proxies,
            verify=False,
        )
        data = resp.json()
        if data.get("ret") == 200:
            return True, data.get("msg", "兑换成功")
        return False, data.get("msg", "兑换失败")
    except Exception as e:
        return False, f"请求异常: {e}"


senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

# ==================== 代理授权辅助函数 ====================


def get_config():
    """获取配置信息（包含代理定价）"""
    try:
        # Regular auth pricing
        price_str = middleware.bucketGet(bucket="G_SYC", key="price") or "0.88"
        price = float(price_str) if price_str.replace(".", "", 1).isdigit() else 0.88
        zsm = middleware.bucketGet(bucket="G_SYC", key="zsm") or ""
        points_per_month_str = (
            middleware.bucketGet(bucket="G_SYC", key="points_per_month") or "100"
        )
        points_per_month = (
            int(points_per_month_str) if points_per_month_str.isdigit() else 100
        )

        # Agent auth pricing (NEW)
        agent_price_str = (
            middleware.bucketGet(bucket="G_SYC", key="agent_price") or "8.88"
        )
        agent_price = (
            float(agent_price_str)
            if agent_price_str.replace(".", "", 1).isdigit()
            else 8.88
        )
        agent_points_str = (
            middleware.bucketGet(bucket="G_SYC", key="agent_points_per_month") or "800"
        )
        agent_points_per_month = (
            int(agent_points_str) if agent_points_str.isdigit() else 800
        )

        return {
            "price": price,
            "zsm": zsm,
            "points_per_month": points_per_month,
            "agent_price": agent_price,
            "agent_points_per_month": agent_points_per_month,
        }
    except Exception as e:
        return {
            "price": 0.88,
            "zsm": "",
            "points_per_month": 100,
            "agent_price": 8.88,
            "agent_points_per_month": 800,
        }


def get_user_points(user_id=None):
    """获取用户积分"""
    if not user_id:
        user_id = userid
    points = middleware.bucketGet("dd_sign_coin", user_id) or "0"
    user_points = middleware.bucketGet("dd_sign_points", user_id) or "0"
    try:
        dd_sign_coin = int(float(points))
    except:
        dd_sign_coin = 0
    try:
        dd_sign_points = int(float(user_points))
    except:
        dd_sign_points = 0
    return {
        "dd_sign_coin": dd_sign_coin,
        "dd_sign_points": dd_sign_points,
        "total": dd_sign_coin + dd_sign_points,
    }


def set_user_points(user_id, points):
    """设置用户积分"""
    middleware.bucketSet("dd_sign_coin", user_id, str(points["dd_sign_coin"]))
    middleware.bucketSet("dd_sign_points", user_id, str(points["dd_sign_points"]))


def extract_payment_info(payment_result):
    """解析支付结果"""
    payment_info = {
        "money": None,
        "time": "",
        "from": "",
        "status": -1,
        "is_canceled": False,
        "raw_message": "",
    }
    if isinstance(payment_result, dict):
        payment_info["raw_message"] = str(payment_result)
    else:
        payment_info["raw_message"] = payment_result
        try:
            payment_result = json.loads(payment_result)
            payment_info["raw_message"] = str(payment_result)
        except:
            pass

    cancel_patterns = [
        "<status>2</status>",
        "status=2",
        'status":2',
        "支付已取消",
        "取消支付",
        "已取消",
        "cancel",
        "cancelled",
    ]
    for pattern in cancel_patterns:
        if pattern.lower() in payment_info["raw_message"].lower():
            payment_info["is_canceled"] = True
            payment_info["status"] = 2
            break

    try:
        if isinstance(payment_result, dict):
            if payment_result.get("Type") == "pay":
                payment_info["money"] = float(payment_result.get("Money", 0))
                payment_info["time"] = payment_result.get("Time", "")
                payment_info["from"] = payment_result.get("FromName", "")
                if not payment_info["is_canceled"]:
                    raw_status = payment_result.get("status")
                    if raw_status is not None:
                        payment_info["status"] = int(raw_status)
                        if payment_info["status"] == 2:
                            payment_info["is_canceled"] = True
                    else:
                        payment_info["status"] = 1
            else:
                raw_status = payment_result.get("status")
                if raw_status is not None:
                    payment_info["status"] = int(raw_status)
                    if payment_info["status"] == 2:
                        payment_info["is_canceled"] = True
                if payment_result.get("Money") is not None:
                    payment_info["money"] = float(payment_result.get("Money", 0))
                elif payment_result.get("money") is not None:
                    payment_info["money"] = float(payment_result.get("money", 0))
                payment_info["time"] = payment_result.get(
                    "Time", ""
                ) or payment_result.get("time", "")
                payment_info["from"] = payment_result.get(
                    "FromName", ""
                ) or payment_result.get("from_name", "")
        elif (
            isinstance(payment_info["raw_message"], str)
            and "<status>" in payment_info["raw_message"]
        ):
            try:
                status_str = (
                    payment_info["raw_message"]
                    .split("<status>")[1]
                    .split("</status>")[0]
                    .strip()
                )
                payment_info["status"] = int(status_str)
                if payment_info["status"] == 2:
                    payment_info["is_canceled"] = True
                if "<fee>" in payment_info["raw_message"]:
                    fee_str = (
                        payment_info["raw_message"]
                        .split("<fee>")[1]
                        .split("</fee>")[0]
                        .strip()
                    )
                    payment_info["money"] = float(fee_str) / 100
            except:
                pass
        elif (
            isinstance(payment_info["raw_message"], str)
            and "收款金额￥" in payment_info["raw_message"]
        ):
            try:
                amount_str = (
                    payment_info["raw_message"].split("收款金额￥")[1].split("\n")[0]
                )
                payment_info["money"] = float(amount_str)
                payment_info["status"] = 1
            except:
                pass
    except Exception:
        pass
    return payment_info


def verify_payment_status(payment_info, expected_amount):
    """验证支付状态"""
    if payment_info["money"] is None:
        return "failed"
    if payment_info["money"] == 5.37:  # Magic number for canceled
        return "canceled"
    if payment_info["is_canceled"] or payment_info["status"] == 2:
        return "canceled"
    if abs(payment_info["money"] - expected_amount) > 0.01:
        return "insufficient"
    if payment_info["status"] == 1 or (
        payment_info["status"] == -1 and not payment_info["is_canceled"]
    ):
        return "success"
    return "failed"


def agent_wechat_payment_flow(days, amount, config):
    """代理授权微信支付流程"""
    zsm = config.get("zsm", "")
    if not zsm:
        sender.reply("❌ 管理员未配置收款码，无法使用微信支付")
        return False

    userid_display = userid[:20] + "..." if len(userid) > 20 else userid
    sender.reply(f"""=====微信扫码支付=====
👤 用户ID: {userid_display}
🎯 代理授权: {days}天
💰 金额: ¥{amount:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
    sender.replyImage(zsm)

    payment_result = sender.waitPay(timeout=600000, exitcode="q")
    if payment_result == "q":
        sender.reply("❌ 支付已取消")
        return False

    try:
        payment_info = extract_payment_info(payment_result)
        payment_status = verify_payment_status(payment_info, amount)
        if payment_status == "success":
            sender.reply("✅ 支付成功")
            return True
        elif payment_status == "canceled":
            sender.reply("❌ 支付已取消")
            return False
        elif payment_status == "insufficient":
            sender.reply("❌ 支付金额不足")
            return False
        else:
            sender.reply("❌ 支付验证失败")
            return False
    except Exception as e:
        sender.reply("❌ 支付验证失败")
        return False


def agent_point_payment_flow(days, required_points):
    """代理授权积分支付流程"""
    user_points = get_user_points()
    if user_points["total"] < required_points:
        sender.reply(f"""❌ 积分不足！
需要: {required_points}积分
当前: {user_points["total"]}积分
请「联系管理员」充值积分""")
        return False

    sender.reply(f"""⚠ 确认使用积分支付吗？
📊 扣除: {required_points}积分
📈 剩余: {user_points["total"] - required_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消""")

    confirm = sender.input(60000, 1, False)
    if confirm is None:
        sender.reply("⏰ 操作超时，已取消积分支付")
        return False
    if str(confirm).strip().upper() != "Y":
        sender.reply("✅ 积分支付已取消")
        return False

    # Re-check points (avoid race condition)
    current_points = get_user_points()
    if current_points["total"] < required_points:
        sender.reply(
            f"❌ 积分不足！当前积分: {current_points['total']}，需要: {required_points}"
        )
        return False

    # Deduct points
    sign_coin = current_points["dd_sign_coin"]
    sign_points = current_points["dd_sign_points"]
    if sign_coin >= required_points:
        sign_coin -= required_points
    else:
        remaining = required_points - sign_coin
        sign_coin = 0
        sign_points -= remaining

    sign_coin = max(0, sign_coin)
    sign_points = max(0, sign_points)

    result_points = {
        "dd_sign_coin": sign_coin,
        "dd_sign_points": sign_points,
    }
    set_user_points(userid, result_points)

    sender.reply(
        f"✅ 积分支付成功！扣除 {required_points}积分，剩余积分: {sign_points + sign_coin}"
    )
    return True


# ==================== 代理授权辅助函数结束 ====================


def get_all_authorized_accounts():
    """获取所有已授权账号"""
    try:
        all_phones = middleware.bucketAllKeys("G_SYC_AUT") or []
        authorized_accounts = {}
        for phone in all_phones:
            expire_date = middleware.bucketGet("G_SYC_AUT", phone)
            if expire_date:
                authorized_accounts[phone] = {
                    "expire_date": expire_date,
                    "phone": phone,
                }
        return authorized_accounts
    except:
        return {}


def get_user_by_phone(phone):
    """根据手机号查找用户ID"""
    try:
        all_users = middleware.bucketAllKeys("G_SYC_user") or []
        for user_id in all_users:
            phones_json = middleware.bucketGet("G_SYC_user", user_id) or "[]"
            phones = json.loads(phones_json)
            if phone in phones:
                return user_id
        return None
    except:
        return None


def adjust_authorization_time(phone, days):
    """调整单个账号的授权时间

    【数据同步说明】
    本函数修改全局授权数据桶(G_SYC_AUT)，用户账号数据会自动同步：
    - G_SYC_AUT: 权威数据源，直接修改
    - user_accounts.auth_status: 通过get_user_accounts()动态构建，自动同步
    - 顺易充授权插件已优先读取G_SYC_AUT，确保使用最新数据
    """
    try:
        current_expire = middleware.bucketGet("G_SYC_AUT", phone)
        if not current_expire:
            return False, "账号未授权"
        try:
            expire_date = datetime.strptime(current_expire, "%Y-%m-%d")
        except:
            return False, "授权日期格式错误"
        new_expire_date = expire_date + timedelta(days=days)
        new_expire_str = new_expire_date.strftime("%Y-%m-%d")
        # 【核心修改】更新全局授权数据，其他数据会自动同步
        middleware.bucketSet("G_SYC_AUT", phone, new_expire_str)
        return True, new_expire_str
    except Exception as e:
        return False, str(e)


def batch_adjust_all_users(days):
    """批量调整所有用户的授权时间"""
    authorized_accounts = get_all_authorized_accounts()
    if not authorized_accounts:
        return 0, 0, []
    success_count = 0
    fail_count = 0
    results = []
    for phone, info in authorized_accounts.items():
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        success, result = adjust_authorization_time(phone, days)
        if success:
            success_count += 1
            results.append(f"✅ {masked_phone}: {result}")
        else:
            fail_count += 1
            results.append(f"❌ {masked_phone}: {result}")
    return success_count, fail_count, results


def parse_selection(choice_str, max_index):
    """解析用户选择（支持 1,4,6 或 1-8 或 0）"""
    indices = []
    if choice_str == "0":
        return list(range(max_index))
    for part in choice_str.split(","):
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                start_idx = int(start) - 1
                end_idx = int(end) - 1
                if 0 <= start_idx < max_index and 0 <= end_idx < max_index:
                    indices.extend(range(start_idx, end_idx + 1))
            except:
                pass
        else:
            try:
                idx = int(part) - 1
                if 0 <= idx < max_index:
                    indices.append(idx)
            except:
                pass
    return list(set(indices))


def adjust_single_user():
    """调整单个用户的授权时间"""
    sender.reply("请输入需要授权的用户ID:")
    user_id_input = sender.input(60000, 1, False)
    if not user_id_input:
        sender.reply("❌ 输入超时")
        return
    target_user_id = str(user_id_input).strip()
    if target_user_id.lower() == "q":
        sender.reply("✅ 已取消")
        return
    try:
        phones_json = middleware.bucketGet("G_SYC_user", target_user_id) or "[]"
        phones = json.loads(phones_json)
    except:
        sender.reply(f"❌ 用户ID不存在或数据错误")
        return
    if not phones:
        sender.reply(f"❌ 用户 {target_user_id[:20]}... 没有绑定账号")
        return
    account_list = []
    for phone in phones:
        expire_date = middleware.bucketGet("G_SYC_AUT", phone) or "未授权"
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        account_list.append(
            {"phone": phone, "masked_phone": masked_phone, "expire_date": expire_date}
        )
    list_msg = f"====用户账号列表====\n"
    list_msg += f"👤 用户ID: {target_user_id[:30]}...\n"
    list_msg += f"📱 账号数: {len(account_list)}个\n"
    list_msg += "--------------------\n"
    for idx, acc in enumerate(account_list, 1):
        list_msg += f"[{idx}] 📱 {acc['masked_phone']} | 📅 {acc['expire_date']}\n"
    list_msg += "--------------------\n"
    list_msg += "[0] 所有账号\n"
    list_msg += "回复序号选择账号\n"
    list_msg += "支持: 1,4,6 或 1-8 或 0\n"
    list_msg += "===================="
    sender.reply(list_msg)
    choice_input = sender.input(60000, 1, False)
    if not choice_input:
        sender.reply("❌ 输入超时")
        return
    choice_str = str(choice_input).strip()
    if choice_str.lower() == "q":
        sender.reply("✅ 已取消")
        return
    selected_indices = parse_selection(choice_str, len(account_list))
    if not selected_indices:
        sender.reply("❌ 无效选择")
        return
    selected_accounts = [account_list[i] for i in selected_indices]
    sender.reply(
        "请输入授权天数:\n"
        "+天数（延长时间，如 +30）\n"
        "-天数（减少时间，如 -10）\n"
        "直接输入数字（如 30）"
    )
    days_input = sender.input(120000, 1, False)
    if not days_input:
        sender.reply("❌ 输入超时")
        return
    days_input = str(days_input).strip()
    if days_input.lower() == "q":
        sender.reply("✅ 已取消")
        return
    try:
        days = int(days_input)
        if abs(days) > 3650:
            sender.reply("❌ 天数范围：-3650 到 +3650")
            return
    except ValueError:
        sender.reply("❌ 天数必须为整数（支持+/-）")
        return
    days_display = f"+{days}" if days > 0 else str(days)
    confirm_msg = f"⚠️ 确认操作\n"
    confirm_msg += f"📱 选中账号: {len(selected_accounts)}个\n"
    confirm_msg += f"📆 调整天数: {days_display}天\n"
    confirm_msg += "回复 Y 确认执行"
    sender.reply(confirm_msg)
    confirm = sender.input(60000, 1, False)
    if not confirm or str(confirm).strip().upper() != "Y":
        sender.reply("✅ 已取消")
        return
    success_count = 0
    fail_count = 0
    results = []
    for acc in selected_accounts:
        phone = acc["phone"]
        masked_phone = acc["masked_phone"]
        success, result = adjust_authorization_time(phone, days)
        if success:
            success_count += 1
            results.append(f"✅ {masked_phone}: {result}")
        else:
            fail_count += 1
            results.append(f"❌ {masked_phone}: {result}")
    summary = (
        f"=====调整完成=====\n"
        f"👤 用户ID: {target_user_id[:20]}...\n"
        f"📱 总账号: {len(selected_accounts)}个\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"📆 调整天数: {days_display}天\n"
        f"==================\n\n"
    )
    summary += "\n".join(results)
    sender.reply(summary)


def fix_expire_year():
    """修正到期时间，把超过 26年的改成25年"""
    authorized_accounts = get_all_authorized_accounts()
    if not authorized_accounts:
        sender.reply("❌ 没有找到已授权账号")
        return
    need_fix = []
    for phone, info in authorized_accounts.items():
        expire_date = info["expire_date"]
        try:
            date_obj = datetime.strptime(expire_date, "%Y-%m-%d")
            if date_obj.year >= 2026:
                masked_phone = (
                    phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                )
                need_fix.append(
                    {
                        "phone": phone,
                        "masked_phone": masked_phone,
                        "expire_date": expire_date,
                        "date_obj": date_obj,
                    }
                )
        except:
            continue
    if not need_fix:
        sender.reply("✅ 没有需要修正的账号（无超过 26年的记录）")
        return
    list_msg = f"====需要修正的账号====\n"
    list_msg += f"📱 共 {len(need_fix)} 个账号到期时间超过 26年\n"
    list_msg += "--------------------\n"
    for acc in need_fix[:20]:
        list_msg += f"📱 {acc['masked_phone']} | 📅 {acc['expire_date']}\n"
    if len(need_fix) > 20:
        list_msg += f"... 还有 {len(need_fix) - 20} 个\n"
    list_msg += "--------------------\n"
    list_msg += "⚠️ 将把2026年及以后的全部改为2025年\n"
    list_msg += "回复 Y 确认执行"
    sender.reply(list_msg)
    confirm = sender.input(60000, 1, False)
    if not confirm or str(confirm).strip().upper() != "Y":
        sender.reply("✅ 已取消")
        return
    success_count = 0
    fail_count = 0
    results = []
    for acc in need_fix:
        phone = acc["phone"]
        masked_phone = acc["masked_phone"]
        date_obj = acc["date_obj"]
        try:
            if date_obj.month == 2 and date_obj.day == 29:
                new_date = date_obj.replace(year=2025, day=28)
            else:
                new_date = date_obj.replace(year=2025)
            new_date_str = new_date.strftime("%Y-%m-%d")
            middleware.bucketSet("G_SYC_AUT", phone, new_date_str)
            success_count += 1
            results.append(f"✅ {masked_phone}: {acc['expire_date']} → {new_date_str}")
        except Exception as e:
            fail_count += 1
            results.append(f"❌ {masked_phone}: {str(e)}")
    summary = (
        f"=====修正完成=====\n"
        f"📱 总账号: {len(need_fix)}个\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"==================\n\n"
    )
    if len(results) <= 20:
        summary += "\n".join(results)
    else:
        summary += (
            "\n".join(results[:10])
            + f"\n... 省略 {len(results) - 20} 个 ...\n"
            + "\n".join(results[-10:])
        )
    sender.reply(summary)


def delete_expired_accounts():
    """删除所有过期账号"""
    today = datetime.now().strftime("%Y-%m-%d")
    authorized_accounts = get_all_authorized_accounts()
    if not authorized_accounts:
        sender.reply("❌ 没有找到已授权账号")
        return
    expired_list = []
    for phone, info in authorized_accounts.items():
        expire_date = info["expire_date"]
        if expire_date < today:
            masked_phone = (
                phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
            )
            expired_list.append(
                {
                    "phone": phone,
                    "masked_phone": masked_phone,
                    "expire_date": expire_date,
                }
            )
    if not expired_list:
        sender.reply("✅ 没有过期账号")
        return
    list_msg = f"====过期账号列表====\n"
    list_msg += f"📱 共 {len(expired_list)} 个过期账号\n"
    list_msg += "--------------------\n"
    for acc in expired_list[:20]:
        list_msg += f"📱 {acc['masked_phone']} | 📅 {acc['expire_date']}\n"
    if len(expired_list) > 20:
        list_msg += f"... 还有 {len(expired_list) - 20} 个\n"
    list_msg += "--------------------\n"
    list_msg += "⚠️ 确认删除所有过期账号？\n"
    list_msg += "回复 Y 确认删除"
    sender.reply(list_msg)
    confirm = sender.input(60000, 1, False)
    if not confirm or str(confirm).strip().upper() != "Y":
        sender.reply("✅ 已取消")
        return
    success_count = 0
    fail_count = 0
    results = []
    for acc in expired_list:
        phone = acc["phone"]
        masked_phone = acc["masked_phone"]
        try:
            middleware.bucketDel("G_SYC_AUT", phone)
            middleware.bucketDel("G_SYC_TOKEN", phone)
            user_id = get_user_by_phone(phone)
            if user_id:
                phones_json = middleware.bucketGet("G_SYC_user", user_id) or "[]"
                phones = json.loads(phones_json)
                if phone in phones:
                    phones.remove(phone)
                    if phones:
                        middleware.bucketSet("G_SYC_user", user_id, json.dumps(phones))
                    else:
                        middleware.bucketDel("G_SYC_user", user_id)
            success_count += 1
            results.append(f"✅ {masked_phone}: 已删除")
        except Exception as e:
            fail_count += 1
            results.append(f"❌ {masked_phone}: {str(e)}")
    summary = (
        f"=====删除完成=====\n"
        f"📱 过期账号: {len(expired_list)}个\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"==================\n\n"
    )
    if len(results) <= 20:
        summary += "\n".join(results)
    else:
        summary += (
            "\n".join(results[:10])
            + f"\n... 省略 {len(results) - 20} 个 ...\n"
            + "\n".join(results[-10:])
        )
    sender.reply(summary)


def delete_user_accounts():
    """删除用户名下所有账号（支持批量）"""
    sender.reply(
        "=====删除操作=====\n"
        "[1] 删除所有过期账号\n"
        "[2] 删除指定用户账号(支持批量)\n"
        "回复数字选择操作\n"
        "=================="
    )
    choice = sender.input(60000, 1, False)
    if not choice:
        sender.reply("❌ 操作超时")
        return
    choice = str(choice).strip()
    if choice.lower() == "q":
        sender.reply("✅ 已取消")
        return
    if choice == "1":
        delete_expired_accounts()
        return
    if choice != "2":
        sender.reply("❌ 无效选择")
        return
    sender.reply("请输入需要删除的用户ID（多个用逗号分隔）:")
    user_id_input = sender.input(120000, 1, False)
    if not user_id_input:
        sender.reply("❌ 输入超时")
        return
    user_id_input = str(user_id_input).strip()
    if user_id_input.lower() == "q":
        sender.reply("✅ 已取消")
        return
    # 解析多个用户ID
    user_ids = [uid.strip() for uid in user_id_input.split(",") if uid.strip()]
    if not user_ids:
        sender.reply("❌ 未输入有效用户ID")
        return
    # 收集所有用户的账号信息
    all_accounts = []
    valid_users = []
    for target_user_id in user_ids:
        try:
            phones_json = middleware.bucketGet("G_SYC_user", target_user_id) or "[]"
            phones = json.loads(phones_json)
            if phones:
                valid_users.append({"user_id": target_user_id, "phones": phones})
                for phone in phones:
                    expire_date = middleware.bucketGet("G_SYC_AUT", phone) or "未授权"
                    masked_phone = (
                        phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                    )
                    all_accounts.append(
                        {
                            "user_id": target_user_id,
                            "phone": phone,
                            "masked_phone": masked_phone,
                            "expire_date": expire_date,
                        }
                    )
        except:
            pass
    if not valid_users:
        sender.reply(f"❌ 输入的 {len(user_ids)} 个用户ID均无绑定账号")
        return
    # 显示汇总信息
    list_msg = f"====批量删除确认====\n"
    list_msg += f"� 用户数: {len(valid_users)}个\n"
    list_msg += f"📱 总账号: {len(all_accounts)}个\n"
    list_msg += "--------------------\n"
    for user in valid_users:
        uid_short = (
            user["user_id"][:15] + "..."
            if len(user["user_id"]) > 15
            else user["user_id"]
        )
        list_msg += f"� {uid_short}: {len(user['phones'])}个账号\n"
    list_msg += "--------------------\n"
    list_msg += (
        f"⚠️ 确认删除以上 {len(valid_users)} 个用户的 {len(all_accounts)} 个账号？\n"
    )
    list_msg += "回复 Y 确认删除"
    sender.reply(list_msg)
    confirm = sender.input(60000, 1, False)
    if not confirm or str(confirm).strip().upper() != "Y":
        sender.reply("✅ 已取消")
        return
    # 执行删除（删除用户名下所有数据桶数据）
    success_count = 0
    fail_count = 0
    user_results = []
    for user in valid_users:
        target_user_id = user["user_id"]
        phones = user["phones"]
        user_success = 0
        for phone in phones:
            try:
                # 删除所有相关数据桶
                try:
                    middleware.bucketDel("G_SYC_AUT", phone)
                except:
                    pass
                try:
                    middleware.bucketDel("G_SYC_token", phone)
                except:
                    pass
                try:
                    middleware.bucketDel("G_SYC_token_status", phone)
                except:
                    pass
                user_success += 1
                success_count += 1
            except Exception as e:
                fail_count += 1
        # 删除用户绑定记录
        try:
            middleware.bucketDel("G_SYC_user", target_user_id)
        except:
            pass
        # 删除用户积分记录
        try:
            middleware.bucketDel("G_SYC_sign", target_user_id)
        except:
            pass
        try:
            middleware.bucketDel("G_SYC_coin", target_user_id)
        except:
            pass
        uid_short = (
            target_user_id[:15] + "..." if len(target_user_id) > 15 else target_user_id
        )
        user_results.append(f"✅ {uid_short}: 删除{user_success}个账号")
    summary = (
        f"=====批量删除完成=====\n"
        f"� 用户数: {len(valid_users)}个\n"
        f"📱 总账号: {len(all_accounts)}个\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"====================\n"
    )
    summary += "\n".join(user_results)
    sender.reply(summary)


def query_exchange_stock():
    """查询兑换库存（随机选择当前用户一个账号）"""
    phones_json = middleware.bucketGet("G_SYC_user", userid) or "[]"
    try:
        phones = json.loads(phones_json)
    except:
        phones = []
    if not phones:
        sender.reply("❌ 你还没有绑定账号")
        return
    phone = random.choice(phones)
    token = middleware.bucketGet("G_SYC_token", phone)
    if not token:
        sender.reply(f"❌ 账号 {phone[:3]}****{phone[-4:]} 无token，请重新登录")
        return
    account_key = f"acc_{phone}"
    rank_info = get_score_rank(token, account_key)
    mall_list = get_score_mall(token, account_key)
    if not mall_list:
        sender.reply("❌ 获取商城数据失败，token可能已过期")
        return
    msg = f"=====兑换库存查询=====\n"
    for g in mall_list:
        name = (
            g.get("goodsName", "").replace("顺易充", "").replace("服务费", "").strip()
        )
        price = g.get("price", 0)
        remain = g.get("remainNum", 0)
        plan = g.get("planNum", 0)
        stock = f"{remain}/{plan}" if plan else str(remain)
        msg += f"🎫 {name}\n💰 {price}分 | 📦 库存: {stock}\n--------------------\n"
    msg += "===================="
    sender.reply(msg)


def do_exchange_stock():
    """库存兑换（选账号、选商品、输数量、确认兑换）"""
    phones_json = middleware.bucketGet("G_SYC_user", userid) or "[]"
    try:
        phones = json.loads(phones_json)
    except:
        phones = []
    if not phones:
        sender.reply("❌ 你还没有绑定账号")
        return
    # 步骤1: 选择账号
    msg = "=====选择账号=====\n"
    for i, p in enumerate(phones, 1):
        masked = p[:3] + "****" + p[-4:] if len(p) == 11 else p
        msg += f"[{i}] {masked}\n"
    msg += "--------------------\n回复序号选择账号"
    sender.reply(msg)
    choice = sender.input(60000, 1, False)
    if not choice:
        sender.reply("❌ 超时退出")
        return
    choice = str(choice).strip()
    if choice.lower() == "q":
        sender.reply("✅ 已取消")
        return
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(phones):
            sender.reply("❌ 无效选择")
            return
    except:
        sender.reply("❌ 请输入数字")
        return
    phone = phones[idx]
    token = middleware.bucketGet("G_SYC_token", phone)
    if not token:
        sender.reply(f"❌ 账号 {phone[:3]}****{phone[-4:]} 无token，请重新登录")
        return
    account_key = f"acc_{phone}"
    masked = phone[:3] + "****" + phone[-4:]
    # 步骤2: 获取商城列表
    rank_info = get_score_rank(token, account_key)
    mall_list = get_score_mall(token, account_key)
    if not mall_list:
        sender.reply("❌ 获取商城数据失败")
        return
    my_points = float(rank_info["available_scores"]) if rank_info else 0
    msg = f"=====选择兑换商品=====\n💰 可用积分: {my_points}\n--------------------\n"
    for i, g in enumerate(mall_list, 1):
        name = (
            g.get("goodsName", "").replace("顺易充", "").replace("服务费", "").strip()
        )
        price = g.get("price", 0)
        remain = g.get("remainNum", 0)
        status = "✅" if my_points >= price and remain > 0 else "❌"
        msg += f"[{i}] {status} {name} | {price}分 | 库存:{remain}\n"
    msg += "--------------------\n回复序号选择商品"
    sender.reply(msg)
    choice = sender.input(60000, 1, False)
    if not choice:
        sender.reply("❌ 超时退出")
        return
    choice = str(choice).strip()
    if choice.lower() == "q":
        sender.reply("✅ 已取消")
        return
    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(mall_list):
            sender.reply("❌ 无效选择")
            return
    except:
        sender.reply("❌ 请输入数字")
        return
    goods = mall_list[idx]
    goods_name = (
        goods.get("goodsName", "").replace("顺易充", "").replace("服务费", "").strip()
    )
    goods_no = goods.get("goodsNo", "")
    goods_price = goods.get("price", 0)
    goods_remain = goods.get("remainNum", 0)
    if goods_remain <= 0:
        sender.reply("❌ 该商品库存不足")
        return
    if my_points < goods_price:
        sender.reply(f"❌ 积分不足\n需要: {goods_price}\n当前: {my_points}")
        return
    # 步骤3: 输入兑换数量
    max_count = min(int(my_points // goods_price), goods_remain)
    sender.reply(
        f"=====输入兑换数量=====\n🎫 {goods_name}\n💰 单价: {goods_price}分\n📦 库存: {goods_remain}\n✅ 最多可兑: {max_count}个\n--------------------\n请输入兑换数量(1-{max_count})"
    )
    choice = sender.input(60000, 1, False)
    if not choice:
        sender.reply("❌ 超时退出")
        return
    choice = str(choice).strip()
    if choice.lower() == "q":
        sender.reply("✅ 已取消")
        return
    try:
        count = int(choice)
        if count <= 0 or count > max_count:
            sender.reply(f"❌ 数量必须在1-{max_count}之间")
            return
    except:
        sender.reply("❌ 请输入数字")
        return
    total_cost = goods_price * count
    # 步骤4: 确认兑换
    sender.reply(
        f"=====确认兑换=====\n📱 账号: {masked}\n🎫 商品: {goods_name}\n💰 单价: {goods_price}分\n📦 数量: {count}个\n💸 总计: {total_cost}分\n--------------------\n回复 Y 确认兑换"
    )
    confirm = sender.input(60000, 1, False)
    if not confirm or str(confirm).strip().upper() != "Y":
        sender.reply("✅ 已取消")
        return
    # 执行兑换
    success_count = 0
    fail_count = 0
    for i in range(count):
        ok, msg = exchange_goods(token, goods_no, account_key)
        if ok:
            success_count += 1
        else:
            fail_count += 1
    sender.reply(
        f"=====兑换完成=====\n📱 账号: {masked}\n🎫 商品: {goods_name}\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个\n===================="
    )


def summarize_all_users():
    """统计每个用户名下的账号数量"""
    sender.reply("🔍 正在统计所有用户账号...")
    all_users = middleware.bucketAllKeys("G_SYC_user") or []
    if not all_users:
        sender.reply("❌ 未找到任何用户数据")
        return
    user_stats = []
    total_accounts = 0
    total_authorized = 0
    today = datetime.now().strftime("%Y-%m-%d")
    for user_id in all_users:
        try:
            phones_json = middleware.bucketGet("G_SYC_user", user_id) or "[]"
            phones = json.loads(phones_json)
            if not phones:
                continue
            auth_count = 0
            for phone in phones:
                expire_date = middleware.bucketGet("G_SYC_AUT", phone) or ""
                if expire_date and expire_date >= today:
                    auth_count += 1
            total_accounts += len(phones)
            total_authorized += auth_count
            uid_short = user_id[:20] + "..." if len(user_id) > 20 else user_id
            user_stats.append(
                {
                    "user_id": user_id,
                    "uid_short": uid_short,
                    "count": len(phones),
                    "auth_count": auth_count,
                }
            )
        except:
            pass
    # 按账号数排序
    user_stats.sort(key=lambda x: x["count"], reverse=True)
    summary = (
        f"=====顺易充用户总结=====\n"
        f"👥 用户数: {len(user_stats)}个\n"
        f"📱 总账号: {total_accounts}个\n"
        f"✅ 已授权: {total_authorized}个\n"
        f"❌ 未授权: {total_accounts - total_authorized}个\n"
        f"====================\n"
    )
    for idx, stat in enumerate(user_stats, 1):
        auth_info = (
            f"(授权{stat['auth_count']})" if stat["auth_count"] > 0 else "(未授权)"
        )
        summary += f"{idx}. {stat['uid_short']}: {stat['count']}个 {auth_info}\n"
    sender.reply(summary)


def run_user_accounts():
    """运行发送指令的微信IID名下所有的已经授权、未到期的账号"""
    try:
        # 获取当前用户的手机号列表
        phones_json = middleware.bucketGet("G_SYC_user", userid) or "[]"
        phones = json.loads(phones_json)
        if not phones:
            sender.reply("❌ 您还没有绑定任何账号\n💡 请先发送「顺易充登录」绑定账号")
            return

        # 检查授权状态和到期时间
        today = datetime.now().strftime("%Y-%m-%d")
        valid_accounts = []
        invalid_accounts = []

        for phone in phones:
            expire_date = middleware.bucketGet("G_SYC_AUT", phone) or ""
            token = middleware.bucketGet("G_SYC_token", phone) or ""

            if not expire_date:
                invalid_accounts.append({"phone": phone, "reason": "未授权"})
                continue

            if expire_date < today:
                invalid_accounts.append(
                    {"phone": phone, "reason": f"已过期({expire_date})"}
                )
                continue

            if not token:
                invalid_accounts.append(
                    {"phone": phone, "reason": "无token，请重新登录"}
                )
                continue

            # 已授权且未到期
            valid_accounts.append(
                {"phone": phone, "expire_date": expire_date, "token": token}
            )

        if not valid_accounts:
            msg = "❌ 没有找到可运行的账号\n\n"
            if invalid_accounts:
                msg += "⚠️ 账号状态:\n"
                for acc in invalid_accounts[:10]:
                    masked = (
                        acc["phone"][:3] + "****" + acc["phone"][-4:]
                        if len(acc["phone"]) == 11
                        else acc["phone"]
                    )
                    msg += f"📱 {masked}: {acc['reason']}\n"
                if len(invalid_accounts) > 10:
                    msg += f"... 还有 {len(invalid_accounts) - 10} 个\n"
            sender.reply(msg)
            return

        # 显示可运行的账号
        msg = f"=====可运行账号列表=====\n"
        msg += f"📱 找到 {len(valid_accounts)} 个已授权、未到期的账号\n"
        msg += "--------------------\n"
        for idx, acc in enumerate(valid_accounts, 1):
            masked = (
                acc["phone"][:3] + "****" + acc["phone"][-4:]
                if len(acc["phone"]) == 11
                else acc["phone"]
            )
            msg += f"[{idx}] 📱 {masked} | 📅 到期: {acc['expire_date']}\n"
        msg += "--------------------\n"
        msg += f"✅ 共 {len(valid_accounts)} 个账号可以运行\n"
        msg += "💡 请使用「顺易充登录」插件中的「顺易充运行」指令执行任务\n"
        msg += "===================="
        sender.reply(msg)

    except Exception as e:
        sender.reply(f"❌ 运行异常: {str(e)}")


# ==================== 代理授权主功能 ====================


def agent_auth_purchase():
    """顺易充代理授权 - 购买代理资格"""
    userid_display = userid[:20] + "..." if len(userid) > 20 else userid

    # Step 1: Ask for months
    sender.reply(f"""=====顺易充代理授权=====
👤 用户ID: {userid_display}
--------------------
请输入授权月数（1-24月）：
回复 q 取消""")

    months_input = sender.input(60000, 1, False)
    if not months_input:
        sender.reply("❌ 输入超时")
        return
    months_input = str(months_input).strip()
    if months_input.lower() == "q":
        sender.reply("✅ 已取消")
        return

    # Validate months
    try:
        months = int(months_input)
        if months < 1 or months > 24:
            sender.reply("❌ 授权月数必须在1-24之间")
            return
    except ValueError:
        sender.reply("❌ 请输入有效的数字（1-24）")
        return

    days = months * 30

    # Step 2: Get config and calculate price
    config = get_config()
    agent_price = config.get("agent_price", 8.88)
    agent_points = config.get("agent_points_per_month", 800)

    total_price = agent_price * months
    total_points = agent_points * months

    # Step 3: Check existing agent authorization
    existing_expire = middleware.bucketGet("G_SYC_AGENT_AUT", userid)
    expire_info = ""
    if existing_expire:
        try:
            existing_date = datetime.strptime(existing_expire, "%Y-%m-%d")
            today = datetime.now()
            if existing_date.date() >= today.date():
                expire_info = f"\n📅 当前到期: {existing_expire} (将累加)"
            else:
                expire_info = f"\n📅 当前已过期: {existing_expire} (将重新计算)"
        except:
            pass

    # Step 4: Show payment options
    user_points = get_user_points()
    pay_options = []
    pay_handlers = {}
    option_num = 1
    if config.get("zsm"):
        pay_options.append(f"[{option_num}] 微信支付")
        pay_handlers[str(option_num)] = "wechat"
        option_num += 1
    pay_options.append(f"[{option_num}] 积分支付")
    pay_handlers[str(option_num)] = "points"

    userid_display = userid[:20] + "..." if len(userid) > 20 else userid

    pay_menu = f"""=====代理授权支付=====
👤 用户ID: {userid_display}
🎯 授权时长: {months}个月（{days}天）{expire_info}
💰 金额: ¥{total_price:.2f}
📊 积分支付: {total_points}积分（当前积分: {user_points["total"]}）
------------------
{chr(10).join(pay_options)}
回复数字选择支付方式，回复q取消
==================="""

    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False)

    if not pay_choice:
        sender.reply("❌ 输入超时")
        return
    pay_choice = str(pay_choice).strip()
    if pay_choice.lower() == "q":
        sender.reply("✅ 已取消授权")
        return

    # Step 5: Process payment
    payment_success = False
    if pay_choice not in pay_handlers:
        sender.reply("❌ 无效支付方式")
        return

    if pay_handlers[pay_choice] == "wechat":
        payment_success = agent_wechat_payment_flow(days, total_price, config)
    elif pay_handlers[pay_choice] == "points":
        payment_success = agent_point_payment_flow(days, total_points)

    if not payment_success:
        return

    # Step 6: Calculate new expiration (cumulative)
    current_time = datetime.now()
    existing_expire = middleware.bucketGet("G_SYC_AGENT_AUT", userid)

    if existing_expire:
        try:
            existing_date = datetime.strptime(existing_expire, "%Y-%m-%d")
            if existing_date.date() >= current_time.date():
                # Not expired - add to existing
                new_expire_date = existing_date + timedelta(days=days)
            else:
                # Expired - start from today
                new_expire_date = current_time + timedelta(days=days)
        except:
            new_expire_date = current_time + timedelta(days=days)
    else:
        new_expire_date = current_time + timedelta(days=days)

    expire_date_str = new_expire_date.strftime("%Y-%m-%d")

    # Step 7: Save to bucket
    middleware.bucketSet("G_SYC_AGENT_AUT", userid, expire_date_str)

    # Step 8: Success message
    sender.reply(f"""✅ 代理授权成功！
👤 用户ID: {userid_display}
🎯 授权时长: {months}个月（{days}天）
📅 到期时间: {expire_date_str}
--------------------
💡 发送「顺易充代理」可将名下所有账号同步到此到期时间""")


def agent_sync_accounts():
    """顺易充代理 - 同步名下所有账号到代理到期时间"""
    userid_display = userid[:20] + "..." if len(userid) > 20 else userid

    # Step 1: Check if user has agent authorization
    agent_expire = middleware.bucketGet("G_SYC_AGENT_AUT", userid)

    if not agent_expire:
        sender.reply("""❌ 您还没有代理资格！
--------------------
请先使用「顺易充代理授权」购买代理资格""")
        return

    # Step 2: Check if agent authorization is expired
    try:
        agent_expire_date = datetime.strptime(agent_expire, "%Y-%m-%d")
        today = datetime.now()
        if agent_expire_date.date() < today.date():
            days_expired = (today.date() - agent_expire_date.date()).days
            sender.reply(f"""❌ 您的代理资格已过期！
📅 过期时间: {agent_expire}
⏰ 已过期: {days_expired}天
--------------------
请使用「顺易充代理授权」续费""")
            return
    except:
        sender.reply("❌ 代理授权数据异常，请联系管理员")
        return

    # Step 3: Get all user's phone accounts
    phones_json = middleware.bucketGet("G_SYC_user", userid) or "[]"
    try:
        phones = json.loads(phones_json)
    except:
        phones = []

    if not phones:
        sender.reply("""❌ 您还没有绑定任何账号！
--------------------
请先使用「顺易充登录」绑定账号""")
        return

    # Step 4: Show accounts and confirm
    days_left = (agent_expire_date.date() - today.date()).days

    account_list = []
    for phone in phones:
        current_expire = middleware.bucketGet("G_SYC_AUT", phone) or "未授权"
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        account_list.append(f"📱 {masked_phone} | 当前到期: {current_expire}")

    confirm_msg = (
        f"""=====顺易充代理同步=====
👤 用户ID: {userid_display}
📅 代理到期: {agent_expire} (剩余{days_left}天)
--------------------
📱 将同步以下 {len(phones)} 个账号:
"""
        + "\n".join(account_list)
        + f"""
--------------------
⚠️ 所有账号的到期时间将被更新为: {agent_expire}
回复 Y 确认同步"""
    )

    sender.reply(confirm_msg)

    confirm = sender.input(60000, 1, False)
    if not confirm or str(confirm).strip().upper() != "Y":
        sender.reply("✅ 已取消")
        return

    # Step 5: Sync all accounts
    success_count = 0
    fail_count = 0
    results = []

    for phone in phones:
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        try:
            # Update G_SYC_AUT with agent's expiration
            middleware.bucketSet("G_SYC_AUT", phone, agent_expire)
            success_count += 1
            results.append(f"✅ {masked_phone}: → {agent_expire}")
        except Exception as e:
            fail_count += 1
            results.append(f"❌ {masked_phone}: 同步失败")

    # Step 6: Show summary
    summary = f"""=====同步完成=====
👤 用户ID: {userid_display}
📱 总账号: {len(phones)}个
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
📅 统一到期: {agent_expire}
==================

""" + "\n".join(results)

    sender.reply(summary)


def agent_query_status():
    """顺易充代理查询 - 查询当前用户的代理授权状态"""
    userid_display = userid[:20] + "..." if len(userid) > 20 else userid

    # Get agent authorization
    agent_expire = middleware.bucketGet("G_SYC_AGENT_AUT", userid)

    if not agent_expire:
        sender.reply(f"""=====代理授权查询=====
👤 用户ID: {userid_display}
📅 代理状态: ❌ 未授权
--------------------
💡 发送「顺易充代理授权」购买代理资格""")
        return

    # Check expiration
    try:
        agent_expire_date = datetime.strptime(agent_expire, "%Y-%m-%d")
        today = datetime.now()

        if agent_expire_date.date() >= today.date():
            days_left = (agent_expire_date.date() - today.date()).days
            status = "✅ 有效"
            time_info = f"剩余 {days_left} 天"
        else:
            days_expired = (today.date() - agent_expire_date.date()).days
            status = "❌ 已过期"
            time_info = f"已过期 {days_expired} 天"
    except:
        status = "⚠️ 数据异常"
        time_info = "请联系管理员"

    # Get user's phone accounts count
    phones_json = middleware.bucketGet("G_SYC_user", userid) or "[]"
    try:
        phones = json.loads(phones_json)
        phone_count = len(phones)
    except:
        phone_count = 0

    sender.reply(f"""=====代理授权查询=====
👤 用户ID: {userid_display}
📅 到期时间: {agent_expire}
🔖 代理状态: {status}
⏰ {time_info}
📱 名下账号: {phone_count} 个
--------------------
💡 发送「顺易充代理」同步账号到期时间
💡 发送「顺易充代理授权」续费""")


# ==================== 代理授权主功能结束 ====================


def admin_agent_config():
    """顺易充代理配置 - 管理员为指定用户设置代理授权时间"""
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
        return

    # Step 1: Ask for target user ID
    sender.reply("""=====顺易充代理配置=====
👑 管理员专用功能
--------------------
请输入目标用户ID：
回复 q 取消""")

    target_userid = sender.input(60000, 1, False)
    if not target_userid:
        sender.reply("❌ 输入超时")
        return
    target_userid = str(target_userid).strip()
    if target_userid.lower() == "q":
        sender.reply("✅ 已取消")
        return

    # Step 2: Check existing agent authorization for target user
    existing_expire = middleware.bucketGet("G_SYC_AGENT_AUT", target_userid)
    target_display = (
        target_userid[:20] + "..." if len(target_userid) > 20 else target_userid
    )

    expire_info = ""
    if existing_expire:
        try:
            existing_date = datetime.strptime(existing_expire, "%Y-%m-%d")
            today = datetime.now()
            if existing_date.date() >= today.date():
                days_left = (existing_date.date() - today.date()).days
                expire_info = f"\n📅 当前到期: {existing_expire} (剩余{days_left}天)"
            else:
                days_expired = (today.date() - existing_date.date()).days
                expire_info = f"\n📅 已过期: {existing_expire} ({days_expired}天前)"
        except:
            expire_info = f"\n📅 当前记录: {existing_expire} (格式异常)"
    else:
        expire_info = "\n📅 当前状态: 未授权"

    # Step 3: Ask for operation type
    sender.reply(f"""=====代理授权设置=====
👤 目标用户: {target_display}{expire_info}
--------------------
请选择操作：
[1] 增加授权时间（累加）
[2] 设置到期日期（覆盖）
[3] 删除代理授权
回复 q 取消""")

    op_choice = sender.input(60000, 1, False)
    if not op_choice:
        sender.reply("❌ 输入超时")
        return
    op_choice = str(op_choice).strip()
    if op_choice.lower() == "q":
        sender.reply("✅ 已取消")
        return

    if op_choice == "1":
        # Add time (cumulative)
        sender.reply("""请输入增加的授权天数：
（正数增加，负数减少）
示例: 30, +90, -15""")

        days_input = sender.input(60000, 1, False)
        if not days_input:
            sender.reply("❌ 输入超时")
            return
        days_input = str(days_input).strip()
        if days_input.lower() == "q":
            sender.reply("✅ 已取消")
            return

        try:
            days = int(days_input.replace("+", ""))
            if abs(days) > 3650:
                sender.reply("❌ 天数范围：-3650 到 +3650")
                return
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return

        # Calculate new expiration
        current_time = datetime.now()
        if existing_expire:
            try:
                existing_date = datetime.strptime(existing_expire, "%Y-%m-%d")
                if existing_date.date() >= current_time.date():
                    new_expire_date = existing_date + timedelta(days=days)
                else:
                    new_expire_date = current_time + timedelta(days=days)
            except:
                new_expire_date = current_time + timedelta(days=days)
        else:
            new_expire_date = current_time + timedelta(days=days)

        expire_date_str = new_expire_date.strftime("%Y-%m-%d")

        # Confirm
        days_display = f"+{days}" if days > 0 else str(days)
        sender.reply(f"""⚠️ 确认操作
👤 用户: {target_display}
📆 调整: {days_display}天
📅 新到期: {expire_date_str}
--------------------
回复 Y 确认""")

        confirm = sender.input(60000, 1, False)
        if not confirm or str(confirm).strip().upper() != "Y":
            sender.reply("✅ 已取消")
            return

        middleware.bucketSet("G_SYC_AGENT_AUT", target_userid, expire_date_str)
        sender.reply(f"""✅ 代理授权设置成功！
👤 用户: {target_display}
📆 调整: {days_display}天
📅 到期时间: {expire_date_str}""")

    elif op_choice == "2":
        # Set specific date
        sender.reply("""请输入到期日期：
格式: YYYY-MM-DD
示例: 2025-12-31""")

        date_input = sender.input(60000, 1, False)
        if not date_input:
            sender.reply("❌ 输入超时")
            return
        date_input = str(date_input).strip()
        if date_input.lower() == "q":
            sender.reply("✅ 已取消")
            return

        try:
            new_expire_date = datetime.strptime(date_input, "%Y-%m-%d")
            expire_date_str = new_expire_date.strftime("%Y-%m-%d")
        except ValueError:
            sender.reply("❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
            return

        # Confirm
        sender.reply(f"""⚠️ 确认操作
👤 用户: {target_display}
📅 设置到期: {expire_date_str}
--------------------
回复 Y 确认""")

        confirm = sender.input(60000, 1, False)
        if not confirm or str(confirm).strip().upper() != "Y":
            sender.reply("✅ 已取消")
            return

        middleware.bucketSet("G_SYC_AGENT_AUT", target_userid, expire_date_str)
        sender.reply(f"""✅ 代理授权设置成功！
👤 用户: {target_display}
📅 到期时间: {expire_date_str}""")

    elif op_choice == "3":
        # Delete authorization
        if not existing_expire:
            sender.reply("❌ 该用户没有代理授权记录")
            return

        sender.reply(f"""⚠️ 确认删除代理授权？
👤 用户: {target_display}
📅 当前到期: {existing_expire}
--------------------
⚠️ 删除后用户将无法使用代理同步功能
回复 Y 确认删除""")

        confirm = sender.input(60000, 1, False)
        if not confirm or str(confirm).strip().upper() != "Y":
            sender.reply("✅ 已取消")
            return

        try:
            middleware.bucketDel("G_SYC_AGENT_AUT", target_userid)
            sender.reply(f"""✅ 已删除代理授权
👤 用户: {target_display}""")
        except:
            sender.reply("❌ 删除失败")

    else:
        sender.reply("❌ 无效选择")


def main():
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
        return
    sender.reply(
        "=====管理员授权操作=====\n"
        "[1] 一键授权所有用户\n"
        "[2] 单独授权用户\n"
        "回复数字选择操作\n"
        "===================="
    )
    choice = sender.input(60000, 1, False)
    if not choice:
        sender.reply("❌ 操作超时")
        return
    choice = str(choice).strip()
    if choice.lower() == "q":
        sender.reply("✅ 已取消")
        return
    if choice not in ["1", "2"]:
        sender.reply("❌ 无效选择")
        return
    if choice == "2":
        adjust_single_user()
        return
    sender.reply(
        "请输入授权天数:\n"
        "+天数（延长时间，如 +30）\n"
        "-天数（减少时间，如 -10）\n"
        "直接输入数字（如 30）"
    )
    days_input = sender.input(120000, 1, False)
    if not days_input:
        sender.reply("❌ 输入超时")
        return
    days_input = str(days_input).strip()
    if days_input.lower() == "q":
        sender.reply("✅ 已取消")
        return
    try:
        days = int(days_input)
        if abs(days) > 3650:
            sender.reply("❌ 天数范围：-3650 到 +3650")
            return
    except ValueError:
        sender.reply("❌ 天数必须为整数（支持+/-）")
        return
    authorized_accounts = get_all_authorized_accounts()
    if not authorized_accounts:
        sender.reply("❌ 没有找到已授权账号")
        return
    days_display = f"+{days}" if days > 0 else str(days)
    sender.reply(
        f"⚠️ 确认操作\n"
        f"📱 影响账号: {len(authorized_accounts)}个\n"
        f"📆 调整天数: {days_display}天\n"
        f"回复 Y 确认执行"
    )
    confirm = sender.input(60000, 1, False)
    if not confirm or str(confirm).strip().upper() != "Y":
        sender.reply("✅ 已取消")
        return
    sender.reply("🔄 正在批量调整授权时间...")
    success_count, fail_count, results = batch_adjust_all_users(days)
    summary = (
        f"=====批量调整完成=====\n"
        f"📱 总账号数: {len(authorized_accounts)}个\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"📆 调整天数: {days_display}天\n"
        f"====================\n"
    )
    if len(results) <= 20:
        summary += "\n详细结果:\n" + "\n".join(results)
    else:
        summary += f"\n前10个结果:\n" + "\n".join(results[:10])
        summary += f"\n...\n后10个结果:\n" + "\n".join(results[-10:])
    sender.reply(summary)


try:
    usermessage = sender.getMessage()
except AttributeError:
    usermessage = ""

if usermessage == "顺易充删除":
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
    else:
        delete_user_accounts()
elif usermessage == "顺易充修正":
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
    else:
        fix_expire_year()
elif usermessage == "顺易充总结":
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
    else:
        summarize_all_users()
elif usermessage == "顺易充时间":
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
    else:
        main()
elif usermessage == "顺易充库存":
    query_exchange_stock()
elif usermessage == "顺易充库存兑换":
    do_exchange_stock()
elif usermessage == "顺易充代理授权":
    agent_auth_purchase()
elif usermessage == "顺易充代理":
    agent_sync_accounts()
elif usermessage == "顺易充代理配置":
    admin_agent_config()
elif usermessage == "顺易充代理查询":
    agent_query_status()
elif usermessage == "顺易充运行":
    run_user_accounts()
else:
    sender.setContinue()
