#[pin:true]
#[public:true]
# [rule: ^唔语管理$]
# [rule: ^管理唔语$]
# [rule: ^唔语查询$]
# [rule: ^查询唔语$]
# [rule: ^唔语登录$]
# [rule: ^登录唔语$]
# [rule: ^登陆唔语$]
# [rule: ^唔语登陆$]
# [rule: ^唔语授权$]
# [rule: ^唔语清理$]
# [rule: ^清理唔语$]
# [cron: 18 8,12,16 * * *]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [version: V2.3]
# [admin: false]
# [author: 97610325]
# [price: 28.80]
# [title: 唔语听书]
# [icon: https://nos.netease.com/ysf/d4f8b7f99ae2b9ffb33ebfdedcf0776c.jpg]
# [description: 唔语听书插件<br>指令：唔语登录、唔语管理、唔语查询、唔语清理<br>功能：自动领红花、每日抽奖、自动看广告，完美对接青龙面板,适配呆呆系统系统]
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
def normalize_token(token):
    """标准化Token,自动处理Bearer前缀
    
    Args:
        token: 原始Token字符串,可能包含Bearer前缀
        
    Returns:
        str: 标准化后的Token(不包含Bearer前缀)
    """
    if not token:
        return ''
    
    # 去除首尾空格
    token = str(token).strip()
    
    # 检查是否包含Bearer前缀(不区分大小写)
    if token.lower().startswith('bearer '):
        # 移除Bearer前缀,只保留token
        token = token[7:]
    
    return token
# [param: {"required":true,"key":"dd_wuyu_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_wuyu_config.Qinglong","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割，这个符号是中文的竖(直接复制)"}]
# [param: {"required":true,"key":"dd_wuyu_config.osname","bool":false,"placeholder":"必填项,例:WuyuToken","name":"青龙变量名","desc":"青龙容器内唔语听书的变量名"}]
# [param: {"required":true,"key":"dd_wuyu_config.WuyuVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_wuyu_config.Wuyucoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_wuyu_config.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_wuyu_user', key=userid)
def getusercontent():
    """获取插件配置信息"""
    dd_wuyu_osname = middleware.bucketGet('dd_wuyu_config', 'osname') or 'WuyuToken'
    dd_wuyu_qlname = middleware.bucketGet('dd_wuyu_config', 'Qinglong')
    dd_managecommand = middleware.bucketGet('dd_wuyu_config', 'dd_managecommand') or '唔语管理'
    dd_querycommand = middleware.bucketGet('dd_wuyu_config', 'dd_querycommand') or '唔语查询'
    dd_signcommand = middleware.bucketGet('dd_wuyu_config', 'dd_signcommand') or '唔语登录'
    
    # 生成随机指令
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    # 获取价格配置
    WuyuVipmoney = Decimal(middleware.bucketGet('dd_wuyu_config', 'WuyuVipmoney') or '0')
    Wuyucoin = int(middleware.bucketGet('dd_wuyu_config', 'Wuyucoin') or '0')
    
    return (dd_wuyu_osname, dd_wuyu_qlname, dd_managecommand, dd_querycommand,
            dd_signcommand, randommanagecommand, randomquerycommand,
            randomsigncommand, WuyuVipmoney, Wuyucoin)
def seekql():
    """连接并验证青龙配置"""
    try:
        if len(dd_wuyu_qlname) == 0:
            sender.reply("""=======配置错误=======
❌ 未配置青龙信息
------------------
请在插件配置中填写:
Host丨ClientID丨ClientSecret
• 使用中文丨分隔
• 示例:
http://ql.example.com丨abcd丨1234
====================""")
            exit(0)
            
        qllist = dd_wuyu_qlname.split('丨')
        if len(qllist) != 3:
            sender.reply(f"""=======格式错误=======
❌ 青龙配置格式错误
------------------
当前格式: {dd_wuyu_qlname}
正确格式:
Host丨ClientID丨ClientSecret
====================""")
            exit(0)
            
        QLurl = qllist[0].strip()
        ClientID = qllist[1].strip()
        ClientSecret = qllist[2].strip()
        
        # 验证每个参数是否为空
        if not all([QLurl, ClientID, ClientSecret]):
            sender.reply("""=======参数错误=======
❌ 青龙配置参数不完整
------------------
请确保以下参数都已填写:
• 青龙面板地址(Host)
• 应用ID(ClientID)
• 应用密钥(ClientSecret)
====================""")
            exit(0)
            
        # 验证URL格式
        if not QLurl.startswith(('http://', 'https://')):
            sender.reply(f"""=======地址错误=======
❌ 青龙地址格式错误
------------------
当前地址: {QLurl}
正确格式:
• http://qinglong.example.com
• https://ql.example.com:5700
====================""")
            exit(0)
            
        try:
            qltoken = QLtoken(QLurl=QLurl, ClientID=ClientID, ClientSecret=ClientSecret)
            return QLurl, qltoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")
            
    except Exception as e:
        sender.reply(f"""=======网络错误=======
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
====================""")
        exit(0)
def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        
        if response.status_code != 200:
            sender.reply(f"""=======请求失败=======
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
            sender.reply("""=======认证失败=======
❌ 获取Token失败
------------------
请检查:
• ClientID是否正确
• ClientSecret是否正确
• 应用是否有权限
====================""")
            exit(0)
            
    except requests.exceptions.RequestException as e:
        sender.reply(f"""=======网络错误=======
❌ 连接青龙面板失败
------------------
请检查:
• 青龙地址是否正确
• 网络是否正常
• 错误信息: {str(e)}
====================""")
        exit(0)
    except Exception as e:
        sender.reply(f"""=======系统错误=======
❌ 处理请求时出错
------------------
请检查:
• 配置格式是否正确
• 错误信息: {str(e)}
====================""")
        exit(0)
def QLzt(osname, value, account, username):
    """添加青龙变量"""
    try:
        qlurl = f"{QLurl}/open/envs"
        accountVip = middleware.bucketGet(bucket='dd_wuyu_auth', key=account)
        data = [{
            "value": value,
            "name": osname,
            "remarks": f'唔语:{username}丨用户:{userid}丨账号:{account}丨授权时间:{accountVip}丨唔语管理'
        }]
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        r = requests.post(qlurl, headers=headers, data=json.dumps(data))
        r_json = r.json()
        if "value must be unique" in r.text:
            return
        else:
            qlid = r_json['data'][0]['id']
            return
    except Exception as e:
        sender.reply(f"""=======添加失败=======
❌ 添加青龙变量失败
------------------
请检查:
• 青龙面板状态
• 变量格式是否正确
• 错误信息: {str(e)}
====================""")
        exit(0)
def QLupdate(osname, value, account, qlid, username):
    """更新青龙变量"""
    try:
        qlurl = f"{QLurl}/open/envs"
        accountVip = middleware.bucketGet(bucket='dd_wuyu_auth', key=account)
        data = {
            "value": value,
            "name": osname,
            "remarks": f'唔语:{username}丨用户:{userid}丨账号:{account}丨授权时间:{accountVip}丨唔语管理',
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
            return data['id'], data['createdAt']
        else:
            sender.reply("""=======更新失败=======
❌ 更新青龙变量失败
------------------
请联系管理员处理
====================""")
            exit(0)
    except Exception as e:
        sender.reply(f"""=======更新错误=======
❌ 更新变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)
def Addenvs(osname, value, account, username):
    """添加或更新青龙变量"""
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json"
    }
    try:
        response = requests.get(url=url, headers=headers).json()
        qlid = None
        username_qlid = None
        
        if response['code'] == 200:
            envslist = response['data']
            for envs in envslist:
                remarks = envs.get('remarks')
                envname = envs.get('name')
                if not remarks or envname != osname:
                    continue
                    
                # 检查是否存在相同账号的变量
                if account in remarks:
                    qlid = envs['id']
                    break
                    
                # 检查是否存在相同用户名的变量
                if '唔语:' in remarks:
                    try:
                        remark_username = remarks.split('唔语:')[1].split('丨')[0]
                        if remark_username == username:
                            username_qlid = envs['id']
                    except:
                        continue
                    
            # 如果找到了相同用户名的变量但没有找到相同账号的变量
            if not qlid and username_qlid:
                qlid = username_qlid
        else:
            sender.reply("""=======连接失败=======
❌ 连接青龙获取变量失败
====================""")
            exit(0)
            
        value = urllib.parse.quote(value)
        if qlid:
            # 更新现有变量
            QLupdate(osname, value, account, qlid, username)
        else:
            # 创建新变量
            QLzt(osname, value, account, username)
    except Exception as e:
        sender.reply(f"""=======操作失败=======
❌ 处理变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)
def get_user_detail(token):
    """获取用户详细信息"""
    try:
        # 标准化token(自动处理Bearer前缀)
        token = normalize_token(token)
        
        url = "https://xcx.myinyun.com:4438/napi/wx/getUserDetail"
        headers = {
            'Host': 'xcx.myinyun.com:4438',
            'Connection': 'keep-alive',
            'content-type': 'application/json',
            'Accept-Encoding': 'gzip,compress,br,deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 26_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.70(0x18004624) NetType/WIFI Language/zh_CN',
            'Referer': 'https://servicewechat.com/wxa25139b08fe6e2b6/23/page-frame.html',
            'authorization': f'Bearer {token}'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        return response.json()
        
    except Exception as e:
        return None
def check_token_valid(token):
    """检查token是否有效"""
    try:
        user_info = get_user_detail(token)
        if user_info and 'username' in user_info:
            return True, user_info.get('username', '未知')
        return False, 'Token失效'
    except:
        return False, 'Token失效'
def bind():
    """绑定账号"""
    def accvip(Newaddition):
        status = '添加' if Newaddition else '更新'
        auth_status = '✅ 已授权' if accountVip >= today_time else '⚠️ 未授权'
        next_step = f'发送 {randommanagecommand} 可管理账号' if accountVip >= today_time else f'发送 {randommanagecommand} 可进行授权'
        
        success_msg = f"""=======绑定成功=======
📱 用户名: {username}
🔐 状态: {auth_status}
⏰ 操作: {next_step}
====================""" 
        if len(accountVip) != 0 and accountVip >= today_time:
            # 标准化token后再保存到青龙
            normalized_token = normalize_token(token)
            Addenvs(osname=dd_wuyu_osname, value=normalized_token, account=account, username=username)
        
        # 更新账号列表，确保不重复
        if account not in accounts:
            accounts.append(account)
            # 去重并保持顺序
            unique_accounts = list(dict.fromkeys(accounts))
            middleware.bucketSet(bucket='dd_wuyu_user', key=userid, value=f'{unique_accounts}')
            
        sender.reply(success_msg)
    sender.reply("""=======唔语登录=======
请输入您的Token:
------------------
⚠️ 建议私聊登录,账号安全
⭐ 支持带Bearer或不带Bearer的Token
⭐ 输入q退出操作
====================""")
    input_token = sender.input(120000, 1, False)
    
    if input_token.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)
        
    # 验证token有效性(自动处理Bearer前缀)
    is_valid, username_or_error = check_token_valid(input_token)
    if not is_valid:
        sender.reply(f"""=======登录失败=======
❌ {username_or_error}
====================""")
        exit(0)
    
    # 标准化token后保存
    token = normalize_token(input_token)
    username = username_or_error
    account = str(int(time.time() * 1000))  # 生成唯一账号ID
    
    # 检查该Token是否已经存在绑定账号
    existing_account = None
    old_auth = None
    accounts = []
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        for acc in accounts:
            acc_token = middleware.bucketGet(bucket='dd_wuyu_token', key=acc)
            # 标准化后比较
            if normalize_token(acc_token) == token:
                existing_account = acc
                # 保存旧账号的授权信息
                old_auth = middleware.bucketGet(bucket='dd_wuyu_auth', key=acc)
                # 从账号列表中移除旧账号
                accounts.remove(acc)
                # 删除旧账号的其他信息
                middleware.bucketDel(bucket='dd_wuyu_username', key=acc)
                middleware.bucketDel(bucket='dd_wuyu_token', key=acc)
                # 删除旧账号的青龙变量
                qlid = allenvs(osname=dd_wuyu_osname, account=acc)
                if qlid:
                    delenvs(id=qlid)
                break
    
    # 保存新账号信息
    middleware.bucketSet(bucket='dd_wuyu_username', key=account, value=username)
    middleware.bucketSet(bucket='dd_wuyu_token', key=account, value=token)
    
    # 如果有旧授权，转移到新账号
    if old_auth:
        middleware.bucketSet(bucket='dd_wuyu_auth', key=account, value=old_auth)
        # 如果授权未过期，更新青龙变量
        if old_auth >= today_time:
            Addenvs(osname=dd_wuyu_osname, value=token, account=account, username=username)
        
    # 新账号绑定
    if len(uservalue) == 0:
        accounts = []
        
    accountVip = middleware.bucketGet(bucket='dd_wuyu_auth', key=account)
    accvip(True)  # 添加新账号
def ValueErrors(value, count):
    """验证输入值是否为有效的整数且在合理范围内"""
    try:
        value = int(value)
        if value > count or value == 0:
            sender.reply(f"""=======输入无效=======
❌ 请输入 1-{count} 之间的数字
====================""")
            exit(0)
        return value
    except ValueError:
        sender.reply("""=======输入无效=======
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
def allenvs(osname, account):
    """获取青龙环境变量"""
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": f"Bearer {qltoken}",
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url=url, headers=headers).json()
        qlid = None
        for envs in response['data']:
            if (envs.get('name') == osname and 
                envs.get('remarks') and 
                str(account) in envs['remarks']):
                qlid = envs['id']
                break
        return qlid
    except:
        return None
def delenvs(id):
    """删除青龙环境变量"""
    if id is None:
        return
        
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": f"Bearer {qltoken}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = [id]
    
    try:
        response = requests.delete(url, headers=headers, json=data)
        if response.status_code != 200:
            return
        result = response.json()
        if result.get('code') != 200:
            return
    except:
        return
def management():
    """账号管理功能"""
    if len(uservalue) == 0:
        sender.reply(f"""=======未绑定账号=======
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
====================""")
        return
    count = 1
    account_list = """
======我的唔语听书账号======""" 
    
    # 获取并去重账号列表
    accounts = list(dict.fromkeys(eval(uservalue))) if uservalue else []
    middleware.bucketSet(bucket='dd_wuyu_user', key=userid, value=f'{accounts}')
    for account in accounts:
        accountVip = middleware.bucketGet(bucket='dd_wuyu_auth', key=f'{account}')
        if len(accountVip) == 0:
            vip_status = '⚠️ 未授权'
        elif accountVip < today_time:
            vip_status = '❌ 已过期'
        else:
            vip_status = f'✅ {accountVip}'
        
        # 获取用户名并进行隐私处理
        username = middleware.bucketGet(bucket='dd_wuyu_username', key=account)
        if username:
            display_username = username[:3] + '*' * 4 + username[7:] if len(username) > 7 else username[:2] + '***'
        else:
            display_username = account[:3] + "****" + account[7:]
            
        account_list += f"""
------------------
[{count}] 账号信息
📱 用户名: {display_username}
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
        if me_as_int > count - 1:
            sender.reply('❌ 输入的序号无效')
            exit(0)
    except ValueError:
        sender.reply('❌ 输入必须是数字')
        exit(0)
            
    account = accounts[me_as_int - 1]
    token = middleware.bucketGet(bucket='dd_wuyu_token', key=f'{account}')
    accountVip = middleware.bucketGet(bucket='dd_wuyu_auth', key=f'{account}')
    username = middleware.bucketGet(bucket='dd_wuyu_username', key=f'{account}')
        
    if len(accountVip) == 0:
        vip_status = '⚠️ 未授权'
    elif accountVip < today_time:
        vip_status = '❌ 已过期'
    else:
        vip_status = f'✅ {accountVip}'
            
    account_info = f"""
=======账号详情======
📱 用户名: {username}
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
        confirm_msg = """=======删除警告=======
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
            qlid = allenvs(osname=dd_wuyu_osname, account=str(account))
            delenvs(id=qlid)
            if len(accounts) == 0:
                middleware.bucketDel(bucket='dd_wuyu_user', key=userid)
            else:
                middleware.bucketSet(bucket='dd_wuyu_user', key=userid, value=f'{accounts}')
            sender.reply('✅ 账号删除成功!')
        else:
            sender.reply('✅ 已取消删除')
            exit(0)
            
    elif inputmessage == '1':
        auth_guide = """=======授权设置=======
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
        money = Decimal(mes) * Decimal(WuyuVipmoney)
        
        zf(project='唔语授权', me_as_int=mes, accountVip=accountVip, token=token,
           username=username, account=account)
           
        accountVip = empower(empowertime=accountVip, me_as_int=mes)
        middleware.bucketSet(bucket='dd_wuyu_auth', key=account, value=accountVip)
        Addenvs(osname=dd_wuyu_osname, value=token, account=account, username=username)
        
        result_msg = f"""=======订单完成=======
🎈 名称: 唔语授权
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
def zf(project, me_as_int, accountVip, token, username, account):
    """支付处理"""
    try:
        zsm = middleware.bucketGet('dd_wuyu_config', 'zsm')
        use_ma_pay = middleware.bucketGet('dd_wuyu_config', 'use_ma_pay') == 'true'
        
        if not zsm and not use_ma_pay:
            sender.reply('❌ 未配置收款方式,请联系管理员!')
            exit(0)
            
        # 检查是否允许使用积分支付
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(Wuyucoin) * me_as_int
        
        # 动态构建支付选项，保证序号连续
        pay_options = []
        
        # 添加微信支付选项
        if zsm:
            money = Decimal(me_as_int) * Decimal(WuyuVipmoney)
            pay_options.append({
                'type': 'wechat',
                'name': '微信支付',
                'money': money,
                'zfcoin': 0
            })
            
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
                money = Decimal(me_as_int) * Decimal(WuyuVipmoney)
                pay_options.append({
                    'type': 'mapay',
                    'name': '码支付',
                    'money': money,
                    'zfcoin': 0,
                    'config': ma_pay_config
                })
            
        # 只有当Wuyucoin > 0时才显示积分支付选项
        if Wuyucoin and int(Wuyucoin) > 0:
            pay_options.append({
                'type': 'coin',
                'name': '积分支付',
                'money': 0,
                'zfcoin': zfcoin
            })
            
        # 构建动态的支付菜单
        pay_menu = """=====选择支付方式===="""
        for idx, option in enumerate(pay_options, 1):
            if option['type'] == 'wechat':
                pay_menu += f"""
{idx}️⃣ 微信支付
   💰 {option['money']}元/{me_as_int}月"""
            elif option['type'] == 'mapay':
                pay_menu += f"""
{idx}️⃣ 码支付
   💰 {option['money']}元/{me_as_int}月"""
            elif option['type'] == 'coin':
                pay_menu += f"""
{idx}️⃣ 积分支付  
   🎯 {option['zfcoin']}积分/{me_as_int}月
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
            
        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(pay_options):
                sender.reply("❌ 输入无效")
                exit(0)
            selected = pay_options[choice_idx]
        except ValueError:
            sender.reply("❌ 输入无效")
            exit(0)
            
        # 根据选择的选项执行对应的支付流程
        if selected['type'] == 'wechat':
            # 微信支付流程
            zfzt = sender.atWaitPay()
            if zfzt:
                sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
                exit(0)
                
            money = selected['money']
            
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
                
        elif selected['type'] == 'mapay':
            # 码支付流程
            ma_pay_config = selected['config']
            money = selected['money']
            
            # 生成订单号
            out_trade_no = f"WY{int(time.time())}{userid}"
            
            # 构造支付参数
            params = {
                'pid': ma_pay_config['pid'],
                'type': ma_pay_config['type'].split(',')[0],  # 默认使用第一个支付方式
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-唔语授权-{str(money)}",
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
                
        elif selected['type'] == 'coin':
            # 积分支付流程
            if int(usercoin) < selected['zfcoin']:
                sender.reply(f"""=====积分不足=====
👤 当前积分: {usercoin}
📍 需要积分: {selected['zfcoin']}
==================""")
                exit(0)
                
            confirm_msg = f"""=====积分支付确认=====
💫 消耗积分: {selected['zfcoin']}
⏰ 授权时长: {me_as_int}月
------------------
确认请回复【y】
取消请回复【n】
=================="""
            sender.reply(confirm_msg)
            
            if yesornos():
                try:
                    new_balance = int(usercoin) - selected['zfcoin']
                    middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                    return True
                except Exception as e:
                    sender.reply(f"❌ 积分支付处理失败: {str(e)}")
                    exit(0)
            else:
                sender.reply("✅ 已取消支付")
                exit(0)
            
    except Exception as e:
        sender.reply(f"❌ 支付处理发生错误: {str(e)}")
        exit(0)
def cxs():
    """查询所有账号"""
    if len(uservalue) == 0:
        sender.reply(f"""=======未绑定账号=======
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
====================""")
        return
    # 获取并去重账号列表
    accounts = list(dict.fromkeys(eval(uservalue))) if uservalue else []
    middleware.bucketSet(bucket='dd_wuyu_user', key=userid, value=f'{accounts}')
    for account in accounts:
        token = middleware.bucketGet(bucket='dd_wuyu_token', key=account)
        accountVip = middleware.bucketGet(bucket='dd_wuyu_auth', key=account)
        username = middleware.bucketGet(bucket='dd_wuyu_username', key=account)
        
        if len(accountVip) == 0 or accountVip < today_time:
            sender.reply(f"""=======授权过期=======
📱 账号: {username}
⚠️ 状态: 授权已过期
====================""")
            continue
            
        # 标准化token后调用API
        info = get_user_detail(normalize_token(token))
        if not info:
            sender.reply(f"""=======查询异常=======
📱 账号: {username}
❌ 状态: 查询失败
====================""")
            continue
            
        account_info = f"""=======账号详情=======
📱 用户名: {info.get('username', '未知')}
🌹 红花数量: {info.get('flowerCount', 0)}
📺 广告次数: {info.get('adCount', 0)}
⏱️ 总收听时长: {info.get('totalListenTime', 0)}秒
🔐 授权至: {accountVip}
===================="""
        sender.reply(account_info)
def wuyu_auth():
    """唔语授权管理功能"""
    if not sender.isAdmin():
        sender.reply("""=======权限错误=======
⛔ 您没有权限执行此操作
====================""")
        return
        
    # 获取必要的全局变量
    dd_wuyu_osname, dd_wuyu_qlname, _, _, _, _, _, _, _, _ = getusercontent()
    QLurl, qltoken = seekql()
    
    sender.reply("""=====唔语授权=====
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
        users = middleware.bucketAllKeys('dd_wuyu_user')
        if not users:
            sender.reply("""=======查询失败=======
❌ 未找到任何绑定账号
====================""")
            return
            
        sender.reply('请输入要给所有用户授权的月数！\n退出【q】！')
        sjts = sender.input(60000, 1, False)
        if sjts.lower() == 'q':
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
            accountlist = middleware.bucketGet('dd_wuyu_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            accounts = eval(accountlist)
            for account in accounts:
                try:
                    accountVip = middleware.bucketGet('dd_wuyu_auth', account)
                    token = middleware.bucketGet('dd_wuyu_token', account)
                    username = middleware.bucketGet('dd_wuyu_username', account)
                    
                    if not token:
                        fail_count += 1
                        continue
                        
                    accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                    middleware.bucketSet('dd_wuyu_auth', account, accountVip)
                    
                    # 更新青龙变量
                    Addenvs(osname=dd_wuyu_osname, value=token, account=account, username=username)
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
        if myuid.lower() == 'q':
            sender.reply("退出！")
            return
        elif myuid == '':
            sender.reply(f'超时退出！')
            return
            
        accountlist = middleware.bucketGet('dd_wuyu_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"未找到{myuid}的唔语听书账号信息!")
            return
            
        accounts = eval(accountlist)
        n = 0
        msg = '========唔语授权========\n'
        msg += '0、授权所有账号\n======================\n'
        
        for account in accounts:
            n += 1
            accountVip = middleware.bucketGet('dd_wuyu_auth', account)
            if len(accountVip) == 0:
                accountVip = '未授权'
            msg += f'{n}、账号:{account}\n授权时间: {accountVip}\n======================\n'
            
        msg += f'回复序号选择账号,退出【q】！'
        sender.reply(msg)
        xz = sender.input(60000, 1, False)
        
        if xz.lower() == 'q':
            sender.reply("退出！")
            return
        elif xz == '':
            sender.reply(f'超时退出！')
            return
            
        if xz == '0':
            # 修改该用户的所有账号
            sender.reply('请输入要调整的天数:\n正数增加天数,负数减少天数\n例如: 100 或 -100')
            days = sender.input(60000, 1, False)
            
            if days.lower() == 'q':
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
                        accountVip = middleware.bucketGet('dd_wuyu_auth', account)
                        token = middleware.bucketGet('dd_wuyu_token', account)
                        username = middleware.bucketGet('dd_wuyu_username', account)
                        
                        if not token:
                            continue
                            
                        if len(accountVip) == 0 or accountVip == '未授权':
                            current_date = today_date
                        else:
                            current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                            
                        new_date = current_date + timedelta(days=days)
                        middleware.bucketSet('dd_wuyu_auth', account, str(new_date))
                        
                        Addenvs(osname=dd_wuyu_osname, value=token, account=account, username=username)
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
            
            if days.lower() == 'q':
                sender.reply("退出！")
                return
            elif days == '':
                sender.reply(f'超时退出！')
                return
                
            try:
                days = int(days)
                accountVip = middleware.bucketGet('dd_wuyu_auth', account)
                token = middleware.bucketGet('dd_wuyu_token', account)
                username = middleware.bucketGet('dd_wuyu_username', account)
                
                if not token:
                    sender.reply("未找到账号token信息!")
                    return
                    
                if len(accountVip) == 0 or accountVip == '未授权':
                    current_date = today_date
                else:
                    current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                    
                new_date = current_date + timedelta(days=days)
                middleware.bucketSet('dd_wuyu_auth', account, str(new_date))
                
                Addenvs(osname=dd_wuyu_osname, value=token, account=account, username=username)
                
                msg = f'修改成功!\n账号: {account}\n调整天数: {days}天\n新到期时间: {new_date}'
                sender.reply(msg)
                
            except ValueError:
                sender.reply('输入的天数无效!')
                return
        else:
            sender.reply('输入的序号无效!')
            return
    elif xz == '3':
        # 修改授权时间（功能与序号2类似，简化处理）
        sender.reply('⚠️ 请使用序号2的单独授权功能')
        return
    else:
        sender.reply('输入的选项无效!')
        return
def clean_expired_accounts():
    """清理过期的唔语听书账号"""
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        exit(0)
        
    users = middleware.bucketAllKeys(bucket='dd_wuyu_user')
    sender.reply(
        "=====清理统计=====\n"
        f"📊 找到用户数: {len(users) if users else 0}\n"
        "==================="
    )
    
    if not users:
        sender.reply("❌ 没有找到任何绑定的唔语听书账号")
        exit(0)
        
    cleaned_count = 0
    ql_cleaned = 0
    ql_failed = 0
    
    for user in users:
        accountlist = middleware.bucketGet(bucket='dd_wuyu_user', key=user)
        if not accountlist:
            continue
            
        accounts = eval(accountlist)
        valid_accounts = []
        
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='dd_wuyu_auth', key=account)
            
            if len(accountVip) == 0 or accountVip <= today_time:
                # 删除青龙面板中的变量
                try:
                    qlid = allenvs(osname=dd_wuyu_osname, account=account)
                    if qlid:
                        delenvs(id=qlid)
                        ql_cleaned += 1
                    else:
                        ql_failed += 1
                except:
                    ql_failed += 1
                    
                # 删除账号相关的存储
                middleware.bucketDel(bucket='dd_wuyu_token', key=account)
                middleware.bucketDel(bucket='dd_wuyu_auth', key=account)
                middleware.bucketDel(bucket='dd_wuyu_username', key=account)
                cleaned_count += 1
            else:
                valid_accounts.append(account)
        
        # 更新或删除用户的账号绑定信息
        if valid_accounts:
            middleware.bucketSet(bucket='dd_wuyu_user', key=user, value=str(valid_accounts))
        else:
            middleware.bucketDel(bucket='dd_wuyu_user', key=user)
    
    sender.reply(
        "=====清理完成=====\n"
        f"🧹 清理插件账号: {cleaned_count}个\n"
        f"🔧 清理青龙变量: {ql_cleaned}个\n"
        f"❌ 青龙变量失败: {ql_failed}个\n"
        "==================="
    )
# 初始化全局变量
today_date = datetime.now().date()
today_time = str(today_date)
dd_wuyu_osname, dd_wuyu_qlname, dd_managecommand, dd_querycommand, dd_signcommand, randommanagecommand, randomquerycommand, randomsigncommand, WuyuVipmoney, Wuyucoin = getusercontent()
QLurl, qltoken = seekql()
usermessage = sender.getMessage()
imtype = sender.getImtype()
if '登录' in usermessage or '登陆' in usermessage:
    bind()
elif '管理' in usermessage:
    management()
elif '查询' in usermessage:
    cxs()
elif '唔语授权' in usermessage:
    wuyu_auth()
elif '清理唔语' in usermessage or '唔语清理' in usermessage:
    clean_expired_accounts()
elif imtype == 'fake':
    """定时任务处理"""
    users = middleware.bucketAllKeys(bucket='dd_wuyu_user')
    if not users:
        exit(0)
        
    for user in users:
        try:
            uservalue = middleware.bucketGet(bucket='dd_wuyu_user', key=user)
            if not uservalue:
                continue
                
            accounts = eval(uservalue)
            for account in accounts:
                try:
                    token = middleware.bucketGet(bucket='dd_wuyu_token', key=account)
                    accountVip = middleware.bucketGet('dd_wuyu_auth', key=account)
                    username = middleware.bucketGet(bucket='dd_wuyu_username', key=account)
                    
                    if not token:
                        continue
                        
                    # 检查授权状态
                    if len(accountVip) == 0 or accountVip < today_time:
                        print(f"账号 {account} 授权已过期")
                        continue
                        
                    # 检查token有效性
                    is_valid, _ = check_token_valid(token)
                    if not is_valid:
                        print(f"账号 {account} token已失效")
                        continue
                        
                    # 同步最新的用户信息
                    info = get_user_detail(token)
                    if info:
                        # 更新用户名
                        if info.get('username') != username:
                            middleware.bucketSet(bucket='dd_wuyu_username', key=account, value=info.get('username'))
                            
                    print(f"账号 {account} ({username}) 运行正常")
                        
                except Exception as e:
                    print(f"处理账号 {account} 时出错: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue