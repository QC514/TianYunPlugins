#[title: 【自用】-爱路桥]
#[language: python]
#[class: 工具类]
#[service: 1603960061] 售后联系方式
#[author: huawei] 作者
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^(爱路桥|alq)(登录|登陆)$|^登(录|陆)(爱路桥|alq)$|^(爱路桥|alq)(查询|管理)$|^(查询|管理)(爱路桥|alq)$|^清理爱路桥$|^爱路桥授权$|^爱路桥教程$]
#[cron: 18 8,12,16 * * *] cron定时，支持5位域和6位域
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: https://img-cf.885666.xyz/65f0d781788eb95ae389d77969b248da.png]图标链接地址，请使用48像素的正方形图标，支持http和https
#[version: 1.0.4]版本号
#[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
#[price: 6.66] 上架价格
# [description: ]

import os
import json
import time
import random
import string
import requests
from datetime import datetime, timedelta
import middleware
import hashlib  # 添加hashlib模块导入

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_alq_user', key=userid)

# [param: {"required":true,"key":"s_alq_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"s_alq_config.alq_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割"}]
# [param: {"required":true,"key":"s_alq_config.alq_osname","bool":false,"placeholder":"必填项,例:S_ALQ","name":"提交到青龙的变量名","desc":"青龙容器内爱路桥的变量名"}]
# [param: {"required":true,"key":"s_alq_config.alqVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"s_alq_config.alqcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]


# 接口地址
base_url = 'https://www.ailuqiao.cn/mobile'

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 's_alq_config',
    'coin_key': 'dd_sign_points',
    'name': '爱路桥'
}

# 支付配置
PAYMENT_CONFIG = {
    'zsm': middleware.bucketGet('s_alq_config', 'zsm') or '',  # 赞赏码链接
    'ma_pay_switch': middleware.bucketGet('s_alq_config', 'ma_pay_switch') or 'false',  # 码支付开关
    'ma_pay_gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',  # 从卡密系统获取支付网关
    'ma_pay_pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',  # 从卡密系统获取商户ID
    'ma_pay_key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',  # 从卡密系统获取商户密钥
    'ma_pay_type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay',  # 从卡密系统获取支付方式
    'ma_pay_notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or 'http://localhost/notify',  # 从卡密系统获取异步通知地址
    'ma_pay_return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or 'http://localhost/return',  # 从卡密系统获取跳转通知地址
    'pid': '',  # 将在后面初始化
    'key': '',  # 将在后面初始化
    'gateway': '',  # 将在后面初始化
    'notify_url': '',  # 将在后面初始化
    'return_url': ''  # 将在后面初始化
}

# 同步配置到标准字段
PAYMENT_CONFIG['pid'] = PAYMENT_CONFIG['ma_pay_pid']
PAYMENT_CONFIG['key'] = PAYMENT_CONFIG['ma_pay_key']
PAYMENT_CONFIG['gateway'] = PAYMENT_CONFIG['ma_pay_gateway']
PAYMENT_CONFIG['notify_url'] = PAYMENT_CONFIG['ma_pay_notify_url'] 
PAYMENT_CONFIG['return_url'] = PAYMENT_CONFIG['ma_pay_return_url']

# 支付方式中文名称映射
PAY_TYPE_NAMES = {
    'alipay': '支付宝',
    'wxpay': '微信支付',
    'qqpay': 'QQ钱包',
}

def get_user_content():
    """获取用户配置内容"""
    alq_osname = middleware.bucketGet('s_alq_config', 'alq_osname') or 'S_ALQ'
    alq_qlname = middleware.bucketGet('s_alq_config', 'alq_qlname') or ''
    alq_managecommand = middleware.bucketGet('s_alq_config', 'alq_managecommand') or '爱路桥管理'
    alq_querycommand = middleware.bucketGet('s_alq_config', 'alq_querycommand') or '爱路桥查询'
    alq_signcommand = middleware.bucketGet('s_alq_config', 'alq_signcommand') or '爱路桥登录'
    
    randommanagecommand = alq_managecommand
    randomquerycommand = alq_querycommand
    randomsigncommand = alq_signcommand
    
    alqVipmoney = float(middleware.bucketGet('s_alq_config', 'alqVipmoney') or '1')
    
    # 优先从卡密系统获取积分配置
    alqcoin = middleware.bucketGet(PLUGIN_CONFIG['bucket'], PLUGIN_CONFIG['coin_key'])
    if not alqcoin:
        # 如果卡密系统未配置，则使用插件配置
        alqcoin = middleware.bucketGet('s_alq_config', 'alqcoin') or '0'
    alqcoin = int(alqcoin)
    
    return (alq_osname, alq_qlname, randommanagecommand, 
            randomquerycommand, randomsigncommand, alqVipmoney, alqcoin)

def mask_phone(phone):
    """手机号脱敏处理"""
    if not phone or len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[7:]}"

def get_random_user_agent():
    """获取随机UA"""
    backup_ua_list = [
        'Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.37 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 14; Pixel 6 Build/UQ1A.240605.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/133.0.6638.41 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(backup_ua_list)

def generate_random_id():
    """生成随机设备ID"""
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

def get_lottery_headers(uid, cookie):
    """获取抽奖相关请求头"""
    return {
        "User-Agent": get_random_user_agent(),
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Cookie": cookie
    }

def get_user_info(uid, cookie):
    """获取用户信息"""
    try:
        url = f"{base_url}/myinfo?uid={uid}"
        headers = get_lottery_headers(uid, cookie)
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get("data"):
            user_data = result["data"]
            return {
                "success": True,
                "nickname": user_data.get("nickname", ""),
                "integral": user_data.get("integral", "0")
            }
        return {"success": False, "message": "获取用户信息失败"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_luck_records(uid, cookie):
    """获取红包记录"""
    try:
        url = f"{base_url}/my_luck?uid={uid}&cid=1028"
        headers = get_lottery_headers(uid, cookie)
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get("data"):
            records = result["data"][:5]  # 只取前5条记录
            return {
                "success": True,
                "records": [{
                    "prize": record.get("draw", ""),
                    "time": record.get("create_time", "")
                } for record in records]
            }
        return {"success": False, "message": "获取红包记录失败"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def login_with_sms():
    """使用短信验证码登录爱路桥"""
    phone_guide_lines = [
        "请输入手机号码",
        "------------------",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("短信登录", phone_guide_lines))
    
    phone = sender.input(120000, 1, False)
    if not phone or phone.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return None
        
    # 验证手机号格式
    if not phone.isdigit() or len(phone) != 11:
        sender.reply("❌ 手机号格式错误，请输入11位数字")
        return None
    
    # 生成会话ID
    session_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
    cookie = f"beegosessionID={session_id}"
    
    # 发送短信验证码
    try:
        url = f"{base_url}/service_send"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie
        }
        data = f"mobile={phone}"
        
        response = requests.post(url, headers=headers, data=data)
        result = response.json()
        
        if result.get("status") != 1:
            sender.reply(f"❌ 发送验证码失败: {result.get('message', '未知错误')}")
            return None
            
        code_sent_lines = [
            f"📱 手机号: {mask_phone(phone)}",
            "✅ 发送成功",
            "------------------",
            "请输入接收到的验证码:"
        ]
        sender.reply(format_message("验证码已发送", code_sent_lines))
        
        # 获取用户输入的验证码
        code = sender.input(300000, 1, False)  # 5分钟超时
        if not code:
            sender.reply("⏰ 验证码输入超时，已取消登录")
            return None
            
        # 验证码登录
        url = f"{base_url}/service_yz"
        data = f"mobile={phone}&code={code}"
        
        response = requests.post(url, headers=headers, data=data)
        result = response.json()
        
        if result.get("status") != 1:
            sender.reply(f"❌ 登录失败: {result.get('message', '验证码错误或已过期')}")
            return None
            
        uid = result.get("uid", "")
        if not uid:
            sender.reply("❌ 登录失败: 未获取到用户ID")
            return None
            
        # 获取用户信息
        user_info = get_user_info(uid, cookie)
        if not user_info.get("success"):
            sender.reply(f"❌ 获取用户信息失败: {user_info.get('message', '未知错误')}")
            return None
            
        # 返回账号信息字典
        return {
            "uid": uid,
            "cookie": cookie,
            "phone": phone,  # 添加手机号
            "nickname": user_info.get("nickname", phone)
        }
        
    except Exception as e:
        sender.reply(f"❌ 登录异常: {str(e)}")
        return None

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply(format_message("未绑定账号", [
            "❌ 未找到任何账号信息",
            f"💡 发送 {randomsigncommand} 绑定"
        ]))
        return
        
    accounts = eval(uservalue)
    account_list_lines = ["[0] 全部账号"]
    
    for i, account in enumerate(accounts, 1):
        account_info_str = middleware.bucketGet('s_alq_token', account)
        if not account_info_str:
            continue
            
        account_info = json.loads(account_info_str)
        remark = account_info.get('nickname', account)
        auth_time = middleware.bucketGet('s_alq_auth', account)
        
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'{auth_time}'
            
        account_list_lines.append(f"[{i}]{mask_phone(account)}({auth_status})")
    
    account_list_lines.append("=====================")
    account_list_lines.append("支持多选，用英文逗号分隔")
    account_list_lines.append("例如: 1,2,3")
    account_list_lines.append("回复\"q\"退出操作")
    account_list_lines.append("=====================")
    
    sender.reply(format_message("选择账号", account_list_lines))
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出查询")
        return
        
    try:
        # 处理账号选择
        selected_accounts = []
        
        if choice == '0':
            # 选择全部账号
            selected_accounts = accounts.copy()
        else:
            # 处理多选
            indices = choice.split(',')
            for idx in indices:
                idx = idx.strip()
                if not idx.isdigit():
                    continue
                    
                index = int(idx) - 1
                if 0 <= index < len(accounts):
                    selected_accounts.append(accounts[index])
        
        if not selected_accounts:
            sender.reply("❌ 未选择有效账号")
            return
            
        # 显示选择的账号数量
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号，正在查询...")
        
        # 查询每个账号的信息
        query_count = 0
        for account in selected_accounts:
            try:
                account_info_str = middleware.bucketGet('s_alq_token', account)
                if not account_info_str:
                    sender.reply(show_error("账号不存在", "未找到账号信息", f"📱 账号: {account}"))
                    continue
                    
                account_info = json.loads(account_info_str)
                uid = account_info.get('uid', '')
                cookie = account_info.get('cookie', '')
                
                if not uid or not cookie:
                    sender.reply(show_error("账号信息不完整", "缺少必要信息", f"📱 账号: {account}"))
                    continue
                    
                # 获取用户信息
                user_info = get_user_info(uid, cookie)
                if not user_info.get("success"):
                    sender.reply(show_error("获取信息失败", user_info.get("message", "未知错误"), f"📱 账号: {account}"))
                    continue
                    
                # 获取红包记录
                luck_records = get_luck_records(uid, cookie)
                
                # 获取授权状态
                auth_time = middleware.bucketGet('s_alq_auth', account)
                if not auth_time:
                    auth_status = '到期: 未授权'
                elif auth_time < str(datetime.now().date()):
                    auth_status = '到期: 已过期'
                else:
                    auth_status = f'到期: {auth_time}'
                
                # 构建账号信息
                info_lines = [
                    f"📱 账号: {mask_phone(account)}",
                    f"👤 昵称: {user_info.get('nickname', '未设置')}",
                    f"💰 积分: {user_info.get('integral', '0')}",
                    f"📅 {auth_status}"
                ]
                
                # 添加红包记录信息
                if luck_records.get("success") and luck_records.get("records"):
                    records = luck_records.get("records")
                    info_lines.append("---------------------------")
                    info_lines.append("🎁 最近红包记录:")
                    
                    for record in records:
                        prize = record.get("prize", "")
                        time_str = record.get("time", "")
                        info_lines.append(f"💰 {prize} ({time_str})")
                
                sender.reply(format_message(f"账号信息[{query_count+1}/{len(selected_accounts)}]", info_lines))
                query_count += 1
                
                # 如果查询的账号过多，中间加一点延迟
                if query_count < len(selected_accounts) and len(selected_accounts) > 3:
                    time.sleep(0.5)
                    
            except Exception as e:
                sender.reply(show_error(f"查询异常[{query_count+1}/{len(selected_accounts)}]", str(e), f"📱 账号: {account}"))
                query_count += 1
            
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")

def manage_account():
    """账号管理功能"""
    if not uservalue:
        sender.reply(format_message("未绑定账号", [
            "❌ 未找到任何账号信息",
            f"💡 发送 {randomsigncommand} 绑定"
        ]))
        return
        
    accounts = eval(uservalue)
    
    # 先显示管理功能菜单
    menu_lines = [
        "[1] 授权账号",
        "[2] 删除账号",
        "[3] 提交青龙",
        "------------------",
        "回复数字选择功能",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("账号管理", menu_lines))
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    
    # 然后显示账号列表供选择
    account_list_lines = ["[0] 全部账号"]
    
    for i, account in enumerate(accounts, 1):
        account_info_str = middleware.bucketGet('s_alq_token', account)
        if not account_info_str:
            continue
            
        account_info = json.loads(account_info_str)
        remark = account_info.get('nickname', account)
        auth_time = middleware.bucketGet('s_alq_auth', account)
        
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'{auth_time}'
            
        account_list_lines.append(f"[{i}]{mask_phone(account)}({auth_status})")
    
    account_list_lines.extend([
        "=====================",
        "支持多选，用英文逗号分隔",
        "例如: 1,2,3",
        "回复\"q\"退出操作"
    ])
        
    sender.reply(format_message("选择账号", account_list_lines))
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
        
    try:
        # 处理账号选择
        selected_accounts = []
        
        if account_choice == '0':
            # 选择全部账号
            selected_accounts = accounts.copy()
        else:
            # 处理多选
            indices = account_choice.split(',')
            for idx in indices:
                idx = idx.strip()
                if not idx.isdigit():
                    continue
                    
                index = int(idx) - 1
                if 0 <= index < len(accounts):
                    selected_accounts.append(accounts[index])
        
        if not selected_accounts:
            sender.reply("❌ 未选择有效账号")
            return
            
        # 显示选择的账号数量
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号")
            
        # 根据之前的功能选择执行对应操作
        if choice == '1':
            # 授权选中的账号
            authorize_multiple_accounts(selected_accounts)
            
        elif choice == '2':
            # 删除选中的账号
            confirm_lines = [
                "⚠️ 此操作不可恢复",
                "------------------",
                "回复 y 确认删除",
                "回复 n 取消操作"
            ]
            sender.reply(format_message("确认删除", confirm_lines))
            
            confirm = sender.input(120000, 1, False)
            if confirm.lower() == 'y':
                success_count = 0
                for account in selected_accounts:
                    try:
                        # 从账号列表中移除
                        if account in accounts:
                            accounts.remove(account)
                            
                        # 删除相关信息
                        middleware.bucketDel('s_alq_token', account)
                        middleware.bucketDel('s_alq_auth', account)
                            
                        # 删除青龙变量
                        delete_ql_env(account)
                        success_count += 1
                    except Exception as e:
                        print(f"删除账号失败: {account}, 错误: {str(e)}")
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet('s_alq_user', userid, str(accounts))
                else:
                    middleware.bucketDel('s_alq_user', userid)
                    
                sender.reply(f"✅ 已成功删除 {success_count}/{len(selected_accounts)} 个账号")
            else:
                sender.reply("✅ 已取消删除")
                
        elif choice == '3':
            # 提交选中账号到青龙
            success_count = 0
            for account in selected_accounts:
                try:
                    account_info_str = middleware.bucketGet('s_alq_token', account)
                    if not account_info_str:
                        continue
                        
                    account_info = json.loads(account_info_str)
                    
                    # 如果已授权则更新青龙变量
                    auth_time = middleware.bucketGet('s_alq_auth', account)
                    if auth_time and auth_time >= str(datetime.now().date()):
                        if update_ql_env(account, account_info):
                            success_count += 1
                    else:
                        print(f"账号未授权或已过期: {account}")
                except Exception as e:
                    print(f"提交青龙失败: {account}, 错误: {str(e)}")
            
            result_lines = [
                f"📊 选择账号: {len(selected_accounts)}个",
                f"✅ 提交成功: {success_count}个",
                f"❌ 提交失败: {len(selected_accounts) - success_count}个",
                "------------------",
                "💡 提示: 未授权账号无法提交"
            ]
            sender.reply(format_message("提交结果", result_lines))
        else:
            sender.reply("❌ 无效的选择")
            
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")

def show_tutorial():
    """显示爱路桥教程"""
    tutorial_url = middleware.bucketGet('s_alq_config', 'tutorial_url') or 'https://example.com/tutorial'
    
    tutorial = f"""
=====爱路桥使用教程=====
🔍 基础功能:
1. 爱路桥登录 - 绑定账号
2. 爱路桥查询 - 查看账号信息
3. 爱路桥管理 - 管理绑定账号
==================
⚠️ 注意事项:
• 账号失效请及时更新
• 请勿泄露账号信息
==================
💡 登录方式:
• 短信登录 - 通过短信验证码登录
==================
❓ 遇到问题请联系管理员
=================="""
    sender.reply(tutorial)

def get_ql_config():
    """获取青龙配置信息"""
    try:
        qlconfig = middleware.bucketGet('s_alq_config', 'alq_qlname')
        if not qlconfig:
            return {"code": 400, "msg": "未配置青龙信息", "data": None}
            
        # 将英文的"|"替换为中文的"丨"
        qlconfig = qlconfig.replace('|', '丨')
        configs = qlconfig.split('丨')
        if len(configs) < 3:
            return {"code": 400, "msg": "青龙配置格式错误", "data": None}
            
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "url": configs[0].strip(),
                "client_id": configs[1].strip(),
                "client_secret": configs[2].strip()
            }
        }
    except Exception as e:
        return {"code": 500, "msg": f"获取青龙配置发生异常: {str(e)}", "data": None}

def get_ql_token(host, client_id, client_secret):
    """获取青龙 token"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        response = requests.get(url, timeout=10)
        data = response.json()
        if data.get('code') == 200 and data.get('data') and data['data'].get('token'):
            return data['data']['token']
        else:
            print(f"获取青龙token失败: {data.get('message', '未知错误')}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求青龙token异常: {str(e)}")
        return None
    except Exception as e:
        print(f"获取青龙token异常: {str(e)}")
        return None

def update_ql_env(phone, account_info):
    """更新青龙环境变量"""
    try:
        # 从配置中获取青龙信息
        ql_config = get_ql_config()
        if ql_config['code'] != 200:
            print(ql_config['msg'])
            return False
            
        host = ql_config['data'].get('url', '')
        client_id = ql_config['data'].get('client_id', '')
        client_secret = ql_config['data'].get('client_secret', '')
        
        if not host or not client_id or not client_secret:
            print("青龙配置信息不完整")
            return False
            
        # 获取token
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            print("获取青龙token失败")
            return False
            
        # 获取配置的变量名
        env_name = middleware.bucketGet('s_alq_config', 'alq_osname') or 'S_ALQ'
        
        # 构建变量值 - 使用uid#cookie格式
        uid = account_info.get('uid', '')
        cookie = account_info.get('cookie', '')
        
        if not uid or not cookie:
            print(f"账号信息不完整: {phone}")
            return False
            
        value = f"{uid}#{cookie}"
        
        # 构建变量备注
        auth_time = middleware.bucketGet('s_alq_auth', phone) or '未授权'
        remark = f"爱路桥:{phone}丨用户:{uid}丨到期:{auth_time}"
        
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # 获取所有环境变量
            response = requests.get(f'{host}/open/envs', headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"获取环境变量失败: {response.text}")
                return False
                
            envs = response.json().get('data', [])
            env_id = None
            
            # 查找是否已存在该变量
            for env in envs:
                env_remarks = env.get('remarks', '')
                if env['name'] == env_name and f"爱路桥:{phone}" in env_remarks:
                    env_id = env.get('_id') or env.get('id')
                    break
            
            # 构建变量数据
            env_data = {
                "name": env_name,
                "value": value,
                "remarks": remark
            }
            
            if env_id:
                # 更新已存在的变量
                env_data["id"] = env_id
                response = requests.put(f'{host}/open/envs', headers=headers, json=env_data, timeout=10)
                if response.status_code != 200:
                    print(f"更新环境变量失败: {response.text}")
                    return False
                    
                # 启用变量
                try:
                    requests.put(f'{host}/open/envs/enable', headers=headers, json=[env_id], timeout=10)
                except Exception as e:
                    print(f"启用变量异常: {str(e)}")
            else:
                # 添加新变量
                response = requests.post(f'{host}/open/envs', headers=headers, json=[env_data], timeout=10)
                if response.status_code != 200:
                    print(f"添加环境变量失败: {response.text}")
                    return False
                    
                # 获取新添加变量的ID并启用
                result = response.json()
                if result.get('code') == 200:
                    new_id = None
                    if result.get('data') and len(result['data']) > 0:
                        new_id = result['data'][0].get('_id') or result['data'][0].get('id')
                    if new_id:
                        try:
                            requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id], timeout=10)
                        except Exception as e:
                            print(f"启用变量异常: {str(e)}")
            
            print(f"青龙变量更新成功: {phone}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"请求青龙API异常: {str(e)}")
            return False
    except Exception as e:
        print(f"更新青龙变量异常: {str(e)}")
        return False

def delete_ql_env(phone):
    """删除青龙环境变量"""
    try:
        # 获取变量名
        env_name = middleware.bucketGet('s_alq_config', 'alq_osname') or 'S_ALQ'
        
        # 从配置中获取青龙信息
        ql_config = get_ql_config()
        if ql_config['code'] != 200:
            print(ql_config['msg'])
            return False
            
        host = ql_config['data'].get('url', '')
        client_id = ql_config['data'].get('client_id', '')
        client_secret = ql_config['data'].get('client_secret', '')
        
        if not host or not client_id or not client_secret:
            print("青龙配置信息不完整")
            return False
        
        # 获取token
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            print("获取青龙token失败")
            return False
            
        # 查找要删除的变量
        headers = {'Authorization': f'Bearer {token}'}
        try:
            response = requests.get(f'{host}/open/envs', headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"获取环境变量失败: {response.text}")
                return False
                
            envs = response.json().get('data', [])
            
            deleted = False
            for env in envs:
                # 精确匹配：变量名必须一致，并且备注中必须包含该手机号
                if env['name'] == env_name and f"爱路桥:{phone}" in env.get('remarks', ''):
                    # 删除变量
                    env_id = env.get('_id') or env.get('id')
                    if not env_id:
                        continue
                        
                    try:
                        response = requests.delete(
                            f'{host}/open/envs',
                            headers=headers,
                            json=[env_id],
                            timeout=10
                        )
                        if response.status_code == 200:
                            deleted = True
                            print(f"删除青龙变量成功: {env_id}")
                        else:
                            print(f"删除青龙变量失败: {response.text}")
                    except Exception as e:
                        print(f"删除变量请求异常: {str(e)}")
                    
            return deleted
        except requests.exceptions.RequestException as e:
            print(f"请求青龙API异常: {str(e)}")
            return False
    except Exception as e:
        print(f"删除青龙变量异常: {str(e)}")
        return False

def bind_account():
    """绑定爱路桥账号"""
    # 直接进行短信登录
    account_info = login_with_sms()
    if not account_info:
        return
        
    # 保存账号信息
    uid = account_info.get('uid')
    phone = account_info.get('phone')  # 从登录信息中获取手机号
    
    if not phone or not uid:
        sender.reply("❌ 获取账号信息失败")
        return
        
    # 更新用户账号列表 - 使用手机号作为标识
    if not uservalue:
        middleware.bucketSet('s_alq_user', userid, str([phone]))
    else:
        accounts = eval(uservalue)
        if phone not in accounts:
            accounts.append(phone)
            middleware.bucketSet('s_alq_user', userid, str(accounts))
            
    # 保存账号详细信息 - 使用手机号作为key
    middleware.bucketSet('s_alq_token', phone, json.dumps(account_info))
    
    success_lines = [
        f"👤 昵称: {account_info.get('nickname')}",
        f"📱 手机号: {mask_phone(phone)}",
        f"🆔 用户ID: {uid}"
    ]
    sender.reply(format_message("绑定成功", success_lines))
    
    # 检查账号是否已授权，如果已授权且未过期则直接更新青龙变量
    dqsj = datetime.now().strftime("%Y-%m-%d")
    accountVip = middleware.bucketGet('s_alq_auth', phone)  # 使用手机号作为key
    
    if accountVip and accountVip > dqsj:
        # 账号已授权且未过期，直接更新青龙变量
        ql_result = update_ql_env(phone, account_info)
        auth_result = f"""
=====账号已授权=====
📱 手机号: {mask_phone(phone)}
👤 昵称: {account_info.get('nickname', '未设置')}
📅 到期时间: {accountVip}
------------------
🔄 青龙更新: {'成功' if ql_result else '失败'}
=================="""
        sender.reply(auth_result)
    else:
        # 账号未授权或已过期，询问是否进入授权流程
        auth_guide = """
=====授权提示=====
❓ 是否需要立即授权账号？
------------------
[1] 立即授权
[2] 暂不授权
------------------
回复数字选择
=================="""
        sender.reply(auth_guide)
        
        choice = sender.input(120000, 1, False)
        if choice == '1':
            # 进入授权流程
            authorize_account(phone, account_info)
        else:
            sender.reply("""
=====提示=====
✅ 账号已绑定成功
❗ 您可以稍后使用"爱路桥管理"命令进行授权
==================""")
            
    # 获取用户信息
    try:
        user_info = get_user_info(uid, account_info.get('cookie', ''))
        if user_info.get("success"):
            info_lines = [
                f"📱 账号: {mask_phone(phone)}",
                f"👤 昵称: {user_info.get('nickname', '未设置')}",
                f"💰 积分: {user_info.get('integral', '0')}"
            ]
            sender.reply(format_message("账号信息", info_lines))
    except:
        pass

def authorize_multiple_accounts(accounts):
    """批量授权账号"""
    # 获取配置信息
    (_, _, _, _, _, alqVipmoney, alqcoin) = get_user_content()
    
    account_infos = []
    # 获取账号信息
    for phone in accounts:
        try:
            account_info_str = middleware.bucketGet('s_alq_token', phone)
            if not account_info_str:
                continue
                
            account_info = json.loads(account_info_str)
            # 直接添加账号，不验证有效性
            account_infos.append({
                'phone': phone,
                'info': account_info
            })
        except Exception as e:
            sender.reply(f"""
⚠️ 账号处理异常:
📱 手机号: {mask_phone(phone)}
❌ 原因: {str(e)}""")
            
    if not account_infos:
        sender.reply("❌ 没有有效的账号可授权")
        return
        
    # 显示选择了多少个有效账号
    #sender.reply(f"✅ 共有 {len(account_infos)} 个有效账号可授权")
    
    # 先询问授权月数
    auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
--------------------------
回复数字设置月数
回复"q"退出操作
=================="""
    sender.reply(auth_guide)
    
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
        
    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
            
        # 计算总价格 = 账号数 * 月数 * 单价
        total_money = len(account_infos) * months * alqVipmoney
    
        # 构建可用的支付方式列表
        available_payments = []
        
        # 检查是否启用码支付
        ma_pay_switch = middleware.bucketGet('s_alq_config', 'ma_pay_switch') or 'false'
        
        # 如果码支付开启，添加码支付方式
        if ma_pay_switch.lower() == 'true':
            # 从卡密系统获取支付配置
            ma_pay_type = middleware.bucketGet('dd_sign_config', 'ma_pay_type') or ''
            ma_pay_pid = middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or ''
            ma_pay_key = middleware.bucketGet('dd_sign_config', 'ma_pay_key') or ''
            ma_pay_gateway = middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or ''
            
            if ma_pay_gateway and ma_pay_pid and ma_pay_key:
                # 获取支付方式列表
                pay_types_str = ma_pay_type.strip()
                if not pay_types_str:
                    pay_types_str = "alipay,wxpay"  # 默认支付方式
                    
                pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
                # 添加每种码支付方式
                for pay_type in pay_types:
                    name = PAY_TYPE_NAMES.get(pay_type, pay_type)
                    available_payments.append((name, f"mapay_{pay_type}"))
        else:
            # 微信支付（检查是否配置了收款码）
            zsm = middleware.bucketGet('s_alq_config', 'zsm')
            if zsm:
                available_payments.append(("微信支付", "wxpay"))
        
        # 积分兑换（检查是否开启了积分功能）
        if alqcoin and int(alqcoin) > 0:
            available_payments.append(("积分兑换", "coin"))
        
        if not available_payments:
            sender.reply("""
=====授权失败=====
❌ 未配置任何支付方式
------------------
请联系管理员配置支付方式
==================""")
            return
        
        # 如果只有一种支付方式，直接使用
        if len(available_payments) == 1:
            payment_name, payment_type = available_payments[0]
        else:
            # 显示支付方式选择菜单
            auth_menu = f"""
=====选择支付方式=====
📊 账号数量: {len(account_infos)}个
⏰ 授权时长: {months}个月
💰 总金额: {total_money}元
------------------------"""
            
            for i, (name, _) in enumerate(available_payments, 1):
                auth_menu += f"""
[{i}] {name}"""
                
            auth_menu += """
------------------------
回复数字选择方式
回复"q"退出操作
=================="""
            
            sender.reply(auth_menu)
            
            pay_choice = sender.input(120000, 1, False)
            if not pay_choice or pay_choice.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
            
            try:
                choice_index = int(pay_choice) - 1
                if not (0 <= choice_index < len(available_payments)):
                    sender.reply("❌ 无效的选择")
                    return
                    
                payment_name, payment_type = available_payments[choice_index]
            except ValueError:
                sender.reply("❌ 请输入有效的数字")
                return
                
        if payment_type == "wxpay":
            # 微信支付
            # 处理支付
            if pay_order(project=f'爱路桥授权(共{len(account_infos)}个账号)', months=months, money=total_money):
                # 处理每个账号的授权
                success_count = 0
                for account in account_infos:
                    try:
                        phone = account['phone']
                        account_info = account['info']
                        
                        # 处理授权
                        if process_authorization(phone, account_info, months):
                            success_count += 1
                    except Exception as e:
                        print(f"授权账号异常: {phone}, 错误: {str(e)}")
                
                # 显示授权结果
                success_msg = f"""
=====授权结果=====
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
-----------------------
⏰ 授权: {months}个月
-----------------------
💰 总金额: {total_money}元
=================="""
                sender.reply(success_msg)
                
        elif payment_type.startswith("mapay_"):
            # 码支付处理
            # 提取实际支付方式（去掉"mapay_"前缀）
            actual_pay_type = payment_type[6:]
            
            # 处理支付
            result = handle_mapay_order(
                project=f'爱路桥授权(共{len(account_infos)}个账号)', 
                months=months, 
                money=total_money,
                pay_type=actual_pay_type
            )
            
            if result:
                # 处理每个账号的授权
                success_count = 0
                for account in account_infos:
                    try:
                        phone = account['phone']
                        account_info = account['info']
                        
                        # 处理授权
                        if process_authorization(phone, account_info, months):
                            success_count += 1
                    except Exception as e:
                        print(f"授权账号异常: {phone}, 错误: {str(e)}")
                
                # 显示授权结果
                success_msg = f"""
=====授权结果=====
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
-----------------------
⏰ 授权: {months}个月
-----------------------
💰 总金额: {total_money}元
=================="""
                sender.reply(success_msg)
                
        elif payment_type == "coin":
            # 积分兑换处理
            if not alqcoin or int(alqcoin) <= 0:
                sender.reply("""
=====兑换失败=====
❌ 未配置积分价格
------------------
请联系管理员配置积分兑换功能
==================""")
                return
                
            # 计算需要的积分总数
            total_coins = int(alqcoin) * months * len(account_infos)
            
            # 获取用户当前积分
            user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            
            if user_coins < total_coins:
                sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 当前积分: {user_coins}
🔢 需要积分: {total_coins}
🔍 差额: {total_coins - user_coins}
==================""")
                return
            
            # 扣除积分
            new_coins = user_coins - total_coins
            middleware.bucketSet('dd_sign_points', userid, str(new_coins))
            
            # 处理每个账号的授权
            success_count = 0
            for account in account_infos:
                try:
                    phone = account['phone']
                    account_info = account['info']
                    
                    # 处理授权
                    if process_authorization(phone, account_info, months):
                        success_count += 1
                except Exception as e:
                    print(f"授权账号异常: {phone}, 错误: {str(e)}")
            
            if success_count > 0:
                # 积分兑换成功通知
                sender.reply(f"""
=====积分兑换成功=====
✅ 已扣除积分: {total_coins}
💰 剩余积分: {new_coins}
------------------
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
            else:
                # 积分兑换失败，退还积分
                middleware.bucketSet('dd_sign_points', userid, str(user_coins))
                sender.reply(f"""
=====积分退还=====
⚠️ 授权处理失败，已退还积分
------------------
💰 当前积分: {user_coins}
==================""")
                
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
        return

def authorize_account(phone, account_info):
    """单个账号授权"""
    # 获取配置信息
    (_, _, _, _, _, alqVipmoney, alqcoin) = get_user_content()
    
    # 先询问授权月数
    auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
--------------------------
回复数字设置月数
回复"q"退出操作
=================="""
    sender.reply(auth_guide)
    
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
        
    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
            
        # 计算价格
        money = months * alqVipmoney
        
        # 构建可用的支付方式列表
        available_payments = []
        
        # 检查是否启用码支付
        ma_pay_switch = middleware.bucketGet('s_alq_config', 'ma_pay_switch') or 'false'
        
        # 如果码支付开启，添加码支付方式
        if ma_pay_switch.lower() == 'true':
            # 从卡密系统获取支付配置
            ma_pay_type = middleware.bucketGet('dd_sign_config', 'ma_pay_type') or ''
            ma_pay_pid = middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or ''
            ma_pay_key = middleware.bucketGet('dd_sign_config', 'ma_pay_key') or ''
            ma_pay_gateway = middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or ''
            
            if ma_pay_gateway and ma_pay_pid and ma_pay_key:
                # 获取支付方式列表
                pay_types_str = ma_pay_type.strip()
                if not pay_types_str:
                    pay_types_str = "alipay,wxpay"  # 默认支付方式
                    
                pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
                # 添加每种码支付方式
                for pay_type in pay_types:
                    name = PAY_TYPE_NAMES.get(pay_type, pay_type)
                    available_payments.append((name, f"mapay_{pay_type}"))
        else:
            # 微信支付（检查是否配置了收款码）
            zsm = middleware.bucketGet('s_alq_config', 'zsm')
            if zsm:
                available_payments.append(("微信支付", "wxpay"))
        
        # 积分兑换（检查是否开启了积分功能）
        if alqcoin and int(alqcoin) > 0:
            available_payments.append(("积分兑换", "coin"))
            
        if not available_payments:
            sender.reply("""
=====授权失败=====
❌ 未配置任何支付方式
------------------
请联系管理员配置支付方式
==================""")
            return
            
        # 如果只有一种支付方式，直接使用
        if len(available_payments) == 1:
            payment_name, payment_type = available_payments[0]
        else:
            # 显示支付方式选择菜单
            auth_menu = f"""
=====选择支付方式=====
⏰ 授权时长: {months}个月
💰 金额: {money}元
------------------"""
            
            for i, (name, _) in enumerate(available_payments, 1):
                auth_menu += f"""
[{i}] {name}"""
                
            auth_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""
            
            sender.reply(auth_menu)
            
            pay_choice = sender.input(120000, 1, False)
            if not pay_choice or pay_choice.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
                
            try:
                choice_index = int(pay_choice) - 1
                if not (0 <= choice_index < len(available_payments)):
                    sender.reply("❌ 无效的选择")
                    return
                    
                payment_name, payment_type = available_payments[choice_index]
            except ValueError:
                sender.reply("❌ 请输入有效的数字")
                return
        
        # 根据支付类型处理不同的支付方式
        if payment_type == "wxpay":
            # 微信支付处理
            if pay_order(project='爱路桥授权', months=months, money=money):
                process_authorization(phone, account_info, months)
        
        elif payment_type.startswith("mapay_"):
            # 码支付处理
            # 提取实际支付方式（去掉"mapay_"前缀）
            actual_pay_type = payment_type[6:]
            
            # 处理支付
            result = handle_mapay_order(project='爱路桥授权', months=months, money=money, pay_type=actual_pay_type)
            
            # 处理授权
            if result:
                process_authorization(phone, account_info, months)
                
        elif payment_type == "coin":
            # 积分兑换处理
            process_coin_exchange(phone, account_info, months, alqcoin)
            
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
        return

def process_authorization(phone, account_info, months):
    """处理账号授权"""
    try:
        # 获取当前授权状态
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_alq_auth', phone)
        
        # 计算新的到期时间
        if accountVip and accountVip > dqsj:
            # 如果当前已有有效授权，从授权到期时间开始计算
            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
        else:
            # 如果没有有效授权，从当前时间开始计算
            start_date = datetime.now()
            
        # 计算新的到期时间(按月计算，每月30天)
        new_expire = start_date + timedelta(days=30*months)
        new_expire_str = new_expire.strftime("%Y-%m-%d")
        
        # 更新授权时间
        middleware.bucketSet('s_alq_auth', phone, new_expire_str)
        
        # 更新青龙变量
        ql_result = update_ql_env(phone, account_info)
        
        # 显示授权结果
        auth_result = f"""
=====授权成功=====
📱 手机号: {mask_phone(phone)}
👤 昵称: {account_info.get('nickname', '未设置')}
⏰ 授权时长: {months}个月
📅 到期时间: {new_expire_str}
------------------
🔄 青龙更新: {'成功' if ql_result else '失败'}
=================="""
        sender.reply(auth_result)
        return True
    except Exception as e:
        error_msg = f"""
=====授权失败=====
📱 手机号: {mask_phone(phone)}
❌ 错误: {str(e)}
=================="""
        print(f"授权处理异常: {phone}, 错误: {str(e)}")
        sender.reply(error_msg)
        return False

def process_coin_exchange(phone, account_info, months, alqcoin):
    """处理积分兑换"""
    try:
        # 验证积分兑换配置
        if not alqcoin or int(alqcoin) <= 0:
            sender.reply(f"""
=====兑换失败=====
❌ 未配置积分价格
------------------
请联系管理员配置积分兑换功能
==================""")
            return False
            
        # 计算所需积分
        required_coins = months * int(alqcoin)
        
        # 获取用户积分
        user_coins = middleware.bucketGet('dd_sign_points', userid) or '0'
        user_coins = int(user_coins)
        
        if user_coins < required_coins:
            sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 当前积分: {user_coins}
🔢 需要积分: {required_coins}
🔍 差额: {required_coins - user_coins}
==================""")
            return False
            
        # 扣除积分
        new_coins = user_coins - required_coins
        middleware.bucketSet('dd_sign_points', userid, str(new_coins))
        
        # 处理授权
        success = process_authorization(phone, account_info, months)
        
        if success:
            # 积分兑换成功通知
            sender.reply(f"""
=====积分兑换成功=====
✅ 已扣除积分: {required_coins}
💰 剩余积分: {new_coins}
------------------
授权已处理完成
==================""")
            return True
        else:
            # 积分兑换失败，退还积分
            middleware.bucketSet('dd_sign_points', userid, str(user_coins))
            sender.reply(f"""
=====积分退还=====
⚠️ 授权处理失败，已退还积分
------------------
💰 当前积分: {user_coins}
==================""")
            return False
    except Exception as e:
        # 尝试退还积分（如果已扣除）
        try:
            original_coins = middleware.bucketGet('dd_sign_points', userid) or '0'
            original_coins = int(original_coins)
            if original_coins < user_coins:
                middleware.bucketSet('dd_sign_points', userid, str(user_coins))
        except:
            pass
            
        error_msg = f"""
=====兑换异常=====
❌ 积分兑换过程出错
------------------
错误: {str(e)}
=================="""
        print(f"积分兑换异常: {phone}, 错误: {str(e)}")
        sender.reply(error_msg)
        return False

def alq_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return
        
    auth_menu = f"""
=====爱路桥授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 一键提交青龙
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(auth_menu)
    xz = sender.listen(60000)
    
    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出授权管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '3':
        # 一键提交青龙
        sender.reply("🔄 正在一键提交所有已授权账号到青龙...")
        
        # 获取所有授权账号
        auth_phones = middleware.bucketAllKeys('s_alq_auth')
        if not auth_phones:
            sender.reply("""
=====提交失败=====
❌ 未找到任何已授权的爱路桥账号
==================""")
            return
            
        success_count = 0
        fail_count = 0
        
        for phone in auth_phones:
            try:
                # 获取账号授权状态
                auth_date = middleware.bucketGet('s_alq_auth', phone)
                
                # 验证是否是有效的授权日期
                if not auth_date or not auth_date.strip():
                    continue
                    
                # 检查授权是否已过期
                try:
                    auth_date_obj = datetime.strptime(auth_date, "%Y-%m-%d")
                    if auth_date_obj < datetime.now():
                        continue  # 已过期的授权跳过
                except ValueError:
                    continue  # 无效的日期格式
                
                # 获取账号token信息
                token_data = middleware.bucketGet('s_alq_token', phone)
                if not token_data:
                    fail_count += 1
                    continue
                    
                # 解析账号信息
                account_info = json.loads(token_data)
                
                # 更新青龙变量
                if update_ql_env(phone, account_info):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                print(f"处理账号失败: {phone}, 错误: {str(e)}")
                
        result_msg = f"""
=====提交青龙完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
=================="""
        sender.reply(result_msg)
        return
    elif xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('s_alq_user')
        if not users:
            sender.reply("""
=====授权失败=====
❌ 未找到任何绑定的爱路桥账号
==================""")
            return
            
        sender.reply(f"""
=====批量授权=====
请输入授权月数
回复数字设置月数
回复"q"退出操作
==================""")
        
        sjts = sender.listen(60000)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("✅ 已取消授权")
            return
        elif sjts is None:
            sender.reply("⏰ 操作超时,已退出")
            return
        
        try:
            months = int(sjts)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
                
            success_count = 0
            fail_count = 0
            
            for user in users:
                accountlist = middleware.bucketGet('s_alq_user', user)
                if accountlist == '' or accountlist == '{}':
                    continue
                    
                accounts = eval(accountlist)
                for account in accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('s_alq_auth', account)
                        token_data = middleware.bucketGet('s_alq_token', account)
                        
                        if not token_data:
                            fail_count += 1
                            continue
                            
                        account_info = json.loads(token_data)
                        
                        if accountVip and accountVip > dqsj:
                            # 如果当前已有有效授权，从授权到期时间开始计算
                            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                        else:
                            # 如果没有有效授权，从当前时间开始计算
                            start_date = datetime.now()
                            
                        # 计算新的到期时间 (按月计算，每月30天)
                        new_sqsj = start_date + timedelta(days=30*months)
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        # 更新授权时间
                        middleware.bucketSet('s_alq_auth', account, new_sqsj)
                        
                        # 更新青龙变量
                        if update_ql_env(account, account_info):
                            success_count += 1
                        else:
                            fail_count += 1
                            print(f"更新青龙变量失败: {account}")
                    except Exception as e:
                        fail_count += 1
                        print(f"处理账号失败: {account}, 错误: {str(e)}")
                        
            result_msg = f"""
=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {months} 个月
=================="""
            sender.reply(result_msg)
            
        except ValueError:
            sender.reply("❌ 月数必须是数字!")
            return
            
    elif xz == '2':
        # 单独授权用户
        user_guide = f"""
======账号授权======
请输入需要授权的账号ID
(发送myuid可获取ID)
------------------
回复"q"退出操作
=================="""
        sender.reply(user_guide)
        
        myuid = sender.listen(60000)
        if myuid == 'q' or myuid == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif myuid is None:
            sender.reply("⏰ 操作超时,已退出")
            return
            
        accountlist = middleware.bucketGet('s_alq_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"❌ 未找到 {myuid} 的爱路桥账号信息!")
            return
            
        accounts = eval(accountlist)
        account_list = """
========选择账号=======
[0] 全部账号"""
        
        for i, account in enumerate(accounts, 1):
            accountVip = middleware.bucketGet('s_alq_auth', account)
            vip_status = accountVip if accountVip else '未授权'
            account_list += f"""
[{i}]{mask_phone(account)}({vip_status})"""
            
        account_list += """
=====================
回复数字选择账号
回复'q'退出
====================="""
        sender.reply(account_list)
        
        xz = sender.listen(60000)
        if xz == 'q' or xz == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif xz is None:
            sender.reply("⏰ 操作超时,已退出")
            return
            
        auth_guide = """
=====设置授权时长=====
请输入要授权的月数
例如: 1 (表示授权1个月)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
        sender.reply(auth_guide)
        
        if xz == '0':
            # 授权该用户的所有账号
            sjts = sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                months = int(sjts)
                if months <= 0:
                    sender.reply("❌ 月数必须大于0")
                    return
                    
                success_count = 0
                for account in accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('s_alq_auth', account)
                        token_data = middleware.bucketGet('s_alq_token', account)
                        
                        if not token_data:
                            continue
                            
                        account_info = json.loads(token_data)
                        
                        if accountVip and accountVip > dqsj:
                            # 如果当前已有有效授权，从授权到期时间开始计算
                            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                        else:
                            # 如果没有有效授权，从当前时间开始计算
                            start_date = datetime.now()
                            
                        # 计算新的到期时间 (按月计算，每月30天)
                        new_sqsj = start_date + timedelta(days=30*months)
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        # 更新授权时间
                        middleware.bucketSet('s_alq_auth', account, new_sqsj)
                        
                        # 更新青龙变量
                        if update_ql_env(account, account_info):
                            success_count += 1
                        else:
                            print(f"更新青龙变量失败: {account}")
                    except Exception as e:
                        print(f"处理账号失败: {account}, 错误: {str(e)}")
                        
                result_msg = f"""
=====授权操作完成=====
✅ 成功授权: {success_count}个账号
⏰ 授权时长: {months}个月
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 月数必须是数字!")
                return
                
        elif 1 <= int(xz) <= len(accounts):
            # 授权单个账号
            account = accounts[int(xz)-1]
            sjts = sender.listen(60000)
            
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                months = int(sjts)
                if months <= 0:
                    sender.reply("❌ 月数必须大于0")
                    return
                    
                dqsj = datetime.now().strftime("%Y-%m-%d")
                accountVip = middleware.bucketGet('s_alq_auth', account)
                token_data = middleware.bucketGet('s_alq_token', account)
                
                if not token_data:
                    sender.reply("❌ 未找到账号token信息!")
                    return
                    
                account_info = json.loads(token_data)
                
                if accountVip and accountVip > dqsj:
                    # 如果当前已有有效授权，从授权到期时间开始计算
                    start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                else:
                    # 如果没有有效授权，从当前时间开始计算
                    start_date = datetime.now()
                    
                # 计算新的到期时间 (按月计算，每月30天)
                new_sqsj = start_date + timedelta(days=30*months)
                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                
                # 更新授权时间
                middleware.bucketSet('s_alq_auth', account, new_sqsj)
                
                # 更新青龙变量
                ql_result = update_ql_env(account, account_info)
                
                result_msg = f"""
=====授权成功=====
📱 手机号: {mask_phone(account)}
⏰ 授权时长: {months}个月
📅 到期时间: {new_sqsj}
------------------
🔄 青龙同步: {'成功' if ql_result else '失败'}
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 月数必须是数字!")
                return
        else:
            sender.reply("❌ 输入的序号无效!")
            return

def format_message(title, content_lines):
    """
    格式化消息，统一处理消息格式
    title: 消息标题
    content_lines: 消息内容行的列表
    """
    message = f"""
====={title}=====
"""
    for line in content_lines:
        message += f"{line}\n"
    return message

def show_error(title, error_msg, extra_info=None):
    """显示统一格式的错误消息"""
    content = [f"❌ {error_msg}"]
    if extra_info:
        content.append("------------------")
        if isinstance(extra_info, list):
            content.extend(extra_info)
        else:
            content.append(extra_info)
    
    return format_message(title, content)

def pay_order(project, months, money):
    """处理支付"""
    if float(money) == 0:
        sender.reply(f"""
=====授权成功=====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: 免费
==================""")
        return True
    
    # 检查是否启用码支付
    ma_pay_switch = PAYMENT_CONFIG['ma_pay_switch'].lower() == 'true'
    if ma_pay_switch:
        return handle_mapay_order(project, months, money)
        
    # 使用赞赏码支付
    zsm = middleware.bucketGet('s_alq_config', 'zsm')
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
        return False
        
    # 发送订单信息
    pay_msg = f"""
=====微信扫码支付====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)

    sender.replyImage(zsm)
    
    # 等待支付结果
    ddzf = sender.waitPay("q", 100 * 1000)
    if str(ddzf) == 'q':
        sender.reply('✅ 已取消支付')
        return False
        
    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
            
        # 支持新旧两种收款消息格式
        try:
            paid_amount = float(ddzf.get('Money') or ddzf.get('money', 0))
            pay_time = ddzf.get('Time') or ddzf.get('time', '').replace('T', ' ').split('.')[0]
            if not pay_time:
                pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            sender.reply("支付金额格式错误")
            return False
            
        if paid_amount >= float(money):
            return True
        else:
            sender.reply(f"""
=====支付失败=====
❌ 支付金额不足
------------------
💰 应付: {money}元
💵 实付: {paid_amount}元
==================""")
            return False
            
    except Exception as e:
        sender.reply(f"""
=====支付异常=====
❌ 支付验证失败
------------------
⚠️ 错误: {str(e)}
==================""")
        return False

def handle_mapay_order(project, months, money, pay_type=None):
    """处理码支付订单
    
    Args:
        project: 商品描述
        months: 月份
        money: 金额
        pay_type: 支付方式，如alipay、wxpay等，如果提供则直接使用
    """
    # 检查是否启用码支付
    ma_pay_switch = middleware.bucketGet('s_alq_config', 'ma_pay_switch') or 'false'
    if ma_pay_switch.lower() != 'true':
        sender.reply('❌ 码支付功能未开启')
        return False
    
    # 从卡密系统数据桶获取码支付配置
    PAYMENT_CONFIG['ma_pay_gateway'] = middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or ''
    PAYMENT_CONFIG['ma_pay_pid'] = middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or ''
    PAYMENT_CONFIG['ma_pay_key'] = middleware.bucketGet('dd_sign_config', 'ma_pay_key') or ''
    PAYMENT_CONFIG['ma_pay_type'] = middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay'
    PAYMENT_CONFIG['ma_pay_notify_url'] = middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or 'http://localhost/notify'
    PAYMENT_CONFIG['ma_pay_return_url'] = middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or 'http://localhost/return'
    
    # 同步配置到标准字段
    PAYMENT_CONFIG['pid'] = PAYMENT_CONFIG['ma_pay_pid']
    PAYMENT_CONFIG['key'] = PAYMENT_CONFIG['ma_pay_key']
    PAYMENT_CONFIG['gateway'] = PAYMENT_CONFIG['ma_pay_gateway']
    PAYMENT_CONFIG['notify_url'] = PAYMENT_CONFIG['ma_pay_notify_url'] 
    PAYMENT_CONFIG['return_url'] = PAYMENT_CONFIG['ma_pay_return_url']
    
    # 检查配置是否完整
    if not (PAYMENT_CONFIG['gateway'] and PAYMENT_CONFIG['pid'] and PAYMENT_CONFIG['key']):
        sender.reply('❌ 卡密系统的码支付配置不完整，请联系管理员')
        return False
    
    # 添加支付锁检查
    pay_lock_key = 'recharge_lock'
    lock_info = middleware.bucketGet('dd_sign_config', pay_lock_key)
    if lock_info:
        try:
            lock_data = json.loads(lock_info)
            # 检查锁是否过期(2分钟)
            if time.time() - lock_data['time'] < 120:
                sender.reply('当前有其他用户正在支付中，请稍后再试!')
                return False
        except:
            pass
    
    # 设置支付锁
    lock_data = {
        'user': userid,
        'time': int(time.time())
    }
    middleware.bucketSet('dd_sign_config', pay_lock_key, json.dumps(lock_data))
    
    try:
        # 保留两位小数
        amount = round(float(money), 2)
        
        # 生成商户订单号
        out_trade_no = f"ALQ{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        
        # 如果已提供支付方式，直接使用
        if pay_type:
            selected_type = pay_type
        else:
            # 解析支付方式
            pay_types_str = PAYMENT_CONFIG['ma_pay_type'].strip()
            if not pay_types_str:
                pay_types_str = "alipay,wxpay"  # 默认支付方式
                
            pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
            
            # 选择支付方式
            if len(pay_types) == 1:
                # 只有一种支付方式，直接使用
                selected_type = pay_types[0]
                
                # 显示支付信息
                sender.reply(f"""===== 支付信息 =====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {amount}元
------------------
💳 支付方式: {PAY_TYPE_NAMES.get(selected_type, selected_type)}
------------------
正在创建支付订单...
==================""")
            else:
                # 多种支付方式，让用户选择
                pay_options_text = """=====选择支付方式====="""
                for i, t in enumerate(pay_types, 1):
                    pay_options_text += f"\n[{i}] {PAY_TYPE_NAMES.get(t, t)}"
                    
                pay_options_text += """
------------------
回复数字选择支付方式
回复"q"取消支付
=================="""
                
                sender.reply(pay_options_text)
                
                choice = sender.input(120000, 1, False)
                
                if choice.lower() == 'q':
                    sender.reply('✅ 已取消支付')
                    middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
                    return False
                    
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(pay_types):
                        selected_type = pay_types[choice_idx]
                        
                        # 显示支付信息
                        sender.reply(f"""===== 支付信息 =====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: {amount}元
------------------
💳 支付方式: {PAY_TYPE_NAMES.get(selected_type, selected_type)}
------------------
正在创建支付订单...
==================""")
                    else:
                        sender.reply('❌ 选择无效，已取消支付')
                        middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
                        return False
                except ValueError:
                    sender.reply('❌ 输入无效，已取消支付')
                    middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
                    return False
        
        # 使用MAPI接口
        ma_pay_api = MaPay_Api(PAYMENT_CONFIG)
        
        # 创建支付订单
        try:
            success, result, msg = ma_pay_api.create_payment(
                amount=amount,
                out_trade_no=out_trade_no,
                name=f"{project}-{str(amount)}",
                user_id=userid,
                pay_type=selected_type
            )
        except Exception as e:
            sender.reply(f'❌ 创建订单时出错: {str(e)}')
            middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
            return False
        
        if not success:
            sender.reply(f'❌ 创建订单失败: {msg}')
            middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
            return False
            
        # 提取支付链接
        pay_url = None
        qrcode = result.get('qrcode', '')
        payurl = result.get('payurl', '')
        code_url = result.get('code_url', '')
        trade_no = result.get('trade_no', '')
        
        # 如果qrcode包含/ewm/,拼接支付网关
        if qrcode and '/ewm/' in qrcode and not qrcode.startswith('http'):
            code_url = qrcode
            qrcode = None

        # 根据返回数据类型构建支付链接
        if payurl:
            pay_url = payurl
        elif qrcode:
            pay_url = qrcode
        elif code_url:
            # 如果有二维码图片地址，构建完整URL
            if not code_url.startswith('http'):
                gateway = PAYMENT_CONFIG['gateway']
                if gateway.endswith('/'):
                    gateway = gateway[:-1]
                pay_url = f"{gateway}/{code_url}"
            else:
                pay_url = code_url
                
        if not pay_url:
            sender.reply('❌ 获取支付链接失败')
            middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
            return False
        
        # 发送支付链接
        selected_type_name = PAY_TYPE_NAMES.get(selected_type, selected_type)
        
        # 如果有二维码链接，生成二维码并发送
        if qrcode:
            sender.reply(f'请使用【{selected_type_name}】扫描下方二维码完成支付:')
            qrcode_api_url = generate_qrcode(qrcode)
            if qrcode_api_url:
                if selected_type == "qqpay":
                    sender.reply('QQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！')
                    sender.replyImage(qrcode)
                else:
                    sender.replyImage(qrcode_api_url)
            else:
                # 如果生成失败，直接发送链接
                sender.reply(f"二维码生成失败，请使用【{selected_type_name}】打开链接：\n{qrcode}")
        else:
            # 没有二维码链接，直接发送支付链接
            if code_url:
                sender.reply(f'请使用【{selected_type_name}】扫描下方二维码完成支付:')
                sender.replyImage(pay_url)
            else:
                sender.reply(f'请使用【{selected_type_name}】打开以下链接完成支付:\n{pay_url}')
            
        sender.reply('支付过程中输入"q"可取消支付')
        
        # 轮询支付结果
        is_paid, msg, data = poll_mapi_payment_status(out_trade_no)
        
        # 释放支付锁
        middleware.bucketDel('dd_sign_config', pay_lock_key)
        
        if is_paid:
            # 支付成功
            return True
        else:
            # 支付失败或超时
            sender.reply(f"❌ 支付未完成: {msg}")
            return False
        
    except Exception as e:
        sender.reply(f'❌ 处理支付订单时出错: {str(e)}')
        # 释放支付锁
        middleware.bucketDel('dd_sign_config', pay_lock_key)
        return False

def generate_qrcode(url):
    """生成二维码图片
    
    Args:
        url: 要生成二维码的URL
        
    Returns:
        str: 二维码API的URL
    """
    try:
        # 使用 qrtool.cn 的API生成二维码
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        # 生成失败时返回原始URL
        return None

# 码支付API类
class MaPay_Api:
    def __init__(self, config):
        """初始化码支付API类
        
        Args:
            config (dict): 配置信息，包含以下字段:
                - gateway: 支付网关地址，例如 https://mpay.vorto.cn
                - pid: 商户ID
                - key: 商户密钥
                - notify_url: 异步通知地址
                - return_url: 跳转通知地址
                - pay_type: 支付方式，多个用逗号分隔
        """
        self.config = config
        self.pay_type_names = {
            'alipay': '支付宝',
            'wxpay': '微信支付',
            'qqpay': 'QQ钱包',
        }

    def calculate_md5(self, text):
        """计算字符串的MD5值"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    def sort_dict_by_key(self, data):
        """对字典按照键名排序"""
        return dict(sorted(data.items(), key=lambda x: x[0]))

    def create_payment(self, amount, out_trade_no, name, user_id, pay_type=None, sitename=""):
        """创建支付订单 (mapi接口)
        
        Args:
            amount: 支付金额
            out_trade_no: 商户订单号
            name: 商品名称
            user_id: 用户ID (会传递到param参数)
            pay_type: 支付方式，如果为None则使用配置中的默认支付方式
            sitename: 网站名称 (可选)
            
        Returns:
            (success, pay_data, msg): 是否成功、支付数据、消息
        """
        try:
            # 获取支付方式
            if pay_type is None:
                pay_types = [p.strip() for p in self.config['ma_pay_type'].split(',') if p.strip()]
                if not pay_types:
                    pay_types = ["alipay", "wxpay"]
                pay_type = pay_types[0]  # 默认使用第一个支付方式
            
            # 构造支付参数
            params = {
                'pid': self.config['pid'],
                'type': pay_type,
                'out_trade_no': out_trade_no,
                'notify_url': self.config['notify_url'],
                'return_url': self.config['return_url'],
                'name': name,
                'money': str(amount),
                'sitename': sitename,
                'param': user_id
            }
            
            # 移除空值
            params = {k: v for k, v in params.items() if v}
            
            # 按照ASCII码排序参数
            sorted_params = self.sort_dict_by_key(params)
            
            # 拼接成key=value&key=value格式
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
            
            # 添加密钥进行MD5签名
            sign = self.calculate_md5(sign_str + self.config['key']).lower()
            
            # 添加签名到参数
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            # 构建mapi接口URL
            mapi_url = self.config['gateway']
            if mapi_url.endswith('/'):
                mapi_url = mapi_url[:-1]
            mapi_url = f"{mapi_url}/mapi.php"
            
            # 发送POST请求
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"创建支付订单失败，HTTP状态码: {response.status_code}"
            
            # 解析响应
            try:
                result = response.json()
            except:
                return False, None, "创建支付订单失败，返回数据格式错误"
            
            # 判断返回结果
            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')
            
            if code == 1:  # 码支付API返回的成功状态码是1
                # 支付成功，返回支付数据
                return True, result, msg
            else:
                return False, None, msg
                
        except Exception as e:
            return False, None, f"创建订单失败: {str(e)}"

    def query_order(self, order_no, order_type=2):
        """查询订单状态
        
        Args:
            order_no: 订单号
            order_type: 订单号类型，1:商户订单号，2:系统订单号
            
        Returns:
            (success, data, msg): 是否成功、订单数据、消息
        """
        try:
            # 构建查询接口URL
            query_url = self.config['gateway']
            if query_url.endswith('/'):
                query_url = query_url[:-1]
            query_url = f"{query_url}/api/findorder"
            
            # 构建请求数据
            params = {
                "order_no": order_no,  # 订单号
                "type": order_type     # 订单号类型
            }
            
            # 发送GET请求
            response = requests.get(query_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"查询订单失败，HTTP状态码: {response.status_code}"
            
            # 解析响应
            try:
                result = response.json()
            except:
                return False, None, "查询订单失败，返回数据格式错误"
            
            # 判断返回结果
            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')
            data = result.get('data', {})
            
            if code == 200:  # 码支付API返回的成功状态码是200
                # 查询成功，返回订单数据
                # 检查订单状态
                order_status = data.get('status')
                if order_status == 1:  # 假设1表示支付成功
                    return True, data, "支付成功"
                else:
                    return True, data, "订单未支付"
            else:
                return True, data, "未找到订单数据"
                
        except Exception as e:
            return False, None, f"查询订单异常: {str(e)}"
            
    def verify_sign(self, params, sign):
        """验证签名
        
        Args:
            params: 参数字典
            sign: 签名值
            
        Returns:
            bool: 验证结果
        """
        try:
            # 移除sign和sign_type字段以及空值
            verify_params = {k: v for k, v in params.items() if v and k != "sign" and k != "sign_type"}
            
            # 按键名ASCII码排序（a-z）
            sorted_params = self.sort_dict_by_key(verify_params)
            
            # 拼接成key=value&key=value格式
            params_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
            
            # 拼接商户密钥
            sign_str = params_str + self.config['key']
            
            # MD5签名
            calculated_sign = self.calculate_md5(sign_str).lower()
            
            # 比较签名
            return calculated_sign == sign.lower()
        except Exception as e:
            return False

# 添加轮询MAPI支付状态的函数
def poll_mapi_payment_status(order_no, order_type=2, max_tries=30):
    """轮询MAPI支付状态
    
    Args:
        order_no: 订单号
        order_type: 订单号类型，1:商户订单号，2:系统订单号
        max_tries: 最大尝试次数
        
    Returns:
        (is_paid, msg, data): 是否支付成功、消息和数据
    """
    # 从卡密系统数据桶获取最新配置
    PAYMENT_CONFIG['ma_pay_gateway'] = middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or ''
    PAYMENT_CONFIG['ma_pay_pid'] = middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or ''
    PAYMENT_CONFIG['ma_pay_key'] = middleware.bucketGet('dd_sign_config', 'ma_pay_key') or ''
    
    # 同步配置到标准字段
    PAYMENT_CONFIG['pid'] = PAYMENT_CONFIG['ma_pay_pid']
    PAYMENT_CONFIG['key'] = PAYMENT_CONFIG['ma_pay_key']
    PAYMENT_CONFIG['gateway'] = PAYMENT_CONFIG['ma_pay_gateway']
    
    # 创建MaPay_Api实例
    ma_pay_api = MaPay_Api(PAYMENT_CONFIG)
    
    for i in range(max_tries):
        # 查询订单状态
        success, data, msg = ma_pay_api.query_order(order_no, order_type)

        # 如果查询成功且订单已支付
        if success and isinstance(data, dict) and data.get('status') == 1:
            return True, msg, data
            
        # 等待用户输入或超时
        result = sender.listen(5000)  # 等待5秒
        if result == 'q':
            return False, "用户取消", None
            
    return False, "查询超时，订单可能尚未支付", None

def main():
    global randommanagecommand, randomquerycommand
    global randomsigncommand, alqVipmoney, alqcoin
    
    # 获取必要的配置
    (_, _, randommanagecommand, randomquerycommand,
     randomsigncommand, alqVipmoney, alqcoin) = get_user_content()
    
    imtype = sender.getImtype()
    usermessage = sender.getMessage()
    
    if '登录' in usermessage or '登陆' in usermessage:
        bind_account()
    elif '管理' in usermessage:
        manage_account()
    elif '查询' in usermessage:
        query_accounts()
    elif '爱路桥教程' in usermessage:
        show_tutorial()
    elif '爱路桥授权' in usermessage:
        alq_auth()
    else:
        sender.setContinue()

if __name__ == "__main__":
    main() 