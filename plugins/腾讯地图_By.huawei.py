# [title: 腾讯地图]
# [language: python]
# [class: 工具类]
# [author: huawei]
# [service: QQ:1603960061] 售后联系方式
# [rule: ^(地图)(登录|登陆)$|^登(录|陆)(地图)$|^(地图)(查询|管理)$|^(查询|管理)(地图)$|^清理地图$|^地图授权$|^地图教程$|^地图检测$|^地图一键运行$]
# [cron: 0 0 4,19 * * * ]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://free.picui.cn/free/2025/11/14/6916bb4577d7a.png]
# [version: 2.0.0]
# [public: true]
# [price: 8.88]
# [description: 腾讯地图现金毛，日0.1<br>指令：地图登录、管理、查询、授权、教程<br>内置签到抽奖提现功能]
# [param: {"required":true,"key":"G_TXDT_CONFIG.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款码链接","desc":"微信收款码/赞赏码链接"}]
# [param: {"required":true,"key":"G_TXDT_CONFIG.sqje","bool":false,"placeholder":"例:6.6,不填为0元","name":"授权价格","desc":"授权价格(单位:元)/月"}]
# [param: {"required":true,"key":"G_TXDT_CONFIG.sqsj","bool":false,"placeholder":"例:30,不填为30天","name":"授权天数","desc":"授权天数，默认30天/月"}]
# [param: {"required":false,"key":"G_TXDT_CONFIG.coin","bool":false,"placeholder":"不填为关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数）"}]
# [param: {"required":false,"key":"G_TXDT_CONFIG.notify","bool":false,"placeholder":"例:qq,wx,tb 多个用英文逗号分隔","name":"通知渠道","desc":"配置检测通知推送渠道"}]
# [param: {"required":false,"key":"G_TXDT_CONFIG.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付，关闭则使用扫码支付"}]
# [param: {"required":false,"key":"G_TXDT_CONFIG.proxy_api","name":"代理API","placeholder":"http://user:pass@ip:port"}]

import json
import time
import uuid
import hashlib
import random
import requests
from datetime import datetime, timedelta
import threading
import middleware

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

def get_proxy_api() -> str:
    """获取代理API配置"""
    try:
        return middleware.bucketGet(bucket=BUCKET_CONFIG, key='proxy_api') or ''
    except Exception:
        return ''

# 代理配置
proxy_url = get_proxy_api()
IS_PROXY = bool(proxy_url)

if IS_PROXY:
    print(f'[INFO] 地图代理模式: 已启用')
    print(f'[INFO] 地图代理API: {proxy_url}')
else:
    print(f'[INFO] 地图代理模式: 未启用')

# 代理池相关
proxy_cache = {}
proxy_lock_dict = threading.Lock()

def get_proxy(force_new=False, account_key=None):
    """动态获取代理池中的代理"""
    if not IS_PROXY or not proxy_url:
        return None
    
    if account_key and not force_new:
        with proxy_lock_dict:
            if account_key in proxy_cache:
                return proxy_cache[account_key]
    
    try:
        response = requests.get(proxy_url, timeout=5)
        if response.status_code == 200:
            ip = response.text.strip()
            if "请先添加白名单" in ip:
                print(f'[WARNING] 地图代理服务异常：请先添加白名单')
                return None
            
            proxy_dict = {'http': ip, 'https': ip}
            
            if account_key:
                with proxy_lock_dict:
                    proxy_cache[account_key] = proxy_dict
            
            print(f'[INFO] 地图获取代理成功: {ip}')
            return proxy_dict
        else:
            print(f'[WARNING] 地图代理API响应异常: {response.status_code}')
            return None
    except Exception as e:
        print(f'[WARNING] 地图获取代理失败: {str(e)}')
        return None

def request_with_retry(method, url, max_retries=3, account_key=None, **kwargs):
    """带重试机制的请求函数"""
    current_proxy = None
    
    for attempt in range(max_retries):
        try:
            if IS_PROXY:
                if attempt == 0:
                    current_proxy = get_proxy(force_new=False, account_key=account_key)
                else:
                    current_proxy = get_proxy(force_new=True, account_key=account_key)
                
                if current_proxy:
                    kwargs['proxies'] = current_proxy
                else:
                    kwargs['proxies'] = None
            
            if method.upper() == 'GET':
                response = requests.get(url, **kwargs)
            else:
                response = requests.post(url, **kwargs)
            
            return response
            
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError) as e:
            print(f'[WARNING] 地图代理连接错误: {str(e)[:100]}')
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                print(f'[ERROR] 地图代理请求失败，已达最大重试次数')
                raise
        except requests.exceptions.Timeout:
            print(f'[WARNING] 地图请求超时')
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                print(f'[ERROR] 地图请求超时，已达最大重试次数')
                raise
        except Exception as e:
            print(f'[ERROR] 地图请求异常: {str(e)[:100]}')
            raise
    
    return None

# 数据桶配置
BUCKET_USER = 'G_TXDT_USER'  # 用户账号列表
BUCKET_TOKEN = 'G_TXDT_TOKEN'  # 账号token信息
BUCKET_AUTH = 'G_TXDT_AUTH'  # 账号授权信息
BUCKET_CONFIG = 'G_TXDT_CONFIG'  # 插件配置

# 获取用户绑定的账号
uservalue = middleware.bucketGet(bucket=BUCKET_USER, key=userid)

# 支付方式中文名称映射
PAY_TYPE_NAMES = {
    'alipay': '支付宝',
    'wxpay': '微信支付',
    'qqpay': 'QQ钱包',
}

def mask_user_id(user_id):
    """user_id脱敏处理"""
    if not user_id or len(user_id) < 8:
        return user_id
    return f"{user_id[:4]}****{user_id[-4:]}"

def get_config(key, default=''):
    """获取配置"""
    return middleware.bucketGet(BUCKET_CONFIG, key) or default


def calculate_md5(text):
    """计算字符串的MD5值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def sort_dict_by_key(data):
    """对字典按照键名排序"""
    return dict(sorted(data.items(), key=lambda x: x[0]))

def generate_qrcode(url):
    """生成二维码图片"""
    try:
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        return None

def create_mapi_payment(config, amount, out_trade_no, name, user_id, pay_type, sitename=""):
    """创建支付订单 (mapi接口)"""
    try:
        # 构造支付参数
        params = {
            'pid': config['pid'],
            'type': pay_type,
            'out_trade_no': out_trade_no,
            'notify_url': config['notify_url'],
            'return_url': config['return_url'],
            'name': name,
            'money': str(amount),
            'sitename': sitename,
            'param': user_id
        }
        
        # 移除空值
        params = {k: v for k, v in params.items() if v}
        
        # 按照ASCII码排序参数
        sorted_params = sort_dict_by_key(params)
        
        # 拼接成key=value&key=value格式
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        
        # 添加密钥进行MD5签名
        sign = calculate_md5(sign_str + config['key']).lower()
        
        # 添加签名到参数
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        
        # 构建mapi接口URL
        mapi_url = config['gateway']
        if mapi_url.endswith('/'):
            mapi_url = mapi_url[:-1]
        mapi_url = f"{mapi_url}/mapi.php"
        
        # 发送POST请求
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = request_with_retry('POST', mapi_url, data=params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return False, None, f"创建支付订单失败，HTTP状态码: {response.status_code}"
        
        # 解析响应
        try:
            result = response.json()
        except:
            return False, None, "创建支付订单失败，返回数据格式错误"
        
        # 判断返回结果
        code = result.get('code', 0)
        msg = result.get('msg', '未知状态')
        
        if code == 1:  # 码支付API返回的成功状态码是1
            return True, result, msg
        else:
            return False, None, msg
            
    except Exception as e:
        return False, None, f"创建订单失败: {str(e)}"

def query_mapi_order(config, order_no, is_trade_no=False):
    """查询订单状态"""
    try:
        # 构建查询API URL
        api_url = config['gateway']
        if api_url.endswith('/'):
            api_url = api_url[:-1]
        
        query_url = f"{api_url}/xpay/epay/api.php"
        
        # 构建请求参数
        params = {
            'act': 'order',
            'pid': config['pid'],
            'key': config['key']
        }
        
        # 根据订单号类型添加相应参数
        if is_trade_no:
            params['trade_no'] = order_no
        else:
            params['out_trade_no'] = order_no
        
        # 发送GET请求
        response = request_with_retry('GET', query_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return False, None, f"查询订单失败，HTTP状态码: {response.status_code}"
        
        # 解析响应
        try:
            result = response.json()
        except:
            return False, None, "查询订单失败，返回数据格式错误"
        
        # 判断返回结果
        code = result.get('code', 0)
        if code == 1:
            return True, result, "查询成功"
        else:
            return False, None, result.get('msg', '查询失败')
            
    except Exception as e:
        return False, None, f"查询订单失败: {str(e)}"

def poll_mapi_payment_status(config, order_no, max_tries=30):
    """轮询MAPI支付状态"""
    for i in range(max_tries):
        # 查询订单状态
        success, data, msg = query_mapi_order(config, order_no, is_trade_no=False)
        
        # 如果查询成功且订单已支付
        if success and isinstance(data, dict) and data.get('status') == 1:
            return True, msg, data
        
        # 等待用户输入或超时
        result = sender.listen(5000)  # 等待5秒
        if result == 'q':
            return False, "用户取消", None
    
    return False, "查询超时，订单可能尚未支付", None

def get_headers(user_id, urlparams):
    """生成腾讯地图API请求头"""
    reqid = str(uuid.uuid4())
    reqtime = str(int(time.time()*1000))
    secret_key = '03a9875e795c3ecff15f617085e72d4cc'
    tmapdefaultstr = f'mapinst=0&mapnonce=0&reqid={reqid}&reqtime={reqtime}{urlparams}{secret_key}'
    tmapdefaultsign = hashlib.md5(tmapdefaultstr.encode()).hexdigest()
    timestamp = reqtime[:-3]
    signstr = f'request_id={reqid}&from_source=wx7643d5f831302ab0&timestamp={timestamp}&token=e643d512f085d621bf6c9e80310d0498'
    sign = hashlib.sha256(signstr.encode()).hexdigest().upper()
    return {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'from_source': 'wx7643d5f831302ab0',
        'request_id': reqid,
        'tmap-nonce': '0',
        'tmap-engine': 'web',
        'tmap-reqid': reqid,
        'sign': sign,
        'user_id': user_id,
        'tmap-reqtime': reqtime,
        'timestamp': timestamp,
        'tmap-install-id': '0',
        'tmap-default-sign': tmapdefaultsign
    }

def verify_account(user_id):
    """验证账号是否有效"""
    try:
        headers = get_headers(user_id, '/activity/v1/lottery/detail')
        resp = request_with_retry(
            'POST', 
            'https://mmapgwh.map.qq.com/activity/v1/lottery/detail',
            headers=headers,
            json={'activity_id':1721983577,'game_id':3,'rule_id':'tencent_map_lottery'},
            timeout=10,
            account_key=user_id
        )
        return resp.status_code == 200 and resp.json().get('message') == 'ok'
    except:
        return False

def do_checkin(user_id):
    """执行签到"""
    try:
        headers = get_headers(user_id, '/activity/v1/checkin')
        resp = request_with_retry(
            'POST',
            'https://mmapgwh.map.qq.com/activity/v1/checkin',
            headers=headers,
            json={'activity_id':1721983577,'game_id':1},
            timeout=10,
            account_key=user_id
        ).json()
        if resp['message'] == 'ok':
            prizes = [prize['name'] for prize in resp['data']['prizes']]
            return True, '、'.join(prizes)
        else:
            return False, resp['message']
    except Exception as e:
        return False, str(e)

def do_lottery(user_id):
    """执行抽奖"""
    try:
        headers = get_headers(user_id, '/activity/v1/lottery/detail')
        resp = request_with_retry(
            'POST',
            'https://mmapgwh.map.qq.com/activity/v1/lottery/detail',
            headers=headers,
            json={'activity_id':1721983577,'game_id':3,'rule_id':'tencent_map_lottery'},
            timeout=10,
            account_key=user_id
        ).json()
        
        if resp['message'] != 'ok':
            return False, resp['message'], 0
        
        tickets = resp['data']['available_ticket_number']
        results = []
        
        for i in range(tickets):
            lottery_resp = request_with_retry(
                'POST',
                'https://mmapgwh.map.qq.com/activity/v1/lottery',
                headers=get_headers(user_id, '/activity/v1/lottery'),
                json={'activity_id':1721983577,'game_id':3},
                timeout=10,
                account_key=user_id
            ).json()
            
            if lottery_resp['message'] == 'ok':
                prizes = [prize['name'] for prize in lottery_resp['data']['prizes']]
                results.append('、'.join(prizes))
            else:
                results.append(lottery_resp['message'])
            time.sleep(0.5)
        
        return True, results, tickets
    except Exception as e:
        return False, str(e), 0

def do_withdraw(user_id):
    """执行提现"""
    try:
        headers = get_headers(user_id, '/activity/v1/withdraw/home')
        resp = request_with_retry(
            'POST',
            'https://mmapgwh.map.qq.com/activity/v1/withdraw/home',
            headers=headers,
            json={'activity_id':1721983577,'game_id':4,'rule_id':'tencent_map_withdraw'},
            timeout=10,
            account_key=user_id
        ).json()
        
        if resp['message'] != 'ok':
            return False, resp['message'], 0, 0
        
        data = resp['data']
        coins = data['coins']/100
        withdrawable = data['withdrawable_amount']/100
        
        if data['withdrawable_amount'] >= data['current_withdraw_threshold']:
            withdraw_resp = request_with_retry(
                'POST',
                'https://mmapgwh.map.qq.com/activity/v1/withdraw',
                headers=get_headers(user_id, '/activity/v1/withdraw'),
                json={'activity_id':1721983577,'game_id':4},
                timeout=10,
                account_key=user_id
            ).json()
            return True, withdraw_resp['message'], coins, withdrawable
        else:
            return True, '未达到提现阈值', coins, withdrawable
    except Exception as e:
        return False, str(e), 0, 0

def query_balance(user_id):
    """查询余额"""
    try:
        headers = get_headers(user_id, '/activity/v1/withdraw/home')
        resp = request_with_retry(
            'POST',
            'https://mmapgwh.map.qq.com/activity/v1/withdraw/home',
            headers=headers,
            json={'activity_id':1721983577,'game_id':4,'rule_id':'tencent_map_withdraw'},
            timeout=10,
            account_key=user_id
        ).json()
        
        if resp['message'] == 'ok':
            data = resp['data']
            coins = data['coins']/100
            withdrawable = data['withdrawable_amount']/100
            return True, coins, withdrawable
        else:
            return False, 0, 0
    except:
        return False, 0, 0

def query_coins_history(user_id, limit=5):
    """查询金币明细"""
    try:
        headers = get_headers(user_id, '/activity/v1/coins/history')
        resp = request_with_retry(
            'POST',
            'https://mmapgwh.map.qq.com/activity/v1/coins/history',
            headers=headers,
            json={'activity_id':1721983577,'state':'normal','last_id':''},
            timeout=10,
            account_key=user_id
        ).json()
        
        if resp['message'] == 'ok' and 'data' in resp:
            history_list = resp['data'].get('list', [])
            # 只取前limit条
            history_list = history_list[:limit]
            
            # 格式化明细
            formatted_history = []
            for item in history_list:
                amount = item['amount'] / 100  # 转换为元
                created_time = item['created_time']
                
                # 转换时间戳为日期时间
                dt = datetime.fromtimestamp(created_time)
                time_str = dt.strftime('%m-%d %H:%M')
                
                formatted_history.append(f"🧧{amount:.2f}金币 {time_str}")
            
            return True, formatted_history
        else:
            return False, []
    except Exception as e:
        return False, []


def bind_account():
    """绑定腾讯地图账号（支持批量）"""
    sender.reply("""
=====腾讯地图登录=====
请按照格式输入账号信息
------------------
📝 格式: 备注#user_id
📝 示例: 
张三#abc123def456
李四#xyz789ghi012
------------------
💡 支持批量登录，每行一个账号
💡 回复"q"随时退出操作
==================""")
    
    input_text = sender.input(120000, 10000, False)
    
    if not input_text:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif input_text.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    # 解析批量账号
    accounts_list = []
    for line in input_text.split('\n'):
        line = line.strip()
        if '#' in line:
            parts = line.split('#', 1)
            if len(parts) == 2:
                remark = parts[0].strip()
                user_id = parts[1].strip()
                if remark and user_id:
                    accounts_list.append({'remark': remark, 'user_id': user_id})
    
    if not accounts_list:
        sender.reply("""
=====格式错误=====
❌ 未检测到有效账号
------------------
请按照格式输入: 备注#user_id
示例: 张三#abc123def456
==================""")
        return
    
    # 批量处理账号
    #sender.reply(f"🔄 开始处理 {len(accounts_list)} 个账号...")
    
    success_count = 0
    fail_count = 0
    results = []
    
    # 获取当前用户的账号列表
    current_accounts = eval(uservalue) if uservalue else []
    
    for idx, acc in enumerate(accounts_list, 1):
        remark = acc['remark']
        user_id = acc['user_id']
        
        #sender.reply(f"🔄 正在处理第{idx}/{len(accounts_list)}个账号: {remark}")
        
        try:
            # 验证user_id格式
            if len(user_id) < 10:
                fail_count += 1
                results.append(f"❌ {remark} - user_id格式不正确")
                continue
            
            # 验证账号有效性
            if not verify_account(user_id):
                fail_count += 1
                results.append(f"❌ {remark} - 账号验证失败")
                continue
            
            # 保存账号到用户列表
            if user_id not in current_accounts:
                current_accounts.append(user_id)
            
            # 保存账号详细信息
            account_info = {
                "user_id": user_id,
                "remark": remark,
                "create_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            middleware.bucketSet(BUCKET_TOKEN, user_id, json.dumps(account_info))
            
            # 检查账号授权状态
            dqsj = datetime.now().strftime("%Y-%m-%d")
            accountVip = middleware.bucketGet(BUCKET_AUTH, user_id)
            
            if accountVip and accountVip > dqsj:
                success_count += 1
                results.append(f"✅ {remark} ({mask_user_id(user_id)}) - 已授权至{accountVip}")
            else:
                success_count += 1
                results.append(f"✅ {remark} ({mask_user_id(user_id)}) - 登录成功，需授权")
            
            # 优化：减少延迟，加快批量登录速度
            time.sleep(0.3)
        
        except Exception as e:
            fail_count += 1
            results.append(f"❌ {remark} - 异常: {str(e)}")
    
    # 保存更新后的账号列表
    middleware.bucketSet(BUCKET_USER, userid, str(current_accounts))
    
    # 显示结果
    result_msg = f"""
=====批量登录完成=====
📊 总数: {len(accounts_list)}个
✅ 成功: {success_count}个
❌ 失败: {fail_count}个
==================
"""
    for result in results:
        result_msg += result + "\n"
    
    result_msg += """==================
💡 发送"地图管理"可管理账号
💡 发送"地图查询"可查询信息
=================="""
    
    sender.reply(result_msg)

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply("""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送"地图登录"绑定
==================""")
        return
    
    accounts = eval(uservalue)
    account_list = """
========选择账号=======
[0] 全部账号"""
    
    for i, user_id in enumerate(accounts, 1):
        try:
            account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, user_id))
            remark = account_info.get('remark', user_id)
            auth_time = middleware.bucketGet(BUCKET_AUTH, user_id)
            
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            
            account_list += f"""
[{i}]{mask_user_id(user_id)}({remark}, {auth_status})"""
        except:
            account_list += f"""
[{i}]{mask_user_id(user_id)}(信息异常)"""
    
    account_list += """
=====================
支持多选，用英文逗号分隔
例如: 1,2,3
回复"q"退出操作
====================="""
    
    sender.reply(account_list)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出查询")
        return
    
    try:
        selected_accounts = []
        
        if choice == '0':
            selected_accounts = accounts.copy()
        else:
            indices = choice.split(',')
            for idx in indices:
                idx = idx.strip()
                if not idx.isdigit():
                    continue
                
                index = int(idx) - 1
                if 0 <= index < len(accounts):
                    selected_accounts.append(accounts[index])
        
        if not selected_accounts:
            sender.reply("❌ 未选择有效账号")
            return
        
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号，正在查询...")
        
        query_count = 0
        for user_id in selected_accounts:
            try:
                account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, user_id))
                auth_time = middleware.bucketGet(BUCKET_AUTH, user_id)
                auth_status = '已授权' if auth_time and auth_time >= str(datetime.now().date()) else '未授权'
                
                # 查询余额
                success, coins, withdrawable = query_balance(user_id)
                
                # 查询金币明细
                history_success, history_list = query_coins_history(user_id, limit=5)
                
                if success:
                    account_info_msg = f"""
=====账号信息[{query_count+1}/{len(selected_accounts)}]=====
🆔 账号: {mask_user_id(user_id)}
📝 备注: {account_info.get('remark')}
🔐 授权状态: {auth_status}
💰 金币余额: {coins}元
💵 可提现: {withdrawable}元"""
                    
                    # 添加金币明细
                    if history_success and history_list:
                        account_info_msg += "\n==================\n📋 金币明细(最近5条):"
                        for history_item in history_list:
                            account_info_msg += f"\n{history_item}"
                    
                    account_info_msg += "\n=================="
                else:
                    account_info_msg = f"""
=====账号信息[{query_count+1}/{len(selected_accounts)}]=====
🆔 账号: {mask_user_id(user_id)}
👤 备注: {account_info.get('remark')}
🔐 授权状态: {auth_status}
❌ 余额查询失败
=================="""
                
                sender.reply(account_info_msg)
                query_count += 1
                
                if query_count < len(selected_accounts) and len(selected_accounts) > 3:
                    time.sleep(0.5)
            
            except Exception as e:
                sender.reply(f"""
=====查询失败[{query_count+1}/{len(selected_accounts)}]=====
🆔 账号: {mask_user_id(user_id)}
❌ 错误: {str(e)}
==================""")
                query_count += 1
        
        if query_count > 0:
            sender.reply(f"✅ 查询完成，共查询了 {query_count} 个账号")
    
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


def manage_account():
    """账号管理功能"""
    if not uservalue:
        sender.reply("""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送"地图登录"绑定
==================""")
        return
    
    accounts = eval(uservalue)
    
    # 显示管理功能菜单
    menu = """
=====账号管理=====
[1] 授权账号
[2] 删除账号
[3] 执行任务
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(menu)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    
    # 显示账号列表
    account_list = """
========选择账号=======
[0] 全部账号"""
    
    for i, user_id in enumerate(accounts, 1):
        try:
            account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, user_id))
            remark = account_info.get('remark', user_id)
            auth_time = middleware.bucketGet(BUCKET_AUTH, user_id)
            
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            
            account_list += f"""
[{i}]{mask_user_id(user_id)}({remark}, {auth_status})"""
        except:
            account_list += f"""
[{i}]{mask_user_id(user_id)}(信息异常)"""
    
    account_list += """
=====================
支持多选，用英文逗号分隔
例如: 1,2,3
回复"q"退出操作
====================="""
    
    sender.reply(account_list)
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    
    try:
        selected_accounts = []
        
        if account_choice == '0':
            selected_accounts = accounts.copy()
        else:
            indices = account_choice.split(',')
            for idx in indices:
                idx = idx.strip()
                if not idx.isdigit():
                    continue
                
                index = int(idx) - 1
                if 0 <= index < len(accounts):
                    selected_accounts.append(accounts[index])
        
        if not selected_accounts:
            sender.reply("❌ 未选择有效账号")
            return
        
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号")
        
        # 根据功能选择执行对应操作
        if choice == '1':
            # 授权选中的账号
            authorize_multiple_accounts(selected_accounts)
        
        elif choice == '2':
            # 删除选中的账号
            confirm = """
=====确认删除=====
⚠️ 此操作不可恢复
------------------
回复 y 确认删除
回复 n 取消操作
=================="""
            sender.reply(confirm)
            
            confirm_input = sender.input(120000, 1, False)
            if confirm_input and confirm_input.lower() == 'y':
                success_count = 0
                for user_id in selected_accounts:
                    try:
                        if user_id in accounts:
                            accounts.remove(user_id)
                        
                        middleware.bucketDel(BUCKET_TOKEN, user_id)
                        middleware.bucketDel(BUCKET_AUTH, user_id)
                        success_count += 1
                    except Exception as e:
                        print(f"删除账号失败: {user_id}, 错误: {str(e)}")
                
                if accounts:
                    middleware.bucketSet(BUCKET_USER, userid, str(accounts))
                else:
                    middleware.bucketDel(BUCKET_USER, userid)
                
                sender.reply(f"✅ 已成功删除 {success_count}/{len(selected_accounts)} 个账号")
            else:
                sender.reply("✅ 已取消删除")
        
        elif choice == '3':
            # 执行任务
            success_count = 0
            for user_id in selected_accounts:
                try:
                    account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, user_id))
                    remark = account_info.get('remark', user_id)
                    
                    # 构建任务结果消息
                    task_msg = f"""
=====任务执行: {remark}====="""
                    
                    # 签到
                    checkin_success, checkin_result = do_checkin(user_id)
                    if checkin_success:
                        task_msg += f"\n✅ 签到成功: {checkin_result}"
                    else:
                        task_msg += f"\n❌ 签到失败: {checkin_result}"
                    
                    time.sleep(1)
                    
                    # 抽奖
                    lottery_success, lottery_result, tickets = do_lottery(user_id)
                    if lottery_success:
                        task_msg += f"\n🎰 抽奖券: {tickets}张"
                        if tickets > 0:
                            for idx, prize in enumerate(lottery_result, 1):
                                task_msg += f"\n  第{idx}次: {prize}"
                    else:
                        task_msg += f"\n❌ 抽奖失败: {lottery_result}"
                    
                    time.sleep(1)
                    
                    # 提现
                    withdraw_success, withdraw_result, coins, withdrawable = do_withdraw(user_id)
                    if withdraw_success:
                        task_msg += f"\n💰 金币余额: {coins}元"
                        task_msg += f"\n💵 可提现: {withdrawable}元"
                        task_msg += f"\n📤 提现结果: {withdraw_result}"
                    else:
                        task_msg += f"\n❌ 提现失败: {withdraw_result}"
                    
                    task_msg += "\n===================="
                    
                    # 一次性发送所有任务结果
                    sender.reply(task_msg)
                    
                    success_count += 1
                    
                    if success_count < len(selected_accounts):
                        time.sleep(2)
                
                except Exception as e:
                    sender.reply(f"""
=====任务执行失败=====
👤 账号: {remark}
❌ 错误: {str(e)}
=====================""")
            
            sender.reply(f"✅ 任务执行完成，共处理 {success_count}/{len(selected_accounts)} 个账号")
        
        else:
            sender.reply("❌ 无效的选择")
    
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")


def authorize_multiple_accounts(user_ids):
    """授权多个账号"""
    account_infos = []
    for user_id in user_ids:
        try:
            account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, user_id))
            account_infos.append({
                'user_id': user_id,
                'info': account_info
            })
        except Exception as e:
            sender.reply(f"""
⚠️ 账号处理异常:
🆔 账号: {mask_user_id(user_id)}
❌ 原因: {str(e)}""")
    
    if not account_infos:
        sender.reply("❌ 没有有效的账号可授权")
        return
    
    #sender.reply(f"✅ 共有 {len(account_infos)} 个有效账号可授权")
    
    # 询问授权月数
    auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
    sender.reply(auth_guide)
    
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
    
    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
        
        # 获取配置
        sqje = float(get_config('sqje', '6.6'))
        sqsj = int(get_config('sqsj', '30'))
        coin = int(get_config('coin', '0'))
        
        # 计算总价格
        total_money = len(account_infos) * months * sqje
        
        # 构建可用的支付方式列表
        available_payments = []
        
        # 检查是否启用码支付
        ma_pay_switch = get_config('ma_pay_switch', 'false')
        
        if ma_pay_switch.lower() == 'true':
            # 从卡密系统获取支付配置
            ma_pay_type = middleware.bucketGet('dd_sign_config', 'ma_pay_type') or ''
            ma_pay_pid = middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or ''
            ma_pay_key = middleware.bucketGet('dd_sign_config', 'ma_pay_key') or ''
            ma_pay_gateway = middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or ''
            
            if ma_pay_gateway and ma_pay_pid and ma_pay_key:
                pay_types_str = ma_pay_type.strip() or "alipay,wxpay"
                pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
                
                for pay_type in pay_types:
                    name = PAY_TYPE_NAMES.get(pay_type, pay_type)
                    available_payments.append((name, f"mapay_{pay_type}"))
            else:
                zsm = get_config('zsm')
                if zsm:
                    available_payments.append(("微信支付", "wxpay"))
        else:
            zsm = get_config('zsm')
            if zsm:
                available_payments.append(("微信支付", "wxpay"))
        
        # 积分兑换
        if coin > 0:
            available_payments.append(("积分兑换", "coin"))
        
        if not available_payments:
            sender.reply("""
=====授权失败=====
❌ 未配置任何支付方式
------------------
请联系管理员配置支付方式
==================""")
            return
        
        # 如果只有一种支付方式，直接使用
        if len(available_payments) == 1:
            selected_payment = available_payments[0][1]
        else:
            # 显示支付方式选择
            payment_menu = f"""
=====选择支付方式=====
📊 账号数量: {len(account_infos)}个
⏰ 授权时长: {months}月
💰 总金额: {total_money}元
------------------"""
            
            for i, (name, _) in enumerate(available_payments, 1):
                if name == "积分兑换":
                    need_coin = coin * months * len(account_infos)
                    user_coin = middleware.bucketGet('dd_sign_points', userid) or '0'
                    payment_menu += f"\n[{i}] {name} ({need_coin}积分, 当前:{user_coin})"
                else:
                    payment_menu += f"\n[{i}] {name} ({total_money}元)"
            
            payment_menu += """
------------------
回复数字选择支付方式
回复"q"退出操作
=================="""
            
            sender.reply(payment_menu)
            
            pay_choice = sender.input(120000, 1, False)
            if not pay_choice or pay_choice.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
            
            try:
                pay_index = int(pay_choice) - 1
                if 0 <= pay_index < len(available_payments):
                    selected_payment = available_payments[pay_index][1]
                else:
                    sender.reply("❌ 无效的选择")
                    return
            except:
                sender.reply("❌ 请输入有效的数字")
                return
        
        # 处理支付
        if selected_payment == "coin":
            # 积分支付
            need_coin = coin * months * len(account_infos)
            user_coin = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            
            if user_coin < need_coin:
                sender.reply(f"""
=====积分不足=====
❌ 当前积分: {user_coin}
💡 需要积分: {need_coin}
==================""")
                return
            
            # 扣除积分
            new_balance = user_coin - need_coin
            middleware.bucketSet('dd_sign_points', userid, str(new_balance))
            
            # 批量授权
            success_count = process_batch_authorization(account_infos, months, sqsj)
            
            sender.reply(f"""
=====支付成功=====
🎫 商品: 地图批量授权
💰 支付方式: 积分支付
💫 消耗积分: {need_coin}
💰 剩余积分: {new_balance}
📊 成功: {success_count}/{len(account_infos)}个账号
==================""")
        
        elif selected_payment == "wxpay":
            # 微信支付
            zsm = get_config('zsm')
            if not zsm:
                sender.reply("❌ 未配置收款码")
                return
            
            status = sender.atWaitPay()
            if status == "True" or status or status == "true":
                sender.reply("🔔目前有其他用户正在付款，请稍后再试！！")
                return
            
            sender.replyImage(zsm)
            sender.reply(f"""
=====微信扫码支付====
🎫 商品: 地图批量授权
📊 账号数量: {len(account_infos)}个
⏰ 时长: {months}月
💰 总金额: {total_money}元
------------------
请使用微信扫码支付
回复"q"取消支付
==================""")
            
            waitPay = sender.waitPay("q", 120000)
            
            if waitPay == 'q':
                sender.reply("✅ 已取消支付")
                return
            
            if isinstance(waitPay, str):
                waitPay = json.loads(waitPay)
            
            Money = float(waitPay['Money'])
            
            if Money >= total_money:
                success_count = process_batch_authorization(account_infos, months, sqsj)
                
                sender.reply(f"""
=====支付成功=====
💰 金额: {Money}元
📊 成功: {success_count}/{len(account_infos)}个账号
==================""")
            else:
                sender.reply(f"❌ 支付金额不足，应付{total_money}元，实付{Money}元")
        
        elif selected_payment.startswith("mapay_"):
            # 码支付
            pay_type = selected_payment.replace("mapay_", "")
            
            # 获取码支付配置
            config = {
                'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
                'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
                'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
                'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or 'http://localhost/notify',
                'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or 'http://localhost/return'
            }
            
            if not (config['gateway'] and config['pid'] and config['key']):
                sender.reply("❌ 码支付配置不完整，请联系管理员")
                return
            
            # 保留两位小数
            amount = round(float(total_money), 2)
            
            # 生成商户订单号
            out_trade_no = f"地图{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
            
            # 显示支付信息
            pay_type_name = PAY_TYPE_NAMES.get(pay_type, pay_type)
            
            # 创建支付订单
            try:
                success, result, msg = create_mapi_payment(
                    config=config,
                    amount=amount,
                    out_trade_no=out_trade_no,
                    name=f"腾讯地图批量授权-{str(amount)}",
                    user_id=userid,
                    pay_type=pay_type
                )
            except Exception as e:
                sender.reply(f'❌ 创建订单时出错: {str(e)}')
                return
            
            if not success:
                sender.reply(f'❌ 创建订单失败: {msg}')
                return
            
            # 提取支付链接
            trade_no = result.get('trade_no')
            if not trade_no:
                sender.reply('❌ 获取支付订单号失败')
                return
            
            # 构建支付链接
            gateway = config['gateway']
            if gateway.endswith('/'):
                gateway = gateway[:-1]
            pay_url = f"{gateway}/pay/{trade_no}"
            
            # 生成短链接
            try:
                encoded_url = requests.utils.quote(pay_url)
                headers = {
                    'sec-ch-ua-platform': 'Windows',
                    'sec-ch-ua': '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'sec-ch-ua-mobile': '?0',
                    'Origin': 'https://www.mrw.so',
                    'Sec-Fetch-Site': 'same-site',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://www.mrw.so/',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
                }
                data = {
                    'urlStr': encoded_url,
                    'domain': 'mrw.so',
                    'expireType': '1',
                    'key': '5d7798c491d2c423c8c33d2d@631d0a6ffd3fbca7c2728bebc6602f98',
                    'random': str(int(time.time() * 1000))
                }
                response = request_with_retry('POST', 'https://create.mrw.so/pageHome/createBySingle.htm', headers=headers, data=data, timeout=5)
                short_url = response.json().get('data')
                if short_url:
                    pay_url = short_url
            except:
                pass  # 短链接生成失败时使用原始链接
            
            # 发送支付二维码
            sender.reply(f'请使用【{pay_type_name}】扫描下方二维码完成支付:')
            sender.replyImage(generate_qrcode(pay_url))
            sender.reply('支付过程中输入"q"可取消支付')
            
            # 轮询支付结果
            is_paid, msg_result, data_result = poll_mapi_payment_status(config, out_trade_no)
            
            if is_paid:
                # 支付成功，批量授权
                success_count = process_batch_authorization(account_infos, months, sqsj)
                
                sender.reply(f"""
=====支付成功=====
🎫 商品: 腾讯地图批量授权
💰 支付方式: {pay_type_name}
💰 金额: {amount}元
📊 成功: {success_count}/{len(account_infos)}个账号
==================""")
            else:
                # 支付失败或超时
                sender.reply(f"❌ 支付未完成: {msg_result}")
        
        else:
            sender.reply("❌ 暂不支持该支付方式")
    
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")

def process_batch_authorization(account_infos, months, sqsj):
    """处理批量授权"""
    success_count = 0
    today = datetime.now().strftime("%Y-%m-%d")
    
    for acc in account_infos:
        try:
            user_id = acc['user_id']
            current_auth = middleware.bucketGet(BUCKET_AUTH, user_id)
            
            if current_auth and current_auth > today:
                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                new_auth = auth_date + timedelta(days=sqsj * months)
            else:
                new_auth = datetime.now() + timedelta(days=sqsj * months)
            
            new_auth_str = new_auth.strftime("%Y-%m-%d")
            middleware.bucketSet(BUCKET_AUTH, user_id, new_auth_str)
            success_count += 1
        except:
            continue
    
    return success_count


def admin_authorize():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    auth_menu = """
=====管理员授权=====
[1] 批量授权
[2] 单独授权
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(auth_menu)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消操作")
        return
    
    if choice == '1':
        # 批量授权所有用户的所有账号
        all_users = []
        for key in middleware.bucketAllKeys(BUCKET_USER):
            userdata = middleware.bucketGet(BUCKET_USER, key)
            if userdata:
                user_accounts = eval(userdata)
                all_users.append({
                    'id': key,
                    'accounts': user_accounts
                })
        
        if not all_users:
            sender.reply("❌ 未找到任何用户")
            return
        
        total_accounts = sum(len(user['accounts']) for user in all_users)
        sender.reply(f"✅ 共找到 {len(all_users)} 个用户，{total_accounts} 个账号")
        
        sender.reply("""
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
==================""")
        
        months = sender.input(120000, 1, False)
        if not months or months.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            months = int(months)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
            
            sender.reply(f"""
=====确认批量授权=====
⚠️ 将为全部 {total_accounts} 个账号授权 {months} 个月
------------------
回复 y 确认授权
回复 n 取消操作
==================""")
            
            confirm = sender.input(120000, 1, False)
            if confirm and confirm.lower() != 'y':
                sender.reply("✅ 已取消授权")
                return
            
            sqsj = int(get_config('sqsj', '30'))
            success_count = 0
            today = datetime.now().strftime("%Y-%m-%d")
            
            for user in all_users:
                for user_id in user['accounts']:
                    try:
                        current_auth = middleware.bucketGet(BUCKET_AUTH, user_id)
                        
                        if current_auth and current_auth > today:
                            start_date = datetime.strptime(current_auth, "%Y-%m-%d")
                        else:
                            start_date = datetime.now()
                        
                        new_expire = start_date + timedelta(days=sqsj * months)
                        middleware.bucketSet(BUCKET_AUTH, user_id, new_expire.strftime("%Y-%m-%d"))
                        success_count += 1
                    except:
                        continue
            
            sender.reply(f"""
=====批量授权结果=====
📊 总账号: {total_accounts}个
✅ 成功: {success_count}个
❌ 失败: {total_accounts - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
        
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
    
    elif choice == '2':
        # 单独授权指定用户
        sender.reply("""
=====输入用户ID=====
请输入需要授权的用户ID
------------------
回复"q"退出操作
==================""")
        
        target_id = sender.input(120000, 1, False)
        if not target_id or target_id.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        userdata = middleware.bucketGet(BUCKET_USER, target_id)
        if not userdata:
            sender.reply("❌ 未找到该用户")
            return
        
        user_accounts = eval(userdata)
        sender.reply(f"✅ 用户 {target_id} 有 {len(user_accounts)} 个账号")
        
        # 显示账号列表
        account_list = """
========选择账号=======
[0] 全部账号"""
        
        for i, user_id in enumerate(user_accounts, 1):
            try:
                account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, user_id))
                remark = account_info.get('remark', user_id)
                auth_time = middleware.bucketGet(BUCKET_AUTH, user_id)
                
                if not auth_time:
                    auth_status = '未授权'
                elif auth_time < str(datetime.now().date()):
                    auth_status = '已过期'
                else:
                    auth_status = f'到期:{auth_time}'
                
                account_list += f"""
[{i}]{mask_user_id(user_id)}({remark}, {auth_status})"""
            except:
                account_list += f"""
[{i}]{mask_user_id(user_id)}(信息异常)"""
        
        account_list += """
=====================
支持多选，用英文逗号分隔
例如: 1,2,3
回复"q"退出操作
====================="""
        
        sender.reply(account_list)
        
        account_choice = sender.input(120000, 1, False)
        if not account_choice or account_choice.lower() == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            selected_accounts = []
            
            if account_choice == '0':
                selected_accounts = user_accounts.copy()
            else:
                indices = account_choice.split(',')
                for idx in indices:
                    idx = idx.strip()
                    if not idx.isdigit():
                        continue
                    
                    index = int(idx) - 1
                    if 0 <= index < len(user_accounts):
                        selected_accounts.append(user_accounts[index])
            
            if not selected_accounts:
                sender.reply("❌ 未选择有效账号")
                return
            
            sender.reply("""
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
==================""")
            
            months = sender.input(120000, 1, False)
            if not months or months.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return
            
            months = int(months)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
            
            sqsj = int(get_config('sqsj', '30'))
            success_count = 0
            today = datetime.now().strftime("%Y-%m-%d")
            
            for user_id in selected_accounts:
                try:
                    current_auth = middleware.bucketGet(BUCKET_AUTH, user_id)
                    
                    if current_auth and current_auth > today:
                        start_date = datetime.strptime(current_auth, "%Y-%m-%d")
                    else:
                        start_date = datetime.now()
                    
                    new_expire = start_date + timedelta(days=sqsj * months)
                    middleware.bucketSet(BUCKET_AUTH, user_id, new_expire.strftime("%Y-%m-%d"))
                    success_count += 1
                except:
                    continue
            
            sender.reply(f"""
=====授权结果=====
📊 选择账号: {len(selected_accounts)}个
✅ 成功: {success_count}个
❌ 失败: {len(selected_accounts) - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
        
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
    
    else:
        sender.reply("❌ 无效的选择")

def check_auth_status():
    """检测所有账号的授权状态"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    try:
        notify_channels = get_config('notify', '')
        if not notify_channels:
            sender.reply("❌ 未配置通知渠道，请在插件配置中设置notify参数")
            return
        
        channels = [channel.strip() for channel in notify_channels.split(',') if channel.strip()]
        if not channels:
            sender.reply("❌ 通知渠道配置格式错误")
            return
        
        all_users = middleware.bucketAllKeys(BUCKET_USER)
        if not all_users:
            sender.reply("❌ 没有找到任何用户绑定的账号")
            return
        
        current_date = str(datetime.now().date())
        total_checked = 0
        total_notified = 0
        
        for user_id in all_users:
            try:
                accounts = eval(middleware.bucketGet(BUCKET_USER, user_id) or '[]')
                if not accounts:
                    continue
            except:
                continue
            
            expired_accounts = []
            invalid_accounts = []
            
            for account in accounts:
                total_checked += 1
                
                auth_time = middleware.bucketGet(BUCKET_AUTH, account)
                if not auth_time or auth_time <= current_date:
                    expired_accounts.append({
                        'user_id': account,
                        'auth_time': auth_time or '未授权'
                    })
                
                # 验证账号有效性
                if not verify_account(account):
                    invalid_accounts.append({
                        'user_id': account,
                        'reason': '账号验证失败'
                    })
            
            if expired_accounts or invalid_accounts:
                notify_msg = "=====地图账号检测报告====="
                
                if expired_accounts:
                    notify_msg += "\n\n🚨 授权过期账号:"
                    notify_msg += "\n" + "-" * 25
                    for acc in expired_accounts:
                        notify_msg += f"\n🆔 {mask_user_id(acc['user_id'])} (到期:{acc['auth_time']})"
                
                if invalid_accounts:
                    notify_msg += "\n\n❌ 账号失效:"
                    notify_msg += "\n" + "-" * 20
                    for acc in invalid_accounts:
                        notify_msg += f"\n🆔 {mask_user_id(acc['user_id'])} ({acc['reason']})"
                
                notify_msg += "\n" + "-" * 20
                notify_msg += "\n💡 发送\"地图管理\"进行处理"
                notify_msg += "\n" + "=" * 14
                
                for channel in channels:
                    try:
                        middleware.push(
                            imType=channel,
                            groupCode='',
                            userID=user_id,
                            title="",
                            content=notify_msg
                        )
                        total_notified += 1
                    except Exception as e:
                        print(f"推送通知失败: {channel}, 用户: {user_id}, 错误: {str(e)}")
        
        sender.reply(f"✅ 检测完成，共检测 {total_checked} 个账号，发送 {total_notified} 条通知")
    
    except Exception as e:
        sender.reply(f"❌ 检测失败: {str(e)}")

def clean_expired_accounts():
    """清理过期账号"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    try:
        sender.reply("🧹 开始清理过期账号...")
        
        expired_accounts = []
        dqsj = datetime.now().strftime("%Y-%m-%d")
        
        for user_id in middleware.bucketAllKeys(BUCKET_AUTH):
            auth_time = middleware.bucketGet(BUCKET_AUTH, user_id)
            if auth_time and auth_time < dqsj:
                expired_accounts.append(user_id)
        
        if not expired_accounts:
            sender.reply("✅ 没有找到过期账号")
            return
        
        sender.reply(f"🔍 找到 {len(expired_accounts)} 个过期账号，开始清理...")
        
        success_count = 0
        for user_id in expired_accounts:
            try:
                middleware.bucketDel(BUCKET_TOKEN, user_id)
                middleware.bucketDel(BUCKET_AUTH, user_id)
                
                # 从用户账号列表中移除
                for uid in middleware.bucketAllKeys(BUCKET_USER):
                    user_accounts = middleware.bucketGet(BUCKET_USER, uid)
                    if user_accounts:
                        try:
                            accounts_list = eval(user_accounts)
                            if user_id in accounts_list:
                                accounts_list.remove(user_id)
                                if accounts_list:
                                    middleware.bucketSet(BUCKET_USER, uid, str(accounts_list))
                                else:
                                    middleware.bucketDel(BUCKET_USER, uid)
                                break
                        except:
                            continue
                
                success_count += 1
            except Exception as e:
                print(f"清理账号异常: {user_id}, 错误: {str(e)}")
        
        sender.reply(f"""
=====清理完成=====
📊 过期账号: {len(expired_accounts)}个
✅ 清理成功: {success_count}个
==================""")
    
    except Exception as e:
        sender.reply(f"""
=====清理异常=====
❌ 错误: {str(e)}
==================""")

def run_all_accounts():
    """一键运行所有已授权账号"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 此功能仅限管理员使用
==================""")
        return
    
    try:
        sender.reply("🔄 开始一键运行所有已授权账号...")
        
        # 获取所有用户
        all_users = middleware.bucketAllKeys(BUCKET_USER)
        if not all_users:
            sender.reply("❌ 未找到任何用户")
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        total_accounts = 0
        valid_accounts = 0
        success_count = 0
        
        # 遍历所有用户
        for user_id in all_users:
            try:
                user_accounts = middleware.bucketGet(BUCKET_USER, user_id)
                if not user_accounts:
                    continue
                
                accounts = eval(user_accounts)
                
                # 遍历该用户的所有账号
                for account_id in accounts:
                    total_accounts += 1
                    
                    # 检查授权状态
                    auth_time = middleware.bucketGet(BUCKET_AUTH, account_id)
                    if not auth_time or auth_time <= today:
                        continue  # 跳过未授权或已过期的账号
                    
                    valid_accounts += 1
                    
                    try:
                        # 获取账号信息
                        account_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, account_id))
                        remark = account_info.get('remark', account_id)
                        
                        # 执行任务
                        task_msg = f"\n🔄 执行账号: {remark}"
                        
                        # 签到
                        checkin_success, checkin_result = do_checkin(account_id)
                        if checkin_success:
                            task_msg += f"\n  ✅ 签到: {checkin_result}"
                        else:
                            task_msg += f"\n  ❌ 签到: {checkin_result}"
                        
                        time.sleep(1)
                        
                        # 抽奖
                        lottery_success, lottery_result, tickets = do_lottery(account_id)
                        if lottery_success and tickets > 0:
                            task_msg += f"\n  🎰 抽奖: {tickets}张券"
                            for idx, prize in enumerate(lottery_result, 1):
                                task_msg += f"\n    第{idx}次: {prize}"
                        
                        time.sleep(1)
                        
                        # 提现
                        withdraw_success, withdraw_result, coins, withdrawable = do_withdraw(account_id)
                        if withdraw_success:
                            task_msg += f"\n  💰 余额: {coins}元 | 提现: {withdraw_result}"
                        
                        sender.reply(task_msg)
                        success_count += 1
                        
                        # 延迟避免请求过快
                        time.sleep(2)
                        
                    except Exception as e:
                        sender.reply(f"\n❌ 账号执行失败: {account_id}, 错误: {str(e)}")
                        continue
            
            except Exception as e:
                print(f"处理用户失败: {user_id}, 错误: {str(e)}")
                continue
        
        # 显示统计结果
        result_msg = f"""
=====一键运行完成=====
📊 总账号数: {total_accounts}个
✅ 已授权: {valid_accounts}个
🎯 执行成功: {success_count}个
❌ 执行失败: {valid_accounts - success_count}个
=================="""
        sender.reply(result_msg)
    
    except Exception as e:
        sender.reply(f"""
=====运行异常=====
❌ 错误: {str(e)}
==================""")


def show_tutorial():
    """显示教程"""
    tutorial = """
=====腾讯地图教程=====
📱 用户指令:
• 地图登录 - 绑定账号
• 地图管理 - 管理账号
• 地图查询 - 查询信息
• 地图教程 - 查看教程
------------------
🔧 管理员指令:
• 地图授权 - 管理员授权
• 地图检测 - 检测账号状态
• 清理地图 - 清理过期账号
------------------
💡 登录格式:
📝 格式: 备注#user_id
📝 示例: 
张三#abc123def456
李四#xyz789ghi012
💡 支持批量登录，每行一个账号
------------------
📝 如何获取user_id:
1. 打开腾讯地图小程序
2. 进入活动页面
3. 抓包获取请求头的user_id参数
------------------
💰 收益说明:
• 每日签到: 获得金币
• 抽奖活动: 随机奖励
• 自动提现: 达到阈值自动提现
• 预计收益: 0.1/天
------------------
🎯 使用流程:
1. 发送"地图登录"绑定账号
2. 发送"地图管理"进行授权
3. 在管理中选择"执行任务"
4. 自动完成签到、抽奖、提现
=================="""
    sender.reply(tutorial)

if __name__ == '__main__':
    message = sender.getMessage()
    
    # 主逻辑处理
    if '登录' in message or '登陆' in message:
        bind_account()
    
    elif '管理' in message:
        manage_account()
    
    elif '查询' in message:
        query_accounts()
    
    elif '授权' in message:
        admin_authorize()
    
    elif '检测' in message:
        check_auth_status()
    
    elif '清理' in message:
        clean_expired_accounts()
    
    elif '一键运行' in message:
        run_all_accounts()
    
    elif '教程' in message:
        show_tutorial()
