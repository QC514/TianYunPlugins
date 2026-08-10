# [language: python] 
# [wb: true]
# [service:	<img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif">QQ：1934103887]
# [disable: false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
# [priority: 99999999999999999999] 优先级，数字越大表示优先级越高
# [open_source: false] 是否开源
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，方便开发者测试
# [pin:false]
# [rule: ^顺丰抢兑$|^运行抢兑$|^清理抢兑$|^顺丰取消抢兑$]
# [price: 12.88]
# [author: 1934103887]
# [title: 顺丰抢兑]
# [cron: ]
# [icon: https://www.sf-express.com/chn/_next/static/media/ic-white-logo.abea573f.png ]
# [version: 7.9.0] #
# [description: ✨顺丰抢兑助手✨<br>插件内置抢兑无需抓包，完美适配呆呆、幼稚园、chuan、yuhua的顺丰<br>功能：抢兑积分商城或积分秒杀内的实物,以及免单券抢兑和6折券抢兑。用户发送”顺丰抢兑”提交账号<br>管理员请去计划任务定时”运行抢兑”自处理命令，详细配置请看配参内说明<br>现已支持自定义抢兑，仅限顺丰代挂用户使用<br>抢兑的账号会储存在Joh_sf建议抢兑完后发送”清理抢兑”清理定时<br>🌸5.20更新：增加代理池和API代理功能选项<br>🌸7.26更新：增加会员日抢免单券功能<br>🌸10.12更新：支持抢兑顺丰积分秒杀板块+优化逻辑<br>🌸11.27更新：增加”顺丰取消抢兑”命令<br>🌸01.21更新：增加超寄星期三 6 折寄件券抢券逻辑]

# [param: {"required":false,"key":"Joh_sf_config.WX","bool":false,"placeholder":"","name":"通知管理员WX","desc":"运行结果会通知WX管理员，不填不推送"}]
# [param: {"required":false,"key":"Joh_sf_config.QQ","bool":false,"placeholder":"","name":"通知管理员QQ","desc":"运行结果会通知QQ管理员，不填不推送"}]
# [param: {"required":false,"key":"Joh_sf_config.TG","bool":false,"placeholder":"","name":"通知管理员TG","desc":"运行结果会通知TG管理员，不填不推送"}]
# [param: {"required":true,"key":"Joh_sf_config.dinshi","bool":false,"placeholder":"09:00:00,10:00:00,12:00:00,14:00:00,15:00:00,18:00:00","name":"抢兑时间","desc":"必须设置设置抢兑时间，格式为: 时:分:秒<br>例如：10:00:00表示10:00:00秒开始执行兑换请求<br>⚠️重要：<br>⚠️①计划任务添加自处理命令”运行抢兑”比如月饼是十点开始就定时30 59 9 * * *<br>到时插件会自动储存账号信息，到点直接请求兑换<br>⚠️②配参建议设置如：09:00:00,10:00:00,12:00:00,14:00:00,15:00:00,18:00:00  插件会自动判断是免单场还是秒杀场 <br>其他时间是免单券是9/12/15点、秒杀是10/14/18点<br>可以一股脑全部定时30 59 9,13,17 * * *和30 59 8,11,14 26-28 * *"}]
# [param: {"required":false,"key":"Joh_sf_config.choice","bool":false,"placeholder":"不填不走代理","name":"代理选择","desc":"填1代理池，填2API代理<br>备用功能如非必要不用设置代理"}]
# [param: {"required":false,"key":"Joh_sf_config.proxy","bool":false,"placeholder":"例:http://192.168.10.7:8081","name":"代理池","desc":"本地代理池链接"}]
# [param: {"required":false,"key":"Joh_sf_config.proxy_api","bool":false,"placeholder":"例:http://api2.xkdaili.com/","name":"API代理","desc":"API代理链接"}]
# [param: {"required":false,"key":"Joh_sf_config.mrd","bool":false,"placeholder":"","name":"是否开启会员日免单券","desc":"填1开启填2关闭，默认开启"}]
# [param: {"required":false,"key":"Joh_sf_config.sc","bool":false,"placeholder":"","name":"是否开启商城实物","desc":"填1开启填2关闭，默认开启"}]
# [param: {"required":false,"key":"Joh_sf_config.ms","bool":false,"placeholder":"","name":"是否开启积分秒杀","desc":"填1开启填2关闭，默认开启"}]
# [param: {"required":false,"key":"Joh_sf_config.zk","bool":false,"placeholder":"","name":"是否开启超寄星期三6折券","desc":"填1开启填2关闭，默认开启"}]

import hashlib
import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time as dt_time
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote, unquote

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

import middleware

# =========================
# 常量与全局
# =========================
SIGN_TOKEN = 'wwesldfs29aniversaryvdld29'
SYS_CODE = 'MCS-MIMP-CORE'

HOST = "mcs-mimp-web.sf-express.com"
BASE_URL = f"https://{HOST}"
USER_INFO_API = f"{BASE_URL}/mcs-mimp/commonPost/~memberIntegral~userInfoService~personalInfoNew"

# 省市区固定 ID（如无则留空）
FIX_PID = ""
FIX_CID = ""
FIX_COID = ""

# 超寄星期三 6 折券 标记前缀
WEEKLY_60_PREFIX = "weekly60"

# 获取当前日期（日）
_now = datetime.now()
_day = _now.day

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# 已登录账号集合（避免重复登录）
logged_in_accounts = set()

# 手机号正则（用于脱敏推送）
PHONE_RE = re.compile(r"1[3-9]\d{9}")

# =========================
# 功能开关配置（类似代码2）
# =========================
FREE_COUPON_ENABLED = middleware.bucketGet('Joh_sf_config', 'mrd') != "2"
GOODS_ENABLED = middleware.bucketGet('Joh_sf_config', 'sc') != "2"
SECKILL_ENABLED = middleware.bucketGet('Joh_sf_config', 'ms') != "2"
WEEKLY_60_ENABLED = middleware.bucketGet('Joh_sf_config', 'zk') != "2"

# =========================
# 工具函数
# =========================

def is_phone_account(account_key: str) -> bool:
    return isinstance(account_key, str) and bool(
        re.fullmatch(r'1\d{10}|1\d{2}\*{4}\d{4}', account_key)
    )

def build_proxies(proxy: Optional[str]) -> Optional[Dict[str, str]]:
    if not proxy:
        return None
    return {"http": proxy, "https": proxy}


def mask_phone_number(phone: str) -> str:
    """对手机号进行脱敏处理，隐藏中间4位数字。"""
    if isinstance(phone, str) and len(phone) == 11 and phone.isdigit():
        return phone[:3] + "****" + phone[7:]
    return phone


def safe_eval_to_list(value) -> List[str]:
    """将存储的字符串解析为列表；兼容单值与列表字符串。"""
    if not value:
        return []
    try:
        obj = eval(value)
        return obj if isinstance(obj, list) else [obj]
    except Exception:
        return [value]


def encode_link(link: str) -> str:
    return quote(link, safe=':/')


def get_proxy() -> Optional[str]:
    """获取代理配置；保持原逻辑与返回值不变。"""
    choice = middleware.bucketGet('Joh_sf_config', 'choice')
    if choice == '1':
        proxy = middleware.bucketGet('Joh_sf_config', 'proxy')
        if not proxy:
            return None
        if not proxy.startswith(('http://', 'https://')):
            proxy = 'http://' + proxy
        return proxy
    elif choice == '2':
        proxy_api = middleware.bucketGet('Joh_sf_config', 'proxy_api')
        if not proxy_api:
            return None
        try:
            resp = requests.get(proxy_api, timeout=10)
            if resp.status_code == 200:
                proxy_text = resp.text.strip()
                if proxy_text:
                    return f'http://{proxy_text}'
        except Exception as e:
            print(f'获取API代理失败: {str(e)}')
            return None
    return None

def fetch_member_level(url: str, proxy: Optional[str] = None) -> Optional[Tuple[int, str]]:

    try:
        s = requests.Session()
        s.verify = False
        s.headers.update({
            "Host": HOST,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue",
            "platform": "MINI_PROGRAM",
        })

        proxies = build_proxies(proxy)
        r = s.get(url, timeout=10, proxies=proxies)
        r.raise_for_status()

        mobile = s.cookies.get("_login_mobile_")
        if not mobile:
            print("❌ 登录失败：缺少 _login_mobile_ Cookie")
            return None

        # 复用 SFExpress 的签名逻辑
        ts = str(int(time.time() * 1000))
        sig = hashlib.md5(f"token={SIGN_TOKEN}&timestamp={ts}&sysCode={SYS_CODE}".encode()).hexdigest()
        
        payload = {"sysCode": "ESG-CEMP-CORE", "optionalColumns": ["levelName"], "token": "zeTLTYeG0bLetfRk"}
        resp = s.post(USER_INFO_API, headers={**s.headers, "sysCode": SYS_CODE, "timestamp": ts, "signature": sig}, 
                     json=payload, timeout=10, proxies=proxies)
        
        data = resp.json()
        if not data.get("success"):
            print(f"❌ 查询失败: {data.get('errorMessage', '未知错误')}")
            return None

        obj = data.get("obj", {})
        level = obj.get("memberLevel")
        if isinstance(level, int) and level >= 0:
            level_name = obj.get("levelName", "")
            print(f"✨ 查询成功！会员 {mobile[:3]}****{mobile[7:]} 等级: {level} ({level_name})")
            return level, level_name
        
        print(f"⚠️ 等级字段异常: {level}")
        return None

    except Exception as e:
        print(f"❌ 查询会员等级异常: {e}")
        return None

def get_account_phone(account_key: str) -> Optional[str]:
    """原 chuan 库：uuid -> 脱敏手机号。"""
    return middleware.bucketGet('chuan_sf_phone', account_key)


def get_real_phone(account_key: str) -> Optional[str]:
    if is_phone_account(account_key):
        return account_key
    if isinstance(account_key, str) and len(account_key) == 32:  # uuid
        masked = middleware.bucketGet('chuan_sf_phone', account_key)
        if masked and '****' in masked:
            return masked
    return None

def get_user_account_keys(sender) -> List[str]:
    user_id = sender.getUserID()
    im_type = sender.getImtype()
    seen_masked = set()
    result = []

    for bucket in ('yuhua_sf_user', 'dd_sf_user', 'Yzyxmm_sf_bind'):
        arr = middleware.bucketGet(bucket, user_id)
        if not arr:
            continue
        for phone in safe_eval_to_list(arr):
            if is_phone_account(phone):
                masked = mask_phone_number(phone) if '****' not in phone else phone
                if masked not in seen_masked:
                    seen_masked.add(masked)
                    result.append(masked)

    bk = {'wx': 'chuan_sfWX', 'qq': 'chuan_sfQQ', 'tg': 'chuan_sfTG'}.get(im_type)
    if bk:
        for uuid in middleware.bucketKeys(bucket=bk, value=user_id):
            masked = middleware.bucketGet('chuan_sf_phone', uuid)
            if masked and masked not in seen_masked:
                seen_masked.add(masked)
                result.append(masked)

    return result


def check_date_valid(date_str_bucket: Optional[str]) -> bool:
    if not date_str_bucket:
        return False
    try:
        today = time.strptime(time.strftime('%Y-%m-%d', time.localtime()), '%Y-%m-%d')
        expire = time.strptime(date_str_bucket, '%Y-%m-%d')
        return today <= expire
    except Exception:
        return False


def check_yuhua_sf_authorization(phone: str) -> bool:
    return check_date_valid(middleware.bucketGet('yuhua_sf_auth', phone))


def check_yzyxmm_authorization(phone: str) -> bool:
    return check_date_valid(middleware.bucketGet('Yzyxmm_sf_Vip', phone))


def check_dd_sf_authorization(phone: str) -> bool:
    return check_date_valid(middleware.bucketGet('dd_sf_auth', phone))


def check_chuan_sf_authorization(account_key: str) -> bool:
    return check_date_valid(middleware.bucketGet('chuan_sf_AuthorizationTime', account_key))


def check_authorization(account_key: str) -> bool:
    if is_phone_account(account_key):
        return (
            check_yzyxmm_authorization(account_key)
            or check_yuhua_sf_authorization(account_key)
            or check_dd_sf_authorization(account_key)
        )
    return check_chuan_sf_authorization(account_key)


def get_account_link(account_key: str) -> Optional[str]:
    if is_phone_account(account_key):
        return (
            middleware.bucketGet('Yzyxmm_sf_account', account_key)
            or middleware.bucketGet('dd_sf_token', account_key)
            or middleware.bucketGet('yuhua_sf_token', account_key)
        )
    return middleware.bucketGet('chuan_sf_accountId', account_key)


def get_user_address(sender, phone_masked: str) -> Optional[str]:
    return middleware.bucketGet('Joh_sf_dz', phone_masked)


def set_user_address(sender, phone_masked: str, address: str) -> None:
    middleware.bucketSet('Joh_sf_dz', phone_masked, address)


def parse_address(address_str: str) -> Optional[Dict[str, str]]:
    try:
        address_str = address_str.replace('，', ',')
        parts = [p.strip() for p in address_str.split(',')]
        if len(parts) != 7:
            return None
        province, city, district, contact, detail_address, phone, full_address = parts
        if not all([province, city, district, contact, detail_address, phone, full_address]):
            return None
        if not (phone.isdigit() and len(phone) == 11):
            return None
        return {
            "province": province,
            "city": city,
            "distinct": district,
            "receiveContact": contact,
            "receiveAddress": detail_address,
            "receivePhone": phone,
            "fullReceiveAddress": full_address,
        }
    except Exception:
        return None


def store_encoded_link(sender, phone_masked: str, encoded_link: str) -> None:
    middleware.bucketSet('Joh_sf', phone_masked, encoded_link)

# =========================
# 业务类：抢兑 / 查询
# =========================

class SFExpress:
    def __init__(self, encoded_link: str, phone_masked: str, index: int, sender):
        self.encoded_link = unquote(encoded_link) if encoded_link else ''
        self.phone_masked = phone_masked
        self.index = index + 1
        self.sender = sender

        self.s = requests.session()
        self.s.verify = False

        # 保持请求头不变
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh',
            'platform': 'MINI_PROGRAM',
        }
        self.session_id = None
        self.cookies: Dict[str, str] = {}
        self.phone = None
        self.mobile = None

        self.proxy = get_proxy()
        self.login_res = self.login()
        self.goods_info: List = []  # 支持多个商品
        self.task_type: Optional[str] = None  # 'goods' / 'seckill' / 'weekly60'
        
    def cleanup_account_data(self) -> None:
        """删除特定账号的兑换数据"""
        try:
            # 仅删除当前账号的兑换数据
            middleware.bucketDel('Joh_sf_Items', self.phone_masked)
            middleware.bucketDel('Joh_sf', self.phone_masked)
            print(f"✅ 账号【{self.phone_masked}】的抢兑信息已清除")
        except Exception as e:
            print(f"❌ 清理数据时出错: {str(e)}")

    def _apply_sign(self) -> None:
        timestamp = str(int(time.time() * 1000))
        data = f'token={SIGN_TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        self.headers.update({'sysCode': SYS_CODE, 'timestamp': timestamp, 'signature': signature})

    def login(self) -> bool:
        if self.phone_masked in logged_in_accounts:
            print(f'👤 账号【{self.phone_masked}】已登录过，跳过重复登录')
            return True
        response = None
        try:
            proxies = build_proxies(self.proxy)
            print(f"📡 账号 {self.phone_masked} 使用代理：{proxies}")
            response = self.s.get(self.encoded_link, headers=self.headers, proxies=proxies)
            self.cookies = self.s.cookies.get_dict()
            self.phone = self.cookies.get('_login_mobile_', 'None')
            self.mobile = (self.phone[:3] + "*" * 4 + self.phone[7:]) if self.phone and self.phone != 'None' else ''
            self.session_id = (
                self.cookies.get('sessionId')
                or self.cookies.get('SESSIONID')
                or self.cookies.get('sessionid')
            )
            if self.phone and self.phone != 'None' and self.session_id:
                print(f'👤 用户:【{self.mobile}】登陆成功\n🔑 sessionId: {self.session_id}')
                logged_in_accounts.add(self.phone_masked)
                return True
            print(f'❌ 登录失败 状态码:{getattr(response, "status_code", "-")} cookies:{self.cookies}')
            return False
        except Exception as e:
            print(f'❌ 登录异常: {str(e)} 状态码:{getattr(response, "status_code", "-")}')
            return False

    def do_request(self, url: str, data: Optional[dict] = None, req_type: str = 'post'):
        self._apply_sign()
        proxies = build_proxies(self.proxy)
        data = data or {}
        try:
            if req_type.lower() == 'get':
                resp = self.s.get(url, headers=self.headers, proxies=proxies)
            else:
                resp = self.s.post(url, headers=self.headers, json=data, proxies=proxies)
            self.cookies = self.s.cookies.get_dict()
            self.session_id = self.cookies.get('sessionId', self.session_id)
            return resp.json()
        except Exception as e:
            print(f'请求异常: {str(e)}')
            return None

    def exchange_goods(self) -> str:
        if not self.session_id:
            print("❌ 无法获取sessionId，兑换失败")
            return "❌ 兑换失败：无法获取sessionId"
        if not self.goods_info:
            print("❌ 未设置商品信息，兑换失败")
            return "❌ 兑换失败：未设置商品信息"

        results = []
        for goods_name, goods_id in self.goods_info:
            print(f'🎁 开始兑换商品: {goods_name}')
            address_str = middleware.bucketGet('Joh_sf_dz', self.phone_masked)
            if not address_str:
                print('❌ 未获取到收货地址信息')
                results.append(f"兑换{goods_name}失败: 未获取到收货地址信息")
                continue
            address = parse_address(address_str)
            if not address:
                print('❌ 地址信息格式错误')
                results.append(f"兑换{goods_name}失败: 地址信息格式错误")
                continue

            payload = {
                "from": "Point_Mall",
                "orderSource": "POINT_MALL_EXCHANGE",
                "goodsNo": goods_id,
                "quantity": 1,
                "province": address["province"],
                "city": address["city"],
                "distinct": address["distinct"],
                "receiveContact": address["receiveContact"],
                "receiveAddress": address["receiveAddress"],
                "receivePhone": address["receivePhone"],
                "fullReceiveAddress": address["fullReceiveAddress"],
            }
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~createOrder"

            try:
                send_time = time.time()
                send_time_str = time.strftime('%Y-%m-%d %H:%M:%S.%f', time.localtime(send_time))
                print(f"📤 发送兑换请求时间: {send_time_str}")

                proxies = build_proxies(self.proxy)
                resp = self.s.post(url, headers=self.headers, json=payload, proxies=proxies)
                data = resp.json()
                if data.get('success'):
                    order_no = data.get("obj", {}).get("orderNo", "")
                    print(f'🎉 兑换成功: {goods_name} 订单号:{order_no}')
                    results.append(f"兑换{goods_name}成功: 订单号:{order_no} ")
                    self.cleanup_account_data()  # 兑换成功后清理当前账号数据
                else:
                    err = data.get("errorMessage", "未知错误")
                    print(f'❌ {goods_name} 兑换失败: {err}')
                    results.append(f"兑换{goods_name}失败: {err} ")
            except Exception as e:
                print(f'❌ {goods_name} 兑换请求异常: {str(e)}')
                results.append(f"兑换{goods_name}失败: {str(e)} ")
        return "\n".join(results)

    def exchange_free_coupon(self, round_time: str) -> str:
        """会员日免单券抢兑（保持请求值与路径一致）。"""
        self._apply_sign()
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        headers = self.headers.copy()
        headers.update({
            "Cookie": cookie_str,
            "Content-Type": "application/json",
            "platform": "MINI_PROGRAM",
            "sysCode": SYS_CODE,
            "timestamp": self.headers.get("timestamp"),
            "signature": self.headers.get("signature"),
        })
        payload = {"roundTime": round_time}
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~memberDayFreeService~freeCouponPurchase"
        try:
            resp = self.s.post(url, headers=headers, json=payload, proxies=build_proxies(self.proxy), timeout=10)
            data = resp.json()
            print(f"【最终请求 Cookie】>>>>\n{cookie_str}\n<<<<")
            if data.get("success"):
                self.cleanup_account_data()
                return f"🎉 免单券抢兑成功（场次：{round_time}）"
            return f"❌ 免单券抢兑失败：{data.get('errorMessage', '未知错误')}（场次：{round_time}）"
        except Exception as e:
            return f"❌ 免单券请求异常：{str(e)}（场次：{round_time}）"

    def exchange_weekly_60_coupon(self) -> str:
        """
        超寄星期三 6 折寄件券抢券逻辑：
        1. 调用 seckillPacketInfo 获取礼包信息
        2. 使用礼包编码调用 receiveSeckillPacket 抢券
        """
        if not self.session_id:
            print("❌ 无法获取sessionId，6折券抢券失败")
            return "❌ 抢6折券失败：无法获取sessionId"

        self._apply_sign()
        cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
        headers = self.headers.copy()
        headers.update({
            "Cookie": cookie_str,
            "Content-Type": "application/json",
            "platform": "MINI_PROGRAM",
            "sysCode": SYS_CODE,
            "timestamp": self.headers.get("timestamp"),
            "signature": self.headers.get("signature"),
        })

        proxies = build_proxies(self.proxy)

        # 1）查询 6 折券活动信息
        info_url = (
            "https://mcs-mimp-web.sf-express.com/"
            "mcs-mimp/commonPost/~memberNonactivity~weeklySendApiService~seckillPacketInfo"
        )
        try:
            info_resp = self.s.post(info_url, headers=headers, json={}, proxies=proxies, timeout=10)
            info_data = info_resp.json()
        except Exception as e:
            print(f"❌ 查询6折券活动信息异常：{e}")
            return f"❌ 查询6折券活动信息异常：{e}"

        if not info_data.get("success"):
            err = info_data.get("errorMessage", "未知错误")
            print(f"❌ 查询6折券活动信息失败：{err}")
            return f"❌ 查询6折券活动信息失败：{err}"

        obj = info_data.get("obj") or {}
        gift_bag_code = obj.get("giftBagCode")
        gift_bag_name = obj.get("giftBagName", "6折寄件券")
        seckill_start = obj.get("seckillActStartTm", "12:00:00")

        if not gift_bag_code:
            print("❌ 未获取到6折券 giftBagCode")
            return "❌ 抢6折券失败：未获取到活动礼包编码"

        print(f"🎯 6折券活动信息：{gift_bag_name}，开始时间：{seckill_start}，giftBagCode：{gift_bag_code}")

        # 2）真正抢券
        # ⚠️ 注意：下面这个接口路径和参数是根据 freePacket 模式推测的，
        #    实际请以你自己抓到的 receive 请求为准进行调整。
        seckill_url = (
            "https://mcs-mimp-web.sf-express.com/"
            "mcs-mimp/commonPost/~memberNonactivity~weeklySendApiService~receiveSeckillPacket"
        )
        payload = {"giftBagCode": gift_bag_code}

        try:
            send_time = time.time()
            print(f"📤 发送6折券抢券请求时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(send_time))}")
            resp = self.s.post(seckill_url, headers=headers, json=payload, proxies=proxies, timeout=10)
            data = resp.json()
        except Exception as e:
            print(f"❌ 抢6折券请求异常：{e}")
            return f"❌ 抢6折券请求异常：{e}"

        print(f"【6折券请求 Cookie】>>>>\n{cookie_str}\n<<<<")
        print(f"【6折券请求 Payload】>>>>\n{json.dumps(payload, ensure_ascii=False)}\n<<<<")

        if data.get("success"):
            print(f"🎉 抢6折券成功：{gift_bag_name}")
            self.cleanup_account_data()
            return f"🎉 抢6折券成功：{gift_bag_name}"
        else:
            err = data.get("errorMessage", "未知错误")
            print(f"❌ 抢6折券失败：{err}")
            return f"❌ 抢6折券失败：{err}"

    def exchange_seckill(self) -> str:
        """积分秒杀抢兑。"""
        if not self.session_id:
            print("❌ 无法获取sessionId，兑换失败")
            return "❌ 兑换失败：无法获取sessionId"
        if not self.goods_info:
            print("❌ 未设置商品信息，兑换失败")
            return "❌ 兑换失败：未设置商品信息"

        results = []
        for goods_entry in self.goods_info:
            parts = goods_entry.split('@')
            if len(parts) < 5 or parts[0] != 'seckill':
                print(f'❌ 商品信息格式错误: {goods_entry}')
                results.append("兑换失败: 商品信息格式错误")
                continue
            if len(parts) == 5:
                _, flash_sale_goods_id, ac_id, periods, goods_name = parts
                goods_type = "SFMD"
            else:
                _, flash_sale_goods_id, ac_id, periods, goods_name, goods_type = parts

            print(f'🎁 开始秒杀商品: {goods_name} (类型:{goods_type})')

            address = None
            if goods_type in ['SFIM', 'SFMD']:
                address_str = middleware.bucketGet('Joh_sf_dz', self.phone_masked)
                if not address_str:
                    print('❌ 未获取到收货地址信息')
                    results.append(f"兑换{goods_name}失败: 未获取到收货地址信息")
                    continue
                address = parse_address(address_str)
                if not address:
                    print('❌ 地址信息格式错误')
                    results.append(f"兑换{goods_name}失败: 地址信息格式错误")
                    continue

            self._apply_sign()
            cookie_str = "; ".join([f"{k}={v}" for k, v in self.cookies.items()])
            seckill_headers = self.headers.copy()
            seckill_headers.update({
                "Cookie": cookie_str,
                "Content-Type": "application/json;charset=utf-8",
                "channel": "miaosha0822",
                "Referer": f"https://mcs-mimp-web.sf-express.com/secondKillDetail?id={ac_id}",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "zh-CN,zh-Hans;q=0.9",
            })
            seckill_payload = {
                "acId": str(ac_id),
                "channel": "MINI_PROGRAM",
                "periods": str(periods),
                "seckillGoodsId": int(flash_sale_goods_id),
                "secondChannel": "miaosha0822",
            }
            if goods_type in ["SFIM", "SFMD"] and address:
                seckill_payload.update({
                    "provinceId": FIX_PID if FIX_PID else "",
                    "provinceName": address["province"],
                    "cityId": FIX_CID if FIX_CID else "",
                    "cityName": address["city"],
                    "countyId": FIX_COID if FIX_COID else "",
                    "countyName": address["distinct"],
                    "receiverName": address["receiveContact"],
                    "receiverMobile": address["receivePhone"],
                    "receiverAddress": address["receiveAddress"],
                })

            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointsSeckillService~receiveGoodN"
            try:
                print(f"📤 发送秒杀请求时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
                resp = self.s.post(url, headers=seckill_headers, json=seckill_payload, proxies=build_proxies(self.proxy))
                data = resp.json()
                print(f"【秒杀请求 Cookie】>>>>\n{cookie_str}\n<<<<")
                print(f"【秒杀请求 Payload】>>>>\n{json.dumps(seckill_payload, ensure_ascii=False, indent=4)}\n<<<<")
                if data.get('success'):
                    order_no = data.get("obj", {}).get("orderNo", "")
                    print(f'🎉 秒杀成功: {goods_name} 订单号:{order_no}')
                    results.append(f"秒杀{goods_name}成功: 订单号:{order_no}")
                    self.cleanup_account_data()  # 兑换成功后清理当前账号数据
                else:
                    err = data.get("errorMessage", "未知错误")
                    print(f'❌ {goods_name} 秒杀失败: {err}')
                    results.append(f"秒杀{goods_name}失败: {err}")
            except Exception as e:
                print(f'❌ {goods_name} 秒杀请求异常: {str(e)}')
                results.append(f"秒杀{goods_name}失败: {str(e)}")
        return "\n".join(results)


class IntegralQuery:
    def __init__(self, sender, account_key: str):
        self.sender = sender
        self.account_key = account_key
        self.session = requests.session()
        self.session.verify = False
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36 NetType/WIFI MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090551) XWEB/6945 Flue',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'zh-CN,zh',
            'platform': 'MINI_PROGRAM',
        }
        self.user_id = None
        self.phone = None
        self.mobile = None

    @staticmethod
    def get_deviceId(characters='abcdef0123456789') -> str:
        result = ''
        for ch in 'xxxxxxxx-xxxx-xxxx':
            result += random.choice(characters) if ch in 'xX' else ch
        return result

    def _apply_sign(self) -> None:
        timestamp = str(int(round(time.time() * 1000)))
        data = f'token={SIGN_TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        self.headers.update({'timestamp': timestamp, 'signature': signature})

    def login(self) -> bool:
        try:
            if is_phone_account(self.account_key):
                sf_url = (
                    middleware.bucketGet('Yzyxmm_sf_account', self.account_key)
                    or middleware.bucketGet('dd_sf_token', self.account_key)
                    or middleware.bucketGet('yuhua_sf_token', self.account_key)
                )
            else:
                sf_url = middleware.bucketGet('chuan_sf_accountId', self.account_key)
            if not sf_url:
                print(f"❌ 未获取到账号 {self.account_key} 的链接")
                return False
            self.session.get(sf_url, headers=self.headers)
            cookies = self.session.cookies.get_dict()
            self.user_id = cookies.get('_login_user_id_', 'None')
            self.phone = cookies.get('_login_mobile_', 'None')
            if self.phone == 'None' or self.user_id == 'None':
                print('❌ 获取用户信息失败')
                return False
            self.mobile = self.phone[:3] + "*" * 4 + self.phone[7:]
            print(f'👤 用户:【{self.mobile}】登陆成功')
            return True
        except Exception as e:
            print(f'❌ 登录异常: {str(e)}')
            return False

    def query_integral(self) -> Optional[int]:
        if not self.login():
            return None
        self._apply_sign()
        try:
            json_data = {'channelType': '1', 'deviceId': self.get_deviceId()}
            url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberNonactivity~integralTaskStrategyService~queryPointTaskAndSignFromES"
            resp = self.session.post(url, headers=self.headers, json=json_data)
            res = resp.json()
            if res.get('success') and res.get('obj') and 'totalPoint' in res.get('obj', {}):
                totalPoint = res['obj']['totalPoint']
                print(f'💰 当前积分：【{totalPoint}】')
                return totalPoint
            print(f"❌ 查询积分失败！原因：{res.get('errorMessage', '未知错误')}")
            return None
        except Exception as e:
            print(f'❌ 查询积分异常: {str(e)}')
            return None


class GoodsQuery:
    def __init__(self, sender, encoded_link: str):
        self.sender = sender
        self.encoded_link = encoded_link
        self.session = requests.session()
        self.session.verify = False
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'sysCode': SYS_CODE,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.50(0x1800323d) NetType/WIFI Language/zh_CN miniProgram/wxd4185d00bf7e08ac',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': 'https://mcs-mimp-web.sf-express.com',
            'Referer': 'https://mcs-mimp-web.sf-express.com/up-member/newPoints',
        }
        self.cookies: Dict[str, str] = {}

    def _apply_sign(self) -> None:
        timestamp = str(int(time.time() * 1000))
        data = f'token={SIGN_TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        self.headers.update({'timestamp': timestamp, 'signature': signature})

    def _get_cookie(self) -> bool:
        response = None
        try:
            response = self.session.get(self.encoded_link, headers=self.headers)
            self.cookies = self.session.cookies.get_dict()
            session_id = (
                self.cookies.get('sessionId')
                or self.cookies.get('SESSIONID')
                or self.cookies.get('sessionid')
            )
            if not session_id:
                print(f'获取Cookie失败 状态码:{getattr(response, "status_code", "-")} cookies:{self.cookies}')
            return True if session_id else False
        except Exception as e:
            print(f'获取Cookie失败: {str(e)} 状态码:{getattr(response, "status_code", "-")}')
            return False

    def query_goods_list(self) -> List[Dict]:
        if not self._get_cookie():
            return []
        self._apply_sign()
        all_goods: List[Dict] = []
        page_no, page_size = 1, 20
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointMallService~goodsList"
        while True:
            payload = {
                "pageSize": page_size,
                "pageNo": page_no,
                "categoryCode": "brandHall",
                "sortedBy": "default",
                "pointRange": 0,
            }
            try:
                r = self.session.post(url, headers=self.headers, json=payload, cookies=self.cookies, timeout=10)
                if r.status_code != 200:
                    break
                data = r.json()
                if not data.get('success'):
                    break
                goods = data['obj'].get('pointGoodsList', [])
                if not goods:
                    break
                all_goods.extend(goods)
                page_no += 1
            except Exception as e:
                print(f'[query_goods_list] 拉取第{page_no}页失败：{e}')
                break
        limited_goods = [g for g in all_goods if g.get('storeDaily', 0) > 0 and g.get('storeDailyReset', 0) > 0]
        return limited_goods


class SeckillQuery:
    def __init__(self, sender, encoded_link: str):
        self.sender = sender
        self.encoded_link = encoded_link
        self.session = requests.session()
        self.session.verify = False
        self.headers = {
            'Host': 'mcs-mimp-web.sf-express.com',
            'sysCode': SYS_CODE,
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.61(0x18003d39) NetType/4G Language/zh_CN miniProgram/wxd4185d00bf7e08ac',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'Origin': 'https://mcs-mimp-web.sf-express.com',
            'Referer': 'https://mcs-mimp-web.sf-express.com/home',
            'platform': 'MINI_PROGRAM',
        }
        self.cookies: Dict[str, str] = {}
        self.ac_info = None
        self.all_sessions: List[Dict] = []

    def _apply_sign(self) -> None:
        timestamp = str(int(time.time() * 1000))
        data = f'token={SIGN_TOKEN}&timestamp={timestamp}&sysCode={SYS_CODE}'
        signature = hashlib.md5(data.encode()).hexdigest()
        self.headers.update({'timestamp': timestamp, 'signature': signature})

    def _get_cookie(self) -> bool:
        try:
            resp = self.session.get(self.encoded_link, headers=self.headers)
            self.cookies = self.session.cookies.get_dict()
            session_id = (
                self.cookies.get('sessionId')
                or self.cookies.get('SESSIONID')
                or self.cookies.get('sessionid')
            )
            if not session_id:
                print(f'获取Cookie失败 状态码:{getattr(resp, "status_code", "-")}')
            return True if session_id else False
        except Exception as e:
            print(f'获取Cookie失败: {str(e)}')
            return False

    def query_seckill_info(self) -> Optional[Dict]:
        if not self._get_cookie():
            return None
        self._apply_sign()
        url = "https://mcs-mimp-web.sf-express.com/mcs-mimp/commonPost/~memberGoods~pointFlashSale~getFlashSaleAcInfo"
        self.all_sessions = []
        for session_id in [6131, 6132, 6133]:
            payload = {"sessionId": session_id}
            try:
                r = self.session.post(url, headers=self.headers, json=payload, cookies=self.cookies, timeout=10)
                if r.status_code != 200:
                    continue
                data = r.json()
                if data.get('success') and data.get('obj'):
                    session_info = data['obj']
                    self.all_sessions.append(session_info)
                    if not self.ac_info:
                        self.ac_info = session_info
            except Exception as e:
                print(f'查询秒杀活动信息失败(sessionId={session_id}): {str(e)}')
                continue
        return self.ac_info if self.all_sessions else None

    def get_seckill_goods_list(self) -> List[Dict]:
        if not self.ac_info:
            if not self.query_seckill_info():
                return []
        all_goods: List[Dict] = []
        seen: set = set()
        sessions = self.all_sessions if self.all_sessions else ([self.ac_info] if self.ac_info else [])
        for session_info in sessions:
            for g in session_info.get('currFlashSaleGoodsList', []):
                gid = g.get('flashSaleGoodsId')
                if gid in seen:
                    continue
                seen.add(gid)
                if g.get('goodsType') in ('SFMD',):
                    all_goods.append({
                        'flashSaleGoodsId': gid,
                        'goodsName': g.get('goodsName'),
                        'flashSalePoint': g.get('flashSalePoint'),
                        'flashSaleCurrentStock': g.get('flashSaleCurrentStock'),
                        'acId': session_info.get('id'),
                        'sessionId': g.get('sessionId'),
                        'goodsType': g.get('goodsType'),
                    })
        if not all_goods:
            print('❌ 未查询到秒杀商品')
        return all_goods

# =========================
# 推送
# =========================

def push_to_admin(summary: str) -> None:
    try:
        admin_qq = middleware.bucketGet('Joh_sf_config', 'QQ')
        admin_wx = middleware.bucketGet('Joh_sf_config', 'WX')
        admin_tg = middleware.bucketGet('Joh_sf_config', 'TG')
        if not any([admin_qq, admin_wx, admin_tg]):
            print("❌ 未配置管理员信息，无法推送")
            return
        summary = PHONE_RE.sub(lambda m: mask_phone_number(m.group()), summary)
        admin_msg = (
            "======SF抢兑通知======\n"
            f"[执行结果]：\n{summary}\n"
            f"[执行时间]：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        if admin_qq:
            middleware.push('qq', '', admin_qq, '', admin_msg)
        if admin_wx:
            middleware.push('wx', '', admin_wx, '', admin_msg)
        if admin_tg:
            middleware.push('tg', '', admin_tg, '', admin_msg)
    except Exception as e:
        print(f"推送通知处理失败: {str(e)}")


def find_user_id_by_account(bucket_name: str, account: str) -> Optional[str]:
    try:
        all_keys = middleware.bucketAllKeys(bucket_name)
        if not all_keys:
            return None
        for key in all_keys:
            value = middleware.bucketGet(bucket_name, key)
            if account in str(value):
                return key
        return None
    except Exception as e:
        print(f"从 {bucket_name} 查询出错: {str(e)}")
        return None


def push_to_user(phone_masked: str, result: str) -> None:
    try:
        push_content = (
            f"======SF抢兑通知======\n{result}\n[执行时间]：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
        )
        yzyxmm_user_id = find_user_id_by_account('Yzyxmm_sf_bind', phone_masked)
        dd_user_id = find_user_id_by_account('dd_sf_user', phone_masked)
        yuhua_user_id = find_user_id_by_account('yuhua_sf_user', phone_masked)
        all_user_ids = [uid for uid in [yzyxmm_user_id, dd_user_id, yuhua_user_id] if uid]
        for uid in all_user_ids:
            middleware.push('wx', '', uid, '', push_content)
            middleware.push('qq', '', uid, '', push_content)
            middleware.push('tg', '', uid, '', push_content)
        account_key = None
        for k in middleware.bucketAllKeys('chuan_sf_phone'):
            if middleware.bucketGet('chuan_sf_phone', k) == phone_masked:
                account_key = k
                break
        if account_key:
            wx_user_id = middleware.bucketGet('chuan_sfWX', account_key)
            qq_user_id = middleware.bucketGet('chuan_sfQQ', account_key)
            tg_user_id = middleware.bucketGet('chuan_sfTG', account_key)
            if wx_user_id:
                middleware.push('wx', '', wx_user_id, '', push_content)
            if qq_user_id:
                middleware.push('qq', '', qq_user_id, '', push_content)
            if tg_user_id:
                middleware.push('tg', '', tg_user_id, '', push_content)
        else:
            print(f"❌ 未找到账号 {phone_masked} 对应的 chuan_sf 账号")
    except Exception as e:
        print(f"推送通知处理失败: {str(e)}")

# =========================
# 主流程
# =========================

def callback_choose_accounts(sender, account_keys: List[str]) -> Optional[List[str]]:
    accounts: List[Tuple[str, str]] = []
    seen = set()
    for key in account_keys:
        phone = key if is_phone_account(key) else get_account_phone(key)
        if phone and phone not in seen:
            accounts.append((key, mask_phone_number(phone)))
            seen.add(phone)
    accounts.sort(key=lambda x: x[1])
    if not accounts:
        return None
    msg = ["请选择要抢兑的账号，多选用逗号隔开：", "【0】全部"]
    for i, (_, mphone) in enumerate(accounts, 1):
        msg.append(f"【{i}】{mphone}")
    sender.reply("\n".join(msg))

    selected_input = sender.listen(120000)
    if not selected_input:
        sender.reply("❌ 操作超时，已取消")
        return None
    if selected_input.lower().strip() == 'q':
        sender.reply("已取消操作")
        return None

    selected_keys: List[str] = []
    selected_input = selected_input.replace('，', ',').strip()
    if selected_input == '0':
        selected_keys = [k for k, _ in accounts]
    else:
        try:
            idxs = [int(x) for x in selected_input.split(',')]
            for idx in idxs:
                if 1 <= idx <= len(accounts):
                    selected_keys.append(accounts[idx - 1][0])
        except Exception:
            sender.reply("❌ 输入格式错误，请使用数字索引")
            return None

    valid: List[str] = []
    for key in selected_keys:
        if check_authorization(key):
            valid.append(key)
        else:
            phone = key if is_phone_account(key) else (get_account_phone(key) or key)
            sender.reply(f"❌ 账号 {mask_phone_number(phone)} 已过期或未授权，请先发\"顺丰代挂\"授权")
    if not valid:
        sender.reply("❌ 所选账号均无法使用，请先完成授权")
        return None
    return valid


def main(sender) -> None:
    try:
        message = sender.getMessage().strip()
        exit_flag = False

        if message == "顺丰抢兑":
            user_id = sender.getUserID()
            im_type = sender.getImtype()

            buckets = [
                {'name': 'dd_sf_user', 'key': user_id},
                {'name': 'yuhua_sf_user', 'key': user_id},
                {'name': 'Yzyxmm_sf_bind', 'key': user_id},
            ]
            account_keys: List[str] = []
            for bk in buckets:
                acc_list = middleware.bucketGet(bucket=bk['name'], key=bk['key'])
                if acc_list:
                    account_keys.extend(safe_eval_to_list(acc_list))

            if im_type == 'wx':
                ch_bucket = 'chuan_sfWX'
            elif im_type == 'qq':
                ch_bucket = 'chuan_sfQQ'
            elif im_type == 'tg':
                ch_bucket = 'chuan_sfTG'
            else:
                ch_bucket = None
            if ch_bucket:
                account_keys.extend(middleware.bucketKeys(bucket=ch_bucket, value=user_id))

            account_keys = sorted(set(account_keys))
            if not account_keys:
                return sender.reply("❌ 未查询到账号，请发顺丰登录")

            selected_keys = callback_choose_accounts(sender, account_keys)
            if not selected_keys:
                return
            
            # 动态构建选项列表（类似代码2的登录菜单）
            options = ["请选择要抢的项目："]
            idx = 1
            option_map = {}  # 映射显示序号到功能编号
            
            # 免单券（1）
            if FREE_COUPON_ENABLED:
                options.append(f"【{idx}】顺丰会员日免单券")
                option_map[str(idx)] = "1"
                idx += 1
            
            # 商城实物（2）
            if GOODS_ENABLED:
                options.append(f"【{idx}】顺丰商城实物")
                option_map[str(idx)] = "2"
                idx += 1
            
            # 积分秒杀（3）
            if SECKILL_ENABLED:
                options.append(f"【{idx}】顺丰积分秒杀")
                option_map[str(idx)] = "3"
                idx += 1
            
            # 6折券（4）
            if WEEKLY_60_ENABLED:
                options.append(f"【{idx}】超寄星期三6折券")
                option_map[str(idx)] = "4"
                idx += 1
            
            # 检查是否全部关闭
            if len(options) == 1:
                return sender.reply("❌ 所有抢兑功能已被管理员关闭，请联系管理员开启")
            
            options.append('(发送 "q" 退出)')
            
            sender.reply("\n".join(options))
            
            selected_input = sender.listen(120000)
            if not selected_input:
                sender.reply("❌ 操作超时，已取消")
                return
            if selected_input.lower().strip() == 'q':
                sender.reply("已取消操作")
                return
            
            # 转换用户输入到功能编号
            selected_num = selected_input.strip()
            biz = option_map.get(selected_num, selected_num)

            if biz == '1':
                if not (33 <= _day <= 33):
                    sender.reply("❌ 会员日免单券抢兑只能在每月26号至28号之间提交，当前时间不可抢兑。")
                    return
                round_time = "ALL"
                first_round_time = None
                for key in selected_keys:
                    link = get_account_link(key)
                    if not link:
                        phone = key if is_phone_account(key) else get_account_phone(key)
                        sender.reply(f"❌ 未获取到账号 {mask_phone_number(phone)} 的链接")
                        continue
                    encoded_link = encode_link(link)
                    phone_masked = key if is_phone_account(key) else (get_account_phone(key) or key)
                    if not check_authorization(key):
                        sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 未授权或已过期")
                        continue
                    if not first_round_time:
                        first_round_time = round_time
                    middleware.bucketSet('Joh_sf_Items', phone_masked, f"free_coupon@{first_round_time}")
                    store_encoded_link(sender, phone_masked, encoded_link)
                    sender.reply(f"✅ 账号 {mask_phone_number(phone_masked)} 已上传待抢免单列表，场次时间：全部{first_round_time}")

            elif biz == '2':
                for key in selected_keys:
                    if exit_flag:
                        break
                    link = get_account_link(key)
                    if not link:
                        phone = key if is_phone_account(key) else get_account_phone(key)
                        sender.reply(f"❌ 未获取到账号 {mask_phone_number(phone)} 的链接")
                        continue
                    encoded_link = encode_link(link)
                    phone_masked = key if is_phone_account(key) else (get_account_phone(key) or key)
                    if not check_authorization(key):
                        sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 未授权或已过期")
                        continue
                    goods_query = GoodsQuery(sender, link)
                    goods_list = goods_query.query_goods_list()
                    if not goods_list:
                        sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 未查询到可抢兑的商品")
                        continue

                    lines = [f"请为账号 {mask_phone_number(phone_masked)} 选择要抢兑的商品，多选用逗号隔开：", "【0】全部"]
                    for i, g in enumerate(goods_list, 1):
                        lines.append(f"【{i}】{g['goodsName']} (需{g['pointPrice']}积分)")
                    sender.reply("\n".join(lines))
                    sender.reply("⚠️ 这个是原价积分兑换，半价兑换请选秒杀")
                    sel = sender.listen(120000)
                    if not sel:
                        sender.reply("❌ 操作超时，已取消")
                        break
                    if sel.lower().strip() == 'q':
                        sender.reply("已取消操作")
                        exit_flag = True
                        break
                    sel = sel.replace('，', ',').strip()
                    try:
                        if sel == '0':
                            idxs = list(range(len(goods_list)))
                        else:
                            idxs = [int(x) - 1 for x in sel.split(',') if 1 <= int(x) <= len(goods_list)]
                    except Exception:
                        sender.reply("❌ 输入格式错误，请使用数字索引")
                        continue
                    if not idxs:
                        sender.reply("❌ 未选择有效的商品")
                        continue
                    selected_goods = [goods_list[i] for i in idxs]
                    integral = IntegralQuery(sender, key).query_integral()
                    if integral is None:
                        sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 查询积分失败")
                        continue
                    lack = [g['goodsName'] for g in selected_goods if int(integral) < g['pointPrice']]
                    if lack:
                        sender.reply(f"❌ 积分不足，无法兑换以下商品：{', '.join(lack)}")
                        continue
                    address = get_user_address(sender, phone_masked)
                    modify_address = False
                    if address:
                        sender.reply(
                            f"当前账号 {mask_phone_number(phone_masked)} 的收货地址为：\n{address}\n是否要修改？\n回复y修改，回复n保持"
                        )
                        mi = sender.listen(120000)
                        if not mi:
                            sender.reply("❌ 操作超时，已取消")
                            break
                        low = mi.lower().strip()
                        if low == 'n':
                            sender.reply(f"✅ 账号 {mask_phone_number(phone_masked)} 的收货地址保持原有设置")
                        elif low == 'y':
                            modify_address = True
                        elif low == 'q':
                            sender.reply("已取消操作")
                            exit_flag = True
                            break
                        else:
                            sender.reply("❌ 输入无效，已取消")
                            break
                    else:
                        modify_address = True
                    if modify_address:
                        sender.reply(
                            "请输入账号 {m} 的收货地址\n⚠️请按照此顺序填写：1省,2市,3县或市区镇,4姓名,5详细地址,6手机号,7完整地址\n"
                            "信息请用逗号隔开\n示例：广东省,广州市,荔湾区,刘德华,芳和小区66栋,13566666666,广东省广州市荔湾区芳和小区66栋\n"
                            "⚠️一共7个信息，6个逗号（顺序或信息错误将影响发货！）".format(m=mask_phone_number(phone_masked))
                        )
                        addr_in = sender.listen(300000)
                        if not addr_in:
                            sender.reply("❌ 操作超时，已取消")
                            break
                        if addr_in.lower().strip() == 'q':
                            sender.reply("已取消操作")
                            exit_flag = True
                            break
                        parsed = parse_address(addr_in)
                        if parsed:
                            set_user_address(sender, phone_masked, addr_in)
                            sender.reply(f"✅ 账号 {mask_phone_number(phone_masked)} 的收货地址已{'更新' if address else '设置'}")
                        else:
                            sender.reply("❌ 地址格式错误或缺少信息，请严格按照上述顺序格式提交")
                            break
                    goods_entries = [f"{g['goodsName']}@{g['goodsNo']}" for g in selected_goods]
                    middleware.bucketSet('Joh_sf_Items', phone_masked, "#".join(goods_entries))
                    store_encoded_link(sender, phone_masked, encoded_link)
                    sender.reply(f"✅ 账号 {mask_phone_number(phone_masked)} 已上传待抢列表")

            elif biz == '3':
                for key in selected_keys:
                    if exit_flag:
                        break
                    link = get_account_link(key)
                    if not link:
                        phone = key if is_phone_account(key) else get_account_phone(key)
                        sender.reply(f"❌ 未获取到账号 {mask_phone_number(phone)} 的链接")
                        continue
                    encoded_link = encode_link(link)
                    phone_masked = key if is_phone_account(key) else (get_account_phone(key) or key)
                    if not check_authorization(key):
                        sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 未授权或已过期")
                        continue
                    seckill_query = SeckillQuery(sender, link)
                    seckill_goods_list = seckill_query.get_seckill_goods_list()
                    if not seckill_goods_list:
                        sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 未查询到可秒杀的商品")
                        continue
                    # === 计算每个商品ID的已选数量（移到前面，供菜单显示使用）===
                    _limit = 8
                    _goods_counts = {}
                    try:
                        _keys = middleware.bucketAllKeys('Joh_sf_Items') or []
                        for _k in _keys:
                            _val = middleware.bucketGet('Joh_sf_Items', _k) or ''
                            for _s in _val.split('#'):
                                if not _s or not _s.startswith('seckill@'):
                                    continue
                                _p = _s.split('@', 5)  # seckill@gid@ac@session@name@type
                                if len(_p) >= 2:
                                    try:
                                        _gid = int(_p[1])
                                    except Exception:
                                        continue
                                    _goods_counts[_gid] = _goods_counts.get(_gid, 0) + 1
                    except Exception:
                        pass

                    lines = [f"请为账号 {mask_phone_number(phone_masked)} 选择要秒杀的商品，多选用逗号隔开：", "【0】全部"]
                    for i, g in enumerate(seckill_goods_list, 1):
                        # 计算剩余额度
                        remaining_quota = _limit - _goods_counts.get(int(g['flashSaleGoodsId']), 0)
                        lines.append(f"【{i}】{g['goodsName']} (需{g['flashSalePoint']}积分）今日剩余车位：{remaining_quota}")
                    sender.reply("\n".join(lines))
                    sel = sender.listen(120000)
                    if not sel:
                        sender.reply("❌ 操作超时，已取消")
                        break
                    if sel.lower().strip() == 'q':
                        sender.reply("已取消操作")
                        exit_flag = True
                        break
                    sel = sel.replace('，', ',').strip()
                    try:
                        if sel == '0':
                            idxs = list(range(len(seckill_goods_list)))
                        else:
                            idxs = [int(x) - 1 for x in sel.split(',') if 1 <= int(x) <= len(seckill_goods_list)]
                    except Exception:
                        sender.reply("❌ 输入格式错误，请使用数字索引")
                        continue
                    if not idxs:
                        sender.reply("❌ 未选择有效的商品")
                        continue
                    selected_seckill_goods = [seckill_goods_list[i] for i in idxs]

                    _allowed, _blocked_names = [], []
                    for g in selected_seckill_goods:
                        try:
                            _gid = int(g['flashSaleGoodsId'])
                        except Exception:
                            _allowed.append(g)
                            continue
                        if _goods_counts.get(_gid, 0) >= _limit:
                            _blocked_names.append(g.get('goodsName') or f"商品{_gid}")
                            continue
                        _goods_counts[_gid] = _goods_counts.get(_gid, 0) + 1
                        _allowed.append(g)
                    selected_seckill_goods = _allowed
                    if not selected_seckill_goods:
                        sender.reply("❌ 所选商品待抢额度已满，建议在当天的抢兑结束后再试（对应实物抢兑的时间）")
                        continue
                    if _blocked_names:
                        sender.reply("⚠️ 以下商品名额已满，已为你剔除：" + "、".join(_blocked_names))

                    integral = IntegralQuery(sender, key).query_integral()
                    if integral is None:
                        sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 查询积分失败")
                        continue
                    lack = [g['goodsName'] for g in selected_seckill_goods if int(integral) < g['flashSalePoint']]
                    if lack:
                        sender.reply(f"❌ 积分不足，无法秒杀以下商品：{', '.join(lack)}")
                        continue
                    address = get_user_address(sender, phone_masked)
                    modify_address = False
                    if address:
                        sender.reply(
                            f"当前账号 {mask_phone_number(phone_masked)} 的收货地址为：\n{address}\n是否要修改？\n回复y修改，回复n保持"
                        )
                        mi = sender.listen(120000)
                        if not mi:
                            sender.reply("❌ 操作超时，已取消")
                            break
                        low = mi.lower().strip()
                        if low == 'n':
                            sender.reply(f"✅ 账号 {mask_phone_number(phone_masked)} 的收货地址保持原有设置")
                        elif low == 'y':
                            modify_address = True
                        elif low == 'q':
                            sender.reply("已取消操作")
                            exit_flag = True
                            break
                        else:
                            sender.reply("❌ 输入无效，已取消")
                            break
                    else:
                        modify_address = True
                    if modify_address:
                        sender.reply(
                            "请输入账号 {m} 的收货地址\n⚠️请按照此顺序填写：1省,2市,3县或市区镇,4姓名,5详细地址,6手机号,7完整地址\n"
                            "信息请用逗号隔开\n示例：广东省,广州市,荔湾区,刘德华,芳和小区66栋,13566666666,广东省广州市荔湾区芳和小区66栋\n"
                            "⚠️一共7个信息，6个逗号（顺序或信息错误将影响发货！）".format(m=mask_phone_number(phone_masked))
                        )
                        addr_in = sender.listen(300000)
                        if not addr_in:
                            sender.reply("❌ 操作超时，已取消")
                            break
                        if addr_in.lower().strip() == 'q':
                            sender.reply("已取消操作")
                            exit_flag = True
                            break
                        parsed = parse_address(addr_in)
                        if parsed:
                            set_user_address(sender, phone_masked, addr_in)
                            sender.reply(f"✅ 账号 {mask_phone_number(phone_masked)} 的收货地址已{'更新' if address else '设置'}")
                        else:
                            sender.reply("❌ 地址格式错误或缺少信息，请严格按照上述顺序格式提交")
                            break

                    entries = [
                        f"seckill@{g['flashSaleGoodsId']}@{g['acId']}@{g['sessionId']}@{g['goodsName']}@{g.get('goodsType', 'SFIM')}"
                        for g in selected_seckill_goods
                    ]
                    middleware.bucketSet('Joh_sf_Items', phone_masked, "#".join(entries))
                    store_encoded_link(sender, phone_masked, encoded_link)
                    sender.reply(f"✅ 账号 {mask_phone_number(phone_masked)} 已上传待秒杀列表")
            
            elif biz == '4':
                            # 配置超寄星期三 6 折寄件券（增加会员等级校验，等级 < 5 不允许提交）
                            proxy = get_proxy()
                            for key in selected_keys:
                                link = get_account_link(key)
                                if not link:
                                    phone = key if is_phone_account(key) else get_account_phone(key)
                                    sender.reply(f"❌ 未获取到账号 {mask_phone_number(phone)} 的链接")
                                    continue

                                phone_masked = key if is_phone_account(key) else (get_account_phone(key) or key)
                                if not check_authorization(key):
                                    sender.reply(f"❌ 账号 {mask_phone_number(phone_masked)} 未授权或已过期")
                                    continue

                            # 等级判断：仅会员等级 >= 5 的账号才允许加入抢券队列
                                level_info = fetch_member_level(link, proxy)
                                if level_info is None:
                                    sender.reply(f"❌ 账号 {phone_masked} 查询会员等级失败，请重试")
                                    continue
                                time.sleep(1)
                            # 解包获取数字和名称
                                level_number, level_name = level_info
                                if level_number < 5:
                                # 显示时使用等级名称
                                    sender.reply(f"❌ 账号 {phone_masked} \n当前会员等级为：{level_name}（等级{level_number}）\n未达到活动要求（需≥5，黄金会员及以上）")
                                    continue

                                encoded_link = encode_link(link)

                                # 6 折券无需地址，只需要账号 + 链接，运行时按时间抢券
                                middleware.bucketSet('Joh_sf_Items', phone_masked, WEEKLY_60_PREFIX)
                                store_encoded_link(sender, phone_masked, encoded_link)

                                sender.reply(
                                    f"✅ 账号 {phone_masked} \n已加入【超寄星期三 6折券】抢券队列\n（当前等级：{level_name}）"
                                )

            else:
                sender.reply("❌ 无效的选项，请重新发送顺丰抢兑")

        elif message == "顺丰取消抢兑":
            # 获取用户所有账号
            user_id = sender.getUserID()
            account_keys = get_user_account_keys(sender)
            if not account_keys:
                return sender.reply("❌ 未查询到您的账号信息")
            
            # 筛选有抢兑记录的账号
            queued_accounts = []
            for key in account_keys:
                phone_masked = key if is_phone_account(key) else get_account_phone(key)
                if phone_masked and middleware.bucketGet('Joh_sf_Items', phone_masked):
                    queued_accounts.append((key, phone_masked))
            
            if not queued_accounts:
                return sender.reply("暂无账号在待抢列表")
            
            # 显示选择列表
            msg = ["请选择要取消抢兑的账号，多选用逗号隔开：", "【0】全部"]
            for i, (_, phone_masked) in enumerate(queued_accounts, 1):
                msg.append(f"【{i}】{phone_masked}")
            sender.reply("\n".join(msg))
            
            # 等待用户选择
            selected_input = sender.listen(120000)
            if not selected_input:
                return sender.reply("❌ 操作超时，已取消")
            if selected_input.lower().strip() == 'q':
                return sender.reply("已取消操作")
            
            # 解析选择
            selected_input = selected_input.replace('，', ',').strip()
            if selected_input == '0':
                selected_keys = [k for k, _ in queued_accounts]
            else:
                try:
                    idxs = [int(x) for x in selected_input.split(',') if x.strip()]
                    selected_keys = [queued_accounts[i-1][0] for i in idxs if 1 <= i <= len(queued_accounts)]
                except Exception:
                    return sender.reply("❌ 输入格式错误，请使用数字索引")
            
            if not selected_keys:
                return sender.reply("❌ 未选择任何账号")
            
            # 执行删除
            success_count = 0
            for key in selected_keys:
                phone_masked = key if is_phone_account(key) else get_account_phone(key)
                if not phone_masked:
                    continue
                try:
                    middleware.bucketDel('Joh_sf_Items', phone_masked)
                    middleware.bucketDel('Joh_sf', phone_masked)
                    success_count += 1
                except Exception as e:
                    print(f"❌ 删除账号 {phone_masked} 失败: {str(e)}")
            
            sender.reply(f"✅ 已成功取消 {success_count} 个账号的抢兑任务")

        elif message == "运行抢兑":
            if not sender.isAdmin():
                sender.reply("⚠️ 该指令仅限管理员使用")
                return
            dinshi_value = middleware.bucketGet('Joh_sf_config', 'dinshi')
            if not dinshi_value:
                sender.reply("❌ 未设置抢兑时间，请先设置抢兑时间")
                return
            try:
                # 解析定时时间并分组（<=10分钟为同组）
                time_points = [s.strip() for s in dinshi_value.split(',') if s.strip()]
                now_ts = time.time()
                cur = time.localtime()
                groups: List[List[float]] = []
                tmp: List[float] = []
                for tstr in time_points:
                    try:
                        ht = time.strptime(tstr, '%H:%M:%S')
                        target = time.mktime((cur.tm_year, cur.tm_mon, cur.tm_mday, ht.tm_hour, ht.tm_min, ht.tm_sec, 0, 0, 0))
                        if target < now_ts:
                            print(f"⏭️ 时间 {tstr} 已过，跳过")
                            continue
                        if not tmp:
                            tmp.append(target)
                        elif target - tmp[0] <= 600:
                            tmp.append(target)
                        else:
                            groups.append(tmp)
                            tmp = [target]
                    except Exception as e:
                        print(f"解析时间出错: {str(e)}")
                        sender.reply(f"❌ 时间解析出错: {str(e)}")
                        return
                if tmp:
                    groups.append(tmp)

                if not groups:
                    sender.reply("❌ 所有定时时间均已过期，无需运行")
                    push_to_admin("⚠️ 所有定时时间均已过期，无需运行")
                    return

                target_times = groups[0]
                wait_seconds = int(target_times[0] - now_ts)
                if wait_seconds > 0:
                    sender.reply(f"⏳ 等待 {wait_seconds} 秒后开始抢兑...")

                keys = middleware.bucketAllKeys('Joh_sf_Items')
                if not keys:
                    return sender.reply("❌ 未找到任何需要抢兑的账号")

                cur_time_obj = dt_time(cur.tm_hour, cur.tm_min)
                current_round = None
                # —— 判断免单 ——
                if dt_time(8, 40) <= cur_time_obj <= dt_time(9, 20):
                    current_round = "09:00"
                elif dt_time(11, 40) <= cur_time_obj <= dt_time(12, 20):
                    current_round = "12:00"
                elif dt_time(14, 40) <= cur_time_obj <= dt_time(15, 20):
                    current_round = "15:00"

                # 超寄星期三 6 折券时间窗：仅周三 11:30–12:00 的「运行抢兑」才会触发
                is_wednesday = datetime.now().weekday() == 2  # Monday=0
                is_weekly_60_time = dt_time(11, 40) <= cur_time_obj <= dt_time(12, 20)

                sf_express_list: List[SFExpress] = []      # 普通实物/秒杀/6折券
                free_coupon_results: Dict[str, Tuple[SFExpress, str]] = {}

                for index, key in enumerate(keys):
                    value = middleware.bucketGet('Joh_sf', key)
                    if not value:
                        continue
                    goods_info = middleware.bucketGet('Joh_sf_Items', key)
                    if not goods_info:
                        sender.reply(f"❌ 账号 {key} 未选择抢兑商品")
                        continue

                    # —— 会员日免单券 —— 
                    if "free_coupon" in goods_info:
                        free_coupon_time = goods_info.split('@')[1]
                        should_run = False
                        if free_coupon_time == "ALL":
                            if current_round:
                                free_coupon_time = current_round
                                should_run = True
                            else:
                                print(f"⏭️ 账号 {key} 选择了全部时间段，但当前不在任何场次时间范围内，跳过")
                        else:
                            try:
                                ttuple = time.strptime(free_coupon_time, '%H:%M')
                                if ttuple.tm_hour < cur.tm_hour:
                                    print(f"⏭️ 账号 {key} 选择的场次 {free_coupon_time} 已过期，跳过")
                                else:
                                    should_run = True
                            except Exception:
                                should_run = True
                        if should_run:
                            sfx = SFExpress(value, key, index, sender)
                            free_coupon_results[key] = (sfx, free_coupon_time)

                    # —— 超寄星期三 6 折券 —— 
                    elif goods_info.startswith(WEEKLY_60_PREFIX):
                        if not (is_wednesday and is_weekly_60_time):
                            print(f"⏭️ 账号 {key} 当前不在周三 6 折券抢兑时间窗内，跳过")
                            continue
                        sfx = SFExpress(value, key, index, sender)
                        sfx.task_type = 'weekly60'
                        if sfx.login_res:
                            sf_express_list.append(sfx)

                    # —— 积分秒杀 —— 
                    elif "seckill@" in goods_info:
                        cur_obj = dt_time(cur.tm_hour, cur.tm_min)
                        target_periods = None
                        if dt_time(9, 40) <= cur_obj <= dt_time(10, 20):
                            target_periods = "6131"
                        elif dt_time(13, 40) <= cur_obj <= dt_time(14, 20):
                            target_periods = "6132"
                        elif dt_time(17, 40) <= cur_obj <= dt_time(18, 20):
                            target_periods = "6133"

                        if not target_periods:
                            print(f"⏭️ 账号 {key} 当前时间不在秒杀场次范围内，跳过")
                            continue

                        matched_entries: List[str] = []
                        for entry in goods_info.split('#'):
                            if entry.startswith('seckill@'):
                                parts = entry.split('@')
                                if len(parts) >= 4 and parts[3] == target_periods:
                                    matched_entries.append(entry)
                                    if len(parts) > 4:
                                        print(f"✅ 账号 {key} 的商品 {parts[4]} 场次匹配 (session:{parts[3]})")

                        if not matched_entries:
                            print(f"⏭️ 账号 {key} 没有当前场次 {target_periods} 的商品，跳过")
                            continue

                        sfx = SFExpress(value, key, index, sender)
                        sfx.goods_info = matched_entries
                        sfx.task_type = 'seckill'
                        if sfx.login_res:
                            sf_express_list.append(sfx)

                    # —— 积分商城实物 —— 
                    else:
                        if not (dt_time(9, 40) <= cur_time_obj <= dt_time(10, 20)):
                            print(f"⏭️ 账号 {key} 当前不在积分实物抢兑时间，跳过")
                            continue

                        sfx = SFExpress(value, key, index, sender)
                        sfx.goods_info = []
                        for entry in goods_info.split('#'):
                            if '@' in entry:
                                gname, gid = entry.split('@', 1)
                                sfx.goods_info.append((gname, gid))
                        sfx.task_type = 'goods'
                        if sfx.login_res:
                            sf_express_list.append(sfx)

                if not sf_express_list and not free_coupon_results:
                    sender.reply("⚠️ 所有账号因场次过期或配置无效，未执行任何抢兑任务")
                    push_to_admin("⚠️ 所有账号因场次过期或配置无效，未执行任何抢兑任务")
                    return

                human_times = ', '.join([time.strftime('%H:%M:%S', time.localtime(tt)) for tt in target_times])
                sender.reply(f"✅ 已准备就绪，将在以下时间开始抢兑：{human_times}")
                push_to_admin(f"✅ 已准备就绪，将在以下时间开始抢兑：{human_times}")

                all_time_results: List[str] = []
                user_results: Dict[str, List[str]] = {}

                # 到点并发执行
                for ts in target_times:
                    wait = ts - time.time()
                    if wait > 0:
                        time.sleep(wait)
                    results: List[str] = []

                    if sf_express_list:
                        with ThreadPoolExecutor(max_workers=len(sf_express_list)) as executor:
                            fut_map = {}
                            for sfx in sf_express_list:
                                task_type = getattr(sfx, "task_type", None)
                                if task_type == 'seckill':
                                    fut = executor.submit(sfx.exchange_seckill)
                                elif task_type == 'weekly60':
                                    fut = executor.submit(sfx.exchange_weekly_60_coupon)
                                else:
                                    fut = executor.submit(sfx.exchange_goods)
                                fut_map[fut] = sfx

                            for fut, sfx in fut_map.items():
                                try:
                                    res = fut.result()
                                    results.append(f"账号 {sfx.phone_masked} 的执行结果：\n{res.strip()}")
                                    user_results.setdefault(sfx.phone_masked, []).append(res.strip())
                                except Exception as e:
                                    print(f"账号 {sfx.phone_masked} 抢兑时出错: {str(e)}")
                                    results.append(f"账号 {sfx.phone_masked} 的执行结果：\n❌ 抢兑时出错: {str(e)} ")
                                    user_results.setdefault(sfx.phone_masked, []).append(f"❌ 抢兑时出错: {str(e)}")

                    for k, (sfx, free_time) in free_coupon_results.items():
                        try:
                            res = sfx.exchange_free_coupon(free_time)
                            results.append(f"账号 {k} 的免单券执行结果：\n{res}")
                            user_results.setdefault(k, []).append(res)
                        except Exception as e:
                            print(f"账号 {k} 免单券抢兑时出错: {str(e)}")
                            results.append(f"账号 {k} 的免单券执行结果：\n❌ 免单券抢兑失败: {str(e)}")
                            user_results.setdefault(k, []).append(f"❌ 免单券抢兑失败: {str(e)}")

                    all_time_results.extend(results)

                final_summary = "\n\n".join(all_time_results)
                push_to_admin(final_summary)
                for k, lst in user_results.items():
                    tip = "💡提示：如果没抢到不用管，隔日会继续尝试"
                    all_user_results = "\n\n".join([f"账号 {k} 的执行结果：\n{r}\n{tip}" for r in lst])
                    push_to_user(k, all_user_results)
                sender.reply(final_summary)

            except Exception as e:
                print(f"执行抢兑时出错: {str(e)}")
                sender.reply(f"❌ 执行抢兑时出错: {str(e)} ")

        elif message == "清理抢兑":
            if not sender.isAdmin():
                sender.reply("⚠️ 该指令仅限管理员使用")
                return
            keys = middleware.bucketAllKeys('Joh_sf')
            if keys:
                for k in keys:
                    middleware.bucketDel('Joh_sf', k)
                items = middleware.bucketAllKeys('Joh_sf_Items')
                if items:
                    for k in items:
                        middleware.bucketDel('Joh_sf_Items', k)
                sender.reply("✅ 已成功清空抢兑数据库。")
            else:
                sender.reply("✅ 抢兑数据库已是空的。")

    except Exception as e:
        print(f"插件出错: {str(e)}")
        sender.reply(f"❌ 任务过程中出错：{str(e)} ")

if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    main(sender)
