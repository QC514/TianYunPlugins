# [title: 酒仙签到]
# [language: python]
# [class: 工具类]
# [service: 2993959969] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(酒仙|jx)(登录|登陆)$|^登(录|陆)(酒仙|jx)$|^(酒仙|jx)(查询|管理)$|^(查询|管理)(酒仙|jx)$|^酒仙授权$|^酒仙检测$|^(酒仙|jx)教程$|^教程(酒仙|jx)$]
# [cron: 0 9 * * *] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用平台
# [open_source: false]
# [icon: https://img-upload.vorto.cc/beb5a0d45aa58e08348e1e4076fa419e.jpg]
# [version: 1.6]
# [public:true]
# [price: 3.88]
# [description: 酒仙签到，每日签到浏览任务领金币<br>指令：酒仙登录、管理、查询、授权、检测、教程<br>1.5：支持AI验证码识别，可配置开关、API地址、密钥、模型]

import os
import json
import time
import hashlib
import random
import string
import re
import requests
import base64
from datetime import datetime, timedelta
from urllib.parse import urlencode
import urllib3
import middleware

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_jx_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_jx', 'coin_key': 'dd_sign_points', 'name': '酒仙'}
PAY_TYPE_NAMES = {'alipay': '支付宝', 'wxpay': '微信支付', 'qqpay': 'QQ钱包'}

# [param: {"required":true,"key":"s_jx.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款方式","desc":"收款码链接"}]
# [param: {"required":true,"key":"s_jx.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"青龙容器参数用丨分割"}]
# [param: {"required":true,"key":"s_jx.osname","bool":false,"placeholder":"例:S_JIUXIAN","name":"青龙变量名","desc":"青龙容器内酒仙的变量名"}]
# [param: {"required":true,"key":"s_jx.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"s_jx.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"s_jx.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_jx.notify_days","bool":false,"placeholder":"例:3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]
# [param: {"required":true,"key":"s_jx.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付"}]
# [param: {"required":false,"key":"s_jx.ai_ocr_switch","bool":true,"placeholder":"","name":"AI验证码识别","desc":"开启后使用AI自动识别验证码，关闭则手动输入"}]
# [param: {"required":false,"key":"s_jx.ai_api_url","bool":false,"placeholder":"https://api.siliconflow.cn/v1","name":"AI API地址","desc":"默认使用硅基流动"}]
# [param: {"required":false,"key":"s_jx.ai_api_key","bool":false,"placeholder":"sk-xxx","name":"AI API密钥","desc":"硅基流动或其他兼容OpenAI API的密钥"}]
# [param: {"required":false,"key":"s_jx.ai_model","bool":false,"placeholder":"Qwen/Qwen3-VL-235B-A22B-Thinking","name":"AI模型","desc":"视觉语言模型名称"}]

# 酒仙API配置
class JiuxianConfig:
    APP_NAME = "酒仙"
    VERSION = "9.2.16"
    LOGIN_URL = "https://newappuser.jiuxian.com/user/loginUserNamePassWd.htm"
    CAPTCHA_URL = "https://newappuser.jiuxian.com/messages/graphCode.htm"
    MEMBER_INFO_URL = "https://newappuser.jiuxian.com/memberChannel/memberInfo.htm"
    
    APP_DEVICE_INFO = {
        "appKey": "daab51fd-a40a-3943-bc95-2f46919da694",
        "appVersion": "9.2.16",
        "areaId": "500",
        "channelCode": "0",
        "cpsId": "tencent",
        "deviceIdentify": "daab51fd-a40a-3943-bc95-2f46919da694",
        "deviceType": "ANDROID",
        "deviceTypeExtra": "0",
        "equipmentType": "SM-A5260",
        "netEnv": "wifi",
        "screenReslolution": "720x1280",
        "supportWebp": "1",
        "sysVersion": "12"
    }
    
    APP_HEADERS = {
        "User-Agent": "okhttp/3.14.9",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "newappuser.jiuxian.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    
    MINI_PROGRAM_INFO = {
        'appKey': '1ba8b341-5a56-49dc-8ee3-92b32db7fc21',
        'appVersion': '9.2.12',
        'apiVersion': '1.0',
        'areaId': '2048',
        'channelCode': '0, 1',
        'appChannel': 'xiaochengxu',
        'deviceType': 'XIAOCHENGXU',
        'supportWebp': '2',
        'longi': '115.80287868923611',
        'lati': '28.155340440538193',
        'screenReslolution': '412x915',
        'sysVersion': 'Android 14'
    }
    
    MINI_PROGRAM_HEADERS = {
        "Host": "newappuser.jiuxian.com",
        "Connection": "keep-alive",
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; M2011K2C) AppleWebKit/537.36 Chrome/138.0.7258.158 Mobile Safari/537.36 MicroMessenger/8.0.64.2940",
        "Accept-Encoding": "gzip, deflate, br"
    }


def get_ai_config():
    """获取AI验证码识别配置"""
    ai_switch = middleware.bucketGet('s_jx', 'ai_ocr_switch') or 'false'
    ai_url = middleware.bucketGet('s_jx', 'ai_api_url') or 'https://api.siliconflow.cn/v1'
    ai_key = middleware.bucketGet('s_jx', 'ai_api_key') or ''
    ai_model = middleware.bucketGet('s_jx', 'ai_model') or 'Qwen/Qwen3-VL-235B-A22B-Thinking'
    return ai_switch.lower() == 'true', ai_url.strip(), ai_key.strip(), ai_model.strip()


def generate_push_token(length=44):
    """生成随机pushToken，由大小写字母和数字组成"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def get_captcha():
    """获取验证码图片
    :return: (成功标志, 验证码base64编码)
    """
    try:
        params = JiuxianConfig.APP_DEVICE_INFO.copy()
        params["pushToken"] = generate_push_token()
        params["type"] = "13"
        
        headers = {
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive",
            "Host": "newappuser.jiuxian.com",
            "User-Agent": "okhttp/3.14.9"
        }
        
        response = requests.get(
            JiuxianConfig.CAPTCHA_URL,
            params=params,
            headers=headers,
            timeout=15,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") == "1" and data.get("result", {}).get("imgCode"):
                return True, data["result"]["imgCode"]
            return False, data.get('errMsg', '获取验证码失败')
        return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)


def recognize_captcha_with_ai(img_base64):
    """使用AI识别验证码
    :param img_base64: 验证码图片的base64编码
    :return: 识别结果，失败返回None
    """
    ai_switch, ai_url, ai_key, ai_model = get_ai_config()
    
    if not ai_key:
        return None
    
    try:
        url = f"{ai_url.rstrip('/')}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {ai_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": ai_model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "text",
                            "text": "这是一个验证码图片，请识别图片中的验证码字符。只需要返回验证码内容，不要包含任何其他文字、解释或标点符号。验证码通常是4-6位的字母和数字组合。"
                        }
                    ]
                }
            ],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
        response.raise_for_status()
        
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0].get("message", {}).get("content", "")
            # 清理响应，只保留字母和数字
            code = re.sub(r'[^a-zA-Z0-9]', '', content.strip())
            if code:
                return code
        return None
    except Exception as e:
        return None


def jx_login(username, password, verify_code=None):
    """酒仙登录（带验证码）"""
    try:
        login_data = JiuxianConfig.APP_DEVICE_INFO.copy()
        login_data["pushToken"] = generate_push_token()
        login_data.update({
            "userName": username,
            "passWord": password,
            "verifyCode": verify_code or ""
        })
        
        response = requests.post(
            JiuxianConfig.LOGIN_URL,
            data=login_data,
            headers=JiuxianConfig.APP_HEADERS,
            timeout=15,
            verify=False
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") == "1":
                user_info = result["result"]["userInfo"]
                return True, user_info["token"], user_info.get("uname", "")
            return False, None, result.get('errMsg', '登录失败')
        return False, None, f"HTTP {response.status_code}"
    except Exception as e:
        return False, None, str(e)


def jx_userinfo(token):
    """获取酒仙用户信息"""
    try:
        params = JiuxianConfig.MINI_PROGRAM_INFO.copy()
        params["token"] = token
        params["equipmentType"] = json.dumps({
            "deviceAbi": "arm64-v8a",
            "system": "Android 14",
            "model": "M2011K2C",
            "brand": "Xiaomi",
            "platform": "android"
        })
        
        response = requests.get(
            JiuxianConfig.MEMBER_INFO_URL,
            params=params,
            headers=JiuxianConfig.MINI_PROGRAM_HEADERS,
            timeout=15,
            verify=False
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success") == "1":
                return True, result["result"]
        return False, "获取失败"
    except Exception as e:
        return False, str(e)


def get_user_content():
    osname = middleware.bucketGet('s_jx', 'osname') or 'S_JIUXIAN'
    qlname = middleware.bucketGet('s_jx', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_jx', 'Vipmoney') or '1')
    coin = middleware.bucketGet(PLUGIN_CONFIG['bucket'], PLUGIN_CONFIG['coin_key'])
    if not coin:
        coin = middleware.bucketGet('s_jx', 'coin') or '0'
    return osname, qlname, '酒仙管理', '酒仙查询', '酒仙登录', Vipmoney, int(coin)


def mask_account(account):
    if not account or len(account) < 4:
        return account
    if account.isdigit() and len(account) == 11:
        return f"{account[:3]}****{account[7:]}"
    return f"{account[:2]}***{account[-2:]}"


def login_with_captcha(username, password):
    """登录流程：支持AI自动识别或手动输入验证码
    :return: (success, token, result_msg)
    """
    ai_switch, ai_url, ai_key, ai_model = get_ai_config()
    
    # 获取验证码
    captcha_success, captcha_result = get_captcha()
    if not captcha_success:
        return False, None, f"获取验证码失败: {captcha_result}"
    
    img_base64 = captcha_result
    verify_code = None
    
    if ai_switch and ai_key:
        # AI自动识别验证码
        #sender.reply(f"🔄 正在使用AI识别验证码...")
        verify_code = recognize_captcha_with_ai(img_base64)
        if not verify_code:
            #sender.reply(f"✅ AI识别验证码: {verify_code}")
            sender.reply(f"❌ AI识别失败，请手动输入")
    
    if not verify_code:
        # 发送验证码图片给用户
        sender.reply("请输入验证码（60秒内有效）：")
        # 调用API将base64转换为图片URL
        try:
            api_url = "https://qrcode.vorto.cn/api/image/base64"
            api_key = "4jpC3Cgd0zA7Z3HTJ6aDfW9QjtzitDGI"
            
            response = requests.post(
                api_url,
                json={"base64": img_base64},
                headers={"X-API-Key": api_key},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and result.get('data', {}).get('url'):
                    # 使用返回的URL发送图片
                    sender.replyImage(result['data']['url'])
                else:
                    sender.reply(f"[验证码图片转换失败: {result.get('error', '未知错误')}，请重试]")
                    return False, None, "验证码图片转换失败"
            else:
                sender.reply(f"[验证码图片上传失败: HTTP {response.status_code}，请重试]")
                return False, None, "验证码图片上传失败"
        except Exception as e:
            sender.reply(f"[验证码图片发送失败: {str(e)}，请重试]")
            return False, None, "验证码图片发送失败"
        
        # 等待用户输入验证码
        user_input = sender.input(60000, 1, False)
        if not user_input:
            return False, None, "验证码输入超时"
        if user_input.lower() == 'q':
            return False, None, "用户取消"
        verify_code = user_input.strip()
    
    # 使用验证码登录
    success, token, result = jx_login(username, password, verify_code)
    
    # 如果验证码错误且AI开启，尝试重新获取
    if not success and result and "验证码" in result and ai_switch and ai_key:
        sender.reply(f"⚠️ 验证码错误，正在重试...")
        # 重新获取验证码
        captcha_success, captcha_result = get_captcha()
        if captcha_success:
            verify_code = recognize_captcha_with_ai(captcha_result)
            if verify_code:
                success, token, result = jx_login(username, password, verify_code)
    
    return success, token, result


def bind_account():
    """绑定账号"""
    sender.reply(
        "=====酒仙登录=====\n"
        "支持批量登录，格式如下:\n"
        "账号#密码\n"
        "（多账号换行分隔）\n"
        "------------------\n"
        "回复\"q\"退出操作\n"
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("⏰ 操作超时")
        return
    if input_text.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    lines = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
    account_list = []
    for line in lines:
        if '#' in line:
            parts = line.split('#', 1)
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                account_list.append({
                    'username': parts[0].strip(),
                    'password': parts[1].strip()
                })
    
    if not account_list:
        sender.reply("❌ 未检测到有效账号\n格式: 账号#密码")
        return
    
    sender.reply(f"🔄 正在登录 {len(account_list)} 个账号...")
    
    success_count = 0
    fail_count = 0
    success_accounts = []
    
    for acc in account_list:
        username = acc['username']
        password = acc['password']
        
        try:
            success, token, result = login_with_captcha(username, password)
            if not success:
                sender.reply(f"❌ {mask_account(username)} 登录失败: {result}")
                fail_count += 1
                continue
            
            current_value = middleware.bucketGet('s_jx_user', userid)
            if not current_value:
                middleware.bucketSet('s_jx_user', userid, str([username]))
            else:
                accounts = eval(current_value)
                if username not in accounts:
                    accounts.append(username)
                    middleware.bucketSet('s_jx_user', userid, str(accounts))
            
            account_info = {"username": username, "password": password, "token": token}
            middleware.bucketSet('s_jx_token', username, json.dumps(account_info))
            
            success_count += 1
            success_accounts.append({'username': username, 'info': account_info})
            sender.reply(f"✅ {mask_account(username)} 登录成功")
            
        except Exception as e:
            sender.reply(f"❌ {mask_account(username)} 异常: {str(e)}")
            fail_count += 1
    
    sender.reply(
        f"=====登录完成=====\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"=================="
    )
    
    if success_accounts:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        need_auth = []
        for acc in success_accounts:
            username = acc['username']
            accountVip = middleware.bucketGet('s_jx_auth', username)
            if accountVip and accountVip > dqsj:
                sender.reply(f"📱 {mask_account(username)} 已授权，到期: {accountVip}")
                update_ql_env(username, acc['info'])
            else:
                need_auth.append(acc)
        
        if need_auth:
            sender.reply(f"\n📋 {len(need_auth)} 个账号需要授权")
            authorize_multiple_accounts([acc['username'] for acc in need_auth])


def query_accounts():
    """查询账号"""
    if not uservalue:
        sender.reply(f"=====未绑定账号=====\n❌ 未找到账号\n💡 发送 酒仙登录 绑定\n==================")
        return
    
    accounts = eval(uservalue)
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_jx_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(username)}({auth_status})"
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
        for i, username in enumerate(selected, 1):
            try:
                account_info = json.loads(middleware.bucketGet('s_jx_token', username))
                auth_time = middleware.bucketGet('s_jx_auth', username)
                auth_status = '已授权' if auth_time and auth_time >= str(datetime.now().date()) else '未授权'
                
                # 重新登录获取最新token
                login_success, token, _ = jx_login(username, account_info.get('password', ''))
                user_info_text = ""
                if login_success:
                    info_success, user_data = jx_userinfo(token)
                    if info_success:
                        gold = user_data.get('goldMoney', 0)
                        sign_days = user_data.get('signDays', 0)
                        is_signed = user_data.get('isSignTody', False)
                        user_info_text = (
                            f"\n💰 金币: {gold}"
                            f"\n📅 连续签到: {sign_days}天"
                            f"\n✅ 今日签到: {'已签' if is_signed else '未签'}"
                        )
                
                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 账号: {mask_account(username)}\n"
                    f"🏷 状态: {auth_status}\n"
                    f"📅 到期: {auth_time or '未授权'}{user_info_text}\n"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"=====查询失败=====\n❌ 错误: {str(e)}\n==================")
        
        sender.reply(f"✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


def manage_account():
    """管理账号"""
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
    
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, username in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_jx_auth', username)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(username)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
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
    
    if choice == '1':
        authorize_multiple_accounts(selected)
    elif choice == '2':
        sender.reply("=====确认删除=====\n⚠️ 此操作不可恢复\n回复 y 确认删除\n==================")
        if sender.input(120000, 1, False).lower() == 'y':
            for username in selected:
                if username in accounts:
                    accounts.remove(username)
                middleware.bucketDel('s_jx_token', username)
                middleware.bucketDel('s_jx_auth', username)
                delete_ql_env(username)
            
            if accounts:
                middleware.bucketSet('s_jx_user', userid, str(accounts))
            else:
                middleware.bucketDel('s_jx_user', userid)
            sender.reply(f"✅ 已删除 {len(selected)} 个账号")
        else:
            sender.reply("✅ 已取消")
    elif choice == '3':
        success = 0
        for username in selected:
            try:
                account_info = json.loads(middleware.bucketGet('s_jx_token', username))
                auth_time = middleware.bucketGet('s_jx_auth', username)
                if auth_time and auth_time >= str(datetime.now().date()):
                    if update_ql_env(username, account_info):
                        success += 1
            except:
                pass
        sender.reply(
            f"=====提交结果=====\n"
            f"✅ 成功: {success}个\n"
            f"❌ 失败: {len(selected) - success}个\n"
            f"=================="
        )


def authorize_multiple_accounts(usernames):
    """批量授权账号"""
    account_infos = []
    for username in usernames:
        try:
            account_infos.append({
                'username': username,
                'info': json.loads(middleware.bucketGet('s_jx_token', username))
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
        
        Vipmoney = float(middleware.bucketGet('s_jx', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_jx', 'coin') or '0')
        
        available = []
        ma_pay_switch = middleware.bucketGet('s_jx', 'ma_pay_switch') or 'false'
        if ma_pay_switch.lower() == 'true' and middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'):
            for pt in (middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay').split(','):
                available.append((PAY_TYPE_NAMES.get(pt.strip(), pt.strip()), f"mapay_{pt.strip()}"))
        elif middleware.bucketGet('s_jx', 'zsm'):
            available.append(("微信支付", "wxpay"))
        
        if coin > 0:
            available.append(("积分兑换", "coin"))
        
        if not available:
            sender.reply("❌ 未配置支付方式")
            return
        
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
        
        if payment_type == 'coin':
            for acc in account_infos:
                process_coin_payment(acc['username'], acc['info'], months, coin)
        elif payment_type.startswith('mapay_'):
            if handle_mapay_order(PLUGIN_CONFIG['name'], months, total_money, payment_type.replace('mapay_', '')):
                for acc in account_infos:
                    process_authorization(acc['username'], acc['info'], months)
        else:
            if pay_order(PLUGIN_CONFIG['name'], months, total_money):
                for acc in account_infos:
                    process_authorization(acc['username'], acc['info'], months)
    except ValueError:
        sender.reply("❌ 请输入有效数字")


def process_authorization(username, account_info, months):
    """处理授权（用户付费，按月计算）"""
    try:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_jx_auth', username)
        if accountVip and accountVip > dqsj:
            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        new_expire = (start_date + timedelta(days=30 * months)).strftime("%Y-%m-%d")
        middleware.bucketSet('s_jx_auth', username, new_expire)
        update_ql_env(username, account_info)
        
        sender.reply(
            f"=====授权成功=====\n"
            f"📱 账号: {mask_account(username)}\n"
            f"📅 到期: {new_expire}\n"
            f"=================="
        )
        return True
    except Exception as e:
        sender.reply(f"授权异常: {str(e)}")
        return False


def admin_authorization(username, account_info, days):
    """管理员授权（按天数，正数增加，负数减少）"""
    try:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_jx_auth', username)
        if accountVip and accountVip > dqsj:
            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        new_expire = (start_date + timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 如果新到期时间早于今天，则设置为无效（已过期）
        if new_expire < dqsj:
            middleware.bucketDel('s_jx_auth', username)
            delete_ql_env(username)
            return False, "授权已清除（到期时间早于今天）"
        
        middleware.bucketSet('s_jx_auth', username, new_expire)
        update_ql_env(username, account_info)
        return True, new_expire
    except Exception as e:
        return False, str(e)


def process_coin_payment(username, account_info, months, coin):
    """积分支付"""
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
        if process_authorization(username, account_info, months):
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


def generate_iframe_url(url):
    """将URL通过base64编码生成iframe页面链接"""
    try:
        encoded = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        iframe_url = f"https://metwhale.github.io?u={encoded}"
        return iframe_url
    except Exception as e:
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
    except Exception as e:
        pass
    
    try:
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        return None


def handle_mapay_order(project, months, money, pay_type=None):
    """码支付订单"""
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
    out_trade_no = f"JX{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
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
        sender.reply('请扫描下方二维码完成支付，输入"q"退出支付:')
        sender.replyImage(generate_qrcode(iframe_url))
        sender.reply('扫码提示风险请使用浏览器扫码打开！')
        
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
    """普通支付"""
    if float(money) == 0:
        sender.reply(
            f"=====授权成功=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: 免费\n"
            f"=================="
        )
        return True
    
    zsm = middleware.bucketGet('s_jx', 'zsm')
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


def get_ql_token(host, client_id, client_secret):
    """获取青龙Token"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        resp = requests.get(url, timeout=10).json()
        if resp.get('code') == 200:
            return resp['data']['token']
        return None
    except:
        return None


def update_ql_env(username, account_info):
    """更新青龙环境变量"""
    account = account_info.get('username', '')
    password = account_info.get('password', '')
    if not account or not password:
        return False
    
    env_value = f"{account}#{password}"
    qlconfig = middleware.bucketGet('s_jx', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        osname = middleware.bucketGet('s_jx', 'osname') or 'S_JIUXIAN'
        auth_time = middleware.bucketGet('s_jx_auth', username) or '未授权'
        
        envs = requests.get(
            f'{host}/open/envs?searchValue={username}',
            headers=headers,
            timeout=10
        ).json().get('data', [])
        env_id = next((e.get('id') for e in envs if e['name'] == osname), None)
        
        env_data = {
            'name': osname,
            'value': env_value,
            'remarks': f"酒仙：{username}|到期:{auth_time}"
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


def delete_ql_env(username):
    """删除青龙环境变量"""
    qlconfig = middleware.bucketGet('s_jx', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        osname = middleware.bucketGet('s_jx', 'osname') or 'S_JIUXIAN'
        envs = requests.get(f'{host}/open/envs', headers=headers, timeout=10).json().get('data', [])
        
        for env in envs:
            if env['name'] == osname and username in env.get('remarks', ''):
                env_id = env.get('_id') or env.get('id')
                requests.delete(f'{host}/open/envs', headers=headers, json=[env_id], timeout=10)
                return True
        return False
    except:
        return False


def check_auth_status():
    """检测授权状态并推送通知
    逻辑：到期时间-当前日期 > 提前天数，不推送
          到期时间-当前日期 <= 提前天数 且 > 0，推送提醒
          到期时间-当前日期 <= 0，清理账号
    """
    notify = middleware.bucketGet('s_jx', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"
    
    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_jx_user')
    if not all_users:
        return "❌ 没有用户"
    
    # 获取提前提醒天数配置，默认3天
    notify_days = int(middleware.bucketGet('s_jx', 'notify_days') or '3')
    
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0
    
    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_jx_user', user_id) or '[]')
            
            # 分类账号：需要提醒的和需要清理的
            to_notify = []  # 需要提醒的账号
            to_clean = []   # 需要清理的账号
            
            for acc in accounts:
                auth_time_str = middleware.bucketGet('s_jx_auth', acc)
                
                if not auth_time_str:
                    # 未授权，直接清理
                    to_clean.append({'phone': acc, 'auth_time': '未授权', 'days_left': 0})
                    continue
                
                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days
                    
                    if days_left <= 0:
                        # 已过期，清理
                        to_clean.append({'phone': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        # 即将过期，提醒
                        to_notify.append({'phone': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                    # days_left > notify_days 不做任何操作
                except:
                    # 日期格式错误，清理
                    to_clean.append({'phone': acc, 'auth_time': auth_time_str, 'days_left': 0})
            
            total += len(accounts)
            
            # 处理需要清理的账号
            if to_clean:
                for exp_acc in to_clean:
                    username = exp_acc['phone']
                    delete_ql_env(username)
                    middleware.bucketDel('s_jx_token', username)
                    
                    if username in accounts:
                        accounts.remove(username)
                    
                    middleware.bucketDel('s_jx_auth', username)
                    cleaned += 1
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet('s_jx_user', user_id, str(accounts))
                else:
                    middleware.bucketDel('s_jx_user', user_id)
            
            # 处理需要提醒的账号
            if to_notify:
                notify_list = "\n".join([
                    f"📱 {mask_account(a['phone'])} 剩余{a['days_left']}天({a['auth_time']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====酒仙账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"酒仙管理\"续费\n"
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
    
    return f"✅ 酒仙检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"


def ks_auth():
    """管理员授权（按天数授权，正数增加，负数减少）"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return
    
    sender.reply(
        "=====管理员授权=====\n"
        "[1] 批量授权\n"
        "[2] 单独授权\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        return
    
    if choice == '1':
        all_users = [
            {'id': k, 'accounts': eval(middleware.bucketGet('s_jx_user', k) or '[]')}
            for k in middleware.bucketAllKeys('s_jx_user')
        ]
        if not all_users:
            sender.reply("❌ 无用户")
            return
        
        total_accs = sum(len(u['accounts']) for u in all_users)
        sender.reply(f"✅ {len(all_users)} 用户，{total_accs} 账号\n请输入授权天数(正数增加/负数减少):")
        
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            return
        days = int(days_input)
        
        action = "增加" if days > 0 else "减少"
        sender.reply(f"确认为 {total_accs} 个账号{action} {abs(days)} 天？回复y确认:")
        if sender.input(120000, 1, False).lower() != 'y':
            sender.reply("✅ 已取消")
            return
        
        success = 0
        fail = 0
        for u in all_users:
            for acc in u['accounts']:
                try:
                    info = json.loads(middleware.bucketGet('s_jx_token', acc))
                    result, msg = admin_authorization(acc, info, days)
                    if result:
                        success += 1
                    else:
                        fail += 1
                except:
                    fail += 1
        
        sender.reply(
            f"=====授权结果=====\n"
            f"✅ 成功: {success}/{total_accs}\n"
            f"❌ 失败: {fail}/{total_accs}\n"
            f"=================="
        )
    
    elif choice == '2':
        sender.reply("请输入用户ID:")
        target_id = sender.input(120000, 1, False)
        if not target_id:
            return
        
        accounts = eval(middleware.bucketGet('s_jx_user', target_id) or '[]')
        if not accounts:
            sender.reply("❌ 用户无账号")
            return
        
        # 显示账号列表
        account_list = "\n========选择账号=======\n[0] 全部账号"
        for i, username in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_jx_auth', username)
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            account_list += f"\n[{i}]{mask_account(username)}({auth_status})"
        account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
        sender.reply(account_list)
        
        account_choice = sender.input(120000, 1, False)
        if not account_choice or account_choice.lower() == 'q':
            sender.reply("✅ 已退出")
            return
        
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
        
        sender.reply(f"✅ 已选择 {len(selected)} 个账号\n请输入授权天数(正数增加/负数减少):")
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        try:
            days = int(days_input)
        except:
            sender.reply("❌ 请输入有效数字")
            return
        
        action = "增加" if days > 0 else "减少"
        sender.reply(f"确认为 {len(selected)} 个账号{action} {abs(days)} 天？回复y确认:")
        if sender.input(120000, 1, False).lower() != 'y':
            sender.reply("✅ 已取消")
            return
        
        success = 0
        for acc in selected:
            try:
                info = json.loads(middleware.bucketGet('s_jx_token', acc))
                result, msg = admin_authorization(acc, info, days)
                if result:
                    sender.reply(f"✅ {mask_account(acc)} 授权成功，到期: {msg}")
                    success += 1
                else:
                    sender.reply(f"❌ {mask_account(acc)} {msg}")
            except Exception as e:
                sender.reply(f"❌ {mask_account(acc)} 异常: {str(e)}")
        
        sender.reply(
            f"=====授权结果=====\n"
            f"✅ 成功: {success}/{len(selected)}\n"
            f"=================="
        )


def show_tutorial():
    """显示酒仙使用教程"""
    tutorial = (
        "=====酒仙教程=====\n"
        "📱 用户指令:\n"
        "• 酒仙登录 - 批量绑定酒仙账号\n"
        "• 酒仙查询 - 查询账号状态和金币信息\n"
        "• 酒仙管理 - 授权/删除/提交青龙\n"
        "• 酒仙教程 - 查看本教程\n"
        "------------------\n"
        "🔧 管理员指令:\n"
        "• 酒仙授权 - 管理员按天数授权\n"
        "• 酒仙检测 - 检测过期账号并清理\n"
        "------------------\n"
        "💡 登录格式:\n"
        "📝 格式: 账号#密码\n"
        "📝 示例: \n"
        "13812345678#password123\n"
        "user@example.com#mypass456\n"
        "💡 支持批量登录，每行一个账号\n"
        "------------------\n"
        "📝 账号获取方式:\n"
        "1. 下载酒仙APP注册账号\n"
        "2. 使用手机号或邮箱注册\n"
        "3. 设置登录密码\n"
        "4. 完成实名认证(签到需要)\n"
        "------------------\n"
        "💰 功能说明:\n"
        "• 账号绑定: 保存账号密码到系统\n"
        "• 状态查询: 查看金币、签到天数等\n"
        "• 授权管理: 付费使用插件功能\n"
        "• 青龙提交: 自动提交到青龙容器\n"
        "• 过期检测: 自动清理过期账号\n"
        "------------------\n"
        "🎯 使用流程:\n"
        "1. 发送\"酒仙登录\"绑定账号\n"
        "2. 发送\"酒仙查询\"查看账号状态\n"
        "3. 发送\"酒仙管理\"选择授权账号\n"
        "4. 选择授权时长并完成支付\n"
        "5. 系统自动提交到青龙容器\n"
        "6. 等待定时任务自动执行签到\n"
        "------------------\n"
        "⚠️ 注意事项:\n"
        "• 授权后才能使用签到功能\n"
        "• 过期账号会被自动清理\n"
        "• 支持微信支付和积分兑换\n"
        "• 管理员可批量授权用户\n"
        "=================="
    )
    sender.reply(tutorial)


def main():
    msg = sender.getMessage()
    
    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('酒仙' in msg or 'jx' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('酒仙' in msg or 'jx' in msg.lower()):
        manage_account()
    elif '酒仙授权' in msg:
        ks_auth()
    elif '酒仙检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    elif '教程' in msg and ('酒仙' in msg or 'jx' in msg.lower()):
        show_tutorial()
    elif sender.getImtype() == 'fake':
        # 定时任务 - 执行检测并通知管理员
        try:
            middleware.notifyMasters(check_auth_status())
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
