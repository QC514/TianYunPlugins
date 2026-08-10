# [language: python]
# [wb: true]
# [service: YYB JD scan login]
# [disable:false]
# [admin: false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [priority: 101]
# [open_source: false]
# [public: false]
# [rule: ^登录$|^登陆$|^京东登录$|^京东登陆$|^登录京东$|^登陆京东$|^扫码$|^扫码登录$|^扫码登陆$]
# [author: 1934103887]
# [title: 京东应用宝协议]
# [version: 2.0.0]
# [description: 应用宝微信扫码登录，换取 JD pt_key/pt_pin，并上传 JD_COOKIE。]
# [param: {"required":true,"key":"Joh_jd_config.Qinglong","bool":false,"placeholder":"http://127.0.0.1:5700----clientID----clientSecret","name":"青龙配置","desc":"格式：http://青龙地址----clientID----clientSecret"}]
# [param: {"required":false,"key":"Joh_jd_config.YYB_GO_URL","bool":false,"placeholder":"http://192.168.10.7:18080","name":"应用宝扫码服务","desc":"yyb_go_pure 服务地址，默认 http://192.168.10.7:18080"}]
# [param: {"required":false,"key":"Joh_jd_config.WX","bool":false,"placeholder":"","name":"通知管理员WX","desc":"有用户登录会通知WX管理员，不填不推送"}]
# [param: {"required":false,"key":"Joh_jd_config.QQ","bool":false,"placeholder":"","name":"通知管理员QQ","desc":"有用户登录会通知QQ管理员，不填不推送"}]
# [param: {"required":false,"key":"Joh_jd_config.TG","bool":false,"placeholder":"","name":"通知管理员TG","desc":"有用户登录会通知TG管理员，不填不推送"}]

# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
from typing import Any

import requests

try:
    requests.packages.urllib3.disable_warnings()  # type: ignore[attr-defined]
except Exception:
    pass


try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


try:
    import middleware  # type: ignore
except ModuleNotFoundError:
    class _LocalSender:
        def __init__(self, sid="local"):
            self.sid = sid

        def getImtype(self): return "local"
        def getUserID(self): return self.sid
        def getMessage(self): return ""

        def reply(self, msg):
            print(msg)
            return msg

        def listen(self, ms): return None

    class _LocalMiddleware:
        _bucket = {}

        @classmethod
        def bucketGet(cls, bucket, key): return cls._bucket.get((bucket, key), "")
        @classmethod
        def bucketSet(cls, bucket, key, value): cls._bucket[(bucket, key)] = value
        @classmethod
        def bucketKeys(cls, bucket, value):
            return [k for (b, k), v in cls._bucket.items() if b == bucket and str(v) == str(value)]
        @classmethod
        def bucketDel(cls, bucket, key): cls._bucket.pop((bucket, key), None)

        @staticmethod
        def getSenderID(): return "local"
        Sender = _LocalSender

    middleware = _LocalMiddleware()  # type: ignore


DEFAULT_YYB_GO_URL = "http://192.168.10.7:18080"
YYB_SCAN_WAIT_SECONDS = 120
YYB_SCAN_POLL_INTERVAL_SECONDS = 3
REQUEST_TIMEOUT = 15

ADMIN_QQ = (middleware.bucketGet("Joh_jd_config", "QQ") or "").strip()
ADMIN_WX = (middleware.bucketGet("Joh_jd_config", "WX") or "").strip()
ADMIN_TG = (middleware.bucketGet("Joh_jd_config", "TG") or "").strip()

LOGIN_COMMANDS = {"登录", "登陆", "京东登录", "京东登陆", "登录京东", "登陆京东"}
QR_COMMANDS = {"扫码", "扫码登录", "扫码登陆"}


class _YYBJDClient:
    @staticmethod
    def _unwrap(resp):
        try:
            data = resp.json()
        except Exception as exc:
            raise RuntimeError(f"non-json response: HTTP {resp.status_code} {resp.text[:300]}") from exc
        if resp.status_code < 200 or resp.status_code >= 300:
            raise RuntimeError(str(data.get("msg") or data.get("message") or data.get("error") or f"HTTP {resp.status_code}"))
        if isinstance(data, dict) and "code" in data and "data" in data:
            if str(data.get("code")) not in ("0", "200"):
                raise RuntimeError(str(data.get("msg") or data.get("message") or data))
            payload = data.get("data")
            return payload if isinstance(payload, dict) else {"value": payload}
        return data if isinstance(data, dict) else {"value": data}

    @staticmethod
    def _abs_url(base_url, path_or_url):
        path_or_url = str(path_or_url or "").strip()
        if not path_or_url:
            return ""
        if urllib.parse.urlsplit(path_or_url).scheme:
            return path_or_url
        return base_url.rstrip("/") + "/" + path_or_url.lstrip("/")

    def create_qr(self, yyb_url, timeout=45):
        data = self._unwrap(requests.post(yyb_url.rstrip("/") + "/qr?as_base64=true", timeout=timeout))
        if not data.get("session_id"):
            raise RuntimeError("QR response missing session_id")
        if data.get("image_url"):
            data["image_url_abs"] = self._abs_url(yyb_url, data.get("image_url"))
        return data

    def poll_qr(self, yyb_url, session_id, timeout=45):
        url = yyb_url.rstrip("/") + "/qr/" + urllib.parse.quote(str(session_id), safe="") + "/poll"
        return self._unwrap(requests.get(url, timeout=timeout))

    def confirm_qr(self, yyb_url, session_id, timeout=45):
        url = yyb_url.rstrip("/") + "/qr/" + urllib.parse.quote(str(session_id), safe="") + "/confirm"
        return self._unwrap(requests.post(url, timeout=timeout))

    def wait_confirmed_account(self, yyb_url, session_id, wait_seconds=120):
        deadline = time.time() + max(30, int(wait_seconds or 120))
        while time.time() < deadline:
            try:
                data = self.poll_qr(yyb_url, session_id)
            except Exception as exc:
                err = str(exc or "").lower()
                if (
                    "long.open.weixin.qq.com" in err
                    or "context deadline exceeded" in err
                    or "client.timeout exceeded" in err
                    or "awaiting headers" in err
                    or "i/o timeout" in err
                ):
                    continue
                raise
            status = str(data.get("status") or "").lower()
            if status == "authorized":
                return self.confirm_qr(yyb_url, session_id)
            if status == "confirmed":
                return data
            if status in ("expired", "cancelled", "unknown"):
                raise RuntimeError("QR status: " + status)
            wait_left = min(float(YYB_SCAN_POLL_INTERVAL_SECONDS), max(0.2, deadline - time.time()))
            time.sleep(wait_left)
        raise RuntimeError("QR login timeout")

    def exchange_pt(self, openid, yyb_url, timeout=60):
        payload = {"ref": openid}
        resp = requests.post(yyb_url.rstrip("/") + "/jd/pt/exchange", json=payload, timeout=timeout)
        data = self._unwrap(resp)
        if not data.get("success"):
            raise RuntimeError(str(data.get("error") or data.get("message") or data.get("msg") or data))
        if not (data.get("pt_key") and data.get("pt_pin") and data.get("ck")):
            raise RuntimeError("exchange response missing pt_key/pt_pin")
        return data


yybjd = _YYBJDClient()


def _format_yyb_scan_error(exc):
    msg = str(exc or "").strip()
    low = msg.lower()
    if "qr login timeout" in low or "qr status: expired" in low:
        return "扫码超时，已退出请重新发送指令"
    return f"扫码登录失败：{msg}"


def _format_yyb_jdpt_error(exc):
    msg = str(exc or "").strip()
    low = msg.lower()
    if "missing pt_key/pt_pin" in low and "last_status=200" in low:
        return "登陆失败，请微信搜索京东购物-我的-绑定账号后再来"
    if "exchange response missing pt_key/pt_pin" in low:
        return "登陆失败，请微信搜索京东购物-我的-绑定账号后再来"
    return f"换取 pt_key/pt_pin 失败：{msg}"


def _yyb_go_url():
    raw = (
        os.environ.get("YYB_GO_URL")
        or middleware.bucketGet("Joh_jd_config", "YYB_GO_URL")
        or DEFAULT_YYB_GO_URL
    )
    return str(raw or DEFAULT_YYB_GO_URL).strip().rstrip("/")


def process_cookie(cookie: str) -> str:
    m_key = re.search(r"(?:^|[;?,\s])pt_key=([^;?,\s]+)", str(cookie or ""))
    m_pin = re.search(r"(?:^|[;?,\s])pt_pin=([^;?,\s]+)", str(cookie or ""))
    return f"pt_key={m_key.group(1)};pt_pin={m_pin.group(1)};" if m_key and m_pin else ""


def _cookie_pin(cookie: str) -> str:
    pure = process_cookie(cookie or "") or (cookie or "")
    m = re.search(r"(?:^|[;,\s])pt_pin=([^;,\s]+)", pure)
    return m.group(1) if m else ""


def _normalize_pin_for_env(pin):
    raw = str(pin or "").strip()
    if not raw:
        return ""
    try:
        return urllib.parse.quote(urllib.parse.unquote(raw), safe="")
    except Exception:
        return raw


def _cookie_pin_encoded(cookie):
    return _normalize_pin_for_env(_cookie_pin(cookie or ""))


def _pin_variants(pin):
    raw = str(pin or "").strip()
    if not raw:
        return set()
    vals = []

    def add(value):
        if value and value not in vals:
            vals.append(value)

    add(raw)
    try:
        add(urllib.parse.unquote(raw))
    except Exception:
        pass
    try:
        add(urllib.parse.quote(raw, safe=""))
    except Exception:
        pass
    try:
        add(urllib.parse.quote(urllib.parse.unquote(raw), safe=""))
    except Exception:
        pass
    return set(vals)


def _bind_pin_to_sender(sender, pin):
    pin = str(pin or "").strip()
    if not pin:
        return
    try:
        im_type = sender.getImtype()
        pin_db = f"pin{str(im_type).upper()}"
        middleware.bucketSet(pin_db, pin, sender.getUserID())
    except Exception as e:
        print(f"绑定 pin 失败: {e}")


def _parse_ql_config():
    env_url = os.environ.get("QL_URL", "").strip()
    env_id = os.environ.get("QL_CLIENT_ID", "").strip()
    env_secret = os.environ.get("QL_CLIENT_SECRET", "").strip()
    if env_url and env_id and env_secret:
        return env_url.rstrip("/"), env_id, env_secret
    raw = ""
    try:
        raw = (middleware.bucketGet("Joh_jd_config", "Qinglong") or "").strip()
    except Exception:
        raw = ""
    if not raw:
        return "", "", ""
    sep = "丨"
    normalized = raw.replace("｜", sep).replace("|", sep).replace("----", sep)
    if normalized.count(sep) < 2 and raw.startswith(("http://", "https://")) and raw.count("?") >= 2:
        normalized = raw.replace("?", sep)
    parts = [p.strip() for p in normalized.split(sep) if p.strip()]
    if len(parts) >= 3:
        return parts[0].rstrip("/"), parts[1], parts[2]
    return "", "", ""


def _safe_json(resp):
    try:
        return resp.json()
    except Exception:
        try:
            return json.loads(getattr(resp, "text", "") or "{}")
        except Exception:
            return {"code": -1, "message": getattr(resp, "text", "") or "invalid json"}


def _ql_ok(data):
    return isinstance(data, dict) and (str(data.get("code")) in ("0", "200", "201") or data.get("success") is True)


def _ql_items(data):
    if not isinstance(data, dict):
        return []
    payload = data.get("data")
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("data", "list", "items", "envs", "records"):
            val = payload.get(key)
            if isinstance(val, list):
                return val
        if payload.get("name") or payload.get("value") or payload.get("id") or payload.get("_id"):
            return [payload]
    return []


class _QLClient:
    def __init__(self, base_url, client_id, client_secret):
        self.base_url = str(base_url or "").rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = ""

    def headers(self):
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json", "Accept": "application/json"}

    def get_token(self):
        resp = requests.get(
            self.base_url + "/open/auth/token",
            params={"client_id": self.client_id, "client_secret": self.client_secret},
            timeout=REQUEST_TIMEOUT,
            verify=False,
        )
        data = _safe_json(resp)
        if not _ql_ok(data):
            raise RuntimeError(f"get ql token failed: {data}")
        payload = data.get("data") or {}
        self.token = payload.get("token") or data.get("token") or ""
        if not self.token:
            raise RuntimeError(f"get ql token empty: {data}")
        return self.token

    def get_envs(self, search_value=""):
        params = {"searchValue": str(search_value).strip()} if search_value else None
        resp = requests.get(self.base_url + "/open/envs", headers=self.headers(), params=params, timeout=REQUEST_TIMEOUT, verify=False)
        data = _safe_json(resp)
        if not _ql_ok(data):
            raise RuntimeError(f"read ql envs failed: {data}")
        return _ql_items(data)

    def create_env(self, name, value, remarks=""):
        resp = requests.post(
            self.base_url + "/open/envs",
            headers=self.headers(),
            json=[{"name": name, "value": value, "remarks": remarks}],
            timeout=REQUEST_TIMEOUT,
            verify=False,
        )
        return _safe_json(resp)

    def update_env(self, env_id, name, value, remarks=""):
        base = {"name": name, "value": value, "remarks": remarks}
        env_id_str = str(env_id)
        payloads = []
        if env_id_str.isdigit():
            payloads.append(dict(base, id=int(env_id_str)))
            payloads.append(dict(base, _id=env_id_str))
        else:
            payloads.append(dict(base, _id=env_id_str))
            payloads.append(dict(base, id=env_id_str))
        last = None
        for payload in payloads:
            resp = requests.put(self.base_url + "/open/envs", headers=self.headers(), json=payload, timeout=REQUEST_TIMEOUT, verify=False)
            data = _safe_json(resp)
            if _ql_ok(data):
                return data
            last = data
        return last or {"code": -1, "message": "update failed"}

    def enable_env(self, env_id):
        variants = [[int(env_id) if str(env_id).isdigit() else env_id], [str(env_id)]]
        last = None
        for body in variants:
            resp = requests.put(self.base_url + "/open/envs/enable", headers=self.headers(), json=body, timeout=REQUEST_TIMEOUT, verify=False)
            data = _safe_json(resp)
            if _ql_ok(data):
                return data
            last = data
        return last or {"code": -1, "message": "enable failed"}


def _env_id(item):
    if not isinstance(item, dict):
        return None
    return item.get("id") if item.get("id") is not None else item.get("_id")


def _upsert_ql_env(name, value, remarks=""):
    ql_url, ql_id, ql_secret = _parse_ql_config()
    if not (ql_url and ql_id and ql_secret):
        return {"ok": False, "message": "QL config missing"}
    ql = _QLClient(ql_url, ql_id, ql_secret)
    ql.get_token()
    try:
        envs = ql.get_envs(remarks or name)
    except Exception:
        envs = ql.get_envs("")

    remark_set = _pin_variants(remarks)
    existing = None
    for item in envs:
        if not isinstance(item, dict) or item.get("name") != name:
            continue
        old_value = item.get("value") or ""
        old_remarks = str(item.get("remarks") or item.get("remark") or "")
        old_pin = ""
        m = re.search(r"(?:^|[;,\s])(?:pt_pin|pin|jdPin)=([^;,\s]+)", old_value)
        if m:
            old_pin = m.group(1)
        if (
            (old_pin and (_pin_variants(old_pin) & remark_set))
            or (_pin_variants(old_remarks) & remark_set)
            or old_value == value
        ):
            existing = item
            break

    if existing:
        item_id = _env_id(existing)
        if item_id is None or item_id == "":
            return {"ok": False, "message": "existing env has no id"}
        ret = ql.update_env(item_id, name, value, remarks)
        if not _ql_ok(ret):
            return {"ok": False, "message": f"update failed: {ret}"}
        try:
            ql.enable_env(item_id)
        except Exception:
            pass
        return {"ok": True, "action": "update"}

    ret = ql.create_env(name, value, remarks)
    if not _ql_ok(ret):
        return {"ok": False, "message": f"create failed: {ret}"}
    return {"ok": True, "action": "create"}


def _upload_cookie_result(cookie):
    pure = process_cookie(cookie or "")
    if not pure:
        return {"status": "fail", "message": "pt_key/pt_pin not found"}
    pin = _cookie_pin_encoded(pure)
    if not pin:
        return {"status": "fail", "message": "pt_pin not found"}
    try:
        ret = _upsert_ql_env("JD_COOKIE", pure, pin)
        return {"status": "success" if ret.get("ok") else "fail", "message": ret.get("message") or ret.get("action") or str(ret), **ret}
    except Exception as exc:
        return {"status": "error", "message": str(exc)}


def _reply_image(sender, image_src, fallback_url=""):
    try:
        if hasattr(sender, "replyImage"):
            sender.replyImage(image_src)
            return
    except Exception as e:
        print(f"发送二维码图片失败: {e}")
    return sender.reply("二维码已生成，但当前平台不支持直接发送图片，请联系管理员查看 18080 扫码页。")


def _save_yybjd_state(sender, pin, cookie, openid, exchange_data=None, account_data=None):
    pin = _normalize_pin_for_env(pin)
    if not pin:
        return {"ok": False, "message": "missing pin"}
    exchange_data = exchange_data if isinstance(exchange_data, dict) else {}
    account_data = account_data if isinstance(account_data, dict) else {}
    record = {
        "pin": pin,
        "pt_pin": exchange_data.get("pt_pin") or pin,
        "jd_cookie": process_cookie(cookie or ""),
        "openid": openid,
        "yyb_ref": openid,
        "yyb_url": _yyb_go_url(),
        "pt_url": _yyb_go_url().rstrip("/") + "/jd/pt/exchange",
        "user_id": sender.getUserID(),
        "im_type": sender.getImtype(),
        "nickname": account_data.get("nickname"),
        "uin": account_data.get("uin"),
        "status": account_data.get("status"),
        "pt_token": exchange_data.get("pt_token") or "",
        "sfstoken": exchange_data.get("sfstoken") or "",
        "saved_at": int(time.time()),
    }
    try:
        middleware.bucketSet("YYBJD", pin, json.dumps(record, ensure_ascii=False))
        if openid:
            middleware.bucketSet("YYBJD_OPENID", openid, pin)
        return {"ok": True, "message": "saved YYBJD"}
    except Exception as e:
        print(f"保存 YYBJD 失败: {e}")
        return {"ok": False, "message": str(e)}


def logined_notice(sender, pin, login_type):
    try:
        admin_msg = (
            "======JD登陆通知======\n"
            f"[登陆用户]：{sender.getUserID()}\n"
            f"[登陆平台]：{sender.getImtype()}\n"
            f"[登陆账户]：{urllib.parse.unquote(str(pin or ''))}\n"
            f"[登陆方式]：{login_type}\n"
            f"[登陆时间]：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())} "
        )
        if ADMIN_QQ:
            middleware.push("qq", "", ADMIN_QQ, "", admin_msg)
        if ADMIN_WX:
            middleware.push("wx", "", ADMIN_WX, "", admin_msg)
        if ADMIN_TG:
            middleware.push("tg", "", ADMIN_TG, "", admin_msg)
    except Exception as e:
        print(f"登录通知处理失败: {e}")


def _success_reply(sender, cookie, upload_ret=None, login_type="扫码"):
    pin_encoded = _cookie_pin(cookie or "")
    pin = urllib.parse.unquote(pin_encoded or "") or "未知"
    if pin_encoded:
        _bind_pin_to_sender(sender, _normalize_pin_for_env(pin_encoded))
    upload_ret = upload_ret or {}
    if upload_ret:
        print("[JD_COOKIE upload]", upload_ret.get("message") or upload_ret.get("status") or str(upload_ret))
    msg = f"🎉 {login_type}登录成功! 账号: {pin}"
    logined_notice(sender, pin, login_type)
    return sender.reply(msg)


def handle_yyb_scan_login(sender):
    yyb_url = _yyb_go_url()
    sender.reply("⌛ 正在加载二维码，请稍后...")
    try:
        qr = yybjd.create_qr(yyb_url)
    except Exception as e:
        return sender.reply(f"生成二维码失败：{e}")
    session_id = str(qr.get("session_id") or "")
    if not session_id:
        return sender.reply("生成二维码失败：缺少 session_id")
    fallback_url = qr.get("image_url_abs") or ""
    image_src = fallback_url or qr.get("image_base64") or ""
    if image_src:
        _reply_image(sender, image_src, fallback_url=fallback_url)
    sender.reply(
        "==================\n"
        "📱 请使用微信后置摄像头扫码\n"
        "💡 微信需绑定京东购物小程序\n"
        "=================="
    )

    try:
        account = yybjd.wait_confirmed_account(yyb_url, session_id, wait_seconds=YYB_SCAN_WAIT_SECONDS)
    except Exception as e:
        return sender.reply(_format_yyb_scan_error(e))

    openid = str(account.get("openid") or account.get("openId") or "").strip()
    if not openid:
        return sender.reply("扫码已确认，但未返回 openid，无法继续换 CK。")
    sender.reply("扫码已确认，正在进行登陆...")
    try:
        exchange_data = yybjd.exchange_pt(openid, yyb_url=yyb_url)
    except Exception as e:
        return sender.reply(_format_yyb_jdpt_error(e))

    cookie = process_cookie(exchange_data.get("ck") or "")
    if not cookie:
        return sender.reply("已返回结果，但未识别到有效 pt_key/pt_pin。")
    pin_encoded = _cookie_pin_encoded(cookie)
    _save_yybjd_state(sender, pin_encoded, cookie, openid, exchange_data=exchange_data, account_data=account)
    upload_ret = _upload_cookie_result(cookie)
    return _success_reply(sender, cookie, upload_ret, login_type="扫码")


def process_message():
    sender = middleware.Sender(middleware.getSenderID())
    msg = (sender.getMessage() or "").strip()
    try:
        if msg in LOGIN_COMMANDS or msg in QR_COMMANDS:
            return handle_yyb_scan_login(sender)
    except Exception as e:
        print(f"登录插件异常: {e}")
        return sender.reply(f"系统异常: {e}")
    return None


if __name__ == "__main__":
    process_message()
