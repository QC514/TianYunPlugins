#[title: 众安健康]
#[language: python]
#[class: 工具类]
#[service: 203066880] 售后联系
#[author: rujingxianghai] 作者
#[disable: false]
#[admin: false]
#[rule: ^(众安|众安管理)(登录|登陆)$|^登(录|陆)(众安管理)$|^(众安|众安管理)(查询|管理)$|^(查询|管理)(众安管理)$|^众安授权$|^众安教程$|^众安一键运行$|^众安总结$|^众安检测$]
#[cron: 56 6,9,13,16,19,20 * * *]
#[priority: 0]
#[platform: qq,wx]
#[open_source: false]
#[icon: http://113.45.39.135:8080/admin/images/gallery/1748901594846584338.png]
#[version: 3.0]
#[public: true]
#[price: 5.88]
#[description: 【白名单插件】购买请前往订阅：huawei<br>vx小程序【众安健康】插件自带任务<br>适配呆呆积分支付<br><br>指令：<br>众安登录：绑定账号<br>众安管理：账号管理与授权<br>众安查询：查询积分与状态<br>众安授权：管理员授权操作<br>众安教程：使用指南<br>众安一键运行：执行任务(仅管理员)<br>众安总结：统计提现总额<br>众安检测：检测过期并清理<br><br>更新日志：<br>1.0：初版<br>1.3：新增完成订阅任务<br>1.4：新增满5元自动提现<br>1.5：新增IP代理支持<br>1.6：新增过期提醒和清理功能<br>1.8：新增众安总结<br>1.9：新增码支付功能<br>2.0：新增智能余额提醒<br>2.2：新增众安检测指令<br>3.0：重构支付模块使用vorto_utils统一支付，移除插件级支付配置，简化积分系统]

import json
import time
import hashlib
import urllib.parse
import random
import requests
from datetime import datetime, timedelta
import middleware
import vorto_utils

# ========== Init ==========
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_zajk_user', key=userid)

# [param: {"required":true,"key":"s_zajk.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_zajk.coin","bool":false,"placeholder":"100","name":"积分开通","desc":"授权一月需要多少积分，不填为关闭"}]
# [param: {"required":false,"key":"s_zajk.proxy_url","bool":false,"placeholder":"http://example.com/api/getip","name":"IP代理地址","desc":"填写获取代理IP的接口地址，不填则不使用代理"}]
# [param: {"required":false,"key":"s_zajk.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道，多个用逗号分隔"}]
# [param: {"required":false,"key":"s_zajk.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]
# [param: {"required":false,"key":"s_zajk.notify_limit","bool":false,"placeholder":"3","name":"推送次数上限","desc":"达到上限后自动清理过期账号"}]

PLUGIN_CONFIG = {'bucket': 's_zajk', 'coin_key': 'dd_sign_points', 'name': '众安健康'}


# ========== Helper ==========
def _get_user_accounts(user_id=None):
    """Get user account list, handles both JSON and eval formats"""
    if user_id is None:
        user_id = userid
    raw = middleware.bucketGet('s_zajk_user', user_id) or '[]'
    try:
        accounts = json.loads(raw)
        if isinstance(accounts, list):
            return [str(a) for a in accounts]
        return [str(accounts)]
    except:
        try:
            result = eval(raw)
            if isinstance(result, (list, tuple, set)):
                return [str(a) for a in result]
            return [str(result)] if result else []
        except:
            return []


def _get_auth_expire(account_id):
    """Get auth expire date string from s_zajk_auth (handles both JSON and plain date formats)"""
    raw = middleware.bucketGet('s_zajk_auth', account_id)
    if not raw:
        return None
    try:
        data = json.loads(raw)
        return data.get('expire_time', '')
    except:
        return raw


def _is_authorized(account_id):
    """Check if account is currently authorized"""
    expire = _get_auth_expire(account_id)
    if not expire:
        return False
    return expire > str(datetime.now().date())


# ========== Zhongan API Classes ==========
class ZhongAnHealthAuto:
    """Zhongan Health auto task client"""

    def __init__(self, access_token_with_remark):
        if '#' in access_token_with_remark:
            self.raw_token, self.remark = access_token_with_remark.split('#', 1)
        else:
            self.raw_token = access_token_with_remark
            self.remark = "默认账号"

        self.access_token = self.raw_token
        self.base_url = "https://ihealth.zhongan.com/api/lemon/v1"
        self.session = requests.Session()

        self.headers = {
            "Host": "ihealth.zhongan.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839",
            "Content-Type": "application/json",
            "Access-Token": self.access_token,
            "Referer": "https://servicewechat.com/wxbac45cc1588a5a75/409/page-frame.html",
            "xweb_xhr": "1",
            "scene": "fa339ec6a687#prd#support",
        }
        self.session.headers.update(self.headers)

        self.proxies = None
        proxy_url = middleware.bucketGet('s_zajk', 'proxy_url') or ''
        self.proxy_url = proxy_url
        self.is_proxy_enabled = bool(proxy_url)
        if self.is_proxy_enabled:
            self.update_proxy()

    def get_proxy(self):
        if not self.is_proxy_enabled:
            return None
        try:
            resp = requests.get(self.proxy_url, timeout=5)
            if resp.status_code != 200:
                return None
            proxy_text = resp.text.strip()
            if not proxy_text:
                return None
            return proxy_text if proxy_text.startswith('http') else f'http://{proxy_text}'
        except:
            return None

    def update_proxy(self):
        if not self.is_proxy_enabled:
            self.proxies = None
            return
        proxy = self.get_proxy()
        self.proxies = {'http': proxy, 'https': proxy} if proxy else None

    def _request_with_retry(self, method, url, **kwargs):
        """Request with proxy retry on failure"""
        kwargs.setdefault('timeout', 10)
        kwargs.setdefault('proxies', self.proxies)
        try:
            return getattr(self.session, method)(url, **kwargs)
        except Exception:
            if self.is_proxy_enabled:
                self.update_proxy()
                kwargs['proxies'] = self.proxies
                return getattr(self.session, method)(url, **kwargs)
            raise

    def get_status(self):
        url = f"{self.base_url}/common/activity/homePage"
        payload = {"channelCode": "c20195660470001", "activityCode": "ONA20220411001"}
        try:
            resp = self._request_with_retry('post', url, json=payload)
            data = resp.json()
            return data['result'] if data.get('code') == '0' else None
        except:
            return None

    def get_masked_phone(self):
        url = f"{self.base_url}/wechatApplet/obtainBaseInfo/c20195660470001"
        try:
            resp = self._request_with_retry('post', url, json={}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('code') == '0' and data.get('result'):
                    return data['result'].get('phone', '未知')
        except:
            pass
        return "未知"

    def _signIn(self):
        data = {
            "channelCode": "c20195660470001", "activityCode": "ONA20220411001",
            "infernalWallParams": {
                "did": "a5e6c0c248b5bfdf6b85c6c4cd791b1cb8695928:77:039945a3f6430a2dd0156cf37331d887fcc6bac3",
                "token": "2:极2:1748763904089:fa339ec6a687#prd#support::09Qb0qTs:1848:000db75acfb4e63dbfefbfd2ebccec4385a9f775:89",
                "s": "fa339ec6a687#prd#support", "scene": "fa339ec6a687#prd#support"
            }, "envSource": "miniprogram"
        }
        try:
            resp = self._request_with_retry('post', f"{self.base_url}/common/activity/signIn", json=data)
            return resp.json().get('code') == '0'
        except:
            return False

    def extract_product_info(self, data):
        result = []
        for pid, info in data.get("productRecommend", {}).items():
            if info.get("status") is False:
                link = info.get("link", "")
                if link:
                    parsed = urllib.parse.urlparse(link)
                    params = urllib.parse.parse_qs(parsed.query)
                    result.append({
                        "activityCode": params.get("activityCode", [""])[0],
                        "channelCode": params.get("healthChannelCode", [""])[0],
                        "goodsCode": pid,
                        "taskId": params.get("taskId", [""])[0]
                    })
        return result

    def _run_task(self, _list):
        count = 0
        for item in _list:
            try:
                self._request_with_retry('post', f"{self.base_url}/applet/mgm/activity/add/award", json=item)
                count += 1
            except:
                pass
        return count


class ZhongAnRewardClaimer:
    """Zhongan reward claimer with subscribe + claim + withdraw"""

    def __init__(self, access_token):
        self.device_hash = hashlib.md5(str(random.random()).encode()).hexdigest()
        token_parts = access_token.split('#', 1)
        self.access_token = token_parts[0].strip()
        self.base_url = "https://ihealth.zhongan.com"
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090819) XWEB/8501',
            'xweb_xhr': '1',
            'access-token': self.access_token,
            'content-type': 'application/json',
            'referer': 'https://servicewechat.com/wxbac45cc1588a5a75/417/page-frame.html'
        })
        self.scene_id = f"frdadbe{random.randint(10000, 99999)}"

        self.proxies = None
        self.is_proxy_enabled = False
        proxy_url = middleware.bucketGet('s_zajk', 'proxy_url') or ''
        if proxy_url:
            self.proxy_url = proxy_url
            self.is_proxy_enabled = True
            proxy = self._get_proxy()
            if proxy:
                self.proxies = {'http': proxy, 'https': proxy}

    def _get_proxy(self):
        try:
            resp = requests.get(self.proxy_url, timeout=5)
            if resp.status_code == 200:
                txt = resp.text.strip()
                return txt if txt.startswith('http') else f'http://{txt}'
        except:
            pass
        return None

    def _gen_did(self):
        t = int(time.time() * 1000)
        p1 = hashlib.sha1(f"{self.device_hash}{t}".encode()).hexdigest()[:40]
        p2 = hashlib.sha256(str(t).encode()).hexdigest()[:40]
        return f"{p1}:35:{p2}"

    def _gen_token(self, action_type=896):
        ts = int(time.time() * 1000)
        salt = hashlib.md5(str(ts).encode()).hexdigest()[:8]
        content = f"{action_type}_{ts}"
        chk = sum(ord(c) for c in salt) % 100
        return f"2:12:{ts}:{self.scene_id}::{salt}:{action_type}:{hashlib.sha256(content.encode()).hexdigest()}:{chk}"

    def _infernal_params(self):
        return {
            "did": self._gen_did(), "token": self._gen_token(896),
            "s": self.scene_id, "scene": self.scene_id
        }

    def get_reward_status(self):
        try:
            resp = self.session.post(
                f"{self.base_url}/api/lemon/v1/common/activity/homePage",
                json={"channelCode": "c20195660470001", "activityCode": "ONA20220411001"},
                timeout=10, proxies=self.proxies
            )
            if resp.status_code == 200 and resp.json().get('code') == '0':
                return resp.json().get('result', {})
        except:
            pass
        return None

    def claim_reward(self, award_detail_id):
        payload = {
            "channelCode": "c20195660470001", "activityCode": "ONA20220411001",
            "id": award_detail_id, "infernalWallParams": self._infernal_params(),
            "envSource": "miniprogram"
        }
        try:
            resp = self.session.post(f"{self.base_url}/api/lemon/v1/common/activity/lottery",
                                     json=payload, proxies=self.proxies)
            data = resp.json()
            if data.get('code') == '0':
                return data.get('result', {}).get('sumAward', 0)
        except:
            pass
        return None

    def get_task_list(self):
        try:
            resp = self.session.get(
                f"{self.base_url}/api/pocket/v1/mp/activity/config?code=sign2022&pageSize=20",
                proxies=self.proxies
            )
            data = resp.json()
            return data.get('result', {}) if data.get('code') == '0' else None
        except:
            return None

    def subscribe_message(self):
        tsklist = self.get_task_list()
        if not tsklist:
            return None
        tmp = tsklist.get('custom', {}).get('subscribe', [])
        if not tmp:
            return None
        payload = {
            "channelCode": "c20195660470001", "activityCode": "ONA20220411001",
            "extraInfo": '{"source":"auth"}', "templateNo": ','.join(tmp),
            "infernalWallParams": self._infernal_params(), "envSource": "miniprogram"
        }
        try:
            resp = self.session.post(
                f"{self.base_url}/api/lemon/v1/common/activity/subscribe/message",
                json=payload, proxies=self.proxies
            )
            return resp.json().get('code') == '0'
        except:
            return None

    def claim_all_rewards(self):
        status = self.get_reward_status()
        if not status:
            return {'success_count': 0, 'total_earned': 0, 'final_points': 0}

        available = []
        for rlist in [status.get('valuableRewardList', []), status.get('rewardList', []),
                      status.get('taskList', []), status.get('activityTasks', []),
                      status.get('unclaimedRewards', [])]:
            if not isinstance(rlist, list):
                continue
            for task in rlist:
                if task.get('received') or task.get('isReceived') or task.get('claimed') or task.get('isClaimed'):
                    continue
                aid = task.get('awardDetailId') or task.get('awardId') or task.get('id') or task.get('taskId')
                if aid:
                    available.append({'id': aid, 'desc': task.get('desc', '未知任务')})

        if not available:
            return {'success_count': 0, 'total_earned': 0, 'final_points': status.get('sumAward', 0)}

        total_earned = 0
        base = status.get('sumAward', 0)
        success = 0
        for rw in available:
            new_total = self.claim_reward(rw['id'])
            if new_total is not None:
                total_earned += new_total - base
                base = new_total
                success += 1
            try:
                self.session.get(f"{self.base_url}/api/health/check", timeout=1)
            except:
                pass

        return {'success_count': success, 'total_earned': total_earned, 'final_points': base}

    def get_balance(self):
        """Get current withdrawable balance"""
        try:
            resp = self.session.post(
                f"{self.base_url}/api/lemon/v1/common/activity/awardList",
                json={"channelCode": "c20195660470001", "activityCode": "ONA20220411001"},
                timeout=10
            )
            data = resp.json()
            if data.get('code') == '0' and 'result' in data and 'detailList' in data['result']:
                details = data['result']['detailList']
                total_in, total_out = 0.0, 0.0
                for item in details:
                    amt = item.get('amount', '')
                    cleaned = amt.replace('+￥', '').replace('-￥-', '')
                    try:
                        val = float(cleaned)
                        if amt.startswith('+'):
                            total_in += val
                        elif amt.startswith('-'):
                            total_out += val
                    except:
                        pass
                return total_in - total_out, total_in, total_out, details
        except:
            pass
        return 0.0, 0.0, 0.0, []

    def withdraw_balance(self, amount=None):
        """Withdraw balance (requires real name verification)"""
        is_verified, message = self.check_real_name()
        if not is_verified:
            return {'success': False, 'message': message}

        payload = {
            "channelCode": "c20195660470001", "activityCode": "ONA20220411001",
            "infernalWallParams": self._infernal_params(), "envSource": "miniprogram"
        }
        if amount is not None:
            payload["amount"] = amount

        for retry in range(3):
            try:
                time.sleep(random.uniform(1.0, 3.0))
                if retry > 0:
                    payload["infernalWallParams"] = self._infernal_params()
                resp = self.session.post(
                    f"{self.base_url}/api/lemon/v1/common/activity/withdraw",
                    json=payload, timeout=15, proxies=self.proxies
                )
                data = resp.json()
                if data.get('code') == '0':
                    return {'success': True, 'message': data.get('message', '提现成功')}
                if "奖品已领完" not in str(data.get('message', '')):
                    return {'success': False, 'message': data.get('message', '提现失败')}
                time.sleep(3.0)
            except:
                if self.is_proxy_enabled:
                    proxy = self._get_proxy()
                    self.proxies = {'http': proxy, 'https': proxy} if proxy else None

        return {'success': False, 'message': '提现失败，已达到最大重试次数'}

    def check_real_name(self):
        for retry in range(3):
            try:
                time.sleep(random.uniform(1.0, 2.0))
                resp = self.session.get(
                    f"{self.base_url}/api/lemon/v1/sign/activity/check/realName",
                    timeout=10, proxies=self.proxies
                )
                data = resp.json()
                if data.get('code') == '0':
                    if data.get('result', False):
                        return True, "已完成实名认证"
                    return False, "未完成实名认证，请在众安健康小程序内完成实名认证"
            except:
                if self.is_proxy_enabled:
                    proxy = self._get_proxy()
                    self.proxies = {'http': proxy, 'https': proxy} if proxy else None
        return False, "实名认证检查失败，请稍后再试"


def validate_access_token(token):
    """Validate token and return account info"""
    try:
        client = ZhongAnHealthAuto(token)
        status = client.get_status()
        if not status:
            return False, {'error': '首页接口请求失败'}

        account_id = status.get('userId') or status.get('accountId')
        if not account_id or account_id == "未知":
            account_id = f"za_{hashlib.md5(str(int(time.time() * 1000)).encode()).hexdigest()[:10]}"

        phone = client.get_masked_phone()
        return True, {'accountId': account_id, 'phone': phone}
    except Exception as e:
        return False, {'error': f'验证异常: {str(e)}'}


# ========== Login ==========
def login():
    """Bind zhongan account via Access-Token"""
    sender.reply(
        "=====众安健康登录=====\n"
        "请按格式输入: Access-Token#备注\n"
        "示例: ABCDEFG123456#我的账号\n"
        "------------------\n"
        "回复\"q\"退出\n"
        "=================="
    )
    ck_input = sender.input(120000, 1, False)
    if not ck_input or ck_input.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    ck_input = ck_input.strip()
    if '#' not in ck_input:
        sender.reply("❌ 格式错误！请输入 Access-Token#备注")
        return

    access_token, remark = ck_input.split('#', 1)
    is_valid, result = validate_access_token(access_token)
    if not is_valid:
        sender.reply(f"❌ Token验证失败: {result.get('error')}")
        return

    account_id = str(result.get('accountId', 'unknown'))
    masked_phone = result.get('phone', '未知')

    middleware.bucketSet('s_zajk_token', account_id, str(access_token))
    middleware.bucketSet('s_zajk_phone', account_id, masked_phone)

    global uservalue
    accounts = _get_user_accounts()
    if account_id not in accounts:
        accounts.append(account_id)
    middleware.bucketSet('s_zajk_user', userid, json.dumps(accounts))
    uservalue = json.dumps(accounts)

    sender.reply(
        f"✅ 登录成功\n"
        f"📱 手机号: {vorto_utils.mask_account(masked_phone)}\n"
        f"🏷️ 备注: {remark}\n"
        f"------------------\n"
        f"发送\"众安管理\"进行账号授权"
    )


# ========== Query ==========
def query_zajk():
    """Query all bound accounts with details"""
    accounts = _get_user_accounts()
    if not accounts:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 众安登录 绑定\n==================")
        return

    for idx, account_id in enumerate(accounts, 1):
        access_token = middleware.bucketGet('s_zajk_token', account_id)
        if not access_token:
            sender.reply(f"===== 众安详情 =====\n账号 {idx}: ❌ Token缺失\n==================")
            continue

        expire = _get_auth_expire(account_id) or '未授权'
        auth_status = "✅ 已授权" if _is_authorized(account_id) else "❌ 未授权"

        client = ZhongAnHealthAuto(access_token)
        claimer = ZhongAnRewardClaimer(access_token)
        phone = client.get_masked_phone() or "未知"

        result_msg = (
            f"===== 众安详情 =====\n"
            f"📱 账号: {vorto_utils.mask_account(phone)}\n"
            f"🔐 状态: {auth_status}\n"
            f"📅 到期: {expire}\n"
        )

        balance, total_in, total_out, details = claimer.get_balance()
        result_msg += f"💰 总收入: {total_in:.2f}元 | 已提现: {total_out:.2f}元 | 余额: {balance:.2f}元\n"

        recent = [d for d in details[:5] if d.get('amount', '').startswith('+')]
        if recent:
            result_msg += "===== 🎁近期收入 =====\n"
            for tx in recent:
                amt = tx.get('amount', '').replace('+￥', '')
                result_msg += f"领取 {amt}元 - {tx.get('time', '')}\n"

        status = client.get_status()
        if status and not status.get('signInStatus', False):
            if client._signIn():
                result_msg += "✅ 已为您自动签到\n"

        result_msg += "=================="
        sender.reply(result_msg)


# ========== Authorization (via vorto_utils) ==========
def authorize_accounts(selected_accounts):
    """Authorize accounts using vorto_utils unified payment"""
    try:
        Vipmoney = float(middleware.bucketGet('s_zajk', 'Vipmoney') or '0.88')
        coin = int(middleware.bucketGet('s_zajk', 'coin') or '0')

        sender.reply(
            f"✅ {len(selected_accounts)} 个账号待授权\n"
            f"=====设置授权时长=====\n"
            f"请输入授权月数(如:1)\n"
            f"回复\"q\"退出\n"
            f"=================="
        )
        months_input = sender.input(120000, 1, False)
        if not months_input or months_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return False

        try:
            months = int(months_input)
            if months <= 0:
                sender.reply("❌ 月数必须大于0")
                return False
        except ValueError:
            sender.reply("❌ 请输入有效数字")
            return False

        total_money = Vipmoney * months * len(selected_accounts)

        if Vipmoney <= 0:
            success = 0
            for acc in selected_accounts:
                new_expire = vorto_utils.calculate_auth_time('s_zajk_auth', acc, months=months)
                middleware.bucketSet('s_zajk_auth', acc, new_expire)
                success += 1
            sender.reply(
                f"=====授权成功=====\n"
                f"📱 账号: {success}/{len(selected_accounts)}\n"
                f"💰 价格: 免费\n"
                f"⏰ 时长: {months}月\n"
                f"=================="
            )
            return True

        pay_config = vorto_utils.get_pay_config()
        available = []
        if pay_config.get('qr_pay_switch'):
            available.append(("扫码支付", "qrcode"))
        if pay_config.get('ma_pay_switch'):
            pay_types = pay_config.get('pay_types', {})
            if pay_types:
                for pk, pn in pay_types.items():
                    available.append((f"{pn}(码支付)", f"mapay_{pk}"))
        if coin > 0:
            available.append(("积分兑换", "coin"))

        if not available:
            sender.reply("❌ 未配置支付方式，请联系管理员在Vorto初始化中开启")
            return False

        pay_msg = (
            f"=====选择支付方式=====\n"
            f"💰 单价: {Vipmoney}元/月\n"
            f"⏰ 时长: {months}月\n"
            f"📱 账号: {len(selected_accounts)}个\n"
            f"💵 总价: {total_money}元\n"
            f"------------------"
        )
        for i, (name, _) in enumerate(available, 1):
            pay_msg += f"\n[{i}] {name}"
        pay_msg += "\n------------------\n回复数字选择\n回复\"q\"退出"

        sender.reply(pay_msg)
        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply("✅ 已退出支付流程")
            return False

        try:
            pay_idx = int(pay_choice) - 1
            if pay_idx < 0 or pay_idx >= len(available):
                sender.reply("❌ 无效的选择")
                return False
        except ValueError:
            sender.reply("❌ 无效的选择")
            return False

        pay_name, pay_type = available[pay_idx]
        paid = False

        if pay_type == "coin":
            total_coins = coin * months * len(selected_accounts)
            user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
            if user_coins < total_coins:
                sender.reply(f"❌ 积分不足\n当前积分: {user_coins}\n所需积分: {total_coins}")
                return False
            sender.reply(
                f"=====积分授权确认=====\n"
                f"🎯 需要: {total_coins}积分\n"
                f"💰 当前: {user_coins}积分\n"
                f"------------------\n"
                f"回复\"y\"确认\n回复其他取消"
            )
            confirm = sender.input(60000, 1, False)
            if not confirm or confirm.lower() != 'y':
                sender.reply("✅ 已取消")
                return False
            middleware.bucketSet('dd_sign_points', userid, str(user_coins - total_coins))
            paid = True

        elif pay_type == "qrcode":
            paid = _process_qrcode_payment("众安健康授权", months, total_money)

        elif pay_type.startswith("mapay_"):
            paid = _process_mapay_payment("众安健康授权", months, total_money, pay_type.replace("mapay_", ""))

        if not paid:
            return False

        success = 0
        for acc in selected_accounts:
            try:
                new_expire = vorto_utils.calculate_auth_time('s_zajk_auth', acc, months=months)
                middleware.bucketSet('s_zajk_auth', acc, new_expire)
                success += 1
            except Exception as e:
                sender.reply(f"账号 {acc} 授权失败: {str(e)}")

        sender.reply(
            f"=====授权成功=====\n"
            f"📱 账号: {success}/{len(selected_accounts)}\n"
            f"💳 支付: {pay_name}\n"
            f"⏰ 时长: {months}月\n"
            f"------------------\n"
            f"发送\"众安查询\"查看详情"
        )
        return True
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")
        return False


def _process_qrcode_payment(project, months, money):
    if float(money) == 0:
        return True
    pay_config = vorto_utils.get_pay_config()
    zsm = pay_config.get('zsm', '')
    if not zsm:
        sender.reply('❌ 未配置收款码，请联系管理员')
        return False
    sender.reply(
        f"======扫码支付======\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)
    ddzf = sender.waitPay("q", 300000)
    if str(ddzf) == 'q':
        sender.reply('✅ 已取消')
        return False
    try:
        if isinstance(ddzf, str):
            ddzf = json.loads(ddzf)
        if float(ddzf.get('Money') or ddzf.get('money', 0)) >= float(money):
            return True
        sender.reply("❌ 支付金额不足")
        return False
    except:
        sender.reply("❌ 支付验证失败")
        return False


def _process_mapay_payment(project, months, money, pay_type='alipay'):
    if float(money) == 0:
        return True
    pay_config = vorto_utils.get_pay_config()
    if not pay_config.get('ma_pay_switch'):
        sender.reply("❌ 码支付功能未开启")
        return False
    try:
        out_trade_no = f"ZAJK{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
        pay_type_name = pay_config.get('pay_types', {}).get(pay_type, '支付宝')
        sender.reply(
            f"=====码支付信息=====\n"
            f"🎫 商品: {project}\n"
            f"📅 时长: {months}月\n"
            f"💰 金额: {money}元\n"
            f"💳 方式: {pay_type_name}\n"
            f"=================="
        )
        mapay = vorto_utils.MaPayClient()
        order = mapay.create_order(float(money), pay_type, out_trade_no, f"{project}-{money}", userid)
        if order.get('error'):
            sender.reply(f"❌ 创建订单失败: {order.get('error')}")
            return False
        pay_url = order.get('pay_url')
        qr_url = vorto_utils.generate_qrcode_url(pay_url)
        sender.replyImage(qr_url)
        sender.reply(f'💳 请使用【{pay_type_name}】扫码支付\n⏰ 5分钟内完成\n输入"q"可取消')
        start = time.time()
        while time.time() - start < 300:
            ui = sender.input(5000, 1, False)
            if ui and ui.lower() == 'q':
                sender.reply("✅ 已取消支付")
                return False
            if mapay.is_paid(out_trade_no):
                sender.reply("✅ 支付成功！")
                return True
        sender.reply("❌ 支付超时")
        return False
    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False


# ========== Manage ==========
def manage_zajk():
    """Account management: authorize / delete"""
    accounts = _get_user_accounts()
    if not accounts:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return

    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    option = sender.input(60000, 1, False)
    if not option or option.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    if option not in ['1', '2']:
        sender.reply("❌ 无效选择")
        return

    action = '授权' if option == '1' else '删除'

    account_list = "=====账号列表=====\n[0] 全部账号"
    for i, acc in enumerate(accounts, 1):
        phone = middleware.bucketGet('s_zajk_phone', acc) or "未知"
        expire = _get_auth_expire(acc) or '未授权'
        status = "✅" if _is_authorized(acc) else "❌"
        account_list += f"\n[{i}] {vorto_utils.mask_account(phone)} {status}({expire})"
    account_list += f"\n------------------\n请选择要{action}的账号\n多账号逗号分隔\n回复\"q\"退出"

    sender.reply(account_list)
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return

    selected = []
    if choice == '0':
        selected = accounts[:]
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(',')]
            for idx in indices:
                if 0 <= idx < len(accounts):
                    selected.append(accounts[idx])
        except ValueError:
            sender.reply("❌ 无效的选择格式")
            return

    if not selected:
        sender.reply("❌ 未选择有效账号")
        return

    if option == '1':
        authorize_accounts(selected)
    else:
        confirm_msg = "=====删除确认=====\n即将删除以下账号:\n"
        for acc in selected:
            phone = middleware.bucketGet('s_zajk_phone', acc) or "未知"
            confirm_msg += f"- {vorto_utils.mask_account(phone)}\n"
        confirm_msg += "------------------\n⚠️ 数据及授权无法恢复\n回复\"y\"确认删除"

        sender.reply(confirm_msg)
        confirm = sender.input(60000, 1, False)
        if not confirm or confirm.lower() != 'y':
            sender.reply("✅ 已取消删除")
            return

        success = 0
        for acc in selected:
            try:
                middleware.bucketDel('s_zajk_token', acc)
                middleware.bucketDel('s_zajk_auth', acc)
                middleware.bucketDel('s_zajk_phone', acc)
                if acc in accounts:
                    accounts.remove(acc)
                success += 1
            except:
                continue

        if accounts:
            middleware.bucketSet('s_zajk_user', userid, json.dumps(accounts))
        else:
            middleware.bucketDel('s_zajk_user', userid)

        sender.reply(f"✅ 已成功删除 {success}/{len(selected)} 个账号")


# ========== Admin Run ==========
def za_auto_run():
    """Admin: run all authorized accounts"""
    if not sender.isAdmin():
        sender.reply("❌ 只有管理员才能使用此命令")
        return

    all_users = middleware.bucketAllKeys('s_zajk_user') or []
    if not all_users:
        sender.reply("❌ 未找到任何用户")
        return

    sender.reply("🚀 开始运行所有已授权账号...")

    success_count, failed_count = 0, 0
    total_income = 0.0
    user_balance_reminders = {}

    for uid in all_users:
        user_accounts = _get_user_accounts(uid)
        for account_id in user_accounts:
            if not _is_authorized(account_id):
                continue

            access_token = middleware.bucketGet('s_zajk_token', account_id)
            if not access_token:
                failed_count += 1
                continue

            try:
                client = ZhongAnHealthAuto(access_token)
                phone = client.get_masked_phone() or "未知"

                status = client.get_status()
                if not status:
                    failed_count += 1
                    continue

                # Sign in
                if not status.get('signInStatus', False):
                    client._signIn()
                    status = client.get_status() or status

                # Run tasks
                tasks = client.extract_product_info(status) if status else []
                if tasks:
                    client._run_task(tasks)

                # Subscribe + claim rewards
                claimer = ZhongAnRewardClaimer(access_token)
                if not status.get('isSubscribeWechat', False):
                    claimer.subscribe_message()
                claimer.claim_all_rewards()

                # Get balance
                balance, _, _, _ = claimer.get_balance()
                total_income += balance
                success_count += 1

                if balance >= 5.0:
                    if uid not in user_balance_reminders:
                        user_balance_reminders[uid] = []
                    user_balance_reminders[uid].append((vorto_utils.mask_account(phone), balance))

            except Exception as e:
                failed_count += 1

    sender.reply(
        f"🚀 众安任务汇总 📊\n"
        f"====================\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {failed_count}个\n"
        f"💰 总余额: {total_income:.2f}元\n"
        f"==================="
    )

    # Push balance reminders
    for uid, accs in user_balance_reminders.items():
        try:
            msg = "=====众安余额提醒=====\n"
            for phone, bal in accs:
                msg += f"📱 账号: {phone}\n💰 余额: {bal:.2f}元\n-------------------\n"
            msg += "💡 余额已达5元以上\n可前往小程序提现\n==================="
            for ch in ['wx', 'qq']:
                try:
                    middleware.push(ch, '', uid, '众安余额提醒', msg)
                    break
                except:
                    continue
        except:
            pass


# ========== Summary ==========
def za_summary():
    """Summary of all account withdrawals"""
    accounts = _get_user_accounts()
    if not accounts:
        sender.reply("❌ 您尚未绑定任何账号")
        return

    sender.reply("⏳ 正在统计所有账号提现记录...")
    total_withdrawal = 0.0
    details_list = []

    for idx, acc in enumerate(accounts, 1):
        access_token = middleware.bucketGet('s_zajk_token', acc)
        if not access_token:
            details_list.append(f"📱 账号{idx}: ❌ Token缺失")
            continue
        try:
            client = ZhongAnHealthAuto(access_token)
            claimer = ZhongAnRewardClaimer(access_token)
            phone = client.get_masked_phone() or f"账号{idx}"

            _, _, withdrawal, _ = claimer.get_balance()
            details_list.append(f"📱 {vorto_utils.mask_account(phone)}: 已提现 {withdrawal:.2f}元")
            total_withdrawal += withdrawal
        except Exception as e:
            details_list.append(f"📱 账号{idx}: ❌ 查询失败")

    sender.reply(
        f"=====众安提现总结=====\n"
        f"📊 账号数: {len(accounts)}个\n"
        f"💰 总提现: {total_withdrawal:.2f}元\n"
        f"====================\n"
        + "\n".join(details_list) +
        f"\n==================="
    )


# ========== Admin Auth (via vorto_utils) ==========
def ks_auth():
    """Admin authorization by days"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return
    sender.reply(
        "=====管理员授权=====\n"
        "[1] 授权所有用户\n"
        "[2] 按用户授权\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出"
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    if choice == '1':
        vorto_utils.admin_auth_all_accounts(sender, 's_zajk_user', 's_zajk_auth', 's_zajk_token')
    elif choice == '2':
        vorto_utils.admin_auth_by_user(sender, 's_zajk_user', 's_zajk_auth', 's_zajk_token')
    else:
        sender.reply("❌ 无效选择")


# ========== Auth Check (custom: push_count + s_zajk_phone cleanup) ==========
def check_auth_status():
    """Check auth status with push count limit, auto-clean after N pushes"""
    notify = middleware.bucketGet('s_zajk', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"

    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_zajk_user')
    if not all_users:
        return "❌ 没有用户"

    notify_limit = int(middleware.bucketGet('s_zajk', 'notify_limit') or '3')
    notify_days = int(middleware.bucketGet('s_zajk', 'notify_days') or '3')
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0

    for uid in all_users:
        try:
            accounts = _get_user_accounts(uid)
            to_notify = []
            to_clean = []

            for acc in accounts:
                expire_str = _get_auth_expire(acc)
                if not expire_str:
                    to_clean.append({'id': acc, 'expire': '未授权', 'days': 0})
                    continue
                try:
                    expire_date = datetime.strptime(expire_str, "%Y-%m-%d").date()
                    days_left = (expire_date - current_date).days
                    if days_left <= 0:
                        to_clean.append({'id': acc, 'expire': expire_str, 'days': days_left})
                    elif days_left <= notify_days:
                        to_notify.append({'id': acc, 'expire': expire_str, 'days': days_left})
                except:
                    to_clean.append({'id': acc, 'expire': expire_str, 'days': 0})

            total += len(accounts)

            if to_clean:
                push_count = int(middleware.bucketGet('s_zajk_push_count', uid) or '0')

                if push_count >= notify_limit:
                    for item in to_clean:
                        middleware.bucketDel('s_zajk_token', item['id'])
                        middleware.bucketDel('s_zajk_auth', item['id'])
                        middleware.bucketDel('s_zajk_phone', item['id'])
                        if item['id'] in accounts:
                            accounts.remove(item['id'])
                        cleaned += 1

                    if accounts:
                        middleware.bucketSet('s_zajk_user', uid, json.dumps(accounts))
                    else:
                        middleware.bucketDel('s_zajk_user', uid)
                    middleware.bucketDel('s_zajk_push_count', uid)
                else:
                    expired_list = "\n".join([
                        f"📱 {vorto_utils.mask_account(middleware.bucketGet('s_zajk_phone', a['id']) or a['id'])} ({a['expire']})"
                        for a in to_clean
                    ])
                    msg = (
                        f"=====众安账号检测=====\n"
                        f"🚨 授权过期:\n{expired_list}\n"
                        f"⚠️ 第{push_count + 1}次提醒(共{notify_limit}次)\n"
                        f"💡 发送\"众安管理\"处理\n"
                        f"=================="
                    )
                    for ch in channels:
                        try:
                            middleware.push(imType=ch, groupCode='', userID=uid, title="", content=msg)
                            notified += 1
                        except:
                            pass
                    middleware.bucketSet('s_zajk_push_count', uid, str(push_count + 1))

            if to_notify:
                notify_list = "\n".join([
                    f"📱 {vorto_utils.mask_account(middleware.bucketGet('s_zajk_phone', a['id']) or a['id'])} 剩余{a['days']}天({a['expire']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====众安账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"众安管理\"续费\n"
                    f"=================="
                )
                for ch in channels:
                    try:
                        middleware.push(imType=ch, groupCode='', userID=uid, title="", content=msg)
                        notified += 1
                    except:
                        pass
        except:
            pass

    return f"✅ 检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"


# ========== Tutorial ==========
def show_tutorial():
    sender.reply(
        "=====众安健康教程=====\n"
        "📱 用户指令:\n"
        "• 众安登录 - 绑定众安健康账号\n"
        "• 众安查询 - 查询账号状态和余额\n"
        "• 众安管理 - 授权/删除账号\n"
        "• 众安总结 - 统计所有账号提现总额\n"
        "• 众安教程 - 查看本教程\n"
        "------------------\n"
        "🔧 管理员指令:\n"
        "• 众安授权 - 管理员按天数授权\n"
        "• 众安一键运行 - 执行所有账号任务\n"
        "• 众安检测 - 检测过期账号并清理\n"
        "------------------\n"
        "💡 登录格式:\n"
        "📝 格式: Access-Token#备注\n"
        "📝 示例: Uemu5zgKoPlE...#我的账号\n"
        "------------------\n"
        "📝 Token获取方式:\n"
        "1. 打开微信小程序「众安健康」\n"
        "   #小程序://众安健康/sp0x8xwo0wlYARj\n"
        "2. 使用抓包工具(HttpCanary/Fiddler)\n"
        "3. 搜索: ihealth.zhongan.com\n"
        "4. 找到请求头中的 access-token\n"
        "------------------\n"
        "🎯 使用流程:\n"
        "1. 发送\"众安登录\"绑定账号\n"
        "2. 发送\"众安管理\"选择授权账号\n"
        "3. 等待定时任务自动执行\n"
        "4. 余额≥5元时会自动提醒提现\n"
        "=================="
    )


# ========== Main ==========
def main():
    try:
        msg = sender.getMessage()
    except:
        msg = ""

    if '众安登录' in msg or '登录众安' in msg:
        login()
    elif '众安查询' in msg:
        query_zajk()
    elif '众安管理' in msg:
        manage_zajk()
    elif '众安教程' in msg:
        show_tutorial()
    elif '众安授权' in msg:
        ks_auth()
    elif '众安一键运行' in msg:
        za_auto_run()
    elif '众安总结' in msg:
        za_summary()
    elif '众安检测' in msg:
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    elif sender.getImtype() == 'fake':
        try:
            result = check_auth_status()
            middleware.notifyMasters(result)
        except:
            pass
    else:
        sender.setContinue()

if __name__ == "__main__":
    main()
