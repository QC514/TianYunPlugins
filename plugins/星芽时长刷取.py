# [title: 星芽时长刷取]
# [language: python]
# [class: 工具类]
# [service: 2993959969] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(星芽|xydj)(刷时长)$|^(刷时长|刷取时长)(星芽|xydj)$|^星芽刷时长$]
# [cron: 0 0 0 0 0] cron定时，支持5位域和6位域
# [priority: 0] 优先级，数字越大表示优先级越高
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [open_source: false]是否开源
# [icon: https://img-cf.885666.xyz/00ba8684fe6b55ef6cd1f255a50812d5.png]图标链接地址，请使用48像素的正方形图标，支持http和https
# [version: 1.0.0]版本号
# [public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 8.88] 上架价格
# [description: 星芽短剧时长刷取付费服务<br>码支付配合积分插件参数进行使用<br>按分钟计费，快速刷取观看时长]

import os
import json
import time
import hashlib
import random
import string
import base64
import requests
import uuid
from datetime import datetime, timedelta
import middleware

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 's_xydj_duration',
    'name': '星芽时长刷取'
}

# 支付方式中文名称映射
PAY_TYPE_NAMES = {
    'alipay': '支付宝',
    'wxpay': '微信支付',
    'qqpay': 'QQ钱包',
}

# [param: {"required":true,"key":"s_xydj_duration.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"s_xydj_duration.price_per_minute","bool":false,"placeholder":"例:0.01","name":"每分钟价格","desc":"刷取1分钟观看时长的收费金额(单位:元)"}]
# [param: {"required":true,"key":"s_xydj_duration.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付，关闭则使用扫码支付。推荐码支付对接：https://mpay.vorto.cn"}]

def get_user_config():
    """获取用户配置"""
    zsm = middleware.bucketGet('s_xydj_duration', 'zsm') or ''
    price_per_minute = float(middleware.bucketGet('s_xydj_duration', 'price_per_minute') or '0.01')
    ma_pay_switch = middleware.bucketGet('s_xydj_duration', 'ma_pay_switch') or 'false'
    
    return zsm, price_per_minute, ma_pay_switch

def generate_random_uuid():
    """生成随机UUID"""
    return str(uuid.uuid4())

def calculate_md5(text):
    """计算字符串的MD5值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def sort_dict_by_key(data):
    """对字典按照键名排序"""
    return dict(sorted(data.items(), key=lambda x: x[0]))

def generate_qrcode(url):
    """生成二维码图片"""
    try:
        # 使用 qrtool.cn 的API生成二维码
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        return None

def get_user_info_by_token(authorization, device_id):
    """通过authorization获取用户信息"""
    try:
        headers = {
            "Host": "speciesweb.whjzjx.cn",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "sec-ch-ua-platform": "Android",
            "authorization": authorization,
            "device_type": "TA-1361",
            "user_agent": "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240912.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 _dsbridge",
            "raw_channel": "default",
            "dev_token": "BR5G0PFyR-9NAkHgS1rSHb9OQ3MiEBxSDpv4-EZbrBjnMuxm5iYdf4ZUjcr9_LmAay6ZA10zo6p_mvCJPB30swIIDDvxiOqFf2Dtr05iL6kbzpkN4OaSGkXIanwRgb9FslgWBiRZIRV2nM3nrI_yccyFdRj0D0C8rc7AqCRRNtOM*",
            "accept": "application/json, text/plain, */*",
            "channel": "default",
            "device_id": device_id,
            "device_platform": "android",
            "app_version": "3.8.5",
            "device_brand": "nokia",
            "os_version": "15",
            "user-agent": "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240912.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36 _dsbridge",
            "origin": "https://h5static.xingya.com.cn",
            "x-requested-with": "com.jz.xydj",
        }
        
        api_url = f"https://speciesweb.whjzjx.cn/v1/sign/info?device_id={device_id}"
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == "ok" and "data" in result:
                user_data = result["data"]
                return True, {
                    'user_id': user_data.get('account_id', ''),  # 修正字段名为account_id
                    'cash_remain': user_data.get('cash_remain', 0),
                    'species': user_data.get('species', 0)
                }
            else:
                return False, f"获取用户信息失败: {result.get('msg', '未知错误')}"
        else:
            return False, f"请求失败，状态码: {response.status_code}"
            
    except Exception as e:
        return False, f"获取用户信息异常: {str(e)}"

def add_viewing_duration(authorization, device_id, user_id, duration_minutes):
    """增加观看时长"""
    try:
        # 准备请求头
        headers = {
            "x-app-id": "7",
            "authorization": authorization,
            "platform": "1",
            "manufacturer": "Xiaomi",
            "version_name": "3.8.3.1",
            "user_agent": "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/131.0.6778.260 Mobile Safari/537.36",
            "app_version": "3.8.3.1",
            "device_platform": "android",
            "personalized_recommend_status": "1",
            "device_type": "2210132C",
            "device_brand": "Xiaomi",
            "os_version": "15",
            "channel": "default",
            "raw_channel": "default",
            "uuid": f"randomUUID_{generate_random_uuid()}",
            "device_id": device_id,
            "ab_id": "",
            "support_h265": "1",
            "font_scale": "1.0",
            "content-type": "application/json; charset=utf-8"
        }
        
        # 获取当前时间戳
        current_timestamp = int(time.time() * 1000)
        
        # 将分钟转换为秒
        duration_seconds = duration_minutes * 60
        
        # 准备请求体
        request_body = [
            {
                "event_id": "action_episode_view",
                "page_id": "page_drama_detail",
                "eventType": "action",
                "event_type": "action",
                "timestamp": current_timestamp,
                "user_id": str(user_id),
                "login_status": True,
                "retry": 0,
                "device_id": device_id,
                "device_type": "Xiaomi",
                "phone_version": "2210132C",
                "os_type": 1,
                "os_name": "15",
                "version": "3.8.3.1",
                "package_name": "com.jz.xydj",
                "app_id": "7",
                "channel": "default",
                "raw_channel": "default",
                "font_scale": 1.0,
                "define_args": json.dumps({
                    "page": "page_drama_detail",
                    "theater_id": "4328",
                    "theater_number": "1",
                    "theater_duration": str(duration_seconds),
                    "lock": "0",
                    "complete": "0",
                    "show_id": "7de1f4a3cfb04c93bb31c11f7e896ad8",
                    "classification_id": "0",
                    "position": "4",
                    "entrance_scene": "0",
                    "entrance": "5",
                    "top_classification_id": "1",
                    "top_classification_name": "剧场",
                    "ab_id": "",
                    "last_page": "page_drama_detail"
                })
            }
        ]
        
        # 发送请求
        response = requests.post(
            "https://xingya-track.shytkjgs.com/receive",
            headers=headers,
            json=request_body,
            timeout=10
        )
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == "ok":
                return True, f"成功增加 {duration_minutes} 分钟观看时长"
            else:
                return False, f"增加时长失败: {result.get('msg', '未知错误')}"
        else:
            return False, f"请求失败，状态码: {response.status_code}"
            
    except Exception as e:
        return False, f"增加观看时长异常: {str(e)}"

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
        response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
        
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
            # 支付成功，返回支付数据
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
        
        # 使用新的查询接口路径
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
        response = requests.get(query_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return False, None, f"查询订单失败，HTTP状态码: {response.status_code}"
        
        # 解析响应
        try:
            result = response.json()
        except:
            return False, None, "查询订单失败，返回数据格式错误"
        
        # 判断返回结果
        code = result.get('code', 0)
        msg = result.get('msg', '未知状态')
        
        if code == 1:  # 查询成功
            # 检查支付状态
            status = result.get('status', 0)
            if status == 1:  # 支付成功
                return True, result, "支付成功"
            else:
                return True, result, "订单未支付"
        else:
            return False, result, msg
            
    except Exception as e:
        return False, None, f"查询订单异常: {str(e)}"

def poll_mapi_payment_status(config, order_no, max_tries=30):
    """轮询MAPI支付状态"""
    for i in range(max_tries):
        # 查询订单状态 (使用商户订单号)
        success, data, msg = query_mapi_order(config, order_no, is_trade_no=False)

        # 如果查询成功且订单已支付
        if success and isinstance(data, dict) and data.get('status') == 1:
            return True, msg, data
            
        # 等待用户输入或超时
        result = sender.listen(5000)  # 等待5秒
        if result == 'q':
            return False, "用户取消", None
            
    return False, "查询超时，订单可能尚未支付", None

def handle_mapay_order(project, duration_minutes, money, pay_type=None):
    """处理码支付订单"""
    # 检查是否启用码支付
    ma_pay_switch = middleware.bucketGet('s_xydj_duration', 'ma_pay_switch') or 'false'
    if ma_pay_switch.lower() != 'true':
        sender.reply('❌ 码支付功能未开启')
        return False
    
    # 从卡密系统数据桶获取码支付配置
    config = {
        'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
        'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
        'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
        'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or 'http://localhost/notify',
        'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or 'http://localhost/return',
        'pay_type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay'
    }
    
    # 检查配置是否完整
    if not (config['gateway'] and config['pid'] and config['key']):
        sender.reply('❌ 卡密系统的码支付配置不完整，请联系管理员')
        return False
    
    # 添加支付锁检查
    pay_lock_key = 'duration_recharge_lock'
    lock_info = middleware.bucketGet('dd_sign_config', pay_lock_key)
    if lock_info:
        try:
            lock_data = json.loads(lock_info)
            # 检查锁是否过期(2分钟)
            if time.time() - lock_data['time'] < 120:
                sender.reply('当前有其他用户正在支付中，请稍后再试!')
                return False
        except:
            pass
    
    # 设置支付锁
    lock_data = {
        'user': userid,
        'time': int(time.time())
    }
    middleware.bucketSet('dd_sign_config', pay_lock_key, json.dumps(lock_data))
    
    try:
        # 保留两位小数
        amount = round(float(money), 2)
        
        # 生成商户订单号
        out_trade_no = f"XYSC{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        
        # 如果已提供支付方式，直接使用
        if pay_type:
            selected_type = pay_type
        else:
            # 解析支付方式
            pay_types_str = config['pay_type'].strip()
            if not pay_types_str:
                pay_types_str = "alipay,wxpay"  # 默认支付方式
                
            pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
            
            # 选择支付方式
            if len(pay_types) == 1:
                # 只有一种支付方式，直接使用
                selected_type = pay_types[0]
                
                # 显示支付信息
                sender.reply(f"""===== 支付信息 =====
🎫 商品: {project}
⏱️ 时长: {duration_minutes}分钟
💰 金额: {amount}元
------------------
💳 支付方式: {PAY_TYPE_NAMES.get(selected_type, selected_type)}
------------------
正在创建支付订单...
==================""")
            else:
                # 多种支付方式，让用户选择
                pay_options_text = """=====选择支付方式====="""
                for i, t in enumerate(pay_types, 1):
                    pay_options_text += f"\n[{i}] {PAY_TYPE_NAMES.get(t, t)}"
                    
                pay_options_text += """
------------------
回复数字选择支付方式
回复"q"取消支付
=================="""
                
                sender.reply(pay_options_text)
                
                choice = sender.input(120000, 1, False)
                
                if choice.lower() == 'q':
                    sender.reply('✅ 已取消支付')
                    middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
                    return False
                    
                try:
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(pay_types):
                        selected_type = pay_types[choice_idx]
                        
                        # 显示支付信息
                        sender.reply(f"""===== 支付信息 =====
🎫 商品: {project}
⏱️ 时长: {duration_minutes}分钟
💰 金额: {amount}元
------------------
💳 支付方式: {PAY_TYPE_NAMES.get(selected_type, selected_type)}
------------------
正在创建支付订单...
==================""")
                    else:
                        sender.reply('❌ 选择无效，已取消支付')
                        middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
                        return False
                except ValueError:
                    sender.reply('❌ 输入无效，已取消支付')
                    middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
                    return False
        
        # 创建支付订单
        try:
            success, result, msg = create_mapi_payment(
                config=config,
                amount=amount,
                out_trade_no=out_trade_no,
                name=f"{project}-{duration_minutes}分钟",
                user_id=userid,
                pay_type=selected_type
            )
        except Exception as e:
            sender.reply(f'❌ 创建订单时出错: {str(e)}')
            middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
            return False
        
        if not success:
            sender.reply(f'❌ 创建订单失败: {msg}')
            middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
            return False
            
        # 提取支付链接
        trade_no = result.get('trade_no')
        if not trade_no:
            sender.reply('❌ 获取支付订单号失败')
            middleware.bucketDel('dd_sign_config', pay_lock_key)  # 释放支付锁
            return False
            
        # 构建支付链接
        gateway = config['gateway']
        if gateway.endswith('/'):
            gateway = gateway[:-1]
        pay_url = f"{gateway}/pay/{trade_no}"
        
        # 生成短链接
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
        try:
            response = requests.post('https://create.mrw.so/pageHome/createBySingle.htm', headers=headers, data=data)
            short_url = response.json().get('data')
            if short_url:
                pay_url = short_url
        except:
            pass  # 短链接生成失败时使用原始链接
            
        # 发送支付链接
        selected_type_name = PAY_TYPE_NAMES.get(selected_type, selected_type)
        sender.reply(f'请使用【{selected_type_name}】扫描下方二维码完成支付:')
        sender.replyImage(generate_qrcode(pay_url))
            
        sender.reply('支付过程中输入"q"可取消支付')
        
        # 轮询支付结果
        is_paid, msg, data = poll_mapi_payment_status(config, out_trade_no)
        
        # 释放支付锁
        middleware.bucketDel('dd_sign_config', pay_lock_key)
        
        if is_paid:
            # 支付成功
            return True
        else:
            # 支付失败或超时
            sender.reply(f"❌ 支付未完成: {msg}")
            return False
        
    except Exception as e:
        sender.reply(f'❌ 处理支付订单时出错: {str(e)}')
        # 释放支付锁
        middleware.bucketDel('dd_sign_config', pay_lock_key)
        return False

def pay_order_wxpay(project, duration_minutes, money):
    """处理微信支付"""
    if float(money) == 0:
        sender.reply(f"""
=====免费服务=====
🎫 商品: {project}
⏱️ 时长: {duration_minutes}分钟
💰 金额: 免费
==================""")
        return True
    
    # 使用赞赏码支付
    zsm = middleware.bucketGet('s_xydj_duration', 'zsm')
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
        return False
        
    # 生成订单号
    order_id = f"XYSC_{int(time.time())}_{userid}"
    
    # 记录待支付订单
    middleware.bucketSet('s_xydj_duration_order', order_id, json.dumps({
        'user': userid,
        'amount': money,
        'duration_minutes': duration_minutes,
        'time': int(time.time()),
        'status': 'pending'
    }))
    
    # 发送订单信息
    pay_msg = f"""
=====微信扫码支付====
🎫 商品: {project}
⏱️ 时长: {duration_minutes}分钟
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)

    sender.replyImage(zsm)
    
    # 等待支付结果
    ddzf = sender.waitPay("q", 100 * 1000)
    if str(ddzf) == 'q':
        sender.reply('✅ 已取消支付')
        return False
        
    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
            
        # 支持新旧两种收款消息格式
        try:
            paid_amount = float(ddzf.get('Money') or ddzf.get('money', 0))
            pay_time = ddzf.get('Time') or ddzf.get('time', '').replace('T', ' ').split('.')[0]
            if not pay_time:
                pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            sender.reply("支付金额格式错误")
            return False
            
        if paid_amount >= float(money):
            # 更新订单状态
            middleware.bucketSet('s_xydj_duration_order', order_id, json.dumps({
                'user': userid,
                'amount': money,
                'duration_minutes': duration_minutes,
                'paid_amount': paid_amount,
                'time': int(time.time()),
                'pay_time': pay_time,
                'status': 'success'
            }))
            return True
        else:
            sender.reply(f"""
=====支付失败=====
❌ 支付金额不足
------------------
💰 应付: {money}元
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

def process_duration_purchase():
    """处理时长购买流程"""
    sender.reply("""
=====星芽时长刷取=====
💡 输入您的账号信息和刷取时长
回复"q"随时退出操作
==================""")
    
    # 步骤1：输入账号信息
    sender.reply("请输入您的账号信息（格式: authorization#device_id）:")
    account_input = sender.input(120000, 1, False)
    if not account_input:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif account_input.lower() == 'q':
        sender.reply("✅ 已取消操作")
        return
    
    # 解析账号信息
    if '#' not in account_input:
        sender.reply("""
=====格式错误=====
❌ 账号信息格式不正确
------------------
请使用格式: authorization#device_id
例如: eyJhbGc...#87387123-7A4D-4B6A-912A
==================""")
        return
    
    try:
        authorization, device_id = account_input.split('#', 1)
        authorization = authorization.strip()
        device_id = device_id.strip()
        
        if not authorization or not device_id:
            sender.reply("""
=====格式错误=====
❌ authorization或device_id不能为空
------------------
请检查输入格式是否正确
==================""")
            return
    except ValueError:
        sender.reply("""
=====格式错误=====
❌ 账号信息格式不正确
------------------
请使用格式: authorization#device_id
==================""")
        return
    
    # 步骤2：验证账号信息并获取用户ID
    sender.reply("正在验证账号信息...")
    success, user_info = get_user_info_by_token(authorization, device_id)
    
    if not success:
        sender.reply(f"""
=====验证失败=====
❌ {user_info}
------------------
请检查authorization和device_id是否正确
==================""")
        return
    
    user_id = user_info['user_id']
    if not user_id:
        sender.reply("""
=====验证失败=====
❌ 无法获取用户ID
------------------
请确认账号信息是否正确
==================""")
        return
    
    # 显示账号信息
    sender.reply(f"""
=====账号验证成功=====
👤 用户ID: {user_id}
💰 现金余额: {user_info.get('cash_remain', 0)}元
🪙 金币数量: {user_info.get('species', 0)}
==================""")
    
    # 步骤3：输入刷取时长
    sender.reply("请输入需要刷取的时长（分钟）:")
    duration_input = sender.input(120000, 1, False)
    if not duration_input:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif duration_input.lower() == 'q':
        sender.reply("✅ 已取消操作")
        return
    
    try:
        duration_minutes = int(duration_input)
        if duration_minutes <= 0:
            sender.reply("❌ 时长必须大于0分钟")
            return
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
        return
    
    # 获取配置
    zsm, price_per_minute, ma_pay_switch = get_user_config()
    
    # 计算总价格
    total_price = duration_minutes * price_per_minute
    
    # 构建可用的支付方式列表
    available_payments = []
    
    # 检查是否启用码支付
    if ma_pay_switch.lower() == 'true':
        # 从卡密系统获取支付配置
        ma_pay_type = middleware.bucketGet('dd_sign_config', 'ma_pay_type') or ''
        ma_pay_pid = middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or ''
        ma_pay_key = middleware.bucketGet('dd_sign_config', 'ma_pay_key') or ''
        ma_pay_gateway = middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or ''
        
        if ma_pay_gateway and ma_pay_pid and ma_pay_key:
            # 获取支付方式列表
            pay_types_str = ma_pay_type.strip()
            if not pay_types_str:
                pay_types_str = "alipay,wxpay"  # 默认支付方式
                
            pay_types = [p.strip() for p in pay_types_str.split(',') if p.strip()]
            # 添加每种码支付方式
            for pay_type in pay_types:
                name = PAY_TYPE_NAMES.get(pay_type, pay_type)
                available_payments.append((name, f"mapay_{pay_type}"))
        else:
            # 码支付配置不完整，回退到微信支付
            if zsm:
                available_payments.append(("微信支付", "wxpay"))
    else:
        # 码支付未开启，使用传统微信支付
        if zsm:
            available_payments.append(("微信支付", "wxpay"))
    
    if not available_payments:
        sender.reply("""
=====购买失败=====
❌ 未配置任何支付方式
------------------
请联系管理员配置支付方式
==================""")
        return
    
    # 如果只有一种支付方式，直接使用
    if len(available_payments) == 1:
        payment_name, payment_type = available_payments[0]
    else:
        # 显示支付方式选择菜单
        payment_menu = f"""
=====选择支付方式=====
⏱️ 刷取时长: {duration_minutes}分钟
💰 总金额: {total_price:.2f}元
💸 单价: {price_per_minute:.2f}元/分钟
------------------------"""
        
        for i, (name, _) in enumerate(available_payments, 1):
            payment_menu += f"""
[{i}] {name}"""
            
        payment_menu += """
------------------------
回复数字选择方式
回复"q"退出操作
=================="""
        
        sender.reply(payment_menu)
        
        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply("✅ 已取消购买")
            return
        
        try:
            choice_index = int(pay_choice) - 1
            if not (0 <= choice_index < len(available_payments)):
                sender.reply("❌ 无效的选择")
                return
                
            payment_name, payment_type = available_payments[choice_index]
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
    
    # 根据支付类型处理不同的支付方式
    if payment_type == "wxpay":
        # 微信支付处理
        if pay_order_wxpay('星芽时长刷取', duration_minutes, total_price):
            # 支付成功，执行刷取
            sender.reply("✅ 支付成功，正在刷取时长...")
            success, message = add_viewing_duration(authorization, device_id, user_id, duration_minutes)
            
            if success:
                sender.reply(f"""
=====刷取成功=====
✅ {message}
👤 用户ID: {user_id}
⏱️ 刷取时长: {duration_minutes}分钟
💰 支付金额: {total_price:.2f}元
==================""")
            else:
                sender.reply(f"""
=====刷取失败=====
❌ {message}
------------------
💡 支付已完成，请联系客服处理
==================""")
    
    elif payment_type.startswith("mapay_"):
        # 码支付处理
        # 提取实际支付方式（去掉"mapay_"前缀）
        actual_pay_type = payment_type[6:]
        
        # 处理支付
        result = handle_mapay_order('星芽时长刷取', duration_minutes, total_price, actual_pay_type)
        
        # 处理刷取
        if result:
            sender.reply("✅ 支付成功，正在刷取时长...")
            success, message = add_viewing_duration(authorization, device_id, user_id, duration_minutes)
            
            if success:
                sender.reply(f"""
=====刷取成功=====
✅ {message}
👤 用户ID: {user_id}
⏱️ 刷取时长: {duration_minutes}分钟
💰 支付金额: {total_price:.2f}元
==================""")
            else:
                sender.reply(f"""
=====刷取失败=====
❌ {message}
------------------
💡 支付已完成，请联系客服处理
==================""")

def show_tutorial():
    """显示使用教程"""
    tutorial = """
=====星芽时长刷取教程=====
1. 获取账号信息:
  • authorization: 星芽APP的登录令牌
  • device_id: 设备唯一标识符

2. 获取方法:
  • 使用抓包工具（如HttpCanary）
  • 登录星芽短剧APP
  • 找到任意API请求的请求头

3. 账号信息格式:
  • 格式: authorization#device_id
  • 示例: eyJhbGciOiJIUz...#87387123-7A4D-4B6A

4. 使用流程:
  • 发送指令触发插件
  • 输入账号信息（authorization#device_id）
  • 输入需要刷取的时长（分钟）
  • 选择支付方式并完成支付
  • 系统自动刷取时长

5. 计费规则:
  • 按分钟计费
  • 当前价格: 每分钟 XXX 元

6. 支付方式:
  • 支持支付宝/微信支付
  • 支付完成后立即刷取

7. 注意事项:
  • 确保账号信息格式正确
  • 使用#号分隔两个参数
  • 时长立即生效
  • 刷取失败支持退款

如有问题请联系客服
=================="""
    sender.reply(tutorial)

# 主函数
def main():
    # 获取用户消息
    usermessage = sender.getMessage()
    
    # 处理时长刷取
    if '时长' in usermessage or '刷取' in usermessage:
        if '教程' in usermessage or '帮助' in usermessage:
            show_tutorial()
        else:
            process_duration_purchase()
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
