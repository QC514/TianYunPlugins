# [rule: ^快手登录$|^快手登陆$|^快手查询$|^快手管理$|^快手教程$|^快手后台$|^快手分成$|^快手提现$]
# [cron: 0 0 8,10,22 * * *]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [public: true]
# [title: 小快手]
# [icon: http://5b0988e595225.cdn.sohucs.com/images/20190724/f8f8ace898584a2dbd3f20c2d2822c96.jpeg]
# [open_source: false]
# [class: 工具类]
# [version: 5.2.5]
# [price: 18.88]
# [admin: false]
# [author: linzixuan]
# [service: 2661320550]
# [description: 小快手V5.0全新重构<br>✨ 支持极速版和普通版独立管理<br>🔐 支持月付授权和分成模式<br>📊 完善的后台管理和数据统计<br>🌐 支持代理IP配置<br>💰 集成码支付和微信支付<br>格式：备注#Cookie#Salt#代理信息]

import re
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal, ROUND_HALF_UP
import requests
import time
import json
import hashlib

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_ks_user', key=userid)

# 配置参数
# [param: {"required":true,"key":"dd_ks.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_ks.dd_ks_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割"}]
# [param: {"required":true,"key":"dd_ks.ks_fast_varname","bool":false,"placeholder":"必填项,例:ksToken_fast","name":"极速版变量名称","desc":"青龙容器内快手极速版的变量名"}]
# [param: {"required":true,"key":"dd_ks.ks_normal_varname","bool":false,"placeholder":"必填项,例:ksToken","name":"普通版变量名称","desc":"青龙容器内快手普通版的变量名"}]
# [param: {"required":false,"key":"dd_ks.allow_proxy","bool":true,"placeholder":"","name":"是否允许填写代理","desc":"是否允许用户在提交时填写代理IP"}]
# [param: {"required":true,"key":"dd_ks.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# [param: {"required":true,"key":"dd_ks.payment_mode","bool":false,"placeholder":"月付/天付/分成","name":"支付模式","desc":"选择支付模式：月付、天付或分成（填写其中一个）"}]
# [param: {"required":true,"key":"dd_ks.ksVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"月付价格","desc":"月付模式的价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_ks.ksDaymoney","bool":false,"placeholder":"例:0.05,不填为0元","name":"天付价格","desc":"天付模式的价格(单位:元)/天"}]
# [param: {"required":true,"key":"dd_ks.kscoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_ks.share_rate","bool":false,"placeholder":"例:55,表示55分成","name":"分成比例","desc":"分成比例（0-100），例如55表示平台收取55%，仅分成模式生效"}]
# [param: {"required":false,"key":"dd_ks.share_allow_coin_pay","bool":true,"placeholder":"","name":"分成允许积分支付","desc":"开启后分成模式可使用积分支付（1元=100积分）"}]

def getusercontent():
    """获取用户配置"""
    dd_ks_qlname = middleware.bucketGet('dd_ks', 'dd_ks_qlname') or ''
    ks_fast_varname = middleware.bucketGet('dd_ks', 'ks_fast_varname') or 'ksToken_fast'
    ks_normal_varname = middleware.bucketGet('dd_ks', 'ks_normal_varname') or 'ksToken'
    allow_proxy = middleware.bucketGet('dd_ks', 'allow_proxy') or 'true'
    allow_proxy = allow_proxy.lower() == 'true'
    
    dd_managecommand = middleware.bucketGet('dd_ks', 'dd_managecommand') or '快手管理'
    dd_querycommand = middleware.bucketGet('dd_ks', 'dd_querycommand') or '快手查询'
    dd_signcommand = middleware.bucketGet('dd_ks', 'dd_signcommand') or '快手登录'
    
    payment_mode = (middleware.bucketGet('dd_ks', 'payment_mode') or '月付').strip()
    if payment_mode not in ['月付', '天付', '分成']:
        payment_mode = '月付'
    
    ksVipmoney = Decimal(middleware.bucketGet('dd_ks', 'ksVipmoney') or '1')
    ksDaymoney = Decimal(middleware.bucketGet('dd_ks', 'ksDaymoney') or '0.05')
    kscoin = int(middleware.bucketGet('dd_ks', 'kscoin') or '0')
    
    use_ma_pay = middleware.bucketGet('dd_ks', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    share_rate = int(middleware.bucketGet('dd_ks', 'share_rate') or '55')
    share_allow_coin_pay = middleware.bucketGet('dd_ks', 'share_allow_coin_pay') or 'false'
    share_allow_coin_pay = share_allow_coin_pay.lower() == 'true'
    
    return (ks_fast_varname, ks_normal_varname, allow_proxy, dd_ks_qlname, 
            dd_managecommand, dd_querycommand, dd_signcommand,
            payment_mode, ksVipmoney, ksDaymoney, kscoin, use_ma_pay, share_rate, share_allow_coin_pay)

def verify_account_fast(cookie_str):
    """验证极速版账号有效性"""
    cookie_str = cookie_str.replace('kpn=KUAISHOU', 'kpn=NEBULA')
    
    url = "https://nebula.kuaishou.com/rest/n/nebula/activity/earn/overview/basicInfo?source=bottom_guide_first"
    
    headers = {
        'Host': 'nebula.kuaishou.com',
        'User-Agent': 'kwai-android aegon/4.29.0',
        'Cookie': cookie_str,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=12)
        result = response.json()
        
        if result.get('result') == 1 and result.get('data'):
            data = result['data']
            nickname = data.get('userData', {}).get('nickname', '未知')
            total_coin = data.get('totalCoin', 0)
            all_cash = data.get('allCash', 0)
            
            return True, {
                'nickname': nickname,
                'coin': total_coin,
                'cash': all_cash
            }
        else:
            return False, "账号验证失败"
            
    except Exception as e:
        return False, f"请求异常: {str(e)}"

def verify_account_normal(cookie_str, default_nickname='未知'):
    """验证普通版账号有效性"""
    cookie_str = cookie_str.replace('kpn=NEBULA', 'kpn=KUAISHOU')
    
    url = "https://encourage.kuaishou.com/rest/wd/encourage/account/basicInfo"
    
    headers = {
        'Host': 'encourage.kuaishou.com',
        'User-Agent': 'kwai-android aegon/4.27.0',
        'Cookie': cookie_str,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        result = response.json()
        
        if result.get('result') == 1 and result.get('data'):
            data = result['data']
            nickname = data.get('userData', {}).get('nickname') or default_nickname
            total_coin = data.get('coinAmount', 0)
            all_cash = data.get('cashAmountDisplay', 0)
            
            return True, {
                'nickname': nickname,
                'coin': total_coin,
                'cash': all_cash
            }
        else:
            return False, "账号验证失败"
            
    except Exception as e:
        return False, f"请求异常: {str(e)}"

def parse_cookies(cookie_str):
    """解析Cookie字符串为字典"""
    cookies = {}
    for item in cookie_str.split(';'):
        if '=' in item:
            key, value = item.strip().split('=', 1)
            cookies[key] = value
    return cookies

def msg_box(title, content, footer=""):
    """生成统一格式的消息框"""
    msg = f"====={title}=====\n{content}"
    if footer:
        msg += f"\n------------------\n{footer}"
    msg += "\n=================="
    return msg

def select_version(prompt="请选择版本"):
    """通用版本选择，返回 (version_choice, version_name, varname) 或 None"""
    menu = msg_box("选择快手版本", f"{prompt}\n------------------\n[1] 某手极速版\n[2] 某手普通版", "回复数字选择\n回复 q 退出")
    sender.reply(menu)
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        return None
    if choice == '1':
        return ('1', "某手极速版", ks_fast_varname)
    elif choice == '2':
        return ('2', "某手普通版", ks_normal_varname)
    return None

def get_version_accounts(accounts, version_choice):
    """获取指定版本的账号列表"""
    result = []
    for acc in accounts:
        full_ck = middleware.bucketGet('dd_ks_token', acc)
        if full_ck:
            info = parse_token(full_ck)
            if info and info['version'] == version_choice:
                result.append(acc)
    return result

def parse_token(full_ck):
    """
    解析token字符串
    新格式: 版本
    旧格式: 备注
    
    返回: {
        'version': '1' or '2',  # 1=极速版, 2=普通版
        'name': '备注',
        'cookie': 'cookie字符串',
        'salt': 'salt',
        'proxy': '代理信息' or None
    }
    """
    if not full_ck:
        return None
    
    parts = full_ck.split('#')
    
    if len(parts) >= 4 and parts[0] in ['1', '2']:
        return {
            'version': parts[0],
            'name': parts[1] if len(parts) >= 2 else '未知',
            'cookie': parts[2] if len(parts) >= 3 else None,
            'salt': parts[3] if len(parts) >= 4 else None,
            'proxy': parts[4] if len(parts) >= 5 else None
        }
    else:
        return {
            'version': '1',  # 默认极速版
            'name': parts[0] if len(parts) >= 1 else '未知',
            'cookie': parts[1] if len(parts) >= 2 else None,
            'salt': parts[2] if len(parts) >= 3 else None,
            'proxy': parts[3] if len(parts) >= 4 else None
        }

def token_to_qinglong_format(full_ck):
    """
    将token转换为青龙格式（去掉版本标识）
    新格式: 版本
    旧格式: 备注
    """
    if not full_ck:
        return full_ck
    
    token_info = parse_token(full_ck)
    if not token_info:
        return full_ck
    
    result = f"{token_info['name']}#{token_info['cookie']}#{token_info['salt']}"
    if token_info['proxy']:
        result += f"#{token_info['proxy']}"
    
    return result

def parse_proxy_to_url(proxy_str):
    """
    解析代理字符串为标准URL格式
    支持三种格式:
    1. IP|端口|用户名|密码|过期时间 -> http://用户名:密码@IP:端口
    2. socks5://账号:密码@ip:端口 -> socks5://账号:密码@ip:端口
    3. http://账号:密码@ip:端口 -> http://账号:密码@ip:端口
    
    返回: (proxy_url, proxy_type) 或 (None, error_msg)
    """
    if not proxy_str:
        return None, "代理信息为空"
    
    proxy_str = proxy_str.strip()
    
    if proxy_str.startswith('socks5://') or proxy_str.startswith('http://'):
        try:
            if proxy_str.startswith('socks5://'):
                protocol = 'socks5'
                rest = proxy_str[9:]
            else:
                protocol = 'http'
                rest = proxy_str[7:]
            
            if '@' not in rest:
                return None, "URL格式错误，缺少@符号"
            
            auth_part, host_part = rest.rsplit('@', 1)
            
            if ':' not in auth_part:
                return None, "URL格式错误，缺少用户名或密码"
            user, pwd = auth_part.split(':', 1)
            
            if ':' not in host_part:
                return None, "URL格式错误，缺少端口"
            ip, port = host_part.rsplit(':', 1)
            
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return None, "端口无效"
            
            if not user or not pwd:
                return None, "用户名或密码为空"
            
            return f"{protocol}://{user}:{pwd}@{ip}:{port}", protocol
        except ValueError:
            return None, "URL格式解析失败"
    
    parts = proxy_str.split('|')
    if len(parts) == 5:
        ip, port, user, pwd, _ = parts
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return None, "端口无效"
        except ValueError:
            return None, "端口必须是数字"
        
        if not user or not pwd:
            return None, "用户名或密码为空"
        
        return f"http://{user}:{pwd}@{ip}:{port}", "http"
    
    return None, "格式错误，不支持的代理格式"

def validate_proxy(proxy_str):
    """
    验证代理格式和连接
    支持三种格式:
    1. IP|端口|用户名|密码|过期时间
    2. socks5://账号:密码@ip:端口
    3. http://账号:密码@ip:端口
    """
    if not proxy_str: 
        return False, "代理信息为空"
    
    proxy_url, result = parse_proxy_to_url(proxy_str)
    if proxy_url is None:
        return False, result
    
    proxy_type = result
    
    try:
        if proxy_type == 'socks5':
            proxies = {'http': proxy_url, 'https': proxy_url}
        else:
            proxies = {'http': proxy_url, 'https': proxy_url}
        
        r = requests.get("https://d.pcs.baidu.com/rest/2.0/pcs/file?method=locateupload", 
            proxies=proxies, timeout=10,
            headers={'User-Agent': 'Mozilla/5.0'})
        if r.status_code == 200:
            try:
                d = r.json()
                if d.get('error_code', -1) == 0:
                    return True, f"✅ 代理验证通过(IP:{d.get('client_ip', '未知')}, 类型:{proxy_type})"
            except: 
                pass
            return True, f"✅ 代理可用(类型:{proxy_type})"
        return False, f"代理连接失败({r.status_code})"
    except requests.exceptions.Timeout: 
        return False, "代理连接超时"
    except requests.exceptions.ProxyError: 
        return False, "代理连接失败"
    except Exception as e: 
        return False, f"代理错误: {str(e)}"

def query_account_fast(cookie_str, proxy_str=None):
    """查询极速版账号详情"""
    cookie_str = cookie_str.replace('kpn=KUAISHOU', 'kpn=NEBULA')
    
    url = "https://nebula.kuaishou.com/rest/n/nebula/account/overview"
    
    headers = {
        'Host': 'nebula.kuaishou.com',
        'User-Agent': 'kwai-android aegon/4.29.0',
        'Cookie': cookie_str,
        'Accept': 'application/json, text/plain, */*'
    }
    
    proxies = None
    if proxy_str:
        proxy_url, proxy_type = parse_proxy_to_url(proxy_str)
        if proxy_url:
            proxies = {'http': proxy_url, 'https': proxy_url}
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=12)
        result = response.json()
        
        if result.get('result') == 1 and result.get('data'):
            data = result['data']
            
            all_coin_records = []
            coin_page = data.get('coinAccountPage', {})
            if coin_page.get('data'):
                all_coin_records = coin_page['data']
            
            cash_records = []
            cash_page = data.get('cashAccountPage', {})
            if cash_page.get('data'):  
                cash_records = cash_page['data'][:3]
            
            return {
                'success': True,
                'coinBalance': data.get('coinBalance', '0'),
                'cashBalance': data.get('cashBalance', '0'),
                'accumulativeAmount': data.get('accumulativeAmount', '0'),
                'accountState': data.get('accountState', 'UNKNOWN'),
                'coinRecords': all_coin_records[:5],  # 显示用（最近5条）
                'allCoinRecords': all_coin_records,   # 统计用（所有记录）
                'cashRecords': cash_records
            }
        return {'success': False, 'msg': '查询失败'}
    except Exception as e:
        return {'success': False, 'msg': str(e)}

def calculate_today_coins_fast(coin_records):
    """统计极速版今日获得的金币数量
    
    Args:
        coin_records: 金币明细记录列表
        
    Returns:
        今日获得的金币总数（正数部分）
    """
    if not coin_records:
        return 0
    
    today_coins = 0
    today_date = datetime.now().date()
    
    for record in coin_records:
        try:
            create_time = record.get('createTime', '')
            if create_time and isinstance(create_time, str):
                parts = create_time.split('.')
                if len(parts) >= 3:
                    record_date = datetime(int(parts[0]), int(parts[1]), int(parts[2])).date()
                    if record_date == today_date:
                        amount = float(record.get('amount', 0))
                        if amount > 0:
                            today_coins += amount
        except:
            continue
    
    return today_coins

def calculate_today_coins_normal(coin_records):
    """统计普通版今日获得的金币数量
    
    Args:
        coin_records: 金币明细记录列表
        
    Returns:
        今日获得的金币总数（正数部分）
    """
    if not coin_records:
        return 0
    
    today_coins = 0
    today_date = datetime.now().date()
    
    for record in coin_records:
        try:
            create_time = record.get('createTime', 0)
            if create_time:
                record_date = datetime.fromtimestamp(create_time / 1000).date()
                if record_date == today_date:
                    amount = float(record.get('displayAmount', 0))
                    direction = record.get('direction', 'IN')
                    if direction == 'IN' and amount > 0:
                        today_coins += amount
        except:
            continue
    
    return today_coins

def query_account_normal(cookie_str, proxy_str=None):
    """查询普通版账号详情"""
    cookie_str = cookie_str.replace('kpn=NEBULA', 'kpn=KUAISHOU')
    
    basic_url = "https://encourage.kuaishou.com/rest/wd/encourage/account/basicInfo"
    headers = {
        'Host': 'encourage.kuaishou.com',
        'User-Agent': 'kwai-android aegon/4.27.0',
        'Cookie': cookie_str,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    proxies = None
    if proxy_str:
        proxy_url, proxy_type = parse_proxy_to_url(proxy_str)
        if proxy_url:
            proxies = {'http': proxy_url, 'https': proxy_url}
    
    try:
        response = requests.get(basic_url, headers=headers, proxies=proxies, timeout=15)
        result = response.json()
        
        if result.get('result') != 1 or not result.get('data'):
            return {'success': False, 'msg': '查询失败'}
        
        data = result['data']
        coin_balance = data.get('coinAmount', 0)
        cash_balance = data.get('cashAmountDisplay', 0)
        nickname = data.get('userData', {}).get('nickname', '未知')
        
        coin_detail_url = "https://encourage.kuaishou.com/rest/wd/encourage/account/detail?sigCatVer=1&accountType=coin&cursor"
        coin_response = requests.get(coin_detail_url, headers=headers, proxies=proxies, timeout=10)
        coin_records = []
        all_coin_records = []
        if coin_response.status_code == 200:
            coin_result = coin_response.json()
            if coin_result.get('result') == 1 and coin_result.get('data', {}).get('datas'):
                all_coin_records = coin_result['data']['datas']  # 保存所有记录
                coin_records = all_coin_records[:5]
        
        cash_detail_url = "https://encourage.kuaishou.com/rest/wd/encourage/account/detail?sigCatVer=1&accountType=cash&cursor"
        cash_response = requests.get(cash_detail_url, headers=headers, proxies=proxies, timeout=10)
        cash_records = []
        if cash_response.status_code == 200:
            cash_result = cash_response.json()
            if cash_result.get('result') == 1 and cash_result.get('data', {}).get('datas'):
                cash_records = cash_result['data']['datas'][:3]
        
        return {
            'success': True,
            'coinBalance': coin_balance,
            'cashBalance': cash_balance,
            'nickname': nickname,
            'coinRecords': coin_records,  # 显示用（最近3条）
            'allCoinRecords': all_coin_records,  # 统计用（所有记录）
            'cashRecords': cash_records
        }
    except Exception as e:
        return {'success': False, 'msg': str(e)}

def query_accounts():
    """查询用户所有账号"""
    if not uservalue or len(uservalue) == 0:
        sender.reply("❌ 您还没有绑定账号\n请先使用 快手登录 绑定账号")
        return
    
    accounts = eval(uservalue)
    if not accounts:
        sender.reply("❌ 账号列表为空")
        return
    
    version_menu = """
=====选择查询版本=====
请选择要查询的版本
------------------
[1] 某手极速版
[2] 某手普通版
------------------
回复数字选择版本
回复"q"退出操作
=================="""
    sender.reply(version_menu)
    
    version_choice = sender.input(120000, 1, False)
    if not version_choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif version_choice.lower() == 'q':
        sender.reply("✅ 已取消查询")
        return
    
    if version_choice not in ['1', '2']:
        sender.reply("❌ 无效的选择")
        return
    
    if version_choice == '1':
        version_name = "某手极速版"
        query_func = query_account_fast
    else:
        version_name = "某手普通版"
        query_func = query_account_normal
    
    version_accounts = []
    for account in accounts:
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            if token_info and token_info['version'] == version_choice:
                version_accounts.append(account)
    
    if not version_accounts:
        sender.reply(f"❌ 您还没有绑定任何{version_name}账号")
        return
    
    account_list = f"====={version_name}账号列表=====\n"
    for idx, account in enumerate(version_accounts, 1):
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            name = token_info['name'] if token_info else '未知'
            account_list += f"[{idx}] {name} (ID:{account})\n"
        else:
            account_list += f"[{idx}] ID:{account}\n"
    
    account_list += "------------------\n"
    account_list += "回复数字选择账号\n"
    account_list += "回复 0 查询所有账号\n"
    account_list += "回复 q 退出操作\n"
    account_list += "=================="
    sender.reply(account_list)
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif account_choice.lower() == 'q':
        sender.reply("✅ 已取消查询")
        return
    
    try:
        account_idx = int(account_choice)
        if account_idx < 0 or account_idx > len(version_accounts):
            sender.reply(f"❌ 请输入 0-{len(version_accounts)} 之间的数字")
            return
    except:
        sender.reply("❌ 请输入数字")
        return
    
    if account_idx == 0:
        query_accounts_list = version_accounts
    else:
        query_accounts_list = [version_accounts[account_idx - 1]]
    
    for idx, account in enumerate(query_accounts_list, 1):
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if not full_ck:
            sender.reply(f"❌ 账号ID: {account}\n未找到Cookie信息")
            continue
        
        token_info = parse_token(full_ck)
        if not token_info or not token_info['cookie']:
            sender.reply(f"❌ 账号ID: {account}\nCookie格式错误")
            continue
        
        name = token_info['name']
        cookie = token_info['cookie']
        proxy_info = token_info['proxy']
        
        query_result = query_func(cookie, proxy_info)
        
        result_msg = f"====={version_name}查询结果=====\n"
        result_msg += f"📝 备注: {name}\n"
        result_msg += f"🆔 ID: {account}\n"
        
        if query_result['success']:
            if version_choice == '1':
                result_msg += f"💰 金币: {query_result['coinBalance']}\n"
                result_msg += f"💵 余额: {query_result['cashBalance']}元\n"
                result_msg += f"📊 累计: {query_result['accumulativeAmount']}元\n"
                
                if payment_mode == '分成':
                    is_paid, saved_revenue, saved_share = get_today_share_status(account)
                    
                    if is_paid:
                        result_msg += f"💳 分成: 今日已结算({saved_share}元)\n"
                    else:
                        current_coins = float(query_result.get('coinBalance', 0))
                        manual_cash = detect_manual_cash_exchange(query_result.get('cashRecords', []))

                        if current_coins > 0 or manual_cash > 0:
                            current_revenue = round(current_coins / 10000, 2)
                            total_revenue = current_revenue + manual_cash
                            today_share = calculate_share_amount(total_revenue, share_rate)
                            if manual_cash > 0:
                                result_msg += f"💳 分成: 待结算(预计{today_share}元，含手动兑换{manual_cash}元)\n"
                            else:
                                result_msg += f"💳 分成: 待结算(预计{today_share}元)\n"
                        else:
                            result_msg += f"💳 分成: 待结算(预计0.0元)\n"
                else:
                    auth_status = middleware.bucketGet('dd_ks_auth', account) or '未授权'
                    result_msg += f"🔐 授权: {auth_status}\n"
                
                if query_result.get('coinRecords'):
                    result_msg += "📝 金币明细(最近5条):\n"
                    for record in query_result['coinRecords']:
                        title = record.get('eventType', '未知')
                        amount = record.get('amount', '0')
                        date_str = ''
                        try:
                            create_time = record.get('createTime', '')
                            if create_time and isinstance(create_time, str):
                                parts = create_time.split('.')
                                if len(parts) >= 3:
                                    date_str = f"{parts[1]}-{parts[2].zfill(2)} "
                        except:
                            pass
                        try:
                            amt_val = float(amount)
                            symbol = '+' if amt_val >= 0 else ''
                        except:
                            symbol = '+'
                        result_msg += f"  • {date_str}{title}: {symbol}{amount}\n"
                
                if query_result.get('cashRecords'):
                    result_msg += "💸 现金明细(最近3条):\n"
                    for record in query_result['cashRecords']:
                        title = record.get('eventType', '未知')
                        amount = record.get('amount', '0')
                        date_str = ''
                        try:
                            create_time = record.get('createTime', '')
                            if create_time and isinstance(create_time, str):
                                parts = create_time.split('.')
                                if len(parts) >= 3:
                                    date_str = f"{parts[1]}-{parts[2].zfill(2)} "
                        except:
                            pass
                        result_msg += f"  • {date_str}{title}: {symbol}{amount}元\n"
            else:
                result_msg += f"💰 金币: {query_result['coinBalance']}\n"
                result_msg += f"💵 余额: {query_result['cashBalance']}元\n"
                
                if payment_mode == '分成':
                    is_paid, saved_revenue, saved_share = get_today_share_status(account)
                    
                    if is_paid:
                        result_msg += f"💳 分成: 今日已结算({saved_share}元)\n"
                    else:
                        current_coins = float(query_result.get('coinBalance', 0))
                        manual_cash = detect_manual_cash_exchange(query_result.get('cashRecords', []))

                        if current_coins > 0 or manual_cash > 0:
                            current_revenue = round(current_coins / 10000, 2)
                            total_revenue = current_revenue + manual_cash
                            today_share = calculate_share_amount(total_revenue, share_rate)
                            if manual_cash > 0:
                                result_msg += f"💳 分成: 待结算(预计{today_share}元，含手动兑换{manual_cash}元)\n"
                            else:
                                result_msg += f"💳 分成: 待结算(预计{today_share}元)\n"
                        else:
                            result_msg += f"💳 分成: 待结算(预计0.0元)\n"
                else:
                    auth_status = middleware.bucketGet('dd_ks_auth', account) or '未授权'
                    result_msg += f"🔐 授权: {auth_status}\n"
                
                if query_result.get('coinRecords'):
                    result_msg += "📝 金币明细(最近5条):\n"
                    for record in query_result['coinRecords']:
                        title = record.get('title', '未知')
                        amount = record.get('displayAmount', '0')
                        date_str = ''
                        try:
                            create_time = record.get('createTime', 0)
                            if create_time:
                                date_obj = datetime.fromtimestamp(create_time / 1000)
                                date_str = date_obj.strftime('%m-%d') + ' '
                        except:
                            pass
                        result_msg += f"  • {date_str}{title}: +{amount}\n"
                
                if query_result.get('cashRecords'):
                    result_msg += "💸 现金明细(最近3条):\n"
                    for record in query_result['cashRecords']:
                        title = record.get('title', '未知')
                        amount = record.get('displayAmount', '0')
                        direction = record.get('direction', 'IN')
                        symbol = '+' if direction == 'IN' else '-'
                        date_str = ''
                        try:
                            create_time = record.get('createTime', 0)
                            if create_time:
                                date_obj = datetime.fromtimestamp(create_time / 1000)
                                date_str = date_obj.strftime('%m-%d') + ' '
                        except:
                            pass
                        result_msg += f"  • {date_str}{title}: {symbol}{amount}元\n"
        else:
            result_msg += f"❌ 查询失败: {query_result.get('msg', '未知错误')}\n"
        
        result_msg += "=================="
        
        sender.reply(result_msg)

def bindaccount():
    """绑定账号 - 支持格式: 备注#cookie#salt 或 备注#cookie#salt#|端口|用户名|密码|过期时间"""
    
    version_menu = """
=====选择快手版本=====
请选择要登录的版本
------------------
[1] 某手极速版
[2] 某手普通版
------------------
回复数字选择版本
回复"q"退出操作
=================="""
    sender.reply(version_menu)
    
    version_choice = sender.input(120000, 1, False)
    if not version_choice:
        sender.reply("⏰ 操作超时,已退出")
        exit(0)
    elif version_choice.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)
    
    if version_choice not in ['1', '2']:
        sender.reply("❌ 无效的选择")
        exit(0)
    
    if version_choice == '1':
        version_name = "某手极速版"
        target_varname = ks_fast_varname
    else:
        version_name = "某手普通版"
        target_varname = ks_normal_varname
    
    if allow_proxy:
        ck_guide = f"""
====={version_name}登录=====
请输入账号信息
📝 支持格式:
1. 备注#cookie#salt
2. 备注#cookie#salt#代理

🌐 代理格式支持:
• IP|端口|用户名|密码|过期时间
• socks5://账号:密码@IP:端口
• http://账号:密码@IP:端口
------------------
"""
    else:
        ck_guide = f"""
====={version_name}登录=====
请输入账号信息
📝 支持格式:
1. 备注#cookie#salt
2. 备注#cookie#salt#代理
------------------
"""
    sender.reply(ck_guide)
    
    while True:
        ck_input = sender.input(120000, 1, False)
        if not ck_input:
            sender.reply("⏰ 操作超时,已退出")
            exit(0)
        elif ck_input.lower() == 'q':
            sender.reply("✅ 已取消登录")
            exit(0)
            
        try:
            parts = ck_input.split('#')
            
            if len(parts) < 3:
                sender.reply("""
❌ 格式错误
------------------
正确格式: 备注
或: 备注#Cookie#Salt#代理信息""")
                exit(0)
            
            name = parts[0]
            ck = parts[1]
            salt_input = parts[2]
            proxy_input = parts[3] if len(parts) >= 4 else ""
            
            if proxy_input:
                proxy_valid, proxy_msg = validate_proxy(proxy_input)
                if not proxy_valid:
                    sender.reply(f"""
❌ 代理验证失败
------------------
{proxy_msg}
------------------
支持的代理格式:
1. IP|端口|用户名|密码|过期时间
   示例: 110.84.77.52|6855|user|pass|2025-12-19
2. socks5://账号:密码@IP:端口
   示例: socks5://user:pass@119.84.77.52:6855
3. http://账号:密码@IP:端口
   示例: http://user:pass@119.84.77.52:6855""")
                    exit(0)
                
                sender.reply(proxy_msg)
            
            if version_choice == '1':
                is_valid, result = verify_account_fast(ck)
            else:
                is_valid, result = verify_account_normal(ck, name)
            
            if is_valid:
                cookies = parse_cookies(ck)
                base_account = cookies.get('userId', 'unknown')
                if base_account == 'unknown':
                    sender.reply("❌ 无法获取账号信息")
                    exit(0)
                
                if payment_mode == '分成':
                    has_debt, total_debt, debts = check_uid_has_debt(base_account)
                    if has_debt:
                        debt_details = "\n".join([f"  • {d.get('date')}: {d.get('share_amount')}元" for d in debts[:5]])
                        if len(debts) > 5:
                            debt_details += f"\n  ... 共{len(debts)}条欠款记录"
                        
                        sender.reply(f"""
=====无法提交=====
❌ 该快手账号存在未支付的分成欠款！

📝 欠款明细:
{debt_details}

💰 欠款总额: {total_debt}元
------------------
请先支付欠款后再提交账号
如需支付欠款，请联系管理员
==================""")
                        exit(0)
                
                account = f"{base_account}_{version_choice}"
                
                nickname = result.get('nickname', name)
                coin = result.get('coin', 0)
                cash = result.get('cash', 0)
                
                full_ck = f"{version_choice}#{name}#{ck}#{salt_input}"
                if proxy_input:
                    full_ck += f"#{proxy_input}"
                
                is_new_account = False
                if len(uservalue) == 0:
                    is_new_account = True
                    middleware.bucketSet('dd_ks_user', userid, str([account]))
                    middleware.bucketSet('dd_ks_token', account, full_ck)
                    middleware.bucketSet('dd_ks_auth', account, '')
                else:
                    accounts = eval(uservalue)
                    if account not in accounts:
                        is_new_account = True
                        accounts.append(account)
                        middleware.bucketSet('dd_ks_user', userid, str(accounts))
                        middleware.bucketSet('dd_ks_auth', account, '')
                    else:
                        is_new_account = False
                    
                    middleware.bucketSet('dd_ks_token', account, full_ck)
                
                accountVip = middleware.bucketGet('dd_ks_auth', account)
                should_submit_to_qinglong = False
                
                if payment_mode == '分成':
                    should_submit_to_qinglong = True
                    auth_status = f'分成模式'
                elif payment_mode == '月付':
                    if accountVip and accountVip >= today_time:
                        should_submit_to_qinglong = True
                        auth_status = f'已授权至{accountVip}(月付)'
                    else:
                        should_submit_to_qinglong = False
                        auth_status = '未授权(月付)'
                else:
                    if accountVip and accountVip >= today_time:
                        should_submit_to_qinglong = True
                        auth_status = f'已授权至{accountVip}(天付)'
                    else:
                        should_submit_to_qinglong = False
                        auth_status = '未授权(天付)'
                
                if should_submit_to_qinglong:
                    qinglong_value = token_to_qinglong_format(full_ck)
                    Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
                
                action_type = "更新" if not is_new_account else "绑定"
                success_msg = f"""
====={action_type}成功=====
👤 昵称: {nickname}
🆔 账号ID: {account}
💰 金币数: {coin}
💵 余额: {cash}元
🔐 授权状态: {auth_status}
🌐 代理状态: {'已设置' if proxy_input else '未设置'}
------------------
提示: {'账号已添加至青龙' if should_submit_to_qinglong else '请先授权账号再使用'}
=================="""
                sender.reply(success_msg)
                break
                
            else:
                sender.reply(f"""
=====验证失败=====
❌ {result}
------------------
请检查Cookie是否有效!
==================""")
                exit(0)
                
        except Exception as e:
            sender.reply(f"""
=====绑定异常=====
请重试或联系管理员
错误: {str(e)}
==================""")
            exit(0)

def seekql():
    """连接青龙"""
    if not dd_ks_qlname:
        sender.reply("❌ 未配置青龙信息")
        exit(0)
        
    qllist = dd_ks_qlname.split('丨')
    if len(qllist) != 3:
        sender.reply("❌ 青龙配置格式错误\n正确格式: Host丨ClientID丨ClientSecret")
        exit(0)
        
    QLurl, ClientID, ClientSecret = [x.strip() for x in qllist]
    
    if not all([QLurl, ClientID, ClientSecret]):
        sender.reply("❌ 青龙配置参数不完整")
        exit(0)
        
    if not QLurl.startswith(('http://', 'https://')):
        sender.reply("❌ 青龙地址格式错误")
        exit(0)
        
    qltoken = QLtoken(QLurl, ClientID, ClientSecret)
    return QLurl, qltoken

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if token := result.get('data', {}).get('token'):
                return token
        
        sender.reply("❌ 获取青龙Token失败")
        exit(0)
    except Exception as e:
        sender.reply(f"❌ 连接青龙失败: {str(e)}")
        exit(0)

def extract_base_account(account):
    """
    从复合键中提取基础账号ID
    例如: '123456_1' -> '123456'
    如果不是复合键格式，直接返回原值
    """
    if not account:
        return account
    
    if account.endswith('_1') or account.endswith('_2'):
        return account.rsplit('_', 1)[0]
    
    return account

def Addenvs(osname, value, account, phone):
    """添加/更新环境变量到青龙
    
    Args:
        osname: 变量名（如 ksToken_fast 或 ksToken）
        value: 变量值
        account: 账号ID（可能是复合键格式，如 123456_1）
        phone: 备注名称
    """
    url = f"{QLurl}/open/envs"
    headers = {"Authorization": f"Bearer {qltoken}", "Content-Type": "application/json"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200 or resp.json()['code'] != 200:
            sender.reply("❌ 获取青龙变量失败")
            return False
        
        base_account = extract_base_account(account)
        
        qlid = None
        for env in resp.json()['data']:
            if env['name'] == osname and env.get('value') == value:
                qlid = env['id']
                break
        
        if not qlid:
            for env in resp.json()['data']:
                remarks = env.get('remarks', '')
                if env['name'] == osname and f'快手:{base_account}丨' in remarks:
                    qlid = env['id']
                    break
        
        accountVip = middleware.bucketGet('dd_ks_auth', account) or '未授权'
        remarks = f'快手:{base_account}丨用户:{userid}丨ID:{phone}丨授权至:{accountVip}'
        
        if qlid:
            data = {"value": value, "name": osname, "remarks": remarks, "id": qlid}
            resp = requests.put(url, headers=headers, json=data, timeout=10)
        else:
            data = [{"value": value, "name": osname, "remarks": remarks}]
            resp = requests.post(url, headers=headers, json=data, timeout=10)
        
        if resp.status_code == 200 and resp.json()['code'] == 200:
            return True
        
        sender.reply("❌ 提交青龙变量失败")
        return False
        
    except Exception as e:
        sender.reply(f"❌ 青龙操作异常: {str(e)}")
        return False

def get_payment_config():
    """获取支付配置"""
    config = {
        'use_ma_pay': middleware.bucketGet('dd_ks', 'use_ma_pay') or 'false',
        'zsm': middleware.bucketGet('dd_ks', 'zsm') or '',
        'ma_pay_gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
        'ma_pay_pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
        'ma_pay_key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
        'ma_pay_type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
        'ma_pay_notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or '',
    }
    config['pid'] = config['ma_pay_pid']
    config['key'] = config['ma_pay_key']
    config['gateway'] = config['ma_pay_gateway']
    return config

PAY_TYPE_NAMES = {
    'alipay': '支付宝',
    'wxpay': '微信支付',
    'qqpay': 'QQ钱包',
}

def generate_qrcode(url):
    """生成二维码图片"""
    try:
        from urllib.parse import quote
        encoded_url = quote(url, safe='')
        api_url = f"https://api.qrtool.cn/?text={encoded_url}"
        return api_url
    except:
        return None

class MaPay_Api:
    """码支付API类"""
    def __init__(self, config):
        self.config = config
        
    def calculate_md5(self, text):
        """计算字符串的MD5值"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
        
    def sort_dict_by_key(self, data):
        """对字典按照键名排序"""
        return dict(sorted(data.items(), key=lambda x: x[0]))
    
    def create_payment(self, amount, out_trade_no, name, user_id, pay_type=None, sitename=""):
        """创建支付订单"""
        try:
            if pay_type is None:
                pay_types = [p.strip() for p in self.config['ma_pay_type'].split(',') if p.strip()]
                if not pay_types:
                    pay_types = ["alipay", "wxpay", "qqpay"]
                pay_type = pay_types[0]
            
            params = {
                'pid': self.config['pid'],
                'type': pay_type,
                'out_trade_no': out_trade_no,
                'name': name,
                'money': str(amount),
                'sitename': sitename,
                'param': user_id
            }
            
            if self.config.get('ma_pay_notify_url'):
                params['notify_url'] = self.config['ma_pay_notify_url']
            
            params = {k: v for k, v in params.items() if v}
            sorted_params = self.sort_dict_by_key(params)
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
            sign = self.calculate_md5(sign_str + self.config['key']).lower()
            
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            mapi_url = self.config['gateway']
            if mapi_url.endswith('/'):
                mapi_url = mapi_url[:-1]
            mapi_url = f"{mapi_url}/mapi.php"
            
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"创建支付订单失败，HTTP状态码: {response.status_code}"
            
            try:
                result = response.json()
            except:
                return False, None, "创建支付订单失败，返回数据格式错误"
            
            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')
            
            if code == 1:
                return True, result, msg
            else:
                return False, None, msg
                
        except Exception as e:
            return False, None, f"创建订单失败: {str(e)}"
    
    def query_order(self, out_trade_no=None, trade_no=None):
        """查询订单状态"""
        try:
            query_url = self.config['gateway']
            if query_url.endswith('/'):
                query_url = query_url[:-1]
            
            if '/xpay/epay/api.php' not in query_url:
                query_url = f"{query_url}/xpay/epay/api.php"
            
            params = {
                "act": "order",
                "pid": self.config['pid'],
                "key": self.config['key']
            }
            
            if trade_no:
                params["trade_no"] = trade_no
            elif out_trade_no:
                params["out_trade_no"] = out_trade_no
            else:
                return False, None, "必须提供商户订单号或系统订单号"
            
            response = requests.get(query_url, params=params, timeout=10)
            
            if response.status_code != 200:
                return False, None, f"查询订单失败，HTTP状态码: {response.status_code}"
            
            try:
                result = response.json()
            except:
                return False, None, "查询订单失败，返回数据格式错误"
            
            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')
            
            if code == 1:
                order_status = result.get('status')
                if order_status == 1:
                    return True, result, "支付成功"
                else:
                    return True, result, "订单未支付"
            else:
                return False, None, msg
                
        except Exception as e:
            return False, None, f"查询订单异常: {str(e)}"

def poll_payment_status(out_trade_no, payment_config, max_tries=30):
    """轮询支付状态"""
    ma_pay_api = MaPay_Api(payment_config)
    
    for i in range(max_tries):
        try:
            success, data, msg = ma_pay_api.query_order(out_trade_no=out_trade_no)
            
            if success and isinstance(data, dict) and data.get('status') == 1:
                return True, "支付成功", data
            
            result = sender.input(5000, 1, False)
            if result and result.lower() == 'q':
                return False, "用户取消查询", None
                
        except Exception as e:
            print(f"查询订单状态出错: {str(e)}")
    
    return False, "查询超时，订单可能尚未支付", None

def acquire_payment_lock(timeout=30):
    """获取支付锁
    
    Args:
        timeout: 锁超时时间（秒），默认30秒
        
    Returns:
        (success, msg): 是否成功获取锁、消息
    """
    lock_key = 'payment_lock'
    lock_data = middleware.bucketGet('dd_ks_lock', lock_key)
    
    current_time = time.time()
    
    if lock_data:
        try:
            lock_info = json.loads(lock_data)
            lock_user = lock_info.get('user_id')
            lock_time = lock_info.get('timestamp', 0)
            
            if current_time - lock_time < timeout:
                if lock_user == userid:
                    return True, "已持有支付锁"
                else:
                    remaining = int(timeout - (current_time - lock_time))
                    return False, f"其他用户正在支付中，请等待{remaining}秒后重试"
        except:
            pass
    
    lock_info = {
        'user_id': userid,
        'timestamp': current_time
    }
    middleware.bucketSet('dd_ks_lock', lock_key, json.dumps(lock_info))
    return True, "成功获取支付锁"

def release_payment_lock():
    """释放支付锁"""
    lock_key = 'payment_lock'
    try:
        lock_data = middleware.bucketGet('dd_ks_lock', lock_key)
        if lock_data:
            lock_info = json.loads(lock_data)
            if lock_info.get('user_id') == userid or sender.isAdmin():
                middleware.bucketDel('dd_ks_lock', lock_key)
                return True
    except:
        pass
    return False

def check_payment_lock_status():
    """检查支付锁状态
    
    Returns:
        (is_locked, lock_user, remaining_time): 是否被锁定、锁定用户ID、剩余时间
    """
    lock_key = 'payment_lock'
    lock_data = middleware.bucketGet('dd_ks_lock', lock_key)
    
    if not lock_data:
        return False, None, 0
    
    try:
        lock_info = json.loads(lock_data)
        lock_user = lock_info.get('user_id')
        lock_time = lock_info.get('timestamp', 0)
        current_time = time.time()
        elapsed = current_time - lock_time
        
        if elapsed >= 30:
            middleware.bucketDel('dd_ks_lock', lock_key)
            return False, None, 0
        
        remaining = int(30 - elapsed)
        return True, lock_user, remaining
    except:
        return False, None, 0

def process_payment(amount, months, account_count=1):
    """处理支付流程
    
    Args:
        amount: 支付金额
        months: 授权月数（0表示分成模式）
        account_count: 账号数量
        
    Returns:
        (success, msg): 是否成功、消息
    """
    lock_success, lock_msg = acquire_payment_lock(timeout=30)
    if not lock_success:
        return False, f"❌ {lock_msg}"
    
    try:
        payment_config = get_payment_config()
        use_ma_pay = payment_config['use_ma_pay'].lower() == 'true'
        
        product_name = '快手分成' if months == 0 else '快手授权'
        
        if months > 0 and kscoin > 0:
            required_coins = kscoin * months * account_count
            user_coins_str = middleware.bucketGet('dd_sign_points', userid) or '0'
            user_coins = int(user_coins_str)
            
            time_unit_display = '天' if payment_mode == '天付' else '月'
            pay_menu = f"""
=====选择支付方式=====
💰 授权金额: {amount}元
📅 授权时长: {months}{time_unit_display}
📊 账号数量: {account_count}个
------------------
[1] 💰 现金支付 ({amount}元)
[2] 🪙 积分支付 ({required_coins}积分)
   💫 当前积分: {user_coins}
------------------
回复数字选择方式
回复'q'退出操作
=================="""
            sender.reply(pay_menu)
            
            choice = sender.input(120000, 1, False)
            if not choice or choice.lower() == 'q':
                release_payment_lock()
                return False, "已取消支付"
            
            if choice == '2':
                if user_coins < required_coins:
                    release_payment_lock()
                    return False, f"积分不足！当前积分: {user_coins}，需要: {required_coins}"
                
                time_unit_display = '天' if payment_mode == '天付' else '月'
                confirm_msg = f"""
💫 积分支付确认
💰 消耗积分: {required_coins}
⏰ 授权时长: {months}{time_unit_display}
📊 账号数量: {account_count}个
------------------
确认请回复【y】
取消请回复【n】
=================="""
                sender.reply(confirm_msg)
                
                confirm = sender.input(120000, 1, False)
                if not confirm or confirm.lower() not in ['y', 'yes', '是', 'Y']:
                    release_payment_lock()
                    return False, "已取消支付"
                
                new_balance = user_coins - required_coins
                middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                release_payment_lock()
                return True, f"积分支付成功！已扣除 {required_coins} 积分（剩余: {new_balance}）"
            elif choice != '1':
                release_payment_lock()
                return False, "无效的选择"
        
        if use_ma_pay and payment_config['ma_pay_gateway'] and payment_config['ma_pay_pid'] and payment_config['ma_pay_key']:
            result = process_ma_pay(amount, months, account_count, payment_config, product_name)
        else:
            result = process_normal_pay(amount, months, account_count, payment_config, product_name)
        
        release_payment_lock()
        return result
    except Exception as e:
        release_payment_lock()
        return False, f"支付异常: {str(e)}"

def process_ma_pay(amount, months, account_count, payment_config, product_name='快手授权'):
    """码支付流程"""
    try:
        out_trade_no = f"KS{int(time.time())}{userid}"
        
        pay_types_str = payment_config['ma_pay_type'].strip()
        if not pay_types_str:
            pay_types_str = "alipay,wxpay,qqpay"
        
        pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
        
        selected_type = ""
        if len(pay_types) == 1:
            selected_type = pay_types[0]
            sender.reply(f"💰 支付金额: {amount}元")
        else:
            pay_options_text = "\n".join([f"{i+1}. {PAY_TYPE_NAMES.get(t, t)}" for i, t in enumerate(pay_types)])
            sender.reply(f"""💰 支付金额: {amount}元
请选择支付方式:
{pay_options_text}

请回复对应序号(1-{len(pay_types)})，或输入q取消:""")
            
            choice = sender.input(120000, 1, False)
            
            if not choice or choice.lower() == 'q':
                return False, "已取消支付"
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(pay_types):
                    selected_type = pay_types[choice_idx]
                else:
                    return False, "选择无效，已取消支付"
            except ValueError:
                return False, "输入无效，已取消支付"
        
        ma_pay_api = MaPay_Api(payment_config)
        
        try:
            success, result, msg = ma_pay_api.create_payment(
                amount=amount,
                out_trade_no=out_trade_no,
                name=f"快手授权-{months}月",
                user_id=userid,
                pay_type=selected_type
            )
        except Exception as e:
            return False, f'创建订单时出错: {str(e)}'
        
        if not success:
            if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                sender.reply(f'码支付暂不可用({msg})，切换到默认收款方式')
                return process_normal_pay(amount, months, account_count, payment_config)
            else:
                return False, f'创建订单失败: {msg}'
        
        payurl = result.get('payurl', '')
        if not payurl:
            return False, '获取支付链接失败'
        
        selected_type_name = PAY_TYPE_NAMES.get(selected_type, selected_type)
        qrcode_api_url = generate_qrcode(payurl)
        
        if qrcode_api_url:
            if selected_type == "qqpay":
                pay_msg = f'请使用【{selected_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！\n[CQ:image,file={qrcode_api_url}]'
            else:
                pay_msg = f'请使用【{selected_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n[CQ:image,file={qrcode_api_url}]'
            sender.reply(pay_msg)
        else:
            sender.reply(f"二维码生成失败，请使用【{selected_type_name}】打开链接：\n{payurl}")
        
        is_paid, msg, data = poll_payment_status(out_trade_no, payment_config)
        
        if is_paid:
            return True, f"支付成功！订单号: {out_trade_no}"
        else:
            return False, f"支付未完成: {msg}"
            
    except Exception as e:
        return False, f'支付处理失败: {str(e)}'

def process_normal_pay(amount, months, account_count, payment_config, product_name='快手授权'):
    """常规支付流程（微信支付）"""
    if not payment_config['zsm']:
        return False, '未配置收款码，请联系管理员'
    
    zfzt = sender.atWaitPay()
    if zfzt:
        return False, '当前有人正在支付，请稍后再试'
    
    if months == 0:
        pay_msg = f"""
=====微信扫码支付=====
🎫 商品: {product_name}
📊 账号: {account_count}个
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    else:
        time_unit_display = '天' if payment_mode == '天付' else '月'
        pay_msg = f"""
=====微信扫码支付=====
🎫 商品: {product_name}
📅 时长: {months}{time_unit_display}
📊 账号数量: {account_count}个
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)
    sender.replyImage(payment_config['zsm'])
    
    ddzf = sender.waitPay("q", 100 * 1000)
    
    try:
        if not ddzf or str(ddzf) == 'q':
            return False, '已取消支付'
        
        try:
            if isinstance(ddzf, str):
                ddzf = json.loads(ddzf)
        except json.JSONDecodeError:
            return False, '支付结果解析失败，如果您已完成支付，请联系管理员'
        
        try:
            if ddzf.get('Type') == '微信赞赏' or ddzf.get('Type') == '微信收款':
                paid_amount = float(ddzf.get('Money', 0))
                pay_time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                payer_name = ddzf.get('FromName', '')
            elif ddzf.get('Money'):
                paid_amount = float(ddzf.get('Money', 0))
                pay_time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                payer_name = ddzf.get('FromName', '')
            elif ddzf.get('money'):
                paid_amount = float(ddzf.get('money', 0))
                pay_time = ddzf.get('time', '').replace('T', ' ').split('.')[0]
                payer_name = ddzf.get('fromName', '')
            else:
                return False, '不支持的支付消息格式'
            
            if not pay_time:
                pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if paid_amount <= 0:
                return False, '支付金额无效'
            
            if abs(paid_amount - amount) > 0.01:
                return False, f'支付金额不符，应付{amount}元，实付{paid_amount}元'
            
            return True, f"支付成功！支付时间: {pay_time}"
            
        except (ValueError, TypeError) as e:
            return False, f"支付金额格式错误: {str(e)}"
            
    except Exception as e:
        return False, f"处理支付结果时出错: {str(e)}"

def calculate_share_amount(revenue, share_rate):
    """计算分成金额
    
    Args:
        revenue: 收益金额
        share_rate: 分成比例（0-100）
        
    Returns:
        应付分成金额（保留一位小数）
    """
    result = Decimal(str(revenue)) * Decimal(str(share_rate)) / Decimal('100')
    return float(result.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))

def detect_manual_cash_exchange(cash_records):
    """检测手动兑换的现金金额
    
    当天存在多次"金币兑换现金"记录时，第一次是自动兑换，后续的是手动兑换
    需要将手动兑换的金额计入分成
    
    Args:
        cash_records: 现金明细记录列表
        
    Returns:
        manual_exchange_amount: 手动兑换的总金额（元）
    """
    if not cash_records:
        return 0.0
    
    today = str(datetime.now().date())
    today_exchanges = []
    
    for record in cash_records:
        title = record.get('eventType') or record.get('title', '')
        
        if '金币兑换现金' in title or '兑换' in title:
            amount_str = record.get('amount') or record.get('displayAmount', '0')
            
            try:
                amount = float(amount_str)
            except:
                continue
            
            create_time = record.get('createTime')
            record_date = None
            
            if isinstance(create_time, str):
                parts = create_time.split('.')
                if len(parts) >= 3:
                    try:
                        year = int(parts[0])
                        month = int(parts[1])
                        day = int(parts[2])
                        record_date = f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}"
                    except:
                        pass
            elif isinstance(create_time, (int, float)):
                try:
                    date_obj = datetime.fromtimestamp(create_time / 1000)
                    record_date = str(date_obj.date())
                except:
                    pass
            
            if record_date == today and amount > 0:
                today_exchanges.append(amount)
    
    if len(today_exchanges) <= 1:
        return 0.0
    
    manual_total = sum(today_exchanges[1:])
    return round(manual_total, 2)

def get_today_share_status(account):
    """获取今日分成状态
    
    Returns:
        (is_paid, revenue, share_amount): 是否已支付、收益、分成金额
    """
    today = str(datetime.now().date())
    share_key = f"share_{account}_{today}"
    share_data = middleware.bucketGet('dd_ks_share', share_key)
    
    if share_data:
        try:
            data = json.loads(share_data)
            return data.get('is_paid', False), data.get('revenue', 0), data.get('share_amount', 0)
        except:
            return False, 0, 0
    return False, 0, 0

def get_ks_uid_from_account(account):
    """从账号ID中提取快手userId
    
    账号格式: {userId}_{version}，例如: 123456_1
    返回: userId（不含版本号）
    """
    if not account:
        return None
    parts = account.rsplit('_', 1)
    return parts[0] if len(parts) >= 1 else account

def add_share_debt(account, revenue, share_amount, date=None):
    """添加分成欠款记录
    
    使用快手userId作为唯一标识，防止删除账号后重新提交逃避欠款
    数据桶: dd_ks_debt
    Key格式: debt_{ks_uid}_{date}
    """
    ks_uid = get_ks_uid_from_account(account)
    if not ks_uid:
        return
    
    if date is None:
        date = str(datetime.now().date())
    
    debt_key = f"debt_{ks_uid}_{date}"
    debt_data = {
        'ks_uid': ks_uid,
        'account': account,
        'date': date,
        'revenue': float(revenue),
        'share_amount': float(share_amount),
        'create_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    middleware.bucketSet('dd_ks_debt', debt_key, json.dumps(debt_data))

def remove_share_debt(account, date=None):
    """删除分成欠款记录（用户支付后调用）"""
    ks_uid = get_ks_uid_from_account(account)
    if not ks_uid:
        return
    
    if date is None:
        date = str(datetime.now().date())
    
    debt_key = f"debt_{ks_uid}_{date}"
    middleware.bucketDel('dd_ks_debt', debt_key)

def get_account_debts(account):
    """获取账号的所有欠款记录
    
    Returns:
        list: 欠款记录列表 [{'date': '2025-12-19', 'share_amount': 0.55}, ...]
    """
    ks_uid = get_ks_uid_from_account(account)
    if not ks_uid:
        return []
    
    return get_uid_debts(ks_uid)

def get_uid_debts(ks_uid):
    """根据快手userId获取所有欠款记录
    
    Returns:
        list: 欠款记录列表
    """
    if not ks_uid:
        return []
    
    debts = []
    today = datetime.now().date()
    for i in range(30):
        check_date = str(today - timedelta(days=i))
        debt_key = f"debt_{ks_uid}_{check_date}"
        debt_data = middleware.bucketGet('dd_ks_debt', debt_key)
        if debt_data:
            try:
                data = json.loads(debt_data)
                debts.append(data)
            except:
                pass
    return debts

def get_total_debt_amount(account):
    """获取账号总欠款金额"""
    debts = get_account_debts(account)
    if not debts:
        return 0
    total = sum(Decimal(str(d.get('share_amount', 0))) for d in debts)
    return float(total.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))

def check_uid_has_debt(ks_uid):
    """检查快手userId是否有欠款
    
    用于新账号提交时检查是否有历史欠款
    Returns:
        (has_debt, total_amount, debts): 是否有欠款、总金额、欠款列表
    """
    debts = get_uid_debts(ks_uid)
    if not debts:
        return False, 0, []
    
    total = sum(Decimal(str(d.get('share_amount', 0))) for d in debts)
    total = float(total.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    return True, total, debts

def save_share_record(account, revenue, share_amount, is_paid=False, coins=None):
    """保存分成记录"""
    today = str(datetime.now().date())
    share_key = f"share_{account}_{today}"
    
    share_data = {
        'account': account,
        'date': today,
        'coins': float(coins) if coins else 0,  # 今日金币数
        'revenue': float(revenue),  # 折合现金
        'share_amount': float(share_amount),
        'is_paid': is_paid,
        'pay_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S") if is_paid else None
    }
    
    middleware.bucketSet('dd_ks_share', share_key, json.dumps(share_data))
    
    if not is_paid and share_amount > 0:
        add_share_debt(account, revenue, share_amount, today)
    elif is_paid:
        remove_share_debt(account, today)

def process_share_payment(account, revenue, share_rate, coins=None):
    """处理分成支付
    
    Args:
        account: 账号ID
        revenue: 今日收益（元）
        share_rate: 分成比例
        coins: 今日金币数（可选）
        
    Returns:
        (success, msg): 是否成功、消息
    """
    share_amount = calculate_share_amount(revenue, share_rate)
    
    if share_amount <= 0:
        return False, "分成金额必须大于0"
    
    required_coins = int(share_amount * 100)
    
    if share_allow_coin_pay:
        user_coins_str = middleware.bucketGet('dd_sign_points', userid) or '0'
        user_coins = int(user_coins_str)
        
        if coins:
            payment_menu = f"""
=====分成结算=====
🪙 今日金币: {coins}个
💰 折合现金: {revenue}元 (1万币=1元)
📈 分成比例: {share_rate}%
💵 应付金额: {share_amount}元
------------------
请选择支付方式：
[1] 💰 现金支付 ({share_amount}元)
[2] 🪙 积分支付 ({required_coins}积分)
   💫 当前积分: {user_coins}
[q] 取消操作
=================="""
        else:
            payment_menu = f"""
=====分成结算=====
📊 今日收益: {revenue}元
📈 分成比例: {share_rate}%
💵 应付金额: {share_amount}元
------------------
请选择支付方式：
[1] 💰 现金支付 ({share_amount}元)
[2] 🪙 积分支付 ({required_coins}积分)
   💫 当前积分: {user_coins}
[q] 取消操作
=================="""
        sender.reply(payment_menu)
        
        payment_choice = sender.input(120000, 1, False)
        if not payment_choice:
            return False, "操作超时"
        elif payment_choice.lower() == 'q':
            return False, "已取消支付"
        
        if payment_choice == '1':
            pay_success, pay_msg = process_payment(share_amount, 0, 1)
        elif payment_choice == '2':
            user_coins_str = middleware.bucketGet('dd_sign_points', userid) or '0'
            user_coins = int(user_coins_str)
            
            if user_coins < required_coins:
                return False, f"积分不足！当前积分: {user_coins}，需要: {required_coins}"
            
            new_balance = user_coins - required_coins
            middleware.bucketSet('dd_sign_points', userid, str(new_balance))
            pay_success = True
            pay_msg = f"积分支付成功！已扣除 {required_coins} 积分（剩余: {new_balance}）"
        else:
            return False, "无效的选择"
    else:
        if coins:
            confirm_msg = f"""
=====分成结算=====
🪙 今日金币: {coins}个
💰 折合现金: {revenue}元 (1万币=1元)
📈 分成比例: {share_rate}%
💵 应付金额: {share_amount}元
------------------
确认支付分成？
[y] 确认支付
[n] 取消操作
=================="""
        else:
            confirm_msg = f"""
=====分成结算=====
📊 今日收益: {revenue}元
📈 分成比例: {share_rate}%
💰 应付金额: {share_amount}元
------------------
确认支付分成？
[y] 确认支付
[n] 取消操作
=================="""
        sender.reply(confirm_msg)
        
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() not in ['y', 'yes', '是', 'Y']:
            return False, "已取消支付"
        
        pay_success, pay_msg = process_payment(share_amount, 0, 1)
    
    if pay_success:
        save_share_record(account, revenue, share_amount, is_paid=True, coins=coins)
        return True, f"{pay_msg}\n今日授权已完成"
    else:
        return False, f"分成支付失败: {pay_msg}"

def check_share_authorization(account, version_choice):
    """检查分成模式授权状态
    
    Returns:
        (is_authorized, msg): 是否已授权、消息
    """
    if payment_mode != '分成':
        auth_status = middleware.bucketGet('dd_ks_auth', account)
        today = str(datetime.now().date())
        
        if auth_status and auth_status >= today:
            return True, f"账号已授权至: {auth_status}"
        else:
            return False, "账号未授权或已过期"
    
    is_paid, revenue, share_amount = get_today_share_status(account)
    
    if is_paid:
        return True, f"今日分成已支付: {share_amount}元"
    else:
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if not full_ck:
            return False, "未找到账号信息"
        
        token_info = parse_token(full_ck)
        if not token_info or not token_info['cookie']:
            return False, "Cookie信息错误"
        
        cookie = token_info['cookie']
        proxy_info = token_info['proxy']
        
        if version_choice == '1':
            query_result = query_account_fast(cookie, proxy_info)
        else:
            query_result = query_account_normal(cookie, proxy_info)
        
        if not query_result.get('success'):
            return False, f"查询收益失败: {query_result.get('msg', '未知错误')}"
        
        today_coins = float(query_result.get('coinBalance', 0))
        
        if today_coins <= 0:
            return False, "今日暂无金币收益，无需支付分成"
        
        today_revenue = round(today_coins / 10000, 2)
        
        share_amount = calculate_share_amount(today_revenue, share_rate)
        
        save_share_record(account, today_revenue, share_amount, is_paid=False, coins=today_coins)
        
        return False, f"今日金币: {int(today_coins)}个 ({today_revenue}元)，需支付分成: {share_amount}元"

def manage_accounts():
    """账号管理功能"""
    if not uservalue or len(uservalue) == 0:
        sender.reply("❌ 您还没有绑定任何账号\n请先发送 快手登录 进行账号绑定")
        return
    
    accounts = eval(uservalue)
    
    version_menu = """
=====选择快手版本=====
请选择要管理的版本
------------------
[1] 某手极速版
[2] 某手普通版
------------------
回复数字选择版本
回复 q 退出操作
=================="""
    sender.reply(version_menu)
    
    version_choice = sender.input(120000, 1, False)
    if not version_choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif version_choice.lower() == 'q':
        sender.reply("✅ 已取消管理")
        return
    
    if version_choice not in ['1', '2']:
        sender.reply("❌ 无效的选择")
        return
    
    if version_choice == '1':
        version_name = "某手极速版"
        target_varname = ks_fast_varname
    else:
        version_name = "某手普通版"
        target_varname = ks_normal_varname
    
    version_accounts = []
    for account in accounts:
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            if token_info and token_info['version'] == version_choice:
                version_accounts.append(account)
    
    if not version_accounts:
        sender.reply(f"❌ 您还没有绑定任何{version_name}账号")
        return
    
    account_list = f"""
====={version_name}账号管理=====
------------------
[0] 🎯 批量授权所有账号
------------------
"""
    
    for idx, account in enumerate(version_accounts, 1):
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            name = token_info['name'] if token_info else '未知'
            account_list += f"[{idx}] {name}\n------------------\n"
        else:
            account_list += f"[{idx}] 未知\n------------------\n"
    
    account_list += "回复数字选择账号\n回复 0 批量管理所有账号\n回复 q 退出操作\n=================="
    sender.reply(account_list)
    
    choice = sender.input(120000, 1, False)
    if not choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif choice.lower() == 'q':
        sender.reply("✅ 已取消管理")
        return
    
    try:
        choice_idx = int(choice)
        if choice_idx < 0 or choice_idx > len(version_accounts):
            sender.reply(f"❌ 请输入 0-{len(version_accounts)} 之间的数字")
            return
    except:
        sender.reply("❌ 请输入正确的数字")
        return
    
    if choice_idx == 0:
        if payment_mode == '天付':
            time_unit = '天数'
            time_example = '30'
        else:
            time_unit = '月数'
            time_example = '1'
        
        auth_guide = f"""
=====批量授权设置=====
版本: {version_name}
账号数量: {len(version_accounts)}个
------------------
请输入授权{time_unit}(如:{time_example})
回复数字设置{time_unit}
回复 q 退出操作
=================="""
        sender.reply(auth_guide)
        
        months = sender.input(120000, 1, False)
        if not months:
            sender.reply("⏰ 操作超时,已退出")
            return
        elif months.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            months = int(months)
            if months <= 0:
                time_unit = '天数' if payment_mode == '天付' else '月数'
                sender.reply(f"❌ 授权{time_unit}必须大于0")
                return
        except:
            sender.reply("❌ 请输入正确的数字")
            return
        
        if payment_mode == '天付':
            unit_price = ksDaymoney
            time_unit = '天'
        else:
            unit_price = ksVipmoney
            time_unit = '月'
        
        total_money = Decimal(months) * unit_price * len(version_accounts)
        
        time_unit_display = '天' if payment_mode == '天付' else '月'
        confirm_msg = f"""
=====批量授权确认=====
📱 版本: {version_name}
📊 账号数量: {len(version_accounts)}个
⏰ 授权时长: {months}{time_unit_display}/每个账号
💰 总计金额: {total_money}元
------------------
确认批量授权？
[y] 确认授权
[n] 取消操作
=================="""
        sender.reply(confirm_msg)
        
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() not in ['y', 'yes', '是', 'Y']:
            sender.reply("✅ 已取消授权")
            return
        
        pay_success, pay_msg = process_payment(float(total_money), months, len(version_accounts))
        if not pay_success:
            sender.reply(f"❌ {pay_msg}")
            return
        
        if payment_mode == '天付':
            days = months
        else:
            days = months * 30
        
        success_count = 0
        fail_count = 0
        
        for account in version_accounts:
            try:
                full_ck = middleware.bucketGet('dd_ks_token', account)
                if not full_ck:
                    fail_count += 1
                    continue
                
                current_auth = middleware.bucketGet('dd_ks_auth', account)
                today = datetime.now().date()
                
                if current_auth and current_auth > str(today):
                    auth_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
                    new_auth_date = auth_date + timedelta(days=days)
                else:
                    new_auth_date = today + timedelta(days=days)
                
                new_auth = new_auth_date.strftime("%Y-%m-%d")
                
                middleware.bucketSet('dd_ks_auth', account, new_auth)
                
                token_info = parse_token(full_ck)
                name = token_info['name'] if token_info else account
                qinglong_value = token_to_qinglong_format(full_ck)
                Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
                
                success_count += 1
            except Exception as e:
                fail_count += 1
                print(f"授权账号 {account} 失败: {str(e)}")
        
        time_unit_display = '天' if payment_mode == '天付' else '月'
        result_msg = f"""
=====授权完成=====
{pay_msg}
------------------
📱 版本: {version_name}
📊 账号数量: {len(version_accounts)}个
✅ 成功: {success_count} 个
❌ 失败: {fail_count} 个
⏰ 授权时长: {months} {time_unit_display}
💰 支付金额: {total_money} 元
=================="""
        sender.reply(result_msg)
        
    else:
        account = version_accounts[choice_idx - 1]
        full_ck = middleware.bucketGet('dd_ks_token', account)
        
        if not full_ck:
            sender.reply("❌ 未找到账号信息")
            return
        
        token_info = parse_token(full_ck)
        name = token_info['name'] if token_info else '未知'
        auth_status = middleware.bucketGet('dd_ks_auth', account) or '未授权'
        
        account_info = f"""
=====账号详情=====
📱 账号: {name}
🆔 ID: {account}
🔐 授权: {auth_status}
📱 版本: {version_name}
==================
[1] 授权账号
[2] 删除账号
------------------
回复数字选择功能
回复 q 退出操作
=================="""
        sender.reply(account_info)
        
        action = sender.input(120000, 1, False)
        if not action:
            sender.reply("⏰ 操作超时,已退出")
            return
        elif action.lower() == 'q':
            sender.reply("✅ 已退出")
            return
        
        if action == '1':
            if payment_mode == '天付':
                time_unit = '天数'
                time_example = '30'
            else:
                time_unit = '月数'
                time_example = '1'
            
            auth_guide = f"""
=====设置授权时长=====
📱账号: {name}
📱版本: {version_name}
------------------
请输入授权{time_unit}(如:{time_example})
回复数字设置{time_unit}
回复 q 退出操作
=================="""
            sender.reply(auth_guide)
            
            months = sender.input(120000, 1, False)
            if not months:
                sender.reply("⏰ 操作超时,已退出")
                return
            elif months.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
            
            try:
                months = int(months)
                if months <= 0:
                    time_unit = '天数' if payment_mode == '天付' else '月数'
                    sender.reply(f"❌ 授权{time_unit}必须大于0")
                    return
            except:
                sender.reply("❌ 请输入正确的数字")
                return
            
            if payment_mode == '天付':
                unit_price = ksDaymoney
                time_unit = '天'
            else:
                unit_price = ksVipmoney
                time_unit = '月'
            
            money = Decimal(months) * unit_price
            
            confirm_msg = f"""
=====授权确认=====
📱 账号: {name}
📱 版本: {version_name}
⏰ 授权: {months}{time_unit}
💰 金额: {money}元
------------------
确认授权？
[y] 确认授权
[n] 取消操作
=================="""
            sender.reply(confirm_msg)
            
            confirm = sender.input(120000, 1, False)
            if not confirm or confirm.lower() not in ['y', 'yes', '是', 'Y']:
                sender.reply("✅ 已取消授权")
                return
            
            pay_success, pay_msg = process_payment(float(money), months, 1)
            if not pay_success:
                sender.reply(f"❌ {pay_msg}")
                return
            
            if payment_mode == '天付':
                days = months
            else:
                days = months * 30
            
            current_auth = middleware.bucketGet('dd_ks_auth', account)
            today = datetime.now().date()
            
            if current_auth and current_auth > str(today):
                auth_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
                new_auth_date = auth_date + timedelta(days=days)
            else:
                new_auth_date = today + timedelta(days=days)
            
            new_auth = new_auth_date.strftime("%Y-%m-%d")
            
            middleware.bucketSet('dd_ks_auth', account, new_auth)
            
            qinglong_value = token_to_qinglong_format(full_ck)
            Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
            
            result_msg = f"""
=====授权完成=====
{pay_msg}
------------------
📱 账号: {name}
📱 版本: {version_name}
⏰ 授权至: {new_auth}
💰 支付金额: {money}元
=================="""
            sender.reply(result_msg)
            
        elif action == '2':
            if payment_mode == '分成':
                debts = get_account_debts(account)
                if debts:
                    total_debt = sum(Decimal(str(d.get('share_amount', 0))) for d in debts) if debts else Decimal('0')
                    total_debt = float(total_debt.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
                    debt_details = "\n".join([f"  • {d.get('date')}: {d.get('share_amount')}元" for d in debts[:5]])
                    if len(debts) > 5:
                        debt_details += f"\n  ... 共{len(debts)}条欠款记录"
                    
                    sender.reply(f"""
=====无法删除=====
❌ 该账号存在未支付的分成欠款！

📝 欠款明细:
{debt_details}

💰 欠款总额: {total_debt}元
------------------
请先支付欠款后再删除账号
发送"快手分成"进行结算
==================""")
                    return
            
            confirm_msg = f"""
=====警告=====
确定要删除账号吗？
账号: {name}
此操作不可恢复！
------------------
[y] 确认删除
[n] 取消操作
=================="""
            sender.reply(confirm_msg)
            
            confirm = sender.input(120000, 1, False)
            if not confirm or confirm.lower() not in ['y', 'yes', '是', 'Y']:
                sender.reply("✅ 已取消删除")
                return
            
            accounts.remove(account)
            middleware.bucketDel('dd_ks_token', account)
            middleware.bucketDel('dd_ks_auth', account)
            
            if len(accounts) == 0:
                middleware.bucketDel('dd_ks_user', userid)
            else:
                middleware.bucketSet('dd_ks_user', userid, str(accounts))
            
            deleted_ql = False
            if payment_mode == '分成':
                if token_info and token_info.get('version') == '1':
                    deleted_ql = delete_account_in_qinglong(account, ks_fast_varname)
                elif token_info and token_info.get('version') == '2':
                    deleted_ql = delete_account_in_qinglong(account, ks_normal_varname)
                else:
                    deleted_ql = delete_account_in_qinglong(account, ks_fast_varname) or \
                                 delete_account_in_qinglong(account, ks_normal_varname)
            
            ql_status = "青龙变量已删除" if deleted_ql else ("青龙变量删除失败，请手动删除" if payment_mode == '分成' else "")
            
            sender.reply(f"""
=====删除成功=====
账号 {name} 已删除
{ql_status}
==================""")
        else:
            sender.reply("❌ 无效的选择")
            return

def push_notification(user, account, message):
    """推送消息到各个平台"""
    push_msg = f"""
=====快手账号通知=====
🆔 账号: {account}
📢 消息: {message}
=================="""
    
    platforms = ['wb', 'tg', 'qq', 'qb', 'wx']
    for platform in platforms:
        try:
            middleware.push(platform, '', user, '', push_msg)
        except:
            pass

def disable_account_in_qinlong(account, target_varname):
    """在青龙中禁用账号"""
    try:
        url = f"{QLurl}/open/envs"
        headers = {"Authorization": f"Bearer {qltoken}", "Content-Type": "application/json"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200 or resp.json()['code'] != 200:
            return False
        
        base_account = extract_base_account(account)
        
        qlid = None
        for env in resp.json()['data']:
            remarks = env.get('remarks', '')
            if target_varname == env['name'] and f'快手:{base_account}丨' in remarks:
                qlid = env['id']
                break
        
        if qlid:
            disable_url = f"{QLurl}/open/envs/disable"
            data = [qlid]
            resp = requests.put(disable_url, headers=headers, json=data, timeout=10)
            
            if resp.status_code == 200 and resp.json()['code'] == 200:
                return True
        
        return False
    except Exception as e:
        print(f"禁用账号失败: {str(e)}")
        return False

def delete_account_in_qinglong(account, target_varname):
    """在青龙中删除账号变量"""
    try:
        url = f"{QLurl}/open/envs"
        headers = {"Authorization": f"Bearer {qltoken}", "Content-Type": "application/json"}
        
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200 or resp.json()['code'] != 200:
            return False
        
        base_account = extract_base_account(account)
        
        qlid = None
        for env in resp.json()['data']:
            remarks = env.get('remarks', '')
            if target_varname == env['name'] and f'快手:{base_account}丨' in remarks:
                qlid = env['id']
                break
        
        if qlid:
            delete_url = f"{QLurl}/open/envs"
            resp = requests.delete(delete_url, headers=headers, json=[qlid], timeout=10)
            
            if resp.status_code == 200 and resp.json()['code'] == 200:
                return True
        
        return False
    except Exception as e:
        print(f"删除青龙变量失败: {str(e)}")
        return False

def check_auth_expiry():
    """定时检查授权到期状态（每天10点执行）"""
    if payment_mode not in ['月付', '天付']:
        return
    
    current_hour = datetime.now().hour
    if current_hour != 10:
        return
    
    all_users = middleware.bucketAllKeys('dd_ks_user')
    if not all_users:
        return
    
    today = str(datetime.now().date())
    expired_count = 0
    notified_count = 0
    
    for user in all_users:
        try:
            accountlist = middleware.bucketGet('dd_ks_user', user)
            if not accountlist:
                continue
            
            accounts = eval(accountlist)
            if isinstance(accounts, str):
                accounts = [accounts]
            
            user_expired_accounts = []
            
            for account in accounts:
                try:
                    auth_date = middleware.bucketGet('dd_ks_auth', account)
                    
                    if auth_date and auth_date <= today:
                        full_ck = middleware.bucketGet('dd_ks_token', account)
                        if full_ck:
                            token_info = parse_token(full_ck)
                            name = token_info['name'] if token_info else account
                            version = token_info.get('version', '1') if token_info else '1'
                            version_name = '极速版' if version == '1' else '普通版'
                            
                            disabled_fast = disable_account_in_qinlong(account, ks_fast_varname)
                            disabled_normal = disable_account_in_qinlong(account, ks_normal_varname)
                            
                            if disabled_fast or disabled_normal:
                                expired_count += 1
                                user_expired_accounts.append({
                                    'name': name,
                                    'version': version_name,
                                    'auth_date': auth_date
                                })
                except Exception as e:
                    print(f"处理账号 {account} 时出错: {str(e)}")
                    continue
            
            if user_expired_accounts:
                mode_name = '月付' if payment_mode == '月付' else '天付'
                account_details = ''.join([
                    f"  • {acc['name']}({acc['version']}) - 到期日:{acc['auth_date']}"
                    for acc in user_expired_accounts
                ])
                
                notification = f"""
⚠️ 授权到期通知
------------------
💳 模式: {mode_name}
📅 检测日期: {today}
🔒 已停用账号: {len(user_expired_accounts)}个

{account_details}
------------------
💡 您的账号授权已到期，青龙变量已自动停用
📝 请及时续费以继续使用服务

续费方式: 发送 快手管理 进行续费操作
------------------
提示: 续费后账号将自动恢复运行"""
                
                push_notification(user, "授权到期", notification)
                notified_count += 1
        
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    
    if expired_count > 0:
        log_msg = f"""
=====授权到期检测完成=====
检测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
支付模式: {payment_mode}
------------------
已停用账号: {expired_count}个
通知用户: {notified_count}个
=================="""
        print(log_msg)

def check_share_payment_status():
    """定时检查分成支付状态（每天8点和22点执行）"""
    if payment_mode != '分成':
        return
    
    all_users = middleware.bucketAllKeys('dd_ks_user')
    if not all_users:
        return
    
    today = str(datetime.now().date())
    yesterday = str((datetime.now() - timedelta(days=1)).date())
    current_hour = datetime.now().hour
    
    is_morning_check = (current_hour == 8)
    is_evening_check = (current_hour == 22)
    
    notify_count = 0
    disable_count = 0
    
    for user in all_users:
        try:
            accountlist = middleware.bucketGet('dd_ks_user', user)
            if not accountlist:
                continue
            
            accounts = eval(accountlist)
            if isinstance(accounts, str):
                accounts = [accounts]
            
            for account in accounts:
                try:
                    if is_morning_check:
                        total_debt = get_total_debt_amount(account)
                        
                        if total_debt > 0:
                            full_ck = middleware.bucketGet('dd_ks_token', account)
                            if full_ck:
                                token_info = parse_token(full_ck)
                                name = token_info['name'] if token_info else account
                                
                                disabled_fast = disable_account_in_qinlong(account, ks_fast_varname)
                                disabled_normal = disable_account_in_qinlong(account, ks_normal_varname)
                                
                                if disabled_fast or disabled_normal:
                                    disable_count += 1
                                    
                                    push_notification(user, name, f"""
⚠️ 账号已停用
------------------
❌ 存在未支付分成: {total_debt}元
📅 停用日期: {today}
💡 请及时支付分成后联系管理员恢复
------------------
提示: 支付完成后请联系管理员
手动启用青龙环境变量""")
                    
                    elif is_evening_check:
                        today_key = f"share_{account}_{today}"
                        today_data = middleware.bucketGet('dd_ks_share', today_key)
                        
                        today_paid = False
                        if today_data:
                            try:
                                data = json.loads(today_data)
                                today_paid = data.get('is_paid', False)
                            except:
                                pass
                        
                        if not today_paid:
                            full_ck = middleware.bucketGet('dd_ks_token', account)
                            if full_ck:
                                token_info = parse_token(full_ck)
                                name = token_info['name'] if token_info else account
                                
                                cookie = token_info['cookie'] if token_info else None
                                proxy_info = token_info['proxy'] if token_info else None
                                
                                if cookie:
                                    version = token_info.get('version', '1')
                                    
                                    if version == '1':
                                        query_result = query_account_fast(cookie, proxy_info)
                                        if query_result.get('success'):
                                            all_coin_records = query_result.get('allCoinRecords', [])
                                            today_coins = calculate_today_coins_fast(all_coin_records)
                                            
                                            if today_coins > 0:
                                                today_revenue = round(today_coins / 10000, 2)
                                                share_amount = calculate_share_amount(today_revenue, share_rate)
                                                
                                                save_share_record(account, today_revenue, share_amount, is_paid=False, coins=today_coins)
                                                
                                                push_notification(user, name, f"""
📊 今日分成提醒
------------------
🪙 今日金币: {int(today_coins)}个
💰 折合现金: {today_revenue}元
📈 分成比例: {share_rate}%
💵 应付金额: {share_amount}元
------------------
💡 请发送"快手分成"进行结算
⚠️ 未支付将在明日早上8点停用账号
------------------
温馨提示: 请在今晚23:59前完成支付""")
                                                notify_count += 1
                                    else:
                                        query_result = query_account_normal(cookie, proxy_info)
                                        if query_result.get('success'):
                                            all_coin_records = query_result.get('allCoinRecords', [])
                                            today_coins = calculate_today_coins_normal(all_coin_records)
                                            
                                            if today_coins > 0:
                                                today_revenue = round(today_coins / 10000, 2)
                                                share_amount = calculate_share_amount(today_revenue, share_rate)
                                                
                                                save_share_record(account, today_revenue, share_amount, is_paid=False, coins=today_coins)
                                                
                                                push_notification(user, name, f"""
📊 今日分成提醒
------------------
🪙 今日金币: {int(today_coins)}个
💰 折合现金: {today_revenue}元
📈 分成比例: {share_rate}%
💵 应付金额: {share_amount}元
------------------
💡 请发送"快手分成"进行结算
⚠️ 未支付将在明日早上8点停用账号
------------------
温馨提示: 请在今晚23:59前完成支付""")  
                                                notify_count += 1
                    
                except Exception as e:
                    print(f"处理账号 {account} 失败: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"处理用户 {user} 失败: {str(e)}")
            continue
    
    if notify_count > 0 or disable_count > 0:
        check_type = "早上检查" if is_morning_check else "晚上检查"
        log_msg = f"""
=====分成{check_type}完成=====
📅 日期: {today}
⏰ 时间: {datetime.now().strftime("%H:%M:%S")}
📢 提醒: {notify_count}个账号
🚫 停用: {disable_count}个账号
=================="""
        print(log_msg)

def handle_share_payment():
    """处理分成支付"""
    if payment_mode != '分成':
        sender.reply("❌ 未启用分成模式")
        return
    
    if not uservalue or len(uservalue) == 0:
        sender.reply("❌ 您还没有绑定任何账号\n请先发送 快手登录 进行账号绑定")
        return
    
    accounts = eval(uservalue)
    
    version_menu = """
=====选择快手版本=====
请选择要结算的版本
------------------
[1] 某手极速版
[2] 某手普通版
------------------
回复数字选择版本
回复 q 退出操作
=================="""
    sender.reply(version_menu)
    
    version_choice = sender.input(120000, 1, False)
    if not version_choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif version_choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    if version_choice not in ['1', '2']:
        sender.reply("❌ 无效的选择")
        return
    
    version_name = "某手极速版" if version_choice == '1' else "某手普通版"
    
    version_accounts = []
    for account in accounts:
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            if token_info and token_info['version'] == version_choice:
                version_accounts.append(account)
    
    if not version_accounts:
        sender.reply(f"❌ 您还没有绑定任何{version_name}账号")
        return
    
    account_list = f"""
====={version_name}分成结算=====
请选择要结算的账号
------------------
"""
    
    for idx, account in enumerate(version_accounts, 1):
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            name = token_info['name'] if token_info else '未知'
            is_paid, revenue, share_amount = get_today_share_status(account)
            
            debts = get_account_debts(account)
            total_debt = sum(Decimal(str(d.get('share_amount', 0))) for d in debts) if debts else Decimal('0')
            total_debt = float(total_debt.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
            
            if is_paid and total_debt == 0:
                status = f"✅ 已结清"
            elif is_paid and total_debt > 0:
                status = f"⚠️ 今日已付，历史欠款{total_debt}元"
            elif total_debt > 0:
                status = f"❌ 欠款{total_debt}元"
            else:
                status = "⏳ 待支付"
            
            account_list += f"[{idx}] {name}\n    状态: {status}\n------------------\n"
        else:
            account_list += f"[{idx}] ID: {account}\n    状态: 未知\n------------------\n"
    
    account_list += "回复数字选择账号\n回复 0 批量支付所有欠款\n回复 q 退出操作\n=================="
    sender.reply(account_list)
    
    choice = sender.input(120000, 1, False)
    if not choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    try:
        choice_idx = int(choice)
        if choice_idx < 0 or choice_idx > len(version_accounts):
            sender.reply(f"❌ 请输入 0-{len(version_accounts)} 之间的数字")
            return
    except:
        sender.reply("❌ 请输入正确的数字")
        return
    
    if choice_idx == 0:
        total_debt = Decimal('0')
        debt_accounts = []
        
        for account in version_accounts:
            debts = get_account_debts(account)
            if debts:
                account_debt = sum(Decimal(str(d.get('share_amount', 0))) for d in debts)
                debt_accounts.append((account, debts, float(account_debt.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))))
                total_debt += account_debt
        
        total_debt = float(total_debt.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
        
        if not debt_accounts:
            sender.reply("✅ 所有账号均无欠款")
            return
        
        debt_detail = ""
        for account, debts, amount in debt_accounts:
            full_ck = middleware.bucketGet('dd_ks_token', account)
            name = '未知'
            if full_ck:
                token_info = parse_token(full_ck)
                name = token_info['name'] if token_info else '未知'
            debt_detail += f"  • {name}: {amount}元 ({len(debts)}笔)\n"
        
        confirm_msg = f"""
=====批量欠款支付=====
待支付账号数: {len(debt_accounts)}个
------------------
{debt_detail}------------------
💰 总欠款金额: {total_debt}元
------------------
确认批量支付？
[y] 确认支付
[n] 取消操作
=================="""
        sender.reply(confirm_msg)
        
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() not in ['y', 'yes', '是', 'Y']:
            sender.reply("✅ 已取消支付")
            return
        
        pay_success, pay_msg = process_payment(total_debt, 0, 1)
        if not pay_success:
            sender.reply(f"❌ {pay_msg}")
            return
        
        cleared_count = 0
        for account, debts, _ in debt_accounts:
            for debt in debts:
                debt_date = debt.get('date')
                if debt_date:
                    remove_share_debt(account, debt_date)
                    save_share_record(account, debt.get('revenue', 0), debt.get('share_amount', 0), is_paid=True)
                    cleared_count += 1
        
        sender.reply(f"""
=====批量支付完成=====
{pay_msg}
------------------
✅ 已支付账号: {len(debt_accounts)}个
📝 已清除欠款: {cleared_count}笔
💰 总金额: {total_debt}元
==================""")
        return
    
    account = version_accounts[choice_idx - 1]
    
    full_ck = middleware.bucketGet('dd_ks_token', account)
    if not full_ck:
        sender.reply("❌ 未找到账号信息")
        return
    
    token_info = parse_token(full_ck)
    name = token_info['name'] if token_info else '未知'
    
    debts = get_account_debts(account)
    total_debt = sum(Decimal(str(d.get('share_amount', 0))) for d in debts) if debts else Decimal('0')
    total_debt = float(total_debt.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))
    
    if total_debt > 0:
        debt_details = "\n".join([f"  • {d.get('date')}: {d.get('share_amount')}元" for d in debts])
        
        confirm_msg = f"""
=====账号欠款支付=====
📝 账号: {name}
------------------
📋 欠款明细:
{debt_details}
------------------
💰 欠款总额: {total_debt}元
------------------
确认支付所有欠款？
[y] 确认支付
[n] 取消操作
=================="""
        sender.reply(confirm_msg)
        
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() not in ['y', 'yes', '是', 'Y']:
            sender.reply("✅ 已取消支付")
            return
        
        pay_success, pay_msg = process_payment(total_debt, 0, 1)
        if not pay_success:
            sender.reply(f"❌ {pay_msg}")
            return
        
        for debt in debts:
            debt_date = debt.get('date')
            if debt_date:
                remove_share_debt(account, debt_date)
                save_share_record(account, debt.get('revenue', 0), debt.get('share_amount', 0), is_paid=True)
        
        sender.reply(f"""
=====支付完成=====
{pay_msg}
------------------
📝 账号: {name}
📋 已清除欠款: {len(debts)}笔
💰 支付金额: {total_debt}元
==================""")
    else:
        is_authorized, msg = check_share_authorization(account, version_choice)
        
        if is_authorized:
            sender.reply(f"✅ {msg}")
            return
        
        sender.reply(f"📊 {msg}")
        
        is_paid, revenue, share_amount = get_today_share_status(account)
        
        if revenue <= 0:
            sender.reply("❌ 今日暂无收益，无需支付")
            return
        
        today_coins = None
        if token_info and token_info['cookie']:
            cookie = token_info['cookie']
            proxy_info = token_info['proxy']
            
            if version_choice == '1':
                query_result = query_account_fast(cookie, proxy_info)
            else:
                query_result = query_account_normal(cookie, proxy_info)
            
            if query_result.get('success'):
                today_coins = float(query_result.get('coinBalance', 0))
                manual_cash = detect_manual_cash_exchange(query_result.get('cashRecords', []))
                if manual_cash > 0:
                    revenue = revenue + manual_cash

        success, result_msg = process_share_payment(account, revenue, share_rate, today_coins)
        
        if success:
            sender.reply(f"✅ {result_msg}")
        else:
            sender.reply(f"❌ {result_msg}")

def handle_withdraw():
    """快手提现(精简版)"""
    if not uservalue: return sender.reply("❌ 未绑定账号")
    accs = eval(uservalue)
    fa = [a for a in accs if middleware.bucketGet('dd_ks_token', a) and parse_token(middleware.bucketGet('dd_ks_token', a)).get('version') == '1']
    if not fa: return sender.reply("❌ 无极速版账号")
    
    lst = "=====极速版提现=====\n[0] 批量提现\n"
    for i, a in enumerate(fa, 1):
        tk = middleware.bucketGet('dd_ks_token', a)
        n = parse_token(tk)['name'] if tk else a
        lst += f"[{i}] {n}\n"
    sender.reply(lst + "回复数字选择")
    
    c = sender.input(120000, 1, False)
    if not c or c.lower() == 'q': return sender.reply("已退出")
    try: ci = int(c)
    except: return sender.reply("❌ 无效")
    if ci < 0 or ci > len(fa): return sender.reply("❌ 无效")
    
    sender.reply("[1]微信 [2]支付宝")
    cc = sender.input(60000, 1, False)
    ch, cn = ("WECHAT", "微信") if cc == '1' else ("ALIPAY", "支付宝") if cc == '2' else (None, None)
    if not ch: return sender.reply("❌ 无效")
    
    sender.reply("[1]0.5元 [2]10元 [3]15元 [4]20元 [5]30元 [6]50元")
    ac = sender.input(60000, 1, False)
    am = {'1': 0.5, '2': 10, '3': 15, '4': 20, '5': 30, '6': 50}.get(ac)
    if not am: return sender.reply("❌ 无效")
    
    tas = fa if ci == 0 else [fa[ci - 1]]
    sc, fc = 0, 0
    for a in tas:
        tk = middleware.bucketGet('dd_ks_token', a)
        ti = parse_token(tk) if tk else None
        if not ti: fc += 1; continue
        success, msg = auto_withdraw(ti['cookie'], am)
        if success: sc += 1; sender.reply(f"✅ {ti['name']} {msg}")
        else: fc += 1; sender.reply(f"❌ {ti['name']} {msg}")
    sender.reply(f"提现完成: 成功{sc}个 失败{fc}个")

def withdraw_query(cookie):
    """查询提现额度信息"""
    url = "https://nebula.kuaishou.com/rest/n/nebula/account/withdraw"
    headers = {
        "Connection": "keep-alive",
        "cookie": cookie,
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            resp = response.json()
            if resp.get('result') == 1:
                return resp
        return None
    except Exception as e:
        return None

def withdraw_info(cookie):
    """绑定信息查询，返回 provider 列表"""
    url = "https://www.kuaishoupay.com/pay/account/h5/withdraw/withdraw_info"
    headers = {
        "cookie": cookie,
    }
    data = {
        "account_group_key": "NEBULA_CASH_ACCOUNT",
        "providers": "",
        "bind_page_type": "3",
        "source": "COMMON_WITHDRAW_PAGE",
        "amount": "300"
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            resp = json.loads(response.text)
            if resp.get('code') == "SUCCESS":
                providers = resp.get("withdraw_provider_infos", [])
                ticket = resp.get("ticket", "")
                return providers, ticket
        return [], ""
    except Exception as e:
        return [], ""

def withdraw_apply(cookie, fen, biz_content, provider="WECHAT", bank_id="", bank_token="", ticket=""):
    """提现申请"""
    url = "https://www.kuaishoupay.com/pay/account/h5/withdraw/apply"
    headers = {
        "cookie": cookie,
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    
    if isinstance(biz_content, dict):
        biz_content_str = json.dumps(biz_content, ensure_ascii=False, separators=(",", ":"))
    else:
        biz_content_str = str(biz_content)

    data = {
        "account_group_key": "NEBULA_CASH_ACCOUNT",
        "mobile_code": "",
        "fen": fen,
        "provider": provider,
        "total_fen": fen,
        "commission_fen": "0",
        "third_account": provider,
        "attach": "",
        "biz_content": biz_content_str,
        "session_id": "",
        "bank_id": bank_id,
        "bank_token": bank_token,
        "skip_show_third_bind_info": "false",
        "agree_sign_policy": "false",
        "ticket": ticket
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            resp = json.loads(response.text)
            if resp.get('code') == "SUCCESS":
                return True, resp.get('msg', '提现成功')
            else:
                return False, resp.get('msg', response.text)
        return False, f"HTTP请求失败: {response.status_code}"
    except Exception as e:
        return False, f"请求异常: {str(e)}"

def auto_withdraw(cookie, target_amount=None):
    """自动提现
    
    Args:
        cookie: 用户cookie
        target_amount: 目标提现金额，None表示自动匹配最高档位
    
    Returns:
        (success, message)
    """
    withdraw_resp = withdraw_query(cookie)
    if not withdraw_resp:
        return False, "查询提现额度失败"
    
    data = withdraw_resp.get("data", {})
    try:
        en_withdraw_amount = float(str(data.get("enWithdrawAmount", "0") or "0"))
        en_withdraw_list = [float(x) for x in data.get("enWithdrawList", [])]
        
        if target_amount is not None:
            if target_amount not in en_withdraw_list or target_amount > en_withdraw_amount:
                return False, f"金额 {target_amount} 元不可用或余额不足"
            final_amount = target_amount
        else:
            candidates = [x for x in en_withdraw_list if x <= en_withdraw_amount]
            if not candidates:
                return False, "余额不足或无可提现档位"
            final_amount = max(candidates)
        
        withdraw_list = data.get("withdrawList", [])
        target_item = None
        for item in withdraw_list:
            try:
                if float(str(item.get("amount", "0"))) == final_amount and not item.get("disabled", False):
                    target_item = item
                    break
            except Exception:
                continue
        
        if not target_item:
            return False, "未找到匹配的提现档位"
        
        biz_content_raw = target_item.get("bizContent")
        biz_content = biz_content_raw if isinstance(biz_content_raw, str) else (biz_content_raw or {})
        fen = str(int(round(final_amount * 100)))
        
    except Exception as e:
        return False, f"处理提现数据失败: {str(e)}"
    
    providers, ticket = withdraw_info(cookie)
    if not providers:
        return False, "绑定信息查询失败"
    
    provider_map = {p.get("provider"): p for p in providers}

    priority = ["WECHAT", "ALIPAY", "UNION_PAY_BANK"]
    
    provider_icon_map = {
        "WECHAT": "💚微信",
        "ALIPAY": "💙支付宝", 
        "UNION_PAY_BANK": "💳银行卡"
    }

    for provider in priority:
        cfg = provider_map.get(provider)
        if not cfg:
            continue
        
        if not cfg.get("has_bind", False) and provider != "UNION_PAY_BANK":
            continue
        
        if provider == "UNION_PAY_BANK" and not cfg.get("has_bind", False):
            continue

        bank_id = cfg.get("bank_bind_infos", [{}])[0].get("bank_id", "") if provider == "UNION_PAY_BANK" else ""
        bank_token = cfg.get("bank_bind_infos", [{}])[0].get("bank_token", "") if provider == "UNION_PAY_BANK" else ""
        
        provider_icon = provider_icon_map.get(provider, provider)
        
        success, msg = withdraw_apply(cookie, fen=fen, biz_content=biz_content, provider=provider, 
                                      bank_id=bank_id, bank_token=bank_token, ticket=ticket)
        if success:
            return True, f"{provider_icon} 提现 {final_amount} 元成功"
    
    return False, "所有可用渠道均提现失败或未绑定"

def admin_panel():
    """快手后台管理"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限访问后台")
        return
    sender.reply(msg_box("快手后台", "[1] 授权管理\n[2] 分成统计\n[3] 清理账号\n[4] 删除用户账号\n[5] 释放支付锁", "回复数字选择"))
    c = sender.input(60000, 1, False)
    if c == '1': admin_authorization()
    elif c == '2': admin_share_statistics()
    elif c == '3': admin_clean_accounts()
    elif c == '4': admin_delete_user_account()
    elif c == '5': admin_release_payment_lock()
    else: sender.reply("已退出")

def admin_authorization():
    """快手授权管理(精简版)"""
    sender.reply(msg_box("选择版本", "[1] 极速版 [2] 普通版", "回复数字"))
    vc = sender.input(60000, 1, False)
    if vc not in ['1', '2']: return sender.reply("已退出")
    vn, tv = ("极速版", ks_fast_varname) if vc == '1' else ("普通版", ks_normal_varname)
    
    sender.reply(msg_box(f"{vn}授权", "[1] 一键授权\n[2] 单独授权", "回复数字"))
    c = sender.input(60000, 1, False)
    if c not in ['1', '2']: return sender.reply("已退出")
    
    if payment_mode == '天付':
        sender.reply("请输入授权天数:")
        mi = sender.input(60000, 1, False)
        try: months = int(mi)
        except: return sender.reply("❌ 天数无效")
    else:
        sender.reply("请输入授权月数:")
        mi = sender.input(60000, 1, False)
        try: months = int(mi)
        except: return sender.reply("❌ 月数无效")
    if months <= 0: return sender.reply("❌ 月数需>0")
    
    if payment_mode == '天付':
        days = months
    else:
        days = months * 30
    
    users = middleware.bucketAllKeys('dd_ks_user') if c == '1' else None
    
    if c == '2':
        sender.reply("请输入用户ID:")
        uid = sender.input(60000, 1, False)
        if not uid: return sender.reply("已退出")
        al = middleware.bucketGet('dd_ks_user', uid)
        if not al: return sender.reply(f"❌ 未找到用户{uid}")
        users = [uid]
    
    if not users: return sender.reply("❌ 无用户")
    
    sc, fc = 0, 0
    for u in users:
        al = middleware.bucketGet('dd_ks_user', u)
        if not al: continue
        try:
            accs = eval(al) if isinstance(eval(al), list) else [eval(al)]
            for acc in accs:
                tk = middleware.bucketGet('dd_ks_token', acc)
                if not tk: fc += 1; continue
                ti = parse_token(tk)
                if not ti or ti['version'] != vc: continue
                ca = middleware.bucketGet('dd_ks_auth', acc)
                td = datetime.now().date()
                nad = (datetime.strptime(ca, "%Y-%m-%d").date() if ca and ca > str(td) else td) + timedelta(days=days)
                middleware.bucketSet('dd_ks_auth', acc, str(nad))
                try: Addenvs(osname=tv, value=token_to_qinglong_format(tk), account=acc, phone=ti['name'])
                except: pass
                sc += 1
        except: fc += 1
    time_unit_display = '天' if payment_mode == '天付' else '月'
    sender.reply(f"✅授权完成: 成功{sc}个, 失败{fc}个, 授权{months}{time_unit_display}")

def admin_share_statistics():
    """分成统计(精简版)"""
    if payment_mode != '分成': return sender.reply("❌ 未启用分成模式")
    today = str(datetime.now().date())
    users = middleware.bucketAllKeys('dd_ks_user')
    if not users: return sender.reply("❌ 无用户")
    
    pc, uc, tr, ts = 0, 0, 0.0, 0.0
    for u in users:
        try:
            al = middleware.bucketGet('dd_ks_user', u)
            if not al: continue
            accs = eval(al) if isinstance(eval(al), list) else [eval(al)]
            for acc in accs:
                d = middleware.bucketGet('dd_ks_share', f"share_{acc}_{today}")
                if d:
                    try:
                        data = json.loads(d)
                        if data.get('is_paid'): pc += 1; tr += float(data.get('revenue', 0)); ts += float(data.get('share_amount', 0))
                        else: uc += 1
                    except: pass
        except: continue
    sender.reply(f"📊今日分成统计({today})\n比例:{share_rate}%\n总收益:{tr:.2f}元 总分成:{ts:.2f}元\n已结算:{pc}个 未结算:{uc}个")

def admin_clean_accounts():
    """清理过期账号(精简版)"""
    users = middleware.bucketAllKeys('dd_ks_user')
    if not users: return sender.reply("❌ 无账号")
    sender.reply(f"🔄 清理中...共{len(users)}个用户")
    cc, today = 0, str(datetime.now().date())
    for u in users:
        try:
            al = middleware.bucketGet('dd_ks_user', u)
            if not al: continue
            accs = eval(al) if isinstance(eval(al), list) else [eval(al)]
            va = []
            for acc in accs:
                auth = middleware.bucketGet('dd_ks_auth', acc)
                if not auth or auth <= today:
                    try: disable_account_in_qinlong(acc, ks_fast_varname); disable_account_in_qinlong(acc, ks_normal_varname)
                    except: pass
                    middleware.bucketDel('dd_ks_token', acc); middleware.bucketDel('dd_ks_auth', acc); cc += 1
                else: va.append(acc)
            if va: middleware.bucketSet('dd_ks_user', u, str(list(dict.fromkeys(va))))
            else: middleware.bucketDel('dd_ks_user', u)
        except: continue
    sender.reply(f"✅清理完成: 已清理{cc}个账号")

def admin_delete_user_account():
    """管理员删除用户账号(用于处理主动结算未通过插件导致的账号无法删除问题)"""
    sender.reply("请输入用户ID:")
    uid = sender.input(60000, 1, False)
    if not uid or uid.lower() == 'q': return sender.reply("已退出")
    
    al = middleware.bucketGet('dd_ks_user', uid)
    if not al: return sender.reply(f"❌ 未找到用户{uid}")
    
    try:
        accs = eval(al) if isinstance(eval(al), list) else [eval(al)]
    except:
        return sender.reply("❌ 账号数据格式错误")
    
    if not accs: return sender.reply("❌ 该用户无账号")
    
    sender.reply(msg_box("选择版本", "[1] 极速版 [2] 普通版", "回复数字"))
    vc = sender.input(60000, 1, False)
    if vc not in ['1', '2']: return sender.reply("已退出")
    vn, tv = ("极速版", ks_fast_varname) if vc == '1' else ("普通版", ks_normal_varname)
    
    version_accs = []
    for acc in accs:
        tk = middleware.bucketGet('dd_ks_token', acc)
        if tk:
            ti = parse_token(tk)
            if ti and ti['version'] == vc:
                version_accs.append((acc, ti['name']))
    
    if not version_accs: return sender.reply(f"❌ 该用户无{vn}账号")
    
    lst = f"====={vn}账号列表=====\n用户ID: {uid}\n------------------\n"
    for i, (acc, name) in enumerate(version_accs, 1):
        lst += f"[{i}] {name} (ID:{acc})\n"
    lst += "------------------\n回复数字选择要删除的账号\n回复 q 退出\n=================="
    sender.reply(lst)
    
    c = sender.input(60000, 1, False)
    if not c or c.lower() == 'q': return sender.reply("已退出")
    
    try:
        ci = int(c)
        if ci < 1 or ci > len(version_accs): return sender.reply("❌ 无效选择")
    except:
        return sender.reply("❌ 请输入数字")
    
    acc, name = version_accs[ci - 1]
    
    sender.reply(msg_box("确认删除", f"账号: {name}\nID: {acc}\n用户: {uid}\n\n此操作将强制删除账号\n不检查分成欠款！", "[y] 确认删除 [n] 取消"))
    confirm = sender.input(60000, 1, False)
    if not confirm or confirm.lower() not in ['y', 'yes', '是']: return sender.reply("✅ 已取消删除")
    
    try:
        accs.remove(acc)
        
        middleware.bucketDel('dd_ks_token', acc)
        middleware.bucketDel('dd_ks_auth', acc)
        
        share_count = 0
        for i in range(30):
            check_date = str(datetime.now().date() - timedelta(days=i))
            share_key = f"share_{acc}_{check_date}"
            if middleware.bucketGet('dd_ks_share', share_key):
                middleware.bucketDel('dd_ks_share', share_key)
                share_count += 1
        
        debt_count = 0
        ks_uid = get_ks_uid_from_account(acc)
        if ks_uid:
            for i in range(30):
                check_date = str(datetime.now().date() - timedelta(days=i))
                debt_key = f"debt_{ks_uid}_{check_date}"
                if middleware.bucketGet('dd_ks_debt', debt_key):
                    middleware.bucketDel('dd_ks_debt', debt_key)
                    debt_count += 1
        
        deleted_ql = delete_account_in_qinglong(acc, tv)
        
        if accs:
            middleware.bucketSet('dd_ks_user', uid, str(accs))
        else:
            middleware.bucketDel('dd_ks_user', uid)
        
        ql_msg = "✅ 青龙变量已删除" if deleted_ql else "⚠️ 青龙变量删除失败，请手动删除"
        share_msg = f"\n✅ 已删除{share_count}条分成记录" if share_count > 0 else ""
        debt_msg = f"\n✅ 已删除{debt_count}条欠款记录" if debt_count > 0 else ""
        sender.reply(f"✅ 删除成功\n账号: {name}\nID: {acc}\n用户: {uid}\n{ql_msg}{share_msg}{debt_msg}")
    except Exception as e:
        sender.reply(f"❌ 删除失败: {str(e)}")

def admin_release_payment_lock():
    """管理员释放支付锁"""
    is_locked, lock_user, remaining = check_payment_lock_status()
    
    if not is_locked:
        sender.reply(msg_box("支付锁状态", "✅ 当前没有活动的支付锁", ""))
        return
    
    lock_info = f"""
=====支付锁信息=====
🔒 锁定状态: 已锁定
👤 锁定用户: {lock_user}
⏰ 剩余时间: {remaining}秒
------------------
是否释放支付锁？
[y] 确认释放
[n] 取消操作
=================="""
    sender.reply(lock_info)
    
    confirm = sender.input(60000, 1, False)
    if not confirm or confirm.lower() not in ['y', 'yes', '是']:
        sender.reply("✅ 已取消操作")
        return
    
    if release_payment_lock():
        sender.reply(msg_box("释放成功", "✅ 支付锁已成功释放\n其他用户现在可以进行支付了", ""))
    else:
        sender.reply(msg_box("释放失败", "❌ 释放支付锁失败\n请稍后重试", ""))

def main():
    """主函数"""
    global ks_fast_varname, ks_normal_varname, allow_proxy, dd_ks_qlname, QLurl, qltoken, today_time
    global payment_mode, ksVipmoney, ksDaymoney, kscoin, share_rate, share_allow_coin_pay
    
    ks_fast_varname, ks_normal_varname, allow_proxy, dd_ks_qlname, dd_managecommand, dd_querycommand, dd_signcommand, \
    payment_mode, ksVipmoney, ksDaymoney, kscoin, use_ma_pay, share_rate, share_allow_coin_pay = getusercontent()
    
    QLurl, qltoken = seekql()
    today_time = str(datetime.now().date())
    msg = sender.getMessage()
    
    imtype = sender.getImtype()
    if imtype == 'fake':
        check_share_payment_status()
        check_auth_expiry()
        return
    
    if '登录' in msg or '登陆' in msg:
        bindaccount()
    elif '查询' in msg:
        query_accounts()
    elif '管理' in msg:
        manage_accounts()
    elif '分成' in msg:
        handle_share_payment()
    elif '后台' in msg:
        admin_panel()
    elif '提现' in msg:
        handle_withdraw()
    elif '教程' in msg:
        sender.reply("📚快手教程\n• 快手登录-绑定账号\n• 快手查询-查询收益\n• 快手管理-账号授权\n• 快手提现-极速版提现\n• 快手分成-分成结算\n格式:备注#Cookie#Salt#代理\n代理:IP|端口|用户名|密码|过期时间")
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()