# [title: 爱路桥]
# [language: python]
# [class: 工具类]
# [service: 2993959969]
# [author: rujingxianghai]
# [rule: ^(爱路桥|alq)(登录|登陆)$|^登(录|陆)(爱路桥|alq)$|^(爱路桥|alq)(查询|管理|授权|检测|教程)$|^(查询|管理|授权|检测|教程)(爱路桥|alq)$]
# [cron: 18 9 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: https://img-cf.885666.xyz/65f0d781788eb95ae389d77969b248da.png]
# [version: 3.3]
# [public: true]
# [price: 8.88]
# [description: 爱路桥积分红包插件<br>指令：登录、查询、管理、授权、检测、教程<br>支持短信登录、批量授权、面板提交、到期检测]
# [param: {"required":false,"key":"s_alq.qlname","bool":false,"placeholder":"青龙:Host丨ClientID丨ClientSecret；呆呆:Host丨AppKey丨AppSecret","name":"设置对接容器","desc":"面板容器参数；use_daipanel=true 时此处应填写呆呆面板 Host丨AppKey丨AppSecret，不填则回退使用 Vorto初始化 全局配置"}]
# [param: {"required":false,"key":"s_alq.use_daipanel","bool":true,"placeholder":"","name":"使用呆呆面板","desc":"勾选后使用呆呆面板，不勾选使用青龙面板"}]
# [param: {"required":false,"key":"s_alq.panel_group","bool":false,"placeholder":"例:爱路桥","name":"呆呆面板分组","desc":"仅 use_daipanel=true 时生效，填写后同步写入 group 字段"}]
# [param: {"required":true,"key":"s_alq.osname","bool":false,"placeholder":"例:S_ALQ","name":"青龙变量名","desc":"上传到面板的变量名","value":"S_ALQ"}]
# [param: {"required":true,"key":"s_alq.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元/月)","value":"1"}]
# [param: {"required":false,"key":"s_alq.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"s_alq.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_alq.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒","value":"3"}]

import base64
import json
import random
import string
import time
from datetime import datetime

import middleware
import requests
import vorto_utils


senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())

PLUGIN_NAME = "爱路桥"
CONFIG_BUCKET = "s_alq"
LEGACY_CONFIG_BUCKET = "s_alq_config"
USER_BUCKET = "s_alq_user"
TOKEN_BUCKET = "s_alq_token"
AUTH_BUCKET = "s_alq_auth"
BASE_URL = "https://www.ailuqiao.cn/mobile"
DDDDOCR_URL = "https://ocr-xn.vzvv.de"
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/135.0.7049.37 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 6 Build/UQ1A.240605.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/133.0.6638.41 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1",
]
LEGACY_KEY_MAP = {
    "qlname": ("qlname", "alq_qlname"),
    "osname": ("osname", "alq_osname"),
    "Vipmoney": ("Vipmoney", "alqVipmoney"),
    "coin": ("coin", "alqcoin"),
    "notify": ("notify",),
    "notify_days": ("notify_days",),
    "use_daipanel": ("use_daipanel", "use_dumbpanel"),
    "panel_group": ("panel_group",),
}


def _loads(raw, default=None):
    if default is None:
        default = {}
    try:
        data = json.loads(raw)
        return data if data is not None else default
    except Exception:
        return default


def _today():
    return str(datetime.now().date())


def _mask_account(account):
    return vorto_utils.mask_account(str(account or ""))


def _config_bucket_name():
    new_keys = ("qlname", "osname", "Vipmoney", "coin", "notify", "notify_days", "use_daipanel", "panel_group")
    old_keys = ("qlname", "alq_qlname", "osname", "alq_osname", "Vipmoney", "alqVipmoney", "coin", "alqcoin", "notify", "notify_days", "use_daipanel", "panel_group")
    for key in new_keys:
        if str(middleware.bucketGet(CONFIG_BUCKET, key) or "").strip():
            return CONFIG_BUCKET
    for key in old_keys:
        if str(middleware.bucketGet(LEGACY_CONFIG_BUCKET, key) or "").strip():
            return LEGACY_CONFIG_BUCKET
    return CONFIG_BUCKET


def _cfg(key, default=""):
    aliases = LEGACY_KEY_MAP.get(key, (key,))
    for bucket in (CONFIG_BUCKET, LEGACY_CONFIG_BUCKET):
        for alias in aliases:
            value = middleware.bucketGet(bucket, alias)
            if value not in (None, ""):
                return value
    return default


def _cfg_float(key, default):
    try:
        return float(_cfg(key, str(default)) or default)
    except Exception:
        return float(default)


def _cfg_int(key, default):
    try:
        return int(_cfg(key, str(default)) or default)
    except Exception:
        return int(default)


def _pkcs7_pad(raw_bytes, block_size=16):
    pad_len = block_size - (len(raw_bytes) % block_size)
    return raw_bytes + bytes([pad_len]) * pad_len


def _aes_encrypt_text(text, key="ailuqiaoAb112112", iv="ailuqiaobagebaao"):
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    except Exception as exc:
        raise RuntimeError("缺少 cryptography 依赖，无法执行短信登录加密") from exc

    plain_bytes = _pkcs7_pad(str(text or "").encode("utf-8"))
    cipher = Cipher(
        algorithms.AES(str(key).encode("utf-8")),
        modes.CBC(str(iv).encode("utf-8")),
    )
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(plain_bytes) + encryptor.finalize()
    return base64.b64encode(encrypted).decode("utf-8")


def _get_user_accounts(user_id=None):
    user_id = str(user_id or userid)
    raw = middleware.bucketGet(USER_BUCKET, user_id) or "[]"
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]
    except Exception:
        pass
    try:
        data = eval(raw)
        if isinstance(data, (list, tuple, set)):
            return [str(item).strip() for item in data if str(item).strip()]
    except Exception:
        pass
    return []


def _save_user_accounts(accounts, user_id=None):
    user_id = str(user_id or userid)
    cleaned = list(dict.fromkeys(str(item).strip() for item in accounts if str(item).strip()))
    if cleaned:
        middleware.bucketSet(USER_BUCKET, user_id, json.dumps(cleaned, ensure_ascii=False))
    else:
        middleware.bucketDel(USER_BUCKET, user_id)


def _get_token_info(account):
    return _loads(middleware.bucketGet(TOKEN_BUCKET, str(account).strip()), {})


def _save_token_info(account, account_info):
    middleware.bucketSet(TOKEN_BUCKET, str(account).strip(), json.dumps(account_info, ensure_ascii=False))


def _get_auth_text(account):
    auth_time = str(middleware.bucketGet(AUTH_BUCKET, str(account).strip()) or "").strip()
    if not auth_time:
        return "未授权"
    if auth_time < _today():
        return f"已过期:{auth_time}"
    return f"到期:{auth_time}"


def _select_accounts():
    accounts, selected = vorto_utils.select_accounts(sender, USER_BUCKET, userid, AUTH_BUCKET, PLUGIN_NAME)
    if accounts is None and selected is None:
        return None, None
    return accounts or [], list(dict.fromkeys(selected or []))


def _get_ql_client():
    osname = str(middleware.bucketGet(CONFIG_BUCKET, "osname") or "S_ALQ").strip()
    qlname = str(middleware.bucketGet(CONFIG_BUCKET, "qlname") or "").strip()
    use_daipanel = str(middleware.bucketGet(CONFIG_BUCKET, "use_daipanel") or "").lower() == "true"
    if use_daipanel:
        return vorto_utils.DumbPanelClient(osname, qlname) if qlname else vorto_utils.DumbPanelClient(osname)
    return vorto_utils.QingLongClient(osname, qlname) if qlname else vorto_utils.QingLongClient(osname)


def _get_panel_name():
    return "呆呆面板" if str(middleware.bucketGet(CONFIG_BUCKET, "use_daipanel") or "").lower() == "true" else "青龙面板"


def _build_panel_env(account, account_info):
    phone = str(account or "").strip()
    uid = str((account_info or {}).get("uid") or "").strip()
    cookie = str((account_info or {}).get("cookie") or "").strip()
    if not phone or not uid or not cookie:
        return None
    auth_time = middleware.bucketGet(AUTH_BUCKET, phone) or "未授权"
    panel_group = str(_cfg("panel_group", "") or "").strip()
    remarks = f"{PLUGIN_NAME}:{phone}|uid:{uid}|到期:{auth_time}"
    return phone, f"{uid}#{cookie}", remarks, panel_group


def update_ql_env(account, account_info):
    env_data = _build_panel_env(account, account_info)
    if not env_data:
        return False
    ql = _get_ql_client()
    if not ql.is_configured():
        return False
    phone, env_value, remarks, panel_group = env_data
    use_daipanel = str(middleware.bucketGet(CONFIG_BUCKET, "use_daipanel") or "").lower() == "true"
    if use_daipanel and panel_group:
        return ql.update_env(phone, env_value, remarks, group=panel_group)
    return ql.update_env(phone, env_value, remarks)


def sync_ql_env(account, account_info):
    ql = _get_ql_client()
    panel_name = _get_panel_name()
    if not ql.is_configured():
        return False, f"{panel_name}未配置"

    env_data = _build_panel_env(account, account_info)
    if not env_data:
        return False, "账号凭证不完整"

    phone, env_value, remarks, panel_group = env_data
    use_daipanel = str(middleware.bucketGet(CONFIG_BUCKET, "use_daipanel") or "").lower() == "true"
    if use_daipanel and panel_group:
        ok = ql.update_env(phone, env_value, remarks, group=panel_group)
    else:
        ok = ql.update_env(phone, env_value, remarks)
    if ok:
        return True, f"{panel_name}同步成功"
    return False, f"{panel_name}变量更新失败"


def delete_ql_env(account):
    return _get_ql_client().delete_env(str(account or "").strip())


class AiLuQiaoClient:
    def __init__(self, phone="", cookie=""):
        self.phone = str(phone or "").strip()
        self.cookie = str(cookie or self._generate_cookie()).strip()
        self.session = requests.Session()

    @staticmethod
    def _generate_cookie():
        session_id = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(32))
        return f"beegosessionID={session_id}"

    @staticmethod
    def _generate_cid():
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choice(chars) for _ in range(32))

    @staticmethod
    def _current_time_text():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _build_sms_headers(self, uid):
        uid = str(uid or self.phone).strip()
        now_text = self._current_time_text()
        return {
            "Content-Types": _aes_encrypt_text(uid),
            "Content-Type2": _aes_encrypt_text(f"{now_text}{uid}"),
        }

    def _request_json(self, method, endpoint, params=None, data=None, extra_headers=None):
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "Cookie": self.cookie,
        }
        if data is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        if extra_headers:
            headers.update(extra_headers)
        response = self.session.request(
            method=method.upper(),
            url=f"{BASE_URL}{endpoint}",
            params=params,
            data=data,
            headers=headers,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()

    def _get_captcha(self):
        """获取图形验证码，返回 (captcha_id, captcha_img_base64)"""
        try:
            data = self._request_json("GET", "/GenerateCaptcha")
        except Exception as exc:
            return None, None, f"获取验证码图片失败: {exc}"
        captcha_data = data.get("data") or data
        captcha_id = str(captcha_data.get("captcha_id") or "").strip()
        captcha_img = str(captcha_data.get("captcha_img") or "").strip()
        if not captcha_id or not captcha_img:
            return None, None, "验证码数据为空"
        return captcha_id, captcha_img, ""

    @staticmethod
    def _recognize_captcha(captcha_img_base64):
        """调用 ddddocr 识别图形验证码"""
        img_data = captcha_img_base64
        if "," in img_data:
            img_data = img_data.split(",", 1)[1]
        try:
            resp = requests.post(
                f"{DDDDOCR_URL}/classification",
                json={"image": img_data},
                timeout=10,
            )
            resp.raise_for_status()
            result = resp.json()
            code = str(result.get("result") or "").strip()
            if not code:
                return None, "验证码识别结果为空"
            return code, ""
        except Exception as exc:
            return None, f"验证码识别失败: {exc}"

    def send_sms_code(self):
        captcha_id, captcha_img, err = self._get_captcha()
        if err:
            return False, err
        captcha_code, err = self._recognize_captcha(captcha_img)
        if err:
            return False, err
        try:
            uid = self.phone
            data = self._request_json(
                "POST",
                "/service_send_0407new",
                data={
                    "cid": self._generate_cid(),
                    "mobile": self.phone,
                    "uid": uid,
                    "captcha_id": captcha_id,
                    "captcha_code": captcha_code,
                },
                extra_headers=self._build_sms_headers(uid),
            )
        except Exception as exc:
            return False, f"发送验证码失败: {exc}"
        if data.get("status") == 1:
            return True, data
        return False, str(data.get("message") or data.get("msg") or "发送验证码失败")

    def fetch_profile(self, uid):
        try:
            data = self._request_json("GET", "/myinfo", params={"uid": uid})
        except Exception as exc:
            return False, f"获取用户信息失败: {exc}"
        user_data = data.get("data") or {}
        if not user_data:
            return False, str(data.get("message") or data.get("msg") or "用户信息为空")
        return True, {
            "nickname": str(user_data.get("nickname") or self.phone),
            "integral": str(user_data.get("integral") or "0"),
        }

    def fetch_records(self, uid, limit=5):
        try:
            data = self._request_json("GET", "/my_luck", params={"uid": uid, "cid": 1028})
        except Exception as exc:
            return False, f"获取红包记录失败: {exc}"
        records = []
        for item in (data.get("data") or [])[:limit]:
            records.append({
                "prize": str(item.get("draw") or ""),
                "time": str(item.get("create_time") or ""),
            })
        return True, records

    def login_with_code(self, code):
        try:
            data = self._request_json("POST", "/service_yz", data={"mobile": self.phone, "code": str(code).strip()})
        except Exception as exc:
            return False, f"登录失败: {exc}"
        if data.get("status") != 1:
            return False, str(data.get("message") or data.get("msg") or "验证码错误或已过期")
        uid = str(data.get("uid") or "").strip()
        if not uid:
            return False, "登录失败: 未获取到 UID"
        nickname = self.phone
        integral = "0"
        ok, profile = self.fetch_profile(uid)
        if ok:
            nickname = profile.get("nickname") or nickname
            integral = profile.get("integral") or integral
        return True, {
            "phone": self.phone,
            "uid": uid,
            "cookie": self.cookie,
            "nickname": nickname,
            "integral": integral,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }


def _query_live_state(account, account_info):
    phone = str(account or "").strip()
    uid = str((account_info or {}).get("uid") or "").strip()
    cookie = str((account_info or {}).get("cookie") or "").strip()
    if not uid or not cookie:
        return False, "缺少 UID 或 Cookie"
    client = AiLuQiaoClient(phone=phone, cookie=cookie)
    ok, profile = client.fetch_profile(uid)
    if not ok:
        return False, profile
    ok_records, records = client.fetch_records(uid)
    return True, {
        "uid": uid,
        "nickname": profile.get("nickname") or phone,
        "integral": profile.get("integral") or "0",
        "records": records if ok_records else [],
        "record_error": "" if ok_records else records,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def bind_account():
    sender.reply(
        "=====爱路桥登录=====\n"
        "请输入手机号码\n"
        "------------------\n"
        '回复"q"退出\n'
        "=================="
    )
    phone = sender.input(120000, 1, False)
    if not phone:
        sender.reply("⏰ 操作超时")
        return
    phone = str(phone).strip()
    if phone.lower() == "q":
        sender.reply("✅ 已取消")
        return
    if not phone.isdigit() or len(phone) != 11:
        sender.reply("❌ 手机号格式错误，请输入 11 位数字")
        return

    client = AiLuQiaoClient(phone=phone)
    ok, result = client.send_sms_code()
    if not ok:
        sender.reply(f"❌ {result}")
        return

    sender.reply(
        "=====验证码已发送=====\n"
        f"📱 手机号: {_mask_account(phone)}\n"
        "------------------\n"
        "请输入短信验证码\n"
        '回复"q"退出\n'
        "=================="
    )
    code = sender.input(300000, 1, False)
    if not code:
        sender.reply("⏰ 验证码输入超时")
        return
    if str(code).strip().lower() == "q":
        sender.reply("✅ 已取消")
        return

    ok, account_info = client.login_with_code(code)
    if not ok:
        sender.reply(f"❌ {account_info}")
        return

    accounts = _get_user_accounts()
    if phone not in accounts:
        accounts.append(phone)
        _save_user_accounts(accounts)
    _save_token_info(phone, account_info)

    auth_time = str(middleware.bucketGet(AUTH_BUCKET, phone) or "").strip()
    sync_text = '未授权，可发送"爱路桥管理"开通'
    if auth_time and auth_time >= _today():
        sync_ok, sync_msg = sync_ql_env(phone, account_info)
        sync_text = f"已授权，{sync_msg}" if sync_ok else f"已授权，但{sync_msg}"

    sender.reply(
        "=====绑定成功=====\n"
        f"📱 账号: {_mask_account(phone)}\n"
        f"👤 昵称: {account_info.get('nickname') or '未设置'}\n"
        f"🆔 UID: {account_info.get('uid') or '未知'}\n"
        f"💰 积分: {account_info.get('integral') or '0'}\n"
        f"📅 授权: {_get_auth_text(phone)}\n"
        f"🔄 状态: {sync_text}\n"
        "=================="
    )


def query_accounts():
    accounts, selected = _select_accounts()
    if accounts is None:
        return
    if not selected:
        sender.reply("❌ 未选择有效账号")
        return

    sender.reply(f"✅ 已选择 {len(selected)} 个账号，正在查询...")
    blocks = []
    for phone in selected:
        token_info = _get_token_info(phone)
        cached_nickname = token_info.get("nickname") or "未设置"
        cached_integral = token_info.get("integral") or "未知"
        ok, result = _query_live_state(phone, token_info)
        if ok:
            token_info.update({
                "phone": phone,
                "uid": result.get("uid") or token_info.get("uid", ""),
                "cookie": token_info.get("cookie", ""),
                "nickname": result.get("nickname") or cached_nickname,
                "integral": result.get("integral") or cached_integral,
                "update_time": result.get("update_time", ""),
            })
            _save_token_info(phone, token_info)
            lines = [
                f"账号: {_mask_account(phone)}",
                f"昵称: {result.get('nickname') or cached_nickname}",
                f"UID: {result.get('uid') or token_info.get('uid') or '未知'}",
                f"积分: {result.get('integral') or cached_integral}",
                f"授权: {_get_auth_text(phone)}",
            ]
            if result.get("records"):
                lines.append("最近红包记录:")
                lines.extend(
                    f"- {item.get('prize') or '未知'} ({item.get('time') or '未知'})"
                    for item in result["records"]
                )
            elif result.get("record_error"):
                lines.append(f"红包记录: {result.get('record_error')}")
        else:
            lines = [
                f"账号: {_mask_account(phone)}",
                f"昵称: {cached_nickname}",
                f"UID: {token_info.get('uid') or '未知'}",
                f"积分: {cached_integral}",
                f"授权: {_get_auth_text(phone)}",
                f"查询说明: {result}",
            ]
        blocks.append("\n".join(lines))

    sender.reply("=====查询结果=====\n" + "\n------------------\n".join(blocks) + "\n==================")


def _process_qrcode_payment(project, months, money):
    if float(money) == 0:
        return True
    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config.get("zsm")
    if not zsm:
        sender.reply("❌ 未配置收款码，请联系管理员在 Vorto初始化 中配置")
        return False
    sender.reply(
        f"=====扫码支付=====\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        "=================="
    )
    sender.replyImage(zsm)
    pay_result = sender.waitPay("q", 300000)
    if str(pay_result) == "q":
        sender.reply("✅ 已取消支付")
        return False
    try:
        if isinstance(pay_result, str):
            pay_result = json.loads(pay_result)
        if float(pay_result.get("Money") or pay_result.get("money") or 0) >= float(money):
            return True
    except Exception:
        pass
    sender.reply("❌ 支付校验失败")
    return False


def _process_mapay_payment(project, months, money, pay_type):
    if float(money) == 0:
        return True
    pay_config = vorto_utils.get_pay_config()
    if not pay_config.get("ma_pay_switch"):
        sender.reply("❌ 码支付功能未开启")
        return False
    try:
        out_trade_no = f"ALQ{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config.get("pay_types", {}).get(pay_type, pay_type)
        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"💳 方式: {pay_type_name}\n"
            "=================="
        )
        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)
        if order.get("error"):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False
        sender.replyImage(vorto_utils.generate_qrcode_url(order.get("pay_url")))
        sender.reply(f'💳 请使用【{pay_type_name}】扫码支付，输入"q"可取消')
        start_time = time.time()
        while time.time() - start_time < 300:
            user_input = sender.input(5000, 1, False)
            if user_input and str(user_input).strip().lower() == "q":
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                sender.reply("✅ 支付成功")
                return True
        sender.reply("❌ 支付超时")
    except Exception as exc:
        sender.reply(f"❌ 支付异常: {exc}")
    return False


def authorize_accounts(accounts):
    selected_accounts = list(dict.fromkeys(str(item).strip() for item in accounts if str(item).strip()))
    if not selected_accounts:
        sender.reply("❌ 没有可授权账号")
        return

    account_infos = []
    for account in selected_accounts:
        info = _get_token_info(account)
        if info.get("uid") and info.get("cookie"):
            account_infos.append({"account": account, "info": info})
    if not account_infos:
        sender.reply("❌ 没有有效账号信息，请重新登录后再试")
        return

    sender.reply(
        f"已选择 {len(account_infos)} 个账号\n"
        "=====设置授权时长=====\n"
        "请输入授权月数，例如 1\n"
        '回复"q"退出\n'
        "=================="
    )
    months_input = sender.input(120000, 1, False)
    if not months_input or str(months_input).strip().lower() == "q":
        sender.reply("✅ 已取消")
        return
    try:
        months = int(str(months_input).strip())
        if months <= 0:
            sender.reply("❌ 月数必须大于 0")
            return
    except ValueError:
        sender.reply("❌ 请输入有效数字")
        return

    vip_money = _cfg_float("Vipmoney", 1)
    coin_cost = _cfg_int("coin", 0)
    total_money = round(len(account_infos) * months * vip_money, 2)
    pay_config = vorto_utils.get_pay_config()
    available = []
    if pay_config.get("qr_pay_switch"):
        available.append(("扫码支付", "qrcode"))
    if pay_config.get("ma_pay_switch"):
        for pay_key, pay_name in pay_config.get("pay_types", {}).items():
            available.append((f"{pay_name}(码支付)", f"mapay_{pay_key}"))
    if coin_cost > 0:
        available.append(("积分兑换", "coin"))
    if not available:
        sender.reply("❌ 未配置任何支付方式，请联系管理员在 Vorto初始化 中开启")
        return

    if len(available) == 1:
        payment_type = available[0][1]
    else:
        menu_lines = [
            "=====选择支付方式=====",
            f"账号: {len(account_infos)}个",
            f"时长: {months}月",
            f"金额: {total_money}元",
            "------------------",
        ]
        menu_lines.extend(f"[{idx}] {name}" for idx, (name, _) in enumerate(available, 1))
        menu_lines.extend(["------------------", '回复"q"退出', "=================="])
        sender.reply("\n".join(menu_lines))
        choice = sender.input(120000, 1, False)
        if not choice or str(choice).strip().lower() == "q":
            sender.reply("✅ 已取消")
            return
        try:
            payment_type = available[int(str(choice).strip()) - 1][1]
        except Exception:
            sender.reply("❌ 无效的选择")
            return

    used_coin = 0
    remaining_points = None
    if payment_type == "qrcode":
        if not _process_qrcode_payment(PLUGIN_NAME, months, total_money):
            return
    elif payment_type.startswith("mapay_"):
        pay_key = payment_type.replace("mapay_", "", 1)
        if not _process_mapay_payment(PLUGIN_NAME, months, total_money, pay_key):
            return
    else:
        used_coin = len(account_infos) * months * coin_cost
        current_points = vorto_utils.get_user_points(userid)
        if current_points < used_coin:
            sender.reply(
                f"=====积分不足=====\n"
                f"❌ 当前: {current_points}\n"
                f"💰 需要: {used_coin}\n"
                "=================="
            )
            return
        if not vorto_utils.update_user_points(userid, current_points - used_coin):
            sender.reply("❌ 积分扣除失败，请联系管理员")
            return
        remaining_points = current_points - used_coin

    success_list = []
    sync_fail_list = []
    fail_list = []
    for item in account_infos:
        account = item["account"]
        info = item["info"]
        try:
            new_expire = vorto_utils.calculate_auth_time(AUTH_BUCKET, account, months=months)
            middleware.bucketSet(AUTH_BUCKET, account, new_expire)
            success_list.append(f"{_mask_account(account)} -> {new_expire}")
            sync_ok, sync_msg = sync_ql_env(account, info)
            if not sync_ok:
                sync_fail_list.append(f"{_mask_account(account)} -> {sync_msg}")
        except Exception as exc:
            fail_list.append(f"{_mask_account(account)} -> {exc}")

    if used_coin and not success_list:
        vorto_utils.update_user_points(userid, remaining_points + used_coin)
        sender.reply("❌ 全部授权失败，积分已退回")
        return

    result_lines = [
        "=====授权完成=====",
        f"账号: {len(account_infos)}个",
        f"时长: {months}月",
        f"支付: {'积分兑换' if payment_type == 'coin' else str(total_money) + '元'}",
        f"✅ 授权成功: {len(success_list)}个",
    ]
    result_lines.extend(success_list[:20])
    if len(success_list) > 20:
        result_lines.append(f"... 共 {len(success_list)} 条成功记录")
    if sync_fail_list:
        result_lines.append(f"⚠️ 面板同步失败: {len(sync_fail_list)}个")
        result_lines.extend(sync_fail_list[:20])
    if fail_list:
        result_lines.append(f"❌ 授权失败: {len(fail_list)}个")
        result_lines.extend(fail_list[:20])
    if used_coin:
        result_lines.append(f"💰 扣除积分: {used_coin}")
        result_lines.append(f"🪙 剩余积分: {remaining_points}")
    result_lines.append("==================")
    sender.reply("\n".join(result_lines))


def manage_account():
    accounts = _get_user_accounts()
    if not accounts:
        sender.reply(
            "=====未绑定账号=====\n"
            "❌ 未找到账号\n"
            '💡 发送"爱路桥登录"绑定\n'
            "=================="
        )
        return

    sender.reply(
        "=====爱路桥管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交面板\n"
        "------------------\n"
        "回复数字选择\n"
        '回复"q"退出\n'
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or str(choice).strip().lower() == "q":
        sender.reply("✅ 已退出")
        return

    accounts, selected = _select_accounts()
    if accounts is None:
        return
    if not selected:
        sender.reply("❌ 未选择有效账号")
        return

    if str(choice).strip() == "1":
        authorize_accounts(selected)
        return

    if str(choice).strip() == "2":
        sender.reply(f'⚠️ 确认删除 {len(selected)} 个账号？回复 y 确认，其它任意内容取消')
        confirm = sender.input(120000, 1, False)
        if not confirm or str(confirm).strip().lower() != "y":
            sender.reply("✅ 已取消")
            return
        remain_accounts = accounts[:]
        success_list = []
        fail_list = []
        for account in selected:
            try:
                if account in remain_accounts:
                    remain_accounts.remove(account)
                middleware.bucketDel(TOKEN_BUCKET, account)
                middleware.bucketDel(AUTH_BUCKET, account)
                try:
                    delete_ql_env(account)
                except Exception:
                    pass
                success_list.append(_mask_account(account))
            except Exception as exc:
                fail_list.append(f"{_mask_account(account)} -> {exc}")
        _save_user_accounts(remain_accounts)
        lines = ["=====删除完成=====", f"✅ 成功: {len(success_list)}个"]
        lines.extend(success_list[:20])
        if fail_list:
            lines.append(f"❌ 失败: {len(fail_list)}个")
            lines.extend(fail_list[:20])
        lines.append("==================")
        sender.reply("\n".join(lines))
        return

    if str(choice).strip() == "3":
        success_list = []
        fail_list = []
        today = _today()
        for account in selected:
            auth_time = str(middleware.bucketGet(AUTH_BUCKET, account) or "").strip()
            if not auth_time or auth_time < today:
                fail_list.append(f"{_mask_account(account)} -> 未授权或已过期")
                continue
            info = _get_token_info(account)
            if not info.get("uid") or not info.get("cookie"):
                fail_list.append(f"{_mask_account(account)} -> 缺少账号凭证，请重新登录")
                continue
            sync_ok, sync_msg = sync_ql_env(account, info)
            if sync_ok:
                success_list.append(_mask_account(account))
            else:
                fail_list.append(f"{_mask_account(account)} -> {sync_msg}")
        lines = ["=====提交结果=====", f"✅ 成功: {len(success_list)}个"]
        lines.extend(success_list[:20])
        if fail_list:
            lines.append(f"❌ 失败: {len(fail_list)}个")
            lines.extend(fail_list[:20])
        lines.append("变量格式: uid#cookie")
        lines.append("==================")
        sender.reply("\n".join(lines))
        return

    sender.reply("❌ 无效的选择")


def _submit_all_authorized_accounts():
    raw_keys = middleware.bucketAllKeys(AUTH_BUCKET) or []
    if isinstance(raw_keys, str):
        raw_keys = [item.strip() for item in raw_keys.split(",") if item.strip()]
    accounts = list(dict.fromkeys(str(item).strip() for item in raw_keys if str(item).strip()))
    if not accounts:
        sender.reply("❌ 未找到已授权账号")
        return

    success_list = []
    fail_list = []
    today = _today()
    for account in accounts:
        auth_time = str(middleware.bucketGet(AUTH_BUCKET, account) or "").strip()
        if not auth_time or auth_time < today:
            fail_list.append(f"{_mask_account(account)} -> 授权已过期")
            continue
        info = _get_token_info(account)
        if not info.get("uid") or not info.get("cookie"):
            fail_list.append(f"{_mask_account(account)} -> 缺少账号凭证")
            continue
        sync_ok, sync_msg = sync_ql_env(account, info)
        if sync_ok:
            success_list.append(_mask_account(account))
        else:
            fail_list.append(f"{_mask_account(account)} -> {sync_msg}")

    lines = ["=====提交全部账号=====", f"✅ 成功: {len(success_list)}个"]
    lines.extend(success_list[:20])
    if fail_list:
        lines.append(f"❌ 失败: {len(fail_list)}个")
        lines.extend(fail_list[:20])
    lines.append("==================")
    sender.reply("\n".join(lines))


def ks_auth():
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return
    sender.reply(
        "=====爱路桥授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "[3] 提交全部已授权账号\n"
        "------------------\n"
        "回复数字选择\n"
        '回复"q"退出\n'
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or str(choice).strip().lower() == "q":
        sender.reply("✅ 已退出")
        return
    choice = str(choice).strip()
    if choice == "1":
        vorto_utils.admin_auth_all_accounts(sender, USER_BUCKET, AUTH_BUCKET, TOKEN_BUCKET, update_ql_callback=update_ql_env)
    elif choice == "2":
        vorto_utils.admin_auth_by_user(sender, USER_BUCKET, AUTH_BUCKET, TOKEN_BUCKET, update_ql_callback=update_ql_env)
    elif choice == "3":
        _submit_all_authorized_accounts()
    else:
        sender.reply("❌ 无效的选择")


def show_tutorial():
    sender.reply(
        "=====爱路桥教程=====\n"
        "用户指令:\n"
        "1. 爱路桥登录 - 绑定账号\n"
        "2. 爱路桥查询 - 查询积分与近期红包记录\n"
        "3. 爱路桥管理 - 授权、删除、提交面板\n"
        "4. 爱路桥教程 - 查看说明\n"
        "------------------\n"
        "管理员指令:\n"
        "1. 爱路桥授权 - 批量授权\n"
        "2. 爱路桥检测 - 检测过期并清理\n"
        "------------------\n"
        "登录方式:\n"
        "按提示输入手机号并完成短信验证码校验\n"
        "一个手机号绑定一个账号\n"
        "=================="
    )


def check_auth_status():
    return vorto_utils.check_auth_status(
        _config_bucket_name(),
        USER_BUCKET,
        AUTH_BUCKET,
        TOKEN_BUCKET,
        PLUGIN_NAME,
        delete_ql_callback=delete_ql_env,
    )


def _is_target_message(message):
    text = str(message or "")
    return PLUGIN_NAME in text or "alq" in text.lower()


def main():
    msg = str(sender.getMessage() or "")
    if sender.getImtype() == "fake":
        try:
            middleware.notifyMasters(check_auth_status())
        except Exception:
            pass
        return

    if ("登录" in msg or "登陆" in msg) and _is_target_message(msg):
        bind_account()
    elif "查询" in msg and _is_target_message(msg):
        query_accounts()
    elif "管理" in msg and _is_target_message(msg):
        manage_account()
    elif "教程" in msg and _is_target_message(msg):
        show_tutorial()
    elif "授权" in msg and _is_target_message(msg):
        ks_auth()
    elif "检测" in msg and _is_target_message(msg):
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()
