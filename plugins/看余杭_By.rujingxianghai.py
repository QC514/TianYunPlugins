# [rule: ^(看余杭|kyh)(登录|登陆)$|^登(录|陆)(看余杭|kyh)$|^(看余杭|kyh)(查询|管理)$|^(查询|管理)(看余杭|kyh)$|^看余杭授权$|^看余杭教程$|^看余杭检测$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 18 9 * * *]
# [public: true]
# [title: 看余杭]
# [icon: https://y.gtimg.cn/music/photo_new/T053M000001FQSCZ2vJ29e.jpg]
# [open_source: false]
# [class: 工具类]
# [version: 1.3.1]
# [price: 3.88]
# [admin: false]
# [author: rujingxianghai]
# [service: 2993959969]
# [description: 看余杭积分实物<br>指令：看余杭登录、管理、查询、授权、教程<br>脚本及卡密进群获取<br>1.3.1：优化码支付二维码生成方式<br>1.3.0：检测逻辑改为到期提前天数提醒，管理员授权改为按天数授权（正数增加负数减少），完善定时任务<br>1.2.5：适配新版积分数据桶]

import os
import json
import time
import base64
import hashlib
import random
import string
import requests
from datetime import datetime, timedelta
import middleware

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_kyh_user', key=userid)

# 接口地址
base_url = 'https://app.eyh.cn/gateway/api'

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 's_kyh_config',
    'coin_key': 'dd_sign_points',
    'name': '看余杭'
}


# [param: {"required":true,"key":"s_kyh_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"s_kyh_config.kyh_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割"}]
# [param: {"required":true,"key":"s_kyh_config.kyh_osname","bool":false,"placeholder":"必填项,例:KYH_CK","name":"提交到青龙的变量名","desc":"青龙容器内看余杭的变量名"}]
# [param: {"required":true,"key":"s_kyh_config.kyhVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"s_kyh_config.kyhcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"s_kyh_config.epay_pid","bool":false,"placeholder":"码支付商户ID","name":"码支付商户ID","desc":"码支付商户ID"}]
# [param: {"required":false,"key":"s_kyh_config.epay_key","bool":false,"placeholder":"码支付密钥","name":"码支付密钥","desc":"码支付密钥"}]
# [param: {"required":false,"key":"s_kyh_config.epay_api","bool":false,"placeholder":"码支付接口地址","name":"码支付接口地址","desc":"码支付接口地址，例如https://pay.example.com/"}]
# [param: {"required":false,"key":"s_kyh_config.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"到期提醒通知推送渠道，多个用逗号分隔"}]
# [param: {"required":false,"key":"s_kyh_config.notify_days","bool":false,"placeholder":"3","name":"到期提醒提前天数","desc":"到期日前多少天开始提醒"}]

def get_user_content():
    """获取用户配置内容"""
    kyh_osname = middleware.bucketGet('s_kyh_config', 'kyh_osname') or 'KYH_CK'
    kyh_qlname = middleware.bucketGet('s_kyh_config', 'kyh_qlname') or ''
    kyh_managecommand = middleware.bucketGet('s_kyh_config', 'kyh_managecommand') or '看余杭管理'
    kyh_querycommand = middleware.bucketGet('s_kyh_config', 'kyh_querycommand') or '看余杭查询'
    kyh_signcommand = middleware.bucketGet('s_kyh_config', 'kyh_signcommand') or '看余杭登录'
    
    randommanagecommand = kyh_managecommand
    randomquerycommand = kyh_querycommand
    randomsigncommand = kyh_signcommand
    
    kyhVipmoney = float(middleware.bucketGet('s_kyh_config', 'kyhVipmoney') or '1')
    
    # 优先从卡密系统获取积分配置
    kyhcoin = middleware.bucketGet(PLUGIN_CONFIG['bucket'], PLUGIN_CONFIG['coin_key'])
    if not kyhcoin:
        # 如果卡密系统未配置，则使用插件配置
        kyhcoin = middleware.bucketGet('s_kyh_config', 'kyhcoin') or '0'
    kyhcoin = int(kyhcoin)
    
    # 获取易支付配置
    epay_pid = middleware.bucketGet('s_kyh_config', 'epay_pid') or ''
    epay_key = middleware.bucketGet('s_kyh_config', 'epay_key') or ''
    epay_api = middleware.bucketGet('s_kyh_config', 'epay_api') or ''
    
    return (kyh_osname, kyh_qlname, randommanagecommand, 
            randomquerycommand, randomsigncommand, kyhVipmoney, kyhcoin, 
            epay_pid, epay_key, epay_api)

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

def generate_trace_id():
    """生成追踪ID"""
    return ''.join([random.choice(string.digits) for _ in range(20)])

def random_str(length=16):
    """生成指定长度的随机字符串"""
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def sort_dict_by_key(data):
    """按键名对字典进行排序（易支付需要）"""
    return dict(sorted(data.items(), key=lambda x: x[0]))

def generate_iframe_url(url):
    """将URL通过base64编码生成iframe页面链接
    
    Args:
        url: 原始支付链接
        
    Returns:
        str: iframe页面链接
    """
    try:
        # 将URL进行base64编码
        encoded = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        # 生成iframe页面链接
        iframe_url = f"https://metwhale.github.io?u={encoded}"
        return iframe_url
    except Exception as e:
        # 编码失败时返回原始URL
        return url

def generate_qrcode(url):
    """生成二维码图片
    
    Args:
        url: 要生成二维码的URL
        
    Returns:
        str: 二维码图片的URL
    """
    # 主接口配置
    QRCODE_API_URL = "https://qrcode.vorto.cn/api/qrcode/generate"
    QRCODE_API_KEY = "4jpC3Cgd0zA7Z3HTJ6aDfW9QjtzitDGI"
    
    try:
        # 使用主接口生成二维码
        response = requests.post(
            QRCODE_API_URL,
            json={"content": url},
            headers={"X-API-Key": QRCODE_API_KEY},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data', {}).get('url'):
                return result['data']['url']
    except Exception as e:
        print(f"主接口生成二维码失败: {str(e)}")
    
    # 备用接口：使用 qrtool.cn 的API生成二维码
    try:
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        # 生成失败时返回None
        return None

def generate_sign(params, key):
    """生成签名（易支付需要）"""
    # 移除sign参数
    if 'sign' in params:
        params.pop('sign')
    if 'sign_type' in params:
        params.pop('sign_type')
    
    # 按键名排序
    sorted_params = sort_dict_by_key(params)
    
    # 构建查询字符串，忽略值为空的参数
    query_string = "&".join([f"{k}={v}" for k, v in sorted_params.items() if v])
    
    # 附加密钥
    sign_string = f"{query_string}{key}"
    
    # MD5加密并转大写
    md5 = hashlib.md5()
    md5.update(sign_string.encode('utf-8'))
    return md5.hexdigest().upper()

def verify_token(token, device_id):
    """验证token是否有效"""
    return api_request("user/getUserInfo", token, device_id, service="core")

def get_award_emoji(description):
    """根据奖品描述返回合适的emoji图标"""
    description = description.lower() if description else ""
    
    if '红包' in description:
        return '💰'
    elif '积分' in description:
        return '🔄'
    elif '优惠券' in description or '代金券' in description:
        return '🎟️'
    elif '兑换券' in description:
        return '🏷️'
    elif '提货券' in description:
        return '🛒'
    else:
        return '🎁'

def get_task_list(token, device_id):
    """获取任务列表"""
    try:
        timestamp = str(int(time.time() * 1000))
        trace_id = f"ZIED77K6{timestamp}"
        data = {
            "traceId": trace_id,
            "data": {"content": "null"},
            "service": "media",
            "userDevice": {
                "os": "9",
                "deviceBrand": "samsung",
                "deviceId": device_id,
                "equipmentId": device_id,
                "deviceType": "Samsung SM-N9760",
                "device": "android",
                "clientVersion": "5.1.0"
            },
            "api": "spreadActivity/getAppUserSpreadActivity",
            "token": token
        }
        
        headers = {
            "Connection": "Keep-Alive",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "*/*",
            "Accept-Language": "zh-cn",
            "Host": "app.eyh.cn",
            "Referer": "https://app.eyh.cn/gateway/api",
            "User-Agent": "okhttp/5.0.0-alpha.2"
        }
        
        response = requests.post(base_url, headers=headers, json=data)
        result = response.json()
        
        if result.get("code") == "0":
            return {
                "success": True,
                "data": result.get("data", {})
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "获取任务失败")
            }
    except Exception as e:
        print(f"获取任务列表失败: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

def get_win_records(token, uid, device_id):
    """获取中奖记录"""
    return api_request("lottery/queryActivityAwardRecordList", token, device_id, data={"uid": uid, "content": "null"})

# 添加一个时间戳转换函数
def timestamp_to_date(timestamp):
    """将毫秒时间戳转换为日期字符串"""
    if not timestamp:
        return ""
    
    # 检查是否是字符串类型，如果是则尝试转换为整数
    if isinstance(timestamp, str):
        try:
            timestamp = int(timestamp)
        except ValueError:
            return timestamp
    
    # 检查是否是13位时间戳（毫秒级）
    if timestamp > 10000000000:  # 13位时间戳
        timestamp = timestamp / 1000  # 转换为秒
        
    try:
        # 转换为datetime对象
        dt_object = datetime.fromtimestamp(timestamp)
        # 格式化为字符串
        return dt_object.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"时间戳转换错误: {e}")
        return str(timestamp)  # 返回原始值

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply(format_message("未绑定账号", [
            "❌ 未找到任何账号信息",
            f"💡 发送 {randomsigncommand} 绑定"
        ]))
        return
        
    accounts = eval(uservalue)
    account_list_lines = ["[0] 全部账号"]
    
    for i, phone in enumerate(accounts, 1):
        account_info_str = middleware.bucketGet('s_kyh_token', phone)
        if not account_info_str:
            continue
            
        account_info = json.loads(account_info_str)
        remark = account_info.get('remark', phone)
        auth_time = middleware.bucketGet('s_kyh_auth', phone)
        
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
            
        account_list_lines.append(f"[{i}]{mask_phone(phone)}({remark}, {auth_status})")
    
    account_list_lines.append("=====================")
    account_list_lines.append("支持多选，用英文逗号分隔")
    account_list_lines.append("例如: 1,2,3")
    account_list_lines.append("回复\"q\"退出操作")
    account_list_lines.append("=====================")
    
    sender.reply(format_message("选择账号", account_list_lines, ""))
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出查询")
        return
        
    try:
        # 处理账号选择
        selected_accounts = []
        
        if choice == '0':
            # 选择全部账号
            selected_accounts = accounts.copy()
        else:
            # 处理多选
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
            
        # 显示选择的账号数量
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号，正在查询...")
        
        # 查询每个账号的信息
        query_count = 0
        for phone in selected_accounts:
            try:
                account_info_str = middleware.bucketGet('s_kyh_token', phone)
                if not account_info_str:
                    sender.reply(show_error("账号不存在", "未找到账号信息", f"📱 手机号: {mask_phone(phone)}"))
                    continue
                    
                account_info = json.loads(account_info_str)
                token = account_info.get('token', '')
                device_id = account_info.get('device_id', '')
                uid = account_info.get('uid', '')
                
                # 验证token有效性
                token_verify = verify_token(token, device_id)
                if not token_verify.get('success'):
                    sender.reply(show_error("账号已失效", "Token已失效", [
                        f"📱 手机号: {mask_phone(phone)}",
                        "------------------",
                        "请重新登录绑定此账号"
                    ]))
                    continue
                    
                # 获取用户数据
                user_data = token_verify.get('data', {})
                
                # 检查微信绑定状态
                wechat_status = "已绑定" if user_data.get('wechatOpenid') else "未绑定"
                wechat_emoji = "✅" if user_data.get('wechatOpenid') else "❌"
                
                # 获取授权信息
                auth_time = middleware.bucketGet('s_kyh_auth', phone)
                auth_status = '未授权'
                if auth_time:
                    if auth_time < str(datetime.now().date()):
                        auth_status = '已过期'
                    else:
                        auth_status = f'到期时间: {auth_time}'
                        
                # 获取中奖记录
                win_records = get_win_records(token, uid, device_id)
                
                # 构建账号信息
                info_lines = [
                    f"📱 手机号: {mask_phone(phone)}",
                    f"👤 备注: {account_info.get('remark', '未设置')}",
                    f"🔐 {auth_status}",
                    f"👋 微信绑定: {wechat_emoji} {wechat_status}"
                ]
                
                # 添加中奖记录信息
                if win_records.get('success') and win_records.get('data'):
                    records = win_records.get('data')
                    info_lines.append("---------------------------")
                    
                    for i, record in enumerate(records[:5], 1):  # 最多显示5条
                        award = record.get('description', record.get('name', '未知奖品'))
                        create_time = record.get('createTime', '')
                        # 使用时间戳转换函数
                        time_str = timestamp_to_date(create_time)
                        emoji = get_award_emoji(award)
                        info_lines.append(f"{emoji} {award} {time_str}")
                
                sender.reply(format_message(f"账号信息[{query_count+1}/{len(selected_accounts)}]", info_lines))
                query_count += 1
                
                # 如果查询的账号过多，中间加一点延迟
                if query_count < len(selected_accounts) and len(selected_accounts) > 3:
                    time.sleep(0.5)
                    
            except Exception as e:
                sender.reply(show_error(f"查询异常[{query_count+1}/{len(selected_accounts)}]", str(e), f"📱 手机号: {mask_phone(phone)}"))
                query_count += 1
                
        # 查询完成提示
        if query_count > 0:
            sender.reply(f"✅ 查询完成，共查询了 {query_count} 个账号")
            
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")

def get_ql_token(host, client_id, client_secret):
    """获取青龙 token"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        response = requests.get(url)
        data = response.json()
        if data.get('code') == 200:
            return data['data']['token']
        return None
    except:
        return None

def update_ql_env(phone, account_info):
    """更新青龙环境变量"""
    remark = account_info.get('remark', phone)
    token = account_info.get('token', '')
    uid = account_info.get('uid', '')
    device_id = account_info.get('device_id', '')
    
    if not token:
        print(f"更新青龙变量失败: 没有有效的token")
        return False
        
    # 格式化变量值: remark#token#uid
    env_value = f"{remark}#{token}#{uid}#{device_id}"
    
    # 获取配置的变量名
    env_name = middleware.bucketGet('s_kyh_config', 'kyh_osname') or 'KYH_CK'
    
    print(f"开始更新青龙变量: 手机号={phone}, 变量名={env_name}, UID={uid}")
    # 使用配置的变量名
    success, message = Addenvs(phone, env_value, env_name, account_info)
    if not success:
        print(f"更新青龙变量失败: {message}")
    else:
        print(f"成功更新青龙变量: 手机号={phone}, 变量名={env_name}")
    return success

def Addenvs(phone, value, env_name="KYH_CK", account_info=None):
    """添加青龙环境变量"""
    try:
        # 从配置中获取青龙信息
        ql_config = get_ql_config()
        if ql_config['code'] != 200:
            return False, ql_config['msg']
            
        host = ql_config['data'].get('url', '')
        client_id = ql_config['data'].get('client_id', '')
        client_secret = ql_config['data'].get('client_secret', '')
        
        if not host or not client_id or not client_secret:
            return False, "青龙配置信息不完整"
            
        # 获取青龙token
        token_response = requests.get(f"{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}")
        if token_response.status_code != 200:
            return False, f"获取青龙token失败: {token_response.text}"
            
        token = token_response.json().get('data', {}).get('token', '')
        if not token:
            return False, "获取青龙token失败: 返回数据中没有token"
            
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # 获取所有环境变量
        envs_response = requests.get(f'{host}/open/envs', headers=headers)
        if envs_response.status_code != 200:
            error_msg = f"获取环境变量失败: {envs_response.text}"
            print(error_msg)
            return False, error_msg
            
        envs = envs_response.json()['data']
        env_id = None
        
        # 构建变量备注 - 手机号是关键匹配信息
        auth_time = middleware.bucketGet('s_kyh_auth', phone) or '未授权'
        remark = f"看余杭:{phone}丨用户:{account_info.get('uid', '')}丨到期:{auth_time}"
        
        print(f"构建的青龙变量备注: {remark}")
        print(f"开始查找已存在的变量: 变量名={env_name}, 手机号={phone}")
        
        # 查找是否已存在该变量 - 通过变量名和手机号精确匹配
        for env in envs:
            env_remarks = env.get('remarks', '')
            if env['name'] == env_name and f"看余杭:{phone}" in env_remarks:
                # 兼容不同版本的青龙面板
                env_id = env.get('_id') or env.get('id')
                print(f"找到已存在的变量ID: {env_id}, 备注: {env_remarks}")
                break
        
        if not env_id:
            print(f"未找到匹配的变量，将创建新变量")
        
        # 构建变量数据
        env_data = {
            "name": env_name,
            "value": value,
            "remarks": remark
        }
        
        # 根据是否存在决定更新或添加
        if env_id:
            # 更新已存在的变量
            env_data["id"] = env_id
            print(f"正在更新变量: ID={env_id}, 名称={env_name}")
            print(f"更新数据: {json.dumps(env_data)}")
            update_response = requests.put(f'{host}/open/envs', headers=headers, json=env_data)
            if update_response.status_code != 200:
                error_msg = f"更新环境变量失败: {update_response.text}"
                print(error_msg)
                return False, error_msg
                
            # 启用变量
            enable_response = requests.put(f'{host}/open/envs/enable', headers=headers, json=[env_id])
            if enable_response.status_code != 200:
                print(f"启用变量失败: {enable_response.text}")
                
            print(f"成功更新变量: {env_id}")
            return True, "更新环境变量成功"
        else:
            # 添加新变量
            print(f"正在添加新变量: 名称={env_name}")
            print(f"添加数据: {json.dumps([env_data])}")
            add_response = requests.post(f'{host}/open/envs', headers=headers, json=[env_data])
            if add_response.status_code != 200:
                error_msg = f"添加环境变量失败: {add_response.text}"
                print(error_msg)
                return False, error_msg
                
            # 获取新添加变量的ID并启用
            result = add_response.json()
            if result['code'] == 200:
                new_id = result['data'][0].get('_id') or result['data'][0].get('id')
                if new_id:
                    enable_response = requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id])
                    if enable_response.status_code != 200:
                        print(f"启用变量失败: {enable_response.text}")
                print(f"成功添加新变量: {new_id}")
            
            return True, "添加环境变量成功"
            
    except Exception as e:
        error_msg = f"添加环境变量发生异常: {str(e)}"
        print(error_msg)
        return False, error_msg

def delete_ql_env(phone, env_name=None):
    """删除青龙环境变量"""
    try:
        # 获取变量名
        if not env_name:
            env_name = middleware.bucketGet('s_kyh_config', 'kyh_osname') or 'KYH_CK'
            
        # 从配置中获取青龙信息
        ql_config = get_ql_config()
        if ql_config['code'] != 200:
            print(ql_config['msg'])
            return False
            
        host = ql_config['data'].get('url', '')
        client_id = ql_config['data'].get('client_id', '')
        client_secret = ql_config['data'].get('client_secret', '')
        
        if not host or not client_id or not client_secret:
            print("青龙配置信息不完整")
            return False
        
        # 获取token
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False
            
        # 查找要删除的变量
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f'{host}/open/envs', headers=headers)
        envs = response.json()['data']
        
        deleted = False
        for env in envs:
            # 精确匹配：变量名必须一致，并且备注中必须包含该手机号
            if env['name'] == env_name and f"看余杭:{phone}" in env.get('remarks', ''):
                # 删除变量
                env_id = env.get('_id') or env.get('id')
                response = requests.delete(
                    f'{host}/open/envs',
                    headers=headers,
                    json=[env_id]
                )
                if response.status_code == 200:
                    deleted = True
                    print(f"删除青龙变量成功: {env_id}")
                else:
                    print(f"删除青龙变量失败: {response.text}")
                    
        return deleted
        
    except Exception as e:
        print(f"删除青龙变量异常: {str(e)}")
        return False

def pay_order(project, months, money):
    """处理支付"""
    if float(money) == 0:
        sender.reply(f"""
=====授权成功=====
🎫 商品: {project}
📅 时长: {months}月
💰 金额: 免费
==================""")
        return True
        
    zsm = middleware.bucketGet('s_kyh_config', 'zsm')
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
        return False
        
    # 生成订单号
    order_id = f"KYH_{int(time.time())}_{userid}"
    
    # 记录待支付订单
    middleware.bucketSet('s_kyh_order', order_id, json.dumps({
        'user': userid,
        'amount': money,
        'months': months,
        'time': int(time.time()),
        'status': 'pending'
    }))
    
    # 发送订单信息
    pay_msg = f"""
=====微信扫码支付====
🎫 商品: {project}
📅 时长: {months}月
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
            middleware.bucketSet('s_kyh_order', order_id, json.dumps({
                'user': userid,
                'amount': money,
                'months': months,
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
def create_epay_order(user_id, product, months, money, pay_type):
    """创建易支付订单"""
    try:
        # 获取易支付配置
        (_, _, _, _, _, _, _, 
         epay_pid, epay_key, epay_api) = get_user_content()
        
        if not epay_pid or not epay_key or not epay_api:
            return {"success": False, "message": "未配置易支付信息"}
            
        # 确保API地址以/结尾
        if not epay_api.endswith('/'):
            epay_api += '/'
            
        # 生成订单号
        out_trade_no = f"KYH{int(time.time())}{random.randint(1000, 9999)}"
        
        # 构建请求参数
        notify_url = "http://127.0.0.1/notify_url"  # 回调通知地址
        return_url = "http://127.0.0.1/return_url"  # 支付后跳转地址
        
        params = {
            "pid": epay_pid,
            "type": pay_type,  # 支付方式
            "out_trade_no": out_trade_no,
            "notify_url": notify_url,
            "return_url": return_url,
            "name": product,
            "money": str(money),
            "sign_type": "MD5"
        }
        
        # 生成签名
        params["sign"] = generate_sign(params, epay_key)
        
        # 发起API请求
        create_url = f"{epay_api}submit.php"
        response = requests.post(create_url, data=params)
        
        # 检查响应结果
        if response.status_code != 200:
            return {"success": False, "message": f"易支付请求失败: {response.status_code}"}
            
        # 尝试解析JSON响应，有些接口可能直接返回支付页面
        try:
            result = response.json()
            if result.get("code") == 1:
                # 保存订单信息
                middleware.bucketSet('s_kyh_epay_order', out_trade_no, json.dumps({
                    'user_id': user_id,
                    'product': product,
                    'months': months,
                    'money': money,
                    'pay_type': pay_type,
                    'status': 'pending',
                    'create_time': int(time.time())
                }))
                
                return {
                    "success": True,
                    "order_no": out_trade_no,
                    "pay_url": result.get("pay_url", ""),
                    "qrcode": result.get("qrcode", "")
                }
            else:
                return {"success": False, "message": result.get("msg", "创建订单失败")}
        except:
            # 如果不是JSON，可能是直接返回了支付页面HTML
            # 保存订单信息
            middleware.bucketSet('s_kyh_epay_order', out_trade_no, json.dumps({
                'user_id': user_id,
                'product': product,
                'months': months,
                'money': money,
                'pay_type': pay_type,
                'status': 'pending',
                'create_time': int(time.time())
            }))
            
            # 提取并返回支付链接或二维码
            pay_url = f"{epay_api}submit.php?pid={epay_pid}&type={pay_type}&out_trade_no={out_trade_no}&name={product}&money={money}&sign_type=MD5&sign={params['sign']}"
            return {
                "success": True,
                "order_no": out_trade_no,
                "pay_url": pay_url,
                "qrcode": ""
            }
    except Exception as e:
        return {"success": False, "message": f"创建易支付订单异常: {str(e)}"}

def query_epay_order(out_trade_no):
    """查询易支付订单状态"""
    try:
        # 获取易支付配置
        (_, _, _, _, _, _, _, 
         epay_pid, epay_key, epay_api) = get_user_content()
        
        if not epay_pid or not epay_key or not epay_api:
            return {"success": False, "message": "未配置易支付信息"}
            
        # 确保API地址以/结尾
        if not epay_api.endswith('/'):
            epay_api += '/'
            
        # 构建请求参数
        params = {
            "act": "order",
            "pid": epay_pid,
            "key": epay_key,
            "out_trade_no": out_trade_no
        }
        
        # 发起API请求
        query_url = f"{epay_api}api.php"
        response = requests.get(query_url, params=params)
        
        # 检查响应结果
        if response.status_code != 200:
            return {"success": False, "message": f"查询订单失败: {response.status_code}"}
            
        result = response.json()
        if result.get("code") == 1:
            # 查询成功
            order_info = result.get("data", {})
            trade_status = order_info.get("status")
            
            # 如果已支付，更新本地订单状态
            if trade_status == 1:  # 已支付
                local_order = middleware.bucketGet('s_kyh_epay_order', out_trade_no)
                if local_order:
                    order_data = json.loads(local_order)
                    order_data['status'] = 'success'
                    order_data['pay_time'] = int(time.time())
                    middleware.bucketSet('s_kyh_epay_order', out_trade_no, json.dumps(order_data))
            
            return {
                "success": True,
                "order_no": out_trade_no,
                "status": trade_status,
                "money": order_info.get("money", "0"),
                "pay_time": order_info.get("endtime", "")
            }
        else:
            return {"success": False, "message": result.get("msg", "查询订单失败")}
    except Exception as e:
        return {"success": False, "message": f"查询易支付订单异常: {str(e)}"}

def poll_order_status(out_trade_no, max_tries=60, interval=3):
    """轮询订单状态"""
    for attempt in range(max_tries):
        result = query_epay_order(out_trade_no)
        if result.get("success") and result.get("status") == 1:
            return True
        time.sleep(interval)
    return False
    
def authorize_account(phone, account_info):
    """授权账号功能"""
    # 获取配置信息
    (_, _, _, _, _, kyhVipmoney, kyhcoin,
     epay_pid, epay_key, epay_api) = get_user_content()
    
    # 构建可用的支付方式列表
    available_payments = []
    
    # 微信支付（检查是否配置了收款码）
    zsm = middleware.bucketGet('s_kyh_config', 'zsm')
    if zsm:
        available_payments.append(("微信支付", "wxpay"))
        
    # 易支付（检查是否配置了完整的易支付信息）
    if epay_pid and epay_key and epay_api:
        available_payments.append(("易支付", "epay"))
        
    # 积分兑换（检查是否开启了积分功能）
    if kyhcoin and int(kyhcoin) > 0:
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
        payment_name, payment_type = available_payments[0]
    else:
        # 显示支付方式选择菜单
        auth_menu = """
=====授权方式选择====="""
        
        for i, (name, _) in enumerate(available_payments, 1):
            auth_menu += f"""
[{i}] {name}"""
            
        auth_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""
        
        sender.reply(auth_menu)
        
        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply("✅ 已取消授权")
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
    
    # 设置授权时长
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
            
        # 根据支付类型处理不同的支付方式
        if payment_type == "wxpay":
            # 计算价格
            money = months * kyhVipmoney
            # 微信支付处理
            if pay_order(project='看余杭授权', months=months, money=money):
                process_authorization(phone, account_info, months)
                
        elif payment_type == "epay":
            # 易支付处理
            # 选择支付方式
            payment_menu = """
=====选择支付方式=====
[1] 支付宝
[2] 微信支付
[3] QQ钱包
------------------
回复数字选择支付方式
回复"q"退出操作
=================="""
            sender.reply(payment_menu)
            
            pay_type_choice = sender.input(120000, 1, False)
            if not pay_type_choice or pay_type_choice.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return
                
            pay_type_map = {
                '1': 'alipay',
                '2': 'wxpay',
                '3': 'qqpay'
            }
            
            if pay_type_choice not in pay_type_map:
                sender.reply("❌ 无效的选择")
                return
                
            money = months * kyhVipmoney
            process_epay_payment(phone, account_info, months, money, pay_type_map[pay_type_choice])
            
        elif payment_type == "coin":
            # 积分兑换处理
            process_coin_exchange(phone, account_info, months, kyhcoin)
            
    except ValueError:
        sender.reply("❌ 请输入有效的数字")
        return

def manage_account():
    """账号管理功能"""
    if not uservalue:
        sender.reply(format_message("未绑定账号", [
            "❌ 未找到任何账号信息",
            f"💡 发送 {randomsigncommand} 绑定"
        ]))
        return
        
    accounts = eval(uservalue)
    
    # 先显示管理功能菜单
    menu_lines = [
        "[1] 授权账号",
        "[2] 删除账号",
        "[3] 提交青龙",
        "------------------",
        "回复数字选择功能",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("账号管理", menu_lines))
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    
    # 然后显示账号列表供选择
    account_list_lines = ["[0] 全部账号"]
    
    for i, phone in enumerate(accounts, 1):
        account_info_str = middleware.bucketGet('s_kyh_token', phone)
        if not account_info_str:
            continue
            
        account_info = json.loads(account_info_str)
        remark = account_info.get('remark', phone)
        auth_time = middleware.bucketGet('s_kyh_auth', phone)
        
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
            
        account_list_lines.append(f"[{i}]{mask_phone(phone)}({remark}, {auth_status})")
    
    account_list_lines.extend([
        "=====================",
        "支持多选，用英文逗号分隔",
        "例如: 1,2,3",
        "回复\"q\"退出操作"
    ])
        
    sender.reply(format_message("选择账号", account_list_lines))
    
    account_choice = sender.input(120000, 1, False)
    if not account_choice or account_choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
        
    try:
        # 处理账号选择
        selected_accounts = []
        
        if account_choice == '0':
            # 选择全部账号
            selected_accounts = accounts.copy()
        else:
            # 处理多选
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
            
        # 显示选择的账号数量
        sender.reply(f"✅ 已选择 {len(selected_accounts)} 个账号")
            
        # 根据之前的功能选择执行对应操作
        if choice == '1':
            # 授权选中的账号
            authorize_multiple_accounts(selected_accounts)
            
        elif choice == '2':
            # 删除选中的账号
            confirm_lines = [
                "⚠️ 此操作不可恢复",
                "------------------",
                "回复 y 确认删除",
                "回复 n 取消操作"
            ]
            sender.reply(format_message("确认删除", confirm_lines))
            
            confirm = sender.input(120000, 1, False)
            if confirm.lower() == 'y':
                success_count = 0
                for phone in selected_accounts:
                    try:
                        # 从账号列表中移除
                        if phone in accounts:
                            accounts.remove(phone)
                            
                        # 删除相关信息
                        middleware.bucketDel('s_kyh_token', phone)
                        middleware.bucketDel('s_kyh_auth', phone)
                            
                        # 删除青龙变量
                        delete_ql_env(phone)
                        success_count += 1
                    except Exception as e:
                        print(f"删除账号失败: {phone}, 错误: {str(e)}")
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet('s_kyh_user', userid, str(accounts))
                else:
                    middleware.bucketDel('s_kyh_user', userid)
                    
                sender.reply(f"✅ 已成功删除 {success_count}/{len(selected_accounts)} 个账号")
            else:
                sender.reply("✅ 已取消删除")
                
        elif choice == '3':
            # 提交选中账号到青龙
            success_count = 0
            for phone in selected_accounts:
                try:
                    account_info_str = middleware.bucketGet('s_kyh_token', phone)
                    if not account_info_str:
                        continue
                        
                    account_info = json.loads(account_info_str)
                    
                    # 如果已授权则更新青龙变量
                    auth_time = middleware.bucketGet('s_kyh_auth', phone)
                    if auth_time and auth_time >= str(datetime.now().date()):
                        if update_ql_env(phone, account_info):
                            success_count += 1
                    else:
                        print(f"账号未授权或已过期: {phone}")
                except Exception as e:
                    print(f"提交青龙失败: {phone}, 错误: {str(e)}")
            
            result_lines = [
                f"📊 选择账号: {len(selected_accounts)}个",
                f"✅ 提交成功: {success_count}个",
                f"❌ 提交失败: {len(selected_accounts) - success_count}个",
                "------------------",
                "💡 提示: 未授权账号无法提交"
            ]
            sender.reply(format_message("提交结果", result_lines))
        else:
            sender.reply("❌ 无效的选择")
            
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")

def authorize_multiple_accounts(phones):
    """授权多个账号"""
    # 获取配置信息
    (_, _, _, _, _, kyhVipmoney, kyhcoin,
     epay_pid, epay_key, epay_api) = get_user_content()
    
    account_infos = []
    # 获取账号信息
    for phone in phones:
        try:
            account_info_str = middleware.bucketGet('s_kyh_token', phone)
            if not account_info_str:
                continue
                
            account_info = json.loads(account_info_str)
            # 直接添加账号，不验证有效性
            account_infos.append({
                'phone': phone,
                'info': account_info
            })
        except Exception as e:
            sender.reply(f"""
⚠️ 账号处理异常:
📱 手机号: {mask_phone(phone)}
❌ 原因: {str(e)}""")
            
    if not account_infos:
        sender.reply("❌ 没有有效的账号可授权")
        return
        
    # 显示选择了多少个有效账号
    sender.reply(f"✅ 共有 {len(account_infos)} 个有效账号可授权")
    
    auth_menu = """
=====授权方式选择=====
[1] 微信支付
[2] 易支付
[3] 积分兑换
------------------
回复数字选择方式
回复"q"退出操作
=================="""
    sender.reply(auth_menu)
    
    pay_choice = sender.input(120000, 1, False)
    if not pay_choice or pay_choice.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return
        
    if pay_choice == '1':
        # 微信支付
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
                
            # 计算总价格 = 账号数 * 月数 * 单价
            total_money = len(account_infos) * months * kyhVipmoney
            
            # 处理支付
            if pay_order(project=f'看余杭授权(共{len(account_infos)}个账号)', months=months, money=total_money):
                # 处理每个账号的授权
                success_count = 0
                for account in account_infos:
                    try:
                        phone = account['phone']
                        account_info = account['info']
                        
                        # 处理授权
                        if process_authorization(phone, account_info, months):
                            success_count += 1
                    except Exception as e:
                        print(f"授权账号异常: {phone}, 错误: {str(e)}")
                
                # 显示授权结果
                success_msg = f"""
=====授权结果=====
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
------------------
⏰ 授权: {months}个月
------------------
💰 总金额: {total_money}元
=================="""
                sender.reply(success_msg)
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
    
    elif pay_choice == '2':
        # 易支付处理
        # 选择支付方式
        payment_menu = """
=====选择支付方式=====
[1] 支付宝
[2] 微信支付
[3] QQ钱包
------------------
回复数字选择支付方式
回复"q"退出操作
=================="""
        sender.reply(payment_menu)
        
        pay_type_choice = sender.input(120000, 1, False)
        if not pay_type_choice or pay_type_choice.lower() == 'q':
            sender.reply("✅ 已取消支付")
            return
            
        pay_type_map = {
            '1': 'alipay',
            '2': 'wxpay',
            '3': 'qqpay'
        }
        
        if pay_type_choice not in pay_type_map:
            sender.reply("❌ 无效的选择")
            return
            
        # 设置授权时长
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
                
            # 计算总价格 = 账号数 * 月数 * 单价
            total_money = len(account_infos) * months * kyhVipmoney
            
            # 创建易支付订单
            order_result = create_epay_order(userid, f'看余杭授权(共{len(account_infos)}个账号)', months, total_money, pay_type_map[pay_type_choice])
            
            if not order_result.get('success'):
                sender.reply(f"""
=====支付失败=====
❌ 创建订单失败
------------------
原因: {order_result.get('message', '未知错误')}
==================""")
                return
            
            # 获取订单信息并处理支付
            order_no = order_result.get('order_no')
            pay_url = order_result.get('pay_url')
            qrcode = order_result.get('qrcode')
            
            # 显示支付信息
            payment_info = f"""
=====易支付=====
🎫 商品: 看余杭授权(共{len(account_infos)}个账号)
📅 时长: {months}月
💰 金额: {total_money}元
------------------
🔗 订单号: {order_no}
"""
            # 使用iframe链接生成二维码
            if pay_url:
                iframe_url = generate_iframe_url(pay_url)
                qrcode_url = generate_qrcode(iframe_url)
                
                payment_info += f"""
请扫描二维码支付
------------------
正在查询支付结果...
=================="""
                sender.reply(payment_info)
                if qrcode_url:
                    sender.replyImage(qrcode_url)
                else:
                    sender.reply(f"🔗 支付链接: {pay_url}")
            else:
                payment_info += f"""
❌ 未获取到支付链接
------------------
请稍后重试
=================="""
                sender.reply(payment_info)
                return
            
            # 轮询订单状态
            paid = poll_order_status(order_no)
            
            if paid:
                sender.reply(f"""
=====支付成功=====
✅ 已确认支付
------------------
正在处理授权...
==================""")
                
                # 处理每个账号的授权
                success_count = 0
                for account in account_infos:
                    try:
                        phone = account['phone']
                        account_info = account['info']
                        
                        # 处理授权
                        if process_authorization(phone, account_info, months):
                            success_count += 1
                    except Exception as e:
                        print(f"授权账号异常: {phone}, 错误: {str(e)}")
                
                # 显示授权结果
                success_msg = f"""
=====授权结果=====
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
------------------
⏰ 授权: {months}个月
------------------
💰 总金额: {total_money}元
=================="""
                sender.reply(success_msg)
            else:
                sender.reply(f"""
=====支付超时=====
❌ 未检测到支付成功
------------------
请稍后重试，或联系管理员处理
订单号: {order_no}
==================""")
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
    
    elif pay_choice == '3':
        # 积分兑换处理
        if not kyhcoin or int(kyhcoin) <= 0:
            sender.reply("""
=====兑换失败=====
❌ 未配置积分价格
------------------
请联系管理员配置积分兑换功能
==================""")
            return
            
        # 设置授权时长
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
                
            # 计算需要的积分总数
            total_coins = int(kyhcoin) * months * len(account_infos)
            
            # 获取用户当前积分
            user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            
            if user_coins < total_coins:
                sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 当前积分: {user_coins}
🔢 需要积分: {total_coins}
🔍 差额: {total_coins - user_coins}
==================""")
                return
            
            # 扣除积分
            new_coins = user_coins - total_coins
            middleware.bucketSet('dd_sign_points', userid, str(new_coins))
            

            
            # 处理每个账号的授权
            success_count = 0
            for account in account_infos:
                try:
                    phone = account['phone']
                    account_info = account['info']
                    
                    # 处理授权
                    if process_authorization(phone, account_info, months):
                        success_count += 1
                except Exception as e:
                    print(f"授权账号异常: {phone}, 错误: {str(e)}")
            
            if success_count > 0:
                # 积分兑换成功通知
                sender.reply(f"""
=====积分兑换成功=====
✅ 已扣除积分: {total_coins}
💰 剩余积分: {new_coins}
------------------
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
            else:
                # 积分兑换失败，退还积分
                middleware.bucketSet('dd_sign_points', userid, str(user_coins))
                sender.reply(f"""
=====积分退还=====
⚠️ 授权处理失败，已退还积分
------------------
💰 当前积分: {user_coins}
==================""")
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
    else:
        sender.reply("❌ 无效的选择")

def show_tutorial():
    """显示看余杭教程"""
    tutorial_url = middleware.bucketGet('s_kyh_config', 'tutorial_url') or 'https://example.com/tutorial'
    
    tutorial = f"""
=====看余杭使用教程=====
🔍 基础功能:
1. 看余杭登录 - 绑定账号
2. 看余杭查询 - 查看账号信息
3. 看余杭管理 - 管理绑定账号
==================
⚠️ 注意事项:
• 账号失效请及时更新
• 请勿泄露账号信息
==================
💡 登录方式:
• 短信登录 - 通过短信验证码登录
• Token登录 - 格式: 备注#手机号#token#设备ID
==================
❓ 遇到问题请联系管理员
=================="""
    sender.reply(tutorial)

def kyh_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return
        
    auth_menu = f"""
=====看余杭授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 一键提交青龙
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(auth_menu)
    xz = sender.listen(60000)
    
    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出授权管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '3':
        # 一键提交青龙
        sender.reply("🔄 正在一键提交所有已授权账号到青龙...")
        
        # 获取所有授权账号
        auth_phones = middleware.bucketAllKeys('s_kyh_auth')
        if not auth_phones:
            sender.reply("""
=====提交失败=====
❌ 未找到任何已授权的看余杭账号
==================""")
            return
            
        success_count = 0
        fail_count = 0
        
        for phone in auth_phones:
            try:
                # 获取账号授权状态
                auth_date = middleware.bucketGet('s_kyh_auth', phone)
                
                # 验证是否是有效的授权日期
                if not auth_date or not auth_date.strip():
                    continue
                    
                # 检查授权是否已过期
                try:
                    auth_date_obj = datetime.strptime(auth_date, "%Y-%m-%d")
                    if auth_date_obj < datetime.now():
                        continue  # 已过期的授权跳过
                except ValueError:
                    continue  # 无效的日期格式
                
                # 获取账号token信息
                token_data = middleware.bucketGet('s_kyh_token', phone)
                if not token_data:
                    fail_count += 1
                    continue
                    
                # 解析账号信息
                account_info = json.loads(token_data)
                
                # 更新青龙变量
                if update_ql_env(phone, account_info):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception as e:
                fail_count += 1
                print(f"处理账号失败: {phone}, 错误: {str(e)}")
                
        result_msg = f"""
=====提交青龙完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
=================="""
        sender.reply(result_msg)
        return
    elif xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('s_kyh_user')
        if not users:
            sender.reply("""
=====授权失败=====
❌ 未找到任何绑定的看余杭账号
==================""")
            return
        
        # 统计总账号数
        total_accounts = 0
        for user in users:
            accountlist = middleware.bucketGet('s_kyh_user', user)
            if accountlist and accountlist != '{}':
                total_accounts += len(eval(accountlist))
            
        sender.reply(f"""
=====授权所有用户=====
👥 用户数: {len(users)}
📊 账号数: {total_accounts}
------------------
请输入授权天数:
(正数增加天数，负数减少天数)
回复"q"退出操作
==================""")
        
        sjts = sender.listen(60000)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("✅ 已取消授权")
            return
        elif sjts is None:
            sender.reply("⏰ 操作超时,已退出")
            return
        
        try:
            days = int(sjts)
            action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
            
            sender.reply(f"""
=====确认授权=====
👥 用户数: {len(users)}
📊 账号数: {total_accounts}
⏰ 操作: {action_text}
------------------
⚠️ 此操作影响所有用户
回复"y"确认
回复其他取消
==================""")
            
            confirm = sender.listen(60000)
            if not confirm or confirm.lower() != 'y':
                sender.reply("✅ 已取消授权")
                return
                
            success_count = 0
            fail_count = 0
            
            for user in users:
                accountlist = middleware.bucketGet('s_kyh_user', user)
                if accountlist == '' or accountlist == '{}':
                    continue
                    
                accounts = eval(accountlist)
                for phone in accounts:
                    try:
                        token_data = middleware.bucketGet('s_kyh_token', phone)
                        
                        if not token_data:
                            fail_count += 1
                            continue
                            
                        account_info = json.loads(token_data)
                        
                        # 计算新的授权时间
                        new_auth_time = calculate_auth_time_by_days(phone, days)
                        middleware.bucketSet('s_kyh_auth', phone, new_auth_time)
                        
                        # 更新青龙变量
                        if update_ql_env(phone, account_info):
                            success_count += 1
                        else:
                            fail_count += 1
                            print(f"更新青龙变量失败: {phone}")
                    except Exception as e:
                        fail_count += 1
                        print(f"处理账号失败: {phone}, 错误: {str(e)}")
                        
            result_msg = f"""
=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 操作: {action_text}
=================="""
            sender.reply(result_msg)
            
        except ValueError:
            sender.reply("❌ 天数必须是数字!")
            return
            
    elif xz == '2':
        # 单独授权用户
        user_guide = f"""
======账号授权======
请输入需要授权的账号ID
(发送myuid可获取ID)
------------------
回复"q"退出操作
=================="""
        sender.reply(user_guide)
        
        myuid = sender.listen(60000)
        if myuid == 'q' or myuid == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif myuid is None:
            sender.reply("⏰ 操作超时,已退出")
            return
            
        accountlist = middleware.bucketGet('s_kyh_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"❌ 未找到 {myuid} 的看余杭账号信息!")
            return
            
        accounts = eval(accountlist)
        account_list = """
========选择账号=======
[0] 全部账号"""
        
        for i, phone in enumerate(accounts, 1):
            accountVip = middleware.bucketGet('s_kyh_auth', phone)
            vip_status = accountVip if accountVip else '未授权'
            account_list += f"""
[{i}]{mask_phone(phone)}({vip_status})"""
            
        account_list += """
=====================
回复数字选择账号
回复'q'退出
====================="""
        sender.reply(account_list)
        
        xz = sender.listen(60000)
        if xz == 'q' or xz == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif xz is None:
            sender.reply("⏰ 操作超时,已退出")
            return
            
        auth_guide = """
=====设置授权时长=====
请输入要授权的天数
(正数增加天数，负数减少天数)
------------------
回复数字设置天数
回复"q"退出操作
=================="""
        sender.reply(auth_guide)
        
        if xz == '0':
            # 授权该用户的所有账号
            sjts = sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                days = int(sjts)
                action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
                    
                success_count = 0
                for phone in accounts:
                    try:
                        token_data = middleware.bucketGet('s_kyh_token', phone)
                        
                        if not token_data:
                            continue
                            
                        account_info = json.loads(token_data)
                        
                        # 计算新的授权时间
                        new_auth_time = calculate_auth_time_by_days(phone, days)
                        middleware.bucketSet('s_kyh_auth', phone, new_auth_time)
                        
                        # 更新青龙变量
                        if update_ql_env(phone, account_info):
                            success_count += 1
                        else:
                            print(f"更新青龙变量失败: {phone}")
                    except Exception as e:
                        print(f"处理账号失败: {phone}, 错误: {str(e)}")
                        
                result_msg = f"""
=====授权操作完成=====
✅ 成功授权: {success_count}个账号
⏰ 操作: {action_text}
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return
                
        elif 1 <= int(xz) <= len(accounts):
            # 授权单个账号
            phone = accounts[int(xz)-1]
            sjts = sender.listen(60000)
            
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                days = int(sjts)
                action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
                    
                token_data = middleware.bucketGet('s_kyh_token', phone)
                
                if not token_data:
                    sender.reply("❌ 未找到账号token信息!")
                    return
                    
                account_info = json.loads(token_data)
                
                # 计算新的授权时间
                new_auth_time = calculate_auth_time_by_days(phone, days)
                middleware.bucketSet('s_kyh_auth', phone, new_auth_time)
                
                # 更新青龙变量
                ql_result = update_ql_env(phone, account_info)
                
                result_msg = f"""
=====授权成功=====
📱 手机号: {mask_phone(phone)}
⏰ 操作: {action_text}
📅 到期时间: {new_auth_time}
------------------
🔄 青龙同步: {'成功' if ql_result else '失败'}
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return
        else:
            sender.reply("❌ 输入的序号无效!")
            return

def check_order(order_id):
    """查询订单状态"""
    data = middleware.bucketGet('s_kyh_order', order_id)
    if not data:
        return '订单不存在'
        
    try:
        data = json.loads(data)
        status = {
            'pending': '待支付',
            'success': '已完成',
            'failed': '已取消'
        }.get(data['status'], '未知')
        
        msg = f"""
=====订单详情=====
📝 订单号: {order_id}
💰 金额: {data['amount']}元
⏰ 时长: {data['months']}月
📊 状态: {status}"""
        
        if data['status'] == 'success':
            msg += f"""
💵 实付: {data.get('paid_amount', 0)}元
⌚ 支付时间: {data.get('pay_time', '')}"""
            
        return msg
        
    except:
        return '查询失败'

def login_with_sms():
    """使用短信验证码登录看余杭"""
    phone_guide_lines = [
        "请输入手机号码",
        "------------------",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("短信登录", phone_guide_lines))
    
    phone = sender.input(120000, 1, False)
    if not phone or phone.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return None
        
    # 验证手机号格式
    if not phone.isdigit() or len(phone) != 11:
        sender.reply("❌ 手机号格式错误，请输入11位数字")
        return None
    
    # 生成设备标识
    device_id = generate_random_id()
    
    # 发送短信验证码
    try:
        # 构建发送验证码请求
        timestamp = str(int(time.time() * 1000))
        trace_id = f"SMS{timestamp}"
        send_code_data = {
            "traceId": trace_id,
            "data": {
                "mobilePhone": phone
            },
            "service": "core",
            "userDevice": {
                "os": "9",
                "deviceBrand": "samsung",
                "deviceId": device_id,
                "equipmentId": device_id,
                "deviceType": "Samsung SM-N9760",
                "device": "android",
                "clientVersion": "5.1.0"
            },
            "api": "v2/login/sendLoginCode",
            "token": ""
        }
        
        headers = {
            "Connection": "Keep-Alive",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "*/*",
            "Accept-Language": "zh-cn",
            "Host": "app.eyh.cn",
            "Referer": "https://app.eyh.cn/gateway/api",
            "User-Agent": "okhttp/5.0.0-alpha.2"
        }
        
        response = requests.post(base_url, headers=headers, json=send_code_data)
        result = response.json()
        
        if result.get("code") != "0":
            sender.reply(f"❌ 发送验证码失败: {result.get('message', '未知错误')}")
            return None
            
        serial_num = result.get("data")
        code_sent_lines = [
            f"📱 手机号: {mask_phone(phone)}",
            "✅ 发送成功",
            "------------------",
            "请输入接收到的验证码:"
        ]
        sender.reply(format_message("验证码已发送", code_sent_lines))
        
        # 获取用户输入的验证码
        code = sender.input(300000, 1, False)  # 5分钟超时
        if not code:
            sender.reply("⏰ 验证码输入超时，已取消登录")
            return None
            
        # 验证码登录请求
        timestamp = str(int(time.time() * 1000))
        trace_id = f"LOGIN{timestamp}"
        login_data = {
            "traceId": trace_id,
            "data": {
                "serialNum": serial_num,
                "code": code
            },
            "service": "core",
            "userDevice": {
                "os": "9",
                "deviceBrand": "samsung",
                "deviceId": device_id,
                "equipmentId": device_id,
                "deviceType": "Samsung SM-N9760",
                "device": "android",
                "clientVersion": "5.1.0"
            },
            "api": "v2/login/codeLogin",
            "token": ""
        }
        
        login_response = requests.post(base_url, headers=headers, json=login_data)
        login_result = login_response.json()
        
        if login_result.get("code") != "0":
            sender.reply(f"❌ 登录失败: {login_result.get('message', '验证码错误或已过期')}")
            return None
            
        token = login_result.get("data", "")
        
        # 获取用户信息和uid
        task_result = get_task_list(token, device_id)
        
        if task_result.get("success"):
            task_data = task_result.get("data", {})
            uid = task_data.get("lotteryActivityUid", "")
            username = task_data.get("userName", "")
            
            # 获取用户其他信息
            user_info = verify_token(token, device_id)
            if user_info.get("success"):
                user_data = user_info.get("data", {})
                if not username:
                    username = user_data.get("nickname", "")
            
            # 返回账号信息字典
            return {
                "remark": username or phone,
                "phone": phone,
                "token": token,
                "uid": uid,
                "device_id": device_id,
                "nickname": username
            }
        else:
            sender.reply(f"❌ 获取用户信息失败: {task_result.get('message', '未知错误')}")
            return None
    except Exception as e:
        sender.reply(f"❌ 登录异常: {str(e)}")
        return None

def login_with_token():
    """使用token登录"""
    token_guide_lines = [
        "请输入看余杭账号信息",
        "格式: 备注#手机号#token#设备ID",
        "------------------",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("Token登录", token_guide_lines))
    
    user_input = sender.input(120000, 1, False)
    if not user_input or user_input.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return None
        
    try:
        # 解析输入
        parts = user_input.split('#')
        if len(parts) < 3:
            sender.reply(show_error("格式错误", "输入格式不正确", "正确格式: 备注#手机号#token#设备ID"))
            return None
            
        remark = parts[0].strip()
        phone = parts[1].strip()
        token = parts[2].strip()
        device_id = parts[3].strip() if len(parts) > 3 else generate_random_id()
        
        # 验证手机号格式
        if not phone.isdigit() or len(phone) != 11:
            sender.reply("❌ 手机号格式错误，请输入11位数字")
            return None
            
        # 验证token有效性
        result = verify_token(token, device_id)
        
        if not result.get('success'):
            sender.reply(show_error("验证失败", "Token验证失败", f"原因: {result.get('message', '未知错误')}"))
            return None
            
        # 获取用户信息
        user_data = result.get('data', {})
        uid = user_data.get('uid', '')
        nickname = user_data.get('nickname', '')
        avatar = user_data.get('avatar', '')
        
        # 返回账号信息字典
        return {
            "remark": remark,
            "phone": phone,
            "token": token,
            "uid": uid,
            "device_id": device_id,
            "nickname": nickname,
            "avatar": avatar
        }
        
    except Exception as e:
        sender.reply(show_error("登录异常", "登录过程发生错误", f"错误: {str(e)}"))
        return None

def bind_account():
    """绑定看余杭账号"""
    # 显示登录方式选择菜单
    login_menu_lines = [
        "[1] 短信验证码登录",
        "[2] Token登录",
        "------------------",
        "回复数字选择登录方式",
        "回复\"q\"退出操作"
    ]
    sender.reply(format_message("看余杭登录", login_menu_lines))
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
        
    account_info = None
    remark = None
    
    if choice == '1':
        # 短信验证码登录
        account_info = login_with_sms()
        if not account_info:
            return
            
        # 如果是短信登录，需要单独设置备注
        remark_lines = [
            "请为当前账号设置一个备注名",
            "------------------",
            "回复备注名称",
            "回复\"q\"退出操作"
        ]
        sender.reply(format_message("设置备注", remark_lines))
        
        remark = sender.input(120000, 1, False)
        if not remark or remark.lower() == 'q':
            sender.reply("✅ 已取消设置备注，将使用手机号作为备注")
            remark = account_info.get('phone')
        
        # 添加备注信息
        account_info['remark'] = remark
        
    elif choice == '2':
        # Token登录
        account_info = login_with_token()
        if not account_info:
            return
    else:
        sender.reply("❌ 无效的选择")
        return
        
    # 保存账号信息
    phone = account_info.get('phone')
    
    # 更新用户账号列表
    if not uservalue:
        middleware.bucketSet('s_kyh_user', userid, str([phone]))
    else:
        accounts = eval(uservalue)
        if phone not in accounts:
            accounts.append(phone)
            middleware.bucketSet('s_kyh_user', userid, str(accounts))
            
    # 保存账号详细信息
    middleware.bucketSet('s_kyh_token', phone, json.dumps(account_info))
    
    success_lines = [
        f"👤 备注: {account_info.get('remark')}",
        f"📱 手机号: {mask_phone(phone)}",
        f"🆔 用户ID: {account_info.get('uid')}"
    ]
    sender.reply(format_message("绑定成功", success_lines))
    
    # 检查账号是否已授权，如果已授权且未过期则直接更新青龙变量
    dqsj = datetime.now().strftime("%Y-%m-%d")
    accountVip = middleware.bucketGet('s_kyh_auth', phone)
    
    if accountVip and accountVip > dqsj:
        # 账号已授权且未过期，直接更新青龙变量
        ql_result = update_ql_env(phone, account_info)
        auth_result = f"""
=====账号已授权=====
📱 手机号: {mask_phone(phone)}
👤 备注: {account_info.get('remark', '未设置')}
📅 到期时间: {accountVip}
------------------
🔄 青龙更新: {'成功' if ql_result else '失败'}
=================="""
        sender.reply(auth_result)
    else:
        # 账号未授权或已过期，进入授权流程
        authorize_account(phone, account_info)

def calculate_auth_time_by_days(phone, days):
    """按天数计算授权时间
    Args:
        phone: 手机号
        days: 天数（正数增加，负数减少）
    Returns:
        新的授权到期日期字符串
    """
    try:
        current_auth = middleware.bucketGet('s_kyh_auth', phone)
        
        if current_auth and datetime.strptime(current_auth, "%Y-%m-%d").date() > datetime.now().date():
            base_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
        else:
            base_date = datetime.now().date()
        
        new_date = base_date + timedelta(days=int(days))
        return str(new_date)
        
    except Exception as e:
        raise Exception(f"计算授权时间失败: {str(e)}")

def process_authorization(phone, account_info, months):
    """处理账号授权"""
    try:
        # 获取当前授权状态
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_kyh_auth', phone)
        
        # 计算新的到期时间
        if accountVip and accountVip > dqsj:
            # 如果当前已有有效授权，从授权到期时间开始计算
            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
        else:
            # 如果没有有效授权，从当前时间开始计算
            start_date = datetime.now()
            
        # 计算新的到期时间(按月计算，每月30天)
        new_expire = start_date + timedelta(days=30*months)
        new_expire_str = new_expire.strftime("%Y-%m-%d")
        
        # 更新授权时间
        middleware.bucketSet('s_kyh_auth', phone, new_expire_str)
        
        # 更新青龙变量
        ql_result = update_ql_env(phone, account_info)
        
        # 显示授权结果
        auth_result = f"""
=====授权成功=====
📱 手机号: {mask_phone(phone)}
👤 备注: {account_info.get('remark', '未设置')}
⏰ 授权时长: {months}个月
📅 到期时间: {new_expire_str}
------------------
🔄 青龙更新: {'成功' if ql_result else '失败'}
=================="""
        sender.reply(auth_result)
        return True
    except Exception as e:
        sender.reply(f"""
=====授权失败=====
📱 手机号: {mask_phone(phone)}
❌ 错误: {str(e)}
==================""")
        return False

def process_epay_payment(phone, account_info, months, money, pay_type):
    """处理易支付支付流程"""
    try:
        # 创建易支付订单
        order_result = create_epay_order(userid, '看余杭授权', months, money, pay_type)
        
        if not order_result.get('success'):
            sender.reply(f"""
=====支付失败=====
❌ 创建订单失败
------------------
原因: {order_result.get('message', '未知错误')}
==================""")
            return False
        
        # 获取订单信息
        order_no = order_result.get('order_no')
        pay_url = order_result.get('pay_url')
        qrcode = order_result.get('qrcode')
        
        # 显示支付信息
        payment_info = f"""
=====易支付=====
🎫 商品: 看余杭授权
📅 时长: {months}月
💰 金额: {money}元
------------------
🔗 订单号: {order_no}
"""
        # 使用iframe链接生成二维码
        if pay_url:
            iframe_url = generate_iframe_url(pay_url)
            qrcode_url = generate_qrcode(iframe_url)
            
            payment_info += f"""
请扫描二维码支付
------------------
正在查询支付结果...
=================="""
            sender.reply(payment_info)
            if qrcode_url:
                sender.replyImage(qrcode_url)
            else:
                sender.reply(f"🔗 支付链接: {pay_url}")
        else:
            payment_info += f"""
❌ 未获取到支付链接
------------------
请稍后重试
=================="""
            sender.reply(payment_info)
            return False
        
        # 轮询订单状态
        paid = poll_order_status(order_no)
        
        if paid:
            sender.reply(f"""
=====支付成功=====
✅ 已确认支付
------------------
正在处理授权...
==================""")
            # 处理授权
            return process_authorization(phone, account_info, months)
        else:
            sender.reply(f"""
=====支付超时=====
❌ 未检测到支付成功
------------------
请稍后重试，或联系管理员处理
订单号: {order_no}
==================""")
            return False
    except Exception as e:
        sender.reply(f"""
=====支付异常=====
❌ 处理支付过程出错
------------------
错误: {str(e)}
==================""")
        return False

def process_coin_exchange(phone, account_info, months, coin_price):
    """处理积分兑换授权"""
    try:
        if not coin_price or int(coin_price) <= 0:
            sender.reply(f"""
=====兑换失败=====
❌ 未配置积分价格
------------------
请联系管理员配置积分兑换功能
==================""")
            return False
        
        # 计算需要的积分总数
        total_coins = int(coin_price) * months
        
        # 获取用户当前积分
        user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
        
        if user_coins < total_coins:
            sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 当前积分: {user_coins}
🔢 需要积分: {total_coins}
🔍 差额: {total_coins - user_coins}
==================""")
            return False
        
        # 扣除积分
        new_coins = user_coins - total_coins
        middleware.bucketSet('dd_sign_points', userid, str(new_coins))
        # 处理授权
        success = process_authorization(phone, account_info, months)
        
        if success:
            # 积分兑换成功通知
            sender.reply(f"""
=====积分兑换成功=====
✅ 已扣除积分: {total_coins}
💰 剩余积分: {new_coins}
------------------
授权已处理完成
==================""")
            return True
        else:
            # 积分兑换失败，退还积分
            middleware.bucketSet('dd_sign_points', userid, str(user_coins))
            sender.reply(f"""
=====积分退还=====
⚠️ 授权处理失败，已退还积分
------------------
💰 当前积分: {user_coins}
==================""")
            return False
    except Exception as e:
        sender.reply(f"""
=====兑换异常=====
❌ 积分兑换过程出错
------------------
错误: {str(e)}
==================""")
        return False

# 添加中奖记录状态映射表
def get_award_status(status):
    """根据状态码返回状态描述"""
    status_map = {
        0: "未领取",
        1: "待领取",
        2: "已领取",
        3: "已过期"
    }
    return status_map.get(status, f"未知状态({status})")

# 添加格式化消息的工具函数
def format_message(title, content_lines, footer="=================="):
    """
    格式化消息，统一处理消息格式
    title: 消息标题
    content_lines: 消息内容行的列表
    footer: 消息底部分隔线
    """
    message = f"""
====={title}=====
"""
    for line in content_lines:
        message += f"{line}\n"
    
    message += footer
    return message

def show_error(title, error_msg, extra_info=None):
    """显示统一格式的错误消息"""
    content = [f"❌ {error_msg}"]
    if extra_info:
        content.append("------------------")
        if isinstance(extra_info, list):
            content.extend(extra_info)
        else:
            content.append(extra_info)
    
    return format_message(title, content)

# 统一API请求函数
def api_request(api_path, token, device_id, data=None, service="media"):
    """
    统一的API请求函数
    api_path: API路径
    token: 用户token
    device_id: 设备ID
    data: 请求数据，默认为None
    service: 服务类型，默认为media
    """
    try:
        timestamp = str(int(time.time() * 1000))
        trace_id = f"{random_str(6).upper()}{timestamp}"
        
        request_data = {
            "traceId": trace_id,
            "service": service,
            "userDevice": {
                "os": "9",
                "deviceBrand": "samsung",
                "deviceId": device_id,
                "equipmentId": device_id,
                "deviceType": "Samsung SM-N9760",
                "device": "android",
                "clientVersion": "5.1.0"
            },
            "api": api_path,
            "token": token
        }
        
        # 添加自定义数据
        if data:
            request_data["data"] = data
            
        headers = {
            "Connection": "Keep-Alive",
            "Content-Type": "application/json; charset=utf-8",
            "Accept": "*/*",
            "Accept-Language": "zh-cn",
            "Host": "app.eyh.cn",
            "Referer": "https://app.eyh.cn/gateway/api",
            "User-Agent": "okhttp/5.0.0-alpha.2"
        }
        
        response = requests.post(base_url, headers=headers, json=request_data)
        result = response.json()
        
        if result.get("code") == "0":
            return {
                "success": True,
                "data": result.get("data", {})
            }
        else:
            return {
                "success": False,
                "message": result.get("message", "请求失败")
            }
    except Exception as e:
        print(f"API请求异常: {str(e)}")
        return {
            "success": False,
            "message": str(e)
        }

def get_ql_config():
    """获取青龙配置信息"""
    try:
        qlconfig = middleware.bucketGet('s_kyh_config', 'kyh_qlname')
        if not qlconfig:
            return {"code": 400, "msg": "未配置青龙信息", "data": None}
            
        # 将英文的"|"替换为中文的"丨"
        qlconfig = qlconfig.replace('|', '丨')
        configs = qlconfig.split('丨')
        if len(configs) < 3:
            return {"code": 400, "msg": "青龙配置格式错误", "data": None}
            
        return {
            "code": 200,
            "msg": "获取成功",
            "data": {
                "url": configs[0].strip(),
                "client_id": configs[1].strip(),
                "client_secret": configs[2].strip()
            }
        }
    except Exception as e:
        return {"code": 500, "msg": f"获取青龙配置发生异常: {str(e)}", "data": None}

def check_auth_status():
    """检测授权状态并推送通知
    逻辑：到期时间-当前日期 > 提前天数，不推送
          到期时间-当前日期 <= 提前天数 且 > 0，推送提醒
          到期时间-当前日期 <= 0，清理账号
    """
    notify = middleware.bucketGet('s_kyh_config', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"
    
    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_kyh_user')
    if not all_users:
        return "❌ 没有用户"
    
    # 获取提前提醒天数配置，默认3天
    notify_days = int(middleware.bucketGet('s_kyh_config', 'notify_days') or '3')
    
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0
    
    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_kyh_user', user_id) or '[]')
            
            # 分类账号：需要提醒的和需要清理的
            to_notify = []  # 需要提醒的账号
            to_clean = []   # 需要清理的账号
            
            for phone in accounts:
                auth_time_str = middleware.bucketGet('s_kyh_auth', phone)
                token_info_str = middleware.bucketGet('s_kyh_token', phone)
                remark = phone
                if token_info_str:
                    try:
                        token_info = json.loads(token_info_str)
                        remark = token_info.get('remark', phone)
                    except:
                        pass
                
                if not auth_time_str:
                    # 未授权，直接清理
                    to_clean.append({'phone': phone, 'remark': remark, 'auth_time': '未授权', 'days_left': 0})
                    continue
                
                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days
                    
                    if days_left <= 0:
                        # 已过期，清理
                        to_clean.append({'phone': phone, 'remark': remark, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        # 即将过期，提醒
                        to_notify.append({'phone': phone, 'remark': remark, 'auth_time': auth_time_str, 'days_left': days_left})
                    # days_left > notify_days 不做任何操作
                except:
                    # 日期格式错误，清理
                    to_clean.append({'phone': phone, 'remark': remark, 'auth_time': auth_time_str, 'days_left': 0})
            
            total += len(accounts)
            
            # 处理需要清理的账号
            if to_clean:
                for acc in to_clean:
                    phone = acc['phone']
                    delete_ql_env(phone)
                    middleware.bucketDel('s_kyh_token', phone)
                    
                    if phone in accounts:
                        accounts.remove(phone)
                    
                    middleware.bucketDel('s_kyh_auth', phone)
                    cleaned += 1
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet('s_kyh_user', user_id, str(accounts))
                else:
                    middleware.bucketDel('s_kyh_user', user_id)
            
            # 处理需要提醒的账号
            if to_notify:
                notify_list = "\n".join([
                    f"📱 {a['remark']}({mask_phone(a['phone'])}) 剩余{a['days_left']}天({a['auth_time']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====看余杭账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"看余杭管理\"续费\n"
                    f"=================="
                )
                for ch in channels:
                    try:
                        middleware.push(
                            imType=ch,
                            groupCode='',
                            userID=user_id,
                            title="",
                            content=msg
                        )
                        notified += 1
                    except:
                        pass
        except:
            pass
    
    return f"✅ 看余杭检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"

def main():
    # 获取必要的配置
    (_, _, randommanagecommand, randomquerycommand,
     randomsigncommand, kyhVipmoney, kyhcoin, _, _, _) = get_user_content()
    
    imtype = sender.getImtype()
    usermessage = sender.getMessage()
    
    # 定时任务 - 执行检测并清理过期账号
    if imtype == 'fake':
        try:
            middleware.notifyMasters(check_auth_status())
        except:
            pass
        return
    
    if '登录' in usermessage or '登陆' in usermessage:
        bind_account()
    elif '管理' in usermessage:
        manage_account()
    elif '查询' in usermessage:
        query_accounts()
    elif '看余杭教程' in usermessage:
        show_tutorial()
    elif '看余杭授权' in usermessage:
        kyh_auth()
    elif '看余杭检测' in usermessage:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    elif usermessage.startswith('KYH_'):  # 查询订单
        msg = check_order(usermessage)
        sender.reply(msg)
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()

