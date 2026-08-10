# [rule: ^(电信|dx)(登录|登陆)$|^登(录|陆)(电信|dx)$|^(电信|dx)(查询|管理)$|^(查询|管理)(电信|dx)$|^电信清理$|^电信授权$|^电信教程$|^电信同步$]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 56 8,15 * * *]
# [public: true]
# [title: 电信]
# [icon: https://i.pinimg.com/564x/39/f2/20/39f2204f052bb3eeb89a7b6a93276cc0.jpg]
# [open_source: false]
# [class: 工具类]
# [version: 2.4]
# [price: 15.88]
# [admin: false]
# [author: sky2022]
# [service: 2661320550]
# [description: 介绍：电信金豆查询管理插件，支持账号管理，查询签到，金豆余额查询，本月话费抢购记录查询<br>登录格式：手机号#密码<br>指令：电信登录、电信管理、电信查询、电信清理、电信授权、电信教程<br>定时任务：每天8点和15点自动检测授权过期并推送通知<br>V2.3:新增定时检测推送，每天8点/15点自动检测授权到期状态并通知用户<br>V2.0:此版本更新适配了呆呆面板<br>V2.1:统一面板配置为面板类型+对接面板配置，并新增呆呆面板分组配置<br>V2.4:新增电信517活动查询]

# [param: {"required":true,"key":"dd_dx.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_dx.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_dx.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_dx.panel_group","bool":false,"placeholder":"例:电信","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_dx.dx_osname","bool":false,"placeholder":"必填项,例:dxToken","name":"面板变量名","desc":"提交到面板中的电信变量名"}]
# [param: {"required":true,"key":"dd_dx.dxVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_dx.dxcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"dd_dx.use_ma_pay","bool":true,"placeholder":"false","name":"启用码支付","desc":"开启后默认使用码支付+积分支付，并隐藏微信支付"}]

import re, os, json, time, datetime, requests, base64, random, binascii, ssl, urllib3, certifi, hashlib, uuid
from typing import Optional, Dict
from Crypto.Cipher import DES3, AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Util.Padding import pad, unpad
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from datetime import datetime, timedelta
import middleware, urllib.parse
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 全局变量初始化
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_dx_user', key=userid)

# 配置常量
DES_KEY = b'1234567`90koiuyhgtfrdews'
DES_IV = 8 * b'\0'
PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+ugG5A8cZ3FqUKDwM57GM4io6JGcStivT8UdGt67PEOihLZTw3P7371+N47PrmsCpnTRzbTgcupKtUv8ImZalYk65dU8rjC/ridwhw9ffW2LBwvkEnDkkKKRi2liWIItDftJVBiWOh17o6gfbPoNrWORcAdcbpk2L+udld5kZNwIDAQAB
-----END PUBLIC KEY-----'''
PUBLIC_KEY_B64 = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDBkLT15ThVgz6/NOl6s8GNPofdWzWbCkWnkaAm7O2LjkM1H7dMvzkiqdxU02jamGRHLX/ZNMCXHnPcW/sDhiFCBN18qFvy8g6VYb9QtroI09e176s+ZCtiv7hbin2cCTj99iUpnEloZm19lwHyo69u5UMiPMpq0/XKBO8lYhN/gwIDAQAB
-----END PUBLIC KEY-----'''

# 消息模板
MSG_TEMPLATES = {
    'config_error': "=====配置错误=====\n❌ {error}\n==================",
    'login_success': "=====电信账号绑定=====\n📱 绑定账号: {phone}\n🔐 授权状态: {status}\n⏰ 下一步: {next_step}\n==================",
    'auth_expired': "=====授权过期=====\n📱 账号: {phone}\n❌ 授权已过期\n💡 请及时续费\n==================",
    'query_result': "=====查询结果=====\n📱 账号: {phone}\n🔐 授权: {auth}\n🪙 金豆: {coin}\n📅 签到: {days}天\n🎯 今日: {today}\n==================",
    'operation_timeout': "⏰ 操作超时,已退出",
    'invalid_input': "❌ 输入无效",
    'no_accounts': "=====未绑定账号=====\n❌ 未找到任何账号信息\n💡 发送 {cmd} 绑定\n=================="
}

def normalize_panel_type(panel_type_value, legacy_use_daidai_value='false'):
    """统一解析面板类型，兼容新旧配置。"""
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    if value:
        return ''

    legacy_value = str(legacy_use_daidai_value or '').strip().lower()
    if legacy_value == 'true':
        return 'daidai'
    return 'qinglong'

def get_config():
    """获取配置信息"""
    panel_type = normalize_panel_type(
        middleware.bucketGet('dd_dx', 'panel_type') or '',
        middleware.bucketGet('dd_dx', 'use_daidai') or 'false'
    )
    if not panel_type:
        sender.reply(format_msg('config_error', error='对接面板类型填写无效\n请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai'))
        exit(0)

    panel_config = (middleware.bucketGet('dd_dx', 'panel_config') or '').strip()
    legacy_ql_config = middleware.bucketGet('dd_dx', 'dx_qlname') or ''
    legacy_dd_config = middleware.bucketGet('dd_dx', 'dd_dx_ddname') or ''

    return {
        'osname': middleware.bucketGet('dd_dx', 'dx_osname') or 'dd_dx_token',
        'qlname': panel_config or legacy_ql_config if panel_type == 'qinglong' else legacy_ql_config,
        'price': Decimal(middleware.bucketGet('dd_dx', 'dxVipmoney') or '1'),
        'coin': int(middleware.bucketGet('dd_dx', 'dxcoin') or '0'),
        'zsm': middleware.bucketGet('dd_dx', 'zsm') or '',
        'use_ma_pay': (middleware.bucketGet('dd_dx', 'use_ma_pay') or 'false').lower() == 'true',
        'use_daidai': panel_type == 'daidai',
        'dd_dx_ddname': panel_config or legacy_dd_config if panel_type == 'daidai' else legacy_dd_config,
        'panel_group': (middleware.bucketGet('dd_dx', 'panel_group') or '').strip()
    }

def format_msg(template, **kwargs):
    """格式化消息"""
    return MSG_TEMPLATES.get(template, template).format(**kwargs)

def mask_phone(phone):
    """手机号脱敏"""
    return phone[:3] + "****" + phone[7:]

def generate_qrcode(url):
    """将支付链接转为二维码图片URL"""
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception as e:
        print(f"生成二维码失败: {str(e)}")
        return None

def send_qrcode_image(pay_sender, qrcode_url, pay_type):
    """发送二维码图片给用户扫码支付"""
    pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
    pay_type_name = pay_type_names.get(pay_type, pay_type)
    try:
        pay_sender.replyImage(qrcode_url)
        if pay_type == 'qqpay':
            pay_sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\nQQ支付打开图片若是黑屏，长按屏幕进行\"识别二维码\"即可！\n支付过程中输入'q'可取消支付")
        else:
            pay_sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付")
    except:
        if pay_type == 'qqpay':
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！\n[CQ:image,file={qrcode_url}]'
        else:
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n[CQ:image,file={qrcode_url}]'
        pay_sender.reply(pay_msg)

def check_auth_status(account):
    """检查授权状态"""
    today = str(datetime.now().date())
    auth_time = middleware.bucketGet('dd_dx_auth', account) or ''
    
    if not auth_time:
        return "⚠️ 未授权", "无"
    elif auth_time <= today:
        return "❌ 已过期", auth_time
    else:
        return "✅ 已授权", auth_time

def parse_accounts(uservalue):
    """解析账号列表"""
    if not uservalue:
        return []
    try:
        cleaned = uservalue.strip('[]').strip()
        if cleaned:
            accounts = [acc.strip().strip("'\"") for acc in cleaned.split(',')]
            return [acc for acc in accounts if acc]
    except:
        pass
    return []

def validate_input(value, max_val, input_type="数字"):
    """验证输入"""
    try:
        value = int(value)
        if value > max_val or value <= 0:
            sender.reply(f"❌ 请输入 1-{max_val} 之间的{input_type}")
            exit(0)
        return value
    except ValueError:
        sender.reply(f"❌ 请输入有效的{input_type}")
        exit(0)

def confirm_operation():
    """确认操作"""
    response = sender.input(120000, 1, False)
    if response in ['Y', 'y', '是']:
        return True
    elif response in ['n', 'N', '否']:
        return False
    elif not response:
        sender.reply(MSG_TEMPLATES['operation_timeout'])
        exit(0)
    else:
        sender.reply(MSG_TEMPLATES['invalid_input'])
        exit(0)

# 加密解密工具函数
def encrypt_para(plaintext):
    """RSA加密参数"""
    if not isinstance(plaintext, str):
        plaintext = json.dumps(plaintext)
    public_key = RSA.import_key(PUBLIC_KEY)
    cipher = PKCS1_v1_5.new(public_key)
    key_size = public_key.size_in_bytes()
    max_chunk_size = key_size - 11
    plaintext_bytes = plaintext.encode()
    ciphertext = b''
    for i in range(0, len(plaintext_bytes), max_chunk_size):
        chunk = plaintext_bytes[i:i + max_chunk_size]
        encrypted_chunk = cipher.encrypt(chunk)
        ciphertext += encrypted_chunk
    return binascii.hexlify(ciphertext).decode()

def b64_encrypt(plaintext):
    """Base64加密"""
    public_key = RSA.import_key(PUBLIC_KEY_B64)
    cipher = PKCS1_v1_5.new(public_key)
    ciphertext = cipher.encrypt(plaintext.encode())
    return base64.b64encode(ciphertext).decode()

def des_encrypt(text):
    """DES3加密"""
    cipher = DES3.new(DES_KEY, DES3.MODE_CBC, DES_IV)
    ciphertext = cipher.encrypt(pad(text.encode(), DES3.block_size))
    return ciphertext.hex()

def des_decrypt(text):
    """DES3解密"""
    ciphertext = bytes.fromhex(text)
    cipher = DES3.new(DES_KEY, DES3.MODE_CBC, DES_IV)
    plaintext = unpad(cipher.decrypt(ciphertext), DES3.block_size)
    return plaintext.decode()

def aes_encrypt(data, key="34d7cb0bcdf07523"):
    """AES加密"""
    if isinstance(data, dict):
        data = json.dumps(data)
    key_bytes = key.encode('utf-8')
    data_bytes = data.encode('utf-8')
    cipher = AES.new(key_bytes, AES.MODE_ECB)
    ct_bytes = cipher.encrypt(pad(data_bytes, AES.block_size))
    return ct_bytes.hex()

def encode_phone(text):
    """编码手机号"""
    return ''.join(chr(ord(char) + 2) for char in text)

def rsa_encrypt_long(plaintext):
    """处理超长文本的RSA加密函数 - 用于星播客"""
    key_content = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIPOHtjs6p4sTlpFvrx+ESsYkEvyT4JB/dcEbU6C8+yclpcmWEvwZFymqlKQq89laSH4IxUsPJHKIOiYAMzNibhED1swzecH5XLKEAJclopJqoO95o8W63Euq6K+AKMzyZt1SEqtZ0mXsN8UPnuN/5aoB3kbPLYpfEwBbhto6yrwIDAQAB"
    res_key = "-----BEGIN PUBLIC KEY-----\n" + key_content + "\n-----END PUBLIC KEY-----"
    
    public_key = RSA.import_key(res_key)
    cipher = PKCS1_v1_5.new(public_key)
    
    key_size = public_key.size_in_bytes()
    max_chunk_size = key_size - 11
    
    if not isinstance(plaintext, bytes):
        plaintext = plaintext.encode('utf-8')
    
    encrypted_chunks = []
    for i in range(0, len(plaintext), max_chunk_size):
        chunk = plaintext[i:i + max_chunk_size]
        encrypted_chunk = cipher.encrypt(chunk)
        encrypted_chunks.append(encrypted_chunk)
    
    ciphertext = b"".join(encrypted_chunks)
    return base64.b64encode(ciphertext).decode('utf-8')

# SSL适配器
class DESAdapter(HTTPAdapter):
    def __init__(self, *args, **kwargs):
        CIPHERS = 'DEFAULT@SECLEVEL=1'.split(':')
        random.shuffle(CIPHERS)
        self.CIPHERS = ':'.join(CIPHERS) + ':!aNULL:!eNULL:!MD5'
        super().__init__(*args, **kwargs)
    
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.CIPHERS)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)

# 面板操作（支持青龙/呆呆面板）
class QingLongManager:
    def __init__(self):
        self.config = get_config()
        self.use_daidai = self.config.get('use_daidai', False)
        self.url, self.token = self._get_connection()
    
    def _get_connection(self):
        """获取面板连接（支持青龙/呆呆面板）"""
        if self.use_daidai:
            dd_ddname = self.config.get('dd_dx_ddname', '')
            if not dd_ddname:
                sender.reply(format_msg('config_error', error='未配置呆呆面板信息\n请填写:\n• 对接面板类型: 呆呆\n• 对接面板配置: Host丨AppKey丨AppSecret'))
                exit(0)
            
            parts = dd_ddname.split('丨')
            if len(parts) != 3:
                sender.reply(format_msg('config_error', error=f'呆呆面板配置格式错误\n当前格式: {dd_ddname}\n正确格式: Host丨AppKey丨AppSecret'))
                exit(0)
            
            dd_url, app_key, app_secret = [p.strip() for p in parts]
            if not all([dd_url, app_key, app_secret]):
                sender.reply(format_msg('config_error', error='呆呆面板配置参数不完整'))
                exit(0)
            
            if not dd_url.startswith(('http://', 'https://')):
                sender.reply(format_msg('config_error', error=f'呆呆面板地址格式错误: {dd_url}'))
                exit(0)
            
            try:
                url = f'{dd_url}/api/open-api/token'
                data = {"app_key": app_key, "app_secret": app_secret}
                response = requests.post(url, json=data)
                if response.status_code == 200:
                    result = response.json()
                    access_token = result.get('data', {}).get('access_token')
                    if access_token:
                        return dd_url, access_token
                sender.reply(format_msg('config_error', error='获取呆呆面板Token失败'))
                exit(0)
            except Exception as e:
                sender.reply(format_msg('config_error', error=f'连接呆呆面板失败: {str(e)}'))
                exit(0)
        else:
            if not self.config['qlname']:
                sender.reply(format_msg('config_error', error='未配置青龙面板信息\n请填写:\n• 对接面板类型: 青龙\n• 对接面板配置: Host丨ClientID丨ClientSecret'))
                exit(0)
            
            parts = self.config['qlname'].split('丨')
            if len(parts) != 3:
                sender.reply(format_msg('config_error', error=f'青龙面板配置格式错误\n当前格式: {self.config["qlname"]}\n正确格式: Host丨ClientID丨ClientSecret'))
                exit(0)
            
            url, client_id, client_secret = [p.strip() for p in parts]
            if not all([url, client_id, client_secret]):
                sender.reply(format_msg('config_error', error='青龙配置参数不完整'))
                exit(0)
            
            try:
                token_url = f'{url}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
                response = requests.get(token_url)
                if response.status_code == 200:
                    result = response.json()
                    if "token" in result.get('data', {}):
                        return url, result['data']['token']
                sender.reply(format_msg('config_error', error='获取青龙Token失败'))
                exit(0)
            except Exception as e:
                sender.reply(format_msg('config_error', error=f'连接青龙失败: {str(e)}'))
                exit(0)
    
    def _get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def get_env_id(self, account):
        """获取环境变量ID（支持青龙/呆呆面板）"""
        headers = self._get_headers()
        
        if self.use_daidai:
            params = {"keyword": str(account), "page_size": 100}
            response = requests.get(f"{self.url}/api/envs", headers=headers, params=params).json()
            data_list = response.get('data', [])
            if isinstance(data_list, list):
                for env in data_list:
                    if env.get('name') == self.config['osname'] and str(account) in (env.get('remarks') or ''):
                        return env['id']
            return None
        else:
            url = f"{self.url}/open/envs"
            response = requests.get(url, headers=headers).json()
            
            if response['code'] == 200:
                for env in response['data']:
                    if env['name'] == self.config['osname'] and str(account) in (env.get('remarks') or ''):
                        return env['id']
            return None
    
    def add_or_update_env(self, account, value):
        """添加或更新环境变量（支持青龙/呆呆面板）"""
        env_id = self.get_env_id(account)
        auth_time = middleware.bucketGet('dd_dx_auth', account) or str(datetime.now().date())
        phone = mask_phone(account)
        
        data = {
            "value": value,
            "name": self.config['osname'],
            "remarks": f'电信:{account}丨用户:{userid}丨到期:{auth_time}丨电信管理'
        }
        
        headers = self._get_headers()
        
        if self.use_daidai:
            if self.config.get('panel_group'):
                data["group"] = self.config['panel_group']
            if env_id:
                requests.put(f"{self.url}/api/envs/{env_id}", headers=headers, json=data)
            else:
                requests.post(f"{self.url}/api/envs", headers=headers, json=data)
        else:
            if env_id:
                data["id"] = env_id
                requests.put(f"{self.url}/open/envs", headers=headers, json=data)
            else:
                requests.post(f"{self.url}/open/envs", headers=headers, json=[data])
    
    def delete_env(self, env_id):
        """删除环境变量（支持青龙/呆呆面板）"""
        if env_id:
            headers = self._get_headers()
            if self.use_daidai:
                requests.delete(f"{self.url}/api/envs/{env_id}", headers=headers)
            else:
                url = f"{self.url}/open/envs"
                requests.delete(url, headers=headers, json=[env_id])

# 电信API操作
class TelecomAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C) AppleWebKit/537.36 Chrome/104.0.5112.97 Mobile Safari/537.36"
        })
        self.session.mount('https://', DESAdapter())
        self.session.verify = False
    
    def login(self, phone, password):
        """账号登录"""
        alphabet = 'abcdef0123456789'
        uuid_parts = [''.join(random.sample(alphabet, 8)), ''.join(random.sample(alphabet, 4)),
                     '4' + ''.join(random.sample(alphabet, 3)), ''.join(random.sample(alphabet, 4)),
                     ''.join(random.sample(alphabet, 12))]
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        auth_cipher = f'iPhone 14 15.4.{uuid_parts[0]}{uuid_parts[1]}{phone}{timestamp}{password[:6]}0$$$0.'
        
        payload = {
            "headerInfos": {
                "code": "userLoginNormal", "timestamp": timestamp, "broadAccount": "", "broadToken": "",
                "clientType": "#11.3.0#channel50#iPhone 14 Pro Max#", "shopId": "20002", "source": "110003",
                "sourcePassword": "Sid98s", "token": "", "userLoginName": encode_phone(phone)
            },
            "content": {
                "attach": "test",
                "fieldData": {
                    "loginType": "4", "accountType": "", "loginAuthCipherAsymmertric": b64_encrypt(auth_cipher),
                    "deviceUid": uuid_parts[0] + uuid_parts[1] + uuid_parts[2], "phoneNum": encode_phone(phone),
                    "isChinatelecom": "0", "systemVersion": "15.4.0", "authentication": encode_phone(password)
                }
            }
        }
        
        try:
            resp = self.session.post('https://appgologin.189.cn:9031/login/client/userLoginNormal', 
                                   json=payload, timeout=15)
            result = resp.json()
            login_data = result.get('responseData', {}).get('data')
            if login_data and login_data.get('loginSuccessResult'):
                return login_data['loginSuccessResult']
        except Exception as e:
            print(f"登录异常: {e}")
        return None
    
    def get_ticket(self, phone, user_id, token):
        """获取ticket"""
        url = 'https://appgologin.189.cn:9031/map/clientXML'
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        target_id = des_encrypt(user_id)
        
        data = f'<Request><HeaderInfos><Code>getSingle</Code><Timestamp>{timestamp}</Timestamp><BroadAccount></BroadAccount><BroadToken></BroadToken><ClientType>#9.6.1#channel50#iPhone 14 Pro Max#</ClientType><ShopId>20002</ShopId><Source>110003</Source><SourcePassword>Sid98s</SourcePassword><Token>{token}</Token><UserLoginName>{phone}</UserLoginName></HeaderInfos><Content><Attach>test</Attach><FieldData><TargetId>{target_id}</TargetId><Url>4a6862274835b451</Url></FieldData></Content></Request>'
        
        try:
            headers = {
                'User-Agent': 'CtClient;10.4.1;Android;13;22081212C;NTQzNzgx!#!MTgwNTg5',
                'Content-Type': 'application/xml'
            }
            resp = self.session.post(url, data=data, headers=headers, timeout=15)
            ticket_match = re.findall('<Ticket>(.*?)</Ticket>', resp.text)
            if ticket_match:
                return des_decrypt(ticket_match[0])
        except Exception as e:
            print(f"获取ticket异常: {e}")
        return None
    
    def get_sign(self, ticket):
        """获取sign"""
        url = f'https://wappark.189.cn/jt-sign/ssoHomLogin?ticket={ticket}'
        try:
            result = self.session.get(url, timeout=15).json()
            if result.get('resoultCode') == '0':
                return result.get('sign'), result.get('accId')
        except Exception as e:
            print(f"获取sign异常: {e}")
        return None, None
    
    def query_account_info(self, phone, password):
        """查询账号信息"""
        try:
            # 登录
            login_result = self.login(phone, password)
            if not login_result:
                return {"status": "error", "message": "登录失败"}
            
            # 获取ticket和sign
            ticket = self.get_ticket(phone, login_result['userId'], login_result['token'])
            if not ticket:
                return {"status": "error", "message": "获取ticket失败"}
            
            sign, acc_id = self.get_sign(ticket)
            if not sign:
                return {"status": "error", "message": "获取sign失败"}
            
            self.session.headers['sign'] = sign
            
            # 查询各项信息
            coin_result = self._query_coin(phone)
            sign_result = self._query_sign_days(phone)
            sign_status = self._check_sign_status(phone)
            pet_result = self._query_pet_info(phone)
            
            return {
                "status": "success", "coin": coin_result.get("coin", 0), "sign_days": sign_result.get("days", 0),
                "today_signed": sign_status.get("today_signed", False), "sign_message": sign_status.get("message", ""),
                "pet_level": pet_result.get("level", 0), "pet_growth": pet_result.get("growth_value", 0),
                "pet_full_growth": pet_result.get("full_growth_value", 0), "pet_progress": pet_result.get("progress_percentage", 0)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _query_coin(self, phone):
        """查询金豆"""
        try:
            url = 'https://wappark.189.cn/jt-sign/api/home/userCoinInfo'
            resp = self.session.post(url, json={"para": encrypt_para({"phone": phone})}, timeout=15)
            data = resp.json()
            return {"status": "success", "coin": data.get("totalCoin", 0)} if data.get('code') != 401 else {"status": "error", "message": "sign过期", "coin": 0}
        except Exception as e:
            return {"status": "error", "message": str(e), "coin": 0}
    
    def _query_sign_days(self, phone):
        """查询签到天数"""
        try:
            now = datetime.now()
            value = {"phone": phone, "checkDate": f"{now.year}-{now.month:02d}"}
            url = 'https://wappark.189.cn/jt-sign/api/signInfo'
            resp = self.session.post(url, json={"para": encrypt_para(value)}, timeout=15)
            data = resp.json()
            if data.get("resoultCode") == "0":
                signed_days = [item for item in data["data"]["signInfo"] if item.get("state") == "Y"]
                return {"status": "success", "days": len(signed_days)}
            return {"status": "error", "message": data.get("message", "未知错误"), "days": 0}
        except Exception as e:
            return {"status": "error", "message": str(e), "days": 0}
    
    def _check_sign_status(self, phone):
        """检查签到状态"""
        try:
            timestamp = int(time.time() * 1000)
            value = {"phone": phone, "sysType": "", "date": str(timestamp)}
            url = 'https://wappark.189.cn/jt-sign/webSign/sign'
            resp = self.session.post(url, json={"encode": aes_encrypt(value)}, timeout=15)
            data = resp.json()
            
            msg = data.get("data", {}).get("msg", "")
            if "已签到" in msg or "不能重复签到" in msg:
                return {"status": "success", "today_signed": True, "message": msg}
            elif "签到成功" in msg:
                return {"status": "success", "today_signed": False, "message": msg}
            return {"status": "success", "today_signed": False, "message": msg}
        except Exception as e:
            return {"status": "error", "today_signed": False, "message": str(e)}
    
    def _query_pet_info(self, phone):
        """查询宠物信息"""
        try:
            url = 'https://wappark.189.cn/jt-sign/paradise/getParadiseInfo'
            resp = self.session.post(url, json={'para': encrypt_para({'phone': phone})}, timeout=15)
            data = resp.json()
            
            if data.get('resoultCode') == "0":
                level_info = data.get('userInfo', {}).get('levelInfoMap', {})
                level, growth, full_growth = level_info.get('level', 0), level_info.get('growthValue', 0), level_info.get('fullGrowthCoinValue', 0)
                return {
                    "status": "success", "level": level, "growth_value": growth, "full_growth_value": full_growth,
                    "progress_percentage": round((growth / full_growth * 100), 1) if full_growth > 0 else 0
                }
            return {"status": "error", "message": data.get('msg', '未知错误')}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_xbk_usercode(self, phone, ticket):
        """获取星播客usercode"""
        try:
            url = "https://xbk.189.cn/xbkapi/api/auth/jump"
            params = {
                "userID": ticket,
                "version": "9.3.3",
                "type": "room",
                "l": "renwu"
            }
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1"
            }

            response = self.session.get(url, params=params, headers=headers, allow_redirects=False)
            
            if response.status_code not in (301, 302, 303, 307, 308):
                return None
                
            location_header = response.headers.get("Location")
            if not location_header:
                return None

            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(location_header)
            query_params = parse_qs(parsed.query)

            usercode_list = query_params.get("usercode", [])
            if not usercode_list:
                return None

            return usercode_list[0]

        except Exception as e:
            print(f"获取星播客usercode错误: {str(e)}")
            return None

    def get_xbk_usertoken(self, phone, usercode):
        """获取星播客usertoken"""
        try:
            url = "https://xbk.189.cn/xbkapi/api/auth/userinfo/codeToken"
            data = {"usercode": usercode}
            headers = {
                "User-Agent": "Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1"
            }
            
            response = self.session.post(url, data=data, headers=headers)
            response_json = response.json()

            if 'data' in response_json and 'token' in response_json['data']:
                token = response_json['data']['token']
                return token
            else:
                return None

        except Exception as e:
            print(f"获取星播客usertoken错误: {str(e)}")
            return None

    def get_xbk_win_list(self, phone, token):
        """查询星播客中奖记录"""
        try:
            url = "https://xbk.189.cn/xbkapi/active/v2/lottery/getMyWinList?page=1&give_status=200&activeCode="
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; U; Android 12; zh-cn; ONEPLUS A9000 Build/QKQ1.190716.003) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1',
                'Authorization': 'Bearer ' + rsa_encrypt_long(token)
            }

            response = self.session.get(url, headers=headers)
            response_text = response.text
            result = json.loads(response_text)
            
            if 'data' not in result:
                return []
                
            items = result.get('data', [])
            return items

        except Exception as e:
            print(f"查询星播客奖品错误: {e}")
            return []

# =============================
# 517活动查询工具函数
# =============================

def _517_get_set_cookie_header(response):
    set_cookie = response.headers.get("Set-Cookie", "")
    raw_headers = getattr(getattr(response, "raw", None), "headers", None)
    if raw_headers:
        get_all = getattr(raw_headers, "get_all", None) or getattr(raw_headers, "getlist", None)
        if get_all:
            cookies = get_all("Set-Cookie")
            if cookies:
                set_cookie = "; ".join(cookies)
    return set_cookie

def _517_extract_reqparam(location):
    match = re.search(r"[?&]reqparam=([^&]+)", location or "")
    if not match:
        return ""
    return urllib.parse.unquote(match.group(1))

def _517_extract_newmallsession(set_cookie):
    match = re.search(r"(newmallsession=[^;]+;)", set_cookie or "")
    if not match:
        return ""
    return match.group(1)

def _517_get_query_param(url, key):
    parsed_url = urllib.parse.urlparse(url or "")
    query = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
    values = query.get(key)
    return values[0] if values else ""

def _517_normalize_cookie(cookie):
    return (cookie or "").strip().rstrip(";")

def _517_build_api_context(newmallsession, referer):
    token = _517_get_query_param(referer, "Token")
    channel = _517_get_query_param(referer, "channel") or "HGOKHD"
    cookie = _517_normalize_cookie(newmallsession)
    return {
        "channel": channel,
        "token": token,
        "referer": referer,
        "cookie": cookie,
        "headers": {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "appcode": "HGOKHD",
            "appCode": "HGOKHD",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Cookie": cookie,
            "Host": "apps.telefen.com",
            "Referer": referer,
            "sec-ch-ua": "\"Google Chrome\";v=\"147\", \"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"147\"",
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": "\"iOS\"",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "ssotoken": token,
            "SSOToken": token,
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.5 Mobile/15E148 Safari/604.1",
        },
    }

CARD_PIECES_517 = [
    (10000, "天翼云盘"),
    (10001, "天翼智铃"),
    (10002, "天翼智屏"),
    (10003, "通讯助理"),
    (10004, "云智手机"),
    (10005, "直连卫星"),
]

def _517_parse_piece_collection(data):
    biz_data = data.get("data") if isinstance(data, dict) else {}
    if not isinstance(biz_data, dict):
        biz_data = {}
    piece_list = biz_data.get("pieceList", []) or []
    piece_map = {}
    for piece in piece_list:
        if not isinstance(piece, dict):
            continue
        piece_id = int(piece.get("pieceId", 0) or 0)
        valid_count = int(piece.get("validPieceCount", 0) or 0)
        piece_map[piece_id] = {
            "pieceId": piece_id,
            "pieceName": piece.get("pieceName", ""),
            "validPieceCount": valid_count,
        }
    cards = []
    missing = []
    for piece_id, name in CARD_PIECES_517:
        item = piece_map.get(piece_id, {})
        available_count = int(item.get("validPieceCount", 0) or 0)
        cards.append({
            "pieceId": piece_id,
            "pieceName": item.get("pieceName") or name,
            "availableCount": available_count,
        })
        if available_count <= 0:
            missing.append(name)
    return {
        "cards": cards,
        "missing": missing,
        "is_all_collected": len(missing) == 0,
    }

def query_517_activity_status(phone, password, telecom_api):
    """查询517活动状态，返回结构化结果"""
    try:
        login_result = telecom_api.login(phone, password)
        if not login_result:
            return {"status": "error", "message": "登录失败"}

        ticket = telecom_api.get_ticket(phone, login_result['userId'], login_result['token'])
        if not ticket:
            return {"status": "error", "message": "获取ticket失败"}

        session = requests.Session()
        session.mount("https://", DESAdapter())
        session.verify = False
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; 22081212C Build/TKQ1.220829.002) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.97 Mobile Safari/537.36"
        })

        # 进入517活动
        params = {
            "channel": "HGOKHD",
            "action": "2",
            "rdurl": "https://apps.telefen.com/mallactive/ck517?channel=HGOKHD",
            "promoid": "f15c4b971ecfa50b",
            "ticket": ticket,
            "utm_scha": "utm_ch-010001002009.utm_sch-hg_sy_yxtc-1.utm_af-1000000037.utm_as-456876200001.utm_sd1-S0076579",
        }
        headers = {
            "User-Agent": "CtClient;13.2.0;Android;14;22021211RC;",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Upgrade-Insecure-Requests": "1",
            "X-Requested-With": "com.ct.client",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
        }
        response = session.get(
            "https://apps.telefen.com/middleparse/api/access/ticket",
            params=params,
            headers=headers,
            allow_redirects=False,
            timeout=15,
        )

        if response.status_code not in (301, 302, 303, 307, 308):
            return {"status": "error", "message": f"517活动入口异常: {response.status_code}"}

        set_cookie = _517_get_set_cookie_header(response)
        location = response.headers.get("Location", "")
        reqparam = _517_extract_reqparam(location)
        newmallsession = _517_extract_newmallsession(set_cookie)

        # 二跳获取Token
        merchants_location = ""
        if reqparam:
            try:
                dock_resp = session.get(
                    location if location else "https://m.telefen.com/MobileSSOv2/MerchantsDock.aspx",
                    headers=headers,
                    allow_redirects=False,
                    timeout=15,
                )
                merchants_location = dock_resp.headers.get("Location", "")
            except Exception:
                pass

        api_context = _517_build_api_context(newmallsession, merchants_location)
        if not api_context.get("token"):
            return {"status": "error", "message": "517活动Token获取失败"}

        # 访问517落地页刷新cookie
        try:
            page_headers = {
                "User-Agent": api_context["headers"]["User-Agent"],
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Cookie": api_context["headers"]["Cookie"],
                "Referer": location,
            }
            page_resp = session.get(
                api_context["referer"],
                headers=page_headers,
                allow_redirects=True,
                timeout=15,
            )
            page_set_cookie = _517_get_set_cookie_header(page_resp)
            page_newmallsession = _517_extract_newmallsession(page_set_cookie)
            if page_newmallsession:
                cookie = _517_normalize_cookie(page_newmallsession)
                api_context["cookie"] = cookie
                api_context["headers"]["Cookie"] = cookie
        except Exception:
            pass

        # 查询任务列表
        task_params = {
            "channel": api_context["channel"],
            "noload": "true",
            "activeCode": "2026517",
        }
        task_resp = session.get(
            "https://apps.telefen.com/mallactive/api/v26517/activity/home",
            params=task_params,
            headers=api_context["headers"],
            timeout=15,
        )
        try:
            task_data = task_resp.json()
        except Exception:
            task_data = None

        task_list = []
        unfinished_count = 0
        finished_count = 0
        if isinstance(task_data, dict) and task_data.get("errCode") == "0000":
            biz_data = task_data.get("data") or {}
            raw_tasks = biz_data.get("taskList", []) or [] if isinstance(biz_data, dict) else []
            for task in raw_tasks:
                if not isinstance(task, dict):
                    continue
                task_name = task.get("taskName", "")
                is_finished = task.get("isFinished", 0)
                completed_times = task.get("completedTimes", 0)
                max_times = task.get("maxTimes", 0)
                task_list.append({
                    "name": task_name,
                    "finished": is_finished == 1,
                    "progress": f"{completed_times}/{max_times}",
                })
                if is_finished == 1:
                    finished_count += 1
                else:
                    unfinished_count += 1

        # 查询卡片和抽奖次数
        piece_params = {"gameId": "10000"}
        piece_resp = session.get(
            "https://apps.telefen.com/mallactive/api/fragment/getMyPieceList",
            params=piece_params,
            headers=api_context["headers"],
            timeout=15,
        )
        try:
            piece_data = piece_resp.json()
        except Exception:
            piece_data = None

        total_chance_count = 0
        collection = {"cards": [], "missing": [], "is_all_collected": False}
        if isinstance(piece_data, dict):
            biz_data = piece_data.get("data") or {}
            if isinstance(biz_data, dict):
                total_chance_count = biz_data.get("totalChanceCount", 0) or 0
            collection = _517_parse_piece_collection(piece_data)

        # 查询合成记录
        has_composite = False
        try:
            comp_headers = dict(api_context["headers"])
            comp_headers["Origin"] = "https://apps.telefen.com"
            comp_resp = session.post(
                "https://apps.telefen.com/mallactive/api/fragment/getCompositeRecord",
                json={"gameId": "10000"},
                headers=comp_headers,
                timeout=15,
            )
            comp_data = comp_resp.json()
            comp_biz = comp_data.get("data") if isinstance(comp_data, dict) else None
            if isinstance(comp_biz, dict) and (
                comp_biz.get("commodityName") or comp_biz.get("compositeRecordId") is not None
                or comp_biz.get("id") is not None or comp_biz.get("compositeTime")
            ):
                has_composite = True
        except Exception:
            pass

        return {
            "status": "success",
            "task_list": task_list,
            "finished_count": finished_count,
            "unfinished_count": unfinished_count,
            "total_chance_count": total_chance_count,
            "collection": collection,
            "has_composite": has_composite,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# 支付处理
class PaymentHandler:
    def __init__(self):
        self.config = get_config()
    
    def process_payment(self, months, accounts_count=1, account=None):
        """处理支付"""
        self.config = get_config()
        
        total_money = Decimal(months) * self.config['price'] * accounts_count
        total_coins = self.config['coin'] * months * accounts_count
        ma_pay_config = self._get_ma_pay_config()
        show_wechat_pay = bool(self.config['zsm']) and not self.config['use_ma_pay']
        show_ma_pay = self.config['use_ma_pay'] and bool(ma_pay_config)
        show_coin_pay = self.config['coin'] > 0
        
        if not show_wechat_pay and not show_ma_pay and not show_coin_pay and float(total_money) > 0:
            sender.reply('❌ 未配置可用收款方式,请联系管理员!')
            return False
        
        # 免费授权
        if float(total_money) == 0:
            return self._process_free_auth(months, account)
        
        # 显示支付选项
        return self._show_payment_options(total_money, total_coins, accounts_count, months, account, ma_pay_config)

    def _get_ma_pay_config(self):
        """获取码支付配置"""
        if not self.config.get('use_ma_pay'):
            return None
        cfg = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
            'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
            'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
        }
        if cfg['switch'].lower() != 'true' or not all([cfg['gateway'], cfg['pid'], cfg['key']]):
            return None
        return cfg
    
    def _process_free_auth(self, months, account=None):
        """免费授权"""
        if account:
            # 如果有账号信息，计算基于现有授权的新到期时间
            current_auth = middleware.bucketGet('dd_dx_auth', account)
            current_time = datetime.now().strftime("%Y-%m-%d")
            
            if current_auth and current_auth > current_time:
                # 现有授权未过期，从现有到期时间延长
                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
            else:
                # 现有授权已过期或无授权，从当前时间开始
                auth_date = datetime.now()
                
            new_expiry = auth_date + timedelta(days=months * 30)
            return new_expiry.strftime("%Y-%m-%d"), 0, 0, "免费授权"
        else:
            # 没有账号信息，使用当前日期
            current_date = datetime.now().date()
            new_expiry = current_date + timedelta(days=months * 30)
            return str(new_expiry), 0, 0, "免费授权"
    
    def _show_payment_options(self, total_money, total_coins, accounts_count, months, account=None, ma_pay_config=None):
        """显示支付选项"""
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        show_wechat_pay = bool(self.config['zsm']) and not self.config['use_ma_pay']
        show_ma_pay = self.config['use_ma_pay'] and bool(ma_pay_config)
        
        options = [
            "=====选择支付方式====",
            "📦 订单信息:",
            f"   📱 账号数量: {accounts_count}个",
            f"   ⏰ 授权时长: {months}月",
            "",
            "💳 支付方式:"
        ]
        
        options_map = {}
        option_num = 1

        if show_wechat_pay:
            options.extend([
                f"   {option_num}️⃣ 微信支付",
                f"      💰 需支付: {total_money}元"
            ])
            options_map[str(option_num)] = 'wechat'
            option_num += 1

        if show_ma_pay:
            options.extend([
                f"   {option_num}️⃣ 码支付",
                f"      💰 需支付: {total_money}元"
            ])
            options_map[str(option_num)] = 'ma'
            option_num += 1
        
        if self.config['coin'] > 0:
            options.extend([
                f"   {option_num}️⃣ 积分支付",
                f"      🎯 需消耗: {total_coins}积分",
                f"      💫 当前余额: {usercoin}积分"
            ])
            options_map[str(option_num)] = 'coin'
        
        options.extend([
            "",
            "💡 请回复数字选择支付方式",
            "💡 回复'q'取消操作",
            "=================="
        ])
        
        sender.reply("\n".join(options))
        
        choice = sender.input(60000, 1, False)
        
        if choice == 'q':
            sender.reply("✅ 已取消支付")
            return False
        selected_pay = options_map.get(choice)
        if selected_pay == 'wechat' and show_wechat_pay:
            return self._process_wechat_pay(total_money, accounts_count, months, account)
        elif selected_pay == 'ma' and show_ma_pay:
            return self._process_ma_pay(total_money, months, account, ma_pay_config)
        elif selected_pay == 'coin' and self.config['coin'] > 0:
            return self._process_coin_pay(total_coins, usercoin, months, account)
        else:
            sender.reply("❌ 输入无效")
            return False

    def _process_ma_pay(self, total_money, months, account=None, ma_pay_config=None):
        """码支付"""
        if not ma_pay_config:
            sender.reply("❌ 码支付配置异常，请联系管理员")
            return False

        out_trade_no = f"DX{int(time.time())}{userid}"
        params = {
            'pid': ma_pay_config['pid'],
            'type': (ma_pay_config.get('type') or 'alipay,wxpay,qqpay').split(',')[0],
            'out_trade_no': out_trade_no,
            'name': f"{senderID}-电信授权-{str(total_money)}",
            'money': str(total_money),
            'param': userid
        }
        if ma_pay_config.get('notify_url'):
            params['notify_url'] = ma_pay_config['notify_url']
        if ma_pay_config.get('return_url'):
            params['return_url'] = ma_pay_config['return_url']

        params = {k: v for k, v in params.items() if v}
        sorted_params = sorted(params.items(), key=lambda x: x[0])
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
        params['sign'] = sign
        params['sign_type'] = 'MD5'

        gateway = ma_pay_config['gateway'].rstrip('/')
        submit_url = gateway + '/mapi.php'

        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(submit_url, data=params, headers=headers, timeout=10)
            if response.status_code != 200:
                sender.reply(f"❌ 创建支付订单失败，HTTP状态码: {response.status_code}")
                return False

            result = response.json()
            if result.get('code') != 1:
                sender.reply(f"❌ 创建支付订单失败: {result.get('msg', '未知错误')}")
                return False

            pay_url = result.get('payurl', '')
            if not pay_url:
                sender.reply("❌ 未获取到支付链接")
                return False

            qrcode_url = generate_qrcode(pay_url)
            pay_type = (ma_pay_config.get('type') or 'alipay,wxpay,qqpay').split(',')[0]
            if qrcode_url:
                send_qrcode_image(sender, qrcode_url, pay_type)
            else:
                sender.reply(f"=====码支付=====\n🎫 商品: 电信插件授权\n💰 金额: {total_money}元\n⏰ 有效期: 5分钟\n------------------\n二维码生成失败，请点击链接完成支付:\n{pay_url}\n==================")

            for _ in range(60):
                result_input = sender.listen(5000)
                if result_input == 'q' or result_input == 'Q':
                    sender.reply("✅ 已取消支付")
                    return False

                check_url = gateway
                if '/xpay/epay/api.php' not in check_url:
                    check_url = f"{check_url}/xpay/epay/api.php"
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
                        if account:
                            current_auth = middleware.bucketGet('dd_dx_auth', account)
                            current_time = datetime.now().strftime("%Y-%m-%d")
                            if current_auth and current_auth > current_time:
                                auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                            else:
                                auth_date = datetime.now()
                            new_expiry = auth_date + timedelta(days=months * 30)
                            return new_expiry.strftime("%Y-%m-%d"), float(total_money), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "码支付"
                        current_date = datetime.now().date()
                        new_expiry = current_date + timedelta(days=months * 30)
                        return str(new_expiry), float(total_money), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "码支付"
                except:
                    continue

            sender.reply("❌ 支付超时,请重新发起支付!")
            return False
        except Exception as e:
            sender.reply(f"❌ 支付请求失败: {str(e)}")
            return False
    
    def _process_wechat_pay(self, total_money, accounts_count, months, account=None):
        """微信支付"""
        if sender.atWaitPay():
            sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
            return False
        
        pay_msg = f"=====微信扫码支付====\n🎫 商品: 电信插件授权\n📱 账号数量: {accounts_count}个\n📅 时长: {months}月\n💰 金额: {total_money}元\n请使用微信扫码支付\n回复'q'取消支付\n=================="
        sender.reply(pay_msg)
        sender.replyImage(self.config['zsm'])
        
        result = sender.waitPay("q", 100 * 1000)
        if str(result) == 'q':
            sender.reply('✅ 已取消支付')
            return False
        
        money, pay_time, from_name = self._parse_payment_result(result)
        if money is None:
            sender.reply("=====支付解析失败=====\n❌ 无法解析支付结果\n💡 如果您已完成支付，请联系管理员\n==================")
            return False
        elif float(money) >= float(total_money):
            # 正确计算新的到期时间
            if account:
                # 如果有账号信息，计算基于现有授权的新到期时间
                current_auth = middleware.bucketGet('dd_dx_auth', account)
                current_time = datetime.now().strftime("%Y-%m-%d")
                
                if current_auth and current_auth > current_time:
                    # 现有授权未过期，从现有到期时间延长
                    auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                else:
                    # 现有授权已过期或无授权，从当前时间开始
                    auth_date = datetime.now()
                    
                new_expiry = auth_date + timedelta(days=months * 30)
                return new_expiry.strftime("%Y-%m-%d"), money, pay_time, "微信支付"
            else:
                # 没有账号信息，使用当前日期
                current_date = datetime.now().date()
                new_expiry = current_date + timedelta(days=months * 30)
                return str(new_expiry), money, pay_time, "微信支付"
        else:
            sender.reply(f"=====支付金额错误=====\n💰 应付: {total_money}元\n💳 实付: {money}元\n❗ 请联系管理员处理退款！\n==================")
            return False
    
    def _process_coin_pay(self, total_coins, usercoin, months, account=None):
        """积分支付"""
        if int(usercoin) < total_coins:
            sender.reply(f"=====积分不足=====\n👤 当前积分: {usercoin}\n📍 需要积分: {total_coins}\n==================")
            return False
        
        confirm_msg = f"=====积分支付确认=====\n💫 消耗积分: {total_coins}\n⏰ 授权时长: {months}月\n确认请回复【y】\n取消请回复【n】\n=================="
        sender.reply(confirm_msg)
        
        if confirm_operation():
            try:
                new_balance = int(usercoin) - total_coins
                middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                
                # 正确计算新的到期时间
                if account:
                    # 如果有账号信息，计算基于现有授权的新到期时间
                    current_auth = middleware.bucketGet('dd_dx_auth', account)
                    current_time = datetime.now().strftime("%Y-%m-%d")
                    
                    if current_auth and current_auth > current_time:
                        # 现有授权未过期，从现有到期时间延长
                        auth_date = datetime.strptime(current_auth, "%Y-%m-%d")
                    else:
                        # 现有授权已过期或无授权，从当前时间开始
                        auth_date = datetime.now()
                        
                    new_expiry = auth_date + timedelta(days=months * 30)
                    return new_expiry.strftime("%Y-%m-%d"), total_coins, new_balance, "积分支付"
                else:
                    # 没有账号信息，使用当前日期
                    current_date = datetime.now().date()
                    new_expiry = current_date + timedelta(days=months * 30)
                    return str(new_expiry), total_coins, new_balance, "积分支付"
            except Exception as e:
                sender.reply(f"❌ 积分支付处理失败: {str(e)}")
                return False
        else:
            sender.reply("✅ 已取消支付")
            return False
    
    def _parse_payment_result(self, result):
        """解析支付结果"""
        try:
            # 尝试解析支付结果
            if isinstance(result, str):
                try:
                    result = json.loads(result)
                except json.JSONDecodeError:
                    # 处理纯文本格式
                    if "二维码赞赏到账" in result:
                        amount = result.split("收款金额￥")[1].split("\n")[0]
                        time = result.split("到账时间")[1].split("\n")[0]
                        money = float(amount)
                        pay_time = time.strip()
                        from_name = ''
                        return money, pay_time, from_name
                    else:
                        return None, None, None
                        
            if isinstance(result, dict):
                money = 0
                pay_time = ''
                from_name = ''
                
                # 支持多种收款消息格式
                # 新格式1: 微信赞赏
                if result.get('Type') == '微信赞赏':
                    money = float(result.get('Money', 0))
                    pay_time = result.get('Time', '').split('.')[0].replace('T', ' ')
                    from_name = result.get('FromName', '')
                # 新格式2: 微信收款
                elif result.get('Type') == '微信收款':
                    money = float(result.get('Money', 0))
                    pay_time = result.get('Time', '').split('.')[0].replace('T', ' ')
                    from_name = result.get('FromName', '')
                # 旧格式1: BORW格式
                elif result.get('Money'):
                    money = float(result.get('Money', 0))
                    pay_time = result.get('Time', '').replace('T', ' ').split('.')[0]
                    from_name = result.get('FromName', '')
                # 旧格式2: GW格式
                elif result.get('money'):
                    money = float(result.get('money', 0))
                    pay_time = result.get('time', '').replace('T', ' ').split('.')[0]
                    from_name = result.get('fromName', '')
                # 其他可能的格式
                elif result.get('type') == '微信赞赏':
                    money = float(result.get('money', 0))
                    pay_time = result.get('time', '')
                    from_name = result.get('from_name', '')
                elif result.get('type') == '微信收款':
                    money = float(result.get('money', 0))
                    pay_time = result.get('time', '')
                    from_name = result.get('from_name', '')
                else:
                    return None, None, None
                    
                if not pay_time:
                    pay_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                return money, pay_time, from_name
                
            return None, None, None
            
        except (ValueError, TypeError, KeyError) as e:
            print(f"解析支付结果错误: {str(e)}")
            return None, None, None
        except Exception as e:
            print(f"处理支付结果时出错: {str(e)}")
            return None, None, None

# 主要业务逻辑类
class TelecomManager:
    def __init__(self):
        self.ql = QingLongManager()
        self.api = TelecomAPI()
        self.payment = PaymentHandler()
        self.today = str(datetime.now().date())
    
    def login_account(self):
        """账号登录"""
        guide = f"=====电信账号登录=====\n请按格式输入: 手机号#密码\n🔰 支持批量登录，一行一个账号\n回复'q'退出操作\n=================="
        sender.reply(guide)
        
        account_info = sender.input(120000, 1, False)
        if not account_info or account_info.lower() == 'q':
            sender.reply("✅ 已取消登录")
            exit(0)
        
        lines = account_info.strip().split('\n')
        success_count, fail_count = 0, 0
        accounts = parse_accounts(uservalue) or []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('#')
            if len(parts) != 2:
                fail_count += 1
                continue
            
            phone, password = parts
            if not re.match(r'^1[3-9]\d{9}$', phone):
                fail_count += 1
                continue
            
            if self.api.login(phone, password):
                middleware.bucketSet('dd_dx_token', phone, line)
                if phone not in accounts:
                    accounts.append(phone)
                success_count += 1
            else:
                fail_count += 1
        
        if accounts:
            middleware.bucketSet('dd_dx_user', userid, str(accounts))
        
        if len(lines) > 1:
            sender.reply(f"=====批量登录结果=====\n✅ 成功: {success_count}个账号\n❌ 失败: {fail_count}个账号\n💡 发送 电信管理 可管理账号\n==================")
        elif success_count == 1:
            phone = lines[0].split('#')[0]
            auth_status, auth_time = check_auth_status(phone)
            next_step = '发送 电信管理 可管理账号' if auth_status == "✅ 已授权" else '发送 电信管理 可进行授权'
            sender.reply(format_msg('login_success', phone=mask_phone(phone), status=auth_status, next_step=next_step))
        else:
            sender.reply("=====登录失败=====\n❌ 所有账号登录均失败\n==================")
    
    def manage_accounts(self):
        """账号管理"""
        accounts = parse_accounts(uservalue)
        if not accounts:
            sender.reply(format_msg('no_accounts', cmd='电信登录'))
            return
        
        menu_items = ["=====电信账号管理=====", "[0] 全部账号授权", "[99] 删除所有账号"]
        
        for i, account in enumerate(accounts, 1):
            auth_status, auth_time = check_auth_status(account)
            menu_items.append(f"[{i}] 账号: {mask_phone(account)}")
            menu_items.append(f"    授权: {auth_status} 到期: {auth_time}")
        
        menu_items.extend(["选择要管理的账号(输入数字)", "回复'q'退出操作", "=================="])
        sender.reply("\n".join(menu_items))
        
        choice = sender.input(120000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply('✅ 已退出管理')
            return
        
        if choice == '0':
            self._batch_authorize(accounts)
        elif choice == '99':
            self._delete_all_accounts(accounts)
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    self._single_account_operation(accounts[index])
                else:
                    sender.reply("❌ 无效的账号编号")
            except ValueError:
                sender.reply("❌ 请输入有效的数字")
    
    def _batch_authorize(self, accounts):
        """批量授权"""
        need_auth = [acc for acc in accounts if check_auth_status(acc)[0] != "✅ 已授权"]
        if not need_auth:
            sender.reply("=====无需授权=====\n✅ 所有账号均已授权且未过期\n==================")
            return
        
        sender.reply(f"=====批量授权确认=====\n📊 待授权账号: {len(need_auth)}个\n📅 请输入授权月数(1-12):\n==================")
        months_input = sender.input(120000, 1, False)
        if not months_input:
            return
        
        months = validate_input(months_input, 12, "月数")
        
        # 询问授权方式
        sender.reply(f"""=====批量授权方式=====
📊 待授权账号: {len(need_auth)}个
📅 授权时长: {months}月

💡 请选择授权方式:
  [1] 逐个授权 - 每个账号单独支付
  [2] 一次性授权 - 一次支付授权所有账号

回复数字选择:
==================""")
        
        auth_mode = sender.input(60000, 1, False)
        if not auth_mode:
            sender.reply("⏰ 操作超时")
            return
        
        if auth_mode == '1':
            # 逐个授权模式
            success_count = 0
            failed_accounts = []
            
            for i, account in enumerate(need_auth, 1):
                sender.reply(f"""=====授权进度=====
📱 当前账号: {mask_phone(account)} ({i}/{len(need_auth)})
📅 授权时长: {months}月
==================""")
                
                result = self.payment.process_payment(months, 1, account)
                
                if result:
                    new_expiry, amount, time_info, pay_type = result
                    try:
                        middleware.bucketSet('dd_dx_auth', account, new_expiry)
                        token = middleware.bucketGet('dd_dx_token', account)
                        if token:
                            self.ql.add_or_update_env(account, token)
                        success_count += 1
                        sender.reply(f"✅ {mask_phone(account)} 授权成功！到期: {new_expiry}")
                    except Exception as e:
                        failed_accounts.append(mask_phone(account))
                        sender.reply(f"❌ {mask_phone(account)} 授权失败: {str(e)}")
                else:
                    failed_accounts.append(mask_phone(account))
                    sender.reply(f"⚠️ {mask_phone(account)} 支付取消或失败")
                
                # 如果不是最后一个账号，询问是否继续
                if i < len(need_auth):
                    sender.reply("💡 继续下一个账号? (Y继续/N退出)")
                    continue_choice = sender.input(30000, 1, False)
                    if continue_choice and continue_choice.lower() in ['n', 'N', '否']:
                        sender.reply(f"⏸️ 已停止批量授权\n✅ 已授权: {success_count}个\n⚠️ 剩余: {len(need_auth) - i}个")
                        return
            
            # 显示最终结果
            result_msg = f"""=====批量授权完成=====
✅ 成功授权: {success_count}/{len(need_auth)}个
📅 授权时长: {months}月"""
            
            if failed_accounts:
                result_msg += f"\n\n⚠️ 失败账号:\n" + "\n".join([f"   • {acc}" for acc in failed_accounts])
            
            result_msg += "\n=================="
            sender.reply(result_msg)
            
        elif auth_mode == '2':
            # 一次性授权模式
            result = self.payment.process_payment(months, len(need_auth))
            
            if result:
                new_expiry, amount, time_info, pay_type = result
                success_count = 0
                for account in need_auth:
                    try:
                        middleware.bucketSet('dd_dx_auth', account, new_expiry)
                        token = middleware.bucketGet('dd_dx_token', account)
                        if token:
                            self.ql.add_or_update_env(account, token)
                            success_count += 1
                    except Exception:
                        continue
                
                sender.reply(f"=====授权成功=====\n✅ 成功: {success_count}/{len(need_auth)}个账号\n📅 到期时间: {new_expiry}\n💰 支付方式: {pay_type}\n==================")
        else:
            sender.reply("❌ 无效的选择")
    
    def _delete_all_accounts(self, accounts):
        """删除所有账号"""
        sender.reply("=====危险操作=====\n⚠️ 即将删除所有绑定的账号\n此操作不可恢复！\n确认删除? (Y/N)\n==================")
        
        if confirm_operation():
            try:
                for account in accounts:
                    env_id = self.ql.get_env_id(account)
                    if env_id:
                        self.ql.delete_env(env_id)
                    middleware.bucketDel('dd_dx_token', account)
                    middleware.bucketDel('dd_dx_auth', account)
                
                middleware.bucketDel('dd_dx_user', userid)
                sender.reply("=====删除完成=====\n✅ 已删除所有账号信息\n💡 如需重新使用，请重新绑定账号\n==================")
            except Exception as e:
                sender.reply(f"删除失败: {str(e)}")
        else:
            sender.reply("✅ 已取消删除")
    
    def _single_account_operation(self, account):
        """单账号操作"""
        auth_status, auth_time = check_auth_status(account)
        menu = f"=====账号操作菜单=====\n📱 选中账号: {mask_phone(account)}\n🔐 授权状态: {auth_status}\n📅 到期时间: {auth_time}\n[1] 授权续费\n[2] 删除账号\n[3] 查询信息\n选择操作(输入数字):\n=================="
        sender.reply(menu)
        
        operation = sender.input(120000, 1, False)
        if not operation:
            return
        
        if operation == '1':
            self._authorize_single_account(account)
        elif operation == '2':
            self._delete_single_account(account)
        elif operation == '3':
            self._query_single_account(account)
        else:
            sender.reply("❌ 无效的操作选项")
    
    def _authorize_single_account(self, account):
        """单账号授权"""
        sender.reply(f"=====账号授权=====\n📱 授权账号: {mask_phone(account)}\n请输入授权月数(1-12):\n==================")
        months_input = sender.input(120000, 1, False)
        if not months_input:
            return
        
        months = validate_input(months_input, 12, "月数")
        result = self.payment.process_payment(months, 1, account)
        
        if result:
            new_expiry, amount, time_info, pay_type = result
            middleware.bucketSet('dd_dx_auth', account, new_expiry)
            token = middleware.bucketGet('dd_dx_token', account)
            if token:
                self.ql.add_or_update_env(account, token)
            sender.reply(f"=====授权成功=====\n📱 账号: {mask_phone(account)}\n📅 到期时间: {new_expiry}\n💰 支付方式: {pay_type}\n==================")
    
    def _delete_single_account(self, account):
        """删除单账号"""
        sender.reply(f"=====删除账号=====\n⚠️ 即将删除账号: {mask_phone(account)}\n此操作不可恢复！\n确认删除? (Y/N)\n==================")
        
        if confirm_operation():
            try:
                env_id = self.ql.get_env_id(account)
                if env_id:
                    self.ql.delete_env(env_id)
                
                middleware.bucketDel('dd_dx_token', account)
                middleware.bucketDel('dd_dx_auth', account)
                
                accounts = parse_accounts(uservalue)
                accounts.remove(account)
                if accounts:
                    middleware.bucketSet('dd_dx_user', userid, str(accounts))
                else:
                    middleware.bucketDel('dd_dx_user', userid)
                
                sender.reply(f"=====删除成功=====\n✅ 已删除账号: {mask_phone(account)}\n==================")
            except Exception as e:
                sender.reply(f"删除失败: {str(e)}")
        else:
            sender.reply("✅ 已取消删除")
    
    def _query_single_account(self, account):
        """查询单账号"""
        auth_status, auth_time = check_auth_status(account)
        if auth_status != "✅ 已授权":
            sender.reply(f"=====账号未授权=====\n📱 账号: {mask_phone(account)}\n🔐 授权: {auth_status}\n⏰ 到期: {auth_time}\n⚠️ 该账号未授权或已过期\n💡 发送 电信管理 进行授权\n==================")
            return
        
        token = middleware.bucketGet('dd_dx_token', account)
        if not token:
            sender.reply("❌ 账号信息不完整")
            return
        
        try:
            phone, password = token.split('#')
            
            # 显示查询选项
            sender.reply(f"""
=====账号查询选项=====
📱 账号: {mask_phone(account)}
🔐 授权状态: ✅ 已授权
⏰ 到期时间: {auth_time}

🔍 查询类型:
  [1] 基础信息查询
  [2] 本月话费抢购查询
  [3] 517活动查询

💡 请选择查询类型:
==================""")

            query_choice = sender.input(60000, 1, False)
            if not query_choice:
                sender.reply("⏰ 操作超时")
                return
            
            if query_choice == '1':
                # 基础信息查询
                result = self.api.query_account_info(phone, password)
                
                if result["status"] == "success":
                    today_sign = "✅" if result.get('today_signed') else "❌"
                    pet_level = result.get('pet_level', 0)
                    pet_progress = result.get('pet_progress', 0)
                    
                    info_msg = f"""
=====基础信息查询结果=====
📱 账号: {mask_phone(account)}
🔐 授权状态: ✅ 已授权
⏰ 到期时间: {auth_time}

📊 账号数据:
   🪙 金豆数量: {result.get('coin', 0)}
   📅 本月签到: {result.get('sign_days', 0)}天
   🎯 今日签到: {today_sign}
   🐾 宠物等级: Lv.{pet_level}
   📈 升级进度: {result.get('pet_growth', 0)}/{result.get('pet_full_growth', 0)} ({pet_progress}%)
=================="""
                else:
                    info_msg = f"""
=====查询失败=====
📱 账号: {mask_phone(account)}
🔐 授权: ✅ 已授权
⏰ 到期: {auth_time}
❌ 错误: {result.get('message', '未知错误')}
💡 请检查账号状态或重新绑定
=================="""
                sender.reply(info_msg)
                
            elif query_choice == '2':
                # 话费抢购记录查询
                result = self._query_single_payment_record(phone, password)
                
                if result["status"] == "success":
                    data = result["data"]
                    stats = data["stats"]
                    
                    # 发送详细结果
                    detail_msg = f"""
=====本月话费抢购查询结果=====
📱 账号: {mask_phone(account)}
🔐 授权状态: ✅ 已授权
⏰ 到期时间: {auth_time}

💰 话费统计:
   🪙 金豆抢兑: {stats['total_coin']:.2f}元 ({stats['coin_count']}次)
   🎁 等级权益: {stats['total_rights']:.2f}元 ({stats['rights_count']}次)
   🎯 抽奖获得: {stats['total_prize']:.2f}元 ({stats['prize_count']}次)
   🌟 星播客: {stats.get('total_xbk', 0):.2f}元 ({stats.get('xbk_count', 0)}次)
   📊 总计: {stats['total_amount']:.2f}元 ({stats['total_count']}次)"""
                    
                    # 如果有详细记录，显示最近的几条
                    if stats['total_count'] > 0:
                        detail_msg += "\n\n📋 本月记录:"
                        all_records = []
                        all_records.extend(data['coin_payments'])
                        all_records.extend(data['rights_payments'])
                        all_records.extend(data['prize_payments'])
                        all_records.extend(data.get('xbk_payments', []))
                        
                        # 按日期排序，显示最近的5条
                        all_records.sort(key=lambda x: x['date'], reverse=True)
                        for j, record in enumerate(all_records[:5], 1):
                            date_str = record['date'][:10] if record['date'] else '未知'
                            detail_msg += f"\n   {j}. {date_str} {record['title']} ({record['amount']:.2f}元)"
                    
                    detail_msg += "\n=================="
                    sender.reply(detail_msg)
                    
                else:
                    sender.reply(f"""
=====话费抢购查询失败=====
📱 账号: {mask_phone(account)}
🔐 授权: ✅ 已授权
⏰ 到期: {auth_time}
❌ 错误: {result.get('message', '未知错误')}
==================""")
            elif query_choice == '3':
                # 517活动查询
                sender.reply(f"=====517活动查询中=====\n📱 账号: {mask_phone(account)}\n⏳ 正在查询517活动状态...\n==================")
                result = query_517_activity_status(phone, password, self.api)

                if result["status"] == "success":
                    # 任务状态
                    task_info = ""
                    if result.get("task_list"):
                        task_info = f"\n📋 任务状态: 已完成{result['finished_count']}个 / 未完成{result['unfinished_count']}个"
                        for task in result["task_list"]:
                            status_icon = "✅" if task["finished"] else "❌"
                            task_info += f"\n   {status_icon} {task['name']} ({task['progress']})"
                    else:
                        task_info = "\n📋 任务状态: 暂无任务数据"

                    # 卡片状态
                    collection = result.get("collection", {})
                    card_info = "\n\n🃏 卡片收集:"
                    for card in collection.get("cards", []):
                        count = card.get("availableCount", 0)
                        icon = "✅" if count > 0 else "❌"
                        card_info += f"\n   {icon} {card['pieceName']} x{count}"

                    missing = collection.get("missing", [])
                    if missing:
                        card_info += f"\n   ⚠️ 缺少: {'、'.join(missing)}"
                    else:
                        card_info += "\n   🎉 已集齐所有卡片！"

                    # 抽奖和合成
                    extra_info = f"\n\n🎰 可用抽奖次数: {result.get('total_chance_count', 0)}"
                    if result.get("has_composite"):
                        extra_info += "\n🏆 合成状态: ✅ 已完成合成"
                    else:
                        if collection.get("is_all_collected"):
                            extra_info += "\n🏆 合成状态: 🟡 卡片已集齐，可合成"
                        else:
                            extra_info += "\n🏆 合成状态: ❌ 未合成（卡片未集齐）"

                    info_msg = f"""=====517活动查询结果=====
📱 账号: {mask_phone(account)}
🔐 授权状态: ✅ 已授权
⏰ 到期时间: {auth_time}
{task_info}{card_info}{extra_info}
=================="""
                    sender.reply(info_msg)
                else:
                    sender.reply(f"""=====517活动查询失败=====
📱 账号: {mask_phone(account)}
❌ 错误: {result.get('message', '未知错误')}
==================""")
            else:
                sender.reply("❌ 无效的选择")
                return
        except Exception as e:
            sender.reply(f"查询出错: {str(e)}")

    def query_accounts(self):
        """账号查询"""
        accounts = parse_accounts(uservalue)
        if not accounts:
            sender.reply(format_msg('no_accounts', cmd='电信登录'))
            return
        
        menu_items = ["=====电信查询=====", "🔍 快速选项:", "  [0] 查询全部账号", "  [9999] 批量快速查询", "  [9998] 本月话费抢购查询", "  [9997] 517活动查询", "", "📱 单独查询:"]
        
        for i, account in enumerate(accounts, 1):
            auth_status, _ = check_auth_status(account)
            status_icon = "✅" if auth_status == "✅ 已授权" else "⚠️" if "未授权" in auth_status else "❌"
            menu_items.append(f"  [{i}] {mask_phone(account)} {status_icon}")
        
        menu_items.extend(["", "💡 回复数字选择查询方式", "💡 回复'q'退出操作", "=================="])
        sender.reply("\n".join(menu_items))
        
        choice = sender.input(120000, 1, False)
        if not choice or choice.lower() == 'q':
            sender.reply('✅ 已退出查询')
            return
        
        if choice == '0':
            self._query_all_accounts(accounts)
        elif choice == '9999':
            self._batch_query_accounts(accounts)
        elif choice == '9998':
            self._query_payment_records(accounts)
        elif choice == '9997':
            self._query_517_activity(accounts)
        else:
            try:
                index = int(choice) - 1
                if 0 <= index < len(accounts):
                    self._query_single_account(accounts[index])
                else:
                    sender.reply("❌ 无效的账号编号")
            except ValueError:
                sender.reply("❌ 请输入有效的数字")
    
    def _query_all_accounts(self, accounts):
        """查询所有账号"""
        total_coin = 0
        for i, account in enumerate(accounts, 1):
            auth_status, auth_time = check_auth_status(account)
            
            if auth_status == "✅ 已授权":
                token = middleware.bucketGet('dd_dx_token', account)
                if token:
                    try:
                        phone, password = token.split('#')
                        result = self.api.query_account_info(phone, password)
                        
                        if result["status"] == "success":
                            coin = result.get('coin', 0)
                            total_coin += coin
                            today_sign = "✅" if result.get('today_signed') else "❌"
                            
                            msg = format_msg('query_result', 
                                           phone=mask_phone(account), auth=auth_status, 
                                           coin=coin, days=result.get('sign_days', 0), today=today_sign)
                        else:
                            msg = f"=====账号{i}查询失败=====\n📱 账号: {mask_phone(account)}\n❌ 错误: {result.get('message')}\n=================="
                    except Exception as e:
                        msg = f"=====账号{i}查询异常=====\n📱 账号: {mask_phone(account)}\n❌ 异常: {str(e)}\n=================="
                else:
                    msg = f"=====账号{i}信息缺失=====\n📱 账号: {mask_phone(account)}\n❌ 账号信息不完整\n=================="
            else:
                msg = f"=====账号{i}未授权=====\n📱 账号: {mask_phone(account)}\n🔐 授权: {auth_status}\n💡 需要先进行授权\n=================="
            
            sender.reply(msg)
            time.sleep(1)  # 每个账号查询间隔1秒，确保数据准确性
    
    def _batch_query_accounts(self, accounts):
        """批量快速查询"""
        def query_single(account):
            auth_status, auth_time = check_auth_status(account)
            if auth_status != "✅ 已授权":
                return {'account': mask_phone(account), 'status': 'unauthorized', 'auth_status': auth_status, 'auth_time': auth_time}
            
            token = middleware.bucketGet('dd_dx_token', account)
            if not token:
                return {'account': mask_phone(account), 'status': 'no_token', 'auth_status': auth_status, 'auth_time': auth_time}
            
            try:
                phone, password = token.split('#')
                result = self.api.query_account_info(phone, password)
                
                if result["status"] == "success":
                    return {
                        'account': mask_phone(account), 'status': 'success', 'coin': result.get('coin', 0),
                        'sign_days': result.get('sign_days', 0), 'today_signed': result.get('today_signed', False),
                        'pet_level': result.get('pet_level', 0), 'auth_status': auth_status, 'auth_time': auth_time
                    }
                else:
                    return {'account': mask_phone(account), 'status': 'error', 'message': result.get('message'), 'auth_status': auth_status, 'auth_time': auth_time}
            except Exception as e:
                return {'account': mask_phone(account), 'status': 'exception', 'message': str(e), 'auth_status': auth_status, 'auth_time': auth_time}
        
        results = []
        # 为了确保数据准确性，批量查询使用顺序执行，每个账号间隔1秒
        for account in accounts:
            result = query_single(account)
            results.append(result)
            time.sleep(1)  # 每个账号查询间隔1秒，确保数据准确性
        
        total_coin = sum(r['coin'] for r in results if r['status'] == 'success')
        success_count = len([r for r in results if r['status'] == 'success'])
        
        batch_result = ["=====批量查询结果====="]
        
        # 分类显示结果
        success_results = [r for r in results if r['status'] == 'success']
        failed_results = [r for r in results if r['status'] != 'success']
        
        # 显示成功的账号
        if success_results:
            batch_result.append("✅ 查询成功:")
            for result in success_results:
                today_sign = "✅" if result.get('today_signed') else "❌"
                batch_result.append(f"📱 {result['account']}")
                batch_result.append(f"   💰 金豆:{result['coin']} | 📅 签到:{result['sign_days']}天 | 🎯 今日:{today_sign}")
                batch_result.append(f"   🐾 宠物:Lv.{result.get('pet_level', 0)} | ⏰ 到期:{result['auth_time']}")
                batch_result.append("")
        
        # 显示失败的账号
        if failed_results:
            batch_result.append("❌ 查询失败:")
            for result in failed_results:
                reason = "未授权" if result['status'] == 'unauthorized' else "信息缺失" if result['status'] == 'no_token' else result.get('message', '查询失败')
                batch_result.append(f"📱 {result['account']} - {reason}")
            batch_result.append("")
        
        # 汇总信息
        batch_result.extend([
            "📊 汇总统计:",
            f"   ✅ 成功: {success_count}个账号",
            f"   ❌ 失败: {len(failed_results)}个账号", 
            f"   🪙 总金豆: {total_coin}",
            "=================="
        ])
        sender.reply("\n".join(batch_result))
    
    def _query_517_activity(self, accounts):
        """批量查询517活动状态"""
        sender.reply("=====517活动批量查询=====\n⏳ 正在查询所有账号的517活动状态...\n==================")

        for i, account in enumerate(accounts, 1):
            auth_status, auth_time = check_auth_status(account)

            if auth_status != "✅ 已授权":
                sender.reply(f"=====账号{i}未授权=====\n📱 账号: {mask_phone(account)}\n🔐 授权: {auth_status}\n💡 需要先进行授权\n==================")
                continue

            token = middleware.bucketGet('dd_dx_token', account)
            if not token:
                sender.reply(f"=====账号{i}信息缺失=====\n📱 账号: {mask_phone(account)}\n❌ 账号信息不完整\n==================")
                continue

            try:
                phone, password = token.split('#')
                result = query_517_activity_status(phone, password, self.api)

                if result["status"] == "success":
                    collection = result.get("collection", {})
                    missing = collection.get("missing", [])

                    # 卡片摘要
                    card_parts = []
                    for card in collection.get("cards", []):
                        card_parts.append(f"{card['pieceName']}x{card.get('availableCount', 0)}")
                    card_summary = "、".join(card_parts) if card_parts else "无数据"

                    # 合成状态
                    if result.get("has_composite"):
                        composite_status = "✅ 已合成"
                    elif collection.get("is_all_collected"):
                        composite_status = "🟡 可合成"
                    else:
                        composite_status = "❌ 未集齐"

                    detail_msg = f"""=====账号{i} 517活动状态=====
📱 账号: {mask_phone(account)}
📋 任务: 已完成{result['finished_count']}个 / 未完成{result['unfinished_count']}个
🎰 抽奖次数: {result.get('total_chance_count', 0)}
🃏 卡片: {card_summary}
{"⚠️ 缺少: " + "、".join(missing) if missing else "🎉 已集齐！"}
🏆 合成: {composite_status}
=================="""
                    sender.reply(detail_msg)
                else:
                    sender.reply(f"=====账号{i} 517查询失败=====\n📱 账号: {mask_phone(account)}\n❌ 错误: {result.get('message', '未知错误')}\n==================")
            except Exception as e:
                sender.reply(f"=====账号{i} 517查询异常=====\n📱 账号: {mask_phone(account)}\n❌ 异常: {str(e)}\n==================")

            time.sleep(1)

    def _query_payment_records(self, accounts):
        """查询话费抢购记录"""
        total_stats = {
            'total_amount': 0,
            'total_count': 0,
            'accounts': []
        }
        
        for i, account in enumerate(accounts, 1):
            auth_status, auth_time = check_auth_status(account)
            
            if auth_status == "✅ 已授权":
                token = middleware.bucketGet('dd_dx_token', account)
                if token:
                    try:
                        phone, password = token.split('#')
                        result = self._query_single_payment_record(phone, password)
                        
                        if result["status"] == "success":
                            data = result["data"]
                            stats = data["stats"]
                            
                            total_stats['total_amount'] += stats['total_amount']
                            total_stats['total_count'] += stats['total_count']
                            
                            account_result = {
                                'mobile': mask_phone(account),
                                'auth_status': auth_status,
                                'auth_time': auth_time,
                                'stats': stats,
                                'records': data
                            }
                            total_stats['accounts'].append(account_result)
                            
                            # 发送单个账号的详细结果
                            detail_msg = f"""
=====账号{i}本月话费抢购记录=====
📱 账号: {mask_phone(account)}
🔐 授权: {auth_status} | ⏰ 到期: {auth_time}

💰 话费统计:
   🪙 金豆抢兑: {stats['total_coin']:.2f}元 ({stats['coin_count']}次)
   🎁 等级权益: {stats['total_rights']:.2f}元 ({stats['rights_count']}次)
   🎯 抽奖获得: {stats['total_prize']:.2f}元 ({stats['prize_count']}次)
   🌟 星播客: {stats.get('total_xbk', 0):.2f}元 ({stats.get('xbk_count', 0)}次)
   📊 总计: {stats['total_amount']:.2f}元 ({stats['total_count']}次)"""
                            
                            # 如果有详细记录，显示最近的几条
                            if stats['total_count'] > 0:
                                detail_msg += "\n\n📋 最近记录:"
                                all_records = []
                                all_records.extend(data['coin_payments'])
                                all_records.extend(data['rights_payments'])
                                all_records.extend(data['prize_payments'])
                                all_records.extend(data.get('xbk_payments', []))
                                
                                # 按日期排序，显示最近的5条
                                all_records.sort(key=lambda x: x['date'], reverse=True)
                                for j, record in enumerate(all_records[:5], 1):
                                    date_str = record['date'][:10] if record['date'] else '未知'
                                    detail_msg += f"\n   {j}. {date_str} {record['title']} ({record['amount']:.2f}元)"
                            
                            detail_msg += "\n=================="
                            sender.reply(detail_msg)
                            
                        else:
                            sender.reply(f"""
=====账号{i}查询失败=====
📱 账号: {mask_phone(account)}
🔐 授权: {auth_status} | ⏰ 到期: {auth_time}
❌ 错误: {result.get('message', '未知错误')}
==================""")
                            
                    except Exception as e:
                        sender.reply(f"""
=====账号{i}查询异常=====
📱 账号: {mask_phone(account)}
🔐 授权: {auth_status} | ⏰ 到期: {auth_time}
❌ 异常: {str(e)}
==================""")
                else:
                    sender.reply(f"""
=====账号{i}信息缺失=====
📱 账号: {mask_phone(account)}
🔐 授权: {auth_status} | ⏰ 到期: {auth_time}
❌ 账号信息不完整
==================""")
            else:
                sender.reply(f"""
=====账号{i}未授权=====
📱 账号: {mask_phone(account)}
🔐 授权: {auth_status} | ⏰ 到期: {auth_time}
💡 需要先进行授权
==================""")
            
            time.sleep(1)  # 每个账号查询间隔1秒，确保数据准确性
        
        # 发送汇总统计
        if total_stats['accounts']:
            summary_msg = f"""
=====本月话费抢购汇总=====
📊 查询账号: {len(total_stats['accounts'])}个
💰 总金额: {total_stats['total_amount']:.2f}元
📈 总次数: {total_stats['total_count']}次

📱 账号明细:"""
            
            for account in total_stats['accounts']:
                summary_msg += f"""
   {account['mobile']}: {account['stats']['total_amount']:.2f}元 ({account['stats']['total_count']}次)"""
            
            summary_msg += "\n=================="
            sender.reply(summary_msg)
        else:
            sender.reply("❌ 没有找到有效的话费抢购记录")
    
    def _query_single_payment_record(self, phone, password):
        """查询单个账号的话费抢购记录"""
        try:
            # 登录获取token
            login_result = self.api.login(phone, password)
            if not login_result:
                return {"status": "error", "message": "登录失败"}
            
            # 获取ticket
            ticket = self.api.get_ticket(phone, login_result['userId'], login_result['token'])
            if not ticket:
                return {"status": "error", "message": "获取ticket失败"}
            
            # 登录金豆商城
            url = 'https://wappark.189.cn/jt-sign/ssoHomLoginForBill'
            try:
                res = self.api.session.get(url, params={'ticket': ticket})
                res_data = res.json()
                accId = res_data.get('accId')
                sign = res_data.get('sign')
                
                if not accId:
                    return {"status": "error", "message": "获取accId失败"}
                
                # 查询各种记录
                coin_records = self._get_coin_mall_records(accId)
                rights_records = self._get_rights_records(accId, sign)
                prize_records = self._get_prize_records(accId, sign)
                
                # 查询星播客记录
                xbk_records = []
                try:
                    usercode = self.api.get_xbk_usercode(phone, ticket)
                    if usercode:
                        usertoken = self.api.get_xbk_usertoken(phone, usercode)
                        if usertoken:
                            xbk_records = self.api.get_xbk_win_list(phone, usertoken)
                except Exception as e:
                    print(f"查询星播客记录失败: {e}")
                
                # 统计话费记录
                payment_stats = self._analyze_payment_records(coin_records, rights_records, prize_records, xbk_records)
                
                return {
                    "status": "success",
                    "data": payment_stats
                }
                
            except Exception as e:
                return {"status": "error", "message": f"查询记录失败: {str(e)}"}
                
        except Exception as e:
            return {"status": "error", "message": f"查询异常: {str(e)}"}
    
    def _get_coin_mall_records(self, accId):
        """获取金豆商城兑换记录"""
        try:
            url = 'https://wappark.189.cn/jt-sign/paradise/getCoinMallExchangetRecords'
            params = {'accId': accId, 'page': 0, 'size': 150}
            data = encrypt_para(json.dumps(params))
            
            res = self.api.session.post(url, data=json.dumps({'para': data}))
            return res.json().get('data', [])
        except Exception:
            return []
    
    def _get_rights_records(self, accId, sign=None):
        """获取权益兑换记录"""
        all_rights_records = []
        try:
            url = 'https://wappark.189.cn/jt-sign/paradise/getRightsExchangetRecords'
            params = {'accId': accId, 'page': 0, 'size': 100}
            data = encrypt_para(json.dumps(params))

            headers = {
                'Content-Type': 'application/json;charset=utf-8',
                'Referer': f'https://wappark.189.cn/resources/dist/recordsNew.html?ticket=$ticket$&type=2'
            }
            if sign:
                headers['sign'] = sign

            res = self.api.session.post(url, data=json.dumps({'para': data}), headers=headers)
            res_json = res.json()
            if res_json.get('resoultCode') == '0' or res_json.get('code') == 0:
                all_rights_records.extend(res_json.get('data', []))
        except Exception:
            pass

        # 从抽奖记录中提取等级权益记录
        try:
            prize_records = self._get_prize_records(accId, sign)
            for record in prize_records:
                win_title = record.get("winTitle", "")
                if "等级" in win_title or "LV" in win_title or "等级权益" in win_title:
                    all_rights_records.append(record)
        except Exception:
            pass

        return all_rights_records
    
    def _get_prize_records(self, accId, sign):
        """获取抽奖记录"""
        try:
            self.api.session.headers['sign'] = sign
            url = 'https://wappark.189.cn/jt-sign/webSign/getPrizeRecords'
            params = {'phone': accId, 'page': 0, 'size': 150}
            data = encrypt_para(json.dumps(params))
            
            res = self.api.session.post(url, data=json.dumps({'para': data}))
            return res.json().get('data', [])
        except Exception:
            return []
    
    def _analyze_payment_records(self, coin_records, rights_records, prize_records, xbk_records=None):
        """分析话费记录"""
        def extract_amount(title):
            """提取话费金额"""
            if "2026LV" in title and "等级" in title:
                match = re.search(r'(\d+(?:\.\d+)?)元话费', title)
                return float(match.group(1)) if match else 0.0
            elif "等级权益" in title or "抽中" in title:
                match = re.search(r'(\d+(?:\.\d+)?)元话费', title)
                if match:
                    return float(match.group(1))
                match = re.search(r'(\d+(?:\.\d+)?)', title)
                return float(match.group(0)) if match else 0.0
            else:
                match = re.search(r'(\d+(?:\.\d+)?)元话费', title)
                return float(match.group(1)) if match else 0.0
        
        def is_current_month(date_str):
            """检查日期是否为当前月份"""
            try:
                if not date_str:
                    return False
                # 提取日期部分（前10个字符）
                date_part = date_str[:10] if len(date_str) >= 10 else date_str
                date_formats = ['%Y-%m-%d', '%Y/%m/%d']
                parsed_date = None
                
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_part, fmt)
                        break
                    except ValueError:
                        continue
                
                if not parsed_date:
                    return False
                
                current_date = datetime.now()
                return parsed_date.year == current_date.year and parsed_date.month == current_date.month
            except Exception:
                return False
        
        # 统计各类话费记录（只统计当月）
        coin_payments = []
        rights_payments = []
        prize_payments = []
        xbk_payments = []
        
        # 处理金豆兑换记录
        for record in coin_records:
            title = record.get('title', '')
            date_str = record.get('createdDate', '')
            if "话费" in title and is_current_month(date_str):
                amount = extract_amount(title)
                if amount > 0:
                    coin_payments.append({
                        'title': title,
                        'amount': amount,
                        'date': date_str,
                        'type': '金豆抢兑'
                    })
        
        # 处理权益兑换记录（可能来自权益接口或抽奖接口，字段名不同）
        for record in rights_records:
            title = record.get('title', '') or record.get('winTitle', '')
            date_str = record.get('createdDate', '')
            if "话费" in title and is_current_month(date_str):
                amount = extract_amount(title)
                if amount > 0:
                    rights_payments.append({
                        'title': title,
                        'amount': amount,
                        'date': date_str,
                        'type': '等级权益'
                    })
        
        # 处理抽奖记录（排除已归类为等级权益的记录，避免重复计算）
        for record in prize_records:
            title = record.get('winTitle', '')
            date_str = record.get('createdDate', '')
            # 跳过已在等级权益中统计的记录
            if "等级" in title or "LV" in title or "等级权益" in title:
                continue
            if "话费" in title and is_current_month(date_str):
                amount = extract_amount(title)
                if amount > 0:
                    prize_payments.append({
                        'title': title,
                        'amount': amount,
                        'date': date_str,
                        'type': '抽奖'
                    })
        
        # 处理星播客记录
        if xbk_records:
            for record in xbk_records:
                title = record.get('title', '')
                date_str = record.get('win_time', '')
                if "话费" in title and is_current_month(date_str):
                    amount = extract_amount(title)
                    if amount > 0:
                        xbk_payments.append({
                            'title': title,
                            'amount': amount,
                            'date': date_str,
                            'type': '星播客'
                        })
        
        # 计算统计信息
        total_coin = sum(p['amount'] for p in coin_payments)
        total_rights = sum(p['amount'] for p in rights_payments)
        total_prize = sum(p['amount'] for p in prize_payments)
        total_xbk = sum(p['amount'] for p in xbk_payments)
        total_amount = total_coin + total_rights + total_prize + total_xbk
        
        return {
            'coin_payments': coin_payments,
            'rights_payments': rights_payments,
            'prize_payments': prize_payments,
            'xbk_payments': xbk_payments,
            'stats': {
                'total_coin': total_coin,
                'total_rights': total_rights,
                'total_prize': total_prize,
                'total_xbk': total_xbk,
                'total_amount': total_amount,
                'coin_count': len(coin_payments),
                'rights_count': len(rights_payments),
                'prize_count': len(prize_payments),
                'xbk_count': len(xbk_payments),
                'total_count': len(coin_payments) + len(rights_payments) + len(prize_payments) + len(xbk_payments)
            }
        }

# 管理员功能
def admin_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)
    
    auth_menu = """=====电信授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 更新变量
[4] 清理过期账号
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(auth_menu)
    xz = sender.input(60000, 1, False)
    
    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出授权管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('dd_dx_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的电信账号")
            return
            
        sender.reply("""=====请输入授权天数=====
------------------
回复数字设置天数
回复"q"退出操作
==================""")
        
        sjts = sender.input(60000, 1, False)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("✅ 已取消授权")
            return
        elif sjts is None:
            sender.reply("⏰ 操作超时,已退出")
            return
        
        try:
            sjts = int(sjts)  # 确保转换为整数
        except:
            sender.reply("❌ 天数必须是数字!")
            return
            
        success_count = 0
        fail_count = 0
        
        # 在循环外创建QingLongManager实例，避免重复连接
        try:
            ql = QingLongManager()
        except Exception as e:
            sender.reply(f"❌ 连接青龙失败")
            return
        
        for user in users:
            accountlist = middleware.bucketGet('dd_dx_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            accounts = parse_accounts(accountlist)
            # 去重账号列表
            accounts = list(dict.fromkeys(accounts))
            
            for account in accounts:
                try:
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    accountVip = middleware.bucketGet('dd_dx_auth', account)
                    token = middleware.bucketGet('dd_dx_token', account)
                    
                    if not token:
                        fail_count += 1
                        continue
                        
                    if accountVip and accountVip > dqsj:
                        sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                        new_sqsj = sqsj + timedelta(days=int(sjts))  # 确保使用整数
                    else:
                        new_sqsj = datetime.now() + timedelta(days=int(sjts))  # 确保使用整数
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    
                    # 更新授权时间
                    middleware.bucketSet('dd_dx_auth', account, new_sqsj)
                    
                    # 更新青龙变量
                    ql.add_or_update_env(account, token)
                    success_count += 1
                except Exception as e:
                    fail_count += 1
                    print(f"授权账号 {account} 失败: {str(e)}")
                    
        result_msg = f"""=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
        sender.reply(result_msg)
        
    elif xz == '2':
        # 单独授权用户
        user_guide = """======账号授权======
请输入需要授权的用户ID
(发送myuid可获取ID)
------------------
回复"q"退出操作
=================="""
        sender.reply(user_guide)
        
        myuid = sender.input(60000, 1, False)
        if myuid == 'q' or myuid == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif myuid is None:
            sender.reply("⏰ 操作超时,已退出")
            return
            
        accountlist = middleware.bucketGet('dd_dx_user', myuid)
        if not accountlist or accountlist == '' or accountlist == '{}':
            sender.reply(f"""=====查询结果=====
❌ 未找到 {myuid} 的账号信息
==================""")
            return
            
        try:
            accounts = parse_accounts(accountlist)
            if not accounts:
                sender.reply(f"""=====数据错误=====
❌ 账号数据格式异常
==================""")
                return
                
            # 使用字典键去重并保持顺序
            accounts = list(dict.fromkeys(accounts))
            
            account_list = """=======账号列表=====
[0] 授权所有账号
------------------"""
            
            for i, account in enumerate(accounts, 1):
                accountVip = middleware.bucketGet('dd_dx_auth', account)
                vip_status = accountVip if accountVip else '未授权'
                account_list += f"\n[{i}] 账号: {mask_phone(account)}\n    授权至: {vip_status}\n------------------"
                
            account_list += "\n回复数字选择账号\n回复'q'退出\n=================="
            sender.reply(account_list)
            
            xz = sender.input(60000, 1, False)
            if xz == 'q' or xz == 'Q':
                sender.reply("✅ 已退出授权")
                return
            elif xz is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                xz = int(xz)
                if xz < 0 or (xz > len(accounts) and xz != 0):
                    sender.reply(f"""=====输入错误=====
❌ 请输入 0-{len(accounts)} 之间的数字
==================""")
                    return
            except ValueError:
                sender.reply("""=====输入错误=====
❌ 请输入正确的数字
==================""")
                return
                
            auth_guide = """=====设置授权天数=====
请输入要授权的天数
------------------
回复数字设置天数
回复"q"退出操作
=================="""
            sender.reply(auth_guide)
            
            sjts = sender.input(60000, 1, False)
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
                    
                success_count = 0
                fail_count = 0
                
                # 处理选择授权所有账号的情况
                if xz == 0:
                    target_accounts = accounts
                else:
                    target_accounts = [accounts[xz-1]]
                    
                # 在循环外创建QingLongManager实例
                try:
                    ql = QingLongManager()
                except Exception as e:
                    sender.reply(f"❌ 连接青龙失败")
                    return
                
                for account in target_accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('dd_dx_auth', account)
                        token = middleware.bucketGet('dd_dx_token', account)
                        
                        if not token:
                            fail_count += 1
                            continue
                            
                        if accountVip and accountVip > dqsj:
                            sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                            new_sqsj = sqsj + timedelta(days=sjts)
                        else:
                            new_sqsj = datetime.now() + timedelta(days=sjts)
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        # 更新授权时间
                        middleware.bucketSet('dd_dx_auth', account, new_sqsj)
                        
                        # 更新青龙变量
                        ql.add_or_update_env(account, token)
                        success_count += 1
                    except Exception as e:
                        fail_count += 1
                        print(f"授权账号 {account} 失败: {str(e)}")
                        
                result_msg = f"""=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return
                
        except Exception as e:
            sender.reply(format_msg("系统错误", f"处理账号数据时出错\n错误: {str(e)}"))
            return
    elif xz == '3':
        # 更新变量 - 把已授权用户的变量更新到青龙
        sender.reply("""=====更新变量=====
⏳ 正在扫描已授权账号...
请稍候...
==================""")
        
        users = middleware.bucketAllKeys('dd_dx_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的电信账号")
            return
            
        success_count = 0
        fail_count = 0
        authorized_count = 0
        
        # 在循环外创建QingLongManager实例
        try:
            ql = QingLongManager()
        except Exception as e:
            sender.reply(f"❌ 连接青龙失败")
            return
        
        for user in users:
            accountlist = middleware.bucketGet('dd_dx_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            try:
                accounts = parse_accounts(accountlist)
                if not accounts:
                    continue
                    
                # 去重账号列表
                accounts = list(dict.fromkeys(accounts))
                
                for account in accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('dd_dx_auth', account)
                        token = middleware.bucketGet('dd_dx_token', account)
                        
                        # 检查是否已授权且未过期
                        if accountVip and accountVip > dqsj and token:
                            authorized_count += 1
                            # 更新青龙变量
                            ql.add_or_update_env(account, token)
                            success_count += 1
                        else:
                            # 未授权或已过期的账号跳过
                            continue
                    except Exception as e:
                        fail_count += 1
                        print(f"更新账号 {account} 变量失败: {str(e)}")
                        continue
            except Exception as e:
                print(f"处理用户 {user} 数据失败: {str(e)}")
                continue
                    
        result_msg = f"""=====变量更新完成=====
🔍 扫描用户: {len(users)}个
✅ 已授权账号: {authorized_count}个
📤 更新成功: {success_count}个
❌ 更新失败: {fail_count}个
=================="""
        sender.reply(result_msg)
        
    elif xz == '4':
        # 清理过期账号
        users = middleware.bucketAllKeys('dd_dx_user')
        
        if not users:
            sender.reply("❌ 未找到任何绑定的电信账号")
            return
            
        sender.reply(f"""=====开始清理过期账号=====
🔍 共找到: {len(users)}个用户
⏳ 清理中请稍候...
==================""")
        
        cleaned_count = 0
        today = str(datetime.now().date())
        
        # 在循环外创建QingLongManager实例
        try:
            ql = QingLongManager()
        except Exception as e:
            sender.reply(f"❌ 连接青龙失败")
            return
        
        for user in users:
            try:
                accountlist = middleware.bucketGet('dd_dx_user', user)
                if not accountlist or accountlist == '' or accountlist == '{}':
                    continue
                    
                # 解析并去重账号列表
                accounts = parse_accounts(accountlist)
                # 去重
                accounts = list(dict.fromkeys(accounts))
                valid_accounts = []
                
                for account in accounts:
                    accountVip = middleware.bucketGet('dd_dx_auth', account)
                    
                    if not accountVip or accountVip <= today:
                        try:
                            # 删除青龙环境变量
                            env_id = ql.get_env_id(account)
                            if env_id:
                                ql.delete_env(env_id)
                        except Exception as e:
                            print(f"删除账号 {account} 环境变量失败")
                            
                        # 删除授权记录和Token（保留用户绑定）
                        middleware.bucketDel('dd_dx_token', account)
                        middleware.bucketDel('dd_dx_auth', account)
                        cleaned_count += 1
                    else:
                        valid_accounts.append(account)
                
                # 去重有效账号
                valid_accounts = list(dict.fromkeys(valid_accounts))
                
                # 更新用户账号列表
                if valid_accounts:
                    middleware.bucketSet('dd_dx_user', user, str(valid_accounts))
                else:
                    middleware.bucketDel('dd_dx_user', user)
                    
            except Exception as e:
                print(f"处理用户 {user} 时出错: {str(e)}")
                continue
        
        result_msg = f"""=====清理完成=====
✅ 已清理: {cleaned_count}个过期账号
🧹 清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💡 过期账号的绑定信息已保留
💡 用户可重新授权使用
=================="""
        sender.reply(result_msg)
        
    else:
        sender.reply("❌ 输入的选项无效!")
        return

def sync_users():
    """同步已授权用户到面板"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)

    sender.reply("=====电信同步=====\n⏳ 正在同步已授权用户到面板...\n==================")

    users = middleware.bucketAllKeys('dd_dx_user')
    if not users:
        sender.reply("=====同步结果=====\n❌ 未找到任何绑定用户\n==================")
        return

    try:
        ql = QingLongManager()
    except Exception:
        sender.reply("❌ 连接面板失败")
        return

    success_count = 0
    skip_count = 0
    fail_count = 0

    for user in users:
        accountlist = middleware.bucketGet('dd_dx_user', user)
        if not accountlist or accountlist == '' or accountlist == '{}':
            continue

        accounts = parse_accounts(accountlist)
        accounts = list(dict.fromkeys(accounts))

        for account in accounts:
            try:
                dqsj = str(datetime.now().date())
                accountVip = middleware.bucketGet('dd_dx_auth', account)
                token = middleware.bucketGet('dd_dx_token', account)

                if not accountVip or accountVip <= dqsj or not token:
                    skip_count += 1
                    continue

                ql.add_or_update_env(account, token)
                success_count += 1
            except Exception:
                fail_count += 1

    sender.reply(f"=====同步完成=====\n✅ 同步成功: {success_count}个账号\n⏭️ 跳过未授权: {skip_count}个账号\n❌ 同步失败: {fail_count}个账号\n==================")


def show_tutorial():
    """显示教程"""
    tutorial = f"""=====电信插件教程=====

🎯 【基本功能】
• 金豆余额查询  
• 签到天数统计
• 宠物等级查询
• 批量账号操作

1️⃣ 绑定账号: 发送 电信登录
2️⃣ 购买授权: 发送 电信授权  
3️⃣ 管理账号: 发送 电信管理
4️⃣ 查询信息: 发送 电信查询

💡 【注意事项】
• 登录格式: 手机号#密码
• 支持批量操作
• 授权到期自动清理

🆘 【常见问题】
Q: 登录失败？ A: 检查手机号密码
Q: 查询提示过期？ A: 重新绑定账号
=================="""
    sender.reply(tutorial)

def clean_expired():
    """清理过期账号"""
    try:
        ql = QingLongManager()
        users = middleware.bucketAllKeys('dd_dx_user')
        cleaned_count = 0
        today = str(datetime.now().date())
        
        for user in users:
            accountlist = middleware.bucketGet('dd_dx_user', user)
            if not accountlist:
                continue
            
            accounts = parse_accounts(accountlist)
            for account in accounts:
                auth_time = middleware.bucketGet('dd_dx_auth', account)
                if not auth_time or auth_time <= today:
                    env_id = ql.get_env_id(account)
                    if env_id:
                        ql.delete_env(env_id)
                        cleaned_count += 1
        
        sender.reply(f"=====清理完成=====\n✅ 已清理 {cleaned_count} 个过期账号的青龙变量\n==================")
    except Exception as e:
        sender.reply(f"清理失败: {str(e)}")

# 主程序入口
def main():
    manager = TelecomManager()
    message = sender.getMessage()
    imtype = sender.getImtype()
    
    if '登录' in message or '登陆' in message:
        manager.login_account()
    elif '管理' in message:
        if uservalue:
            manager.manage_accounts()
        else:
            sender.reply(format_msg('no_accounts', cmd='电信登录'))
    elif '查询' in message:
        if uservalue:
            manager.query_accounts()
        else:
            sender.reply(format_msg('no_accounts', cmd='电信登录'))
    elif message == '电信清理':
        clean_expired()
    elif message == '电信授权':
        admin_auth()
    elif message == '电信教程':
        show_tutorial()
    elif message == '电信同步':
        sync_users()
    elif imtype == 'fake':
        # 定时任务 - 检测授权过期推送
        users = middleware.bucketAllKeys('dd_dx_user')
        today = str(datetime.now().date())
        for user in users:
            accountlist = middleware.bucketGet('dd_dx_user', user)
            if not accountlist:
                continue
            accounts = parse_accounts(accountlist)
            for account in accounts:
                try:
                    auth_time = middleware.bucketGet('dd_dx_auth', account)
                    phone = account[:3] + '****' + account[7:] if len(account) >= 11 else account
                    if not auth_time or auth_time <= today:
                        push_msg = f"""
=====电信账号通知=====
📱 账号: {phone}
📢 消息: ⏰ 定时检测提醒\n------------------\n❌ 授权已过期\n💡 请及时续费授权
=================="""
                        for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                            try:
                                middleware.push(platform, '', user, '', push_msg)
                            except:
                                pass
                    else:
                        try:
                            expire_date = datetime.strptime(auth_time, '%Y-%m-%d').date()
                            days_left = (expire_date - datetime.now().date()).days
                            if days_left <= 3:
                                push_msg = f"""
=====电信账号通知=====
📱 账号: {phone}
📢 消息: ⏰ 定时检测提醒\n------------------\n⚠️ 授权即将到期\n📅 到期时间: {auth_time}\n⏳ 剩余天数: {days_left}天\n💡 请及时续费授权
=================="""
                                for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                                    try:
                                        middleware.push(platform, '', user, '', push_msg)
                                    except:
                                        pass
                        except:
                            pass
                except:
                    continue
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
