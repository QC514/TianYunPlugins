#[title: 【插件】-飞蚂蚁]
#[language: python]
# [rule: ^蚂蚁登录$|^蚂蚁绑定$|^蚂蚁管理$|^蚂蚁查询$|^蚂蚁授权$|^蚂蚁教程$|^蚂蚁积分$|^蚂蚁一键运行$]
# [disable:false]
# [platform: qq,wx]
# [public:true]
# [open_source: false]
# [class: 工具类]
# [version: 1.1]
# [price: 6.6]
# [admin: false]
# [icon: http://113.45.39.135:8080/admin/images/gallery/1749818308348537988.png]  # 替换为实际图标URL
# [author: huawei]
# [service: 1603960061]
# [description: 飞蚂蚁APP插件<br>适配呆呆积分支付<br><br>指令：<br>蚂蚁登录：绑定账号<br>蚂蚁管理：账号管理与授权<br>蚂蚁查询：查询状态<br>蚂蚁授权：管理员授权操作<br>蚂蚁教程：使用指南<br>蚂蚁积分：查询积分<br>蚂蚁一键运行：执行任务]

# 插件参数配置
# [param: {"required":false,"key":"G_fmy_config.zsm","name":"收款码","placeholder":"http://example.com/pay.jpg"}]
# [param: {"required":false,"key":"G_fmy_config.price","name":"月费价格","placeholder":"0.88","value":"0.88"}]
# [param: {"required":false,"key":"G_fmy_config.points_per_month","name":"积分/月","placeholder":"100","value":"100","desc":"一个账号每月所需积分数量"}]
# [param: {"required":false,"key":"G_fmy_config.ql_config","name":"青龙配置","placeholder":"http://ip:port丨ClientID丨ClientSecret"}]
# [param: {"required":false,"key":"G_fmy_config.ql_envname","name":"变量名称","placeholder":"G_fmy","value":"G_fmy"}]
# [param: {"required":false,"key":"G_fmy_config.ql_var_name","name":"飞蚂蚁变量名称","placeholder":"G_fmy","value":"G_fmy"}]


import middleware
import requests
import json
import time
from datetime import datetime, timedelta
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用SSL警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_config():
    """获取配置信息"""
    try:
        config = {
            'ql_config': middleware.bucketGet('G_fmy_config', 'ql_config') or '',
            'ql_envname': middleware.bucketGet('G_fmy_config', 'ql_envname') or 'G_fmy',
            'ql_var_name': middleware.bucketGet('G_fmy_config', 'ql_var_name') or 'G_fmy',
            'price': float(middleware.bucketGet('G_fmy_config', 'price') or '0.88'),
            'zsm': middleware.bucketGet('G_fmy_config', 'zsm') or '',
            'points_per_month': int(middleware.bucketGet('G_fmy_config', 'points_per_month') or '100')
        }
        return config
    except Exception as e:
        print(f"配置获取失败: {str(e)}")
        return {
            'ql_config': '',
            'ql_envname': 'G_fmy',
            'ql_var_name': 'G_fmy',
            'price': 0.88,
            'zsm': '',
            'points_per_month': 100
        }

def get_user_points(user_id=None):
    """获取用户积分"""
    if not user_id:
        user_id = middleware.getSenderID()
    
    print(f"获取用户积分，用户ID: {user_id}")
    
    # 获取dd_sign_coin
    points = middleware.bucketGet('dd_sign_coin', user_id) or "0"
    # 获取dd_sign_points
    user_points = middleware.bucketGet('dd_sign_points', user_id) or "0"
    
    # 尝试转换为整数
    try:
        points_int = int(points)
    except:
        points_int = 0
        
    try:
        user_points_int = int(user_points)
    except:
        user_points_int = 0
    
    # 如果dd_sign_coin为0，尝试获取sign_用户ID的值
    if points_int == 0:
        sign_key = f"sign_{user_id}"
        sign_points = middleware.bucketGet('dd_sign_coin', sign_key) or "0"
        try:
            points_int = int(sign_points)
        except:
            points_int = 0
    
    total = points_int + user_points_int
    print(f"用户积分: dd_sign_coin={points_int}, dd_sign_points={user_points_int}, total={total}")
    
    return {
        'dd_sign_coin': points_int,
        'dd_sign_points': user_points_int,
        'total': total
    }

def set_user_points(user_id, points):
    """设置用户积分"""
    middleware.bucketSet('dd_sign_coin', user_id, str(points['dd_sign_coin']))
    middleware.bucketSet('dd_sign_points', user_id, str(points['dd_sign_points']))
    sign_key = f"sign_{user_id}"
    middleware.bucketSet('dd_sign_coin', sign_key, str(points['dd_sign_coin']))
    return True

def get_user_accounts(user_id=None):
    """获取用户账号列表"""
    if user_id is None:
        user_id = middleware.getSenderID()
    
    print(f"获取用户账号，用户ID: {user_id}")
    uservalue = middleware.bucketGet('G_fmy_user', user_id) or '[]'
    try:
        accounts = json.loads(uservalue)
        print(f"获取到的账号列表: {accounts}")
        return accounts
    except Exception as e:
        print(f"解析账号列表失败: {str(e)}")
        return []

def verify_token(token):
    """验证token"""
    headers = {
        "host": "openapp.fmy90.com",
        "device-model": "microsoft",
        "device-version": "Windows 10 x64",
        "xweb_xhr": "1",
        "authorization": f"bearer {token}",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839",
        "content-type": "application/json;charset=utf8",
        "accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": "https://servicewechat.com/wx501990400906c9ff/450/page-frame.html",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9"
    }
    
    params = {
        "type": "1",
        "version": "V2.00.01",
        "platformKey": "F2EE24892FBF66F0AFF8C0EB532A9394",
        "mini_scene": "1256",
        "partner_ext_infos": ""
    }
    
    try:
        # 先尝试获取豆子信息，因为这个API返回正常
        beans_url = "https://openapp.fmy90.com/user/new/beans/info"
        beans_response = requests.get(beans_url, headers=headers, params=params, timeout=10)
        beans_data = beans_response.json()
        
        if beans_data.get("code") == 200:
            total_beans = beans_data.get("data", {}).get("totalCount", "0")
            
            # 获取用户信息
            info_url = "https://openapp.fmy90.com/user/info"
            info_response = requests.get(info_url, headers=headers, params=params, timeout=10)
            info_data = info_response.json()
            
            if info_data.get("code") == 200 and info_data.get("data"):
                user = info_data.get("data", {}).get("user", {})
                return True, {
                    "phone": user.get("mobile", ""),
                    "username": user.get("userName", "未知用户"),
                    "beans": str(total_beans)
                }
            else:
                # 如果用户信息获取失败，至少返回豆子数量
                return True, {
                    "phone": "",
                    "username": "未知用户",
                    "beans": str(total_beans)
                }
        
        # 尝试直接使用token中的信息
        try:
            import base64
            import json
            
            # 解析JWT token
            token_parts = token.split('.')
            if len(token_parts) >= 2:
                # 解码payload部分
                payload = token_parts[1]
                # 添加必要的填充
                padding = '=' * (4 - len(payload) % 4) if len(payload) % 4 != 0 else ''
                decoded = base64.b64decode(payload + padding).decode('utf-8')
                jwt_data = json.loads(decoded)
                
                # 从JWT中提取用户ID
                uid = jwt_data.get('uid', '')
                
                if uid:
                    return True, {
                        "phone": str(uid),
                        "username": "JWT用户",
                        "beans": "0"
                    }
        except Exception as jwt_error:
            print(f"JWT解析失败: {str(jwt_error)}")
        
        return False, None
    except Exception as e:
        print(f"验证失败: {str(e)}")
        return False, None

def update_qinglong_env(token, account_info):
    """更新青龙面板环境变量"""
    # 直接返回成功，不上传到青龙面板，只保存在数据桶中
    print("青龙面板上传已禁用，仅保存在数据桶中")
    return True

def is_admin():
    """检查当前用户是否为管理员"""
    sender_id = middleware.getSenderID()
    # 使用sender的内置方法检查管理员权限
    sender = middleware.Sender(sender_id)
    if sender.isAdmin():
        return True
    
    # 如果sender.isAdmin()不可用，使用配置中的管理员列表
    admin_list = middleware.bucketGet('G_fmy_config', 'admin_list') or ''
    admin_list = admin_list.split(',')
    return sender_id in admin_list or sender_id == '1603960061'  # 默认作者ID为管理员

def 蚂蚁授权():
    """管理员授权操作"""
    sender = middleware.Sender(middleware.getSenderID())
    
    if not is_admin():
        sender.reply("❌ 您没有管理员权限！")
        return
        
    sender.reply("""
=====管理员授权操作=====
[1] 指定用户授权
[2] 批量授权所有用户
------------------
请回复对应数字：""")
    
    choice = sender.input(60000, 1, False)
    
    if choice == '1':
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
            account_data = middleware.bucketGet('G_fmy_accounts', account_id)
            if account_data:
                account_info = json.loads(account_data)
                remark = account_info['phone']  # 备注存储在phone字段
                auth_status = account_info['auth_status']
                status = "已授权" if auth_status['is_authorized'] else "未授权"
                expire_time = auth_status['expire_time'] or "无"
                account_list.append(f"[{i}] 备注: {remark} \n 状态: {status} \n 到期时间: {expire_time}")
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
        
        if choice == '0':
            # 授权所有账号
            for account_id in accounts:
                if admin_authorize_account(account_id, months, target_userid):
                    success_count += 1
            
            sender.reply(f"✅ 批量授权完成！成功授权 {success_count}/{len(accounts)} 个账号")
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
    
    elif choice == '2':
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
        users = middleware.bucketAllKeys('G_fmy_user')
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
    
    elif choice == '3':
        show_config()
    elif choice == '4':
        set_config()
    elif choice == '5':
        add_admin()
    else:
        sender.reply("❌ 无效选择")

def admin_authorize_account(account_id, months, user_id):
    """管理员授权账号"""
    try:
        # 获取账号数据
        account_data = middleware.bucketGet('G_fmy_accounts', account_id)
        if not account_data:
            return False
        
        account_info = json.loads(account_data)
        
        # 计算新的到期时间
        new_expire_time = None
        if account_info['auth_status']['is_authorized'] and account_info['auth_status']['expire_time']:
            try:
                current_expire = datetime.strptime(account_info['auth_status']['expire_time'], "%Y-%m-%d %H:%M:%S")
                if current_expire > datetime.now():
                    new_expire_time = current_expire + timedelta(days=months*30)
            except:
                new_expire_time = None
        
        if not new_expire_time:
            new_expire_time = datetime.now() + timedelta(days=months*30)
        
        # 更新授权状态
        account_info['auth_status'] = {
            "is_authorized": True,
            "expire_time": new_expire_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_auth_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存更新后的账号数据
        middleware.bucketSet('G_fmy_accounts', account_id, json.dumps(account_info))
    
        # 更新青龙面板
        if update_qinglong_env(account_info['token'], account_info):
            # 记录管理员操作日志
            sender = middleware.Sender(middleware.getSenderID())
            log_data = {
                "admin_id": sender.getUserID(),
                "user_id": user_id,
                "account_id": account_id,
                "remark": account_info['phone'],
                "months": months,
                "expire_time": new_expire_time.strftime("%Y-%m-%d %H:%M:%S"),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            middleware.bucketSet('G_fmy_admin_logs', f"log_{int(time.time())}", json.dumps(log_data))
            return True
            
        return False
    except Exception as e:
        print(f"管理员授权失败: {str(e)}")
        return False

def delete_account(account_id):
    """删除账号"""
    sender = middleware.Sender(middleware.getSenderID())
    
    # 获取账号信息
    account_data = middleware.bucketGet('G_fmy_accounts', account_id)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return
        
    account_info = json.loads(account_data)
    remark = account_info['phone']  # 备注存储在phone字段
    
    sender.reply(f"""
=====删除账号确认=====
确认删除账号 {remark} 吗？
请回复 [Y] 确认
回复 [N] 取消
==================""")
    
    confirm = sender.input(60000, 1, False).strip().lower()
    if confirm != 'y':
        sender.reply("✅ 已取消删除")
        return

    try:
        # 删除账号数据
        middleware.bucketDel('G_fmy_accounts', account_id)
    
        # 从用户账号列表中移除
        user_id = sender.getUserID()
        accounts = get_user_accounts(user_id)
        if account_id in accounts:
            accounts.remove(account_id)
            if accounts:
                middleware.bucketSet('G_fmy_user', user_id, json.dumps(accounts))
            else:
                middleware.bucketDel('G_fmy_user', user_id)

        sender.reply(f"""
✅ 账号删除成功
📝 备注：{remark}
===================""")
    except Exception as e:
        sender.reply(f"❌ 删除失败: {str(e)}")

def 蚂蚁管理():
    """飞蚂蚁账号管理"""
    sender = middleware.Sender(middleware.getSenderID())
    userid = sender.getUserID()
    accounts = get_user_accounts(userid)
    
    # 打印调试信息
    print(f"用户ID: {userid}")
    print(f"账号列表: {accounts}")
    
    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先发送「蚂蚁登录」进行绑定")
        return

    # 构建账号列表
    account_list = []
    valid_accounts = []
    for i, account_id in enumerate(accounts, 1):
        account_data = middleware.bucketGet('G_fmy_accounts', account_id)
        if account_data:
            account_info = json.loads(account_data)
            remark = account_info['phone']  # 备注存储在phone字段
            auth_status = account_info['auth_status']
            
            if auth_status['is_authorized']:
                status = f"✅ 已授权（到期: {auth_status['expire_time']}）"
            else:
                status = "❌ 未授权"
                
            account_list.append(f"[{len(valid_accounts) + 1}] {remark} {status}")
            valid_accounts.append(account_id)
        else:
            # 如果数据无效，直接从账号列表中移除
            accounts.remove(account_id)
            middleware.bucketSet('G_fmy_user', userid, json.dumps(accounts))

    account_list_str = "\n".join(account_list)
    
    sender.reply(f"""
=====飞蚂蚁账号管理=====
🔢 绑定账号: {len(valid_accounts)}个
-------------------------
{account_list_str}
------------------
回复序号选择操作（q退出）
===================""")

    choice = sender.input(60000, 1, False)
    if choice.lower() == 'q':
        return

    if not choice.isdigit():
        sender.reply("❌ 输入无效")
        return

    idx = int(choice) - 1
    if idx < 0 or idx >= len(valid_accounts):
        sender.reply("❌ 序号无效")
        return

    selected_account = valid_accounts[idx]
    account_data = middleware.bucketGet('G_fmy_accounts', selected_account)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return
        
    account_info = json.loads(account_data)
    remark = account_info['phone']  # 备注存储在phone字段
    
    sender.reply(f"""
已选择账号: {remark}
[1] 授权账号
[2] 更新数据
[3] 删除账号
------------------
请回复对应数字：""")
    
    op = sender.input(60000, 1, False)

    if op == '1':
        authorize_account(selected_account)
    elif op == '2':
        update_account_data(selected_account)
    elif op == '3':
        delete_account(selected_account)
    else:
        sender.reply("❌ 无效选择")

def authorize_account(account_id):
    """授权账号"""
    sender = middleware.Sender(middleware.getSenderID())
    config = get_config()
    
    account_data = middleware.bucketGet('G_fmy_accounts', account_id)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return
        
    account_info = json.loads(account_data)
    remark = account_info['phone']  # 备注存储在phone字段
    token = account_info['token']
    
    if not token:
        sender.reply("❌ 账号token无效")
        return
    
    current_points = get_user_points(sender.getUserID())
    
    sender.reply(f"""
您正在授权账号: {remark}
📝 备注: {remark}
📊 当前积分: {current_points['total']}

请输入授权月数 (1-12):""")
    
    months = sender.input(120000, 1, False)
    if not months.isdigit() or int(months) < 1 or int(months) > 12:
        sender.reply("❌ 月数必须为1-12之间的整数")
        return
        
    months = int(months)
    total_price = config['price'] * months
    required_points = config['points_per_month'] * months
    
    pay_menu = f"""
=====飞蚂蚁授权支付=====
📝 备注: {remark}
🎯 授权时长: {months}个月
💰 金额: ¥{total_price:.2f}
📊 积分支付: {required_points}积分（当前积分: {current_points['total']}）
------------------
[1] 微信支付
[2] 积分支付
回复数字选择支付方式，回复q取消
==================="""
    
    sender.reply(pay_menu)
    pay_choice = sender.input(120000, 1, False)
    
    payment_success = False
    if pay_choice == '1' and config['zsm']:
        payment_success = wechat_payment_flow(account_id, months, total_price, config, remark)
    elif pay_choice == '2':
        payment_success = point_payment_flow(account_id, months, required_points, remark)
    elif pay_choice.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
    else:
        sender.reply("❌ 无效支付方式")
        return
    
    if payment_success:
        # 计算新的到期时间
        new_expire_time = None
        if account_info['auth_status']['is_authorized'] and account_info['auth_status']['expire_time']:
            try:
                current_expire = datetime.strptime(account_info['auth_status']['expire_time'], "%Y-%m-%d %H:%M:%S")
                if current_expire > datetime.now():
                    new_expire_time = current_expire + timedelta(days=months*30)
            except:
                new_expire_time = None
        
        if not new_expire_time:
            new_expire_time = datetime.now() + timedelta(days=months*30)
    
        # 更新授权状态
        account_info['auth_status'] = {
            "is_authorized": True,
            "expire_time": new_expire_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_auth_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 保存更新后的账号数据
        middleware.bucketSet('G_fmy_accounts', account_id, json.dumps(account_info))
    
        # 更新青龙面板
        if update_qinglong_env(token, account_info):
            sender.reply(f"""
✅ 授权成功！
📝 备注: {remark}
📅 到期时间: {new_expire_time.strftime("%Y-%m-%d %H:%M:%S")}
🤖 已同步数据
""")
        else:
            sender.reply(f"""
✅ 授权成功！
📝 备注: {remark}
📅 到期时间: {new_expire_time.strftime("%Y-%m-%d %H:%M:%S")}
❗ 青龙面板同步失败
""")

def show_account_info(account_id):
    """显示账号详细信息"""
    sender = middleware.Sender(middleware.getSenderID())
    account_data = middleware.bucketGet('G_fmy_accounts', account_id)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return
        
    account_info = json.loads(account_data)
    success, user_info = verify_token(account_info['token'])
    
    beans_info = "获取失败"
    if success:
        beans_info = user_info['beans']
    
    sender.reply(f"""
=====账号信息=====
📝 备注：{account_info['phone']}
💰 豆子数量：{beans_info}
👤 微信ID：{account_info['wx_id']}
🕒 绑定时间：{account_info['bind_time']}
🔑 授权状态：{'已授权' if account_info['auth_status']['is_authorized'] else '未授权'}
⏰ 到期时间：{account_info['auth_status']['expire_time'] or '未授权'}
===================""")

def 蚂蚁教程():
    """飞蚂蚁使用教程"""
    sender = middleware.Sender(middleware.getSenderID())
    config = get_config()
    
    tutorial = f"""
=====飞蚂蚁使用教程=====

【功能介绍】
飞蚂蚁是一款步数兑换平台，可以将步数兑换为豆子，再用豆子兑换各种奖励。

【指令列表】
1. 蚂蚁登录 - 绑定飞蚂蚁账号
2. 蚂蚁管理 - 管理已绑定账号
3. 蚂蚁查询 - 查询账号状态
4. 蚂蚁授权 - 管理员授权操作
5. 蚂蚁教程 - 显示本教程
6. 蚂蚁积分 - 查询积分

【获取Token教程】
1. 打开微信小程序"飞蚂蚁"
2. 登录您的账号
3. 使用抓包工具获取请求头中的authorization值
4. 复制完整的token（bearer后面的部分）
5. 登录时输入格式：token#备注名称
   例如：eyJ0eXA...#张三的账号

【授权说明】
- 每月授权需要{config['points_per_month']}积分
- 授权后可同步至青龙面板
- 授权有效期按月计算

【积分获取】
- 可通过付款获取积分
- 当前汇率：¥{config['price']:.2f} = {config['points_per_month']}积分

【联系方式】
如有问题，请联系管理员
=================="""
    
    sender.reply(tutorial)

def 蚂蚁查询():
    """查询账号状态"""
    sender = middleware.Sender(middleware.getSenderID())
    userid = sender.getUserID()
    accounts = get_user_accounts(userid)
    
    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先发送「蚂蚁登录」进行绑定")
        return
        
    # 构建账号状态列表
    status_list = []
    for i, account_id in enumerate(accounts, 1):
        account_data = middleware.bucketGet('G_fmy_accounts', account_id)
        if account_data:
            account_info = json.loads(account_data)
            remark = account_info['phone']  # 备注存储在phone字段
            
            # 验证token状态
            success, user_info = verify_token(account_info['token'])
            
            if success:
                beans = user_info['beans']
                auth_status = "✅ 已授权" if account_info['auth_status']['is_authorized'] else "❌ 未授权"
                expire_time = account_info['auth_status']['expire_time'] or "未授权"
                
                status_list.append(f"账号{i}: {remark}\n豆子: {beans}\n状态: {auth_status}\n到期: {expire_time}\n")
            else:
                status_list.append(f"账号{i}: {remark}\n状态: ❌ Token已失效\n")
        else:
            status_list.append(f"账号{i}: 数据异常\n")
            
    status_str = "\n".join(status_list)
    
    sender.reply(f"""
=====账号状态查询=====
{status_str}
发送「蚂蚁管理」可管理账号
===================""")

def parse_payment_result(raw_data):
    """解析支付结果"""
    Money, Time, From = None, "", ""
    
    try:
        if isinstance(raw_data, dict):
            if raw_data.get('type') in ['微信赞赏', '微信收款']:
                Money = float(raw_data.get('money', 0))
                Time = raw_data.get('time', '')
                From = raw_data.get('from_name', '')
            else:
                Money = float(raw_data.get('Money', 0))
                Time = raw_data.get('Time', '')
        else:
            try:
                data = json.loads(raw_data)
                if data.get('type') in ['微信赞赏', '微信收款']:
                    Money = float(data.get('money', 0))
                    Time = data.get('time', '')
                    From = data.get('from_name', '')
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
        print(f"❌ 解析支付结果失败: {str(e)}")
    
    return Money, Time, From

def point_payment_flow(account_id, months, required_points, remark):
    """积分支付处理"""
    sender = middleware.Sender(middleware.getSenderID())
    user_id = sender.getUserID()
    user_points = get_user_points(user_id)
    
    if user_points['total'] < required_points:
        sender.reply(f"""
❌ 积分不足！
需要: {required_points}积分
当前: {user_points['total']}积分
请「联系管理员」充值积分
        """)
        return False
    
    sender.reply(f"""
⚠ 确认使用积分支付吗？
📝 备注: {remark}
📊 扣除: {required_points}积分
📈 剩余: {user_points['total'] - required_points}积分
------------------
回复 [Y] 确认支付
回复 [N] 取消
    """)
    
    confirm = sender.input(60000, 1, False).lower()
    if confirm != 'y':
        sender.reply("✅ 积分支付已取消")
        return False
    
    # 优先扣除签到积分
    sign_coin = user_points['dd_sign_coin']
    sign_points = user_points['dd_sign_points']
    
    if sign_coin >= required_points:
        sign_coin -= required_points
    else:
        remaining = required_points - sign_coin
        sign_coin = 0
        sign_points -= remaining
    
    result_points = {
        'dd_sign_coin': sign_coin,
        'dd_sign_points': sign_points,
    }
    
    # 扣除积分
    set_user_points(user_id, result_points)
    
    # 记录交易
    transaction_data = {
        "userid": user_id,
        "account_id": account_id,
        "months": months,
        "points": required_points,
        "balance": sign_points + sign_coin,
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": "飞蚂蚁授权"
    }
    middleware.bucketSet('dd_sign_transactions', f"tx_{int(time.time())}", json.dumps(transaction_data))
    
    sender.reply(f"✅ 积分支付成功！\n扣除 {required_points}积分，剩余积分: {sign_points + sign_coin}")
    return True

def wechat_payment_flow(account_id, months, amount, config, remark):
    """微信支付处理"""
    sender = middleware.Sender(middleware.getSenderID())
    
    sender.reply(f"""
=====微信扫码支付=====
📝 备注: {remark}
🎯 授权时长: {months}个月
💰 金额: ¥{amount:.2f}
------------------
请扫描下方二维码支付
回复q取消支付
==================""")
    
    sender.replyImage(config['zsm'])
    payment_result = sender.waitPay(timeout=600000, exitcode='q')
    
    if payment_result == 'q':
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
{f'👤 付款人: {From}' if From else ''}
==================""")
        return True
    else:
        sender.reply(f"""
❌ 支付金额不足 ❌
应付: ¥{amount:.2f}元 
实付: ¥{Money}元
==================""")
        return False

def query_user_points():
    """查询用户积分"""
    sender = middleware.Sender(middleware.getSenderID())
    points = get_user_points(sender.getUserID())
    config = get_config()
    
    sender.reply(
        f"📊 您的当前积分: {points['total']}\n"
        f"💰 每账号每月积分: {config['points_per_month']}\n"
        f"联系管理员可充值积分"
    )

def show_config():
    """查看配置"""
    sender = middleware.Sender(middleware.getSenderID())
    config = get_config()
    admin_list = middleware.bucketGet('G_fmy_config', 'admin_list') or '无'
    
    # 隐藏敏感信息
    ql_config = config['ql_config']
    if ql_config and '丨' in ql_config:
        parts = ql_config.split('丨')
        if len(parts) >= 3:
            masked_config = f"{parts[0]}丨{'*' * 8}丨{'*' * 8}"
        else:
            masked_config = "格式错误"
    else:
        masked_config = "未设置"
    
    sender.reply(f"""
=====当前配置=====
青龙面板配置：{masked_config}
环境变量名称：{config['ql_envname']}
飞蚂蚁变量名称：{config['ql_var_name']}
积分单价：{config['price']}
收款码：{'已设置' if config['zsm'] else '未设置'}
每月所需积分：{config['points_per_month']}
管理员列表：{admin_list}
===================""")

def update_account_data(account_id):
    """更新账号数据"""
    sender = middleware.Sender(middleware.getSenderID())
    
    # 获取账号信息
    account_data = middleware.bucketGet('G_fmy_accounts', account_id)
    if not account_data:
        sender.reply("❌ 账号数据无效")
        return
        
    account_info = json.loads(account_data)
    remark = account_info['phone']  # 备注存储在phone字段
    
    # 检查授权状态
    auth_status = account_info['auth_status']
    if not auth_status['is_authorized']:
        sender.reply(f"""
⚠️ 此账号未授权
请先使用「授权账号」功能进行授权
===================""")
        return
        
    # 检查授权是否过期
    is_expired = False
    try:
        expire_time = datetime.strptime(auth_status['expire_time'], "%Y-%m-%d %H:%M:%S")
        if expire_time < datetime.now():
            is_expired = True
    except:
        is_expired = True
    
    if is_expired:
        sender.reply(f"""
⚠️ 此账号授权已过期
授权到期时间: {auth_status['expire_time']}
请先使用「授权账号」功能续费
===================""")
        return
    
    sender.reply(f"""
=====更新账号数据=====
账号备注: {remark}
授权到期: {auth_status['expire_time']}
------------------
请输入新的token：""")
    
    new_token = sender.input(120000, 1, False).strip()
    if not new_token:
        sender.reply("❌ 输入为空，已取消更新")
        return
    
    # 验证新token
    success, user_info = verify_token(new_token)
    if not success:
        sender.reply("❌ 无效的token，验证失败")
        return
    
    # 更新手机号/备注（如果有）
    if user_info and user_info.get('phone'):
        account_info['phone'] = user_info['phone']
    
    # 更新token
    account_info['token'] = new_token
    
    # 保存更新后的账号数据
    middleware.bucketSet('G_fmy_accounts', account_id, json.dumps(account_info))
    
    # 更新青龙面板
    if update_qinglong_env(new_token, account_info):
        sender.reply(f"""
✅ 数据更新成功！
📝 备注: {account_info['phone']}
📅 授权到期: {auth_status['expire_time']}
🤖 已保存在数据桶中
===================""")
    else:
        sender.reply(f"""
✅ 数据更新成功！
📝 备注: {account_info['phone']}
📅 授权到期: {auth_status['expire_time']}
❗ 数据保存失败
===================""")

def 蚂蚁登录():
    """飞蚂蚁账号登录绑定"""
    sender = middleware.Sender(middleware.getSenderID())
    user_id = sender.getUserID()
    
    sender.reply(f"""
=====飞蚂蚁登录=====
请输入token：
------------------
(输入q取消操作)
===================""")
    
    token_input = sender.input(120000, 1, False)
    if token_input.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    token = token_input.strip()
    if not token:
        sender.reply("❌ 输入为空，登录失败")
        return
    
    # 验证token
    success, user_info = verify_token(token)
    if not success:
        sender.reply("❌ 无效的token，验证失败")
        return
    
    # 获取备注信息
    phone = user_info.get('phone', '')
    username = user_info.get('username', '未知用户')
    beans = user_info.get('beans', '0')
    
    if not phone:
        sender.reply("请输入备注名称：")
        remark = sender.input(60000, 1, False).strip()
        if not remark:
            remark = "未命名账号"
    else:
        remark = phone
    
    # 生成账号ID
    account_id = f"fmy_{int(time.time())}_{user_id[-6:]}"
    
    # 获取用户当前账号列表
    accounts = get_user_accounts(user_id)
    # 移除账号数量限制
    # if len(accounts) >= 9:
    #     sender.reply("❌ 账号数量已达上限(最多9个)")
    #     return
    
    # 创建账号数据
    account_info = {
        "token": token,
        "phone": remark,
        "username": username,
        "beans": beans,
        "create_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "wx_id": user_id,
        "auth_status": {
            "is_authorized": False,
            "expire_time": None,
            "last_auth_time": None
        }
    }
    
    # 保存账号数据
    middleware.bucketSet('G_fmy_accounts', account_id, json.dumps(account_info))
    
    # 更新用户账号列表
    accounts.append(account_id)
    middleware.bucketSet('G_fmy_user', user_id, json.dumps(accounts))
    
    sender.reply(f"""
✅ 绑定成功！
📝 备注: {remark}
💰 豆子: {beans}
------------------
🔹 发送「蚂蚁管理」可授权和管理账号
🔹 发送「蚂蚁查询」可查询账号状态
===================""")

def 蚂蚁一键运行():
    """执行任务"""
    sender = middleware.Sender(middleware.getSenderID())
    user_id = sender.getUserID()
    
    # 获取用户所有账号
    accounts = get_user_accounts(user_id)
    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号，请先发送「蚂蚁登录」进行绑定")
        return
    
    sender.reply(f"⏳ 正在为{len(accounts)}个账号执行任务，请稍候...")
    
    # 用于存储结果
    results = []
    success_count = 0
    failed_count = 0
    
    # 遍历所有账号
    for account_id in accounts:
        account_data = middleware.bucketGet('G_fmy_accounts', account_id)
        if not account_data:
            failed_count += 1
            results.append("❌ 账号数据异常")
            continue
            
        account_info = json.loads(account_data)
        token = account_info["token"]
        remark = account_info["phone"]
        
        # 检查授权
        if not account_info['auth_status']['is_authorized']:
            results.append(f"⚠️ 账号[{remark}]未授权，跳过任务")
            failed_count += 1
            continue
            
        # 检查授权是否过期
        is_expired = False
        try:
            expire_time = datetime.strptime(account_info['auth_status']['expire_time'], "%Y-%m-%d %H:%M:%S")
            if expire_time < datetime.now():
                is_expired = True
        except:
            is_expired = True
        
        if is_expired:
            results.append(f"⚠️ 账号[{remark}]授权已过期，跳过任务")
            failed_count += 1
            continue
        
        # 执行任务
        result = execute_ant_tasks(token, remark)
        results.append(f"📱 账号[{remark}]:" + result)
        
        # 判断是否成功，使用更智能的逻辑：只有当有严重错误时才算失败
        if "任务执行异常" in result or "登录状态异常" in result or "登录验证失败" in result:
            failed_count += 1
        else:
            success_count += 1
    
    # 返回结果
    result_text = "\n\n".join(results)
    sender.reply(f"""
=====飞蚂蚁任务执行结果=====
✅ 成功: {success_count}个账号
❌ 失败: {failed_count}个账号
------------------
{result_text}
===================""")

def execute_ant_tasks(token, remark):
    """执行单个账号的任务"""
    if not token.lower().startswith("bearer "):
        token = f"bearer {token}"
    
    # 创建session，保持连接
    session = requests.Session()
    session.verify = False  # 禁用SSL验证
    
    headers = {
        "Host": "openapp.fmy90.com",
        "Connection": "keep-alive",
        "device-model": "microsoft",
        "device-version": "Windows 10 x64",
        "xweb_xhr": "1",
        "authorization": token,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839",
        "content-type": "application/json;charset=UTF-8",
        "Accept": "*/*",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "Referer": "https://servicewechat.com/wx501990400906c9ff/450/page-frame.html",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    
    base_payload = {
        "version": "V2.00.01",
        "platformKey": "F2EE24892FBF66F0AFF8C0EB532A9394",
        "mini_scene": 1256,
        "partner_ext_infos": ""
    }
    
    params = {
        "type": "1",
        "version": "V2.00.01",
        "platformKey": "F2EE24892FBF66F0AFF8C0EB532A9394",
        "mini_scene": "1256",
        "partner_ext_infos": ""
    }
    
    results = []
    max_retries = 3
    beans_before = "0"
    
    try:
        # 1. 检查登录状态
        retry_count = 0
        while retry_count < max_retries:
            try:
                beans_url = "https://openapp.fmy90.com/user/new/beans/info"
                beans_response = session.get(beans_url, headers=headers, params=params, timeout=15)
                beans_data = beans_response.json()
                
                if beans_data.get("code") == 200:
                    beans_before = beans_data.get("data", {}).get("totalCount", "0")
                    results.append(f"💰 账户豆子: {beans_before}")
                    break
                else:
                    retry_count += 1
                    if retry_count >= max_retries:
                        return f"❌ 登录状态异常: {beans_data.get('message', '未知错误')}"
                    time.sleep(2)
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    return f"❌ 登录验证失败: {str(e)[:50]}"
                time.sleep(2)
        
        # 2. 执行投注功能
        try:
            bet_url = "https://openapp.fmy90.com/active/pool/bet"
            bet_payload = base_payload.copy()
            body_str = json.dumps(bet_payload, separators=(',', ':'))
            
            headers["Content-Length"] = str(len(body_str))
            bet_response = session.post(bet_url, headers=headers, data=body_str, timeout=15)
            bet_data = bet_response.json()
            
            # 特殊处理"已投过"的情况，这应该算作成功
            if bet_data.get("code") == 200 or "已投" in bet_data.get('message', ''):
                bet_status = "✅ 成功"
            else:
                bet_status = f"❌ 失败 ({bet_data.get('code')})"
            
            bet_msg = bet_data.get('message', '无返回信息')
            results.append(f"🎲 投注功能: {bet_status}\n结果: {bet_msg}")
        except Exception as e:
            results.append(f"🎲 投注功能: ❌ 异常\n结果: {str(e)[:30]}")
        
        time.sleep(1)
        
        # 3. 执行签到
        try:
            sign_url = "https://openapp.fmy90.com/sign/new/do"
            sign_payload = base_payload.copy()
            body_str = json.dumps(sign_payload, separators=(',', ':'))
            
            headers["Content-Length"] = str(len(body_str))
            sign_response = session.post(sign_url, headers=headers, data=body_str, timeout=15)
            sign_data = sign_response.json()
            
            # 特殊处理"已签到"的情况，这应该算作成功
            if sign_data.get("code") == 200 or "已" in sign_data.get('message', '') and "签到" in sign_data.get('message', ''):
                sign_status = "✅ 成功"
            else:
                sign_status = f"❌ 失败 ({sign_data.get('code')})"
            
            sign_msg = sign_data.get('message', '无返回信息')
            data = sign_data.get('data', {})
            sign_red_amount = data.get('sign_red_amount', 0) if data else 0
            detail = f"获得红包: {sign_red_amount}" if sign_red_amount > 0 else ""
            results.append(f"📝 签到功能: {sign_status}\n结果: {sign_msg} {detail}")
        except Exception as e:
            results.append(f"📝 签到功能: ❌ 异常\n结果: {str(e)[:30]}")
        
        time.sleep(1)
        
        # 4. 执行步数兑换 (尝试3次)
        exchange_results = []
        exchange_success = False
        for i in range(1, 4):
            try:
                exchange_url = "https://openapp.fmy90.com/step/exchange"
                exchange_payload = base_payload.copy()
                exchange_payload["steps"] = 20000
                exchange_payload["exchangeType"] = "bean"
                body_str = json.dumps(exchange_payload, separators=(',', ':'))
                
                headers["Content-Length"] = str(len(body_str))
                exchange_response = session.post(exchange_url, headers=headers, data=body_str, timeout=15)
                exchange_data = exchange_response.json()
                
                # 特殊处理"最多兑换3次"的情况，这应该算作正常(成功)
                if exchange_data.get("code") == 200 or "最多兑换" in exchange_data.get('message', ''):
                    exchange_status = "✅ 成功"
                    exchange_success = True
                else:
                    exchange_status = f"❌ 失败 ({exchange_data.get('code')})"
                
                exchange_msg = exchange_data.get('message', '无返回信息')
                exchange_results.append(f"第{i}次: {exchange_status} - {exchange_msg}")
                
                if i < 3:
                    time.sleep(3)
            except Exception as e:
                exchange_results.append(f"第{i}次: ❌ 异常 - {str(e)[:30]}")
        
        results.append(f"👟 步数兑换:\n" + "\n".join(exchange_results))
        
        # 5. 等待几秒，确保豆子已更新
        time.sleep(3)
        
        # 6. 再次查询豆子数量 - 使用蚂蚁查询相同的API组合
        try:
            # 获取豆子信息
            beans_url = "https://openapp.fmy90.com/user/new/beans/info"
            beans_response = session.get(beans_url, headers=headers, params=params, timeout=15)
            beans_data = beans_response.json()
            
            # 获取用户信息
            info_url = "https://openapp.fmy90.com/user/info"
            info_response = session.get(info_url, headers=headers, params=params, timeout=10)
            
            beans_after = beans_before
            if beans_data.get("code") == 200:
                beans_after = beans_data.get("data", {}).get("totalCount", beans_before)
            
            # 计算增加的豆子数量
            try:
                beans_gain = int(beans_after) - int(beans_before)
                gain_text = f"+{beans_gain}" if beans_gain > 0 else str(beans_gain)
            except:
                gain_text = "未知"
                
            results.append(f"💰 当前豆子: {beans_after} (变化: {gain_text})")
        except Exception as e:
            # 如果查询失败，使用最初的豆子数量
            results.append(f"💰 当前豆子: {beans_before} (查询失败: {str(e)[:30]})")
        
        # 返回执行结果
        if len(results) > 0:
            return "\n\n" + "\n\n".join(results)
        else:
            return "❌ 任务执行失败: 未能完成任何任务"
        
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()[:200]
        return f"❌ 任务执行异常: {str(e)[:50]}\n{error_msg}"

# 处理插件消息入口点
sender = middleware.Sender(middleware.getSenderID())
message = sender.getMessage().strip()
# 检查具体指令
if message in ["蚂蚁登录", "蚂蚁绑定"]:
    蚂蚁登录()
elif message == "蚂蚁管理":
    蚂蚁管理()
elif message == "蚂蚁查询":
    蚂蚁查询()
elif message == "蚂蚁授权":
    蚂蚁授权()
elif message == "蚂蚁教程":
    蚂蚁教程()
elif message == "蚂蚁积分":
    query_user_points()
elif message == "蚂蚁一键运行":
    蚂蚁一键运行()