# [title: 店铛铛]
# [language: python]
# [class: 工具类]
# [service: 10086] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(店铛铛|ddd)(登录|登陆)$|^登(录|陆)(店铛铛|ddd)$|^(店铛铛|ddd)(查询|管理|授权|检测|提醒|教程)$|^(查询|管理|授权|检测|提醒|教程)(店铛铛|ddd)$]
# [cron: 5 8 * * *] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [open_source: false] 是否开源
# [icon: https://img.xxkx.de/file/9sJgODq0.png] 图标链接地址
# [version: 1.3] 版本号
# [public: true] 是否发布
# [price: 8.88] 上架价格
# [description: 店铛铛插件，必须走邀请才有入口：https://mallapps.jiudageapp.com/#/pages/subject/newcomerDebut?id=0&shardCode=NbcBNLbRz&unlockStatus=0&showNewbiePoster=1&platform=web&level=2<br>指令：店铛铛登录、管理、查询、授权、检测、提醒、教程<br>v1.0：初始版本]

import os
import json
import time
import hashlib
import random
import re
import base64
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode
import middleware

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_ddd_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_ddd', 'coin_key': 'dd_sign_points', 'name': '店铛铛'}
BASE_HOST = 'gw.jiudageapp.com'
BASE_URL = f'https://{BASE_HOST}'
API = {
    "pwd_login": f"{BASE_URL}/api/web/auth/pwdLogin",
    "member_info": f"{BASE_URL}/api/web/member/getMemberInfo",
    "member_center": f"{BASE_URL}/api/web/member/getMemberCenterInfo",
    "contrib_detail": f"{BASE_URL}/api/web/member/contributDetail/list",
    "ip_detail": f"{BASE_URL}/api/web/member/ipDetail/page",
}
PAY_TYPE_NAMES = {'alipay': '支付宝', 'wxpay': '微信支付', 'qqpay': 'QQ钱包'}

# [param: {"required":true, "key":"s_ddd.qlname", "bool":false, "placeholder":"Host丨ClientID丨ClientSecret", "name":"设置对接容器", "desc":"青龙容器参数用丨分割"}]
# [param: {"required":true, "key":"s_ddd.osname", "bool":false, "placeholder":"例:S_DDD", "name":"青龙变量名", "desc":"青龙容器内店铛铛的变量名"}]
# [param: {"required":true, "key":"s_ddd.Vipmoney", "bool":false, "placeholder":"例:0.88", "name":"上车价格", "desc":"上车价格(单位:元)/月"}]
# [param: {"required":true, "key":"s_ddd.coin", "bool":false, "placeholder":"不填为关闭", "name":"积分开通", "desc":"授权一个月需要多少积分"}]
# [param: {"required":true, "key":"s_ddd.zsm", "bool":false, "placeholder":"http://xxxx.co/xxx.jpg", "name":"收款方式", "desc":"收款码链接"}]
# [param: {"required":false, "key":"s_ddd.notify", "bool":false, "placeholder":"qq,wx,tb", "name":"通知渠道", "desc":"检测通知推送渠道"}]
# [param: {"required":false, "key":"s_ddd.notify_days", "bool":false, "placeholder":"3", "name":"提前提醒天数", "desc":"到期前多少天开始提醒"}]
# [param: {"required":true, "key":"s_ddd.ma_pay_switch", "bool":true, "placeholder":"", "name":"码支付功能", "desc":"开启后使用码支付"}]
# [param: {"required":false, "key":"s_ddd.default_version", "bool":false, "placeholder":"例:1.5.6", "name":"默认APP版本号", "desc":"用户登录时自动使用的版本号"}]
# [param: {"required":false, "key":"s_ddd.proxy_api", "bool":false, "placeholder":"http://your-proxy-api.com/get", "name":"代理API地址", "desc":"返回格式 ip:port"}]
# [param: {"required":false, "key":"s_ddd.invite_phone", "bool":false, "placeholder":"例:13800138000", "name":"邀请人手机号", "desc":"用户登录后需要验证邀请人信息"}]
# [param: {"required":false, "key":"s_ddd.invite_reward_days", "bool":false, "placeholder":"例:7", "name":"邀请赠送天数", "desc":"邀请验证通过后赠送的授权天数，默认7天"}]

def get_user_content():
    osname = middleware.bucketGet('s_ddd', 'osname') or 'S_DDD'
    qlname = middleware.bucketGet('s_ddd', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_ddd', 'Vipmoney') or '1')
    coin = middleware.bucketGet(PLUGIN_CONFIG['bucket'], PLUGIN_CONFIG['coin_key'])
    if not coin:
        coin = middleware.bucketGet('s_ddd', 'coin') or '0'
    default_version = middleware.bucketGet('s_ddd', 'default_version') or '1.5.6'
    proxy_api = middleware.bucketGet('s_ddd', 'proxy_api') or ''
    invite_phone = middleware.bucketGet('s_ddd', 'invite_phone') or ''
    invite_reward_days = int(middleware.bucketGet('s_ddd', 'invite_reward_days') or '7')
    return osname, qlname, '店铛铛管理', '店铛铛查询', '店铛铛登录', Vipmoney, int(coin), default_version, proxy_api, invite_phone, invite_reward_days

def mask_account(account):
    if not account or len(account) < 4:
        return account
    if account.isdigit() and len(account) == 11:
        return f"{account[:3]}****{account[7:]}"
    if len(account) <= 16:
        return f"{account[:4]}****{account[-4:]}"
    return f"{account[:8]}****{account[-8:]}"

def md5_hash(text):
    return hashlib.md5(text.encode()).hexdigest().upper()

def get_proxy(proxy_api, max_retries=3):
    if not proxy_api:
        return None
    for attempt in range(max_retries):
        try:
            resp = requests.get(proxy_api, timeout=8)
            if resp.status_code == 200:
                proxy_text = resp.text.strip()
                if proxy_text.startswith('http'):
                    return {'http': proxy_text, 'https': proxy_text}
                return {'http': f'http://{proxy_text}', 'https': f'http://{proxy_text}'}
        except:
            pass
        time.sleep(1 + attempt)
    return None

def get_headers(authorization, version):
    """构建请求头"""
    return {
        "Host": BASE_HOST,
        "authorization": authorization,
        "version": f"v{version}" if not version.startswith('v') else version,
        "platform": "Android",
        "user-agent": "okhttp/4.10.0",
        "accept-encoding": "gzip",
        "Content-Type": "application/json"
    }

# ============ 店铛铛API接口 ============

def ddd_pwd_login(phone, password):
    """账密登录"""
    _, _, _, _, _, _, _, default_version, proxy_api, _, _ = get_user_content()
    
    for attempt in range(3):
        try:
            headers = {
                "Host": BASE_HOST,
                "user-agent": "okhttp/4.10.0",
                "accept-encoding": "gzip",
                "version": f"v{default_version}",
                "platform": "Android",
                "Content-Type": "application/json"
            }
            
            proxies = get_proxy(proxy_api) if proxy_api else None
            login_data = {"phone": phone, "password": md5_hash(password)}
            resp = requests.post(API["pwd_login"], headers=headers, json=login_data, timeout=10, proxies=proxies)
            result = resp.json()
            
            if result.get("code") != 200:
                return False, None, None, result.get("message", "登录失败")
            
            token = result.get("result", {}).get("token")
            if not token:
                return False, None, None, "获取Token失败"
            
            headers["authorization"] = token
            resp = requests.post(API["member_info"], headers=headers, json={}, timeout=10, proxies=proxies)
            result = resp.json()
            
            if result.get("code") != 200:
                return False, token, None, result.get("message", "获取会员信息失败")
            
            return True, token, result.get("result", {}), None
            
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < 2:
                continue
            return False, None, None, "网络波动，请稍后重试"
        except:
            return False, None, None, "登录失败，请稍后重试"
    
    return False, None, None, "网络波动，请稍后重试"

def ddd_get_basic_member_info(authorization, version):
    """获取会员基本信息（phone, invitePhone等）"""
    try:
        _, _, _, _, _, _, _, _, proxy_api, _, _ = get_user_content()
        headers = get_headers(authorization, version)
        proxies = get_proxy(proxy_api) if proxy_api else None
        resp = requests.post(API['member_info'], headers=headers, json={}, timeout=20, proxies=proxies)
        
        if resp is None:
            return {"error": "请求失败，请重试"}
        
        data = resp.json()
        if data and data.get('success') and data.get('code') == 200:
            return data.get('result') or {}
        return {"error": data.get('message', '获取会员信息失败')}
    except Exception as e:
        return {"error": str(e)}

def ddd_get_member_info(authorization, version):
    """获取会员中心信息"""
    try:
        _, _, _, _, _, _, _, _, proxy_api, _, _ = get_user_content()
        headers = get_headers(authorization, version)
        proxies = get_proxy(proxy_api) if proxy_api else None
        resp = requests.post(API['member_center'], headers=headers, json={}, timeout=20, proxies=proxies)
        
        if resp is None:
            return {"error": "请求失败，请重试"}
        
        data = resp.json()
        if data and data.get('success') and data.get('code') == 200:
            return data.get('result') or {}
        return {"error": data.get('message', '获取会员信息失败')}
    except Exception as e:
        return {"error": str(e)}

def ddd_get_contrib_detail(authorization, version, page_size=5):
    """获取贡献值明细"""
    try:
        _, _, _, _, _, _, _, _, proxy_api, _, _ = get_user_content()
        headers = get_headers(authorization, version)
        proxies = get_proxy(proxy_api) if proxy_api else None
        
        url = f"{API['contrib_detail']}?pageNum=1&pageSize={page_size}&contributionType=1"
        resp = requests.get(url, headers=headers, timeout=20, proxies=proxies)
        
        data = resp.json()
        if data and data.get('success') and data.get('code') == 200:
            records = data.get('result', {}).get('records', [])
            return records[:page_size]
        return []
    except:
        return []

def ddd_get_ip_detail(authorization, version, page_size=5):
    """获取兑换值明细"""
    try:
        _, _, _, _, _, _, _, _, proxy_api, _, _ = get_user_content()
        headers = get_headers(authorization, version)
        proxies = get_proxy(proxy_api) if proxy_api else None
        
        date_month = datetime.now().strftime("%Y%m")
        request_body = {
            "dateMonth": date_month,
            "transactionTypeList": [1, 3],
            "pageNum": 1,
            "pageSize": page_size
        }
        resp = requests.post(API['ip_detail'], headers=headers, json=request_body, timeout=20, proxies=proxies)
        
        data = resp.json()
        if data and data.get('success') and data.get('code') == 200:
            records = data.get('result', {}).get('records', [])
            return records[:page_size]
        return []
    except:
        return []


# ============ 登录功能 ============

def bind_account():
    osname, _, _, _, _, _, _, default_version, _, _, _ = get_user_content()
    
    # 账密登录
    sender.reply(
        "=====店铛铛登录=====\n"
        "格式: 手机号#密码\n"
        "示例: 13800138000#123456\n"
        "------------------\n"
        "支持批量登录(换行分割)\n"
        "回复\"q\"退出\n"
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("⏰ 操作超时")
        return
    if input_text.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    # 按换行分割，支持批量
    lines = [line.strip() for line in input_text.split('\n') if line.strip() and '#' in line]
    if not lines:
        sender.reply("❌ 格式错误\n请输入: 手机号#密码")
        return
    
    total = len(lines)
    success_count = 0
    fail_count = 0
    need_auth_accounts = []  # 需要授权的账号列表
    
    if total > 1:
        sender.reply(f"🔄 检测到 {total} 个账号，开始批量登录...")
    
    for line in lines:
        parts = line.split('#', 1)
        if len(parts) < 2 or not parts[0].strip() or not parts[1].strip():
            fail_count += 1
            continue
        
        phone = parts[0].strip()
        password = parts[1].strip()
        
        if not phone.isdigit() or len(phone) != 11:
            sender.reply(f"❌ {phone} 手机号格式错误")
            fail_count += 1
            continue
        
        sender.reply(f"🔄 正在登录 {mask_account(phone)}... [{success_count + fail_count + 1}/{total}]")
        
        success, token, member_info, error_msg = ddd_pwd_login(phone, password)
        if not success:
            sender.reply(f"❌ {mask_account(phone)} 登录失败: {error_msg}")
            fail_count += 1
            continue
        
        # 保存账号（批量模式），传入密码用于后续存储
        need_auth = _save_account(phone, password, token, member_info, batch_mode=(total > 1))
        if need_auth:
            need_auth_accounts.append(phone)
        success_count += 1
    
    if total > 1:
        sender.reply(f"=====批量登录完成=====\n✅ 成功: {success_count}\n❌ 失败: {fail_count}\n==================")
        # 统一处理需要授权的账号
        if need_auth_accounts:
            sender.reply(f"📋 共 {len(need_auth_accounts)} 个账号需要授权")
            authorize_multiple_accounts(need_auth_accounts)

def _save_account(phone, password, token, member_info, batch_mode=False):
    """保存账密登录的账号
    batch_mode: 批量模式，不处理授权，返回是否需要授权
    """
    osname, qlname, _, _, _, _, _, default_version, _, invite_phone_config, invite_reward_days = get_user_content()

    # 保存到用户列表（使用全局 userid）
    current_value = middleware.bucketGet('s_ddd_user', userid)
    if not current_value:
        middleware.bucketSet('s_ddd_user', userid, str([phone]))
    else:
        accounts = eval(current_value)
        if phone not in accounts:
            accounts.append(phone)
            middleware.bucketSet('s_ddd_user', userid, str(accounts))
    
    # 保存账号信息（包含密码用于青龙变量）
    account_info = {
        "phone": phone,
        "password": password,
        "token": token,
        "version": default_version
    }
    middleware.bucketSet('s_ddd_token', phone, json.dumps(account_info))
    
    # 检查授权状态
    dqsj = datetime.now().strftime("%Y-%m-%d")
    accountVip = middleware.bucketGet('s_ddd_auth', phone)
    if accountVip and accountVip > dqsj:
        sender.reply(f"📱 {mask_account(phone)} 已授权，到期: {accountVip}")
        update_ql_env(phone, account_info)
        return False  # 不需要授权
    
    # 邀请人验证逻辑（仅配置了邀请人时才验证和赠送）
    if invite_phone_config:
        invite_phone_actual = member_info.get('invitePhone', '') if member_info else ''
        if invite_phone_actual == invite_phone_config:
            # 验证通过，检查是否已领取过首次登录赠送
            free_phones = middleware.bucketGet('s_ddd_free_phone', userid) or ''
            free_phone_list = [p.strip() for p in free_phones.split(',') if p.strip()]
            
            if phone not in free_phone_list:
                today_date = datetime.now().date()
                new_vip = str(today_date + timedelta(days=invite_reward_days))
                middleware.bucketSet('s_ddd_auth', phone, new_vip)
                
                free_phone_list.append(phone)
                middleware.bucketSet('s_ddd_free_phone', userid, ','.join(free_phone_list))
                
                update_ql_env(phone, account_info)
                
                sender.reply(
                    f"=====邀请验证通过=====\n"
                    f"📱 账号: {mask_account(phone)}\n"
                    f"🎁 已赠送{invite_reward_days}天授权\n"
                    f"📅 到期: {new_vip}\n"
                    f"=================="
                )
                return False  # 不需要授权
        else:
            # 验证失败，提示邀请人不匹配
            sender.reply(
                f"=====邀请人验证失败=====\n"
                f"❌ 邀请人手机号不匹配\n"
                f"📱 配置邀请人: {mask_account(invite_phone_config)}\n"
                f"📱 实际邀请人: {mask_account(invite_phone_actual) if invite_phone_actual else '无'}\n"
                f"=================="
            )
            # 邀请人不匹配，需要授权
            if batch_mode:
                return True  # 需要授权
            sender.reply(f"📋 {mask_account(phone)} 需要授权")
            authorize_multiple_accounts([phone])
            return False
    
    # 未配置邀请人，需要授权
    if batch_mode:
        return True  # 需要授权
    sender.reply(f"📋 {mask_account(phone)} 需要授权")
    authorize_multiple_accounts([phone])
    return False

def _save_ck_account(phone, authorization, version, member_info=None, batch_mode=False):
    """保存CK登录的账号
    member_info: 会员信息（包含phone, invitePhone等）
    batch_mode: 批量模式，不处理授权，返回是否需要授权
    """
    _, _, _, _, _, _, _, _, _, invite_phone_config, invite_reward_days = get_user_content()
    
    # 使用手机号作为账号标识
    account_key = phone
    
    # 保存到用户列表
    current_value = middleware.bucketGet('s_ddd_user', userid)
    if not current_value:
        middleware.bucketSet('s_ddd_user', userid, str([account_key]))
    else:
        accounts = eval(current_value)
        if account_key not in accounts:
            accounts.append(account_key)
            middleware.bucketSet('s_ddd_user', userid, str(accounts))
    
    # 保存账号信息
    account_info = {
        "phone": phone,
        "token": authorization,
        "version": version
    }
    middleware.bucketSet('s_ddd_token', account_key, json.dumps(account_info))
    
    # 检查授权状态
    dqsj = datetime.now().strftime("%Y-%m-%d")
    accountVip = middleware.bucketGet('s_ddd_auth', account_key)
    if accountVip and accountVip > dqsj:
        sender.reply(f"📱 {mask_account(phone)} 已授权，到期: {accountVip}")
        update_ql_env(account_key, account_info)
        return False  # 不需要授权
    
    # 邀请人验证逻辑（仅配置了邀请人时才验证和赠送）
    if invite_phone_config and member_info:
        invite_phone_actual = member_info.get('invitePhone', '')
        if invite_phone_actual == invite_phone_config:
            # 验证通过，检查是否已领取过首次登录赠送
            free_phones = middleware.bucketGet('s_ddd_free_phone', userid) or ''
            free_phone_list = [p.strip() for p in free_phones.split(',') if p.strip()]
            
            if phone not in free_phone_list:
                today_date = datetime.now().date()
                new_vip = str(today_date + timedelta(days=invite_reward_days))
                middleware.bucketSet('s_ddd_auth', account_key, new_vip)
                
                free_phone_list.append(phone)
                middleware.bucketSet('s_ddd_free_phone', userid, ','.join(free_phone_list))
                
                update_ql_env(account_key, account_info)
                
                sender.reply(
                    f"=====邀请验证通过=====\n"
                    f"📱 账号: {mask_account(phone)}\n"
                    f"🎁 已赠送{invite_reward_days}天授权\n"
                    f"📅 到期: {new_vip}\n"
                    f"=================="
                )
                return False  # 不需要授权
        else:
            # 验证失败，提示邀请人不匹配
            sender.reply(
                f"=====邀请人验证失败=====\n"
                f"❌ 邀请人手机号不匹配\n"
                f"📱 配置邀请人: {mask_account(invite_phone_config)}\n"
                f"📱 实际邀请人: {mask_account(invite_phone_actual) if invite_phone_actual else '无'}\n"
                f"=================="
            )
            # 邀请人不匹配，需要授权
            if batch_mode:
                return True  # 需要授权
            sender.reply(f"📋 {mask_account(phone)} 需要授权")
            authorize_multiple_accounts([account_key])
            return False
    
    # 未配置邀请人，需要授权
    if batch_mode:
        return True  # 需要授权
    sender.reply(f"📋 {mask_account(phone)} 需要授权")
    authorize_multiple_accounts([account_key])
    return False

# ============ 查询功能 ============

def query_accounts():
    if not uservalue:
        sender.reply(
            "=====未绑定账号=====\n"
            "❌ 未找到账号\n"
            "💡 发送 店铛铛登录 绑定\n"
            "=================="
        )
        return
    
    accounts = eval(uservalue)
    osname, _, _, _, _, _, _, default_version, _, _, _ = get_user_content()
    
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, account in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_ddd_auth', account)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        
        # 获取备注
        try:
            token_data = middleware.bucketGet('s_ddd_token', account)
            if token_data:
                info = json.loads(token_data)
                display_name = info.get('remark') or mask_account(info.get('phone') or account)
            else:
                display_name = mask_account(account)
        except:
            display_name = mask_account(account)
        
        account_list += f"\n[{i}]{display_name}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    try:
        if choice == '0':
            selected = accounts.copy()
        else:
            selected = [
                accounts[int(idx.strip()) - 1]
                for idx in choice.split(',')
                if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
            ]
        
        if not selected:
            sender.reply("❌ 未选择有效账号")
            return
        
        sender.reply(f"✅ 已选择 {len(selected)} 个账号，正在查询...")
        
        for i, account in enumerate(selected, 1):
            try:
                token_data = middleware.bucketGet('s_ddd_token', account)
                if not token_data:
                    sender.reply(f"=====账号信息[{i}/{len(selected)}]=====\n📱 账号: {mask_account(account)}\n❌ 账号数据丢失，请重新登录\n==================")
                    continue
                
                account_info = json.loads(token_data)
                auth_time = middleware.bucketGet('s_ddd_auth', account)
                
                if auth_time and auth_time >= str(datetime.now().date()):
                    auth_status = '已授权'
                else:
                    auth_status = '未授权'
                
                token = account_info.get('token', '')
                version = account_info.get('version', default_version)
                display_name = account_info.get('remark') or mask_account(account_info.get('phone') or account)
                
                # 获取会员信息
                member_info_text = ""
                record_text = ""
                
                if token:
                    info = ddd_get_member_info(token, version)
                    if 'error' not in info:
                        member_info_text = (
                            f"\n📊 贡献值: {info.get('contribution', 0)}"
                            f"\n💎 兑换值: {info.get('ipValue', 0)}"
                            f"\n📺 已看广告: {info.get('watchedVideoCount', 0)}/{info.get('videoCount', 0)}"
                        )
                    
                    # 获取贡献值明细
                    contrib_records = ddd_get_contrib_detail(token, version, 5)
                    if contrib_records:
                        record_text += "\n------------------\n📋 贡献值明细:"
                        for rec in contrib_records[:3]:
                            contrib_val = rec.get('contribution', 0)
                            create_time = rec.get('createTime', '')
                            record_text += f"\n  +{contrib_val} {create_time}"
                
                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 账号: {display_name}\n"
                    f"🏷 状态: {auth_status}\n"
                    f"📅 到期: {auth_time or '未授权'}{member_info_text}"
                    f"{record_text}\n"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"=====查询失败=====\n❌ 错误: {str(e)}\n==================")
        
        sender.reply("✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


# ============ 管理功能 ============

def manage_account():
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return
    
    accounts = eval(uservalue)
    
    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交青龙\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    # 构建账号列表
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, account in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_ddd_auth', account)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        
        try:
            info = json.loads(middleware.bucketGet('s_ddd_token', account))
            display_name = info.get('remark') or mask_account(info.get('phone') or account)
        except:
            display_name = mask_account(account)
        
        account_list += f"\n[{i}]{display_name}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    # 解析选择的账号
    if account_choice == '0':
        selected = accounts.copy()
    else:
        selected = [
            accounts[int(idx.strip()) - 1]
            for idx in account_choice.split(',')
            if idx.strip().isdigit() and 0 <= int(idx.strip()) - 1 < len(accounts)
        ]
    
    if not selected:
        sender.reply("❌ 未选择有效账号")
        return
    
    sender.reply(f"✅ 已选择 {len(selected)} 个账号")
    
    # 执行操作
    if choice == '1':
        authorize_multiple_accounts(selected)
    elif choice == '2':
        sender.reply("=====确认删除=====\n⚠️ 此操作不可恢复\n回复 y 确认删除\n==================")
        if sender.input(120000, 1, False).lower() == 'y':
            for account in selected:
                if account in accounts:
                    accounts.remove(account)
                middleware.bucketDel('s_ddd_token', account)
                middleware.bucketDel('s_ddd_auth', account)
                delete_ql_env(account)
            
            if accounts:
                middleware.bucketSet('s_ddd_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_ddd_user', userid)
            sender.reply(f"✅ 已删除 {len(selected)} 个账号")
        else:
            sender.reply("✅ 已取消")
    elif choice == '3':
        success = 0
        for account in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_ddd_token', account))
                auth_time = middleware.bucketGet('s_ddd_auth', account)
                if auth_time and auth_time >= str(datetime.now().date()):
                    if update_ql_env(account, account_info):
                        success += 1
            except:
                pass
        sender.reply(
            f"=====提交结果=====\n"
            f"✅ 成功: {success}个\n"
            f"❌ 失败: {len(selected) - success}个\n"
            f"=================="
        )

# ============ 授权功能 ============

def authorize_multiple_accounts(accounts):
    account_infos = []
    for account in accounts:
        try:
            account_infos.append({
                'account': account,
                'info': json.loads(middleware.bucketGet('s_ddd_token', account))
            })
        except:
            pass
    
    if not account_infos:
        sender.reply("❌ 没有有效账号")
        return
    
    sender.reply(
        f"✅ {len(account_infos)} 个有效账号\n"
        f"=====设置授权时长=====\n"
        f"请输入授权月数(如:1)\n"
        f"回复\"q\"退出\n"
        f"=================="
    )
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
        
        Vipmoney = float(middleware.bucketGet('s_ddd', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_ddd', 'coin') or '0')
        
        # 构建可用支付方式
        available = []
        ma_pay_switch = middleware.bucketGet('s_ddd', 'ma_pay_switch') or 'false'
        if ma_pay_switch.lower() == 'true' and middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'):
            for pt in (middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay').split(','):
                available.append((PAY_TYPE_NAMES.get(pt.strip(), pt.strip()), f"mapay_{pt.strip()}"))
        elif middleware.bucketGet('s_ddd', 'zsm'):
            available.append(("微信支付", "wxpay"))
        
        if coin > 0:
            available.append(("积分兑换", "coin"))
        
        if not available:
            sender.reply("❌ 未配置支付方式")
            return
        
        # 选择支付方式
        if len(available) == 1:
            payment_name, payment_type = available[0]
        else:
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
            
            pay_idx = int(pay_choice) - 1
            if 0 <= pay_idx < len(available):
                payment_name, payment_type = available[pay_idx]
            else:
                sender.reply("❌ 无效选择")
                return
        
        # 执行支付
        if payment_type == 'coin':
            for acc in account_infos:
                process_coin_payment(acc['account'], acc['info'], months, coin)
        elif payment_type.startswith('mapay_'):
            if handle_mapay_order(PLUGIN_CONFIG['name'], months, total_money, payment_type.replace('mapay_', '')):
                for acc in account_infos:
                    process_authorization(acc['account'], acc['info'], months)
        else:
            if pay_order(PLUGIN_CONFIG['name'], months, total_money):
                for acc in account_infos:
                    process_authorization(acc['account'], acc['info'], months)
    except ValueError:
        sender.reply("❌ 请输入有效数字")

def process_authorization(account, account_info, months):
    try:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_ddd_auth', account)
        if accountVip and accountVip > dqsj:
            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        new_expire = (start_date + timedelta(days=30 * months)).strftime("%Y-%m-%d")
        middleware.bucketSet('s_ddd_auth', account, new_expire)
        update_ql_env(account, account_info)
        
        display_name = account_info.get('remark') or mask_account(account_info.get('phone') or account)
        sender.reply(
            f"=====授权成功=====\n"
            f"📱 账号: {display_name}\n"
            f"📅 到期: {new_expire}\n"
            f"=================="
        )
        return True
    except Exception as e:
        sender.reply(f"授权异常: {str(e)}")
        return False

def process_coin_payment(account, account_info, months, coin):
    try:
        required = months * coin
        user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
        
        if user_coins < required:
            sender.reply(
                f"=====积分不足=====\n"
                f"❌ 当前: {user_coins}\n"
                f"💰 需要: {required}\n"
                f"=================="
            )
            return False
        
        middleware.bucketSet('dd_sign_points', userid, str(user_coins - required))
        if process_authorization(account, account_info, months):
            sender.reply(
                f"=====积分兑换成功=====\n"
                f"✅ 扣除: {required}\n"
                f"💰 剩余: {user_coins - required}\n"
                f"=================="
            )
            return True
        
        middleware.bucketSet('dd_sign_points', userid, str(user_coins))
        return False
    except Exception as e:
        sender.reply(f"积分兑换异常: {str(e)}")
        return False


# ============ 支付功能 ============

def generate_iframe_url(url):
    """将URL通过base64编码生成iframe页面链接"""
    try:
        encoded = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        iframe_url = f"https://metwhale.github.io?u={encoded}"
        return iframe_url
    except:
        return url

def generate_qrcode(url):
    """生成二维码图片"""
    QRCODE_API_URL = "https://qrcode.vorto.cn/api/qrcode/generate"
    QRCODE_API_KEY = "4jpC3Cgd0zA7Z3HTJ6aDfW9QjtzitDGI"
    
    try:
        response = requests.post(
            QRCODE_API_URL,
            json={"content": url},
            headers={"X-API-Key": QRCODE_API_KEY},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data', {}).get('url'):
                return result['data']['url']
    except:
        pass
    
    # 备用接口
    try:
        encoded_url = requests.utils.quote(url)
        return f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
    except:
        return None

def handle_mapay_order(project, months, money, pay_type=None):
    config = {
        'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
        'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
        'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
        'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or '',
        'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or ''
    }
    
    if not (config['gateway'] and config['pid'] and config['key']):
        sender.reply('❌ 码支付配置不完整')
        return False
    
    amount = round(float(money), 2)
    out_trade_no = f"DDD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
    selected_type = pay_type or 'alipay'
    
    sender.reply(
        f"===== 支付信息 =====\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {amount}元\n"
        f"💳 支付: {PAY_TYPE_NAMES.get(selected_type, selected_type)}\n"
        f"=================="
    )
    
    params = {
        'pid': config['pid'],
        'type': selected_type,
        'out_trade_no': out_trade_no,
        'notify_url': config['notify_url'],
        'return_url': config['return_url'],
        'name': f"{project}-{amount}",
        'money': str(amount),
        'param': userid
    }
    params = {k: v for k, v in params.items() if v}
    sign_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    params['sign'] = hashlib.md5((sign_str + config['key']).encode()).hexdigest().lower()
    params['sign_type'] = 'MD5'
    
    try:
        resp = requests.post(f"{config['gateway'].rstrip('/')}/mapi.php", data=params, timeout=10).json()
        if resp.get('code') != 1:
            sender.reply(f'❌ 创建订单失败: {resp.get("msg")}')
            return False
        
        trade_no = resp.get('trade_no')
        pay_url = f"{config['gateway'].rstrip('/')}/pay/{trade_no}"
        iframe_url = generate_iframe_url(pay_url)
        sender.reply('请扫描下方二维码完成支付:')
        sender.replyImage(generate_qrcode(iframe_url))
        sender.reply('输入"q"可取消')
        
        for _ in range(30):
            qresp = requests.get(
                f"{config['gateway'].rstrip('/')}/xpay/epay/api.php",
                params={
                    'act': 'order',
                    'pid': config['pid'],
                    'key': config['key'],
                    'out_trade_no': out_trade_no
                },
                timeout=10
            ).json()
            if qresp.get('code') == 1 and qresp.get('status') == 1:
                return True
            if sender.listen(5000) == 'q':
                sender.reply("✅ 已取消")
                return False
        
        sender.reply("❌ 支付超时")
        return False
    except Exception as e:
        sender.reply(f'❌ 支付异常: {str(e)}')
        return False

def pay_order(project, months, money):
    if float(money) == 0:
        sender.reply(
            f"=====授权成功=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: 免费\n"
            f"=================="
        )
        return True
    
    zsm = middleware.bucketGet('s_ddd', 'zsm')
    if not zsm:
        sender.reply('❌ 未配置收款码')
        return False
    
    sender.reply(
        f"=====微信扫码支付====\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)
    
    ddzf = sender.waitPay("q", 100000)
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
    except:
        sender.reply("❌ 支付验证失败")
        return False

# ============ 青龙操作 ============

def get_ql_token(host, client_id, client_secret):
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        resp = requests.get(url, timeout=10).json()
        if resp.get('code') == 200:
            return resp['data']['token']
        return None
    except:
        return None

def update_ql_env(account, account_info):
    phone = account_info.get('phone', '')
    password = account_info.get('password', '')
    version = account_info.get('version', '')
    if not phone or not password:
        return False
    
    # 构建环境变量值：账号#密码#版本号
    env_value = f"{phone}#{password}#{version}" if version else f"{phone}#{password}"
    
    qlconfig = middleware.bucketGet('s_ddd', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        ql_token = get_ql_token(host, client_id, client_secret)
        if not ql_token:
            return False
        
        headers = {'Authorization': f'Bearer {ql_token}'}
        osname = middleware.bucketGet('s_ddd', 'osname') or 'S_DDD'
        auth_time = middleware.bucketGet('s_ddd_auth', account) or '未授权'
        display_name = account_info.get('remark') or mask_account(account_info.get('phone') or account)
        
        # 查找现有环境变量（使用脱敏手机号搜索remarks）
        masked_account = mask_account(account)
        envs = requests.get(
            f'{host}/open/envs?searchValue={masked_account}',
            headers=headers,
            timeout=10
        ).json().get('data', [])
        env_id = next((e.get('id') for e in envs if e['name'] == osname), None)
        
        env_data = {
            'name': osname,
            'value': env_value,
            'remarks': f"店铛铛：{display_name}|用户:{userid}|到期:{auth_time}"
        }
        
        if env_id:
            env_data['id'] = env_id
            requests.put(f'{host}/open/envs', headers=headers, json=env_data, timeout=10)
            requests.put(f'{host}/open/envs/enable', headers=headers, json=[env_id], timeout=10)
        else:
            resp = requests.post(f'{host}/open/envs', headers=headers, json=[env_data], timeout=10).json()
            if resp.get('data'):
                new_id = resp['data'][0].get('_id') or resp['data'][0].get('id')
                if new_id:
                    requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id], timeout=10)
        return True
    except:
        return False

def delete_ql_env(account):
    qlconfig = middleware.bucketGet('s_ddd', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        ql_token = get_ql_token(host, client_id, client_secret)
        if not ql_token:
            return False
        
        headers = {'Authorization': f'Bearer {ql_token}'}
        osname = middleware.bucketGet('s_ddd', 'osname') or 'S_DDD'
        envs = requests.get(f'{host}/open/envs', headers=headers, timeout=10).json().get('data', [])
        
        for env in envs:
            if env['name'] == osname and account in env.get('remarks', ''):
                env_id = env.get('_id') or env.get('id')
                requests.delete(f'{host}/open/envs', headers=headers, json=[env_id], timeout=10)
                return True
        return False
    except:
        return False


# ============ 检测功能（含自动清理） ============

def check_auth_status():
    """检测授权状态并推送通知
    逻辑：到期时间-当前日期 > 提前天数，不推送
          到期时间-当前日期 <= 提前天数 且 > 0，推送提醒
          到期时间-当前日期 <= 0，清理账号
    """
    notify = middleware.bucketGet('s_ddd', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"
    
    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_ddd_user')
    if not all_users:
        return "❌ 没有用户"
    
    # 获取提前提醒天数配置，默认3天
    notify_days = int(middleware.bucketGet('s_ddd', 'notify_days') or '3')
    
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0
    
    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_ddd_user', user_id) or '[]')
            
            # 分类账号：需要提醒的和需要清理的
            to_notify = []  # 需要提醒的账号
            to_clean = []   # 需要清理的账号
            
            for acc in accounts:
                auth_time_str = middleware.bucketGet('s_ddd_auth', acc)
                try:
                    info = json.loads(middleware.bucketGet('s_ddd_token', acc))
                    display_name = info.get('remark') or mask_account(info.get('phone') or acc)
                except:
                    display_name = mask_account(acc)
                
                if not auth_time_str:
                    # 未授权，直接清理
                    to_clean.append({'phone': acc, 'name': display_name, 'auth_time': '未授权', 'days_left': 0})
                    continue
                
                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days
                    
                    if days_left <= 0:
                        # 已过期，清理
                        to_clean.append({'phone': acc, 'name': display_name, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        # 即将过期，提醒
                        to_notify.append({'phone': acc, 'name': display_name, 'auth_time': auth_time_str, 'days_left': days_left})
                    # days_left > notify_days 不做任何操作
                except:
                    # 日期格式错误，清理
                    to_clean.append({'phone': acc, 'name': display_name, 'auth_time': auth_time_str, 'days_left': 0})
            
            total += len(accounts)
            
            # 处理需要清理的账号
            if to_clean:
                for exp_acc in to_clean:
                    account = exp_acc['phone']
                    delete_ql_env(account)
                    middleware.bucketDel('s_ddd_token', account)
                    
                    if account in accounts:
                        accounts.remove(account)
                    
                    middleware.bucketDel('s_ddd_auth', account)
                    cleaned += 1
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet('s_ddd_user', user_id, str(accounts))
                else:
                    middleware.bucketDel('s_ddd_user', user_id)
            
            # 处理需要提醒的账号
            if to_notify:
                notify_list = "\n".join([
                    f"📱 {a['name']} 剩余{a['days_left']}天({a['auth_time']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====店铛铛账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"店铛铛管理\"续费\n"
                    f"=================="
                )
                for ch in channels:
                    try:
                        middleware.push(
                            imType=ch,
                            groupCode='',
                            userID=user_id,
                            title="",
                            content=msg
                        )
                        notified += 1
                    except:
                        pass
        except:
            pass
    
    return f"✅ 店铛铛检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"

# ============ 每日打卡提醒功能 ============

def daily_checkin_reminder():
    """每日提醒已授权的账号登录APP"""
    notify = middleware.bucketGet('s_ddd', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"
    
    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_ddd_user')
    if not all_users:
        return "❌ 没有用户"
    
    current_date = str(datetime.now().date())
    total_accounts, notified_users = 0, 0
    
    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_ddd_user', user_id) or '[]')
            
            # 筛选已授权的账号
            authorized_accounts = []
            for acc in accounts:
                auth_time = middleware.bucketGet('s_ddd_auth', acc)
                # 只提醒授权有效的账号
                if auth_time and auth_time >= current_date:
                    try:
                        info = json.loads(middleware.bucketGet('s_ddd_token', acc))
                        display_name = info.get('remark') or mask_account(info.get('phone') or acc)
                    except:
                        display_name = mask_account(acc)
                    
                    authorized_accounts.append({
                        'name': display_name,
                        'auth_time': auth_time
                    })
            
            total_accounts += len(authorized_accounts)
            
            # 只有已授权账号才推送提醒
            if authorized_accounts:
                account_list = "\n".join([
                    f"📱 {a['name']} (到期:{a['auth_time']})"
                    for a in authorized_accounts
                ])
                msg = (
                    f"=====🔔 店铛铛提醒=====\n"
                    f"👋 早上好！别忘了打卡哦~\n"
                    f"------------------\n"
                    f"📋 您的账号:\n{account_list}\n"
                    f"------------------\n"
                    f"📲 请登录APP完成每日任务\n"
                    f"===================="
                )
                for ch in channels:
                    try:
                        middleware.push(
                            imType=ch,
                            groupCode='',
                            userID=user_id,
                            title="",
                            content=msg
                        )
                        notified_users += 1
                    except:
                        pass
        except:
            pass
    
    return f"✅ 提醒完成，共 {total_accounts} 个有效账号，发送 {notified_users} 条通知"

# ============ 管理员授权 ============

def calculate_auth_time_by_days(account, days):
    """按天数计算授权时间
    Args:
        account: 账号
        days: 天数（正数增加，负数减少）
    Returns:
        新的授权到期日期字符串
    """
    try:
        current_auth = middleware.bucketGet('s_ddd_auth', account)
        
        if current_auth and datetime.strptime(current_auth, "%Y-%m-%d").date() > datetime.now().date():
            base_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
        else:
            base_date = datetime.now().date()
        
        new_date = base_date + timedelta(days=int(days))
        return str(new_date)
        
    except Exception as e:
        raise Exception(f"计算授权时间失败: {str(e)}")

def ks_auth():
    """管理员授权管理"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return
    
    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理员授权")
        return
    
    if choice == '1':
        admin_auth_all_accounts()
    elif choice == '2':
        admin_auth_by_user()
    else:
        sender.reply("❌ 无效的选择")

def admin_auth_all_accounts():
    """管理员一键授权所有用户的所有账号"""
    try:
        users = middleware.bucketAllKeys('s_ddd_user')
        if not users:
            sender.reply("❌ 未找到任何用户账号")
            return
        
        # 统计总账号数
        total_accounts = 0
        for user_id in users:
            accounts_str = middleware.bucketGet('s_ddd_user', user_id)
            if accounts_str and accounts_str != '[]':
                total_accounts += len(eval(accounts_str))
        
        sender.reply(
            f"=====授权所有用户=====\n"
            f"👥 用户数: {len(users)}\n"
            f"📊 账号数: {total_accounts}\n"
            f"------------------\n"
            f"请输入授权天数:\n"
            f"(正数增加天数，负数减少天数)\n"
            f"回复\"q\"退出\n"
            f"=================="
        )
        
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            days = int(days_input)
        except ValueError:
            sender.reply("❌ 无效的天数")
            return
        
        action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
        sender.reply(
            f"=====确认授权=====\n"
            f"👥 用户数: {len(users)}\n"
            f"📊 账号数: {total_accounts}\n"
            f"⏰ 操作: {action_text}\n"
            f"------------------\n"
            f"⚠️ 此操作影响所有用户\n"
            f"回复\"y\"确认\n"
            f"回复其他取消\n"
            f"=================="
        )
        
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() != 'y':
            sender.reply("✅ 已取消授权")
            return
        
        success_count = 0
        fail_count = 0
        
        for user_id in users:
            accounts_str = middleware.bucketGet('s_ddd_user', user_id)
            if not accounts_str or accounts_str == '[]':
                continue
            
            try:
                accounts = eval(accounts_str)
                for acc in accounts:
                    try:
                        token_info_str = middleware.bucketGet('s_ddd_token', acc)
                        if not token_info_str:
                            fail_count += 1
                            continue
                        
                        new_auth_time = calculate_auth_time_by_days(acc, days)
                        middleware.bucketSet('s_ddd_auth', acc, new_auth_time)
                        
                        # 同步青龙
                        try:
                            token_info = json.loads(token_info_str)
                            update_ql_env(acc, token_info)
                        except:
                            pass
                        
                        success_count += 1
                    except Exception as e:
                        fail_count += 1
            except:
                pass
        
        sender.reply(
            f"=====授权结果=====\n"
            f"✅ 成功: {success_count} 个账号\n"
            f"❌ 失败: {fail_count} 个账号\n"
            f"⏰ 操作: {action_text}\n"
            f"=================="
        )
        
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")

def admin_auth_by_user():
    """管理员按用户授权 - 手动输入用户ID，按天数授权"""
    try:
        sender.reply(
            "=====按用户授权=====\n"
            "请输入用户ID:\n"
            "回复\"q\"退出\n"
            "=================="
        )
        
        target_user_id = sender.input(120000, 1, False)
        if not target_user_id or target_user_id.lower() == 'q':
            sender.reply("✅ 已退出")
            return
        
        accounts_str = middleware.bucketGet('s_ddd_user', target_user_id)
        if not accounts_str or accounts_str == '[]':
            sender.reply(f"❌ 用户 {target_user_id} 没有绑定任何账号")
            return
        
        accounts = eval(accounts_str)
        
        account_list = f"=====用户 {target_user_id} 的账号=====\n[0] 选择全部账号\n"
        for i, acc in enumerate(accounts, 1):
            try:
                info = json.loads(middleware.bucketGet('s_ddd_token', acc))
                display_name = info.get('remark') or mask_account(info.get('phone') or acc)
            except:
                display_name = mask_account(acc)
            auth_time = middleware.bucketGet('s_ddd_auth', acc) or '未授权'
            account_list += f"[{i}] {display_name} - {auth_time}\n"
        
        account_list += "------------------\n支持多选，用逗号分隔\n回复\"q\"退出\n=================="
        
        sender.reply(account_list)
        account_choice = sender.input(120000, 1, False)
        
        if not account_choice or account_choice.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        selected_accounts = []
        if account_choice == '0':
            selected_accounts = accounts.copy()
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in account_choice.split(',') if idx.strip().isdigit()]
                for index in indices:
                    if 0 <= index < len(accounts):
                        selected_accounts.append(accounts[index])
            except:
                sender.reply("❌ 无效的选择格式")
                return
        
        if not selected_accounts:
            sender.reply("❌ 未选择任何账号")
            return
        
        sender.reply(
            f"已选择 {len(selected_accounts)} 个账号\n"
            f"请输入授权天数:\n"
            f"(正数增加天数，负数减少天数)\n"
            f"回复\"q\"退出\n"
            f"=================="
        )
        
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            days = int(days_input)
        except ValueError:
            sender.reply("❌ 无效的天数")
            return
        
        action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
        sender.reply(
            f"=====确认授权=====\n"
            f"📊 账号数: {len(selected_accounts)} 个\n"
            f"⏰ 操作: {action_text}\n"
            f"------------------\n"
            f"回复\"y\"确认\n"
            f"回复其他取消\n"
            f"=================="
        )
        
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() != 'y':
            sender.reply("✅ 已取消授权")
            return
        
        success_count = 0
        fail_count = 0
        
        for acc in selected_accounts:
            try:
                token_info_str = middleware.bucketGet('s_ddd_token', acc)
                if not token_info_str:
                    fail_count += 1
                    continue
                
                new_auth_time = calculate_auth_time_by_days(acc, days)
                middleware.bucketSet('s_ddd_auth', acc, new_auth_time)
                
                # 同步青龙
                try:
                    token_info = json.loads(token_info_str)
                    update_ql_env(acc, token_info)
                except:
                    pass
                
                success_count += 1
            except Exception as e:
                fail_count += 1
        
        sender.reply(
            f"=====授权结果=====\n"
            f"✅ 成功: {success_count} 个账号\n"
            f"❌ 失败: {fail_count} 个账号\n"
            f"⏰ 操作: {action_text}\n"
            f"=================="
        )
        
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")


# ============ 主函数入口 ============

def show_tutorial():
    """显示店铛铛教程"""
    tutorial = """=====店铛铛教程=====
📱 用户指令:
• 店铛铛登录 - 绑定店铛铛账号
• 店铛铛查询 - 查询账号状态和收益
• 店铛铛管理 - 授权/删除/提交青龙
• 店铛铛教程 - 查看本教程
------------------
🔧 管理员指令:
• 店铛铛授权 - 管理员按天数授权
• 店铛铛检测 - 检测过期账号并清理
• 店铛铛提醒 - 发送打卡提醒
------------------
💡 登录格式:
[1] 账密登录
📝 格式: 手机号#密码
� 示例:量 13812345678#password123
💡 账密登录会顶掉已登录的APP

[2] CK登录
📝 格式: Authorization#版本号
📝 示例: eyJhbGci...#1.5.6
💡 支持批量登录，每行一个CK
------------------
📝 账号获取方式:
1. 必须通过邀请链接才有活动页面，可联系管理员获取
2. 使用手机号注册账号
3. 设置登录密码
------------------
💰 功能说明:
• 账号绑定: 保存账号信息到系统
• 状态查询: 查看贡献值、兑换值等
• 授权管理: 付费使用插件功能
• 青龙提交: 自动提交到青龙容器
• 过期检测: 到期前提醒，过期自动清理
• 打卡提醒: 每日提醒已授权用户
------------------
🎯 使用流程:
1. 发送"店铛铛登录"绑定账号
2. 发送"店铛铛查询"查看账号状态
3. 发送"店铛铛管理"选择授权账号
4. 选择授权时长并完成支付
5. 系统自动提交到青龙容器
------------------
⚠️ 注意事项:
• 授权后才能使用自动任务
• 过期账号会被自动清理
• 支持微信支付和积分兑换
• 必须通过邀请进入活动页面
=================="""
    sender.reply(tutorial)

def main():
    msg = sender.getMessage()
    
    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('店铛铛' in msg or 'ddd' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('店铛铛' in msg or 'ddd' in msg.lower()):
        manage_account()
    elif '教程' in msg and ('店铛铛' in msg or 'ddd' in msg.lower()):
        show_tutorial()
    elif '店铛铛授权' in msg or 'ddd授权' in msg.lower():
        ks_auth()
    elif ('检测' in msg or '清理' in msg) and ('店铛铛' in msg or 'ddd' in msg.lower()):
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    elif '提醒' in msg and ('店铛铛' in msg or 'ddd' in msg.lower()):
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔔 正在发送提醒...")
        sender.reply(daily_checkin_reminder())
    elif sender.getImtype() == 'fake':
        # 定时任务 - 执行检测并清理过期账号，发送打卡提醒
        try:
            middleware.notifyMasters(check_auth_status())
            #daily_checkin_reminder()
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
