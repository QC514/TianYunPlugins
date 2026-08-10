# [rule: ^顺丰(登录|登陆)$|^登(录|陆)顺丰$|^顺丰(查询|管理)$|^(查询|管理)顺丰$|^顺丰教程$|^顺丰后台$|^顺丰(Token)?刷新$|^顺丰快递查询$]
# [disable:true]
# [cron: 56 8,15 * * *]
# [public: true]
# [title: 顺丰速运]
# [icon: https://i.miji.bid/2025/06/27/23807db429fd2b7854eeeb052d604f58.jpeg]
# [open_source: false]
# [class: 工具类]
# [version: 9.7]
# [price: 12.88]
# [admin: false]
# [author: sky2022]
# [service: 2661320550]
# [description: 介绍：顺丰速运插件，支持验证码登录和微信扫码登录<br>指令：顺丰登录、顺丰管理、顺丰查询、顺丰快递查询、顺丰后台、顺丰教程、顺丰刷新<br>定时任务：每天8点和15点自动检测授权过期及CK失效并推送通知<br>更新日志：9.5版本新增定时检测推送，每天8点/15点自动检测授权到期和CK失效状态并通知用户；9.2版本移除CK登录，新增短信验证码接口登录与签名校验；9.0版本将顺丰授权合并到顺丰后台菜单<br>8.9版本新增呆呆面板分组配置，提交变量时支持写入 group<br>8.8版本简化对接配置，统一为面板类型 + 对接面板配置<br>9.6版本新增指令：顺丰快递查询，支持查询寄件和收件的全部信息，需要重新进行验证码或扫码登录，同时登录后不可登录APP，会挤掉Token]
# [param: {"required":true,"key":"dd_sf.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_sf.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_sf.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_sf.panel_group","bool":false,"placeholder":"例:顺丰","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_sf.dd_sf_osname","bool":false,"placeholder":"必填项,例:sfsyUrl","name":"面板变量名","desc":"提交到面板中的顺丰变量名"}]
# [param: {"required":true,"key":"dd_sf.sfVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_sf.sfcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"dd_sf.show_point_status","bool":true,"placeholder":"","name":"显示积分状态","desc":"是否在查询结果中显示积分状态判断"}]
# [param: {"required":false,"key":"dd_sf.show_other_coupons","bool":true,"placeholder":"","name":"显示其他优惠券","desc":"是否显示除免单券外的其他优惠券(仅显示10元以上)"}]
# [param: {"required":true,"key":"dd_sf.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]

import re
import ast
import hmac as _hmac
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal
import requests
import time
import json
import hashlib
import uuid
import random
import string

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_sf_user', key=userid)

SF_CAPTCHA_SEND_PATH = '/api/v1/sf/send-captcha'
SF_CAPTCHA_LOGIN_PATH = '/api/v1/sf/login'
SF_CAPTCHA_API_BASE_URL = 'http://115.190.238.245:17666'
SF_CAPTCHA_API_KEY = '2e3cbe46b243a6672e471fdb36c77930'
SF_CAPTCHA_API_SECRET = '33c1660729f1c14737ac945186ce119859588945b1d3e271eb826a875111eac2'
MOBILE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
CAPTCHA_PATTERN = re.compile(r'^\d{4,8}$')

def format_message(title, content, status="info"):
    status_icons = {
        "info": "ℹ️",
        "success": "✅", 
        "warning": "⚠️",
        "error": "❌",
        "loading": "⏳"
    }
    icon = status_icons.get(status, "ℹ️")
    return f"{icon} {title}\n{content}"

def format_account_info(login_mobile, auth_status, auth_time, **kwargs):
    info = f"=====================\n📱 账号: {login_mobile}"

    if 'coin' in kwargs:
        info += f"\n💎 总计积分: {kwargs['coin']}"
    if 'today_coin' in kwargs:
        info += f"\n🎯 今日积分: {kwargs['today_coin']}"
    if 'auth_time' in kwargs:
        info += f"\n📅 授权到期: {kwargs['auth_time']}"
    else:
        info += f"\n📅 授权到期: {auth_time}"
    if 'account_status' in kwargs:
        info += f"\n📈 账号检测: {kwargs['account_status']}"
    if 'express_count' in kwargs:
        info += f"\n🚚 快递数量: {kwargs['express_count']}"
    if 'coupons' in kwargs:
        info += f"\n🎫 大额优惠券: {kwargs['coupons']}"
    info += "\n====================="
    return info

def generate_qrcode(url):
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception as e:
        print(f"生成二维码失败: {str(e)}")
        return None

def send_qrcode_image(sender, qrcode_url, pay_type):
    pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
    pay_type_name = pay_type_names.get(pay_type, pay_type)
    
    try:
        sender.replyImage(qrcode_url)
        if pay_type == 'qqpay':
            sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\nQQ支付打开图片若是黑屏，长按屏幕进行\"识别二维码\"即可！\n支付过程中输入'q'可取消支付")
        else:
            sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付")
    except:
        if pay_type == 'qqpay':
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！\n[CQ:image,file={qrcode_url}]'
        else:
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n[CQ:image,file={qrcode_url}]'
        sender.reply(pay_msg)

def validate_input(value, max_count, field_name="输入"):
    try:
        value = int(value)
        if value > max_count or value == 0:
            sender.reply(format_message("输入无效", f"请输入 1-{max_count} 之间的数字", "error"))
            exit(0)
        return value
    except ValueError:
        sender.reply(format_message("输入无效", f"{field_name}必须是数字", "error"))
        exit(0)

def get_user_choice(prompt, timeout=120000, allow_quit=True):
    choice = sender.input(timeout, 1, False)
    if choice is None or choice == 'timeout':
        sender.reply('⏰ 操作超时,已退出')
        exit(0)
    elif allow_quit and (choice == 'q' or choice == 'Q'):
        sender.reply('✅ 已退出操作')
        exit(0)
    return choice

def mask_phone(phone):
    if len(phone) >= 11:
        return phone[:3] + '*' * 4 + phone[7:]
    return phone

def _build_captcha_auth_headers(path, body_bytes):
    ts = str(int(time.time()))
    nonce = uuid.uuid4().hex
    body_md5 = hashlib.md5(body_bytes).hexdigest()
    sign_str = f"{SF_CAPTCHA_API_KEY}|{ts}|{nonce}|{path}|{body_md5}"
    signature = _hmac.new(SF_CAPTCHA_API_SECRET.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256).hexdigest()
    return {
        'X-API-Key': SF_CAPTCHA_API_KEY,
        'X-Timestamp': ts,
        'X-Nonce': nonce,
        'X-Signature': signature,
    }

def call_captcha_api(path, payload, timeout=30):
    base_url = str(SF_CAPTCHA_API_BASE_URL or '').rstrip('/')
    body_bytes = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    headers.update(_build_captcha_auth_headers(path, body_bytes))
    try:
        response = requests.post(
            f"{base_url}{path}",
            data=body_bytes,
            headers=headers,
            timeout=timeout,
            verify=False
        )
    except requests.RequestException as exc:
        raise ValueError('请求验证码接口失败') from exc

    if response.status_code >= 400:
        try:
            err = response.json()
            msg = err.get('message') or err.get('code') or f'HTTP {response.status_code}'
        except Exception:
            msg = f'HTTP {response.status_code}'
        raise ValueError(f'验证码接口请求失败: {msg}')

    try:
        result = response.json()
    except ValueError as exc:
        raise ValueError('验证码接口返回的不是 JSON') from exc

    if not isinstance(result, dict):
        raise ValueError('验证码接口返回格式异常')

    return result

def send_sf_sms_captcha(mobile):
    result = call_captcha_api(SF_CAPTCHA_SEND_PATH, {'mobile': mobile})
    if not result.get('success'):
        raise ValueError(result.get('message') or '验证码发送失败')
    return result.get('message')

def build_sms_token_data(account, mobile, data):
    return json.dumps(
        {
            'userId': data.get('userId', '') or data.get('memberId', '') or data.get('login_user_id', ''),
            'memNo': data.get('memNo', ''),
            'mobile': mobile,
            'sign': data.get('sign', ''),
            'deviceId': data.get('deviceId', ''),
            'srcDeviceGuid': data.get('srcDeviceGuid', ''),
            'clientVersion': data.get('clientVersion', ''),
            'ck': data.get('ck', ''),
            'appToken': data.get('token', '') or data.get('appToken', ''),
        },
        ensure_ascii=False,
    )

def login_with_sms_api(mobile, captcha):
    result = call_captcha_api(SF_CAPTCHA_LOGIN_PATH, {'mobile': mobile, 'captcha': captcha})
    if not result.get('success'):
        raise ValueError(result.get('message') or '验证码登录失败')

    data = result.get('data') or {}
    if not isinstance(data, dict):
        raise ValueError('验证码登录接口返回格式异常')

    ck = str(data.get('ck', '')).strip()
    if not ck:
        raise ValueError('验证码登录接口未返回 CK')

    account = str(data.get('login_mobile') or data.get('mobile') or mobile).strip()
    if not account:
        raise ValueError('验证码登录接口未返回账号手机号')

    token_data = build_sms_token_data(account, account, data)
    return token_data, account, mask_phone(account)

def parse_accounts(account_data):
    if not account_data:
        return []
    try:
        if isinstance(account_data, (list, tuple, set)):
            accounts = list(account_data)
        elif isinstance(account_data, str):
            normalized = account_data.strip()
            if not normalized or normalized in ('{}', '[]'):
                return []
            try:
                parsed = ast.literal_eval(normalized)
            except Exception:
                return [normalized]
            if isinstance(parsed, (list, tuple, set)):
                accounts = list(parsed)
            elif parsed is None:
                return []
            else:
                accounts = [str(parsed)]
        else:
            accounts = [str(account_data)]

        return list(dict.fromkeys(str(item) for item in accounts if item))
    except Exception:
        return []

def get_auth_status(account_vip, today_time):
    if not account_vip:
        return "⚠️ 未授权", "无"
    elif account_vip <= today_time:
        return "❌ 已过期", account_vip
    else:
        return "✅ 已授权", account_vip

def has_valid_auth(account_vip, compare_date):
    auth_value = str(account_vip or '').strip()
    return bool(auth_value) and auth_value > compare_date

def normalize_panel_type(panel_type_value, legacy_use_daidai_value='false'):
    value = str(panel_type_value or '').strip().lower()

    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    if value:
        return ''

    legacy_value = str(legacy_use_daidai_value or '').strip().lower()
    if legacy_value == 'true':
        return 'daidai'
    return 'qinglong'

def getusercontent():
    dd_sf_osname = middleware.bucketGet('dd_sf', 'dd_sf_osname') or 'dd_sf_token'
    panel_type_value = middleware.bucketGet('dd_sf', 'panel_type') or ''
    panel_config_value = (middleware.bucketGet('dd_sf', 'panel_config') or '').strip()
    panel_group = (middleware.bucketGet('dd_sf', 'panel_group') or '').strip()
    legacy_ql_config = middleware.bucketGet('dd_sf', 'dd_sf_qlname') or ''
    legacy_use_daidai = middleware.bucketGet('dd_sf', 'use_daidai') or 'false'
    legacy_dd_config = middleware.bucketGet('dd_sf', 'dd_sf_ddname') or ''
    dd_managecommand = middleware.bucketGet('dd_sf', 'dd_managecommand') or '顺丰管理'
    dd_querycommand = middleware.bucketGet('dd_sf', 'dd_querycommand') or '顺丰查询'
    dd_signcommand = middleware.bucketGet('dd_sf', 'dd_signcommand') or '顺丰登录'
    sfVipmoney = Decimal(middleware.bucketGet('dd_sf', 'sfVipmoney') or '1')
    sfcoin = int(middleware.bucketGet('dd_sf', 'sfcoin') or '0')

    show_point_status = middleware.bucketGet('dd_sf', 'show_point_status') or 'false'
    show_point_status = show_point_status.lower() == 'true'
    show_other_coupons = middleware.bucketGet('dd_sf', 'show_other_coupons') or 'false'
    show_other_coupons = show_other_coupons.lower() == 'true'
    use_ma_pay = middleware.bucketGet('dd_sf', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'

    panel_type = normalize_panel_type(panel_type_value, legacy_use_daidai)
    if not panel_type:
        sender.reply(format_message("配置错误",
            "对接面板类型填写无效\n请填写以下任一值:\n• 青龙 / 青龙面板 / QL\n• 呆呆 / 呆呆面板 / Daidai", "error"))
        exit(0)

    use_daidai = panel_type == 'daidai'
    if use_daidai:
        dd_sf_ddname = panel_config_value or legacy_dd_config
        dd_sf_qlname = legacy_ql_config
    else:
        dd_sf_qlname = panel_config_value or legacy_ql_config
        dd_sf_ddname = legacy_dd_config

    return (dd_sf_osname, dd_sf_qlname, dd_managecommand, dd_querycommand,
            dd_signcommand, sfVipmoney, sfcoin, show_point_status,
            show_other_coupons, use_ma_pay, use_daidai, dd_sf_ddname, panel_group)

def seekql():
    try:
        if not dd_sf_qlname:
            sender.reply(format_message("配置错误", 
                "未配置青龙面板信息\n请在插件配置中填写:\n• 对接面板类型: 青龙\n• 对接面板配置: Host丨ClientID丨ClientSecret\n• 使用中文丨分隔\n• 示例:\nhttp://ql.example.com丨abcd丨1234", "error"))
            exit(0)
            
        qllist = dd_sf_qlname.split('丨')
        if len(qllist) != 3:
            sender.reply(format_message("格式错误", 
                f"青龙面板配置格式错误\n当前格式: {dd_sf_qlname}\n正确格式:\nHost丨ClientID丨ClientSecret", "error"))
            exit(0)
            
        QLurl = qllist[0].strip()
        ClientID = qllist[1].strip()
        ClientSecret = qllist[2].strip()
        
        if not all([QLurl, ClientID, ClientSecret]):
            sender.reply(format_message("参数错误", 
                "青龙面板配置参数不完整\n请确保以下参数都已填写:\n• 青龙面板地址(Host)\n• 应用ID(ClientID)\n• 应用密钥(ClientSecret)", "error"))
            exit(0)
            
        if not QLurl.startswith(('http://', 'https://')):
            sender.reply(format_message("地址错误", 
                f"青龙地址格式错误\n当前地址: {QLurl}\n正确格式:\n• http://qinglong.example.com\n• https://ql.example.com:5700", "error"))
            exit(0)
            
        try:
            qltoken = QLtoken(QLurl=QLurl, ClientID=ClientID, ClientSecret=ClientSecret)
            return QLurl, qltoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")
            
    except Exception as e:
        sender.reply(format_message("连接失败", 
            f"无法连接青龙面板\n请检查:\n1. 青龙面板是否运行\n2. 网络是否正常\n3. 配置是否正确\n4. 错误信息: {str(e)}\n\n当前配置:\n• 地址: {QLurl if 'QLurl' in locals() else '未设置'}\n• 应用ID: {ClientID[:4] + '****' if 'ClientID' in locals() else '未设置'}", "error"))
        exit(0)

def get_ql_headers(content_type="application/json"):
    return {
        "Authorization": f"Bearer {qltoken}",
        "accept": "application/json",
        "Content-Type": content_type
    }

def delenvs(id):
    if use_daidai:
        dd_delenvs(id)
        return
    if id is None:
        return
    url = f"{QLurl}/open/envs"
    headers = get_ql_headers()
    data = [id]
    response = requests.delete(url, headers=headers, json=data).json()

def allenvs(osname, account):
    if use_daidai:
        return dd_allenvs(osname, account)
    url = f"{QLurl}/open/envs"
    headers = get_ql_headers()
    response = requests.get(url=url, headers=headers).json()
    
    if response['code'] == 200:
        envslist = response['data']
        for envs in envslist:
            envname = envs['name']
            remarks = envs['remarks']
            if remarks is None:
                continue
            if osname == envname and str(account) in remarks:
                return envs['id']
        return None
    else:
        sender.reply(format_message("连接失败", "连接青龙获取变量失败", "error"))
        exit(0)

def Addenvs(osname, value, account, phone, target_userid=None, expire_time=None):
    phone = mask_phone(phone)
    actual_userid = target_userid if target_userid else userid
    expire_info = f'丨到期:{expire_time}' if expire_time else ''

    if use_daidai:
        env_id = dd_allenvs(osname, account)
        if env_id is None:
            DDcreate(osname, value, account, phone, target_userid, expire_time)
        else:
            DDupdate(osname, value, account, env_id, phone, target_userid, expire_time)
        return

    qlid = allenvs(osname, account)

    if qlid is None:
        QLzt(osname, value, account, phone, target_userid, expire_time)
    else:
        QLupdate(osname, value, account, qlid, phone, target_userid, expire_time)

def QLupdate(osname, value, account, qlid, phone, target_userid=None, expire_time=None):
    actual_userid = target_userid if target_userid else userid
    expire_info = f'丨到期:{expire_time}' if expire_time else ''
    qlurl = f"{QLurl}/open/envs"

    data = {
        "value": value,
        "name": osname,
        "remarks": f'顺丰:{account}丨用户:{actual_userid}丨手机:{phone}{expire_info}丨顺丰管理',
        "id": qlid
    }
    
    headers = get_ql_headers()
    response = requests.put(qlurl, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        response_json = response.json()
        data = response_json['data']
        if data is None:
            exit(0)
        return data['id'], data['createdAt']
    else:
        sender.reply(format_message("更新失败", "更新变量失败,请联系管理员处理", "error"))
        exit(0)

def QLzt(osname, value, account, phone, target_userid=None, expire_time=None):
    try:
        actual_userid = target_userid if target_userid else userid
        expire_info = f'丨到期:{expire_time}' if expire_time else ''
        qlurl = f"{QLurl}/open/envs"

        data = [{
            "value": value,
            "name": osname,
            "remarks": f'顺丰:{account}丨用户:{actual_userid}丨手机:{phone}{expire_info}丨顺丰管理'
        }]
        
        headers = get_ql_headers()
        response = requests.post(qlurl, headers=headers, json=data)
        
        if response.status_code != 200:
            sender.reply(format_message("添加变量失败", f"请求失败\n状态码: {response.status_code}", "error"))
            exit(0)
            
        result = response.json()
        if result.get('code') != 200:
            sender.reply(format_message("添加变量失败", f"青龙返回错误\n错误信息: {result.get('message')}", "error"))
            exit(0)
            
        if "value must be unique" in response.text:
            return
            
        data = result.get('data')
        if not data or not isinstance(data, list) or len(data) == 0:
            sender.reply(format_message("添加变量失败", "青龙返回数据异常", "error"))
            exit(0)
            
        return data[0].get('id')
        
    except Exception as e:
        sender.reply(format_message("系统错误", f"添加青龙变量失败\n错误信息: {str(e)}", "error"))
        exit(0)

def QLtoken(QLurl, ClientID, ClientSecret):
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        
        if response.status_code != 200:
            sender.reply(format_message("请求失败", 
                f"青龙API请求失败\n状态码: {response.status_code}\n请检查:\n• API地址是否正确\n• 面板是否正常运行", "error"))
            exit(0)
            
        result = response.json()
        if "token" in result.get('data', {}):
            return result['data']['token']
        else:
            sender.reply(format_message("认证失败", 
                "获取Token失败\n请检查:\n• ClientID是否正确\n• ClientSecret是否正确\n• 应用是否有权限", "error"))
            exit(0)
            
    except requests.exceptions.RequestException as e:
        sender.reply(format_message("网络错误", 
            f"连接青龙面板失败\n请检查:\n• 青龙地址是否正确\n• 网络是否正常\n• 错误信息: {str(e)}", "error"))
        exit(0)
    except Exception as e:
        sender.reply(format_message("系统错误",
            f"处理请求时出错\n请检查:\n• 配置格式是否正确\n• 错误信息: {str(e)}", "error"))
        exit(0)

def seekdd():
    try:
        if not dd_sf_ddname:
            sender.reply(format_message("配置错误",
                "未配置呆呆面板信息\n请在插件配置中填写:\n• 对接面板类型: 呆呆\n• 对接面板配置: Host丨AppKey丨AppSecret\n• 使用中文丨分隔", "error"))
            exit(0)

        ddlist = dd_sf_ddname.split('丨')
        if len(ddlist) != 3:
            sender.reply(format_message("格式错误",
                f"呆呆面板配置格式错误\n当前格式: {dd_sf_ddname}\n正确格式:\nHost丨AppKey丨AppSecret", "error"))
            exit(0)

        DDurl = ddlist[0].strip()
        AppKey = ddlist[1].strip()
        AppSecret = ddlist[2].strip()

        if not all([DDurl, AppKey, AppSecret]):
            sender.reply(format_message("参数错误",
                "呆呆面板配置参数不完整\n请确保以下参数都已填写:\n• 面板地址(Host)\n• AppKey\n• AppSecret", "error"))
            exit(0)

        if not DDurl.startswith(('http://', 'https://')):
            sender.reply(format_message("地址错误",
                f"呆呆面板地址格式错误\n当前地址: {DDurl}\n正确格式:\n• http://panel.example.com\n• https://panel.example.com", "error"))
            exit(0)

        try:
            ddtoken = DDtoken(DDurl=DDurl, AppKey=AppKey, AppSecret=AppSecret)
            return DDurl, ddtoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")

    except SystemExit:
        raise
    except Exception as e:
        sender.reply(format_message("连接失败",
            f"无法连接呆呆面板\n请检查:\n1. 面板是否运行\n2. 网络是否正常\n3. 配置是否正确\n4. 错误信息: {str(e)}\n\n当前配置:\n• 地址: {DDurl if 'DDurl' in locals() else '未设置'}\n• AppKey: {AppKey[:4] + '****' if 'AppKey' in locals() else '未设置'}", "error"))
        exit(0)

def DDtoken(DDurl, AppKey, AppSecret):
    try:
        url = f'{DDurl}/api/open-api/token'
        data = {"app_key": AppKey, "app_secret": AppSecret}
        response = requests.post(url, json=data)

        if response.status_code != 200:
            sender.reply(format_message("请求失败",
                f"呆呆面板API请求失败\n状态码: {response.status_code}\n请检查:\n• API地址是否正确\n• 面板是否正常运行", "error"))
            exit(0)

        result = response.json()
        access_token = result.get('data', {}).get('access_token')
        if access_token:
            return access_token
        else:
            sender.reply(format_message("认证失败",
                "获取Token失败\n请检查:\n• AppKey是否正确\n• AppSecret是否正确\n• 应用是否有权限", "error"))
            exit(0)

    except requests.exceptions.RequestException as e:
        sender.reply(format_message("网络错误",
            f"连接呆呆面板失败\n请检查:\n• 面板地址是否正确\n• 网络是否正常\n• 错误信息: {str(e)}", "error"))
        exit(0)
    except SystemExit:
        raise
    except Exception as e:
        sender.reply(format_message("系统错误",
            f"处理请求时出错\n请检查:\n• 配置格式是否正确\n• 错误信息: {str(e)}", "error"))
        exit(0)

def get_dd_headers(content_type="application/json"):
    return {
        "Authorization": f"Bearer {panel_token}",
        "accept": "application/json",
        "Content-Type": content_type
    }

def dd_allenvs(osname, account):
    url = f"{panel_url}/api/envs"
    headers = get_dd_headers()
    params = {"keyword": str(account), "page_size": 100}
    response = requests.get(url=url, headers=headers, params=params).json()

    data_list = response.get('data', [])
    if isinstance(data_list, list):
        for envs in data_list:
            envname = envs.get('name', '')
            remarks = envs.get('remarks', '')
            if remarks is None:
                continue
            if osname == envname and str(account) in remarks:
                return envs['id']
        return None
    else:
        sender.reply(format_message("连接失败", "连接呆呆面板获取变量失败", "error"))
        exit(0)

def dd_delenvs(id):
    if id is None:
        return
    url = f"{panel_url}/api/envs/{id}"
    headers = get_dd_headers()
    requests.delete(url, headers=headers)

def DDcreate(osname, value, account, phone, target_userid=None, expire_time=None):
    try:
        actual_userid = target_userid if target_userid else userid
        expire_info = f'丨到期:{expire_time}' if expire_time else ''
        url = f"{panel_url}/api/envs"

        data = {
            "value": value,
            "name": osname,
            "remarks": f'顺丰:{account}丨用户:{actual_userid}丨手机:{phone}{expire_info}丨顺丰管理'
        }
        if panel_group:
            data["group"] = panel_group

        headers = get_dd_headers()
        response = requests.post(url, headers=headers, json=data)

        if response.status_code not in (200, 201):
            sender.reply(format_message("添加变量失败", f"请求失败\n状态码: {response.status_code}", "error"))
            exit(0)

        result = response.json()
        resp_data = result.get('data')
        if resp_data:
            return resp_data.get('id')

    except SystemExit:
        raise
    except Exception as e:
        sender.reply(format_message("系统错误", f"添加变量失败\n错误信息: {str(e)}", "error"))
        exit(0)

def DDupdate(osname, value, account, env_id, phone, target_userid=None, expire_time=None):
    actual_userid = target_userid if target_userid else userid
    expire_info = f'丨到期:{expire_time}' if expire_time else ''
    url = f"{panel_url}/api/envs/{env_id}"

    data = {
        "value": value,
        "name": osname,
        "remarks": f'顺丰:{account}丨用户:{actual_userid}丨手机:{phone}{expire_info}丨顺丰管理'
    }
    if panel_group:
        data["group"] = panel_group

    headers = get_dd_headers()
    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        return env_id, None
    else:
        sender.reply(format_message("更新失败", "更新变量失败,请联系管理员处理", "error"))
        exit(0)

def session_ids(url_or_ck):
    if not url_or_ck:
        sender.reply(format_message("输入无效", "输入内容无效，请重新输入！", "error"))
        exit(0)

    if url_or_ck.startswith(('http://', 'https://')):
        try:
            response = requests.get(url_or_ck, allow_redirects=False)
            cookie_str = str(response.headers)
        except requests.exceptions.RequestException as e:
            sender.reply(format_message("网络错误", f"网络请求失败: {str(e)}", "error"))
            exit(0)
    else:
        cookie_str = url_or_ck

    try:
        session_id_pattern = r'sessionId=([^;]+)'
        login_mobile_pattern = r'_login_mobile_=([^;]+)'

        session_id_match = re.search(session_id_pattern, cookie_str)
        login_mobile_match = re.search(login_mobile_pattern, cookie_str)

        if not session_id_match or not login_mobile_match:
            sender.reply(format_message("获取失败", "无法从输入中获取用户信息，请检查CK是否正确！", "error"))
            exit(0)

        session_id = session_id_match.group(1)
        login_mobile = login_mobile_match.group(1)

        if url_or_ck.startswith(('http://', 'https://')) and '用户手机号校验未通过' in response.text:
            sender.reply(format_message("校验失败", "用户手机号校验未通过，请检查账号状态！", "error"))
            exit(0)

        return session_id, login_mobile
        
    except requests.exceptions.RequestException as e:
        sender.reply(format_message("网络错误", f"网络请求失败: {str(e)}", "error"))
        exit(0)
    except Exception as e:
        sender.reply(format_message("处理错误", f"处理用户信息时出错: {str(e)}", "error"))
        exit(0)

def query_user_info(session_id):
    url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberIntegral~userInfoService~queryUserInfo"
    
    headers = {
        "Cookie": f"sessionId={session_id}",
        "Content-Type": "application/json",
        "syscode": "MCS-MIMP-CORE"
    }
    
    data = {
        "sysCode": "ESG-CEMP-CORE",
        "optionalColumns": ["usablePoint", "cycleSub", "leavePoint"],
        "token": "zeTLTYeG0bLetfRk"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get('success'):
            obj = result.get('obj', {})
            usable_point = obj.get('usablePoint', 0)
            cycle_add = obj.get('cycleAdd', 0)
            point_clear_cycle = obj.get('pointClearCycle', '')
            expiring_points = usable_point - cycle_add if cycle_add else usable_point
            if point_clear_cycle:
                try:
                    original_date = datetime.strptime(point_clear_cycle, "%Y-%m-%d")
                    next_year_date = original_date.replace(year=original_date.year + 1)
                    point_clear_cycle = next_year_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            
            return {
                'usable_point': usable_point,
                'cycle_add': cycle_add,
                'expiring_points': max(0, expiring_points),
                'point_clear_cycle': point_clear_cycle
            }
    except Exception as e:
        print(f"查询用户信息失败: {str(e)}")
        return None
    
    return None

def todaycoin(session_id):
    pageNo = 1
    coin = 0
    user_info = query_user_info(session_id)
    
    while True:
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberIntegral~memberPoint~queryMemberPointDetail"

        headers = {
            "Cookie": f"sessionId={session_id}"
        }

        data = {
            "type": "ALL",
            "pageNo": pageNo,
            "pageSize": 10
        }

        response = requests.post(url, headers=headers, json=data).json()
        success = response['success']
        data = response['obj']['data']
        if len(data) < 1:
            return 0, '0', user_info
        if success:
            allcoin = response['obj']['usablePoint']
            for coinjson in data:
                createTm = coinjson['createTm']
                datetime_obj = datetime.strptime(createTm, "%Y-%m-%d %H:%M:%S")
                date_str = datetime_obj.strftime("%Y-%m-%d")
                if date_str < str(today_time):
                    break
                else:
                    opCode = coinjson['opCode']
                    pointVal = coinjson['pointVal']
                    if opCode == 'ADD':
                        coin = coin + int(pointVal)
                    else:
                        continue
            createTm = data[-1]['createTm']
            datetime_obj = datetime.strptime(createTm, "%Y-%m-%d %H:%M:%S")
            date_str = datetime_obj.strftime("%Y-%m-%d")
            if date_str >= str(today_time):
                pageNo = pageNo + 1
            else:
                break
    return coin, allcoin, user_info

def ValueErrors(value, count):
    return validate_input(value, count)

def sytTokens(payload, deviceId):
    t = int(time.time() * 1000)
    datamd5 = generate_md5(payload + '&080R3MAC57J2{A19!$3:WO{I<1N$31BI')
    deviceidmd5 = generate_md5(
        deviceId + f'{t}' + '9.77.02NBF+BE4{@P:@X${Q9BAE>{PAK!D:N*^CNsc' + datamd5 + '705088894ad6ef475bdf4875c9d533b8&2NBF+BE4{@P:@X${Q9BAE>{PAK!D:N*^')

    sytToken = generate_md5(deviceidmd5 + '&0HQ%H91K&AA{DH$*XV>XR)VKL:QFE{&%')
    return sytToken, t

def generate_md5(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    md5_digest = md5_hash.hexdigest()

    return md5_digest

def build_token_url(sign):
    encoded_string = urllib.parse.quote(sign)
    return f'https://mcs-mimp-web.sf-express.com/mcs-mimp/share/app/shareRedirect?sign={encoded_string}&source=SFAPP&bizCode=647@RnlvejM1R3VTSVZ6d3BNaXJxRFpOUVVtQkp0ZnFpNDBKdytobm5TQWxMeHpVUXVrVzVGMHVmTU5BVFA1bXlwcw=='

def get_ck_from_url(token_url):
    try:
        session = requests.Session()
        session.get(token_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
        }, timeout=15)
        cookies = session.cookies.get_dict()
        session_id = cookies.get('sessionId', '')
        login_mobile = cookies.get('_login_mobile_', '')
        login_user_id = cookies.get('_login_user_id_', '')
        if session_id and login_mobile:
            return f'sessionId={session_id};_login_mobile_={login_mobile};_login_user_id_={login_user_id}'
        return None
    except Exception as e:
        print(f"获取CK失败: {str(e)}")
        return None

def validate_ck(ck):
    if not ck:
        return False
    try:
        session_id_match = re.search(r'sessionId=([^;]+)', ck)
        if not session_id_match:
            return False
        session_id = session_id_match.group(1)
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberIntegral~memberPoint~queryMemberPointDetail"
        headers = {
            "Cookie": f"sessionId={session_id}",
            "Content-Type": "application/json"
        }
        data = {"type": "ALL", "pageNo": 1, "pageSize": 1}
        response = requests.post(url, headers=headers, json=data, timeout=10)
        result = response.json()
        return result.get('success', False)
    except:
        return False

def get_ck_with_fallback(account):
    td = parse_token_data(account)
    if not td:
        return None

    saved_ck = td.get('ck', '')
    if saved_ck and validate_ck(saved_ck):
        return saved_ck

    sign = td.get('sign', '')
    userId = td.get('userId', '')
    memNo = td.get('memNo', '')
    mobile = td.get('mobile', '')
    deviceId = td.get('deviceId', '')

    if sign:
        token_url = build_token_url(sign)
        new_ck = get_ck_from_url(token_url)
        if new_ck and validate_ck(new_ck):
            save_token_data(account, userId, memNo, mobile, sign, deviceId, new_ck)
            return new_ck

        if userId and memNo and mobile:
            new_sign = refresh_sign(userId, memNo, mobile, deviceId)
            if new_sign:
                new_url = build_token_url(new_sign)
                new_ck = get_ck_from_url(new_url)
                if new_ck and validate_ck(new_ck):
                    save_token_data(account, userId, memNo, mobile, new_sign, deviceId, new_ck)
                    return new_ck
                save_token_data(account, userId, memNo, mobile, new_sign, deviceId, '')
                return new_ck

    if userId and memNo and mobile:
        new_sign = refresh_sign(userId, memNo, mobile, deviceId)
        if new_sign:
            new_url = build_token_url(new_sign)
            new_ck = get_ck_from_url(new_url)
            save_token_data(account, userId, memNo, mobile, new_sign, deviceId, new_ck or '')
            if new_ck and validate_ck(new_ck):
                return new_ck

    raw = middleware.bucketGet(bucket='dd_sf_token', key=account)
    if raw and raw.startswith('http'):
        new_ck = get_ck_from_url(raw)
        return new_ck

    return None

def parse_token_data(account):
    raw = middleware.bucketGet(bucket='dd_sf_token', key=account)
    if not raw:
        return None
    raw_text = str(raw).strip()
    try:
        data = json.loads(raw_text)
        if isinstance(data, dict):
            data.setdefault('sign', '')
            data.setdefault('mobile', account)
            data.setdefault('userId', '')
            data.setdefault('memNo', '')
            data.setdefault('deviceId', '')
            data.setdefault('srcDeviceGuid', '')
            data.setdefault('clientVersion', '')
            data.setdefault('ck', '')
            data.setdefault('appToken', '')
            return data
    except (json.JSONDecodeError, TypeError):
        pass

    result = {'sign': '', 'mobile': account, 'userId': '', 'memNo': '', 'deviceId': '', 'srcDeviceGuid': '', 'clientVersion': '', 'ck': '', 'appToken': ''}
    if 'sessionId=' in raw_text:
        result['ck'] = raw_text
        login_mobile_match = re.search(r'_login_mobile_=([^;]+)', raw_text)
        if login_mobile_match:
            result['mobile'] = login_mobile_match.group(1)
        return result

    try:
        parsed = urllib.parse.urlparse(raw_text)
        params = urllib.parse.parse_qs(parsed.query)
        if 'sign' in params:
            result['sign'] = urllib.parse.unquote(params['sign'][0])
    except Exception:
        pass
    return result

def save_token_data(account, userId, memNo, mobile, sign, deviceId='', ck='', appToken='', srcDeviceGuid='', clientVersion=''):
    old_data = parse_token_data(account) or {}
    appToken = appToken or old_data.get('appToken', '')
    srcDeviceGuid = srcDeviceGuid or old_data.get('srcDeviceGuid', '')
    clientVersion = clientVersion or old_data.get('clientVersion', '')
    data = json.dumps(
        {
            'userId': userId,
            'memNo': memNo,
            'mobile': mobile,
            'sign': sign,
            'deviceId': deviceId,
            'srcDeviceGuid': srcDeviceGuid,
            'clientVersion': clientVersion,
            'ck': ck,
            'appToken': appToken,
        },
        ensure_ascii=False,
    )
    middleware.bucketSet(bucket='dd_sf_token', key=account, value=data)

def get_token_as_ck(account):
    return get_ck_with_fallback(account)

def refresh_sign(userId, memNo, mobile, deviceId=''):
    try:
        if not deviceId:
            deviceId = str(uuid.uuid4())
        url = "https://ccsp-egmas.sf-express.com/cx-app-member/member/app/user/universalSign"
        payload = json.dumps({
            "mobile": mobile,
            "userId": userId,
            "memNo": memNo,
            "name": "mcs-mimp-web.sf-express.com",
            "extra": "",
            "needReqTime": "1"
        })
        sytToken, t = sytTokens(payload, deviceId)
        headers = {
            'User-Agent': "okhttp/4.9.1",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'jsbundle': "705088894ad6ef475bdf4875c9d533b8",
            'clientVersion': "9.77.0",
            'languageCode': "sc",
            'systemVersion': "13",
            'deviceId': deviceId,
            'regionCode': "CN",
            'carrier': "unknown",
            'screenSize': "1080x2400",
            'sytToken': sytToken,
            'timeInterval': f"{t}",
            'model': "MEIZU 20",
            'mediaCode': "AndroidML"
        }
        response = requests.post(url, data=payload, headers=headers)
        new_sign = response.json()['obj']['sign']
        return new_sign
    except Exception as e:
        print(f"刷新sign失败: {str(e)}")
        return None

def get_token_url_auto_refresh(account):
    token_data = parse_token_data(account)
    if not token_data:
        return None, False
    sign = token_data.get('sign', '')
    userId = token_data.get('userId', '')
    memNo = token_data.get('memNo', '')
    mobile = token_data.get('mobile', '')
    deviceId = token_data.get('deviceId', '')
    if not sign:
        if userId and memNo and mobile:
            new_sign = refresh_sign(userId, memNo, mobile, deviceId)
            if new_sign:
                new_url = build_token_url(new_sign)
                new_ck = get_ck_from_url(new_url)
                save_token_data(account, userId, memNo, mobile, new_sign, deviceId, new_ck or '')
                return new_url, True
        raw = middleware.bucketGet(bucket='dd_sf_token', key=account)
        if raw and raw.startswith('http'):
            return raw, False
        return None, False
    token_url = build_token_url(sign)
    try:
        response = requests.get(token_url, allow_redirects=False, timeout=10)
        session_id_match = re.search(r'sessionId=([^;]+);', str(response.headers))
        if session_id_match:
            return token_url, False
    except:
        pass
    if not userId or not memNo or not mobile:
        return token_url, False
    new_sign = refresh_sign(userId, memNo, mobile, deviceId)
    if new_sign:
        new_url = build_token_url(new_sign)
        new_ck = get_ck_from_url(new_url)
        save_token_data(account, userId, memNo, mobile, new_sign, deviceId, new_ck or '')
        return new_url, True
    return token_url, False

def refresh_all_signs():
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)
    users = middleware.bucketAllKeys(bucket='dd_sf_user')
    if not users:
        sender.reply(format_message("刷新结果", "未找到任何绑定账号", "error"))
        return
    sender.reply(format_message("开始刷新", f"共找到: {len(users)}个用户\n⏳ 刷新中请稍候...", "loading"))
    success_count = 0
    fail_count = 0
    skip_count = 0
    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_sf_user', key=user)
            if not accountlist:
                continue
            accounts = parse_accounts(accountlist)
            for account in accounts:
                try:
                    token_data = parse_token_data(account)
                    if not token_data:
                        fail_count += 1
                        continue
                    userId = token_data.get('userId', '')
                    memNo = token_data.get('memNo', '')
                    mobile = token_data.get('mobile', '')
                    deviceId = token_data.get('deviceId', '')
                    if not userId or not memNo or not mobile:
                        skip_count += 1
                        continue
                    new_sign = refresh_sign(userId, memNo, mobile, deviceId)
                    if new_sign:
                        new_url = build_token_url(new_sign)
                        new_ck = get_ck_from_url(new_url)
                        save_token_data(account, userId, memNo, mobile, new_sign, deviceId, new_ck or '')
                        accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
                        if accountVip and accountVip > today_time:
                            try:
                                ck = new_ck or get_ck_from_url(new_url)
                                if ck:
                                    phone = mask_phone(account)
                                    Addenvs(osname=dd_sf_osname, value=ck, account=account, phone=phone, target_userid=user, expire_time=accountVip)
                            except:
                                pass
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    print(f"刷新账号 {account} 失败: {str(e)}")
                    fail_count += 1
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    result_msg = f"""=====登录态刷新完成=====
✅ 刷新成功: {success_count}个账号
⏭️ 跳过(无法刷新): {skip_count}个账号
❌ 刷新失败: {fail_count}个账号
=================="""
    sender.reply(result_msg)

def sf_captcha_login(sender):
    guide = """
=====短信验证码登录=====
请输入顺丰绑定手机号
------------------
回复"q"可随时退出
=================="""
    sender.reply(guide)

    mobile = get_user_choice('请输入手机号')
    mobile = str(mobile or '').strip()
    if not MOBILE_PATTERN.match(mobile):
        sender.reply(format_message('登录失败', '手机号格式错误，请输入 11 位大陆手机号', 'error'))
        exit(0)

    try:
        send_message = send_sf_sms_captcha(mobile)
    except ValueError as exc:
        sender.reply(format_message('发送失败', str(exc), 'error'))
        exit(0)

    sender.reply(format_message('发送成功', f'\n请输入收到的短信验证码', 'success'))

    retry_count = 3
    while retry_count > 0:
        captcha = get_user_choice('请输入验证码')
        captcha = str(captcha or '').strip()
        if not CAPTCHA_PATTERN.match(captcha):
            retry_count -= 1
            if retry_count == 0:
                sender.reply(format_message('登录失败', '验证码格式错误次数过多，请重新执行顺丰登录', 'error'))
                exit(0)
            sender.reply(format_message('输入有误', f'验证码格式错误，请重新输入\n剩余次数: {retry_count}', 'warning'))
            continue

        try:
            return login_with_sms_api(mobile, captcha)
        except ValueError as exc:
            retry_count -= 1
            if retry_count == 0:
                sender.reply(format_message('登录失败', f'{exc}\n请重新执行顺丰登录', 'error'))
                exit(0)
            sender.reply(format_message('校验失败', f'{exc}\n剩余次数: {retry_count}', 'warning'))

    sender.reply(format_message('登录失败', '验证码重试次数已耗尽，请重新执行顺丰登录', 'error'))
    exit(0)

def sf_login(sender):
    try:
        scan_msg = """
=====微信扫码登录=====
⌛ 正在加载二维码...
⏳ 请稍候...
=================="""
        mesid3 = sender.reply(scan_msg)
        
        url_getQr = 'https://wxsm.linzixuan.top/api/getQr'
        url_checkQr = 'https://wxsm.linzixuan.top/api/checkQr'
        response = requests.post(url_getQr, json={'project': 'sf'})
        response_data = response.json()
        if not response_data.get('data') or 'uuid' not in response_data['data']:
            sender.reply('❌ 获取二维码失败!')
            exit(0)
            
        QRcode = response_data['data']['uuid']
        QRcodeImg = response_data['data']['img_url']

        mesid = sender.replyImage(QRcodeImg)
        
        scan_guide = """
=====登录说明=====
📱 请使用微信扫描二维码登录
------------------
⚠️ 注意事项:
1. 请确保已用微信登录过顺丰APP和微信小程序
2. 如果登录失败,请先下载顺丰APP和登录小程序
3. 扫码后请等待5分钟内完成授权
=================="""
        mesid2 = sender.reply(scan_guide)
        
        retry = 150
        check_interval = 2
        while True:
            time.sleep(check_interval)
            data = {'project': 'sf', 'uuid': QRcode}
            try:
                response = requests.post(url_checkQr, json=data, timeout=10)
                response_data = response.json()
                
                if response_data.get('code') == 0 and response_data.get('data', {}).get('code'):
                    code = response_data['data']['code']
                    break
                elif response_data.get('code') == 2:
                    sender.reply('❌ 二维码已过期,请重新尝试!')
                    exit(0)
                else:
                    retry -= 1
                    if retry == 0:
                        sender.reply('❌ 扫码超时,请重新尝试!')
                        exit(0)
            except requests.exceptions.Timeout:
                retry -= 1
                if retry == 0:
                    sender.reply('❌ 网络请求超时,请检查网络后重试!')
                    exit(0)
            except Exception as e:
                retry -= 1
                if retry == 0:
                    sender.reply(f'❌ 检查扫码状态失败: {str(e)}')
                    exit(0)

        deviceId = str(uuid.uuid4())
        url = "https://ccsp-egmas.sf-express.com/cx-app-member/member/app/weixin/getAccessTokenByCode"
        payload = json.dumps({"code": code})
        sytToken, t = sytTokens(payload, deviceId)
        headers = {
            'User-Agent': "okhttp/4.9.1",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'jsbundle': "705088894ad6ef475bdf4875c9d533b8",
            'clientVersion': "9.77.0",
            'languageCode': "sc",
            'systemVersion': "13",
            'deviceId': deviceId,
            'regionCode': "CN",
            'carrier': "unknown",
            'screenSize': "1080x2400",
            'sytToken': sytToken,
            'timeInterval': f"{t}",
            'model': "MEIZU 20",
            'mediaCode': "AndroidML"
        }
        response = requests.post(url, data=payload, headers=headers)
        wx_login_obj = response.json().get('obj', {})
        url = "https://ccsp-egmas.sf-express.com/cx-app-member/member/app/user/universalSign"
        account = wx_login_obj['memInfos'][0]['userId']
        memNo = wx_login_obj['memInfos'][0]['memNo']
        mobile = wx_login_obj['memInfos'][0]['mobile']
        wx_app_token = wx_login_obj.get('token', '')

        payload = json.dumps({
            "mobile": mobile,
            "userId": account,
            "memNo": memNo,
            "name": "mcs-mimp-web.sf-express.com",
            "extra": "",
            "needReqTime": "1"
        })
        sytToken, t = sytTokens(payload, deviceId)
        headers['sytToken'] = sytToken
        headers['timeInterval'] = str(t)
        response = requests.post(url, data=payload, headers=headers)
        sign = response.json()['obj']['sign']
        Token = build_token_url(sign)

        try:
            web_headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 13; MEIZU 20 Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/122.0.6261.120 Mobile Safari/537.36 XWEB/1220133 MMWEBSDK/20231202 MMWEBID/2247 MicroMessenger/8.0.47.2560(0x28002F30) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive'
            }
            requests.get(Token, headers=web_headers, allow_redirects=True, timeout=10)
        except Exception as e:
            print(f"访问Web端URL时出现异常(可忽略): {str(e)}")

        login_ck = get_ck_from_url(Token)
        token_data = json.dumps(
            {
                'userId': account,
                'memNo': memNo,
                'mobile': mobile,
                'sign': sign,
                'deviceId': deviceId,
                'srcDeviceGuid': '',
                'clientVersion': '9.77.0',
                'ck': login_ck or '',
                'appToken': wx_app_token,
            },
            ensure_ascii=False,
        )
        account = mobile
        mobile = mobile[:3] + '*' * 4 + mobile[7:]

        return token_data, str(account), mobile
    except Exception as e:
        sender.reply(f'❌ 获取Token失败，请仔细查看注意事项！')
        exit(0)

def bindaccount():
    welcome_msg = """
=====顺丰速运登录=====
[1] 验证码登录
[2] 微信扫码登录
------------------
回复数字选择方式
回复"q"退出操作
=================="""

    sender.reply(welcome_msg)
    input_choice = get_user_choice('请选择登录方式')

    if input_choice == '1':
        Token, account, mobile = sf_captcha_login(sender)
    elif input_choice == '2':
        Token, account, mobile = sf_login(sender)
    else:
        sender.reply('❌ 输入错误,请重新选择登录方式')
        return

    def accvip(account, Token, mobile):
        accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
        auth_status = '✅ 已授权' if accountVip and accountVip >= today_time else '⚠️ 未授权'
        next_step = f'发送 {dd_managecommand} 可管理账号' if accountVip and accountVip >= today_time else f'发送 {dd_managecommand} 可进行授权'
        
        success_msg = f"""
=====顺丰账号绑定=====
📱 绑定账号: {mobile}
🔐 授权状态: {auth_status}
⏰ 下一步操作: 
   {next_step}
=================="""

        accounts = parse_accounts(uservalue)
        if account not in accounts:
            accounts.append(account)
        accounts = list(dict.fromkeys(accounts))
        if accounts:
            middleware.bucketSet(bucket='dd_sf_user', key=userid, value=str(accounts))
        middleware.bucketSet(bucket='dd_sf_token', key=account, value=Token)

        if accountVip and accountVip >= today_time:
            try:
                try:
                    td = json.loads(Token)
                    ql_value = td.get('ck', '')
                    if not ql_value and td.get('sign'):
                        token_url = build_token_url(td['sign'])
                        ql_value = get_ck_from_url(token_url) or Token
                    elif not ql_value:
                        ql_value = Token
                except (json.JSONDecodeError, TypeError):
                    ql_value = get_ck_from_url(Token) if Token.startswith('http') else Token
                qlid = allenvs(osname=dd_sf_osname, account=account)
                if qlid:
                    if use_daidai:
                        DDupdate(osname=dd_sf_osname, value=ql_value, account=account, env_id=qlid, phone=mobile, expire_time=accountVip)
                    else:
                        QLupdate(osname=dd_sf_osname, value=ql_value, account=account, qlid=qlid, phone=mobile, expire_time=accountVip)
                else:
                    Addenvs(osname=dd_sf_osname, value=ql_value, account=account, phone=mobile, expire_time=accountVip)
            except Exception as e:
                sender.reply(f"""
=====更新失败=====
❌ 更新变量失败
⚠️ 错误: {str(e)}
==================""")
            
        sender.reply(success_msg)

    accvip(account, Token, mobile)

def empower(empowertime, me_as_int):
    day = me_as_int * 30
    if len(empowertime) == 0 or empowertime <= str(today_time):
        delayed_date = today_date + timedelta(days=day)
    elif empowertime > today_time:
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        delayed_date = delayed_date.date()
    else:
        sender.reply('出错！')
        exit(0)
    return str(delayed_date)

def sf_auth():
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)
        
    auth_menu = """
=====顺丰授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 更新变量
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
    elif xz == '1':
        users = middleware.bucketAllKeys('dd_sf_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的顺丰账号")
            return
            
        sender.reply("""
=====请输入授权天数=====
------------------
回复数字设置天数
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
            sjts = int(sjts)
        except:
            sender.reply("❌ 天数必须是数字!")
            return
            
        success_count = 0
        fail_count = 0
        sync_fail_count = 0
        
        for user in users:
            accountlist = middleware.bucketGet('dd_sf_user', user)
            if not accountlist or accountlist == '{}':
                continue

            accounts = parse_accounts(accountlist)
            if not accounts:
                continue
            for account in accounts:
                try:
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    accountVip = middleware.bucketGet('dd_sf_auth', account)
                    if has_valid_auth(accountVip, dqsj):
                        sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                        new_sqsj = sqsj + timedelta(days=int(sjts))  # 确保使用整数
                    else:
                        new_sqsj = datetime.now() + timedelta(days=int(sjts))  # 确保使用整数
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    
                    middleware.bucketSet('dd_sf_auth', account, new_sqsj)
                    success_count += 1
                    token = get_token_as_ck(account)
                    if token:
                        try:
                            phone = account[:3] + '*' * 4 + account[7:]
                            Addenvs(osname=dd_sf_osname, value=token, account=account, phone=phone, target_userid=user, expire_time=new_sqsj)
                        except Exception:
                            sync_fail_count += 1
                    else:
                        sync_fail_count += 1
                except Exception:
                    fail_count += 1

        result_msg = f"""
=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⚠️ 面板未同步: {sync_fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
        sender.reply(result_msg)
        notify = middleware.bucketGet('bd_tptconfig', 'notify')
        if notify:
            tsqd = notify.split(',')
            middleware.notifyMasters(result_msg, tsqd)
            
    elif xz == '2':
        user_guide = """
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
            
        accountlist = middleware.bucketGet('dd_sf_user', myuid)
        if not accountlist or accountlist == '' or accountlist == '{}':
            sender.reply(f"""
=====查询结果=====
❌ 未找到 {myuid} 的账号信息
==================""")
            return
            
        try:
            accounts = parse_accounts(accountlist)
            if not accounts:
                sender.reply(f"""
=====数据错误=====
❌ 账号数据格式异常
==================""")
                return
            
            account_list = """
=======账号列表=====
[0] 授权所有账号
------------------"""
            
            for i, account in enumerate(accounts, 1):
                accountVip = middleware.bucketGet('dd_sf_auth', account)
                vip_status = accountVip if accountVip else '未授权'
                account_list += f"\n[{i}] 账号: {account}\n    授权至: {vip_status}\n------------------"
                
            account_list += "\n回复数字选择账号\n回复'q'退出\n=================="
            sender.reply(account_list)
            
            xz = sender.listen(60000)
            if xz == 'q' or xz == 'Q':
                sender.reply("✅ 已退出授权")
                return
            elif xz is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                xz = int(xz)
                if xz < 0 or (xz > len(accounts) and xz != 0):
                    sender.reply(f"""
=====输入错误=====
❌ 请输入 0-{len(accounts)} 之间的数字
==================""")
                    return
            except ValueError:
                sender.reply("""
=====输入错误=====
❌ 请输入正确的数字
==================""")
                return
                
            auth_guide = """
=====设置授权天数=====
请输入要授权的天数
------------------
回复数字设置天数
回复"q"退出操作
=================="""
            sender.reply(auth_guide)
            
            sjts = sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                sjts = int(sjts)
                if sjts <= 0:
                    sender.reply("❌ 授权天数必须大于0!")
                    return
                    
                success_count = 0
                fail_count = 0
                sync_fail_count = 0
                
                if xz == 0:
                    target_accounts = accounts
                else:
                    target_accounts = [accounts[xz-1]]
                    
                for account in target_accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('dd_sf_auth', account)
                        if has_valid_auth(accountVip, dqsj):
                            sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                            new_sqsj = sqsj + timedelta(days=sjts)
                        else:
                            new_sqsj = datetime.now() + timedelta(days=sjts)
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        middleware.bucketSet('dd_sf_auth', account, new_sqsj)
                        success_count += 1
                        token = get_token_as_ck(account)
                        if token:
                            try:
                                phone = account[:3] + '*' * 4 + account[7:]
                                Addenvs(osname=dd_sf_osname, value=token, account=account, phone=phone, target_userid=myuid, expire_time=new_sqsj)
                            except Exception as e:
                                sync_fail_count += 1
                                print(f"同步账号 {account} 变量失败: {str(e)}")
                        else:
                            sync_fail_count += 1
                    except Exception as e:
                        fail_count += 1
                        print(f"授权账号 {account} 失败: {str(e)}")
                        
                result_msg = f"""
=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⚠️ 面板未同步: {sync_fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return
                
        except Exception as e:
            sender.reply(format_message("系统错误", f"处理账号数据时出错\n错误: {str(e)}", "error"))
            return
    elif xz == '3':
        sync_to_panel()
    else:
        sender.reply("❌ 输入的选项无效!")
        return

def meituanmanage():
    if not uservalue:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {dd_signcommand} 绑定", "error"))
        return
        
    try:
        accounts = parse_accounts(uservalue)
        if not accounts:
            sender.reply(format_message("账号错误", "账号数据格式异常", "error"))
            return
        middleware.bucketSet(bucket='dd_sf_user', key=userid, value=str(accounts))
        account_list = "=====我的顺丰账号=====\n[0] 🎯 批量授权所有账号\n"
        for i, account in enumerate(accounts, 1):
            accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
            auth_status, auth_time = get_auth_status(accountVip, today_time)
            login_mobile = mask_phone(account)
            
            account_list += f"""
[{i}] 账号信息
📱 账号: {login_mobile}
🔐 授权: {auth_status}"""
            if i < len(accounts):
                account_list += "\n------------------"
                
        account_list += "\n==================\n回复数字选择账号\n回复'q'退出操作"
        
        sender.reply(account_list)
        
        inputmessage = get_user_choice("", 120000, True)
        try:
            me_as_int = int(inputmessage)
            if me_as_int < 0 or me_as_int > len(accounts):
                sender.reply(format_message("输入无效", "输入的序号无效", "error"))
                exit(0)
        except ValueError:
            sender.reply(format_message("输入错误", "输入必须是数字", "error"))
            exit(0)
            
        if me_as_int == 0:
            batch_auth_guide = """
=====批量授权设置=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
            sender.reply(batch_auth_guide)
            
            mes = get_user_choice("", 120000, True)
            mes = ValueErrors(value=mes, count=999)
            total_money = Decimal(mes) * Decimal(sfVipmoney) * len(accounts)
            
            confirm_msg = f"""
=====批量授权确认=====
📊 账号数量: {len(accounts)}个
⏰ 授权时长: {mes}月/每个账号
💰 总计金额: {total_money}元
------------------
确认批量授权？
[y] 确认授权
[n] 取消操作
=================="""
            sender.reply(confirm_msg)
            
            if yesornos():
                batch_zf(project='顺丰批量授权', accounts=accounts, months=mes, total_money=total_money)
            else:
                sender.reply(format_message("已取消", "已取消批量授权", "info"))
                exit(0)
        else:
            account = accounts[me_as_int - 1]
            accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
            login_mobile = mask_phone(account)
            
            auth_status, auth_time = get_auth_status(accountVip, today_time)
            
            account_info = f"""
=====账号详情=====
📱 账号: {login_mobile}
🔐 授权: {auth_status}
==================
[1] 授权账号
[2] 删除账号
------------------
回复数字选择功能
回复"q"退出操作
=================="""
            sender.reply(account_info)
            
            inputmessage = get_user_choice("", 120000, True)
            
            if inputmessage == '2':
                confirm_msg = """
=====警告=====
确定要删除该账号吗？
此操作不可恢复！
------------------
[y] 确认删除
[n] 取消操作
=================="""
                sender.reply(confirm_msg)
                
                if yesornos():
                    accounts.remove(str(account))
                    qlid = allenvs(osname=dd_sf_osname, account=str(account))
                    delenvs(id=qlid)
                    if len(accounts) == 0:
                        middleware.bucketDel(bucket='dd_sf_user', key=userid)
                    else:
                        middleware.bucketSet(bucket='dd_sf_user', key=userid, value=str(accounts))
                    sender.reply(format_message("删除成功", "账号删除成功!", "success"))
                else:
                    sender.reply(format_message("已取消", "已取消删除", "info"))
                    exit(0)
            elif inputmessage == '1':
                auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
                sender.reply(auth_guide)
                
                mes = get_user_choice("", 120000, True)
                mes = ValueErrors(value=mes, count=999)
                money = Decimal(mes) * Decimal(sfVipmoney)
                account_ck = get_ck_with_fallback(account)
                if not account_ck:
                    userurl, _ = get_token_url_auto_refresh(account)
                    account_ck = get_ck_from_url(userurl) if userurl else None
                zf(project='顺丰授权', me_as_int=mes, accountVip=accountVip, token=account_ck or '',
                   phone=account, account=account)
                accountVip = empower(empowertime=accountVip, me_as_int=mes)
                middleware.bucketSet(bucket='dd_sf_auth', key=account, value=accountVip)
                if account_ck:
                    try:
                        Addenvs(osname=dd_sf_osname, value=account_ck, account=account, phone=login_mobile, expire_time=accountVip)
                    except Exception as e:
                        print(f"同步账号 {account} 变量失败: {str(e)}")
                
                result_msg = f"""
=====订单完成=====
🎈 名称: 顺丰授权
🎉 数量: {mes} 个月
💰 金额: {money} 元
==================""" 
                sender.reply(result_msg)
                
    except Exception as e:
        sender.reply(format_message("账号处理错误", f"账号列表处理失败\n错误: {str(e)}", "error"))
        return

def yesornos():
    choice = get_user_choice("", 120000, True)
    if choice in ['Y', 'y', '是']:
        return True
    elif choice in ['n', 'N', '否']:
        return False
    else:
        sender.reply(format_message("输入错误", "请输入正确的选项", "error"))
        exit(0)

def get_payment_config():
    zsm = middleware.bucketGet('dd_sf', 'zsm')
    use_ma_pay = middleware.bucketGet('dd_sf', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    if use_ma_pay:
        ma_pay_config = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type'),
            'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
            'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
        }
        
        if ma_pay_config['switch'].lower() != 'true' or not all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
            use_ma_pay = False
    else:
        ma_pay_config = None
    
    return zsm, use_ma_pay, ma_pay_config

def parse_payment_result(ddzf):
    try:
        if isinstance(ddzf, dict):
            if ddzf.get('Type') == '微信赞赏':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            elif ddzf.get('Type') == '微信收款':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            elif ddzf.get('Money'):
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
            elif ddzf.get('money'):
                return float(ddzf.get('money', 0)), ddzf.get('time', '').replace('T', ' ').split('.')[0], ddzf.get('fromName', '')
            else:
                sender.reply(format_message("支付错误", "不支持的支付消息格式", "error"))
                exit(0)
        else:
            try:
                ddzf = json.loads(ddzf)
                if ddzf.get('Type') == '微信赞赏':
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
                elif ddzf.get('Type') == '微信收款':
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
                else:
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
            except:
                sender.reply(format_message("解析错误", "无法解析支付结果", "error"))
                exit(0)
    except Exception as e:
        sender.reply(format_message("处理错误", f"处理支付结果时出错: {str(e)}", "error"))
        exit(0)

def zf(project, me_as_int, accountVip, token, phone, account):
    try:
        money = Decimal(me_as_int) * Decimal(sfVipmoney)
        if money == 0:
            accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
            middleware.bucketSet('dd_sf_auth', account, accountVip)
            Addenvs(osname=dd_sf_osname, value=token, account=account, phone=phone, expire_time=accountVip)
            
            sender.reply(format_message("免费授权成功", 
                f"商品: {project}\n金额: 免费\n授权时长: {me_as_int}月", "success"))
            return True
        
        zsm, use_ma_pay, ma_pay_config = get_payment_config()
        if not zsm and not use_ma_pay:
            sender.reply(format_message("配置错误", "未配置收款方式,请联系管理员!", "error"))
            exit(0)
            
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(sfcoin) * me_as_int if sfcoin else 0
        pay_menu = "=====选择支付方式====="
        option_num = 1
        options_map = {}

        if zsm and not use_ma_pay:
            pay_menu += f"\n{option_num}️⃣ 微信支付\n   💰 {money}元/{me_as_int}月"
            options_map[str(option_num)] = 'wechat'
            option_num += 1

        if use_ma_pay:
            pay_menu += f"\n{option_num}️⃣ 码支付\n   💰 {money}元/{me_as_int}月"
            options_map[str(option_num)] = 'ma'
            option_num += 1
            
        if sfcoin and sfcoin != '' and int(sfcoin) > 0:
            pay_menu += f"\n{option_num}️⃣ 积分支付\n   🎯 {zfcoin}积分/{me_as_int}月\n   💫 当前积分: {usercoin}"
            options_map[str(option_num)] = 'points'
            
        pay_menu += "\n------------------\n回复数字选择方式\n回复'q'退出操作\n=================="

        sender.reply(pay_menu)
        choice = get_user_choice("", 60000, True)
            
        selected_pay = options_map.get(choice)
        if selected_pay == 'wechat' and zsm:
            zfzt = sender.atWaitPay()
            if zfzt:
                sender.reply(format_message("支付繁忙", "当前有人正在支付,请稍后再试！", "warning"))
                exit(0)
                
            pay_msg = f"""
=====微信扫码支付====
🎫 商品: {project}
📅 时长: {me_as_int}月
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
            sender.reply(pay_msg)
            sender.replyImage(zsm)
            
            ddzf = sender.waitPay("q", 100 * 1000)
            
            if str(ddzf) == 'q':
                sender.reply(format_message("已取消", "已取消支付", "info"))
                exit(0)
                
            try:
                Money, Time, From = parse_payment_result(ddzf)
                    
                if float(Money) >= float(money):
                    accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                    middleware.bucketSet('dd_sf_auth', account, accountVip)
                    Addenvs(osname=dd_sf_osname, value=token, account=account, phone=phone, expire_time=accountVip)
                    
                    result_msg = f"""
=====支付成功=====
🎫 商品: {project}
💰 金额: {Money}元
⏰ 时间: {Time}
{f'👤 付款人: {From}' if From else ''}
=================="""
                    sender.reply(result_msg)
                    return True
                else:
                    sender.reply(format_message("支付金额错误", 
                        f"应付: {money}元\n实付: {Money}元\n{f'付款人: {From}' if From else ''}\n\n❗ 请联系管理员处理退款！", "error"))
                    exit(0)
            except Exception as e:
                sender.reply(format_message("处理错误", f"处理支付结果时出错: {str(e)}", "error"))
                exit(0)
                
        elif selected_pay == 'ma' and use_ma_pay:
            out_trade_no = f"SF{int(time.time())}{userid}"
            params = {
                'pid': ma_pay_config['pid'],
                'type': ma_pay_config['type'].split(',')[0],
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-顺丰授权-{str(money)}",
                'money': str(money),
                'notify_url': ma_pay_config['notify_url'],
                'return_url': ma_pay_config['return_url'],
                'param': userid
            }
            params = {k: v for k, v in params.items() if v}
            sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
            sign = hashlib.md5((sign_str + ma_pay_config['key']).encode('utf-8')).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            gateway = ma_pay_config['gateway']
            if gateway.endswith('/'):
                gateway = gateway[:-1]
            mapi_url = f"{gateway}/mapi.php"
            
            try:
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    sender.reply(format_message("支付失败", f"创建支付订单失败，HTTP状态码: {response.status_code}", "error"))
                    exit(0)
                
                try:
                    result = response.json()
                except:
                    sender.reply(format_message("支付失败", "创建支付订单失败，返回数据格式错误", "error"))
                    exit(0)
                
                code = result.get('code', 0)
                msg = result.get('msg', '未知状态')

                if code == 1:
                    payurl = result.get('payurl', '')
                    if not payurl:
                        sender.reply(format_message("支付失败", "未获取到支付链接", "error"))
                        exit(0)
                    
                    qrcode_url = generate_qrcode(payurl)
                    pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
                    if qrcode_url:
                        send_qrcode_image(sender, qrcode_url, pay_type)
                    else:
                        sender.reply(f"""=====码支付=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 有效期: 5分钟
------------------
二维码生成失败，请点击链接完成支付:
{payurl}
==================""")
                else:
                    if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                        sender.reply(format_message("支付失败", f"码支付暂不可用({msg})", "error"))
                    else:
                        sender.reply(format_message("支付失败", f"创建订单失败: {msg}", "error"))
                    exit(0)
                
                for i in range(60):
                    check_url = gateway
                    if check_url.endswith('/'):
                        check_url = check_url[:-1]
                    
                    if '/xpay/epay/api.php' not in check_url:
                        check_url = f"{check_url}/xpay/epay/api.php"
                    
                    check_params = {
                        'act': 'order',
                        'pid': ma_pay_config['pid'],
                        'key': ma_pay_config['key'],
                        'out_trade_no': out_trade_no
                    }
                    
                    try:
                        check_resp = requests.get(check_url, params=check_params, timeout=10)
                        check_result = check_resp.json()
                        
                        if check_result.get('code') == 1 and check_result.get('status') == 1:
                            accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                            middleware.bucketSet('dd_sf_auth', account, accountVip)
                            Addenvs(osname=dd_sf_osname, value=token, account=account, phone=phone, expire_time=accountVip)
                            
                            sender.reply(f"""=====支付成功=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 授权时长: {me_as_int}月
==================""")
                            return True
                    except Exception as e:
                        print(f"查询订单状态出错: {str(e)}")
                    
                    result = sender.listen(5000)
                    if result == 'q' or result == 'Q':
                        sender.reply("✅ 已取消支付")
                        exit(0)
                
                sender.reply("❌ 支付超时,请重新发起支付!")
                exit(0)
            except Exception as e:
                sender.reply(f"❌ 支付请求失败: {str(e)}")
                exit(0)
                
        elif selected_pay == 'points' and sfcoin != '' and sfcoin is not None and int(sfcoin) > 0:
            if int(usercoin) < zfcoin:
                sender.reply(format_message("积分不足", f"当前积分: {usercoin}\n需要积分: {zfcoin}", "error"))
                exit(0)
                
            confirm_msg = f"💫 积分支付确认\n💰 消耗积分: {zfcoin}\n⏰ 授权时长: {me_as_int}月\n------------------\n确认请回复【y】\n取消请回复【n】"
            sender.reply(confirm_msg)
            
            if yesornos():
                try:
                    new_balance = int(usercoin) - zfcoin
                    middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                    accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                    middleware.bucketSet('dd_sf_auth', account, accountVip)
                    Addenvs(osname=dd_sf_osname, value=token, account=account, phone=phone, expire_time=accountVip)
                    
                    result_msg = f"✅ 支付成功\n💫 扣除积分: {zfcoin}\n💰 剩余积分: {new_balance}\n⏰ 授权时长: {me_as_int}月"
                    sender.reply(result_msg)
                    exit(0)
                except Exception as e:
                    sender.reply(format_message("支付失败", f"积分处理失败\n错误信息: {str(e)}", "error"))
                    exit(0)
            else:
                sender.reply(format_message("已取消支付", "操作已取消", "info"))
                exit(0)
        else:
            sender.reply(format_message("输入无效", "请输入正确的选项", "error"))
            exit(0)
            
    except Exception as e:
        sender.reply(format_message("系统错误", f"支付处理异常\n错误信息: {str(e)}", "error"))
        exit(0)

def _batch_authorize(accounts, months):
    success = 0
    for account in accounts:
        try:
            av = middleware.bucketGet('dd_sf_auth', account)
            token = get_token_as_ck(account)
            av = empower(empowertime=av, me_as_int=months)
            middleware.bucketSet('dd_sf_auth', account, av)
            Addenvs(osname=dd_sf_osname, value=token, account=account, phone=mask_phone(account), expire_time=av)
            success += 1
        except:
            continue
    return success

def batch_zf(project, accounts, months, total_money):
    try:
        if total_money == 0:
            sc = _batch_authorize(accounts, months)
            sender.reply(f"=====批量授权成功=====\n🎫 商品: {project}\n💰 金额: 免费\n📊 成功: {sc}/{len(accounts)}个账号\n⏰ 授权时长: {months}月/每个账号\n==================")
            return True

        zsm, use_ma_pay_local, ma_pay_config = get_payment_config()
        if not zsm and not use_ma_pay_local:
            sender.reply('未配置收款方式,请联系管理员!')
            exit(0)

        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(sfcoin) * months * len(accounts) if sfcoin else 0

        pay_menu = f"=====选择支付方式====\n💰 总金额: {total_money}元\n📊 账号: {len(accounts)}个\n⏰ 时长: {months}月/每个"
        option_num = 1
        options_map = {}
        if zsm and not use_ma_pay_local:
            pay_menu += f"\n------------------\n{option_num}️⃣ 微信支付 💰 {total_money}元"
            options_map[str(option_num)] = 'wechat'
            option_num += 1
        if use_ma_pay_local:
            pay_menu += f"\n{option_num}️⃣ 码支付 💰 {total_money}元"
            options_map[str(option_num)] = 'ma'
            option_num += 1
        if sfcoin and sfcoin != '' and int(sfcoin) > 0:
            pay_menu += f"\n{option_num}️⃣ 积分支付 🎯 {zfcoin}积分 💫 当前: {usercoin}"
            options_map[str(option_num)] = 'points'
        pay_menu += "\n------------------\n回复数字选择方式\n回复\"q\"退出操作\n=================="

        sender.reply(pay_menu)
        choice = sender.input(60000, 1, False)
        if choice in ('q', 'Q'):
            sender.reply("✅ 已取消支付")
            exit(0)

        selected_pay = options_map.get(choice)
        if selected_pay == 'wechat' and zsm:
            zfzt = sender.atWaitPay()
            if zfzt:
                sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
                exit(0)
            sender.reply(f"=====微信扫码支付====\n🎫 商品: {project}\n📊 账号: {len(accounts)}个\n⏰ 时长: {months}月/每个\n💰 总金额: {total_money}元\n------------------\n请使用微信扫码支付\n回复\"q\"取消支付\n==================")
            sender.replyImage(zsm)
            ddzf = sender.waitPay("q", 100 * 1000)
            if str(ddzf) == 'q':
                sender.reply('✅ 已取消支付')
                exit(0)
            try:
                Money, Time, From = parse_payment_result(ddzf)
                if float(Money) >= float(total_money):
                    sc = _batch_authorize(accounts, months)
                    sender.reply(f"=====支付成功=====\n🎫 商品: {project}\n💰 金额: {Money}元\n📊 成功: {sc}/{len(accounts)}个账号\n⏰ 时间: {Time}\n{f'👤 付款人: {From}' if From else ''}\n==================")
                    return True
                else:
                    sender.reply(f"=====支付金额错误=====\n💰 应付: {total_money}元\n💳 实付: {Money}元\n{f'👤 付款人: {From}' if From else ''}\n❗ 请联系管理员处理退款！\n==================")
                    exit(0)
            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                exit(0)

        elif selected_pay == 'ma' and use_ma_pay_local:
            out_trade_no = f"SFBATCH{int(time.time())}{userid}"
            params = {
                'pid': ma_pay_config['pid'], 'type': ma_pay_config['type'].split(',')[0],
                'out_trade_no': out_trade_no, 'name': f"{senderID}-顺丰批量授权-{str(total_money)}",
                'money': str(total_money), 'notify_url': ma_pay_config['notify_url'],
                'return_url': ma_pay_config['return_url'], 'param': userid
            }
            params = {k: v for k, v in params.items() if v}
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            gateway = ma_pay_config['gateway'].rstrip('/')
            mapi_url = f"{gateway}/mapi.php"
            try:
                response = requests.post(mapi_url, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10)
                if response.status_code != 200:
                    sender.reply(format_message("支付失败", f"创建订单失败，HTTP {response.status_code}", "error"))
                    exit(0)
                try:
                    result = response.json()
                except:
                    sender.reply(format_message("支付失败", "返回数据格式错误", "error"))
                    exit(0)
                code = result.get('code', 0)
                msg = result.get('msg', '未知状态')
                if code == 1:
                    payurl = result.get('payurl', '')
                    if not payurl:
                        sender.reply(format_message("支付失败", "未获取到支付链接", "error"))
                        exit(0)
                    qrcode_url = generate_qrcode(payurl)
                    pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
                    if qrcode_url:
                        send_qrcode_image(sender, qrcode_url, pay_type)
                    else:
                        sender.reply(f"=====码支付=====\n💰 金额: {total_money}元\n⏰ 有效期: 5分钟\n------------------\n{payurl}\n==================")
                else:
                    sender.reply(format_message("支付失败", f"创建订单失败: {msg}", "error"))
                    exit(0)
                check_url = gateway.rstrip('/')
                if '/xpay/epay/api.php' not in check_url:
                    check_url = f"{check_url}/xpay/epay/api.php"
                for i in range(60):
                    try:
                        check_resp = requests.get(check_url, params={'act': 'order', 'pid': ma_pay_config['pid'], 'key': ma_pay_config['key'], 'out_trade_no': out_trade_no}, timeout=10)
                        check_result = check_resp.json()
                        if check_result.get('code') == 1 and check_result.get('status') == 1:
                            sc = _batch_authorize(accounts, months)
                            sender.reply(f"=====支付成功=====\n🎫 商品: {project}\n💰 金额: {total_money}元\n📊 成功: {sc}/{len(accounts)}个账号\n⏰ 授权时长: {months}月/每个账号\n==================")
                            return True
                    except:
                        pass
                    result = sender.listen(5000)
                    if result in ('q', 'Q'):
                        sender.reply("✅ 已取消支付")
                        exit(0)
                sender.reply("❌ 支付超时,请重新发起支付!")
                exit(0)
            except Exception as e:
                sender.reply(f"❌ 支付请求失败: {str(e)}")
                exit(0)

        elif selected_pay == 'points' and sfcoin and int(sfcoin) > 0:
            if int(usercoin) < zfcoin:
                sender.reply(format_message("积分不足", f"当前积分: {usercoin}\n需要积分: {zfcoin}", "error"))
                exit(0)
            sender.reply(f"💫 积分支付确认\n消耗积分: {zfcoin}\n📊 账号: {len(accounts)}个\n⏰ 时长: {months}月/每个\n\n确认请回复【y】\n取消请回复【n】")
            if yesornos():
                try:
                    new_balance = int(usercoin) - zfcoin
                    middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                    sc = _batch_authorize(accounts, months)
                    sender.reply(f"✅ 支付成功\n💫 扣除积分: {zfcoin}\n💰 剩余积分: {new_balance}\n📊 成功: {sc}/{len(accounts)}个账号\n⏰ 授权时长: {months}月/每个账号")
                    exit(0)
                except Exception as e:
                    sender.reply(format_message("支付失败", f"积分处理失败\n错误信息: {str(e)}", "error"))
                    exit(0)
            else:
                sender.reply(format_message("已取消支付", "操作已取消", "info"))
                exit(0)
        else:
            sender.reply(format_message("输入无效", "请输入正确的选项", "error"))
            exit(0)
    except Exception as e:
        sender.reply(format_message("系统错误", f"支付处理异常\n错误信息: {str(e)}", "error"))
        exit(0)

def cx_by_session(session_id):
    coin, allcoin, user_info = todaycoin(session_id)
    large_coupons = query_large_coupons(session_id, show_other_coupons)
    return coin, allcoin, large_coupons, user_info

def get_session_from_ck(ck):
    if not ck:
        return None
    match = re.search(r'sessionId=([^;]+)', ck)
    if match:
        return match.group(1)
    return None

def _sf_express_headers_to_lower(headers):
    """详情接口抓包为全小写关键 header，这里只转换顺丰自定义字段。"""
    key_map = {
        "srcDeviceGuid": "srcdeviceguid",
        "clientVersion": "clientversion",
        "languageCode": "languagecode",
        "systemVersion": "systemversion",
        "deviceId": "deviceid",
        "regionCode": "regioncode",
        "screenSize": "screensize",
        "sytToken": "syttoken",
        "timeInterval": "timeinterval",
        "mediaCode": "mediacode",
        "memberId": "memberid",
    }
    return {key_map.get(k, k): v for k, v in headers.items()}


def _sf_express_post(url, body_obj, app_token, member_id, extra_headers=None, device_id="", ck="", lowercase_headers=False):
    """顺丰快递查询专用的POST请求，必须复用登录时保存的 deviceId。"""
    if not device_id:
        return {"success": False, "errorMessage": "快递查询缺少登录设备信息，请重新登录后再试"}

    cfg = {
        "clientVersion": "9.77.0",
        "languageCode": "sc",
        "systemVersion": "13",
        "deviceId": device_id,
        "regionCode": "CN",
        "carrier": "unknown",
        "screenSize": "1080x2400",
        "model": "MEIZU 20",
        "mediaCode": "AndroidML",
        "jsbundle": "705088894ad6ef475bdf4875c9d533b8",
        "srcDeviceGuid": "".join(random.choices(string.ascii_letters + string.digits + "_", k=38)),
    }
    body_str = json.dumps(body_obj, separators=(",", ":"), ensure_ascii=False)
    ts = str(int(time.time() * 1000))
    body_md5 = generate_md5(body_str + "&080R3MAC57J2{A19!$3:WO{I<1N$31BI")
    mix = cfg["deviceId"] + ts + cfg["clientVersion"] + "2NBF+BE4{@P:@X${Q9BAE>{PAK!D:N*^" + "CN" + cfg["languageCode"] + body_md5 + cfg["jsbundle"]
    computed_syt = generate_md5(generate_md5(mix + "&2NBF+BE4{@P:@X${Q9BAE>{PAK!D:N*^") + "&0HQ%H91K&AA{DH$*XV>XR)VKL:QFE{&%")
    headers = {
        "User-Agent": "okhttp/4.9.1",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json",
        "jsbundle": cfg["jsbundle"],
        "srcDeviceGuid": cfg["srcDeviceGuid"],
        "clientVersion": cfg["clientVersion"],
        "languageCode": cfg["languageCode"],
        "systemVersion": cfg["systemVersion"],
        "deviceId": cfg["deviceId"],
        "regionCode": cfg["regionCode"],
        "carrier": cfg["carrier"],
        "screenSize": cfg["screenSize"],
        "sytToken": computed_syt,
        "timeInterval": ts,
        "model": cfg["model"],
        "mediaCode": cfg["mediaCode"],
        "token": app_token,
        "memberId": member_id,
    }
    if ck:
        headers["Cookie"] = ck
    if extra_headers:
        headers.update(extra_headers)
    if lowercase_headers:
        headers = _sf_express_headers_to_lower(headers)
    return requests.post(url, headers=headers, data=body_str.encode("utf-8"), timeout=15).json()


def sf_query_express_list(app_token, member_id, mobile, data_type=0, page_no=1, device_id="", ck=""):
    """查询快递列表 data_type: 0=寄件 1=收件"""
    body = {
        "pageRows": 10,
        "orderType": "1",
        "payTypeList": [],
        "accountMobile": mobile,
        "pageNo": page_no,
        "dataType": data_type,
        "orderStatusList": [],
        "mobile": mobile,
        "memberId": member_id,
        "timeRange": "",
        "queryLastRouter": True,
        "supportWaybillStatusNew": True,
        "userInfos": [],
        "selectedFamily": False,
    }
    url = "https://ccsp-egmas.sf-express.com/cx-app-query/query/app/waybill/queryMultAccountBillListComplex"
    return _sf_express_post(url, body, app_token, member_id, device_id=device_id, ck=ck)


def sf_query_express_detail(app_token, member_id, waybill_no, device_id="", ck=""):
    """查询快递详情"""
    body = {"waybillNo": waybill_no, "mediaCode": "AndroidML"}
    url = "https://ucmp.sf-express.com/cx-wechat-query/query/newWaybill/search"
    extra = {"cxgw-appid": "sfapp-valid-a85073uy"}
    return _sf_express_post(url, body, app_token, member_id, extra, device_id=device_id, ck=ck, lowercase_headers=True)


def get_app_auth_info(account):
    """获取账号的appToken和memberId"""
    td = parse_token_data(account)
    if not td:
        return None, None, None
    app_token = td.get("appToken", "")
    member_id = td.get("userId", "")
    mobile = td.get("mobile", account)
    return app_token, member_id, mobile


def get_app_query_context(account):
    """获取快递查询所需登录上下文。查询接口必须复用登录时保存的 deviceId。"""
    td = parse_token_data(account)
    if not td:
        return None, None, None, None, None
    app_token = td.get("appToken", "")
    member_id = td.get("userId", "")
    mobile = td.get("mobile", account)
    device_id = td.get("deviceId", "")
    ck = td.get("ck", "")
    return app_token, member_id, mobile, device_id, ck


def format_express_detail(detail_obj):
    """格式化快递详情信息。聊天场景默认输出摘要，避免物流轨迹刷屏。"""
    if not detail_obj:
        return "❌ 无法获取快递详情"

    def short_text(text, limit=46):
        text = str(text or "").strip()
        if len(text) <= limit:
            return text
        return text[:limit] + "..."

    waybill_no = detail_obj.get("waybillNo", "")
    sender_name = detail_obj.get("consignorContName", "")
    sender_mobile = detail_obj.get("consignorMobile", "")
    sender_addr = detail_obj.get("consignorAddr", "")
    receiver_name = detail_obj.get("addresseeContName", "")
    receiver_mobile = detail_obj.get("addresseeMobile", "")
    receiver_addr = detail_obj.get("addresseeAddr", "")
    product_name = detail_obj.get("productDisplayName", "") or detail_obj.get("limitTypeName", "")
    status_msg = detail_obj.get("waybillStatusMessage", "")
    consigned_tm = detail_obj.get("consignedTm", "")
    signed_tm = detail_obj.get("signinTm", "")
    weight = detail_obj.get("meterageWeightQty", "")
    fee = detail_obj.get("transportFeeAmt", "")
    goods_name = detail_obj.get("consNames", "")

    lines = [
        "=====快递详情=====",
        f"📦 单号: {waybill_no}",
        f"📊 状态: {status_msg}｜{product_name}",
        f"📤 寄件: {sender_name} {sender_mobile}",
        f"📍 {short_text(sender_addr)}",
        f"📥 收件: {receiver_name} {receiver_mobile}",
        f"📍 {short_text(receiver_addr)}",
    ]

    extra_parts = []
    if goods_name:
        extra_parts.append(f"物品: {goods_name}")
    if weight:
        extra_parts.append(f"重量: {weight}kg")
    if fee:
        extra_parts.append(f"运费: ¥{fee}")
    if extra_parts:
        lines.append("｜".join(extra_parts))

    if consigned_tm:
        lines.append(f"🕐 揽收: {consigned_tm}")
    if signed_tm and status_msg == "已签收":
        lines.append(f"🕐 签收: {signed_tm}")

    bar_list = detail_obj.get("barNewList", [])
    if bar_list:
        display_bars = bar_list
        if len(bar_list) > 5:
            display_bars = [bar_list[0]] + bar_list[-4:]

        lines.append("------------------")
        lines.append(f"🚚 关键轨迹({len(display_bars)}/{len(bar_list)}):")
        for bar in display_bars:
            scan_date = bar.get("barScanDt", "")
            scan_time = bar.get("barScanTm", "")
            remark = bar.get("remark", "")
            pkg_msg = bar.get("cxPackageMessage", "")
            if remark:
                time_str = f"{scan_date} {scan_time}"
                lines.append(f"  [{pkg_msg}] {time_str}")
                lines.append(f"  {short_text(remark, 72)}")
        if len(bar_list) > len(display_bars):
            lines.append(f"  已省略 {len(bar_list) - len(display_bars)} 条中间轨迹")

    lines.append("==================")
    return "\n".join(lines)


def sf_express_interactive_query():
    """顺丰快递查询交互流程"""
    if not uservalue:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {dd_signcommand} 绑定", "error"))
        return

    accounts = parse_accounts(uservalue)
    if not accounts:
        sender.reply(format_message("账号错误", "账号数据格式异常", "error"))
        return

    selected_account = None
    if len(accounts) == 1:
        selected_account = accounts[0]
    else:
        msg_lines = ["=====选择查询账号====="]
        for i, acc in enumerate(accounts):
            msg_lines.append(f"[{i + 1}] {mask_phone(acc)}")
        msg_lines.append("------------------")
        msg_lines.append('回复序号选择，回复"q"退出')
        msg_lines.append("=" * 22)
        sender.reply("\n".join(msg_lines))
        choice = get_user_choice("选择账号")
        if choice is None or choice == "q":
            exit(0)
        idx = validate_input(choice, len(accounts), "序号")
        selected_account = accounts[idx - 1]

    accountVip = middleware.bucketGet(bucket="dd_sf_auth", key=selected_account)
    if not has_valid_auth(accountVip, today_time):
        sender.reply(format_message("授权过期", f'账号授权已过期，请发送"{dd_managecommand}"续费', "error"))
        return

    app_token, member_id, mobile, device_id, ck = get_app_query_context(selected_account)
    if not app_token or not member_id or not device_id:
        sender.reply(format_message("需要重新登录", f"快递查询需要重新登录以获取授权\n💡 请发送 {dd_signcommand} 重新登录", "warning"))
        return

    sender.reply("""=====顺丰快递查询=====
[1] 📤 寄件快递
[2] 📥 收件快递
------------------
回复序号选择，回复"q"退出
======================""")
    type_choice = get_user_choice("选择类型")
    if type_choice is None or type_choice == "q":
        exit(0)
    if type_choice not in ("1", "2"):
        sender.reply("❌ 输入错误，请回复1或2")
        return

    data_type = 0 if type_choice == "1" else 1
    type_name = "寄件" if data_type == 0 else "收件"

    sender.reply(f"⏳ 正在查询{type_name}快递...")
    try:
        result = sf_query_express_list(app_token, member_id, mobile, data_type, device_id=device_id, ck=ck)
    except Exception as e:
        sender.reply(format_message("查询失败", f"网络请求异常: {str(e)}", "error"))
        return

    if not result.get("success"):
        sender.reply(format_message("查询失败", result.get("errorMessage", "未知错误"), "error"))
        return

    obj = result.get("obj", {})
    data_list = obj.get("dataList", [])
    send_total = obj.get("mySendTotal", 0)
    recv_total = obj.get("myReceiveTotal", 0)

    if not data_list:
        sender.reply(format_message("查询结果", f"暂无{type_name}快递记录\n📤 寄件: {send_total}件  📥 收件: {recv_total}件", "info"))
        return

    msg_lines = [
        f"====={type_name}快递列表=====",
        f"📤 寄件: {send_total}件  📥 收件: {recv_total}件",
        "-" * 24,
    ]
    for i, item in enumerate(data_list):
        origin = item.get("originateContacts", "")
        dest = item.get("destinationContacts", "")
        origin_city = item.get("originateCityName", "")
        dest_city = item.get("destinationCityName", "")
        waybill = item.get("waybillno", "")
        status = item.get("waybillStatusMessage", "")
        product = item.get("productDisplayName", "")
        recv_time = item.get("receivedTime", "")[:10] if item.get("receivedTime") else ""
        msg_lines.append(f"[{i + 1}] {origin}→{dest}")
        msg_lines.append(f"    {origin_city}→{dest_city} | {product}")
        msg_lines.append(f"    单号: {waybill}")
        msg_lines.append(f"    状态: {status} | {recv_time}")
        if i < len(data_list) - 1:
            msg_lines.append("")

    msg_lines.append("-" * 24)
    msg_lines.append('回复序号查看详情，回复"q"退出')
    msg_lines.append("=" * 24)
    sender.reply("\n".join(msg_lines))

    detail_choice = get_user_choice("选择快递")
    if detail_choice is None or detail_choice == "q":
        exit(0)
    detail_idx = validate_input(detail_choice, len(data_list), "序号")
    selected_item = data_list[detail_idx - 1]
    waybill_no = selected_item.get("waybillno", "")

    sender.reply(f"⏳ 正在查询 {waybill_no} 的详细信息...")
    try:
        detail_result = sf_query_express_detail(app_token, member_id, waybill_no, device_id=device_id, ck=ck)
    except Exception as e:
        sender.reply(format_message("查询失败", f"网络请求异常: {str(e)}", "error"))
        return

    if not detail_result.get("success"):
        sender.reply(format_message("查询失败", detail_result.get("errorMessage", "未知错误"), "error"))
        return

    detail_obj = detail_result.get("obj", {})
    sender.reply(format_express_detail(detail_obj))


def sf_query_express_count(app_token, member_id, mobile, device_id="", ck=""):
    """查询快递数量统计"""
    try:
        result = sf_query_express_list(app_token, member_id, mobile, data_type=0, page_no=1, device_id=device_id, ck=ck)
        if result.get("success"):
            obj = result.get("obj", {})
            return obj.get("mySendTotal", 0), obj.get("myReceiveTotal", 0)
    except:
        pass
    return None, None


def cxs():
    if not uservalue:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {dd_signcommand} 绑定", "error"))
        return
        
    accounts = parse_accounts(uservalue)
    if not accounts:
        sender.reply(format_message("账号错误", "账号数据格式异常", "error"))
        return
    middleware.bucketSet(bucket='dd_sf_user', key=userid, value=str(accounts))
    
    for account in accounts:
        accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
        login_mobile = mask_phone(account)

        if has_valid_auth(accountVip, today_time):
            auth_time_display = accountVip
        else:
            auth_time_display = "❌ 已过期，请发\"顺丰管理\"续费"

        if has_valid_auth(accountVip, today_time):
            try:
                ck = get_ck_with_fallback(account)
                session_id = get_session_from_ck(ck) if ck else None

                if session_id and validate_ck(ck):
                    coin, allcoin, large_coupons, user_info = cx_by_session(session_id)
                    try:
                        phone = mask_phone(account)
                        Addenvs(osname=dd_sf_osname, value=ck, account=account, phone=phone, expire_time=accountVip)
                    except:
                        pass
                else:
                    userurl, refreshed = get_token_url_auto_refresh(account)
                    if not userurl:
                        sender.reply(format_account_info(
                            login_mobile, "", auth_time_display,
                account_status="❌ 登录态失效",
                            coupons="查询失败"
                        ))
                        continue
                    if refreshed:
                        try:
                            phone = mask_phone(account)
                            new_ck = get_ck_from_url(userurl)
                            if new_ck:
                                Addenvs(osname=dd_sf_osname, value=new_ck, account=account, phone=phone, expire_time=accountVip)
                        except:
                            pass
                    url_session_id, _ = session_ids(userurl)
                    session_id = url_session_id
                    coin, allcoin, large_coupons, user_info = cx_by_session(session_id)

                account_status = "✅ 账号正常"
                today_coin_display = str(coin)

                if user_info and user_info.get('expiring_points', 0) > 0:
                    try:
                        expire_date_str = user_info['point_clear_cycle']
                        expire_date = datetime.strptime(expire_date_str, '%Y-%m-%d')
                        today = datetime.now()
                        days_until_expire = (expire_date - today).days

                        if 0 <= days_until_expire <= 30:
                            today_coin_display += f"\n⚠️ 临期积分: {user_info['expiring_points']} (将于{user_info['point_clear_cycle']}过期)"
                    except:
                        pass

                express_count_str = ""
                try:
                    app_token, m_id, m_mobile, m_device_id, m_ck = get_app_query_context(account)
                    if app_token and m_id and m_device_id:
                        send_cnt, recv_cnt = sf_query_express_count(app_token, m_id, m_mobile, device_id=m_device_id, ck=m_ck)
                        if send_cnt is not None:
                            express_count_str = f"{send_cnt}寄件, {recv_cnt}收件"
                except:
                    pass

                extra_kwargs = {}
                if express_count_str:
                    extra_kwargs["express_count"] = express_count_str

                account_info = format_account_info(
                    login_mobile, "", auth_time_display,
                    coin=allcoin,
                    today_coin=today_coin_display,
                    account_status=account_status,
                    coupons=large_coupons,
                    **extra_kwargs,
                )
                sender.reply(account_info)

            except SystemExit:
                sender.reply(format_account_info(
                    login_mobile, "", auth_time_display,
                    account_status="❌ 账号失效",
                    coupons="查询失败"
                ))
                continue
        else:
            sender.reply(format_account_info(
                login_mobile, "", auth_time_display,
                account_status="⚠️ 授权已过期",
                coupons="需要续费后查询"
            ))

def push(user, account, c):
    login_mobile = mask_phone(account)

    push_msg = f"""
=====顺丰账号通知=====
📱 账号: {login_mobile}
📢 消息: {c}
=================="""

    platforms = ['wb', 'tg', 'qq', 'qb', 'wx']
    for platform in platforms:
        middleware.push(platform, '', user, '', push_msg)

def clean_expired_accounts():
    users = middleware.bucketAllKeys(bucket='dd_sf_user')
    
    if not users:
        sender.reply(format_message("清理结果", "未找到任何绑定账号", "error"))
        return
        
    sender.reply(format_message("开始清理", f"共找到: {len(users)}个用户\n⏳ 清理中请稍候...", "loading"))
    
    cleaned_count = 0
    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_sf_user', key=user)
            if not accountlist:
                continue
                
            accounts = parse_accounts(accountlist)
            valid_accounts = []
            for account in accounts:
                accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
                
                if not accountVip or accountVip <= today_time:
                    try:
                        qlid = allenvs(osname=dd_sf_osname, account=account)
                        if qlid:
                            delenvs(id=qlid)
                    except:
                        pass
                        
                    middleware.bucketDel(bucket='dd_sf_token', key=account)
                    middleware.bucketDel(bucket='dd_sf_auth', key=account)
                    cleaned_count += 1
                else:
                    valid_accounts.append(account)
            
            valid_accounts = list(dict.fromkeys(valid_accounts))
            
            if valid_accounts:
                middleware.bucketSet(bucket='dd_sf_user', key=user, value=str(valid_accounts))
            else:
                middleware.bucketDel(bucket='dd_sf_user', key=user)
                
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    
    sender.reply(format_message("清理完成", f"已清理: {cleaned_count}个账号", "success"))

def sync_to_panel():
    users = middleware.bucketAllKeys(bucket='dd_sf_user')
    
    if not users:
        sender.reply(format_message("同步结果", "未找到任何绑定账号", "error"))
        return
        
    sender.reply(format_message("开始同步", f"共找到: {len(users)}个用户\n⏳ 同步中请稍候...", "loading"))
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_sf_user', key=user)
            if not accountlist:
                continue
                
            accounts = parse_accounts(accountlist)
            for account in accounts:
                try:
                    accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
                    if not accountVip or accountVip <= today_time:
                        skip_count += 1
                        continue
                    
                    token = get_token_as_ck(account)
                    if not token:
                        fail_count += 1
                        continue
                    
                    phone = mask_phone(account)
                    Addenvs(
                        osname=dd_sf_osname,
                        value=token,
                        account=account,
                        phone=phone,
                        target_userid=user,
                        expire_time=accountVip
                    )
                    success_count += 1
                    
                except Exception as e:
                    print(f"同步账号 {account} 失败: {str(e)}")
                    fail_count += 1
                    continue
                    
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    
    result_msg = f"""=====同步完成=====
✅ 成功同步: {success_count}个账号
⏭️ 跳过未授权: {skip_count}个账号
❌ 同步失败: {fail_count}个账号
=================="""
    sender.reply(result_msg)

def sf_backend_manage():
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)
        
    backend_menu = """=====顺丰后台管理=====
[1] 顺丰授权
[2] 顺丰清理
[3] 顺丰面板同步
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(backend_menu)
    xz = sender.listen(60000)

    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出后台管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '1':
        sf_auth()
    elif xz == '2':
        clean_expired_accounts()
    elif xz == '3':
        sync_to_panel()
    else:
        sender.reply("❌ 输入错误,请重新选择")
        return

def query_large_coupons(session_id, show_other_coupons=False):
    url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/coupon/available/list"
    
    headers = {
        "Cookie": f"sessionId={session_id}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148"
    }
    
    data = {
        "couponType": "",
        "pageNo": 1,
        "pageSize": 100
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if not result.get('success'):
            return "优惠券查询失败"
            
        coupons = result.get('obj', [])
        if not coupons:
            return "暂无优惠券"
            
        free_coupons = []
        other_coupons = []
        
        for coupon in coupons:
            try:
                coupon_name = coupon.get('couponName', '未知优惠券')
                expire_time = coupon.get('invalidTm', '')
                coupon_value = coupon.get('discountPrice', 0)
                coupon_num = coupon.get('couponNum', 1)
                coupon_amount = 0
                try:
                    coupon_amount = float(coupon_value)
                except (TypeError, ValueError):
                    pass
                if coupon_amount <= 0:
                    amount_match = re.match(r'^(\d+)元', coupon_name)
                    if amount_match:
                        coupon_amount = int(amount_match.group(1))
                if '寄件' in coupon_name and coupon_amount >= 12:
                    if coupon_num > 1:
                        coupon_info = f"{coupon_name} (共{coupon_num}张), 过期时间: {expire_time}"
                    else:
                        coupon_info = f"{coupon_name}, 过期时间: {expire_time}"
                    free_coupons.append(coupon_info)
                elif show_other_coupons:
                    try:
                        if isinstance(coupon_value, (int, float)) and coupon_value >= 10:
                            if coupon_num > 1:
                                coupon_info = f"{coupon_name} (共{coupon_num}张), 面额: {coupon_value}元, 过期时间: {expire_time}"
                            else:
                                coupon_info = f"{coupon_name}, 面额: {coupon_value}元, 过期时间: {expire_time}"
                            other_coupons.append(coupon_info)
                        else:
                            amount_match = re.search(r'(\d+)元', coupon_name)
                            if amount_match:
                                amount = int(amount_match.group(1))
                                if amount >= 10:
                                    if coupon_num > 1:
                                        coupon_info = f"{coupon_name} (共{coupon_num}张), 过期时间: {expire_time}"
                                    else:
                                        coupon_info = f"{coupon_name}, 过期时间: {expire_time}"
                                    other_coupons.append(coupon_info)
                    except:
                        continue
                        
            except Exception as e:
                print(f"处理优惠券出错: {str(e)}")
                continue
        
        result_lines = []
        if free_coupons:
            result_lines.extend(free_coupons)
        
        if show_other_coupons and other_coupons:
            if free_coupons:
                result_lines.append("------------------")
                result_lines.append("🎫 其他大额优惠券:")
            result_lines.extend(other_coupons)
        
        if not result_lines:
            return "无"
            
        return '\n'.join(result_lines)
        
    except Exception as e:
        print(f"优惠券查询异常: {str(e)}")
        return "无"

def show_tutorial():
    tutorial = """📚 顺丰插件教程

🔰 基础功能指令:
1️⃣ 顺丰登录 - 绑定顺丰账号(支持验证码登录 / 微信扫码登录)
2️⃣ 顺丰查询 - 查看账号积分、大额优惠券和快递数量
3️⃣ 顺丰快递查询 - 查询寄件/收件快递详情和物流轨迹
4️⃣ 顺丰管理 - 管理已绑定账号([0]批量授权 [1-N]单个账号)
5️⃣ 顺丰刷新 - 刷新登录态并同步最新 CK

🔧 管理员功能:
• 顺丰后台 - 进入管理员后台
• 后台内可执行: 顺丰授权 / 顺丰清理 / 顺丰面板同步

⚠️ 注意事项:
1. 定期查看账号状态，授权到期后及时续费"""
    sender.reply(tutorial)

dd_sf_osname, dd_sf_qlname, dd_managecommand, dd_querycommand, dd_signcommand, \
sfVipmoney, sfcoin, show_point_status, \
show_other_coupons, use_ma_pay, use_daidai, dd_sf_ddname, panel_group = getusercontent()
if use_daidai:
    panel_url, panel_token = seekdd()
    QLurl, qltoken = panel_url, panel_token
else:
    QLurl, qltoken = seekql()
    panel_url, panel_token = QLurl, qltoken
imtype = sender.getImtype()
today_date = datetime.now().date()
today_time = str(today_date)
usermessage = sender.getMessage()
if '登录' in usermessage or '登陆' in usermessage:
    bindaccount()
elif '管理' in usermessage:
    if uservalue:
        meituanmanage()
    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {dd_signcommand} 绑定
==================""")
elif '快递查询' in usermessage:
    sf_express_interactive_query()
elif '查询' in usermessage:
    if uservalue:
        cxs()
    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {dd_signcommand} 绑定
==================""")
elif usermessage == '顺丰后台':
    sf_backend_manage()
elif usermessage == '顺丰教程':
    show_tutorial()
elif usermessage in ('顺丰刷新', '顺丰Token刷新'):
    refresh_all_signs()
elif imtype == 'fake':
    users = middleware.bucketAllKeys(bucket='dd_sf_user')
    for user in users:
        accountlist = middleware.bucketGet(bucket='dd_sf_user', key=f'{user}')
        if not accountlist:
            continue
        accounts = parse_accounts(accountlist)
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='dd_sf_auth', key=account)
            ck = get_ck_with_fallback(account)
            if ck and validate_ck(ck):
                if has_valid_auth(accountVip, today_time):
                    try:
                        expire_date = datetime.strptime(accountVip, "%Y-%m-%d")
                        days_left = (expire_date - datetime.now()).days
                        if days_left <= 3:
                            push(user=user, account=account, c=f"""
⏰ 定时检测提醒
------------------
⚠️ 授权即将到期
📅 到期时间: {accountVip}
⏳ 剩余天数: {days_left}天
💡 请及时续费授权""")
                    except:
                        pass
                    try:
                        phone = mask_phone(account)
                        Addenvs(osname=dd_sf_osname, value=ck, account=account, phone=phone, target_userid=user, expire_time=accountVip)
                    except:
                        pass
                else:
                    qlid = allenvs(osname=dd_sf_osname, account=account)
                    delenvs(id=qlid)
                    push(user=user, account=account, c="""
⏰ 定时检测提醒
------------------
❌ 授权已过期
💡 请及时续费授权""")
            else:
                push(user=user, account=account, c="""
⏰ 定时检测提醒
------------------
❌ CK已失效，登录态异常
💡 请尽快重新登录""")
else:
    sender.setContinue()
