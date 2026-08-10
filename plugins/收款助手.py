#[title: 收款助手]
#[language: python]
#[service: 421148494]
#[author: zq8884]
#[disable:false]
#[admin: false]
#[class: 工具类]
#[rule: ^收款助手$]
#[rule: ^我要充值$]
#[rule: ^查询到期$]
#[rule: ^绑定账号$]
#[rule: ^设置默认费用$]
#[rule: ^收款助手到期检查$]
#[rule: ^续费账号$]
#[rule: ^调整收款助手余额$]
#[priority: 999]
#[platform: qq,qb,wx,tb,tg,web,wxmp]
#[open_source: false]
#[version: 4.0]
#[public: true]
#[price: 100]
#[description: 微信扫码收款+账户到期管理。支持按日费用自动计算续费时间。交互式账号绑定流程。按JD账号数量计费，自动同步账号变化。独立账号续费，用户余额管理。]
#[param: {"required":false,"key":"zq8884.zhushoudianfei","bool":false,"placeholder":"","name":"JD代挂日单价","desc":"JD代挂日单价"}]
#[param: {"required":false,"key":"zq8884.shoukuanma","bool":false,"placeholder":"","name":"收款码地址","desc":"收款码地址"}]
#[param: {"required":false,"key":"zq8884.daoqitixing","bool":false,"placeholder":"7","name":"到期提前提醒天数","desc":"到期前多少天开始提醒"}]

import re
import json
import time
import datetime
import hashlib
from typing import Dict, List, Optional, Tuple, Set
import middleware

# 表情符号常量
EMOJI = {
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "money": "💰",
    "user": "👤",
    "time": "⏰",
    "config": "⚙️",
    "bell": "🔔",
    "jd": "🛍️",
    "pin": "📌",
    "charge": "💳",
    "balance": "💎"
}

# ---------- 辅助函数 ----------
def get_im_type():
    """获取当前会话渠道类型"""
    try:
        sender = middleware.Sender(middleware.getSenderID())
        im_type = sender.getImtype()
        return im_type or "wx"
    except Exception as e:
        print(f"获取IM类型失败: {e}")
        return "wx"

def get_user_pin_accounts(im_type: str, user_id: str) -> List[str]:
    """获取用户绑定的JD账号pin列表"""
    try:
        channel_key = f"pin{im_type.upper()}"  # 当前渠道的标识，如 pinQQ, pinWX
        bound_pins = middleware.bucketKeys(channel_key, user_id) or []
        print(f"获取用户pin账号: 渠道={channel_key}, 用户ID={user_id}, 账号数量={len(bound_pins)}")
        return bound_pins
    except Exception as e:
        print(f"获取用户pin账号失败: {e}")
        return []

def get_pin_nickname(pin: str) -> str:
    """获取pin对应的昵称"""
    return pin  # 直接返回完整pin

# ---------- 推送消息 ----------
def push_message(im_type: str, user_id: str, title: str, content: str, group_code: str = ""):
    """推送消息到用户"""
    try:
        middleware.push(
            imType=im_type,
            groupCode=group_code,
            userID=user_id,
            title=title,
            content=content
        )
        print(f"[推送成功] 渠道={im_type}, 用户ID={user_id}, 标题={title}")
        return True
    except Exception as e:
        print(f"[推送异常] 渠道={im_type}, 用户ID={user_id}, 错误={e}")
        return False

# ---------- 配置管理 ----------
def get_fee_config():
    """获取费用配置（从插件参数读取）"""
    config = {}
    
    try:
        electricity_fee = middleware.bucketGet(bucket="zq8884", key="zhushoudianfei")
        if electricity_fee and electricity_fee != "":
            config["fee_per_day"] = float(electricity_fee)
        else:
            config["fee_per_day"] = 0.5
            
    except Exception as e:
        print(f"读取费用参数失败: {e}")
        config = {"fee_per_day": 0.5}
    
    return config

def get_fee_per_day() -> float:
    """获取每日费用（单个JD账号）"""
    config = get_fee_config()
    return config.get("fee_per_day", 0.5)

def get_payment_qrcode_url() -> str:
    """获取收款码地址"""
    qrcode_url = middleware.bucketGet(bucket="zq8884", key="shoukuanma")
    if qrcode_url and qrcode_url != "":
        return qrcode_url
    else:
        return "http://113.44.90.254:1211/admin/images/gallery/1775707515047419941.png"

def get_expiry_reminder_days() -> int:
    """获取到期提前提醒天数"""
    try:
        reminder_days_str = middleware.bucketGet(bucket="zq8884", key="daoqitixing")
        if reminder_days_str and reminder_days_str != "":
            return int(reminder_days_str)
        else:
            return 7
    except:
        return 7

def set_fee_per_day(amount: float):
    """设置每日费用（保存到插件参数）"""
    try:
        middleware.bucketSet(bucket="zq8884", key="zhushoudianfei", value=str(amount))
    except Exception as e:
        print(f"设置费用参数失败: {e}")

# ---------- 工具函数 ----------
def get_user_input(sender, prompt, emoji="💬", timeout=30000, is_password=False):
    """获取用户输入"""
    full_prompt = f"{emoji} {prompt}\n(输入 q 取消操作)"
    sender.reply(full_prompt)
    user_input = sender.listen(timeout=timeout)
    if user_input is None or user_input.strip().lower() == "q":
        sender.reply(f"{EMOJI['warning']} 操作已取消")
        return None
    return user_input.strip()

# ---------- 用户数据管理 ----------
def get_user_data(account: str) -> Dict:
    """获取用户数据"""
    data_str = middleware.bucketGet(bucket="pay_users", key=account)
    if not data_str or data_str == "":
        return {
            "account": account,
            "total_days": 0,
            "expire_time": "",
            "balance": 0.0,
            "pay_records": [],
            "bind_time": "",
            "username": "",
            "sender_id": "",
            "user_id": "",
            "im_type": "wx",
            "last_remind_date": "",
            "pin_accounts": [],  # 绑定的pin账号列表
            "pin_expiry": {},  # 每个pin账号的独立到期时间，格式: {"pin1": "2024-12-31", "pin2": "2024-12-25"}
            "pin_count": 0,  # pin账号数量
            "pin_last_update": ""  # pin信息最后更新时间
        }
    try:
        data = json.loads(data_str)
        # 兼容旧数据格式
        if "pin_expiry" not in data:
            data["pin_expiry"] = {}
        if "pin_last_update" not in data:
            data["pin_last_update"] = ""
        return data
    except:
        return {
            "account": account,
            "total_days": 0,
            "expire_time": "",
            "balance": 0.0,
            "pay_records": [],
            "bind_time": "",
            "username": "",
            "sender_id": "",
            "user_id": "",
            "im_type": "wx",
            "last_remind_date": "",
            "pin_accounts": [],
            "pin_expiry": {},
            "pin_count": 0,
            "pin_last_update": ""
        }

def save_user_data(user_data: Dict):
    """保存用户数据"""
    account = user_data["account"]
    middleware.bucketSet(bucket="pay_users", key=account, value=json.dumps(user_data, ensure_ascii=False))

def calculate_new_expiry(current_expiry: str, days_to_add: int) -> str:
    """计算新的到期日期"""
    if not current_expiry or current_expiry == "":
        base_date = datetime.datetime.now()
    else:
        try:
            base_date = datetime.datetime.strptime(current_expiry, "%Y-%m-%d")
        except:
            base_date = datetime.datetime.now()
    
    new_date = base_date + datetime.timedelta(days=days_to_add)
    return new_date.strftime("%Y-%m-%d")

def refresh_user_pin_info(account: str, im_type: str, user_id: str) -> Tuple[bool, List[str], int]:
    """刷新用户的pin账号信息，返回是否发生变化"""
    try:
        # 获取用户数据
        user_data = get_user_data(account)
        
        # 获取当前最新的pin账号
        current_pin_accounts = get_user_pin_accounts(im_type, user_id)
        current_pin_count = len(current_pin_accounts)
        
        # 获取之前的pin账号
        old_pin_accounts = user_data.get("pin_accounts", [])
        old_pin_count = user_data.get("pin_count", 0)
        
        # 获取之前的pin到期时间
        old_pin_expiry = user_data.get("pin_expiry", {})
        
        # 比较是否有变化
        has_changed = (
            set(current_pin_accounts) != set(old_pin_accounts) or
            current_pin_count != old_pin_count
        )
        
        if has_changed:
            # 更新pin账号列表
            new_pin_expiry = {}
            for pin in current_pin_accounts:
                if pin in old_pin_expiry:
                    new_pin_expiry[pin] = old_pin_expiry[pin]
                else:
                    new_pin_expiry[pin] = ""  # 新账号没有到期时间
            
            # 移除不存在的pin账号的到期时间
            for pin in list(old_pin_expiry.keys()):
                if pin not in current_pin_accounts:
                    del old_pin_expiry[pin]
            
            # 更新用户数据
            user_data["pin_accounts"] = current_pin_accounts
            user_data["pin_count"] = current_pin_count
            user_data["pin_expiry"] = new_pin_expiry
            user_data["pin_last_update"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_user_data(user_data)
            print(f"[INFO] 用户 {account} 的JD账号信息已更新: {old_pin_count}个 -> {current_pin_count}个")
        
        return has_changed, current_pin_accounts, current_pin_count
        
    except Exception as e:
        print(f"[ERROR] 刷新用户pin信息失败: {e}")
        # 返回原始数据
        user_data = get_user_data(account)
        return False, user_data.get("pin_accounts", []), user_data.get("pin_count", 0)

def get_pin_expiry_info(pin: str, pin_expiry_data: Dict) -> Tuple[str, int]:
    """获取pin账号的到期信息"""
    expiry_date = pin_expiry_data.get(pin, "")
    if not expiry_date or expiry_date == "":
        return "未开通", 0
    
    try:
        expiry_datetime = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
        today = datetime.datetime.now()
        days_left = (expiry_datetime - today).days
        return expiry_date, days_left
    except:
        return expiry_date, 0

# ---------- 核心匹配函数 ----------
def get_current_user_info():
    """获取当前用户信息"""
    try:
        sender_id = middleware.getSenderID()
        sender_obj = middleware.Sender(sender_id)
        im_type = get_im_type()
        
        try:
            user_id = sender_obj.getUserID()
            if not user_id or user_id == "":
                user_id = sender_id
        except:
            user_id = sender_id
        
        return {
            "sender_id": sender_id,
            "im_type": im_type,
            "user_id": user_id
        }
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return {"sender_id": "", "im_type": "wx", "user_id": ""}

def find_account_by_user(im_type: str, user_id: str) -> Optional[str]:
    """通过IM类型和用户ID查找账号 - 一对一匹配"""
    all_keys = middleware.bucketAllKeys(bucket="pay_users") or []
    
    for key in all_keys:
        user_data = get_user_data(key)
        data_im_type = user_data.get("im_type", "")
        data_user_id = user_data.get("user_id", "")
        
        if data_im_type == im_type and data_user_id == user_id:
            return key
    
    return None

def find_account_by_user_id(user_id: str) -> Optional[str]:
    """通过用户ID查找账号（跨渠道查找）"""
    all_keys = middleware.bucketAllKeys(bucket="pay_users") or []
    
    for key in all_keys:
        user_data = get_user_data(key)
        data_user_id = user_data.get("user_id", "")
        
        if data_user_id == user_id:
            return key
    
    return None

# ---------- 支付核心流程 ----------
def wait_for_payment(sender, account: str, amount: float, description: str = "充值") -> bool:
    """等待支付完成，成功后增加用户余额"""
    try:
        order_id = f"RECHARGE_{int(time.time())}"
        print(f"[DEBUG] 使用订单号: {order_id}")
        
        pay_res = sender.waitPay(exitcode=order_id, timeout=300000)
        
        if not pay_res or pay_res == "q" or pay_res == "error":
            sender.reply(f"{EMOJI['warning']} 支付流程已取消或发生错误")
            return False
        
        try:
            if isinstance(pay_res, dict):
                # 统一转换为小写键名查找
                pay_res_lower = {k.lower(): v for k, v in pay_res.items()}
                paid_amount = float(pay_res_lower.get('money', 0))
            else:
                paid_amount = float(pay_res)
                
            print(f"[INFO] 支付成功: 金额={paid_amount}")
            
            if paid_amount <= 0:
                sender.reply(f"{EMOJI['error']} 支付金额无效，请重新支付")
                return False
            
            # 处理支付成功，增加用户余额
            success = process_recharge_success(account, paid_amount, order_id, description)
            
            if success:
                user_data = get_user_data(account)
                
                success_msg = f"""
{EMOJI['success']} 充值成功！

📊 充值详情：
👤 用户名：{user_data.get('username', 'N/A')}
💰 充值金额：{paid_amount:.2f}元
{EMOJI['balance']} 账户余额：{user_data.get('balance', 0.0):.2f}元
"""
                sender.reply(success_msg)
                return True
            else:
                sender.reply(f"{EMOJI['error']} 支付成功但处理失败，请联系管理员")
                return False
                
        except ValueError as e:
            sender.reply(f"{EMOJI['error']} 支付金额解析失败: {str(e)}")
            return False
            
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 支付处理异常: {str(e)}")
        print(f"[EXCEPTION] wait_for_payment 异常: {e}")
        return False

def process_recharge_success(account: str, paid_amount: float, order_id: str, description: str) -> bool:
    """处理充值成功逻辑，增加用户余额"""
    try:
        print(f"[DEBUG] 开始处理充值成功: 账号={account}, 金额={paid_amount}")
        
        user_data = get_user_data(account)
        if not user_data:
            print(f"[ERROR] 用户 {account} 不存在")
            return False
        
        new_balance = user_data.get("balance", 0.0) + paid_amount
        
        new_record = {
            "order_id": order_id,
            "amount": paid_amount,
            "description": description,
            "pay_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "recharge"
        }
        
        if "pay_records" not in user_data:
            user_data["pay_records"] = []
        user_data["pay_records"].append(new_record)
        
        user_data["balance"] = new_balance
        
        save_user_data(user_data)
        
        print(f"[SUCCESS] 充值处理成功: 账号={account}, 充值金额={paid_amount:.2f}, 新余额={new_balance:.2f}")
        return True
        
    except Exception as e:
        print(f"[EXCEPTION] 处理充值成功异常: {e}")
        return False

def process_pin_renewal(account: str, pin: str, days: int) -> Tuple[bool, str, float]:
    """处理指定pin账号的续费"""
    try:
        user_data = get_user_data(account)
        fee_per_day = get_fee_per_day()
        
        # 计算所需金额
        amount_needed = fee_per_day * days
        
        # 检查余额是否足够
        current_balance = user_data.get("balance", 0.0)
        
        if current_balance < amount_needed:
            return False, f"余额不足，当前余额: {current_balance:.2f}元，需要: {amount_needed:.2f}元", amount_needed
        
        # 获取当前到期时间
        pin_expiry_data = user_data.get("pin_expiry", {})
        current_expiry = pin_expiry_data.get(pin, "")
        
        # 计算新的到期时间
        today = datetime.datetime.now()
        if not current_expiry or current_expiry == "":
            # 如果没有到期时间，从今天开始计算
            new_expiry = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        else:
            try:
                # 检查是否已过期
                expiry_datetime = datetime.datetime.strptime(current_expiry, "%Y-%m-%d")
                if expiry_datetime < today:
                    # 已过期，从今天开始计算
                    new_expiry = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                else:
                    # 未过期，从原到期时间开始计算
                    new_expiry = (expiry_datetime + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            except:
                # 日期解析失败，从今天开始计算
                new_expiry = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 扣除余额
        new_balance = current_balance - amount_needed
        
        # 更新到期时间
        pin_expiry_data[pin] = new_expiry
        user_data["pin_expiry"] = pin_expiry_data
        user_data["balance"] = new_balance
        
        # 添加支付记录
        new_record = {
            "order_id": f"PIN_RENEW_{int(time.time())}",
            "amount": amount_needed,
            "description": f"续费{pin}账号",
            "pay_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "days": days,
            "pin": pin,
            "fee_per_day": fee_per_day,
            "expiry_before": current_expiry,
            "expiry_after": new_expiry,
            "type": "pin_renewal"
        }
        
        if "pay_records" not in user_data:
            user_data["pay_records"] = []
        user_data["pay_records"].append(new_record)
        
        save_user_data(user_data)
        
        print(f"[SUCCESS] PIN续费成功: 账号={account}, PIN={pin}, 天数={days}, 金额={amount_needed:.2f}, 新到期时间={new_expiry}")
        return True, new_expiry, amount_needed
        
    except Exception as e:
        print(f"[EXCEPTION] 处理PIN续费异常: {e}")
        return False, f"续费处理异常: {str(e)}", 0

# ---------- 到期提醒功能 ----------
def check_expiry_and_send_reminders(sender):
    """检查到期账号并发送提醒 - 每次执行都提醒，显示具体pin账号信息"""
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        reminder_days = get_expiry_reminder_days()
        
        all_keys = middleware.bucketAllKeys(bucket="pay_users") or []
        users_to_remind = []
        pin_expiry_details = []  # 存储每个pin账号的到期信息
        
        for account in all_keys:
            user_data = get_user_data(account)
            
            im_type = user_data.get("im_type", "wx")
            user_id = user_data.get("user_id", "")
            if not user_id:
                continue
                
            # 刷新用户的pin信息
            refresh_user_pin_info(account, im_type, user_id)
            
            # 重新获取更新后的用户数据
            user_data = get_user_data(account)
            
            # 检查每个pin账号的到期时间
            pin_accounts = user_data.get("pin_accounts", [])
            pin_expiry_data = user_data.get("pin_expiry", {})
            
            for pin in pin_accounts:
                expiry_date = pin_expiry_data.get(pin, "")
                if not expiry_date or expiry_date == "":
                    continue
                    
                try:
                    expire_date = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
                    today_date = datetime.datetime.now()
                    days_left = (expire_date - today_date).days
                    
                    if 0 <= days_left <= reminder_days:
                        # 添加到提醒列表
                        users_to_remind.append({
                            "account": account,
                            "user_data": user_data,
                            "days_left": days_left
                        })
                        
                        # 添加到pin详情列表
                        pin_expiry_details.append({
                            "account": account,
                            "username": user_data.get("username", "N/A"),
                            "im_type": im_type,
                            "user_id": user_id,
                            "pin": pin,
                            "expiry_date": expiry_date,
                            "days_left": days_left
                        })
                        
                except Exception as e:
                    print(f"计算pin到期天数失败 {account}:{pin}: {e}")
                    continue
        
        if not users_to_remind:
            sender.reply(f"{EMOJI['info']} 没有需要提醒的到期账号")
            return 0
        
        reminder_count = 0
        for user_info in users_to_remind:
            account = user_info["account"]
            user_data = user_info["user_data"]
            days_left = user_info["days_left"]
            
            user_id = user_data.get("user_id") or user_data.get("sender_id", "")
            im_type = user_data.get("im_type", "wx")
            username = user_data.get("username", "N/A")
            
            if days_left == 0:
                title = "【紧急提醒】JD账号今天到期！"
                content = f"您有JD账号今天到期，请立即续费！"
            elif days_left < 0:
                title = "【重要通知】JD账号已过期！"
                content = f"您有JD账号已过期{-days_left}天，请立即续费！"
            else:
                title = "【温馨提醒】JD账号即将到期"
                content = f"您有JD账号还有{days_left}天到期，请及时续费。"
            
            try:
                if user_id:
                    success = push_message(im_type, user_id, title, content, group_code="")
                    if success:
                        print(f"已推送到期提醒: 用户={user_id}, 用户名={username}, 剩余天数={days_left}")
                        reminder_count += 1
                        
                        user_data["last_remind_date"] = today
                        save_user_data(user_data)
                    else:
                        print(f"推送失败: 用户={user_id}, 用户名={username}")
                else:
                    print(f"用户 {username} 没有用户ID，无法推送")
                
            except Exception as e:
                print(f"发送提醒失败 {account}: {e}")
        
        result_msg = f"""
{EMOJI['bell']} 到期提醒检查完成
----------------------------
📅 检查日期：{today}
⏰ 提前提醒天数：{reminder_days}天
👤 总用户数：{len(all_keys)}
🔔 本次已发送提醒：{reminder_count}人
📧 推送方式：内置推送接口
----------------------------
💡 每次执行此命令都会向所有符合提醒条件的用户发送提醒
"""
        
        # 检查当前用户是否是管理员
        try:
            is_admin = sender.isAdmin()
        except Exception as e:
            print(f"检查管理员权限失败: {e}")
            is_admin = False
        
        if is_admin and pin_expiry_details:
            admin_info = f"""
📋 【管理员查看】即将过期账号详情：
----------------------------"""
            
            # 按用户分组显示
            user_groups = {}
            for detail in pin_expiry_details:
                account = detail["account"]
                if account not in user_groups:
                    user_groups[account] = []
                user_groups[account].append(detail)
            
            for i, (account, pins) in enumerate(user_groups.items(), 1):
                first_pin = pins[0]
                username = first_pin["username"]
                im_type = first_pin["im_type"]
                user_id = first_pin["user_id"]
                
                admin_info += f"""
{i}. 用户: {username}
   ├─ 渠道: {im_type}
   ├─ 用户ID: {user_id}
   ├─ 账号标识: {account}
   └─ 即将过期JD账号:"""
                
                for j, pin_detail in enumerate(pins, 1):
                    pin = pin_detail["pin"]
                    expiry_date = pin_detail["expiry_date"]
                    days_left = pin_detail["days_left"]
                    
                    if days_left == 0:
                        status = "今天到期"
                    elif days_left < 0:
                        status = f"已过期{-days_left}天"
                    else:
                        status = f"剩余{days_left}天"
                    
                    admin_info += f"""
     {j}. {pin}: {expiry_date} ({status})"""
            
            result_msg += admin_info
        
        sender.reply(result_msg)
        
        return reminder_count
        
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 到期提醒检查失败: {str(e)}")
        return 0

# ---------- 主功能模块 ----------
def start_collection_assistant(sender):
    """主菜单"""
    config = get_fee_config()
    reminder_days = get_expiry_reminder_days()
    
    menu = f"""
{EMOJI['money']} 收款助手 v4.0
----------------------------
{EMOJI['jd']} 独立JD账号计费模式
💡 支持账号独立续费管理
1. 绑定拼车账号 - 绑定/更新拼车账号
2. 我要充值 - 为账户充值余额
3. 续费JD账号 - 为指定JD账号续费
4. 查询到期 - 查询账号余额和到期时间
5. 收款助手到期检查 - 手动检查到期账号
6. 设置默认费用 - 设置默认费用
7. 调整收款助手余额 - 调整用户余额
----------------------------
{EMOJI['info']} 当前费用设置（插件参数）：
  JD代挂：{config.get('fee_per_day', 0.5):.2f}元/天/账号
📅 到期提醒：提前{reminder_days}天提醒
📱 收款码：已配置
----------------------------
💡 独立账号续费，使用账户余额结算
🔄 每次操作自动同步最新JD账号
🔧 费用设置：在插件管理中配置参数
"""
    sender.reply(menu)

def bind_account_interactive(sender):
    """绑定拼车账号 - 使用user_id作为用户名，自动获取JD账号"""
    try:
        # 获取当前用户信息
        user_info = get_current_user_info()
        im_type = user_info["im_type"]
        user_id = user_info["user_id"]
        sender_id = user_info["sender_id"]
        
        print(f"[绑定请求] im_type={im_type}, user_id={user_id}, sender_id={sender_id}")
        
        # 检查是否已绑定
        existing_account = find_account_by_user(im_type, user_id)
        if existing_account:
            # 已绑定，刷新pin信息
            has_changed, pin_accounts, pin_count = refresh_user_pin_info(existing_account, im_type, user_id)
            
            user_data = get_user_data(existing_account)
            username = user_data.get("username", "N/A")
            balance = user_data.get("balance", 0.0)
            
            if has_changed:
                sender.reply(f"{EMOJI['success']} 已更新您的JD账号信息\n当前绑定{EMOJI['jd']} {pin_count}个JD账号")
            else:
                sender.reply(f"{EMOJI['info']} 您已绑定账号：{username}\n当前绑定{EMOJI['jd']} {pin_count}个JD账号")
            
            # 显示绑定的pin账号和到期时间
            if pin_count > 0:
                pin_info = f"{EMOJI['jd']} 当前绑定JD账号（{pin_count}个）：\n"
                pin_expiry_data = user_data.get("pin_expiry", {})
                
                for i, pin in enumerate(pin_accounts, 1):
                    expiry_date, days_left = get_pin_expiry_info(pin, pin_expiry_data)
                    if expiry_date == "未开通":
                        expiry_text = "未开通"
                    else:
                        if days_left > 0:
                            expiry_text = f"{expiry_date}（剩余{days_left}天）"
                        elif days_left == 0:
                            expiry_text = f"{expiry_date}（今天到期）"
                        else:
                            expiry_text = f"{expiry_date}（已过期{-days_left}天）"
                    
                    pin_info += f"{i}. {pin} - {expiry_text}\n"
                
                sender.reply(pin_info)
            
            # 显示余额
            sender.reply(f"{EMOJI['balance']} 当前账户余额：{balance:.2f}元")
            return
        
        # 获取用户绑定的JD pin账号
        pin_accounts = get_user_pin_accounts(im_type, user_id)
        pin_count = len(pin_accounts)
        
        if pin_count == 0:
            sender.reply(f"{EMOJI['warning']} 您尚未绑定任何JD账号，请先绑定JD账号")
            return
        
        # 使用user_id作为用户名
        username = user_id
        
        # 生成账号标识
        account = f"user_{hashlib.md5(username.encode()).hexdigest()[:16]}"
        
        # 创建用户数据
        user_data = {
            "account": account,
            "username": username,
            "total_days": 0,
            "expire_time": "",
            "balance": 0.0,
            "pay_records": [],
            "bind_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender_id": sender_id,
            "user_id": user_id,
            "im_type": im_type,
            "last_remind_date": "",
            "pin_accounts": pin_accounts,
            "pin_expiry": {pin: "" for pin in pin_accounts},
            "pin_count": pin_count,
            "pin_last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_user_data(user_data)
        
        fee_per_day = get_fee_per_day()
        
        success_msg = f"""
{EMOJI['success']} 拼车账号绑定成功！
----------------------------
👤 用户名：{username}
{EMOJI['jd']} 绑定JD账号：{pin_count}个
💰 费用标准：{fee_per_day:.2f}元/天/账号
📱 绑定渠道：{im_type}
⏰ 绑定时间：{user_data['bind_time']}
{EMOJI['balance']} 当前账户余额：0.00元
----------------------------
💡 绑定完成！请先充值余额，然后为指定JD账号续费
"""
        sender.reply(success_msg)
        
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 绑定账号失败: {str(e)}")
        print(f"绑定账号异常: {e}")

def recharge_balance(sender):
    """充值功能 - 为账户充值余额"""
    try:
        # 获取当前用户信息
        user_info = get_current_user_info()
        im_type = user_info["im_type"]
        user_id = user_info["user_id"]
        
        print(f"[充值请求] im_type={im_type}, user_id={user_id}")
        
        # 通过 IM类型 + 用户ID 查找账号
        account = find_account_by_user(im_type, user_id)
        
        if not account:
            sender.reply(f"{EMOJI['error']} 未找到您的绑定账号，请先使用【绑定拼车账号】进行绑定")
            return
        
        # 刷新用户的pin信息
        has_changed, pin_accounts, pin_count = refresh_user_pin_info(account, im_type, user_id)
        
        if has_changed:
            sender.reply(f"{EMOJI['info']} 已更新您的JD账号信息，当前绑定{pin_count}个账号")
        
        # 获取用户数据
        user_data = get_user_data(account)
        username = user_data.get("username", "N/A")
        balance = user_data.get("balance", 0.0)
        
        # 显示当前信息
        current_info = f"""
{EMOJI['info']} 当前账户信息：
👤 用户名：{username}
{EMOJI['balance']} 当前余额：{balance:.2f}元
{EMOJI['jd']} 绑定JD账号：{pin_count}个
"""
        sender.reply(current_info)
        
        # 显示充值选项
        recharge_menu = f"""
{EMOJI['charge']} 充值选项
----------------------------
👤 用户名：{username}
{EMOJI['balance']} 当前余额：{balance:.2f}元
----------------------------
请选择充值金额：
1. 10元
2. 30元
3. 50元
4. 100元
5. 自定义金额
"""
        sender.reply(recharge_menu)
        
        choice = get_user_input(sender, "请输入选项编号（1-5）", EMOJI['charge'])
        
        if choice == "1":
            amount = 10.0
        elif choice == "2":
            amount = 30.0
        elif choice == "3":
            amount = 50.0
        elif choice == "4":
            amount = 100.0
        elif choice == "5":
            # 自定义金额
            amount_input = get_user_input(sender, "请输入充值金额（元）", EMOJI['money'])
            if not amount_input:
                return
            
            try:
                amount = float(amount_input)
                if amount <= 0:
                    sender.reply(f"{EMOJI['error']} 金额必须大于0")
                    return
            except ValueError:
                sender.reply(f"{EMOJI['error']} 请输入有效的金额")
                return
        else:
            sender.reply(f"{EMOJI['error']} 无效的选项")
            return
        
        # 发送收款码
        qrcode_url = get_payment_qrcode_url()
        if qrcode_url:
            # 发送支付信息
            payment_msg = f"""
{EMOJI['money']} 账户充值
👤 用户名：{username}
💰 充值金额：{amount:.2f}元
{EMOJI['balance']} 充值后余额：{balance + amount:.2f}元
⏰ 有效时间：5分钟
💡 充值成功后余额可用于为JD账号续费
"""
            sender.reply(payment_msg)
            
            # 发送收款码图片
            img_msg = f"[CQ:image,file={qrcode_url}]"
            sender.reply(img_msg)
        else:
            sender.reply(f"{EMOJI['warning']} 收款码未配置，请联系管理员")
            return
        
        # 等待支付
        sender.reply(f"{EMOJI['info']} 请扫码支付，支付成功后自动充值到账户余额...")
        
        if wait_for_payment(sender, account, amount, f"账户充值{amount}元"):
            # 支付成功的消息已在 wait_for_payment 中发送
            pass
        else:
            sender.reply(f"{EMOJI['error']} 支付失败或已取消")
            
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 充值失败: {str(e)}")
        print(f"充值异常: {e}")

def renew_jd_account(sender):
    """为指定JD账号续费"""
    try:
        # 获取当前用户信息
        user_info = get_current_user_info()
        im_type = user_info["im_type"]
        user_id = user_info["user_id"]
        
        print(f"[续费请求] im_type={im_type}, user_id={user_id}")
        
        # 通过 IM类型 + 用户ID 查找账号
        account = find_account_by_user(im_type, user_id)
        
        if not account:
            sender.reply(f"{EMOJI['error']} 未找到您的绑定账号，请先使用【绑定拼车账号】进行绑定")
            return
        
        # 刷新用户的pin信息
        has_changed, pin_accounts, pin_count = refresh_user_pin_info(account, im_type, user_id)
        
        if has_changed:
            sender.reply(f"{EMOJI['info']} 已更新您的JD账号信息，当前绑定{pin_count}个账号")
        
        if pin_count == 0:
            sender.reply(f"{EMOJI['warning']} 您当前未绑定任何JD账号，请先绑定JD账号")
            return
        
        # 获取用户数据
        user_data = get_user_data(account)
        username = user_data.get("username", "N/A")
        balance = user_data.get("balance", 0.0)
        pin_expiry_data = user_data.get("pin_expiry", {})
        
        fee_per_day = get_fee_per_day()
        
        # 显示用户信息
        user_info_msg = f"""
{EMOJI['info']} 账户信息：
👤 用户名：{username}
{EMOJI['balance']} 当前余额：{balance:.2f}元
💰 费用标准：{fee_per_day:.2f}元/天/账号
{EMOJI['jd']} 绑定JD账号：{pin_count}个
"""
        sender.reply(user_info_msg)
        
        # 显示JD账号列表
        pin_list_msg = f"{EMOJI['jd']} 请选择要续费的JD账号：\n"
        for i, pin in enumerate(pin_accounts, 1):
            expiry_date, days_left = get_pin_expiry_info(pin, pin_expiry_data)
            if expiry_date == "未开通":
                expiry_text = "未开通"
            else:
                if days_left > 0:
                    expiry_text = f"{expiry_date}（剩余{days_left}天）"
                elif days_left == 0:
                    expiry_text = f"{expiry_date}（今天到期）"
                else:
                    expiry_text = f"{expiry_date}（已过期{-days_left}天）"
            
            pin_list_msg += f"{i}. {pin} - {expiry_text}\n"
        
        pin_list_msg += f"{len(pin_accounts) + 1}. 续费所有账号\n"
        pin_list_msg += f"{len(pin_accounts) + 2}. 批量续费多个账号"
        
        sender.reply(pin_list_msg)
        
        # 获取用户选择
        choice_input = get_user_input(sender, f"请输入要续费的账号编号（1-{len(pin_accounts) + 2}）", EMOJI['jd'])
        if not choice_input:
            return
        
        try:
            choice = int(choice_input)
            if choice < 1 or choice > len(pin_accounts) + 2:
                sender.reply(f"{EMOJI['error']} 编号超出范围")
                return
        except ValueError:
            sender.reply(f"{EMOJI['error']} 请输入有效的编号")
            return
        
        selected_pins = []
        
        if choice == len(pin_accounts) + 1:
            # 续费所有账号
            selected_pins = pin_accounts.copy()
            sender.reply(f"{EMOJI['info']} 已选择续费所有 {len(selected_pins)} 个JD账号")
        elif choice == len(pin_accounts) + 2:
            # 批量续费多个账号
            batch_input = get_user_input(sender, f"请输入要续费的账号编号，多个用逗号分隔（如：1,3,5）", EMOJI['jd'])
            if not batch_input:
                return
            
            try:
                selected_indices = [int(x.strip()) for x in batch_input.split(",") if x.strip()]
                for index in selected_indices:
                    if 1 <= index <= len(pin_accounts):
                        selected_pins.append(pin_accounts[index-1])
                
                if not selected_pins:
                    sender.reply(f"{EMOJI['error']} 未选择任何有效账号")
                    return
                
                sender.reply(f"{EMOJI['info']} 已选择续费 {len(selected_pins)} 个JD账号：{', '.join(selected_pins)}")
            except ValueError:
                sender.reply(f"{EMOJI['error']} 请输入有效的编号")
                return
        else:
            # 续费单个账号
            selected_pin = pin_accounts[choice-1]
            selected_pins = [selected_pin]
            sender.reply(f"{EMOJI['info']} 已选择续费账号：{selected_pin}")
        
        # 选择续费天数
        fee_per_day = get_fee_per_day()
        daily_fee_per_pin = fee_per_day * len(selected_pins)
        
        days_menu = f"""
{EMOJI['time']} 续费天数选择
----------------------------
{EMOJI['jd']} 续费账号：{len(selected_pins)}个
💰 每日总费用：{daily_fee_per_pin:.2f}元
  （{fee_per_day:.2f}元/天/账号 × {len(selected_pins)}个账号）
{EMOJI['balance']} 当前余额：{balance:.2f}元
----------------------------
请选择续费天数：
1. 1天 - {daily_fee_per_pin:.2f}元
2. 7天 - {daily_fee_per_pin*7:.2f}元
3. 30天 - {daily_fee_per_pin*30:.2f}元
4. 自定义天数
"""
        sender.reply(days_menu)
        
        days_choice = get_user_input(sender, "请输入选项编号（1-4）", EMOJI['time'])
        if not days_choice:
            return
        
        if days_choice == "1":
            days = 1
        elif days_choice == "2":
            days = 7
        elif days_choice == "3":
            days = 30
        elif days_choice == "4":
            # 自定义天数
            days_input = get_user_input(sender, f"请输入续费天数（{len(selected_pins)}个账号，总费用={daily_fee_per_pin:.2f}元/天）", EMOJI['time'])
            if not days_input:
                return
            
            try:
                days = int(days_input)
                if days <= 0:
                    sender.reply(f"{EMOJI['error']} 天数必须大于0")
                    return
            except ValueError:
                sender.reply(f"{EMOJI['error']} 请输入有效的天数")
                return
        else:
            sender.reply(f"{EMOJI['error']} 无效的选项")
            return
        
        # 计算总金额
        total_amount = fee_per_day * len(selected_pins) * days
        
        # 检查余额
        if balance < total_amount:
            sender.reply(f"{EMOJI['error']} 余额不足！\n当前余额：{balance:.2f}元\n需要金额：{total_amount:.2f}元\n缺少金额：{total_amount - balance:.2f}元\n请先充值！")
            return
        
        # 确认续费
        confirm_msg = f"""
{EMOJI['warning']} 确认续费
----------------------------
👤 用户名：{username}
{EMOJI['jd']} 续费账号：{len(selected_pins)}个
📅 续费天数：{days}天
💰 单日费用：{fee_per_day:.2f}元/账号/天
💰 每日总费用：{daily_fee_per_pin:.2f}元
💰 总金额：{total_amount:.2f}元
{EMOJI['balance']} 当前余额：{balance:.2f}元
{EMOJI['balance']} 续费后余额：{balance - total_amount:.2f}元
----------------------------
是否确认续费？（输入 y 确认，输入其他取消）
"""
        sender.reply(confirm_msg)
        
        confirm = get_user_input(sender, "确认续费", EMOJI['warning'])
        if not confirm or confirm.lower() != 'y':
            sender.reply(f"{EMOJI['warning']} 已取消续费")
            return
        
        # 执行续费
        success_count = 0
        failed_pins = []
        
        for pin in selected_pins:
            success, new_expiry, used_amount = process_pin_renewal(account, pin, days)
            if success:
                success_count += 1
                sender.reply(f"{EMOJI['success']} 账号 {pin} 续费成功！\n到期时间：{new_expiry}\n消耗金额：{used_amount:.2f}元")
            else:
                failed_pins.append(pin)
                sender.reply(f"{EMOJI['error']} 账号 {pin} 续费失败：{new_expiry}")
        
        # 显示最终结果
        if success_count > 0:
            # 重新获取用户数据以获取最新余额
            user_data = get_user_data(account)
            new_balance = user_data.get("balance", 0.0)
            
            result_msg = f"""
{EMOJI['success']} 续费完成！
----------------------------
✅ 成功续费：{success_count}个账号
{EMOJI['error']} 失败续费：{len(failed_pins)}个账号
💰 总计金额：{total_amount:.2f}元
{EMOJI['balance']} 剩余余额：{new_balance:.2f}元
"""
            if failed_pins:
                result_msg += f"\n失败账号：{', '.join(failed_pins)}"
            
            sender.reply(result_msg)
        else:
            sender.reply(f"{EMOJI['error']} 所有账号续费失败")
            
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 续费失败: {str(e)}")
        print(f"JD账号续费异常: {e}")

def query_expiry(sender):
    """查询到期时间 - 显示账户余额和所有pin账号到期时间"""
    try:
        # 获取当前用户信息
        user_info = get_current_user_info()
        im_type = user_info["im_type"]
        user_id = user_info["user_id"]
        
        print(f"[查询请求] im_type={im_type}, user_id={user_id}")
        
        # 通过 IM类型 + 用户ID 查找账号
        account = find_account_by_user(im_type, user_id)
        
        if not account:
            sender.reply(f"{EMOJI['warning']} 未找到您绑定的账号，请先使用【绑定拼车账号】绑定")
            return
        
        # 刷新用户的pin信息
        has_changed, pin_accounts, pin_count = refresh_user_pin_info(account, im_type, user_id)
        
        if has_changed:
            sender.reply(f"{EMOJI['info']} 已更新您的JD账号信息，当前绑定{pin_count}个账号")
        
        # 获取用户数据
        user_data = get_user_data(account)
        username = user_data.get("username", "N/A")
        balance = user_data.get("balance", 0.0)
        pin_expiry_data = user_data.get("pin_expiry", {})
        
        # 计算支付记录
        pay_records = user_data.get("pay_records", [])
        total_recharge = sum(record.get("amount", 0) for record in pay_records if record.get("type") == "recharge")
        total_pin_payment = sum(record.get("amount", 0) for record in pay_records if record.get("type") == "pin_renewal")
        
        # 计算最早和最晚到期时间
        earliest_expiry = None
        latest_expiry = None
        
        for pin in pin_accounts:
            expiry_date = pin_expiry_data.get(pin, "")
            if expiry_date and expiry_date != "":
                try:
                    expiry_datetime = datetime.datetime.strptime(expiry_date, "%Y-%m-%d")
                    if earliest_expiry is None or expiry_datetime < earliest_expiry:
                        earliest_expiry = expiry_datetime
                    if latest_expiry is None or expiry_datetime > latest_expiry:
                        latest_expiry = expiry_datetime
                except:
                    pass
        
        # 显示账户信息
        account_info = f"""
{EMOJI['time']} 账户信息查询
----------------------------
👤 用户名：{username}
📱 绑定渠道：{im_type}
{EMOJI['balance']} 账户余额：{balance:.2f}元
💳 累计充值：{total_recharge:.2f}元
💰 累计续费：{total_pin_payment:.2f}元
{EMOJI['jd']} 绑定JD账号：{pin_count}个
"""
        
        if earliest_expiry and latest_expiry:
            today = datetime.datetime.now()
            earliest_days = (earliest_expiry - today).days
            latest_days = (latest_expiry - today).days
            
            earliest_text = f"{earliest_expiry.strftime('%Y-%m-%d')}"
            if earliest_days > 0:
                earliest_text += f"（剩余{earliest_days}天）"
            elif earliest_days == 0:
                earliest_text += "（今天到期）"
            else:
                earliest_text += f"（已过期{-earliest_days}天）"
            
            latest_text = f"{latest_expiry.strftime('%Y-%m-%d')}"
            if latest_days > 0:
                latest_text += f"（剩余{latest_days}天）"
            elif latest_days == 0:
                latest_text += "（今天到期）"
            else:
                latest_text += f"（已过期{-latest_days}天）"
            
            account_info += f"📅 最早到期：{earliest_text}\n"
            account_info += f"📅 最晚到期：{latest_text}\n"
        
        sender.reply(account_info)
        
        # 显示每个pin账号的详细信息
        if pin_count > 0:
            pin_details = f"{EMOJI['jd']} JD账号详情：\n"
            
            for i, pin in enumerate(pin_accounts, 1):
                expiry_date, days_left = get_pin_expiry_info(pin, pin_expiry_data)
                
                if expiry_date == "未开通":
                    expiry_text = "未开通"
                else:
                    if days_left > 0:
                        expiry_text = f"{expiry_date}（剩余{days_left}天）"
                    elif days_left == 0:
                        expiry_text = f"{expiry_date}（今天到期）"
                    else:
                        expiry_text = f"{expiry_date}（已过期{-days_left}天）"
                
                # 计算该账号的累计续费金额
                pin_total = sum(record.get("amount", 0) for record in pay_records 
                              if record.get("type") == "pin_renewal" and record.get("pin") == pin)
                
                pin_details += f"{i}. {pin}\n"
                pin_details += f"   到期时间：{expiry_text}\n"
            
            sender.reply(pin_details)
        
        # 显示最近支付记录
        recent_records = []
        for record in reversed(pay_records[-5:]):  # 显示最近5条记录
            record_type = record.get("type", "")
            if record_type == "recharge":
                record_desc = f"充值 {record.get('amount', 0):.2f}元"
            elif record_type == "pin_renewal":
                record_desc = f"续费 {record.get('pin', '未知')} {record.get('days', 0)}天 {record.get('amount', 0):.2f}元"
            else:
                record_desc = f"未知操作 {record.get('amount', 0):.2f}元"
            
            recent_records.append(f"{record.get('pay_time', 'N/A')} - {record_desc}")
        
        if recent_records:
            records_info = f"📊 最近交易记录：\n" + "\n".join(recent_records)
            #sender.reply(records_info)
        
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 查询失败: {str(e)}")
        print(f"查询到期异常: {e}")

def set_default_fee(sender):
    """设置默认费用（交互式）"""
    
    current_fee = get_fee_per_day()
    amount_input = get_user_input(sender, f"请输入JD代挂每日金额（当前：{current_fee:.2f}元/账号/天）", EMOJI['money'])
    if not amount_input:
        return
    
    try:
        amount = float(amount_input)
        if amount <= 0:
            sender.reply(f"{EMOJI['error']} 金额必须大于0")
            return
        
        set_fee_per_day(amount)
        sender.reply(f"{EMOJI['success']} JD代挂日单价已设置为 {amount:.2f} 元/账号/天")
        
    except ValueError:
        sender.reply(f"{EMOJI['error']} 请输入有效的数字")
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 设置失败：{str(e)}")

def adjust_user_balance(sender):
    """调整用户余额（管理员功能）"""
    try:
        # 检查管理员权限
        is_admin = sender.isAdmin()
        if not is_admin:
            sender.reply(f"{EMOJI['error']} 此功能仅管理员可用")
            return
        
        # 获取要调整的用户
        user_id_input = get_user_input(sender, "请输入要调整的用户ID（userid）：", EMOJI['user'])
        if not user_id_input:
            return
        
        # 查找账号
        account = find_account_by_user_id(user_id_input)
        if not account:
            sender.reply(f"{EMOJI['error']} 未找到用户ID为 {user_id_input} 的账号")
            return
        
        # 获取用户数据
        user_data = get_user_data(account)
        username = user_data.get("username", "N/A")
        current_balance = user_data.get("balance", 0.0)
        
        sender.reply(f"{EMOJI['info']} 找到用户：{username}\n当前余额：{current_balance:.2f}元")
        
        # 获取调整金额
        amount_input = get_user_input(sender, "请输入调整金额（正数为增加，负数为减少）：", EMOJI['money'])
        if not amount_input:
            return
        
        try:
            amount = float(amount_input)
            if amount == 0:
                sender.reply(f"{EMOJI['error']} 调整金额不能为0")
                return
        except ValueError:
            sender.reply(f"{EMOJI['error']} 请输入有效的数字")
            return
        
        # 获取调整原因
        reason_input = get_user_input(sender, "请输入调整原因：", EMOJI['info'])
        if not reason_input:
            reason = "管理员调整"
        else:
            reason = reason_input
        
        # 计算新余额
        new_balance = current_balance + amount
        
        if new_balance < 0:
            sender.reply(f"{EMOJI['error']} 调整后余额不能为负数")
            return
        
        # 确认调整
        confirm_msg = f"""
{EMOJI['warning']} 确认调整用户余额
----------------------------
👤 用户名：{username}
💰 当前余额：{current_balance:.2f}元
{'➕' if amount > 0 else '➖'} 调整金额：{amount:.2f}元
💰 调整后余额：{new_balance:.2f}元
📝 调整原因：{reason}
----------------------------
是否确认调整？（输入 y 确认，输入其他取消）
"""
        sender.reply(confirm_msg)
        
        confirm = get_user_input(sender, "确认调整", EMOJI['warning'])
        if not confirm or confirm.lower() != 'y':
            sender.reply(f"{EMOJI['warning']} 已取消调整")
            return
        
        # 执行调整
        user_data["balance"] = new_balance
        
        # 添加调整记录
        new_record = {
            "order_id": f"ADJUST_{int(time.time())}",
            "amount": amount,
            "description": f"管理员调整：{reason}",
            "pay_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "admin_adjustment",
            "admin": sender.getUserID() or "unknown"
        }
        
        if "pay_records" not in user_data:
            user_data["pay_records"] = []
        user_data["pay_records"].append(new_record)
        
        save_user_data(user_data)
        
        result_msg = f"""
{EMOJI['success']} 用户余额调整成功！
----------------------------
👤 用户名：{username}
💰 调整前余额：{current_balance:.2f}元
{'➕' if amount > 0 else '➖'} 调整金额：{amount:.2f}元
💰 调整后余额：{new_balance:.2f}元
📝 调整原因：{reason}
⏰ 调整时间：{new_record['pay_time']}
"""
        sender.reply(result_msg)
        
    except Exception as e:
        sender.reply(f"{EMOJI['error']} 调整用户余额失败: {str(e)}")
        print(f"调整用户余额异常: {e}")

# ---------- 主函数 ----------
def main():
    sender = middleware.Sender(middleware.getSenderID())
    content = sender.getMessage().strip()
    
    try:
        is_admin = sender.isAdmin()
    except Exception as e:
        print(f"检查管理员权限失败: {e}")
        is_admin = False
    
    print(f"[权限检查] 用户: {sender.getUserID()}, 是管理员: {is_admin}, 命令: {content}")
    
    if content == "收款助手":
        start_collection_assistant(sender)
    
    elif content == "绑定账号":
        bind_account_interactive(sender)
    
    elif content == "我要充值":
        recharge_balance(sender)
    
    elif content == "续费账号":
        renew_jd_account(sender)
    
    elif content == "查询到期":
        query_expiry(sender)
    
    elif content == "设置默认费用":
        if is_admin:
            set_default_fee(sender)
        else:
            sender.reply(f"{EMOJI['error']} 此功能仅管理员可用")
    
    elif content == "收款助手到期检查":
        if is_admin:
            check_expiry_and_send_reminders(sender)
        else:
            sender.reply(f"{EMOJI['error']} 此功能仅管理员可用")
    
    elif content == "调整收款助手余额":
        if is_admin:
            adjust_user_balance(sender)
        else:
            sender.reply(f"{EMOJI['error']} 此功能仅管理员可用")
    
    else:
        sender.reply(f"{EMOJI['error']} 未知命令，请输入【收款助手】查看帮助")

if __name__ == "__main__":
    main()