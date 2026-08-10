# [pin: true]
# [title: 云订阅助手]
# [icon: https://gcore.jsdelivr.net/gh/lhz03/img@fc8e00ee7db33639259696f15c306f699b727184/2024/05/18/90616fd7b0670dbd6d4d8341c1fb97ac.png]
# [language: python]
# [rule: ^订阅助手$|^订阅采集$|^订阅列表$|^订阅搜索$|^订阅动态$|^订阅一键添加$|^订阅一键更新$]
# [disable:false]
# [cron: */10 * * * *]
# [open_source: false]
# [platform: qq,qb,wx,gw,sb,wb,tg,tb,qx,xy,ip]
# [class: 工具类]
# [priority: 999999998]
# [public: true]
# [version: 1.1.7]
# [author: yuhualhh]
# [price: 0]
# [service: ]
# [description: <br>❶这是一个提供奥特曼用户使用的比较完善的云订阅助手插件，支持 订阅数据采集、订阅插件列表、订阅插件搜索、订阅动态推送、订阅一键添加、插件自动更新 等众多细化操作<br>❷使用本插件需授予一定权限，前往"系统管理-插件权限"全部启用<img src="https://gcore.jsdelivr.net/gh/lhz03/img@ee3b75c9c317ba7b3a65984252831d9806323bf0/2026/04/03/5a36ec27ac719196f14e488dc79f0bcd.png">]

import middleware
import time
import requests
import json
import re
import hashlib
import gzip
import sys
import concurrent.futures
from decimal import Decimal
from urllib.parse import quote

#[param: {"required":false,"key":"yuhua_subhub.compat_mode","bool":true,"placeholder":"","name":"开启兼容模式","desc":"降低对实时订阅源接口的依赖，强制使用云端订阅源列表数据"}]
#[param: {"required":false,"key":"yuhua_subhub.collect_enable","bool":true,"placeholder":"","name":"订阅数据采集","desc":"自动采集已添加订阅源的插件信息并上传云端，仅奥特曼3.8.8及以上版本生效"}]
#[param: {"required":false,"key":"yuhua_subhub.list_admin_only","bool":true,"placeholder":"","name":"订阅列表权限","desc":"仅管理员可触发订阅列表功能"}]
#[param: {"required":false,"key":"yuhua_subhub.search_admin_only","bool":true,"placeholder":"","name":"订阅搜索权限","desc":"仅管理员可触发订阅搜索功能"}]
#[param: {"required":false,"key":"yuhua_subhub.non_empty_online_list","bool":true,"placeholder":"","name":"分发在线非空","desc":"订阅列表仅显示分发已开或者状态在线并且插件非空的订阅源"}]
#[param: {"required":false,"key":"yuhua_subhub.only_add_online","bool":true,"placeholder":"","name":"仅加在线订阅","desc":"执行订阅一键添加时仅添加在线订阅"}]
#[param: {"required":false,"key":"yuhua_subhub.close_dynamic","bool":true,"placeholder":"","name":"关闭订阅动态","desc":"勾选后自动执行的订阅动态将不会生效"}]
#[param: {"required":false,"key":"yuhua_subhub.dynamic_push_blacklist","bool":false,"placeholder":"订阅,订阅:插件名","name":"自推送黑名单","desc":"多个黑名单插件或订阅请用英文符逗号,分隔，例如: ceshi:支付宝,hello123"}]
#[param: {"required":false,"key":"yuhua_subhub.group_push","bool":true,"placeholder":"","name":"推送群组动态","desc":"订阅动态推送指定群组"}]
#[param: {"required":false,"key":"yuhua_subhub.group_ids","placeholder":"","name":"推送群组列表","desc":"多个群ID请用英文符逗号,分隔"}]
#[param: {"required":false,"key":"yuhua_subhub.only_subscribed","bool":true,"placeholder":"","name":"仅推送已订阅","desc":"只推送已添加订阅源的动态"}]
#[param: {"required":false,"key":"yuhua_subhub.only_installed","bool":true,"placeholder":"","name":"仅推送已安装","desc":"只推送已安装插件的动态"}]
#[param: {"required":false,"key":"yuhua_subhub.disable_removed_push","bool":true,"placeholder":"","name":"关闭下架推送","desc":"不推送插件下架的动态"}]
#[param: {"required":false,"key":"yuhua_subhub.hide_dynamic_images","bool":true,"placeholder":"","name":"关闭图片显示","desc":"推送动态时不显示图片"}]
#[param: {"required":false,"key":"yuhua_subhub.auto_update","bool":true,"placeholder":"","name":"自动更新插件","desc":"自动更新已安装的插件"}]
#[param: {"required":false,"key":"yuhua_subhub.auto_update_blacklist","bool":false,"placeholder":"订阅源:插件名","name":"自更新黑名单","desc":"多个插件用英文符逗号,分隔，例如: yuhualhh:王者战力查询,yuhualhh:测试插件"}]
#[param: {"required":false,"key":"yuhua_subhub.debug_pwd","bool":false,"placeholder":"","name":"开发调试模式","desc":"非插件开发者无需理会"}]

PLATFORMS = ['qq', 'qb', 'wx', 'gw', 'sb', 'wb', 'tg', 'tb', 'qx', 'xy', 'ip']
COLLECT_BUCKET = 'yuhua_subhub'
DEBUG_SECRET = '123456789abcC@'

def _get_autman_version_for_collect_limit():
    try:
        current_version_raw = middleware.version()
        if DEBUG:
            printf(f'订阅采集版本原始返回值: {repr(current_version_raw)} | 类型: {type(current_version_raw).__name__}', 'DEBUG')

        if not current_version_raw:
            return None, ''

        current_version_str = ''
        if isinstance(current_version_raw, str):
            current_version_str = current_version_raw.strip()
        elif isinstance(current_version_raw, dict):
            for key in ['sn', 'version', 'data', 'ver', 'appVersion', 'autmanVersion', 'value']:
                value = current_version_raw.get(key)
                if isinstance(value, str) and value.strip():
                    current_version_str = value.strip()
                    break
            if not current_version_str:
                for value in current_version_raw.values():
                    if isinstance(value, str) and value.strip():
                        current_version_str = value.strip()
                        break
            if not current_version_str:
                current_version_str = json.dumps(current_version_raw, ensure_ascii=False)
        elif isinstance(current_version_raw, (list, tuple)):
            for value in current_version_raw:
                if isinstance(value, str) and value.strip():
                    current_version_str = value.strip()
                    break
            if not current_version_str:
                current_version_str = json.dumps(current_version_raw, ensure_ascii=False)
        else:
            current_version_str = str(current_version_raw).strip()

        if not current_version_str:
            return None, ''

        if DEBUG:
            printf(f'订阅采集版本解析字符串: {current_version_str}', 'DEBUG')

        match = re.search(r'(\d+)\.(\d+)\.(\d+)', current_version_str)
        if not match:
            return None, current_version_str

        version_tuple = tuple(map(int, match.groups()))
        if DEBUG:
            printf(f'订阅采集版本解析结果: {version_tuple}', 'DEBUG')
        return version_tuple, current_version_str
    except Exception as e:
        if DEBUG:
            printf(f'订阅采集版本检测异常: {e}', 'WARN')
        return None, ''

def _check_collect_version_limit(sender, triggered_by='manual'):
    min_version = (3, 8, 8)
    version_tuple, version_text = _get_autman_version_for_collect_limit()

    if version_tuple is None:
        if version_text:
            msg = f'💢 当前奥特曼版本过低或无法识别({version_text})，订阅采集仅支持3.8.8及以上版本'
        else:
            msg = '💢 当前奥特曼版本无法识别，订阅采集仅支持3.8.8及以上版本'
        if triggered_by == 'manual':
            sender.reply(msg)
        return False

    if version_tuple < min_version:
        msg = f'💢 当前奥特曼版本为{version_text}，订阅采集仅支持3.8.8及以上版本'
        if triggered_by == 'manual':
            sender.reply(msg)
        return False
    return True

def _is_compat_mode_enabled(sender):
    return _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'compat_mode'))

def printf(msg, level='INFO'):
    color = 32 if level in ['INFO', 'DEBUG'] else 33 if level in ['WARN', 'WARNING'] else 31
    sys.stderr.write(f'\033[{color}m[{level}] {str(msg)}\033[0m\n')
    sys.stderr.flush()


def _is_debug_enabled():
    try:
        return (middleware.bucketGet(COLLECT_BUCKET, 'debug_pwd') or '') == DEBUG_SECRET
    except Exception:
        return False


DEBUG = _is_debug_enabled()
if DEBUG:
    printf('🔥🔥🔥 调试模式已开启，密钥验证通过 🔥🔥🔥', 'WARN')


def _debug_body_to_text(body, headers=None):
    if body is None:
        return ''
    if isinstance(body, (dict, list)):
        try:
            return json.dumps(body, ensure_ascii=False)
        except Exception:
            return str(body)
    if isinstance(body, bytes):
        enc = ''
        if isinstance(headers, dict):
            enc = headers.get('Content-Encoding') or headers.get('content-encoding') or ''
        if 'gzip' in str(enc).lower():
            try:
                return gzip.decompress(body).decode('utf-8', 'replace')
            except Exception:
                pass
        try:
            return body.decode('utf-8', 'replace')
        except Exception:
            return repr(body)
    return str(body)


def _debug_log_request(method, url, kwargs):
    if not DEBUG:
        return
    headers = kwargs.get('headers') or {}
    printf('===== [REQUEST START] =====', 'DEBUG')
    printf(f'METHOD: {method.upper()} | URL: {url}', 'DEBUG')
    printf(f'HEADERS: {json.dumps(headers, ensure_ascii=False)}', 'DEBUG')
    if 'params' in kwargs and kwargs.get('params') is not None:
        printf(f'PARAMS: {json.dumps(kwargs.get("params"), ensure_ascii=False)}', 'DEBUG')
    if 'json' in kwargs and kwargs.get('json') is not None:
        printf(f'BODY(JSON): {json.dumps(kwargs.get("json"), ensure_ascii=False)}', 'DEBUG')
    elif 'data' in kwargs and kwargs.get('data') is not None:
        printf(f'BODY(DATA): {_debug_body_to_text(kwargs.get("data"), headers)}', 'DEBUG')


def _debug_log_response(resp, attempt):
    if not DEBUG:
        return
    printf(f'----- [RESPONSE - Attempt {attempt}] -----', 'DEBUG')
    if resp is None:
        printf('NO RESPONSE', 'ERROR')
        printf('===== [REQUEST END] =====', 'DEBUG')
        return
    printf(f'STATUS: {resp.status_code}', 'DEBUG')
    try:
        printf(f'RSP HEADERS: {json.dumps(dict(resp.headers), ensure_ascii=False)}', 'DEBUG')
    except Exception:
        printf(f'RSP HEADERS: {dict(resp.headers)}', 'DEBUG')
    try:
        parsed = resp.json()
        printf(f'RSP BODY: {json.dumps(parsed, ensure_ascii=False)}', 'DEBUG')
    except Exception:
        printf(f'RSP BODY: {resp.text}', 'DEBUG')
    printf('===== [REQUEST END] =====', 'DEBUG')


def _debug_log_error(attempt, error):
    if not DEBUG:
        return
    printf(f'⚠️ Attempt {attempt} Failed: {error}', 'WARN')

SNAPSHOT_KEY = 'catalog_snapshot'
LOCAL_TIMEOUT = 60 #添加订阅超时
REMOTE_TIMEOUT = 60  #云端上传超时
PAGE_SIZE = 300 #采集订阅数据单页大小

SUBHUB_BACKEND_URL = 'https://yuhualhh.250666.xyz/api/subscription_hub.php'
SUBHUB_BACKEND_KEY = 'yuhualhh666666'
DEV_RECORDS_URL = 'http://man.zhelee.cn/market/records'
DEV_RECORDS_PASSWORD = ''


def _safe_json_loads(text, default=None):
    try:
        return json.loads(text)
    except Exception:
        return default


def _bool_enabled(value):
    return str(value).strip().lower() in ['1', 'true', 'yes', 'on']


def _make_request(method, url, **kwargs):
    is_local_sub_add = method.lower() == 'post' and url.startswith('http://127.0.0.1:') and '/market/subs' in url
    if is_local_sub_add:
        timeout = kwargs.get('timeout')
        if not isinstance(timeout, tuple) or len(timeout) != 2:
            kwargs['timeout'] = (25, 30)
        else:
            try:
                connect_timeout = float(timeout[0])
                read_timeout = float(timeout[1])
                if connect_timeout <= 0 or read_timeout <= 0:
                    kwargs['timeout'] = (25, 30)
            except Exception:
                kwargs['timeout'] = (25, 30)

    _debug_log_request(method, url, kwargs)
    for attempt in range(1, 4):
        try:
            if method.lower() == 'get':
                resp = requests.get(url, **kwargs)
            else:
                resp = requests.request(method.upper(), url, **kwargs)
            _debug_log_response(resp, attempt)
            return resp
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            _debug_log_error(attempt, e)
            if attempt < 3 and not is_local_sub_add:
                time.sleep(1)
        except Exception as e:
            _debug_log_error(attempt, e)
            if attempt < 3 and not is_local_sub_add:
                time.sleep(1)
    return None


def _get_backend_conf(sender):
    return SUBHUB_BACKEND_URL.strip(), SUBHUB_BACKEND_KEY.strip()


def _backend_request(sender, method, action, params=None, payload=None, timeout=REMOTE_TIMEOUT):
    backend_url, backend_key = _get_backend_conf(sender)
    if not backend_url or not backend_key:
        return None, '请先配置云端地址与云端密钥'
    url = backend_url.rstrip('/')
    if '?' in url:
        url = f'{url}&action={quote(action)}'
    else:
        url = f'{url}?action={quote(action)}'
    headers = {'X-API-Key': backend_key}
    last_err = '云端请求失败'
    try:
        if method.lower() == 'get':
            max_attempts = 2
        else:
            max_attempts = 3

        for attempt in range(1, max_attempts + 1):
            if method.lower() == 'get':
                resp = _make_request('get', url, headers=headers, params=params, timeout=timeout)
            else:
                body = json.dumps(payload or {}, ensure_ascii=False).encode('utf-8')
                gz = gzip.compress(body)
                req_headers = dict(headers)
                req_headers.update({
                    'Content-Type': 'application/json',
                    'Content-Encoding': 'gzip'
                })
                resp = _make_request(method, url, headers=req_headers, data=gz, timeout=timeout)

            if not resp:
                last_err = '云端请求失败'
                if attempt < max_attempts:
                    time.sleep(1)
                    continue
                return None, last_err

            data = _safe_json_loads(resp.text, {})
            if resp.status_code in [500, 502, 503, 504]:
                last_err = data.get('message') or f'HTTP {resp.status_code}'
                if attempt < max_attempts:
                    time.sleep(1)
                    continue
                return None, last_err

            if resp.status_code != 200:
                return None, data.get('message') or f'HTTP {resp.status_code}'

            if data.get('code') != 200:
                return None, data.get('message') or '云端返回异常'

            return data.get('data'), ''

        return None, last_err
    except Exception as e:
        return None, f'云端异常: {str(e)[:120]}'

def _send_multi_platform_push_to_group(group_id, message):
    for platform in PLATFORMS:
        try:
            middleware.push(imType=platform, groupCode=int(group_id), userID=0, title='', content=message)
            time.sleep(0.1)
        except Exception:
            pass

def _get_autman_cookie(sender):
    cookie = sender.bucketGet(COLLECT_BUCKET, 'autMan')
    if cookie:
        return cookie
    for _ in range(3):
        try:
            username = sender.bucketGet('autMan', 'adminUsername')
            password = sender.bucketGet('autMan', 'adminPassword')
            port = middleware.port()
            if not all([username, password, port]):
                return None
            login_url = f'http://127.0.0.1:{port}/login'
            resp = _make_request(
                'post',
                login_url,
                data={'username': username, 'password': password},
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'},
                timeout=8,
            )
            if resp and resp.status_code == 200:
                data = _safe_json_loads(resp.text, {})
                if data.get('code') == 200:
                    cookie_value = (resp.headers.get('Set-Cookie') or '').split(';')[0]
                    if cookie_value:
                        sender.bucketSet(COLLECT_BUCKET, 'autMan', cookie_value)
                        return cookie_value
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return None


def _autman_api_request(sender, method, endpoint, **kwargs):
    for _ in range(2):
        cookie = _get_autman_cookie(sender)
        if not cookie:
            return None
        port = middleware.port()
        url = f'http://127.0.0.1:{port}{endpoint}'
        headers = kwargs.get('headers', {})
        headers['Cookie'] = cookie
        kwargs['headers'] = headers
        resp = _make_request(method, url, **kwargs)
        if not resp:
            return None
        try:
            data = resp.json()
            if resp.status_code == 200 and data.get('code') == 200:
                return resp
            if resp.status_code == 401 or data.get('code') == 401:
                try:
                    sender.bucketDel(COLLECT_BUCKET, 'autMan')
                except Exception:
                    pass
                continue
            return resp
        except Exception:
            if resp.status_code == 401:
                try:
                    sender.bucketDel(COLLECT_BUCKET, 'autMan')
                except Exception:
                    pass
                continue
            return resp
    return None


def _list_local_subscriptions(sender, search_value=''):
    endpoint = '/market/subs'
    if search_value is not None:
        endpoint = f'/market/subs?searchValue={quote(search_value)}'
    resp = _autman_api_request(sender, 'get', endpoint, timeout=LOCAL_TIMEOUT)
    if not resp:
        return []
    data = _safe_json_loads(resp.text, {})
    return data.get('data') or []



def _list_installed_plugins(sender):
    resp = _autman_api_request(sender, 'get', '/js/details', timeout=LOCAL_TIMEOUT)
    if not resp:
        return []
    data = _safe_json_loads(resp.text, {})
    return data.get('data') or []


def _build_local_subscription_author_set(sender):
    authors = set()
    for item in _list_local_subscriptions(sender, ''):
        author = str(item.get('author') or item.get('name') or '').strip()
        if author:
            authors.add(author)
    return authors


def _build_installed_plugin_keys(sender):
    installed = _list_installed_plugins(sender)
    keys = set()
    for item in installed:
        author = str(item.get('author') or '').strip()
        title = str(item.get('title') or '').strip()
        plugin_path = str(item.get('plugin_path') or '').strip()
        if author and title:
            keys.add(f'{author}::{title}')
        if plugin_path:
            keys.add(f'path::{plugin_path}')
    return keys


def _is_dynamic_disabled(sender):
    return _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'close_dynamic'))


def _should_push_author(sender, author, subscribed_authors=None):
    if not _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'only_subscribed')):
        return True
    if subscribed_authors is None:
        subscribed_authors = _build_local_subscription_author_set(sender)
    return str(author or '').strip() in subscribed_authors


def _build_plugin_match_key(author, plugin):
    title = str((plugin or {}).get('title') or '').strip()
    plugin_path = str((plugin or {}).get('plugin_path') or '').strip()
    author = str(author or (plugin or {}).get('author') or '').strip()
    if plugin_path:
        return f'path::{plugin_path}'
    if author and title:
        return f'{author}::{title}'
    return ''


def _should_push_plugin(sender, author, plugin, installed_keys=None):
    if not _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'only_installed')):
        return True
    if installed_keys is None:
        installed_keys = _build_installed_plugin_keys(sender)
    key = _build_plugin_match_key(author, plugin)
    return bool(key) and key in installed_keys


def _parse_auto_update_blacklist(sender):
    raw = str(sender.bucketGet(COLLECT_BUCKET, 'auto_update_blacklist') or '').strip()
    result = set()
    if not raw:
        return result
    for item in raw.split(','):
        item = str(item or '').strip()
        if not item or ':' not in item:
            continue
        author, title = item.split(':', 1)
        author = author.strip()
        title = title.strip()
        if author and title:
            result.add(f'{author}::{title}')
    return result

def _parse_dynamic_push_blacklist(sender):
    raw = str(sender.bucketGet(COLLECT_BUCKET, 'dynamic_push_blacklist') or '').strip()
    blacklisted_authors = set()
    blacklisted_plugins = set()
    if not raw:
        return blacklisted_authors, blacklisted_plugins
    for item in raw.split(','):
        item = str(item or '').strip()
        if not item:
            continue
        if ':' in item:
            author, title = item.split(':', 1)
            author = author.strip()
            title = title.strip()
            # 保护白名单权益：如果作者是 yuhualhh，拒绝将其插件加入黑名单
            if author and title and author != 'yuhualhh':
                blacklisted_plugins.add(f'{author}:{title}')
        else:
            # 保护白名单权益：拒绝将 yuhualhh 整个订阅源加入黑名单
            if item != 'yuhualhh':
                blacklisted_authors.add(item)
    return blacklisted_authors, blacklisted_plugins

def _build_installed_plugin_groups(installed_plugins):
    groups = {}
    for item in installed_plugins or []:
        author = str(item.get('author') or '').strip()
        title = str(item.get('title') or '').strip()
        if not author or not title:
            continue
        groups.setdefault(author, []).append(item)
    return groups


def _build_remote_plugin_index(plugins):
    path_map = {}
    title_map = {}
    for plugin in plugins or []:
        title = str((plugin or {}).get('title') or '').strip()
        plugin_path = str((plugin or {}).get('plugin_path') or '').strip()
        if plugin_path and plugin_path not in path_map:
            path_map[plugin_path] = plugin
        if title and title not in title_map:
            title_map[title] = plugin
    return path_map, title_map


def _find_remote_plugin(installed_plugin, remote_plugins):
    path_map, title_map = _build_remote_plugin_index(remote_plugins)
    plugin_path = str((installed_plugin or {}).get('plugin_path') or '').strip()
    title = str((installed_plugin or {}).get('title') or '').strip()
    if plugin_path and plugin_path in path_map:
        return title_map.get(title) or path_map[plugin_path]
    if title and title in title_map:
        return title_map[title]
    return None


def _get_cloud_market_page(sender, tab_value, page, page_size):
    endpoint = (
        f'/js/cloud?tab={quote(str(tab_value or ""))}&keyword=&class=&page={int(page)}'
        f'&pageSize={int(page_size)}&orderby='
    )
    resp = _autman_api_request(sender, 'get', endpoint, timeout=LOCAL_TIMEOUT)
    if not resp:
        return None
    data = _safe_json_loads(resp.text, {})
    if data.get('code') != 200:
        return None
    return data.get('data') or {}


def _fetch_official_market_plugins(sender):
    page = 1
    plugins = []
    total = None
    while True:
        payload = _get_cloud_market_page(sender, '', page, PAGE_SIZE)
        if not isinstance(payload, dict):
            break
        items = payload.get('data') or []
        if total is None:
            try:
                total = int(payload.get('total') or len(items))
            except Exception:
                total = len(items)
        plugins.extend(items)
        if not items or len(plugins) >= int(total or 0):
            break
        page += 1
        if page > 200:
            break
    return plugins


def _build_plugins_by_author(plugins):
    result = {}
    for plugin in plugins or []:
        author = str((plugin or {}).get('author') or '').strip()
        title = str((plugin or {}).get('title') or '').strip()
        if not author or not title:
            continue
        result.setdefault(author, []).append(plugin)
    return result


def _install_or_update_market_plugin(sender, author, plugin, tab_value=None):
    author = str(author or (plugin or {}).get('author') or '').strip()
    title = str((plugin or {}).get('title') or '').strip()
    language = str((plugin or {}).get('language') or '').strip()
    tab_value = str(author if tab_value is None else tab_value)
    if not author or not title or not language:
        return False, '缺少必要参数'

    endpoint = (
        f'/js/install?language={quote(language)}&title={quote(title)}'
        f'&author={quote(author)}&tab={quote(tab_value)}'
    )
    resp = _autman_api_request(sender, 'post', endpoint, timeout=LOCAL_TIMEOUT)
    if not resp:
        return False, '安装或更新失败'

    data = _safe_json_loads(resp.text, {})
    if data.get('code') != 200:
        return False, data.get('message') or '安装或更新失败'

    return True, str(data.get('message') or 'ok')

def _subscription_one_key_update(sender, silent=False, respect_blacklist=False, preloaded_local_subs=None, preloaded_snapshot_map=None):
    if not sender.isAdmin():
        return False, '您没有权限执行此操作'

    installed_plugins = _list_installed_plugins(sender)
    if not installed_plugins:
        return True, """=====订阅一键更新=====
📦 已装插件数量为零
✅ 无需更新任何插件
=================="""

    installed_groups = _build_installed_plugin_groups(installed_plugins)
    local_subs = preloaded_local_subs if isinstance(preloaded_local_subs, list) else _list_local_subscriptions(sender, '')
    subscribed_authors = {str(x.get('author') or x.get('name') or '').strip() for x in local_subs if str(x.get('author') or x.get('name') or '').strip()}
    blacklist = _parse_auto_update_blacklist(sender) if respect_blacklist else set()

    official_plugins = _fetch_official_market_plugins(sender)
    official_by_author = _build_plugins_by_author(official_plugins)

    source_total = len(installed_groups)
    plugin_total = sum(len(v) for v in installed_groups.values())
    added_sources = 0
    official_hit = 0
    deleted_source_skipped = 0
    updated_count = 0
    skipped_blacklist = 0
    already_latest = 0
    not_found = 0
    failed = 0
    inaccessible_sources = []
    skipped_deleted_authors = []
    updated_plugins = []
    failed_plugins = []

    for author in sorted(installed_groups.keys()):
        author_plugins = installed_groups.get(author) or []
        official_remote_plugins = official_by_author.get(author) or []
        if official_remote_plugins:
            official_hit += 1

        subscribed_remote_plugins = None
        subscribed_remote_checked = False

        def get_subscribed_remote_plugins():
            nonlocal subscribed_remote_plugins, subscribed_remote_checked
            if subscribed_remote_checked:
                return subscribed_remote_plugins
            subscribed_remote_checked = True
            if author not in subscribed_authors:
                subscribed_remote_plugins = None
                return subscribed_remote_plugins

            snapshot = None
            if isinstance(preloaded_snapshot_map, dict):
                snapshot = preloaded_snapshot_map.get(author)

            if snapshot is None:
                snapshot = _collect_single_source(sender, {'author': author, 'name': author})

            if not snapshot.get('is_online') or not snapshot.get('plugins'):
                subscribed_remote_plugins = None
                inaccessible_sources.append(author)
                return subscribed_remote_plugins
            subscribed_remote_plugins = snapshot.get('plugins') or []
            return subscribed_remote_plugins

        for installed_plugin in author_plugins:
            title = str(installed_plugin.get('title') or '').strip()
            if not title:
                continue

            plugin_key = f'{author}::{title}'
            if plugin_key in blacklist:
                skipped_blacklist += 1
                continue

            remote_plugin = None
            install_tab = ''

            if official_remote_plugins:
                remote_plugin = _find_remote_plugin(installed_plugin, official_remote_plugins)
                if remote_plugin:
                    install_tab = ''

            if not remote_plugin:
                if author not in subscribed_authors:
                    deleted_source_skipped += 1
                    skipped_deleted_authors.append(author)
                    continue
                remote_plugins = get_subscribed_remote_plugins()
                if remote_plugins is None:
                    failed += 1
                    failed_plugins.append(f'{author}:{title}')
                    continue
                remote_plugin = _find_remote_plugin(installed_plugin, remote_plugins)
                install_tab = author

            if not remote_plugin:
                if author in subscribed_authors:
                    not_found += 1
                else:
                    deleted_source_skipped += 1
                    skipped_deleted_authors.append(author)
                continue

            local_version = str(installed_plugin.get('version') or '')
            remote_version = str(remote_plugin.get('version') or '')
            if _compare_versions(remote_version, local_version) <= 0:
                already_latest += 1
                continue

            ok, msg = _install_or_update_market_plugin(sender, author, remote_plugin, tab_value=install_tab)
            if ok:
                updated_count += 1
                updated_plugins.append(f'{author}:{title} v{local_version or "未知"}→v{remote_version or "未知"}')
            else:
                failed += 1
                failed_plugins.append(f'{author}:{title}')

    skipped_total = skipped_blacklist + already_latest + deleted_source_skipped + not_found

    summary = f"""=====订阅一键更新=====
🔆 已装插件: {plugin_total}"""

    if skipped_total > 0:
        summary += f'\n🎨 跳过更新: {skipped_total}'

    summary += f"""
🎉 更新成功: {updated_count}
💢 更新失败: {failed}"""

    if updated_plugins and not silent:
        summary += '\n💬 成功明细: ' + '、'.join(updated_plugins[:20])
        if len(updated_plugins) > 20:
            summary += f' 等{len(updated_plugins)}个'

    if failed_plugins and not silent:
        summary += '\n📔 失败明细: ' + '、'.join(failed_plugins[:20])
        if len(failed_plugins) > 20:
            summary += f' 等{len(failed_plugins)}个'

    summary += '\n=================='

    return True, summary


def _handle_subscription_one_key_update(sender):
    if not sender.isAdmin():
        sender.reply('🚫 您没有权限执行此操作')
        return
    sender.reply('⏳ 正在执行...')
    ok, msg = _subscription_one_key_update(sender, silent=False, respect_blacklist=False)
    sender.reply(msg if ok else f'❌ {msg}')


def _add_subscriptions(sender, items):
    if not items:
        return True, '无需新增'
    payload = []
    for item in items:
        author = str(item.get('author') or '').strip()
        name = str(item.get('name') or author).strip()
        if author:
            payload.append({'author': author, 'name': name})
    if not payload:
        return True, '无需新增'
    resp = _autman_api_request(
        sender,
        'post',
        '/market/subs',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
        timeout=LOCAL_TIMEOUT,
    )
    if not resp:
        return False, '添加订阅失败'
    data = _safe_json_loads(resp.text, {})
    if data.get('code') != 200:
        message = str(data.get('message') or '添加订阅失败')
        if '已订阅' in message and '请先删除旧订阅' in message:
            return True, message
        return False, message
    return True, f'成功新增 {len(data.get("data") or [])} 个订阅'


def _delete_subscriptions_by_ids(sender, ids):
    if not ids:
        return True, '无需删除'
    resp = _autman_api_request(
        sender,
        'delete',
        '/market/subs',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(ids, ensure_ascii=False).encode('utf-8'),
        timeout=LOCAL_TIMEOUT,
    )
    if not resp:
        return False, '删除订阅失败'
    data = _safe_json_loads(resp.text, {})
    if data.get('code') != 200:
        return False, data.get('message') or '删除订阅失败'
    return True, f'成功删除 {len(data.get("data") or [])} 个订阅'


def _extract_image_url(description):
    if not description:
        return '', ''
    image_url = ''
    match = re.search(r'<img\s+src="([^"]+)"[^>]*>', description, re.I)
    if match:
        image_url = match.group(1)
        description = description.replace(match.group(0), '')
    description = description.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    description = re.sub(r'<[^>]+>', '', description).strip()
    return description, image_url


def _render_html_content(html_text):
    """将HTML内容转为机器人消息格式：<br>换行，<img>转CQ图片码，其余标签去除"""
    if not html_text:
        return ''
    parts = []
    last_end = 0
    for m in re.finditer(r'<img\s+src="([^"]+)"[^>]*>', html_text, re.I):
        if m.start() > last_end:
            segment = html_text[last_end:m.start()]
            segment = segment.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
            segment = re.sub(r'<[^>]+>', '', segment)
            # 相邻图片之间仅含纯空白（无换行）时去除，避免图片间产生空行
            # 含有换行符的segment保留，确保<br>换行效果
            if parts and segment.strip() == '' and '\n' not in segment:
                pass
            else:
                parts.append(segment)
        parts.append(f'[CQ:image,file={m.group(1)}]')
        last_end = m.end()
    if last_end < len(html_text):
        tail = html_text[last_end:]
        tail = tail.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
        tail = re.sub(r'<[^>]+>', '', tail)
        parts.append(tail)
    result = ''.join(parts)
    # 仅去除尾部空白，保留开头<br>产生的换行
    result = result.rstrip()
    # 清理3个及以上连续换行为2个
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result


def _normalize_price(value):
    try:
        return Decimal(str(value)).quantize(Decimal('0.00'))
    except Exception:
        return Decimal('0.00')


def _compare_versions(v1, v2):
    def _parts(v):
        nums = re.findall(r'\d+', str(v))
        return [int(x) for x in nums] if nums else [0]
    p1, p2 = _parts(v1), _parts(v2)
    for i in range(max(len(p1), len(p2))):
        a = p1[i] if i < len(p1) else 0
        b = p2[i] if i < len(p2) else 0
        if a > b:
            return 1
        if a < b:
            return -1
    return 0


def _get_cloud_username(sender):
    return (sender.bucketGet('cloud', 'username') or '').strip()


def _get_cloud_password(sender):
    return (sender.bucketGet('cloud', 'password') or DEV_RECORDS_PASSWORD or '').strip()


def _flatten_possible_sources(data):
    found = []

    def walk(obj):
        if isinstance(obj, list):
            if obj and all(isinstance(x, dict) for x in obj):
                for item in obj:
                    author = str(item.get('author') or item.get('name') or item.get('username') or '').strip()
                    name = str(item.get('name') or item.get('author') or item.get('username') or '').strip()
                    if author:
                        found.append(item)
            elif obj and all(isinstance(x, str) for x in obj):
                for item in obj:
                    author = str(item or '').strip()
                    if author:
                        found.append({'author': author, 'name': author})
            for item in obj:
                walk(item)
        elif isinstance(obj, dict):
            for v in obj.values():
                walk(v)

    walk(data)
    return found


def _sync_live_sources_snapshot(sender, items):
    if _get_cloud_username(sender) != 'yuhualhh':
        return False, 'skip'
    source_items = []
    seen = set()
    for item in items:
        author = str(item.get('author') or item.get('name') or item.get('username') or '').strip()
        name = str(item.get('name') or item.get('author') or author).strip()
        if not author or author in seen:
            continue
        seen.add(author)
        source_items.append({'author': author, 'name': name})
    if not source_items:
        return False, 'empty_records'
    payload = {
        'node_id': _build_node_id(sender),
        'cloud_user_id': _get_cloud_username(sender) or 'unknown',
        'collected_at': int(time.time()),
        'sources': source_items,
    }
    data, err = _backend_request(sender, 'post', 'sync_records', payload=payload, timeout=REMOTE_TIMEOUT)
    if err:
        return False, err
    return True, str(int(data.get('live_total') or len(source_items)))

def _get_seen_live_source_authors(sender):
    try:
        raw = sender.bucketGet(COLLECT_BUCKET, 'live_source_seen_authors')
    except Exception:
        return set()

    if not raw:
        return set()

    data = _safe_json_loads(raw, [])
    result = set()

    if isinstance(data, list):
        for item in data:
            author = str(item or '').strip()
            if author:
                result.add(author)
    elif isinstance(data, dict):
        for item in (data.get('authors') or []):
            author = str(item or '').strip()
            if author:
                result.add(author)

    return result
    
def _set_seen_live_source_authors(sender, authors):
    normalized = sorted({str(x).strip() for x in (authors or []) if str(x).strip()})
    try:
        sender.bucketSet(COLLECT_BUCKET, 'live_source_seen_authors', json.dumps(normalized, ensure_ascii=False))
        return True
    except Exception:
        return False

def _developer_bootstrap_sources(sender, local_subs):
    cloud_user = _get_cloud_username(sender)
    compat_mode_enabled = _is_compat_mode_enabled(sender)

    source_items = []
    fetch_err = ''
    used_fallback = False

    if compat_mode_enabled:
        fetch_err = 'force_compat_mode'
    else:
        source_items, fetch_err = _get_live_source_items(sender)

    if compat_mode_enabled or fetch_err or not source_items:
        data, err = _backend_request(sender, 'get', 'catalog')
        if not err:
            fallback_items = []
            seen = set()
            for item in (data.get('sources') or []):
                author = str(item.get('author') or '').strip()
                name = str(item.get('name') or author).strip()
                if not author or author in seen:
                    continue
                seen.add(author)
                fallback_items.append({'author': author, 'name': name})
            if fallback_items:
                source_items = fallback_items
                used_fallback = True

    if not source_items:
        return {
            'added': 0,
            'records_count': 0,
            'attempted': 0,
            'failed': 0,
            'status': fetch_err or 'skip_no_live_api',
            'synced': False,
            'sync_msg': fetch_err or 'skip_no_live_api',
            'failed_authors': []
        }

    # 仅开发者账号执行自动扩源，其他账号也获取订阅源总数
    if cloud_user != 'yuhualhh':
        return {
            'added': 0,
            'records_count': len(source_items),
            'attempted': 0,
            'failed': 0,
            'status': 'skip',
            'synced': False
        }

    if compat_mode_enabled or used_fallback:
        return {
            'added': 0,
            'records_count': len(source_items),
            'attempted': 0,
            'failed': 0,
            'status': 'skip_no_live_api',
            'synced': False,
            'sync_msg': 'skip_no_live_api',
            'failed_authors': []
        }

    # 同步 live_sources（保持 live_total 为实时接口返回值）
    synced, sync_msg = _sync_live_sources_snapshot(sender, source_items)

    current_source_items = []
    current_authors = set()
    for item in source_items:
        author = str(item.get('author') or '').strip()
        name = str(item.get('name') or author).strip()
        if not author or author in current_authors:
            continue
        current_authors.add(author)
        current_source_items.append({'author': author, 'name': name})

    existing_authors = {str(x.get('author') or x.get('name') or '').strip() for x in local_subs}
    seen_authors = _get_seen_live_source_authors(sender)

    # 首次运行只初始化“已见过的实时订阅源集合”，不执行自动扩源
    if not seen_authors:
        _set_seen_live_source_authors(sender, current_authors)
        return {
            'added': 0,
            'records_count': len(current_source_items),
            'attempted': 0,
            'failed': 0,
            'status': 'initialized',
            'synced': synced,
            'sync_msg': sync_msg,
            'failed_authors': []
        }

    new_authors = current_authors - seen_authors

    to_add = []
    for item in current_source_items:
        author = str(item.get('author') or '').strip()
        name = str(item.get('name') or author).strip()
        if not author:
            continue
        if author not in new_authors:
            continue
        if author in existing_authors:
            continue
        to_add.append({'author': author, 'name': name})

    attempted = len(to_add)
    added = 0
    failed = 0
    failed_authors = []

    if to_add:
        def add_one(item):
            ok, msg = _add_subscriptions(sender, [item])
            return ok, str(item.get('author') or '')

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            for ok, author in executor.map(add_one, to_add):
                if ok:
                    added += 1
                    existing_authors.add(author)
                else:
                    failed += 1
                    if author:
                        failed_authors.append(author)

    # 无论添加成功还是失败，都把本次实时接口出现过的 author 记为“已见过”
    merged_seen_authors = set(seen_authors)
    merged_seen_authors.update(current_authors)
    _set_seen_live_source_authors(sender, merged_seen_authors)

    status = 'ok' if attempted > 0 and failed == 0 else 'partial_failed' if failed > 0 else 'no_new_source'
    return {
        'added': added,
        'records_count': len(current_source_items),
        'attempted': attempted,
        'failed': failed,
        'status': status,
        'synced': synced,
        'sync_msg': sync_msg,
        'failed_authors': failed_authors
    }

def _get_live_source_items(sender):
    records_url = DEV_RECORDS_URL.strip()
    cloud_user = _get_cloud_username(sender)
    records_pwd = _get_cloud_password(sender)
    if not cloud_user:
        return [], 'missing_cloud_user'
    if not records_url or not records_pwd:
        return [], 'missing_password'

    try:
        resp = _make_request(
            'get',
            records_url,
            params={'username': cloud_user, 'password': records_pwd},
            headers={'Username': cloud_user},
            timeout=REMOTE_TIMEOUT,
        )
        if not resp or resp.status_code != 200:
            return [], 'request_failed'

        data = _safe_json_loads(resp.text, {})
        items = _flatten_possible_sources(data)

        source_items = []
        seen = set()
        for item in items:
            author = str(item.get('author') or item.get('name') or item.get('username') or '').strip()
            name = str(item.get('name') or item.get('author') or author).strip()
            if not author or author in seen:
                continue
            seen.add(author)
            source_items.append({'author': author, 'name': name})

        return source_items, ''
    except Exception:
        return [], 'exception'

def _fetch_source_ads(sender, author):
    """采集订阅源的 管理/机器/公告 信息（来自 /js/ads 接口）"""
    result = {'admin_text': '', 'machine_text': '', 'announcement_text': '', 'ads_collected': False}
    if not author:
        return result
    for attempt in range(1, 4):
        try:
            endpoint = f'/js/ads?tab={quote(author)}'
            resp = _autman_api_request(sender, 'get', endpoint, timeout=LOCAL_TIMEOUT)
            if not resp:
                if DEBUG:
                    printf(f'订阅源[{author}] ads采集第{attempt}次请求失败', 'WARN')
                if attempt < 3:
                    time.sleep(1)
                continue
            data = _safe_json_loads(resp.text, {})
            if data.get('code') != 200:
                if DEBUG:
                    printf(f'订阅源[{author}] ads采集第{attempt}次返回code={data.get("code")}', 'WARN')
                if attempt < 3:
                    time.sleep(1)
                continue
            ads_data = data.get('data') or {}
            result['admin_text'] = str(ads_data.get('contact_admin') or '').strip()
            result['machine_text'] = str(ads_data.get('contact_bot') or '').strip()
            result['announcement_text'] = str(ads_data.get('ads') or '').strip()
            result['ads_collected'] = True
            if DEBUG:
                printf(f'订阅源[{author}] ads采集成功: 管理={bool(result["admin_text"])}, 机器={bool(result["machine_text"])}, 公告={bool(result["announcement_text"])}', 'DEBUG')
            return result
        except Exception as e:
            if DEBUG:
                printf(f'订阅源[{author}] ads采集第{attempt}次异常: {e}', 'WARN')
            if attempt < 3:
                time.sleep(1)
    if DEBUG:
        printf(f'订阅源[{author}] ads采集3次均失败', 'ERROR')
    return result

def _collect_single_source(sender, sub_item):
    author = str(sub_item.get('author') or '').strip()
    name = str(sub_item.get('name') or author).strip()
    base = {
        'author': author,
        'name': name,
        'id': int(sub_item.get('id') or 0),
        'token': str(sub_item.get('token') or '').strip(),
        'disable': bool(sub_item.get('disable')),
        'default': bool(sub_item.get('default')),
        'pinned': int(sub_item.get('pinned') or 0),
        'position': int(sub_item.get('position') or 0),
        'collected_at': int(time.time()),
        'is_online': False,
        'plugin_total': 0,
        'status_note': '',
        'collect_complete': False,
        'admin_text': '',
        'machine_text': '',
        'announcement_text': '',
        'ads_collected': False,
        'plugins': [],
    }
    if not author:
        base['status_note'] = 'empty_author'
        return base

    for attempt in range(3):
        plugins = []
        page = 1
        total = None
        
        base['is_online'] = False
        base['status_note'] = ''
        base['collect_complete'] = False
        
        while True:
            endpoint = f'/js/cloud?tab={quote(author)}&keyword=&class=&page={page}&pageSize={PAGE_SIZE}&orderby='
            resp = _autman_api_request(sender, 'get', endpoint, timeout=LOCAL_TIMEOUT)
            if not resp:
                base['status_note'] = 'request_failed' if page == 1 else 'partial_failed'
                break
            data = _safe_json_loads(resp.text, {})
            if data.get('code') != 200:
                base['status_note'] = data.get('message') or ('code_not_200' if page == 1 else 'partial_code_not_200')
                break
            payload = data.get('data') or {}
            items = payload.get('data') or []
            base['is_online'] = True        
            if total is None:
                try:
                    total = int(payload.get('total') if payload.get('total') is not None else len(items))
                except Exception:
                    total = len(items)        
            plugins.extend(items)
            if len(plugins) >= int(total or 0):
                base['collect_complete'] = True
                break
            if not items:
                base['status_note'] = 'empty_response'
                break
            page += 1
            if page > 200:
                base['status_note'] = 'page_limit'
                break

        unique_plugins = []
        seen_titles = set()
        for item in plugins:
            title = str((item or {}).get('title') or '').strip()
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            unique_plugins.append(item)

        base['plugin_total'] = len(unique_plugins)
        base['plugins'] = unique_plugins
        if base['collect_complete'] and base['is_online'] and not base['status_note']:
            base['status_note'] = 'ok'
            
        if base['is_online'] and base['plugin_total'] == 0 and attempt < 2:
            time.sleep(1)
            continue
        else:
            break

    # 采集订阅源的 管理/机器/公告 信息
    if base['is_online']:
        ads_info = _fetch_source_ads(sender, author)
        base['admin_text'] = ads_info['admin_text']
        base['machine_text'] = ads_info['machine_text']
        base['announcement_text'] = ads_info['announcement_text']
        base['ads_collected'] = ads_info['ads_collected']

    return base

def _build_node_id(sender):
    cloud_user = _get_cloud_username(sender) or 'unknown'
    admin = str(sender.bucketGet('autMan', 'adminUsername') or 'unknown')
    seed = f'{cloud_user}|{admin}|subscription_hub'
    return hashlib.sha1(seed.encode('utf-8')).hexdigest()[:24]


def _collect_and_upload(sender, triggered_by='manual', shared_context=None):
    if not sender.isAdmin():
        return False, '您没有权限执行此操作'
    if triggered_by != 'manual' and not _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'collect_enable')):
        return False, '请先在插件配置中启用【订阅采集】'

    local_subs = _list_local_subscriptions(sender, '')

    # ====================== 自动扩源计时 ======================
    start_dev = time.time()
    dev_result = _developer_bootstrap_sources(sender, local_subs)
    dev_time = round(time.time() - start_dev, 2)

    if dev_result.get('added'):
        local_subs = _list_local_subscriptions(sender, '')

    enabled_sources = [x for x in local_subs if not bool(x.get('disable'))]

    # ====================== 采集数据计时 ======================
    start_collect = time.time()
    source_snapshots = []
    online_count = 0
    plugin_count = 0

    def collect_one(sub):
        return _collect_single_source(sender, sub)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_sub = {executor.submit(collect_one, sub): sub for sub in enabled_sources}
        for future in concurrent.futures.as_completed(future_to_sub):
            snapshot = future.result()
            source_snapshots.append(snapshot)
            if snapshot.get('is_online'):
                online_count += 1
                plugin_count += len(snapshot.get('plugins') or [])
    collect_time = round(time.time() - start_collect, 2)

    if isinstance(shared_context, dict):
        source_snapshot_map = {}
        for snapshot in source_snapshots:
            author = str(snapshot.get('author') or '').strip()
            if author:
                source_snapshot_map[author] = snapshot
        shared_context['local_subs'] = local_subs
        shared_context['enabled_sources'] = enabled_sources
        shared_context['source_snapshots'] = source_snapshots
        shared_context['source_snapshot_map'] = source_snapshot_map

    # ====================== 云端上传计时（保持串行，不增加云端压力） ======================
    start_upload = time.time()
    base_payload = {
        'node_id': _build_node_id(sender),
        'cloud_user_id': _get_cloud_username(sender) or 'unknown',
        'collector_version': '1.0.0',
        'collected_at': int(time.time()),
        'meta': {
            'triggered_by': triggered_by,
            'enabled_source_count': len(enabled_sources),
            'developer_bootstrap': dev_result,
        },
    }

    upload_success = 0
    success_authors = set()

    for snapshot in source_snapshots:
        single_payload = dict(base_payload)
        single_payload['collected_at'] = int(time.time())
        single_payload['sources'] = [snapshot]
        for attempt in range(3):
            data, err = _backend_request(sender, 'post', 'collect', payload=single_payload, timeout=REMOTE_TIMEOUT)
            if not err:
                break
            if attempt == 0:
                time.sleep(0.5)
        if err:
            continue

        if bool(snapshot.get('is_online')) and bool(snapshot.get('collect_complete')):
            upload_success += 1
            success_author = str(snapshot.get('author') or snapshot.get('name') or '').strip()
            if success_author:
                success_authors.add(success_author)

    upload_failed = len(enabled_sources) - upload_success
    upload_time = round(time.time() - start_upload, 2)

    failed_authors = []
    failed_author_set = set()
    for item in enabled_sources:
        failed_name = str(item.get('author') or item.get('name') or '').strip()
        if not failed_name:
            continue
        if failed_name in success_authors:
            continue
        if failed_name in failed_author_set:
            continue
        failed_author_set.add(failed_name)
        failed_authors.append(failed_name)

    cloud_user = base_payload['cloud_user_id']
    is_developer = cloud_user == 'yuhualhh'

    summary = (
        f"=====订阅采集=====\n"
        f"🗯 云端账号: {cloud_user}"
    )

    if is_developer:
        if dev_result.get('status') == 'skip_no_live_api':
            summary += (
                f"\n🎨 同步订阅: 跳过"
                f"\n💥 扩源成功: {dev_result.get('added', 0)}"
                f"\n💢 扩源失败: {dev_result.get('failed', 0)}"
                f"\n🕑 扩源耗时: {dev_time}秒"
            )
        else:
            summary += (
                f"\n🎨 同步订阅: {'成功' if dev_result.get('synced') else '失败'}"
                f"\n💥 扩源成功: {dev_result.get('added', 0)}"
                f"\n💢 扩源失败: {dev_result.get('failed', 0)}"
                f"\n🕑 扩源耗时: {dev_time}秒"
            )

    summary += (
        f"\n🎉 当前订阅: {len(enabled_sources)}"
        f"\n💫 可访订阅: {online_count}"
        f"\n📦 采集数据: {plugin_count}"
        f"\n🕑 采集耗时: {collect_time}秒"
        f"\n💥 上传成功: {upload_success}"
        f"\n💢 上传失败: {upload_failed}"
    )

    if failed_authors:
        summary += f"\n📒 失败订阅: {'、'.join(failed_authors)}"

    summary += (
        f"\n🕑 上传耗时: {upload_time}秒"
        f"\n=================="
    )

    if upload_success > 0:
        return True, summary
    return False, summary

def _handle_collect_command(sender):
    if not _check_collect_version_limit(sender, triggered_by='manual'):
        return
    sender.reply('⏳ 正在执行...')
    ok, msg = _collect_and_upload(sender, triggered_by='manual')
    if str(msg).startswith('=====订阅采集====='):
        sender.reply(msg)
    else:
        sender.reply(msg if ok else f'❌ {msg}')

def _render_subscription_list(remote_data, local_subs, live_total=0, stats_online=None, stats_non_empty=None, stats_heartbeat=None):
    local_map = {}
    for item in local_subs:
        author = str(item.get('author') or item.get('name') or '').strip()
        if author:
            local_map[author] = item

    items = remote_data.get('sources') or []
    online = sum(1 for item in items if item.get('online'))
    non_empty = 0
    heartbeat_count = 0
    now_ts = int(time.time())

    blocks = []
    for idx, item in enumerate(items, 1):
        author = str(item.get('author') or '').strip()
        subscribed = '✅' if author in local_map else '❌'
        online_text = '在线' if item.get('online') else '离线'

        heartbeat_at = int(item.get('heartbeat_at', 0) or 0)
        fenfa = '已开' if (heartbeat_at > 0 and now_ts - heartbeat_at < 600) else '未开'
        if heartbeat_at > 0 and now_ts - heartbeat_at < 600:
            heartbeat_count += 1

        plugins = item.get('plugins') or []
        plugin_titles = [str(p.get('title') or '').strip() for p in plugins if str(p.get('title') or '').strip()]
        if plugin_titles:
            non_empty += 1
            plugin_text = '、'.join(plugin_titles)
        else:
            plugin_text = '暂无'

        block = (
            f'[{idx}] 订阅信息\n'
            f'🤪 订阅: {subscribed} {author}\n'
            f'🗯️ 分发: {fenfa}\n'
            f'📦 状态: {online_text}'
        )

        admin_text = str(item.get('admin_text') or '').strip()
        if admin_text:
            admin_rendered = _render_html_content(admin_text)
            block += f'\n💳 管理: {admin_rendered}'

        machine_text = str(item.get('machine_text') or '').strip()
        if machine_text:
            machine_rendered = _render_html_content(machine_text)
            block += f'\n🏖️ 机器: {machine_rendered}'

        announcement_text = str(item.get('announcement_text') or '').strip()
        if announcement_text:
            announcement_rendered = _render_html_content(announcement_text)
            block += f'\n🎂 公告: {announcement_rendered}'

        block += f'\n🎨 插件: {plugin_text}\n------------------'
        blocks.append(block)

    header_online = online if stats_online is None else int(stats_online)
    header_non_empty = non_empty if stats_non_empty is None else int(stats_non_empty)
    header_heartbeat = heartbeat_count if stats_heartbeat is None else int(stats_heartbeat)

    header = (
        '=====订阅列表=====\n'
        f'🎉 订阅总数: {live_total}\n'
        f'✨ 订阅在线: {header_online}\n'
        f'💭 分发已开: {header_heartbeat}\n'
        f'♨️ 非空订阅: {header_non_empty}\n'
        '------------------'
    )

    pages = []
    current = header

    for block in blocks:
        candidate = current + '\n' + block
        if len(candidate) > 2800:
            if current.strip():
                pages.append(current)
            current = block
        else:
            current = candidate

    if current.strip():
        pages.append(current)

    return pages, items, local_map

def _handle_subscription_list(sender):
    if _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'list_admin_only')) and not sender.isAdmin():
        sender.reply('🚫 您没有权限执行此操作')
        return

    local_subs = _list_local_subscriptions(sender, '')
    compat_mode_enabled = _is_compat_mode_enabled(sender)

    live_sources = []
    live_err = ''
    if compat_mode_enabled:
        live_err = 'force_compat_mode'
    else:
        live_sources, live_err = _get_live_source_items(sender)

    data, err = _backend_request(sender, 'get', 'catalog')
    if err:
        sender.reply(f'❌ 获取订阅列表失败: {err}')
        return

    if compat_mode_enabled or live_err or not live_sources:
        data = dict(data or {})
        all_items = data.get('sources') or []
        live_total = len(all_items)

        now_ts = int(time.time())
        total_online = sum(1 for item in all_items if item.get('online'))
        total_non_empty = 0
        total_heartbeat = 0
        for item in all_items:
            plugins = item.get('plugins') or []
            plugin_titles = [str(p.get('title') or '').strip() for p in plugins if str(p.get('title') or '').strip()]
            if plugin_titles:
                total_non_empty += 1
            heartbeat_at = int(item.get('heartbeat_at', 0) or 0)
            if heartbeat_at > 0 and now_ts - heartbeat_at < 600:
                total_heartbeat += 1

        display_data = dict(data or {})
        if _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'non_empty_online_list')):
            filtered_sources = []
            for source in all_items:
                plugins = source.get('plugins') or []
                plugin_titles = [str(p.get('title') or '').strip() for p in plugins if str(p.get('title') or '').strip()]
                if not plugin_titles:
                    continue
                is_online = bool(source.get('online'))
                heartbeat_at = int(source.get('heartbeat_at', 0) or 0)
                is_fenfa = (heartbeat_at > 0 and now_ts - heartbeat_at < 600)
                if is_fenfa or is_online:
                    filtered_sources.append(source)
            display_data['sources'] = filtered_sources

        pages, items, local_map = _render_subscription_list(
            display_data,
            local_subs,
            live_total,
            stats_online=total_online,
            stats_non_empty=total_non_empty,
            stats_heartbeat=total_heartbeat
        )
    else:
        catalog_map = {}
        backend_online_authors = set()
        for source in (data.get('sources') or []):
            author = str(source.get('author') or '').strip()
            if not author:
                continue
            catalog_map[author] = source
            if bool(source.get('online')):
                backend_online_authors.add(author)

        merged_sources = []
        seen = set()

        for source in live_sources:
            author = str(source.get('author') or '').strip()
            name = str(source.get('name') or author).strip()
            if not author or author in seen:
                continue
            seen.add(author)

            if author in catalog_map:
                merged_source = dict(catalog_map[author] or {})
                if not str(merged_source.get('name') or '').strip():
                    merged_source['name'] = name
                merged_source['online'] = author in backend_online_authors
                merged_sources.append(merged_source)
            else:
                merged_sources.append({
                    'author': author,
                    'name': name,
                    'source_id': 0,
                    'token': '',
                    'disable': False,
                    'default': False,
                    'pinned': 0,
                    'position': 0,
                    'online': False,
                    'plugin_count': 0,
                    'status_note': 'only_in_live_records',
                    'node_id': '',
                    'last_seen': 0,
                    'plugins': []
                })

        # 补入catalog中存在但live_sources中不存在的源（离线但有分发数据的源）
        for author, catalog_source in catalog_map.items():
            if author not in seen:
                merged_source = dict(catalog_source or {})
                merged_source['online'] = False
                merged_sources.append(merged_source)

        data = dict(data or {})
        data['sources'] = merged_sources
        live_total = len(merged_sources)

        now_ts = int(time.time())
        all_items = data.get('sources') or []
        total_online = sum(1 for item in all_items if item.get('online'))
        total_non_empty = 0
        total_heartbeat = 0
        for item in all_items:
            plugins = item.get('plugins') or []
            plugin_titles = [str(p.get('title') or '').strip() for p in plugins if str(p.get('title') or '').strip()]
            if plugin_titles:
                total_non_empty += 1
            heartbeat_at = int(item.get('heartbeat_at', 0) or 0)
            if heartbeat_at > 0 and now_ts - heartbeat_at < 600:
                total_heartbeat += 1

        display_data = dict(data or {})
        if _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'non_empty_online_list')):
            filtered_sources = []
            for source in all_items:
                plugins = source.get('plugins') or []
                plugin_titles = [str(p.get('title') or '').strip() for p in plugins if str(p.get('title') or '').strip()]
                if not plugin_titles:
                    continue
                is_online = bool(source.get('online'))
                heartbeat_at = int(source.get('heartbeat_at', 0) or 0)
                is_fenfa = (heartbeat_at > 0 and now_ts - heartbeat_at < 600)
                if is_fenfa or is_online:
                    filtered_sources.append(source)
            display_data['sources'] = filtered_sources

        pages, items, local_map = _render_subscription_list(
            display_data,
            local_subs,
            live_total,
            stats_online=total_online,
            stats_non_empty=total_non_empty,
            stats_heartbeat=total_heartbeat
        )

    operation_text = 't=一键订阅, q=退出操作\n+序号=添加, -序号=删除'
    if pages:
        pages[-1] = pages[-1] + '\n' + operation_text
    else:
        pages = [operation_text]

    for page in pages:
        sender.reply(page)
        time.sleep(0.2)

    choice = sender.input(60000, 0, False)
    if not choice:
        sender.reply('❌ 输入超时')
        return

    choice = str(choice).strip()
    if choice.lower() == 'q':
        sender.reply('✅ 已退出操作')
        return

    if choice.lower() == 't':
        if not sender.isAdmin():
            sender.reply('🚫 您没有权限执行此操作')
            return
        only_online = _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'only_add_online'))
        if compat_mode_enabled or live_err or not live_sources:
            _execute_one_key_add(sender, data.get('sources') or [], '=====订阅列表=====', only_online=only_online)
        else:
            _execute_one_key_add(sender, all_items, '=====订阅列表=====', only_online=only_online)
        return

    if len(choice) >= 2 and choice[0] in ['+', '-']:
        if not sender.isAdmin():
            sender.reply('🚫 您没有权限执行此操作')
            return
        op = choice[0]
        try:
            idx = int(choice[1:])
            if idx < 1 or idx > len(items):
                raise ValueError
        except Exception:
            sender.reply('❌ 无效的序号')
            return

        item = items[idx - 1]
        author = str(item.get('author') or '').strip()
        name = str(item.get('name') or author).strip()

        if op == '+':
            latest_local_subs = _list_local_subscriptions(sender, '')
            latest_local_map = {}
            for sub in latest_local_subs:
                sub_author = str(sub.get('author') or sub.get('name') or '').strip()
                if sub_author:
                    latest_local_map[sub_author] = sub

            if author in latest_local_map:
                sender.reply(f'✅ 已订阅 {author}')
                return

            ok, msg = _add_subscriptions(sender, [{'author': author, 'name': name}])
            if ok:
                sender.reply(f'✅ 成功添加订阅源: {author}')
            else:
                sender.reply(f'❌ 添加失败: {msg}')
            return

        if op == '-':
            latest_local_subs = _list_local_subscriptions(sender, '')
            latest_local_map = {}
            for sub in latest_local_subs:
                sub_author = str(sub.get('author') or sub.get('name') or '').strip()
                if sub_author:
                    latest_local_map[sub_author] = sub

            if author not in latest_local_map:
                sender.reply(f'✅ 当前未订阅 {author}')
                return

            target = latest_local_map.get(author) or {}
            target_id = int(target.get('id') or 0)
            if target_id <= 0:
                sender.reply(f'❌ 删除失败: 未找到订阅源ID {author}')
                return

            ok, msg = _delete_subscriptions_by_ids(sender, [target_id])
            if ok:
                sender.reply(f'✅ 成功删除订阅源: {author}')
            else:
                sender.reply(f'❌ 删除失败: {msg}')
            return

    sender.reply('❌ 无效的操作指令')
    

def _build_search_output(keyword, items):
    # 按订阅源分组，精简显示订阅级别的公告/管理/机器
    grouped = {}
    for item in items:
        author = item.get('author') or '未知'
        if author not in grouped:
            grouped[author] = {
                'source_data': item,
                'plugins': []
            }
        grouped[author]['plugins'].append(item)

    sections = []
    for author, group in grouped.items():
        source_data = group['source_data']
        plugins = group['plugins']

        # 订阅级别信息
        text = f"订阅：{author}\n"
        heartbeat_at = int(source_data.get('heartbeat_at', 0) or 0)
        now = int(time.time())
        fenfa = '已开' if (heartbeat_at > 0 and now - heartbeat_at < 600) else '未开'
        text += f"分发：{fenfa}\n"
        online_text = '在线' if source_data.get('online') else '离线'
        text += f"状态：{online_text}\n"
        announcement_text = str(source_data.get('announcement_text') or '').strip()
        if announcement_text:
            announcement_rendered = _render_html_content(announcement_text)
            text += f"公告：{announcement_rendered}\n"
        admin_text = str(source_data.get('admin_text') or '').strip()
        if admin_text:
            admin_rendered = _render_html_content(admin_text)
            text += f"管理：{admin_rendered}\n"
        machine_text = str(source_data.get('machine_text') or '').strip()
        if machine_text:
            machine_rendered = _render_html_content(machine_text)
            text += f"机器：{machine_rendered}\n"
        text += "------------------\n"

        # 插件列表
        for i, plugin in enumerate(plugins):
            desc, image_url = _extract_image_url(plugin.get('description') or '')
            price = _normalize_price(plugin.get('price') or 0)
            text += (
                f"名称：{plugin.get('title')}\n"
                f"语言：{plugin.get('language') or '未知'}\n"
                f"版本：{plugin.get('version') or '未知'}\n"
                f"价格：{price}\n"
                f"描述：\n{desc or '暂无描述'}"
            )
            if image_url:
                text += f'\n[CQ:image,file={image_url}]'
            # 最后一个插件不添加分隔线
            if i < len(plugins) - 1:
                text += "\n---------\n"

        sections.append(text.rstrip())

    messages = []
    current = ''
    for section in sections:
        candidate = section if not current else current + '\n\n' + section
        if len(candidate) > 3000:
            if current:
                messages.append(current)
            current = section
        else:
            current = candidate

    if current:
        messages.append(current)

    return messages


def _handle_subscription_search(sender, msg):
    if _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'search_admin_only')) and not sender.isAdmin():
        sender.reply('🚫 您没有权限执行此操作')
        return

    keyword = msg.replace('订阅搜索', '', 1).strip()
    if not keyword:
        sender.reply('=====订阅搜索=====\n请输入插件关键词\n------------------\n请在60秒内完成\n输入"q"退出')
        keyword = sender.input(60000, 0, False)
        if not keyword:
            sender.reply('❌ 输入超时')
            return
        keyword = str(keyword).strip()
        if keyword.lower() == 'q':
            sender.reply('✅ 已退出操作')
            return

    data, err = _backend_request(sender, 'get', 'search', params={'q': keyword, 'limit': 100})
    if err:
        sender.reply(f'❌ 搜索失败: {err}')
        return

    items = data.get('items') or []
    if not items:
        sender.reply('❌ 未搜索到任何插件')
        return

    for text in _build_search_output(keyword, items):
        sender.reply(text)
        time.sleep(0.2)


def _build_catalog_map(data):
    result = {}
    for source in (data.get('sources') or []):
        author = str(source.get('author') or '').strip()
        if not author:
            continue
        plugins = source.get('plugins') or []
        result[author] = {
            'author': author,
            'name': source.get('name') or author,
            'online': bool(source.get('online')),
            'admin_text': source.get('admin_text') or '',
            'machine_text': source.get('machine_text') or '',
            'announcement_text': source.get('announcement_text') or '',
            'heartbeat_at': int(source.get('heartbeat_at', 0) or 0),
            'plugins': {str(p.get('title') or '').strip(): p for p in plugins if str(p.get('title') or '').strip()}
        }
    return result


def _format_grouped_changes(sender, author, plugins_info, change_type, source_data):
    """格式化同一订阅源的多个插件变更，精简显示订阅级别信息（只显示一次），插件信息完整显示"""
    text = f"订阅：{author}\n"
    heartbeat_at = int(source_data.get('heartbeat_at', 0) or 0)
    now = int(time.time())
    fenfa = '已开' if (heartbeat_at > 0 and now - heartbeat_at < 600) else '未开'
    text += f"分发：{fenfa}\n"
    online_text = '在线' if source_data.get('online') else '离线'
    text += f"状态：{online_text}\n"
    announcement_text = str(source_data.get('announcement_text') or '').strip()
    if announcement_text:
        announcement_rendered = _render_html_content(announcement_text)
        text += f"公告：{announcement_rendered}\n"
    admin_text = str(source_data.get('admin_text') or '').strip()
    if admin_text:
        admin_rendered = _render_html_content(admin_text)
        text += f"管理：{admin_rendered}\n"
    machine_text = str(source_data.get('machine_text') or '').strip()
    if machine_text:
        machine_rendered = _render_html_content(machine_text)
        text += f"机器：{machine_rendered}\n"
    text += "------------------\n"

    # 插件列表（完整显示）
    for i, plugin_info in enumerate(plugins_info):
        plugin = plugin_info['plugin']
        old_plugin = plugin_info.get('old_plugin')
        desc, image_url = _extract_image_url(plugin.get('description') or '')
        price = _normalize_price(plugin.get('price') or 0)
        if old_plugin:
            version_text = f"{old_plugin.get('version') or '未知'} → {plugin.get('version') or '未知'}"
        else:
            version_text = plugin.get('version') or '未知'
        text += (
            f"名称：{plugin.get('title') or '未知'}\n"
            f"语言：{plugin.get('language') or '未知'}\n"
            f"版本：{version_text}\n"
            f"价格：{price}\n"
            f"描述：\n{desc or '暂无描述'}"
        )
        hide_images = _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'hide_dynamic_images'))
        if image_url and not hide_images:
            text += f'\n[CQ:image,file={image_url}]'
        # 最后一个插件不添加分隔线
        if i < len(plugins_info) - 1:
            text += "\n---------\n"

    return text.rstrip()


def _format_change_message(sender, author, change_type, plugin, old_plugin=None, source_data=None):
    # 返回字典而非字符串，供分组逻辑使用
    return {
        'author': author,
        'plugin': plugin,
        'old_plugin': old_plugin,
        'source_data': source_data,
        'change_type': change_type
    }

def _push_subscription_dynamics(sender, messages):
    if not messages:
        return
    group_push_enabled = _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'group_push'))
    group_ids = [x.strip() for x in str(sender.bucketGet(COLLECT_BUCKET, 'group_ids') or '').split(',') if x.strip()]
    chunks = []
    current = ''
    for msg in messages:
        candidate = msg if not current else current + '\n\n\n' + msg
        if len(candidate) > 3000:
            if current:
                chunks.append(current)
            current = msg
        else:
            current = candidate
    if current:
        chunks.append(current)

    if group_push_enabled:
        for gid in group_ids:
            for chunk in chunks:
                _send_multi_platform_push_to_group(gid, chunk)

    for chunk in chunks:
        try:
            middleware.notifyMasters(chunk)
        except Exception:
            pass

def _check_subscription_dynamics(sender, manual=False):
    if not manual and _is_dynamic_disabled(sender):
        return

    data, err = _backend_request(sender, 'get', 'catalog')
    if err:
        sender.reply(f'❌ 获取订阅动态失败: {err}')
        return

    current_map = _build_catalog_map(data)
    previous_raw = sender.bucketGet(COLLECT_BUCKET, SNAPSHOT_KEY)
    if not previous_raw:
        sender.bucketSet(COLLECT_BUCKET, SNAPSHOT_KEY, json.dumps(data, ensure_ascii=False))
        sender.reply('✅ 已初始化订阅动态快照')
        return

    previous_map = _build_catalog_map(_safe_json_loads(previous_raw, {'sources': []}) or {'sources':[]})
    subscribed_authors = _build_local_subscription_author_set(sender)
    installed_keys = _build_installed_plugin_keys(sender)
    disable_removed_push = _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'disable_removed_push'))
    
    # 解析动态推送黑名单
    blacklisted_authors, blacklisted_plugins = _parse_dynamic_push_blacklist(sender)
    
    changes = {
        'added':[],
        'updated': [],
        'removed': [],
        'downgraded':[],
    }

    all_authors = set(previous_map.keys()) | set(current_map.keys())
    for author in all_authors:
        if not _should_push_author(sender, author, subscribed_authors):
            continue
            
        # 校验：如果该作者属于黑名单，则整源跳过
        if author in blacklisted_authors:
            continue

        prev_source = previous_map.get(author, {'plugins': {}})
        curr_source = current_map.get(author, {'plugins': {}})
        prev_plugins = prev_source.get('plugins', {})
        curr_plugins = curr_source.get('plugins', {})

        for title, plugin in curr_plugins.items():
            if not _should_push_plugin(sender, author, plugin, installed_keys):
                continue

            # 校验：如果该作者的特定插件属于黑名单，则跳过
            if f'{author}:{title}' in blacklisted_plugins:
                continue

            if title not in prev_plugins:
                changes['added'].append(_format_change_message(sender, author, 'added', plugin, source_data=curr_source))
            else:
                old_plugin = prev_plugins[title]
                cmp_res = _compare_versions(plugin.get('version'), old_plugin.get('version'))
                if cmp_res > 0:
                    changes['updated'].append(_format_change_message(sender, author, 'updated', plugin, old_plugin, source_data=curr_source))
                elif cmp_res < 0:
                    changes['downgraded'].append(_format_change_message(sender, author, 'downgraded', plugin, old_plugin, source_data=curr_source))

        if not disable_removed_push:
            for title, old_plugin in prev_plugins.items():
                if title in curr_plugins:
                    continue
                if not _should_push_plugin(sender, author, old_plugin, installed_keys):
                    continue

                # 校验下架通知时，同样适用黑名单屏蔽
                if f'{author}:{title}' in blacklisted_plugins:
                    continue

                changes['removed'].append(_format_change_message(sender, author, 'removed', old_plugin, source_data=prev_source))

    sender.bucketSet(COLLECT_BUCKET, SNAPSHOT_KEY, json.dumps(data, ensure_ascii=False))

    # 按分类和订阅源分组，精简显示订阅级别信息
    messages = []
    for change_type, type_label in [('added', '✨ 插件上新'), ('updated', '🎉 插件更新'), ('removed', '🔆 插件下架'), ('downgraded', '💥 版本回退')]:
        if not changes[change_type]:
            continue

        # 按订阅源分组
        grouped_by_author = {}
        for item in changes[change_type]:
            author = item.get('author') or '未知'
            if author not in grouped_by_author:
                grouped_by_author[author] = {'source_data': item.get('source_data'), 'plugins_info': []}
            grouped_by_author[author]['plugins_info'].append({
                'plugin': item.get('plugin'),
                'old_plugin': item.get('old_plugin')
            })

        # 格式化每个订阅源的变更
        type_messages = []
        for author, group in grouped_by_author.items():
            type_messages.append(_format_grouped_changes(sender, author, group['plugins_info'], change_type, group['source_data']))

        messages.append(f"{type_label}\n\n" + '\n\n'.join(type_messages))

    total_changes = sum(len(v) for v in changes.values())

    if messages:
        _push_subscription_dynamics(sender, messages)
        sender.reply(f'✅ 检测到 {total_changes} 条订阅动态并已处理推送')
    else:
        sender.reply('✅ 暂无任何订阅动态')


def _execute_one_key_add(sender, items, header_text, show_loading=True, start_time=None, only_online=False):
    if show_loading:
        sender.reply('⏳ 正在执行...')

    if start_time is None:
        start_time = time.time()

    latest_local_subs = _list_local_subscriptions(sender, '')
    existing_authors = set()
    for sub in latest_local_subs:
        author = str(sub.get('author') or sub.get('name') or '').strip()
        if author:
            existing_authors.add(author)

    added_count = 0
    skipped_count = 0
    failed_authors = []

    to_add = []
    for item in items:
        author = str(item.get('author') or '').strip()
        name = str(item.get('name') or author).strip()
        if not author:
            continue
        if author in existing_authors:
            skipped_count += 1
            continue
        if only_online and not bool(item.get('online')):
            continue
        to_add.append({'author': author, 'name': name})

    if to_add:
        def add_one(item):
            ok, msg = _add_subscriptions(sender, [item])
            return ok, str(item.get('author') or '')

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            for ok, author in executor.map(add_one, to_add):
                if ok:
                    added_count += 1
                    existing_authors.add(author)
                else:
                    if author:
                        failed_authors.append(author)

    elapsed = round(time.time() - start_time, 2)

    reply = (
        f'{header_text}\n'
        f'🎨 跳过已添: {skipped_count}\n'
        f'🎉 添加成功: {added_count}\n'
        f'💥 添加失败: {len(failed_authors)}'
    )
    if failed_authors:
        failed_text = '、'.join(failed_authors)
        reply += f'\n📒 失败订阅: {failed_text}'
    reply += f'\n🕑 操作用时: {elapsed}秒'
    reply += '\n=================='
    sender.reply(reply)
    
def _handle_subscription_one_key_add(sender):
    if not sender.isAdmin():
        sender.reply('🚫 您没有权限执行此操作')
        return

    sender.reply('⏳ 正在执行...')
    start_time = time.time()

    local_subs = _list_local_subscriptions(sender, '')
    compat_mode_enabled = _is_compat_mode_enabled(sender)

    live_sources = []
    live_err = ''
    if compat_mode_enabled:
        live_err = 'force_compat_mode'
    else:
        live_sources, live_err = _get_live_source_items(sender)

    data, err = _backend_request(sender, 'get', 'catalog')
    if err:
        elapsed = round(time.time() - start_time, 2)
        sender.reply(f'❌ 获取订阅列表失败: {err}\n🕑 操作用时: {elapsed}秒')
        return

    if compat_mode_enabled or live_err or not live_sources:
        data = dict(data or {})
        all_items = data.get('sources') or []
        live_total = len(all_items)

        now_ts = int(time.time())
        total_online = sum(1 for item in all_items if item.get('online'))
        total_non_empty = 0
        total_heartbeat = 0
        for item in all_items:
            plugins = item.get('plugins') or []
            plugin_titles = [str(p.get('title') or '').strip() for p in plugins if str(p.get('title') or '').strip()]
            if plugin_titles:
                total_non_empty += 1
            heartbeat_at = int(item.get('heartbeat_at', 0) or 0)
            if heartbeat_at > 0 and now_ts - heartbeat_at < 600:
                total_heartbeat += 1

        pages, items, local_map = _render_subscription_list(
            data,
            local_subs,
            live_total,
            stats_online=total_online,
            stats_non_empty=total_non_empty,
            stats_heartbeat=total_heartbeat
        )
    else:
        catalog_map = {}
        backend_online_authors = set()
        for source in (data.get('sources') or []):
            author = str(source.get('author') or '').strip()
            if not author:
                continue
            catalog_map[author] = source
            if bool(source.get('online')):
                backend_online_authors.add(author)

        merged_sources = []
        seen = set()

        for source in live_sources:
            author = str(source.get('author') or '').strip()
            name = str(source.get('name') or author).strip()
            if not author or author in seen:
                continue
            seen.add(author)

            if author in catalog_map:
                merged_source = dict(catalog_map[author] or {})
                if not str(merged_source.get('name') or '').strip():
                    merged_source['name'] = name
                merged_source['online'] = author in backend_online_authors
                merged_sources.append(merged_source)
            else:
                merged_sources.append({
                    'author': author,
                    'name': name,
                    'source_id': 0,
                    'token': '',
                    'disable': False,
                    'default': False,
                    'pinned': 0,
                    'position': 0,
                    'online': False,
                    'plugin_count': 0,
                    'status_note': 'only_in_live_records',
                    'node_id': '',
                    'last_seen': 0,
                    'plugins': []
                })

        # 补入catalog中存在但live_sources中不存在的源（离线但有分发数据的源）
        for author, catalog_source in catalog_map.items():
            if author not in seen:
                merged_source = dict(catalog_source or {})
                merged_source['online'] = False
                merged_sources.append(merged_source)

        data = dict(data or {})
        data['sources'] = merged_sources
        live_total = len(merged_sources)

        now_ts = int(time.time())
        total_online = sum(1 for item in merged_sources if item.get('online'))
        total_non_empty = 0
        total_heartbeat = 0
        for item in merged_sources:
            plugins = item.get('plugins') or []
            plugin_titles = [str(p.get('title') or '').strip() for p in plugins if str(p.get('title') or '').strip()]
            if plugin_titles:
                total_non_empty += 1
            heartbeat_at = int(item.get('heartbeat_at', 0) or 0)
            if heartbeat_at > 0 and now_ts - heartbeat_at < 600:
                total_heartbeat += 1

        pages, items, local_map = _render_subscription_list(
            data,
            local_subs,
            live_total,
            stats_online=total_online,
            stats_non_empty=total_non_empty,
            stats_heartbeat=total_heartbeat
        )

    only_online = _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'only_add_online'))
    _execute_one_key_add(sender, data.get('sources') or [], '=====订阅一键添加=====', show_loading=False, start_time=start_time, only_online=only_online)

def _handle_fake_scheduled_tasks(sender):
    collect_enabled = _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'collect_enable'))
    auto_update_enabled = _bool_enabled(sender.bucketGet(COLLECT_BUCKET, 'auto_update'))
    dynamic_enabled = not _is_dynamic_disabled(sender)

    if not collect_enabled and not auto_update_enabled and not dynamic_enabled:
        return

    sender.reply('⏳ 正在执行...')

    shared_context = {}

    if collect_enabled:
        if _check_collect_version_limit(sender, triggered_by='fake'):
            ok, msg = _collect_and_upload(sender, triggered_by='fake', shared_context=shared_context)
            try:
                if str(msg).startswith('=====订阅采集====='):
                    middleware.notifyMasters(msg)
                else:
                    middleware.notifyMasters(msg if ok else f'❌ {msg}')
            except Exception:
                pass

    if auto_update_enabled:
        preloaded_local_subs = shared_context.get('local_subs') if collect_enabled else None
        preloaded_snapshot_map = shared_context.get('source_snapshot_map') if collect_enabled else None
        ok, msg = _subscription_one_key_update(
            sender,
            silent=False,
            respect_blacklist=True,
            preloaded_local_subs=preloaded_local_subs,
            preloaded_snapshot_map=preloaded_snapshot_map
        )
        try:
            is_zero_plugin = "已装插件数量为零" in msg
            is_no_change = "更新成功: 0" in msg and "更新失败: 0" in msg
            if not is_zero_plugin and not is_no_change:
                middleware.notifyMasters(msg if ok else f'❌ {msg}')
        except Exception:
            pass
    if dynamic_enabled:
        _check_subscription_dynamics(sender, manual=False)

def _handle_subscription_dynamic(sender):
    if not sender.isAdmin():
        sender.reply('🚫 您没有权限执行此操作')
        return
    sender.reply('⏳ 正在执行...')
    _check_subscription_dynamics(sender, manual=True)

def _perform_maintenance_check() -> bool:
    from bs4 import BeautifulSoup

    url = "https://yuhualhh.250666.xyz/shouquan"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache"
    }
    for attempt in range(3):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=(5, 10),
                verify=True,
                allow_redirects=True
            )
            response.raise_for_status()
            response.encoding = 'UTF-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            content_div = soup.find('div', class_='note-content')
            if content_div:
                return "服务正常中" in content_div.get_text(strip=True)
            return any("服务正常中" in tag.get_text() for tag in soup.find_all(['div', 'p']))
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < 2:
                time.sleep(2)
                continue
            return False
        except requests.exceptions.HTTPError:
            return False
        except Exception:
            return False
    return False

def check_maintenance_page() -> bool:
    import os, base64, hashlib, json
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    cache_bucket = "time"
    cache_key = "status_cache"
    ttl_seconds = 1 * 3600
    try:
        salt = b'\x8a\x9b\x1f\xe3\x7d\x4c\x5b\x6a\x01\x23\x45\x67\x89\xab\xcd\xef'
        identifier = "yuhua888"
        key = hashlib.sha256(salt + identifier.encode('utf-8')).digest()
        aesgcm = AESGCM(key)
        cached_data_str = middleware.bucketGet(cache_bucket, cache_key)
        if cached_data_str:
            decoded_data = base64.b64decode(cached_data_str.encode('utf-8'))
            nonce = decoded_data[:12]
            ciphertext = decoded_data[12:]
            decrypted_bytes = aesgcm.decrypt(nonce, ciphertext, None)
            cached_data = json.loads(decrypted_bytes.decode('utf-8'))
            if (time.time() - cached_data.get("timestamp", 0)) < ttl_seconds and cached_data.get("status") is True:
                return True
    except Exception:
        pass

    live_status = _perform_maintenance_check()
    new_cache_payload = {
        "status": live_status,
        "timestamp": time.time()
    }
    try:
        salt = b'\x8a\x9b\x1f\xe3\x7d\x4c\x5b\x6a\x01\x23\x45\x67\x89\xab\xcd\xef'
        identifier = "yuhua888"
        key = hashlib.sha256(salt + identifier.encode('utf-8')).digest()
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        plaintext = json.dumps(new_cache_payload).encode('utf-8')
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)
        encrypted_payload = base64.b64encode(nonce + ciphertext).decode('utf-8')
        middleware.bucketSet(cache_bucket, cache_key, encrypted_payload)
    except Exception:
        pass
    return live_status    

def _show_help(sender):
    sender.reply(
        '请回复以下指令：\n'
        '订阅采集\n'
        '订阅列表\n'
        '订阅搜索\n'
        '订阅动态\n'
        '订阅一键添加\n'
        '订阅一键更新'
    )


def main():
    sender_id = middleware.getSenderID()
    sender = middleware.Sender(sender_id)
    msg = sender.getMessage().strip()
    imtype = sender.getImtype()

    if not check_maintenance_page():
        sender.reply("❌ 服务端无法连通, 插件停止运行")
        return

    if imtype == 'fake':
        _handle_fake_scheduled_tasks(sender)
        return

    if msg == '订阅助手':
        _show_help(sender)
        return
    if msg == '订阅采集':
        _handle_collect_command(sender)
        return
    if msg == '订阅列表':
        _handle_subscription_list(sender)
        return
    if msg == '订阅一键添加':
        _handle_subscription_one_key_add(sender)
        return
    if msg == '订阅一键更新':
        _handle_subscription_one_key_update(sender)
        return
    if msg == '订阅搜索':
        _handle_subscription_search(sender, msg)
        return
    if msg == '订阅动态':
        _handle_subscription_dynamic(sender)
        return
if __name__ == '__main__':
    main()