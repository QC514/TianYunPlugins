# [title: 爱坤助手]
# [language: python]
# [class: 工具类]
# [service: 203066880] 售后联系
# [author: rujingxianghai]
# [rule: ^(爱坤|ik)(登录|登陆)$|^登(录|陆)(爱坤|ik)$|^(爱坤|ik)(查询|管理|授权|检测|教程)$]
# [cron: 0 8 * * *]
# [priority: 0]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [open_source: false]
# [icon: ]
# [version: 3.0.1]
# [public: true]
# [price: 88.88]
# [description: 爱坤/ik登录、爱坤/ik管理、爱坤/ik查询。<br>支持多账号管理，授权后自动上传变量到青龙执行签到。]

# [param: {"required":true,"key":"s_ikuu.qlname","bool":false,"placeholder":"Host丨ClientID丨ClientSecret","name":"设置对接容器","desc":"青龙容器参数用丨分割"}]
# [param: {"required":true,"key":"s_ikuu.osname","bool":false,"placeholder":"例:S_IKUU","name":"青龙变量名","desc":"青龙容器内的变量名"}]
# [param: {"required":true,"key":"s_ikuu.zsm","bool":false,"placeholder":"http://xxx.jpg","name":"收款码链接","desc":"收款码链接"}]
# [param: {"required":true,"key":"s_ikuu.Vipmoney","bool":false,"placeholder":"例:0.88","name":"上车价格","desc":"授权价格(元)/月"}]
# [param: {"required":false,"key":"s_ikuu.coin","bool":false,"placeholder":"不填为关闭","name":"积分开通","desc":"授权一月需要多少积分"}]
# [param: {"required":false,"key":"s_ikuu.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_ikuu.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]
# [param: {"required":true,"key":"s_ikuu.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付"}]
# [param: {"required":false,"key":"s_ikuu.proxy_api","bool":false,"placeholder":"http://xxx.com/api/proxy","name":"代理API地址","desc":"代理API返回txt格式ip:port，未配置则直连"}]

import os
import json
import time
import hashlib
import random
import base64
import requests
import parsel
from datetime import datetime, timedelta
import middleware

# 初始化
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='s_ikuu_user', key=userid)

PLUGIN_CONFIG = {'bucket': 's_ikuu', 'coin_key': 'dd_sign_points', 'name': '爱坤'}
PAY_TYPE_NAMES = {'alipay': '支付宝', 'wxpay': '微信支付', 'qqpay': 'QQ钱包'}
BASE_URL = "https://ikuuu.de"

# 代理缓存
_proxy_cache = {'proxy': None, 'time': 0}


def get_proxy():
    """
    获取代理IP
    从配置的API获取代理，返回格式 {'http': 'http://ip:port', 'https': 'http://ip:port'}
    未配置或获取失败返回 None（使用直连）
    """
    proxy_api = middleware.bucketGet('s_ikuu', 'proxy_api')
    if not proxy_api:
        return None
    
    # 检查缓存（缓存30秒）
    current_time = time.time()
    if _proxy_cache['proxy'] and (current_time - _proxy_cache['time']) < 30:
        return _proxy_cache['proxy']
    
    try:
        resp = requests.get(proxy_api, timeout=10)
        resp.raise_for_status()
        proxy_text = resp.text.strip()
        
        if not proxy_text or ':' not in proxy_text:
            return None
        
        # 取第一行（如果返回多个代理）
        proxy_ip = proxy_text.split('\n')[0].strip()
        if not proxy_ip or ':' not in proxy_ip:
            return None
        
        proxy_dict = {
            'http': f'http://{proxy_ip}',
            'https': f'http://{proxy_ip}'
        }
        
        # 更新缓存
        _proxy_cache['proxy'] = proxy_dict
        _proxy_cache['time'] = current_time
        
        return proxy_dict
    except Exception:
        return None


def get_user_content():
    """获取用户配置"""
    osname = middleware.bucketGet('s_ikuu', 'osname') or 'S_IKUU'
    qlname = middleware.bucketGet('s_ikuu', 'qlname') or ''
    Vipmoney = float(middleware.bucketGet('s_ikuu', 'Vipmoney') or '1')
    coin = int(middleware.bucketGet('s_ikuu', 'coin') or '0')
    return osname, qlname, Vipmoney, coin


def mask_account(account):
    """账号脱敏处理"""
    if not account or len(account) < 4:
        return account
    # 邮箱
    if '@' in account:
        local, domain = account.split('@', 1)
        if len(local) <= 4:
            return f"{local[:1]}***@{domain}"
        return f"{local[:3]}****{local[-2:]}@{domain}"
    # 手机号
    if account.isdigit() and len(account) == 11:
        return f"{account[:3]}****{account[7:]}"
    # 其他类型
    if len(account) <= 16:
        return f"{account[:4]}****{account[-4:]}"
    return f"{account[:8]}****{account[-8:]}"


def get_ikuuu_session(email, password):
    """
    核心登录逻辑
    支持代理：配置了代理API时使用代理，否则直连
    """
    session = requests.Session()
    login_url = f'{BASE_URL}/auth/login'
    
    # 获取代理配置
    proxies = get_proxy()
    
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Origin': BASE_URL,
        'Referer': f'{BASE_URL}/auth/login',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest'
    })

    payload = {
        'host': 'ikuuu.de',
        'email': email,
        'passwd': password,
        'code': '',
        'pageLoadedAt': str(int(datetime.now().timestamp() * 1000))
    }

    try:
        response = session.post(login_url, data=payload, timeout=15, proxies=proxies)
        result = response.json()
        if result.get('ret') == 1:
            # 将代理配置保存到session供后续请求使用
            session.proxies = proxies or {}
            return session, "登录成功"
        else:
            return None, result.get('msg', '登录失败')
    except Exception as e:
        return None, f"网络请求异常: {str(e)}"


def query_flow(session):
    """
    流量查询逻辑
    """
    user_url = f'{BASE_URL}/user'
    try:
        response = session.get(user_url, timeout=15)
        response.encoding = 'utf-8'
        html_text = response.text

        # 检查响应是否被 base64 编码（服务器返回的 originBody 变量）
        import re
        base64_match = re.search(r'var\s+originBody\s*=\s*"([^"]+)"', html_text)
        if base64_match:
            # 提取并解码 base64 内容
            encoded_body = base64_match.group(1)
            try:
                html_text = base64.b64decode(encoded_body).decode('utf-8')
            except Exception:
                pass  # 解码失败则使用原始响应

        selector = parsel.Selector(html_text)

        target_card = selector.xpath('//div[@class="card-wrap"][.//h4[contains(text(), "剩余流量")]]')

        if target_card:
            full_text = target_card.xpath('.//div[@class="card-body"]').xpath('string(.)').get()
            if full_text:
                return full_text.strip().replace("\n", "")

        return "未能解析流量信息"
    except Exception as e:
        return f"查询异常: {str(e)}"


def get_ql_token(host, client_id, client_secret):
    """获取青龙token"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        resp = requests.get(url, timeout=10).json()
        if resp.get('code') == 200:
            return resp['data']['token']
        return None
    except:
        return None


def update_ql_env(account, account_info):
    """更新青龙环境变量"""
    env_value = account_info.get('token', '')
    if not env_value:
        return False
    
    qlconfig = middleware.bucketGet('s_ikuu', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        osname = middleware.bucketGet('s_ikuu', 'osname') or 'S_IKUU'
        auth_time = middleware.bucketGet('s_ikuu_auth', account) or '未授权'
        
        # 查找现有环境变量
        envs = requests.get(
            f'{host}/open/envs?searchValue={account[:10]}',
            headers=headers, timeout=10
        ).json().get('data', [])
        env_id = next((e.get('id') for e in envs if e['name'] == osname and account in e.get('value', '')), None)
        
        env_data = {
            'name': osname,
            'value': env_value,
            'remarks': f"爱坤：{mask_account(account)}|到期:{auth_time}"
        }
        
        if env_id:
            env_data['id'] = env_id
            requests.put(f'{host}/open/envs', headers=headers, json=env_data, timeout=10)
            requests.put(f'{host}/open/envs/enable', headers=headers, json=[env_id], timeout=10)
        else:
            resp = requests.post(f'{host}/open/envs', headers=headers, json=[env_data], timeout=10).json()
            if resp.get('data'):
                new_id = resp['data'][0].get('_id') or resp['data'][0].get('id')
                if new_id:
                    requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id], timeout=10)
        return True
    except:
        return False


def delete_ql_env(account):
    """删除青龙环境变量"""
    qlconfig = middleware.bucketGet('s_ikuu', 'qlname')
    if not qlconfig:
        return False
    
    configs = qlconfig.replace('|', '丨').split('丨')
    if len(configs) < 3:
        return False
    
    host, client_id, client_secret = [x.strip() for x in configs]
    
    try:
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False
        
        headers = {'Authorization': f'Bearer {token}'}
        osname = middleware.bucketGet('s_ikuu', 'osname') or 'S_IKUU'
        envs = requests.get(f'{host}/open/envs', headers=headers, timeout=10).json().get('data', [])
        
        for env in envs:
            if env['name'] == osname and account in env.get('value', ''):
                env_id = env.get('_id') or env.get('id')
                requests.delete(f'{host}/open/envs', headers=headers, json=[env_id], timeout=10)
                return True
        return False
    except:
        return False


def generate_qrcode(url):
    """生成二维码图片"""
    QRCODE_API_URL = "https://qrcode.vorto.cn/api/qrcode/generate"
    QRCODE_API_KEY = "4jpC3Cgd0zA7Z3HTJ6aDfW9QjtzitDGI"
    
    try:
        response = requests.post(
            QRCODE_API_URL,
            json={"content": url},
            headers={"X-API-Key": QRCODE_API_KEY},
            timeout=10
        )
        if response.status_code == 200:
            result = response.json()
            if result.get('success') and result.get('data', {}).get('url'):
                return result['data']['url']
    except:
        pass
    
    try:
        encoded_url = requests.utils.quote(url)
        return f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
    except:
        return None


def bind_account():
    """绑定账号"""
    sender.reply(
        "=====爱坤登录=====\n"
        "请输入账号信息\n"
        "格式: 邮箱#密码\n"
        "------------------\n"
        "支持批量登录(换行分隔)\n"
        "回复\"q\"退出\n"
        "=================="
    )
    input_text = sender.input(120000, 1, False)
    if not input_text:
        sender.reply("⏰ 操作超时")
        return
    if input_text.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    success_count = 0
    fail_count = 0
    results = []
    
    for line in lines:
        if '#' not in line:
            results.append(f"❌ 格式错误: {line[:20]}...")
            fail_count += 1
            continue
        
        parts = line.split('#', 1)
        if len(parts) != 2:
            results.append(f"❌ 格式错误: {line[:20]}...")
            fail_count += 1
            continue
        
        email, password = parts[0].strip(), parts[1].strip()
        
        # 验证登录
        session, msg = get_ikuuu_session(email, password)
        if not session:
            results.append(f"❌ {mask_account(email)}: {msg}")
            fail_count += 1
            continue
        
        # 保存账号
        accounts = eval(uservalue) if uservalue else []
        if email not in accounts:
            accounts.append(email)
            middleware.bucketSet('s_ikuu_user', userid, str(accounts))
        
        # 存储token信息（邮箱#密码格式，供青龙脚本使用）
        token_info = {
            'email': email,
            'password': password,
            'token': f"{email}#{password}"  # 青龙变量格式
        }
        middleware.bucketSet('s_ikuu_token', email, json.dumps(token_info))
        
        results.append(f"✅ {mask_account(email)}: 登录成功")
        success_count += 1
    
    result_text = "\n".join(results[:10])
    if len(results) > 10:
        result_text += f"\n... 共 {len(results)} 条"
    
    sender.reply(
        f"=====登录完成=====\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"------------------\n"
        f"{result_text}\n"
        f"=================="
    )


def query_accounts():
    """查询账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n💡 发送 爱坤登录 绑定\n==================")
        return
    
    accounts = eval(uservalue)
    account_list = "\n========选择账号======\n[0] 全部账号"
    for i, account in enumerate(accounts, 1):
        auth_time = middleware.bucketGet('s_ikuu_auth', account)
        if not auth_time:
            auth_status = '未授权'
        elif auth_time < str(datetime.now().date()):
            auth_status = '已过期'
        else:
            auth_status = f'到期:{auth_time}'
        account_list += f"\n[{i}]{mask_account(account)}({auth_status})"
    account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
    sender.reply(account_list)
    
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    # 解析选择
    selected = []
    if choice == '0':
        selected = accounts
    else:
        try:
            indices = [int(x.strip()) for x in choice.split(',')]
            for idx in indices:
                if 1 <= idx <= len(accounts):
                    selected.append(accounts[idx - 1])
        except:
            sender.reply("❌ 输入无效")
            return
    
    if not selected:
        sender.reply("❌ 未选择有效账号")
        return
    
    sender.reply("🔍 正在查询...")
    results = []
    for account in selected:
        try:
            token_data = json.loads(middleware.bucketGet('s_ikuu_token', account) or '{}')
            email = token_data.get('email', account)
            password = token_data.get('password', '')
            
            if not password:
                results.append(f"❌ {mask_account(account)}: 缺少密码信息")
                continue
            
            session, msg = get_ikuuu_session(email, password)
            if session:
                flow = query_flow(session)
                auth_time = middleware.bucketGet('s_ikuu_auth', account) or '未授权'
                results.append(f"📱 {mask_account(account)}\n   💾 流量: {flow}\n   📅 授权: {auth_time}")
            else:
                results.append(f"❌ {mask_account(account)}: 登录失败-{msg}")
        except Exception as e:
            results.append(f"❌ {mask_account(account)}: 异常-{str(e)}")
    
    sender.reply(
        "=====查询结果=====\n" +
        "\n------------------\n".join(results) +
        "\n=================="
    )


def process_authorization(account, account_info, months):
    """处理授权"""
    try:
        dqsj = datetime.now().strftime("%Y-%m-%d")
        accountVip = middleware.bucketGet('s_ikuu_auth', account)
        if accountVip and accountVip > dqsj:
            start_date = datetime.strptime(accountVip, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        new_expire = (start_date + timedelta(days=30 * months)).strftime("%Y-%m-%d")
        middleware.bucketSet('s_ikuu_auth', account, new_expire)
        
        # 同步青龙
        update_ql_env(account, account_info)
        
        sender.reply(
            f"=====授权成功=====\n"
            f"📱 账号: {mask_account(account)}\n"
            f"📅 到期: {new_expire}\n"
            f"=================="
        )
        return True
    except Exception as e:
        sender.reply(f"授权异常: {str(e)}")
        return False


def pay_order(project, months, money):
    """收款码支付"""
    if float(money) == 0:
        return True
    
    zsm = middleware.bucketGet('s_ikuu', 'zsm')
    if not zsm:
        sender.reply('❌ 未配置收款码')
        return False
    
    sender.reply(
        f"=====微信扫码支付====\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {money}元\n"
        f"=================="
    )
    sender.replyImage(zsm)
    
    ddzf = sender.waitPay("q", 100000)
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


def process_coin_payment(account, account_info, months, coin):
    """积分支付"""
    try:
        required = months * coin
        user_coins = int(middleware.bucketGet('dd_sign_points', userid) or '0')
        
        if user_coins < required:
            sender.reply(
                f"=====积分不足=====\n"
                f"❌ 当前: {user_coins}\n"
                f"💰 需要: {required}\n"
                f"=================="
            )
            return False
        
        middleware.bucketSet('dd_sign_points', userid, str(user_coins - required))
        if process_authorization(account, account_info, months):
            sender.reply(
                f"=====积分兑换成功=====\n"
                f"✅ 扣除: {required}\n"
                f"💰 剩余: {user_coins - required}\n"
                f"=================="
            )
            return True
        
        # 授权失败则退还积分
        middleware.bucketSet('dd_sign_points', userid, str(user_coins))
        return False
    except Exception as e:
        sender.reply(f"积分兑换异常: {str(e)}")
        return False


def handle_mapay_order(project, months, money, pay_type=None):
    """码支付订单"""
    config = {
        'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway') or '',
        'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid') or '',
        'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key') or '',
        'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url') or '',
        'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url') or ''
    }
    
    if not (config['gateway'] and config['pid'] and config['key']):
        sender.reply('❌ 码支付配置不完整')
        return False
    
    amount = round(float(money), 2)
    out_trade_no = f"IKUU{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
    selected_type = pay_type or 'alipay'
    
    params = {
        'pid': config['pid'],
        'type': selected_type,
        'out_trade_no': out_trade_no,
        'notify_url': config['notify_url'],
        'return_url': config['return_url'],
        'name': f"{project}-{amount}",
        'money': str(amount),
        'param': userid
    }
    params = {k: v for k, v in params.items() if v}
    sign_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    params['sign'] = hashlib.md5((sign_str + config['key']).encode()).hexdigest().lower()
    params['sign_type'] = 'MD5'
    
    try:
        resp = requests.post(f"{config['gateway'].rstrip('/')}/mapi.php", data=params, timeout=10).json()
        if resp.get('code') != 1:
            sender.reply(f'❌ 创建订单失败: {resp.get("msg")}')
            return False
        
        trade_no = resp.get('trade_no')
        pay_url = f"{config['gateway'].rstrip('/')}/pay/{trade_no}"
        sender.reply(f'请使用【{PAY_TYPE_NAMES.get(selected_type, selected_type)}】扫描二维码完成支付:')
        sender.replyImage(generate_qrcode(pay_url))
        sender.reply('输入"q"可取消')
        
        for _ in range(30):
            qresp = requests.get(
                f"{config['gateway'].rstrip('/')}/xpay/epay/api.php",
                params={'act': 'order', 'pid': config['pid'], 'key': config['key'], 'out_trade_no': out_trade_no},
                timeout=10
            ).json()
            if qresp.get('code') == 1 and qresp.get('status') == 1:
                return True
            if sender.listen(5000) == 'q':
                sender.reply("✅ 已取消")
                return False
        
        sender.reply("❌ 支付超时")
        return False
    except Exception as e:
        sender.reply(f'❌ 支付异常: {str(e)}')
        return False


def authorize_multiple_accounts(accounts):
    """批量授权账号"""
    account_infos = []
    for account in accounts:
        try:
            account_infos.append({
                'account': account,
                'info': json.loads(middleware.bucketGet('s_ikuu_token', account))
            })
        except:
            pass
    
    if not account_infos:
        sender.reply("❌ 没有有效账号")
        return
    
    sender.reply(
        f"✅ {len(account_infos)} 个有效账号\n"
        f"=====设置授权时长=====\n"
        f"请输入授权月数(如:1)\n"
        f"回复\"q\"退出\n"
        f"=================="
    )
    months = sender.input(120000, 1, False)
    if not months or months.lower() == 'q':
        sender.reply("✅ 已取消")
        return
    
    try:
        months = int(months)
        if months <= 0:
            sender.reply("❌ 月数必须大于0")
            return
        
        Vipmoney = float(middleware.bucketGet('s_ikuu', 'Vipmoney') or '1')
        total_money = len(account_infos) * months * Vipmoney
        coin = int(middleware.bucketGet('s_ikuu', 'coin') or '0')
        
        # 构建可用支付方式
        available = []
        ma_pay_switch = middleware.bucketGet('s_ikuu', 'ma_pay_switch') or 'false'
        if ma_pay_switch.lower() == 'true' and middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'):
            for pt in (middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay').split(','):
                available.append((PAY_TYPE_NAMES.get(pt.strip(), pt.strip()), f"mapay_{pt.strip()}"))
        elif middleware.bucketGet('s_ikuu', 'zsm'):
            available.append(("微信支付", "wxpay"))
        
        if coin > 0:
            available.append(("积分兑换", "coin"))
        
        if not available:
            sender.reply("❌ 未配置支付方式")
            return
        
        pay_menu = "=====选择支付方式=====\n"
        for i, (name, _) in enumerate(available, 1):
            if name == "积分兑换":
                pay_menu += f"[{i}] {name} ({months * coin * len(account_infos)}积分)\n"
            else:
                pay_menu += f"[{i}] {name}\n"
        pay_menu += f"------------------\n💰 总金额: {total_money}元\n回复\"q\"退出\n=================="
        sender.reply(pay_menu)
        
        pay_choice = sender.input(120000, 1, False)
        if not pay_choice or pay_choice.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        try:
            pay_idx = int(pay_choice) - 1
            if pay_idx < 0 or pay_idx >= len(available):
                sender.reply("❌ 无效选择")
                return
            
            pay_name, pay_type = available[pay_idx]
            
            # 处理支付
            if pay_type == "coin":
                for acc_info in account_infos:
                    process_coin_payment(acc_info['account'], acc_info['info'], months, coin)
            elif pay_type == "wxpay":
                if pay_order(f"爱坤授权x{len(account_infos)}", months, total_money):
                    for acc_info in account_infos:
                        process_authorization(acc_info['account'], acc_info['info'], months)
            elif pay_type.startswith("mapay_"):
                real_type = pay_type.replace("mapay_", "")
                if handle_mapay_order(f"爱坤授权x{len(account_infos)}", months, total_money, real_type):
                    for acc_info in account_infos:
                        process_authorization(acc_info['account'], acc_info['info'], months)
        except ValueError:
            sender.reply("❌ 请输入有效数字")
    except ValueError:
        sender.reply("❌ 请输入有效数字")


def submit_to_ql(accounts):
    """提交变量到青龙"""
    osname, qlname, _, _ = get_user_content()
    if not qlname:
        sender.reply("❌ 未配置青龙容器")
        return
    
    success_count = 0
    fail_count = 0
    
    for account in accounts:
        try:
            token_data = json.loads(middleware.bucketGet('s_ikuu_token', account) or '{}')
            if token_data:
                if update_ql_env(account, token_data):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1
        except:
            fail_count += 1
    
    sender.reply(
        f"=====提交青龙=====\n"
        f"✅ 成功: {success_count}个\n"
        f"❌ 失败: {fail_count}个\n"
        f"=================="
    )


def manage_account():
    """管理账号"""
    if not uservalue:
        sender.reply("=====未绑定账号=====\n❌ 未找到账号\n==================")
        return
    
    accounts = eval(uservalue)
    sender.reply(
        "=====账号管理=====\n"
        "[1] 授权账号\n"
        "[2] 删除账号\n"
        "[3] 提交青龙\n"
        "------------------\n"
        "回复数字选择\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    if choice == '1':
        # 授权账号
        account_list = "\n========选择账号======\n[0] 全部账号"
        for i, account in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_ikuu_auth', account)
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            account_list += f"\n[{i}]{mask_account(account)}({auth_status})"
        account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
        sender.reply(account_list)
        
        sel = sender.input(120000, 1, False)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已退出")
            return
        
        selected = []
        if sel == '0':
            selected = accounts
        else:
            try:
                indices = [int(x.strip()) for x in sel.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(accounts):
                        selected.append(accounts[idx - 1])
            except:
                sender.reply("❌ 输入无效")
                return
        
        if selected:
            authorize_multiple_accounts(selected)
    
    elif choice == '2':
        # 删除账号
        account_list = "\n========选择删除======\n[0] 全部删除"
        for i, account in enumerate(accounts, 1):
            account_list += f"\n[{i}]{mask_account(account)}"
        account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
        sender.reply(account_list)
        
        sel = sender.input(120000, 1, False)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已退出")
            return
        
        to_delete = []
        if sel == '0':
            to_delete = accounts[:]
        else:
            try:
                indices = [int(x.strip()) for x in sel.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(accounts):
                        to_delete.append(accounts[idx - 1])
            except:
                sender.reply("❌ 输入无效")
                return
        
        for account in to_delete:
            delete_ql_env(account)
            middleware.bucketDel('s_ikuu_token', account)
            middleware.bucketDel('s_ikuu_auth', account)
            if account in accounts:
                accounts.remove(account)
        
        if accounts:
            middleware.bucketSet('s_ikuu_user', userid, str(accounts))
        else:
            middleware.bucketDel('s_ikuu_user', userid)
        
        sender.reply(f"✅ 已删除 {len(to_delete)} 个账号")
    
    elif choice == '3':
        # 提交青龙
        account_list = "\n========选择账号======\n[0] 全部账号"
        for i, account in enumerate(accounts, 1):
            auth_time = middleware.bucketGet('s_ikuu_auth', account)
            if not auth_time:
                auth_status = '未授权'
            elif auth_time < str(datetime.now().date()):
                auth_status = '已过期'
            else:
                auth_status = f'到期:{auth_time}'
            account_list += f"\n[{i}]{mask_account(account)}({auth_status})"
        account_list += "\n=====================\n支持多选，用逗号分隔\n回复\"q\"退出\n====================="
        sender.reply(account_list)
        
        sel = sender.input(120000, 1, False)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已退出")
            return
        
        selected = []
        if sel == '0':
            selected = accounts
        else:
            try:
                indices = [int(x.strip()) for x in sel.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(accounts):
                        selected.append(accounts[idx - 1])
            except:
                sender.reply("❌ 输入无效")
                return
        
        if selected:
            # 检查是否已授权
            unauthorized = []
            authorized = []
            for acc in selected:
                auth_time = middleware.bucketGet('s_ikuu_auth', acc)
                if auth_time and auth_time >= str(datetime.now().date()):
                    authorized.append(acc)
                else:
                    unauthorized.append(acc)
            
            if unauthorized:
                sender.reply(f"⚠️ 以下账号未授权或已过期，无法提交:\n" + 
                           "\n".join([f"  - {mask_account(a)}" for a in unauthorized]))
            
            if authorized:
                submit_to_ql(authorized)


def check_auth_status():
    """检测授权状态"""
    notify = middleware.bucketGet('s_ikuu', 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"
    
    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys('s_ikuu_user')
    if not all_users:
        return "❌ 没有用户"
    
    notify_days = int(middleware.bucketGet('s_ikuu', 'notify_days') or '3')
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0
    
    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet('s_ikuu_user', user_id) or '[]')
            to_notify = []
            to_clean = []
            
            for acc in accounts:
                auth_time_str = middleware.bucketGet('s_ikuu_auth', acc)
                
                if not auth_time_str:
                    to_clean.append({'account': acc, 'auth_time': '未授权', 'days_left': 0})
                    continue
                
                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days
                    
                    if days_left <= 0:
                        to_clean.append({'account': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        to_notify.append({'account': acc, 'auth_time': auth_time_str, 'days_left': days_left})
                except:
                    to_clean.append({'account': acc, 'auth_time': auth_time_str, 'days_left': 0})
            
            total += len(accounts)
            
            # 处理需要清理的账号
            if to_clean:
                for exp_acc in to_clean:
                    account = exp_acc['account']
                    delete_ql_env(account)
                    middleware.bucketDel('s_ikuu_token', account)
                    if account in accounts:
                        accounts.remove(account)
                    middleware.bucketDel('s_ikuu_auth', account)
                    cleaned += 1
                
                if accounts:
                    middleware.bucketSet('s_ikuu_user', user_id, str(accounts))
                else:
                    middleware.bucketDel('s_ikuu_user', user_id)
            
            # 处理需要提醒的账号
            if to_notify:
                notify_list = "\n".join([
                    f"📱 {mask_account(a['account'])} 剩余{a['days_left']}天({a['auth_time']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====爱坤账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"爱坤管理\"续费\n"
                    f"=================="
                )
                for ch in channels:
                    try:
                        middleware.push(imType=ch, groupCode='', userID=user_id, title="", content=msg)
                        notified += 1
                    except:
                        pass
        except:
            pass
    
    return f"✅ 检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"


def ks_auth():
    """管理员授权"""
    if not sender.isAdmin():
        sender.reply("❌ 仅限管理员")
        return
    
    sender.reply(
        "=====管理员授权=====\n"
        "[1] 批量授权所有用户\n"
        "[2] 单独授权指定用户\n"
        "回复\"q\"退出\n"
        "=================="
    )
    choice = sender.input(120000, 1, False)
    if not choice or choice.lower() == 'q':
        sender.reply("✅ 已退出")
        return
    
    if choice == '1':
        all_users = [
            {'id': k, 'accounts': eval(middleware.bucketGet('s_ikuu_user', k) or '[]')}
            for k in middleware.bucketAllKeys('s_ikuu_user')
        ]
        if not all_users:
            sender.reply("❌ 无用户")
            return
        
        total_accs = sum(len(u['accounts']) for u in all_users)
        sender.reply(
            f"=====批量授权=====\n"
            f"👥 用户数: {len(all_users)}\n"
            f"📊 账号数: {total_accs}\n"
            f"请输入授权天数(正数增加/负数减少):\n"
            f"=================="
        )
        
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        try:
            days = int(days_input)
            success = 0
            for user in all_users:
                for account in user['accounts']:
                    try:
                        auth_time_str = middleware.bucketGet('s_ikuu_auth', account)
                        if auth_time_str:
                            auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d")
                        else:
                            auth_date = datetime.now()
                        
                        new_date = (auth_date + timedelta(days=days)).strftime("%Y-%m-%d")
                        middleware.bucketSet('s_ikuu_auth', account, new_date)
                        
                        # 同步青龙
                        token_data = json.loads(middleware.bucketGet('s_ikuu_token', account) or '{}')
                        if token_data:
                            update_ql_env(account, token_data)
                        
                        success += 1
                    except:
                        pass
            
            sender.reply(f"✅ 授权完成，成功 {success}/{total_accs} 个账号")
        except ValueError:
            sender.reply("❌ 无效的天数")
    
    elif choice == '2':
        sender.reply("请输入用户ID:")
        user_id_input = sender.input(120000, 1, False)
        if not user_id_input or user_id_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        user_accounts = middleware.bucketGet('s_ikuu_user', user_id_input)
        if not user_accounts:
            sender.reply("❌ 该用户无账号")
            return
        
        accounts = eval(user_accounts)
        account_list = "\n".join([f"[{i}] {mask_account(acc)}" for i, acc in enumerate(accounts, 1)])
        sender.reply(
            f"=====用户账号=====\n"
            f"[0] 全部账号\n"
            f"{account_list}\n"
            f"=================="
        )
        
        sel = sender.input(120000, 1, False)
        if not sel or sel.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        selected = []
        if sel == '0':
            selected = accounts
        else:
            try:
                indices = [int(x.strip()) for x in sel.split(',')]
                for idx in indices:
                    if 1 <= idx <= len(accounts):
                        selected.append(accounts[idx - 1])
            except:
                sender.reply("❌ 输入无效")
                return
        
        if not selected:
            sender.reply("❌ 未选择账号")
            return
        
        sender.reply("请输入授权天数(正数增加/负数减少):")
        days_input = sender.input(120000, 1, False)
        if not days_input or days_input.lower() == 'q':
            sender.reply("✅ 已取消")
            return
        
        try:
            days = int(days_input)
            success = 0
            for account in selected:
                try:
                    auth_time_str = middleware.bucketGet('s_ikuu_auth', account)
                    if auth_time_str:
                        auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d")
                    else:
                        auth_date = datetime.now()
                    
                    new_date = (auth_date + timedelta(days=days)).strftime("%Y-%m-%d")
                    middleware.bucketSet('s_ikuu_auth', account, new_date)
                    
                    token_data = json.loads(middleware.bucketGet('s_ikuu_token', account) or '{}')
                    if token_data:
                        update_ql_env(account, token_data)
                    
                    success += 1
                except:
                    pass
            
            sender.reply(f"✅ 授权完成，成功 {success}/{len(selected)} 个账号")
        except ValueError:
            sender.reply("❌ 无效的天数")


def show_tutorial():
    """显示教程"""
    sender.reply(
        "=====爱坤使用教程=====\n"
        "📝 指令说明：\n"
        "• 爱坤登录 - 添加账号\n"
        "• 爱坤查询 - 查询流量\n"
        "• 爱坤管理 - 管理账号\n"
        "------------------\n"
        "📋 登录格式：\n"
        "邮箱#密码\n"
        "支持多账号换行\n"
        "------------------\n"
        "💡 使用流程：\n"
        "1. 发送\"爱坤登录\"添加账号\n"
        "2. 发送\"爱坤管理\"授权账号\n"
        "3. 授权后提交到青龙执行签到\n"
        "=================="
    )


def main():
    """主入口"""
    msg = sender.getMessage()
    
    if '登录' in msg or '登陆' in msg:
        bind_account()
    elif '查询' in msg and ('爱坤' in msg or 'ik' in msg.lower()):
        query_accounts()
    elif '管理' in msg and ('爱坤' in msg or 'ik' in msg.lower()):
        manage_account()
    elif '教程' in msg and ('爱坤' in msg or 'ik' in msg.lower()):
        show_tutorial()
    elif '爱坤授权' in msg or 'ik授权' in msg.lower():
        ks_auth()
    elif '爱坤检测' in msg or 'ik检测' in msg.lower():
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    # 定时任务
    elif sender.getImtype() == 'fake':
        try:
            middleware.notifyMasters(check_auth_status())
        except:
            pass
    else:
        sender.setContinue()


if __name__ == "__main__":
    main()