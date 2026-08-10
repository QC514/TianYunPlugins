# [rule: ^(爱仙居)(登录|登陆)$|^登(录|陆)(爱仙居)$|^(爱仙居)(查询|管理)$|^(查询|管理)(爱仙居)$|^爱仙居清理$|^爱仙居授权$|^爱仙居教程$|^爱仙居通知 ?(.*)$|^清理爱仙居$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 5 10 * * *]
# [public: true]
# [title: 爱仙居助手]
# [open_source: false]
# [class: 工具类]
# [version: 1.8]
# [price: 18.8]
# [admin: false]
# [author: 8165799]
# [service: 技术咨询QQ：8165799]
# [description: 爱仙居提交插件。<br>1. 支持短信/抓包登录。新增短信登录开关 1.7修复查询登录问题。<br>2.爱仙居登录、爱仙居管理、爱仙居授权 。<br> 📞 售后联系：QQ 8165799，售后群1003974618 br>]

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
logger = logging.getLogger('axj_plugin')

# 请求超时配置
REQUEST_TIMEOUT = 30 

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
usermessage = sender.getMessage()

_RUNTIME_BUCKET = "plugin_push_runtime"
_RUNTIME_KEY = "爱仙居"
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
# [param: {"required":true,"key":"dd_axj.dd_axj_qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"对接系统配置","desc":"必填项，青龙面板对接信息"}]
# [param: {"required":false,"key":"dd_axj.dd_axj_osname","bool":false,"placeholder":"默认:axj","name":"系统变量名","desc":"系统容器内变量名"}]
# [param: {"required":true,"key":"dd_axj.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_axj.hhttVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_axj.hhttcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"dd_axj.show_point_status","bool":true,"placeholder":"","name":"显示钱包状态","desc":"是否在查询结果中显示钱包金额"}]
# [param: {"required":true,"key":"dd_axj.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统"}]
# [param: {"required":true,"key":"dd_axj.enable_proxy","bool":true,"placeholder":"True/False","name":"是否启用代理","desc":"是否启用代理功能"}]
# [param: {"required":false,"key":"dd_axj.proxy_pool_url","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]
# [param: {"required":true,"key":"dd_axj.points_bucket","bool":false,"placeholder":"默认使用dd_sign_points","name":"积分桶名称","desc":"存储用户积分的桶名称"}]
# [param: {"required":true,"key":"dd_axj.enable_remark","bool":true,"placeholder":"True/False","name":"启用备注功能","desc":"是否启用账号备注功能"}]
# [param: {"required":false,"key":"dd_axj.enable_sms","bool":true,"placeholder":"True/False","name":"开启短信登录","desc":"是否允许使用短信登录(关闭后只能抓包)"}]
# [param: {"required":true,"key":"dd_axj.reminder_days","bool":false,"placeholder":"例:2","name":"到期提醒天数","desc":"到期前多少天开始发送提醒通知"}]
_shared_proxy = None

def getusercontent():
    """获取插件完整配置"""
    dd_hhtt_qlname = middleware.bucketGet('dd_axj', 'dd_axj_qlname') or ''
    dd_hhtt_osname = middleware.bucketGet('dd_axj', 'dd_axj_osname') or 'axj'
    
    if not dd_hhtt_qlname:
        sender.reply("❌ 配置错误：您未配置【对接系统配置】。\n请在插件配置中填写。")
        exit(0)
    
    dd_managecommand = middleware.bucketGet('dd_axj', 'dd_managecommand') or '爱仙居管理'
    dd_querycommand = middleware.bucketGet('dd_axj', 'dd_querycommand') or '爱仙居查询'
    dd_signcommand = middleware.bucketGet('dd_axj', 'dd_signcommand') or '爱仙居登录'
    zsm = middleware.bucketGet('dd_axj', 'zsm') or ''
    
    enable_proxy = middleware.bucketGet('dd_axj', 'enable_proxy') or 'false'
    enable_proxy = enable_proxy.lower() == 'true'
    proxy_pool_url = middleware.bucketGet('dd_axj', 'proxy_pool_url') or ''
    
    points_bucket = middleware.bucketGet('dd_axj', 'points_bucket') or 'dd_sign_points'
    
    enable_remark = middleware.bucketGet('dd_axj', 'enable_remark') or 'false'
    enable_remark = enable_remark.lower() == 'true'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    xyVipmoney = Decimal(middleware.bucketGet('dd_axj', 'hhttVipmoney') or '0')
    xycoin = int(middleware.bucketGet('dd_axj', 'hhttcoin') or '0')
    
    show_point_status = middleware.bucketGet('dd_axj', 'show_point_status') or 'false'
    show_point_status = show_point_status.lower() == 'true'
    
    use_ma_pay = middleware.bucketGet('dd_axj', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    reminder_days = int(middleware.bucketGet('dd_axj', 'reminder_days') or '2')
    
    enable_sms_val = middleware.bucketGet('dd_axj', 'enable_sms')
    enable_sms = enable_sms_val.lower() == 'true' if enable_sms_val else True

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
        'enable_sms': enable_sms == 'true' if isinstance(enable_sms, str) else bool(enable_sms),
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
        for owner in middleware.bucketAllKeys(bucket='dd_axj_user'):
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

def send_user_notice(user_id, msg, title="爱仙居助手通知"):
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
def generate_user_agent():
    import random
    android_v = random.choice(["10", "11", "12", "13", "14", "15"])
    model = random.choice(["SM-G998B", "V2049A", "M2102K1C", "PGM110", "PD2241"])
    build_id = f"{random.choice(['RP1A', 'SP1A', 'TP1A'])}.{random.randint(100000, 999999)}.0{random.randint(10, 99)}"
    chrome_v = f"{random.randint(110, 144)}.0.{random.randint(5000, 8000)}.132"
    return f"Mozilla/5.0 (Linux; Android {android_v}; {model} Build/{build_id}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/{chrome_v} Mobile Safari/537.36;xsb_xianju;xsb_xianju;2.1.3;native_app;7.8.0"

def empower(empowertime, days):
    """支持正数延期与负数扣除天数"""
    try:
        today_date = datetime.now().date()
        if not empowertime or empowertime <= str(today_date):
            delayed_date = today_date + timedelta(days=days)
        elif empowertime > str(today_date):
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            delayed_date = empower_date + timedelta(days=days)
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

# ===================== 核心逻辑类 (爱仙居适配版) =====================
class AiXianJuClient:
    def __init__(self, token_combined):
        self.session_id = ""
        self.account_id = ""
        
        parts = token_combined.split('#')
        if len(parts) >= 2:
            self.session_id = parts[0].strip()
            self.account_id = parts[1].strip()
        else:
            self.session_id = token_combined.strip()

        self.tenant_id = "62"
        self.base_url = "https://vapp.tmuyun.com"
        self.signature_salt = "FR*r!isE5W"
        self.client_id = str(uuid.uuid4())
        
        if len(parts) >= 3:
            test_ua = parts[2].strip()
            # 兼容旧的被WAF拦截的残缺UA，直接使用新生成的UA替换它
            if "Mozilla" not in test_ua:
                self.user_agent = generate_user_agent()
            else:
                self.user_agent = test_ua
        else:
            self.user_agent = generate_user_agent()

    def _get_proxies(self):
        import os
        axj_proxy = os.environ.get("axj_proxy", "")
        if axj_proxy:
            return {"http": axj_proxy, "https": axj_proxy}

        proxies = globals().get('_shared_proxy')
            
        if config.get('enable_proxy') and config.get('proxy_pool_url') and not proxies:
            try:
                import re
                res = requests.get(config['proxy_pool_url'], timeout=3)
                if res.status_code == 200:
                    proxy_ip = res.text.strip()
                    match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+)', proxy_ip)
                    if match:
                        proxy_ip = match.group(1)
                        proxies = {'http': f"http://{proxy_ip}", 'https': f"http://{proxy_ip}"}
                        globals()['_shared_proxy'] = proxies
            except: pass
        return proxies

    def _generate_signature(self, path, request_id, timestamp):
        if path.startswith("/api/v1"):
            path = path.replace("/api/v1", "")
        sign_string = f"{path}&&{self.session_id}&&{request_id}&&{timestamp}&&{self.signature_salt}&&{self.tenant_id}"
        return hashlib.sha256(sign_string.encode('utf-8')).hexdigest()

    def _request_main(self, method, path, params=None):
        request_id = str(uuid.uuid4())
        timestamp = str(int(time.time() * 1000))
        signature = self._generate_signature(path, request_id, timestamp)
        
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Chromium\";v=\"118\", \"Android WebView\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-With": "com.increator.cc.xianjusmk",
            "X-TENANT-ID": self.tenant_id,
            "X-SESSION-ID": self.session_id,
            "X-REQUEST-ID": request_id,
            "X-TIMESTAMP": timestamp,
            "X-SIGNATURE": signature,
            "X-ACCOUNT-ID": self.account_id,
        }
        url = f"{self.base_url}{path}"
        proxies = self._get_proxies()
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, verify=False, proxies=proxies, timeout=15)
            else:
                response = requests.post(url, headers=headers, json=params, verify=False, proxies=proxies, timeout=15)
            
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code} - {response.text[:100]}"}
            
            try:
                return response.json()
            except Exception as je:
                return {"error": f"非JSON响应: {response.text[:100]}"}
        except Exception as e:
            return {"error": str(e)}

    def _request_activity(self, method, url, headers_update, json_data=None):
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Chromium\";v=\"118\", \"Android WebView\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
            "sec-ch-ua-platform": "\"Android\"",
            "X-Requested-With": "com.increator.cc.xianjusmk",
            "X-TENANT-ID": self.tenant_id,
        }
        headers.update(headers_update)
        proxies = self._get_proxies()
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, verify=False, proxies=proxies, timeout=15)
            else:
                response = requests.post(url, headers=headers, json=json_data, verify=False, proxies=proxies, timeout=15)
                
            if response.status_code != 200:
                return {}
            return response.json()
        except: return {}

    def _request_lottery_info(self):
        """查询爱仙居抽奖状态 (替代失效的钱包接口)"""
        try:
            # 1. 获取任务Token
            headers1 = {"Content-Type": "application/json"}
            payload1 = {"q": "1GwxSBurLoUdKeZiyHuqn7u0cv2qTf081Qj/sdyPH2E=", "accountId": self.account_id, "sessionId": self.session_id, "tenantCode": "xsb_xianju"}
            res1 = self._request_activity("POST", "https://act.tmlyun.com/activity-api/task/h5/auth/userLogin", headers1, payload1)
            task_token = (res1.get("data") or {}).get("token")
            if not task_token: return "⚠️获取抽奖节点失败"

            # 2. 动态获取q值
            headers2 = {"Authorization": task_token}
            res2 = self._request_activity("GET", "https://act.tmlyun.com/activity-api/task/h5/activity/getActivityInfo", headers2)
            url = (res2.get("data") or {}).get("activityStyle", {}).get("lotteryButtonUrl", "")
            dynamic_q = "1GwxSBurLoUdKeZiyHuqn7u0cv2qTf081Qj/sdyPH2E="
            try:
                import urllib.parse
                q_parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('q', [None])[0]
                if q_parsed: dynamic_q = q_parsed
            except: pass

            # 3. 获取抽奖权限token
            import urllib.parse
            headers3 = {
                'Content-Type': "application/json", 
                'Origin': "https://act.tmlyun.com",
                'Referer': f"https://act.tmlyun.com/lottery/?q={urllib.parse.quote(dynamic_q)}&gaze_open=1"
            }
            payload3 = {"q": dynamic_q, "accountId": self.account_id, "sessionId": self.session_id, "tenantCode": "xsb_xianju"}
            res3 = self._request_activity("POST", "https://act.tmlyun.com/activity-api/lottery/api/auth/userLogin", headers3, payload3)
            auth_token = (res3.get("data") or {}).get("token")
            activity_id = (res3.get("data") or {}).get("thirdId", 569)
            if not auth_token: return "⚠️获取抽奖信息失败"

            # 4. 获取剩余次数
            headers4 = {'Authorization': auth_token}
            res4 = self._request_activity("GET", f"https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/frontPageNum?activityId={activity_id}", headers4)
            remain = (res4.get("data") or {}).get("remainPrizeNum", 0)
            return f"今日剩余可抽奖: {remain}次"
        except Exception as e:
            return f"❌抽奖信息查询失败"

    def check_info(self):
        """统一信息查询校验并获取详情"""
        try:
            # 1. 查询手机号
            user_res = self._request_main("GET", "/api/user_mumber/numberCenter", {"is_new": 1})
            mobile = "未知"
            if "error" not in user_res:
                data = user_res.get("data") or {}
                rst = data.get("rst") or {}
                if rst:
                    mobile = rst.get('mobile', '未知')
            else:
                logger.warning(f"尝试获取手机号失败(可能被服务端封堵)，转而强制继续获取核心钱包数据: {user_res.get('error')}")
            
            activity_id = 569
            remain = 0
            prize_records = []
            wallet_info = {"alipay": 0.0, "withdraw": 0.0, "total": 0.0}
            
            try:
                # 2. 获取任务Token
                headers1 = {"Content-Type": "application/json"}
                payload1 = {"q": "1GwxSBurLoUdKeZiyHuqn7u0cv2qTf081Qj/sdyPH2E=", "accountId": self.account_id, "sessionId": self.session_id, "tenantCode": "xsb_xianju"}
                res1 = self._request_activity("POST", "https://act.tmlyun.com/activity-api/task/h5/auth/userLogin", headers1, payload1)
                
                # 如果我们前面连手机号都没提取出来，这里依然抛出了网络错误，才是真挂了
                if "error" in res1 and mobile == "未知":
                    raise Exception(f"全网拦截或身份已彻底过期, 服务器回应阻断码: {res1.get('error')}")
                    
                task_token = (res1.get("data") or {}).get("token")
                
                if task_token:
                    # 3. 获取活动信息(q值和活动ID)
                    headers2 = {"Authorization": task_token}
                    res2 = self._request_activity("GET", "https://act.tmlyun.com/activity-api/task/h5/activity/getActivityInfo", headers2)
                    url = (res2.get("data") or {}).get("activityStyle", {}).get("lotteryButtonUrl", "")
                    dynamic_q = "1GwxSBurLoUdKeZiyHuqn7u0cv2qTf081Qj/sdyPH2E="
                    try:
                        import urllib.parse
                        q_parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query).get('q', [None])[0]
                        if q_parsed: dynamic_q = q_parsed
                    except: pass

                    # 4. 登录抽奖
                    import urllib.parse
                    headers3 = {
                        'Content-Type': "application/json", 
                        'Origin': "https://act.tmlyun.com",
                        'Referer': f"https://act.tmlyun.com/lottery/?q={urllib.parse.quote(dynamic_q)}&gaze_open=1"
                    }
                    payload3 = {"q": dynamic_q, "accountId": self.account_id, "sessionId": self.session_id, "tenantCode": "xsb_xianju"}
                    res3 = self._request_activity("POST", "https://act.tmlyun.com/activity-api/lottery/api/auth/userLogin", headers3, payload3)
                    
                    lottery_token = (res3.get("data") or {}).get("token")
                    activity_id_api = (res3.get("data") or {}).get("thirdId")
                    if activity_id_api:
                        activity_id = activity_id_api
                    
                    if lottery_token:
                        # 5. 获取剩余次数
                        headers4 = {'Authorization': lottery_token}
                        try:
                            res4 = self._request_activity("GET", f"https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/frontPageNum?activityId={activity_id}", headers4)
                            remain = int((res4.get("data") or {}).get("remainPrizeNum", 0))
                        except:
                            remain = 0
                            
                        u_value = None
                        try:
                            wallet_url = "https://act.tmlyun.com/activity-api/lottery/h5/activity/lottery/accountPrizeRecord/jumpEquityWallet"
                            headers_wallet = {
                                'Authorization': lottery_token,
                                'Referer': f'https://act.tmlyun.com/lottery/prizeRecord?q={urllib.parse.quote(dynamic_q)}'
                            }
                            res_jump = self._request_activity("GET", wallet_url, headers_wallet)
                            if "error" not in res_jump and res_jump.get("code") == 0 and res_jump.get("data"):
                                data_str = res_jump.get("data", "")
                                if "u=" in data_str:
                                    u_part = data_str.split("u=")[1].split("&")[0]
                                    u_value = urllib.parse.unquote(u_part)
                        except Exception as e:
                            logger.error(f"提取u_value异常: {e}")
                                        
                        # 7. 查询钱包余额
                        if u_value:
                            payload_u = {"u": u_value, "accountId": self.account_id, "sessionId": self.session_id}
                            res_u = self._request_activity("POST", "https://my.tmlyun.com/equity-api/user/auth/userLogin", headers1, payload_u)
                            user_token = (res_u.get("data") or {}).get("token")
                            if user_token:
                                h_w = {
                                    "Authorization": user_token,
                                    "X-REQUEST-ID": str(uuid.uuid4()),
                                    "sec-ch-ua-platform": '"Android"'
                                }
                                import urllib.parse
                                x_token = urllib.parse.unquote("dxA2jxuFFRjq5pngScCY2mol9UwV37AiJRZzxSWH6ZUDF4q+IAHP3vlc1ThxdvFAwoH30tw34I71U5ckf7l56g%3D%3D")
                                h_w["X-TOKEN"] = x_token
                                
                                device = f"00000000-{self.session_id[:4]}-{self.session_id[4:8]}-0000-0000{self.account_id[:8]}"
                                res_wallet = self._request_activity("GET", f"https://my.tmlyun.com/equity-api/redBag/getWalletInfo?device={device}", h_w)
                                
                                w_list = res_wallet.get("data", []) if res_wallet.get("success") else []
                                if w_list:
                                    w_data = w_list[0] if isinstance(w_list, list) and len(w_list) > 0 else {}
                                    wallet_info["total"] = w_data.get("totalPrice", 0.0)
                                    wallet_info["withdraw"] = w_data.get("totalTransPrice", 0.0)
                                    wallet_info["alipay"] = w_data.get("aliPayTotalPrice", 0.0)
            except Exception as inner_e:
                logger.error(f"查询核心部分出错，已容错: {inner_e}")

            return {
                "mobile": mobile,
                "wallet_info": wallet_info,
                "activity_id": activity_id,
                "remain_draws": remain,
                "prize_records": prize_records
            }
        except Exception as e:
            logger.error(f"外层查询出错: {str(e)}")
            raise e

    def get_captcha_image(self, phone):
        import uuid
        import time
        import hashlib
        import random
        import random
        
        client_id = "10016"
        url = "https://passport.tmuyun.com/web/security/send_security_code"
        req_id = str(uuid.uuid4())
        sig = hashlib.sha256(f"{uuid.uuid4()}{int(time.time()*1000)}".encode()).hexdigest()
        data = {"captcha": "0000", "client_id": client_id, "phone_number": phone}
        
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Chromium\";v=\"118\", \"Android WebView\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
            "sec-ch-ua-platform": "\"Android\"",
            "X-REQUEST-ID": req_id,
            "X-SIGNATURE": sig,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "X-TENANT-ID": self.tenant_id,
            "X-Requested-With": "com.increator.cc.xianjusmk",
        }
        try:
            sess = requests.Session()
            proxies = self._get_proxies()
            res1 = sess.post(url, data=data, headers=headers, verify=False, proxies=proxies, timeout=15)
            req_id_2 = str(uuid.uuid4())
            
            headers2 = {
                "X-REQUEST-ID": req_id_2, 
                "User-Agent": self.user_agent,
                "Accept": "application/json, text/plain, */*",
                "sec-ch-ua": "\"Chromium\";v=\"118\", \"Android WebView\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
                "sec-ch-ua-platform": "\"Android\"",
                "X-TENANT-ID": self.tenant_id,
                "X-Requested-With": "com.increator.cc.xianjusmk",
            }
            res = sess.get("https://passport.tmuyun.com/web/security/captcha_image", headers=headers2, proxies=proxies, verify=False, timeout=15)
            if res.status_code == 200 and res.content:
                import base64
                b64 = base64.b64encode(res.content).decode()
                return sess.cookies.get_dict(), b64
            else:
                err = f"获取验证码失败: HTTP {res.status_code} - {res.text[:50]}"
                logger.error(err)
                return err, None
        except Exception as e:
            err = f"网络异常: {str(e)}"
            logger.error(f"Captcha Fetch Error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return err, None

    def send_sms(self, phone, captcha, cookies):
        import uuid, time, hashlib
        client_id = "10016"
        url = "https://passport.tmuyun.com/web/security/send_security_code"
        req_id = str(uuid.uuid4())
        sig = hashlib.sha256(f"{uuid.uuid4()}{int(time.time()*1000)}".encode()).hexdigest()
        data = {"captcha": captcha, "client_id": client_id, "phone_number": phone}
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Chromium\";v=\"118\", \"Android WebView\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
            "sec-ch-ua-platform": "\"Android\"",
            "X-REQUEST-ID": req_id,
            "X-SIGNATURE": sig,
            "X-TENANT-ID": self.tenant_id,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "X-Requested-With": "com.increator.cc.xianjusmk",
        }
        try:
            proxies = self._get_proxies()
            res = requests.post(url, data=data, headers=headers, cookies=cookies, verify=False, proxies=proxies, timeout=15).json()
            if res.get("code") == 0:
                return True, res.get("message", "")
            else:
                logger.error(f"SMS Send Failed Data: {res}")
                return False, res.get("message", "短信发送失败")
        except Exception as e:
            logger.error(f"SMS Fetch Error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, str(e)
            
    def auth_login(self, phone, code, cookies):
        import uuid, time, hashlib
        client_id = "10016"
        url1 = "https://passport.tmuyun.com/web/oauth/security_code_auth"
        req_id = str(uuid.uuid4())
        sig = hashlib.sha256(f"{uuid.uuid4()}{int(time.time()*1000)}".encode()).hexdigest()
        data1 = {"client_id": client_id, "phone_number": phone, "security_code": code}
        headers1 = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "sec-ch-ua": "\"Chromium\";v=\"118\", \"Android WebView\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
            "sec-ch-ua-platform": "\"Android\"",
            "X-REQUEST-ID": req_id,
            "X-SIGNATURE": sig,
            "X-TENANT-ID": self.tenant_id,
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "X-Requested-With": "com.increator.cc.xianjusmk",
        }
        
        try:
            proxies = self._get_proxies()
            res1 = requests.post(url1, data=data1, headers=headers1, cookies=cookies, verify=False, proxies=proxies, timeout=15).json()
            if res1.get("code") != 0 or "authorization_code" not in res1.get("data", {}):
                return False, res1.get("message", "获取AuthCode失败")
                
            auth_code = res1["data"]["authorization_code"]["code"]
            
            mock_session_id = "68ff31bd3cbc283c4ca83496"
            path10 = "/api/zbtxz/login"
            req_id10 = str(uuid.uuid4())
            timestamp10 = str(int(time.time()*1000))
            
            saved_sess = self.session_id
            self.session_id = mock_session_id
            sig10 = self._generate_signature(path10, req_id10, timestamp10)
            self.session_id = saved_sess
            
            data10 = {"check_token": "", "code": auth_code, "token": "", "type": "-1", "union_id": ""}
            headers10 = {
                "User-Agent": self.user_agent,
                "X-SESSION-ID": mock_session_id,
                "X-REQUEST-ID": req_id10,
                "X-TIMESTAMP": timestamp10,
                "X-SIGNATURE": sig10,
                "X-TENANT-ID": self.tenant_id,
                "X-Requested-With": "com.increator.cc.xianjusmk",
                "Accept": "application/json, text/plain, */*",
                "sec-ch-ua": "\"Chromium\";v=\"118\", \"Android WebView\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
                "sec-ch-ua-platform": "\"Android\"",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            res10 = requests.post(f"https://vapp.tmuyun.com{path10}", data=data10, headers=headers10, verify=False, proxies=proxies, timeout=15).json()
            
            if res10.get("code") == 0 and "session" in res10.get("data", {}):
                real_sess = res10["data"]["session"]["id"]
                real_acc = res10["data"]["session"]["account_id"]
                return True, f"{real_sess}#{real_acc}#{self.user_agent}"
            logger.error(f"Final Auth Login Failed Data: {res10}")
            return False, res10.get("message", "最终登录失败")
        except Exception as e:
            logger.error(f"Auth Login Error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return False, str(e)

# ===================== 管理器类 =====================
class RemarkManager:
    @staticmethod
    def get_account_remark(user_id, account_id):
        try:
            remark_data = middleware.bucketGet(bucket='dd_axj_remarks', key=f'{user_id}_{account_id}')
            if remark_data: return remark_data
            return ""
        except: return ""
    
    @staticmethod
    def set_account_remark(user_id, account_id, remark):
        try:
            remark_clean = remark.strip()[:20]
            if remark_clean:
                middleware.bucketSet(bucket='dd_axj_remarks', key=f'{user_id}_{account_id}', value=remark_clean)
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
            middleware.bucketDel(bucket='dd_axj_remarks', key=f'{user_id}_{account_id}')
            return True
        except: return False

class AccountManager:
    @staticmethod
    def get_accounts(user_id):
        try:
            value = middleware.bucketGet(bucket='dd_axj_user', key=user_id)
            if not value: return []
            if value.startswith('[') and value.endswith(']'):
                try:
                    accounts = eval(value)
                    if isinstance(accounts, (list, tuple, set)):
                        accounts = list(dict.fromkeys(accounts))
                    return accounts
                except: pass
            return [str(value)]
        except: return []

    @staticmethod
    def add_account(user_id, account):
        try:
            accounts = AccountManager.get_accounts(user_id)
            if account not in accounts:
                accounts.append(account)
                middleware.bucketSet(bucket='dd_axj_user', key=user_id, value=str(accounts))
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
                    middleware.bucketSet(bucket='dd_axj_user', key=user_id, value=str(accounts))
                else:
                    middleware.bucketDel(bucket='dd_axj_user', key=user_id)
                return True
            return False
        except: return False
    
    @staticmethod
    def update_account_token(account, token):
        try:
            encrypted_token = encrypt_token(token)
            middleware.bucketSet(bucket='dd_axj_token', key=account, value=encrypted_token)
            return True
        except: return False
    
    @staticmethod
    def get_token(account):
        try:
            enc = middleware.bucketGet(bucket='dd_axj_token', key=account)
            return decrypt_token(enc) if enc else None
        except: return None

    @staticmethod
    def get_all_users():
        try:
            users = middleware.bucketAllKeys(bucket='dd_axj_user')
            user_list = []
            for user in users:
                accounts = AccountManager.get_accounts(user)
                if accounts: user_list.append(user)
            return user_list
        except: return []

# ===================== 系统对接模块(青龙) =====================
class SystemAPI:
    def __init__(self):
        self.enabled = False
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
        if not self.enabled: return None
        try:
            envs = self.get_all_envs()
            for env in envs:
                if env.get('name') != config['dd_hhtt_osname']: continue
                
                # 优先手机号匹配防重复
                if env.get('remarks') and str(phone) in env.get('remarks'): 
                    return env.get('id')
                
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
        if not self.enabled: return False
        try:
            env_id = self.find_env(phone, token)
            
            remarks_parts = [f'爱仙居:{phone}']
            if auth_time: remarks_parts.append(f'到期:{auth_time}')
            else: remarks_parts.append('到期:未授权')
            if remark: remarks_parts.append(f'备注:{remark}')
            owner_user = get_owner_user_id(account if 'account' in locals() else phone if 'phone' in locals() else user_id if 'user_id' in locals() else '', owner_user_id if 'owner_user_id' in locals() else None)
            if not owner_user:
                raise Exception("无法确认账号真实归属，已阻止写入面板备注，避免青龙数据错乱")
            remarks_parts.extend([f'用户:{owner_user}', '爱仙居提交'])
            final_remark = '丨'.join(remarks_parts)

            headers = {"Authorization": f"Bearer {self.qltoken}", "Content-Type": "application/json"}
            url = f"{self.QLurl}/open/envs"

            if env_id:
                data = {"value": token, "name": config['dd_hhtt_osname'], "remarks": final_remark, "id": env_id}
                requests.put(url, headers=headers, json=data, timeout=10)
            else:
                data = [{"value": token, "name": config['dd_hhtt_osname'], "remarks": final_remark}]
                requests.post(url, headers=headers, json=data, timeout=10)
            return True
        except: return False

# 初始化系统API
class DummySysAPI:
    def sync_env(self, *args, **kwargs): return False
    def delete_env(self, *args, **kwargs): return False

sys_api = DummySysAPI()
try:
    _temp_api = SystemAPI()
    if getattr(_temp_api, 'enabled', False):
        sys_api = _temp_api
except:
    pass

# ===================== 功能逻辑 =====================

def process_single_account_query(account, index, total_count, account_remarks):
    try:
        full_token = AccountManager.get_token(account)
        if not full_token: full_token = "No Token"
        
        accountVip = middleware.bucketGet(bucket='dd_axj_auth', key=f'{account}')
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        if len(accountVip) == 0:
            auth_time = "无"
        elif accountVip <= today_time:
            auth_time = f"{accountVip} (已过期)"
        else:
            auth_time = accountVip
        
        safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account

        if len(accountVip) != 0 and accountVip > today_time:
            try:
                client = AiXianJuClient(full_token)
                info = client.check_info()
                
                w = info['wallet_info']
                pr = info['prize_records']
                pr_str = "\n".join(pr) if pr else "- 暂无中奖记录"
                
                mobile_disp = info['mobile']
                if mobile_disp == "未知":
                    mobile_disp = safe_display
                else:
                    mobile_disp = mobile_disp[:3] + "****" + mobile_disp[-4:] if len(mobile_disp) == 11 else mobile_disp
                
                account_info = f"""
=====爱仙居详情=====
📱 账号：{mobile_disp}
💰 余额：{w['alipay']}元
📩 提现：{w['withdraw']}元
📊 累计：{w['total']}元
⏰ 授权到期：{auth_time}
--------------------
🎯 今日活动ID：{info['activity_id']}
🎰 当前剩余抽奖次数：{info['remain_draws']}
🎁 最近中奖记录：
{pr_str}
"""
                return account_info.strip()
            except Exception as e:
                return f"""
=====爱仙居查询失败=====
📱 账号: {safe_display}
❌ 错误: {str(e)[:50]}
=================="""
        else:
            return f"""
📝 【备注名称】 : {remark if remark else "账号"+str(index)}
📱 【绑机账号】 : {safe_display}
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
            future_to_index = {}
            for index, account in enumerate(accounts, 1):
                future = executor.submit(process_single_account_query, account, index, total_count, account_remarks)
                future_to_index[future] = index - 1 

            results = [""] * total_count
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                results[idx] = future.result()
                
            for res in results:
                if res: sender.reply(res)
                
    except Exception as e:
        logger.error("批量查询失败: " + str(e))
        sender.reply("❌ 查询失败: " + str(e))

def notify_authorized_users():
    if not sender.isAdmin():
        sender.reply("❌ 只有管理员可以使用此功能")
        return
    
    content = ""
    match = re.search(r'爱仙居通知 ?(.*)', usermessage, re.DOTALL)
    if match:
        content = match.group(1).strip()
    
    if not content:
        sender.reply("❌ 请输入通知内容，例如：爱仙居通知 系统维护中")
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
                vip_date = middleware.bucketGet(bucket='dd_axj_auth', key=acc)
                if vip_date and vip_date >= today:
                    has_auth = True
                    break
            
            if has_auth:
                try:
                    send_user_notice(uid, f"📢 【爱仙居管理员通知】\n\n{content}")
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
        
        if config.get('enable_sms', True):
            sender.reply(f"""
=====爱仙居账号绑定=====
请选择登录方式：
[1] 短信登录 (推荐，自动获取Token)
[2] Token登录 (手动提交Token/抓包)
------------------
回复数字选择，Q退出
==================""")
            
            login_type = get_user_input(timeout=120)
            if not login_type or login_type.lower() == 'q':
                sender.reply("✅ 已取消")
                return
        else:
            # 如果后台关闭了短信登录功能，直接跳过选单，强制采用手工 Token 登录方式
            login_type = '2'

        if login_type == '1':
            if not config.get('enable_sms', True):
                sender.reply("❌ 管理员已在后台关闭短信登录功能！\n由于官方风控升级，短信提取账号可能无法产生阅读收益。\n请回复 Q 退出并选择 [2] 提交手机抓包获取的长Token！")
                return
            sender.reply("请输入11位手机号码(Q退出)：")
            phone = get_user_input(timeout=120)
            if not phone or phone.lower() == 'q': return
            if len(phone) != 11 or not phone.isdigit():
                sender.reply("❌ 手机号格式错误")
                return
                
            client = AiXianJuClient("")
            cookies_or_err, b64_img = client.get_captcha_image(phone)
            if not b64_img:
                sender.reply(f"❌ {cookies_or_err}")
                return
            
            cookies = cookies_or_err
                
            sender.reply("请查看下方图形验证码，输入图中数字 (Q退出)：")
            try:
                import os
                import base64
                img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"axj_cap_{phone}.jpg")
                with open(img_path, 'wb') as f:
                    f.write(base64.b64decode(b64_img))
                
                # 尝试用本地绝对路径发送图片
                try:
                    sender.replyImage(img_path)
                except:
                    pass
                
                # 同时发送 Base64 CQ码作为兜底，防止有些框架不支持本地路径
                sender.reply(f"[CQ:image,file=base64://{b64_img}]")
            except Exception as e:
                sender.reply(f"[CQ:image,file=base64://{b64_img}]")
                
            captcha = get_user_input(timeout=120)
            if not captcha or captcha.lower() == 'q': return
            
            success, msg = client.send_sms(phone, captcha, cookies)
            if not success:
                sender.reply(f"❌ 发送短信失败: {msg}")
                return
                
            sender.reply("✅ 短信发送成功！请输入您收到的短信验证码 (Q退出)：")
            sms_code = get_user_input(timeout=120)
            if not sms_code or sms_code.lower() == 'q': return
            
            sender.reply("⏳ 正在登录提取变量中，请稍候...")
            auth_success, result = client.auth_login(phone, sms_code, cookies)
            
            if auth_success:
                full_token_str = result
                sender.reply(f"🎉 登录成功！正在为您自动绑定...")
                
                info_client = AiXianJuClient(full_token_str)
                info_res = info_client.check_info()
                if info_res:
                    nick = info_res.get('nickname', '未设置昵称')
                    process_account_binding(full_token_str, phone, nick, remark)
                else:
                    process_account_binding(full_token_str, phone, "未知用户", remark)
            else:
                sender.reply(f"❌ 登录失败: {result}")
                return
                
        elif login_type == '2':
            sender.reply(f"""
=====Token登录=====
当前模式: 🌐 系统(青龙)托管
------------------
格式：手机号#X-SESSION-ID#X-ACCOUNT-ID
例如：13812345678#xxxx#yyyy 或 13812345678#xxxx#yyyy#ua参数
------------------
支持批量提交，一行一个
⚠️ 格式必须正确，以便后续换Token时自动覆盖防重复!
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
                    parts = line.split('#')
                    if len(parts) < 3:
                        sender.reply(f"❌ 格式错误: {line[:15]}... (需包含手机号及两段Token)")
                        continue
                    
                    phone_id = parts[0].strip()
                    full_token_str = "#".join(parts[1:]).strip()
                    
                    if not phone_id.isdigit() or len(phone_id) != 11:
                         sender.reply(f"⚠️ 手机号格式错误: {phone_id}")
                         continue
                    
                    
                    try:
                        client = AiXianJuClient(full_token_str)
                        info_res = client.check_info()
                        nick = info_res.get('nickname', '未设置昵称')
                        process_account_binding(full_token_str, phone_id, nick, remark) 
                    except Exception as verify_err:
                         sender.reply(f"❌ 登录失败: {str(verify_err)} ({phone_id})")
                except Exception as ex:
                    sender.reply(f"❌ 处理异常: {str(ex)}")
        else:
            sender.reply("❌ 无效选择")
            
    except Exception as e:
        logger.error("绑定失败: " + str(e))
        sender.reply("❌ 绑定失败: " + str(e))

def process_account_binding(full_token, unique_id, nickname, remark=""):
    try:
        account = unique_id 
        
        accountVip = middleware.bucketGet(bucket='dd_axj_auth', key=account)
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

        AccountManager.add_account(userid, account)
        AccountManager.update_account_token(account, full_token) 
        
        if config['enable_remark'] and remark:
            RemarkManager.set_account_remark(userid, account, remark)
        
        ql_msg = ""
        if is_authorized:
            if sys_api.sync_env(full_token, account, remark, accountVip):
                ql_msg = "\n🌐 状态: ✅ 系统已同步"
            else:
                ql_msg = "\n🌐 状态: ❌ 系统同步失败"
        else:
            ql_msg = "\n🌐 状态: ⏸️ 未授权暂不同步"

        sender.reply(f"""
=====爱仙居账号更新=====
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
    account_list = "======我的爱仙居账号====="
    today_time = str(datetime.now().date())
    
    for account in accounts:
        accountVip = middleware.bucketGet(bucket='dd_axj_auth', key=f'{account}')
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
        accountVip = middleware.bucketGet(bucket='dd_axj_auth', key=f'{account}')
        remark = account_remarks.get(account, "") if config['enable_remark'] else ""
        
        today_time = str(datetime.now().date())
        vip_status = '⚠️ 未授权' if not accountVip else ('❌ 已过期' if accountVip < today_time else f'✅ {accountVip}')
        
        safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account
        
        menu_items = """
[1] 授权账号
[2] 删除账号
[3] 修改备注"""
            
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
            
            if process_payment('爱仙居授权', months, accountVip, token, account, account, account, remark):
                days = months * 30
                new_auth_time = empower(accountVip, days)
                middleware.bucketSet(bucket='dd_axj_auth', key=f'{account}', value=new_auth_time)
                
                if token:
                    sys_api.sync_env(token, account, remark, new_auth_time)
                    sender.reply("🔄 授权成功并同步到系统！")
                else:
                    sender.reply("✅ 授权成功")
                
                money = Decimal(months) * config['xyVipmoney']
                sender.reply(f"=====订单完成=====\n💰 金额: {money}元\n📅 到期: {new_auth_time}")

        elif choice == '2':
            sender.reply("确认删除回复【y】")
            if get_user_input() == 'y':
                AccountManager.remove_account(userid, account)
                middleware.bucketDel(bucket='dd_axj_token', key=account)
                middleware.bucketDel(bucket='dd_axj_auth', key=account)
                if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
                sys_api.delete_env(account)
                sender.reply("✅ 删除成功")

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
            out_trade_no = f"AXJ_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"爱仙居授权-{months}月",
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
            out_trade_no = f"AXJ_BATCH_{int(time.time())}{userid}"
            params = {
                'pid': conf['pid'],
                'type': 'alipay',
                'out_trade_no': out_trade_no,
                'name': f"爱仙居批量-{count}号-{months}月",
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
            accountVip = middleware.bucketGet(bucket='dd_axj_auth', key=account)
            new_date = empower(accountVip, months*30)
            middleware.bucketSet('dd_axj_auth', account, new_date)
            
            token = AccountManager.get_token(account)
            curr_remark = account_remarks.get(account, "") if account_remarks else ""
            
            if token:
                sys_api.sync_env(token, account, curr_remark, new_date)
        except: pass
    
    sender.reply("✅ 批量授权完成")

def batch_delete_all_accounts(accounts):
    sender.reply("确认删除回复【确认删除】")
    if get_user_input() == "确认删除":
        for account in accounts:
             AccountManager.remove_account(userid, account)
             middleware.bucketDel(bucket='dd_axj_token', key=account)
             middleware.bucketDel(bucket='dd_axj_auth', key=account)
             if config['enable_remark']: RemarkManager.delete_account_remark(userid, account)
             sys_api.delete_env(account)
        sender.reply("✅ 批量删除完成")

def clean_expired_accounts():
    users = middleware.bucketAllKeys(bucket='dd_axj_user')
    if not users:
        if sender.isAdmin() and usermessage in ['爱仙居清理', '清理爱仙居']:
            sender.reply("=====执行结果=====\n📭 暂无用户数据")
        return

    if sender.isAdmin() and usermessage in ['爱仙居清理', '清理爱仙居']:
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
                accountVip = middleware.bucketGet(bucket='dd_axj_auth', key=account)
                
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
                    has_reminded = middleware.bucketGet('dd_axj_remind_log', remind_key)
                    
                    if not has_reminded:
                        safe_display = account[:3] + "****" + account[-4:] if len(account) == 11 and account.isdigit() else account
                        msg = f"""=====⏰ 到期提醒=====
您的爱仙居账号授权即将到期！
📱 账号: {safe_display}
📅 到期: {expiration_str} (剩余 {days_diff} 天)
------------------
为避免影响挂机，请及时续费。
发送 {config['randommanagecommand']} 进行续费
=================="""
                        send_user_notice(user, msg)
                        middleware.bucketSet('dd_axj_remind_log', remind_key, "1")
                        reminded_count += 1
                    continue

                if days_diff < 0:
                    sys_api.delete_env(account)
                    
                    middleware.bucketDel(bucket='dd_axj_token', key=account)
                    middleware.bucketDel(bucket='dd_axj_auth', key=account)
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
                    middleware.bucketSet(bucket='dd_axj_user', key=user, value=str(valid_accounts))
                else:
                    middleware.bucketDel(bucket='dd_axj_user', key=user)

        except Exception as e:
            continue

    if sender.isAdmin() and usermessage in ['爱仙居清理', '清理爱仙居']:
        sender.reply(f"=====维护完成=====\n✅ 已清理过期: {cleaned_count}个\n📢 发送提醒: {reminded_count}个\n==================")

def admin_auth_options():
    if not sender.isAdmin():
        sender.reply("❌ 权限不足\n只有管理员可以执行授权操作")
        return
    
    sender.reply("""=====授权管理=====

[1] 一键授权所有用户
[2] 指定用户授权 (支持加减时间)

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
        
    sender.reply("请输入授权天数(正数增加，负数如 -10 扣除):\n回复q退出")
    days_str = get_user_input()
    if not days_str or days_str.lower() == 'q': return
    try:
        days = int(days_str)
    except:
        sender.reply("❌ 无效天数")
        return
        
    sender.reply(f"⚠️ 即将为所有用户的所有账号改变 {days} 天期限。\n确认请回复【确认授权】")
    if get_user_input() != "确认授权":
        sender.reply("✅ 已取消操作")
        return
        
    success = 0
    sender.reply("⏳ 开始批量授权，请稍候...")
    for user in all_users:
        accounts = AccountManager.get_accounts(user)
        for account in accounts:
            try:
                accVip = middleware.bucketGet(bucket='dd_axj_auth', key=account)
                new_vip = empower(accVip, days)
                middleware.bucketSet(bucket='dd_axj_auth', key=account, value=new_vip)
                
                token = AccountManager.get_token(account)
                remark = RemarkManager.get_account_remark(user, account) if config['enable_remark'] else ""
                
                if token:
                    sys_api.sync_env(token, account, remark, new_vip)
                success += 1
            except: pass
    sender.reply(f"✅ 一键授权完成！成功处理 {success} 个账号。")

def admin_auth_specific_user():
    sender.reply("请输入该用户的奥特曼用户标识(QQ号或微信wxid):\n回复q退出")
    target_qq = get_user_input()
    if not target_qq or target_qq.lower() == 'q': return
    target_qq = target_qq.strip()
        
    target_accounts = AccountManager.get_accounts(target_qq)
    if not target_accounts:
        sender.reply(f"❌ 用户 {target_qq} 未绑定任何账号")
        return
        
    account_remarks = RemarkManager.get_all_remarks(target_qq) if config['enable_remark'] else {}
    
    msg = f"=====用户 {target_qq} 的账号====="
    for i, acc in enumerate(target_accounts, 1):
        accVip = middleware.bucketGet(bucket='dd_axj_auth', key=acc)
        vip_st = '未授权' if not accVip else f"已授权({accVip})"
        rem = account_remarks.get(acc, "")
        rem_disp = f" - {rem}" if rem else ""
        safe_acc = acc[:3] + "****" + acc[-4:] if len(acc) == 11 else acc
        msg += f"\n[{i}] {safe_acc}{rem_disp} - {vip_st}"
    msg += "\n------------------\n回复数字选择账号\n回复 a 操作所有账号\n回复 q 退出\n=================="
    sender.reply(msg)
    
    sel = get_user_input()
    if not sel or sel.lower() == 'q': return
    
    if sel.lower() == 'a':
        sender.reply("请输入改变的天数(正数增加，负数如 -10 扣除):")
        d_str = get_user_input()
        if not d_str: return
        try: days = int(d_str)
        except: return sender.reply("❌ 无效天数")
        
        for acc in target_accounts:
            accVip = middleware.bucketGet(bucket='dd_axj_auth', key=acc)
            new_vip = empower(accVip, days)
            middleware.bucketSet(bucket='dd_axj_auth', key=acc, value=new_vip)
            
            token = AccountManager.get_token(acc)
            remark = account_remarks.get(acc, "")
            if token:
                sys_api.sync_env(token, acc, remark, new_vip)
        sender.reply(f"✅ 已操作该用户下所有账号 {days} 天")
        
    else:
        try:
            idx = int(sel) - 1
            if idx < 0 or idx >= len(target_accounts): raise ValueError
            acc = target_accounts[idx]
        except: return sender.reply("❌ 序号无效")
        
        safe_acc = acc[:3] + "****" + acc[-4:] if len(acc) == 11 else acc
        sender.reply(f"目标账号: {safe_acc}\n请输入改变的天数(正数增加，负数如 -10 扣除):")
        d_str = get_user_input()
        if not d_str: return
        try: days = int(d_str)
        except: return sender.reply("❌ 无效天数")
        
        accVip = middleware.bucketGet(bucket='dd_axj_auth', key=acc)
        new_vip = empower(accVip, days)
        middleware.bucketSet(bucket='dd_axj_auth', key=acc, value=new_vip)
        
        token = AccountManager.get_token(acc)
        remark = account_remarks.get(acc, "")
        if token:
            sys_api.sync_env(token, acc, remark, new_vip)
        sender.reply(f"✅ 已为账号 {safe_acc} 操作 {days} 天\n⏰ 最新到期时间: {new_vip}")

def show_tutorial():
    sender.reply(f"""
=====爱仙居插件教程=====
当前模式: 🌐 提交到青龙面板

1️⃣ {config['randomsigncommand']}
   格式：手机号#X-SESSION_ID#X-ACCOUNT_ID
   支持批量，全自动更新覆盖Token和同步

2️⃣ {config['randomquerycommand']}
   查询爱仙居余额与资产

3️⃣ {config['randommanagecommand']}
   续费、删除、修改备注

4️⃣ 爱仙居清理 / 爱仙居授权
   清理过期并同步删除系统变量
   管理员进行全局或个人独立授权(支持加减天数)
==================""")

# ===================== 主入口 =====================
try:
    if sender.getImtype() == 'fake':
        clean_expired_accounts()
    
    elif usermessage == config['dd_signcommand'] or any(kw in usermessage for kw in ['爱仙居登录', '爱仙居登陆', '登录爱仙居', '登陆爱仙居']):
        bindaccount()
    elif usermessage == config['dd_managecommand'] or usermessage in ['爱仙居管理', '管理爱仙居']:
       xy_manage()
    elif usermessage == config['dd_querycommand'] or usermessage in ['爱仙居查询', '查询爱仙居']:
        cxs()
    elif usermessage in ['爱仙居清理', '清理爱仙居']:
        clean_expired_accounts()
    elif usermessage.startswith('爱仙居通知'):
        notify_authorized_users()
    elif usermessage == '爱仙居授权':
        admin_auth_options()
    elif usermessage == '爱仙居教程':
        show_tutorial()

except Exception as e:
    logger.error(f"Error: {e}")
    sender.reply(f"❌ 系统错误: {e}")
