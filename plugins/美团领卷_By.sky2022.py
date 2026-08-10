#[pin:false]
# [disable:true]
# [rule: ^(美团领劵|美团领卷|美团领券|美团加白|领卷余额查询)$]
# [admin: false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [public: true]
# [title: 美团领卷]
# [icon: https://q6.itc.cn/images01/20240412/04c3902c5fba4ade86ca6082d064f855.jpeg]
# [category: 娱乐类]
# [author:sky2022]
# [version: 1.4.4]
# [price: 0]
# [admin: false]
# [service: sky2022]
# [description: 指令：美团领卷、美团加白、领卷余额查询<br>需要找作者获取token并充值，领卷成功扣除token值！<br>普通券种包含[20-6、25-9、33-10、37-11、60-30、28-13、38-18]<br>更新：优化赞赏码支付，同时新增码支付，需使用市场卡密系统！<br>更新：新增次数支付，用户如果付款后领取失败，返还一次领取次数，在下一次领取时可使用！<br>更新：新增积分支付功能，支持使用积分进行领券支付！]
# [param: {"required":true,"key":"bd_mtconfig.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"bd_mtconfig.money","bool":false,"placeholder":"例:0.88","name":"领券价格","desc":"领取一次券需要多少钱(单位:元)"}]
# [param: {"required":true,"key":"bd_mtconfig.token","bool":false,"placeholder":"必填项","name":"Token","desc":"计费的token值，请找插件作者获取！"}]
# [param: {"required":true,"key":"bd_mtconfig.is_free","bool":true,"placeholder":"","name":"是否免费领券","desc":"开启后用户无需付费即可领券"}]
# [param: {"required":true,"key":"bd_mtconfig.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]
# [param: {"required":true,"key":"bd_mtconfig.use_point_pay","bool":true,"placeholder":"","name":"开启积分支付","desc":"是否允许用户使用积分支付"}]
# [param: {"required":true,"key":"bd_mtconfig.point_price","bool":false,"placeholder":"例:100","name":"积分支付价格","desc":"领取一次券需要多少积分（只能为整数）"}]
# [param: {"required":true,"key":"bd_mtconfig.lock_timeout","bool":false,"placeholder":"例:300,默认300秒","name":"支付锁超时时间","desc":"支付锁定超时自动释放时间(单位:秒)"}]
import requests
import middleware
import re
import json
from decimal import Decimal, InvalidOperation
import hashlib
import time
from urllib.parse import parse_qs, parse_qsl, unquote, urlencode, urlsplit, urlunsplit

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()  # Changed from userID to userid for consistency
usermessage = sender.getMessage()
zsm = middleware.bucketGet('bd_mtconfig', 'zsm') or '' 
try:
    money_str = middleware.bucketGet('bd_mtconfig', 'money') or '0.2'
    money = Decimal(money_str.strip()) 
except (InvalidOperation, TypeError):
    money = Decimal('0.2') 
token = middleware.bucketGet('bd_mtconfig', 'token') or '' 
is_free = middleware.bucketGet('bd_mtconfig', 'is_free') == 'true' 
use_ma_pay = middleware.bucketGet('bd_mtconfig', 'use_ma_pay') == 'true' 

# 读取积分支付配置
use_point_pay = middleware.bucketGet('bd_mtconfig', 'use_point_pay') == 'true'
try:
    point_price = int(middleware.bucketGet('bd_mtconfig', 'point_price') or '0')
except (ValueError, TypeError):
    point_price = 0

# 读取支付锁超时时间配置
try:
    lock_timeout = int(middleware.bucketGet('bd_mtconfig', 'lock_timeout') or '30') 
except (ValueError, TypeError):
    lock_timeout = 30 

# Flask API接口地址
FLASK_API_BASE = "https://mt.linzixuan.top/api"
COUPON_API_URL = f"{FLASK_API_BASE}/coupons"
TOKEN_API_URL = f"{FLASK_API_BASE}/token"

# 添加固定的 User-Agent
DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

URL_CANDIDATE_PATTERN = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+", re.IGNORECASE)
TOKEN_QUERY_PATTERN = re.compile(r"(?:[?&])token=([^&#\s]+)", re.IGNORECASE)
TOKEN_HEAD_PATTERN = re.compile(r"[A-Za-z0-9._\-+/=]+")


def sanitize_meituan_token(raw_token):
    """清洗token，去除末尾脏字符，兼容URL编码"""
    if not raw_token:
        return ''

    token_text = raw_token.strip()
    for _ in range(2):
        decoded = unquote(token_text)
        if decoded == token_text:
            break
        token_text = decoded

    # parse_qs 会把 + 视为空格，这里做一次还原
    token_text = token_text.replace(' ', '+')
    head_match = TOKEN_HEAD_PATTERN.match(token_text)
    if not head_match:
        return ''
    return head_match.group(0)


def extract_meituan_login_data(raw_input):
    """从用户输入中稳健提取 token 和美团链接"""
    if not raw_input:
        return '', ''

    text = raw_input.strip().replace('&amp;', '&')
    queue = [text]
    seen = set()

    while queue:
        candidate = queue.pop(0).strip()
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)

        url_matches = URL_CANDIDATE_PATTERN.findall(candidate)
        if candidate.lower().startswith('http') and candidate not in url_matches:
            url_matches.insert(0, candidate)

        for url in url_matches:
            cleaned_url = url.replace('&amp;', '&')

            # 优先从原始query中提取，避免被其他文本污染
            token_match = TOKEN_QUERY_PATTERN.search(cleaned_url)
            if token_match:
                token_value = sanitize_meituan_token(token_match.group(1))
                if token_value:
                    return token_value, cleaned_url

            # 兼容嵌套跳转URL参数（如 redirect/url/jump）
            parsed = urlsplit(cleaned_url)
            if parsed.query:
                query_dict = parse_qs(parsed.query, keep_blank_values=True)
                token_list = query_dict.get('token') or query_dict.get('Token') or query_dict.get('TOKEN')
                if token_list:
                    token_value = sanitize_meituan_token(token_list[0])
                    if token_value:
                        return token_value, cleaned_url

                for key, values in query_dict.items():
                    key_lower = key.lower()
                    if 'url' in key_lower or 'redirect' in key_lower or 'target' in key_lower or 'jump' in key_lower:
                        for value in values:
                            value = value.strip()
                            if value:
                                queue.append(value)

        decoded_candidate = unquote(candidate)
        if decoded_candidate != candidate:
            queue.append(decoded_candidate)

    # 兼容纯 token=xxx 文本提交
    fallback_match = re.search(r"(?i)(?:^|[?&\s])token=([A-Za-z0-9._\-+/=%]+)", text)
    if fallback_match:
        token_value = sanitize_meituan_token(fallback_match.group(1))
        if token_value:
            return token_value, ''

    return '', ''


def normalize_meituan_link(link, token_value):
    """规范化链接，确保提交给后端的是干净 token"""
    if token_value and not link:
        return f"https://i.meituan.com/mttouch/page/account?{urlencode({'token': token_value})}"

    if not link:
        return ''

    cleaned_link = link.replace('&amp;', '&')
    parsed = urlsplit(cleaned_link)
    query_pairs = parse_qsl(parsed.query, keep_blank_values=True)

    new_pairs = []
    token_replaced = False
    for key, value in query_pairs:
        if key.lower() == 'token':
            new_pairs.append((key, token_value))
            token_replaced = True
        else:
            new_pairs.append((key, value))

    if token_value and not token_replaced:
        new_pairs.append(('token', token_value))

    normalized_query = urlencode(new_pairs, doseq=True)
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, normalized_query, parsed.fragment))

def check_token_balance():
    """检查token余额"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {'token': token}
        response = requests.post(f"{TOKEN_API_URL}/balance", headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return result.get('data', {}).get('balance', 0)
        return 0
    except Exception as e:
        sender.reply(f"检查token余额失败，请检查接口是否正常！")
        return 0

def deduct_token(amount=0.15):
    """扣除token"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            'token': token,
            'amount': amount,
            'force_charge': not is_free  # 根据是否免费模式决定是否强制收费
        }
       
        response = requests.post(f"{TOKEN_API_URL}/deduct", headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            return result.get('success', False)
        return False
    except Exception as e:
        sender.reply(f"扣除token失败")
        return False

# 这些函数已经移到Flask API中，不再需要

def fetch_coupons_from_flask_api(mt_cookie):
    """通过Flask API领取券"""
    try:
        headers = {'Content-Type': 'application/json'}
        data = {
            'mt_cookie': mt_cookie,
            'token': token,
            'free_mode': is_free
        }
        response = requests.post(f"{COUPON_API_URL}/fetch", headers=headers, json=data, timeout=60)
        try:
            result = response.json()
            response_data = result.get('data', {})
            # 处理补偿逻辑
            if response_data.get('compensation'):
                add_user_tickets(userid, 1, 'normal')
                sender.reply(response_data.get('compensation_message', '未领到目标券，已自动补偿'))
                sender.reply(f"💳 当前剩余次数: {get_user_tickets(userid, 'normal')}次")
            if result.get('success'):
                coupons = response_data.get('coupons', [])
                details = response_data.get('details', [])
                for detail in details:
                    if detail.get('success'):
                        sender.reply(f"✅ {detail.get('name')} 领取成功")
                    else:
                        sender.reply(f"❌ {detail.get('message')}")
                return coupons
            else:
                error_message = result.get('message', '未知错误')
                sender.reply(f"❌ {error_message}")
                return []
        except json.JSONDecodeError:
            sender.reply(f"❌ Flask API请求失败：HTTP {response.status_code}")
            return []
    except requests.exceptions.RequestException as e:
        sender.reply(f"❌ 网络请求出错：{str(e)}")
        return []
    except Exception as e:
        sender.reply(f"❌ 处理过程出错：{str(e)}")
        return []


def get_user_tickets(user_id, ticket_type='normal'):
    """获取用户剩余次数"""
    bucket_key = f'mt_user_tickets_{ticket_type}'
    tickets = middleware.bucketGet(bucket_key, str(user_id)) or '0'
    return int(tickets)

def add_user_tickets(user_id, count=1, ticket_type='normal'):
    """增加用户次数"""
    bucket_key = f'mt_user_tickets_{ticket_type}'
    current = get_user_tickets(user_id, ticket_type)
    middleware.bucketSet(bucket_key, str(user_id), str(current + count))

def use_user_ticket(user_id, ticket_type='normal'):
    """使用一次次数，如果有次数则返回True，否则返回False"""
    bucket_key = f'mt_user_tickets_{ticket_type}'
    current = get_user_tickets(user_id, ticket_type)
    if current > 0:
        middleware.bucketSet(bucket_key, str(user_id), str(current - 1))
        return True
    return False

def process_payment(custom_price=None):
    """处理支付流程"""
    payment_result = (False, False)  # 默认返回值
    
    try:
        # 检查是否有其他用户正在支付
        if middleware.bucketGet('mt_payment_lock', 'lock_status') == 'locked':
            lock_user = middleware.bucketGet('mt_payment_lock', 'lock_user') or '未知用户'
            current_timestamp = time.time()
            lock_start_time = float(middleware.bucketGet('mt_payment_lock', 'lock_start_time') or '0')
            
            # 检查是否超时
            if current_timestamp - lock_start_time > lock_timeout:
                # 超时自动释放锁
                middleware.bucketSet('mt_payment_lock', 'lock_status', 'unlocked')
                middleware.bucketSet('mt_payment_lock', 'lock_user', '')
                middleware.bucketSet('mt_payment_lock', 'lock_time', '')
                middleware.bucketSet('mt_payment_lock', 'lock_start_time', '')
            else:
                # 计算剩余时间
                remaining_time = int(lock_timeout - (current_timestamp - lock_start_time))
                sender.reply(f"""=====支付锁定中=====
⚠️ 当前有其他用户正在支付
👤 用户: {lock_user}
⌛ 剩余: {remaining_time}秒
------------------
请稍后再试！
==================""")
                return False, False

        # 设置支付锁
        middleware.bucketSet('mt_payment_lock', 'lock_status', 'locked')
        middleware.bucketSet('mt_payment_lock', 'lock_user', str(userid))
        middleware.bucketSet('mt_payment_lock', 'lock_time', time.strftime('%Y-%m-%d %H:%M:%S'))
        middleware.bucketSet('mt_payment_lock', 'lock_start_time', str(time.time()))

        # 检查支付配置
        if not zsm and not use_ma_pay and not (use_point_pay and point_price > 0):
            sender.reply('未配置收款方式,请联系管理员!')
            payment_result = (False, False)
            return payment_result

        # 获取用户剩余次数（根据券种类型）
        ticket_type = 'normal' if custom_price is None or custom_price == money else 'premium'
        user_tickets = get_user_tickets(userid, ticket_type)
        
        # 获取用户积分余额（参考顺丰插件的积分数据桶）
        user_points = int(middleware.bucketGet('dd_sign_points', str(userid)) or '0')
        
        # 获取价格配置
        if custom_price is not None:
            # 使用传入的自定义价格
            current_price = Decimal(str(custom_price))
        else:
            # 使用默认配置价格
            money_str = middleware.bucketGet('bd_mtconfig', 'money') or '0.2'
            current_price = Decimal(money_str.strip()) if money_str.strip() else Decimal('0.2')
        
        # 构建支付选择菜单
        pay_menu = """=====选择支付方式===="""
        options_map = {}
        option_num = 1

        # 码支付配置
        ma_pay_config = None
        if use_ma_pay:
            ma_pay_config = {
                'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
                'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
                'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
                'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
                'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
                'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
                'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
            }
            if ma_pay_config['switch'].lower() != 'true' or not all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                ma_pay_config = None

        show_wechat_pay = bool(zsm) and not use_ma_pay
        show_ma_pay = use_ma_pay and bool(ma_pay_config)

        # 添加次数支付选项（只有有剩余次数时才显示）
        if user_tickets > 0:
            pay_menu += f"""
0️⃣ 使用次数支付
   💳 剩余次数: {user_tickets}次"""
            options_map['0'] = 'ticket'

        # 添加微信支付选项
        if show_wechat_pay:
            pay_menu += f"""
{option_num}️⃣ 微信支付
   💰 {current_price}元"""
            options_map[str(option_num)] = 'wechat'
            option_num += 1
        
        # 添加码支付选项
        if show_ma_pay:
            pay_menu += f"""
{option_num}️⃣ 码支付
   💰 {current_price}元"""
            options_map[str(option_num)] = 'ma'
            option_num += 1

        # 添加积分支付选项（只有开启积分支付且配置了积分价格时才显示）
        if use_point_pay and point_price > 0:
            pay_menu += f"""
{option_num}️⃣ 积分支付
   🎯 {point_price}积分
   💫 当前积分: {user_points}"""
            options_map[str(option_num)] = 'points'

        pay_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""

        sender.reply(pay_menu)
        choice = sender.input(60000, 1, False)
        
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消支付")
            payment_result = (False, False)
            return payment_result

        selected_pay = options_map.get(choice)
        if not selected_pay:
            sender.reply("❌ 输入无效")
            payment_result = (False, False)
            return payment_result
        
        elif selected_pay == 'ticket' and user_tickets > 0:
            # 使用次数支付
            if use_user_ticket(userid, ticket_type):
                sender.reply(f"""=====使用次数支付=====
✅ 支付成功
💳 剩余次数: {get_user_tickets(userid, ticket_type)}次
==================""")
                payment_result = (True, False)
                return payment_result
            else:
                sender.reply("❌ 次数不足")
                payment_result = (False, False)
                return payment_result
        
        elif selected_pay == 'wechat' and show_wechat_pay:
            # 微信支付流程
            zfzt = sender.atWaitPay()
            if zfzt:
                sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
                payment_result = (False, False)
                return payment_result
                
            pay_msg = f"""=====微信扫码支付====
🎫 商品: 美团领券
💰 金额: {current_price}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
            sender.reply(pay_msg)
            sender.replyImage(zsm)
            
            ddzf = sender.waitPay("q", 100 * 1000)
            
            if str(ddzf) == 'q':
                sender.reply('✅ 已取消支付')
                payment_result = (False, False)
                return payment_result
                
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
                        payment_result = (False, False)
                        return payment_result
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
                                payment_time = str(ddzf).split("到账时间")[1].split("\n")[0].strip()
                                Money = float(amount)
                                Time = payment_time
                                From = ''
                            except Exception as e:
                                sender.reply(f"❌ 解析收款信息失败: {str(e)}")
                                payment_result = (False, False)
                                return payment_result
                        else:
                            sender.reply("❌ 无法解析支付结果")
                            payment_result = (False, False)
                            return payment_result
                
                if float(Money) >= float(current_price):
                    sender.reply(f"""=====支付成功=====
💰 支付金额: {Money}元
{f'👤 付款人: {From}' if From else ''}
==================""")
                    payment_result = (True, True)  # 返回支付成功和需要补偿标记
                    return payment_result
                else:
                    sender.reply(f"""=====支付金额错误=====
💰 应付: {current_price}元
💳 实付: {Money}元
{f'👤 付款人: {From}' if From else ''}

❗ 请联系管理员处理退款！
==================""")
                    payment_result = (False, False)
                    return payment_result
            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                payment_result = (False, False)
                return payment_result
            
        elif selected_pay == 'ma' and show_ma_pay:
            # 码支付流程
            pay_cfg = ma_pay_config
            if not pay_cfg:
                sender.reply("❌ 码支付配置异常，请联系管理员")
                payment_result = (False, False)
                return payment_result

            out_trade_no = f"MT{int(time.time())}{userid}"
            params = {
                'pid': pay_cfg['pid'],
                'type': (pay_cfg.get('type') or 'alipay,wxpay,qqpay').split(',')[0],
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-美团领券-{str(current_price)}",
                'money': str(current_price),
                'param': userid
            }
            if pay_cfg.get('notify_url'):
                params['notify_url'] = pay_cfg['notify_url']
            if pay_cfg.get('return_url'):
                params['return_url'] = pay_cfg['return_url']

            params = {k: v for k, v in params.items() if v}
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + pay_cfg['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'

            gateway = pay_cfg['gateway'].rstrip('/')
            submit_url = gateway + '/mapi.php'

            try:
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                response = requests.post(submit_url, data=params, headers=headers, timeout=10)
                if response.status_code != 200:
                    sender.reply(f"❌ 创建支付订单失败，HTTP状态码: {response.status_code}")
                    payment_result = (False, False)
                    return payment_result

                result = response.json()
                if result.get('code') != 1:
                    sender.reply(f"❌ 创建支付订单失败: {result.get('msg', '未知错误')}")
                    payment_result = (False, False)
                    return payment_result

                pay_url = result.get('payurl', '')
                if not pay_url:
                    sender.reply("❌ 未获取到支付链接")
                    payment_result = (False, False)
                    return payment_result

                sender.reply(f"""=====码支付=====
🎫 商品: 美团领券
💰 金额: {current_price}元
⏰ 有效期: 5分钟
------------------
请点击链接完成支付:
{pay_url}

💡 支付过程中输入"q"可取消支付
==================""")

                for _ in range(60):
                    result_input = sender.listen(5000)
                    if result_input == 'q' or result_input == 'Q':
                        sender.reply("✅ 已取消支付")
                        payment_result = (False, False)
                        return payment_result

                    check_url = gateway
                    if '/xpay/epay/api.php' not in check_url:
                        check_url = f"{check_url}/xpay/epay/api.php"
                    check_params = {
                        'act': 'order',
                        'pid': pay_cfg['pid'],
                        'key': pay_cfg['key'],
                        'out_trade_no': out_trade_no
                    }
                    try:
                        check_resp = requests.get(check_url, params=check_params, timeout=10)
                        check_result = check_resp.json()
                        if check_result.get('code') == 1 and check_result.get('status') == 1:
                            sender.reply(f"""=====支付成功=====
💰 支付金额: {current_price}元
==================""")
                            payment_result = (True, True)
                            return payment_result
                    except:
                        continue

                sender.reply("❌ 支付超时,请重新发起支付!")
                payment_result = (False, False)
                return payment_result
            except Exception as e:
                sender.reply(f"❌ 支付请求失败: {str(e)}")
                payment_result = (False, False)
                return payment_result
        
        elif selected_pay == 'points' and use_point_pay and point_price > 0:
            # 积分支付流程
            if user_points < point_price:
                sender.reply(f"""=====积分不足=====
👤 当前积分: {user_points}
📍 需要积分: {point_price}
❌ 积分不足，请选择其他支付方式
==================""")
                payment_result = (False, False)
                return payment_result
                
            confirm_msg = f"""=====积分支付确认=====
🎫 商品: 美团领券
💫 消耗积分: {point_price}
💰 剩余积分: {user_points - point_price}
------------------
确认使用积分支付？
[y] 确认支付
[n] 取消支付
=================="""
            sender.reply(confirm_msg)
            
            confirm = sender.input(60000, 1, False)
            if confirm == 'y' or confirm == 'Y' or confirm == '是':
                try:
                    # 扣除积分
                    new_balance = user_points - point_price
                    middleware.bucketSet('dd_sign_points', str(userid), str(new_balance))
                    
                    sender.reply(f"""=====积分支付成功=====
💫 扣除积分: {point_price}
💰 剩余积分: {new_balance}
✅ 支付成功
==================""")
                    payment_result = (True, False)  # 积分支付成功，不需要补偿
                    return payment_result
                except Exception as e:
                    sender.reply(f"""=====积分支付失败=====
❌ 积分处理失败
------------------
错误信息: {str(e)}
==================""")
                    payment_result = (False, False)
                    return payment_result
            elif confirm == 'n' or confirm == 'N' or confirm == '否':
                sender.reply("✅ 已取消积分支付")
                payment_result = (False, False)
                return payment_result
            else:
                sender.reply("❌ 输入无效，已取消支付")
                payment_result = (False, False)
                return payment_result
        else:
            sender.reply("❌ 输入无效")
            payment_result = (False, False)
            return payment_result
            
    except Exception as e:
        sender.reply(f"❌ 支付处理发生错误: {str(e)}")
        payment_result = (False, False)
    
    finally:
        # 在finally块中安全地释放支付锁，避免异常影响主流程
        try:
            middleware.bucketSet('mt_payment_lock', 'lock_status', 'unlocked')
            middleware.bucketSet('mt_payment_lock', 'lock_user', '')
            middleware.bucketSet('mt_payment_lock', 'lock_time', '')
            middleware.bucketSet('mt_payment_lock', 'lock_start_time', '')
        except:
            # 静默处理锁释放异常，不影响支付结果
            pass
    
    return payment_result

def refund_token(amount):
    headers = {'Content-Type': 'application/json'}
    data = {'token': token, 'amount': float(amount)}
    try:
        response = requests.post(f"{TOKEN_API_URL}/refund", headers=headers, json=data, timeout=10)
        return response.status_code == 200 and response.json().get('success')
    except Exception as e:
        sender.reply("Token返还失败，请联系管理员")
        return False

if __name__ == "__main__":
    if '美团加白' in usermessage:
        # 发送引导图片
        sender.replyImage("https://i.mji.rip/2025/07/20/13f99df7dea6158d4feed5a699861c57.png")
        sender.reply("请发送您需要加白的账号店铺链接")
        
        # 等待用户输入链接
        shop_link = sender.input(120000, 1, False)
        
        if shop_link == "error":
            sender.reply("输入超时，退出任务")
            exit()
            
        try:
            # 通过Flask API加白
            headers = {'Content-Type': 'application/json'}
            data = {'shop_link': shop_link}
            
            response = requests.post(f"{COUPON_API_URL}/white", headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    sender.reply("✅ 刷白成功！")
                else:
                    sender.reply(f"❌ {result.get('message')}")
            else:
                sender.reply(f"❌ Flask API请求失败：HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            sender.reply(f"网络请求出错：{str(e)}")
        except Exception as e:
            sender.reply(f"处理过程出错：{str(e)}")
            
    elif '领卷余额查询' in usermessage:
        if not token:
            sender.reply("❌ 未配置Token值，请联系管理员")
            exit(0)
            
        # 检查token余额
        balance = check_token_balance()
        if balance >= 0:
            sender.reply(f"""=====Token余额=====
💰 当前余额: {balance}
==================""")
        else:
            sender.reply("❌ 查询余额失败，请联系管理员")
            
    elif '美团' in usermessage:
        if not token:
            sender.reply("❌ 未配置Token值，请联系管理员")
            exit(0)
            
        # 检查token余额
        balance = check_token_balance()
        if balance < 0.2:
            sender.reply("❌ Token余额不足，请联系管理员")
            exit(0)

        # 如果不是免费模式，需要检查收款码和价格配置
        if not is_free:
            if not (zsm or use_ma_pay or (use_point_pay and point_price > 0)):
                sender.reply("❌ 未配置收款方式，请联系管理员")
                exit(0)
                
            if money <= 0 and not (use_point_pay and point_price > 0):
                sender.reply("❌ 未配置领券价格，请联系管理员")
                exit(0)
            
        # 第一步：获取美团登录链接
        sender.replyImage("https://img.cdn1.vip/i/6a032ef4e7f50_1778593524.webp")
        sender.reply("""=====美团领券=====
普通套券[28-18、38-15等]
------------------
请发送美团账号链接
==================""")
        mt = sender.input(120000, 1, False)

        if mt == "error":
            sender.reply("输入超时，退出任务")
            exit()

        # 提取并清洗token（兼容URL后附带文本/嵌套跳转参数）
        meituan_token, extracted_link = extract_meituan_login_data(mt)
        if not meituan_token:
            sender.reply("❌ 未识别到有效token，请重新提交完整美团账号链接")
            exit()

        mt_clean = normalize_meituan_link(extracted_link, meituan_token)
        if not mt_clean:
            mt_clean = normalize_meituan_link('', meituan_token)

        if mt_clean != mt.strip():
            sender.reply("ℹ️ 已自动清洗链接参数，继续为您领取")
        
        # 询问用户选择领取方式
        sender.reply(f"""=====选择领取方式=====
1️⃣ 普通券种领取
   📦 包含普通套券[20-6、25-9、33-10、37-11、60-30、28-13、38-18]
   💰 价格: {money}元
   
------------------
回复数字选择方式
回复"q"退出操作
==================""")
        
        choice = sender.input(60000, 1, False)
        
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消操作")
            exit()
        
        # 处理普通券种领取
        if choice == '1':
            proceed_with_coupon = False  # 标记是否继续领券流程
            need_compensation = False  # 标记是否需要补偿次数
            ticket_type = 'normal'  # 普通券种
                
            # 如果不是免费模式且不是管理员，处理支付
            if not is_free and not sender.isAdmin():
                proceed_with_coupon, need_compensation = process_payment(money)
                # 记录是否使用了次数支付
                used_ticket_payment = proceed_with_coupon and not need_compensation
            else:
                proceed_with_coupon = True  # 免费模式或管理员，直接标记可以继续领券
                used_ticket_payment = False
                need_compensation = False
                
            # 如果可以继续领券（免费模式或已支付），执行领券流程
            if proceed_with_coupon:
                try:
                    # 使用Flask API领券
                    all_coupons = fetch_coupons_from_flask_api(mt_clean)
                    
                    # Flask API已经处理了token扣除
                    if all_coupons:
                        
                        # 汇总显示所有领取到的券
                        if len(all_coupons) == 1:
                            success_msg = f"""🎉 ========「领券成功」======== 🎉
✨ 恭喜您成功领取到以下优惠券：

{all_coupons[0]}

🎊 ========================== 🎊"""
                        else:
                            success_msg = f"""🎉 ========「领券汇总结果」======== 🎉
✨ 恭喜您成功领取到 {len(all_coupons)} 张优惠券：

"""
                            for i, coupon in enumerate(all_coupons, 1):
                                success_msg += f"{i:2d}. {coupon}\n"
                            success_msg += "\n🎊 ============================ 🎊"
                        
                        sender.reply(success_msg)
                    else:
                        if (need_compensation and not is_free) or used_ticket_payment:
                            add_user_tickets(userid, 1, ticket_type)
                            sender.reply(f"""=====领券失败补偿=====
✅ 已补偿一次普通券种次数
💳 当前剩余次数: {get_user_tickets(userid, ticket_type)}次
==================""")
                        
                except Exception as e:
                    sender.reply(f"处理过程出错：{str(e)}")
                    # 如果需要补偿且是付费领取失败的情况,或者使用了次数支付
                    if (need_compensation and not is_free) or used_ticket_payment:
                        add_user_tickets(userid, 1, ticket_type)
                        sender.reply(f"""=====领券失败补偿=====
✅ 已补偿一次普通券种次数
💳 当前剩余次数: {get_user_tickets(userid, ticket_type)}次
==================""")
        
        else:
            sender.reply("❌ 输入无效，已取消操作")
