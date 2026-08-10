#[title: 爱坤助手]
#[language: python]
#[service: 2565720211] 售后联系方式
#[disable:false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[author: ahhhahh]
#[rule: ^(爱坤|ik)登录$] 匹配规则，多个规则时向下依次写多个
#[rule: ^(爱坤|ik)签到$] 匹配规则，多个规则时向下依次写多个
#[rule: ^(爱坤|ik)查询$] 匹配规则，多个规则时向下依次写多个
#[rule: ^(爱坤|ik)管理$] 匹配规则，多个规则时向下依次写多个
#[rule: ^(爱坤|ik)一键签到$] 匹配规则，多个规则时向下依次写多个
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: ] 图标链接地址，请使用48像素的正方形图标，支持http和https
#[version: 2.3.3]版本号
#[public:true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
#[price: 0.00] 上架价格
#[description: 爱坤/ik登录，爱坤/ik签到，爱坤/ik查询。支持多账号管理，自动验证账号有效性。新增查询所有账号功能，输入0即可查询全部。如有问题请联系售后。更新接口] 使用方法尽量写具体

import asyncio
import requests
import json
import parsel
import middleware
import re
import base64
from typing import List, Dict

# 全局常量
BUCKET_NAME = "ahhh_ikuu_accounts"  # 数据桶名称

class IkuuAccount:
    """账号信息类"""
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password

class IkuuClient:
    """ikuuu客户端核心类"""
    def __init__(self, userid: str):
        self.userid = userid
        self.accounts = self.load_accounts()  # 加载用户账号列表

    def load_accounts(self) -> List[Dict]:
        """从数据桶加载账号列表"""
        data = middleware.bucketGet(BUCKET_NAME, self.userid) or "[]"
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return []

    def save_accounts(self) -> None:
        """保存账号列表到数据桶"""
        if not self.accounts:
            # 如果没有账号了，删除整个key
            middleware.bucketDel(BUCKET_NAME, self.userid)
        else:
            middleware.bucketSet(BUCKET_NAME, self.userid, json.dumps(self.accounts))

    def add_account(self, email: str, password: str) -> bool:
        """添加单个账号（自动去重）"""
        if any(account["email"] == email for account in self.accounts):
            return False  # 账号已存在
        self.accounts.append({"email": email, "password": password})
        self.save_accounts()
        return True

    def delete_account(self, index: int) -> (bool, Dict):
        """删除指定索引的账号（索引从1开始）"""
        if 1 <= index <= len(self.accounts):
            deleted = self.accounts.pop(index - 1)
            self.save_accounts()
            return True, deleted
        return False, None

    def get_account_menu(self) -> str:
        """生成账号列表菜单（美化版）"""
        if not self.accounts:
            return "📭 当前没有存储任何账号，请先添加哦~"
        menu = "📋 已保存账号列表：\n"
        for idx, account in enumerate(self.accounts, 1):
            menu += f"  {idx}. {account['email'][:3]}****{account['email'][-4:]}\n"
        return menu.strip()

def login_with_account(account: Dict) -> (requests.Session, str):
    """使用账号信息登录ikuuu并返回会话和结果消息"""
    session = requests.session()
    login_url = 'https://ikuuu.de/auth/login'
    header = {
        'origin': 'https://ikuuu.art',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/109.0.0.0 Safari/537.36'
    }
    data = {
        'email': account['email'],
        'passwd': account['password']
    }
    try:
        response = session.post(login_url, headers=header, data=data)
        result = json.loads(response.text)
        return session, result.get('msg', '登录失败')
    except Exception as e:
        return None, f'登录异常: {str(e)}'

def check_in(session):
    """使用已登录的session进行签到"""
    check_url = 'https://ikuuu.de/user/checkin'
    header = {
        'origin': 'https://ikuuu.art',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
    }
    try:
        check_result = json.loads(session.post(url=check_url, headers=header).text)
        return check_result['msg']
    except Exception as e:
        return f'签到失败: {str(e)}'


def decode_base64(str_b64):
    """解码Base64字符串，支持UTF-8编码和URL安全Base64"""
    try:
        # 处理可能的URL安全Base64
        str_b64 = str_b64.replace('-', '+').replace('_', '/')
        # 补充Base64填充
        padding = len(str_b64) % 4
        if padding:
            str_b64 += '=' * (4 - padding)
        # 解码并转换为字符串
        bytes_data = base64.b64decode(str_b64)
        return bytes_data.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Base64解码失败: {e}")
        return None

def query_flow(session):
    """使用已登录的session查询剩余流量，先解密再提取"""
    if not session:  # 增加对会话对象的检查
        return "会话对象不存在，无法查询流量"

    data_url = 'https://ikuuu.de/user'
    header = {
        'origin': 'https://ikuuu.art',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
        'referer': 'https://ikuuu.ch/auth/login'
    }
    try:
        data_response = session.get(url=data_url, headers=header)
        data_response.encoding = 'utf-8'  # 确保正确编码
        html = data_response.text
        

        # 提取Base64编码的数据
        match = re.search(r'var originBody\s*=\s*"([^"]+)"', html)
        if not match:
            return "未找到Base64编码数据"

        encoded_data = match.group(1)
        decoded_html = decode_base64(encoded_data)

        if not decoded_html:
            return "Base64数据解码失败"

        # 从解码后的HTML中提取流量信息
        selector = parsel.Selector(decoded_html)

        # 使用指定的CSS选择器
        flow_selector = "#app > div > div.main-content > section > div:nth-child(3) > div:nth-child(2) > div > div.card-wrap > div.card-body > span"
        flow_value = selector.css(f"{flow_selector}::text").extract_first()

        # 同时检查counter类
        if not flow_value:
            flow_value = selector.css("span.counter::text").extract_first()

        if flow_value:
            # 提取数字部分并添加单位
            flow_num = re.search(r'\d+\.\d+', flow_value)
            if flow_num:
                return f"{flow_num.group()} GB"
            return flow_value.strip()
        else:
            return "解码成功，但未找到流量信息"

    except Exception as e:
        return f'查询失败: {str(e)}'

async def handle_login(sender):
    """处理登录流程（验证账号有效性后保存）"""
    sender.reply("🔐 请输入邮箱（格式：xxx@xxx.com），输入Q取消~")
    email = sender.listen(timeout=60000)

    if not email or email.lower() == 'q':
        sender.reply("✅ 已取消操作啦~")
        return

    sender.reply("🔑 请输入密码，输入Q取消~")
    password = sender.listen(timeout=60000)

    if not password or password.lower() == 'q':
        sender.reply("✅ 已取消操作啦~")
        return

    # 验证账号有效性
    temp_account = {"email": email, "password": password}
    session, msg = login_with_account(temp_account)

    if msg == '登录成功':
        client = IkuuClient(sender.getUserID())
        if client.add_account(email, password):
            sender.reply(f"🎉 账号 {email[:3]}****{email[-4:]} 验证成功并已保存~")
        else:
            sender.reply(f"⚠️ 账号 {email} 已经存在咯~")
    else:
        sender.reply(f"❌ 账号或密码错误：{msg}")

async def handle_checkin(sender, all_accounts=False):
    """处理签到流程（支持全部或单个账号）"""
    client = IkuuClient(sender.getUserID())
    if not client.accounts:
        sender.reply("❌ 请先添加账号哦~")
        return

    if not all_accounts:
        # 单个签到
        sender.reply("🎁 请选择要签到的账号序号（0.签到所有账号）：")
        sender.reply(client.get_account_menu())
        selection = sender.listen(timeout=60000)
        try:
            index = int(selection)
            if index == 0:
                # 签到所有账号
                await handle_checkin(sender, all_accounts=True)
                return
            elif 1 <= index <= len(client.accounts):
                account = client.accounts[index - 1]
                session, msg = login_with_account(account)
                if session:
                    result = check_in(session)
                    sender.reply(f"🎊 账号 {account['email'][:3]}****{account['email'][-4:]} 签到结果：{result}")
                else:
                    sender.reply(f"❌ 账号 {account['email'][:3]}****{account['email'][-4:]} 登录失败：{msg}")
            else:
                sender.reply("❌ 无效的账号编号哦~")
        except:
            sender.reply("❌ 输入格式错误，请输入数字~")
    else:
        # 全部签到
        sender.reply("🚀 开始批量签到所有账号...")
        results = []

        for account in client.accounts:
            session, msg = login_with_account(account)
            if session:
                result = check_in(session)
                results.append(f"✅ {account['email'][:3]}****{account['email'][-4:]}: {result}")
            else:
                results.append(f"❌ {account['email'][:3]}****{account['email'][-4:]}: 登录失败 - {msg}")

        reply = "📊 全部账号签到结果汇总：\n" + "\n".join(results)
        success_count = sum(1 for r in results if r.startswith('✅'))
        total_count = len(results)
        reply += f"\n💡 成功: {success_count}/{total_count}"
        sender.reply(reply)

async def handle_query(sender):
    """处理流量查询，新增查询所有账号功能"""
    client = IkuuClient(sender.getUserID())
    if not client.accounts:
        sender.reply("❌ 请先添加账号哦~")
        return

    sender.reply("📊 请选择要查询的账号序号（0.查询所有账号）：")
    sender.reply(client.get_account_menu())
    selection = sender.listen(timeout=60000)
    try:
        index = int(selection)
        if index == 0:
            # 查询所有账号
            sender.reply("🔍 开始查询所有账号流量...")
            results = []
            for account in client.accounts:
                session, msg = login_with_account(account)
                if session:
                    flow = query_flow(session)
                    results.append(f"💡 {account['email'][:3]}****{account['email'][-4:]}: {flow}")
                else:
                    results.append(f"❌ {account['email'][:3]}****{account['email'][-4:]}: 登录失败 - {msg}")
            
            reply = "📊 所有账号流量查询结果：\n" + "\n".join(results)
            sender.reply(reply)
            return
            
        elif 1 <= index <= len(client.accounts):
            account = client.accounts[index - 1]
            session, msg = login_with_account(account)
            if session:
                flow = query_flow(session)
                sender.reply(f"💡 账号 {account['email'][:3]}****{account['email'][-4:]} 剩余流量：{flow}")
            else:
                sender.reply(f"❌ 账号 {account['email'][:3]}****{account['email'][-4:]} 登录失败：{msg}")
        else:
            sender.reply("❌ 无效的账号编号哦~")
    except:
        sender.reply("❌ 输入格式错误，请输入数字~")

async def handle_manage(sender):
    """处理账号管理"""
    client = IkuuClient(sender.getUserID())
    menu = """
🔧 账号管理中心 🔧
-----------------
0. 查看所有账号 📋
1. 添加账号 ➕
2. 删除账号 ➖
q. 取消操作 ❌
-----------------
请选择操作（输入数字或q）
"""
    sender.reply(menu)
    choice = sender.listen(timeout=60000)

    if choice == '0':
        # 查看所有账号
        sender.reply(client.get_account_menu())
        if len(client.accounts) > 0:
            sender.reply(f"ℹ️ 共 {len(client.accounts)} 个账号")
        return
    elif choice == '1':
        await handle_login(sender)
    elif choice == '2':
        if not client.accounts:
            sender.reply("❌ 没有可删除的账号哦~")
            return
        sender.reply(client.get_account_menu())
        sender.reply("🗑️ 请输入要删除的账号编号（输入q取消）")
        selection = sender.listen(timeout=60000)
        if not selection or selection.lower() == 'q':
            sender.reply("✅ 已取消操作啦~")
            return
        try:
            index = int(selection)
            success, deleted = client.delete_account(index)
            if success:
                sender.reply(f"🗑️ 账号 {deleted['email'][:3]}****{deleted['email'][-4:]} 已删除~")
                if not client.accounts:
                    sender.reply("💡 您的账号列表已清空，数据桶已自动删除")
            else:
                sender.reply(f"❌ 账号 {index} 不存在哦~")
        except:
            sender.reply("❌ 输入格式错误，请输入数字~")
    elif choice.lower() == 'q':
        sender.reply("✅ 已取消操作啦~")
    else:
        sender.reply("❌ 无效的操作选择，请重新输入~")

async def handle_one_key_signin(sender):
    """处理一键签到（管理员权限）"""
    if not sender.isAdmin():
        sender.reply("你没有权限执行此操作哦~❌")
        return
    # 获取所有账号数据
    sender.reply("开始执行一键签到啦~🚀")
    all_data = middleware.bucketAll(BUCKET_NAME)
    results = []
    for user_id, accounts_json in all_data.items():
        try:
            accounts = json.loads(accounts_json)
        except json.JSONDecodeError:
            continue
        for account in accounts:
            session, msg = login_with_account(account)
            if session:
                result = check_in(session)
                results.append(f"✅ {account['email']} 签到结果：{result}")
            else:
                results.append(f"❌ {account['email']} 登录失败：{msg}")
    # 汇总输出
    reply_message = "一键签到完成，结果如下：\n" + "\n".join(results)
    sender.reply(reply_message)

# 主程序
async def main():
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    content = sender.getMessage()

    # 指令匹配
    if re.match(r'^(爱坤|ik)登录$', content, re.IGNORECASE):
        await handle_login(sender)
    elif re.match(r'^(爱坤|ik)签到$', content, re.IGNORECASE):
        await handle_checkin(sender)
    elif re.match(r'^(爱坤|ik)查询$', content, re.IGNORECASE):
        await handle_query(sender)
    elif re.match(r'^(爱坤|ik)管理$', content, re.IGNORECASE):
        await handle_manage(sender)
    elif re.match(r'^(爱坤|ik)一键签到$', content, re.IGNORECASE):
        await handle_one_key_signin(sender)
    else:
        sender.reply("""
❌ 不支持的指令，请输入以下指令：
- (爱坤|ik)登录 📲
- (爱坤|ik)签到 📅
- (爱坤|ik)查询 📊
- (爱坤|ik)管理 🔧
""")

if __name__ == "__main__":
    asyncio.run(main())
    