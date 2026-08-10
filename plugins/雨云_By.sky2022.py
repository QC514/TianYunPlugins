#[pin:false]
#[disable:true]
#[public:true]
#[rule: ^(雨云登录|雨云登陆|登陆雨云|登录雨云|雨云查询|查询雨云|雨云管理|管理雨云|雨云授权|雨云教程)$]
#[version: 1.1.1]
#[price: 12.88]
#[title: 雨云]
#[author: sky2022]
#[admin: false]
#[cron: 1 8,15 * * *]
#[icon: https://www.rainyun.com/img/logo.d193755d.png]
#[description: 指令:雨云登陆 雨云查询 雨云管理 支持账号#密码登陆，支持多账号管理丨定时任务：每天8点和15点自动检测授权过期及CK失效并推送通知丨V1.1.1:新增定时检测推送，每天8点/15点自动检测授权到期和账号失效状态并通知用户丨V1.1.0:统一面板配置为面板类型+对接面板配置，并新增呆呆面板分组配置]

import re
import middleware
import requests
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal 
import base64
import random
import time
import urllib3
from urllib.parse import unquote

# 禁用 SSL 警告
urllib3.disable_warnings()

# 禁用 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# [param: {"required":true,"key":"dd_Rainyun_PluginsData.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_Rainyun_PluginsData.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_Rainyun_PluginsData.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_Rainyun_PluginsData.panel_group","bool":false,"placeholder":"例:雨云","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# 变量名
# [param: {"required":true,"key":"dd_Rainyun_PluginsData.osname","bool":false,"placeholder":"必填项,例:rainyun","name":"面板变量名","desc":"提交到面板中的雨云变量名"}]
# 上车价格
# [param: {"required":true,"key":"dd_Rainyun_PluginsData.RainyunVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# 积分上车价格
# [param: {"required":true,"key":"dd_Rainyun_PluginsData.Rainyuncoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_Rainyun_bind', key=userid) or ''

def normalize_panel_type(panel_type_value):
    """统一解析面板类型。"""
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    return ''

def login(value):
    """登录雨云账号"""
    try:
        values = value.split('#')
        if len(values) != 2:
            return "登录参数格式错误", "登录失败", False
            
        username = values[0]
        password = values[1]
        
        url = "https://api.v2.rainyun.com/user/login"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "x-csrf-token": "undefined",
            "origin": "https://app.rainyun.com",
            "referer": "https://app.rainyun.com/",
            "accept-language": "zh-CN,zh;q=0.9"
        }
        
        data = {
            "field": username,
            "password": password
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get('code') != 200:
            return f"登录失败: {result.get('message', '未知错误')}", "登录失败", False
            
        # 获取csrf token
        csrf_token = response.cookies.get('X-CSRF-Token')
        if not csrf_token:
            return "获取Token失败", "登录失败", False
            
        # 构造token字符串
        token = f"{username}#{password}#{csrf_token}"
        
        return username, csrf_token, token
        
    except Exception as e:
        return f"登录异常: {str(e)}", "登录异常", False

def bind():
    """绑定雨云账号"""
    sender.reply(
        "=====雨云账号登录=====\n"
        "📝 请输入登录参数:\n"
        "格式: 账号#密码\n"
        "⚠️ 建议私聊登录,密码泄露风险自负\n"
        "⭐ 输入q退出操作\n"
        "====================="
    )
    
    login_value = sender.input(120000, 1, False)
    if login_value == '':
        sender.reply('输入超时！')
        exit(0)
    elif login_value.lower() == 'q':
        sender.reply('退出操作！')
        exit(0)
        
    try:
        values = login_value.split('#')
        if len(values) != 2:
            sender.reply('输入格式错误！需要账号#密码格式')
            exit(0)
    except:
        exit(0)
        
    account, loginToken, token = login(login_value)
    if token is False:
        sender.reply(f'{account}')
        exit(0)
        
    middleware.bucketSet(bucket='dd_Rainyun_account', key=account, value=token)
    # 保存原始登录信息
    middleware.bucketSet(bucket='dd_Rainyun_login', key=account, value=login_value)
    accountVip = middleware.bucketGet(bucket='dd_Rainyun_Vip', key=account) or ''
    
    if len(uservalue) == 0:
        accounts = []
        accounts.append(account)
        middleware.bucketSet(bucket='dd_Rainyun_bind', key=userid, value=f'{accounts}')
        if len(accountVip) != 0 and accountVip >= today_time:
            Addenvs(osname=osname, value=login_value, account=account)
            sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[雨云管理]管理账号\n🔍 发送[雨云查询]查询状态\n===================")
        else:
            sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[雨云管理]管理账号\n🔍 发送[雨云查询]查询状态\n===================")
    else:
        accounts = eval(uservalue)
        if account in accounts:
            if len(accountVip) != 0 and accountVip >= today_time:
                Addenvs(osname=osname, value=login_value, account=account)
                sender.reply("更新账号成功，可对我说'雨云管理'对账号进行管理！")
            else:
                sender.reply("更新账号成功,授权已过期！")
        else:
            accounts.append(account)
            middleware.bucketSet(bucket='dd_Rainyun_bind', key=userid, value=f'{accounts}')
            if len(accountVip) != 0 and accountVip >= today_time:
                Addenvs(osname=osname, value=login_value, account=account)
                sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[雨云管理]管理账号\n🔍 发送[雨云查询]查询状态\n===================")
            else:
                sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[雨云管理]管理账号\n🔍 发送[雨云查询]查询状态\n===================")

def query_balance(token):
    """查询雨云账户积分"""
    try:
        values = token.split('#')
        if len(values) != 3:
            return "获取账号信息失败", 0
            
        username = values[0]
        password = values[1]
        
        # 重新登录获取token
        url = "https://api.v2.rainyun.com/user/login"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "x-csrf-token": "undefined",
            "origin": "https://app.rainyun.com",
            "referer": "https://app.rainyun.com/",
            "accept-language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json"
        }
        
        data = {
            "field": username,
            "password": password
        }
        
        session = requests.Session()
        response = session.post(url, headers=headers, json=data, verify=False)
        if response.status_code != 200:
            return f"登录失败: HTTP {response.status_code}", 0
            
        result = response.json()
        if result.get('code') != 200:
            return f"登录失败: {result.get('message', '未知错误')}", 0
            
        # 从Set-Cookie中提取session和csrf token
        cookies = response.headers.get('Set-Cookie', '')
        session_cookie = None
        csrf_token = None
        
        for cookie in cookies.split(', '):
            if 'rain-session=' in cookie:
                session_cookie = cookie.split(';')[0]
            elif 'X-CSRF-Token=' in cookie:
                csrf_token = cookie.split('=')[1].split(';')[0]
                
        if not session_cookie or not csrf_token:
            return "无法获取必要的Cookie信息", 0
            
        # 查询用户信息
        user_url = "https://api.v2.rainyun.com/user/?no_cache=false"
        user_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "x-csrf-token": csrf_token,
            "origin": "https://app.rainyun.com",
            "referer": "https://app.rainyun.com/",
            "accept-language": "zh-CN,zh;q=0.9",
            "Cookie": f"{session_cookie}; X-CSRF-Token={csrf_token}"
        }
        
        user_response = session.get(user_url, headers=user_headers, verify=False)
        if user_response.status_code != 200:
            return f"查询用户信息失败: HTTP {user_response.status_code}", 0
            
        user_result = user_response.json()
        if user_result.get('code') != 200:
            return f"查询用户信息失败: {user_result.get('message', '未知错误')}", 0
            
        points = user_result['data']['Points']
        return points, 1
        
    except Exception as e:
        return f"查询异常: {str(e)}", 0

def query():
    """查询雨云账号状态"""
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        for account in accounts:
            try:
                accountVip = middleware.bucketGet(bucket='dd_Rainyun_Vip', key=account) or ''
                Token = middleware.bucketGet(bucket='dd_Rainyun_account', key=account)
                if not Token:
                    sender.reply(f'【账号】Token获取失败')
                    continue

                points, status = query_balance(Token)
                if status == 0:
                    sender.reply(f'【账号】{points}')
                    continue

                if len(accountVip) == 0:
                    sender.reply(f'【{account}】账号未授权')
                    continue
                elif accountVip < today_time:
                    sender.reply(f'【{account}】云授权过期')
                    continue
                else:
                    sender.reply(
                        "=====账号详情=====\n"
                        f"📱 账号: {account}\n"
                        f"💎 积分余额: {points}分\n"
                        f"⏰ 授权期限: {accountVip}\n"
                        "==================="
                    )

            except Exception as e:
                sender.reply(f'【{account}】查询出错: {str(e)}')
    else:
        sender.reply('未绑定雨云账号')

def Administration():
    """管理雨云账号"""
    accst = '状态正常'
    message = ''
    count = 1
    
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        # 显示账号列表
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='dd_Rainyun_Vip', key=account) or ''
            Token = middleware.bucketGet(bucket='dd_Rainyun_account', key=account)
            
            try:
                # 验证账号状态
                points, _ = query_balance(Token)
                if isinstance(points, str):
                    accst = '账号失效'
            except:
                accst = '账号异常'
                
            if len(accountVip) == 0:
                accvip = '未授权'
            elif accountVip < today_time:
                accvip = '授权过期'
            else:
                accvip = accountVip
                
            message += (
                f"[{count}] 账号信息\n"
                f"📱 账号: {account}\n"
                f"💫 状态: {accst}\n"
                f"⏰ 到期: {accvip}\n"
                f"-------------------\n"
            )
            count += 1
            
        # 选择要管理的账号
        sender.reply(
            f"====雨云管理====\n"
            f"{message}"
            "📝 请输入[]中需要管理的账号\n"
            "⚠️ 输入q退出操作"
        )
        mes = sender.input(120000, 1, False)
        if mes.lower() == 'q':
            sender.reply('退出操作')
            exit(0)
            
        try:
            mes = int(mes)
            if mes < 1 or mes >= count:
                sender.reply('输入的账号序号无效')
                exit(0)
        except:
            sender.reply('输入有误，请输入数字')
            exit(0)
            
        # 获取选中的账号信息
        selected_account = accounts[mes - 1]
        accountVip = middleware.bucketGet(bucket='dd_Rainyun_Vip', key=selected_account) or ''
        Token = middleware.bucketGet(bucket='dd_Rainyun_account', key=selected_account)

        # 处理授权状态显示的一致性
        if len(accountVip) == 0:
            display_vip = '未授权'
        elif accountVip < today_time:
            display_vip = '授权过期'
        else:
            display_vip = accountVip
        
        # 显示账号管理选项
        message = (
            "=====账号详情=====\n"
            f"📱 账号: {selected_account}\n"
            f"💫 状态: {accst}\n"
            f"⏰ 到期: {display_vip}\n"
            "-------------------\n"
            "🔧 管理选项:\n"
            "  [1] 📅 授权账号\n"
            "  [2] ❌ 删除账号\n"
            "⚠️ 输入q退出操作\n"
            "==================="
        )
        sender.reply(message)

        # 选择管理操作
        mes = sender.input(120000, 1, False)
        if mes.lower() == 'q':
            sender.reply('退出操作')
            exit(0)
            
        try:
            mes = int(mes)
            if mes < 1 or mes > 2:
                sender.reply('输入的选项无效')
                exit(0)
        except:
            sender.reply('输入有误，请输入数字')
            exit(0)

        # 获取选中的账号信息
        selected_account = accounts[mes - 1]
        accountVip = middleware.bucketGet(bucket='dd_Rainyun_Vip', key=selected_account) or ''
        Token = middleware.bucketGet(bucket='dd_Rainyun_account', key=selected_account)
        
        if mes == 1:  # 授权账号
            sender.reply(
                "=====授权时长=====\n"
                "📝 请输入需要的月数\n"
                "💡 示例: 输入1代表1个月\n"
                "⚠️ 输入q退出操作\n"
                "==================="
            )
            
            months = sender.input(120000, 1, False)
            if months.lower() == 'q':
                sender.reply('退出操作')
                exit(0)
                
            try:
                months = int(months)
                if months < 1 or months > 99:
                    sender.reply('输入的月数无效')
                    exit(0)
            except:
                sender.reply('输入有误，请输入数字')
                exit(0)
                
            # 执行授权
            if not zf(project='雨云授权', me_as_int=months, accountVip=accountVip, account=selected_account, token=Token):
                sender.reply('授权失败')
                return
            
            # 计算新的到期时间
            new_expire_date = empower(empowertime=accountVip, me_as_int=months)
            middleware.bucketSet(bucket='dd_Rainyun_Vip', key=selected_account, value=new_expire_date)
            
            # 获取原始登录信息并更新青龙变量
            login_value = middleware.bucketGet('dd_Rainyun_login', selected_account)
            if login_value:
                Addenvs(osname=osname, value=login_value, account=selected_account)
            
            sender.reply(
                "=====授权成功=====\n"
                f"📱 账号: {selected_account}\n"
                f"⏰ 到期时间: {new_expire_date}\n"
                "==================="
            )
            
        elif mes == 2:  # 删除账号
            sender.reply(
                "=====删除确认=====\n"
                f"📱 账号: {selected_account}\n"
                "是否删除这个账号?\n"
                "[y]确认删除 | [n]取消操作\n"
                "⚠️ 输入q退出操作\n"
                "==================="
            )
            yesorno = sender.input(120000, 1, False)
            if yesorno.lower() == 'y' or yesorno == '是':
                try:
                    # 删除青龙变量
                    qlid = allenvs(osname=osname, account=selected_account)
                    if qlid:
                        delenvs(id=qlid)
                    
                    # 从账号列表中移除
                    if selected_account in accounts:
                        accounts.remove(selected_account)
                        # 更新或删除用户绑定信息
                        if len(accounts) == 0:
                            middleware.bucketDel(bucket='dd_Rainyun_bind', key=userid)
                        else:
                            middleware.bucketSet(bucket='dd_Rainyun_bind', key=userid, value=f'{accounts}')
                        # 删除账号相关的其他数据
                        middleware.bucketDel(bucket='dd_Rainyun_account', key=selected_account)
                        middleware.bucketDel(bucket='dd_Rainyun_Vip', key=selected_account)
                        sender.reply('删除完成！')
                    else:
                        sender.reply('账号不存在！')
                except Exception as e:
                    sender.reply(f'删除失败: {str(e)}')
            elif yesorno.lower() == 'n' or yesorno == '否':
                sender.reply('已取消删除')
            elif yesorno.lower() == 'q':
                sender.reply('退出操作')
            else:
                sender.reply('输入有误！')
            exit(0)
    else:
        sender.reply('未绑定雨云账号！')
        exit(0)

def PluginsData():
    """获取插件配置数据"""
    panel_type = normalize_panel_type(middleware.bucketGet(bucket='dd_Rainyun_PluginsData', key='panel_type') or '')
    if not panel_type:
        sender.reply('对接面板类型填写无效，请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai')
        exit(0)

    panel_config = (middleware.bucketGet(bucket='dd_Rainyun_PluginsData', key='panel_config') or '').strip()
    RainyunVipmoney = middleware.bucketGet(bucket='dd_Rainyun_PluginsData', key='RainyunVipmoney')
    osname = middleware.bucketGet(bucket='dd_Rainyun_PluginsData', key='osname')
    Rainyuncoin = middleware.bucketGet(bucket='dd_Rainyun_PluginsData', key='Rainyuncoin')
    panel_group = (middleware.bucketGet(bucket='dd_Rainyun_PluginsData', key='panel_group') or '').strip()
    
    if not panel_config:
        if panel_type == 'qinglong':
            sender.reply('未配置青龙面板信息，请填写：对接面板类型=青龙，对接面板配置=Host丨ClientID丨ClientSecret')
        else:
            sender.reply('未配置呆呆面板信息，请填写：对接面板类型=呆呆，对接面板配置=Host丨AppKey丨AppSecret')
        exit(0)
    
    qllist = panel_config.split('丨')
    if len(qllist) != 3:
        if panel_type == 'qinglong':
            sender.reply('青龙面板配置格式错误，请使用"丨"分隔 URL、ClientID 和 ClientSecret')
        else:
            sender.reply('呆呆面板配置格式错误，请使用"丨"分隔 URL、AppKey 和 AppSecret')
        exit(0)
        
    QLurl = qllist[0]
    ClientID = qllist[1]
    ClientSecret = qllist[2]
    
    # 处理 RainyunVipmoney
    if not RainyunVipmoney or RainyunVipmoney == '0':
        RainyunVipmoney = Decimal('0')
    else:
        try:
            RainyunVipmoney = Decimal(str(RainyunVipmoney))
        except:
            RainyunVipmoney = Decimal('0')
    
    # 检查 osname
    if not osname:
        sender.reply('雨云未填写变量信息，请检查配参信息！')
        exit(0)
    
    # 处理 Rainyuncoin
    if not Rainyuncoin:
        Rainyuncoin = 9999
    else:
        try:
            Rainyuncoin = int(Rainyuncoin)
        except:
            Rainyuncoin = 9999
            
    return QLurl, ClientID, ClientSecret, RainyunVipmoney, osname, Rainyuncoin, panel_type == 'daidai', panel_group

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙Token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        if "token" in response.text:
            result = response.json()
            return result['data']['token']
    except Exception:
        sender.reply("链接青龙失败,请检查对接容器！")
        exit(0)

def DDtoken(DDurl, AppKey, AppSecret):
    """获取呆呆面板Token"""
    try:
        url = f'{DDurl}/api/open-api/token'
        response = requests.post(url, json={"app_key": AppKey, "app_secret": AppSecret})
        if response.status_code != 200:
            sender.reply("链接呆呆面板失败,请检查对接面板配置！")
            exit(0)
        result = response.json()
        access_token = result.get('data', {}).get('access_token')
        if access_token:
            return access_token
        sender.reply("获取呆呆面板Token失败，请检查 AppKey/AppSecret")
        exit(0)
    except Exception:
        sender.reply("链接呆呆面板失败,请检查对接面板配置！")
        exit(0)

def Addenvs(osname, value, account):
    """添加或更新青龙变量"""
    try:
        qlid = None
        if use_daidai:
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            response = requests.get(url=f"{QLurl}/api/envs", headers=headers, params={"keyword": str(account), "page_size": 100}).json()
            data_list = response.get('data', [])
            if isinstance(data_list, list):
                for envs in data_list:
                    remarks = envs.get('remarks', '')
                    if remarks and account in remarks and osname == envs.get('name'):
                        qlid = envs['id']
                        break
            else:
                sender.reply('连接呆呆面板获取变量失败')
                return False
        else:
            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json"
            }
            response = requests.get(url=url, headers=headers).json()
            if response['code'] == 200:
                envslist = response['data']
                for envs in envslist:
                    remarks = envs.get('remarks', '')
                    if remarks and account in remarks and osname == envs['name']:
                        qlid = envs['id']
                        break
            else:
                sender.reply('连接青龙获取变量失败')
                return False
            
        if qlid is None:
            return QLzt(osname, value, account)
        else:
            return QLupdate(osname, value, account, qlid)
    except Exception as e:
        sender.reply(f'添加/更新青龙变量失败: {str(e)}')
        return False

def QLzt(osname, value, account):
    """添加青龙变量"""
    try:
        if use_daidai:
            url = f"{QLurl}/api/envs"
            data = {
                "value": value,
                "name": osname,
                "remarks": f'雨云:{account}丨用户:{userid}丨雨云管理'
            }
            if panel_group:
                data["group"] = panel_group
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            r = requests.post(url, headers=headers, json=data)
            return r.status_code in (200, 201)
        else:
            qlurl = f"{QLurl}/open/envs"
            data = [{
                "value": value,
                "name": osname,
                "remarks": f'雨云:{account}丨用户:{userid}丨雨云管理'
            }]
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            r = requests.post(qlurl, headers=headers, data=json.dumps(data))
            r_json = r.json()
            
            if r.status_code != 200:
                sender.reply(f"添加变量失败: {r_json.get('message', '未知错误')}")
                return False
                
            if "value must be unique" in r.text:
                return True
                
            if r_json.get('code') == 200:
                return True
            else:
                sender.reply(f"添加变量失败: {r_json.get('message', '未知错误')}")
                return False
            
    except Exception as e:
        sender.reply(f"添加面板变量错误: {str(e)}")
        return False

def QLupdate(osname, value, account, qlid):
    """更新青龙变量"""
    try:
        if use_daidai:
            url = f"{QLurl}/api/envs/{qlid}"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            data = {
                "value": value,
                "name": osname,
                "remarks": f'雨云:{account}丨用户:{userid}丨雨云管理'
            }
            if panel_group:
                data["group"] = panel_group
            response = requests.put(url=url, headers=headers, json=data)
            return response.status_code == 200
        else:
            url = f"{QLurl}/open/envs/{qlid}"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json"
            }
            response = requests.put(url=url, headers=headers, json={"value": value})
            r_json = response.json()
            
            if response.status_code != 200:
                sender.reply(f"更新变量失败: {r_json.get('message', '未知错误')}")
                return False
                
            if r_json.get('code') == 200:
                return True
            else:
                sender.reply(f"更新变量失败: {r_json.get('message', '未知错误')}")
                return False
            
    except Exception as e:
        sender.reply(f"更新面板变量错误: {str(e)}")
        return False

def allenvs(osname, account):
    """获取指定账号的青龙变量ID"""
    try:
        if use_daidai:
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json"
            }
            response = requests.get(url=f"{QLurl}/api/envs", headers=headers, params={"keyword": str(account), "page_size": 100}).json()
            data_list = response.get('data', [])
            if isinstance(data_list, list):
                for envs in data_list:
                    remarks = envs.get('remarks', '')
                    if remarks and account in remarks and osname == envs.get('name'):
                        return envs['id']
            return None
        else:
            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json"
            }
            response = requests.get(url=url, headers=headers).json()
            
            if response['code'] == 200:
                envslist = response['data']
                for envs in envslist:
                    remarks = envs.get('remarks', '')
                    if remarks and account in remarks and osname == envs['name']:
                        return envs['id']
            return None
        
    except Exception as e:
        sender.reply(f'获取变量ID失败: {str(e)}')
        return None

def delenvs(id):
    """删除青龙变量"""
    try:
        if use_daidai:
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            response = requests.delete(url=f"{QLurl}/api/envs/{id}", headers=headers)
            return response.status_code == 200
        else:
            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            response = requests.delete(url=url, headers=headers, data=json.dumps([id]))
            return response.json().get('code') == 200
    except Exception as e:
        sender.reply(f'删除变量失败: {str(e)}')
        return False

def zf(project, me_as_int, accountVip, account, token):
    """处理支付授权"""
    try:
        # 计算支付金额
        money = Decimal(me_as_int) * Decimal(RainyunVipmoney)
        
        # 如果金额为0,直接授权
        if money == 0:
            return True
            
        # 检查是否可以使用积分
        if Rainyuncoin != 9999:
            sender.reply(
                "=====支付方式=====\n"
                f"💰 支付金额: {money}元\n"
                f"💎 所需积分: {me_as_int * Rainyuncoin}分\n"
                "[1] 余额支付\n"
                "[2] 积分支付\n"
                "⚠️ 输入q退出操作\n"
                "=================="
            )
            
            choice = sender.input(60000, 1, False)
            if choice == 'q':
                sender.reply('已取消支付')
                return False
                
            try:
                choice = int(choice)
                if choice == 2:
                    # 检查积分是否足够
                    user_points = middleware.bucketGet('dd_points', userid) or 0
                    needed_points = me_as_int * Rainyuncoin
                    
                    if int(user_points) < needed_points:
                        sender.reply(f'积分不足,当前积分:{user_points},需要积分:{needed_points}')
                        return False
                        
                    # 扣除积分
                    new_points = int(user_points) - needed_points
                    middleware.bucketSet('dd_points', userid, str(new_points))
                    return True
                    
                elif choice != 1:
                    sender.reply('选择无效')
                    return False
            except:
                sender.reply('输入无效')
                return False
                
        # 显示收款码
        zsm = middleware.bucketGet('dd_Rainyun_PluginsData', 'zsm')
        if not zsm:
            sender.reply('未配置收款方式')
            return False
            
        sender.reply(
            "=====扫码支付=====\n"
            f"💰 支付金额: {money}元\n"
            "⚠️ 支付完成后回复[y]\n"
            "⚠️ 输入q退出操作\n"
            "=================="
        )
        sender.image(zsm)
        
        # 等待支付确认
        confirm = sender.input(300000, 1, False)
        if confirm.lower() != 'y':
            sender.reply('已取消支付')
            return False
            
        return True
        
    except Exception as e:
        sender.reply(f'支付处理异常: {str(e)}')
        return False

def empower(empowertime, me_as_int):
    """计算授权到期时间"""
    try:
        if len(empowertime) == 0 or empowertime == '未授权' or empowertime == '授权过期':
            start_date = datetime.now()
        else:
            start_date = datetime.strptime(empowertime, '%Y-%m-%d')
            if start_date.date() < datetime.now().date():
                start_date = datetime.now()
                
        end_date = start_date + timedelta(days=me_as_int * 30)
        return end_date.strftime('%Y-%m-%d')
        
    except Exception as e:
        sender.reply(f'计算授权时间异常: {str(e)}')
        return datetime.now().strftime('%Y-%m-%d')

def tutorial():
    """显示雨云使用教程"""
    tutorial_text = (
        "=====雨云教程=====\n"
        "🌟 基础指令:\n"
        "1️⃣ 雨云登录 - 绑定账号\n" 
        "2️⃣ 雨云查询 - 查看状态\n"
        "3️⃣ 雨云管理 - 管理账号\n"
        "-------------------\n"
        "📝 使用说明:\n"
        "1. 发送[雨云登录]绑定账号\n"
        "2. 按提示输入账号和密码\n"
        "3. 登录成功后可以管理账号\n"
        "4. 定时签到获取奖励\n"
        "-------------------\n"
        "⚠️ 注意事项:\n"
        "1. 建议私聊登录更安全\n"
        "2. 密码不会被保存记录\n"
        "3. 定期更新账号保活\n"
        "=================="
    )
    sender.reply(tutorial_text)

def check_sign(token):
    """检查签到状态"""
    try:
        values = token.split('#')
        if len(values) != 3:
            return False
            
        username = values[0]
        csrf_token = values[2]
        
        url = "https://api.v2.rainyun.com/user/reward/sign-in"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "x-csrf-token": csrf_token,
            "origin": "https://app.rainyun.com",
            "referer": "https://app.rainyun.com/",
            "accept-language": "zh-CN,zh;q=0.9"
        }
        
        response = requests.post(url, headers=headers)
        result = response.json()
        
        if result.get('code') == 200:
            return True
        elif "今日已签到" in result.get('message', ''):
            return True
        else:
            return False
            
    except Exception as e:
        print(f"签到检查异常: {str(e)}")
        return False

# 主程序入口
today_date = datetime.now().date()
today_time = str(today_date)
QLurl, ClientID, ClientSecret, RainyunVipmoney, osname, Rainyuncoin, use_daidai, panel_group = PluginsData()
if use_daidai:
    qltoken = DDtoken(QLurl, ClientID, ClientSecret)
else:
    qltoken = QLtoken(QLurl, ClientID, ClientSecret)
usermessage = sender.getMessage()

if usermessage in ['雨云登录', '雨云登陆', '登陆雨云', '登录雨云']:
    bind()
elif usermessage in ['雨云管理', '管理雨云']:
    Administration()
elif usermessage in ['雨云查询', '查询雨云']:
    query()
elif usermessage == '雨云教程':
    tutorial()
elif usermessage == 'fake':
    """定时任务处理 - 8点/15点检测授权过期及CK失效"""
    users = middleware.bucketAllKeys(bucket='dd_Rainyun_bind')
    if not users:
        exit(0)
    
    today = datetime.now().date()
    three_days_later = today + timedelta(days=3)
    
    for user in users:
        try:
            uservalue = middleware.bucketGet(bucket='dd_Rainyun_bind', key=user) or ''
            if not uservalue:
                continue
                
            accounts = eval(uservalue)
            for account in accounts:
                try:
                    Token = middleware.bucketGet(bucket='dd_Rainyun_account', key=account)
                    accountVip = middleware.bucketGet(bucket='dd_Rainyun_Vip', key=account) or ''
                    
                    if not Token:
                        continue
                    
                    phone = account[:3] + '****' + account[7:] if len(account) >= 11 else account
                    
                    # 检查授权状态
                    if len(accountVip) == 0 or accountVip < str(today):
                        push_msg = f"""
=====雨云账号通知=====
📱 账号: {phone}
⏰ 定时检测提醒
------------------
❌ 授权已过期
💡 请及时续费授权
=================="""
                        for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                            try:
                                middleware.push(platform, '', user, '', push_msg)
                            except:
                                pass
                    else:
                        try:
                            expire_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                            if today <= expire_date <= three_days_later:
                                days_left = (expire_date - today).days
                                push_msg = f"""
=====雨云账号通知=====
📱 账号: {phone}
⏰ 定时检测提醒
------------------
⚠️ 授权即将到期
� 到期时间: {accountVip}
⏳ 剩余天数: {days_left}天
💡 请及时续费授权
=================="""
                                for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                                    try:
                                        middleware.push(platform, '', user, '', push_msg)
                                    except:
                                        pass
                        except Exception as e:
                            print(f"检查账号 {account} 过期时间时出错: {str(e)}")
                            continue
                            
                except Exception as e:
                    print(f"处理账号 {account} 时出错: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
