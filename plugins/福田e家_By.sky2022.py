#[disable:true]
#[pin:false]
#[public:true]
# [rule: ^福田登录$|^福田登陆$|^登陆福田$|^登录福田$|^福田查询$|^查询福田$|^福田管理$|^管理福田$|^福田授权$|^清理福田$|^福田清理$|^福田订单查询$|^福田批量登录$|^福田批量登陆$|^批量登录福田$|^批量登陆福田$]
# [version: 5.0]
# [price: 12.88]
# [author: sky2022]
# [title: 福田e家]
# [cron: 18 8,15 * * *]
# [icon: https://images.mingming.dev/file/7c1c97c112588fbf7c0db.png]
# [description: 指令:福田登陆 福田查询 福田管理 福田订单 福田批量登录 对接青龙/呆呆面板<br>定时任务：每天8点和15点自动检测授权过期及CK失效并推送通知<br>4.9更新：新增定时检测推送，每天8点/15点自动检测授权到期和账号失效状态并通知用户<br>更新：新增批量登录功能，支持账号#密码格式一行一个的批量导入<br>更新：新增订单查询功能，可查看积分商城购买记录<br>更新：新增管理员授权指令：福田授权<br><br>更新：适配BOGW和GW框架的收款<br>更新：福田抢购会显示本期的抢购信息<br>3.4更新：优化赞赏码支付，同时新增码支付，需使用市场卡密系统！<br>4.8更新：统一面板配置为面板类型+对接面板配置，并新增呆呆面板分组配置]
import re
import middleware
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
import base64
import hashlib
import time

# [param: {"required":true,"key":"dd_fukuda_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_fukuda_config.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_fukuda_config.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_fukuda_config.panel_group","bool":false,"placeholder":"例:福田","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_fukuda_config.osname","bool":false,"placeholder":"必填项,例:Fukuda","name":"面板变量名","desc":"提交到面板中的福田e家变量名"}]
# [param: {"required":true,"key":"dd_fukuda_config.FukudaVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_fukuda_config.Fukudacoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_fukuda_config.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# [param: {"required":false,"key":"dd_fukuda_config.expire_notify","bool":true,"placeholder":"","name":"过期提醒","desc":"是否开启账号过期提醒推送(默认开启)"}]
# [param: {"required":false,"key":"dd_fukuda_config.proxy_url","bool":false,"placeholder":"例:http://127.0.0.1:8899","name":"代理地址","desc":"登录请求使用的代理拉取接口，返回 http(s)://host:port"}]
senderID = middleware.getSenderID()  # 创建发送者
sender = middleware.Sender(senderID)  # 向用户发送消息
userid = sender.getUserID()  # 消息接收者
uservalue = middleware.bucketGet(bucket='dd_fukuda_user', key=userid) or ''  # 获取用户的值

def normalize_panel_type(panel_type_value):
    """统一解析面板类型。"""
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    return ''

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        
        if response.status_code != 200:
            sender.reply("""
==================
    请求失败
==================
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
==================
    认证失败
==================
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
==================
    网络错误
==================
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
==================
    系统错误
==================
❌ 处理请求时出错
------------------
请检查:
• 配置格式是否正确
• 错误信息: {str(e)}
==================""")
        exit(0)

def DDtoken(DDurl, AppKey, AppSecret):
    """获取呆呆面板Token"""
    try:
        response = requests.post(f'{DDurl}/api/open-api/token', json={"app_key": AppKey, "app_secret": AppSecret})
        if response.status_code != 200:
            raise Exception(f"请求失败: {response.status_code}")
        result = response.json()
        access_token = result.get('data', {}).get('access_token')
        if access_token:
            return access_token
        raise Exception("获取Token失败")
    except Exception as e:
        sender.reply(f"""
==================
    系统错误
==================
❌ 获取呆呆面板Token失败
------------------
请检查:
• 配置格式是否正确
• 错误信息: {str(e)}
==================""")
        exit(0)

def PluginsData():
    """获取插件配置数据"""
    panel_type = normalize_panel_type(middleware.bucketGet(bucket='dd_fukuda_config', key='panel_type') or '')
    if not panel_type:
        sender.reply("对接面板类型填写无效，请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai")
        exit(0)

    panel_config = (middleware.bucketGet(bucket='dd_fukuda_config', key='panel_config') or '').strip()
    FukudaVipmoney = middleware.bucketGet(bucket='dd_fukuda_config', key='FukudaVipmoney')
    osname = middleware.bucketGet(bucket='dd_fukuda_config', key='osname')
    Fukudacoin = middleware.bucketGet(bucket='dd_fukuda_config', key='Fukudacoin')
    use_ma_pay = middleware.bucketGet(bucket='dd_fukuda_config', key='use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    proxy_url = middleware.bucketGet(bucket='dd_fukuda_config', key='proxy_url')
    panel_group = (middleware.bucketGet(bucket='dd_fukuda_config', key='panel_group') or '').strip()
    
    if len(panel_config) == 0:
        if panel_type == 'qinglong':
            sender.reply("""
==================
    配置错误
==================
❌ 未配置青龙面板信息
------------------
请在插件配置中填写:
• 对接面板类型: 青龙
• 对接面板配置: Host丨ClientID丨ClientSecret
==================""")
        else:
            sender.reply("""
==================
    配置错误
==================
❌ 未配置呆呆面板信息
------------------
请在插件配置中填写:
• 对接面板类型: 呆呆
• 对接面板配置: Host丨AppKey丨AppSecret
==================""")
        exit(0)
        
    qllist = panel_config.split('丨')
    if len(qllist) != 3:
        if panel_type == 'qinglong':
            sender.reply(f"""
==================
    格式错误
==================
❌ 青龙面板配置格式错误
------------------
当前格式: {panel_config}
正确格式:
Host丨ClientID丨ClientSecret
==================""")
        else:
            sender.reply(f"""
==================
    格式错误
==================
❌ 呆呆面板配置格式错误
------------------
当前格式: {panel_config}
正确格式:
Host丨AppKey丨AppSecret
==================""")
        exit(0)
        
    QLurl = qllist[0].strip()
    ClientID = qllist[1].strip()
    ClientSecret = qllist[2].strip()
    
    # 验证每个参数是否为空
    if not all([QLurl, ClientID, ClientSecret]):
        sender.reply("""
==================
    参数错误
==================
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
==================
    地址错误
==================
❌ 青龙地址格式错误
------------------
当前地址: {QLurl}
正确格式:
• http://qinglong.example.com
• https://ql.example.com:5700
==================""")
        exit(0)
        
    if len(osname) == 0:
        sender.reply("""
==================
    配置错误
==================
❌ 未配置变量名称
------------------
请在插件配置中填写:
面板变量名
==================""")
        exit(0)
        
    FukudaVipmoney = Decimal(FukudaVipmoney or '0')
    Fukudacoin = int(Fukudacoin or '9999')
    
    return QLurl, ClientID, ClientSecret, FukudaVipmoney, osname, Fukudacoin, use_ma_pay, proxy_url, panel_type == 'daidai', panel_group

def update_proxy(session, proxy_url):
    """更新代理配置到给定会话"""
    if not proxy_url:
        return
    try:
        ip = requests.get(proxy_url).text
        if not ip or '请先添加白名单' in ip:
            return
        session.proxies = {'http': ip, 'https': ip}
    except Exception:
        return

def get_proxy() -> dict | None:
    """获取代理字典{'http': url, 'https': url}，获取失败返回None"""
    try:
        if not proxy_url:
            return None
        ip = requests.get(proxy_url, timeout=8).text
        if not ip or '请先添加白名单' in ip:
            return None
        return {'http': ip, 'https': ip}
    except Exception:
        return None

def create_proxy_session(headers: dict | None=None):
    """创建携带代理与可选headers的requests会话"""
    session = requests.Session()
    if headers:
        session.headers.update(headers)
    update_proxy(session, proxy_url)
    return session

def allenvs(osname, account):
    """获取青龙环境变量"""
    if use_daidai:
        url = f"{QLurl}/api/envs"
        headers = {
            "Authorization": f"Bearer {qltoken}",
            "accept": "application/json"
        }
    else:
        url = f"{QLurl}/open/envs"
        headers = {
            "Authorization": f"Bearer {qltoken}",
            "accept": "application/json"
        }
    
    try:
        if use_daidai:
            response = requests.get(url=url, headers=headers, params={"keyword": str(account), "page_size": 100})
            if response.status_code != 200:
                sender.reply("连接呆呆面板获取变量失败")
                exit(0)
            result = response.json()
            qlid = None
            for env in result.get('data', []):
                if (env.get('name') == osname and env.get('remarks') and str(account) in env['remarks']):
                    qlid = env['id']
                    break
        else:
            response = requests.get(url=url, headers=headers)
            if response.status_code != 200:
                sender.reply("""
==================
    请求失败
==================
❌ 获取变量失败
------------------
请检查:
• 青龙面板是否正常
• Token是否有效
==================""")
                exit(0)
                
            result = response.json()
            if result['code'] != 200:
                sender.reply("""
==================
    响应错误
==================
❌ 获取变量失败
------------------
请检查:
• 应用权限是否正确
• 变量是否存在
==================""")
                exit(0)
                
            qlid = None
            for env in result['data']:
                if (env.get('name') == osname and 
                    env.get('remarks') and 
                    str(account) in env['remarks']):
                    qlid = env['id']
                    break
                
        return qlid
        
    except Exception as e:
        sender.reply(f"""
==================
    系统错误
==================
❌ 获取变量时出错
------------------
错误信息: {str(e)}
==================""")
        exit(0)

def login(name, password):
    """福田账号登录"""
    url = "https://czyl.foton.com.cn/ehomes-new/homeManager/getLoginMember"
    payload = json.dumps({
        "password": password,
        "name": name,
    })
    headers = {
        'User-Agent': "okhttp/3.14.9",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
    }
    
    try:
        session = requests.Session()
        session.headers.update(headers)
        # 仅登录走代理
        update_proxy(session, proxy_url)
        response = session.post(url, data=payload)
        if response.status_code != 200:
            return "网络请求失败", "登录失败", False
            
        result = response.json()
        if 'data' not in result:
            return result.get('msg', "登录失败"), "登录失败", False
            
        memberID = result['data']['memberID']
        account = result['data']['uid']
        return str(account), memberID, f'{name}#{password}'
        
    except Exception as e:
        return f"登录异常: {str(e)}", "登录异常", False

def Addenvs(osname, value, account, phone):
    """添加或更新青龙变量"""
    phone = phone[:3] + '*' * 4 + phone[7:]
    qlid = allenvs(osname, account)
    
    if qlid is None:
        QLzt(osname, value, account, phone)
    else:
        QLupdate(osname, value, account, qlid, phone)

def QLzt(osname, value, account, phone):
    """添加青龙变量"""
    try:
        if use_daidai:
            url = f"{QLurl}/api/envs"
            data = {
                "value": value,
                "name": osname,
                "remarks": f'福田:{account}丨用户:{userid}丨手机:{phone}丨福田管理'
            }
            if panel_group:
                data["group"] = panel_group
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code not in (200, 201):
                sender.reply("添加呆呆面板变量失败")
                exit(0)
            result = response.json()
            return result.get('data', {}).get('id')
        else:
            url = f"{QLurl}/open/envs"
            data = [{
                "value": value,
                "name": osname,
                "remarks": f'福田:{account}丨用户:{userid}丨手机:{phone}丨福田管理'
            }]
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code != 200:
                sender.reply("""
==================
    请求失败
==================
❌ 添加变量失败
------------------
请检查:
• 青龙面板是否正常
• Token是否有效
==================""")
                exit(0)
                
            result = response.json()
            if "value must be unique" in response.text:
                return
                
            if result.get('code') != 200:
                sender.reply("""
==================
    添加失败
==================
❌ 变量添加失败
------------------
请检查:
• 变量格式是否正确
• 应用权限是否正确
==================""")
                exit(0)
                
            return result['data'][0]['id']
        
    except Exception as e:
        sender.reply(f"""
==================
    系统错误
==================
❌ 添加变量时出错
------------------
错误信息: {str(e)}
==================""")
        exit(0)

def QLupdate(osname, value, account, qlid, phone):
    """更新青龙变量"""
    try:
        if use_daidai:
            url = f"{QLurl}/api/envs/{qlid}"
            data = {
                "value": value,
                "name": osname,
                "remarks": f'福田:{account}丨用户:{userid}丨手机:{phone}丨福田管理'
            }
            if panel_group:
                data["group"] = panel_group
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            response = requests.put(url, headers=headers, json=data)
            if response.status_code != 200:
                sender.reply("更新呆呆面板变量失败")
                exit(0)
            return qlid, None
        else:
            url = f"{QLurl}/open/envs"
            data = {
                "value": value,
                "name": osname,
                "remarks": f'福田:{account}丨用户:{userid}丨手机:{phone}丨福田管理',
                "id": qlid
            }
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            
            response = requests.put(url, headers=headers, data=json.dumps(data))
            if response.status_code != 200:
                sender.reply("""
==================
    请求失败
==================
❌ 更新变量失败
------------------
请检查:
• 青龙面板是否正常
• Token是否有效
==================""")
                exit(0)
                
            result = response.json()
            if result.get('code') != 200:
                sender.reply("""
==================
    更新失败
==================
❌ 变量更新失败
------------------
请检查:
• 变量格式是否正确
• 应用权限是否正确
==================""")
                exit(0)
                
            data = result.get('data')
            if not data:
                sender.reply("""
==================
    数据错误
==================
❌ 未返回更新数据
------------------
请检查:
• 变量ID是否存在
• 数据格式是否正确
==================""")
                exit(0)
                
            return data['id'], data['createdAt']
        
    except Exception as e:
        sender.reply(f"""
==================
    系统错误
==================
❌ 更新变量时出错
------------------
错误信息: {str(e)}
==================""")
        exit(0)

def bind():
    """绑定福田账号"""
    def accvip(Newaddition):
        """处理账号授权状态"""
        status = "添加" if Newaddition else "更新"
        auth_status = "✅ 已授权" if (accountVip and accountVip != '未授权' and accountVip != '授权过期' and accountVip >= today_time) else "⚠️ 未授权"
        next_step = "福田管理" if (accountVip and accountVip != '未授权' and accountVip != '授权过期' and accountVip >= today_time) else "福田管理"
        
        msg = f"""
=====账号{status}成功=====
📱 账号: {mobile}
🔐 授权状态: {auth_status}
------------------
💡 发送"{next_step}"进行授权
=================="""

        if accountVip and accountVip != '未授权' and accountVip != '授权过期' and len(accountVip) > 0 and accountVip >= today_time:
            Addenvs(osname=osname, value=token, account=account, phone=mobile)
            
        if Newaddition:
            accounts.append(account)
            
        sender.reply(msg)
        middleware.bucketSet(bucket='dd_fukuda_user', key=userid, value=f'{accounts}')
        middleware.bucketSet(bucket='dd_fukuda_token', key=account, value=token)
        middleware.bucketSet(bucket='dd_fukuda_auth', key=account, value=accountVip)

    sender.reply("""
=====福田账号登录=====
📱 请输入福田e家账号:
⚠️ 建议私聊登录,账号安全
⭐ 输入q退出操作
===================""")
    
    mobile = sender.input(120000, 1, False)
    if not mobile:
        sender.reply("⏰ 输入超时!")
        exit(0)
    elif mobile.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)
    elif len(mobile) != 11:
        sender.reply("❌ 手机号格式错误!")
        exit(0)
        
    sender.reply("请输入福田e家密码:")
    password = sender.input(120000, 1, False)
    if not password:
        sender.reply("⏰ 输入超时!")
        exit(0)
    elif password.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)
        
    account, memberID, token = login(mobile, password)
    if token is False:
        sender.reply(f"""
==================
    登录失败
==================
❌ {account}
==================""")
        exit(0)
        
    accountVip = middleware.bucketGet(bucket='dd_fukuda_auth', key=account) or ''
    
    # 获取最新的用户账号列表
    current_uservalue = middleware.bucketGet(bucket='dd_fukuda_user', key=userid) or ''
    if len(current_uservalue) == 0:
        accounts = []
        accvip(True)
    else:
        accounts = eval(current_uservalue)
        accvip(False if account in accounts else True)

def batch_bind():
    """批量绑定福田账号"""
    sender.reply("""
=====福田批量登录=====
📝 请输入账号密码信息:
格式: 账号#密码
示例: 
13800138000#password123
13900139000#password456

⚠️ 每行一个账号
⚠️ 建议私聊操作,确保安全
⭐ 输入q退出操作
===================""")
    
    account_data = sender.input(300000, 1, False)  # 5分钟超时
    if not account_data:
        sender.reply("⏰ 输入超时!")
        exit(0)
    elif account_data.lower() == 'q':
        sender.reply("✅ 已取消批量登录")
        exit(0)
    
    # 解析账号数据
    lines = account_data.strip().split('\n')
    if not lines:
        sender.reply("❌ 未输入任何账号信息!")
        exit(0)
    
    # 验证格式并解析账号
    account_list = []
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        if '#' not in line:
            sender.reply(f"""
==================
    格式错误
==================
❌ 第{i}行格式错误
正确格式: 账号#密码
错误内容: {line}
==================""")
            exit(0)
            
        parts = line.split('#')
        if len(parts) != 2:
            sender.reply(f"""
==================
    格式错误
==================
❌ 第{i}行格式错误
正确格式: 账号#密码
错误内容: {line}
==================""")
            exit(0)
            
        mobile, password = parts[0].strip(), parts[1].strip()
        
        # 验证手机号格式
        if len(mobile) != 11 or not mobile.isdigit():
            sender.reply(f"""
==================
    手机号错误
==================
❌ 第{i}行手机号格式错误
手机号: {mobile}
请确保为11位数字
==================""")
            exit(0)
            
        account_list.append((mobile, password))
    
    if not account_list:
        sender.reply("❌ 未找到有效的账号信息!")
        exit(0)
    
    # 确认批量操作
    sender.reply(f"""
=====确认批量登录=====
📊 共解析到 {len(account_list)} 个账号
------------------
确认批量登录请回复【y】
取消操作请回复【n】
==================""")
    
    if not yesornos():
        sender.reply("✅ 已取消批量登录")
        exit(0)
    
    # 获取当前用户账号列表
    current_uservalue = middleware.bucketGet(bucket='dd_fukuda_user', key=userid) or ''
    if len(current_uservalue) == 0:
        accounts = []
    else:
        accounts = eval(current_uservalue)
    
    # 批量处理账号
    success_count = 0
    fail_count = 0
    results = []
    
    for i, (mobile, password) in enumerate(account_list, 1):
        try:
            sender.reply(f"正在处理第{i}/{len(account_list)}个账号...")
            
            # 登录验证
            account, memberID, token = login(mobile, password)
            if token is False:
                fail_count += 1
                phone = mobile[:3] + '*' * 4 + mobile[7:]
                results.append(f"❌ {phone}: 登录失败 - {account}")
                continue
            
            # 检查是否已存在
            is_new = account not in accounts
            if is_new:
                accounts.append(account)
            
            # 保存账号信息
            middleware.bucketSet(bucket='dd_fukuda_token', key=account, value=token)
            
            # 获取或设置授权状态
            accountVip = middleware.bucketGet(bucket='dd_fukuda_auth', key=account) or ''
            if not accountVip:
                accountVip = '未授权'
                middleware.bucketSet(bucket='dd_fukuda_auth', key=account, value=accountVip)
            
            # 如果已授权，添加到青龙变量
            if accountVip != '未授权' and accountVip != '授权过期' and len(accountVip) > 0 and accountVip >= today_time:
                phone = mobile[:3] + '*' * 4 + mobile[7:]
                Addenvs(osname=osname, value=token, account=account, phone=phone)
            
            success_count += 1
            phone = mobile[:3] + '*' * 4 + mobile[7:]
            status = "新增" if is_new else "更新"
            auth_status = "已授权" if (accountVip != '未授权' and accountVip != '授权过期' and len(accountVip) > 0 and accountVip >= today_time) else "未授权"
            results.append(f"✅ {phone}: {status}成功 - {auth_status}")
            
        except Exception as e:
            fail_count += 1
            phone = mobile[:3] + '*' * 4 + mobile[7:]
            results.append(f"❌ {phone}: 处理异常 - {str(e)}")
    
    # 更新用户账号列表
    if accounts:
        middleware.bucketSet(bucket='dd_fukuda_user', key=userid, value=f'{accounts}')
    
    # 生成结果报告
    result_msg = f"""
=====批量登录完成=====
📊 处理结果统计:
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
------------------
💡 发送"福田管理"进行授权
==================
"""

    sender.reply(result_msg)

def ValueErrors(value, count):
    """验证输入值是否有效"""
    if value is None or value == '':
        sender.reply('输入超时！')
        exit(0)
    elif value.lower() == 'q':
        sender.reply('退出！')
        exit(0)
        
    try:
        value = int(value)
        # 在福田管理中，0表示一键授权所有账号
        if value < 0 or (value > count and value != 0):
            sender.reply('输入错误！')
            exit(0)
        return value
    except ValueError:
        sender.reply('输入错误！')
        exit(0)

def Administration():
    accst = '状态正常'
    message = ''
    count = 1
    # 在这里获取zsm配置
    zsm = middleware.bucketGet(bucket='dd_fukuda_config', key='zsm')
    
    # 重新获取最新的用户账号列表，不使用全局uservalue
    current_uservalue = middleware.bucketGet(bucket='dd_fukuda_user', key=userid) or ''
    
    if len(current_uservalue) != 0:
        accounts = eval(current_uservalue)
        valid_accounts = []
        invalid_accounts = []  # 添加失效账号列表
        account_info_list = []  # 添加账号信息列表，用于对应显示序号
        message = '0、一键授权所有账号\n==================\n'
        for account in accounts:
            Token = middleware.bucketGet(bucket='dd_fukuda_token', key=account)
            if not Token:
                continue
                
            accountVip = middleware.bucketGet(bucket='dd_fukuda_auth', key=account) or ''
            mobile = Token.split('#')[0]
            password = Token.split('#')[1]
            account, memberID, token = login(mobile, password)
            if token is False:
                accst = '账密失效'
                invalid_accounts.append(account)  # 记录失效账号
            else:
                accst = '状态正常'
                valid_accounts.append(account)
                
            if len(accountVip) == 0:
                accvip = '未授权'
            elif accountVip < today_time:
                accvip = '授权过期'
            else:
                accvip = accountVip
            mobile = mobile[:3] + '*' * 4 + mobile[7:]
            
            # 保存账号信息，用于后续选择
            account_info_list.append({
                'account': account,
                'token': Token,
                'accountVip': accountVip,
                'status': accst,
                'mobile': mobile
            })
            
            message += f"""=== 账号 [{count}] ===
📱 账号: {mobile}
💫 状态: {accst}
⏰ 到期: {accvip}
=================="""
            count += 1

        # 不再自动删除失效账号，而是显示所有账号状态
        # 只有当所有账号都失效时才提示重新绑定
        if len(valid_accounts) == 0 and len(invalid_accounts) > 0:
            sender.reply("""
=====所有账号失效=====
❌ 所有账号都已失效
💡 发送"福田登录"重新绑定
或通过福田管理删除失效账号
==================""")
            # 不直接退出，让用户可以删除失效账号
        elif len(accounts) == 0:
            sender.reply("""
=====账号错误=====
❌ 未绑定福田账号
💡 发送"福田登录"绑定
==================""")
            exit(0)

        # 如果有失效账号，在消息中添加提示
        if len(invalid_accounts) > 0:
            message += f"""💡 提示: 检测到{len(invalid_accounts)}个失效账号
建议通过删除功能清理失效账号
=================="""

        sender.reply(f"""
=====福田管理=====
{message}
📝 请选择要管理的账号序号
⚠️ 输入"q"退出操作
==================""")

        mes = sender.input(120000, 1, False)
        mes = ValueErrors(value=mes, count=count)
        
        if mes == 0:
            # 一键授权所有有效账号
            if len(valid_accounts) == 0:
                sender.reply("""
==================
    无有效账号
==================
❌ 没有可授权的有效账号
💡 请先删除失效账号后重新绑定
==================""")
                exit(0)
            
            sender.reply("""
=====授权操作=====
📝 请输入授权月数
💡 示例输入: 1
⚠️ 输入"q"退出
==================""")
            sjts = sender.input(120000, 1, False)
            sjts = ValueErrors(value=sjts, count=99)
            
            # 计算总金额(只计算有效账号)
            total_money = Decimal(sjts) * Decimal(FukudaVipmoney) * len(valid_accounts)
            total_coin = int(Fukudacoin) * sjts * len(valid_accounts)
            
            # 如果价格为0，直接免费授权所有有效账号
            if total_money == 0:
                success_count = 0
                fail_count = 0
                
                for account in valid_accounts:
                    try:
                        accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                        token = middleware.bucketGet('dd_fukuda_token', account)
                        
                        if not token:
                            fail_count += 1
                            continue
                            
                        accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                        middleware.bucketSet('dd_fukuda_auth', account, accountVip)
                        
                        # 更新青龙变量
                        mobile = token.split('#')[0]
                        phone = mobile[:3] + '*' * 4 + mobile[7:]
                        Addenvs(osname=osname, value=token, account=account, phone=phone)
                        success_count += 1
                    except:
                        fail_count += 1
                        
                result_msg = f"""
==================
    免费授权成功
==================
🎫 商品: 福田一键授权
💰 金额: 免费
------------------
✅ 成功授权: {success_count}个账号
❌ 授权失败: {fail_count}个账号
⏰ 授权月数: {sjts}月
=================="""
                sender.reply(result_msg)
                return
            
            pay_menu = """
=====选择支付方式===="""
            if zsm:
                pay_menu += f"""
1️⃣ 微信支付
   💰 {total_money}元/{sjts}月/{len(valid_accounts)}个有效账号"""
                
            if Fukudacoin != 9999:
                usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
                pay_menu += f"""
2️⃣ 积分支付  
   🎯 {total_coin}积分/{sjts}月/{len(valid_accounts)}个有效账号
   💫 当前积分: {usercoin}"""
                
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
                
            elif choice == '1' and zsm:
                zfzt = sender.atWaitPay()
                if zfzt:
                    sender.reply("""
==================
    支付冲突
==================
⚠️ 当前有人正在支付
请稍后再试
==================""")
                    exit(0)
                    
                pay_msg = f"""
=====微信扫码支付====
🎫 商品: 福田一键授权
📅 时长: {sjts}月/{len(valid_accounts)}个有效账号
💰 金额: {total_money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
                sender.reply(pay_msg)
                sender.replyImage(zsm)
                
                ddzf = sender.waitPay("q", 100 * 1000)
                
                if str(ddzf) == 'q':
                    sender.reply("✅ 已取消支付")
                    exit(0)
                    
                try:
                    if isinstance(ddzf, dict):
                        # 新版微信赞赏消息格式
                        if ddzf.get('type') == '微信赞赏':
                            Money = float(ddzf.get('money', 0))
                            Time = ddzf.get('time', '')
                            From = ddzf.get('from_name', '')
                        # 旧版微信收款消息格式  
                        elif ddzf.get('type') == '微信收款':
                            Money = float(ddzf.get('money', 0))
                            Time = ddzf.get('time', '')
                            From = ddzf.get('from_name', '')
                        else:
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '')
                            From = ''
                    else:
                        # 尝试解析JSON字符串
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
                                    sender.reply(f"""
==================
    解析失败
==================
❌ 无法解析收款信息
------------------
错误信息: {str(e)}
==================""")
                                    exit(0)
                            else:
                                sender.reply("""
==================
    格式错误
==================
❌ 无法识别支付信息
------------------
请联系管理员处理
==================""")
                                exit(0)
                        
                    if float(Money) >= float(total_money):
                        success_count = 0
                        fail_count = 0
                        
                        for account in valid_accounts:
                            try:
                                accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                                token = middleware.bucketGet('dd_fukuda_token', account)
                                
                                if not token:
                                    fail_count += 1
                                    continue
                                    
                                accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                                middleware.bucketSet('dd_fukuda_auth', account, accountVip)
                                
                                # 更新青龙变量
                                mobile = token.split('#')[0]
                                phone = mobile[:3] + '*' * 4 + mobile[7:]
                                Addenvs(osname=osname, value=token, account=account, phone=phone)
                                success_count += 1
                            except:
                                fail_count += 1
                                
                        result_msg = f"""
==================
    支付成功
==================
🎫 商品: 福田一键授权
💰 金额: {Money}元
⏰ 时间: {Time}
{f'👤 付款人: {From}' if From else ''}
------------------
✅ 成功授权: {success_count}个账号
❌ 授权失败: {fail_count}个账号
⏰ 授权月数: {sjts}月
=================="""
                        sender.reply(result_msg)
                        return True
                    else:
                        sender.reply(f"""
==================
   支付金额错误
==================
💰 应付: {total_money}元
💳 实付: {Money}元
{f'👤 付款人: {From}' if From else ''}

❗ 请联系管理员处理退款！
==================""")
                        exit(0)
                except Exception as e:
                    sender.reply(f"""
==================
    处理异常
==================
❌ 处理支付结果出错
------------------
错误信息: {str(e)}
==================""")
                    exit(0)
                    
            elif choice == '2' and Fukudacoin != 9999:
                # 积分支付流程
                if int(usercoin) < total_coin:
                    sender.reply(f"""
==================
    积分不足
==================
👤 当前积分: {usercoin}
📍 需要积分: {total_coin}
==================""")
                    exit(0)
                    
                confirm_msg = f"""
==================
    积分支付确认
==================
💫 消耗积分: {total_coin}
⏰ 授权时长: {sjts}月/账号
------------------
确认请回复【y】
取消请回复【n】
=================="""
                sender.reply(confirm_msg)
                
                if yesornos():
                    try:
                        new_balance = int(usercoin) - total_coin
                        middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                        
                        success_count = 0
                        fail_count = 0
                        
                        for account in valid_accounts:
                            try:
                                accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                                token = middleware.bucketGet('dd_fukuda_token', account)
                                
                                if not token:
                                    fail_count += 1
                                    continue
                                    
                                accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                                middleware.bucketSet('dd_fukuda_auth', account, accountVip)
                                
                                # 更新青龙变量
                                mobile = token.split('#')[0]
                                phone = mobile[:3] + '*' * 4 + mobile[7:]
                                Addenvs(osname=osname, value=token, account=account, phone=phone)
                                success_count += 1
                            except:
                                fail_count += 1
                                
                        result_msg = f"""
==================
    支付成功
==================
💫 扣除积分: {total_coin}
💰 剩余积分: {new_balance}
⏰ 授权时长: {sjts}月/账号
------------------
✅ 成功授权: {success_count}个账号
❌ 授权失败: {fail_count}个账号
=================="""
                        sender.reply(result_msg)
                        exit(0)
                    except Exception as e:
                        sender.reply(f"""
==================
    支付失败
==================
❌ 积分处理失败
------------------
错误信息: {str(e)}
==================""")
                        exit(0)
                else:
                    sender.reply("""
==================
    已取消支付
==================
✅ 操作已取消
==================""")
                    exit(0)
            else:
                sender.reply("""
==================
    输入无效
==================
❌ 请输入正确的选项
==================""")
                exit(0)
            
        # 选择具体账号进行操作 
        selected_account_info = account_info_list[mes - 1]
        account = selected_account_info['account']
        Token = selected_account_info['token']
        accountVip = selected_account_info['accountVip']
        mobile_display = selected_account_info['mobile']
        accst = selected_account_info['status']
        
        # 重新验证账号状态
        mobile = Token.split('#')[0]
        password = Token.split('#')[1]
        login_account, memberID, login_token = login(mobile, password)
        if login_token is False:
            accst = '账密失效'
        
        if len(accountVip) == 0:
            accvip = '未授权'
        elif accountVip < today_time:
            accvip = '授权过期'
        else:
            accvip = accountVip
        
        sender.reply(f"""
=====账号详情=====
📱 账号: {mobile_display}
🪫 状态: {accst}
☁️ 授权: {accvip}
------------------
[1] 📅 授权账号
[2] ❌ 删除账号

请选择操作序号
==================""")

        mes = sender.input(120000, 1, False)
        mes = ValueErrors(value=mes, count=2)
        if mes == 1:
            sender.reply("""
=====授权操作=====
📝 请输入授权月数
💡 示例输入: 1
⚠️ 输入"q"退出
==================""")
            mes = sender.input(120000, 1, False)
            mes = ValueErrors(value=mes, count=99)
            zf(project='福田授权', me_as_int=mes, accountVip=accountVip, account=account, token=Token, phone=mobile_display)
        elif mes == 2:
            sender.reply("""
=====删除确认=====
⚠️ 是否删除该账号?
------------------
[y] 确认删除
[n] 取消操作
==================""")

            yesorno = sender.input(120000, 1, False)
            if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
                try:
                    # 删除青龙变量
                    qlid = allenvs(osname=osname, account=account)
                    if qlid:
                        delenvs(id=qlid)
                    
                    # 删除账号相关的存储
                    middleware.bucketDel(bucket='dd_fukuda_token', key=account)
                    middleware.bucketDel(bucket='dd_fukuda_auth', key=account)
                    
                    # 从原始账号列表中移除
                    try:
                        accounts.remove(account)
                    except ValueError:
                        # 如果账号不在列表中，忽略错误
                        pass
                    
                    # 更新或删除用户的账号列表
                    if accounts:
                        middleware.bucketSet(bucket='dd_fukuda_user', key=userid, value=f'{accounts}')
                    else:
                        middleware.bucketDel(bucket='dd_fukuda_user', key=userid)
                        
                    sender.reply("""
=====操作成功=====
✅ 账号已删除
==================""")

                except Exception as e:
                    sender.reply(f"""
=====删除失败=====
❌ 删除账号时出错
------------------
错误信息: {str(e)}
==================""")

                exit(0)
            
            elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
                sender.reply("""
=====操作取消=====
✅ 已取消删除
==================""")

            else:
                sender.reply("""
=====输入错误=====
❌ 无效的选择
==================""")

            exit(0)
    else:
        sender.reply("""
=====账号错误=====
❌ 未绑定福田账号
💡 发送"福田登录"绑定
==================""")

        exit(0)

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
        sender.reply('退出！')
        exit(0)
    else:
        sender.reply('输入错误！')
        exit(0)

def zf(project, me_as_int, accountVip, token, phone, account):
    """处理支付流程"""
    try:
        # 检查是否为免费授权（价格为0）
        money = Decimal(me_as_int) * Decimal(FukudaVipmoney)
        if money == 0:
            # 免费授权，直接处理
            accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
            middleware.bucketSet('dd_fukuda_auth', account, accountVip)
            Addenvs(osname=osname, value=token, account=account, phone=phone)
            
            result_msg = f"""
=====免费授权成功=====
🎫 商品: {project}
💰 金额: 免费
⏰ 授权时长: {me_as_int}月
=================="""
            sender.reply(result_msg)
            return True
        
        # 获取支付配置
        zsm = middleware.bucketGet('dd_fukuda_config', 'zsm')
        use_ma_pay = middleware.bucketGet('dd_fukuda_config', 'use_ma_pay') or 'false'
        use_ma_pay = use_ma_pay.lower() == 'true'
        
        if use_ma_pay:
            # 从卡密系统获取码支付配置
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
        
        if not zsm and not use_ma_pay:
            sender.reply('未配置收款方式,请联系管理员!')
            exit(0)
            
        # 检查是否允许使用积分支付
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(Fukudacoin) * me_as_int
        
        # 构建支付选择菜单
        pay_menu = """
=====选择支付方式===="""

        # 添加微信支付选项
        if zsm:
            pay_menu += f"""
1️⃣ 微信支付
   💰 {money}元/{me_as_int}月"""
            
        # 添加码支付选项
        if use_ma_pay:
            pay_menu += f"""
2️⃣ 码支付
   💰 {money}元/{me_as_int}月"""
            
        # 只有当Fukudacoin > 0时才显示积分支付选项
        if Fukudacoin and int(Fukudacoin) > 0:
            pay_menu += f"""
3️⃣ 积分支付  
   🎯 {zfcoin}积分/{me_as_int}月
   💫 当前积分: {usercoin}"""
            
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
            
        elif choice == '1' and zsm:
            # 微信支付流程
            zfzt = sender.atWaitPay()
            if zfzt:
                sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
                exit(0)
                
            money = Decimal(me_as_int) * Decimal(FukudaVipmoney)
            
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
                sender.reply('✅ 已取消支付')
                exit(0)
                
            try:
                if isinstance(ddzf, dict):
                    # 新版微信赞赏消息格式
                    if ddzf.get('Type') == '微信赞赏':
                        Money = float(ddzf.get('Money', 0))
                        Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                        From = ddzf.get('FromName', '')
                    # 新版微信收款消息格式  
                    elif ddzf.get('Type') == '微信收款':
                        Money = float(ddzf.get('Money', 0))
                        Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                        From = ddzf.get('FromName', '')
                    # 旧版BORW格式
                    elif ddzf.get('Money'):
                        Money = float(ddzf.get('Money', 0))
                        Time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                        From = ddzf.get('FromName', '')
                    # 旧版GW格式
                    elif ddzf.get('money'):
                        Money = float(ddzf.get('money', 0))
                        Time = ddzf.get('time', '').replace('T', ' ').split('.')[0]
                        From = ddzf.get('fromName', '')
                    else:
                        sender.reply('不支持的支付消息格式')
                        exit(0)
                else:
                    # 尝试解析JSON字符串
                    try:
                        ddzf = json.loads(ddzf)
                        if ddzf.get('Type') == '微信赞赏':
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                            From = ddzf.get('FromName', '')
                        elif ddzf.get('Type') == '微信收款':
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                            From = ddzf.get('FromName', '')
                        else:
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                            From = ddzf.get('FromName', '')
                    except:
                        sender.reply("❌ 无法解析支付结果")
                        exit(0)
                    
                if float(Money) >= float(money):
                    accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                    middleware.bucketSet('dd_fukuda_auth', account, accountVip)
                    Addenvs(osname=osname, value=token, account=account, phone=phone)
                    
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
                    sender.reply(f"""
=====支付金额错误=====
💰 应付: {money}元
💳 实付: {Money}元
{f'👤 付款人: {From}' if From else ''}

❗ 请联系管理员处理退款！
==================""")
                    exit(0)
            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                exit(0)
                
        elif choice == '2' and use_ma_pay:
            # 码支付流程
            money = Decimal(me_as_int) * Decimal(FukudaVipmoney)
            
            # 生成订单号
            out_trade_no = f"FT{int(time.time())}{userid}"
            
            # 构造支付参数
            params = {
                'pid': ma_pay_config['pid'],
                'type': ma_pay_config['type'].split(',')[0],
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-福田授权-{str(money)}",
                'money': str(money),
                'notify_url': ma_pay_config['notify_url'],
                'return_url': ma_pay_config['return_url'],
                'param': userid
            }
            params = {k: v for k, v in params.items() if v}
            
            # 按照ASCII码排序参数
            sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
            
            # 拼接成URL键值对格式
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
            
            # 添加密钥进行MD5签名
            sign = hashlib.md5((sign_str + ma_pay_config['key']).encode('utf-8')).hexdigest().lower()
            
            # 添加签名到参数
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            # 发送支付请求
            gateway = ma_pay_config['gateway']
            if gateway.endswith('/'):
                gateway = gateway[:-1]
            mapi_url = f"{gateway}/mapi.php"
            
            try:
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    sender.reply(f"❌ 创建支付订单失败，HTTP状态码: {response.status_code}")
                    exit(0)
                
                try:
                    result = response.json()
                except:
                    sender.reply("❌ 创建支付订单失败，返回数据格式错误")
                    exit(0)
                
                code = result.get('code', 0)
                msg = result.get('msg', '未知状态')
                
                if code == 1:
                    pay_url = result.get('payurl', '')
                    if not pay_url:
                        sender.reply("❌ 未获取到支付链接!")
                        exit(0)
                        
                    sender.reply(f"""
=====码支付=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 有效期: 5分钟
------------------
请点击链接完成支付:
{pay_url}
==================""")
                    
                    # 轮询订单状态
                    for _ in range(60):  # 最多等待5分钟
                        time.sleep(5)
                        check_url = f"{gateway}/api.php"
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
                                middleware.bucketSet('dd_fukuda_auth', account, accountVip)
                                Addenvs(osname=osname, value=token, account=account, phone=phone)
                                
                                sender.reply(f"""
=====支付成功=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 授权时长: {me_as_int}月
==================""")
                                return True
                        except:
                            continue
                            
                    sender.reply("❌ 支付超时,请重新发起支付!")
                    exit(0)
                else:
                    if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                        sender.reply(f"❌ 码支付暂不可用({msg})")
                    else:
                        sender.reply(f"❌ 创建订单失败: {msg}")
                    exit(0)
            except Exception as e:
                sender.reply(f"❌ 支付请求失败: {str(e)}")
                exit(0)
                
        elif choice == '3' and Fukudacoin != 9999:
            # 积分支付流程
            if int(usercoin) < zfcoin:
                sender.reply(f"""
==================
    积分不足
==================
👤 当前积分: {usercoin}
📍 需要积分: {zfcoin}
==================""")
                exit(0)
                
            confirm_msg = f"""
==================
    积分支付确认
==================
💫 消耗积分: {zfcoin}
⏰ 授权时长: {me_as_int}月
------------------
确认请回复【y】
取消请回复【n】
=================="""
            sender.reply(confirm_msg)
            
            if yesornos():
                try:
                    new_balance = int(usercoin) - zfcoin
                    middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                    accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                    middleware.bucketSet('dd_fukuda_auth', account, accountVip)
                    Addenvs(osname=osname, value=token, account=account, phone=phone)
                    
                    result_msg = f"""
==================
    支付成功
==================
💫 扣除积分: {zfcoin}
💰 剩余积分: {new_balance}
⏰ 授权时长: {me_as_int}月
=================="""
                    sender.reply(result_msg)
                    exit(0)
                except Exception as e:
                    sender.reply(f"""
==================
    支付失败
==================
❌ 积分处理失败
------------------
错误信息: {str(e)}
==================""")
                    exit(0)
            else:
                sender.reply("""
==================
    已取消支付
==================
✅ 操作已取消
==================""")
                exit(0)
        else:
            sender.reply("""
==================
    输入无效
==================
❌ 请输入正确的选项
==================""")
            exit(0)
            
    except Exception as e:
        sender.reply(f"""
==================
    系统错误
==================
❌ 支付处理异常
------------------
错误信息: {str(e)}
==================""")
        exit(0)

def empower(empowertime, me_as_int):
    day = me_as_int * 30
    if empowertime == '未授权' or empowertime == '授权过期' or empowertime <= str(today_time):
        delayed_date = today_date + timedelta(days=day)
    elif empowertime > today_time:
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        delayed_date = delayed_date.date()
    else:
        sender.reply('出错！')
        exit(0)
    return str(delayed_date)

def delenvs(id):
    """删除青龙环境变量"""
    if id is None:
        return
    
    try:
        if use_daidai:
            url = f"{QLurl}/api/envs/{id}"
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            response = requests.delete(url, headers=headers)
            if response.status_code != 200:
                sender.reply("删除呆呆面板变量失败")
                return
        else:
            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            data = [id]
            response = requests.delete(url, headers=headers, json=data)
            if response.status_code != 200:
                sender.reply("""
==================
    删除失败
==================
❌ 删除变量失败
------------------
请检查:
• 青龙面板是否正常
• Token是否有效
==================""")
                return
                
            result = response.json()
            if result.get('code') != 200:
                sender.reply("""
==================
    删除错误
==================
❌ 变量删除失败
------------------
请检查:
• 变量ID是否存在
• 应用权限是否正确
==================""")
            return
            
    except Exception as e:
        sender.reply(f"""
==================
    系统错误
==================
❌ 删除变量时出错
------------------
错误信息: {str(e)}
==================""")
        return

def cx(memberID):
    try:
        url = "https://czyl.foton.com.cn/ehomes-new/homeManager/api/Member/findMemberPointsInfo"

        payload = json.dumps({
            "memberId": f"{memberID}",
        })

        headers = {
            'User-Agent': "web",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
        }

        session = create_proxy_session(headers)
        response = session.post(url, data=payload, timeout=15)
        if response.status_code != 200:
            return f"错误: HTTP {response.status_code}", 0

        # 兼容不同返回结构
        try:
            r = response.json()
        except Exception as e:
            return f"错误: 响应非JSON({str(e)})", 0

        pointValue = 0
        if isinstance(r, dict):
            # 优先按标准code判断
            code = r.get('code') or r.get('stateCode')
            if code == 200 or code == 0 or ('查询成功' in str(r)):
                data = r.get('data') or {}
                # data可能是dict或直接数值
                if isinstance(data, dict):
                    pv = data.get('pointValue') or data.get('points') or data.get('point')
                else:
                    pv = data
                try:
                    pointValue = int(pv)
                except Exception:
                    # 若取不到有效值
                    return "错误: 未返回有效积分", 0
            else:
                return f"错误: {r.get('msg') or r.get('message') or '查询失败'}", 0
        else:
            return "错误: 返回格式异常", 0

        todaycoin = 0
        url = "https://czyl.foton.com.cn/ehomes-new/homeManager/api/Member/getIntegralList"

        data = {"memberId": memberID, 'transactionDate': today_time}

        response = session.post(url, data=json.dumps(data), timeout=15)
        if response.status_code != 200:
            return pointValue, 0

        try:
            r2 = response.json()
        except Exception:
            return pointValue, 0

        items = r2.get('data') or []
        if not isinstance(items, list):
            items = []

        for coinj in items:
            integral = coinj.get('integral', 0)
            date = coinj.get('date', '') or coinj.get('createTime', '')
            # 兼容多种时间格式，只比较日期前10位
            try:
                if str(date)[:10] == today_time:
                    todaycoin += int(integral)
            except Exception:
                continue

        return pointValue, todaycoin
        
    except Exception as e:
        return f"错误: 查询异常({str(e)})", 0

def cxs():
    """查询账号状态"""
    # 获取最新的用户账号列表
    current_uservalue = middleware.bucketGet(bucket='dd_fukuda_user', key=userid) or ''
    if len(current_uservalue) == 0:
        sender.reply("""
======未绑定账号=====
❌ 未找到任何账号信息
💡 发送"福田登录"绑定
==================""")
        return

    accounts = eval(current_uservalue)
    # 移除自动清理逻辑，只用于统计展示
    valid_count = 0
    invalid_count = 0
    
    for account in accounts:
        try:
            Token = middleware.bucketGet(bucket='dd_fukuda_token', key=account)
            if not Token:
                invalid_count += 1
                continue
                
            accountVip = middleware.bucketGet(bucket='dd_fukuda_auth', key=account) or ''
            mobile = Token.split('#')[0]
            password = Token.split('#')[1]
            phone = mobile[:3] + '*' * 4 + mobile[7:]
            
            account, memberID, token = login(mobile, password)
            if not token:
                invalid_count += 1
                sender.reply(f"""
==================
    登录失败
==================
📱 账号: {phone}
❌ 状态: 登录失败
💡 请使用"福田清理"清除失效账号
==================""")
                continue

            valid_count += 1
            if len(accountVip) == 0:
                sender.reply(f"""
======未授权账号=====
📱 账号: {phone}
⚠️ 状态: 未授权
==================""")
                continue
            elif accountVip < today_time:
                sender.reply(f"""
=====授权已过期======
📱 账号: {phone}
❌ 状态: 授权过期
💡 请使用"福田清理"清除过期账号
==================""")
                continue
            else:
                pointValue, todaycoin = cx(memberID)
                if isinstance(pointValue, str) and "错误" in pointValue:
                    sender.reply(f"""
=====查询异常=====
📱 账号: {phone}
❌ 错误: {pointValue}
==================""")
                else:
                    # 查询订单信息
                    order_total, order_items = cx_orders(memberID, account, mobile, Token)
                    
                    order_info = ""
                    if isinstance(order_total, int):
                        order_info = f"\n📦 总订单数: {order_total}个"
                        
                        # 显示最近的几个订单
                        if order_items:
                            order_info += "\n━━━━━━━━━━━━━━━━━━"
                            
                            for i, order in enumerate(order_items[:3]):  # 只显示最近3个订单
                                order_status = order.get('orderStatusName', '未知状态')
                                order_time = order.get('orderCreateTime', '未知时间')
                                
                                # 获取商品信息
                                products = order.get('productList', [])
                                product_name = "未知商品"
                                if products:
                                    product_name = products[0].get('name', '未知商品')
                                    if len(product_name) > 18:  # 商品名太长则截断
                                        product_name = product_name[:18] + "..."
                                
                                # 状态相关信息
                                status_info = ""
                                if order.get('sign'):
                                    status_info += "📋 待签收"
                                
                                if order.get('commentable'):
                                    status_info += " ✅ 已签收"
                                
                                # 根据订单状态选择emoji
                                status_emoji = ""
                                if "待收货" in order_status:
                                    status_emoji = "🚚"
                                elif "已签收" in order_status:
                                    status_emoji = "🚚"
                                elif "待发货" in order_status:
                                    status_emoji = "📦"
                                elif "已取消" in order_status:
                                    status_emoji = "❌"
                                else:
                                    status_emoji = "📋"
                                
                                order_info += f"""
╭─ {status_emoji} 订单 {i+1} 
├🛒 商品: {product_name}
├📅 时间: {order_time[:16]}
{f"╰🔔 {status_info}" if status_info else "╰──────────────────"}"""
                    else:
                        order_info = f"\n📦 订单查询: {order_total}"
                    
                    sender.reply(f"""
======账号详情=====
📱 账号: {phone}
💎 当前积分: {pointValue}
📈 今日积分: {todaycoin}
📅 到期时间: {accountVip}{order_info}
==================""")
        
        except Exception as e:
            invalid_count += 1
            try:
                phone = mobile[:3] + '*' * 4 + mobile[7:]
            except:
                phone = "未知账号"
                
            sender.reply(f"""
=====系统错误=====
📱 账号: {phone}
❌ 错误: {str(e)}
==================""")
    
    # 显示统计信息，不自动清理
    if invalid_count > 0:
        sender.reply(f"""
=====统计信息=====
✅ 有效账号: {valid_count}个
❌ 失效账号: {invalid_count}个
💡 使用"福田清理"清除失效账号
==================""")
            
    # 移除原有的自动清理逻辑
    # 不再自动更新账号列表

def push(user, mobile, message):
    """推送消息到各个平台
    
    Args:
        user: 用户ID
        mobile: 手机号(已脱敏)
        message: 推送消息内容
    """
    push_msg = f"""
======账号通知======
📱 账号: {mobile}
📢 消息: {message}
=================="""

    # 发送到各个平台
    platforms = ['wb', 'tg', 'qq', 'qb', 'wx']
    for platform in platforms:
        try:
            middleware.push(platform, '', user, '', push_msg)
        except Exception as e:
            print(f"推送到{platform}失败: {str(e)}")

def fukuda_auth():
    """福田授权功能"""
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        exit(0)
        
    sender.reply(
        "=====福田授权=====\n"
        "  [1] 📱 一键授权所有用户\n" 
        "  [2] 👤 单独授权用户\n"
        "  [3] ⏰ 修改授权时间\n"
        "-------------------\n"
        "⚠️ 输入q退出操作\n"
        "=================="
    )
    xz = sender.input(60000, 1, False)
    
    if xz == 'q' or xz == 'Q':
        sender.reply("退出！")
        return
    elif xz == '':
        sender.reply(f'超时退出！')
        return
    elif xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('dd_fukuda_user')
        if not users:
            sender.reply("未找到任何绑定的福田账号")
            return
            
        sender.reply('请输入要给所有用户授权的月数！\n退出【q】！')
        sjts = sender.input(60000, 1, False)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("退出！")
            return
        elif sjts == '':
            sender.reply(f'超时退出！')
            return
        
        try:
            sjts = int(sjts)
        except:
            sender.reply(f'输入的月数无效，必须是数字！')
            return
            
        success_count = 0
        fail_count = 0
        
        for user in users:
            accountlist = middleware.bucketGet('dd_fukuda_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            accounts = eval(accountlist)
            for account in accounts:
                try:
                    accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                    token = middleware.bucketGet('dd_fukuda_token', account)
                    
                    if not token:
                        fail_count += 1
                        continue
                        
                    accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                    middleware.bucketSet('dd_fukuda_auth', account, accountVip)
                    
                    # 更新青龙变量
                    mobile = token.split('#')[0]
                    phone = mobile[:3] + '*' * 4 + mobile[7:]
                    Addenvs(osname=osname, value=token, account=account, phone=phone)
                    success_count += 1
                except:
                    fail_count += 1
                    
        msg = f"一键授权完成!\n成功授权: {success_count}个账号\n授权失败: {fail_count}个账号\n授权月数: {sjts}月"
        sender.reply(msg)
        
    elif xz == '2':
        # 单独授权用户
        msg = f'请输入需要授权的账号id\n通过给机器人发送myuid获得\n退出【q】！'
        sender.reply(msg)
        myuid = sender.input(60000, 1, False)
        if myuid == 'q' or myuid == 'Q':
            sender.reply("退出！")
            return
        elif myuid == '':
            sender.reply(f'超时退出！')
            return
            
        accountlist = middleware.bucketGet('dd_fukuda_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"未找到{myuid}的福田账号信息!")
            return
            
        accounts = eval(accountlist)
        n = 0
        msg = '========福田授权========\n'
        msg += '0、授权所有账号\n======================\n'
        
        for account in accounts:
            n += 1
            accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
            if len(accountVip) == 0:
                accountVip = '未授权'
            msg += f'{n}、账号:{account}\n授权时间: {accountVip}\n======================\n'
            
        msg += f'回复序号选择账号,退出【q】！'
        sender.reply(msg)
        xz = sender.input(60000, 1, False)
        
        if xz == 'q' or xz == 'Q':
            sender.reply("退出！")
            return
        elif xz == '':
            sender.reply(f'超时退出！')
            return
            
        if xz == '0':
            # 修改该用户的所有账号
            sender.reply('请输入要调整的天数:\n正数增加天数,负数减少天数\n例如: 100 或 -100')
            days = sender.input(60000, 1, False)
            
            if days == 'q' or days == 'Q':
                sender.reply("退出！")
                return
            elif days == '':
                sender.reply(f'超时退出！')
                return
                
            try:
                days = int(days)
                success_count = 0
                for account in accounts:
                    try:
                        accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                        token = middleware.bucketGet('dd_fukuda_token', account)
                        
                        if not token:
                            continue
                            
                        if len(accountVip) == 0 or accountVip == '未授权':
                            current_date = today_date
                        else:
                            current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                            
                        new_date = current_date + timedelta(days=days)
                        middleware.bucketSet('dd_fukuda_auth', account, str(new_date))
                        
                        mobile = token.split('#')[0]
                        phone = mobile[:3] + '*' * 4 + mobile[7:]
                        Addenvs(osname=osname, value=token, account=account, phone=phone)
                        success_count += 1
                    except:
                        continue
                        
                msg = f"批量修改完成!\n成功修改: {success_count}个账号\n调整天数: {days}天"
                sender.reply(msg)
                
            except ValueError:
                sender.reply('输入的天数无效!')
                return
                
        elif 1 <= int(xz) <= len(accounts):
            # 修改单个账号
            account = accounts[int(xz)-1]
            sender.reply('请输入要调整的天数:\n正数增加天数,负数减少天数\n例如: 100 或 -100')
            days = sender.input(60000, 1, False)
            
            if days == 'q' or days == 'Q':
                sender.reply("退出！")
                return
            elif days == '':
                sender.reply(f'超时退出！')
                return
                
            try:
                days = int(days)
                accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                token = middleware.bucketGet('dd_fukuda_token', account)
                
                if not token:
                    sender.reply("未找到账号token信息!")
                    return
                    
                if len(accountVip) == 0 or accountVip == '未授权':
                    current_date = today_date
                else:
                    current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                    
                new_date = current_date + timedelta(days=days)
                middleware.bucketSet('dd_fukuda_auth', account, str(new_date))
                
                mobile = token.split('#')[0]
                phone = mobile[:3] + '*' * 4 + mobile[7:]
                Addenvs(osname=osname, value=token, account=account, phone=phone)
                
                msg = f'修改成功!\n账号: {account}\n调整天数: {days}天\n新到期时间: {new_date}'
                sender.reply(msg)
                
            except ValueError:
                sender.reply('输入的天数无效!')
                return
        else:
            sender.reply('输入的序号无效!')
            return
    elif xz == '3':
        # 修改授权时间
        sender.reply(
            "=====修改授权时间=====\n"
            "  [1] 📱 修改所有用户\n"
            "  [2] 👤 修改单独用户\n"
            "-------------------\n"
            "⚠️ 输入q退出操作\n"
            "==================="
        )
        choice = sender.input(60000, 1, False)
        
        if choice == 'q' or choice == 'Q':
            sender.reply("退出！")
            return
        elif choice == '':
            sender.reply(f'超时退出！')
            return
        elif choice == '1':
            users = middleware.bucketAllKeys('dd_fukuda_user')
            if not users:
                sender.reply("未找到任何绑定的福田账号")
                return
                
            sender.reply('请输入要调整的天数:\n正数增加天数,负数减少天数\n例如: 100 或 -100')
            days = sender.input(60000, 1, False)
            if days == 'q' or days == 'Q':
                sender.reply("退出！")
                return
            elif days == '':
                sender.reply(f'超时退出！')
                return
                
            try:
                days = int(days)
                total_success = 0
                
                for user in users:
                    accountlist = middleware.bucketGet('dd_fukuda_user', user)
                    if accountlist == '' or accountlist == '{}':
                        continue
                        
                    accounts = eval(accountlist)
                    for account in accounts:
                        try:
                            accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                            token = middleware.bucketGet('dd_fukuda_token', account)
                            
                            if not token:
                                continue
                                
                            if len(accountVip) == 0 or accountVip == '未授权':
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                                
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('dd_fukuda_auth', account, str(new_date))
                            
                            mobile = token.split('#')[0]
                            phone = mobile[:3] + '*' * 4 + mobile[7:]
                            Addenvs(osname=osname, value=token, account=account, phone=phone)
                            total_success += 1
                        except:
                            continue
                            
                msg = f"批量修改完成!\n成功修改: {total_success}个账号\n调整天数: {days}天"
                sender.reply(msg)
                
            except ValueError:
                sender.reply('输入的天数无效!')
                return
                
        elif choice == '2':
            # 修改单独用户
            msg = f'请输入需要修改的账号id\n通过给机器人发送myuid获得\n退出【q】！'
            sender.reply(msg)
            myuid = sender.input(60000, 1, False)
            if myuid == 'q' or myuid == 'Q':
                sender.reply("退出！")
                return
            elif myuid == '':
                sender.reply(f'超时退出！')
                return
                
            accountlist = middleware.bucketGet('dd_fukuda_user', myuid)
            if accountlist == '' or accountlist == '{}':
                sender.reply(f"未找到{myuid}的福田账号信息!")
                return
                
            accounts = eval(accountlist)
            n = 0
            msg = '========修改授权时间========\n'
            msg += '0、修改所有账号\n======================\n'
            
            for account in accounts:
                n += 1
                accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                if len(accountVip) == 0:
                    accountVip = '未授权'
                msg += f'{n}、账号:{account}\n授权时间: {accountVip}\n======================\n'
                
            msg += f'回复序号选择账号,退出【q】！'
            sender.reply(msg)
            xz = sender.input(60000, 1, False)
            
            if xz == 'q' or xz == 'Q':
                sender.reply("退出！")
                return
            elif xz == '':
                sender.reply(f'超时退出！')
                return
                
            if xz == '0':
                # 修改该用户的所有账号
                sender.reply('请输入要调整的天数:\n正数增加天数,负数减少天数\n例如: 100 或 -100')
                days = sender.input(60000, 1, False)
                
                if days == 'q' or days == 'Q':
                    sender.reply("退出！")
                    return
                elif days == '':
                    sender.reply(f'超时退出！')
                    return
                    
                try:
                    days = int(days)
                    success_count = 0
                    for account in accounts:
                        try:
                            accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                            token = middleware.bucketGet('dd_fukuda_token', account)
                            
                            if not token:
                                continue
                                
                            if len(accountVip) == 0 or accountVip == '未授权':
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                                
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('dd_fukuda_auth', account, str(new_date))
                            
                            mobile = token.split('#')[0]
                            phone = mobile[:3] + '*' * 4 + mobile[7:]
                            Addenvs(osname=osname, value=token, account=account, phone=phone)
                            success_count += 1
                        except:
                            continue
                            
                    msg = f"批量修改完成!\n成功修改: {success_count}个账号\n调整天数: {days}天"
                    sender.reply(msg)
                    
                except ValueError:
                    sender.reply('输入的天数无效!')
                    return
                    
            elif 1 <= int(xz) <= len(accounts):
                # 修改单个账号
                account = accounts[int(xz)-1]
                sender.reply('请输入要调整的天数:\n正数增加天数,负数减少天数\n例如: 100 或 -100')
                days = sender.input(60000, 1, False)
                
                if days == 'q' or days == 'Q':
                    sender.reply("退出！")
                    return
                elif days == '':
                    sender.reply(f'超时退出！')
                    return
                    
                try:
                    days = int(days)
                    accountVip = middleware.bucketGet('dd_fukuda_auth', account) or ''
                    token = middleware.bucketGet('dd_fukuda_token', account)
                    
                    if not token:
                        sender.reply("未找到账号token信息!")
                        return
                        
                    if len(accountVip) == 0 or accountVip == '未授权':
                        current_date = today_date
                    else:
                        current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                        
                    new_date = current_date + timedelta(days=days)
                    middleware.bucketSet('dd_fukuda_auth', account, str(new_date))
                    
                    mobile = token.split('#')[0]
                    phone = mobile[:3] + '*' * 4 + mobile[7:]
                    Addenvs(osname=osname, value=token, account=account, phone=phone)
                    
                    msg = f'修改成功!\n账号: {account}\n调整天数: {days}天\n新到期时间: {new_date}'
                    sender.reply(msg)
                    
                except ValueError:
                    sender.reply('输入的天数无效!')
                    return
        else:
            sender.reply('输入的选项无效!')
            return
    else:
        sender.reply('输入的选项无效!')
    return

def clean_expired_accounts():
    """清理过期的福田账号（删除青龙变量和数据桶内容）"""
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        exit(0)
        
    users = middleware.bucketAllKeys(bucket='dd_fukuda_user')
    sender.reply(
        "=====清理统计=====\n"
        f"📊 找到用户数: {len(users) if users else 0}\n"
        "==================="
    )
    
    if not users:
        sender.reply("❌ 没有找到任何绑定的福田账号")
        exit(0)
        
    cleaned_count = 0
    cleaned_vars = 0
    login_failed_count = 0  # 新增：登录失效账号计数
    
    for user in users:
        accountlist = middleware.bucketGet(bucket='dd_fukuda_user', key=user)
        if not accountlist:
            continue
            
        accounts = eval(accountlist)
        valid_accounts = []
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='dd_fukuda_auth', key=account) or ''
            token = middleware.bucketGet(bucket='dd_fukuda_token', key=account)
            
            should_clean = False
            clean_reason = ""
            
            # 检查是否有token
            if not token:
                should_clean = True
                clean_reason = "缺少Token信息"
            else:
                # 检查登录状态
                mobile = token.split('#')[0]
                password = token.split('#')[1]
                login_account, memberID, login_token = login(mobile, password)
                
                if login_token is False:
                    should_clean = True
                    clean_reason = "账号登录失效"
                    login_failed_count += 1
                else:
                    # 检查授权状态
                    if len(accountVip) == 0 or accountVip <= today_time:
                        should_clean = True
                        clean_reason = "授权已过期"
            
            if should_clean:
                try:
                    # 检查是否开启过期提醒
                    expire_notify = middleware.bucketGet('dd_fukuda_config', 'expire_notify')
                    if expire_notify is None or expire_notify.lower() == 'true':
                        # 发送清理提醒
                        if token:
                            mobile = token.split('#')[0]
                            phone = mobile[:3] + '*' * 4 + mobile[7:]
                        else:
                            phone = f"账号{account}"
                        
                        push(user, phone, f"""
⚠️ 福田账号已被清理
------------------
❌ 清理原因: {clean_reason}
💡 如需继续使用请重新绑定""")
                    
                    # 删除青龙变量
                    qlid = allenvs(osname=osname, account=account)
                    if qlid:
                        delenvs(id=qlid)
                        cleaned_vars += 1
                    
                    # 删除数据桶中的内容
                    middleware.bucketDel(bucket='dd_fukuda_token', key=account)
                    middleware.bucketDel(bucket='dd_fukuda_auth', key=account)
                    cleaned_count += 1
                except Exception as e:
                    print(f"处理账号 {account} 时出错: {str(e)}")
                    continue
            else:
                valid_accounts.append(account)
        
        # 更新用户的账号列表
        if valid_accounts:
            middleware.bucketSet(bucket='dd_fukuda_user', key=user, value=str(valid_accounts))
        else:
            middleware.bucketDel(bucket='dd_fukuda_user', key=user)
    
    sender.reply(
        "=====清理完成=====\n"
        f"🧹 清理账号数: {cleaned_count}个\n"
        f"🧹 清理青龙变量: {cleaned_vars}个\n"
        f"📱 登录失效: {login_failed_count}个\n"
        f"⏰ 授权过期: {cleaned_count - login_failed_count}个\n"
        "==================="
    )

def cx_orders(memberID, userId, mobile, stored_token):
    """查询订单信息"""
    try:
        # 构建订单查询参数
        payload = {
            "memberId": memberID,
            "userId": userId,
            "userType": "61",
            "uid": userId,
            "mobile": mobile,
            "tel": mobile,
            "phone": mobile,
            "brandName": "萨普",
            "seriesName": "萨普T",
            "token": "ebf76685e48d4e14a9de6fccc76483e3",  # 使用硬编码的token
            "safeEnc": int(time.time() * 1000),
            "businessId": 1,
            "pageNum": 1,
            "pageSize": 10
        }
        
        headers = {
            'User-Agent': "web",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/json",
            'app-key': "7918d2d1a92a02cbc577adb8d570601e72d3b640",
            'content-type': "application/json; charset=utf-8",
            'token': "",  # 订单API的token在headers中为空
            'app-token': "58891364f56afa1b6b7dae3e4bbbdfbfde9ef489"
        }
        
        url = "https://czyl.foton.com.cn/ehomes-new/homeManager/api/other/foton365MyOrders"
        
        session = create_proxy_session(headers)
        response = session.post(url, data=json.dumps(payload), timeout=15)
        if response.status_code != 200:
            return f"HTTP错误: {response.status_code}", []
            
        result = response.json()
        if result.get('code') != 200:
            return f"查询失败: {result.get('msg', '未知错误')}", []
            
        data = result.get('data', {})
        items = data.get('items', [])
        total = data.get('total', 0)
        
        return total, items
        
    except Exception as e:
        return f"查询异常: {str(e)}", []

def cxdd():
    """查询订单详情"""
    # 获取最新的用户账号列表
    current_uservalue = middleware.bucketGet(bucket='dd_fukuda_user', key=userid) or ''
    if len(current_uservalue) == 0:
        sender.reply("""
======未绑定账号=====
❌ 未找到任何账号信息
💡 发送"福田登录"绑定
==================""")
        return

    accounts = eval(current_uservalue)
    valid_accounts = []
    
    # 构建账号选择菜单
    if len(accounts) > 1:
        message = '=====选择查询账号=====\n'
        count = 1
        
        for account in accounts:
            Token = middleware.bucketGet(bucket='dd_fukuda_token', key=account)
            if not Token:
                continue
                
            mobile = Token.split('#')[0]
            phone = mobile[:3] + '*' * 4 + mobile[7:]
            message += f'{count}. 账号: {phone}\n'
            valid_accounts.append(account)
            count += 1
            
        if not valid_accounts:
            sender.reply("""
======无有效账号======
❌ 未找到有效账号信息
💡 请重新绑定账号
==================""")
            return
            
        message += '------------------\n请选择要查询的账号序号\n⚠️ 输入"q"退出操作\n=================='
        sender.reply(message)
        
        mes = sender.input(120000, 1, False)
        mes = ValueErrors(value=mes, count=len(valid_accounts))
        account = valid_accounts[mes - 1]
    else:
        account = accounts[0]
        valid_accounts = [account]
    
    # 获取账号信息
    Token = middleware.bucketGet(bucket='dd_fukuda_token', key=account)
    if not Token:
        sender.reply("❌ 未找到账号Token信息")
        return
        
    mobile = Token.split('#')[0]
    password = Token.split('#')[1]
    phone = mobile[:3] + '*' * 4 + mobile[7:]
    
    # 登录获取最新信息
    account, memberID, token = login(mobile, password)
    if not token:
        sender.reply(f"""
==================
    登录失败
==================
📱 账号: {phone}
❌ 状态: 登录失败
==================""")
        return
    
    # 查询订单信息
    sender.reply("正在查询订单信息...")
    order_total, order_items = cx_orders(memberID, account, mobile, Token)
    
    if isinstance(order_total, str):
        sender.reply(f"""
=====订单查询失败=====
📱 账号: {phone}
❌ 错误: {order_total}
==================""")
        return
    
    if order_total == 0:
        sender.reply(f"""
=====订单查询结果=====
📱 账号: {phone}
📦 订单总数: 0个
💡 暂无订单记录
==================""")
        return
    
    # 显示订单详情
    message = f"""
=====订单查询结果=====
📱 账号: {phone}
📦 订单总数: {order_total}个
=================="""
    
    for i, order in enumerate(order_items):
        order_number = order.get('orderNumber', '未知订单号')
        order_status = order.get('orderStatusName', '未知状态')
        order_time = order.get('orderCreateTime', '未知时间')
        merchant_name = order.get('merchantName', '未知商家')
        payable_amount = order.get('payableAmount', '0.00')
        
        # 获取商品信息
        products = order.get('productList', [])
        product_info = "未知商品"
        if products:
            product = products[0]
            product_name = product.get('name', '未知商品')
            if len(products) > 1:
                product_info = f"{product_name} 等{len(products)}件商品"
            else:
                product_info = product_name
        
        # 状态相关信息
        status_info = ""
        if order.get('sign'):
            status_info += "📋 待签收"
        
        if order.get('commentable'):
            status_info += " ✅ 已签收"
            
        # 根据订单状态选择emoji
        status_emoji = ""
        if "待收货" in order_status:
            status_emoji = "🚚"
        elif "已签收" in order_status:
            status_emoji = "🚚"
        elif "待发货" in order_status:
            status_emoji = "📦"
        elif "已取消" in order_status:
            status_emoji = "❌"
        else:
            status_emoji = "📋"
        
        message += f"""
╭─ {status_emoji} 订单 {i+1} 
├🛒 商品: {product_info}
├📅 时间: {order_time[:16]}
{f"╰🔔 {status_info}" if status_info else "╰──────────────────"}"""
    
    sender.reply(message)

today_date = datetime.now().date()
today_time = str(today_date)
QLurl, ClientID, ClientSecret, FukudaVipmoney, osname, Fukudacoin, use_ma_pay, proxy_url, use_daidai, panel_group = PluginsData()
if use_daidai:
    qltoken = DDtoken(QLurl, ClientID, ClientSecret)
else:
    qltoken = QLtoken(QLurl, ClientID, ClientSecret)
usermessage = sender.getMessage()
imtype = sender.getImtype()
if '登录' in usermessage or '登陆' in usermessage:
    if '批量' in usermessage:
        batch_bind()
    else:
        bind()
elif '管理' in usermessage:
    Administration()
elif '福田查询' in usermessage:
    cxs()
elif '福田订单查询' in usermessage:
    cxdd()
elif '福田授权' in usermessage:
    fukuda_auth()
elif '清理福田' in usermessage or '福田清理' in usermessage:
    clean_expired_accounts()
elif imtype == 'fake':
    """定时任务处理"""
    users = middleware.bucketAllKeys(bucket='dd_fukuda_user')
    if not users:
        exit(0)
        
    # 检查是否开启过期提醒
    expire_notify = middleware.bucketGet('dd_fukuda_config', 'expire_notify')
    if expire_notify is None or expire_notify.lower() == 'true':
        for user in users:
            try:
                uservalue = middleware.bucketGet(bucket='dd_fukuda_user', key=user) or ''
                if not uservalue:
                    continue
                    
                accounts = eval(uservalue)
                for account in accounts:
                    try:
                        token = middleware.bucketGet(bucket='dd_fukuda_token', key=account)
                        accountVip = middleware.bucketGet(bucket='dd_fukuda_auth', key=account) or ''
                        
                        if not token:
                            continue
                            
                        mobile = token.split('#')[0]
                        password = token.split('#')[1]
                        phone = mobile[:3] + '*' * 4 + mobile[7:]
                        
                        account, memberID, token = login(mobile, password)
                        if token is False:
                            push(user, phone, """
⏰ 定时检测提醒
------------------
❌ 账号密码已失效
💡 请尽快更新账号""")
                            continue
                            
                        # 检查授权状态
                        if len(accountVip) == 0 or accountVip < today_time:
                            push(user, phone, """
⏰ 定时检测提醒
------------------
❌ 授权已过期
💡 请及时续费授权""")
                        else:
                            try:
                                expire_date = datetime.strptime(accountVip, '%Y-%m-%d').date()
                                days_left = (expire_date - datetime.now().date()).days
                                if days_left <= 3:
                                    push(user, phone, f"""
⏰ 定时检测提醒
------------------
⚠️ 授权即将到期
📅 到期时间: {accountVip}
⏳ 剩余天数: {days_left}天
💡 请及时续费授权""")
                            except:
                                pass
                            
                    except Exception as e:
                        print(f"处理账号 {account} 时出错: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"处理用户 {user} 时出错: {str(e)}")
                continue
