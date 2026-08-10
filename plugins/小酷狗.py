#[public:true]
# [rule: ^(酷狗)(登录|登陆)$|^(酷狗)(查询)$|^(酷狗)(管理)$|^酷狗授权$|^酷狗清理$|^酷狗教程$]
# [disable:true]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [cron: 56 8,15 * * *]
# [admin: false]
# [title: 小酷狗]
# [open_source: false]
# [class: 工具类]
# [version: 2.0]
# [price: 15.88]
# [icon: https://img.3dmgame.com/uploads/images/thumbnews/20220914/1663143036_387843.jpg]
# [author: sky2022]
# [service: 2661320550]
# [description: 介绍：酷狗音乐代挂插件<br>指令：酷狗登录、查询、管理、授权、清理、教程<br>插件支持手机号登录，无需抓包！！！！<br>定时任务：每天8点和15点自动检测授权过期并推送通知<br>1.9更新：新增定时检测推送，每天8点/15点自动检测授权到期状态并通知用户<br>1.7更新：统一面板配置为面板类型+对接面板配置，并新增呆呆面板分组配置]

import re
from datetime import datetime, timedelta
from decimal import Decimal
import middleware
import requests
import json
import os
import time
import hashlib
import uuid
import base64
import urllib.parse
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

today_date = datetime.now().date()
today_time = str(today_date)

def ValueErrors(value, count):
    """验证输入值"""
    try:
        value = int(value)
        if value <= 0 or value > count:
            sender.reply(f"❌ 请输入1-{count}之间的数字")
            exit(0)
        return value
    except:
        sender.reply("❌ 请输入正确的数字")
        exit(0)

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
userid = sender.getUserID()
uservalue = middleware.bucketGet(bucket='dd_kg_user', key=userid) or ''

def normalize_panel_type(panel_type_value):
    """统一解析面板类型。"""
    value = str(panel_type_value or '').strip().lower()
    if value in ('呆呆', '呆呆面板', 'daidai', 'dd'):
        return 'daidai'
    if value in ('青龙', '青龙面板', 'qinglong', 'ql'):
        return 'qinglong'
    return ''

# [param: {"required":true,"key":"dd_kg.panel_type","bool":false,"placeholder":"青龙 或 呆呆","name":"对接面板类型","desc":"填写你当前使用的面板类型，支持：青龙、青龙面板、QL、呆呆、呆呆面板、Daidai"}]
# [param: {"required":true,"key":"dd_kg.panel_config","bool":false,"placeholder":"Host丨ClientID丨ClientSecret 或 Host丨AppKey丨AppSecret","name":"对接面板配置","desc":"统一填写面板对接参数。青龙：Host丨ClientID丨ClientSecret；呆呆：Host丨AppKey丨AppSecret；分隔符使用中文丨"}]
# [param: {"required":false,"key":"dd_kg.panel_group","bool":false,"placeholder":"例:酷狗","name":"对接面板分组","desc":"仅呆呆面板生效。填写后新增或更新变量时会同步写入 group 字段；留空则不处理分组"}]
# [param: {"required":true,"key":"dd_kg.var_name","bool":false,"placeholder":"必填项,例:kgck","name":"面板变量名","desc":"提交到面板中的酷狗变量名"}]
# [param: {"required":true,"key":"dd_kg.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# [param: {"required":true,"key":"dd_kg.kgVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# [param: {"required":true,"key":"dd_kg.kgcoin","bool":false,"placeholder":"不填为关闭积分支付","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
# [param: {"required":false,"key":"dd_kg.use_ma_pay","bool":true,"placeholder":"","name":"使用码支付","desc":"是否使用码支付系统,开启后将使用卡密系统配置的码支付"}]

# 和主程序相同的盐值
salt = 'OIlwieks28dk2k092lksi2UIkp'
salt2 = "t6us8yan^mEtWj7P"

# 请求头
info_headers = {"KG-THash": "1509162", "Accept-Encoding": "gzip, deflate", "x-router": "loginservice.kugou.com",
           "User-Agent": "Android9-AndroidPhone-12149-201-0-SendMobileCodeProtocolV7-wifi", "KG-RC": "1",
           "KG-FAKE": "0", "KG-RF": "0078a6ee", "Content-Type": "application/json; charset=utf-8",
           "Connection": "close"}

info2_headers = {"Connection": "close",
                "User-Agent": "Mozilla/5.0 (Linux; Android 9;Build/PQ3B.190801.12281726; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36 KugouBrowser GDTTangramMobSDK/8.620.3421 GDTMobSDK/8.620.3421",
                "Accept": "*/*", "Origin": "https://h5pkg.kugou.com", "X-Requested-With": "com.kugou.android",
                "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty",
                "Referer": "https://h5pkg.kugou.com/", "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7"}

# 账号信息类
class Account:
    def __init__(self, userid, token):
        self.userid = userid
        self.token = token

def aes_encrypt(plaintext, key, iv):
    """AES加密 - 输出hex格式"""
    try:
        key_bytes = key.encode('utf-8')
        iv_bytes = iv.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        padded_data = pad(plaintext.encode('utf-8'), AES.block_size, style='pkcs7')
        encrypted = cipher.encrypt(padded_data)
        return encrypted.hex()
    except Exception as e:
        print(f"AES加密失败: {str(e)}")
        return None

def aes_decrypt(ciphertext, key, iv):
    """AES解密 - 输入hex格式"""
    try:
        key_bytes = key.encode('utf-8')
        iv_bytes = iv.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv_bytes)
        encrypted_data = bytes.fromhex(ciphertext)
        decrypted = cipher.decrypt(encrypted_data)
        unpadded_data = unpad(decrypted, AES.block_size, style='pkcs7')
        return unpadded_data.decode('utf-8')
    except Exception as e:
        print(f"AES解密失败: {str(e)}")
        return None

def md5_encrypt(text):
    """MD5加密 - 输出小写"""
    try:
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    except Exception as e:
        print(f"MD5加密失败: {str(e)}")
        return None

def generate_qrcode(url):
    """将支付链接转为二维码图片URL"""
    try:
        encoded_url = urllib.parse.quote(url, safe='')
        return f"https://api.qrtool.cn/?text={encoded_url}"
    except Exception as e:
        print(f"生成二维码失败: {str(e)}")
        return None

def send_qrcode_image(pay_sender, qrcode_url, pay_type):
    """发送二维码图片给用户扫码支付"""
    pay_type_names = {'alipay': '支付宝', 'wxpay': '微信', 'qqpay': 'QQ钱包'}
    pay_type_name = pay_type_names.get(pay_type, pay_type)
    try:
        pay_sender.replyImage(qrcode_url)
        if pay_type == 'qqpay':
            pay_sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\nQQ支付打开图片若是黑屏，长按屏幕进行\"识别二维码\"即可！\n支付过程中输入'q'可取消支付")
        else:
            pay_sender.reply(f"请使用【{pay_type_name}】扫描上方二维码完成支付\n支付过程中输入'q'可取消支付")
    except:
        if pay_type == 'qqpay':
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\nQQ支付打开图片若是黑屏，长按屏幕进行"识别二维码"即可！\n[CQ:image,file={qrcode_url}]'
        else:
            pay_msg = f'请使用【{pay_type_name}】扫描下方二维码完成支付，支付过程中输入"q"可取消支付:\n[CQ:image,file={qrcode_url}]'
        pay_sender.reply(pay_msg)

def get_config():
    """获取配置信息"""
    panel_type = normalize_panel_type(middleware.bucketGet('dd_kg', 'panel_type') or '')
    if not panel_type:
        sender.reply("对接面板类型填写无效，请填写：青龙/青龙面板/QL 或 呆呆/呆呆面板/Daidai")
        exit(0)

    panel_config = (middleware.bucketGet('dd_kg', 'panel_config') or '').strip()
    var_name = middleware.bucketGet('dd_kg', 'var_name') or 'kgck'
    zsm = middleware.bucketGet('dd_kg', 'zsm') or ''
    kgVipmoney = middleware.bucketGet('dd_kg', 'kgVipmoney') or '0'
    kgcoin = middleware.bucketGet('dd_kg', 'kgcoin') or '0'
    use_ma_pay = middleware.bucketGet('dd_kg', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    panel_group = (middleware.bucketGet('dd_kg', 'panel_group') or '').strip()
    return panel_type, panel_config, var_name, zsm, kgVipmoney, kgcoin, use_ma_pay, panel_group

def get_panel_settings():
    """获取面板配置。"""
    panel_type, panel_config, var_name, _, _, _, _, panel_group = get_config()
    return panel_type, panel_config, var_name, panel_group

def get_payment_config():
    """获取支付配置"""
    zsm = middleware.bucketGet('dd_kg', 'zsm')
    use_ma_pay = middleware.bucketGet('dd_kg', 'use_ma_pay') or 'false'
    use_ma_pay = use_ma_pay.lower() == 'true'
    
    if use_ma_pay:
        # 从卡密系统获取码支付配置
        ma_pay_config = {
            'switch': middleware.bucketGet('dd_sign_config', 'ma_pay_switch') or 'false',
            'gateway': middleware.bucketGet('dd_sign_config', 'ma_pay_gateway'),
            'pid': middleware.bucketGet('dd_sign_config', 'ma_pay_pid'),
            'key': middleware.bucketGet('dd_sign_config', 'ma_pay_key'),
            'type': middleware.bucketGet('dd_sign_config', 'ma_pay_type') or 'alipay,wxpay,qqpay',
            'notify_url': middleware.bucketGet('dd_sign_config', 'ma_pay_notify_url'),
            'return_url': middleware.bucketGet('dd_sign_config', 'ma_pay_return_url')
        }
        
        if ma_pay_config['switch'].lower() != 'true' or not all([ma_pay_config['gateway'], ma_pay_config['pid'], ma_pay_config['key']]):
            ma_pay_config = None
    else:
        ma_pay_config = None
    
    return zsm, use_ma_pay, ma_pay_config

def empower(empowertime, me_as_int):
    """授权时间计算"""
    day = me_as_int * 30
    if len(empowertime) == 0 or empowertime <= str(today_time):
        delayed_date = today_date + timedelta(days=day)
    elif empowertime > today_time:
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        delayed_date = delayed_date.date()
    else:
        sender.reply('出错！')
        exit(0)
    return str(delayed_date)

def zf(project, me_as_int, accountVip, token, phone, account):
    """支付处理函数"""
    try:
        # 检查是否免费
        money = Decimal(me_as_int) * Decimal(kgVipmoney)
        if money == 0:
            # 免费授权，直接处理
            accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
            middleware.bucketSet('dd_kg_auth', account, accountVip)
            
            sender.reply(f"""
=====免费授权成功=====
🎫 商品: {project}
💰 金额: 免费
⏰ 授权时长: {me_as_int}月
==================""")
            return True
        
        # 获取支付配置
        zsm, use_ma_pay, ma_pay_config = get_payment_config()
        
        points_enabled = kgcoin and kgcoin != '' and int(kgcoin) > 0
        if use_ma_pay and not ma_pay_config and not points_enabled:
            sender.reply('❌ 码支付已开启，但码支付配置不完整，请联系管理员检查卡密系统配置!')
            exit(0)
        if not use_ma_pay and not zsm and not points_enabled:
            sender.reply('❌ 未配置收款方式,请联系管理员!')
            exit(0)
            
        # 检查是否允许使用积分支付
        usercoin = middleware.bucketGet('dd_sign_points', userid) or '0'
        zfcoin = int(kgcoin) * me_as_int if kgcoin else 0
        
        # 构建支付选择菜单
        pay_menu = "=====选择支付方式====="
        option_num = 1
        options_map = {}

        # 添加微信支付选项
        if zsm and not use_ma_pay:
            pay_menu += f"\n{option_num}️⃣ 微信支付\n   💰 {money}元/{me_as_int}月"
            options_map[str(option_num)] = 'wechat'
            option_num += 1
            
        # 添加码支付选项
        if use_ma_pay and ma_pay_config:
            pay_menu += f"\n{option_num}️⃣ 码支付\n   💰 {money}元/{me_as_int}月"
            options_map[str(option_num)] = 'ma'
            option_num += 1
            
        # 只有当kgcoin > 0且不等于空字符串时才显示积分支付选项
        if kgcoin and kgcoin != '' and int(kgcoin) > 0:
            pay_menu += f"\n{option_num}️⃣ 积分支付\n   🎯 {zfcoin}积分/{me_as_int}月\n   💫 当前积分: {usercoin}"
            options_map[str(option_num)] = 'points'
            
        pay_menu += "\n------------------\n回复数字选择方式\n回复'q'退出操作\n=================="

        sender.reply(pay_menu)
        choice = sender.input(60000, 1, False)
        
        if choice == 'q' or choice == 'Q':
            sender.reply("✅ 已取消支付")
            exit(0)
            
        selected_pay = options_map.get(choice)
        if selected_pay == 'wechat' and zsm and not use_ma_pay:
            # 微信支付流程
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
                sender.reply('✅ 已取消支付')
                exit(0)
                
            try:
                Money, Time, From = parse_payment_result(ddzf)
                    
                if float(Money) >= float(money):
                    accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                    middleware.bucketSet('dd_kg_auth', account, accountVip)
                    
                    result_msg = f"""
=====支付成功=====
🎫 商品: {project}
💰 金额: {Money}元
⏰ 时间: {Time}
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
                    exit(0)
            except Exception as e:
                sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
                exit(0)
                
        elif selected_pay == 'ma' and use_ma_pay and ma_pay_config:
            # 码支付流程
            
            # 生成订单号
            out_trade_no = f"KG{int(time.time())}{userid}"
            
            # 构造支付参数
            params = {
                'pid': ma_pay_config['pid'],
                'type': ma_pay_config['type'].split(',')[0],  # 默认使用第一个支付方式
                'out_trade_no': out_trade_no,
                'name': f"{senderID}-酷狗授权-{str(money)}",
                'money': str(money),
                'param': userid  # 传递用户ID作为附加参数
            }
            
            # 添加回调地址（如果配置了）
            if ma_pay_config.get('notify_url'):
                params['notify_url'] = ma_pay_config['notify_url']
            if ma_pay_config.get('return_url'):
                params['return_url'] = ma_pay_config['return_url']
            
            # 移除空值
            params = {k: v for k, v in params.items() if v}
            
            # 按照ASCII码排序参数
            sorted_params = sorted(params.items(), key=lambda x: x[0])
            
            # 拼接成URL键值对格式
            sign_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            
            # 添加密钥进行MD5签名
            sign = hashlib.md5((sign_str + ma_pay_config['key']).encode()).hexdigest().lower()
            
            # 添加签名到参数
            params['sign'] = sign
            params['sign_type'] = 'MD5'
            
            # 发送支付请求
            gateway = ma_pay_config['gateway']
            if not gateway.endswith('/'):
                gateway += '/'
            submit_url = gateway + 'mapi.php'
            
            try:
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                response = requests.post(submit_url, data=params, headers=headers, timeout=10)
                
                if response.status_code != 200:
                    sender.reply(f"❌ 创建支付订单失败，HTTP状态码: {response.status_code}")
                    exit(0)
                
                # 解析响应
                try:
                    result = response.json()
                except:
                    sender.reply("❌ 创建支付订单失败，返回数据格式错误")
                    exit(0)
                
                # 判断返回结果
                code = result.get('code', 0)
                msg = result.get('msg', '未知状态')
                
                if code == 1:  # 码支付API返回的成功状态码是1
                    # 获取支付URL
                    pay_url = result.get('payurl', '')
                    if not pay_url:
                        sender.reply("❌ 获取支付链接失败")
                        exit(0)

                    qrcode_url = generate_qrcode(pay_url)
                    pay_type = ma_pay_config['type'].split(',')[0] if ma_pay_config.get('type') else 'alipay'
                    if qrcode_url:
                        send_qrcode_image(sender, qrcode_url, pay_type)
                    else:
                        sender.reply(f"""
=====码支付=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 有效期: 5分钟
------------------
二维码生成失败，请点击链接完成支付:
{pay_url}
==================""")
                    
                    # 轮询订单状态
                    for _ in range(60):  # 最多等待5分钟
                        # 等待用户输入或超时
                        result = sender.listen(5000)  # 等待5秒
                        if result == 'q':
                            sender.reply("❌ 用户取消支付")
                            exit(0)
                        
                        # 使用正确的查询API路径
                        check_url = gateway
                        if check_url.endswith('/'):
                            check_url = check_url[:-1]
                        # 根据文档，查询接口路径应该是 /xpay/epay/api.php
                        if '/xpay/epay/api.php' not in check_url:
                            check_url = f"{check_url}/xpay/epay/api.php"
                        
                        check_params = {
                            'act': 'order',
                            'pid': ma_pay_config['pid'],
                            'key': ma_pay_config['key'],
                            'out_trade_no': out_trade_no
                        }
                        
                        try:
                            check_resp = requests.get(check_url, params=check_params)
                            check_result = check_resp.json()
                            
                            # 根据文档，成功状态码是1，订单状态status=1表示支付成功
                            if check_result.get('code') == 1 and check_result.get('status') == 1:  # 支付成功
                                accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                                middleware.bucketSet('dd_kg_auth', account, accountVip)
                                
                                sender.reply(f"""
=====支付成功=====
🎫 商品: {project}
💰 金额: {money}元
⏰ 授权时长: {me_as_int}月
==================""")
                                return True
                        except:
                            continue
                            
                    sender.reply("❌ 支付超时,请重新发起支付!")
                    exit(0)
                else:
                    # 检查是否是没有可用支付账号的错误，如果是则提示用户使用微信支付
                    if "没有找到可用支付账号" in msg or "没有找到可用的" in msg:
                        sender.reply(f"❌ 码支付暂不可用({msg})")
                        sender.reply("💡 请尝试使用微信支付方式")
                    else:
                        sender.reply(f"❌ 创建支付订单失败: {msg}")
                    exit(0)
            except Exception as e:
                sender.reply(f"❌ 支付请求失败: {str(e)}")
                exit(0)
                
        elif selected_pay == 'points' and kgcoin != '' and kgcoin is not None and int(kgcoin) > 0:
            # 积分支付流程
            if int(usercoin) < zfcoin:
                sender.reply(f"""
=====积分不足=====
👤 当前积分: {usercoin}
📍 需要积分: {zfcoin}
==================""")
                exit(0)
                
            confirm_msg = f"💫 积分支付确认\n💰 消耗积分: {zfcoin}\n⏰ 授权时长: {me_as_int}月\n------------------\n确认请回复【y】\n取消请回复【n】"
            sender.reply(confirm_msg)
            
            if yesornos():
                try:
                    new_balance = int(usercoin) - zfcoin
                    middleware.bucketSet('dd_sign_points', userid, str(new_balance))
                    accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                    middleware.bucketSet('dd_kg_auth', account, accountVip)
                    
                    result_msg = f"✅ 支付成功\n💫 扣除积分: {zfcoin}\n💰 剩余积分: {new_balance}\n⏰ 授权时长: {me_as_int}月"
                    sender.reply(result_msg)
                    return True
                except Exception as e:
                    sender.reply(f"❌ 积分处理失败: {str(e)}")
                    exit(0)
            else:
                sender.reply("✅ 已取消支付")
                exit(0)
        else:
            sender.reply("❌ 请输入正确的选项")
            exit(0)
            
    except Exception as e:
        sender.reply(f"❌ 支付处理异常: {str(e)}")
        exit(0)

def parse_payment_result(ddzf):
    """解析支付结果"""
    try:
        if isinstance(ddzf, dict):
            # 新版微信赞赏消息格式
            if ddzf.get('Type') == '微信赞赏':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            # 新版微信收款消息格式  
            elif ddzf.get('Type') == '微信收款':
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
            # 旧版BORW格式
            elif ddzf.get('Money'):
                return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
            # 旧版GW格式
            elif ddzf.get('money'):
                return float(ddzf.get('money', 0)), ddzf.get('time', '').replace('T', ' ').split('.')[0], ddzf.get('fromName', '')
            else:
                sender.reply("❌ 不支持的支付消息格式")
                exit(0)
        else:
            # 尝试解析JSON字符串
            try:
                ddzf = json.loads(ddzf)
                if ddzf.get('Type') == '微信赞赏':
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
                elif ddzf.get('Type') == '微信收款':
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').split('.')[0].replace('T', ' '), ddzf.get('FromName', '')
                else:
                    return float(ddzf.get('Money', 0)), ddzf.get('Time', '').replace('T', ' ').split('.')[0], ddzf.get('FromName', '')
            except:
                if "二维码赞赏到账" in str(ddzf):
                    try:
                        amount = str(ddzf).split("收款金额￥")[1].split("\n")[0]
                        time_str = str(ddzf).split("到账时间")[1].split("\n")[0]
                        return float(amount), time_str.strip(), ''
                    except Exception as e:
                        sender.reply(f"❌ 解析收款信息失败: {str(e)}")
                        exit(0)
                else:
                    sender.reply("❌ 无法解析支付结果")
                    exit(0)
    except Exception as e:
        sender.reply(f"❌ 处理支付结果时出错: {str(e)}")
        exit(0)

def yesornos():
    """确认选择处理"""
    yesorno = sender.input(120000, 1, False)
    if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
        return True
    elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
        return False
    elif yesorno == '':
        sender.reply('输入超时！')
        exit(0)
    elif yesorno == 'q' or yesorno == 'Q' or yesorno == '退出':
        sender.reply('退出!')
        exit(0)
    else:
        sender.reply('输入错误！')
        exit(0)

def kg_auth():
    """酷狗授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 您没有权限执行此操作!")
        exit(0)
        
    auth_menu = """
=====酷狗授权管理=====
[1] 一键授权所有用户
[2] 单独授权用户
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
        users = middleware.bucketAllKeys('dd_kg_user')
        if not users:
            sender.reply("❌ 未找到任何绑定的酷狗账号")
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
            sjts = int(sjts)  # 确保转换为整数
        except:
            sender.reply("❌ 天数必须是数字!")
            return
            
        success_count = 0
        fail_count = 0
        
        for user in users:
            accountlist = middleware.bucketGet('dd_kg_user', user)
            if accountlist == '' or accountlist == '{}':
                continue
                
            accounts = eval(accountlist)
            for account in accounts:
                try:
                    dqsj = datetime.now().strftime("%Y-%m-%d")
                    accountVip = middleware.bucketGet('dd_kg_auth', account) or ''
                    account_str = middleware.bucketGet('dd_kg_info', f"{user}_{account}")
                    
                    if not account_str:
                        fail_count += 1
                        continue
                        
                    if len(accountVip) != 0 and accountVip > dqsj:
                        sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                        new_sqsj = sqsj + timedelta(days=int(sjts))
                    else:
                        new_sqsj = datetime.now() + timedelta(days=int(sjts))
                    new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                    
                    # 更新授权时间
                    middleware.bucketSet('dd_kg_auth', account, new_sqsj)
                    
                    # 更新青龙变量
                    ql_url, token = connect_qinglong()
                    if ql_url and token:
                        # 使用完整的account_str更新青龙变量
                        update_env(ql_url, token, account_str, account, account)
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
        
        # 发送管理员通知
        notify = middleware.bucketGet('bd_tptconfig', 'notify')
        if notify:
            tsqd = notify.split(',')
            middleware.notifyMasters(result_msg, tsqd)
            
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
            
        accountlist = middleware.bucketGet('dd_kg_user', myuid)
        if accountlist == '' or accountlist == '{}':
            sender.reply(f"❌ 未找到 {myuid} 的酷狗账号信息!")
            return
            
        accounts = eval(accountlist)
        account_list = """
=======账号列表=====
[0] 授权所有账号
------------------"""
        
        for i, account in enumerate(accounts, 1):
            accountVip = middleware.bucketGet('dd_kg_auth', account) or ''
            vip_status = accountVip if accountVip else '未授权'
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
            
        auth_guide = """
=====设置授权天数=====
请输入要授权的天数
------------------
回复数字设置天数
回复"q"退出操作
=================="""

        if xz == '0':
            # 授权该用户的所有账号
            sender.reply(auth_guide)
            sjts = sender.listen(60000)
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                sjts = int(sjts)  # 确保转换为整数
                success_count = 0
                for account in accounts:
                    try:
                        dqsj = datetime.now().strftime("%Y-%m-%d")
                        accountVip = middleware.bucketGet('dd_kg_auth', account) or ''
                        account_str = middleware.bucketGet('dd_kg_info', f"{myuid}_{account}")
                        
                        if not account_str:
                            continue
                            
                        if len(accountVip) != 0 and accountVip > dqsj:
                            sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                            new_sqsj = sqsj + timedelta(days=int(sjts))
                        else:
                            new_sqsj = datetime.now() + timedelta(days=int(sjts))
                        new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                        
                        # 更新授权时间
                        middleware.bucketSet('dd_kg_auth', account, new_sqsj)
                        
                        # 更新青龙变量
                        ql_url, token = connect_qinglong()
                        if ql_url and token:
                            update_env(ql_url, token, account_str, account, account)
                        success_count += 1
                    except:
                        continue
                        
                result_msg = f"""
=====授权操作完成=====
📱 账号: {mask_phone(account)}
⏰ 授权天数: {sjts} 天
📅 到期时间: {new_sqsj}
=================="""
                sender.reply(result_msg)
                
            except ValueError:
                sender.reply("❌ 天数必须是数字!")
                return
                
        elif 1 <= int(xz) <= len(accounts):
            # 授权单个账号
            account = accounts[int(xz)-1]
            sender.reply(auth_guide)
            sjts = sender.listen(60000)
            
            if sjts == 'q' or sjts == 'Q':
                sender.reply("✅ 已取消授权")
                return
            elif sjts is None:
                sender.reply("⏰ 操作超时,已退出")
                return
                
            try:
                sjts = int(sjts)  # 确保转换为整数
                dqsj = datetime.now().strftime("%Y-%m-%d")
                accountVip = middleware.bucketGet('dd_kg_auth', account) or ''
                account_str = middleware.bucketGet('dd_kg_info', f"{myuid}_{account}")
                
                if not account_str:
                    sender.reply("未找到账号信息!")
                    return
                    
                if len(accountVip) != 0 and accountVip > dqsj:
                    sqsj = datetime.strptime(accountVip, "%Y-%m-%d")
                    new_sqsj = sqsj + timedelta(days=int(sjts))
                else:
                    new_sqsj = datetime.now() + timedelta(days=int(sjts))
                new_sqsj = new_sqsj.strftime("%Y-%m-%d")
                
                # 更新授权时间
                middleware.bucketSet('dd_kg_auth', account, new_sqsj)
                
                # 更新青龙变量
                ql_url, token = connect_qinglong()
                if ql_url and token:
                    update_env(ql_url, token, account_str, account, account)
                
                msg = f"""
=====授权成功=====
📱 账号: {mask_phone(account)}
⏰ 授权天数: {sjts}天
📅 到期时间: {new_sqsj}
=================="""
                sender.reply(msg)
                
            except ValueError:
                sender.reply('❌ 输入的天数无效!')
                return
        else:
            sender.reply("❌ 输入的序号无效!")
            return

def clean_expired_accounts():
    """清理过期的酷狗账号"""
    if not sender.isAdmin():
        sender.reply("""
=====权限不足=====
❌ 您没有权限执行此操作
==================""")
        exit(0)
        
    users = middleware.bucketAllKeys(bucket='dd_kg_user')
    
    if not users:
        sender.reply("""
=====清理结果=====
❌ 未找到任何绑定账号
==================""")
        exit(0)
        
    sender.reply(f"""
=====开始清理=====
📊 共找到: {len(users)}个用户
⏳ 清理中请稍候...
==================""")
    
    cleaned_count = 0
    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_kg_user', key=f'{user}')
            if not accountlist:
                continue
                
            # 解析并去重账号列表
            accounts = eval(accountlist)
            if isinstance(accounts, (list, tuple, set)):
                accounts = list(dict.fromkeys(accounts))
            else:
                accounts = [str(accounts)]
                
            valid_accounts = []
            
            for account in accounts:
                accountVip = middleware.bucketGet(bucket='dd_kg_auth', key=account) or ''
                
                if len(accountVip) == 0 or accountVip <= today_time:
                    try:
                        ql_url, token = connect_qinglong()
                        if ql_url and token:
                            delete_env_by_account(ql_url, token, account)
                    except:
                        pass
                        
                    middleware.bucketDel(bucket='dd_kg_info', key=f"{user}_{account}")
                    middleware.bucketDel(bucket='dd_kg_auth', key=account)
                    cleaned_count += 1
                else:
                    valid_accounts.append(account)
            
            # 去重有效账号
            valid_accounts = list(dict.fromkeys(valid_accounts))
            
            if valid_accounts:
                middleware.bucketSet(bucket='dd_kg_user', key=user, value=str(valid_accounts))
            else:
                middleware.bucketDel(bucket='dd_kg_user', key=user)
                
        except Exception as e:
            print(f"处理用户 {user} 时出错: {str(e)}")
            continue
    
    sender.reply(f"""
=====清理完成=====
✅ 已清理: {cleaned_count}个账号
==================""")


def connect_qinglong():
    """连接面板"""
    panel_type, panel_config, _, _ = get_panel_settings()
    if not panel_config:
        if panel_type == 'qinglong':
            sender.reply("❌ 未配置青龙面板信息，请填写：对接面板类型=青龙，对接面板配置=Host丨ClientID丨ClientSecret")
        else:
            sender.reply("❌ 未配置呆呆面板信息，请填写：对接面板类型=呆呆，对接面板配置=Host丨AppKey丨AppSecret")
        return None, None
        
    try:
        ql_parts = panel_config.split('丨')
        if len(ql_parts) != 3:
            if panel_type == 'qinglong':
                sender.reply("❌ 青龙面板配置格式错误，正确格式: Host丨ClientID丨ClientSecret")
            else:
                sender.reply("❌ 呆呆面板配置格式错误，正确格式: Host丨AppKey丨AppSecret")
            return None, None
            
        ql_url = ql_parts[0].strip()
        client_id = ql_parts[1].strip()
        client_secret = ql_parts[2].strip()
        
        if panel_type == 'qinglong':
            token_url = f'{ql_url}/open/auth/token?client_id={client_id}&client_secret={client_secret}'
            response = requests.get(token_url)
            result = response.json()
            
            if result.get('code') != 200:
                sender.reply("❌ 获取青龙token失败")
                return None, None
            token = result['data']['token']
        else:
            response = requests.post(f'{ql_url}/api/open-api/token', json={"app_key": client_id, "app_secret": client_secret})
            result = response.json()
            token = result.get('data', {}).get('access_token')
            if response.status_code != 200 or not token:
                sender.reply("❌ 获取呆呆面板token失败")
                return None, None
            
        return ql_url, token
        
    except Exception as e:
        sender.reply(f"❌ 连接{'青龙' if panel_type == 'qinglong' else '呆呆'}面板失败: {str(e)}")
        return None, None

def update_env(ql_url, token, value, account, remark):
    """更新面板环境变量"""
    try:
        panel_type, _, var_name, panel_group = get_panel_settings()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        if panel_type == 'qinglong':
            query_url = f"{ql_url}/open/envs"
            response = requests.get(query_url, headers=headers)
            if response.status_code != 200:
                return False
            envs = response.json()['data']
        else:
            query_url = f"{ql_url}/api/envs"
            response = requests.get(query_url, headers=headers, params={"keyword": str(account), "page_size": 100})
            if response.status_code != 200:
                return False
            envs = response.json().get('data', [])
        env_id = None
        remark_pattern = f"酷狗:{account}丨"
        
        # 获取授权到期时间
        accountVip = middleware.bucketGet('dd_kg_auth', account) or '未授权'
        
        # 查找是否存在该备注的变量
        for env in envs:
            if env['name'] == var_name and env.get('remarks', '').startswith(remark_pattern):
                env_id = env['id']
                break
                
        if env_id:
            if panel_type == 'qinglong':
                update_url = f"{ql_url}/open/envs"
                data = {
                    "name": var_name,
                    "value": value,
                    "id": env_id,
                    "remarks": f"酷狗:{account}丨授权至:{accountVip}"
                }
                response = requests.put(update_url, headers=headers, json=data)
            else:
                update_url = f"{ql_url}/api/envs/{env_id}"
                data = {
                    "name": var_name,
                    "value": value,
                    "remarks": f"酷狗:{account}丨授权至:{accountVip}"
                }
                if panel_group:
                    data["group"] = panel_group
                response = requests.put(update_url, headers=headers, json=data)
        else:
            if panel_type == 'qinglong':
                add_url = f"{ql_url}/open/envs"
                data = [{
                    "name": var_name,
                    "value": value,
                    "remarks": f"酷狗:{account}丨授权至:{accountVip}"
                }]
                response = requests.post(add_url, headers=headers, json=data)
            else:
                add_url = f"{ql_url}/api/envs"
                data = {
                    "name": var_name,
                    "value": value,
                    "remarks": f"酷狗:{account}丨授权至:{accountVip}"
                }
                if panel_group:
                    data["group"] = panel_group
                response = requests.post(add_url, headers=headers, json=data)
            
        return response.status_code in (200, 201)
        
    except Exception as e:
        print(f"更新环境变量失败: {str(e)}")
        return False

def delete_env_by_account(ql_url, token, account):
    """按账号删除面板环境变量。"""
    try:
        panel_type, _, var_name, _ = get_panel_settings()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        remark_pattern = f"酷狗:{account}丨"

        if panel_type == 'qinglong':
            query_url = f"{ql_url}/open/envs"
            response = requests.get(query_url, headers=headers)
            if response.status_code != 200:
                return False
            envs = response.json()['data']
            for env in envs:
                if env['name'] == var_name and env.get('remarks', '').startswith(remark_pattern):
                    delete_url = f"{ql_url}/open/envs"
                    requests.delete(delete_url, headers=headers, json=[env['id']])
                    break
        else:
            query_url = f"{ql_url}/api/envs"
            response = requests.get(query_url, headers=headers, params={"keyword": str(account), "page_size": 100})
            if response.status_code != 200:
                return False
            envs = response.json().get('data', [])
            for env in envs:
                if env.get('name') == var_name and env.get('remarks', '').startswith(remark_pattern):
                    requests.delete(f"{ql_url}/api/envs/{env['id']}", headers=headers)
                    break
        return True
    except Exception as e:
        print(f"删除环境变量失败: {str(e)}")
        return False

def send_code(mobile):
    """发送验证码"""
    if len(mobile) != 11:
        sender.reply("❌ 请输入正确的手机号码")
        return False
        
    try:
        param1 = "dfid=-"
        param2 = "appid=1005"
        param3 = "mid=30767145192326147088652695110646018138"
        param4 = "clientver=12149"
        param5 = f"clienttime={str(int(time.time()))}"
        param6 = "uuid=-"
        bodyparamsstr = '{"mobile":"' + mobile + '"}'
        
        # 使用本地AES加密
        key = "795808cbe5da3c6b3b85b09541e60059"
        iv = "3b85b09541e60059"
        params = aes_encrypt(bodyparamsstr, key, iv)
        
        if not params:
            sender.reply("❌ AES加密失败")
            return False
        
        body_mobile = mobile[:3] + '*' * 5 + mobile[-3:]
        body_json = {
            "plat": "1",
            "businessid": 5,
            "clienttime_ms": 1705903784,
            "pk": "03AC4F6D2852BD7D0BE3A198C666647A0BFDFB5C51EF2FFB53E7427A99A972BAB41075404A37FBC1F23542A984114C51EF60FAA3640018A8C271507722F1E8FF4AE50D9D2BF40AE6FB2FA0D3B303552BBFD33E2224D2A40D8A01CF464E30F05230E38A1A12CD371C2690EB37965FC0585FB735F02E333729C27BFD5C417973A6",
            "mobile": body_mobile,
            "params": params
        }
        
        variables = [param1, param2, param3, param4, param5, param6]
        sorted_variables = sorted(variables)
        signstr = '' + salt
        for param in sorted_variables:
            signstr = signstr + param
        signstr = signstr + (json.dumps(body_json)) + salt
        
        # 使用本地MD5加密
        signature = md5_encrypt(signstr.replace(" ", ""))
        
        if not signature:
            sender.reply("❌ MD5签名生成失败")
            return False
        
        url = "https://gateway.kugou.com:443/v8/send_mobile_code/?" + param1 + "&signature=" + signature + "&" + param2 + "&" + param3 + "&" + param4 + "&" + param5 + "&" + param6
        
        try:
            response = requests.post(url, headers=info_headers, data=(json.dumps(body_json)).replace(" ", ""), timeout=10)
            response.raise_for_status()  # 检查HTTP状态码
            
            try:
                rejson = response.json()
            except json.JSONDecodeError:
                sender.reply("❌ 服务器返回数据解析失败")
                return False
                
            if rejson.get('status') == 1:
                sender.reply("✅ 验证码发送成功")
                return True
            else:
                error_msg = rejson.get('error_msg') or '未知错误'
                sender.reply(f"❌ 验证码发送失败: {error_msg}")
                return False
        except requests.exceptions.RequestException as e:
            sender.reply(f"❌ 网络请求失败: {str(e)}")
            return False
        except Exception as e:
            sender.reply(f"❌ 发送验证码失败: {str(e)}")
            return False
            
    except Exception as e:
        sender.reply(f"❌ 发送验证码异常: {str(e)}")
        return False

def login_by_code(mobile, code):
    """使用验证码登录"""
    if len(mobile) != 11:
        sender.reply("❌ 请输入正确的手机号码")
        return None
        
    key = '0756785487a71b02a3c5df3dca995c35'
    iv = 'a3c5df3dca995c35'
    
    # 使用本地AES加密
    params = aes_encrypt('{"mobile":"' + mobile + '","code":"' + code + '"}', key, iv)
    
    if not params:
        sender.reply("❌ AES加密失败")
        return None
        
    param1 = "dfid=-"
    param2 = "appid=1005"
    param3 = "mid=30767145192326147088652695110646018138"
    param4 = "clientver=12149"
    param5 = "clienttime=1705903808"
    param6 = "uuid=-"
    body_mobile = mobile[:3] + '*' * 5 + mobile[-3:]
    body_json = {
        "mobile": body_mobile,
        "params": params,
        "clienttime_ms": "1705903808203",
        "dfid": "-",
        "dev": "vivo PD1728",
        "plat": 1,
        "pk": "A046B448DB409D5E521A7892FC6CBAF8C5563927BC3E84F4DBE76F98AC4EACD977FE760FAF798E345FE08C88FD5E996293496616C416CABBAB64E314940074FD501372B8B24F20115E139BC65F73A57A60451501AED0FB7390CE090B42CA02EA7E857C9F85F867BE186E5EA7C383FD68BD8F0CE36FB5A6E55B95A47067A8661E",
        "t1": "ce7fa8810d9c008b0ff1be345902b811",
        "support_multi": 1,
        "gitversion": "5ac9396",
        "t2": "9d03b32655894a2c61d4e35dd0a1e7087be55d711bf930f327bc11653d442d0ded29f237e5eca9fc16e16f04358f6011a54b3a13ec00adaa54c08cca987dfc5c26ec00ede093ae9eb505bbcaabfa9cadbb4bdd4816ba72f07d593bb75b1fabd3529f2edc3211571cb4da06fef34c3941",
        "key": "338557f741a6224d9d6c696493aae70b",
        "t3": "MCwwLDAsMCwwLDY1NTMwLDAsMCww"
    }
    
    variables = [param1, param2, param3, param4, param5, param6]
    sorted_variables = sorted(variables)
    signstr = '' + salt
    for param in sorted_variables:
        signstr = signstr + param
    signstr = signstr + (json.dumps(body_json)) + salt
    
    # 使用本地MD5加密
    signature = md5_encrypt(signstr.replace(" ", ""))
    
    if not signature:
        sender.reply("❌ MD5签名生成失败")
        return None
    
    url = "https://gateway.kugou.com:443/v7/login_by_verifycode/?" + param1 + "&signature=" + signature + "&" + param2 + "&" + param3 + "&" + param4 + "&" + param5 + "&" + param6
    
    try:
        respond = requests.post(url, headers=info_headers, data=(json.dumps(body_json)).replace(" ", ""))
        rejson = respond.json()
        if rejson['status'] == 1 and rejson['error_code'] == 0:
            secu_params = rejson['data']['secu_params']
            userid = str(rejson['data']['userid'])
            key = '0756785487a71b02a3c5df3dca995c35'
            iv = 'a3c5df3dca995c35'
            
            # 使用本地AES解密
            secu_params_jiemi = aes_decrypt(secu_params, key, iv)
            
            if not secu_params_jiemi:
                sender.reply("❌ AES解密失败")
                return None
                
            token = (json.loads(secu_params_jiemi))['token']
            return Account(userid, token)
        else:
            error_msg = """
=====登录失败=====
❌ 登录失败，可能原因：
1. 验证码错误或已过期
2. 手机号绑定了多个酷狗账号

💡 解决方法：
1. 重新获取验证码
2. 请检查手机号绑定的酷狗账号
3. 如有多个账号请注销多余账号
4. 如仍有问题请联系管理员
=================="""
            sender.reply(error_msg)
            return None
    except Exception as e:
        sender.reply(f"""
=====登录失败=====
❌ 登录失败，可能原因：
1. 验证码错误或已过期
2. 手机号绑定了多个酷狗账号

💡 解决方法：
1. 重新获取验证码
2. 请检查手机号绑定的酷狗账号
3. 如有多个账号请注销多余账号
4. 如仍有问题请联系管理员

⚠️ 错误信息：{str(e)}
==================""")
        return None

def bind_account():
    """绑定账号"""
    sender.reply("""
=====酷狗账号登录=====
请输入手机号码:
------------------
回复"q"退出操作
==================""")

    mobile = sender.input(120000, 1, False)
    if not mobile:
        sender.reply("⏰ 操作超时，已退出")
        return
    elif mobile.lower() == 'q':
        sender.reply("✅ 已取消登录")
        return
        
    if send_code(mobile):
        sender.reply("""
请输入收到的验证码:
------------------
回复"q"退出操作""")
        
        code = sender.input(120000, 1, False)
        if not code:
            sender.reply("⏰ 操作超时，已退出")
            return
        elif code.lower() == 'q':
            sender.reply("✅ 已取消登录")
            return
            
        account = login_by_code(mobile, code)
        if account:
            # 新格式：token#userid
            account_str = f"{account.token}#{account.userid}"
            
            # 保存账号信息
            if not uservalue:
                middleware.bucketSet('dd_kg_user', userid, str([mobile]))
            else:
                accounts = eval(uservalue)
                if mobile not in accounts:
                    accounts.append(mobile)
                    middleware.bucketSet('dd_kg_user', userid, str(accounts))
            
            # 保存账号详细信息
            middleware.bucketSet('dd_kg_info', f"{userid}_{mobile}", account_str)
            
            # 检查授权状态
            accountVip = middleware.bucketGet('dd_kg_auth', mobile) or ''
            if len(accountVip) == 0 or accountVip <= today_time:
                # 未授权或已过期,显示授权选项
                auth_menu = """
=====账号未授权=====
[1] 立即授权
[2] 稍后授权
------------------
回复数字选择操作
回复"q"退出操作
=================="""
                sender.reply(auth_menu)
                choice = sender.input(120000, 1, False)
                
                if choice == '1':
                    auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
                    sender.reply(auth_guide)
                    
                    mes = sender.input(120000, 1, False)
                    if mes is None or mes == 'timeout':
                        sender.reply('⏰ 操作超时,已退出')
                        exit(0)
                    elif mes == 'q' or mes == 'Q':
                        sender.reply('✅ 已退出管理')
                        exit(0)
                    mes = ValueErrors(value=mes, count=999)
                    money = Decimal(mes) * Decimal(kgVipmoney)
                    zf(project='酷狗授权', me_as_int=mes, accountVip=accountVip, token=account_str,
                       phone=mobile, account=mobile)
                    accountVip = empower(empowertime=accountVip, me_as_int=mes)
                    middleware.bucketSet(bucket='dd_kg_auth', key=mobile, value=accountVip)
                    
                    # 更新青龙变量
                    ql_url, token = connect_qinglong()
                    if ql_url and token:
                        update_env(ql_url, token, account_str, mobile, mobile)
                    
                    result_msg = f"""
=====订单完成=====
🎈 名称: 酷狗授权
🎉 数量: {mes} 个月
💰 金额: {money} 元
==================""" 
                    sender.reply(result_msg)
                elif choice == '2':
                    sender.reply(f"""
=====绑定成功=====
👤 账号: {mask_phone(mobile)}
⚠️ 请尽快完成授权
💡 发送 kg管理 可进行授权
==================""")
                else:
                    sender.reply("✅ 已取消操作")
            else:
                # 已授权,直接更新青龙变量
                ql_url, token = connect_qinglong()
                if ql_url and token:
                    if update_env(ql_url, token, account_str, mobile, mobile):
                        sender.reply(f"""
=====绑定成功=====
👤 账号: {mask_phone(mobile)}
✅ 账号已添加至青龙
📅 授权到期: {accountVip}
==================""")
                    else:
                        sender.reply(f"""
=====绑定成功=====
👤 账号: {mask_phone(mobile)}
❌ 添加青龙变量失败
📅 授权到期: {accountVip}
==================""")
                else:
                    sender.reply(f"""
=====绑定成功=====
👤 账号: {mask_phone(mobile)}
❌ 未配置青龙或连接失败
📅 授权到期: {accountVip}
==================""")

def get_account_info(account):
    """获取账号信息"""
    try:
        ctime13 = str(int(time.time() * 1000))
        paramsdata = f'srcappid=2919&clientver=12149&clienttime={ctime13}&mid=&uuid=&dfid=&appid=1005&userid={account.userid}&token={account.token}&from=client&spec=15&h5=1'
        datalist = paramsdata.split('&')
        # 排序
        sorted_variables = sorted(datalist)
        signstr = ''
        for param in sorted_variables:
            signstr = signstr + param
        signstr = 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt ' + signstr + 'NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt '
        signature = md5_encrypt(signstr.replace(" ", ""))
        if not signature:
            return {'success': False, 'error': 'MD5签名生成失败'}
        params = paramsdata + '&signature=' + signature
        url = 'https://gateway.kugou.com/mstc/musicsymbol/v1/user/info?' + params
        
        respond = requests.get(url, headers=info2_headers)
        rejson = respond.json()
        
        if rejson['status'] == 1:
            account_data = rejson.get('data', {}).get('account', {})
            return {
                'success': True,
                'balance_coins': account_data.get('balance_coins', 0),
                'nickname': account_data.get('nick_name', '未知'),
                'error': None
            }
        else:
            return {
                'success': False,
                'error': rejson.get('error', '获取账号信息失败')
            }
    except Exception as e:
        return {
            'success': False,
            'error': f"获取账号信息失败: {str(e)}"
        }

def get_today_coins(account):
    """获取今日金币"""
    try:
        ctime10 = str(int(time.time()))
        
        # 构建参数
        param1 = f'userid={account.userid}'
        param2 = f'token={account.token}'
        param3 = 'appid=1005'
        param4 = 'from=client'
        param5 = 'page=1'
        param6 = 'option=1'  # 1表示收入明细
        param7 = 'pagesize=50'  # 增加pagesize以确保获取当天所有记录
        param8 = 'dfid='
        param9 = 'mid=30767145192326147088652695110646018138'
        param10 = 'clientver=12149'
        param11 = f'clienttime={ctime10}'
        param12 = 'uuid=-'
        
        variables = [param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12]
        # 排序
        sorted_variables = sorted(variables)
        signstr = ''
        for param in sorted_variables:
            signstr = signstr + param
        signstr = salt + signstr + salt
        
        signature = md5_encrypt(signstr.replace(" ", ""))
        if not signature:
            return {'success': False, 'today_coins': 0, 'error': 'MD5签名生成失败'}
        
        url = 'https://gateway.kugou.com/mstc/musicsymbol/v1/user/bills?' + param1 + '&' + param2 + '&' + param3 + '&' + param4 + '&' + param5 + '&' + param6 + '&' + param7 + '&' + param8 + '&signature=' + signature + '&' + param9 + '&' + param10 + '&' + param11 + '&' + param12
        
        respond = requests.get(url, headers=info2_headers)
        rejson = respond.json()
        
        # 获取今天的日期
        today = datetime.now().date()
        today_coins = 0
        
        # 统计今日收入
        if rejson['status'] == 1 and 'list' in rejson.get('data', {}):
            for item in rejson['data']['list']:
                try:
                    timestamp = item.get('addtime', 0)
                    change_coins = item.get('change_coins', 0)
                    
                    # 转换时间戳
                    dt_object = datetime.fromtimestamp(timestamp)
                    
                    # 如果是今天的记录
                    if dt_object.date() == today:
                        today_coins += change_coins
                except Exception:
                    continue
            
            return {
                'success': True,
                'today_coins': today_coins,
                'error': None
            }
        else:
            return {
                'success': False,
                'today_coins': 0,
                'error': rejson.get('error', '获取今日金币数据异常')
            }
    except Exception as e:
        return {
            'success': False,
            'today_coins': 0,
            'error': f"获取今日金币失败: {str(e)}"
        }

def mask_phone(phone):
    """手机号码脱敏处理"""
    if len(phone) != 11:
        return phone
    return phone[:3] + '*' * 4 + phone[-4:]

def query_accounts():
    """查询账号信息"""
    if not uservalue:
        sender.reply("""
=====未绑定账号=====
❌ 未找到任何账号信息
==================""")
        return
        
    try:
        accounts = eval(uservalue)
        account_list = """
=====账号列表=====
[0] 查询所有账号
------------------"""
        
        for i, mobile in enumerate(accounts, 1):
            account_list += f"\n[{i}] {mask_phone(mobile)}"
            
        account_list += """
------------------
回复数字选择账号
回复"q"退出操作
=================="""
        
        sender.reply(account_list)
        
        choice = sender.input(120000, 1, False)
        if not choice:
            sender.reply("⏰ 操作超时，已退出")
            return
        elif choice.lower() == 'q':
            sender.reply("✅ 已取消查询")
            return
            
        try:
            choice_num = int(choice)
            if choice_num == 0:
                # 查询所有账号
                for mobile in accounts:
                    account_str = middleware.bucketGet('dd_kg_info', f"{userid}_{mobile}")
                    accountVip = middleware.bucketGet('dd_kg_auth', mobile) or '未授权'
                    auth_status = "已授权" if accountVip and accountVip > today_time else "未授权"
                    if account_str:
                        try:
                            # 新格式：token#userid
                            token, account_userid = account_str.split('#')
                            account = Account(account_userid, token)
                            info = get_account_info(account)
                            today = get_today_coins(account)
                            if info['success'] and today['success']:
                                sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
💰 总金币: {info['balance_coins']}
📈 今日金币: {today['today_coins']}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
==================""")
                            else:
                                error = info['error'] if not info['success'] else today['error']
                                sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
❌ {error}
==================""")
                        except Exception as e:
                            sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
❌ 账号信息解析失败: {str(e)}
==================""")
                    else:
                        sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
❌ 未找到账号信息
==================""")
                        
            elif 1 <= choice_num <= len(accounts):
                mobile = accounts[choice_num-1]
                account_str = middleware.bucketGet('dd_kg_info', f"{userid}_{mobile}")
                accountVip = middleware.bucketGet('dd_kg_auth', mobile) or '未授权'
                auth_status = "已授权" if accountVip and accountVip > today_time else "未授权"
                if account_str:
                    try:
                        # 新格式：token#userid
                        token, account_userid = account_str.split('#')
                        account = Account(account_userid, token)
                        info = get_account_info(account)
                        today = get_today_coins(account)
                        if info['success'] and today['success']:
                            sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
💰 总金币: {info['balance_coins']}
📈 今日金币: {today['today_coins']}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
==================""")
                        else:
                            error = info['error'] if not info['success'] else today['error']
                            sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
❌ {error}
==================""")
                    except Exception as e:
                        sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
❌ 账号信息解析失败: {str(e)}
==================""")
                else:
                    sender.reply(f"""
=====账号信息=====
👤 账号: {mask_phone(mobile)}
🔐 授权状态: {auth_status}
📅 授权到期: {accountVip}
❌ 未找到账号信息
==================""")
                        
            else:
                sender.reply("❌ 无效的序号")
                
        except ValueError:
            sender.reply("❌ 请输入正确的序号")
            
    except Exception as e:
        sender.reply(f"""
=====查询失败=====
❌ 错误: {str(e)}
==================""")

def manage_accounts():
    """管理账号"""
    if not uservalue:
        sender.reply("""
=====账号管理=====
❌ 未找到任何账号信息
==================""")
        return
        
    try:
        accounts = eval(uservalue)
        account_list = """
=====账号管理=====
[1] 授权账号
[2] 删除账号
------------------
回复数字选择操作
回复"q"退出操作
=================="""
        
        sender.reply(account_list)
        
        choice = sender.input(120000, 1, False)
        if not choice:
            sender.reply("⏰ 操作超时，已退出")
            return
        elif choice.lower() == 'q':
            sender.reply("✅ 已取消操作")
            return
            
        if choice == '2':
            # 删除账号
            account_list = """
=====选择账号====="""
            
            for i, mobile in enumerate(accounts, 1):
                account_list += f"\n[{i}] {mask_phone(mobile)}"
                
            account_list += """
------------------
回复数字选择账号
回复"q"退出操作
=================="""
            
            sender.reply(account_list)
            
            account_choice = sender.input(120000, 1, False)
            if not account_choice:
                sender.reply("⏰ 操作超时，已退出")
                return
            elif account_choice.lower() == 'q':
                sender.reply("✅ 已取消操作")
                return
                
            try:
                choice_num = int(account_choice)
                if 1 <= choice_num <= len(accounts):
                    mobile = accounts[choice_num-1]
                    
                    # 删除账号信息
                    accounts.remove(mobile)
                    middleware.bucketSet('dd_kg_user', userid, str(accounts))
                    middleware.bucketDel('dd_kg_info', f"{userid}_{mobile}")
                    middleware.bucketDel('dd_kg_auth', mobile)
                    
                    # 从青龙中删除变量
                    ql_url, token = connect_qinglong()
                    if ql_url and token:
                        delete_env_by_account(ql_url, token, mobile)
                    
                    sender.reply(f"""
=====删除成功=====
✅ 账号 {mask_phone(mobile)} 已删除
==================""")
                else:
                    sender.reply("❌ 无效的序号")
                    
            except ValueError:
                sender.reply("❌ 请输入正确的序号")
                
        elif choice == '1':
            # 授权账号
            account_list = """
=====选择账号====="""
            
            for i, mobile in enumerate(accounts, 1):
                accountVip = middleware.bucketGet('dd_kg_auth', mobile) or ''
                vip_status = accountVip if accountVip else '未授权'
                account_list += f"\n[{i}] {mask_phone(mobile)}\n    授权至: {vip_status}"
                
            account_list += """
------------------
回复数字选择账号
回复"q"退出操作
=================="""
            
            sender.reply(account_list)
            
            account_choice = sender.input(120000, 1, False)
            if not account_choice:
                sender.reply("⏰ 操作超时，已退出")
                return
            elif account_choice.lower() == 'q':
                sender.reply("✅ 已取消操作")
                return
                
            try:
                choice_num = int(account_choice)
                if 1 <= choice_num <= len(accounts):
                    mobile = accounts[choice_num-1]
                    account_str = middleware.bucketGet('dd_kg_info', f"{userid}_{mobile}")
                    if not account_str:
                        sender.reply(f"""
=====授权失败=====
❌ 未找到账号 {mask_phone(mobile)} 的信息
==================""")
                        return
                        
                    auth_guide = """
=====设置授权时长=====
请输入授权月数(如:1)
------------------
回复数字设置月数
回复"q"退出操作
=================="""
                    sender.reply(auth_guide)
                    
                    mes = sender.input(120000, 1, False)
                    if mes is None or mes == 'timeout':
                        sender.reply('⏰ 操作超时,已退出')
                        return
                    elif mes == 'q' or mes == 'Q':
                        sender.reply('✅ 已退出管理')
                        return
                        
                    mes = ValueErrors(value=mes, count=999)
                    money = Decimal(mes) * Decimal(kgVipmoney)
                    accountVip = middleware.bucketGet('dd_kg_auth', mobile) or ''
                    
                    zf(project='酷狗授权', me_as_int=mes, accountVip=accountVip, token=account_str,
                       phone=mobile, account=mobile)
                    accountVip = empower(empowertime=accountVip, me_as_int=mes)
                    middleware.bucketSet(bucket='dd_kg_auth', key=mobile, value=accountVip)
                    
                    # 更新青龙变量
                    ql_url, token = connect_qinglong()
                    if ql_url and token:
                        update_env(ql_url, token, account_str, mobile, mobile)
                    
                    result_msg = f"""
=====订单完成=====
🎈 名称: 酷狗授权
🎉 数量: {mes} 个月
💰 金额: {money} 元
==================""" 
                    sender.reply(result_msg)
                else:
                    sender.reply("❌ 无效的序号")
                    
            except ValueError:
                sender.reply("❌ 请输入正确的序号")
        else:
            sender.reply("❌ 无效的选择")
            
    except Exception as e:
        sender.reply(f"""
=====操作失败=====
❌ 错误: {str(e)}
==================""")

def show_tutorial():
    """显示酷狗教程"""
    tutorial = """
=====酷狗使用教程=====
🎯 功能介绍：
本插件无需抓包，直接手机号登录

📝 指令说明：
1️⃣ 酷狗登录 - 绑定账号
2️⃣ 酷狗查询 - 查看账号信息
3️⃣ 酷狗管理 - 管理账号授权
4️⃣ 酷狗授权 - 管理员授权功能
5️⃣ 酷狗清理 - 管理员清理功能

💡 使用流程：
1. 发送【酷狗登录】
2. 输入手机号
3. 输入收到的验证码
4. 选择是否立即授权
5. 发送【酷狗查询】查看状态

⚠️ 注意事项：
1. 请确保输入正确的手机号
2. 验证码有效期较短，请及时输入
3. 授权到期前请及时续期
4. 同一手机号不要重复绑定

🔔 温馨提示：
如遇到问题请联系管理员
=================="""
    sender.reply(tutorial)

def kg_cron_check():
    """定时检测授权过期推送"""
    users = middleware.bucketAllKeys(bucket='dd_kg_user')
    if not users:
        return
    today = str(datetime.now().date())
    for user in users:
        try:
            accountlist = middleware.bucketGet(bucket='dd_kg_user', key=user) or ''
            if not accountlist:
                continue
            accounts = eval(accountlist)
            for account in accounts:
                try:
                    accountVip = middleware.bucketGet(bucket='dd_kg_auth', key=account) or ''
                    phone = mask_phone(account)
                    if not accountVip or accountVip <= today:
                        push_msg = f"""
=====酷狗账号通知=====
📱 账号: {phone}
⏰ 定时检测提醒
------------------
❌ 授权已过期
💡 请及时续费授权
=================="""
                        for platform in ['wb', 'tg', 'qq', 'qb', 'wx']:
                            try:
                                middleware.push(platform, '', user, '', push_msg)
                            except:
                                pass
                    else:
                        try:
                            expire_date = datetime.strptime(accountVip, '%Y-%m-%d').date()
                            days_left = (expire_date - datetime.now().date()).days
                            if days_left <= 3:
                                push_msg = f"""
=====酷狗账号通知=====
📱 账号: {phone}
⏰ 定时检测提醒
------------------
⚠️ 授权即将到期
📅 到期时间: {accountVip}
⏳ 剩余天数: {days_left}天
💡 请及时续费授权
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
    global kgVipmoney, kgcoin
    _, _, var_name, zsm, kgVipmoney, kgcoin, use_ma_pay, _ = get_config()
    message = sender.getMessage()
    imtype = sender.getImtype()
    
    if imtype == 'fake':
        kg_cron_check()
    elif '酷狗登录' in message or '酷狗登陆' in message:
        bind_account()
    elif '酷狗查询' in message:
        query_accounts()
    elif '酷狗管理' in message:
        manage_accounts()
    elif '酷狗清理' in message:
        clean_expired_accounts()
    elif message == '酷狗授权':
        kg_auth()
    elif message == '酷狗教程':
        show_tutorial()
    else:
        sender.setContinue()

if __name__ == "__main__":
    main() 
