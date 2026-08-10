# [rule: ^(看余杭)(登录|登陆)$|^登(录|陆)(看余杭)$|^(看余杭)(查询|管理)$|^(查询|管理)(看余杭)$|^清理看余杭$|^看余杭授权$]
# [disable:false]
# [platform: qq,wx]
#[icon: https://www.helloimg.com/i/2025/02/03/67a06719bd58f.jpg]
# [cron: 0 0 * * *]  # 每天0点运行
# [public: true]:是否上架
# [open_source: false]是否开源
# [title: 看余杭]
# [version: 1.9]
# [price: 5.88]
# [author: Lies]
# [service: 订阅公告]
#[description: 看余杭插件，支持短信跟Token登录<br>管理、查询、授权等功能（支持呆呆市场积分授权）<br>相关指令有看余杭登录/登陆/查询/管理/授权/清理看余杭<br>由流云集团附属集团开发，维护能力有限，<br>更新:  修复未授权提交青龙，优化<br>        账号交青龙禁用启用逻辑<br>更新:  修复未登录查询异常bug<br>更新:  修复未登录管理异常<br>更新:  修复0积分开通授权异常<br>更新:  修复用户积分过大导致的计算问题<br>更新:  优化支付处理逻辑<br>更新:  优化了一些已知问题<br>更新:  优化了一些已知问题2/26/22:20<br>相关脚本链接：[看余杭交流学习文件.py](https://www.123865.com/s/WgTSVv-8SvAh)<br><img src="https://www.helloimg.com/i/2025/02/03/67a0593d758e1.jpg" alt="看余杭插件图片1" style="max-width:300px;" /><img src="https://www.helloimg.com/i/2025/02/03/67a0593daf853.jpg" alt="看余杭插件图片2" style="max-width:300px;" />]
import re#处理正则表达式
from datetime import datetime, timedelta#操作日期、时间以及时间间隔
import middleware #autman的中间件
import urllib.parse #处理url编码
from decimal import Decimal#处理浮点数
import requests#处理http请求
import time#处理时间
import json#处理json数据
import hashlib#处理哈希值
import uuid#生成唯一ID
import asyncio
import aiohttp
from functools import lru_cache
import decimal

# 获取发送者信息
senderID = middleware.getSenderID()#获取发送者QQ号
sender = middleware.Sender(senderID)#获取发送者对象
userid = sender.getUserID()#存储当前发送者的用户 ID，与 senderID 类似，但通常用于内部标识
uservalue = middleware.bucketGet(bucket='kangyh_user', key=userid)

# [param: {"required":true,"key":"kangyh.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"kangyh.ql_host","bool":false,"placeholder":"必填项,http://ql.example.com","name":"青龙地址","desc":"青龙面板的访问地址"}]
# [param: {"required":true,"key":"kangyh.ql_client_id","bool":false,"placeholder":"必填项,client_id","name":"青龙应用ID","desc":"青龙面板的应用ID"}]
# [param: {"required":true,"key":"kangyh.ql_client_secret","bool":false,"placeholder":"必填项,client_secret","name":"青龙应用秘钥","desc":"青龙面板的应用秘钥"}]
# [param: {"required":true,"key":"kangyh.var_name","bool":false,"placeholder":"必填项,例:Look_at_Yuhang","name":"青龙变量名","desc":"提交到青龙的变量名"}]
# [param: {"required":true,"key":"kangyh.price","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"kangyh.coin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分"}]

def get_config():
    """获取插件配置"""
    try:
        # 获取基本配置
        var_name = middleware.bucketGet('kangyh', 'var_name')
        if not var_name:
            print("未配置变量名，使用默认值: Look_at_Yuhang")
            var_name = 'Look_at_Yuhang'
            middleware.bucketSet('kangyh', 'var_name', var_name)
        
        # 获取青龙配置
        ql_host = middleware.bucketGet('kangyh', 'ql_host')
        ql_client_id = middleware.bucketGet('kangyh', 'ql_client_id')
        ql_client_secret = middleware.bucketGet('kangyh', 'ql_client_secret')
        
        # 验证青龙配置
        if not all([ql_host, ql_client_id, ql_client_secret]):
            raise Exception("青龙配置不完整，请检查配置")
        
        # 获取命令配置
        manage_cmd = middleware.bucketGet('kangyh', 'manage_cmd') or '看余杭管理'
        query_cmd = middleware.bucketGet('kangyh', 'query_cmd') or '看余杭查询'
        login_cmd = middleware.bucketGet('kangyh', 'login_cmd') or '看余杭登录'
        
        # 获取价格配置
        try:
            price = Decimal(middleware.bucketGet('kangyh', 'price') or '1')
            if price < 0:
                raise ValueError("价格不能为负数")
        except (ValueError, decimal.InvalidOperation):
            print("价格配置无效，使用默认值: 1")
            price = Decimal('1')
            middleware.bucketSet('kangyh', 'price', '1')
        
        # 获取积分配置
        try:
            coin_price = int(middleware.bucketGet('kangyh', 'coin') or '0')
            if coin_price < 0:
                raise ValueError("积分不能为负数")
        except ValueError:
            print("积分配置无效，使用默认值: 0")
            coin_price = 0
            middleware.bucketSet('kangyh', 'coin', '0')
        
        return (var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price)
        
    except Exception as e:
        error_msg = f"获取配置失败: {str(e)}"
        print(error_msg)
        sender.reply(f"❌ {error_msg}")
        raise

def init_qinglong():
    """初始化青龙连接"""
    try:
        # 从配置中读取青龙信息
        ql_host = middleware.bucketGet('kangyh', 'ql_host') or ''
        ql_client_id = middleware.bucketGet('kangyh', 'ql_client_id') or ''
        ql_client_secret = middleware.bucketGet('kangyh', 'ql_client_secret') or ''
        
        if not ql_host or not ql_client_id or not ql_client_secret:
            sender.reply("❌ 未配置完整的青龙信息")
            exit(0)
            
        # 检查青龙地址是否以 / 结尾，如果没有则自动添加
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
        # 确保URL以 / 结尾
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

def add_to_qinglong(token, account, mobile):
    """添加变量到青龙"""
    try:
        url = f"{ql_url}/open/envs"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        
        # 检查是否已存在
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception("获取变量失败")
        
        try:
            response_data = response.json()
            if not isinstance(response_data, dict) or 'data' not in response_data:
                raise Exception("青龙返回数据格式错误")
            envs_data = response_data['data']
            if not isinstance(envs_data, list):
                raise Exception("青龙环境变量数据格式错误")
        except json.JSONDecodeError:
            raise Exception("解析青龙返回数据失败")
        
        exists_id = None
        for env in envs_data:
            if isinstance(env, dict) and env.get('name') == var_name and account in env.get('remarks', ''):
                exists_id = env.get('id')
                break

        # 构建备注信息
        if len(token) == 32:  # 标准token长度为32位
            remarks = f"账号:{account}丨用户:{userid}丨Token:{token[:6]}...{token[-6:]}"
        else:
            remarks = f"账号:{account}丨用户:{userid}丨手机:{mobile}"
        
        # 构建变量数据
        data = {
            "name": var_name,
            "value": token,
            "remarks": remarks
        }
        
        new_env_ids = []
        if exists_id:
            # 更新已存在的变量
            data['id'] = exists_id
            response = requests.put(url, headers=headers, json=data)
            if response.status_code == 200:
                new_env_ids.append(exists_id)
                print(f"更新变量成功: {var_name}")
        else:
            # 添加新变量
            response = requests.post(url, headers=headers, json=[data])
            if response.status_code == 200:
                try:
                    resp_data = response.json()
                    if isinstance(resp_data, dict) and isinstance(resp_data.get('data'), list):
                        for env_item in resp_data['data']:
                            if isinstance(env_item, dict) and 'id' in env_item:
                                new_env_ids.append(env_item['id'])
                                print(f"添加变量成功: {var_name}")
                except Exception as e:
                    print(f"解析新增变量响应失败: {str(e)}")
        
        if response.status_code != 200:
            raise Exception(f"提交变量失败: HTTP {response.status_code}")
            
        # 保存环境变量ID到数据桶
        if new_env_ids:
            middleware.bucketSet('kangyh_env_id', account, json.dumps(new_env_ids))
            print(f"保存环境变量ID成功: {new_env_ids}")
        
        return True
        
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
            if env['name'] == var_name and account in env.get('remarks', ''):
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

def login():
    """登录实现"""
    login_guide = """
=====登录方式=====
[1] 验证码登录
[2] Token登录
------------------
回复数字选择方式
回复"q"退出"""

    sender.reply(login_guide)
    choice = sender.listen(60000)
    
    if not choice:
        sender.reply("❌ 操作超时")
        return
    elif choice == 'q':
        sender.reply("✅ 已取消登录")
        return
        
    try:
        if choice == '1':
            return code_login()
        elif choice == '2':
            return token_login()
        else:
            sender.reply("❌ 无效的选择")
            return
            
    except Exception as e:
        sender.reply(f"❌ 登录失败: {str(e)}")
        return

def code_login():
    """验证码登录实现"""
    try:
        # 获取手机号
        sender.reply("请输入手机号:")
        mobile = sender.listen(60000)
        
        if not mobile:
            sender.reply("❌ 操作超时")
            return
        elif mobile == 'q':
            sender.reply("✅ 已取消登录")
            return
            
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            raise Exception("无效的手机号")
            
        # 构造发送验证码请求
        send_data = {
            "traceId": f"G9OBF59J{int(time.time()*1000)}",
            "data": {
                "mobilePhone": mobile
            },
            "service": "core",
            "userDevice": {
                "os": "14",
                "deviceBrand": "Redmi",
                "deviceId": "13666addccf39a5c",
                "equipmentId": "13666addccf39a5c", 
                "deviceType": "Xiaomi Redmi K30 Pro Zoom Edition",
                "device": "android",
                "clientVersion": "5.2.3",
                "gtCid": ""
            },
            "api": "v2/login/sendLoginCode",
            "token": ""
        }
        
        # 发送验证码
        response = requests.post(
            "https://app.eyh.cn/gateway/api",
            json=send_data,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
        if response.status_code != 200:
            raise Exception("发送验证码失败")
            
        result = response.json()
        if result['code'] != "0":
            raise Exception(f"发送验证码失败: {result['message']}")
            
        serial_num = result['data']
        
        # 获取验证码
        sender.reply("请输入收到的验证码:")
        code = sender.listen(60000)
        
        if not code:
            sender.reply("❌ 操作超时")
            return
        elif code == 'q':
            sender.reply("✅ 已取消登录")
            return
            
        if not code.isdigit():
            raise Exception("无效的验证码")
            
        # 构造验证码登录请求
        login_data = {
            "traceId": f"EAROJV8N{int(time.time()*1000)}",
            "data": {
                "serialNum": serial_num,
                "code": code
            },
            "service": "core",
            "userDevice": {
                "os": "14",
                "deviceBrand": "Redmi",
                "deviceId": "13666addccf39a5c",
                "equipmentId": "13666addccf39a5c",
                "deviceType": "Xiaomi Redmi K30 Pro Zoom Edition",
                "device": "android",
                "clientVersion": "5.2.3",
                "gtCid": ""
            },
            "api": "v2/login/codeLogin",
            "token": ""
        }
        
        # 验证码登录
        response = requests.post(
            "https://app.eyh.cn/gateway/api",
            json=login_data,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
        
        if response.status_code != 200:
            raise Exception("登录失败")
            
        result = response.json()
        if result['code'] != "0":
            raise Exception(f"登录失败: {result['message']}")
            
        token = result['data']
        return process_login(token, mobile, mobile)
        
    except Exception as e:
        raise Exception(f"验证码登录失败: {str(e)}")

def token_login():
    """Token登录实现"""
    token_guide = """
=====看余杭Token登录=====
请在一分钟内输入Token字符串
示例: 08adb1b15e5492381cb6d900
a416407b
=======================
回复"q"退出"""

    sender.reply(token_guide)
    token = sender.listen(60000)
    
    if not token:
        sender.reply("❌ 操作超时")
        return
    elif token == 'q':
        sender.reply("✅ 已取消登录")
        return
        
    try:
        # 验证Token有效性
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # 构造查询请求数据
        data = {
            "service": "media",
            "api": "lottery/queryActivityAwardRecordList",
            "data": {
                "uid": "30a7f9016d224fc2a8367200cbbab62a",
                "content": "null"
            },
            "userDevice": {
                "os": "14",
                "deviceBrand": "Redmi",
                "deviceId": "13666addccf39a5c",
                "equipmentId": "13666addccf39a5c",
                "deviceType": "Xiaomi Redmi K30 Pro Zoom Edition",
                "device": "android",
                "clientVersion": "5.2.3",
                "gtCid": ""
            },
            "traceId": f"KICUBKZ9{int(time.time()*1000)}",
            "token": token
        }
        
        # 发送查询请求验证Token
        response = requests.post(
            "https://app.eyh.cn/gateway/api",
            json=data,
            headers=headers
        )
        
        if response.status_code != 200:
            raise Exception("Token验证失败")
            
        result = response.json()
        if result['code'] != "0":
            error_msg = result.get('message', '未知错误')
            if "登录状态已失效" in error_msg:
                raise Exception("Token已失效,请重新登录")
            raise Exception(f"Token无效: {error_msg}")
            
        # Token验证成功后，使用发送者ID作为标识
        mobile = userid  # 使用发送者ID替代手机号
        
        # 记录日志
        log_operation('token_login', userid, mobile, 'success')
        
        return process_login(token, mobile, mobile)
        
    except Exception as e:
        log_operation('token_login', userid, 'unknown', 'failed', str(e))
        raise Exception(f"Token登录失败: {str(e)}")

def process_login(token, account, mobile):
    """处理登录成功后的操作"""
    try:
        accounts = eval(uservalue or '[]')
        # 如果是Token登录，使用token作为账号标识
        if len(token) == 32:
            account = token
            display = f"Token...{token[-6:]}"
        else:
            account = mobile
            display = f"{mobile[:3]}****{mobile[-4:]}"
        
        if account not in accounts:
            accounts.append(account)
            middleware.bucketSet('kangyh_user', userid, str(accounts))
        
        # 保存token
        middleware.bucketSet('kangyh_token', account, token)
        
        # 添加到青龙
        if not add_to_qinglong(token, account, mobile):
            raise Exception("添加青龙变量失败")
        
        # 刚登录，尚未授权 => 禁用该变量
        env_id_str = middleware.bucketGet('kangyh_env_id', account)
        if env_id_str:
            env_ids = json.loads(env_id_str)
            disable_in_qinglong(env_ids)
        
        success_msg = f"""
=====登录成功=====
📱 账号: {display}
✅ 已保存到青龙(当前禁用)
------------------
发送"{manage_cmd}"管理账号
发送"{query_cmd}"查询账号
"""
        sender.reply(success_msg)
        return True
    except Exception as e:
        raise Exception(f"处理登录失败: {str(e)}")

def manage_accounts():
    """管理账号"""
    if not uservalue:
        sender.reply(f"""
=====账号管理=====
❌ 未找到任何账号
------------------
💡 发送"{login_cmd}"登录账号
==================""")
        return
        
    accounts = eval(uservalue)
    if not accounts:  # 如果账号列表为空
        sender.reply(f"""
=====账号管理=====
❌ 未找到任何账号
------------------
💡 发送"{login_cmd}"登录账号
==================""")
        return
        
    account_list = """
=====账号列表=====
批量操作:
[01] 删除全部账号
[00] 授权全部账号
------------------
账号列表:"""

    for i, account in enumerate(accounts, 1):
        # 获取token和授权信息
        token = middleware.bucketGet('kangyh_token', account)
        auth = middleware.bucketGet('kangyh_auth', account)
        auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        
        # 根据登录方式显示不同格式的账号信息
        if len(token) == 32:  # Token登录
            display = f"Token...{token[-6:]}"  # 只显示token后6位
        else:  # 手机号登录
            display = f"{account[:3]}****{account[-4:]}"  # 隐藏中间4位手机号
            
        account_list += f"\n[{i}] {display}\n    {auth_status}"
        if auth and auth > today:
            account_list += f"\n    到期: {auth}"

    # 在所有账号列表后面只添加一次提示
    account_list += """
------------------
回复数字选择账号
回复"q"退出"""

    sender.reply(account_list)
    choice = sender.listen(60000)
    
    if not choice:
        sender.reply("❌ 操作超时")
        return
    elif choice == 'q':
        sender.reply("✅ 已取消操作")
        return
        
    try:
        if choice == '01':
            # 删除所有账号
            for account in accounts:
                delete_account(account)
            sender.reply("✅ 已删除全部账号")
        elif choice == '00':
            # 授权所有账号
            sender.reply("请输入授权天数:")
            days = sender.listen(60000)
            
            if not days:
                sender.reply("❌ 操作超时")
                return
            elif days == 'q':
                sender.reply("✅ 已取消授权")
                return
                
            try:
                days = int(days)
                if days <= 0:
                    raise ValueError()
                    
                # 计算总金额
                amount = price * (Decimal(days) / Decimal(30)) * Decimal(len(accounts))
                amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding='ROUND_UP')
                
                if process_payment(amount, days):
                    success_count = 0
                    for account in accounts:
                        auth_time = calculate_auth_time(account, days/30)
                        middleware.bucketSet('kangyh_auth', account, auth_time)
                        success_count += 1
                        
                    sender.reply(f"""
=====批量授权成功=====
💰 支付: {amount}元
⏰ 时长: {days}天
✅ 成功: {success_count}个账号
==================""")
                    
            except ValueError:
                sender.reply("❌ 无效的天数")
            except Exception as e:
                sender.reply(f"❌ 批量授权失败: {str(e)}")
        else:
            # 选择单个账号操作
            index = int(choice) - 1
            if not 0 <= index < len(accounts):
                raise ValueError()
                
            account = accounts[index]
            show_account_menu(account)
            
    except ValueError:
        sender.reply("❌ 无效的选择")
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")

def show_account_menu(account):
    """显示账号操作菜单"""
    # 获取token和授权信息用于显示
    token = middleware.bucketGet('kangyh_token', account)
    auth = middleware.bucketGet('kangyh_auth', account)
    
    # 确定显示格式
    if len(token) == 32:
        display = f"Token...{token[-6:]}"
    else:
        display = f"{account[:3]}****{account[-4:]}"
        
    # 显示授权状态
    auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
    auth_info = f"\n    到期: {auth}" if auth and auth > today else ""
    
    menu = f"""
=====账号操作=====
📱 账号: {display}
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
        # 获取用户积分
        user_coin = middleware.bucketGet('dd_sign_coin', userid) or '0'
        user_coin = Decimal(user_coin)  # 使用 Decimal 处理大数值
        
        # 计算一个月需要的积分
        month_coin = Decimal(coin_price)  # 从配置获取每月所需积分
        
        # 如果积分设置为0，关闭积分支付
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
            # 微信支付
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
                
            # 计算金额
            amount = price * (Decimal(days) / Decimal(30))
            amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding='ROUND_UP')
            if amount < Decimal('0.01'):
                amount = Decimal('0.01')
                
            payment_success = process_payment(amount, days)  # 处理支付
            if payment_success:  # 只有在支付成功的情况下才进行授权
                auth_time = calculate_auth_time(account, days/30)
                middleware.bucketSet('kangyh_auth', account, auth_time)
                
                # 启用环境变量
                env_id_str = middleware.bucketGet('kangyh_env_id', account)
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
            # 积分支付
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
                
            # 计算所需积分
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
            
            # 扣除积分
            new_coin = user_coin - need_coin
            middleware.bucketSet('dd_sign_coin', userid, str(new_coin))
            
            # 设置授权时间
            auth_time = calculate_auth_time(account, months)
            middleware.bucketSet('kangyh_auth', account, auth_time)
            
            # 启用环境变量
            env_id_str = middleware.bucketGet('kangyh_env_id', account)
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
    zsm = middleware.bucketGet('kangyh', 'zsm')
    if not zsm:
        sender.reply("❌ 未配置收款码")
        return False
        
    # 显示支付信息
    pay_msg = f"""
=====微信扫码支付====
🎫 商品: 看余杭授权
📅 时长: {days}天
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)
    sender.replyImage(zsm)
    
    # 等待支付结果
    result = sender.waitPay("q", 100000)
    
    if not result:
        sender.reply("❌ 支付超时")
        return False
    elif result == 'q':
        sender.reply("✅ 已取消支付")
        return False
        
    try:
        if isinstance(result, str):
            # 解析JSON字符串
            result = json.loads(result)
            
        # 统一处理支付信息
        if 'Money' in result:
            # 老格式
            paid_amount = Decimal(str(result.get('Money', 0)))
            pay_time = result.get('Time', '')
            pay_from = ''
        else:
            # 新格式
            paid_amount = Decimal(str(result.get('money', 0)))
            pay_time = result.get('Time', '')
            pay_from = result.get('FromName', '')
            
        # 检查支付金额
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
    auth = middleware.bucketGet('kangyh_auth', account)
    
    if auth and auth > str(current):
        start = datetime.strptime(auth, "%Y-%m-%d").date()
    else:
        start = current
        
    # 使用传入的月数（可以是小数）计算天数
    days = int(months * 30)
    end = start + timedelta(days=days)
    return str(end)

def query_account():
    """查询账号信息"""
    if not uservalue:
        sender.reply(f"""
=====账号查询=====
❌ 未找到任何账号
------------------
💡 发送"{login_cmd}"登录账号
==================""")
        return
        
    accounts = eval(uservalue)
    if not accounts:  # 如果账号列表为空
        sender.reply(f"""
=====账号查询=====
❌ 未找到任何账号
------------------
💡 发送"{login_cmd}"登录账号
==================""")
        return
        
    for account in accounts:
        try:
            # 检查授权状态
            auth = middleware.bucketGet('kangyh_auth', account)
            token = middleware.bucketGet('kangyh_token', account)
            
            # 确定显示格式
            if len(token) == 32:
                display = f"Token...{token[-6:]}"
            else:
                display = f"{account[:3]}****{account[-4:]}"
                
            if not auth or auth <= today:
                sender.reply(f"""
=====账号未授权=====
📱 账号: {display}
❌ 状态: 未授权
💡 请先完成授权后再查询
==================""")
                continue
                
            if not token:
                continue
                
            # 构造查询请求
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "User-Agent": "okhttp/5.0.0-alpha.2",
                "Host": "app.eyh.cn",
                "Connection": "Keep-Alive",
                "Accept-Encoding": "gzip"
            }
            
            data = {
                "service": "media",
                "api": "lottery/queryActivityAwardRecordList",
                "data": {
                    "uid": "30a7f9016d224fc2a8367200cbbab62a",
                    "content": "null"
                },
                "userDevice": {
                    "os": "14",
                    "deviceBrand": "Redmi",
                    "deviceId": "13666addccf39a5c",
                    "equipmentId": "13666addccf39a5c",
                    "deviceType": "Xiaomi Redmi K30 Pro Zoom Edition",
                    "device": "android",
                    "clientVersion": "5.2.3",
                    "gtCid": ""
                },
                "traceId": f"QUERY{int(time.time()*1000)}",
                "token": token
            }
            
            # 发送查询请求
            response = requests.post(
                "https://app.eyh.cn/gateway/api",
                json=data,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception("查询失败")
                
            result = response.json()
            if result['code'] != "0":
                raise Exception(f"查询失败: {result['message']}")
                
            # 处理奖励记录
            awards = result['data']
            
            # 获取授权信息
            auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
            auth_time = f"\n📅 到期: {auth}" if auth else ""
            
            # 计算最近奖励总额
            recent_awards = sorted(awards, key=lambda x: x['createTime'], reverse=True)[:3]
            total_amount = sum(
                float(award['description'].replace('元微信红包', ''))
                for award in recent_awards
                if '元微信红包' in award['description']
            )
            
            # 构建奖励记录显示
            awards_display = ""
            if recent_awards:
                awards_display = "最近奖励记录:"
                for award in recent_awards:
                    award_time = datetime.fromtimestamp(award['createTime']/1000).strftime('%Y-%m-%d %H:%M:%S')
                    status = '已发放' if award['status'] == 2 else '未发放'
                    awards_display += f"\n🎁 {award['name']} ({award['description']})"
                    awards_display += f"\n⏰ 时间: {award_time}"
                    awards_display += f"\n📌 状态: {status}"
                    if award.get('grantTip'):
                        awards_display += f"\n💡 说明: {award['grantTip']}"
                
                if total_amount > 0:
                    awards_display += f"\n💰 近期总额: {total_amount:.2f}元"
            
            # 显示账号信息
            account_info = f"""
=====账号信息=====
📱 账号: {display}
🔐 授权: {auth_status}{auth_time}{awards_display}
=================="""
            account_info = account_info.replace("\n\n", "\n")  # 去掉多余的换行
            sender.reply(account_info)
            
        except Exception as e:
            error_msg = str(e)
            sender.reply(f"❌ 查询失败: {error_msg}")
            log_operation('query_account', userid, account, 'failed', error_msg)
            continue

def clean_expired():
    """清理过期账号"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
        
    users = middleware.bucketAllKeys('kangyh_user')
    cleaned = 0
    
    for user in users:
        accounts = eval(middleware.bucketGet('kangyh_user', user) or '[]')
        valid = []
        
        for account in accounts:
            auth = middleware.bucketGet('kangyh_auth', account)
            if not auth or auth <= str(datetime.now().date()):
                middleware.bucketDel('kangyh_token', account)
                middleware.bucketDel('kangyh_auth', account)
                cleaned += 1
            else:
                valid.append(account)
                
        if valid:
            middleware.bucketSet('kangyh_user', user, str(valid))
        else:
            middleware.bucketDel('kangyh_user', user)
            
    sender.reply(f"✅ 已清理 {cleaned} 个过期账号")

def main():
    """主函数"""
    message = sender.getMessage()
    
    if '登录' in message:
        login()
    elif '管理' in message:
        manage_accounts()
    elif '查询' in message:
        query_account()
    elif message == '清理看余杭':
        clean_expired()
    elif message == '看余杭授权' and sender.isAdmin():
        admin_auth()
    else:
        sender.setContinue()

def cron_task():
    """定时任务处理"""
    if imtype != 'fake':
        return
        
    try:
        users = middleware.bucketAllKeys('kangyh_user')
        for user in users:
            accounts = eval(middleware.bucketGet('kangyh_user', user) or '[]')
            for account in accounts:
                try:
                    # 检查账号状态
                    token = middleware.bucketGet('kangyh_token', account)
                    if not token:
                        continue
                        
                    # 检查授权状态
                    auth = middleware.bucketGet('kangyh_auth', account)
                    if auth and auth <= today:
                        # 授权已过期,禁用环境变量
                        env_id_str = middleware.bucketGet('kangyh_env_id', account)
                        if env_id_str:
                            env_ids = json.loads(env_id_str)
                            disable_in_qinglong(env_ids)
                        notify_user(user, account, "授权已过期,环境变量已禁用,请及时续费")
                        continue

                    # 构造查询请求验证 Token 有效性
                    headers = {
                        "Content-Type": "application/json; charset=utf-8",
                        "User-Agent": "okhttp/5.0.0-alpha.2",
                        "Host": "app.eyh.cn",
                        "Connection": "Keep-Alive",
                        "Accept-Encoding": "gzip"
                    }
                    
                    data = {
                        "service": "media",
                        "api": "lottery/queryActivityAwardRecordList",
                        "data": {
                            "uid": "30a7f9016d224fc2a8367200cbbab62a",
                            "content": "null"
                        },
                        "userDevice": {
                            "os": "14",
                            "deviceBrand": "Redmi",
                            "deviceId": "13666addccf39a5c",
                            "equipmentId": "13666addccf39a5c",
                            "deviceType": "Xiaomi Redmi K30 Pro Zoom Edition",
                            "device": "android",
                            "clientVersion": "5.2.3",
                            "gtCid": ""
                        },
                        "traceId": f"CRON{int(time.time()*1000)}",
                        "token": token
                    }
                    
                    # 发送查询请求验证Token
                    response = requests.post(
                        "https://app.eyh.cn/gateway/api",
                        json=data,
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        notify_user(user, account, "账号状态异常,请更新token")
                        continue
                        
                    result = response.json()
                    if result['code'] != "0":
                        error_msg = result.get('message', '未知错误')
                        if "登录状态已失效" in error_msg:
                            notify_user(user, account, "Token已失效,请重新登录")
                            # 删除无效token
                            middleware.bucketDel('kangyh_token', account)
                        else:
                            notify_user(user, account, f"账号异常: {error_msg}")
                        continue
                        
                    # Token有效，检查授权状态
                    auth = middleware.bucketGet('kangyh_auth', account)
                    if auth and auth <= today:
                        notify_user(user, account, "授权已过期,请及时续费")
                        
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
📱 账号: {account[:3]}****{account[-4:]}
📢 消息: {message}
=================="""
        
        # 发送到各个平台
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
        
        logs = eval(middleware.bucketGet('kangyh_logs', 'operations') or '[]')
        logs.append(log)
        if len(logs) > 1000:  # 只保留最近1000条
            logs = logs[-1000:]
        middleware.bucketSet('kangyh_logs', 'operations', str(logs))
        
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
------------------
回复数字选择功能
回复"q"退出"""

    sender.reply(auth_menu)
    choice = sender.listen(60000)
    
    if not choice or choice == 'q':
        return
        
    if choice == '1':
        auth_all_users()
    elif choice == '2':
        auth_specific_user()
    else:
        sender.reply("❌ 无效的选择")

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
        
        users = middleware.bucketAllKeys('kangyh_user')
        success = 0
        failed = 0
        
        for user in users:
            accounts = eval(middleware.bucketGet('kangyh_user', user) or '[]')
            for account in accounts:
                try:
                    auth_time = calculate_auth_time(account, days/30)
                    middleware.bucketSet('kangyh_auth', account, auth_time)
                    
                    # 更新青龙变量（已存在也会覆盖）
                    token = middleware.bucketGet('kangyh_token', account)
                    if token:
                        phone = account[:3] + '*'*4 + account[7:]
                        add_to_qinglong(token, account, phone)
                        
                    # ★ 新增：启用青龙变量
                    env_ids_str = middleware.bucketGet('kangyh_env_id', account)
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
        
    accounts = eval(middleware.bucketGet('kangyh_user', user_id) or '[]')
    if not accounts:
        sender.reply("❌ 未找到该用户的账号")
        return
        
    account_list = """
=====账号列表=====
[0] 授权全部账号"""
    
    for i, account in enumerate(accounts, 1):
        auth = middleware.bucketGet('kangyh_auth', account)
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
            # 授权所有账号
            for account in accounts:
                try:
                    auth_time = calculate_auth_time(account, days/30)
                    middleware.bucketSet('kangyh_auth', account, auth_time)
                    
                    token = middleware.bucketGet('kangyh_token', account)
                    if token:
                        phone = account[:3] + '*'*4 + account[7:]
                        add_to_qinglong(token, account, phone)
                        
                    # ★ 新增：启用青龙变量
                    env_ids_str = middleware.bucketGet('kangyh_env_id', account)
                    if env_ids_str:
                        env_ids = json.loads(env_ids_str)
                        enable_in_qinglong(env_ids)

                    log_operation('auth', user_id, account, 'success')
                except Exception as e:
                    log_operation('auth', user_id, account, 'failed', str(e))
            
            sender.reply(f"✅ 已授权所有账号 {days}天")
            
        else:
            # 授权单个账号
            index = int(choice) - 1
            if not 0 <= index < len(accounts):
                raise ValueError()
                
            account = accounts[index]
            auth_time = calculate_auth_time(account, days/30)
            middleware.bucketSet('kangyh_auth', account, auth_time)
            
            token = middleware.bucketGet('kangyh_token', account)
            if token:
                phone = account[:3] + '*'*4 + account[7:]
                add_to_qinglong(token, account, phone)
                
            # ★ 新增：启用青龙变量
            env_ids_str = middleware.bucketGet('kangyh_env_id', account)
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
    
    response = requests.post(
        "https://app.eyh.cn/gateway/api",
        json=data,
        headers=headers
    )
    return response

def delete_account(account):
    """删除账号"""
    try:
        # 从青龙面板删除变量
        if not delete_from_qinglong(account):
            raise Exception("从青龙删除变量失败")
            
        # 删除本地存储的token和授权信息
        middleware.bucketDel('kangyh_token', account)
        middleware.bucketDel('kangyh_auth', account)
        
        # 从用户账号列表中移除
        accounts = eval(uservalue)
        if account in accounts:
            accounts.remove(account)
            middleware.bucketSet('kangyh_user', userid, str(accounts))
            
        sender.reply(f"""
=====删除成功=====
📱 账号: {account[:3]}****{account[-4:]}
✅ 状态: 已删除
==================""")
        
        # 记录操作日志
        log_operation('delete_account', userid, account, 'success')
        return True
        
    except Exception as e:
        error_msg = f"删除账号失败: {str(e)}"
        sender.reply(f"❌ {error_msg}")
        log_operation('delete_account', userid, account, 'failed', str(e))
        return False

# 异步请求工具
async def async_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

# 缓存数据桶操作
@lru_cache(maxsize=100)
def cached_bucket_get(bucket, key):
    return middleware.bucketGet(bucket, key)

# 异步处理登录
async def async_login():
    token = await async_request("https://app.eyh.cn/gateway/api", login_data)
    if token:
        await async_add_to_qinglong(token)

if __name__ == "__main__":
    try:
        # 初始化配置
        var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price = get_config()
        
        # 初始化青龙
        ql_url, ql_token = init_qinglong()
        
        # 获取其他信息
        imtype = sender.getImtype()
        today = str(datetime.now().date())
        
        # 处理定时任务
        if imtype == 'fake':
            cron_task()
        else:
            # 运行主函数
            main()
            
    except Exception as e:
        sender.reply(f"❌ 运行出错: {str(e)}")

