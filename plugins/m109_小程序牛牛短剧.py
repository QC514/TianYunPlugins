# [author: mrconli]
# [title: m109_小程序牛牛短剧]
# [language: python]
# [class: 工具类]
# [service: 呆瓜群：591022646，插件群：1040780519] 售后联系方式
# [disable: false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^小牛牛(.*)|(.*)小牛牛$] 匹配规则，多个规则时向下依次写多个
# [cron: 49 8,18 * * *] cron定时，支持5位域和6位域
# [priority: 99999999] 优先级，数字越大表示优先级越高
# [platform: all] 适用的平台
# [open_source: false]是否开源
# [icon: ]图标链接地址，请使用48像素的正方形图标，支持http和https
# [version: 1.0.0]版本号
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 8.88] 上架价格
# [description: 无脚本提供。ck提交青龙，格式：token<br>指令：小牛牛(登录|登陆|上车|查询|管理|授权|清理)<br>仅环境变量提交青龙<br>支持积分支付授权,可自定义积分数据桶。<br>1.0.0初版：支持授权、批量登录、代理、积分开通等功能] 使用方法尽量写具体




# [param: {"required":true,"key":"mrconli.config.zsm","bool":false,"placeholder":"示例: http://10.10.10.10:8080/zsm.jpg","name":"收款码地址","desc":"赞赏码或收款码地址"}]
# [param: {"required":true,"key":"mrconli.xnndj.ql_config","bool":false,"placeholder":"http://xx.xx.xx.xx:xxxx|xxx|xxx","name":"对接青龙","desc":"|"}]
# [param: {"required":false,"key":"mrconli.xnndj.var_name","bool":false,"placeholder":"xnndj","name":"环境变量名","desc":"青龙容器内的变量名，默认为：xnndj"}]
# [param: {"required":false,"key":"mrconli.xnndj.price","bool":false,"placeholder":"1","name":"上车价格","desc":"上车价格(单位:元)/30天"}]
# [param: {"required":false,"key":"mrconli.xnndj.coin","bool":false,"placeholder":"不填为关闭状态","name":"积分开通","desc":"授权一个月的积分，只能为整数"}]
# [param: {"required":false,"key":"mrconli.xnndj.coin_bucket","bool":false,"placeholder":"","name":"积分数据桶","desc":"默认使用dd_sign_points"}]
# [param: {"required":false,"key":"mrconli.xnndj.is_proxy","bool":true,"placeholder":"","name":"是否启用代理","desc":"开启代理就勾选，其实不需要代理"}]
# [param: {"required":false,"key":"mrconli.xnndj.proxy_pool","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]





scripts_name =  "小牛牛"
full_scripts_name =  "小牛牛短剧"
bucket_prefix = "mrconli.xnndj"

from datetime import datetime, timedelta  # 操作日期、时间以及时间间隔
import middleware  # autman的中间件
import urllib3
from decimal import Decimal  # 处理浮点数
import requests  # 处理http请求
import time  # 处理时间
import json  # 处理json数据
import re
from datetime import datetime, timedelta
import uuid
import time, base64, random, hashlib
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA


# 禁用 SSL 警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



senderID = middleware.getSenderID()  # 获取发送者QQ号
sender = middleware.Sender(senderID)  # 获取发送者对象
userid = sender.getUserID()  # 存储当前发送者的用户 ID，与 senderID 类似，但通常用于内部标识
uservalue = middleware.bucketGet(bucket=f'{bucket_prefix}.user', key=userid)
today_date = datetime.now().date()
today_time = str(today_date)



# 代理配置
MAX_RETRIES = 5  # 最大重试次数
IS_PROXY = middleware.bucketGet(bucket_prefix, 'is_proxy')  # 是否启用代理True
PROXY_API = middleware.bucketGet(bucket_prefix, 'proxy_pool') or "http://mrconli.com:12306"
proxy = None  # 初始化全局代理变量


def update_proxy():
    """更新代理IP地址"""
    global proxy
    try:
        if not IS_PROXY or IS_PROXY == "false":
            proxy = None
            return
        response = requests.get(PROXY_API, timeout=15)
        ip = response.text.strip()
        if "请先添加白名单" in ip:
            raise ValueError("请配置代理白名单")
        proxy = {
            'http': ip,
            'https': ip,
        }
    #    sender.reply(f"✅ 代理获取成功: {ip}")
    except Exception as e:
        sender.reply(f"❌ 代理获取失败: {str(e)}")
        proxy = None


def _send_request(method, url, **kwargs):
    """带代理重试的请求方法"""
    global proxy
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            # 确保代理已初始化
            if IS_PROXY:
                proxy = proxy if 'proxy' in globals() else None
                if not proxy:
                    update_proxy()
            kwargs['timeout'] = kwargs.get('timeout', 15)  # 默认超时时间 15 秒
            response = requests.request(
                method=method,
                url=url,
                proxies=proxy if IS_PROXY and proxy else None,
                verify=False,
                **kwargs
            )
            response.raise_for_status()
            return response
        except (requests.exceptions.ProxyError, requests.exceptions.Timeout) as e:
            print(f"⚠️ 代理异常: {str(e)}")
            if IS_PROXY:
                update_proxy()
                attempts += 1
                print(f"🔄 重试请求 ({attempts}/{MAX_RETRIES})")
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"🚨 请求失败: {str(e)}")
            raise
    raise Exception(f"请求失败，超过最大重试次数: {MAX_RETRIES}")

###   请求头    _send_request('GET',   _send_request('POST',

def mask_phone(phone):
    """手机号脱敏处理"""
    if not phone or len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[7:]}"
 
def is_valid_phone(phone):
    """验证手机号格式是否正确
    Args:
        phone: 待验证的手机号字符串
    Returns:
        bool: 格式正确返回True，否则返回False
    """
    if not phone or not isinstance(phone, str):
        return False
    pattern = r'^1[3-9]\d{9}$'    # 中国大陆手机号正则表达式：以1开头，第二位3-9，后面9位数字
    return re.match(pattern, phone) is not None





# 登录验证及查询函数


def get_user_info(token):
    coin_url = "https://api.tianjinzhitongdaohe.com/sqx_fast/app/integral/selectByUserId"
    money_url = "https://api.tianjinzhitongdaohe.com/sqx_fast/app/invite/selectInviteMoney"
    headers = {
        "Host": "api.tianjinzhitongdaohe.com",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254181d) XWEB/19201",
        "xweb_xhr": "1",
        "Content-Type": "application/x-www-form-urlencoded",
        "token": token,
        "Accept": "*/*",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://servicewechat.com/wxcb95401f250e9a53/19/page-frame.html",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }
    coin_response = _send_request('GET', coin_url, headers=headers)
    if coin_response.status_code == 200:
        data = coin_response.json()
        if data.get("code") == 0:
            money_response = _send_request('GET', money_url, headers=headers)
            nn_id = data.get("data", {}).get("userId")
            integral = data.get("data", {}).get("integralNum")
            inviteMoney = money_response.json().get("data", {}).get("inviteMoney")
            money = inviteMoney.get("money")
            return True, nn_id, integral, money
        else:
            print("请求失败:", data.get("msg"))
            return False, None, None, None
    else:
        print("请求失败，状态码:", coin_response.status_code)
        return False, None, None, None

####    扫码登录       ########################################################################


def get_qr_code():
    """获取微信二维码UUID"""
    url = "https://open.weixin.qq.com/connect/app/qrconnect"
    params = {
        'appid': APPID,
        'bundleid': BUNDLEID,
        'scope': 'snsapi_userinfo',
        'state': 'wx_oauth_authorization_state',
        'pass_ticket': str(uuid.uuid4())
    }
    headers = {
        'User-Agent': DEFAULT_UA,
        'Referer': "https://open.weixin.qq.com/"
    }
    try:
        response = _send_request('GET', url, params=params, headers=headers)
        if response.status_code == 200:
            match = re.search(r'uuid\: *"(\w+)"', response.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f'获取二维码失败：{e}')
    return None

def check_scan_status(uuid_str):
    """检查二维码扫描状态"""
    url = f"https://long.open.weixin.qq.com/connect/l/qrconnect"
    params = {
        'uuid': uuid_str,
        'f': 'url',
        '_': int(time.time() * 1000)
    }
    headers = {
        'User-Agent': DEFAULT_UA,
        'Referer': "https://open.weixin.qq.com/"
    }
    try:
        response = _send_request('GET', url, params=params, headers=headers)
        if response.status_code == 200:
            print(response.text)
            if 'window.wx_errcode=405' in response.text:
                code_pattern = r'oauth\?code=([^&]+)&state='
                code_match = re.search(code_pattern, response.text)
                nickname_match = re.search(r"window\.wx_nickname='([^']+)'", response.text)
                if code_match:
                    code = code_match.group(1)
                    nickname = nickname_match.group(1) if nickname_match else "未知用户"
                    return {"code": code, "nickname": nickname}
            elif 'window.wx_errcode=408' in response.text:
                return {"status": "waiting"}
            elif 'window.wx_errcode=404' in response.text:
                return {"status": "expired"}
            else:
                return {"status": "unknown"}
    except Exception as e:
        print(f'检查扫码状态失败：{e}')
    return {"status": "error"}




########    登录选择    ########
def bind():
    """账号登录"""
    login_guide = """
=====登录方式=====
[1] 扫码登录
[2] 抓包登录（支持批量）
------------------
回复数字选择方式
回复"q"退出"""
    sender.reply(login_guide)
    choice = sender.input(60000, recallDuration=60000, forGroup=False)
    if not choice:
        sender.reply('❌ 输入超时！')
        return
    if choice == 'q' or choice == 'Q':
        sender.reply('❌ 已退出登录操作！')
        return
    try:
        if choice == '1':
            scan_login()
        elif choice == '2':
            batch_login()
        else:
            sender.reply("❌ 无效的选择")
            return
    except Exception as e:
        sender.reply(f"❌ 登录失败: {str(e)}")
        return


########    短信登录    ########
def sms_login():
    account, u_token, uuid, oaid, device_id = sms_send()
    if account is None or u_token is None or oaid is None or device_id is None:
        sender.reply('❌ 登录失败，无法获取账户信息')
        return
    token = f"{u_token}#{device_id}"
    try:
        try:
            accounts = eval(uservalue or '[]')
        except (json.JSONDecodeError, TypeError):
            return
        auth = middleware.bucketGet(f'{bucket_prefix}.auth', account)
        auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        if account not in accounts:
            dlzt = "登录"
            accounts.append(account)
            middleware.bucketSet(f'{bucket_prefix}.user', userid, json.dumps(accounts))
        else:
            dlzt = "更新"
            if not auth or auth < today_time:
                sender.reply(f"⚠️ 账号未授权或授权已过期，环境变量未提交青龙...")
            else:
                add_to_qinglong(token, account, userid)
        middleware.bucketSet(f'{bucket_prefix}.token', account, token)
        middleware.bucketSet(f'{bucket_prefix}.oaid', account, oaid)
        middleware.bucketSet(f'{bucket_prefix}.uuid', account, uuid)    
        if auth and auth > today:
            success_msg = f"""
=====星芽{dlzt}成功=====
📱 手机号: {mask_phone(account)}
🔐 授权状态: {auth_status}
⏰ 授权到期: {auth}
------------------
发送"{manage_cmd}"管理账号
发送"{query_cmd}"查询账号
"""
        else:
            success_msg = f"""
=====星芽{dlzt}成功=====
📱 手机号: {mask_phone(account)}
🔐 授权状态: {auth_status}
------------------
发送"{manage_cmd}"管理账号
发送"{query_cmd}"查询账号
"""
        sender.reply(success_msg)
    except Exception as e:
        sender.reply(f"❌ 处理登录失败: {str(e)}")
        return

########    扫码登录    ########
def scan_login():
    """微信扫码登录流程"""
    uuid_str = get_qr_code()
    if not uuid_str:
        sender.reply("❌ 获取登录二维码失败，请稍后再试")
        return False
    qr_url = f"https://open.weixin.qq.com/connect/qrcode/{uuid_str}"
    sender.reply("请使用微信扫描下方二维码登录")
    sender.replyImage(qr_url)
    sender.replyImage("扫码后请在微信中点击「确认登录」\n等待扫码中...\n回复'q'取消操作")
    retry_count = 0
    max_retries = 90  # 最多等待90秒
    while retry_count < max_retries:
        try:
            message = sender.listen(1000)  # 等待1秒
            if message == 'q' or message == 'Q':
                sender.reply("❌ 已取消扫码登录")
                exit(0)
        except:
            pass
        result = check_scan_status(uuid_str)
        if isinstance(result, dict):
            if 'code' in result:
                code = result['code']
                nickname = result.get('nickname', '未知用户')
                sender.reply(f"{nickname} 扫码成功，正在处理登录...")
                break
            elif result.get('status') == 'waiting':
                pass
            elif result.get('status') == 'unknown':
                sender.reply("❌ 扫码出现未知状态，请重新尝试")
                return False, None, None
            elif result.get('status') == 'error':
                sender.reply("❌ 扫码出现错误，请重新尝试")
                return False, None, None
        retry_count += 1
        time.sleep(1)
    if max_retries <= retry_count:
        sender.reply("❌ 扫码超时，请重新尝试")
        exit(0)
    success, uid, token = get_token_by_code(code)
    if success:
        phone = str(uid)
        middleware.bucketSet(f'{bucket_prefix}.token', phone, token)
      
        current_accounts = eval(middleware.bucketGet(f'{bucket_prefix}.user', userid) or '[]')
        if phone not in current_accounts:  
            status = f"{scripts_name}登录成功"
            accountVip = middleware.bucketGet(f'{bucket_prefix}.auth', phone)
            if not accountVip or accountVip < today_time:
                accountVip = f"❌ 未授权"
            current_accounts.append(phone)
            middleware.bucketSet(f'{bucket_prefix}.user', userid, json.dumps(current_accounts, ensure_ascii=False))
        else:
            status = f"{scripts_name}更新成功"
            accountVip = middleware.bucketGet(f'{bucket_prefix}.auth', phone)
            if not accountVip or accountVip < today_time:
                accountVip = f"❌ 未授权"
                sender.reply(f"⚠️ 账号未授权或授权已过期，环境变量未提交青龙...")
            else:
                add_to_qinglong(token, phone, userid)
        sender.reply(f"""
====={status}=====
📱 账号: {nickname}[{mask_phone(phone)}]
⏰ 授权到期：{accountVip}
==================""")
    else:
        sender.reply(f"❌ {nickname} 登录失败，请稍后重试")



########    批量登录    ########
def batch_login():
    """批量登录函数"""
    global uservalue
    sender.reply(
        f"======={login_cmd}=======\n"
        "📝 请输入ck参数: 备注#token\n"
        "说明:\n"
        "  1. 支持批量，一个账号一行\n"
        "=====================\n"
        "⭐ 输入q退出操作\n"
    )
    success_count = 0
    add_count = 0
    update_count = 0
    fail_count = 0
    error_reasons = []
    
    accounts_str = sender.input(120000, 1, False)
    if accounts_str == 'q':
        sender.reply('❌ 已退出登录操作！')
        return
    if not accounts_str:
        sender.reply('❌ 输入超时！')
        return
    accounts = [line.strip() for line in accounts_str.split('\n') if line.strip()]
    
    total = len(accounts)
    if total == 0:
        sender.reply("❌ 未检测到有效账号信息")
        return
    
    sender.reply(f"🔍 共检测到 {total} 个账号，开始批量登录...")
    
    for index, account in enumerate(accounts, 1):
        try: 
            parts = account.split("#")
            if len(parts) == 2:
                remark = parts[0]
                token = parts[1]
            else:
                fail_count += 1
                sender.reply(f"❌ {account} ck格式错误")
                continue
            success, nn_id, integral, money = get_user_info(token)
            if not success:
                fail_count += 1
                error_reasons.append(f"❌ {account} 登录认证失败")
                continue
            if success:
                phone = str(nn_id)
                success_count += 1
                middleware.bucketSet(f'{bucket_prefix}.token', phone, token)
                middleware.bucketSet(f'{bucket_prefix}.remark', phone, remark)
                current_accounts = eval(middleware.bucketGet(f'{bucket_prefix}.user', userid) or '[]')
                if phone not in current_accounts:
                    add_count += 1
                    status = f"✅ {remark} 登录成功"
                    current_accounts.append(phone)
                    middleware.bucketSet(f'{bucket_prefix}.user', userid, json.dumps(current_accounts, ensure_ascii=False))
                else:
                    update_count += 1
                    status = f"✅ {remark} 更新成功"
                    accountVip = middleware.bucketGet(f'{bucket_prefix}.auth', phone)
                    if not accountVip or accountVip < today_time:
                        sender.reply(f"⚠️ 账号未授权或授权已过期，环境变量未提交青龙...")
                    else:
                        add_to_qinglong(token, phone, userid)
            else:
                print(f"登录失败")
                fail_count += 1
                error_reasons.append(f"❌ {account} 登录认证失败")
                continue                                                                                     
                                                                                                    
            # 强制刷新全局账户缓存
            uservalue = json.dumps(current_accounts) 
               
            # 进度反馈
            progress = f"[{index}/{total}] {status}"
            sender.reply(progress) 
        except Exception as e:
            fail_count += 1
            error_msg = f"无效账号: {account}：{e}"
            error_reasons.append(error_msg)
            sender.reply(f"⚠️ 第{index}个账号处理失败: {error_msg}")
        time.sleep(2)

    # 生成统计报告
    report = (
        f"📊 登录完成\n"
        f"✅ 执行成功: {success_count} 个\n"
        f"➕ 添加: {add_count} 个\n"
        f"🔄 更新: {update_count} 个\n"
        f"✖️ 失败: {fail_count} 个\n"
        f"------------------------\n"
        f"发送“{manage_cmd}”管理账号\n"
        f"发送“{query_cmd}”查询账号\n"
    )
    
    if error_reasons:
        report += "\n❌ 失败原因:\n" + "\n".join(error_reasons[:5])
        if len(error_reasons) > 5:
            report += f"\n...等{len(error_reasons)-5}个错误" 
    sender.reply(report)



def query():
    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply(
            f'\n==={query_cmd}===\n❌ 未找到任何账号\n------------------\n💡 发送"{login_cmd}"绑定账号\n===================')
        return
    # 生成交互菜单
    if len(accounts) > 1:
        menu = "=====请选择查询账号=====\n[0] 查询全部账号\n------------------\n"
        for idx, acc in enumerate(accounts, 1):
            remark = middleware.bucketGet(f'{bucket_prefix}.remark', acc)
            menu += f"[{idx}] {remark} \n"
        menu += "====================\n⚠️ 请回复数字序号(输入q退出)\n💡 支持多选，如：1,3,4,7"
        sender.reply(menu)

        # 获取用户输入
        choice = sender.input(30000, 1, False)
        if not choice:
            sender.reply('❌ 输入超时！')
            return
        if choice.lower() == 'q':
            sender.reply('已取消查询')
            return
        
        # 处理多选输入
        if ',' in choice:
            # 多选模式：1,3,4,7
            choices = [c.strip() for c in choice.split(',')]
            target_accounts = []
            
            for c in choices:
                if not c.isdigit():
                    sender.reply(f'❌ 输入格式错误："{c}"不是有效数字')
                    return
                
                c_num = int(c)
                if c_num == 0:
                    # 如果包含0，则查询全部账号
                    target_accounts = accounts
                    break
                elif 1 <= c_num <= len(accounts):
                    target_accounts.append(accounts[c_num - 1])
                else:
                    sender.reply(f'❌ 选择超出范围：{c_num}')
                    return
            
            if target_accounts == accounts:
                sender.reply(f'正在查询全部{scripts_name}账号...')
            else:
                sender.reply(f'正在查询选中的{len(target_accounts)}个账号...')
        else:
            # 单选模式
            if not choice.isdigit():
                sender.reply('输入格式错误，请回复数字')
                return
            
            choice_num = int(choice)
            if choice_num < 0 or choice_num > len(accounts):
                sender.reply('选择超出范围，已取消查询')
                return
            
            if choice_num == 0:
                target_accounts = accounts
                sender.reply(f'正在查询全部{scripts_name}账号...')
            else:
                target_accounts = [accounts[choice_num - 1]]
    else:
        # 单个账号直接查询
        target_accounts = accounts

    for account in target_accounts:
        try:
            accountVip = middleware.bucketGet(f'{bucket_prefix}.auth', account)
            token = middleware.bucketGet(f'{bucket_prefix}.token', account)
            remark = middleware.bucketGet(f'{bucket_prefix}.remark', account)
            if not remark:
                remark = mask_phone(account)
            if not token:
                sender.reply(f'❌ 【{remark}】ck获取失败')
                continue
            if not accountVip:
                sender.reply(f'❌ 【{remark}】账号未授权')
            elif accountVip < today_time:
                sender.reply(f'❌ 【{remark}】云授权过期')
            else:
                success, nn_id, integral, money = get_user_info(token)
                if not success:
                    sender.reply(f'❌ {remark}：登录认证失败')
                    continue
                sender.reply(f"""
====={scripts_name}账号详情=====
👤 账号: {remark}
💎 积分: {integral}分
💰 余额: {money}元
⏰ 授权到期：{accountVip}
==================""")
        except Exception as e:
            sender.reply(f'❌ 【{mask_phone(account)}】查询出错: {str(e)}')


def cron_task():
    """定时任务处理"""
    if imtype != 'fake':
        return
    try:
        users = middleware.bucketAllKeys(f'{bucket_prefix}.user')
        for user in users:
            accounts = eval(middleware.bucketGet(f'{bucket_prefix}.user', user) or '[]')
            for account in accounts:
                try:
                    auth = middleware.bucketGet(f'{bucket_prefix}.auth', account)
                    if auth and auth <= today:
                        delete_from_qinglong(account)
                        notify_user(user, account, "授权已过期,环境变量已删除,请及时续费")
                        continue
                    token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                    remark = middleware.bucketGet(f'{bucket_prefix}.remark', account)
                    success, nn_id, integral, money = get_user_info(token)
                    if not success:
                        notify_user(user, account, f"账号 {remark} ck检测失效")
                        continue
                except Exception as e:
                    print(f"处理账号 {account} 出错: {str(e)}")
                    continue
    except Exception as e:
        print(f"定时任务出错: {str(e)}")


def notify_user(user, account, message):
    """发送用户通知"""
    try:
        notify_msg = f"""
====={full_scripts_name}账号通知=====
📱 账号: {account}
📢 消息: {message}
=================="""
        middleware.push('qq', '', user, '', notify_msg)
        middleware.push('wx', '', user, '', notify_msg)
        middleware.push('tg', '', user, '', notify_msg)
        middleware.push('qx', '', user, '', notify_msg)
        middleware.push('ipad', '', user, '', notify_msg)
    except Exception as e:
        print(f"发送通知失败: {str(e)}")

def get_config():
    """获取插件配置"""
    try:
        var_name = middleware.bucketGet(bucket_prefix, 'var_name') or "xnndj"
        if not var_name:
            print("未配置变量名，使用默认值: xnndj")
            var_name = 'xnndj'
            middleware.bucketSet(bucket_prefix, 'var_name', var_name)
        ql_config = middleware.bucketGet(bucket_prefix, 'ql_config')
        if not ql_config:
            raise ValueError("青龙配置未设置")
        ql_params = ql_config.split('丨')
        if len(ql_params) != 3:
            raise ValueError("青龙配置格式错误，应为 地址丨ClientID丨ClientSecret")
        if len(ql_params) == 3:
            ql_host = ql_params[0]
            ql_client_id = ql_params[1]
            ql_client_secret = ql_params[2]
        else:
            print("青龙配置不完整，请检查配置")
        manage_cmd = middleware.bucketGet(bucket_prefix, 'manage_cmd') or f'{scripts_name}管理'
        query_cmd = middleware.bucketGet(bucket_prefix, 'query_cmd') or f'{scripts_name}查询'
        login_cmd = middleware.bucketGet(bucket_prefix, 'login_cmd') or f'{scripts_name}登录'
        try:
            price = Decimal(middleware.bucketGet(bucket_prefix, 'price') or '1')
            if price < 0:
                raise ValueError("价格不能为负数")
        except (ValueError, decimal.InvalidOperation):
            print("价格配置无效，使用默认值: 1")
            price = Decimal('1')
            middleware.bucketSet(bucket_prefix, 'price', '1')
        try:
            coin_price = int(middleware.bucketGet(bucket_prefix, 'coin') or '0')
            if coin_price < 0:
                raise ValueError("积分不能为负数")
        except ValueError:
            print("积分配置无效，使用默认值: 0")
            coin_price = 0
            middleware.bucketSet(bucket_prefix, 'coin', '0')
        return (var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price)
    except Exception as e:
        error_msg = f"获取配置失败: {str(e)}"
        print(error_msg)
        sender.reply(f"❌ {error_msg}")
        raise


def init_qinglong():
    """初始化青龙连接"""
    try:
        ql_config = middleware.bucketGet(bucket_prefix, 'ql_config')
        if not ql_config:
            raise ValueError("青龙配置未设置")
        ql_host, ql_client_id, ql_client_secret = ql_config.split('丨')
        if not ql_host or not ql_client_id or not ql_client_secret:
            print("青龙配置不完整，请检查配置")
            exit(0)
        if not ql_host.endswith('/'):
            ql_host += '/'
        token = get_ql_token(ql_host, ql_client_id, ql_client_secret)
        return ql_host, token
    except Exception as e:
        sender.reply(f"❌ 连接青龙失败: {str(e)}")
        exit(0)


def get_ql_token(url, client_id, client_secret):
    """获取青龙token"""
    try:
        if not url.endswith('/'):
            url += '/'
        r = requests.get(f'{url}open/auth/token?client_id={client_id}&client_secret={client_secret}')
        if r.status_code != 200:
            raise Exception(f"请求失败: {r.status_code}")
        data = r.json()
        if "token" not in data.get('data', {}):
            raise Exception("获取token失败")
        return data['data']['token']
    except Exception as e:
        raise Exception(f"获取token失败: {str(e)}")


def add_to_qinglong(token, account, username):
    """添加变量到青龙"""
    try:
        url = f"{ql_host}/open/envs"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        
        # 强制更新逻辑（新增删除旧变量）
        existing_ids = []
        duplicate_vars = []
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            for env in response.json().get('data', []):
                if env['name'] == var_name and env.get('remarks', '') and account in env.get('remarks', ''):
                    existing_ids.append(env['id'])
                elif env['value'] == token:  # 新增重复值检测
                    duplicate_vars.append(env['id'])
        
        # 删除冲突变量（新增）
        if duplicate_vars:
            del_response = requests.delete(url, json=duplicate_vars, headers=headers)
            if del_response.status_code != 200:
                raise Exception(f"删除冲突变量失败: {del_response.text}")
        
        # 删除旧变量
        if existing_ids:
            del_response = requests.delete(url, json=existing_ids, headers=headers)
            if del_response.status_code != 200:
                raise Exception(f"删除旧变量失败: {del_response.text}")

        # 创建新变量（优化请求体格式）
        auth_time = middleware.bucketGet(f'{bucket_prefix}.auth', account) or '未授权'
        data = {
            "name": var_name,
            "value": token,
            "remarks": f"{full_scripts_name}账号:{account}丨用户:{username}丨授权时间:{auth_time}",
        }
        
        # 添加容错重试机制（新增）
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(url, headers=headers, json=[data])
            if response.status_code == 200:
                new_ids = [item['id'] for item in response.json().get('data', [])]
                middleware.bucketSet(f'{bucket_prefix}.env_id', account, json.dumps(new_ids))
                return True
            elif response.status_code == 500 and "SequelizeUniqueConstraintError" in response.text:
                print(f"🔄 检测到唯一性冲突，正在重试 ({attempt+1}/{max_retries})")
                time.sleep(1)
        
        # 增强错误信息（新增服务器响应详情）
        error_detail = response.json().get('message') or response.text
        raise Exception(f"操作失败：多次尝试后仍存在唯一性冲突 | {error_detail} [HTTP {response.status_code}]")
        
    except Exception as e:
        error_msg = f"青龙操作失败: {str(e)}"
        print(error_msg)
        sender.reply(f"❌ {error_msg}")
        return False


def enable_in_qinglong(env_ids):
    """启用环境变量"""
    try:
        url = f"{ql_url}/open/envs/enable"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, data=json.dumps(env_ids))
        if response.status_code == 200:
            rjson = response.json()
            if rjson.get('code') == 200:
                return True
            else:
                sender.reply(f"❌ 启用环境变量失败: {rjson.get('message')}")
                return False
        else:
            raise Exception(f"{response.status_code}")
    except Exception as e:
        sender.reply(f"❌ 启用环境变量失败: {str(e)}")
        return False


def disable_in_qinglong(env_ids):
    """禁用环境变量"""
    try:
        url = f"{ql_url}/open/envs/disable"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, data=json.dumps(env_ids))
        if response.status_code == 200:
            rjson = response.json()
            if rjson.get('code') == 200:
                return True
            else:
                sender.reply(f"❌ 禁用环境变量失败: {rjson.get('message')}")
                return False
        else:
            raise Exception(f"{response.status_code}")
    except Exception as e:
        sender.reply(f"❌ 禁用环境变量失败: {str(e)}")
        return False


def delete_from_qinglong(account):
    """从青龙删除变量"""
    try:
        url = f"{ql_url}/open/envs"
        headers = {
            "Authorization": f"Bearer {ql_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception("获取变量失败")
        env_id = None
        for env in response.json()['data']:
            if env['name'] == var_name and env.get('remarks', '') and account in env.get('remarks', ''):
                env_id = env['id']
                break
        if env_id:
            response = requests.delete(url, headers=headers, json=[env_id])
            if response.status_code != 200:
                raise Exception("删除变量失败")
        return True
    except Exception as e:
        sender.reply(f"❌ 青龙操作失败: {str(e)}")
        return False


def manage_accounts():
    """管理账号"""
    accounts = eval(middleware.bucketGet(bucket=f'{bucket_prefix}.user', key=userid))
    if not accounts:
        sender.reply(f"""
=====账号管理=====
❌ 未找到任何账号
------------------
💡 发送"{login_cmd}"绑定账号
==================""")
        return

    # 账号列表构建
    account_list = """
=====账号列表=====
批量操作:
[00] 授权全部账号
[01] 删除全部账号
[02] 查看全部账号ck
------------------
账号列表:"""
    for i, account in enumerate(accounts, 1):
        token = middleware.bucketGet(f'{bucket_prefix}.token', account)
        remark = middleware.bucketGet(f'{bucket_prefix}.remark', account)
        auth = middleware.bucketGet(f'{bucket_prefix}.auth', account)
        auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        account_list += f"\n[{i}] {remark}\n    {auth_status}"
        if auth and auth > today:
            account_list += f"\n    授权到期: {auth}"
    account_list += "\n------------------\n回复数字选择账号\n回复'q'退出"

    sender.reply(account_list)
    choice = sender.listen(60000)

    # 处理用户选择
    if not choice:
        sender.reply("❌ 操作超时")
        return
    elif choice == 'q' or choice == 'Q':
        sender.reply("✅ 已取消操作")
        return
    try:
        if choice == '01':
            # 删除全部账号逻辑
            for account in accounts:
                delete_account(account)
            middleware.bucketSet(f'{bucket_prefix}.user', userid, '[]')
            sender.reply("✅ 已删除全部账号")
        elif choice == '02':
            # 查看全部ck逻辑
            for account in accounts:
                show_ck(account)
        elif choice == '00':
            # 批量授权逻辑
            sender.reply("📝 请输入授权天数(如使用积分兑换，必须为30的倍数):")
            days = sender.listen(60000)
            if not days:
                sender.reply("❌ 操作超时")
                return
            elif days == 'q' or days == 'Q':
                sender.reply("✅ 已取消授权")
                return
            # 新增配置获取（修复积分显示问题）
            coin_bucket = middleware.bucketGet(bucket_prefix, 'coin_bucket') or 'dd_sign_points'
            coin_price = int(middleware.bucketGet(bucket_prefix, 'coin') or '0')  # 确保获取最新积分价格
            try:
                days = int(days)
                if days <= 0:
                    raise ValueError("天数必须大于0")

                # 支付方式选择
                pay_choice = '1'
                if coin_price > 0:
                    user_coin = Decimal(middleware.bucketGet(coin_bucket, userid) or '0')
                    auth_guide = f"""
=====批量授权方式=====
[1] 微信支付
[2] 积分支付 (当前积分: {user_coin})
--------------------
💰 积分比例: {coin_price}积分/月
回复数字选择方式"""
                    sender.reply(auth_guide)
                    pay_choice = sender.listen(60000)
                    if pay_choice not in ['1', '2']:
                        sender.reply("❌ 无效的支付方式")
                        return

                # 微信支付处理
                if pay_choice == '1':
                    amount = price * (Decimal(days) / 30) * len(accounts)
                    amount = amount.quantize(Decimal('0.01'), rounding='ROUND_UP')
                    if process_payment(amount, days):
                        success_count = 0
                        for account in accounts:
                            auth_time = calculate_auth_time(account, days / 30)
                            middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
                            token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                          
                            if token:
                                add_to_qinglong(token, account, userid)
                            success_count += 1
                        sender.reply(f"""
=====批量授权成功=====
💰 支付: {amount}元
⏰ 时长: {days}天
✅ 成功: {success_count}个账号
====================""")

                # 积分支付处理
                elif pay_choice == '2':
                    coin_bucket = middleware.bucketGet(bucket_prefix, 'coin_bucket') or 'dd_sign_points'
                    user_coin = Decimal(middleware.bucketGet(coin_bucket, userid) or '0')
                    months = days / 30
                    if months != int(months):
                        sender.reply("❌ 积分支付需整月授权")
                        return
                    months = int(months)
                    need_coin = coin_price * months * len(accounts)
                    if user_coin < need_coin:
                        sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 所需积分: {need_coin}
💵 当前积分: {user_coin}
====================""")
                        return

                    new_coin = int(user_coin - need_coin)
                    middleware.bucketSet(coin_bucket, userid, str(new_coin))
                    success_count = 0
                    for account in accounts:
                        auth_time = calculate_auth_time(account, months)
                        middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
                        token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                       
                        if token:
                            add_to_qinglong(token, account, userid)
                        success_count += 1
                    sender.reply(f"""
=====批量授权成功=====
💰 消耗: {need_coin}积分
⏰ 时长: {days}天
✅ 成功: {success_count}个账号
💵 剩余: {new_coin}积分
====================""")

                # 更新青龙状态
                for account in accounts:
                    env_id_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
                    if env_id_str:
                        env_ids = json.loads(env_id_str)
                        enable_in_qinglong(env_ids)

            except ValueError as ve:
                sender.reply(f"❌ 无效的输入: {str(ve)}")
            except Exception as e:
                sender.reply(f"❌ 批量授权失败: {str(e)}")

        else:
            # 单个账号操作
            index = int(choice) - 1
            if 0 <= index < len(accounts):
                show_account_menu(accounts[index])
            else:
                sender.reply("❌ 无效的序号")

    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")


def show_account_menu(account):
    """显示账号操作菜单"""
    remark = middleware.bucketGet(f'{bucket_prefix}.remark', account)
    auth = middleware.bucketGet(f'{bucket_prefix}.auth', account)
    auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
    auth_info = f"\n    到期: {auth}" if auth and auth > today else ""
    menu = f"""
=====账号操作=====
📱 账号: {remark}
🔐 状态: {auth_status}{auth_info}
------------------
[1] 授权账号
[2] 删除账号
[3] 查看账号ck
------------------
回复数字选择操作
回复"q"退出"""
    sender.reply(menu)
    choice = sender.listen(60000)
    if not choice:
        sender.reply("❌ 操作超时")
        return
    elif choice == 'q':
        sender.reply("✅ 已取消操作")
        return
    try:
        if choice == '1':
            auth_account(account)
        elif choice == '2':
            delete_account(account)
        elif choice == '3':
            show_ck(account)
        else:
            sender.reply("❌ 无效的选择")
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")


def auth_account(account):
    """账号授权"""
    try:
        # 从配置获取积分桶名称
        price = Decimal(middleware.bucketGet(bucket_prefix, 'price') or '1')   #  每月价格
        coin_bucket = middleware.bucketGet(bucket_prefix, 'coin_bucket') or 'dd_sign_points'
        user_coin = middleware.bucketGet(coin_bucket, userid) or '0'
        user_coin = Decimal(user_coin)  # 使用 Decimal 处理大数值
        month_coin = Decimal(coin_price)  # 从配置获取每月所需积分
        remark = middleware.bucketGet(f'{bucket_prefix}.remark', account)

        if price == 0:
            sender.reply("📝 请输入授权天数:")
            days = sender.listen(60000)
            if not days:
                sender.reply("❌ 操作超时")
                return False
            elif days == 'q':
                sender.reply("✅ 已取消授权")
                return False
            days = int(days)
            if days <= 0:
                raise ValueError()
            auth_time = calculate_auth_time(account, days / 30)
            middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
            # 新增强制更新青龙变量逻辑
            token = middleware.bucketGet(f'{bucket_prefix}.token', account)
            if token:
                add_to_qinglong(token, account, userid)  # 强制更新变量
            else:
                sender.reply("⚠️ token获取失败，请联系管理员")
            env_id_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
            if env_id_str:
                env_ids = json.loads(env_id_str)
                enable_in_qinglong(env_ids)
            sender.reply(f"""
=====授权成功=====
📱 账号: {remark}
⏰ 时长: {days}天
📅 到期: {auth_time}
==================""")
            return True
        if month_coin <= 0:
            auth_guide = """
=====授权方式=====
[1] 微信支付
------------------
💰 现金比例: {price}元/30天
回复数字选择方式
回复"q"退出"""
        else:
            auth_guide = f"""
=====授权方式=====
[1] 微信支付
[2] 积分支付 (当前积分: {user_coin})
------------------
💰 现金比例: {price}元/30天
🌸 积分比例: {month_coin}积分/月
回复数字选择方式
回复"q"退出"""
        sender.reply(auth_guide)
        choice = sender.listen(60000)
        if not choice:
            sender.reply("❌ 操作超时")
            return False
        elif choice == 'q':
            sender.reply("✅ 已取消授权")
            return False
        if choice == '1':
            sender.reply("📝 请输入授权天数:")
            days = sender.listen(60000)
            if not days:
                sender.reply("❌ 操作超时")
                return False
            elif days == 'q':
                sender.reply("✅ 已取消授权")
                return False
            days = int(days)
            if days <= 0:
                raise ValueError()
            amount = price * (Decimal(days) / Decimal(30))
            amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding='ROUND_UP')

            if amount == 0:
                auth_time = calculate_auth_time(account, days / 30)
                middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
                # 新增强制更新青龙变量逻辑
                token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                if token:
                    add_to_qinglong(token, account, userid)  # 强制更新变量
                else:
                    sender.reply("⚠️ 令牌获取失败，请联系管理员")
                env_id_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
                if env_id_str:
                    env_ids = json.loads(env_id_str)
                    enable_in_qinglong(env_ids)
                sender.reply(f"""
=====授权成功=====
📱 账号: {remark}
⏰ 时长: {days}天
📅 到期: {auth_time}
==================""")
                return True            
            
            if amount != 0:
                payment_success = process_payment(amount, days)  # 处理支付
                if payment_success:  # 只有在支付成功的情况下才进行授权
                    auth_time = calculate_auth_time(account, days / 30)
                    middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
                    # 新增强制更新青龙变量逻辑
                    token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                    if token:
                        add_to_qinglong(token, account, userid)  # 强制更新变量
                    else:
                        sender.reply("⚠️ 令牌获取失败，请联系管理员")
                    env_id_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
                    if env_id_str:
                        env_ids = json.loads(env_id_str)
                        enable_in_qinglong(env_ids)
                    sender.reply(f"""
    =====授权成功=====
    📱 账号: {remark}
    💰 支付: {amount}元
    ⏰ 时长: {days}天
    📅 到期: {auth_time}
    ==================""")
                    return True
                else:
                    sender.reply("❌ 支付未成功，授权未完成")
                    return False
        elif choice == '2' and month_coin > 0:  # 只有积分支付开启时才处理
            sender.reply("📝 授权月数:")
            months = sender.listen(60000)
            if not months:
                sender.reply("❌ 操作超时")
                return False
            elif months == 'q':
                sender.reply("✅ 已取消授权")
                return False
            months = int(months)
            if months <= 0:
                raise ValueError()
            need_coin = month_coin * months
            if user_coin < need_coin:
                sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 所需积分: {need_coin}
💵 当前积分: {user_coin}
==================""")
                return False
            new_coin = int(user_coin - need_coin)
            middleware.bucketSet(coin_bucket, userid, str(new_coin))
            auth_time = calculate_auth_time(account, months)
            middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
            token = middleware.bucketGet(f'{bucket_prefix}.token', account)

            if token:
                add_to_qinglong(token, account, userid)  # 强制更新变量
            else:
                sender.reply("⚠️ 令牌获取失败，请联系管理员")

            env_id_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
            if env_id_str:
                env_ids = json.loads(env_id_str)
                enable_in_qinglong(env_ids)
            sender.reply(f"""
=====授权成功=====
📱 账号: {remark}
💰 消耗: {need_coin}积分
⏰ 时长: {months}月
📅 到期: {auth_time}
------------------
💵 剩余: {new_coin}积分
==================""")
            return True
        else:
            sender.reply("❌ 无效的选择")
    except ValueError:
        sender.reply("❌ 无效的数值")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")
    return False


def process_payment(amount, days):
    """处理支付"""
    if amount == 0:
        return True
    zsm = middleware.bucketGet('mrconli.config', 'zsm')
    if not zsm:
        sender.reply("❌ 未配置收款码")
        return False
    zfzt = sender.atWaitPay()
    if zfzt:
        sender.reply('当前有人正在支付,请稍后再试！')
        exit(0)
    pay_msg = f"""
=====微信扫码支付====
🎫 商品: {full_scripts_name}授权
📅 时长: {days}天
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)
    sender.replyImage(zsm)
    result = sender.waitPay("q", 100000)
    if not result:
        sender.reply("❌ 支付超时")
        return False
    elif result == 'q':
        sender.reply("✅ 已取消支付")
        return False
    try:
        if isinstance(result, str):
            result = json.loads(result)
        if 'Money' in result:
            paid_amount = Decimal(str(result.get('Money', 0)))
            pay_time = result.get('Time', '')
            pay_from = ''
        else:
            paid_amount = Decimal(str(result.get('money', 0)))
            pay_time = result.get('Time', '')
            pay_from = result.get('FromName', '')
        if paid_amount >= amount:
            return True
        else:
            sender.reply(f"""
=====支付失败=====
❌ 支付金额不足
------------------
💰 应付: {amount}元
💵 实付: {paid_amount}元
==================""")
            return False
    except Exception as e:
        sender.reply(f"""
=====支付异常=====
❌ 支付验证失败
------------------
⚠️ 错误: {str(e)}
==================""")
        return False


def calculate_auth_time(account, months):
    """计算授权时间"""
    current = datetime.now().date()
    auth = middleware.bucketGet(f'{bucket_prefix}.auth', account)
    if auth and auth > str(current):
        start = datetime.strptime(auth, "%Y-%m-%d").date()
    else:
        start = current
    days = int(months * 30)
    end = start + timedelta(days=days)
    return str(end)


def clean_expired():
    """清理过期账号"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    users = middleware.bucketAllKeys(f'{bucket_prefix}.user')
    cleaned = 0
    for user in users:
        accounts = eval(middleware.bucketGet(f'{bucket_prefix}.user', user) or '[]')
        valid = []
        for account in accounts:
            auth = middleware.bucketGet(f'{bucket_prefix}.auth', account)
            if not auth or auth <= str(datetime.now().date()):
                middleware.bucketDel(f'{bucket_prefix}.token', account)
                middleware.bucketDel(f'{bucket_prefix}.auth', account)
                middleware.bucketDel(f'{bucket_prefix}.env_id', account)
                cleaned += 1
            else:
                valid.append(account)
        if valid:
            middleware.bucketSet(f'{bucket_prefix}.user', user, str(valid))
        else:
            middleware.bucketDel(f'{bucket_prefix}.user', user)
    sender.reply(f"✅ 已清理 {cleaned} 个过期账号")



def retry_on_error(func, retries=3, delay=1):
    """错误重试装饰器"""
    def wrapper(*args, **kwargs):
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == retries - 1:
                    raise e
                time.sleep(delay)
        return None
    return wrapper


def log_operation(operation, user, account, status, message=''):
    """记录操作日志"""
    try:
        log = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'user': user,
            'account': account,
            'status': status,
            'message': message
        }
        logs = eval(middleware.bucketGet(f'{bucket_prefix}.logs', 'operations') or '[]')
        logs.append(log)
        if len(logs) > 1000:  # 只保留最近1000条
            logs = logs[-1000:]
        middleware.bucketSet(f'{bucket_prefix}.logs', 'operations', str(logs))
    except Exception as e:
        print(f"记录日志失败: {str(e)}")


def admin_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    auth_menu = """
=====授权管理=====
[1] 一键授权所有用户
[2] 指定用户授权
[3] 更新青龙环境变量
------------------
回复数字选择功能
回复"q"退出"""
    sender.reply(auth_menu)
    choice = sender.listen(60000)
    if not choice or choice == 'q':
        sender.reply("❌ 已取消操作")
        return
    if choice == '1':
        auth_all_users()
    elif choice == '2':
        auth_specific_user()
    elif choice == '3':
        update_qinglong_env()
    else:
        sender.reply("❌ 无效的选择")


def update_qinglong_env():
    """更新全部青龙环境变量"""
    sender.reply("正在更新全部账号的青龙环境变量...")
    users = middleware.bucketAllKeys(f'{bucket_prefix}.user')
    total_users = len(users)
    total_accounts = 0
    success = 0
    failed = 0
    for user in users:
        accounts = eval(middleware.bucketGet(f'{bucket_prefix}.user', user) or '[]')
        for account in accounts:
            total_accounts += 1
            try:   
                token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                if token:
                    add_to_qinglong(token, account, user)
                env_ids_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
                if env_ids_str:
                    env_ids = json.loads(env_ids_str)
                    enable_in_qinglong(env_ids)
                success += 1
            except Exception as e:
                failed += 1
    sender.reply(f"""
=====更新青龙完成=====
共计: {total_users}个用户{total_accounts}个账号
------------------
✅ 成功: {success}个账号
❌ 失败: {failed}个账号
==================""")



def auth_all_users():
    """一键授权所有用户"""
    sender.reply("""
=====批量授权=====
📝 请输入授权天数
------------------
回复数字设置天数
回复"q"退出""")
    try:
        days = sender.listen(60000)
        if not days or days == 'q':
            sender.reply("✅ 已取消授权")
            return
        days = int(days)
        if days <= 0:
            raise ValueError()
        users = middleware.bucketAllKeys(f'{bucket_prefix}.user')
        success = 0
        failed = 0
        for user in users:
            accounts = eval(middleware.bucketGet(f'{bucket_prefix}.user', user) or '[]')
            for account in accounts:
                try:
                    auth_time = calculate_auth_time(account, days / 30)
                    middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
                    token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                    if token:
                        add_to_qinglong(token, account, user)
                    env_ids_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
                    if env_ids_str:
                        env_ids = json.loads(env_ids_str)
                        enable_in_qinglong(env_ids)
                    success += 1
                    log_operation('batch_auth', user, account, 'success')
                except Exception as e:
                    failed += 1
                    log_operation('batch_auth', user, account, 'failed', str(e))
        sender.reply(f"""
=====授权完成=====
✅ 成功: {success}个账号
❌ 失败: {failed}个账号
⏰ 授权: {days}天
==================""")
    except ValueError:
        sender.reply("❌ 无效的天数")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")


def auth_specific_user():
    """指定用户授权"""
    sender.reply("""
=====指定授权=====
📝 请输入用户ID
(发送myuid可获取ID)
------------------
回复"q"退出""")
    user_id = sender.listen(60000)
    if not user_id or user_id == 'q':
        return
    accounts = eval(middleware.bucketGet(f'{bucket_prefix}.user', user_id) or '[]')
    if not accounts:
        sender.reply("❌ 未找到该用户的账号")
        return
    account_list = """
=====账号列表=====
[00] 授权全部账号
[01] 修改全部账号授权
----------------"""
    for i, account in enumerate(accounts, 1):
        auth = middleware.bucketGet(f'{bucket_prefix}.auth', account)
        status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        account_list += f"\n[{i}] {mask_phone(account)}\n    {status}"
    account_list += """
------------------
回复数字选择账号
回复"q"退出"""
    sender.reply(account_list)
    choice = sender.listen(60000)
    if not choice:
        sender.reply("❌ 操作超时！")
        return
    if choice == 'q' or choice == 'Q':
        sender.reply("❌ 退出操作！")
        return

    if choice == '00':
        sender.reply("""
=====设置授权时间=====
📝 请输入授权天数
------------------
回复数字设置天数
回复"q"退出""")
        days = sender.listen(60000)
        if not days or days == 'q':
            return
        days = int(days)
        if days <= 0:
            raise ValueError()
        for account in accounts:
            try:
                auth_time = calculate_auth_time(account, days / 30)
                middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
                token = middleware.bucketGet(f'{bucket_prefix}.token', account)
                if token:
                    add_to_qinglong(token, account, user_id)
                env_ids_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
                if env_ids_str:
                    env_ids = json.loads(env_ids_str)
                    enable_in_qinglong(env_ids)
                log_operation('auth', user_id, account, 'success')
            except Exception as e:
                log_operation('auth', user_id, account, 'failed', str(e))
        sender.reply(f"✅ 已授权所有账号 {days}天")
    elif choice == '01':
        sender.reply("""=====批量修改授权=====
📝 请输入授权日期
格式：2025-01-01
------------------
回复"q"退出""")
        new_auth = sender.listen(60000)
        if not new_auth:
            sender.reply("❌ 操作超时！")
            return
        if new_auth == 'q' or new_auth == 'Q':
            sender.reply("❌ 退出操作！")
            return
        # 验证日期格式必须为 YYYY-MM-DD
        date_pattern = r'^\d{4}-\d{2}-\d{2}$'
        if not re.match(date_pattern, new_auth):
                sender.reply("❌ 日期格式错误！请使用格式：2025-01-01")
                return
        try:
            datetime.strptime(new_auth, '%Y-%m-%d')
        except ValueError:
            sender.reply("❌ 无效的日期！请检查输入的日期是否正确")
            return
        for account in accounts:
            middleware.bucketSet(f'{bucket_prefix}.auth', account, new_auth)
            token = middleware.bucketGet(f'{bucket_prefix}.token', account)
            if token:
                add_to_qinglong(token, account, user_id)
            env_ids_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
            if env_ids_str:
                env_ids = json.loads(env_ids_str)
                enable_in_qinglong(env_ids)
        sender.reply(f"✅ 所有账号授权日期修改为： {new_auth}")

    else:
        try:
            index = int(choice) - 1
            if not 0 <= index < len(accounts):
                raise ValueError()
            sender.reply("""
=====设置授权时间=====
📝 请输入授权天数
------------------
回复数字设置天数
回复"q"退出""")
            days = sender.listen(60000)
            if not days or days == 'q':
                sender.reply(f"❌ 退出操作！")
                return
            days = int(days)
            if days <= 0:
                raise ValueError()
            account = accounts[index]
            auth_time = calculate_auth_time(account, days / 30)
            middleware.bucketSet(f'{bucket_prefix}.auth', account, auth_time)
            token = middleware.bucketGet(f'{bucket_prefix}.token', account)
            if token:
                add_to_qinglong(token, account, user_id)
            env_ids_str = middleware.bucketGet(f'{bucket_prefix}.env_id', account)
            if env_ids_str:
                env_ids = json.loads(env_ids_str)
                enable_in_qinglong(env_ids)
            sender.reply(f"""
=====授权成功=====
📱 账号: {mask_phone(account)}
⏰ 时长: {days}天
📅 到期: {auth_time}
==================""")
            log_operation('auth', user_id, account, 'success')
        except Exception as e:
            sender.reply(f"❌ 授权失败: {str(e)}")
            log_operation('auth', user_id, account, 'failed', str(e))



def delete_account(account):
    """删除账号"""
    try:
        if not delete_from_qinglong(account):
            raise Exception("从青龙删除变量失败")
        middleware.bucketDel(f'{bucket_prefix}.token', account)
        middleware.bucketDel(f'{bucket_prefix}.auth', account)
        middleware.bucketDel(f'{bucket_prefix}.env_id', account)

        # 安全解析用户列表
        try:
            accounts = eval(uservalue or "[]")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"用户列表解析失败: {str(e)}")
        
        # 校验账号存在性并更新
        if account in accounts:
            accounts.remove(account)
            try:
                middleware.bucketSet(f'{bucket_prefix}.user', userid, json.dumps(accounts, ensure_ascii=False))
            except Exception as e:
                raise Exception(f"用户列表更新失败: {str(e)}")
        sender.reply(f"""
=====删除成功=====
📱 账号: {mask_phone(account)}
✅ 状态: 已删除
==================""")
        log_operation('delete_account', userid, account, 'success')
        return True
    except Exception as e:
        error_msg = f"删除账号失败: {str(e)}"
        sender.reply(f"❌ {error_msg}")
        log_operation('delete_account', userid, account, 'failed', str(e))
        return False

def show_ck(account):
    """查看账号ck"""
    token = middleware.bucketGet(f'{bucket_prefix}.token', account)
    if token:
        sender.reply(f"""
====={full_scripts_name}账号ck=====
📱 账号: {mask_phone(account)}
🔑 CK: {token}
====================""")
    else:
        sender.reply(f"❌ {full_scripts_name}账号未绑定ck")


def tutorial():
    f"""显示{full_scripts_name}使用教程"""
    tutorial_text = (
        f"====={full_scripts_name}教程=====\n"
        "📝 入口:\n"
        f"    #小程序://牛牛短剧/YeooKG8yVePqsco\n"
        "🌟 基础指令:\n"
        f"1. {scripts_name}登录 - 绑定账号\n"
        f"2. {scripts_name}查询 - 查看状态\n"
        f"3. {scripts_name}时长 - 刷新时长\n"
        f"4. {scripts_name}管理 - 管理账号\n"
        f"5. {scripts_name}授权 - 管理员授权账号\n"
        f"6. {scripts_name}清理 - 管理员清理过期\n"
        "-------------------\n"
        "🚩 收益说明:\n"
        "▸ 现金收益\n"
        "=================="
    )
    sender.reply(tutorial_text)


def main():
    """主函数"""
    message = sender.getMessage()
    if '登录' in message or '登陆' in message or '上车' in message:
        bind_choice = middleware.bucketGet(bucket_prefix, 'bind') or "2"
        if bind_choice == "0" or bind_choice == "所有方式":
            bind()
        elif bind_choice == "1" or bind_choice == "仅短信登录":
            sms_login()
        elif bind_choice == "2" or bind_choice == "仅CK登录":
            batch_login()
    elif '管理' in message:
        manage_accounts()
    elif '查询' in message:
        query()
    elif '教程' in message:
        tutorial()
    elif message == f'{scripts_name}清理':
        clean_expired()
    elif message == f'{scripts_name}授权':
        if sender.isAdmin():
            admin_auth()
        else:
            sender.reply("❌ 您不是管理员，无法执行此操作")


if __name__ == "__main__":
    try:
        var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price = get_config()
        ql_url, ql_token = init_qinglong()
        imtype = sender.getImtype()
        today = str(datetime.now().date())
        if imtype == 'fake':
            cron_task()
        else:
            main()
    except Exception as e:
        sender.reply(f"❌ 运行出错: {str(e)}")
