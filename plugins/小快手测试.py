# [rule: ^快手登录$|^快手登陆$|^快手查询$|^快手管理$|^快手教程$|^快手后台$|^快手分成$]
# [cron: 0 0 8,21 * * *]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [public: true]
# [title: 小快手测试]
# [icon: http://5b0988e595225.cdn.sohucs.com/images/20190724/f8f8ace898584a2dbd3f20c2d2822c96.jpeg]
# [open_source: false]
# [class: 工具类]
# [version: 5.0]
# [price: 18.88]
# [admin: false]
# [author: linzixu]
# [service: 2661320550]
# [description: 小快手V5.0重构<br>支持极速版和普通版一键提交<br>格式：备注#cookie#salt#代理信息]

import re
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal
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
# [param: {"required":true,"key":"dd_ks.ksVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_ks.kscoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_ks.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# [param: {"required":false,"key":"dd_ks.use_share_mode","bool":true,"placeholder":"","name":"使用分成模式","desc":"开启后用户按日结算分成，无需月付授权"}]
# [param: {"required":true,"key":"dd_ks.share_rate","bool":false,"placeholder":"例:55,表示55分成","name":"分成比例","desc":"分成比例（0-100），例如55表示平台收取55%"}]

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
    
    ksVipmoney = Decimal(middleware.bucketGet('dd_ks', 'ksVipmoney') or '1')
    kscoin = int(middleware.bucketGet('dd_ks', 'kscoin') or '0')
    
    use_ma_pay = middleware.bucketGet('dd_ks', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    # 分成模式配置
    use_share_mode = middleware.bucketGet('dd_ks', 'use_share_mode') or 'false'
    use_share_mode = use_share_mode.lower() == 'true'
    share_rate = int(middleware.bucketGet('dd_ks', 'share_rate') or '55')
    
    return (ks_fast_varname, ks_normal_varname, allow_proxy, dd_ks_qlname, 
            dd_managecommand, dd_querycommand, dd_signcommand,
            ksVipmoney, kscoin, use_ma_pay, use_share_mode, share_rate)

def verify_account_fast(cookie_str):
    """验证极速版账号有效性"""
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
            # 如果接口返回的昵称为空，使用备注名称
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

def parse_token(full_ck):
    """
    解析token字符串
    新格式: 版本#备注#cookie#salt#代理
    旧格式: 备注#cookie#salt#代理
    
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
    
    # 判断是新格式还是旧格式
    # 新格式第一个字段是版本号(1或2)，旧格式第一个字段是备注
    if len(parts) >= 4 and parts[0] in ['1', '2']:
        # 新格式: 版本#备注#cookie#salt#代理
        return {
            'version': parts[0],
            'name': parts[1] if len(parts) >= 2 else '未知',
            'cookie': parts[2] if len(parts) >= 3 else None,
            'salt': parts[3] if len(parts) >= 4 else None,
            'proxy': parts[4] if len(parts) >= 5 else None
        }
    else:
        # 旧格式: 备注#cookie#salt#代理 (默认为极速版)
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
    新格式: 版本#备注#cookie#salt#代理 -> 备注#cookie#salt#代理
    旧格式: 备注#cookie#salt#代理 -> 备注#cookie#salt#代理
    """
    if not full_ck:
        return full_ck
    
    token_info = parse_token(full_ck)
    if not token_info:
        return full_ck
    
    # 重新组装为青龙格式（不包含版本标识）
    result = f"{token_info['name']}#{token_info['cookie']}#{token_info['salt']}"
    if token_info['proxy']:
        result += f"#{token_info['proxy']}"
    
    return result

def validate_proxy(proxy_str):
    """
    验证代理格式和有效性
    格式: IP|端口|用户名|密码|过期时间
    示例: 119.84.77.52|6855|user|pass|2025-12-19
    
    返回: (is_valid, error_msg)
    """
    if not proxy_str:
        return False, "代理信息为空"
    
    try:
        parts = proxy_str.split('|')
        
        if len(parts) != 5:
            return False, f"代理格式错误，应为5个部分（IP|端口|用户名|密码|过期时间），实际为{len(parts)}个"
        
        proxy_ip, port, username, password, expire_date = parts
        
        # 验证端口
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                return False, f"端口号无效: {port}"
        except ValueError:
            return False, f"端口号格式错误: {port}"
        
        # 验证用户名和密码
        if not username or not password:
            return False, "用户名或密码不能为空"
        
        # 实际连接测试
        try:
            proxy_url = f"http://{username}:{password}@{proxy_ip}:{port}"
            test_url = "https://d.pcs.baidu.com/rest/2.0/pcs/file?method=locateupload"
            
            response = requests.get(
                test_url,
                proxies={'http': proxy_url, 'https': proxy_url},
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # 百度云接口返回包含client_ip字段
                    client_ip = data.get('client_ip', '')
                    error_code = data.get('error_code', -1)
                    
                    if error_code == 0:
                        # 检查返回的IP
                        if client_ip:
                            # 只比较前三段IP（因为百度可能会隐藏最后一段）
                            proxy_prefix = '.'.join(proxy_ip.split('.')[:3])
                            client_prefix = '.'.join(client_ip.split('.')[:3])
                            
                            if proxy_prefix == client_prefix:
                                return True, f"✅ 代理验证通过（IP: {client_ip}）"
                            else:
                                return True, f"✅ 代理可用（代理IP: {proxy_ip}, 返回IP: {client_ip}）"
                        else:
                            return True, "✅ 代理验证通过"
                    else:
                        return False, f"代理连接失败，错误码: {error_code}"
                except:
                    # 如果不是JSON格式，但状态码是200，也认为代理可用
                    return True, "✅ 代理可用"
            else:
                return False, f"代理连接失败，状态码: {response.status_code}"
                
        except requests.exceptions.Timeout:
            return False, "代理连接超时（10秒）"
        except requests.exceptions.ProxyError:
            return False, "代理连接失败，请检查代理配置"
        except Exception as e:
            return False, f"代理测试异常: {str(e)}"
        
    except Exception as e:
        return False, f"代理验证异常: {str(e)}"

def query_account_fast(cookie_str, proxy_str=None):
    """查询极速版账号详情"""
    url = "https://nebula.kuaishou.com/rest/n/nebula/account/overview"
    
    headers = {
        'Host': 'nebula.kuaishou.com',
        'User-Agent': 'kwai-android aegon/4.29.0',
        'Cookie': cookie_str,
        'Accept': 'application/json, text/plain, */*'
    }
    
    # 构建代理配置
    proxies = None
    if proxy_str:
        try:
            parts = proxy_str.split('|')
            if len(parts) == 5:
                proxy_ip, port, username, password, _ = parts
                proxy_url = f"http://{username}:{password}@{proxy_ip}:{port}"
                proxies = {'http': proxy_url, 'https': proxy_url}
        except:
            pass
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=12)
        result = response.json()
        
        if result.get('result') == 1 and result.get('data'):
            data = result['data']
            
            # 获取金币明细（最近3条）
            coin_records = []
            coin_page = data.get('coinAccountPage', {})
            if coin_page.get('data'):
                coin_records = coin_page['data'][:3]
            
            # 获取现金明细（最近3条）
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
                'coinRecords': coin_records,
                'cashRecords': cash_records
            }
        return {'success': False, 'msg': '查询失败'}
    except Exception as e:
        return {'success': False, 'msg': str(e)}

def query_account_normal(cookie_str, proxy_str=None):
    """查询普通版账号详情"""
    # 先获取基本信息
    basic_url = "https://encourage.kuaishou.com/rest/wd/encourage/account/basicInfo"
    headers = {
        'Host': 'encourage.kuaishou.com',
        'User-Agent': 'kwai-android aegon/4.27.0',
        'Cookie': cookie_str,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # 构建代理配置
    proxies = None
    if proxy_str:
        try:
            parts = proxy_str.split('|')
            if len(parts) == 5:
                proxy_ip, port, username, password, _ = parts
                proxy_url = f"http://{username}:{password}@{proxy_ip}:{port}"
                proxies = {'http': proxy_url, 'https': proxy_url}
        except:
            pass
    
    try:
        # 获取基本信息
        response = requests.get(basic_url, headers=headers, proxies=proxies, timeout=15)
        result = response.json()
        
        if result.get('result') != 1 or not result.get('data'):
            return {'success': False, 'msg': '查询失败'}
        
        data = result['data']
        coin_balance = data.get('coinAmount', 0)
        cash_balance = data.get('cashAmountDisplay', 0)
        nickname = data.get('userData', {}).get('nickname', '未知')
        
        # 获取金币明细（最近3条）
        coin_detail_url = "https://encourage.kuaishou.com/rest/wd/encourage/account/detail?sigCatVer=1&accountType=coin&cursor"
        coin_response = requests.get(coin_detail_url, headers=headers, proxies=proxies, timeout=10)
        coin_records = []
        if coin_response.status_code == 200:
            coin_result = coin_response.json()
            if coin_result.get('result') == 1 and coin_result.get('data', {}).get('datas'):
                coin_records = coin_result['data']['datas'][:3]
        
        # 获取现金明细（最近3条）
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
            'coinRecords': coin_records,
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
    
    # 第一步：选择版本
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
    
    # 根据选择设置版本信息
    if version_choice == '1':
        version_name = "某手极速版"
        query_func = query_account_fast
    else:
        version_name = "某手普通版"
        query_func = query_account_normal
    
    # 第二步：过滤并显示对应版本的账号
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
    
    # 显示账号列表供用户选择
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
            sender.reply("❌ 无效的选择")
            return
    except:
        sender.reply("❌ 请输入数字")
        return
    
    # 确定要查询的账号列表
    if account_idx == 0:
        query_accounts_list = accounts
    else:
        query_accounts_list = [accounts[account_idx - 1]]
    
    result_msg = f"====={version_name}查询结果=====\n"
    
    for idx, account in enumerate(query_accounts_list, 1):
        # 获取账号信息
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if not full_ck:
            result_msg += f"\n{idx}. 账号ID: {account}\n   ❌ 未找到Cookie信息\n"
            continue
        
        # 解析token
        token_info = parse_token(full_ck)
        if not token_info or not token_info['cookie']:
            result_msg += f"\n{idx}. 账号ID: {account}\n   ❌ Cookie格式错误\n"
            continue
        
        name = token_info['name']
        cookie = token_info['cookie']
        proxy_info = token_info['proxy']
        
        # 查询对应版本的账号信息（如果有代理则使用代理）
        query_result = query_func(cookie, proxy_info)
        
        result_msg += f"🆔 ID: {account}\n"
        
        if query_result['success']:
            if version_choice == '1':
                # 极速版
                result_msg += f"💰 金币: {query_result['coinBalance']}\n"
                result_msg += f"💵 余额: {query_result['cashBalance']}元\n"
                result_msg += f"📊 累计: {query_result['accumulativeAmount']}元\n"
                
                # 根据模式显示不同的状态
                if use_share_mode:
                    # 分成模式：显示今日分成状态
                    today = str(datetime.now().date())
                    is_paid, revenue, share_amount = get_today_share_status(account)
                    if is_paid:
                        result_msg += f"💳 分成: 今日已结算({share_amount}元)\n"
                    elif revenue > 0:
                        result_msg += f"💳 分成: 待结算({share_amount}元)\n"
                    else:
                        result_msg += f"💳 分成: 暂无收益\n"
                else:
                    # 常规模式：显示授权时间
                    auth_status = middleware.bucketGet('dd_ks_auth', account) or '未授权'
                    result_msg += f"🔐 授权: {auth_status}\n"
                
                # 显示金币明细
                if query_result.get('coinRecords'):
                    result_msg += "\n📝 金币明细(最近3条):\n"
                    for record in query_result['coinRecords']:
                        title = record.get('eventType', '未知')
                        amount = record.get('amount', '0')
                        # 判断正负
                        try:
                            amt_val = float(amount)
                            symbol = '+' if amt_val >= 0 else ''
                        except:
                            symbol = '+'
                        result_msg += f"  • {title}: {symbol}{amount}\n"
                
                # 显示现金明细
                if query_result.get('cashRecords'):
                    result_msg += "\n💸 现金明细(最近3条):\n"
                    for record in query_result['cashRecords']:
                        title = record.get('eventType', '未知')
                        amount = record.get('amount', '0')
                        # 判断正负
                        try:
                            amt_val = float(amount)
                            symbol = '+' if amt_val >= 0 else ''
                        except:
                            symbol = '+'
                        result_msg += f"  • {title}: {symbol}{amount}元\n"
            else:
                # 普通版
                result_msg += f"💰 金币: {query_result['coinBalance']}\n"
                result_msg += f"💵 余额: {query_result['cashBalance']}元\n"
                
                # 根据模式显示不同的状态
                if use_share_mode:
                    # 分成模式：显示今日分成状态
                    today = str(datetime.now().date())
                    is_paid, revenue, share_amount = get_today_share_status(account)
                    if is_paid:
                        result_msg += f"💳 分成: 今日已结算({share_amount}元)\n"
                    elif revenue > 0:
                        result_msg += f"💳 分成: 待结算({share_amount}元)\n"
                    else:
                        result_msg += f"💳 分成: 暂无收益\n"
                else:
                    # 常规模式：显示授权时间
                    auth_status = middleware.bucketGet('dd_ks_auth', account) or '未授权'
                    result_msg += f"🔐 授权: {auth_status}\n"
                
                # 显示金币明细
                if query_result.get('coinRecords'):
                    result_msg += "\n📝 金币明细(最近3条):\n"
                    for record in query_result['coinRecords']:
                        title = record.get('title', '未知')
                        amount = record.get('displayAmount', '0')
                        result_msg += f"  • {title}: +{amount}\n"
                
                # 显示现金明细
                if query_result.get('cashRecords'):
                    result_msg += "\n💸 现金明细(最近3条):\n"
                    for record in query_result['cashRecords']:
                        title = record.get('title', '未知')
                        amount = record.get('displayAmount', '0')
                        direction = record.get('direction', 'IN')
                        symbol = '+' if direction == 'IN' else '-'
                        result_msg += f"  • {title}: {symbol}{amount}元\n"
        else:
            result_msg += f"❌ 查询失败: {query_result.get('msg', '未知错误')}\n"
        
        result_msg += "------------------"
    
    sender.reply(result_msg)

def bindaccount():
    """绑定账号 - 支持格式: 备注#cookie#salt 或 备注#cookie#salt#|端口|用户名|密码|过期时间"""
    
    # 先让用户选择版本
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
    
    # 根据选择设置版本信息
    if version_choice == '1':
        version_name = "某手极速版"
        target_varname = ks_fast_varname
    else:
        version_name = "某手普通版"
        target_varname = ks_normal_varname
    
    # 根据是否允许代理显示不同的提示
    if allow_proxy:
        ck_guide = f"""
====={version_name}登录=====
请输入账号信息
📝 支持格式:
1. 备注#Cookie#Salt
2. 备注#Cookie#Salt#IP|端口|用户名|密码|过期时间
------------------
"""
    else:
        ck_guide = f"""
====={version_name}登录=====
请输入账号信息
📝 支持格式:
1. 备注#Cookie#Salt
2. 备注#Cookie#Salt#端口|用户名|密码|过期时间
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
            
            # 验证格式
            if len(parts) < 3:
                sender.reply("""
❌ 格式错误
------------------
正确格式: 备注#Cookie#Salt
或: 备注#Cookie#Salt#代理信息""")
                exit(0)
            
            # 解析输入
            name = parts[0]
            ck = parts[1]
            salt_input = parts[2]
            proxy_input = parts[3] if len(parts) >= 4 else ""
            
            # 验证代理（如果有）
            if proxy_input:
                proxy_valid, proxy_msg = validate_proxy(proxy_input)
                if not proxy_valid:
                    sender.reply(f"""
❌ 代理验证失败
------------------
{proxy_msg}
------------------
请检查代理格式: IP|端口|用户名|密码|过期时间
示例: 119.84.77.52|6855|user|pass|2025-12-19""")
                    exit(0)
                
                # 显示验证结果
                sender.reply(proxy_msg)
            
            # 根据版本选择验证Cookie
            if version_choice == '1':
                # 极速版验证
                is_valid, result = verify_account_fast(ck)
            else:
                # 普通版验证（传入备注名称作为默认昵称）
                is_valid, result = verify_account_normal(ck, name)
            
            if is_valid:
                # 从Cookie中获取userId
                cookies = parse_cookies(ck)
                account = cookies.get('userId', 'unknown')
                if account == 'unknown':
                    sender.reply("❌ 无法获取账号信息")
                    exit(0)
                
                # 获取账号信息
                nickname = result.get('nickname', name)
                coin = result.get('coin', 0)
                cash = result.get('cash', 0)
                
                # 组装完整的CK字符串: 版本#备注#cookie#salt#代理
                # 版本标识：1=极速版，2=普通版
                full_ck = f"{version_choice}#{name}#{ck}#{salt_input}"
                if proxy_input:
                    full_ck += f"#{proxy_input}"
                
                # 保存账号信息
                if len(uservalue) == 0:
                    middleware.bucketSet('dd_ks_user', userid, str([account]))
                    middleware.bucketSet('dd_ks_token', account, full_ck)
                    middleware.bucketSet('dd_ks_auth', account, '')
                else:
                    accounts = eval(uservalue)
                    if account not in accounts:
                        accounts.append(account)
                        middleware.bucketSet('dd_ks_user', userid, str(accounts))
                    middleware.bucketSet('dd_ks_token', account, full_ck)
                
                # 直接使用之前选择的版本提交
                accountVip = middleware.bucketGet('dd_ks_auth', account)
                if accountVip and accountVip >= today_time:
                    # 已授权账号，直接提交到选择的版本（转换为青龙格式）
                    qinglong_value = token_to_qinglong_format(full_ck)
                    Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
                    auth_status = f'已授权({version_name})'
                else:
                    auth_status = '未授权'
                
                success_msg = f"""
=====绑定成功=====
👤 昵称: {nickname}
🆔 账号ID: {account}
💰 金币数: {coin}
💵 余额: {cash}元
🔐 授权状态: {auth_status}
🌐 代理状态: {'已设置' if proxy_input else '未设置'}
------------------
提示: {'账号已添加至青龙' if '已授权' in auth_status and '未提交' not in auth_status else '请先授权账号再使用'}
=================="""
                sender.reply(success_msg)
                break
                
            else:
                sender.reply(f"""
=====验证失败=====
❌ {result}
------------------
请检查CK是否正确
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

def Addenvs(osname, value, account, phone):
    """添加/更新环境变量到青龙"""
    url = f"{QLurl}/open/envs"
    headers = {"Authorization": f"Bearer {qltoken}", "Content-Type": "application/json"}
    
    try:
        # 查询已存在的变量
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200 or resp.json()['code'] != 200:
            sender.reply("❌ 获取青龙变量失败")
            return False
        
        # 查找是否已存在
        qlid = None
        for env in resp.json()['data']:
            if account in env.get('remarks', '') and osname == env['name']:
                qlid = env['id']
                break
        
        # 构建备注
        accountVip = middleware.bucketGet('dd_ks_auth', account) or '未授权'
        remarks = f'快手:{account}丨用户:{userid}丨ID:{phone}丨授权至:{accountVip}'
        
        # 更新或添加
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

# ==================== 支付功能 ====================

def get_payment_config():
    """获取支付配置"""
    config = {
        'use_ma_pay': middleware.bucketGet('dd_ks', 'use_ma_pay') or 'false',
        'zsm': middleware.bucketGet('dd_ks', 'zsm') or '',
        # 从卡密系统读取码支付配置
        'ma_pay_gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
        'ma_pay_pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
        'ma_pay_key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
        'ma_pay_type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
        'ma_pay_notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or '',
    }
    # 同步字段
    config['pid'] = config['ma_pay_pid']
    config['key'] = config['ma_pay_key']
    config['gateway'] = config['ma_pay_gateway']
    return config

# 支付方式中文名称映射
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

def process_payment(amount, months, account_count=1):
    """处理支付流程
    
    Args:
        amount: 支付金额
        months: 授权月数
        account_count: 账号数量
        
    Returns:
        (success, msg): 是否成功、消息
    """
    payment_config = get_payment_config()
    use_ma_pay = payment_config['use_ma_pay'].lower() == 'true'
    
    # 如果启用码支付且配置完整
    if use_ma_pay and payment_config['ma_pay_gateway'] and payment_config['ma_pay_pid'] and payment_config['ma_pay_key']:
        return process_ma_pay(amount, months, account_count, payment_config)
    else:
        return process_normal_pay(amount, months, account_count, payment_config)

def process_ma_pay(amount, months, account_count, payment_config):
    """码支付流程"""
    try:
        # 生成商户订单号
        out_trade_no = f"KS{int(time.time())}{userid}"
        
        # 解析支付方式
        pay_types_str = payment_config['ma_pay_type'].strip()
        if not pay_types_str:
            pay_types_str = "alipay,wxpay,qqpay"
        
        pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
        
        # 选择支付方式
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
        
        # 创建支付订单
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
        
        # 提取支付链接
        payurl = result.get('payurl', '')
        if not payurl:
            return False, '获取支付链接失败'
        
        # 发送支付二维码
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
        
        # 轮询支付结果
        is_paid, msg, data = poll_payment_status(out_trade_no, payment_config)
        
        if is_paid:
            return True, f"支付成功！订单号: {out_trade_no}"
        else:
            return False, f"支付未完成: {msg}"
            
    except Exception as e:
        return False, f'支付处理失败: {str(e)}'

def process_normal_pay(amount, months, account_count, payment_config):
    """常规支付流程（微信支付）"""
    if not payment_config['zsm']:
        return False, '未配置收款码，请联系管理员'
    
    # 检查是否有人正在支付
    zfzt = sender.atWaitPay()
    if zfzt:
        return False, '当前有人正在支付，请稍后再试'
    
    # 发送支付信息
    pay_msg = f"""
=====微信扫码支付=====
🎫 商品: 快手授权
📅 时长: {months}月
📊 账号: {account_count}个
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)
    sender.replyImage(payment_config['zsm'])
    
    # 等待支付结果
    ddzf = sender.waitPay("q", 100 * 1000)
    
    try:
        if not ddzf or str(ddzf) == 'q':
            return False, '已取消支付'
        
        # 解析支付结果
        try:
            if isinstance(ddzf, str):
                ddzf = json.loads(ddzf)
        except json.JSONDecodeError:
            return False, '支付结果解析失败，如果您已完成支付，请联系管理员'
        
        # 支持多种收款消息格式
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

# ==================== 分成模式功能 ====================

def calculate_share_amount(revenue, share_rate):
    """计算分成金额
    
    Args:
        revenue: 收益金额
        share_rate: 分成比例（0-100）
        
    Returns:
        应付分成金额
    """
    return round(float(revenue) * (share_rate / 100), 2)

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
    # 计算分成金额
    share_amount = calculate_share_amount(revenue, share_rate)
    
    if share_amount <= 0:
        return False, "分成金额必须大于0"
    
    # 显示分成信息
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
    
    # 执行支付（使用分成金额，月数设为0表示分成模式）
    pay_success, pay_msg = process_payment(share_amount, 0, 1)
    
    if pay_success:
        # 保存分成记录（包含金币数量）
        save_share_record(account, revenue, share_amount, is_paid=True, coins=coins)
        return True, f"分成支付成功！今日授权已完成"
    else:
        return False, f"分成支付失败: {pay_msg}"

def check_share_authorization(account, version_choice):
    """检查分成模式授权状态
    
    Returns:
        (is_authorized, msg): 是否已授权、消息
    """
    if not use_share_mode:
        # 未启用分成模式，检查常规授权
        auth_status = middleware.bucketGet('dd_ks_auth', account)
        today = str(datetime.now().date())
        
        if auth_status and auth_status >= today:
            return True, f"账号已授权至: {auth_status}"
        else:
            return False, "账号未授权或已过期"
    
    # 分成模式：检查今日是否已支付
    is_paid, revenue, share_amount = get_today_share_status(account)
    
    if is_paid:
        return True, f"今日分成已支付: {share_amount}元"
    else:
        # 查询今日收益
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if not full_ck:
            return False, "未找到账号信息"
        
        token_info = parse_token(full_ck)
        if not token_info or not token_info['cookie']:
            return False, "Cookie信息错误"
        
        cookie = token_info['cookie']
        proxy_info = token_info['proxy']
        
        # 查询账号信息
        if version_choice == '1':
            query_result = query_account_fast(cookie, proxy_info)
        else:
            query_result = query_account_normal(cookie, proxy_info)
        
        if not query_result.get('success'):
            return False, f"查询收益失败: {query_result.get('msg', '未知错误')}"
        
        # 获取今日新增金币（从金币明细中统计）
        today_coins = 0
        if query_result.get('coinRecords'):
            today_date = datetime.now().date()
            for record in query_result['coinRecords']:
                # 只统计今天的金币收入（正数）
                try:
                    amount = float(record.get('amount', 0))
                    if amount > 0:
                        today_coins += amount
                except:
                    continue
        
        if today_coins <= 0:
            return False, "今日暂无金币收益，无需支付分成"
        
        # 将金币转换为现金：1万金币=1元
        today_revenue = round(today_coins / 10000, 2)
        
        # 计算分成金额
        share_amount = calculate_share_amount(today_revenue, share_rate)
        
        # 保存分成记录（未支付状态，包含金币数量）
        save_share_record(account, today_revenue, share_amount, is_paid=False, coins=today_coins)
        
        return False, f"今日金币: {int(today_coins)}个 ({today_revenue}元)，需支付分成: {share_amount}元"

# ==================== 账号管理功能 ====================

def manage_accounts():
    """账号管理功能"""
    # 获取用户的所有账号
    if not uservalue or len(uservalue) == 0:
        sender.reply("❌ 您还没有绑定任何账号\n请先发送 快手登录 进行账号绑定")
        return
    
    accounts = eval(uservalue)
    
    # 第一步：选择版本
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
    
    # 设置目标变量名
    if version_choice == '1':
        version_name = "某手极速版"
        target_varname = ks_fast_varname
    else:
        version_name = "某手普通版"
        target_varname = ks_normal_varname
    
    # 第二步：过滤并显示对应版本的账号
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
请选择要管理的账号
------------------
[0] 🎯 批量授权所有账号
------------------
"""
    
    for idx, account in enumerate(version_accounts, 1):
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            name = token_info['name'] if token_info else '未知'
            
            # 根据模式显示不同的状态
            if use_share_mode:
                # 分成模式：显示今日分成状态
                today = str(datetime.now().date())
                is_paid, revenue, share_amount = get_today_share_status(account)
                if is_paid:
                    status_text = f"✅ 今日已结算({share_amount}元)"
                elif revenue > 0:
                    status_text = f"⏳ 待结算({share_amount}元)"
                else:
                    status_text = "📊 暂无收益"
                account_list += f"[{idx}] {name}\n    ID: {account}\n    状态: {status_text}\n------------------\n"
            else:
                # 常规模式：显示授权时间
                auth_status = middleware.bucketGet('dd_ks_auth', account) or '未授权'
                account_list += f"[{idx}] {name}\n    ID: {account}\n    授权至: {auth_status}\n------------------\n"
        else:
            if use_share_mode:
                account_list += f"[{idx}] ID: {account}\n    状态: 未知\n------------------\n"
            else:
                account_list += f"[{idx}] ID: {account}\n    授权至: 未授权\n------------------\n"
    
    account_list += "回复数字选择账号\n回复 q 退出操作\n=================="
    sender.reply(account_list)
    
    # 等待用户选择
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
    
    # 第三步：处理批量授权或单个账号
    if choice_idx == 0:
        # 批量授权
        auth_guide = f"""
=====批量授权设置=====
版本: {version_name}
账号数量: {len(version_accounts)}个
------------------
请输入授权月数(如:1)
回复数字设置月数
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
                sender.reply("❌ 授权月数必须大于0")
                return
        except:
            sender.reply("❌ 请输入正确的数字")
            return
        
        # 计算总金额
        total_money = Decimal(months) * ksVipmoney * len(version_accounts)
        
        # 显示确认信息
        confirm_msg = f"""
=====批量授权确认=====
📱 版本: {version_name}
📊 账号数量: {len(version_accounts)}个
⏰ 授权时长: {months}月/每个账号
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
        
        # 执行支付
        pay_success, pay_msg = process_payment(float(total_money), months, len(version_accounts))
        if not pay_success:
            sender.reply(f"❌ {pay_msg}")
            return
        
        # 批量授权所有账号（不显示中间过程）
        success_count = 0
        fail_count = 0
        
        for account in version_accounts:
            try:
                full_ck = middleware.bucketGet('dd_ks_token', account)
                if not full_ck:
                    fail_count += 1
                    continue
                
                # 计算新的授权时间
                current_auth = middleware.bucketGet('dd_ks_auth', account)
                today = datetime.now().date()
                
                if current_auth and current_auth > str(today):
                    auth_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
                    new_auth_date = auth_date + timedelta(days=days)
                else:
                    new_auth_date = today + timedelta(days=days)
                
                new_auth = new_auth_date.strftime("%Y-%m-%d")
                
                # 更新授权时间
                middleware.bucketSet('dd_ks_auth', account, new_auth)
                
                # 提交到青龙（转换为青龙格式）
                token_info = parse_token(full_ck)
                name = token_info['name'] if token_info else account
                qinglong_value = token_to_qinglong_format(full_ck)
                Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
                
                success_count += 1
            except Exception as e:
                fail_count += 1
                print(f"授权账号 {account} 失败: {str(e)}")
        
        # 合并支付和授权结果
        result_msg = f"""
=====授权完成=====
{pay_msg}
------------------
📱 版本: {version_name}
📊 账号数量: {len(version_accounts)}个
✅ 成功: {success_count} 个
❌ 失败: {fail_count} 个
⏰ 授权时长: {months} 月
💰 支付金额: {total_money} 元
=================="""
        sender.reply(result_msg)
        
    else:
        # 单个账号管理
        account = version_accounts[choice_idx - 1]
        full_ck = middleware.bucketGet('dd_ks_token', account)
        
        if not full_ck:
            sender.reply("❌ 未找到账号信息")
            return
        
        token_info = parse_token(full_ck)
        name = token_info['name'] if token_info else '未知'
        auth_status = middleware.bucketGet('dd_ks_auth', account) or '未授权'
        
        # 显示账号详情和操作菜单
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
            # 授权账号
            auth_guide = f"""
=====设置授权时长=====
📱账号: {name}
📱版本: {version_name}
------------------
请输入授权月数(如:1)
回复数字设置月数
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
                    sender.reply("❌ 授权月数必须大于0")
                    return
            except:
                sender.reply("❌ 请输入正确的数字")
                return
            
            # 计算金额
            money = Decimal(months) * ksVipmoney
            
            # 显示确认信息
            confirm_msg = f"""
=====授权确认=====
📱 账号: {name}
📱 版本: {version_name}
⏰ 授权: {months}月
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
            
            # 执行支付
            pay_success, pay_msg = process_payment(float(money), months, 1)
            if not pay_success:
                sender.reply(f"❌ {pay_msg}")
                return
            
            # 计算新的授权时间
            days = months * 30
            current_auth = middleware.bucketGet('dd_ks_auth', account)
            today = datetime.now().date()
            
            if current_auth and current_auth > str(today):
                auth_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
                new_auth_date = auth_date + timedelta(days=days)
            else:
                new_auth_date = today + timedelta(days=days)
            
            new_auth = new_auth_date.strftime("%Y-%m-%d")
            
            # 更新授权时间
            middleware.bucketSet('dd_ks_auth', account, new_auth)
            
            # 提交到青龙（转换为青龙格式）
            qinglong_value = token_to_qinglong_format(full_ck)
            Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
            
            # 合并支付和授权结果
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
            # 删除账号
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
            
            # 删除账号
            accounts.remove(account)
            middleware.bucketDel('dd_ks_token', account)
            middleware.bucketDel('dd_ks_auth', account)
            
            if len(accounts) == 0:
                middleware.bucketDel('dd_ks_user', userid)
            else:
                middleware.bucketSet('dd_ks_user', userid, str(accounts))
            
            sender.reply(f"""
=====删除成功=====
账号 {name} 已删除
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
    
    # 发送到各个平台
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
        
        # 查询已存在的变量
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200 or resp.json()['code'] != 200:
            return False
        
        # 查找对应的环境变量
        qlid = None
        for env in resp.json()['data']:
            if account in env.get('remarks', '') and target_varname == env['name']:
                qlid = env['id']
                break
        
        if qlid:
            # 禁用环境变量
            disable_url = f"{QLurl}/open/envs/disable"
            data = [qlid]
            resp = requests.put(disable_url, headers=headers, json=data, timeout=10)
            
            if resp.status_code == 200 and resp.json()['code'] == 200:
                return True
        
        return False
    except Exception as e:
        print(f"禁用账号失败: {str(e)}")
        return False

def check_share_payment_status():
    """定时检查分成支付状态（每天8点和21点执行）"""
    if not use_share_mode:
        return
    
    # 获取所有用户
    all_users = middleware.bucketAllKeys('dd_ks_user')
    if not all_users:
        return
    
    today = str(datetime.now().date())
    yesterday = str((datetime.now() - timedelta(days=1)).date())
    current_hour = datetime.now().hour
    
    # 判断是早上检查还是晚上检查
    is_morning_check = (current_hour == 8)  # 早上8点
    is_evening_check = (current_hour == 21)  # 晚上21点
    
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
                    # ========== 早上8点：检查昨日支付并禁用未支付账号 ==========
                    if is_morning_check:
                        yesterday_key = f"share_{account}_{yesterday}"
                        yesterday_data = middleware.bucketGet('dd_ks_share', yesterday_key)
                        
                        yesterday_paid = False
                        if yesterday_data:
                            try:
                                data = json.loads(yesterday_data)
                                yesterday_paid = data.get('is_paid', False)
                            except:
                                pass
                        
                        # 如果昨天有收益但没有支付，禁用账号
                        if not yesterday_paid and yesterday_data:
                            # 获取账号信息
                            full_ck = middleware.bucketGet('dd_ks_token', account)
                            if full_ck:
                                token_info = parse_token(full_ck)
                                name = token_info['name'] if token_info else account
                                
                                # 禁用账号（两个版本都尝试禁用）
                                disabled_fast = disable_account_in_qinlong(account, ks_fast_varname)
                                disabled_normal = disable_account_in_qinlong(account, ks_normal_varname)
                                
                                if disabled_fast or disabled_normal:
                                    disable_count += 1
                                    
                                    # 推送停用通知
                                    push_notification(user, name, f"""
⚠️ 账号已停用
------------------
❌ 昨日未支付分成
📅 停用日期: {today}
💡 请及时支付分成后联系管理员恢复
------------------
提示: 支付完成后请联系管理员
手动启用青龙环境变量""")
                    
                    # ========== 晚上21点：查询今日收益并提醒支付 ==========
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
                        
                        # 如果今天还没支付，查询收益并发送提醒
                        if not today_paid:
                            full_ck = middleware.bucketGet('dd_ks_token', account)
                            if full_ck:
                                token_info = parse_token(full_ck)
                                name = token_info['name'] if token_info else account
                                
                                # 查询今日收益
                                cookie = token_info['cookie'] if token_info else None
                                proxy_info = token_info['proxy'] if token_info else None
                                
                                if cookie:
                                    # 尝试查询极速版
                                    try:
                                        query_result = query_account_fast(cookie, proxy_info)
                                        if query_result.get('success'):
                                            cash_balance = float(query_result.get('cashBalance', 0))
                                            if cash_balance > 0:
                                                share_amount = calculate_share_amount(cash_balance, share_rate)
                                                
                                                # 保存分成记录
                                                save_share_record(account, cash_balance, share_amount, is_paid=False)
                                                
                                                # 推送支付提醒
                                                push_notification(user, name, f"""
📊 今日分成提醒
------------------
💰 今日收益: {cash_balance}元
📈 分成比例: {share_rate}%
💵 应付金额: {share_amount}元
------------------
💡 请发送"快手分成"进行结算
⚠️ 未支付将在明日早上8点停用账号
------------------
温馨提示: 请在今晚23:59前完成支付""")
                                                notify_count += 1
                                    except:
                                        pass
                    
                except Exception as e:
                    print(f"处理账号 {account} 失败: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"处理用户 {user} 失败: {str(e)}")
            continue
    
    # 记录日志
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
    if not use_share_mode:
        sender.reply("❌ 未启用分成模式")
        return
    
    # 获取用户的所有账号
    if not uservalue or len(uservalue) == 0:
        sender.reply("❌ 您还没有绑定任何账号\n请先发送 快手登录 进行账号绑定")
        return
    
    accounts = eval(uservalue)
    
    # 选择版本
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
    
    # 显示账号列表
    account_list = f"""
====={version_name}分成结算=====
请选择要结算的账号
------------------
"""
    
    for idx, account in enumerate(accounts, 1):
        full_ck = middleware.bucketGet('dd_ks_token', account)
        if full_ck:
            token_info = parse_token(full_ck)
            name = token_info['name'] if token_info else '未知'
            is_paid, revenue, share_amount = get_today_share_status(account)
            status = f"✅ 已支付{share_amount}元" if is_paid else "⏳ 待支付"
            account_list += f"[{idx}] {name}\n    状态: {status}\n------------------\n"
        else:
            account_list += f"[{idx}] ID: {account}\n    状态: 未知\n------------------\n"
    
    account_list += "回复数字选择账号\n回复 q 退出操作\n=================="
    sender.reply(account_list)
    
    # 等待用户选择
    choice = sender.input(120000, 1, False)
    if not choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif choice.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    try:
        choice_idx = int(choice)
        if choice_idx < 1 or choice_idx > len(accounts):
            sender.reply(f"❌ 请输入 1-{len(accounts)} 之间的数字")
            return
    except:
        sender.reply("❌ 请输入正确的数字")
        return
    
    account = accounts[choice_idx - 1]
    
    # 检查授权状态
    is_authorized, msg = check_share_authorization(account, version_choice)
    
    if is_authorized:
        sender.reply(f"✅ {msg}")
        return
    
    # 需要支付分成
    sender.reply(f"📊 {msg}")
    
    # 获取分成记录
    is_paid, revenue, share_amount = get_today_share_status(account)
    
    if revenue <= 0:
        sender.reply("❌ 今日暂无收益")
        return
    
    # 重新查询获取金币数量
    full_ck = middleware.bucketGet('dd_ks_token', account)
    today_coins = None
    if full_ck:
        token_info = parse_token(full_ck)
        if token_info and token_info['cookie']:
            cookie = token_info['cookie']
            proxy_info = token_info['proxy']
            
            # 查询账号信息
            if version_choice == '1':
                query_result = query_account_fast(cookie, proxy_info)
            else:
                query_result = query_account_normal(cookie, proxy_info)
            
            # 统计今日金币
            if query_result.get('success') and query_result.get('coinRecords'):
                today_coins = 0
                for record in query_result['coinRecords']:
                    try:
                        amount = float(record.get('amount', 0))
                        if amount > 0:
                            today_coins += amount
                    except:
                        continue
    
    # 处理分成支付
    success, result_msg = process_share_payment(account, revenue, share_rate, today_coins)
    
    if success:
        sender.reply(f"✅ {result_msg}")
    else:
        sender.reply(f"❌ {result_msg}")

def admin_panel():
    """快手后台管理"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限访问后台")
        return
    
    admin_menu = """
=====快手后台管理=====
[1] 快手授权
[2] 分成统计
[3] 快手清理
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(admin_menu)
    
    choice = sender.input(60000, 1, False)
    
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出后台")
        return
    
    if choice == '1':
        admin_authorization()
    elif choice == '2':
        admin_share_statistics()
    elif choice == '3':
        admin_clean_accounts()
    else:
        sender.reply("❌ 无效的选择")

def admin_authorization():
    """快手授权管理"""
    # 第一步：选择版本
    version_menu = """
=====选择快手版本=====
请选择要管理的版本
------------------
[1] 某手极速版
[2] 某手普通版
------------------
回复数字选择版本
回复"q"退出操作
=================="""
    sender.reply(version_menu)
    
    version_choice = sender.input(60000, 1, False)
    if not version_choice or version_choice.lower() == 'q':
        sender.reply("✅ 已退出授权管理")
        return
    
    if version_choice not in ['1', '2']:
        sender.reply("❌ 无效的选择")
        return
    
    # 设置版本信息
    if version_choice == '1':
        version_name = "某手极速版"
        target_varname = ks_fast_varname
    else:
        version_name = "某手普通版"
        target_varname = ks_normal_varname
    
    # 第二步：选择功能
    auth_menu = f"""
====={version_name}授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 更新青龙变量
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(auth_menu)
    
    choice = sender.input(60000, 1, False)
    
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出授权管理")
        return
    
    if choice == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('dd_ks_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的快手账号")
            return
        
        sender.reply("""
=====请输入授权月数=====
------------------
回复数字设置月数
回复"q"退出操作
==================""")
        
        months_input = sender.input(60000, 1, False)
        if not months_input or months_input.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            months = int(months_input)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
        except:
            sender.reply("❌ 月数必须是数字!")
            return
        
        success_count = 0
        fail_count = 0
        days = months * 30
        
        for user in users:
            accountlist = middleware.bucketGet('dd_ks_user', user)
            if not accountlist:
                continue
            
            try:
                accounts = eval(accountlist)
                if isinstance(accounts, str):
                    accounts = [accounts]
                
                for account in accounts:
                    try:
                        token = middleware.bucketGet('dd_ks_token', account)
                        if not token:
                            fail_count += 1
                            continue
                        
                        # 检查版本是否匹配
                        token_info = parse_token(token)
                        if not token_info or token_info['version'] != version_choice:
                            continue  # 跳过不匹配版本的账号
                        
                        # 计算新的授权时间
                        current_auth = middleware.bucketGet('dd_ks_auth', account)
                        today = datetime.now().date()
                        
                        if current_auth and current_auth > str(today):
                            auth_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
                            new_auth_date = auth_date + timedelta(days=days)
                        else:
                            new_auth_date = today + timedelta(days=days)
                        
                        new_auth_str = str(new_auth_date)
                        
                        # 更新授权时间
                        middleware.bucketSet('dd_ks_auth', account, new_auth_str)
                        
                        # 更新青龙变量（只更新对应版本）
                        name = token_info['name'] if token_info else account
                        qinglong_value = token_to_qinglong_format(token)
                        
                        try:
                            Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
                        except:
                            pass
                        
                        success_count += 1
                    except Exception as e:
                        fail_count += 1
                        print(f"授权账号 {account} 失败: {str(e)}")
            except:
                continue
        
        result_msg = f"""
=====授权操作完成=====
📱 版本: {version_name}
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {months} 月
=================="""
        sender.reply(result_msg)
    
    elif choice == '2':
        # 单独授权用户
        sender.reply("""
======账号授权======
请输入需要授权的用户ID
------------------
回复"q"退出操作
==================""")
        
        target_user = sender.input(60000, 1, False)
        if not target_user or target_user.lower() == 'q':
            sender.reply("✅ 已退出授权")
            return
        
        accountlist = middleware.bucketGet('dd_ks_user', target_user)
        if not accountlist:
            sender.reply(f"❌ 未找到用户 {target_user} 的账号信息")
            return
        
        try:
            accounts = eval(accountlist)
            if isinstance(accounts, str):
                accounts = [accounts]
            
            # 过滤对应版本的账号
            version_accounts = []
            for account in accounts:
                full_ck = middleware.bucketGet('dd_ks_token', account)
                if full_ck:
                    token_info = parse_token(full_ck)
                    if token_info and token_info['version'] == version_choice:
                        version_accounts.append(account)
            
            if not version_accounts:
                sender.reply(f"❌ 用户 {target_user} 没有{version_name}账号")
                return
            
            # 显示账号列表
            account_list = f"""
======={version_name}账号列表=====
[0] 授权所有账号
------------------"""
            
            for i, account in enumerate(version_accounts, 1):
                auth_status = middleware.bucketGet('dd_ks_auth', account)
                vip_status = auth_status if auth_status else '未授权'
                
                full_ck = middleware.bucketGet('dd_ks_token', account)
                if full_ck:
                    token_info = parse_token(full_ck)
                    name = token_info['name'] if token_info else account
                else:
                    name = account
                
                account_list += f"\n[{i}] {name}\n    授权至: {vip_status}\n------------------"
            
            account_list += "\n回复数字选择账号\n回复'q'退出\n=================="
            sender.reply(account_list)
            
            acc_choice = sender.input(60000, 1, False)
            if not acc_choice or acc_choice.lower() == 'q':
                sender.reply("✅ 已退出授权")
                return
            
            try:
                acc_idx = int(acc_choice)
                if acc_idx < 0 or acc_idx > len(version_accounts):
                    sender.reply(f"❌ 请输入 0-{len(version_accounts)} 之间的数字")
                    return
            except:
                sender.reply("❌ 请输入正确的数字")
                return
            
            # 输入授权月数
            sender.reply("""
=====请输入授权月数=====
------------------
回复数字设置月数
回复"q"退出操作
==================""")
            
            months_input = sender.input(60000, 1, False)
            if not months_input or months_input.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
            
            try:
                months = int(months_input)
                if months <= 0:
                    sender.reply("❌ 月数必须大于0")
                    return
            except:
                sender.reply("❌ 月数必须是数字!")
                return
            
            days = months * 30
            
            # 批量授权或单个授权
            if acc_idx == 0:
                target_accounts = version_accounts
            else:
                target_accounts = [version_accounts[acc_idx - 1]]
            
            success_count = 0
            fail_count = 0
            
            for account in target_accounts:
                try:
                    token = middleware.bucketGet('dd_ks_token', account)
                    if not token:
                        fail_count += 1
                        continue
                    
                    # 计算新的授权时间
                    current_auth = middleware.bucketGet('dd_ks_auth', account)
                    today = datetime.now().date()
                    
                    if current_auth and current_auth > str(today):
                        auth_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
                        new_auth_date = auth_date + timedelta(days=days)
                    else:
                        new_auth_date = today + timedelta(days=days)
                    
                    new_auth_str = str(new_auth_date)
                    
                    # 更新授权时间
                    middleware.bucketSet('dd_ks_auth', account, new_auth_str)
                    
                    # 更新青龙变量（只更新对应版本）
                    token_info = parse_token(token)
                    name = token_info['name'] if token_info else account
                    qinglong_value = token_to_qinglong_format(token)
                    
                    try:
                        Addenvs(osname=target_varname, value=qinglong_value, account=account, phone=name)
                    except:
                        pass
                    
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    print(f"授权账号失败: {str(e)}")
            
            result_msg = f"""
=====授权操作完成=====
📱 版本: {version_name}
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {months} 月
=================="""
            sender.reply(result_msg)
            
        except Exception as e:
            sender.reply(f"❌ 操作失败: {str(e)}")
    
    elif choice == '3':
        # 更新青龙变量
        sender.reply("🔄 正在同步青龙变量...")
        
        users = middleware.bucketAllKeys('dd_ks_user')
        if not users:
            sender.reply("❌ 未找到任何绑定账号")
            return
        
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        for user in users:
            accountlist = middleware.bucketGet('dd_ks_user', user)
            if not accountlist:
                continue
            
            try:
                accounts = eval(accountlist)
                if isinstance(accounts, str):
                    accounts = [accounts]
                
                for account in accounts:
                    try:
                        auth_status = middleware.bucketGet('dd_ks_auth', account)
                        
                        # 只同步已授权且未过期的账号
                        if not auth_status or auth_status <= str(datetime.now().date()):
                            skip_count += 1
                            continue
                        
                        token = middleware.bucketGet('dd_ks_token', account)
                        if not token:
                            fail_count += 1
                            continue
                        
                        token_info = parse_token(token)
                        name = token_info['name'] if token_info else account
                        
                        # 同步到青龙
                        try:
                            Addenvs(target_varname=ks_fast_varname, value=token, account=account, name=name, expire_time=auth_status)
                        except:
                            pass
                        
                        try:
                            Addenvs(target_varname=ks_normal_varname, value=token, account=account, name=name, expire_time=auth_status)
                        except:
                            pass
                        
                        success_count += 1
                    except:
                        fail_count += 1
            except:
                continue
        
        result_msg = f"""
=====同步完成=====
✅ 成功: {success_count} 个账号
⏭️ 跳过: {skip_count} 个账号
❌ 失败: {fail_count} 个账号
=================="""
        sender.reply(result_msg)

def admin_share_statistics():
    """分成统计"""
    if not use_share_mode:
        sender.reply("❌ 未启用分成模式")
        return
    
    today = str(datetime.now().date())
    
    # 获取所有用户
    all_users = middleware.bucketAllKeys('dd_ks_user')
    if not all_users:
        sender.reply("❌ 未找到任何用户")
        return
    
    paid_count = 0
    unpaid_count = 0
    total_revenue = 0.0
    total_share = 0.0
    
    paid_list = []
    unpaid_list = []
    
    for user in all_users:
        try:
            accountlist = middleware.bucketGet('dd_ks_user', user)
            if not accountlist:
                continue
            
            accounts = eval(accountlist)
            if isinstance(accounts, str):
                accounts = [accounts]
            
            for account in accounts:
                today_key = f"share_{account}_{today}"
                today_data = middleware.bucketGet('dd_ks_share', today_key)
                
                if today_data:
                    try:
                        data = json.loads(today_data)
                        is_paid = data.get('is_paid', False)
                        revenue = float(data.get('revenue', 0))
                        share_amount = float(data.get('share_amount', 0))
                        
                        # 获取账号名称
                        full_ck = middleware.bucketGet('dd_ks_token', account)
                        if full_ck:
                            token_info = parse_token(full_ck)
                            name = token_info['name'] if token_info else account
                        else:
                            name = account
                        
                        if is_paid:
                            paid_count += 1
                            total_revenue += revenue
                            total_share += share_amount
                            paid_list.append(f"✅ {name}: {revenue}元 → {share_amount}元")
                        else:
                            unpaid_count += 1
                            unpaid_list.append(f"⏳ {name}: {revenue}元 → {share_amount}元")
                    except:
                        pass
        except:
            continue
    
    # 生成统计报告
    report = f"""
=====今日分成统计=====
📅 日期: {today}
📈 分成比例: {share_rate}%
------------------
💰 总收益: {total_revenue:.2f}元
💵 总分成: {total_share:.2f}元
------------------
✅ 已结算: {paid_count}个账号
⏳ 未结算: {unpaid_count}个账号
=================="""
    
    sender.reply(report)
    
    # 显示详细列表
    if paid_list or unpaid_list:
        detail_menu = """
=====查看详情=====
[1] 查看已结算列表
[2] 查看未结算列表
[3] 查看全部列表
------------------
回复数字查看详情
回复"q"退出
=================="""
        sender.reply(detail_menu)
        
        choice = sender.input(60000, 1, False)
        
        if choice == '1' and paid_list:
            detail = "\n=====已结算列表=====\n" + "\n".join(paid_list)
            sender.reply(detail)
        elif choice == '2' and unpaid_list:
            detail = "\n=====未结算列表=====\n" + "\n".join(unpaid_list)
            sender.reply(detail)
        elif choice == '3':
            all_list = paid_list + unpaid_list
            detail = "\n=====全部列表=====\n" + "\n".join(all_list[:20])
            if len(all_list) > 20:
                detail += f"\n...(共{len(all_list)}条，仅显示前20条)"
            sender.reply(detail)

def admin_clean_accounts():
    """清理过期账号"""
    users = middleware.bucketAllKeys('dd_ks_user')
    
    if not users:
        sender.reply("❌ 未找到任何绑定账号")
        return
    
    sender.reply(f"🔄 开始清理，共找到: {len(users)}个用户\n⏳ 清理中请稍候...")
    
    cleaned_count = 0
    today = str(datetime.now().date())
    
    for user in users:
        try:
            accountlist = middleware.bucketGet('dd_ks_user', user)
            if not accountlist:
                continue
            
            accounts = eval(accountlist)
            if isinstance(accounts, str):
                accounts = [accounts]
            
            valid_accounts = []
            
            for account in accounts:
                auth_status = middleware.bucketGet('dd_ks_auth', account)
                
                # 如果未授权或已过期，清理账号
                if not auth_status or auth_status <= today:
                    try:
                        # 从青龙删除环境变量
                        disable_account_in_qinlong(account, ks_fast_varname)
                        disable_account_in_qinlong(account, ks_normal_varname)
                    except:
                        pass
                    
                    # 删除账号数据
                    middleware.bucketDel('dd_ks_token', account)
                    middleware.bucketDel('dd_ks_auth', account)
                    cleaned_count += 1
                else:
                    valid_accounts.append(account)
            
            # 去重有效账号
            valid_accounts = list(dict.fromkeys(valid_accounts))
            
            # 更新用户账号列表
            if valid_accounts:
                middleware.bucketSet('dd_ks_user', user, str(valid_accounts))
            else:
                middleware.bucketDel('dd_ks_user', user)
        
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    
    sender.reply(f"""
=====清理完成=====
✅ 已清理: {cleaned_count}个账号
==================""")

def main():
    """主函数"""
    global ks_fast_varname, ks_normal_varname, allow_proxy, dd_ks_qlname, QLurl, qltoken, today_time
    global ksVipmoney, kscoin, use_share_mode, share_rate
    
    # 初始化配置
    ks_fast_varname, ks_normal_varname, allow_proxy, dd_ks_qlname, dd_managecommand, dd_querycommand, dd_signcommand, \
    ksVipmoney, kscoin, use_ma_pay, use_share_mode, share_rate = getusercontent()
    
    QLurl, qltoken = seekql()
    today_time = str(datetime.now().date())
    msg = sender.getMessage()
    
    # 检查是否是定时任务触发
    imtype = sender.getImtype()
    if imtype == 'fake':
        # 定时任务：检查分成支付状态
        check_share_payment_status()
        return
    
    # 路由处理
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
    elif '教程' in msg:
        sender.reply("""
=====快手使用教程=====
🔍 功能: 快手登录 | 快手查询 | 快手管理
💡 格式: 备注#Cookie#Salt#|端口|用户|密码|过期
📝 版本: 极速版 | 普通版
==================""")
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
