#[disable:false]
# [pin:false]
# [public:true] 
# [rule: ^提交步数$|^添加账号$|^查看账号$|^删除账号$]  # 仅保留步数相关命令
# [version: 1.0]  # 更新版本号
# [price: 0] 
# [author: 1668485780]
# [title: 步数]  # 修改标题
# [open_source: false]
# [cron: 18 9 * * *]
# [icon: ]
# [description: 功能：刷步数功能（支持账号管理）<br>更新：修复已知bug ]  # 更新功能描述

import middleware
import requests
import time
import random  # 用于随机生成步数

# 修改：从数据桶获取当前用户的账号列表（使用发送者ID作为key）
def get_accounts() -> list:
    """从数据桶获取当前用户的账号列表（使用发送者ID作为key）"""
    accounts = []
    # 使用当前用户ID作为数据桶的key
    user_id = sender.getUserID()
    account_data = middleware.bucketGet(bucket='dd_zepp_account', key=user_id)
    if not account_data:
        return accounts
    
    # 解析账号数据（格式：手机号1#密码1|手机号2#密码2|...）
    for line in account_data.split('|'):
        line = line.strip()
        if not line:
            continue
        try:
            mobile, password = line.split('#', 1)
            accounts.append((mobile, password))
        except:
            print(f"无效账号数据: {line}")
            continue
    return accounts

# 查看当前用户的账号列表
def handle_view_accounts():
    """查看当前用户的账号列表"""
    accounts = get_accounts()
    
    if not accounts:
        sender.reply("您还没有绑定任何账号\n💡 请发送\"添加账号\"命令添加账号")
        return
    
    reply = "=====账号列表=====\n"
    for i, (mobile, password) in enumerate(accounts, 1):
        reply += f"{i}. 账号: {mobile[:3]}****{mobile[-4:]}\n   密码: {'*' * len(password)}\n"
        if i < len(accounts):
            reply += "------------------\n"
    
    reply += f"==================\n共有 {len(accounts)} 个账号"
    sender.reply(reply)

def handle_delete_account():
    """删除指定账号（支持手机号/QQ邮箱）"""
    accounts = get_accounts()
    
    if not accounts:
        sender.reply("您还没有绑定任何账号\n💡 请发送\"添加账号\"命令添加账号")
        return
    
    # 优化账号显示
    reply = f"=====删除账号=====\n当前有 {len(accounts)} 个账号，请选择要删除的编号（1-{len(accounts)}）：\n"
    for i, (account, password) in enumerate(accounts, 1):
        masked_account = f"{account[:3]}****{account[-4:]}" if '@' not in account else f"{account.split('@')[0][:3]}****@{account.split('@')[1]}"
        reply += f"{i}. {masked_account}\n"
    reply += "0. 取消\n=================="
    sender.reply(reply)
    
    # 获取用户输入（修正参数顺序）
    choice = sender.input(60000, False, "请输入要删除的账号编号：")
    
    if not choice:
        return sender.reply("❌ 操作取消\n原因: 未输入选择或操作超时")
    
    try:
        choice_index = int(choice.strip())
        
        if choice_index == 0:
            return sender.reply("✅ 操作已取消")
            
        if 1 <= choice_index <= len(accounts):
            user_id = sender.getUserID()
            deleted_account = accounts.pop(choice_index - 1)
            
            # 更新数据桶（使用 bucketSet 替代 bucketDelete）
            if accounts:
                new_data = '|'.join([f"{acc}#{pwd}" for acc, pwd in accounts])
                middleware.bucketSet(bucket='dd_zepp_account', key=user_id, value=new_data)
            else:
                # 如果账号列表为空，将数据桶值设为空字符串
                middleware.bucketSet(bucket='dd_zepp_account', key=user_id, value="")
            
            # 生成脱敏后的删除账号信息
            deleted_masked = deleted_account[0]
            deleted_display = f"{deleted_masked[:3]}****{deleted_masked[-4:]}" if '@' not in deleted_masked else f"{deleted_masked.split('@')[0][:3]}****@{deleted_masked.split('@')[1]}"
            
            return sender.reply(f"✅ 已删除账号：{deleted_display}")
            
        else:
            return sender.reply(f"❌ 无效编号：{choice_index}，请输入1-{len(accounts)}之间的数字")
            
    except ValueError:
        return sender.reply(f"❌ 无效输入：{choice}，请输入有效数字")
    except Exception as e:
        return sender.reply(f"❌ 系统错误：{str(e)}")

# 更新步数（使用新接口）
def update_steps(account: str, password: str, steps: int) -> dict:
    """调用新接口更新步数"""
    url = "http://api.mmp.cc/api/ZeppLife"
    params = {"user": account, "pass": password, "count": steps}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {str(e)}")
        return {"success": False, "message": f"网络请求失败: {str(e)}"}

# 处理刷步数请求（适配实际接口返回格式）
def handle_step_update():
    """处理刷步数请求（支持自定义步数和选择账号）"""
    accounts = get_accounts()
    
    if not accounts:
        sender.reply("❌ 未找到有效的账号信息\n💡 请先发送\"添加账号\"命令添加账号")
        return
    
    # 让用户选择要刷步数的账号（支持多个编号，用逗号分隔）
    reply = "=====选择账号=====\n请输入要刷步数的账号编号（用逗号分隔，0=全部）：\n"
    for i, (account, password) in enumerate(accounts, 1):
        masked_account = f"{account[:3]}****{account[-4:]}" if '@' not in account else f"{account.split('@')[0][:3]}****@{account.split('@')[1]}"
        reply += f"{i}. {masked_account}\n"
    reply += "0. 全部账号\n"
    reply += "=================="
    sender.reply(reply)
    
    # 获取用户输入的多个编号
    account_choice = sender.input(60000, False, "请输入账号编号（0-全部，多个用逗号分隔）：")
    
    if not account_choice:
        sender.reply("❌ 操作取消\n原因: 未输入选择或操作超时")
        return
    
    try:
        # 解析多个编号（支持0或1,2,3格式）
        choices = account_choice.strip().split(',')
        selected_indices = []
        
        for choice in choices:
            idx = int(choice)
            if idx == 0:
                selected_indices = list(range(1, len(accounts)+1))  # 0代表全部账号，覆盖其他选择
                break
            if 1 <= idx <= len(accounts):
                selected_indices.append(idx)
        
        if not selected_indices and 0 not in [int(c) for c in choices]:  # 无有效选择
            raise ValueError("未选择有效账号编号")
        
        # 获取用户指定的步数
        sender.reply("=====刷步数=====\n请输入您想要的步数（直接回车使用默认随机值）：")
        step_input = sender.input(60000, False, "请输入步数：")
        
        if step_input:
            try:
                step_value = int(step_input)
                if step_value <= 0:
                    raise ValueError("步数必须大于0")
            except ValueError as e:
                sender.reply(f"❌ 无效输入: {str(e)}")
                return
        else:
            step_value = get_step_increase()  # 使用默认随机步数
            
        sender.reply(f"开始执行步数更新，步数: {step_value}...")
        
        # 确定要处理的账号列表（去重并排序）
        unique_indices = sorted(list(set(selected_indices)))
        accounts_to_process = []
        
        if 0 in [int(c) for c in choices]:  # 处理全部账号
            accounts_to_process = accounts
            sender.reply(f"将更新全部 {len(accounts)} 个账号的步数")
        else:
            for idx in unique_indices:
                accounts_to_process.append(accounts[idx-1])
            sender.reply(f"将更新选中的 {len(accounts_to_process)} 个账号的步数")
        
        # 遍历账号执行刷步数
        total_accounts = len(accounts_to_process)
        for index, (account, password) in enumerate(accounts_to_process, 1):
            sender.reply(f"处理账号 [{index}/{total_accounts}]: {account[:3]}****{account[-4:]}")
            result = update_steps(account, password, step_value)
            
            # 适配实际接口返回格式
            if result.get("code") == 200 and "提交步数成功" in result.get("msg", ""):
                sender.reply(f"✅ 步数更新成功: {result.get('msg', '操作成功')}")
            else:
                sender.reply(f"❌ 步数更新失败: {result.get('msg', '未知错误')}")
        
        sender.reply("所有选择的账号处理完毕")
        
    except ValueError as e:
        sender.reply(f"❌ 无效输入：{e}，请输入有效数字（如0或1,2,3）")
    except Exception as e:
        sender.reply(f"程序执行出错: {str(e)}")

# 交互式添加账号（使用发送者ID作为key）
def handle_add_account():
    """交互式添加账号密码（使用发送者ID作为key）"""
    sender.reply("=====添加账号=====\n请输入您的账号（手机号）：")
    account = sender.input(60000, 0, False)  # 等待用户输入账号，超时60秒
    
    if not account:
        sender.reply("❌ 操作取消\n原因: 未输入账号或操作超时")
        return
    
    sender.reply("请输入您的密码：")
    password = sender.input(60000, 0, True)  # 等待用户输入密码，超时60秒，密码隐藏显示
    
    if not password:
        sender.reply("❌ 操作取消\n原因: 未输入密码或操作超时")
        return
    
    # 获取当前用户ID作为数据桶的key
    user_id = sender.getUserID()
    
    # 获取现有账号数据 - 使用 dd_zepp_account 数据桶
    current_data = middleware.bucketGet(bucket='dd_zepp_account', key=user_id) or ""
    
    # 检查是否已存在相同账号
    for line in current_data.split('|'):
        if line.strip().startswith(f"{account}#"):
            sender.reply(f"❌ 该账号已存在: {account[:3]}****{account[-4:]}")
            return
    
    # 添加新账号（格式：手机号#密码|...）
    new_entry = f"{account}#{password}"
    if current_data:
        current_data += f"|{new_entry}"
    else:
        current_data = new_entry
    
    # 保存到数据桶 - 使用 dd_zepp_account 数据桶
    middleware.bucketSet(bucket='dd_zepp_account', key=user_id, value=current_data)
    
    sender.reply(f"""
✅ 账号添加成功
账号: {account[:3]}****{account[-4:]}
密码: {'*' * len(password)}
------------------
已加密保存到您的专属数据桶
""")

# 获取默认步数增量（仅在用户未输入时使用）
def get_step_increase() -> int:
    """获取默认步数增量（随机生成20000-30000之间的数值）"""
    return random.randint(20000, 30000)

# 创建Sender对象及变量声明
sender = middleware.Sender(middleware.getSenderID())
message = sender.getMessage()
userID = sender.getUserID()

# 主命令处理逻辑（仅保留步数相关命令）
if message == "提交步数":
    handle_step_update()
elif message == "添加账号":
    handle_add_account()
elif message == "查看账号":
    handle_view_accounts()
elif message == "删除账号":
    handle_delete_account()