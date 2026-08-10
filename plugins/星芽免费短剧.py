#[title: 星芽免费短剧]
#[language: python]
#[class: 工具类]
#[service: 945227797]
#[disable:false] 禁用开关，true表示禁用，false表示可用
#[admin: false]
#[rule: ^星芽教程$]
#[rule: ^星芽登录$]
#[rule: ^星芽登陆$]
#[rule: ^星芽查询$]
#[rule: ^星芽ck提交$]
#[rule: ^星芽CK提交$]
#[rule: ^星芽管理$]
#[rule: ^星芽授权$]
#[rule: ^星芽刷时长$]
#[cron: 18 8,12,16 * * *] cron定时，支持5位域和6位域
#[priority: 100]
#[platform: qq]
#[author: Jiang0529]
#[open_source: false]
#[icon: https://pp.myapp.com/ma_icon/0/icon_54326748_1755482552/256]
#[version: 2.2]
#[public: true]
#[price: 28.88]
#[description: 星芽免费短剧插件。<br>支持指令：星芽教程、星芽登录、星芽查询、星芽ck提交/星芽CK提交、星芽管理、星芽授权、星芽刷时长。<br>功能包含手机号验证码登录、CK批量导入、账号查询、账号管理、单个/批量授权、单个/批量刷时长，并支持青龙/呆呆面板变量自动同步与失败待补交。<br>2.2版本更新日志：按面板对接模板增加呆呆面板支持，统一完善青龙/呆呆面板变量查询、新增、更新、删除、失败补交逻辑，兼容旧版青龙配置。]


# [param: {"required":true,"key":"ch_xy_config.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"ch_xy_config.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"ch_xy_config.panel_group","bool":false,"placeholder":"例:我的分组","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":false,"key":"ch_xy_config.Qinglong","bool":false,"placeholder":"旧版兼容: http://xxx.xx丨ClientID丨ClientSecret","name":"旧版青龙配置","desc":"兼容旧版配置；新安装建议使用“对接面板类型/对接面板配置”"}]
# [param: {"required":true,"key":"ch_xy_config.osname","bool":false,"placeholder":"必填项,例:ch_xy","name":"面板变量名","desc":"青龙/呆呆面板内星芽短剧的环境变量名，默认 ch_xy"}]
# [param: {"required":true,"key":"ch_xy_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"ch_xy_config.money","bool":false,"placeholder":"必填项,数字","name":"星芽月费","desc":"填写数字，单位元"}]
# [param: {"required":true,"key":"ch_xy_config.jfmoney","bool":false,"placeholder":"必填项,积分配置","name":"星芽积分月费","desc":"填写数字，单位积分，填写非0值后开启积分支付"}]
# [param: {"required":true,"key":"ch_xy_config.jfbl","bool":false,"placeholder":"必填项,积分参数配置","name":"星芽积分桶","desc":"填写积分配置数据桶名，默认对接呆呆积分市场插件"}]
# [param: {"required":true,"key":"ch_xy_config.dl","bool":false,"placeholder":"必填项,代理地址","name":"代理地址","desc":"填写代理api链接(一次一条丨http/https丨txt格式丨白名单验证)，不填为禁用代理（建议填写无限代理池）"}]


import base64
import hashlib
import json
import logging

import requests
from datetime import datetime, timedelta
from decimal import Decimal
import re
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import time
import uuid
import random
import string
import middleware


HEX_DIGITS = '0123456789abcdef'
DEFAULT_REQUEST_TIMEOUT = 10
logger = logging.getLogger(__name__)
PLUGIN_NAMESPACE = 'ch_xy_config'
QLurl, qltoken = None, None
panel_client = None



# 工具函数
def xyauth(plaintext):
    '''AES加密'''
    key = 'B@ecf920Od8A4df7'.encode('utf-8')
    # 创建AES/ECB加密器
    cipher = AES.new(key, AES.MODE_ECB)

    # 将明文转换为字节串并添加PKCS7填充
    plaintext_bytes = plaintext.encode('utf-8')
    padded_plaintext = pad(plaintext_bytes, AES.block_size)

    # 加密数据
    ciphertext = cipher.encrypt(padded_plaintext)

    # 返回Base64编码的密文
    return base64.b64encode(ciphertext).decode('utf-8')


def generate_android_id():
    """随机生成一个Android ID (16位十六进制字符串)"""
    return ''.join(random.choice(HEX_DIGITS) for _ in range(16))


def android_id_to_device_id(android_id):
    """将Android ID转换为设备ID"""
    if not android_id or android_id == "9774d56d68369ce":
        # 无效的Android ID，使用前缀9并生成随机UUID
        return "9" + str(uuid.uuid4()).replace("-", "")
    else:
        # 有效的Android ID，使用前缀2
        return "2" + str(uuid.uuid5(uuid.NAMESPACE_DNS, android_id)).replace("-", "")


def getdid():
    '''
    随机生成安卓id并生成did
    :return: android_id, device_id
    '''
    android_id = generate_android_id()
    device_id = android_id_to_device_id(android_id)
    return android_id, device_id


def mask_phone(phone):
    """手机号脱敏显示"""
    phone = safe_str(phone)
    if len(phone) < 11:
        return phone
    return f'{phone[:3]}****{phone[7:]}'


def mask_phone_list(phones):
    """脱敏展示多个手机号"""
    return '、'.join(mask_phone(phone) for phone in phones)


def phone_digest(phone):
    """生成手机号匹配标识，避免在外部备注中暴露完整手机号"""
    return hashlib.sha256(safe_str(phone).encode('utf-8')).hexdigest()[:12]


def extract_remark_user(remarks):
    """从青龙备注中提取原用户标识，定时更新时避免被 fake 触发用户覆盖"""
    if not remarks or '用户:' not in remarks:
        return ''
    try:
        return remarks.split('用户:')[1].split('丨')[0]
    except Exception:
        return ''


def build_ql_remark(phone, account_vip, owner_user=None, existing_remarks=None):
    owner = owner_user or extract_remark_user(existing_remarks) or user
    return f'星芽:{mask_phone(phone)}丨标识:{phone_digest(phone)}丨用户:{owner}丨授权时间:{account_vip}丨星芽管理'


def remark_matches_phone(remarks, phone):
    """兼容新版哈希标识、旧版明文手机号与脱敏手机号备注"""
    remarks = safe_str(remarks)
    phone = safe_str(phone)
    if not remarks or not phone:
        return False

    digest = phone_digest(phone)
    if f'标识:{digest}' in remarks:
        return True

    # 兼容历史备注：星芽:13800138000 / 星芽:138****8000
    if f'星芽:{phone}' in remarks or f'星芽:{mask_phone(phone)}' in remarks:
        return True

    if '星芽:' not in remarks:
        return False

    try:
        remark_phone = remarks.split('星芽:')[1].split('丨')[0]
        return remark_phone in (phone, mask_phone(phone))
    except Exception:
        return False


def split_accounts(data):
    """将存储的账号字符串拆分为账号列表"""
    if not data:
        return []
    return [item for item in data.split('&') if item]


def safe_str(value):
    """将 None 等空值安全转成字符串，避免 len(None) 等异常"""
    return value or ''


def bind_user_phone(user_id, phone):
    """为用户绑定手机号，自动去重"""
    phones = split_accounts(middleware.bucketGet("ch_xy_phone", user_id))
    if phone not in phones:
        phones.append(phone)
        middleware.bucketSet("ch_xy_phone", user_id, '&'.join(phones))


def unbind_user_phone(user_id, phone):
    """解绑用户手机号"""
    phones = split_accounts(middleware.bucketGet("ch_xy_phone", user_id))
    phones = [item for item in phones if item != phone]
    if phones:
        middleware.bucketSet("ch_xy_phone", user_id, '&'.join(phones))
    else:
        middleware.bucketDel(bucket='ch_xy_phone', key=user_id)

def ValueErrors(value, count, sender_obj=None):
    """验证输入值是否为有效的整数且在合理范围内"""
    try:
        value = int(value)
        if value <= 0 or value > count:
            if sender_obj:
                sender_obj.reply(f"""=======输入无效=====
❌ 请输入 1-{count} 之间的数字
====================""")
            return None
        return value
    except (TypeError, ValueError):
        if sender_obj:
            sender_obj.reply("""=======输入无效=====
❌ 请输入正确的数字
====================""")
        return None



def empower(empowertime, me_as_int):
    """授权时间计算"""
    day = int(me_as_int) * 30
    try:
        if len(empowertime) == 0:
            # 没有授权时间，从今天开始计算
            delayed_date = today_date + timedelta(days=day)
        else:
            # 有授权时间，判断是否已过期
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            if empower_date <= today_date:
                # 已过期，从今天开始计算
                delayed_date = today_date + timedelta(days=day)
            else:
                # 未过期，在现有授权时间基础上累加
                delayed_date = empower_date + timedelta(days=day)

        return str(delayed_date)
    except Exception as e:
        print(f"授权时间计算出错: {str(e)}")
        return str(today_date + timedelta(days=day))



# ============================================================
# 面板对接部分：兼容青龙面板与呆呆面板
# ============================================================

def normalize_panel_type(panel_type_value):
    """统一解析面板类型，返回 qinglong / daidai / ''"""
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    return ''


def panel_type_label(panel_type_value=None):
    panel_type = normalize_panel_type(panel_type_value)
    if panel_type == 'daidai':
        return '呆呆面板'
    if panel_type == 'qinglong':
        return '青龙面板'
    return '对接面板'


def parse_panel_config():
    """读取并校验面板配置；兼容旧版 ch_xy_config.Qinglong 配置"""
    panel_type_raw = middleware.bucketGet(PLUGIN_NAMESPACE, 'panel_type') or ''
    panel_config = safe_str(middleware.bucketGet(PLUGIN_NAMESPACE, 'panel_config')).strip()
    legacy_qinglong = safe_str(middleware.bucketGet(PLUGIN_NAMESPACE, 'Qinglong')).strip()

    panel_type = normalize_panel_type(panel_type_raw)

    # 兼容旧版：未配置 panel_type/panel_config 时，沿用 Qinglong 字段并默认为青龙面板。
    if not panel_config and legacy_qinglong:
        panel_config = legacy_qinglong
        if not panel_type:
            panel_type = 'qinglong'

    # 兼容部分旧配置：只填了 panel_config 但未填 panel_type 时，默认按青龙解析。
    if panel_config and not panel_type:
        panel_type = 'qinglong'

    if not panel_type:
        raise RuntimeError("""=======配置错误=====
❌ 未配置或无法识别对接面板类型
------------------
请在插件配置中填写：
• 对接面板类型：青龙 或 呆呆
• 对接面板配置：Host丨ID丨Secret
====================""")

    if not panel_config:
        if panel_type == 'qinglong':
            tip = "Host丨ClientID丨ClientSecret"
        else:
            tip = "Host丨AppKey丨AppSecret"
        raise RuntimeError(f"""=======配置错误=====
❌ 未配置{panel_type_label(panel_type)}信息
------------------
请在插件配置中填写：
{tip}
====================""")

    parts = [item.strip() for item in panel_config.split('丨')]
    if len(parts) != 3:
        if panel_type == 'qinglong':
            tip = "Host丨ClientID丨ClientSecret"
        else:
            tip = "Host丨AppKey丨AppSecret"
        raise RuntimeError(f"""=======格式错误=====
❌ {panel_type_label(panel_type)}配置格式错误
------------------
当前格式: {panel_config}
正确格式:
{tip}
====================""")

    host, key, secret = parts
    if not all([host, key, secret]):
        raise RuntimeError(f"""=======参数错误=====
❌ {panel_type_label(panel_type)}配置参数不完整
------------------
请确保 Host、ID/Key、Secret 都已填写
====================""")

    if not host.startswith(('http://', 'https://')):
        raise RuntimeError(f"""=======地址错误=====
❌ 面板地址格式错误
------------------
当前地址: {host}
正确格式:
• http://example.com
• https://example.com:5700
====================""")

    panel_group = safe_str(middleware.bucketGet(PLUGIN_NAMESPACE, 'panel_group')).strip()
    return panel_type, host.rstrip('/'), key, secret, panel_group


def get_qinglong_token(host, client_id, client_secret):
    """获取青龙面板 API Token"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        response = requests.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

        result = response.json()
        token = result.get('data', {}).get('token')
        if not token:
            raise RuntimeError(f"返回数据中无 token 字段: {result}")
        return token
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"连接青龙面板失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"获取青龙面板Token失败: {str(e)}")


def get_daidai_token(host, app_key, app_secret):
    """获取呆呆面板 API Token"""
    try:
        url = f'{host}/api/open-api/token'
        response = requests.post(
            url,
            json={"app_key": app_key, "app_secret": app_secret},
            timeout=DEFAULT_REQUEST_TIMEOUT,
        )
        if response.status_code != 200:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

        result = response.json()
        token = result.get('data', {}).get('access_token') or result.get('data', {}).get('token')
        if not token:
            raise RuntimeError(f"返回数据中无 access_token 字段: {result}")
        return token
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"连接呆呆面板失败: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"获取呆呆面板Token失败: {str(e)}")


class PanelClient:
    """青龙/呆呆面板统一环境变量客户端"""

    def __init__(self, host, token, panel_type, panel_group=''):
        self.host = host.rstrip('/')
        self.token = token
        self.panel_type = panel_type
        self.panel_group = panel_group

    @property
    def is_daidai(self):
        return self.panel_type == 'daidai'

    @property
    def label(self):
        return panel_type_label(self.panel_type)

    @property
    def base_url(self):
        if self.is_daidai:
            return f"{self.host}/api/envs"
        return f"{self.host}/open/envs"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }

    @classmethod
    def from_config(cls):
        panel_type, host, key, secret, panel_group = parse_panel_config()
        if panel_type == 'qinglong':
            token = get_qinglong_token(host, key, secret)
        else:
            token = get_daidai_token(host, key, secret)
        return cls(host, token, panel_type, panel_group)

    @staticmethod
    def env_id(env):
        if not isinstance(env, dict):
            return None
        return env.get('id') or env.get('_id') or env.get('env_id')

    @staticmethod
    def response_ok(response, result=None):
        if response.status_code not in (200, 201):
            return False
        if result is None:
            try:
                result = response.json()
            except Exception:
                return True
        if not isinstance(result, dict):
            return True
        code = result.get('code')
        if code in (None, 0, 1, 200, '0', '1', '200', 'ok', 'success'):
            return True
        if result.get('success') is True:
            return True
        return False

    @staticmethod
    def extract_data_list(result):
        if not isinstance(result, dict):
            return []
        data = result.get('data', [])
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            for key in ('list', 'records', 'items', 'rows', 'data'):
                value = data.get(key)
                if isinstance(value, list):
                    return value
        return []

    def _request_json(self, method, url, **kwargs):
        try:
            response = requests.request(method, url, headers=self.headers, timeout=kwargs.pop('timeout', DEFAULT_REQUEST_TIMEOUT), **kwargs)
            try:
                result = response.json()
            except Exception:
                result = {}
            return response, result
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"{self.label}请求失败: {str(e)}")

    def get_all_envs(self, var_name=None, keyword=''):
        """获取面板变量列表，可按变量名/关键字过滤"""
        params = {}
        if self.is_daidai:
            params = {"page_size": 1000}
            if keyword:
                params["keyword"] = str(keyword)

        response, result = self._request_json('GET', self.base_url, params=params or None, timeout=15)
        if not self.response_ok(response, result):
            raise RuntimeError(f"获取{self.label}变量失败: HTTP {response.status_code} {getattr(response, 'text', '')}")

        envs = self.extract_data_list(result)
        if var_name:
            envs = [env for env in envs if isinstance(env, dict) and env.get('name') == var_name]
        return envs

    def search_env(self, var_name, phone=None, keyword=''):
        """按变量名 + 手机标识/关键字搜索变量"""
        phone = safe_str(phone)
        keyword = safe_str(keyword)
        query_keyword = keyword or (phone_digest(phone) if phone else '')

        envs = []
        if self.is_daidai and query_keyword:
            # 呆呆面板支持 keyword，先走服务端搜索，查不到再兜底全量搜索。
            try:
                envs = self.get_all_envs(var_name=var_name, keyword=query_keyword)
            except Exception:
                envs = []
            if not envs:
                envs = self.get_all_envs(var_name=var_name)
        else:
            envs = self.get_all_envs(var_name=var_name)

        matched = []
        for env in envs:
            if not isinstance(env, dict) or env.get('name') != var_name:
                continue
            remarks = safe_str(env.get('remarks') or env.get('remark') or env.get('description'))
            if phone:
                if remark_matches_phone(remarks, phone):
                    matched.append(env)
            elif keyword:
                if keyword in remarks:
                    matched.append(env)
            else:
                matched.append(env)
        return matched

    def find_env(self, var_name, phone):
        envs = self.search_env(var_name, phone=phone)
        return envs[0] if envs else None

    def add_env(self, var_name, value, remarks=''):
        data = {
            "name": var_name,
            "value": value,
            "remarks": remarks,
        }

        if self.is_daidai:
            if self.panel_group:
                data["group"] = self.panel_group
            response, result = self._request_json('POST', self.base_url, json=data)
        else:
            response, result = self._request_json('POST', self.base_url, json=[data])

        response_text = getattr(response, 'text', '')
        if "value must be unique" in response_text:
            raise RuntimeError(f"{self.label}变量 value 已存在，请检查是否有重复变量")

        if not self.response_ok(response, result):
            raise RuntimeError(f"添加{self.label}变量失败: HTTP {response.status_code} {response_text}")

        created = result.get('data') if isinstance(result, dict) else None
        if isinstance(created, list) and created:
            return created[0]
        if isinstance(created, dict):
            return created
        return data

    def update_env(self, env_id, var_name, value, remarks=''):
        if not env_id:
            raise RuntimeError("更新变量失败：缺少变量ID")

        data = {
            "name": var_name,
            "value": value,
            "remarks": remarks,
        }

        if self.is_daidai:
            if self.panel_group:
                data["group"] = self.panel_group
            url = f"{self.base_url}/{env_id}"
            response, result = self._request_json('PUT', url, json=data)
        else:
            data["id"] = env_id
            response, result = self._request_json('PUT', self.base_url, json=data)

        if not self.response_ok(response, result):
            raise RuntimeError(f"更新{self.label}变量失败: HTTP {response.status_code} {getattr(response, 'text', '')}")

        updated = result.get('data') if isinstance(result, dict) else None
        if isinstance(updated, dict):
            return updated
        return data

    def delete_env(self, env_id):
        if not env_id:
            return True

        if self.is_daidai:
            url = f"{self.base_url}/{env_id}"
            response, result = self._request_json('DELETE', url)
        else:
            response, result = self._request_json('DELETE', self.base_url, json=[env_id])

        if not self.response_ok(response, result):
            raise RuntimeError(f"删除{self.label}变量失败: HTTP {response.status_code} {getattr(response, 'text', '')}")
        return True

    def upsert_env_for_phone(self, var_name, value, phone, owner_user=None):
        account_vip = middleware.bucketGet(bucket='ch_xy_accountvip', key=phone)
        existing = self.find_env(var_name, phone)
        existing_remarks = existing.get('remarks') if existing else None
        remarks = build_ql_remark(phone, account_vip, owner_user=owner_user, existing_remarks=existing_remarks)
        if existing:
            env_id = self.env_id(existing)
            return self.update_env(env_id, var_name, value, remarks)
        return self.add_env(var_name, value, remarks)


def ensure_panel_connection():
    """按需建立面板连接，避免无关指令受配置影响"""
    global panel_client, QLurl, qltoken
    if panel_client is None:
        panel_client = PanelClient.from_config()
        # 兼容旧变量名，避免其他逻辑直接读取 QLurl/qltoken 时异常。
        QLurl, qltoken = panel_client.host, panel_client.token
    return panel_client


def ensure_ql_connection():
    """兼容旧函数名：实际返回当前对接面板的 host/token"""
    client = ensure_panel_connection()
    return client.host, client.token


def seekql():
    """兼容旧函数名：连接并验证当前对接面板配置"""
    client = ensure_panel_connection()
    return client.host, client.token


def QLtoken(QLurl, ClientID, ClientSecret):
    """兼容旧函数名：获取青龙 token"""
    return get_qinglong_token(QLurl.rstrip('/'), ClientID, ClientSecret)


def QLzt(osname, value, phone, owner_user=None):
    """兼容旧函数名：向当前面板添加变量"""
    client = ensure_panel_connection()
    account_vip = middleware.bucketGet(bucket='ch_xy_accountvip', key=phone)
    remarks = build_ql_remark(phone, account_vip, owner_user=owner_user)
    created = client.add_env(osname, value, remarks)
    return PanelClient.env_id(created)


def QLupdate(osname, value, qlid, phone, owner_user=None, existing_remarks=None):
    """兼容旧函数名：更新当前面板变量"""
    client = ensure_panel_connection()
    account_vip = middleware.bucketGet(bucket='ch_xy_accountvip', key=phone)
    remarks = build_ql_remark(phone, account_vip, owner_user=owner_user, existing_remarks=existing_remarks)
    updated = client.update_env(qlid, osname, value, remarks)
    return PanelClient.env_id(updated) or qlid, updated.get('createdAt') if isinstance(updated, dict) else None


def queue_pending_ql_sync(phone, value):
    """记录待同步到面板的账号变量，避免因配置错误导致授权后账号未提交"""
    middleware.bucketSet(bucket='ch_xy_ql_pending', key=phone, value=value)


def clear_pending_ql_sync(phone):
    middleware.bucketDel(bucket='ch_xy_ql_pending', key=phone)


def addenvs_raise(osname, value, phone, owner_user=None):
    """添加或更新当前对接面板变量，失败时抛异常，由上层决定是否中断"""
    client = ensure_panel_connection()
    client.upsert_env_for_phone(osname, value, phone, owner_user=owner_user)


def sync_ql_env(osname, value, phone, owner_user=None):
    """同步账号到当前面板；失败时自动写入待同步队列"""
    try:
        addenvs_raise(osname, value, phone, owner_user=owner_user)
        clear_pending_ql_sync(phone)
        return True, ''
    except Exception as e:
        queue_pending_ql_sync(phone, value)
        return False, str(e)


def Addenvs(osname, value, phone, owner_user=None):
    """兼容旧函数名：添加或更新当前面板变量"""
    return addenvs_raise(osname, value, phone, owner_user=owner_user)


def allenvs(osname, account):
    """查询当前面板变量 ID"""
    client = ensure_panel_connection()
    env = client.find_env(osname, account)
    return PanelClient.env_id(env) if env else None


def delenvs(id):
    """删除当前面板变量"""
    if not id:
        return
    client = ensure_panel_connection()
    client.delete_env(id)


def retry_pending_panel_sync(osname, phone_owner_map=None):
    """定时任务补交授权成功但面板同步失败的账号"""
    phone_owner_map = phone_owner_map or {}
    try:
        pending_keys = middleware.bucketAllKeys("ch_xy_ql_pending") or []
    except Exception:
        pending_keys = []

    if not pending_keys:
        return

    success_count = 0
    fail_count = 0
    for phone in pending_keys:
        phone = safe_str(phone)
        if not phone:
            continue

        account_vip = safe_str(middleware.bucketGet(bucket='ch_xy_accountvip', key=phone))
        if not account_vip or account_vip < today_time:
            clear_pending_ql_sync(phone)
            continue

        value = safe_str(middleware.bucketGet(bucket='ch_xy_ql_pending', key=phone))
        if not value:
            token = middleware.bucketGet(bucket='ch_xy_token', key=phone)
            did = middleware.bucketGet(bucket='ch_xy_did', key=phone)
            value = f'{token}#{did}' if token and did else ''

        if not value:
            fail_count += 1
            continue

        try:
            Addenvs(
                osname=osname,
                value=value,
                phone=phone,
                owner_user=phone_owner_map.get(phone),
            )
            clear_pending_ql_sync(phone)
            success_count += 1
        except Exception as e:
            fail_count += 1
            print(f'待同步面板变量补交失败 {mask_phone(phone)}: {str(e)}')
        time.sleep(0.3)

    if success_count or fail_count:
        print(f"待同步面板变量补交完成: 成功 {success_count} 个，失败 {fail_count} 个")


def getRandom(start, end):
    return random.randint(start, end)


class ProxyManager:
    def __init__(self, session, is_proxy, proxy_url):
        self.session = session
        self.IS_PROXY = is_proxy
        self.PROXY_URL = proxy_url
        self.proxies = None
        self.max_retries = 5
        self.base_timeout = 3

    def _fetch_proxy(self):
        """内部方法：从代理服务获取代理地址"""
        for _ in range(self.max_retries):
            try:
                response = requests.get(self.PROXY_URL, timeout=self.base_timeout)
                if response.status_code != 200:
                    print("代理服务响应异常，状态码: {}".format(response.status_code))
                    time.sleep(1)
                    continue

                proxy_text = response.text.strip()
                if not proxy_text:
                    print("获取到空代理地址")
                    time.sleep(2)
                    continue

                print("成功获取代理: {}".format(proxy_text))
                return proxy_text

            except requests.exceptions.RequestException as e:
                print("代理请求失败: {}".format(str(e)))
                time.sleep(2)

        print("代理获取失败，已达最大重试次数")
        return None

    def update_proxy(self):
        """更新当前代理配置"""
        if not self.IS_PROXY:
            return

        proxy_ip = self._fetch_proxy()
        if not proxy_ip:
            print("代理更新失败，保持当前配置")
            return

        if "白名单" in proxy_ip:
            print("代理服务异常：请先添加白名单", "critical")
            raise RuntimeError("代理白名单未配置")

        self.proxies = {
            'http': proxy_ip,
            'https': proxy_ip
        }
        print("代理已更新: {}".format(proxy_ip))

    def _request_with_retry(self, method, url, **kwargs):
        """统一的请求重试逻辑"""
        params = kwargs.get('params')
        headers = kwargs.get('headers')
        data = kwargs.get('data')
        json_data = kwargs.get('json')
        cookies = kwargs.get('cookies')
        allow_redirects = kwargs.get('allow_redirects', True)
        raw = kwargs.get('raw', False)
        timeout = kwargs.get('timeout', self.base_timeout)

        for attempt in range(self.max_retries):
            # 动态代理管理
            if self.IS_PROXY:
                if not self.proxies:
                    self.update_proxy()
            else:
                self.proxies = None

            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    data=data,
                    json=json_data,
                    cookies=cookies,
                    proxies=self.proxies,
                    allow_redirects=allow_redirects,
                    timeout=timeout
                )

                # 处理特殊响应（如代理服务返回的异常）
                if "白名单" in response.text:
                    print("检测到白名单错误，刷新代理")
                    self.update_proxy()
                    continue

                return response if raw else self._parse_response(response)

            except requests.exceptions.RequestException as e:
                sleep_time = random.uniform(1, 3)
                print("请求失败: {}，等待{:.1f}秒后重试".format(str(e), sleep_time))
                time.sleep(sleep_time)
                if self.IS_PROXY:
                    self.update_proxy()

        print("请求失败已达最大重试次数: {}".format(url))
        return None

    def _parse_response(self, response):
        """解析响应内容"""
        try:
            return response.json()
        except ValueError:
            return response.text

    def get(self, url, **kwargs):
        """GET请求封装"""
        return self._request_with_retry('GET', url, **kwargs)

    def post(self, url, **kwargs):
        """POST请求封装"""
        return self._request_with_retry('POST', url, **kwargs)


class Xingya:
    def __init__(self, user, sender):
        self.user = user  # 获取的用户id
        self.sender = sender  # 获取的middleware.py里面的sender类
        self.headers = {
            'X-App-Id': '7',
            'Authorization': '',
            'platform': '1',
            'manufacturer': 'Xiaomi',
            'version_name': '3.8.6',
            'user_agent': 'Mozilla/5.0 (Linux; Android 15; 24018RPACC Build/AQ3A.240627.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Safari/537.36',
            'app_version': '3.8.6',
            'device_platform': 'android',
            'personalized_recommend_status': '1',
            'device_type': '24018RPACC',
            'device_brand': 'Xiaomi',
            'os_version': '15',
            'channel': 'default',
            'raw_channel': 'default',
            'oaid': 'b9a08ed322bd0c26',
            'msa_oaid': 'b9a08ed322bd0c26',
            'uuid': 'randomUUID_f0975752-80b2-436d-8884-3cea3ff37fe0',
            'device_id': '',
            'ab_id': '',
            'support_h265': '1',
            'font_scale': '1.0',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/4.10.0'
        }

    def get_user_phones(self):
        return split_accounts(middleware.bucketGet("ch_xy_phone", self.user))

    def input_or_cancel(self, timeout=120000):
        """统一处理输入取消与超时，减少分散的 exit(0)"""
        value = self.sender.input(timeout, 1, False)
        if value == 'timeout' or value == '':
            self.sender.reply('⏰ 操作超时,已退出')
            return None
        if isinstance(value, str) and value.lower() == 'q':
            return 'q'
        return value

    def validate_number_input(self, value, count=999):
        return ValueErrors(value=value, count=count, sender_obj=self.sender)

    def ensure_admin_auth_ready(self):
        """管理员授权前统一校验面板，避免授权后未提交"""
        try:
            ensure_ql_connection()
            return True
        except Exception as e:
            self.sender.reply(f"""=======面板预检查失败=====
❌ 当前面板配置不可用，已终止管理员授权
------------------
请先修复面板配置后再重试
错误信息: {str(e)}
====================""")
            return False

    def delete_ql_env_for_phone(self, phone):
        """业务层承接面板删除异常并统一提示"""
        try:
            qlid = allenvs(osname=ch_xy_osname, account=str(phone))
            if qlid:
                delenvs(id=qlid)
            return True
        except Exception as e:
            self.sender.reply(str(e))
            return False

    def apply_authorization_to_phone(self, phone, months):
        """统一单账号授权逻辑，普通用户/管理员共用"""
        token = middleware.bucketGet(bucket='ch_xy_token', key=phone)
        did = middleware.bucketGet(bucket='ch_xy_did', key=phone)
        if not token or not did:
            self.sender.reply(f"❌ 账号 {mask_phone(phone)} 缺少登录凭证，请先重新登录")
            return False

        accountVip = safe_str(middleware.bucketGet(bucket='ch_xy_accountvip', key=phone))
        accountVip = empower(empowertime=accountVip, me_as_int=months)
        middleware.bucketSet(bucket='ch_xy_accountvip', key=phone, value=accountVip)
        return self.sync_authorized_account(phone, token, did)

    def get_account_vip_status(self, phone):
        account_vip = safe_str(middleware.bucketGet(bucket='ch_xy_accountvip', key=phone))
        if len(account_vip) == 0:
            return account_vip, '⚠️ 未授权', False, '未授权'
        if account_vip < today_time:
            return account_vip, '❌ 已过期', False, '已过期'
        return account_vip, f'✅ {account_vip}', True, f'到期：{account_vip}'

    def ensure_ql_ready_for_auth(self):
        """授权前先校验面板配置，避免付费/授权成功后账号未提交到面板"""
        try:
            ensure_ql_connection()
            return True
        except Exception as e:
            self.sender.reply(f"""=======面板预检查失败=====
❌ 当前面板配置不可用，已终止授权
------------------
请先修复面板配置后再重试
错误信息: {str(e)}
====================""")
            return False

    def sync_authorized_account(self, phone, token, did):
        """授权后同步账号到面板，失败时保留授权并记录待同步状态"""
        env_value = f'{token}#{did}'
        success, error = sync_ql_env(ch_xy_osname, env_value, phone, owner_user=self.user)
        if success:
            return True

        self.sender.reply(f"""=======授权完成但同步失败=====
⚠️ 账号已完成授权，但提交面板失败
📱 账号: {mask_phone(phone)}
------------------
系统已自动记录为“待同步”
修复面板配置后，可等待定时任务自动补交
错误信息: {error}
==========================""")
        return False

    def build_phone_selection_menu(self, title, phones, include_all_query=False, include_all_manage=False):
        lines = [f'===== {title} =====']
        if include_all_query:
            lines.append('[0] 查询全部账号')
        for i, phone in enumerate(phones, 1):
            _, _, _, status_text = self.get_account_vip_status(phone)
            lines.append(f'[{i}] {mask_phone(phone)} ({status_text})')
        if include_all_manage:
            lines.append('[999] 选择全部')
        lines.append('===================')
        lines.append('输入序号选择账号，可多选如 1,3,5')
        if include_all_query or include_all_manage:
            lines.append('输入 999 选择全部账号')
        lines.append('输入q取消操作')
        return '\n'.join(lines)

    def get_account_credentials(self, phone):
        token = middleware.bucketGet(bucket='ch_xy_token', key=phone)
        did = middleware.bucketGet(bucket='ch_xy_did', key=phone)
        return token, did

    def parse_phone_selections(self, selection_text, phones, allow_select_all=False, allow_zero_all=False):
        """解析账号多选输入，支持 1,2,3 / 1 2 3 / 1、2、3 / 999 全选"""
        if not selection_text:
            return None

        selection_text = selection_text.strip()
        if allow_select_all and selection_text == '999':
            return phones[:]
        if allow_zero_all and selection_text == '0':
            return phones[:]

        normalized = selection_text
        for sep in ['，', '、', ' ', '\n', '\t', ';', '；', '|']:
            normalized = normalized.replace(sep, ',')

        raw_items = [item.strip() for item in normalized.split(',') if item.strip()]
        if not raw_items:
            return None

        selected_phones = []
        used_index = set()
        for item in raw_items:
            if not item.isdigit():
                return None

            index = int(item)
            if allow_select_all and index == 999:
                return phones[:]
            if allow_zero_all and index == 0:
                return phones[:]
            if index < 1 or index > len(phones):
                return None

            if index not in used_index:
                selected_phones.append(phones[index - 1])
                used_index.add(index)

        return selected_phones

    def query_selected_accounts(self, phones):
        self.sender.reply(f"正在查询{len(phones)}个星芽账号信息……")
        for phone in phones:
            self.account_cx(phone)
            time.sleep(3)

    def batch_authorize_phones(self, phones, months, pay_project='星芽批量授权', need_pay=True):
        if not phones:
            self.sender.reply('❌ 未选择任何账号')
            return
        if not self.ensure_ql_ready_for_auth():
            return

        account_count = len(phones)
        months = int(months)
        money = Decimal(months) * Decimal(ch_xy_money) * Decimal(account_count)
        if need_pay and not self.zf(project=pay_project, me_as_int=months * account_count):
            return

        success_count = 0
        for phone in phones:
            if self.apply_authorization_to_phone(phone, months):
                success_count += 1
            print(f"phone: {mask_phone(phone)} 授权处理完成")
            time.sleep(0.5)

        self.sender.reply(f"""=======订单完成=====
🎈 名称: {pay_project}
👌 账号数量: {account_count} 个
🎉 数量: {months} 个月
💰 金额: {money} 元
✅ 授权完成: {success_count} 个
====================""")

    def batch_delete_phones(self, phones):
        success_count = 0
        failed_accounts = []
        for phone in phones:
            if self.delete_ql_env_for_phone(phone):
                unbind_user_phone(self.user, phone)
                success_count += 1
            else:
                failed_accounts.append(mask_phone(phone))
            time.sleep(0.3)

        result_lines = [
            '=======批量删除完成=======',
            f'✅ 删除成功: {success_count}个',
        ]
        if failed_accounts:
            result_lines.append(f'⚠️ 删除失败: {"、".join(failed_accounts)}')
        result_lines.append('==========================')
        self.sender.reply('\n'.join(result_lines))

    def batch_upload_time(self, phones, times):
        success_count = 0
        skipped_accounts = []
        for phone in phones:
            _, _, is_authorized, _ = self.get_account_vip_status(phone)
            if not is_authorized:
                skipped_accounts.append(mask_phone(phone))
                continue

            token, did = self.get_account_credentials(phone)
            if not token or not did:
                skipped_accounts.append(mask_phone(phone))
                continue

            if self.uploadtime(times, token, did, phone=phone, notify=False):
                success_count += 1
            else:
                skipped_accounts.append(mask_phone(phone))
            time.sleep(1)

        result_lines = [
            '=======批量刷时长完成=======',
            f'✅ 成功账号: {success_count}个',
            f'⏰ 提交时长: {times}分钟',
        ]
        if skipped_accounts:
            result_lines.append(f'⚠️ 跳过/失败: {"、".join(skipped_accounts)}')
        result_lines.append('==========================')
        self.sender.reply('\n'.join(result_lines))

    def zf(self,project, me_as_int):
        """支付处理"""
        try:
            zsm = middleware.bucketGet('ch_xy_config', 'zsm')
            use_ma_pay = middleware.bucketGet('ch_xy_config', 'use_ma_pay') == 'true'

            if not zsm and not use_ma_pay and not xycoin:
                self.sender.reply('❌ 未配置收款方式,请联系管理员!')
                return False

            # 检查是否允许使用积分支付
            if int(xycoin) > 0:
                points = middleware.bucketGet('ch_xy_config', "jfbl") or "dd_sign_points"
                usercoin = middleware.bucketGet(points, user) or '0'
                zfcoin = int(xycoin) * me_as_int

            # 构建支付选择菜单
            pay_menu = """=====选择支付方式===="""

            # 添加微信支付选项
            if zsm:
                money = Decimal(me_as_int) * Decimal(ch_xy_money)
                pay_menu += f"""
1️⃣ 微信支付
   💰 {money}元/{me_as_int}月"""

            # 添加码支付选项
            if use_ma_pay:
                # 从卡密系统获取码支付配置
                ma_pay_data = middleware.bucketGet('ch_xy_config', 'mzf')
                parts = ma_pay_data.split('丨')
                ma_pay_config = {
                    'switch': middleware.bucketGet('ch_xy_config', 'ma_pay_switch') or 'false',
                    'gateway': parts[0],
                    'pid': parts[1],
                    'key': parts[2],
                    'type': parts[3],
                    'notify_url': '',
                    'return_url': ''
                }

                if ma_pay_config['switch'].lower() == 'true' and all(
                        [ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                    money = Decimal(me_as_int) * Decimal(ch_xy_money)
                    pay_menu += f"""
2️⃣ 码支付
   💰 {money}元/{me_as_int}月"""

            # 只有当pgcoin > 0时才显示积分支付选项
            if xycoin and int(xycoin) > 0:
                pay_menu += f"""
3️⃣ 积分支付  
   🎯 {zfcoin}积分/{me_as_int}月
   💫 当前积分: {usercoin}"""

            pay_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""

            self.sender.reply(pay_menu)
            choice = self.sender.input(60000, 1, False)

            if choice == 'q' or choice == 'Q':
                self.sender.reply("✅ 已取消支付")
                return False

            elif choice == '1' and zsm:
                # 微信支付流程
                zfzt = self.sender.atWaitPay()
                if zfzt:
                    self.sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
                    return False

                money = Decimal(me_as_int) * Decimal(ch_xy_money)

                pay_msg = f"""=====微信扫码支付====
🎫 商品: {project}
📅 时长: {me_as_int}月
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
                self.sender.reply(pay_msg)
                self.sender.replyImage(zsm)

                ddzf = self.sender.waitPay("q", 100 * 1000)

                if str(ddzf) == 'q':
                    self.sender.reply('✅ 已取消支付')
                    return False

                try:
                    if isinstance(ddzf, dict):
                        # 新版微信赞赏消息格式
                        if ddzf.get('Type') == '微信赞赏':
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                            From = ddzf.get('FromName', '')
                        # 新版微信收款消息格式
                        elif ddzf.get('Type') == '微信收款':
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                            From = ddzf.get('FromName', '')
                        # 旧版BORW格式
                        elif ddzf.get('Money'):
                            Money = float(ddzf.get('Money', 0))
                            Time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                            From = ddzf.get('FromName', '')
                        # 旧版GW格式
                        elif ddzf.get('money'):
                            Money = float(ddzf.get('money', 0))
                            Time = ddzf.get('time', '').replace('T', ' ').split('.')[0]
                            From = ddzf.get('fromName', '')
                        else:
                            self.sender.reply('不支持的支付消息格式')
                            return False
                    else:
                        # 尝试解析JSON字符串
                        try:
                            ddzf = json.loads(ddzf)
                            if ddzf.get('Type') == '微信赞赏':
                                Money = float(ddzf.get('Money', 0))
                                Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                                From = ddzf.get('FromName', '')
                            elif ddzf.get('Type') == '微信收款':
                                Money = float(ddzf.get('Money', 0))
                                Time = ddzf.get('Time', '').split('.')[0].replace('T', ' ')
                                From = ddzf.get('FromName', '')
                            else:
                                Money = float(ddzf.get('Money', 0))
                                Time = ddzf.get('Time', '').replace('T', ' ').split('.')[0]
                                From = ddzf.get('FromName', '')
                        except:
                            if "二维码赞赏到账" in str(ddzf):
                                try:
                                    amount = str(ddzf).split("收款金额￥")[1].split("\n")[0]
                                    time = str(ddzf).split("到账时间")[1].split("\n")[0]
                                    Money = float(amount)
                                    Time = time.strip()
                                    From = ''
                                except Exception as e:
                                    self.sender.reply(f"❌ 解析收款信息失败: {str(e)}")
                                    return False
                            else:
                                self.sender.reply("❌ 无法解析支付结果")
                                return False

                    if float(Money) >= float(money):
                        return True
                    else:
                        self.sender.reply(f"""=====支付金额错误=====
💰 应付: {money}元
💳 实付: {Money}元
{f'👤 付款人: {From}' if From else ''}

❗ 请联系管理员处理退款！
==================""")
                        return False
                except Exception as e:
                    self.sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                    return False

            elif choice == '2' and use_ma_pay:
                # 码支付流程
                money = Decimal(me_as_int) * Decimal(ch_xy_money)

                # 生成订单号
                out_trade_no = f"XY{int(time.time())}{user}"

                # 构造支付参数
                params = {
                    'pid': ma_pay_config['pid'],
                    'type': ma_pay_config['type'].split(',')[0],  # 默认使用第一个支付方式
                    'out_trade_no': out_trade_no,
                    'name': f"{senderID}-星芽授权-{str(money)}",
                    'money': str(money),
                    'notify_url': ma_pay_config['notify_url'],
                    'return_url': ma_pay_config['return_url'],
                    'param': user  # 传递用户ID作为附加参数
                }

                # 按照ASCII码排序参数
                sorted_params = sorted(params.items(), key=lambda x: x[0])

                # 拼接成URL键值对格式
                sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])

                # 添加密钥进行MD5签名
                sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()

                # 添加签名到参数
                params['sign'] = sign
                params['sign_type'] = 'MD5'

                # 发送支付请求
                gateway = ma_pay_config['gateway']
                if not gateway.endswith('/'):
                    gateway += '/'
                submit_url = gateway + 'submit.php'

                try:
                    response = requests.post(submit_url, data=params)
                    if 'location.href' in response.text:
                        # 提取支付URL
                        match = re.search(r'location\.href\s*=\s*[\'"](.*?)[\'"]', response.text)
                        if match:
                            pay_url = match.group(1)
                            if not pay_url.startswith('http'):
                                pay_url = gateway + pay_url

                            self.sender.reply(f"""=====码支付=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 有效期: 5分钟
------------------
请点击链接完成支付:
{pay_url}
==================""")

                            # 轮询订单状态
                            for _ in range(60):  # 最多等待5分钟
                                time.sleep(5)
                                check_url = gateway + 'api.php'
                                check_params = {
                                    'act': 'order',
                                    'pid': ma_pay_config['pid'],
                                    'key': ma_pay_config['key'],
                                    'out_trade_no': out_trade_no
                                }

                                try:
                                    check_resp = requests.get(check_url, params=check_params)
                                    result = check_resp.json()

                                    if result.get('code') == 1:  # 支付成功
                                        return True
                                except:
                                    continue

                            self.sender.reply("❌ 支付超时,请重新发起支付!")
                            return False
                    else:
                        self.sender.reply("❌ 创建支付订单失败!")
                        return False
                except Exception as e:
                    self.sender.reply(f"❌ 支付请求失败: {str(e)}")
                    return False

            elif choice == '3' and xycoin != 0:
                # 积分支付流程
                if int(usercoin) < zfcoin:
                    self.sender.reply(f"""=====积分不足=====
👤 当前积分: {usercoin}
📍 需要积分: {zfcoin}
==================""")
                    return False

                confirm_msg = f"""=====积分支付确认=====
💫 消耗积分: {zfcoin}
⏰ 授权时长: {me_as_int}月
------------------
确认请回复【y】
取消请回复【n】
=================="""
                self.sender.reply(confirm_msg)

                if self.yesornos():
                    try:
                        new_balance = int(usercoin) - zfcoin
                        points = middleware.bucketGet('ch_xy_config', "jfbl") or "dd_sign_points"
                        middleware.bucketSet(points, user, str(new_balance))
                        return True
                    except Exception as e:
                        self.sender.reply(f"❌ 积分支付处理失败: {str(e)}")
                        return False
                else:
                    self.sender.reply("✅ 已取消支付")
                    return False
            else:
                self.sender.reply("❌ 输入无效")
                return False

        except Exception as e:
            self.sender.reply(f"❌ 支付处理发生错误: {str(e)}")
            return False

    def yesornos(self):
        """确认操作"""
        yesorno = self.sender.input(120000, 1, False)
        if not yesorno or yesorno == 'timeout':
            self.sender.reply('⏰ 输入超时！')
            return None
        if yesorno.lower() in ['y', '是']:
            return True
        elif yesorno.lower() in ['n', '否']:
            return False
        elif yesorno.lower() in ['q', '退出']:
            self.sender.reply('✅ 已退出!')
            return None
        else:
            self.sender.reply('❌ 输入错误！')
            return None
    def getfirsttoken(self, android_id, device_id):
        a_time = int(time.time() * 1000)
        b_time = str(a_time - 3600000)
        xydata = (f'{{"device":"{device_id}",'
                  '"package_name":"com.jz.xydj",'
                  f'"android_id":"{android_id}",'
                  '"install_first_open":true,'
                  f'"first_install_time":{b_time},'
                  f'"last_update_time":{b_time},'
                  '"report_link_url":"",'
                  '"authorization":"",'
                  f'"timestamp":{a_time}}}'
                  )
        auth = xyauth(xydata)
        headers = self.headers.copy()
        headers['device_id'] = device_id
        headers['Content-Type'] = 'application/json; charset=utf-8'

        response0 = proxy_manager.post(
            "https://u.shytkjgs.com/user/v3/account/login",
            data=auth,
            headers=headers,
            timeout=DEFAULT_REQUEST_TIMEOUT,
        )
        print(f"验证码接口返回: {response0.get('code')}")
        json_data = response0
        token = json_data['data']['token']
        headers['Authorization'] = token
        return headers
    def caidan(self):
        mes = '''=====星芽插件教程=====
🏅用户功能指令：
------------------
1️⃣ 星芽登录
• 支持手机号验证码登录
• 输入手机号后获取短信验证码完成绑定
• 登录成功后自动保存 token 与 did

2️⃣ 星芽ck提交 / 星芽CK提交
• 支持批量提交账号 CK
• CK格式：authorization#device_id
• 提交格式：一行一个

3️⃣ 星芽查询
• 查询已绑定账号
• 支持单个查询或全部查询
• 可查看账号授权状态、金币与可提现余额

4️⃣ 星芽管理
• 查看当前绑定的全部账号
• 支持单账号授权、删除账号
• 支持全部账号批量授权
• 授权后自动同步青龙/呆呆面板，失败会记录待补交

5️⃣ 星芽刷时长
• 支持单账号刷时长
• 支持多账号/全部账号批量刷时长
• 仅授权有效账号可正常使用

🔱管理员指令：
------------------
• 星芽授权
  - 可按用户ID批量授权该用户全部账号
  - 可单独授权指定手机号账号
  - 可修改账号授权时长

⚠️使用说明：
------------------
1. 首次使用前，请先在星芽完成账号注册
2. 如需自动同步面板，请先正确配置青龙或呆呆面板参数
3. 授权账号到期后，定时任务会自动尝试清理对应面板变量
4. 若授权后同步失败，系统会记录待同步数据，修复配置后可自动补交
5. 建议定期执行查询，及时检查账号状态与余额
==================
'''
        self.sender.reply(mes)
        return

    def sms_login(self):
        aid, did = getdid()
        headers = self.getfirsttoken(aid, did)
        self.sender.reply("""=======星芽登录=====
请输入手机号:
------------------
回复"q"退出操作
====================""")
        phone = self.input_or_cancel(120000)
        if phone is None:
            return
        if phone == 'q':
            self.sender.reply("✅ 已取消登录")
            return
        if not phone.isdigit() or len(phone) != 11:
            self.sender.reply("""=======格式错误=====
❌ 请输入正确的11位手机号
====================""")
            return
        payload = f'{{"mobile":"{phone}"}}'

        response0 = proxy_manager.post(
            "https://u.shytkjgs.com/user/v1/sms/code",
            data=payload,
            headers=headers,
        )
        if response0['code'] == 'ok':
            print("验证码获取成功！")
            self.sender.reply("""=======验证码登录=====
请输入收到的4位验证码:
------------------
回复"q"退出操作
====================""")
            smscode = self.input_or_cancel(120000)
            if smscode is None:
                return
            if smscode == 'q':
                self.sender.reply("✅ 已取消登录")
                return
            payload1 = f'mobile={phone}&code={smscode}'
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

            response1 = proxy_manager.post(
                "https://u.shytkjgs.com/user/v1/account/sms/login",
                data=payload1,
                headers=headers,
            )
            print(f"短信登录接口返回: {response1.get('code')}")
            if response1['code'] == 'ok':
                token = response1['data']['token']
                headers['Authorization'] = token
                headers.pop('Content-Type', None)
                headers.pop('Content-Length', None)

                response2 = proxy_manager.get(
                    "https://u.shytkjgs.com/user/v1/account/detail",
                    headers=headers,
                    timeout=DEFAULT_REQUEST_TIMEOUT,
                )
                print(f"账号详情接口返回: {response2.get('code')}")

                if response2['code'] == 'ok':
                    token2 = response2['data']['token']
                    middleware.bucketSet("ch_xy_token", phone, token2)
                    middleware.bucketSet("ch_xy_did", phone, did)
                    bind_user_phone(self.user, phone)
                    self.sender.reply(f"{mask_phone(phone)}登陆成功！")
                else:
                    self.sender.reply("异常错误")
                    return
            else:
                self.sender.reply("异常错误")
                return
        else:
            self.sender.reply("异常错误")
            return
    def ck_login(self):
        zh = f'===================\nCK提交登录\nCK格式：authorization#device_id\n提交格式：一行一个\n\n输入q取消操作\n==================='
        self.sender.reply(zh)
        cks = self.sender.input(120000, 1, False)
        if not cks or cks.lower() == 'q':
            self.sender.reply("✅ 已取消CK提交")
            return
        cklist = [item.strip() for item in cks.split("\n") if item.strip()]
        num = len(cklist)
        self.sender.reply(f"解析出{str(num)}个账号")
        success_count = 0
        failed_count = 0
        for cookie in cklist:
            spl = cookie.split("#")
            if len(spl) != 2 or not spl[0] or not spl[1]:
                failed_count += 1
                continue
            auth = spl[0]
            did = spl[1]

            headers = {'X-App-Id': '7', 'platform': '1', 'manufacturer': 'Xiaomi', 'version_name': '3.8.6',
                               'user_agent': 'Mozilla/5.0 (Linux; Android 15; 23127PN0CC Build/AQ3A.240627.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36',
                               'app_version': '3.8.6', 'device_platform': 'android',
                               'personalized_recommend_status': '1', 'device_type': '23127PN0CC',
                               'device_brand': 'Xiaomi', 'os_version': '15', 'channel': 'default',
                               'raw_channel': 'default', 'uuid': 'randomUUID_799e9ea8-24e7-4cbe-aba0-bdd6fcbd8c01',
                               'device_id': did, 'ab_id': '', 'support_h265': '1', 'font_scale': '1.0',
                               'Content-Type': 'application/json; charset=utf-8', 'Content-Length': '738',
                               'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip', 'User-Agent': 'okhttp/4.10.0'}
            timestemp = int(time.time() * 1000)
            data = f'{{"device":"{did}","package_name":"com.jz.xydj","android_id":"1f225bd92500df96","install_first_open":false,"first_install_time":1748882426598,"last_update_time":1748882426598,"report_link_url":"","authorization":"{auth}","timestamp":{timestemp}}}'

            payload = xyauth(data)
            max_retry = 3
            for attempt in range(max_retry):
                try:
                    r = proxy_manager.post(
                        "https://u.shytkjgs.com/user/v3/account/login",
                        data=payload,
                        headers=headers,
                    )


                    if r['code'] == 'ok':
                        phone = r['data']['mobile']
                        token = r['data']['token']
                        middleware.bucketSet("ch_xy_token", phone, token)
                        middleware.bucketSet("ch_xy_did", phone, did)
                        bind_user_phone(self.user, phone)
                        success_count += 1

                        time.sleep(5)
                        break  # 成功则跳出重试循环

                except Exception as e:
                    print(f'代理请求异常({attempt + 1}/{max_retry}): {str(e)}')
                    time.sleep(2)  # 失败后短暂等待
            else:
                failed_count += 1
        self.sender.reply(f"已添加{success_count}个账号，失败{failed_count}个")
    # 账号查询函数
    def account_cx(self, phone):
        zhanghao = ''
        accountVip = safe_str(middleware.bucketGet(bucket='ch_xy_accountvip', key=phone))
        if len(accountVip) == 0 or accountVip < today_time:
            accountVip = '授权已过期'
        try:
            auth = middleware.bucketGet(bucket='ch_xy_token', key=phone)
            did = middleware.bucketGet(bucket='ch_xy_did', key=phone)
            headers = self.headers.copy()
            headers['Authorization'] = auth
            headers['device_id'] = did

            res = proxy_manager.get(
                "https://app.whjzjx.cn/v1/account/detail",
                headers=headers,
                allow_redirects=False
            )
            if res['code'] == 'ok':
                coins = res['data']['species']
                monee = res['data']['cash_remain']
                zhanghao += f'''=====账号详情=====
📱账号: {mask_phone(phone)}
📅到期时间: {accountVip}
💰目前金币数量: {coins}
💰可提现: {monee}
=================='''
                self.sender.reply(zhanghao)
            else:
                self.sender.reply(f'账号{mask_phone(phone)}:\n❌账号失效，请重新登陆！\n====================\n')
        except Exception as e:
            self.sender.reply(f'查询异常：{e}')
    # 上传时长
    def uploadtime(self,times,auth,did, phone=None, notify=True):
        timess = int(times) * 60
        url = "https://xingya-track.shytkjgs.com/receive"
        timestamp = int(time.time() * 1000)
        timestamp2 = timestamp + 500
        headers = {
            "X-App-Id": "7",
            "Authorization": auth,
            "platform": "1",
            "manufacturer": "Xiaomi",
            "version_name": "3.7.0.1",
            "user_agent": "Mozilla/5.0 (Linux; Android 15; 24018RPACC Build/AQ3A.240627.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Safari/537.36",
            "app_version": "3.7.0.1",
            "device_platform": "android",
            "personalized_recommend_status": "1",
            "device_type": "24018RPACC",
            "device_brand": "Xiaomi",
            "os_version": "15",
            "channel": "default",
            "raw_channel": "default",
            "oaid": "eae5956f5dbb7182",
            "msa_oaid": "eae5956f5dbb7182",
            "uuid": "randomUUID_dd75b61d-f085-40c6-9b5c-85693b23342b",
            "device_id": did,
            "ab_id": "",
            "support_h265": "1",
            "font_scale": "1.0",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "User-Agent": "okhttp/4.10.0"
        }
        # res = requests.request('get', 'https://app.whjzjx.cn/v1/account/detail', headers=headers, timeout=15)
        res = proxy_manager.get(
            "https://app.whjzjx.cn/v1/account/detail",
            headers=headers,
            allow_redirects=False
        )
        user_id = res['data']['user_id']
        headers["Host"] = "xingya-track.shytkjgs.com"
        payload = [
            {
                "event_id": "action_episode_view",
                "page_id": "page_drama_detail",
                "eventType": "action",
                "event_type": "action",
                "timestamp": timestamp,
                "user_id": user_id,
                "login_status": True,
                "retry": 0,
                "device_id": did,
                "device_type": "Xiaomi",
                "phone_version": "24018RPACC",
                "os_type": 1,
                "os_name": "15",
                "version": "3.7.0.1",
                "package_name": "com.jz.xydj",
                "app_id": "7",
                "channel": "default",
                "raw_channel": "default",
                "font_scale": 1.0,
                "define_args": f"{{\"page\":\"page_drama_detail\",\"theater_id\":\"4063\",\"theater_number\":\"2\",\"theater_duration\":\"{timess}\",\"lock\":\"0\",\"complete\":\"1\",\"entrance_scene\":\"0\",\"entrance\":\"27\",\"ab_id\":\"\",\"last_page\":\"page_welfare\"}}"
            },
            {
                "event_id": "theater_play_show",
                "page_id": "page_drama_detail",
                "eventType": "show",
                "event_type": "show",
                "timestamp": timestamp2,
                "user_id": user_id,
                "login_status": True,
                "retry": 0,
                "device_id": did,
                "device_type": "Xiaomi",
                "phone_version": "24018RPACC",
                "os_type": 1,
                "os_name": "15",
                "version": "3.7.0.1",
                "package_name": "com.jz.xydj",
                "app_id": "7",
                "channel": "default",
                "raw_channel": "default",
                "font_scale": 1.0,
                "define_args": f"{{\"theater_id\":\"4063\",\"theater_number\":\"3\",\"ab_id\":\"\",\"last_page\":\"page_welfare\"}}"
            }
        ]
        try:
            response = proxy_manager.post(
                url,
                json=payload,
                headers=headers,
            )
            if notify:
                prefix = f"账号 {mask_phone(phone)} " if phone else ""
                self.sender.reply(f"{prefix}看剧时长已提交{times}分钟")
            return True
        except Exception as e:
            if notify:
                prefix = f"账号 {mask_phone(phone)} " if phone else ""
                self.sender.reply(f"{prefix}看剧时长提交失败")
            return False

    # 账号登录功能
    def login(self):

        self.sms_login()

    # 账号查询功能
    def chaxun(self):
        parts = self.get_user_phones()
        if not parts:
            self.sender.reply("""=======未绑定账号=====
❌ 未找到任何账号信息
💡 发送星芽登录绑定
====================""")
            return

        self.sender.reply(self.build_phone_selection_menu('选择查询账号', parts, include_all_query=True, include_all_manage=True))
        xuan = self.sender.input(120000, 1, False)
        if not xuan or xuan.lower() == 'q':
            self.sender.reply("✅ 已取消查询")
            return

        selected_phones = self.parse_phone_selections(xuan, parts, allow_select_all=True, allow_zero_all=True)
        if selected_phones:
            self.query_selected_accounts(selected_phones)
            return

        self.sender.reply("❌ 输入无效，请输入正确的账号序号，多个序号可用逗号分隔")


    # 账号管理功能
    def guanli(self):
        parts = self.get_user_phones()
        if not parts:
            self.sender.reply(f"""=======未绑定账号=====
❌ 未找到任何账号信息
💡 发送星芽登录绑定
====================""")
            return
        self.sender.reply(self.build_phone_selection_menu('我的星芽账号', parts, include_all_manage=True))
        self.sender.reply('💡 支持单选或多选，例如：1 或 1,3,5；输入 999 表示全部账号')
        xuan = self.sender.input(120000, 1, False)
        if xuan == 'timeout':
            self.sender.reply('⏰ 操作超时,已退出')
            return
        if not xuan or xuan.lower() == 'q':
            self.sender.reply("✅ 已取消管理")
            return

        selected_phones = self.parse_phone_selections(xuan, parts, allow_select_all=True)
        if not selected_phones:
            self.sender.reply('❌ 输入无效，请输入正确的账号序号，多个序号可用逗号分隔')
            return

        if len(selected_phones) == 1:
            phone = selected_phones[0]
            token = middleware.bucketGet(bucket='ch_xy_token', key=phone)
            did = middleware.bucketGet(bucket='ch_xy_did', key=phone)
            accountVip, vip_status, _, _ = self.get_account_vip_status(phone)
            account_info = f"""
=======账号详情======
📱 账号: {mask_phone(phone)}
🔐 授权: {vip_status}
=================="""
            self.sender.reply(account_info)

            menu = """=======账号管理======
[1] 授权账号
[2] 删除账号
------------------
回复数字选择功能
回复"q"退出操作
=================="""
            self.sender.reply(menu)

            inputmessage = self.sender.input(120000, 1, False)
            if inputmessage == '2':
                confirm_msg = """=======删除警告=====
❌ 确定要删除该账号吗？
------------------
此操作不可恢复！
[y] 确认删除
[n] 取消操作
===================="""
                self.sender.reply(confirm_msg)

                yesorno = self.sender.input(120000, 1, False)
                if yesorno and yesorno.lower() in ['y', '是']:
                    parts.remove(str(phone))
                    if not self.delete_ql_env_for_phone(phone):
                        return
                    unbind_user_phone(self.user, phone)
                    self.sender.reply('✅ 账号删除成功!')
                else:
                    self.sender.reply('✅ 已取消删除')
                    return
            elif inputmessage == '1':
                if not self.ensure_ql_ready_for_auth():
                    return
                auth_guide = """=======授权设置=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
===================="""
                self.sender.reply(auth_guide)

                mes = self.sender.input(120000, 1, False)
                if not mes or mes == 'timeout':
                    self.sender.reply('⏰ 操作超时,已退出')
                    return
                if mes.lower() == 'q':
                    self.sender.reply("✅ 已取消授权")
                    return

                mes = self.validate_number_input(value=mes, count=999)
                if mes is None:
                    return
                money = Decimal(mes) * Decimal(ch_xy_money)
                if not self.zf(project='星芽授权', me_as_int=mes):
                    return

                success = self.apply_authorization_to_phone(phone, mes)

                result_msg = f"""=======订单完成=====
🎈 名称: 星芽授权
🎉 数量: {mes} 个月
💰 金额: {money} 元
✅ 授权完成: {1 if success else 0} 个
===================="""
                self.sender.reply(result_msg)
        else:
            num = len(selected_phones)
            account_list = mask_phone_list(selected_phones)
            account_info = f"""
=======账号详情======
📱 账号: 共{num}个账号
📋 已选: {account_list}
=================="""
            self.sender.reply(account_info)

            menu = """=======账号管理======
[1] 批量授权
[2] 批量删除
------------------
回复数字选择功能
回复"q"退出操作
=================="""
            self.sender.reply(menu)

            inputmessage = self.sender.input(120000, 1, False)
            if inputmessage == '1':
                auth_guide = """=======授权设置=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
===================="""
                self.sender.reply(auth_guide)

                mes = self.sender.input(120000, 1, False)
                if not mes or mes == 'timeout':
                    self.sender.reply('⏰ 操作超时,已退出')
                    return
                if mes.lower() == 'q':
                    self.sender.reply("✅ 已取消授权")
                    return

                mes = self.validate_number_input(value=mes, count=999)
                if mes is None:
                    return
                self.batch_authorize_phones(selected_phones, mes)
            elif inputmessage == '2':
                confirm_msg = f"""=======删除警告=====
❌ 确定要删除选中的 {num} 个账号吗？
📋 已选: {account_list}
------------------
此操作不可恢复！
[y] 确认删除
[n] 取消操作
===================="""
                self.sender.reply(confirm_msg)
                yesorno = self.sender.input(120000, 1, False)
                if yesorno and yesorno.lower() in ['y', '是']:
                    self.batch_delete_phones(selected_phones)
                else:
                    self.sender.reply('✅ 已取消删除')
            else:
                self.sender.reply(f"❌ 输入无效")
                return


    # 提现（刷时长）功能
    def tixian(self):
        parts = self.get_user_phones()
        if not parts:
            self.sender.reply(f"""=======未绑定账号=====
❌ 未找到任何账号信息
💡 发送星芽登录绑定
====================""")
            return
        self.sender.reply(self.build_phone_selection_menu('我的星芽账号', parts, include_all_manage=True))
        self.sender.reply('💡 支持单选或多选，例如：1 或 1,3,5；输入 999 表示全部账号')
        xuan = self.sender.input(120000, 1, False)
        if xuan == 'timeout':
            self.sender.reply('⏰ 操作超时,已退出')
            return
        if not xuan or xuan.lower() == 'q':
            self.sender.reply("✅ 已取消时长刷取")
            return

        selected_phones = self.parse_phone_selections(xuan, parts, allow_select_all=True)
        if not selected_phones:
            self.sender.reply('❌ 输入无效，请输入正确的账号序号，多个序号可用逗号分隔')
            return

        if len(selected_phones) == 1:
            phone = selected_phones[0]
            token = middleware.bucketGet(bucket='ch_xy_token', key=phone)
            did = middleware.bucketGet(bucket='ch_xy_did', key=phone)
            _, vip_status, is_tixian, _ = self.get_account_vip_status(phone)
            account_info = f"""
=======账号详情======
📱 账号: {mask_phone(phone)}
🔐 授权: {vip_status}
=================="""
            self.sender.reply(account_info)
            if is_tixian == 0:
                self.sender.reply("⚠️ 账号未授权，请先授权")
                return
            menu = "回复需要刷取的时长（数字）单位分钟"
            self.sender.reply(menu)
            timess = self.sender.input(120000, 1, False)
            if timess.isdigit():
                self.uploadtime(timess, token, did, phone=phone)
                return
            else:
                self.sender.reply('❌ 输入无效')
                return
        else:
            account_list = '、'.join(mask_phone(phone) for phone in selected_phones)
            self.sender.reply(f"已选择 {len(selected_phones)} 个账号：{account_list}")
            menu = "回复需要批量刷取的时长（数字）单位分钟"
            self.sender.reply(menu)
            timess = self.sender.input(120000, 1, False)
            if timess and timess.isdigit():
                self.batch_upload_time(selected_phones, timess)
                return
            self.sender.reply('❌ 输入无效')
            return

        # 授权/清理功能
    def shouquan(self):
        print("开始执行星芽授权功能")

        if not self.sender.isAdmin():
            self.sender.reply("""=======权限错误=====
⛔ 您没有权限执行此操作
====================""")
            return
        self.sender.reply("""=====星芽授权=====
[1] 📱 授权选定用户的星芽
[2] 👤 单独授权星芽账号
[3] ⏰ 修改授权时间
------------------
⚠️ 输入q退出操作
====================""")
        xz = self.sender.input(60000, 1, False)
        if not xz:  # 处理空输入
            self.sender.reply('⏰ 操作超时')
            return

        if xz.lower() == 'q':
            self.sender.reply("✅ 已退出授权")
            return
        if xz == '1':
            if not self.ensure_admin_auth_ready():
                return
            # 一键授权所有用户
            self.sender.reply("""=======授权用户=====
📝 请输入用户ID（QQ号）
💡 通过发送myuid获取
⚠️ 输入q退出操作
====================""")
            usersid = self.sender.input(60000, 1, False)
            if not usersid:
                self.sender.reply('⏰ 操作超时')
                return
            if usersid.lower() == 'q':
                self.sender.reply("✅ 已退出授权")
                return
            users = safe_str(middleware.bucketGet("ch_xy_phone", usersid))
            if len(users) == 0:
                self.sender.reply(f"""=======未绑定账号=====
❌ 未找到任何账号信息
💡 发送星芽登录绑定
====================""")
                return
            parts = split_accounts(users)
            self.sender.reply(f"""=======批量授权=====
📝 共找到{len(parts)}个星芽账号
💡 请输入授权月数，示例: 1
⚠️ 输入q退出操作
====================""")
            sjts = self.sender.input(60000, 1, False)
            num = 0
            success_count = 0
            if sjts == 'q' or sjts == 'Q':
                self.sender.reply("✅ 已退出授权")
                return
            elif sjts == '':
                self.sender.reply('⏰ 操作超时')
                return
            sjts = self.validate_number_input(sjts, 999)
            if sjts is None:
                return
            for phone in parts:
                if self.apply_authorization_to_phone(phone, sjts):
                    success_count += 1
                num += 1
            self.sender.reply(f"""=======授权完成=====
✅ 处理账号: {num}个
🎉 授权完成: {success_count}个
⏰ 授权时长: {sjts}月
====================""")
        elif xz == '2':
            if not self.ensure_admin_auth_ready():
                return
            # 单独授权用户
            self.sender.reply("""=======单独授权星芽=====
📝 请输入星芽手机号（私聊）
⚠️ 输入q退出操作
====================""")
            phone = self.sender.input(60000, 1, False)
            if not phone:
                self.sender.reply('⏰ 操作超时')
                return
            if phone == 'q' or phone == 'Q':
                self.sender.reply("✅ 已退出授权")
                return

            self.sender.reply("""=======单独授权星芽=====
📝 请输入授权月数，示例: 1
⚠️ 输入q退出操作
====================""")
            sjts = self.sender.input(60000, 1, False)
            num = 1
            if sjts == 'q' or sjts == 'Q':
                self.sender.reply("✅ 已退出授权")
                return
            elif sjts == '':
                self.sender.reply('⏰ 操作超时')
                return
            sjts = self.validate_number_input(sjts, 999)
            if sjts is None:
                return
            if self.apply_authorization_to_phone(phone, sjts):
                self.sender.reply("授权完成")
            else:
                self.sender.reply("授权处理结束，请检查上方提示")
if __name__ == "__main__":
    ch_xy_osname = middleware.bucketGet('ch_xy_config', 'osname') or 'ch_xy'
    # 新版统一面板配置；ch_xy_qlname 保留用于兼容旧配置
    ch_xy_panel_type = middleware.bucketGet('ch_xy_config', 'panel_type') or ''
    ch_xy_panel_config = middleware.bucketGet('ch_xy_config', 'panel_config') or ''
    ch_xy_panel_group = middleware.bucketGet('ch_xy_config', 'panel_group') or ''
    ch_xy_qlname = middleware.bucketGet('ch_xy_config', 'Qinglong')
    ch_xy_money = middleware.bucketGet('ch_xy_config', 'money') or '10'

    dl = middleware.bucketGet('ch_xy_config', 'dl') or None
    proxies = None
    is_proxy = False
    proxy_url = ""
    if dl:
        is_proxy = True
        proxy_url = dl
    xycoin = middleware.bucketGet('ch_xy_config', 'jfmoney')
    session = requests.Session()
    today_date = datetime.now().date()
    today_time = str(today_date)
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    imtype = sender.getImtype()
    usermessage = sender.getMessage()
    user = sender.getUserID()
    QLurl, qltoken = None, None
    panel_client = None

    # 创建代理管理器
    proxy_manager = ProxyManager(
        session=session,
        is_proxy=is_proxy,
        proxy_url=proxy_url,
    )
    uservalue = middleware.bucketGet("ch_xy_phone", user)
    A = Xingya(user, sender)  # 类
    if '登录' in usermessage or '登陆' in usermessage:
        A.login()
    elif 'ck提交' in usermessage or 'CK提交' in usermessage:
        A.ck_login()
    elif '教程' in usermessage:
        A.caidan()
    elif '管理' in usermessage:
        A.guanli()
    elif '查询' in usermessage:
        A.chaxun()
    elif '刷时长' in usermessage:
        A.tixian()
    elif '授权' in usermessage:
        A.shouquan()
    elif imtype == 'fake':
        # 定时任务
        # 初始化配置
        # GET请求示例
        # response = proxy_manager.get(
        #     "https://api.example.com/data",
        #     params={"page": 1},
        #     headers={"User-Agent": "MyClient"},
        #     allow_redirects=False
        # )
        #
        # # POST请求示例
        # response = proxy_manager.post(
        #     "https://api.example.com/submit",
        #     json={"payload": "data"},
        #     cookies={"session_id": "abc123"},
        #     raw=True  # 获取原始响应对象
        # )


        keys = middleware.bucketAllKeys("ch_xy_phone")
        print(f"定时任务扫描用户数: {len(keys)}")
        phones = []
        phone_owner_map = {}
        for key in keys:
            account_phones = split_accounts(middleware.bucketGet("ch_xy_phone", key))
            for account_phone in account_phones:
                if account_phone not in phone_owner_map:
                    phone_owner_map[account_phone] = key
                    phones.append(account_phone)
            print([mask_phone(phone) for phone in phones])
        retry_pending_panel_sync(ch_xy_osname, phone_owner_map)
        if phones:
            for phone in phones:
                token = middleware.bucketGet(bucket='ch_xy_token', key=phone)
                did = middleware.bucketGet(bucket='ch_xy_did', key=phone)
                accountVip = safe_str(middleware.bucketGet(bucket='ch_xy_accountvip', key=phone))
                if accountVip < today_time:
                    try:
                        qlid = allenvs(osname=ch_xy_osname, account=str(phone))
                        if qlid:
                            delenvs(id=qlid)
                    except Exception as e:
                        print(f'清理面板变量失败 {mask_phone(phone)}: {str(e)}')
                if datetime.now().time().hour >= 15 and accountVip > today_time:
                    headers = {'X-App-Id': '7', 'platform': '1', 'manufacturer': 'Xiaomi', 'version_name': '3.8.6',
                               'user_agent': 'Mozilla/5.0 (Linux; Android 15; 23127PN0CC Build/AQ3A.240627.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.86 Mobile Safari/537.36',
                               'app_version': '3.8.6', 'device_platform': 'android',
                               'personalized_recommend_status': '1', 'device_type': '23127PN0CC',
                               'device_brand': 'Xiaomi', 'os_version': '15', 'channel': 'default',
                               'raw_channel': 'default', 'uuid': 'randomUUID_799e9ea8-24e7-4cbe-aba0-bdd6fcbd8c01',
                               'device_id': did, 'ab_id': '', 'support_h265': '1', 'font_scale': '1.0',
                               'Content-Type': 'application/json; charset=utf-8', 'Content-Length': '738',
                               'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip', 'User-Agent': 'okhttp/4.10.0'}
                    timestemp = int(time.time() * 1000)
                    data = f'{{"device":"{did}","package_name":"com.jz.xydj","android_id":"1f225bd92500df96","install_first_open":false,"first_install_time":1748882426598,"last_update_time":1748882426598,"report_link_url":"","authorization":"{token}","timestamp":{timestemp}}}'

                    payload = xyauth(data)
                    max_retry = 3
                    for attempt in range(max_retry):
                        try:
                            r = proxy_manager.post(
                                "https://u.shytkjgs.com/user/v3/account/login",
                                data=payload,
                                headers=headers,
                            )


                            if r['code'] == 'ok':
                                token = r['data']['token']
                                middleware.bucketSet("ch_xy_token", phone, token)
                                newvalue = token + "#" + did
                                try:
                                    Addenvs(
                                        osname=ch_xy_osname,
                                        value=newvalue,
                                        phone=phone,
                                        owner_user=phone_owner_map.get(phone),
                                    )
                                except Exception as e:
                                    print(f'同步面板变量失败 {mask_phone(phone)}: {str(e)}')
                                time.sleep(5)
                                break  # 成功则跳出重试循环
                        except Exception as e:
                            print(f'账号备注：{mask_phone(phone)}，代理请求异常({attempt + 1}/{max_retry}): {str(e)}')
                            time.sleep(2)  # 失败后短暂等待
        # 授权查询+通知
        # def tz():
        #     a = 1
