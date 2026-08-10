#[pin:false]
#[public:true]
# [rule: ^胖乖管理$]
# [rule: ^管理胖乖$]
# [rule: ^胖乖查询$]
# [rule: ^查询胖乖$]
# [rule: ^胖乖登录$]
# [rule: ^登录胖乖$]
# [rule: ^登陆胖乖$]
# [rule: ^胖乖登陆$]
# [rule: ^胖乖授权$]
# [rule: ^胖乖清理$]
# [rule: ^清理胖乖$]
# [cron: 18 8,15 * * *]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [version: 4.4]
# [admin: false]
# [author: sky2022]
# [price: 12.88]
# [title: 胖乖生活]
# [icon: https://y.gtimg.cn/music/photo_new/T053M000002Qqrye0oyZSp.jpg]
# [description: 2.0全新UI <br>指令：胖乖登录、胖乖管理、胖乖查询、胖乖清理<br>定时任务：每天8点和15点自动检测授权过期及CK失效并推送通知<br>4.4更新：新增定时检测推送，每天8点/15点自动检测授权到期和Token失效状态并通知用户<br>3.9更新：优化赞赏码支付，同时新增码支付，需使用市场卡密系统！<br>4.3更新：统一面板配置为面板类型+对接面板配置，并新增呆呆面板分组配置]

import middleware
import time
import requests
import hashlib
from urllib.parse import urlparse
import json
from datetime import datetime, timedelta
from decimal import Decimal
import urllib.parse
import re

# [param: {"required":true,"key":"dd_pg_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_pg_config.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_pg_config.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_pg_config.panel_group","bool":false,"placeholder":"例:胖乖","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_pg_config.osname","bool":false,"placeholder":"必填项,例:pangguai","name":"面板变量名","desc":"提交到面板中的胖乖变量名"}]
# [param: {"required":true,"key":"dd_pg_config.pgVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_pg_config.pgcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_pg_config.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_pg_user', key=userid) or ''

def normalize_panel_type(panel_type_value):
    """统一解析面板类型。"""
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    return ''

def getusercontent():
    """获取插件配置信息"""
    dd_pg_osname = middleware.bucketGet('dd_pg_config', 'osname') or 'pangguai'
    panel_type = normalize_panel_type(middleware.bucketGet('dd_pg_config', 'panel_type') or '')
    if not panel_type:
        sender.reply("对接面板类型填写无效，请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai")
        exit(0)

    panel_config = (middleware.bucketGet('dd_pg_config', 'panel_config') or '').strip()
    dd_pg_qlname = panel_config if panel_type == 'qinglong' else ''
    dd_pg_ddname = panel_config if panel_type == 'daidai' else ''
    dd_managecommand = middleware.bucketGet('dd_pg_config', 'dd_managecommand') or '胖乖管理'
    dd_querycommand = middleware.bucketGet('dd_pg_config', 'dd_querycommand') or '胖乖查询'
    dd_signcommand = middleware.bucketGet('dd_pg_config', 'dd_signcommand') or '胖乖登录'
    
    # 生成随机指令
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    # 获取价格配置
    pgVipmoney = Decimal(middleware.bucketGet('dd_pg_config', 'pgVipmoney') or '1')
    pgcoin = int(middleware.bucketGet('dd_pg_config', 'pgcoin') or '0')
    panel_group = (middleware.bucketGet('dd_pg_config', 'panel_group') or '').strip()
    
    return (dd_pg_osname, dd_pg_qlname, dd_managecommand, dd_querycommand,
            dd_signcommand, randommanagecommand, randomquerycommand,
            randomsigncommand, pgVipmoney, pgcoin, panel_type == 'daidai', dd_pg_ddname, panel_group)

def seekql():
    """连接并验证面板配置"""
    try:
        panel_config = dd_pg_ddname if use_daidai else dd_pg_qlname
        if len(panel_config) == 0:
            if use_daidai:
                sender.reply("""=======配置错误=====
❌ 未配置呆呆面板信息
------------------
请在插件配置中填写:
• 对接面板类型: 呆呆
• 对接面板配置: Host丨AppKey丨AppSecret
====================""")
            else:
                sender.reply("""=======配置错误=====
❌ 未配置青龙面板信息
------------------
请在插件配置中填写:
• 对接面板类型: 青龙
• 对接面板配置: Host丨ClientID丨ClientSecret
====================""")
            exit(0)
            
        qllist = panel_config.split('丨')
        if len(qllist) != 3:
            if use_daidai:
                sender.reply(f"""=======格式错误=====
❌ 呆呆面板配置格式错误
------------------
当前格式: {panel_config}
正确格式:
Host丨AppKey丨AppSecret
====================""")
            else:
                sender.reply(f"""=======格式错误=====
❌ 青龙面板配置格式错误
------------------
当前格式: {panel_config}
正确格式:
Host丨ClientID丨ClientSecret
====================""")
            exit(0)
            
        QLurl = qllist[0].strip()
        ClientID = qllist[1].strip()
        ClientSecret = qllist[2].strip()
        
        if not all([QLurl, ClientID, ClientSecret]):
            sender.reply("❌ 面板配置参数不完整")
            exit(0)
            
        if not QLurl.startswith(('http://', 'https://')):
            sender.reply(f"❌ 面板地址格式错误: {QLurl}")
            exit(0)
            
        try:
            if use_daidai:
                qltoken = DDtoken(DDurl=QLurl, AppKey=ClientID, AppSecret=ClientSecret)
            else:
                qltoken = QLtoken(QLurl=QLurl, ClientID=ClientID, ClientSecret=ClientSecret)
            return QLurl, qltoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")
            
    except Exception as e:
        sender.reply(f"""=======网络错误=====
❌ 无法连接{'呆呆' if use_daidai else '青龙'}面板
------------------
请检查:
1. 面板是否运行
2. 网络是否正常
3. 配置是否正确
4. 错误信息: {str(e)}
------------------
当前配置:
• 地址: {QLurl if 'QLurl' in locals() else '未设置'}
• Key: {ClientID[:4] + '****' if 'ClientID' in locals() else '未设置'}
====================""")
        exit(0)

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        
        if response.status_code != 200:
            sender.reply(f"""=======请求失败=====
❌ 青龙API请求失败
------------------
状态码: {response.status_code}
请检查:
• API地址是否正确
• 面板是否正常运行
====================""")
            exit(0)
            
        result = response.json()
        if "token" in result.get('data', {}):
            return result['data']['token']
        else:
            sender.reply("""=======认证失败=====
❌ 获取Token失败
------------------
请检查:
• ClientID是否正确
• ClientSecret是否正确
• 应用是否有权限
====================""")
            exit(0)
            
    except requests.exceptions.RequestException as e:
        sender.reply(f"""=======网络错误=====
❌ 连接青龙面板失败
------------------
请检查:
• 青龙地址是否正确
• 网络是否正常
• 错误信息: {str(e)}
====================""")
        exit(0)
    except Exception as e:
        sender.reply(f"""=======系统错误=====
❌ 处理请求时出错
------------------
请检查:
• 配置格式是否正确
• 错误信息: {str(e)}
====================""")
        exit(0)

def DDtoken(DDurl, AppKey, AppSecret):
    """获取呆呆面板token"""
    try:
        url = f'{DDurl}/api/open-api/token'
        response = requests.post(url, json={"app_key": AppKey, "app_secret": AppSecret})
        if response.status_code != 200:
            sender.reply("❌ 呆呆面板API请求失败")
            exit(0)
        result = response.json()
        access_token = result.get('data', {}).get('access_token')
        if access_token:
            return access_token
        sender.reply("❌ 获取呆呆面板Token失败")
        exit(0)
    except Exception as e:
        sender.reply(f"❌ 连接呆呆面板失败: {str(e)}")
        exit(0)

def QLzt(osname, value, account, phone):
    """添加青龙变量"""
    try:
        accountVip = middleware.bucketGet(bucket='dd_pg_auth', key=account) or ''
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if use_daidai:
            data = {
                "value": value,
                "name": osname,
                "remarks": f'胖乖:{phone}丨用户:{userid}丨授权时间:{accountVip}丨胖乖管理'
            }
            if panel_group:
                data["group"] = panel_group
            r = requests.post(f"{QLurl}/api/envs", headers=headers, json=data)
            if r.status_code not in (200, 201):
                sender.reply("❌ 添加呆呆面板变量失败")
                exit(0)
            return
        else:
            qlurl = f"{QLurl}/open/envs"
            data = [{
                "value": value,
                "name": osname,
                "remarks": f'胖乖:{phone}丨用户:{userid}丨授权时间:{accountVip}丨胖乖管理'
            }]
            r = requests.post(qlurl, headers=headers, data=json.dumps(data))
            r_json = r.json()
            if "value must be unique" in r.text:
                return
            else:
                qlid = r_json['data'][0]['id']
                return
    except Exception as e:
        sender.reply(f"""=======添加失败=====
❌ 添加青龙变量失败
------------------
请检查:
• 青龙面板状态
• 变量格式是否正确
• 错误信息: {str(e)}
====================""")
        exit(0)

def QLupdate(osname, value, account, qlid, phone):
    """更新青龙变量"""
    try:
        accountVip = middleware.bucketGet(bucket='dd_pg_auth', key=account) or ''
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        if use_daidai:
            data = {
                "value": value,
                "name": osname,
                "remarks": f'胖乖:{phone}丨用户:{userid}丨授权时间:{accountVip}丨胖乖管理'
            }
            if panel_group:
                data["group"] = panel_group
            response = requests.put(f"{QLurl}/api/envs/{qlid}", headers=headers, json=data)
            if response.status_code == 200:
                return qlid, None
            sender.reply("❌ 更新呆呆面板变量失败")
            exit(0)
        else:
            qlurl = f"{QLurl}/open/envs"
            data = {
                "value": value,
                "name": osname,
                "remarks": f'胖乖:{phone}丨用户:{userid}丨授权时间:{accountVip}丨胖乖管理',
                "id": qlid
            }
            response = requests.put(qlurl, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                response_json = response.json()
                data = response_json['data']
                if data is None:
                    exit(0)
                return data['id'], data['createdAt']
            else:
                sender.reply("""=======更新失败=====
❌ 更新青龙变量失败
------------------
请联系管理员处理
====================""")
                exit(0)
    except Exception as e:
        sender.reply(f"""=======更新错误=====
❌ 更新变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def Addenvs(osname, value, account, phone):
    """添加或更新青龙变量"""
    try:
        qlid = None
        phone_qlid = None
        if use_daidai:
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json"
            }
            response = requests.get(url=f"{QLurl}/api/envs", headers=headers, params={"keyword": str(account), "page_size": 100}).json()
            envslist = response.get('data', [])
        else:
            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json"
            }
            response = requests.get(url=url, headers=headers).json()
            if response['code'] != 200:
                sender.reply("""=======连接失败=====
❌ 连接青龙获取变量失败
====================""")
                exit(0)
            envslist = response['data']

        for envs in envslist:
            remarks = envs.get('remarks')
            envname = envs.get('name')
            if not remarks or envname != osname:
                continue
                
            if account in remarks:
                qlid = envs['id']
                break
                
            if '胖乖:' in remarks:
                try:
                    remark_phone = remarks.split('胖乖:')[1].split('丨')[0]
                    if remark_phone == phone:
                        phone_qlid = envs['id']
                except:
                    continue
                
        if not qlid and phone_qlid:
            qlid = phone_qlid
            
        value = urllib.parse.quote(value)
        if qlid:
            # 更新现有变量
            QLupdate(osname, value, account, qlid, phone)
        else:
            # 创建新变量
            QLzt(osname, value, account, phone)
    except Exception as e:
        sender.reply(f"""=======操作失败=====
❌ 处理变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def times13():
    """生成13位时间戳"""
    timestamp = time.time()
    return int(timestamp * 1000)

def calculate_sha2562(timestamp_ms, token, url):
    """计算SHA256签名"""
    parsed_url = urlparse(url)
    path = parsed_url.path
    data = f'appSecret=xl8v4s/5qpBLvN+8CzFx7vVjy31NgXXcedU7G0QpOMM=&channel=alipay&timestamp={timestamp_ms}&token={token}&version=1.57.0&{path}'
    sha256_hash = hashlib.sha256()
    sha256_hash.update(data.encode('utf-8'))
    return sha256_hash.hexdigest()

def login(token):
    """登录验证token"""
    try:
        url = "https://userapi.qiekj.com/user/info"
        timestamp_ms = times13()
        sign = calculate_sha2562(timestamp_ms, token, url)
        payload = f"token={token}"

        headers = {
            'User-Agent': "okhttp/3.14.9",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': f"{token}",
            'Version': "1.57.0",
            'channel': "android_app",
            'phoneBrand': "meizu",
            'timestamp': f"{timestamp_ms}",
            'sign': f"{sign}",
        }

        response = requests.post(url, data=payload, headers=headers)
        if '成功' in response.text:
            r = response.json()
            phone = r['data']['phone']
            # 创建一个带星号的手机号用于显示
            display_phone = phone[:3] + '*' * 4 + phone[7:]
            account = r['data']['id']
            # 返回完整手机号和账号ID
            return phone, str(account), display_phone
        else:
            return 'Token失效', 'Token失效', 'Token失效'
    except Exception as e:
        sender.reply(f"""=======登录失败=====
❌ 验证Token失败
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def sms(phone):
    """发送验证码"""
    try:
        url = "https://userapi.qiekj.com/common/sms/sendCode"
        timestamp_ms = times13()
        sign = calculate_sha2562(timestamp_ms, '', url)
        payload = f"phone={phone}&template=reg"

        headers = {
            'User-Agent': "okhttp/3.14.9",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "",
            'Version': "1.57.0",
            'channel': "android_app",
            'phoneBrand': "meizu",
            'timestamp': f"{timestamp_ms}",
            'sign': f"{sign}",
        }

        response = requests.post(url, data=payload, headers=headers)
        result = response.json()
        
        if result.get('code') == 0 and result.get('msg') == '成功':
            return True
        else:
            error_msg = result.get('msg', '未知错误')
            sender.reply(f"""=======发送失败=====
❌ 获取验证码失败
------------------
错误信息: {error_msg}
====================""")
            exit(0)
            
    except Exception as e:
        sender.reply(f"""=======请求失败=====
❌ 发送验证码失败
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def smslogin(phone, code):
    """短信验证码登录"""
    if len(code) != 4:
        sender.reply("""=======验证码错误=====
❌ 请输入正确的4位验证码
====================""")
        exit(0)
        
    try:
        url = "https://userapi.qiekj.com/user/reg"
        timestamp_ms = times13()
        sign = calculate_sha2562(timestamp_ms, '', url)
        payload = f"channel=h5&phone={phone}&verify={code}"
        headers = {
            'User-Agent': "okhttp/3.14.9",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded",
            'Authorization': "",
            'Version': "1.57.0",
            'channel': "android_app",
            'phoneBrand': "meizu",
            'timestamp': f"{timestamp_ms}",
            'sign': f"{sign}"
        }
        response = requests.post(url, data=payload, headers=headers)
        if '成功' in response.text:
            r = response.json()
            token = r['data']['token']
            phone, account, display_phone = login(token)
            if phone == 'Token失效':
                sender.reply("""=======登录失败=====
❌ 登录验证失败
====================""")
                exit(0)
            else:
                return phone, account, token, display_phone
        else:
            sender.reply("""=======登录失败=====
❌ 登录请求失败
====================""")
            exit(0)
    except Exception as e:
        sender.reply(f"""=======系统错误=====
❌ 登录处理失败
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def bind():
    """绑定账号"""
    def accvip(Newaddition):
        status = '添加' if Newaddition else '更新'
        auth_status = '✅ 已授权' if accountVip >= today_time else '⚠️ 未授权'
        next_step = f'发送 {randommanagecommand} 可管理账号' if accountVip >= today_time else f'发送 {randommanagecommand} 可进行授权'
        
        success_msg = f"""=======绑定成功=====
📱 账号: {display_phone}
🔐 状态: {auth_status}
⏰ 操作: {next_step}
====================""" 

        if len(accountVip) != 0 and accountVip >= today_time:
            Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
        
        # 更新账号列表，确保不重复
        if account not in accounts:
            accounts.append(account)
            # 去重并保持顺序
            unique_accounts = list(dict.fromkeys(accounts))
            middleware.bucketSet(bucket='dd_pg_user', key=userid, value=f'{unique_accounts}')
            
        sender.reply(success_msg)

    sender.reply("""=======胖乖登录=====
请输入手机号:
------------------
回复"q"退出操作
====================""")
    input_phone = sender.input(120000, 1, False)
    
    if input_phone.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)
        
    if not input_phone.isdigit() or len(input_phone) != 11:
        sender.reply("""=======格式错误=====
❌ 请输入正确的11位手机号
====================""")
        exit(0)

    # 检查该手机号是否已经存在绑定账号
    existing_account = None
    old_auth = None
    accounts = []
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        for acc in accounts:
            acc_phone = middleware.bucketGet(bucket='dd_pg_mobile', key=acc)
            if acc_phone == input_phone:
                existing_account = acc
                # 保存旧账号的授权信息
                old_auth = middleware.bucketGet(bucket='dd_pg_auth', key=acc) or ''
                # 从账号列表中移除旧账号
                accounts.remove(acc)
                # 删除旧账号的其他信息
                middleware.bucketDel(bucket='dd_pg_mobile', key=acc)
                middleware.bucketDel(bucket='dd_pg_token', key=acc)
                # 删除旧账号的青龙变量
                qlid = allenvs(osname=dd_pg_osname, account=acc)
                if qlid:
                    delenvs(id=qlid)
                break
    
    sms(input_phone)
    sender.reply("""=======验证码登录=====
请输入收到的4位验证码:
------------------
回复"q"退出操作
====================""")
    code = sender.input(120000, 1, False)
    
    if code.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)
        
    phone, account, token, display_phone = smslogin(input_phone, code)
    
    # 保存新账号信息
    middleware.bucketSet(bucket='dd_pg_mobile', key=account, value=phone)
    middleware.bucketSet(bucket='dd_pg_token', key=account, value=token)
    
    # 如果有旧授权，转移到新账号
    if old_auth:
        middleware.bucketSet(bucket='dd_pg_auth', key=account, value=old_auth)
        # 如果授权未过期，更新青龙变量
        if old_auth >= today_time:
            Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
        
    # 新账号绑定
    if len(uservalue) == 0:
        accounts = []
        
    accountVip = middleware.bucketGet(bucket='dd_pg_auth', key=account) or ''
    accvip(True)  # 添加新账号

def ValueErrors(value, count):
    """验证输入值是否为有效的整数且在合理范围内"""
    try:
        value = int(value)
        if value > count or value == 0:
            sender.reply(f"""=======输入无效=====
❌ 请输入 1-{count} 之间的数字
====================""")
            exit(0)
        return value
    except ValueError:
        sender.reply("""=======输入无效=====
❌ 请输入正确的数字
====================""")
        exit(0)

def empower(empowertime, me_as_int):
    """授权时间计算"""
    day = me_as_int * 30
    try:
        if len(empowertime) == 0:
            # 没有授权时间，从今天开始计算
            delayed_date = today_date + timedelta(days=day)
        else:
            # 有授权时间，判断是否已过期
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            if empower_date <= today_date:
                # 已过期，从今天开始计算
                delayed_date = today_date + timedelta(days=day)
            else:
                # 未过期，在现有授权时间基础上累加
                delayed_date = empower_date + timedelta(days=day)
        
        return str(delayed_date)
    except Exception as e:
        print(f"授权时间计算出错: {str(e)}")
        return str(today_date + timedelta(days=day))

def management():
    """账号管理功能"""
    if len(uservalue) == 0:
        sender.reply(f"""=======未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
====================""")
        return

    count = 1
    account_list = """
======我的胖乖账号=====""" 
    
    # 获取并去重账号列表
    accounts = list(dict.fromkeys(eval(uservalue))) if uservalue else []
    middleware.bucketSet(bucket='dd_pg_user', key=userid, value=f'{accounts}')

    for account in accounts:
        accountVip = middleware.bucketGet(bucket='dd_pg_auth', key=f'{account}') or ''
        if len(accountVip) == 0:
            vip_status = '⚠️ 未授权'
        elif accountVip < today_time:
            vip_status = '❌ 已过期'
        else:
            vip_status = f'✅ {accountVip}'
        
        # 获取手机号码并进行隐私处理
        phone = middleware.bucketGet(bucket='dd_pg_mobile', key=account)
        if phone:
            display_phone = phone[:3] + '*' * 4 + phone[7:]
        else:
            display_phone = account[:3] + "****" + account[7:]
            
        account_list += f"""
------------------
[{count}] 账号信息
📱 账号: {display_phone}
🔐 授权: {vip_status}"""
        count += 1
            
    account_list += """
==================
回复数字选择账号
回复"q"退出操作
=================="""
        
    sender.reply(account_list)
        
    inputmessage = sender.input(120000, 1, False)
    if inputmessage == 'timeout':
        sender.reply('⏰ 操作超时,已退出')
        exit(0)
    elif inputmessage == 'q':
        sender.reply('✅ 已退出管理')
        exit(0)
            
    try:
        me_as_int = int(inputmessage)
        if me_as_int > count:
            sender.reply('❌ 输入的序号无效')
            exit(0)
    except ValueError:
        sender.reply('❌ 输入必须是数字')
        exit(0)
            
    account = accounts[me_as_int - 1]
    token = middleware.bucketGet(bucket='dd_pg_token', key=f'{account}')
    accountVip = middleware.bucketGet(bucket='dd_pg_auth', key=f'{account}') or ''
    phone, account_status, display_phone = login(token)
        
    if len(accountVip) == 0:
        vip_status = '⚠️ 未授权'
    elif accountVip < today_time:
        vip_status = '❌ 已过期'
    else:
        vip_status = f'✅ {accountVip}'
            
    account_info = f"""
=======账号详情======
📱 账号: {display_phone}
🔐 授权: {vip_status}
=================="""
    sender.reply(account_info)

    menu = """
=======账号管理======
[1] 授权账号
[2] 删除账号
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(menu)

    inputmessage = sender.input(120000, 1, False)
    if inputmessage == '2':
        confirm_msg = """=======删除警告=====
❌ 确定要删除该账号吗？
------------------
此操作不可恢复！
[y] 确认删除
[n] 取消操作
===================="""
        sender.reply(confirm_msg)
        
        yesorno = sender.input(120000, 1, False)
        if yesorno.lower() in ['y', '是']:
            accounts.remove(str(account))
            qlid = allenvs(osname=dd_pg_osname, account=str(account))
            delenvs(id=qlid)
            if len(accounts) == 0:
                middleware.bucketDel(bucket='dd_pg_user', key=userid)
            else:
                middleware.bucketSet(bucket='dd_pg_user', key=userid, value=f'{accounts}')
            sender.reply('✅ 账号删除成功!')
        else:
            sender.reply('✅ 已取消删除')
            exit(0)
            
    elif inputmessage == '1':
        auth_guide = """=======授权设置=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
===================="""
        sender.reply(auth_guide)
        
        mes = sender.input(120000, 1, False)
        if mes.lower() == 'q':
            sender.reply("✅ 已取消授权")
            exit(0)
            
        mes = ValueErrors(value=mes, count=999)
        money = Decimal(mes) * Decimal(pgVipmoney)
        
        zf(project='胖乖授权', me_as_int=mes, accountVip=accountVip, token=token,
           phone=phone, account=account)
           
        accountVip = empower(empowertime=accountVip, me_as_int=mes)
        middleware.bucketSet(bucket='dd_pg_auth', key=account, value=accountVip)
        Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
        
        result_msg = f"""=======订单完成=====
🎈 名称: 胖乖授权
🎉 数量: {mes} 个月
💰 金额: {money} 元
===================="""
        sender.reply(result_msg)
        
    elif inputmessage.lower() == 'q':
        sender.reply('✅ 已退出管理')
        exit(0)
    else:
        sender.reply('❌ 输入无效')
        exit(0)

def yesornos():
    """确认操作"""
    yesorno = sender.input(120000, 1, False)
    if yesorno.lower() in ['y', '是']:
        return True
    elif yesorno.lower() in ['n', '否']:
        return False
    elif yesorno == '':
        sender.reply('⏰ 输入超时！')
        exit(0)
    elif yesorno.lower() in ['q', '退出']:
        sender.reply('✅ 已退出!')
        exit(0)
    else:
        sender.reply('❌ 输入错误！')
        exit(0)

def zf(project, me_as_int, accountVip, token, phone, account):
    """支付处理"""
    try:
        zsm = middleware.bucketGet('dd_pg_config', 'zsm')
        use_ma_pay = middleware.bucketGet('dd_pg_config', 'use_ma_pay') == 'true'
        
        if not zsm and not use_ma_pay:
            sender.reply('❌ 未配置收款方式,请联系管理员!')
            exit(0)
            
        # 检查是否允许使用积分支付
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(pgcoin) * me_as_int
        
        # 构建支付选择菜单
        pay_menu = """=====选择支付方式===="""
        
        # 添加微信支付选项
        if zsm:
            money = Decimal(me_as_int) * Decimal(pgVipmoney)
            pay_menu += f"""
1️⃣ 微信支付
   💰 {money}元/{me_as_int}月"""
            
        # 添加码支付选项
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
            
            if ma_pay_config['switch'].lower() == 'true' and all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                money = Decimal(me_as_int) * Decimal(pgVipmoney)
                pay_menu += f"""
2️⃣ 码支付
   💰 {money}元/{me_as_int}月"""
            
        # 只有当pgcoin > 0时才显示积分支付选项
        if pgcoin and int(pgcoin) > 0:
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
                
            money = Decimal(me_as_int) * Decimal(pgVipmoney)
            
            pay_msg = f"""=====微信扫码支付====
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
                    
                if float(Money) >= float(money):
                    return True
                else:
                    sender.reply(f"""=====支付金额错误=====
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
            money = Decimal(me_as_int) * Decimal(pgVipmoney)
            
            # 生成订单号
            out_trade_no = f"PG{int(time.time())}{userid}"
            
            # 构造支付参数
            params = {
                'pid': ma_pay_config['pid'],
                'type': ma_pay_config['type'].split(',')[0],  # 默认使用第一个支付方式
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-胖乖授权-{str(money)}",
                'money': str(money),
                'notify_url': ma_pay_config['notify_url'],
                'return_url': ma_pay_config['return_url'],
                'param': userid  # 传递用户ID作为附加参数
            }
            
            # 按照ASCII码排序参数
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            
            # 拼接成URL键值对格式
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            
            # 添加密钥进行MD5签名
            sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
            
            # 添加签名到参数
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            # 发送支付请求
            gateway = ma_pay_config['gateway']
            if not gateway.endswith('/'):
                gateway += '/'
            submit_url = gateway + 'submit.php'
            
            try:
                response = requests.post(submit_url, data=params)
                if 'location.href' in response.text:
                    # 提取支付URL
                    match = re.search(r'location\.href\s*=\s*[\'"](.*?)[\'"]', response.text)
                    if match:
                        pay_url = match.group(1)
                        if not pay_url.startswith('http'):
                            pay_url = gateway + pay_url
                            
                        sender.reply(f"""=====码支付=====
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
                            check_url = gateway + 'api.php'
                            check_params = {
                                'act': 'order',
                                'pid': ma_pay_config['pid'],
                                'key': ma_pay_config['key'],
                                'out_trade_no': out_trade_no
                            }
                            
                            try:
                                check_resp = requests.get(check_url, params=check_params)
                                result = check_resp.json()
                                
                                if result.get('code') == 1:  # 支付成功
                                    return True
                            except:
                                continue
                                
                        sender.reply("❌ 支付超时,请重新发起支付!")
                        exit(0)
                else:
                    sender.reply("❌ 创建支付订单失败!")
                    exit(0)
            except Exception as e:
                sender.reply(f"❌ 支付请求失败: {str(e)}")
                exit(0)
                
        elif choice == '3' and pgcoin != 0:
            # 积分支付流程
            if int(usercoin) < zfcoin:
                sender.reply(f"""=====积分不足=====
👤 当前积分: {usercoin}
📍 需要积分: {zfcoin}
==================""")
                exit(0)
                
            confirm_msg = f"""=====积分支付确认=====
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

def cx(token):
    """查询账号信息"""
    try:
        # 查询用户余额和积分
        url = "https://userapi.qiekj.com/user/balance"
        timestamp_ms = times13()
        sign = calculate_sha2562(timestamp_ms, token, url)
        payload = f"token={token}"
        
        headers = {
            'User-Agent': "okhttp/3.14.9",
            'Authorization': token,
            'Version': "1.57.0", 
            'channel': "android_app",
            'timestamp': str(timestamp_ms),
            'sign': sign,
            'Content-Type': "application/x-www-form-urlencoded"
        }
        
        response = requests.post(url, data=payload, headers=headers)
        if '成功' in response.text:
            balance_data = response.json()['data']
            
            # 查询今日积分
            h = {
                'User-Agent': 'okhttp/3.14.9',
                'Accept': 'application/json, text/plain, */*',
                'channel': 'android_app',
                'Authorization': token,
                'Version': '1.57.0'
            }
            data = {
                'page': (None, '1'),
                'pageSize': (None, '100'),
                'type': (None, '100'),
                'receivedStatus': (None, '1'),
                'token': (None, token),
            }
            integral_response = requests.post(
                'https://userapi.qiekj.com/integralRecord/pageList', 
                headers=h, 
                files=data
            ).json()
            
            # 计算今日获得的积分
            current_date = datetime.now().strftime('%Y-%m-%d')
            today_integral = 0
            for item in integral_response['data']['items']:
                received_date = item['receivedTime'][:10]
                if received_date == current_date:
                    today_integral += item['amount']
                    
            return {
                'balance': balance_data['balance'],
                'integral': balance_data['integral'],
                'today_integral': today_integral
            }
        return None
    except:
        return None

def cxs():
    """查询所有账号"""
    if len(uservalue) == 0:
        sender.reply(f"""=======未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
====================""")
        return

    # 获取并去重账号列表
    accounts = list(dict.fromkeys(eval(uservalue))) if uservalue else []
    middleware.bucketSet(bucket='dd_pg_user', key=userid, value=f'{accounts}')

    for account in accounts:
        token = middleware.bucketGet(bucket='dd_pg_token', key=account)
        accountVip = middleware.bucketGet(bucket='dd_pg_auth', key=account) or ''
        phone = middleware.bucketGet(bucket='dd_pg_mobile', key=account)
        
        if len(accountVip) == 0 or accountVip < today_time:
            sender.reply(f"""=======授权过期=====
📱 账号: {phone[:3]}****{phone[7:]}
⚠️ 状态: 授权已过期
====================""")
            continue
            
        info = cx(token)
        if not info:
            sender.reply(f"""=======查询异常=====
📱 账号: {phone[:3]}****{phone[7:]}
❌ 状态: 查询失败
====================""")
            continue
            
        account_info = f"""=======账号详情=====
📱 账号: {phone[:3]}****{phone[7:]}
🎯 总积分: {info['integral']}
📈 今日积分: {info['today_integral']}
🔐 授权至: {accountVip}
===================="""
        sender.reply(account_info)

def push(user, account, message):
    """推送通知"""
    phone = middleware.bucketGet(bucket='dd_pg_mobile', key=account)
    if not phone:
        return
        
    phone = phone[:3] + "****" + phone[7:]
    push_msg = f"""=======账号通知=====
📱 账号: {phone}
📢 消息: {message}
===================="""

    # 获取并去重账号列表
    accountlist = middleware.bucketGet('dd_pg_user', user)
    if accountlist:
        accounts = list(dict.fromkeys(eval(accountlist)))
        middleware.bucketSet(bucket='dd_pg_user', key=user, value=f'{accounts}')

    middleware.push('wb', '', user, '', push_msg)
    middleware.push('tg', '', user, '', push_msg)
    middleware.push('qq', '', user, '', push_msg)
    middleware.push('qb', '', user, '', push_msg)
    middleware.push('wx', '', user, '', push_msg)

def pangguai_auth():
    """胖乖授权管理功能"""
    # 添加调试日志
    print("开始执行胖乖授权功能")
    
    if not sender.isAdmin():
        sender.reply("""=======权限错误=====
⛔ 您没有权限执行此操作
====================""")
        return
        
    # 获取必要的全局变量
    dd_pg_osname, dd_pg_qlname, _, _, _, _, _, _, _, _, _, _, _ = getusercontent()
    QLurl, qltoken = seekql()
    
    sender.reply("""=====胖乖授权=====
[1] 📱 一键授权所有用户
[2] 👤 单独授权用户
[3] ⏰ 修改授权时间
------------------
⚠️ 输入q退出操作
====================""")

    xz = sender.input(60000, 1, False)
    
    if not xz:  # 处理空输入
        sender.reply('⏰ 操作超时')
        return
        
    if xz.lower() == 'q':
        sender.reply("✅ 已退出授权")
        return

    if xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('dd_pg_user')
        if not users:
            sender.reply("""=======查询失败=====
❌ 未找到任何绑定账号
====================""")
            return
            
        sender.reply("""=======批量授权=====
📝 请输入授权月数
💡 示例输入: 1
⚠️ 输入q退出操作
====================""")

        sjts = sender.input(60000, 1, False)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif sjts == '':
            sender.reply('⏰ 操作超时')
            return
        
        try:
            sjts = int(sjts)
            success_count = 0
            fail_count = 0
            skip_count = 0
            
            for user in users:
                accountlist = middleware.bucketGet('dd_pg_user', user)
                if not accountlist or accountlist == '{}':
                    continue
                    
                # 获取并去重账号列表
                accounts = list(dict.fromkeys(eval(accountlist))) if accountlist else []
                middleware.bucketSet(bucket='dd_pg_user', key=user, value=f'{accounts}')
                
                for account in accounts:
                    try:
                        token = middleware.bucketGet('dd_pg_token', account)
                        if not token:
                            fail_count += 1
                            continue

                        # 获取当前授权时间
                        accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
                        
                        # 计算新的授权时间（在现有时间基础上累加）
                        new_vip_date = empower(empowertime=accountVip, me_as_int=sjts)
                        
                        # 更新授权时间
                        middleware.bucketSet('dd_pg_auth', account, new_vip_date)
                        
                        # 更新青龙变量
                        phone = middleware.bucketGet('dd_pg_mobile', key=account)
                        if phone:
                            Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
                            
                            # 添加授权成功日志
                            old_date = "无" if not accountVip else accountVip
                            print(f"授权成功 - 账号: {account}, 原授权期: {old_date}, 新授权期: {new_vip_date}")
                            success_count += 1
                        else:
                            fail_count += 1
                            
                    except Exception as e:
                        print(f"授权账号 {account} 失败: {str(e)}")
                        fail_count += 1
                        
            sender.reply(f"""=======授权完成=====
✅ 成功授权: {success_count}个
❌ 授权失败: {fail_count}个
⏰ 授权时长: {sjts}月
====================""")
                
        except ValueError:
            sender.reply("""=======输入错误=====
❌ 请输入有效的月数
====================""")
            return

    elif xz == '2':
        # 单独授权用户
        sender.reply("""=======单独授权=====
📝 请输入用户ID
💡 通过发送myuid获取
⚠️ 输入q退出操作
====================""")

        myuid = sender.input(60000, 1, False)
        if myuid == 'q' or myuid == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif myuid == '':
            sender.reply('⏰ 操作超时')
            return
            
        accountlist = middleware.bucketGet('dd_pg_user', myuid)
        if not accountlist or accountlist == '{}':
            sender.reply(f"""=======查询失败=====
❌ 未找到该用户账号信息
====================""")
            return
            
        # 获取并去重账号列表
        accounts = list(dict.fromkeys(eval(accountlist))) if accountlist else []
        middleware.bucketSet(bucket='dd_pg_user', key=myuid, value=f'{accounts}')
        
        msg = """=======账号列表=====
[0] 授权所有账号
------------------\n"""
        
        for i, account in enumerate(accounts, 1):
            accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
            vip_status = accountVip if accountVip else '未授权'
            msg += f"""[{i}] 账号信息:
📱 账号: {account}
⏰ 授权: {vip_status}
------------------\n"""
            
        msg += """💡 回复序号选择账号
⚠️ 输入q退出操作
====================""" 
        sender.reply(msg)
        
        xz = sender.input(60000, 1, False)
        if xz == 'q' or xz == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif xz == '':
            sender.reply('⏰ 操作超时')
            return
            
        try:
            xz = int(xz)
            if xz == 0:
                # 授权所有账号
                sender.reply("""=======批量授权=====
📝 请输入授权月数:
====================""")
                sjts = sender.input(60000, 1, False)
                
                try:
                    sjts = int(sjts)
                    success_count = 0
                    
                    for account in accounts:
                        try:
                            accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
                            token = middleware.bucketGet('dd_pg_token', account)
                            
                            if not token:
                                continue
                                
                            accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                            middleware.bucketSet('dd_pg_auth', account, accountVip)
                            
                            phone = middleware.bucketGet('dd_pg_mobile', key=account)
                            if phone:
                                Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
                            success_count += 1
                        except:
                            continue
                            
                    sender.reply(f"""=======授权完成=====
✅ 成功授权: {success_count}个
⏰ 授权时长: {sjts}月
====================""")
                    
                except ValueError:
                    sender.reply("""=======输入错误=====
❌ 请输入有效的月数
====================""")
                    return
                    
            elif 1 <= xz <= len(accounts):
                # 授权单个账号
                account = accounts[xz-1]
                sender.reply(f"""=======单独授权=====
📝 请输入授权月数:
====================""")
                sjts = sender.input(60000, 1, False)
                
                try:
                    sjts = int(sjts)
                    accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
                    token = middleware.bucketGet('dd_pg_token', account)
                    
                    if not token:
                        sender.reply("""=======授权失败=====
❌ 未找到账号Token信息
====================""")
                        return
                        
                    accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                    middleware.bucketSet('dd_pg_auth', account, accountVip)
                    
                    phone = middleware.bucketGet('dd_pg_mobile', key=account)
                    if phone:
                        Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
                    
                    sender.reply(f"""=======授权成功=====
📱 账号: {account}
⏰ 授权时长: {sjts}月
📅 到期时间: {accountVip}
====================""")
                    
                except ValueError:
                    sender.reply("""=======输入错误=====
❌ 请输入有效的月数
====================""")
                    return
            else:
                sender.reply("""=======输入错误=====
❌ 请输入有效的序号
====================""")
                return
        except ValueError:
            sender.reply("""=======输入错误=====
❌ 请输入有效的序号
====================""")
            return
            
    elif xz == '3':
        # 修改授权时间
        sender.reply("""=====修改授权时间=====
[1] 📱 修改所有用户
[2] 👤 修改单独用户
------------------
⚠️ 输入q退出操作
====================""")

        choice = sender.input(60000, 1, False)
        
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif choice == '':
            sender.reply('⏰ 操作超时')
            return
        elif choice == '1':
            users = middleware.bucketAllKeys('dd_pg_user')
            if not users:
                sender.reply("""=======查询失败=====
❌ 未找到任何绑定账号
====================""")
                return
                
            sender.reply("""=======批量修改=====
📝 请输入调整天数:
💡 正数增加,负数减少
⚠️ 示例: 30 或 -30
====================""")

            days = sender.input(60000, 1, False)
            if days == 'q' or days == 'Q':
                sender.reply("✅ 已退出授权")
                return
            elif days == '':
                sender.reply('⏰ 操作超时')
                return
                
            try:
                days = int(days)
                total_success = 0
                
                for user in users:
                    accountlist = middleware.bucketGet('dd_pg_user', user)
                    if not accountlist or accountlist == '{}':
                        continue
                        
                    # 获取并去重账号列表
                    accounts = list(dict.fromkeys(eval(accountlist))) if accountlist else []
                    middleware.bucketSet(bucket='dd_pg_user', key=user, value=f'{accounts}')
                    
                    for account in accounts:
                        try:
                            accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
                            token = middleware.bucketGet('dd_pg_token', account)
                            
                            if not token:
                                continue
                                
                            if len(accountVip) == 0:
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                                
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('dd_pg_auth', account, str(new_date))
                            
                            phone = middleware.bucketGet('dd_pg_mobile', key=account)
                            if phone:
                                Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
                            total_success += 1
                        except:
                            continue
                            
                sender.reply(f"""=======修改完成=====
✅ 成功修改: {total_success}个
📅 调整天数: {days}天
====================""")
                
            except ValueError:
                sender.reply("""=======输入错误=====
❌ 请输入有效的天数
====================""")
                return
                
        elif choice == '2':
            sender.reply("""=======单独修改=====
📝 请输入用户ID
💡 通过发送myuid获取
⚠️ 输入q退出操作
====================""")

            myuid = sender.input(60000, 1, False)
            if myuid == 'q' or myuid == 'Q':
                sender.reply("✅ 已退出授权")
                return
            elif myuid == '':
                sender.reply('⏰ 操作超时')
                return
                
            accountlist = middleware.bucketGet('dd_pg_user', myuid)
            if not accountlist or accountlist == '{}':
                sender.reply(f"""=======查询失败=====
❌ 未找到该用户账号信息
====================""")
                return
                
            # 获取并去重账号列表
            accounts = list(dict.fromkeys(eval(accountlist))) if accountlist else []
            middleware.bucketSet(bucket='dd_pg_user', key=myuid, value=f'{accounts}')
            
            msg = """=======账号列表=====
[0] 修改所有账号
------------------\n"""
            
            for i, account in enumerate(accounts, 1):
                accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
                vip_status = accountVip if accountVip else '未授权'
                msg += f"""[{i}] 账号信息:
📱 账号: {account}
⏰ 授权: {vip_status}
------------------\n"""
                
            msg += """💡 回复序号选择账号
⚠️ 输入q退出操作
====================""" 
            sender.reply(msg)
            
            xz = sender.input(60000, 1, False)
            if xz == 'q' or xz == 'Q':
                sender.reply("✅ 已退出授权")
                return
            elif xz == '':
                sender.reply('⏰ 操作超时')
                return
                
            try:
                xz = int(xz)
                if xz == 0 or (1 <= xz <= len(accounts)):
                    sender.reply("""=======时间调整=====
📝 请输入调整天数:
💡 正数增加,负数减少
⚠️ 示例: 30 或 -30
====================""")

                    days = sender.input(60000, 1, False)
                    if days == 'q' or days == 'Q':
                        sender.reply("✅ 已退出授权")
                        return
                    elif days == '':
                        sender.reply('⏰ 操作超时')
                        return
                        
                    try:
                        days = int(days)
                        success_count = 0
                        
                        if xz == 0:
                            # 修改所有账号
                            for account in accounts:
                                try:
                                    accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
                                    token = middleware.bucketGet('dd_pg_token', account)
                                    
                                    if not token:
                                        continue
                                        
                                    if len(accountVip) == 0:
                                        current_date = today_date
                                    else:
                                        current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                                        
                                    new_date = current_date + timedelta(days=days)
                                    middleware.bucketSet('dd_pg_auth', account, str(new_date))
                                    
                                    phone = middleware.bucketGet('dd_pg_mobile', key=account)
                                    if phone:
                                        Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
                                    success_count += 1
                                except:
                                    continue
                                    
                            sender.reply(f"""=======修改完成=====
✅ 成功修改: {success_count}个
📅 调整天数: {days}天
====================""")
                            
                        else:
                            # 修改单个账号
                            account = accounts[xz-1]
                            accountVip = middleware.bucketGet('dd_pg_auth', account) or ''
                            token = middleware.bucketGet('dd_pg_token', account)
                            
                            if not token:
                                sender.reply("""=======修改失败=====
❌ 未找到账号Token信息
====================""")
                                return
                                
                            if len(accountVip) == 0:
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                                
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('dd_pg_auth', account, str(new_date))
                            
                            phone = middleware.bucketGet('dd_pg_mobile', key=account)
                            if phone:
                                Addenvs(osname=dd_pg_osname, value=token, account=account, phone=phone)
                                
                            sender.reply(f"""=======修改成功=====
📱 账号: {account}
📅 调整天数: {days}天
⏰ 新到期时间: {new_date}
====================""")
                            
                    except ValueError:
                        sender.reply("""=======输入错误=====
❌ 请输入有效的天数
====================""")
                        return
                else:
                    sender.reply("""=======输入错误=====
❌ 请输入有效的序号
====================""")
                    return
            except ValueError:
                sender.reply("""=======输入错误=====
❌ 请输入有效的序号
====================""")
            return
        else:
            sender.reply("""=======输入错误=====
❌ 请输入有效的选项
====================""")
            return
    else:
        sender.reply("""=======输入错误=====
❌ 请输入有效的选项
====================""")
    return

def allenvs(osname, account):
    """查询青龙变量"""
    try:
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json"
        }
        if use_daidai:
            response = requests.get(url=f"{QLurl}/api/envs", headers=headers, params={"keyword": str(account), "page_size": 100}).json()
            for env in response.get('data', []):
                if env.get('remarks') and account in env['remarks'] and osname == env.get('name'):
                    return env['id']
        else:
            url = f"{QLurl}/open/envs"
            response = requests.get(url=url, headers=headers).json()
            
            if response['code'] == 200:
                for env in response['data']:
                    if env['remarks'] and account in env['remarks'] and osname == env['name']:
                        return env['id']
        return None
        
    except Exception as e:
        sender.reply(f"""=======查询失败=====
❌ 查询变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def delenvs(id):
    """删除青龙变量"""
    if not id:
        return
        
    try:
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        if use_daidai:
            response = requests.delete(f"{QLurl}/api/envs/{id}", headers=headers)
            if response.status_code != 200:
                sender.reply("❌ 删除呆呆面板变量失败")
        else:
            url = f"{QLurl}/open/envs"
            data = [id]
            response = requests.delete(url, headers=headers, json=data)
            
            if response.status_code != 200:
                sender.reply("""=======删除失败=====
❌ 删除变量失败
------------------
请检查青龙面板状态
====================""")
            
    except Exception as e:
        sender.reply(f"""=======删除错误=====
❌ 删除变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def clean_expired_accounts():
    """清理过期账号"""
    if not sender.isAdmin():
        sender.reply("""=======权限错误=====
⛔ 您没有权限执行此操作
====================""")
        return

    # 获取必要的全局变量
    dd_pg_osname, dd_pg_qlname, _, _, _, _, _, _, _, _, _, _, _ = getusercontent()
    QLurl, qltoken = seekql()

    sender.reply("""=======清理确认=====
⚠️ 即将清理所有过期账号
⚠️ 此操作不可恢复
------------------
[y] 确认清理
[n] 取消操作
====================""")
    
    if not yesornos():
        sender.reply("✅ 已取消清理")
        return

    # 获取所有用户
    users = middleware.bucketAllKeys(bucket='dd_pg_user')
    if not users:
        sender.reply("""=======查询结果=====
ℹ️ 没有找到任何用户
====================""")
        return

    total_accounts = 0
    expired_accounts = 0
    cleaned_accounts = 0
    cleaned_vars = 0

    # 先获取所有青龙变量
    try:
        url = f"{QLurl}/open/envs"
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json"
        }
        response = requests.get(url=url, headers=headers).json()
        if response['code'] != 200:
            sender.reply("""=======查询失败=====
❌ 无法获取青龙变量
------------------
请检查青龙面板状态
====================""")
            return
        all_envs = response['data']
    except Exception as e:
        sender.reply(f"""=======查询错误=====
❌ 获取青龙变量失败
------------------
错误信息: {str(e)}
====================""")
        return

    # 收集需要删除的变量ID
    env_ids_to_delete = []

    for user in users:
        accountlist = middleware.bucketGet('dd_pg_user', user)
        if not accountlist:
            continue

        # 获取并去重账号列表
        accounts = list(dict.fromkeys(eval(accountlist))) if accountlist else []
        valid_accounts = []

        for account in accounts:
            total_accounts += 1
            accountVip = middleware.bucketGet('dd_pg_auth', key=account) or ''
            
            # 检查是否过期
            if len(accountVip) == 0 or accountVip < today_time:
                expired_accounts += 1
                phone = middleware.bucketGet('dd_pg_mobile', key=account)
                
                # 查找并收集该账号的所有青龙变量ID
                for env in all_envs:
                    if env['name'] == dd_pg_osname:
                        # 检查remarks中是否包含账号ID或手机号
                        remarks = env.get('remarks', '')
                        if (account in remarks) or (phone and phone in remarks):
                            env_ids_to_delete.append(env['id'])
                            cleaned_vars += 1
                
                cleaned_accounts += 1
                # 删除账号相关信息
                middleware.bucketDel(bucket='dd_pg_mobile', key=account)
                middleware.bucketDel(bucket='dd_pg_token', key=account)
                middleware.bucketDel(bucket='dd_pg_auth', key=account)
            else:
                valid_accounts.append(account)

        # 更新用户的账号列表
        if valid_accounts:
            middleware.bucketSet(bucket='dd_pg_user', key=user, value=f'{valid_accounts}')
        else:
            middleware.bucketDel(bucket='dd_pg_user', key=user)

    # 批量删除青龙变量
    if env_ids_to_delete:
        try:
            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            response = requests.delete(url, headers=headers, json=env_ids_to_delete)
            if response.status_code != 200:
                sender.reply("""=======删除失败=====
❌ 删除青龙变量失败
------------------
请检查青龙面板状态
====================""")
        except Exception as e:
            sender.reply(f"""=======删除错误=====
❌ 删除青龙变量时出错
------------------
错误信息: {str(e)}
====================""")
            return

    # 发送清理结果
    result_msg = f"""=======清理完成=====
📊 统计信息:
• 总账号数: {total_accounts}
• 过期账号: {expired_accounts}
• 清理账号: {cleaned_accounts}
• 清理变量: {cleaned_vars}
====================""" 
    sender.reply(result_msg)

# 获取配置
dd_pg_osname, dd_pg_qlname, dd_managecommand, dd_querycommand, \
dd_signcommand, randommanagecommand, randomquerycommand, \
randomsigncommand, pgVipmoney, pgcoin, use_daidai, dd_pg_ddname, panel_group = getusercontent()

# 连接青龙
QLurl, qltoken = seekql()

# 获取当前时间
today_date = datetime.now().date()
today_time = str(today_date)

# 获取消息类型和内容
imtype = sender.getImtype()
usermessage = sender.getMessage()

# 主逻辑处理
if '登录' in usermessage or '登陆' in usermessage:
    bind()
elif '管理' in usermessage:
    management()
elif '查询' in usermessage:
    cxs()
elif usermessage.strip() == '胖乖授权':
    try:
        pangguai_auth()
    except Exception as e:
        sender.reply(f"""=======系统错误=====
❌ 执行授权功能时出错
------------------
错误信息: {str(e)}
====================""")
elif usermessage.strip() in ['胖乖清理', '清理胖乖']:
    try:
        clean_expired_accounts()
    except Exception as e:
        sender.reply(f"""=======系统错误=====
❌ 执行清理功能时出错
------------------
错误信息: {str(e)}
====================""")
elif imtype == 'fake':
    # 定时任务
    users = middleware.bucketAllKeys(bucket='dd_pg_user')
    for user in users:
        accountlist = middleware.bucketGet(bucket='dd_pg_user', key=user)
        if not accountlist:
            continue
            
        # 获取并去重账号列表
        accounts = list(dict.fromkeys(eval(accountlist))) if accountlist else []
        middleware.bucketSet(bucket='dd_pg_user', key=user, value=f'{accounts}')
        
        for account in accounts:
            token = middleware.bucketGet(bucket='dd_pg_token', key=account)
            accountVip = middleware.bucketGet(bucket='dd_pg_auth', key=account) or ''
            
            # 检查token有效性
            info = cx(token)
            if not info:
                qlid = allenvs(osname=dd_pg_osname, account=account)
                delenvs(id=qlid)
                
                push(user, account, """=======胖乖定时检测=====
⏰ 定时检测提醒
------------------
❌ Token已失效
💡 请尽快更新账号
====================""")
                continue
                
            # 检查授权状态
            if len(accountVip) == 0 or accountVip <= today_time:
                qlid = allenvs(osname=dd_pg_osname, account=account)
                delenvs(id=qlid)
                push(user, account, """=======胖乖定时检测=====
⏰ 定时检测提醒
------------------
❌ 授权已过期
💡 请及时续费授权
====================""")
            else:
                try:
                    expire_date = datetime.strptime(accountVip, '%Y-%m-%d').date()
                    days_left = (expire_date - datetime.now().date()).days
                    if days_left <= 3:
                        push(user, account, f"""=======胖乖定时检测=====
⏰ 定时检测提醒
------------------
⚠️ 授权即将到期
📅 到期时间: {accountVip}
⏳ 剩余天数: {days_left}天
💡 请及时续费授权
====================""")
                except:
                    pass
else:
    sender.setContinue()
