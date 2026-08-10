#[pin:false]
#[disable:true]
#[public:true]
#[rule: ^(酷我登录|酷我登陆|登陆酷我|登录酷我|酷我查询|查询酷我|酷我管理|管理酷我|酷我授权|酷我教程|酷我提现说明|总结今日酷我|酷我清理)$]
#[version: 1.3.9]
#[price: 18.88]
#[title: 酷我Music]
#[author: sky2022]
#[admin: false]
#[cron: 1 8,15 * * *]
#[icon: https://picui.ogmua.cn/s1/2026/02/26/69a05264c50f8.webp]
#[description: 指令:酷我登陆 酷我查询 酷我管理 对接青龙/呆呆面板 支持手机号丨定时任务：每天8点和15点自动检测授权过期及CK失效并推送通知丨V1.3.9:新增定时检测推送，每天8点/15点自动检测授权到期和账号失效状态并通知用户丨V1.3.8:统一面板配置为面板类型+对接面板配置，并新增呆呆面板分组配置]

import re
import middleware
import requests
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal 
import base64
import random
import time
from urllib.parse import unquote

log = print

# [param: {"required":true,"key":"dd_Kuwo_PluginsData.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_Kuwo_PluginsData.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_Kuwo_PluginsData.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_Kuwo_PluginsData.panel_group","bool":false,"placeholder":"例:酷我","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# 变量名
# [param: {"required":true,"key":"dd_Kuwo_PluginsData.osname","bool":false,"placeholder":"必填项,例:kwyy","name":"面板变量名","desc":"提交到面板中的酷我音乐变量名"}]
# 上车价格
# [param: {"required":true,"key":"dd_Kuwo_PluginsData.KuwoVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# 积分上车价格
# [param: {"required":true,"key":"dd_Kuwo_PluginsData.Kuwocoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_Kuwo_PluginsData.days_per_month","bool":false,"placeholder":"默认30天","name":"每月天数","desc":"设置每月按多少天计算"}]

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_Kuwo_bind', key=userid) or ''

def normalize_panel_type(panel_type_value, legacy_use_daidai_value='false'):
    """统一解析面板类型，兼容新旧配置。"""
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

def QLtoken(QLurl, ClientID, ClientSecret):
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        A = requests.get(url)
        if "token" in A.text:
            ql = A.content
            qlrequests = json.loads(ql)
            qltoken = qlrequests['data']['token']
            return qltoken
    except Exception:
        sender.reply("链接青龙失败,请检查对接容器！")
        exit(0)

def seekdd():
    """获取呆呆面板配置"""
    try:
        if not dd_Kuwo_ddname:
            sender.reply("=====配置错误=====\n未配置呆呆面板信息\n请在插件配置中填写:\n• 对接面板类型: 呆呆\n• 对接面板配置: Host丨AppKey丨AppSecret\n• 使用中文丨分隔\n==================")
            exit(0)

        ddlist = dd_Kuwo_ddname.split('丨')
        if len(ddlist) != 3:
            sender.reply(f"=====格式错误=====\n呆呆面板配置格式错误\n当前格式: {dd_Kuwo_ddname}\n正确格式:\nHost丨AppKey丨AppSecret\n==================")
            exit(0)

        DDurl = ddlist[0].strip()
        AppKey = ddlist[1].strip()
        AppSecret = ddlist[2].strip()

        if not all([DDurl, AppKey, AppSecret]):
            sender.reply("=====参数错误=====\n呆呆面板配置参数不完整\n请确保以下参数都已填写:\n• 面板地址(Host)\n• AppKey\n• AppSecret\n==================")
            exit(0)

        if not DDurl.startswith(('http://', 'https://')):
            sender.reply(f"=====地址错误=====\n呆呆面板地址格式错误\n当前地址: {DDurl}\n正确格式:\n• http://panel.example.com\n• https://panel.example.com\n==================")
            exit(0)

        try:
            ddtoken = DDtoken(DDurl=DDurl, AppKey=AppKey, AppSecret=AppSecret)
            return DDurl, ddtoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")

    except SystemExit:
        raise
    except Exception as e:
        sender.reply(f"=====连接失败=====\n无法连接呆呆面板\n请检查:\n1. 面板是否运行\n2. 网络是否正常\n3. 配置是否正确\n4. 错误信息: {str(e)}\n==================")
        exit(0)

def DDtoken(DDurl, AppKey, AppSecret):
    """获取呆呆面板Token"""
    try:
        url = f'{DDurl}/api/open-api/token'
        data = {"app_key": AppKey, "app_secret": AppSecret}
        response = requests.post(url, json=data)

        if response.status_code != 200:
            sender.reply(f"=====请求失败=====\n呆呆面板API请求失败\n状态码: {response.status_code}\n请检查:\n• API地址是否正确\n• 面板是否正常运行\n==================")
            exit(0)

        result = response.json()
        access_token = result.get('data', {}).get('access_token')
        if access_token:
            return access_token
        else:
            sender.reply("=====认证失败=====\n获取Token失败\n请检查:\n• AppKey是否正确\n• AppSecret是否正确\n• 应用是否有权限\n==================")
            exit(0)

    except requests.exceptions.RequestException as e:
        sender.reply(f"=====网络错误=====\n连接呆呆面板失败\n错误信息: {str(e)}\n==================")
        exit(0)
    except SystemExit:
        raise
    except Exception as e:
        sender.reply(f"=====系统错误=====\n处理请求时出错\n错误信息: {str(e)}\n==================")
        exit(0)

def get_dd_headers(content_type="application/json"):
    """获取呆呆面板请求头"""
    return {
        "Authorization": f"Bearer {panel_token}",
        "accept": "application/json",
        "Content-Type": content_type
    }

def dd_allenvs(osname, account):
    """查询呆呆面板环境变量"""
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
        sender.reply("=====连接失败=====\n连接呆呆面板获取变量失败\n==================")
        exit(0)

def dd_delenvs(id):
    """删除呆呆面板环境变量"""
    if id is None:
        return
    url = f"{panel_url}/api/envs/{id}"
    headers = get_dd_headers()
    requests.delete(url, headers=headers)

def DDcreate(osname, value, account, phone):
    """在呆呆面板创建新的环境变量"""
    try:
        expire_date = middleware.bucketGet('dd_Kuwo_Vip', account) or '未授权'
        url = f"{panel_url}/api/envs"

        data = {
            "value": value,
            "name": osname,
            "remarks": f'酷我:{account}丨用户:{userid}丨手机:{phone}丨到期:{expire_date}'
        }
        if panel_group:
            data["group"] = panel_group

        headers = get_dd_headers()
        response = requests.post(url, headers=headers, json=data)

        if response.status_code not in (200, 201):
            sender.reply(f"=====添加变量失败=====\n请求失败\n状态码: {response.status_code}\n==================")
            return False

        result = response.json()
        resp_data = result.get('data')
        if resp_data:
            return True
        return False

    except SystemExit:
        raise
    except Exception as e:
        sender.reply(f"=====系统错误=====\n添加变量失败\n错误信息: {str(e)}\n==================")
        return False

def DDupdate(osname, value, account, env_id, phone):
    """更新呆呆面板环境变量"""
    expire_date = middleware.bucketGet('dd_Kuwo_Vip', account) or '未授权'
    url = f"{panel_url}/api/envs/{env_id}"

    data = {
        "value": value,
        "name": osname,
        "remarks": f'酷我:{account}丨用户:{userid}丨手机:{phone}丨到期:{expire_date}'
    }
    if panel_group:
        data["group"] = panel_group

    headers = get_dd_headers()
    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        return True
    else:
        sender.reply("=====更新失败=====\n更新变量失败,请联系管理员处理\n==================")
        return False

def PluginsData():
    """获取插件配置数据"""
    panel_type = normalize_panel_type(
        middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='panel_type') or '',
        middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='use_daidai') or 'false'
    )
    if not panel_type:
        sender.reply('对接面板类型填写无效，请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai')
        exit(0)

    panel_config = (middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='panel_config') or '').strip()
    legacy_qinglong = middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='Qinglong') or ''
    legacy_dd_config = middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='dd_Kuwo_ddname') or ''
    KuwoVipmoney = middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='KuwoVipmoney')
    osname = middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='osname')
    Kuwocoin = middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='Kuwocoin')
    panel_group = (middleware.bucketGet(bucket='dd_Kuwo_PluginsData', key='panel_group') or '').strip()

    use_daidai = panel_type == 'daidai'
    Qinglong = panel_config or legacy_qinglong if panel_type == 'qinglong' else legacy_qinglong
    dd_Kuwo_ddname = panel_config or legacy_dd_config if panel_type == 'daidai' else legacy_dd_config

    QLurl = ''
    ClientID = ''
    ClientSecret = ''

    if not use_daidai:
        # 检查 Qinglong 是否为空或 None
        if not Qinglong:
            sender.reply('未配置青龙面板信息，请填写：对接面板类型=青龙，对接面板配置=Host丨ClientID丨ClientSecret')
            exit(0)
        
        # 解析青龙配置
        qllist = Qinglong.split('丨')
        if len(qllist) != 3:
            sender.reply('青龙面板配置格式错误，请使用"丨"分隔 URL、ClientID 和 ClientSecret')
            exit(0)
            
        QLurl = qllist[0]
        ClientID = qllist[1]
        ClientSecret = qllist[2]
    
    # 处理 KuwoVipmoney
    if not KuwoVipmoney or KuwoVipmoney == '0':
        KuwoVipmoney = Decimal('0')
    else:
        try:
            KuwoVipmoney = Decimal(str(KuwoVipmoney))
        except:
            KuwoVipmoney = Decimal('0')
    
    # 检查 osname
    if not osname:
        sender.reply('酷我音乐未填写变量信息，请检查配参信息！')
        exit(0)
    
    # 处理 Kuwocoin
    if not Kuwocoin:
        Kuwocoin = 9999
    else:
        try:
            Kuwocoin = int(Kuwocoin)
        except:
            Kuwocoin = 9999
            
    return QLurl, ClientID, ClientSecret, KuwoVipmoney, osname, Kuwocoin, use_daidai, dd_Kuwo_ddname, panel_group

def recognize_captcha(image_base64: str) -> str:
    """使用远程ddddocr接口进行验证码识别"""
    try:
        # 使用远程ddddocr接口
        ocr_url = 'https://ddddocr.linzixuan.work/classification'
        
        # 移除base64头部信息(如果有的话)
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        image_base64 = image_base64.replace('data:image/jpeg;base64,', '')
        image_base64 = image_base64.replace('data:image/png;base64,', '')
        
        # 准备POST数据
        data = {'image': image_base64}
        
        # 发送POST请求
        response = requests.post(
            ocr_url,
            json=data,
            timeout=10
        )
        
        # 解析JSON响应
        result = response.json()
        if not result or 'result' not in result:
            raise Exception("验证码识别失败: 返回结果无效")
            
        return result['result'].strip()  # 返回result字段的值
        
    except Exception as e:
        raise

def login(value):
    """登录酷我账号
    参数格式: 手机号#密码
    """
    try:
        values = value.split('#')
        if len(values) != 2:
            return "登录参数格式错误", "登录失败", False
            
        phone = values[0]
        password = values[1]
        
        # 获取验证码
        captcha_url = 'http://www.kuwo.cn/api/common/captcha/getcode'
        captcha_params = {
            'reqId': 'bb7dd120-d1b7-11ef-b9c9-9dd176f54932',
            'httpsStatus': '1'
        }
        
        captcha_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'Referer': 'http://www.kuwo.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        response = requests.get(
            captcha_url,
            params=captcha_params,
            headers=captcha_headers
        )
        
        if 'data' not in response.json():
            raise Exception("获取验证码失败")
            
        captcha_data = response.json()['data']
        image_data = captcha_data['img']
        token = captcha_data['token']
        
        # 识别验证码
        verify_code = recognize_captcha(
            image_data.replace('data:image/jpeg;base64,', '')
        )
        
        # 执行登录
        login_url = 'https://wapi.kuwo.cn/api/www/login/loginByKw'
        login_data = json.dumps({
            'userIp': 'www.kuwo.cn',
            'uname': phone,
            'password': password,
            'verifyCode': verify_code,
            'img': image_data,
            'verifyCodeToken': token
        })
        
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'http://www.kuwo.cn',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'http://www.kuwo.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        login_response = requests.post(
            login_url,
            params={'httpsStatus': '1'},
            data=login_data,
            headers=login_headers,
            timeout=10
        )
        
        result = login_response.json()
        if result.get('code') != 200:
            raise Exception(f"登录失败: {result.get('msg', '未知错误')}")
            
        cookies = result['data']['cookies']
        username = cookies.get('uname3', phone)
        loginSid = cookies.get('websid')
        loginUid = cookies.get('userid')
        
        # 生成或获取其他必要信息
        appUid = result['data'].get('uid', loginUid)
        devId = ''.join(random.choices('0123456789abcdef', k=16))
        
        # 构造token
        token = f"{appUid}#{devId}#{loginSid}#{phone}"
        
        # 登录成功后，保存原始登录信息
        middleware.bucketSet(bucket='dd_Kuwo_login', key=username, value=value)
        
        return username, loginSid, token
        
    except Exception as e:
        return f"登录异常: {str(e)}", "登录异常", False

def bind():
    """绑定酷我账号"""
    sender.reply(
        "=====酷我账号登录=====\n"
        "🎵 请输入登录参数:\n"
        "📝 格式: 手机号#密码\n"
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
            sender.reply('输入格式错误！需要手机号#密码格式')
            exit(0)
        phone = values[0]  # 获取手机号用于显示
    except:
        exit(0)
        
    account, loginSid, token = login(login_value)
    if token is False:
        sender.reply(f'{account}')
        exit(0)
        
    middleware.bucketSet(bucket='dd_Kuwo_account', key=account, value=token)
    # 保存原始登录信息
    middleware.bucketSet(bucket='dd_Kuwo_login', key=account, value=login_value)  # 确保保存原始登录信息
    accountVip = middleware.bucketGet(bucket='dd_Kuwo_Vip', key=account) or ''
    
    if len(uservalue) == 0:
        accounts = []
        accounts.append(account)
        middleware.bucketSet(bucket='dd_Kuwo_bind', key=userid, value=f'{accounts}')
        if len(accountVip) != 0 and accountVip >= today_time:
            # 使用原始登录信息而不是token
            Addenvs(osname=osname, value=login_value, account=account, phone=phone)
            sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[酷我管理]管理账号\n🔍 发送[酷我查询]查询状态\n===================")
        else:
            sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[酷我管理]管理账号\n🔍 发送[酷我查询]查询状态\n===================")
    else:
        accounts = eval(uservalue)
        if account in accounts:
            if len(accountVip) != 0 and accountVip >= today_time:
                # 使用原始登录信息而不是token
                Addenvs(osname=osname, value=login_value, account=account, phone=phone)
                sender.reply("更新账号成功，可对我说'酷我管理'对账号进行管理！")
            else:
                sender.reply("更新账号成功,授权已过期！")
        else:
            accounts.append(account)
            middleware.bucketSet(bucket='dd_Kuwo_bind', key=userid, value=f'{accounts}')
            if len(accountVip) != 0 and accountVip >= today_time:
                # 使用原始登录信息而不是token
                Addenvs(osname=osname, value=login_value, account=account, phone=phone)
                sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[酷我管理]管理账号\n🔍 发送[酷我查询]查询状态\n===================")
            else:
                sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[酷我管理]管理账号\n🔍 发送[酷我查询]查询状态\n===================")

def Administration():
    """管理酷我账号"""
    accst = '状态正常'
    message = ''
    count = 1
    
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        # 显示账号列表
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='dd_Kuwo_Vip', key=account) or ''
            Token = middleware.bucketGet(bucket='dd_Kuwo_account', key=account)
            try:
                values = Token.split('#')
                phone = values[3]  # 获取手机号
                loginUid = values[0]  # 获取loginUid
                loginSid = values[2]  # 获取loginSid
                
                # 验证账号状态
                verify_url = "https://integralapi.kuwo.cn/api/v1/online/sign/new/todayStatus"
                verify_headers = {
                    'Cookie': f'tmeAppID=kwplayer;loginSid={loginSid};loginUid={loginUid}',
                    'User-Agent': 'KWPlayer/11.1.2 (iPhone; iOS 17.7.2; Scale/3.00)'
                }
                verify_response = requests.get(verify_url, headers=verify_headers)
                if verify_response.status_code != 200:
                    accst = '账号失效'
            except:
                accst = '账号异常'
                
            if len(accountVip) == 0:
                accvip = '未授权'
            elif accountVip < today_time:
                accvip = '授权过期'
            else:
                accvip = accountVip
                
            phone = phone[:3] + '*' * 4 + phone[7:]  # 手机号脱敏
            message += (
                f"[{count}] 账号信息\n"
                f"📱 账号: {phone}\n"
                f"💫 状态: {accst}\n"
                f"⏰ 到期: {accvip}\n"  # 使用 accvip 而不是直接使用 accountVip
                f"-------------------\n"
            )
            count += 1
            
        # 选择要管理的账号
        sender.reply(
            f"====酷我管理====\n"
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
            if mes < 1 or mes >= count:  # 修改这里的判断条件
                sender.reply('输入的账号序号无效')
                exit(0)
        except:
            sender.reply('输入有误，请输入数字')
            exit(0)
            
        # 获取选中的账号信息
        selected_account = accounts[mes - 1]
        accountVip = middleware.bucketGet(bucket='dd_Kuwo_Vip', key=selected_account) or ''
        Token = middleware.bucketGet(bucket='dd_Kuwo_account', key=selected_account)
        values = Token.split('#')
        phone = values[3]
        loginUid = values[0]
        loginSid = values[2]
        phone_masked = phone[:3] + '*' * 4 + phone[7:]

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
            f"📱 账号: {phone_masked}\n"
            f"💫 状态: {accst}\n"
            f"⏰ 到期: {display_vip}\n"  # 使用处理后的 display_vip
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
            if mes < 1 or mes > 2:  # 修改这里的判断条件
                sender.reply('输入的选项无效')
                exit(0)
        except:
            sender.reply('输入有误，请输入数字')
            exit(0)
            
        # 执行选择的操作
        if mes == 1:
            # 授权账号
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
            if not zf(project='酷我授权', me_as_int=months, accountVip=accountVip, account=selected_account, token=Token, phone=values[3]):
                # 如果支付失败或用户退出，不执行授权操作
                return
            
            money = Decimal(months) * Decimal(KuwoVipmoney)
            accountVip = empower(empowertime=accvip, me_as_int=months)
            middleware.bucketSet(bucket='dd_Kuwo_Vip', key=selected_account, value=accountVip)
            # 获取原始登录信息
            login_value = middleware.bucketGet('dd_Kuwo_login', selected_account)
            if not login_value:
                sender.reply('获取账号登录信息失败')
                exit(0)
            Addenvs(osname=osname, value=login_value, account=selected_account, phone=values[3])
            
        elif mes == 2:
            # 删除账号
            sender.reply(
                "=====删除确认=====\n"
                f"📱 账号: {phone_masked}\n"
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
                            middleware.bucketDel(bucket='dd_Kuwo_bind', key=userid)
                        else:
                            middleware.bucketSet(bucket='dd_Kuwo_bind', key=userid, value=f'{accounts}')
                        # 删除账号相关的其他数据
                        middleware.bucketDel(bucket='dd_Kuwo_account', key=selected_account)
                        middleware.bucketDel(bucket='dd_Kuwo_Vip', key=selected_account)
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
        sender.reply('未绑定酷我音乐账号！')
        exit(0)

def query_withdraw_history(token):
    """查询提现记录"""
    try:
        # 从token中解析必要参数
        values = token.split('#')
        if len(values) != 4:
            return "获取账号信息失败"
            
        loginUid = values[0]
        loginSid = values[2]
        
        # 构造请求
        url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/withdrawDetails"
        params = {
            'loginUid': loginUid,
            'loginSid': loginSid,
            'pn': '1',  # 第一页
            'rn': '2'   # 只获取最近2条记录
        }
        
        headers = {
            'Host': 'integralapi.kuwo.cn',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://h5app.kuwo.cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KWMusic/11.1.2.0',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9'
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            return "查询失败，请稍后重试"
            
        data = response.json()
        if data.get('code') != 200:
            return f"查询失败: {data.get('msg', '未知错误')}"
            
        records = data.get('data', {}).get('list', [])
        if not records:
            return "暂无提现记录"
            
        # 格式化提现记录
        result = "=====提现记录=====\n"
        for record in records:
            status = record.get('status')
            status_text = {
                '0': '处理中',
                '1': '成功',
                '2': '失败'
            }.get(str(status), '未知状态')
            
            amount = record.get('amount', 0)
            # 将时间转换为24小时制格式
            date_str = record.get('dateTime', '')
            if date_str:
                try:
                    # 解析原始时间字符串并转换为北京时间
                    dt = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                    beijing_tz = timezone(timedelta(hours=8))
                    dt = dt.replace(tzinfo=timezone.utc).astimezone(beijing_tz)
                    # 格式化为24小时制
                    date_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    date_time = date_str.replace('T', ' ').split('.')[0]
            else:
                date_time = '未知时间'
            
            result += (
                f"💰 金额: {amount}元\n"
                f"⏰ 时间: {date_time}\n"
                f"📝 状态: {status_text}\n"
                "-------------------\n"
            )
        return result.rstrip("-------------------\n") + "\n=================="
        
    except Exception as e:
        return f"查询提现记录失败: {str(e)}"

def query():
    """查询酷我账号状态"""
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        for account in accounts:
            try:
                accountVip = middleware.bucketGet(bucket='dd_Kuwo_Vip', key=account) or ''
                Token = middleware.bucketGet(bucket='dd_Kuwo_account', key=account)
                if not Token:
                    sender.reply(f'【账号】Token获取失败')
                    continue

                pointValue, todaycoin = cx(Token)
                if isinstance(pointValue, str):
                    sender.reply(f'【账号】{pointValue}')
                    continue

                phone = Token.split('#')[3]  # 从Token中获取手机号
                phone_masked = phone[:3] + '*' * 4 + phone[7:]  # 手机号脱敏

                if len(accountVip) == 0:
                    sender.reply(f'【{phone_masked}】账号未授权')
                    continue
                elif accountVip < today_time:
                    sender.reply(f'【{phone_masked}】云授权过期')
                    continue
                else:
                    # 获取提现记录
                    withdraw_history = query_withdraw_history(Token)
                    
                    sender.reply(
                        "=====账号详情=====\n"
                        f"📱 账号: {phone_masked}\n"
                        f"💰 当前金币: {pointValue}\n"
                        f"✨ 今日收益: {todaycoin}\n"
                        f"⏰ 授权期限: {accountVip}\n"
                        "===================\n"
                        f"{withdraw_history}"
                    )

            except Exception as e:
                try:
                    phone_masked = phone[:3] + '*' * 4 + phone[7:]
                except:
                    phone_masked = "未知账号"
                sender.reply(f'【{phone_masked}】查询出错: {str(e)}')
    else:
        sender.reply('未绑定酷我账号')

def cx(token):
    """查询酷我音乐金币"""
    try:
        # 解析登录参数
        values = token.split('#')
        if len(values) != 4:
            return "登录参数格式错误", 0
            
        appuid = values[0]
        devid = values[1]
        loginSid = values[2]
        phone = values[3]

        # 查询总金币
        url = "https://integralapi.kuwo.cn/api/v1/online/sign/new/todayStatus"
        headers = {
            'Host': 'integralapi.kuwo.cn',
            'Accept': '*/*',
            'Cookie': f'tmeAppID=kwplayer;loginSid={loginSid};ct=1;newdevicelevel=0;deviceScore=0;loginUid={appuid};cv=11120;chid=TJ;os_ver=17.7.2;user={devid};nettype=WiFi;appUid={appuid}',
            'User-Agent': 'KWPlayer/11.1.2 (iPhone; iOS 17.7.2; Scale/3.00)',
            'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
        
        params = {
            'uuid': devid,
            'newver': '3',
            'corp': 'kuwo',
            'uid': appuid,
            'loginSid': loginSid,
            'plat': 'ip',
            'source': 'kwplayer_ip_11.1.2.0_TJ.ipa',
            'loginUid': appuid,
            'prod': 'kwplayer_ip_11.1.2.0',
            'user': devid,
            'locationid': '1'
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return f"HTTP错误: {response.status_code}", 0
            
        r = response.json()
        if r.get('code') != 200:
            return f"查询失败: {r.get('msg', '未知错误')}", 0
            
        remain_score = r['data']['remainScore']  # 总金币

        # 查询今日金币明细
        detail_url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/earningSignIn/userGoldDetail"
        detail_headers = {
            'Host': 'integralapi.kuwo.cn',
            'Accept': 'application/json, text/plain, */*',
            'Origin': 'https://h5app.kuwo.cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KWMusic/11.1.2.0',
            'Accept-Language': 'zh-CN,zh-Hans;q=0.9'
        }
        
        today_coin = 0
        page = 1
        has_more = True
        beijing_tz = timezone(timedelta(hours=8))
        today = datetime.now(beijing_tz).strftime("%Y-%m-%d")
        
        while has_more:
            detail_params = {
                'userId': appuid,
                'loginSid': loginSid,
                'pn': str(page),
                'rn': '50'
            }
            
            detail_response = requests.get(detail_url, headers=detail_headers, params=detail_params)
            if detail_response.status_code != 200:
                break
                
            detail_data = detail_response.json()
            if detail_data.get('code') != 200:
                break
                
            records = detail_data.get('data', {}).get('list', [])
            if not records:
                break
                
            found_today = False
            for item in records:
                date_str = item.get('dateTime', '')
                if date_str:
                    try:
                        # 解析UTC时间并转换为北京时间
                        utc_time = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                        utc_time = utc_time.replace(tzinfo=timezone.utc)
                        beijing_time = utc_time.astimezone(beijing_tz)
                        record_date = beijing_time.strftime("%Y-%m-%d")
                        
                        if record_date == today:
                            found_today = True
                            amount = int(item.get('amount', 0))
                            if amount > 0:  # 只计算正数（收入）
                                today_coin += amount
                    except:
                        continue
                    
            # 如果这一页没有找到今天的记录，就停止查询
            if not found_today:
                has_more = False
            else:
                page += 1

        return remain_score, today_coin
        
    except Exception as e:
        return f"查询异常: {str(e)}", 0

# 其他必要的辅助函数
def ValueErrors(value, count):
    """验证输入值的有效性"""
    if value is None or value == '':
        sender.reply('输入超时！')
        exit(0)
    elif value.lower() == 'q':  # 添加对输入q的处理
        sender.reply('退出操作！')
        exit(0)
        
    try:
        value = int(value)
        if value > count or value == 0:
            sender.reply('输入错误！')
            exit(0)
        return value
    except ValueError:
        sender.reply('输入错误！')
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

def Addenvs(osname, value, account, phone):
    """添加或更新环境变量（支持青龙/呆呆面板）"""
    if use_daidai:
        env_id = dd_allenvs(osname, account)
        if env_id is None:
            return DDcreate(osname, value, account, phone)
        else:
            return DDupdate(osname, value, account, env_id, phone)

    try:
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
                remarks = envs.get('remarks', '')
                if remarks and account in remarks and osname == envs['name']:
                    qlid = envs['id']
                    break
        else:
            sender.reply('连接青龙获取变量失败')
            return False
            
        if qlid is None:
            return QLzt(osname, value, account, phone)
        else:
            return QLupdate(osname, value, account, qlid, phone)
    except Exception as e:
        sender.reply(f'添加/更新青龙变量失败: {str(e)}')
        return False

def QLzt(osname, value, account, phone):
    """添加青龙变量"""
    try:
        # 获取账号到期时间
        expire_date = middleware.bucketGet('dd_Kuwo_Vip', account) or '未授权'
        
        url = f"{QLurl}/open/envs"
        data = [{
            "value": value,
            "name": osname,
            "remarks": f'酷我:{account}丨用户:{userid}丨手机:{phone}丨到期:{expire_date}'
        }]
        headers = {
            "Authorization": f"Bearer {qltoken}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            sender.reply("添加变量失败")
            return False
            
        result = response.json()
        if "value must be unique" in response.text:
            return True
            
        if result.get('code') == 200:
            return True
        else:
            sender.reply(f"添加变量失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        sender.reply(f"添加青龙变量错误: {str(e)}")
        return False

def QLupdate(osname, value, account, qlid, phone):
    """更新青龙变量"""
    try:
        # 获取账号到期时间
        expire_date = middleware.bucketGet('dd_Kuwo_Vip', account) or '未授权'
        
        url = f"{QLurl}/open/envs"
        data = {
            "value": value,
            "name": osname,
            "remarks": f'酷我:{account}丨用户:{userid}丨手机:{phone}丨到期:{expire_date}',
            "id": qlid
        }
        headers = {
            "Authorization": f"Bearer {qltoken}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        
        response = requests.put(url, headers=headers, data=json.dumps(data))
        if response.status_code != 200:
            sender.reply('更新变量失败')
            return False
            
        result = response.json()
        if result.get('code') == 200:
            return True
        else:
            sender.reply(f"更新变量失败: {result.get('message', '未知错误')}")
            return False
            
    except Exception as e:
        sender.reply(f'更新变量失败: {str(e)}')
        return False

def allenvs(osname, account):
    """获取所有环境变量（支持青龙/呆呆面板）"""
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

def delenvs(id):
    """删除环境变量（支持青龙/呆呆面板）"""
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

def zf(project, me_as_int, accountVip, account, token, phone):
    """支付处理"""
    # 获取原始登录信息
    login_info = middleware.bucketGet('dd_Kuwo_login', account)
    if not login_info:
        sender.reply('获取账号登录信息失败')
        return False

    # 计算支付金额
    money = Decimal(me_as_int) * Decimal(KuwoVipmoney)

    # 获取用户积分信息
    user_points = int(middleware.bucketGet('dd_sign_points', userid) or '0')
    jfsl = middleware.bucketGet('dd_Kuwo_PluginsData', 'Kuwocoin')
    
    # 检查是否有人正在支付
    zfzt = sender.atWaitPay()
    if zfzt:
        sender.reply('当前有人正在支付,请稍后再试！')
        exit(0)

    # 如果价格为0，直接授权
    if money == 0:
        try:
            # 计算新的到期时间
            if accountVip and accountVip not in ['未授权', '授权过期'] and accountVip > today_time:
                start_date = datetime.strptime(accountVip, "%Y-%m-%d")
            else:
                start_date = datetime.now()
            
            # 使用配参中的天数计算到期时间
            days_per_month = int(middleware.bucketGet('dd_Kuwo_PluginsData', 'days_per_month') or '30')
            new_expire_date = (start_date + timedelta(days=me_as_int * days_per_month)).strftime("%Y-%m-%d")
            
            # 更新授权时间
            middleware.bucketSet('dd_Kuwo_Vip', account, new_expire_date)
            
            # 更新青龙变量
            if not Addenvs(osname=osname, value=login_info, account=account, phone=phone):
                sender.reply("警告：青龙变量更新失败，但授权已完成")
                
            msg = (
                "=====授权完成=====\n"
                f"🎈名称:{project}\n"
                f"🎉数量:{me_as_int}月\n"
                f"💰费用:免费\n"
                f"📅到期时间:{new_expire_date}\n"
                "=================="
            )
            sender.reply(msg)
            return True
        except Exception as e:
            sender.reply(f"授权更新失败: {str(e)}")
            exit(0)

    # 获取赞赏码链接
    zsm = middleware.bucketGet('dd_Kuwo_PluginsData', 'zsm')
    if not zsm:
        sender.reply('未配置收款方式，请联系管理员')
        exit(0)

    # 计算所需积分
    total_points = 0
    if jfsl:
        try:
            total_points = int(jfsl) * me_as_int
        except:
            total_points = 0

    # 显示支付选项
    if total_points > 0:
        sender.reply(
            "=====支付方式=====\n"
            f"1️⃣ 积分支付: {total_points}积分\n"
            f"2️⃣ 微信支付: {money}元\n"
            "请选择支付方式(1/2):\n"
            "⚠️ 输入q退出支付"
        )
        choice = sender.input(60000, 1, False)
        
        if not choice:
            sender.reply('输入超时')
            return False
        elif choice.lower() == 'q':
            sender.reply('退出支付')
            return False
        elif choice == '1':
            # 检查用户积分是否足够
            current_points = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            if current_points < total_points:
                sender.reply(
                    "=====积分不足=====\n"
                    f"💰 当前积分: {current_points}\n"
                    f"💵 所需积分: {total_points}\n"
                    f"❌ 积分不足，请选择其他支付方式\n"
                    "==================="
                )
                # 询问是否使用微信支付
                sender.reply(
                    "=====支付选择=====\n"
                    "是否使用微信支付继续?\n"
                    "[y]继续 | [n]取消\n"
                    "=================="
                )
                if yesornos():
                    return handle_wx_payment(zsm, money, me_as_int, accountVip, account, token, phone, login_info, project)
                return False

            # 处理积分支付
            sender.reply(
                "=====积分支付=====\n"
                f"💰 当前积分: {current_points}\n"
                f"💵 所需积分: {total_points}\n"
                f"💡 购买时长: {me_as_int}月\n"
                "是否确认支付?\n"
                "[y]确认 | [n]取消"
            )
            if yesornos():
                try:
                    # 再次验证积分是否足够（防止支付过程中积分变动）
                    final_points = int(middleware.bucketGet('dd_sign_points', userid) or '0')
                    if final_points < total_points:
                        sender.reply(
                            "=====支付失败=====\n"
                            "❌ 积分不足，无法完成支付\n"
                            "==================="
                        )
                        return False
                    
                    new_balance = final_points - total_points
                    middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                    accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                    middleware.bucketSet('dd_Kuwo_Vip', account, accountVip)
                    Addenvs(osname=osname, value=login_info, account=account, phone=phone)
                    
                    # 发送支付成功消息
                    msg = (
                        "=====支付成功=====\n"
                        f"🎈 商品: 酷我音乐授权\n"
                        f"🎉 时长: {me_as_int}月\n"
                        f"💰 支付: {total_points}积分\n"
                        f"💎 剩余: {new_balance}积分\n"
                        "==================="
                    )
                    sender.reply(msg)
                    return True

                except Exception as e:
                    sender.reply(f"授权更新失败: {str(e)}")
                    return False
            else:
                sender.reply('已取消积分支付')
                return False
        elif choice == '2':
            # 处理微信支付
            return handle_wx_payment(zsm, money, me_as_int, accountVip, account, token, phone, login_info, project)
        else:
            sender.reply('输入无效')
            return False
    else:
        # 直接进行微信支付
        return handle_wx_payment(zsm, money, me_as_int, accountVip, account, token, phone, login_info, project)

def handle_wx_payment(zsm, money, me_as_int, accountVip, account, token, phone, login_info, project):
    """处理微信支付"""
    # 显示收款二维码
    sender.reply(
        "=====订单信息=====\n"
        f"🎈名称: 酷我授权\n"
        f"🎉数量: {me_as_int}月\n"
        f"💰应付: {money}元\n"
        "⚠️ 输入q退出支付\n"
        "==================="
    )
    sender.replyImage(zsm)

    # 等待支付结果
    ddzf = sender.waitPay("q", 100 * 1000)
    
    if str(ddzf) == 'q':
        sender.reply('退出支付')
        return False

    try:
        # 处理支付结果
        Money = 0
        pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(ddzf, dict):
            Money = Decimal(str(ddzf.get('Money', 0) or ddzf.get('money', 0)))  # 使用 Decimal
            pay_time = ddzf.get('Time', '') or ddzf.get('time', '')
            if pay_time:
                pay_time = pay_time.replace('T', ' ').split('.')[0]
            else:
                pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(ddzf, str):
            if "二维码赞赏到账" in ddzf:
                try:
                    amount_str = ddzf.split("收款金额￥")[1].split("\n")[0]
                    Money = Decimal(str(amount_str))  # 使用 Decimal
                    time_str = ddzf.split("到账时间")[1].split("\n")[0].strip()
                    pay_time = time_str
                except Exception as e:
                    sender.reply(f"解析收款信息失败: {str(e)}")
                    return False
            else:
                try:
                    json_data = json.loads(ddzf)
                    Money = Decimal(str(json_data.get('Money', 0) or json_data.get('money', 0)))  # 使用 Decimal
                    pay_time = json_data.get('Time', '') or json_data.get('time', '')
                    if pay_time:
                        pay_time = pay_time.replace('T', ' ').split('.')[0]
                    else:
                        pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                except:
                    sender.reply("支付结果格式错误")
                    return False
        else:
            sender.reply("未知的支付结果格式")
            return False

        # 验证支付金额
        if Money <= 0:
            sender.reply("支付金额无效")
            return False

        # 使用 Decimal 进行精确比较
        money = Decimal(str(money))
        if Money == money:  # 改为精确比较
            try:
                # 计算新的到期时间
                if accountVip and accountVip not in ['未授权', '授权过期'] and accountVip > today_time:
                    start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                else:
                    start_date = datetime.now()
                
                # 使用配参中的天数计算到期时间
                days_per_month = int(middleware.bucketGet('dd_Kuwo_PluginsData', 'days_per_month') or '30')
                new_expire_date = (start_date + timedelta(days=me_as_int * days_per_month)).strftime("%Y-%m-%d")
                
                # 更新授权时间
                middleware.bucketSet('dd_Kuwo_Vip', account, new_expire_date)
                
                # 更新青龙变量
                if not Addenvs(osname=osname, value=login_info, account=account, phone=phone):
                    sender.reply("警告：青龙变量更新失败，但授权已完成")
                    
                # 发送支付成功消息
                msg = (
                    "=====订单完成=====\n"
                    f"🎈名称:{project}\n"
                    f"🎉数量:{me_as_int}月\n"
                    f"💰支付金额:{Money}元\n"
                    f"⏰支付时间:{pay_time}\n"
                    f"📅到期时间:{new_expire_date}\n"
                    "=================="
                )
                sender.reply(msg)
                return True

            except Exception as e:
                sender.reply(f"授权更新失败: {str(e)}")
                return False

        else:
            sender.reply(f'支付金额错误\n应付:{money}元\n实付:{Money}元\n请联系管理员处理退款！')
            return False

    except Exception as e:
        sender.reply(f"处理支付结果时出错: {str(e)}")
        return False

def yesornos():
    """确认选择"""
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

def kuwo_auth():
    """酷我授权功能"""
    if not sender.isAdmin():
        sender.reply("您没有权限执行此操作！")
        exit(0)
        
    sender.reply(
        "=====酷我授权=====\n"
        "  [1] 一键授权所有用户\n" 
        "  [2] 单独授权用户\n"
        "-------------------\n"
        "⚠️ 输入q退出操作\n"
        "=================="
    )
    xz = sender.input(60000, 1, False)
    
    if xz == 'q' or xz == 'Q':
        sender.reply("退出操作")
        return
    elif xz is None or xz not in ['1', '2']:
        sender.reply("输入无效")
        return

    if xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('dd_Kuwo_bind')
        if not users:
            sender.reply("未找到任何绑定的酷我账号")
            return
    else:
        # 单独授权用户
        sender.reply(
            "=====用户授权=====\n"
            "📝 请输入需要授权的用户ID\n"
            "💡 通过发送myuid获得\n"
            "⚠️ 输入q退出操作\n"
            "=================="
        )
        myuid = sender.input(60000, 1, False)
        if not myuid or myuid.lower() == 'q':
            sender.reply("退出操作")
            return
            
        # 获取用户的账号列表
        accountlist = middleware.bucketGet('dd_Kuwo_bind', myuid)
        if not accountlist or accountlist == '{}':
            sender.reply(f"未找到用户 {myuid} 的酷我账号信息!")
            return
            
        try:
            accounts = eval(accountlist)
            msg = "=====账号列表=====\n[0] 授权所有账号\n-------------------\n"
            
            for i, account in enumerate(accounts, 1):
                accountVip = middleware.bucketGet('dd_Kuwo_Vip', account) or '未授权'
                Token = middleware.bucketGet('dd_Kuwo_account', account)
                phone = Token.split('#')[3] if Token else "未知"
                phone = phone[:3] + '*' * 4 + phone[7:] if len(phone) == 11 else phone
                msg += (
                    f"[{i}] 账号信息\n"
                    f"📱 账号: {phone}\n"
                    f"⏰ 到期: {accountVip}\n"
                    f"-------------------\n"
                )
            
            msg += "⚠️ 输入q退出操作"
            sender.reply(msg)
            
            # 选择要授权的账号
            choice = sender.input(60000, 1, False)
            if not choice or choice.lower() == 'q':
                sender.reply("退出操作")
                return
                
            try:
                choice = int(choice)
                if choice < 0 or choice > len(accounts):
                    sender.reply("输入的序号无效")
                    return
            except:
                sender.reply("输入的序号无效")
                return
                
            # 确定要授权的账号列表
            users = [myuid]
            if choice == 0:
                target_accounts = accounts
            else:
                target_accounts = [accounts[choice-1]]
                
        except Exception as e:
            sender.reply(f"处理账号列表时出错: {str(e)}")
            return

    # 获取授权天数
    sender.reply(
        "=====授权天数=====\n"
        "📝 请输入要授权的天数\n"
        "⚠️ 输入q退出操作\n"
        "=================="
    )
    days = sender.input(60000, 1, False)
    if days == 'q' or days == 'Q':
        sender.reply("退出操作")
        return
    elif days is None:
        sender.reply("输入超时")
        return
        
    try:
        days = int(days)
        if days <= 0:
            sender.reply("授权天数必须大于0")
            return
    except:
        sender.reply("输入的天数无效，必须是数字！")
        return

    # 使用字典来存储计数，这样可以在函数间共享
    stats = {
        'success': 0,
        'fail': 0,
        'fail_accounts': []
    }

    # 处理授权
    if xz == '1':  # 一键授权所有用户
        for user in users:
            accountlist = middleware.bucketGet('dd_Kuwo_bind', key=user)
            if not accountlist or accountlist == '{}':
                continue
                
            try:
                accounts = eval(accountlist)
                for account in accounts:
                    try:
                        # 获取原始登录信息（手机号#密码）
                        login_info = middleware.bucketGet('dd_Kuwo_login', account)
                        if not login_info:
                            stats['fail'] += 1
                            stats['fail_accounts'].append(f"账号:{account}(登录信息获取失败)")
                            continue
                            
                        # 获取手机号
                        phone = login_info.split('#')[0]

                        # 计算新的到期时间
                        current_vip = middleware.bucketGet('dd_Kuwo_Vip', account)
                        current_date = datetime.now()
                        
                        if current_vip and current_vip > current_date.strftime("%Y-%m-%d"):
                            start_date = datetime.strptime(current_vip, "%Y-%m-%d")
                        else:
                            start_date = current_date

                        new_expire_date = (start_date + timedelta(days=days)).strftime("%Y-%m-%d")
                        
                        # 更新授权时间
                        middleware.bucketSet('dd_Kuwo_Vip', account, new_expire_date)
                        
                        # 更新青龙变量 - 使用原始登录信息
                        if Addenvs(osname=osname, value=login_info, account=account, phone=phone):
                            stats['success'] += 1
                        else:
                            stats['fail'] += 1
                            stats['fail_accounts'].append(f"账号:{account}(青龙变量更新失败)")
                            
                    except Exception as e:
                        stats['fail'] += 1
                        stats['fail_accounts'].append(f"账号:{account}(处理失败:{str(e)})")
            except Exception as e:
                sender.reply(f"处理用户 {user} 的账号列表时出错: {str(e)}")
                continue
    else:  # 单独授权指定账号
        for account in target_accounts:
            try:
                process_auth(account, days, stats)
            except Exception as e:
                stats['fail'] += 1
                stats['fail_accounts'].append(f"账号:{account}(处理失败:{str(e)})")

    # 生成结果报告
    msg = (
        "=====授权结果=====\n"
        f"✅ 成功: {stats['success']}个账号\n"
        f"❌ 失败: {stats['fail']}个账号\n"
        f"⏰ 授权天数: {days}天\n"
    )
    
    if stats['fail_accounts']:
        msg += "\n失败详情:\n" + "\n".join(stats['fail_accounts'][:5])  # 只显示前5个失败账号
        if len(stats['fail_accounts']) > 5:
            msg += f"\n... 等共{len(stats['fail_accounts'])}个失败账号"
            
    msg += "\n=================="
    sender.reply(msg)

def process_auth(account, days, stats):
    """处理单个账号的授权"""
    try:
        # 获取原始登录信息（手机号#密码）
        login_info = middleware.bucketGet('dd_Kuwo_login', account)
        if not login_info:
            stats['fail'] += 1
            stats['fail_accounts'].append(f"账号:{account}(登录信息获取失败)")
            return
            
        # 获取手机号
        phone = login_info.split('#')[0]

        # 计算新的到期时间
        current_vip = middleware.bucketGet('dd_Kuwo_Vip', account)
        current_date = datetime.now()
        
        if current_vip and current_vip > current_date.strftime("%Y-%m-%d"):
            start_date = datetime.strptime(current_vip, "%Y-%m-%d")
        else:
            start_date = current_date

        new_expire_date = (start_date + timedelta(days=days)).strftime("%Y-%m-%d")
        
        # 更新授权时间
        middleware.bucketSet('dd_Kuwo_Vip', account, new_expire_date)
        
        # 更新青龙变量 - 使用原始登录信息
        if Addenvs(osname=osname, value=login_info, account=account, phone=phone):
            stats['success'] += 1
        else:
            stats['fail'] += 1
            stats['fail_accounts'].append(f"账号:{account}(青龙变量更新失败)")
            
    except Exception as e:
        stats['fail'] += 1
        stats['fail_accounts'].append(f"账号:{account}(处理失败:{str(e)})")

def tutorial():
    """显示酷我使用教程"""
    tutorial_text = (
        "=====酷我教程=====\n"
        "🎵 基础指令:\n"
        "1️⃣ 酷我登录 - 绑定账号\n" 
        "2️⃣ 酷我查询 - 查看状态\n"
        "3️⃣ 酷我管理 - 管理账号\n"
        "-------------------\n"
        "📝 使用说明:\n"
        "1. 发送[酷我登录]绑定账号\n"
        "2. 按提示输入手机号和密码\n"
        "3. 登录成功后可以管理账号\n"
        "4. 定时签到获取金币奖励\n"
        "5. 金币达到门槛可以提现\n"
        "-------------------\n"
        "⚠️ 注意事项:\n"
        "1. 建议私聊登录更安全\n"
        "2. 密码不会被保存记录\n"
        "3. 定期更新账号保活\n"
        "=================="
    )
    sender.reply(tutorial_text)

def withdraw_tutorial():
    """显示酷我提现教程"""
    txjc = (
        "=====提现说明=====\n"
        "💰 提现说明:\n"
        "1、指令：酷我提现\n"
        "2、2元提现需要20000金币\n"
        "3、10元提现需要100000金币\n"
        "4、每天限提现一次\n"
        "-------------------\n"
        "🎯 登录说明:\n"
        "1、使用手机号和密码登录\n"
        "2、格式: 手机号#密码\n"
        "3、建议私聊操作更安全\n"
        "=================="
    )
    sender.reply(txjc)

def query_today_withdrawals():
    """查询今日提现情况"""
    if not sender.isAdmin():
        sender.reply("您没有权限执行此操作！")
        exit(0)
        
    # 获取所有绑定的用户
    all_users = middleware.bucketAllKeys('dd_KuwoTX_bind')
    if not all_users:
        sender.reply("未找到任何绑定的酷我提现账号")
        return
        
    # 统计变量
    stats = {
        'total_accounts': 0,  # 已授权账号总数
        'withdrawn_accounts': 0,  # 已提现账号数
        'total_amount': 0,  # 提现总金额
        'processing_accounts': 0,  # 处理中的提现数
        'failed_accounts': 0  # 失败的提现数
    }
    
    # 获取今天的日期（北京时间）
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).strftime("%Y-%m-%d")
    
    # 遍历所有用户的账号
    for user in all_users:
        try:
            accountlist = middleware.bucketGet('dd_KuwoTX_bind', key=user)
            if not accountlist or accountlist == '{}':
                continue
                
            accounts = eval(accountlist)
            for account in accounts:
                # 检查账号是否已授权且未过期
                accountVip = middleware.bucketGet('dd_KuwoTX_Vip', key=account) or ''
                if not accountVip or accountVip <= today:
                    continue
                    
                stats['total_accounts'] += 1
                
                # 获取账号token
                Token = middleware.bucketGet('dd_KuwoTX_account', key=account)
                if not Token:
                    continue
                    
                # 获取提现记录
                try:
                    values = Token.split('#')
                    if len(values) != 4:
                        continue
                        
                    loginUid = values[0]
                    loginSid = values[2]
                    
                    # 查询提现记录
                    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/withdrawDetails"
                    params = {
                        'loginUid': loginUid,
                        'loginSid': loginSid,
                        'pn': '1',  # 第一页
                        'rn': '50'  # 增加每页记录数以确保获取所有今日记录
                    }
                    
                    headers = {
                        'Host': 'integralapi.kuwo.cn',
                        'Accept': 'application/json, text/plain, */*',
                        'Origin': 'https://h5app.kuwo.cn',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KWMusic/11.1.2.0',
                        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                        'Referer': 'https://h5app.kuwo.cn/'
                    }
                    
                    response = requests.get(url, params=params, headers=headers)
                    if response.status_code != 200:
                        continue
                        
                    data = response.json()
                    if data.get('code') != 200:
                        continue
                        
                    records = data.get('data', {}).get('list', [])
                    
                    # 检查今日提现记录
                    has_withdrawal_today = False
                    for record in records:
                        date_str = record.get('dateTime', '') or record.get('createTime', '')
                        if not date_str:
                            continue
                            
                        try:
                            # 解析UTC时间并转换为北京时间
                            if 'T' in date_str:
                                utc_time = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                            else:
                                utc_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            utc_time = utc_time.replace(tzinfo=timezone.utc)
                            beijing_time = utc_time.astimezone(beijing_tz)
                            record_date = beijing_time.strftime("%Y-%m-%d")
                            
                            if record_date == today:
                                has_withdrawal_today = True
                                amount = float(record.get('amount', 0))
                                status = str(record.get('status', ''))
                                
                                if status == '1':  # 成功
                                    stats['withdrawn_accounts'] += 1
                                    stats['total_amount'] += amount
                                elif status == '0':  # 处理中
                                    stats['processing_accounts'] += 1
                                elif status == '2':  # 失败
                                    stats['failed_accounts'] += 1
                                break  # 找到今日记录后跳出循环
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            continue
            
    # 生成报告
    msg = (
        "=====提现统计=====\n"
        f"📅 统计日期: {today}\n"
        f"📊 总账号: {stats['total_accounts']}个\n"
        f"✅ 提现成功: {stats['withdrawn_accounts']}个\n"
        f"⏳ 处理中: {stats['processing_accounts']}个\n"
        f"💵 提现总额: {stats['total_amount']}元\n"
        "=================="
    )
    
    sender.reply(msg)

def clean_expired_accounts():
    """清理过期账号的青龙变量"""
    if not sender.isAdmin():
        sender.reply("您没有权限执行此操作！")
        exit(0)
        
    # 统计变量
    stats = {
        'total': 0,
        'expired': 0,
        'cleaned': 0,
        'failed': []
    }
    
    try:
        # 获取所有 VIP 记录
        all_vips = middleware.bucketAll('dd_Kuwo_Vip')
        if not all_vips:
            sender.reply("未找到任何 VIP 记录")
            return
            
        # 获取今天的日期
        today = datetime.now().date()
        
        # 获取所有面板变量
        all_ql_envs = {}
        if use_daidai:
            url = f"{panel_url}/api/envs"
            headers = get_dd_headers()
            params = {"keyword": osname, "page_size": 1000}
            response = requests.get(url=url, headers=headers, params=params)
            if response.status_code != 200:
                sender.reply(f"获取呆呆面板变量失败: HTTP {response.status_code}")
                return
            data_list = response.json().get('data', [])
            if isinstance(data_list, list):
                for env in data_list:
                    if env.get('name') == osname:
                        remarks = env.get('remarks', '')
                        if remarks and '酷我:' in remarks:
                            try:
                                account_info = remarks.split('酷我:')[1].split('丨')[0]
                                all_ql_envs[account_info] = {
                                    'id': env['id'],
                                    'value': env.get('value', '')
                                }
                            except:
                                continue
        else:
            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json"
            }
            
            response = requests.get(url=url, headers=headers)
            if response.status_code != 200:
                sender.reply(f"获取青龙变量失败: HTTP {response.status_code}")
                return
                
            ql_data = response.json()
            if ql_data['code'] != 200:
                sender.reply(f"获取青龙变量失败: {ql_data.get('message', '未知错误')}")
                return
                
            # 过滤出酷我相关的变量，并按照remarks中的账号信息建立索引
            for env in ql_data['data']:
                if env['name'] == osname:
                    remarks = env.get('remarks', '')
                    if remarks and '酷我:' in remarks:
                        try:
                            account_info = remarks.split('酷我:')[1].split('丨')[0]
                            all_ql_envs[account_info] = {
                                'id': env['id'],
                                'value': env['value']
                            }
                        except:
                            continue
        
        # 遍历所有 VIP 记录
        for account, vip_date in all_vips.items():
            stats['total'] += 1
            need_clean = False
            
            try:
                # 检查授权状态
                if not vip_date or vip_date in ['未授权', '授权过期']:
                    need_clean = True
                    stats['expired'] += 1
                else:
                    try:
                        expire_date = datetime.strptime(vip_date, "%Y-%m-%d").date()
                        if expire_date <= today:
                            need_clean = True
                            stats['expired'] += 1
                    except ValueError:
                        need_clean = True
                        stats['expired'] += 1
                
                if need_clean:
                    # 查找对应的面板变量
                    env_info = all_ql_envs.get(account)
                    if env_info:
                        try:
                            if use_daidai:
                                # 删除呆呆面板变量
                                del_url = f"{panel_url}/api/envs/{env_info['id']}"
                                del_headers = get_dd_headers()
                                del_response = requests.delete(del_url, headers=del_headers)
                            else:
                                # 删除青龙变量
                                del_url = f"{QLurl}/open/envs"
                                del_headers = {
                                    "Authorization": f"Bearer {qltoken}",
                                    "accept": "application/json",
                                    "Content-Type": "application/json"
                                }
                                del_response = requests.delete(
                                    del_url, 
                                    headers=del_headers, 
                                    json=[env_info['id']]
                                )
                            
                            if del_response.status_code == 200:
                                stats['cleaned'] += 1
                            else:
                                stats['failed'].append(f"{account}: 删除失败(HTTP {del_response.status_code})")
                        except Exception as e:
                            stats['failed'].append(f"{account}: 删除异常({str(e)})")
                        
                    # 删除账号相关的其他数据
                    middleware.bucketDel(bucket='dd_Kuwo_account', key=account)
                    middleware.bucketDel(bucket='dd_Kuwo_Vip', key=account)
                    
                    # 从用户绑定列表中移除
                    users = middleware.bucketAllKeys('dd_Kuwo_bind')
                    for user in users:
                        try:
                            user_accounts = eval(middleware.bucketGet('dd_Kuwo_bind', user) or '[]')
                            if account in user_accounts:
                                user_accounts.remove(account)
                                if user_accounts:
                                    middleware.bucketSet('dd_Kuwo_bind', user, str(user_accounts))
                                else:
                                    middleware.bucketDel('dd_Kuwo_bind', user)
                        except:
                            continue
                        
            except Exception as e:
                stats['failed'].append(f"{account}: 处理异常({str(e)})")
                continue
                
    except Exception as e:
        sender.reply(f"清理过程出错: {str(e)}")
        return
        
    # 生成清理报告
    msg = (
        "=====清理报告=====\n"
        f"📊 总账号: {stats['total']}个\n"
        f"⚠️ 已过期: {stats['expired']}个\n"
        f"🧹 已清理: {stats['cleaned']}个\n"
    )
    
    if stats['failed']:
        msg += "\n失败详情:\n" + "\n".join(stats['failed'][:5])  # 只显示前5个失败记录
        if len(stats['failed']) > 5:
            msg += f"\n... 等共{len(stats['failed'])}个失败记录"
            
    msg += "\n=================="
    sender.reply(msg)

def push(user, phone, message):
    """推送消息到各个平台
    
    Args:
        user: 用户ID
        phone: 手机号(已脱敏)
        message: 推送消息内容
    """
    push_msg = f"""
=====酷我账号通知=====
📱 账号: {phone}
📢 消息: {message}
=================="""

    # 发送到各个平台
    platforms = ['wb', 'tg', 'qq', 'qb', 'wx']
    for platform in platforms:
        try:
            middleware.push(platform, '', user, '', push_msg)
        except Exception as e:
            print(f"推送到{platform}失败: {str(e)}")

def check_withdrawal_status():
    """检查提现状态并推送成功提现的通知"""
    # 获取所有绑定的用户
    all_users = middleware.bucketAllKeys('dd_KuwoTX_bind')
    if not all_users:
        return
        
    # 获取今天的日期（北京时间）
    beijing_tz = timezone(timedelta(hours=8))
    today = datetime.now(beijing_tz).strftime("%Y-%m-%d")
    
    # 遍历所有用户的账号
    for user in all_users:
        try:
            accountlist = middleware.bucketGet('dd_KuwoTX_bind', key=user)
            if not accountlist or accountlist == '{}':
                continue
                
            accounts = eval(accountlist)
            for account in accounts:
                # 检查账号是否已授权且未过期
                accountVip = middleware.bucketGet('dd_KuwoTX_Vip', key=account) or ''
                if not accountVip or accountVip <= today:
                    continue
                    
                # 获取账号token
                Token = middleware.bucketGet('dd_KuwoTX_account', key=account)
                if not Token:
                    continue
                    
                # 获取提现记录
                try:
                    values = Token.split('#')
                    if len(values) != 4:
                        continue
                        
                    loginUid = values[0]
                    loginSid = values[2]
                    phone = values[3]  # 获取手机号
                    phone_masked = phone[:3] + '*' * 4 + phone[7:]  # 脱敏手机号
                    
                    # 查询提现记录
                    url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/withdrawDetails"
                    params = {
                        'loginUid': loginUid,
                        'loginSid': loginSid,
                        'pn': '1',  # 第一页
                        'rn': '10'  # 获取最近10条记录
                    }
                    
                    headers = {
                        'Host': 'integralapi.kuwo.cn',
                        'Accept': 'application/json, text/plain, */*',
                        'Origin': 'https://h5app.kuwo.cn',
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 KWMusic/11.1.2.0',
                        'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                        'Referer': 'https://h5app.kuwo.cn/'
                    }
                    
                    response = requests.get(url, params=params, headers=headers)
                    if response.status_code != 200:
                        continue
                        
                    data = response.json()
                    if data.get('code') != 200:
                        continue
                        
                    records = data.get('data', {}).get('list', [])
                    
                    # 检查今日提现记录
                    for record in records:
                        date_str = record.get('dateTime', '') or record.get('createTime', '')
                        if not date_str:
                            continue
                            
                        try:
                            # 解析UTC时间并转换为北京时间
                            if 'T' in date_str:
                                utc_time = datetime.strptime(date_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
                            else:
                                utc_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            utc_time = utc_time.replace(tzinfo=timezone.utc)
                            beijing_time = utc_time.astimezone(beijing_tz)
                            record_date = beijing_time.strftime("%Y-%m-%d")
                            record_time = beijing_time.strftime("%H:%M:%S")
                            
                            # 检查是否是今天的记录
                            if record_date == today:
                                amount = float(record.get('amount', 0))
                                status = str(record.get('status', ''))
                                
                                # 检查是否是成功提现的记录
                                if status == '1':  # 成功
                                    # 检查是否已经推送过这条记录
                                    record_id = record.get('id', '')
                                    pushed_key = f'dd_Kuwo_pushed_{account}_{record_id}'
                                    if not middleware.bucketGet('dd_Kuwo_pushed', pushed_key):
                                        # 标记为已推送
                                        middleware.bucketSet('dd_Kuwo_pushed', pushed_key, 'pushed')
                                        
                                        # 推送提现成功通知
                                        push_msg = f"""
=====提现成功通知=====
📱 账号: {phone_masked}
💰 金额: {amount}元
⏰ 时间: {record_date} {record_time}
✅ 状态: 提现成功
-------------------
💡 资金将在1-3个工作日内到账
=================="""
                                        
                                        # 发送到各个平台
                                        platforms = ['wb', 'tg', 'qq', 'qb', 'wx']
                                        for platform in platforms:
                                            try:
                                                middleware.push(platform, '', user, '', push_msg)
                                            except Exception as e:
                                                print(f"推送到{platform}失败: {str(e)}")
                        except Exception as e:
                            continue
                            
                except Exception as e:
                    continue
                    
        except Exception as e:
            continue

# 主逻辑
today_date = datetime.now().date()
today_time = str(today_date)
QLurl, ClientID, ClientSecret, KuwoVipmoney, osname, Kuwocoin, use_daidai, dd_Kuwo_ddname, panel_group = PluginsData()

# 根据配置初始化面板连接
panel_url = ''
panel_token = ''
qltoken = ''
if use_daidai:
    panel_url, panel_token = seekdd()
else:
    qltoken = QLtoken(QLurl, ClientID, ClientSecret)
usermessage = sender.getMessage()

if usermessage in ['酷我登录', '酷我登陆', '登陆酷我', '登录酷我']:
    bind()
elif usermessage in ['酷我管理', '管理酷我']:
    Administration()
elif usermessage in ['酷我查询', '查询酷我']:
    query()
elif usermessage == '酷我授权':
    kuwo_auth()
elif usermessage == '酷我教程':
    tutorial()
elif usermessage == '酷我提现说明':
    withdraw_tutorial()
elif usermessage == '总结今日酷我':
    query_today_withdrawals()
elif usermessage == '酷我清理':  # 添加新的指令处理
    clean_expired_accounts()
elif usermessage == 'fake':
    """定时任务处理 - 8点/15点检测授权过期及CK失效"""
    # 执行账号状态检查
    users = middleware.bucketAllKeys(bucket='dd_Kuwo_bind')
    if not users:
        exit(0)
    
    # 获取当前日期和3天后的日期
    today = datetime.now().date()
    three_days_later = today + timedelta(days=3)
    
    for user in users:
        try:
            uservalue = middleware.bucketGet(bucket='dd_Kuwo_bind', key=user) or ''
            if not uservalue:
                continue
                
            accounts = eval(uservalue)
            for account in accounts:
                try:
                    Token = middleware.bucketGet(bucket='dd_Kuwo_account', key=account)
                    accountVip = middleware.bucketGet(bucket='dd_Kuwo_Vip', key=account) or ''
                    
                    if not Token:
                        continue
                        
                    values = Token.split('#')
                    if len(values) != 4:
                        continue
                        
                    phone = values[3]  # 获取手机号
                    phone_masked = phone[:3] + '*' * 4 + phone[7:]  # 脱敏手机号
                    
                    # 检查账号状态
                    try:
                        loginUid = values[0]
                        loginSid = values[2]
                        
                        # 验证账号状态
                        verify_url = "https://integralapi.kuwo.cn/api/v1/online/sign/new/todayStatus"
                        verify_headers = {
                            'Cookie': f'tmeAppID=kwplayer;loginSid={loginSid};loginUid={loginUid}',
                            'User-Agent': 'KWPlayer/11.1.2 (iPhone; iOS 17.7.2; Scale/3.00)'
                        }
                        verify_response = requests.get(verify_url, headers=verify_headers)
                        if verify_response.status_code != 200:
                            push(user, phone_masked, """
⏰ 定时检测提醒
------------------
❌ 账号登录已失效
💡 请尽快更新账号""")
                            continue
                            
                    except Exception as e:
                        print(f"验证账号 {account} 状态时出错: {str(e)}")
                        continue
                        
                    # 检查授权状态
                    if len(accountVip) == 0 or accountVip < str(today):
                        push(user, phone_masked, """
⏰ 定时检测提醒
------------------
❌ 授权已过期
💡 请及时续费授权""")
                    else:
                        try:
                            expire_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                            if today <= expire_date <= three_days_later:
                                days_left = (expire_date - today).days
                                push(user, phone_masked, f"""
⏰ 定时检测提醒
------------------
⚠️ 授权即将到期
📅 到期时间: {accountVip}
⏳ 剩余天数: {days_left}天
💡 请及时续费授权""")
                        except Exception as e:
                            print(f"检查账号 {account} 过期时间时出错: {str(e)}")
                            continue
                        
                except Exception as e:
                    print(f"处理账号 {account} 时出错: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
