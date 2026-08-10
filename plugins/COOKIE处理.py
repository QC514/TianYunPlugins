# [language: python]
# [wb: true]
# [disable: true]
# [admin: false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [priority: 1]
# [open_source: false]
# [public: true]
# [pin: false]
# [rule: ^[\s\S]*(pt_key|wskey=)[\s\S]*$]
# [price: 1.88]
# [author: 1934103887]
# [service:	<img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif">QQ：1934103887]
# [title: COOKIE处理]
# [cron: ]
# [icon:https://user-images.githubusercontent.com/22700758/191449379-f9f56204-0e31-4a16-be5a-331f52696a73.png        ]
# [version: 2.5.0]
# [description: ✨青龙京东COOKIE处理助手✨<br>支持设置多容器支持设置关键词识别同步到指定容器<br>🌸7.7更新：判断京东CK有效性，无效禁止上传<br>🌸4.15更新：支持wsck自动转换上传<br><img src="https://joh.obs.cn-east-3.myhuaweicloud.com/image/gallery/CK%E7%AE%A1%E7%90%86.png">]
# [param: {"required":false,"key":"Joh_CK.Name1","bool":false,"placeholder":"容器名称1","name":"容器名称1","desc":"容器1的名称"}]
# [param: {"required":true,"key":"Joh_CK.container1","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret","name":"设置CK容器1","desc":"分隔使用丨这个符号"}]
# [param: {"required":true,"key":"Joh_CK.Keywords1","bool":false,"placeholder":"比如: pt_key","name":"识别关键词1","desc":"识别关键词1<br>如：pt_key"}]
# [param: {"required":false,"key":"Joh_CK.Name2","bool":false,"placeholder":"容器名称2","name":"容器名称2","desc":"容器2的名称"}]
# [param: {"required":true,"key":"Joh_CK.container2","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret","name":"设置CK容器2","desc":"分隔使用丨这个符号"}]
# [param: {"required":true,"key":"Joh_CK.Keywords2","bool":false,"placeholder":"比如: pt_key","name":"设置关键词2","desc":"设置关键词2<br>如：pt_key"}]
# [param: {"required":true,"key":"dd_fukuda_config.proxy","bool":false,"placeholder":"例:http://192.168.10.7:8081","name":"代理池","desc":"本地代理池链接"}]
# [param: {"required":true,"key":"dd_fukuda_config.proxyapi","bool":false,"placeholder":"例:http://192.168.10.7:8080/open/proxy?token=19341","name":"代理API","desc":"代理API"}]

import middleware
import base64
import importlib.util
import json
import os
import random
import re
import time
import uuid
import urllib.parse  # 导入 urllib.parse 模块用于 URL 编码
import requests  # 导入 requests 模块用于发送 HTTP 请求
from hashlib import md5

# 动态加载 middleware.ql 模块
def load_module(file_path):
    module_name = os.path.splitext(os.path.basename(file_path))[0].replace('.', '_')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise FileNotFoundError(f"无法加载模块: {file_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 尝试多个可能的文件名（支持 middleware.ql.py 和 middleware_ql.py）
middleware_ql = None
ql_module_path = None

# 候选路径列表（按优先级）
candidates = [
    "middleware.ql.py",           # 原始文件名
    "middleware_ql.py",           # 下划线版本
    os.path.join("middleware", "ql.py"),  # 子目录版本
]

for candidate in candidates:
    try:
        middleware_ql = load_module(candidate)
        ql_module_path = candidate
        print(f"[COOKIE处理] 成功加载模块: {candidate}")
        break
    except Exception as e:
        print(f"[COOKIE处理] 加载模块失败 {candidate}: {e}")
        continue

if middleware_ql is None:
    raise ImportError(
        f"无法加载 middleware.ql 模块，已尝试: {candidates}\n"
        f"请确保以下任一文件存在:\n"
        f"  - middleware.ql.py\n"
        f"  - middleware_ql.py\n"
        f"  - middleware/ql.py"
    )

# 引入青龙模块
QL_API = middleware_ql.QL_API
Env = middleware_ql.Env

requests.packages.urllib3.disable_warnings()

WSKEY_PROXY_BUCKET = "dd_fukuda_config"
WSKEY_PROXY = middleware.bucketGet(bucket=WSKEY_PROXY_BUCKET, key="proxy") or None
WSKEY_PROXY_API = middleware.bucketGet(bucket=WSKEY_PROXY_BUCKET, key="proxyapi") or None
JD_UA = ""

# 从数据库获取容器1配置
container1_config_str = middleware.bucketGet("Joh_CK", "container1")
if not container1_config_str:
    raise Exception("容器1配置未设置")
container1_parts = container1_config_str.split("丨")
if len(container1_parts) != 3:
    raise Exception("容器1配置格式错误，应为 URL丨ClientID丨ClientSecret")
container1 = {
    "url": container1_parts[0],
    "client_id": container1_parts[1],
    "client_secret": container1_parts[2],
}

# 从数据库获取容器2配置
container2_config_str = middleware.bucketGet("Joh_CK", "container2")
if not container2_config_str:
    raise Exception("容器2配置未设置")
container2_parts = container2_config_str.split("丨")
if len(container2_parts) != 3:
    raise Exception("容器2配置格式错误，应为 URL丨ClientID丨ClientSecret")
container2 = {
    "url": container2_parts[0],
    "client_id": container2_parts[1],
    "client_secret": container2_parts[2],
}

# 从数据库获取容器1关键词配置
keywords1_str = middleware.bucketGet("Joh_CK", "Keywords1")
if not keywords1_str:
    raise Exception("容器1关键词未设置")
keywords1 = keywords1_str.split(",")

# 从数据库获取容器2关键词配置
keywords2_str = middleware.bucketGet("Joh_CK", "Keywords2")
if not keywords2_str:
    raise Exception("容器2关键词未设置")
keywords2 = keywords2_str.split(",")

# 从数据库获取容器1名称配置
name1_str = middleware.bucketGet("Joh_CK", "Name1")
container1_name = name1_str if name1_str else "容器1"

# 从数据库获取容器2名称配置
name2_str = middleware.bucketGet("Joh_CK", "Name2")
container2_name = name2_str if name2_str else "容器2"

def process_cookie(cookie_str):
    pt_key_match = re.search(r"pt_key=([a-zA-Z0-9_%-]+)[;；]", cookie_str)
    pt_pin_match = re.search(r"pt_pin=([\w%-]+)[;；]", cookie_str)
    
    if not pt_key_match or not pt_pin_match:
        # 尝试仅匹配 pt_key
        pt_key_match = re.search(r"pt_key=([a-zA-Z0-9_%-]+)[;；]", cookie_str)
        if pt_key_match:
            return f"pt_key={pt_key_match.group(1)};"
        return None
    
    pt_key = pt_key_match.group(1)
    pt_pin = pt_pin_match.group(1)
    
    return f"pt_key={pt_key};pt_pin={pt_pin};"

def extract_wskey(cookie_str):
    pin_match = re.search(r"pin=([^;；]+)[;；]", cookie_str)
    wskey_match = re.search(r"wskey=([^;；]+)[;；]", cookie_str)
    if not pin_match or not wskey_match:
        return None
    return f"pin={pin_match.group(1)};wskey={wskey_match.group(1)};"

def build_proxy_dict(proxy_text):
    if not proxy_text:
        return None
    proxy_text = str(proxy_text).strip()
    if not proxy_text:
        return None
    if proxy_text.startswith(("http://", "https://")):
        return {"http": proxy_text, "https": proxy_text}
    return {"http": f"http://{proxy_text}", "https": f"http://{proxy_text}"}

def fetch_api_proxy_once():
    if not WSKEY_PROXY_API:
        return None
    try:
        response = requests.get(WSKEY_PROXY_API, timeout=8)
        if response.status_code != 200:
            print(f"[COOKIE处理] 代理API返回异常: {response.status_code}")
            return None
        proxy_dict = build_proxy_dict(response.text)
        print(f"[COOKIE处理] 代理API返回: {response.text.strip()}")
        return proxy_dict
    except requests.RequestException as e:
        print(f"[COOKIE处理] 获取API代理失败: {e}")
        return None

def get_api_proxy_with_retries(retries=5):
    retries = max(1, min(retries, 5))
    for _ in range(retries):
        proxy_dict = fetch_api_proxy_once()
        if proxy_dict:
            return proxy_dict
        time.sleep(0.3)
    return None

def get_static_proxy():
    return build_proxy_dict(WSKEY_PROXY)

def randomstr(num):
    return "".join(str(uuid.uuid4()).split("-"))[:num]

def randomstr1(num):
    return "".join(random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(num))

def sign_core(inarg: bytes):
    key = b"80306f4370b39fd5630ad0529f77adb6"
    mask = [0x37, 0x92, 0x44, 0x68, 0xA5, 0x3D, 0xCC, 0x7F, 0xBB, 0x0F, 0xD9, 0x88, 0xEE, 0x9A, 0xE9, 0x5A]
    array = [0 for _ in range(len(inarg))]
    for i in range(len(inarg)):
        r0 = int(inarg[i])
        r2 = mask[i & 0xF]
        r4 = int(key[i & 7])
        r0 = r2 ^ r0
        r0 = r0 ^ r4
        r0 = r0 + r2
        r2 = r2 ^ r0
        r1 = int(key[i & 7])
        r2 = r2 ^ r1
        array[i] = r2 & 0xFF
    return bytes(array)

def base64_encode(text):
    return base64.b64encode(text.encode("utf-8")).decode("utf-8").translate(
        str.maketrans(
            "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/",
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        )
    )

def randomeid():
    return "eidAaf8081218as20a2GM%s7FnfQYOecyDYLcd0rfzm3Fy2ePY4UJJOeV0Ub840kG8C7lmIqt3DTlc11fB/s4qsAP8gtPTSoxu" % randomstr1(20)

def get_ep(jduuid: str = ""):
    if not jduuid:
        jduuid = randomstr(16)
    ts = str(int(time.time() * 1000))
    bsjduuid = base64_encode(jduuid)
    area = base64_encode(
        "%s_%s_%s_%s" % (
            random.randint(1, 10000),
            random.randint(1, 10000),
            random.randint(1, 10000),
            random.randint(1, 10000),
        )
    )
    d_model = base64_encode(random.choice(["Mi11Ultra", "Mi11", "Mi10"]))
    ep = (
        '{"hdid":"JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",'
        '"ts":%s,"ridx":-1,"cipher":{"area":"%s","d_model":"%s",'
        '"wifiBssid":"dW5hbw93bq==","osVersion":"CJS=","d_brand":"WQvrb21f",'
        '"screen":"CtS1DIenCNqm","uuid":"%s","aid":"%s","openudid":"%s"},'
        '"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"}'
        % (int(ts) - random.randint(100, 1000), area, d_model, bsjduuid, bsjduuid, bsjduuid)
    )
    return ep, jduuid, ts

def get_sign(function_id, body, client="android", client_version="11.2.8", jduuid=""):
    if isinstance(body, dict):
        body = json.dumps(body, separators=(",", ":"), ensure_ascii=False)

    ep, suid, st = get_ep(jduuid)
    sv = random.choice(["102", "111", "120"])
    all_arg = "functionId=%s&body=%s&uuid=%s&client=%s&clientVersion=%s&st=%s&sv=%s" % (
        function_id, body, suid, client, client_version, st, sv
    )
    sign = md5(base64.b64encode(sign_core(str.encode(all_arg)))).hexdigest()
    return (
        "body=%s&clientVersion=%s&client=%s&sdkVersion=31&lang=zh_CN&harmonyOs=0"
        "&networkType=wifi&oaid=%s&ef=1&ep=%s&st=%s&sign=%s&sv=%s"
        % (body, client_version, client, suid, urllib.parse.quote(ep), st, sign, sv)
    )

def randomuserAgent():
    global JD_UA
    letters = "abcdefghijklmnopqrstuvwxyz0123456789"
    struuid = "".join(random.choices(letters, k=40))
    addressid = "".join(random.choices("1234567898647", k=10))
    ios_ver = random.choice(["15.1.1", "14.5.1", "14.4", "14.3", "14.2", "14.1", "14.0.1"])
    ios_v = ios_ver.replace(".", "_")
    client_version = random.choice(["10.3.0", "10.2.7", "10.2.4"])
    iphone = random.choice(["8", "9", "10", "11", "12", "13"])
    adid = (
        "".join(random.choices("0987654321ABCDEF", k=8)) + "-" +
        "".join(random.choices("0987654321ABCDEF", k=4)) + "-" +
        "".join(random.choices("0987654321ABCDEF", k=4)) + "-" +
        "".join(random.choices("0987654321ABCDEF", k=4)) + "-" +
        "".join(random.choices("0987654321ABCDEF", k=12))
    )
    JD_UA = (
        f"jdapp;iPhone;{client_version};{ios_ver};{struuid};network/wifi;"
        f"ADID/{adid};model/iPhone{iphone},1;addressid/{addressid};appBuild/167707;"
        f"jdSupportDarkMode/0;Mozilla/5.0 (iPhone; CPU iPhone OS {ios_v} like Mac OS X) "
        f"AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/null;supportJDSHWK/1"
    )

def getcookie_wskey(wskey: str, proxys=None):
    body = "body=%7B%22to%22%3A%22https%3A//plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html%22%7D"
    pin_match = re.findall(r"pin=([^;]*);", wskey)
    pin = pin_match[0] if pin_match else ""
    token = "xxx"

    for num in range(5):
        sign_str = get_sign(
            "genToken",
            {"url": "https://plogin.m.jd.com/jd-mlogin/static/html/appjmp_blank.html"},
            "android",
            "11.2.8",
        )
        if not sign_str:
            continue
        url = f"http://api.m.jd.com/client.action?functionId=genToken&{sign_str}"
        headers = {
            "cookie": wskey,
            "user-agent": JD_UA,
            "accept-language": "zh-Hans-CN;q=1, en-CN;q=0.9",
            "content-type": "application/x-www-form-urlencoded;",
        }
        try:
            kwargs = {"verify": False}
            if proxys:
                kwargs["proxies"] = proxys if isinstance(proxys, dict) else {"http": proxys, "https": proxys}
            response = requests.post(url=url, headers=headers, data=body, timeout=5, **kwargs)
            data = response.json()
            token = data.get("tokenKey", "xxx")
        except Exception as e:
            print(f"[COOKIE处理] {urllib.parse.unquote(pin)} 获取 token 失败: {e}")
            time.sleep(1)
            randomuserAgent()
            continue

        if token != "xxx":
            break

        print(f"[COOKIE处理] {urllib.parse.unquote(pin)} 获取 token 返回空，准备重试")
        time.sleep(1)
        randomuserAgent()

    if token == "xxx":
        return "Error"

    res = {}
    for num in range(5):
        try:
            kwargs = {"verify": False, "allow_redirects": False}
            if proxys:
                kwargs["proxies"] = proxys if isinstance(proxys, dict) else {"http": proxys, "https": proxys}
            response = requests.get(
                url="https://un.m.jd.com/cgi-bin/app/appjmp",
                params={
                    "tokenKey": token,
                    "to": "https://plogin.m.jd.com/cgi-bin/m/thirdapp_auth_page",
                    "client_type": "android",
                    "appid": 879,
                    "appup_type": 1,
                },
                timeout=5,
                **kwargs,
            )
            res = response.cookies.get_dict()
            break
        except Exception as e:
            print(f"[COOKIE处理] {urllib.parse.unquote(pin)} 获取 cookie 失败: {e}")
            time.sleep(1)
            randomuserAgent()
            if num == 4:
                return "Error"

    try:
        if "app_open" in res.get("pt_key", ""):
            return f"pt_key={res['pt_key']};pt_pin={res['pt_pin']};"
        return "Error:" + str(res)
    except Exception:
        print(f"[COOKIE处理] 获取 cookie 返回异常: {res}")
        return "Error"

def convert_wskey_to_cookie(wskey_str):
    cookie = "Error"

    for attempt in range(1, 4):
        try:
            randomuserAgent()
            proxys = get_api_proxy_with_retries(5) or get_static_proxy()
            print(f"[COOKIE处理] wskey 转换第 {attempt} 次使用代理: {proxys}")
            cookie = getcookie_wskey(wskey_str, proxys=proxys)
            print(f"[COOKIE处理] wskey 转换第 {attempt} 次结果: {cookie}")
            if isinstance(cookie, str) and cookie.startswith("pt_key=") and "app_open" in cookie:
                return process_cookie(cookie)
        except Exception as e:
            print(f"[COOKIE处理] wskey 转换第 {attempt} 次异常: {e}")

        if attempt < 3:
            time.sleep(1)

    print(f"[COOKIE处理] wskey 转换失败: {cookie}")
    return None

def extract_pt_pin(cookie_str):
    pin_match = re.search(r"pt_pin=([^;；]+)[;；]", cookie_str or "")
    return pin_match.group(1) if pin_match else None

def extract_raw_pin(wskey_str):
    pin_match = re.search(r"pin=([^;；]+)[;；]", wskey_str or "")
    return pin_match.group(1) if pin_match else None

def get_env_id(env_item):
    return env_item.get("id") or env_item.get("_id")

def choose_container(sender):
    sender.reply(f"请选择要登录的服务器（回复数字）\n【1】{container1_name}\n【2】{container2_name}")
    choice = (sender.listen(30000) or "").strip()
    if choice == '1':
        return [(container1_name, container1)]
    if choice == '2':
        return [(container2_name, container2)]
    sender.reply("❌ 选择无效，操作已取消")
    return None

def find_env_by_name_and_pin(env_items, env_name, pin, pin_key):
    for env_item in env_items:
        if env_item.get("name") != env_name:
            continue
        value = env_item.get("value", "")
        pin_match = re.search(rf"{re.escape(pin_key)}=([^;；]+)[;；]", value)
        if pin_match and pin_match.group(1) == pin:
            return env_item
    return None

def extract_created_env_ids(response):
    data = response.get("data")
    if isinstance(data, list):
        return [item.get("id") or item.get("_id") for item in data if isinstance(item, dict) and (item.get("id") or item.get("_id"))]
    if isinstance(data, dict):
        env_id = data.get("id") or data.get("_id")
        return [env_id] if env_id else []
    return []

def upsert_env_by_pin(env, env_name, value, pin, pin_key):
    all_envs = env.get_env_list()
    if all_envs.get("code") != 200:
        return False, "", f"获取环境变量失败：{all_envs.get('message', all_envs)}"

    existing_env = find_env_by_name_and_pin(all_envs.get("data", []), env_name, pin, pin_key)
    if existing_env:
        env_id = get_env_id(existing_env)
        if not env_id:
            return False, "", "未找到环境变量ID"
        update_response = env.update_varible(env_id, env_name, value, f"{pin}")
        if update_response.get("code") != 200:
            return False, "", update_response.get("message", "更新失败")
        env.enable_variable([env_id])
        return True, "更新", ""

    create_response = env.create_variable(env_name, value, f"{pin}")
    if create_response.get("code") != 200:
        return False, "", create_response.get("message", "创建失败")

    created_ids = extract_created_env_ids(create_response)
    if created_ids:
        env.enable_variable(created_ids)
    return True, "添加", ""

def upload_jd_cookie(env, pure_cookie):
    pin = extract_pt_pin(pure_cookie)
    if not pin:
        return False, "", "无法提取pt_pin", pure_cookie

    normalized_cookie = pure_cookie
    if any(ord(char) > 127 for char in pin):
        encoded_pin = urllib.parse.quote(pin)
        normalized_cookie = re.sub(r"pt_pin=[^;；]+[;；]", f"pt_pin={encoded_pin};", normalized_cookie)
        pin = encoded_pin

    success, action, message = upsert_env_by_pin(env, "JD_COOKIE", normalized_cookie, pin, "pt_pin")
    return success, action, message, normalized_cookie

def check_ck(cookie):
    """检测CK是否有效"""
    REQUEST_TIMEOUT = 15
    result1 = {"success": False, "message": "", "valid": False}
    result2 = {"success": False, "message": "", "valid": False}

    # 检测接口1（已调整为与接口2逻辑一致）
    try:
        headers = {
            'Cookie': cookie,
            'Referer': 'https://h5.m.jd.com/',
            'User-Agent': 'jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'
        }
        response = requests.get('https://plogin.m.jd.com/cgi-bin/ml/islogin', headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        status = data.get('islogin', 'undefined')
        result1 = {
            'success': status == "1",
            'message': '接口1检测正常' if status == "1" else f'接口1检测异常[{status}]',
            'valid': status == "1"
        }
        # 如果接口1检测成功，直接返回结果，不再检测接口2
        if result1['success']:
            return result1
    except Exception as e:
        result1 = {'success': False, 'message': f'接口检测错误: {str(e)}', 'valid': False}

    # 如果接口1检测失败，检测接口2
    try:
        headers = {
            'Cookie': cookie,
            'Referer': 'https://h5.m.jd.com/',
            'User-Agent': 'jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1'
        }
        response = requests.get('https://plogin.m.jd.com/cgi-bin/ml/islogin', headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()
        status = data.get('islogin', 'undefined')
        result2 = {
            'success': status == "1",
            'message': '接口2检测正常' if status == "1" else f'接口2检测异常[{status}]',
            'valid': status == "1"
        }
    except Exception as e:
        result2 = {'success': False, 'message': f'接口检测错误: {str(e)}', 'valid': False}

    # 只要有一个接口检测成功就认为CK有效
    return {
        'valid': result1['valid'] or result2['valid'],
        'detail': f'{result1["message"]} | {result2["message"]}'
    }

class CookieHandler:
    def __init__(self, sender):
        self.sender = sender

    def handle(self, cookie_str, containers=None):
        try:
            sender_id = self.sender.getUserID()
            im_type = self.sender.getImtype().upper()

            # 处理cookie
            pure_cookie = process_cookie(cookie_str)
            wskey_str = extract_wskey(cookie_str)

            if not pure_cookie and not wskey_str:
                self.sender.reply("❌ 无效的cookie格式")
                return

            final_pin = None

            if wskey_str:
                wskey_pin = extract_raw_pin(wskey_str)
                if not wskey_pin:
                    self.sender.reply("❌ 无法提取wskey中的pin")
                    return

                if containers is None:
                    containers = choose_container(self.sender)
                    if not containers:
                        return

                for container_name, container in containers:
                    self.sender.reply(f"⏳ 已选择{container_name}，正在尝试上传，请稍候...")
                    ql = QL_API(container["url"], container["client_id"], container["client_secret"])
                    token = ql.get_token()
                    if not token:
                        self.sender.reply(f"❌ 无法连接到{container_name}，请检查配置")
                        continue

                    env = Env(token, ql.url)
                    pure_cookie = convert_wskey_to_cookie(wskey_str)
                    if not pure_cookie:
                        self.sender.reply(f"❌ 此CK失效，请重新抓包后提交\n未保存到{container_name}：\n账号：{wskey_pin}")
                        continue

                    wsck_success, wsck_action, wsck_message = upsert_env_by_pin(env, "BBK_WSCK", wskey_str, wskey_pin, "pin")
                    if not wsck_success:
                        self.sender.reply(f"❌ {wsck_action or '处理'}BBK_WSCK到{container_name}失败：{wsck_message}")
                        continue

                    jd_success, jd_action, jd_message, pure_cookie = upload_jd_cookie(env, pure_cookie)
                    if jd_success:
                        final_pin = extract_pt_pin(pure_cookie) or final_pin
                        self.sender.reply(f"✅ BBK_WSCK已成功{wsck_action}到{container_name}：\n账号：{wskey_pin}\n✅ JD_COOKIE已成功{jd_action}到{container_name}：\n账号：{final_pin}")
                    else:
                        self.sender.reply(f"⚠️ BBK_WSCK已成功{wsck_action}到{container_name}：\n账号：{wskey_pin}\n❌ 上传JD_COOKIE到{container_name}失败：{jd_message}")

                if final_pin:
                    pin_db = f"pin{im_type}"
                    middleware.bucketSet(pin_db, final_pin, sender_id)
                return

            # 检测CK是否有效
            ck_check_result = check_ck(pure_cookie)
            if not ck_check_result['valid']:
                self.sender.reply("❌ 此CK失效，请重新抓包后提交")
                return

            # 如果没有传入containers，则使用默认逻辑
            if containers is None:
                keyword_source = f"{cookie_str}\n{pure_cookie}"

                # 检查是否包含容器1关键词
                use_container1 = False
                for keyword in keywords1:
                    if keyword in keyword_source:
                        use_container1 = True
                        break

                # 检查是否包含容器2关键词
                use_container2 = False
                for keyword in keywords2:
                    if keyword in keyword_source:
                        use_container2 = True
                        break

                # 如果同时匹配两个容器关键词，提示用户选择
                if use_container1 and use_container2:
                    containers = choose_container(self.sender)
                    if not containers:
                        return
                else:
                    # 否则根据匹配情况添加容器
                    containers = []
                    if use_container1:
                        containers.append((container1_name, container1))
                    if use_container2:
                        containers.append((container2_name, container2))
                    if not containers:
                        containers.append((container1_name, container1))

            for container_name, container in containers:
                ql = QL_API(container["url"], container["client_id"], container["client_secret"])
                token = ql.get_token()
                if not token:
                    self.sender.reply(f"❌ 无法连接到{container_name}，请检查配置")
                    continue

                env = Env(token, ql.url)
                upload_success, upload_action, upload_message, pure_cookie = upload_jd_cookie(env, pure_cookie)
                pure_pin = extract_pt_pin(pure_cookie)
                if upload_success:
                    self.sender.reply(f"✅ 账号已成功{upload_action}到{container_name}：\n账号：{pure_pin}")
                else:
                    self.sender.reply(f"❌ 上传cookie到{container_name}失败：{upload_message}")

            # 存储账号与用户ID的关联关系，保持大写格式
            pin = extract_pt_pin(pure_cookie)
            if pin:
                pin_db = f"pin{im_type}"
                middleware.bucketSet(pin_db, pin, sender_id)
                # self.sender.reply(f"✅ 已将账号 {pin} 与您的{im_type}账号关联")

        except Exception as e:
            print(f"插件出错: {str(e)}")
            self.sender.reply(f"❌ 出错：{str(e)}")

def handle_cookie():
    try:
        # 获取发送者ID
        sender_id = middleware.getSenderID()
        if not sender_id:
            middleware.reply("❌ 无法获取您的用户ID，请稍后重试")
            return

        # 使用Sender类
        sender = middleware.Sender(sender_id)

        # 获取用户发送的消息
        message = sender.getMessage()

        # 处理cookie
        cookie_str = message.strip()

        # 提取纯cookie部分
        pure_cookie = process_cookie(cookie_str)
        if not pure_cookie and not extract_wskey(cookie_str):
            # 如果不是cookie，直接返回，不做处理
            return

        cookie_handler = CookieHandler(sender)
        cookie_handler.handle(cookie_str)

    except Exception as e:
        print(f"插件出错: {str(e)}")
        middleware.reply(f"❌ 出错：{str(e)}")

# 调用插件主函数
handle_cookie()
