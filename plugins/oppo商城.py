# [rule: ^([Oo][Pp][Pp][Oo]商城)(登录|登陆)$|^登(录|陆)([Oo][Pp][Pp][Oo]商城)$|^([Oo][Pp][Pp][Oo]商城)(查询|管理)$|^(查询|管理)([Oo][Pp][Pp][Oo]商城)$|^[Oo][Pp][Pp][Oo]商城清理$|^[Oo][Pp][Pp][Oo]商城授权$|^[Oo][Pp][Pp][Oo]商城教程$|^[Oo][Pp][Pp][Oo]商城通知 ?(.*)$|^清理[Oo][Pp][Pp][Oo]商城$|^[Oo][Pp][Pp][Oo]商城广播 ?(.*)$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 10 * * *]
# [public: true]
# [title: OPPO商城助手]
# [open_source: false]
# [class: 工具类]
# [version: 1.7]
# [price: 18.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: OPPO商城提交计费版 <br>1. 指令：OPPO商城登录、OPPO商城管理、OPPO商城查询、OPPO商城授权<br>2. 支持青龙呆呆面板。<br>3. 授权到期自动推送QQ/微信通知并清理系统变量。<br>4. 售后群1003974618。 售后联系：QQ 8165799<br>]

import re
import ast
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal
import requests
import time
import json
import hashlib
import logging
import base64
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('oppo_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = str(sender.getUserID())
usermessage = sender.getMessage()
try:
    current_imtype = str(sender.getImtype() or "")
except:
    current_imtype = ""
if current_imtype and current_imtype.lower() not in ["fake", "cron"]:
    try: middleware.bucketSet("dd_oppo_runtime", "sender", str(senderID))
    except: pass
    try: middleware.bucketSet("dd_oppo_runtime", "imtype", current_imtype)
    except: pass

# ===================== 插件配置参数 =====================
# [param: {"required":true,"key":"dd_oppo.panel_type","bool":false,"placeholder":"qinglong/daidai","name":"对接面板类型","desc":"qinglong=青龙面板 daidai=呆呆面板"}]
# [param: {"required":true,"key":"dd_oppo.dd_oppo_qlname","bool":false,"placeholder":"Host丨ClientID/AppKey丨Secret","name":"对接系统配置","desc":"青龙:URL丨ID丨Secret 呆呆:URL丨Key丨Secret"}]
# [param: {"required":true,"key":"dd_oppo.dd_oppo_osname","bool":false,"placeholder":"默认:OPPOCK","name":"系统变量名","desc":"系统容器内变量名(默认为OPPOCK)"}]
# [param: {"required":true,"key":"dd_oppo.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_oppo.hjVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_oppo.hjcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"dd_oppo.show_point_status","bool":true,"placeholder":"","name":"显示钱包状态","desc":"是否在查询结果中显示钱包金额"}]
# [param: {"required":true,"key":"dd_oppo.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统"}]
# [param: {"required":true,"key":"dd_oppo.enable_proxy","bool":true,"placeholder":"True/False","name":"是否启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_oppo.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_oppo.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"dd_oppo.enable_remark","bool":true,"placeholder":"True/False","name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"dd_oppo.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]
def getusercontent():
    """获取插件完整配置"""
    panel_type = middleware.bucketGet('dd_oppo', 'panel_type') or 'qinglong'
    panel_type = panel_type.lower()
    
    env_qlconfig = middleware.bucketGet('dd_oppo', 'dd_oppo_qlname') or ''
    env_name = middleware.bucketGet('dd_oppo', 'dd_oppo_osname') or 'OPPOCK'
    
    if not env_qlconfig:
        sender.reply("❌ 配置错误：请在插件配置中填写【对接系统配置】(面板信息)。")
        exit(0)
    
    dd_managecommand = middleware.bucketGet('dd_oppo', 'dd_managecommand') or 'OPPO商城管理'
    dd_querycommand = middleware.bucketGet('dd_oppo', 'dd_querycommand') or 'OPPO商城查询'
    dd_signcommand = middleware.bucketGet('dd_oppo', 'dd_signcommand') or 'OPPO商城登录'
    zsm = middleware.bucketGet('dd_oppo', 'zsm') or ''
    
    enable_remark = middleware.bucketGet('dd_oppo', 'enable_remark') or 'false'
    enable_remark = enable_remark.lower() == 'true'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    hjVipmoney = Decimal(middleware.bucketGet('dd_oppo', 'hjVipmoney') or '0')
    hjcoin = int(middleware.bucketGet('dd_oppo', 'hjcoin') or '0')
    
    use_ma_pay = middleware.bucketGet('dd_oppo', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    reminder_days = int(middleware.bucketGet('dd_oppo', 'reminder_days') or '2')
    
    points_bucket = middleware.bucketGet('dd_oppo', 'points_bucket') or 'dd_sign_points'

    return {
        'panel_type': panel_type,
        'env_name': env_name,
        'env_qlconfig': env_qlconfig,
        'dd_managecommand': dd_managecommand,
        'dd_querycommand': dd_querycommand,
        'dd_signcommand': dd_signcommand,
        'randommanagecommand': randommanagecommand,
        'randomquerycommand': randomquerycommand,
        'randomsigncommand': randomsigncommand,
        'zsm': zsm,
        'points_bucket': points_bucket,
        'enable_remark': enable_remark,
        'hjVipmoney': hjVipmoney,
        'hjcoin': hjcoin,
        'use_ma_pay': use_ma_pay,
        'reminder_days': reminder_days
    }

config = getusercontent()

def get_owner_user_id(account, fallback_userid=None):
    account = str(account or "")
    try:
        if fallback_userid and account in [str(x) for x in AccountManager.get_accounts(str(fallback_userid))]:
            return str(fallback_userid)
    except:
        pass
    try:
        for frame_info in __import__('inspect').stack()[1:6]:
            local_vars = frame_info.frame.f_locals
            for key in ['owner_user_id', 'target_userid', 'target_qq', 'target_user', 'user', 'uid']:
                candidate = local_vars.get(key)
                if not candidate:
                    continue
                candidate = str(candidate)
                try:
                    if account in [str(x) for x in AccountManager.get_accounts(candidate)]:
                        return candidate
                except:
                    pass
    except:
        pass
    try:
        for owner in middleware.bucketAllKeys(bucket='dd_oppo_user'):
            try:
                if account in [str(x) for x in AccountManager.get_accounts(owner)]:
                    return str(owner)
            except:
                pass
    except:
        pass
    try:
        if not sender.isAdmin() and str(userid):
            return str(userid)
    except:
        pass
    return 

# ===================== 辅助工具函数 =====================
def send_user_notice(user_id, msg, title="OPPO商城通知"):
    user_id = str(user_id or "").strip()
    if not user_id:
        return False
    imtype = ""
    try:
        imtype = str(sender.getImtype() or "")
    except:
        pass
    if not imtype or imtype.lower() in ["fake", "cron"]:
        imtype = middleware.bucketGet("dd_oppo_runtime", "imtype") or ""
    try:
        if imtype:
            middleware.Push(imtype, "", user_id, title, msg)
            return True
    except Exception as e:
        logger.warning(f"Push发送失败 {user_id}: {e}")
    return False

def safe_send_message(user_id, msg, log_context=""):
    ok = send_user_notice(user_id, msg)
    if not ok:
        logger.warning(f"消息发送失败 {log_context}")
    return ok

def empower(empowertime, days):
    try:
        today_date = datetime.now().date()
        if not empowertime or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            delayed_date = empower_date + timedelta(days=days)
        return str(delayed_date)
    except Exception as e:
        logger.error(f"授权时间计算失败: {e}")
        raise Exception(f"授权时间计算失败: {e}")

def encrypt_token(token):
    try:
        return base64.b64encode(token.encode()).decode()
    except:
        return token

def decrypt_token(encrypted_token):
    try:
        return base64.b64decode(encrypted_token.encode()).decode()
    except:
        return encrypted_token

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='dd_oppo_remarks', key=f'{user_id}_{account_id}')
            return str(remark_data) if remark_data else ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = str(remark).strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='dd_oppo_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
                return remark_clean
            return ""
        except: return ""
    
    @staticmethod
    def get_all_remarks(user_id):
        try:
            accounts = AccountManager.get_accounts(user_id)
            remarks = {}
            for account in accounts:
                remark = RemarkManager.get_account_remark(user_id, account)
                if remark: remarks[str(account)] = remark
            return remarks
        except: return {}
    
    @staticmethod
    def delete_account_remark(user_id, account_id):
        try:
            middleware.bucketDel(bucket='dd_oppo_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket='dd_oppo_user', key=str(user_id))
            if not value: return []
            if value.startswith('[') and value.endswith(']'):
                try:
                    accounts = ast.literal_eval(value)
                    if isinstance(accounts, (list, tuple, set)):
                        return [str(x) for x in list(dict.fromkeys(accounts))]
                except: pass
            return [str(value)]
        except: return []

    @staticmethod
    def add_account(user_id, account):
        try:
            account = str(account)
            accounts = AccountManager.get_accounts(user_id)
            if account not in accounts:
                accounts.append(account)
                middleware.bucketSet(bucket='dd_oppo_user', key=str(user_id), value=str(accounts))
                return True
            return False
        except: return False
    
    @staticmethod
    def remove_account(user_id, account):
        try:
            account = str(account)
            accounts = AccountManager.get_accounts(user_id)
            if account in accounts:
                accounts.remove(account)
                if accounts:
                    middleware.bucketSet(bucket='dd_oppo_user', key=str(user_id), value=str(accounts))
                else:
                    middleware.bucketDel(bucket='dd_oppo_user', key=str(user_id))
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(account, token):
        try:
            encrypted_token = encrypt_token(str(token))
            middleware.bucketSet(bucket='dd_oppo_token', key=str(account), value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_token(account):
        try:
            enc = middleware.bucketGet(bucket='dd_oppo_token', key=str(account))
            return decrypt_token(enc) if enc else None
        except: return None

    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket='dd_oppo_user')
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts: user_list.append(str(user))
            return user_list
        except: return []

# ===================== 系统对接模块(青龙/呆呆) =====================
class SystemAPI:
    def __init__(self):
        self.enabled = False
        self.panel_type = config.get('panel_type', 'qinglong')
        ql_config = config['env_qlconfig']
        try:
            if not ql_config: raise ValueError("对接配置为空")
            qllist = ql_config.split('丨')
            if len(qllist) != 3: raise ValueError("对接配置格式错误")
            self.QLurl = qllist[0].strip().rstrip('/')
            self.ClientID = qllist[1].strip()
            self.ClientSecret = qllist[2].strip()
            
            if self.panel_type == 'daidai':
                self.access_token = self._get_daidai_token()
            else:
                self.qltoken = self._get_ql_token()
            self.enabled = True
        except Exception as e:
            logger.error(f"系统初始化失败: {e}")
    
    def _get_ql_token(self):
        try:
            url = f"{self.QLurl}/open/auth/token?client_id={self.ClientID}&client_secret={self.ClientSecret}"
            response = requests.get(url, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()['data']['token']
            raise Exception("获取青龙Token失败")
        except Exception as e: raise

    def _get_daidai_token(self):
        try:
            url = f"{self.QLurl}/api/open-api/token"
            data = {"app_key": self.ClientID, "app_secret": self.ClientSecret}
            response = requests.post(url, json=data, timeout=10, verify=False)
            if response.status_code == 200:
                return response.json()['data']['access_token']
            raise Exception("获取呆呆Token失败")
        except Exception as e: raise
    
    def get_all_envs(self):
        if not self.enabled: return []
        try:
            if self.panel_type == 'daidai':
                url = f"{self.QLurl}/api/envs?keyword={config['env_name']}&page_size=9999"
                headers = {"Authorization": f"Bearer {self.access_token}", "accept": "application/json"}
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                if response.status_code == 200: 
                    return response.json().get('data', [])
                return []
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "accept": "application/json"}
                response = requests.get(url, headers=headers, timeout=10, verify=False)
                if response.status_code == 200: 
                    return response.json()['data']
                return []
        except: return []
   
    def find_env(self, phone, token=None):
        if not self.enabled: return None
        phone = str(phone)
        try:
            envs = self.get_all_envs()
            for env in envs:
                if env.get('name') != config['env_name']: continue
                env_id = env.get('id') if env.get('id') is not None else env.get('_id')
                if env.get('remarks') and f'ID:{phone}' in env.get('remarks'): 
                    return env_id
                if env.get('remarks') and phone in env.get('remarks'):
                    return env_id
            return None
        except: return None
    
    def delete_env(self, phone):
        if not self.enabled: return False
        phone = str(phone)
        try:
            env_id = self.find_env(phone)
            if env_id is None: return False
            if self.panel_type == 'daidai':
                url = f"{self.QLurl}/api/envs/{env_id}"
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                requests.delete(url, headers=headers, timeout=10, verify=False)
            else:
                url = f"{self.QLurl}/open/envs"
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                requests.delete(url, headers=headers, json=[env_id], timeout=10, verify=False)
            return True
        except: return False
    
    def sync_env(self, token, phone, remark="", auth_time="", owner_user_id=None):
        if not self.enabled: return False
        phone = str(phone)
        try:
            env_id = self.find_env(phone, token)
            ql_value = str(token).strip()
            
            safe_phone = phone[:3] + "****" + phone[-4:] if len(phone) >= 11 else phone[:2] + "***"
            remarks_parts = [f'OPPO:{safe_phone}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{phone}', 'OPPO商城提交'])
            final_remark = '丨'.join(remarks_parts)

            if self.panel_type == 'daidai':
                headers = {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}
                if env_id is not None:
                    url = f"{self.QLurl}/api/envs/{env_id}"
                    data = {"name": config['env_name'], "value": ql_value, "remarks": final_remark}
                    res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code == 200:
                        try: requests.put(f"{self.QLurl}/api/envs/{env_id}/enable", headers=headers, timeout=5, verify=False)
                        except: pass
                    else: return False
                else:
                    url = f"{self.QLurl}/api/envs"
                    data = {"name": config['env_name'], "value": ql_value, "remarks": final_remark}
                    res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code != 200: return False
            else:
                headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
                url = f"{self.QLurl}/open/envs"
                if env_id is not None:
                    data = {"value": ql_value, "name": config['env_name'], "remarks": final_remark}
                    if isinstance(env_id, int) or str(env_id).isdigit():
                        data["id"] = env_id
                    else:
                        data["_id"] = env_id
                        
                    res = requests.put(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code == 200:
                        try: requests.put(f"{self.QLurl}/open/envs/enable", headers=headers, json=[env_id], timeout=5, verify=False)
                        except: pass
                    else: return False
                else:
                    data = [{"value": ql_value, "name": config['env_name'], "remarks": final_remark}]
                    res = requests.post(url, headers=headers, json=data, timeout=10, verify=False)
                    if res.status_code != 200: return False
            return True
        except Exception as e: 
            logger.error(f"Sync Env Error: {e}")
            return False

try:
    sys_api = SystemAPI()
except:
    sys_api = type('obj', (object,), {'enabled': False, 'sync_env': lambda *a, **k: None, 'delete_env': lambda *a, **k: None})()

def parse_panel_oppo_remark(remarks):
    info = {"user": "", "account": "", "auth": "", "remark": ""}
    for part in re.split(r"[丨|,，\s]+", str(remarks or "")):
        part = part.strip()
        if not part:
            continue
        if part.startswith("用户:"):
            info["user"] = part.split(":", 1)[1].strip()
        elif part.startswith("ID:"):
            info["account"] = part.split(":", 1)[1].strip()
        elif part.startswith("到期:"):
            info["auth"] = part.split(":", 1)[1].strip()
        elif part.startswith("备注:"):
            info["remark"] = part.split(":", 1)[1].strip()[:20]
    return info

def sync_local_auth_from_panel():
    logger.info("面板反向同步本地归属已禁用，跳过以保护本地数据")
    return {'scanned': 0, 'synced': 0, 'failed': 0, 'disabled': True}
    if not getattr(sys_api, "enabled", False):
        return {"synced": 0, "failed": 0}
    synced = 0
    failed = 0
    try:
        envs = sys_api.get_all_envs()
    except Exception as e:
        logger.warning(f"读取面板环境失败: {e}")
        return {"synced": 0, "failed": 1}
    for env in envs or []:
        try:
            if env.get("name") != config["env_name"]:
                continue
            token = str(env.get("value") or "").strip()
            if not token:
                continue
            info = parse_panel_oppo_remark(env.get("remarks", ""))
            user = info.get("user")
            account = info.get("account")
            if not user or not account:
                continue
            existing_owner = get_owner_user_id(account, '')
            if existing_owner and existing_owner != str(user):
                logger.warning(f"跳过面板反向同步：账号 {account} 本地归属 {existing_owner}，面板备注归属 {user}")
                continue
            AccountManager.add_account(user, account)
            AccountManager.update_account_token(account, token)
            auth_time = info.get("auth")
            if auth_time and auth_time not in ["未授权", "无"] and re.fullmatch(r"\d{4}-\d{2}-\d{2}", auth_time):
                middleware.bucketSet("dd_oppo_auth", account, auth_time)
            if config["enable_remark"] and info.get("remark"):
                RemarkManager.set_account_remark(user, account, info.get("remark"))
            synced += 1
        except Exception as e:
            failed += 1
            logger.warning(f"同步OPPO面板数据失败: {e}")
    return {"synced": synced, "failed": failed}

# ===================== 核心查询类 =====================
class OPPOClient:
    def __init__(self, token_str):
        self.token = token_str
        self.base_url = "https://store.oppo.com"
        
        self.headers = {
            "Host": "store.oppo.com",
            "Connection": "keep-alive",
            "source-type": "501",
            "client-type": "1",
            "Accept": "application/json, text/plain, */*",
            "xweb_xhr": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a1b) UnifiedPCWindowsWechat(0xf254181c) XWEB/11253",
            "Content-Type": "application/x-www-form-urlencoded",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://store.oppo.com/cn/m/task/center/index?clearance=1",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": f"NEWOPPOSID={self.token}"
        }

    def get_points(self):
        """实时拉取积分余额"""
        url = f"{self.base_url}/api/mobile/account/user/credits"
        try:
            res = requests.get(url, headers=self.headers, verify=False, timeout=10)
            rj = res.json()
            if rj.get("code") == 0:
                return str(rj.get("data", {}).get("credits", "0"))
            else:
                msg = rj.get('msg') or '未知错误'
                if is_definitive_oppo_auth_failure(msg):
                    return f"失效({msg})"
                return f"接口异常({msg})"
        except Exception as e:
            return "服务挂机中请自行去小程序查询"

def is_definitive_oppo_auth_failure(message):
    text = str(message or "").lower()
    keywords = [
        "登录失效", "登录过期", "token过期", "token失效", "token无效",
        "未登录", "请登录", "sid失效", "cookie失效", "unauthorized",
        "invalid token", "expired token"
    ]
    return any(keyword in text for keyword in keywords)

# ===================== 功能逻辑 =====================

def process_single_account_query(account, index, total_count, account_remarks):
    try:
        account = str(account)
        full_token = AccountManager.get_token(account)
        if not full_token: full_token = ""
        
        accountVip = middleware.bucketGet(bucket='dd_oppo_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        if not accountVip:
            auth_time = "无"
        elif accountVip <= today_time:
            auth_time = f"{accountVip} (已过期)"
        else:
            auth_time = accountVip

        safe_display = account[:3] + "****" + account[-4:] if len(account) >= 11 else account[:2] + "***"
        remark_display = f" [{remark}]" if remark else ""

        if accountVip and accountVip > today_time and full_token:
            client = OPPOClient(full_token)
            points = client.get_points()
            
            account_info = f"""
=====OPPO商城详情=====
🚀 平台: OPPO商城 (小程序)
📱 绑定手机: {safe_display}{remark_display}
💰 当前积分: {points}
⏰ 授权到期: {auth_time}"""
            return account_info.strip()
        else:
            return f"""
=====OPPO商城状态=====
📝 备注: {remark if remark else "账号"+str(index)}
📱 手机: {safe_display}
🔐 授权: {'⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')}
⏰ 到期: {auth_time}
=================="""
    except Exception:
        return None

def cxs():
    try:
        accounts = AccountManager.get_accounts(userid)
        if not accounts:
            sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {config['randomsigncommand']} 绑定
==================""")
            return

        account_remarks = {}
        if config['enable_remark']:
            account_remarks = RemarkManager.get_all_remarks(userid)

        total_count = len(accounts)
        today_time = str(datetime.now().date())

        menu = "=====OPPO商城查询====="
        for i, acc in enumerate(accounts, 1):
            acc = str(acc)
            remark = account_remarks.get(acc, "") if config['enable_remark'] else ""
            safe_acc = acc[:3] + "****" + acc[-4:] if len(acc) >= 11 else acc[:2] + "***"
            vip = middleware.bucketGet(bucket='dd_oppo_auth', key=acc)
            if not vip:
                vip_tag = '⚠️未授权'
            elif vip < today_time:
                vip_tag = '❌已过期'
            else:
                vip_tag = f'✅{vip}'
            remark_disp = f" [{remark}]" if remark else ""
            menu += f"\n[{i}] {safe_acc}{remark_disp} {vip_tag}"
        menu += f"\n------------------\n[a] 查询全部\n回复数字单独查询\n回复q退出\n=================="
        sender.reply(menu)

        sel = get_user_input(timeout=60)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已退出")
            return

        if sel.lower() == 'a':
            target_accounts = list(enumerate(accounts, 1))
        else:
            try:
                idx = int(sel)
                if idx < 1 or idx > total_count:
                    sender.reply("❌ 序号无效")
                    return
                target_accounts = [(idx, accounts[idx - 1])]
            except:
                sender.reply("❌ 请输入有效数字或 a")
                return

        sender.reply(f"🚀 正在提取 {len(target_accounts)} 个账号信息，请稍候...")
        max_workers = min(10, len(target_accounts))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_account = {}
            for index, account in target_accounts:
                future = executor.submit(process_single_account_query, account, index, total_count, account_remarks)
                future_to_account[future] = account

            for future in as_completed(future_to_account):
                result_msg = future.result()
                if result_msg: sender.reply(result_msg)

    except Exception as e:
        logger.error(f"批量查询失败: {e}")
        sender.reply(f"❌ 查询失败: {e}")

def notify_authorized_users():
    if not sender.isAdmin():
        sender.reply("❌ 只有管理员可以使用此功能")
        return
    
    content = ""
    msg_upper = usermessage.upper() if usermessage else ""
    # 兼容大小写正则提取
    match = re.search(r'([Oo][Pp][Pp][Oo]商城广播|[Oo][Pp][Pp][Oo]商城通知) ?(.*)', usermessage, re.IGNORECASE)
    if match:
        content = match.group(2).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：OPPO商城通知 系统维护中")
        return
        
    sender.reply("⏳ 正在扫描授权用户并发送通知...")
    
    try:
        sync_result = sync_local_auth_from_panel()
        all_users = AccountManager.get_all_users()
        success_count = 0
        today = str(datetime.now().date())
        
        for uid in all_users:
            user_accounts = AccountManager.get_accounts(uid)
            has_auth = False
            for acc in user_accounts:
                vip_date = middleware.bucketGet(bucket='dd_oppo_auth', key=str(acc))
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                if send_user_notice(uid, f"📢 【OPPO商城通知】\n\n{content}", "OPPO商城通知"):
                    success_count += 1
                    time.sleep(0.1)
        
        sender.reply(f"✅ 通知完成\n📢 已送达: {success_count} 人\n🔄 面板同步: {sync_result.get('synced', 0)} 条")
    except: pass

def get_user_input(timeout=60):
    try:
        response = sender.listen(timeout * 1000)
        if not response: return None
        response = response.strip()
        if response.lower() in ['q', 'quit', 'exit', '退出', 'cancel']: return 'q'
        return response
    except: return None

def bindaccount():
    try:
        remark = ""
        if config['enable_remark']:
            sender.reply("=====账号备注设置=====\n🎯 请输入账号备注名\n(批量提交时此备注将应用到所有账号)\n------------------\n回复备注名继续\n回复\"n\"跳过备注\n回复\"q\"退出操作\n==================")
            remark_input = get_user_input(timeout=120)
            if remark_input == 'q': return
            elif remark_input != 'n' and remark_input: remark = remark_input.strip()[:20]
        
        sender.reply(f"""=====OPPO商城 登录=====
👉 必须带上手机号录入，格式如下：
------------------
格式：手机号#Token
示例：13800000000#eyJpdiI...
------------------
支持批量提交，一行一个
⚠️ 系统以此手机号为主键，实现无损平滑更新!
------------------
回复"q"退出操作
==================""")
        
        input_str = get_user_input(timeout=120)
        if not input_str or input_str.lower() == 'q': return
        
        token_lines = [line.strip() for line in input_str.split('\n') if line.strip()]
        if not token_lines: return
        
        sender.reply(f"⏳ 正在物理入库 {len(token_lines)} 个账号，请稍候...")
        
        for line in token_lines:
            try:
                val = line.strip()
                if '#' not in val:
                    sender.reply(f"❌ 格式错误: 缺少手机号前缀！请按照 手机号#Token 的格式发送。")
                    continue
                
                parts = val.split('#')
                phone = parts[0].strip()
                token_val = parts[1].strip()
                
                if len(phone) < 11:
                    sender.reply(f"❌ 格式错误: 手机号长度不正确！")
                    continue
                
                # 吸尘器：无论Token被加了什么前缀后缀，强行提取 eyJ
                match = re.search(r'(eyJ[a-zA-Z0-9_+=/]+)', token_val)
                if match:
                    token_val = match.group(1)
                
                # 断开网络校验，直接入库！
                process_account_binding(token_val, phone, f"OPPO_{phone[-4:]}", remark) 
            except Exception as ex:
                sender.reply(f"❌ 录入失败: {str(ex)}")
            
    except Exception as e:
        sender.reply(f"❌ 绑定失败: {e}")

def process_account_binding(full_token, unique_id, nickname, remark=""):
    try:
        account = str(unique_id)
        accountVip = middleware.bucketGet(bucket='dd_oppo_auth', key=account)
        today_time = str(datetime.now().date())
       
        is_authorized = False
        if accountVip and accountVip >= today_time:
            is_authorized = True
            auth_status = f'✅ 已授权 ({accountVip})'
            next_step = f'发送 {config["randommanagecommand"]} 可管理账号'
        else:
            auth_status = '⚠️ 未授权'
            next_step = f'发送 {config["randommanagecommand"]} 进行授权'
        
        remark_info = f"\n📝 备注: {remark}" if remark else ""
        safe_display = account[:3] + "****" + account[-4:] if len(account) >= 11 else account[:2] + "***"

        is_new = AccountManager.add_account(userid, account)
        if is_new:
            try: middleware.bucketSet(bucket='dd_oppo_bind_date', key=account, value=str(datetime.now().date()))
            except: pass
        AccountManager.update_account_token(account, full_token)
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account, remark)
        
        ql_msg = ""
        if is_authorized:
            if sys_api.sync_env(full_token, account, remark, accountVip):
                ql_msg = "\n🌐 状态: ✅ 系统已同步更新"
            else:
                ql_msg = "\n🌐 状态: ❌ 系统同步失败"
        else:
            ql_msg = "\n🌐 状态: ⏸️ 未授权暂不同步"

        sender.reply(f"=====OPPO商城账号更新=====\n✅ 处理成功!\n👤 用户: {nickname}\n📱 账号: {safe_display}{remark_info}\n🔐 授权: {auth_status}{ql_msg}\n⏰ 下一步操作: \n   {next_step}\n==================")
    except: pass

# ===================== 支付与管理 =====================
def xy_manage():
    accounts = AccountManager.get_accounts(userid)
    if not accounts:
        sender.reply(f"❌ 未找到账号，请发送 {config['randomsigncommand']} 绑定")
        return
    
    account_remarks = RemarkManager.get_all_remarks(userid) if config['enable_remark'] else {}
    count = 1
    account_list = "======我的OPPO商城账号====="
    today_time = str(datetime.now().date())
    
    for account in accounts:
        account = str(account)
        accountVip = middleware.bucketGet(bucket='dd_oppo_auth', key=account)
        if not accountVip: vip_status = '⚠️ 未授权'
        elif accountVip < today_time: vip_status = '❌ 已过期'
        else: vip_status = f'✅ {accountVip}'
        
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        remark_display = f" - {remark}" if remark else ""
        
        safe_display = account[:3] + "****" + account[-4:] if len(account) >= 11 else account[:2] + "***"
        
        account_list += f"\n------------------\n[{count}] 账号: {safe_display}{remark_display}\n🔐 授权: {vip_status}"
        count += 1
        
    account_list += "\n------------------\n[b] 批量授权\n[d] 批量删除\n[q] 退出管理\n=================="
    sender.reply(account_list)
    
    response = get_user_input()
    if not response or response == 'q':
        sender.reply('✅ 已退出')
        return
    
    if response.lower() == 'b':
        batch_auth_all_accounts(accounts, account_remarks)
        return
    elif response.lower() == 'd':
        batch_delete_all_accounts(accounts)
        return
    
    try:
        choice_num = int(response)
        if 1 <= choice_num < count:
            manage_single_account(str(accounts[choice_num - 1]), account_remarks)
        else:
            sender.reply('❌ 序号无效')
    except:
        sender.reply('❌ 输入必须是数字')

def manage_single_account(account, account_remarks):
    try:
        account = str(account)
        token = AccountManager.get_token(account)
        if not token: token = ""
        accountVip = middleware.bucketGet(bucket='dd_oppo_auth', key=account)
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        safe_display = account[:3] + "****" + account[-4:] if len(account) >= 11 else account[:2] + "***"
        
        menu_items = "[1] 授权账号\n[2] 删除账号\n[3] 修改备注"
        sender.reply(f"=====账号详情=====\n📱 账号: {safe_display}\n📝 备注: {remark}\n🔐 授权: {vip_status}\n==================\n{menu_items}\n------------------\n回复数字选择，Q退出\n==================")
        
        choice = get_user_input()
        if not choice or choice == 'q': return
        
        if choice == '1':
            sender.reply("请输入授权月数(如:1)，Q退出")
            months_str = get_user_input()
            if not months_str or months_str == 'q': return
            try:
                months = int(months_str)
                if months <= 0: raise ValueError
            except:
                sender.reply("❌ 数字无效")
                return
            
            if process_payment('OPPO商城授权', months, accountVip, token, account, remark):
                try:
                    days = months * 30
                    new_auth_time = empower(accountVip, days)
                    try: middleware.bucketSet(bucket='dd_oppo_auth', key=account, value=new_auth_time)
                    except: pass

                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel(bucket='dd_oppo_remind_log', key=remind_key)
                        except: pass

                    if token:
                        sys_api.sync_env(token, account, remark, new_auth_time)
                        sender.reply("🔄 授权成功并同步到系统！")
                    else:
                        sender.reply("✅ 授权成功")

                    money = Decimal(months) * config['hjVipmoney']
                    sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")
                except Exception as ex:
                    sender.reply(f"❌ 授权后续写入异常: {ex}")

        elif choice == '2':
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                try:
                    AccountManager.remove_account(userid, account)
                    try: middleware.bucketDel(bucket='dd_oppo_token', key=account)
                    except: pass
                    try: middleware.bucketDel(bucket='dd_oppo_auth', key=account)
                    except: pass
                    if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                    sys_api.delete_env(account)
                    today_date = datetime.now().date()
                    for d in range(config['reminder_days'] + 1):
                        remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                        try: middleware.bucketDel(bucket='dd_oppo_remind_log', key=remind_key)
                        except: pass
                    sender.reply("✅ 删除成功")
                except Exception as ex:
                    sender.reply(f"❌ 删除异常: {ex}")

        elif choice == '3':
             sender.reply("请输入新备注:")
             new_remark = get_user_input()
             if new_remark and new_remark != 'q':
                 RemarkManager.set_account_remark(userid, account, new_remark)
                 if token:
                     sys_api.sync_env(token, account, new_remark, accountVip)
                 sender.reply("✅ 备注更新成功")

    except Exception as e:
        sender.reply(f"操作失败: {e}")

def process_payment(project, months, accountVip, token, account, remark=""):
    money = Decimal(months) * config['hjVipmoney']
    points_needed = config['hjcoin'] * months
    user_points = int(middleware.bucketGet(config['points_bucket'], userid) or '0')
    
    options = []
    idx = 1
    if config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '微信支付', 'amount': money})
        idx += 1
    if config['use_ma_pay']:
        ma_conf = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch'),
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key')
        }
        if ma_conf['switch'] == 'true':
            options.append({'id': idx, 'type': 'ma', 'name': '码支付', 'amount': money, 'conf': ma_conf})
            idx += 1
    if config['hjcoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': points_needed, 'curr': user_points})
    
    if not options:
        sender.reply("❌ 未配置支付方式")
        return False

    msg = "=====选择支付方式====="
    for opt in options:
        amount_str = f"{opt['amount']}积分" if opt['type'] == 'pt' else f"{opt['amount']}元"
        suffix = f" (当前拥有: {opt['curr']})" if opt['type'] == 'pt' else ""
        msg += f"\n[{opt['id']}] {opt['name']} ({amount_str}){suffix}"
    msg += "\n回复数字选择，Q退出"
    sender.reply(msg)
    
    sel = get_user_input()
    if not sel or sel == 'q': return False

    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError

        if opt['type'] == 'wx':
            if sender.atWaitPay():
                sender.reply("⚠️ 当前有人支付中")
                return False
            sender.reply(f"=====微信扫码=====\n金额: {opt['amount']}元")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            if str(res) == 'q': return False
            
            try:
                if isinstance(res, dict):
                    Money = float(res.get('Money', res.get('money', 0)))
                    From = res.get('FromName', res.get('fromName', ''))
                else:
                    try:
                        res_json = json.loads(res)
                        Money = float(res_json.get('Money', res_json.get('money', 0)))
                        From = res_json.get('FromName', res_json.get('fromName', ''))
                    except:
                        sender.reply("❌ 无法解析支付结果")
                        return False
                
                if float(Money) >= float(money):
                    return True
                else:
                    sender.reply(f"=====支付金额错误=====\n💰 应付: {money}元\n💳 实付: {Money}元\n👤 付款人: {From}\n❗ 请联系管理员处理退款！")
                    return False
            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                return False

        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply("❌ 积分不足")
                return False
            sender.reply("确认支付回复【y】")
            if get_user_input() == 'y':
                new_pt = int(opt['curr']) - int(opt['amount'])
                try:
                    middleware.bucketSet(config['points_bucket'], userid, str(new_pt))
                except Exception as e:
                    sender.reply(f"❌ 扣除积分失败: {e}")
                    return False
                return True
            return False

        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"OPPO_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"OPPO商城授权-{months}月",
                'money': str(opt['amount']),
                'notify_url': '', 'return_url': '', 'param': userid
            }
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + conf['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            url = conf['gateway'].rstrip('/') + '/submit.php'
            res = requests.post(url, data=params, timeout=10)
            if 'http' in res.text:
                sender.reply("请完成支付后联系管理员手动授权")
            else:
                sender.reply("❌ 创建订单失败")
            return False

    except:
        sender.reply("❌ 支付异常")
        return False

def batch_auth_all_accounts(accounts, account_remarks):
    sender.reply("请输入授权月数，Q退出")
    m = get_user_input()
    if not m or not m.isdigit(): return
    months = int(m)
    if months <= 0: return
    
    count = len(accounts)
    total_money = Decimal(months) * config['hjVipmoney'] * count
    total_points = config['hjcoin'] * months * count
    user_points = int(middleware.bucketGet(config['points_bucket'], userid) or '0')

    options = []
    idx = 1
    if config['zsm']:
        options.append({'id': idx, 'type': 'wx', 'name': '微信支付', 'amount': total_money})
        idx += 1
    if config['use_ma_pay']:
        ma_conf = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch'),
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key')
        }
        if ma_conf['switch'] == 'true':
            options.append({'id': idx, 'type': 'ma', 'name': '码支付', 'amount': total_money, 'conf': ma_conf})
            idx += 1
    
    if config['hjcoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': total_points, 'curr': user_points})

    if not options:
        sender.reply("❌ 未配置支付方式")
        return

    msg = f"=====批量授权确认=====\n👥 账号数量: {count}个\n📅 授权时长: {months}个月\n💰 总需金额: {total_money}元\n💎 总需积分: {total_points}"
    msg += "\n------------------"
    for opt in options:
        amount_str = f"{opt['amount']}积分" if opt['type'] == 'pt' else f"{opt['amount']}元"
        suffix = f" (当前: {opt['curr']})" if opt['type'] == 'pt' else ""
        msg += f"\n[{opt['id']}] {opt['name']} ({amount_str}){suffix}"
    msg += "\n------------------\n回复数字选择，Q退出\n=================="
    
    sender.reply(msg)

    sel = get_user_input()
    if not sel or sel == 'q': return

    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError

        if opt['type'] == 'wx':
            if sender.atWaitPay(): 
                sender.reply("⚠️ 当前有人支付中")
                return
            sender.reply(f"=====微信扫码=====\n金额: {opt['amount']}元")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            if str(res) == 'q': return
            
            try:
                if isinstance(res, dict): Money = float(res.get('Money', res.get('money', 0)))
                else: Money = float(json.loads(res).get('Money', 0))
                if float(Money) < float(opt['amount']): return sender.reply("支付金额错误！")
            except: return
        
        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply(f"❌ 积分不足，需要 {opt['amount']}，当前 {opt['curr']}")
                return
            sender.reply(f"确认消耗 {opt['amount']} 积分？回复【y】")
            if get_user_input() != 'y': return
            new_pt = int(opt['curr']) - int(opt['amount'])
            try: middleware.bucketSet(config['points_bucket'], userid, str(new_pt))
            except Exception as e:
                sender.reply(f"❌ 积分扣除异常: {e}")
                return

        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"OPPO_BATCH_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"OPPO商城批量-{count}号-{months}月",
                'money': str(opt['amount']),
                'notify_url': '', 'return_url': '', 'param': userid
            }
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            sign = hashlib.md5((sign_str + conf['key']).encode()).hexdigest().lower()
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            url = conf['gateway'].rstrip('/') + '/submit.php'
            res = requests.post(url, data=params, timeout=10)
            if 'http' in res.text:
                sender.reply("请完成支付后联系管理员")
            else:
                sender.reply("❌ 创建订单失败")
            return

    except Exception:
        sender.reply("❌ 输入错误或支付取消")
        return

    sender.reply(f"🚀 支付成功，正在处理 {count} 个账号...")
    for account in accounts:
        try:
            account = str(account)
            accountVip = middleware.bucketGet(bucket='dd_oppo_auth', key=account)
            new_date = empower(accountVip, months*30)
            try: middleware.bucketSet('dd_oppo_auth', account, new_date)
            except: pass

            token = AccountManager.get_token(account)
            curr_remark = account_remarks.get(account, "") if account_remarks else ""

            if token:
                sys_api.sync_env(token, account, curr_remark, new_date)

            today_date = datetime.now().date()
            for d in range(config['reminder_days'] + 1):
                remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                try: middleware.bucketDel(bucket='dd_oppo_remind_log', key=remind_key)
                except: pass
        except: pass

    sender.reply("✅ 批量授权完成")

def batch_delete_all_accounts(accounts):
    sender.reply("确认删除回复【确认删除】")
    if get_user_input() == "确认删除":
        today_date = datetime.now().date()
        for account in accounts:
            try:
                 account = str(account)
                 AccountManager.remove_account(userid, account)
                 try: middleware.bucketDel(bucket='dd_oppo_token', key=account)
                 except: pass
                 try: middleware.bucketDel(bucket='dd_oppo_auth', key=account)
                 except: pass
                 if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                 sys_api.delete_env(account)
                 for d in range(config['reminder_days'] + 1):
                     remind_key = f"{userid}_{account}_{today_date - timedelta(days=d)}"
                     try: middleware.bucketDel(bucket='dd_oppo_remind_log', key=remind_key)
                     except: pass
            except: pass
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts():
    sync_result = sync_local_auth_from_panel()
    users = middleware.bucketAllKeys(bucket='dd_oppo_user')
    msg_upper = usermessage.upper() if usermessage else ""
    
    if not users:
        if sender.isAdmin() and msg_upper in ['OPPO商城清理', '清理OPPO商城']:
            sender.reply(f"=====执行结果=====\n📭 暂无用户数据\n🔄 面板同步: {sync_result.get('synced', 0)} 条")
        return

    if sender.isAdmin() and msg_upper in ['OPPO商城清理', '清理OPPO商城']:
        sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n⚙️ 提醒天数: {config['reminder_days']}天\n⏳ 处理中...")

    cleaned_count = 0
    reminded_count = 0
    ck_expired_count = 0
    today_date = datetime.now().date()
    reminder_days_cfg = config['reminder_days']

    for user in users:
        try:
            accounts = AccountManager.get_accounts(user)
            if not accounts: continue
            
            valid_accounts = []
            user_has_change = False

            for account in accounts:
                account = str(account)
                accountVip = middleware.bucketGet(bucket='dd_oppo_auth', key=account)
                if not accountVip: continue
                
                try:
                    expiration_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                    expiration_str = accountVip
                except:
                    expiration_date = today_date - timedelta(days=1)
                    expiration_str = "日期错误"

                days_diff = (expiration_date - today_date).days
                safe_display = account[:3] + "****" + account[-4:] if len(account) >= 11 else account[:2] + "***"

                # 授权内：验证CK是否失效 + 判断是否临期
                if days_diff >= 0:
                    valid_accounts.append(account)
                    
                    encrypted_token = middleware.bucketGet(bucket='dd_oppo_token', key=account)
                    token = decrypt_token(encrypted_token) if encrypted_token else None
                    is_ck_valid = True
                    
                    if token:
                        invalid_remind_key = f"invalid_ck_{user}_{account}_{today_date}"
                        if not middleware.bucketGet('dd_oppo_remind_log', invalid_remind_key):
                            client = OPPOClient(token)
                            points = client.get_points()
                            if "失效" in points:
                                is_ck_valid = False
                                msg = f"=====⚠️ 账号失效提醒=====\n您的OPPO商城账号授权仍在有效期内，但登录凭证(Token)已失效！\n📱 手机: {safe_display}\n\n请尽快重新抓包并发送 {config['randomsigncommand']} 重新录入，以免影响挂机收益。"
                                if safe_send_message(user, msg, f"CK失效提醒 {user}-{account}"):
                                    middleware.bucketSet('dd_oppo_remind_log', invalid_remind_key, "1")
                                    ck_expired_count += 1
                    
                    # 只有在CK没失效的前提下，触发即将到期提醒
                    if is_ck_valid and 0 <= days_diff <= reminder_days_cfg:
                        remind_key = f"{user}_{account}_{today_date}"
                        has_reminded = middleware.bucketGet('dd_oppo_remind_log', remind_key)
                        
                        if not has_reminded:
                            msg = f"=====⏰ 到期提醒=====\n您的小程序账号授权即将到期！\n📱 手机: {safe_display}\n📅 到期: {expiration_str} (剩余 {days_diff} 天)\n为避免影响挂机，请及时续费。"
                            if safe_send_message(user, msg, f"到期提醒 {user}-{account}"):
                                middleware.bucketSet('dd_oppo_remind_log', remind_key, "1")
                                reminded_count += 1
                    continue

                # 过期清理逻辑
                if days_diff < 0:
                    try:
                        sys_api.delete_env(account)
                        try: middleware.bucketDel(bucket='dd_oppo_token', key=account)
                        except: pass
                        try: middleware.bucketDel(bucket='dd_oppo_auth', key=account)
                        except: pass
                        if config['enable_remark']: RemarkManager.delete_account_remark(user, account)
                    except: pass
                    
                    clean_msg = f"=====🗑️ 过期清理通知=====\n您的账号授权已过期并清理。\n📱 手机: {safe_display}\n📅 到期: {expiration_str}\n相关配置已失效移除，如需继续使用请重新录入并授权。"
                    if safe_send_message(user, clean_msg, f"过期清理通知 {user}-{account}"):
                        cleaned_count += 1
                        user_has_change = True

            if user_has_change:
                if valid_accounts:
                    try: middleware.bucketSet(bucket='dd_oppo_user', key=str(user), value=str(valid_accounts))
                    except: pass
                else:
                    try: middleware.bucketDel(bucket='dd_oppo_user', key=str(user))
                    except: pass
        except: continue

    if sender.isAdmin() and msg_upper in ['OPPO商城清理', '清理OPPO商城']:
        sender.reply(f"=====维护完成=====\n✅ 已清理过期: {cleaned_count}个\n📢 授权提醒: {reminded_count}个\n⚠️ CK失效通知: {ck_expired_count}个\n🔄 面板同步: {sync_result.get('synced', 0)} 条\n==================")

def admin_auth_options():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足\n只有管理员可以执行授权操作")
        return
    sender.reply("=====管理员强制授权=====\n请输入需要授权的用户QQ号(或ID)：\n回复 q 退出")
    target_userid = get_user_input(timeout=60)
    if not target_userid or target_userid.lower() == 'q': return
    target_userid = target_userid.strip()
    accounts = AccountManager.get_accounts(target_userid)
    if not accounts: return sender.reply("❌ 未找到账号。")
    sender.reply(f"👥 找到 {len(accounts)} 个账号。\n请输入要授权的月数：\n回复 q 退出")
    months_str = get_user_input(timeout=60)
    if not months_str or months_str.lower() == 'q': return
    try: months = int(months_str)
    except: return
    days = months * 30
    success_count = 0
    for account in accounts:
        try:
            account = str(account)
            accountVip = middleware.bucketGet(bucket='dd_oppo_auth', key=account)
            new_auth_time = empower(accountVip, days)
            try: middleware.bucketSet(bucket='dd_oppo_auth', key=account, value=new_auth_time)
            except: pass
            token = AccountManager.get_token(account)
            remark = RemarkManager.get_account_remark(target_userid, account)
            if token: sys_api.sync_env(token, account, remark, new_auth_time)
            success_count += 1
        except: pass
    sender.reply(f"✅ 管理员授权完成！成功 {success_count} 个。")

def show_tutorial():
    panel_name = '青龙' if config['panel_type'] == 'qinglong' else '呆呆'
    sender.reply(f"""=====OPPO商城插件教程=====\n当前模式: 🌐 提交至{panel_name}面板\n\n1️⃣ {config['randomsigncommand']}\n   使用 手机号#Token 格式录入。\n\n2️⃣ {config['randomquerycommand']}\n   查询账号有效状态与可用积分。\n\n3️⃣ {config['randommanagecommand']}\n   续费授权、删除账号。\n\n4️⃣ OPPO商城清理 / OPPO商城授权\n   清理过期并同步删除变量；管理员可强制授权。""")

# ===================== 主入口 =====================
try:
    command = str(usermessage or "").strip()
    msg_upper = command.upper()
    if sender.getImtype() == 'fake':
        clean_expired_accounts()
    elif re.fullmatch(r"(?i)oppo商城(通知|广播)(\s+.*)?", command):
        notify_authorized_users()
    elif command in ['OPPO商城登录', 'OPPO商城登陆', 'oppo商城登录', 'oppo商城登陆', '登录OPPO商城', '登陆OPPO商城', '登录oppo商城', '登陆oppo商城']:
        bindaccount()
    elif command in ['OPPO商城管理', 'oppo商城管理', '管理OPPO商城', '管理oppo商城']:
       xy_manage()
    elif command in ['OPPO商城查询', 'oppo商城查询', '查询OPPO商城', '查询oppo商城']:
        cxs()
    elif command in ['OPPO商城清理', 'oppo商城清理', '清理OPPO商城', '清理oppo商城']:
        clean_expired_accounts()
    elif command in ['OPPO商城授权', 'oppo商城授权']:
        admin_auth_options()
    elif command in ['OPPO商城教程', 'oppo商城教程']:
        show_tutorial()
except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")
