# [title: 太平洋汽车]
# [language: python]
# [class: 工具类]
# [service: 203066880]
# [author: rujingxianghai]
# [rule: ^太平洋(登录|登陆)$|^太平洋(查询|管理|授权|检测|教程)$]
# [cron: 10 8 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://img-upload.vorto.cc/beb5a0d45aa58e08348e1e4076fa419e.jpg]
# [version: 1.2]
# [public: true]
# [price: 3.88]
# [description: 太平洋汽车插件（每周0.6元 + 315积分）<br>变量格式: 手机号#密码<br>功能: 绑定、查询、授权、提交面板、到期检测<br>查询返回: 积分、余额、已提现、累计收入<br>指令: 太平洋登录、太平洋查询、太平洋管理、太平洋授权、太平洋教程、太平洋检测]
# [param: {"required":false,"key":"s_tpyqc.qlname","bool":false,"placeholder":"Host|ClientID|ClientSecret","name":"设置对接容器","desc":"面板容器参数，不填则使用 Vorto 初始化全局配置"}]
# [param: {"required":false,"key":"s_tpyqc.use_daipanel","bool":true,"placeholder":"","name":"使用呆呆面板","desc":"勾选后使用呆呆面板，不勾选使用青龙面板"}]
# [param: {"required":false,"key":"s_tpyqc.panel_group","bool":false,"placeholder":"例如 太平洋汽车","name":"呆呆面板分组","desc":"填写后新增或更新变量时同步写入 group 字段"}]
# [param: {"required":true,"key":"s_tpyqc.osname","bool":false,"placeholder":"例如 S_TPYQC","name":"面板变量名","desc":"上传到面板中的环境变量名","value":"S_TPYQC"}]
# [param: {"required":true,"key":"s_tpyqc.Vipmoney","bool":false,"placeholder":"例如 0.88","name":"上车价格","desc":"授权价格(元/月)","value":"1"}]
# [param: {"required":false,"key":"s_tpyqc.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"s_tpyqc.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_tpyqc.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒","value":"3"}]

import json
import random
import time
from datetime import datetime
from hashlib import md5

import middleware
import requests
import vorto_utils


senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket="s_tpyqc_user", key=userid)

PLUGIN_CONFIG = {"bucket": "s_tpyqc", "coin_key": "dd_sign_points", "name": "太平洋汽车"}

LOGIN_URL = "https://mrobot.pcauto.com.cn/auto_passport3_back_intf/passport3/rest/login_new.jsp"
SIGN_CENTER_URL = "https://api.pcauto.com.cn/user-growth/sign/getSignCenterInfo"
WALLET_BALANCE_URL = "https://app-gateway.pcauto.com.cn/wallet/cash/balance"


def _loads(value, default=None):
    if default is None:
        default = {}
    try:
        result = json.loads(value)
        return result if result is not None else default
    except Exception:
        return default


def _mask_account(account):
    return vorto_utils.mask_account(str(account or ""))


def _today():
    return str(datetime.now().date())


def _get_user_accounts(user_id=None):
    if user_id is None:
        user_id = userid
    raw = middleware.bucketGet("s_tpyqc_user", user_id) or "[]"
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(item) for item in data if str(item).strip()]
    except Exception:
        pass
    try:
        data = eval(raw)
        if isinstance(data, (list, tuple, set)):
            return [str(item) for item in data if str(item).strip()]
    except Exception:
        pass
    return []


def _save_user_accounts(accounts, user_id=None):
    if user_id is None:
        user_id = userid
    cleaned = [str(item).strip() for item in accounts if str(item).strip()]
    if cleaned:
        middleware.bucketSet("s_tpyqc_user", user_id, json.dumps(cleaned, ensure_ascii=False))
    else:
        middleware.bucketDel("s_tpyqc_user", user_id)


def _get_token_info(account):
    return _loads(middleware.bucketGet("s_tpyqc_token", account), {})


def _save_token_info(account, account_info):
    middleware.bucketSet("s_tpyqc_token", account, json.dumps(account_info, ensure_ascii=False))


def _get_auth_text(account):
    auth_time = middleware.bucketGet("s_tpyqc_auth", account) or ""
    if not auth_time:
        return "未授权"
    if auth_time < _today():
        return f"已过期:{auth_time}"
    return f"到期:{auth_time}"


def _get_ql_client():
    osname = middleware.bucketGet("s_tpyqc", "osname") or "S_TPYQC"
    qlname = middleware.bucketGet("s_tpyqc", "qlname") or ""
    use_dp_raw = (
        middleware.bucketGet("s_tpyqc", "use_daipanel")
        or middleware.bucketGet("s_tpyqc", "use_dumbpanel")
        or ""
    )
    use_dp = str(use_dp_raw).lower() == "true"
    if use_dp:
        return vorto_utils.DumbPanelClient(osname, qlname) if qlname else vorto_utils.DumbPanelClient(osname)
    return vorto_utils.QingLongClient(osname, qlname) if qlname else vorto_utils.QingLongClient(osname)


def update_ql_env(account, account_info):
    phone = str(account or "").strip()
    password = str((account_info or {}).get("password") or "").strip()
    if not phone or not password:
        return False
    auth_time = middleware.bucketGet("s_tpyqc_auth", phone) or "未授权"
    panel_group = str(middleware.bucketGet("s_tpyqc", "panel_group") or "").strip()
    env_value = f"{phone}#{password}"
    remarks = f"{PLUGIN_CONFIG['name']}|{_mask_account(phone)}|到期:{auth_time}"
    ql = _get_ql_client()
    return ql.update_env(phone, env_value, remarks, group=panel_group)


def delete_ql_env(account):
    ql = _get_ql_client()
    return ql.delete_env(account)


def _parse_login_line(line):
    item = str(line or "").strip()
    if not item or "#" not in item:
        return "", ""
    phone, password = item.split("#", 1)
    return phone.strip(), password.strip()


def _build_select_menu(accounts, action_name):
    lines = [f"========选择{action_name}========", "[0] 全部账号"]
    for idx, account in enumerate(accounts, 1):
        auth_text = _get_auth_text(account)
        lines.append(
            f"[{idx}] {_mask_account(account)} {auth_text}"
        )
    lines.append("=====================")
    lines.append("支持多选，逗号分隔")
    lines.append('回复"q"退出')
    lines.append("=====================")
    return "\n".join(lines)


def _select_accounts(accounts, action_name):
    sender.reply(_build_select_menu(accounts, action_name))
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == "q":
        return None
    if choice == "0":
        return accounts.copy()
    selected = []
    try:
        for item in choice.split(","):
            index = int(item.strip())
            if 1 <= index <= len(accounts):
                selected.append(accounts[index - 1])
    except Exception:
        return []
    return selected


def _generate_signature(timestamp_str):
    raw = f"PCauto-2025-{timestamp_str}"
    first_md5 = md5(raw.encode("utf-8")).hexdigest()
    return md5(first_md5.encode("utf-8")).hexdigest()


class TaiPingYangClient:
    def __init__(self, phone, password):
        self.phone = str(phone or "").strip()
        self.password = str(password or "").strip()
        self.user_id = ""
        self.session_id = ""
        self.session = requests.Session()

    def _request_json(self, url, method="GET", headers=None, params=None, data=None, json_data=None):
        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json_data,
            timeout=15,
            verify=False,
        )
        response.raise_for_status()
        return response.json()

    def login(self):
        try:
            data = self._request_json(
                LOGIN_URL,
                method="POST",
                headers={
                    "Host": "mrobot.pcauto.com.cn",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "User-Agent": "Mozilla/5.0",
                },
                data={"username": self.phone, "password": self.password},
            )
        except Exception as exc:
            return False, f"登录请求失败: {exc}"

        if data.get("status") == 0:
            self.session_id = str(data.get("common_session_id") or "").strip()
            self.user_id = str(data.get("userId") or "").strip()
            if self.session_id and self.user_id:
                return True, {
                    "phone": self.phone,
                    "user_id": self.user_id,
                    "session_id": self.session_id,
                }
        return False, str(data.get("msg") or data.get("message") or "登录失败")

    def _build_sign_headers(self):
        timestamp = str(int(time.time() * 1000))
        return {
            "Host": "api.pcauto.com.cn",
            "x-auto-signature": _generate_signature(timestamp),
            "x-auto-time": timestamp,
            "distinctid": str(self.user_id),
            "sessionid": self.session_id,
            "Cookie": f"common_session_id={self.session_id}",
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 16; PLC110 Build/BP2A.250605.015; wv) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                "Chrome/145.0.7632.159 Mobile Safari/537.36/PCAutoApp"
            ),
            "Connection": "Keep-Alive",
        }

    def _build_wallet_headers(self):
        return {
            "Host": "app-gateway.pcauto.com.cn",
            "Content-Type": "application/json",
            "Cookie": f"common_session_id={self.session_id}",
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 16; PLC110 Build/BP2A.250605.015; wv) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 "
                "Chrome/145.0.7632.159 Mobile Safari/537.36"
            ),
        }

    def query_assets(self):
        if not self.session_id or not self.user_id:
            ok, result = self.login()
            if not ok:
                return False, result

        try:
            sign_data = self._request_json(
                SIGN_CENTER_URL,
                method="GET",
                headers=self._build_sign_headers(),
                params={"sessionId": self.session_id},
            )
            wallet_data = self._request_json(
                f"{WALLET_BALANCE_URL}?common_session_id={self.session_id}",
                method="POST",
                headers=self._build_wallet_headers(),
                json_data={},
            )
        except Exception as exc:
            return False, f"查询失败: {exc}"

        if sign_data.get("code") != 200:
            return False, str(sign_data.get("message") or sign_data.get("msg") or "积分接口返回异常")
        if wallet_data.get("code") != 200:
            return False, str(wallet_data.get("message") or wallet_data.get("msg") or "钱包接口返回异常")

        sign_info = sign_data.get("data") or {}
        wallet_info = wallet_data.get("data") or {}
        return True, {
            "phone": self.phone,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "points": str(sign_info.get("myPoint", "0")),
            "balance": str(wallet_info.get("balance", "0.00")),
            "withdrawn": str(wallet_info.get("withdrawn", "0.00")),
            "total": str(wallet_info.get("total", "0.00")),
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def _query_live_state(phone, password):
    client = TaiPingYangClient(phone, password)
    ok, login_result = client.login()
    if not ok:
        return False, login_result
    return client.query_assets()


def bind_account():
    sender.reply(
        "=====太平洋登录=====\n"
        "支持批量绑定，每行一个账号\n"
        "输入格式: 手机号#密码\n"
        "------------------\n"
        '回复"q"退出\n'
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("操作超时")
        return
    if input_text.lower() == "q":
        sender.reply("已取消")
        return

    lines = [line.strip() for line in input_text.split("\n") if line.strip()]
    if not lines:
        sender.reply("未检测到有效输入")
        return

    user_accounts = _get_user_accounts()
    success_list = []
    fail_list = []
    auto_sync_count = 0

    for line in lines:
        phone, password = _parse_login_line(line)
        if not phone or not password:
            fail_list.append(f"{line[:24]} -> 格式错误，正确格式: 手机号#密码")
            continue

        ok, result = _query_live_state(phone, password)
        if not ok:
            fail_list.append(f"{_mask_account(phone)} -> {result}")
            continue

        token_info = {
            "phone": phone,
            "password": password,
            "user_id": result.get("user_id", ""),
            "points": result.get("points", "0"),
            "balance": result.get("balance", "0.00"),
            "withdrawn": result.get("withdrawn", "0.00"),
            "total": result.get("total", "0.00"),
            "update_time": result.get("update_time", ""),
        }
        _save_token_info(phone, token_info)
        if phone not in user_accounts:
            user_accounts.append(phone)

        auth_time = middleware.bucketGet("s_tpyqc_auth", phone) or ""
        if auth_time and auth_time >= _today():
            try:
                if update_ql_env(phone, token_info):
                    auto_sync_count += 1
            except Exception:
                pass

        success_list.append(
            f"{_mask_account(phone)} -> 积分:{token_info['points']} | 余额:{token_info['balance']}元"
        )

    _save_user_accounts(user_accounts)

    result_text = "=====绑定完成=====\n"
    result_text += f"成功: {len(success_list)}个\n"
    if success_list:
        result_text += "\n".join(success_list[:12]) + "\n"
        if len(success_list) > 12:
            result_text += f"... 共 {len(success_list)} 条成功记录\n"
    if fail_list:
        result_text += f"失败: {len(fail_list)}个\n"
        result_text += "\n".join(fail_list[:12]) + "\n"
        if len(fail_list) > 12:
            result_text += f"... 共 {len(fail_list)} 条失败记录"
    result_text += "=================="
    sender.reply(result_text)


def query_accounts():
    accounts = _get_user_accounts()
    if not accounts:
        sender.reply(
            "=====未绑定账号=====\n"
            "未找到账号\n"
            "发送“太平洋登录”绑定\n"
            "=================="
        )
        return

    selected = _select_accounts(accounts, "查询账号")
    if selected is None:
        sender.reply("已退出")
        return
    if not selected:
        sender.reply("未选择有效账号")
        return

    sender.reply(f"已选择 {len(selected)} 个账号，正在查询...")
    result_blocks = []

    for phone in selected:
        token_info = _get_token_info(phone)
        password = str(token_info.get("password") or "").strip()
        auth_time = middleware.bucketGet("s_tpyqc_auth", phone) or "未授权"

        if not password:
            result_blocks.append(
                "\n".join(
                    [
                        f"账号: {_mask_account(phone)}",
                        f"授权: {auth_time}",
                        "查询状态: 失败",
                        "原因: 缺少密码，请重新绑定",
                    ]
                )
            )
            continue

        ok, result = _query_live_state(phone, password)
        source_text = "实时接口"
        if ok:
            token_info.update(
                {
                    "phone": phone,
                    "password": password,
                    "user_id": result.get("user_id", ""),
                    "points": result.get("points", "0"),
                    "balance": result.get("balance", "0.00"),
                    "withdrawn": result.get("withdrawn", "0.00"),
                    "total": result.get("total", "0.00"),
                    "update_time": result.get("update_time", ""),
                }
            )
            _save_token_info(phone, token_info)
        else:
            source_text = f"缓存数据，实时查询失败: {result}"
            result = {
                "points": token_info.get("points", "未知"),
                "balance": token_info.get("balance", "未知"),
                "withdrawn": token_info.get("withdrawn", "未知"),
                "total": token_info.get("total", "未知"),
                "user_id": token_info.get("user_id", ""),
                "update_time": token_info.get("update_time", "未知"),
            }

        result_blocks.append(
            "\n".join(
                [
                    f"账号: {_mask_account(phone)}",
                    f"用户ID: {result.get('user_id', '') or '未知'}",
                    f"授权: {auth_time}",
                    f"积分: {result.get('points', '未知')}",
                    f"余额: {result.get('balance', '未知')}元",
                    f"已提现: {result.get('withdrawn', '未知')}元",
                    f"累计收入: {result.get('total', '未知')}元",
                ]
            )
        )

    sender.reply(
        "=====查询结果=====\n"
        + "\n------------------\n".join(result_blocks)
        + "\n=================="
    )


def _process_qrcode_payment(project, months, money):
    if float(money) == 0:
        return True
    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config["zsm"]
    if not zsm:
        sender.reply("未配置收款码，请先在 Vorto 初始化中配置")
        return False
    sender.reply(
        f"=====扫码支付=====\n"
        f"商品: {project}\n"
        f"时长: {months} 月\n"
        f"金额: {money} 元\n"
        f"=================="
    )
    sender.replyImage(zsm)
    ddzf = sender.waitPay("q", 300000)
    if str(ddzf) == "q":
        sender.reply("已取消支付")
        return False
    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
        if float(ddzf.get("Money") or ddzf.get("money", 0)) >= float(money):
            return True
    except Exception:
        pass
    sender.reply("支付校验失败")
    return False


def _process_mapay_payment(project, months, money, pay_type="alipay"):
    if float(money) == 0:
        return True
    pay_config = vorto_utils.get_pay_config()
    if not pay_config["ma_pay_switch"]:
        sender.reply("码支付功能未开启")
        return False
    try:
        out_trade_no = f"TPYQC{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config["pay_types"].get(pay_type, pay_type)
        sender.reply(
            f"=====码支付信息=====\n"
            f"商品: {project}\n"
            f"时长: {months} 月\n"
            f"金额: {money} 元\n"
            f"方式: {pay_type_name}\n"
            f"=================="
        )
        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)
        if order.get("error"):
            sender.reply(f"创建订单失败: {order.get('error')}")
            return False
        qr_url = vorto_utils.generate_qrcode_url(order.get("pay_url"))
        sender.replyImage(qr_url)
        sender.reply(f'请使用【{pay_type_name}】扫码支付，输入"q"可取消')

        start_time = time.time()
        while time.time() - start_time < 300:
            user_input = sender.input(5000, 1, False)
            if user_input and user_input.lower() == "q":
                sender.reply("已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                sender.reply("支付成功")
                return True
        sender.reply("支付超时")
        return False
    except Exception as exc:
        sender.reply(f"支付异常: {str(exc)}")
        return False


def authorize_accounts(accounts):
    if not accounts:
        sender.reply("没有可授权账号")
        return

    account_infos = []
    for account in accounts:
        info = _get_token_info(account)
        if info.get("password"):
            account_infos.append({"account": account, "info": info})

    if not account_infos:
        sender.reply("没有有效账号信息")
        return

    sender.reply(
        f"已选择 {len(account_infos)} 个账号\n"
        "=====设置授权时长=====\n"
        "请输入授权月数，例如 1\n"
        '回复"q"退出\n'
        "=================="
    )
    months_input = sender.input(120000, 1, False)
    if not months_input or months_input.lower() == "q":
        sender.reply("已取消")
        return

    try:
        months = int(months_input)
        if months <= 0:
            sender.reply("月数必须大于 0")
            return
    except ValueError:
        sender.reply("请输入有效数字")
        return

    vip_money = float(middleware.bucketGet("s_tpyqc", "Vipmoney") or "1")
    coin_cost = int(middleware.bucketGet("s_tpyqc", "coin") or "0")
    total_money = round(len(account_infos) * months * vip_money, 2)

    pay_config = vorto_utils.get_pay_config()
    available = []
    if pay_config["qr_pay_switch"]:
        available.append(("扫码支付", "qrcode"))
    if pay_config["ma_pay_switch"]:
        for pay_key, pay_name in pay_config["pay_types"].items():
            available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
    if coin_cost > 0:
        available.append(("积分兑换", "coin"))

    if not available:
        sender.reply("未配置任何支付方式，请先在 Vorto 初始化中开启")
        return

    if len(available) == 1:
        payment_type = available[0][1]
    else:
        menu = [
            "=====选择支付方式=====",
            f"账号: {len(account_infos)} 个",
            f"时长: {months} 月",
            f"金额: {total_money} 元",
            "------------------",
        ]
        for idx, item in enumerate(available, 1):
            menu.append(f"[{idx}] {item[0]}")
        menu.extend(["------------------", "回复序号选择", "=================="])
        sender.reply("\n".join(menu))
        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == "q":
            sender.reply("已取消")
            return
        try:
            payment_type = available[int(pay_choice) - 1][1]
        except Exception:
            sender.reply("无效选择")
            return

    paid = False
    if payment_type == "coin":
        total_coin = len(account_infos) * months * coin_cost
        user_coin = int(middleware.bucketGet("dd_sign_points", userid) or "0")
        if user_coin < total_coin:
            sender.reply(f"积分不足，需要 {total_coin}，当前 {user_coin}")
            return
        middleware.bucketSet("dd_sign_points", userid, str(user_coin - total_coin))
        paid = True
    elif payment_type == "qrcode":
        paid = _process_qrcode_payment(PLUGIN_CONFIG["name"], months, total_money)
    elif payment_type.startswith("mapay_"):
        paid = _process_mapay_payment(PLUGIN_CONFIG["name"], months, total_money, payment_type.replace("mapay_", ""))

    if not paid:
        sender.reply("授权未完成")
        return

    success_list = []
    fail_list = []
    for item in account_infos:
        account = item["account"]
        info = item["info"]
        try:
            new_expire = vorto_utils.calculate_auth_time("s_tpyqc_auth", account, months=months)
            middleware.bucketSet("s_tpyqc_auth", account, new_expire)
            sync_ok = False
            try:
                sync_ok = update_ql_env(account, info)
            except Exception:
                sync_ok = False
            if sync_ok:
                success_list.append(f"{_mask_account(account)} -> {new_expire}")
            else:
                success_list.append(f"{_mask_account(account)} -> {new_expire} (面板未同步，可稍后手动提交)")
        except Exception as exc:
            fail_list.append(f"{_mask_account(account)} -> {str(exc)}")

    result = "=====授权完成=====\n"
    result += f"成功: {len(success_list)}个\n"
    if success_list:
        result += "\n".join(success_list) + "\n"
    if fail_list:
        result += f"失败: {len(fail_list)}个\n"
        result += "\n".join(fail_list) + "\n"
    result += "=================="
    sender.reply(result)


def manage_account():
    accounts = _get_user_accounts()
    if not accounts:
        sender.reply(
            "=====未绑定账号=====\n"
            "未找到账号\n"
            "=================="
        )
        return

    sender.reply(
        "=====太平洋管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交面板\n"
        "------------------\n"
        "回复数字选择\n"
        '回复"q"退出\n'
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == "q":
        sender.reply("已退出")
        return

    selected = _select_accounts(accounts, "操作账号")
    if selected is None:
        sender.reply("已退出")
        return
    if not selected:
        sender.reply("未选择有效账号")
        return

    if choice == "1":
        authorize_accounts(selected)
        return

    if choice == "2":
        sender.reply(f'确认删除 {len(selected)} 个账号？回复 y 确认，其它任意内容取消')
        confirm = sender.input(120000, 1, False)
        if not confirm or confirm.lower() != "y":
            sender.reply("已取消")
            return

        remain_accounts = accounts[:]
        success_list = []
        fail_list = []
        for account in selected:
            try:
                if account in remain_accounts:
                    remain_accounts.remove(account)
                middleware.bucketDel("s_tpyqc_token", account)
                middleware.bucketDel("s_tpyqc_auth", account)
                try:
                    delete_ql_env(account)
                except Exception:
                    pass
                success_list.append(_mask_account(account))
            except Exception as exc:
                fail_list.append(f"{_mask_account(account)} -> {str(exc)}")

        _save_user_accounts(remain_accounts)

        result = "=====删除完成=====\n"
        result += f"成功: {len(success_list)}个\n"
        if success_list:
            result += "\n".join(success_list) + "\n"
        if fail_list:
            result += f"失败: {len(fail_list)}个\n"
            result += "\n".join(fail_list) + "\n"
        result += "=================="
        sender.reply(result)
        return

    if choice == "3":
        success_list = []
        fail_list = []
        today = _today()
        for account in selected:
            auth_time = middleware.bucketGet("s_tpyqc_auth", account) or ""
            if not auth_time or auth_time < today:
                fail_list.append(f"{_mask_account(account)} -> 未授权或已过期")
                continue
            info = _get_token_info(account)
            if not info.get("password"):
                fail_list.append(f"{_mask_account(account)} -> 缺少密码，请重新绑定")
                continue
            try:
                if update_ql_env(account, info):
                    success_list.append(_mask_account(account))
                else:
                    fail_list.append(f"{_mask_account(account)} -> 面板更新失败")
            except Exception as exc:
                fail_list.append(f"{_mask_account(account)} -> {str(exc)}")

        result = "=====提交结果=====\n"
        result += f"成功: {len(success_list)}个\n"
        if success_list:
            result += "\n".join(success_list) + "\n"
        if fail_list:
            result += f"失败: {len(fail_list)}个\n"
            result += "\n".join(fail_list) + "\n"
        result += "变量格式: 手机号#密码\n"
        result += "=================="
        sender.reply(result)
        return

    sender.reply("无效选择")


def ks_auth():
    if not sender.isAdmin():
        sender.reply("仅限管理员")
        return

    sender.reply(
        "=====太平洋授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择\n"
        '回复"q"退出\n'
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == "q":
        sender.reply("已退出")
        return

    if choice == "1":
        vorto_utils.admin_auth_all_accounts(
            sender, "s_tpyqc_user", "s_tpyqc_auth", "s_tpyqc_token", update_ql_callback=update_ql_env
        )
    elif choice == "2":
        vorto_utils.admin_auth_by_user(
            sender, "s_tpyqc_user", "s_tpyqc_auth", "s_tpyqc_token", update_ql_callback=update_ql_env
        )
    else:
        sender.reply("无效选择")


def show_tutorial():
    sender.reply(
        "=====太平洋教程=====\n"
        "用户指令:\n"
        "1. 太平洋登录 - 绑定账号\n"
        "2. 太平洋查询 - 查询积分、余额、已提现、累计收入\n"
        "3. 太平洋管理 - 授权、删除、提交面板\n"
        "4. 太平洋教程 - 查看说明\n"
        "------------------\n"
        "管理员指令:\n"
        "1. 太平洋授权 - 批量授权\n"
        "2. 太平洋检测 - 检测过期并清理\n"
        "------------------\n"
        "绑定格式:\n"
        "手机号#密码\n"
        "支持换行批量绑定\n"
        "=================="
    )


def main():
    msg = sender.getMessage()

    if ("登录" in msg or "登陆" in msg) and "太平洋" in msg:
        bind_account()
    elif "查询" in msg and "太平洋" in msg:
        query_accounts()
    elif "管理" in msg and "太平洋" in msg:
        manage_account()
    elif "教程" in msg and "太平洋" in msg:
        show_tutorial()
    elif "太平洋授权" in msg:
        ks_auth()
    elif "太平洋检测" in msg:
        if not sender.isAdmin():
            sender.reply("仅限管理员")
            return
        sender.reply("正在检测...")
        sender.reply(
            vorto_utils.check_auth_status(
                "s_tpyqc",
                "s_tpyqc_user",
                "s_tpyqc_auth",
                "s_tpyqc_token",
                "太平洋汽车",
                delete_ql_callback=delete_ql_env,
            )
        )
    elif sender.getImtype() == "fake":
        try:
            result = vorto_utils.check_auth_status(
                "s_tpyqc",
                "s_tpyqc_user",
                "s_tpyqc_auth",
                "s_tpyqc_token",
                "太平洋汽车",
                delete_ql_callback=delete_ql_env,
            )
            middleware.notifyMasters(result)
        except Exception:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
