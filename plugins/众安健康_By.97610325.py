#[pin:true]
#[public:true]
# [rule: ^众安管理$]
# [rule: ^管理众安$]
# [rule: ^众安查询$]
# [rule: ^查询众安$]
# [rule: ^众安登录$]
# [rule: ^登录众安$]
# [rule: ^众安授权$]
# [rule: ^众安清理$]
# [rule: ^清理众安$]
# [cron: 32 7 * * *]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [version: 1.6]
# [admin: false]
# [author: 97610325]
# [price: 9.9]
# [title: 众安健康]
# [icon: https://nos.netease.com/ysf/82b362badc596b99e5c3ad437973a560.jpg]
# [description: 众安健康插件<br>指令：众安登录、众安管理、众安查询、众安清理<br>功能：账号托管、余额查询、签到任务、自动提现、付费授权，完美对接青龙面板,适配呆呆积分系统<br>5.9更新：修复众安查询问题<br>5.16更新：Token真实有效新检测]
import middleware
import time
import re
import random
import requests
import http.client
import json
from datetime import datetime, timedelta
from decimal import Decimal
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# HTTP头中文编码支持补丁
_original_putheader = http.client.HTTPConnection.putheader
def _patched_putheader(self, header, *values):
    encoded_values = []
    for value in values:
        if isinstance(value, str):
            try:
                value.encode('latin-1')
                encoded_values.append(value)
            except UnicodeEncodeError:
                encoded_values.append(value.encode('utf-8'))
        else:
            encoded_values.append(value)
    return _original_putheader(self, header, *encoded_values)
http.client.HTTPConnection.putheader = _patched_putheader

# [param: {"required":true,"key":"dd_zajk_config.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码的图片链接"}]
# [param: {"required":true,"key":"dd_zajk_config.Qinglong","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割，这个符号是中文的竖线(直接复制)"}]
# [param: {"required":true,"key":"dd_zajk_config.osname","bool":false,"placeholder":"必填项,例:zajk","name":"青龙变量名","desc":"青龙面板中众安健康脚本对应的环境变量名称"}]
# [param: {"required":true,"key":"dd_zajk_config.zajkVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"用户购买账号授权的月费，单位元"}]
# [param: {"required":true,"key":"dd_zajk_config.zajkcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要的积分（只能为整数不能为小数）"}]
# [param: {"required":true,"key":"dd_zajk_config.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否开启码支付系统，开启后会对接卡密系统的码支付配置"}]

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_zajk_user', key=userid)

# 全局变量
today_date = datetime.now().date()
today_time = str(today_date)

# 众安健康API配置
API_HOST = "ihealth.zhongan.com"
ACTIVITY_CODE = "ONA20220411001"
CHANNEL_CODE = "c20195660470001"

# 众安健康请求头模板
ZA_BASE_HEADERS = {
    "Host": API_HOST,
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.23(0x1800172f) NetType/WIFI Language/zh_CN",
    "Referer": "https://servicewechat.com/wxbac45cc1588a5a75/210/page-frame.html"
}


def clean_cookie(cookie):
    """清理cookie格式"""
    return cookie.strip('\'" ')


def parse_token_cookie(token_cookie_str):
    """解析Access-Token#Cookie格式，仅支持#分隔符"""
    token_cookie_str = token_cookie_str.strip()
    if '#' not in token_cookie_str:
        return None, None
    parts = token_cookie_str.split('#', 1)
    if len(parts) < 2:
        return None, None
    access_token = parts[0].strip()
    cookie = clean_cookie(parts[1].strip())
    return access_token, cookie


def za_get_headers(access_token, use_cookie=False, cookie=''):
    """生成众安健康请求头"""
    headers = ZA_BASE_HEADERS.copy()
    headers["Access-Token"] = access_token
    if use_cookie and cookie:
        headers["Cookie"] = cookie
        headers["Origin"] = f"https://{API_HOST}"
        headers["Accept-Language"] = "zh-cn"
        headers["User-Agent"] += " miniProgram/wxbac45cc1588a5a75"
    return headers

def getusercontent():
    """获取插件配置信息"""
    dd_zajk_osname = middleware.bucketGet('dd_zajk_config', 'osname') or 'zajk'
    dd_zajk_qlname = middleware.bucketGet('dd_zajk_config', 'Qinglong')
    dd_managecommand = middleware.bucketGet('dd_zajk_config', 'dd_managecommand') or '众安管理'
    dd_querycommand = middleware.bucketGet('dd_zajk_config', 'dd_querycommand') or '众安查询'
    dd_signcommand = middleware.bucketGet('dd_zajk_config', 'dd_signcommand') or '众安登录'
    
    randommanagecommand = dd_managecommand
    randomquerycommand = dd_querycommand
    randomsigncommand = dd_signcommand
    
    zajkVipmoney = Decimal(middleware.bucketGet('dd_zajk_config', 'zajkVipmoney') or '0')
    zajkcoin = int(middleware.bucketGet('dd_zajk_config', 'zajkcoin') or '0')
    
    return (dd_zajk_osname, dd_zajk_qlname, dd_managecommand, dd_querycommand,
            dd_signcommand, randommanagecommand, randomquerycommand, randomsigncommand, zajkVipmoney, zajkcoin)

def seekql():
    """连接并验证青龙配置"""
    try:
        if len(dd_zajk_qlname) == 0:
            sender.reply("""=======配置错误=======
❌ 未配置青龙信息
------------------
请在插件配置中填写:
Host丨ClientID丨ClientSecret
• 使用中文丨分隔
• 示例:
http://ql.example.com丨abcd1234丨efgh5678
====================""")
            exit(0)
            
        qllist = dd_zajk_qlname.split('丨')
        if len(qllist) != 3:
            sender.reply(f"""=======格式错误=======
❌ 青龙配置格式错误
------------------
当前格式: {dd_zajk_qlname}
正确格式:
青龙地址丨ClientID丨ClientSecret
====================""")
            exit(0)
            
        QLurl = qllist[0].strip()
        ClientID = qllist[1].strip()
        ClientSecret = qllist[2].strip()
        
        if not all([QLurl, ClientID, ClientSecret]):
            sender.reply("""=======参数错误=======
❌ 青龙配置参数不完整
------------------
请确保以下参数都已填写:
• 青龙面板地址(Host)
• 应用ID(ClientID)
• 应用密钥(ClientSecret)
====================""")
            exit(0)
            
        if not QLurl.startswith(('http://', 'https://')):
            sender.reply(f"""=======地址错误=======
❌ 青龙地址格式错误
------------------
当前地址: {QLurl}
正确格式:
• http://qinglong.example.com
• https://ql.example.com:5700
====================""")
            exit(0)
            
        try:
            qltoken = QLtoken(QLurl=QLurl, ClientID=ClientID, ClientSecret=ClientSecret)
            return QLurl, qltoken
        except Exception as e:
            raise Exception(f"获取Token失败: {str(e)}")
            
    except Exception as e:
        sender.reply(f"""=======网络错误=======
❌ 无法连接青龙面板
------------------
请检查:
1. 青龙面板是否运行
2. 网络是否正常
3. 配置是否正确
4. 错误信息: {str(e)}
------------------
当前配置:
• 地址: {QLurl if 'QLurl' in locals() else '未设置'}
• 应用ID: {ClientID[:4] + '****' if 'ClientID' in locals() else '未设置'}
====================""")
        exit(0)

def QLtoken(QLurl, ClientID, ClientSecret):
    """获取青龙token"""
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        response = requests.get(url)
        
        if response.status_code != 200:
            sender.reply(f"""=======请求失败=======
❌ 青龙API请求失败
------------------
状态码: {response.status_code}
请检查:
• API地址是否正确
• 面板是否正常运行
====================""")
            exit(0)
            
        result = response.json()
        if "token" in result.get('data', {}):
            return result['data']['token']
        else:
            sender.reply("""=======认证失败=======
❌ 获取Token失败
------------------
请检查:
• ClientID是否正确
• ClientSecret是否正确
• 应用是否有权限
====================""")
            exit(0)
            
    except requests.exceptions.RequestException as e:
        sender.reply(f"""=======网络错误=======
❌ 连接青龙面板失败
------------------
请检查:
• 青龙地址是否正确
• 网络是否正常
• 错误信息: {str(e)}
====================""")
        exit(0)
    except Exception as e:
        sender.reply(f"""=======系统错误=======
❌ 处理请求时出错
------------------
请检查:
• 配置格式是否正确
• 错误信息: {str(e)}
====================""")
        exit(0)

def QLzt(osname, value, account, username):
    """添加青龙变量"""
    try:
        qlurl = f"{QLurl}/open/envs"
        accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
        data = [{
            "value": value,
            "name": osname,
            "remarks": f'众安:{username}丨用户:{userid}丨账号:{account}丨授权时间:{accountVip}丨众安管理'
        }]
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        r = requests.post(qlurl, headers=headers, data=json.dumps(data))
        r_json = r.json()
        if "value must be unique" in r.text:
            return
        else:
            qlid = r_json['data'][0]['id']
            return
    except Exception as e:
        sender.reply(f"""=======添加失败=======
❌ 添加青龙变量失败
------------------
请检查:
• 青龙面板状态
• 变量格式是否正确
• 错误信息: {str(e)}
====================""")
        exit(0)

def QLupdate(osname, value, account, qlid, username):
    """更新青龙变量"""
    try:
        qlurl = f"{QLurl}/open/envs"
        accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
        data = {
            "value": value,
            "name": osname,
            "remarks": f'众安:{username}丨用户:{userid}丨账号:{account}丨授权时间:{accountVip}丨众安管理',
            "id": qlid
        }
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.put(qlurl, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            response_json = response.json()
            data = response_json['data']
            if data is None:
                exit(0)
            return data['id'], data['createdAt']
        else:
            sender.reply("""=======更新失败=======
❌ 更新青龙变量失败
------------------
请联系管理员处理
====================""")
            exit(0)
    except Exception as e:
        sender.reply(f"""=======更新错误=======
❌ 更新变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def Addenvs(osname, value, account, username):
    """添加或更新青龙变量"""
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json"
    }
    try:
        response = requests.get(url=url, headers=headers).json()
        qlid = None
        username_qlid = None
        
        if response['code'] == 200:
            envslist = response['data']
            for envs in envslist:
                remarks = envs.get('remarks')
                envname = envs.get('name')
                if not remarks or envname != osname:
                    continue
                    
                # 检查是否存在相同账号的变量
                if account in remarks:
                    qlid = envs['id']
                    break
                    
                # 检查是否存在相同用户名的变量
                if '众安:' in remarks:
                    try:
                        remark_username = remarks.split('众安:')[1].split('丨')[0]
                        if remark_username == username:
                            username_qlid = envs['id']
                    except:
                        continue
                    
            # 如果找到了相同用户名的变量但没有找到相同账号的变量
            if not qlid and username_qlid:
                qlid = username_qlid
        else:
            sender.reply("""=======连接失败=======
❌ 连接青龙获取变量失败
====================""")
            exit(0)
            
        if qlid:
            # 更新现有变量
            QLupdate(osname, value, account, qlid, username)
        else:
            # 创建新变量
            QLzt(osname, value, account, username)
    except Exception as e:
        sender.reply(f"""=======操作失败=======
❌ 处理变量时出错
------------------
错误信息: {str(e)}
====================""")
        exit(0)

def allenvs(osname, account):
    """获取青龙环境变量"""
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": f"Bearer {qltoken}",
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url=url, headers=headers).json()
        qlid = None
        for envs in response['data']:
            if (envs.get('name') == osname and 
                envs.get('remarks') and 
                str(account) in envs['remarks']):
                qlid = envs['id']
                break
        return qlid
    except:
        return None

def delenvs(id):
    """删除青龙环境变量"""
    if id is None:
        return
        
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": f"Bearer {qltoken}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = [id]
    
    try:
        response = requests.delete(url, headers=headers, json=data)
        if response.status_code != 200:
            return
        result = response.json()
        if result.get('code') != 200:
            return
    except:
        return

def query_zajk_info(token_cookie):
    """查询众安健康账号信息（增强版，返回更多数据）"""
    try:
        access_token, cookie = parse_token_cookie(token_cookie)
        if not access_token or not cookie:
            return {"success": False, "error": "变量格式错误，需Access-Token#Cookie"}
        
        session = requests.Session()
        session.verify = False
        headers = za_get_headers(access_token, use_cookie=False)
        
        url = f"https://{API_HOST}/api/lemon/v1/common/activity/homePage"
        body = {
            "activityCode": ACTIVITY_CODE,
            "channelCode": CHANNEL_CODE
        }
        
        resp = session.post(url, headers=headers, json=body, timeout=15)
        result = resp.json()
        
        if result.get("code") == "0":
            data = result.get("result", {})
            # 提取签到状态（增强检查逻辑）
            is_signed = False
            sign_in_info = data.get("signInInfo", {}) or {}
            # 优先检查 signInInfo.status
            sign_status = sign_in_info.get("status", "")
            if str(sign_status) == "1" or sign_status == 1:
                is_signed = True
            # 备用字段名：signInStatus
            if not is_signed:
                sign_status2 = sign_in_info.get("signInStatus", "")
                if str(sign_status2) == "1" or sign_status2 == 1:
                    is_signed = True
            # 直接检查 data.signInStatus
            if not is_signed:
                direct_status = data.get("signInStatus", "")
                if str(direct_status) == "1" or direct_status == 1:
                    is_signed = True
            # 如果以上都没有，通过签到API判断
            if not is_signed:
                sign_url = f"https://{API_HOST}/api/lemon/v1/common/activity/signIn"
                sign_resp = session.post(sign_url, headers=headers, json=body, timeout=15)
                sign_result = sign_resp.json()
                sign_msg = sign_result.get("message", "").lower()
                if "已签到" in sign_msg or "already" in sign_msg or "repeat" in sign_msg:
                    is_signed = True
            
            # 提取可领取奖励
            valuable_rewards = data.get("valuableRewardList", []) or []
            # 提取商品任务
            product_recommend = data.get("productRecommend", {}) or {}
            product_count = len(product_recommend.keys()) if product_recommend else 0
            return {
                "success": True,
                "sum_award": data.get("sumAward", 0),
                "sum_allow_withdraw": data.get("sumAllowWithdraw", 0),
                "is_signed": is_signed,
                "reward_count": len(valuable_rewards),
                "product_count": product_count,
            }
        else:
            return {"success": False, "error": result.get("message", result.get("msg", "API返回错误"))}
            
    except Exception as e:
        return {"success": False, "error": f"查询异常: {str(e)[:50]}"}

def validate_token(token_str):
    """验证token格式，仅支持#分隔符"""
    if not token_str or token_str.strip() == '':
        return False, ["Token为空"]
    
    access_token, cookie = parse_token_cookie(token_str)
    if not access_token or not cookie:
        return False, ["格式错误，需Access-Token#Cookie格式"]
    
    missing = []
    if not access_token:
        missing.append("Access-Token")
    if not cookie:
        missing.append("Cookie")
    
    if missing:
        return False, missing
    
    return True, []

def mask_name(name):
    """名称打码：保留首尾，中间用*替代"""
    if not name or name == "未知":
        return name
    if len(name) <= 1:
        return name
    if len(name) == 2:
        return name[0] + "*"
    return name[0] + "*" * (len(name) - 2) + name[-1]


def check_token_alive(token_cookie):
    """调用API检测token是否真实有效"""
    try:
        info = query_zajk_info(token_cookie)
        return info.get("success", False), info.get("error", "")
    except:
        return False, "请求异常"


def bind():
    """绑定账号"""
    def accvip(Newaddition):
        auth_status = '✅ 已授权' if accountVip >= today_time else '⚠️ 未授权'
        next_step = f'发送 {randommanagecommand} 可管理账号' if accountVip >= today_time else f'发送 {randommanagecommand} 可进行授权'
        
        success_msg = f"""=======绑定成功=======
📱 账号: {display_account}
🔐 状态: {auth_status}
⏰ 操作: {next_step}
===================="""
        if len(accountVip) != 0 and accountVip >= today_time:
            # 写入青龙变量：使用JS脚本格式 Access-Token&Cookie
            ql_value = token_cookie.replace('#', '&')
            Addenvs(osname=dd_zajk_osname, value=ql_value, account=account, username=display_account)
        
        if account not in accounts:
            accounts.append(account)
            unique_accounts = list(dict.fromkeys(accounts))
            middleware.bucketSet(bucket='dd_zajk_user', key=userid, value=f'{unique_accounts}')
            
        sender.reply(success_msg)
    
    sender.reply("""=======众安登录=======
请输入您的众安健康账号，格式为：Access-Token#Cookie
------------------
⚠️ 建议私聊登录,账号安全
⭐ 例如：token值#cookie值

📌 抓包方法：
1. 打开微信小程序「众安健康」
2. 抓包 ihealth.zhongan.com 请求
3. 获取请求头中的 Access-Token
4. 获取请求头中的 Cookie

📌 格式要求：
• Access-Token#Cookie 用 # 连接

⭐ 输入q退出操作
====================""")
    input_account = sender.input(60000, 1, False)
    if not input_account:
        sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
        exit(0)
    elif input_account.lower() == 'q':
        sender.reply("✅ 已取消登录")
        exit(0)
    
    token_cookie = input_account.strip()
    
    # 验证token格式
    is_valid, missing = validate_token(token_cookie)
    if not is_valid:
        missing_str = '、'.join(missing)
        sender.reply(f"""=======验证失败=======
❌ Token格式错误
------------------
缺少参数: {missing_str}

⚠️ 正确格式：
Access-Token#Cookie
====================""")
        exit(0)
    
    # 验证账号有效性（调API）
    sender.reply("🔄 正在验证账号...")
    info = query_zajk_info(token_cookie)
    if not info["success"]:
        sender.reply(f"""=======验证失败=======
❌ 账号验证失败: {info.get('error', '未知错误')}
请检查Token和Cookie是否正确
====================""")
        exit(0)
    
    # 用Access-Token前几位作为显示名
    access_token_val, _ = parse_token_cookie(token_cookie)
    display_account = mask_name(access_token_val) if access_token_val else "众安用户"
    
    # 保存账号信息（格式：Access-Token#Cookie，不带备注）
    account_str = token_cookie
    account = str(int(time.time() * 1000))
    
    # 检查是否重复绑定（用Access-Token匹配）
    old_auth = None
    accounts = []
    if len(uservalue) != 0:
        accounts = eval(uservalue)
        cur_token = token_cookie.split('#')[0] if '#' in token_cookie else ''
        for acc in accounts:
            acc_account = middleware.bucketGet(bucket='dd_zajk_account', key=acc)
            acc_token = acc_account.split('#')[0] if acc_account and '#' in acc_account else ''
            if acc_token and acc_token == cur_token:
                old_auth = middleware.bucketGet(bucket='dd_zajk_auth', key=acc)
                sender.reply('📝 检测到已绑定账号，将更新信息')
                accounts.remove(acc)
                middleware.bucketDel(bucket='dd_zajk_account', key=acc)
                middleware.bucketDel(bucket='dd_zajk_username', key=acc)
                middleware.bucketDel(bucket='dd_zajk_auth', key=acc)
                qlid = allenvs(osname=dd_zajk_osname, account=str(acc))
                if qlid:
                    delenvs(id=qlid)
                break
    
    # 保存新账号信息
    middleware.bucketSet(bucket='dd_zajk_username', key=account, value=display_account)
    middleware.bucketSet(bucket='dd_zajk_account', key=account, value=account_str)
    
    # 如果有旧授权，转移到新账号
    if old_auth:
        middleware.bucketSet(bucket='dd_zajk_auth', key=account, value=old_auth)
        if old_auth >= today_time:
            ql_value = token_cookie.replace('#', '&')
            Addenvs(osname=dd_zajk_osname, value=ql_value, account=account, username=display_account)
        
    if len(uservalue) == 0:
        accounts = []
        
    accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
    accvip(True)

def ValueErrors(value, count):
    """验证输入值"""
    try:
        value = int(value)
        if value > count or value == 0:
            sender.reply(f"""=======输入无效=======
❌ 请输入 1-{count} 之间的数字
====================""")
            exit(0)
        return value
    except ValueError:
        sender.reply("""=======输入无效=======
❌ 请输入正确的数字
====================""")
        exit(0)

def empower(empowertime, me_as_int):
    """授权时间计算"""
    day = me_as_int * 30
    try:
        if len(empowertime) == 0:
            delayed_date = today_date + timedelta(days=day)
        else:
            empower_date = datetime.strptime(empowertime, "%Y-%m-%d").date()
            if empower_date <= today_date:
                delayed_date = today_date + timedelta(days=day)
            else:
                delayed_date = empower_date + timedelta(days=day)
        
        return str(delayed_date)
    except Exception as e:
        print(f"授权时间计算出错: {str(e)}")
        return str(today_date + timedelta(days=day))

def management():
    """账号管理功能"""
    if len(uservalue) == 0:
        sender.reply(f"""=======未绑定账号=======
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
====================""")
        return
    count = 1
    account_list = """
======我的众安健康账号======""" 
    
    accounts = list(dict.fromkeys(eval(uservalue))) if uservalue else []
    middleware.bucketSet(bucket='dd_zajk_user', key=userid, value=f'{accounts}')
    for account in accounts:
        accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
        account_str = middleware.bucketGet(bucket='dd_zajk_account', key=account)
        
        # 检查token真实有效性（调API验证）
        token_status = ''
        if account_str:
            token_cookie = account_str
            is_alive, err = check_token_alive(token_cookie)
            if not is_alive:
                token_status = ' 🔴Token失效'
        
        if len(accountVip) == 0:
            vip_status = '⚠️ 未授权'
        elif accountVip < today_time:
            vip_status = '❌ 已过期'
        else:
            vip_status = f'✅ {accountVip}'
        
        username = middleware.bucketGet(bucket='dd_zajk_username', key=account)
        if username:
            display_username = username
        else:
            display_username = account[:3] + "****" + account[7:]
            
        account_list += f"""
------------------
[{count}] 账号信息
📱 账号: {display_username}
🔐 授权: {vip_status}{token_status}"""
        count += 1
            
    account_list += """
==================
回复数字选择账号
回复"q"退出操作
=================="""
    
    sender.reply(account_list)
    
    inputmessage = sender.input(60000, 1, False)
    if not inputmessage:
        sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
        exit(0)
    elif inputmessage.lower() == 'q':
        sender.reply('✅ 已退出管理')
        exit(0)
            
    try:
        me_as_int = int(inputmessage)
        if me_as_int > count - 1:
            sender.reply('❌ 输入的序号无效')
            exit(0)
    except ValueError:
        sender.reply('❌ 输入必须是数字')
        exit(0)
            
    account = accounts[me_as_int - 1]
    account_str = middleware.bucketGet(bucket='dd_zajk_account', key=account)
    accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
    username = middleware.bucketGet(bucket='dd_zajk_username', key=account)
        
    if len(accountVip) == 0:
        vip_status = '⚠️ 未授权'
    elif accountVip < today_time:
        vip_status = '❌ 已过期'
    else:
        vip_status = f'✅ {accountVip}'
            
    account_info = f"""
=======账号详情======
📱 账号: {username}
🔐 授权: {vip_status}
=================="""
    sender.reply(account_info)
    menu = """
=======账号管理======
[1] 授权账号
[2] 删除账号
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(menu)
    inputmessage = sender.input(60000, 1, False)
    if not inputmessage:
        sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
        exit(0)
    elif inputmessage == '2':
        confirm_msg = """=======删除警告=======
❌ 确定要删除该账号吗？
------------------
此操作不可恢复！
[y] 确认删除
[n] 取消操作
===================="""
        sender.reply(confirm_msg)
        
        yesorno = sender.input(60000, 1, False)
        if not yesorno:
            sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
            exit(0)
        elif yesorno.lower() in ['y', '是']:
            accounts.remove(str(account))
            qlid = allenvs(osname=dd_zajk_osname, account=str(account))
            delenvs(id=qlid)
            if len(accounts) == 0:
                middleware.bucketDel(bucket='dd_zajk_user', key=userid)
            else:
                middleware.bucketSet(bucket='dd_zajk_user', key=userid, value=f'{accounts}')
            middleware.bucketDel(bucket='dd_zajk_account', key=account)
            middleware.bucketDel(bucket='dd_zajk_username', key=account)
            middleware.bucketDel(bucket='dd_zajk_auth', key=account)
            sender.reply('✅ 账号删除成功!')
        else:
            sender.reply('✅ 已取消删除')
            exit(0)
            
    elif inputmessage == '1':
        auth_guide = """=======授权设置=======
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
===================="""
        sender.reply(auth_guide)
        
        mes = sender.input(60000, 1, False)
        if not mes:
            sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
            exit(0)
        elif mes.lower() == 'q':
            sender.reply("✅ 已取消授权")
            exit(0)
            
        mes = ValueErrors(value=mes, count=999)
        money = Decimal(mes) * Decimal(zajkVipmoney)
        
        zf(project='众安授权', me_as_int=mes, accountVip=accountVip, account_str=account_str,
           username=username, account=account)
           
        accountVip = empower(empowertime=accountVip, me_as_int=mes)
        middleware.bucketSet(bucket='dd_zajk_auth', key=account, value=accountVip)
        ql_value = account_str.replace('#', '&') if account_str else ''
        Addenvs(osname=dd_zajk_osname, value=ql_value, account=account, username=username)
        
        result_msg = f"""=======订单完成=======
🎈 名称: 众安授权
🎉 数量: {mes} 个月
💰 金额: {money} 元
===================="""
        sender.reply(result_msg)
        
    elif inputmessage.lower() == 'q':
        sender.reply('✅ 已退出管理')
        exit(0)
    else:
        sender.reply('❌ 输入无效')
        exit(0)

def yesornos():
    """确认操作"""
    yesorno = sender.input(60000, 1, False)
    if yesorno.lower() in ['y', '是']:
        return True
    elif yesorno.lower() in ['n', '否']:
        return False
    elif not yesorno:
        sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
        exit(0)
    elif yesorno.lower() in ['q', '退出']:
        sender.reply('✅ 已退出!')
        exit(0)
    else:
        sender.reply('❌ 输入错误！')
        exit(0)

def zf(project, me_as_int, accountVip, account_str, username, account):
    """支付处理"""
    try:
        zsm = middleware.bucketGet('dd_zajk_config', 'zsm')
        use_ma_pay = middleware.bucketGet('dd_zajk_config', 'use_ma_pay') == 'true'
        
        if not zsm and not use_ma_pay:
            sender.reply('❌ 未配置收款方式,请联系管理员!')
            exit(0)
            
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(zajkcoin) * me_as_int
        
        pay_options = []
        
        if zsm:
            money = Decimal(me_as_int) * Decimal(zajkVipmoney)
            pay_options.append({
                'type': 'wechat',
                'name': '微信支付',
                'money': money,
                'zfcoin': 0
            })
            
        if use_ma_pay:
            ma_pay_config = {
                'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
                'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
                'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
                'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
                'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type'),
                'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
                'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
            }
            
            if ma_pay_config['switch'].lower() == 'true' and all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
                money = Decimal(me_as_int) * Decimal(zajkVipmoney)
                pay_options.append({
                    'type': 'mapay',
                    'name': '码支付',
                    'money': money,
                    'zfcoin': 0,
                    'config': ma_pay_config
                })
            
        if zajkcoin and int(zajkcoin) > 0:
            pay_options.append({
                'type': 'coin',
                'name': '积分支付',
                'money': 0,
                'zfcoin': zfcoin
            })
            
        pay_menu = """=====选择支付方式===="""
        for idx, option in enumerate(pay_options, 1):
            if option['type'] == 'wechat':
                pay_menu += f"""
{idx}️⃣ 微信支付
   💰 {option['money']}元/{me_as_int}月"""
            elif option['type'] == 'mapay':
                pay_menu += f"""
{idx}️⃣ 码支付
   💰 {option['money']}元/{me_as_int}月"""
            elif option['type'] == 'coin':
                pay_menu += f"""
{idx}️⃣ 积分支付  
   🎯 {option['zfcoin']}积分/{me_as_int}月
   💫 当前积分: {usercoin}"""
            
        pay_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""
        sender.reply(pay_menu)
        choice = sender.input(60000, 1, False)
        
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消支付")
            exit(0)
            
        try:
            choice_idx = int(choice) - 1
            if choice_idx < 0 or choice_idx >= len(pay_options):
                sender.reply("❌ 输入无效")
                exit(0)
            selected = pay_options[choice_idx]
        except ValueError:
            sender.reply("❌ 输入无效")
            exit(0)
            
        if selected['type'] == 'wechat':
            zfzt = sender.atWaitPay()
            if zfzt:
                sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
                exit(0)
                
            money = selected['money']
            
            pay_msg = f"""=====微信扫码支付====
🎫 商品: {project}
📅 时长: {me_as_int}月
💰 金额: {money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
            sender.reply(pay_msg)
            sender.replyImage(zsm)
            
            ddzf = sender.waitPay("q", 100 * 1000)
            
            if str(ddzf) == 'q':
                sender.reply('✅ 已取消支付')
                exit(0)
                
            try:
                if isinstance(ddzf, dict):
                    if ddzf.get('Type') == '微信赞赏':
                        Money = float(ddzf.get('Money', 0))
                    elif ddzf.get('Type') == '微信收款':
                        Money = float(ddzf.get('Money', 0))
                    elif ddzf.get('Money'):
                        Money = float(ddzf.get('Money', 0))
                    elif ddzf.get('money'):
                        Money = float(ddzf.get('money', 0))
                    else:
                        sender.reply('❌ 不支持的支付消息格式')
                        exit(0)
                else:
                    try:
                        ddzf = json.loads(ddzf)
                        Money = float(ddzf.get('Money', ddzf.get('money', 0)))
                    except:
                        sender.reply("❌ 无法解析支付结果")
                        exit(0)
                    
                if float(Money) >= float(money):
                    return True
                else:
                    sender.reply(f"""=====支付金额错误=====
💰 应付: {money}元
💳 实付: {Money}元
❗ 请联系管理员处理退款！
==================""")
                    exit(0)
            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                exit(0)
                
        elif selected['type'] == 'coin':
            if int(usercoin) < selected['zfcoin']:
                sender.reply(f"""=====积分不足=====
👤 当前积分: {usercoin}
📍 需要积分: {selected['zfcoin']}
==================""")
                exit(0)
                
            confirm_msg = f"""=====积分支付确认=====
💫 消耗积分: {selected['zfcoin']}
⏰ 授权时长: {me_as_int}月
------------------
确认请回复【y】
取消请回复【n】
=================="""
            sender.reply(confirm_msg)
            
            if yesornos():
                new_balance = int(usercoin) - selected['zfcoin']
                middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                return True
            else:
                sender.reply("✅ 已取消支付")
                exit(0)
            
    except Exception as e:
        sender.reply(f"❌ 支付处理发生错误: {str(e)}")
        exit(0)

def cxs():
    """查询所有账号"""
    if len(uservalue) == 0:
        sender.reply(f"""=======未绑定账号=======
❌ 未找到任何账号信息
💡 发送 {randomsigncommand} 绑定
====================""")
        return
    accounts = list(dict.fromkeys(eval(uservalue))) if uservalue else []
    middleware.bucketSet(bucket='dd_zajk_user', key=userid, value=f'{accounts}')
    for account in accounts:
        account_str = middleware.bucketGet(bucket='dd_zajk_account', key=account)
        accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
        username = middleware.bucketGet(bucket='dd_zajk_username', key=account)
        
        if len(accountVip) == 0 or accountVip < today_time:
            sender.reply(f"""=======授权过期=======
📱 账号: {username}
⚠️ 状态: 授权已过期
💡 发送 {randommanagecommand} 续费
====================""")
            continue
        
        # 提取token部分（格式：Access-Token#Cookie，无备注前缀）
        token_cookie = account_str
        
        # 查询账号信息
        info = query_zajk_info(token_cookie)
        
        if info["success"]:
            sum_award = info.get("sum_award", 0) / 100
            sum_withdraw = info.get("sum_allow_withdraw", 0) / 100
            is_signed = info.get("is_signed", False)
            reward_count = info.get("reward_count", 0)
            sign_icon = '✅ 已签到' if is_signed else '❌ 未签到'
            
            msg = f"""=======账号详情=======
📱 账号: {username}
🔐 授权至: {accountVip}
━━━━━━━━━━━━━━
💰 累计金额: {sum_award:.2f}元
💵 可提现: {sum_withdraw:.2f}元
📋 签到状态: {sign_icon}"""
            if reward_count > 0:
                msg += f"\n🎁 待领奖励: {reward_count}个"
            msg += "\n===================="
            sender.reply(msg)
        else:
            sender.reply(f"""=======账号详情=======
📱 账号: {username}
🔐 授权至: {accountVip}
❌ 查询失败: {info.get('error', '未知错误')}
💡 请重新登录更新账号
====================""")

def zajk_auth():
    """众安授权管理功能"""
    if not sender.isAdmin():
        sender.reply("""=======权限错误=======
⛔ 您没有权限执行此操作
====================""")
        return
        
    dd_zajk_osname, dd_zajk_qlname, _, _, _, _, _, _, _, _ = getusercontent()
    QLurl, qltoken = seekql()
    
    sender.reply("""=====众安授权=====
[1] 📱 一键授权所有用户
[2] 👤 单独授权用户
[3] ⏰ 修改授权时间
------------------
⚠️ 输入q退出操作
====================""")
    xz = sender.input(60000, 1, False)
    
    if not xz:
        sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
        return
        
    if xz.lower() == 'q':
        sender.reply("✅ 已退出授权")
        return
        
    if xz == '1':
        users = middleware.bucketAllKeys('dd_zajk_user')
        if not users:
            sender.reply("""=======查询失败=======
❌ 未找到任何绑定账号
====================""")
            return
            
        sender.reply('请输入要给所有用户授权的月数！\n退出【q】！')
        sjts = sender.input(60000, 1, False)
        if not sjts:
            sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
            return
        elif sjts.lower() == 'q':
            sender.reply("退出！")
            return
            
        try:
            sjts = int(sjts)
        except:
            sender.reply('输入的月数无效，必须是数字！')
            return
            
        success_count = 0
        fail_count = 0
        
        for user in users:
            accountlist = middleware.bucketGet('dd_zajk_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            accounts = eval(accountlist)
            for account in accounts:
                try:
                    accountVip = middleware.bucketGet('dd_zajk_auth', account)
                    username = middleware.bucketGet('dd_zajk_username', account)
                    account_str = middleware.bucketGet('dd_zajk_account', account)
                    
                    if not account:
                        fail_count += 1
                        continue
                        
                    accountVip = empower(empowertime=accountVip, me_as_int=sjts)
                    middleware.bucketSet('dd_zajk_auth', account, accountVip)
                    
                    # 写入青龙变量：Access-Token&Cookie格式
                    ql_value = account_str.replace('#', '&') if account_str else ''
                    Addenvs(dd_zajk_osname, ql_value, account, username)
                    success_count += 1
                except:
                    fail_count += 1
                    
        sender.reply(f"一键授权完成!\n成功授权: {success_count}个账号\n授权失败: {fail_count}个账号\n授权月数: {sjts}月")
        
    elif xz == '2':
        sender.reply('请输入需要授权的用户ID\n通过给机器人发送myuid获得\n退出【q】！')
        target_uid = sender.input(60000, 1, False)
        if not target_uid:
            sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
            return
        elif target_uid.lower() == 'q':
            sender.reply("退出！")
            return
            
        accountlist = middleware.bucketGet('dd_zajk_user', target_uid)
        if accountlist == '' or accountlist == '{}':
            sender.reply('该用户没有绑定账号')
            return
            
        sender.reply('请输入授权月数！')
        months = sender.input(60000, 1, False)
        if not months:
            sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
            return
        try:
            months = int(months)
        except:
            sender.reply('输入的月数无效')
            return
            
        accounts = eval(accountlist)
        for account in accounts:
            accountVip = middleware.bucketGet('dd_zajk_auth', account)
            username = middleware.bucketGet('dd_zajk_username', account)
            account_str = middleware.bucketGet('dd_zajk_account', account)
            
            accountVip = empower(empowertime=accountVip, me_as_int=months)
            middleware.bucketSet('dd_zajk_auth', account, accountVip)
            
            # 写入青龙变量：Access-Token&Cookie格式
            ql_value = account_str.replace('#', '&') if account_str else ''
            Addenvs(dd_zajk_osname, ql_value, account, username)
                
        sender.reply(f"授权成功！用户 {target_uid} 已授权 {months} 个月")
        
    elif xz == '3':
        sender.reply('请输入用户ID')
        target_uid = sender.input(60000, 1, False)
        if target_uid.lower() == 'q':
            sender.reply("退出！")
            return
            
        accountlist = middleware.bucketGet('dd_zajk_user', target_uid)
        if accountlist == '' or accountlist == '{}':
            sender.reply('该用户没有绑定账号')
            return
            
        sender.reply('请输入新的授权日期（格式：2026-05-01）')
        new_date = sender.input(60000, 1, False)
        if not new_date:
            sender.reply('⏰ 操作超时（60秒未响应），请重新发送指令操作')
            return
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
        except:
            sender.reply('日期格式错误')
            return
            
        accounts = eval(accountlist)
        for account in accounts:
            middleware.bucketSet('dd_zajk_auth', account, new_date)
            username = middleware.bucketGet('dd_zajk_username', account)
            account_str = middleware.bucketGet('dd_zajk_account', account)
            # 写入青龙变量：Access-Token&Cookie格式
            ql_value = account_str.replace('#', '&') if account_str else ''
            Addenvs(dd_zajk_osname, ql_value, account, username)
                
        sender.reply(f"授权时间已修改为 {new_date}")
    else:
        sender.reply('❌ 输入无效')

def clean_expired_accounts():
    """清理过期账号"""
    users = middleware.bucketAllKeys('dd_zajk_user')
    if not users:
        sender.reply("""=======清理完成=====
🧹 没有需要清理的账号
====================""")
        exit(0)
        
    cleaned_count = 0
    ql_cleaned = 0
    
    for user in users:
        accountlist = middleware.bucketGet('dd_zajk_user', user)
        if accountlist == '' or accountlist == '{}':
            continue
            
        accounts = eval(accountlist)
        valid_accounts = []
        
        for account in accounts:
            accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
            if accountVip and accountVip > today_time:
                valid_accounts.append(account)
            else:
                cleaned_count += 1
                middleware.bucketDel(bucket='dd_zajk_account', key=account)
                middleware.bucketDel(bucket='dd_zajk_username', key=account)
                middleware.bucketDel(bucket='dd_zajk_auth', key=account)
                
                try:
                    qlid = allenvs(dd_zajk_osname, account)
                    if qlid:
                        delenvs(qlid)
                        ql_cleaned += 1
                except:
                    pass
        
        if len(valid_accounts) == 0:
            middleware.bucketDel(bucket='dd_zajk_user', key=user)
        else:
            middleware.bucketSet('dd_zajk_user', user, str(valid_accounts))
    
    sender.reply(
        "=====清理完成=====\n"
        f"🧹 清理插件账号: {cleaned_count}个\n"
        f"🔧 清理青龙变量: {ql_cleaned}个\n"
        "==================="
    )
    exit(0)

# =============== 主函数 ===============
if __name__ == '__main__':
    dd_zajk_osname, dd_zajk_qlname, dd_managecommand, dd_querycommand, dd_signcommand, randommanagecommand, randomquerycommand, randomsigncommand, zajkVipmoney, zajkcoin = getusercontent()
    QLurl, qltoken = seekql()
    usermessage = sender.getMessage()
    
    if usermessage in ['众安登录', '登录众安']:
        bind()
    elif usermessage in ['众安管理', '管理众安']:
        management()
    elif usermessage in ['众安查询', '查询众安']:
        cxs()
    elif usermessage in ['众安授权']:
        zajk_auth()
    elif usermessage in ['众安清理', '清理众安']:
        clean_expired_accounts()
    else:
        # 定时任务：签到+任务+抽奖+提现
        users = middleware.bucketAllKeys(bucket='dd_zajk_user')
        if not users:
            exit(0)
        
        for user in users:
            try:
                user_val = middleware.bucketGet(bucket='dd_zajk_user', key=user)
                if not user_val:
                    continue
                    
                accounts = eval(user_val)
                for account in accounts:
                    try:
                        account_str = middleware.bucketGet(bucket='dd_zajk_account', key=account)
                        accountVip = middleware.bucketGet(bucket='dd_zajk_auth', key=account)
                        
                        if not account_str:
                            continue
                        
                        # 检查授权状态
                        if len(accountVip) == 0 or accountVip < today_time:
                            print(f"账号 {account} 授权已过期")
                            continue
                        
                        # 提取token和cookie（格式：Access-Token#Cookie，无备注前缀）
                        token_cookie = account_str
                        
                        access_token, cookie = parse_token_cookie(token_cookie)
                        if not access_token or not cookie:
                            print(f"账号 {account} Token格式错误")
                            continue
                        
                        session = requests.Session()
                        session.verify = False
                        
                        # 1. 获取首页信息（不使用Cookie）
                        headers = za_get_headers(access_token, use_cookie=False)
                        home_body = {"activityCode": ACTIVITY_CODE, "channelCode": CHANNEL_CODE}
                        home_url = f"https://{API_HOST}/api/lemon/v1/common/activity/homePage"
                        
                        resp = session.post(home_url, headers=headers, json=home_body, timeout=15)
                        home_result = resp.json()
                        
                        if home_result.get("code") != "0":
                            print(f"账号 {account} 获取首页失败: {home_result.get('message', '未知')}")
                            continue
                        
                        print(f"账号 {account} 获取首页成功")
                        time.sleep(random.uniform(2, 4))
                        
                        # 2. 签到（不使用Cookie）
                        sign_url = f"https://{API_HOST}/api/lemon/v1/common/activity/signIn"
                        sign_resp = session.post(sign_url, headers=headers, json=home_body, timeout=15)
                        sign_result = sign_resp.json()
                        if sign_result.get("code") == "0":
                            print(f"账号 {account} 签到成功")
                        else:
                            print(f"账号 {account} 签到: {sign_result.get('message', '失败')}")
                        time.sleep(random.uniform(2, 4))
                        
                        # 3. 商品浏览任务（最多3个，使用Cookie）
                        product_recommend = home_result.get("result", {}).get("productRecommend", {}) or {}
                        product_keys = list(product_recommend.keys())[:3]
                        product_headers = za_get_headers(access_token, use_cookie=True, cookie=cookie)
                        for goods_code in product_keys:
                            task_url = f"https://{API_HOST}/api/lemon/v1/applet/mgm/activity/add/award"
                            task_body = {
                                "activityCode": ACTIVITY_CODE,
                                "channelCode": "1000000004",
                                "goodsCode": goods_code,
                                "taskId": "110"
                            }
                            task_resp = session.post(task_url, headers=product_headers, json=task_body, timeout=15)
                            task_result = task_resp.json()
                            if task_result.get("code") == "0":
                                print(f"账号 {account} 商品任务 {goods_code} 完成")
                            else:
                                print(f"账号 {account} 商品任务 {goods_code} 失败: {task_result.get('message')}")
                            time.sleep(random.uniform(2, 4))
                        
                        # 4. 再次获取首页，抽奖（不使用Cookie）
                        resp2 = session.post(home_url, headers=headers, json=home_body, timeout=15)
                        home_result2 = resp2.json()
                        
                        if home_result2.get("code") == "0":
                            reward_list = home_result2.get("result", {}).get("valuableRewardList", []) or []
                            lottery_url = f"https://{API_HOST}/api/lemon/v1/common/activity/lottery"
                            for reward in reward_list:
                                award_id = reward.get("awardDetailId")
                                if not award_id:
                                    continue
                                lottery_body = {
                                    "channelCode": CHANNEL_CODE,
                                    "activityCode": ACTIVITY_CODE,
                                    "id": award_id
                                }
                                lottery_resp = session.post(lottery_url, headers=headers, json=lottery_body, timeout=15)
                                lottery_result = lottery_resp.json()
                                if lottery_result.get("code") == "0":
                                    print(f"账号 {account} 抽奖 {award_id} 成功")
                                else:
                                    print(f"账号 {account} 抽奖 {award_id} 失败: {lottery_result.get('message')}")
                                time.sleep(random.uniform(2, 4))
                            else:
                                if not reward_list:
                                    print(f"账号 {account} 今日无可领取奖励")
                        else:
                            print(f"账号 {account} 二次获取首页失败")
                        
                        # 5. 查询可提现金额，>=5元自动提现（不使用Cookie）
                        sum_allow_withdraw = home_result2.get("result", {}).get("sumAllowWithdraw", 0) if home_result2.get("code") == "0" else 0
                        sum_award = home_result2.get("result", {}).get("sumAward", 0) if home_result2.get("code") == "0" else 0
                        print(f"账号 {account} 累计金额: {sum_award/100:.2f}元 | 可提现: {sum_allow_withdraw/100:.2f}元")
                        
                        if sum_allow_withdraw >= 500:  # 500分=5元
                            withdraw_url = f"https://{API_HOST}/api/lemon/v1/common/activity/withdraw"
                            withdraw_body = {
                                "channelCode": CHANNEL_CODE,
                                "activityCode": ACTIVITY_CODE,
                                "amount": 500
                            }
                            withdraw_resp = session.post(withdraw_url, headers=headers, json=withdraw_body, timeout=15)
                            withdraw_result = withdraw_resp.json()
                            if withdraw_result.get("code") == "0":
                                print(f"账号 {account} 提现5元成功!")
                            else:
                                print(f"账号 {account} 提现失败: {withdraw_result.get('message')}")
                        else:
                            print(f"账号 {account} 可提现不足5元，跳过")
                        
                        print(f"账号 {account} 运行完毕")
                        
                    except Exception as e:
                        print(f"处理账号 {account} 时出错: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"处理用户 {user} 时出错: {str(e)}")
                continue
