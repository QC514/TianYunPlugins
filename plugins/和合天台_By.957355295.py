# [pin:true]
# [public:true]
# [rule: ^(和合查询|查询和合|和合登录|登录和合|和合登陆|登陆和合|和合授权|授权和合|和合教程|和合授权检测|和合通知|通知和合|和合删除|删除和合|和合管理|管理和合|和合管理员|管理员和合|天台链接)(\s.*)?$]
# [cron: 0 5 0 * * *]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [version: 1.0]
# [admin: false]
# [author: 957355295]
# [author: hhtt]
# [price: 0]
# [title: 和合天台]
# [icon: https://pp.myapp.com/ma_icon/0/icon_42259219_1711261436/256]
# [description: 和合天台青龙/呆呆面板对接插件，仅负责把账号变量提交到面板，不包含任何内置任务；请配合定时脚本使用。]
# [param: {"required":false,"key":"dd_hhttconfig.PanelType","bool":false,"placeholder":"qinglong 或 daidai","name":"面板类型","desc":"对接面板：qinglong=青龙，daidai=呆呆（DaiDaiPanel），不填默认为青龙"}]
# [param: {"required":true,"key":"dd_hhttconfig.Qinglong","bool":false,"placeholder":"青龙: URL丨ClientID丨ClientSecret；呆呆: URL丨app_key丨app_secret","name":"设置对接容器","desc":"青龙用丨分割3项；呆呆为 Open API 的 host、app_key、app_secret"}]
# [param: {"required":true,"key":"dd_hhttconfig.osname","bool":false,"placeholder":"必填项,例:HHTT","name":"变量名","desc":"面板内和合天台账号使用的变量名（青龙/呆呆通用，建议填 HHTT）"}]
# [param: {"required":false,"key":"dd_hhttconfig.link_osname","bool":false,"placeholder":"例:HHTT_LINK","name":"抽奖链接变量名","desc":"面板中保存和合天台当月抽奖链接使用的变量名，默认 HHTT_LINK"}]
# [param: {"required":false,"key":"dd_hhttconfig.sqje","bool":false,"placeholder":"例:6.6,不填为0元","name":"授权金额","desc":"每个账号授权金额(单位:元)"}]
# [param: {"required":false,"key":"dd_hhttconfig.sqsj","bool":false,"placeholder":"例:30,不填为30天","name":"授权天数","desc":"授权有效天数，默认30天"}]
# [param: {"required":false,"key":"dd_hhttconfig.wccoin","bool":false,"placeholder":"例:100,不填为关闭积分支付","name":"积分支付","desc":"授权一个账号需要多少积分（只能为整数）"}]
# [param: {"required":false,"key":"dd_hhttconfig.wxzsm","bool":false,"placeholder":"http://127.0.0.1/赞赏码.png","name":"赞赏码链接","desc":"用于扫码支付的赞赏码链接"}]
# [param: {"required":false,"key":"dd_hhttconfig.sdyx","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统，开启后将使用卡密系统配置的码支付"}]

import json
import re
import time
import hashlib

import middleware
import requests

try:
    from datetime import datetime, timedelta
except Exception:
    datetime = None
    timedelta = None


senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
dd_hhtt_osname = middleware.bucketGet("dd_hhttconfig", "osname") or "HHTT"
dd_hhtt_link_osname = middleware.bucketGet("dd_hhttconfig", "link_osname") or "HHTT_LINK"
dd_hhtt_qlname = middleware.bucketGet("dd_hhttconfig", "Qinglong")
dd_hhtt_panel_type = (middleware.bucketGet("dd_hhttconfig", "PanelType") or "qinglong").strip().lower()
sqje = middleware.bucketGet("dd_hhttconfig", "sqje") or "0"
sqsj = middleware.bucketGet("dd_hhttconfig", "sqsj") or "30"
wccoin = middleware.bucketGet("dd_hhttconfig", "wccoin") or "0"
BUCKET_PENDING = "dd_hhtt_pending"
wxzsm = middleware.bucketGet("dd_hhttconfig", "wxzsm")
today_time = time.strftime("%Y-%m-%d", time.localtime())


def _safe_int(v, default=0):
    try:
        return int(str(v).strip())
    except Exception:
        return default


def _expiry_date_str(days: int) -> str:
    if not datetime or not timedelta:
        return today_time
    return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")


def _parse_remarks(remarks: str) -> dict:
    """
    remarks 格式：和合天台:{name}丨账户:{account}丨用户:{uid}丨授权时间:{YYYY-MM-DD}丨和合授权
    """
    s = remarks or ""
    parts = [p.strip() for p in s.split("丨") if p.strip()]
    out = {}
    for p in parts:
        if ":" in p:
            k, v = p.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def _is_expired(expiry_date_str: str) -> bool:
    if not expiry_date_str:
        return True
    if not datetime:
        return False
    try:
        d = datetime.strptime(expiry_date_str.strip(), "%Y-%m-%d").date()
        return d < datetime.now().date()
    except Exception:
        return False


def _get_user_authorized_accounts_map(osname: str) -> dict:
    """
    从面板 remarks 里解析当前用户已授权账号的到期日。
    返回：{账户标识: 到期日字符串}
    """
    try:
        envs = HHTT_ListEnv(osname)
    except Exception:
        return {}

    m = {}
    for env in envs or []:
        r = env.get("remarks") or ""
        info = _parse_remarks(r)
        if info.get("用户") != str(userid):
            continue
        acc = info.get("账户")
        exp = info.get("授权时间")
        if acc:
            m[str(acc)] = exp or ""
    return m


def QLtoken(QLurl, ClientID, ClientSecret):
    url = f"{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise Exception(f"API请求失败，状态码: {response.status_code}")
        result = response.json()
        if result.get("code") == 200 and result.get("data", {}).get("token"):
            return result["data"]["token"]
        else:
            error_msg = result.get("message", "未知错误")
            raise Exception(f"认证失败: {error_msg}")
    except requests.exceptions.Timeout:
        raise Exception("连接超时，请检查网络和青龙面板状态")
    except requests.exceptions.ConnectionError:
        raise Exception("连接失败，请检查青龙地址和面板状态")
    except Exception as e:
        raise Exception(f"系统错误: {str(e)}")


def _get_ql_config():
    if not dd_hhtt_qlname:
        raise Exception("未配置对接容器信息，请先在插件配置中设置")
    parts = [p.strip() for p in dd_hhtt_qlname.split("丨") if p.strip()]
    if len(parts) != 3:
        raise Exception("对接容器格式错误：青龙为 URL丨ClientID丨ClientSecret，呆呆为 URL丨app_key丨app_secret")
    return parts[0], parts[1], parts[2]


def _get_panel_config():
    if not dd_hhtt_qlname:
        raise Exception("未配置对接容器信息，请先在插件配置中设置")
    parts = [p.strip() for p in dd_hhtt_qlname.split("丨") if p.strip()]
    if len(parts) != 3:
        raise Exception("对接容器格式错误：青龙为 URL丨ClientID丨ClientSecret，呆呆为 URL丨app_key丨app_secret")
    if dd_hhtt_panel_type == "daidai":
        return "daidai", parts[0].rstrip("/"), parts[1], parts[2]
    return "qinglong", parts[0], parts[1], parts[2]


def _daidai_get_token(host: str, app_key: str, app_secret: str) -> str:
    url = f"{host}/api/open-api/token"
    payload = {"app_key": app_key, "app_secret": app_secret}
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    token = (data.get("data") or {}).get("access_token")
    if not token:
        raise Exception(data.get("message", "未获取到 access_token"))
    return token


def _daidai_request(host: str, app_key: str, app_secret: str, method: str, path: str, json_data=None, token=None):
    if token is None:
        token = _daidai_get_token(host, app_key, app_secret)
    url = f"{host}{path}" if path.startswith("/") else f"{host}/{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    fn = getattr(requests, method.lower())
    kwargs = {"headers": headers, "timeout": 10}
    if json_data is not None:
        kwargs["json"] = json_data
    resp = fn(url, **kwargs)
    if resp.status_code == 401:
        token = _daidai_get_token(host, app_key, app_secret)
        headers["Authorization"] = f"Bearer {token}"
        resp = fn(url, **kwargs)
    return resp


def _daidai_find_env(host: str, app_key: str, app_secret: str, name: str, keyword: str = ""):
    path = f"/api/envs?keyword={name}&page_size=100"
    resp = _daidai_request(host, app_key, app_secret, "get", path)
    if resp.status_code != 200:
        raise Exception(f"呆呆面板请求失败，状态码: {resp.status_code}")
    for env in (resp.json().get("data") or []):
        if env.get("name") == name:
            if not keyword or (keyword in (env.get("remarks") or "")):
                return env.get("id")
    return None


def _daidai_add_env(host: str, app_key: str, app_secret: str, name: str, value: str, remarks: str = "") -> bool:
    path = "/api/envs"
    data = {"name": name, "value": value, "remarks": remarks}
    resp = _daidai_request(host, app_key, app_secret, "post", path, json_data=data)
    return resp.status_code == 200


def _daidai_update_env(host: str, app_key: str, app_secret: str, env_id, name: str, value: str, remarks: str = "") -> bool:
    path = f"/api/envs/{env_id}"
    data = {"name": name, "value": value, "remarks": remarks}
    resp = _daidai_request(host, app_key, app_secret, "put", path, json_data=data)
    return resp.status_code == 200


def _daidai_delete_env(host: str, app_key: str, app_secret: str, env_id) -> bool:
    path = f"/api/envs/{env_id}"
    resp = _daidai_request(host, app_key, app_secret, "delete", path)
    return resp.status_code == 200


def _daidai_list_envs(host: str, app_key: str, app_secret: str, keyword: str):
    path = f"/api/envs?keyword={keyword}&page_size=100"
    resp = _daidai_request(host, app_key, app_secret, "get", path)
    if resp.status_code != 200:
        raise Exception(f"呆呆面板请求失败，状态码: {resp.status_code}")
    raw = resp.json().get("data") or []
    return [
        {
            "id": e.get("id"),
            "name": e.get("name", ""),
            "value": e.get("value", ""),
            "remarks": e.get("remarks") or "",
        }
        for e in raw
    ]


def _ql_request(method, url_suffix, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            QLurl, ClientID, ClientSecret = _get_ql_config()
            qltoken = QLtoken(QLurl, ClientID, ClientSecret)
            headers = {
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
                "Content-Type": "application/json",
            }
            func = getattr(requests, method.lower())
            response = func(
                f"{QLurl}{url_suffix}",
                headers=headers,
                json=data,
                timeout=10,
                verify=False,
            )
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 200:
                    return result
                elif attempt == 2:
                    raise Exception(f"操作失败: {result.get('message', '未知错误')}")
            elif attempt == 2:
                raise Exception(f"请求失败，状态码: {response.status_code}")
            time.sleep(1)
        except requests.exceptions.Timeout:
            if attempt == 2:
                raise Exception("连接超时，请检查网络和青龙面板状态")
            time.sleep(1)
        except Exception as e:
            if attempt == 2:
                raise Exception(f"面板操作失败: {str(e)}")
            time.sleep(1)


def QL_add_env(osname, value, account, name, auth_time=None, user_id=None):
    auth_time = auth_time or today_time
    owner_uid = user_id or userid
    remarks = f"和合天台:{name}丨账户:{account}丨用户:{owner_uid}丨授权时间:{auth_time}丨和合授权"
    result = _ql_request(
        "post",
        "/open/envs",
        [{"value": value, "name": osname, "remarks": remarks}],
    )
    if result and "value must be unique" not in str(result):
        return result.get("data", [{}])[0].get("id")


def QL_update_env(osname, value, account, qlid, name, auth_time=None, user_id=None):
    auth_time = auth_time or today_time
    owner_uid = user_id or userid
    remarks = f"和合天台:{name}丨账户:{account}丨用户:{owner_uid}丨授权时间:{auth_time}丨和合授权"
    _ql_request(
        "put",
        "/open/envs",
        {"value": value, "name": osname, "remarks": remarks, "id": qlid},
    )


def HHTT_AddOrUpdateEnv(osname, value, account, name, auth_time=None, user_id=None):
    auth_time = auth_time or today_time
    owner_uid = user_id or userid
    remarks = f"和合天台:{name}丨账户:{account}丨用户:{owner_uid}丨授权时间:{auth_time}丨和合授权"

    panel_type, p1, p2, p3 = _get_panel_config()
    if panel_type == "daidai":
        host, app_key, app_secret = p1, p2, p3
        env_id = _daidai_find_env(host, app_key, app_secret, osname, keyword=account)
        if env_id:
            ok = _daidai_update_env(host, app_key, app_secret, env_id, osname, value, remarks)
        else:
            ok = _daidai_add_env(host, app_key, app_secret, osname, value, remarks)
        if not ok:
            raise Exception("呆呆面板添加/更新环境变量失败")
        return True

    QLurl, ClientID, ClientSecret = p1, p2, p3
    qltoken = QLtoken(QLurl, ClientID, ClientSecret)
    resp = requests.get(
        f"{QLurl}/open/envs",
        headers={
            "Authorization": f"Bearer {qltoken}",
            "accept": "application/json",
        },
        timeout=10,
        verify=False,
    )
    if resp.status_code != 200:
        raise Exception(f"获取青龙环境变量失败，HTTP 状态码: {resp.status_code}")
    result = resp.json()
    if result.get("code") != 200:
        raise Exception(
            f"获取青龙环境变量失败，错误信息: {result.get('message', '未知错误')}"
        )
    account_key, name_key = f"账户:{account}", f"和合天台:{name}"
    qlid = next(
        (
            env["id"]
            for env in result.get("data", [])
            if env.get("name") == osname
            and env.get("remarks")
            and (
                account_key in env["remarks"]
                or (name_key in env["remarks"] and env.get("value") == value)
            )
        ),
        None,
    )
    if qlid:
        QL_update_env(
            osname=osname, value=value, account=account, qlid=qlid, name=name,
            auth_time=auth_time, user_id=user_id,
        )
    else:
        QL_add_env(
            osname=osname, value=value, account=account, name=name,
            auth_time=auth_time, user_id=user_id,
        )
    return True


def HHTT_DeleteEnv(env_id):
    if not env_id:
        return
    try:
        panel_type, p1, p2, p3 = _get_panel_config()
        if panel_type == "daidai":
            host, app_key, app_secret = p1, p2, p3
            _daidai_delete_env(host, app_key, app_secret, env_id)
        else:
            _ql_request("delete", "/open/envs", [env_id])
    except Exception as e:
        print(f"删除变量时出错: {str(e)}")


def HHTT_ListEnv(osname):
    try:
        panel_type, p1, p2, p3 = _get_panel_config()
        if panel_type == "daidai":
            host, app_key, app_secret = p1, p2, p3
            all_envs = _daidai_list_envs(host, app_key, app_secret, osname)
            return [e for e in all_envs if e.get("name") == osname]
        QLurl, ClientID, ClientSecret = p1, p2, p3
        qltoken = QLtoken(QLurl, ClientID, ClientSecret)
        resp = requests.get(
            f"{QLurl}/open/envs?searchValue={osname}",
            headers={
                "Authorization": f"Bearer {qltoken}",
                "accept": "application/json",
            },
            timeout=10,
            verify=False,
        )
        if resp.status_code != 200:
            raise Exception(f"获取青龙环境变量失败，HTTP 状态码: {resp.status_code}")
        result = resp.json()
        if result.get("code") != 200:
            raise Exception(f"获取青龙环境变量失败，错误信息: {result.get('message')}")
        return result.get("data", [])
    except Exception as e:
        raise Exception(f"面板查询失败: {str(e)}")


def _reply(msg):
    sender.reply(str(msg))


def _is_admin() -> bool:
    """
    判断当前发送者是否为管理员（根据 sender 提供的方法自动适配）。
    """
    for attr in ("isAdmin", "isMaster", "isOwner"):
        fn = getattr(sender, attr, None)
        if callable(fn):
            try:
                if fn():
                    return True
            except Exception:
                continue
    return False


def HHTT_AddOrUpdateLinkEnv(osname: str, value: str):
    """
    抽奖链接环境变量：仅按变量名唯一，存在则更新，不存在则创建。
    """
    panel_type, p1, p2, p3 = _get_panel_config()
    remarks = f"和合天台:当月抽奖链接丨用户:{userid}丨更新时间:{today_time}"

    if panel_type == "daidai":
        host, app_key, app_secret = p1, p2, p3
        env_id = _daidai_find_env(host, app_key, app_secret, osname, keyword="")
        if env_id:
            ok = _daidai_update_env(host, app_key, app_secret, env_id, osname, value, remarks)
        else:
            ok = _daidai_add_env(host, app_key, app_secret, osname, value, remarks)
        if not ok:
            raise Exception("呆呆面板添加/更新抽奖链接变量失败")
        return True

    QLurl, ClientID, ClientSecret = p1, p2, p3
    qltoken = QLtoken(QLurl, ClientID, ClientSecret)
    resp = requests.get(
        f"{QLurl}/open/envs?searchValue={osname}",
        headers={
            "Authorization": f"Bearer {qltoken}",
            "accept": "application/json",
        },
        timeout=10,
        verify=False,
    )
    if resp.status_code != 200:
        raise Exception(f"获取青龙环境变量失败，HTTP 状态码: {resp.status_code}")
    result = resp.json()
    if result.get("code") != 200:
        raise Exception(f"获取青龙环境变量失败，错误信息: {result.get('message', '未知错误')}")

    data_list = result.get("data", []) or []
    exist_id = None
    for env in data_list:
        if env.get("name") == osname:
            exist_id = env.get("id")
            break

    if exist_id:
        _ql_request(
            "put",
            "/open/envs",
            {"value": value, "name": osname, "remarks": remarks, "id": exist_id},
        )
    else:
        _ql_request(
            "post",
            "/open/envs",
            [{"value": value, "name": osname, "remarks": remarks}],
        )
    return True


def get_payment_config():
    wxzsm_cfg = middleware.bucketGet("dd_hhttconfig", "wxzsm")
    use_ma_pay = middleware.bucketGet("dd_hhttconfig", "sdyx") or "false"
    use_ma_pay = str(use_ma_pay).lower() == "true"

    if use_ma_pay:
        ma_pay_config = {
            "switch": middleware.bucketGet("dd_sign_config", "ma_pay_switch") or "false",
            "gateway": middleware.bucketGet("dd_sign_config", "ma_pay_gateway"),
            "pid": middleware.bucketGet("dd_sign_config", "ma_pay_pid"),
            "key": middleware.bucketGet("dd_sign_config", "ma_pay_key"),
            "type": middleware.bucketGet("dd_sign_config", "ma_pay_type"),
            "notify_url": middleware.bucketGet("dd_sign_config", "ma_pay_notify_url"),
            "return_url": middleware.bucketGet("dd_sign_config", "ma_pay_return_url"),
        }

        if (
            ma_pay_config["switch"].lower() != "true"
            or not ma_pay_config["gateway"]
            or not ma_pay_config["pid"]
            or not ma_pay_config["key"]
        ):
            use_ma_pay = False
    else:
        ma_pay_config = None

    return wxzsm_cfg, use_ma_pay, ma_pay_config


def send_qrcode_image(qrcode_url, pay_type: str):
    pay_type_names = {"alipay": "支付宝", "wxpay": "微信", "qqpay": "QQ钱包", "ma": "码支付"}
    pay_type_name = pay_type_names.get(pay_type, pay_type)

    try:
        sender.replyImage(qrcode_url)
        if pay_type in ("qqpay", "ma"):
            sender.reply(
                f"请使用【{pay_type_name}】扫描上方二维码完成支付\n"
                f"QQ支付或部分客户端若图片无法识别，可长按图片选择“识别二维码”！\n"
                f"支付过程中输入'q'可取消支付"
            )
        else:
            sender.reply(
                f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付"
            )
    except Exception:
        if pay_type in ("qqpay", "ma"):
            pay_msg = (
                f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n'
                f'[CQ:image,file={qrcode_url}]'
            )
        else:
            pay_msg = (
                f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n'
                f'[CQ:image,file={qrcode_url}]'
            )
        sender.reply(pay_msg)


def cmd_help():
    _reply(
        "【和合天台青龙管理使用说明】\n"
        "本插件不包含任何内置任务，只负责将和合天台账号变量提交到青龙/呆呆面板，请自行在面板中配合定时脚本使用。\n\n"
        "指令列表：\n"
        "1、和合登录 / 登录和合：\n"
        "   发送「和合登录」，按提示在120秒内发送，每行格式为 账号#密码 或 账号#密码#抽奖链接。\n"
        "   登录成功后发送【和合授权】进入授权界面完成支付。\n\n"
        "2、和合授权 / 授权和合 / 和合授权检测：\n"
        "   无参数：进入待授权账号的支付界面。\n"
        "   带参数：可根据序号或关键字查询授权记录。\n\n"
        "3、和合查询 / 查询和合：\n"
        "   交互式查询：列出账号序号，回复序号查看详情（仅显示备注、账号与到期情况）。\n\n"
        "4、和合删除 / 删除和合：\n"
        "   交互式删除：列出账号，支持删除单个 / 全部 / 已过期账号。\n\n"
        "面板配置说明：\n"
        " - 青龙：面板类型选 qinglong，对接容器填 URL丨ClientID丨ClientSecret\n"
        " - 呆呆：面板类型选 daidai，对接容器填 URL丨app_key丨app_secret（Open API）\n"
        " - 变量名：保存和合天台账号的变量名（建议 HHTT），青龙/呆呆通用。\n"
    )


def _parse_token_lines(text):
    """
    解析用户回复的多行和合天台账号：
    每行格式：账号#密码 或 账号#密码#抽奖链接
    返回 [(account, name, value), ...]
    其中 account=账号（手机号），name=账号本身，value=「账号#密码[#抽奖链接]」（写入面板变量）。
    """
    lines = [ln.strip() for ln in (text or "").splitlines() if ln.strip()]
    result = []
    for line in lines:
        parts = [p.strip() for p in line.split("#") if p.strip()]
        if len(parts) < 2:
            continue
        phone = parts[0]
        pwd = parts[1]
        link = parts[2] if len(parts) >= 3 else ""
        if not phone or not pwd:
            continue
        value = f"{phone}#{pwd}"
        if link:
            value = f"{value}#{link}"
        account = phone
        name = phone
        result.append((account, name, value))
    return result


def handle_login(content):
    try:
        text = (content or "").strip()

        for prefix in ("和合登录", "登录和合", "和合登陆", "登陆和合"):
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                break

        if not text:
            _reply(
                "========和合天台账号登录========\n"
                "1、每行格式：账号#密码 或 账号#密码#抽奖链接\n"
                "2、多账号可多行发送，例：18888888888#123456\n"
                "3、如需单独设置抽奖链接，可在插件登录后于面板中手动补充第三段。\n"
                "===============================\n"
                "请在120秒内发送内容（多行亦可）。输入 q 取消。"
            )
            user_input = sender.listen(120000)
            if user_input in ("q", "Q"):
                _reply("✅ 已取消本次登录操作。")
                return
            if user_input is None or not str(user_input).strip():
                _reply("⏰ 操作超時或未收到有效內容，已取消。")
                return
            text = str(user_input).strip()

        accounts = _parse_token_lines(text)
        if not accounts:
            _reply("❌ 未检测到有效账号，请使用：账号#密码 或 账号#密码#抽奖链接 格式。")
            return

        n = len(accounts)
        data = [{"account": a, "name": nm, "value": v} for a, nm, v in accounts]
        middleware.bucketSet(BUCKET_PENDING, userid, json.dumps(data, ensure_ascii=False))

        price = float(sqje) if sqje else 0.0
        _reply(
            f"✅ 共提交 {n} 个和合天台账号，已为您保存账号信息。\n"
            f"目前账号尚未授权。\n"
            f"当前授权价格为：{price} 元/{sqsj}天（如设置为 0 则直接写入面板）。\n"
            f"请发送【和合授权】进入授权界面。"
        )
        return
    except Exception as e:
        _reply(f"❌ 和合天台账号提交失败：{str(e)}")


def _run_authorization_flow(accounts, months: int):
    try:
        osname = dd_hhtt_osname
        n = len(accounts)
        acc_tuples = [(a["account"], a["name"], a["value"]) for a in accounts]
        months = _safe_int(months, 1)
        if months <= 0:
            months = 1
        expiry_days_per_month = _safe_int(sqsj, 30)
        expiry_str = _expiry_date_str(expiry_days_per_month * months)

        def add_all_to_panel():
            success = 0
            for acc, nm, val in acc_tuples:
                try:
                    HHTT_AddOrUpdateEnv(osname, val, acc, nm, auth_time=expiry_str, user_id=userid)
                    success += 1
                except Exception:
                    pass
            return success

        price = float(sqje) if sqje else 0.0
        wxzsm_cfg, use_ma_pay, ma_pay_config = get_payment_config()
        use_points = wccoin and str(wccoin).isdigit() and int(wccoin) > 0
        total_price = price * n * months
        need_coin_total = int(wccoin) * n * months if use_points else 0

        if price <= 0 and not wxzsm_cfg and not use_ma_pay and not use_points:
            cnt = add_all_to_panel()
            middleware.bucketSet(BUCKET_PENDING, userid, "")
            _reply(
                f"✅ 和合天台账号提交成功\n"
                f"成功写入：{cnt}/{n} 个账号\n已写入面板变量：{osname}"
            )
            return

        msg = [f"=====和合天台授权确认=====\n📊 账号数量：{n} 个\n⏰ 授权时长：{months} 个月"]
        if price > 0:
            msg.append(f"💰 授权金额：{price} 元/账号/月，合计 {total_price} 元")
        if use_points:
            need_coin = int(wccoin)
            usercoin = middleware.bucketGet("dd_sign_points", userid) or "0"
            msg.append(
                f"🎯 积分支付：{need_coin} 积分/账号/月，合计 {need_coin_total} 积分，当前积分：{usercoin}"
            )
        msg.append("------------------")

        options = {}
        idx = 1

        if use_points:
            options[str(idx)] = "points"
            msg.append(f"{idx}️⃣ 使用积分支付")
            idx += 1

        if wxzsm_cfg:
            options[str(idx)] = "wechat"
            msg.append(f"{idx}️⃣ 使用赞赏码扫码支付")
            idx += 1

        if use_ma_pay and ma_pay_config and ma_pay_config.get("gateway"):
            options[str(idx)] = "ma"
            msg.append(f"{idx}️⃣ 使用码支付")
            idx += 1

        if not options:
            cnt = add_all_to_panel()
            middleware.bucketSet(BUCKET_PENDING, userid, "")
            _reply(
                f"✅ 和合天台账号提交成功\n"
                f"成功写入：{cnt}/{n} 个账号\n已写入面板变量：{osname}"
            )
            return

        msg.append("------------------")
        msg.append("回复数字选择支付方式，回复“q”取消本次授权。")

        _reply("\n".join(msg))
        choice = sender.listen(60000)

        if choice in ("q", "Q"):
            _reply("✅ 已取消本次授权操作。")
            return
        if choice is None or str(choice) not in options:
            _reply("⏰ 操作超时或选项无效，已取消授权。")
            return

        pay_type = options[str(choice)]

        if pay_type == "points" and use_points:
            usercoin = middleware.bucketGet("dd_sign_points", userid) or "0"
            if int(usercoin) < need_coin_total:
                _reply(
                    f"❌ 积分不足，无法完成授权。\n当前积分：{usercoin}\n需要积分：{need_coin_total}"
                )
                return
            new_balance = int(usercoin) - need_coin_total
            middleware.bucketSet("dd_sign_points", userid, str(new_balance))
            cnt = add_all_to_panel()
            middleware.bucketSet(BUCKET_PENDING, userid, "")
            _reply(
                f"✅ 积分支付成功，已为 {cnt}/{n} 个账号授权并写入面板。\n剩余积分：{new_balance}"
            )
            return

        if pay_type == "wechat" and wxzsm_cfg:
            send_qrcode_image(wxzsm_cfg, "wxpay")
            _reply(
                "已发送赞赏码二维码，请完成支付后耐心等待管理员核对。\n本次将直接为你提交账号到面板。"
            )
            cnt = add_all_to_panel()
            middleware.bucketSet(BUCKET_PENDING, userid, "")
            _reply(
                f"✅ 和合天台账号提交成功\n成功写入：{cnt}/{n} 个账号\n已写入面板变量：{osname}"
            )
            return

        if pay_type == "ma" and use_ma_pay and ma_pay_config:
            try:
                gateway = ma_pay_config.get("gateway")
                if not gateway:
                    raise Exception("未配置码支付网关地址")

                if gateway.endswith("/"):
                    gateway = gateway[:-1]

                mapi_url = f"{gateway}/mapi.php"
                out_trade_no = f"HHTT{int(time.time())}{userid}"
                money_str = f"{total_price:.2f}" if total_price > 0 else "0.01"

                params = {
                    "pid": ma_pay_config.get("pid"),
                    "type": ma_pay_config.get("type") or "wxpay",
                    "out_trade_no": out_trade_no,
                    "name": f"{senderID}-和合授權-{money_str}",
                    "money": money_str,
                    "param": userid,
                }
                if ma_pay_config.get("notify_url"):
                    params["notify_url"] = ma_pay_config.get("notify_url")
                if ma_pay_config.get("return_url"):
                    params["return_url"] = ma_pay_config.get("return_url")

                sorted_params = sorted(params.items(), key=lambda x: x[0])
                sign_str = "&".join([f"{k}={v}" for k, v in sorted_params if v])
                sign = hashlib.md5(
                    (sign_str + ma_pay_config["key"]).encode()
                ).hexdigest().lower()

                params["sign"] = sign
                params["sign_type"] = "MD5"

                headers = {"Content-Type": "application/x-www-form-urlencoded"}
                response = requests.post(
                    mapi_url, data=params, headers=headers, timeout=10
                )

                if response.status_code != 200:
                    _reply(f"❌ 创建码支付订单失败，HTTP状态码: {response.status_code}")
                    return

                try:
                    result = response.json()
                except Exception:
                    _reply("❌ 创建码支付订单失败，返回数据格式错误")
                    return

                code = result.get("code", 0)
                msg_text = result.get("msg", "未知状态")

                if code != 1:
                    if "没有找到可用支付账号" in msg_text or "没有找到可用的" in msg_text:
                        _reply(f"❌ 码支付暂不可用（{msg_text}）")
                    else:
                        _reply(f"❌ 创建码支付订单失败：{msg_text}")
                    return

                payurl = result.get("payurl", "")
                if not payurl:
                    _reply("❌ 未获取到码支付链接")
                    return

                send_qrcode_image(payurl, "ma")
                _reply(
                    f"=====码支付=====\n"
                    f"商品: 和合账号授权\n"
                    f"账号数量: {n} 个\n"
                    f"金額: {money_str} 元\n"
                    f"授权到期: {expiry_str}\n"
                    f"说明: 请在5分钟内完成支付。\n"
                    f'回复 "q" 可取消本次支付。\n'
                    f"=================="
                )

                for _ in range(60):
                    user_cmd = sender.listen(5000)
                    if user_cmd in ("q", "Q"):
                        _reply("✅ 已取消本次码支付授权。")
                        return

                    check_url = gateway
                    if check_url.endswith("/"):
                        check_url = check_url[:-1]
                    if "/xpay/epay/api.php" not in check_url:
                        check_url = f"{check_url}/xpay/epay/api.php"

                    check_params = {
                        "act": "order",
                        "pid": ma_pay_config["pid"],
                        "key": ma_pay_config["key"],
                        "out_trade_no": out_trade_no,
                    }

                    try:
                        check_resp = requests.get(
                            check_url, params=check_params, timeout=10
                        )
                        check_result = check_resp.json()
                        if (
                            check_result.get("code") == 1
                            and check_result.get("status") == 1
                        ):
                            cnt = add_all_to_panel()
                            middleware.bucketSet(BUCKET_PENDING, userid, "")
                            _reply(
                                f"✅ 码支付成功，已为 {cnt}/{n} 个账号授权并写入面板。"
                            )
                            return
                    except Exception:
                        pass

                _reply("⏰ 码支付订单超时未支付或状态未知，请稍后查询或联系客服。")
                return
            except Exception as e:
                _reply(f"❌ 码支付处理失败：{str(e)}")
                return

        cnt = add_all_to_panel()
        middleware.bucketSet(BUCKET_PENDING, userid, "")
        _reply(
            f"✅ 和合天台账号提交成功\n"
            f"成功写入：{cnt}/{n} 个账号\n已写入面板变量：{osname}"
        )
    except Exception as e:
        _reply(f"❌ 和合天台授權失敗：{str(e)}")


def handle_list():
    try:
        osname = dd_hhtt_osname
        envs = HHTT_ListEnv(osname) or []
        user_envs = []
        for env in envs:
            info = _parse_remarks(env.get("remarks") or "")
            if info.get("用户") == str(userid):
                user_envs.append(env)

        if not user_envs:
            _reply("当前面板中没有您的和合天台环境变量。")
            return

        lines = [f"=====和合天台查询菜单=====\n变量名：{osname}"]
        for i, env in enumerate(user_envs, start=1):
            info = _parse_remarks(env.get("remarks") or "")
            acc = info.get("账户") or "未知账号"
            nm = info.get("和合天台") or info.get("name") or ""
            exp = info.get("授权时间") or ""
            status = "未授权"
            if exp:
                status = "已过期" if _is_expired(exp) else "已授权"
            title = (nm or acc).strip()
            lines.append(f"{i}、{title} | 账号:{acc} | {status}{f'(到期:{exp})' if exp else ''}")

        lines.append("------------------")
        lines.append('回复序号查看该账号详情；回复 "q" 退出。')
        _reply("\n".join(lines))

        choice = sender.listen(120000)
        if choice in ("q", "Q"):
            _reply("✅ 已退出查询。")
            return
        if choice is None:
            _reply("⏰ 操作超时，已退出查询。")
            return
        c = str(choice).strip()
        if not c.isdigit():
            _reply("❌ 输入无效，请重新发送【和合查询】。")
            return
        idx = int(c)
        if idx < 1 or idx > len(user_envs):
            _reply("❌ 序号超出范围，请重新发送【和合查询】。")
            return
        env = user_envs[idx - 1]
        info = _parse_remarks(env.get("remarks") or "")
        acc = info.get("账户") or "未知账号"
        nm = info.get("和合天台") or info.get("name") or ""
        exp = info.get("授权时间") or ""
        status = "未授权" if not exp else ("已过期" if _is_expired(exp) else "已授权")

        _reply(
            "========账号详情========\n"
            f"序号: {idx}\n"
            f"备注名: {nm}\n"
            f"账号: {acc}\n"
            f"状态: {status}{f' (到期:{exp})' if exp else ''}\n"
            "======================"
        )
    except Exception as e:
        _reply(f"❌ 查询面板环境变量失败：{str(e)}")


def handle_delete(content):
    try:
        osname = dd_hhtt_osname
        envs = HHTT_ListEnv(osname) or []
        user_envs = []
        for env in envs:
            info = _parse_remarks(env.get("remarks") or "")
            if info.get("用户") == str(userid):
                user_envs.append(env)

        if not user_envs:
            _reply("您暂无可删除的和合天台环境变量。")
            return

        lines = ["=====和合天台删除菜单====="]
        lines.append("0、一键删除所有账号")
        lines.append("9、一键删除所有过期账号")
        lines.append("------------------")

        expired_idxs = []
        for i, env in enumerate(user_envs, start=1):
            info = _parse_remarks(env.get("remarks") or "")
            acc = info.get("账户") or "未知账号"
            nm = info.get("和合天台") or info.get("name") or acc
            exp = info.get("授权时间") or ""
            is_exp = _is_expired(exp) if exp else False
            if exp and is_exp:
                expired_idxs.append(i)
            status = "已过期" if (exp and is_exp) else ("已授权" if exp else "未授权")
            lines.append(f"{i}、{nm} | 账号:{acc} | {status}{f'(到期:{exp})' if exp else ''}")

        lines.append("------------------")
        lines.append('回复序号删除单个账号；回复 0 删除全部；回复 9 删除过期；回复 "q" 取消。')
        _reply("\n".join(lines))

        choice = sender.listen(120000)
        if choice in ("q", "Q"):
            _reply("✅ 已取消删除操作。")
            return
        if choice is None:
            _reply("⏰ 操作超时，已取消删除。")
            return
        c = str(choice).strip()

        target_envs = []
        if c == "0":
            target_envs = user_envs
        elif c == "9":
            if not expired_idxs:
                _reply("✅ 当前没有检测到过期账号可删除。")
                return
            target_envs = [user_envs[i - 1] for i in expired_idxs if 1 <= i <= len(user_envs)]
        elif c.isdigit():
            idx = int(c)
            if idx < 1 or idx > len(user_envs):
                _reply("❌ 序号超出范围，请重新发送【和合删除】。")
                return
            target_envs = [user_envs[idx - 1]]
        else:
            _reply("❌ 输入无效，请重新发送【和合删除】。")
            return

        preview_lines = ["=====删除确认====="]
        preview_lines.append(f"将删除：{len(target_envs)} 条账号")
        preview_lines.append("------------------")
        for i, env in enumerate(target_envs, start=1):
            info = _parse_remarks(env.get("remarks") or "")
            acc = info.get("账户") or "未知账号"
            nm = info.get("和合天台") or info.get("name") or acc
            exp = info.get("授权时间") or ""
            preview_lines.append(f"{i}、{nm} | 账号:{acc}{f' | 到期:{exp}' if exp else ''}")
        preview_lines.append("------------------")
        preview_lines.append('回复 "y" 确认删除；回复 "q" 取消。')
        _reply("\n".join(preview_lines))

        confirm = sender.listen(60000)
        if confirm in ("q", "Q"):
            _reply("✅ 已取消删除操作。")
            return
        if confirm is None:
            _reply("⏰ 操作超时，已取消删除。")
            return
        if str(confirm).strip().lower() != "y":
            _reply("✅ 未确认删除，已取消。")
            return

        ok = 0
        for env in target_envs:
            try:
                HHTT_DeleteEnv(env.get("id"))
                ok += 1
            except Exception:
                pass
        _reply(f"✅ 删除完成：{ok}/{len(target_envs)} 条。")
    except Exception as e:
        _reply(f"❌ 删除失败：{str(e)}")


def handle_auth(content):
    try:
        args = (content or "").strip().split()
        if len(args) < 2:
            pending_raw = middleware.bucketGet(BUCKET_PENDING, userid) or ""
            if not pending_raw or not pending_raw.strip():
                _reply("您暂无待授权账号，请先发送【和合登录】提交账号。")
                return
            try:
                accounts = json.loads(pending_raw)
            except Exception:
                middleware.bucketSet(BUCKET_PENDING, userid, "")
                _reply("待授权数据已失效，请重新发送【和合登录】提交账号。")
                return
            if not accounts:
                _reply("您暂无待授权账号，请先发送【和合登录】提交账号。")
                return

            osname = dd_hhtt_osname
            price = float(sqje) if sqje else 0.0
            expiry_days = _safe_int(sqsj, 30)
            auth_map = _get_user_authorized_accounts_map(osname)

            lines = []
            lines.append("=====和合天台授权菜单=====")
            lines.append("0、一键授权所有账号")
            lines.append("9、一键授权所有过期账号")
            lines.append("------------------")

            idx_to_account = {}
            expired_idxs = []

            for i, a in enumerate(accounts, start=1):
                acc = str(a.get("account") or f"账号{i}")
                nm = str(a.get("name") or acc)
                exp = auth_map.get(acc, "")
                expired = _is_expired(exp) if exp else True
                status = f"已授权(到期:{exp})" if exp else "未授权"
                if exp and expired:
                    status = f"已过期(到期:{exp})"
                if expired:
                    expired_idxs.append(i)
                idx_to_account[str(i)] = acc
                lines.append(f"{i}、{nm} | 账号:{acc} | {status}")

            lines.append("------------------")
            lines.append(f"当前授权价格：{price} 元/{expiry_days}天（按选择账号数量与月数计费）")
            lines.append('回复序号授权单个账号；回复 0 授权全部；回复 9 授权过期；回复 "q" 取消。')
            _reply("\n".join(lines))

            choice = sender.listen(120000)
            if choice in ("q", "Q"):
                _reply("✅ 已取消本次授权操作。")
                return
            if choice is None:
                _reply("⏰ 操作超时，已取消授权。")
                return

            c = str(choice).strip()
            selected = []
            if c == "0":
                selected = accounts
            elif c == "9":
                if not expired_idxs:
                    _reply("✅ 当前没有检测到过期账号。")
                    return
                selected = [accounts[i - 1] for i in expired_idxs if 1 <= i <= len(accounts)]
            elif c in idx_to_account:
                i = int(c)
                selected = [accounts[i - 1]]
            else:
                _reply("❌ 输入无效，请重新发送【和合授权】。")
                return

            _reply("请输入授权月数（整数，例如 1/3/6），回复 q 取消。")
            m = sender.listen(60000)
            if m in ("q", "Q"):
                _reply("✅ 已取消本次授权操作。")
                return
            if m is None or not str(m).strip().isdigit():
                _reply("❌ 月数输入无效，已取消。")
                return
            months = int(str(m).strip())
            if months <= 0:
                _reply("❌ 月数必须大于0，已取消。")
                return

            _run_authorization_flow(selected, months)
            return

        keyword = " ".join(args[1:]).strip()
        osname = dd_hhtt_osname
        auth_map = _get_user_authorized_accounts_map(osname)

        if not auth_map:
            _reply("您当前没有已授权记录，可发送【和合登录】后再授权。")
            return

        items = list(auth_map.items())
        if keyword.isdigit():
            idx = int(keyword)
            if idx < 1 or idx > len(items):
                _reply("❌ 序号超出范围，请重新发送【和合授权】。")
                return
            acc, exp = items[idx - 1]
            status = "已过期" if _is_expired(exp) else "已授权"
            _reply(f"账号：{acc}\n状态：{status}\n到期：{exp or '未知'}")
            return

        matched = [(acc, exp) for acc, exp in items if keyword in str(acc)]
        if not matched:
            _reply("未匹配到账号，请重新发送【和合授权】。")
            return
        if len(matched) == 1:
            acc, exp = matched[0]
            status = "已过期" if _is_expired(exp) else "已授权"
            _reply(f"账号：{acc}\n状态：{status}\n到期：{exp or '未知'}")
            return
        lines = ["=====授权记录匹配结果====="]
        for i, (acc, exp) in enumerate(matched, start=1):
            status = "已过期" if _is_expired(exp) else "已授权"
            lines.append(f"{i}、{acc} | {status}{f'(到期:{exp})' if exp else ''}")
        lines.append('回复序号查看；回复 "q" 退出。')
        _reply("\n".join(lines))
        ch = sender.listen(60000)
        if ch in ("q", "Q"):
            _reply("✅ 已退出。")
            return
        if ch is None or not str(ch).strip().isdigit():
            _reply("❌ 输入无效。")
            return
        idx = int(str(ch).strip())
        if idx < 1 or idx > len(matched):
            _reply("❌ 序号超出范围。")
            return
        acc, exp = matched[idx - 1]
        status = "已过期" if _is_expired(exp) else "已授权"
        _reply(f"账号：{acc}\n状态：{status}\n到期：{exp or '未知'}")
    except Exception as e:
        _reply(f"❌ 授权检测失败：{str(e)}")


def handle_tiantai_link(content: str):
    """
    管理員指令：天台链接
    流程：
    1. 仅允许管理员使用；
    2. 提示在 60 秒内发送当月抽奖链接（可直接跟在指令后，或下一条消息单发）；
    3. 自动写入 / 更新面板中的抽奖链接变量（变量名由配置 link_osname 控制，默认为 HHTT_LINK）。
    """
    if not _is_admin():
        _reply("❌ 此指令仅限管理员使用。")
        return

    text = (content or "").strip()
    for prefix in ("天台链接",):
        if text.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    if not text:
        _reply(
            "====== 和合天台抽奖链接设置 ======\n"
            "请在 60 秒内发送本月抽奖链接：\n"
            "例如：https://act.tmlyun.com/lottery/?q=********\n"
            "回复 q 取消本次设置。"
        )
        user_input = sender.listen(60000)
        if user_input in ("q", "Q"):
            _reply("✅ 已取消本次抽奖链接设置。")
            return
        if user_input is None or not str(user_input).strip():
            _reply("⏰ 操作超时或未收到有效内容，已取消。")
            return
        text = str(user_input).strip()

    link = text.strip()
    if not link.startswith("http"):
        _reply("❌ 检测到的内容不像是有效链接，请确认是否已包含 https:// 前缀。")
        return

    osname = dd_hhtt_link_osname or "HHTT_LINK"
    try:
        HHTT_AddOrUpdateLinkEnv(osname, link)
        _reply(
            f"✅ 已成功将当月抽奖链接提交到面板。\n"
            f"变量名：{osname}\n"
            f"如面板中原有同名变量，已自动更新为最新链接。"
        )
    except Exception as e:
        _reply(f"❌ 提交抽奖链接到面板失败：{str(e)}")


def main():
    raw_text = sender.getMessage()
    text = (raw_text or "").strip()

    if re.match(r"^和合(教程|帮助|使用说明)$", text):
        cmd_help()
    elif re.match(r"^(和合登录|登录和合|和合登陆|登陆和合)", text):
        handle_login(text)
    elif re.match(r"^(和合查询|查询和合)$", text):
        handle_list()
    elif re.match(r"^(和合删除|删除和合)(\s|$)", text):
        handle_delete(text)
    elif re.match(r"^(和合授权|授权和合|和合授权检测)(\s|$)", text):
        handle_auth(text)
    elif re.match(r"^(天台链接)(\s|$)", text):
        handle_tiantai_link(text)
    else:
        cmd_help()


if __name__ == "__main__":
    main()
