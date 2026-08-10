# [rule: ^(牛卡福货主)(登录|登陆)$|^登(录|陆)(牛卡福货主)$|^(牛卡福货主)(查询|管理)$|^(查询|管理)(牛卡福货主)$|^牛卡福货主清理$|^牛卡福货主授权$|^牛卡福货主教程$|^牛卡福货主通知 ?(.*)$|^清理牛卡福货主$|^牛卡福货主一键运行$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 10 * * *]
# [public: true]
# [title: 牛卡福货主助手]
# [open_source: false]
# [class: 工具类]
# [version: 1.2]
# [price: 8.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 牛卡福货主全能版。<br>1. 支持【本地运行】或【系统对接】双模式切换，已内置任务，增加失效告警、定时汇总推送、修复通知Bug<br>2. 采用【手机号#Token】登录，防重复防丢数据。<br>3. 内置定时任务，脱离后台也能跑。📞 售后联系：QQ 8165799 售后群1003974618<br>]

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
logger = logging.getLogger('nkf_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
usermessage = sender.getMessage()

_RUNTIME_BUCKET = "plugin_push_runtime"
_RUNTIME_KEY = "牛卡福货主"
try:
    current_imtype = str(sender.getImtype() or "")
except:
    current_imtype = ""
if current_imtype and current_imtype.lower() not in ["fake", "cron"]:
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_sender", str(senderID))
    except: pass
    try: middleware.bucketSet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype", current_imtype)
    except: pass

# ===================== 插件配置参数 =====================
# [param: {"required":true,"key":"dd_nkf.run_mode","bool":false,"placeholder":"local/system","name":"运行模式(必选)","desc":"local=本地内置任务(推荐，无需配置后台)\nsystem=提交到系统后台面板"}]
# [param: {"required":false,"key":"dd_nkf.dd_nkf_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"对接系统配置","desc":"模式选system时必填，本地模式可留空"}]
# [param: {"required":false,"key":"dd_nkf.dd_nkf_osname","bool":false,"placeholder":"默认:NKF_TOKENS","name":"系统变量名","desc":"系统容器内变量名(仅系统模式有效)"}]
# [param: {"required":true,"key":"dd_nkf.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_nkf.hhttVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_nkf.hhttcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"dd_nkf.show_point_status","bool":true,"placeholder":"","name":"显示钱包状态","desc":"是否在查询结果中显示钱包金额"}]
# [param: {"required":true,"key":"dd_nkf.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统"}]
# [param: {"required":true,"key":"dd_nkf.enable_proxy","bool":true,"placeholder":"True/False","name":"是否启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_nkf.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_nkf.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"dd_nkf.enable_remark","bool":true,"placeholder":"True/False","name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":true,"key":"dd_nkf.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]

def getusercontent():
    """获取插件完整配置"""
    # 1. 运行模式判断
    run_mode_input = middleware.bucketGet('dd_nkf', 'run_mode')
    if run_mode_input and ('system' in run_mode_input.lower() or 'qinglong' in run_mode_input.lower()):
        run_mode = 'system'
    else:
        run_mode = 'local'

    dd_hhtt_qlname = middleware.bucketGet('dd_nkf', 'dd_nkf_qlname') or ''
    dd_hhtt_osname = middleware.bucketGet('dd_nkf', 'dd_nkf_osname') or 'NKF_TOKENS'
    
    # 模式检查
    if run_mode == 'system':
        if not dd_hhtt_qlname:
            sender.reply("❌ 配置错误：您选择了【系统模式】，但未配置【对接系统配置】。\n请在插件配置中填写，或切换回【本地模式】。")
            exit(0)
    
    dd_managecommand = middleware.bucketGet('dd_nkf', 'dd_managecommand') or '牛卡福货主管理'
    dd_querycommand = middleware.bucketGet('dd_nkf', 'dd_querycommand') or '牛卡福货主查询'
    dd_signcommand = middleware.bucketGet('dd_nkf', 'dd_signcommand') or '牛卡福货主登录'
    zsm = middleware.bucketGet('dd_nkf', 'zsm') or ''
    
    enable_proxy = middleware.bucketGet('dd_nkf', 'enable_proxy') or 'false'
    enable_proxy = enable_proxy.lower() == 'true'
    proxy_pool_url = middleware.bucketGet('dd_nkf', 'proxy_pool_url') or ''
    
    points_bucket = middleware.bucketGet('dd_nkf', 'points_bucket') or 'dd_sign_points'
    
    enable_remark = middleware.bucketGet('dd_nkf', 'enable_remark') or 'false'
    enable_remark = enable_remark.lower() == 'true'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    xyVipmoney = Decimal(middleware.bucketGet('dd_nkf', 'hhttVipmoney') or '0')
    xycoin = int(middleware.bucketGet('dd_nkf', 'hhttcoin') or '0')
    
    show_point_status = middleware.bucketGet('dd_nkf', 'show_point_status') or 'false'
    show_point_status = show_point_status.lower() == 'true'
    
    use_ma_pay = middleware.bucketGet('dd_nkf', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    reminder_days = int(middleware.bucketGet('dd_nkf', 'reminder_days') or '2')

    return {
        'run_mode': run_mode,
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
        for owner in middleware.bucketAllKeys(bucket='dd_nkf_user'):
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

def send_user_notice(user_id, msg, title="牛卡福货主助手通知"):
    user_id = str(user_id or "").strip()
    if not user_id:
        return False
    imtype = ""
    try:
        imtype = str(sender.getImtype() or "")
    except:
        pass
    if not imtype or imtype.lower() in ["fake", "cron"]:
        imtype = middleware.bucketGet(_RUNTIME_BUCKET, _RUNTIME_KEY + "_imtype") or ""
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

# ===================== 辅助工具函数 =====================
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

# ===================== 核心逻辑类 (牛卡福货主适配版) =====================
class NiuKaFuClient:
    def __init__(self, token):
        self.host = "shippers.nucarf.net"
        self.base_url = f"https://{self.host}"
        self.token = token.strip()
        
        # 生成唯一设备ID
        device_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16]
        
        # 基础Headers
        self.headers = {
            "content-type": "application/json",
            "user-agent": "okhttp/3.14.9",
            "x-access-token": self.token,
            "oss-token": self.token,
            "x-apptype": "APP",
            "x-device-type": "ANDROID",
            "x-device-id": device_id,
            "x-device-name": "Android",
            "x-appversion": "2.4.7",
            "x-term-id": "30971511",
            "request-source": "ONE_STOP_WX_DISPATCH",
            "accept-encoding": "gzip"
        }

    def _request(self, method, endpoint, payload=None):
        url = f"{self.base_url}{endpoint}"
        
        proxies = None
        if config['enable_proxy'] and config['proxy_pool_url']:
            try:
                res = requests.get(config['proxy_pool_url'], timeout=3)
                if res.status_code == 200:
                    proxy_ip = res.text.strip()
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', proxy_ip)
                    if match:
                        proxy_ip = match.group(1)
                        # 使用socks5或http取决于您的代理池，这里默认兼容http格式
                        proxies = {'http': f"http://{proxy_ip}", 'https': f"http://{proxy_ip}"}
            except: pass
            
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=payload or {}, verify=False, proxies=proxies, timeout=15)
            else:
                response = requests.get(url, headers=self.headers, verify=False, proxies=proxies, timeout=15)
            
            return response.json()
        except Exception as e:
            logger.error(f"请求异常: {e}")
            return {"code": -1, "message": str(e)}

    def check_info(self):
        """查询用户信息"""
        try:
            # 获取用户信息 (GET)
            user_res = self._request("GET", "/api/shippers/user/mine")
            if not user_res or user_res.get("code") != 200:
                return None
            
            data = user_res.get("data", {})
            user_info = data.get("userInfo", {})
            
            nick_name = user_info.get("userName", "牛卡福用户")
            phone = user_info.get("phoneNo", "未知")
            wallet = data.get("walletAmount", "0")
            points = data.get("pointAmount", 0)

            wallet_info = {
                "price": wallet, 
                "totalPrice": points, 
                "valid": True, 
                "records": ["请在APP查看"] 
            }
            
            return {
                "nickname": f"{nick_name}",
                "integral": f"积分:{points} | 余额:{wallet}元",
                "wallet": wallet_info
            }
        except Exception as e:
            logger.error(f"查询出错: {e}")
            return None

    def execute_sign_task(self):
        """执行签到任务"""
        logs = []
        try:
            # 1. 检查签到状态
            status_res = self._request("GET", "/api/campaign/dailySignIn")
            
            if status_res and status_res.get("code") == 200:
                sign_data = status_res.get("data", {})
                sign_count = sign_data.get("signInCount", 0)
                
                if sign_data.get("signInStatus", False):
                    logs.append(f"🔵 今日已签到 (连续{sign_count}天)")
                    # 查询一下最新积分
                    user_res = self._request("GET", "/api/shippers/user/mine")
                    if user_res and user_res.get("code") == 200:
                        pts = user_res.get("data", {}).get("pointAmount", 0)
                        logs.append(f"💰 当前积分: {pts}")
                    return "\n".join(logs)
            
            # 2. 模拟延时防风控
            time.sleep(2)

            # 3. 执行签到
            sign_res = self._request("POST", "/api/campaign/signIn", {})
            
            if sign_res and sign_res.get("code") == 200:
                result = sign_res.get("data", {})
                pts = result.get("pointAmount", 0)
                day = result.get("day", 0)
                logs.append(f"✅ 签到成功: 获得{pts}积分 (第{day}天)")
            else:
                msg = sign_res.get("message", "未知错误") if sign_res else "请求无响应"
                logs.append(f"❌ 签到失败: {msg}")
            
            # 模拟延时
            time.sleep(1)
            
            # 4. 查询最新积分状态
            user_res = self._request("GET", "/api/shippers/user/mine")
            if user_res and user_res.get("code") == 200:
                 data = user_res.get("data", {})
                 logs.append(f"💰 积分: {data.get('pointAmount', 0)} | 余额: {data.get('walletAmount', 0)}元")
            else:
                 logs.append("⚠️ 积分余额查询失败")

            return "\n".join(logs)
        except Exception as e:
            return f"❌ 执行异常: {str(e)}"

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='dd_nkf_remarks', key=f'{user_id}_{account_id}')
            if remark_data: return remark_data
            return ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = remark.strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='dd_nkf_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
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
            middleware.bucketDel(bucket='dd_nkf_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        """获取用户绑定的账号列表(手机号)"""
        try:
            value = middleware.bucketGet(bucket='dd_nkf_user', key=user_id)
            if not value: return []
            if value.startswith('[') and value.endswith(']'):
                try:
                    accounts = eval(value)
                    if isinstance(accounts, (list, tuple, set)):
                        accounts = list(dict.fromkeys(accounts)) # 去重
                    return accounts
                except: pass
            return [str(value)]
        except: return []

    @staticmethod
    def add_account(user_id, account):
        """添加账号到用户列表"""
        try:
            accounts = AccountManager.get_accounts(user_id)
            if account not in accounts:
                accounts.append(account)
                middleware.bucketSet(bucket='dd_nkf_user', key=user_id, value=str(accounts))
                return True
            return False
        except: return False
    
    @staticmethod
    def remove_account(user_id, account):
        """移除账号"""
        try:
            accounts = AccountManager.get_accounts(user_id)
            if account in accounts:
                accounts.remove(account)
                if accounts:
                    middleware.bucketSet(bucket='dd_nkf_user', key=user_id, value=str(accounts))
                else:
                    middleware.bucketDel(bucket='dd_nkf_user', key=user_id)
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(account, token):
        """更新Token (Key为手机号)"""
        try:
            encrypted_token = encrypt_token(token)
            middleware.bucketSet(bucket='dd_nkf_token', key=account, value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_token(account):
        """获取Token"""
        try:
            enc = middleware.bucketGet(bucket='dd_nkf_token', key=account)
            return decrypt_token(enc) if enc else None
        except: return None

    @staticmethod
    def get_all_users():
        """获取所有用户ID"""
        try:
            users = middleware.bucketAllKeys(bucket='dd_nkf_user')
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts: user_list.append(user)
            return user_list
        except: return []

# ===================== 系统对接模块(原青龙) =====================
class SystemAPI:
    def __init__(self):
        self.enabled = False
        if config['run_mode'] == 'system':
            ql_config = config['dd_hhtt_qlname']
            try:
                if not ql_config: raise ValueError("对接配置为空")
                qllist = ql_config.split('丨')
                if len(qllist) != 3: raise ValueError("对接配置格式错误")
                self.QLurl = qllist[0].strip()
                self.ClientID = qllist[1].strip()
                self.ClientSecret = qllist[2].strip()
                self.qltoken = self._get_token()
                self.enabled = True
            except Exception as e:
                logger.error("系统初始化失败: " + str(e))
                # 不阻断程序，只是禁用对接功能
    
    def _get_token(self):
        try:
            url = f"{self.QLurl}/open/auth/token?client_id={self.ClientID}&client_secret={self.ClientSecret}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()['data']['token']
            raise Exception("获取Token失败")
        except Exception as e: raise
    
    def get_all_envs(self):
        if not self.enabled: return []
        try:
            url = f"{self.QLurl}/open/envs"
            headers = {"Authorization": f"Bearer {self.qltoken}", "accept": "application/json"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200: return response.json()['data']
            return []
        except: return []
   
    def find_env(self, phone, token=None):
        """智能查找: 优先手机号, 其次Token值(防止重复)"""
        if not self.enabled: return None
        try:
            envs = self.get_all_envs()
            for env in envs:
                if env.get('name') != config['dd_hhtt_osname']: continue
                
                # 1. 优先通过备注中的手机号精准匹配
                if env.get('remarks') and str(phone) in env.get('remarks'): 
                    return env.get('id')
                
                # 2. 其次检查Value(Token)是否一致
                if token and env.get('value'):
                    env_val = env.get('value').strip()
                    input_val = token.strip()
                    if env_val == input_val:
                         return env.get('id')
                    
            return None
        except: return None
    
    def delete_env(self, phone):
        if not self.enabled: return False
        try:
            env_id = self.find_env(phone)
            if not env_id: return False
            url = f"{self.QLurl}/open/envs"
            headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
            requests.delete(url, headers=headers, json=[env_id], timeout=10)
            return True
        except: return False
    
    def sync_env(self, token, phone, remark="", auth_time="", owner_user_id=None):
        """同步(新增或更新)"""
        if not self.enabled: return False
        try:
            # 传入Token用于排重检测
            env_id = self.find_env(phone, token)
            
            # 构造标准化备注
            remarks_parts = [f'牛卡福货主:{phone}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', '牛卡福货主提交'])
            final_remark = '丨'.join(remarks_parts)

            headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
            url = f"{self.QLurl}/open/envs"

            if env_id:
                # 更新
                data = {"value": token, "name": config['dd_hhtt_osname'], "remarks": final_remark, "id": env_id}
                requests.put(url, headers=headers, json=data, timeout=10)
            else:
                # 新增
                data = [{"value": token, "name": config['dd_hhtt_osname'], "remarks": final_remark}]
                requests.post(url, headers=headers, json=data, timeout=10)
            return True
        except: return False

# 初始化系统API
try:
    sys_api = SystemAPI()
except:
    pass

# ===================== 功能逻辑 =====================

def process_single_account_query(account, index, total_count, account_remarks):
    try:
        # account 是手机号
        full_token = AccountManager.get_token(account)
        if not full_token: full_token = "No Token"
        
        accountVip = middleware.bucketGet(bucket='dd_nkf_auth', key=f'{account}')
        
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
        
        # 手机号脱敏
        safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account

        if len(accountVip) != 0 and accountVip > today_time:
            try:
                client = NiuKaFuClient(full_token)
                info = client.check_info()
                
                if not info:
                    raise Exception("Token失效或查询失败")
                
                account_info = f"""
📝 【备注名称】 : {remark if remark else "账号"+str(index)}
📱 【牛卡福账号】 : {safe_display}
🏆 【当前资产】 : {info['integral']}
💵 【账户状态】 : 正常
⏰ 【授权时间】 : {auth_time}
"""
                return account_info.strip()
            except Exception as e:
                return f"""
=====牛卡福货主查询失败=====
📱 账号: {safe_display}
❌ 错误: {str(e)[:50]}
=================="""
        else:
            return f"""
📝 【备注名称】 : {remark if remark else "账号"+str(index)}
📱 【牛卡福账号】 : {safe_display}
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
                future = executor.submit(process_single_account_query, account, index, total_count, account_remarks)
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
    match = re.search(r'牛卡福货主通知 ?(.*)', usermessage)
    if match:
        content = match.group(1).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：牛卡福货主通知 系统维护中")
        return
        
    sender.reply("⏳ 正在扫描授权用户并发送通知...")
    
    try:
        all_users = AccountManager.get_all_users()
        success_count = 0
        today = str(datetime.now().date())
        
        for uid in all_users:
            user_accounts = AccountManager.get_accounts(uid)
            has_auth = False
            for acc in user_accounts:
                vip_date = middleware.bucketGet(bucket='dd_nkf_auth', key=acc)
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                try:
                    # 【核心修复】：如果是管理员自己，强制使用reply回复，避免私聊被拦截
                    if str(uid) == str(userid):
                        sender.reply(f"📢 【牛卡福货主管理员通知】\n\n{content}")
                    else:
                        send_user_notice(uid, f"📢 【牛卡福货主管理员通知】\n\n{content}")
                    success_count += 1
                except: pass
        
        sender.reply(f"✅ 通知完成\n📢 已送达: {success_count} 人")
        
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
    """绑定账号 (核心逻辑更新: 手机号#Token)"""
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
        
        run_mode_text = "🌐 系统托管" if config['run_mode'] == 'system' else "🏠 本地运行"
        sender.reply(f"""
=====牛卡福货主 登录=====
当前模式: {run_mode_text}
------------------
格式：手机号#Token
例如：13812345678#eyJh...
------------------
支持批量提交，一行一个
⚠️ 格式必须正确，以确保能够实现Token更新!
------------------
回复"q"退出操作
==================""")
        
        input_str = get_user_input(timeout=120)
        if not input_str or input_str == 'q':
            sender.reply("✅ 已取消")
            return
        
        token_lines = []
        raw_lines = [line.strip() for line in input_str.split('\n') if line.strip()]
        for line in raw_lines:
            token_lines.append(line.strip())
        
        if not token_lines:
            sender.reply("❌ 内容为空")
            return

        sender.reply(f"⏳ 正在处理 {len(token_lines)} 个账号，请稍候...")
        
        for line in token_lines:
            try:
                # 解析格式 手机号#Token
                parts = line.split('#')
                if len(parts) != 2:
                    sender.reply(f"❌ 格式错误: {line[:15]}... (需包含手机号、Token)")
                    continue
                
                phone_id = parts[0].strip()
                full_token_str = parts[1].strip()
                
                if not phone_id.isdigit() or len(phone_id) != 11:
                     sender.reply(f"⚠️ 手机号格式错误: {phone_id}")
                     continue
                
                # 验证Token
                client = NiuKaFuClient(full_token_str)
                info_res = client.check_info()
                
                if info_res:
                    nick = info_res['nickname']
                    process_account_binding(full_token_str, phone_id, nick, remark) 
                else:
                     sender.reply(f"❌ 登录失败: Token无效 ({phone_id})")
            except Exception as ex:
                sender.reply(f"❌ 处理异常: {str(ex)}")
            
    except Exception as e:
        logger.error("绑定失败: " + str(e))
        sender.reply("❌ 绑定失败: " + str(e))

def process_account_binding(full_token, unique_id, nickname, remark=""):
    """处理绑定入库与同步"""
    try:
        account = unique_id # 手机号作为唯一标识
        
        accountVip = middleware.bucketGet(bucket='dd_nkf_auth', key=account)
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
        safe_display = account[:3] + "****" + account[-4:]

        # 核心逻辑：Upsert (添加或更新)
        AccountManager.add_account(userid, account) # 绑定到用户
        AccountManager.update_account_token(account, full_token) # 更新Token
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account, remark)
        
        # 同步逻辑
        ql_msg = ""
        if config['run_mode'] == 'system':
            if is_authorized:
                if sys_api.sync_env(full_token, account, remark, accountVip):
                    ql_msg = "\n🌐 状态: ✅ 系统已同步"
                else:
                    ql_msg = "\n🌐 状态: ❌ 系统同步失败"
            else:
                ql_msg = "\n🌐 状态: ⏸️ 未授权暂不同步"
        else:
            ql_msg = "\n🏠 状态: ✅ 本地已保存"

        sender.reply(f"""
=====牛卡福账号更新=====
✅ 处理成功!
👤 用户: {nickname}
📱 账号: {safe_display}{remark_info}
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
    account_list = "======我的牛卡福账号====="
    today_time = str(datetime.now().date())
    
    for account in accounts:
        accountVip = middleware.bucketGet(bucket='dd_nkf_auth', key=f'{account}')
        if len(accountVip) == 0: vip_status = '⚠️ 未授权'
        elif accountVip < today_time: vip_status = '❌ 已过期'
        else: vip_status = f'✅ {accountVip}'
        
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        remark_display = f" - {remark}" if remark else ""
        
        safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account
        
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
        token = AccountManager.get_token(account)
        if not token: token = ""
        accountVip = middleware.bucketGet(bucket='dd_nkf_auth', key=f'{account}')
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account
        
        # 菜单项构造：系统模式下不显示[4]立即运行
        menu_items = """
[1] 授权账号
[2] 删除账号
[3] 修改备注"""
        if config['run_mode'] == 'local':
            menu_items += "\n[4] 立即运行"
            
        sender.reply(f"""
=====账号详情=====
📱 账号: {safe_display}
📝 备注: {remark}
🔐 授权: {vip_status}
=================={menu_items}
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
            
            if process_payment('牛卡福货主授权', months, accountVip, token, account, account, account, remark):
                days = months * 30
                new_auth_time = empower(accountVip, days)
                middleware.bucketSet(bucket='dd_nkf_auth', key=f'{account}', value=new_auth_time)
                
                # 支付成功后，如果是系统模式，自动同步
                if config['run_mode'] == 'system' and token:
                    sys_api.sync_env(token, account, remark, new_auth_time)
                    sender.reply("🔄 授权成功并同步到系统！")
                else:
                    sender.reply("✅ 授权成功")
                
                money = Decimal(months) * config['xyVipmoney']
                sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")

        elif choice == '2': # 删除
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                AccountManager.remove_account(userid, account)
                middleware.bucketDel(bucket='dd_nkf_token', key=account)
                middleware.bucketDel(bucket='dd_nkf_auth', key=account)
                if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                # 系统同步删除
                if config['run_mode'] == 'system':
                    sys_api.delete_env(account)
                sender.reply("✅ 删除成功")

        elif choice == '3': # 备注
             sender.reply("请输入新备注:")
             new_remark = get_user_input()
             if new_remark and new_remark != 'q':
                 RemarkManager.set_account_remark(userid, account, new_remark)
                 if config['run_mode'] == 'system' and token:
                     sys_api.sync_env(token, account, new_remark, accountVip)
                 sender.reply("✅ 备注更新成功")
        
        elif choice == '4' and config['run_mode'] == 'local': # 立即运行
            # === 运行前强制鉴权 ===
            if not accountVip or accountVip < today_time:
                sender.reply("⛔️ 账号未授权或已过期，无法执行任务！\n请先回复 [1] 进行授权。")
                return

            sender.reply("⏳ 正在请求本地运行，请稍后...")
            if not token:
                sender.reply("❌ 账号Token失效")
                return
            client = NiuKaFuClient(token)
            log = client.execute_sign_task()
            sender.reply(f"=====运行结果=====\n{log}")

    except Exception as e:
        sender.reply(f"操作失败: {e}")

def process_payment(project, months, accountVip, token, phone, account, yt_account, remark=""):
    """复刻原版支付逻辑"""
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
            out_trade_no = f"NKF_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"牛卡福货主授权-{months}月",
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
            out_trade_no = f"NKF_BATCH_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"牛卡福货主批量-{count}号-{months}月",
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
            accountVip = middleware.bucketGet(bucket='dd_nkf_auth', key=account)
            new_date = empower(accountVip, months*30)
            middleware.bucketSet('dd_nkf_auth', account, new_date)
            
            token = AccountManager.get_token(account)
            curr_remark = account_remarks.get(account, "") if account_remarks else ""
            
            if config['run_mode'] == 'system' and token:
                sys_api.sync_env(token, account, curr_remark, new_date)
        except: pass
    
    sender.reply("✅ 批量授权完成")

def batch_delete_all_accounts(accounts):
    sender.reply("确认删除回复【确认删除】")
    if get_user_input() == "确认删除":
        for account in accounts:
             AccountManager.remove_account(userid, account)
             middleware.bucketDel(bucket='dd_nkf_token', key=account)
             middleware.bucketDel(bucket='dd_nkf_auth', key=account)
             if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
             if config['run_mode'] == 'system':
                 sys_api.delete_env(account)
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts():
    """定时任务：过期提醒与清理"""
    users = middleware.bucketAllKeys(bucket='dd_nkf_user')
    if not users:
        if sender.isAdmin() and usermessage in ['牛卡福货主清理', '清理牛卡福货主']:
            sender.reply("=====执行结果=====\n📭 暂无用户数据")
        return

    if sender.isAdmin() and usermessage in ['牛卡福货主清理', '清理牛卡福货主']:
        sender.reply(f"=====开始执行维护=====\n📊 扫描用户数: {len(users)}\n⚙️ 提醒天数: {config['reminder_days']}天\n⏳ 处理中...")

    cleaned_count = 0
    reminded_count = 0
    today_date = datetime.now().date()
    reminder_days_cfg = config['reminder_days']

    for user in users:
        try:
            accounts = AccountManager.get_accounts(user)
            if not accounts: continue
            
            valid_accounts = []
            user_has_change = False
            
            try:
                user_sender = middleware.Sender(user)
            except: continue

            for account in accounts:
                accountVip = middleware.bucketGet(bucket='dd_nkf_auth', key=account)
                
                if not accountVip:
                    expiration_date = today_date - timedelta(days=1)
                    expiration_str = "未授权"
                else:
                    try:
                        expiration_date = datetime.strptime(accountVip, "%Y-%m-%d").date()
                        expiration_str = accountVip
                    except:
                        expiration_date = today_date - timedelta(days=1)
                        expiration_str = "日期错误"

                days_diff = (expiration_date - today_date).days

                if days_diff > reminder_days_cfg:
                    valid_accounts.append(account)
                    continue
                
                if 0 <= days_diff <= reminder_days_cfg:
                    valid_accounts.append(account)
                    remind_key = f"{user}_{account}_{today_date}"
                    has_reminded = middleware.bucketGet('dd_nkf_remind_log', remind_key)
                    
                    if not has_reminded:
                        safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account
                        msg = f"""=====⏰ 到期提醒=====
您的牛卡福账号授权即将到期！
📱 账号: {safe_display}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                        send_user_notice(user, msg)
                        middleware.bucketSet('dd_nkf_remind_log', remind_key, "1")
                        reminded_count += 1
                    continue

                if days_diff < 0:
                    if config['run_mode'] == 'system':
                        sys_api.delete_env(account)
                    
                    middleware.bucketDel(bucket='dd_nkf_token', key=account)
                    middleware.bucketDel(bucket='dd_nkf_auth', key=account)
                    if config['enable_remark']:
                        RemarkManager.delete_account_remark(user, account)
                    
                    safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account
                    clean_msg = f"""=====🗑️ 过期清理通知=====
您的账号授权已过期并清理。
📱 账号: {safe_display}
📅 到期: {expiration_str}
------------------
相关配置已失效移除。
如需继续使用，请重新登录并授权。
=================="""
                    send_user_notice(user, clean_msg)
                    cleaned_count += 1
                    user_has_change = True

            if user_has_change:
                if valid_accounts:
                    middleware.bucketSet(bucket='dd_nkf_user', key=user, value=str(valid_accounts))
                else:
                    middleware.bucketDel(bucket='dd_nkf_user', key=user)

        except Exception as e:
            continue

    if sender.isAdmin() and usermessage in ['牛卡福货主清理', '清理牛卡福货主']:
        sender.reply(f"=====维护完成=====\n✅ 已清理过期: {cleaned_count}个\n📢 发送提醒: {reminded_count}个\n==================")


def admin_auth_options():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足\n只有管理员可以执行授权操作")
        return
    
    sender.reply("""=====授权管理=====

[1] 一键授权所有用户
[2] 指定用户授权

------------------
回复数字选择功能
回复"q"退出
==================""")
    choice = get_user_input(timeout=60)
    if choice is None or choice.lower() == 'q':
        sender.reply("✅ 已退出授权管理")
        return
    
    if choice == '1':
        admin_auth_all_users()
    elif choice == '2':
        admin_auth_specific_user()
    else:
        sender.reply("❌ 请输入有效的选项 (1或2)")

def admin_auth_all_users():
    all_users = AccountManager.get_all_users()
    if not all_users:
        sender.reply("📭 暂无绑定账号的用户")
        return
        
    sender.reply("请输入授权天数(如:30)\n回复q退出")
    days_str = get_user_input()
    if not days_str or days_str.lower() == 'q': return
    try:
        days = int(days_str)
        if days <= 0: raise ValueError
    except:
        sender.reply("❌ 无效天数")
        return
        
    sender.reply(f"⚠️ 即将为所有用户的所有账号授权 {days} 天。\n确认请回复【确认授权】")
    if get_user_input() != "确认授权":
        sender.reply("✅ 已取消操作")
        return
        
    success = 0
    sender.reply("⏳ 开始批量授权，请稍候...")
    for user in all_users:
        accounts = AccountManager.get_accounts(user)
        for account in accounts:
            try:
                accVip = middleware.bucketGet(bucket='dd_nkf_auth', key=account)
                new_vip = empower(accVip, days)
                middleware.bucketSet(bucket='dd_nkf_auth', key=account, value=new_vip)
                
                token = AccountManager.get_token(account)
                remark = RemarkManager.get_account_remark(user, account) if config['enable_remark'] else ""
                
                if config['run_mode'] == 'system' and token:
                    sys_api.sync_env(token, account, remark, new_vip)
                success += 1
            except: pass
    sender.reply(f"✅ 一键授权完成！成功处理 {success} 个账号。")

def admin_auth_specific_user():
    sender.reply("请输入要授权的QQ号(纯数字):\n回复q退出")
    target_qq = get_user_input()
    if not target_qq or target_qq.lower() == 'q': return
    if not target_qq.isdigit():
        sender.reply("❌ QQ号必须是纯数字")
        return
        
    target_accounts = AccountManager.get_accounts(target_qq)
    if not target_accounts:
        sender.reply(f"❌ QQ用户 {target_qq} 未绑定任何账号")
        return
        
    account_remarks = RemarkManager.get_all_remarks(target_qq) if config['enable_remark'] else {}
    today_time = str(datetime.now().date())
    
    msg = f"=====QQ {target_qq} 的账号====="
    for i, acc in enumerate(target_accounts, 1):
        accVip = middleware.bucketGet(bucket='dd_nkf_auth', key=acc)
        vip_st = '未授权' if not accVip else f"已授权({accVip})"
        rem = account_remarks.get(acc, "")
        rem_disp = f" - {rem}" if rem else ""
        safe_acc = acc[:3] + "****" + acc[-4:] if len(acc) == 11 else acc
        msg += f"\n[{i}] {safe_acc}{rem_disp} - {vip_st}"
    msg += "\n------------------\n回复数字选择账号\n回复 a 授权所有账号\n回复 q 退出\n=================="
    sender.reply(msg)
    
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    if sel.lower() == 'a':
        sender.reply("请输入授权天数(如:30)")
        d_str = get_user_input()
        if not d_str: return
        try: days = int(d_str)
        except: return sender.reply("❌ 无效天数")
        
        for acc in target_accounts:
            accVip = middleware.bucketGet(bucket='dd_nkf_auth', key=acc)
            new_vip = empower(accVip, days)
            middleware.bucketSet(bucket='dd_nkf_auth', key=acc, value=new_vip)
            
            token = AccountManager.get_token(acc)
            remark = account_remarks.get(acc, "")
            if config['run_mode'] == 'system' and token:
                sys_api.sync_env(token, acc, remark, new_vip)
        sender.reply(f"✅ 已为该QQ下所有账号授权 {days} 天")
        
    else:
        try:
            idx = int(sel) - 1
            if idx < 0 or idx >= len(target_accounts): raise ValueError
            acc = target_accounts[idx]
        except: return sender.reply("❌ 序号无效")
        
        safe_acc = acc[:3] + "****" + acc[-4:] if len(acc) == 11 else acc
        sender.reply(f"目标账号: {safe_acc}\n请输入授权天数(如:30)")
        d_str = get_user_input()
        if not d_str: return
        try: days = int(d_str)
        except: return sender.reply("❌ 无效天数")
        
        accVip = middleware.bucketGet(bucket='dd_nkf_auth', key=acc)
        new_vip = empower(accVip, days)
        middleware.bucketSet(bucket='dd_nkf_auth', key=acc, value=new_vip)
        
        token = AccountManager.get_token(acc)
        remark = account_remarks.get(acc, "")
        if config['run_mode'] == 'system' and token:
            sys_api.sync_env(token, acc, remark, new_vip)
        sender.reply(f"✅ 已为账号 {safe_acc} 授权 {days} 天\n⏰ 到期时间: {new_vip}")

def show_tutorial():
    sender.reply(f"""
=====牛卡福货主插件教程=====
当前模式: {'🌐 系统托管' if config['run_mode']=='system' else '🏠 本地运行'}

1️⃣ {config['randomsigncommand']}
   格式：手机号#Token
   支持批量，自动更新Token和同步

2️⃣ {config['randomquerycommand']}
   查询牛卡福货主积分与余额

3️⃣ {config['randommanagecommand']}
   续费、删除、[立即运行]

4️⃣ 牛卡福货主一键运行
   (管理员) 并发执行所有账号任务

5️⃣ 牛卡福货主清理 / 牛卡福货主授权
   清理过期并同步删除系统变量
   管理员进行全局或个人独立授权

⚠️ 变量名: {config['dd_hhtt_osname']}
==================""")

# ===================== 管理员一键运行 =====================
def run_task_single_quiet(user, account):
    """静默运行单个任务（含告警机制）"""
    try:
        # 1. 检查授权
        auth_date = middleware.bucketGet('dd_nkf_auth', account)
        if not auth_date or auth_date < str(datetime.now().date()):
            return None # 未授权跳过
        
        # 2. 获取Token
        token = AccountManager.get_token(account)
        if not token: return None
        
        # 3. 执行前检测Token失效并告警 (功能B)
        client = NiuKaFuClient(token)
        info = client.check_info()
        if not info:
            safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account
            alert_msg = f"⚠️【牛卡福货主】Token失效告警\n您的账号({safe_display}) Token已失效或过期！\n请重新抓包并发送“{config['randomsigncommand']}”更新Token，以免影响挂机收益。"
            try:
                # 避免管理员群发任务时疯弹自己，只有确实不一样的用户或者系统才发送
                if str(user) != str(userid):
                    send_user_notice(user, alert_msg)
            except: pass
            return f"❌ {account[-4:]}: 失效"
        
        # 4. 执行签到任务
        log = client.execute_sign_task()
        if "❌" in log:
            return f"🔴 {account[-4:]}: 失败"
        else:
            return f"🟢 {account[-4:]}: 成功"
    except Exception as e:
        return f"🔴 {account[-4:]}: 异常"

def batch_run_all_tasks_admin():
    """管理员全局运行"""
    if not sender.isAdmin(): return

    sender.reply("🚀 开始执行牛卡福货主全量任务 (本地模式)...")
    
    # 获取所有用户的所有账号，并携带上用户ID
    all_users = AccountManager.get_all_users()
    tasks = []
    for u in all_users:
        phones = AccountManager.get_accounts(u)
        for p in phones: tasks.append((u, p))
    
    total = len(tasks)
    if total == 0:
        sender.reply("⚠️ 系统无任何账号")
        return
        
    sender.reply(f"📊 扫描到 {total} 个账号，并发执行中...")
    
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_task = {executor.submit(run_task_single_quiet, t[0], t[1]): t for t in tasks}
        for future in as_completed(future_to_task):
            res = future.result()
            if res: results.append(res)
            
    success = sum(1 for r in results if "🟢" in r)
    fail = sum(1 for r in results if "🔴" in r)
    invalid = sum(1 for r in results if "❌" in r)
    
    # 汇总报告
    sender.reply(f"✅ 执行完毕\n成功: {success}\n失败: {fail}\n失效: {invalid}\n(未授权账号已自动跳过)")

# ===================== 主入口 =====================
try:
    # 自动定时任务入口 (由cron触发，模拟fake消息)
    if sender.getImtype() == 'fake':
        # 🟢 【修复Bug】: 触发所有到期提醒与过期清理任务
        clean_expired_accounts()
        
        # 如果是本地模式，cron触发时执行全量任务
        if config['run_mode'] == 'local':
            all_users = AccountManager.get_all_users()
            tasks = []
            for u in all_users:
                phones = AccountManager.get_accounts(u)
                for p in phones: tasks.append((u, p))
            
            if not tasks:
                logger.info("Cron任务执行结束: 系统无任何账号")
            else:
                results = []
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = [executor.submit(run_task_single_quiet, t[0], t[1]) for t in tasks]
                    for future in as_completed(futures):
                        res = future.result()
                        if res: results.append(res)
                
                success = sum(1 for r in results if "🟢" in r)
                fail = sum(1 for r in results if "🔴" in r)
                invalid = sum(1 for r in results if "❌" in r)
                
                # 🟢 【功能C】: 每天定时跑完后，给管理员发送全局汇总消息
                summary_msg = f"📊 今日牛卡福任务执行完毕。\n总账号：{len(tasks)} 个\n✅ 成功：{success} 个\n🔴 失败：{fail} 个\n❌ 失效：{invalid} 个"
                sender.reply(summary_msg) # 在Cron fake上下文中，reply默认会发给管理员(主人)
                logger.info(f"Cron任务执行完成: {summary_msg}")
    
    elif re.search(r'(通知|广播)', usermessage or ''):
        notify_authorized_users()
    elif re.search(r'(通知|广播)', usermessage or ''):
        notify_authorized_users()
    elif '登录' in usermessage or '登陆' in usermessage:
        bindaccount()
    elif '管理' in usermessage:
       xy_manage()
    elif '查询' in usermessage:
        cxs()
    elif usermessage in ['牛卡福货主清理', '清理牛卡福货主']:
        clean_expired_accounts()
    elif '通知' in usermessage:
        notify_authorized_users()
    elif usermessage == '牛卡福货主授权':
        admin_auth_options()
    elif usermessage == '牛卡福货主教程':
        show_tutorial()
    elif usermessage == '牛卡福货主一键运行':
        batch_run_all_tasks_admin()

except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")
