# [rule: ^(战马)(登录|登陆)$|^登(录|陆)(战马)$|^(战马)(查询|管理)$|^(查询|管理)(战马)$|^战马清理$|^战马授权$|^战马教程$|^战马通知 ?(.*)$|^战马广播 ?(.*)$|^清理战马$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 56 9,19 * * *]
# [public: true]
# [title: 战马能量星球]
# [open_source: false]
# [class: 工具类]
# [version: 1.5]
# [price: 8.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 战马能量星球代挂提交插件，支持Safe参数登录。<br>支持批量登录。<br>v1.4修复登录过期，查询过期。<br>指令：战马登录、战马管理、战马查询、战马授权、战马通知<br>支持呆呆积分桶,脚本在售后群1003974618。 售后联系：QQ 8165799<br>]

import re
from datetime import datetime, timedelta
import middleware
import urllib.parse
from urllib.parse import unquote, quote
from decimal import Decimal
import requests
import time
import json
import hashlib
import logging
import base64
import ast
import ssl
import warnings
import random
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

# 禁用SSL警告
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
requests.packages.urllib3.disable_warnings()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('zm_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 

WARHORSE_API_HOST = "warhorsechina.cojoy.com.cn"
WARHORSE_BASE_URL = f"https://{WARHORSE_API_HOST}/app/api/custom"
WARHORSE_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf2541939) XWEB/19841"
WARHORSE_REFERER = "https://servicewechat.com/wx94dca6ef07a54c55/180/page-frame.html"
WARHORSE_SIGNATURE = "ku9qdPDtR7HDR8Z48R8YU5G0wnRDZ4a1f2FqddxzwOyJ2AaqmnZxBPDCrE0S"

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
usermessage = sender.getMessage()
try:
    current_imtype = str(sender.getImtype() or "")
except:
    current_imtype = ""
if current_imtype and current_imtype.lower() not in ["fake", "cron"]:
    try: middleware.bucketSet("dd_zm_runtime", "sender", str(senderID))
    except: pass
    try: middleware.bucketSet("dd_zm_runtime", "imtype", current_imtype)
    except: pass

# [param: {"required":true,"key":"dd_zm.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_zm.dd_zm_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接系统","desc":"你的变量需要添加到的系统容器？参数用丨分割"}]
# [param: {"required":true,"key":"dd_zm.dd_zm_osname","bool":false,"placeholder":"必填项,例:zmnlyl","name":"提交到系统的变量名","desc":"系统容器内战马的变量名(默认为zmnlyl)"}]
# [param: {"required":true,"key":"dd_zm.hhttVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_zm.hhttcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"dd_zm.show_point_status","bool":true,"placeholder":"","name":"显示钱包状态","desc":"是否在查询结果中显示钱包金额"}]
# [param: {"required":true,"key":"dd_zm.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统"}]
# [param: {"required":true,"key":"dd_zm.enable_proxy","bool":true,"placeholder":"True/False","name":"是否启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_zm.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_zm.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"dd_zm.enable_remark","bool":true,"placeholder":"True/False","name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"dd_zm.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]

def getusercontent():
    """获取插件完整配置"""
    dd_hhtt_qlname = middleware.bucketGet('dd_zm', 'dd_zm_qlname') or ''
    dd_hhtt_osname = middleware.bucketGet('dd_zm', 'dd_zm_osname') or 'zmnlyl'
    
    dd_managecommand = middleware.bucketGet('dd_zm', 'dd_managecommand') or '战马管理'
    dd_querycommand = middleware.bucketGet('dd_zm', 'dd_querycommand') or '战马查询'
    dd_signcommand = middleware.bucketGet('dd_zm', 'dd_signcommand') or '战马登录'
    zsm = middleware.bucketGet('dd_zm', 'zsm') or ''
    
    enable_proxy = middleware.bucketGet('dd_zm', 'enable_proxy') or 'false'
    enable_proxy = enable_proxy.lower() == 'true'
    proxy_pool_url = middleware.bucketGet('dd_zm', 'proxy_pool_url') or ''
    
    points_bucket = middleware.bucketGet('dd_zm', 'points_bucket') or 'dd_sign_points'
    
    enable_remark = middleware.bucketGet('dd_zm', 'enable_remark') or 'false'
    enable_remark = enable_remark.lower() == 'true'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    xyVipmoney = Decimal(middleware.bucketGet('dd_zm', 'hhttVipmoney') or '0')
    xycoin = int(middleware.bucketGet('dd_zm', 'hhttcoin') or '0')
    
    show_point_status = middleware.bucketGet('dd_zm', 'show_point_status') or 'false'
    show_point_status = show_point_status.lower() == 'true'
    
    use_ma_pay = middleware.bucketGet('dd_zm', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    reminder_days = int(middleware.bucketGet('dd_zm', 'reminder_days') or '2')

    if not dd_hhtt_qlname:
        sender.reply("❌ 对接系统配置未设置 (Host丨ClientID丨ClientSecret)")
        exit(0)
    
    if not dd_hhtt_osname:
        sender.reply("❌ 变量名称未设置")
        exit(0)
   
    return {
        'dd_hhtt_osname': dd_hhtt_osname,
        'dd_hhtt_qlname': dd_hhtt_qlname,
        'dd_managecommand': dd_managecommand,
        'dd_querycommand': dd_querycommand,
        'dd_signcommand': dd_signcommand,
        'randommanagecommand': randommanagecommand,
        'randomquerycommand': randomquerycommand,
        'randomsigncommand': randomsigncommand,
        'zsm': zsm,
        'enable_proxy': enable_proxy,
        'proxy_pool_url': proxy_pool_url,
        'points_bucket': points_bucket,
        'enable_remark': enable_remark,
        'xyVipmoney': xyVipmoney,
        'xycoin': xycoin,
        'show_point_status': show_point_status,
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
        for owner in middleware.bucketAllKeys(bucket='dd_zm_user'):
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
def send_user_notice(user_id, msg, title="战马通知"):
    user_id = str(user_id or "").strip()
    if not user_id:
        return False
    imtype = ""
    try:
        imtype = str(sender.getImtype() or "")
    except:
        pass
    if not imtype or imtype.lower() in ["fake", "cron"]:
        imtype = middleware.bucketGet("dd_zm_runtime", "imtype") or ""
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

def mask_account(account):
    account = str(account or "")
    return account[:4] + "****" + account[-4:] if len(account) >= 8 else account

def get_account_display(account, remark=""):
    remark = str(remark or "").strip()
    return remark if remark else mask_account(account)

def generate_ua_from_safe(safe_str: str) -> str:
    seed_value = int(hashlib.md5(safe_str.encode()).hexdigest()[:8], 16)
    random.seed(seed_value)
    
    os_type = random.choice(["Android", "iOS"])
    if os_type == "Android":
        version = f"8.0.{random.randint(30, 45)}"
        return f"Mozilla/5.0 (Linux; Android {random.randint(10, 14)}; M2012K11AC Build/TKQ1.220829.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{random.randint(100, 120)}.0.0.0 Mobile Safari/537.36 XWEB/1160065 MMWEBID/2617 MicroMessenger/{version}.2420(0x28002837) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64 MiniProgramEnv/android"
    else:
        version = f"8.0.{random.randint(30, 46)}"
        return f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(14, 17)}_{random.randint(0, 5)} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/{version}(0x18002a28) NetType/WIFI Language/zh_CN"

def empower(empowertime, days):
    try:
        today_date = datetime.now().date()
        if len(empowertime) == 0 or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
            delayed_date = empower_date + timedelta(days=days)
            delayed_date = delayed_date.date()
        else:
            raise Exception('时间计算出错！')
        return str(delayed_date)
    except Exception as e:
        logger.error("授权时间计算失败: " + str(e))
        raise Exception("授权时间计算失败: " + str(e))

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

# ===================== 核心逻辑类 (战马版) =====================
class WarHorseClient:
    def __init__(self, safe):
        self.session = requests.Session()
        self.safe = str(safe or "").strip()
        self.ua = WARHORSE_USER_AGENT
        
    def _get_headers(self):
        return {
            'Host': WARHORSE_API_HOST,
            'Connection': 'keep-alive',
            'CUSTOMAPPID': 'wx94dca6ef07a54c55',
            'User-Agent': self.ua,
            'xweb_xhr': '1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'cGvnZetrWSWfLcdYaN40mLdFx6ObkRltdZmhS5hQkgDbuZd9bLcQevwBVEjx-war-horse-zm-2025': WARHORSE_SIGNATURE,
            'Accept': '*/*',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': WARHORSE_REFERER,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

    def p(self, endpoint, method="GET", params=""):
        url = f"{WARHORSE_BASE_URL}/{endpoint}?{params}"
        headers = self._get_headers()
        
        proxies = None
        if config['enable_proxy'] and config['proxy_pool_url']:
            try:
                res = requests.get(config['proxy_pool_url'], timeout=5)
                if res.status_code == 200:
                    proxy_ip = res.text.strip()
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', proxy_ip)
                    if match:
                        proxy_ip = match.group(1)
                        proxies = {'http': f"http://{proxy_ip}", 'https': f"http://{proxy_ip}"}
            except: pass
             
        try:
            response = self.session.get(url, headers=headers, verify=False, proxies=proxies, timeout=REQUEST_TIMEOUT)
            response.encoding = "utf-8"
            return response.json()
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return {"status": 0, "msg": str(e)}
    
    def check_info(self):
        try:
            data = self.p("getusercenter", params=f"safe={self.safe}")
            if data and data.get("status") == 1:
                nowscore = data.get('nowscore', 0)
                nick_name = "战马用户"
                wallet_info = {
                    "price": 0, 
                    "totalPrice": nowscore, 
                    "valid": True, 
                    "records": ["请在小程序查看"] 
                }
                return {
                    "nickname": nick_name,
                    "integral": nowscore,
                    "wallet": wallet_info
                }
            return None
        except Exception as e:
            logger.error(f"查询出错: {e}")
            return None

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='dd_zm_remarks', key=f'{user_id}_{account_id}')
            if remark_data: return remark_data
            return ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = remark.strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='dd_zm_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
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
                if remark: remarks[account] = remark
            return remarks
        except: return {}
    
    @staticmethod
    def delete_account_remark(user_id, account_id):
        try:
            middleware.bucketDel(bucket='dd_zm_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket='dd_zm_user', key=user_id)
            if not value: return []
            if value.startswith('[') and value.endswith(']'):
                try:
                    accounts = ast.literal_eval(value)
                    if isinstance(accounts, (list, tuple, set)):
                        accounts = list(dict.fromkeys(str(account).strip() for account in accounts if str(account).strip()))
                        return accounts
                except: pass
            return [str(value).strip()] if str(value).strip() else []
        except: return []

    @staticmethod
    def add_account(user_id, account):
        try:
            accounts = AccountManager.get_accounts(user_id)
            if account not in accounts:
                accounts.append(account)
                middleware.bucketSet(bucket='dd_zm_user', key=user_id, value=str(accounts))
                return True
            return False
        except: return False
    
    @staticmethod
    def remove_account(user_id, account):
        try:
            accounts = AccountManager.get_accounts(user_id)
            if account in accounts:
                accounts.remove(account)
                if accounts:
                    # 修复：将userid改为user_id
                    middleware.bucketSet(bucket='dd_zm_user', key=user_id, value=str(accounts))
                else:
                    # 修复：将userid改为user_id
                    middleware.bucketDel(bucket='dd_zm_user', key=user_id)
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(user_id, account, token):
        try:
            encrypted_token = encrypt_token(token)
            middleware.bucketSet(bucket='dd_zm_token', key=account, value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket='dd_zm_user')
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts: user_list.append(user)
            return user_list
        except: return []

class QingLongAPI:
    def __init__(self):
        ql_config = config['dd_hhtt_qlname']
        try:
            if not ql_config: raise ValueError("对接配置为空")
            qllist = ql_config.split('丨')
            if len(qllist) != 3: raise ValueError("对接配置格式错误")
            self.QLurl = qllist[0].strip()
            self.ClientID = qllist[1].strip()
            self.ClientSecret = qllist[2].strip()
            if not all([self.QLurl, self.ClientID, self.ClientSecret]): raise ValueError("配置不完整")
            self.qltoken = self._get_token()
        except Exception as e:
            logger.error("系统初始化失败: " + str(e))
            raise
    
    def _get_token(self):
        try:
            url = f"{self.QLurl}/open/auth/token?client_id={self.ClientID}&client_secret={self.ClientSecret}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()['data']['token']
            raise Exception("获取Token失败")
        except Exception as e: raise
    
    def get_all_envs(self):
        try:
            url = f"{self.QLurl}/open/envs"
            headers = {"Authorization": f"Bearer {self.qltoken}", "accept": "application/json"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200: return response.json()['data']
            return []
        except: return []
   
    def find_env_by_account(self, account, token=None):
        try:
            envs = self.get_all_envs()
            for env in envs:
                if env.get('name') != config['dd_hhtt_osname']: continue
                if token and env.get('value') == token: return env.get('id')
                if env.get('remarks') and str(account) in env.get('remarks'): return env.get('id')
            return None
        except: return None
    
    def delete_env(self, env_id):
        if not env_id: return False
        try:
            url = f"{self.QLurl}/open/envs"
            headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
            response = requests.delete(url, headers=headers, json=[env_id], timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"删除青龙变量失败: {e}")
            return False
    
    def add_env(self, token, account, phone, remark="", auth_time="", owner_user_id=None):
        try:
            url = f"{self.QLurl}/open/envs"
            phone_display = phone[:10] + '...' if len(phone) > 10 else phone
            remarks_parts = [f'战马:{phone_display}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{account}', '战马提交'])
            
            data = [{"value": token, "name": config['dd_hhtt_osname'], "remarks": '丨'.join(remarks_parts)}]
            headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code != 200:
                logger.error(f"新增青龙变量失败: {response.status_code} {response.text[:200]}")
                return False
            return True
        except Exception as e:
            logger.error(f"新增青龙变量异常: {e}")
            return False
    
    def update_env(self, env_id, token, account, phone, remark="", auth_time="", owner_user_id=None):
        try:
            url = f"{self.QLurl}/open/envs"
            phone_display = phone[:10] + '...' if len(phone) > 10 else phone
            remarks_parts = [f'战马:{phone_display}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', f'ID:{account}', '战马提交'])
            
            data = {"value": token, "name": config['dd_hhtt_osname'], "remarks": '丨'.join(remarks_parts), "id": env_id}
            headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
            response = requests.put(url, headers=headers, json=data, timeout=10)
            if response.status_code != 200:
                logger.error(f"更新青龙变量失败: {response.status_code} {response.text[:200]}")
                return False
            return True
        except Exception as e:
            logger.error(f"更新青龙变量异常: {e}")
            return False

try:
    ql_api = QingLongAPI()
except Exception as e:
    sender.reply("❌ 系统连接失败: " + str(e))
    exit(0)

def parse_panel_zm_remark(remarks):
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
    synced = 0
    failed = 0
    try:
        envs = ql_api.get_all_envs()
    except Exception as e:
        logger.warning(f"读取青龙环境失败: {e}")
        return {"synced": 0, "failed": 1}

    for env in envs or []:
        try:
            if env.get("name") != config["dd_hhtt_osname"]:
                continue
            token = str(env.get("value") or "").strip()
            if not token:
                continue
            info = parse_panel_zm_remark(env.get("remarks", ""))
            user = info.get("user")
            account = info.get("account") or token
            if not user or not account:
                continue
            existing_owner = get_owner_user_id(account, '')
            if existing_owner and existing_owner != str(user):
                logger.warning(f"跳过面板反向同步：账号 {account} 本地归属 {existing_owner}，面板备注归属 {user}")
                continue
            AccountManager.add_account(user, account)
            AccountManager.update_account_token(user, account, token)
            auth_time = info.get("auth")
            if auth_time and auth_time not in ["未授权", "无"] and re.fullmatch(r"\d{4}-\d{2}-\d{2}", auth_time):
                middleware.bucketSet("dd_zm_auth", account, auth_time)
            if config["enable_remark"] and info.get("remark"):
                RemarkManager.set_account_remark(user, account, info.get("remark"))
            synced += 1
        except Exception as e:
            failed += 1
            logger.warning(f"同步战马面板数据失败: {e}")
    return {"synced": synced, "failed": failed}

# ===================== 功能逻辑 =====================

def process_single_account(account, index, total_count, account_remarks):
    try:
        safe = account
        token_data = middleware.bucketGet(bucket='dd_zm_token', key=f'{account}')
        if token_data:
            full_token = decrypt_token(token_data)
        else:
            full_token = safe
        
        accountVip = middleware.bucketGet(bucket='dd_zm_auth', key=f'{account}')
        
        remark = ""
        if config['enable_remark']:
            remark = account_remarks.get(account, "")
        
        today_time = str(datetime.now().date())
        if len(accountVip) == 0:
            auth_time = "无"
        elif accountVip <= today_time:
            auth_time = f"{accountVip} (已过期)"
        else:
            auth_time = accountVip
        
        if len(accountVip) != 0 and accountVip > today_time:
            try:
                client = WarHorseClient(safe)
                info = client.check_info()
                
                if not info:
                    raise Exception("Cookie失效或查询失败")
                
                account_info = f"""
📝 【备注名称】 : {remark if remark else "账号"+str(index)}
📛 【用户标识】 : 战马用户
🏆 【当前积分】 : {info['integral']}
💵 【账户状态】 : 正常
⏰ 【授权时间】 : {auth_time}
"""
                return account_info.strip()
            except Exception as e:
                return f"""
=====战马查询失败=====
🔑 账号: {safe[:10]}...
❌ 错误: {str(e)[:50]}
=================="""
        else:
            return f"""
📝 【备注名称】 : {remark if remark else "账号"+str(index)}
🔑 【登录账号】 : {safe[:10]}...
🔐 【授权状态】 : {'⚠️ 未授权' if not accountVip else '❌ 已过期'}
⏰ 【授权时间】 : {auth_time}
"""
    except Exception as e:
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
        sender.reply(f"🚀 正在并发查询 {total_count} 个账号，请稍候...")

        max_workers = min(10, total_count)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_account = {}
            for index, account in enumerate(accounts, 1):
                future = executor.submit(process_single_account, account, index, total_count, account_remarks)
                future_to_account[future] = account 

            for future in as_completed(future_to_account):
                result_msg = future.result()
                if result_msg: sender.reply(result_msg)
                
    except Exception as e:
        logger.error("批量查询失败: " + str(e))
        sender.reply("❌ 查询失败: " + str(e))

def notify_authorized_users():
    """管理员通知已授权用户"""
    if not sender.isAdmin():
        sender.reply("❌ 只有管理员可以使用此功能")
        return
    
    content = ""
    match = re.search(r'(战马通知|战马广播) ?(.*)', str(usermessage or ""))
    if match:
        content = match.group(2).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：战马通知 系统维护中")
        return
        
    sender.reply("⏳ 正在扫描授权用户并发送通知...")
    
    try:
        sync_result = sync_local_auth_from_panel()
        all_users = AccountManager.get_all_users()
        success_count = 0
        today = str(datetime.now().date())
        
        for uid in all_users:
            # 检查该用户是否有任意一个有效授权账号
            user_accounts = AccountManager.get_accounts(uid)
            has_auth = False
            for acc in user_accounts:
                vip_date = middleware.bucketGet(bucket='dd_zm_auth', key=acc)
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                if send_user_notice(uid, f"📢 【战马管理员通知】\n\n{content}", "战马管理员通知"):
                    success_count += 1
                    time.sleep(0.1)
        
        sender.reply(f"✅ 通知完成\n📢 已送达: {success_count} 人\n🔄 面板同步: {sync_result.get('synced', 0)} 条")
        
    except Exception as e:
        sender.reply(f"❌ 通知异常: {e}")

def get_user_input(timeout=60):
    try:
        response = sender.listen(timeout * 1000)
        if not response: return None
        response = response.strip()
        if response.lower() in ['q', 'quit', 'exit', '退出', 'cancel']: return 'q'
        return response
    except: return None

def bindaccount():
    """绑定账号 (支持批量)"""
    try:
        remark = ""
        if config['enable_remark']:
            sender.reply("""
=====账号备注设置=====
🎯 请输入账号备注名
(批量提交时此备注将应用到所有账号)
------------------
回复备注名继续
回复"n"跳过备注
回复"q"退出操作
==================""")
            remark_input = get_user_input(timeout=120)
            if remark_input == 'q':
                sender.reply("✅ 已取消")
                return
            elif remark_input != 'n' and remark_input:
               remark = remark_input.strip()[:20]

        sender.reply("""
=====战马CK登录=====
请输入 Safe 参数
------------------
支持批量提交，一行一个
------------------
回复"q"退出操作
==================""")
        
        input_str = get_user_input(timeout=120)
        if not input_str or input_str == 'q':
            sender.reply("✅ 已取消")
            return
        
        safe_lines = [line.strip() for line in re.split(r"[\n\r&]+", input_str) if line.strip()]
        
        if not safe_lines:
            sender.reply("❌ 内容为空")
            return

        sender.reply(f"⏳ 正在处理 {len(safe_lines)} 个账号，请稍候...")
        
        for line in safe_lines:
            try:
                # 兼容Safe#备注格式，只取Safe部分
                parts = line.split('#')
                safe = parts[0].strip()
                if not safe:
                    sender.reply(f"❌ Safe为空，已跳过: {line[:10]}...")
                    continue
                
                # 如果输入里自带了备注，优先使用输入里的备注(如果全局备注为空)
                line_remark = parts[1].strip() if len(parts) > 1 else ""
                final_remark = remark if remark else line_remark
                
                client = WarHorseClient(safe)
                info_res = client.check_info()
                
                if info_res:
                    nick = info_res['nickname']
                    # 恢复详细输出
                    process_account_binding(safe, safe, nick, final_remark)
                else:
                     sender.reply(f"❌ 登录失败: Safe失效或接口返回异常 ({safe[:10]}...)")
            except Exception as e:
                logger.error(f"处理登录异常 {line[:10]}...: {e}")
                sender.reply(f"❌ 处理异常: {line[:10]}...，{e}")
            
    except Exception as e:
        logger.error("绑定失败: " + str(e))
        sender.reply("❌ 绑定失败: " + str(e))

def process_account_binding(full_token, phone, nickname, remark=""):
    """处理绑定入库并恢复详细回复"""
    try:
        account = full_token 
        accountVip = middleware.bucketGet(bucket='dd_zm_auth', key=account)
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
        safe_display = account[:10] + "..." + account[-6:] if len(account) > 16 else account

        existing_accounts = AccountManager.get_accounts(userid)
        if account in existing_accounts:
            AccountManager.update_account_token(userid, account, full_token)
        else:
            AccountManager.add_account(userid, account)
            encrypted_token = encrypt_token(full_token)
            middleware.bucketSet(bucket='dd_zm_token', key=account, value=encrypted_token)
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account, remark)
        
        ql_msg = ""
        if is_authorized:
            try:
                qlid = ql_api.find_env_by_account(account, full_token)
                if qlid:
                    ql_api.update_env(qlid, full_token, account, account, remark, auth_time=accountVip)
                else:
                    ql_api.add_env(full_token, account, account, remark, auth_time=accountVip)
                ql_msg = "\n🔄 状态: ✅ 已同步到系统"
            except: 
                ql_msg = "\n🔄 状态: ❌ 系统同步失败"
        else:
            ql_msg = "\n🔄 状态: ⏸️ 未授权，暂不提交"

        # 恢复核心：详细回复框
        sender.reply(f"""
=====战马账号绑定=====
✅ 绑定成功!
👤 用户: {nickname}
🔑 账号: {safe_display}{remark_info}
🔐 授权: {auth_status}{ql_msg}
⏰ 下一步操作: 
   {next_step}
==================""")
            
    except Exception as e:
        logger.error(f"入库异常: {e}")
        sender.reply(f"❌ 入库异常: {e}")

# ===================== 支付与管理 =====================
def xy_manage():
    accounts = AccountManager.get_accounts(userid)
    if not accounts:
        sender.reply(f"❌ 未找到账号，请发送 {config['randomsigncommand']} 绑定")
        return
    
    account_remarks = RemarkManager.get_all_remarks(userid) if config['enable_remark'] else {}
    count = 1
    account_list = "======我的战马账号====="
    today_time = str(datetime.now().date())
    
    for account in accounts:
        accountVip = middleware.bucketGet(bucket='dd_zm_auth', key=f'{account}')
        if len(accountVip) == 0: vip_status = '⚠️ 未授权'
        elif accountVip < today_time: vip_status = '❌ 已过期'
        else: vip_status = f'✅ {accountVip}'
        
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        remark_display = f" - {remark}" if remark else ""
        
        safe_display = account[:8] + "..." + account[-6:]
        
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
            manage_single_account(accounts[choice_num - 1], account_remarks)
        else:
            sender.reply('❌ 序号无效')
    except:
        sender.reply('❌ 输入必须是数字')

def manage_single_account(account, account_remarks):
    try:
        encrypted_token = middleware.bucketGet(bucket='dd_zm_token', key=f'{account}')
        token = decrypt_token(encrypted_token) if encrypted_token else ""
        accountVip = middleware.bucketGet(bucket='dd_zm_auth', key=f'{account}')
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        safe_display = account[:10] + "..."
        
        sender.reply(f"""
=====账号详情=====
🔑 账号: {safe_display}
📝 备注: {remark}
🔐 授权: {vip_status}
==================
[1] 授权账号
[2] 删除账号
[3] 修改备注
------------------
回复数字选择，Q退出
==================""")
        
        choice = get_user_input()
        if not choice or choice == 'q': return
        
        if choice == '1': # 授权
            sender.reply("请输入授权月数(如:1)，Q退出")
            months_str = get_user_input()
            if not months_str or months_str == 'q': return
            try:
                months = int(months_str)
                if months <= 0: raise ValueError
            except:
                sender.reply("❌ 数字无效")
                return
            
            if process_payment('战马授权', months, accountVip, token, account, account, account, remark):
                days = months * 30
                new_auth_time = empower(accountVip, days)
                middleware.bucketSet(bucket='dd_zm_auth', key=f'{account}', value=new_auth_time)
                
                if token:
                    try:
                        qlid = ql_api.find_env_by_account(account, token)
                        if qlid: ql_api.update_env(qlid, token, account, account, remark, new_auth_time)
                        else: ql_api.add_env(token, account, account, remark, new_auth_time)
                        sender.reply("🔄 授权成功并同步到系统！")
                    except: sender.reply("⚠️ 授权成功但系统同步失败")
                
                money = Decimal(months) * config['xyVipmoney']
                sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")

        elif choice == '2': # 删除
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                AccountManager.remove_account(userid, account)
                qlid = ql_api.find_env_by_account(account, token)
                if qlid: ql_api.delete_env(qlid)
                middleware.bucketDel(bucket='dd_zm_token', key=account)
                middleware.bucketDel(bucket='dd_zm_auth', key=account)
                if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                sender.reply("✅ 删除成功")

        elif choice == '3': # 备注
             sender.reply("请输入新备注:")
             new_remark = get_user_input()
             if new_remark and new_remark != 'q':
                 RemarkManager.set_account_remark(userid, account, new_remark)
                 if token:
                     qlid = ql_api.find_env_by_account(account, token)
                     if qlid: ql_api.update_env(qlid, token, account, account, new_remark, accountVip)
                 sender.reply("✅ 备注更新成功")

    except Exception as e:
        sender.reply(f"操作失败: {e}")

def process_payment(project, months, accountVip, token, phone, account, yt_account, remark=""):
    money = Decimal(months) * config['xyVipmoney']
    points_needed = config['xycoin'] * months
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
    if config['xycoin'] > 0:
        options.append({'id': idx, 'type': 'pt', 'name': '积分支付', 'amount': points_needed, 'curr': user_points})
    
    if not options:
        sender.reply("❌ 未配置支付方式")
        exit(0)
    
    msg = "=====选择支付方式====="
    for opt in options:
        amount_str = f"{opt['amount']}积分" if opt['type'] == 'pt' else f"{opt['amount']}元"
        suffix = f" (当前拥有: {opt['curr']})" if opt['type'] == 'pt' else ""
        msg += f"\n[{opt['id']}] {opt['name']} ({amount_str}){suffix}"
    msg += "\n回复数字选择，Q退出"
    sender.reply(msg)
    
    sel = get_user_input()
    if not sel or sel == 'q': exit(0)
    
    try:
        choice = int(sel)
        opt = next((o for o in options if o['id'] == choice), None)
        if not opt: raise ValueError
        
        if opt['type'] == 'wx':
            if sender.atWaitPay(): 
                sender.reply("⚠️ 当前有人支付中")
                exit(0)
            sender.reply(f"=====微信扫码=====\n金额: {opt['amount']}元")
            sender.replyImage(config['zsm'])
            res = sender.waitPay("q", 60000)
            if str(res) == 'q': exit(0)
            return True
        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply("❌ 积分不足")
                exit(0)
            sender.reply("确认支付回复【y】")
            if get_user_input() == 'y':
                new_pt = int(opt['curr']) - int(opt['amount'])
                middleware.bucketSet(config['points_bucket'], userid, str(new_pt))
                return True
            exit(0)
            
        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"ZM_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"战马授权-{months}月",
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
                return True
            return False

    except:
        sender.reply("❌ 支付异常")
        exit(0)

def batch_auth_all_accounts(accounts, account_remarks):
    sender.reply("请输入授权月数，Q退出")
    m = get_user_input()
    if not m or not m.isdigit(): return
    months = int(m)
    if months <= 0: return
    
    count = len(accounts)
    total_money = Decimal(months) * config['xyVipmoney'] * count
    total_points = config['xycoin'] * months * count
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
    if config['xycoin'] > 0:
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
        
        elif opt['type'] == 'pt':
            if int(opt['curr']) < int(opt['amount']):
                sender.reply(f"❌ 积分不足，需要 {opt['amount']}，当前 {opt['curr']}")
                return
            sender.reply(f"确认消耗 {opt['amount']} 积分？回复【y】")
            if get_user_input() != 'y': return
            new_pt = int(opt['curr']) - int(opt['amount'])
            middleware.bucketSet(config['points_bucket'], userid, str(new_pt))

        elif opt['type'] == 'ma':
            conf = opt['conf']
            out_trade_no = f"ZM_BATCH_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"战马批量-{count}号-{months}月",
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
            accountVip = middleware.bucketGet(bucket='dd_zm_auth', key=account)
            new_date = empower(accountVip, months*30)
            middleware.bucketSet('dd_zm_auth', account, new_date)
            
            encrypted_token = middleware.bucketGet(bucket='dd_zm_token', key=account)
            token = decrypt_token(encrypted_token) if encrypted_token else None
            
            curr_remark = account_remarks.get(account, "") if account_remarks else ""
            
            if token:
                  try:
                     qid = ql_api.find_env_by_account(account, token)
                     if qid: ql_api.update_env(qid, token, account, account, curr_remark, new_date)
                     else: ql_api.add_env(token, account, account, curr_remark, new_date)
                  except: pass
        except: pass
    
    sender.reply("✅ 批量授权完成")

def batch_delete_all_accounts(accounts):
    sender.reply("确认删除回复【确认删除】")
    if get_user_input() == "确认删除":
        for account in accounts:
             encrypted_token = middleware.bucketGet(bucket='dd_zm_token', key=account)
             token = decrypt_token(encrypted_token) if encrypted_token else None
             qlid = ql_api.find_env_by_account(account, token)
             if qlid: ql_api.delete_env(qlid)
             middleware.bucketDel(bucket='dd_zm_token', key=account)
             middleware.bucketDel(bucket='dd_zm_auth', key=account)
             if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
        middleware.bucketDel(bucket='dd_zm_user', key=userid)
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts():
    """清理过期账号并处理到期提醒"""
    try:
        sync_result = sync_local_auth_from_panel()
        today_time = str(datetime.now().date())
        remind_date = str((datetime.now() + timedelta(days=config['reminder_days'])).date())
        
        users = AccountManager.get_all_users()
        expired_count = 0
        remind_count = 0
        
        for user in users:
            accounts = AccountManager.get_accounts(user)
            for account in accounts:
                accountVip = middleware.bucketGet(bucket='dd_zm_auth', key=account)
                if not accountVip: 
                    continue
                
                # 1. 过期清理逻辑
                if accountVip < today_time:
                    # 获取 Token 并从青龙删除环境变量
                    encrypted_token = middleware.bucketGet(bucket='dd_zm_token', key=account)
                    token = decrypt_token(encrypted_token) if encrypted_token else None
                    qlid = ql_api.find_env_by_account(account, token)
                    if qlid: 
                        ql_api.delete_env(qlid)
                        
                    # 从本地存储中删除数据
                    AccountManager.remove_account(user, account)
                    middleware.bucketDel(bucket='dd_zm_token', key=account)
                    middleware.bucketDel(bucket='dd_zm_auth', key=account)
                    if config['enable_remark']: 
                        RemarkManager.delete_account_remark(user, account)
                    expired_count += 1
                    account_display = get_account_display(account, RemarkManager.get_account_remark(user, account) if config['enable_remark'] else "")
                    clean_msg = f"""=====🗑️ 过期清理通知=====
您的战马账号授权已过期并清理。
📱 账号: {account_display}
📅 到期: {accountVip}
------------------
如需继续使用，请重新登录并授权。
=================="""
                    safe_send_message(user, clean_msg, f"过期清理通知 {user}-{account}")
                
                # 2. 到期提醒逻辑
                elif accountVip <= remind_date:
                    remind_key = f"{user}_{account}_{today_time}"
                    if not middleware.bucketGet("dd_zm_remind_log", remind_key):
                        account_display = get_account_display(account, RemarkManager.get_account_remark(user, account) if config['enable_remark'] else "")
                        msg = f"""=====⏰ 到期提醒=====
您的战马账号授权即将到期！
📱 账号: {account_display}
📅 到期: {accountVip}
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                        if safe_send_message(user, msg, f"到期提醒 {user}-{account}"):
                            middleware.bucketSet("dd_zm_remind_log", remind_key, "1")
                            remind_count += 1

        # 反馈给用户或记录日志
        if usermessage in ['战马清理', '清理战马']: 
            sender.reply(f"✅ 清理完成！\n🗑️ 共删除了 {expired_count} 个过期账号的数据(含青龙)。\n📢 到期提醒 {remind_count} 个。\n🔄 面板同步: {sync_result.get('synced', 0)} 条")
        elif sender.getImtype() == 'fake': # 触发Cron定时任务时
            logger.info(f"定时清理任务完成: 清理过期账号 {expired_count} 个，即将到期 {remind_count} 个。")
            
    except Exception as e:
        logger.error(f"清理任务执行异常: {e}")
        if usermessage in ['战马清理', '清理战马']: 
            sender.reply(f"❌ 清理过程发生异常: {str(e)}")

def admin_auth_options():
    """管理员专用：强制给指定用户授权"""
    if not sender.isAdmin():
        sender.reply("❌ 权限不足，此功能仅限管理员使用")
        return

    sender.reply("=====管理员强制授权=====\n请输入需要授权的用户QQ号(或ID)：\n------------------\n回复 q 退出")
    target_userid = get_user_input(timeout=60)
    if not target_userid or target_userid.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    target_userid = target_userid.strip()
    accounts = AccountManager.get_accounts(target_userid)
    if not accounts:
        sender.reply(f"❌ 未找到该用户({target_userid})绑定的任何账号。")
        return

    sender.reply(f"👥 找到该用户绑定了 {len(accounts)} 个账号。\n请输入要授权的月数 (如 1)：\n------------------\n回复 q 退出")
    months_str = get_user_input(timeout=60)
    if not months_str or months_str.lower() == 'q':
        sender.reply("✅ 已取消")
        return

    try:
        months = int(months_str)
        if months <= 0: raise ValueError
    except:
        sender.reply("❌ 输入的月数无效")
        return

    days = months * 30
    success_count = 0
    account_remarks = RemarkManager.get_all_remarks(target_userid) if config['enable_remark'] else {}

    sender.reply(f"⏳ 正在为用户 {target_userid} 的 {len(accounts)} 个账号执行授权并同步青龙...")

    for account in accounts:
        try:
            accountVip = middleware.bucketGet(bucket='dd_zm_auth', key=account)
            new_auth_time = empower(accountVip, days)
            middleware.bucketSet(bucket='dd_zm_auth', key=account, value=new_auth_time)

            encrypted_token = middleware.bucketGet(bucket='dd_zm_token', key=account)
            token = decrypt_token(encrypted_token) if encrypted_token else None
            curr_remark = account_remarks.get(account, "") if account_remarks else ""

            if token:
                qlid = ql_api.find_env_by_account(account, token)
                if qlid:
                    ql_api.update_env(qlid, token, account, account, curr_remark, new_auth_time)
                else:
                    ql_api.add_env(token, account, account, curr_remark, new_auth_time)
            success_count += 1
        except Exception as e:
            logger.error(f"授权账号 {account} 失败: {e}")

    sender.reply(f"✅ 管理员授权完成！\n成功为 {target_userid} 的 {success_count} 个账号延长了 {months} 个月。")

def show_tutorial():
    sender.reply(f"""
=====战马插件教程=====
1️⃣ {config['randomsigncommand']}
   输入：Safe值 (支持批量，一行一个)
   自动登录验证并同步系统

2️⃣ {config['randomquerycommand']}
   查询战马积分

3️⃣ {config['randommanagecommand']}
   续费授权、删除账号

4️⃣ 战马通知 内容
   管理员群发消息给已授权用户

⚠️ 变量名: {config['dd_hhtt_osname']}
==================""")

# ===================== 主入口 =====================
try:
    command = str(usermessage or "").strip()
    if re.fullmatch(r"战马(通知|广播)(\s+.*)?", command):
        notify_authorized_users()
    elif command in ['战马登录', '战马登陆', '登录战马', '登陆战马']:
        bindaccount()
    elif command in ['战马管理', '管理战马']:
       xy_manage()
    elif command in ['战马查询', '查询战马']:
        cxs()
    elif command in ['战马清理', '清理战马']:
        clean_expired_accounts()
    elif command == '战马授权':
        admin_auth_options()
    elif command == '战马教程':
        show_tutorial()
    elif sender.getImtype() == 'fake':
        clean_expired_accounts()
except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")
