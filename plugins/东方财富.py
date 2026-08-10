#[title: 东方财富]
#[language: python]
#[class: 工具类]
#[author: rujingxianghai]
#[service: 2993959969] 售后联系方式
#[disable: false] 禁用开关，true表示禁用，false表示可用
#[admin: false] 是否为管理员指令
#[rule: ^东方登录$|^登录东方$|^东方查询$|^东方管理$|^东方提现$|^东方授权$|^东方检测$|^东方教程$] 匹配规则，多个规则时向下依次写多个
#[cron: 10 7 * * *] cron定时，支持5位域和6位域
#[priority: 0] 优先级，数字越大表示优先级越高
#[platform: qq,qb,wx,tb,tg,web,wxmp] 适用的平台
#[open_source: false]是否开源
#[icon: https://img-cf.885666.xyz/5967b00a7a39fba673de40a4c9e89c78.jpg]图标链接地址，请使用48像素的正方形图标，支持http和https
#[version: 1.4]版本号
#[public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
#[price: 8.88] 上架价格
#[description: 刷视频领现金，1.5r/日，需实名<br>微信扫码登录 + 账号密码登录，需要手动登录app绑定账号，进入活动页面一次。脚本群内获取<br>1.0.7：更新自动识别验证码，使用ddddocr，推荐自行搭建接口。<br>接口项目：https://github.com/sml2h3/ddddocr-fastapi] 

# 插件参数配置
# [param: {"required":false,"key":"s_eastmoney.zsm","bool":false,"placeholder":"非必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"微信赞赏码/收款码链接"}]
# [param: {"required":false,"key":"s_eastmoney.price","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"授权价格(单位:元)/月"}]
# [param: {"required":false,"key":"s_eastmoney.coin","bool":false,"placeholder":"不填为关闭积分授权","name":"积分开通","desc":"授权一个月需要多少积分"}]
# [param: {"required":false,"key":"s_eastmoney.ql_config","bool":false,"placeholder":"格式:http://qinglong地址|ClientID|ClientSecret","name":"青龙配置","desc":"青龙面板配置信息，用|分隔"}]
# [param: {"required":false,"key":"s_eastmoney.ql_envname","bool":false,"placeholder":"例:S_DFCF","name":"青龙变量名","desc":"推送到青龙的变量名称"}]
# [param: {"required":false,"key":"s_eastmoney.captcha_api","bool":false,"placeholder":"https://api.example.com/ocr","name":"验证码识别API","desc":"填写验证码识别接口地址，不填使用作者接口（不保证可用性）"}]
# [param: {"required":false,"key":"s_eastmoney.ma_pay_switch","bool":true,"placeholder":"","name":"码支付功能","desc":"开启后使用码支付"}]
# [param: {"required":false,"key":"s_eastmoney.notify","bool":false,"placeholder":"qq,wx,tb","name":"通知渠道","desc":"检测通知推送渠道"}]
# [param: {"required":false,"key":"s_eastmoney.notify_days","bool":false,"placeholder":"3","name":"提前提醒天数","desc":"到期前多少天开始提醒"}]

import json
import requests
import re
import uuid
import time
import random
import string
import middleware
import base64
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
import urllib.parse
import os

# 数据桶名称配置
BUCKET_USER = 's_eastmoney_user'  # 用户账号列表
BUCKET_TOKEN = 's_eastmoney_token'  # 用户Token信息
BUCKET_AUTH = 's_eastmoney_auth'   # 授权信息
BUCKET_CONFIG = 's_eastmoney'      # 插件配置

# 码支付相关配置
PAY_TYPE_NAMES = {'alipay': '支付宝', 'wxpay': '微信支付', 'qqpay': 'QQ钱包'}
PLUGIN_NAME = '东方财富'

# 微信相关配置
APPID = "wxb062331269cec15f"  # 东方财富App的微信AppID
BUNDLEID = "com.eastmoney.android.berlin"  # 东方财富App的BundleID
DEFAULT_UA = "Mozilla/5.0 (Linux; Android 15; 2210132C Build/AQ3A.240812.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/130.0.6723.103 Mobile Safari/537.36 XWEB/1300473 MMWEBSDK/20250201 MMWEBID/9172 MicroMessenger/8.0.57.2820(0x28003939) WeChat/arm64 Weixin NetType/WIFI Language/zh_CN ABI/arm64"

# 获取发送者信息
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()

# 获取配置信息
def get_config():
    """获取插件配置"""
    price = Decimal(middleware.bucketGet(BUCKET_CONFIG, 'price') or '0')
    coin_price = middleware.bucketGet(BUCKET_CONFIG, 'coin') or ''
    zsm = middleware.bucketGet(BUCKET_CONFIG, 'zsm') or ''
    ql_config = middleware.bucketGet(BUCKET_CONFIG, 'ql_config') or ''
    ql_envname = middleware.bucketGet(BUCKET_CONFIG, 'ql_envname') or 'S_DFCF'
    captcha_api = middleware.bucketGet(BUCKET_CONFIG, 'captcha_api') or "http://42.194.132.65:30052/ocr"
    
    return price, coin_price, zsm, ql_config, ql_envname, captcha_api

# 授权相关函数
def calculate_auth_time(uid, months):
    """计算授权时间"""
    try:
        # 获取当前授权时间
        current_auth = middleware.bucketGet(BUCKET_AUTH, uid)
        
        # 设置基准时间
        if current_auth and datetime.strptime(current_auth, "%Y-%m-%d").date() > datetime.now().date():
            # 如果当前授权未过期，则从当前授权时间开始计算
            base_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
        else:
            # 否则从今天开始计算
            base_date = datetime.now().date()
            
        # 计算新的授权到期时间
        new_date = base_date + timedelta(days=30 * int(months))
        
        return str(new_date)
        
    except Exception as e:
        raise Exception(f"计算授权时间失败: {str(e)}")

def set_auth_success(uid, months, total_price):
    """设置授权成功并显示成功信息"""
    try:
        # 获取用户信息
        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
        if not token_info_str:
            sender.reply(f"❌ 未找到账号 {uid} 的Token信息")
            return False
            
        token_info = json.loads(token_info_str)
        alias = token_info.get("Alias", "未知用户")
        
        # 设置授权时间
        auth_time = calculate_auth_time(uid, months)
        middleware.bucketSet(BUCKET_AUTH, uid, auth_time)
        
        # 更新青龙变量
        _, _, _, ql_config, ql_envname, _ = get_config()
        ql_result = False
        
        if ql_config:
            ql_result, ql_message = add_to_qinglong(uid, token_info, ql_envname)
        
        # 显示成功信息
        success_msg = f"""
=====授权成功=====
👤 用户: {alias}
📱 UID: {uid}
💰 支付: {total_price}元
📅 有效期至: {auth_time}
------------------
🔄 青龙同步: {'成功' if ql_result else '失败'}
=================="""
        
        sender.reply(success_msg)
        return True
        
    except Exception as e:
        sender.reply(f"❌ 设置授权失败: {str(e)}")
        return False

def process_payment_zsm(uid):
    """处理扫码支付"""
    try:
        # 获取配置
        price, _, zsm, _, _, _ = get_config()
        
        if price is None:
            sender.reply("❌ 未设置价格，请联系管理员")
            return False
            
        # 获取用户信息
        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
        if not token_info_str:
            sender.reply(f"❌ 未找到账号 {uid} 的Token信息")
            return False
            
        token_info = json.loads(token_info_str)
        alias = token_info.get("Alias", "未知用户")
        
        sender.reply("""请输入授权月数:
回复"q"退出""")
        months = sender.listen(60000)
        
        if not months or months == 'q':
            sender.reply("✅ 已退出扫码支付流程")
            return False
            
        try:
            months = int(months)
            if months <= 0:
                raise ValueError()
        except ValueError:
            sender.reply("❌ 无效的月数")
            return False
            
        # 计算总价
        total_price = price * months
            
        # 获取收款码
        if not zsm:
            sender.reply("❌ 未配置收款码")
            return False
            
        # 显示收款码
        pay_msg = f"""
=====扫码支付=====
💰 单价: {price}元/月
⏰ 时长: {months}月
👤 用户: {alias}
📱 UID: {uid}
💵 总价: {total_price}元
------------------"""
        
        # 如果价格为0，直接授权，不需要扫码支付
        if price == 0:
            pay_msg += "/n✅ 免费授权，无需支付"
            sender.reply(pay_msg)
            return set_auth_success(uid, months, total_price)
        else:
            # 需要扫码支付
            pay_msg += """请使用微信扫码支付
回复"q"取消"""
            sender.reply(pay_msg)
            sender.replyImage(zsm)
            
            # 等待支付
            result = sender.waitPay("q", 120000)
            if result == 'q':
                sender.reply("✅ 已取消支付")
                return False
                
            # 解析支付结果
            try:
                if isinstance(result, str):
                    result = json.loads(result)
                
                if float(result.get('Money', 0)) or float(result.get('money', 0)) >= float(total_price):
                    # 支付成功，设置授权时间并返回True
                    success = set_auth_success(uid, months, total_price)
                    
                    # 确保上传到青龙
                    if success:
                        # 尝试再次上传到青龙
                        token_info = json.loads(middleware.bucketGet(BUCKET_TOKEN, uid) or '{}')
                        _, _, _, ql_config, ql_envname, _ = get_config()
                        if ql_config and token_info:
                            add_to_qinglong(uid, token_info, ql_envname)
                    
                    return success
                else:
                    sender.reply(f"❌ 支付失败，应付金额{total_price}元，实付金额{result.get('Money', 0)}元")
            except:
                sender.reply("❌ 支付失败，返回数据格式错误")
                return False
    except Exception as e:
        sender.reply(f"❌ 扫码支付失败: {str(e)}")
        return False

def process_coin_auth(uid):
    """处理积分兑换授权"""
    try:
        # 获取配置
        _, coin_price, _, _, _, _ = get_config()
        
        if not coin_price:
            sender.reply("❌ 积分授权未开启")
            return False
            
        # 获取用户信息
        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
        if not token_info_str:
            sender.reply(f"❌ 未找到账号 {uid} 的Token信息")
            return False
            
        token_info = json.loads(token_info_str)
        alias = token_info.get("Alias", "未知用户")
            
        # 获取积分数据桶中的用户积分
        user_coin = Decimal(middleware.bucketGet('dd_sign_points', userid) or '0')
        
        sender.reply(f"""
=====积分兑换=====
👤 用户: {alias}
📱 UID: {uid}
💰 积分: {user_coin}
🎟️ 兑换比例: {coin_price}积分/月
------------------
请输入兑换月数:
回复"q"退出""")
        
        months = sender.listen(60000)
        
        if not months or months == 'q':
            sender.reply("✅ 已退出积分兑换流程")
            return False
            
        try:
            months = int(months)
            if months <= 0:
                raise ValueError()
        except ValueError:
            sender.reply("❌ 无效的月数")
            return False
            
        # 计算所需积分
        required_coin = Decimal(coin_price) * months
        
        # 检查积分是否足够
        if user_coin < required_coin:
            sender.reply(f"❌ 积分不足，当前积分: {user_coin}，需要积分: {required_coin}")
            return False
            
        # 显示确认信息
        confirm_msg = f"""
=====兑换确认=====
👤 用户: {alias}
📱 UID: {uid}
💰 当前积分: {user_coin}
🎟 兑换: {months}个月
💵 需要积分: {required_coin}
💰 剩余积分: {user_coin - required_coin}
------------------
回复"y"确认兑换
回复其他取消"""
        
        sender.reply(confirm_msg)
        confirm = sender.listen(60000)
        
        if confirm.lower() != 'y':
            sender.reply("✅ 已取消兑换")
            return False
            
        # 实际扣除积分数据桶中的积分
        remaining_coin = user_coin - required_coin
        middleware.bucketSet('dd_sign_points', userid, str(remaining_coin))
        
        # 设置授权时间
        auth_time = calculate_auth_time(uid, months)
        middleware.bucketSet(BUCKET_AUTH, uid, auth_time)
        
        # 更新青龙变量
        _, _, _, ql_config, ql_envname, _ = get_config()
        ql_result = False
        
        if ql_config:
            ql_result, _ = add_to_qinglong(uid, token_info, ql_envname)
        
        # 显示成功信息
        success_msg = f"""
=====兑换成功=====
👤 用户: {alias}
📱 UID: {uid}
🎟️ 兑换: {months}个月授权
📅 有效期至: {auth_time}
💰 剩余积分: {remaining_coin}
------------------
🔄 青龙同步: {'成功' if ql_result else '失败'}
=================="""
        
        sender.reply(success_msg)
        return True
        
    except Exception as e:
        sender.reply(f"❌ 积分兑换失败: {str(e)}")
        return False

def generate_iframe_url(url):
    """将URL通过base64编码生成iframe页面链接
    
    Args:
        url: 原始支付链接
        
    Returns:
        str: iframe页面链接
    """
    try:
        encoded = base64.b64encode(url.encode('utf-8')).decode('utf-8')
        iframe_url = f"https://metwhale.github.io?u={encoded}"
        return iframe_url
    except Exception as e:
        return url

def generate_qrcode(url):
    """生成二维码图片
    
    Args:
        url: 要生成二维码的URL
        
    Returns:
        str: 二维码图片的URL
    """
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
    except Exception as e:
        print(f"主接口生成二维码失败: {str(e)}")
    
    try:
        encoded_url = requests.utils.quote(url)
        api_url = f"https://api.qrtool.cn/?text={encoded_url}&size=300&level=M"
        return api_url
    except Exception as e:
        return None

def handle_mapay_order(project, months, money, pay_type=None):
    """处理码支付订单"""
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
    out_trade_no = f"DFCF{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(10000, 99999)}"
    selected_type = pay_type or 'alipay'
    
    sender.reply(
        f"===== 支付信息 =====\n"
        f"🎫 商品: {project}\n"
        f"📅 时长: {months}月\n"
        f"💰 金额: {amount}元\n"
        f"💳 支付: {PAY_TYPE_NAMES.get(selected_type, selected_type)}\n"
        f"=================="
    )
    
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
        # 生成iframe链接后再生成二维码
        iframe_url = generate_iframe_url(pay_url)
        sender.reply('请扫描下方二维码完成支付:')
        sender.replyImage(generate_qrcode(iframe_url))
        sender.reply('输入"q"可取消')
        
        for _ in range(30):
            qresp = requests.get(
                f"{config['gateway'].rstrip('/')}/xpay/epay/api.php",
                params={
                    'act': 'order',
                    'pid': config['pid'],
                    'key': config['key'],
                    'out_trade_no': out_trade_no
                },
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

def process_auth(uid):
    """处理授权流程"""
    try:
        # 获取配置
        price, coin_price, zsm, ql_config, ql_envname, _ = get_config()
        
        # 获取用户信息
        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
        if not token_info_str:
            sender.reply(f"❌ 未找到账号 {uid} 的Token信息")
            return False
            
        token_info = json.loads(token_info_str)
        alias = token_info.get("Alias", "未知用户")
        
        # 构建授权选项
        auth_options = """=====授权选项=====\n"""
        
        # 可用的选项
        options = []
        option_index = 1
        
        # 检查码支付是否开启
        ma_pay_switch = middleware.bucketGet(BUCKET_CONFIG, 'ma_pay_switch') or 'false'
        if ma_pay_switch.lower() == 'true' and middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'):
            for pt in (middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay').split(','):
                auth_options += f"[{option_index}] {PAY_TYPE_NAMES.get(pt.strip(), pt.strip())} ({price}元/月)\n"
                options.append((str(option_index), f"mapay_{pt.strip()}"))
                option_index += 1
        elif zsm and price is not None:  # 只要设置了价格(包括0)和收款码就显示选项
            auth_options += f"[{option_index}] 扫码支付 ({price}元/月)\n"
            options.append((str(option_index), "zsm"))
            option_index += 1
            
        # 积分兑换选项
        if coin_price:
            auth_options += f"[{option_index}] 积分兑换 ({coin_price}积分/月)\n"
            options.append((str(option_index), "coin"))
            option_index += 1
            
        # 检查是否有可用选项
        if not options:
            sender.reply("❌ 未配置任何授权方式，请联系管理员")
            return False
            
        auth_options += """------------------
请选择授权方式
回复"q"退出"""
        
        sender.reply(auth_options)
        option = sender.listen(60000)
        
        if not option or option == 'q':
            sender.reply("✅ 已退出授权流程")
            return False
        
        # 查找选择的支付方式
        selected_pay_type = None
        for opt_num, pay_type in options:
            if option == opt_num:
                selected_pay_type = pay_type
                break
        
        if not selected_pay_type:
            sender.reply("❌ 无效的选择")
            return False
        
        # 获取授权月数
        sender.reply("""请输入授权月数:
回复"q"退出""")
        months = sender.listen(60000)
        
        if not months or months == 'q':
            sender.reply("✅ 已退出授权流程")
            return False
            
        try:
            months = int(months)
            if months <= 0:
                raise ValueError()
        except ValueError:
            sender.reply("❌ 无效的月数")
            return False
        
        # 根据支付方式处理
        if selected_pay_type == "coin":
            return process_coin_auth_with_months(uid, months)
        elif selected_pay_type == "zsm":
            return process_payment_zsm_with_months(uid, months)
        elif selected_pay_type.startswith("mapay_"):
            total_price = float(price) * months
            if handle_mapay_order(PLUGIN_NAME, months, total_price, selected_pay_type.replace('mapay_', '')):
                return set_auth_success(uid, months, total_price)
            return False
        else:
            sender.reply("❌ 无效的选择")
            return False
            
    except Exception as e:
        sender.reply(f"❌ 授权流程失败: {str(e)}")
        return False

def process_payment_zsm_with_months(uid, months):
    """处理扫码支付（已知月数）"""
    try:
        price, _, zsm, _, _, _ = get_config()
        
        if price is None:
            sender.reply("❌ 未设置价格，请联系管理员")
            return False
            
        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
        if not token_info_str:
            sender.reply(f"❌ 未找到账号 {uid} 的Token信息")
            return False
            
        token_info = json.loads(token_info_str)
        alias = token_info.get("Alias", "未知用户")
        total_price = price * months
        
        if not zsm:
            sender.reply("❌ 未配置收款码")
            return False
        
        pay_msg = f"""
=====扫码支付=====
💰 单价: {price}元/月
⏰ 时长: {months}月
👤 用户: {alias}
📱 UID: {uid}
💵 总价: {total_price}元
------------------"""
        
        if price == 0:
            pay_msg += "\n✅ 免费授权，无需支付"
            sender.reply(pay_msg)
            return set_auth_success(uid, months, total_price)
        else:
            pay_msg += """请使用微信扫码支付
回复"q"取消"""
            sender.reply(pay_msg)
            sender.replyImage(zsm)
            
            result = sender.waitPay("q", 120000)
            if result == 'q':
                sender.reply("✅ 已取消支付")
                return False
                
            try:
                if isinstance(result, str):
                    result = json.loads(result)
                
                if float(result.get('Money', 0)) or float(result.get('money', 0)) >= float(total_price):
                    return set_auth_success(uid, months, total_price)
                else:
                    sender.reply(f"❌ 支付失败，应付金额{total_price}元，实付金额{result.get('Money', 0)}元")
            except:
                sender.reply("❌ 支付失败，返回数据格式错误")
                return False
    except Exception as e:
        sender.reply(f"❌ 扫码支付失败: {str(e)}")
        return False

def process_coin_auth_with_months(uid, months):
    """处理积分兑换授权（已知月数）"""
    try:
        _, coin_price, _, _, _, _ = get_config()
        
        if not coin_price:
            sender.reply("❌ 积分授权未开启")
            return False
            
        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
        if not token_info_str:
            sender.reply(f"❌ 未找到账号 {uid} 的Token信息")
            return False
            
        token_info = json.loads(token_info_str)
        alias = token_info.get("Alias", "未知用户")
        user_coin = Decimal(middleware.bucketGet('dd_sign_points', userid) or '0')
        required_coin = Decimal(coin_price) * months
        
        if user_coin < required_coin:
            sender.reply(f"❌ 积分不足，当前积分: {user_coin}，需要积分: {required_coin}")
            return False
        
        confirm_msg = f"""
=====兑换确认=====
👤 用户: {alias}
📱 UID: {uid}
💰 当前积分: {user_coin}
🎟 兑换: {months}个月
💵 需要积分: {required_coin}
💰 剩余积分: {user_coin - required_coin}
------------------
回复"y"确认兑换
回复其他取消"""
        
        sender.reply(confirm_msg)
        confirm = sender.listen(60000)
        
        if confirm.lower() != 'y':
            sender.reply("✅ 已取消兑换")
            return False
        
        remaining_coin = user_coin - required_coin
        middleware.bucketSet('dd_sign_points', userid, str(remaining_coin))
        
        auth_time = calculate_auth_time(uid, months)
        middleware.bucketSet(BUCKET_AUTH, uid, auth_time)
        
        _, _, _, ql_config, ql_envname, _ = get_config()
        ql_result = False
        
        if ql_config:
            ql_result, _ = add_to_qinglong(uid, token_info, ql_envname)
        
        success_msg = f"""
=====兑换成功=====
👤 用户: {alias}
📱 UID: {uid}
🎟️ 兑换: {months}个月授权
📅 有效期至: {auth_time}
💰 剩余积分: {remaining_coin}
------------------
🔄 青龙同步: {'成功' if ql_result else '失败'}
=================="""
        
        sender.reply(success_msg)
        return True
        
    except Exception as e:
        sender.reply(f"❌ 积分兑换失败: {str(e)}")
        return False

# 生成随机UniqueId
def generate_unique_id():
    """生成随机的UniqueId，格式类似: Mcb2djFlYjEwMDZmNDc5MmRmNWVkNTAyNDU4YTAwZTA0MGN8fGllbWlfdGx1YWZlZF9tZQ=eb1b="""
    # 生成随机的hex字符串 (32-40字符)
    hex_part = ''.join(random.choice('0123456789abcdef') for _ in range(random.randint(32, 40)))
    
    # 生成随机的字符串用于base64编码
    random_str = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(20, 30)))
    
    # 添加一些特殊字符
    random_str = f"{random_str}|{random.choice('|+*')}|{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}_" \
                + f"{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}_" \
                + f"{random.choice(string.ascii_letters)}{random.choice(string.ascii_letters)}"
    
    # Base64编码
    base64_part = base64.b64encode(random_str.encode()).decode()
    
    # 添加后缀
    suffix = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(4))
    
    # 组合
    return f"M{hex_part}|{base64_part}{suffix}="

# 微信扫码登录相关函数
def get_qr_code():
    """获取微信二维码UUID"""
    url = "https://open.weixin.qq.com/connect/app/qrconnect"
    params = {
        'appid': APPID,
        'bundleid': BUNDLEID,
        'scope': 'snsapi_userinfo',
        'state': 'wx_oauth_authorization_state',
        'pass_ticket': str(uuid.uuid4())
    }
    headers = {
        'User-Agent': DEFAULT_UA,
        'Referer': "https://open.weixin.qq.com/"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            # 从响应中提取uuid
            match = re.search(r'uuid\: *"(\w+)"', response.text)
            if match:
                return match.group(1)
    except Exception as e:
        print(f'获取二维码失败：{e}')
    return None

def check_scan_status(uuid_str):
    """检查二维码扫描状态"""
    url = f"https://long.open.weixin.qq.com/connect/l/qrconnect"
    params = {
        'uuid': uuid_str,
        'f': 'url',
        '_': int(time.time() * 1000)
    }
    headers = {
        'User-Agent': DEFAULT_UA,
        'Referer': "https://open.weixin.qq.com/"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            # 检查是否扫码成功
            if 'window.wx_errcode=405' in response.text:
                # 提取code和nickname
                code_pattern = r'oauth\?code=([^&]+)&state='
                code_match = re.search(code_pattern, response.text)
                nickname_match = re.search(r"window\.wx_nickname='([^']+)'", response.text)
                
                if code_match:
                    code = code_match.group(1)
                    nickname = nickname_match.group(1) if nickname_match else "未知用户"
                    return {"code": code, "nickname": nickname}
            elif 'window.wx_errcode=408' in response.text:
                return {"status": "waiting"}
            elif 'window.wx_errcode=404' in response.text:
                return {"status": "expired"}
            else:
                return {"status": "unknown"}
    except Exception as e:
        print(f'检查扫码状态失败：{e}')
    return {"status": "error"}

def get_token_by_code(code, device_id=None):
    """通过授权码获取Token（东方财富版本）"""
    if not device_id:
        # 生成随机设备ID
        device_id = generate_device_id()
    
    # 生成随机的EM-GT值
    em_gt = 'ceab-' + ''.join(random.choice('0123456789abcdef') for _ in range(31))
    
    # 1. 获取微信AccessToken
    wechat_token_url = "https://awebapi2-account.eastmoney.com/core/api/ThirdParty/WeChatAccessToken"
    wechat_token_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 15; 2210132C Build/AQ3A.240912.001)',
        'Host': 'awebapi2-account.eastmoney.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip'
    }
    
    # 生成随机的UniqueId
    unique_id = generate_unique_id()
    
    wechat_token_data = {
        "AppId": APPID,
        "UniqueId": unique_id,
        "ProductType": "DFCFT",
        "Version": "10.28.1",
        "DeviceType": "Android15",
        "DomainName": "EastMoneyApp",
        "DeviceModel": "2210132C",
        "DeviceAlias": "",
        "AuthCode": code
    }
    
    # 发送请求获取微信AccessToken
    try:
        wechat_token_response = requests.post(
            wechat_token_url, 
            headers=wechat_token_headers,
            json=wechat_token_data
        )
        
        if wechat_token_response.status_code == 200:
            wechat_token_result = wechat_token_response.json()
            
            # 检查响应是否成功
            if wechat_token_result.get("ReturnCode") == "0":
                # 提取所需数据
                wechat_data = wechat_token_result.get("Data", {})
                access_token = wechat_data.get("Access_Token")
                union_id = wechat_data.get("UnionId")
                nick_name = wechat_data.get("NickName", "未知用户")
                
                # 2. 获取东方财富Token
                dfcf_token_url = "https://awebapi2-account.eastmoney.com/core/api/ThirdParty/AppThirdpartyAccountLoginV2"
                dfcf_token_headers = {
                    'Accept': 'application/json',
                    'EM-OS': 'Android',
                    'EM-PKG': 'com.eastmoney.android.berlin',
                    'EM-VER': '10.28.1',
                    'qgqp-b-id': em_gt,
                    'EM-GT': em_gt,
                    'Content-Type': 'application/json',
                    'Host': 'awebapi2-account.eastmoney.com',
                    'Connection': 'Keep-Alive',
                    'Accept-Encoding': 'gzip',
                    'User-Agent': 'okhttp/3.12.13'
                }
                
                dfcf_token_data = {
                    "AppId": APPID,
                    "UniqueId": unique_id,
                    "ProductType": "DFCFT",
                    "Version": "10.28.1",
                    "DeviceType": "Android15",
                    "DomainName": "EastMoneyApp",
                    "DeviceModel": "2210132C",
                    "DeviceAlias": "",
                    "ScenarioId": "202004073458",
                    "ThirdAccountType": "500",
                    "OpenId": union_id,
                    "At": access_token,
                    "AppType": "cft",
                    "Alias": nick_name,
                    "WangZhengExtension": {
                        "PackageName": "com.eastmoney.android.berlin"
                    }
                }
                
                # 发送请求获取东方财富Token
                dfcf_token_response = requests.post(
                    dfcf_token_url, 
                    headers=dfcf_token_headers,
                    json=dfcf_token_data
                )
                
                if dfcf_token_response.status_code == 200:
                    dfcf_token_result = dfcf_token_response.json()
                    
                    # 3. 发送信息服务请求
                    info_service_result = send_info_service_request(em_gt)
                    
                    # 4. 保存用户信息到数据桶
                    save_user_info(
                        token_result={
                            "wechat_token": wechat_token_result,
                            "dfcf_token": dfcf_token_result,
                            "em_gt": em_gt,
                            "info_service": info_service_result
                        }, 
                        em_gt=em_gt, 
                        device_id=device_id
                    )
                    
                    # 返回完整的Token信息
                    return {
                        "wechat_token": wechat_token_result,
                        "dfcf_token": dfcf_token_result,
                        "em_gt": em_gt,
                        "info_service": info_service_result
                    }
                else:
                    sender.reply(f"获取东方财富Token失败: {dfcf_token_response.text}")
            else:
                sender.reply(f"获取微信AccessToken失败: {wechat_token_result.get('Msg')}")
        else:
            sender.reply(f"请求失败: {wechat_token_response.text}")
    except Exception as e:
        sender.reply(f"获取Token过程中出错: {str(e)}")
    
    return None

def scan_login():
    """微信扫码登录流程"""
    # 获取二维码UUID
    uuid_str = get_qr_code()
    if not uuid_str:
        sender.reply("❌ 获取登录二维码失败，请稍后再试")
        return False
    
    # 构建二维码URL
    qr_url = f"https://open.weixin.qq.com/connect/qrcode/{uuid_str}"
    
    # 发送二维码给用户
    sender.reply("请使用微信扫描下方二维码登录")
    sender.replyImage(qr_url)
    sender.reply("扫码后请在微信中点击「确认登录」\n等待扫码中...\n回复'q'取消操作")
    
    # 轮询检查扫码状态
    retry_count = 0
    max_retries = 60  # 最多等待60秒
    
    while retry_count < max_retries:
        # 检查用户是否取消
        try:
            message = sender.listen(1000)  # 等待1秒
            if message and message.lower() == 'q':
                sender.reply("✅ 已取消扫码登录")
                return False
        except:
            # 如果没有输入，继续检查扫码状态
            pass
        
        # 检查扫码状态
        result = check_scan_status(uuid_str)
        
        if isinstance(result, dict):
            if 'code' in result:
                # 扫码成功
                code = result['code']
                nickname = result.get('nickname', '未知用户')
                sender.reply(f"✅ {nickname} 扫码成功，正在处理登录...")
                
                # 获取token
                token_result = get_token_by_code(code)
                
                return token_result
            elif result.get('status') == 'waiting':
                # 等待扫码
                pass
            #elif result.get('status') == 'expired':
                # 二维码过期
                #sender.reply("⚠️ 二维码已过期，请重新尝试")
                #return False
            elif result.get('status') == 'unknown':
                # 未知状态
                sender.reply("❌ 扫码出现未知状态，请重新尝试")
                return False
            elif result.get('status') == 'error':
                # 扫码错误
                sender.reply("❌ 扫码出现错误，请重新尝试")
                return False
        
        retry_count += 1
        time.sleep(1)
    
    # 超时
    sender.reply("⚠️ 扫码超时，请重新尝试")
    return False

# 生成随机设备ID
def generate_device_id():
    """生成随机的设备ID, 格式: 随机32位字符串||iemi_tluafed_me"""
    random_str = ''.join(random.choice('0123456789abcdef') for _ in range(32))
    return f"{random_str}||iemi_tluafed_me"

# MD5加密
def md5_encrypt(text):
    """计算文本的MD5值"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# 从API获取gtoken
def get_gtoken_from_api(uid):
    """从API获取gtoken
    Args:
        uid: 用户ID
    Returns:
        gtoken或None
    """
    try:
        # 获取管理员用户名
        admin_username = userid
        if not admin_username:
            print("未配置管理员用户名")
            return None
            
        # 构建请求数据
        url = "http://42.194.132.65:62173/get_dfcf_gtoken"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "user": admin_username,
            "uid": uid
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                gtoken = result.get("data", {}).get("gtoken")
                if gtoken == "limit":
                    sender.reply("❌ 该账号已达到gtoken使用上限")
                    return None
                    
                used_count = result.get("data", {}).get("used_count", 0)
                limit = result.get("data", {}).get("limit", 0)
                sender.reply(f"✅ 成功从API获取gtoken: {gtoken[:8]}...\n已使用: {used_count}/{limit}")
                return gtoken
            else:
                print(f"获取gtoken失败: {result.get('message')}")
                return None
        else:
            print(f"请求失败: 状态码 {response.status_code}")
            return None
    except Exception as e:
        print(f"获取gtoken异常: {str(e)}")
        return None

# 生成随机randomCode (类似UUID)
def generate_random_code():
    """生成随机的randomCode，格式类似UUID"""
    return str(uuid.uuid4())

# 获取当前时间戳（毫秒级）
def get_timestamp():
    """获取当前时间戳（毫秒）"""
    return int(time.time() * 1000)

# 发送信息服务请求
def send_info_service_request(em_gt=None):
    """发送信息服务请求
    Args:
        em_gt: EM-GT头部值，如果为None则随机生成
    Returns:
        响应内容
    """
    # 如果未提供em_gt，则随机生成
    if not em_gt:
        em_gt = 'ceab-' + ''.join(random.choice('0123456789abcdef') for _ in range(32))
    
    # 生成设备ID
    device_id = generate_device_id()
    
    # 构建请求URL和Headers
    url = "https://emdcadvertise.eastmoney.com/infoService/v2"
    headers = {
        'Host': 'emdcadvertise.eastmoney.com',
        'em-os': 'Android',
        'em-pkg': 'com.eastmoney.android.berlin',
        'em-ver': '10.28.1',
        'em-gt': em_gt,
        'em-chl': 'xiaomi22_64',
        'em-gv': '3f4605b67',
        'em-sl': '0',
        'em-pa': '1',
        'em-dns': '1',
        'em-ab': 'R_1Lk;test_1LG;',
        'content-type': 'text/json; charset=utf-8',
        'accept-encoding': 'gzip',
        'user-agent': 'okhttp/3.12.13'
    }
    
    # 构建请求体
    request_body = {
        "appKey": "cfw",
        "args": {
            "customerId": "",
            "fundLogin": False,
            "hkFundLogin": False,
            "line": 5,
            "pageId": "app_grzx",
            "positions": "",
            "switchMap": {"shilaohua": "0"},
            "uid": ""
        },
        "client": "android",
        "clientType": "cfw",
        "clientVersion": "10.28.1",
        "deviceId": device_id,
        "method": "marketad",
        "randomCode": generate_random_code(),
        "reserve": "",
        "timestamp": get_timestamp()
    }
    
    # 发送请求
    try:
        response = requests.post(
            url,
            headers=headers,
            json=request_body
        )
        
        if response.status_code == 200:
            try:
                response_json = response.json()
                return response_json
            except:
                return response.text
        else:
            return None
    except Exception as e:
        print(f"发送请求出错: {str(e)}")
        return None

# 获取token后保存用户信息到数据桶
def save_user_info(token_result, em_gt, device_id):
    """保存用户信息到数据桶
    Args:
        token_result: 获取token的响应结果
        em_gt: EM-GT值
        device_id: 设备ID
    Returns:
        是否保存成功
    """
    try:
        # 从响应中提取所需数据
        if not token_result or "dfcf_token" not in token_result:
            sender.reply("❌ 无法保存用户信息，数据不完整")
            return False
            
        # 获取dfcf_token数据
        dfcf_data = token_result.get("dfcf_token", {}).get("Data", {})
        if not dfcf_data:
            sender.reply("❌ 无法获取用户Token数据")
            return False
            
        # 提取所需的字段
        uid = dfcf_data.get("UID")
        c_token = dfcf_data.get("CToken")
        u_token = dfcf_data.get("UToken")
        g_token = f"ceab-{dfcf_data.get('CId')}"
        alias = dfcf_data.get("Alias", "未知用户")  # 用户昵称
        
        # 生成设备ID的base64编码
        em_md = base64.b64encode(device_id.encode()).decode()
        
        # 没有UID无法保存
        if not uid:
            sender.reply("❌ 无法获取用户UID")
            return False
            
        # 从API获取gtoken
        api_gtoken = get_gtoken_from_api(uid)
        if not api_gtoken:
            sender.reply(f"⚠️ 从API获取gtoken失败，使用原始gtoken: {em_gt[:15]}...")
        
        # 构建要保存的数据
        token_data = {
            "UID": uid,
            "CToken": c_token,
            "UToken": u_token,
            "EM-MD": em_md,
            "GToken": api_gtoken or em_gt,  # 优先使用API获取的gtoken，失败则使用原始的
            "DeviceID": device_id,
            "Alias": alias,
            "UpdateTime": int(time.time())  # 保存更新时间
        }
        
        # 获取当前用户已绑定的账号列表
        user_accounts = eval(middleware.bucketGet(BUCKET_USER, userid) or '[]')
        
        # 检查当前账号是否已存在
        if uid not in user_accounts:
            user_accounts.append(uid)
            middleware.bucketSet(BUCKET_USER, userid, str(user_accounts))
            
        # 保存Token信息
        middleware.bucketSet(BUCKET_TOKEN, uid, json.dumps(token_data, ensure_ascii=False))
        
        # 登录成功提示
        success_msg = f"""
=====登录成功=====
👤 用户: {alias}
📱 UID: {uid}
✅ 数据已保存
=================="""
        
        sender.reply(success_msg)
        
        # 检查是否已授权
        auth_time = middleware.bucketGet(BUCKET_AUTH, uid) or ''
        current_date = datetime.now().strftime("%Y-%m-%d")
        if not auth_time or auth_time < current_date:
            process_auth(uid)
        else:
            # 已授权，更新青龙变量
            _, _, _, ql_config, ql_envname, _ = get_config()
            if ql_config:
                ql_result, ql_message = add_to_qinglong(uid, token_data, ql_envname)
                if ql_result:
                    print(f"更新青龙变量成功: {uid}")
                else:
                    print(f"更新青龙变量失败: {ql_message}")
        
        return True
        
    except Exception as e:
        sender.reply(f"❌ 保存用户信息失败: {str(e)}")
        return False
# 添加查询用户信息功能
def query_user_info(uid):
    """查询用户信息
    Args:
        uid: 用户UID
    Returns:
        查询结果
    """
    try:
        # 从数据桶中获取Token信息
        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
        if not token_info_str:
            return f"❌ 未找到账号 {uid} 的Token信息"
            
        # 解析Token信息
        token_info = json.loads(token_info_str)
        c_token = token_info.get("CToken")
        u_token = token_info.get("UToken")
        g_token = token_info.get("GToken")
        em_md = token_info.get("EM-MD")
        alias = token_info.get("Alias", "未知用户")
        
        # 获取授权信息
        auth_time = middleware.bucketGet(BUCKET_AUTH, uid) or '未授权'
        
        # 检查必要的Token是否存在
        if not all([c_token, u_token, g_token, em_md]):
            return f"❌ 账号 {uid} 的Token信息不完整"
            
        # 构建请求Headers
        headers = {
            "Host": "empointcpf.eastmoney.com",
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "\"Android\"",
            "CToken": c_token,
            "UToken": u_token,
            "sec-ch-ua": "\"Chromium\";v=\"142\", \"Android WebView\";v=\"142\", \"Not_A Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?1",
            "EM-OS": "Android",
            "EM-VER": "10.37.1",
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; 2210132C Build/BP2A.250605.031.A3; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/142.0.7444.102 Mobile Safari/537.36;eastmoney_android;color=w;pkg=com.eastmoney.android.berlin;appver=10.37.1;tag=260491657;statusBarHeight=35.142857;titleBarHeight=45.142857;density=3.5;androidsdkversion=36;fontsize=2;listFontSize=1;adaptAgedSwitch=0",
            "Appkey": "EIBnBlYuvK",
            "EM-MD": em_md,
            "Accept": "*/*",
            "Origin": "https://vipmoney.eastmoney.com",
            "X-Requested-With": "com.eastmoney.android.berlin",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://vipmoney.eastmoney.com/",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        # 查询余额信息
        balance_url = "https://empointcpf.eastmoney.com/cashredpackets/Cash/balance?v=0723667712619922"
        response = requests.get(balance_url, headers=headers)

        if response.status_code != 200:
            return f"❌ 请求失败: 状态码 {response.status_code}"

        try:
            result = response.json()
            if result.get("result") != 1:
                return f"❌ 请求失败: {result.get('message', '未知错误')}"

            balance = result.get("data", 0)
            
            # 查询余额明细
            flows_url = "https://empointcpf.eastmoney.com/cashredpackets/cash/flows?pageIndex=1&pageSize=20"
            flows_response = requests.get(flows_url, headers=headers)
            
            flow_details = ""
            if flows_response.status_code == 200:
                flows_result = flows_response.json()
                if flows_result.get("result") == 1:
                    flows_data = flows_result.get("data", [])
                    # 取前5条明细
                    for flow in flows_data[:5]:
                        amount = flow.get("Amount", 0)
                        flow_type = flow.get("FlowType", 1)
                        flow_time = flow.get("FlowTime", "")
                        # FlowType: 1为正(收入), 2为负(支出)
                        if flow_type == 1:
                            flow_details += f"💵 +{amount:.2f} {flow_time}\n"
                        else:
                            flow_details += f"💸 -{amount:.2f} {flow_time}\n"
            
            # 构建查询结果消息
            query_msg = f"""=====账号信息=====
👤 用户: {alias}
📱 UID: {uid}
💰 余额: {balance}
📅 授权到期: {auth_time}
==================
{flow_details}=================="""
            return query_msg
            
        except json.JSONDecodeError:
            return f"❌ 解析响应失败: 响应不是有效的JSON格式"
            
    except Exception as e:
        return f"❌ 查询失败: {str(e)}"

# 添加查询所有账号功能
def query_all_accounts():
    """查询用户所有绑定账号的信息"""
    try:
        # 获取用户绑定的账号
        user_accounts = eval(middleware.bucketGet(BUCKET_USER, userid) or '[]')
        if not user_accounts:
            sender.reply("❌ 您还没有绑定东方财富账号")
            return

        # 遍历每个账号
        for uid in user_accounts:
            # 查询账号信息
            result = query_user_info(uid)
            sender.reply(result)
            
    except Exception as e:
        sender.reply(f"❌ 查询失败: {str(e)}")

# 账号管理功能
def manage_eastmoney():
    """东方财富账号管理"""
    try:
        # 获取用户绑定的账号
        accounts = eval(middleware.bucketGet(BUCKET_USER, userid) or '[]')
        if not accounts:
            sender.reply("❌ 您还没有绑定东方财富账号")
            return

        # 显示管理选项
        manage_options = """
=====管理选项=====
[1] 账号授权
[2] 账号删除
------------------
回复数字选择操作
回复"q"退出"""
        
        sender.reply(manage_options)
        option = sender.listen(60000)
        
        if not option or option == 'q':
            sender.reply("✅ 已退出管理流程")
            return
            
        if option not in ['1', '2']:
            sender.reply("❌ 无效的选择")
            return

        # 显示账号列表
        account_list = "=====账号列表=====\n[0] 选择全部账号\n"
        for i, uid in enumerate(accounts, 1):
            token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
            if token_info_str:
                try:
                    token_info = json.loads(token_info_str)
                    alias = token_info.get("Alias", "未知用户")
                    auth_time = middleware.bucketGet(BUCKET_AUTH, uid) or '未授权'
                    account_list += f"[{i}] {alias} ({uid}) - {auth_time}\n"
                except:
                    account_list += f"[{i}] {uid} - 数据错误\n"
            else:
                account_list += f"[{i}] {uid} - 数据错误\n"
            
        manage_msg = f"""{account_list}
------------------
请选择要{option=='1'and'授权'or'删除'}的账号
可以输入多个账号序号，使用英文逗号分隔
例如: 1,3,5
回复"q"退出"""
        
        sender.reply(manage_msg)
        choice = sender.listen(60000)
        
        if not choice or choice == 'q':
            sender.reply("✅ 已退出管理流程")
            return

        # 处理选择的账号
        selected_uids = []
        try:
            if choice == '0':
                # 选择全部账号
                selected_uids = accounts.copy()
            else:
                # 处理多选
                indices = [int(idx.strip()) - 1 for idx in choice.split(',')]
                for index in indices:
                    if 0 <= index < len(accounts):
                        selected_uids.append(accounts[index])
                    else:
                        sender.reply(f"❌ 无效的选择: {index + 1}")
                        return
                
            if not selected_uids:
                sender.reply("❌ 未选择任何账号")
                return
        except ValueError:
            sender.reply("❌ 无效的选择格式")
            return

        if option == '1':
            # 授权
            success_count = 0
            for selected_uid in selected_uids:
                auth_success = process_auth(selected_uid)
                
                # 确保上传到青龙
                if auth_success:
                    success_count += 1
                    token_info_str = middleware.bucketGet(BUCKET_TOKEN, selected_uid)
                    if token_info_str:
                        token_info = json.loads(token_info_str)
                        _, _, _, ql_config, ql_envname, _ = get_config()
                        if ql_config:
                            add_to_qinglong(selected_uid, token_info, ql_envname)
            
            if len(selected_uids) > 1:
                sender.reply(f"✅ 授权完成，成功授权 {success_count}/{len(selected_uids)} 个账号")
        else:
            # 删除
            if len(selected_uids) == 1:
                # 如果只选择了一个账号，按原来的流程处理
                selected_uid = selected_uids[0]
                token_info_str = middleware.bucketGet(BUCKET_TOKEN, selected_uid)
                alias = "未知用户"
                if token_info_str:
                    try:
                        token_info = json.loads(token_info_str)
                        alias = token_info.get("Alias", "未知用户")
                    except:
                        pass
                        
                confirm_msg = f"""=====删除确认=====
即将删除以下账号:
👤 用户: {alias}
📱 UID: {selected_uid}
------------------
⚠️ 数据无法恢复
回复"y"确认删除
"""
                
                sender.reply(confirm_msg)
                confirm = sender.listen(60000)
                
                if confirm.lower() != 'y':
                    sender.reply("✅ 已取消删除")
                    return
                
                # 删除账号
                try:
                    accounts.remove(selected_uid)
                    middleware.bucketSet(BUCKET_TOKEN, selected_uid, '')
                    middleware.bucketSet(BUCKET_AUTH, selected_uid, '')
                    
                    # 更新用户的账号列表
                    if accounts:
                        middleware.bucketSet(BUCKET_USER, userid, str(accounts))
                    else:
                        middleware.bucketDel(BUCKET_USER, userid)
                        
                    # 从青龙中删除
                    _, _, _, ql_config, ql_envname, _ = get_config()
                    if ql_config:
                        delete_from_qinglong(selected_uid, ql_envname)
                    
                    sender.reply(f"✅ 已成功删除账号: {alias} ({selected_uid})")
                except Exception as e:
                    sender.reply(f"❌ 删除失败: {str(e)}")
            else:
                # 如果选择了多个账号，显示一个总的确认信息
                account_info = ""
                for i, uid in enumerate(selected_uids, 1):
                    token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
                    alias = "未知用户"
                    if token_info_str:
                        try:
                            token_info = json.loads(token_info_str)
                            alias = token_info.get("Alias", "未知用户")
                        except:
                            pass
                    account_info += f"{i}. {alias} ({uid})\n"
                    
                confirm_msg = f"""=====删除确认=====
即将删除以下 {len(selected_uids)} 个账号:
{account_info}
------------------
⚠️ 数据无法恢复
回复"y"确认删除
"""
                
                sender.reply(confirm_msg)
                confirm = sender.listen(60000)
                
                if confirm.lower() != 'y':
                    sender.reply("✅ 已取消删除")
                    return
                
                # 删除账号
                success_count = 0
                for selected_uid in selected_uids:
                    try:
                        accounts.remove(selected_uid)
                        middleware.bucketSet(BUCKET_TOKEN, selected_uid, '')
                        middleware.bucketSet(BUCKET_AUTH, selected_uid, '')
                        
                        # 从青龙中删除
                        _, _, _, ql_config, ql_envname, _ = get_config()
                        if ql_config:
                            delete_from_qinglong(selected_uid, ql_envname)
                        
                        success_count += 1
                    except Exception as e:
                        print(f"删除账号 {selected_uid} 失败: {str(e)}")
                
                # 更新用户的账号列表
                if accounts:
                    middleware.bucketSet(BUCKET_USER, userid, str(accounts))
                else:
                    middleware.bucketDel(BUCKET_USER, userid)
                
                sender.reply(f"✅ 删除完成，成功删除 {success_count}/{len(selected_uids)} 个账号")
            
    except Exception as e:
        sender.reply(f"❌ 管理失败: {str(e)}")

def calculate_auth_time_by_days(uid, days):
    """按天数计算授权时间
    Args:
        uid: 用户UID
        days: 天数（正数增加，负数减少）
    Returns:
        新的授权到期日期字符串
    """
    try:
        current_auth = middleware.bucketGet(BUCKET_AUTH, uid)
        
        if current_auth and datetime.strptime(current_auth, "%Y-%m-%d").date() > datetime.now().date():
            base_date = datetime.strptime(current_auth, "%Y-%m-%d").date()
        else:
            base_date = datetime.now().date()
        
        new_date = base_date + timedelta(days=int(days))
        return str(new_date)
        
    except Exception as e:
        raise Exception(f"计算授权时间失败: {str(e)}")

# 管理员授权所有用户
def admin_auth_all_accounts():
    """管理员一键授权所有用户的所有账号"""
    try:
        users = middleware.bucketAllKeys(BUCKET_USER)
        if not users:
            sender.reply("❌ 未找到任何用户账号")
            return
        
        # 统计总账号数
        total_accounts = 0
        for user_id in users:
            accounts_str = middleware.bucketGet(BUCKET_USER, user_id)
            if accounts_str and accounts_str != '[]':
                total_accounts += len(eval(accounts_str))
        
        sender.reply(f"""
=====授权所有用户=====
👥 用户数: {len(users)}
📊 账号数: {total_accounts}
------------------
请输入授权天数:
(正数增加天数，负数减少天数)
回复"q"退出""")
        
        days_input = sender.listen(60000)
        if not days_input or days_input == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            days = int(days_input)
        except ValueError:
            sender.reply("❌ 无效的天数")
            return
        
        action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
        sender.reply(f"""
=====确认授权=====
👥 用户数: {len(users)}
📊 账号数: {total_accounts}
⏰ 操作: {action_text}
------------------
⚠️ 此操作影响所有用户
回复"y"确认
回复其他取消""")
        
        confirm = sender.listen(60000)
        if not confirm or confirm.lower() != 'y':
            sender.reply("✅ 已取消授权")
            return
        
        success_count = 0
        fail_count = 0
        
        for user_id in users:
            accounts_str = middleware.bucketGet(BUCKET_USER, user_id)
            if not accounts_str or accounts_str == '[]':
                continue
            
            try:
                accounts = eval(accounts_str)
                for uid in accounts:
                    try:
                        token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
                        if not token_info_str:
                            fail_count += 1
                            continue
                        
                        new_auth_time = calculate_auth_time_by_days(uid, days)
                        middleware.bucketSet(BUCKET_AUTH, uid, new_auth_time)
                        
                        _, _, _, ql_config, ql_envname, _ = get_config()
                        if ql_config:
                            token_info = json.loads(token_info_str)
                            add_to_qinglong(uid, token_info, ql_envname)
                        
                        success_count += 1
                    except Exception as e:
                        print(f"授权账号 {uid} 出错: {str(e)}")
                        fail_count += 1
            except Exception as e:
                print(f"处理用户 {user_id} 出错: {str(e)}")
        
        sender.reply(f"""
=====授权结果=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 操作: {action_text}
==================""")
        
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")

# 管理员按用户授权
def admin_auth_by_user():
    """管理员按用户授权 - 手动输入用户ID，按天数授权"""
    try:
        sender.reply("""
=====按用户授权=====
请输入用户ID:
回复"q"退出""")
        
        target_user_id = sender.listen(60000)
        if not target_user_id or target_user_id == 'q':
            sender.reply("✅ 已退出")
            return
        
        accounts_str = middleware.bucketGet(BUCKET_USER, target_user_id)
        if not accounts_str or accounts_str == '[]':
            sender.reply(f"❌ 用户 {target_user_id} 没有绑定任何账号")
            return
        
        accounts = eval(accounts_str)
        
        account_list = f"=====用户 {target_user_id} 的账号=====\n[0] 选择全部账号\n"
        for i, uid in enumerate(accounts, 1):
            token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
            if token_info_str:
                try:
                    token_info = json.loads(token_info_str)
                    alias = token_info.get("Alias", "未知用户")
                    auth_time = middleware.bucketGet(BUCKET_AUTH, uid) or '未授权'
                    account_list += f"[{i}] {alias} ({uid}) - {auth_time}\n"
                except:
                    account_list += f"[{i}] {uid} - 数据错误\n"
            else:
                account_list += f"[{i}] {uid} - 数据错误\n"
        
        account_list += """------------------
支持多选，用逗号分隔
回复"q"退出"""
        
        sender.reply(account_list)
        account_choice = sender.listen(60000)
        
        if not account_choice or account_choice == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        selected_uids = []
        if account_choice == '0':
            selected_uids = accounts.copy()
        else:
            try:
                indices = [int(idx.strip()) - 1 for idx in account_choice.split(',') if idx.strip().isdigit()]
                for index in indices:
                    if 0 <= index < len(accounts):
                        selected_uids.append(accounts[index])
            except:
                sender.reply("❌ 无效的选择格式")
                return
        
        if not selected_uids:
            sender.reply("❌ 未选择任何账号")
            return
        
        sender.reply(f"""
已选择 {len(selected_uids)} 个账号
请输入授权天数:
(正数增加天数，负数减少天数)
回复"q"退出""")
        
        days_input = sender.listen(60000)
        if not days_input or days_input == 'q':
            sender.reply("✅ 已取消授权")
            return
        
        try:
            days = int(days_input)
        except ValueError:
            sender.reply("❌ 无效的天数")
            return
        
        action_text = f"增加 {days} 天" if days > 0 else f"减少 {abs(days)} 天"
        sender.reply(f"""
=====确认授权=====
📊 账号数: {len(selected_uids)} 个
⏰ 操作: {action_text}
------------------
回复"y"确认
回复其他取消""")
        
        confirm = sender.listen(60000)
        if not confirm or confirm.lower() != 'y':
            sender.reply("✅ 已取消授权")
            return
        
        success_count = 0
        fail_count = 0
        
        for uid in selected_uids:
            try:
                token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
                if not token_info_str:
                    fail_count += 1
                    continue
                
                new_auth_time = calculate_auth_time_by_days(uid, days)
                middleware.bucketSet(BUCKET_AUTH, uid, new_auth_time)
                
                _, _, _, ql_config, ql_envname, _ = get_config()
                if ql_config:
                    token_info = json.loads(token_info_str)
                    add_to_qinglong(uid, token_info, ql_envname)
                
                success_count += 1
            except Exception as e:
                print(f"授权账号 {uid} 出错: {str(e)}")
                fail_count += 1
        
        sender.reply(f"""
=====授权结果=====
✅ 成功: {success_count} 个账号
❌ 失败: {fail_count} 个账号
⏰ 操作: {action_text}
==================""")
        
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")

# 管理员授权功能入口
def admin_auth_management():
    """管理员授权管理"""
    try:
        sender.reply("""
=====管理员授权=====
[1] 授权所有用户
[2] 按用户授权
------------------
回复数字选择操作
回复"q"退出""")
        
        option = sender.listen(60000)
        if not option or option == 'q':
            sender.reply("✅ 已退出管理员授权")
            return
        
        if option == '1':
            admin_auth_all_accounts()
        elif option == '2':
            admin_auth_by_user()
        else:
            sender.reply("❌ 无效的选择")
            
    except Exception as e:
        sender.reply(f"❌ 管理员授权失败: {str(e)}")

def mask_uid(uid):
    """隐藏UID中间部分"""
    if not uid or len(uid) < 6:
        return uid
    return f"{uid[:3]}***{uid[-3:]}"

def check_auth_status():
    """检测授权状态并推送通知
    逻辑：到期时间-当前日期 > 提前天数，不推送
          到期时间-当前日期 <= 提前天数 且 > 0，推送提醒
          到期时间-当前日期 <= 0，清理账号
    """
    notify = middleware.bucketGet(BUCKET_CONFIG, 'notify') or ''
    if not notify:
        return "❌ 未配置通知渠道"
    
    channels = [c.strip() for c in notify.split(',') if c.strip()]
    all_users = middleware.bucketAllKeys(BUCKET_USER)
    if not all_users:
        return "❌ 没有用户"
    
    # 获取提前提醒天数配置，默认3天
    notify_days = int(middleware.bucketGet(BUCKET_CONFIG, 'notify_days') or '3')
    
    current_date = datetime.now().date()
    total, notified, cleaned = 0, 0, 0
    
    for user_id in all_users:
        try:
            accounts = eval(middleware.bucketGet(BUCKET_USER, user_id) or '[]')
            
            # 分类账号：需要提醒的和需要清理的
            to_notify = []  # 需要提醒的账号
            to_clean = []   # 需要清理的账号
            
            for uid in accounts:
                auth_time_str = middleware.bucketGet(BUCKET_AUTH, uid)
                token_info_str = middleware.bucketGet(BUCKET_TOKEN, uid)
                alias = "未知用户"
                if token_info_str:
                    try:
                        token_info = json.loads(token_info_str)
                        alias = token_info.get("Alias", "未知用户")
                    except:
                        pass
                
                if not auth_time_str:
                    # 未授权，直接清理
                    to_clean.append({'uid': uid, 'alias': alias, 'auth_time': '未授权', 'days_left': 0})
                    continue
                
                try:
                    auth_date = datetime.strptime(auth_time_str, "%Y-%m-%d").date()
                    days_left = (auth_date - current_date).days
                    
                    if days_left <= 0:
                        # 已过期，清理
                        to_clean.append({'uid': uid, 'alias': alias, 'auth_time': auth_time_str, 'days_left': days_left})
                    elif days_left <= notify_days:
                        # 即将过期，提醒
                        to_notify.append({'uid': uid, 'alias': alias, 'auth_time': auth_time_str, 'days_left': days_left})
                    # days_left > notify_days 不做任何操作
                except:
                    # 日期格式错误，清理
                    to_clean.append({'uid': uid, 'alias': alias, 'auth_time': auth_time_str, 'days_left': 0})
            
            total += len(accounts)
            
            # 处理需要清理的账号
            if to_clean:
                for acc in to_clean:
                    uid = acc['uid']
                    delete_from_qinglong(uid)
                    middleware.bucketSet(BUCKET_TOKEN, uid, '')
                    
                    if uid in accounts:
                        accounts.remove(uid)
                    
                    middleware.bucketSet(BUCKET_AUTH, uid, '')
                    cleaned += 1
                
                # 更新用户账号列表
                if accounts:
                    middleware.bucketSet(BUCKET_USER, user_id, str(accounts))
                else:
                    middleware.bucketDel(BUCKET_USER, user_id)
            
            # 处理需要提醒的账号
            if to_notify:
                notify_list = "\n".join([
                    f"📱 {a['alias']}({mask_uid(a['uid'])}) 剩余{a['days_left']}天({a['auth_time']})"
                    for a in to_notify
                ])
                msg = (
                    f"=====东方财富账号检测=====\n"
                    f"⚠️ 即将过期:\n{notify_list}\n"
                    f"💡 发送\"东方管理\"续费\n"
                    f"=================="
                )
                for ch in channels:
                    try:
                        middleware.push(
                            imType=ch,
                            groupCode='',
                            userID=user_id,
                            title="",
                            content=msg
                        )
                        notified += 1
                    except:
                        pass
        except:
            pass
    
    return f"✅ 东方财富检测完成，共 {total} 个账号，发送 {notified} 条通知，清理 {cleaned} 个过期账号"

# 青龙相关功能实现
def get_ql_token(host, client_id, client_secret):
    """获取青龙面板的访问令牌"""
    try:
        url = f'{host}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
        response = requests.get(url)
        data = response.json()
        if data.get('code') == 200:
            return data['data']['token']
        print(f"获取青龙token失败: {data}")
        return None
    except Exception as e:
        print(f"获取青龙token异常: {str(e)}")
        return None

def add_to_qinglong(uid, token_info, env_name="S_DFCF"):
    """添加东方财富账号到青龙"""
    try:
        # 获取配置
        _, _, _, ql_config, ql_envname, _ = get_config()
        
        if not ql_config:
            print("未配置青龙信息")
            return False, "未配置青龙信息"
            
        # 分割青龙配置信息 - 使用中文丨分隔符
        configs = ql_config.split('丨')
        if len(configs) < 3:
            # 尝试使用英文|分割作为兼容处理
            configs = ql_config.split('|')
            if len(configs) < 3:
                print("青龙配置格式错误")
                return False, "青龙配置格式错误"
            
        host = configs[0].strip()
        client_id = configs[1].strip()
        client_secret = configs[2].strip()
        
        # 获取token
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False, "获取青龙token失败"
            
        headers = {'Authorization': f'Bearer {token}'}
        
        # 查找并删除已存在的变量
        envs_response = requests.get(f'{host}/open/envs', headers=headers)
        if envs_response.status_code != 200:
            print(f"获取环境变量失败: {envs_response.text}")
            return False, "获取环境变量失败"
            
        envs = envs_response.json()['data']
        for env in envs:
            if env['name'] == env_name and uid in env['value']:
                # 兼容不同版本的青龙面板
                env_id = env.get('_id') or env.get('id')
                if env_id:
                    delete_response = requests.delete(f'{host}/open/envs', headers=headers, json=[env_id])
                    if delete_response.status_code != 200:
                        print(f"删除旧变量失败: {delete_response.text}")
                break
        
        # 构建变量值
        # 从token_info中提取必要信息
        if isinstance(token_info, str):
            token_info = json.loads(token_info)
            
        uid = token_info.get("UID", "")
        c_token = token_info.get("CToken", "")
        u_token = token_info.get("UToken", "")
        g_token = token_info.get("GToken", "")
        em_md = token_info.get("EM-MD", "")
        device_id = token_info.get("DeviceID", "")
        alias = token_info.get("Alias", "未知用户")
        
        # 构建变量值 - 格式: uid#ctoken#utoken#gtoken#emmd#deviceid#alias
        env_value = f"{uid}#{c_token}#{u_token}#{g_token}#{em_md}#{device_id}#{alias}"
        
        # 获取授权时间
        auth_time = middleware.bucketGet(BUCKET_AUTH, uid) or '未授权'
        
        # 添加新变量
        data = [{
            'name': env_name,
            'value': env_value,
            'remarks': f"东方UID：{uid}|到期：{auth_time}"
        }]
        
        add_response = requests.post(f'{host}/open/envs', headers=headers, json=data)
        if add_response.status_code != 200:
            print(f"添加变量失败: {add_response.text}")
            return False, "添加变量失败"
            
        result = add_response.json()
        if result['code'] != 200:
            print(f"添加变量失败: {result}")
            return False, f"添加变量失败: {result.get('message')}"
            
        # 启用变量
        new_id = result['data'][0].get('_id') or result['data'][0].get('id')
        if new_id:
            enable_response = requests.put(f'{host}/open/envs/enable', headers=headers, json=[new_id])
            if enable_response.status_code != 200:
                print(f"启用变量失败: {enable_response.text}")
        
        return True, "添加青龙变量成功"
        
    except Exception as e:
        error_msg = f"添加青龙变量异常: {str(e)}"
        print(error_msg)
        return False, error_msg

def delete_from_qinglong(uid, env_name=None):
    """从青龙面板删除指定账号的变量"""
    try:
        # 获取配置
        _, _, _, ql_config, ql_envname, _ = get_config()
        
        if not env_name:
            env_name = ql_envname
            
        if not ql_config:
            print("未配置青龙信息")
            return False, "未配置青龙信息"
            
        # 分割青龙配置信息 - 使用中文丨分隔符
        configs = ql_config.split('丨')
        if len(configs) < 3:
            # 尝试使用英文|分割作为兼容处理
            configs = ql_config.split('|')
            if len(configs) < 3:
                print("青龙配置格式错误")
                return False, "青龙配置格式错误"
            
        host = configs[0].strip()
        client_id = configs[1].strip()
        client_secret = configs[2].strip()
        
        # 获取token
        token = get_ql_token(host, client_id, client_secret)
        if not token:
            return False, "获取青龙token失败"
            
        headers = {'Authorization': f'Bearer {token}'}
        
        # 查找并删除变量
        envs_response = requests.get(f'{host}/open/envs', headers=headers)
        if envs_response.status_code != 200:
            print(f"获取环境变量失败: {envs_response.text}")
            return False, "获取环境变量失败"
            
        envs = envs_response.json()['data']
        deleted = False
        
        for env in envs:
            if env['name'] == env_name and uid in env['value']:
                # 删除变量
                env_id = env.get('_id') or env.get('id')
                if env_id:
                    delete_response = requests.delete(f'{host}/open/envs', headers=headers, json=[env_id])
                    if delete_response.status_code == 200:
                        deleted = True
                        print(f"删除青龙变量成功: {env_id}")
                    else:
                        print(f"删除青龙变量失败: {delete_response.text}")
                        
        return deleted, "删除" + ("成功" if deleted else "失败")
        
    except Exception as e:
        error_msg = f"删除青龙变量异常: {str(e)}"
        print(error_msg)
        return False, error_msg

# 在scan_login函数后添加密码登录函数
def account_login(account, password):
    """账号密码登录东方财富
    Args:
        account: 账号（手机号）
        password: 密码
    Returns:
        登录结果，成功返回True，失败返回False
    """
    try:
        # 生成随机设备ID
        device_id = generate_device_id()
        
        # 生成随机UniqueId
        unique_id = generate_unique_id()
        
        # 生成随机的EM-GT值
        em_gt = 'ceab-' + ''.join(random.choice('0123456789abcdef') for _ in range(31))
        
        # 设备ID的base64编码
        em_md = base64.b64encode(device_id.encode()).decode()
        
        # MD5加密密码
        password_md5 = md5_encrypt(password)
        
        # 登录流程
        return account_login_with_verification(account, password_md5, unique_id, device_id, em_gt)
    except Exception as e:
        sender.reply(f"❌ 登录过程出错: {str(e)}")
        return False

def account_login_with_verification(account, password_md5, unique_id, device_id, em_gt, vcode="", vcode_context=""):
    """带验证码处理的账号密码登录流程
    Args:
        account: 账号
        password_md5: MD5加密后的密码
        unique_id: 唯一ID
        device_id: 设备ID
        em_gt: EM-GT值
        vcode: 图片验证码
        vcode_context: 验证码上下文
    Returns:
        登录结果
    """
    try:
        # 设备ID的base64编码
        em_md = base64.b64encode(device_id.encode()).decode()
        
        # 构建请求URL和Headers
        url = "https://awebapi2-account.eastmoney.com/core/api/MPassport/LoginMobileV4"
        headers = {
            'Accept': 'application/json',
            'em-clt-uiid': unique_id,
            'em-clt-auth': '202107280688;qXU2bhqAdsux+eTFLOqWgXwz8GJyfhX/ejnm0eJ9aMc=',
            'qgqp-b-id': em_gt,
            'em_clt_uiid': unique_id,
            'qgqp_b_id': em_gt,
            'EM-OS': 'Android',
            'EM-PKG': 'com.eastmoney.android.berlin',
            'EM-VER': '10.28.1',
            'EM-GT': em_gt,
            'EM-MD': urllib.parse.quote(em_md),
            'EM-CHL': 'xiaomi22_64',
            'EM-GV': '3f4605b67',
            'EM-CT': '',
            'EM-UT': '',
            'EM-SL': '0',
            'EM-PA': '1',
            'em-dns': '1',
            'EM-AB': 'R_1Lk|1Ls;test_1LG;',
            'Content-Type': 'application/json',
            'Host': 'awebapi2-account.eastmoney.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.12.13'
        }
        
        # 构建请求体
        request_body = {
            "AppId": "202107280688",
            "UniqueId": unique_id,
            "ProductType": "DFCFT",
            "Version": "10.28.1",
            "DeviceType": "Android15",
            "DomainName": "EastMoneyApp",
            "DeviceModel": "2210132C",
            "DeviceAlias": "",
            "ScenarioId": "202003257918",
            "Account": account,
            "Password": password_md5
        }
        
        # 如果有验证码，添加到请求中
        if vcode:
            request_body["VCode"] = vcode
            request_body["VCodeContext"] = vcode_context if vcode_context else "EmPaVCodeCo"
        
        # 发送请求
        response = requests.post(url, headers=headers, json=request_body)
        
        # 检查响应状态
        if response.status_code == 200:
            # 解析响应
            login_result = response.json()
            
            # 检查登录状态
            return_code = login_result.get("ReturnCode")
            error_msg = login_result.get("Msg", "")
            
            # 处理不同的登录结果
            if return_code == "0":
                # 登录成功
                user_data = login_result.get("Data", {})
                
                # 发送信息服务请求
                info_service_result = send_info_service_request(em_gt)
                
                # 保存用户信息
                token_result = {
                    "dfcf_token": {
                        "Data": {
                            "UID": user_data.get("UID"),
                            "CToken": user_data.get("CToken"),
                            "UToken": user_data.get("UToken"),
                            "Alias": user_data.get("Alias", "未知用户")
                        }
                    },
                    "em_gt": em_gt,
                    "info_service": info_service_result
                }
                
                # 保存用户信息到数据桶
                save_success = save_user_info(token_result, em_gt, device_id)
                return save_success
            elif return_code == "42" or "验证码" in error_msg or "图片验证" in error_msg:
                
                # 获取图片验证码
                vcode_result, em_pa_vcode_co = get_verify_code_image(account, device_id, em_gt)
                if not vcode_result:
                    sender.reply("❌ 获取图片验证码失败")
                    return False
                
                # 如果vcode_result是字符串且以http开头，说明是图片链接
                if isinstance(vcode_result, str) and vcode_result.startswith('http'):
                    sender.reply("验证码自动识别失败，请手动输入：")
                    sender.replyImage(vcode_result)
                    vcode_input = sender.listen(60000)
                    if not vcode_input or vcode_input == 'q':
                        sender.reply("✅ 已取消登录")
                        return False
                    vcode = vcode_input
                else:
                    # API识别成功，直接使用识别结果
                    vcode = vcode_result
                    sender.reply("验证码自动识别成功")
                
                # 再次尝试登录，带上验证码
                return account_login_with_verification(
                    account, password_md5, unique_id, device_id, em_gt,
                    vcode=vcode, vcode_context=em_pa_vcode_co
                )
            elif return_code == "39":
                # 需要短信验证码

                
                # 从返回数据中获取短信验证码上下文
                mobile_active_code_context = login_result.get("Data", {}).get("MobileActiveCodeContext")
                if not mobile_active_code_context:
                    mobile_active_code_context = login_result.get("Data", {}).get("ApiContext")
                
                if not mobile_active_code_context:
                    sender.reply("❌ 获取短信验证码上下文失败")
                    return False
                
                # 使用短信验证码登录
                return login_with_sms_code(account, password_md5, mobile_active_code_context, unique_id, device_id, em_gt)
            else:
                # 其他登录失败情况
                sender.reply(f"❌ 登录失败: {error_msg}")
                return False
        else:
            # 请求失败
            sender.reply(f"❌ 请求失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        sender.reply(f"❌ 登录过程出错: {str(e)}")
        return False

# 在account_login函数后添加登录处理函数
def process_login():
    """处理登录流程"""
    # 显示登录选项
    login_options = """
=====登录方式=====
[1] 扫码登录
[2] 账号密码登录
------------------
请选择登录方式
回复"q"退出"""
    
    sender.reply(login_options)
    option = sender.listen(60000)
    
    if not option or option == 'q':
        sender.reply("✅ 已取消登录")
        return False
        
    if option == "1":
        # 扫码登录
        return scan_login()
    elif option == "2":
        # 账号密码登录
        sender.reply("请输入账号（手机号）：")
        account = sender.listen(60000)
        
        if not account or account == 'q':
            sender.reply("✅ 已取消登录")
            return False
            
        sender.reply("请输入密码：")
        password = sender.listen(60000)
        
        if not password or password == 'q':
            sender.reply("✅ 已取消登录")
            return False
            
        return account_login(account, password)
    else:
        sender.reply("❌ 无效的选择")
        return False

# 获取图片验证码
def get_verify_code_image(account, device_id, em_gt):
    """获取图片验证码
    Args:
        account: 账号
        device_id: 设备ID
        em_gt: EM-GT值
    Returns:
        验证码图片临时文件路径和验证码cookie值
    """
    try:
        # 设备ID的base64编码
        em_md = base64.b64encode(device_id.encode()).decode()
        em_md_encoded = urllib.parse.quote(em_md)
        
        # 随机生成唯一标识
        unique_id = generate_unique_id()
        
        # 随机数作为rnd参数
        rnd = str(int(time.time() * 1000))
        
        # 构建请求URL
        url = f"https://vcode2.eastmoney.com/V2/verifycode2.ashx"
        params = {
            "rnd": rnd,
            "vcodeTarget": account
        }
        
        # 构建请求headers
        headers = {
            'EM-OS': 'Android',
            'EM-PKG': 'com.eastmoney.android.berlin',
            'EM-VER': '10.28.1',
            'EM-GT': em_gt,
            'EM-MD': em_md_encoded,
            'EM-CHL': 'xiaomi22_64',
            'EM-GV': '3f4605b67',
            'EM-CT': '',
            'EM-UT': '',
            'EM-SL': '0',
            'EM-PA': '1',
            'em-dns': '1',
            'EM-AB': 'R_1Lk|1Ls;test_1LG;',
            'Host': 'vcode2.eastmoney.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.12.13'
        }
        
        # 发送请求获取验证码图片
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            # 获取验证码cookie
            em_pa_vcode_co = None
            for cookie in response.cookies:
                if cookie.name == "EmPaVCodeCo":
                    em_pa_vcode_co = cookie.value
                    break
            
            # 如果没有从cookies中获取，尝试从headers中获取
            if not em_pa_vcode_co and 'Set-Cookie' in response.headers:
                cookie_header = response.headers.get('Set-Cookie', '')
                match = re.search(r'EmPaVCodeCo=([^;]+)', cookie_header)
                if match:
                    em_pa_vcode_co = match.group(1)
            
            # 如果仍未获取到cookie，使用默认值
            if not em_pa_vcode_co:
                em_pa_vcode_co = "EmPaVCodeCo"
            
            # 将图片转为base64编码
            image_base64 = base64.b64encode(response.content).decode('utf-8')
            
            # 获取验证码识别API配置
            _, _, _, _, _, captcha_api = get_config()
            
            # 尝试使用API识别验证码
            if captcha_api:
                try:
                    # 构建请求参数
                    data = {
                        "image": image_base64,
                        "probability": False,
                        "png_fix": False
                    }
                    
                    # 发送识别请求
                    api_response = requests.post(captcha_api, data=data)
                    
                    # 解析响应
                    result = api_response.json()
                    if result.get("code") == 200:
                        vcode = result.get("data")
                        if vcode:
                            return vcode, em_pa_vcode_co
                except Exception as e:
                    print(f"API识别验证码异常: {str(e)}")
            
            # API识别失败，使用uapis.cn获取图片链接
            try:
                upload_url = "https://uapis.cn/api/baseimg.php"
                upload_data = {
                    "imageData": image_base64
                }
                
                upload_response = requests.post(upload_url, data=upload_data)
                result = upload_response.json()
                
                if result.get("code") == 200 and result.get("img"):
                    return None, em_pa_vcode_co
            except Exception as e:
                print(f"上传图片获取链接异常: {str(e)}")
            
            # 如果都失败了，保存为临时文件
            temp_file = f"vcode_{unique_id}.jpg"
            with open(temp_file, "wb") as f:
                f.write(response.content)
            return temp_file, em_pa_vcode_co
            
        return None, None
    except Exception as e:
        print(f"获取验证码异常: {str(e)}")
        return None, None

# 使用短信验证码登录
def login_with_sms_code(account, password, api_context, unique_id, device_id, em_gt):
    """使用短信验证码完成登录流程
    Args:
        account: 账号
        password: MD5加密后的密码
        api_context: 短信验证码API上下文
        unique_id: 唯一ID
        device_id: 设备ID
        em_gt: EM-GT值
    Returns:
        登录结果
    """
    try:
        # 提示用户输入短信验证码
        sender.reply("请输入收到的短信验证码：")
        sms_code = sender.listen(180000)  # 等待3分钟
        
        if not sms_code or sms_code.lower() == 'q':
            sender.reply("✅ 已取消登录")
            return False
        
        # 设备ID的base64编码
        em_md = base64.b64encode(device_id.encode()).decode()
        
        # 构建请求URL和Headers
        url = "https://awebapi2-account.eastmoney.com/core/api/MPassport/LoginByActiveCodeV4"
        headers = {
            'Accept': 'application/json',
            'em-clt-uiid': unique_id,
            'em-clt-auth': '202107280688;qXU2bhqAdsux+eTFLOqWgXwz8GJyfhX/ejnm0eJ9aMc=',
            'qgqp-b-id': em_gt,
            'em_clt_uiid': unique_id,
            'qgqp_b_id': em_gt,
            'EM-OS': 'Android',
            'EM-PKG': 'com.eastmoney.android.berlin',
            'EM-VER': '10.28.1',
            'EM-GT': em_gt,
            'EM-MD': urllib.parse.quote(em_md),
            'EM-CHL': 'xiaomi22_64',
            'EM-GV': '3f4605b67',
            'EM-CT': '',
            'EM-UT': '',
            'EM-SL': '0',
            'EM-PA': '1',
            'em-dns': '1',
            'EM-AB': 'R_1Lk|1Ls;test_1LG;',
            'Content-Type': 'application/json',
            'Host': 'awebapi2-account.eastmoney.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.12.13'
        }
        
        # 构建请求体
        request_body = {
            "AppId": "202107280688",
            "UniqueId": unique_id,
            "ProductType": "DFCFT",
            "Version": "10.28.1",
            "DeviceType": "Android15",
            "DomainName": "EastMoneyApp",
            "DeviceModel": "2210132C",
            "DeviceAlias": "",
            "ScenarioId": "202003257918",
            "ActiveCode": sms_code,
            "MobileActiveCodeContext": api_context
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, json=request_body)
        
        # 检查响应状态
        if response.status_code == 200:
            # 解析响应
            login_result = response.json()
            
            # 检查登录是否成功
            if login_result.get("ReturnCode") == "0":
                # 获取用户信息
                user_data = login_result.get("Data", {})
                
                # 发送信息服务请求
                info_service_result = send_info_service_request(em_gt)
                
                # 保存用户信息
                token_result = {
                    "dfcf_token": {
                        "Data": {
                            "UID": user_data.get("UID"),
                            "CToken": user_data.get("CToken"),
                            "UToken": user_data.get("UToken"),
                            "Alias": user_data.get("Alias", "未知用户")
                        }
                    },
                    "em_gt": em_gt,
                    "info_service": info_service_result
                }
                
                # 保存用户信息到数据桶
                save_success = save_user_info(token_result, em_gt, device_id)
                return save_success
            else:
                # 登录失败
                error_msg = login_result.get("Msg", "未知错误")
                sender.reply(f"❌ 短信验证码登录失败: {error_msg}")
                return False
        else:
            # 请求失败
            sender.reply(f"❌ 请求失败: 状态码 {response.status_code}")
            return False
    except Exception as e:
        sender.reply(f"❌ 短信验证码登录过程出错: {str(e)}")
        return False
        
# 将account_login函数修改为支持验证码

def recognize_captcha(base64_image, api_url=None):
    """识别验证码
    Args:
        base64_image: base64编码的图片数据
        api_url: 验证码识别API地址
    Returns:
        识别结果或图片链接
    """
    try:
        # 先尝试使用配置的API识别
        if api_url:
            # 构建请求参数
            data = {
                "image": base64_image,
                "probability": False,
                "png_fix": False
            }
            
            # 发送识别请求
            response = requests.post(api_url, data=data)
            
            # 解析响应
            result = response.json()
            if result.get("code") == 200:
                return result.get("data")
        
        # API识别失败，使用uapis.cn获取图片链接
        upload_url = "https://uapis.cn/api/baseimg.php"
        upload_data = {
            "imageData": base64_image
        }
        
        response = requests.post(upload_url, data=upload_data)
        result = response.json()
        
        if result.get("code") == 200 and result.get("img"):
            return result.get("img")
        
        return None
    except Exception as e:
        print(f"识别验证码异常: {str(e)}")
        return None

def show_tutorial():
    """显示东方财富插件使用教程"""
    tutorial = """=====东方教程=====
📱 用户指令:
• 东方登录 - 绑定东方财富账号
• 东方查询 - 查询账号余额和状态
• 东方管理 - 授权/删除账号
• 东方教程 - 查看本教程
------------------
🔧 管理员指令:
• 东方授权 - 管理员按天数授权
• 东方检测 - 检测过期账号并清理
------------------
💡 登录方式:
📝 方式一: 微信扫码登录
📝 方式二: 账号密码登录
💡 登录后自动进入授权流程
------------------
📝 账号获取方式:
1. 下载东方财富APP注册账号
2. 使用手机号注册并设置密码
3. 完成实名认证
4. 进入活动页面一次激活账号
------------------
💰 功能说明:
• 账号绑定: 保存账号信息到系统
• 余额查询: 查看现金余额和明细
• 授权管理: 付费使用插件功能
• 青龙提交: 自动提交到青龙容器
• 过期检测: 自动清理过期账号
------------------
🎯 使用流程:
1. 发送"东方登录"绑定账号
2. 选择扫码或账号密码登录
3. 登录成功后选择授权方式
4. 完成支付获得使用权限
5. 系统自动提交到青龙容器
6. 等待定时任务自动执行
------------------
⚠️ 注意事项:
• 授权后才能使用签到功能
• 过期账号会被自动清理
• 支持微信支付和积分兑换
• 管理员可批量授权用户
• 每日收益约1.5元(需实名)
=================="""
    sender.reply(tutorial)

def main():
    # 获取用户输入的消息
    message = sender.getMessage()
    
    if "东方登录" in message or "登录东方" in message:
        process_login()
    elif "东方查询" in message:
        # 查询功能
        query_all_accounts()
    elif "东方管理" in message:
        # 管理功能
        manage_eastmoney()
    elif "东方授权" in message:
        # 授权功能
        if sender.isAdmin():
            # 管理员授权功能
            admin_auth_management()
    elif "东方提现" in message:
        sender.reply("东方财富提现功能待实现")
    elif "东方检测" in message:
        # 检测功能（仅管理员）
        if not sender.isAdmin():
            sender.reply("❌ 仅限管理员")
            return
        sender.reply("🔍 正在检测...")
        sender.reply(check_auth_status())
    elif "东方教程" in message:
        # 显示教程
        show_tutorial()
    elif sender.getImtype() == 'fake':
    # 定时任务 - 执行检测并清理过期账号
        try:
            middleware.notifyMasters(check_auth_status())
        except:
            pass

if __name__ == "__main__":
    main()
