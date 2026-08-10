# [pin:true]
# [author: yueiqiu4523]
# [title: 白鲸鱼]
# [language: python]
# [class: 工具类]
# [service: 3116835832] 售后联系方式
# [disable:false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^^白鲸鱼登录$|^白鲸鱼登陆$|^登陆白鲸鱼$|^登录白鲸鱼$|^白鲸鱼查询$|^查询白鲸鱼$|^白鲸鱼管理$|^管理白鲸鱼$|^白鲸鱼清理$|^白鲸鱼授权$|^白鲸鱼教程$] 
# [cron: 0 8 * * *] cron定时，支持5位域和6位域
# [priority: 55] 优先级，数字越大表示优先级越高
# [platform: all] 适用的平台
# [open_source: false]是否开源
# [icon: https://www.yili.com/static/images/logo.png]图标链接
# [version: 1.5.1]版本号
# [public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 6.66] 上架价格
# [description: 白鲸鱼旧衣服回收插件<br>支持签到、查询可回收金额<br>1.使用手机号+密码登录<br>2.支持签到、查询可回收金额<br>1.2版本.就行了美化处理<br>1.5.1版本支持青龙/呆呆面板填在同一格子里面]

# [param: {"required":true,"key":"JQB.bjy.zsm","bool":false,"placeholder":"收款码地址","name":"收款码地址","desc":"赞赏码或收款码地址"}]
# [param: {"required":false,"key":"JQB.bjy.panel_config","bool":false,"placeholder":"http://面板地址丨AppKey丨AppSecret","name":"面板配置","desc":"支持青龙/呆呆面板格式：Host丨AppKey丨AppSecret 使用中文竖线丨分隔"}]
# [param: {"required":false,"key":"JQB.bjy.ql_host","bool":false,"placeholder":"http://127.0.0.1:5700","name":"【兼容旧版】青龙地址","desc":"若未配置上方面板配置，则使用此项（仅限青龙）"}]
# [param: {"required":false,"key":"JQB.bjy.ql_client_id","bool":false,"placeholder":"","name":"【兼容旧版】青龙应用ID","desc":""}]
# [param: {"required":false,"key":"JQB.bjy.ql_client_secret","bool":false,"placeholder":"","name":"【兼容旧版】青龙应用秘钥","desc":""}]
# [param: {"required":true,"key":"JQB.bjy.var_name","bool":false,"placeholder":"bjy","name":"环境变量名","desc":"面板内的环境变量名，如 bjy"}]
# [param: {"required":true,"key":"JQB.bjy.price","bool":false,"placeholder":"1","name":"上车价格","desc":"上车价格(单位:元)/30天"}]
# [param: {"required":true,"key":"JQB.bjy.coin","bool":false,"placeholder":"0","name":"积分开通","desc":"授权一个月的积分"}]
# [param: {"required":true,"key":"JQB.bjy.coin_bucket","bool":false,"placeholder":"dd_sign_points","name":"积分数据桶","desc":""}]
# [param: {"required":false,"key":"JQB.bjy.proxy_pool","bool":false,"placeholder":"http://代理池API","name":"代理池地址","desc":""}]

import re
from datetime import datetime, timedelta
import middleware
import urllib.parse
import urllib3
from decimal import Decimal
import requests
import time
import json
import hashlib
import uuid
import asyncio
import aiohttp
from functools import lru_cache
import traceback
import random

# 禁用SSL警告
urllib3.disable_warnings()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 代理配置
MAX_RETRIES = 3
IS_PROXY = False
PROXY_API = middleware.bucketGet('JQB.bjy', 'proxy_pool') or "http://代理池API"
proxy = None

def mask_phone(phone):
    if len(phone) != 11:
        return phone
    return phone[:3] + '****' + phone[7:]

def update_proxy():
    global proxy
    try:
        if not IS_PROXY:
            proxy = None
            return
        response = requests.get(PROXY_API, timeout=10)
        ip = response.text.strip()
        proxy = {'http': ip, 'https': ip}
    except Exception as e:
        print(f"代理获取失败: {str(e)}")
        proxy = None

def _send_request(method, url, **kwargs):
    global proxy
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            if IS_PROXY and not proxy:
                update_proxy()
            kwargs['timeout'] = kwargs.get('timeout', 15)
            kwargs['verify'] = False
            response = requests.request(
                method=method,
                url=url,
                proxies=proxy if IS_PROXY and proxy else None,
                **kwargs
            )
            response.raise_for_status()
            return response
        except (requests.exceptions.ProxyError, requests.exceptions.Timeout) as e:
            print(f"代理异常: {str(e)}")
            if IS_PROXY:
                update_proxy()
                attempts += 1
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {str(e)}")
            attempts += 1
            if attempts == MAX_RETRIES:
                raise

def extract_cash_value(cash_str):
    if isinstance(cash_str, (int, float)):
        return float(cash_str)
    match = re.search(r'(\d+\.\d+)|(\d+)', str(cash_str))
    if match:
        return float(match.group(0))
    return 0.0

def login(account_name, password):
    try:
        if not account_name or not password:
            return "账号或密码不能为空", None
            
        url = "https://www.52bjy.com/api/app/member.php"
        payload = {
            'action': "login",
            'username': account_name,
            'password': password,
            'app': "self",
            'sign': ""
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 11; SHARK KLE-A0 Build/KLEN2202130CN00MR4; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/29.09091)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'EnvConnection': "test",
        }

        response = _send_request('POST', url, data=payload, headers=headers)
        result = response.json()

        if result.get("message") != "登录成功":
            return f"登录失败: {result.get('message', '未知错误')}", None
            
        return f"{mask_phone(account_name)}", password
        
    except Exception as e:
        return f"登录异常: {str(e)}", None

def bind(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.bjy.user', key=userid)
    
    sender.reply(
        """=====白鲸鱼登录=====
📝 请输入登录参数:手机号#密码
说明: 支持批量，一个账号一行
示例：
    13888888888#password123
    13999999999#password456
=====================
⭐ 输入q退出操作"""
    )
    
    input_text = sender.input(120000, 10, True).strip()
    if not input_text or input_text.lower() == 'q':
        sender.reply('已取消操作')
        return
        
    accounts = []
    success_count = 0
    fail_count = 0
    
    lines = input_text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if '#' not in line:
            sender.reply(f"❌ 格式错误: {line} (缺少#分隔符)")
            fail_count += 1
            continue
            
        parts = line.split('#', 1)
        if len(parts) < 2:
            sender.reply(f"❌ 格式错误: {line} (缺少密码)")
            fail_count += 1
            continue
            
        phone = parts[0].strip()
        password = parts[1].strip()
        
        if not re.match(r'^1[3-9]\d{9}$', phone):
            sender.reply(f"❌ 手机号格式错误: {phone}")
            fail_count += 1
            continue
            
        username, valid_password = login(phone, password)
        if not valid_password:
            sender.reply(f'{username}')
            fail_count += 1
            continue
            
        try:
            account_data = {
                'password': valid_password,
                'account_name': phone
            }
            middleware.bucketSet('JQB.bjy.account', phone, json.dumps(account_data))
            
            if phone not in accounts:
                accounts.append(phone)
                success_count += 1
        except Exception as e:
            sender.reply(f"❌ 保存失败: {phone} - {str(e)}")
            fail_count += 1
    
    if accounts:
        existing_accounts = eval(uservalue or '[]')
        for account in accounts:
            if account not in existing_accounts:
                existing_accounts.append(account)
        middleware.bucketSet('JQB.bjy.user', userid, str(existing_accounts))
    
    result_msg = f"""=====绑定结果=====
✅ 成功绑定: {success_count}个账号
❌ 失败绑定: {fail_count}个账号
------------------
发送"白鲸鱼查询"查看状态
发送"白鲸鱼管理"管理账号
====================="""
    sender.reply(result_msg)

def query_balance(account_name):
    try:
        account_data = middleware.bucketGet('JQB.bjy.account', account_name)
        if not account_data:
            return "账号信息不存在", 0, 0
        
        account_info = json.loads(account_data)
        password = account_info.get('password')
        
        if not password:
            return "账号信息不完整", 0, 0
            
        url = "https://www.52bjy.com/api/app/member.php"
        payload = {
            'action': "login",
            'username': account_name,
            'password': password,
            'app': "self",
            'sign': ""
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 11; SHARK KLE-A0 Build/KLEN2202130CN00MR4; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/29.09091)",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'EnvConnection': "test",
        }

        response = _send_request('POST', url, data=payload, headers=headers)
        result = response.json()

        if result.get("message") != "登录成功":
            return f"登录失败: {result.get('message', '未知错误')}", 0, 0
            
        token = result["data"]["token"]
        
        url = "https://www.52bjy.com/api/app/user.php"
        params = {
            'action': 'userinfo',
            'app': 'self',
            'appkey': 'a9827e37ed2becd8',
            'auth': token,
            'is_pop': '0',
            'username': account_name,
            'version': '2'
        }
        
        response = _send_request('GET', url, params=params, headers=headers)
        result = response.json()
        
        if result.get('code') == 0:
            credit_to_cash = result.get('data', {}).get('credit_to_cash', '0元')
            cash_value = extract_cash_value(credit_to_cash)
            return cash_value, cash_value, 1
        elif 'data' in result and 'credit_to_cash' in result['data']:
            credit_to_cash = result['data']['credit_to_cash']
            cash_value = extract_cash_value(credit_to_cash)
            return cash_value, cash_value, 1
        else:
            error_msg = result.get('message', '未知错误')
            return f"查询失败: {error_msg}", 0, 0
        
    except Exception as e:
        return f"查询异常: {str(e)}", 0, 0

# ==================== 面板配置获取 ====================
def get_panel_config():
    """
    获取面板配置，返回 (host, app_key, app_secret)
    优先使用新的 panel_config 参数，兼容旧的青龙三个独立参数
    """
    # 尝试新配置
    config_str = middleware.bucketGet('JQB.bjy', 'panel_config')
    if config_str and '丨' in config_str:
        parts = config_str.split('丨', 2)
        if len(parts) == 3:
            host = parts[0].strip()
            app_key = parts[1].strip()
            app_secret = parts[2].strip()
            if host and app_key and app_secret:
                return host, app_key, app_secret
    # 兼容旧版青龙配置
    host = middleware.bucketGet('JQB.bjy', 'ql_host')
    client_id = middleware.bucketGet('JQB.bjy', 'ql_client_id')
    client_secret = middleware.bucketGet('JQB.bjy', 'ql_client_secret')
    if host and client_id and client_secret:
        print("警告: 使用旧的青龙配置，建议迁移到新的 panel_config 格式(Host丨AppKey丨AppSecret)")
        return host, client_id, client_secret
    return None, None, None

# ==================== 青龙面板API ====================
def get_qinglong_token(host, app_key, app_secret):
    """获取青龙面板token"""
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}open/auth/token?client_id={app_key}&client_secret={app_secret}"
        response = requests.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('token')
    except Exception as e:
        print(f"获取青龙token失败: {str(e)}")
    return None

def add_to_qinglong(host, token, env_data):
    """添加或更新青龙环境变量，返回环境变量ID"""
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}open/envs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        # 查询是否已存在相同name且remarks包含标识的变量
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code != 200:
            return None
        envs = response.json().get('data', [])
        exists_id = None
        # 从remarks中提取手机号（已打码）和用户ID
        match = re.search(r'账号([^丨]+)丨用户:([^丨]+)', env_data['remarks'])
        account_phone_mask = match.group(1) if match else None
        user_id = match.group(2) if match else None

        for env in envs:
            if env.get('name') != env_data['name']:
                continue
            env_remarks = env.get('remarks', '')
            if account_phone_mask and user_id:
                if account_phone_mask in env_remarks and user_id in env_remarks:
                    exists_id = env.get('id')
                    break
            else:
                # 降级匹配
                if env_data.get('remarks') in env_remarks:
                    exists_id = env.get('id')
                    break

        if exists_id:
            # 更新
            update_url = f"{host}open/envs"
            env_data['id'] = exists_id
            response = requests.put(update_url, headers=headers, json=env_data, verify=False)
            if response.status_code == 200:
                return exists_id
        else:
            # 新增（需包装为数组）
            response = requests.post(url, headers=headers, json=[env_data], verify=False)
            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get('data') and len(resp_data['data']) > 0:
                    return resp_data['data'][0]['id']
    except Exception as e:
        print(f"青龙添加环境变量失败: {str(e)}")
    return None

def delete_qinglong_env(host, token, env_id):
    """删除青龙环境变量"""
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}open/envs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        data = [int(env_id)]
        response = requests.delete(url, headers=headers, json=data, verify=False)
        return response.status_code == 200
    except Exception as e:
        print(f"删除青龙环境变量失败: {str(e)}")
        return False

# ==================== 呆呆面板API ====================
def get_daidai_token(host, app_key, app_secret):
    """获取呆呆面板token"""
    try:
        if not host.endswith('/'):
            host += '/'
        url = f"{host}api/open-api/token"
        headers = {"Content-Type": "application/json"}
        payload = {"app_key": app_key, "app_secret": app_secret}
        response = requests.post(url, json=payload, timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", {}).get("access_token")
    except Exception as e:
        print(f"获取呆呆token失败: {str(e)}")
    return None

def _daidai_request(method, host, token, url_suffix, **kwargs):
    """呆呆面板请求封装，自动处理401刷新token"""
    if not host.endswith('/'):
        host += '/'
    full_url = host + url_suffix.lstrip('/')
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = f"Bearer {token}"
    headers['Content-Type'] = 'application/json'
    resp = requests.request(method, full_url, headers=headers, timeout=10, verify=False, **kwargs)
    if resp.status_code == 401:
        # token过期，重新获取并重试一次
        new_token = get_daidai_token(host, *get_panel_config()[1:])  # 重新获取token
        if new_token:
            headers['Authorization'] = f"Bearer {new_token}"
            resp = requests.request(method, full_url, headers=headers, timeout=10, verify=False, **kwargs)
    return resp

def add_to_daidai(host, token, env_data):
    """添加或更新呆呆环境变量，返回环境变量ID"""
    try:
        # 搜索是否存在相同name且remarks包含标识的变量
        search_url = f"api/envs?keyword={env_data['name']}&page_size=100"
        search_resp = _daidai_request('GET', host, token, search_url)
        if search_resp.status_code != 200:
            return None
        search_result = search_resp.json()
        envs = search_result if isinstance(search_result, list) else search_result.get('data', [])

        match = re.search(r'账号([^丨]+)丨用户:([^丨]+)', env_data['remarks'])
        account_phone_mask = match.group(1) if match else None
        user_id = match.group(2) if match else None

        exists_id = None
        for env in envs:
            if env.get('name') != env_data['name']:
                continue
            env_remarks = env.get('remarks', '')
            if account_phone_mask and user_id:
                if account_phone_mask in env_remarks and user_id in env_remarks:
                    exists_id = env.get('id')
                    break
            else:
                if env_data.get('remarks') in env_remarks:
                    exists_id = env.get('id')
                    break

        data = env_data.copy()
        data['enabled'] = True

        if exists_id:
            # 更新
            update_url = f"api/envs/{exists_id}"
            update_resp = _daidai_request('PUT', host, token, update_url, json=data)
            if update_resp.status_code == 200:
                return exists_id
        else:
            # 新增
            add_url = "api/envs"
            add_resp = _daidai_request('POST', host, token, add_url, json=data)
            if add_resp.status_code == 200:
                resp_data = add_resp.json()
                return resp_data.get('data', {}).get('id')
    except Exception as e:
        print(f"呆呆添加环境变量失败: {str(e)}")
    return None

def delete_daidai_env(host, token, env_id):
    """删除呆呆环境变量"""
    try:
        del_url = f"api/envs/{env_id}"
        del_resp = _daidai_request('DELETE', host, token, del_url)
        return del_resp.status_code == 200
    except Exception as e:
        print(f"删除呆呆环境变量失败: {str(e)}")
        return False

# ==================== 统一面板操作 ====================
def add_to_panel(env_data):
    """
    统一添加/更新环境变量，自动识别青龙或呆呆
    返回带前缀的环境变量ID，格式 "ql:123" 或 "dd:456"
    """
    host, app_key, app_secret = get_panel_config()
    if not host:
        return None
    # 尝试青龙
    ql_token = get_qinglong_token(host, app_key, app_secret)
    if ql_token:
        env_id = add_to_qinglong(host, ql_token, env_data)
        if env_id:
            return f"ql:{env_id}"
    # 尝试呆呆
    dd_token = get_daidai_token(host, app_key, app_secret)
    if dd_token:
        env_id = add_to_daidai(host, dd_token, env_data)
        if env_id:
            return f"dd:{env_id}"
    return None

def delete_from_panel(env_id_with_prefix):
    """
    统一删除环境变量，根据前缀调用对应面板的删除函数
    """
    if not env_id_with_prefix:
        return False
    parts = env_id_with_prefix.split(':', 1)
    if len(parts) != 2:
        return False
    panel_type, env_id = parts
    host, app_key, app_secret = get_panel_config()
    if not host:
        return False
    if panel_type == 'ql':
        token = get_qinglong_token(host, app_key, app_secret)
        if token:
            return delete_qinglong_env(host, token, env_id)
    elif panel_type == 'dd':
        token = get_daidai_token(host, app_key, app_secret)
        if token:
            return delete_daidai_env(host, token, env_id)
    return False

# ==================== 业务功能 ====================
def query(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.bjy.user', key=userid)
    today_date = datetime.now().date()
    today_time = str(today_date)
    
    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply(
            """\n=====白鲸鱼账号查询=====
❌ 未找到任何账号
------------------
💡 发送"白鲸鱼登录"绑定账号
==================="""
        )
        return

    if len(accounts) > 1:
        menu = """=====请选择查询账号=====
[0] 查询全部账号
"""
        for idx, acc in enumerate(accounts, 1):
            menu += f"[{idx}] {mask_phone(acc)}\n"
        menu += "=======================\n⚠️ 请回复数字序号(输入q退出)"
        sender.reply(menu)

        choice = sender.input(30000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply('已取消查询')
            return
            
        if choice == '0':
            target_accounts = accounts
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    target_accounts = [accounts[index]]
                else:
                    sender.reply('选择超出范围，已取消查询')
                    return
            except:
                sender.reply('格式错误，已取消查询')
                return
    else:
        target_accounts = accounts

    for account in target_accounts:
        try:
            account_auth = middleware.bucketGet('JQB.bjy.auth', account)
            auth_status = f"⏰ 授权到期: {account_auth}" if account_auth and account_auth >= today_time else "❌ 未授权"
            
            total_balance, withdraw_balance, status = query_balance(account)
            if status == 0:
                sender.reply(f'【{mask_phone(account)}】{total_balance}')
                continue

            sender.reply(
                f"""=====账号详情=====
📱 账号: {mask_phone(account)}
{auth_status}
💮 可回收金额: {total_balance}灵石💮
==================="""
            )
        except Exception as e:
            sender.reply(f'【{mask_phone(account)}】查询出错: {str(e)}')

def sign_in(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.bjy.user', key=userid)
    today_date = datetime.now().date()
    today_time = str(today_date)
    
    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply('❌ 未绑定任何账号')
        return
        
    for account in accounts:
        try:
            auth = middleware.bucketGet('JQB.bjy.auth', account)
            if not auth or auth < today_time:
                sender.reply(f'【{mask_phone(account)}】未授权，无法签到')
                continue
                
            account_data = middleware.bucketGet('JQB.bjy.account', account)
            if not account_data:
                sender.reply(f'【{mask_phone(account)}】账号信息不存在')
                continue
                
            account_info = json.loads(account_data)
            password = account_info.get('password')
            
            if not password:
                sender.reply(f'【{mask_phone(account)}】账号信息不完整')
                continue
                
            login_url = "https://www.52bjy.com/api/app/member.php"
            payload = {
                'action': "login",
                'username': account,
                'password': password,
                'app': "self",
                'sign': ""
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (Linux; Android 11; SHARK KLE-A0 Build/KLEN2202130CN00MR4; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 uni-app Html5Plus/1.0 (Immersed/29.09091)",
                'Connection': "Keep-Alive",
                'Accept-Encoding': "gzip",
                'EnvConnection': "test",
            }

            login_response = _send_request('POST', login_url, data=payload, headers=headers)
            login_result = login_response.json()

            if login_result.get("message") != "登录成功":
                sender.reply(f"【{mask_phone(account)}】登录失败: {login_result.get('message', '未知错误')}")
                continue
                
            token = login_result["data"]["token"]
            
            sign_url = f"https://www.52bjy.com/api/app/user.php?action=qiandao&app=self&auth={token}&username={account}"
            
            sign_response = _send_request('GET', sign_url, headers=headers)
            sign_result = sign_response.json()
            
            if sign_result.get('message') == "签到成功":
                query_url = "https://www.52bjy.com/api/app/user.php"
                params = {
                    'action': 'userinfo',
                    'app': 'self',
                    'appkey': 'a9827e37ed2becd8',
                    'auth': token,
                    'is_pop': '0',
                    'username': account,
                    'version': '2'
                }
                
                query_response = _send_request('GET', query_url, params=params, headers=headers)
                query_result = query_response.json()
                
                if query_result.get('code') == 0:
                    credit_to_cash = query_result.get('data', {}).get('credit_to_cash', '0元')
                    cash_value = extract_cash_value(credit_to_cash)
                    sender.reply(f"【{mask_phone(account)}】签到成功，当前可回收金额: {cash_value}元")
                elif 'data' in query_result and 'credit_to_cash' in query_result['data']:
                    credit_to_cash = query_result['data']['credit_to_cash']
                    cash_value = extract_cash_value(credit_to_cash)
                    sender.reply(f"【{mask_phone(account)}】签到成功，当前可回收金额: {cash_value}元")
                else:
                    error_msg = query_result.get('message', '未知错误')
                    sender.reply(f"【{mask_phone(account)}】签到成功，但查询金额失败: {error_msg}")
            else:
                error_msg = sign_result.get('message', '未知错误')
                sender.reply(f"【{mask_phone(account)}】签到失败: {error_msg}")
                
        except Exception as e:
            sender.reply(f'【{mask_phone(account)}】签到失败: {str(e)}')

def manage_accounts(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.bjy.user', key=userid)
    
    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply("""=====账号管理=====
❌ 未找到任何账号
------------------
💡 发送"白鲸鱼登录"绑定账号
====================""")
        return

    menu = """=====账号管理=====
[1] 授权所有账号
[2] 删除账号
[3] 选择账号授权
------------------
请回复数字选择操作"""
    sender.reply(menu)
    
    choice = sender.input(30000, 1, False)
    if not choice:
        return sender.reply('操作超时')
        
    if choice == '1':
        authorize_accounts(sender, accounts)
    elif choice == '2':
        delete_account(sender)
    elif choice == '3':
        select_accounts_authorize(sender, accounts)
    else:
        sender.reply('无效的选择')

def delete_account(sender):
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    userid = sender.getUserID()
    uservalue = middleware.bucketGet(bucket='JQB.bjy.user', key=userid)
    
    accounts = eval(uservalue or '[]')
    if not accounts:
        return sender.reply('❌ 无账号可删除')
        
    if len(accounts) > 1:
        menu = "=====选择要删除的账号=====\n"
        for idx, acc in enumerate(accounts, 1):
            menu += f"[{idx}] {mask_phone(acc)}\n"
        menu += "=======================\n⚠️ 回复数字序号(输入q退出)"
        sender.reply(menu)

        choice = sender.input(30000, 1, False)
        if not choice or choice.lower() == 'q':
            return sender.reply('已取消')
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(accounts):
                account = accounts[index]
                
                confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
📱 账号: {mask_phone(account)}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                sender.reply(confirm_msg)
                
                confirm = sender.input(30000, 1, False)
                if confirm.lower() != 'y':
                    return sender.reply('✅ 已取消删除操作')
                
                # 删除面板中的环境变量
                env_id_with_prefix = middleware.bucketGet('JQB.bjy.env_id', account)
                if env_id_with_prefix:
                    delete_from_panel(env_id_with_prefix)
                
                middleware.bucketDel('JQB.bjy.account', account)
                middleware.bucketDel('JQB.bjy.auth', account)
                middleware.bucketDel('JQB.bjy.env_id', account)
                
                accounts.pop(index)
                middleware.bucketSet('JQB.bjy.user', userid, str(accounts))
                sender.reply(f'✅ 已删除账号: {mask_phone(account)}')
            else:
                sender.reply('选择超出范围')
        except:
            sender.reply('输入错误')
    else:
        account = accounts[0]
        
        confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
📱 账号: {mask_phone(account)}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
        sender.reply(confirm_msg)
        
        confirm = sender.input(30000, 1, False)
        if confirm.lower() != 'y':
            return sender.reply('✅ 已取消删除操作')
        
        env_id_with_prefix = middleware.bucketGet('JQB.bjy.env_id', account)
        if env_id_with_prefix:
            delete_from_panel(env_id_with_prefix)
        
        middleware.bucketDel('JQB.bjy.account', account)
        middleware.bucketDel('JQB.bjy.auth', account)
        middleware.bucketDel('JQB.bjy.env_id', account)
        middleware.bucketSet('JQB.bjy.user', userid, '[]')
        sender.reply(f'✅ 已删除账号: {mask_phone(account)}')

def authorize_accounts(sender, accounts):
    if not accounts:
        return sender.reply('❌ 无账号可授权')
    
    account_list = "\n".join([f"  - {mask_phone(acc)}" for acc in accounts])
    sender.reply(f"""=====即将授权以下账号=====
{account_list}
------------------""")
    
    coin_bucket = middleware.bucketGet('JQB.bjy', 'coin_bucket') or 'dd_sign_points'
    coin_price = int(middleware.bucketGet('JQB.bjy', 'coin') or '0')
    price = Decimal(middleware.bucketGet('JQB.bjy', 'price') or '1')
    
    menu = f"""=====授权方式选择=====
[1] 微信支付 ({price}元/账号/月)
[2] 积分支付 ({coin_price}积分/账号/月)
------------------
请回复数字选择方式"""
    sender.reply(menu)
    
    choice = sender.input(30000, 1, False)
    if not choice or choice not in ['1', '2']:
        return sender.reply('已取消')
        
    sender.reply("请输入授权月数:")
    months = sender.input(30000, 1, False)
    if not months:
        return sender.reply('输入超时')
        
    try:
        months = int(months)
        if months <= 0:
            return sender.reply('月数必须大于0')
            
        var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
            
        if choice == '1':
            amount = price * months * len(accounts)
            if process_payment(amount, months * 30, sender):
                today_date = datetime.now().date()
                today_time = str(today_date)
                for account in accounts:
                    # 获取原有授权时间（如果有）
                    auth = middleware.bucketGet('JQB.bjy.auth', account)
                    if not auth or auth < today_time:
                        auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                    else:
                        auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')
                    
                    middleware.bucketSet('JQB.bjy.auth', account, auth_time)
                    
                    # 添加到面板
                    account_data = middleware.bucketGet('JQB.bjy.account', account)
                    if account_data:
                        account_info = json.loads(account_data)
                        password = account_info.get('password')
                        
                        if password:
                            remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                            env_data = {
                                "name": var_name,
                                "value": f"{account}#{password}",
                                "remarks": remarks
                            }
                            env_id_with_prefix = add_to_panel(env_data)
                            if env_id_with_prefix:
                                middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                
                sender.reply(f'✅ 已授权 {len(accounts)} 个账号 {months} 个月')
        elif choice == '2':
            user_coin = Decimal(middleware.bucketGet(coin_bucket, sender.getUserID()) or '0')
            need_coin = coin_price * months * len(accounts)
            if user_coin < need_coin:
                return sender.reply(f'❌ 积分不足，需要{need_coin}，当前有{user_coin}')
                
            new_coin = user_coin - need_coin
            middleware.bucketSet(coin_bucket, sender.getUserID(), str(new_coin))
            today_date = datetime.now().date()
            today_time = str(today_date)
            for account in accounts:
                auth = middleware.bucketGet('JQB.bjy.auth', account)
                if not auth or auth < today_time:
                    auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                else:
                    auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')
                
                middleware.bucketSet('JQB.bjy.auth', account, auth_time)
                
                account_data = middleware.bucketGet('JQB.bjy.account', account)
                if account_data:
                    account_info = json.loads(account_data)
                    password = account_info.get('password')
                    
                    if password:
                        remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                        env_data = {
                            "name": var_name,
                            "value": f"{account}#{password}",
                            "remarks": remarks
                        }
                        env_id_with_prefix = add_to_panel(env_data)
                        if env_id_with_prefix:
                            middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
            
            sender.reply(
                f"""✅ 已用 {need_coin} 积分授权 {len(accounts)} 个账号 {months} 个月
剩余积分: {new_coin}"""
            )
            
    except Exception as e:
        sender.reply(f'❌ 授权失败: {str(e)}')

def select_accounts_authorize(sender, accounts):
    if not accounts:
        return sender.reply('❌ 无账号可授权')
    
    menu = "=====选择要授权的账号=====\n"
    for idx, acc in enumerate(accounts, 1):
        menu += f"[{idx}] {mask_phone(acc)}\n"
    menu += "=======================\n⚠️ 回复数字序号(多个用逗号分隔, 输入q退出)"
    sender.reply(menu)
    
    choice_str = sender.input(30000, 1, False)
    if not choice_str or choice_str.lower() == 'q':
        return sender.reply('已取消授权操作')
    
    try:
        selected_indexes = [int(idx.strip()) for idx in choice_str.split(',')]
        selected_accounts = []
        
        for idx in selected_indexes:
            if 1 <= idx <= len(accounts):
                selected_accounts.append(accounts[idx-1])
            else:
                sender.reply(f"❌ 无效的序号: {idx}，已跳过")
        
        if not selected_accounts:
            return sender.reply('❌ 未选择有效账号')
        
        account_list = "\n".join([f"  - {mask_phone(acc)}" for acc in selected_accounts])
        sender.reply(f"""=====已选择以下账号=====
{account_list}
------------------""")
        
        authorize_selected_accounts(sender, selected_accounts)
        
    except Exception as e:
        sender.reply(f'❌ 选择失败: {str(e)}')

def authorize_selected_accounts(sender, selected_accounts):
    coin_bucket = middleware.bucketGet('JQB.bjy', 'coin_bucket') or 'dd_sign_points'
    coin_price = int(middleware.bucketGet('JQB.bjy', 'coin') or '0')
    price = Decimal(middleware.bucketGet('JQB.bjy', 'price') or '1')
    
    menu = f"""=====授权方式选择=====
[1] 微信支付 ({price}元/账号/月)
[2] 积分支付 ({coin_price}积分/账号/月)
------------------
请回复数字选择方式"""
    sender.reply(menu)
    
    choice = sender.input(30000, 1, False)
    if not choice or choice not in ['1', '2']:
        return sender.reply('已取消')
        
    sender.reply("请输入授权月数:")
    months = sender.input(30000, 1, False)
    if not months:
        return sender.reply('输入超时')
        
    try:
        months = int(months)
        if months <= 0:
            return sender.reply('月数必须大于0')
            
        var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
            
        if choice == '1':
            amount = price * months * len(selected_accounts)
            if process_payment(amount, months * 30, sender):
                today_date = datetime.now().date()
                today_time = str(today_date)
                for account in selected_accounts:
                    auth = middleware.bucketGet('JQB.bjy.auth', account)
                    if not auth or auth < today_time:
                        auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                    else:
                        auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')
                    
                    middleware.bucketSet('JQB.bjy.auth', account, auth_time)
                    
                    account_data = middleware.bucketGet('JQB.bjy.account', account)
                    if account_data:
                        account_info = json.loads(account_data)
                        password = account_info.get('password')
                        
                        if password:
                            remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                            env_data = {
                                "name": var_name,
                                "value": f"{account}#{password}",
                                "remarks": remarks
                            }
                            env_id_with_prefix = add_to_panel(env_data)
                            if env_id_with_prefix:
                                middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                
                sender.reply(f'✅ 已授权 {len(selected_accounts)} 个账号 {months} 个月')
        elif choice == '2':
            user_coin = Decimal(middleware.bucketGet(coin_bucket, sender.getUserID()) or '0')
            need_coin = coin_price * months * len(selected_accounts)
            if user_coin < need_coin:
                return sender.reply(f'❌ 积分不足，需要{need_coin}，当前有{user_coin}')
                
            new_coin = user_coin - need_coin
            middleware.bucketSet(coin_bucket, sender.getUserID(), str(new_coin))
            today_date = datetime.now().date()
            today_time = str(today_date)
            for account in selected_accounts:
                auth = middleware.bucketGet('JQB.bjy.auth', account)
                if not auth or auth < today_time:
                    auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                else:
                    auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')
                
                middleware.bucketSet('JQB.bjy.auth', account, auth_time)
                
                account_data = middleware.bucketGet('JQB.bjy.account', account)
                if account_data:
                    account_info = json.loads(account_data)
                    password = account_info.get('password')
                    
                    if password:
                        remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{sender.getUserID()}丨授权时间:{auth_time}"
                        env_data = {
                            "name": var_name,
                            "value": f"{account}#{password}",
                            "remarks": remarks
                        }
                        env_id_with_prefix = add_to_panel(env_data)
                        if env_id_with_prefix:
                            middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
            
            sender.reply(
                f"""✅ 已用 {need_coin} 积分授权 {len(selected_accounts)} 个账号 {months} 个月
剩余积分: {new_coin}"""
            )
            
    except Exception as e:
        sender.reply(f'❌ 授权失败: {str(e)}')

def process_payment(amount, days, sender):
    zsm = middleware.bucketGet('JQB.bjy', 'zsm')
    if not zsm:
        sender.reply("❌ 未配置收款码")
        return False
        
    if sender.atWaitPay():
        sender.reply('当前有人正在支付,请稍后再试！')
        return False
        
    pay_msg = f"""=====微信扫码支付====
🎫 商品: 白鲸鱼授权
📅 时长: {days}天
💮 金额: {amount}灵石💮
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)
    sender.replyImage(zsm)
    result = sender.waitPay("q",100000)
    
    if not result:
        sender.reply("❌ 支付超时")
        return False
    elif result == 'q':
        sender.reply("✅ 已取消支付")
        return False
        
    try:
        if isinstance(result, str):
            result = json.loads(result)
            
        paid_amount = Decimal(str(result.get('money') or result.get('Money') or 0))
        if paid_amount >= amount:
            return True
        else:
            sender.reply(f"❌ 支付金额不足，应付: {amount}元，实付: {paid_amount}元")
            return False
    except Exception as e:
        sender.reply(f"❌ 支付验证失败: {str(e)}")
        return False

def tutorial(sender):
    sender.reply("""=====白鲸鱼教程=====
🌟 核心功能指令:
1. 白鲸鱼登录 - 绑定账号(手机号#密码)
2. 白鲸鱼查询 - 查看可回收金额
3. 白鲸鱼签到 - 每日签到
4. 白鲸鱼管理 - 账号管理功能

⚙️ 授权说明:
1. 支持微信支付和积分支付
2. 授权后解锁全部功能
3. 自动同步到青龙/呆呆面板

⚠️ 注意事项:
1. 使用手机号+密码登录
2. 每日签到可获得积分
3. 积分可兑换现金
======================""")

def bjy_auth(sender):
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        return
    
    today_date = datetime.now().date()
    today_time = str(today_date)
    
    sender.reply(
        "=====白鲸鱼授权管理=====\n"
        "  [1] 📱 一键授权所有用户\n" 
        "  [2] 👤 单独授权用户\n"
        "  [3] ⏰ 修改授权时间\n"
        "  [4] 🗑️ 删除用户账号\n"
        "-------------------\n"
        "⚠️ 输入q退出操作\n"
        "=================="
    )
    choice = sender.input(60000, 1, False)
    
    if choice == 'q' or choice == 'Q':
        sender.reply("✅ 已取消操作")
        return
    elif choice == '':
        sender.reply('⏰ 输入超时!')
        return
    elif choice == '1':
        users = middleware.bucketAllKeys('JQB.bjy.user')
        if not users:
            sender.reply("❌ 未找到任何绑定的白鲸鱼账号")
            return
            
        sender.reply('📝 请输入要给所有用户授权的月数！\n⚠️ 输入"q"退出操作')
        months = sender.input(60000, 1, False)
        if months == 'q' or months == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif months == '':
            sender.reply('⏰ 输入超时!')
            return
        
        try:
            months = int(months)
            success_count = 0
            var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
            
            for user in users:
                accountlist = middleware.bucketGet('JQB.bjy.user', user)
                if not accountlist or accountlist == '[]':
                    continue
                    
                accounts = eval(accountlist)
                for account in accounts:
                    try:
                        account_data = middleware.bucketGet('JQB.bjy.account', account)
                        if not account_data:
                            continue
                            
                        auth = middleware.bucketGet('JQB.bjy.auth', account)
                        if not auth or auth < today_time:
                            auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                        else:
                            auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')
                        
                        middleware.bucketSet('JQB.bjy.auth', account, auth_time)
                        
                        # 添加到面板
                        account_info = json.loads(account_data)
                        password = account_info.get('password')
                        
                        if password:
                            remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{user}丨授权时间:{auth_time}"
                            env_data = {
                                "name": var_name,
                                "value": f"{account}#{password}",
                                "remarks": remarks
                            }
                            env_id_with_prefix = add_to_panel(env_data)
                            if env_id_with_prefix:
                                middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                        success_count += 1
                    except:
                        continue
                        
            msg = f"""
=====一键授权完成=====
✅ 成功授权: {success_count}个账号
⏰ 授权月数: {months}月
=================="""
            sender.reply(msg)
            
        except ValueError:
            sender.reply('❌ 输入的月数无效!')
            return
            
    elif choice == '2':
        sender.reply('📝 请输入需要授权的用户ID\n💡 通过给机器人发送"myuid"获得\n⚠️ 输入"q"退出操作')
        user_id = sender.input(60000, 1, False)
        if user_id == 'q' or user_id == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif user_id == '':
            sender.reply('⏰ 输入超时!')
            return
            
        accountlist = middleware.bucketGet('JQB.bjy.user', user_id)
        if not accountlist or accountlist == '[]':
            sender.reply(f"❌ 未找到用户 {user_id} 的白鲸鱼账号信息!")
            return
            
        accounts = eval(accountlist)
        n = 0
        msg = '=====用户账号列表=====\n'
        msg += '0、授权所有账号\n==================\n'
        
        for account in accounts:
            n += 1
            auth = middleware.bucketGet('JQB.bjy.auth', account)
            if not auth:
                auth_status = '未授权'
            elif auth < today_time:
                auth_status = '授权过期'
            else:
                auth_status = f'到期: {auth}'
            msg += f'{n}、账号:{mask_phone(account)}\n授权状态: {auth_status}\n==================\n'
            
        msg += f'📝 回复序号选择账号\n⚠️ 输入"q"退出操作'
        sender.reply(msg)
        choice = sender.input(60000, 1, False)
        
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif choice == '':
            sender.reply('⏰ 输入超时!')
            return
            
        if choice == '0':
            sender.reply('📝 请输入授权月数\n⚠️ 输入"q"退出操作')
            months = sender.input(60000, 1, False)
            
            if months == 'q' or months == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif months == '':
                sender.reply('⏰ 输入超时!')
                return
                
            try:
                months = int(months)
                success_count = 0
                var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
                
                for account in accounts:
                    try:
                        account_data = middleware.bucketGet('JQB.bjy.account', account)
                        if not account_data:
                            continue
                            
                        auth = middleware.bucketGet('JQB.bjy.auth', account)
                        if not auth or auth < today_time:
                            auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                        else:
                            auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')
                        
                        middleware.bucketSet('JQB.bjy.auth', account, auth_time)
                        
                        account_info = json.loads(account_data)
                        password = account_info.get('password')
                        
                        if password:
                            remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{auth_time}"
                            env_data = {
                                "name": var_name,
                                "value": f"{account}#{password}",
                                "remarks": remarks
                            }
                            env_id_with_prefix = add_to_panel(env_data)
                            if env_id_with_prefix:
                                middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                        success_count += 1
                    except:
                        continue
                        
                msg = f"""
=====批量授权完成=====
✅ 成功授权: {success_count}个账号
⏰ 授权月数: {months}月
=================="""
                sender.reply(msg)
                
            except ValueError:
                sender.reply('❌ 输入的月数无效!')
                return
                
        elif 1 <= int(choice) <= len(accounts):
            account = accounts[int(choice)-1]
            sender.reply('📝 请输入授权月数\n⚠️ 输入"q"退出操作')
            months = sender.input(60000, 1, False)
            
            if months == 'q' or months == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif months == '':
                sender.reply('⏰ 输入超时!')
                return
                
            try:
                months = int(months)
                account_data = middleware.bucketGet('JQB.bjy.account', account)
                
                if not account_data:
                    sender.reply("❌ 未找到账号信息!")
                    return
                    
                auth = middleware.bucketGet('JQB.bjy.auth', account)
                if not auth or auth < today_time:
                    auth_time = (datetime.now() + timedelta(days=months*30)).strftime('%Y-%m-%d')
                else:
                    auth_time = (datetime.strptime(auth, "%Y-%m-%d") + timedelta(days=months*30)).strftime('%Y-%m-%d')
                
                middleware.bucketSet('JQB.bjy.auth', account, auth_time)
                
                var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
                account_info = json.loads(account_data)
                password = account_info.get('password')
                
                if password:
                    remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{auth_time}"
                    env_data = {
                        "name": var_name,
                        "value": f"{account}#{password}",
                        "remarks": remarks
                    }
                    env_id_with_prefix = add_to_panel(env_data)
                    if env_id_with_prefix:
                        middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                
                msg = f"""
=====授权成功=====
✅ 账号: {mask_phone(account)}
⏰ 授权月数: {months}月
📅 到期时间: {auth_time}
=================="""
                sender.reply(msg)
                
            except ValueError:
                sender.reply('❌ 输入的月数无效!')
                return
        else:
            sender.reply('❌ 输入的序号无效!')
            return
    elif choice == '3':
        sender.reply(
            "=====修改授权时间=====\n"
            "  [1] 📱 修改所有用户\n"
            "  [2] 👤 修改单独用户\n"
            "-------------------\n"
            "⚠️ 输入q退出操作\n"
            "==================="
        )
        sub_choice = sender.input(60000, 1, False)
        
        if sub_choice == 'q' or sub_choice == 'Q':
            sender.reply("✅ 已取消操作")
            return
        elif sub_choice == '':
            sender.reply('⏰ 输入超时!')
            return
        elif sub_choice == '1':
            users = middleware.bucketAllKeys('JQB.bjy.user')
            if not users:
                sender.reply("❌ 未找到任何绑定的白鲸鱼账号")
                return
                
            sender.reply('📝 请输入要调整的天数:\n➕ 正数增加天数\n➖ 负数减少天数\n💡 例如: 100 或 -100\n⚠️ 输入"q"退出操作')
            days = sender.input(60000, 1, False)
            if days == 'q' or days == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif days == '':
                sender.reply('⏰ 输入超时!')
                return
                
            try:
                days = int(days)
                total_success = 0
                
                var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
                
                for user in users:
                    accountlist = middleware.bucketGet('JQB.bjy.user', user)
                    if not accountlist or accountlist == '[]':
                        continue
                        
                    accounts = eval(accountlist)
                    for account in accounts:
                        try:
                            auth = middleware.bucketGet('JQB.bjy.auth', account)
                            account_data = middleware.bucketGet('JQB.bjy.account', account)
                            
                            if not account_data or not auth:
                                continue
                                
                            if auth == '未授权' or auth < today_time:
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(auth, "%Y-%m-%d").date()
                                
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('JQB.bjy.auth', account, str(new_date))
                            
                            # 更新面板中的环境变量（备注可能变化）
                            account_info = json.loads(account_data)
                            password = account_info.get('password')
                            
                            if password:
                                remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{user}丨授权时间:{new_date}"
                                env_data = {
                                    "name": var_name,
                                    "value": f"{account}#{password}",
                                    "remarks": remarks
                                }
                                env_id_with_prefix = add_to_panel(env_data)
                                if env_id_with_prefix:
                                    middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                            total_success += 1
                        except:
                            continue
                            
                msg = f"""
=====批量修改完成=====
✅ 成功修改: {total_success}个账号
⏰ 调整天数: {days}天
=================="""
                sender.reply(msg)
                
            except ValueError:
                sender.reply('❌ 输入的天数无效!')
                return
                
        elif sub_choice == '2':
            sender.reply('📝 请输入需要修改的用户ID\n💡 通过给机器人发送"myuid"获得\n⚠️ 输入"q"退出操作')
            user_id = sender.input(60000, 1, False)
            if user_id == 'q' or user_id == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif user_id == '':
                sender.reply('⏰ 输入超时!')
                return
                
            accountlist = middleware.bucketGet('JQB.bjy.user', user_id)
            if not accountlist or accountlist == '[]':
                sender.reply(f"❌ 未找到用户 {user_id} 的白鲸鱼账号信息!")
                return
                
            accounts = eval(accountlist)
            n = 0
            msg = '=====用户账号列表=====\n'
            msg += '0、修改所有账号\n==================\n'
            
            for account in accounts:
                n += 1
                auth = middleware.bucketGet('JQB.bjy.auth', account)
                if not auth:
                    auth_status = '未授权'
                elif auth < today_time:
                    auth_status = '授权过期'
                else:
                    auth_status = f'到期: {auth}'
                msg += f'{n}、账号:{mask_phone(account)}\n授权状态: {auth_status}\n==================\n'
                
            msg += f'📝 回复序号选择账号\n⚠️ 输入"q"退出操作'
            sender.reply(msg)
            choice = sender.input(60000, 1, False)
            
            if choice == 'q' or choice == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif choice == '':
                sender.reply('⏰ 输入超时!')
                return
                
            if choice == '0':
                sender.reply('📝 请输入要调整的天数:\n➕ 正数增加天数\n➖ 负数减少天数\n💡 例如: 100 或 -100\n⚠️ 输入"q"退出操作')
                days = sender.input(60000, 1, False)
                
                if days == 'q' or days == 'Q':
                    sender.reply("✅ 已取消操作")
                    return
                elif days == '':
                    sender.reply('⏰ 输入超时!')
                    return
                    
                try:
                    days = int(days)
                    success_count = 0
                    
                    var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
                    
                    for account in accounts:
                        try:
                            auth = middleware.bucketGet('JQB.bjy.auth', account)
                            account_data = middleware.bucketGet('JQB.bjy.account', account)
                            
                            if not account_data or not auth:
                                continue
                                
                            if auth == '未授权' or auth < today_time:
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(auth, "%Y-%m-%d").date()
                                
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('JQB.bjy.auth', account, str(new_date))
                            
                            account_info = json.loads(account_data)
                            password = account_info.get('password')
                            
                            if password:
                                remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{new_date}"
                                env_data = {
                                    "name": var_name,
                                    "value": f"{account}#{password}",
                                    "remarks": remarks
                                }
                                env_id_with_prefix = add_to_panel(env_data)
                                if env_id_with_prefix:
                                    middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                            success_count += 1
                        except:
                            continue
                            
                    msg = f"""
=====批量修改完成=====
✅ 成功修改: {success_count}个账号
⏰ 调整天数: {days}天
=================="""
                    sender.reply(msg)
                    
                except ValueError:
                    sender.reply('❌ 输入的天数无效!')
                    return
                    
            elif 1 <= int(choice) <= len(accounts):
                account = accounts[int(choice)-1]
                sender.reply('📝 请输入要调整的天数:\n➕ 正数增加天数\n➖ 负数减少天数\n💡 例如: 100 或 -100\n⚠️ 输入"q"退出操作')
                days = sender.input(60000, 1, False)
                
                if days == 'q' or days == 'Q':
                    sender.reply("✅ 已取消操作")
                    return
                elif days == '':
                    sender.reply('⏰ 输入超时!')
                    return
                    
                try:
                    days = int(days)
                    auth = middleware.bucketGet('JQB.bjy.auth', account)
                    account_data = middleware.bucketGet('JQB.bjy.account', account)
                    
                    if not account_data or not auth:
                        sender.reply("❌ 未找到账号信息!")
                        return
                        
                    if auth == '未授权' or auth < today_time:
                        current_date = today_date
                    else:
                        current_date = datetime.strptime(auth, "%Y-%m-%d").date()
                        
                    new_date = current_date + timedelta(days=days)
                    middleware.bucketSet('JQB.bjy.auth', account, str(new_date))
                    
                    var_name = middleware.bucketGet('JQB.bjy', 'var_name') or 'bjy'
                    account_info = json.loads(account_data)
                    password = account_info.get('password')
                    
                    if password:
                        remarks = f"白鲸鱼账号{mask_phone(account)}丨用户:{user_id}丨授权时间:{new_date}"
                        env_data = {
                            "name": var_name,
                            "value": f"{account}#{password}",
                            "remarks": remarks
                        }
                        env_id_with_prefix = add_to_panel(env_data)
                        if env_id_with_prefix:
                            middleware.bucketSet('JQB.bjy.env_id', account, env_id_with_prefix)
                    
                    msg = f"""
=====修改成功=====
✅ 账号: {mask_phone(account)}
⏰ 调整天数: {days}天
📅 新到期时间: {new_date}
=================="""
                    sender.reply(msg)
                    
                except ValueError:
                    sender.reply('❌ 输入的天数无效!')
                    return
            else:
                sender.reply('❌ 输入的序号无效!')
                return
        else:
            sender.reply('❌ 输入的选项无效!')
            return
    elif choice == '4':
        users = middleware.bucketAllKeys('JQB.bjy.user')
        if not users:
            return sender.reply("❌ 没有可删除的用户账号")
            
        menu = "=====选择要删除的用户=====\n"
        for idx, user in enumerate(users, 1):
            accounts = eval(middleware.bucketGet('JQB.bjy.user', user) or [])
            menu += f"[{idx}] 用户ID: {user} (账号数: {len(accounts)})\n"
        menu += "=======================\n⚠️ 回复数字序号(输入q退出)"
        sender.reply(menu)
        
        choice = sender.input(60000, 1, False)
        if not choice or choice.lower() == 'q':
            return sender.reply('已取消操作')
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(users):
                user_id = users[index]
                
                accounts = eval(middleware.bucketGet('JQB.bjy.user', user_id) or [])
                
                menu = "=====用户账号列表=====\n"
                menu += "0、删除所有账号\n==================\n"
                for idx, account in enumerate(accounts, 1):
                    auth = middleware.bucketGet('JQB.bjy.auth', account)
                    if not auth:
                        auth_status = '未授权'
                    elif auth < today_time:
                        auth_status = '授权过期'
                    else:
                        auth_status = f'到期: {auth}'
                    menu += f"{idx}、账号: {mask_phone(account)}\n授权状态: {auth_status}\n==================\n"
                menu += "📝 回复序号选择账号\n⚠️ 输入'q'退出操作"
                sender.reply(menu)
                
                acc_choice = sender.input(60000, 1, False)
                if not acc_choice or acc_choice.lower() == 'q':
                    return sender.reply('已取消操作')
                    
                if acc_choice == '0':
                    confirm_msg = f"""=====⚠️警告⚠️=====
即将删除用户ID: {user_id} 的所有账号
账号列表:
{", ".join([mask_phone(acc) for acc in accounts])}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                    sender.reply(confirm_msg)
                    
                    confirm = sender.input(60000, 1, False)
                    if confirm.lower() != 'y':
                        return sender.reply('✅ 已取消删除操作')
                    
                    deleted_count = 0
                    for account in accounts:
                        try:
                            env_id_with_prefix = middleware.bucketGet('JQB.bjy.env_id', account)
                            if env_id_with_prefix:
                                delete_from_panel(env_id_with_prefix)
                            
                            middleware.bucketDel('JQB.bjy.account', account)
                            middleware.bucketDel('JQB.bjy.auth', account)
                            middleware.bucketDel('JQB.bjy.env_id', account)
                            deleted_count += 1
                        except:
                            continue
                    
                    middleware.bucketDel('JQB.bjy.user', user_id)
                    
                    sender.reply(f"✅ 已删除用户 {user_id} 的 {deleted_count} 个账号")
                    
                elif acc_choice.isdigit() and 1 <= int(acc_choice) <= len(accounts):
                    acc_index = int(acc_choice) - 1
                    account = accounts[acc_index]
                    
                    confirm_msg = f"""=====⚠️警告⚠️=====
即将删除账号:
📱 账号: {mask_phone(account)}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                    sender.reply(confirm_msg)
                    
                    confirm = sender.input(60000, 1, False)
                    if confirm.lower() != 'y':
                        return sender.reply('✅ 已取消删除操作')
                    
                    env_id_with_prefix = middleware.bucketGet('JQB.bjy.env_id', account)
                    if env_id_with_prefix:
                        delete_from_panel(env_id_with_prefix)
                    
                    middleware.bucketDel('JQB.bjy.account', account)
                    middleware.bucketDel('JQB.bjy.auth', account)
                    middleware.bucketDel('JQB.bjy.env_id', account)
                    
                    accounts.pop(acc_index)
                    if accounts:
                        middleware.bucketSet('JQB.bjy.user', user_id, str(accounts))
                    else:
                        middleware.bucketDel('JQB.bjy.user', user_id)
                    
                    sender.reply(f"✅ 已删除账号: {mask_phone(account)}")
                else:
                    sender.reply('❌ 输入的序号无效!')
            else:
                sender.reply('❌ 选择超出范围')
        except:
            sender.reply('❌ 输入错误')
    else:
        sender.reply('❌ 输入的选项无效!')

def main():
    try:
        senderID = middleware.getSenderID()
        sender = middleware.Sender(senderID)
        message = sender.getMessage().strip().lower()
        
        if '登录' in message:
            bind(sender)
        elif '查询' in message:
            query(sender)
        elif '签到' in message:
            sign_in(sender)
        elif '管理' in message:
            manage_accounts(sender)
        elif '教程' in message or '帮助' in message:
            tutorial(sender)
        elif message == '白鲸鱼清理' and sender.isAdmin():
            clean_expired(sender)
        elif message == '白鲸鱼授权' and sender.isAdmin():
            bjy_auth(sender)
        else:
            sender.reply("""指令未识别，可用指令:
白鲸鱼登录 - 绑定账号
白鲸鱼查询 - 查看状态
白鲸鱼签到 - 每日签到
白鲸鱼管理 - 账号管理
白鲸鱼教程 - 使用说明""")
    except Exception as e:
        traceback.print_exc()
        try:
            senderID = middleware.getSenderID()
            if senderID:
                sender = middleware.Sender(senderID)
                sender.reply(f"❌ 插件运行出错: {str(e)}")
        except:
            pass

def clean_expired(sender):
    if not sender.isAdmin():
        return sender.reply("❌ 需要管理员权限")
        
    today_date = datetime.now().date()
    today_time = str(today_date)
    
    users = middleware.bucketAllKeys('JQB.bjy.user')
    cleaned = 0
    
    for user in users:
        accounts = eval(middleware.bucketGet('JQB.bjy.user', user) or [])
        valid = []
        
        for account in accounts:
            auth = middleware.bucketGet('JQB.bjy.auth', account)
            if not auth or auth < today_time:
                env_id_with_prefix = middleware.bucketGet('JQB.bjy.env_id', account)
                if env_id_with_prefix:
                    delete_from_panel(env_id_with_prefix)
                
                middleware.bucketDel('JQB.bjy.account', account)
                middleware.bucketDel('JQB.bjy.auth', account)
                middleware.bucketDel('JQB.bjy.env_id', account)
                cleaned += 1
            else:
                valid.append(account)
                
        if valid:
            middleware.bucketSet('JQB.bjy.user', user, str(valid))
        else:
            middleware.bucketDel('JQB.bjy.user', user)
            
    sender.reply(f"✅ 已清理 {cleaned} 个过期账号")

if __name__ == "__main__":
    try:
        if middleware.getSenderID() == "":
            pass  # 定时任务模式（已移除）
        else:
            main()
    except Exception as e:
        traceback.print_exc()
        try:
            senderID = middleware.getSenderID()
            if senderID:
                sender = middleware.Sender(senderID)
                sender.reply(f"❌ 插件运行出错: {str(e)}")
        except:
            pass