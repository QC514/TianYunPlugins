#[title: 捷停车]
#[language: python]
#[class: 工具类]
#[author: huawei]
#[service: 1603960061]
#[disable:false]
#[admin: false]
#[rule: ^捷停车登录$|^登录捷停车$|^捷停车查询$|^捷停车管理$|^捷停车授权$|^捷停车清理$|^捷停车上传$]
#[cron: ]
#[priority: 0]
#[platform: qq,qb,wx,tb,tg,web,wxmp]
#[open_source: false]
#[icon: https://free.picui.cn/free/2025/12/17/69418a3031112.png]
#[version: 1.5.3]
#[public: true]
#[price: 28.88]
#[description: 捷停车小程序自动登录，支持验证码自动识别<br>功能：账号登录、授权管理、积分兑换、token管理<br>支持：码支付、呆呆面板同步]

# [param: {"required":false,"key":"G_JTC.ocr_api","bool":false,"placeholder":"http://1.94.118.234:8886/ocr","name":"ddddocr API地址","desc":"验证码识别API地址，默认: http://1.94.118.234:8886/ocr"}]
# [param: {"required":false,"key":"G_JTC.price","bool":false,"placeholder":"例:0.88,不填为0元","name":"授权价格","desc":"授权价格(单位:元)/月"}]
# [param: {"required":false,"key":"G_JTC.coin","bool":false,"placeholder":"不填为关闭积分授权","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"G_JTC.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"微信赞赏码/收款码链接"}]
# [param: {"required":false,"key":"G_JTC.ql_config","bool":false,"placeholder":"格式:http://qinglong地址|ClientID|ClientSecret","name":"青龙配置","desc":"青龙面板配置信息，用|分隔"}]
# [param: {"required":false,"key":"G_JTC.ql_envname","bool":false,"placeholder":"例:G_JTC","name":"青龙变量名","desc":"推送到青龙的变量名称"}]
# [param: {"required":false,"key":"G_JTC.daidai_config","bool":false,"placeholder":"格式:http://呆呆地址丨app_key丨app_secret","name":"呆呆面板配置","desc":"呆呆面板配置信息，用丨分隔"}]
# [param: {"required":false,"key":"G_JTC.daidai_group","bool":false,"placeholder":"例:捷停车","name":"呆呆分组","desc":"呆呆面板环境变量分组名称"}]
# [param: {"required":false,"key":"G_JTC.use_daidai","bool":true,"name":"使用呆呆面板","desc":"勾选=上传呆呆面板，不勾选=上传青龙面板(默认)"}]
# [param: {"required":false,"key":"dd_sign_config.zsm","bool":false,"placeholder":"http://xxxx.co/xxx.jpg","name":"收款码(全局)","desc":"微信赞赏码/收款码链接"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_switch","bool":true,"name":"码支付开关(全局)","desc":"勾选启用码支付功能"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_gateway","bool":false,"placeholder":"https://demopay.9999.blue/","name":"码支付网关(全局)","desc":"支付网关地址"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_pid","bool":false,"placeholder":"10006","name":"商户ID(全局)","desc":"支付平台的商户ID"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_key","bool":false,"placeholder":"FwzZNeOdNAD5FHm1PDsT","name":"商户密钥(全局)","desc":"支付平台的商户密钥"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_type","bool":false,"placeholder":"alipay,wxpay","name":"支付方式(全局)","desc":"支付方式，多个用英文逗号隔开"}]
# [param: {"required":false,"key":"dd_sign_config.ma_pay_notify_url","bool":false,"placeholder":"https://xxx.com/notify","name":"回调地址(全局)","desc":"支付回调通知地址（可选）"}]

import json, requests, re, time, base64, middleware, uuid, random, warnings, hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from urllib.parse import quote
warnings.filterwarnings('ignore', message='Unverified HTTPS request')
try:
    from user_agent import generate_user_agent
    HAS_UA_LIB = True
except:
    HAS_UA_LIB = False

try:
    from autman_huawei import DadaiPanelClient, QingLongClient, MaPayClient, generate_qrcode_url, get_pay_config
    HAS_HUAWEI_LIB = True
except ImportError:
    DadaiPanelClient = None
    QingLongClient = None
    MaPayClient = None
    generate_qrcode_url = None
    get_pay_config = None
    HAS_HUAWEI_LIB = False

BUCKET_ACCOUNTS = 'jtc_accounts'
BUCKET_CONFIG = 'G_JTC'
PROJECT_NAME = '捷停车'
BASE_URL = "https://sytgate.jslife.com.cn"
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

def get_random_ua() -> str:
    if HAS_UA_LIB:
        try:
            return generate_user_agent()
        except:
            pass
    uas = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36","Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0","Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"]
    return random.choice(uas)

def get_headers() -> dict:
    return {"User-Agent": get_random_ua(), "Accept": "application/json", "Content-Type": "application/json"}

def get_config() -> dict:
    ma_pay_switch_raw = middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false'
    if isinstance(ma_pay_switch_raw, bool): ma_pay_switch = ma_pay_switch_raw
    elif ma_pay_switch_raw is None: ma_pay_switch = False
    else: ma_pay_switch = str(ma_pay_switch_raw).lower() == 'true'

    use_daidai_raw = middleware.bucketGet(BUCKET_CONFIG, 'use_daidai') or 'false'
    if isinstance(use_daidai_raw, bool): use_daidai = use_daidai_raw
    elif use_daidai_raw is None: use_daidai = False
    else: use_daidai = str(use_daidai_raw).lower() == 'true'

    return {
        'ocr_api': middleware.bucketGet(BUCKET_CONFIG, 'ocr_api') or 'http://1.94.118.234:8886/ocr',
        'price': Decimal(middleware.bucketGet(BUCKET_CONFIG, 'price') or '0'),
        'coin': middleware.bucketGet(BUCKET_CONFIG, 'coin') or '',
        'zsm': middleware.bucketGet('dd_sign_config', 'zsm') or middleware.bucketGet(BUCKET_CONFIG, 'zsm') or '',
        'ql_config': middleware.bucketGet(BUCKET_CONFIG, 'ql_config') or '',
        'ql_envname': middleware.bucketGet(BUCKET_CONFIG, 'ql_envname') or 'JT_TOKEN',
        'daidai_config': middleware.bucketGet(BUCKET_CONFIG, 'daidai_config') or '',
        'daidai_group': middleware.bucketGet(BUCKET_CONFIG, 'daidai_group') or PROJECT_NAME,
        'use_daidai': use_daidai,
        'ma_pay_switch': ma_pay_switch,
        'ma_pay_gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
        'ma_pay_pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
        'ma_pay_key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
        'ma_pay_type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay',
        'ma_pay_notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or ''
    }

def get_user_accounts(user_id=None) -> dict:
    if not user_id: user_id = userid
    accounts_json = middleware.bucketGet(BUCKET_ACCOUNTS, user_id) or "{}"
    try:
        return json.loads(accounts_json)
    except:
        return {}

def save_user_accounts(accounts, user_id=None):
    if not user_id: user_id = userid
    middleware.bucketSet(BUCKET_ACCOUNTS, user_id, json.dumps(accounts, ensure_ascii=False))

def recognize_captcha(image_url: str, ocr_api: str) -> str:
    try:
        r = requests.get(image_url, timeout=10, verify=False)
        if r.status_code != 200: return ""
        base64_img = base64.b64encode(r.content).decode()
        api_resp = requests.post(ocr_api, data={"image": base64_img, "probability": False, "png_fix": False}, timeout=10, verify=False)
        result = api_resp.json()
        if result.get("code") == 200 and result.get("data"):
            return result.get("data", "").strip()
        return ""
    except Exception as e:
        return ""

def generate_timestamp() -> str:
    """生成时间戳（毫秒）"""
    return str(int(time.time() * 1000))

def get_app_headers(uc_id: str) -> dict:
    """生成APP请求头"""
    return {
        "User-Agent": "okhttp/4.10.0",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json; charset=utf-8",
        "UC_ID": uc_id,
        "applicationVersion": "60400"
    }

def get_verify_image(telephone: str, device_id: str, uc_id: str) -> dict:
    try:
        params = {
            "applictionType": "APP",
            "applictionVersion": "60400",
            "privacyVersion": "1.0",
            "telephone": telephone,
            "telephoneType": 1,
            "timestamp": generate_timestamp(),
            "verifyType": "VERIFY_LOGIN",
            "version": "V1.0"
        }
        r = requests.post(f"{BASE_URL}/core-gateway/user/login/verify/image", json=params, headers=get_app_headers(uc_id), timeout=10, verify=False)
        result = r.json()
        return result.get("obj", {}) if result.get("success") else {}
    except:
        return {}

def send_sms_code(telephone: str, key: str, captcha_code: str, device_id: str, uc_id: str) -> bool:
    try:
        params = {
            "applictionType": "APP",
            "applictionVersion": "60400",
            "privacyVersion": "1.0",
            "telephone": telephone,
            "telephoneType": 1,
            "timestamp": generate_timestamp(),
            "verifyType": "VERIFY_LOGIN",
            "version": "V1.0"
        }
        if captcha_code:
            params["captchaCode"] = captcha_code
        if key:
            params["key"] = key
        r = requests.post(f"{BASE_URL}/core-gateway/user/login/sms/push", json=params, headers=get_app_headers(uc_id), timeout=10, verify=False)
        return r.json().get("success", False)
    except:
        return False

def login_with_sms(telephone: str, msg_code: str, device_id: str, uc_id: str) -> dict:
    try:
        params = {
            "appSource": "A3",
            "applictionType": "APP",
            "applictionVersion": "60400",
            "deviceId": device_id,
            "osType": "ANDROID",
            "privacyVersion": "1.0",
            "sceneSource": "LOGIN",
            "telephone": telephone,
            "telephoneType": 1,
            "timestamp": generate_timestamp(),
            "userSource": "A3",
            "userType": "APP_JTC",
            "verificationCode": msg_code
        }
        r = requests.post(f"{BASE_URL}/core-gateway/user/login/app_login", json=params, headers=get_app_headers(uc_id), timeout=10, verify=False)
        result = r.json()
        if result.get("success") and result.get("obj"):
            user_info = result.get("obj", {})
            user_id = user_info.get("userId", "")
            token = user_info.get("token", "")
            return {
                "user_id": user_id,
                "telephone": user_info.get("telephone", telephone),
                "nickName": user_info.get("nickName", ""),
                "token": token,
                "deviceId": device_id
            }
        return {}
    except:
        return {}

def process_login(config: dict) -> bool:
    try:
        sender.reply("请输入手机号：")
        telephone = sender.listen(60000)
        if not telephone:
            sender.reply("感谢使用！")
            return False
        telephone = telephone.strip()
        if not telephone:
            sender.reply("❌ 未收到手机号")
            return False
        if telephone.lower() == 'q':
            sender.reply("✅ 已取消")
            return False
        if not re.match(r'^1[3-9]\d{9}$', telephone):
            sender.reply("❌ 手机号格式不正确，请输入11位手机号")
            return False
        
        device_id = str(uuid.uuid4()).replace('-', '')
        uc_id = device_id
        ocr_api = config.get('ocr_api', '')
        
        # 获取验证图片（只获取一次）
        verify_data = get_verify_image(telephone, device_id, uc_id)
        if not verify_data:
            sender.reply("❌ 获取验证图片失败，请稍后重试")
            return False
        
        key = verify_data.get("key", "")
        is_verify_image = verify_data.get("isVerifyImage", "1") == "1"
        url = verify_data.get("url", "")
        
        captcha_code = ""
        if is_verify_image and url:
            # 图片验证码：3次输入机会
            for captcha_attempt in range(1, 4):
                if captcha_attempt == 1:
                    sender.reply("🔍 正在识别验证码...")
                    captcha_code = recognize_captcha(url, ocr_api)
                    if captcha_code:
                        sender.reply(f"✅ 识别成功: {captcha_code}")
                    else:
                        sender.reply(f"⚠️ 自动识别失败\n请输入图片验证码（剩余{4-captcha_attempt}次机会）：")
                        captcha_code = sender.listen(60000)
                        if not captcha_code:
                            sender.reply("感谢使用！")
                            return False
                        captcha_code = captcha_code.strip()
                else:
                    sender.reply(f"请重新输入图片验证码（剩余{4-captcha_attempt}次机会）：")
                    captcha_code = sender.listen(60000)
                    if not captcha_code:
                        sender.reply("感谢使用！")
                        return False
                    captcha_code = captcha_code.strip()
                
                if not captcha_code:
                    sender.reply("❌ 验证码不能为空")
                    if captcha_attempt == 3:
                        sender.reply("❌ 验证码输入失败次数过多，请重新开始")
                        return False
                    continue
                if captcha_code.lower() == 'q':
                    sender.reply("✅ 已取消")
                    return False
                if len(captcha_code) != 4:
                    sender.reply("❌ 验证码格式错误（应为4位）")
                    if captcha_attempt == 3:
                        sender.reply("❌ 验证码输入失败次数过多，请重新开始")
                        return False
                    continue
                
                # 尝试发送短信
                if send_sms_code(telephone, key, captcha_code, device_id, uc_id):
                    break
                else:
                    if captcha_attempt == 3:
                        sender.reply("❌ 图片验证码错误次数过多，请重新开始")
                        return False
                    sender.reply("❌ 图片验证码错误")
        else:
            sender.reply("✅ 账号已注册，无需图片验证")
            if not send_sms_code(telephone, key, captcha_code, device_id, uc_id):
                sender.reply("❌ 短信发送失败，请稍后重试")
                return False
        
        # 短信验证码：3次输入机会
        sender.reply("✅ 短信发送成功！\n请输入收到的验证码（有效期3分钟）：")
        for sms_attempt in range(1, 4):
            if sms_attempt > 1:
                sender.reply(f"请重新输入短信验证码（剩余{4-sms_attempt}次机会）：")
            
            msg_code = sender.listen(180000)
            if not msg_code:
                sender.reply("感谢使用！")
                return False
            msg_code = msg_code.strip()
            if not msg_code:
                sender.reply("❌ 验证码输入超时")
                return False
            if msg_code.lower() == 'q':
                sender.reply("✅ 已取消")
                return False
            if len(msg_code) != 6:
                sender.reply("❌ 验证码格式错误（应为6位）")
                if sms_attempt == 3:
                    sender.reply("❌ 短信验证码输入失败次数过多")
                    return False
                continue
            
            sender.reply("🔐 正在验证登录...")
            user_info = login_with_sms(telephone, msg_code, device_id, uc_id)
            if user_info and user_info.get("user_id"):
                user_id = user_info.get("user_id")
                phone = user_info.get("telephone", telephone)
                token = user_info.get("token", "")
                user_accounts = get_user_accounts()
                
                # 检查是否已存在相同手机号的账号，如果存在则更新而非新增
                existing_account_id = None
                for acc_id, acc in user_accounts.items():
                    if acc.get('phone') == phone:
                        existing_account_id = acc_id
                        break
                
                if existing_account_id:
                    # 更新已存在的账号
                    user_accounts[existing_account_id]['data'] = f"{user_id}#{token}"
                    user_accounts[existing_account_id]['nickName'] = user_info.get("nickName", "")
                    user_accounts[existing_account_id]['bind_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    save_user_accounts(user_accounts)
                    masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                    # 如果已授权且未过期，同步新token到面板
                    panel_msg = ""
                    auth_status = user_accounts[existing_account_id].get('auth_status', {})
                    expire_time = auth_status.get('expire_time', '')
                    is_valid = auth_status.get('is_authorized', False) and expire_time and datetime.strptime(expire_time, '%Y-%m-%d').date() >= datetime.now().date()
                    if is_valid:
                        panel_ok = sync_to_panel(existing_account_id, phone, expire_time, config)
                        pn = get_panel_name(config)
                        if is_panel_configured(config):
                            panel_msg = f"\n🔄 {pn}同步: 成功" if panel_ok else f"\n⚠️ {pn}同步: 失败"
                    sender.reply(f"✅ 账号更新成功！\n📱 账号: {masked_phone}{panel_msg}\n\n您可以发送「捷停车管理」进行授权")
                else:
                    # 新增账号
                    account_id = str(uuid.uuid4())
                    user_accounts[account_id] = {
                        "phone": phone,
                        "data": f"{user_id}#{token}",
                        "nickName": user_info.get("nickName", ""),
                        "bind_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "auth_status": {"is_authorized": False, "expire_time": ""}
                    }
                    save_user_accounts(user_accounts)
                    masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                    sender.reply(f"✅ 登录成功！\n📱 账号: {masked_phone}\n\n您可以发送「捷停车管理」进行授权")
                return True
            else:
                if sms_attempt == 3:
                    sender.reply("❌ 短信验证码错误次数过多")
                    return False
                sender.reply("❌ 短信验证码错误")
        
        return False
    except Exception as e:
        sender.reply(f"❌ 登录异常: {str(e)}")
        return False

def query_accounts() -> bool:
    try:
        user_accounts = get_user_accounts()
        if not user_accounts:
            sender.reply("您还没有绑定任何捷停车账号\n请发送「捷停车登录」进行绑定")
            return False
        
        for account_id, account in user_accounts.items():
            phone = account.get('phone', '未知')
            masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
            account_data = account.get('data', '')
            auth_status = account.get('auth_status', {})
            is_authorized = auth_status.get('is_authorized', False)
            expire_time = auth_status.get('expire_time', '')
            
            # 获取余额信息
            balance_info = query_balance(account_data)
            total_coin = balance_info.get('data', {}).get('accountAmt', 0) if balance_info.get('success') else 0
            
            # 获取停车币记录
            today = datetime.now().strftime("%Y-%m-%d")
            today_coin = 0
            recent_records = []
            try:
                parts = account_data.split('#')
                if len(parts) >= 2:
                    user_id = parts[0]
                    url = f"{BASE_URL}/base-gateway/integral/v2/user/page/new"
                    data = {"userId": user_id, "valueType": "", "pageIndex": 1, "pageSize": 100}
                    r = requests.post(url, json=data, timeout=10, verify=False)
                    if r.status_code == 200:
                        result = r.json()
                        if result.get('success') and result.get('data'):
                            records = result['data'].get('data', [])
                            for record in records:
                                create_time = record.get('createTime', '')
                                value_type = record.get('valueType', '')
                                integral_value = int(record.get('integralValue', 0))
                                if value_type == 'ADD':
                                    if create_time.startswith(today):
                                        today_coin += integral_value
                                    if len(recent_records) < 5:
                                        date_str = create_time[:10] if len(create_time) >= 10 else create_time
                                        recent_records.append(f"领取 {integral_value}停车币-{date_str}")
            except:
                pass
            
            auth_msg = f"✅ 已授权\n📅 到期时间: 到期: {expire_time}" if is_authorized else "❌ 未授权"
            msg = f"=====捷停车详情========\n"
            msg += f"📱 账号: {masked_phone}\n"
            msg += f"🔐 授权状态: {auth_msg}\n"
            msg += f"💰 总币: {total_coin}元，今日币：{today_coin}\n"
            if recent_records:
                msg += "===== 🎁任务完成🎁 =====\n"
                msg += "\n".join(recent_records) + "\n"
            msg += "===================="
            sender.reply(msg)
        
        return True
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")
        return False

def query_balance(account_data: str) -> dict:
    """查询积分余额，account_data格式: user_id#token"""
    try:
        parts = account_data.split('#')
        if len(parts) < 2:
            return {"success": False}
        user_id = parts[0]
        url = f"{BASE_URL}/base-gateway/integral/v2/balance/query"
        data = {"userId": user_id, "signType": "MD5", "reqSource": "APP_JTC", "applictionType": "APP", "applictionVersion": "60408", "timestamp": str(int(time.time() * 1000)), "sign": "E8E4E0E6C6A619AA09869E875B78697D", "nonce": str(uuid.uuid4()).upper()}
        r = requests.post(url, json=data, timeout=10, verify=False)
        return r.json() if r.status_code == 200 else {"success": False}
    except:
        return {"success": False}

def cleanup_expired_data() -> bool:
    """清理过期账号并推送即将过期通知"""
    try:
        try:
            users = middleware.bucketAllKeys(bucket=BUCKET_ACCOUNTS) or []
        except:
            users = []
        if not users:
            sender.reply("❌ 无用户数据")
            return False
        
        sender.reply("🔍 正在检查所有用户账号状态...")
        config = get_config()
        ql_config, ql_envname = config.get('ql_config', ''), config.get('ql_envname', 'G_JTC')
        current_date = datetime.now().date()
        total_accounts, expired_count, warning_count, notified_users = 0, 0, 0, 0
        
        for uid in users:
            user_accounts = get_user_accounts(uid)
            if not user_accounts: continue
            expired_ids, warning_phones = [], []
            
            for account_id, account in user_accounts.items():
                total_accounts += 1
                phone = account.get('phone', '')
                auth_status = account.get('auth_status', {})
                expire_str = auth_status.get('expire_time', '')
                is_authorized = auth_status.get('is_authorized', False)
                
                if not is_authorized or not expire_str:
                    expired_ids.append((account_id, phone, "未授权"))
                    continue
                try:
                    expire_date = datetime.strptime(expire_str, '%Y-%m-%d').date()
                    days_left = (expire_date - current_date).days
                    if days_left < 0:
                        expired_ids.append((account_id, phone, f"已过期{abs(days_left)}天"))
                    elif days_left <= 3:
                        masked = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                        warning_phones.append((masked, f"剩余{days_left}天"))
                except:
                    expired_ids.append((account_id, phone, "授权异常"))
            
            # 清理过期账号
            for account_id, phone, reason in expired_ids:
                if phone:
                    delete_from_panel(phone, config)
                if account_id in user_accounts:
                    del user_accounts[account_id]
                expired_count += 1
            if expired_ids:
                save_user_accounts(user_accounts, uid)
            
            # 推送即将过期通知
            if warning_phones:
                warning_count += len(warning_phones)
                account_msgs = [f"📱 {p}\n⚠️ 授权即将过期({r})，请续费" for p, r in warning_phones]
                notify_msg = "=====捷停车账号通知=====\n" + "\n-------------------\n".join(account_msgs) + "\n====================\n发送「捷停车管理」续费"
                push_ok = False
                try:
                    middleware.push('wx', '', uid, '账号状态提醒', notify_msg)
                    push_ok = True
                except: pass
                try:
                    middleware.push('qq', '', uid, '账号状态提醒', notify_msg)
                    push_ok = True
                except: pass
                if push_ok: notified_users += 1
        
        sender.reply(
            f"=====清理报告=====\n"
            f"📊 检查用户数: {len(users)}个\n"
            f"📱 检查账号数: {total_accounts}个\n"
            f"🗑️ 清理过期: {expired_count}个\n"
            f"⚠️ 即将过期: {warning_count}个\n"
            f"📤 已推送用户: {notified_users}个\n"
            f"===================="
        )
        return True
    except Exception as e:
        sender.reply(f"❌ 清理失败: {str(e)}")
        return False

def parse_account_selection(choice_str: str, max_index: int) -> list:
    """解析账号选择字符串
    支持格式：
    - 单个数字: "3"
    - 范围: "3-6"
    - 多个选择: "1,4,6"
    - 混合: "1,3-5,8"
    """
    if not choice_str or not choice_str.strip():
        return None
    choice_str = choice_str.strip()
    selected_indices = set()
    try:
        parts = choice_str.split(',')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                range_parts = part.split('-')
                if len(range_parts) != 2:
                    return None
                start = int(range_parts[0].strip())
                end = int(range_parts[1].strip())
                if start < 1 or end < 1 or start > max_index or end > max_index:
                    return None
                if start > end:
                    return None
                for i in range(start - 1, end):
                    selected_indices.add(i)
            else:
                num = int(part)
                if num < 1 or num > max_index:
                    return None
                selected_indices.add(num - 1)
        return sorted(list(selected_indices))
    except (ValueError, AttributeError):
        return None

def process_auth(account_id: str, config: dict) -> bool:
    """单个账号授权（参考顺易充优化）"""
    try:
        user_accounts = get_user_accounts()
        if account_id not in user_accounts:
            sender.reply("❌ 账号不存在")
            return False
        
        account = user_accounts[account_id]
        phone = account.get('phone', '未知')
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        price, coin_price, zsm = config.get('price', Decimal('0')), config.get('coin', ''), config.get('zsm', '')
        user_coin = Decimal(middleware.bucketGet('dd_sign_points', userid) or '0')

        has_pay = price and zsm
        has_mapay = config.get('ma_pay_switch') and config.get('ma_pay_gateway') and config.get('ma_pay_pid') and config.get('ma_pay_key')
        has_coin = coin_price
        if not has_pay and not has_mapay and not has_coin:
            sender.reply("❌ 未配置任何授权方式")
            return False

        # 询问授权月数
        sender.reply("请输入授权月数（1-12）：")
        months_str = sender.listen(60000)
        if not months_str:
            sender.reply("感谢使用！")
            return False
        months_str = months_str.strip()
        if not months_str or months_str == 'q':
            sender.reply("✅ 已取消")
            return False
        try:
            months = int(months_str)
            if not (1 <= months <= 12): raise ValueError()
        except:
            sender.reply("❌ 无效的月数，请输入1-12之间的数字")
            return False

        # 计算费用
        total_price = price * months
        total_coin = Decimal(coin_price) * months if coin_price else Decimal('0')

        # 构建支付选项（三选项标准格式）
        pay_options = []
        pay_handlers = {}
        opt_num = 1
        if has_pay:
            pay_options.append(f"[{opt_num}] 微信扫码 ¥{total_price}")
            pay_handlers[str(opt_num)] = lambda: process_payment_direct(account_id, phone, months, total_price, zsm, user_accounts, config)
            opt_num += 1
        if has_mapay:
            pay_options.append(f"[{opt_num}] 支付宝 ¥{total_price}")
            pay_handlers[str(opt_num)] = lambda: _single_alipay_flow(account_id, phone, months, total_price, user_accounts, config)
            opt_num += 1
        if has_coin:
            pay_options.append(f"[{opt_num}] 积分 {total_coin}")
            pay_handlers[str(opt_num)] = lambda: process_coin_auth_direct(account_id, phone, months, total_coin, user_accounts, config)
        
        # 显示支付菜单（参考顺易充格式）
        auth_msg = f"""
=====捷停车授权支付=====
📱 账号: {masked_phone}
⏰ 时长: {months}月
💰 金额: ¥{total_price}
📊 积分支付: {total_coin}积分（当前积分: {user_coin}）
------------------
{chr(10).join(pay_options)}
回复数字选择支付方式，回复q取消
==================="""
        sender.reply(auth_msg)
        choice = sender.listen(60000)
        if not choice:
            sender.reply("感谢使用！")
            return False
        choice = choice.strip()
        if choice == 'q':
            sender.reply("✅ 已取消")
            return False
        
        if choice in pay_handlers:
            return pay_handlers[choice]()
        else:
            sender.reply("❌ 无效选择")
            return False
    except Exception as e:
        sender.reply(f"❌ 授权异常: {str(e)}")
        return False

def batch_auth(config: dict) -> bool:
    """管理员授权操作（参考顺易充）"""
    try:
        if not sender.isAdmin():
            sender.reply("❌ 您没有管理员权限，无法使用授权功能！\n请发送「捷停车管理」管理您自己的账号")
            return False
        
        sender.reply(
            "=====管理员授权操作=====\n"
            "[1] 一键授权所有用户\n"
            "[2] 单独授权用户\n"
            "回复数字选择操作\n"
            "===================="
        )
        
        choice = sender.listen(60000)
        if not choice:
            sender.reply("感谢使用")
            return False
        choice = choice.strip()
        
        if choice == '1':
            # 一键授权所有用户
            try:
                users = middleware.bucketAllKeys(bucket='jtc_accounts') or []
            except:
                users = []
            
            if not users:
                sender.reply("❌ 未找到任何绑定用户")
                return False
            
            sender.reply("请输入授权月数（1-12）：")
            months_str = sender.listen(120000)
            if not months_str:
                sender.reply("感谢使用")
                return False
            months_str = months_str.strip()
            if not months_str:
                sender.reply("❌ 输入不能为空")
                return False
            
            try:
                months = int(months_str)
                if not (1 <= months <= 12):
                    sender.reply("❌ 月数必须为1-12之间的整数")
                    return False
            except ValueError:
                sender.reply("❌ 月数必须为整数")
                return False
            
            success_count, panel_success_count = 0, 0
            expire_date = (datetime.now().date() + timedelta(days=30 * months)).strftime('%Y-%m-%d')
            pn = get_panel_name(config)

            for user_id in users:
                user_accounts = get_user_accounts(user_id)
                for account_id in user_accounts:
                    user_accounts[account_id]['auth_status'] = {
                        "is_authorized": True,
                        "expire_time": expire_date
                    }
                    phone = user_accounts[account_id].get('phone', '')
                    if sync_to_panel(account_id, phone, expire_date, config, user_id):
                        panel_success_count += 1
                    success_count += 1
                save_user_accounts(user_accounts, user_id)

            panel_msg = f"\n🔄 {pn}推送: {panel_success_count}/{success_count}个" if is_panel_configured(config) else ""
            sender.reply(f"✅ 一键授权完成！\n授权账号数: {success_count}\n授权月数: {months}月\n到期时间: {expire_date}{panel_msg}")
            return True
            
        elif choice == '2':
            # 单独授权用户
            sender.reply("请输入需要授权的用户ID:")
            target_userid = sender.listen(120000)
            if not target_userid:
                sender.reply("感谢使用")
                return False
            target_userid = target_userid.strip()
            if not target_userid:
                sender.reply("❌ 用户ID无效")
                return False
            
            accounts = get_user_accounts(target_userid)
            if not accounts:
                sender.reply(f"❌ 用户 {target_userid} 未绑定任何捷停车账号")
                return False
            
            account_lines = []
            account_ids = []
            for i, (account_id, account) in enumerate(accounts.items(), 1):
                phone = account.get('phone', '未知')
                masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
                auth_status = account.get('auth_status', {})
                is_authorized = auth_status.get('is_authorized', False)
                expire_time = auth_status.get('expire_time', '')
                auth_msg = f"✅ 到期:{expire_time}" if is_authorized else "❌ 未授权"
                account_lines.append(f"[{i}] 📱 {masked_phone} {auth_msg}")
                account_ids.append(account_id)
            
            account_list = "\n".join(account_lines)
            sender.reply(
                "=====用户账号列表=====\n"
                f"账号列表:\n{account_list}\n"
                "------------------\n"
                "回复 [0] 授权全部账号\n"
                "回复序号授权单个账号\n"
                "\n"
                "💡 批量选择示例:\n"
                "   范围选择: 3-6\n"
                "   多个选择: 1,4,6\n"
                "   混合选择: 1,3-5,8\n"
                "===================="
            )
            
            account_choice = sender.listen(120000)
            if not account_choice:
                sender.reply("感谢使用")
                return False
            account_choice = account_choice.strip()
            
            to_authorize_ids = []
            if account_choice == '0':
                to_authorize_ids = account_ids
            else:
                selected_indices = parse_account_selection(account_choice, len(account_ids))
                if selected_indices is None:
                    sender.reply("❌ 选择格式无效！请使用正确格式:\n单个: 3\n范围: 3-6\n多个: 1,4,6\n混合: 1,3-5,8")
                    return False
                if not selected_indices:
                    sender.reply("❌ 未选择任何账号")
                    return False
                to_authorize_ids = [account_ids[idx] for idx in selected_indices]
            
            sender.reply("请输入授权月数（1-12）：")
            months_str = sender.listen(120000)
            if not months_str:
                sender.reply("感谢使用")
                return False
            months_str = months_str.strip()
            if not months_str:
                sender.reply("❌ 输入不能为空")
                return False
            
            try:
                months = int(months_str)
                if not (1 <= months <= 12):
                    sender.reply("❌ 月数必须为1-12之间的整数")
                    return False
            except ValueError:
                sender.reply("❌ 月数必须为整数")
                return False
            
            authorized_count = 0
            expire_date = (datetime.now().date() + timedelta(days=30 * months)).strftime('%Y-%m-%d')

            for account_id in to_authorize_ids:
                if account_id in accounts:
                    accounts[account_id]['auth_status'] = {
                        "is_authorized": True,
                        "expire_time": expire_date
                    }
                    phone = accounts[account_id].get('phone', '')
                    sync_to_panel(account_id, phone, expire_date, config, target_userid)
                    authorized_count += 1

            save_user_accounts(accounts, target_userid)
            sender.reply(
                f"✅ 授权成功！\n"
                f"用户ID: {target_userid}\n"
                f"授权账号数: {authorized_count}\n"
                f"授权月数: {months}月\n"
                f"到期时间: {expire_date}"
            )
            return True
        else:
            sender.reply("❌ 无效选择")
            return False
            
    except Exception as e:
        sender.reply(f"❌ 授权异常: {str(e)}")
        return False

def batch_manage(config: dict) -> bool:
    """批量管理账号"""
    try:
        user_accounts = get_user_accounts()
        if not user_accounts:
            sender.reply("您还没有绑定任何捷停车账号\n请发送「捷停车登录」进行绑定")
            return False
        
        user_coin = Decimal(middleware.bucketGet('dd_sign_points', userid) or '0')
        authorized_count = sum(1 for acc in user_accounts.values() if acc.get('auth_status', {}).get('is_authorized', False))
        unauthorized_count = len(user_accounts) - authorized_count
        
        account_ids = list(user_accounts.keys())
        account_lines = []
        for i, account_id in enumerate(account_ids, 1):
            phone = user_accounts[account_id].get('phone', '未知')
            masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
            auth_status = user_accounts[account_id].get('auth_status', {})
            is_authorized = auth_status.get('is_authorized', False)
            expire_time = auth_status.get('expire_time', '')
            auth_msg = f"✅ 到期:{expire_time}" if is_authorized else "❌ 未授权"
            account_lines.append(f"[{i}] 📱 {masked_phone}\n {auth_msg}")
        
        account_list = "\n".join(account_lines)
        sender.reply(
            "=====账号管理=====\n"
            f"📱 绑定账号: {len(user_accounts)}个\n"
            f"✅ 已授权: {authorized_count}个\n"
            f"❌ 未授权: {unauthorized_count}个\n"
            f"💰 当前积分: {user_coin}\n"
            "--------------------\n"
            f"{account_list}\n"
            "[0] 全部授权\n"
            "[00] 未授权账号\n"
            "[9998] 删除所有账号\n"
            "--------------------\n"
            "💡 批量选择示例:\n"
            "   范围选择: 3-6\n"
            "   多个选择: 1,4,6\n"
            "   混合选择: 1,3-5,8\n"
            "回复序号选择操作 (q退出)\n"
            "=================="
        )
        
        choice = sender.listen(120000)
        if not choice:
            sender.reply("感谢使用！")
            return False
        choice = choice.strip()
        if not choice:
            sender.reply("⏰ 操作超时")
            return False
        
        if choice == 'q':
            sender.reply("✅ 已取消")
            return False
        
        to_manage_ids = []
        if choice == '0':
            to_manage_ids = account_ids
        elif choice == '00':
            to_manage_ids = [aid for aid in account_ids if not user_accounts[aid].get('auth_status', {}).get('is_authorized', False)]
            if not to_manage_ids:
                sender.reply("✅ 所有账号都已授权")
                return False
        elif choice == '9998':
            sender.reply("⚠️ 确认删除所有账号吗？\n回复 [Y] 确认删除\n回复 [N] 取消")
            confirm = sender.listen(60000)
            if not confirm or confirm.strip().lower() != 'y':
                sender.reply("✅ 已取消")
                return False
            middleware.bucketDel(BUCKET_ACCOUNTS, userid)
            sender.reply("✅ 删除成功！\n所有账号已删除")
            return True
        else:
            selected_indices = parse_account_selection(choice, len(account_ids))
            if selected_indices is None:
                sender.reply("❌ 选择格式无效！\n请使用正确格式:\n单个: 3\n范围: 3-6\n多个: 1,4,6\n混合: 1,3-5,8")
                return False
            if not selected_indices:
                sender.reply("❌ 未选择任何账号")
                return False
            to_manage_ids = [account_ids[idx] for idx in selected_indices]
        
        sender.reply("====操作选项====\n[1] 授权\n[2] 删除\n[0] 返回\n================\n请选择操作：")
        op = sender.listen(60000)
        if not op:
            sender.reply("感谢使用！")
            return False
        op = op.strip()
        if not op:
            sender.reply("⏰ 操作超时")
            return False
        
        if op == '0':
            sender.reply("✅ 已返回")
            return False
        
        if op == '1':
            if len(to_manage_ids) == 1:
                return process_auth(to_manage_ids[0], config)
            return process_batch_payment(to_manage_ids, user_accounts, config)
        elif op == '2':
            # 删除账号时同步删除面板变量
            delete_count = 0
            panel_deleted_count = 0
            pn = get_panel_name(config)
            for account_id in to_manage_ids:
                phone = user_accounts[account_id].get('phone', '')
                if phone:
                    if delete_from_panel(phone, config):
                        panel_deleted_count += 1
                del user_accounts[account_id]
                delete_count += 1
            save_user_accounts(user_accounts)
            panel_msg = f"\n🔄 {pn}变量已删除: {panel_deleted_count}个" if is_panel_configured(config) and panel_deleted_count > 0 else ""
            sender.reply(f"✅ 删除成功！\n已删除 {delete_count} 个账号{panel_msg}")
        else:
            sender.reply("❌ 无效选择")
        
        return True
    except Exception as e:
        sender.reply(f"❌ 管理异常: {str(e)}")
        return False

def process_batch_payment(account_ids: list, user_accounts: dict, config: dict) -> bool:
    """多个账号合并支付（参考顺易充优化）"""
    try:
        price, coin_price, zsm = config.get('price', Decimal('0')), config.get('coin', ''), config.get('zsm', '')
        user_coin = Decimal(middleware.bucketGet('dd_sign_points', userid) or '0')

        has_pay = price and zsm
        has_mapay = config.get('ma_pay_switch') and config.get('ma_pay_gateway') and config.get('ma_pay_pid') and config.get('ma_pay_key')
        has_coin = coin_price
        if not has_pay and not has_mapay and not has_coin:
            sender.reply("❌ 未配置任何授权方式")
            return False
        
        # 获取第一个账号的手机号用于显示
        first_phone = user_accounts[account_ids[0]].get('phone', '未知')
        
        # 询问授权月数
        sender.reply("请输入授权月数（1-12）：")
        months_str = sender.listen(60000)
        if not months_str:
            sender.reply("感谢使用！")
            return False
        months_str = months_str.strip()
        if not months_str or months_str == 'q':
            sender.reply("✅ 已取消" if months_str == 'q' else "感谢使用！")
            return False
        try:
            months = int(months_str)
            if not (1 <= months <= 12): raise ValueError()
        except:
            sender.reply("❌ 无效的月数，请输入1-12之间的数字")
            return False
        
        # 合并计算总费用（参考顺易充）
        total_price = price * months * len(account_ids)
        total_coin = Decimal(coin_price) * months * len(account_ids) if coin_price else Decimal('0')
        
        # 构建支付选项（三选项标准格式）
        pay_options = []
        pay_handlers = {}
        opt_num = 1
        if has_pay:
            pay_options.append(f"[{opt_num}] 微信扫码 ¥{total_price}")
            pay_handlers[str(opt_num)] = lambda: _batch_pay_only(account_ids, months, total_price, zsm, user_accounts, config)
            opt_num += 1
        if has_mapay:
            pay_options.append(f"[{opt_num}] 支付宝 ¥{total_price}")
            pay_handlers[str(opt_num)] = lambda: _batch_alipay_only(account_ids, months, total_price, user_accounts, config)
            opt_num += 1
        if has_coin:
            pay_options.append(f"[{opt_num}] 积分 {total_coin}")
            pay_handlers[str(opt_num)] = lambda: _batch_coin_only(account_ids, months, total_coin, user_accounts, user_coin, config)
        
        # 显示支付菜单（参考顺易充格式）
        pay_menu = f"""
=====捷停车授权支付=====
📱 手机号: {first_phone}{f" 等{len(account_ids)}个账号" if len(account_ids) > 1 else ""}
🎯 授权操作: 增加{months}月
💰 金额: ¥{total_price:.2f}
📊 积分支付: {total_coin}积分（当前积分: {user_coin}）
------------------
{chr(10).join(pay_options)}
回复数字选择支付方式，回复q取消
==================="""
        sender.reply(pay_menu)
        choice = sender.listen(60000)
        if not choice:
            sender.reply("感谢使用！")
            return False
        choice = choice.strip()
        if choice == 'q':
            sender.reply("✅ 已取消")
            return False
        if choice in pay_handlers:
            return pay_handlers[choice]()
        sender.reply("❌ 无效选择")
        return False
    except Exception as e:
        sender.reply(f"❌ 批量支付异常: {str(e)}")
        return False

def _batch_pay_only(account_ids: list, months: int, total_price: Decimal, zsm: str, user_accounts: dict, config: dict) -> bool:
    """多个账号纯扫码支付（优化版）"""
    try:
        # 获取第一个账号的手机号
        first_phone = user_accounts[account_ids[0]].get('phone', '未知')
        sender.reply(f"====扫码支付====\n📱 手机号: {first_phone}{f' 等{len(account_ids)}个账号' if len(account_ids) > 1 else ''}\n⏰ 时长: {months}月\n💰 总金额: ¥{total_price}\n=================\n请扫描下方二维码支付\n回复q取消支付")
        sender.replyImage(zsm)
        payment_result = sender.waitPay(timeout=600000, exitcode='q')
        if payment_result is None:
            sender.reply("⏰ 支付超时\n请重新发起支付操作")
            return False
        if payment_result == 'q':
            sender.reply("❌ 支付已取消")
            return False
        
        payment_info = extract_payment_info(payment_result)
        payment_status = verify_payment(payment_info, total_price)
        if payment_status != "success":
            if payment_status == "canceled":
                sender.reply("❌ 支付已取消")
            elif payment_status == "insufficient":
                sender.reply(f"❌ 支付金额不足\n💰 需要: ¥{total_price}\n💰 实际: ¥{payment_info.get('money', 0)}")
            else:
                sender.reply("❌ 支付验证失败")
            return False
        
        # 批量授权（每个账号独立计算到期时间）
        panel_success_count = 0
        pn = get_panel_name(config)
        for account_id in account_ids:
            # 计算新的到期时间（在原有基础上累加）
            auth_status = user_accounts[account_id].get('auth_status', {})
            current_expire = auth_status.get('expire_time', '')
            if current_expire and auth_status.get('is_authorized', False):
                try:
                    base_date = datetime.strptime(current_expire, '%Y-%m-%d').date()
                    if base_date > datetime.now().date():
                        expire_date = base_date + timedelta(days=30 * months)
                    else:
                        expire_date = datetime.now().date() + timedelta(days=30 * months)
                except:
                    expire_date = datetime.now().date() + timedelta(days=30 * months)
            else:
                expire_date = datetime.now().date() + timedelta(days=30 * months)

            user_accounts[account_id]['auth_status'] = {"is_authorized": True, "expire_time": str(expire_date)}
            phone = user_accounts[account_id].get('phone', '')
            if sync_to_panel(account_id, phone, str(expire_date), config):
                panel_success_count += 1
        save_user_accounts(user_accounts)

        panel_msg = f"\n🔄 {pn}推送: {panel_success_count}/{len(account_ids)}个" if is_panel_configured(config) else ""
        sender.reply(f"✅ 支付成功！\n📱 账号数: {len(account_ids)}\n⏰ 时长: {months}月\n💰 金额: ¥{total_price}{panel_msg}")
        return True
    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False

def _batch_coin_only(account_ids: list, months: int, total_coin: Decimal, user_accounts: dict, user_coin: Decimal, config: dict) -> bool:
    """多个账号纯积分支付（优化版）"""
    try:
        if user_coin < total_coin:
            sender.reply(f"❌ 积分不足！\n🎟️ 需要: {total_coin}积分\n💰 当前: {user_coin}积分\n请「联系管理员」充值积分")
            return False
        
        # 获取第一个账号的手机号
        first_phone = user_accounts[account_ids[0]].get('phone', '未知')
        confirm_msg = f"⚠️ 确认使用积分支付吗？\n📱 手机号: {first_phone}{f' 等{len(account_ids)}个账号' if len(account_ids) > 1 else ''}\n⏰ 时长: {months}月\n📊 扣除: {total_coin}积分\n📈 剩余: {user_coin - total_coin}积分\n------------------\n回复 [Y] 确认支付\n回复 [N] 取消"
        sender.reply(confirm_msg)
        confirm = sender.listen(60000)
        if not confirm:
            sender.reply("感谢使用！")
            return False
        confirm = confirm.strip().lower()
        if confirm != 'y':
            sender.reply("✅ 已取消")
            return False
        
        # 扣除积分
        remaining_coin = user_coin - total_coin
        middleware.bucketSet('dd_sign_points', userid, str(remaining_coin))
        
        # 批量授权（每个账号独立计算到期时间）
        panel_success_count = 0
        pn = get_panel_name(config)
        for account_id in account_ids:
            # 计算新的到期时间（在原有基础上累加）
            auth_status = user_accounts[account_id].get('auth_status', {})
            current_expire = auth_status.get('expire_time', '')
            if current_expire and auth_status.get('is_authorized', False):
                try:
                    base_date = datetime.strptime(current_expire, '%Y-%m-%d').date()
                    if base_date > datetime.now().date():
                        expire_date = base_date + timedelta(days=30 * months)
                    else:
                        expire_date = datetime.now().date() + timedelta(days=30 * months)
                except:
                    expire_date = datetime.now().date() + timedelta(days=30 * months)
            else:
                expire_date = datetime.now().date() + timedelta(days=30 * months)

            user_accounts[account_id]['auth_status'] = {"is_authorized": True, "expire_time": str(expire_date)}
            phone = user_accounts[account_id].get('phone', '')
            if sync_to_panel(account_id, phone, str(expire_date), config):
                panel_success_count += 1
        save_user_accounts(user_accounts)

        panel_msg = f"\n🔄 {pn}推送: {panel_success_count}/{len(account_ids)}个" if is_panel_configured(config) else ""
        sender.reply(f"✅ 积分支付成功！\n📱 账号数: {len(account_ids)}\n⏰ 时长: {months}月\n🎟️ 扣除: {total_coin}积分\n💰 剩余: {remaining_coin}积分{panel_msg}")
        return True
    except Exception as e:
        sender.reply(f"❌ 积分支付异常: {str(e)}")
        return False


def get_ql_token(host: str, client_id: str, client_secret: str) -> str:
    """获取青龙访问令牌（修复版 - 使用GET请求）"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        print(f"[DEBUG] 请求青龙token: {url[:80]}...")
        r = requests.get(url, timeout=10, verify=False)
        print(f"[DEBUG] Token响应: status={r.status_code}")
        if r.status_code == 200:
            result = r.json()
            print(f"[DEBUG] Token结果: code={result.get('code')}, message={result.get('message', 'None')}")
            token = result.get('data', {}).get('token', '')
            if token:
                print(f"[SUCCESS] 获取token成功: {token[:20]}...")
                return token
            else:
                print(f"[ERROR] Token为空: {result}")
        else:
            print(f"[ERROR] Token请求失败: HTTP {r.status_code}, body={r.text[:200]}")
    except Exception as e:
        print(f"[ERROR] 获取token异常: {str(e)}")
    return ""

def delete_from_qinglong(phone: str, ql_config: str, ql_envname: str) -> bool:
    """从青龙面板删除指定手机号的变量"""
    if not ql_config or not ql_envname or not phone:
        return False
    try:
        configs = ql_config.split('丨') if '丨' in ql_config else ql_config.split('|')
        if len(configs) < 3:
            print(f"[ERROR] 青龙配置格式错误")
            return False
        host, client_id, client_secret = configs[0].strip(), configs[1].strip(), configs[2].strip()
        ql_token = get_ql_token(host, client_id, client_secret)
        if not ql_token:
            print(f"[ERROR] 获取青龙token失败")
            return False
        headers = {'Authorization': f'Bearer {ql_token}', 'Content-Type': 'application/json'}
        # 查询包含该手机号的变量
        envs_r = requests.get(f'{host}/open/envs', headers=headers, params={'searchValue': ql_envname}, timeout=10, verify=False)
        if envs_r.status_code != 200:
            print(f"[ERROR] 查询青龙变量失败: HTTP {envs_r.status_code}")
            return False
        envs = envs_r.json().get('data', [])
        deleted = False
        for env in envs:
            if env.get('name') == ql_envname and phone in str(env.get('remarks', '')):
                env_id = env.get('_id') or env.get('id')
                if env_id:
                    try:
                        del_r = requests.delete(f'{host}/open/envs', headers=headers, json=[env_id], timeout=10, verify=False)
                        if del_r.status_code == 200:
                            print(f"[SUCCESS] 删除青龙变量成功: phone={phone}, id={env_id}")
                            deleted = True
                        else:
                            print(f"[ERROR] 删除青龙变量失败: {del_r.text}")
                    except Exception as e:
                        print(f"[ERROR] 删除青龙变量异常: {str(e)}")
        return deleted
    except Exception as e:
        print(f"[ERROR] 删除青龙变量异常: {str(e)}")
        return False

def push_to_qinglong(account_id: str, phone: str, expire_date: str, ql_config: str, ql_envname: str, user_id: str = None) -> bool:
    """推送账号信息到青龙面板（增强调试版）"""
    if not ql_config or not ql_envname:
        print(f"[ERROR] 青龙配置为空: ql_config={bool(ql_config)}, ql_envname={ql_envname}")
        return False
    try:
        user_accounts = get_user_accounts(user_id)
        if account_id not in user_accounts:
            print(f"[ERROR] 账号ID不存在: {account_id}")
            return False
        
        account = user_accounts[account_id]
        env_value = account.get('data', '')
        print(f"[DEBUG] 账号数据: account_id={account_id}, phone={phone}")
        print(f"[DEBUG] env_value={env_value[:50] if env_value else 'None'}...")
        
        if not env_value or '#' not in env_value:
            print(f"[ERROR] env_value格式错误: {env_value}")
            return False
        
        # 解析青龙配置（支持中英文分隔符）
        configs = ql_config.split('丨') if '丨' in ql_config else ql_config.split('|')
        print(f"[DEBUG] 解析青龙配置: 分段数={len(configs)}")
        if len(configs) < 3:
            print(f"[ERROR] 青龙配置格式错误，需要3段，实际{len(configs)}段")
            return False
        
        host, client_id, client_secret = configs[0].strip(), configs[1].strip(), configs[2].strip()
        print(f"[DEBUG] 青龙地址: {host}")
        print(f"[DEBUG] ClientID: {client_id[:10]}...")
        
        # 获取青龙token
        ql_token = get_ql_token(host, client_id, client_secret)
        if not ql_token:
            print(f"[ERROR] 获取青龙token失败")
            return False
        print(f"[DEBUG] 获取token成功: {ql_token[:20]}...")
        
        headers = {'Authorization': f'Bearer {ql_token}', 'Content-Type': 'application/json'}
        
        # 查询已存在的变量
        try:
            print(f"[DEBUG] 查询已存在变量: searchValue={ql_envname}")
            envs_r = requests.get(f'{host}/open/envs', headers=headers, params={'searchValue': ql_envname}, timeout=10, verify=False)
            print(f"[DEBUG] 查询响应: status={envs_r.status_code}")
            if envs_r.status_code == 200:
                envs = envs_r.json().get('data', [])
                print(f"[DEBUG] 找到{len(envs)}个变量")
                for env in envs:
                    if env.get('name') == ql_envname and phone in str(env.get('remarks', '')):
                        env_id = env.get('_id') or env.get('id')
                        if env_id:
                            try:
                                del_r = requests.delete(f'{host}/open/envs', headers=headers, json=[env_id], timeout=10, verify=False)
                                print(f"[INFO] 删除旧变量: id={env_id}, status={del_r.status_code}")
                            except Exception as del_err:
                                print(f"[WARNING] 删除旧变量失败: {del_err}")
        except Exception as query_err:
            print(f"[WARNING] 查询变量失败: {query_err}")
        
        # 添加新变量
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        remarks = f"捷停车:{phone}|用户:{userid}|手机:{masked_phone}|到期:{expire_date}|捷停车管理"
        data = [{'name': ql_envname, 'value': env_value, 'remarks': remarks}]
        
        print(f"[DEBUG] 添加新变量: name={ql_envname}, value长度={len(env_value)}")
        add_r = requests.post(f'{host}/open/envs', headers=headers, json=data, timeout=10, verify=False)
        print(f"[DEBUG] 添加响应: status={add_r.status_code}")
        
        if add_r.status_code != 200:
            print(f"[ERROR] 添加变量失败: HTTP {add_r.status_code}, body={add_r.text[:200]}")
            return False
        
        result = add_r.json()
        print(f"[DEBUG] 添加结果: code={result.get('code')}, message={result.get('message', 'None')}")
        
        if result.get('code') != 200:
            print(f"[ERROR] 添加变量失败: {result.get('message', '未知错误')}")
            return False
        
        # 启用变量
        new_ids = []
        for item in result.get('data', []):
            new_id = item.get('_id') or item.get('id')
            if new_id:
                new_ids.append(new_id)
        
        print(f"[DEBUG] 准备启用变量: ids={new_ids}")
        if new_ids:
            try:
                enable_r = requests.put(f'{host}/open/envs/enable', headers=headers, json=new_ids, timeout=10, verify=False)
                print(f"[INFO] 启用变量: status={enable_r.status_code}, ids={new_ids}")
            except Exception as enable_err:
                print(f"[WARNING] 启用变量失败: {enable_err}")
        
        print(f"[SUCCESS] 推送青龙成功: {phone}")
        return True
    except Exception as e:
        import traceback
        print(f"[ERROR] 推送青龙异常: {str(e)}")
        print(f"[ERROR] 异常堆栈: {traceback.format_exc()}")
        return False

def parse_ql_token(ql_token_value: str) -> dict:
    """解析青龙 JT_TOKEN 环境变量，格式: user_id#token"""
    try:
        parts = ql_token_value.split('#')
        if len(parts) >= 2:
            return {'user_id': parts[0], 'token': parts[1]}
    except:
        pass
    return {}

# ===== 呆呆面板封装 =====

def get_daidai_client(config: dict):
    """获取呆呆面板客户端"""
    if DadaiPanelClient is None: return None
    daidai_config = config.get('daidai_config', '')
    if not daidai_config: return None
    ql_envname = config.get('ql_envname', 'JT_TOKEN')
    daidai_group = config.get('daidai_group', PROJECT_NAME)
    try:
        client = DadaiPanelClient(ql_envname, daidai_config, project_name=PROJECT_NAME)
        return client if client.is_configured() else None
    except:
        return None

def push_to_daidai(account_id: str, phone: str, expire_date: str, config: dict, user_id: str = None) -> bool:
    """推送账号信息到呆呆面板"""
    client = get_daidai_client(config)
    if not client: return False
    try:
        user_accounts = get_user_accounts(user_id)
        if account_id not in user_accounts: return False
        account = user_accounts[account_id]
        env_value = account.get('data', '')
        if not env_value or '#' not in env_value: return False
        remarks = f"捷停车:{phone}|用户:{userid}|到期:{expire_date}"
        return client.update_env(username=phone, env_value=env_value, remark=remarks)
    except:
        return False

def delete_from_daidai(phone: str, config: dict) -> bool:
    """从呆呆面板删除指定手机号的变量"""
    client = get_daidai_client(config)
    if not client: return False
    try:
        return client.delete_env(phone)
    except:
        return False

def sync_to_panel(account_id: str, phone: str, expire_date: str, config: dict, user_id: str = None) -> bool:
    """根据 use_daidai 开关推送到对应面板（二选一）"""
    if config.get('use_daidai'):
        return push_to_daidai(account_id, phone, expire_date, config, user_id)
    ql_config = config.get('ql_config', '')
    ql_envname = config.get('ql_envname', 'JT_TOKEN')
    if ql_config:
        return push_to_qinglong(account_id, phone, expire_date, ql_config, ql_envname, user_id)
    return False

def delete_from_panel(phone: str, config: dict) -> bool:
    """根据 use_daidai 开关从对应面板删除（二选一）"""
    if config.get('use_daidai'):
        return delete_from_daidai(phone, config)
    ql_config = config.get('ql_config', '')
    ql_envname = config.get('ql_envname', 'JT_TOKEN')
    if ql_config:
        return delete_from_qinglong(phone, ql_config, ql_envname)
    return False

def get_panel_name(config: dict) -> str:
    """返回当前面板名称"""
    return "呆呆" if config.get('use_daidai') else "青龙"

def is_panel_configured(config: dict) -> bool:
    """检查当前选中的面板是否已配置"""
    if config.get('use_daidai'):
        return bool(config.get('daidai_config'))
    return bool(config.get('ql_config'))

# ===== 码支付核心函数 =====

def _generate_qrcode(url: str) -> str:
    """生成二维码图片URL"""
    if HAS_HUAWEI_LIB and generate_qrcode_url:
        try:
            return generate_qrcode_url(url)
        except:
            pass
    try:
        encoded_url = quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except:
        return None

def ma_pay_sign(params: dict, key: str) -> str:
    """码支付签名"""
    sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
    sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
    return hashlib.md5((sign_str + key).encode('utf-8')).hexdigest().lower()

def ma_pay_create_order(config: dict, amount: float, out_trade_no: str, name: str, pay_type: str) -> tuple:
    """创建码支付订单"""
    if HAS_HUAWEI_LIB and MaPayClient:
        try:
            client = MaPayClient()
            if client.is_configured():
                result = client.create_order(amount=amount, pay_type=pay_type, out_trade_no=out_trade_no, subject=name)
                if result and result.get('code') == 1:
                    return True, result, result.get('msg', '成功')
                return False, None, result.get('msg', '创建订单失败') if result else '创建订单失败'
        except:
            pass
    # 回退到内置实现
    if not (config.get('ma_pay_gateway') and config.get('ma_pay_pid') and config.get('ma_pay_key')):
        return False, None, "码支付配置不完整"
    params = {'pid': config['ma_pay_pid'], 'type': pay_type, 'out_trade_no': out_trade_no, 'name': name, 'money': str(amount)}
    if config.get('ma_pay_notify_url'): params['notify_url'] = config['ma_pay_notify_url']
    params = {k: v for k, v in params.items() if v}
    params['sign'] = ma_pay_sign(params, config['ma_pay_key'])
    params['sign_type'] = 'MD5'
    gateway = config['ma_pay_gateway'].rstrip('/') + '/mapi.php'
    try:
        r = requests.post(gateway, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}, timeout=10, verify=False)
        if r.status_code != 200: return False, None, f"HTTP错误: {r.status_code}"
        result = r.json()
        if result.get('code') == 1: return True, result, result.get('msg', '成功')
        return False, None, result.get('msg', '创建订单失败')
    except Exception as e: return False, None, str(e)

def ma_pay_query_order(config: dict, out_trade_no: str) -> tuple:
    """查询码支付订单状态"""
    if HAS_HUAWEI_LIB and MaPayClient:
        try:
            client = MaPayClient()
            if client.is_configured():
                result = client.check_order(out_trade_no)
                if result and result.get('code') == 1:
                    if result.get('status') == 1: return True, result, "支付成功"
                    return True, result, "订单未支付"
                return False, None, result.get('msg', '查询失败') if result else '查询失败'
        except:
            pass
    # 回退到内置实现
    gateway = config['ma_pay_gateway'].rstrip('/')
    if '/xpay/epay/api.php' not in gateway: gateway = f"{gateway}/xpay/epay/api.php"
    params = {'act': 'order', 'pid': config['ma_pay_pid'], 'key': config['ma_pay_key'], 'out_trade_no': out_trade_no}
    try:
        r = requests.get(gateway, params=params, timeout=10, verify=False)
        if r.status_code != 200: return False, None, f"HTTP错误: {r.status_code}"
        result = r.json()
        if result.get('code') == 1:
            if result.get('status') == 1: return True, result, "支付成功"
            return True, result, "订单未支付"
        return False, None, result.get('msg', '查询失败')
    except Exception as e: return False, None, str(e)

def poll_ma_pay_status(config: dict, out_trade_no: str, max_tries: int = 30) -> tuple:
    """轮询码支付订单状态"""
    for _ in range(max_tries):
        success, data, msg = ma_pay_query_order(config, out_trade_no)
        if success and isinstance(data, dict) and data.get('status') == 1:
            return True, "支付成功", data
        result = sender.listen(5000)
        if result and result.strip().lower() == 'q': return False, "用户取消", None
    return False, "查询超时", None

def alipay_direct_flow(account_ids: list, months: int, total_price: Decimal, config: dict, user_accounts: dict) -> bool:
    """支付宝直接支付流程（码支付）"""
    if not (config.get('ma_pay_gateway') and config.get('ma_pay_pid') and config.get('ma_pay_key')):
        sender.reply('❌ 码支付配置不完整'); return False
    first_phone = user_accounts[account_ids[0]].get('phone', '未知')
    phone_display = (first_phone[:3] + "****" + first_phone[-4:]) if len(first_phone) == 11 else first_phone
    if len(account_ids) > 1: phone_display += f" 等{len(account_ids)}个"
    out_trade_no = f"JTC{int(time.time())}{userid[-8:]}"
    success, result, msg = ma_pay_create_order(config, float(total_price), out_trade_no, f"捷停车-{phone_display}-{months}月授权", 'alipay')
    if not success: sender.reply(f'❌ 创建订单失败: {msg}'); return False
    payurl = result.get('payurl', '')
    if not payurl: sender.reply('❌ 获取支付链接失败'); return False
    qrcode_url = _generate_qrcode(payurl)
    if qrcode_url:
        sender.reply(f'=====支付宝支付=====\n📱 {phone_display}\n⏰ {months}月\n💰 ¥{total_price}\n请使用【支付宝】扫码支付，输入q取消')
        sender.replyImage(qrcode_url)
    else:
        sender.reply(f"请使用【支付宝】打开链接支付：\n{payurl}\n输入q取消")
    is_paid, msg, _ = poll_ma_pay_status(config, out_trade_no)
    if not is_paid:
        sender.reply(f"❌ 支付未完成: {msg}"); return False
    return True

def extract_payment_info(payment_result: str) -> dict:
    """提取支付信息（参考顺易充实现）"""
    payment_info = {
        "money": None,
        "time": "",
        "from": "",
        "status": -1,
        "is_canceled": False,
        "raw_message": ""
    }
    if isinstance(payment_result, dict):
        payment_info["raw_message"] = str(payment_result)
    else:
        payment_info["raw_message"] = str(payment_result) if payment_result is not None else ""
        try:
            payment_result = json.loads(payment_result)
            payment_info["raw_message"] = str(payment_result)
        except:
            pass
    
    cancel_patterns = [
        "<status>2</status>", "status=2", "status\":2",
        "支付已取消", "取消支付", "已取消", "cancel", "cancelled"
    ]
    for pattern in cancel_patterns:
        if pattern.lower() in payment_info["raw_message"].lower():
            payment_info["is_canceled"] = True
            payment_info["status"] = 2
            break
    
    try:
        if isinstance(payment_result, dict):
            if payment_result.get('Type') == 'pay':
                payment_info["money"] = float(payment_result.get('Money', 0))
                payment_info["time"] = payment_result.get('Time', '')
                payment_info["from"] = payment_result.get('FromName', '')
                if not payment_info["is_canceled"]:
                    raw_status = payment_result.get('status')
                    if raw_status is not None:
                        payment_info["status"] = int(raw_status)
                        if payment_info["status"] == 2:
                            payment_info["is_canceled"] = True
                    else:
                        payment_info["status"] = 1
            else:
                raw_status = payment_result.get('status')
                if raw_status is not None:
                    payment_info["status"] = int(raw_status)
                    if payment_info["status"] == 2:
                        payment_info["is_canceled"] = True
                if payment_result.get('Money') is not None:
                    payment_info["money"] = float(payment_result.get('Money', 0))
                elif payment_result.get('money') is not None:
                    payment_info["money"] = float(payment_result.get('money', 0))
                payment_info["time"] = payment_result.get('Time', '') or payment_result.get('time', '')
                payment_info["from"] = payment_result.get('FromName', '') or payment_result.get('from_name', '')
        elif isinstance(payment_info["raw_message"], str) and "<status>" in payment_info["raw_message"]:
            try:
                status_str = payment_info["raw_message"].split("<status>")[1].split("</status>")[0].strip()
                payment_info["status"] = int(status_str)
                if payment_info["status"] == 2:
                    payment_info["is_canceled"] = True
                if "<fee>" in payment_info["raw_message"]:
                    fee_str = payment_info["raw_message"].split("<fee>")[1].split("</fee>")[0].strip()
                    payment_info["money"] = float(fee_str) / 100
                if "<timestamp>" in payment_info["raw_message"]:
                    timestamp_str = payment_info["raw_message"].split("<timestamp>")[1].split("</timestamp>")[0].strip()
                    payment_info["time"] = datetime.fromtimestamp(int(timestamp_str)).strftime("%Y-%m-%d %H:%M:%S")
                if "<displayname>" in payment_info["raw_message"]:
                    display_name = payment_info["raw_message"].split("<displayname>")[1].split("</displayname>")[0].strip()
                    payment_info["from"] = display_name.replace("<![CDATA[", "").replace("]]>", "")
            except:
                pass
        elif isinstance(payment_info["raw_message"], str) and "收款金额￥" in payment_info["raw_message"]:
            try:
                amount_str = payment_info["raw_message"].split("收款金额￥")[1].split("\n")[0]
                payment_info["money"] = float(amount_str)
                if "到账时间" in payment_info["raw_message"]:
                    time_str = payment_info["raw_message"].split("到账时间")[1].split("\n")[0].strip()
                    payment_info["time"] = time_str
                payment_info["status"] = 1
            except:
                pass
    except Exception:
        pass
    return payment_info

def verify_payment(payment_info: dict, expected_amount: Decimal) -> str:
    """验证支付状态（参考顺易充实现）"""
    if payment_info["money"] is None:
        return "failed"
    if payment_info["money"] == 5.37:
        return "canceled"
    if payment_info["is_canceled"] or payment_info["status"] == 2:
        return "canceled"
    if abs(Decimal(str(payment_info["money"])) - expected_amount) > Decimal("0.01"):
        return "insufficient"
    if payment_info["status"] == 1 or (payment_info["status"] == -1 and not payment_info["is_canceled"]):
        return "success"
    return "failed"

def process_payment_direct(account_id: str, phone: str, months: int, total_price: Decimal, zsm: str, user_accounts: dict, config: dict) -> bool:
    """直接支付（已知月数和总价）"""
    try:
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        sender.reply(f"====微信扫码支付====\n📱 账号: {masked_phone}\n⏰ 时长: {months}月\n💰 金额: ¥{total_price}\n=================\n请扫描下方二维码支付\n回复q取消支付")
        sender.replyImage(zsm)
        payment_result = sender.waitPay(timeout=600000, exitcode='q')
        if payment_result is None:
            sender.reply("⏰ 支付超时\n请重新发起支付操作")
            return False
        if payment_result == 'q':
            sender.reply("❌ 支付已取消")
            return False
        
        payment_info = extract_payment_info(payment_result)
        payment_status = verify_payment(payment_info, total_price)
        if payment_status == "success":
            # 计算新的到期时间（在原有基础上累加）
            auth_status = user_accounts[account_id].get('auth_status', {})
            current_expire = auth_status.get('expire_time', '')
            if current_expire and auth_status.get('is_authorized', False):
                try:
                    base_date = datetime.strptime(current_expire, '%Y-%m-%d').date()
                    if base_date > datetime.now().date():
                        expire_date = base_date + timedelta(days=30 * months)
                    else:
                        expire_date = datetime.now().date() + timedelta(days=30 * months)
                except:
                    expire_date = datetime.now().date() + timedelta(days=30 * months)
            else:
                expire_date = datetime.now().date() + timedelta(days=30 * months)
            
            user_accounts[account_id]['auth_status'] = {"is_authorized": True, "expire_time": str(expire_date)}
            panel_ok = sync_to_panel(account_id, phone, str(expire_date), config)
            save_user_accounts(user_accounts)
            pn = get_panel_name(config)
            panel_msg = f"\n🔄 {pn}推送: 成功" if panel_ok else (f"\n⚠️ {pn}推送: 失败" if is_panel_configured(config) else "")
            sender.reply(f"✅ 支付成功！\n📱 账号: {masked_phone}\n⏰ 时长: {months}月\n💰 金额: ¥{total_price}\n📅 有效期至: {expire_date}{panel_msg}\n\n您可以发送「捷停车查询」查看账号状态")
            return True
        elif payment_status == "canceled":
            sender.reply("❌ 支付已取消")
            return False
        elif payment_status == "insufficient":
            sender.reply(f"❌ 支付金额不足\n💰 需要: ¥{total_price}\n💰 实际: ¥{payment_info.get('money', 0)}")
            return False
        else:
            sender.reply("❌ 支付验证失败")
            return False
    except Exception as e:
        sender.reply(f"❌ 支付异常: {str(e)}")
        return False

def process_hybrid_payment(account_id: str, phone: str, price: Decimal, coin_price: str, zsm: str, user_accounts: dict, config: dict) -> bool:
    """混合支付：部分扫码支付 + 部分积分兑换"""
    try:
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        user_coin = Decimal(middleware.bucketGet('dd_sign_points', userid) or '0')
        sender.reply("请输入授权月数（1-12）：")
        months_str = sender.listen(60000)
        if not months_str:
            sender.reply("感谢使用！")
            return False
        months_str = months_str.strip()
        if not months_str:
            sender.reply("❌ 输入超时")
            return False
        if months_str == 'q':
            sender.reply("✅ 已取消")
            return False
        try:
            months = int(months_str)
            if not (1 <= months <= 12): raise ValueError()
        except:
            sender.reply("❌ 无效的月数，请输入1-12之间的数字")
            return False
        
        total_price = price * months
        total_coin = Decimal(coin_price) * months
        sender.reply(f"====混合支付====\n📱 账号: {masked_phone}\n⏰ 时长: {months}月\n💰 总金额: ¥{total_price}\n🎟️ 总积分: {total_coin}积分\n💰 当前积分: {user_coin}\n=================\n请输入用积分支付的月数（0-{months}）：")
        coin_months_str = sender.listen(60000)
        if not coin_months_str:
            sender.reply("感谢使用！")
            return False
        coin_months_str = coin_months_str.strip()
        if not coin_months_str:
            sender.reply("❌ 输入超时")
            return False
        try:
            coin_months = int(coin_months_str)
            if not (0 <= coin_months <= months): raise ValueError()
        except:
            sender.reply("❌ 无效的月数")
            return False
        
        pay_months = months - coin_months
        pay_amount = price * pay_months
        coin_amount = Decimal(coin_price) * coin_months
        if user_coin < coin_amount:
            sender.reply(f"❌ 积分不足\n💰 需要: {coin_amount}积分\n💰 当前: {user_coin}积分")
            return False
        
        confirm_msg = f"====支付确认====\n📱 账号: {masked_phone}\n💳 扫码支付: ¥{pay_amount} ({pay_months}月)\n🎟️ 积分支付: {coin_amount}积分 ({coin_months}月)\n💰 剩余积分: {user_coin - coin_amount}\n=================\n回复'y'确认，其他取消："
        sender.reply(confirm_msg)
        confirm = sender.listen(60000)
        if not confirm:
            sender.reply("感谢使用！")
            return False
        confirm = confirm.strip().lower()
        if not confirm or confirm != 'y':
            sender.reply("✅ 已取消")
            return False
        
        if pay_months > 0:
            sender.reply(f"====扫码支付====\n💳 金额: ¥{pay_amount}\n⏰ 时长: {pay_months}月\n请使用微信扫码支付（q取消）")
            sender.replyImage(zsm)
            if sender.waitPay("q", 120000) == 'q':
                sender.reply("✅ 已取消")
                return False
        
        remaining_coin = user_coin - coin_amount
        middleware.bucketSet('dd_sign_points', userid, str(remaining_coin))
        expire_date = datetime.now().date() + timedelta(days=30 * months)
        user_accounts[account_id]['auth_status'] = {"is_authorized": True, "expire_time": str(expire_date)}
        sync_to_panel(account_id, phone, str(expire_date), config)
        save_user_accounts(user_accounts)
        sender.reply(f"✅ 授权成功！\n📱 账号: {masked_phone}\n💳 扫码: ¥{pay_amount} ({pay_months}月)\n🎟️ 积分: {coin_amount}积分 ({coin_months}月)\n📅 有效期至: {expire_date}\n💰 剩余积分: {remaining_coin}\n\n您可以发送「捷停车查询」查看账号状态")
        return True
    except Exception as e:
        sender.reply(f"❌ 混合支付异常: {str(e)}")
        return False

def process_coin_auth_direct(account_id: str, phone: str, months: int, total_coin: Decimal, user_accounts: dict, config: dict) -> bool:
    """直接积分支付（已知月数和总积分）"""
    try:
        user_coin = Decimal(middleware.bucketGet('dd_sign_points', userid) or '0')
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        
        if user_coin < total_coin:
            sender.reply(f"❌ 积分不足！\n🎟️ 需要: {total_coin}积分\n💰 当前: {user_coin}积分\n请「联系管理员」充值积分")
            return False
        
        confirm_msg = f"⚠️ 确认使用积分支付吗？\n📱 账号: {masked_phone}\n⏰ 时长: {months}月\n📊 扣除: {total_coin}积分\n📈 剩余: {user_coin - total_coin}积分\n------------------\n回复 [Y] 确认支付\n回复 [N] 取消"
        sender.reply(confirm_msg)
        confirm = sender.listen(60000)
        if not confirm:
            sender.reply("感谢使用！")
            return False
        confirm = confirm.strip().lower()
        if confirm != 'y':
            sender.reply("✅ 积分支付已取消")
            return False
        
        remaining_coin = user_coin - total_coin
        middleware.bucketSet('dd_sign_points', userid, str(remaining_coin))
        
        # 计算新的到期时间（在原有基础上累加）
        auth_status = user_accounts[account_id].get('auth_status', {})
        current_expire = auth_status.get('expire_time', '')
        if current_expire and auth_status.get('is_authorized', False):
            try:
                base_date = datetime.strptime(current_expire, '%Y-%m-%d').date()
                if base_date > datetime.now().date():
                    expire_date = base_date + timedelta(days=30 * months)
                else:
                    expire_date = datetime.now().date() + timedelta(days=30 * months)
            except:
                expire_date = datetime.now().date() + timedelta(days=30 * months)
        else:
            expire_date = datetime.now().date() + timedelta(days=30 * months)
        
        user_accounts[account_id]['auth_status'] = {"is_authorized": True, "expire_time": str(expire_date)}
        panel_ok = sync_to_panel(account_id, phone, str(expire_date), config)
        save_user_accounts(user_accounts)
        pn = get_panel_name(config)
        panel_msg = f"\n🔄 {pn}推送: 成功" if panel_ok else (f"\n⚠️ {pn}推送: 失败" if is_panel_configured(config) else "")
        sender.reply(f"✅ 积分支付成功！\n📱 账号: {masked_phone}\n⏰ 时长: {months}月\n🎟️ 扣除: {total_coin}积分\n💰 剩余: {remaining_coin}积分\n📅 有效期至: {expire_date}{panel_msg}")
        return True
    except Exception as e:
        sender.reply(f"❌ 兑换失败: {str(e)}")
        return False

def _single_alipay_flow(account_id: str, phone: str, months: int, total_price: Decimal, user_accounts: dict, config: dict) -> bool:
    """单个账号支付宝支付流程"""
    try:
        if not alipay_direct_flow([account_id], months, total_price, config, user_accounts):
            return False
        # 支付成功，执行授权
        masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
        auth_status = user_accounts[account_id].get('auth_status', {})
        current_expire = auth_status.get('expire_time', '')
        if current_expire and auth_status.get('is_authorized', False):
            try:
                base_date = datetime.strptime(current_expire, '%Y-%m-%d').date()
                if base_date > datetime.now().date():
                    expire_date = base_date + timedelta(days=30 * months)
                else:
                    expire_date = datetime.now().date() + timedelta(days=30 * months)
            except:
                expire_date = datetime.now().date() + timedelta(days=30 * months)
        else:
            expire_date = datetime.now().date() + timedelta(days=30 * months)
        user_accounts[account_id]['auth_status'] = {"is_authorized": True, "expire_time": str(expire_date)}
        panel_ok = sync_to_panel(account_id, phone, str(expire_date), config)
        save_user_accounts(user_accounts)
        pn = get_panel_name(config)
        panel_msg = f"\n🔄 {pn}推送: 成功" if panel_ok else (f"\n⚠️ {pn}推送: 失败" if is_panel_configured(config) else "")
        sender.reply(f"✅ 支付宝支付成功！\n📱 账号: {masked_phone}\n⏰ 时长: {months}月\n💰 金额: ¥{total_price}\n📅 有效期至: {expire_date}{panel_msg}")
        return True
    except Exception as e:
        sender.reply(f"❌ 支付宝支付异常: {str(e)}")
        return False

def _batch_alipay_only(account_ids: list, months: int, total_price: Decimal, user_accounts: dict, config: dict) -> bool:
    """多个账号支付宝支付流程"""
    try:
        if not alipay_direct_flow(account_ids, months, total_price, config, user_accounts):
            return False
        # 支付成功，批量授权
        panel_success_count = 0
        pn = get_panel_name(config)
        for account_id in account_ids:
            auth_status = user_accounts[account_id].get('auth_status', {})
            current_expire = auth_status.get('expire_time', '')
            if current_expire and auth_status.get('is_authorized', False):
                try:
                    base_date = datetime.strptime(current_expire, '%Y-%m-%d').date()
                    if base_date > datetime.now().date():
                        expire_date = base_date + timedelta(days=30 * months)
                    else:
                        expire_date = datetime.now().date() + timedelta(days=30 * months)
                except:
                    expire_date = datetime.now().date() + timedelta(days=30 * months)
            else:
                expire_date = datetime.now().date() + timedelta(days=30 * months)
            user_accounts[account_id]['auth_status'] = {"is_authorized": True, "expire_time": str(expire_date)}
            phone = user_accounts[account_id].get('phone', '')
            if sync_to_panel(account_id, phone, str(expire_date), config):
                panel_success_count += 1
        save_user_accounts(user_accounts)
        panel_msg = f"\n🔄 {pn}推送: {panel_success_count}/{len(account_ids)}个" if is_panel_configured(config) else ""
        sender.reply(f"✅ 支付宝支付成功！\n📱 账号数: {len(account_ids)}\n⏰ 时长: {months}月\n💰 金额: ¥{total_price}{panel_msg}")
        return True
    except Exception as e:
        sender.reply(f"❌ 支付宝批量支付异常: {str(e)}")
        return False

def upload_all_to_qinglong() -> bool:
    """上传所有已授权用户数据到面板（根据开关选择青龙/呆呆）"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有管理员权限！")
        return False
    config = get_config()
    pn = get_panel_name(config)
    if not is_panel_configured(config):
        sender.reply(f"❌ 未配置{pn}面板！\n请先配置对应面板信息")
        return False

    use_daidai = config.get('use_daidai', False)

    # 呆呆面板模式
    if use_daidai:
        sender.reply("🔄 正在同步数据到呆呆面板...")
        try: users = middleware.bucketAllKeys(bucket=BUCKET_ACCOUNTS) or []
        except: users = []
        success_count, skip_count = 0, 0
        for uid in users:
            ua = get_user_accounts(uid)
            for aid, acc in ua.items():
                auth_st = acc.get('auth_status', {})
                if not auth_st.get('is_authorized', False): skip_count += 1; continue
                et = auth_st.get('expire_time', '')
                if et:
                    try:
                        if datetime.strptime(et, '%Y-%m-%d').date() < datetime.now().date(): skip_count += 1; continue
                    except: pass
                ev = acc.get('data', '')
                if not ev or '#' not in ev: skip_count += 1; continue
                ph = acc.get('phone', '')
                if sync_to_panel(aid, ph, et, config): success_count += 1
        sender.reply(f"✅ 呆呆同步完成！\n🔄 推送成功: {success_count}个\n⏭️ 跳过: {skip_count}个")
        return True

    # 青龙面板模式
    ql_config = config.get('ql_config', '')
    ql_envname = config.get('ql_envname', 'JT_TOKEN')
    sender.reply("🔄 正在获取青龙面板变量...")
    configs = ql_config.split('丨') if '丨' in ql_config else ql_config.split('|')
    if len(configs) < 3: sender.reply("❌ 青龙配置格式错误"); return False
    host, client_id, client_secret = configs[0].strip(), configs[1].strip(), configs[2].strip()
    ql_token = get_ql_token(host, client_id, client_secret)
    if not ql_token: sender.reply("❌ 获取青龙token失败"); return False
    headers = {'Authorization': f'Bearer {ql_token}', 'Content-Type': 'application/json'}
    try:
        envs_r = requests.get(f'{host}/open/envs', headers=headers, params={'searchValue': ql_envname}, timeout=10, verify=False)
        if envs_r.status_code != 200: sender.reply(f"❌ 获取青龙变量失败: HTTP {envs_r.status_code}"); return False
        ql_envs = [env for env in envs_r.json().get('data', []) if env.get('name') == ql_envname]
    except Exception as e: sender.reply(f"❌ 获取青龙变量异常: {e}"); return False
    ql_phones = {}
    for env in ql_envs:
        remarks = env.get('remarks', '')
        env_id = env.get('_id') or env.get('id')
        if '捷停车:' in remarks:
            phone = remarks.split('捷停车:')[1].split('|')[0].strip()
            if phone and env_id: ql_phones[phone] = env_id
    sender.reply(f"📊 青龙变量数: {len(ql_envs)}\n🔍 识别手机号: {len(ql_phones)}个\n🔄 正在匹配本地数据...")
    try: users = middleware.bucketAllKeys(bucket=BUCKET_ACCOUNTS) or []
    except: users = []
    update_count, add_count, skip_count, fail_count = 0, 0, 0, 0
    for user_id in users:
        user_accounts = get_user_accounts(user_id)
        for account_id, account in user_accounts.items():
            phone = account.get('phone', '')
            auth_status = account.get('auth_status', {})
            if not auth_status.get('is_authorized', False): skip_count += 1; continue
            expire_time = auth_status.get('expire_time', '')
            if expire_time:
                try:
                    if datetime.strptime(expire_time, '%Y-%m-%d').date() < datetime.now().date(): skip_count += 1; continue
                except: pass
            env_value = account.get('data', '')
            if not env_value or '#' not in env_value: skip_count += 1; continue
            masked_phone = phone[:3] + "****" + phone[-4:] if len(phone) == 11 else phone
            remarks = f"捷停车:{phone}|用户:{user_id}|手机:{masked_phone}|到期:{expire_time}|捷停车管理"
            if phone in ql_phones:
                try:
                    update_data = {'id': ql_phones[phone], 'name': ql_envname, 'value': env_value, 'remarks': remarks}
                    r = requests.put(f'{host}/open/envs', headers=headers, json=update_data, timeout=10, verify=False)
                    if r.status_code == 200 and r.json().get('code') == 200: update_count += 1
                    else: fail_count += 1
                except: fail_count += 1
            else:
                try:
                    add_data = [{'name': ql_envname, 'value': env_value, 'remarks': remarks}]
                    r = requests.post(f'{host}/open/envs', headers=headers, json=add_data, timeout=10, verify=False)
                    if r.status_code == 200 and r.json().get('code') == 200: add_count += 1
                    else: fail_count += 1
                except: fail_count += 1
    sender.reply(f"✅ 青龙同步完成！\n📊 原有变量: {len(ql_envs)}\n🔄 更新: {update_count}\n➕ 新增: {add_count}\n⏭️ 跳过: {skip_count}\n❌ 失败: {fail_count}")
    return True

def main():
    try:
        config = get_config()
        command = sender.getMessage()
        
        if command == "捷停车登录" or command == "登录捷停车":
            process_login(config)
        elif command == "捷停车查询":
            query_accounts()
        elif command == "捷停车管理":
            batch_manage(config)
        elif command == "捷停车授权":
            batch_auth(config)
        elif command == "捷停车清理":
            if not sender.isAdmin():
                sender.reply("❌ 您没有管理员权限！")
                return
            cleanup_expired_data()
        elif command == "捷停车上传":
            upload_all_to_qinglong()
        else:
            sender.reply("未知指令，请发送「捷停车管理」查看账号管理")
    except Exception as e:
        sender.reply(f"❌ 执行异常: {str(e)}")

if __name__ == "__main__":
    main()
