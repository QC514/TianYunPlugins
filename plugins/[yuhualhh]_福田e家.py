#[disable:true]
# [title: 福田e家]
# [language: python]
# [rule: ^(福田)(登录|查询|管理|清理|授权|抢购)$]
# [pin:false]
# [priority: 9999999999999999999]
# [platform: qq,qb,wx,gw,sb,wb,tg,tb,qx,xy,ip]
# [open_source: false]
# [public:false]
# [admin: true]
# [version: 1.0]
# [price: 6666.66]
# [author: yuhualhh]
# [cron: 30 6,18 * * *]
# [icon: https://gcore.jsdelivr.net/gh/lhz03/img@d2cd89d42453045c1e79c4aca6f6dc130c1001df/2025/12/24/ac404fbc14f217ac74f1b3f857a16120.png]
# [description: <br>福田e家插件，支持登录、查询、管理、授权、检测授权过期以及CK失效推送等功能]

import re
import middleware
import requests
import json
from datetime import datetime, timedelta
from decimal import Decimal
import base64
import hashlib
import time

# [param: {"required":true,"key":"yuhua_ftej_config.zsm","bool":false,"placeholder":"","name":"收款码子","desc":"微信Bot收款码直链"}]
# [param: {"required":true,"key":"yuhua_ftej_config.Qinglong","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"对接容器","desc":"各参数之间用中文符用丨分割，例如: http://127.0.01:5700/丨abcdef-ghijk丨abcdefghijklmnopqrs_tuvw"}]
# [param: {"required":true,"key":"yuhua_ftej_config.osname","bool":false,"placeholder":"必填项,例:FTEJ","name":"环境变量","desc":"定义提交至容器的变量名称"}]
# [param: {"required":true,"key":"yuhua_ftej_config.FukudaVipmoney","bool":false,"placeholder":"","name":"收费价格","desc":"不填默认0元，单位: 元/月"}]

senderID = middleware.getSenderID()  # 创建发送者
sender = middleware.Sender(senderID)  # 向用户发送消息
userid = sender.getUserID()  # 消息接收者
uservalue = middleware.bucketGet(bucket='yuhua_ftej_user', key=userid)  # 获取用户的值

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        if response.status_code != 200:
            sender.reply(f"""
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
==================""")
        exit(0)

def PluginsData():
    """获取插件配置数据"""
    Qinglong = middleware.bucketGet(bucket='yuhua_ftej_config', key='Qinglong')
    FukudaVipmoney = middleware.bucketGet(bucket='yuhua_ftej_config', key='FukudaVipmoney')
    osname = middleware.bucketGet(bucket='yuhua_ftej_config', key='osname')
    if len(Qinglong) == 0:
        sender.reply("""
==================
    配置错误
==================
❌ 未配置青龙信息
------------------
请在插件配置中填写:
Host丨ClientID丨ClientSecret
• 使用中文丨分隔
• 示例:
http://ql.example.com丨abcd丨1234
==================""")
        exit(0)
    qllist = Qinglong.split('丨')
    if len(qllist) != 3:
        sender.reply(f"""
==================
    格式错误
==================
❌ 青龙配置格式错误
------------------
当前格式: {Qinglong}
正确格式:
Host丨ClientID丨ClientSecret
==================""")
        exit(0)
    QLurl = qllist[0].strip()
    ClientID = qllist[1].strip()
    ClientSecret = qllist[2].strip()
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
    if not QLurl.startswith(('http://', 'https://')):
        sender.reply(f"""
==================
    地址错误
==================
❌ 青龙地址格式错误
------------------
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
青龙变量名
==================""")
        exit(0)
    FukudaVipmoney = Decimal(FukudaVipmoney or '0')
    return QLurl, ClientID, ClientSecret, FukudaVipmoney, osname

def allenvs(osname, account):
    """获取青龙环境变量"""
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": f"Bearer {qltoken}",
        "accept": "application/json"
    }
    try:
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
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 200:
            return "网络请求失败", "登录失败", False
        result = response.json()
        if 'data' not in result:
            return result.get('msg', "登录失败"), "登录失败", False
        memberID = result['data']['memberID']
        account = result['data']['uid']
        session_data = {
            'memberID': memberID,
            'uid': str(account),
            'timestamp': time.time()
        }
        middleware.bucketSet('yuhua_ftej_api_session', name, json.dumps(session_data))

        return str(account), memberID, f'{name}#{password}'
    except Exception as e:
        return f"登录异常: {str(e)}", "登录异常", False

def get_valid_session(mobile, password, force_refresh=False):
    """
    获取有效的Session信息(核心优化函数)
    优先从缓存获取，如果强制刷新或缓存不存在，则静默登录获取
    """
    if not force_refresh:
        try:
            cached_str = middleware.bucketGet('yuhua_ftej_api_session', mobile)
            if cached_str:
                cached_data = json.loads(cached_str)
                return cached_data.get('memberID')
        except:
            pass
            
    _, memberID, token_status = login(mobile, password)
    
    if token_status is False:
        return None
        
    return memberID

def Addenvs(osname, value, account, phone, owner_id): 
    """添加或更新青龙变量"""
    phone = phone[:3] + '*' * 4 + phone[7:]
    qlid = allenvs(osname, account)
    if qlid is None:
        QLzt(osname, value, account, phone, owner_id)
    else:
        QLupdate(osname, value, account, qlid, phone, owner_id)

def QLzt(osname, value, account, phone, owner_id): 
    """添加青龙变量"""
    try:
        url = f"{QLurl}/open/envs"
        data = [{
            "value": value,
            "name": osname,
            "remarks": f'福田:{account}丨用户:{owner_id}丨手机:{phone}丨福田管理'
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

def QLupdate(osname, value, account, qlid, phone, owner_id): 
    """更新青龙变量"""
    try:
        url = f"{QLurl}/open/envs"
        data = {
            "value": value,
            "name": osname,
            "remarks": f'福田:{account}丨用户:{owner_id}丨手机:{phone}丨福田管理',
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
        auth_status = "✅ 已授权" if accountVip >= today_time else "⚠️ 未授权"
        next_step = "福田管理" if accountVip >= today_time else "福田管理"
        msg = f"""
=====账号{status}成功=====
📱 账号: {mobile}
🔐 授权状态: {auth_status}
------------------
💡 发送"{next_step}"进行授权
=================="""
        if len(accountVip) != 0 and accountVip >= today_time:
            Addenvs(osname=osname, value=token, account=account, phone=mobile, owner_id=userid)
        if Newaddition:
            accounts.append(account)
        sender.reply(msg)
        middleware.bucketSet(bucket='yuhua_ftej_user', key=userid, value=f'{accounts}')
        middleware.bucketSet(bucket='yuhua_ftej_token', key=account, value=token)
        middleware.bucketSet(bucket='yuhua_ftej_auth', key=account, value=accountVip)
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
    accountVip = middleware.bucketGet(bucket='yuhua_ftej_auth', key=account)
    if len(uservalue) == 0:
        accounts = []
        accvip(True)
    else:
        accounts = eval(uservalue)
        accvip(False if account in accounts else True)

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
    zsm = middleware.bucketGet(bucket='yuhua_ftej_config', key='zsm')
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        message = '0、一键授权所有账号\n==================\n'
        for account_in_display_loop in accounts: 
            accountVip_display = middleware.bucketGet(bucket='yuhua_ftej_auth', key=account_in_display_loop)
            Token_display = middleware.bucketGet(bucket='yuhua_ftej_token', key=account_in_display_loop)
            _temp_accst_display_ = '状态正常' 
            _temp_mobile_display_ = "手机号未知"
            if Token_display:
                try:
                    _mobile_ = Token_display.split('#')[0]
                    _password_ = Token_display.split('#')[1]
                    _temp_mobile_display_ = _mobile_[:3] + '*' * 4 + _mobile_[7:]
                    _, _, _token_status_ = login(_mobile_, _password_)
                    if _token_status_ is False:
                        _temp_accst_display_ = '账密失效'
                except (IndexError, AttributeError): 
                     _temp_accst_display_ = 'Token异常'
            else:
                _temp_accst_display_ = 'Token缺失'
            _temp_accvip_display_ = '未授权'
            if len(accountVip_display) == 0:
                _temp_accvip_display_ = '未授权'
            elif accountVip_display < today_time:
                _temp_accvip_display_ = '授权过期'
            else:
                _temp_accvip_display_ = accountVip_display
            message += f"""
=== 账号 [{count}] ===
📱 账号: {_temp_mobile_display_}
💫 状态: {_temp_accst_display_}
⏰ 到期: {_temp_accvip_display_}
==================\n"""
            count += 1
        sender.reply(f"""
=====福田管理=====
{message}------------------
📝 请选择要管理的账号序号
⚠️ 输入"q"退出操作
==================""")
        mes = sender.input(120000, 1, False) 
        mes = ValueErrors(value=mes, count=count) 
        if mes == 0: 
            sender.reply("""
=====授权操作=====
📝 请输入授权月数
💡 示例输入: 1
⚠️ 输入"q"退出
==================""")
            sjts = sender.input(120000, 1, False)
            sjts = ValueErrors(value=sjts, count=99)
            if Decimal(FukudaVipmoney) == 0:
                success_count = 0
                fail_count = 0
                for acc_one_click in accounts: 
                    try:
                        accVip_one_click = middleware.bucketGet('yuhua_ftej_auth', acc_one_click)
                        tok_one_click = middleware.bucketGet('yuhua_ftej_token', acc_one_click)
                        if not tok_one_click:
                            fail_count += 1
                            continue
                        accVip_one_click_new = empower(empowertime=accVip_one_click, me_as_int=sjts)
                        middleware.bucketSet('yuhua_ftej_auth', acc_one_click, accVip_one_click_new)
                        mob_one_click = tok_one_click.split('#')[0]
                        phn_one_click = mob_one_click[:3] + '*' * 4 + mob_one_click[7:]
                        Addenvs(osname=osname, value=tok_one_click, account=acc_one_click, phone=phn_one_click, owner_id=userid)
                        success_count += 1
                    except:
                        fail_count += 1
                result_msg = f"""
==================
    授权成功
==================
🎫 商品: 福田一键授权
⏰ 授权月数: {sjts}月
------------------
✅ 成功授权: {success_count}个账号
❌ 授权失败: {fail_count}个账号
=================="""
                sender.reply(result_msg)
                exit(0)
            total_money = Decimal(sjts) * Decimal(FukudaVipmoney) * len(accounts)
            pay_menu = """
=====选择支付方式===="""
            if zsm:
                pay_menu += f"""
1️⃣ 微信支付
   💰 {total_money}元/{sjts}月/账号"""
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
📅 时长: {sjts}月/账号
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
                        if ddzf.get('type') == '微信赞赏': Money = float(ddzf.get('money', 0)); Time = ddzf.get('time', ''); From = ddzf.get('from_name', '')
                        elif ddzf.get('type') == '微信收款': Money = float(ddzf.get('money', 0)); Time = ddzf.get('time', ''); From = ddzf.get('from_name', '')
                        else: Money = float(ddzf.get('Money', 0)); Time = ddzf.get('Time', ''); From = ''
                    else:
                        try:
                            ddzf = json.loads(ddzf)
                            if ddzf.get('type') == '微信赞赏': Money = float(ddzf.get('money', 0)); Time = ddzf.get('time', ''); From = ddzf.get('from_name', '')
                            elif ddzf.get('type') == '微信收款': Money = float(ddzf.get('money', 0)); Time = ddzf.get('time', ''); From = ddzf.get('from_name', '')
                            else: Money = float(ddzf.get('Money', 0)); Time = ddzf.get('Time', ''); From = ''
                        except:
                            if "二维码赞赏到账" in str(ddzf):
                                try:
                                    amount = str(ddzf).split("收款金额￥")[1].split("\n")[0]; time_str_pay_all = str(ddzf).split("到账时间")[1].split("\n")[0]
                                    Money = float(amount); Time = time_str_pay_all.strip(); From = ''
                                except Exception as e_parse: sender.reply(f"""
==================
    解析失败
==================
❌ 无法解析收款信息
------------------
错误信息: {str(e_parse)}
=================="""); exit(0)
                            else: sender.reply("""
==================
    格式错误
==================
❌ 无法识别支付信息
------------------
请联系管理员处理
=================="""); exit(0)
                    if float(Money) >= float(total_money):
                        s_count_pay = 0 
                        f_count_pay = 0 
                        for acc_pay_loop_all in accounts: 
                            try:
                                accVip_pay_all = middleware.bucketGet('yuhua_ftej_auth', acc_pay_loop_all) 
                                tok_pay_all = middleware.bucketGet('yuhua_ftej_token', acc_pay_loop_all) 
                                if not tok_pay_all: f_count_pay += 1; continue
                                accVip_pay_all_new = empower(empowertime=accVip_pay_all, me_as_int=sjts) 
                                middleware.bucketSet('yuhua_ftej_auth', acc_pay_loop_all, accVip_pay_all_new)
                                mob_pay_all = tok_pay_all.split('#')[0] 
                                phn_pay_all = mob_pay_all[:3] + '*' * 4 + mob_pay_all[7:] 
                                Addenvs(osname=osname, value=tok_pay_all, account=acc_pay_loop_all, phone=phn_pay_all, owner_id=userid)
                                s_count_pay += 1
                            except: f_count_pay += 1
                        res_msg_pay = f"""
==================
    支付成功
==================
🎫 商品: 福田一键授权
💰 金额: {Money}元
⏰ 时间: {Time}
{f'👤 付款人: {From}' if From else ''}
------------------
✅ 成功授权: {s_count_pay}个账号
❌ 授权失败: {f_count_pay}个账号
⏰ 授权月数: {sjts}月
=================="""
                        sender.reply(res_msg_pay)
                        exit(0)
                    else: sender.reply(f"""
==================
   支付金额错误
==================
💰 应付: {total_money}元
💳 实付: {Money}元
{f'👤 付款人: {From}' if From else ''}

❗ 请联系管理员处理退款！
=================="""); exit(0)
                except Exception as e_outer_pay: sender.reply(f"""
==================
    处理异常
==================
❌ 处理支付结果出错
------------------
错误信息: {str(e_outer_pay)}
=================="""); exit(0)
            else: sender.reply("""
==================
    输入无效
==================
❌ 请输入正确的选项
=================="""); exit(0)
        account_to_manage = accounts[mes - 1] 
        accountVip = middleware.bucketGet(bucket='yuhua_ftej_auth', key=account_to_manage)
        Token = middleware.bucketGet(bucket='yuhua_ftej_token', key=account_to_manage)
        mobile = "手机号未知"
        password = ""
        if Token:
            try:
                mobile = Token.split('#')[0]
                password = Token.split('#')[1]
            except IndexError:
                mobile = "Token格式错误" 
        login_returned_id_or_msg, memberID, login_status_token = login(mobile, password)
        accst = '状态正常'
        if login_status_token is False:
            accst = '账密失效'
            if isinstance(login_returned_id_or_msg, str) and "登录失败" not in login_returned_id_or_msg and "异常" not in login_returned_id_or_msg:
                accst = f"失效: {login_returned_id_or_msg}"
        accvip = '未授权'
        if len(accountVip) == 0: accvip = '未授权'
        elif accountVip < today_time: accvip = '授权过期'
        else: accvip = accountVip
        mobile_display = mobile[:3] + '*' * 4 + mobile[7:] if mobile not in ["手机号未知", "Token格式错误"] else mobile
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
        action_choice_str = sender.input(120000, 1, False)
        try:
            action_choice = int(action_choice_str)
            if action_choice not in [1,2]:
                sender.reply('输入错误！')
                exit(0)
        except (ValueError, TypeError):
             sender.reply('输入错误！')
             exit(0)
        if action_choice == 1: 
            sender.reply("""
=====授权操作=====
📝 请输入授权月数
💡 示例输入: 1
⚠️ 输入"q"退出
==================""")
            auth_months_str = sender.input(120000, 1, False)
            auth_months = ValueErrors(value=auth_months_str, count=99)
            zf(project='福田授权', me_as_int=auth_months, accountVip=accountVip, account=account_to_manage, token=Token, phone=mobile, owner_id=userid)
            _ = Decimal(auth_months) * Decimal(FukudaVipmoney)
            accountVip_after_action = empower(empowertime=accountVip, me_as_int=auth_months)
            middleware.bucketSet(bucket='yuhua_ftej_auth', key=account_to_manage, value=accountVip_after_action)
            Addenvs(osname=osname, value=f'{Token}', account=account_to_manage, phone=mobile, owner_id=userid)
        elif action_choice == 2: 
            sender.reply("""
=====删除确认=====
⚠️ 是否删除该账号?
------------------
[y] 确认删除
[n] 取消操作
==================""")
            yesorno_confirm = sender.input(120000, 1, False)
            if yesorno_confirm and yesorno_confirm.lower() in ['y', '是']:
                try:
                    qlid = allenvs(osname=osname, account=account_to_manage)
                    if qlid:
                        delenvs(id=qlid)
                    middleware.bucketDel(bucket='yuhua_ftej_token', key=account_to_manage)
                    middleware.bucketDel(bucket='yuhua_ftej_auth', key=account_to_manage)
                    accounts.remove(account_to_manage) 
                    if accounts:
                        middleware.bucketSet(bucket='yuhua_ftej_user', key=userid, value=f'{accounts}')
                    else:
                        middleware.bucketDel(bucket='yuhua_ftej_user', key=userid)
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
            elif yesorno_confirm and yesorno_confirm.lower() in ['n', '否']:
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

def zf(project, me_as_int, accountVip, token, phone, account, owner_id):
    try:
        zsm = middleware.bucketGet('yuhua_ftej_config', 'zsm')
        if Decimal(FukudaVipmoney) == 0:
            accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
            middleware.bucketSet('yuhua_ftej_auth', account, accountVip)
            Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=owner_id)
            sender.reply(f"""
=====授权成功=====
🎫 商品: {project}
⏰ 授权时长: {me_as_int}月
==================""")
            return True
        if not zsm:
            sender.reply('未配置收款方式,请联系管理员!')
            exit(0)
        pay_menu = """
=====选择支付方式===="""
        if zsm:
            money = Decimal(me_as_int) * Decimal(FukudaVipmoney)
            pay_menu += f"""
1️⃣ 微信支付
   💰 {money}元/{me_as_int}月"""
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
                    if ddzf.get('Type') == '微信赞赏':
                        Money = float(ddzf.get('Money', 0))
                        Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                        From = ddzf.get('FromName', '')
                    elif ddzf.get('Type') == '微信收款':
                        Money = float(ddzf.get('Money', 0))
                        Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                        From = ddzf.get('FromName', '')
                    elif ddzf.get('Money'):
                        Money = float(ddzf.get('Money', 0))
                        Time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                        From = ddzf.get('FromName', '')
                    elif ddzf.get('money'):
                        Money = float(ddzf.get('money', 0))
                        Time = ddzf.get('time', '').replace('T', ' ').split('.')[0]
                        From = ddzf.get('fromName', '')
                    else:
                        sender.reply('不支持的支付消息格式')
                        exit(0)
                else:
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
                    middleware.bucketSet('yuhua_ftej_auth', account, accountVip)
                    Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=owner_id)
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
        response = requests.post(url, data=payload, headers=headers)
        if response.status_code != 200:
            return f"HTTP错误: {response.status_code}", 0
        if '查询成功' in response.text:
            r = response.json()
            if r.get('data'):
                pointValue = r['data'].get('pointValue', 0)
            else:
                pointValue = 0
        else:
            return f"查询失败: {response.text}", 0
        todaycoin = 0
        url = "https://czyl.foton.com.cn/ehomes-new/homeManager/api/Member/getIntegralList"
        data = {"memberId": memberID, 'transactionDate': today_time}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        if response.status_code != 200:
            return pointValue, 0
        res_json = response.json()
        data_list = res_json.get('data')        
        if data_list:
            for coinj in data_list:
                integral = coinj.get('integral', 0)
                date = coinj.get('date', '')
                try:
                    dt = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                    date_str = dt.strftime("%Y-%m-%d")
                    if date_str == today_time:
                        todaycoin += int(integral)
                except Exception as e:
                    continue
        return pointValue, todaycoin
    except Exception as e:
        return f"查询异常: {str(e)}", 0

def cxs():
    """查询账号状态"""
    if len(uservalue) == 0:
        sender.reply("""
======未绑定账号=====
❌ 未找到任何账号信息
💡 发送"福田登录"绑定
==================""")
        return
    accounts = eval(uservalue)
    for account in accounts:
        try:
            accountVip = middleware.bucketGet(bucket='yuhua_ftej_auth', key=account)
            Token = middleware.bucketGet(bucket='yuhua_ftej_token', key=account)
            if not Token:
                sender.reply("""
==================
    获取失败
==================
❌ Token获取失败
==================""")
                continue
            mobile = Token.split('#')[0]
            password = Token.split('#')[1]
            phone = mobile[:3] + '*' * 4 + mobile[7:]
            memberID = get_valid_session(mobile, password)
            if not memberID:
                sender.reply(f"""
==================
    登录失败
==================
📱 账号: {phone}
❌ 状态: 账密失效或网络异常
==================""")
                continue
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
==================""")
                continue
            else:
                pointValue, todaycoin = cx(memberID)
                if isinstance(pointValue, str) and ("错误" in pointValue or "失效" in pointValue or "失败" in pointValue):
                     memberID = get_valid_session(mobile, password, force_refresh=True)
                     if memberID:
                         pointValue, todaycoin = cx(memberID)

                if isinstance(pointValue, str) and "错误" in pointValue:
                    sender.reply(f"""
=====查询异常=====
📱 账号: {phone}
❌ 错误: {pointValue}
==================""")
                else:
                    sender.reply(f"""
======账号详情=====
📱 账号: {phone}
💎 当前积分: {pointValue}
📈 今日积分: {todaycoin}
📅 到期时间: {accountVip}
==================""")
        except Exception as e:
            try:
                phone = mobile[:3] + '*' * 4 + mobile[7:]
            except:
                phone = "未知账号"
            sender.reply(f"""
=====系统错误=====
📱 账号: {phone}
❌ 错误: {str(e)}
==================""")

def push(user, mobile, message):
    """推送消息到各个平台"""
    push_msg = f"""
======账号通知======
📱 账号: {mobile}
📢 消息: {message}
=================="""
    platforms = ['qq', 'qb', 'wx', 'gw', 'sb', 'wb', 'tg', 'tb', 'qx', 'xy', 'ip']
    for platform in platforms:
        try:
            middleware.push(platform, '', user, '', push_msg)
        except Exception as e:
            print(f"推送到{platform}失败: {str(e)}")

def qgcx():
    sender.reply('正在加载...')
    from curl_cffi import requests
    headers = {
        'User-Agent': "okhttp/3.14.9",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/json",
    }
    def ProductDetails(productId):
        try:
            url = "https://wap.365autogo.com/mobile/api/product/info"
            param = {"productId": productId}
            params = {
                'param': json.dumps(param)
            }
            response = requests.get(url, params=params, headers=headers)
            data = response.json()['data']
            availableStock = data['product']['goods']['availableStock']
            point = data['product']['goods']['point']
            name = data['product']['name']
            title = data['product']['title']
            date_pattern = re.compile(r'(\d{1,2}月\d{1,2}日)')
            time_pattern = re.compile(r'(上午|下午)?\d{1,2}[:：]\d{2}')
            price_pattern = re.compile(r'抢购价(\d+)元')
            date_match = date_pattern.search(title)
            time_match = time_pattern.search(title)
            price_match = price_pattern.search(title)
            date = date_match.group(0) if date_match else "未知日期"
            time = time_match.group(0) if time_match else "未知时间"
            price = int(price_match.group(1)) * 100 if price_match else 0
            if date != "未知日期":
                text = f"2024年{date}"
                date_match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
                if date_match:
                    year, month, day = date_match.groups()
                    date2 = f"{int(year)}-{int(month)}-{int(day)}"
                else:
                    date2 = None
            else:
                date2 = None
            return availableStock, point, name, date, time, price, date2
        except Exception as e:
            sender.reply(f'查询商品详情失败：{str(e)}')
            return None, None, None, None, None, None, None
    try:
        url = "https://wap.365autogo.com/mobile/api/pointShop"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            sender.reply("获取商品列表失败")
            return
        data = response.json()
        if 'data' not in data or 'limitExchange' not in data['data']:
            sender.reply("未找到抢购商品信息")
            return
        limitExchange = data['data']['limitExchange']
        if not limitExchange:
            sender.reply("当前没有抢购商品")
            return
        for goodsjson in limitExchange:
            productId = goodsjson['productId']
            result = ProductDetails(productId)
            if result[0] is None: 
                continue
            availableStock, point, name, date, time, price, date2 = result
            msg = (
                f"商品名称: {name or '未知'}\n"
                f"抢购时间: {date or '未知'} {time or '未知'}\n"
                f"商品原价: {point or '未知'}\n"
                f"抢购价: {price/100 if price else '未知'}元\n"
                f"库存: {availableStock or '未知'}"
            )
            sender.reply(msg)
        if date2 and today_time < date2:
            sender.reply('温馨提示: 请注意抢购时间，本期抢购可能已结束！')
    except Exception as e:
        sender.reply(f'查询抢购信息失败：{str(e)}')

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
        users = middleware.bucketAllKeys('yuhua_ftej_user')
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
            accountlist = middleware.bucketGet('yuhua_ftej_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
            accounts = eval(accountlist)
            for account in accounts:
                try:
                    accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
                    token = middleware.bucketGet('yuhua_ftej_token', account)
                    if not token:
                        fail_count += 1
                        continue
                    accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                    middleware.bucketSet('yuhua_ftej_auth', account, accountVip)
                    mobile = token.split('#')[0]
                    phone = mobile[:3] + '*' * 4 + mobile[7:]
                    Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=user)
                    success_count += 1
                except:
                    fail_count += 1
        msg = f"一键授权完成!\n成功授权: {success_count}个账号\n授权失败: {fail_count}个账号\n授权月数: {sjts}月"
        sender.reply(msg)
    elif xz == '2':
        msg = f'请输入需要授权的账号id\n通过给机器人发送myuid获得\n退出【q】！'
        sender.reply(msg)
        myuid = sender.input(60000, 1, False) 
        if myuid == 'q' or myuid == 'Q':
            sender.reply("退出！")
            return
        elif myuid == '':
            sender.reply(f'超时退出！')
            return
        accountlist = middleware.bucketGet('yuhua_ftej_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"未找到{myuid}的福田账号信息!")
            return
        accounts = eval(accountlist)
        n = 0
        msg = '========福田授权========\n'
        msg += '0、授权所有账号\n======================\n'
        for account in accounts:
            n += 1
            accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
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
                        accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
                        token = middleware.bucketGet('yuhua_ftej_token', account)
                        if not token:
                            continue
                        if len(accountVip) == 0 or accountVip == '未授权':
                            current_date = today_date
                        else:
                            current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                        new_date = current_date + timedelta(days=days)
                        middleware.bucketSet('yuhua_ftej_auth', account, str(new_date))
                        mobile = token.split('#')[0]
                        phone = mobile[:3] + '*' * 4 + mobile[7:]
                        Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=myuid)
                        success_count += 1
                    except:
                        continue
                msg = f"批量修改完成!\n成功修改: {success_count}个账号\n调整天数: {days}天"
                sender.reply(msg)
            except ValueError:
                sender.reply('输入的天数无效!')
                return
        elif 1 <= int(xz) <= len(accounts):
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
                accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
                token = middleware.bucketGet('yuhua_ftej_token', account)
                if not token:
                    sender.reply("未找到账号token信息!")
                    return
                if len(accountVip) == 0 or accountVip == '未授权':
                    current_date = today_date
                else:
                    current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                new_date = current_date + timedelta(days=days)
                middleware.bucketSet('yuhua_ftej_auth', account, str(new_date))
                mobile = token.split('#')[0]
                phone = mobile[:3] + '*' * 4 + mobile[7:]
                Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=myuid)
                msg = f'修改成功!\n账号: {account}\n调整天数: {days}天\n新到期时间: {new_date}'
                sender.reply(msg)
            except ValueError:
                sender.reply('输入的天数无效!')
                return
        else:
            sender.reply('输入的序号无效!')
            return
    elif xz == '3':
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
            users = middleware.bucketAllKeys('yuhua_ftej_user')
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
                    accountlist = middleware.bucketGet('yuhua_ftej_user', user)
                    if accountlist == '' or accountlist == '{}':
                        continue
                    accounts = eval(accountlist)
                    for account in accounts:
                        try:
                            accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
                            token = middleware.bucketGet('yuhua_ftej_token', account)
                            if not token:
                                continue
                            if len(accountVip) == 0 or accountVip == '未授权':
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('yuhua_ftej_auth', account, str(new_date))
                            mobile = token.split('#')[0]
                            phone = mobile[:3] + '*' * 4 + mobile[7:]
                            Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=user)
                            total_success += 1
                        except:
                            continue
                msg = f"批量修改完成!\n成功修改: {total_success}个账号\n调整天数: {days}天"
                sender.reply(msg)
            except ValueError:
                sender.reply('输入的天数无效!')
                return
        elif choice == '2':
            msg = f'请输入需要修改的账号id\n通过给机器人发送myuid获得\n退出【q】！'
            sender.reply(msg)
            myuid = sender.input(60000, 1, False) 
            if myuid == 'q' or myuid == 'Q':
                sender.reply("退出！")
                return
            elif myuid == '':
                sender.reply(f'超时退出！')
                return
            accountlist = middleware.bucketGet('yuhua_ftej_user', myuid)
            if accountlist == '' or accountlist == '{}':
                sender.reply(f"未找到{myuid}的福田账号信息!")
                return
            accounts = eval(accountlist)
            n = 0
            msg = '========修改授权时间========\n'
            msg += '0、修改所有账号\n======================\n'
            for account in accounts:
                n += 1
                accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
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
                            accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
                            token = middleware.bucketGet('yuhua_ftej_token', account)
                            if not token:
                                continue
                            if len(accountVip) == 0 or accountVip == '未授权':
                                current_date = today_date
                            else:
                                current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                            new_date = current_date + timedelta(days=days)
                            middleware.bucketSet('yuhua_ftej_auth', account, str(new_date))
                            mobile = token.split('#')[0]
                            phone = mobile[:3] + '*' * 4 + mobile[7:]
                            Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=myuid)
                            success_count += 1
                        except:
                            continue
                    msg = f"批量修改完成!\n成功修改: {success_count}个账号\n调整天数: {days}天"
                    sender.reply(msg)
                except ValueError:
                    sender.reply('输入的天数无效!')
                    return
            elif 1 <= int(xz) <= len(accounts):
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
                    accountVip = middleware.bucketGet('yuhua_ftej_auth', account)
                    token = middleware.bucketGet('yuhua_ftej_token', account)
                    if not token:
                        sender.reply("未找到账号token信息!")
                        return
                    if len(accountVip) == 0 or accountVip == '未授权':
                        current_date = today_date
                    else:
                        current_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                    new_date = current_date + timedelta(days=days)
                    middleware.bucketSet('yuhua_ftej_auth', account, str(new_date))
                    mobile = token.split('#')[0]
                    phone = mobile[:3] + '*' * 4 + mobile[7:]
                    Addenvs(osname=osname, value=token, account=account, phone=phone, owner_id=myuid)
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
    """清理过期的福田账号"""
    if not sender.isAdmin():
        sender.reply("⛔ 您没有权限执行此操作！")
        exit(0)
    users = middleware.bucketAllKeys(bucket='yuhua_ftej_user')
    sender.reply(
        "=====清理统计=====\n"
        f"📊 找到用户数: {len(users) if users else 0}\n"
        "==================="
    )
    if not users:
        sender.reply("❌ 没有找到任何绑定的福田账号")
        exit(0)
    cleaned_count = 0
    for user in users:
        accountlist = middleware.bucketGet(bucket='yuhua_ftej_user', key=user)
        if not accountlist:
            continue
        accounts = eval(accountlist)
        valid_accounts = []
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='yuhua_ftej_auth', key=account)
            if len(accountVip) == 0 or accountVip <= today_time:
                try:
                    qlid = allenvs(osname=osname, account=account)
                    if qlid:
                        delenvs(id=qlid)
                except:
                    pass
                middleware.bucketDel(bucket='yuhua_ftej_token', key=account)
                middleware.bucketDel(bucket='yuhua_ftej_auth', key=account)
                cleaned_count += 1
            else:
                valid_accounts.append(account)
        if valid_accounts:
            middleware.bucketSet(bucket='yuhua_ftej_user', key=user, value=str(valid_accounts))
        else:
            middleware.bucketDel(bucket='yuhua_ftej_user', key=user)
    sender.reply(
        "=====清理完成=====\n"
        f"🧹 清理账号: {cleaned_count}个\n"
        "==================="
    )

###################### 防连通检测(禁止删除) ######################
from bs4 import BeautifulSoup

def _perform_maintenance_check() -> bool:
    url = "https://yuhualhh.250666.xyz/shouquan"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache"
    }
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=(5, 10),
                verify=True,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='note-content')
            if content_div:
                return "已启动服务" in content_div.get_text(strip=True)
            return any("已启动服务" in tag.get_text() for tag in soup.find_all(['div', 'p']))
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < 2:
                time.sleep(2)
                continue
            return False
        except requests.exceptions.HTTPError:
            return False
        except Exception:
            return False
    return False
def check_maintenance_page() -> bool:
    import os, base64, hashlib, json
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    cache_bucket = "time"
    cache_key = "status_cache"
    ttl_seconds = 12 * 3600
    try:
        salt = b'\x8a\x9b\x1f\xe3\x7d\x4c\x5b\x6a\x01\x23\x45\x67\x89\xab\xcd\xef'
        identifier = "yuhua666"
        key = hashlib.sha256(salt + identifier.encode('utf-8')).digest()
        aesgcm = AESGCM(key)
        cached_data_str = middleware.bucketGet(cache_bucket, cache_key)
        if cached_data_str:
            decoded_data = base64.b64decode(cached_data_str.encode('utf-8'))
            nonce = decoded_data[:12]
            ciphertext = decoded_data[12:]
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            cached_data = json.loads(decrypted_bytes.decode('utf-8'))
            if (time.time() - cached_data.get("timestamp", 0)) < ttl_seconds and cached_data.get("status") is True:
                return True
    except Exception:
        pass
    live_status = _perform_maintenance_check()
    new_cache_payload = {
        "status": live_status,
        "timestamp": time.time()
    }
    try:
        salt = b'\x8a\x9b\x1f\xe3\x7d\x4c\x5b\x6a\x01\x23\x45\x67\x89\xab\xcd\xef'
        identifier = "yuhua666"
        key = hashlib.sha256(salt + identifier.encode('utf-8')).digest()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        plaintext = json.dumps(new_cache_payload).encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        encrypted_payload = base64.b64encode(nonce + ciphertext).decode('utf-8')
        middleware.bucketSet(cache_bucket, cache_key, encrypted_payload)
    except Exception as e:
        pass
    return live_status

today_date = datetime.now().date()
today_time = str(today_date)
QLurl, ClientID, ClientSecret, FukudaVipmoney, osname = PluginsData()
qltoken = QLtoken(QLurl, ClientID, ClientSecret)
usermessage = sender.getMessage()
imtype = sender.getImtype()

if not check_maintenance_page():
        sender.reply("❌ 服务端无法连通, 插件停止运行")
        exit(0)
        
if '登录' in usermessage or '登陆' in usermessage:
    bind()
elif '管理' in usermessage:
    Administration()
elif '查询' in usermessage:
    cxs()
elif '福田抢购' in usermessage:
    qgcx()
elif '福田授权' in usermessage:
    fukuda_auth()
elif '清理福田' in usermessage or '福田清理' in usermessage:
    clean_expired_accounts()
elif imtype == 'fake':
    """定时任务处理"""
    users = middleware.bucketAllKeys(bucket='yuhua_ftej_user')
    if not users:
        exit(0)
    for user in users:
        try:
            uservalue = middleware.bucketGet(bucket='yuhua_ftej_user', key=user)
            if not uservalue:
                continue
            accounts = eval(uservalue)
            for account in accounts:
                try:
                    token = middleware.bucketGet(bucket='yuhua_ftej_token', key=account)
                    accountVip = middleware.bucketGet(bucket='yuhua_ftej_auth', key=account)
                    if not token:
                        continue
                    mobile = token.split('#')[0]
                    password = token.split('#')[1]
                    phone = mobile[:3] + '*' * 4 + mobile[7:]
                    valid_memberID = None
                    cached_str = middleware.bucketGet('yuhua_ftej_api_session', mobile)
                    if cached_str:
                        try:
                            cached_data = json.loads(cached_str)
                            temp_id = cached_data.get('memberID')
                            if temp_id:
                                res, _ = cx(temp_id)
                                if not (isinstance(res, str) and ("错误" in res or "失败" in res or "异常" in res)):
                                    valid_memberID = temp_id
                        except:
                            pass
                    if not valid_memberID:
                        _, new_id, status = login(mobile, password)
                        if status is not False:
                            valid_memberID = new_id
                            session_data = {
                                'memberID': new_id,
                                'uid': str(new_id),
                                'timestamp': time.time()
                            }
                            middleware.bucketSet('yuhua_ftej_api_session', mobile, json.dumps(session_data))
                        else:
                            push(user, phone, """   
⚠️ 福田账号状态异常
------------------
❌ 账号密码已失效
💡 请尽快更新账号""")
                        continue
                    if len(accountVip) == 0 or accountVip < today_time:
                        push(user, phone, """
⚠️ 福田授权已过期
------------------
❌ 授权状态失效
💡 请及时续费授权""")
                except Exception as e:
                    print(f"处理账号 {account} 时出错: {str(e)}")
                    continue
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue