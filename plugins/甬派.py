# [rule: ^(甬派|yy)(登录|登陆)$|^登(录|陆)(甬派|yy)$|^甬派查询$|^甬派管理$|^甬派清理$|^甬派后台管理$|^甬派教程$]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 56 6,16 * * *]
# [public: true]
# [title: 甬派]
# [icon: https://img.cdn1.vip/i/6a0b1e9842df2_1779113624.webp]
# [open_source: false]
# [class: 工具类]
# [version: 4.5]
# [price: 38.88]
# [admin: false]
# [author: sky2022]
# [service: 2661320550]
# [description: 介绍：甬派插件 <br>登录格式：手机号#密码#支付宝账号#支付宝姓名 <br>指令：甬派登录、甬派管理、甬派查询、甬派清理、甬派后台]

import re
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal
import requests
import time
import json
import hashlib
import urllib.parse
import uuid
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

senderID = middleware.getSenderID()
# 创建发送者
sender = middleware.Sender(senderID)
# 获取发送者QQ号
userid = sender.getUserID()
# 获取用户的值
uservalue = middleware.bucketGet(bucket='dd_yy_user', key=userid)

android_versions = ['7.0', '8.0', '9.0', '10', '11', '12', '13']
phone_models = ['Xiaomi', 'Samsung Galaxy', 'Huawei', 'OPPO', 'Vivo', 'Realme', 'Oppo']

LOTTERY_ACTIVITY_ID = 1997
LOTTERY_Q = "1DvvL80TsnkfuVjfbdhTeOa1Xz0ttq5tQkt33EX3Kvc="
LOTTERY_TENANT_CODE = "yongpai"


# [param: {"required":true,"key":"dd_yy.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_yy.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_yy.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_yy.panel_group","bool":false,"placeholder":"例:甬派","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_yy.dd_yy_osname","bool":false,"placeholder":"必填项,例:yyToken","name":"面板变量名","desc":"提交到面板中的甬派变量名"}]
# [param: {"required":true,"key":"dd_yy.yyVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_yy.yycoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_yy.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# [param: {"required":false,"key":"dd_yy.prize_show_count","bool":false,"placeholder":"默认5","name":"中奖记录显示条数","desc":"查询时显示最近多少条中奖记录，不填默认显示5条"}]
# [param: {"required":false,"key":"dd_yy.proxy_url","bool":false,"placeholder":"例:http://127.0.0.1:8899","name":"代理地址","desc":"代理服务器地址，用于登录请求"}]
def normalize_panel_type(panel_type_value):
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    if value:
        return ''
    return 'qinglong'


def getusercontent():
    dd_yy_osname = middleware.bucketGet('dd_yy', 'dd_yy_osname') or 'dd_yy_token'
    panel_type_value = middleware.bucketGet('dd_yy', 'panel_type') or ''
    panel_config_value = (middleware.bucketGet('dd_yy', 'panel_config') or '').strip()
    panel_group = (middleware.bucketGet('dd_yy', 'panel_group') or '').strip()
    legacy_ql_config = middleware.bucketGet('dd_yy', 'dd_yy_qlname') or ''
    dd_managecommand = middleware.bucketGet('dd_yy', 'dd_managecommand') or '甬派管理'
    dd_querycommand = middleware.bucketGet('dd_yy', 'dd_querycommand') or '甬派查询'
    dd_signcommand = middleware.bucketGet('dd_yy', 'dd_signcommand') or '甬派登录'
    dd_tutorialcommand = '甬派教程'
    proxy_url = middleware.bucketGet('dd_yy', 'proxy_url')

    # 生成随机指令
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand

    # 获取价格配置
    yyVipmoney = Decimal(middleware.bucketGet('dd_yy', 'yyVipmoney') or '1')
    yycoin = int(middleware.bucketGet('dd_yy', 'yycoin') or '0')

    # 码支付配置
    use_ma_pay = middleware.bucketGet('dd_yy', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'

    # 中奖记录显示条数
    prize_show_count = int(middleware.bucketGet('dd_yy', 'prize_show_count') or '5')

    # 面板类型
    panel_type = normalize_panel_type(panel_type_value)
    if not panel_type:
        sender.reply("""
=====配置错误=====
❌ 对接面板类型填写无效
------------------
请填写以下任一值:
• 青龙 / 青龙面板 / QL
• 呆呆 / 呆呆面板 / Daidai
==================""")
        exit(0)

    use_daidai = panel_type == 'daidai'
    if use_daidai:
        dd_yy_ddname = panel_config_value or ''
        dd_yy_qlname = legacy_ql_config
    else:
        dd_yy_qlname = panel_config_value or legacy_ql_config
        dd_yy_ddname = ''

    return (dd_yy_osname, dd_yy_qlname, dd_managecommand, dd_querycommand,
            dd_signcommand, randommanagecommand, randomquerycommand,
            randomsigncommand, yyVipmoney, yycoin, proxy_url,
            use_ma_pay, use_daidai, dd_yy_ddname, panel_group, prize_show_count)


def update_proxy(session, proxy_url):
    """更新代理配置，返回代理字典"""
    if not proxy_url:
        return None

    try:
        ip_raw = requests.get(proxy_url, timeout=5).text.strip()
        if "请先添加白名单" in ip_raw:
            print("代理服务异常：请先添加白名单")
            return None
        
        # 取第一行代理（有些API返回多行）
        ip_raw = ip_raw.splitlines()[0].strip()
        
        if not ip_raw:
            print("获取到的代理为空")
            return None
        
        # 如果没带协议，自动补上 http://
        if not ip_raw.startswith("http://") and not ip_raw.startswith("https://"):
            proxy_url_full = "http://" + ip_raw
        else:
            proxy_url_full = ip_raw
            
        proxies = {'http': proxy_url_full, 'https': proxy_url_full}
        return proxies
    except Exception as e:
        print(f"获取代理失败: {str(e)}")
        return None


def seekql():
    try:
        if len(dd_yy_qlname) == 0:
            sender.reply("""
=====配置错误=====
❌ 未配置青龙信息
------------------
请在插件配置中填写:
Host丨ClientID丨ClientSecret
• 使用中文丨分隔
• 示例:
http://ql.example.com丨abcd丨1234
==================""")
            exit(0)

        qllist = dd_yy_qlname.split('丨')
        if len(qllist) != 3:
            sender.reply("""
=====格式错误=====
❌ 青龙配置格式错误
------------------
当前格式: {dd_yy_qlname}
正确格式:
Host丨ClientID丨ClientSecret
==================""")
            exit(0)

        QLurl = qllist[0].strip()
        ClientID = qllist[1].strip()
        ClientSecret = qllist[2].strip()

        # 验证每个参数是否为空
        if not all([QLurl, ClientID, ClientSecret]):
            sender.reply("""
=====参数错误=====
❌ 青龙配置参数不完整
------------------
请确保以下参数都已填写:
• 青龙面板地址(Host)
• 应用ID(ClientID)
• 应用密钥(ClientSecret)
==================""")
            exit(0)

        # 验证URL格式
        if not QLurl.startswith(('http://', 'https://')):
            sender.reply(f"""
=====地址错误=====
❌ 青龙地址格式错误
------------------
当前地址: {QLurl}
正确格式:
• http://qinglong.example.com
• https://ql.example.com:5700
==================""")
            exit(0)

        try:
            qltoken = QLtoken(QLurl=QLurl, ClientID=ClientID, ClientSecret=ClientSecret)
            return QLurl, qltoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")

    except Exception as e:
        sender.reply(f"""
=====连接失败=====
❌ 无法连接青龙面板
------------------
请检查:
1. 青龙面板是否运行
2. 网络是否正常
3. 配置是否正确
4. 错误信息: {str(e)}
------------------
当前配置:
• 地址: {QLurl if 'QLurl' in locals() else '未设置'}
• 应用ID: {ClientID[:4] + '****' if 'ClientID' in locals() else '未设置'}
==================""")
        exit(0)


def seekdd():
    try:
        if not dd_yy_ddname:
            sender.reply("""
=====配置错误=====
❌ 未配置呆呆面板信息
------------------
请在插件配置中填写:
• 对接面板类型: 呆呆
• 对接面板配置: Host丨AppKey丨AppSecret
• 使用中文丨分隔
==================""")
            exit(0)

        ddlist = dd_yy_ddname.split('丨')
        if len(ddlist) != 3:
            sender.reply(f"""
=====格式错误=====
❌ 呆呆面板配置格式错误
------------------
当前格式: {dd_yy_ddname}
正确格式:
Host丨AppKey丨AppSecret
==================""")
            exit(0)

        DDurl = ddlist[0].strip()
        AppKey = ddlist[1].strip()
        AppSecret = ddlist[2].strip()

        if not all([DDurl, AppKey, AppSecret]):
            sender.reply("""
=====参数错误=====
❌ 呆呆面板配置参数不完整
------------------
请确保以下参数都已填写:
• 面板地址(Host)
• AppKey
• AppSecret
==================""")
            exit(0)

        if not DDurl.startswith(('http://', 'https://')):
            sender.reply(f"""
=====地址错误=====
❌ 呆呆面板地址格式错误
------------------
当前地址: {DDurl}
正确格式:
• http://panel.example.com
• https://panel.example.com
==================""")
            exit(0)

        try:
            ddtoken = DDtoken(DDurl=DDurl, AppKey=AppKey, AppSecret=AppSecret)
            return DDurl, ddtoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")

    except SystemExit:
        raise
    except Exception as e:
        sender.reply(f"""
=====连接失败=====
❌ 无法连接呆呆面板
------------------
请检查:
1. 面板是否运行
2. 网络是否正常
3. 配置是否正确
4. 错误信息: {str(e)}
------------------
当前配置:
• 地址: {DDurl if 'DDurl' in locals() else '未设置'}
• AppKey: {AppKey[:4] + '****' if 'AppKey' in locals() else '未设置'}
==================""")
        exit(0)


def DDtoken(DDurl, AppKey, AppSecret):
    try:
        url = f'{DDurl}/api/open-api/token'
        data = {"app_key": AppKey, "app_secret": AppSecret}
        response = requests.post(url, json=data)

        if response.status_code != 200:
            sender.reply(f"""
=====请求失败=====
❌ 呆呆面板API请求失败
状态码: {response.status_code}
==================""")
            exit(0)

        result = response.json()
        access_token = result.get('data', {}).get('access_token')
        if access_token:
            return access_token
        else:
            sender.reply("""
=====认证失败=====
❌ 获取Token失败
------------------
请检查:
• AppKey是否正确
• AppSecret是否正确
• 应用是否有权限
==================""")
            exit(0)

    except requests.exceptions.RequestException as e:
        sender.reply(f"""
=====网络错误=====
❌ 连接呆呆面板失败
错误信息: {str(e)}
==================""")
        exit(0)
    except SystemExit:
        raise
    except Exception as e:
        sender.reply(f"""
=====系统错误=====
❌ 处理请求时出错
错误信息: {str(e)}
==================""")
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
        sender.reply('连接呆呆面板获取变量失败')
        exit(0)


def dd_delenvs(id):
    if id is None:
        return
    url = f"{panel_url}/api/envs/{id}"
    headers = get_dd_headers()
    requests.delete(url, headers=headers)


def DDcreate(osname, value, account, phone, target_userid=None):
    try:
        actual_userid = target_userid if target_userid else userid
        accountVip = middleware.bucketGet('dd_yy_auth', account) or str(datetime.now().date())
        url = f"{panel_url}/api/envs"

        data = {
            "value": value,
            "name": osname,
            "remarks": f'甬派:{account}丨用户:{actual_userid}丨手机:{phone}丨到期:{accountVip}丨甬派管理'
        }
        if panel_group:
            data["group"] = panel_group

        headers = get_dd_headers()
        response = requests.post(url, headers=headers, json=data)

        if response.status_code not in (200, 201):
            sender.reply(f"""
=====添加变量失败=====
❌ 请求失败
状态码: {response.status_code}
==================""")
            exit(0)

        result = response.json()
        resp_data = result.get('data')
        if resp_data:
            return resp_data.get('id')

    except SystemExit:
        raise
    except Exception as e:
        sender.reply(f"""
=====系统错误=====
❌ 添加变量失败
错误信息: {str(e)}
==================""")
        exit(0)


def DDupdate(osname, value, account, env_id, phone, target_userid=None):
    actual_userid = target_userid if target_userid else userid
    accountVip = middleware.bucketGet('dd_yy_auth', account) or str(datetime.now().date())
    url = f"{panel_url}/api/envs/{env_id}"

    data = {
        "value": value,
        "name": osname,
        "remarks": f'甬派:{account}丨用户:{actual_userid}丨手机:{phone}丨到期:{accountVip}丨甬派管理'
    }
    if panel_group:
        data["group"] = panel_group

    headers = get_dd_headers()
    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        return env_id, None
    else:
        sender.reply('更新变量失败,请联系管理员处理')
        exit(0)


def delenvs(id):
    if id is None:
        return
    if use_daidai:
        dd_delenvs(id)
        return
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = [id]
    response = requests.delete(url, headers=headers, json=data).json()


def allenvs(osname, account):
    if use_daidai:
        return dd_allenvs(osname, account)
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json"
    }
    response = requests.get(url=url, headers=headers).json()
    qlid = None
    if response['code'] == 200:
        envslist = response['data']
        for envs in envslist:
            envname = envs['name']
            remarks = envs['remarks']
            if remarks is None:
                continue
            if osname == envname and str(account) in remarks:
                qlid = envs['id']
                break
        return qlid
    else:
        sender.reply('连接青龙获取变量失败')
        exit(0)


def Addenvs(osname, value, account, phone, target_userid=None):
    phone = phone[:3] + '*' * 4 + phone[7:]

    if use_daidai:
        env_id = dd_allenvs(osname, account)
        if env_id is None:
            DDcreate(osname, value, account, phone, target_userid)
        else:
            DDupdate(osname, value, account, env_id, phone, target_userid)
        return

    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json"
    }
    response = requests.get(url=url, headers=headers).json()
    qlid = None
    if response['code'] == 200:
        envslist = response['data']
        for envs in envslist:
            remarks = envs['remarks']
            envname = envs['name']
            if remarks is None:
                continue
            if account in remarks and osname == envname:
                qlid = envs['id']
                break
    else:
        sender.reply('连接青龙获取变量失败')
        exit(0)

    if qlid is None:
        QLzt(osname, value, account, phone, target_userid)
    else:
        QLupdate(osname, value, account, qlid, phone, target_userid)


def QLupdate(osname, value, account, qlid, phone, target_userid=None):
    qlurl = f"{QLurl}/open/envs"
    # 获取账号到期时间
    accountVip = middleware.bucketGet('dd_yy_auth', account) or str(datetime.now().date())
    # 使用传入的target_userid，如果没有则使用当前用户ID
    user_id_for_remarks = target_userid if target_userid is not None else userid
    data = {
        "value": value,
        "name": osname,
        "remarks": f'甬派:{account}丨用户:{user_id_for_remarks}丨到期:{accountVip}丨甬派管理',
        "id": qlid
    }
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.put(qlurl, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response_json = response.json()
        data = response_json['data']
        if data is None:
            exit(0)
        id = data['id']
        createdAt = data['createdAt']
        return id, createdAt
    else:
        sender.reply('更新变量失败,请联系管理员处理')
        exit(0)


def QLzt(osname, value, account, phone, target_userid=None):  # 添加青龙变量
    try:
        qlurl = f"{QLurl}/open/envs"
        accountVip = middleware.bucketGet('dd_yy_auth', account) or str(datetime.now().date())
        # 使用传入的target_userid，如果没有则使用当前用户ID
        user_id_for_remarks = target_userid if target_userid is not None else userid

        data = [{
            "value": value,
            "name": osname,
            "remarks": f'甬派:{account}丨用户:{user_id_for_remarks}丨到期:{accountVip}丨甬派管理'
        }]

        headers = {
            "Authorization": f"Bearer {qltoken}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

        response = requests.post(qlurl, headers=headers, json=data)

        if response.status_code != 200:
            sender.reply(f"""
=====添加变量失败=====
❌ 请求失败
状态码: {response.status_code}
==================""")
            exit(0)

        result = response.json()
        if result.get('code') != 200:
            sender.reply(f"""
=====添加变量失败=====
❌ 青龙返回错误
错误信息: {result.get('message')}
==================""")
            exit(0)

        if "value must be unique" in response.text:
            # 变量已存在,不需要处理
            return

        data = result.get('data')
        if not data or not isinstance(data, list) or len(data) == 0:
            sender.reply("""
=====添加变量失败=====
❌ 青龙返回数据异常
==================""")
            exit(0)

        return data[0].get('id')

    except Exception as e:
        sender.reply(f"""
=====系统错误=====
❌ 添加青龙变量失败
------------------
错误信息: {str(e)}
==================""")
        exit(0)


def QLtoken(QLurl, ClientID, ClientSecret):  # 获取青龙token
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)

        if response.status_code != 200:
            sender.reply(f"""
=====请求失败=====
❌ 青龙API请求失败
------------------
状态码: {response.status_code}
请检查:
• API地址是否正确
• 面板是否正常运行
==================""")
            exit(0)

        result = response.json()
        if "token" in result.get('data', {}):
            return result['data']['token']
        else:
            sender.reply("""
=====认证失败=====
❌ 获取Token失败
------------------
请检查:
• ClientID是否正确
• ClientSecret是否正确
• 应用是否有权限
==================""")
            exit(0)

    except requests.exceptions.RequestException as e:
        sender.reply(f"""
=====网络错误=====
❌ 连接青龙面板失败
------------------
请检查:
• 青龙地址是否正确
• 网络是否正常
• 错误信息: {str(e)}
==================""")
        exit(0)
    except Exception as e:
        sender.reply(f"""
=====系统错误=====
❌ 处理请求时出错
------------------
请检查:
• 配置格式是否正确
• 错误信息: {str(e)}
==================""")
        exit(0)


def getRandom(start, end):
    return random.randint(start, end)


def generate_random_ua():
    android_version = random.choice(android_versions)
    phone_model = random.choice(phone_models) + random.choice(['Note', 'Pro', 'X', 'S']) + str(random.randint(1, 30))
    ua = f'Mozilla/5.0 (Linux; Android {android_version}; {phone_model} Build/RP1A.00121.012) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.92 Mobile Safari/537.36'
    return ua


def ValueErrors(value, count):
    """验证输入值是否为有效的整数且在合理范围内"""
    try:
        value = int(value)
        if value > count or value == 0:
            sender.reply(f"""
=====输入无效=====
❌ 请输入 1-{count} 之间的数字
==================""")
            exit(0)
        return value
    except ValueError:
        sender.reply("""
=====输入无效=====
❌ 请输入正确的数字
==================""")
        exit(0)


def parse_batch_selection(input_str, max_count):
    """解析批量选择输入，支持逗号分隔和范围选择
    示例：
    - 1,3,5 -> [1,3,5]
    - 1-5 -> [1,2,3,4,5]
    - 1,3-5,7 -> [1,3,4,5,7]
    """
    try:
        selected_indices = []
        parts = input_str.split(',')

        for part in parts:
            part = part.strip()
            if '-' in part:
                # 处理范围选择
                range_parts = part.split('-')
                if len(range_parts) == 2:
                    start = int(range_parts[0].strip())
                    end = int(range_parts[1].strip())
                    if start <= end and start >= 1:
                        selected_indices.extend(range(start, end + 1))
                    else:
                        raise ValueError(f"范围格式错误: {part}")
                else:
                    raise ValueError(f"范围格式错误: {part}")
            else:
                # 处理单个数字
                selected_indices.append(int(part))

        # 去重并排序
        selected_indices = sorted(list(set(selected_indices)))

        # 验证范围
        valid_indices = []
        invalid_indices = []

        for idx in selected_indices:
            if 1 <= idx <= max_count:
                valid_indices.append(idx)
            else:
                invalid_indices.append(idx)

        return valid_indices, invalid_indices

    except ValueError as e:
        raise ValueError(f"输入格式错误: {str(e)}")


def generate_md5(input_string):
    md5_hash = hashlib.md5()
    md5_hash.update(input_string.encode('utf-8'))
    md5_digest = md5_hash.hexdigest()
    return md5_digest


def yesornos():
    yesorno = sender.input(120000, 1, False)
    if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
        return True
    elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
        return False
    elif yesorno == '':
        sender.reply('输入超时！')
        exit(0)
    elif yesorno == 'q' or yesorno == 'Q' or yesorno == '退出':
        sender.reply('退出!')
        exit(0)
    else:
        sender.reply('输入错误！')
        exit(0)


def sf_login(sender):
    """甬派账号登录"""
    login_guide = """
=====甬派账号登录=====
请按以下格式输入账号信息:
手机号#密码#zfb账号(可用邮箱)#zfb姓名

🔰 支持批量登录，一行一个账号
示例:
13812345678#123456#13888888888#张三
13912345678#123456#13999999999#李四

注意: 
• zfb信息用于自动提现
• 批量登录时请确保格式正确
------------------
回复"q"退出操作
=================="""
    sender.reply(login_guide)

    account_info = sender.input(120000, 1, False)
    if not account_info:
        sender.reply("⏰ 操作超时,已退出")
        exit(0)
    elif account_info.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)

    # 分割多行输入
    account_lines = account_info.strip().split('\n')
    success_count = 0
    fail_count = 0

    # 获取现有账号列表
    accounts = []
    if uservalue:
        try:
            existing_accounts = eval(uservalue)
            if isinstance(existing_accounts, (list, tuple, set)):
                accounts = list(existing_accounts)
            else:
                accounts = [str(existing_accounts)]
        except:
            accounts = []

    # 如果是批量登录（多于一行）
    is_batch = len(account_lines) > 1
    last_success_info = None
    last_success_phone = None

    for line in account_lines:
        line = line.strip()
        if not line:  # 跳过空行
            continue

        # 解析输入信息
        try:
            parts = line.split('#')
            if len(parts) != 4:
                fail_count += 1
                continue

            phone, password, alipay, realname = parts

            # 验证手机号格式
            if not re.match(r'^1[3-9]\d{9}$', phone):
                fail_count += 1
                continue

            # 初始化session并配置代理
            session = requests.session()
            proxies = None
            if proxy_url:
                proxies = update_proxy(session, proxy_url)

            # 生成随机UA
            ua = generate_random_ua() + ' agentweb/4.0.2 UCBrowser/11.6.4.950 yongpai'
            
            # 设置完整的请求头
            session.headers.update({
                'Host': 'ypapp.cnnb.com.cn',
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': ua,
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            })

            # 尝试登录（添加重试机制）
            deviceId = str(uuid.uuid4())
            ts = str(int(time.time() * 1000))
            sign = hashlib.md5(f'globalDatetime{ts}username{phone}test_123456679890123456'.encode()).hexdigest()
            url = f'https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3?username={phone}&password={password}&deviceId={deviceId}&globalDatetime={ts}&sign={sign}'

            # 添加重试逻辑
            result = None
            login_success = False
            for retry in range(3):
                try:
                    response = session.get(url, proxies=proxies, timeout=5)
                    result = response.json()
                    login_success = True
                    break
                except Exception as e:
                    if retry < 2:
                        time.sleep(1)
                        # 失败时更新代理重试
                        if proxy_url:
                            proxies = update_proxy(session, proxy_url)
                        continue
                    else:
                        fail_count += 1
                        break
            
            # 如果请求失败，跳过这个账号
            if not login_success or not result:
                continue

            if result.get("code") == 0:
                # 本地存储完整账号信息
                middleware.bucketSet(bucket='dd_yy_token', key=phone, value=line)

                # 添加到账号列表
                if phone not in accounts:
                    accounts.append(phone)
                success_count += 1

                # 保存最后一个成功的账号信息
                last_success_info = line
                last_success_phone = phone
            else:
                fail_count += 1

        except Exception as e:
            fail_count += 1
            continue

    # 更新用户账号列表
    if accounts:
        # 使用集合去重并保持顺序
        accounts = list(dict.fromkeys(accounts))
        middleware.bucketSet(bucket='dd_yy_user', key=userid, value=str(accounts))

    # 显示批量登录结果
    if is_batch:
        # 在批量登录后，检查已授权账号并更新青龙变量
        updated_count = 0
        for line in account_lines:
            line = line.strip()
            if not line:
                continue

            try:
                parts = line.split('#')
                if len(parts) != 4:
                    continue

                phone, password, alipay, realname = parts

                # 验证手机号格式
                if not re.match(r'^1[3-9]\d{9}$', phone):
                    continue

                # 检查该账号是否成功登录且已授权
                stored_info = middleware.bucketGet(bucket='dd_yy_token', key=phone)
                if stored_info and stored_info == line:  # 确认是刚才成功登录的账号
                    accountVip = middleware.bucketGet('dd_yy_auth', phone)
                    if accountVip and accountVip >= today_time:
                        try:
                            # 更新青龙变量
                            login_mobile = phone[:3] + '*' * 4 + phone[7:]
                            qlid = allenvs(osname=dd_yy_osname, account=phone)
                            if qlid:
                                # 如果变量存在，更新它
                                QLupdate(osname=dd_yy_osname, value=line, account=phone, qlid=qlid, phone=login_mobile)
                            else:
                                # 如果变量不存在，添加新的
                                Addenvs(osname=dd_yy_osname, value=line, account=phone, phone=login_mobile)
                            updated_count += 1
                        except Exception as e:
                            print(f"更新账号 {phone} 的青龙变量时出错: {str(e)}")
                            continue

            except Exception as e:
                continue

        result_msg = f"""
=====批量登录结果=====
✅ 成功: {success_count}个账号
❌ 失败: {fail_count}个账号"""

        if updated_count > 0:
            result_msg += f"""
🔄 已更新: {updated_count}个已授权账号的青龙变量"""

        result_msg += f"""
------------------
💡 发送 {randommanagecommand} 可管理账号
=================="""
        sender.reply(result_msg)
        exit(0)  # 批量登录后直接退出
    elif success_count == 1:
        # 单个账号登录成功，返回账号信息
        return last_success_info, last_success_phone, last_success_phone
    else:
        sender.reply("""
=====登录失败=====
❌ 所有账号登录均失败
==================""")
        exit(0)


def bindaccount():
    account_info, account, mobile = sf_login(sender)

    # 处理账号绑定逻辑
    def accvip(account, account_info, mobile):
        accountVip = middleware.bucketGet('dd_yy_auth', account)
        auth_status = '✅ 已授权' if accountVip and accountVip >= today_time else '⚠️ 未授权'
        next_step = f'发送 {randommanagecommand} 可管理账号' if accountVip and accountVip >= today_time else f'发送 {randommanagecommand} 可进行授权'

        success_msg = f"""
=====甬派账号绑定=====
📱 绑定账号: {mobile}
🔐 授权状态: {auth_status}
⏰ 下一步操作: 
   {next_step}
=================="""

        # 获取并处理账号列表
        accounts = []
        if uservalue:
            try:
                existing_accounts = eval(uservalue)
                if isinstance(existing_accounts, (list, tuple, set)):
                    accounts = list(existing_accounts)
                else:
                    accounts = [str(existing_accounts)]
            except:
                accounts = []

        # 确保账号不重复
        if account not in accounts:
            accounts.append(account)

        # 使用集合去重并保持顺序
        accounts = list(dict.fromkeys(accounts))

        # 更新用户账号列表
        if accounts:
            middleware.bucketSet(bucket='dd_yy_user', key=userid, value=str(accounts))

        # 本地存储完整账号信息
        middleware.bucketSet(bucket='dd_yy_token', key=account, value=account_info)

        # 只有在已授权的情况下才更新青龙变量
        if accountVip and accountVip >= today_time:
            try:
                qlid = allenvs(osname=dd_yy_osname, account=account)
                if qlid:
                    # 如果变量存在，更新它（使用完整账号信息）
                    QLupdate(osname=dd_yy_osname, value=account_info, account=account, qlid=qlid, phone=mobile)
                else:
                    # 如果变量不存在，添加新的（使用完整账号信息）
                    Addenvs(osname=dd_yy_osname, value=account_info, account=account, phone=mobile)
            except Exception as e:
                sender.reply(f"""
=====青龙更新失败=====
❌ 更新青龙变量失败
⚠️ 错误: {str(e)}
==================""")

        sender.reply(success_msg)

    # 调用修改后的accvip函数
    accvip(account, account_info, mobile)


def empower(empowertime, me_as_int):
    """授权时间计算"""
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
    """甬派后台管理功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)

    auth_menu = """
=====甬派后台管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 更新面板变量
[4] 删除用户账号
[5] 加减用户授权时间
------------------
💡 清理过期请发送: 甬派清理
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
    elif xz == '5':
        # 加减用户授权时间
        time_menu = """
=====加减授权时间=====
[1] 单独加减用户授权时间
[2] 一键加减所有用户授权时间
------------------
回复数字选择功能
回复"q"退出操作
=================="""
        sender.reply(time_menu)

        time_choice = sender.listen(60000)
        if time_choice == 'q' or time_choice == 'Q':
            sender.reply("✅ 已退出时间管理")
            return
        elif time_choice is None:
            sender.reply("⏰ 操作超时,已退出")
            return

        if time_choice == '1':
            # 单独加减用户授权时间
            user_guide = """
=====单独加减授权时间=====
请输入用户ID
(发送myuid可获取ID)
------------------
回复"q"退出操作
=================="""
            sender.reply(user_guide)

            myuid = sender.listen(60000)
            if myuid == 'q' or myuid == 'Q':
                sender.reply("✅ 已退出操作")
                return
            elif myuid is None:
                sender.reply("⏰ 操作超时,已退出")
                return

            # 获取用户的账号列表
            accountlist = middleware.bucketGet('dd_yy_user', myuid)
            if not accountlist or accountlist == '{}':
                sender.reply(f"""
=====查询结果=====
❌ 未找到用户 {myuid} 的账号信息
==================""")
                return

            try:
                accounts = eval(accountlist)
                if isinstance(accounts, (list, tuple, set)):
                    accounts = list(accounts)
                else:
                    accounts = [str(accounts)]

                # 显示账号列表
                account_list = """
=====账号列表=====
[0] 加减全部账号时间
------------------"""

                for i, account in enumerate(accounts, 1):
                    accountVip = middleware.bucketGet('dd_yy_auth', account)
                    vip_status = accountVip if accountVip else '未授权'
                    login_mobile = account[:3] + "****" + account[7:]
                    account_list += f"""
[{i}] 账号: {login_mobile}
    授权至: {vip_status}
------------------"""

                account_list += """
回复数字选择账号
回复"q"退出操作
=================="""
                sender.reply(account_list)

                # 获取用户选择
                choice = sender.listen(60000)
                if choice == 'q' or choice == 'Q':
                    sender.reply("✅ 已退出操作")
                    return
                elif choice is None:
                    sender.reply("⏰ 操作超时,已退出")
                    return

                # 获取要加减的天数
                days_guide = """
=====设置加减天数=====
请输入要加减的天数
• 正数为增加天数
• 负数为减少天数
示例: 30 (增加30天)
示例: -15 (减少15天)
------------------
回复数字设置天数
回复"q"退出操作
=================="""
                sender.reply(days_guide)

                days_input = sender.listen(60000)
                if days_input == 'q' or days_input == 'Q':
                    sender.reply("✅ 已取消操作")
                    return
                elif days_input is None:
                    sender.reply("⏰ 操作超时,已退出")
                    return

                try:
                    days = int(days_input)
                except ValueError:
                    sender.reply("❌ 天数必须是数字!")
                    return

                if choice == '0':
                    # 加减该用户的所有账号时间
                    success_count = 0
                    for account in accounts:
                        try:
                            current_auth = middleware.bucketGet('dd_yy_auth', account)
                            token = middleware.bucketGet('dd_yy_token', account)

                            if not token:
                                continue

                            # 计算新的授权时间
                            if current_auth and current_auth > today_time:
                                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                            else:
                                auth_date = datetime.now()

                            new_auth_date = auth_date + timedelta(days=days)
                            new_auth_time = new_auth_date.strftime("%Y-%m-%d")

                            # 检查新时间是否有效（不能设置为过去的时间，除非是减少操作导致的）
                            if new_auth_time < today_time and days > 0:
                                sender.reply(f"❌ 账号 {account} 新授权时间不能早于今天")
                                continue

                            # 更新授权时间
                            middleware.bucketSet('dd_yy_auth', account, new_auth_time)

                            # 如果授权未过期，更新青龙变量
                            if new_auth_time >= today_time:
                                login_mobile = account[:3] + "****" + account[7:]
                                Addenvs(osname=dd_yy_osname, value=token, account=account, phone=login_mobile)
                            else:
                                # 如果授权已过期，删除青龙变量
                                qlid = allenvs(osname=dd_yy_osname, account=account)
                                if qlid:
                                    delenvs(id=qlid)

                            success_count += 1

                        except Exception as e:
                            print(f"处理账号 {account} 时出错: {str(e)}")
                            continue

                    action_text = "增加" if days > 0 else "减少"
                    result_msg = f"""
=====操作完成=====
👤 用户: {myuid}
📅 {action_text}: {abs(days)}天
✅ 成功: {success_count}/{len(accounts)}个账号
=================="""
                    sender.reply(result_msg)

                else:
                    # 加减单个账号时间
                    try:
                        choice_num = int(choice)
                        if choice_num < 1 or choice_num > len(accounts):
                            sender.reply("❌ 输入的序号无效")
                            return

                        account = accounts[choice_num - 1]
                        current_auth = middleware.bucketGet('dd_yy_auth', account)
                        token = middleware.bucketGet('dd_yy_token', account)

                        if not token:
                            sender.reply("❌ 未找到账号token信息!")
                            return

                        # 计算新的授权时间
                        if current_auth and current_auth > today_time:
                            auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                        else:
                            auth_date = datetime.now()

                        new_auth_date = auth_date + timedelta(days=days)
                        new_auth_time = new_auth_date.strftime("%Y-%m-%d")

                        # 更新授权时间
                        middleware.bucketSet('dd_yy_auth', account, new_auth_time)

                        # 如果授权未过期，更新青龙变量
                        if new_auth_time >= today_time:
                            login_mobile = account[:3] + "****" + account[7:]
                            Addenvs(osname=dd_yy_osname, value=token, account=account, phone=login_mobile)
                        else:
                            # 如果授权已过期，删除青龙变量
                            qlid = allenvs(osname=dd_yy_osname, account=account)
                            if qlid:
                                delenvs(id=qlid)

                        action_text = "增加" if days > 0 else "减少"
                        result_msg = f"""
=====操作完成=====
👤 用户: {myuid}
📱 账号: {account[:3] + "****" + account[7:]}
📅 {action_text}: {abs(days)}天
📅 新到期时间: {new_auth_time}
=================="""
                        sender.reply(result_msg)

                    except ValueError:
                        sender.reply("❌ 输入必须是数字")
                        return

            except Exception as e:
                sender.reply(f"""
=====操作失败=====
❌ 处理账号列表时出错
⚠️ 错误: {str(e)}
==================""")
                return

        elif time_choice == '2':
            # 一键加减所有用户授权时间
            users = middleware.bucketAllKeys('dd_yy_user')
            if not users:
                sender.reply("❌ 未找到任何绑定的甬派账号")
                return

            days_guide = """
=====一键加减授权时间=====
请输入要加减的天数
• 正数为增加天数
• 负数为减少天数
示例: 30 (增加30天)
示例: -15 (减少15天)
------------------
回复数字设置天数
回复"q"退出操作
=================="""
            sender.reply(days_guide)

            days_input = sender.listen(60000)
            if days_input == 'q' or days_input == 'Q':
                sender.reply("✅ 已取消操作")
                return
            elif days_input is None:
                sender.reply("⏰ 操作超时,已退出")
                return

            try:
                days = int(days_input)
            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return

            # 确认操作
            action_text = "增加" if days > 0 else "减少"
            confirm_msg = f"""
=====确认操作=====
将对所有用户的所有账号:
📅 {action_text}: {abs(days)}天
------------------
此操作将影响所有已绑定账号
确认请回复【y】
取消请回复【n】
=================="""
            sender.reply(confirm_msg)

            if not yesornos():
                sender.reply("✅ 已取消操作")
                return

            sender.reply("""
=====开始处理=====
⏳ 正在更新所有账号...
==================""")

            success_count = 0
            fail_count = 0

            for user in users:
                accountlist = middleware.bucketGet('dd_yy_user', user)
                if not accountlist or accountlist == '{}':
                    continue

                try:
                    accounts = eval(accountlist)
                    if isinstance(accounts, (list, tuple, set)):
                        accounts = list(accounts)
                    else:
                        accounts = [str(accounts)]

                    for account in accounts:
                        try:
                            current_auth = middleware.bucketGet('dd_yy_auth', account)
                            token = middleware.bucketGet('dd_yy_token', account)

                            if not token:
                                fail_count += 1
                                continue

                            # 计算新的授权时间
                            if current_auth and current_auth > today_time:
                                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                            else:
                                auth_date = datetime.now()

                            new_auth_date = auth_date + timedelta(days=days)
                            new_auth_time = new_auth_date.strftime("%Y-%m-%d")

                            # 更新授权时间
                            middleware.bucketSet('dd_yy_auth', account, new_auth_time)

                            # 如果授权未过期，更新青龙变量
                            if new_auth_time >= today_time:
                                login_mobile = account[:3] + "****" + account[7:]
                                Addenvs(osname=dd_yy_osname, value=token, account=account, phone=login_mobile)
                            else:
                                # 如果授权已过期，删除青龙变量
                                qlid = allenvs(osname=dd_yy_osname, account=account)
                                if qlid:
                                    delenvs(id=qlid)

                            success_count += 1

                        except Exception as e:
                            print(f"处理账号 {account} 时出错: {str(e)}")
                            fail_count += 1
                            continue

                except Exception as e:
                    print(f"处理用户 {user} 时出错: {str(e)}")
                    continue

            result_msg = f"""
=====操作完成=====
📅 {action_text}: {abs(days)}天
✅ 成功: {success_count}个账号
❌ 失败: {fail_count}个账号
=================="""
            sender.reply(result_msg)

        else:
            sender.reply("❌ 输入的选项无效!")
            return

    elif xz == '4':
        # 删除指定用户的账号
        user_guide = """
=====删除用户账号=====
请输入要删除的用户ID
(发送myuid可获取ID)
------------------
回复"q"退出操作
=================="""
        sender.reply(user_guide)

        myuid = sender.listen(60000)
        if myuid == 'q' or myuid == 'Q':
            sender.reply("✅ 已退出删除")
            return
        elif myuid is None:
            sender.reply("⏰ 操作超时,已退出")
            return

        # 获取用户的账号列表
        accountlist = middleware.bucketGet('dd_yy_user', myuid)
        if not accountlist or accountlist == '{}':
            sender.reply(f"""
=====查询结果=====
❌ 未找到用户 {myuid} 的账号信息
==================""")
            return

        try:
            accounts = eval(accountlist)
            if isinstance(accounts, (list, tuple, set)):
                accounts = list(accounts)
            else:
                accounts = [str(accounts)]

            # 显示账号列表
            account_list = """
=====账号列表=====
[0] 删除全部账号
------------------"""

            for i, account in enumerate(accounts, 1):
                accountVip = middleware.bucketGet('dd_yy_auth', account)
                vip_status = accountVip if accountVip else '未授权'
                account_list += f"""
[{i}] 账号信息:
📱 账号: {account}
🔐 授权至: {vip_status}
------------------"""

            account_list += """
回复数字选择账号
回复"q"退出操作
=================="""
            sender.reply(account_list)

            # 获取用户选择
            choice = sender.listen(60000)
            if choice == 'q' or choice == 'Q':
                sender.reply("✅ 已退出删除")
                return
            elif choice is None:
                sender.reply("⏰ 操作超时,已退出")
                return

            try:
                if choice == '0':
                    # 删除所有账号
                    confirm_msg = f"""
=====⚠️警告⚠️=====
即将删除用户 {myuid} 的所有账号:
• 共 {len(accounts)} 个账号
• 所有授权记录
• 所有青龙变量
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                    sender.reply(confirm_msg)

                    if not yesornos():
                        sender.reply("✅ 已取消删除")
                        return

                    deleted_accounts = 0
                    deleted_ql_vars = 0

                    for account in accounts:
                        try:
                            # 删除青龙变量
                            qlid = allenvs(osname=dd_yy_osname, account=account)
                            if qlid:
                                delenvs(id=qlid)
                                deleted_ql_vars += 1

                            # 删除token信息
                            middleware.bucketDel(bucket='dd_yy_token', key=account)
                            # 删除授权信息
                            middleware.bucketDel(bucket='dd_yy_auth', key=account)
                            deleted_accounts += 1

                        except Exception as e:
                            print(f"处理账号 {account} 时出错: {str(e)}")
                            continue

                    # 删除用户数据
                    middleware.bucketDel(bucket='dd_yy_user', key=myuid)

                    result_msg = f"""
=====删除完成=====
👤 用户: {myuid}
✅ 已删除:
• {deleted_accounts}/{len(accounts)}个账号
• {deleted_ql_vars}个青龙变量
=================="""
                    sender.reply(result_msg)

                else:
                    # 删除单个账号
                    choice = int(choice)
                    if choice < 1 or choice > len(accounts):
                        sender.reply("❌ 输入的序号无效")
                        return

                    account = accounts[choice - 1]
                    confirm_msg = f"""
=====⚠️警告⚠️=====
即将删除账号:
📱 账号: {account}
------------------
此操作不可恢复！
确认请回复【y】
取消请回复【n】
=================="""
                    sender.reply(confirm_msg)

                    if not yesornos():
                        sender.reply("✅ 已取消删除")
                        return

                    try:
                        # 删除青龙变量
                        qlid = allenvs(osname=dd_yy_osname, account=account)
                        if qlid:
                            delenvs(id=qlid)

                        # 删除token信息
                        middleware.bucketDel(bucket='dd_yy_token', key=account)
                        # 删除授权信息
                        middleware.bucketDel(bucket='dd_yy_auth', key=account)

                        # 更新用户的账号列表
                        accounts.remove(account)
                        if accounts:
                            middleware.bucketSet(bucket='dd_yy_user', key=myuid, value=str(accounts))
                        else:
                            middleware.bucketDel(bucket='dd_yy_user', key=myuid)

                        result_msg = f"""
=====删除完成=====
👤 用户: {myuid}
📱 账号: {account}
✅ 已删除账号及相关数据
=================="""
                        sender.reply(result_msg)

                    except Exception as e:
                        sender.reply(f"""
=====删除失败=====
❌ 删除账号时出错
⚠️ 错误: {str(e)}
==================""")
                        return

            except ValueError:
                sender.reply("❌ 输入必须是数字")
                return

        except Exception as e:
            sender.reply(f"""
=====删除失败=====
❌ 处理账号列表时出错
⚠️ 错误: {str(e)}
==================""")
            return

    elif xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('dd_yy_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的甬派账号")
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
            sjts = int(sjts)  # 确保转换为整数
        except:
            sender.reply("❌ 天数必须是数字!")
            return

        success_count = 0
        fail_count = 0

        for user in users:
            accountlist = middleware.bucketGet('dd_yy_user', user)
            if accountlist == '' or accountlist == '{}':
                continue

            accounts = eval(accountlist)
            for account in accounts:
                try:
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    accountVip = middleware.bucketGet('dd_yy_auth', account)
                    token = middleware.bucketGet('dd_yy_token', account)

                    if not token:
                        fail_count += 1
                        continue

                    if len(accountVip) != 0 and accountVip > dqsj:
                        sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                        new_sqsj = sqsj + timedelta(days=int(sjts))  # 确保使用整数
                    else:
                        new_sqsj = datetime.now() + timedelta(days=int(sjts))  # 确保使用整数
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")

                    # 更新授权时间
                    middleware.bucketSet('dd_yy_auth', account, new_sqsj)

                    # 更新青龙变量
                    phone = account[:3] + '*' * 4 + account[7:]
                    Addenvs(osname=dd_yy_osname, value=token, account=account, phone=phone, target_userid=user)
                    success_count += 1
                except:
                    fail_count += 1

        result_msg = f"""
=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
        sender.reply(result_msg)

    elif xz == '2':
        # 单独授权用户
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

        accountlist = middleware.bucketGet('dd_yy_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"❌ 未找到 {myuid} 的甬派账号信息!")
            return

        accounts = eval(accountlist)
        account_list = """
=======账号列表=====
[0] 授权所有账号
------------------"""

        for i, account in enumerate(accounts, 1):
            accountVip = middleware.bucketGet('dd_yy_auth', account)
            if len(accountVip) == 0:
                vip_status = '⚠️ 未授权'
            elif accountVip < today_time:
                vip_status = '❌ 已过期'
            else:
                vip_status = f'✅ {accountVip}'
            account_list += f"\n[{i}] 账号: {account}\n    授权至: {vip_status}\n------------------"

        account_list += "\n[9999] 授权未授权账号\n------------------"
        account_list += "\n回复数字选择账号\n回复'q'退出\n=================="
        sender.reply(account_list)

        xz = sender.listen(60000)
        if xz == 'q' or xz == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif xz is None:
            sender.reply("⏰ 操作超时,已退出")
            return

        auth_guide = """
=====设置授权天数=====
请输入要授权的天数
------------------
回复数字设置天数
回复"q"退出操作
=================="""

        if xz == '0':
            # 授权该用户的所有账号
            sender.reply(auth_guide)
            sjts = sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return

            try:
                sjts = int(sjts)  # 确保转换为整数
                success_count = 0
                for account in accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('dd_yy_auth', account)
                        token = middleware.bucketGet('dd_yy_token', account)

                        if not token:
                            continue

                        if len(accountVip) != 0 and accountVip > dqsj:
                            sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                            new_sqsj = sqsj + timedelta(days=int(sjts))
                        else:
                            new_sqsj = datetime.now() + timedelta(days=int(sjts))
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")

                        # 更新授权时间
                        middleware.bucketSet('dd_yy_auth', account, new_sqsj)

                        # 更新青龙变量
                        phone = account[:3] + '*' * 4 + account[7:]
                        Addenvs(osname=dd_yy_osname, value=token, account=account, phone=phone, target_userid=myuid)
                        success_count += 1
                    except:
                        continue

                result_msg = f"""
=====授权操作完成=====
✅ 成功授权: {success_count}个账号
⏰ 授权天数: {sjts} 天
=================="""
                sender.reply(result_msg)

            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return

        elif xz == '9999':
            # 授权未授权账号
            # 筛选出未授权的账号
            unauthorized_accounts = []
            for account in accounts:
                accountVip = middleware.bucketGet('dd_yy_auth', account)
                if len(accountVip) == 0 or accountVip <= today_time:
                    unauthorized_accounts.append(account)

            if not unauthorized_accounts:
                sender.reply("""
=====没有未授权账号=====
✅ 该用户所有账号都已授权
==================""")
                return

            # 构建完整的未授权账号列表消息
            unauthorized_list = f"""
=====未授权账号列表=====
📱 找到 {len(unauthorized_accounts)} 个未授权账号
------------------"""

            for i, account in enumerate(unauthorized_accounts, 1):
                unauthorized_list += f"\n[{i}] {account}"

            sender.reply(unauthorized_list)

            sender.reply(auth_guide)
            sjts = sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return

            try:
                sjts = int(sjts)  # 确保转换为整数
                success_count = 0
                for account in unauthorized_accounts:
                    try:
                        token = middleware.bucketGet('dd_yy_token', account)
                        if not token:
                            continue

                        new_sqsj = datetime.now() + timedelta(days=int(sjts))
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")

                        # 更新授权时间
                        middleware.bucketSet('dd_yy_auth', account, new_sqsj)

                        # 更新青龙变量
                        phone = account[:3] + '*' * 4 + account[7:]
                        Addenvs(osname=dd_yy_osname, value=token, account=account, phone=phone, target_userid=myuid)
                        success_count += 1
                    except Exception as e:
                        print(f"处理账号 {account} 时出错: {str(e)}")
                        continue

                result_msg = f"""
=====授权操作完成=====
✅ 成功授权: {success_count}/{len(unauthorized_accounts)}个未授权账号
⏰ 授权天数: {sjts} 天
📅 到期时间: {new_sqsj}
=================="""
                sender.reply(result_msg)

            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return

        elif 1 <= int(xz) <= len(accounts):
            # 授权单个账号
            account = accounts[int(xz) - 1]
            sender.reply(auth_guide)
            sjts = sender.listen(60000)

            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return

            try:
                sjts = int(sjts)  # 确保转换为整数
                dqsj = datetime.now().strftime("%Y-%m-%d")
                accountVip = middleware.bucketGet('dd_yy_auth', account)
                token = middleware.bucketGet('dd_yy_token', account)

                if not token:
                    sender.reply("未找到账号token信息!")
                    return

                if len(accountVip) != 0 and accountVip > dqsj:
                    sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                    new_sqsj = sqsj + timedelta(days=int(sjts))
                else:
                    new_sqsj = datetime.now() + timedelta(days=int(sjts))
                new_sqsj = new_sqsj.strftime("%Y-%m-%d")

                # 更新授权时间
                middleware.bucketSet('dd_yy_auth', account, new_sqsj)

                # 更新青龙变量
                phone = account[:3] + '*' * 4 + account[7:]
                Addenvs(osname=dd_yy_osname, value=token, account=account, phone=phone, target_userid=myuid)

                msg = f"""
=====授权成功=====
📱 账号: {account}
⏰ 授权天数: {sjts}天
📅 到期时间: {new_sqsj}
=================="""
                sender.reply(msg)

            except ValueError:
                sender.reply('❌ 输入的天数无效!')
                return
        else:
            sender.reply("❌ 输入的序号无效!")
            return

    elif xz == '3':
        # 更新青龙变量
        users = middleware.bucketAllKeys('dd_yy_user')
        if not users:
            sender.reply("""
=====更新失败=====
❌ 未找到任何绑定账号
==================""")
            return

        sender.reply("""
=====开始更新=====
⏳ 正在更新面板变量...
==================""")

        success_count = 0
        fail_count = 0

        for user in users:
            accountlist = middleware.bucketGet('dd_yy_user', user)
            if not accountlist or accountlist == '{}':
                continue

            try:
                accounts = eval(accountlist)
                if isinstance(accounts, (list, tuple, set)):
                    accounts = list(dict.fromkeys(accounts))
                else:
                    accounts = [str(accounts)]

                for account in accounts:
                    try:
                        accountVip = middleware.bucketGet('dd_yy_auth', account)
                        token = middleware.bucketGet('dd_yy_token', account)

                        # 只更新已授权且未过期的账号
                        if token and accountVip and accountVip > today_time:
                            phone = account[:3] + '*' * 4 + account[7:]
                            Addenvs(osname=dd_yy_osname, value=token, account=account, phone=phone, target_userid=user)
                            success_count += 1
                        else:
                            fail_count += 1

                    except Exception as e:
                        fail_count += 1
                        continue

            except Exception as e:
                continue

        result_msg = f"""
=====更新完成=====
✅ 成功: {success_count}个账号
❌ 失败: {fail_count}个账号
=================="""
        sender.reply(result_msg)

    else:
        sender.reply("❌ 输入的选项无效!")
        return


def meituanmanage():
    if len(uservalue) != 0:
        try:
            # 解析账号列表
            accounts = []
            try:
                # 如果是字符串形式的列表，先去除首尾的方括号
                cleaned_value = uservalue.strip('[]').strip()
                # 分割并清理每个账号
                if cleaned_value:
                    accounts = [acc.strip().strip("'\"") for acc in cleaned_value.split(',')]
                    accounts = [acc for acc in accounts if acc]  # 移除空值
            except Exception as e:
                print(f"解析账号列表出错: {str(e)}")
                accounts = []

            # 创建一个新的有序账号列表用于显示
            display_accounts = []

            for account in accounts:
                accountVip = middleware.bucketGet('dd_yy_auth', account)
                if len(accountVip) == 0:
                    vip_status = '⚠️ 未授权'
                elif accountVip < today_time:
                    vip_status = '❌ 已过期'
                else:
                    vip_status = f'✅ {accountVip}'

                # 将账号信息添加到显示列表
                display_accounts.append({
                    'account': account,
                    'vip_status': vip_status
                })

            # 按照授权时间排序（未授权的排在最后）
            display_accounts.sort(key=lambda x: (
                '9999-99-99' if len(x.get('vip_status', '')) <= 5  # 未授权或已过期
                else x.get('vip_status', '').split(' ')[-1]  # 获取日期部分
            ), reverse=True)

            # 分页参数
            page_size = 10  # 每页显示的账号数
            total_pages = (len(display_accounts) + page_size - 1) // page_size
            current_page = 1

            while True:
                start_idx = (current_page - 1) * page_size
                end_idx = min(start_idx + page_size, len(display_accounts))
                current_accounts = display_accounts[start_idx:end_idx]

                account_list = f"""
======我的甬派账号=====
📄 第{current_page}/{total_pages}页
[0] 批量授权模式"""

                # 显示当前页的账号列表
                for i, acc_info in enumerate(current_accounts, start_idx + 1):
                    account = acc_info['account']
                    vip_status = acc_info['vip_status']
                    login_mobile = account[:3] + "****" + account[7:]
                    account_list += f"""
------------------
[{i}] 账号信息
📱 账号: {login_mobile}
🔐 授权: {vip_status}"""

                # 添加分页导航选项
                account_list += """
------------------"""
                if total_pages > 1:
                    account_list += """
[n] 下一页
[p] 上一页"""

                account_list += """
[q] 退出操作
------------------
请输入序号选择账号
=================="""

                sender.reply(account_list)

                inputmessage = sender.input(120000, 1, False)
                if inputmessage is None or inputmessage == 'timeout':
                    sender.reply('⏰ 操作超时,已退出')
                    exit(0)
                elif inputmessage.lower() == 'q':
                    sender.reply('✅ 已退出管理')
                    exit(0)
                elif inputmessage.lower() == 'n' and current_page < total_pages:
                    current_page += 1
                    continue
                elif inputmessage.lower() == 'p' and current_page > 1:
                    current_page -= 1
                    continue
                elif inputmessage == '0':
                    # 进入批量授权模式
                    sender.reply("""
=====批量授权模式=====
请输入要授权的账号序号
支持以下格式:
• 单个: 1
• 多个: 1,3,5
• 范围: 1-5
• 混合: 1,3-5,7
------------------
示例: 1-3,5,7-9
回复"q"退出操作
==================""")

                    batch_input = sender.input(120000, 1, False)
                    if batch_input is None or batch_input == 'timeout':
                        sender.reply('⏰ 操作超时,已退出')
                        continue
                    elif batch_input.lower() == 'q':
                        sender.reply('✅ 已退出批量授权')
                        continue

                    try:
                        # 使用新的解析函数处理输入
                        valid_indices, invalid_indices = parse_batch_selection(batch_input, len(display_accounts))

                        # 提示无效的序号
                        if invalid_indices:
                            sender.reply(f'❌ 以下序号无效已忽略: {",".join(map(str, invalid_indices))}')

                        if not valid_indices:
                            sender.reply('❌ 未选择有效的账号序号')
                            continue

                        # 显示选中的账号
                        selected_info = f"""
=====选中账号列表=====
📱 共选择: {len(valid_indices)}个账号
------------------"""
                        for idx in valid_indices:
                            account = display_accounts[idx - 1]['account']
                            login_mobile = account[:3] + "****" + account[7:]
                            selected_info += f"""
[{idx}] {login_mobile}"""

                        selected_info += """
------------------
确认选择请继续
=================="""
                        sender.reply(selected_info)

                        # 批量授权选中的账号
                        auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
                        sender.reply(auth_guide)

                        mes = sender.input(120000, 1, False)
                        if mes is None or mes == 'timeout':
                            sender.reply('⏰ 操作超时,已退出')
                            continue
                        elif mes == 'q' or mes == 'Q':
                            sender.reply('✅ 已退出授权')
                            continue

                        mes = ValueErrors(value=mes, count=999)

                        # 准备批量账号信息
                        batch_accounts = []
                        for idx in valid_indices:
                            account = display_accounts[idx - 1]['account']
                            userurl = middleware.bucketGet(bucket='dd_yy_token', key=f'{account}')
                            accountVip = middleware.bucketGet('dd_yy_auth', account)
                            batch_accounts.append({
                                'account': account,
                                'token': userurl,
                                'accountVip': accountVip,
                                'phone': account[:3] + "****" + account[7:]
                            })

                        # 调用支付函数进行批量支付
                        zf(project='甬派授权', me_as_int=mes, accountVip='', token='', phone='', account='',
                           batch_accounts=batch_accounts)
                        break

                    except ValueError as ve:
                        sender.reply(f'❌ {str(ve)}')
                        continue
                    except Exception as e:
                        sender.reply(f'❌ 处理输入时出错: {str(e)}')
                        continue

                try:
                    # 处理单个账号选择
                    me_as_int = int(inputmessage)
                    if me_as_int <= 0 or me_as_int > len(display_accounts):
                        sender.reply('❌ 输入的序号无效')
                        continue

                    # 使用选择的序号获取账号
                    selected_account = display_accounts[me_as_int - 1]['account']
                    userurl = middleware.bucketGet('dd_yy_token', selected_account)
                    accountVip = middleware.bucketGet('dd_yy_auth', selected_account)

                    if len(accountVip) == 0:
                        vip_status = '⚠️ 未授权'
                    elif accountVip < today_time:
                        vip_status = '❌ 已过期'
                    else:
                        vip_status = f'✅ {accountVip}'

                    login_mobile = selected_account[:3] + "****" + selected_account[7:]

                    combined_menu = f"""
=====账号详情=====
📱 账号: {login_mobile}
🔐 授权: {vip_status}
------------------
[1] 授权账号
[2] 删除账号
------------------
回复数字选择功能
回复"q"退出操作
=================="""
                    sender.reply(combined_menu)

                    inputmessage = sender.input(120000, 1, False)
                    if inputmessage is None or inputmessage == 'timeout':
                        sender.reply('⏰ 操作超时,已退出')
                        exit(0)
                    elif inputmessage == 'q' or inputmessage == 'Q':
                        sender.reply('✅ 已退出管理')
                        exit(0)
                    elif inputmessage == '2':
                        confirm_msg = """
=====警告=====
确定要删除该账号吗？
此操作不可恢复！
------------------
[y] 确认删除
[n] 取消操作
=================="""
                        sender.reply(confirm_msg)

                        yesorno = sender.input(120000, 1, False)
                        if yesorno is None or yesorno == 'timeout':
                            sender.reply('⏰ 操作超时,已退出')
                            exit(0)
                        elif yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
                            accounts.remove(str(selected_account))
                            qlid = allenvs(osname=dd_yy_osname, account=str(selected_account))
                            delenvs(id=qlid)
                            if len(accounts) == 0:
                                middleware.bucketDel(bucket='dd_yy_user', key=userid)
                            else:
                                middleware.bucketSet(bucket='dd_yy_user', key=userid, value=f'{accounts}')
                            sender.reply('✅ 账号删除成功!')
                            break
                        elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
                            sender.reply('✅ 已取消删除')
                            break
                    elif inputmessage == '1':
                        auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
                        sender.reply(auth_guide)

                        mes = sender.input(120000, 1, False)
                        if mes is None or mes == 'timeout':
                            sender.reply('⏰ 操作超时,已退出')
                            exit(0)
                        elif mes == 'q' or mes == 'Q':
                            sender.reply('✅ 已退出管理')
                            exit(0)
                        mes = ValueErrors(value=mes, count=999)
                        zf(project='甬派授权', me_as_int=mes, accountVip=accountVip, token=userurl,
                           phone=selected_account, account=selected_account)
                        break

                except ValueError:
                    sender.reply('❌ 输入必须是数字')
                    continue

            return

        except Exception as e:
            sender.reply(f"""
=====账号处理错误=====
❌ 账号列表处理失败
⚠️ 错误: {str(e)}
==================""")
            return
    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
==================""")


def generate_qrcode(url):
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception as e:
        print(f"生成二维码失败: {str(e)}")
        return None


def get_payment_config():
    zsm = middleware.bucketGet('dd_yy', 'zsm')
    ma_pay_local = middleware.bucketGet('dd_yy', 'use_ma_pay') or 'false'
    ma_pay_local = ma_pay_local.lower() == 'true'
    ma_pay_config = None

    if ma_pay_local:
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
            ma_pay_local = False
            ma_pay_config = None

    return zsm, ma_pay_local, ma_pay_config


def zf(project, me_as_int, accountVip, token, phone, account, batch_accounts=None):
    """支付功能,支持单个和批量账号支付"""
    try:
        zsm, use_ma_pay_local, ma_pay_config = get_payment_config()
        if not zsm and not use_ma_pay_local:
            sender.reply('❌ 未配置收款方式，请联系管理员')
            exit(0)

        # 计算总金额和所需积分
        accounts_count = len(batch_accounts) if batch_accounts else 1
        total_money = Decimal(me_as_int) * Decimal(yyVipmoney) * accounts_count
        total_coins = int(yycoin) * me_as_int * accounts_count

        # 免费授权
        if total_money == 0:
            success_count = 0
            accounts_to_process = batch_accounts if batch_accounts else [
                {'account': account, 'token': token, 'accountVip': accountVip, 'phone': phone}]
            for acc in accounts_to_process:
                try:
                    new_auth_time = empower(empowertime=acc['accountVip'], me_as_int=me_as_int)
                    middleware.bucketSet('dd_yy_auth', acc['account'], new_auth_time)
                    stored_info = middleware.bucketGet('dd_yy_token', acc['account'])
                    if stored_info:
                        Addenvs(osname=dd_yy_osname, value=stored_info, account=acc['account'],
                                phone=acc['phone'])
                        success_count += 1
                except Exception as e:
                    print(f"处理账号 {acc['account']} 时出错: {str(e)}")
                    continue
            sender.reply(f"""
=====免费授权成功=====
🎫 商品: {project}
💰 金额: 免费
✅ 成功: {success_count}/{len(accounts_to_process)}个账号
⏰ 授权时长: {me_as_int}月/每个
==================""")
            return True

        # 检查是否允许使用积分支付
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'

        # 构建动态支付选择菜单
        pay_menu = f"""
=====选择支付方式====
📱 账号数量: {accounts_count}个
⏰ 授权时长: {me_as_int}月"""

        option_num = 1
        options_map = {}

        if zsm and not use_ma_pay_local:
            pay_menu += f"""
{option_num}️⃣ 微信支付
   💰 {total_money}元"""
            options_map[str(option_num)] = 'wechat'
            option_num += 1

        if use_ma_pay_local:
            pay_menu += f"""
{option_num}️⃣ 码支付
   💰 {total_money}元"""
            options_map[str(option_num)] = 'ma'
            option_num += 1

        if yycoin and int(yycoin) > 0:
            pay_menu += f"""
{option_num}️⃣ 积分支付
   🎯 {total_coins}积分
   💫 当前积分: {usercoin}"""
            options_map[str(option_num)] = 'points'

        pay_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""

        sender.reply(pay_menu)
        choice = sender.input(60000, 1, False)

        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消支付")
            exit(0)

        selected_pay = options_map.get(choice)

        if selected_pay == 'wechat' and zsm:
            # 微信支付流程
            zfzt = sender.atWaitPay()
            if zfzt:
                sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
                exit(0)

            pay_msg = f"""
=====微信扫码支付====
🎫 商品: {project}
📱 数量: {accounts_count}个账号
📅 时长: {me_as_int}月/每个
💰 金额: {total_money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
            sender.reply(pay_msg)
            sender.replyImage(zsm)

            ddzf = sender.waitPay("q", 100 * 1000)

            if str(ddzf) == 'q':
                sender.reply('✅ 已取消支付')
                exit(0)

            try:
                if isinstance(ddzf, dict):
                    if ddzf.get('type') == '微信赞赏':
                        Money = float(ddzf.get('money', 0))
                        Time = ddzf.get('time', '')
                        From = ddzf.get('from_name', '')
                    elif ddzf.get('type') == '微信收款':
                        Money = float(ddzf.get('money', 0))
                        Time = ddzf.get('time', '')
                        From = ddzf.get('from_name', '')
                    else:
                        Money = float(ddzf.get('Money', 0))
                        Time = ddzf.get('Time', '')
                        From = ''
                else:
                    try:
                        ddzf = json.loads(ddzf)
                        if ddzf.get('type') == '微信赞赏':
                            Money = float(ddzf.get('money', 0))
                            Time = ddzf.get('time', '')
                            From = ddzf.get('from_name', '')
                        elif ddzf.get('type') == '微信收款':
                            Money = float(ddzf.get('money', 0))
                            Time = ddzf.get('time', '')
                            From = ddzf.get('from_name', '')
                        else:
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '')
                            From = ''
                    except:
                        if "二维码赞赏到账" in str(ddzf):
                            try:
                                amount = str(ddzf).split("收款金额￥")[1].split("\n")[0]
                                time = str(ddzf).split("到账时间")[1].split("\n")[0]
                                Money = float(amount)
                                Time = time.strip()
                                From = ''
                            except Exception as e:
                                sender.reply(f"❌ 解析收款信息失败: {str(e)}")
                                exit(0)
                        else:
                            sender.reply("❌ 无法解析支付结果")
                            exit(0)

                if float(Money) >= float(total_money):
                    success_count = 0
                    accounts_to_process = batch_accounts if batch_accounts else [
                        {'account': account, 'token': token, 'accountVip': accountVip, 'phone': phone}]

                    for acc in accounts_to_process:
                        try:
                            new_auth_time = empower(empowertime=acc['accountVip'], me_as_int=me_as_int)
                            middleware.bucketSet('dd_yy_auth', acc['account'], new_auth_time)

                            stored_info = middleware.bucketGet('dd_yy_token', acc['account'])
                            if stored_info:
                                Addenvs(osname=dd_yy_osname, value=stored_info, account=acc['account'],
                                        phone=acc['phone'])
                                success_count += 1

                        except Exception as e:
                            print(f"处理账号 {acc['account']} 时出错: {str(e)}")
                            continue

                    result_msg = f"""
=====支付成功=====
🎫 商品: {project}
💰 金额: {Money}元
⏰ 时间: {Time}
✅ 成功: {success_count}/{len(accounts_to_process)}个账号
=================="""
                    sender.reply(result_msg)
                    return True

                else:
                    sender.reply(f"""
=====支付金额错误=====
💰 应付: {total_money}元
💳 实付: {Money}元
❗ 请联系管理员处理退款！
==================""")
                    exit(0)

            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                exit(0)

        elif selected_pay == 'ma' and use_ma_pay_local:
            # 码支付流程
            out_trade_no = f"YY{int(time.time())}{userid}"
            params = {
                'pid': ma_pay_config['pid'],
                'type': ma_pay_config['type'].split(',')[0],
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-甬派授权-{str(total_money)}",
                'money': str(total_money),
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
                    sender.reply(f"""
=====支付失败=====
❌ 创建支付订单失败
HTTP状态码: {response.status_code}
==================""")
                    exit(0)

                try:
                    result = response.json()
                except:
                    sender.reply("""
=====支付失败=====
❌ 创建支付订单失败
返回数据格式错误
==================""")
                    exit(0)

                code = result.get('code', 0)
                msg = result.get('msg', '未知状态')

                if code == 1:
                    payurl = result.get('payurl', '')
                    if not payurl:
                        sender.reply("""
=====支付失败=====
❌ 未获取到支付链接
==================""")
                        exit(0)

                    qrcode_url = generate_qrcode(payurl)
                    if qrcode_url:
                        sender.replyImage(qrcode_url)
                    else:
                        sender.reply(f"""=====码支付=====
🎫 商品: {project}
💰 金额: {total_money}元
⏰ 有效期: 5分钟
------------------
二维码生成失败，请点击链接完成支付:
{payurl}
==================""")
                else:
                    sender.reply(f"""
=====支付失败=====
❌ 创建订单失败: {msg}
==================""")
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
                            success_count = 0
                            accounts_to_process = batch_accounts if batch_accounts else [
                                {'account': account, 'token': token, 'accountVip': accountVip, 'phone': phone}]

                            for acc in accounts_to_process:
                                try:
                                    new_auth_time = empower(empowertime=acc['accountVip'], me_as_int=me_as_int)
                                    middleware.bucketSet('dd_yy_auth', acc['account'], new_auth_time)

                                    stored_info = middleware.bucketGet('dd_yy_token', acc['account'])
                                    if stored_info:
                                        Addenvs(osname=dd_yy_osname, value=stored_info, account=acc['account'],
                                                phone=acc['phone'])
                                        success_count += 1
                                except Exception as e:
                                    print(f"处理账号 {acc['account']} 时出错: {str(e)}")
                                    continue

                            sender.reply(f"""
=====支付成功=====
🎫 商品: {project}
💰 金额: {total_money}元
✅ 成功: {success_count}/{len(accounts_to_process)}个账号
⏰ 授权时长: {me_as_int}月/每个
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
            except SystemExit:
                raise
            except Exception as e:
                sender.reply(f"❌ 支付请求失败: {str(e)}")
                exit(0)

        elif selected_pay == 'points' and yycoin and int(yycoin) > 0:
            # 积分支付流程
            if int(usercoin) < total_coins:
                sender.reply(f"""
=====积分不足=====
👤 当前积分: {usercoin}
📍 需要积分: {total_coins}
==================""")
                exit(0)

            confirm_msg = f"""
=====积分支付确认=====
📱 账号数量: {accounts_count}个
💫 消耗积分: {total_coins}
⏰ 授权时长: {me_as_int}月/每个
------------------
确认请回复【y】
取消请回复【n】
=================="""
            sender.reply(confirm_msg)

            if yesornos():
                try:
                    new_balance = int(usercoin) - total_coins
                    middleware.bucketSet('dd_sign_points', userid, str(new_balance))

                    success_count = 0
                    accounts_to_process = batch_accounts if batch_accounts else [
                        {'account': account, 'token': token, 'accountVip': accountVip, 'phone': phone}]

                    for acc in accounts_to_process:
                        try:
                            new_auth_time = empower(empowertime=acc['accountVip'], me_as_int=me_as_int)
                            middleware.bucketSet('dd_yy_auth', acc['account'], new_auth_time)

                            stored_info = middleware.bucketGet('dd_yy_token', acc['account'])
                            if stored_info:
                                Addenvs(osname=dd_yy_osname, value=stored_info, account=acc['account'],
                                        phone=acc['phone'])
                                success_count += 1

                        except Exception as e:
                            print(f"处理账号 {acc['account']} 时出错: {str(e)}")
                            continue

                    result_msg = f"""
=====支付成功=====
💫 扣除积分: {total_coins}
💰 剩余积分: {new_balance}
✅ 成功: {success_count}/{len(accounts_to_process)}个账号
⏰ 授权时长: {me_as_int}月/每个
=================="""
                    sender.reply(result_msg)
                    return True

                except Exception as e:
                    sender.reply(f"❌ 积分支付处理失败: {str(e)}")
                    exit(0)
            else:
                sender.reply("✅ 已取消支付")
                exit(0)
        else:
            sender.reply("❌ 输入无效")
            exit(0)

    except Exception as e:
        sender.reply(f"❌ 支付处理发生错误: {str(e)}")
        exit(0)


def cx(token, use_proxy=False):
    """查询用户信息和中奖记录"""
    try:
        # 解析token获取账号密码
        account_info = token.split('#')
        if len(account_info) < 2:
            return "未知", "未知", []

        phone = account_info[0]
        password = account_info[1]

        # 初始化session（默认不使用代理，提高查询速度）
        session = requests.session()
        proxies = None
        if use_proxy and proxy_url:
            proxies = update_proxy(session, proxy_url)

        ua = generate_random_ua() + ' agentweb/4.0.2 UCBrowser/11.6.4.950 yongpai'
        session.headers.update({
            'Host': 'ypapp.cnnb.com.cn',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': ua,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })

        # 登录获取新token
        ts = str(int(time.time() * 1000))
        deviceId = str(uuid.uuid4())
        sign = hashlib.md5(f'globalDatetime{ts}username{phone}test_123456679890123456'.encode()).hexdigest()
        url = f'https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3?username={phone}&password={password}&deviceId={deviceId}&globalDatetime={ts}&sign={sign}'

        response = session.get(url, proxies=proxies, timeout=5)
        result = response.json()

        if result.get("code") != 0:
            return "未知", "未知", []

        nickname = result.get("data", {}).get("nickname", "未知")
        mobile = result.get("data", {}).get("mobile", "未知")
        userId = result.get("data", {}).get("userId")
        new_token = result.get("data", {}).get("token")

        # 查询中奖记录（通过tmlyun抽奖系统）
        prizes = []
        try:
            lottery_login_body = {
                "accountId": str(userId),
                "sessionId": new_token,
                "q": LOTTERY_Q,
                "tenantCode": LOTTERY_TENANT_CODE,
            }
            lottery_headers = {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "user-agent": ua,
                "X-REQUEST-ID": f"{random.randint(1000,9999)}.{uuid.uuid4().hex[:12]}|{int(time.time() * 1000)}"
            }
            lottery_resp = requests.post(
                "https://act.tmlyun.com/activity-api/lottery/api/auth/userLogin",
                headers=lottery_headers,
                json=lottery_login_body,
                proxies=proxies,
                timeout=10
            )
            lottery_data = lottery_resp.json().get("data") or {}
            lottery_token = lottery_data.get("token")
            x_token = lottery_data.get("xToken") or lottery_data.get("x_token")

            if lottery_token:
                record_headers = {
                    "accept": "application/json, text/plain, */*",
                    "authorization": lottery_token,
                    "user-agent": ua,
                    "X-REQUEST-ID": f"{random.randint(1000,9999)}.{uuid.uuid4().hex[:12]}|{int(time.time() * 1000)}"
                }
                if x_token:
                    record_headers["X-TOKEN"] = x_token

                record_resp = requests.get(
                    f"https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/accountPrizeRecord/userPrizeRecord?activityId={LOTTERY_ACTIVITY_ID}",
                    headers=record_headers,
                    proxies=proxies,
                    timeout=10
                )
                record_result = record_resp.json()

                if record_result.get("code") == 0 or record_result.get("success") is True:
                    prize_list = record_result.get("data", {}).get("activityAccountPrizeVoList", [])
                    for prize in prize_list:
                        prizes.append({
                            'type': prize.get('grade', '未知类型'),
                            'title': prize.get('prizeName', '未知奖品'),
                            'time': prize.get('createTime', '')
                        })
        except Exception as prize_error:
            print(f"[警告] 查询中奖记录失败: {str(prize_error)}")
            pass

        return nickname, mobile, prizes

    except Exception as e:
        print(f"查询异常: {str(e)}")
        return "未知", "未知", []


def calculate_today_income(prizes):
    """计算今日收益"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        today_income = 0.0

        for prize in prizes:
            prize_time = prize.get('time', '')
            # 检查是否是今日的记录
            if prize_time.startswith(today):
                # 提取金额
                amount = re.search(r'(\d+\.?\d*)元', prize['title'])
                if amount:
                    today_income += float(amount.group(1))

        return today_income
    except Exception as e:
        print(f"计算今日收益出错: {str(e)}")
        return 0.0


def cxs():
    if len(uservalue) != 0:
        # 解析账号列表
        accounts = []
        try:
            # 如果是字符串形式的列表，先去除首尾的方括号
            cleaned_value = uservalue.strip('[]').strip()
            # 分割并清理每个账号
            if cleaned_value:
                accounts = [acc.strip().strip("'\"") for acc in cleaned_value.split(',')]
                accounts = [acc for acc in accounts if acc]  # 移除空值
        except Exception as e:
            print(f"解析账号列表出错: {str(e)}")
            accounts = []

        if not accounts:
            sender.reply(f"""
=====未绑定账号=====
❌ 账号信息异常
💡 发送 {randomsigncommand} 重新绑定
==================""")
            return

        # 构建账号选择菜单
        account_menu = """
=====甬派查询=====
[0] 查询全部账号
[9999] 查询全部账号今日收益
------------------"""

        # 显示账号列表
        for i, account in enumerate(accounts, 1):
            accountVip = middleware.bucketGet('dd_yy_auth', account)
            login_mobile = account[:3] + "****" + account[7:]

            if len(accountVip) == 0:
                auth_status = "⚠️ 未授权"
            elif accountVip <= today_time:
                auth_status = "❌ 已过期"
            else:
                auth_status = "✅ 已授权"

            account_menu += f"""
[{i}] 账号: {login_mobile}
    授权: {auth_status}
------------------"""

        account_menu += """
回复数字选择查询方式
回复"q"退出操作
=================="""

        sender.reply(account_menu)

        # 获取用户选择
        choice = sender.input(120000, 1, False)
        if choice is None or choice == 'timeout':
            sender.reply('⏰ 操作超时,已退出')
            return
        elif choice.lower() == 'q':
            sender.reply('✅ 已退出查询')
            return

        try:
            if choice == '0':
                # 查询全部账号
                sender.reply('⏳ 正在查询全部账号,请稍候...')

                for i, account in enumerate(accounts, 1):
                    userToken = middleware.bucketGet(bucket='dd_yy_token', key=f'{account}')
                    accountVip = middleware.bucketGet('dd_yy_auth', account)
                    login_mobile = account[:3] + "****" + account[7:]

                    if len(accountVip) == 0:
                        auth_status = "⚠️ 未授权"
                        auth_time = "无"
                    elif accountVip <= today_time:
                        auth_status = "❌ 已过期"
                        auth_time = accountVip
                    else:
                        auth_status = "✅ 已授权"
                        auth_time = accountVip

                    if len(accountVip) != 0 and accountVip > today_time:
                        try:
                            nickname, mobile, prizes = cx(userToken)

                            # 计算成功领取的数量和总金额
                            success_count = 0
                            total_income = 0.0

                            for prize in prizes:
                                amount = re.search(r'(\d+\.?\d*)元', prize['title'])
                                if amount:
                                    success_count += 1
                                    total_income += float(amount.group(1))

                            # 构建基本账号信息
                            account_info = f"""
=====账号详情[{i}]=====
📱 账号: {login_mobile}
👤 昵称: {nickname}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
💰 成功领取: {success_count}笔, 总计: {total_income:.2f}元"""

                            # 添加转盘抽奖记录
                            if prizes:
                                account_info += "\n===== 🎁转盘抽奖🎁 ====="
                                # 按时间排序，最新的在前面
                                sorted_prizes = sorted(prizes, key=lambda x: x['time'], reverse=True)[:prize_show_count]
                                for prize in sorted_prizes:
                                    amount = re.search(r'(\d+\.?\d*)元', prize['title'])
                                    if amount:
                                        amount = f"现金{amount.group(1)}元"
                                    else:
                                        amount = prize['title']
                                    account_info += f"\n{amount}-{prize['time']}"
                            else:
                                account_info += "\n暂无中奖记录"

                            account_info += "\n=================="""
                            sender.reply(account_info)

                        except Exception as e:
                            sender.reply(f"""
=====甬派查询异常[{i}]=====
📱 账号: {login_mobile}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
❌ 状态: 查询失败
==================""")
                            continue
                    else:
                        sender.reply(f"""
=====甬派授权过期[{i}]=====
📱 账号: {login_mobile}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
==================""")

            elif choice == '9999':
                # 查询全部账号今日收益（优化版本）
                sender.reply('⏳ 正在查询今日收益,请稍候...')

                # 使用优化后的并发查询
                results = cx_batch_today_income(accounts)

                income_summary = f"""
=====今日收益汇总=====
📅 查询日期: {datetime.now().strftime("%Y-%m-%d")}
------------------"""

                total_today_income = 0.0
                valid_count = 0
                error_count = 0
                unauthorized_count = 0

                for i, account in enumerate(accounts, 1):
                    result = results.get(account, {})
                    status = result.get('status', 'unknown')
                    income = result.get('income', 0.0)
                    mobile = result.get('mobile', account[:3] + "****" + account[7:])

                    if status == 'success':
                        income_summary += f"""
[{i}]-{mobile}-今日收益:{income:.2f}元"""
                        total_today_income += income
                        valid_count += 1
                    elif status == 'unauthorized':
                        income_summary += f"""
[{i}]-{mobile}-今日收益:账号未授权"""
                        unauthorized_count += 1
                    else:
                        income_summary += f"""
[{i}]-{mobile}-今日收益:查询失败"""
                        error_count += 1

                income_summary += f"""
------------------
💰 总计收益: {total_today_income:.2f}元
📊 有效账号: {valid_count}/{len(accounts)}个
=================="""

                sender.reply(income_summary)

            else:
                # 查询单个账号
                choice_num = int(choice)
                if choice_num < 1 or choice_num > len(accounts):
                    sender.reply('❌ 输入的序号无效')
                    return

                account = accounts[choice_num - 1]
                userToken = middleware.bucketGet(bucket='dd_yy_token', key=f'{account}')
                accountVip = middleware.bucketGet('dd_yy_auth', account)
                login_mobile = account[:3] + "****" + account[7:]

                if len(accountVip) == 0:
                    auth_status = "⚠️ 未授权"
                    auth_time = "无"
                elif accountVip <= today_time:
                    auth_status = "❌ 已过期"
                    auth_time = accountVip
                else:
                    auth_status = "✅ 已授权"
                    auth_time = accountVip

                if len(accountVip) != 0 and accountVip > today_time:
                    try:
                        nickname, mobile, prizes = cx(userToken)

                        # 计算成功领取的数量和总金额
                        success_count = 0
                        total_income = 0.0
                        today_income = calculate_today_income(prizes)

                        for prize in prizes:
                            amount = re.search(r'(\d+\.?\d*)元', prize['title'])
                            if amount:
                                success_count += 1
                                total_income += float(amount.group(1))

                        # 构建基本账号信息
                        account_info = f"""
=====账号详情[{choice_num}]=====
📱 账号: {login_mobile}
👤 昵称: {nickname}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
💰 总计收益: {total_income:.2f}元({success_count}笔)
💵 今日收益: {today_income:.2f}元"""

                        # 添加转盘抽奖记录
                        if prizes:
                            account_info += "\n===== 🎁转盘抽奖🎁 ====="
                            # 按时间排序，最新的在前面
                            sorted_prizes = sorted(prizes, key=lambda x: x['time'], reverse=True)[:prize_show_count]
                            for prize in sorted_prizes:
                                amount = re.search(r'(\d+\.?\d*)元', prize['title'])
                                if amount:
                                    amount = f"现金{amount.group(1)}元"
                                else:
                                    amount = prize['title']
                                account_info += f"\n{amount}-{prize['time']}"
                        else:
                            account_info += "\n暂无中奖记录"

                        account_info += "\n=================="""
                        sender.reply(account_info)

                    except Exception as e:
                        sender.reply(f"""
=====甬派查询异常=====
📱 账号: {login_mobile}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
❌ 状态: 查询失败
⚠️ 错误: {str(e)}
==================""")
                else:
                    sender.reply(f"""
=====甬派授权过期=====
📱 账号: {login_mobile}
🔐 授权状态: {auth_status}
📅 到期时间: {auth_time}
💡 请及时续费授权
==================""")

        except ValueError:
            sender.reply('❌ 输入必须是数字')
            return
        except Exception as e:
            sender.reply(f'❌ 查询过程中出错: {str(e)}')
            return

    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
==================""")


def push(user, account, c):
    login_mobile = account[:3] + "****" + account[7:]

    push_msg = f"""
=====甬派账号通知=====
📱 账号: {login_mobile}
📢 消息: {c}
=================="""

    middleware.push('wb', '', user, '', push_msg)
    middleware.push('tg', '', user, '', push_msg)
    middleware.push('qq', '', user, '', push_msg)
    middleware.push('qb', '', user, '', push_msg)
    middleware.push('wx', '', user, '', push_msg)


def clean_expired_accounts():
    """清理过期的甬派账号"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作")
        exit(0)

    users = middleware.bucketAllKeys(bucket='dd_yy_user')
    if not users:
        sender.reply("❌ 未找到任何绑定账号")
        exit(0)

    sender.reply(f"""
=====开始清理=====
📊 共找到: {len(users)}个用户
⏳ 清理中请稍候...
==================""")

    cleaned_accounts = 0
    cleaned_vars = 0
    cleaned_users = 0

    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_yy_user', key=user)
            if not accountlist:
                continue

            accounts = eval(accountlist)
            if isinstance(accounts, (list, tuple, set)):
                accounts = list(dict.fromkeys(accounts))
            else:
                accounts = [str(accounts)]

            valid_accounts = []

            for account in accounts:
                accountVip = middleware.bucketGet('dd_yy_auth', account)

                if len(accountVip) == 0 or accountVip <= today_time:
                    try:
                        qlid = allenvs(osname=dd_yy_osname, account=account)
                        if qlid:
                            delenvs(id=qlid)
                            cleaned_vars += 1
                        middleware.bucketDel(bucket='dd_yy_token', key=account)
                        middleware.bucketDel(bucket='dd_yy_auth', key=account)
                        cleaned_accounts += 1
                    except Exception as e:
                        print(f"处理账号 {account} 时出错: {str(e)}")
                        continue
                else:
                    valid_accounts.append(account)

            if valid_accounts:
                middleware.bucketSet(bucket='dd_yy_user', key=user, value=str(valid_accounts))
            else:
                middleware.bucketDel(bucket='dd_yy_user', key=user)
                cleaned_users += 1

        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue

    sender.reply(f"""
=====清理完成=====
✅ 已清理:
• {cleaned_accounts}个过期账号
• {cleaned_vars}个面板变量
• {cleaned_users}个空用户记录
==================""")


def show_tutorial():
    """显示甬派插件使用教程"""
    tutorial = """
=====甬派插件教程=====
🔰 基础功能指令:
------------------
1️⃣ 甬派登录
• 输入格式: 手机号#密码#zfb账号(可用邮箱)#zfb姓名
• 示例: 13812345678#123456#13888888888#张三
• zfb信息用于自动提现

2️⃣ 甬派查询
• 查看账号信息
• 查看中奖信息

3️⃣ 甬派管理
• 管理已绑定账号
• 授权账号/删除账号
• 支持积分/微信支付

🔧 管理员功能:
------------------
• 甬派后台: 后台管理
• 甬派清理: 清理过期账号

⚠️ 注意事项:
------------------
1. 首次使用请先登录绑定
2. 定期查看账号状态
3. 及时处理授权到期
4. 请确保zfb信息准确
=================="""
    sender.reply(tutorial)


def cx_today_income_fast(token, use_proxy=False):
    """快速查询今日收益（只查询最近记录）"""
    try:
        # 解析token获取账号密码
        account_info = token.split('#')
        if len(account_info) < 2:
            return 0.0, "未知"

        phone = account_info[0]
        password = account_info[1]

        # 初始化session（默认不使用代理，提高查询速度）
        session = requests.session()
        proxies = None
        if use_proxy and proxy_url:
            proxies = update_proxy(session, proxy_url)

        ua = generate_random_ua() + ' agentweb/4.0.2 UCBrowser/11.6.4.950 yongpai'
        session.headers.update({
            'Host': 'ypapp.cnnb.com.cn',
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': ua,
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        })

        # 登录获取新token
        ts = str(int(time.time() * 1000))
        deviceId = str(uuid.uuid4())
        sign = hashlib.md5(f'globalDatetime{ts}username{phone}test_123456679890123456'.encode()).hexdigest()
        url = f'https://ypapp.cnnb.com.cn/yongpai-user/api/login2/local3?username={phone}&password={password}&deviceId={deviceId}&globalDatetime={ts}&sign={sign}'

        response = session.get(url, proxies=proxies, timeout=5)
        result = response.json()

        if result.get("code") != 0:
            return 0.0, "登录失败"

        nickname = result.get("data", {}).get("nickname", "未知")
        userId = result.get("data", {}).get("userId")

        # 查询中奖记录（通过tmlyun抽奖系统）
        today_income = 0.0
        try:
            lottery_login_body = {
                "accountId": str(userId),
                "sessionId": result.get("data", {}).get("token", ""),
                "q": LOTTERY_Q,
                "tenantCode": LOTTERY_TENANT_CODE,
            }
            lottery_headers = {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "user-agent": ua,
                "X-REQUEST-ID": f"{random.randint(1000,9999)}.{uuid.uuid4().hex[:12]}|{int(time.time() * 1000)}"
            }
            lottery_resp = requests.post(
                "https://act.tmlyun.com/activity-api/lottery/api/auth/userLogin",
                headers=lottery_headers,
                json=lottery_login_body,
                proxies=proxies,
                timeout=10
            )
            lottery_data = lottery_resp.json().get("data") or {}
            lottery_token = lottery_data.get("token")
            x_token = lottery_data.get("xToken") or lottery_data.get("x_token")

            if lottery_token:
                record_headers = {
                    "accept": "application/json, text/plain, */*",
                    "authorization": lottery_token,
                    "user-agent": ua,
                    "X-REQUEST-ID": f"{random.randint(1000,9999)}.{uuid.uuid4().hex[:12]}|{int(time.time() * 1000)}"
                }
                if x_token:
                    record_headers["X-TOKEN"] = x_token

                record_resp = requests.get(
                    f"https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/accountPrizeRecord/userPrizeRecord?activityId={LOTTERY_ACTIVITY_ID}",
                    headers=record_headers,
                    proxies=proxies,
                    timeout=10
                )
                record_result = record_resp.json()

                if record_result.get("code") == 0 or record_result.get("success") is True:
                    today = datetime.now().strftime("%Y-%m-%d")
                    prize_list = record_result.get("data", {}).get("activityAccountPrizeVoList", [])
                    for prize in prize_list:
                        prize_time = prize.get('createTime', '')
                        if prize_time.startswith(today):
                            prize_name = prize.get('prizeName', '')
                            amount = re.search(r'(\d+\.?\d*)元', prize_name)
                            if amount:
                                today_income += float(amount.group(1))
        except Exception as prize_error:
            print(f"[警告] 查询今日收益失败: {str(prize_error)}，昵称: {nickname}")
            pass

        return today_income, nickname

    except Exception as e:
        print(f"快速查询今日收益异常: {str(e)}")
        return 0.0, "查询失败"


def cx_batch_today_income(accounts):
    """批量查询今日收益（支持并发）"""
    results = {}

    def query_single_account(account):
        try:
            userToken = middleware.bucketGet(bucket='dd_yy_token', key=f'{account}')
            accountVip = middleware.bucketGet('dd_yy_auth', account)
            login_mobile = account[:3] + "****" + account[7:]

            if len(accountVip) != 0 and accountVip > today_time:
                today_income, nickname = cx_today_income_fast(userToken)
                return account, {
                    'status': 'success',
                    'income': today_income,
                    'nickname': nickname,
                    'mobile': login_mobile
                }
            else:
                return account, {
                    'status': 'unauthorized',
                    'income': 0.0,
                    'nickname': '未授权',
                    'mobile': login_mobile
                }
        except Exception as e:
            return account, {
                'status': 'error',
                'income': 0.0,
                'nickname': '查询失败',
                'mobile': login_mobile,
                'error': str(e)
            }

    # 使用线程池并发查询（最多5个并发，避免请求过于频繁）
    with ThreadPoolExecutor(max_workers=min(5, len(accounts))) as executor:
        future_to_account = {executor.submit(query_single_account, account): account for account in accounts}

        for future in as_completed(future_to_account):
            account, result = future.result()
            results[account] = result

    return results


# 主程序入口
dd_yy_osname, dd_yy_qlname, dd_managecommand, dd_querycommand, dd_signcommand, \
    randommanagecommand, randomquerycommand, randomsigncommand, yyVipmoney, yycoin, proxy_url, \
    use_ma_pay, use_daidai, dd_yy_ddname, panel_group, prize_show_count = getusercontent()
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
elif usermessage == '甬派后台管理':
    sf_auth()
elif usermessage == '甬派清理':
    clean_expired_accounts()
elif usermessage == '甬派教程':
    show_tutorial()
elif '管理' in usermessage:
    if len(uservalue) != 0:
        meituanmanage()
    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
==================""")
elif '查询' in usermessage:
    if len(uservalue) != 0:
        cxs()
    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
==================""")
elif imtype == 'fake':
    users = middleware.bucketAllKeys(bucket='dd_yy_user')  
    for user in users:
        accountlist = middleware.bucketGet(bucket='dd_yy_user', key=f'{user}')
        accounts = eval(accountlist)
        for account in accounts:
            token = middleware.bucketGet(bucket='dd_yy_token', key=f'{account}')
            accountVip = middleware.bucketGet('dd_yy_auth', account)

            # 只检查授权状态
            if len(accountVip) != 0 and accountVip > today_time:
                continue
            else:
                qlid = allenvs(osname=dd_yy_osname, account=account)
                delenvs(id=qlid)
                push(user=user, account=account, c="""
⚠️ 授权已过期
------------------
❌ 授权状态失效
💡 请及时续费授权""")
else:
    sender.setContinue()
