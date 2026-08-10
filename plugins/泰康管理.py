# [title: 泰康管理]
# [language: python]
# [class: 工具类]
# [service: 203066880]
# [author: rujingxianghai]
# [rule: ^(泰康|tk)(登录|登陆)$|^登(录|陆)(泰康|tk)$|^(泰康|tk)(查询|管理|授权|检测|教程)$]
# [cron: 0 5 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://y.gtimg.cn/music/photo_new/T053M000002Qqrye0oyZSp.jpg]
# [version: 3.0]
# [public: true]
# [price: 3.88]
# [description: 泰康青龙变量管理插件<br>指令：泰康登录、泰康管理、泰康查询、泰康授权、泰康检测、泰康教程]

# [param: {"required":false,"key":"s_tkzx.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_tkzx.use_daipanel","bool":true,"placeholder":"","name":"使用呆呆面板","desc":"勾选使用呆呆面板，不勾选使用青龙面板"}]
# [param: {"required":false,"key":"s_tkzx.panel_group","bool":false,"placeholder":"例:泰康","name":"呆呆面板分组","desc":"填写后新增/更新变量时同步写入group字段，留空则不处理"}]
# [param: {"required":true,"key":"s_tkzx.osname","bool":false,"placeholder":"例:S_TKRS","name":"青龙变量名","desc":"青龙容器内泰康的变量名"}]
# [param: {"required":true,"key":"s_tkzx.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_tkzx.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_tkzx.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_tkzx.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]

import os
import json
import time
import hashlib
import random
import base64
import string
import requests
import uuid as uuid_module
from datetime import datetime, timedelta
import middleware
import vorto_utils
from vorto_utils import mask_account, check_auth_status
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 初始化
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_tkzx_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_tkzx', 'coin_key': 'dd_sign_points', 'name': '泰康'}


# ==================== 泰康API类 ====================

class TaikangOnline:
    """泰康在线API"""

    def __init__(self, union_id=None, open_id=None):
        self.base_url = "https://m.tk.cn"
        self.device_id = 'WC39ZUyXRgdExSj90tOeGomyOuuFeIVfnoBh4K6/N2S6+cPQvxZzEMpX4YkYGt7bl61lJVmGniEtWjSm22hAKQUL4jL6rQD4StL/WmrP2Tauiuo9Z2Nzm4Q==1487577677129'
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.8(0x13080812) XWEB/1216'
        self.session = requests.Session()
        self.union_id = union_id
        self.open_id = open_id
        self.account_name = mask_account(union_id) if union_id else "未知账户"

        self.session.headers.update({
            'Connection': 'keep-alive',
            'xweb_xhr': '1',
            'user-agent': self.user_agent,
            'accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://servicewechat.com/wx9e3e7020c4a10356/280/page-frame.html',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })

    def md5(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def generate_uuid(self):
        chars = "0123456789abcdef"
        u = [random.choice(chars) for _ in range(36)]
        u[14] = "4"
        u[19] = chars[3 & int(u[19], 16) | 8]
        u[8] = u[13] = u[18] = u[23] = "-"
        return ''.join(u)

    def encrypt(self, plain_text, key="EEue2kxI0oh2GBJh"):
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        padded_data = pad(plain_text.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        return encrypted.hex().upper()

    def get_sign(self):
        client_id = 'ytngbmji'
        non_str = self.generate_uuid()
        timestamp = int(time.time() * 1000)
        t = 60000 * (timestamp // 60000)
        md5_key = 'f2fc9b5e36E90745AB79'
        sign = self.md5(self.md5(f"{client_id}{non_str}{t}{md5_key}"))
        body = {"clientId": client_id, "nonStr": non_str, "timestamp": timestamp, "sign": sign}
        return self.encrypt(json.dumps(body), 'xdh3OmA5gEMMy0Mz')

    def get_f_sign(self):
        client_id = 'zehsmfluqja'
        timestamp = int(time.time() * 1000)
        non_str = str(timestamp) + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        t = 60000 * (timestamp // 60000)
        md5_key = 'd0ZGEyNGM4MmI3ODZOVE'
        sign = self.md5(self.md5(f"{client_id}{non_str}{t}{md5_key}"))
        body = {"clientId": client_id, "nonStr": non_str, "timestamp": timestamp, "sign": sign}
        return self.encrypt(json.dumps(body), 'xdh3OmA5gEMMy0Mz')

    def common_json_post(self, url, data):
        try:
            response = self.session.post(
                f"{self.base_url}{url}", json=data,
                headers={'content-type': 'application/json'}, timeout=30
            )
            time.sleep(2)
            return response.json()
        except:
            return None

    def common_json_sign_post(self, url, data):
        try:
            response = self.session.post(
                f"{self.base_url}{url}", json=data,
                headers={'content-type': 'application/json', 'Signature': self.get_sign()},
                timeout=30
            )
            time.sleep(2)
            return response.json()
        except:
            return None

    def common_text_post(self, url, data):
        try:
            response = self.session.post(
                f"{self.base_url}{url}", data=data,
                headers={'content-type': 'application/x-www-form-urlencoded'}, timeout=30
            )
            time.sleep(2)
            return response.json()
        except:
            return None

    def get_member_info(self, union_id):
        url = '/member_api/'
        params = f'api_s=member.userbind&api_m=selectwxbindbybindid&params=%7B%22platform%22%3A%22APPLET%22%2C%22fromid%22%3A%2271672%22%2C%22bindid%22%3A%22{union_id}%22%7D'
        response = self.common_text_post(url, params)
        if response and response.get('data'):
            return response['data'].get('token'), response['data'].get('memberid')
        return None, None

    def get_nickname(self, member_id, token):
        body = {"memberId": member_id, "token": token}
        response = self.common_json_post(
            '/activity_execute/rest/membergoldbean/getMemberGoldbeanNickName',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )
        if response and response.get('data'):
            return response['data'].get('nickName', '')
        return ''

    def get_points(self, member_id, token, nickname, open_id):
        body = {
            "memberid": member_id, "token": token, "coordinate": "",
            "platform": "WECHAT",
            "nickName": base64.b64encode(nickname.encode('utf-8')).decode('utf-8'),
            "openId": open_id, "fromid": "71672", "deviceId": self.device_id
        }
        response = self.common_json_sign_post(
            '/activity_execute/rest/membergoldbean/mainPage',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )
        if response and response.get('data'):
            return response['data'].get('allbeans', 0)
        return 0

    def get_points_info(self):
        try:
            token, member_id = self.get_member_info(self.union_id)
            if not token or not member_id:
                return None
            nickname = self.get_nickname(member_id, token)
            return self.get_points(member_id, token, nickname, self.open_id)
        except:
            return None

    def sign_in(self, member_id, token, union_id, nickname):
        body = {
            "memberid": member_id, "token": token, "unionid": union_id,
            "deviceId": self.device_id, "fromid": "71672", "platform": "WECHAT",
            "coordinate": "",
            "nickName": base64.b64encode(nickname.encode('utf-8')).decode('utf-8')
        }
        response = self.common_json_post(
            '/activity_execute/rest/membergoldbean/sign',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )
        if response and response.get('error_code') == 0:
            return True
        return False

    def walking_challenge(self, member_id, token):
        body = {
            "platform": "WECHAT", "memberId": member_id,
            "token": token, "openStatus": "Y"
        }
        self.common_json_sign_post(
            '/promotion/activity_execute/rest/springOuting/openChallenge',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )
        for task_num in ['dailyOneK', 'dailyFiveK', 'dailyTenK']:
            body = {
                "platform": "WECHAT", "memberId": member_id, "token": token,
                "fromId": "71672", "deviceId": self.device_id, "taskNum": task_num
            }
            self.common_json_sign_post(
                '/promotion/activity_execute/rest/springOuting/draw',
                {"enc": True, "encData": self.encrypt(json.dumps(body))}
            )

    def answer_question(self, member_id, token, union_id, open_id):
        body = {
            "memberId": member_id, "token": token, "unionId": union_id,
            "xcxOpenId": open_id, "fromId": "72474", "platform": "APPLET"
        }
        response = self.common_json_sign_post(
            '/promotion/activity_execute/rest/tk/answer/mainPage',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )
        if not response or not response.get('data'):
            return
        answer = response['data']['questionDetail']['answer']
        body = {
            "memberId": member_id, "token": token, "result": answer,
            "deviceId": self.device_id, "os": "weapp", "platform": "APPLET", "fromId": "72474"
        }
        self.common_json_sign_post(
            '/promotion/activity_execute/rest/tk/answer/answer',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )
        body = {
            "memberId": member_id, "token": token, "eventType": "ANSWER",
            "activityCode": "membergoldbean", "activityId": "",
            "assignmentId": "", "assignmentType": ""
        }
        self.common_json_post(
            '/activity_execute/rest/noseEvent/saveNoseEventLog',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )

    def execute_tasks(self, member_id, token):
        body = {"memberid": member_id, "token": token, "platform": "WECHAT"}
        response = self.common_json_post(
            '/activity_execute/rest/membergoldbean/queryTask',
            {"enc": True, "encData": self.encrypt(json.dumps(body))}
        )
        if not response or not response.get('data'):
            return
        for task in response['data']:
            if task.get('status') == "Y":
                continue
            body = {
                "memberId": member_id, "token": token,
                "eventType": task['taskCode'], "activityCode": "membergoldbean",
                "activityId": "", "assignmentId": "", "assignmentType": ""
            }
            self.common_json_post(
                '/activity_execute/rest/noseEvent/saveNoseEventLog',
                {"enc": True, "encData": self.encrypt(json.dumps(body))}
            )
            if task.get('taskToken'):
                self.common_json_post(
                    '/activity_execute/rest/callback/taskCallBack',
                    {"memberId": member_id, "taskToken": task['taskToken']}
                )


# ==================== 配置与面板操作 ====================

def get_user_content():
    osname = middleware.bucketGet('s_tkzx', 'osname') or 'S_TKRS'
    qlname = middleware.bucketGet('s_tkzx', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_tkzx', 'Vipmoney') or '1')
    coin = int(middleware.bucketGet('s_tkzx', 'coin') or '0')
    return osname, qlname, Vipmoney, coin


def _get_ql_client():
    """获取面板客户端，根据开关决定使用青龙或呆呆面板"""
    osname = middleware.bucketGet('s_tkzx', 'osname') or 'S_TKRS'
    qlname = middleware.bucketGet('s_tkzx', 'qlname') or ''
    use_dp = str(middleware.bucketGet('s_tkzx', 'use_daipanel') or '').lower() == 'true'

    if use_dp:
        return vorto_utils.DumbPanelClient(osname, qlname) if qlname else vorto_utils.DumbPanelClient(osname)
    else:
        return vorto_utils.QingLongClient(osname, qlname) if qlname else vorto_utils.QingLongClient(osname)


def update_ql_env(account, account_info):
    """更新面板环境变量（青龙/呆呆面板 通用）"""
    union_id = account_info.get('unionId', '')
    open_id = account_info.get('openId', '')
    if not union_id or not open_id:
        return False
    env_value = f'{union_id}#{open_id}'
    auth_time = middleware.bucketGet('s_tkzx_auth', account) or '未授权'
    panel_group = (middleware.bucketGet('s_tkzx', 'panel_group') or '').strip()
    ql = _get_ql_client()
    return ql.update_env(
        account, env_value,
        f"泰康:{mask_account(account)}|到期:{auth_time}",
        group=panel_group,
    )


def delete_ql_env(account):
    """删除面板环境变量（青龙/呆呆面板 通用）"""
    ql = _get_ql_client()
    return ql.delete_env(account)


# ==================== 核心功能 ====================

def bind_account():
    """绑定账号"""
    sender.reply(
        "=====泰康登录=====\n"
        "请输入泰康数据\n"
        "格式: unionId#openId\n"
        "------------------\n"
        "回复\"q\"退出\n"
        "=================="
    )
    input_data = sender.input(120000, 1, False)
    if not input_data:
        sender.reply("⏰ 操作超时")
        return
    if input_data.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    if '#' not in input_data or input_data.count('#') != 1:
        sender.reply(
            "=====格式错误=====\n"
            "❌ 请输入正确的数据格式\n"
            "格式: unionId#openId\n"
            "=================="
        )
        return

    parts = input_data.split('#')
    union_id = parts[0].strip()
    open_id = parts[1].strip()

    if not union_id or not open_id:
        sender.reply(
            "=====数据不完整=====\n"
            "❌ unionId和openId不能为空\n"
            "=================="
        )
        return

    # 验证数据有效性
    tk = TaikangOnline(union_id, open_id)
    member_info = tk.get_member_info(union_id)
    if not member_info or not member_info[0]:
        sender.reply(
            "=====数据无效=====\n"
            "❌ 无法验证数据有效性\n"
            "请检查unionId和openId是否正确\n"
            "=================="
        )
        return

    # 解析账号列表
    accounts = eval(uservalue) if uservalue else []
    is_new = union_id not in accounts

    # 保存token信息
    token_data = json.dumps({"unionId": union_id, "openId": open_id})
    middleware.bucketSet(bucket='s_tkzx_token', key=union_id, value=token_data)

    # 新账号加入列表
    if is_new:
        accounts.append(union_id)
        middleware.bucketSet(bucket='s_tkzx_user', key=userid, value=str(accounts))

    # 检查授权状态，已授权则提交青龙
    auth_time = middleware.bucketGet('s_tkzx_auth', union_id)
    ql_status = "⚠️ 未授权，未提交青龙"
    if auth_time and auth_time >= str(datetime.now().date()):
        try:
            account_info = json.loads(token_data)
            update_ql_env(union_id, account_info)
            ql_status = "✅ 已提交青龙"
        except:
            ql_status = "❌ 青龙提交失败"

    status = '添加' if is_new else '更新'
    sender.reply(
        f"=====绑定成功=====\n"
        f"📱 账号: {mask_account(union_id)}\n"
        f"🔐 状态: ✅ 已{status}\n"
        f"📦 青龙: {ql_status}\n"
        f"⏰ 发送 泰康管理 可管理账号\n"
        f"=================="
    )


def query_accounts():
    """查询账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 泰康登录 绑定\n==================")
        return

    accounts = eval(uservalue)

    # 账号选择
    account_list = "\n========选择账号=======\n[0] 全部账号"
    for i, account in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_tkzx_auth', account)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(account)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    # 解析选择
    try:
        if choice == '0':
            selected = accounts.copy()
        else:
            selected = [
                accounts[int(idx.strip()) - 1]
                for idx in choice.split(',')
                if idx.strip().isdigit() and 0 < int(idx.strip()) <= len(accounts)
            ]

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        sender.reply(f"✅ 已选择 {len(selected)} 个账号，正在查询...")

        for i, account in enumerate(selected, 1):
            try:
                token_data = middleware.bucketGet('s_tkzx_token', account)
                if not token_data:
                    sender.reply(f"=====查询失败=====\n❌ {mask_account(account)} 数据丢失\n==================")
                    continue
                account_info = json.loads(token_data)
                auth_time = middleware.bucketGet('s_tkzx_auth', account)
                if auth_time and auth_time >= str(datetime.now().date()):
                    auth_status = '✅ 已授权'
                else:
                    auth_status = '⚠️ 未授权' if not auth_time else '❌ 已过期'

                # 查询积分
                tk = TaikangOnline(account_info.get('unionId'), account_info.get('openId'))
                points = tk.get_points_info()
                points_text = f"\n💎 当前积分: {points}" if points is not None else ""

                sender.reply(
                    f"=====账号信息[{i}/{len(selected)}]=====\n"
                    f"📱 账号: {mask_account(account)}\n"
                    f"🏷 状态: {auth_status}\n"
                    f"📅 到期: {auth_time or '未授权'}{points_text}\n"
                    f"=================="
                )
            except Exception as e:
                sender.reply(f"=====查询失败=====\n❌ {mask_account(account)}: {str(e)}\n==================")

        sender.reply("✅ 查询完成")
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")


def manage_account():
    """管理账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

    accounts = eval(uservalue)
    osname, qlname, Vipmoney, coin = get_user_content()

    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交青龙\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    if choice == '1':
        # 授权账号 - 选择账号后进入支付流程
        account_list = "\n========选择账号=======\n[0] 全部账号"
        for i, account in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_tkzx_auth', account)
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            account_list += f"\n[{i}]{mask_account(account)}({auth_status})"
        account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
        sender.reply(account_list)

        acc_choice = sender.input(120000, 1, False)
        if not acc_choice or acc_choice.lower() == 'q':
            sender.reply("✅ 已退出")
            return

        if acc_choice == '0':
            selected = accounts.copy()
        else:
            selected = [
                accounts[int(idx.strip()) - 1]
                for idx in acc_choice.split(',')
                if idx.strip().isdigit() and 0 < int(idx.strip()) <= len(accounts)
            ]

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        # 收集账号信息
        account_infos = []
        for account in selected:
            try:
                token_data = middleware.bucketGet('s_tkzx_token', account)
                if token_data:
                    account_infos.append({
                        'account': account,
                        'info': json.loads(token_data)
                    })
            except:
                pass

        if not account_infos:
            sender.reply("❌ 没有有效账号")
            return

        # 输入授权月数
        sender.reply(
            f"✅ {len(account_infos)} 个有效账号\n"
            f"=====设置授权时长=====\n"
            f"请输入授权月数(如:1)\n"
            f"回复\"q\"退出\n"
            f"=================="
        )
        months_input = sender.input(120000, 1, False)
        if not months_input or months_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return

        try:
            months = int(months_input)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return
        except ValueError:
            sender.reply("❌ 请输入有效数字")
            return

        total_money = len(account_infos) * months * Vipmoney

        # 构建支付方式
        pay_config = vorto_utils.get_pay_config()
        available = []
        if pay_config['qr_pay_switch']:
            available.append(("扫码支付", "qrcode"))
        if pay_config['ma_pay_switch']:
            pay_types = pay_config.get('pay_types', {})
            if pay_types:
                for pay_key, pay_name in pay_types.items():
                    available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
        if coin > 0:
            available.append(("积分兑换", "coin"))

        if not available:
            sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
            return

        pay_menu = f"=====选择支付方式=====\n💰 总价: {total_money}元({len(account_infos)}个×{months}月×{Vipmoney}元)\n"
        for idx, (name, _) in enumerate(available, 1):
            pay_menu += f"[{idx}] {name}\n"
        pay_menu += "------------------\n回复数字选择\n回复\"q\"退出\n=================="
        sender.reply(pay_menu)

        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply("✅ 已取消")
            return

        try:
            pay_idx = int(pay_choice) - 1
            if pay_idx < 0 or pay_idx >= len(available):
                sender.reply("❌ 无效选择")
                return
        except ValueError:
            sender.reply("❌ 请输入数字")
            return

        pay_name, pay_type = available[pay_idx]
        paid = False

        if pay_type == "qrcode":
            paid = _process_qrcode_payment('泰康授权', months, total_money)
        elif pay_type.startswith("mapay_"):
            actual_type = pay_type.replace("mapay_", "")
            paid = _process_mapay_payment('泰康授权', months, total_money, actual_type)
        elif pay_type == "coin":
            total_coin = len(account_infos) * months * coin
            user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            if user_coins < total_coin:
                sender.reply(
                    f"=====积分不足=====\n"
                    f"❌ 当前: {user_coins}\n"
                    f"💰 需要: {total_coin}\n"
                    f"=================="
                )
                return
            middleware.bucketSet('dd_sign_points', userid, str(user_coins - total_coin))
            paid = True

        if not paid:
            return

        # 批量授权 - 收集结果后统一回复
        success_list = []
        fail_list = []
        for item in account_infos:
            try:
                account = item['account']
                info = item['info']
                new_expire = vorto_utils.calculate_auth_time('s_tkzx_auth', account, months=months)
                middleware.bucketSet('s_tkzx_auth', account, new_expire)
                update_ql_env(account, info)
                success_list.append(f"{mask_account(account)} → {new_expire}")
            except Exception as e:
                fail_list.append(f"{mask_account(item['account'])} {str(e)}")

        result = "=====授权完成=====\n"
        result += f"✅ 成功: {len(success_list)}个\n"
        if success_list:
            result += '\n'.join(success_list) + '\n'
        if fail_list:
            result += f"❌ 失败: {len(fail_list)}个\n"
            result += '\n'.join(fail_list) + '\n'
        result += "=================="
        sender.reply(result)

    elif choice == '2':
        # 删除账号
        account_list = "\n========选择账号======="
        for i, account in enumerate(accounts, 1):
            account_list += f"\n[{i}]{mask_account(account)}"
        account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
        sender.reply(account_list)

        del_choice = sender.input(120000, 1, False)
        if not del_choice or del_choice.lower() == 'q':
            sender.reply("✅ 已退出")
            return

        selected = [
            accounts[int(idx.strip()) - 1]
            for idx in del_choice.split(',')
            if idx.strip().isdigit() and 0 < int(idx.strip()) <= len(accounts)
        ]

        if not selected:
            sender.reply("❌ 未选择有效账号")
            return

        sender.reply(
            f"=====确认删除=====\n"
            f"⚠️ 将删除 {len(selected)} 个账号\n"
            f"此操作不可恢复！\n"
            f"[y] 确认删除\n"
            f"[n] 取消操作\n"
            f"=================="
        )
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() != 'y':
            sender.reply("✅ 已取消")
            return

        success_list = []
        fail_list = []
        for account in selected:
            try:
                delete_ql_env(account)
                middleware.bucketDel(bucket='s_tkzx_token', key=account)
                middleware.bucketDel(bucket='s_tkzx_auth', key=account)
                if account in accounts:
                    accounts.remove(account)
                success_list.append(mask_account(account))
            except Exception as e:
                fail_list.append(f"{mask_account(account)} {str(e)}")

        if accounts:
            middleware.bucketSet(bucket='s_tkzx_user', key=userid, value=str(accounts))
        else:
            middleware.bucketDel(bucket='s_tkzx_user', key=userid)

        result = "=====删除完成=====\n"
        result += f"✅ 成功: {len(success_list)}个\n"
        if fail_list:
            result += f"❌ 失败: {len(fail_list)}个\n"
            result += '\n'.join(fail_list) + '\n'
        result += "=================="
        sender.reply(result)

    elif choice == '3':
        # 提交青龙
        success_list = []
        fail_list = []
        for account in accounts:
            try:
                token_data = middleware.bucketGet('s_tkzx_token', account)
                if not token_data:
                    fail_list.append(f"{mask_account(account)} 数据丢失")
                    continue
                account_info = json.loads(token_data)
                auth_time = middleware.bucketGet('s_tkzx_auth', account)
                if not auth_time or auth_time < str(datetime.now().date()):
                    fail_list.append(f"{mask_account(account)} 未授权")
                    continue
                update_ql_env(account, account_info)
                success_list.append(mask_account(account))
            except Exception as e:
                fail_list.append(f"{mask_account(account)} {str(e)}")

        result = "=====提交完成=====\n"
        result += f"✅ 成功: {len(success_list)}个\n"
        if fail_list:
            result += f"❌ 失败: {len(fail_list)}个\n"
            result += '\n'.join(fail_list) + '\n'
        result += "=================="
        sender.reply(result)


# ==================== 支付功能 ====================

def _process_qrcode_payment(project, months, money):
    """收款码支付"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config['zsm']
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
        return False

    sender.reply(
        f"======扫码支付======\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)

    ddzf = sender.waitPay("q", 300000)
    if str(ddzf) == 'q':
        sender.reply('✅ 已取消')
        return False

    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
        if float(ddzf.get('Money') or ddzf.get('money', 0)) >= float(money):
            return True
        sender.reply("❌ 支付金额不足")
        return False
    except:
        sender.reply("❌ 支付验证失败")
        return False


def _process_mapay_payment(project, months, money, pay_type='alipay'):
    """码支付处理"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config['ma_pay_switch']:
        sender.reply("❌ 码支付功能未开启")
        return False

    try:
        out_trade_no = f"TKZX{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config['pay_types'].get(pay_type, '支付宝')

        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"💳 方式: {pay_type_name}\n"
            f"=================="
        )

        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)

        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False

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
                return False
            if mapay.is_paid(out_trade_no):
                sender.reply("✅ 支付成功！")
                return True

        sender.reply("❌ 支付超时")
        return False
    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False


# ==================== 教程 ====================

def show_tutorial():
    """显示教程"""
    sender.reply(
        '=====泰康教程=====\n'
        '用户指令:\n'
        '1. 泰康登录 - 绑定账号\n'
        '2. 泰康查询 - 查询积分和授权状态\n'
        '3. 泰康管理 - 授权、删除、提交面板\n'
        '4. 泰康教程 - 查看说明\n'
        '------------------\n'
        '管理员指令:\n'
        '1. 泰康授权 - 批量授权\n'
        '2. 泰康检测 - 检测过期并清理\n'
        '------------------\n'
        '绑定输入:\n'
        'unionId#openId\n'
        '=================='
    )


# ==================== 管理员功能 ====================

def ks_auth():
    """管理员授权"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return

    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择操作\n"
        "回复\"q\"退出"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理员授权")
        return

    if choice == '1':
        vorto_utils.admin_auth_all_accounts(
            sender, 's_tkzx_user', 's_tkzx_auth', 's_tkzx_token',
            update_ql_callback=update_ql_env
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender, 's_tkzx_user', 's_tkzx_auth', 's_tkzx_token',
            update_ql_callback=update_ql_env
        )
    else:
        sender.reply("❌ 无效的选择")


# ==================== 主入口 ====================

def main():
    """主入口"""
    msg = sender.getMessage()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and '泰康' in msg:
        query_accounts()
    elif '管理' in msg and '泰康' in msg:
        manage_account()
    elif '教程' in msg and '泰康' in msg:
        show_tutorial()
    elif '泰康授权' in msg:
        ks_auth()
    elif '泰康检测' in msg or '检测泰康' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        result = check_auth_status(
            's_tkzx', 's_tkzx_user', 's_tkzx_auth', 's_tkzx_token',
            '泰康', delete_ql_callback=delete_ql_env
        )
        sender.reply(result)
    elif sender.getImtype() == 'fake':
        try:
            result = check_auth_status(
                's_tkzx', 's_tkzx_user', 's_tkzx_auth', 's_tkzx_token',
                '泰康', delete_ql_callback=delete_ql_env
            )
            middleware.notifyMasters(result)
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
