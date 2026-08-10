# [author: mrconli]
# [title: 爱路桥]
# [language: python]
# [class: 工具类]
# [service: 呆瓜群：591022646，插件群：1040780519] 售后联系方式
# [disable: true] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^爱路桥(.*)|(.*)爱路桥$] 匹配规则，多个规则时向下依次写多个
# [cron: 0 8 * * *] cron定时，支持5位域和6位域
# [priority: 55] 优先级，数字越大表示优先级越高
# [platform: all] 适用的平台
# [open_source: false]是否开源
# [icon: https://pp.myapp.com/ma_icon/0/icon_52735792_1742312403/256]图标链接地址，请使用48像素的正方形图标，支持http和https
# [version: 1.4.0]版本号
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 2] 上架价格
# [description: AI练手，自用，短信验证码登录，仅账号查询、授权管理及提交青龙，无脚本提供。青龙环境变量格式为“uid#cookie”,配参可以设置不带cookie<br>指令：爱路桥（登录|查询|管理|授权|清理|教程）<br>1.支持积分支付数据桶自定义，不再为积分系统不统一烦恼！<br>2.默认支持调用linzixuan最新积分。<br>1.3.0更新：增加参数效验，统一数据结构<br>1.2.0更新：增加ck登录（可批量登录）<br>1.1.0更新：配参自定义历史红包显示条数<br>1.0.0初版：脚本自行购买好用的。] 使用方法尽量写具体


# [param: {"required":true,"key":"mrconli.config.zsm","bool":false,"placeholder":"示例: http://10.10.10.10:8080/zsm.jpg","name":"收款码地址","desc":"赞赏码或收款码地址"}]
# [param: {"required":true,"key":"mrconli.ailuqiao.ql_config","bool":false,"placeholder":"http://10.10.10.10:5700|xxx|xxx","name":"对接青龙","desc":"|"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.var_name","bool":false,"placeholder":"S_ALQ","name":"环境变量名","desc":"青龙容器内的变量名，默认为：S_ALQ"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.is_cookie","bool":true,"placeholder":"","name":"环境变量带COOKIE","desc":"提交的环境变量是否带cookie"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.price","bool":false,"placeholder":"1","name":"上车价格","desc":"上车价格(单位:元)/30天"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.coin","bool":false,"placeholder":"不填为关闭状态","name":"积分开通","desc":"授权一个月的积分，只能为整数"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.coin_bucket","bool":false,"placeholder":"","name":"积分数据桶","desc":"默认使用dd_sign_points"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.is_proxy","bool":false,"placeholder":"False","name":"是否启用代理","desc":"True/False"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.proxy_pool","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":false,"key":"mrconli.ailuqiao.number","bool":false,"placeholder":"5","name":"历史红包显示","desc":"只能填写整数，默认显示5条"}]



from datetime import datetime, timedelta  # 操作日期、时间以及时间间隔
import middleware  # autman的中间件
import urllib3
from decimal import Decimal  # 处理浮点数
import requests  # 处理http请求
import time  # 处理时间
import json  # 处理json数据
import aiohttp
import random
from functools import lru_cache
import string



# 禁用 SSL 警告
urllib3.disable_warnings()

# 禁用 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

senderID = middleware.getSenderID()  # 获取发送者QQ号
sender = middleware.Sender(senderID)  # 获取发送者对象
userid = sender.getUserID()  # 存储当前发送者的用户 ID，与 senderID 类似，但通常用于内部标识
uservalue = middleware.bucketGet(bucket='mrconli.ailuqiao.user', key=userid)
today_date = datetime.now().date()
today_time = str(today_date)

base_url = 'https://www.ailuqiao.cn/mobile'  # 基础URL

# 代理配置
MAX_RETRIES = 5  # 最大重试次数
IS_PROXY = middleware.bucketGet('mrconli.ailuqiao', 'is_proxy') or "False"  # 是否启用代理True
PROXY_API = middleware.bucketGet('mrconli.ailuqiao', 'proxy_pool') or "http://10.10.10.251:12306/help/proxy/original"
if not PROXY_API:
    raise ValueError("代理池地址未配置，请在插件设置中配参")
proxy = None  # 初始化全局代理变量



def update_proxy():
    """更新代理IP地址"""
    global proxy
    try:
        if not IS_PROXY:
            proxy = None
            return
        response = requests.get(PROXY_API, timeout=10)
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

def get_random_user_agent():
    """获取随机UA"""
    backup_ua_list = [
        'Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.37 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 14; Pixel 6 Build/UQ1A.240605.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/133.0.6638.41 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1'
    ]
    return random.choice(backup_ua_list)

def generate_random_id():
    """生成随机设备ID"""
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))

def get_headers(uid, cookie):
    """获取相关请求头"""
    return {
        "User-Agent": get_random_user_agent(),
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Cookie": cookie
    }

def login_sms():
    """使用短信验证码登录爱路桥"""
    sender.reply(f"📝 请输入爱路桥手机号（q退出）")
    phone = sender.listen(120000)
    if phone == 'q' or phone == 'Q':
        sender.reply("❌ 已取消登录！")
        return None, None, None
    elif not phone:
        sender.reply("❌ 超时退出！")
        return None, None, None
    elif len(phone) != 11 or not phone.isdigit():
        sender.reply("❌ 手机号格式错误！")
        return None, None, None

    session_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
    cookie = f"beegosessionID={session_id}"
    try:
        url = f"{base_url}/service_send"
        headers = {
            "User-Agent": get_random_user_agent(),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": cookie
        }
        data = f"mobile={phone}"
        response = _send_request('POST',url, headers=headers, data=data)
        result = response.json()
        if result.get("status") != 1:
            sender.reply(f"❌ 发送验证码失败: {result.get('message', '未知错误')}")
            return None, None, None
        code_sent_lines = [
            f"✅ {mask_phone(phone)}验证码发送成功",
            "------------------",
            "📝 请输入接收到的验证码:"
        ]
        sender.reply("\n".join(code_sent_lines))
        code = sender.input(300000, 1, False)  # 5分钟超时
        if not code:
            sender.reply("⏰ 验证码输入超时，已取消登录")
            return None, None, None
        url = f"{base_url}/service_yz"
        data = f"mobile={phone}&code={code}"
    #    response = _send_request('POST',url, headers=headers, data=data)
        response = requests.post(url, headers=headers, data=data)
        result = response.json()
        if result.get("status") != 1:
            sender.reply(f"❌ 登录失败: {result.get('message', '验证码错误或已过期')}")
            return None, None, None
        uid = result.get("uid", "")
        if not uid:
            sender.reply("❌ 登录失败: 未获取到用户uid")
            return None, None, None
        return phone, uid, cookie
    except Exception as e:
        sender.reply(f"❌ 登录异常: {str(e)}")
        return None, None, None


def bind():
    """选择登录方式"""
    sender.reply(
        "=====爱路桥登录=====\n"
        "1. 短信验证码登录\n"
        "2. ck登录（可批量）\n"
        "=====================\n"
        "📝 请输入数字选择登录方式\n"
        "⭐ 输入q退出操作\n"
    )
    choice = sender.input(60000, 1, False)
    if choice == 'q' or choice == 'Q':
        sender.reply('❌ 已退出登录操作')
        return
    if not choice:
        sender.reply('❌ 输入超时！')
        return  
    if choice == '1':
        sms_login()
    elif choice == '2':
        batch_login()


def sms_login():
    global uservalue
    phone, uid, cookie=login_sms()
    mobile,nickname, integral = get_user_info(uid, cookie)
    if not mobile:
        return
    token = f"{uid}#{cookie}"
    
    try:
        try:
        #    accounts = json.loads(uservalue) if uservalue else []
            accounts = eval(uservalue or '[]')
        except (json.JSONDecodeError, TypeError):
            return
        account = f"{phone}"
        if account not in accounts:
            dlzt = "登录"
            accounts.append(account)
            middleware.bucketSet('mrconli.ailuqiao.user', userid, json.dumps(accounts))
        else:
            dlzt = "更新"
        middleware.bucketSet('mrconli.ailuqiao.token', account, token)
        success_msg = f"""
====={dlzt}成功=====
📱 手机号: {mask_phone(phone)}
👤 昵称: {nickname}
------------------
发送"{manage_cmd}"管理账号
发送"{query_cmd}"查询账号
"""
        sender.reply(success_msg)
    except Exception as e:
        sender.reply(f"❌ 处理登录失败: {str(e)}")
        exit(0)


def batch_login():
    """批量登录函数"""
    global uservalue
    sender.reply(
        "=====爱路桥登录=====\n"
        "📝 请输入登录参数:手机号#uid\n"
        "说明: 支持批量，一个账号一行” \n"
        "示例：\n"
        "    13888888888#123456\n"
        "    13999999999#654321\n"
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
            if account.count('#') == 1:
                phone, uid = account.split('#')
                # 新增格式校验
                if len(phone) != 11 or not phone.isdigit():
                    fail_count += 1
                    error_reasons.append(f"账号格式错误: {account} (手机号必须11位数字)")
                    continue
                if len(uid) != 6 or not uid.isdigit():
                    fail_count += 1
                    error_reasons.append(f"账号格式错误: {account} (UID必须6位数字)")
                session_id = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
                cookie = f"beegosessionID={session_id}"
                token = f"{uid}#{cookie}"
                # 执行登录
                mobile,nickname, integral = get_user_info(uid, cookie)
                mask_phone = f"{phone[:3]}*****{phone[-2:]}"
                if mobile and mobile == mask_phone:
                    success_count += 1
                    middleware.bucketSet('mrconli.ailuqiao.token', phone, token)
                    current_accounts = eval(middleware.bucketGet('mrconli.ailuqiao.user', userid) or '[]')
                    if phone not in current_accounts:
                        add_count += 1
                        status = "✅ 登录成功"
                        current_accounts.append(phone)
                        middleware.bucketSet('mrconli.ailuqiao.user', userid, json.dumps(current_accounts, ensure_ascii=False))
                    else:
                        update_count += 1
                        status = "✅ 更新成功"
                    # 强制刷新全局账户缓存
                    uservalue = json.dumps(current_accounts) 
                else:
                    fail_count += 1
                    status = "❌ 登录失败"
                    error_reasons.append(f"{phone[:3]}****{phone[-4:]}: 认证失败")
                # 进度反馈
                progress = f"[{index}/{total}] {phone[:3]}****{phone[-4:]} {status}"
                sender.reply(progress)       
        except Exception as e:
            fail_count += 1
            error_msg = f"{phone[:3]}****{phone[-4:]}: {str(e)}" if '#' in account else f"无效账号: {account}"
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


def get_user_info(uid, cookie):
    """获取用户信息"""
    try:
        url = f"{base_url}/myinfo?uid={uid}"
        headers = get_headers(uid, cookie)
        response = requests.get(url, headers=headers)
        result = response.json()
    #    sender.reply(f"获取用户信息结果: {json.dumps(result, ensure_ascii=False)}")
        if result.get("data"):
            user_data = result["data"]
            nickname = user_data.get("nickname", "未知用户")
            integral = user_data.get("integral", "0")
            mobile = user_data.get("mobile", "未绑定")   # 获取的格式为："153*****65"
            return mobile,nickname, integral
        return None, None, None
    except Exception as e:
        return None, None, None

def get_luck_records(uid, cookie):
    """获取红包记录"""
    number = int(middleware.bucketGet('mrconli.ailuqiao', 'number') or 5)
    try:
        url = f"{base_url}/my_luck?uid={uid}&cid=1028"
        headers = get_headers(uid, cookie)
        response = _send_request('GET',url, headers=headers)
        result = response.json()
        if not result.get("data"):
            return None
        records = result["data"]
        current_month = datetime.now().month
        current_year = datetime.now().year
        last_month = current_month - 1 if current_month > 1 else 12

        # 初始化统计变量
        total = 0.0
        current_month_total = 0.0
        last_month_total = 0.0
        latest_records = []
        for record in records:
            try:
                # 转换金额格式
                amount_str = record.get("draw", "0元").replace("元", "").strip()
                amount = float(amount_str)
                
                # 转换时间格式
                create_time = datetime.strptime(record["create_time"], "%Y-%m-%d %H:%M:%S")
                
                # 统计总金额
                total += amount
                
                # 统计本月金额
                if create_time.month == current_month and create_time.year == current_year:
                    current_month_total += amount
                
                # 统计上月金额
                if (create_time.month == last_month and current_month != 1) or \
                   (create_time.month == 12 and current_month == 1):
                    last_month_total += amount
                
                # 记录最近N次
                if len(latest_records) < number:
                    latest_records.append(f'[{amount:.2f}元] {create_time}')
                    show_records = '\n'.join(latest_records)
                
            except (ValueError, KeyError) as e:
                print(f"记录解析错误: {str(e)}")
                continue
        
        luck_records = (
            f"------------------------\n"
            f"🧧 历史汇总: {total:.2f}元\n"
            f"📈 本月累计: {current_month_total:.2f}元\n"
            f"📊 上月统计: {last_month_total:.2f}元\n"
            f"------------------------\n"
            f"🎁 最近{number}次红包:\n"
            f"{show_records}"
        )
        return luck_records
    except Exception as e:
        print(f"获取红包记录异常: {str(e)}")
        return None




def query():
    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply(
            '\n=====爱路桥账号查询=====\n❌ 未找到任何账号\n------------------\n💡 发送"爱路桥登录"绑定账号\n===================')
        return
    # 生成交互菜单
    if len(accounts) > 1:
        menu = "=====请选择查询账号=====\n[0] 查询全部账号\n------------------\n"
        for idx, acc in enumerate(accounts, 1):
            menu += f"[{idx}] {acc[:3]}****{acc[-4:]}\n"
        menu += "=======================\n⚠️ 请回复数字序号(输入q退出)"
        sender.reply(menu)

        # 获取用户输入
        choice = sender.input(30000, 1, False)
        if choice.lower() == 'q':
            sender.reply('已取消查询')
            return
        if not choice.isdigit():
            sender.reply('输入格式错误，请回复数字')
            return

        choice = int(choice)
        if choice < 0 or choice > len(accounts):
            sender.reply('选择超出范围，已取消查询')
            return
    else:
        choice = 1  # 单个账号直接查询

    # 执行查询逻辑
    if choice == 0:
        target_accounts = accounts
        sender.reply('正在查询全部账号...')
    else:
        target_accounts = [accounts[choice - 1]]
        sender.reply('正在查询爱路桥，请耐心等待...')

    for account in target_accounts:
        try:
            accountVip = middleware.bucketGet('mrconli.ailuqiao.auth', account)
            token = middleware.bucketGet('mrconli.ailuqiao.token', account)
            if not token:
                sender.reply(f'【{account}】token获取失败')
                continue
            if not accountVip:
                sender.reply(f'【{account}】账号未授权')
            elif accountVip < today_time:
                sender.reply(f'【{account}】云授权过期')
            else:
                uid, cookie = token.split('#')
                mobile,nickname, integral = get_user_info(uid, cookie)
                luck_records = get_luck_records(uid, cookie)
                if integral is None:
                    sender.reply('登录失败，无法获取积分信息')
                    continue
                else:
                    sender.reply(f"""
=====爱路桥账号详情=====
📱 账号: {account[:3]}****{account[-4:]}
👤 昵称: {nickname}
🌸 当前积分: {integral}
⏰ 到期时间: {accountVip}
{luck_records}
==================""")
        except Exception as e:
            sender.reply(f'【{account}】查询出错: {str(e)}')
        


def get_config():
    """获取插件配置"""
    try:
        coin_bucket = middleware.bucketGet('mrconli.ailuqiao', 'coin_bucket') or 'dd_sign_points'
        var_name = middleware.bucketGet('mrconli.ailuqiao', 'var_name') or "S_ALQ"
        if not var_name:
            print("未配置变量名，使用默认值: S_ALQ")
            var_name = 'S_ALQ'
            middleware.bucketSet('mrconli.ailuqiao', 'var_name', var_name)
        ql_config = middleware.bucketGet('mrconli.ailuqiao', 'ql_config')
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
        manage_cmd = middleware.bucketGet('mrconli.ailuqiao', 'manage_cmd') or '爱路桥管理'
        query_cmd = middleware.bucketGet('mrconli.ailuqiao', 'query_cmd') or '爱路桥查询'
        login_cmd = middleware.bucketGet('mrconli.ailuqiao', 'login_cmd') or '爱路桥登录'
        try:
            price = Decimal(middleware.bucketGet('mrconli.ailuqiao', 'price') or '1')
            if price < 0:
                raise ValueError("价格不能为负数")
        except (ValueError, decimal.InvalidOperation):
            print("价格配置无效，使用默认值: 1")
            price = Decimal('1')
            middleware.bucketSet('mrconli.ailuqiao', 'price', '1')
        try:
            coin_price = int(middleware.bucketGet('mrconli.ailuqiao', 'coin') or '0')
            if coin_price < 0:
                raise ValueError("积分不能为负数")
        except ValueError:
            print("积分配置无效，使用默认值: 0")
            coin_price = 0
            middleware.bucketSet('mrconli.ailuqiao', 'coin', '0')
        try:
            show_records = int(middleware.bucketGet('mrconli.ailuqiao', 'show_records') or '3')
            if show_records < 1:
                raise ValueError("显示记录数不能小于1")
        except ValueError:
            print("显示记录数配置无效，使用默认值: 3")
            show_records = 3
            middleware.bucketSet('mrconli.ailuqiao', 'show_records', '3')
        return (var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price,
                show_records, show_records)
    except Exception as e:
        error_msg = f"获取配置失败: {str(e)}"
        print(error_msg)
        sender.reply(f"❌ {error_msg}")
        raise


def init_qinglong():
    """初始化青龙连接"""
    try:
        ql_config = middleware.bucketGet('mrconli.ailuqiao', 'ql_config')
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
    is_cookie = middleware.bucketGet('mrconli.ailuqiao', 'is_cookie') or "false"
    uid, cookie = token.split('#')
    if is_cookie == "true":
        new_token = token
    else:
        new_token = f'{uid}'
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
            #    if isinstance(env, dict) and env.get('name') == var_name and account in env.get('remarks', ''):
            #    if isinstance(env, dict) and env.get('name') == var_name and env.get('remarks', '') and account in env.get('remarks', ''):
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
        auth_time = middleware.bucketGet('mrconli.ailuqiao.auth', account) or '未授权'
        data = {
            "name": var_name,
            "value": new_token,
            "remarks": f"爱路桥账号:{account}丨用户:{userid}丨授权时间:{auth_time}",
        }
        
        # 添加容错重试机制（新增）
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(url, headers=headers, json=[data])
            if response.status_code == 200:
                new_ids = [item['id'] for item in response.json().get('data', [])]
                middleware.bucketSet('mrconli.ailuqiao.env_id', account, json.dumps(new_ids))
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
        #    if env['name'] == var_name and account in env.get('remarks', ''):
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
    accounts = eval(uservalue or "[]")
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
------------------
账号列表:"""
    for i, account in enumerate(accounts, 1):
        token = middleware.bucketGet('mrconli.ailuqiao.token', account)
        auth = middleware.bucketGet('mrconli.ailuqiao.auth', account)
        auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        username = f"{account}"
        account_list += f"\n[{i}] {username[:3]}****{username[-4:]}\n    {auth_status}"
        if auth and auth > today:
            account_list += f"\n    授权到期: {auth}"
    account_list += "\n------------------\n回复数字选择账号\n回复'q'退出"

    sender.reply(account_list)
    choice = sender.listen(60000)

    # 处理用户选择
    if not choice:
        sender.reply("❌ 操作超时")
        return
    elif choice == 'q':
        sender.reply("✅ 已取消操作")
        return

    try:
        if choice == '01':
            # 删除全部账号逻辑
            accounts_copy = accounts.copy()
            for account in accounts:
                delete_account(account)
            middleware.bucketSet('mrconli.ailuqiao.user', userid, '[]')
            sender.reply("✅ 已删除全部账号")

        elif choice == '00':
            # 批量授权逻辑
            sender.reply("请输入授权天数(如使用积分兑换，必须为30的倍数):")
            days = sender.listen(60000)
            if not days:
                sender.reply("❌ 操作超时")
                return
            elif days == 'q':
                sender.reply("✅ 已取消授权")
                return
            # 新增配置获取（修复积分显示问题）
            coin_bucket = middleware.bucketGet('mrconli.ailuqiao', 'coin_bucket') or 'dd_sign_points'
            coin_price = int(middleware.bucketGet('mrconli.ailuqiao', 'coin') or '0')  # 确保获取最新积分价格

            try:
                days = int(days)
                if days <= 0:
                    raise ValueError("天数必须大于0")

                # 支付方式选择
                pay_choice = '1'
                if coin_price > 0:
                    user_coin = Decimal(middleware.bucketGet('coin_bucket', userid) or '0')
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
                            middleware.bucketSet('mrconli.ailuqiao.auth', account, auth_time)
                            token = middleware.bucketGet('mrconli.ailuqiao.token', account)
                            username = account
                            if token and username:
                                add_to_qinglong(token, account, username)

                            success_count += 1
                        sender.reply(f"""
=====批量授权成功=====
💰 支付: {amount}元
⏰ 时长: {days}天
✅ 成功: {success_count}个账号
====================""")

                # 积分支付处理
                elif pay_choice == '2':
                    coin_bucket = middleware.bucketGet('mrconli.ailuqiao', 'coin_bucket') or 'dd_sign_points'
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
                        middleware.bucketSet('mrconli.ailuqiao.auth', account, auth_time)
                        token = middleware.bucketGet('mrconli.ailuqiao.token', account)
                        username = account
                        if token and username:
                            add_to_qinglong(token, account, username)

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
                    env_id_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
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
    token = middleware.bucketGet('mrconli.ailuqiao.token', account)
    auth = middleware.bucketGet('mrconli.ailuqiao.auth', account)
    if len(token) == 32:
        username = f"Token...{token[-6:]}"
    else:
        username = f"{account}"
    auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
    auth_info = f"\n    到期: {auth}" if auth and auth > today else ""
    menu = f"""
=====账号操作=====
📱 账号: {username[:3]}****{username[-4:]}
🔐 状态: {auth_status}{auth_info}
------------------
[1] 授权账号
[2] 删除账号
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
        else:
            sender.reply("❌ 无效的选择")
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")


def auth_account(account):
    """账号授权"""
    try:
        # 从配置获取积分桶名称
        coin_bucket = middleware.bucketGet('mrconli.ailuqiao', 'coin_bucket') or 'dd_sign_points'
        user_coin = middleware.bucketGet(coin_bucket, userid) or '0'
        user_coin = Decimal(user_coin)  # 使用 Decimal 处理大数值
        month_coin = Decimal(coin_price)  # 从配置获取每月所需积分
        if month_coin <= 0:
            auth_guide = """
=====授权方式=====
[1] 微信支付
------------------
回复数字选择方式
回复"q"退出"""
        else:
            auth_guide = f"""
=====授权方式=====
[1] 微信支付
[2] 积分支付 (当前积分: {user_coin})
------------------
💰 积分比例: {month_coin}积分/月
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
            sender.reply("请输入授权天数:")
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
            if amount < Decimal('0.01'):
                amount = Decimal('0.01')
            payment_success = process_payment(amount, days)  # 处理支付
            if payment_success:  # 只有在支付成功的情况下才进行授权
                auth_time = calculate_auth_time(account, days / 30)
                middleware.bucketSet('mrconli.ailuqiao.auth', account, auth_time)
                # 新增强制更新青龙变量逻辑
                token = middleware.bucketGet('mrconli.ailuqiao.token', account)
                username = account  # 假设account存储的是手机号
                if token and username:
                    add_to_qinglong(token, account, username)  # 强制更新变量
                else:
                    sender.reply("⚠️ 令牌获取失败，请联系管理员")
                env_id_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
                if env_id_str:
                    env_ids = json.loads(env_id_str)
                    enable_in_qinglong(env_ids)
                sender.reply(f"""
=====授权成功=====
📱 账号: {account[:3]}****{account[-4:]}
💰 支付: {amount}元
⏰ 时长: {days}天
📅 到期: {auth_time}
==================""")
                return True
            else:
                sender.reply("❌ 支付未成功，授权未完成")
                return False
        elif choice == '2' and month_coin > 0:  # 只有积分支付开启时才处理
            sender.reply("请输入授权月数:")
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
            middleware.bucketSet('mrconli.ailuqiao.auth', account, auth_time)
            token = middleware.bucketGet('mrconli.ailuqiao.token', account)
            username = account  # 假设account存储的是手机号
            if token and username:
                add_to_qinglong(token, account, username)  # 强制更新变量
            else:
                sender.reply("⚠️ 令牌获取失败，请联系管理员")

            env_id_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
            if env_id_str:
                env_ids = json.loads(env_id_str)
                enable_in_qinglong(env_ids)
            sender.reply(f"""
=====授权成功=====
📱 账号: {account[:3]}****{account[-4:]}
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
🎫 商品: 爱路桥授权
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
    auth = middleware.bucketGet('mrconli.ailuqiao.auth', account)
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
    users = middleware.bucketAllKeys('mrconli.ailuqiao.user')
    cleaned = 0
    for user in users:
        accounts = eval(middleware.bucketGet('mrconli.ailuqiao.user', user) or '[]')
        valid = []
        for account in accounts:
            auth = middleware.bucketGet('mrconli.ailuqiao.auth', account)
            if not auth or auth <= str(datetime.now().date()):
                middleware.bucketDel('mrconli.ailuqiao.token', account)
                middleware.bucketDel('mrconli.ailuqiao.auth', account)
                middleware.bucketDel('mrconli.ailuqiao.env_id', account)
                cleaned += 1
            else:
                valid.append(account)
        if valid:
            middleware.bucketSet('mrconli.ailuqiao.user', user, str(valid))
        else:
            middleware.bucketDel('mrconli.ailuqiao.user', user)
    sender.reply(f"✅ 已清理 {cleaned} 个过期账号")


def cron_task():
    """定时任务处理"""
    if imtype != 'fake':
        return
    try:
        users = middleware.bucketAllKeys('mrconli.ailuqiao.user')
        for user in users:
            accounts = eval(middleware.bucketGet('mrconli.ailuqiao.user', user) or '[]')
            for account in accounts:
                try:
                    token = middleware.bucketGet('mrconli.ailuqiao.token', account)
                    if not status:
                        continue
                    auth = middleware.bucketGet('mrconli.ailuqiao.auth', account)
                    if auth and auth <= today:
                        env_id_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
                        if env_id_str:
                            env_ids = json.loads(env_id_str)
                            disable_in_qinglong(env_ids)
                        notify_user(user, account, "授权已过期,环境变量已禁用,请及时续费")
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
=====账号通知=====
📱 账号: {account}
📢 消息: {message}
=================="""
        middleware.push('qq', '', user, '', notify_msg)
        middleware.push('wx', '', user, '', notify_msg)
        middleware.push('tg', '', user, '', notify_msg)
    except Exception as e:
        print(f"发送通知失败: {str(e)}")


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
        logs = eval(middleware.bucketGet('mrconli.ailuqiao.logs', 'operations') or '[]')
        logs.append(log)
        if len(logs) > 1000:  # 只保留最近1000条
            logs = logs[-1000:]
        middleware.bucketSet('mrconli.ailuqiao.logs', 'operations', str(logs))
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
    users = middleware.bucketAllKeys('mrconli.ailuqiao.user')
    total_users = len(users)
    total_accounts = 0
    success = 0
    failed = 0
    for user in users:
        accounts = eval(middleware.bucketGet('mrconli.ailuqiao.user', user) or '[]')
        for account in accounts:
            total_accounts += 1
            try:   
                token = middleware.bucketGet('mrconli.ailuqiao.token', account)
                if token:
                    add_to_qinglong(token, account, user)
                env_ids_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
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
请输入授权天数
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
        users = middleware.bucketAllKeys('mrconli.ailuqiao.user')
        success = 0
        failed = 0
        for user in users:
            accounts = eval(middleware.bucketGet('mrconli.ailuqiao.user', user) or '[]')
            for account in accounts:
                try:
                    auth_time = calculate_auth_time(account, days / 30)
                    middleware.bucketSet('mrconli.ailuqiao.auth', account, auth_time)
                    token = middleware.bucketGet('mrconli.ailuqiao.token', account)
                    if token:
                        phone = account[:3] + '*' * 4 + account[7:]
                        add_to_qinglong(token, account, phone)
                    env_ids_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
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
请输入用户ID
(发送myuid可获取ID)
------------------
回复"q"退出""")
    user_id = sender.listen(60000)
    if not user_id or user_id == 'q':
        return
    accounts = eval(middleware.bucketGet('mrconli.ailuqiao.user', user_id) or '[]')
    if not accounts:
        sender.reply("❌ 未找到该用户的账号")
        return
    account_list = """
=====账号列表=====
[0] 授权全部账号"""
    for i, account in enumerate(accounts, 1):
        auth = middleware.bucketGet('mrconli.ailuqiao.auth', account)
        status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        account_list += f"\n[{i}] {account[:3]}****{account[-4:]}\n    {status}"
    account_list += """
------------------
回复数字选择账号
回复"q"退出"""
    sender.reply(account_list)
    choice = sender.listen(60000)
    if not choice or choice == 'q':
        return
    try:
        sender.reply("""
=====设置授权时间=====
请输入授权天数
------------------
回复数字设置天数
回复"q"退出""")
        days = sender.listen(60000)
        if not days or days == 'q':
            return
        days = int(days)
        if days <= 0:
            raise ValueError()
        if choice == '0':
            for account in accounts:
                try:
                    auth_time = calculate_auth_time(account, days / 30)
                    middleware.bucketSet('mrconli.ailuqiao.auth', account, auth_time)
                    token = middleware.bucketGet('mrconli.ailuqiao.token', account)
                    if token:
                        phone = account[:3] + '*' * 4 + account[7:]
                        add_to_qinglong(token, account, phone)
                    env_ids_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
                    if env_ids_str:
                        env_ids = json.loads(env_ids_str)
                        enable_in_qinglong(env_ids)
                    log_operation('auth', user_id, account, 'success')
                except Exception as e:
                    log_operation('auth', user_id, account, 'failed', str(e))
            sender.reply(f"✅ 已授权所有账号 {days}天")
        else:
            index = int(choice) - 1
            if not 0 <= index < len(accounts):
                raise ValueError()
            account = accounts[index]
            auth_time = calculate_auth_time(account, days / 30)
            middleware.bucketSet('mrconli.ailuqiao.auth', account, auth_time)
            token = middleware.bucketGet('mrconli.ailuqiao.token', account)
            if token:
                phone = account[:3] + '*' * 4 + account[7:]
                add_to_qinglong(token, account, phone)
            env_ids_str = middleware.bucketGet('mrconli.ailuqiao.env_id', account)
            if env_ids_str:
                env_ids = json.loads(env_ids_str)
                enable_in_qinglong(env_ids)
            sender.reply(f"""
=====授权成功=====
📱 账号: {account[:3]}****{account[-4:]}
⏰ 时长: {days}天
📅 到期: {auth_time}
==================""")
            log_operation('auth', user_id, account, 'success')
    except ValueError:
        sender.reply("❌ 无效的输入")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")
        log_operation('auth', user_id, account, 'failed', str(e))


def check_account_status(self, token):
    """检查账号状态"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "service": "media",
        "api": "lottery/queryActivityAwardRecordList",
        "data": {
            "uid": "30a7f9016d224fc2a8367200cbbab62a",
            "content": "null"}
    }
    response = _send_request(
        'POST',
        "https://app.eyh.cn/gateway/api",
        json=data,
        headers=headers
    )
    return response


def delete_account(account):
    """删除账号"""
    try:
        if not delete_from_qinglong(account):
            raise Exception("从青龙删除变量失败")
        middleware.bucketDel('mrconli.ailuqiao.token', account)
        middleware.bucketDel('mrconli.ailuqiao.auth', account)
        middleware.bucketDel('mrconli.ailuqiao.env_id', account)
        # 安全解析用户列表
        try:
            accounts = eval(uservalue or "[]")
        except (json.JSONDecodeError, TypeError) as e:
            print(f"用户列表解析失败: {str(e)}")
            accounts = []
        
        # 校验账号存在性并更新
        if account in accounts:
            accounts.remove(account)
            try:
                middleware.bucketSet('mrconli.ailuqiao.user', userid, json.dumps(accounts, ensure_ascii=False))
            except Exception as e:
                raise Exception(f"用户列表更新失败: {str(e)}")
        sender.reply(f"""
=====删除成功=====
📱 账号: {account[:3]}****{account[-4:]}
✅ 状态: 已删除
==================""")
        log_operation('delete_account', userid, account, 'success')
        return True
    except Exception as e:
        error_msg = f"删除账号失败: {str(e)}"
        sender.reply(f"❌ {error_msg}")
        log_operation('delete_account', userid, account, 'failed', str(e))
        return False


async def async_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()


@lru_cache(maxsize=100)
def cached_bucket_get(bucket, key):
    return middleware.bucketGet(bucket, key)


async def async_login():
    token = await async_request("https://app.eyh.cn/gateway/api", login_data)
    if token:
        await async_add_to_qinglong(token)


def tutorial():
    """显示爱路桥使用教程"""
    tutorial_text = (
        "=====爱路桥教程=====\n"
        "📝 入口:\n"
        "    应用商店下载“爱路桥”app，第一次使用微信登录，然后绑定手机号\n"
        "🌟 基础指令:\n"
        "1. 爱路桥登录 - 绑定账号\n"
        "2. 爱路桥查询 - 查看状态\n"
        "3. 爱路桥抽奖 - 参与抽奖\n"
        "4. 爱路桥管理 - 管理账号\n"
        "5. 爱路桥授权 - 管理员授权账号\n"
        "6. 爱路桥清理 - 管理员清理过期\n"
        "-------------------\n"
        "🚩 收益说明:\n"
        "▸ 呆瓜为每日自动运行阅读抽奖\n"
        "▸ 自动提现到微信\n"
        "▸ 积分还可以兑换实物\n"
        "-------------------\n"
        "⚠️ 注意事项:\n"
        "1. 建议私聊登录更安全\n"
        "=================="
    )
    sender.reply(tutorial_text)


def main():
    """主函数"""
    message = sender.getMessage()
    if '登录' in message or '登陆' in message or '上车' in message:
        bind()
    elif '管理' in message:
        manage_accounts()
    elif '查询' in message:
        query()
    elif '教程' in message:
        tutorial()
    elif message == '爱路桥清理':
        clean_expired()
    elif message == '爱路桥授权' and sender.isAdmin():
        admin_auth()


if __name__ == "__main__":
    try:
        var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price, show_records, show_records = get_config()
        ql_url, ql_token = init_qinglong()
        imtype = sender.getImtype()
        today = str(datetime.now().date())
        if imtype == 'fake':
            cron_task()
        else:
            main()
    except Exception as e:
        sender.reply(f"❌ 运行出错: {str(e)}")
