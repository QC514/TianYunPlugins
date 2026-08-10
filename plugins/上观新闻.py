# [rule: ^(上观|sgxw)(登录|登陆)$|^登(录|陆)(上观|sgxw)$|^(上观|sgxw)(查询|管理)$|^(查询|管理)(上观|sgxw)$|^清理上观$|^上观授权$|^上观教程$]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: ]
# [public: true]
# [title: 上观新闻]
# [icon: https://y.gtimg.cn/music/photo_new/T053M000001NYort1rZecQ.png]
# [open_source: false]
# [class: 工具类]
# [version: 1.1.2]
# [price: 6.88]
# [admin: false]
# [author: rujingxianghai]
# [service: 2993959969]
# [description: 上观新闻积分实物<br>指令：上观登录、管理、查询、授权、教程<br>脚本及卡密进群获取]

import os
import json
import time
import hashlib
import random
import string
import base64
import requests
from datetime import datetime, timedelta
import middleware

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='sgxw_user', key=userid)

# 接口地址
BASE_URL = "https://services.shobserver.cn"
FIXED_TOKEN = "rVX9ITrrTPrCurUe"

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 'sgxw_config',
    'coin_key': 'sgxwcoin',
    'name': '上观新闻'
}

# [param: {"required":true,"key":"sgxw_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"sgxw_config.sgxw_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割"}]
# [param: {"required":true,"key":"sgxw_config.sgxw_osname","bool":false,"placeholder":"必填项,例:S_SGXW","name":"提交到青龙的变量名","desc":"青龙容器内上观新闻的变量名"}]
# [param: {"required":true,"key":"sgxw_config.sgxwVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"sgxw_config.sgxwcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]

def get_user_content():
    """获取用户配置内容"""
    sgxw_osname = middleware.bucketGet('sgxw_config', 'sgxw_osname') or 'S_SGXW'
    sgxw_qlname = middleware.bucketGet('sgxw_config', 'sgxw_qlname') or 'S_SGXW'
    sgxw_managecommand = middleware.bucketGet('sgxw_config', 'sgxw_managecommand') or '上观管理'
    sgxw_querycommand = middleware.bucketGet('sgxw_config', 'sgxw_querycommand') or '上观查询'
    sgxw_signcommand = middleware.bucketGet('sgxw_config', 'sgxw_signcommand') or '上观登录'
    
    randommanagecommand = sgxw_managecommand
    randomquerycommand = sgxw_querycommand
    randomsigncommand = sgxw_signcommand
    
    sgxwVipmoney = float(middleware.bucketGet('sgxw_config', 'sgxwVipmoney') or '1')
    
    # 优先从卡密系统获取积分配置
    sgxwcoin = middleware.bucketGet(PLUGIN_CONFIG['bucket'], PLUGIN_CONFIG['coin_key'])
    if not sgxwcoin:
        # 如果卡密系统未配置，则使用插件配置
        sgxwcoin = middleware.bucketGet('sgxw_config', 'sgxwcoin') or '0'
    sgxwcoin = int(sgxwcoin)
    
    return (sgxw_osname, sgxw_qlname, randommanagecommand, 
            randomquerycommand, randomsigncommand, sgxwVipmoney, sgxwcoin)

def mask_phone(phone):
    """手机号脱敏处理"""
    if not phone or len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[7:]}"

def generate_random_base64(length=32):
    """生成随机base64字符串"""
    random_bytes = ''.join(random.choices(string.ascii_letters + string.digits, k=length)).encode()
    return base64.b64encode(random_bytes).decode()

def generate_signature(raw_str: str) -> str:
    """生成MD5签名"""
    try:
        return hashlib.md5(raw_str.encode(), usedforsecurity=True).hexdigest()
    except TypeError:
        return hashlib.md5(raw_str.encode()).hexdigest()

def verify_account(username, password):
    """验证账号有效性，登录上观新闻
    username: 手机号
    password: 密码
    """
    try:
        # 准备登录请求
        timestamp = int(time.time() * 1000)
        sign_str = f"{username}${timestamp}${FIXED_TOKEN}"
        sign = generate_signature(sign_str)
        
        data = {
            "mobile": username,
            "password": password,
            "times": timestamp,
            "sign": sign
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "okhttp/4.10.0",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }
        
        # 发送登录请求
        response = requests.post(f"{BASE_URL}/user/login", data=data, headers=headers, timeout=10, verify=False)
        result = response.json()
        
        if result.get("breturn", False):
            # 登录成功
            user_id = result.get("object", {}).get("id", "")
            score = result.get("object", {}).get("score", "未知")
            return {
                "success": True,
                "message": "登录成功",
                "user_id": user_id,
                "score": score
            }
        else:
            # 登录失败
            return {
                "success": False,
                "message": result.get('errorinfo', '登录失败，请检查账号密码')
            }
        
    except Exception as e:
        print(f"验证账号失败: {str(e)}")
        return {"success": False, "message": str(e)}

def bind_account():
    """绑定上观新闻账号"""
    sender.reply("""
=====上观新闻登录=====
请按照提示依次输入账号信息
回复"q"随时退出操作
==================""")
    
    # 步骤1：输入手机号
    sender.reply("请输入手机号（上观新闻登录账号）:")
    username = sender.input(120000, 1, False)
    if not username:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif username.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    # 简单验证手机号格式
    if not username.isdigit() or len(username) != 11:
        sender.reply("""
=====格式错误=====
❌ 手机号格式不正确
------------------
请输入11位数字手机号
==================""")
        return
    
    # 步骤2：输入密码
    sender.reply("请输入密码（上观新闻登录密码）:")
    password = sender.input(120000, 1, False)
    if not password:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif password.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    # 步骤3：输入备注
    sender.reply("请输入备注名称（用于区分不同账号）:")
    remark = sender.input(120000, 1, False)
    if not remark:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif remark.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
    
    # 验证账号
    try:
        login_result = verify_account(username, password)
        if login_result.get('success'):
            user_id = login_result.get('user_id')
            score = login_result.get('score')
            
            # 保存账号信息
            if not uservalue:
                middleware.bucketSet('sgxw_user', userid, str([username]))
            else:
                accounts = eval(uservalue)
                if username not in accounts:
                    accounts.append(username)
                    middleware.bucketSet('sgxw_user', userid, str(accounts))
                    
            # 保存账号详细信息
            account_info = {
                "username": username,
                "password": password,
                "remark": remark,
                "user_id": user_id
            }
            middleware.bucketSet('sgxw_token', username, json.dumps(account_info))
            
            success_msg = f"""
=====绑定成功=====
👤 备注: {remark}
📱 手机号: {mask_phone(username)}
🪙 当前积分: {score}
=================="""
            sender.reply(success_msg)
            
            # 绑定成功后立即开始授权流程
            authorize_account(username, account_info)
            
        else:
            sender.reply(f"""
=====验证失败=====
❌ 原因: {login_result.get('message', '未知错误')}
请检查账号密码是否正确
==================""")
            
    except Exception as e:
        sender.reply(f"""
=====绑定异常=====
❌ 错误: {str(e)}
请重试或联系管理员
==================""")

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
==================""")
        return
        
    accounts = eval(uservalue)
    account_list = """
========选择账号=======
[0] 全部账号"""
    
    for i, username in enumerate(accounts, 1):
        account_info = json.loads(middleware.bucketGet('sgxw_token', username))
        remark = account_info.get('remark', username)
        auth_time = middleware.bucketGet('sgxw_auth', username)
        
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
            
        account_list += f"""
[{i}]{mask_phone(username)}({remark}, {auth_status})"""
        
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
        for username in selected_accounts:
            try:
                account_info = json.loads(middleware.bucketGet('sgxw_token', username))
                password = account_info.get('password', '')
                
                # 验证账号是否有效
                login_result = verify_account(username, password)
                
                if login_result.get('success'):
                    # 更新user_id
                    account_info['user_id'] = login_result.get('user_id', '')
                    middleware.bucketSet('sgxw_token', username, json.dumps(account_info))
                    
                    # 获取授权信息
                    auth_time = middleware.bucketGet('sgxw_auth', username)
                    auth_status = '已授权' if auth_time and auth_time >= str(datetime.now().date()) else '未授权'
                    
                    # 显示账号信息
                    account_info_msg = f"""
=====账号信息[{query_count+1}/{len(selected_accounts)}]=====
📱 手机号: {mask_phone(username)}
👤 备注: {account_info.get('remark')}
🔐 授权状态: {auth_status}
🪙 当前积分: {login_result.get('score', '未知')}
=================="""
                    sender.reply(account_info_msg)
                    query_count += 1
                    
                    # 如果查询的账号过多，中间加一点延迟
                    if query_count < len(selected_accounts) and len(selected_accounts) > 3:
                        time.sleep(0.5)
                        
                else:
                    sender.reply(f"""
=====查询失败[{query_count+1}/{len(selected_accounts)}]=====
📱 手机号: {mask_phone(username)}
❌ 状态: {login_result.get('message', '账号验证失败')}
==================""")
                    query_count += 1
                    
            except Exception as e:
                sender.reply(f"""
=====查询异常[{query_count+1}/{len(selected_accounts)}]=====
📱 手机号: {mask_phone(username)}
❌ 错误: {str(e)}
==================""")
                query_count += 1
                
        # 查询完成提示
        if query_count > 0:
            sender.reply(f"✅ 查询完成，共查询了 {query_count} 个账号")
            
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")

def manage_account():
    """账号管理功能"""
    if not uservalue:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
==================""")
        return
        
    accounts = eval(uservalue)
    
    # 先显示管理功能菜单
    menu = """
=====账号管理=====
[1] 授权账号
[2] 删除账号
[3] 提交青龙
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(menu)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出操作")
        return
    
    # 然后显示账号列表供选择
    account_list = """
========选择账号=======
[0] 全部账号"""
    
    for i, username in enumerate(accounts, 1):
        account_info = json.loads(middleware.bucketGet('sgxw_token', username))
        remark = account_info.get('remark', username)
        auth_time = middleware.bucketGet('sgxw_auth', username)
        
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
            
        account_list += f"""
[{i}]{mask_phone(username)}({remark}, {auth_status})"""
        
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
            confirm = """
=====确认删除=====
⚠️ 此操作不可恢复
------------------
回复 y 确认删除
回复 n 取消操作
=================="""
            sender.reply(confirm)
            
            confirm = sender.input(120000, 1, False)
            if confirm.lower() == 'y':
                success_count = 0
                for username in selected_accounts:
                    try:
                        # 从账号列表中移除
                        if username in accounts:
                            accounts.remove(username)
                            
                        # 删除相关信息
                        middleware.bucketDel('sgxw_token', username)
                        middleware.bucketDel('sgxw_auth', username)
                            
                        # 删除青龙变量
                        delete_ql_env(username)
                        success_count += 1
                    except Exception as e:
                        print(f"删除账号失败: {username}, 错误: {str(e)}")
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet('sgxw_user', userid, str(accounts))
                else:
                    middleware.bucketDel('sgxw_user', userid)
                    
                sender.reply(f"✅ 已成功删除 {success_count}/{len(selected_accounts)} 个账号")
            else:
                sender.reply("✅ 已取消删除")
                
        elif choice == '3':
            # 提交选中账号到青龙
            success_count = 0
            for username in selected_accounts:
                try:
                    account_info = json.loads(middleware.bucketGet('sgxw_token', username))
                    
                    # 如果已授权则更新青龙变量
                    auth_time = middleware.bucketGet('sgxw_auth', username)
                    if auth_time and auth_time >= str(datetime.now().date()):
                        if update_ql_env(username, account_info):
                            success_count += 1
                    else:
                        print(f"账号未授权或已过期: {username}")
                except Exception as e:
                    print(f"提交青龙失败: {username}, 错误: {str(e)}")
            
            sender.reply(f"""
=====提交结果=====
📊 选择账号: {len(selected_accounts)}个
✅ 提交成功: {success_count}个
❌ 提交失败: {len(selected_accounts) - success_count}个
------------------
💡 提示: 未授权账号无法提交
==================""")
        else:
            sender.reply("❌ 无效的选择")
            
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}") 

def authorize_multiple_accounts(usernames):
    """授权多个账号"""
    account_infos = []
    # 获取账号信息
    for username in usernames:
        try:
            account_info = json.loads(middleware.bucketGet('sgxw_token', username))
            password = account_info.get('password', '')
            
            # 验证账号有效性
            login_result = verify_account(username, password)
            if login_result.get('success'):
                # 更新user_id
                account_info['user_id'] = login_result.get('user_id', '')
                middleware.bucketSet('sgxw_token', username, json.dumps(account_info))
                account_infos.append({
                    'username': username,
                    'info': account_info
                })
            else:
                sender.reply(f"""
⚠️ 账号登录失败:
📱 手机号: {mask_phone(username)}
❌ 原因: {login_result.get('message', '验证失败')}""")
        except Exception as e:
            sender.reply(f"""
⚠️ 账号处理异常:
📱 手机号: {mask_phone(username)}
❌ 原因: {str(e)}""")
            
    if not account_infos:
        sender.reply("❌ 没有有效的账号可授权")
        return
        
    # 显示选择了多少个有效账号
    sender.reply(f"✅ 共有 {len(account_infos)} 个有效账号可授权")
    
    auth_menu = """
=====授权方式选择=====
[1] 微信支付
[2] 积分兑换
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
        # 余额支付
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
            total_money = len(account_infos) * months * sgxwVipmoney
            
            # 处理支付
            if pay_order(project=f'上观新闻授权(共{len(account_infos)}个账号)', months=months, money=total_money):
                # 处理每个账号的授权
                success_count = 0
                for account in account_infos:
                    try:
                        username = account['username']
                        account_info = account['info']
                        
                        # 获取当前授权状态
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('sgxw_auth', username)
                        
                        # 计算新的到期时间
                        if accountVip and accountVip > dqsj:
                            # 如果当前已有有效授权，从授权到期时间开始计算
                            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                        else:
                            # 如果没有有效授权，从当前时间开始计算
                            start_date = datetime.now()
                            
                        # 计算新的到期时间(按月计算，每月30天)
                        new_expire = start_date + timedelta(days=30*months)
                        new_expire = new_expire.strftime("%Y-%m-%d")
                        
                        # 更新授权时间
                        middleware.bucketSet('sgxw_auth', username, new_expire)
                        
                        # 更新青龙变量
                        if update_ql_env(username, account_info):
                            success_count += 1
                    except Exception as e:
                        print(f"授权账号异常: {username}, 错误: {str(e)}")
                
                # 显示授权结果
                success_msg = f"""
=====授权结果=====
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
------------------
⏰ 授权: {months}个月
📅 到期: {new_expire}
------------------
💰 总金额: {total_money}元
=================="""
                sender.reply(success_msg)
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
        
    elif pay_choice == '2':
        # 积分兑换
        if not sgxwcoin:
            sender.reply("""
=====兑换失败=====
❌ 积分兑换功能未开启
------------------
💡 请选择其他支付方式
==================""")
            return
            
        # 从卡密系统获取用户积分
        user_coin = middleware.bucketGet('dd_sign_points', userid) or '0'
        try:
            user_coin = int(user_coin)
        except:
            user_coin = 0
            
        # 显示积分兑换信息
        sender.reply(f"""
=====积分兑换=====
💰 当前积分: {user_coin}
🎯 兑换比例: {sgxwcoin}积分/月/账号
📊 账号数量: {len(account_infos)}个
------------------
请输入兑换月数
回复"q"退出操作
==================""")
        
        months = sender.input(120000, 1, False)
        if not months or months.lower() == 'q':
            sender.reply("✅ 已取消兑换")
            return
            
        try:
            months = int(months)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
                
            # 计算所需总积分 = 账号数 * 月数 * 每月积分
            total_coin_needed = len(account_infos) * months * sgxwcoin
            
            if user_coin < total_coin_needed:
                sender.reply(f"""
=====兑换失败=====
❌ 积分不足
------------------
💰 当前积分: {user_coin}
🎯 所需积分: {total_coin_needed}
==================""")
                return
                
            # 扣除积分
            new_coin = user_coin - total_coin_needed
            middleware.bucketSet('dd_sign_points', userid, str(new_coin))
            
            # 处理每个账号的授权
            success_count = 0
            for account in account_infos:
                try:
                    username = account['username']
                    account_info = account['info']
                    
                    # 获取当前授权状态
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    accountVip = middleware.bucketGet('sgxw_auth', username)
                    
                    # 计算新的到期时间
                    if accountVip and accountVip > dqsj:
                        # 如果当前已有有效授权，从授权到期时间开始计算
                        start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                    else:
                        # 如果没有有效授权，从当前时间开始计算
                        start_date = datetime.now()
                        
                    # 计算新的到期时间(按月计算，每月30天)
                    new_expire = start_date + timedelta(days=30*months)
                    new_expire = new_expire.strftime("%Y-%m-%d")
                    
                    # 更新授权时间
                    middleware.bucketSet('sgxw_auth', username, new_expire)
                    
                    # 更新青龙变量
                    if update_ql_env(username, account_info):
                        success_count += 1
                except Exception as e:
                    print(f"授权账号异常: {username}, 错误: {str(e)}")
            
            # 显示兑换结果
            success_msg = f"""
=====兑换结果=====
📊 总账号: {len(account_infos)}个
✅ 成功: {success_count}个
❌ 失败: {len(account_infos) - success_count}个
------------------
⏰ 授权: {months}个月
📅 到期: {new_expire}
------------------
💰 积分详情:
• 消耗积分: {total_coin_needed}
• 剩余积分: {new_coin}
=================="""
            sender.reply(success_msg)
            
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
    else:
        sender.reply("❌ 无效的选择")

def authorize_account(username, account_info):
    """授权账号功能"""
    # 获取青龙配置信息
    qlconfig = middleware.bucketGet('sgxw_config', 'sgxw_qlname')
    
    # 简单提示青龙配置状态
    if not qlconfig:
        sender.reply("⚠️ 未配置青龙容器信息，授权后将无法自动提交变量")
    
    auth_menu = """
=====授权方式选择=====
[1] 微信支付
[2] 积分兑换
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
        # 余额支付
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
                
            # 计算价格
            money = months * sgxwVipmoney
            
            # 处理支付
            if pay_order(project='上观新闻授权', months=months, money=money):
                # 获取当前授权状态
                dqsj = datetime.now().strftime("%Y-%m-%d")
                accountVip = middleware.bucketGet('sgxw_auth', username)
                
                # 计算新的到期时间
                if accountVip and accountVip > dqsj:
                    # 如果当前已有有效授权，从授权到期时间开始计算
                    start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                else:
                    # 如果没有有效授权，从当前时间开始计算
                    start_date = datetime.now()
                    
                # 计算新的到期时间(按月计算，每月30天)
                new_expire = start_date + timedelta(days=30*months)
                new_expire = new_expire.strftime("%Y-%m-%d")
                
                # 更新授权时间
                middleware.bucketSet('sgxw_auth', username, new_expire)
                
                # 更新青龙变量
                ql_result = update_ql_env(username, account_info)
                
                success_msg = f"""
=====授权成功=====
📱 手机号: {mask_phone(username)}
⏰ 时长: {months}个月
📅 到期: {new_expire}
------------------
🔄 青龙同步: {'成功' if ql_result else '失败'}
=================="""
                sender.reply(success_msg)
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
        
    elif pay_choice == '2':
        # 积分兑换
        if not sgxwcoin:
            sender.reply("""
=====兑换失败=====
❌ 积分兑换功能未开启
------------------
💡 请选择其他支付方式
==================""")
            return
            
        # 从卡密系统获取用户积分
        user_coin = middleware.bucketGet('dd_sign_points', userid) or '0'
        try:
            user_coin = int(user_coin)
        except:
            user_coin = 0
            
        # 计算可兑换月数
        max_months = user_coin // sgxwcoin
        if max_months <= 0:
            sender.reply(f"""
=====积分不足=====
💰 当前积分: {user_coin}
🎯 所需积分: {sgxwcoin}/月
------------------
❌ 积分不足以兑换
==================""")
            return
            
        sender.reply(f"""
=====积分兑换=====
💰 当前积分: {user_coin}
🎯 兑换比例: {sgxwcoin}积分/月
📊 最多可兑: {max_months}个月
------------------
请输入兑换月数
回复"q"退出操作
==================""")
        
        months = sender.input(120000, 1, False)
        if not months or months.lower() == 'q':
            sender.reply("✅ 已取消兑换")
            return
            
        try:
            months = int(months)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
            elif months > max_months:
                sender.reply(f"""
=====兑换失败=====
❌ 积分不足
------------------
💰 当前积分: {user_coin}
🎯 需要积分: {months * sgxwcoin}
==================""")
                return
                
            # 扣除积分
            new_coin = user_coin - (months * sgxwcoin)
            middleware.bucketSet('dd_sign_points', userid, str(new_coin))
            
            # 获取当前授权状态
            dqsj = datetime.now().strftime("%Y-%m-%d")
            accountVip = middleware.bucketGet('sgxw_auth', username)
            
            # 计算新的到期时间
            if accountVip and accountVip > dqsj:
                # 如果当前已有有效授权，从授权到期时间开始计算
                start_date = datetime.strptime(accountVip, "%Y-%m-%d")
            else:
                # 如果没有有效授权，从当前时间开始计算
                start_date = datetime.now()
                
            # 计算新的到期时间(按月计算，每月30天)
            new_expire = start_date + timedelta(days=30*months)
            new_expire = new_expire.strftime("%Y-%m-%d")
            
            # 更新授权时间
            middleware.bucketSet('sgxw_auth', username, new_expire)
            
            # 更新青龙变量
            ql_result = update_ql_env(username, account_info)
            
            sender.reply(f"""
=====兑换成功=====
📱 手机号: {mask_phone(username)}
⏰ 时长: {months}个月
📅 到期: {new_expire}
------------------
💰 积分详情:
• 消耗积分: {months * sgxwcoin}
• 剩余积分: {new_coin}
------------------
🔄 青龙同步: {'成功' if ql_result else '失败'}
==================""")
            
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
    else:
        sender.reply("❌ 无效的选择")

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
        
    zsm = middleware.bucketGet('sgxw_config', 'zsm')
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
        return False
        
    # 生成订单号
    order_id = f"SGXW_{int(time.time())}_{userid}"
    
    # 记录待支付订单
    middleware.bucketSet('sgxw_order', order_id, json.dumps({
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
            middleware.bucketSet('sgxw_order', order_id, json.dumps({
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

def Addenvs(username, env_value, env_name="S_SGXW", account_info=None):
    """添加青龙变量
    env_name: 环境变量名称，默认S_SGXW
    """
    try:
        qlconfig = middleware.bucketGet('sgxw_config', 'sgxw_qlname')
        if not qlconfig:
            print("未配置青龙信息")
            return False, "未配置青龙信息"
            
        # 将英文的"|"替换为中文的"丨"
        qlconfig = qlconfig.replace('|', '丨')
        configs = qlconfig.split('丨')
        if len(configs) < 3:
            print("青龙配置格式错误")
            return False, "青龙配置格式错误"
            
        host = configs[0].strip()
        client_id = configs[1].strip()
        client_secret = configs[2].strip()
        
        # 获取token
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                error_msg = f"获取青龙token失败: {response.text}"
                print(error_msg)
                return False, error_msg
                
            result = response.json()
            if result['code'] != 200:
                error_msg = f"获取青龙token失败: {result.get('message')}"
                print(error_msg)
                return False, error_msg
                
            token = result['data']['token']
            headers = {'Authorization': f'Bearer {token}'}
        except Exception as e:
            error_msg = f"获取青龙token异常: {str(e)}"
            print(error_msg)
            return False, error_msg
        
        # 查找并删除已存在的变量
        try:
            envs_response = requests.get(f'{host}/open/envs', headers=headers, timeout=10)
            if envs_response.status_code != 200:
                error_msg = f"获取环境变量失败: {envs_response.text}"
                print(error_msg)
                return False, error_msg
                
            envs_data = envs_response.json()
            if envs_data.get('code') != 200:
                error_msg = f"获取环境变量失败: {envs_data.get('message')}"
                print(error_msg)
                return False, error_msg
                
            envs = envs_data['data']
            
            for env in envs:
                if env['name'] == env_name and username in env['value']:
                    # 兼容不同版本的青龙面板
                    env_id = env.get('_id') or env.get('id')
                    if env_id:
                        delete_response = requests.delete(f'{host}/open/envs', headers=headers, json=[env_id], timeout=10)
                        if delete_response.status_code != 200:
                            print(f"删除旧变量失败: {delete_response.text}")
                    break
        except Exception as e:
            error_msg = f"查询环境变量异常: {str(e)}"
            print(error_msg)
            # 这里不返回错误，继续尝试添加新变量
        
        # 获取用户ID和授权到期时间，如果account_info为None就从存储中获取
        if account_info is None:
            try:
                account_info = json.loads(middleware.bucketGet('sgxw_token', username))
            except:
                account_info = {}
        
        user_id = account_info.get('user_id', '')
        auth_time = middleware.bucketGet('sgxw_auth', username) or '未授权'
        
        # 添加新变量
        data = [{
            'name': env_name,
            'value': f"{env_value}",
            'remarks': f"上观UID：{user_id}|到期:{auth_time}"
        }]
        
        try:
            add_response = requests.post(f'{host}/open/envs', headers=headers, json=data, timeout=10)
            if add_response.status_code != 200:
                error_msg = f"添加变量失败: {add_response.text}"
                print(error_msg)
                return False, error_msg
                
            add_result = add_response.json()
            if add_result.get('code') != 200:
                error_msg = f"添加变量失败: {add_result.get('message')}"
                print(error_msg)
                return False, error_msg
                
            # 兼容不同版本的青龙面板
            new_id = None
            if 'data' in add_result and add_result['data'] and len(add_result['data']) > 0:
                new_id = add_result['data'][0].get('_id') or add_result['data'][0].get('id')
                
            if new_id:
                enable_response = requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id], timeout=10)
                if enable_response.status_code != 200:
                    print(f"启用变量失败: {enable_response.text}")
            else:
                print("未找到变量ID，跳过启用步骤")
                
            return True, "更新成功"
        except Exception as e:
            error_msg = f"添加变量异常: {str(e)}"
            print(error_msg)
            return False, error_msg
        
    except Exception as e:
        error_msg = f"更新青龙变量异常: {str(e)}"
        print(error_msg)
        return False, error_msg

def update_ql_env(username, account_info):
    """更新青龙环境变量"""
    password = account_info.get('password', '')
    user_id = account_info.get('user_id', '')
    remark = account_info.get('remark', '')
    
    if not password or not user_id:
        print(f"更新青龙变量失败: 账号信息不完整")
        return False
        
    # 格式化变量值: 备注#账号#密码
    env_value = f"{remark}#{username}#{password}"
    
    # 使用固定的变量名S_SGXW
    success, message = Addenvs(username, env_value, "S_SGXW", account_info)
    if not success:
        print(f"更新青龙变量失败: {message}")
    return success

def delete_ql_env(username, env_name="S_SGXW"):
    """删除青龙环境变量"""
    try:
        ql_config = middleware.bucketGet('sgxw_config', 'sgxw_qlname')
        if not ql_config:
            print("未配置青龙信息")
            return False
            
        # 将英文的"|"替换为中文的"丨"
        ql_config = ql_config.replace('|', '丨')
        host, client_id, client_secret = [x.strip() for x in ql_config.split('丨')]
        
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
            if env['name'] == env_name and username in env['value']:
                # 删除变量
                response = requests.delete(
                    f'{host}/open/envs',
                    headers=headers,
                    json=[env.get('_id') or env.get('id')]
                )
                if response.status_code == 200:
                    deleted = True
                    print(f"删除青龙变量成功: {env.get('_id') or env.get('id')}")
                else:
                    print(f"删除青龙变量失败: {response.text}")
                    
        return deleted
        
    except Exception as e:
        print(f"删除青龙变量异常: {str(e)}")
        return False 

def show_tutorial():
    """显示插件使用教程"""
    tutorial = """
=====上观新闻使用教程=====
1. 基本功能:
  • 上观登录: 绑定上观新闻账号
  • 上观查询: 查询账号信息和积分
  • 上观管理: 管理账号(授权/删除/提交青龙)
  • 上观授权: 管理员专用授权功能

2. 使用须知:
  • 账号需要先授权才能提交青龙
  • 支持微信支付和积分兑换两种授权方式
  • 授权后可自动同步至青龙环境变量

3. 账号绑定格式:
  • 备注#手机号#密码
  • 示例: 张三#13812345678#123456

4. 青龙提交格式:
  • 变量名: S_SGXW
  • 变量值: UID#账号#密码
  • 备注: 上观UID：xxxx|到期:yyyy-mm-dd

5. 如有问题请联系管理员
=================="""
    sender.reply(tutorial)

def check_order(order_id=None):
    """查询订单状态"""
    if not order_id:
        sender.reply("""
=====订单查询=====
请输入订单号
回复"q"退出操作
==================""")
        
        order_id = sender.input(120000, 1, False)
        if not order_id or order_id.lower() == 'q':
            sender.reply("✅ 已取消查询")
            return
            
    try:
        order_info = middleware.bucketGet('sgxw_order', order_id)
        if not order_info:
            sender.reply("""
=====查询结果=====
❌ 未找到订单信息
------------------
请确认订单号是否正确
==================""")
            return
            
        order_data = json.loads(order_info)
        sender.reply(f"""
=====订单详情=====
🔖 订单号: {order_id}
💰 金额: {order_data.get('amount', '未知')}元
⏱️ 时长: {order_data.get('months', '未知')}个月
📊 状态: {'已支付' if order_data.get('status') == 'success' else '未支付'}
==================""")
            
    except Exception as e:
        sender.reply(f"""
=====查询异常=====
❌ 错误: {str(e)}
==================""")

def ks_auth():
    """管理员授权功能"""
    # 检查管理员权限
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
        # 批量授权
        # 获取所有用户
        all_users = []
        for key in middleware.bucketKeys('sgxw_user'):
            userdata = middleware.bucketGet('sgxw_user', key)
            if userdata:
                user_accounts = eval(userdata)
                all_users.append({
                    'id': key,
                    'accounts': user_accounts
                })
                
        if not all_users:
            sender.reply("❌ 未找到任何用户")
            return
            
        sender.reply(f"✅ 共找到 {len(all_users)} 个用户，{sum(len(user['accounts']) for user in all_users)} 个账号")
        
        # 设置授权时长
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
                
            # 确认批量授权
            sender.reply(f"""
=====确认批量授权=====
⚠️ 将为全部 {sum(len(user['accounts']) for user in all_users)} 个账号授权 {months} 个月
------------------
回复 y 确认授权
回复 n 取消操作
==================""")
            
            confirm = sender.input(120000, 1, False)
            if confirm.lower() != 'y':
                sender.reply("✅ 已取消授权")
                return
                
            # 开始批量授权
            success_count = 0
            for user in all_users:
                for username in user['accounts']:
                    try:
                        account_info = json.loads(middleware.bucketGet('sgxw_token', username))
                        
                        # 获取当前授权状态
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('sgxw_auth', username)
                        
                        # 计算新的到期时间
                        if accountVip and accountVip > dqsj:
                            # 如果当前已有有效授权，从授权到期时间开始计算
                            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                        else:
                            # 如果没有有效授权，从当前时间开始计算
                            start_date = datetime.now()
                            
                        # 计算新的到期时间(按月计算，每月30天)
                        new_expire = start_date + timedelta(days=30*months)
                        new_expire = new_expire.strftime("%Y-%m-%d")
                        
                        # 更新授权时间
                        middleware.bucketSet('sgxw_auth', username, new_expire)
                        
                        # 更新青龙变量
                        update_ql_env(username, account_info)
                        success_count += 1
                    except Exception as e:
                        print(f"批量授权异常: {username}, 错误: {str(e)}")
            
            # 显示授权结果
            sender.reply(f"""
=====批量授权结果=====
📊 总账号: {sum(len(user['accounts']) for user in all_users)}个
✅ 成功: {success_count}个
❌ 失败: {sum(len(user['accounts']) for user in all_users) - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
            
    elif choice == '2':
        # 单独授权
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
            
        # 查找该用户的账号
        userdata = middleware.bucketGet('sgxw_user', target_id)
        if not userdata:
            sender.reply("❌ 未找到该用户")
            return
            
        user_accounts = eval(userdata)
        sender.reply(f"✅ 用户 {target_id} 有 {len(user_accounts)} 个账号")
        
        # 设置授权时长
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
                
            # 开始授权
            success_count = 0
            for username in user_accounts:
                try:
                    account_info = json.loads(middleware.bucketGet('sgxw_token', username))
                    
                    # 获取当前授权状态
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    accountVip = middleware.bucketGet('sgxw_auth', username)
                    
                    # 计算新的到期时间
                    if accountVip and accountVip > dqsj:
                        # 如果当前已有有效授权，从授权到期时间开始计算
                        start_date = datetime.strptime(accountVip, "%Y-%m-%d")
                    else:
                        # 如果没有有效授权，从当前时间开始计算
                        start_date = datetime.now()
                        
                    # 计算新的到期时间(按月计算，每月30天)
                    new_expire = start_date + timedelta(days=30*months)
                    new_expire = new_expire.strftime("%Y-%m-%d")
                    
                    # 更新授权时间
                    middleware.bucketSet('sgxw_auth', username, new_expire)
                    
                    # 更新青龙变量
                    update_ql_env(username, account_info)
                    success_count += 1
                except Exception as e:
                    print(f"授权异常: {username}, 错误: {str(e)}")
            
            # 显示授权结果
            sender.reply(f"""
=====授权结果=====
📊 总账号: {len(user_accounts)}个
✅ 成功: {success_count}个
❌ 失败: {len(user_accounts) - success_count}个
------------------
⏰ 授权: {months}个月
==================""")
                
        except ValueError:
            sender.reply("❌ 请输入有效的数字")
            return
    else:
        sender.reply("❌ 无效的选择")

# 主函数
def main():
    global randommanagecommand, randomquerycommand
    global randomsigncommand, sgxwVipmoney, sgxwcoin
    
    # 获取用户配置
    sgxw_osname, sgxw_qlname, randommanagecommand, randomquerycommand, randomsigncommand, sgxwVipmoney, sgxwcoin = get_user_content()
    
    # 获取用户消息
    usermessage = sender.getMessage()
    
    # 处理上观登录
    if '登录' in usermessage or '登陆' in usermessage:
        bind_account()
    # 处理上观查询
    elif '查询' in usermessage and ('上观' in usermessage or 'sgxw' in usermessage):
        query_accounts()
    # 处理上观管理
    elif '管理' in usermessage and ('上观' in usermessage or 'sgxw' in usermessage):
        manage_account()
    # 处理上观授权
    elif '上观授权' in usermessage:
        ks_auth()
    # 处理上观教程
    elif '上观教程' in usermessage:
        show_tutorial()
    # 处理清理上观
    elif '清理上观' in usermessage:
        if not sender.isAdmin():
            sender.reply("❌ 此功能仅限管理员使用")
            return
            
        # 清理过期账号
        expired_count = 0
        dqsj = datetime.now().strftime("%Y-%m-%d")
        
        for username in middleware.bucketKeys('sgxw_auth'):
            auth_time = middleware.bucketGet('sgxw_auth', username)
            if auth_time < dqsj:
                middleware.bucketDel('sgxw_auth', username)
                expired_count += 1
                
        sender.reply(f"✅ 已清理 {expired_count} 个过期账号")
    elif usermessage.startswith('SGXW_'):  # 查询订单
        order_result = check_order(usermessage)
        if order_result:
            sender.reply(order_result)
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()