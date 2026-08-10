#[title: 雪乃改密]
#[language: python]
#[class: 工具类]
#[service: 2993959969] 售后联系方式
#[author: rujingxianghai] 作者
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^(雪乃)(改密|改密码|修改密码)$|^(西施眼|望潮|新江北|桐庐|ZSWY|SHPJ|越城|大潮|融磐安|蓝精灵|爱海盐|青椒|荆州)(改密|改密码|修改密码)$|^雪乃管理$|^雪乃教程$|^雪乃配置$]
#[cron: 0 0 0 0 0] cron定时，支持5位域和6位域
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: https://img-cf.885666.xyz/92097575b33522261453fe1426366af5.jpg]图标链接地址，请使用48像素的正方形图标，支持http和https
#[version: 1.0.1]版本号
#[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
#[price: 88.88] 上架价格
# [description: 【白名单专属】基于雪之下雪乃JS代码改编的Python改密插件，支持13个项目的密码修改<br>指令：改密、改密配置、改密管理、改密教程<br>支持自动图片验证码识别<br>v1.0.0：初始版本发布]

import os
import json
import time
import uuid
import random
import string
import requests
import hashlib
import hmac
import base64
import re
from urllib.parse import quote
from datetime import datetime, timedelta
import middleware
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_changepass_user', key=userid)

# [param: {"required":true,"key":"s_changepass_config.ocr_server","bool":false,"placeholder":"https://ddddocr.xzxxn7.live","name":"OCR识别服务器","desc":"图片验证码自动识别服务器地址"}]
# [param: {"required":false,"key":"s_changepass_config.timeout","bool":false,"placeholder":"30","name":"请求超时时间","desc":"API请求超时时间(秒)，默认30秒"}]
# [param: {"required":false,"key":"s_changepass_config.debug_mode","bool":true,"placeholder":"","name":"调试模式","desc":"开启后显示详细的调试信息"}]
# [param: {"required":false,"key":"s_changepass_config.auto_retry","bool":true,"placeholder":"","name":"自动重试","desc":"失败时是否自动重试"}]
# [param: {"required":false,"key":"s_changepass_config.proxy","bool":false,"placeholder":"http://api.example.com/proxy 或 127.0.0.1:8080","name":"代理设置","desc":"http开头为API模式获取代理，否则为固定代理池模式"}]

# 项目配置映射 - 基于原JS代码
PROJECT_CONFIG = {
    "1": {"name": "西施眼", "code": "XiShiYan", "k": "34", "p": "50"},
    "2": {"name": "望潮", "code": "WangChao", "k": "64", "p": "10019"},
    "3": {"name": "新江北", "code": "XinJiangBei", "k": "102", "p": "10050"},
    "4": {"name": "桐庐", "code": "TongLu", "k": "59", "p": "10017"},
    "5": {"name": "ZSWY", "code": "ZSWY", "k": "73", "p": "10024"},
    "6": {"name": "SHPJ", "code": "SHPJ", "k": "14", "p": "12"},
    "7": {"name": "越城", "code": "YueCheng", "k": "31", "p": "48"},
    "8": {"name": "大潮", "code": "DaChao", "k": "94", "p": "10048"},
    "9": {"name": "融磐安", "code": "RongPanAn", "k": "30", "p": "45"},
    "10": {"name": "蓝精灵", "code": "LanJingLing", "k": "72", "p": "10026"},
    "11": {"name": "爱海盐", "code": "AiHaiYan", "k": "60", "p": "10018"},
    "12": {"name": "青椒", "code": "QingJiao", "k": "23", "p": "34"},
    "13": {"name": "荆州", "code": "JingZhou", "k": "92", "p": "10046"}
}

# RSA公钥 - 来自原JS代码
RSA_PUBLIC_KEY = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB"""

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 's_changepass_config',
    'user_bucket': 's_changepass_user',
    'name': '雪乃改密'
}

def get_config(key, default=''):
    """获取配置项"""
    return middleware.bucketGet(PLUGIN_CONFIG['bucket'], key) or default

def set_config(key, value):
    """设置配置项"""
    middleware.bucketSet(PLUGIN_CONFIG['bucket'], key, str(value))

def log_debug(message):
    """调试日志"""
    if get_config('debug_mode', 'false').lower() == 'true':
        sender.reply(f"[DEBUG] {message}")

def format_message(title, content_lines):
    """格式化消息"""
    message = f"✨ {title} ✨\n"
    message += "─" * 20 + "\n"
    for line in content_lines:
        message += f"{line}\n"
    message += "─" * 20
    return message

def show_error(title, error_msg, extra_info=None):
    """显示错误信息"""
    error_lines = [f"❌ {error_msg}"]
    if extra_info:
        error_lines.extend(extra_info)
    return format_message(title, error_lines)

def generate_uuid():
    """生成UUID"""
    return str(uuid.uuid4())

def generate_ua(project_p):
    """生成用户代理 - 基于JS代码的UA生成逻辑"""
    version = "6.0.2"
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
    os_name = "Android"
    
    ua = f"{os_name.upper()};11;{project_p};{version};1.0;null;{device}"
    common_ua = f"{version};{device_uuid};{device_name};{os_name};11;Release;6.10.0"
    
    log_debug(f"生成UA: {ua}")
    return ua, common_ua

def get_signature_for_vapp(path, session_id, project_k):
    """生成vapp签名 - 基于JS代码的H函数"""
    request_uuid = generate_uuid()
    timestamp = int(time.time() * 1000)
    
    if "?" in path:
        path = path.split("?")[0]
    
    # JS代码中的签名算法: path&&session_id&&uuid&&timestamp&&FR*r!isE5W&&tenant_id
    sign_str = f"{path}&&{session_id}&&{request_uuid}&&{timestamp}&&FR*r!isE5W&&{project_k}"
    signature = hashlib.sha256(sign_str.encode()).hexdigest()
    
    log_debug(f"vapp签名字符串: {sign_str}")
    
    return {
        "uuid": request_uuid,
        "time": timestamp,
        "signature": signature
    }

def get_signature_for_passport(path, signature_key, body=""):
    """生成passport签名 - 基于JS代码的G函数"""
    request_uuid = generate_uuid()
    
    if body:
        # POST请求 - JS: "post%%{path}?{body}%%{uuid}%%"
        sign_str = f"post%%{path}?{body}%%{request_uuid}%%"
    else:
        # GET请求
        if "?" in path:
            query = path.split("?")[1]
            path_only = path.split("?")[0]
            sign_str = f"get%%{path_only}?{query}%%{request_uuid}%%"
        else:
            sign_str = f"get%%{path}%%{request_uuid}%%"
    
    # 使用HMAC-SHA256签名
    signature = hmac.new(
        signature_key.encode(),
        sign_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    log_debug(f"passport签名字符串: {sign_str}")
    
    return {
        "uuid": request_uuid,
        "signature": signature
    }

def encrypt_password(password):
    """RSA加密密码 - 基于JS代码的加密逻辑"""
    try:
        # 解码公钥
        key_data = base64.b64decode(RSA_PUBLIC_KEY)
        public_key = RSA.import_key(key_data)
        cipher = PKCS1_v1_5.new(public_key)
        encrypted = cipher.encrypt(password.encode())
        result = base64.b64encode(encrypted).decode()
        
        log_debug(f"密码加密成功，长度: {len(result)}")
        return result
    except Exception as e:
        log_debug(f"密码加密失败: {e}")
        return password  # 如果加密失败，返回原密码

def request_vapp_api(path, session_id, project, account_id="", data=None):
    """请求vapp API - 基于JS代码的w函数"""
    sign_info = get_signature_for_vapp(path, session_id, project["k"])
    _, common_ua = generate_ua(project["p"])
    
    headers = {
        "Connection": "Keep-Alive",
        "X-TIMESTAMP": str(sign_info["time"]),
        "X-SESSION-ID": session_id,
        "X-REQUEST-ID": sign_info["uuid"],
        "X-SIGNATURE": sign_info["signature"],
        "X-TENANT-ID": project["k"],
        "X-ACCOUNT-ID": account_id,
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip",
        "user-agent": common_ua
    }
    
    url = f"https://vapp.tmuyun.com{path}"
    timeout = int(get_config('timeout', '30'))
    proxies = get_proxy()
    
    log_debug(f"vapp API请求: {url}")
    log_debug(f"请求头: {headers}")
    if data:
        log_debug(f"请求体: {data}")
    if proxies:
        log_debug(f"使用代理: {proxies}")
    
    try:
        if data:
            response = requests.post(url, headers=headers, data=data, timeout=timeout, proxies=proxies)
        else:
            response = requests.post(url, headers=headers, timeout=timeout, proxies=proxies)
        
        log_debug(f"vapp API响应状态码: {response.status_code}")
        log_debug(f"vapp API响应头: {dict(response.headers)}")
        
        time.sleep(2)  # JS代码中的等待
        
        result = response.json()
        log_debug(f"vapp API响应内容: {result}")
        return result
    except Exception as e:
        log_debug(f"vapp API请求失败: {e}")
        return {"code": -1, "message": f"请求失败: {str(e)}"}

def request_passport_api(path, signature_key, project, cookie="", data=None, method="GET"):
    """请求passport API - 基于JS代码的y和C函数"""
    if method == "POST" and data:
        sign_info = get_signature_for_passport(path, signature_key, data)
    else:
        sign_info = get_signature_for_passport(path, signature_key)
    
    ua, _ = generate_ua(project["p"])
    
    headers = {
        "Connection": "Keep-Alive",
        "X-REQUEST-ID": sign_info["uuid"],
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip",
        "user-agent": ua
    }
    
    if method == "POST":
        headers["X-SIGNATURE"] = sign_info["signature"]
        headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
    
    if cookie:
        headers["Cookie"] = cookie
    
    url = f"https://passport.tmuyun.com{path}"
    timeout = int(get_config('timeout', '30'))
    proxies = get_proxy()
    
    log_debug(f"passport API请求: {url} ({method})")
    log_debug(f"请求头: {headers}")
    if data:
        log_debug(f"请求体: {data}")
    if proxies:
        log_debug(f"使用代理: {proxies}")
    
    try:
        if method == "POST" and data:
            response = requests.post(url, headers=headers, data=data, timeout=timeout, proxies=proxies)
        else:
            response = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
        
        log_debug(f"passport API响应状态码: {response.status_code}")
        log_debug(f"passport API响应头: {dict(response.headers)}")
        
        return response
    except Exception as e:
        log_debug(f"passport API请求失败: {e}")
        return None

def get_captcha_image(signature_key, project, cookie):
    """获取验证码图片 - 基于JS代码的A函数"""
    # 注意：JS代码中获取图片验证码使用的是GET请求，不需要签名
    ua, _ = generate_ua(project["p"])
    
    headers = {
        "Connection": "Keep-Alive",
        "Cache-Control": "no-cache",
        "X-REQUEST-ID": generate_uuid(),  # JS代码中使用I()生成新的UUID
        "Accept-Encoding": "gzip",
        "user-agent": ua,
        "Cookie": cookie
    }
    
    url = f"https://passport.tmuyun.com/web/security/captcha_image"
    timeout = int(get_config('timeout', '30'))
    proxies = get_proxy()
    
    log_debug(f"获取验证码图片请求: {url}")
    log_debug(f"请求头: {headers}")
    if proxies:
        log_debug(f"使用代理: {proxies}")
    
    try:
        response = requests.get(url, headers=headers, timeout=timeout, proxies=proxies)
        
        log_debug(f"获取验证码图片响应状态码: {response.status_code}")
        log_debug(f"获取验证码图片响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            image_b64 = base64.b64encode(response.content).decode()
            log_debug(f"获取验证码图片成功，大小: {len(response.content)} 字节")
            return image_b64
        else:
            log_debug(f"获取验证码图片失败，状态码: {response.status_code}")
            log_debug(f"响应内容: {response.text[:500]}")
            return None
    except Exception as e:
        log_debug(f"获取验证码图片失败: {e}")
        return None

def solve_captcha(image_base64):
    """解析验证码 - 基于JS代码的E函数"""
    ocr_server = get_config('ocr_server', 'https://ddddocr.xzxxn7.live')
    proxies = get_proxy()
    
    log_debug(f"开始识别验证码，OCR服务器: {ocr_server}")
    if proxies:
        log_debug(f"OCR请求使用代理: {proxies}")
    
    try:
        response = requests.post(
            f"{ocr_server}/classification",
            json={"image": image_base64},
            timeout=30,
            proxies=proxies
        )
        
        log_debug(f"OCR响应状态码: {response.status_code}")
        
        result = response.json()
        log_debug(f"OCR响应内容: {result}")
        
        if result.get('result'):
            log_debug(f"验证码识别成功: {result['result']}")
            return result['result']
        return None
    except Exception as e:
        log_debug(f"验证码识别失败: {e}")
        return None

def init_session(project):
    """初始化会话 - 基于JS代码的会话初始化"""
    log_debug("开始初始化会话")
    # 在JS代码中，初始调用时session_id是空的，account_id也是空的
    result = request_vapp_api("/api/account/init", "", project, "")
    if result.get("code") == 0 and result.get("data", {}).get("session"):
        session_id = result["data"]["session"]["id"]
        log_debug(f"会话初始化成功: {session_id}")
        return session_id
    log_debug(f"会话初始化失败: {result}")
    return None

def get_signature_key(project):
    """获取签名密钥 - 基于JS代码的签名密钥获取"""
    log_debug("开始获取签名密钥")
    path = f"/web/init?client_id={project['p']}"
    response = request_passport_api(path, "", project)
    
    if response and response.status_code == 200:
        result = response.json()
        if result.get("code") == 0 and result.get("data", {}).get("client"):
            signature_key = result["data"]["client"]["signature_key"]
            log_debug(f"签名密钥获取成功: {signature_key}")
            
            # 处理cookie - 从响应中提取所有需要的cookie
            cookie = ""
            
            # 使用requests的cookies对象，这样更可靠
            if response.cookies:
                cookie_pairs = []
                for cookie_obj in response.cookies:
                    cookie_pairs.append(f"{cookie_obj.name}={cookie_obj.value}")
                cookie = '; '.join(cookie_pairs)
                log_debug(f"从cookies对象解析: {cookie_pairs}")
            
            # 如果cookies对象为空，回退到解析Set-Cookie头
            if not cookie:
                set_cookie_header = response.headers.get('set-cookie') or response.headers.get('Set-Cookie')
                if set_cookie_header:
                    log_debug(f"原始Set-Cookie头: {set_cookie_header}")
                    
                    # 简单的解析方法：分割每个cookie并提取name=value部分
                    cookies = []
                    # 使用正则表达式匹配cookie
                    cookie_pattern = r'([^=,;]+=[^,;]+)'
                    matches = re.findall(cookie_pattern, set_cookie_header)
                    for match in matches:
                        if '=' in match and not any(keyword in match.lower() for keyword in ['expires', 'max-age', 'path', 'domain']):
                            cookies.append(match.strip())
                    
                    cookie = '; '.join(cookies)
                    log_debug(f"正则解析后的cookies: {cookies}")
            
            log_debug(f"最终cookie: {cookie}")
            return signature_key, cookie
    
    log_debug("签名密钥获取失败")
    return None, ""

def send_verification_code(phone, project, signature_key, cookie):
    """发送验证码 - 基于JS代码的验证码发送逻辑"""
    log_debug(f"开始发送验证码到: {phone}")
    data = f"client_id={project['p']}&phone_number={phone}"
    response = request_passport_api("/web/security/send_security_code", signature_key, project, cookie, data, "POST")
    
    if response and response.status_code == 200:
        result = response.json()
        log_debug(f"发送验证码API响应: {result}")
        
        if result.get("code") == 0:
            log_debug("验证码发送成功")
            return True, "发送成功", cookie
        
        # 如果需要图片验证码
        if result.get("code") != 0:
            log_debug(f"需要图片验证码，错误码: {result.get('code')}, 错误信息: {result.get('message')}")
            # 获取图片验证码
            captcha_image = get_captcha_image(signature_key, project, cookie)
            if not captcha_image:
                return False, "获取验证码图片失败", cookie
            
            # 解析验证码
            log_debug("开始识别图片验证码")
            captcha_result = solve_captcha(captcha_image)
            if not captcha_result:
                return False, "验证码识别失败", cookie
            
            log_debug(f"图片验证码识别结果: {captcha_result}")
            
            # 重新发送验证码
            data = f"captcha={captcha_result}&client_id={project['p']}&phone_number={phone}"
            response = request_passport_api("/web/security/send_security_code", signature_key, project, cookie, data, "POST")
            
            if response and response.status_code == 200:
                result = response.json()
                log_debug(f"使用图片验证码的API响应: {result}")
                
                if result.get("code") == 0:
                    log_debug("使用图片验证码发送成功")
                    return True, "发送成功", cookie
                else:
                    log_debug(f"使用图片验证码发送失败: {result.get('message')}")
                    return False, result.get("message", "发送失败"), cookie
            else:
                log_debug(f"使用图片验证码的请求失败，状态码: {response.status_code if response else 'None'}")
                return False, "请求失败", cookie
        
        log_debug(f"验证码发送失败: {result.get('message')}")
        return False, result.get("message", "发送失败"), cookie
    else:
        log_debug(f"发送验证码请求失败，状态码: {response.status_code if response else 'None'}")
        return False, "请求失败", cookie

def verify_code(phone, code, project, signature_key, cookie):
    """验证验证码 - 基于JS代码的验证码验证"""
    log_debug(f"开始验证验证码: {code}")
    path = f"/web/security/check_security_code?client_id={project['p']}&phone_number={phone}&security_code={code}"
    response = request_passport_api(path, signature_key, project, cookie)
    
    if response and response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            log_debug("验证码验证成功")
            return True, "验证成功"
        else:
            log_debug(f"验证码验证失败: {result.get('message')}")
            return False, result.get("message", "验证失败")
    
    return False, "请求失败"

def change_password(phone, code, password, project, signature_key, cookie):
    """修改密码 - 基于JS代码的密码修改逻辑"""
    log_debug("开始修改密码")
    # 加密密码
    encrypted_password = encrypt_password(password)
    
    # URL编码加密后的密码
    encoded_password = quote(encrypted_password)
    
    data = f"client_id={project['p']}&new_password={encoded_password}&phone_number={phone}&security_code={code}"
    response = request_passport_api("/web/oauth/reset_password", signature_key, project, cookie, data, "POST")
    
    if response and response.status_code == 200:
        result = response.json()
        if result.get("code") == 0:
            log_debug("密码修改成功")
            return True, "密码修改成功"
        elif result.get("code") == 100001:
            # 需要注册，先获取授权码 - 基于JS代码的注册逻辑
            log_debug("用户不存在，开始注册流程")
            auth_data = f"client_id={project['p']}&phone_number={phone}&security_code={code}"
            auth_response = request_passport_api("/web/oauth/security_code_auth", signature_key, project, cookie, auth_data, "POST")
            
            if auth_response and auth_response.status_code == 200:
                auth_result = auth_response.json()
                if auth_result.get("code") == 0:
                    auth_code = auth_result["data"]["authorization_code"]["code"]
                    log_debug(f"获取授权码成功: {auth_code}")
                    
                    # 注册 - 这里需要使用空的session_id，因为还没有完整的会话
                    register_data = f"check_token=&code={auth_code}&token=&type=-1&union_id="
                    register_result = request_vapp_api("/api/zbtxz/login", "", project, "", register_data)
                    
                    log_debug(f"注册结果: {register_result}")
                    return True, f"注册并设置密码成功: {register_result.get('message', '成功')}"
                else:
                    log_debug(f"获取授权码失败: {auth_result.get('message')}")
                    return False, auth_result.get("message", "获取授权码失败")
        else:
            log_debug(f"密码修改失败: {result.get('message')}")
            return False, result.get("message", "密码修改失败")
    
    return False, "请求失败"

def show_project_list():
    """显示项目列表"""
    content_lines = ["🎯 支持的项目列表:", ""]
    for key, project in PROJECT_CONFIG.items():
        content_lines.append(f"{key}. {project['name']}")
    content_lines.extend(["", "请回复项目编号选择"])
    return format_message("项目选择", content_lines)

def show_tutorial():
    """显示使用教程"""
    tutorial_lines = [
        "📖 使用教程",
        "",
        "1. 发送【雪乃改密】开始修改密码",
        "2. 选择要修改的项目",
        "3. 输入手机号码",
        "4. 输入收到的验证码",
        "5. 输入新密码",
        "6. 完成密码修改",
        "",
        "📝 指令列表:",
        "• 雪乃改密 / 雪乃改密码 / 雪乃修改密码 - 开始改密",
        "• 雪乃配置 - 配置OCR服务器和代理",
        "• 雪乃管理 - 管理已保存账号",
        "• 雪乃教程 - 查看此教程",
        "",
        "🚀 快捷指令:",
        "• 西施眼改密 / 望潮改密 / 新江北改密",
        "• 桐庐改密 / ZSWY改密 / SHPJ改密",
        "• 越城改密 / 大潮改密 / 融磐安改密",
        "• 蓝精灵改密 / 爱海盐改密 / 青椒改密",
        "• 荆州改密",
        "",
        "⚠️ 注意事项:",
        "• 验证码有效期为5分钟",
        "• 密码将使用RSA加密传输",
        "• 如遇图片验证码会自动识别",
        "",
        "📞 技术支持:",
        "基于 @xzxxn777 JS代码改编",
        "售后群: 2993959969"
    ]
    return format_message("雪乃改密教程", tutorial_lines)

def show_config():
    """显示配置页面"""
    ocr_server = get_config('ocr_server', 'https://ddddocr.xzxxn7.live')
    timeout = get_config('timeout', '30')
    debug_mode = get_config('debug_mode', 'false')
    auto_retry = get_config('auto_retry', 'true')
    proxy = get_config('proxy', '')
    
    config_lines = [
        "⚙️ 当前配置:",
        "",
        f"OCR服务器: {ocr_server}",
        f"请求超时: {timeout}秒",
        f"调试模式: {'开启' if debug_mode.lower() == 'true' else '关闭'}",
        f"自动重试: {'开启' if auto_retry.lower() == 'true' else '关闭'}",
        f"代理设置: {proxy if proxy else '未设置'}",
        "",
        "📝 操作指令:",
        "1 - 修改OCR服务器",
        "2 - 修改请求超时",
        "3 - 切换调试模式",
        "4 - 切换自动重试",
        "5 - 设置代理",
        "q - 退出配置",
        "",
        "代理格式说明:",
        "• http开头为API模式: http://api.example.com/proxy",
        "• 其他为固定代理: 127.0.0.1:8080",
        "",
        "请选择要修改的配置:"
    ]
    return format_message("雪乃改密配置", config_lines)

def handle_config():
    """处理配置"""
    sender.reply(show_config())
    
    while True:
        choice = sender.input(60000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply("✅ 已退出配置")
            break
        
        if choice == '1':
            sender.reply("请输入新的OCR服务器地址:")
            new_server = sender.input(60000, 1, False)
            if new_server:
                set_config('ocr_server', new_server)
                sender.reply(f"✅ OCR服务器已更新为: {new_server}")
            else:
                sender.reply("❌ 输入无效")
        
        elif choice == '2':
            sender.reply("请输入新的超时时间(秒):")
            new_timeout = sender.input(60000, 1, False)
            if new_timeout and new_timeout.isdigit():
                set_config('timeout', new_timeout)
                sender.reply(f"✅ 请求超时已更新为: {new_timeout}秒")
            else:
                sender.reply("❌ 请输入有效数字")
        
        elif choice == '3':
            current = get_config('debug_mode', 'false')
            new_value = 'false' if current.lower() == 'true' else 'true'
            set_config('debug_mode', new_value)
            sender.reply(f"✅ 调试模式已{'开启' if new_value == 'true' else '关闭'}")
        
        elif choice == '4':
            current = get_config('auto_retry', 'true')
            new_value = 'false' if current.lower() == 'true' else 'true'
            set_config('auto_retry', new_value)
            sender.reply(f"✅ 自动重试已{'开启' if new_value == 'true' else '关闭'}")
        
        elif choice == '5':
            sender.reply("请输入新的代理设置:")
            sender.reply("• http开头为API模式: http://api.example.com/proxy")
            sender.reply("• 其他为固定代理: 127.0.0.1:8080")
            sender.reply("• 留空取消代理设置")
            new_proxy = sender.input(60000, 1, False)
            if new_proxy is not None:
                set_config('proxy', new_proxy)
                if new_proxy:
                    sender.reply(f"✅ 代理设置已更新为: {new_proxy}")
                else:
                    sender.reply("✅ 代理设置已清空")
            else:
                sender.reply("❌ 输入超时")
        
        else:
            sender.reply("❌ 无效选择，请重新输入")
        
        sender.reply(show_config())

def get_proxy():
    """获取代理设置"""
    proxy_config = get_config('proxy', '')
    if not proxy_config:
        return None
    
    try:
        if proxy_config.startswith('http'):
            # API模式获取代理
            log_debug(f"从API获取代理: {proxy_config}")
            response = requests.get(proxy_config, timeout=10)
            if response.status_code == 200:
                proxy_data = response.text.strip()
                # 假设API返回格式为 IP:PORT
                if ':' in proxy_data:
                    proxy = {
                        'http': f'http://{proxy_data}',
                        'https': f'http://{proxy_data}'
                    }
                    log_debug(f"获取到代理: {proxy_data}")
                    return proxy
            log_debug("API获取代理失败")
            return None
        else:
            # 固定代理池模式
            if ':' in proxy_config:
                proxy = {
                    'http': f'http://{proxy_config}',
                    'https': f'http://{proxy_config}'
                }
                log_debug(f"使用固定代理: {proxy_config}")
                return proxy
            else:
                log_debug("代理格式错误")
                return None
    except Exception as e:
        log_debug(f"获取代理失败: {e}")
        return None

def main_change_password():
    """主要的改密流程"""
    # 显示项目列表
    sender.reply(show_project_list())
    
    # 选择项目
    project_choice = sender.input(120000, 1, False)
    if not project_choice or project_choice not in PROJECT_CONFIG:
        sender.reply("❌ 无效的项目选择")
        return
    
    project = PROJECT_CONFIG[project_choice]
    sender.reply(f"✅ 已选择项目: {project['name']}")
    log_debug(f"选择的项目配置: {project}")
    
    # 输入手机号
    sender.reply("📱 请输入手机号:")
    phone = sender.input(120000, 1, False)
    if not phone or not phone.isdigit() or len(phone) != 11:
        sender.reply("❌ 手机号格式错误")
        return
    
    log_debug(f"输入的手机号: {phone}")
    sender.reply("📡 正在初始化...")
    
    # 初始化会话
    session_id = init_session(project)
    if not session_id:
        sender.reply("❌ 初始化会话失败")
        return
    
    log_debug(f"初始化成功，session_id: {session_id}")
    
    # 获取签名密钥
    signature_key, cookie = get_signature_key(project)
    if not signature_key:
        sender.reply("❌ 获取签名密钥失败")
        return
    
    log_debug(f"获取签名密钥成功: {signature_key}")
    log_debug(f"获取cookie成功: {cookie}")
    
    sender.reply("📱 正在发送验证码...")
    
    # 发送验证码
    success, message, cookie = send_verification_code(phone, project, signature_key, cookie)
    if not success:
        sender.reply(f"❌ 发送验证码失败: {message}")
        return
    
    sender.reply(f"✅ {message}")
    sender.reply("🔐 请输入收到的验证码:")
    
    # 输入验证码
    code = sender.input(300000, 1, False)  # 5分钟有效期
    if not code:
        sender.reply("❌ 验证码输入超时")
        return
    
    sender.reply("🔍 正在验证...")
    
    # 验证验证码
    success, message = verify_code(phone, code, project, signature_key, cookie)
    if not success:
        sender.reply(f"❌ 验证失败: {message}")
        return
    
    sender.reply(f"✅ {message}")
    sender.reply("🔒 请输入新密码:")
    
    # 输入新密码
    password = sender.input(120000, 1, False)
    if not password:
        sender.reply("❌ 密码不能为空")
        return
    
    sender.reply("🔄 正在修改密码...")
    
    # 修改密码 - 传递session_id用于可能的注册流程
    success, message = change_password(phone, code, password, project, signature_key, cookie)
    if success:
        result_lines = [
            "🎉 密码修改成功!",
            "",
            f"项目: {project['name']}",
            f"手机号: {phone[:3]}****{phone[7:]}",
            "",
            "请妥善保管新密码"
        ]
        sender.reply(format_message("修改成功", result_lines))
    else:
        sender.reply(f"❌ 密码修改失败: {message}")

def main():
    """主函数"""
    # 获取触发的消息内容
    message = sender.getMessage()
    
    if not message:
        return
    
    # 指令匹配
    if message in ['雪乃改密', '雪乃改密码', '雪乃修改密码']:
        main_change_password()
    elif message == '雪乃教程':
        sender.reply(show_tutorial())
    elif message == '雪乃配置':
        handle_config()
    elif message == '雪乃管理':
        sender.reply("🚧 账号管理功能开发中...")
    else:
        # 检查是否是项目特定指令
        for key, project in PROJECT_CONFIG.items():
            if message in [f'{project["name"]}改密', f'{project["name"]}改密码', f'{project["name"]}修改密码']:
                # 直接跳转到指定项目的改密流程
                sender.reply(f"✅ 已选择项目: {project['name']}")
                # 这里可以实现直接进入指定项目的改密流程
                main_change_password()
                return
        
        # 默认显示帮助
        sender.reply(show_tutorial())

if __name__ == "__main__":
    main() 