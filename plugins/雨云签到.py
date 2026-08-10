# [title: 雨云签到]
# [language: python]
# [class: 工具类]
# [service: 2993959969] 售后联系方式
# [author: rujingxianghai] 作者
# [rule: ^(雨云|yy)(登录|登陆)$|^登(录|陆)(雨云|yy)$|^(雨云|yy)(查询|管理|授权|检测|教程)$|^(查询|管理)(雨云|yy)$]
# [cron: 45 6 * * *] cron定时
# [priority: 0] 优先级
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用平台
# [open_source: false]
# [icon: https://img-upload.vorto.cc/f5359ebff5c25a7d99acf466414d8f76.png]
# [version: 1.1]
# [public: true]
# [price: 2.88]
# [description: 雨云签到，每日自动签到领积分<br>指令：雨云登录、管理、查询、授权、检测、教程<br>1.1.0：按 AUT 规范重构，接入 vorto_utils，统一支付配置，支持 QingLong / DumbPanel]

import ast
import base64
import json
import random
import time
from datetime import datetime

import middleware
import requests
import vorto_utils

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_yy_user', key=userid)

PLUGIN_CONFIG = {
    'bucket': 's_yy',
    'coin_key': 'dd_sign_points',
    'name': '雨云',
}
PLUGIN_NAME = PLUGIN_CONFIG['name']
CONFIG_BUCKET = PLUGIN_CONFIG['bucket']
USER_BUCKET = 's_yy_user'
TOKEN_BUCKET = 's_yy_token'
AUTH_BUCKET = 's_yy_auth'
CURRENT_VERSION = "1.1.0"
PAY_TYPE_NAMES = {'alipay': '支付宝', 'wxpay': '微信支付', 'qqpay': 'QQ钱包'}
mask_account = vorto_utils.mask_account

# [param: {"required":false,"key":"s_yy.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用Vorto初始化配置"}]
# [param: {"required":false,"key":"s_yy.use_dumbpanel","bool":true,"placeholder":"","name":"使用呆呆面板","desc":"勾选使用呆呆面板，不勾选使用青龙面板"}]
# [param: {"required":false,"key":"s_yy.panel_group","bool":false,"placeholder":"例:雨云","name":"呆呆面板分组","desc":"填写后新增/更新变量时同步写入group字段，留空则不处理"}]
# [param: {"required":true,"key":"s_yy.osname","bool":false,"placeholder":"例:S_YYQD","name":"青龙变量名","desc":"青龙或呆呆面板内雨云签到变量名"}]
# [param: {"required":true,"key":"s_yy.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_yy.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_yy.proxy_api","bool":false,"placeholder":"http://proxy-api.com/get","name":"代理API","desc":"获取代理IP的API链接，返回格式 host:port"}]
# [param: {"required":false,"key":"s_yy.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_yy.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]


def get_user_content():
    """获取用户配置内容。"""
    osname = middleware.bucketGet(CONFIG_BUCKET, 'osname') or 'S_YYQD'
    qlname = middleware.bucketGet(CONFIG_BUCKET, 'qlname') or ''
    vip_money = float(middleware.bucketGet(CONFIG_BUCKET, 'Vipmoney') or '1')
    coin_raw = middleware.bucketGet(CONFIG_BUCKET, 'coin') or '0'
    return osname, qlname, '雨云管理', '雨云查询', '雨云登录', vip_money, int(coin_raw)


def parse_batch_accounts(input_text):
    """解析批量登录输入，格式为 账号#密码。"""
    accounts = []
    for line in input_text.strip().splitlines():
        line = line.strip()
        if not line or '#' not in line:
            continue
        username, password = line.split('#', 1)
        username = username.strip()
        password = password.strip()
        if username and password:
            accounts.append({'username': username, 'password': password})
    return accounts


def load_user_accounts(user_id=None):
    """读取用户绑定账号列表。"""
    target_user = str(user_id or userid)
    raw_value = middleware.bucketGet(USER_BUCKET, target_user)
    if not raw_value:
        return []

    try:
        data = ast.literal_eval(raw_value)
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
    except Exception:
        pass
    return []


def save_user_accounts(accounts, user_id=None):
    """保存用户绑定账号列表。"""
    target_user = str(user_id or userid)
    cleaned = []
    for account in accounts:
        account = str(account).strip()
        if account and account not in cleaned:
            cleaned.append(account)

    if cleaned:
        middleware.bucketSet(USER_BUCKET, target_user, str(cleaned))
    else:
        middleware.bucketDel(USER_BUCKET, target_user)


def load_account_info(username):
    """读取单个账号信息。"""
    raw_value = middleware.bucketGet(TOKEN_BUCKET, username)
    if not raw_value:
        return None

    try:
        data = json.loads(raw_value)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def build_env_value(account_info):
    """构造面板环境变量值。"""
    username = str(account_info.get('username', '')).strip()
    password = str(account_info.get('password', '')).strip()
    if not username or not password:
        return ''
    return f"{username}#{password}"


def is_valid_auth(auth_time):
    """判断授权是否仍有效。"""
    if not auth_time:
        return False
    try:
        expire_date = datetime.strptime(str(auth_time), "%Y-%m-%d").date()
        return expire_date >= datetime.now().date()
    except Exception:
        return False


def render_batch_result(title, success_list=None, fail_list=None, warn_list=None, extra_lines=None):
    """生成批量操作统一回执。"""
    success_list = success_list or []
    fail_list = fail_list or []
    warn_list = warn_list or []
    extra_lines = extra_lines or []

    result = f"====={title}=====\n"
    result += f"✅ 成功: {len(success_list)}个\n"
    if success_list:
        result += "\n".join(success_list) + "\n"
    if warn_list:
        result += f"⚠️ 注意: {len(warn_list)}项\n"
        result += "\n".join(warn_list) + "\n"
    if fail_list:
        result += f"❌ 失败: {len(fail_list)}个\n"
        result += "\n".join(fail_list) + "\n"
    if extra_lines:
        result += "\n".join(extra_lines) + "\n"
    result += "=================="
    return result


def _get_ql_client():
    """获取面板客户端，根据开关决定使用青龙或呆呆面板。"""
    osname = middleware.bucketGet(CONFIG_BUCKET, 'osname') or 'S_YYQD'
    qlname = middleware.bucketGet(CONFIG_BUCKET, 'qlname') or ''
    use_dp = str(middleware.bucketGet(CONFIG_BUCKET, 'use_dumbpanel') or '').lower() == 'true'

    if use_dp:
        return vorto_utils.DumbPanelClient(osname, qlname) if qlname else vorto_utils.DumbPanelClient(osname)
    return vorto_utils.QingLongClient(osname, qlname) if qlname else vorto_utils.QingLongClient(osname)


def update_ql_env(username, account_info):
    """更新面板环境变量（青龙 / 呆呆面板通用）。"""
    env_value = build_env_value(account_info)
    if not env_value:
        return False

    auth_time = middleware.bucketGet(AUTH_BUCKET, username) or '未授权'
    panel_group = (middleware.bucketGet(CONFIG_BUCKET, 'panel_group') or '').strip()
    ql = _get_ql_client()
    return ql.update_env(
        username,
        env_value,
        f"雨云:{username}|到期:{auth_time}",
        group=panel_group,
    )


def delete_ql_env(username):
    """删除面板环境变量（青龙 / 呆呆面板通用）。"""
    return _get_ql_client().delete_env(username)


class RainyunAPI:
    """雨云 API 客户端。"""

    BASE_URL = "https://api.v2.rainyun.com"
    TEST_URL = "http://www.baidu.com"

    def __init__(self):
        self.session = requests.Session()
        self.csrf_token = None
        self.proxy_api_url = middleware.bucketGet(CONFIG_BUCKET, 'proxy_api') or ''
        self._set_proxy()

    def test_proxy(self, proxy_url):
        """测试代理是否可用。"""
        try:
            proxies = {
                'http': f'http://{proxy_url}',
                'https': f'http://{proxy_url}',
            }
            response = requests.get(self.TEST_URL, proxies=proxies, timeout=10)
            return response.status_code == 200
        except Exception:
            return False

    def _set_proxy(self):
        """从代理 API 获取代理并设置到会话。"""
        if not self.proxy_api_url:
            return

        try:
            response = requests.get(self.proxy_api_url, timeout=10)
            response.raise_for_status()
            proxy_address = response.text.strip()
            if not proxy_address:
                return

            if self.test_proxy(proxy_address):
                self.session.proxies = {
                    'http': f'http://{proxy_address}',
                    'https': f'http://{proxy_address}',
                }
        except Exception:
            pass

    def login(self, username, password):
        """登录雨云账号。"""
        try:
            response = self.session.post(
                f"{self.BASE_URL}/user/login",
                headers={"Content-Type": "application/json"},
                data=json.dumps({"field": username, "password": password}),
                timeout=10,
            )
            result = response.json()
            if result.get('code') == 200:
                self.csrf_token = response.cookies.get_dict().get('X-CSRF-Token')
                return True, result.get('message') or result.get('msg') or '登录成功'
            return False, result.get('message') or result.get('msg') or '登录失败'
        except Exception as exc:
            return False, f"登录异常: {str(exc)}"

    def get_user_info(self):
        """获取用户信息。"""
        if not self.csrf_token:
            return False, "未获取到 csrf_token"

        try:
            response = self.session.get(
                f"{self.BASE_URL}/user/?no_cache=false",
                headers={
                    "Content-Type": "application/json",
                    "x-csrf-token": self.csrf_token,
                },
                timeout=10,
            )
            result = response.json()
            if result.get('code') == 200:
                return True, result.get('data', {})
            return False, result.get('message') or result.get('msg') or '获取失败'
        except Exception as exc:
            return False, str(exc)


def yy_login(username, password):
    """雨云登录兼容函数。"""
    api = RainyunAPI()
    success, message = api.login(username, password)
    if success:
        return True, api, message
    return False, None, message


def yy_userinfo(username, api, csrf_token=None):
    """雨云用户信息兼容函数。"""
    if isinstance(api, RainyunAPI):
        return api.get_user_info()
    return False, "API对象无效"


def bind_account():
    """绑定账号。"""
    sender.reply(
        "=====雨云登录=====\n"
        "请输入账号信息\n"
        "格式: 账号#密码\n"
        "------------------\n"
        "支持批量登录(换行分隔)\n"
        "回复\"q\"退出\n"
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("⏰ 操作超时")
        return
    if input_text.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    account_list = parse_batch_accounts(input_text)
    if not account_list:
        sender.reply("❌ 未检测到有效账号\n格式: 账号#密码")
        return

    sender.reply(f"🔄 正在登录 {len(account_list)} 个账号...")

    bound_accounts = load_user_accounts()
    success_list = []
    fail_list = []
    warn_list = []
    success_accounts = []

    for account in account_list:
        username = account['username']
        password = account['password']
        success, _, message = yy_login(username, password)
        if not success:
            fail_list.append(f"{mask_account(username)} {message}")
            continue

        if username not in bound_accounts:
            bound_accounts.append(username)

        account_info = {
            'username': username,
            'password': password,
            'version': CURRENT_VERSION,
        }
        middleware.bucketSet(TOKEN_BUCKET, username, json.dumps(account_info, ensure_ascii=False))
        success_accounts.append({'username': username, 'info': account_info})
        success_list.append(f"{mask_account(username)} 登录成功")

    save_user_accounts(bound_accounts)

    panel_client = _get_ql_client()
    panel_configured = panel_client.is_configured()
    already_authed_count = 0
    need_auth = []

    for account in success_accounts:
        username = account['username']
        auth_time = middleware.bucketGet(AUTH_BUCKET, username)
        if is_valid_auth(auth_time):
            already_authed_count += 1
            if panel_configured and not update_ql_env(username, account['info']):
                warn_list.append(f"{mask_account(username)} 已授权，但面板同步失败")
        else:
            need_auth.append(username)

    extra_lines = []
    if already_authed_count:
        if panel_configured:
            extra_lines.append(f"🔄 已授权并尝试同步: {already_authed_count}个")
        else:
            extra_lines.append(f"🔄 已授权账号: {already_authed_count}个（当前未配置面板，同步已跳过）")
    if need_auth:
        extra_lines.append(f"📋 待授权: {len(need_auth)}个")

    sender.reply(render_batch_result("登录完成", success_list, fail_list, warn_list, extra_lines))

    if need_auth:
        sender.reply(f"📋 检测到 {len(need_auth)} 个账号尚未授权，进入授权流程")
        authorize_multiple_accounts(need_auth)


def query_accounts():
    """查询账号信息。"""
    _, selected = vorto_utils.select_accounts(sender, USER_BUCKET, str(userid), AUTH_BUCKET, PLUGIN_NAME)
    if not selected:
        return

    sender.reply(f"✅ 已选择 {len(selected)} 个账号，正在查询...")
    for index, username in enumerate(selected, 1):
        account_info = load_account_info(username)
        auth_time = middleware.bucketGet(AUTH_BUCKET, username)
        auth_status = '已授权' if is_valid_auth(auth_time) else '未授权'
        user_info_text = ""

        if not account_info:
            user_info_text = "\n⚠️ 本地账号信息缺失"
        else:
            login_success, api, message = yy_login(username, account_info.get('password', ''))
            if login_success:
                info_success, user_data = yy_userinfo(username, api)
                if info_success:
                    points = int(user_data.get('Points', 0) or 0)
                    cash_amount = round(points / 2000, 2)
                    user_info_text = (
                        f"\n💰 积分: {points} (≈{cash_amount}元现金)"
                        f"\n📊 换算: 2000积分 = 1元"
                    )
                else:
                    user_info_text = f"\n⚠️ 获取用户信息失败: {user_data}"
            else:
                user_info_text = f"\n⚠️ 登录失败: {message}"

        sender.reply(
            f"=====账号信息[{index}/{len(selected)}]=====\n"
            f"📱 账号: {mask_account(username)}\n"
            f"🏷 状态: {auth_status}\n"
            f"📅 到期: {auth_time or '未授权'}{user_info_text}\n"
            f"=================="
        )

    sender.reply("✅ 查询完成")


def manage_account():
    """管理账号。"""
    if not load_user_accounts():
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

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

    _, selected = vorto_utils.select_accounts(sender, USER_BUCKET, str(userid), AUTH_BUCKET, PLUGIN_NAME)
    if not selected:
        return

    sender.reply(f"✅ 已选择 {len(selected)} 个账号")

    if choice == '1':
        authorize_multiple_accounts(selected)
        return

    if choice == '2':
        sender.reply(
            "=====确认删除=====\n"
            "⚠️ 此操作不可恢复\n"
            "回复 y 确认删除\n"
            "=================="
        )
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() != 'y':
            sender.reply("✅ 已取消")
            return

        current_accounts = load_user_accounts()
        success_list = []
        fail_list = []
        for username in selected:
            try:
                if username in current_accounts:
                    current_accounts.remove(username)
                middleware.bucketDel(TOKEN_BUCKET, username)
                middleware.bucketDel(AUTH_BUCKET, username)
                delete_ql_env(username)
                success_list.append(mask_account(username))
            except Exception as exc:
                fail_list.append(f"{mask_account(username)} {str(exc)}")

        save_user_accounts(current_accounts)
        sender.reply(render_batch_result("删除完成", success_list, fail_list))
        return

    if choice == '3':
        panel_client = _get_ql_client()
        success_list = []
        fail_list = []
        extra_lines = []

        if not panel_client.is_configured():
            extra_lines.append("⚠️ 未配置面板容器，请先在插件配置或 Vorto初始化 中补全配置")

        for username in selected:
            account_info = load_account_info(username)
            auth_time = middleware.bucketGet(AUTH_BUCKET, username)

            if not account_info:
                fail_list.append(f"{mask_account(username)} 本地账号信息缺失")
                continue
            if not is_valid_auth(auth_time):
                fail_list.append(f"{mask_account(username)} 未授权或已过期")
                continue
            if update_ql_env(username, account_info):
                success_list.append(f"{mask_account(username)} → {auth_time}")
            else:
                fail_list.append(f"{mask_account(username)} 面板同步失败")

        sender.reply(render_batch_result("提交结果", success_list, fail_list, extra_lines=extra_lines))
        return

    sender.reply("❌ 无效选择")


def authorize_multiple_accounts(usernames):
    """批量授权账号，符合 AUT 批量回执规范。"""
    account_infos = []
    for username in usernames:
        account_info = load_account_info(username)
        if account_info:
            account_infos.append({'username': username, 'info': account_info})

    if not account_infos:
        sender.reply("❌ 没有有效账号")
        return

    sender.reply(
        f"✅ {len(account_infos)} 个有效账号\n"
        "=====设置授权时长=====\n"
        "请输入授权月数(如:1)\n"
        "回复\"q\"退出\n"
        "=================="
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

    vip_money = float(middleware.bucketGet(CONFIG_BUCKET, 'Vipmoney') or '1')
    coin_price = int(middleware.bucketGet(CONFIG_BUCKET, 'coin') or '0')
    total_money = round(len(account_infos) * months * vip_money, 2)

    pay_config = vorto_utils.get_pay_config()
    available = []
    if pay_config.get('qr_pay_switch'):
        available.append(("扫码支付", "qrcode"))
    if pay_config.get('ma_pay_switch'):
        for pay_key, pay_name in (pay_config.get('pay_types') or {}).items():
            available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
    if coin_price > 0:
        available.append(("积分兑换", "coin"))

    if not available:
        sender.reply("❌ 未配置支付方式，请联系管理员在 Vorto初始化 中开启")
        return

    if len(available) == 1:
        _, pay_type = available[0]
    else:
        menu = (
            "=====选择支付方式=====\n"
            f"📊 账号: {len(account_infos)}个\n"
            f"⏰ 时长: {months}月\n"
            f"💰 金额: {total_money}元\n"
            "------------------------"
        )
        for index, (name, _) in enumerate(available, 1):
            menu += f"\n[{index}] {name}"
        menu += "\n------------------------\n回复数字选择\n=================="
        sender.reply(menu)

        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply("✅ 已取消")
            return

        try:
            pay_index = int(pay_choice) - 1
            if not 0 <= pay_index < len(available):
                sender.reply("❌ 无效选择")
                return
            _, pay_type = available[pay_index]
        except ValueError:
            sender.reply("❌ 请输入有效数字")
            return

    total_coin = len(account_infos) * months * coin_price
    deducted_coin = False
    original_coin_balance = 0

    if pay_type == 'qrcode':
        if not process_qrcode_payment(PLUGIN_NAME, months, total_money):
            return
    elif pay_type.startswith('mapay_'):
        if not process_mapay_payment(PLUGIN_NAME, months, total_money, pay_type.replace('mapay_', '')):
            return
    elif pay_type == 'coin':
        original_coin_balance = int(middleware.bucketGet(PLUGIN_CONFIG['coin_key'], str(userid)) or '0')
        if original_coin_balance < total_coin:
            sender.reply(
                "=====积分不足=====\n"
                f"❌ 当前: {original_coin_balance}\n"
                f"💰 需要: {total_coin}\n"
                "=================="
            )
            return
        middleware.bucketSet(PLUGIN_CONFIG['coin_key'], str(userid), str(original_coin_balance - total_coin))
        deducted_coin = True

    panel_client = _get_ql_client()
    panel_configured = panel_client.is_configured()
    success_list = []
    fail_list = []
    warn_list = []

    for item in account_infos:
        username = item['username']
        account_info = item['info']
        try:
            new_expire = vorto_utils.calculate_auth_time(AUTH_BUCKET, username, months=months)
            middleware.bucketSet(AUTH_BUCKET, username, new_expire)
            if panel_configured:
                if update_ql_env(username, account_info):
                    success_list.append(f"{mask_account(username)} → {new_expire}")
                else:
                    success_list.append(f"{mask_account(username)} → {new_expire}")
                    warn_list.append(f"{mask_account(username)} 已授权，但面板同步失败")
            else:
                success_list.append(f"{mask_account(username)} → {new_expire}")
        except Exception as exc:
            fail_list.append(f"{mask_account(username)} {str(exc)}")

    if deducted_coin and not success_list and not warn_list:
        middleware.bucketSet(PLUGIN_CONFIG['coin_key'], str(userid), str(original_coin_balance))

    extra_lines = []
    if deducted_coin:
        remain_points = int(middleware.bucketGet(PLUGIN_CONFIG['coin_key'], str(userid)) or '0')
        extra_lines.append(f"🪙 剩余积分: {remain_points}")
    if not panel_configured:
        extra_lines.append("⚠️ 当前未配置面板，本次仅完成本地授权，可后续在“雨云管理 -> 提交青龙”同步")

    sender.reply(render_batch_result("授权完成", success_list, fail_list, warn_list, extra_lines))


def authorize_account(username, account_info):
    """单账号授权复用批量逻辑。"""
    authorize_multiple_accounts([username])


def process_authorization(username, account_info, months):
    """兼容旧调用：单账号授权。"""
    try:
        new_expire = vorto_utils.calculate_auth_time(AUTH_BUCKET, username, months=months)
        middleware.bucketSet(AUTH_BUCKET, username, new_expire)
        panel_client = _get_ql_client()
        if panel_client.is_configured():
            return update_ql_env(username, account_info)
        return True
    except Exception:
        return False


def process_coin_payment(username, account_info, months, coin_per_month):
    """兼容旧调用：单账号积分授权。"""
    return vorto_utils.process_coin_payment(
        sender,
        userid,
        AUTH_BUCKET,
        username,
        account_info,
        months,
        int(coin_per_month),
        auth_callback=lambda acc, info, m: process_authorization(acc, info, m),
    )


def generate_iframe_url(url):
    """将 URL 转为 iframe 页面链接。"""
    try:
        encoded = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        return f"https://metwhale.github.io?u={encoded}"
    except Exception:
        return url


def process_qrcode_payment(project, months, money):
    """扫码支付处理，配置读取自 Vorto初始化。"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config.get('zsm', '')
    if not pay_config.get('qr_pay_switch') or not zsm:
        sender.reply("❌ 未配置扫码支付，请联系管理员在 Vorto初始化 中开启")
        return False

    sender.reply(
        "======扫码支付======\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        "=================="
    )
    sender.replyImage(zsm)

    ddzf = sender.waitPay("q", 300000)
    if str(ddzf) == 'q':
        sender.reply("✅ 已取消")
        return False

    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
        paid_money = float(ddzf.get('Money') or ddzf.get('money', 0))
        if paid_money >= float(money):
            return True
        sender.reply("❌ 支付金额不足")
        return False
    except Exception:
        sender.reply("❌ 支付验证失败")
        return False


def process_mapay_payment(project, months, money, pay_type='alipay'):
    """码支付处理，配置读取自 Vorto初始化。"""
    if float(money) == 0:
        return True

    pay_config = vorto_utils.get_pay_config()
    if not pay_config.get('ma_pay_switch'):
        sender.reply("❌ 码支付功能未开启")
        return False

    pay_type_name = (pay_config.get('pay_types') or {}).get(pay_type, PAY_TYPE_NAMES.get(pay_type, pay_type))
    out_trade_no = f"YY{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"

    try:
        sender.reply(
            "=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"💳 方式: {pay_type_name}\n"
            "=================="
        )

        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)
        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False

        pay_url = order.get('pay_url')
        if not pay_url:
            sender.reply("❌ 创建订单失败: 未返回支付链接")
            return False

        qr_url = vorto_utils.generate_qrcode_url(generate_iframe_url(pay_url))
        sender.replyImage(qr_url)
        sender.reply(f'💳 请使用【{pay_type_name}】扫码支付\n⏰ 5分钟内完成支付\n输入"q"可取消')

        start_time = time.time()
        while time.time() - start_time < 300:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                return True

        sender.reply("❌ 支付超时")
        return False
    except Exception as exc:
        sender.reply(f"❌ 支付异常: {str(exc)}")
        return False


def pay_order(project, months, money):
    """兼容旧调用：扫码支付。"""
    return process_qrcode_payment(project, months, money)


def check_auth_status():
    """按 AUT 规范使用 vorto_utils 统一检测逻辑。"""
    return vorto_utils.check_auth_status(
        CONFIG_BUCKET,
        USER_BUCKET,
        AUTH_BUCKET,
        TOKEN_BUCKET,
        PLUGIN_NAME,
        delete_ql_callback=delete_ql_env,
    )


def ks_auth():
    """管理员授权菜单。"""
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
            sender,
            USER_BUCKET,
            AUTH_BUCKET,
            TOKEN_BUCKET,
            update_ql_callback=update_ql_env,
        )
    elif choice == '2':
        vorto_utils.admin_auth_by_user(
            sender,
            USER_BUCKET,
            AUTH_BUCKET,
            TOKEN_BUCKET,
            update_ql_callback=update_ql_env,
        )
    else:
        sender.reply("❌ 无效的选择")


def show_tutorial():
    """显示使用教程。"""
    tutorial = """
=====雨云签到教程=====
📱 用户指令:
• 雨云登录 - 绑定雨云账号
• 雨云查询 - 查询账号状态和积分信息
• 雨云管理 - 授权 / 删除 / 提交青龙
• 雨云教程 - 查看本教程
------------------
🔧 管理员指令:
• 雨云授权 - 管理员按天数授权
• 雨云检测 - 检测过期账号并清理
------------------
💡 登录说明:
• 格式: 账号#密码
• 支持批量登录，多账号换行分隔
• 插件负责管理账号并同步环境变量，实际签到脚本请在面板中运行
------------------
🧩 面板支持:
• 默认支持 QingLong
• 勾选 s_yy.use_dumbpanel 后可切换为 DumbPanel
• 可选配置 s_yy.panel_group 作为 DumbPanel 分组
------------------
💳 支付说明:
• 扫码支付 / 码支付 / 支付方式统一读取 Vorto初始化 配置
• 插件内不再单独配置收款码和码支付参数
------------------
🌐 代理说明:
• 可配置 s_yy.proxy_api 获取代理 IP
• API 返回格式需为 host:port
==================
"""
    sender.reply(tutorial.strip())


def main():
    """主入口。"""
    msg = sender.getMessage()
    lower_msg = msg.lower()

    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('雨云' in msg or 'yy' in lower_msg):
        query_accounts()
    elif '管理' in msg and ('雨云' in msg or 'yy' in lower_msg):
        manage_account()
    elif '教程' in msg and ('雨云' in msg or 'yy' in lower_msg):
        show_tutorial()
    elif '雨云授权' in msg:
        ks_auth()
    elif '雨云检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测雨云账号...")
        sender.reply(check_auth_status())
    elif sender.getImtype() == 'fake':
        try:
            middleware.notifyMasters(check_auth_status())
        except Exception:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
