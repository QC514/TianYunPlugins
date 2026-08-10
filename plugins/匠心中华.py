# [rule: ^匠心登录$|^登录匠心$|^匠心管理$|^管理匠心$|^匠心查询$|^查询匠心$|^匠心物流$|^物流匠心$|^匠心兑换$|^兑换匠心$|^匠心批量兑换$|^匠心批量地址$|^匠心授权$|^匠心教程$|^匠心清理$|^匠心上传$|^匠心地址$|^匠心注销$|^匠心CK$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [title: 匠心中华]
# [icon: https://i.miji.bid/2025/04/11/7e8ab0b1dcf0e9a0a4ecbe3f4c9ec8b4.png]
# [open_source: false]
# [class: 工具类]
# [version: 1.3.7]
# [price:38.88]
# [admin: false]
# [author: huawei]
# [service: 1603960061]
# [description: 介绍：匠心插件，支持扫码登录、CK批量登录、查询、兑换、批量兑换、物流、地址管理与管理<br>指令：匠心登录、匠心CK、匠心管理、匠心查询、匠心兑换、匠心批量兑换、匠心物流、匠心地址、匠心批量地址、匠心注销、匠心授权、匠心清理、匠心教程、匠心上传<br>更新日志：1.3.7 新增「匠心CK」指令，支持批量CK登录，格式：备注#ck]
# [param: {"required":true,"key":"G_JXZH.panel_type","bool":false,"placeholder":"qinglong 或 daidai","name":"面板类型","desc":"对接面板：qinglong=青龙，daidai=呆呆（DaiDaiPanel），不填默认为青龙"}]
# [param: {"required":true,"key":"G_JXZH.panel_config","bool":false,"placeholder":"青龙: URL | ClientID | ClientSecret; 呆呆: URL | app_key | app_secret","name":"设置对接容器","desc":"青龙用 | 分割3项；呆呆为 Open API 的 host、app_key、app_secret（也支持中文丨分隔）"}]
# [param: {"required":true,"key":"G_JXZH.ql_envname","bool":false,"placeholder":"必填项,例:G_JXZH_TOKEN","name":"变量名","desc":"面板内匠心账号使用的变量名（青龙/呆呆通用），默认 G_JXZH_TOKEN"}]
# [param: {"required":false,"key":"dd_sign_config.zsm","bool":false,"placeholder":"http://127.0.0.1/赞赏码.png","name":"赞赏码链接","desc":"你的机器人赞赏码链接（用于微信收款码方式）"}]
# [param: {"required":true,"key":"G_JXZH.price","bool":false,"placeholder":"例:6.6,不填为0元","name":"授权价格","desc":"授权价格(单位:元)，为0则免费授权"}]
# [param: {"required":false,"key":"G_JXZH.auth_days","bool":false,"placeholder":"例:30,不填为30天","name":"授权天数","desc":"授权天数，默认30天（按「月」倍数叠加：选N月则延长 N×本天数）"}]
# [param: {"required":false,"key":"G_JXZH.coin","bool":false,"placeholder":"例:100,不填为关闭积分支付","name":"积分支付","desc":"授权一个月需要多少积分（只能为整数）"}]
# [param: {"required":true,"key":"G_JXZH.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统，开启后将使用卡密系统配置的码支付"}]
# [param: {"required":false,"key":"G_JXZH.panel_group","bool":false,"placeholder":"例:匠心","name":"对接面板分组","desc":"可选。仅呆呆面板生效，新增/更新变量时写入 group；留空不处理"}]
# [param: {"required":false,"key":"G_JXZH.points_limit","bool":false,"placeholder":"例:10,不填为10条","name":"积分明细条数","desc":"查询时显示的积分明细条数，默认为10条"}]

import re
import json
import time
import uuid
import hashlib
import requests
import urllib.parse
import middleware
from datetime import datetime, timedelta
from decimal import Decimal

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

BUCKET_USER = 'G_JXZH_user'
BUCKET_TOKEN = 'G_JXZH_token'
BUCKET_AUTH = 'G_JXZH_auth'
BUCKET_CONFIG = 'G_JXZH'
DEFAULT_ENV_NAME = 'G_JXZH_TOKEN'

DEFAULT_UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541721) XWEB/18787'
APP_UA = 'quwa/1.6.1 (iPhone; iOS 26.3.1; Scale/3.00)'
USER_CENTER_URL = 'https://api.quwayouxuan.com/dmluser/center.do'
THIRD_LOGIN_URL = 'https://api.quwayouxuan.com/login/third.do'
TASK_LIST_URL = 'https://api.quwayouxuan.com/task/task/taskList.do'
POINTS_LIST_URL = 'https://api.quwayouxuan.com/points/api/getpointslist.do'
ORDER_LIST_URL = 'https://api.quwayouxuan.com/selfsupport/order/list.do'
PRODUCT_LIST_URL = 'https://api.quwayouxuan.com/selfsupport/product/getProducts.do'
PRODUCT_DETAIL_URL = 'https://api.quwayouxuan.com/selfsupport/product/getProductDetail.do'
ORDER_CREATE_URL = 'https://api.quwayouxuan.com/selfsupport/order/createOrder.do'
ADDRESS_LIST_URL = 'https://api.quwayouxuan.com/selfsupport/address/list.do'
ADDRESS_DEL_URL = 'https://api.quwayouxuan.com/selfsupport/address/del.do'
ADDRESS_CREATE_URL = 'https://api.quwayouxuan.com/selfsupport/address/create.do'
ADDRESS_SEARCH_URL = 'https://api.quwayouxuan.com/address/searchAddress.do'
ADDRESS_AREA_CODE_URL = 'https://api.quwayouxuan.com/address/getAreaCode.do'
LOGOFF_URL = 'https://api.quwayouxuan.com/login/logoff.do'
ADDRESS_AREA_URL = 'https://api.quwayouxuan.com/address/getArea.do'
PROJECT_CONFIG = {'appid': 'wx4adbe69a9114c474', 'bundleid': '(null)'}
QR_EXPIRE_SECONDS = 180
LOGISTICS_ORDER_LIMIT = 3
EXCHANGE_ORDER_LIMIT = 5
APP_HEADERS = {
    'User-Agent': APP_UA,
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Language': 'zh-Hans-CN;q=1, zh-Hant-CN;q=0.9, en-CN;q=0.8',
}


def parse_bool(value, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value in (None, ''):
        return default
    return str(value).strip().lower() == 'true'


def parse_decimal(value, default: str = '0') -> Decimal:
    try:
        return Decimal(str(value).strip() or default)
    except Exception:
        return Decimal(default)


def parse_int(value, default: int) -> int:
    try:
        return int(str(value).strip() or str(default))
    except Exception:
        return default


def normalize_text(value):
    if value is None:
        return ''
    return str(value)


def dedupe_phones(phones: list) -> list:
    return list(dict.fromkeys([str(phone).strip() for phone in phones if str(phone).strip()]))


def get_user_phones(user_id=None) -> list:
    user_id = user_id or userid
    data = middleware.bucketGet(BUCKET_USER, user_id) or ''
    return dedupe_phones(data.split(','))


def save_user_phones(phones: list, user_id=None):
    user_id = user_id or userid
    values = dedupe_phones(phones)
    if values:
        middleware.bucketSet(BUCKET_USER, user_id, ','.join(values))
        return
    middleware.bucketDel(BUCKET_USER, user_id)


def add_account(phone: str, user_id=None):
    phones = get_user_phones(user_id)
    if phone not in phones:
        phones.append(phone)
        save_user_phones(phones, user_id)


def parse_token_parts(data: str) -> dict:
    if not data:
        return {}
    parts = str(data).split('#')
    if len(parts) < 2:
        return {}
    return {
        'userId': parts[0],
        'token': parts[1],
        'refreshToken': parts[2] if len(parts) > 2 else '',
    }


def save_token(phone: str, userId: str, token: str, refreshToken: str = ''):
    middleware.bucketSet(BUCKET_TOKEN, phone, f'{userId}#{token}#{refreshToken}')


def get_token(phone: str) -> dict:
    data = middleware.bucketGet(BUCKET_TOKEN, phone) or ''
    return parse_token_parts(data)


def get_auth(phone: str) -> str:
    return str(middleware.bucketGet(BUCKET_AUTH, phone) or '')


def save_auth(phone: str, expire_date: str):
    middleware.bucketSet(BUCKET_AUTH, phone, expire_date)


def is_authorized(phone: str) -> bool:
    expire = get_auth(phone)
    if not expire:
        return False
    try:
        return datetime.strptime(expire, '%Y-%m-%d').date() >= datetime.now().date()
    except Exception:
        return False


def del_account(phone: str, user_id=None, panel_config: str = '', panel_envname: str = ''):
    user_id = user_id or userid
    phones = get_user_phones(user_id)
    if phone in phones:
        phones.remove(phone)
        save_user_phones(phones, user_id)
    env_id = allenvs(osname=panel_envname or DEFAULT_ENV_NAME, account=str(phone))
    if env_id:
        delenvs(id=env_id)
    middleware.bucketDel(BUCKET_TOKEN, phone)
    middleware.bucketDel(BUCKET_AUTH, phone)


def get_config() -> dict:
    auth_days = parse_int(middleware.bucketGet(BUCKET_CONFIG, 'auth_days') or '30', 30)
    points_limit = parse_int(middleware.bucketGet(BUCKET_CONFIG, 'points_limit') or '10', 10)
    return {
        'panel_type': (middleware.bucketGet(BUCKET_CONFIG, 'panel_type') or 'qinglong').strip(),
        'panel_config': (middleware.bucketGet(BUCKET_CONFIG, 'panel_config') or '').strip(),
        'panel_group': (middleware.bucketGet(BUCKET_CONFIG, 'panel_group') or '').strip(),
        'ql_envname': (middleware.bucketGet(BUCKET_CONFIG, 'ql_envname') or DEFAULT_ENV_NAME).strip() or DEFAULT_ENV_NAME,
        'price': parse_decimal(middleware.bucketGet(BUCKET_CONFIG, 'price') or '0', '0'),
        'auth_days': auth_days if auth_days > 0 else 30,
        'coin': parse_int(middleware.bucketGet(BUCKET_CONFIG, 'coin') or '0', 0),
        'points_limit': points_limit if points_limit > 0 else 10,
        'use_ma_pay': parse_bool(middleware.bucketGet(BUCKET_CONFIG, 'use_ma_pay') or 'false', False),
        'zsm': (middleware.bucketGet('dd_sign_config', 'zsm') or '').strip(),
        'ma_pay_switch': parse_bool(middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false', False),
        'ma_pay_gateway': (middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '').strip(),
        'ma_pay_pid': (middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '').strip(),
        'ma_pay_key': (middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '').strip(),
        'ma_pay_type': (middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay').strip(),
        'ma_pay_notify_url': (middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or '').strip(),
        'ma_pay_return_url': (middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or '').strip(),
    }


CONFIG = get_config()
uservalue = ','.join(get_user_phones(userid))

# ==================== 匠心API配置 ====================


def build_signed_payload(extra=None, use_app_style: bool = False, sign_mode: str = 'encoded'):
    if use_app_style:
        payload = {
            'appInfo': '1.6.1',
            'current_time': int(time.time() * 1000),
            'deviceabout': 'system:26.3.1,platform:iOS',
            'idfa': '00000000-0000-0000-0000-000000000000',
            'os': 'ios',
        }
    else:
        payload = {
            'current_time': int(time.time() * 1000),
            'os': 'miniProgram',
            'deviceabout': 'miniProgram',
            'version': '1.3.01',
            'miniprogram_os': 'Windows',
        }
    for key, value in (extra or {}).items():
        if value is not None:
            payload[key] = value
    joined = ''.join(
        f'{key}={normalize_text(payload[key])}'
        for key in sorted(payload)
        if payload[key] is not None and str(payload[key]) != 'signature'
    ) + 'superjing'
    sign_mode = str(sign_mode or 'encoded').strip().lower()
    if sign_mode == 'raw':
        sign_source = joined
    else:
        joined = re.sub(r'\s+', '', joined)
        encoded = urllib.parse.quote(joined, safe='-_.')
        encoded = encoded.replace('~', '%7E')
        for ch in "!'()*":
            encoded = encoded.replace(ch, '%' + format(ord(ch), '02X'))
        sign_source = encoded
    payload['key'] = hashlib.sha1(sign_source.encode('utf-8')).hexdigest()
    return payload


def get_base_headers():
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541411) XWEB/16965',
        'xweb_xhr': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wxddaa0832e6acc5f1/123/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }


def get_app_base_headers():
    return APP_HEADERS.copy()


def is_signature_error_result(result) -> bool:
    if not isinstance(result, dict):
        return False
    code = str(result.get('code') or '').strip()
    if code == '10002':
        return True
    message = str(result.get('message') or result.get('msg') or '').strip().lower()
    if not message:
        return False
    keywords = (
        '校验',
        '验签',
        '签名',
        'signature',
        'invalid sign',
        'sign error',
        'invalid key',
    )
    return any(keyword in message for keyword in keywords)


def signed_post_with_fallback(url, headers, extra=None, use_app_style: bool = False, timeout=10):
    payload = build_signed_payload(extra, use_app_style=use_app_style, sign_mode='encoded')
    response = requests.post(url, headers=headers, data=payload, timeout=timeout)
    result = load_json_response(response)
    if not is_signature_error_result(result):
        return result

    fallback_payload = build_signed_payload(extra, use_app_style=use_app_style, sign_mode='raw')
    fallback_response = requests.post(url, headers=headers, data=fallback_payload, timeout=timeout)
    fallback_result = load_json_response(fallback_response)
    if fallback_result.get('code') == 1:
        print(f"签名兼容重试成功: {url}")
        return fallback_result
    return fallback_result if fallback_result else result


def load_json_response(response):
    raw = getattr(response, 'content', b'') or b''
    if not raw:
        return {}
    encodings = ['utf-8', 'utf-8-sig']
    apparent = getattr(response, 'apparent_encoding', None)
    declared = getattr(response, 'encoding', None)
    if apparent:
        encodings.append(apparent)
    if declared and str(declared).lower() not in ('iso-8859-1', 'latin-1', 'ascii'):
        encodings.append(declared)
    encodings.extend(['gb18030', 'latin-1'])

    tried = set()
    for encoding in encodings:
        encoding = str(encoding or '').strip()
        if not encoding:
            continue
        lowered = encoding.lower()
        if lowered in tried:
            continue
        tried.add(lowered)
        try:
            return json.loads(raw.decode(encoding))
        except (LookupError, UnicodeDecodeError, json.JSONDecodeError):
            continue

    try:
        return response.json()
    except Exception:
        return {}


def get_user_info(token):
    try:
        result = signed_post_with_fallback(
            USER_CENTER_URL,
            headers=get_app_base_headers(),
            extra={'token': token},
            use_app_style=True,
            timeout=10,
        )
        if result.get('code') != 1 or not result.get('data'):
            return None
        user_info = result['data'].get('user_info', {})
        return {
            'id': user_info.get('id'),
            'username': user_info.get('username'),
            'mobile': user_info.get('mobile'),
            'level_name': user_info.get('level_name'),
            'store_name': user_info.get('store_name'),
            'points': user_info.get('points', '0'),
            'rice': user_info.get('rice', '0'),
        }
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return None


def get_task_list(token):
    try:
        result = signed_post_with_fallback(
            TASK_LIST_URL,
            headers=get_app_base_headers(),
            extra={'token': token, 'source': '4'},
            use_app_style=True,
            timeout=10,
        )
        if result.get('code') == 1 and result.get('data'):
            return result['data']
        return None
    except Exception as e:
        print(f"获取任务列表失败: {e}")
        return None


def get_task_userinfo(token):
    task_data = get_task_list(token)
    if not task_data:
        return None
    userinfo = task_data.get('userinfo', {})
    if not isinstance(userinfo, dict):
        return None
    return {
        'username': userinfo.get('username', ''),
        'level_name': userinfo.get('level_name', ''),
        'points': userinfo.get('points', '0'),
        'task_rice': userinfo.get('task_rice', '0'),
    }


def get_points_list(token, page=1):
    try:
        result = signed_post_with_fallback(
            POINTS_LIST_URL,
            headers=get_app_base_headers(),
            extra={
                'sj_h5': '1',
                'token': token,
                'page': str(page),
                'date': '',
                'type': '1',
                'points_type': '0',
                'version': '2.0.0',
                'os': 'h5',
            },
            use_app_style=True,
            timeout=10,
        )
        if result.get('code') == 1 and result.get('data'):
            return result['data']
        return None
    except Exception as e:
        print(f"获取积分明细失败: {e}")
        return None


def get_order_list(token, status='3', page=1, keywords=''):
    try:
        result = signed_post_with_fallback(
            ORDER_LIST_URL,
            headers=get_base_headers(),
            extra={
                'token': token,
                'status': str(status),
                'page': str(page),
                'keywords': keywords or '',
            },
            use_app_style=False,
            timeout=10,
        )
        code = result.get('code')
        if code == 1 and isinstance(result.get('data'), list):
            return {
                'ok': True,
                'code': code,
                'message': str(result.get('message') or ''),
                'data': result.get('data') or [],
            }
        message = str(result.get('message') or '').strip()
        if code == 10002:
            message = '物流接口校验失败'
        return {
            'ok': False,
            'code': code,
            'message': message or '物流接口返回异常',
            'data': [],
        }
    except Exception as e:
        print(f"获取物流订单失败: {e}")
        return {
            'ok': False,
            'code': -1,
            'message': f'获取物流订单失败: {e}',
            'data': [],
        }


def wx_exchange_code_for_token(code):
    params = {
        'appid': PROJECT_CONFIG['appid'],
        'secret': 'b6b2767963bec470ec2505c8da5eec47',
        'code': code,
        'grant_type': 'authorization_code',
    }
    try:
        resp = requests.get('https://api.weixin.qq.com/sns/oauth2/access_token', params=params, timeout=10)
        result = load_json_response(resp)
        if 'access_token' in result:
            return {
                'access_token': result['access_token'],
                'refresh_token': result.get('refresh_token', ''),
                'openid': result['openid'],
                'unionid': result.get('unionid', ''),
            }
        return None
    except Exception as e:
        print(f"微信换取token失败: {e}")
        return None


def wx_get_userinfo(access_token, openid):
    try:
        resp = requests.get(
            'https://api.weixin.qq.com/sns/userinfo',
            params={'access_token': access_token, 'openid': openid},
            timeout=10,
        )
        result = load_json_response(resp)
        if 'openid' in result:
            return {'nickname': result.get('nickname', ''), 'picurl': result.get('headimgurl', '')}
        return None
    except Exception as e:
        print(f"获取微信用户信息失败: {e}")
        return None


def exchange_token(wx_code):
    if not wx_code:
        print("exchange_token: wx_code 为空")
        sender.reply('❌ 扫码异常：未获取到授权码')
        return None
    try:
        result = signed_post_with_fallback(
            THIRD_LOGIN_URL,
            headers=get_app_base_headers(),
            extra={
                'code': wx_code,
            },
            use_app_style=True,
            timeout=10,
        )
        if result.get('code') == 1 and result.get('data'):
            data = result.get('data', {})
            return {
                'token': data.get('token'),
                'userId': data.get('userID') or data.get('userId'),
                'username': data.get('username'),
                'mobile': data.get('mobile'),
                'level_name': data.get('level_name'),
                'store_name': data.get('store_name'),
                'unionid': data.get('unionid', ''),
                'nickname': data.get('nickname', ''),
                'picurl': data.get('picurl', ''),
                'raw': data,
            }
        msg = result.get('message') or result.get('msg') or ''
        rcode = result.get('code', '')
        print(f"换取token失败: code={rcode}, message={msg}")
        sender.reply(f'❌ 平台登录失败: {msg}(code={rcode})')
        return None
    except Exception as e:
        print(f"换取token异常: {e}")
        sender.reply(f'❌ 换取Token异常: {e}')
        return None


def get_qr_code():
    url = 'https://open.weixin.qq.com/connect/app/qrconnect'
    params = {
        'appid': PROJECT_CONFIG['appid'],
        'bundleid': PROJECT_CONFIG['bundleid'],
        'scope': 'snsapi_userinfo',
        'state': 'wx_oauth_authorization_state',
        'pass_ticket': str(uuid.uuid4()),
    }
    headers = {'User-Agent': DEFAULT_UA, 'Referer': 'https://open.weixin.qq.com/'}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
        match = re.search(r'uuid\: *"(\w+)"', response.text)
        if not match:
            return None
        qr_uuid = match.group(1)
        return {'uuid': qr_uuid, 'img_url': f'https://open.weixin.qq.com/connect/qrcode/{qr_uuid}'}
    except Exception as e:
        print(f"获取二维码失败: {e}")
        return None


def check_qr_status(qr_uuid, qr_created_at=None):
    if qr_created_at and time.time() - qr_created_at >= QR_EXPIRE_SECONDS:
        return {'code': 2, 'msg': '二维码已过期'}
    url = 'https://lp.open.weixin.qq.com/connect/l/qrconnect'
    params = {'uuid': qr_uuid, 'f': 'url', '_': int(time.time() * 1000)}
    headers = {'User-Agent': DEFAULT_UA, 'Referer': 'https://open.weixin.qq.com/'}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=(10, 30))
        if response.status_code != 200:
            return None
        if not response.encoding or response.encoding.lower() in ('iso-8859-1', 'latin-1'):
            response.encoding = response.apparent_encoding or 'utf-8'
        wx_code_match = re.search(r'wx_errcode=(\d+)', response.text)
        if not wx_code_match:
            return {'code': 1, 'msg': '未知状态'}
        wx_code = int(wx_code_match.group(1))
        if wx_code == 405:
            code_match = re.search(r'\?code=(\w+)', response.text)
            name_match = re.search(r"wx_nickname='([^']*)'", response.text)
            nick_raw = name_match.group(1) if name_match else None
            return {
                'code': 0,
                'data': {
                    'code': code_match.group(1) if code_match else None,
                    'nickname': decode_wechat_nickname(nick_raw) if nick_raw else None,
                },
                'msg': '扫码成功',
            }
        if wx_code == 404:
            return {'code': 1, 'msg': '等待扫码'}
        return {'code': 1, 'msg': '未知状态'}
    except requests.exceptions.ReadTimeout:
        return {'code': 1, 'msg': '等待扫码'}
    except Exception as e:
        print(f"检查扫码状态异常: {e}")
        return None


# ==================== 通用工具函数 ====================

def format_message(title, content, status='info'):
    status_icons = {'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'error': '❌', 'loading': '⏳'}
    return f"{status_icons.get(status, 'ℹ️')} {title}\n{content}"


def mask_phone(phone):
    if len(phone) >= 11:
        return phone[:3] + '*' * 4 + phone[7:]
    return phone


def parse_accounts(account_data):
    return dedupe_phones(str(account_data or '').split(','))


def parse_selection(choice, max_index: int) -> list:
    choice = str(choice or '').strip()
    if not choice:
        raise ValueError('请输入序号')
    if choice in ('0', '9999'):
        return [choice]

    values = []
    seen = set()
    parts = [part.strip() for part in choice.split(',')]
    if not parts or any(not part for part in parts):
        raise ValueError('格式错误，支持 1,3,5 或 1-5')

    for part in parts:
        if '-' in part:
            start_end = [item.strip() for item in part.split('-')]
            if len(start_end) != 2 or not start_end[0] or not start_end[1]:
                raise ValueError('区间格式错误，支持 1-5')
            try:
                start = int(start_end[0])
                end = int(start_end[1])
            except ValueError:
                raise ValueError('区间必须是数字')
            if start > end:
                raise ValueError('区间起始值不能大于结束值')
            if start < 1 or end > max_index:
                raise ValueError(f'序号超出范围，请输入 1-{max_index}')
            for index in range(start, end + 1):
                if index not in seen:
                    seen.add(index)
                    values.append(index)
            continue

        try:
            index = int(part)
        except ValueError:
            raise ValueError('序号必须是数字')
        if index < 1 or index > max_index:
            raise ValueError(f'序号超出范围，请输入 1-{max_index}')
        if index not in seen:
            seen.add(index)
            values.append(index)

    if not values:
        raise ValueError('请输入有效序号')
    return values


def get_auth_status(account_vip, today_time):
    if not account_vip:
        return '⚠️ 未授权', '无'
    if account_vip <= today_time:
        return '❌ 已过期', account_vip
    return '✅ 已授权', account_vip


def decode_wechat_nickname(raw):
    if raw is None:
        return ''
    s = re.sub(r'\s+', ' ', str(raw).replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')).strip().strip("'")
    if not s:
        return ''

    candidates = [s]
    try:
        unquoted = urllib.parse.unquote(s.replace('+', ' '))
        if unquoted:
            candidates.append(re.sub(r'\s+', ' ', unquoted).strip().strip("'"))
    except Exception:
        pass

    repaired = []
    for text in candidates[:]:
        if not text:
            continue
        for source_encoding in ('latin-1', 'cp1252'):
            try:
                fixed = text.encode(source_encoding).decode('utf-8')
                if fixed:
                    repaired.append(re.sub(r'\s+', ' ', fixed).strip().strip("'"))
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
            try:
                fixed = text.encode(source_encoding, errors='ignore').decode('utf-8', errors='ignore')
                if fixed:
                    repaired.append(re.sub(r'\s+', ' ', fixed).strip().strip("'"))
            except (UnicodeDecodeError, UnicodeEncodeError):
                pass
    candidates.extend(repaired)

    def score(text):
        if not text:
            return -1000
        cjk_count = len(re.findall(r'[\u3400-\u4dbf\u4e00-\u9fff]', text))
        mojibake_count = sum(
            1 for ch in text
            if 0x80 <= ord(ch) <= 0x9f or ch in 'ÃÂÅÆÇÐÑØÙÚÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ€�'
        )
        printable_count = sum(1 for ch in text if ch.isprintable() and not ch.isspace())
        return cjk_count * 20 + printable_count - mojibake_count * 12

    best = max(
        (text for text in candidates if text),
        key=score,
        default='',
    )
    return best


def is_usable_display_name(name):
    name = str(name or '').strip()
    if not name:
        return False
    cjk_pattern = r'[\u3400-\u4dbf\u4e00-\u9fff]'
    if not re.search(cjk_pattern, name) and not re.search(r'[A-Za-z0-9]', name):
        return False
    if name.strip('.…-_ ') == '':
        return False
    if ('...' in name or '…' in name) and not re.search(cjk_pattern, name):
        meaningful = re.sub(r'[^A-Za-z0-9]+', '', name)
        if len(meaningful) < 2:
            return False
    mojibake_count = sum(
        1 for ch in name
        if 0x80 <= ord(ch) <= 0x9f or ch in 'ÃÂÅÆÇÐÑØÙÚÝÞßàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ€�'
    )
    if re.search(cjk_pattern, name):
        return True
    return mojibake_count == 0


def get_account_display_name(account, userinfo=None):
    username = ''
    if isinstance(userinfo, dict):
        username = decode_wechat_nickname(userinfo.get('username', ''))
    if is_usable_display_name(username):
        return username
    return mask_phone(account) if len(account) >= 11 else account


def get_user_choice(prompt, timeout=120000, allow_quit=True):
    if prompt:
        sender.reply(prompt)
    choice = sender.input(timeout, 1, False)
    if choice is None or choice == 'timeout':
        sender.reply('✅ 已取消')
        return ''
    choice = str(choice).strip()
    if allow_quit and choice.lower() == 'q':
        sender.reply('✅ 已取消')
        return ''
    return choice


def get_content_config():
    return CONFIG['ql_envname'], '匠心管理', '匠心查询', '匠心登录'


# ==================== 面板对接函数 ====================

jxzh_osname, jxzh_managecommand, jxzh_querycommand, jxzh_signcommand = get_content_config()
panel_type_value = CONFIG['panel_type']
panel_config_value = CONFIG['panel_config']
panel_group = CONFIG['panel_group']
jxzh_zsm = CONFIG['zsm']
jxzhVipmoney = CONFIG['price']
jxzh_auth_days = CONFIG['auth_days']
jxzhcoin = CONFIG['coin']
jxzh_points_limit = CONFIG['points_limit']
jxzh_use_ma_pay = CONFIG['use_ma_pay']


def split_panel_config(raw):
    raw = (raw or '').strip()
    if not raw:
        return []
    parts = re.split(r'\s*[|｜丨]\s*', raw)
    return [p.strip() for p in parts if p and p.strip()]


def normalize_panel_type(panel_type_value):
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    return 'qinglong'


panel_type = normalize_panel_type(panel_type_value)
use_daidai = panel_type == 'daidai'


def get_ql_config():
    if not panel_config_value:
        sender.reply(format_message('配置错误', '未配置对接容器（青龙需要 URL、ClientID、ClientSecret）', 'error'))
        return '', '', ''
    parts = split_panel_config(panel_config_value)
    if len(parts) != 3:
        sender.reply(format_message('格式错误', '青龙对接容器需用 | 或 丨 分割为 3 段：Host、ClientID、ClientSecret', 'error'))
        return '', '', ''
    return parts[0], parts[1], parts[2]


def get_dd_config():
    if not panel_config_value:
        sender.reply(format_message('配置错误', '未配置对接容器（呆呆需要 host、app_key、app_secret）', 'error'))
        return '', '', ''
    parts = split_panel_config(panel_config_value)
    if len(parts) != 3:
        sender.reply(format_message('格式错误', '呆呆对接容器需用 | 或 丨 分割为 3 段', 'error'))
        return '', '', ''
    return parts[0], parts[1], parts[2]


panel_token_cache = None

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
    try:
        response = requests.get(url)
        result = response.json()
        if "token" in result.get('data', {}):
            return result['data']['token']
        return None
    except Exception as e:
        print(f"获取青龙Token失败: {e}")
        return None


def DDtoken(DDurl, AppKey, AppSecret):
    """获取呆呆面板token"""
    url = f'{DDurl.rstrip("/")}/api/open-api/token'
    data = {"app_key": AppKey, "app_secret": AppSecret}
    try:
        response = requests.post(url, json=data)
        result = response.json()
        return result.get('data', {}).get('access_token')
    except Exception as e:
        print(f"获取呆呆Token失败: {e}")
        return None


def get_panel_token():
    """获取面板token（带缓存）"""
    global panel_token_cache
    if panel_token_cache:
        return panel_token_cache
    
    if use_daidai:
        DDurl, AppKey, AppSecret = get_dd_config()
        panel_token_cache = DDtoken(DDurl, AppKey, AppSecret)
    else:
        QLurl, ClientID, ClientSecret = get_ql_config()
        panel_token_cache = QLtoken(QLurl, ClientID, ClientSecret)
    return panel_token_cache


def get_panel_headers(content_type="application/json"):
    """获取面板API请求头"""
    token = get_panel_token()
    return {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
        "Content-Type": content_type
    }


def get_panel_base_url():
    """获取面板基础URL"""
    if use_daidai:
        DDurl, _, _ = get_dd_config()
        return DDurl
    else:
        QLurl, _, _ = get_ql_config()
        return QLurl


def allenvs(osname, account):
    """查找环境变量"""
    if use_daidai:
        return dd_allenvs(osname, account)
    
    url = f"{get_panel_base_url()}/open/envs"
    headers = get_panel_headers()
    try:
        response = requests.get(url=url, headers=headers).json()
        if response['code'] == 200:
            envslist = response['data']
            for envs in envslist:
                envname = envs['name']
                remarks = envs['remarks']
                if remarks is None:
                    continue
                if osname == envname and str(account) in remarks:
                    return envs['id']
            return None
    except:
        pass
    return None


def dd_allenvs(osname, account):
    """呆呆面板查找环境变量"""
    url = f"{get_panel_base_url()}/api/envs"
    headers = get_panel_headers()
    params = {"keyword": str(account), "page_size": 100}
    try:
        response = requests.get(url=url, headers=headers, params=params).json()
        data_list = response.get('data', [])
        for envs in data_list:
            envname = envs.get('name', '')
            remarks = envs.get('remarks', '')
            if remarks is None:
                continue
            if osname == envname and str(account) in remarks:
                return envs['id']
    except:
        pass
    return None


def delenvs(id):
    """删除环境变量"""
    if id is None:
        return
    if use_daidai:
        url = f"{get_panel_base_url()}/api/envs/{id}"
        headers = get_panel_headers()
        requests.delete(url, headers=headers)
    else:
        url = f"{get_panel_base_url()}/open/envs"
        headers = get_panel_headers()
        data = [id]
        requests.delete(url, headers=headers, json=data)


def Addenvs(osname, value, account, phone, target_userid=None, expire_time=None):
    """添加或更新环境变量"""
    phone = mask_phone(phone)
    actual_userid = target_userid if target_userid else userid
    expire_info = f'丨到期:{expire_time}' if expire_time else ''
    
    qlid = allenvs(osname, account)
    
    if qlid is None:
        if use_daidai:
            DDcreate(osname, value, account, phone, actual_userid, expire_info)
        else:
            QLzt(osname, value, account, phone, actual_userid, expire_info)
    else:
        if use_daidai:
            DDupdate(osname, value, account, qlid, phone, actual_userid, expire_info)
        else:
            QLupdate(osname, value, account, qlid, phone, actual_userid, expire_info)


def QLupdate(osname, value, account, qlid, phone, target_userid, expire_info):
    """更新青龙环境变量"""
    url = f"{get_panel_base_url()}/open/envs"
    data = {
        "value": value,
        "name": osname,
        "remarks": f'匠心:{account}丨用户:{target_userid}丨手机:{phone}{expire_info}',
        "id": qlid
    }
    headers = get_panel_headers()
    requests.put(url, headers=headers, data=json.dumps(data))


def QLzt(osname, value, account, phone, target_userid, expire_info):
    """添加青龙环境变量"""
    url = f"{get_panel_base_url()}/open/envs"
    data = [{
        "value": value,
        "name": osname,
        "remarks": f'匠心:{account}丨用户:{target_userid}丨手机:{phone}{expire_info}'
    }]
    headers = get_panel_headers()
    requests.post(url, headers=headers, json=data)


def DDcreate(osname, value, account, phone, target_userid, expire_info):
    """添加呆呆环境变量"""
    url = f"{get_panel_base_url()}/api/envs"
    data = {
        "value": value,
        "name": osname,
        "remarks": f'匠心:{account}丨用户:{target_userid}丨手机:{phone}{expire_info}'
    }
    if panel_group:
        data["group"] = panel_group
    headers = get_panel_headers()
    requests.post(url, headers=headers, json=data)


def DDupdate(osname, value, account, env_id, phone, target_userid, expire_info):
    """更新呆呆环境变量"""
    url = f"{get_panel_base_url()}/api/envs/{env_id}"
    data = {
        "value": value,
        "name": osname,
        "remarks": f'匠心:{account}丨用户:{target_userid}丨手机:{phone}{expire_info}'
    }
    if panel_group:
        data["group"] = panel_group
    headers = get_panel_headers()
    requests.put(url, headers=headers, json=data)


# ==================== 支付与授权时长 ====================

def generate_qrcode(url):
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception as e:
        print(f"生成二维码失败: {str(e)}")
        return None


def send_qrcode_image(sender, qrcode_url, pay_type):
    pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
    pay_type_name = pay_type_names.get(pay_type, pay_type)
    try:
        sender.replyImage(qrcode_url)
        if pay_type == 'qqpay':
            sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\nQQ支付打开图片若是黑屏，长按屏幕进行\"识别二维码\"即可！\n支付过程中输入'q'可取消支付")
        else:
            sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付")
    except Exception:
        if pay_type == 'qqpay':
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！\n[CQ:image,file={qrcode_url}]'
        else:
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n[CQ:image,file={qrcode_url}]'
        sender.reply(pay_msg)


def yesornos():
    choice = get_user_choice("", 120000, True)
    if choice in ['Y', 'y', '是']:
        return True
    if choice in ['n', 'N', '否', '']:
        return False
    sender.reply(format_message("输入错误", "请输入正确的选项", "error"))
    return False


def jxzh_get_payment_config():
    zsm = jxzh_zsm
    use_ma_pay = jxzh_use_ma_pay
    ma_pay_config = None
    if use_ma_pay:
        ma_pay_config = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type'),
            'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
            'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
        }
        if ma_pay_config['switch'].lower() != 'true' or not all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
            use_ma_pay = False
            ma_pay_config = None
    return zsm, use_ma_pay, ma_pay_config


def jxzh_parse_payment_result(ddzf):
    try:
        if isinstance(ddzf, dict):
            if ddzf.get('Type') == '微信赞赏':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            if ddzf.get('Type') == '微信收款':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            if ddzf.get('Money'):
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
            if ddzf.get('money'):
                return float(ddzf.get('money', 0)), ddzf.get('time', '').replace('T', ' ').split('.')[0], ddzf.get('fromName', '')
            sender.reply(format_message("支付错误", "不支持的支付消息格式", "error"))
            return None
        try:
            ddzf = json.loads(ddzf)
        except Exception:
            sender.reply(format_message("解析错误", "无法解析支付结果", "error"))
            return None
        if ddzf.get('Type') == '微信赞赏':
            return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
        if ddzf.get('Type') == '微信收款':
            return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
        return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
    except Exception as e:
        sender.reply(format_message("处理错误", f"处理支付结果时出错: {str(e)}", "error"))
        return None


def jxzh_empower(empowertime, months_int):
    """按配置「授权天数」×月数延长到期日"""
    today_time = datetime.now().strftime("%Y-%m-%d")
    today_date = datetime.now().date()
    day = int(months_int) * jxzh_auth_days
    if not empowertime or empowertime <= today_time:
        delayed_date = today_date + timedelta(days=day)
    elif empowertime > today_time:
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        delayed_date = delayed_date.date()
    else:
        sender.reply('出错！')
        return ''
    return str(delayed_date)


def jxzh_token_value_for_account(account):
    token_data = get_token(account)
    return token_data.get('token', '')


def jxzh_zf(project, months_int, accountVip, token, phone, account):
    """匠心用户授权支付（与顺丰逻辑一致，配置来自插件框）"""
    try:
        money = Decimal(months_int) * jxzhVipmoney
        if money == 0:
            new_vip = jxzh_empower(accountVip or '', months_int)
            if not new_vip:
                return False
            save_auth(account, new_vip)
            Addenvs(osname=jxzh_osname, value=token, account=account, phone=phone, expire_time=new_vip)
            sender.reply(format_message("免费授权成功",
                f"商品: {project}\n金额: 免费\n授权时长: {months_int}月（每{jxzh_auth_days}天为1月）", "success"))
            return True

        zsm, use_ma_pay, ma_pay_config = jxzh_get_payment_config()
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(jxzhcoin) * int(months_int) if jxzhcoin else 0
        opt_points = bool(jxzhcoin and int(jxzhcoin) > 0)
        opt_ma = bool(use_ma_pay and ma_pay_config)
        opt_zsm = bool(zsm and str(zsm).strip())

        if not opt_points and not opt_ma and not opt_zsm:
            sender.reply(format_message("配置错误",
                "付费授权需至少配置一种支付方式：\n• 填写「积分支付」\n或开启有效「使用码支付」并完成卡密系统码支付配置\n或填写「赞赏码链接」", "error"))
            return False

        pay_menu = "=====请选择支付方式====="
        option_num = 1
        options_map = {}

        if opt_points:
            pay_menu += f"\n[{option_num}] 积分支付\n   🎯 需 {zfcoin} 积分（{months_int}月）\n   💫 当前积分: {usercoin}"
            options_map[str(option_num)] = 'points'
            option_num += 1
        if opt_ma:
            pay_menu += f"\n[{option_num}] 码支付\n   💰 {money}元 / {months_int}月"
            options_map[str(option_num)] = 'ma'
            option_num += 1
        if opt_zsm:
            pay_menu += f"\n[{option_num}] 赞赏码支付\n   💰 {money}元 / {months_int}月（微信扫码赞赏或收款）"
            options_map[str(option_num)] = 'wechat'
            option_num += 1

        pay_menu += "\n------------------\n回复对应数字\n回复'q'退出\n=================="
        sender.reply(pay_menu)
        choice = get_user_choice("", 60000, True)
        if not choice:
            return False

        selected_pay = options_map.get(choice)
        if selected_pay == 'wechat' and opt_zsm:
            if sender.atWaitPay():
                sender.reply(format_message("支付繁忙", "当前有人正在支付,请稍后再试！", "warning"))
                return False
            pay_msg = f"""=====微信扫码支付====
🎫 商品: {project}
📅 时长: {months_int}月
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
            sender.reply(pay_msg)
            sender.replyImage(zsm)
            ddzf = sender.waitPay("q", 100 * 1000)
            if str(ddzf) == 'q':
                sender.reply(format_message("已取消", "已取消支付", "info"))
                return False
            payment_result = jxzh_parse_payment_result(ddzf)
            if not payment_result:
                return False
            Money, Time, From = payment_result
            if float(Money) >= float(money):
                new_vip = jxzh_empower(accountVip or '', months_int)
                if not new_vip:
                    return False
                save_auth(account, new_vip)
                Addenvs(osname=jxzh_osname, value=token, account=account, phone=phone, expire_time=new_vip)
                sender.reply(f"""=====支付成功=====
🎫 商品: {project}
💰 金额: {Money}元
⏰ 时间: {Time}
{f'👤 付款人: {From}' if From else ''}
==================""")
                return True
            sender.reply(format_message("支付金额错误",
                f"应付: {money}元\n实付: {Money}元\n{f'付款人: {From}' if From else ''}\n\n❗ 请联系管理员处理退款！", "error"))
            return False

        if selected_pay == 'ma' and opt_ma and ma_pay_config:
            out_trade_no = f"JX{int(time.time())}{userid}"
            params = {
                'pid': ma_pay_config['pid'],
                'type': ma_pay_config['type'].split(',')[0],
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-匠心授权-{str(money)}",
                'money': str(money),
                'notify_url': ma_pay_config['notify_url'],
                'return_url': ma_pay_config['return_url'],
                'param': userid
            }
            params = {k: v for k, v in params.items() if v}
            sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
            sign = hashlib.md5((sign_str + ma_pay_config['key']).encode('utf-8')).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            gateway = ma_pay_config['gateway']
            if gateway.endswith('/'):
                gateway = gateway[:-1]
            mapi_url = f"{gateway}/mapi.php"
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
            if response.status_code != 200:
                sender.reply(format_message("支付失败", f"创建支付订单失败，HTTP状态码: {response.status_code}", "error"))
                return False
            try:
                result = response.json()
            except Exception:
                sender.reply(format_message("支付失败", "创建支付订单失败，返回数据格式错误", "error"))
                return False
            if result.get('code', 0) != 1:
                msg = result.get('msg', '未知状态')
                sender.reply(format_message("支付失败", f"创建订单失败: {msg}", "error"))
                return False
            payurl = result.get('payurl', '')
            if not payurl:
                sender.reply(format_message("支付失败", "未获取到支付链接", "error"))
                return False
            qrcode_url = generate_qrcode(payurl)
            pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
            if qrcode_url:
                send_qrcode_image(sender, qrcode_url, pay_type)
            else:
                sender.reply(f"请点击链接完成支付:\n{payurl}")
            for _ in range(60):
                check_url = gateway
                if '/xpay/epay/api.php' not in check_url:
                    check_url = f"{check_url.rstrip('/')}/xpay/epay/api.php"
                check_params = {
                    'act': 'order',
                    'pid': ma_pay_config['pid'],
                    'key': ma_pay_config['key'],
                    'out_trade_no': out_trade_no
                }
                try:
                    check_resp = requests.get(check_url, params=check_params, timeout=10)
                    check_result = check_resp.json()
                    if check_result.get('code') == 1 and check_result.get('status') == 1:
                        new_vip = jxzh_empower(accountVip or '', months_int)
                        if not new_vip:
                            return False
                        save_auth(account, new_vip)
                        Addenvs(osname=jxzh_osname, value=token, account=account, phone=phone, expire_time=new_vip)
                        sender.reply(f"""=====支付成功=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 授权时长: {months_int}月
==================""")
                        return True
                except Exception as e:
                    print(f"查询订单状态出错: {str(e)}")
                result = sender.listen(5000)
                if result == 'q' or result == 'Q':
                    sender.reply("✅ 已取消支付")
                    return False
            sender.reply("❌ 支付超时,请重新发起支付!")
            return False

        if selected_pay == 'points' and jxzhcoin and int(jxzhcoin) > 0:
            if int(usercoin) < zfcoin:
                sender.reply(format_message("积分不足", f"当前积分: {usercoin}\n需要积分: {zfcoin}", "error"))
                return False
            sender.reply(f"💫 积分支付确认\n💰 消耗积分: {zfcoin}\n⏰ 授权时长: {months_int}月\n------------------\n确认请回复【y】\n取消请回复【n】")
            if yesornos():
                new_balance = int(usercoin) - zfcoin
                middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                new_vip = jxzh_empower(accountVip or '', months_int)
                if not new_vip:
                    return False
                save_auth(account, new_vip)
                Addenvs(osname=jxzh_osname, value=token, account=account, phone=phone, expire_time=new_vip)
                sender.reply(f"✅ 支付成功\n💫 扣除积分: {zfcoin}\n💰 剩余积分: {new_balance}\n⏰ 授权时长: {months_int}月")
                return True
            sender.reply(format_message("已取消支付", "操作已取消", "info"))
            return False

        sender.reply(format_message("输入无效", "请输入正确的选项", "error"))
        return False
    except Exception as e:
        sender.reply(format_message("系统错误", f"支付处理异常\n错误信息: {str(e)}", "error"))
        return False


# ==================== 登录功能 ====================

def jxzh_login():
    """匠心扫码登录"""
    try:
        sender.reply("=====匠心扫码登录=====\n⌛ 正在加载二维码...\n⏳ 请稍候...\n==================")
        qr_data = get_qr_code()
        if not qr_data:
            sender.reply('❌ 获取二维码失败!')
            return
        qr_uuid = qr_data.get('uuid')
        qr_url = qr_data.get('img_url')
        qr_created_at = time.time()
        sender.replyImage(qr_url)
        sender.reply(f"=====登录说明=====\n📱 请使用微信扫描二维码登录\n------------------\n⚠️ 注意事项:\n1. 请确保已登录微信\n2. 扫码后请等待授权完成\n3. 二维码有效期{QR_EXPIRE_SECONDS // 60}分钟，超过后请重新登录\n4. 输入 q 可取消登录\n==================")
        retry = 150
        while retry > 0:
            user_input = sender.listen(2000)
            if user_input and str(user_input).strip().lower() == 'q':
                sender.reply('✅ 已取消登录')
                return
            result = check_qr_status(qr_uuid, qr_created_at)
            retry -= 1
            if not result:
                continue
            code = result.get('code')
            msg = result.get('msg')
            if code == 0:
                data = result.get('data', {})
                wx_code = data.get('code')
                wx_nickname = data.get('nickname')
                sender.reply(f"✅ 扫码成功! 昵称: {wx_nickname}")
                token_info = exchange_token(wx_code)
                if not token_info:
                    return
                token = token_info.get('token')
                user_id = token_info.get('userId')
                mobile = token_info.get('mobile') or ''
                username = decode_wechat_nickname(token_info.get('username') or '')
                if not is_usable_display_name(username):
                    username = decode_wechat_nickname(token_info.get('nickname') or wx_nickname or '')
                if not token:
                    sender.reply('❌ 获取Token失败，请重试!')
                    return
                account = mobile or user_id
                add_account(account, userid)
                save_token(account, str(user_id or ''), str(token or ''), '')
                display_mobile = mask_phone(account) if len(account) >= 11 else account
                display_name = username if is_usable_display_name(username) else display_mobile
                authorized = is_authorized(account)
                auth_status = '✅ 已授权' if authorized else '⚠️ 未授权'
                upload_status = ''
                if authorized:
                    expire_date = get_auth(account)
                    try:
                        Addenvs(
                            osname=jxzh_osname,
                            value=token,
                            account=account,
                            phone=account,
                            expire_time=expire_date,
                        )
                        upload_status = '\n📤 匠心上传：✅ 已同步到面板'
                    except Exception as e:
                        upload_status = f'\n📤 匠心上传：❌ 同步失败({e})'
                sender.reply(
                    f"✅ 扫码成功! 昵称: {display_name}\n"
                    f"📱 账号: {display_mobile}\n"
                    f"🔐 授权状态: {auth_status}"
                    f"{upload_status}\n"
                    f"💡 发送 {jxzh_managecommand} 可管理账号"
                )
                return
            if code == 1:
                if retry % 10 == 0:
                    sender.reply(f"⏳ 等待扫码中... (剩余 {retry * 2}秒)")
                continue
            if code == 2:
                sender.reply('❌ 二维码已过期,请重新尝试!')
                return
            if retry % 10 == 0:
                sender.reply(f"⏳ {msg} (剩余 {retry * 2}秒)")
        sender.reply('❌ 扫码超时,请重新尝试!')
    except Exception as e:
        sender.reply(f'❌ 登录失败: {str(e)}')


# ==================== 查询功能 ====================

def jxzh_query_detail_lines(account, today_time):
    """单账号接口详情行（不含总标题），供单个/批量查询复用"""
    accountVip = get_auth(account)
    auth_status, auth_time = get_auth_status(accountVip, today_time)
    login_mobile = mask_phone(account) if len(account) >= 11 else account

    token = jxzh_token_value_for_account(account)

    lines = [f"📱 账号：{login_mobile}"]

    username = ''
    total_points = '0'
    today_points = '0'

    if token:
        userinfo = get_task_userinfo(token)
        if userinfo:
            total_points = userinfo.get('points', '0')
            today_points = userinfo.get('task_rice', '0')
            username = decode_wechat_nickname(userinfo.get('username', ''))

    if is_usable_display_name(username):
        lines.append(f"👤 昵称：{username}")

    if not token:
        lines.append("❌ 本地无 Token，请发送「匠心登录」重新绑定")
        return lines

    lines.append(f"⭐ 今日积分：{today_points}")
    lines.append(f"⭐ 总积分：{total_points}")
    if auth_time and auth_time != '无':
        lines.append(f"📅 到期：{auth_time}")

    points_data = get_points_list(token)
    all_records = []
    if points_data:
        rows = points_data.get('dataRows', [])
        if rows:
            records = rows[0].get('list', [])
            all_records = records[:jxzh_points_limit]

    if all_records:
        lines.append("🧾 积分明细：")
        for record in all_records:
            addtime = record.get('addtime', '')
            actlog = record.get('actlog', '未知')
            points = record.get('points', '0')
            date_part = addtime.split(' ')[0].replace('-', '.')
            lines.append(f"{date_part} {actlog} {points}")
    else:
        lines.append("🧾 积分明细：暂无记录")

    return lines


def format_order_product_titles(order_items) -> str:
    titles = []
    for item in order_items or []:
        title = str(item.get('product_title') or '').strip()
        if title and title not in titles:
            titles.append(title)
    if not titles:
        return '未知商品'
    if len(titles) == 1:
        return titles[0]
    return f"{titles[0]} 等{len(titles)}件商品"


def jxzh_logistics_detail_lines(account):
    """单账号物流详情行（不含总标题），供单个/批量物流复用"""
    token = jxzh_token_value_for_account(account)
    userinfo = get_task_userinfo(token) if token else None
    display_name = get_account_display_name(account, userinfo)
    lines = [f"📱 账号：{display_name}"]

    if not token:
        lines.append("❌ 本地无 Token，请发送「匠心登录」重新绑定")
        return lines

    order_result = get_order_list(token, status='3', page=1, keywords='')
    if not order_result.get('ok'):
        lines.append(f"❌ 物流查询失败：{order_result.get('message') or order_result.get('code') or '未知错误'}")
        return lines
    orders = order_result.get('data') or []
    if not orders:
        lines.append("📦 暂无待收货订单")
        return lines

    lines.append(f"📦 待收货订单：{len(orders)}个")

    for index, order in enumerate(orders[:LOGISTICS_ORDER_LIMIT], 1):
        logistic_data = order.get('logistic_data') or {}
        last_message = re.sub(r'\s+', ' ', str(logistic_data.get('theLastMessage') or '')).strip()
        company_name = str(logistic_data.get('logisticsCompanyName') or '').strip()
        logistic_status = str(logistic_data.get('logisticsStatus') or '').strip()
        product_title = format_order_product_titles(order.get('list') or [])
        status_text = str(order.get('statusTxt') or order.get('status') or '未知状态')
        order_number = str(order.get('order_number') or '')
        create_time = str(order.get('create_time') or '')
        delivery_time = str(order.get('delivery_time') or '')
        pay_text = str(order.get('pay_txt') or order.get('pay_all_txt') or '')

        lines.append(f"【物流{index}】")
        if order_number:
            lines.append(f"🚚 物流单号：{order_number}")
        if create_time:
            lines.append(f"🕒 兑换时间：{create_time}")
        lines.append(f"🎁 兑换物品：{product_title}")
        lines.append(f"📌 当前状态：{status_text}")
        if pay_text:
            lines.append(f"💰 扣费信息：{pay_text}")
        if delivery_time:
            lines.append(f"📤 发货时间：{delivery_time}")
        if company_name:
            lines.append(f"🏷️ 快递公司：{company_name}")
        if logistic_status:
            lines.append(f"📍 物流状态：{logistic_status}")
        lines.append(f"📝 最新轨迹：{last_message or '暂无物流信息'}")
        lines.append("-------------------")

    if len(orders) > LOGISTICS_ORDER_LIMIT:
        lines.append(f"ℹ️ 仅展示前 {LOGISTICS_ORDER_LIMIT} 条待收货订单")
    return lines


def jxzh_query():
    """查询账号信息"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {jxzh_signcommand} 绑定", "error"))
        return

    try:
        today_time = datetime.now().strftime("%Y-%m-%d")

        for account in accounts:
            detail = jxzh_query_detail_lines(account, today_time)
            sender.reply("=====匠心查询=====\n" + "\n".join(detail) + "\n====================")

    except Exception as e:
        sender.reply(format_message("查询错误", f"查询失败: {str(e)}", "error"))


def _format_points(value) -> str:
    try:
        return str(int(float(str(value or '0').strip() or '0')))
    except Exception:
        return str(value or '0')


def _mask_mobile(text: str) -> str:
    text = str(text or '').strip()
    digits = re.sub(r'\D+', '', text)
    if len(digits) >= 11:
        return f"{digits[:3]}****{digits[-4:]}"
    return text


def _mask_address(text: str) -> str:
    text = str(text or '').strip()
    if not text:
        return ''
    text = re.sub(r'\d{2,}.*$', '', text)
    text = re.sub(r'(室|单元|栋|幢|楼|号房|门牌).*$', '', text)
    text = text.strip(' -,，。')
    if len(text) > 18:
        text = text[:18] + '...'
    return text or '详细地址已隐藏'


def get_product_list(token, page=1):
    try:
        result = signed_post_with_fallback(
            PRODUCT_LIST_URL,
            headers=get_base_headers(),
            extra={
                'token': token,
                'page': str(page),
                'points': '2',
                'points_price_stage': '0',
                'tag_id': '0',
                'type': '6',
                'mode': '0',
            },
            use_app_style=False,
            timeout=10,
        )
        if result.get('code') == 1:
            data = result.get('data') or []
            return data if isinstance(data, list) else []
        return []
    except Exception as e:
        print(f"获取商品列表失败: {e}")
        return []


def get_all_products(token, max_pages=10):
    all_products = []
    for page in range(1, max_pages + 1):
        page_data = get_product_list(token, page=page)
        if not page_data:
            break
        all_products.extend(page_data)
        if len(page_data) < 10:
            break
    return all_products


def get_product_detail(token, product_num):
    try:
        result = signed_post_with_fallback(
            PRODUCT_DETAIL_URL,
            headers=get_base_headers(),
            extra={
                'token': token,
                'productNum': str(product_num),
                'numcode': '',
            },
            use_app_style=False,
            timeout=10,
        )
        if result.get('code') == 1:
            data = result.get('data') or {}
            return data if isinstance(data, dict) else {}
        return {}
    except Exception as e:
        print(f"获取商品详情失败: {e}")
        return {}


def get_address_list(token):
    try:
        result = signed_post_with_fallback(
            ADDRESS_LIST_URL,
            headers=get_base_headers(),
            extra={'token': token},
            use_app_style=False,
            timeout=10,
        )
        if result.get('code') == 1:
            data = result.get('data') or []
            return data if isinstance(data, list) else []
        return []
    except Exception as e:
        print(f"获取地址列表失败: {e}")
        return []


def delete_address(token, address_id):
    try:
        result = signed_post_with_fallback(
            ADDRESS_DEL_URL,
            headers=get_base_headers(),
            extra={'token': token, 'address_id': str(address_id)},
            use_app_style=False,
            timeout=10,
        )
        return result if isinstance(result, dict) else {}
    except Exception as e:
        print(f"删除地址失败: {e}")
        return {}


def create_address(token, name, mobile, address, province_id, city_id, area_id, region_id, province_str, city_str, area_str, region_str, house_number='', is_default='1'):
    try:
        result = signed_post_with_fallback(
            ADDRESS_CREATE_URL,
            headers=get_base_headers(),
            extra={
                'token': token,
                'name': name,
                'mobile': mobile,
                'address': address,
                'is_default': str(is_default),
                'house_number': house_number or '',
                'province_id': str(province_id),
                'city_id': str(city_id),
                'area_id': str(area_id),
                'region_id': str(region_id),
                'province_str': province_str,
                'city_str': city_str,
                'area_str': area_str,
                'region_str': region_str,
            },
            use_app_style=False,
            timeout=10,
        )
        return result if isinstance(result, dict) else {}
    except Exception as e:
        print(f"创建地址失败: {e}")
        return {}


def search_address(token, province_str, keyword):
    try:
        result = signed_post_with_fallback(
            ADDRESS_SEARCH_URL,
            headers=get_base_headers(),
            extra={
                'token': token,
                'provinceStr': province_str,
                'keyword': keyword,
            },
            use_app_style=False,
            timeout=10,
        )
        if result.get('code') == 1:
            data = result.get('data') or []
            return data if isinstance(data, list) else []
        return []
    except Exception as e:
        print(f"搜索地址失败: {e}")
        return []


def get_area_code(token, location):
    try:
        result = signed_post_with_fallback(
            ADDRESS_AREA_CODE_URL,
            headers=get_base_headers(),
            extra={'token': token, 'location': str(location)},
            use_app_style=False,
            timeout=10,
        )
        if result.get('code') == 1 and result.get('data'):
            return result['data']
        return {}
    except Exception as e:
        print(f"获取区域编码失败: {e}")
        return {}


def get_area_list(token, area_type, pid='0'):
    for attempt in range(3):
        try:
            result = signed_post_with_fallback(
                ADDRESS_AREA_URL,
                headers=get_base_headers(),
                extra={
                    'token': token,
                    'type': str(area_type),
                    'pid': str(pid),
                },
                use_app_style=False,
                timeout=15,
            )
            if result.get('code') == 1 and result.get('data'):
                data = result.get('data') or []
                return data if isinstance(data, list) else []
            print(f"获取区域列表响应异常(type={area_type},pid={pid},attempt={attempt+1}): {result}")
        except Exception as e:
            print(f"获取区域列表失败(type={area_type},pid={pid},attempt={attempt+1}): {e}")
        if attempt < 2:
            time.sleep(1)
    return []


def flatten_area_list(area_data: list) -> list:
    items = []
    for group in area_data:
        if isinstance(group, dict) and isinstance(group.get('list'), list):
            for item in group['list']:
                if isinstance(item, dict) and item.get('id') and item.get('name'):
                    items.append({'id': str(item['id']), 'name': str(item['name'])})
    return items


def create_order(token, address_id, product_id, product_sku, num=1):
    try:
        result = signed_post_with_fallback(
            ORDER_CREATE_URL,
            headers=get_base_headers(),
            extra={
                'token': token,
                'source': '2',
                'address_id': str(address_id),
                'product_id': str(product_id),
                'product_sku': str(product_sku),
                'num': str(num),
                'comment': '',
                'group_name_id': '',
                'sid': '',
                'is_point_deduct': '2',
                'pay_type': '3',
                'coupon_id': '0',
                'optimal_deduction': '2',
                'isPickup': '2',
                'pickupMobile': '',
                'commission_deduction_type': '2',
            },
            use_app_style=False,
            timeout=10,
        )
        return result if isinstance(result, dict) else {}
    except Exception as e:
        print(f"创建订单失败: {e}")
        return {}


def _is_create_order_sku(candidate, product_num=None):
    val = str(candidate or '').strip()
    if not val:
        return False
    pn = str(product_num or '').strip()
    if pn and val == pn:
        return False
    if pn and val.isdigit() and len(val) >= 10 and len(pn) >= 10:
        return False
    return True


def _sku_from_sku_list(node, product_num=None):
    if not isinstance(node, dict):
        return ''
    for arr_key in ('skuList', 'sku_list', 'skus', 'productSkus', 'product_skus', 'default_skus'):
        arr = node.get(arr_key)
        if not isinstance(arr, list):
            continue
        for item in arr:
            if not isinstance(item, dict):
                continue
            for key in ('id', 'sku_id', 'product_sku', 'skuId'):
                value = item.get(key)
                if _is_create_order_sku(value, product_num):
                    return str(value).strip()
    return ''


def _sku_from_product_item(product):
    if not isinstance(product, dict):
        return ''
    product_num = product.get('product_num') or product.get('productNum')
    got = _sku_from_sku_list(product, product_num)
    if got and _is_create_order_sku(got, product_num):
        return got
    for key in ('product_sku', 'productSku', 'sku_id', 'sku', 'default_sku', 'defaultSku'):
        value = product.get(key)
        if _is_create_order_sku(value, product_num):
            return str(value).strip()
    return ''


def _sku_from_product_detail(detail):
    if not isinstance(detail, dict):
        return ''
    product_num = detail.get('product_num') or detail.get('productNum')
    got = _sku_from_sku_list(detail, product_num)
    if got and _is_create_order_sku(got, product_num):
        return got
    inner = detail.get('product_info') or detail.get('productInfo') or detail.get('info')
    if isinstance(inner, dict):
        got = _sku_from_product_detail(inner)
        if got:
            return got
    prod = detail.get('product') or detail.get('productDetail')
    if isinstance(prod, dict):
        got = _sku_from_product_item(prod)
        if got:
            return got
    for key in ('product_sku', 'productSku', 'sku_id', 'sku', 'default_sku', 'defaultSku'):
        value = detail.get(key)
        if _is_create_order_sku(value, product_num):
            return str(value).strip()
    return ''


def resolve_exchange_product_sku(token, selected):
    product_num = (
        selected.get('product_num')
        or selected.get('productNum')
        or selected.get('numcode')
        or selected.get('product_num_id')
    )
    detail = {}
    sku = ''
    if product_num:
        detail = get_product_detail(token, str(product_num)) or {}
        sku = _sku_from_product_detail(detail)
    if not sku:
        sku = _sku_from_product_item(selected)
    return sku or '', detail


PAGE_SIZE = 10


def _render_product_page(display_list: list, page_idx: int, total: int, title_prefix: str):
    """渲染一页商品列表，返回当前页的 product 子列表"""
    start = page_idx * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(display_list))
    page_items = display_list[start:end]
    total_pages = (len(display_list) + PAGE_SIZE - 1) // PAGE_SIZE

    lines = [f"====={title_prefix}====="]
    lines.append(f"📦 共 {total} 件  第 {page_idx + 1}/{total_pages} 页")
    for idx, product in enumerate(page_items, start + 1):
        title = str(product.get("title") or "未知商品").strip()
        points = _format_points(product.get("points", "0"))
        market_price = str(product.get("market_price") or product.get("price") or "")
        stock = str(product.get("stock") or "")
        limited_str = str(product.get("limited_str") or "").strip()
        title_short = title[:22] + "..." if len(title) > 22 else title
        lines.append(f"[{idx}] {title_short}")
        lines.append(f"    💰 积分: {points}  市价: ¥{market_price}")
        if stock:
            lines.append(f"    📦 库存: {stock}")
        if limited_str:
            lines.append(f"    🔖 {limited_str}")
    lines.append("-------------------")
    nav_hints = []
    if page_idx > 0:
        nav_hints.append("上一页: p")
    if end < len(display_list):
        nav_hints.append("下一页: n")
    if nav_hints:
        lines.append("翻页: " + " | ".join(nav_hints))
    lines.append("回复商品序号选择，回复 q 退出")
    sender.reply("\n".join(lines))
    return page_items


def _search_and_select_product(token):
    """关键词搜索并选择商品（支持翻页），返回选中的 product dict 或 None"""
    sender.reply("🔍 请输入商品关键词搜索\n回复 0 查看全部商品列表\n回复 q 退出")
    keyword = get_user_choice("", 120000, True)
    if not keyword:
        return None
    use_keyword = keyword.strip() != '0'

    sender.reply("🎁 正在加载全部积分商品...")
    products = get_all_products(token)
    if not products:
        sender.reply(format_message("加载失败", "暂无可兑换商品，请稍后重试", "error"))
        return None

    if use_keyword:
        kw = keyword.strip().lower()
        display_list = [p for p in products if kw in str(p.get('title') or '').lower()]
        if not display_list:
            sender.reply(format_message("搜索无结果", f"未找到包含「{keyword.strip()}」的商品\n💡 请换个关键词重试", "error"))
            return None
        title_prefix = f"搜索「{keyword.strip()}」"
    else:
        display_list = products
        title_prefix = "匠心积分兑换"

    page_idx = 0
    total_pages = (len(display_list) + PAGE_SIZE - 1) // PAGE_SIZE

    while True:
        _render_product_page(display_list, page_idx, len(display_list), title_prefix)
        user_choice = get_user_choice("", 120000, True)
        if not user_choice:
            return None

        cmd = user_choice.strip().lower()
        if cmd == 'n':
            if page_idx + 1 < total_pages:
                page_idx += 1
                continue
            sender.reply("⚠️ 已经是最后一页了")
            continue
        if cmd == 'p':
            if page_idx > 0:
                page_idx -= 1
                continue
            sender.reply("⚠️ 已经是第一页了")
            continue

        try:
            choice_idx = int(user_choice) - 1
        except ValueError:
            sender.reply(format_message("输入错误", "请输入商品序号、n翻下页、p翻上页", "error"))
            continue
        if choice_idx < 0 or choice_idx >= len(display_list):
            sender.reply(format_message("输入无效", f"商品序号超出范围（1-{len(display_list)}）", "error"))
            continue
        return display_list[choice_idx]


def jxzh_exchange():
    """匠心积分兑换商品"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n🔕 发送「{jxzh_signcommand}」绑定", "error"))
        return

    try:
        today_time = datetime.now().strftime("%Y-%m-%d")
        if len(accounts) > 1:
            lines = ["=====选择兑换账号=====", "0. 取消返回"]
            for i, account in enumerate(accounts, 1):
                account_vip = get_auth(account)
                auth_status, _ = get_auth_status(account_vip, today_time)
                token = jxzh_token_value_for_account(account)
                userinfo = get_task_userinfo(token) if token else None
                login_name = get_account_display_name(account, userinfo)
                lines.append(f"{i}. {login_name}（{auth_status}）")
            lines.append("回复账号序号选择，回复 q 退出")
            sender.reply("\n".join(lines))
            account_choice = get_user_choice("", 120000, True)
            if not account_choice:
                return
            try:
                account_idx = int(account_choice)
            except ValueError:
                sender.reply(format_message("输入错误", "请输入账号序号", "error"))
                return
            if account_idx == 0:
                sender.reply("✅ 已取消兑换")
                return
            if account_idx < 1 or account_idx > len(accounts):
                sender.reply(format_message("输入无效", "账号序号超出范围", "error"))
                return
            account = accounts[account_idx - 1]
        else:
            account = accounts[0]

        account_vip = get_auth(account)
        auth_status, _ = get_auth_status(account_vip, today_time)
        if "未授权" in auth_status or "已过期" in auth_status:
            sender.reply(format_message("未授权", "该账号未授权或已过期，请先授权后再兑换", "error"))
            return

        token = jxzh_token_value_for_account(account)
        if not token:
            sender.reply(format_message("登录失效", "Token 已失效，请重新发送「匠心登录」绑定", "error"))
            return

        selected = _search_and_select_product(token)
        if not selected:
            return

        product_id = str(selected.get("id") or "").strip()
        product_title = str(selected.get("title") or "未知商品").strip()
        product_points = _format_points(selected.get("points", "0"))
        product_price = str(selected.get("price") or selected.get("market_price") or "")
        stock = str(selected.get("stock") or "").strip()
        limited_str = str(selected.get("limited_str") or "").strip()

        sender.reply("⏳ 正在获取商品规格信息...")
        product_sku, sku_detail = resolve_exchange_product_sku(token, selected)
        if not product_sku:
            sender.reply(format_message("商品信息异常", "无法获取该商品的规格ID，请稍后重试或到小程序内兑换", "error"))
            return
        if sku_detail and sku_detail.get("id"):
            product_id = str(sku_detail.get("id")).strip() or product_id
        if stock and stock.isdigit() and int(stock) <= 0:
            sender.reply(format_message("库存不足", "该商品库存为 0，无法下单", "error"))
            return

        spec_hint = ""
        standard_json = sku_detail.get("standard_json") or sku_detail.get("standardJson") or []
        if isinstance(standard_json, list) and standard_json:
            parts = []
            for item in standard_json[:3]:
                if isinstance(item, dict):
                    name = str(item.get("name") or "").strip()
                    value = str(item.get("value") or "").strip()
                    if name or value:
                        parts.append(f"{name}:{value}" if name else value)
            if parts:
                spec_hint = " / ".join(parts)

        confirm_lines = ["=====确认兑换====="]
        confirm_lines.append(f"🎁 商品: {product_title}")
        confirm_lines.append(f"💰 所需积分: {product_points}")
        if product_price:
            confirm_lines.append(f"💵 商品价格: ¥{product_price}")
        if product_id:
            confirm_lines.append(f"🆔 商品ID: {product_id}")
        confirm_lines.append(f"📦 规格ID: {product_sku}")
        if spec_hint:
            confirm_lines.append(f"🏷️ 规格: {spec_hint}")
        if stock:
            confirm_lines.append(f"📦 库存: {stock}")
        if limited_str:
            confirm_lines.append(f"🔖 限购: {limited_str}")
        confirm_lines.append("回复【Y】立即兑换")
        confirm_lines.append("回复 q 取消")
        sender.reply("\n".join(confirm_lines))

        confirm = get_user_choice("", 120000, True)
        if not confirm:
            return
        if str(confirm).strip().upper() != "Y":
            sender.reply(format_message("操作取消", "未确认兑换，已退出", "info"))
            return

        sender.reply("📍 正在获取收货地址...")
        address_list = get_address_list(token)
        if not address_list:
            sender.reply(format_message("地址错误", "未找到收货地址，请先在匠心小程序中添加收货地址", "error"))
            return

        if len(address_list) > 1:
            addr_lines = ["=====选择收货地址====="]
            for i, addr in enumerate(address_list, 1):
                is_default = "【默认】" if str(addr.get("is_default") or "") == "1" else ""
                masked_mobile = _mask_mobile(addr.get("mobile", ""))
                masked_addr = _mask_address(addr.get("address", ""))
                region = f"{addr.get('province_str', '')}{addr.get('city_str', '')}{addr.get('area_str', '')}"
                addr_lines.append(f"[{i}] {addr.get('name', '')} {masked_mobile} {is_default}")
                addr_lines.append(f"    {region}{masked_addr}")
            addr_lines.append("回复数字选择地址，回复 q 取消")
            sender.reply("\n".join(addr_lines))
            addr_choice = get_user_choice("", 120000, True)
            if not addr_choice:
                return
            try:
                addr_idx = int(addr_choice) - 1
            except ValueError:
                sender.reply(format_message("输入错误", "请输入地址序号", "error"))
                return
            if addr_idx < 0 or addr_idx >= len(address_list):
                sender.reply(format_message("输入无效", "地址序号超出范围", "error"))
                return
            selected_addr = address_list[addr_idx]
        else:
            selected_addr = address_list[0]

        addr_id = selected_addr.get("id", "")
        addr_name = str(selected_addr.get("name") or "").strip()
        addr_mobile = _mask_mobile(selected_addr.get("mobile", ""))
        addr_province = str(selected_addr.get("province_str") or "").strip()
        addr_city = str(selected_addr.get("city_str") or "").strip()
        addr_area = str(selected_addr.get("area_str") or "").strip()
        addr_detail = _mask_address(selected_addr.get("address", ""))

        sender.reply(f"📍 收货人: {addr_name}\n📱 手机: {addr_mobile}\n🏠 地址: {addr_province}{addr_city}{addr_area}{addr_detail}")
        sender.reply("📋 收货地址确认\n回复【Y】使用此地址下单\n回复 q 取消")
        addr_confirm = get_user_choice("", 120000, True)
        if not addr_confirm:
            return
        if str(addr_confirm).strip().upper() != "Y":
            sender.reply(format_message("操作取消", "已取消兑换", "info"))
            return

        sender.reply("🎁 正在创建兑换订单，请稍候...")
        create_result = create_order(token, addr_id, product_id, product_sku, num=1)
        if not create_result or create_result.get("code") != 1:
            err_msg = create_result.get("message", "创建订单失败") if isinstance(create_result, dict) else "网络错误"
            sender.reply(format_message("下单失败", f"创建兑换订单失败: {err_msg}", "error"))
            return

        order_data = create_result.get("data") or {}
        order_number = str(order_data.get("order_number") or "").strip()
        pay_status = str(order_data.get("pay_status") or "").strip()
        if not order_number:
            sender.reply(format_message("下单异常", "订单号为空，请联系管理员处理", "error"))
            return

        success_lines = ["=====兑换成功====="]
        success_lines.append("✅ 订单创建成功")
        success_lines.append(f"📋 订单号: {order_number}")
        success_lines.append(f"💰 支付积分: {product_points}")
        if product_price:
            success_lines.append(f"💵 商品价格: ¥{product_price}")
        success_lines.append(f"🎁 商品: {product_title}")
        success_lines.append(f"👤 收货人: {addr_name}")
        success_lines.append(f"📱 手机: {addr_mobile}")
        success_lines.append(f"🏠 地址: {addr_province}{addr_city}{addr_area}{addr_detail}")
        if pay_status == "1":
            success_lines.append("💳 支付状态: 积分已扣除")
        success_lines.append("回复【匠心物流】查看物流")
        success_lines.append("回复【匠心兑换】继续兑换")
        sender.reply("\n".join(success_lines))

    except Exception as e:
        sender.reply(format_message("兑换错误", f"积分兑换失败: {str(e)}", "error"))


def jxzh_batch_exchange():
    """批量兑换：选择多个账号 + 同一商品，一键下单"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送「{jxzh_signcommand}」绑定", "error"))
        return

    if len(accounts) < 2:
        sender.reply(format_message("提示", "仅有1个账号，请直接使用「匠心兑换」", "info"))
        return

    try:
        choice = _show_accounts_selection(accounts, "批量兑换-选择账号")
        if not choice:
            return
        try:
            selections = parse_selection(choice, len(accounts))
        except ValueError as e:
            sender.reply(format_message("输入错误", str(e), "error"))
            return

        selected_accounts = [accounts[i - 1] for i in selections if isinstance(i, int)]
        if not selected_accounts:
            sender.reply(format_message("无可选账号", "没有匹配的账号", "error"))
            return

        today_time = datetime.now().strftime("%Y-%m-%d")
        valid_accounts = []
        skip_reasons = []
        for acc in selected_accounts:
            display = get_account_display_name(acc)
            account_vip = get_auth(acc)
            auth_status, _ = get_auth_status(account_vip, today_time)
            if "未授权" in auth_status or "已过期" in auth_status:
                skip_reasons.append(f"⚠️ {display}：未授权/已过期，跳过")
                continue
            token = jxzh_token_value_for_account(acc)
            if not token:
                skip_reasons.append(f"⚠️ {display}：无Token，跳过")
                continue
            valid_accounts.append((acc, token))

        if skip_reasons:
            sender.reply("\n".join(skip_reasons))
        if not valid_accounts:
            sender.reply(format_message("无有效账号", "所选账号均不可用", "error"))
            return

        sender.reply(f"✅ 共 {len(valid_accounts)} 个有效账号")
        first_token = valid_accounts[0][1]
        selected = _search_and_select_product(first_token)
        if not selected:
            return

        product_title = str(selected.get("title") or "未知商品").strip()
        product_points = _format_points(selected.get("points", "0"))

        sender.reply("⏳ 正在获取商品规格信息...")
        product_sku, sku_detail = resolve_exchange_product_sku(first_token, selected)
        product_id = str(selected.get("id") or "").strip()
        if not product_sku:
            sender.reply(format_message("商品信息异常", "无法获取该商品的规格ID，请稍后重试", "error"))
            return
        if sku_detail and sku_detail.get("id"):
            product_id = str(sku_detail.get("id")).strip() or product_id

        confirm_lines = [
            "=====确认批量兑换=====",
            f"🎁 商品: {product_title}",
            f"💰 所需积分: {product_points}/个",
            f"📦 账号数: {len(valid_accounts)} 个",
            f"💰 总消耗: {product_points} × {len(valid_accounts)}",
            "-------------------",
            "将为每个账号使用其默认收货地址下单",
            "回复【Y】确认批量兑换",
            "回复 q 取消",
        ]
        sender.reply("\n".join(confirm_lines))

        confirm = get_user_choice("", 120000, True)
        if not confirm or str(confirm).strip().upper() != 'Y':
            sender.reply(format_message("已取消", "已取消批量兑换", "info"))
            return

        sender.reply(f"🎁 正在为 {len(valid_accounts)} 个账号批量下单...")
        success_count = 0
        fail_count = 0
        result_details = []

        for acc, token in valid_accounts:
            display = get_account_display_name(acc)
            addr_list = get_address_list(token)
            if not addr_list:
                result_details.append(f"❌ {display}：无收货地址")
                fail_count += 1
                continue

            default_addr = next((a for a in addr_list if str(a.get('is_default') or '') == '1'), addr_list[0])
            addr_id = default_addr.get('id', '')

            create_result = create_order(token, addr_id, product_id, product_sku, num=1)
            if create_result and create_result.get('code') == 1:
                order_data = create_result.get('data') or {}
                order_number = str(order_data.get('order_number') or '').strip()
                result_details.append(f"✅ {display}：成功（{order_number}）")
                success_count += 1
            else:
                err_msg = create_result.get('message', '失败') if isinstance(create_result, dict) else '网络错误'
                result_details.append(f"❌ {display}：{err_msg}")
                fail_count += 1

        final_lines = [
            "=====批量兑换完成=====",
            f"🎁 商品: {product_title}",
            f"✅ 成功: {success_count} 个",
        ]
        if fail_count:
            final_lines.append(f"❌ 失败: {fail_count} 个")
        final_lines.append("-------------------")
        final_lines.extend(result_details)
        final_lines.append("===================")
        sender.reply("\n".join(final_lines))

    except Exception as e:
        sender.reply(format_message("批量兑换错误", f"操作失败: {str(e)}", "error"))


def jxzh_logistics():
    """查询待收货订单物流"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {jxzh_signcommand} 绑定", "error"))
        return

    try:
        if len(accounts) == 1:
            detail = jxzh_logistics_detail_lines(accounts[0])
            sender.reply("=====匠心物流=====\n" + "\n".join(detail) + "\n===================")
            return

        lines = ["匠心物流查询", "0. 全部账号"]
        for i, account in enumerate(accounts, 1):
            token = jxzh_token_value_for_account(account)
            userinfo = get_task_userinfo(token) if token else None
            login_name = get_account_display_name(account, userinfo)
            lines.append(f"{i}. {login_name}")
        lines.append("回复序号查看物流，回复 q 退出")
        sender.reply("\n".join(lines))

        choice = get_user_choice("", 120000, True)
        if not choice:
            return

        try:
            idx = int(choice)
        except ValueError:
            sender.reply(format_message("输入错误", "请输入列表中的数字序号", "error"))
            return
        if idx < 0 or idx > len(accounts):
            sender.reply(format_message("输入无效", f"请输入 0～{len(accounts)} 之间的数字", "error"))
            return

        if idx == 0:
            batch_lines = ["=====匠心物流=====", "全部账号"]
            for j, account in enumerate(accounts, 1):
                batch_lines.append("")
                batch_lines.append(f"[{j}]")
                batch_lines.extend(jxzh_logistics_detail_lines(account))
            batch_lines.append("===================")
            sender.reply("\n".join(batch_lines))
            return

        account = accounts[idx - 1]
        detail = jxzh_logistics_detail_lines(account)
        sender.reply("=====匠心物流=====\n" + "\n".join(detail) + "\n===================")

    except Exception as e:
        sender.reply(format_message("物流查询错误", f"查询失败: {str(e)}", "error"))


def build_manage_account_cards(accounts: list, today_time: str) -> str:
    lines = ["=====匠心管理====="]
    for index, account in enumerate(accounts, 1):
        account_vip = get_auth(account)
        auth_status, auth_time = get_auth_status(account_vip, today_time)
        token = jxzh_token_value_for_account(account)
        userinfo = get_task_userinfo(token) if token else None
        login_mobile = get_account_display_name(account, userinfo)
        lines.append(f"[{index}] ")
        lines.append(f"  账号：{login_mobile}")
        lines.append(f"  状态：{auth_status}")
        if auth_time and auth_time != '无':
            lines.append(f"  到期：{auth_time}")
        lines.append("-------------------")
    lines.append("[0] 所有账号")
    lines.append("[9999] 未授权账号")
    lines.append("支持: 1,3,5 或 1-5")
    lines.append("回复序号选择操作（q退出）")
    lines.append("===================")
    return "\n".join(lines)


def resolve_selected_accounts(choice, accounts: list) -> list:
    selections = parse_selection(choice, len(accounts))
    if selections == ['0']:
        return accounts[:]
    if selections == ['9999']:
        return [account for account in accounts if not is_authorized(account)]
    return [accounts[index - 1] for index in selections]


def format_batch_target_label(accounts: list) -> str:
    accounts = dedupe_phones(accounts)
    if not accounts:
        return '账号'
    first_account = accounts[0]
    token = jxzh_token_value_for_account(first_account)
    userinfo = get_task_userinfo(token) if token else None
    first_label = get_account_display_name(first_account, userinfo)
    if len(accounts) == 1:
        return first_label
    return f"{first_label} 等{len(accounts)}个账号"


def batch_authorize_accounts(accounts: list, months: int, today_time: str):
    accounts = dedupe_phones(accounts)
    success_count = 0
    fail_count = 0
    extend_days = months * jxzh_auth_days

    for account in accounts:
        try:
            account_vip = get_auth(account)
            if account_vip and account_vip > today_time:
                current_expire = datetime.strptime(account_vip, "%Y-%m-%d")
                new_expire = current_expire + timedelta(days=extend_days)
            else:
                new_expire = datetime.now() + timedelta(days=extend_days)
            expire_date = new_expire.strftime("%Y-%m-%d")
            save_auth(account, expire_date)
            token = jxzh_token_value_for_account(account)
            phone = mask_phone(account) if len(account) >= 11 else account
            Addenvs(osname=jxzh_osname, value=token, account=account, phone=phone, expire_time=expire_date)
            success_count += 1
        except Exception as e:
            print(f"授权账号 {account} 失败: {e}")
            fail_count += 1

    return success_count, fail_count


def build_batch_authorize_result(project: str, target_label: str, account_count: int, months: int, success_count: int, fail_count: int, extra_lines=None) -> str:
    lines = [
        "=====批量授权完成=====",
        f"🎫 商品: {project}",
        f"👤 目标: {target_label}",
        f"📦 账号数: {account_count}个",
        f"✅ 成功：{success_count} 个",
        f"❌ 失败：{fail_count} 个",
        f"⏰ 时长：{months} 月（每 {jxzh_auth_days} 天计 1 月）",
    ]
    for line in (extra_lines or []):
        if line:
            lines.append(str(line))
    lines.append("===================")
    return "\n".join(lines)


def jxzh_batch_zf(project: str, months_int: int, accounts: list, today_time: str):
    accounts = dedupe_phones(accounts)
    if not accounts:
        sender.reply(format_message("未绑定账号", "没有可授权的账号", "error"))
        return False

    account_count = len(accounts)
    target_label = format_batch_target_label(accounts)
    money = Decimal(months_int) * jxzhVipmoney * account_count

    if money == 0:
        success_count, fail_count = batch_authorize_accounts(accounts, months_int, today_time)
        sender.reply(
            build_batch_authorize_result(
                project,
                target_label,
                account_count,
                months_int,
                success_count,
                fail_count,
                [f"💰 金额：免费"],
            )
        )
        return fail_count == 0 and success_count > 0

    zsm, use_ma_pay, ma_pay_config = jxzh_get_payment_config()
    usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
    zfcoin = int(jxzhcoin) * int(months_int) * account_count if jxzhcoin else 0
    opt_points = bool(jxzhcoin and int(jxzhcoin) > 0)
    opt_ma = bool(use_ma_pay and ma_pay_config)
    opt_zsm = bool(zsm and str(zsm).strip())

    if not opt_points and not opt_ma and not opt_zsm:
        sender.reply(format_message(
            "配置错误",
            "付费授权需至少配置一种支付方式：\n• 填写「积分支付」\n或开启有效「使用码支付」并完成卡密系统码支付配置\n或填写「赞赏码链接」",
            "error"
        ))
        return False

    pay_menu = (
        "=====批量授权支付=====\n"
        f"🎫 商品: {project}\n"
        f"👤 目标: {target_label}\n"
        f"📦 账号数: {account_count}个\n"
        f"⏰ 授权时长: {months_int}月\n"
        f"💰 总金额: {money}元"
    )
    option_num = 1
    options_map = {}

    if opt_points:
        pay_menu += f"\n[{option_num}] 积分支付\n   🎯 需 {zfcoin} 积分（{months_int}月 × {account_count}个）\n   💫 当前积分: {usercoin}"
        options_map[str(option_num)] = 'points'
        option_num += 1
    if opt_ma:
        pay_menu += f"\n[{option_num}] 码支付\n   💰 {money}元 / {account_count}个账号"
        options_map[str(option_num)] = 'ma'
        option_num += 1
    if opt_zsm:
        pay_menu += f"\n[{option_num}] 赞赏码支付\n   💰 {money}元 / {account_count}个账号（微信扫码赞赏或收款）"
        options_map[str(option_num)] = 'wechat'
        option_num += 1

    pay_menu += "\n------------------\n回复对应数字\n回复'q'退出\n=================="
    sender.reply(pay_menu)
    choice = get_user_choice("", 60000, True)
    if not choice:
        return False

    selected_pay = options_map.get(choice)
    if selected_pay == 'wechat' and opt_zsm:
        if sender.atWaitPay():
            sender.reply(format_message("支付繁忙", "当前有人正在支付,请稍后再试！", "warning"))
            return False
        pay_msg = f"""=====微信扫码支付====
🎫 商品: {project}
👤 目标: {target_label}
📦 账号数: {account_count}个
📅 时长: {months_int}月
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
        sender.reply(pay_msg)
        sender.replyImage(zsm)
        ddzf = sender.waitPay("q", 100 * 1000)
        if str(ddzf) == 'q':
            sender.reply(format_message("已取消", "已取消支付", "info"))
            return False
        payment_result = jxzh_parse_payment_result(ddzf)
        if not payment_result:
            return False
        Money, Time, From = payment_result
        if float(Money) < float(money):
            sender.reply(format_message(
                "支付金额错误",
                f"应付: {money}元\n实付: {Money}元\n{f'付款人: {From}' if From else ''}\n\n❗ 请联系管理员处理退款！",
                "error"
            ))
            return False
        success_count, fail_count = batch_authorize_accounts(accounts, months_int, today_time)
        sender.reply(
            build_batch_authorize_result(
                project,
                target_label,
                account_count,
                months_int,
                success_count,
                fail_count,
                [
                    f"💰 实付：{Money}元",
                    f"⏰ 时间：{Time}",
                    f"👤 付款人：{From}" if From else "",
                ],
            )
        )
        return fail_count == 0 and success_count > 0

    if selected_pay == 'ma' and opt_ma and ma_pay_config:
        out_trade_no = f"JX{int(time.time())}{userid}"
        params = {
            'pid': ma_pay_config['pid'],
            'type': ma_pay_config['type'].split(',')[0],
            'out_trade_no': out_trade_no,
            'name': f"{senderID}-匠心批量授权-{str(money)}",
            'money': str(money),
            'notify_url': ma_pay_config['notify_url'],
            'return_url': ma_pay_config['return_url'],
            'param': userid
        }
        params = {k: v for k, v in params.items() if v}
        sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode('utf-8')).hexdigest().lower()
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        gateway = ma_pay_config['gateway']
        if gateway.endswith('/'):
            gateway = gateway[:-1]
        mapi_url = f"{gateway}/mapi.php"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
        if response.status_code != 200:
            sender.reply(format_message("支付失败", f"创建支付订单失败，HTTP状态码: {response.status_code}", "error"))
            return False
        try:
            result = response.json()
        except Exception:
            sender.reply(format_message("支付失败", "创建支付订单失败，返回数据格式错误", "error"))
            return False
        if result.get('code', 0) != 1:
            msg = result.get('msg', '未知状态')
            sender.reply(format_message("支付失败", f"创建订单失败: {msg}", "error"))
            return False
        payurl = result.get('payurl', '')
        if not payurl:
            sender.reply(format_message("支付失败", "未获取到支付链接", "error"))
            return False
        qrcode_url = generate_qrcode(payurl)
        pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
        if qrcode_url:
            send_qrcode_image(sender, qrcode_url, pay_type)
        else:
            sender.reply(f"请点击链接完成支付:\n{payurl}")
        for _ in range(60):
            check_url = gateway
            if '/xpay/epay/api.php' not in check_url:
                check_url = f"{check_url.rstrip('/')}/xpay/epay/api.php"
            check_params = {
                'act': 'order',
                'pid': ma_pay_config['pid'],
                'key': ma_pay_config['key'],
                'out_trade_no': out_trade_no
            }
            try:
                check_resp = requests.get(check_url, params=check_params, timeout=10)
                check_result = check_resp.json()
                if check_result.get('code') == 1 and check_result.get('status') == 1:
                    success_count, fail_count = batch_authorize_accounts(accounts, months_int, today_time)
                    sender.reply(
                        build_batch_authorize_result(
                            project,
                            target_label,
                            account_count,
                            months_int,
                            success_count,
                            fail_count,
                            [
                                f"💰 金额：{money}元",
                                "💳 支付方式：码支付",
                            ],
                        )
                    )
                    return fail_count == 0 and success_count > 0
            except Exception as e:
                print(f"查询订单状态出错: {str(e)}")
            result = sender.listen(5000)
            if result == 'q' or result == 'Q':
                sender.reply("✅ 已取消支付")
                return False
        sender.reply("❌ 支付超时,请重新发起支付!")
        return False

    if selected_pay == 'points' and jxzhcoin and int(jxzhcoin) > 0:
        if int(usercoin) < zfcoin:
            sender.reply(format_message("积分不足", f"当前积分: {usercoin}\n需要积分: {zfcoin}", "error"))
            return False
        sender.reply(
            f"💫 批量积分支付确认\n👤 目标: {target_label}\n📦 账号数: {account_count}个\n💰 消耗积分: {zfcoin}\n⏰ 授权时长: {months_int}月\n------------------\n确认请回复【y】\n取消请回复【n】"
        )
        if not yesornos():
            sender.reply(format_message("已取消支付", "操作已取消", "info"))
            return False
        new_balance = int(usercoin) - zfcoin
        middleware.bucketSet('dd_sign_points', userid, str(new_balance))
        success_count, fail_count = batch_authorize_accounts(accounts, months_int, today_time)
        sender.reply(
            build_batch_authorize_result(
                project,
                target_label,
                account_count,
                months_int,
                success_count,
                fail_count,
                [
                    f"💫 扣除积分：{zfcoin}",
                    f"💰 剩余积分：{new_balance}",
                ],
            )
        )
        return fail_count == 0 and success_count > 0

    sender.reply(format_message("输入无效", "请输入正确的选项", "error"))
    return False


def batch_delete_accounts(accounts: list):
    success_count = 0
    fail_count = 0

    for account in accounts:
        try:
            del_account(account, userid, panel_config_value, jxzh_osname)
            success_count += 1
        except Exception as e:
            print(f"删除账号 {account} 失败: {e}")
            fail_count += 1

    return success_count, fail_count


def prompt_months_input(title: str):
    sender.reply(
        f"""====={title}=====
请输入授权月数（例：1）
每 1 月 = 插件配置的「授权天数」
-------------------
回复序号选择操作（q退出）
==================="""
    )
    value = get_user_choice("", 120000, True)
    if not value:
        return None
    try:
        months = int(value)
    except ValueError:
        sender.reply("❌ 月数必须是数字!")
        return None
    if months <= 0:
        sender.reply("❌ 月数必须大于0!")
        return None
    return months


def prompt_batch_manage_action(selected_accounts: list) -> str:
    sender.reply(
        f"""=====批量账号操作=====
已选账号：{len(selected_accounts)} 个
[1] 批量授权
[2] 批量删除
[3] 取消返回
-------------------
回复序号选择操作（q退出）
==================="""
    )
    return get_user_choice("", 120000, True)


# ==================== 管理功能 ====================

def jxzh_manage():
    """账号管理主函数"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {jxzh_signcommand} 绑定", "error"))
        return

    try:
        save_user_phones(accounts, userid)
        today_time = datetime.now().strftime("%Y-%m-%d")
        sender.reply(build_manage_account_cards(accounts, today_time))

        inputmessage = get_user_choice("", 120000, True)
        if not inputmessage:
            return

        try:
            selected_accounts = resolve_selected_accounts(inputmessage, accounts)
        except ValueError as e:
            sender.reply(format_message("输入错误", str(e), "error"))
            return

        if not selected_accounts:
            sender.reply("=====暂无可选账号=====\n当前没有匹配的账号\n===================")
            return

        if len(selected_accounts) == 1:
            account = selected_accounts[0]
            accountVip = get_auth(account)
            token = jxzh_token_value_for_account(account)
            userinfo = get_task_userinfo(token) if token else None
            login_mobile = get_account_display_name(account, userinfo)
            auth_status, auth_time = get_auth_status(accountVip, today_time)
            account_info = f"""=====当前账号=====
📱 {login_mobile}
🔐 {auth_status}
{f'📅 {auth_time}' if auth_time and auth_time != '无' else ''}
-------------------
[1] 授权续期
[2] 删除账号
-------------------
回复序号选择操作（q退出）
==================="""
            sender.reply(account_info)

            single_choice = get_user_choice("", 120000, True)
            if not single_choice:
                return

            if single_choice == '2':
                confirm_msg = """=====删除账号=====
确定删除？不可恢复。
[1] 确认删除
[2] 取消返回
-------------------
回复序号选择操作（q退出）
==================="""
                sender.reply(confirm_msg)
                choice = get_user_choice("", 120000, True)
                if not choice:
                    return
                if choice == '1':
                    del_account(account, userid, panel_config_value, jxzh_osname)
                    sender.reply("=====删除成功=====\n账号删除成功!\n===================")
                    return
                sender.reply("=====已取消=====\n已取消删除\n===================")
                return

            if single_choice == '1':
                months = prompt_months_input('授权续期')
                if months is None:
                    return
                token = jxzh_token_value_for_account(account)
                jxzh_zf('匠心授权', months, accountVip, token, account, account)
                return

            sender.reply("=====输入错误=====\n请输入正确的选项\n===================")
            return

        batch_choice = prompt_batch_manage_action(selected_accounts)
        if not batch_choice or batch_choice == '3':
            sender.reply("=====已取消=====\n已取消批量操作\n===================")
            return

        if batch_choice == '1':
            months = prompt_months_input('批量授权')
            if months is None:
                return
            jxzh_batch_zf('匠心批量授权', months, selected_accounts, today_time)
            return

        if batch_choice == '2':
            sender.reply(
                f"""=====批量删除=====
即将删除 {len(selected_accounts)} 个账号
[1] 确认删除
[2] 取消返回
-------------------
回复序号选择操作（q退出）
==================="""
            )
            confirm_choice = get_user_choice("", 120000, True)
            if not confirm_choice:
                return
            if confirm_choice != '1':
                sender.reply("=====已取消=====\n已取消批量删除\n===================")
                return
            success_count, fail_count = batch_delete_accounts(selected_accounts)
            sender.reply(
                f"""=====批量删除完成=====
✅ 成功：{success_count} 个
❌ 失败：{fail_count} 个
==================="""
            )
            return

        sender.reply("=====输入错误=====\n请输入正确的选项\n===================")

    except Exception as e:
        sender.reply(f"=====账号处理错误=====\n账号列表处理失败\n错误: {str(e)}\n===================")


# ==================== 管理员授权功能 ====================

def jxzh_admin_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return

    auth_menu = """=====匠心授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 清理过期授权
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(auth_menu)

    xz = sender.listen(60000)

    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出授权管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return

    if xz == '1':
        users = middleware.bucketAllKeys(BUCKET_USER)
        if not users:
            sender.reply("❌ 未找到任何绑定的匠心账号")
            return

        sender.reply("""=====请输入授权天数=====
------------------
回复数字设置天数
回复"q"退出操作
==================""")

        sjts = sender.listen(60000)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("✅ 已取消授权")
            return
        elif sjts is None:
            sender.reply("⏰ 操作超时,已退出")
            return

        try:
            sjts = int(sjts)
        except Exception:
            sender.reply("❌ 天数必须是数字!")
            return

        success_count = 0
        fail_count = 0
        today_time = datetime.now().strftime("%Y-%m-%d")

        for user in users:
            accounts = get_user_phones(user)
            for account in accounts:
                try:
                    accountVip = get_auth(account)
                    if accountVip and accountVip > today_time:
                        sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                        new_sqsj = sqsj + timedelta(days=sjts)
                    else:
                        new_sqsj = datetime.now() + timedelta(days=sjts)
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    save_auth(account, new_sqsj)
                    token = jxzh_token_value_for_account(account)
                    phone = mask_phone(account) if len(account) >= 11 else account
                    Addenvs(osname=jxzh_osname, value=token, account=account, phone=phone, expire_time=new_sqsj)
                    success_count += 1
                except Exception:
                    fail_count += 1

        result_msg = f"""=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
        sender.reply(result_msg)
        return

    if xz == '2':
        user_guide = """======账号授权======
请输入需要授权的用户ID
(发送myuid可获取ID)
------------------
回复"q"退出操作
=================="""
        sender.reply(user_guide)

        target_uid = sender.listen(60000)
        if target_uid == 'q' or target_uid == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif target_uid is None:
            sender.reply("⏰ 操作超时,已退出")
            return

        accounts = get_user_phones(target_uid)
        if not accounts:
            sender.reply(f"❌ 未找到 {target_uid} 的账号信息")
            return

        today_time = datetime.now().strftime("%Y-%m-%d")
        account_list = "=======账号列表======\n[0] 授权所有账号\n------------------"

        for i, account in enumerate(accounts, 1):
            accountVip = get_auth(account)
            vip_status = accountVip if accountVip else '未授权'
            account_list += f"\n[{i}] 账号: {account}\n    授权至: {vip_status}\n------------------"

        account_list += "\n回复数字选择账号\n回复'q'退出\n=================="
        sender.reply(account_list)

        xz = sender.listen(60000)
        if xz == 'q' or xz == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif xz is None:
            sender.reply("⏰ 操作超时,已退出")
            return

        try:
            xz = int(xz)
            if xz < 0 or (xz > len(accounts) and xz != 0):
                sender.reply(f"❌ 请输入 0-{len(accounts)} 之间的数字")
                return
        except ValueError:
            sender.reply("❌ 请输入正确的数字")
            return

        auth_guide = """=====设置授权天数=====
请输入要授权的天数
------------------
回复数字设置天数
回复"q"退出操作
=================="""
        sender.reply(auth_guide)

        sjts = sender.listen(60000)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("✅ 已取消授权")
            return
        elif sjts is None:
            sender.reply("⏰ 操作超时,已退出")
            return

        try:
            sjts = int(sjts)
            if sjts <= 0:
                sender.reply("❌ 授权天数必须大于0!")
                return
        except ValueError:
            sender.reply("❌ 天数必须是数字!")
            return

        success_count = 0
        fail_count = 0
        target_accounts = accounts if xz == 0 else [accounts[xz - 1]]

        for account in target_accounts:
            try:
                accountVip = get_auth(account)
                if accountVip and accountVip > today_time:
                    sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                    new_sqsj = sqsj + timedelta(days=sjts)
                else:
                    new_sqsj = datetime.now() + timedelta(days=sjts)
                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                save_auth(account, new_sqsj)
                token = jxzh_token_value_for_account(account)
                phone = mask_phone(account) if len(account) >= 11 else account
                Addenvs(osname=jxzh_osname, value=token, account=account, phone=phone, expire_time=new_sqsj)
                success_count += 1
            except Exception as e:
                print(f"授权账号 {account} 失败: {e}")
                fail_count += 1

        result_msg = f"""=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
        sender.reply(result_msg)
        return

    if xz == '3':
        sender.reply("⏳ 正在清理过期授权...")
        users = middleware.bucketAllKeys(BUCKET_USER)
        if not users:
            sender.reply("❌ 未找到任何账号")
            return

        today_time = datetime.now().strftime("%Y-%m-%d")
        cleared_count = 0

        for user in users:
            accounts = get_user_phones(user)
            for account in accounts:
                accountVip = get_auth(account)
                if accountVip and accountVip <= today_time:
                    middleware.bucketDel(BUCKET_AUTH, account)
                    qlid = allenvs(osname=jxzh_osname, account=str(account))
                    if qlid:
                        delenvs(id=qlid)
                    cleared_count += 1

        result_msg = f"""=====清理完成=====
🗑️ 已清理过期账号: {cleared_count} 个
=================="""
        sender.reply(result_msg)
        return

    sender.reply("❌ 输入的选项无效!")


# ==================== 清理功能 ====================

def jxzh_logoff():
    """匠心账号注销（列出账号，支持多选/全选）"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {jxzh_signcommand} 绑定", "error"))
        return

    today_time = datetime.now().strftime("%Y-%m-%d")
    menu_lines = ["=====匠心账号注销=====", "------------------"]
    for idx, account in enumerate(accounts, 1):
        display = mask_phone(account) if len(account) >= 11 else account
        accountVip = get_auth(account)
        auth_status, auth_time = get_auth_status(accountVip, today_time)
        expire_info = f'  📅{auth_time}' if auth_time and auth_time != '无' else ''
        menu_lines.append(f"[{idx}] {display}  {auth_status}{expire_info}")
    menu_lines.append("------------------")
    menu_lines.append("[0] 全部注销")
    menu_lines.append("⚠️ 注销后平台数据不可恢复")
    menu_lines.append("支持多选: 1,3 或 1-3（q退出）")
    menu_lines.append("==================")
    sender.reply('\n'.join(menu_lines))

    choice = get_user_choice("", 120000, True)
    if not choice:
        return

    if choice.strip() == '0':
        selected_accounts = accounts[:]
    else:
        try:
            indices = parse_selection(choice, len(accounts))
        except ValueError as e:
            sender.reply(format_message("输入错误", str(e), "error"))
            return
        selected_accounts = [accounts[i - 1] for i in indices]

    names = ', '.join(mask_phone(a) if len(a) >= 11 else a for a in selected_accounts)
    confirm_msg = f"""=====确认注销=====
⚠️ 即将注销 {len(selected_accounts)} 个账号:
{names}

注销后：
• 平台账号将被永久删除
• 积分、订单等数据不可恢复
• 本地绑定同步移除
------------------
[1] 确认注销
[2] 取消返回
------------------
回复序号（q退出）
=================="""
    sender.reply(confirm_msg)
    confirm = get_user_choice("", 60000, True)
    if not confirm or confirm != '1':
        sender.reply("✅ 已取消注销")
        return

    success_list = []
    fail_list = []
    for account in selected_accounts:
        display = mask_phone(account) if len(account) >= 11 else account
        token = jxzh_token_value_for_account(account)
        if not token:
            del_account(account, userid, panel_config_value, jxzh_osname)
            success_list.append(f"{display}（仅清除本地）")
            continue
        try:
            result = signed_post_with_fallback(
                LOGOFF_URL,
                headers=get_app_base_headers(),
                extra={'token': token},
                use_app_style=True,
                timeout=10,
            )
            if result.get('code') == 1:
                del_account(account, userid, panel_config_value, jxzh_osname)
                success_list.append(display)
            else:
                msg = result.get('message') or result.get('msg') or '未知错误'
                fail_list.append(f"{display}: {msg}")
        except Exception as e:
            print(f"注销异常[{account}]: {e}")
            fail_list.append(f"{display}: {e}")

    result_lines = ["=====注销结果====="]
    if success_list:
        result_lines.append(f"✅ 成功 {len(success_list)} 个:")
        for name in success_list:
            result_lines.append(f"  • {name}")
    if fail_list:
        result_lines.append(f"❌ 失败 {len(fail_list)} 个:")
        for msg in fail_list:
            result_lines.append(f"  • {msg}")
    result_lines.append("==================")
    sender.reply('\n'.join(result_lines))


def jxzh_clear():
    """清理账号授权（用户自主清理）"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", "未找到任何账号信息", "error"))
        return

    try:
        today_time = datetime.now().strftime("%Y-%m-%d")
        expired_accounts = [account for account in accounts if (get_auth(account) and get_auth(account) <= today_time)]

        if not expired_accounts:
            sender.reply("✅ 您没有过期的账号需要清理")
            return

        confirm_msg = f"""=====清理过期账号=====
📊 过期账号数量: {len(expired_accounts)} 个
------------------
确定要清理这些过期账号吗？
[y] 确认清理
[n] 取消操作
=================="""
        sender.reply(confirm_msg)

        choice = get_user_choice("", 120000, True)
        if not choice:
            return
        if choice in ['Y', 'y', '是']:
            for account in expired_accounts:
                try:
                    del_account(account, userid, panel_config_value, jxzh_osname)
                except Exception:
                    continue
            sender.reply(format_message("清理成功", f"已清理 {len(expired_accounts)} 个过期账号", "success"))
            return

        sender.reply(format_message("已取消", "已取消清理", "info"))

    except Exception as e:
        sender.reply(format_message("清理错误", f"清理失败: {str(e)}", "error"))


# ==================== CK批量登录功能 ====================

def jxzh_ck_login():
    """匠心CK批量登录，格式：备注#ck，每行一个"""
    sender.reply(
        "=====匠心CK登录=====\n"
        "📋 请发送CK信息，格式：\n"
        "备注#token\n"
        "------------------\n"
        "💡 支持多行批量提交，每行一个\n"
        "💡 备注可为手机号或自定义名称\n"
        "💡 token 从匠心平台获取\n"
        "💡 输入 q 取消\n"
        "=================="
    )
    raw_input = get_user_choice("", 120000, True)
    if not raw_input:
        return

    lines = [line.strip() for line in raw_input.replace('\r\n', '\n').split('\n') if line.strip()]
    if not lines:
        sender.reply(format_message("输入为空", "未检测到有效的CK信息", "error"))
        return

    ck_list = []
    for i, line in enumerate(lines, 1):
        if '#' not in line:
            sender.reply(format_message("格式错误", f"第{i}行格式不正确: {line}\n正确格式: 备注#token", "error"))
            return
        parts = line.split('#', 1)
        remark = parts[0].strip()
        token = parts[1].strip()
        if not remark or not token:
            sender.reply(format_message("格式错误", f"第{i}行备注或token为空\n正确格式: 备注#token", "error"))
            return
        ck_list.append({'remark': remark, 'token': token})

    sender.reply(f"⏳ 正在验证 {len(ck_list)} 个账号...")

    success_count = 0
    fail_count = 0
    result_lines = ["=====CK登录结果====="]

    for item in ck_list:
        remark = item['remark']
        token = item['token']
        user_info = get_user_info(token)
        if not user_info:
            result_lines.append(f"❌ {remark}：Token无效或已过期")
            fail_count += 1
            continue

        user_id = str(user_info.get('id') or '')
        mobile = str(user_info.get('mobile') or '').strip()
        username = decode_wechat_nickname(user_info.get('username') or '')
        account = mobile or user_id or remark

        add_account(account, userid)
        save_token(account, user_id, token, '')

        display_name = username if is_usable_display_name(username) else remark
        display_mobile = mask_phone(account) if len(account) >= 11 else account
        authorized = is_authorized(account)
        auth_label = '已授权' if authorized else '未授权'

        upload_status = ''
        if authorized:
            expire_date = get_auth(account)
            try:
                Addenvs(
                    osname=jxzh_osname,
                    value=token,
                    account=account,
                    phone=account,
                    expire_time=expire_date,
                )
                upload_status = ' | 已同步面板'
            except Exception:
                upload_status = ' | 同步失败'

        result_lines.append(f"✅ {display_name}({display_mobile}) [{auth_label}]{upload_status}")
        success_count += 1

    result_lines.append("-------------------")
    result_lines.append(f"✅ 成功：{success_count} 个")
    if fail_count:
        result_lines.append(f"❌ 失败：{fail_count} 个")
    result_lines.append("====================")
    sender.reply("\n".join(result_lines))


# ==================== 上传功能 ====================

def jxzh_upload():
    """上传已授权且未过期的账号数据到面板"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {jxzh_signcommand} 绑定", "error"))
        return

    authorized_accounts = [acc for acc in accounts if is_authorized(acc)]
    if not authorized_accounts:
        sender.reply(format_message("无可上传账号", "当前没有已授权且未过期的账号", "warning"))
        return

    success_count = 0
    fail_count = 0
    result_lines = ["=====匠心上传====="]

    for account in authorized_accounts:
        token = jxzh_token_value_for_account(account)
        if not token:
            display = mask_phone(account) if len(account) >= 11 else account
            result_lines.append(f"❌ {display}：无Token，请重新登录")
            fail_count += 1
            continue
        expire_date = get_auth(account)
        try:
            Addenvs(
                osname=jxzh_osname,
                value=token,
                account=account,
                phone=account,
                expire_time=expire_date,
            )
            display = mask_phone(account) if len(account) >= 11 else account
            result_lines.append(f"✅ {display}：已同步（到期 {expire_date}）")
            success_count += 1
        except Exception as e:
            display = mask_phone(account) if len(account) >= 11 else account
            result_lines.append(f"❌ {display}：同步失败（{e}）")
            fail_count += 1

    result_lines.append("-------------------")
    result_lines.append(f"✅ 成功：{success_count} 个")
    if fail_count:
        result_lines.append(f"❌ 失败：{fail_count} 个")
    result_lines.append("===================")
    sender.reply("\n".join(result_lines))


# ==================== 地址管理功能 ====================

def _format_address_card(addr, index=None) -> str:
    prefix = f"[{index}] " if index is not None else ""
    is_default = "【默认】" if str(addr.get('is_default') or '') == '1' else ''
    name = str(addr.get('name') or '').strip()
    mobile = str(addr.get('mobile') or '').strip()
    province = str(addr.get('province_str') or '').strip()
    city = str(addr.get('city_str') or '').strip()
    area = str(addr.get('area_str') or '').strip()
    region = str(addr.get('region_str') or '').strip()
    address = str(addr.get('address') or '').strip()
    house = str(addr.get('house_number') or '').strip()
    full_region = f"{province}{city}{area}"
    if region and region not in full_region:
        full_region += region
    detail = address
    if house:
        detail = f"{address} {house}"
    return f"{prefix}{name} {mobile} {is_default}\n    {full_region} {detail}"


def _select_account_for_address(accounts: list, today_time: str):
    if len(accounts) == 1:
        return accounts[0]
    lines = ["=====选择账号=====", "0. 取消返回"]
    for i, account in enumerate(accounts, 1):
        token = jxzh_token_value_for_account(account)
        userinfo = get_task_userinfo(token) if token else None
        login_name = get_account_display_name(account, userinfo)
        lines.append(f"{i}. {login_name}")
    lines.append("回复账号序号选择，回复 q 退出")
    sender.reply("\n".join(lines))
    choice = get_user_choice("", 120000, True)
    if not choice:
        return None
    try:
        idx = int(choice)
    except ValueError:
        sender.reply(format_message("输入错误", "请输入账号序号", "error"))
        return None
    if idx == 0:
        sender.reply("✅ 已取消")
        return None
    if idx < 1 or idx > len(accounts):
        sender.reply(format_message("输入无效", "账号序号超出范围", "error"))
        return None
    return accounts[idx - 1]


def _match_area_items(items: list, keyword: str) -> list:
    keyword = keyword.strip()
    if not keyword:
        return items
    exact = [it for it in items if it['name'] == keyword]
    if exact:
        return exact
    return [it for it in items if keyword in it['name'] or it['name'].replace('省', '').replace('市', '').replace('区', '').replace('县', '').replace('街道', '').replace('镇', '') == keyword.replace('省', '').replace('市', '').replace('区', '').replace('县', '').replace('街道', '').replace('镇', '')]


def _select_area_step(token, area_type, pid, label, show_all_threshold=20):
    sender.reply(f"⏳ 正在加载{label}列表...")
    raw_data = get_area_list(token, area_type, pid)
    items = flatten_area_list(raw_data)
    if not items:
        sender.reply(f"⚠️ 加载{label}列表失败，回复【r】重试，回复 q 取消")
        retry = get_user_choice("", 60000, True)
        if retry and retry.strip().lower() == 'r':
            sender.reply(f"⏳ 正在重新加载{label}列表...")
            raw_data = get_area_list(token, area_type, pid)
            items = flatten_area_list(raw_data)
        if not items:
            sender.reply(format_message("加载失败", f"无法获取{label}列表，请稍后重试", "error"))
            return None

    if len(items) <= show_all_threshold:
        lines = [f"=====选择{label}====="]
        for i, it in enumerate(items, 1):
            lines.append(f"[{i}] {it['name']}")
        lines.append(f"回复序号或输入{label}名称，回复 q 取消")
        sender.reply("\n".join(lines))
    else:
        sender.reply(f"请输入{label}名称（如：安徽、北京）\n回复 q 取消")

    choice = get_user_choice("", 120000, True)
    if not choice:
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(items):
            return items[idx]
        sender.reply(format_message("输入无效", f"序号超出范围（1-{len(items)}）", "error"))
        return None
    except ValueError:
        pass

    matched = _match_area_items(items, choice.strip())
    if len(matched) == 1:
        return matched[0]
    if len(matched) > 1:
        lines = [f"=====匹配到多个{label}====="]
        for i, it in enumerate(matched, 1):
            lines.append(f"[{i}] {it['name']}")
        lines.append("回复序号选择，回复 q 取消")
        sender.reply("\n".join(lines))
        sub_choice = get_user_choice("", 120000, True)
        if not sub_choice:
            return None
        try:
            sub_idx = int(sub_choice) - 1
            if 0 <= sub_idx < len(matched):
                return matched[sub_idx]
        except ValueError:
            pass
        sender.reply(format_message("输入无效", "请输入正确的序号", "error"))
        return None

    sender.reply(format_message("未匹配", f"未找到匹配的{label}「{choice}」，请重试", "error"))
    return None


def _address_add_flow(token):
    """单账号新增地址"""
    addr_info = _collect_address_info(token)
    if not addr_info:
        return

    full_region = f"{addr_info['province_str']}{addr_info['city_str']}{addr_info['area_str']}{addr_info['region_str']}"
    detail_str = addr_info['address']
    if addr_info['house_number']:
        detail_str = f"{addr_info['address']} {addr_info['house_number']}"

    confirm_lines = [
        "=====确认新增地址=====",
        f"👤 收货人: {addr_info['name']}",
        f"📱 手机号: {addr_info['mobile']}",
        f"🏠 地区: {full_region}",
        f"📍 地址: {detail_str}",
        "-------------------",
        "回复【Y】新增地址",
        "回复 q 取消",
    ]
    sender.reply("\n".join(confirm_lines))

    confirm = get_user_choice("", 120000, True)
    if not confirm or str(confirm).strip().upper() != 'Y':
        sender.reply(format_message("已取消", "未确认，已取消新增地址", "info"))
        return

    sender.reply("📝 正在保存地址...")
    result = create_address(
        token, addr_info['name'], addr_info['mobile'], addr_info['address'],
        addr_info['province_id'], addr_info['city_id'], addr_info['area_id'], addr_info['region_id'],
        addr_info['province_str'], addr_info['city_str'], addr_info['area_str'], addr_info['region_str'],
        house_number=addr_info['house_number'], is_default='1',
    )
    if result.get('code') == 1:
        sender.reply(format_message("新增成功", f"收货地址已保存\n👤 {addr_info['name']} {addr_info['mobile']}\n🏠 {full_region} {detail_str}", "success"))
    else:
        err_msg = result.get('message', '未知错误') if isinstance(result, dict) else '网络错误'
        sender.reply(format_message("保存失败", f"新增地址失败: {err_msg}", "error"))


def _collect_address_info(token):
    """收集一份完整的地址信息（省市区街+详细地址+门牌号），返回 dict 或 None"""
    sender.reply("=====填写收货地址=====\n请输入收货人姓名（回复 q 取消）")
    name = get_user_choice("", 120000, True)
    if not name:
        return None
    name = name.strip()
    if not name:
        sender.reply(format_message("输入错误", "姓名不能为空", "error"))
        return None

    sender.reply("请输入手机号（回复 q 取消）")
    mobile = get_user_choice("", 120000, True)
    if not mobile:
        return None
    mobile = mobile.strip()
    if not mobile or len(mobile) < 11:
        sender.reply(format_message("输入错误", "请输入正确的手机号", "error"))
        return None

    province = _select_area_step(token, 1, '0', '省份')
    if not province:
        return None
    city = _select_area_step(token, 2, province['id'], '城市')
    if not city:
        return None
    area = _select_area_step(token, 3, city['id'], '区/县')
    if not area:
        return None
    region = _select_area_step(token, 4, area['id'], '街道/镇')
    if not region:
        return None

    sender.reply("请输入详细地址（如：xxx小区-x号楼）\n回复 q 取消")
    address_input = get_user_choice("", 120000, True)
    if not address_input:
        return None
    address_detail = address_input.strip()
    if not address_detail:
        sender.reply(format_message("输入错误", "详细地址不能为空", "error"))
        return None

    sender.reply("请输入门牌号（如：3栋1903）\n无门牌号可回复 0 跳过，回复 q 取消")
    house_input = get_user_choice("", 120000, True)
    if not house_input:
        return None
    house_number = '' if house_input.strip() == '0' else house_input.strip()

    return {
        'name': name, 'mobile': mobile,
        'province_id': province['id'], 'province_str': province['name'],
        'city_id': city['id'], 'city_str': city['name'],
        'area_id': area['id'], 'area_str': area['name'],
        'region_id': region['id'], 'region_str': region['name'],
        'address': address_detail, 'house_number': house_number,
    }


def _show_accounts_selection(accounts: list, title: str) -> str:
    lines = [f"====={title}====="]
    today_time = datetime.now().strftime("%Y-%m-%d")
    for i, account in enumerate(accounts, 1):
        token = jxzh_token_value_for_account(account)
        userinfo = get_task_userinfo(token) if token else None
        login_name = get_account_display_name(account, userinfo)
        account_vip = get_auth(account)
        auth_status, _ = get_auth_status(account_vip, today_time)
        lines.append(f"[{i}] {login_name}（{auth_status}）")
    lines.append("-------------------")
    lines.append("💡 操作说明:")
    lines.append("• 支持单选: 1")
    lines.append("• 支持范围: 1-4")
    lines.append("• 支持多选: 2,3,7")
    lines.append("• 混合模式: 1,3-5,7")
    lines.append("请输入要操作的账号编号:")
    lines.append("回复 q 退出")
    sender.reply("\n".join(lines))
    return get_user_choice("", 120000, True)


def _address_batch_flow(accounts: list):
    """批量给多个账号设置同一个收货地址"""
    choice = _show_accounts_selection(accounts, "批量设置地址")
    if not choice:
        return
    try:
        selections = parse_selection(choice, len(accounts))
    except ValueError as e:
        sender.reply(format_message("输入错误", str(e), "error"))
        return

    selected_accounts = [accounts[i - 1] for i in selections if isinstance(i, int)]
    if not selected_accounts:
        sender.reply(format_message("无可选账号", "没有匹配的账号", "error"))
        return

    valid_accounts = []
    for acc in selected_accounts:
        token = jxzh_token_value_for_account(acc)
        if token:
            valid_accounts.append((acc, token))
    if not valid_accounts:
        sender.reply(format_message("无有效账号", "所选账号均无 Token，请先登录", "error"))
        return

    sender.reply(f"📝 已选中 {len(valid_accounts)} 个账号，开始填写地址信息")
    first_token = valid_accounts[0][1]
    addr_info = _collect_address_info(first_token)
    if not addr_info:
        return

    full_region = f"{addr_info['province_str']}{addr_info['city_str']}{addr_info['area_str']}{addr_info['region_str']}"
    detail_str = addr_info['address']
    if addr_info['house_number']:
        detail_str = f"{addr_info['address']} {addr_info['house_number']}"

    confirm_lines = [
        "=====确认批量设置地址=====",
        f"👤 收货人: {addr_info['name']}",
        f"📱 手机号: {addr_info['mobile']}",
        f"🏠 地区: {full_region}",
        f"📍 地址: {detail_str}",
        f"📦 账号数: {len(valid_accounts)} 个",
        "-------------------",
        "回复【Y】确认批量设置",
        "回复 q 取消",
    ]
    sender.reply("\n".join(confirm_lines))
    confirm = get_user_choice("", 120000, True)
    if not confirm or str(confirm).strip().upper() != 'Y':
        sender.reply(format_message("已取消", "已取消批量设置地址", "info"))
        return

    sender.reply(f"📝 正在为 {len(valid_accounts)} 个账号设置地址...")
    success_count = 0
    fail_count = 0
    for acc, token in valid_accounts:
        display = get_account_display_name(acc)
        result = create_address(
            token, addr_info['name'], addr_info['mobile'], addr_info['address'],
            addr_info['province_id'], addr_info['city_id'], addr_info['area_id'], addr_info['region_id'],
            addr_info['province_str'], addr_info['city_str'], addr_info['area_str'], addr_info['region_str'],
            house_number=addr_info['house_number'], is_default='1',
        )
        if result.get('code') == 1:
            success_count += 1
        else:
            err_msg = result.get('message', '未知') if isinstance(result, dict) else '网络错误'
            print(f"账号 {display} 设置地址失败: {err_msg}")
            fail_count += 1

    result_lines = [
        "=====批量设置地址完成=====",
        f"✅ 成功: {success_count} 个",
    ]
    if fail_count:
        result_lines.append(f"❌ 失败: {fail_count} 个")
    result_lines.append(f"👤 收货人: {addr_info['name']}")
    result_lines.append(f"🏠 {full_region} {detail_str}")
    result_lines.append("===================")
    sender.reply("\n".join(result_lines))


def _address_delete_flow(token, address_list):
    if not address_list:
        sender.reply(format_message("无地址", "当前没有收货地址可删除", "warning"))
        return
    lines = ["=====删除收货地址====="]
    for i, addr in enumerate(address_list, 1):
        lines.append(_format_address_card(addr, i))
    lines.append("回复序号选择要删除的地址，回复 q 取消")
    sender.reply("\n".join(lines))

    choice = get_user_choice("", 120000, True)
    if not choice:
        return
    try:
        idx = int(choice) - 1
    except ValueError:
        sender.reply(format_message("输入错误", "请输入序号", "error"))
        return
    if idx < 0 or idx >= len(address_list):
        sender.reply(format_message("输入无效", "序号超出范围", "error"))
        return

    target = address_list[idx]
    target_name = str(target.get('name') or '').strip()
    target_mobile = str(target.get('mobile') or '').strip()
    sender.reply(f"确定删除地址？\n👤 {target_name} {target_mobile}\n回复【Y】删除，回复 q 取消")

    confirm = get_user_choice("", 120000, True)
    if not confirm or str(confirm).strip().upper() != 'Y':
        sender.reply(format_message("已取消", "已取消删除", "info"))
        return

    result = delete_address(token, target.get('id'))
    if result.get('code') == 1:
        sender.reply(format_message("删除成功", f"已删除地址: {target_name} {target_mobile}", "success"))
    else:
        err_msg = result.get('message', '未知错误') if isinstance(result, dict) else '网络错误'
        sender.reply(format_message("删除失败", f"删除地址失败: {err_msg}", "error"))


def jxzh_address():
    """收货地址管理"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {jxzh_signcommand} 绑定", "error"))
        return

    try:
        has_multi = len(accounts) > 1
        lines = ["=====匠心地址管理====="]
        lines.append("[1] 查看/新增/删除（单账号）")
        if has_multi:
            lines.append(f"[2] 批量设置地址（{len(accounts)}个账号）")
        lines.append("[0] 退出")
        lines.append("回复序号选择操作（q 退出）")
        sender.reply("\n".join(lines))

        top_action = get_user_choice("", 120000, True)
        if not top_action or top_action == '0':
            sender.reply("✅ 已退出地址管理")
            return

        if top_action == '2' and has_multi:
            _address_batch_flow(accounts)
            return

        if top_action == '1':
            today_time = datetime.now().strftime("%Y-%m-%d")
            account = _select_account_for_address(accounts, today_time)
            if not account:
                return

            token = jxzh_token_value_for_account(account)
            if not token:
                sender.reply(format_message("登录失效", "Token 已失效，请重新发送「匠心登录」绑定", "error"))
                return

            sender.reply("📍 正在加载收货地址...")
            address_list = get_address_list(token)

            if address_list:
                sub_lines = ["=====我的收货地址====="]
                for i, addr in enumerate(address_list, 1):
                    sub_lines.append(_format_address_card(addr, i))
                sub_lines.append("-------------------")
            else:
                sub_lines = ["=====我的收货地址=====", "📭 暂无收货地址", "-------------------"]

            sub_lines.append("[1] 新增地址")
            if address_list:
                sub_lines.append("[2] 删除地址")
            sub_lines.append("[0] 退出")
            sub_lines.append("回复序号选择操作（q 退出）")
            sender.reply("\n".join(sub_lines))

            action = get_user_choice("", 120000, True)
            if not action or action == '0':
                sender.reply("✅ 已退出地址管理")
                return
            if action == '1':
                _address_add_flow(token)
                return
            if action == '2' and address_list:
                _address_delete_flow(token, address_list)
                return
            sender.reply(format_message("输入无效", "请输入正确的选项", "error"))
            return

        sender.reply(format_message("输入无效", "请输入正确的选项", "error"))

    except Exception as e:
        sender.reply(format_message("地址管理错误", f"操作失败: {str(e)}", "error"))


def jxzh_batch_address():
    """批量设置地址（独立指令入口）"""
    accounts = get_user_phones(userid)
    if not accounts:
        sender.reply(format_message("未绑定账号", f"未找到任何账号信息\n💡 发送 {jxzh_signcommand} 绑定", "error"))
        return
    if len(accounts) < 2:
        sender.reply(format_message("提示", "仅有1个账号，请直接使用「匠心地址」新增", "info"))
        return
    _address_batch_flow(accounts)


# ==================== 教程功能 ====================

def jxzh_tutorial():
    """显示使用教程"""
    tutorial_msg = """=====匠心使用教程=====
------------------
📱 登录指令: 匠心登录
   用于扫码绑定账号

🔑 CK登录: 匠心CK
   批量CK登录，格式：备注#token
   支持多行批量提交

📊 查询指令: 匠心查询
   用于查看账号状态

🎁 兑换指令: 匠心兑换
   用于积分兑换商品（单账号）

🎁 批量兑换: 匠心批量兑换
   多账号一键兑换同一商品

📦 物流指令: 匠心物流
   用于查看待收货订单物流

⚙️ 管理指令: 匠心管理
   用于账号授权和删除

🔑 授权指令: 匠心授权
   管理员专用，用于批量授权

🚫 注销指令: 匠心注销
   注销平台账号（不可恢复）

🗑️ 清理指令: 匠心清理
   用于清理过期账号

📤 上传指令: 匠心上传
   上传已授权且未过期的账号到面板

📍 地址指令: 匠心地址
   管理收货地址（新增/删除）

📍 批量地址: 匠心批量地址
   多账号批量设置同一收货地址
------------------
💡 提示: 首次使用请先登录绑定账号
=================="""
    sender.reply(tutorial_msg)


# ==================== 主程序入口 ====================

# 获取用户触发文本（与顺丰等插件一致，由框架通过 sender 提供）
command = (sender.getMessage() or "").strip()

today_time = datetime.now().strftime("%Y-%m-%d")

if command in ['匠心登录', '登录匠心']:
    jxzh_login()
elif command in ['匠心CK']:
    jxzh_ck_login()
elif command in ['匠心查询', '查询匠心']:
    jxzh_query()
elif command in ['匠心物流', '物流匠心']:
    jxzh_logistics()
elif command in ['匠心兑换', '兑换匠心']:
    jxzh_exchange()
elif command in ['匠心批量兑换']:
    jxzh_batch_exchange()
elif command in ['匠心管理', '管理匠心']:
    jxzh_manage()
elif command in ['匠心授权']:
    jxzh_admin_auth()
elif command in ['匠心清理']:
    jxzh_clear()
elif command in ['匠心上传']:
    jxzh_upload()
elif command in ['匠心地址']:
    jxzh_address()
elif command in ['匠心批量地址']:
    jxzh_batch_address()
elif command in ['匠心注销']:
    jxzh_logoff()
elif command in ['匠心教程']:
    jxzh_tutorial()
else:
    sender.reply(format_message("未知命令", "未识别的指令，请发送 匠心教程 查看帮助", "error"))

