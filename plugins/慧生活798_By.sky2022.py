# [rule: ^慧生活(登录|登陆)$|^登(录|陆)慧生活$|^慧生活(查询|管理)$|^(查询|管理)慧生活$|^慧生活授权$|^慧生活教程$|^慧生活后台$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 0 0 1 * * *]
# [public: true]
# [title: 慧生活798]
# [icon: https://i.ilife798.com/favicon.ico]
# [open_source: false]
# [class: 工具类]
# [version: 1.1]
# [price: 9.88]
# [admin: false]
# [author: sky2022]
# [service: 2661320550]
# [description: 介绍：慧生活798插件，每日310积分左右，支持手机号验证码登录和Token登录<br>内置任务：每天凌晨1点自动执行每日签到、观看广告、观看视频、支付宝视频，完成后推送结果给对应用户<br>指令：慧生活登录、慧生活管理、慧生活查询、慧生活授权、慧生活教程]
# [param: {"required":true,"key":"dd_hsh.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_hsh.hshVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_hsh.hshcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_hsh.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]

import re
from datetime import datetime, timedelta
import middleware
import urllib.parse
from decimal import Decimal
import requests
import time
import json
import hashlib
import random
import base64

# 禁用SSL警告
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_hsh_user', key=userid)

# ==================== 通用工具函数 ====================

def format_message(title, content, status="info"):
    """统一的消息格式化函数"""
    status_icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
        "loading": "⏳"
    }
    icon = status_icons.get(status, "ℹ️")
    return f"{icon} {title}\n{content}"

def format_account_info(uid, auth_status, auth_time, **kwargs):
    """格式化账号信息显示"""
    info = f"=====================\n👤 账号: {uid}"

    if 'current_score' in kwargs:
        info += f"\n💎 当前积分: {kwargs['current_score']}"
    if 'today_score' in kwargs:
        info += f"\n🎯 今日积分: {kwargs['today_score']}"
    if 'total_score' in kwargs:
        info += f"\n📊 总积分: {kwargs['total_score']}"
    if 'auth_time' in kwargs:
        info += f"\n📅 授权到期: {kwargs['auth_time']}"
    else:
        info += f"\n📅 授权到期: {auth_time}"
    if 'account_status' in kwargs:
        info += f"\n📈 账号检测: {kwargs['account_status']}"

    info += "\n====================="
    return info

def generate_qrcode(url):
    """生成二维码图片"""
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception as e:
        print(f"生成二维码失败: {str(e)}")
        return None

def send_qrcode_image(sender, qrcode_url, pay_type):
    """发送二维码图片"""
    pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
    pay_type_name = pay_type_names.get(pay_type, pay_type)

    try:
        sender.replyImage(qrcode_url)
        if pay_type == 'qqpay':
            sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\nQQ支付打开图片若是黑屏，长按屏幕进行\"识别二维码\"即可！\n支付过程中输入'q'可取消支付")
        else:
            sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付")
    except:
        if pay_type == 'qqpay':
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！\n[CQ:image,file={qrcode_url}]'
        else:
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n[CQ:image,file={qrcode_url}]'
        sender.reply(pay_msg)

def validate_input(value, max_count, field_name="输入"):
    """验证用户输入"""
    try:
        value = int(value)
        if value > max_count or value == 0:
            sender.reply(format_message("输入无效", f"请输入 1-{max_count} 之间的数字", "error"))
            exit(0)
        return value
    except ValueError:
        sender.reply(format_message("输入无效", f"{field_name}必须是数字", "error"))
        exit(0)

def get_user_choice(prompt, timeout=120000, allow_quit=True):
    """获取用户选择，统一处理超时和退出"""
    choice = sender.input(timeout, 1, False)
    if choice is None or choice == 'timeout':
        sender.reply('⏰ 操作超时,已退出')
        exit(0)
    elif allow_quit and (choice == 'q' or choice == 'Q'):
        sender.reply('✅ 已退出操作')
        exit(0)
    return choice

def mask_phone(phone):
    """手机号脱敏处理"""
    if len(phone) >= 11:
        return phone[:3] + '*' * 4 + phone[7:]
    return phone

def parse_accounts(account_data):
    """解析并去重账号列表"""
    if not account_data:
        return []
    try:
        accounts = eval(account_data)
        if isinstance(accounts, (list, tuple, set)):
            return list(dict.fromkeys(accounts))
        else:
            return [str(accounts)]
    except:
        return []

def get_auth_status(account_vip, today_time):
    """获取授权状态"""
    if not account_vip:
        return "⚠️ 未授权", "无"
    elif account_vip <= today_time:
        return "❌ 已过期", account_vip
    else:
        return "✅ 已授权", account_vip

def getusercontent():
    dd_managecommand = middleware.bucketGet('dd_hsh', 'dd_managecommand') or '慧生活管理'
    dd_querycommand = middleware.bucketGet('dd_hsh', 'dd_querycommand') or '慧生活查询'
    dd_signcommand = middleware.bucketGet('dd_hsh', 'dd_signcommand') or '慧生活登录'

    hshVipmoney = Decimal(middleware.bucketGet('dd_hsh', 'hshVipmoney') or '1')
    hshcoin = int(middleware.bucketGet('dd_hsh', 'hshcoin') or '0')

    use_ma_pay = middleware.bucketGet('dd_hsh', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'

    return (dd_managecommand, dd_querycommand, dd_signcommand,
            hshVipmoney, hshcoin, use_ma_pay)

# ==================== 慧生活API相关函数 ====================

class HuiCampusAPI:
    """慧生活API客户端"""
    BASE_URL = "https://i.ilife798.com/api/v1"
    OCR_API = "https://ddddocr.linzixuan.work/classification"
    TIMEOUT = 10

    HEADERS_APP = {
        'User-Agent': 'Android_ilife798_3.1.4',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json; charset=UTF-8',
        'ApplicationType': '1,1',
        'VersionCode': '3.1.4'
    }

    HEADERS_LOGIN = {
        'User-Agent': 'Android_ilife798_3.1.4',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'Authorization': '',
        'ApplicationType': '1,3',
        'VersionCode': '3.1.4',
        'Content-Type': 'application/json; charset=UTF-8'
    }

    @staticmethod
    def generate_sign(ad_id, timestamp, token, uid):
        """生成接口签名"""
        token_suffix = token[-8:] if len(token) >= 8 else token
        uid_suffix = str(uid)[-8:] if len(str(uid)) >= 8 else str(uid)
        sign_str = f"{ad_id}{timestamp}{token_suffix}{uid_suffix}"
        return hashlib.md5(sign_str.encode('utf-8')).hexdigest()

    @staticmethod
    def get_captcha(random_seed):
        """获取图片验证码"""
        try:
            timestamp = int(time.time() * 1000)
            captcha_url = f"{HuiCampusAPI.BASE_URL}/captcha/?s={random_seed}&r={timestamp}"

            response = requests.get(captcha_url, timeout=HuiCampusAPI.TIMEOUT, verify=False)
            if response.status_code == 200:
                return response.content
        except:
            pass
        return None

    @staticmethod
    def recognize_captcha(image_bytes):
        """识别验证码"""
        try:
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            payload = {"image": image_base64}

            response = requests.post(HuiCampusAPI.OCR_API, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                return result.get('result')
        except:
            pass
        return None

    @staticmethod
    def send_sms_code(phone, captcha_code, random_seed):
        """发送短信验证码"""
        try:
            url = f"{HuiCampusAPI.BASE_URL}/acc/login/code"
            headers = HuiCampusAPI.HEADERS_LOGIN.copy()

            payload = {
                "authCode": captcha_code,
                "s": random_seed,
                "un": phone
            }

            response = requests.post(url, json=payload, headers=headers, timeout=HuiCampusAPI.TIMEOUT, verify=False)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    return True, "发送成功"
                else:
                    return False, result.get('msg', '未知错误')
        except Exception as e:
            return False, str(e)
        return False, "请求失败"

    @staticmethod
    def login_with_sms(phone, sms_code):
        """使用短信验证码登录"""
        try:
            url = f"{HuiCampusAPI.BASE_URL}/acc/login"
            headers = HuiCampusAPI.HEADERS_LOGIN.copy()

            payload = {
                "authCode": sms_code,
                "un": phone
            }

            response = requests.post(url, json=payload, headers=headers, timeout=HuiCampusAPI.TIMEOUT, verify=False)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    data = result.get('data', {})
                    al = data.get('al', {})
                    token = al.get('token')
                    uid = al.get('uid')
                    return True, token, uid
                else:
                    return False, None, result.get('msg', '未知错误')
        except Exception as e:
            return False, None, str(e)
        return False, None, "请求失败"

    @staticmethod
    def get_uid_from_token(token):
        """从token获取UID"""
        try:
            headers = HuiCampusAPI.HEADERS_APP.copy()
            headers['Authorization'] = token
            url = f"{HuiCampusAPI.BASE_URL}/ui/app/master"
            response = requests.get(url, headers=headers, timeout=HuiCampusAPI.TIMEOUT, verify=False)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    uid = result.get('data', {}).get('account', {}).get('id')
                    return uid
        except:
            pass
        return None

    @staticmethod
    def get_score_info(token):
        """获取积分信息 - 从积分明细统计"""
        try:
            headers = HuiCampusAPI.HEADERS_APP.copy()
            headers['Authorization'] = token

            # 从score-lst统计积分
            url = f"{HuiCampusAPI.BASE_URL}/acc/score/score-lst?page=0&size=100&hasCount=true"
            response = requests.get(url, headers=headers, timeout=HuiCampusAPI.TIMEOUT, verify=False)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    data = result.get('data', [])
                    total_score = 0
                    for item in data:
                        score = int(item.get('data', {}).get('score', 0))
                        total_score += score

                    return {
                        'current': total_score,
                        'total': total_score,
                        'valid': total_score
                    }
                elif result.get('code') == -99:
                    return {'error': 'token_expired'}
        except:
            pass
        return None

    @staticmethod
    def get_today_score(token):
        """获取今日积分"""
        try:
            headers = HuiCampusAPI.HEADERS_APP.copy()
            headers['Authorization'] = token
            url = f"{HuiCampusAPI.BASE_URL}/acc/score/score-lst?page=0&size=20&hasCount=true"
            response = requests.get(url, headers=headers, timeout=HuiCampusAPI.TIMEOUT, verify=False)

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    today = datetime.now().date()
                    today_score = 0
                    data = result.get('data', [])
                    for item in data:
                        ctime = item.get('ctime', 0)
                        item_date = datetime.fromtimestamp(ctime / 1000).date()
                        if item_date == today:
                            score = int(item.get('data', {}).get('score', 0))
                            today_score += score
                    return today_score
        except:
            pass
        return 0

    @staticmethod
    def check_token_valid(token):
        """检查token是否有效"""
        score_info = HuiCampusAPI.get_score_info(token)
        if score_info and 'error' not in score_info:
            return True
        return False

def query_account_info(token):
    """查询账号信息"""
    uid = HuiCampusAPI.get_uid_from_token(token)
    if not uid:
        return None

    # 转换uid为字符串
    uid = str(uid)

    score_info = HuiCampusAPI.get_score_info(token)
    if not score_info or 'error' in score_info:
        return None

    today_score = HuiCampusAPI.get_today_score(token)

    return {
        'uid': uid,
        'current_score': score_info.get('current', 0),
        'total_score': score_info.get('total', 0),
        'valid_score': score_info.get('valid', 0),
        'today_score': today_score
    }

# ==================== 每日任务执行 ====================

class TaskRunner:
    """每日任务执行器（整合自慧生活脚本）"""

    HEADERS_ALIPAY = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; RMX3031 Build/RP1A.200720.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/105.0.5195.148 Mobile Safari/537.36 AlipayClient/10.7.20.8000',
        'Accept-Encoding': 'gzip',
        'Content-Type': 'application/json',
        'Accept-Charset': 'UTF-8',
        'Referer': 'https://2019061465519660.hybrid.alipay-eco.com/2019061465519660/0.2.2512111152.32/index.html#pages/index/index',
        'VersionCode': '2.0.83',
        'ApplicationType': '1,5',
        'AliPayMiniMark': 'Q81flLfEY0rWCRguKpNqTklzQ6hJhmSZc/BjrOPYttlrrnCAqKrSHasEp9XH4DFU+KxP+j8xj2EAwU7YDKG5Bj9VWvxxV3XRN95AL7hIPwk='
    }

    def __init__(self, token, uid=None):
        self.token = token
        self.uid = uid or str(HuiCampusAPI.get_uid_from_token(token) or '')
        self.login_expired = not bool(self.uid)

    def _api_request(self, method, endpoint, headers, data=None, retry_on_frequent=True):
        """统一请求方法，带频繁请求重试"""
        try:
            url = f"{HuiCampusAPI.BASE_URL}{endpoint}"
            if method == 'GET':
                resp = requests.get(url, headers=headers, timeout=HuiCampusAPI.TIMEOUT, verify=False)
            else:
                resp = requests.post(url, json=data, headers=headers, timeout=HuiCampusAPI.TIMEOUT, verify=False)

            if resp.status_code == 200:
                try:
                    resp_data = resp.json()
                    if retry_on_frequent and resp_data.get('code') == -98:
                        time.sleep(5)
                        return self._api_request(method, endpoint, headers, data, retry_on_frequent=False)
                    elif resp_data.get('code') == -99:
                        self.login_expired = True
                        return None
                    return resp_data
                except:
                    return None
            return None
        except:
            return None

    def _get_app_headers(self):
        headers = HuiCampusAPI.HEADERS_APP.copy()
        headers['Authorization'] = self.token
        return headers

    def check_valid(self):
        """验证账号状态"""
        result = self._api_request('GET', '/acc/score/mission-lst', self._get_app_headers())
        if not result or result.get('code') == -99:
            self.login_expired = True
            return False
        return True

    def daily_check_in(self):
        """每日签到"""
        current_weekday = datetime.now().weekday() + 1
        timestamp = int(time.time() / 10) * 10
        ad_id = "DAILY_CHECK_IN"
        payload = {"adId": ad_id, "addScore": 5, "addScoreType": 1, "weekday": current_weekday}
        sign = HuiCampusAPI.generate_sign(ad_id, timestamp, self.token, self.uid)
        result = self._api_request('POST', f'/acc/score/score-send?sign={sign}', self._get_app_headers(), payload)
        return bool(result and result.get('code') == 0)

    def watch_ad(self, max_count=5):
        """观看广告"""
        success = 0
        ad_id = "popsreen"
        for i in range(max_count):
            timestamp = int(time.time() / 10) * 10
            payload = {"adId": ad_id, "addScore": 10, "addScoreType": 4, "type": 101}
            sign = HuiCampusAPI.generate_sign(ad_id, timestamp, self.token, self.uid)
            result = self._api_request('POST', f'/acc/score/score-send?sign={sign}', self._get_app_headers(), payload)
            if result and result.get('code') == 0:
                success += 1
            if i < max_count - 1:
                time.sleep(5)
        return success

    def watch_videos(self, max_count=5):
        """观看视频"""
        success = 0
        ad_id = "1705776998"
        for i in range(max_count):
            timestamp = int(time.time() / 10) * 10
            payload = {"adId": ad_id, "addScore": 30, "addScoreType": 2, "type": 101}
            sign = HuiCampusAPI.generate_sign(ad_id, timestamp, self.token, self.uid)
            result = self._api_request('POST', f'/acc/score/score-send?sign={sign}', self._get_app_headers(), payload)
            if result and result.get('code') == 0:
                success += 1
            if i < max_count - 1:
                time.sleep(5)
        return success

    def watch_videos_alipay(self, max_count=5):
        """观看支付宝小程序视频"""
        success = 0
        ad_id = "ad_tiny_2019061465519660_202402222200083035"
        headers = self.HEADERS_ALIPAY.copy()
        headers['Authorization'] = self.token
        for i in range(max_count):
            timestamp = int(time.time() / 10) * 10
            payload = {"adId": ad_id, "type": 101}
            sign = HuiCampusAPI.generate_sign(ad_id, timestamp, self.token, self.uid)
            result = self._api_request('POST', f'/acc/score/score-send?sign={sign}', headers, payload)
            if result and result.get('code') == 0:
                success += 1
            if i < max_count - 1:
                time.sleep(5)
        return success

    def run_daily_tasks(self):
        """执行全部每日任务，返回结果摘要"""
        checkin_ok = self.daily_check_in()
        time.sleep(5)
        ad_count = self.watch_ad(5)
        time.sleep(5)
        video_count = self.watch_videos(5)
        time.sleep(5)
        alipay_count = self.watch_videos_alipay(5)

        today_score = HuiCampusAPI.get_today_score(self.token)

        return {
            'checkin': checkin_ok,
            'ad': ad_count,
            'video': video_count,
            'alipay_video': alipay_count,
            'today_score': today_score
        }

# ==================== 支付相关函数 ====================

def get_ma_pay_config():
    """从卡密系统获取码支付配置"""
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
        return None
    return ma_pay_config

def create_payment_order(amount, pay_type='wxpay'):
    """创建支付订单（码支付）"""
    try:
        if not use_ma_pay:
            sender.reply(format_message("支付未开启", "管理员未开启支付功能", "error"))
            return None

        ma_pay_config = get_ma_pay_config()
        if not ma_pay_config:
            sender.reply(format_message("配置错误", "未配置码支付系统，请在卡密系统中配置码支付", "error"))
            return None

        out_trade_no = f"HSH{int(time.time())}{userid}"

        # 构造支付参数
        params = {
            'pid': ma_pay_config['pid'],
            'type': ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'wxpay',
            'out_trade_no': out_trade_no,
            'name': f"{senderID}-慧生活授权-{str(amount)}",
            'money': str(amount),
            'notify_url': ma_pay_config['notify_url'],
            'return_url': ma_pay_config['return_url'],
            'param': userid
        }

        # 移除空值参数（签名时不能包含空值）
        params = {k: v for k, v in params.items() if v}

        # 按照ASCII码排序参数
        sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))

        # 拼接成key=value&key=value格式并MD5签名
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode('utf-8')).hexdigest().lower()

        params['sign'] = sign
        params['sign_type'] = 'MD5'

        # 构建mapi接口URL
        gateway = ma_pay_config['gateway']
        if gateway.endswith('/'):
            gateway = gateway[:-1]
        mapi_url = f"{gateway}/mapi.php"

        # 发送POST请求到mapi接口
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(mapi_url, data=params, headers=headers, timeout=10)

        if response.status_code != 200:
            sender.reply(format_message("支付失败", f"创建支付订单失败，HTTP状态码: {response.status_code}", "error"))
            return None

        try:
            result = response.json()
        except:
            sender.reply(format_message("支付失败", "创建支付订单失败，返回数据格式错误", "error"))
            return None

        code = result.get('code', 0)
        msg = result.get('msg', '未知状态')

        if code == 1:
            payurl = result.get('payurl', '')
            if not payurl:
                sender.reply(format_message("支付失败", "未获取到支付链接", "error"))
                return None

            return {
                'order_id': out_trade_no,
                'payurl': payurl,
                'pay_type': ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay',
                'gateway': gateway,
                'ma_pay_config': ma_pay_config
            }
        else:
            if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                sender.reply(format_message("支付失败", f"码支付暂不可用({msg})", "error"))
            else:
                sender.reply(format_message("支付失败", f"创建订单失败: {msg}", "error"))
            return None

    except Exception as e:
        sender.reply(format_message("创建订单失败", f"错误信息: {str(e)}", "error"))
        return None

def check_payment_status(order_id, gateway, ma_pay_config, timeout=300):
    """轮询检查支付状态"""
    try:
        check_url = gateway
        if check_url.endswith('/'):
            check_url = check_url[:-1]

        # 根据码支付文档，查询接口路径
        if '/xpay/epay/api.php' not in check_url:
            check_url = f"{check_url}/xpay/epay/api.php"

        for i in range(60):  # 最多等待5分钟（每5秒一次）
            check_params = {
                'act': 'order',
                'pid': ma_pay_config['pid'],
                'key': ma_pay_config['key'],
                'out_trade_no': order_id
            }

            try:
                check_resp = requests.get(check_url, params=check_params, timeout=10)
                check_result = check_resp.json()

                if check_result.get('code') == 1 and check_result.get('status') == 1:
                    return True
            except Exception as e:
                print(f"查询订单状态出错: {str(e)}")

            # 等待用户输入或超时（5秒）
            result = sender.listen(5000)
            if result == 'q' or result == 'Q':
                sender.reply("✅ 已取消支付")
                exit(0)

        return False
    except:
        return False

def calc_expire_date(uid, days=30):
    """计算到期时间，已授权未过期则在原到期时间上续期"""
    current_vip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid) or ''
    if current_vip and current_vip > today_time:
        base_date = datetime.strptime(current_vip, "%Y-%m-%d")
        return (base_date + timedelta(days=days)).strftime("%Y-%m-%d")
    else:
        return (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

# ==================== 主要功能函数 ====================

def handle_login():
    """处理登录"""
    welcome_msg = """
=====慧生活798登录=====
[1] 验证码登录（推荐）
[2] Token登录
-------------------
回复数字选择方式
回复"q"退出操作
=================="""

    sender.reply(welcome_msg)
    input_choice = sender.input(120000, 1, False)

    if input_choice == '1':
        handle_captcha_login()
    elif input_choice == '2':
        handle_token_login()
    elif input_choice == 'q' or input_choice == 'Q':
        sender.reply("✅ 已取消登录")
        return
    elif input_choice is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    else:
        sender.reply("❌ 输入错误,请重新选择登录方式")
        return

def handle_captcha_login():
    """处理验证码登录"""
    sender.reply("📱 请输入手机号:")
    phone = get_user_choice("请输入手机号", allow_quit=True)

    if not phone or len(phone) != 11:
        sender.reply("❌ 请输入11位手机号")
        return

    random_seed = random.random()
    image_bytes = HuiCampusAPI.get_captcha(random_seed)
    if not image_bytes:
        sender.reply("❌ 无法获取图片验证码")
        return

    captcha_text = HuiCampusAPI.recognize_captcha(image_bytes)
    success, msg = HuiCampusAPI.send_sms_code(phone, captcha_text, random_seed)

    if not success:
        sender.reply(f"❌ 发送失败: {msg}")
        return

    sender.reply("✅ 短信验证码已发送，请输入:")
    sms_code = get_user_choice("请输入短信验证码", allow_quit=True)

    if not sms_code:
        sender.reply("❌ 短信验证码不能为空")
        return

    success, token, uid = HuiCampusAPI.login_with_sms(phone, sms_code)

    if not success:
        sender.reply(f"❌ 登录失败: {uid}")
        return

    if not token or not uid:
        sender.reply("❌ 无法获取登录信息")
        return

    uid = str(uid)
    user_accounts = parse_accounts(uservalue)

    # 保存手机号
    middleware.bucketSet(bucket='dd_hsh_phone', key=uid, value=phone)

    # 如果账号已存在，更新Token
    if uid in user_accounts:
        middleware.bucketSet(bucket='dd_hsh_token', key=uid, value=token)

        account_info = query_account_info(token)
        accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid)
        auth_status = '✅ 已授权' if accountVip and accountVip >= today_time else '⚠️ 未授权'

        masked_phone = mask_phone(phone)

        if account_info:
            sender.reply(f"""
=====慧生活账号更新=====
📱 手机号: {masked_phone}
💎 当前积分: {account_info['current_score']}
🎯 今日积分: {account_info['today_score']}
🔐 授权: {auth_status}
✅ Token已更新
💡 发送 {dd_managecommand} 管理账号
==================""")
        else:
            sender.reply(f"""
=====慧生活账号更新=====
📱 手机号: {masked_phone}
🔐 授权: {auth_status}
✅ Token已更新
💡 发送 {dd_managecommand} 管理账号
==================""")
        return

    user_accounts.append(uid)
    middleware.bucketSet(bucket='dd_hsh_user', key=userid, value=str(user_accounts))
    middleware.bucketSet(bucket='dd_hsh_token', key=uid, value=token)

    account_info = query_account_info(token)

    accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid)
    auth_status = '✅ 已授权' if accountVip and accountVip >= today_time else '⚠️ 未授权'

    masked_phone = mask_phone(phone)

    if account_info:
        sender.reply(f"""
=====慧生活账号绑定=====
📱 手机号: {masked_phone}
💎 当前积分: {account_info['current_score']}
🎯 今日积分: {account_info['today_score']}
🔐 授权: {auth_status}
💡 发送 {dd_managecommand} 管理账号
==================""")
    else:
        sender.reply(f"""
=====慧生活账号绑定=====
📱 手机号: {masked_phone}
🔐 授权: {auth_status}
✅ Token已保存
💡 发送 {dd_managecommand} 管理账号
==================""")

def handle_token_login():
    """处理Token登录"""
    sender.reply("🔑 请输入慧生活Token:")
    token = get_user_choice("请输入Token", allow_quit=True)

    if not token or len(token) < 10:
        sender.reply("❌ 请输入有效的Token")
        return

    if not HuiCampusAPI.check_token_valid(token):
        sender.reply("❌ Token无效或已过期")
        return

    account_info = query_account_info(token)
    if not account_info:
        sender.reply("❌ 无法获取账号信息")
        return

    uid = account_info['uid']
    user_accounts = parse_accounts(uservalue)

    # Token登录无法获取手机号，使用UID作为标识
    # 尝试从已保存的手机号中获取
    saved_phone = middleware.bucketGet(bucket='dd_hsh_phone', key=uid)
    display_phone = mask_phone(saved_phone) if saved_phone else f"UID:{uid[:8]}..."

    # 如果账号已存在，更新Token
    if uid in user_accounts:
        middleware.bucketSet(bucket='dd_hsh_token', key=uid, value=token)

        accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid)
        auth_status = '✅ 已授权' if accountVip and accountVip >= today_time else '⚠️ 未授权'

        sender.reply(f"""
=====慧生活账号更新=====
📱 账号: {display_phone}
💎 当前积分: {account_info['current_score']}
🎯 今日积分: {account_info['today_score']}
🔐 授权: {auth_status}
✅ Token已更新
💡 发送 {dd_managecommand} 管理账号
==================""")
        return

    user_accounts.append(uid)
    middleware.bucketSet(bucket='dd_hsh_user', key=userid, value=str(user_accounts))
    middleware.bucketSet(bucket='dd_hsh_token', key=uid, value=token)

    accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid)
    auth_status = '✅ 已授权' if accountVip and accountVip >= today_time else '⚠️ 未授权'

    sender.reply(f"""
=====慧生活账号绑定=====
📱 账号: {display_phone}
💎 当前积分: {account_info['current_score']}
🎯 今日积分: {account_info['today_score']}
🔐 授权: {auth_status}
💡 发送 {dd_managecommand} 管理账号
==================""")

def handle_query():
    """处理查询"""
    user_accounts = parse_accounts(uservalue)

    if not user_accounts:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {dd_signcommand} 绑定
==================""")
        return

    today_time = datetime.now().strftime("%Y-%m-%d")

    for idx, uid in enumerate(user_accounts, 1):
        token = middleware.bucketGet(bucket='dd_hsh_token', key=uid)
        phone = middleware.bucketGet(bucket='dd_hsh_phone', key=uid)
        display_phone = mask_phone(phone) if phone else f"UID:{uid[:8]}..."

        if not token:
            sender.reply(f"""
=====账号 {idx}=====
📱 手机号: {display_phone}
❌ Token丢失
==================""")
            continue

        account_vip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid)
        auth_status, auth_time = get_auth_status(account_vip, today_time)

        account_info = query_account_info(token)
        if not account_info:
            sender.reply(f"""
=====账号 {idx}=====
📱 手机号: {display_phone}
🔐 授权: {auth_status}
❌ 账号异常
==================""")
            continue

        account_status = "✅ 正常" if HuiCampusAPI.check_token_valid(token) else "❌ 异常"

        sender.reply(f"""
=====账号 {idx}=====
📱 手机号: {display_phone}
🎯 今日积分: {account_info['today_score']}
📊 总积分: {account_info['total_score']}
📈 账号状态: {account_status}
📅 到期时间: {auth_time}
==================""")

def handle_manage():
    """处理管理"""
    user_accounts = parse_accounts(uservalue)

    if not user_accounts:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {dd_signcommand} 绑定
==================""")
        return

    account_list = "=====我的慧生活账号====="

    for i, uid in enumerate(user_accounts, 1):
        accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid)
        auth_status, auth_time = get_auth_status(accountVip, today_time)

        phone = middleware.bucketGet(bucket='dd_hsh_phone', key=uid)
        display_phone = mask_phone(phone) if phone else f"UID:{uid[:8]}..."

        account_list += f"""
[{i}] 账号信息
📱 手机号: {display_phone}
🔐 授权: {auth_status}"""
        if i < len(user_accounts):
            account_list += "\n------------------"

    account_list += "\n==================\n回复数字选择账号\n回复'q'退出操作"

    sender.reply(account_list)

    inputmessage = get_user_choice("", 120000, True)

    try:
        me_as_int = int(inputmessage)
        if me_as_int < 1 or me_as_int > len(user_accounts):
            sender.reply("❌ 输入的序号无效")
            return
    except ValueError:
        sender.reply("❌ 输入必须是数字")
        return

    uid = user_accounts[me_as_int - 1]
    token = middleware.bucketGet(bucket='dd_hsh_token', key=uid)
    accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=uid)

    auth_status, auth_time = get_auth_status(accountVip, today_time)

    phone = middleware.bucketGet(bucket='dd_hsh_phone', key=uid)
    display_phone = mask_phone(phone) if phone else f"UID:{uid[:8]}..."

    account_info = f"""
=====账号详情=====
📱 手机号: {display_phone}
🔐 授权: {auth_status}
==================
[1] 授权账号
[2] 删除账号
[3] 返回
=================="""

    sender.reply(account_info)
    choice = get_user_choice("", 120000, True)

    if choice == '1':
        handle_authorize_single(uid)
    elif choice == '2':
        handle_delete_single(uid, user_accounts)
    elif choice == '3':
        sender.reply("✅ 已返回")
    else:
        sender.reply("❌ 输入错误")

def handle_authorize_single(uid):
    """授权单个账号"""
    phone = middleware.bucketGet(bucket='dd_hsh_phone', key=uid)
    display_phone = mask_phone(phone) if phone else f"UID:{uid[:8]}..."

    token = middleware.bucketGet(bucket='dd_hsh_token', key=uid)

    # 价格为0，直接免费授权
    if hshVipmoney <= 0 and hshcoin <= 0:
        expire_date = calc_expire_date(uid)
        middleware.bucketSet(bucket='dd_hsh_vip', key=uid, value=expire_date)

        sender.reply(f"""
=====授权成功=====
📱 手机号: {display_phone}
💰 支付方式: 免费授权
📅 到期时间: {expire_date}
==================""")
        return

    payment_msg = "💰 选择支付方式:\n"
    payment_options = []

    if hshVipmoney > 0:
        payment_msg += f"[1] 现金支付 ({hshVipmoney}元/月)\n"
        payment_options.append('cash')

    if hshcoin > 0:
        user_coin = middleware.bucketGet(bucket='dd_sign_points', key=userid) or 0
        payment_msg += f"[2] 积分支付 ({hshcoin}积分/月)\n   当前积分: {user_coin}\n"
        payment_options.append('coin')

    if not payment_options:
        sender.reply("❌ 管理员未开启任何支付方式")
        return

    payment_msg += "\n回复数字选择支付方式"
    sender.reply(payment_msg)

    pay_choice = get_user_choice("", 120000, True)
    try:
        pay_index = int(pay_choice)
        if pay_index < 1 or pay_index > len(payment_options):
            sender.reply("❌ 输入无效")
            return
    except ValueError:
        sender.reply("❌ 输入必须是数字")
        return

    pay_method = payment_options[pay_index - 1]

    if pay_method == 'coin':
        user_coin = int(middleware.bucketGet(bucket='dd_sign_points', key=userid) or 0)
        if user_coin < hshcoin:
            sender.reply(f"❌ 积分不足\n需要 {hshcoin} 积分，当前只有 {user_coin} 积分")
            return

        middleware.bucketSet(bucket='dd_sign_points', key=userid, value=str(user_coin - hshcoin))
        expire_date = calc_expire_date(uid)
        middleware.bucketSet(bucket='dd_hsh_vip', key=uid, value=expire_date)

        sender.reply(f"""
=====授权成功=====
📱 手机号: {display_phone}
💰 支付方式: 积分支付
💎 消耗积分: {hshcoin}
💎 剩余积分: {user_coin - hshcoin}
📅 到期时间: {expire_date}
==================""")

    elif pay_method == 'cash':
        order = create_payment_order(hshVipmoney)
        if not order:
            return

        # 生成并发送二维码
        qrcode_url = generate_qrcode(order['payurl'])
        pay_type = order['pay_type']

        if qrcode_url:
            send_qrcode_image(sender, qrcode_url, pay_type)
        else:
            sender.reply(f"""=====码支付=====
💰 金额: {hshVipmoney}元
⏰ 有效期: 5分钟
------------------
二维码生成失败，请点击链接完成支付:
{order['payurl']}
==================""")

        # 轮询订单状态
        if check_payment_status(order['order_id'], order['gateway'], order['ma_pay_config'], timeout=300):
            expire_date = calc_expire_date(uid)
            middleware.bucketSet(bucket='dd_hsh_vip', key=uid, value=expire_date)

            sender.reply(f"""
=====支付成功=====
📱 手机号: {display_phone}
💰 支付金额: {hshVipmoney}元
📅 到期时间: {expire_date}
==================""")
        else:
            sender.reply("❌ 支付超时,请重新发起支付!")

def handle_delete_single(uid, user_accounts):
    """删除单个账号"""
    phone = middleware.bucketGet(bucket='dd_hsh_phone', key=uid)
    display_phone = mask_phone(phone) if phone else f"UID:{uid[:8]}..."

    sender.reply(f"确认删除账号 {display_phone} 吗？\n[y] 确认删除\n[n] 取消")
    confirm = get_user_choice("", 120000, False)

    if confirm and confirm.lower() == 'y':
        user_accounts.remove(uid)
        middleware.bucketSet(bucket='dd_hsh_user', key=userid, value=str(user_accounts))
        middleware.bucketDel(bucket='dd_hsh_token', key=uid)
        middleware.bucketDel(bucket='dd_hsh_vip', key=uid)
        middleware.bucketDel(bucket='dd_hsh_phone', key=uid)
        sender.reply(f"✅ 账号 {display_phone} 已删除")
    else:
        sender.reply("✅ 已取消删除")

def handle_backend():
    """后台管理"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return

    backend_menu = """=====慧生活后台管理=====
[1] 清理过期账号
[2] 手动执行每日任务
-------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(backend_menu)
    xz = sender.input(60000, 1, False)

    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出后台管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '1':
        clean_expired_accounts()
    elif xz == '2':
        run_all_daily_tasks()
    else:
        sender.reply("❌ 输入错误,请重新选择")

def clean_expired_accounts():
    """清理过期账号"""
    users = middleware.bucketAllKeys(bucket='dd_hsh_user')

    if not users:
        sender.reply("❌ 未找到任何绑定账号")
        return

    sender.reply(f"⏳ 共找到 {len(users)} 个用户，清理中...")

    cleaned_count = 0
    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_hsh_user', key=user)
            if not accountlist:
                continue

            accounts = parse_accounts(accountlist)
            valid_accounts = []

            for account in accounts:
                accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=account)

                if not accountVip or accountVip <= today_time:
                    middleware.bucketDel(bucket='dd_hsh_token', key=account)
                    middleware.bucketDel(bucket='dd_hsh_vip', key=account)
                    cleaned_count += 1
                else:
                    valid_accounts.append(account)

            valid_accounts = list(dict.fromkeys(valid_accounts))

            if valid_accounts:
                middleware.bucketSet(bucket='dd_hsh_user', key=user, value=str(valid_accounts))
            else:
                middleware.bucketDel(bucket='dd_hsh_user', key=user)

        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue

    sender.reply(f"✅ 清理完成，已清理 {cleaned_count} 个账号")

def run_all_daily_tasks():
    """遍历所有已授权账号执行每日任务"""
    users = middleware.bucketAllKeys(bucket='dd_hsh_user')

    if not users:
        return

    total_count = 0
    success_count = 0
    expired_count = 0

    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_hsh_user', key=user)
            if not accountlist:
                continue

            accounts = parse_accounts(accountlist)

            for account in accounts:
                accountVip = middleware.bucketGet(bucket='dd_hsh_vip', key=account)
                token = middleware.bucketGet(bucket='dd_hsh_token', key=account)

                if not token:
                    continue

                # Token失效检测
                if not HuiCampusAPI.check_token_valid(token):
                    push(user=user, account=account, c="""
⚠️ 慧生活账号状态异常
------------------
❌ Token已失效
💡 请尽快重新登录""")
                    continue

                # 授权过期检测
                if not accountVip or accountVip <= today_time:
                    expired_count += 1
                    push(user=user, account=account, c="""
⚠️ 慧生活授权已过期
------------------
❌ 授权状态失效
💡 请及时续费授权""")
                    continue

                # 已授权且Token有效，执行每日任务
                total_count += 1
                try:
                    runner = TaskRunner(token, str(account))
                    if runner.login_expired:
                        push(user=user, account=account, c="""
⚠️ 慧生活账号状态异常
------------------
❌ Token已失效
💡 请尽快重新登录""")
                        continue

                    result = runner.run_daily_tasks()
                    success_count += 1

                    phone = middleware.bucketGet(bucket='dd_hsh_phone', key=account)
                    display_phone = mask_phone(phone) if phone else f"UID:{str(account)[:8]}..."

                    push(user=user, account=account, c=f"""
✅ 每日任务执行完成
------------------
📋 签到: {'✅' if result['checkin'] else '❌'}
📺 广告: {result['ad']}/5
🎬 视频: {result['video']}/5
💳 支付宝视频: {result['alipay_video']}/5
🎯 今日积分: +{result['today_score']}""")

                except Exception as e:
                    push(user=user, account=account, c=f"""
❌ 每日任务执行失败
------------------
错误: {str(e)}""")

                # 账号间间隔，避免请求过于频繁
                time.sleep(15)

        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue

    return success_count, total_count, expired_count

def handle_tutorial():
    """显示教程"""
    tutorial = """📚 慧生活798教程

🔰 基础功能指令:
1️⃣ 慧生活登录 - 绑定账号(验证码/Token登录)
2️⃣ 慧生活查询 - 查看账号积分信息
3️⃣ 慧生活管理 - 管理已绑定账号

🔧 管理员功能:
• 慧生活后台 - 后台管理

💡 登录说明:
• 验证码登录
• Token登录

⚠️ 注意事项:
1. 首次使用请先登录绑定
2. 定期查看账号状态
3. 及时处理授权到期"""
    sender.reply(tutorial)

def push(user, account, c):
    """推送消息到各个平台"""
    phone = middleware.bucketGet(bucket='dd_hsh_phone', key=account)
    display_phone = mask_phone(phone) if phone else f"UID:{account[:8]}..."

    push_msg = f"""
=====慧生活账号通知=====
📱 账号: {display_phone}
📢 消息: {c}
=================="""

    platforms = ['wb', 'tg', 'qq', 'qb', 'wx']
    for platform in platforms:
        middleware.push(platform, '', user, '', push_msg)

# ==================== 主程序入口 ====================

(dd_managecommand, dd_querycommand, dd_signcommand,
 hshVipmoney, hshcoin, use_ma_pay) = getusercontent()

today_date = datetime.now().date()
today_time = str(today_date)
usermessage = sender.getMessage()

if '登录' in usermessage or '登陆' in usermessage:
    handle_login()
elif '管理' in usermessage:
    if len(uservalue) != 0:
        handle_manage()
    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {dd_signcommand} 绑定
==================""")
elif '查询' in usermessage:
    if len(uservalue) != 0:
        handle_query()
    else:
        sender.reply(f"""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 {dd_signcommand} 绑定
==================""")
elif usermessage == '慧生活后台':
    handle_backend()
elif usermessage == '慧生活教程':
    handle_tutorial()
elif sender.getImtype() == 'fake':
    # 定时任务（凌晨1点）：执行所有已授权账号的每日任务
    run_all_daily_tasks()
else:
    sender.setContinue()
