#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [language: python]
# [wb: true]
# [pin: true]
# [public: true]
# [rule: ^(登录)$]
# [rule: ^(登陆)$]
# [rule: ^(上车)$]
# [rule: ^(京东续期)$]
# [disable: false]
# [platform: qq,qb,wx,tb,tg,web,wxmp,dd,fs]
# [version: 3.3.0]
# [author: 97610325]
# [price: 49.9]
# [title: 京东登录]
# [icon: https://nos.netease.com/ysf/163f467c1927aac084ffea14e4cdea79.png]
# [description: 京东登录插件<br>指令:登录/登陆/上车/京东续期<br>✨ 三大登录服务:Pro / RabbitPro / 微信Code 各自独立开关<br>✨ 统一菜单极简展示:扫码登录/口令登录/短信登录/账密登录<br>v3.3.0优化: 京东微信Code智能续期双通道转换CK降级(静默+网页协议)提高成功率，管理员一键静默续期免确认。]

# ===================== 京东CK管理兼容参数(青龙容器复用) =====================
# [param: {"required":false,"key":"Joh_CK.Name1","bool":false,"placeholder":"容器1名称","name":"容器1名称(京东CK管理)","desc":"复用京东CK管理插件的容器1配置"}]
# [param: {"required":false,"key":"Joh_CK.container1","bool":false,"placeholder":"URL丨ClientID丨ClientSecret","name":"CK容器1(京东CK管理)","desc":"复用京东CK管理插件的容器1配置"}]
# [param: {"required":false,"key":"Joh_CK.Name2","bool":false,"placeholder":"容器2名称","name":"容器2名称(京东CK管理)","desc":"复用京东CK管理插件的容器2配置"}]
# [param: {"required":false,"key":"Joh_CK.container2","bool":false,"placeholder":"URL丨ClientID丨ClientSecret","name":"CK容器2(京东CK管理)","desc":"复用京东CK管理插件的容器2配置"}]
# [param: {"required":false,"key":"dd_jdck_config.Qinglong","bool":false,"placeholder":"URL丨ClientID丨ClientSecret","name":"默认青龙(京东CK管理)","desc":"复用京东CK管理的默认青龙配置"}]

# ===================== 微信Code登录配置(与Pro/RabbitPro平级) =====================
# [param: {"required":false,"key":"jd_code_config.codeServerUrl","bool":false,"placeholder":"http://192.168.100.55:8000","name":"Code服务地址","desc":"YYB Go API地址(YYB模式),启用Code登录后必填"}]
# [param: {"required":false,"key":"jd_code_config.codeApiType","bool":false,"placeholder":"yyb","name":"Code接口模式","desc":"yyb=YYB Go API(支持扫码绑定+自动续期);simple=仅/login?appId=xxx获取code,不支持绑定"}]
# [param: {"required":false,"key":"jd_code_config.defaultRef","bool":false,"placeholder":"","name":"默认微信账号ref","desc":"YYB模式可填账号ID/UIN/openid,留空则扫码;simple模式可留空"}]
# [param: {"required":false,"key":"jd_code_config.jdAppId","bool":false,"placeholder":"wxf95d0d80e9d5bfc0","name":"京东小程序AppID","desc":"默认 wxf95d0d80e9d5bfc0"}]
# [param: {"required":false,"key":"jd_code_config.QLVarName","bool":false,"placeholder":"JD_COOKIE","name":"青龙变量名","desc":"Code登录写入青龙的变量名"}]
# [param: {"required":false,"key":"jd_code_config.qrPollInterval","bool":false,"placeholder":"3","name":"扫码轮询间隔","desc":"Code扫码状态轮询间隔(秒)"}]
# [param: {"required":false,"key":"jd_code_config.qrTimeout","bool":false,"placeholder":"180","name":"扫码超时","desc":"Code扫码超时时间(秒)"}]
# [param: {"required":false,"key":"jd_code_config.checkBeforeRefresh","bool":true,"name":"续期前检查","desc":"续期前检查账号是否已过期，未过期则跳过续期"}]

# ===================== 服务总开关 =====================
# [param: {"required":false,"key":"jd_code_config.enableCode","bool":true,"name":"启用微信Code登录","desc":"总开关:开启后在登录菜单中显示【微信扫码登录】选项"}]
# [param: {"required":false,"key":"dd_login_config.enablePro","bool":true,"name":"启用Pro服务","desc":"总开关:关闭后Pro相关登录方式全部不可用"}]
# [param: {"required":false,"key":"dd_login_config.enableRabbit","bool":true,"name":"启用RabbitPro服务","desc":"总开关:关闭后RabbitPro相关登录方式全部不可用"}]

# ===================== 各登录方式独立开关 =====================
# [param: {"required":false,"key":"dd_login_config.enableProQr","bool":true,"name":"Pro扫码登录","desc":"Pro服务的扫码登录"}]
# [param: {"required":false,"key":"dd_login_config.enableProShort","bool":true,"name":"Pro口令登录","desc":"Pro服务的口令登录"}]
# [param: {"required":false,"key":"dd_login_config.enableProSms","bool":true,"name":"Pro短信登录","desc":"Pro服务的短信登录"}]
# [param: {"required":false,"key":"dd_login_config.enableRabbitQr","bool":true,"name":"RabbitPro扫码登录","desc":"RabbitPro服务的扫码登录"}]
# [param: {"required":false,"key":"dd_login_config.enableRabbitShort","bool":true,"name":"RabbitPro口令登录","desc":"RabbitPro服务的口令登录"}]
# [param: {"required":false,"key":"dd_login_config.enableRabbitSms","bool":true,"name":"RabbitPro短信登录","desc":"RabbitPro服务的短信登录"}]
# [param: {"required":false,"key":"dd_login_config.enablePassword","bool":true,"name":"账号密码登录","desc":"需要开启Pro或RabbitPro账密接口"}]
# [param: {"required":false,"key":"dd_login_config.passwordApi","bool":false,"name":"账密接口","desc":"0=rabbitPro, 1=Pro"}]

# ===================== 登录服务连接参数 =====================
# [param: {"required":false,"key":"dd_login_config.proUrl","bool":false,"placeholder":"例:http://127.0.0.1:8080","name":"Pro服务地址","desc":"Pro服务地址(留空表示不启用Pro登录)"}]
# [param: {"required":false,"key":"dd_login_config.proBotApiToken","bool":false,"placeholder":"","name":"Pro机器人Token","desc":"Pro机器人Token"}]
# [param: {"required":false,"key":"dd_login_config.rabbitProUrl","bool":false,"placeholder":"例:http://127.0.0.1:8081","name":"RabbitPro服务地址","desc":"RabbitPro服务地址(留空表示不启用RabbitPro登录)"}]
# [param: {"required":false,"key":"dd_login_config.rabbitBotApiToken","bool":false,"placeholder":"","name":"RabbitPro机器人Token","desc":"RabbitPro机器人Token"}]
# [param: {"required":false,"key":"dd_login_config.qrCookieType","bool":false,"placeholder":"1=服务管理后台/2=青龙","name":"扫码写入方式","desc":"1=服务管理后台接收/2=写入青龙"}]
# [param: {"required":false,"key":"dd_login_config.rabbitProContainerId","bool":false,"placeholder":"0","name":"RabbitPro容器ID","desc":"RabbitPro容器ID(qrCookieType=1时使用)"}]

# ===================== 其他配置 =====================
# [param: {"required":false,"key":"dd_login_config.pushAdminOn","bool":false,"placeholder":"","name":"通知管理员","desc":"登录结果通知管理员"}]
# [param: {"required":false,"key":"dd_login_config.pushPlatform","bool":false,"placeholder":"qq&wx","name":"通知平台","desc":"多个用&分隔"}]
# [param: {"required":false,"key":"dd_login_config.adminID","bool":false,"placeholder":"","name":"管理员ID","desc":"接收通知的管理员ID"}]
# [param: {"required":false,"key":"dd_login_config.whiteList","bool":false,"placeholder":"留空不限","name":"群白名单","desc":"留空不限制,多个用逗号"}]
# [param: {"required":false,"key":"dd_login_config.inlineCommand","bool":false,"placeholder":"京东查询","name":"登录后执行命令","desc":"登录成功后自动执行"}]
# [param: {"required":false,"key":"dd_login_config.qrCodeBaseUrl","bool":false,"placeholder":"https://api.qqsuu.cn/api/dm-qrcode?frame=1&e=L&text=","name":"二维码生成地址","desc":"二维码生成API前缀"}]
# [param: {"required":false,"key":"dd_login_config.saveHistory","bool":true,"placeholder":"","name":"保存登录历史","desc":"保存手机号密码以便一键登录"}]
# [param: {"required":false,"key":"dd_login_config.historyLimit","bool":false,"placeholder":"10","name":"历史账号数","desc":"每个用户最多保存历史账号数"}]
# [param: {"required":false,"key":"dd_login_config.maxHistoryDisplay","bool":false,"placeholder":"5","name":"菜单显示历史账号数","desc":"登录菜单最多显示几个历史账号"}]
# [param: {"required":false,"key":"dd_login_config.remarksOpen","bool":false,"placeholder":"","name":"询问备注","desc":"新用户登录后询问备注"}]
# [param: {"required":false,"key":"dd_login_config.QLVarName","bool":false,"placeholder":"JD_COOKIE","name":"青龙CK变量名","desc":"Cookie保存到青龙的变量名(可与京东CK管理一致)"}]
# [param: {"required":false,"key":"dd_login_config.WSCKVarName","bool":false,"placeholder":"JD_R_WSCK","name":"青龙WSKEY变量名","desc":"WSKEY保存到青龙的变量名"}]
# [param: {"required":false,"key":"dd_login_config.JD_AUTO_PWD","bool":false,"placeholder":"JD_AUTO_PWD","name":"账密变量名","desc":"保存账密的青龙变量名"}]
# [param: {"required":false,"key":"dd_login_config.ProxyAPI","bool":false,"placeholder":"例:http://api.xxx.com/getip","name":"代理API","desc":"代理IP提取API(CK检测/京东登录/Code服务共用)。留空则不启用代理。自动复用京东查询插件 dd_jd_query_config.ProxyAPI"}]
# [param: {"required":false,"key":"dd_login_config.ProxyScope","bool":false,"placeholder":"all","name":"代理范围","desc":"all=CK检测+登录+Code服务全启用;ck=仅CK检测;login=仅登录相关;code=仅Code服务"}]
# [param: {"required":false,"key":"dd_login_config.ProxyTimeout","bool":false,"placeholder":"10","name":"代理超时","desc":"单次代理请求超时(秒)"}]
# [param: {"required":false,"key":"dd_login_config.phoneInputTip","bool":false,"placeholder":"请输入11位手机号:","name":"手机号提示","desc":"手机号输入提示"}]
# [param: {"required":false,"key":"dd_login_config.codeTip","bool":false,"placeholder":"请输入6位验证码:","name":"验证码提示","desc":"验证码输入提示"}]
# [param: {"required":false,"key":"dd_login_config.passwordTip","bool":false,"placeholder":"请输入8到20位密码:","name":"密码提示","desc":"账密登录密码输入提示"}]
# [param: {"required":false,"key":"dd_login_config.passwordRetryLimit","bool":false,"placeholder":"3","name":"密码错误重试","desc":"账密登录密码最大错误重试次数"}]
# [param: {"required":false,"key":"dd_login_config.showAccountInfo","bool":true,"placeholder":"","name":"登录后显示账号","desc":"登录成功时显示账号信息"}]
# [param: {"required":false,"key":"dd_login_config.enableQQ","bool":true,"placeholder":"","name":"QQ群可用","desc":"是否在QQ群可用"}]
# [param: {"required":false,"key":"dd_login_config.enableQX","bool":true,"placeholder":"","name":"QQ私聊可用","desc":"是否在QQ私聊可用"}]
# [param: {"required":false,"key":"dd_login_config.enableWX","bool":true,"placeholder":"","name":"微信可用","desc":"是否在微信可用"}]
# [param: {"required":false,"key":"dd_login_config.enableTG","bool":true,"placeholder":"","name":"Telegram可用","desc":"是否在Telegram可用"}]
# [param: {"required":false,"key":"dd_login_config.enableOther","bool":true,"placeholder":"","name":"其他平台可用","desc":"是否在其他平台可用"}]

import base64
import hashlib
import json
import os
import random
import re
import time
import urllib.parse

import requests
import middleware

requests.packages.urllib3.disable_warnings()

# ===================== 模块级 sender 捕获 (多用户安全) =====================
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID) if senderID else None
userid = sender.getUserID() if sender else ""

def _log(*args, **kwargs):
    """带时间戳的日志输出"""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [京东登录]", *args, **kwargs)

# ===================== 常量 =====================
TIMEOUT_MSG = "⏰ 操作超时,已取消本次操作"
INPUT_TIMEOUT = 60
QUIT_KEYWORDS = ("q", "Q", "退出", "取消")
TIMEOUT = 30

JD_APPID_DEFAULT = "wxf95d0d80e9d5bfc0"
JD_SILENT_AUTH_URL = "https://wxapplogin.m.jd.com/cgi-bin/jxpp/silentauthlogin"
JD_LOGIN_REDIRECT_URL = "https://wqlogin1.jd.com/mlogin/wxv3/LoginRedirect"

BUCKET_HISTORY = "dd_login_history"
BUCKET_PASSWORD = "dd_login_pwd"
BUCKET_QL_TOKEN = "dd_login_ql_token"


# ===================== 通用工具 =====================

def _cfg(bucket, key, default=""):
    value = middleware.bucketGet(bucket, key)
    return value if value not in (None, "") else default

def _to_bool(value, default=False):
    if isinstance(value, bool): return value
    if isinstance(value, str):
        if value.lower() == "true": return True
        if value.lower() == "false": return False
    return default

def _to_int(value, default=0):
    try: return int(str(value).strip())
    except: return default

def get_input(sender, timeout=INPUT_TIMEOUT, validator=None, error_tip=None, retry_limit=0):
    attempts = 0
    while True:
        try:
            inp = sender.input(timeout * 1000, 1, False)
        except Exception:
            sender.reply(TIMEOUT_MSG)
            return None
        if not inp:
            sender.reply(TIMEOUT_MSG)
            return None
        if isinstance(inp, dict):
            inp = inp.get("text") or inp.get("message") or ""
        text = str(inp).strip()
        if text in QUIT_KEYWORDS:
            sender.reply("✅ 已退出")
            return None
        if validator is None:
            return text
        try:
            ok = validator(text)
        except Exception:
            ok = False
        if ok:
            return text
        attempts += 1
        if retry_limit > 0 and attempts >= retry_limit:
            sender.reply("❌ 错误次数过多,已退出")
            return None
        if error_tip:
            sender.reply(error_tip)

def friendly_err(e):
    msg = str(e)
    if "Remote end closed" in msg: return "代理连接被关闭"
    if "timed out" in msg or "Timeout" in msg: return "连接超时"
    if "Connection refused" in msg: return "连接被拒绝"
    if "getaddrinfo" in msg: return "域名解析失败"
    if "Connection reset" in msg: return "连接被重置"
    if "SSL" in msg or "ssl" in msg: return "SSL错误"
    return msg

def mask_phone(phone):
    if not phone: return ""
    phone = str(phone)
    if len(phone) != 11: return phone
    return phone[:3] + "****" + phone[7:]

def decode_pin(pin):
    try: return urllib.parse.unquote(str(pin))
    except: return str(pin)

def encode_pin(pin):
    try:
        pin_str = str(pin)
        decoded = urllib.parse.unquote(pin_str)
        if decoded != pin_str: return pin_str
        return urllib.parse.quote(decoded, safe="")
    except: return str(pin)

def get_platform(sender):
    for method_name in ("getImtype", "getImType"):
        try:
            method = getattr(sender, method_name)
            im_type = method()
            if im_type:
                im_type = str(im_type).upper()
                if im_type == "QB": return "QQ"
                if im_type == "WXMP": return "WX"
                if im_type == "DD": return "DD"
                if im_type == "FS": return "FS"
                return im_type
        except: pass
    return "QQ"

def is_group_chat(sender):
    try:
        chat_id = sender.getChatID()
        return bool(chat_id) and str(chat_id) != "0"
    except: return False


# ===================== 历史账号管理 =====================

def get_history_accounts(userid):
    raw = middleware.bucketGet(BUCKET_HISTORY, str(userid))
    if not raw: return []
    try:
        accounts = json.loads(str(raw))
        if isinstance(accounts, list): return accounts
    except: pass
    return []

def add_history_account(userid, phone, pwd="", method=""):
    accounts = get_history_accounts(userid)
    accounts = [a for a in accounts if str(a.get("phone") or "") != str(phone)]
    # method: "sms"=短信登录保存, "password"=账密登录保存, 空字符串=兼容老数据
    accounts.insert(0, {
        "phone": str(phone),
        "pwd": str(pwd or ""),
        "method": str(method or "").strip().lower(),
        "last_used": int(time.time()),
    })
    config = get_config()
    accounts = accounts[:max(1, config["history_limit"])]
    try:
        middleware.bucketSet(BUCKET_HISTORY, str(userid), json.dumps(accounts, ensure_ascii=False))
    except: pass
    if pwd:
        try:
            middleware.bucketSet(BUCKET_PASSWORD, str(phone), str(pwd))
        except: pass

def get_saved_password(phone):
    try: return middleware.bucketGet(BUCKET_PASSWORD, str(phone)) or ""
    except: return ""

# ===================== 配置读取 =====================

def get_config():
    api_type = str(_cfg("jd_code_config", "codeApiType", "yyb")).strip().lower()
    if api_type not in ("yyb", "simple"): api_type = "yyb"

    return {
        "enable_pro": _to_bool(_cfg("dd_login_config", "enablePro", "true"), True),
        "enable_rabbit": _to_bool(_cfg("dd_login_config", "enableRabbit", "true"), True),
        "enable_pro_qr": _to_bool(_cfg("dd_login_config", "enableProQr", "true"), True),
        "enable_pro_short": _to_bool(_cfg("dd_login_config", "enableProShort", "true"), True),
        "enable_pro_sms": _to_bool(_cfg("dd_login_config", "enableProSms", "true"), True),
        "enable_rabbit_qr": _to_bool(_cfg("dd_login_config", "enableRabbitQr", "true"), True),
        "enable_rabbit_short": _to_bool(_cfg("dd_login_config", "enableRabbitShort", "true"), True),
        "enable_rabbit_sms": _to_bool(_cfg("dd_login_config", "enableRabbitSms", "true"), True),
        "enable_password": _to_bool(_cfg("dd_login_config", "enablePassword", "false"), False),
        "password_api": _to_int(_cfg("dd_login_config", "passwordApi", "0"), 0),
        "pro_url": str(_cfg("dd_login_config", "proUrl", "")).strip().rstrip("/"),
        "pro_token": str(_cfg("dd_login_config", "proBotApiToken", "")).strip(),
        "rabbit_url": str(_cfg("dd_login_config", "rabbitProUrl", "")).strip().rstrip("/"),
        "rabbit_token": str(_cfg("dd_login_config", "rabbitBotApiToken", "")).strip(),
        "qr_cookie_type": _to_int(_cfg("dd_login_config", "qrCookieType", "2"), 2),
        "rabbit_container_id": _to_int(_cfg("dd_login_config", "rabbitProContainerId", "0"), 0),
        "push_admin": _to_bool(_cfg("dd_login_config", "pushAdminOn", "false"), False),
        "push_platform": str(_cfg("dd_login_config", "pushPlatform", "")).strip(),
        "admin_id": str(_cfg("dd_login_config", "adminID", "")).strip(),
        "white_list": [x.strip() for x in str(_cfg("dd_login_config", "whiteList", "")).split(",") if x.strip()],
        "inline_command": str(_cfg("dd_login_config", "inlineCommand", "")).strip(),
        "qr_base_url": str(_cfg("dd_login_config", "qrCodeBaseUrl", "https://api.qqsuu.cn/api/dm-qrcode?frame=1&e=L&text=")).strip(),
        "save_history": _to_bool(_cfg("dd_login_config", "saveHistory", "true"), True),
        "history_limit": max(1, _to_int(_cfg("dd_login_config", "historyLimit", "10"), 10)),
        "max_history_display": max(0, _to_int(_cfg("dd_login_config", "maxHistoryDisplay", "5"), 5)),
        "remarks_open": _to_bool(_cfg("dd_login_config", "remarksOpen", "false"), False),
        "ql_var_name": str(_cfg("dd_login_config", "QLVarName", "JD_COOKIE") or "JD_COOKIE").strip(),
        "wsck_var_name": str(_cfg("dd_login_config", "WSCKVarName", "JD_R_WSCK") or "JD_R_WSCK").strip(),
        "auto_pwd_var": str(_cfg("dd_login_config", "JD_AUTO_PWD", "JD_AUTO_PWD") or "JD_AUTO_PWD").strip(),
        "phone_input_tip": str(_cfg("dd_login_config", "phoneInputTip", "请输入11位手机号:")),
        "code_tip": str(_cfg("dd_login_config", "codeTip", "请输入6位验证码:")),
        "password_tip": str(_cfg("dd_login_config", "passwordTip", "请输入8到20位密码:")),
        "password_retry_limit": max(1, _to_int(_cfg("dd_login_config", "passwordRetryLimit", "3"), 3)),
        "show_account_info": _to_bool(_cfg("dd_login_config", "showAccountInfo", "true"), True),
        "enableqq": _to_bool(_cfg("dd_login_config", "enableQQ", "true"), True),
        "enableqx": _to_bool(_cfg("dd_login_config", "enableQX", "true"), True),
        "enablewx": _to_bool(_cfg("dd_login_config", "enableWX", "true"), True),
        "enabletg": _to_bool(_cfg("dd_login_config", "enableTG", "true"), True),
        "enableother": _to_bool(_cfg("dd_login_config", "enableOther", "true"), True),
        "enable_code": _to_bool(_cfg("jd_code_config", "enableCode", "false"), False),
        "code_url": str(_cfg("jd_code_config", "codeServerUrl", "")).strip().rstrip("/"),
        "code_api_type": api_type,
        "code_default_ref": str(_cfg("jd_code_config", "defaultRef", "")).strip(),
        "code_jd_app_id": str(_cfg("jd_code_config", "jdAppId", JD_APPID_DEFAULT) or JD_APPID_DEFAULT).strip() or JD_APPID_DEFAULT,
        "code_ql_var_name": str(_cfg("jd_code_config", "QLVarName", "JD_COOKIE") or "JD_COOKIE").strip(),
        "code_qr_poll_interval": max(1, _to_int(_cfg("jd_code_config", "qrPollInterval", "3"), 3)),
        "code_qr_timeout": max(60, _to_int(_cfg("jd_code_config", "qrTimeout", "180"), 180)),
        "code_check_before_refresh": _to_bool(_cfg("jd_code_config", "checkBeforeRefresh", "true"), True),
        "code_auto_refresh_on_login": _to_bool(_cfg("jd_code_config", "autoRefreshOnLogin", "false"), False),
        "code_auto_refresh_interval": max(60, _to_int(_cfg("jd_code_config", "autoRefreshInterval", "21600"), 21600)),
        # 代理 IP 配置
        "proxy_api": str(_cfg("dd_login_config", "ProxyAPI", "") or _cfg("dd_jd_query_config", "ProxyAPI", "")).strip(),
        "proxy_scope": str(_cfg("dd_login_config", "ProxyScope", "all")).strip().lower() or "all",
        "proxy_timeout": max(3, _to_int(_cfg("dd_login_config", "ProxyTimeout", "10"), 10)),
    }

def check_admin(sender, config):
    try: return bool(sender.isAdmin())
    except: return False

def check_white_list(sender, config):
    if not config["white_list"]: return True
    if not is_group_chat(sender): return True
    if check_admin(sender, config): return True
    try:
        chat_id = str(sender.getChatID() or "")
        return chat_id in config["white_list"]
    except: return False

def check_platform_enabled(config, sender):
    platform = get_platform(sender)
    is_group = is_group_chat(sender)
    if platform == "QQ" and is_group: key = "enableqq"
    elif platform == "QX" or (platform == "QQ" and not is_group): key = "enableqx"
    elif platform in ("WX", "WC", "WXMP"): key = "enablewx"
    elif platform == "TG": key = "enabletg"
    else: key = "enableother"
    return _to_bool(config.get(key, "true"), True)

def is_pro_configured(config):
    return config["enable_pro"] and bool(config["pro_url"] and config["pro_token"])

def is_rabbit_configured(config):
    return config["enable_rabbit"] and bool(config["rabbit_url"] and config["rabbit_token"])

def is_code_configured(config):
    return config.get("enable_code", False) and bool(config.get("code_url", ""))

# ===================== ✨ 动态登录菜单 =====================

def build_login_menu(config, history):
    enabled_methods = []
    lines = ["🔐 选择登录方式", "━━━━━━━━━━━━━━"]

    pro_ok = is_pro_configured(config)
    rabbit_ok = is_rabbit_configured(config)
    code_ok = is_code_configured(config)

    method_idx = 0

    def add_method(method_id, tip):
        nonlocal method_idx
        method_idx += 1
        enabled_methods.append({
            "id": method_id,
            "index": method_idx,
            "tip": tip,
        })
        lines.append(f"【{method_idx}】{tip}")

    if code_ok:
        add_method("code_qr", "微信扫码登录")

    if pro_ok and config["enable_pro_qr"]:
        add_method("pro_qr", "京东APP扫码登录")
    elif rabbit_ok and config["enable_rabbit_qr"]:
        add_method("rabbit_qr", "京东APP扫码登录")

    if pro_ok and config["enable_pro_short"]:
        add_method("pro_short", "口令登录")
    elif rabbit_ok and config["enable_rabbit_short"]:
        add_method("rabbit_short", "口令登录")

    if pro_ok and config["enable_pro_sms"]:
        add_method("pro_sms", "短信登录")
    elif rabbit_ok and config["enable_rabbit_sms"]:
        add_method("rabbit_sms", "短信登录")

    if config["enable_password"] and (pro_ok or rabbit_ok):
        add_method("password", "账号密码登录")

    lines.append("━━━━━━━━━━━━━━")
    lines.append("(q 退出)")
    return lines, enabled_methods


def build_sms_submenu(config, history):
    """短信登录二级菜单:【0】新增手机号 + 【1-N】短信保存的历史账号一键登录
    只显示 method=sms 的历史账号, 账密保存的不在此处显示(账密登录走主菜单单独入口)
    """
    lines = ["📱 短信登录", "━━━━━━━━━━━━━━"]
    enabled = []

    # 0 = 新增手机号(走 run_xxx_sms_login 内部输入手机号流程)
    enabled.append({
        "id": "sms_new",
        "index": 0,
        "tip": "新增手机号",
    })
    lines.append("【0】➕ 新增手机号")

    sms_history = []
    for a in history:
        m = str(a.get("method", "") or "").strip().lower()
        if not m:
            # 兼容老数据: 无method字段时按pwd是否为空判断 (pwd空=sms)
            m = "sms" if not a.get("pwd") else "password"
        if m == "sms":
            sms_history.append(a)
    if config["save_history"] and sms_history:
        max_display = min(len(sms_history), config["max_history_display"])
        if max_display > 0:
            lines.append("━━━━━━━━━━━━━━")
            lines.append("📱 历史账号一键登录:")
            for i in range(max_display):
                phone = sms_history[i].get("phone", "")
                if not phone: continue
                masked = mask_phone(phone)
                last_used = sms_history[i].get("last_used", 0)
                time_str = ""
                if last_used:
                    try:
                        dt = time.strftime("%m-%d %H:%M", time.localtime(int(last_used)))
                        time_str = f" ({dt})"
                    except: pass
                idx = i + 1
                enabled.append({
                    "id": "sms_history",
                    "index": idx,
                    "tip": f"历史账号 {masked}{time_str}",
                    "phone": phone,
                    "history_idx": i,  # 在 sms_history 子列表里的位置
                })
                lines.append(f"【{idx}】历史账号 {masked}{time_str}")

    lines.append("━━━━━━━━━━━━━━")
    lines.append("(q 退出)")
    return lines, enabled


# ===================== 青龙面板客户端 =====================

def load_ql_panels():
    panels = []
    for i in (1, 2):
        container_str = middleware.bucketGet("Joh_CK", f"container{i}")
        if container_str:
            parts = str(container_str).split("丨")
            if len(parts) >= 3:
                name = middleware.bucketGet("Joh_CK", f"Name{i}") or f"容器{i}"
                panels.append({
                    "Name": name,
                    "Host": parts[0].strip().rstrip("/"),
                    "ClientID": parts[1].strip(),
                    "ClientSecret": parts[2].strip(),
                    "Version": "2.17.0",
                })
    if not panels:
        default_str = middleware.bucketGet("dd_jdck_config", "Qinglong")
        if default_str:
            parts = str(default_str).split("丨")
            if len(parts) >= 3:
                panels.append({
                    "Name": "默认容器",
                    "Host": parts[0].strip().rstrip("/"),
                    "ClientID": parts[1].strip(),
                    "ClientSecret": parts[2].strip(),
                    "Version": "2.17.0",
                })
    return panels

class QingLongClient:
    def __init__(self, panel):
        self.panel = panel
        self.host = str(panel.get("Host") or "").strip().rstrip("/")
        self.client_id = str(panel.get("ClientID") or "")
        self.client_secret = str(panel.get("ClientSecret") or "")
        version_parts = str(panel.get("Version") or "2.17.0").split(".")
        try: minor = int(version_parts[1]) if len(version_parts) > 1 else 17
        except: minor = 17
        self.id_key = "_id" if minor < 11 else "id"

    def get_token(self, force=False):
        cache_key = f"{self.client_id}_token"
        if not force:
            cached = middleware.bucketGet(BUCKET_QL_TOKEN, cache_key)
            if cached:
                try:
                    data = json.loads(str(cached))
                    if int(data.get("expiration", 0)) * 1000 > int(time.time() * 1000):
                        return data
                except: pass
        if not self.host or not self.client_id or not self.client_secret: return None
        try:
            url = f"{self.host}/open/auth/token?client_id={urllib.parse.quote(self.client_id)}&client_secret={urllib.parse.quote(self.client_secret)}"
            resp = requests.get(url, timeout=30, verify=False)
            if resp.status_code != 200: return None
            body = resp.json()
            if body.get("code") == 200 and "data" in body:
                middleware.bucketSet(BUCKET_QL_TOKEN, cache_key, json.dumps(body["data"]))
                return body["data"]
        except: pass
        return None

    def request(self, method, path, body=None):
        token_data = self.get_token()
        if not token_data: raise Exception("获取青龙Token失败")
        headers = {
            "Authorization": f"{token_data.get('token_type', 'Bearer')} {token_data.get('token')}",
            "Content-Type": "application/json",
        }
        url = f"{self.host}{path}"
        try:
            if method.upper() == "GET": resp = requests.get(url, headers=headers, timeout=30, verify=False)
            elif method.upper() == "POST": resp = requests.post(url, headers=headers, json=body or {}, timeout=30, verify=False)
            elif method.upper() == "PUT": resp = requests.put(url, headers=headers, json=body or {}, timeout=30, verify=False)
            elif method.upper() == "DELETE": resp = requests.delete(url, headers=headers, json=body or {}, timeout=30, verify=False)
            
            if resp.status_code == 401:
                token_data = self.get_token(force=True)
                if not token_data: raise Exception("青龙Token刷新失败")
                headers["Authorization"] = f"{token_data.get('token_type', 'Bearer')} {token_data.get('token')}"
                if method.upper() == "GET": resp = requests.get(url, headers=headers, timeout=30, verify=False)
                elif method.upper() == "POST": resp = requests.post(url, headers=headers, json=body or {}, timeout=30, verify=False)
                elif method.upper() == "PUT": resp = requests.put(url, headers=headers, json=body or {}, timeout=30, verify=False)
                elif method.upper() == "DELETE": resp = requests.delete(url, headers=headers, json=body or {}, timeout=30, verify=False)
            res = resp.json()
            if res.get("code") == 200: return res.get("data")
            raise Exception(res.get("message") or "请求失败")
        except Exception as e:
            raise Exception(friendly_err(e))

    def all_envs(self):
        return self.request("GET", "/open/envs") or []

    def search_envs(self, remark):
        try: return self.request("GET", f"/open/envs?searchValue={urllib.parse.quote(str(remark))}") or []
        except: return []

    def add_envs(self, envs):
        return self.request("POST", "/open/envs", envs)

    def edit_env(self, env):
        return self.request("PUT", "/open/envs", env)

    def enable_env(self, env_id):
        return self.request("PUT", "/open/envs/enable", [env_id])

    def disable_env(self, env_id):
        return self.request("PUT", "/open/envs/disable", [env_id])

    def delete_env(self, env_id):
        return self.request("DELETE", "/open/envs", [env_id])

# ===================== 账号绑定 =====================

def bind_user_pin_with_sender(sender, userid, pin):
    platform = get_platform(sender)
    bucket = f"pin{platform}"
    try: middleware.bucketSet(bucket, str(pin), str(userid))
    except: pass
    try:
        raw = middleware.bucketGet("dd_jdck_user", str(userid))
        if raw:
            try:
                arr = json.loads(str(raw))
                if not isinstance(arr, list): arr = []
            except: arr = []
        else:
            arr = []
        if str(pin) not in arr:
            arr.append(str(pin))
            middleware.bucketSet("dd_jdck_user", str(userid), json.dumps(arr, ensure_ascii=False))
    except: pass

# ===================== WSKEY/Cookie 上传到青龙 =====================

def get_pin_from_cookie(cookie):
    m = re.search(r"pt_pin=([^;\s]+)", cookie or "")
    return m.group(1) if m else ""

def get_pin_from_wskey(wskey):
    m = re.search(r"(?:^|[;])pin=([^;\s]+)", wskey or "")
    return m.group(1) if m else ""

def commit_cookie_to_ql(sender, userid, cookie_value, env_name="JD_COOKIE", skip_bind=False, append_remark=None):
    panels = load_ql_panels()
    if not panels:
        sender.reply("⚠️ 未配置青龙面板,Cookie未写入\n💡 请在京东CK管理插件中配置 Joh_CK.container1")
        return False, []
    pin = get_pin_from_cookie(cookie_value)
    if not pin:
        sender.reply("❌ Cookie格式错误,未找到pt_pin")
        return False, []
    pin_dec = decode_pin(pin)
    pin_enc = encode_pin(pin)
    final_cookie = cookie_value
    if any(ord(c) > 127 for c in pin_dec):
        encoded = urllib.parse.quote(pin_dec, safe="")
        final_cookie = re.sub(r"pt_pin=([^;\s]+)", f"pt_pin={encoded}", cookie_value)
    success_panels = []
    for panel_info in panels:
        try:
            ql = QingLongClient(panel_info)
            envs = ql.all_envs()
            matched = None
            for env in envs:
                if env.get("name") != env_name: continue
                value = str(env.get("value", ""))
                env_pin_m = re.search(r"pt_pin=([^;\s]+)", value)
                if not env_pin_m: continue
                env_pin = env_pin_m.group(1)
                env_pin_dec = decode_pin(env_pin)
                env_pin_enc = encode_pin(env_pin)
                if pin in (env_pin, env_pin_dec, env_pin_enc) or pin_dec in (env_pin, env_pin_dec, env_pin_enc) or pin_enc in (env_pin, env_pin_dec, env_pin_enc):
                    matched = env
                    break
            remark = pin_dec
            if matched:
                env_id = matched.get(ql.id_key) or matched.get("_id") or matched.get("id")
                if not env_id: continue
                old_remarks = str(matched.get("remarks", "") or "")
                if old_remarks: 
                    remark = old_remarks
                    # 自动把微信昵称追加到青龙备注中，方便下次续期精准匹配
                    if append_remark and append_remark not in remark:
                        remark = f"{remark} ({append_remark})"
                else:
                    if append_remark and append_remark not in remark:
                        remark = f"{pin_dec} ({append_remark})"
                
                ql.edit_env({
                    "name": env_name,
                    "value": final_cookie,
                    "remarks": remark,
                    ql.id_key: env_id,
                })
                ql.enable_env(env_id)
            else:
                if append_remark and append_remark not in remark:
                    remark = f"{pin_dec} ({append_remark})"
                ql.add_envs([{
                    "name": env_name,
                    "value": final_cookie,
                    "remarks": remark,
                }])
            success_panels.append(panel_info.get("Name", "未知"))
        except Exception as e:
            sender.reply(f"❌ 写入青龙 [{panel_info.get('Name', '?')}] 失败:{friendly_err(e)}")
            
    if success_panels:
        if not skip_bind:
            bind_user_pin_with_sender(sender, userid, pin_dec)
        return True, success_panels
    return False, []

def commit_wskey_to_ql(sender, userid, wskey_value, env_name="JD_R_WSCK", skip_bind=False):
    panels = load_ql_panels()
    if not panels:
        sender.reply("⚠️ 未配置青龙面板,WSKEY未写入")
        return False, []
    pin = get_pin_from_wskey(wskey_value)
    if not pin:
        sender.reply("❌ WSKEY格式错误,未找到pin")
        return False, []
    pin_dec = decode_pin(pin)
    success_panels = []
    for panel_info in panels:
        try:
            ql = QingLongClient(panel_info)
            envs = ql.all_envs()
            matched = None
            for env in envs:
                if env.get("name") != env_name: continue
                value = str(env.get("value", ""))
                env_pin_m = re.search(r"(?:^|[;])pin=([^;\s]+)", value)
                if not env_pin_m: continue
                env_pin = env_pin_m.group(1)
                if pin == env_pin or pin_dec == decode_pin(env_pin):
                    matched = env
                    break
            remark = pin_dec
            if matched:
                env_id = matched.get(ql.id_key) or matched.get("_id") or matched.get("id")
                if not env_id: continue
                old_remarks = str(matched.get("remarks", "") or "")
                if old_remarks: remark = old_remarks
                ql.edit_env({
                    "name": env_name,
                    "value": wskey_value,
                    "remarks": remark,
                    ql.id_key: env_id,
                })
                ql.enable_env(env_id)
            else:
                ql.add_envs([{
                    "name": env_name,
                    "value": wskey_value,
                    "remarks": remark,
                }])
            success_panels.append(panel_info.get("Name", "未知"))
        except Exception as e:
            sender.reply(f"❌ 写入WSKEY [{panel_info.get('Name', '?')}] 失败:{friendly_err(e)}")
    if success_panels:
        if not skip_bind:
            bind_user_pin_with_sender(sender, userid, pin_dec)
        return True, success_panels
    return False, []

# ===================== RabbitPro 加密 =====================

def rabbit_pro_encrypt_pwd(account, pwd):
    try: from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except Exception as exc: raise RuntimeError("RabbitPro账密登录需要安装 cryptography 库") from exc
    digest = hashlib.sha512(f"#(*():dfgjn^%&89$%#{account}#(*():dfgjn^%&89$%#".encode()).digest()
    key = digest[:32]
    nonce = os.urandom(12)
    padded = os.urandom(16) + pwd.encode() + os.urandom(16)
    encrypted = AESGCM(key).encrypt(nonce, padded, None)
    ciphertext, tag = encrypted[:-16], encrypted[-16:]
    return base64.b64encode(tag + ciphertext + nonce).decode()

# ===================== 二维码URL =====================

def qr_code_url(qrkey, base):
    raw = f"https://qr.m.jd.com/p?k={urllib.parse.quote(qrkey)}&size=150"
    return (base + raw) if base else raw

def jd_scan_command_url(qrkey):
    params = {
        "category": "jump", "des": "scanLogin", "key": qrkey,
        "sourceType": "JSHOP_SOURCE_TYPE", "sourceValue": "JSHOP_SOURCE_VALUE",
        "M_sourceFrom": "mxz", "msf_type": "auto",
    }
    encoded = urllib.parse.quote(json.dumps(params, separators=(",", ":")))
    return f"https://lzkj-isv.isvjcloud.com/lzclient/cjwx/common/openJDApp.html?actlink=openapp.jdmobile://virtual?params={encoded}"

# ===================== 通知 =====================

def notify_admin(config, msg):
    if not config["push_admin"] or not config["admin_id"]: return
    platforms = [x.strip() for x in config["pushplatform"].split("&") if x.strip()] if "pushplatform" in config else [x.strip() for x in config.get("push_platform", "").split("&") if x.strip()]
    if not platforms: platforms = ["qq"]
    try: middleware.pushAdmin(platforms, msg)
    except: pass

def run_inline_command(config):
    cmd = config.get("inline_command", "").strip()
    if not cmd: return
    try:
        inline_fn = getattr(middleware, "inline", None)
        if inline_fn: inline_fn(cmd)
    except Exception as e:
        _log("inline命令执行失败:", e)

# ===================== ✨ 微信Code登录核心实现 =====================

def _extract_proxy_from_text(text):
    text = (text or "").strip()
    if not text: return None
    ip, port, user, pwd = "", 0, "", ""
    try:
        js = text.find("{"); je = text.rfind("}")
        if js != -1 and je != -1 and je > js:
            data = json.loads(text[js:je + 1])
            def _ext(d):
                if not isinstance(d, dict) or not d.get("ip") or not d.get("port"): return None
                return {"ip": str(d.get("ip")), "port": int(d.get("port")),
                        "user": str(d.get("account") or d.get("user") or ""),
                        "pass": str(d.get("password") or d.get("pass") or "")}
            info = _ext(data)
            if not info and isinstance(data.get("data"), dict):
                inner = data["data"]
                if isinstance(inner.get("list"), list) and inner["list"]:
                    info = _ext(inner["list"][0])
                else:
                    info = _ext(inner)
            if info: ip, port, user, pwd = info["ip"], info["port"], info["user"], info["pass"]
    except Exception: pass
    if not ip:
        m = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})[:\s\t]+(\d{1,5})", text)
        if m: ip, port = m.group(1), int(m.group(2))
    if not ip or not port: return None
    if 1 <= port > 65535: return None
    if user and pwd:
        url = f"http://{urllib.parse.quote(user)}:{urllib.parse.quote(pwd)}@{ip}:{port}"
    else:
        url = f"http://{ip}:{port}"
    return {"url": url, "ip": ip, "port": port, "display": f"{ip}:{port}"}

def fetch_proxy_info(proxy_api, timeout=10):
    if not proxy_api: return None
    try:
        resp = requests.get(proxy_api, timeout=timeout, verify=False,
                            headers={"User-Agent": "JDLoginPlugin/3.3.0", "Accept": "*/*"})
        info = _extract_proxy_from_text(resp.text)
        if info: _log(f"代理获取成功: {info['display']}")
        return info
    except Exception as e:
        _log(f"代理API拉取失败: {friendly_err(e)}")
        return None

def build_proxies(proxy_info):
    if not proxy_info or not proxy_info.get("url"): return None
    return {"http": proxy_info["url"], "https": proxy_info["url"]}

def _proxy_in_scope(scope, area):
    scope = (scope or "all").strip().lower()
    if scope in ("no", "off", "false", "0", "disable", "disabled"): return False
    if scope in ("all", "*", ""): return True
    for token in scope.replace("，", ",").split(","):
        if token.strip() == area: return True
    return False

def _request_with_proxy(method, url, proxy_api=None, scope="all", area="login", timeout=10, **kwargs):
    proxies = None
    proxy_info = None
    if proxy_api and _proxy_in_scope(scope, area):
        proxy_info = fetch_proxy_info(proxy_api, timeout=timeout)
        proxies = build_proxies(proxy_info)
    kw = dict(kwargs)
    if proxies: kw["proxies"] = proxies
    kw.setdefault("timeout", timeout)
    kw.setdefault("verify", False)
    try:
        resp = requests.request(method, url, **kw)
        return resp, proxy_info, False
    except Exception as e:
        if proxies:
            _log(f"代理请求失败({friendly_err(e)}),回退直连重试")
            kw2 = dict(kwargs)
            kw2.setdefault("timeout", timeout)
            kw2.setdefault("verify", False)
            try:
                resp = requests.request(method, url, **kw2)
                return resp, None, True
            except Exception as e2:
                raise e2
        raise e

def check_ck_validity(cookie, proxy_api=None, proxy_scope="all"):
    try:
        cookie.encode("latin-1")
    except UnicodeEncodeError:
        try:
            pin_match = re.search(r"pt_pin=([^;\s]+)", cookie)
            if pin_match:
                orig_pin = pin_match.group(1)
                cookie = cookie.replace(f"pt_pin={orig_pin}", f"pt_pin={urllib.parse.quote(orig_pin, safe='')}")
        except: pass
    headers = {
        "Cookie": cookie,
        "Referer": "https://h5.m.jd.com/",
        "User-Agent": "jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"
    }
    for _ in range(2):
        try:
            if proxy_api and _proxy_in_scope(proxy_scope, "ck"):
                resp, pinfo, _ = _request_with_proxy("get", "https://plogin.m.jd.com/cgi-bin/ml/islogin",
                                                     proxy_api=proxy_api, scope=proxy_scope, area="ck",
                                                     headers=headers, timeout=10)
            else:
                resp = requests.get("https://plogin.m.jd.com/cgi-bin/ml/islogin", headers=headers, timeout=10, verify=False)
            data = resp.json()
            if str(data.get("islogin")) == "1":
                return True
        except:
            time.sleep(1)
    return False

def _gen_state():
    r1 = random.randint(10**19, 10**20 - 1)
    ts = int(time.time())
    r2 = random.randint(100000, 999999)
    r3 = random.randint(10000, 99999)
    return f"snsapi_base{r1}-{ts}-{r2}-{r3}-0-default-0-1-biz_wxMy"

def _extract_set_cookie_headers(resp):
    result = []
    try:
        if hasattr(resp, "raw") and resp.raw and hasattr(resp.raw, "headers"):
            raw_hdrs = resp.raw.headers
            if hasattr(raw_hdrs, "get_all"):
                vals = raw_hdrs.get_all("Set-Cookie")
                if vals:
                    result.extend(str(v).strip() for v in vals if str(v).strip())
                    if result: return result
    except: pass
    try:
        if hasattr(resp, "cookies"):
            for c in resp.cookies:
                if c.name and c.value:
                    result.append(f"{c.name}={c.value}")
            if result: return result
    except: pass
    return []

def _code_create_qr(config):
    if config.get("code_api_type") != "yyb": return None
    try:
        resp, _, _ = _request_with_proxy("post", f"{config['code_url']}/qr",
                                         proxy_api=config.get("proxy_api"), scope=config.get("proxy_scope", "all"),
                                         area="code", params={"as_base64": "true"}, timeout=TIMEOUT)
        data = resp.json()
        if data.get("code") == 0: return data.get("data")
        return None
    except: return None

def _code_poll_qr(config, session_id):
    try:
        resp, _, _ = _request_with_proxy("get", f"{config['code_url']}/qr/{urllib.parse.quote(str(session_id))}/poll",
                                         proxy_api=config.get("proxy_api"), scope=config.get("proxy_scope", "all"),
                                         area="code", timeout=TIMEOUT)
        data = resp.json()
        if data.get("code") == 0: return data.get("data", {}).get("status", "unknown")
        return "unknown"
    except: return "unknown"

def _code_confirm_qr(config, session_id):
    try:
        resp, _, _ = _request_with_proxy("post", f"{config['code_url']}/qr/{urllib.parse.quote(str(session_id))}/confirm",
                                         proxy_api=config.get("proxy_api"), scope=config.get("proxy_scope", "all"),
                                         area="code", timeout=TIMEOUT)
        data = resp.json()
        if data.get("code") == 0: return data.get("data")
        return None
    except: return None

def _code_get_code(config, ref):
    url = config.get("code_url", "")
    api_type = config.get("code_api_type", "yyb")
    app_id = config.get("code_jd_app_id", JD_APPID_DEFAULT)
    try:
        if api_type == "simple":
            resp, _, _ = _request_with_proxy("get", f"{url}/login",
                                             proxy_api=config.get("proxy_api"), scope=config.get("proxy_scope", "all"),
                                             area="code", params={"appId": app_id}, timeout=TIMEOUT)
            data = resp.json()
            if data.get("err") == 0 and data.get("code"): return data.get("code"), None
            return None, None

        resp, _, _ = _request_with_proxy("post", f"{url}/wxapp/getCode",
                                         proxy_api=config.get("proxy_api"), scope=config.get("proxy_scope", "all"),
                                         area="code", json={"ref": str(ref), "app_id": app_id}, timeout=TIMEOUT)
        data = resp.json()
        if data.get("code") != 0: return None, None
        wx_data = data.get("data", {}) or {}
        openid = wx_data.get("openid") or ""
        result = wx_data.get("result")
        code = result.get("code") if isinstance(result, dict) else (result if isinstance(result, str) and result else wx_data.get("code"))
        if code: return code, openid or None
        return None, None
    except: return None, None

def _jd_code_login(code, app_id, openid=None, proxy_api=None, proxy_scope="all"):
    if not app_id: app_id = JD_APPID_DEFAULT
    _log(f"收到code, 准备Login (AppId: {app_id})")

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 26_5_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.75(0x18004b34) NetType/WIFI Language/zh_CN",
        "Referer": f"https://servicewechat.com/{app_id}/676/page-frame.html",
        "Accept": "*/*",
        "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        "Connection": "keep-alive",
    }

    session = requests.Session()
    session.headers.update(headers)
    session.verify = False

    if openid:
        ts_part = f"{int(time.time() * 1000)}{random.randint(1000000000, 9999999999)}"
        rand_part = f"JA2019_{random.randint(1000000, 9999999)}"
        jdwxapp_value = f"{ts_part}.{rand_part}.{app_id}..{openid}"
        session.cookies.set("__jdwxapp", jdwxapp_value, domain=".jd.com")
        session.cookies.set("wxapp_openid", openid, domain=".jd.com")
        session.cookies.set("wq_unionid", openid, domain=".jd.com")
        session.cookies.set("open_id", openid, domain=".jd.com")
        session.cookies.set("wxapp_type", "1", domain=".jd.com")
        session.cookies.set("wxapp_version", "11.18.300", domain=".jd.com")

    try:
        silent_headers = headers.copy()
        silent_headers["Content-Type"] = "application/x-www-form-urlencoded"
        silent_headers["Accept-Encoding"] = "gzip,compress,br,deflate"
        silent_payload = f"code={urllib.parse.quote(code)}&eid_token=&returnurl=%2Fpages%2Flogin%2Fweb-view%2Fweb-view&wxappid={app_id}&appid=1340&client_ver=1.3.2&ts=1783260263&sign=688acba45785e9770f2569f93018732a"
        silent_resp = session.post(JD_SILENT_AUTH_URL, data=silent_payload, headers=silent_headers, timeout=TIMEOUT)
        silent_data = silent_resp.json()
        if silent_data.get("pt_key") and silent_data.get("pt_pin"):
            pin = urllib.parse.unquote(silent_data["pt_pin"])
            return f"pt_key={silent_data['pt_key']};pt_pin={silent_data['pt_pin']};", pin, None, 0, ""
        err_msg = silent_data.get("message") or silent_data.get("msg") or silent_data.get("errMsg") or silent_data.get("err_msg") or "silentauthlogin 未返回凭证"
        err_code_val = silent_data.get("err_code") or silent_data.get("errCode") or 0
        try: err_code_int = int(err_code_val)
        except: err_code_int = 0
        # ✨ 错误信息优化:128=短信/语音验证(支持等待+重试),118=人脸验证(直接友好提示)
        # 128 时把 jmp_url 作为独立返回值返回,让上层可直接给用户展示验证链接
        if err_code_int == 128:
            jmp = silent_data.get("jmp_url") or silent_data.get("JmpUrl") or ""
            if jmp:
                return None, None, "需要短信/语音验证(请在京东app完成验证后,等待60s发送 ok 再次续期)", 128, jmp
            return None, None, "需要短信/语音验证(请在京东app完成验证后,等待60s发送 ok 再次续期)", 128, ""
        if err_code_int == 118:
            return None, None, "可能需要人脸二次验证，请打开京东app重新登录过人脸验证后再试！", 118, ""
        return None, None, f"silentauthlogin 响应: {silent_data} | 错误: {err_msg}", err_code_int, ""
    except Exception as e:
        _log(f"silentauthlogin 异常: {friendly_err(e)}")

    state = _gen_state()
    url = f"{JD_LOGIN_REDIRECT_URL}?code={urllib.parse.quote(code)}&state={urllib.parse.quote(state)}"
    try:
        resp = session.get(url, allow_redirects=False, timeout=TIMEOUT)
    except Exception as e:
        return None, None, f"LoginRedirect 请求失败: {friendly_err(e)}", 0, ""

    current_resp = resp
    redirect_count = 0
    extracted_pt_key = None
    extracted_pt_pin = None

    while redirect_count < 10:
        raw_sc_list = _extract_set_cookie_headers(current_resp)
        for raw_sc in raw_sc_list:
            pk_match = re.search(r'pt_key=([^;]+)', raw_sc)
            pp_match = re.search(r'pt_pin=([^;]+)', raw_sc)
            wq_match = re.search(r'wq_skey=([^;]+)', raw_sc)
            sf_match = re.search(r'sfstoken=([^;]+)', raw_sc)
            if pk_match: extracted_pt_key = pk_match.group(1)
            if pp_match: extracted_pt_pin = pp_match.group(1)
            if not extracted_pt_key and wq_match: extracted_pt_key = wq_match.group(1)
            if not extracted_pt_key and sf_match: extracted_pt_key = sf_match.group(1)
        if extracted_pt_key and extracted_pt_pin: break
        if current_resp.status_code not in (301, 302, 303, 307, 308): break
        location = current_resp.headers.get("Location", "")
        if not location: break
        if location.startswith("/"):
            parsed_url = urllib.parse.urlparse(current_resp.url)
            location = f"{parsed_url.scheme}://{parsed_url.netloc}{location}"
        try:
            current_resp = session.get(location, allow_redirects=False, timeout=TIMEOUT)
            redirect_count += 1
        except: break

    if extracted_pt_key and extracted_pt_pin:
        pin = urllib.parse.unquote(extracted_pt_pin)
        return f"pt_key={extracted_pt_key};pt_pin={extracted_pt_pin};", pin, None, 0, ""
    return None, None, f"LoginRedirect 流程未提取到 pt_key/pt_pin (重定向{redirect_count}次)", 0, ""

# ✨ 新增 1：纯 Python 版的 login_lt 备用登录接口
def _jd_code_login_lt(code, app_id, proxy_api=None, proxy_scope="all"):
    if not app_id: app_id = JD_APPID_DEFAULT
    _log(f"🔄 启动备用通道: login_lt 接口换取CK (AppId: {app_id})")

    url = "https://wq.jd.com/mlogin/wxapp/login_lt"
    params = {
        "appid": app_id, "code": code, "type": "silent", "isPopup": "false",
        "isIgnoreCookie": "false", "isOfficialPin": "false", "loginColor": "{}",
        "returnUrl": "pages/my/index/index", "deviceName": "iPhone",
        "deviceOS": "iOS", "deviceOSVersion": "17.0", "deviceVersion": "8.0.49",
        "g_tk": "0", "g_ty": "ls"
    }
    headers = {
        "User-Agent": f"Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.49 NetType/WIFI Language/zh_CN miniProgram/{app_id}",
        "Referer": f"https://servicewechat.com/{app_id}/873/page-frame.html",
        "Accept": "application/json,text/plain,*/*",
    }
    
    session = requests.Session()
    session.verify = False
    
    # 提取有效 pt_key/pt_pin 的内置方法
    def _extract_pt(jar):
        pk = pp = ""
        for c in jar:
            if c.name == 'pt_key' and c.value: pk = c.value
            if c.name == 'pt_pin' and c.value: pp = c.value
        if pk and pp:
            return f"pt_key={pk};pt_pin={pp};", urllib.parse.unquote(pp)
        return None, None
        
    try:
        proxies = None
        if proxy_api and _proxy_in_scope(proxy_scope, "login"):
            pinfo = fetch_proxy_info(proxy_api, timeout=10)
            proxies = build_proxies(pinfo)
            
        resp = session.get(url, params=params, headers=headers, proxies=proxies, timeout=15)
        
        # 1. 尝试直接从第一步结果提取 CK
        ck, pin = _extract_pt(session.cookies)
        if ck: return ck, pin, None, 0, ""
        
        # 2. 检查是否有服务端重定向刷新 (ACRJUrl)
        data = resp.json()
        info = data.get("info") or (data.get("data") or {}).get("info") or {}
        acrj_url = info.get("ACRJUrl") or info.get("acrjUrl")
        acrj_state = info.get("ACRJState") or info.get("acrjState")
        
        if acrj_url:
            if acrj_url.startswith("//"): acrj_url = "https:" + acrj_url
            elif acrj_url.startswith("/"): acrj_url = "https://wq.jd.com" + acrj_url
            if acrj_state and "ACRJState=" not in acrj_url:
                sep = "&" if "?" in acrj_url else "?"
                acrj_url += f"{sep}ACRJState={acrj_state}"
                
            headers["Accept"] = "text/html,application/xhtml+xml,application/json,*/*;q=0.8"
            # 追踪跳转链（最多5次）
            for _ in range(5):
                r_resp = session.get(acrj_url, headers=headers, proxies=proxies, allow_redirects=False, timeout=15)
                ck, pin = _extract_pt(session.cookies)
                if ck: return ck, pin, None, 0, ""
                
                if r_resp.status_code in (301, 302, 303, 307, 308):
                    loc = r_resp.headers.get("Location")
                    if not loc: break
                    acrj_url = urllib.parse.urljoin(acrj_url, loc)
                else: break
                    
        return None, None, f"login_lt 未返回有效凭证 (resp: {str(data)[:100]})", 0, ""
    except Exception as e:
        return None, None, f"login_lt 异常: {friendly_err(e)}", 0, ""

# ✨ 新增 2：智能双通道切换中枢
def _do_login_with_fallback(config, ref, app_id, openid):
    # 第一次获取 code 并尝试原生接口
    code, code_openid = _code_get_code(config, ref)
    if not code:
        return None, None, "🔴 获取Code失败(微信授权可能已失效，请重新扫码)", 0, ""
    
    cookie, pin, err_log, err_code_val, jmp_url = _jd_code_login(code, app_id, openid=code_openid or openid, proxy_api=config.get("proxy_api"), proxy_scope=config.get("proxy_scope", "all"))
    
    # 若失败，并且不是需要图形/人脸、短信验证(118/128)，则启动备用方案
    if not cookie and err_code_val not in (118, 128):
        _log(f"静默登录失败({err_log})，拉取新Code切换至 login_lt 备用通道...")
        code2, _ = _code_get_code(config, ref)
        if code2:
            cookie, pin, err_log, err_code_val, jmp_url = _jd_code_login_lt(code2, app_id, proxy_api=config.get("proxy_api"), proxy_scope=config.get("proxy_scope", "all"))
        else:
            err_log += " | 备用通道拉取新Code失败"
            
    return cookie, pin, err_log, err_code_val, jmp_url

def _code_login_with_ref(sender, userid, config, ref, openid, nickname=""):
    sender.reply(f"⏳ 正在为【{nickname or '已绑定微信'}】换取登录凭证(智能双通道)...")
    # 替换为双通道 fallback 方法
    cookie, pin, err_log, _err_code, _jmp = _do_login_with_fallback(config, ref, config.get("code_jd_app_id", JD_APPID_DEFAULT), openid)
    
    if not cookie:
        sender.reply("❌ 京东Code登录失败")
        if err_log: sender.reply(f"📋 底层日志: {err_log}")
        sender.reply("💡 温馨提示: 京东小程序需绑定手机号")
        return False

    sender.reply("⏳ 正在写入青龙...")
    success, panels = commit_cookie_to_ql(sender, userid, cookie, config.get("code_ql_var_name", "JD_COOKIE"))
    if success:
        pin_dec = decode_pin(pin)
        try: middleware.bucketSet("jd_code_wechat_pin_map", ref, pin_dec)
        except: pass
        
        sender.reply(f"✅ 微信Code登录成功\n👤 账号: {pin_dec}\n📦 已写入: {', '.join(panels)}")
        bind_user_pin_with_sender(sender, userid, pin_dec)
        notify_admin(config, f"用户{userid}通过微信Code登录: {pin_dec}")
        run_inline_command(config)
        if config.get("code_auto_refresh_on_login"):
            run_code_auto_refresh(sender, userid, config)
        return True
    sender.reply("❌ 写入青龙失败, 请检查 Joh_CK 容器配置")
    return False


# ===================== ✨ 微信Code登录续期实现 (增强验证与UI版) =====================

def _get_user_bound_code_accounts(userid, config):
    if config.get("code_api_type") == "simple": return []
    url = config.get("code_url", "").rstrip("/")
    if not url: return []
    try:
        resp = requests.get(f"{url}/accounts", timeout=10, verify=False)
        data = resp.json()
        if isinstance(data, dict) and data.get("code") == 0 and isinstance(data.get("data"), list):
            return list(data["data"])
    except Exception as e:
        _log(f"拉取YYB账号列表失败: {friendly_err(e)}")
    return []

def _get_local_user_refs(userid):
    raw = middleware.bucketGet("jd_code_user_refs", str(userid))
    try: return set(json.loads(str(raw)) if raw else [])
    except: return set()

def bind_local_user_ref(userid, ref):
    if not userid or not ref: return
    ref = str(ref)
    raw = middleware.bucketGet("jd_code_user_refs", str(userid))
    try:
        arr = json.loads(str(raw)) if raw else []
        if not isinstance(arr, list): arr = []
    except: arr = []
    if ref not in arr:
        arr.append(ref)
        middleware.bucketSet("jd_code_user_refs", str(userid), json.dumps(arr, ensure_ascii=False))

def _unbind_local_user_ref(userid, ref):
    if not userid or not ref: return
    ref = str(ref)
    raw = middleware.bucketGet("jd_code_user_refs", str(userid))
    try:
        arr = json.loads(str(raw)) if raw else []
        if not isinstance(arr, list): arr = []
    except: arr = []
    if ref in arr:
        arr.remove(ref)
        middleware.bucketSet("jd_code_user_refs", str(userid), json.dumps(arr, ensure_ascii=False))

def _filter_accounts_for_user(accounts, userid, is_admin):
    if is_admin: return accounts
    user_refs = _get_local_user_refs(userid)
    return [a for a in accounts if str(a.get("id") or a.get("openid") or "") in user_refs]

def _refresh_one_code_account(config, sender, userid, acc, is_admin=False):
    ref = str(acc.get("id") or acc.get("openid") or "")
    nick = acc.get("nickname") or "未知"
    
    yyb_pin = str(acc.get("pt_pin") or acc.get("pin") or "")
    local_mapped_pin = str(middleware.bucketGet("jd_code_wechat_pin_map", ref) or "")
    
    sender.reply(f"🔍 正在检测账号【{nick}】状态...")
    if config.get("code_check_before_refresh"):
        try:
            panels = load_ql_panels()
            is_valid = False
            valid_pin_dec = ""  # 用于存放验证有效的京东账号，以便重新恢复绑定
            for panel in panels:
                if is_valid: break
                ql = QingLongClient(panel)
                envs = ql.all_envs()
                for env in envs:
                    if env.get("name") == config.get("code_ql_var_name", "JD_COOKIE"):
                        val = str(env.get("value", ""))
                        remark = str(env.get("remarks", ""))
                        pin_m = re.search(r"pt_pin=([^;\s]+)", val)
                        if pin_m:
                            pin_raw = pin_m.group(1)
                            pin_dec = decode_pin(pin_raw)
                            
                            is_match = False
                            if local_mapped_pin and local_mapped_pin in (pin_raw, pin_dec):
                                is_match = True
                            elif yyb_pin and yyb_pin in (pin_raw, pin_dec):
                                is_match = True
                            elif nick in (pin_dec, pin_raw) or (nick in remark and nick.strip()):
                                is_match = True
                                
                            if is_match:
                                if check_ck_validity(val,
                                                     proxy_api=config.get("proxy_api"),
                                                     proxy_scope=config.get("proxy_scope", "all")):
                                    is_valid = True
                                    valid_pin_dec = pin_dec  # 记录这把验证成功的账号名
                                    break
            
            # ✨ V3.2.7 核心修复：管理员续期时绝不动账号绑定关系
            # 之前逻辑(用户在 V3.2.6 加入)会"即使跳过续期也恢复本地绑定"，但管理员给别用户续期时
            # 这会把别人的京东账号错误地绑到管理员名下 (pinWX[pin_others] = userid_admin)
            # 正确语义：只有普通用户续期自己账号时，才维护本地绑定；管理员续期他人账号时只做 CK 检测
            if is_valid:
                if not is_admin and valid_pin_dec:
                    bind_user_pin_with_sender(sender, userid, valid_pin_dec)
                    return True, f"{nick} -> 🟢 京东CK未过期，跳过续期 (已恢复本地绑定)", False
                else:
                    return True, f"{nick} -> 🟢 京东CK未过期，跳过续期", False
        except Exception as e:
            _log(f"尝试检查前置有效性时发生异常: {e}")

    app_id = config.get("code_jd_app_id", JD_APPID_DEFAULT)
    # 替换为双通道 fallback 方法
    cookie, pin, err_log, err_code_val, jmp_url = _do_login_with_fallback(config, ref, app_id, acc.get("openid"))

    # ✨ err_code 128: 短信/语音验证 (保留重试功能，依旧调用双通道)
    if not cookie and err_code_val == 128:
        sender.reply(f"⏸️ 账号【{nick}】触发短信验证,请在京东APP内搜索[验证码]进行验证，等待60s期间可输入 ok 重试")
        if jmp_url:
            sender.reply(f"🔗 或复制链接打开验证:\n{jmp_url}")
        ok_inp = sender.input(70000, 1, False) 
        if ok_inp and str(ok_inp).strip().lower() == "ok":
            sender.reply("🔄 收到 ok,正在自动双通道重试续期...")
            cookie, pin, err_log, err_code_val, jmp_url = _do_login_with_fallback(config, ref, app_id, acc.get("openid"))
        else:
            sender.reply(f"⏹️ 账号【{nick}】未在等待时间内确认 ok,已取消重试")
            
    if not cookie:
        return False, f"{nick} -> 🔴 京东CK提取失败 ({err_log or '无底层日志'})", False
        
    try: middleware.bucketSet("jd_code_wechat_pin_map", ref, decode_pin(pin))
    except: pass
    
    success, panels = commit_cookie_to_ql(sender, userid, cookie, config.get("code_ql_var_name", "JD_COOKIE"), skip_bind=True, append_remark=nick)
    if success:
        return True, f"{nick} -> 🟢 续期成功 ({', '.join(panels)})", False
    return False, f"{nick} -> 🔴 写入青龙失败", False

def run_code_auto_refresh(sender, userid, config):
    if config.get("code_api_type") != "yyb":
        sender.reply("❌ Code续期仅支持yyb模式")
        return
    interval = config.get("code_auto_refresh_interval", 21600)
    sender.reply(f"🔄 [Code自动续期托管] 已启动\n ⏱ 续期间隔: {interval} 秒\n 💡 发送 q 终止托管")
    round_num = 0
    while True:
        round_num += 1
        sender.reply(f"🔄 [Code自动续期] 第 {round_num} 轮巡检启动...")
        accounts = _get_user_bound_code_accounts(userid, config)
        try: is_admin = check_admin(sender, config)
        except: is_admin = False
        accounts = _filter_accounts_for_user(accounts, userid, is_admin)
        if not accounts:
            sender.reply("⚠️ 暂无可续期账号,托管继续监控新绑定...")
        else:
            succ = fail = 0
            for acc in accounts:
                # ✨ V3.2.7 修复：透传 is_admin，避免管理员自动续期时抢占账号归属
                ok, msg, _ = _refresh_one_code_account(config, sender, userid, acc, is_admin=is_admin)
                if ok: succ += 1
                else: fail += 1
            sender.reply(f"✅ 第 {round_num} 轮续期完成: 成功 {succ}, 失败 {fail}")
        sender.reply(f"⏳ 下一轮将在 {interval} 秒后进行,发送 q 终止")
        waited = 0
        while waited < interval:
            chunk = min(300, interval - waited)
            try:
                inp = sender.input(chunk * 1000, 1, False)
                if inp:
                    txt = str(inp if not isinstance(inp, dict) else inp.get("text", "")).strip()
                    if txt in QUIT_KEYWORDS:
                        sender.reply(f"✅ Code自动续期托管已安全终止 (共完成 {round_num} 轮)")
                        return
            except: pass
            waited += chunk

def run_code_refresh_menu(sender, userid, config):
    if config.get("code_api_type") != "yyb":
        sender.reply("❌ Code续期仅支持yyb模式")
        return
    accounts = _get_user_bound_code_accounts(userid, config)
    try: is_admin = check_admin(sender, config)
    except: is_admin = False
    accounts = _filter_accounts_for_user(accounts, userid, is_admin)
    
    if not accounts:
        sender.reply("❌ 暂未绑定任何微信账号\n💡 请先完成【微信扫码登录】后再来续期")
        return

    lines = ["╭━━━ 🔄 京东账号续期 (管理员) ━━━╮"]
    for i, acc in enumerate(accounts, 1):
        status = acc.get("status", "unknown")
        nick = acc.get("nickname") or "未知"
        if status == "alive":
            lines.append(f"【{i}】🟢 {nick} (微信有效)")
        elif status == "expired":
            lines.append(f"【{i}】🔴 {nick} (微信失效/需扫码)")
        else:
            lines.append(f"【{i}】🟡 {nick} (状态异常/未知)")
            
    lines.append("━━━━━━━━━━━━━━━━━━━━━━━━")
    lines.append("💡 提示: 续期前会自动检测京东CK有效性")
    lines.append("【A】一键检测并续期全部账号")
    lines.append("╰━━━━━━━━━━━━━━━━━━━━━━╯\n(回复对应字符执行，q 退出)")
    
    sender.reply("\n".join(lines))
    inp = get_input(sender, validator=lambda t: t.lower() in ("q", "a") or t.isdigit())
    if not inp or inp.lower() == "q":
        return
    if inp.lower() == "a":
        sender.reply(f"⏳ 正在批量检测并续期 {len(accounts)} 个账号...")
        succ = skip = fail = 0
        for acc in accounts:
            # ✨ V3.2.7 修复：透传 is_admin，避免管理员续期时把账号绑到管理员名下
            ok, msg, _ = _refresh_one_code_account(config, sender, userid, acc, is_admin=is_admin)
            sender.reply(msg)
            if ok: 
                if "跳过续期" in msg: skip += 1
                else: succ += 1
            else: fail += 1
        sender.reply(f"📊 批量操作完成: 成功续期 {succ}, 有效跳过 {skip}, 失败 {fail}")
        return
    
    idx = int(inp)
    if idx < 1 or idx > len(accounts):
        sender.reply("❌ 选择无效")
        return
    # ✨ V3.2.7 修复：透传 is_admin
    ok, msg, _expired = _refresh_one_code_account(config, sender, userid, accounts[idx-1], is_admin=is_admin)
    sender.reply(msg)


def run_code_qr_login(sender, userid):
    config = get_config()
    if not is_code_configured(config):
        sender.reply("❌ 微信Code登录未启用或未配置服务地址")
        return

    if config.get("code_api_type") == "yyb":
        local_refs = _get_local_user_refs(userid)
        if local_refs:
            all_accounts = _get_user_bound_code_accounts(userid, config)
            user_accounts = [a for a in all_accounts if str(a.get("id") or a.get("openid") or "") in local_refs]
            
            if user_accounts:
                while True:
                    lines = ["╭━━━ 📱 当前已绑定微信 ━━━╮"]
                    for i, acc in enumerate(user_accounts, 1):
                        nick = acc.get("nickname") or "未知"
                        status = acc.get("status")
                        if status == "alive":
                            status_icon = "🟢 微信有效"
                        elif status == "expired":
                            status_icon = "🔴 微信失效(需重新扫码)"
                        else:
                            status_icon = "🟡 状态异常"
                        lines.append(f"【{i}】👤 {nick} (状态: {status_icon})")
                        
                    lines.append("╰━━━━━━━━━━━━━━━━━━━━━━╯")
                    lines.append("回复对应【数字】进行 续期/解绑 操作")
                    lines.append("回复【A】🔁 一键续期所有账号")
                    lines.append("回复【0】➕ 新增微信扫码账号")
                    lines.append("(发送 q 退出)")
                    
                    sender.reply("\n".join(lines))
                    inp = get_input(sender, validator=lambda t: t.isdigit() or t.lower() in ("a", "q"))
                    
                    if not inp or inp.lower() == "q": return
                    
                    # ✨ 一键续期所有账号(普通用户版)
                    if inp.lower() == "a":
                        sender.reply(f"⏳ 正在一键续期 {len(user_accounts)} 个账号,请稍候...")
                        succ = skip = fail = 0
                        for acc in user_accounts:
                            # 普通用户一键续期自己账号,is_admin 显式传 False
                            ok, msg, expired = _refresh_one_code_account(config, sender, userid, acc, is_admin=False)
                            sender.reply(msg)
                            if ok:
                                if "跳过续期" in msg: skip += 1
                                else: succ += 1
                            else:
                                fail += 1
                                # 单个账号失败后,继续处理下一个,不卡住
                        sender.reply(f"📊 一键续期完成: 成功续期 {succ}, 有效跳过 {skip}, 失败 {fail}")
                        return
                    
                    choice = int(inp)
                    if choice == 0: break 
                    elif 1 <= choice <= len(user_accounts):
                        target_acc = user_accounts[choice - 1]
                        nick = target_acc.get("nickname") or "未知"
                        
                        sender.reply(f"当前选中: 👤 {nick}\n【1】🔄 手动续期\n【2】🗑️ 解除绑定\n【0】返回上级")
                        sub_inp = get_input(sender, validator=lambda t: t in ("0", "1", "2", "q"))
                        if not sub_inp or sub_inp.lower() == "q": return
                        if sub_inp == "0": continue
                        elif sub_inp == "2":
                            _unbind_local_user_ref(userid, str(target_acc.get("id") or target_acc.get("openid") or ""))
                            sender.reply(f"✅ 已解除微信【{nick}】的绑定")
                            user_accounts.pop(choice - 1)
                            if not user_accounts: break
                            continue
                        elif sub_inp == "1":
                            # ✨ V3.2.7 修复：普通用户续期自己账号，is_admin 显式传 False
                            ok, msg, expired = _refresh_one_code_account(config, sender, userid, target_acc, is_admin=False)
                            if ok:
                                sender.reply(msg)
                                return
                            
                            sender.reply(msg)
                            if expired:
                                sender.reply("⚠️ 检测到该微信绑定已失效，已自动清理本地绑定。\n即将引导您重新扫码...")
                                _unbind_local_user_ref(userid, str(target_acc.get("id") or target_acc.get("openid") or ""))
                                break
                            else:
                                return
                    else:
                        sender.reply("❌ 选择无效，请重新输入")

    sender.reply("⏳ 正在创建微信扫码会话...")
    qr_data = _code_create_qr(config)
    if not qr_data:
        sender.reply(f"❌ 创建二维码失败: Code服务返回异常, 请检查 {config['code_url']}/qr 接口")
        return

    session_id = qr_data.get("session_id")
    image_base64 = qr_data.get("image_base64")
    image_url = f"{config['code_url'].rstrip('/')}/qr/{urllib.parse.quote(str(session_id))}/image"

    image_sent = False
    try:
        sender.reply(f"[CQ:image,file={image_url}]")
        image_sent = True
    except: pass
    if not image_sent and image_base64:
        try:
            b64_str = str(image_base64)
            if "," in b64_str: b64_str = b64_str.split(",", 1)[1]
            image_bytes = base64.b64decode(b64_str)
            temp_path = os.path.join("/tmp" if os.path.exists("/tmp") else os.getcwd(), f"jd_code_qr_{session_id}.jpg")
            with open(temp_path, "wb") as f:
                f.write(image_bytes)
            try:
                sender.reply(f"[CQ:image,file=file:///{temp_path}]")
                image_sent = True
            except: pass
        except: pass
    if not image_sent:
        sender.reply(f"📱 二维码URL: {image_url}")
    sender.reply("✅ 二维码已发送, 请使用微信扫码\n(发送 q 退出)")

    start_time = time.time()
    last_status = ""
    account = None
    while time.time() - start_time < config.get("code_qr_timeout", 180):
        try:
            inp = sender.input(int(config.get("code_qr_poll_interval", 3) * 1000), 1, False)
            if inp:
                txt = str(inp if not isinstance(inp, dict) else inp.get("text", "")).strip()
                if txt in QUIT_KEYWORDS:
                    sender.reply("✅ 已安全退出")
                    return
        except: pass

        status = _code_poll_qr(config, session_id)
        if status != last_status:
            if status == "scanned": sender.reply("✅ 已扫码, 请在手机端点击确认授权")
            elif status in ("authorized", "confirmed"):
                account = _code_confirm_qr(config, session_id)
                break
            elif status == "expired":
                sender.reply("❌ 二维码已过期, 请重试")
                return
            last_status = status
    else:
        sender.reply("⏰ 扫码超时")
        return

    if not account:
        sender.reply("❌ 微信授权校验失败, 未获取到账号信息")
        return

    ref = str(account.get("id") or account.get("openid") or "")
    openid = account.get("openid") or ""
    nickname = account.get("nickname") or "未知"
    sender.reply(f"✅ 微信绑定成功: {nickname}")

    if ref: bind_local_user_ref(userid, ref)

    _code_login_with_ref(sender, userid, config, ref, openid, nickname)

# ===================== 其余登录方法实现 (Pro/RabbitPro) =====================

def run_pro_qr_login(sender, userid):
    config = get_config()
    if not is_pro_configured(config):
        sender.reply("❌ Pro服务未启用或未配置")
        return
    sender.reply("⏳ 正在获取二维码...")
    try:
        resp = requests.post(
            f"{config['pro_url']}/qr/GetQRKey",
            json={"botApitoken": config["pro_token"]},
            timeout=30, verify=False,
        )
        body = resp.json()
        qrkey = (body.get("data") or {}).get("key")
        if not qrkey:
            sender.reply(f"❌ 扫码服务器异常: {body.get('message') or body.get('msg') or body}")
            return
        qr_url = qr_code_url(qrkey, config["qr_base_url"])
        try: sender.reply({"type": "image", "path": qr_url})
        except: sender.reply(f"📱 二维码URL:{qr_url}")
        sender.reply("请使用京东APP扫码,完成后发送 1 确认(退出发送 q)")
        inp = get_input(sender, validator=lambda t: t in ("1", "q"))
        if not inp or inp == "q": return
        check_body = {"qrkey": qrkey}
        if config["qr_cookie_type"] == 2:
            check_body["botApitoken"] = config["pro_token"]
        resp = requests.post(
            f"{config['pro_url']}/qr/CheckQRKey",
            json=check_body,
            timeout=30, verify=False,
        )
        data = resp.json()
        if not data.get("success"):
            sender.reply(f"❌ 扫码登录失败: {data.get('message') or '未知错误'}")
            return
        if config["qr_cookie_type"] == 1:
            username = (data.get("data") or {}).get("username")
            if username:
                bind_user_pin_with_sender(sender, userid, username)
                sender.reply(f"✅ {username} 扫码登录成功")
                notify_admin(config, f"用户{userid}通过扫码登录: {username}")
            else: sender.reply("⚠️ 服务管理返回未带username")
            return
        rwskey = (data.get("data") or {}).get("rwskey")
        if not rwskey:
            sender.reply("❌ 未返回WSKEY")
            return
        success, panels = commit_wskey_to_ql(sender, userid, rwskey, config["wsck_var_name"])
        if success:
            pin_dec = decode_pin(get_pin_from_wskey(rwskey))
            sender.reply(f"✅ 扫码登录成功\n👤 账号: {pin_dec}\n📦 已写入: {', '.join(panels)}")
            notify_admin(config, f"用户{userid}通过扫码登录: {pin_dec}")
            run_inline_command(config)
    except Exception as e:
        sender.reply(f"❌ 扫码异常: {friendly_err(e)}")

def run_pro_short_login(sender, userid):
    config = get_config()
    if not is_pro_configured(config):
        sender.reply("❌ Pro服务未启用或未配置")
        return
    sender.reply("⏳ 正在生成口令...")
    try:
        resp = requests.post(
            f"{config['pro_url']}/qr/GetQRKey",
            json={"botApitoken": config["pro_token"]},
            timeout=30, verify=False,
        )
        body = resp.json()
        qrkey = (body.get("data") or {}).get("key")
        if not qrkey:
            sender.reply(f"❌ 口令服务器异常: {body.get('message') or body}")
            return
        cmd_url = jd_scan_command_url(qrkey)
        try: sender.reply({"msg": cmd_url, "dontEdit": True})
        except: sender.reply(f"📋 请复制以下链接到京东打开:\n{cmd_url}")
        sender.reply("复制口令打开京东确认登录,完成后发送 1 确认(退出发送 q)")
        inp = get_input(sender, validator=lambda t: t in ("1", "q"))
        if not inp or inp == "q": return
        check_body = {"qrkey": qrkey}
        if config["qr_cookie_type"] == 2:
            check_body["botApitoken"] = config["pro_token"]
        resp = requests.post(
            f"{config['pro_url']}/qr/CheckQRKey",
            json=check_body,
            timeout=30, verify=False,
        )
        data = resp.json()
        if not data.get("success"):
            sender.reply(f"❌ 口令登录失败: {data.get('message') or '未知错误'}")
            return
        if config["qr_cookie_type"] == 1:
            username = (data.get("data") or {}).get("username")
            if username:
                bind_user_pin_with_sender(sender, userid, username)
                sender.reply(f"✅ {username} 口令登录成功")
                notify_admin(config, f"用户{userid}通过口令登录: {username}")
            return
        rwskey = (data.get("data") or {}).get("rwskey")
        if not rwskey:
            sender.reply("❌ 未返回WSKEY")
            return
        success, panels = commit_wskey_to_ql(sender, userid, rwskey, config["wsck_var_name"])
        if success:
            pin_dec = decode_pin(get_pin_from_wskey(rwskey))
            sender.reply(f"✅ 口令登录成功\n👤 账号: {pin_dec}\n📦 已写入: {', '.join(panels)}")
            notify_admin(config, f"用户{userid}通过口令登录: {pin_dec}")
            run_inline_command(config)
    except Exception as e:
        sender.reply(f"❌ 口令异常: {friendly_err(e)}")

def run_pro_sms_login(sender, userid, phone=None):
    config = get_config()
    if not is_pro_configured(config):
        sender.reply("❌ Pro服务未启用或未配置")
        return
    if not phone:
        sender.reply(config["phone_input_tip"])
        phone = get_input(
            sender,
            validator=lambda t: bool(re.fullmatch(r"\d{11}", t)),
            error_tip="❌ 手机号格式错误,请输入11位手机号:",
            retry_limit=2,
        )
        if not phone: return
    try:
        resp = requests.post(
            f"{config['pro_url']}/sms/SendSMS",
            json={"phone": phone, "botApitoken": config["pro_token"]},
            timeout=60, verify=False,
        )
        body = resp.json()
        if not body.get("success"):
            sender.reply(f"❌ 发送短信失败: {body.get('message') or body}")
            return
    except Exception as e:
        sender.reply(f"❌ 发送短信异常: {friendly_err(e)}")
        return
    sender.reply(f"📱 {mask_phone(phone)} {config['code_tip']}")
    code = get_input(
        sender,
        validator=lambda t: bool(re.fullmatch(r"\d{6}", t)),
        error_tip="❌ 验证码格式错误,请输入6位数字:",
        retry_limit=3,
    )
    if not code: return
    try:
        resp = requests.post(
            f"{config['pro_url']}/sms/VerifyCode",
            json={"phone": phone, "botApitoken": config["pro_token"], "code": code},
            timeout=60, verify=False,
        )
        data = resp.json()
        if data.get("success"):
            ck = (data.get("data") or {}).get("ck", "")
            handle_pro_sms_result(sender, userid, config, data, phone, ck)
            return
        sub = data.get("data") or {}
        status = sub.get("status")
        mode = sub.get("mode") or data.get("mode")
        if status == 555 and mode == "USER_ID":
            sender.reply("需要身份验证,请输入身份证前2后4:")
            id_code = get_input(sender, validator=lambda t: len(t) == 6, retry_limit=2)
            if not id_code: return
            resp = requests.post(
                f"{config['pro_url']}/sms/VerifyCardCode",
                json={"phone": phone, "botApitoken": config["pro_token"], "code": id_code},
                timeout=60, verify=False,
            )
            res = resp.json()
            if res.get("success"):
                ck = (res.get("data") or {}).get("ck", "")
                handle_pro_sms_result(sender, userid, config, res, phone, ck)
                return
            sender.reply(f"❌ 身份验证失败: {res.get('message') or '未知'}")
            return
        if status == 555 and mode == "HISTORY_DEVICE":
            sender.reply("⚠️ 检测到新设备登录\n请在京东APP确认新设备登录,完成后回复 已确认")
            confirm = get_input(sender, validator=lambda t: t == "已确认", retry_limit=2)
            if not confirm: return
            resp = requests.post(
                f"{config['pro_url']}/sms/VerifyCardCode",
                json={"phone": phone, "botApitoken": config["pro_token"], "code": ""},
                timeout=60, verify=False,
            )
            res = resp.json()
            if res.get("success"):
                ck = (res.get("data") or {}).get("ck", "")
                handle_pro_sms_result(sender, userid, config, res, phone, ck)
                return
            sender.reply(f"❌ 新设备验证失败: {res.get('message') or '未知'}")
            return
        sender.reply(f"❌ 短信登录失败: {data.get('message') or '未知'}")
    except Exception as e:
        sender.reply(f"❌ 短信异常: {friendly_err(e)}")

def handle_pro_sms_result(sender, userid, config, data, phone, ck):
    if not ck or "pt_key=" not in ck:
        sender.reply(f"❌ 未返回有效Cookie: {data.get('message') or '未知'}")
        return
    success, panels = commit_cookie_to_ql(sender, userid, ck, config["ql_var_name"])
    if success:
        pin = get_pin_from_cookie(ck)
        pin_dec = decode_pin(pin)
        sender.reply(f"✅ 短信登录成功\n📱 手机: {mask_phone(phone)}\n👤 账号: {pin_dec}\n📦 已写入: {', '.join(panels)}")
        if config["save_history"]: add_history_account(userid, phone, "", method="sms")
        notify_admin(config, f"用户{userid}通过短信登录: {pin_dec}")
        run_inline_command(config)

def run_rabbit_qr_login(sender, userid, short=False):
    config = get_config()
    if not is_rabbit_configured(config):
        sender.reply("❌ RabbitPro服务未启用或未配置")
        return
    sender.reply("⏳ 正在获取二维码...")
    try:
        if config["qr_cookie_type"] == 1:
            gen_url = f"{config['rabbit_url']}/api/GenQrCode"
            check_url = f"{config['rabbit_url']}/api/QrCheck"
        else:
            gen_url = f"{config['rabbit_url']}/bot/GenQrCode?BotApiToken={urllib.parse.quote(config['rabbit_token'])}"
            check_url = f"{config['rabbit_url']}/bot/QrCheck?BotApiToken={urllib.parse.quote(config['rabbit_token'])}"
        resp = requests.post(gen_url, timeout=30, verify=False)
        body = resp.json()
        if resp.status_code != 200 or body.get("code") not in (0, 200) or not body.get("QRCodeKey"):
            sender.reply(f"❌ 扫码服务器异常: {body.get('msg') or body}")
            return
        qrkey = body["QRCodeKey"]
        if short:
            cmd_url = body.get("jcommond") or jd_scan_command_url(qrkey)
            try: sender.reply({"msg": cmd_url, "dontEdit": True})
            except: sender.reply(f"📋 请复制以下链接到京东打开:\n{cmd_url}")
            prompt = "复制口令打开京东确认登录,完成后发送 1 确认(退出发送 q)"
        else:
            qr_url = qr_code_url(qrkey, config["qr_base_url"])
            try: sender.reply({"type": "image", "path": qr_url})
            except: sender.reply(f"📱 二维码URL:{qr_url}")
            prompt = "请使用京东APP扫码,完成后发送 1 确认(退出发送 q)"
        sender.reply(prompt)
        inp = get_input(sender, validator=lambda t: t in ("1", "q"))
        if not inp or inp == "q": return
        body_data = {"QRCodeKey": qrkey}
        if config["qr_cookie_type"] == 1:
            body_data = {"QRCodeKey": qrkey, "container_id": config["rabbit_container_id"], "token": ""}
        resp = requests.post(check_url, json=body_data, timeout=30, verify=False)
        data = resp.json()
        if resp.status_code != 200 or data.get("code") not in (0, 200):
            sender.reply(f"❌ 扫码登录失败: {data.get('msg') or '未知错误'}")
            return
        if config["qr_cookie_type"] == 1:
            pin = data.get("pin")
            if pin:
                bind_user_pin_with_sender(sender, userid, pin)
                sender.reply(f"✅ 扫码登录成功(服务管理)\n👤 账号: {pin}")
                notify_admin(config, f"用户{userid}通过扫码登录: {pin}")
            return
        wskey_pin = data.get("pin")
        wskey_val = data.get("wskey")
        if not wskey_pin or not wskey_val:
            sender.reply("❌ 未返回完整的WSKEY/pin")
            return
        wskey_str = f"pin={wskey_pin};wskey={wskey_val};"
        success, panels = commit_wskey_to_ql(sender, userid, wskey_str, config["wsck_var_name"])
        if success:
            pin_dec = decode_pin(wskey_pin)
            sender.reply(f"✅ 扫码登录成功\n👤 账号: {pin_dec}\n📦 已写入: {', '.join(panels)}")
            notify_admin(config, f"用户{userid}通过扫码登录: {pin_dec}")
            run_inline_command(config)
    except Exception as e:
        sender.reply(f"❌ 扫码异常: {friendly_err(e)}")

def run_rabbit_sms_login(sender, userid, phone=None):
    config = get_config()
    if not is_rabbit_configured(config):
        sender.reply("❌ RabbitPro服务未启用或未配置")
        return
    if not phone:
        sender.reply(config["phone_input_tip"])
        phone = get_input(
            sender,
            validator=lambda t: bool(re.fullmatch(r"\d{11}", t)),
            error_tip="❌ 手机号格式错误,请输入11位手机号:",
            retry_limit=2,
        )
        if not phone: return

    def rabbit_api(path, body, timeout=90):
        try:
            resp = requests.post(
                f"{config['rabbit_url']}{path}?BotApiToken={urllib.parse.quote(config['rabbit_token'])}",
                json=body, timeout=timeout, verify=False,
            )
            return resp.json() if resp.status_code == 200 else {}
        except Exception as e:
            return {"message": friendly_err(e)}

    send_data = rabbit_api("/bot/mck/sendSMS", {"Phone": phone})
    if not send_data.get("success"):
        if send_data.get("code") == 666 or (send_data.get("data") or {}).get("status") == 666:
            sender.reply("⚠️ 需要图形验证,自动处理中...")
            auto_data = rabbit_api("/bot/mck/AutoCaptcha", {"Phone": phone})
            if not auto_data.get("success"):
                sender.reply(f"❌ 图形验证失败: {auto_data.get('message') or auto_data.get('msg') or '未知'}")
                return
        elif send_data.get("code") == 503:
            sender.reply(f"❌ RabbitPro授权异常: {send_data.get('message') or send_data.get('msg')}")
            return
        else:
            sender.reply(f"❌ 发送短信失败: {send_data.get('message') or send_data.get('msg') or '未知'}")
            return
    max_sms_retry = 5
    sms_attempt = 0
    while sms_attempt < max_sms_retry:
        sms_attempt += 1
        sender.reply(f"📱 {mask_phone(phone)} {config['code_tip']}")
        code = get_input(
            sender,
            validator=lambda t: bool(re.fullmatch(r"\d{6}", t)),
            error_tip="❌ 验证码格式错误,请重新输入:",
            retry_limit=3,
        )
        if not code: return
        verify_data = rabbit_api("/bot/mck/VerifyCode", {"Phone": phone, "Code": code})
        if verify_data.get("success") and verify_data.get("code") == 200:
            ck = verify_data.get("ck") or (verify_data.get("data") or {}).get("ck", "")
            if ck:
                handle_rabbit_sms_result(sender, userid, config, ck, phone)
                return
        msg = verify_data.get("message") or verify_data.get("msg") or "验证码错误"
        if verify_data.get("code") in (503, 505):
            sender.reply(msg)
            continue
        sender.reply(f"❌ {msg}")
        return
    sender.reply("❌ 验证码验证次数过多,已退出")

def handle_rabbit_sms_result(sender, userid, config, ck, phone):
    if not ck or "pt_key=" not in ck:
        sender.reply("❌ 未返回有效Cookie")
        return
    success, panels = commit_cookie_to_ql(sender, userid, ck, config["ql_var_name"])
    if success:
        pin = get_pin_from_cookie(ck)
        pin_dec = decode_pin(pin)
        sender.reply(f"✅ 短信登录成功\n📱 手机: {mask_phone(phone)}\n👤 账号: {pin_dec}\n📦 已写入: {', '.join(panels)}")
        if config["save_history"]: add_history_account(userid, phone, "", method="sms")
        notify_admin(config, f"用户{userid}通过短信登录: {pin_dec}")
        run_inline_command(config)

def run_password_login(sender, userid, phone=None, pwd=None):
    config = get_config()
    # 历史账号一键登录(已带phone)不受总开关限制;仅菜单直接选账密登录时检查开关
    if not phone and not config["enable_password"]:
        sender.reply("❌ 账号密码登录未启用")
        return

    actual_api = config["password_api"]
    if actual_api == 0 and not is_rabbit_configured(config):
        if is_pro_configured(config):
            sender.reply("⚠️ 配置的rabbitPro不可用,自动切换到Pro账密登录")
            actual_api = 1
        else:
            sender.reply("❌ 账密登录需要至少配置 Pro 或 rabbitPro 其中之一")
            return
    elif actual_api == 1 and not is_pro_configured(config):
        if is_rabbit_configured(config):
            sender.reply("⚠️ 配置的Pro不可用,自动切换到rabbitPro账密登录")
            actual_api = 0
        else:
            sender.reply("❌ 账密登录需要至少配置 Pro 或 rabbitPro 其中之一")
            return

    if not phone:
        sender.reply("请输入11位手机号或账号:")
        phone = get_input(
            sender,
            validator=lambda t: bool(re.fullmatch(r"[a-zA-Z0-9_-]{4,16}|\d{11}", t)),
            error_tip="❌ 账号格式错误,请输入11位手机号或账号:",
            retry_limit=2,
        )
        if not phone: return

    if not pwd:
        saved_pwd = get_saved_password(phone) if config["save_history"] else ""
        if saved_pwd:
            sender.reply(
                f"🔐 检测到已保存的密码\n📱 {mask_phone(phone)}\n"
                f"是否使用已保存的密码登录?\n【1】使用已保存密码\n【2】输入新密码\n(q 退出)"
            )
            choice = get_input(sender, validator=lambda t: t in ("1", "2", "q"))
            if not choice: return
            if choice == "2":
                sender.reply(config["password_tip"])
                pwd = get_input(
                    sender,
                    validator=lambda t: bool(re.fullmatch(r"\S{8,20}", t)),
                    error_tip="❌ 密码格式错误,请输入8到20位:",
                    retry_limit=config["password_retry_limit"],
                )
                if not pwd: return
                sender.reply("是否保存此次输入的密码以便下次自动登录?\n【1】保存\n【2】不保存")
                save_choice = get_input(sender, validator=lambda t: t in ("1", "2"))
                if save_choice == "1":
                    add_history_account(userid, phone, pwd, method="password")
                    sender.reply("✅ 密码已保存")
                else: add_history_account(userid, phone, "", method="password")
            else: pwd = saved_pwd
        else:
            sender.reply(config["password_tip"])
            pwd = get_input(
                sender,
                validator=lambda t: bool(re.fullmatch(r"\S{8,20}", t)),
                error_tip="❌ 密码格式错误,请输入8到20位:",
                retry_limit=config["password_retry_limit"],
            )
            if not pwd: return
            sender.reply("是否保存账号和密码以便下次一键登录?\n【1】保存\n【2】不保存\n(q 退出)")
            save_choice = get_input(sender, validator=lambda t: t in ("1", "2", "q"))
            if save_choice in ("q", None, "2"):
                add_history_account(userid, phone, "", method="password")
                if save_choice == "q": return
            elif save_choice == "1":
                add_history_account(userid, phone, pwd, method="password")
                sender.reply("✅ 账号和密码已保存,下次可一键登录")

    sender.reply(f"⏳ 正在使用账号密码登录...\n📱 {mask_phone(phone)}")
    if actual_api == 0: ck = do_rabbit_password_login(sender, config, phone, pwd)
    else: ck = do_pro_password_login(sender, config, phone, pwd)
    if not ck: return
    if "pt_key=" not in ck:
        sender.reply("❌ 登录失败,未返回有效Cookie")
        return
    success, panels = commit_cookie_to_ql(sender, userid, ck, config["ql_var_name"])
    if success:
        pin = get_pin_from_cookie(ck)
        pin_dec = decode_pin(pin)
        sender.reply(f"✅ 账号密码登录成功\n📱 手机: {mask_phone(phone)}\n👤 账号: {pin_dec}\n📦 已写入: {', '.join(panels)}")
        notify_admin(config, f"用户{userid}通过账密登录: {pin_dec}")
        run_inline_command(config)
        save_password_to_ql(sender, config, pin_dec, phone, pwd)

def do_rabbit_password_login(sender, config, phone, pwd):
    if not is_rabbit_configured(config):
        sender.reply("❌ RabbitPro服务未启用或未配置")
        return None

    def rabbit_api(path, body, timeout=90):
        try:
            resp = requests.post(
                f"{config['rabbit_url']}{path}?BotApiToken={urllib.parse.quote(config['rabbit_token'])}",
                json=body, timeout=timeout, verify=False,
            )
            return resp.json() if resp.status_code == 200 else {}
        except Exception as e:
            return {"message": friendly_err(e)}

    init_data = rabbit_api("/bot/pwd/init", {"account": phone})
    if not init_data.get("success") and init_data.get("code") == 666:
        sender.reply("⚠️ 需要图形验证,自动处理中...")
        auto = rabbit_api("/bot/pwd/AutoCaptcha", {"account": phone})
        if not auto.get("success"):
            sender.reply(f"❌ 图形验证失败: {auto.get('message') or auto.get('msg')}")
            return None
    elif not init_data.get("success"):
        sender.reply(f"❌ 初始化失败: {init_data.get('message') or init_data.get('msg')}")
        return None
    try: encrypted_pwd = rabbit_pro_encrypt_pwd(phone, pwd)
    except Exception as e:
        sender.reply(f"❌ 密码加密失败: {e}\n💡 请安装 cryptography: pip install cryptography")
        return None
    data = rabbit_api("/bot/pwd/login", {"account": phone, "pwd": encrypted_pwd})
    if data.get("success") and data.get("ck"): return data["ck"]
    if data.get("code") in (601, 602):
        sender.reply("⚠️ 需要短信验证,正在发送...")
        rabbit_api("/bot/risk/risk_send", {"account": phone})
        sender.reply(f"📱 {mask_phone(phone)} {config['code_tip']}")
        code = get_input(
            sender,
            validator=lambda t: bool(re.fullmatch(r"\d{6}", t)),
            error_tip="❌ 验证码格式错误,请重新输入:",
            retry_limit=3,
        )
        if not code: return None
        verify = rabbit_api("/bot/risk/risk_verify_code", {"account": phone, "code": code})
        if verify.get("ck"): return verify["ck"]
    sender.reply(f"❌ RabbitPro账密登录失败: {data.get('message') or data.get('msg') or '未知'}")
    return None

def do_pro_password_login(sender, config, phone, pwd):
    if not is_pro_configured(config):
        sender.reply("❌ Pro服务未启用或未配置")
        return None
    payload = {"username": phone, "password": pwd, "BotApitoken": config["pro_token"]}
    for retry in range(3):
        try:
            resp = requests.post(f"{config['pro_url']}/Pwd/Login", json=payload, timeout=60, verify=False)
            data = resp.json() if resp.status_code == 200 else {}
            if data.get("success"):
                ck = (data.get("data") or {}).get("ck", "")
                if ck: return ck
                sender.reply("❌ Pro返回未带Cookie")
                return None
            sub = data.get("data") or {}
            msg = str(data.get("message") or "")
            if retry < 2 and re.search(r"哦豁|获取im失败|加载异常", msg):
                time.sleep(1)
                continue
            if sub.get("status") == 555:
                sender.reply(f"❌ {msg}\n{sub.get('jmp_url') or sub.get('RiskUrl') or ''}")
                return None
            sender.reply(f"❌ Pro账密登录失败: {msg or '未知'}")
            return None
        except Exception as e:
            sender.reply(f"❌ Pro账密登录异常: {friendly_err(e)}")
            return None
    return None

def save_password_to_ql(sender, config, pin, phone, pwd):
    try:
        remark = f"{pin}@{pin}"
        value = f"{phone}#{pwd}"
        panels = load_ql_panels()
        for panel_info in panels:
            try:
                ql = QingLongClient(panel_info)
                envs = ql.search_envs(remark)
                found = [e for e in envs if e.get("name") == config["auto_pwd_var"]]
                if found:
                    env_id = found[0].get(ql.id_key) or found[0].get("_id") or found[0].get("id")
                    ql.edit_env({"name": config["auto_pwd_var"], "value": value, "remarks": remark, ql.id_key: env_id})
                    ql.enable_env(env_id)
                else:
                    ql.add_envs([{"name": config["auto_pwd_var"], "value": value, "remarks": remark}])
            except Exception as e:
                _log("保存账密到青龙失败:", e)
    except: pass


# ===================== ✨ 主入口 =====================

def main():
    global sender
    try:
        if not sender:
            sender_id = middleware.getSenderID()
            if not sender_id:
                middleware.reply("❌ 无法获取用户ID")
                return
            sender = middleware.Sender(sender_id)
        userid = sender.getUserID() or ""
        if not userid:
            sender.reply("❌ 无法获取用户ID")
            return
        msg = ""
        try: msg = sender.getMessage() or ""
        except: pass
        msg = msg.strip()

        # ✨ 新增独立管理员指令逻辑
        if msg == "京东续期":
            config = get_config()
            if not check_admin(sender, config):
                sender.reply("❌ 权限不足: 仅管理员可执行该指令！")
                return
            
            # ====== 以下为修改内容：跳过菜单，直接执行“一键续期全部账号” ======
            if config.get("code_api_type") != "yyb":
                sender.reply("❌ Code续期仅支持yyb模式")
                return
                
            accounts = _get_user_bound_code_accounts(userid, config)
            # is_admin=True 会获取所有账号进行续期
            accounts = _filter_accounts_for_user(accounts, userid, is_admin=True)
            
            if not accounts:
                sender.reply("❌ 暂未绑定任何微信账号\n💡 请先完成【微信扫码登录】后再来续期")
                return
                
            sender.reply(f"⏳ 管理员指令: 正在一键检测并续期 {len(accounts)} 个账号，请稍候...")
            succ = skip = fail = 0
            for acc in accounts:
                # 遍历直接调用续期核心函数
                ok, msg_reply, _ = _refresh_one_code_account(config, sender, userid, acc, is_admin=True)
                sender.reply(msg_reply) # 实时回复每个账号的续期状态
                if ok: 
                    if "跳过续期" in msg_reply: 
                        skip += 1
                    else: 
                        succ += 1
                else: 
                    fail += 1
                    
            sender.reply(f"📊 批量操作完成: 成功续期 {succ}, 有效跳过 {skip}, 失败 {fail}")
            return
            # ====== 修改结束 ======

        if msg not in ("登录", "登陆", "上车"):
            return
            
        config = get_config()

        if not check_platform_enabled(config, sender):
            sender.reply("❌ 当前平台未启用登录")
            return
        if not check_white_list(sender, config):
            sender.reply("❌ 当前群未开启登录功能")
            return

        pro_ok = is_pro_configured(config)
        rabbit_ok = is_rabbit_configured(config)
        code_ok = is_code_configured(config)
        if not pro_ok and not rabbit_ok and not code_ok:
            sender.reply(
                "❌ 未配置任何登录服务\n"
                "💡 请至少完成以下之一:\n"
                "  • 启用 Pro + 配置 proUrl + proBotApiToken\n"
                "  • 启用 RabbitPro + 配置 rabbitProUrl + rabbitBotApiToken\n"
                "  • 启用微信Code + 配置 codeServerUrl"
            )
            return

        history = get_history_accounts(userid) if config["save_history"] else []
        lines, enabled_methods = build_login_menu(config, history)
        sender.reply("\n".join(lines))

        if not enabled_methods:
            sender.reply("❌ 当前没有可用的登录方式\n💡 请在后台插件配置启用至少一种登录方式")
            return

        inp = get_input(sender, validator=lambda t: t.isdigit() or t.lower() == "q")
        if not inp: return
        if inp.lower() == "q":
            sender.reply("✅ 已退出")
            return
        try: choice = int(inp)
        except ValueError:
            sender.reply("❌ 输入无效")
            return
        if choice < 1 or choice > len(enabled_methods):
            sender.reply("❌ 选择无效")
            return

        selected = enabled_methods[choice - 1]
        method_id = selected["id"]

        # 短信登录走二级菜单(选手机号或历史账号)
        if method_id in ("pro_sms", "rabbit_sms"):
            if method_id == "pro_sms" and not is_pro_configured(config):
                sender.reply("❌ Pro服务未启用或未配置")
                return
            if method_id == "rabbit_sms" and not is_rabbit_configured(config):
                sender.reply("❌ RabbitPro服务未启用或未配置")
                return
            sms_lines, sms_methods = build_sms_submenu(config, history)
            sender.reply("\n".join(sms_lines))
            sms_inp = get_input(sender, validator=lambda t: t.isdigit() or t.lower() == "q")
            if not sms_inp: return
            if sms_inp.lower() == "q":
                sender.reply("✅ 已退出")
                return
            try: sms_choice = int(sms_inp)
            except ValueError:
                sender.reply("❌ 输入无效")
                return
            # 0=新增手机号, 1-N=历史账号一键登录
            if sms_choice < 0 or sms_choice > len([m for m in sms_methods if m["id"] == "sms_history"]):
                sender.reply("❌ 选择无效")
                return
            if sms_choice == 0:
                # 新增手机号: phone=None 让 run_xxx_sms_login 自己输入
                if method_id == "pro_sms": run_pro_sms_login(sender, userid)
                else: run_rabbit_sms_login(sender, userid)
            else:
                # 历史账号一键登录: phone=xxx 自动发验证码
                sms_history = []
                for a in history:
                    m = str(a.get("method", "") or "").strip().lower()
                    if not m:
                        m = "sms" if not a.get("pwd") else "password"
                    if m == "sms":
                        sms_history.append(a)
                if sms_choice - 1 >= len(sms_history):
                    sender.reply("❌ 历史账号数据已变更,请重新选择")
                    return
                hist_phone = sms_history[sms_choice - 1].get("phone", "")
                if not hist_phone:
                    sender.reply("❌ 历史账号数据异常")
                    return
                sender.reply(f"🔁 历史账号一键登录\n📱 {mask_phone(hist_phone)}\n🔧 登录方式: 短信验证")
                if method_id == "pro_sms": run_pro_sms_login(sender, userid, phone=hist_phone)
                else: run_rabbit_sms_login(sender, userid, phone=hist_phone)
            return

        if method_id == "code_qr": run_code_qr_login(sender, userid)
        elif method_id == "pro_qr": run_pro_qr_login(sender, userid)
        elif method_id == "pro_short": run_pro_short_login(sender, userid)
        elif method_id == "rabbit_qr": run_rabbit_qr_login(sender, userid, short=False)
        elif method_id == "rabbit_short": run_rabbit_qr_login(sender, userid, short=True)
        elif method_id == "password": run_password_login(sender, userid)
        else: sender.reply(f"❌ 未实现的登录方式: {method_id}")

    except Exception as e:
        err = f"❌ 插件执行出错: {friendly_err(e)}"
        try:
            if sender: sender.reply(err)
            else: middleware.reply(err)
        except:
            try: middleware.reply(err)
            except: pass

if __name__ == "__main__":
    main()