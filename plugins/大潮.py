# [title: 大潮]
# [language: python]
# [class: 工具类]
# [service: 2993959969] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(大潮|dc)(登录|登陆)$|^登(录|陆)(大潮|dc)$|^(大潮|dc)(查询|管理)$|^(查询|管理)(大潮|dc)$|^大潮授权$|^大潮检测$|^大潮红包推送$|^大潮教程$]
# [cron: 0 9 * * *] cron定时，支持5位域和6位域
# [priority: 0] 优先级，数字越大表示优先级越高
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [open_source: false]是否开源
# [icon: https://img-upload.vorto.cc/beb5a0d45aa58e08348e1e4076fa419e.jpg]图标链接地址
# [version: 1.4]版本号
# [public:true] 是否发布
# [price: 6.88] 上架价格
# [description: 大潮现金毛，概率0.2~1<br>指令：大潮登录、管理、查询、授权、红包推送、教程<br>脚本及卡密进群获取<br>1.2:增加大潮教程指令，优化码支付二维码生成方式<br>1.1:检测逻辑优化(提前天数提醒+自动清理)，管理员授权改为按天数(支持正负数)<br>1.0.3:增加备注功能，推送显示对应备注]

import json
import time
import hashlib
import random
import base64
import requests
import uuid
import hmac
from datetime import datetime, timedelta
import middleware
import vorto_utils
from vorto_utils import mask_account
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_dc_user', key=userid)

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 's_dc',
    'coin_key': 'dd_sign_points',
    'name': '大潮'
}

# 大潮API配置
TENANT_ID = "94"
CLIENT_ID = "10048"

# [param: {"required":false,"key":"s_dc.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_dc.use_daipanel","bool":true,"placeholder":"","name":"使用呆呆面板","desc":"勾选使用呆呆面板，不勾选使用青龙面板"}]
# [param: {"required":false,"key":"s_dc.panel_group","bool":false,"placeholder":"例:顺丰","name":"呆呆面板分组","desc":"填写后新增/更新变量时同步写入group字段，留空则不处理"}]
# [param: {"required":true,"key":"s_dc.osname","bool":false,"placeholder":"必填项,例:S_DC","name":"提交到青龙的变量名","desc":"青龙容器内大潮的变量名"}]
# [param: {"required":true,"key":"s_dc.Vipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":false,"key":"s_dc.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_dc.notify","bool":false,"placeholder":"例:qq,wx,tb 多个用英文逗号分隔","name":"通知渠道","desc":"配置检测通知推送渠道"}]
# [param: {"required":false,"key":"s_dc.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]

def get_user_content():
    """获取用户配置内容"""
    osname = middleware.bucketGet('s_dc', 'osname') or 'S_DC'
    qlname = middleware.bucketGet('s_dc', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_dc', 'Vipmoney') or '1')
    coin = int(middleware.bucketGet('s_dc', 'coin') or '0')
    return osname, qlname, Vipmoney, coin


def generate_random_uuid():
    """生成随机UUID"""
    return str(uuid.uuid4())

def generate_random_device_id():
    """生成随机设备ID"""
    return ''.join(random.choices('0123456789abcdef', k=32))

def generate_signature_md5(raw_str: str) -> str:
    """生成MD5签名"""
    try:
        return hashlib.md5(raw_str.encode(), usedforsecurity=True).hexdigest()
    except TypeError:
        return hashlib.md5(raw_str.encode()).hexdigest()

def generate_random_ua():
    """生成随机UA"""
    version = "14.1.6"
    uuid_str = generate_random_uuid()
    device_models = ["M1903F2A", "M2001J2E", "M2001J2C", "M2001J1E", "M2001J1C", 
                    "M2002J9E", "M2011K2C", "M2102K1C", "M2101K9C", "2107119DC", 
                    "2201123C", "2112123AC", "2201122C", "2211133C", "2210132C", 
                    "2304FPN6DC", "23127PN0CC", "24031PN0DC", "23090RA98C", 
                    "2312DRA50C", "2312CRAD3C", "2312DRAABC", "22101316UCP", "22101316C"]
    
    device_model = random.choice(device_models)
    device_name = f"Xiaomi {device_model}"
    os_name = "Android"
    
    ua = f"{os_name.upper()};11;{CLIENT_ID};{version};1.0;null;{device_model}"
    common_ua = f"{version};{uuid_str};{device_name};{os_name};11;6.11.0"
    
    return {
        'ua': ua,
        'commonUa': common_ua,
        'uuid': uuid_str
    }


def get_session_id():
    """获取sessionId"""
    init_url = "https://vapp.tmuyun.com/api/account/init"
    device_id = generate_random_device_id()
    ua_info = generate_random_ua()
    
    init_headers = {
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip",
        "user-agent": ua_info['commonUa'],
        "X-TENANT-ID": TENANT_ID,
        "Content-Type": "application/json;charset=utf-8"
    }
    
    try:
        init_response = requests.post(init_url, headers=init_headers, json={}, timeout=10)
        time.sleep(1)
        
        if init_response.status_code != 200:
            return None, None, None, None
            
        init_result = init_response.json()
        
        if 'data' in init_result and 'session' in init_result['data']:
            session_id = init_result['data']['session']['id']
            return session_id, device_id, ua_info['ua'], ua_info['commonUa']
        else:
            return None, None, None, None
            
    except Exception as e:
        sender.reply(f"获取sessionId异常: {str(e)}")
        return None, None, None, None

def get_signature_key(user_agent):
    """获取signature_key"""
    passport_url = f"https://passport.tmuyun.com/web/init?client_id={CLIENT_ID}"
    passport_headers = {
        "Connection": "Keep-Alive",
        "Cache-Control": "no-cache",
        "X-REQUEST-ID": generate_random_uuid(),
        "Accept-Encoding": "gzip",
        "user-agent": user_agent
    }
    
    try:
        passport_response = requests.get(passport_url, headers=passport_headers, timeout=10)
        if passport_response.status_code != 200:
            return None
            
        passport_result = passport_response.json()
        
        if 'data' in passport_result and 'client' in passport_result['data'] and 'signature_key' in passport_result['data']['client']:
            return passport_result['data']['client']['signature_key']
        else:
            return None
            
    except Exception as e:
        sender.reply(f"获取signature_key异常: {str(e)}")
        return None

def get_authorization_code(phone, password, signature_key, user_agent, device_id):
    """获取授权码"""
    request_uuid = generate_random_uuid()
    
    try:
        # 使用公钥加密密码
        public_key = """MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD6XO7e9YeAOs+cFqwa7ETJ+WXizPqQeXv68i5vqw9pFREsrqiBTRcg7wB0RIp3rJkDpaeVJLsZqYm5TW7FWx/iOiXFc+zCPvaKZric2dXCw27EvlH5rq+zwIPDAJHGAfnn1nmQH7wR3PCatEIb8pz5GFlTHMlluw4ZYmnOwg+thwIDAQAB"""
        
        key = RSA.importKey(base64.b64decode(public_key))
        cipher = PKCS1_v1_5.new(key)
        
        encrypted_password = cipher.encrypt(password.encode())
        base64_encrypted_password = base64.b64encode(encrypted_password).decode()
        
        # 构建原始请求体（用于签名）
        raw_body = f"client_id={CLIENT_ID}&password={base64_encrypted_password}&phone_number={phone}"
            
        # 构建签名字符串
        sign_str = f"post%%/web/oauth/credential_auth?{raw_body}%%{request_uuid}%%"
        signature = hmac.new(
            signature_key.encode(),
            sign_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # URL编码加密后的密码
        encoded_password = requests.utils.quote(base64_encrypted_password)
        encoded_body = f"client_id={CLIENT_ID}&password={encoded_password}&phone_number={phone}"
        
        url = "https://passport.tmuyun.com/web/oauth/credential_auth"
        
        headers = {
            "Connection": "Keep-Alive",
            "X-REQUEST-ID": request_uuid,
            "X-SIGNATURE": signature,
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Accept-Encoding": "gzip",
            "User-Agent": user_agent
        }
        
        response = requests.post(url, headers=headers, data=encoded_body, timeout=10)
        time.sleep(1)
        
        if response.status_code != 200:
            return None
        
        result = response.json()
        
        if result.get('code') != 0:
            return None
        
        auth_code = result['data']['authorization_code']['code']
        return auth_code
        
    except Exception as e:
        sender.reply(f"获取授权码异常: {str(e)}")
        return None

def login_account(auth_code, session_id, device_id, common_ua):
    """登录账号"""
    # 生成签名信息
    uuid_str = generate_random_uuid()
    timestamp = str(int(time.time() * 1000))
    
    path = "/api/zbtxz/login"
    sign_str = f"{path}&&{session_id}&&{uuid_str}&&{timestamp}&&FR*r!isE5W&&{TENANT_ID}"
    signature = hashlib.sha256(sign_str.encode()).hexdigest()
    
    login_url = "https://vapp.tmuyun.com/api/zbtxz/login"
    login_data = f"check_token=&code={auth_code}&token=&type=-1&union_id="
    
    login_headers = {
        "Connection": "Keep-Alive",
        "X-SESSION-ID": session_id,
        "X-TENANT-ID": TENANT_ID,
        "Cache-Control": "no-cache",
        "Accept-Encoding": "gzip",
        "user-agent": common_ua,
        "Content-Type": "application/x-www-form-urlencoded",
        "X-SIGNATURE": signature,
        "X-REQUEST-ID": uuid_str,
        "X-TIMESTAMP": timestamp
    }
    
    try:
        response = requests.post(login_url, headers=login_headers, data=login_data, timeout=10)
        time.sleep(1)
        
        if response.status_code != 200:
            return None, None
        
        try:
            result = response.json()
        except json.JSONDecodeError:
            return None, None
        
        if result.get('code') != 0:
            return None, None
        
        if 'data' not in result or 'session' not in result['data']:
            return None, None
            
        session_data = result['data']['session']
        if 'account_id' not in session_data or 'id' not in session_data:
            return None, None
        
        account_id = session_data['account_id']
        new_session_id = session_data['id']
        return account_id, new_session_id
            
    except Exception as e:
        sender.reply(f"登录异常: {str(e)}")
        return None, None

def bind_account():
    """绑定大潮账号"""
    sender.reply("""
=====大潮登录=====
请按照提示依次输入账号信息
回复"q"退出
==================""")
    
    # 步骤1：输入手机号
    sender.reply("请输入手机号（大潮登录账号）:")
    username = sender.input(120000, 1, False)
    if not username:
        sender.reply("⏰ 操作超时")
        return
    elif username.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    # 简单验证手机号格式
    if not username.isdigit() or len(username) != 11:
        sender.reply("""
=====格式错误=====
❌ 手机号格式不正确
------------------
请输入11位数字手机号
==================""")
        return
    
    # 步骤2：输入密码
    sender.reply("请输入密码:")
    password = sender.input(120000, 1, False)
    if not password:
        sender.reply("⏰ 操作超时")
        return
    elif password.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    # 开始登录流程
    sender.reply("🔄 正在登录...")
    
    try:
        # 获取sessionId
        session_id, device_id, user_agent, common_ua = get_session_id()
        if not session_id:
            sender.reply("❌ 获取会话失败")
            return
        
        # 获取signature_key
        signature_key = get_signature_key(user_agent)
        if not signature_key:
            sender.reply("❌ 获取签名密钥失败")
            return
        
        # 获取授权码
        auth_code = get_authorization_code(username, password, signature_key, user_agent, device_id)
        if not auth_code:
            sender.reply("❌ 账号或密码错误")
            return
        
        # 登录
        account_id, new_session_id = login_account(auth_code, session_id, device_id, common_ua)
        if not account_id:
            sender.reply("❌ 登录失败")
            return
        
        # 保存账号信息
        if not uservalue:
            middleware.bucketSet('s_dc_user', userid, str([username]))
        else:
            accounts = eval(uservalue)
            if username not in accounts:
                accounts.append(username)
                middleware.bucketSet('s_dc_user', userid, str(accounts))
                
        # 保存账号详细信息（只保存账号密码和推送设置）
        account_info = {
            "username": username,
            "password": password,
            "enable_redpack_push": False  # 默认不推送红包
        }
        middleware.bucketSet('s_dc_token', username, json.dumps(account_info))
        
        success_msg = f"""
=====绑定成功=====
📱 手机号: {mask_account(username)}
=================="""
        sender.reply(success_msg)
        
        # 询问是否开启红包推送
        sender.reply("""
=====红包推送设置=====
是否开启红包链接推送功能？
------------------
回复 y 开启推送
回复 n 不开启
==================""")
        
        push_choice = sender.input(120000, 1, False)
        if push_choice and push_choice.lower() == 'y':
            account_info['enable_redpack_push'] = True
            middleware.bucketSet('s_dc_token', username, json.dumps(account_info))
            sender.reply("✅ 已开启红包推送功能")
        else:
            sender.reply("✅ 未开启红包推送功能")
        
        # 检查账号授权状态
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_dc_auth', username)
        
        if accountVip and accountVip > dqsj:
            # 账号已授权且未到期，直接更新账号信息
            sender.reply(f"""
=====账号已授权=====
📅 到期时间: {accountVip}
------------------
正在更新账号信息...
==================""")
            
            # 更新青龙变量
            if update_ql_env(username, account_info):
                sender.reply("✅ 账号信息更新成功")
            else:
                sender.reply("❌ 账号信息更新失败")
        else:
            # 账号未授权或已到期，进入授权流程
            #sender.reply("""
#=====账号未授权=====
#❌ 当前账号未授权或已过期
#------------------
#即将进入授权流程...
#==================""")
            authorize_multiple_accounts([username])
        
    except Exception as e:
        sender.reply(f"""
=====绑定异常=====
❌ 错误: {str(e)}
请重试或联系管理员
==================""")


def relogin_account(username, password):
    """重新登录获取session信息"""
    try:
        # 获取sessionId
        session_id, device_id, user_agent, common_ua = get_session_id()
        if not session_id:
            return None
        
        # 获取signature_key
        signature_key = get_signature_key(user_agent)
        if not signature_key:
            return None
        
        # 获取授权码
        auth_code = get_authorization_code(username, password, signature_key, user_agent, device_id)
        if not auth_code:
            return None
        
        # 登录
        account_id, new_session_id = login_account(auth_code, session_id, device_id, common_ua)
        if not account_id:
            return None
        
        return {
            'session_id': new_session_id,
            'account_id': account_id,
            'device_id': device_id,
            'user_agent': user_agent,
            'common_ua': common_ua
        }
        
    except Exception as e:
        sender.reply(f"重新登录异常: {str(e)}")
        return None

def get_member_token(username, password):
    """获取member_token用于红包API"""
    try:
        # 重新登录获取session信息
        login_info = relogin_account(username, password)
        if not login_info:
            return None, None
        
        session_id = login_info['session_id']
        account_id = login_info['account_id']
        common_ua = login_info['common_ua']
        
        if not session_id or not account_id:
            return None
        
        # 先获取用户信息
        uuid_str = generate_random_uuid()
        timestamp = str(int(time.time() * 1000))
        path = "/api/user_mumber/account_detail"
        sign_str = f"{path}&&{session_id}&&{uuid_str}&&{timestamp}&&FR*r!isE5W&&{TENANT_ID}"
        signature = hashlib.sha256(sign_str.encode()).hexdigest()
        
        headers = {
            "Connection": "Keep-Alive",
            "X-SESSION-ID": session_id,
            "X-REQUEST-ID": uuid_str,
            "X-SIGNATURE": signature,
            "X-TIMESTAMP": timestamp,
            "X-TENANT-ID": TENANT_ID,
            "X-ACCOUNT-ID": account_id,
            "Cache-Control": "no-cache",
            "Accept-Encoding": "gzip",
            "user-agent": common_ua
        }
        
        response = requests.get("https://vapp.tmuyun.com/api/user_mumber/account_detail", headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        result = response.json()
        if result.get('code') != 0 or 'data' not in result:
            return None
        
        user_data = result['data'].get('rst', {})
        
        # 生成签名获取member_token
        timestamp_sec = int(time.time())
        signature_str = f" &id&mobile&nick_name&&{timestamp_sec}&&KO>N<O5&3^L1%23YH0H1#G91*2H"
        signature_hash = hashlib.sha256(signature_str.encode()).hexdigest()
        
        signature_data = {
            "accountId": account_id,
            "signature": signature_hash,
            "mobile": "1",
            "sessionId": session_id,
            "login": "1",
            "user": {
                "realName": "",
                "image_url": user_data.get('image_url', ''),
                "nick_name": user_data.get('nick_name', ''),
                "is_face_verify": 0,
                "idcard": "",
                "id": account_id
            },
            "timestamp": str(timestamp_sec),
            "sign": "xsb_hn"
        }
        
        # 请求member_token
        member_response = requests.post(
            "https://m.aihoge.com/api/memberhy/tm/signature",
            json=signature_data,
            headers={
                "Content-Type": "application/json;charset=UTF-8",
                "Connection": "keep-alive",
                "X-DEVICE-SIGN": "xsb_hn",
                "X-CLIENT-VERSION": "1314",
                "accept": "application/json, text/plain, */*",
                "user-agent": "Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36;xsb_hn;xsb_hn;14.1.6;native_app;6.11.0",
                "HTTP-X-H5-VERSION": "1",
                "Limit": "default",
                "sessionId": session_id,
                "X-DEVICE-ID": "000",
                "accountId": account_id,
                "x-requested-with": "com.hoge.android.app.dachao",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "accept-encoding": "gzip, deflate",
                "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
            },
            timeout=10
        )
        
        if member_response.status_code != 200:
            return None
        
        member_result = member_response.json()
        if not member_result:
            return None
        
        # 构建member_token
        member_token = json.dumps({
            "id": member_result.get('id', ''),
            "black": 0,
            "btoken": member_result.get('btoken', ''),
            "expire": member_result.get('expire', ''),
            "token": member_result.get('token', ''),
            "source": "xsb_hn",
            "mobile": member_result.get('mobile', ''),
            "mark": member_result.get('mark', ''),
            "mtoken": member_result.get('mtoken', ''),
            "stoken": member_result.get('stoken', ''),
            "nick_name": requests.utils.quote(member_result.get('nick_name', '')),
            "avatar": member_result.get('avatar', '')
        })
        
        return member_token, login_info
        
    except Exception as e:
        sender.reply(f"获取member_token异常: {str(e)}")
        return None

def get_redpack_list(account_info):
    """获取未领取红包列表"""
    try:
        username = account_info.get('username', '')
        password = account_info.get('password', '')
        
        if not username or not password:
            return None, "账号信息不完整"
        
        # 重新登录并获取member_token
        member_token, login_info = get_member_token(username, password)
        if not member_token or not login_info:
            return None, "获取member_token失败"
        
        session_id = login_info['session_id']
        account_id = login_info['account_id']
        
        # 使用axh5 API获取红包列表
        url = "https://axh5.aihoge.com/api/lotteryhy/api/client/cj/member/prize/info?prize_type=3&page=1&count=20"
        
        headers = {
            "Connection": "keep-alive",
            "X-DEVICE-SIGN": "xsb_hn",
            "X-CLIENT-VERSION": "1314",
            "accept": "application/json, text/plain, */*",
            "user-agent": "Mozilla/5.0 (Linux; Android 11; 21091116AC Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/94.0.4606.85 Mobile Safari/537.36;xsb_hn;xsb_hn;14.1.6;native_app;6.11.0",
            "HTTP-X-H5-VERSION": "1",
            "member": member_token,
            "Limit": "default",
            "sessionId": session_id,
            "X-DEVICE-ID": "000",
            "accountId": account_id,
            "x-requested-with": "com.hoge.android.app.dachao",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "Referer": "https://axh5.aihoge.com/winningList?refresh_times=1641284795642",
            "accept-encoding": "gzip, deflate",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None, f"请求失败，状态码: {response.status_code}"
        
        result = response.json()
        
        if not result or 'data' not in result:
            return None, "获取红包列表失败"
        
        # 解析红包数据
        data = result.get('data', [])
        
        redpacks = []
        
        # 遍历红包列表
        for prize in data:
            # 只获取未领取的红包 (status != 2)
            status = prize.get('status', 0)
            
            if status != 2 and status != 6:
                # 解析prize_info获取code
                prize_info_str = prize.get('prize_info', '{}')
                try:
                    prize_info = json.loads(prize_info_str)
                    code = prize_info.get('code', '')
                except:
                    code = ''
                
                # 构建红包链接
                link = f"https://m.aihoge.com/lottery/rotor/drawRedPacket?CHECK_CODE={code}"
                
                # 获取过期时间
                end_time = prize.get('end_time', 0)
                if end_time > 0:
                    expire_time_str = datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M")
                else:
                    expire_time_str = "未知"
                
                redpacks.append({
                    'id': prize.get('id', ''),
                    'amount': prize.get('prize_content', '未知'),
                    'link': link,
                    'expire_time': expire_time_str,
                    'activity_name': prize.get('activity_name', ''),
                    'code': code,
                    'status_name': prize.get('status_name', '未知')
                })
        
        return redpacks, "获取成功"
        
    except Exception as e:
        return None, f"获取红包列表异常: {str(e)}"

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到账号
💡 发送 大潮登录 绑定
==================""")
        return

    accounts = eval(uservalue)
    account_list = "\n========选择账号=======\n[0] 全部账号"

    for i, username in enumerate(accounts, 1):
        account_info = json.loads(middleware.bucketGet('s_dc_token', username))
        auth_time = middleware.bucketGet('s_dc_auth', username)

        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'

        remark = account_info.get('remark', '')
        remark_display = f", {remark}" if remark else ""

        account_list += f"\n[{i}]{mask_account(username)}({auth_status}{remark_display})"

    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="

    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    try:
        if choice == '0':
            selected_accounts = accounts.copy()
        else:
            selected_accounts = [
                accounts[int(idx.strip()) - 1]
                for idx in choice.split(',')
                if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
            ]

        if not selected_accounts:
            sender.reply("❌ 未选择有效账号")
            return

        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号，正在查询...")
        
        # 查询每个账号的信息
        query_count = 0
        for username in selected_accounts:
            try:
                account_info = json.loads(middleware.bucketGet('s_dc_token', username))
                
                # 获取授权信息
                auth_time = middleware.bucketGet('s_dc_auth', username)
                auth_status = '已授权' if auth_time and auth_time >= str(datetime.now().date()) else '未授权'
                
                # 获取红包推送状态
                push_status = "已开启" if account_info.get('enable_redpack_push', False) else "未开启"
                
                # 获取备注信息
                remark = account_info.get('remark', '')
                
                # 获取红包列表
                redpacks, msg = get_redpack_list(account_info)
                
                redpack_info = ""
                if redpacks:
                    redpack_info = "=================="
                    redpack_info += f"\n🎁 待领红包: {len(redpacks)}个"
                    for i, pack in enumerate(redpacks[:5], 1):  # 最多显示5个
                        # 缩短红包链接
                        short_link = shorten_url(pack.get('link', '无链接'))
                        redpack_info += f"\n  [{i}] {pack.get('amount', '未知')}"
                        redpack_info += f"\n      🔗 {short_link}"
                        redpack_info += f"\n      ⏰ 过期：{pack.get('expire_time', '未知')}"
                    if len(redpacks) > 5:
                        redpack_info += f"\n  ... 还有{len(redpacks)-5}个红包"
                else:
                    redpack_info = "\n🎁 待领红包: 0个"
                
                # 显示账号信息
                remark_info = f"\n📝 备注: {remark}" if remark else ""
                account_info_msg = f"""
=====账号信息[{query_count+1}/{len(selected_accounts)}]=====
📱 手机号: {mask_account(username)}
🏷 状态: {auth_status}
💰 红包推送: {push_status}{remark_info}{redpack_info}
=================="""
                sender.reply(account_info_msg)
                query_count += 1
                
                if query_count < len(selected_accounts) and len(selected_accounts) > 3:
                    time.sleep(0.5)
                    
            except Exception as e:
                sender.reply(f"""
=====查询失败[{query_count+1}/{len(selected_accounts)}]=====
📱 手机号: {mask_account(username)}
❌ 状态: 账号信息查询失败
❌ 错误: {str(e)}
==================""")
                query_count += 1
                
        if query_count > 0:
            sender.reply("✅ 查询完成")
            
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")

def push_redpack_links():
    """推送红包链接给用户（管理员功能）"""
    # 检查管理员权限
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return
    
    sender.reply("🔍 正在检查红包...")
    
    # 获取所有用户
    all_users = middleware.bucketAllKeys('s_dc_user')
    if not all_users:
        sender.reply("❌ 没有用户")
        return
    
    # 统计信息
    total_users = 0
    total_accounts = 0
    total_redpacks = 0
    pushed_users = 0
    
    # 遍历所有用户
    for user_id in all_users:
        try:
            # 获取用户的账号列表
            user_accounts = eval(middleware.bucketGet('s_dc_user', user_id) or '[]')
            if not user_accounts:
                continue
            
            total_users += 1
            user_redpacks = []  # 该用户的所有红包
            
            # 检查该用户的每个账号
            for username in user_accounts:
                try:
                    total_accounts += 1
                    account_info = json.loads(middleware.bucketGet('s_dc_token', username))
                    
                    # 检查是否开启红包推送
                    if not account_info.get('enable_redpack_push', False):
                        continue
                    
                    # 检查授权状态
                    auth_time = middleware.bucketGet('s_dc_auth', username)
                    if not auth_time or auth_time < str(datetime.now().date()):
                        continue
                    
                    # 获取红包列表
                    redpacks, msg = get_redpack_list(account_info)
                    
                    if redpacks and len(redpacks) > 0:
                        user_redpacks.append({
                            'username': username,
                            'redpacks': redpacks
                        })
                        
                except Exception as e:
                    print(f"检查账号异常: {username}, 错误: {str(e)}")
                    continue
            
            # 如果该用户有红包，推送给该用户
            if user_redpacks:
                push_msg = "=====红包提醒=====\n"
                
                for account_data in user_redpacks:
                    username = account_data['username']
                    redpacks = account_data['redpacks']
                    
                    # 获取账号备注信息
                    try:
                        account_info = json.loads(middleware.bucketGet('s_dc_token', username))
                        remark = account_info.get('remark', '')
                    except:
                        remark = ''
                    
                    # 显示账号信息，如果有备注则显示备注
                    if remark:
                        push_msg += f"\n📱 账号: {mask_account(username)}({remark})\n"
                    else:
                        push_msg += f"\n📱 账号: {mask_account(username)}\n"
                    
                    push_msg += f"🎁 待领红包: {len(redpacks)}个\n"
                    push_msg += "------------------\n"
                    
                    for i, pack in enumerate(redpacks, 1):
                        # 缩短红包链接
                        short_link = shorten_url(pack.get('link', '无链接'))
                        push_msg += f"[{i}] {pack.get('amount', '未知')}\n"
                        push_msg += f"🔗 {short_link}\n"
                        push_msg += f"⏰ 过期: {pack.get('expire_time', '未知')}\n"
                        
                        total_redpacks += 1
                    
                    push_msg += "\n"
                
                push_msg += "------------------\n"
                push_msg += "请及时领取红包\n"
                push_msg += "=================="
                
                # 推送给该用户
                try:
                    # 获取通知渠道配置
                    notify_channels = middleware.bucketGet('s_dc', 'notify') or 'qq'
                    channels = [channel.strip() for channel in notify_channels.split(',') if channel.strip()]
                    
                    for channel in channels:
                        try:
                            middleware.push(
                                imType=channel,
                                groupCode='',
                                userID=user_id,
                                title="",
                                content=push_msg
                            )
                        except Exception as e:
                            print(f"推送失败: {channel}, 用户: {user_id}, 错误: {str(e)}")
                            continue
                    
                    pushed_users += 1
                    
                except Exception as e:
                    print(f"推送给用户失败: {user_id}, 错误: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"处理用户异常: {user_id}, 错误: {str(e)}")
            continue
    
    # 推送完成提示
    sender.reply(f"""
=====推送完成=====
👥 检查用户: {total_users}个
📱 检查账号: {total_accounts}个
✅ 推送用户: {pushed_users}个
🎁 红包总数: {total_redpacks}个
==================""")


def manage_account():
    """账号管理功能"""
    if not uservalue:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到账号
💡 发送 大潮登录 绑定
==================""")
        return

    accounts = eval(uservalue)

    # 先显示管理功能菜单
    menu = """
=====账号管理=====
[1] 授权账号
[2] 删除账号
[3] 提交青龙
[4] 红包推送设置
[5] 添加备注
------------------
回复数字选择
回复"q"退出
=================="""
    sender.reply(menu)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    # 然后显示账号列表供选择
    account_list = """
========选择账号=======
[0] 全部账号"""
    
    for i, username in enumerate(accounts, 1):
        account_info = json.loads(middleware.bucketGet('s_dc_token', username))
        auth_time = middleware.bucketGet('s_dc_auth', username)
        
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        
        # 显示红包推送状态
        push_status = "推送✓" if account_info.get('enable_redpack_push', False) else "推送✗"
        
        # 获取备注信息
        remark = account_info.get('remark', '')
        remark_display = f", {remark}" if remark else ""
            
        account_list += f"""
[{i}]{mask_account(username)}({auth_status}, {push_status}{remark_display})"""
        
    account_list += """
=====================
支持多选，用逗号分隔
回复"q"退出
====================="""
    
    sender.reply(account_list)
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
        
    try:
        # 处理账号选择
        selected_accounts = []
        
        if account_choice == '0':
            selected_accounts = accounts.copy()
        else:
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
            
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号")
            
        # 根据之前的功能选择执行对应操作
        if choice == '1':
            # 授权选中的账号
            authorize_multiple_accounts(selected_accounts)
            
        elif choice == '2':
            # 删除选中的账号
            confirm = """
=====确认删除=====
⚠️ 此操作不可恢复
------------------
回复 y 确认删除
回复 n 取消操作
=================="""
            sender.reply(confirm)
            
            confirm = sender.input(120000, 1, False)
            if confirm and confirm.lower() == 'y':
                success_list = []
                fail_list = []
                for username in selected_accounts:
                    try:
                        if username in accounts:
                            accounts.remove(username)
                            
                        middleware.bucketDel('s_dc_token', username)
                        middleware.bucketDel('s_dc_auth', username)
                            
                        delete_ql_env(username)
                        success_list.append(mask_account(username))
                    except Exception as e:
                        fail_list.append(f"{mask_account(username)} {str(e)}")
                
                if accounts:
                    middleware.bucketSet('s_dc_user', userid, str(accounts))
                else:
                    middleware.bucketDel('s_dc_user', userid)

                result = "=====删除完成=====\n"
                result += f"✅ 成功: {len(success_list)}个\n"
                if success_list:
                    result += "、".join(success_list) + "\n"
                if fail_list:
                    result += f"❌ 失败: {len(fail_list)}个\n"
                    result += "\n".join(fail_list) + "\n"
                result += "=================="
                sender.reply(result)
            else:
                sender.reply("✅ 已取消删除")
                
        elif choice == '3':
            # 提交选中账号到青龙
            success_list = []
            fail_list = []
            for username in selected_accounts:
                try:
                    raw = middleware.bucketGet('s_dc_token', username)
                    if not raw:
                        fail_list.append(f"{mask_account(username)} 无账号数据")
                        continue
                    account_info = json.loads(raw)
                    
                    auth_time = middleware.bucketGet('s_dc_auth', username)
                    if auth_time and auth_time >= str(datetime.now().date()):
                        if update_ql_env(username, account_info):
                            success_list.append(mask_account(username))
                        else:
                            fail_list.append(f"{mask_account(username)} 提交失败")
                    else:
                        fail_list.append(f"{mask_account(username)} 未授权/已过期")
                except Exception as e:
                    fail_list.append(f"{mask_account(username)} {str(e)}")
            
            result = "=====提交完成=====\n"
            result += f"✅ 成功: {len(success_list)}个\n"
            if success_list:
                result += "、".join(success_list) + "\n"
            if fail_list:
                result += f"❌ 失败: {len(fail_list)}个\n"
                result += "\n".join(fail_list) + "\n"
            result += "=================="
            sender.reply(result)
        
        elif choice == '4':
            # 红包推送设置
            sender.reply("""
=====红包推送设置=====
请选择操作:
[1] 开启推送
[2] 关闭推送
------------------
回复数字选择
回复"q"退出
==================""")
            
            push_choice = sender.input(120000, 1, False)
            if not push_choice or push_choice.lower() == 'q':
                sender.reply("✅ 已退出")
                return
            
            if push_choice == '1':
                enable_push = True
                action_text = "开启"
            elif push_choice == '2':
                enable_push = False
                action_text = "关闭"
            else:
                sender.reply("❌ 无效的选择")
                return
            
            success_list = []
            fail_list = []
            for username in selected_accounts:
                try:
                    account_info = json.loads(middleware.bucketGet('s_dc_token', username))
                    account_info['enable_redpack_push'] = enable_push
                    middleware.bucketSet('s_dc_token', username, json.dumps(account_info))
                    success_list.append(mask_account(username))
                except Exception as e:
                    fail_list.append(f"{mask_account(username)} {str(e)}")

            result = "=====设置完成=====\n"
            result += f"✅ 已{action_text}: {len(success_list)}个\n"
            if success_list:
                result += "、".join(success_list) + "\n"
            if fail_list:
                result += f"❌ 失败: {len(fail_list)}个\n"
                result += "\n".join(fail_list) + "\n"
            result += "=================="
            sender.reply(result)
        
        elif choice == '5':
            # 添加备注
            sender.reply("""
=====添加备注=====
请输入备注内容:
------------------
回复"q"退出
==================""")
            
            remark_text = sender.input(120000, 1, False)
            if not remark_text or remark_text.lower() == 'q':
                sender.reply("✅ 已退出")
                return
            
            success_list = []
            fail_list = []
            for username in selected_accounts:
                try:
                    account_info = json.loads(middleware.bucketGet('s_dc_token', username))
                    account_info['remark'] = remark_text
                    middleware.bucketSet('s_dc_token', username, json.dumps(account_info))
                    success_list.append(mask_account(username))
                except Exception as e:
                    fail_list.append(f"{mask_account(username)} {str(e)}")
            
            result = "=====备注添加完成=====\n"
            result += f"✅ 成功: {len(success_list)}个\n"
            if success_list:
                result += "、".join(success_list) + "\n"
            if fail_list:
                result += f"❌ 失败: {len(fail_list)}个\n"
                result += "\n".join(fail_list) + "\n"
            result += f"📝 备注: {remark_text}\n"
            result += "=================="
            sender.reply(result)
        else:
            sender.reply("❌ 无效的选择")
            
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")


def authorize_multiple_accounts(usernames):
    """批量授权账号（符合批量回执规范）"""
    account_infos = []
    for username in usernames:
        try:
            token_data = middleware.bucketGet('s_dc_token', username)
            if token_data:
                account_infos.append({'username': username, 'info': json.loads(token_data)})
        except Exception:
            pass

    if not account_infos:
        sender.reply("❌ 没有有效账号")
        return

    sender.reply(
        f"✅ {len(account_infos)} 个有效账号\n"
        "=====设置授权时长=====\n"
        "请输入授权月数(如:1)\n"
        "回复\"q\"退出\n"
        "=================="
    )
    months_input = sender.input(120000, 1, False)
    if not months_input or months_input.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        months = int(months_input)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
    except ValueError:
        sender.reply("❌ 请输入有效数字")
        return

    vip_money = float(middleware.bucketGet('s_dc', 'Vipmoney') or '1')
    coin_price = int(middleware.bucketGet('s_dc', 'coin') or '0')
    total_money = len(account_infos) * months * vip_money

    pay_config = vorto_utils.get_pay_config()
    available = []
    if pay_config.get('qr_pay_switch'):
        available.append(("扫码支付", "qrcode"))
    if pay_config.get('ma_pay_switch'):
        for pay_key, pay_name in (pay_config.get('pay_types') or {}).items():
            available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
    if coin_price > 0:
        available.append(("积分兑换", "coin"))

    if not available:
        sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
        return

    menu = (
        f"=====选择支付方式=====\n"
        f"📊 账号: {len(account_infos)}个\n"
        f"⏰ 时长: {months}月\n"
        f"💰 金额: {total_money}元\n"
        f"------------------------"
    )
    for i, (name, _) in enumerate(available, 1):
        menu += f"\n[{i}] {name}"
    menu += "\n------------------------\n回复数字选择\n=================="
    sender.reply(menu)

    pay_choice = sender.input(120000, 1, False)
    if not pay_choice or pay_choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        pay_idx = int(pay_choice) - 1
        if not (0 <= pay_idx < len(available)):
            sender.reply("❌ 无效选择")
            return
        _, pay_type = available[pay_idx]
    except ValueError:
        sender.reply("❌ 请输入有效数字")
        return

    if pay_type == 'qrcode':
        if not process_qrcode_payment(PLUGIN_CONFIG['name'], months, total_money):
            return
    elif pay_type.startswith('mapay_'):
        actual_pay_type = pay_type.replace('mapay_', '')
        if not process_mapay_payment(PLUGIN_CONFIG['name'], months, total_money, actual_pay_type):
            return
    elif pay_type == 'coin':
        total_coin = len(account_infos) * months * coin_price
        user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
        if user_coins < total_coin:
            sender.reply(
                f"=====积分不足=====\n"
                f"❌ 当前: {user_coins}\n"
                f"💰 需要: {total_coin}\n"
                f"=================="
            )
            return
        middleware.bucketSet('dd_sign_points', userid, str(user_coins - total_coin))

    success_list = []
    fail_list = []
    for item in account_infos:
        username = item['username']
        info = item['info']
        try:
            new_expire = vorto_utils.calculate_auth_time('s_dc_auth', username, months=months)
            middleware.bucketSet('s_dc_auth', username, new_expire)
            ql_ok = update_ql_env(username, info)
            if ql_ok:
                success_list.append(f"{mask_account(username)} → {new_expire}")
            else:
                fail_list.append(f"{mask_account(username)} 青龙同步失败")
        except Exception as e:
            fail_list.append(f"{mask_account(username)} {str(e)}")

    result = "=====授权完成=====\n"
    result += f"✅ 成功: {len(success_list)}个\n"
    if success_list:
        result += "\n".join(success_list) + "\n"
    if fail_list:
        result += f"❌ 失败: {len(fail_list)}个\n"
        result += "\n".join(fail_list) + "\n"
    if pay_type == 'coin':
        remaining = int(middleware.bucketGet('dd_sign_points', userid) or '0')
        result += f"🪙 剩余积分: {remaining}\n"
    result += "=================="
    sender.reply(result)

def generate_iframe_url(url):
    """将URL通过base64编码生成iframe页面链接"""
    try:
        encoded = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        iframe_url = f"https://metwhale.github.io?u={encoded}"
        return iframe_url
    except Exception as e:
        return url

def shorten_url(long_url):
    """缩短链接"""
    try:
        encoded_url = requests.utils.quote(long_url)
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
        response = requests.post('https://create.mrw.so/pageHome/createBySingle.htm', headers=headers, data=data, timeout=10)
        short_url = response.json().get('data')
        if short_url:
            return short_url
        return long_url
    except:
        return long_url

def process_mapay_payment(project, months, money, pay_type='alipay'):
    """码支付处理（vorto_utils）"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config.get('ma_pay_switch'):
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        out_trade_no = f"DC{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = (pay_config.get('pay_types') or {}).get(pay_type, '支付宝')

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
        while time.time() - start_time < 300:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                return True

        sender.reply("❌ 支付超时")
        return False
    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False


def process_qrcode_payment(project, months, money):
    """收款码支付处理"""
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
    except Exception:
        sender.reply("❌ 支付验证失败")
        return False


def update_ql_env(username, account_info):
    """更新青龙环境变量"""
    phone = account_info.get('username', '')
    password = account_info.get('password', '')
    
    if not phone or not password:
        sender.reply(f"更新青龙变量失败: 账号信息不完整")
        return False
        
    # 格式化变量值: 手机号#密码
    env_value = f"{phone}#{password}"

    auth_time = middleware.bucketGet('s_dc_auth', username) or '未授权'
    panel_group = (middleware.bucketGet('s_dc', 'panel_group') or '').strip()
    ql = _get_ql_client()
    return ql.update_env(
        username,
        env_value,
        f"大潮:{mask_account(username)}|到期:{auth_time}",
        group=panel_group,
    )

def delete_ql_env(username):
    """删除面板环境变量（青龙/呆呆面板 通用）"""
    ql = _get_ql_client()
    return ql.delete_env(username)


def _get_ql_client():
    """获取面板客户端，根据开关决定使用青龙或DumbPanel"""
    osname = middleware.bucketGet('s_dc', 'osname') or 'S_DC'
    qlname = middleware.bucketGet('s_dc', 'qlname') or ''
    use_dp = str(middleware.bucketGet('s_dc', 'use_daipanel') or '').lower() == 'true'

    if use_dp:
        if qlname:
            return vorto_utils.DumbPanelClient(osname, qlname)
        return vorto_utils.DumbPanelClient(osname)
    else:
        if qlname:
            return vorto_utils.QingLongClient(osname, qlname)
        return vorto_utils.QingLongClient(osname)


def check_auth_status():
    """按规范使用 vorto_utils 统一检测逻辑"""
    return vorto_utils.check_auth_status(
        's_dc', 's_dc_user', 's_dc_auth', 's_dc_token',
        '大潮', delete_ql_callback=delete_ql_env
    )

def ks_auth():
    """管理员授权菜单（按规范使用 vorto_utils）"""
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理员授权")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(
            sender, 's_dc_user', 's_dc_auth', 's_dc_token',
            update_ql_callback=update_ql_env
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender, 's_dc_user', 's_dc_auth', 's_dc_token',
            update_ql_callback=update_ql_env
        )
    else:
        sender.reply("❌ 无效的选择")


def show_tutorial():
    """显示大潮教程"""
    sender.reply(
        '=====大潮教程=====\n'
        '用户指令:\n'
        '1. 大潮登录 - 绑定账号\n'
        '2. 大潮查询 - 查询账号状态和红包\n'
        '3. 大潮管理 - 授权、删除、提交面板\n'
        '4. 大潮教程 - 查看说明\n'
        '------------------\n'
        '管理员指令:\n'
        '1. 大潮授权 - 批量授权\n'
        '2. 大潮检测 - 检测过期并清理\n'
        '3. 大潮红包推送 - 推送红包链接\n'
        '------------------\n'
        '绑定输入:\n'
        '按提示依次输入手机号和密码\n'
        '登录成功后可选择开启红包推送\n'
        '------------------\n'
        '使用流程:\n'
        '1. 发送"大潮登录"绑定账号\n'
        '2. 发送"大潮查询"查看状态\n'
        '3. 发送"大潮管理"授权账号\n'
        '4. 选择时长并完成支付\n'
        '=================='
    )


def main():
    """主入口"""
    msg = sender.getMessage()
    
    # 处理大潮登录
    if ('登录' in msg or '登陆' in msg) and ('大潮' in msg or 'dc' in msg.lower()):
        bind_account()
    # 处理大潮查询
    elif '查询' in msg and ('大潮' in msg or 'dc' in msg.lower()):
        query_accounts()
    # 处理大潮管理
    elif '管理' in msg and ('大潮' in msg or 'dc' in msg.lower()):
        manage_account()
    # 处理大潮授权
    elif '大潮授权' in msg:
        ks_auth()
    # 处理大潮检测
    elif '大潮检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 此功能仅限管理员使用")
            return
        
        sender.reply("🔍 正在检测所有账号状态...")
        result = check_auth_status()
        sender.reply(result)
    # 处理大潮红包推送
    elif '大潮红包推送' in msg or '红包推送' in msg:
        push_redpack_links()
    # 处理大潮教程
    elif '教程' in msg and ('大潮' in msg or 'dc' in msg.lower()):
        show_tutorial()
    # 定时任务 - 执行检测并清理过期账号
    elif sender.getImtype() == 'fake':
        try:
            middleware.notifyMasters(check_auth_status())
        except:
            pass
    elif msg.startswith('S_DC_'):  # 查询订单
        try:
            order_info = middleware.bucketGet('s_dc_order', msg)
            if not order_info:
                sender.reply("""
=====查询结果=====
❌ 未找到订单信息
------------------
请确认订单号是否正确
==================""")
            else:
                order_data = json.loads(order_info)
                sender.reply(f"""
=====订单详情=====
🔖 订单号: {msg}
💰 金额: {order_data.get('amount', '未知')}元
⏱️ 时长: {order_data.get('months', '未知')}个月
📊 状态: {'已支付' if order_data.get('status') == 'success' else '未支付'}
==================""")
        except Exception as e:
            sender.reply(f"""
=====查询异常=====
❌ 错误: {str(e)}
==================""")
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
