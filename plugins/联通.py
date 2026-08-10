# [rule: ^联通(登录|登陆|查询|管理|授权|后台|教程)$]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 0 8,15 * * *]
# [public: true]
# [title: 联通]
# [icon: https://uapis.cn/static/uploads/9b25f4d581_5gbszuxm7Mt8.webp]
# [open_source: false]
# [class: 工具类]
# [version: 2.1]
# [price: 15.88]
# [admin: false]
# [author: sky2022]
# [service: 2661320550]
# [description: 联通插件，使用Online_token登录<br>指令：联通登录、联通查询、联通管理、联通授权、联通后台、联通教程<br>定时任务：每天8点和15点自动检测授权过期并推送通知<br>V2.1:新增定时检测推送，每天8点/15点自动检测授权到期状态并通知用户<br>V1.7:统一面板配置为面板类型+对接面板配置，并新增呆呆面板分组配置丨]

import os
import re
import json
import time
import base64
import hashlib
import random
import asyncio
from datetime import datetime, timedelta
import middleware
import requests
import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_ltyp_user', key=userid)

# 插件配置
PLUGIN_CONFIG = {
    'bucket': 'dd_ltyp',
    'coin_key': 'ltypcoin',
    'name': '联通'
}

# [param: {"required":true,"key":"dd_ltyp.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_ltyp.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_ltyp.panel_group","bool":false,"placeholder":"例:联通","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_ltyp.var_name","bool":false,"placeholder":"必填项,例:LTYPCookie","name":"面板变量名","desc":"提交到面板中的变量名"}]
# [param: {"required":true,"key":"dd_ltyp.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_ltyp.vip_money","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_ltyp.vip_coin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"dd_ltyp.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]


def normalize_panel_type(panel_type_value, legacy_use_daidai_value='false'):
    """统一解析面板类型，兼容新旧配置。"""
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    if value:
        return ''

    legacy_value = str(legacy_use_daidai_value or '').strip().lower()
    if legacy_value == 'true':
        return 'daidai'
    return 'qinglong'

def get_config():
    """获取插件配置"""
    var_name = middleware.bucketGet('dd_ltyp', 'var_name') or 'LTYPCookie'
    panel_type = normalize_panel_type(
        middleware.bucketGet('dd_ltyp', 'panel_type') or '',
        middleware.bucketGet('dd_ltyp', 'use_daidai') or 'false'
    )
    if not panel_type:
        sender.reply("对接面板类型填写无效，请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai")
        exit(0)

    panel_config = (middleware.bucketGet('dd_ltyp', 'panel_config') or '').strip()
    legacy_ql_config = middleware.bucketGet('dd_ltyp', 'ql_config') or ''
    ql_config = panel_config or legacy_ql_config if panel_type == 'qinglong' else legacy_ql_config
    return var_name, ql_config

def get_daidai_config():
    """获取呆呆面板配置"""
    panel_type = normalize_panel_type(
        middleware.bucketGet('dd_ltyp', 'panel_type') or '',
        middleware.bucketGet('dd_ltyp', 'use_daidai') or 'false'
    )
    if not panel_type:
        sender.reply("对接面板类型填写无效，请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai")
        exit(0)

    panel_config = (middleware.bucketGet('dd_ltyp', 'panel_config') or '').strip()
    legacy_dd_config = middleware.bucketGet('dd_ltyp', 'dd_ltyp_ddname') or ''
    use_daidai = panel_type == 'daidai'
    dd_ltyp_ddname = panel_config or legacy_dd_config if use_daidai else legacy_dd_config
    panel_group = (middleware.bucketGet('dd_ltyp', 'panel_group') or '').strip()
    return use_daidai, dd_ltyp_ddname, panel_group


def get_full_config():
    """获取完整插件配置"""
    from decimal import Decimal
    var_name = middleware.bucketGet('dd_ltyp', 'var_name') or 'LTYPCookie'
    _, ql_config = get_config()
    zsm = middleware.bucketGet('dd_ltyp', 'zsm') or ''
    vip_money = Decimal(middleware.bucketGet('dd_ltyp', 'vip_money') or '0')
    vip_coin = int(middleware.bucketGet('dd_ltyp', 'vip_coin') or '0')
    use_ma_pay = middleware.bucketGet('dd_ltyp', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    return var_name, ql_config, zsm, vip_money, vip_coin, use_ma_pay


def get_payment_config():
    """获取支付配置"""
    zsm = middleware.bucketGet('dd_ltyp', 'zsm')
    use_ma_pay = middleware.bucketGet('dd_ltyp', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    ma_pay_config = None
    if use_ma_pay:
        # 从卡密系统获取码支付配置
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
            use_ma_pay = False
            ma_pay_config = None
    
    return zsm, use_ma_pay, ma_pay_config


def generate_qrcode(url):
    """生成二维码图片"""
    try:
        import urllib.parse
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


def empower(empowertime, me_as_int):
    """授权时间计算"""
    today_date = datetime.now().date()
    today_time = str(today_date)
    day = me_as_int * 30
    if len(empowertime) == 0 or empowertime <= today_time:
        delayed_date = today_date + timedelta(days=day)
    elif empowertime > today_time:
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        delayed_date = delayed_date.date()
    else:
        return None
    return str(delayed_date)


def get_auth_status(account_vip, today_time):
    """获取授权状态"""
    if not account_vip:
        return "⚠️ 未授权", "无"
    elif account_vip <= today_time:
        return "❌ 已过期", account_vip
    else:
        return "✅ 已授权", account_vip


def parse_payment_result(ddzf):
    """解析支付结果"""
    try:
        if isinstance(ddzf, dict):
            if ddzf.get('Type') == '微信赞赏':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            elif ddzf.get('Type') == '微信收款':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            elif ddzf.get('Money'):
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
            elif ddzf.get('money'):
                return float(ddzf.get('money', 0)), ddzf.get('time', '').replace('T', ' ').split('.')[0], ddzf.get('fromName', '')
            else:
                return None, None, None
        else:
            try:
                ddzf = json.loads(ddzf)
                if ddzf.get('Type') == '微信赞赏':
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
                elif ddzf.get('Type') == '微信收款':
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
                else:
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
            except:
                return None, None, None
    except Exception as e:
        return None, None, None


def mask_phone(phone):
    """手机号脱敏"""
    if isinstance(phone, str) and len(phone) >= 11:
        return phone[:3] + "****" + phone[-4:]
    return phone

# ========== 青龙相关 ==========
def get_ql_token(url, client_id, client_secret):
    """获取青龙token"""
    try:
        r = requests.get(f'{url}/open/auth/token?client_id={client_id}&client_secret={client_secret}')
        if r.status_code != 200:
            raise Exception(f"请求失败: {r.status_code}")
        data = r.json()
        if "token" not in data.get('data', {}):
            raise Exception("获取token失败")
        return data['data']['token']
    except Exception as e:
        raise Exception(f"获取token失败: {str(e)}")


def dd_get_token(dd_url, app_key, app_secret):
    """获取呆呆面板Token"""
    try:
        url = f'{dd_url}/api/open-api/token'
        data = {"app_key": app_key, "app_secret": app_secret}
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise Exception(f"请求失败: {response.status_code}")
        result = response.json()
        access_token = result.get('data', {}).get('access_token')
        if access_token:
            return access_token
        raise Exception("获取Token失败")
    except Exception as e:
        raise Exception(f"获取呆呆面板Token失败: {str(e)}")


def init_qinglong():
    """初始化面板连接（支持青龙/呆呆面板）"""
    use_daidai, dd_ltyp_ddname, _ = get_daidai_config()
    var_name, ql_config = get_config()

    if use_daidai:
        if not dd_ltyp_ddname:
            return None, None, None
        ddlist = dd_ltyp_ddname.split('丨')
        if len(ddlist) != 3:
            return None, None, None
        dd_url = ddlist[0].strip()
        app_key = ddlist[1].strip()
        app_secret = ddlist[2].strip()
        if not all([dd_url, app_key, app_secret]):
            return None, None, None
        try:
            token = dd_get_token(dd_url, app_key, app_secret)
            return dd_url, token, var_name
        except:
            return None, None, None

    if not ql_config:
        return None, None, None
    ql_params = ql_config.split('丨')
    if len(ql_params) != 3:
        return None, None, None
    ql_url = ql_params[0].strip()
    client_id = ql_params[1].strip()
    client_secret = ql_params[2].strip()
    if not all([ql_url, client_id, client_secret]):
        return None, None, None
    try:
        token = get_ql_token(ql_url, client_id, client_secret)
        return ql_url, token, var_name
    except:
        return None, None, None


def add_to_qinglong(ql_url, ql_token, var_name, token_online, phone, remark, ecs_token=None, expire_time=None):
    """添加变量到面板（支持青龙/呆呆面板）"""
    use_daidai, _, panel_group = get_daidai_config()

    # 青龙变量格式固定为 手机号#online_token
    env_value = f"{phone}#{token_online}"

    # 构建备注
    account_remark = remark
    if not account_remark:
        account_data = middleware.bucketGet('dd_ltyp_token', phone)
        if account_data:
            try:
                account_remark = json.loads(account_data).get('remark', '')
            except:
                account_remark = ''
    
    remarks_parts = [f"手机:{phone}"]
    remarks_parts.append(f"备注:{account_remark or ''}")
    if expire_time:
        remarks_parts.append(f"到期:{expire_time}")
    remarks_parts.append(f"用户:{userid}")

    if use_daidai:
        try:
            # 呆呆面板逻辑
            headers = {
                "Authorization": f"Bearer {ql_token}",
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            # 查询是否已存在
            params = {"keyword": str(phone), "page_size": 100}
            response = requests.get(f"{ql_url}/api/envs", headers=headers, params=params).json()
            exists_id = None
            data_list = response.get('data', [])
            if isinstance(data_list, list):
                for env in data_list:
                    if env.get('name') == var_name and str(phone) in (env.get('remarks') or ''):
                        exists_id = env['id']
                        break

            data = {
                "value": env_value,
                "name": var_name,
                "remarks": "丨".join(remarks_parts)
            }
            if panel_group:
                data["group"] = panel_group

            if exists_id:
                response = requests.put(f"{ql_url}/api/envs/{exists_id}", headers=headers, json=data)
            else:
                response = requests.post(f"{ql_url}/api/envs", headers=headers, json=data)

            return response.status_code in (200, 201)
        except:
            return False
    else:
        try:
            # 青龙面板逻辑
            url = f"{ql_url}/open/envs"
            headers = {
                "Authorization": f"Bearer {ql_token}",
                "Content-Type": "application/json"
            }
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                raise Exception("获取变量失败")

            exists_id = None
            for env in response.json().get('data', []):
                if env['name'] == var_name and phone in env.get('remarks', ''):
                    exists_id = env['id']
                    break

            data = {
                "name": var_name,
                "value": env_value,
                "remarks": "丨".join(remarks_parts)
            }

            if exists_id:
                data['id'] = exists_id
                response = requests.put(url, headers=headers, json=data)
            else:
                response = requests.post(url, headers=headers, json=[data])

            if response.status_code != 200:
                raise Exception("提交变量失败")
            return True
        except Exception as e:
            return False


def delete_from_qinglong(ql_url, ql_token, var_name, phone):
    """从面板删除变量（支持青龙/呆呆面板）"""
    use_daidai, _, _ = get_daidai_config()

    if use_daidai:
        try:
            headers = {
                "Authorization": f"Bearer {ql_token}",
                "accept": "application/json",
                "Content-Type": "application/json"
            }
            params = {"keyword": str(phone), "page_size": 100}
            response = requests.get(f"{ql_url}/api/envs", headers=headers, params=params).json()
            data_list = response.get('data', [])
            if isinstance(data_list, list):
                for env in data_list:
                    if env.get('name') == var_name and str(phone) in (env.get('remarks') or ''):
                        requests.delete(f"{ql_url}/api/envs/{env['id']}", headers=headers)
                        break
            return True
        except:
            return False
    else:
        try:
            url = f"{ql_url}/open/envs"
            headers = {"Authorization": f"Bearer {ql_token}"}
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return False
            env_id = None
            for env in response.json().get('data', []):
                if env['name'] == var_name and phone in env.get('remarks', ''):
                    env_id = env['id']
                    break
            if env_id:
                requests.delete(url, headers=headers, json=[env_id])
            return True
        except:
            return False


# ========== 云盘查询相关 ==========
def encrypt_aes(text, key, iv='wNSOYIB1k1DjY5lA'):
    """AES加密"""
    key_bytes = key[:16].encode('utf-8')
    iv_bytes = iv.encode('utf-8')
    cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
    padded_text = pad(text.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_text)
    return base64.b64encode(encrypted_bytes).decode('utf-8')


async def get_ecstoken(session, token_online):
    """获取ecs_token和手机号"""
    try:
        url = "https://m.client.10010.com/mobileService/onLine.htm"
        payload = {
            'isFirstInstall': "1",
            'version': "android@11.0702",
            'token_online': token_online
        }
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
            'Content-Type': "application/x-www-form-urlencoded",
        }
        response = await session.post(url, data=payload, headers=headers)
        response_text = response.text
        try:
            data = json.loads(response_text)
        except:
            return None, None, f"返回非JSON: {response_text[:200]}"
        # 检查是否登录失效
        if data.get("code") == "9999" or data.get("code") == "ECS99999":
            return None, None, "token已失效，请重新登录"
        desmobile = data.get("desmobile")
        ecs_token = data.get("ecs_token")
        if not ecs_token:
            return None, None, data.get("dsc", "获取ecs_token失败")
        return desmobile, ecs_token, None
    except Exception as e:
        return None, None, str(e)


async def get_ticket(session, ecs_token):
    """获取ticket"""
    try:
        url = "https://m.client.10010.com/mobileService/openPlatform/openPlatLineNew.htm?to_url=https://contact.bol.wo.cn/market"
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Cookie': f'ecs_token={ecs_token}',
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
        }
        response = await session.get(url, headers=headers, follow_redirects=False)
        if response.status_code in (301, 302, 303, 307, 308):
            location = response.headers.get('Location')
            if location:
                from urllib.parse import urlparse, parse_qs
                parsed_url = urlparse(location)
                query_params = parse_qs(parsed_url.query)
                ticket = query_params.get('ticket', [None])[0]
                return ticket, None
        return None, f"状态码:{response.status_code}"
    except Exception as e:
        return None, str(e)


async def get_cloud_token(session, ticket):
    """获取云盘token"""
    try:
        url = "https://panservice.mail.wo.cn/wohome/dispatcher"
        timestamp = str(int(time.time() * 1000))
        result = random.randint(123456, 199999)
        key = "HandheldHallAutoLogin"
        channel = "100002"
        client_id = "1001000035"

        string_to_hash = key + timestamp + str(result) + channel
        md5_hash = hashlib.md5()
        md5_hash.update(string_to_hash.encode('utf-8'))
        md5Hash = md5_hash.hexdigest()

        payload = {
            "header": {
                "key": key,
                "resTime": timestamp,
                "reqSeq": result,
                "channel": channel,
                "version": "",
                "sign": md5Hash
            },
            "body": {
                "clientId": client_id,
                "ticket": ticket
            }
        }
        headers = {
            'User-Agent': "LianTongYunPan/5.0.8 (Android 12)",
            'Content-Type': "application/json",
        }
        response = await session.post(url, headers=headers, json=payload)
        data = response.json()
        rsp_data = data.get("RSP", {}).get("DATA")
        if isinstance(rsp_data, dict):
            return rsp_data.get("token")
        return None
    except:
        return None


async def get_market_user_token(session, ecs_token):
    """获取权益超市userToken（用于抽奖记录查询，与脚本一致）"""
    try:
        from urllib.parse import urlparse, parse_qs
        # 获取ticket
        url = "https://m.client.10010.com/mobileService/openPlatform/openPlatLineNew.htm?to_url=https://contact.bol.wo.cn/market"
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Cookie': f'ecs_token={ecs_token}',
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
        }
        response = await session.get(url, headers=headers, follow_redirects=False)
        if response.status_code not in (301, 302, 303, 307, 308):
            return None
        
        location = response.headers.get('Location')
        if not location:
            return None
        
        parsed_url = urlparse(location)
        query_params = parse_qs(parsed_url.query)
        ticket = query_params.get('ticket', [None])[0]
        if not ticket:
            return None
        
        # 使用ticket获取userToken
        login_url = f"https://backward.bol.wo.cn/prod-api/auth/marketUnicomLogin?ticket={ticket}"
        login_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; Mi 10 Pro MIUI/21.11.3);unicom{version:android@11.0802}",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
        }
        for attempt in range(3):
            login_resp = await session.post(login_url, headers=login_headers)
            login_result = login_resp.json()
            if login_result.get("code") == 200:
                user_token = login_result.get("data", {}).get("token")
                if user_token:
                    return user_token
            if attempt < 2:
                await asyncio.sleep(2)
    except Exception as e:
        print(f"get_market_user_token error: {e}")
        return None
    return None


def parse_record_time(value):
    """解析奖品记录时间，用于统一排序。"""
    raw_value = str(value or '').strip()
    if not raw_value:
        return datetime.min
    normalized = raw_value.replace('T', ' ')
    if '.' in normalized:
        normalized = normalized.split('.', 1)[0]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(normalized, fmt)
        except ValueError:
            continue
    return datetime.min


def normalize_prize_records(records):
    """统一过滤、去重并按时间倒序整理中奖记录。"""
    normalized_records = []
    seen = set()
    for item in records or []:
        name = str(item.get('name') or '').strip()
        if not name or '谢谢参与' in name:
            continue
        time_value = str(item.get('time') or '').strip()
        normalized_item = dict(item)
        normalized_item['name'] = name
        normalized_item['time'] = time_value
        dedupe_key = (
            name,
            time_value,
            str(item.get('status') or ''),
            str(item.get('deadline') or ''),
        )
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        normalized_records.append(normalized_item)
    normalized_records.sort(key=lambda item: parse_record_time(item.get('time')), reverse=True)
    return normalized_records


def format_money_text(value):
    """格式化金额展示。"""
    if value is None:
        return "查询失败"
    return f"{value:.2f}元"


def format_cloud_score_text(available_score, all_score):
    """格式化云盘积分展示。"""
    if available_score is None and all_score is None:
        return "查询失败"
    current_value = available_score if available_score is not None else all_score
    total_value = all_score if all_score is not None else available_score
    if total_value is not None and current_value != total_value:
        return f"{current_value} (累计{total_value})"
    return str(current_value)


def format_record_date(value):
    """格式化记录日期显示。"""
    raw_value = str(value or '').strip()
    if not raw_value:
        return "未知时间"
    normalized = raw_value.replace('T', ' ')
    if '.' in normalized:
        normalized = normalized.split('.', 1)[0]
    return normalized[:10] if len(normalized) >= 10 else normalized


def build_record_section(title, icon, records, limit=5, include_status=False):
    """构建统一的记录展示区块。"""
    section_lines = [f"{icon} {title} {len(records)}条"]
    if not records:
        section_lines.append("暂无记录")
        return "\n".join(section_lines)

    display_records = records[:limit]
    for index, record in enumerate(display_records, 1):
        name = str(record.get('name') or '未知奖品').strip()
        line = f"{index}. {format_record_date(record.get('time'))}｜{name}"
        status = str(record.get('status') or '').strip()
        if include_status and status:
            line += f"｜{status}"
        section_lines.append(line)

    remaining = len(records) - len(display_records)
    if remaining > 0:
        section_lines.append(f"… 其余 {remaining} 条未展示")
    return "\n".join(section_lines)


def build_lottery_query_message(phone, market_records, cloud_records):
    """构建中奖记录查询消息。"""
    lines = [
        "=====中奖记录=====",
        f"📱 手机号: {mask_phone(phone)}",
        "------------------",
        build_record_section("权益超市", "🏪", market_records, limit=5, include_status=True),
        "------------------",
        build_record_section("云盘抽奖", "☁️", cloud_records, limit=5),
        "==================",
    ]
    return "\n".join(lines)


def build_account_query_message(phone, remark, auth_status, auth_time, result):
    """构建账号信息查询消息。"""
    market_records = result.get('market_records', [])
    cloud_records = result.get('cloud_records', [])
    sign_telephone = result.get('sign_telephone')
    ttlxj_available = result.get('ttlxj_available')
    woread_balance = result.get('woread_balance')
    watering_progress = result.get('watering_progress')
    cloud_all_score = result.get('cloud_all_score')
    cloud_available_score = result.get('cloud_available_score')

    lines = [
        "=====账号信息=====",
        f"👤 备注: {remark}",
        f"📱 手机号: {mask_phone(phone)}",
        f"🔐 授权: {auth_status}",
        f"📅 到期: {auth_time}",
        "------------------",
        "💰 资产概览",
        f"• 话费红包：{format_money_text(sign_telephone)}",
        f"• 阅读红包：{format_money_text(woread_balance)}",
        f"• 沃立减金：{format_money_text(ttlxj_available)}",
        f"• 浇花进度：{watering_progress if watering_progress else '查询失败'}",
        f"• 云盘积分：{format_cloud_score_text(cloud_available_score, cloud_all_score)}",
        "------------------",
        build_record_section("权益超市", "🏪", market_records, limit=5, include_status=True),
        "------------------",
        build_record_section("云盘抽奖", "☁️", cloud_records, limit=5),
        "==================",
    ]
    return "\n".join(lines)


async def query_raffle_records(session, user_token, mobile):
    """查询权益超市抽奖中奖记录（与联通日常脚本一致）"""
    try:
        url = "https://backward.bol.wo.cn/prod-api/market/contactReceive/queryReceiveRecord"
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; Mi 10 Pro MIUI/21.11.3);unicom{version:android@11.0802}",
            'Content-Type': "application/json",
            'Authorization': f'Bearer {user_token}',
            'Origin': "https://contact.bol.wo.cn",
            'Referer': "https://contact.bol.wo.cn/",
            'X-Requested-With': "com.sinovatech.unicom.ui",
        }
        payload = {
            "isReceive": None,
            "receiveStatus": None,
            "mobile": mobile,
            "businessSources": ["3", "4", "5", "6", "99"],
            "isPromotion": 1,
            "returnFormatType": 1,
            "page": 1,
            "limit": 100
        }
        response = await session.post(url, headers=headers, json=payload)
        data = response.json()
        if data.get("code") == 200:
            records = []
            for item in data.get("data", {}).get("recordObjs", []):
                records.append({
                    'id': item.get('id') or item.get('recordId'),
                    'name': item.get('recordName') or item.get('prizesName'),
                    'time': item.get('receiveTime') or item.get('createTime'),
                    'deadline': item.get('deadline'),
                    'status': item.get('receiveStatusName') or item.get('receiveStatus') or '',
                })
            return normalize_prize_records(records)
        return []
    except Exception as e:
        print(f"query_raffle_records error: {e}")
        return []


async def query_cloud_lottery_records(session, cloud_token, activity_id):
    """查询云盘抽奖中奖记录（与20251210联通云盘抽奖.py脚本一致）"""
    try:
        url = "https://panservice.mail.wo.cn/activity/lottery/recordList"
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Accept': "application/json, text/plain, */*",
            'requestTime': str(int(time.time() * 1000)),
            'clientId': "1001000165",
            'X-YP-Client-Id': "1001000165",
            'source-type': "woapi",
            'X-YP-Access-Token': cloud_token,
            'token': cloud_token,
        }
        params = {'activityId': activity_id}
        response = await session.get(url, headers=headers, params=params)
        data = response.json()
        if data.get("meta", {}).get("code") == "200":
            records = []
            for item in data.get("result", []):
                records.append({
                    'name': item.get('prizeName') or item.get('recordName'),
                    'time': item.get('createTime') or item.get('receiveTime'),
                })
            return normalize_prize_records(records)
        return []
    except Exception as e:
        print(f"query_cloud_lottery_records error: {e}")
        return []


async def query_sign_telephone(session, ecs_token):
    """查询签到区话费红包总额"""
    try:
        url = "https://act.10010.com/SigninApp/convert/getTelephone"
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Cookie': f'ecs_token={ecs_token}',
            'Content-Type': "application/x-www-form-urlencoded",
        }
        response = await session.post(url, headers=headers, data={})
        data = response.json()
        if data.get("status") == "0000" and data.get("data"):
            telephone_val = data["data"].get("telephone", 0)
            # 处理可能的字符串或None值
            try:
                telephone = float(telephone_val) if telephone_val else 0.0
            except (ValueError, TypeError):
                telephone = 0.0
            return telephone
        return None
    except Exception as e:
        print(f"query_sign_telephone error: {e}")
        return None


async def query_ttlxj_available(session, ecs_token, mobile):
    """查询天天领现金-可用立减金"""
    try:
        # 1. 通过openPlatLineNew获取ticket
        target_url = "https://epay.10010.com/ci-mps-st-web/?webViewNavIsHidden=webViewNavIsHidden"
        open_url = f"https://m.client.10010.com/mobileService/openPlatform/openPlatLineNew.htm?to_url={target_url}"
        open_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Cookie': f'ecs_token={ecs_token}',
        }
        open_resp = await session.get(open_url, headers=open_headers, follow_redirects=False)
        if open_resp.status_code not in (301, 302, 303, 307, 308):
            return None
        
        location = open_resp.headers.get('Location', '')
        if not location:
            return None
        
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(location)
        params = parse_qs(parsed.query)
        ticket = params.get('ticket', [None])[0]
        st_type = params.get('type', ['02'])[0]
        
        if not ticket:
            return None
        
        # 2. 进行authorize认证
        import secrets
        auth_url = "https://epay.10010.com/woauth2/v2/authorize"
        auth_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Content-Type': "application/json",
            'Origin': "https://epay.10010.com",
            'Referer': location,
        }
        auth_payload = {
            "response_type": "rptid",
            "client_id": "73b138fd-250c-4126-94e2-48cbcc8b9cbe",
            "redirect_uri": "https://epay.10010.com/ci-mps-st-web/",
            "login_hint": {
                "credential_type": "st_ticket",
                "credential": ticket,
                "st_type": st_type,
                "force_logout": True,
                "source": "app_sjyyt"
            },
            "device_info": {
                "token_id": f"chinaunicom-pro-{int(time.time()*1000)}-{secrets.token_hex(6)}",
                "trace_id": secrets.token_hex(16)
            }
        }
        auth_resp = await session.post(auth_url, headers=auth_headers, json=auth_payload)
        auth_data = auth_resp.json()
        if auth_data.get("status") != 200:
            return None
        
        # 3. 进行authCheck
        biz_info = json.dumps({
            "bizChannelCode": "225",
            "disriBiz": "party",
            "unionSessionId": "",
            "stType": "",
            "stDesmobile": "",
            "source": "",
            "rptId": "",
            "ticket": "",
            "tongdunTokenId": "",
            "xindunTokenId": ""
        })
        
        check_url = "https://epay.10010.com/ps-pafs-auth-front/v1/auth/check"
        check_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'bizchannelinfo': biz_info,
        }
        check_resp = await session.post(check_url, headers=check_headers)
        check_data = check_resp.json()
        
        session_id = ""
        token_id = ""
        
        if check_data.get("code") == "0000":
            auth_info_data = check_data.get("data", {}).get("authInfo", {})
            session_id = auth_info_data.get("sessionId", "")
            token_id = auth_info_data.get("tokenId", "")
        elif check_data.get("code") == "2101000100":
            # 需要进行login
            login_url_base = check_data.get("data", {}).get("woauth_login_url", "")
            if login_url_base:
                full_login_url = f"{login_url_base}https://epay.10010.com/ci-mcss-party-web/clockIn/?bizFrom=225&bizChannelCode=225"
                login_headers = {
                    'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
                }
                login_resp = await session.get(full_login_url, headers=login_headers, follow_redirects=False)
                if login_resp.status_code in (301, 302, 303, 307, 308):
                    login_location = login_resp.headers.get('Location', '')
                    if 'rptid=' in login_location:
                        # 从Location中提取rptid
                        parsed_login = urlparse(login_location)
                        login_params = parse_qs(parsed_login.query)
                        rpt_id = login_params.get('rptid', [''])[0]
                        
                        # 用新的rptId重新构建bizchannelinfo
                        biz_info = json.dumps({
                            "bizChannelCode": "225",
                            "disriBiz": "party",
                            "unionSessionId": "",
                            "stType": "",
                            "stDesmobile": "",
                            "source": "",
                            "rptId": rpt_id,
                            "ticket": "",
                            "tongdunTokenId": "",
                            "xindunTokenId": ""
                        })
                        
                        # 再次authCheck (带rptId)
                        check_headers2 = {
                            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
                            'bizchannelinfo': biz_info,
                        }
                        check_resp2 = await session.post(check_url, headers=check_headers2)
                        check_data2 = check_resp2.json()
                        if check_data2.get("code") == "0000":
                            auth_info_data = check_data2.get("data", {}).get("authInfo", {})
                            session_id = auth_info_data.get("sessionId", "")
                            token_id = auth_info_data.get("tokenId", "")
        
        if not session_id or not token_id:
            return None
        
        # 4. 查询可用立减金
        query_url = "https://epay.10010.com/ci-mcss-party-front/v1/ttlxj/queryAvailable"
        auth_info = json.dumps({
            "mobile": "",
            "sessionId": session_id,
            "tokenId": token_id,
            "userId": ""
        })
        query_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'bizchannelinfo': biz_info,
            'authinfo': auth_info,
        }
        query_resp = await session.post(query_url, headers=query_headers)
        query_data = query_resp.json()
        if query_data.get("code") == "0000" and str(query_data.get("data", {}).get("returnCode")) == "0":
            available_amount = int(query_data["data"].get("availableAmount", 0))
            return available_amount / 100  # 转换为元
        return None
    except Exception as e:
        print(f"query_ttlxj_available error: {e}")
        return None


async def query_woread_balance(session, token_online):
    """查询阅读区话费红包余额"""
    try:
        import hashlib as hl
        from Crypto.Cipher import AES
        from Crypto.Util.Padding import pad
        import cryptography
        
        # 阅读区加密参数
        default_password = "woreadst^&*12345"
        iv_string = "16-Bytes--String"
        product_id = "10000002"
        secret_key = "7k1HcDL8RKvc"
        
        def encode_woread_hex(data):
            """AES加密并返回hex再base64"""
            key_bytes = default_password[:16].encode('utf-8')
            iv_bytes = iv_string.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            if isinstance(data, dict):
                json_str = json.dumps(data)
            else:
                json_str = str(data)
            padded = pad(json_str.encode('utf-8'), AES.block_size)
            encrypted = cipher.encrypt(padded)
            hex_str = encrypted.hex()
            return base64.b64encode(hex_str.encode('utf-8')).decode('utf-8')
        
        # 1. 设备认证 - 使用app/auth接口
        timestamp = int(time.time() * 1000)
        sign_str = f"{product_id}{secret_key}{timestamp}"
        md5_hash = hl.md5(sign_str.encode()).hexdigest()
        
        date_str = datetime.now().strftime('%Y%m%d%H%M%S')
        crypt_text = {"timestamp": date_str}
        encoded_sign = encode_woread_hex(crypt_text)
        
        auth_url = f"https://10010.woread.com.cn/ng_woread_service/rest/app/auth/{product_id}/{timestamp}/{md5_hash}"
        auth_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Content-Type': "application/json",
        }
        auth_resp = await session.post(auth_url, headers=auth_headers, json={"sign": encoded_sign})
        auth_data = auth_resp.json()
        if auth_data.get("code") != "0000":
            return None
        
        access_token = auth_data.get("data", {}).get("accesstoken")
        if not access_token:
            return None
        
        # 2. 账号登录
        def encode_woread_str(text):
            """单字符串加密"""
            key_bytes = default_password[:16].encode('utf-8')
            iv_bytes = iv_string.encode('utf-8')
            cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
            padded = pad(text.encode('utf-8'), AES.block_size)
            encrypted = cipher.encrypt(padded)
            hex_str = encrypted.hex()
            return base64.b64encode(hex_str.encode('utf-8')).decode('utf-8')
        
        token_enc = encode_woread_str(token_online)
        phone_enc = encode_woread_str("13800000000")
        login_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        inner_json = json.dumps({
            "tokenOnline": token_enc,
            "phone": phone_enc,
            "timestamp": login_timestamp
        })
        login_sign = encode_woread_str(inner_json)
        
        login_url = "https://10010.woread.com.cn/ng_woread_service/rest/account/login"
        login_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Content-Type': "application/json",
            'accesstoken': access_token,
        }
        login_resp = await session.post(login_url, headers=login_headers, json={"sign": login_sign})
        login_data = login_resp.json()
        if login_data.get("code") != "0000":
            return None
        
        woread_token = login_data.get("data", {}).get("token")
        woread_userid = login_data.get("data", {}).get("userid")
        woread_userindex = login_data.get("data", {}).get("userindex")
        woread_verifycode = login_data.get("data", {}).get("verifycode")
        
        if not woread_token:
            return None
        
        # 3. 查询话费红包余额
        query_param = {
            "timestamp": datetime.now().strftime('%Y%m%d%H%M%S'),
            "token": woread_token,
            "userid": woread_userid,
            "userId": woread_userid,
            "userIndex": woread_userindex,
            "userAccount": "",
            "verifyCode": woread_verifycode
        }
        query_sign = encode_woread_hex(query_param)
        query_url = "https://10010.woread.com.cn/ng_woread_service/rest/phone/vouchers/queryTicketAccount"
        query_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Content-Type': "application/json",
            'accesstoken': access_token,
        }
        query_resp = await session.post(query_url, headers=query_headers, json={"sign": query_sign})
        query_data = query_resp.json()
        if query_data.get("code") == "0000":
            usable_num = query_data.get("data", {}).get("usableNum", 0)
            return usable_num / 100  # 转换为元
        return None
    except Exception as e:
        print(f"query_woread_balance error: {e}")
        return None


async def query_watering_progress(session, user_token):
    """查询权益超市浇花进度"""
    try:
        url = "https://backward.bol.wo.cn/prod-api/promotion/activityTask/getMultiCycleProcess?activityId=13"
        headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Authorization': f'Bearer {user_token}',
        }
        response = await session.get(url, headers=headers)
        data = response.json()
        if data.get("code") == 200 and data.get("data"):
            triggered_time = data["data"].get("triggeredTime", 0)
            trigger_time = data["data"].get("triggerTime", 0)
            return triggered_time, trigger_time
        return None, None
    except Exception as e:
        print(f"query_watering_progress error: {e}")
        return None, None


async def query_cloud_points(session, ecs_token):
    """查询云盘任务积分（完整流程）"""
    try:
        # 1. 获取ticket (通过getTicketByNative)
        ticket_url = f"https://m.client.10010.com/edop_ng/getTicketByNative?appId=edop_unicom_d67b3e30&token={ecs_token}"
        ticket_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Connection': "Keep-Alive",
            'Accept-Encoding': "gzip",
        }
        ticket_resp = await session.get(ticket_url, headers=ticket_headers)
        ticket_data = ticket_resp.json()
        ticket = ticket_data.get("ticket")
        if not ticket:
            return None, None
        
        # 2. 获取云盘token (通过ltypDispatcher)
        timestamp = str(int(time.time() * 1000))
        result_num = random.randint(123456, 199999)
        string_to_hash = f"HandheldHallAutoLoginV2{timestamp}{result_num}wohome"
        md5_hash = hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()
        
        dispatcher_url = "https://panservice.mail.wo.cn/wohome/dispatcher"
        dispatcher_payload = {
            "header": {
                "key": "HandheldHallAutoLoginV2",
                "resTime": timestamp,
                "reqSeq": result_num,
                "channel": "wohome",
                "version": "",
                "sign": md5_hash
            },
            "body": {
                "clientId": "1001000003",
                "ticket": ticket
            }
        }
        dispatcher_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Content-Type': "application/json",
        }
        dispatcher_resp = await session.post(dispatcher_url, headers=dispatcher_headers, json=dispatcher_payload)
        dispatcher_data = dispatcher_resp.json()
        user_token = dispatcher_data.get("RSP", {}).get("DATA", {}).get("token")
        if not user_token:
            return None, None
        
        # 3. 获取userticket
        userticket_url = "https://panservice.mail.wo.cn/api-user/api/user/ticket"
        userticket_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Content-Type': 'application/json',
            'X-YP-Access-Token': user_token,
            'accesstoken': user_token,
            'token': user_token,
            'clientId': "1001000003",
            'X-YP-Client-Id': "1001000003",
            'source-type': "woapi",
            'app-type': "unicom"
        }
        userticket_resp = await session.post(userticket_url, headers=userticket_headers, json={})
        userticket_data = userticket_resp.json()
        user_ticket = userticket_data.get("result", {}).get("ticket")
        if not user_ticket:
            return None, None
        
        # 4. 查询用户积分信息
        userinfo_url = "https://m.jf.10010.com/jf-external-application/jftask/userInfo"
        userinfo_headers = {
            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
            'Content-Type': 'application/json;charset=UTF-8',
            'ticket': user_ticket,
            'partnersid': "1649",
            'origin': "https://m.jf.10010.com",
            'clienttype': "yunpan_android",
            'x-requested-with': "com.sinovatech.unicom.ui"
        }
        userinfo_resp = await session.post(userinfo_url, headers=userinfo_headers, json={})
        userinfo_data = userinfo_resp.json()
        
        if userinfo_data.get("data"):
            all_earn_score = userinfo_data["data"].get("allEarnScore", 0)
            available_score = userinfo_data["data"].get("availableScore", 0)
            return all_earn_score, available_score
        return None, None
    except Exception as e:
        print(f"query_cloud_points error: {e}")
        return None, None


async def query_cloud_records(token_online, original_phone=None):
    """查询账号信息（包含各类余额和中奖记录）"""
    try:
        async with httpx.AsyncClient(timeout=30, verify=False) as session:
            # 获取ecs_token和手机号
            phone, ecs_token, err = await get_ecstoken(session, token_online)
            if not ecs_token:
                return None, err or "获取ecs_token失败"
            query_phone = original_phone or phone

            result = {
                'phone': phone, 
                'market_records': [], 
                'cloud_records': [],
                # 新增查询字段
                'sign_telephone': None,  # 签到区话费红包
                'ttlxj_available': None,  # 天天领现金-立减金
                'woread_balance': None,  # 阅读区话费红包余额
                'watering_progress': None,  # 浇花进度
                'cloud_all_score': None,  # 云盘已赚积分
                'cloud_available_score': None,  # 云盘可用积分
            }

            # 1. 查询签到区话费红包
            sign_telephone = await query_sign_telephone(session, ecs_token)
            result['sign_telephone'] = sign_telephone

            # 2. 查询天天领现金-立减金
            ttlxj_available = await query_ttlxj_available(session, ecs_token, phone)
            result['ttlxj_available'] = ttlxj_available

            # 3. 查询阅读区话费红包余额
            woread_balance = await query_woread_balance(session, token_online)
            result['woread_balance'] = woread_balance

            # 4. 查询权益超市相关
            user_token = await get_market_user_token(session, ecs_token)
            if user_token:
                # 查询抽奖记录
                market_records = await query_raffle_records(session, user_token, query_phone)
                result['market_records'] = normalize_prize_records(market_records)
                
                # 查询浇花进度
                triggered, trigger = await query_watering_progress(session, user_token)
                if triggered is not None and trigger is not None:
                    result['watering_progress'] = f"{triggered}/{trigger}"

            # 5. 查询云盘相关
            # 查询云盘积分（使用ecs_token，独立流程）
            all_score, available_score = await query_cloud_points(session, ecs_token)
            result['cloud_all_score'] = all_score
            result['cloud_available_score'] = available_score
            
            # 查询云盘抽奖记录
            ticket, _ = await get_ticket(session, ecs_token)
            if ticket:
                cloud_token = await get_cloud_token(session, ticket)
                if cloud_token:
                    activity_ids = ['MTg=', 'MTk=', 'MjU=']
                    all_cloud_records = []
                    for aid in activity_ids:
                        records = await query_cloud_lottery_records(session, cloud_token, aid)
                        all_cloud_records.extend(records)
                    result['cloud_records'] = normalize_prize_records(all_cloud_records)

            return result, None
    except Exception as e:
        return None, str(e)


# ========== 插件主逻辑 ==========
def bind_account():
    """绑定联通账号"""
    login_by_token()


def _parse_login_line(line):
    parts = [p.strip() for p in line.split('#')]
    count = len(parts)

    def _is_phone(s):
        return bool(re.match(r'^1[3-9]\d{9}$', s))

    def _is_captcha(s):
        return bool(re.match(r'^\d{4,8}$', s))

    def _is_long_token(s):
        return len(s) > 100

    if count >= 5 and _is_phone(parts[0]) and _is_captcha(parts[1]) and _is_long_token(parts[2]):
        return parts[0], parts[0][-4:], parts[2]

    if count >= 6 and _is_phone(parts[1]) and _is_captcha(parts[2]) and _is_long_token(parts[3]):
        return parts[0], parts[0], parts[3]

    if count >= 2 and _is_long_token(parts[0]):
        return None, parts[0][-8:], parts[0]

    if count >= 3 and _is_long_token(parts[1]):
        return parts[0], parts[0], parts[1]

    if count >= 2:
        return parts[0], parts[0], parts[1]

    return None, None, None


def login_by_token():
    sender.reply("""
=====Token登录=====
当前版本仅支持 Token 登录
🌐 获取Token: https://api.5gyh.cf/dl.php
   打开网站 → 验证码登录 → 复制Token数据
------------------
📋 支持以下格式(直接粘贴网站数据即可):
  ① 备注#token_online
  ② 手机号#验证码#token_online#ecs_token#appid
  ③ token_online#appid
💡 格式②③为网站直接复制的数据
💡 支持批量登录(换行分割)
------------------
回复"q"退出
==================""")

    user_input = sender.input(120000, 1, False)
    if not user_input:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif user_input.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return

    lines = [line.strip() for line in user_input.split('\n') if line.strip()]
    if not lines:
        sender.reply("❌ 格式错误\n请输入Token数据")
        return

    total = len(lines)
    success_count = 0
    fail_count = 0

    for line in lines:
        if '#' not in line:
            sender.reply(f"❌ 格式错误，跳过: {line[:30]}...")
            fail_count += 1
            continue

        phone_hint, remark, token_online = _parse_login_line(line)

        if not token_online:
            sender.reply("❌ 无法识别Token，请检查格式")
            fail_count += 1
            continue

        if not remark:
            remark = token_online[-8:]

        try:
            async def verify_token():
                async with httpx.AsyncClient(verify=False, timeout=30) as session:
                    try:
                        url = "https://m.client.10010.com/mobileService/onLine.htm"
                        payload = {
                            'isFirstInstall': "1",
                            'version': "android@11.0702",
                            'token_online': token_online
                        }
                        headers = {
                            'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; leijun Pro Build/SKQ1.22013.001);unicom{version:android@11.0702}",
                            'Connection': "Keep-Alive",
                            'Accept-Encoding': "gzip",
                            'Content-Type': "application/x-www-form-urlencoded",
                        }
                        response = await session.post(url, data=payload, headers=headers)
                        response_text = response.text

                        try:
                            data = json.loads(response_text)
                        except:
                            return None, None, f"返回非JSON格式: {response_text[:100]}"

                        code = data.get("code")
                        if code == "9999" or code == "ECS99999":
                            return None, None, f"Token已失效 [code:{code}]"

                        desmobile = data.get("desmobile")
                        ecs_token = data.get("ecs_token")

                        if not ecs_token:
                            error_msg = data.get("dsc") or data.get("msg") or "未返回ecs_token,可能Token已经失效了"
                            return None, None, f"{error_msg} [code:{code}]"

                        if not desmobile:
                            return None, None, f"未返回手机号 [code:{code}]"

                        return desmobile, ecs_token, None
                    except Exception as e:
                        return None, None, f"请求异常: {str(e)}"

            phone, ecs_token, error = asyncio.run(verify_token())

            if error or not phone:
                sender.reply(f"❌ {remark} Token验证失败\n原因: {error or 'Token无效或已过期'}")
                fail_count += 1
                continue

            _save_token_account(phone, token_online, ecs_token, remark)
            success_count += 1
            sender.reply(f"✅ {remark} ({mask_phone(phone)}) 登录成功 [{success_count + fail_count}/{total}]")

        except Exception as e:
            sender.reply(f"❌ {remark} 登录异常\n错误: {str(e)}")
            fail_count += 1
            continue

    if total > 1:
        sender.reply(f"=====批量登录完成=====\n✅ 成功: {success_count}\n❌ 失败: {fail_count}\n==================")


def _save_token_account(phone, token_online, ecs_token, remark):
    """保存Token登录的账号信息"""
    global uservalue
    
    # 保存到用户账号列表
    if not uservalue:
        accounts = [phone]
    else:
        accounts = eval(uservalue)
        if phone not in accounts:
            accounts.append(phone)
    uservalue = str(accounts)
    middleware.bucketSet('dd_ltyp_user', userid, uservalue)
    
    # 保存账号详细信息
    account_info = {
        "phone": phone,
        "remark": remark,
        "token_online": token_online,
        "ecs_token": ecs_token,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    middleware.bucketSet('dd_ltyp_token', phone, json.dumps(account_info))
    
    # 检查是否已授权，只有已授权账号才提交到青龙
    today_time = str(datetime.now().date())
    account_vip = middleware.bucketGet('dd_ltyp_auth', phone)
    
    if account_vip and account_vip > today_time:
        # 已授权账号，提交到青龙
        ql_url, ql_token, var_name = init_qinglong()
        if ql_url and ql_token:
            add_to_qinglong(ql_url, ql_token, var_name, token_online, phone, remark, ecs_token, account_vip)


def manage_account():
    """账号管理功能"""
    from decimal import Decimal
    
    if not uservalue:
        sender.reply("""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 联通登录 绑定账号
==================""")
        return

    accounts = eval(uservalue)
    today_time = str(datetime.now().date())
    
    # 获取配置
    var_name, ql_config, zsm, vip_money, vip_coin, use_ma_pay = get_full_config()
    
    account_list = """
=====我的联通账号=====
[0] 🎯 批量授权所有账号"""

    for i, phone in enumerate(accounts, 1):
        account_data = middleware.bucketGet('dd_ltyp_token', phone)
        account_vip = middleware.bucketGet('dd_ltyp_auth', phone)
        auth_status, auth_time = get_auth_status(account_vip, today_time)
        
        if account_data:
            account_info = json.loads(account_data)
            remark = account_info.get('remark', phone)
        else:
            remark = phone

        account_list += f"""
------------------
[{i}] 账号信息
📱 手机号: {mask_phone(phone)}
👤 备注: {remark}
⏰ 授权: {auth_status}"""

    account_list += """
==================
回复数字选择账号
回复"q"退出操作"""

    sender.reply(account_list)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出管理")
        return

    try:
        me_as_int = int(choice)
        if me_as_int < 0 or me_as_int > len(accounts):
            sender.reply("❌ 无效的选择")
            return
        
        # 批量授权
        if me_as_int == 0:
            batch_auth_guide = """
=====批量授权设置=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
            sender.reply(batch_auth_guide)
            
            mes = sender.input(120000, 1, False)
            if not mes or mes.lower() == 'q':
                sender.reply("✅ 已取消操作")
                return
            
            try:
                mes = int(mes)
                if mes <= 0:
                    sender.reply("❌ 月数必须大于0")
                    return
            except ValueError:
                sender.reply("❌ 请输入正确的数字")
                return
            
            total_money = Decimal(mes) * vip_money * len(accounts)
            
            confirm_msg = f"""
=====批量授权确认=====
📊 账号数量: {len(accounts)}个
⏰ 授权时长: {mes}月/每个账号
💰 总计金额: {total_money}元
------------------
确认批量授权？
[y] 确认授权
[n] 取消操作
=================="""
            sender.reply(confirm_msg)
            
            confirm = sender.input(60000, 1, False)
            if confirm and confirm.lower() == 'y':
                batch_payment(accounts=accounts, months=mes, total_money=total_money)
            else:
                sender.reply("✅ 已取消批量授权")
        else:
            phone = accounts[me_as_int - 1]
            show_account_menu(phone, accounts)

    except ValueError:
        sender.reply("❌ 无效的选择")


def show_account_menu(phone, accounts):
    """显示账号操作菜单"""
    from decimal import Decimal
    
    today_time = str(datetime.now().date())
    account_vip = middleware.bucketGet('dd_ltyp_auth', phone)
    auth_status, auth_time = get_auth_status(account_vip, today_time)
    
    menu = f"""
=====账号管理=====
📱 手机号: {mask_phone(phone)}
🔐 授权: {auth_status}
------------------
[1] 授权账号
[2] 提交青龙
[3] 查询中奖
[4] 删除账号
------------------
回复数字选择功能
回复"q"退出操作
=================="""
    sender.reply(menu)

    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        return

    account_data = middleware.bucketGet('dd_ltyp_token', phone)
    if not account_data:
        sender.reply("❌ 账号信息不存在")
        return
    account_info = json.loads(account_data)

    if choice == '1':
        # 授权账号
        var_name, ql_config, zsm, vip_money, vip_coin, use_ma_pay = get_full_config()
        
        auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
        sender.reply(auth_guide)
        
        mes = sender.input(120000, 1, False)
        if not mes or mes.lower() == 'q':
            sender.reply("✅ 已取消操作")
            return
        
        try:
            mes = int(mes)
            if mes <= 0:
                sender.reply("❌ 月数必须大于0")
                return
        except ValueError:
            sender.reply("❌ 请输入正确的数字")
            return
        
        money = Decimal(mes) * vip_money
        token_online = account_info.get('token_online')
        ecs_token = account_info.get('ecs_token')
        
        # 执行支付
        process_payment(
            project='联通授权',
            me_as_int=mes,
            account_vip=account_vip or '',
            token=token_online,
            phone=phone,
            account=phone,
            money=money,
            vip_money=vip_money,
            vip_coin=vip_coin,
            ecs_token=ecs_token
        )

    elif choice == '2':
        # 提交青龙
        account_vip = middleware.bucketGet('dd_ltyp_auth', phone)
        if not account_vip or account_vip <= today_time:
            sender.reply("❌ 账号未授权或已过期，请先授权")
            return
        
        ql_url, ql_token, var_name = init_qinglong()
        if not ql_url:
            sender.reply("❌ 未配置青龙信息")
            return

        token_online = account_info.get('token_online')
        ecs_token = account_info.get('ecs_token')
        if not token_online:
            sender.reply("❌ 未获取到Token，请重新登录")
            return

        if add_to_qinglong(ql_url, ql_token, var_name, token_online, phone, account_info.get('remark', ''), ecs_token, account_vip):
            sender.reply(f"""
=====提交成功=====
📱 手机号: {mask_phone(phone)}
✅ 已同步到青龙
==================""")
        else:
            sender.reply(f"""
=====提交失败=====
📱 手机号: {mask_phone(phone)}
❌ 青龙操作失败
==================""")

    elif choice == '3':
        # 查询中奖
        token_online = account_info.get('token_online')
        if not token_online:
            sender.reply("❌ 未获取到Token，请重新登录")
            return

        result, error = asyncio.run(query_cloud_records(token_online, phone))
        if error:
            sender.reply(f"""
=====查询失败=====
📱 手机号: {mask_phone(phone)}
❌ 原因: {error}
==================""")
            return

        market_records = result.get('market_records', [])
        cloud_records = result.get('cloud_records', [])
        sender.reply(build_lottery_query_message(phone, market_records, cloud_records))

    elif choice == '4':
        # 删除账号
        confirm = """
=====确认删除=====
⚠️ 此操作不可恢复
------------------
回复 y 确认删除
回复 n 取消操作
=================="""
        sender.reply(confirm)

        confirm_input = sender.input(60000, 1, False)
        if confirm_input and confirm_input.lower() == 'y':
            accounts.remove(phone)
            if accounts:
                middleware.bucketSet('dd_ltyp_user', userid, str(accounts))
            else:
                middleware.bucketDel('dd_ltyp_user', userid)

            middleware.bucketDel('dd_ltyp_token', phone)
            middleware.bucketDel('dd_ltyp_auth', phone)

            # 删除青龙变量
            ql_url, ql_token, var_name = init_qinglong()
            if ql_url and ql_token:
                delete_from_qinglong(ql_url, ql_token, var_name, phone)

            sender.reply("✅ 账号已删除")
        else:
            sender.reply("✅ 已取消删除")

    else:
        sender.reply("❌ 无效的选择")


def process_payment(project, me_as_int, account_vip, token, phone, account, money, vip_money, vip_coin, ecs_token=None):
    """处理单个账号支付流程"""
    from decimal import Decimal
    
    # 检查是否为免费授权（价格为0）
    if money == 0:
        # 免费授权，直接处理
        new_vip = empower(empowertime=account_vip, me_as_int=me_as_int)
        middleware.bucketSet('dd_ltyp_auth', account, new_vip)
        
        # 更新青龙变量
        ql_url, ql_token, var_name = init_qinglong()
        if ql_url and ql_token and token:
            add_to_qinglong(ql_url, ql_token, var_name, token, phone, '', ecs_token, new_vip)
        
        sender.reply(f"""
=====免费授权成功=====
🎫 商品: {project}
💰 金额: 免费
⏰ 授权时长: {me_as_int}月
📅 到期时间: {new_vip}
==================""")
        return True
    
    # 获取支付配置
    zsm, use_ma_pay, ma_pay_config = get_payment_config()
    
    if not zsm and not use_ma_pay:
        sender.reply("❌ 未配置收款方式,请联系管理员!")
        return False
    
    # 检查是否允许使用积分支付
    usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
    zfcoin = vip_coin * me_as_int if vip_coin else 0
    
    # 构建支付选择菜单
    pay_menu = "=====选择支付方式====="
    option_num = 1
    options_map = {}

    # 添加微信支付选项
    if zsm:
        pay_menu += f"\n{option_num}️⃣ 微信支付\n   💰 {money}元/{me_as_int}月"
        options_map[str(option_num)] = 'wechat'
        option_num += 1
        
    # 添加码支付选项
    if use_ma_pay and ma_pay_config:
        pay_menu += f"\n{option_num}️⃣ 码支付\n   💰 {money}元/{me_as_int}月"
        options_map[str(option_num)] = 'ma'
        option_num += 1
        
    # 积分支付选项
    if vip_coin and vip_coin > 0:
        pay_menu += f"\n{option_num}️⃣ 积分支付\n   🎯 {zfcoin}积分/{me_as_int}月\n   💫 当前积分: {usercoin}"
        options_map[str(option_num)] = 'points'
        
    pay_menu += "\n------------------\n回复数字选择方式\n回复'q'退出操作\n=================="

    sender.reply(pay_menu)
    choice = sender.input(60000, 1, False)
    
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消支付")
        return False
        
    selected_pay = options_map.get(choice)
    
    if selected_pay == 'wechat' and zsm:
        # 微信支付流程
        zfzt = sender.atWaitPay()
        if zfzt:
            sender.reply("⚠️ 当前有人正在支付,请稍后再试！")
            return False
            
        pay_msg = f"""
=====微信扫码支付====
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
            sender.reply("✅ 已取消支付")
            return False
            
        Money, Time, From = parse_payment_result(ddzf)
        if Money is None:
            sender.reply("❌ 不支持的支付消息格式")
            return False
            
        if float(Money) >= float(money):
            new_vip = empower(empowertime=account_vip, me_as_int=me_as_int)
            middleware.bucketSet('dd_ltyp_auth', account, new_vip)
            
            # 更新青龙变量
            ql_url, ql_token, var_name = init_qinglong()
            if ql_url and ql_token and token:
                add_to_qinglong(ql_url, ql_token, var_name, token, phone, '', ecs_token, new_vip)
            
            result_msg = f"""
=====支付成功=====
🎫 商品: {project}
💰 金额: {Money}元
⏰ 时间: {Time}
📅 到期时间: {new_vip}
{f'👤 付款人: {From}' if From else ''}
=================="""
            sender.reply(result_msg)
            return True
        else:
            sender.reply(f"""
=====支付金额错误=====
💰 应付: {money}元
💳 实付: {Money}元
{f'👤 付款人: {From}' if From else ''}

❗ 请联系管理员处理退款！
==================""")
            return False
            
    elif selected_pay == 'ma' and use_ma_pay and ma_pay_config:
        # 码支付流程
        out_trade_no = f"LTYP{int(time.time())}{userid}"
        
        params = {
            'pid': ma_pay_config['pid'],
            'type': ma_pay_config['type'].split(',')[0],
            'out_trade_no': out_trade_no,
            'name': f"{senderID}-联通权益授权-{str(money)}",
            'money': str(money),
            'param': userid
        }
        
        # 添加回调地址（如果有配置）
        if ma_pay_config.get('notify_url'):
            params['notify_url'] = ma_pay_config['notify_url']
        if ma_pay_config.get('return_url'):
            params['return_url'] = ma_pay_config['return_url']
        
        # 移除空值参数
        params = {k: v for k, v in params.items() if v}
        
        # 按照ASCII码排序参数
        sorted_params = dict(sorted(params.items(), key=lambda x: x[0]))
        sign_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
        
        params['sign'] = sign
        params['sign_type'] = 'MD5'
        
        gateway = ma_pay_config['gateway']
        if gateway.endswith('/'):
            gateway = gateway[:-1]
        mapi_url = f"{gateway}/mapi.php"
        
        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            response = requests.post(mapi_url, data=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                sender.reply(f"❌ 创建支付订单失败，HTTP状态码: {response.status_code}")
                return False
            
            result = response.json()
            code = result.get('code', 0)
            msg = result.get('msg', '未知状态')
            
            if code == 1:
                payurl = result.get('payurl', '')
                if not payurl:
                    sender.reply("❌ 未获取到支付链接")
                    return False
                
                qrcode_url = generate_qrcode(payurl)
                pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
                
                if qrcode_url:
                    send_qrcode_image(sender, qrcode_url, pay_type)
                else:
                    sender.reply(f"""=====码支付=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 有效期: 5分钟
------------------
二维码生成失败，请点击链接完成支付:
{payurl}
==================""")
            else:
                sender.reply(f"❌ 创建订单失败: {msg}")
                return False
            
            # 轮询订单状态
            for i in range(60):
                check_url = gateway
                if '/xpay/epay/api.php' not in check_url:
                    check_url = f"{check_url}/xpay/epay/api.php"
                
                check_params = {
                    'act': 'order',
                    'pid': ma_pay_config['pid'],
                    'key': ma_pay_config['key'],
                    'out_trade_no': out_trade_no
                }
                
                try:
                    check_resp = requests.get(check_url, params=check_params, timeout=10)
                    check_result = check_resp.json()
                    
                    if check_result.get('code') == 1 and check_result.get('status') == 1:
                        new_vip = empower(empowertime=account_vip, me_as_int=me_as_int)
                        middleware.bucketSet('dd_ltyp_auth', account, new_vip)
                        
                        ql_url, ql_token, var_name = init_qinglong()
                        if ql_url and ql_token and token:
                            add_to_qinglong(ql_url, ql_token, var_name, token, phone, '', ecs_token, new_vip)
                        
                        sender.reply(f"""=====支付成功=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 授权时长: {me_as_int}月
📅 到期时间: {new_vip}
==================""")
                        return True
                except Exception as e:
                    print(f"查询订单状态出错: {str(e)}")
                
                result = sender.listen(5000)
                if result == 'q' or result == 'Q':
                    sender.reply("✅ 已取消支付")
                    return False
            
            sender.reply("❌ 支付超时,请重新发起支付!")
            return False
        except Exception as e:
            sender.reply(f"❌ 支付请求失败: {str(e)}")
            return False
            
    elif selected_pay == 'points' and vip_coin and vip_coin > 0:
        # 积分支付流程
        if int(usercoin) < zfcoin:
            sender.reply(f"""
=====积分不足=====
💫 当前积分: {usercoin}
🎯 需要积分: {zfcoin}
==================""")
            return False
            
        confirm_msg = f"""
=====积分支付确认=====
💰 消耗积分: {zfcoin}
⏰ 授权时长: {me_as_int}月
------------------
确认请回复【y】
取消请回复【n】
=================="""
        sender.reply(confirm_msg)
        
        confirm = sender.input(60000, 1, False)
        if confirm and confirm.lower() == 'y':
            try:
                new_balance = int(usercoin) - zfcoin
                middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                new_vip = empower(empowertime=account_vip, me_as_int=me_as_int)
                middleware.bucketSet('dd_ltyp_auth', account, new_vip)
                
                ql_url, ql_token, var_name = init_qinglong()
                if ql_url and ql_token and token:
                    add_to_qinglong(ql_url, ql_token, var_name, token, phone, '', ecs_token, new_vip)
                
                result_msg = f"""
=====支付成功=====
💫 扣除积分: {zfcoin}
💰 剩余积分: {new_balance}
⏰ 授权时长: {me_as_int}月
📅 到期时间: {new_vip}
=================="""
                sender.reply(result_msg)
                return True
            except Exception as e:
                sender.reply(f"❌ 积分处理失败: {str(e)}")
                return False
        else:
            sender.reply("✅ 已取消支付")
            return False
    else:
        sender.reply("❌ 请输入正确的选项")
        return False


def batch_payment(accounts, months, total_money):
    """处理批量支付流程"""
    from decimal import Decimal
    
    var_name, ql_config, zsm, vip_money, vip_coin, use_ma_pay = get_full_config()
    
    # 检查是否为免费授权
    if total_money == 0:
        success_count = 0
        for account in accounts:
            try:
                account_vip = middleware.bucketGet('dd_ltyp_auth', account) or ''
                account_data = middleware.bucketGet('dd_ltyp_token', account)
                account_json = json.loads(account_data) if account_data else {}
                token = account_json.get('token_online')
                ecs_token = account_json.get('ecs_token')
                
                new_vip = empower(empowertime=account_vip, me_as_int=months)
                middleware.bucketSet('dd_ltyp_auth', account, new_vip)
                
                ql_url, ql_token, var_name = init_qinglong()
                if ql_url and ql_token and token:
                    add_to_qinglong(ql_url, ql_token, var_name, token, account, '', ecs_token, new_vip)
                success_count += 1
            except:
                continue
        
        sender.reply(f"""
=====批量授权成功=====
🎫 商品: 联通批量授权
💰 金额: 免费
📊 成功: {success_count}/{len(accounts)}个账号
⏰ 授权时长: {months}月/每个账号
==================""")
        return True
    
    # 获取支付配置
    zsm_config, use_ma_pay, ma_pay_config = get_payment_config()
    
    if not zsm_config and not use_ma_pay:
        sender.reply("❌ 未配置收款方式,请联系管理员!")
        return False
    
    usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
    zfcoin = vip_coin * months * len(accounts) if vip_coin else 0
    
    pay_menu = f"""
=====选择支付方式====
💰 联通批量授权总金额: {total_money}元
📊 账号数量: {len(accounts)}个
⏰ 每账号时长: {months}月"""
    option_num = 1
    options_map = {}

    if zsm_config:
        pay_menu += f"""
------------------
{option_num}️⃣ 微信支付
   💰 {total_money}元"""
        options_map[str(option_num)] = 'wechat'
        option_num += 1
        
    if use_ma_pay and ma_pay_config:
        pay_menu += f"""
{option_num}️⃣ 码支付
   💰 {total_money}元"""
        options_map[str(option_num)] = 'ma'
        option_num += 1
        
    if vip_coin and vip_coin > 0:
        pay_menu += f"""
{option_num}️⃣ 积分支付  
   🎯 {zfcoin}积分
   💫 当前积分: {usercoin}"""
        options_map[str(option_num)] = 'points'
        
    pay_menu += """
------------------
回复数字选择方式
回复"q"退出操作
=================="""

    sender.reply(pay_menu)
    choice = sender.input(60000, 1, False)
    
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已取消支付")
        return False
        
    selected_pay = options_map.get(choice)
    
    if selected_pay == 'wechat' and zsm_config:
        zfzt = sender.atWaitPay()
        if zfzt:
            sender.reply('⚠️ 当前有人正在支付,请稍后再试！')
            return False
            
        pay_msg = f"""
=====微信扫码支付====
🎫 商品: 联通批量授权
📊 账号数量: {len(accounts)}个
⏰ 时长: {months}月/每个账号
💰 总金额: {total_money}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
        sender.reply(pay_msg)
        sender.replyImage(zsm_config)
        
        ddzf = sender.waitPay("q", 100 * 1000)
        
        if str(ddzf) == 'q':
            sender.reply('✅ 已取消支付')
            return False
            
        Money, Time, From = parse_payment_result(ddzf)
        if Money is None:
            sender.reply("❌ 无法解析支付结果")
            return False
            
        if float(Money) >= float(total_money):
            success_count = 0
            for account in accounts:
                try:
                    account_vip = middleware.bucketGet('dd_ltyp_auth', account) or ''
                    account_data = middleware.bucketGet('dd_ltyp_token', account)
                    account_json = json.loads(account_data) if account_data else {}
                    token = account_json.get('token_online')
                    ecs_token = account_json.get('ecs_token')
                    
                    new_vip = empower(empowertime=account_vip, me_as_int=months)
                    middleware.bucketSet('dd_ltyp_auth', account, new_vip)
                    
                    ql_url, ql_token, var_name = init_qinglong()
                    if ql_url and ql_token and token:
                        add_to_qinglong(ql_url, ql_token, var_name, token, account, '', ecs_token, new_vip)
                    success_count += 1
                except:
                    continue
            
            result_msg = f"""
=====支付成功=====
🎫 商品: 联通批量授权
💰 金额: {Money}元
📊 成功: {success_count}/{len(accounts)}个账号
⏰ 时间: {Time}
{f'👤 付款人: {From}' if From else ''}
=================="""
            sender.reply(result_msg)
            return True
        else:
            sender.reply(f"""
=====支付金额错误=====
💰 应付: {total_money}元
💳 实付: {Money}元
{f'👤 付款人: {From}' if From else ''}

❗ 请联系管理员处理退款！
==================""")
            return False
            
    elif selected_pay == 'points' and vip_coin and vip_coin > 0:
        if int(usercoin) < zfcoin:
            sender.reply(f"""
=====积分不足=====
💫 当前积分: {usercoin}
🎯 需要积分: {zfcoin}
==================""")
            return False
            
        confirm_msg = f"""
=====积分支付确认=====
💰 消耗积分: {zfcoin}
📊 账号数量: {len(accounts)}个
⏰ 授权时长: {months}月/每个账号
------------------
确认请回复【y】
取消请回复【n】
=================="""
        sender.reply(confirm_msg)
        
        confirm = sender.input(60000, 1, False)
        if confirm and confirm.lower() == 'y':
            try:
                new_balance = int(usercoin) - zfcoin
                middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                
                success_count = 0
                for account in accounts:
                    try:
                        account_vip = middleware.bucketGet('dd_ltyp_auth', account) or ''
                        account_data = middleware.bucketGet('dd_ltyp_token', account)
                        account_json = json.loads(account_data) if account_data else {}
                        token = account_json.get('token_online')
                        ecs_token = account_json.get('ecs_token')
                        
                        new_vip = empower(empowertime=account_vip, me_as_int=months)
                        middleware.bucketSet('dd_ltyp_auth', account, new_vip)
                        
                        ql_url, ql_token, var_name = init_qinglong()
                        if ql_url and ql_token and token:
                            add_to_qinglong(ql_url, ql_token, var_name, token, account, '', ecs_token, new_vip)
                        success_count += 1
                    except:
                        continue
                
                result_msg = f"""
=====支付成功=====
💫 扣除积分: {zfcoin}
💰 剩余积分: {new_balance}
📊 成功: {success_count}/{len(accounts)}个账号
⏰ 授权时长: {months}月/每个账号
=================="""
                sender.reply(result_msg)
                return True
            except Exception as e:
                sender.reply(f"❌ 积分处理失败: {str(e)}")
                return False
        else:
            sender.reply("✅ 已取消支付")
            return False
    else:
        sender.reply("❌ 请输入正确的选项")
        return False


def query_account():
    """查询账号信息"""
    if not uservalue:
        sender.reply("""
=====未绑定账号=====
❌ 未找到任何账号信息
💡 发送 联通登录 绑定账号
==================""")
        return

    accounts = eval(uservalue)
    today_time = str(datetime.now().date())

    # 显示账号列表
    account_list_msg = "=====选择查询账号=====\n"
    account_list_msg += "[0] 全部查询\n"
    
    for idx, phone in enumerate(accounts, 1):
        account_data = middleware.bucketGet('dd_ltyp_token', phone)
        account_vip = middleware.bucketGet('dd_ltyp_auth', phone)
        auth_status, _ = get_auth_status(account_vip, today_time)
        
        if account_data:
            account_info = json.loads(account_data)
            remark = account_info.get('remark', phone)
        else:
            remark = phone
        
        account_list_msg += f"[{idx}] {mask_phone(phone)}\n"
    
    account_list_msg += "------------------\n"
    account_list_msg += "回复序号选择账号\n"
    account_list_msg += "回复\"q\"退出\n"
    account_list_msg += "=================="
    sender.reply(account_list_msg)
    
    # 等待用户选择
    user_choice = sender.input(60000, 1, False)
    if not user_choice:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif user_choice.lower() == 'q':
        sender.reply("✅ 已取消查询")
        return
    
    # 验证输入
    try:
        choice_num = int(user_choice)
        if choice_num < 0 or choice_num > len(accounts):
            sender.reply("❌ 序号无效，请输入正确的序号")
            return
    except ValueError:
        sender.reply("❌ 请输入数字序号")
        return
    
    # 确定要查询的账号列表
    if choice_num == 0:
        # 查询全部账号
        query_phones = accounts
    else:
        # 查询指定账号
        query_phones = [accounts[choice_num - 1]]
    
    # 执行查询
    for phone in query_phones:
        account_data = middleware.bucketGet('dd_ltyp_token', phone)
        account_vip = middleware.bucketGet('dd_ltyp_auth', phone)
        auth_status, auth_time = get_auth_status(account_vip, today_time)
        
        if not account_data:
            continue

        account_info = json.loads(account_data)
        token_online = account_info.get('token_online')
        remark = account_info.get('remark', phone)

        if not token_online:
            sender.reply(f"""
=====账号信息=====
📱 手机号: {mask_phone(phone)}
👤 备注: {remark}
🔐 授权: {auth_status}
📅 到期: {auth_time}
❌ Token未获取
==================""")
            continue

        result, error = asyncio.run(query_cloud_records(token_online, phone))
        if error:
            sender.reply(f"""
=====账号信息=====
📱 手机号: {mask_phone(phone)}
👤 备注: {remark}
🔐 授权: {auth_status}
📅 到期: {auth_time}
❌ 查询失败: {error}
==================""")
            continue

        sender.reply(build_account_query_message(phone, remark, auth_status, auth_time, result))


def admin_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return
        
    auth_menu = """
=====联通授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
[3] 更新变量
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(auth_menu)
    xz = sender.listen(60000)
    
    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出授权管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '1':
        # 一键授权所有用户
        users = middleware.bucketAllKeys('dd_ltyp_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的联通账号")
            return
            
        sender.reply("""
=====请输入授权天数=====
------------------
回复数字设置天数
回复"q"退出操作
==================""")
        
        sjts = sender.listen(60000)
        if sjts == 'q' or sjts == 'Q':
            sender.reply("✅ 已取消授权")
            return
        elif sjts is None:
            sender.reply("⏰ 操作超时,已退出")
            return
        
        try:
            sjts = int(sjts)
        except:
            sender.reply("❌ 天数必须是数字!")
            return
            
        success_count = 0
        fail_count = 0
        today_time = str(datetime.now().date())
        
        for user in users:
            accountlist = middleware.bucketGet('dd_ltyp_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            accounts = eval(accountlist)
            for account in accounts:
                try:
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    account_vip = middleware.bucketGet('dd_ltyp_auth', account)
                    account_data = middleware.bucketGet('dd_ltyp_token', account)
                    account_json = json.loads(account_data) if account_data else {}
                    token = account_json.get('token_online')
                    ecs_token = account_json.get('ecs_token')
                    
                    if not token:
                        fail_count += 1
                        continue
                        
                    if account_vip and account_vip > dqsj:
                        sqsj = datetime.strptime(account_vip, "%Y-%m-%d")
                        new_sqsj = sqsj + timedelta(days=int(sjts))
                    else:
                        new_sqsj = datetime.now() + timedelta(days=int(sjts))
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    
                    # 更新授权时间
                    middleware.bucketSet('dd_ltyp_auth', account, new_sqsj)
                    
                    # 更新青龙变量
                    ql_url, ql_token, var_name = init_qinglong()
                    if ql_url and ql_token:
                        add_to_qinglong(ql_url, ql_token, var_name, token, account, '', ecs_token, new_sqsj)
                    success_count += 1
                except:
                    fail_count += 1
                    
        result_msg = f"""
=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
        sender.reply(result_msg)
            
    elif xz == '2':
        # 单独授权用户
        user_guide = """
======账号授权======
请输入需要授权的账号ID
(发送myuid可获取ID)
------------------
回复"q"退出操作
=================="""
        sender.reply(user_guide)
        
        myuid = sender.listen(60000)
        if myuid == 'q' or myuid == 'Q':
            sender.reply("✅ 已退出授权")
            return
        elif myuid is None:
            sender.reply("⏰ 操作超时,已退出")
            return
            
        accountlist = middleware.bucketGet('dd_ltyp_user', myuid)
        if not accountlist or accountlist == '' or accountlist == '{}':
            sender.reply(f"""
=====查询结果=====
❌ 未找到 {myuid} 的账号信息
==================""")
            return
            
        try:
            accounts = eval(accountlist)
            if isinstance(accounts, str):
                accounts = [accounts]
            elif not isinstance(accounts, (list, tuple)):
                sender.reply("""
=====数据错误=====
❌ 账号数据格式异常
==================""")
                return
                
            accounts = list(dict.fromkeys(accounts))
            
            account_list = """
=======账号列表=====
[0] 授权所有账号
------------------"""
            
            for i, account in enumerate(accounts, 1):
                account_vip = middleware.bucketGet('dd_ltyp_auth', account)
                vip_status = account_vip if account_vip else '未授权'
                account_list += f"\n[{i}] 账号: {mask_phone(account)}\n    授权至: {vip_status}\n------------------"
                
            account_list += "\n回复数字选择账号\n回复'q'退出\n=================="
            sender.reply(account_list)
            
            xz = sender.listen(60000)
            if xz == 'q' or xz == 'Q':
                sender.reply("✅ 已退出授权")
                return
            elif xz is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                xz = int(xz)
                if xz < 0 or (xz > len(accounts) and xz != 0):
                    sender.reply(f"""
=====输入错误=====
❌ 请输入 0-{len(accounts)} 之间的数字
==================""")
                    return
            except ValueError:
                sender.reply("""
=====输入错误=====
❌ 请输入正确的数字
==================""")
                return
                
            auth_guide = """
=====设置授权天数=====
请输入要授权的天数
------------------
回复数字设置天数
回复"q"退出操作
=================="""
            sender.reply(auth_guide)
            
            sjts = sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                sjts = int(sjts)
                if sjts <= 0:
                    sender.reply("❌ 授权天数必须大于0!")
                    return
                    
                success_count = 0
                fail_count = 0
                
                if xz == 0:
                    target_accounts = accounts
                else:
                    target_accounts = [accounts[xz-1]]
                    
                for account in target_accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        account_vip = middleware.bucketGet('dd_ltyp_auth', account)
                        account_data = middleware.bucketGet('dd_ltyp_token', account)
                        account_json = json.loads(account_data) if account_data else {}
                        token = account_json.get('token_online')
                        ecs_token = account_json.get('ecs_token')
                        
                        if not token:
                            fail_count += 1
                            continue
                            
                        if account_vip and account_vip > dqsj:
                            sqsj = datetime.strptime(account_vip, "%Y-%m-%d")
                            new_sqsj = sqsj + timedelta(days=sjts)
                        else:
                            new_sqsj = datetime.now() + timedelta(days=sjts)
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        middleware.bucketSet('dd_ltyp_auth', account, new_sqsj)
                        
                        ql_url, ql_token, var_name = init_qinglong()
                        if ql_url and ql_token:
                            add_to_qinglong(ql_url, ql_token, var_name, token, account, '', ecs_token, new_sqsj)
                        success_count += 1
                    except Exception as e:
                        fail_count += 1
                        print(f"授权账号 {account} 失败: {str(e)}")
                        
                result_msg = f"""
=====授权操作完成=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 授权: {sjts} 天
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return
                
        except Exception as e:
            sender.reply(f"❌ 处理账号数据时出错: {str(e)}")
            return
            
    elif xz == '3':
        # 更新变量 - 把已授权用户的变量更新到青龙
        sender.reply("""
=====更新变量=====
⏳ 正在扫描已授权账号...
请稍候...
==================""")
        
        users = middleware.bucketAllKeys('dd_ltyp_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的联通账号")
            return
            
        success_count = 0
        fail_count = 0
        authorized_count = 0
        today_time = str(datetime.now().date())
        
        for user in users:
            accountlist = middleware.bucketGet('dd_ltyp_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            try:
                accounts = eval(accountlist)
                if isinstance(accounts, str):
                    accounts = [accounts]
                elif not isinstance(accounts, (list, tuple)):
                    continue
                    
                accounts = list(dict.fromkeys(accounts))
                
                for account in accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        account_vip = middleware.bucketGet('dd_ltyp_auth', account)
                        account_data = middleware.bucketGet('dd_ltyp_token', account)
                        account_json = json.loads(account_data) if account_data else {}
                        token = account_json.get('token_online')
                        ecs_token = account_json.get('ecs_token')
                        
                        if account_vip and account_vip > dqsj and token:
                            authorized_count += 1
                            ql_url, ql_token, var_name = init_qinglong()
                            if ql_url and ql_token:
                                add_to_qinglong(ql_url, ql_token, var_name, token, account, '', ecs_token, account_vip)
                            success_count += 1
                        else:
                            continue
                    except Exception as e:
                        fail_count += 1
                        print(f"更新账号 {account} 变量失败: {str(e)}")
                        continue
            except Exception as e:
                print(f"处理用户 {user} 数据失败: {str(e)}")
                continue
                    
        result_msg = f"""
=====变量更新完成=====
🔍 扫描用户: {len(users)}个
✅ 已授权账号: {authorized_count}个
📤 更新成功: {success_count}个
❌ 更新失败: {fail_count}个
=================="""
        sender.reply(result_msg)
            
    else:
        sender.reply("❌ 输入的选项无效!")
        return


def backend_manage():
    """后台管理功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        return
        
    backend_menu = """=====联通后台管理=====
[1] 清理过期账号
[2] 同步青龙变量
------------------
回复数字选择功能
回复"q"退出
=================="""
    sender.reply(backend_menu)
    xz = sender.listen(60000)
    
    if xz == 'q' or xz == 'Q':
        sender.reply("✅ 已退出后台管理")
        return
    elif xz is None:
        sender.reply("⏰ 操作超时,已退出")
        return
    elif xz == '1':
        # 清理过期账号
        clean_expired_accounts()
    elif xz == '2':
        # 青龙同步
        sync_to_qinglong()
    else:
        sender.reply("❌ 输入错误,请重新选择")
        return


def clean_expired_accounts():
    """清理过期的联通账号"""
    users = middleware.bucketAllKeys('dd_ltyp_user')
    
    if not users:
        sender.reply("❌ 未找到任何绑定账号")
        return
        
    sender.reply(f"⏳ 共找到: {len(users)}个用户\n清理中请稍候...")
    
    cleaned_count = 0
    today_time = str(datetime.now().date())
    
    for user in users:
        try:
            accountlist = middleware.bucketGet('dd_ltyp_user', user)
            if not accountlist:
                continue
                
            accounts = eval(accountlist)
            valid_accounts = []
            
            for account in accounts:
                account_vip = middleware.bucketGet('dd_ltyp_auth', account)
                
                if not account_vip or account_vip <= today_time:
                    try:
                        ql_url, ql_token, var_name = init_qinglong()
                        if ql_url and ql_token:
                            delete_from_qinglong(ql_url, ql_token, var_name, account)
                    except:
                        pass
                        
                    middleware.bucketDel('dd_ltyp_token', account)
                    middleware.bucketDel('dd_ltyp_auth', account)
                    cleaned_count += 1
                else:
                    valid_accounts.append(account)
            
            valid_accounts = list(dict.fromkeys(valid_accounts))
            
            if valid_accounts:
                middleware.bucketSet('dd_ltyp_user', user, str(valid_accounts))
            else:
                middleware.bucketDel('dd_ltyp_user', user)
                
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    
    sender.reply(f"""
=====清理完成=====
✅ 已清理: {cleaned_count}个过期账号
==================""")


def sync_to_qinglong():
    """同步已授权账号到青龙"""
    users = middleware.bucketAllKeys('dd_ltyp_user')
    
    if not users:
        sender.reply("❌ 未找到任何绑定账号")
        return
        
    sender.reply(f"⏳ 共找到: {len(users)}个用户\n同步中请稍候...")
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    today_time = str(datetime.now().date())
    
    for user in users:
        try:
            accountlist = middleware.bucketGet('dd_ltyp_user', user)
            if not accountlist:
                continue
                
            accounts = eval(accountlist)
            
            for account in accounts:
                try:
                    account_vip = middleware.bucketGet('dd_ltyp_auth', account)
                    
                    if not account_vip or account_vip <= today_time:
                        skip_count += 1
                        continue
                    
                    account_data = middleware.bucketGet('dd_ltyp_token', account)
                    account_json = json.loads(account_data) if account_data else {}
                    token = account_json.get('token_online')
                    ecs_token = account_json.get('ecs_token')
                    if not token:
                        fail_count += 1
                        continue
                    
                    ql_url, ql_token, var_name = init_qinglong()
                    if ql_url and ql_token:
                        add_to_qinglong(ql_url, ql_token, var_name, token, account, '', ecs_token, account_vip)
                    success_count += 1
                    
                except Exception as e:
                    print(f"同步账号 {account} 失败: {str(e)}")
                    fail_count += 1
                    continue
                    
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    
    result_msg = f"""=====同步完成=====
✅ 成功同步: {success_count}个账号
⏭️ 跳过未授权: {skip_count}个账号
❌ 同步失败: {fail_count}个账号
=================="""
    sender.reply(result_msg)


def show_tutorial():
    """显示联通插件使用教程"""
    tutorial = """📚 联通插件教程

🔰 基础功能指令:
1️⃣ 联通登录 - 绑定联通账号(Token登录)
2️⃣ 联通查询 - 查看账号中奖记录
3️⃣ 联通管理 - 管理已绑定账号([0]批量授权 [1-N]单个账号)

🔧 管理员功能:
• 联通授权 - 管理员授权用户
• 联通后台 - 清理过期账号/同步青龙

💡 授权说明:
• 选择[0]可批量授权所有账号
• 自动计算总金额和所需积分
• 支持微信、码支付、积分支付

⚠️ 注意事项:
1. 首次使用请先登录绑定
2. 定期查看账号状态
3. 及时处理授权到期
4. 登录格式: 备注#online_token"""
    sender.reply(tutorial)


def cron_check():
    """定时检测授权过期推送"""
    users = middleware.bucketAllKeys('dd_ltyp_user')
    if not users:
        return
    today = str(datetime.now().date())
    for user in users:
        try:
            accountlist = middleware.bucketGet('dd_ltyp_user', user)
            if not accountlist:
                continue
            accounts = eval(accountlist) if accountlist else []
            for account in accounts:
                try:
                    account_vip = middleware.bucketGet('dd_ltyp_auth', account) or ''
                    phone = account[:3] + '****' + account[7:] if len(account) >= 11 else account
                    if not account_vip or account_vip <= today:
                        push_msg = f"""
=====联通账号通知=====
📱 账号: {phone}
📢 消息: ⏰ 定时检测提醒\n------------------\n❌ 授权已过期\n💡 请及时续费授权
=================="""
                        for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                            try:
                                middleware.push(platform, '', user, '', push_msg)
                            except:
                                pass
                    else:
                        try:
                            expire_date = datetime.strptime(account_vip, '%Y-%m-%d').date()
                            days_left = (expire_date - datetime.now().date()).days
                            if days_left <= 3:
                                push_msg = f"""
=====联通账号通知=====
📱 账号: {phone}
📢 消息: ⏰ 定时检测提醒\n------------------\n⚠️ 授权即将到期\n📅 到期时间: {account_vip}\n⏳ 剩余天数: {days_left}天\n💡 请及时续费授权
=================="""
                                for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                                    try:
                                        middleware.push(platform, '', user, '', push_msg)
                                    except:
                                        pass
                        except:
                            pass
                except:
                    continue
        except:
            continue


def main():
    """主函数"""
    message = sender.getMessage()
    imtype = sender.getImtype()

    if imtype == 'fake':
        cron_check()
    elif '联通登录' in message or '联通登陆' in message:
        bind_account()
    elif '联通管理' in message:
        manage_account()
    elif '联通查询' in message:
        query_account()
    elif message == '联通授权':
        admin_auth()
    elif message == '联通后台':
        backend_manage()
    elif message == '联通教程':
        show_tutorial()
    else:
        sender.setContinue()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sender.reply(f"❌ 运行出错: {str(e)}")
