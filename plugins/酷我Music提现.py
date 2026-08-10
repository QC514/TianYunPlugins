#[pin:false]
#[disable:false]
#[public:true]
#[rule: ^(酷我提现|酷我提现次数检测|酷我提现次数迁移)$]
#[version: 3.11]
#[price: 38.88]
#[cron: 0 8 * * *]
#[title: 酷我Music提现]
#[author: sky2022]
#[admin: false]
#[icon: https://img.cdn1.vip/i/69d62b975e88c_1775643543.png]
#[description: 酷我提现插件，插件内置提现！等候定时提现和立即提现，采用次数制，用户可充值次数来进行提现，提现成功则扣除次数<br>指令:酷我提现、酷我提现次数检测<br>格式：手机号#密码<br>无需抓包，无需抓包<br>内置定时检测次数数量]

# 全局变量声明
today_date = None
today_time = None
KuwoTXmoney = None
KuwoTXcoin = None
proxy_manager = None
withdraw_delay = 0.0  # 默认值设为0，支持小数
_time_offset = None  # NTP时间偏移量缓存（秒）

import re
import middleware
import requests
import json
import hashlib
import urllib.parse
from datetime import datetime, timedelta
import base64
import random
import time
from decimal import Decimal
from urllib.parse import unquote
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import threading
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Tuple, List
import urllib3
from urllib3.exceptions import InsecureRequestWarning
try:
    import ntplib
except ImportError:
    # 如果没有安装ntplib，可以使用requests获取时间
    pass

# 禁用不安全请求警告
urllib3.disable_warnings(InsecureRequestWarning)

# [param: {"required":true,"key":"dd_KuwoTX_PluginsData.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_KuwoTX_PluginsData.proxy_api","bool":false,"placeholder":"必填项,代理API地址","name":"代理API","desc":"提现使用的代理API接口"}]
# 上车价格
# [param: {"required":true,"key":"dd_KuwoTX_PluginsData.KuwoTXmoney","bool":false,"placeholder":"例:1.00,不填为0元","name":"提现单价","desc":"每次提现价格(单位:元)"}]
# 积分上车价格
# [param: {"required":true,"key":"dd_KuwoTX_PluginsData.KuwoTXcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"每次提现需要多少积分（只能为整数不能为小数）"}]
# 提现延迟设置
# [param: {"required":false,"key":"dd_KuwoTX_PluginsData.withdraw_delay","bool":false,"placeholder":"默认为0秒,支持小数如0.3","name":"提现延迟","desc":"整点提现时延后发包的秒数，支持小数(范围0-5,例如0.3)"}]
# [param: {"required":true,"key":"dd_KuwoTX_PluginsData.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_KuwoTX_bind', key=userid)

class ProxyManager:
    def __init__(self, proxy_api: str):
        self.proxy_api = proxy_api
        self.proxy_lock = threading.Lock()
        self.proxy_cache = {}
        self._proxy_pool = []  # 预获取的代理池
        self.last_error = ''
        self._fatal_proxy_error = False

    def _mask_proxy(self, proxy: str) -> str:
        """隐藏代理账号密码，避免日志泄露。"""
        if '@' not in proxy:
            return proxy
        return f"***@{proxy.rsplit('@', 1)[-1]}"

    def _valid_port(self, port: str) -> bool:
        return port.isdigit() and 0 < int(port) <= 65535

    def _split_host_port(self, proxy: str) -> Tuple[Optional[str], Optional[int]]:
        """从标准化后的 user:pass@host:port / host:port 中取验证用地址。"""
        target = proxy.rsplit('@', 1)[-1].strip()

        if target.startswith('['):
            end = target.find(']')
            if end > 0 and target[end + 1:end + 2] == ':':
                port = target[end + 2:]
                if self._valid_port(port):
                    return target[1:end], int(port)
            return None, None

        if ':' not in target:
            return None, None

        host, port = target.rsplit(':', 1)
        if host and self._valid_port(port):
            return host, int(port)
        return None, None

    def _normalize_proxy(self, raw_proxy: str) -> Optional[str]:
        """兼容 ip:port、http://ip:port、user:pass@ip:port、ip:port:user:pass。"""
        proxy = (raw_proxy or '').strip().strip('"\' ,;')
        if not proxy:
            return None

        if '://' in proxy:
            try:
                parsed = urllib.parse.urlparse(proxy)
                host = parsed.hostname
                port = parsed.port
                if host and port and self._valid_port(str(port)):
                    auth = ''
                    if parsed.username:
                        username = urllib.parse.quote(urllib.parse.unquote(parsed.username), safe='')
                        password = ''
                        if parsed.password is not None:
                            password = ':' + urllib.parse.quote(urllib.parse.unquote(parsed.password), safe='')
                        auth = f"{username}{password}@"
                    host_text = f"[{host}]" if ':' in host and not host.startswith('[') else host
                    return f"{auth}{host_text}:{port}"
            except Exception:
                return None

        proxy = re.sub(r'\s+', '', proxy)

        # 部分代理商返回 ip:port:username:password，需要转成 requests 可识别的认证代理格式。
        if '@' not in proxy:
            parts = proxy.split(':')
            if len(parts) >= 4 and self._valid_port(parts[1]):
                host, port = parts[0], parts[1]
                username = urllib.parse.quote(urllib.parse.unquote(parts[2]), safe='')
                password = urllib.parse.quote(urllib.parse.unquote(':'.join(parts[3:])), safe='')
                if host and username:
                    return f"{username}:{password}@{host}:{port}"

        host, port = self._split_host_port(proxy)
        if host and port:
            return proxy
        return None

    def _proxy_candidates_from_json(self, data) -> List[str]:
        candidates = []
        if isinstance(data, dict):
            lower = {str(k).lower(): v for k, v in data.items()}
            host = lower.get('ip') or lower.get('host') or lower.get('proxyhost') or lower.get('server')
            port = lower.get('port') or lower.get('proxyport')
            if host and port:
                candidates.append(f"{host}:{port}")

            proxy_value = lower.get('proxy') or lower.get('addr') or lower.get('address')
            if proxy_value:
                candidates.append(str(proxy_value))

            for value in data.values():
                candidates.extend(self._proxy_candidates_from_json(value))
        elif isinstance(data, list):
            for item in data:
                candidates.extend(self._proxy_candidates_from_json(item))
        elif isinstance(data, str):
            candidates.append(data)
        return candidates

    def _proxy_error_from_json(self, data) -> Optional[str]:
        """识别代理商JSON错误响应，避免把 status:200 误当代理。"""
        if not isinstance(data, dict):
            return None

        lower = {str(k).lower(): v for k, v in data.items()}
        message = (
            lower.get('message')
            or lower.get('msg')
            or lower.get('error')
            or lower.get('errmsg')
            or lower.get('desc')
            or lower.get('description')
        )
        code = lower.get('code')
        data_value = lower.get('data')

        if message and (data_value is None or str(code) not in ('0', '200', 'success', 'true', 'None')):
            return str(message)
        return None

    def _extract_proxies(self, response_text: str) -> List[str]:
        """从代理API响应中提取一个或多个可用代理。"""
        proxies = []
        seen = set()
        endpoint_index = {}

        def add(candidate: str):
            normalized = self._normalize_proxy(candidate)
            if not normalized or normalized in seen:
                return

            host, port = self._split_host_port(normalized)
            endpoint = (host, port) if host and port else None
            if endpoint in endpoint_index:
                old_index = endpoint_index[endpoint]
                old_proxy = proxies[old_index]
                if '@' in normalized and '@' not in old_proxy:
                    seen.discard(old_proxy)
                    proxies[old_index] = normalized
                    seen.add(normalized)
                return

            if normalized:
                seen.add(normalized)
                if endpoint:
                    endpoint_index[endpoint] = len(proxies)
                proxies.append(normalized)

        text = (response_text or '').strip()
        if not text:
            return proxies

        try:
            data = json.loads(text)
            json_error = self._proxy_error_from_json(data)
            for candidate in self._proxy_candidates_from_json(data):
                add(candidate)
            if json_error and not proxies:
                self.last_error = json_error
                self._fatal_proxy_error = True
                print(f"[代理] 代理API返回错误: {json_error}")
            return proxies
        except Exception:
            pass

        for line in text.replace('\r', '\n').split('\n'):
            for part in re.split(r'[\s,;]+', line.strip()):
                add(part)

        proxy_pattern = (
            r'(?:(?:https?|socks5?)://)?'
            r'(?:[^\s/@:]+(?::[^\s/@]+)?@)?'
            r'(?:\[[0-9A-Fa-f:]+\]|(?:\d{1,3}\.){3}\d{1,3}|localhost|(?:[A-Za-z0-9-]+\.)+[A-Za-z0-9-]+)'
            r':\d{2,5}'
        )
        for match in re.finditer(proxy_pattern, text):
            add(match.group(0))

        return proxies

    def _short_response(self, text: str, limit: int = 120) -> str:
        brief = re.sub(r'\s+', ' ', (text or '').strip())
        if len(brief) > limit:
            brief = brief[:limit] + '...'
        return brief or '<空响应>'

    def _debug_api_response(self, response, prefix: str = "代理API"):
        """打印代理API原始响应，便于定位代理商返回格式变化。"""
        try:
            body = response.text or ''
        except Exception:
            body = '<无法读取响应体>'

        display = repr(body)
        if len(display) > 2000:
            display = display[:2000] + "...<已截断>"
        print(f"[代理调试] {prefix}状态码: {getattr(response, 'status_code', '<未知>')}")
        print(f"[代理调试] {prefix}原始响应: {display}")

    def _debug_proxy_candidates(self, proxies: List[str]):
        if not proxies:
            print("[代理调试] 解析候选代理: []")
            return
        masked = [self._mask_proxy(proxy) for proxy in proxies]
        print(f"[代理调试] 解析候选代理: {masked}")

    def get_last_error(self) -> str:
        return self.last_error or '代理API未返回可用代理'

    def validate_proxy(self, proxy: str) -> bool:
        """轻量级代理验证：TCP connect测试（比HTTP快10倍）"""
        normalized = self._normalize_proxy(proxy)
        if not normalized:
            print(f"[代理] 验证失败: 无法识别代理格式: {self._short_response(proxy)}")
            return False

        host, port = self._split_host_port(normalized)
        if not host or not port:
            print(f"[代理] 验证失败: 无法解析代理地址: {self._mask_proxy(normalized)}")
            return False

        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            if result != 0:
                print(f"[代理] 验证失败: TCP连接失败 proxy={self._mask_proxy(normalized)} host={host} port={port} code={result}")
            return result == 0
        except Exception as e:
            print(f"[代理] 验证失败: proxy={self._mask_proxy(normalized)} host={host} port={port} error={str(e)}")
            return False
        finally:
            if sock:
                sock.close()

    def get_proxy(self) -> Optional[str]:
        """从代理池获取代理，池空则从API获取"""
        with self.proxy_lock:
            if self._proxy_pool:
                return self._proxy_pool.pop(0)

        if self._fatal_proxy_error:
            return None

        max_retries = 3
        self.last_error = ''
        for attempt in range(max_retries):
            try:
                if not self.proxy_api:
                    print("[错误] 未配置代理API")
                    self.last_error = '未配置代理API'
                    self._fatal_proxy_error = True
                    return None

                response = requests.get(self.proxy_api, timeout=10, verify=False)
                if response.status_code != 200:
                    print(f"[错误] 代理API返回状态码: {response.status_code}")
                    self.last_error = f'代理API返回状态码 {response.status_code}'
                    continue

                proxies = self._extract_proxies(response.text)
                if self._fatal_proxy_error:
                    return None

                self._debug_api_response(response)
                self._debug_proxy_candidates(proxies)
                if not proxies:
                    if not self.last_error:
                        self.last_error = f'API响应未解析到代理: {self._short_response(response.text)}'
                    print(f"[代理] {self.last_error}")
                    continue

                for proxy in proxies:
                    if self.validate_proxy(proxy):
                        return proxy

                if not self.last_error:
                    self.last_error = '代理验证失败'

            except Exception as e:
                print(f"[代理] 获取代理失败: {str(e)}")
                self.last_error = f'获取代理异常: {str(e)}'
                continue

        return None

    def prefetch_proxies(self, count: int):
        """预获取多个代理到代理池（在等待期间调用）"""
        print(f"[代理] 开始预获取 {count} 个代理...")
        fetched = 0
        if not self.proxy_api:
            print("[错误] 未配置代理API")
            self.last_error = '未配置代理API'
            self._fatal_proxy_error = True
            return

        if self._fatal_proxy_error:
            return

        for _ in range(count * 2):  # 多尝试几次以确保拿够
            if fetched >= count:
                break
            try:
                response = requests.get(self.proxy_api, timeout=10, verify=False)
                if response.status_code == 200:
                    proxies = self._extract_proxies(response.text)
                    if self._fatal_proxy_error:
                        break

                    self._debug_api_response(response, "预获取代理API")
                    self._debug_proxy_candidates(proxies)
                    if not proxies:
                        if not self.last_error:
                            self.last_error = f'预获取响应未解析到代理: {self._short_response(response.text)}'
                        print(f"[代理] {self.last_error}")
                        continue

                    for proxy in proxies:
                        if fetched >= count:
                            break
                        if self.validate_proxy(proxy):
                            with self.proxy_lock:
                                self._proxy_pool.append(proxy)
                            fetched += 1
                            print(f"[代理] 预获取成功 ({fetched}/{count}): {self._mask_proxy(proxy)}")
                else:
                    print(f"[代理] 预获取API返回状态码: {response.status_code}")
                    self.last_error = f'预获取代理API返回状态码 {response.status_code}'
            except Exception as e:
                print(f"[代理] 预获取失败: {str(e)}")
                self.last_error = f'预获取代理异常: {str(e)}'
                continue
        print(f"[代理] 预获取完成，共获取 {fetched} 个代理")

    def create_warmed_session(self, proxy: str, phone: str = "") -> requests.Session:
        """创建预热的HTTP Session（提前建立TCP+TLS连接）"""
        session = requests.Session()
        session.verify = False
        session.proxies = {
            'http': f'http://{proxy}',
            'https': f'http://{proxy}'
        }
        session.headers.update({
            "User-Agent": generate_kuwo_ua(phone),
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://h5app.kuwo.cn",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Referer": "https://h5app.kuwo.cn/apps/earning-sign/cash_out.html",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9"
        })

        # 预热连接：发送一个轻量请求建立TCP+TLS
        try:
            warmup_url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/getWithdraw"
            session.head(warmup_url, timeout=5)
            print(f"[Session] 连接预热成功: {proxy}")
        except Exception as e:
            # 预热失败不影响使用，只是首次请求会慢一点
            print(f"[Session] 连接预热失败（不影响使用）: {str(e)}")

        return session

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        if "token" in response.text:
            data = response.json()
            return data['data']['token']
    except Exception:
        sender.reply("链接青龙失败,请检查对接容器！")
        exit(0)

def PluginsData():
    """获取插件配置数据"""
    global withdraw_delay  # 添加全局变量声明
    
    KuwoTXmoney = middleware.bucketGet(bucket='dd_KuwoTX_PluginsData', key='KuwoTXmoney')
    KuwoTXcoin = middleware.bucketGet(bucket='dd_KuwoTX_PluginsData', key='KuwoTXcoin')
    proxy_api = middleware.bucketGet(bucket='dd_KuwoTX_PluginsData', key='proxy_api')
    withdraw_delay_str = middleware.bucketGet(bucket='dd_KuwoTX_PluginsData', key='withdraw_delay')
    
    if not proxy_api:
        sender.reply('未配置代理API，请检查配置')
        exit(0)
        
    # 检查提现单价是否设置
    if not KuwoTXmoney or KuwoTXmoney == '0':
        KuwoTXmoney = Decimal(0)
    else:
        try:
            KuwoTXmoney = Decimal(KuwoTXmoney)
            if KuwoTXmoney < Decimal('0.5'):
                sender.reply('提现单价不能低于0.5元，请修改配置')
                exit(0)
        except:
            sender.reply('提现单价格式错误，请检查配置')
            exit(0)
            
    if not KuwoTXcoin:
        KuwoTXcoin = 9999
    else:
        KuwoTXcoin = int(KuwoTXcoin)
    
    # 处理提现延迟设置
    try:
        if withdraw_delay_str:
            withdraw_delay = float(withdraw_delay_str)
            # 限制延迟范围在0-5秒之间
            withdraw_delay = max(0.0, min(5.0, withdraw_delay))
        else:
            withdraw_delay = 0.0
    except:
        withdraw_delay = 0.0
            
    return KuwoTXmoney, KuwoTXcoin, proxy_api, withdraw_delay

def get_payment_config():
    """获取支付配置（赞赏码 + 码支付）"""
    zsm = middleware.bucketGet('dd_KuwoTX_PluginsData', 'zsm')
    use_ma_pay = (middleware.bucketGet('dd_KuwoTX_PluginsData', 'use_ma_pay') or 'false').lower() == 'true'

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

def generate_qrcode(url):
    """生成二维码URL"""
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except:
        return None

def handle_ma_payment(money, project, ma_pay_config, on_success):
    """处理码支付流程"""
    out_trade_no = f"KWTX{int(time.time())}{userid}"
    params = {
        'pid': ma_pay_config['pid'],
        'type': ma_pay_config['type'].split(',')[0],
        'out_trade_no': out_trade_no,
        'name': f"{senderID}-酷我提现次数-{str(money)}",
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

    gateway = ma_pay_config['gateway'].rstrip('/')
    mapi_url = f"{gateway}/mapi.php"

    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(mapi_url, data=params, headers=headers, timeout=10)

        if response.status_code != 200:
            sender.reply(f"=====支付失败=====\n创建订单失败，HTTP状态码: {response.status_code}\n===================")
            exit(0)

        try:
            result = response.json()
        except:
            sender.reply("=====支付失败=====\n创建订单失败，返回数据格式错误\n===================")
            exit(0)

        code = result.get('code', 0)
        msg = result.get('msg', '未知状态')

        if code == 1:
            payurl = result.get('payurl', '')
            if not payurl:
                sender.reply("=====支付失败=====\n未获取到支付链接\n===================")
                exit(0)

            qrcode_url = generate_qrcode(payurl)
            pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
            pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
            pay_type_name = pay_type_names.get(pay_type, pay_type)

            if qrcode_url:
                try:
                    sender.replyImage(qrcode_url)
                    sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付")
                except:
                    sender.reply(f"请使用【{pay_type_name}】扫描下方二维码完成支付:\n[CQ:image,file={qrcode_url}]\n支付过程中输入'q'可取消支付")
            else:
                sender.reply(
                    f"=====码支付=====\n"
                    f"🎫 商品: {project}\n"
                    f"💰 金额: {money}元\n"
                    f"⏰ 有效期: 5分钟\n"
                    f"-------------------\n"
                    f"二维码生成失败，请点击链接完成支付:\n{payurl}\n"
                    f"==================="
                )
        else:
            sender.reply(f"=====支付失败=====\n创建订单失败: {msg}\n===================")
            exit(0)

        for i in range(60):
            check_url = f"{gateway}/xpay/epay/api.php"
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
                    on_success()
                    return True
            except Exception as e:
                print(f"查询订单状态出错: {str(e)}")

            result = sender.listen(5000)
            if result and str(result).lower() == 'q':
                sender.reply("已取消支付")
                exit(0)

        sender.reply("支付超时，请重新发起支付！")
        exit(0)

    except SystemExit:
        raise
    except Exception as e:
        sender.reply(f"支付请求失败: {str(e)}")
        exit(0)

def recognize_captcha(image_base64: str) -> str:
    """验证码识别"""
    try:
        ocr_url = 'https://ddddocr.linzixuan.work/classification'
        
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        image_base64 = image_base64.replace('data:image/jpeg;base64,', '')
        image_base64 = image_base64.replace('data:image/png;base64,', '')
        
        data = {'image': image_base64}
        response = requests.post(ocr_url, json=data, timeout=10)
        
        result = response.json()
        if not result or 'result' not in result:
            raise Exception("验证码识别失败: 返回结果无效")
            
        return result['result'].strip()
        
    except Exception as e:
        print(f"验证码识别出错: {str(e)}")
        raise

def encrypt_phone(phone: str) -> str:
    """加密手机号生成phone值"""
    try:
        key = base64.b64decode('eXNpVmtMSkhIbnZNV0NIcQ==')
        iv = base64.b64decode('aWNoWW9vWCtNYjFnUmV0UA==')
        
        data = phone.encode('utf-8')
        padded_data = pad(data, AES.block_size)
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_base64 = base64.b64encode(cipher.encrypt(padded_data)).decode('utf-8')
        
        return encrypted_base64
    except Exception as e:
        print(f"[错误] 手机号加密失败: {str(e)}")
        return None

def generate_appuid() -> str:
    """生成10位随机数字的appuid"""
    return ''.join(random.choices('0123456789', k=10))

_ANDROID_DEVICES = [
    ('Pixel 8 Pro', 'AP4A.250405.002'), ('Pixel 7', 'AP2A.240805.005'),
    ('Pixel 9', 'AD4A.250605.001'), ('SM-S9280', 'UP1A.231005.007'),
    ('SM-S9110', 'UP1A.231005.007'), ('SM-A5560', 'TP1A.220624.014'),
    ('2211133C', 'TKQ1.220829.002'), ('23127PN0CC', 'UKQ1.231003.002'),
    ('2407FPN8EC', 'VKQ1.240610.001'), ('24122RKC7C', 'BP2A.250605.031'),
    ('V2329A', 'UP1A.231005.007'), ('V2336A', 'TP1A.220624.014'),
    ('PHZ110', 'TP1A.220905.001'), ('PJZ110', 'UKQ1.240118.001'),
    ('RMX3820', 'TP1A.220905.001'), ('LE2120', 'SKQ1.211006.001'),
    ('NE2210', 'TP1A.220905.001'), ('22081212C', 'V417IR.240305.001'),
]
_ANDROID_VERSIONS = [12, 13, 14, 15, 16]
_CHROME_VERSIONS = [
    '120.0.6099.230', '122.0.6261.95', '124.0.6367.113', '126.0.6478.122',
    '128.0.6613.88', '130.0.6723.107', '133.0.6943.137', '136.0.7103.60',
    '140.0.7241.98', '144.0.7564.45', '146.0.7688.100', '148.0.7778.120',
]
_phone_ua_cache = {}

def generate_kuwo_ua(phone: str) -> str:
    """为每个手机号生成固定的随机 User-Agent"""
    if phone in _phone_ua_cache:
        return _phone_ua_cache[phone]
    seed = int(hashlib.md5(phone.encode()).hexdigest(), 16)
    model, build = _ANDROID_DEVICES[seed % len(_ANDROID_DEVICES)]
    av = _ANDROID_VERSIONS[seed % len(_ANDROID_VERSIONS)]
    cv = _CHROME_VERSIONS[(seed >> 8) % len(_CHROME_VERSIONS)]
    ua = (f'Mozilla/5.0 (Linux; Android {av}; {model} Build/{build}; wv) '
          f'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 '
          f'Chrome/{cv} Mobile Safari/537.36/ kuwopage')
    _phone_ua_cache[phone] = ua
    return ua

def login_for_withdraw(phone, password):
    """登录获取最新的loginUid和loginSid"""
    try:
        # 获取验证码
        captcha_url = 'http://www.kuwo.cn/api/common/captcha/getcode'
        captcha_params = {
            'reqId': 'bb7dd120-d1b7-11ef-b9c9-9dd176f54932',
            'httpsStatus': '1'
        }
        
        captcha_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'Referer': 'http://www.kuwo.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        response = requests.get(
            captcha_url,
            params=captcha_params,
            headers=captcha_headers
        )
        
        if 'data' not in response.json():
            raise Exception("获取验证码失败")
            
        captcha_data = response.json()['data']
        image_data = captcha_data['img']
        token = captcha_data['token']
        
        # 识别验证码
        verify_code = recognize_captcha(
            image_data.replace('data:image/jpeg;base64,', '')
        )
        
        # 执行登录
        login_url = 'https://wapi.kuwo.cn/api/www/login/loginByKw'
        login_data = json.dumps({
            'userIp': 'www.kuwo.cn',
            'uname': phone,
            'password': password,
            'verifyCode': verify_code,
            'img': image_data,
            'verifyCodeToken': token
        })
        
        login_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'http://www.kuwo.cn',
            'Referer': 'http://www.kuwo.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
        
        login_response = requests.post(
            login_url,
            params={'httpsStatus': '1'},
            data=login_data,
            headers=login_headers,
            timeout=10,
            verify=False
        )
        
        result = login_response.json()
        if result.get('code') != 200:
            error_msg = result.get('msg', '未知错误')
            if "picture captcha error" in error_msg:
                return None, None, "登录接口抽风，请再试一次即可"
            raise Exception(f"登录失败: {error_msg}")
            
        cookies = result.get('data', {}).get('cookies', {})
        if not cookies or not isinstance(cookies, dict):
            raise Exception("登录响应中没有找到有效的cookies")
            
        loginSid = cookies.get('websid')
        loginUid = cookies.get('userid')
        
        if not loginSid or not loginUid:
            raise Exception("登录响应中缺少必要的cookie信息")
            
        return loginUid, loginSid, None
        
    except Exception as e:
        return None, None, str(e)

def login(value):
    """登录账号"""
    try:
        values = value.split('#')
        if len(values) != 2:
            return "登录参数格式错误", None, False
            
        phone, password = values
        
        # 生成随机appuid
        appUid = ''.join(random.choices('0123456789', k=10))
        
        # 加密手机号
        phone_value = encrypt_phone(phone)
        if not phone_value:
            return "手机号加密失败", None, False
            
        # 重新登录获取最新的loginUid和loginSid
        loginUid, loginSid, error = login_for_withdraw(phone, password)
        if error:
            return error, None, False
            
        # 发送短信验证码
        url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/userBindPhone"
        params = {
            "loginUid": loginUid,
            "loginSid": loginSid,
            "mobile": phone_value
        }
        
        headers = {
            "User-Agent": generate_kuwo_ua(phone),
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://h5app.kuwo.cn",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Referer": "https://h5app.kuwo.cn/apps/earning-sign/cash_out.html",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9"
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            sender.reply("发送验证码失败")
            return
            
        result = response.json()
        if result.get('code') != 200:
            error_msg = result.get('msg', '未知错误')
            sender.reply(f"发送验证码失败: {error_msg}")
            return
            
        # 提示用户输入验证码
        sender.reply(f"验证码已发送至 {phone[:3]}****{phone[7:]}\n请输入收到的验证码:")
        sms_code = sender.input(60000, 1, False)
        
        if not sms_code:
            sender.reply("验证码输入超时")
            return
            
        # 使用提现接口验证账号
        withdraw_url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/getWithdraw"
        withdraw_params = {
            "encry": "",
            "type": "",
            "quotaId": "30002",
            "loginUid": loginUid,
            "loginSid": loginSid,
            "appuid": generate_appuid(),
            "source": "kwplayer_ar_12.1.4.0_40.apk",
            "version": "1",
            "phone": phone_value,
            "code": sms_code
        }
        
        response = requests.get(withdraw_url, params=withdraw_params, headers=headers)
        
        if response.status_code != 200:
            return "账号验证失败", None, False
            
        result = response.json()
        if result.get('data', {}).get('text'):
            error_msg = result['data']['text']
            
            # 这些情况表示账号是有效的
            valid_messages = [
                "每日仅能提现一次",
                "今日提现次数已用完",
                "账号存在风险",
                "提现额度已用完",
                "提现次数已用完",
                "提现时间未到",
                "当前时段额度已提完",
                "当前账户金币余额不足",
                "提现成功"
            ]
            
            if any(msg in error_msg for msg in valid_messages):
                print(f"[验证] 账号有效: {error_msg}")
                # 验证通过,生成token
                devId = ''.join(random.choices('0123456789abcdef', k=16))
                token = f"{loginUid}#{devId}#{loginSid}#{phone_value}"
                return phone, token, True
                
            # 其他错误情况
            print(f"[验证] 未知错误: {error_msg}")
            return f"账号验证失败: {error_msg}", None, False
            
        return "账号验证失败: 提现接口返回异常状态", None, False
        
    except Exception as e:
        print(f"[错误] 登录过程异常: {str(e)}")
        if "picture captcha error" in str(e):
            return "登录接口抽风，请再试一次即可", None, False
        if "登录响应中" in str(e):
            return "登录失败: 服务器返回数据格式异常", None, False
        return f"登录异常: {str(e)}", None, False

def bind():
    """绑定账号"""
    sender.reply(
        "=====酷我提现=====\n"
        "🎵 请输入登录参数:\n"
        "📝 格式: 手机号#密码\n"
        "⚠️ 建议私聊登录,密码泄露风险自负\n"
        "⭐ 输入q退出操作\n"
        "====================="
    )
    
    login_value = sender.input(120000, 1, False)
    if not login_value:
        sender.reply('输入超时！')
        exit(0)
    elif login_value.lower() == 'q':
        sender.reply('退出操作！')
        exit(0)
        
    account, token, success = login(login_value)
    if not success:
        sender.reply(f'{account}')
        exit(0)
        
    middleware.bucketSet(bucket='dd_KuwoTX_account', key=account, value=token)
    middleware.bucketSet(bucket='dd_KuwoTX_login', key=account, value=login_value)

    if not uservalue:
        accounts = [account]
        middleware.bucketSet(bucket='dd_KuwoTX_bind', key=userid, value=f'{accounts}')
        sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[酷我提现]管理账号\n===================")
    else:
        accounts = eval(uservalue)
        if account in accounts:
            sender.reply("更新账号成功，可对我说'酷我提现'对账号进行管理！")
        else:
            accounts.append(account)
            middleware.bucketSet(bucket='dd_KuwoTX_bind', key=userid, value=f'{accounts}')
            sender.reply("=====登录成功=====\n✅ 账号添加成功\n🎮 发送[酷我提现]管理账号\n===================")

def migrate_account_counts_to_user():
    """将账号级别的次数迁移到用户级别"""
    all_binds = middleware.bucketAll(bucket='dd_KuwoTX_bind')
    migration_results = []
    
    for user_id, uservalue in all_binds.items():
        try:
            accounts = eval(uservalue)
            total_account_count = 0
            migrated_accounts = []
            
            # 计算所有账号的总次数
            for account in accounts:
                account_count = middleware.bucketGet(bucket='dd_KuwoTX_UserCount', key=account) or '0'
                if int(account_count) > 0:
                    total_account_count += int(account_count)
                    migrated_accounts.append((account, account_count))
                    # 清除账号级别的次数
                    middleware.bucketDel(bucket='dd_KuwoTX_UserCount', key=account)
            
            if total_account_count > 0:
                # 更新用户级别的次数
                user_count = middleware.bucketGet(bucket='dd_KuwoTX_UserCount', key=user_id) or '0'
                new_user_count = int(user_count) + total_account_count
                middleware.bucketSet(bucket='dd_KuwoTX_UserCount', key=user_id, value=str(new_user_count))
                
                migration_results.append(f"用户 {user_id}: 账号次数 {total_account_count} + 用户次数 {user_count} = 新次数 {new_user_count}")
                print(f"[迁移] 用户 {user_id}: 账号次数 {total_account_count} + 用户次数 {user_count} = 新次数 {new_user_count}")
            
        except Exception as e:
            print(f"[错误] 迁移用户 {user_id} 次数时出错: {str(e)}")
            continue
    
    return migration_results

def _sync_time_offset():
    """通过NTP同步时间偏移量，计算本地时间与服务器时间的差值"""
    global _time_offset

    ntp_servers = [
        'ntp.aliyun.com',
        'ntp1.aliyun.com',
        'ntp.tencent.com',
        'time1.cloud.tencent.com',
        'time.windows.com'
    ]

    # 优先使用NTP（精度最高，延迟<10ms）
    if 'ntplib' in dir():
        try:
            import ntplib as _ntplib
            client = _ntplib.NTPClient()
            for server in ntp_servers:
                try:
                    response = client.request(server, timeout=3)
                    _time_offset = response.offset  # 本地时间与NTP服务器的偏差（秒）
                    print(f"[时间] NTP同步成功 ({server})，偏移量: {_time_offset:.3f}秒")
                    return
                except Exception as e:
                    print(f"[警告] NTP服务器 {server} 失败: {str(e)}")
                    continue
        except ImportError:
            pass

    # NTP不可用时，尝试HTTP API计算偏移量
    time_apis = [
        ('http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp', 'taobao'),
        ('http://worldtimeapi.org/api/timezone/Asia/Shanghai', 'worldtime'),
    ]

    for api_url, api_type in time_apis:
        try:
            local_before = time.time()
            response = requests.get(api_url, timeout=3, verify=False)
            local_after = time.time()

            if response.status_code != 200:
                continue

            data = response.json()
            local_mid = (local_before + local_after) / 2  # 估算请求时的本地时间

            if api_type == 'taobao' and 'data' in data:
                server_time = int(data['data']['t']) / 1000
            elif api_type == 'worldtime' and 'unixtime' in data:
                server_time = float(data['unixtime'])
            else:
                continue

            _time_offset = server_time - local_mid
            print(f"[时间] HTTP API同步成功 ({api_type})，偏移量: {_time_offset:.3f}秒")
            return

        except Exception as e:
            print(f"[警告] 从API {api_url} 获取时间失败: {str(e)}")
            continue

    # 所有方法失败，假设偏移量为0
    _time_offset = 0
    print("[警告] 所有时间源都失败，使用本地时间（偏移量=0）")

def get_precise_time():
    """基于偏移量快速获取精确的当前时间（无网络请求）"""
    global _time_offset
    if _time_offset is None:
        _sync_time_offset()
    return datetime.fromtimestamp(time.time() + _time_offset)

def get_beijing_time():
    """获取北京时间（兼容原有调用）"""
    global _time_offset
    if _time_offset is None:
        _sync_time_offset()
    return get_precise_time()

def precision_wait(target_time):
    """高精度等待到目标时间：先sleep粗等，最后busy-wait精等"""
    now = get_precise_time()
    wait_seconds = (target_time - now).total_seconds()

    if wait_seconds <= 0:
        return

    # 阶段1：粗等待（>2秒部分用sleep，节省CPU）
    if wait_seconds > 2:
        coarse_wait = wait_seconds - 1.5
        print(f"[等待] 粗等待 {coarse_wait:.1f} 秒...")
        time.sleep(coarse_wait)

    # 阶段2：精等待（最后1.5秒用busy-wait，精度<1ms）
    print("[等待] 进入精确等待模式...")
    target_ts = target_time.timestamp()
    offset = _time_offset or 0
    while True:
        current_ts = time.time() + offset
        if current_ts >= target_ts:
            break
        remaining = target_ts - current_ts
        # 剩余>50ms时短暂sleep减少CPU占用
        if remaining > 0.05:
            time.sleep(0.001)

    actual_time = get_precise_time()
    diff_ms = (actual_time - target_time).total_seconds() * 1000
    print(f"[等待] 等待完成，实际偏差: {diff_ms:.1f}ms")

def Administration():
    """管理账号"""
    global uservalue, withdraw_delay  # 添加withdraw_delay到global声明中
    
    base_message = (
        "=====酷我提现=====\n"
        "1️⃣ 提交账号\n"
        "2️⃣ 授权账号\n" 
        "3️⃣ 删除账号\n"
        "4️⃣ 账号提现\n"
    )
    
    if sender.isAdmin():
        base_message += "5️⃣ 用户授权\n"
        
    base_message += "⚠️ 输入q退出操作\n==================="
    
    sender.reply(base_message)
    
    choice = sender.input(60000, 1, False)
    if choice.lower() == 'q':
        sender.reply('退出操作')
        return
        
    try:
        choice = int(choice)
        if choice == 1:
            # 提交账号
            bind()
            return
            
        elif choice == 2:
            # 授权账号
            if not uservalue:
                sender.reply("未绑定任何账号,请先提交账号")
                return
                
            accounts = eval(uservalue)
            # 获取用户的总提现次数
            user_withdraw_count = get_user_withdraw_count(userid)
            
            message = f"=====账号授权=====\n"
            message += f"🔢 当前可用次数: {user_withdraw_count}次\n"
            message += f"📱 绑定账号数: {len(accounts)}个\n"
            message += f"-------------------\n"
            
            # 显示账号列表
            count = 1
            for account in accounts:
                Token = middleware.bucketGet(bucket='dd_KuwoTX_account', key=account)
                login_info = middleware.bucketGet(bucket='dd_KuwoTX_login', key=account)
                
                try:
                    # 从登录信息中获取手机号
                    if login_info:
                        login_values = login_info.split('#')
                        phone = login_values[0]
                    else:
                        token_values = Token.split('#')
                        phone = token_values[0]
                        
                    phone_masked = phone[:3] + '*' * 4 + phone[7:]
                    
                    message += f"[{count}] 账号: {phone_masked}\n"
                    count += 1
                except:
                    continue
            
            message += "-------------------\n"
            message += "请输入充值次数(输入q退出):"
            sender.reply(message)
            
            count_input = sender.input(60000, 1, False)
            if count_input.lower() == 'q':
                sender.reply('退出操作')
                return
                
            try:
                count = int(count_input)
                if count <= 0:
                    sender.reply('充值次数必须大于0')
                    return
                    
                # 调用支付函数，为用户充值
                project = "酷我提现次数充值"
                if zf(project, count, userid):
                    return
                    
            except ValueError:
                sender.reply('输入的次数无效')
                return
            
        elif choice == 3:
            # 删除账号
            if not uservalue:
                sender.reply("未绑定任何账号")
                return
                
            accounts = eval(uservalue)
            message = "=====选择账号=====\n"
            count = 1
            
            for account in accounts:
                Token = middleware.bucketGet(bucket='dd_KuwoTX_account', key=account)
                login_info = middleware.bucketGet(bucket='dd_KuwoTX_login', key=account)
                
                try:
                    # 从登录信息中获取手机号
                    if login_info:
                        login_values = login_info.split('#')
                        phone = login_values[0]  # 获取登录手机号
                    else:
                        # 如果没有登录信息，则从Token中获取
                        token_values = Token.split('#')
                        phone = token_values[0]
                        
                    phone_masked = phone[:3] + '*' * 4 + phone[7:]
                    message += (
                        f"[{count}] 账号: {phone_masked}\n"
                        f"-------------------\n"
                    )
                    count += 1
                except:
                    continue
                    
            message += "⚠️ 输入q退出操作\n=================="
            sender.reply(message)
            
            acc_choice = sender.input(60000, 1, False)
            if acc_choice.lower() == 'q':
                sender.reply('退出操作')
                return
                
            try:
                acc_choice = int(acc_choice)
                if acc_choice < 1 or acc_choice >= count:
                    sender.reply('输入的账号序号无效')
                    return
                    
                # 选择账号后确认删除
                selected_account = accounts[acc_choice - 1]
                Token = middleware.bucketGet(bucket='dd_KuwoTX_account', key=selected_account)
                login_info = middleware.bucketGet(bucket='dd_KuwoTX_login', key=selected_account)
                
                try:
                    # 从登录信息中获取手机号
                    if login_info:
                        login_values = login_info.split('#')
                        phone = login_values[0]
                    else:
                        token_values = Token.split('#')
                        phone = token_values[0]
                        
                    phone_masked = phone[:3] + '*' * 4 + phone[7:]
                    
                    sender.reply(
                        f"=====删除确认=====\n"
                        f"📱 账号: {phone_masked}\n"
                        f"是否确认删除?\n"
                        f"[y]确认 | [n]取消\n"
                        f"==================="
                    )
                    
                    confirm = sender.input(60000, 1, False)
                    if confirm.lower() == 'y':
                        try:
                            # 删除账号相关数据
                            accounts.remove(selected_account)
                            if accounts:
                                middleware.bucketSet(bucket='dd_KuwoTX_bind', key=userid, value=f'{accounts}')
                            else:
                                middleware.bucketDel(bucket='dd_KuwoTX_bind', key=userid)
                                
                            middleware.bucketDel(bucket='dd_KuwoTX_account', key=selected_account)
                            middleware.bucketDel(bucket='dd_KuwoTX_login', key=selected_account)
                            
                            sender.reply('删除成功')
                        except Exception as e:
                            sender.reply(f'删除失败: {str(e)}')
                    elif confirm.lower() == 'n':
                        sender.reply('已取消删除')
                    else:
                        sender.reply('输入无效')
                    
                except Exception as e:
                    sender.reply(f'处理删除请求时出错: {str(e)}')
                    return
                
            except ValueError:
                sender.reply('输入无效')
                return
                
        elif choice == 4:
            # 提现功能
            if not uservalue:
                sender.reply("未绑定任何账号,请先提交账号")
                return
            
            # 获取用户的提现次数
            user_withdraw_count = get_user_withdraw_count(userid)
            
            # 检查是否有账号级别的次数，如果有则迁移
            account_total_count = 0
            accounts = eval(uservalue)
            for account in accounts:
                account_count = middleware.bucketGet(bucket='dd_KuwoTX_UserCount', key=account) or '0'
                account_total_count += int(account_count)
            
            # 如果有账号级别的次数，执行迁移
            if account_total_count > 0:
                migrate_results = migrate_account_counts_to_user()
                # 重新获取用户次数
                user_withdraw_count = get_user_withdraw_count(userid)
                sender.reply(f"检测到账号级别次数，已自动迁移到用户级别\n当前可用次数: {user_withdraw_count}次")
            
            if int(user_withdraw_count) <= 0:
                sender.reply("您当前没有可用的提现次数，请先充值")
                return
            
            message = f"=====账号提现=====\n"
            message += f"🔢 当前可用次数: {user_withdraw_count}次\n"
            message += f"-------------------\n"
            count = 1
            valid_accounts = []
            
            for account in accounts:
                Token = middleware.bucketGet(bucket='dd_KuwoTX_account', key=account)
                login_info = middleware.bucketGet(bucket='dd_KuwoTX_login', key=account)
                
                try:
                    if login_info:
                        login_values = login_info.split('#')
                        phone = login_values[0]
                    else:
                        token_values = Token.split('#')
                        phone = token_values[0]
                    
                    phone_masked = phone[:3] + '*' * 4 + phone[7:]
                    
                    message += (
                        f"[{count}] 账号: {phone_masked}\n"
                        f"-------------------\n"
                    )
                    valid_accounts.append({
                        'index': count - 1,
                        'account': account,
                        'phone_masked': phone_masked,
                        'login_info': login_info,
                        'token': Token
                    })
                    count += 1
                except:
                    continue
            
            if not valid_accounts:
                sender.reply("没有可用的已授权账号，请先授权后再使用提现功能")
                return
            
            # 修改选择账号的提示消息
            message += """0️⃣ 批量提现
⚠️ 输入q退出操作
=================="""
            sender.reply(message)
            
            acc_choice = sender.input(60000, 1, False)
            if acc_choice.lower() == 'q':
                sender.reply('退出操作')
                return

            selected_indices = []
            if acc_choice == '0':
                # 如果选择0，提示输入序号范围
                sender.reply(
                    "=====批量提现=====\n"
                    "请输入账号序号\n"
                    "格式1: 起始序号-结束序号 (例如: 1-3)\n"
                    "格式2: 单独序号,序号,序号 (例如: 1,3,5)\n"
                    "==================="
                )
                range_choice = sender.input(60000, 1, False)
                if not range_choice:
                    sender.reply('输入超时')
                    return
                    
                try:
                    # 处理两种格式的输入
                    if '-' in range_choice:
                        # 处理范围格式 (例如: 1-3)
                        start, end = map(int, range_choice.split('-'))
                        selected_indices = list(range(start-1, end))
                    elif ',' in range_choice:
                        # 处理单独序号格式 (例如: 1,3,5)
                        selected_indices = [int(idx.strip())-1 for idx in range_choice.split(',')]
                    else:
                        # 处理单个数字
                        selected_indices = [int(range_choice.strip())-1]
                except:
                    sender.reply('输入格式错误')
                    return
            else:
                try:
                    # 处理单个账号选择
                    selected_index = int(acc_choice) - 1
                    selected_indices = [selected_index]
                except:
                    sender.reply('输入格式错误，请输入有效的账号序号')
                    return

            # 验证选择的账号是否有效
            valid_indices = [acc['index'] for acc in valid_accounts]
            selected_indices = [i for i in selected_indices if i in valid_indices]
            if not selected_indices:
                sender.reply('未选择任何有效账号')
                return
            
            # 获取选中的账号信息
            selected_accounts = [acc for acc in valid_accounts if acc['index'] in selected_indices]
            
            # 显示选中的账号
            message = "=====已选择账号=====\n"
            for acc in selected_accounts:
                message += f"📱 账号: {acc['phone_masked']}\n"
            message += f"共选择了 {len(selected_accounts)} 个账号\n"
            message += "==================="
            sender.reply(message)
            
            # 询问是否等待整点提现
            sender.reply(
                "=====提现时间=====\n"
                "是否等待整点提现?\n"
                "[y]是 | [n]否\n"
                "==================="
            )
            wait_choice = sender.input(60000, 1, False)
            if not wait_choice:
                sender.reply('输入超时')
                return

            # 获取北京时间
            now = get_beijing_time()
            current_hour = now.hour
            current_minute = now.minute
            withdraw_hours = [0, 9, 13, 17, 20]
            wait_hours = [23, 8, 12, 16, 19]
            today_wait_hours = [8, 12, 16, 19, 23]

            # 存储所有账号的验证码信息
            accounts_info = []

            if wait_choice.lower() == 'y':
                # 检查是否在等待时间点（整点前5分钟开始等待）
                is_wait_time = False
                target_hour = None
                
                if current_hour == 23 and current_minute >= 55:
                    is_wait_time = True
                    target_hour = 0
                else:
                    for hour in wait_hours:
                        if current_hour == hour and current_minute >= 55:
                            is_wait_time = True
                            target_hour = withdraw_hours[(wait_hours.index(hour) + 1) % len(withdraw_hours)]
                            break

                if not is_wait_time:
                    next_wait_hour = None
                    for hour in today_wait_hours:
                        if (hour > current_hour) or (hour == current_hour and current_minute < 55):
                            next_wait_hour = hour
                            target_time = now.replace(
                                hour=next_wait_hour,
                                minute=55,
                                second=0,
                                microsecond=0
                            )
                            break
                    
                    if next_wait_hour is None:
                        target_time = (now + timedelta(days=1)).replace(
                            hour=today_wait_hours[0],
                            minute=55,
                            second=0,
                            microsecond=0
                        )
                    
                    sender.reply(
                        f"当前不在提现等待时间段\n"
                        f"当前北京时间: {now.strftime('%H:%M')}\n"
                        f"下次等待时间: {target_time.strftime('%H:%M')}\n"
                        f"请在该时间后再试"
                    )
                    return

                # 为每个选中的账号获取验证码并存储信息
                for acc in selected_accounts:
                    try:
                        # 获取代理
                        proxy = proxy_manager.get_proxy()
                        if not proxy:
                            sender.reply(f"获取代理失败，跳过账号 {acc['phone_masked']}\n原因: {proxy_manager.get_last_error()}")
                            continue

                        proxies = {
                            'http': f'http://{proxy}',
                            'https': f'http://{proxy}'
                        }

                        # 先从login_info获取手机号和密码，重新登录获取最新凭证
                        login_info = acc.get('login_info')
                        if not login_info:
                            sender.reply(f"账号 {acc['phone_masked']} 缺少登录信息，跳过")
                            continue

                        login_values = login_info.split('#')
                        phone = login_values[0]
                        password = login_values[1] if len(login_values) > 1 else ''

                        sender.reply(f"正在为账号 {acc['phone_masked']} 重新登录获取凭证...")

                        # 重新登录获取最新凭证
                        loginUid, loginSid, error = login_for_withdraw(phone, password)
                        if error:
                            sender.reply(f"账号 {acc['phone_masked']} 重新登录失败: {error}")
                            continue

                        # 重新加密手机号
                        phone_value = encrypt_phone(phone)
                        if not phone_value:
                            sender.reply(f"账号 {acc['phone_masked']} 手机号加密失败")
                            continue

                        # 更新存储的token
                        new_token = f"{loginUid}#{phone}#{loginSid}#{phone_value}"
                        middleware.bucketSet(bucket='dd_KuwoTX_account', key=acc['account'], value=new_token)

                        sender.reply(f"账号 {acc['phone_masked']} 重新登录成功")

                        params = {
                            "loginUid": loginUid,
                            "loginSid": loginSid,
                            "mobile": phone_value
                        }

                        # 发送验证码
                        url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/userBindPhone"
                        headers = {
                            "User-Agent": generate_kuwo_ua(phone),
                            "Accept": "application/json, text/plain, */*",
                            "Origin": "https://h5app.kuwo.cn",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "Referer": "https://h5app.kuwo.cn/apps/earning-sign/cash_out.html",
                            "Sec-Fetch-Dest": "empty",
                            "Accept-Language": "zh-CN,zh-Hans;q=0.9"
                        }

                        response = requests.get(url, params=params, headers=headers, verify=False)
                        if response.status_code != 200:
                            sender.reply(f"账号 {acc['phone_masked']} 发送验证码失败")
                            continue

                        result = response.json()
                        # 检查是否返回"用户未登录"错误
                        data_status = result.get('data', {}).get('status')
                        data_desc = result.get('data', {}).get('description', '')
                        if data_status == 0 and data_desc == '用户未登录':
                            sender.reply(f"账号 {acc['phone_masked']} 登录凭证已失效！\n请重新执行「1️⃣ 提交账号」绑定账号")
                            continue

                        if result.get('code') != 200:
                            error_msg = result.get('msg', '未知错误')
                            sender.reply(f"账号 {acc['phone_masked']} 发送验证码失败: {error_msg}")
                            continue

                        sender.reply(f"请输入账号 {acc['phone_masked']} 的验证码:")
                        sms_code = sender.input(60000, 1, False)
                        if not sms_code:
                            sender.reply(f"账号 {acc['phone_masked']} 验证码输入超时")
                            continue

                        # 存储账号信息
                        accounts_info.append({
                            'phone_masked': acc['phone_masked'],
                            'phone_raw': phone,
                            'loginUid': loginUid,
                            'loginSid': loginSid,
                            'phone_value': phone_value,
                            'sms_code': sms_code,
                            'proxy': proxy
                        })

                    except Exception as e:
                        sender.reply(f"处理账号 {acc['phone_masked']} 时出错: {str(e)}")
                        continue

                if not accounts_info:
                    sender.reply("没有成功准备好的账号，退出操作")
                    return

                # 计算目标提现时间
                if current_hour == 23:
                    target_time = (now + timedelta(days=1)).replace(
                        hour=0, minute=0, second=0, microsecond=0
                    )
                else:
                    target_time = now.replace(
                        hour=current_hour + 1, minute=0, second=0, microsecond=0
                    )

                # 应用提现延迟设置，整点后延迟发包（至少1秒）
                actual_delay = withdraw_delay if withdraw_delay > 0 else 1.0
                target_time = target_time + timedelta(seconds=actual_delay)
                wait_seconds = (target_time - now).total_seconds()
                wait_seconds = max(0, wait_seconds)

                sender.reply(
                    f"=====提现准备就绪=====\n"
                    f"📱 账号数: {len(accounts_info)}个\n"
                    f"⏰ 目标时间: {target_time.strftime('%H:%M:%S')}\n"
                    f"🚀 延后发包: {actual_delay:g}秒\n"
                    f"⏳ 等待: {int(wait_seconds)}秒\n"
                    f"======================"
                )

                # === 等待期间执行预热操作 ===
                # 1. 重新同步时间（确保偏移量精确）
                print("[优化] 重新同步NTP时间...")
                _sync_time_offset()

                # 2. 预获取代理到代理池
                proxy_manager.prefetch_proxies(len(accounts_info))

                # 3. 为每个账号创建预热的Session（提前建立TCP+TLS连接）
                print("[优化] 预热HTTP连接...")
                for acc_info in accounts_info:
                    try:
                        session = proxy_manager.create_warmed_session(acc_info['proxy'], acc_info.get('phone_raw', ''))
                        acc_info['session'] = session
                    except Exception as e:
                        print(f"[警告] Session预热失败: {str(e)}")
                        acc_info['session'] = None

                # 4. 预构建所有提现请求参数
                withdraw_url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/getWithdraw"
                for acc_info in accounts_info:
                    acc_info['withdraw_params'] = {
                        "encry": "",
                        "type": "",
                        "quotaId": "30002",
                        "loginUid": acc_info['loginUid'],
                        "loginSid": acc_info['loginSid'],
                        "appuid": generate_appuid(),
                        "source": "kwplayer_ar_12.1.4.0_40.apk",
                        "version": "1",
                        "phone": acc_info['phone_value'],
                        "code": acc_info['sms_code']
                    }

                sender.reply("预热完成，等待整点...")

                # === 高精度等待 ===
                try:
                    precision_wait(target_time)
                except Exception as e:
                    print(f"[错误] 等待过程出错: {str(e)}")
                    sender.reply("等待过程出现问题，将直接执行提现操作")

                # === 整点到达，立即并发提现 ===
                fire_time = get_precise_time()
                sender.reply(f"开始批量提现... 发包时间: {fire_time.strftime('%H:%M:%S.%f')[:-3]}")

                success_count = 0
                fail_count = 0

                def process_withdraw(acc_info):
                    """单次提现处理（只请求一次，避免触发频繁限制）"""
                    session = acc_info.get('session')

                    try:
                        if session:
                            response = session.get(
                                withdraw_url,
                                params=acc_info['withdraw_params'],
                                timeout=8
                            )
                        else:
                            proxies = {
                                'http': f'http://{acc_info["proxy"]}',
                                'https': f'http://{acc_info["proxy"]}'
                            }
                            response = requests.get(
                                withdraw_url,
                                params=acc_info['withdraw_params'],
                                headers={
                                    "User-Agent": generate_kuwo_ua(acc_info.get('phone_raw', '')),
                                    "Accept": "application/json, text/plain, */*",
                                    "Origin": "https://h5app.kuwo.cn",
                                    "Referer": "https://h5app.kuwo.cn/apps/earning-sign/cash_out.html",
                                },
                                proxies=proxies,
                                verify=False,
                                timeout=8
                            )

                        return response, acc_info

                    except Exception as e:
                        print(f"[提现] 账号 {acc_info['phone_masked']} 请求失败: {str(e)}")
                        return None, acc_info

                # 使用线程池并发处理（提升到10线程）
                with ThreadPoolExecutor(max_workers=min(len(accounts_info), 10)) as executor:
                    futures = [executor.submit(process_withdraw, acc_info) for acc_info in accounts_info]

                    for future in as_completed(futures):
                        response, acc_info = future.result()
                        if not response:
                            sender.reply(f"账号 {acc_info['phone_masked']} 提现请求失败")
                            fail_count += 1
                            continue

                        try:
                            result = response.json()
                            text = result.get('data', {}).get('text', '')
                            if "提现成功" in text or "提现申请发起成功" in text:
                                new_count = decrease_user_withdraw_count(userid)
                                sender.reply(f"✅ 账号 {acc_info['phone_masked']} 提现成功: {text}\n剩余提现次数: {new_count}次")
                                success_count += 1
                            else:
                                sender.reply(f"❌ 账号 {acc_info['phone_masked']} 提现失败: {text}")
                                fail_count += 1
                        except Exception as e:
                            sender.reply(f"账号 {acc_info['phone_masked']} 处理响应出错: {str(e)}")
                            fail_count += 1

                # 清理Session
                for acc_info in accounts_info:
                    session = acc_info.get('session')
                    if session:
                        try:
                            session.close()
                        except:
                            pass

                sender.reply(f"批量提现完成\n✅ 成功: {success_count}个\n❌ 失败: {fail_count}个")

            elif wait_choice.lower() == 'n':
                # 直接执行提现操作，不需要发送批量提现消息
                for acc in selected_accounts:
                    try:
                        # 获取代理
                        proxy = proxy_manager.get_proxy()
                        if not proxy:
                            sender.reply(f"获取代理失败，跳过账号 {acc['phone_masked']}\n原因: {proxy_manager.get_last_error()}")
                            continue

                        proxies = {
                            'http': f'http://{proxy}',
                            'https': f'http://{proxy}'
                        }

                        # 先从login_info获取手机号和密码，重新登录获取最新凭证
                        login_info = acc.get('login_info')
                        if not login_info:
                            sender.reply(f"账号 {acc['phone_masked']} 缺少登录信息，跳过")
                            continue

                        login_values = login_info.split('#')
                        phone = login_values[0]
                        password = login_values[1] if len(login_values) > 1 else ''

                        sender.reply(f"正在为账号 {acc['phone_masked']} 重新登录获取凭证...")

                        # 重新登录获取最新凭证
                        loginUid, loginSid, error = login_for_withdraw(phone, password)
                        if error:
                            sender.reply(f"账号 {acc['phone_masked']} 重新登录失败: {error}")
                            continue

                        # 重新加密手机号
                        phone_value = encrypt_phone(phone)
                        if not phone_value:
                            sender.reply(f"账号 {acc['phone_masked']} 手机号加密失败")
                            continue

                        # 更新存储的token
                        new_token = f"{loginUid}#{phone}#{loginSid}#{phone_value}"
                        middleware.bucketSet(bucket='dd_KuwoTX_account', key=acc['account'], value=new_token)

                        sender.reply(f"账号 {acc['phone_masked']} 重新登录成功")

                        params = {
                            "loginUid": loginUid,
                            "loginSid": loginSid,
                            "mobile": phone_value
                        }

                        # 发送验证码
                        url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/userBindPhone"
                        headers = {
                            "User-Agent": generate_kuwo_ua(phone),
                            "Accept": "application/json, text/plain, */*",
                            "Origin": "https://h5app.kuwo.cn",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-site",
                            "Referer": "https://h5app.kuwo.cn/apps/earning-sign/cash_out.html",
                            "Sec-Fetch-Dest": "empty",
                            "Accept-Language": "zh-CN,zh-Hans;q=0.9"
                        }

                        response = requests.get(url, params=params, headers=headers, verify=False)
                        if response.status_code != 200:
                            sender.reply(f"账号 {acc['phone_masked']} 发送验证码失败")
                            continue

                        result = response.json()
                        # 检查是否返回"用户未登录"错误
                        data_status = result.get('data', {}).get('status')
                        data_desc = result.get('data', {}).get('description', '')
                        if data_status == 0 and data_desc == '用户未登录':
                            sender.reply(f"账号 {acc['phone_masked']} 登录凭证已失效！\n请重新执行「1️⃣ 提交账号」绑定账号")
                            continue

                        if result.get('code') != 200:
                            error_msg = result.get('msg', '未知错误')
                            sender.reply(f"账号 {acc['phone_masked']} 发送验证码失败: {error_msg}")
                            continue

                        sender.reply(f"请输入账号 {acc['phone_masked']} 的验证码:")
                        sms_code = sender.input(60000, 1, False)
                        if not sms_code:
                            sender.reply(f"账号 {acc['phone_masked']} 验证码输入超时")
                            continue

                        # 执行提现
                        withdraw_url = "https://integralapi.kuwo.cn/api/v1/online/sign/v1/getWithdraw"
                        withdraw_params = {
                            "encry": "",
                            "type": "",
                            "quotaId": "30002",
                            "loginUid": loginUid,
                            "loginSid": loginSid,
                            "appuid": generate_appuid(),
                            "source": "kwplayer_ar_12.1.4.0_40.apk",
                            "version": "1",
                            "phone": phone_value,
                            "code": sms_code
                        }

                        response = requests.get(
                            withdraw_url,
                            params=withdraw_params,
                            headers=headers,
                            proxies=proxies,
                            verify=False,
                            timeout=10
                        )

                        if response.status_code != 200:
                            sender.reply(f"账号 {acc['phone_masked']} 提现请求失败")
                            continue

                        result = response.json()
                        if result.get('data', {}).get('text'):
                            error_msg = result['data']['text']
                            if "提现成功" in error_msg or "提现申请发起成功" in error_msg:
                                # 减少提现次数
                                new_count = decrease_user_withdraw_count(userid)
                                sender.reply(f"✅ 账号 {acc['phone_masked']} 提现成功: {error_msg}\n剩余提现次数: {new_count}次")
                            else:
                                sender.reply(f"❌ 账号 {acc['phone_masked']} 提现失败: {error_msg}")
                        else:
                            sender.reply(f"账号 {acc['phone_masked']} 提现失败: 接口返回异常")

                    except Exception as e:
                        sender.reply(f"处理账号 {acc['phone_masked']} 时出错: {str(e)}")
                        continue
            else:
                sender.reply("输入无效,已取消操作")
            return

        elif choice == 5 and sender.isAdmin():
            # 用户授权功能
            sender.reply(
                "=====用户授权=====\n"
                "1️⃣ 单用户授权\n"
                "2️⃣ 全部用户授权\n"
                "⚠️ 输入q退出操作\n"
                "==================="
            )
            
            auth_choice = sender.input(60000, 1, False)
            if auth_choice.lower() == 'q':
                sender.reply('退出操作')
                return
                
            try:
                auth_choice = int(auth_choice)
                if auth_choice == 1:
                    # 单用户授权
                    sender.reply("请输入用户ID:")
                    target_userid = sender.input(60000, 1, False)
                    if not target_userid:
                        sender.reply('输入超时')
                        return
                        
                    target_uservalue = middleware.bucketGet('dd_KuwoTX_bind', target_userid)
                    if not target_uservalue:
                        sender.reply('该用户未绑定任何账号')
                        return
                        
                    # 获取用户当前次数
                    current_count = middleware.bucketGet('dd_KuwoTX_UserCount', target_userid) or '0'
                    
                    # 显示用户信息
                    accounts = eval(target_uservalue)
                    message = "=====用户信息=====\n"
                    message += f"👤 用户ID: {target_userid}\n"
                    message += f"🔢 当前次数: {current_count}次\n"
                    message += f"📱 绑定账号数: {len(accounts)}个\n"
                    message += "-------------------\n"
                    
                    # 显示账号列表
                    for i, account in enumerate(accounts):
                        login_info = middleware.bucketGet('dd_KuwoTX_login', account)
                        
                        try:
                            if login_info:
                                login_values = login_info.split('#')
                                phone = login_values[0]
                            else:
                                Token = middleware.bucketGet(bucket='dd_KuwoTX_account', key=account)
                                if not Token:
                                    continue
                                token_values = Token.split('#')
                                phone = token_values[0]
                                
                            phone_masked = phone[:3] + '*' * 4 + phone[7:]
                            message += f"[{i+1}] 账号: {phone_masked}\n"
                        except:
                            continue
                    
                    message += "-------------------\n"
                    message += "请输入充值次数:"
                    sender.reply(message)
                    
                    count_input = sender.input(60000, 1, False)
                    if not count_input:
                        sender.reply('输入超时')
                        return
                        
                    try:
                        count = int(count_input)
                        if count <= 0:
                            sender.reply('充值次数必须大于0')
                            return
                            
                        # 直接为用户ID增加次数
                        new_count = empower(user_id=target_userid, count=count)
                        
                        sender.reply(f"""=====充值成功=====
👤 用户ID: {target_userid}
🔢 充值次数: {count}次
📊 当前可用次数: {new_count}次
===================""")
                        
                    except ValueError:
                        sender.reply('充值次数必须为数字')
                        return
                    
                elif auth_choice == 2:
                    # 全部用户授权
                    sender.reply("请输入充值次数:")
                    count_input = sender.input(60000, 1, False)
                    if not count_input:
                        sender.reply('输入超时')
                        return
                        
                    try:
                        count = int(count_input)
                        if count <= 0:
                            sender.reply('充值次数必须大于0')
                            return
                            
                        # 获取所有用户绑定信息
                        all_binds = middleware.bucketAll(bucket='dd_KuwoTX_bind')
                        if not all_binds:
                            sender.reply('没有找到任何用户绑定信息')
                            return
                            
                        success_count = 0
                        failed_count = 0
                        result_message = "=====全部授权结果=====\n"
                        
                        for user_id, uservalue in all_binds.items():
                            try:
                                # 直接为用户ID增加次数
                                new_count = empower(user_id=user_id, count=count)
                                success_count += 1
                                result_message += f"✅ 用户 {user_id}: 充值成功，当前次数 {new_count}\n"
                                    
                            except Exception as e:
                                failed_count += 1
                                result_message += f"❌ 用户 {user_id} 处理失败: {str(e)}\n"
                                
                        result_message += f"""-------------------
📊 统计信息:
👤 用户总数: {len(all_binds)}
✅ 成功充值: {success_count}
❌ 充值失败: {failed_count}
🔢 充值次数: {count}次
===================""" 
                        
                        sender.reply(result_message)
                        
                    except ValueError:
                        sender.reply('充值次数必须为数字')
                        return
                        
                else:
                    sender.reply('输入无效')
                    
            except ValueError:
                sender.reply('输入无效')
            
        else:
            sender.reply('输入无效')
            
    except ValueError:
        sender.reply('输入无效')

def zf(project, count, user_id):
    """支付处理"""
    if KuwoTXmoney == Decimal(0):
        return

    money = Decimal(count) * Decimal(KuwoTXmoney)

    # 获取支付配置
    zsm, use_ma_pay_local, ma_pay_config = get_payment_config()
    if not zsm and not use_ma_pay_local:
        sender.reply('未配置收款方式，请联系管理员')
        exit(0)

    # 积分信息
    user_points = middleware.bucketGet('dd_sign_points', userid) or '0'
    jfsl = middleware.bucketGet('dd_KuwoTX_PluginsData', 'KuwoTXcoin') or '200'
    total_points = int(jfsl) * count

    # 动态构建支付菜单
    pay_menu = "=====选择支付方式====="
    option_num = 1
    options_map = {}

    if zsm and not use_ma_pay_local:
        pay_menu += f"\n{option_num}️⃣ 微信支付\n   💰 {money}元/{count}次"
        options_map[str(option_num)] = 'wechat'
        option_num += 1

    if use_ma_pay_local:
        pay_menu += f"\n{option_num}️⃣ 码支付\n   💰 {money}元/{count}次"
        options_map[str(option_num)] = 'ma'
        option_num += 1

    if total_points > 0:
        pay_menu += f"\n{option_num}️⃣ 积分支付\n   🎯 {total_points}积分/{count}次\n   💫 当前积分: {user_points}"
        options_map[str(option_num)] = 'points'

    pay_menu += "\n-------------------\n回复数字选择方式\n回复'q'退出操作\n==================="

    sender.reply(pay_menu)
    choice = sender.input(60000, 1, False)

    if not choice:
        sender.reply('输入超时')
        return False
    if choice.lower() == 'q':
        sender.reply('退出支付')
        return False

    selected_pay = options_map.get(choice)

    if selected_pay == 'wechat' and zsm:
        # 检查是否有人正在支付
        zfzt = sender.atWaitPay()
        if zfzt:
            sender.reply('当前有人正在支付,请稍后再试！')
            exit(0)

        sender.reply(
            "=====订单信息=====\n"
            f"🎈名称:{project}\n"
            f"🎉数量:{count}次\n"
            f"💰应付:{money}元\n"
            "⚠️ 输入q退出支付\n"
            "==================="
        )
        sender.replyImage(zsm)

        ddzf = sender.waitPay("q", 100 * 1000)
        if str(ddzf) == 'q':
            sender.reply('退出支付')
            exit(0)

        try:
            if isinstance(ddzf, str):
                try:
                    ddzf = json.loads(ddzf)
                except:
                    if "二维码赞赏到账" in ddzf:
                        try:
                            amount = ddzf.split("收款金额￥")[1].split("\n")[0]
                            pay_t = ddzf.split("到账时间")[1].split("\n")[0]
                            ddzf = {"Money": float(amount), "Time": pay_t.strip()}
                        except:
                            sender.reply("解析收款信息失败")
                            exit(0)

            try:
                Money = float(ddzf.get('Money') or ddzf.get('money', 0))
                pay_time = ddzf.get('Time') or ddzf.get('time', '').replace('T', ' ').split('.')[0]
                if not pay_time:
                    pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                sender.reply("支付金额格式错误")
                exit(0)

            if float(Money) >= float(money):
                new_count = empower(user_id=user_id, count=count)
                sender.reply(
                    f"=====支付成功=====\n"
                    f"🎈 商品: {project}\n"
                    f"🎉 次数: {count}次\n"
                    f"💰 支付: {Money}元\n"
                    f"⏰ 时间: {pay_time}\n"
                    f"🔢 当前可提现次数: {new_count}次\n"
                    f"==================="
                )
                return True
            else:
                sender.reply(f'支付金额错误\n应付:{money}元\n实付:{Money}元\n请联系管理员处理退款！')
                exit(0)
        except Exception as e:
            sender.reply(f"处理支付结果时出错: {str(e)}")
            exit(0)

    elif selected_pay == 'ma' and use_ma_pay_local:
        def on_ma_success():
            new_count = empower(user_id=user_id, count=count)
            sender.reply(
                f"=====支付成功=====\n"
                f"🎈 商品: {project}\n"
                f"🎉 次数: {count}次\n"
                f"💰 金额: {money}元\n"
                f"🔢 当前可提现次数: {new_count}次\n"
                f"==================="
            )
        return handle_ma_payment(money, project, ma_pay_config, on_ma_success)

    elif selected_pay == 'points' and total_points > 0:
        current_points = int(user_points)
        if current_points < total_points:
            sender.reply(
                "=====积分不足=====\n"
                f"💰 当前积分: {current_points}\n"
                f"💵 所需积分: {total_points}\n"
                "==================="
            )
            return False

        sender.reply(
            "=====积分支付=====\n"
            f"💰 当前积分: {user_points}\n"
            f"💵 所需积分: {total_points}\n"
            f"💡 购买次数: {count}次\n"
            "是否确认支付?\n"
            "[y]确认 | [n]取消"
        )
        if yesornos():
            new_balance = int(user_points) - total_points
            middleware.bucketSet('dd_sign_points', userid, str(new_balance))
            new_count = empower(user_id=user_id, count=count)
            sender.reply(
                f"=====支付成功=====\n"
                f"🎈 商品: {project}\n"
                f"🎉 次数: {count}次\n"
                f"💰 支付: {total_points}积分\n"
                f"💎 剩余: {new_balance}积分\n"
                f"🔢 当前可提现次数: {new_count}次\n"
                f"==================="
            )
            exit(0)
        return False
    else:
        sender.reply("输入无效")
        return False

def empower(user_id, count):
    """更新用户的提现次数"""
    current_count = middleware.bucketGet(bucket='dd_KuwoTX_UserCount', key=user_id) or '0'
    try:
        new_count = int(current_count) + count
        middleware.bucketSet(bucket='dd_KuwoTX_UserCount', key=user_id, value=str(new_count))
        return new_count
    except:
        middleware.bucketSet(bucket='dd_KuwoTX_UserCount', key=user_id, value=str(count))
        return count

def yesornos():
    """确认选择"""
    yesorno = sender.input(60000, 1, False)
    if yesorno.lower() in ['y', '是']:
        return True
    elif yesorno.lower() in ['n', '否']:
        return False
    elif not yesorno:
        sender.reply('输入超时！')
        exit(0)
    elif yesorno.lower() in ['q', '退出']:
        sender.reply('退出！')
        exit(0)
    else:
        sender.reply('输入错误！')
        exit(0)

def check_authorization():
    """每天检查授权状态并处理过期账号"""
    total_zero_count = 0  # 记录总共无提现次数的用户数
    
    # 获取所有用户的绑定信息
    all_binds = middleware.bucketAll(bucket='dd_KuwoTX_bind')
    if not all_binds:
        return
        
    for userid, uservalue in all_binds.items():
        try:
            # 检查用户的提现次数
            user_withdraw_count = get_user_withdraw_count(userid)
            
            if int(user_withdraw_count) <= 0:
                total_zero_count += 1
                
                # 获取用户的账号信息用于通知
                accounts = eval(uservalue)
                account_info = []
                
                for account in accounts:
                    login_info = middleware.bucketGet(bucket='dd_KuwoTX_login', key=account)
                    
                    if login_info:
                        login_values = login_info.split('#')
                        phone = login_values[0]
                        phone_masked = phone[:3] + '*' * 4 + phone[7:]
                        account_info.append(phone_masked)
                    else:
                        Token = middleware.bucketGet(bucket='dd_KuwoTX_account', key=account)
                        if not Token:
                            continue
                        token_values = Token.split('#')
                        phone = token_values[0]
                        phone_masked = phone[:3] + '*' * 4 + phone[7:]
                        account_info.append(phone_masked)
                
                # 发送通知给用户
                message = "=====酷我提现次数不足通知=====\n"
                message += f"🔢 当前可用次数: {user_withdraw_count}次\n"
                message += f"📱 绑定账号数: {len(account_info)}个\n"
                if account_info:
                    message += "-------------------\n"
                    message += "绑定的账号:\n"
                    for i, phone in enumerate(account_info):
                        message += f"[{i+1}] {phone}\n"
                message += "-------------------\n"
                message += "请及时充值以继续使用提现功能\n"
                message += "==================="
                
                try:
                    notifier = middleware.Sender(userid)
                    notifier.reply(message)
                except:
                    print(f"[通知] 向用户 {userid} 发送通知失败")
                
        except Exception as e:
            print(f"[错误] 处理用户 {userid} 时出错: {str(e)}")
            continue
    
    # 向管理员发送总结报告
    try:
        print(f"[通知] 提现次数检测完毕，共发现 {total_zero_count} 个提现次数不足用户")
        if sender.isAdmin():
            sender.reply(f"酷我提现次数检测完毕，共发现 {total_zero_count} 个提现次数不足用户")
    except:
        print("[错误] 发送管理员通知失败")

def get_user_withdraw_count(user_id):
    """获取用户的提现次数"""
    # 直接从用户ID获取次数
    count = middleware.bucketGet(bucket='dd_KuwoTX_UserCount', key=user_id) or '0'
    return count

def decrease_user_withdraw_count(user_id):
    """减少用户的提现次数"""
    current_count = middleware.bucketGet(bucket='dd_KuwoTX_UserCount', key=user_id) or '0'
    try:
        new_count = max(0, int(current_count) - 1)
        middleware.bucketSet(bucket='dd_KuwoTX_UserCount', key=user_id, value=str(new_count))
        return new_count
    except:
        return 0

def main():
    """主函数"""
    global today_date, today_time, KuwoTXmoney, KuwoTXcoin, proxy_manager, withdraw_delay
    
    # 使用北京时间
    today_date = get_beijing_time().date()
    today_time = str(today_date)
    KuwoTXmoney, KuwoTXcoin, proxy_api, withdraw_delay = PluginsData()
    proxy_manager = ProxyManager(proxy_api)
    
    message = sender.getMessage()
    
    if message == "酷我提现授权检测":
        check_authorization()
        return
    
    if message == "酷我提现次数迁移":
        if sender.isAdmin():
            results = migrate_account_counts_to_user()
            if results:
                sender.reply("=====次数迁移结果=====\n" + "\n".join(results) + "\n===================")
            else:
                sender.reply("没有需要迁移的次数数据")
        else:
            sender.reply("只有管理员可以执行此操作")
        return
        
    Administration()

# 确保主函数被调用
main()
