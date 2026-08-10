# [title: 腾讯地图]
# [language: python]
# [class: 工具类]
# [author: rujingxianghai]
# [rule: ^(地图)(登录|登陆)$|^登(录|陆)(地图)$|^(地图)(查询|管理)$|^(查询|管理)(地图)$|^地图授权$|^地图教程$|^地图检测$|^地图一键运行$]
# [cron: 40 7 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://img-upload.vorto.cc/617ce0659fd516ddb62bf889e8a7c988.png]
# [version: 2.3]
# [public: true]
# [price: 5.88]
# [description: 腾讯地图现金毛，日0.1<br>指令：地图登录、管理、查询、授权、教程<br>内置签到抽奖提现功能<br>2.3：重构码支付/管理员授权/检测，统一走vorto_utils]
# [param: {"required":true,"key":"S_TXDT_CONFIG.sqje","bool":false,"placeholder":"例:6.6,不填为0元","name":"授权价格","desc":"授权价格(单位:元)/月"}]
# [param: {"required":true,"key":"S_TXDT_CONFIG.sqsj","bool":false,"placeholder":"例:30,不填为30天","name":"授权天数","desc":"授权天数，默认30天/月"}]
# [param: {"required":false,"key":"S_TXDT_CONFIG.coin","bool":false,"placeholder":"不填为关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数）"}]
# [param: {"required":false,"key":"S_TXDT_CONFIG.notify","bool":false,"placeholder":"例:qq,wx,tb 多个用英文逗号分隔","name":"通知渠道","desc":"配置检测通知推送渠道"}]
# [param: {"required":false,"key":"S_TXDT_CONFIG.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒，到期后自动清理"}]

import json
import time
import uuid
import hashlib
import random
import requests
from datetime import datetime, timedelta
import middleware
import vorto_utils

# 获取用户信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

# 数据桶配置
BUCKET_USER = 'S_TXDT_USER'  # 用户账号列表
BUCKET_TOKEN = 'S_TXDT_TOKEN'  # 账号token信息
BUCKET_AUTH = 'S_TXDT_AUTH'  # 账号授权信息
BUCKET_CONFIG = 'S_TXDT_CONFIG'  # 插件配置

# 获取用户绑定的账号
uservalue = middleware.bucketGet(bucket=BUCKET_USER, key=userid)

def get_config(key, default=''):
    """获取配置"""
    return middleware.bucketGet(BUCKET_CONFIG, key) or default

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
        resp = requests.post(
            'https://mmapgwh.map.qq.com/activity/v1/lottery/detail',
            headers=headers,
            json={'activity_id':1721983577,'game_id':3,'rule_id':'tencent_map_lottery'},
            timeout=10
        )
        return resp.status_code == 200 and resp.json().get('message') == 'ok'
    except:
        return False

def do_checkin(user_id):
    """执行签到"""
    try:
        headers = get_headers(user_id, '/activity/v1/checkin')
        resp = requests.post(
            'https://mmapgwh.map.qq.com/activity/v1/checkin',
            headers=headers,
            json={'activity_id':1721983577,'game_id':1},
            timeout=10
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
        resp = requests.post(
            'https://mmapgwh.map.qq.com/activity/v1/lottery/detail',
            headers=headers,
            json={'activity_id':1721983577,'game_id':3,'rule_id':'tencent_map_lottery'},
            timeout=10
        ).json()
        
        if resp['message'] != 'ok':
            return False, resp['message'], 0
        
        tickets = resp['data']['available_ticket_number']
        results = []
        
        for i in range(tickets):
            lottery_resp = requests.post(
                'https://mmapgwh.map.qq.com/activity/v1/lottery',
                headers=get_headers(user_id, '/activity/v1/lottery'),
                json={'activity_id':1721983577,'game_id':3},
                timeout=10
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
        resp = requests.post(
            'https://mmapgwh.map.qq.com/activity/v1/withdraw/home',
            headers=headers,
            json={'activity_id':1721983577,'game_id':4,'rule_id':'tencent_map_withdraw'},
            timeout=10
        ).json()
        
        if resp['message'] != 'ok':
            return False, resp['message'], 0, 0
        
        data = resp['data']
        coins = data['coins']/100
        withdrawable = data['withdrawable_amount']/100
        
        if data['withdrawable_amount'] >= data['current_withdraw_threshold']:
            withdraw_resp = requests.post(
                'https://mmapgwh.map.qq.com/activity/v1/withdraw',
                headers=get_headers(user_id, '/activity/v1/withdraw'),
                json={'activity_id':1721983577,'game_id':4},
                timeout=10
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
        resp = requests.post(
            'https://mmapgwh.map.qq.com/activity/v1/withdraw/home',
            headers=headers,
            json={'activity_id':1721983577,'game_id':4,'rule_id':'tencent_map_withdraw'},
            timeout=10
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
        resp = requests.post(
            'https://mmapgwh.map.qq.com/activity/v1/coins/history',
            headers=headers,
            json={'activity_id':1721983577,'state':'normal','last_id':''},
            timeout=10
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
                results.append(f"✅ {remark} ({vorto_utils.mask_account(user_id)}) - 已授权至{accountVip}")
            else:
                success_count += 1
                results.append(f"✅ {remark} ({vorto_utils.mask_account(user_id)}) - 登录成功，需授权")
            
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
[{i}]{vorto_utils.mask_account(user_id)}({remark}, {auth_status})"""
        except:
            account_list += f"""
[{i}]{vorto_utils.mask_account(user_id)}(信息异常)"""
    
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
🆔 账号: {vorto_utils.mask_account(user_id)}
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
🆔 账号: {vorto_utils.mask_account(user_id)}
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
🆔 账号: {vorto_utils.mask_account(user_id)}
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
[{i}]{vorto_utils.mask_account(user_id)}({remark}, {auth_status})"""
        except:
            account_list += f"""
[{i}]{vorto_utils.mask_account(user_id)}(信息异常)"""
    
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
            sender.reply(f"⚠️ 账号处理异常: {vorto_utils.mask_account(user_id)} - {str(e)}")

    if not account_infos:
        sender.reply("❌ 没有有效的账号可授权")
        return

    sender.reply(
        "=====设置授权时长=====\n"
        "请输入授权月数(如:1)\n"
        "------------------\n"
        "回复数字设置月数\n"
        "回复\"q\"退出操作\n"
        "=================="
    )

    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消授权")
        return

    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return

        sqje = float(get_config('sqje', '6.6'))
        sqsj = int(get_config('sqsj', '30'))
        coin = int(get_config('coin', '0'))
        total_money = len(account_infos) * months * sqje

        # Build available payment methods from Vorto config
        pay_config = vorto_utils.get_pay_config()
        pay_types = pay_config['pay_types']

        available = []
        if pay_config['qr_pay_switch']:
            available.append(("扫码支付", "qrcode"))
        if pay_config['ma_pay_switch']:
            if not pay_types:
                sender.reply("⚠️ 未配置码支付方式，请联系管理员在Vorto初始化中填写")
            else:
                for pay_key, pay_name in pay_types.items():
                    available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
        if coin > 0:
            available.append(("积分兑换", "coin"))

        if not available:
            sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
            return

        # Select payment method
        if len(available) == 1:
            selected_payment = available[0][1]
        else:
            payment_menu = (
                f"=====选择支付方式=====\n"
                f"📊 账号数量: {len(account_infos)}个\n"
                f"⏰ 授权时长: {months}月\n"
                f"💰 总金额: {total_money}元\n"
                f"------------------"
            )
            for i, (name, _) in enumerate(available, 1):
                if name == "积分兑换":
                    need_coin = coin * months * len(account_infos)
                    user_coin = middleware.bucketGet('dd_sign_points', userid) or '0'
                    payment_menu += f"\n[{i}] {name} ({need_coin}积分, 当前:{user_coin})"
                else:
                    payment_menu += f"\n[{i}] {name} ({total_money}元)"
            payment_menu += "\n------------------\n回复数字选择\n回复\"q\"退出\n=================="

            sender.reply(payment_menu)

            pay_choice = sender.input(120000, 1, False)
            if not pay_choice or pay_choice.lower() == 'q':
                sender.reply("✅ 已取消授权")
                return

            try:
                pay_index = int(pay_choice) - 1
                if 0 <= pay_index < len(available):
                    selected_payment = available[pay_index][1]
                else:
                    sender.reply("❌ 无效的选择")
                    return
            except:
                sender.reply("❌ 请输入有效的数字")
                return

        # Process payment
        if selected_payment == "coin":
            need_coin = coin * months * len(account_infos)
            user_coin = int(middleware.bucketGet('dd_sign_points', userid) or '0')

            if user_coin < need_coin:
                sender.reply(
                    f"=====积分不足=====\n"
                    f"❌ 当前积分: {user_coin}\n"
                    f"💡 需要积分: {need_coin}\n"
                    f"=================="
                )
                return

            middleware.bucketSet('dd_sign_points', userid, str(user_coin - need_coin))
            success_count = process_batch_authorization(account_infos, months, sqsj)

            sender.reply(
                f"=====支付成功=====\n"
                f"🎫 商品: 地图批量授权\n"
                f"💰 支付方式: 积分支付\n"
                f"💫 消耗积分: {need_coin}\n"
                f"💰 剩余积分: {user_coin - need_coin}\n"
                f"📊 成功: {success_count}/{len(account_infos)}个账号\n"
                f"=================="
            )

        elif selected_payment == "qrcode":
            pay_config_data = vorto_utils.get_pay_config()
            zsm = pay_config_data['zsm']
            if not zsm:
                sender.reply("❌ 未配置收款码，请联系管理员在Vorto初始化中配置")
                return

            sender.replyImage(zsm)
            sender.reply(
                f"=====扫码支付=====\n"
                f"🎫 商品: 地图批量授权\n"
                f"📊 账号数量: {len(account_infos)}个\n"
                f"⏰ 时长: {months}月\n"
                f"💰 总金额: {total_money}元\n"
                f"------------------\n"
                f"请使用微信扫码支付\n"
                f"回复\"q\"取消支付\n"
                f"=================="
            )

            ddzf = sender.waitPay("q", 300000)
            if str(ddzf) == 'q':
                sender.reply("✅ 已取消支付")
                return

            try:
                if isinstance(ddzf, str):
                    ddzf = json.loads(ddzf)
                money = float(ddzf.get('Money') or ddzf.get('money', 0))
                if money >= total_money:
                    success_count = process_batch_authorization(account_infos, months, sqsj)
                    sender.reply(
                        f"=====支付成功=====\n"
                        f"💰 金额: {money}元\n"
                        f"📊 成功: {success_count}/{len(account_infos)}个账号\n"
                        f"=================="
                    )
                else:
                    sender.reply(f"❌ 支付金额不足，应付{total_money}元，实付{money}元")
            except:
                sender.reply("❌ 支付验证失败")

        elif selected_payment.startswith("mapay_"):
            pay_type = selected_payment.replace("mapay_", "")
            pay_type_name = pay_types.get(pay_type, pay_type)
            amount = round(float(total_money), 2)
            out_trade_no = f"DT{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"

            sender.reply(
                f"=====码支付信息=====\n"
                f"🎫 商品: 腾讯地图批量授权\n"
                f"💰 金额: {amount}元\n"
                f"💳 方式: {pay_type_name}\n"
                f"=================="
            )

            try:
                mapay = vorto_utils.MaPayClient()
                order = mapay.create_order(float(amount), pay_type, out_trade_no, f"腾讯地图批量授权-{amount}", userid)

                if order.get('error'):
                    sender.reply(f"❌ 创建订单失败: {order.get('error')}")
                    return

                pay_url = order.get('pay_url')
                qr_url = vorto_utils.generate_qrcode_url(pay_url)
                sender.replyImage(qr_url)
                sender.reply(f'💳 请使用【{pay_type_name}】扫码支付\n⏰ 5分钟内完成支付\n输入"q"可取消')

                start_time = time.time()
                timeout = 300

                while time.time() - start_time < timeout:
                    user_input = sender.input(5000, 1, False)
                    if user_input and user_input.lower() == 'q':
                        sender.reply("✅ 已取消支付")
                        return
                    if mapay.is_paid(out_trade_no):
                        success_count = process_batch_authorization(account_infos, months, sqsj)
                        sender.reply(
                            f"=====支付成功=====\n"
                            f"🎫 商品: 腾讯地图批量授权\n"
                            f"💰 支付方式: {pay_type_name}\n"
                            f"💰 金额: {amount}元\n"
                            f"📊 成功: {success_count}/{len(account_infos)}个账号\n"
                            f"=================="
                        )
                        return

                sender.reply("❌ 支付超时")
            except Exception as e:
                sender.reply(f"❌ 支付异常: {str(e)}")

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
    """管理员授权功能（按天数授权）"""
    if not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 批量授权所有用户\n"
        "[2] 单独授权指定用户\n"
        "------------------\n"
        "回复数字选择功能\n"
        "回复\"q\"退出操作\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消操作")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(
            sender, BUCKET_USER, BUCKET_AUTH, BUCKET_TOKEN
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender, BUCKET_USER, BUCKET_AUTH, BUCKET_TOKEN
        )
    else:
        sender.reply("❌ 无效的选择")

def check_auth_status(is_cron=False):
    """检测所有账号的授权状态"""
    if not is_cron and not sender.isAdmin():
        sender.reply("❌ 此功能仅限管理员使用")
        return None

    try:
        result = vorto_utils.check_auth_status(
            BUCKET_CONFIG, BUCKET_USER, BUCKET_AUTH, BUCKET_TOKEN,
            '腾讯地图'
        )
        if not is_cron:
            sender.reply(result)
        return result
    except Exception as e:
        error_msg = f"❌ 检测失败: {str(e)}"
        if not is_cron:
            sender.reply(error_msg)
        return error_msg



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
• 地图检测 - 检测并清理过期账号
• 地图一键运行 - 运行所有账号
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
2. 进入签到活动页面
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
    
    elif '一键运行' in message:
        run_all_accounts()
    
    elif '教程' in message:
        show_tutorial()
    
    # 定时任务处理（放在最后）
    elif sender.getImtype() == 'fake':
        try:
            result = check_auth_status(is_cron=True)
            if result:
                middleware.notifyMasters(result)
        except:
            pass
