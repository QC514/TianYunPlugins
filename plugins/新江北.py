#[title: 新江北]
#[language: python]
#[class: 工具类]
#[service: 2993959969] 售后联系方式
#[author: rujingxianghai] 作者
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^(新江北|xjb)(登录|登陆)$|^登(录|陆)(新江北|xjb)$|^(新江北|xjb)(查询|管理)$|^(查询|管理)(新江北|xjb)$|^新江北清理$|^新江北检测$|^新江北授权$|^新江北教程$]
#[cron: 0 0 0 0 0] cron定时，支持5位域和6位域
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: https://img-cf.885666.xyz/67a4e3f375b22339a460f197a764f645.png]图标链接地址，请使用48像素的正方形图标，支持http和https
#[version: 1.1.3]版本号
#[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
#[price: 8.88] 上架价格
# [description: 新江北积分任务，低保项目。每日签到+抽奖提现（不需要抓包）、任务积分（需抓包）<br>指令：新江北登录、管理、查询、授权、教程、检测、清理<br>脚本及卡密进群获取<br>1.0.0：基础版本<br>1.1.3：修复MaPay_Api缺少query_order方法的错误]

import os
import json
import time
import random
import string
import requests
from datetime import datetime, timedelta
import middleware
import hashlib
import hmac
import base64
import uuid
from urllib.parse import quote
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_xjb_user', key=userid)

# [param: {"required":true,"key":"s_xjb_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"s_xjb_config.xjb_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割"}]
# [param: {"required":true,"key":"s_xjb_config.xjb_osname","bool":false,"placeholder":"必填项,例:S_XJB","name":"提交到青龙的变量名","desc":"青龙容器内新江北的变量名"}]
# [param: {"required":true,"key":"s_xjb_config.xjbVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"s_xjb_config.xjbcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"s_xjb_config.notify","bool":false,"placeholder":"例:qq,wx,tg","name":"通知渠道","desc":"检测功能的通知渠道，多个渠道用逗号分隔"}]
# [param: {"required":true,"key":"s_xjb_config.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付，关闭则使用扫码支付。推荐码支付对接：https://mzf.vorto.cn"}]

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 's_xjb_config',
    'coin_key': 'dd_sign_points',
    'name': '新江北'
}

# 支付配置
PAYMENT_CONFIG = {
    'zsm': middleware.bucketGet('s_xjb_config', 'zsm') or '',  # 赞赏码链接
    'ma_pay_switch': middleware.bucketGet('s_xjb_config', 'ma_pay_switch') or 'false',  # 码支付开关
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

# 全局变量存储支付状态
payment_status = {}

# 新江北API常量
A = "102"  # X-TENANT-ID
B = "10050"  # client_id
C = "FR*r!isE5W"  # 签名密钥

def get_user_content():
    """获取用户配置内容"""
    xjb_osname = middleware.bucketGet('s_xjb_config', 'xjb_osname') or 'S_XJB'
    xjb_qlname = middleware.bucketGet('s_xjb_config', 'xjb_qlname') or ''
    xjb_managecommand = middleware.bucketGet('s_xjb_config', 'xjb_managecommand') or '新江北管理'
    xjb_querycommand = middleware.bucketGet('s_xjb_config', 'xjb_querycommand') or '新江北查询'
    xjb_signcommand = middleware.bucketGet('s_xjb_config', 'xjb_signcommand') or '新江北登录'
    
    randommanagecommand = xjb_managecommand
    randomquerycommand = xjb_querycommand
    randomsigncommand = xjb_signcommand
    
    xjbVipmoney = float(middleware.bucketGet('s_xjb_config', 'xjbVipmoney') or '1')
    
    # 优先从卡密系统获取积分配置
    xjbcoin = middleware.bucketGet(PLUGIN_CONFIG['bucket'], PLUGIN_CONFIG['coin_key'])
    if not xjbcoin:
        # 如果卡密系统未配置，则使用插件配置
        xjbcoin = middleware.bucketGet('s_xjb_config', 'xjbcoin') or '0'
    xjbcoin = int(xjbcoin)
    
    return (xjb_osname, xjb_qlname, randommanagecommand, 
            randomquerycommand, randomsigncommand, xjbVipmoney, xjbcoin)

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

def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())

def generate_device_info():
    """生成设备信息"""
    version = "1.7.0"
    device_uuid = generate_uuid()
    
    devices = [
        "M1903F2A", "M2001J2E", "M2001J2C", "M2001J1E", "M2001J1C",
        "M2002J9E", "M2011K2C", "M2102K1C", "M2101K9C", "2107119DC",
        "2201123C", "2112123AC", "2201122C", "2211133C", "2210132C",
        "2304FPN6DC", "23127PN0CC", "24031PN0DC", "23090RA98C",
        "2312DRA50C", "2312CRAD3C", "2312DRAABC", "22101316UCP", "22101316C"
    ]
    
    device = random.choice(devices)
    device_name = f"Xiaomi {device}"
    android_version = "11"
    os_name = "Android"
    
    ua = f"{os_name.upper()};{android_version};{B};{version};1.0;null;{device}"
    common_ua = f"{version};{device_uuid};{device_name};{os_name};{android_version};6.9.0"
    
    return ua, common_ua, device_uuid

def get_signature(path, session_id="", request_uuid=""):
    """生成API签名"""
    timestamp = int(time.time() * 1000)
    if not request_uuid:
        request_uuid = generate_uuid()
    
    # 移除查询参数
    if "?" in path:
        path = path.split("?")[0]
    
    # 构建签名字符串
    sign_string = f"{path}&&{session_id}&&{request_uuid}&&{timestamp}&&{C}&&{A}"
    
    # SHA256哈希
    signature = hashlib.sha256(sign_string.encode()).hexdigest()
    
    return {
        'uuid': request_uuid,
        'timestamp': timestamp,
        'signature': signature
    }

def get_passport_signature(body_params, signature_key, request_uuid=""):
    """生成passport API签名"""
    if not request_uuid:
        request_uuid = generate_uuid()
    
    # 构建签名字符串
    sign_string = f"post%%/web/oauth/credential_auth?{body_params}%%{request_uuid}%%"
    
    # HMAC-SHA256
    signature = hmac.new(
        signature_key.encode(),
        sign_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return {
        'uuid': request_uuid,
        'signature': signature
    }

def encrypt_password(password):
    """使用RSA加密密码"""
    try:
        # 与JavaScript代码中相同的公钥
        public_key_str = """-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXi
zPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXF
c+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlT
HMlluw4ZYmnOwg+thwIDAQAB
-----END PUBLIC KEY-----"""
        
        # 导入公钥
        public_key = RSA.importKey(public_key_str)
        cipher = PKCS1_v1_5.new(public_key)
        
        # 加密密码
        encrypted_password = cipher.encrypt(password.encode('utf-8'))
        encrypted_password_b64 = base64.b64encode(encrypted_password).decode('utf-8')
        
        return encrypted_password_b64
    except Exception as e:
        print(f"❌ RSA加密失败: {e}")
        return password  # 如果加密失败，返回原始密码

def request_passport_api(path, ua):
    """请求passport API"""
    url = f"https://passport.tmuyun.com{path}"
    
    headers = {
        "Connection": "Keep-Alive",
        "Cache-Control": "no-cache",
        "X-REQUEST-ID": generate_uuid(),
        "Accept-Encoding": "gzip",
        "user-agent": ua
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ passport API请求失败: {e}")
        return None

def request_passport_post(path, data, ua, signature_key):
    """发送passport POST请求"""
    url = f"https://passport.tmuyun.com{path}"
    
    # 生成签名
    sig_info = get_passport_signature(data, signature_key)
    
    headers = {
        "Connection": "Keep-Alive",
        "X-REQUEST-ID": sig_info['uuid'],
        "X-SIGNATURE": sig_info['signature'],
        "Cache-Control": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Accept-Encoding": "gzip",
        "user-agent": ua
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        return response.json()
    except Exception as e:
        print(f"❌ passport POST请求失败: {e}")
        return None

def request_vapp_api(path, session_id, account_id, common_ua, method='GET', data=None):
    """请求vapp API"""
    url = f"https://vapp.tmuyun.com{path}"
    
    sig_info = get_signature(path, session_id)
    
    headers = {
        "Connection": "Keep-Alive",
        "X-TIMESTAMP": str(sig_info['timestamp']),
        "X-SESSION-ID": session_id,
        "X-REQUEST-ID": sig_info['uuid'],
        "X-SIGNATURE": sig_info['signature'],
        "X-TENANT-ID": A,
        "X-ACCOUNT-ID": account_id,
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip",
        "user-agent": common_ua
    }
    
    # 为POST请求添加Content-Type
    if method.upper() == 'POST':
        headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        else:
            # 确保data不为None
            if data is None:
                data = ""
            response = requests.post(url, headers=headers, data=data, timeout=10)
        
        time.sleep(1)  # 避免请求过快
        return response.json()
    except Exception as e:
        print(f"❌ API请求失败: {e}")
        return None

def get_user_info(account_info):
    """获取用户信息和积分"""
    try:
        phone = account_info.get('phone', '')
        password = account_info.get('password', '')
        
        if not phone or not password:
            return {"success": False, "message": "账号信息不完整"}
        
        # 生成设备信息
        ua, common_ua, device_uuid = generate_device_info()
        
        # 1. 获取sessionId
        result = request_vapp_api("/api/account/init", "", "", common_ua, 'POST')
        if not result or not result.get('data') or not result['data'].get('session'):
            return {"success": False, "message": "获取sessionId失败"}
        
        session_id = result['data']['session']['id']
        
        # 2. 获取signature_key
        result = request_passport_api(f"/web/init?client_id={B}", ua)
        if not result or not result.get('data') or not result['data'].get('client'):
            return {"success": False, "message": "获取signature_key失败"}
        
        signature_key = result['data']['client']['signature_key']
        
        # 3. RSA加密密码
        encrypted_password = encrypt_password(password)
        
        # URL编码加密后的密码
        encoded_password = quote(encrypted_password)
        
        data = f"client_id={B}&password={encoded_password}&phone_number={phone}"
        
        # 4. 获取授权码
        result = request_passport_post("/web/oauth/credential_auth", data, ua, signature_key)
        if not result or not result.get('data') or not result['data'].get('authorization_code'):
            return {"success": False, "message": f"获取授权码失败: {result.get('message', '未知错误')}"}
        
        auth_code = result['data']['authorization_code']['code']
        
        # 5. 登录
        data = f"check_token=&code={auth_code}&token=&type=-1&union_id="
        result = request_vapp_api("/api/zbtxz/login", session_id, "", common_ua, 'POST', data)
        
        if not result or not result.get('data') or not result['data'].get('session'):
            return {"success": False, "message": "登录失败"}
        
        account_id = result['data']['session']['account_id']
        session_id = result['data']['session']['id']
        
        # 6. 查询积分
        result = request_vapp_api("/api/user_mumber/account_detail", session_id, account_id, common_ua)
        
        if result and result.get('data') and result['data'].get('rst'):
            integral = result['data']['rst'].get('total_integral', 0)
            return {
                "success": True,
                "integral": str(integral),
                "account_id": account_id,
                "session_id": session_id
            }
        else:
            return {"success": False, "message": "查询积分失败"}
            
    except Exception as e:
        return {"success": False, "message": str(e)}

def bind_account():
    """绑定新江北账号"""
    # 手机号输入
    phone_guide_lines = [
        "请输入手机号码",
        "------------------",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("账号绑定", phone_guide_lines))
    
    phone = sender.input(120000, 1, False)
    if not phone or phone.lower() == 'q':
        sender.reply("✅ 已取消绑定")
        return None
        
    # 验证手机号格式
    if not phone.isdigit() or len(phone) != 11:
        sender.reply("❌ 手机号格式错误，请输入11位数字")
        return None
    
    # 密码输入
    password_guide_lines = [
        f"📱 手机号: {mask_phone(phone)}",
        "------------------",
        "请输入密码",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("输入密码", password_guide_lines))
    
    password = sender.input(120000, 1, False)
    if not password or password.lower() == 'q':
        sender.reply("✅ 已取消绑定")
        return None
    
    # 支付宝姓名输入
    alipay_name_guide_lines = [
        f"📱 手机号: {mask_phone(phone)}",
        "------------------",
        "请输入支付宝姓名",
        "💡 提示: 填写支付宝实名姓名",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("输入支付宝姓名", alipay_name_guide_lines))
    
    alipay_name = sender.input(120000, 1, False)
    if not alipay_name or alipay_name.lower() == 'q':
        sender.reply("✅ 已取消绑定")
        return None
    
    # 支付宝账号输入
    alipay_account_guide_lines = [
        f"📱 手机号: {mask_phone(phone)}",
        "------------------",
        "请输入支付宝账号",
        "💡 提示: 可以是手机号或邮箱",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("输入支付宝账号", alipay_account_guide_lines))
    
    alipay_account = sender.input(120000, 1, False)
    if not alipay_account or alipay_account.lower() == 'q':
        sender.reply("✅ 已取消绑定")
        return None
    
    # SessionID输入（可选）
    session_id_guide_lines = [
        f"📱 手机号: {mask_phone(phone)}",
        f"💳 支付宝账号: {alipay_account}",
        "------------------",
        "请输入SessionID（可选）",
        "💡 提示: 留空可自动获取",
        "直接回复\"n\"跳过",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("输入SessionID（可选）", session_id_guide_lines))
    
    session_id = sender.input(120000, 1, False)
    if session_id and session_id.lower() == 'q':
        sender.reply("✅ 已取消绑定")
        return None
    
    # 如果输入为空或只是回车，则不设置sessionid
    if session_id.strip() == "n":
        session_id = ""
    
    # 验证账号
    sender.reply("🔄 正在验证账号...")
    account_info = {
        'phone': phone,
        'password': password,
        'alipay_name': alipay_name,
        'alipay_account': alipay_account,
        'session_id': session_id  # 添加sessionid字段
    }
    
    # 仅验证登录账号，不验证支付宝信息
    login_info = {
        'phone': phone,
        'password': password
    }
    
    user_info = get_user_info(login_info)
    if not user_info.get("success"):
        sender.reply(f"❌ 账号验证失败: {user_info.get('message', '未知错误')}")
        return None
    
    # 更新用户账号列表 - 使用手机号作为标识
    if not uservalue:
        middleware.bucketSet('s_xjb_user', userid, str([phone]))
    else:
        accounts = eval(uservalue)
        if phone not in accounts:
            accounts.append(phone)
            middleware.bucketSet('s_xjb_user', userid, str(accounts))
    
    # 保存账号详细信息 - 使用手机号作为key，包含支付宝信息
    middleware.bucketSet('s_xjb_token', phone, json.dumps(account_info))
    
    success_lines = [
        f"📱 手机号: {mask_phone(phone)}",
        f"💳 支付宝账号: {alipay_account}",
        f"💰 积分: {user_info.get('integral', '0')}"
    ]
    
    if session_id:
        success_lines.append(f"🔑 SessionID: {session_id[:20]}...")
    else:
        success_lines.append("🔑 SessionID: 自动获取")
        
    sender.reply(format_message("绑定成功", success_lines))
    
    # 检查账号是否已授权，如果已授权且未过期则直接更新青龙变量
    dqsj = datetime.now().strftime("%Y-%m-%d")
    accountVip = middleware.bucketGet('s_xjb_auth', phone)  # 使用手机号作为key
    
    if accountVip and accountVip > dqsj:
        # 账号已授权且未过期，直接更新青龙变量
        ql_result = update_ql_env(phone, account_info)
        auth_result = f"""
=====账号已授权=====
📱 手机号: {mask_phone(phone)}
💰 积分: {user_info.get('integral', '0')}
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
❗ 您可以稍后使用"新江北管理"命令进行授权
==================""")

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply(format_message("未绑定账号", [
            "❌ 未找到任何账号信息",
            f"💡 发送 新江北登录 绑定"
        ]))
        return
        
    accounts = eval(uservalue)
    account_list_lines = ["[0] 全部账号"]
    
    for i, account in enumerate(accounts, 1):
        account_info_str = middleware.bucketGet('s_xjb_token', account)
        if not account_info_str:
            continue
            
        auth_time = middleware.bucketGet('s_xjb_auth', account)
        
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
                account_info_str = middleware.bucketGet('s_xjb_token', account)
                if not account_info_str:
                    sender.reply(show_error("账号不存在", "未找到账号信息", f"📱 账号: {account}"))
                    continue
                    
                account_info = json.loads(account_info_str)
                
                # 获取用户信息
                user_info = get_user_info(account_info)
                if not user_info.get("success"):
                    sender.reply(show_error("获取信息失败", user_info.get("message", "未知错误"), f"📱 账号: {account}"))
                    continue
                
                # 获取授权状态
                auth_time = middleware.bucketGet('s_xjb_auth', account)
                if not auth_time:
                    auth_status = '到期: 未授权'
                elif auth_time < str(datetime.now().date()):
                    auth_status = '到期: 已过期'
                else:
                    auth_status = f'到期: {auth_time}'
                
                # 构建账号信息
                info_lines = [
                    f"📱 账号: {mask_phone(account)}",
                    f"💰 积分: {user_info.get('integral', '0')}",
                    f"📅 {auth_status}"
                ]
                
                # 添加支付宝信息显示
                try:
                    alipay_name = account_info.get('alipay_name', '')
                    alipay_account = account_info.get('alipay_account', '')
                    session_id = account_info.get('session_id', '')
                    
                    if alipay_account:
                        # 对支付宝账号进行脱敏处理
                        if '@' in alipay_account:  # 邮箱格式
                            masked_alipay = alipay_account[:3] + '***' + alipay_account[alipay_account.find('@'):]
                        elif len(alipay_account) == 11:  # 手机号格式
                            masked_alipay = mask_phone(alipay_account)
                        else:
                            masked_alipay = alipay_account[:3] + '***'
                        info_lines.append(f"💳 支付宝账号: {masked_alipay}")
                    
                    # 显示SessionID状态
                    if session_id:
                        info_lines.append(f"🔑 SessionID: {session_id[:20]}...")
                    else:
                        info_lines.append("🔑 SessionID: 未绑定")
                        
                except Exception:
                    pass  # 如果获取信息出错，不影响其他信息显示
                
                # 获取红包明细
                try:
                    red_packet_result = get_red_packet_details(user_info)
                    if red_packet_result.get("success") and red_packet_result.get("data") and red_packet_result["data"].get("records"):
                        records = red_packet_result["data"]["records"]
                        if records:
                            red_packet_details = format_red_packet_details(records)
                            info_lines.append("-------------------")
                            info_lines.extend(red_packet_details)
                except Exception as e:
                    print(f"获取红包明细失败: {str(e)}")
                    # 失败不影响其他信息显示
                
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

def get_ql_config():
    """获取青龙配置信息"""
    try:
        qlconfig = middleware.bucketGet('s_xjb_config', 'xjb_qlname')
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
        print(f"开始更新青龙变量: {phone}")
        
        # 从配置中获取青龙信息
        ql_config = get_ql_config()
        if ql_config['code'] != 200:
            print(f"获取青龙配置失败: {ql_config['msg']}")
            return False
            
        host = ql_config['data'].get('url', '')
        client_id = ql_config['data'].get('client_id', '')
        client_secret = ql_config['data'].get('client_secret', '')
        
        if not host or not client_id or not client_secret:
            print("青龙配置信息不完整")
            return False
            
        print(f"青龙地址: {host}")
            
        # 获取token
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            print("获取青龙token失败")
            return False
            
        print("青龙token获取成功")
            
        # 获取配置的变量名
        env_name = middleware.bucketGet('s_xjb_config', 'xjb_osname') or 'S_XJB'
        print(f"变量名: {env_name}")
        
        # 构建变量值 - 使用手机号#密码#支付宝姓名#支付宝账号#sessionid格式
        password = account_info.get('password', '')
        alipay_name = account_info.get('alipay_name', '')
        alipay_account = account_info.get('alipay_account', '')
        session_id = account_info.get('session_id', '')  # 可选的sessionid
        
        if not password:
            print(f"账号信息不完整: {phone}")
            return False
            
        # 构建5段格式变量值：手机号#密码#支付宝姓名#支付宝账号#sessionid
        # 如果支付宝信息为空，使用空字符串占位，确保兼容性
        if session_id:
            value = f"{phone}#{password}#{alipay_name}#{alipay_account}#{session_id}"
            print(f"变量值: {phone}#***#{alipay_name}#{alipay_account[:3] if alipay_account else ''}***#{session_id[:20] if session_id else ''}...")
        else:
            value = f"{phone}#{password}#{alipay_name}#{alipay_account}"
            print(f"变量值: {phone}#***#{alipay_name}#{alipay_account[:3] if alipay_account else ''}***")
        
        # 构建变量备注
        auth_time = middleware.bucketGet('s_xjb_auth', phone) or '未授权'
        remark = f"新江北:{phone}丨到期:{auth_time}"
        print(f"变量备注: {remark}")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            # 获取所有环境变量
            print("正在获取环境变量列表...")
            response = requests.get(f'{host}/open/envs', headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"获取环境变量失败: {response.text}")
                return False
                
            envs = response.json().get('data', [])
            if not envs:
                envs = []  # 确保envs不为None
            print(f"找到 {len(envs)} 个环境变量")
            env_id = None
            
            # 查找是否已存在该变量
            for env in envs:
                if not env:  # 跳过None或空值
                    continue
                # 精确匹配：变量名必须一致，并且备注中必须包含该手机号
                env_remarks = env.get('remarks', '') or ''  # 确保不为None
                env_name_val = env.get('name', '') or ''    # 确保不为None
                if env_name_val == env_name and f"新江北:{phone}" in env_remarks:
                    env_id = env.get('_id') or env.get('id')
                    print(f"找到已存在的变量，ID: {env_id}")
                    break
            
            # 构建变量数据
            env_data = {
                "name": env_name,
                "value": value,
                "remarks": remark
            }
            
            if env_id:
                # 更新已存在的变量
                print("正在更新已存在的变量...")
                env_data["id"] = env_id
                response = requests.put(f'{host}/open/envs', headers=headers, json=env_data, timeout=10)
                if response.status_code != 200:
                    print(f"更新环境变量失败: {response.text}")
                    return False
                    
                # 启用变量
                try:
                    requests.put(f'{host}/open/envs/enable', headers=headers, json=[env_id], timeout=10)
                    print("变量已启用")
                except Exception as e:
                    print(f"启用变量异常: {str(e)}")
            else:
                # 添加新变量
                print("正在添加新变量...")
                response = requests.post(f'{host}/open/envs', headers=headers, json=[env_data], timeout=10)
                if response.status_code != 200:
                    print(f"添加环境变量失败: {response.text}")
                    return False
                    
                # 获取新添加变量的ID并启用
                result = response.json()
                print(f"添加变量响应: {result}")
                if result.get('code') == 200:
                    new_id = None
                    if result.get('data') and len(result['data']) > 0:
                        new_id = result['data'][0].get('_id') or result['data'][0].get('id')
                    if new_id:
                        try:
                            requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id], timeout=10)
                            print("新变量已启用")
                        except Exception as e:
                            print(f"启用变量异常: {str(e)}")
                else:
                    print(f"添加变量失败，响应码: {result.get('code')}")
                    return False
            
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
        env_name = middleware.bucketGet('s_xjb_config', 'xjb_osname') or 'S_XJB'
        
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
                if not env:  # 跳过None或空值
                    continue
                # 精确匹配：变量名必须一致，并且备注中必须包含该手机号
                env_remarks = env.get('remarks', '') or ''  # 确保不为None
                env_name_val = env.get('name', '') or ''    # 确保不为None
                if env_name_val == env_name and f"新江北:{phone}" in env_remarks:
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

def manage_account():
    """账号管理功能"""
    if not uservalue:
        sender.reply(format_message("未绑定账号", [
            "❌ 未找到任何账号信息",
            f"💡 发送 新江北登录 绑定"
        ]))
        return
        
    accounts = eval(uservalue)
    
    # 先显示管理功能菜单
    menu_lines = [
        "[1] 授权账号",
        "[2] 删除账号",
        "[3] 提交青龙",
        "[4] 更新支付宝信息",
        "[5] 更新SessionID",
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
        account_info_str = middleware.bucketGet('s_xjb_token', account)
        if not account_info_str:
            continue
            
        auth_time = middleware.bucketGet('s_xjb_auth', account)
        
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
                        middleware.bucketDel('s_xjb_token', account)
                        middleware.bucketDel('s_xjb_auth', account)
                            
                        # 删除青龙变量
                        delete_ql_env(account)
                        success_count += 1
                    except Exception as e:
                        print(f"删除账号失败: {account}, 错误: {str(e)}")
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet('s_xjb_user', userid, str(accounts))
                else:
                    middleware.bucketDel('s_xjb_user', userid)
                    
                sender.reply(f"✅ 已成功删除 {success_count}/{len(selected_accounts)} 个账号")
            else:
                sender.reply("✅ 已取消删除")
                
        elif choice == '3':
            # 提交选中账号到青龙
            success_count = 0
            for account in selected_accounts:
                try:
                    account_info_str = middleware.bucketGet('s_xjb_token', account)
                    if not account_info_str:
                        continue
                        
                    account_info = json.loads(account_info_str)
                    
                    # 如果已授权则更新青龙变量
                    auth_time = middleware.bucketGet('s_xjb_auth', account)
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
        elif choice == '4':
            # 更新支付宝信息
            update_alipay_info(selected_accounts)
        elif choice == '5':
            # 更新SessionID
            update_session_id(selected_accounts)
        else:
            sender.reply("❌ 无效的选择")
            
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")

def show_tutorial():
    """显示新江北教程"""
    tutorial_url = middleware.bucketGet('s_xjb_config', 'tutorial_url') or 'https://example.com/tutorial'
    
    tutorial = f"""
=====新江北使用教程=====
🔍 基础功能:
1. 新江北登录 - 绑定账号
2. 新江北查询 - 查看账号信息
3. 新江北管理 - 管理绑定账号
==================
⚠️ 注意事项:
• 账号失效请及时更新
• 请勿泄露账号信息
==================
💡 登录方式:
• 账号密码登录 - 使用手机号和密码登录
==================
❓ 遇到问题请联系管理员
=================="""
    sender.reply(tutorial)

# 码支付API类
class MaPay_Api:
    def __init__(self, config):
        """初始化码支付API类"""
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
        """创建支付订单 (mapi接口)"""
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
        """查询订单状态"""
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

# 支付回调处理器
class PaymentCallbackHandler(BaseHTTPRequestHandler):
    """支付回调处理器"""
    def do_GET(self):
        try:
            # 解析URL路径，忽略查询参数，获取订单号
            parsed_url = urlparse(self.path)
            path = parsed_url.path.strip('/')
            order_no = path
            
            # 标记支付完成
            payment_status[order_no] = {'paid': True, 'time': time.time()}
            
            # 返回成功响应
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Payment received')
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f'Error: {str(e)}'.encode())
    
    def log_message(self, format, *args):
        # 禁用日志输出
        pass

def start_payment_server(order_no, callback_url, port):
    """启动支付回调服务器"""
    try:
        # 将端口转换为整数
        port = int(port)
        
        # 创建HTTP服务器
        server = HTTPServer(('0.0.0.0', port), PaymentCallbackHandler)
        
        # 在新线程中启动服务器
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        # 回调地址还是使用callback_url/订单号的格式
        return server, f"{callback_url.rstrip('/')}/{order_no}"
        
    except Exception as e:
        return None, f"启动服务器失败: {str(e)}"

def poll_mapi_payment_status(order_no, max_tries=30):
    """通过临时接口检测支付状态
    
    Args:
        order_no: 订单号(商户订单号)
        max_tries: 最大尝试次数（每次等待5秒）
        
    Returns:
        (is_paid, msg, data): 是否支付成功、消息和数据
    """
    # 从卡密积分系统获取回调URL和端口配置
    callback_url = middleware.bucketGet('dd_sign_config', 'callback_url')
    callback_port = middleware.bucketGet('dd_sign_config', 'callback_port') or '8080'
    
    if not callback_url:
        # 如果没有配置回调URL，返回错误
        return False, "未配置回调URL，请在卡密积分系统中设置callback_url参数", None
    
    # 启动临时支付服务器
    server, full_callback_url = start_payment_server(order_no, callback_url, callback_port)
    
    if not server:
        sender.reply(f"❌ {full_callback_url}")
        return False, "服务器启动失败", None
    
    try:
        # 等待支付完成
        for i in range(max_tries):
            # 检查是否收到支付回调
            if order_no in payment_status and payment_status[order_no]['paid']:
                # 清理支付状态
                del payment_status[order_no]
                return True, "支付成功", {'status': 1}
            
            # 等待用户输入或超时
            result = sender.listen(5000)  # 等待5秒
            if result == 'q':
                return False, "用户取消", None
        
        return False, "等待超时，如已支付请联系管理员", None
        
    finally:
        # 关闭服务器
        try:
            server.shutdown()
            server.server_close()
        except:
            pass

def generate_qrcode(url):
    """生成二维码图片
    
    Args:
        url: 要生成二维码的URL
        
    Returns:
        str: 二维码API的URL
    """
    try:
        # 使用 qrtool.cn 的API生成二维码
        encoded_url = quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        # 生成失败时返回原始URL
        return None

def poll_mapi_payment_status(order_no, max_tries=30):
    """通过临时接口检测支付状态
    
    Args:
        order_no: 订单号(商户订单号)
        max_tries: 最大尝试次数（每次等待5秒）
        
    Returns:
        (is_paid, msg, data): 是否支付成功、消息和数据
    """
    # 从卡密积分系统获取回调URL和端口配置
    callback_url = middleware.bucketGet('dd_sign_config', 'callback_url')
    callback_port = middleware.bucketGet('dd_sign_config', 'callback_port') or '8080'
    
    if not callback_url:
        # 如果没有配置回调URL，返回错误
        return False, "未配置回调URL，请在卡密积分系统中设置callback_url参数", None
    
    # 启动临时支付服务器
    server, full_callback_url = start_payment_server(order_no, callback_url, callback_port)
    
    if not server:
        sender.reply(f"❌ {full_callback_url}")
        return False, "服务器启动失败", None
    
    try:
        # 等待支付完成
        for i in range(max_tries):
            # 检查是否收到支付回调
            if order_no in payment_status and payment_status[order_no]['paid']:
                # 清理支付状态
                del payment_status[order_no]
                return True, "支付成功", {'status': 1}
            
            # 等待用户输入或超时
            result = sender.listen(5000)  # 等待5秒
            if result == 'q':
                return False, "用户取消", None
        
        return False, "等待超时，如已支付请联系管理员", None
        
    finally:
        # 关闭服务器
        try:
            server.shutdown()
            server.server_close()
        except:
            pass

def authorize_account(phone, account_info):
    """单个账号授权"""
    # 获取配置信息
    (_, _, _, _, _, xjbVipmoney, xjbcoin) = get_user_content()
    
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
        money = months * xjbVipmoney
        
        # 构建可用的支付方式列表
        available_payments = []
        
        # 检查是否启用码支付
        ma_pay_switch = middleware.bucketGet('s_xjb_config', 'ma_pay_switch') or 'false'
        
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
            zsm = middleware.bucketGet('s_xjb_config', 'zsm')
            if zsm:
                available_payments.append(("微信支付", "wxpay"))
        
        # 积分兑换（检查是否开启了积分功能）
        if xjbcoin and int(xjbcoin) > 0:
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
            if pay_order(project='新江北授权', months=months, money=money):
                process_authorization(phone, account_info, months)
        
        elif payment_type.startswith("mapay_"):
            # 码支付处理
            # 提取实际支付方式（去掉"mapay_"前缀）
            actual_pay_type = payment_type[6:]
            
            # 处理支付
            result = handle_mapay_order(project='新江北授权', months=months, money=money, pay_type=actual_pay_type)
            
            # 处理授权
            if result:
                process_authorization(phone, account_info, months)
                
        elif payment_type == "coin":
            # 积分兑换处理
            process_coin_exchange(phone, account_info, months, xjbcoin)
            
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
        return

def authorize_multiple_accounts(accounts):
    """批量授权账号"""
    # 获取配置信息
    (_, _, _, _, _, xjbVipmoney, xjbcoin) = get_user_content()
    
    account_infos = []
    # 获取账号信息
    for phone in accounts:
        try:
            account_info_str = middleware.bucketGet('s_xjb_token', phone)
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
        total_money = len(account_infos) * months * xjbVipmoney
    
        # 构建可用的支付方式列表
        available_payments = []
        
        # 检查是否启用码支付
        ma_pay_switch = middleware.bucketGet('s_xjb_config', 'ma_pay_switch') or 'false'
        
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
            zsm = middleware.bucketGet('s_xjb_config', 'zsm')
            if zsm:
                available_payments.append(("微信支付", "wxpay"))
        
        # 积分兑换（检查是否开启了积分功能）
        if xjbcoin and int(xjbcoin) > 0:
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
            if pay_order(project=f'新江北授权(共{len(account_infos)}个账号)', months=months, money=total_money):
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
                project=f'新江北授权(共{len(account_infos)}个账号)', 
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
            if not xjbcoin or int(xjbcoin) <= 0:
                sender.reply("""
=====兑换失败=====
❌ 未配置积分价格
------------------
请联系管理员配置积分兑换功能
==================""")
                return
                
            # 计算需要的积分总数
            total_coins = int(xjbcoin) * months * len(account_infos)
            
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

def process_authorization(phone, account_info, months):
    """处理账号授权"""
    try:
        print(f"开始处理授权: {phone}")
        
        # 获取当前授权状态
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_xjb_auth', phone)
        
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
        
        print(f"计算到期时间: {new_expire_str}")
        
        # 更新授权时间
        middleware.bucketSet('s_xjb_auth', phone, new_expire_str)
        print(f"授权时间已更新: {phone} -> {new_expire_str}")
        
        # 更新青龙变量
        print(f"开始更新青龙变量: {phone}")
        ql_result = update_ql_env(phone, account_info)
        print(f"青龙更新结果: {phone} -> {'成功' if ql_result else '失败'}")
        
        # 显示授权结果
        auth_result = f"""
=====授权成功=====
📱 手机号: {mask_phone(phone)}
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

def process_coin_exchange(phone, account_info, months, xjbcoin):
    """处理积分兑换"""
    try:
        # 验证积分兑换配置
        if not xjbcoin or int(xjbcoin) <= 0:
            sender.reply(f"""
=====兑换失败=====
❌ 未配置积分价格
------------------
请联系管理员配置积分兑换功能
==================""")
            return False
            
        # 计算所需积分
        required_coins = months * int(xjbcoin)
        
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
    ma_pay_switch = middleware.bucketGet('s_xjb_config', 'ma_pay_switch') or 'false'
    if ma_pay_switch.lower() == 'true':
        return handle_mapay_order(project, months, money)
        
    # 使用赞赏码支付
    zsm = middleware.bucketGet('s_xjb_config', 'zsm')
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
    """处理码支付订单"""
    # 检查是否启用码支付
    ma_pay_switch = middleware.bucketGet('s_xjb_config', 'ma_pay_switch') or 'false'
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
        out_trade_no = f"XJB{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        
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
        
        # 更新支付配置中的回调URL - 使用卡密积分系统的回调URL/订单号格式
        callback_url = middleware.bucketGet('dd_sign_config', 'callback_url')
        if callback_url:
            PAYMENT_CONFIG['notify_url'] = f"{callback_url.rstrip('/')}/{out_trade_no}"
            PAYMENT_CONFIG['return_url'] = f"http://baidu.com"
        
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
        pay_url_fh = None  # 初始化变量
        if result.get('payurl'):
            encoded_url = requests.utils.quote(result.get('payurl'))
            headers = {
                'sec-ch-ua-platform': 'Windows',
                'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'sec-ch-ua-mobile': '?0',
                'Origin': 'https://www.mrw.so',
                'Sec-Fetch-Site': 'same-site',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': 'https://www.mrw.so/',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
            }
            data = {
                'urlStr': encoded_url,
                'domain': 'mrw.so',
                'expireType': '1',
                'key': '5d7798c491d2c423c8c33d2d@631d0a6ffd3fbca7c2728bebc6602f98',
                'random': str(int(time.time() * 1000))
            }
            try:
                response = requests.post('https://create.mrw.so/pageHome/createBySingle.htm', headers=headers, data=data)
                pay_url_fh = response.json().get('data')
            except Exception as e:
                print(f"获取短链接失败: {str(e)}")
                pay_url_fh = None
        qrcode = result.get('qrcode') or pay_url_fh
        payurl = result.get('payurl')
        code_url = result.get('code_url')
        trade_no = result.get('trade_no')
        
        # 根据返回数据类型构建支付链接

        # 如果qrcode包含图片格式,拼接支付网关
        if qrcode and ('.jpeg' in qrcode or '.jpg' in qrcode or '.png' in qrcode) and not qrcode.startswith('http'):
            code_url = qrcode
            qrcode = None
        if payurl:
            pay_url = payurl
        elif qrcode:
            pay_url = qrcode
        elif code_url:
            # 如果有二维码图片地址，构建完整URL
            if code_url and not code_url.startswith('http'):
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
        
        # 使用回调方式检测支付结果
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

def xjb_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return
        
    auth_menu = f"""
=====新江北授权管理=====
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
        auth_phones = middleware.bucketAllKeys('s_xjb_auth')
        if not auth_phones:
            sender.reply("""
=====提交失败=====
❌ 未找到任何已授权的新江北账号
==================""")
            return
            
        success_count = 0
        fail_count = 0
        
        for phone in auth_phones:
            try:
                # 获取账号授权状态
                auth_date = middleware.bucketGet('s_xjb_auth', phone)
                
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
                token_data = middleware.bucketGet('s_xjb_token', phone)
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
        users = middleware.bucketAllKeys('s_xjb_user')
        if not users:
            sender.reply("""
=====授权失败=====
❌ 未找到任何绑定的新江北账号
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
                accountlist = middleware.bucketGet('s_xjb_user', user)
                if accountlist == '' or accountlist == '{}':
                    continue
                    
                accounts = eval(accountlist)
                for account in accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('s_xjb_auth', account)
                        token_data = middleware.bucketGet('s_xjb_token', account)
                        
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
                        middleware.bucketSet('s_xjb_auth', account, new_sqsj)
                        
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
            
        accountlist = middleware.bucketGet('s_xjb_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"❌ 未找到 {myuid} 的新江北账号信息!")
            return
            
        accounts = eval(accountlist)
        account_list = """
========选择账号=======
[0] 全部账号"""
        
        for i, account in enumerate(accounts, 1):
            accountVip = middleware.bucketGet('s_xjb_auth', account)
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
                        accountVip = middleware.bucketGet('s_xjb_auth', account)
                        token_data = middleware.bucketGet('s_xjb_token', account)
                        
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
                        middleware.bucketSet('s_xjb_auth', account, new_sqsj)
                        
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
                accountVip = middleware.bucketGet('s_xjb_auth', account)
                token_data = middleware.bucketGet('s_xjb_token', account)
                
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
                middleware.bucketSet('s_xjb_auth', account, new_sqsj)
                
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

def update_alipay_info(accounts):
    """更新账号支付宝信息"""
    success_count = 0
    
    for phone in accounts:
        try:
            # 获取账号信息
            account_info_str = middleware.bucketGet('s_xjb_token', phone)
            if not account_info_str:
                sender.reply(f"❌ 账号 {mask_phone(phone)} 信息不存在")
                continue
                
            account_info = json.loads(account_info_str)
            
            # 检查是否已有支付宝信息
            has_alipay_name = account_info.get('alipay_name', '')
            has_alipay_account = account_info.get('alipay_account', '')
            
            # 支付宝姓名输入
            alipay_name_guide_lines = [
                f"📱 手机号: {mask_phone(phone)}",
                "------------------",
                "请输入新的支付宝姓名",
                "💡 提示: 填写支付宝实名姓名",
                "回复\"s\"跳过此账号",
                "回复\"q\"退出操作"
            ]
            sender.reply(format_message("更新支付宝姓名", alipay_name_guide_lines))
            
            alipay_name = sender.input(120000, 1, False)
            if not alipay_name or alipay_name.lower() == 'q':
                sender.reply("✅ 已退出更新")
                return
            elif alipay_name.lower() == 's':
                continue
                
            # 支付宝账号输入
            alipay_account_guide_lines = [
                f"📱 手机号: {mask_phone(phone)}",
                f"💳 当前支付宝账号: {has_alipay_account or '未设置'}",
                "------------------",
                "请输入新的支付宝账号",
                "💡 提示: 可以是手机号或邮箱",
                "回复\"s\"跳过此账号",
                "回复\"q\"退出操作"
            ]
            sender.reply(format_message("更新支付宝账号", alipay_account_guide_lines))
            
            alipay_account = sender.input(120000, 1, False)
            if not alipay_account or alipay_account.lower() == 'q':
                sender.reply("✅ 已退出更新")
                return
            elif alipay_account.lower() == 's':
                continue
                
            # 更新账号信息
            account_info['alipay_name'] = alipay_name
            account_info['alipay_account'] = alipay_account
            
            # 保存更新后的账号信息
            middleware.bucketSet('s_xjb_token', phone, json.dumps(account_info))
            
            # 如果账号已授权，同时更新青龙变量
            auth_time = middleware.bucketGet('s_xjb_auth', phone)
            if auth_time and auth_time >= str(datetime.now().date()):
                update_ql_env(phone, account_info)
                sender.reply(f"""
=====更新成功=====
📱 手机号: {mask_phone(phone)}
💳 支付宝账号: {alipay_account}
🔄 已同步到青龙
==================""")
            else:
                sender.reply(f"""
=====更新成功=====
📱 手机号: {mask_phone(phone)}
💳 支付宝账号: {alipay_account}
==================""")
                
            success_count += 1
            
        except Exception as e:
            sender.reply(f"❌ 更新账号 {mask_phone(phone)} 失败: {str(e)}")
            
    if success_count > 0:
        sender.reply(f"✅ 已成功更新 {success_count} 个账号的支付宝信息")

def update_session_id(accounts):
    """更新SessionID"""
    success_count = 0
    
    for phone in accounts:
        try:
            # 获取账号信息
            account_info_str = middleware.bucketGet('s_xjb_token', phone)
            if not account_info_str:
                sender.reply(f"❌ 账号 {mask_phone(phone)} 信息不存在")
                continue
                
            account_info = json.loads(account_info_str)
            
            # 检查是否已有SessionID
            has_session_id = account_info.get('session_id', '')
            
            # SessionID输入
            session_id_guide_lines = [
                f"📱 手机号: {mask_phone(phone)}",
                f"🔑 当前SessionID: {has_session_id[:20] + '...' if has_session_id and len(has_session_id) > 20 else has_session_id or '未设置'}",
                "------------------",
                "请输入新的SessionID",
                "💡 提示: 留空则清除SessionID",
                "回复\"s\"跳过此账号",
                "回复\"q\"退出操作"
            ]
            sender.reply(format_message("更新SessionID", session_id_guide_lines))
            
            new_session_id = sender.input(120000, 1, False)
            if not new_session_id:
                new_session_id = ""  # 处理None情况
            
            if new_session_id.lower() == 'q':
                sender.reply("✅ 已退出更新")
                return
            elif new_session_id.lower() == 's':
                continue
            elif new_session_id == '':
                account_info['session_id'] = ''
                display_session_id = "已清除"
            else:
                account_info['session_id'] = new_session_id.strip()
                display_session_id = f"{new_session_id.strip()[:20]}..." if len(new_session_id.strip()) > 20 else new_session_id.strip()
            
            # 保存更新后的账号信息
            middleware.bucketSet('s_xjb_token', phone, json.dumps(account_info))
            
            # 如果账号已授权，同时更新青龙变量
            auth_time = middleware.bucketGet('s_xjb_auth', phone)
            if auth_time and auth_time >= str(datetime.now().date()):
                update_ql_env(phone, account_info)
                sender.reply(f"""
=====更新成功=====
📱 手机号: {mask_phone(phone)}
🔑 SessionID: {display_session_id}
🔄 已同步到青龙
==================""")
            else:
                sender.reply(f"""
=====更新成功=====
📱 手机号: {mask_phone(phone)}
🔑 SessionID: {display_session_id}
==================""")
                
            success_count += 1
            
        except Exception as e:
            sender.reply(f"❌ 更新账号 {mask_phone(phone)} 失败: {str(e)}")
            
    if success_count > 0:
        sender.reply(f"✅ 已成功更新 {success_count} 个账号的SessionID")

def get_red_packet_details(user_info):
    """获取红包明细"""
    try:
        # 从user_info中获取sessionId和accountId
        session_id = user_info.get('session_id', '')
        account_id = user_info.get('account_id', '')
        
        if not session_id or not account_id:
            return {"success": False, "message": "缺少sessionId或accountId"}
        
        # 步骤1: 获取自动登录链接
        auto_login_url = "https://92261.activity-42.m.duiba.com.cn/customActivity/zjtm/autoLogin"
        auto_login_params = {
            "_": str(int(time.time() * 1000)),
            "sessionId": session_id,
            "accountId": account_id,
            "redirectUrl": "https%3A%2F%2F92261.activity-14.m.duiba.com.cn%2Fhdtool%2Findex%3Fid%3D299402208083641%26dbnewopen"
        }
        
        auto_login_headers = {
            "host": "92261.activity-42.m.duiba.com.cn",
            "sec-ch-ua-platform": "Android",
            "user-agent": "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.260 Mobile Safari/537.36;xsb_xinjiangbei;xsb_xinjiangbei;1.7.0;native_app;6.9.0",
            "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "accept": "*/*",
            "x-requested-with": "io.pailian.jiangbei",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://92261.activity-42.m.duiba.com.cn/customShare/share?id=6600&dbredirect=https%3A%2F%2F92261.activity-14.m.duiba.com.cn%2Fhdtool%2Findex%3Fid%3D299402208083641%26dbnewopen&gaze_control=01&isNeedLogin=true",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # 获取自动登录链接
        try:
            auto_login_response = requests.get(auto_login_url, params=auto_login_params, headers=auto_login_headers, timeout=10)
            if auto_login_response.status_code != 200:
                return {"success": False, "message": f"获取自动登录链接失败，状态码: {auto_login_response.status_code}"}
            
            auto_login_result = auto_login_response.json()
            if not auto_login_result.get('success'):
                return {"success": False, "message": "获取自动登录链接失败"}
            
            login_data_url = auto_login_result.get('data', '')
            if not login_data_url:
                return {"success": False, "message": "自动登录链接为空"}
            
            # 如果URL以//开头，添加https:协议
            if login_data_url.startswith('//'):
                login_data_url = 'https:' + login_data_url
                
        except Exception as e:
            return {"success": False, "message": f"获取自动登录链接异常: {str(e)}"}
        
        # 步骤2: 访问自动登录链接获取cookies
        try:
            login_headers = {
                "user-agent": "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.260 Mobile Safari/537.36;xsb_xinjiangbei;xsb_xinjiangbei;1.7.0;native_app;6.9.0",
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-encoding": "gzip, deflate, br, zstd",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
            }
            
            # 访问自动登录链接，不跟随重定向，获取set-cookie
            login_response = requests.get(login_data_url, headers=login_headers, allow_redirects=False, timeout=10)
            
            # 从响应头中提取cookies
            cookies = {}
            if 'Set-Cookie' in login_response.headers:
                set_cookie_header = login_response.headers['Set-Cookie']
                # 解析Set-Cookie头
                for cookie_part in set_cookie_header.split(','):
                    if '=' in cookie_part:
                        key_value = cookie_part.split(';')[0].strip()
                        if '=' in key_value:
                            key, value = key_value.split('=', 1)
                            cookies[key.strip()] = value.strip()
            
            # 如果没有获取到足够的cookies，使用默认值
            if not cookies:
                cookies = {
                    "_ac": "eyJhaWQiOjkyMjYxLCJjaWQiOjQyODQxMDIzNDZ9",
                    "w_ts": str(int(time.time() * 1000))
                }
                
        except Exception as e:
            return {"success": False, "message": f"获取cookies异常: {str(e)}"}
        
        # 步骤3: 使用获取到的cookies查询红包明细
        record_url = "https://92261.activity-14.m.duiba.com.cn/crecord/getrecord"
        record_params = {
            "page": "1",
            "_": str(int(time.time() * 1000))
        }
        
        record_headers = {
            "host": "92261.activity-14.m.duiba.com.cn",
            "sec-ch-ua-platform": "Android",
            "x-requested-with": "XMLHttpRequest",
            "user-agent": "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.260 Mobile Safari/537.36;xsb_xinjiangbei;xsb_xinjiangbei;1.7.0;native_app;6.9.0",
            "accept": "application/json",
            "sec-ch-ua": '"Android WebView";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?1",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://92261.activity-14.m.duiba.com.cn/crecord/record?dbnewopen&dpm=92261.3.2.0",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # 发送红包明细查询请求
        try:
            response = requests.get(record_url, params=record_params, headers=record_headers, cookies=cookies, timeout=10)
            if response.status_code != 200:
                return {"success": False, "message": f"查询红包明细失败，状态码: {response.status_code}"}
            
            result = response.json()
            if not result.get('success'):
                return {"success": False, "message": "获取红包明细失败"}
            
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "message": f"查询红包明细异常: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"获取红包明细失败: {str(e)}"}
        
def format_red_packet_details(records):
    """格式化红包明细信息"""
    if not records:
        return ["🧧 暂无红包明细"]
    
    details = ["🧧 近期红包明细:"]
    
    # 计算总金额和成功数量
    total_amount = 0
    success_count = 0
    
    # 遍历记录，最多显示10条
    for record in records[:10]:
        title = record.get('title', '未知红包')
        # 提取金额，如果是"支付宝充值0.18元"形式
        amount = '0.00'
        if '充值' in title and '元' in title:
            try:
                amount = title.split('元')[0].split('充值')[-1]
            except:
                pass
        # 如果只有"0.28元"形式
        elif '元' in title:
            try:
                amount = title.split('元')[0]
            except:
                pass
                
        # 判断状态和选择emoji
        is_success = False
        status_text = record.get('statusText', '')
        if '成功' in status_text:
            emoji = "🧧"
            is_success = True
        else:
            emoji = "❌"
            
        # 格式化日期 (只显示月-日)
        create_time = record.get('gmtCreate', '')
        
        # 添加到详情列表 - 格式: emoji 金额 日期
        details.append(f"{emoji} {amount}元 {create_time}")
        
        # 累计成功提现的金额
        if is_success:
            try:
                total_amount += float(amount)
                success_count += 1
            except:
                pass
    
    # 添加统计信息
    details.append("-------------------")
    details.append(f"✅ 成功提现: {success_count}笔")
    details.append(f"💰 累计金额: {total_amount:.2f}元")
    
    return details

def check_xjb_auth_status():
    """检测所有账号的授权状态并通知用户"""
    try:
        # 获取通知渠道配置
        notify_channels = middleware.bucketGet('s_xjb_config', 'notify') or ''
        if not notify_channels:
            return "❌ 未配置通知渠道，请在插件配置中设置notify参数"
            
        # 解析通知渠道
        channels = [channel.strip() for channel in notify_channels.split(',') if channel.strip()]
        if not channels:
            return "❌ 通知渠道配置格式错误"
            
        # 获取所有用户ID
        all_users = middleware.bucketAllKeys('s_xjb_user')
        if not all_users:
            return "❌ 没有找到任何用户绑定的账号"
            
        # 当前日期
        current_date = str(datetime.now().date())
        
        # 统计信息
        total_checked = 0
        total_notified = 0
        
        # 遍历所有用户
        for user_id in all_users:
            # 获取用户绑定的账号
            try:
                accounts = eval(middleware.bucketGet('s_xjb_user', user_id) or '[]')
                if not accounts:
                    continue
            except:
                continue
                
            # 检查每个账号的状态
            expired_accounts = []  # 授权过期账号
            
            for account in accounts:
                total_checked += 1
                
                # 检查授权状态
                auth_time = middleware.bucketGet('s_xjb_auth', account)
                if not auth_time or auth_time <= current_date:
                    expired_accounts.append({
                        'phone': account,
                        'auth_time': auth_time or '未授权'
                    })
                    
            # 如果有过期账号，发送通知
            if expired_accounts:
                # 构建通知消息
                notify_msg = "=====新江北账号检测报告====="
                notify_msg += "\n\n🚨 授权过期账号:"
                notify_msg += "\n" + "-" * 25
                for acc in expired_accounts:
                    phone_masked = acc['phone'][:3] + '****' + acc['phone'][-4:] if len(acc['phone']) >= 7 else acc['phone']
                    notify_msg += f"\n📱 {phone_masked} (到期:{acc['auth_time']})"
                
                notify_msg += "\n" + "-" * 20
                notify_msg += "\n💡 发送\"新江北管理\"进行续费"
                notify_msg += "\n" + "=" * 14
                
                # 向所有配置的渠道推送通知
                for channel in channels:
                    try:
                        middleware.push(
                            imType=channel,
                            groupCode='',
                            userID=user_id,
                            title="",
                            content=notify_msg
                        )
                        total_notified += 1
                    except Exception as e:
                        # 推送失败不影响其他渠道推送
                        print(f"推送通知失败: {channel}, 用户: {user_id}, 错误: {str(e)}")
                        continue
                
        return f"✅ 检测完成，共检测 {total_checked} 个账号，发送 {total_notified} 条通知"
        
    except Exception as e:
        return f"❌ 检测失败: {str(e)}"

def clean_xjb_expired():
    """清理过期账号函数"""
    try:
        # 清理过期账号
        expired_count = 0
        token_deleted_count = 0
        dqsj = datetime.now().strftime("%Y-%m-%d")
        
        sender.reply("🧹 开始清理过期账号...")
        
        # 收集所有过期账号
        expired_accounts = []
        for username in middleware.bucketAllKeys('xjb_auth'):
            auth_time = middleware.bucketGet('xjb_auth', username)
            if auth_time and auth_time < dqsj:
                expired_accounts.append(username)
                
        if not expired_accounts:
            sender.reply("✅ 没有找到过期账号")
            return
            
        sender.reply(f"🔍 找到 {len(expired_accounts)} 个过期账号，开始清理...")
        
        # 清理每个过期账号
        for username in expired_accounts:
            try:
                # 1. 删除青龙变量
                delete_ql_env(username)
                     
                # 2. 删除账号token信息
                middleware.bucketDel('xjb_token', username)
                token_deleted_count += 1
                
                # 3. 删除支付宝信息
                middleware.bucketDel('xjb_alipay', username)
                
                # 4. 删除SessionID信息
                middleware.bucketDel('xjb_sessionid', username)
                
                # 5. 从用户账号列表中移除
                # 找到拥有此账号的用户
                for user_id in middleware.bucketAllKeys('xjb_user'):
                    user_accounts = middleware.bucketGet('xjb_user', user_id)
                    if user_accounts:
                        try:
                            accounts_list = eval(user_accounts)
                            if username in accounts_list:
                                accounts_list.remove(username)
                                if accounts_list:
                                    # 如果用户还有其他账号，更新列表
                                    middleware.bucketSet('xjb_user', user_id, str(accounts_list))
                                else:
                                    # 如果用户没有其他账号，删除用户记录
                                    middleware.bucketDel('xjb_user', user_id)
                                break
                        except:
                            continue
                
                # 6. 删除授权记录
                middleware.bucketDel('xjb_auth', username)
                expired_count += 1
                
            except Exception as e:
                print(f"清理账号异常: {username}, 错误: {str(e)}")
                continue
                
        # 显示清理结果
        result_msg = f"""
=====清理完成=====
📊 过期账号: {len(expired_accounts)}个
🗃️ 账号信息: 清理{token_deleted_count}个
🗃️ 青龙变量: 已清理
=================="""
        sender.reply(result_msg)
        
    except Exception as e:
        sender.reply(f"""
=====清理异常=====
❌ 错误: {str(e)}
==================""")

def main():
    global randommanagecommand, randomquerycommand
    global randomsigncommand, xjbVipmoney, xjbcoin
    
    # 获取必要的配置
    (_, _, randommanagecommand, randomquerycommand,
     randomsigncommand, xjbVipmoney, xjbcoin) = get_user_content()
    
    imtype = sender.getImtype()
    usermessage = sender.getMessage()
    
    if '登录' in usermessage or '登陆' in usermessage:
        bind_account()
    elif '管理' in usermessage:
        manage_account()
    elif '查询' in usermessage:
        query_accounts()
    elif '新江北教程' in usermessage:
        show_tutorial()
    elif '新江北授权' in usermessage:
        xjb_auth()
    elif '新江北检测' in usermessage:
        if not sender.isAdmin():
            sender.reply("❌ 此功能仅限管理员使用")
            return
        
        sender.reply("🔍 正在检测所有账号状态...")
        result = check_xjb_auth_status()
        sender.reply(result)
    elif '新江北清理' in usermessage:
        if not sender.isAdmin():
            sender.reply("❌ 此功能仅限管理员使用")
            return
            
        clean_xjb_expired()
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
