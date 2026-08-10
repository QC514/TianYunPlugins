# [author: mrconli]
# [title: 泰康在线]
# [language: python]
# [class: 工具类]
# [service: 呆瓜群：591022646，插件群：1040780519] 售后联系方式
# [disable: false] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [rule: ^泰康(.*)|(.*)泰康$] 匹配规则，多个规则时向下依次写多个
# [cron: 0 8 * * *] cron定时，支持5位域和6位域
# [priority: 55] 优先级，数字越大表示优先级越高
# [platform: all] 适用的平台
# [open_source: false]是否开源
# [icon: https://pp.myapp.com/ma_icon/0/icon_42327729_1745494497/256]图标链接地址，请使用48像素的正方形图标，支持http和https
# [version: 1.5.0]版本号
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [price: 13.88] 上架价格
# [description: AI练手，自用。仅提交青龙”<br>指令：泰康（登录|查询|管理|授权|清理|教程）<br>1.支持积分支付数据桶自定义，不再为积分系统不统一烦恼！<br>2.默认支持调用linzixuan最新积分。<1.5.0更新(20250515)：优化查询显示，优化青龙提交；><br>1.4.0更新(20250430)：增加红包记录查询。] 使用方法尽量写具体


# [param: {"required":true,"key":"mrconli.config.zsm","bool":false,"placeholder":"示例: http://10.10.10.10:8080/zsm.jpg","name":"收款码地址","desc":"赞赏码或收款码地址"}]
# [param: {"required":true,"key":"mrconli.taikang.ql_config","bool":false,"placeholder":"http://10.10.10.10:5700丨ClientID丨ClientSecret","name":"对接青龙地址","desc":"使用丨分割"}]
# [param: {"required":false,"key":"mrconli.taikang.var_name","bool":false,"placeholder":"mrconli_tkzx","name":"环境变量名","desc":"青龙容器内的变量名，默认为：mrconli_tkzx"}]
# [param: {"required":false,"key":"mrconli.taikang.price","bool":false,"placeholder":"1","name":"上车价格","desc":"上车价格(单位:元)/30天"}]
# [param: {"required":false,"key":"mrconli.taikang.coin","bool":false,"placeholder":"不填为关闭状态","name":"积分开通","desc":"授权一个月的积分，只能为整数"}]
# [param: {"required":false,"key":"mrconli.taikang.coin_bucket","bool":false,"placeholder":"","name":"积分数据桶","desc":"默认使用dd_sign_points"}]
# [param: {"required":false,"key":"mrconli.taikang.is_proxy","bool":false,"placeholder":"False","name":"是否启用代理","desc":"True/False"}]
# [param: {"required":false,"key":"mrconli.taikang.proxy_pool","bool":false,"placeholder":"http://代理池API地址","name":"代理池地址","desc":"代理API服务地址"}]

import httpx
import os
import json
from urllib.parse import urlencode
import re  # 处理正则表达式
from datetime import datetime, timedelta  # 操作日期、时间以及时间间隔
import middleware  # autman的中间件
import urllib.parse  # 处理url编码
import urllib3
from decimal import Decimal  # 处理浮点数
import time  # 处理时间
import json  # 处理json数据
import hashlib  # 处理哈希值
import uuid  # 生成唯一ID
import asyncio
import aiohttp
from functools import lru_cache
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import requests
from typing import Dict, Any





# 禁用 SSL 警告
urllib3.disable_warnings()

# 禁用 InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

senderID = middleware.getSenderID()  # 获取发送者QQ号
sender = middleware.Sender(senderID)  # 获取发送者对象
userid = sender.getUserID()  # 存储当前发送者的用户 ID，与 senderID 类似，但通常用于内部标识
uservalue = middleware.bucketGet(bucket='mrconli.taikang.user', key=userid)
today_date = datetime.now().date()
today_time = str(today_date)

# 代理配置
MAX_RETRIES = 5  # 最大重试次数
IS_PROXY = middleware.bucketGet('mrconli.taikang', 'is_proxy') or "False"  # 是否启用代理True
PROXY_API = middleware.bucketGet('mrconli.taikang', 'proxy_pool') or "http://10.10.10.251:12306/help/proxy/original"
if not PROXY_API:
    raise ValueError("代理池地址未配置，请在插件设置中配参")
proxy = None  # 初始化全局代理变量

def update_proxy():
    """更新代理IP地址"""
    global proxy
    try:
        if not IS_PROXY:
            proxy = None
            return
        response = requests.get(PROXY_API, timeout=10)
        ip = response.text.strip()
        if "请先添加白名单" in ip:
            raise ValueError("请配置代理白名单")
        proxy = {
            'http': ip,
            'https': ip,
        }
    #    sender.reply(f"✅ 代理获取成功: {ip}")
    except Exception as e:
        sender.reply(f"❌ 代理获取失败: {str(e)}")
        proxy = None


def _send_request(method, url, **kwargs):
    """带代理重试的请求方法"""
    global proxy
    attempts = 0
    while attempts < MAX_RETRIES:
        try:
            # 确保代理已初始化
            if IS_PROXY:
                proxy = proxy if 'proxy' in globals() else None
                if not proxy:
                    update_proxy()
            kwargs['timeout'] = kwargs.get('timeout', 15)  # 默认超时时间 15 秒
            response = requests.request(
                method=method,
                url=url,
                proxies=proxy if IS_PROXY and proxy else None,
                **kwargs
            )
            response.raise_for_status()
            return response
        except (requests.exceptions.ProxyError, requests.exceptions.Timeout) as e:
            print(f"⚠️ 代理异常: {str(e)}")
            if IS_PROXY:
                update_proxy()
                attempts += 1
                print(f"🔄 重试请求 ({attempts}/{MAX_RETRIES})")
                time.sleep(2)
        except requests.exceptions.RequestException as e:
            print(f"🚨 请求失败: {str(e)}")
            raise
    raise Exception(f"请求失败，超过最大重试次数: {MAX_RETRIES}")


def task_api(config):
    result = {}
    try:
        host = config['url'].split('//', 1)[-1].split('/', 1)[0]
        headers = {
            "Host": host,
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.25(0x18001929) NetType/WIFI Language/zh_CN",
            "Referer": "https://servicewechat.com/wx9e3e7020c4a10356/185/page-frame.html"
        }
        headers.update(config.get('headerParam', {}))
        
        with httpx.Client(timeout=5) as client:
            url = config['url']
            if 'queryParam' in config:
                url += '?' + urlencode(config['queryParam'], doseq=True)
            
            data = None
            if 'body' in config:
                content_type = config.get('Content-Type') or 'application/x-www-form-urlencoded'
                headers['Content-Type'] = content_type
                
                if isinstance(config['body'], dict):
                    if 'json' in content_type:
                        data = json.dumps(config['body'])
                    else:
                        processed_body = {}
                        for k, v in config['body'].items():
                            if isinstance(v, (dict, list)):
                                processed_body[k] = json.dumps(v, ensure_ascii=False)
                            else:
                                processed_body[k] = v
                        data = urlencode(processed_body, doseq=True)
                else:
                    data = str(config['body'])
            
            response = client.request(
                method=config.get('method', 'POST'),
                url=url,
                headers=headers,
                data=data,
                timeout=5
            )
            
            result['status_code'] = response.status_code
            result['resp'] = {
                'statusCode': response.status_code,
                'body': response.text
            }
            
            try:
                result['result'] = response.json()
            except json.JSONDecodeError as e:
                print(f"[{config.get('fn', '')}] 非JSON响应: {str(e)}")
                result['result'] = response.text
            
    except Exception as e:
        print(f"请求失败: {str(e)}")
    finally:
        return result

def get_user_info(unionid):
    user_info = {
        'valid': False,
        'memberid': '',
        'token': '',
        'mobile': '',
        'name': ''
    }
    
    try:
        config = {
            'fn': 'getUserInfo',
            'method': 'POST',
            'url': 'https://m.tk.cn/member_api/',
            'body': {
                'api_s': 'member.userbind',
                'api_m': 'selectwxbindbybindid',
                'params': {
                    'platform': 'APPLET',
                    'fromid': '71672',
                    'bindid': unionid
                }
            }
        }
        response = task_api(config)
        if isinstance(response.get('result'), dict):
            res_data = response['result']
            if res_data.get('result') == 'success':
                user_info.update({
                    'valid': True,
                    'memberid': res_data['data']['memberid'],
                    'token': res_data['data']['token'],
                    'mobile': res_data['data']['pmemberuser']['membertmmobile'],
                    'name': res_data['data']['pmemberuser']['membertmrealname']
                })
            #    sender.reply(f"手机：{user_info['mobile']}    实名: {user_info['name']}")  
                return user_info        
            else:
            #    sender.reply(f"登录失败：{res_data.get('message', '未知错误')}")
                return None
        return user_info
    except Exception as e:
        print(f"获取用户信息异常：{str(e)}")
        return None

def do_sign(memberid, token, unionid, index):
    try:
        config = {
            'fn': 'doSign',
            'method': 'POST',
            'url': 'https://m.tk.cn/activity_execute/rest/membergoldbean/sign',
            'body': {
                'enc': False,
                'memberid': memberid,
                'token': token,
                'unionid': unionid,
                'deviceId': "",
                'fromid': '71672',
                'platform': 'WECHAT',
                'coordinate': "",
                'nickName': ""
            }
        }
        
        response = task_api(config)
        if isinstance(response.get('result'), dict):
            res_data = response['result']
            if res_data.get('error_code') in ['0', 0]:
                print(f"账号[{index}] 签到成功，获得{res_data['data']['amount']}积分")
            elif res_data.get('error_code') == '200004200003':
                print(f"账号[{index}] 今日已完成签到")
            else:
                err_msg = res_data.get('error_message') or res_data.get('message') or res_data.get('msg', '未知错误')
                print(f"账号[{index}] 签到失败：{err_msg}")
        return response
    except Exception as e:
        print(f"账号[{index}] 签到异常：{str(e)}")
        return {}

def main_page(unionid):
    user_info = get_user_info(unionid)
#    sender.reply(user_info)
    memberid = user_info.get('memberid')
    token = user_info.get('token')
    mobile = user_info.get('mobile')
    name = user_info.get('name')
    try:
        config = {
            'fn': 'mainPage',
            'method': 'POST',
            'url': 'https://m.tk.cn/activity_execute/rest/membergoldbean/mainPage',
            'body': {
                'enc': False,
                'memberid': memberid,
                'token': token,
                'platform': 'WECHAT',
                'fromid': '71672'
            }
        }
        
        response = task_api(config)
        if isinstance(response.get('result'), dict):
            res_data = response['result']
            if res_data.get('error_code') in ['0', 0] and res_data.get('data') and 'allbeans' in res_data['data']:
        #        print(f"当前金币: {res_data['data']['allbeans']}")
                allbeans = res_data['data']['allbeans']

            else:
                err_msg = res_data.get('error_message') or res_data.get('message') or res_data.get('msg', '未知错误')
                print(f"查询金币失败：{err_msg}")
        return mobile, name, allbeans
    except Exception as e:
        print(f"主页面查询异常：{str(e)}")
        return {}
        
def get_coupon_list(unionid):
    user_info = get_user_info(unionid)
    memberid = user_info.get('memberid')
    token = user_info.get('token')
    """查询待领取红包列表"""
    try:
        config = {
            'fn': 'getCouponList',
            'method': 'POST',
            'url': 'https://m.tk.cn/member_api/',
            'body': {
                'api_s': 'member.coupon',
                'api_m': 'selectmembercouponlist',
                'params': {
                    'memberid': memberid,
                    'token': token,
                    'status': "1",  # 1-有效 2-已使用 3-已过期
                    'fromid': '67527'
                }
            }
        }
        
        response = task_api(config)
        if isinstance(response.get('result'), dict):
            res_data = response['result']
            if res_data.get('result') == 'success':
                coupons = res_data.get('data', {}).get('pmembercoupon', [])
                print(f"共{len(coupons)}个带领取：")
                for coupon in coupons:
                    print(f"待领红包: "
                          f"金额: {coupon.get('inventoryvalue','0.00')}元 "
                          f"有效期至: {coupon.get('voiddateend','未知日期')}")
                    dailingred = f"🍀【待领 {len(coupons)} 个红包】：\n"
                    dailingred_list = []
                    for coupon in coupons:
                        dailingred_list.append(f"🧧{coupon.get('couponname','未知')}: {coupon.get('inventoryvalue','0.00')}元\n⏰有效期至: {coupon.get('voiddateend','未知日期')}\n")
                    dailingred_show = "\n".join(dailingred_list)
                return dailingred, dailingred_show
            else:
                print(f"查询失败：{res_data.get('message', '未知错误')}")
                return ("", "")
        return ("", "")
    except Exception as e:
        print(f"优惠券查询异常：{str(e)}")
        return ("", "")

def get_mycoupon_list(unionid):
    """查询已领取红包列表"""
    user_info = get_user_info(unionid)
    memberid = user_info.get('memberid')
    token = user_info.get('token')
    try:
        config = {
            'fn': 'getCouponList',
            'method': 'POST',
            'url': 'https://m.tk.cn/member_api/',
            'body': {
                'api_s': 'member.coupon',
                'api_m': 'selectmembercouponlist',
                'params': {
                    'memberid': memberid,
                    'token': token,
                    'status': "2",  # 1-有效 2-已使用 3-已过期
                    'fromid': '67527'
                }
            }
        }
        
        response = task_api(config)
        if isinstance(response.get('result'), dict):
            res_data = response['result']
            if res_data.get('result') == 'success':
                coupons = res_data.get('data', {}).get('pmembercoupon', [])
                total = 0.0
                for coupon in coupons:
                    try:
                        total += float(coupon.get('inventoryvalue', '0.00'))
                    except:
                        pass
                print(f"共找到{len(coupons)}条已领红包记录，显示前5条")
                for coupon in coupons[:5]:
                    print(f"已领红包: "
                          f"金额: {coupon.get('inventoryvalue','0.00')}元 "
                          f"发放时间: {coupon.get('verifydate','未知日期')}")  
                print(f"已领红包总金额: {total:.2f}元")
                huizongred_total = f"===================\n💰️累计 {len(coupons)} 个红包，共 {total:.2f} 元\n"
                yilingred_total = f"\n🍃【已领红包】(近5条):\n" 
                yilingred_list = []
                for coupon in coupons[:5]:
                    yilingred_list.append(f"🧧{coupon.get('couponname','未知')}: {coupon.get('inventoryvalue','0.00')}元\n⏰领取时间: {coupon.get('verifydate','未知日期')}\n")
                yilingred_show = "\n".join(yilingred_list)
                return yilingred_total, yilingred_show, huizongred_total
            else:
                print(f"查询失败：{res_data.get('message', '未知错误')}")
                return ("", "")
        return ("", "")
    except Exception as e:
        print(f"优惠券查询异常：{str(e)}")
        return ("", "")



def bind():
    """绑定泰康账号"""
    sender.reply(
        "=====泰康账号登录=====\n"
        "📝 请输入登录参数:unionid\n"
        "抓包: 进小程序捉https://m.tk.cn/wechat_item/rest/xcx/login把返回里的unionid\n"
        "=====================\n"
        "⭐ 输入q退出操作\n"
    )
    unionid = sender.input(120000, 1, False)
    if unionid == '':
        sender.reply('输入超时！')
        exit(0)
    elif unionid.lower() == 'q':
        sender.reply('退出操作！')
        exit(0)
    user_info = get_user_info(unionid)
    
    memberid = user_info.get('memberid')
    mobile = user_info.get('mobile')
    name = user_info.get('name')
    
    if mobile is None:
        sender.reply('登录失败，无法获取账户信息')
        exit(0)
    try:
        try:
            accounts = json.loads(str(uservalue)) if uservalue else []
        except (json.JSONDecodeError, TypeError):
            return
        account = f"{memberid}"
        if account not in accounts:
            dlzt = "登录"
            accounts.append(account)
            middleware.bucketSet('mrconli.taikang.user', userid, json.dumps(accounts))
        else:
            dlzt = "更新"
            add_to_qinglong(unionid, account, userid)
        middleware.bucketSet('mrconli.taikang.token', account, unionid)
        middleware.bucketSet('mrconli.taikang.mobile', account, mobile)
#        if not add_to_qinglong(token, account, userid):
#            raise Exception("添加青龙变量失败")
        success_msg = f"""
====={dlzt}成功=====
📱 账号: {mobile}
------------------
发送"{manage_cmd}"管理账号
发送"{query_cmd}"查询账号
"""
        sender.reply(success_msg)
        return mobile, name
    except Exception as e:
        sender.reply(f"❌ 处理登录失败: {str(e)}")
        exit(0)

def batch_login():
    """批量登录函数"""
    global uservalue
    sender.reply(
        "=====泰康登录=====\n"
        "📝 请输入登录参数:unionid\n"
        "说明: 支持批量，一个账号一行” \n"
        "抓包: 进小程序捉https://m.tk.cn/wechat_item/rest/xcx/login把返回里的unionid\n"
        "=====================\n"
        "⭐ 输入q退出操作\n"
    )
    success_count = 0
    add_count = 0
    update_count = 0
    fail_count = 0
    error_reasons = []
    
    accounts_str = sender.input(120000, 1, False).strip()
    if accounts_str == 'q':
        sender.reply('⭐ 已退出登录操作')
        return
    if not accounts_str:
        sender.reply('⭐ 输入超时！')
        return
    accounts = [line.strip() for line in accounts_str.split('\n') if line.strip()]  # 移除lower()保持原始大小写
    
    total = len(accounts)
    if total == 0:
        sender.reply("❌ 未检测到有效账号信息")
        return
    sender.reply(f"🔍 共检测到 {total} 个账号，开始登录...")
    
    for index, account in enumerate(accounts, 1):
        try:
            # 执行登录
            user_info = get_user_info(account)
            memberid = user_info.get('memberid')
            mobile = user_info.get('mobile')
            name = user_info.get('name')
            if memberid:
                success_count += 1
                middleware.bucketSet('mrconli.taikang.token', memberid, account)
                middleware.bucketSet('mrconli.taikang.mobile', memberid, mobile)
                middleware.bucketSet('mrconli.taikang.name', memberid, name)
                current_accounts = eval(middleware.bucketGet('mrconli.taikang.user', userid) or '[]')
                if memberid not in current_accounts:
                    add_count += 1
                    status = "✅ 登录成功"
                    current_accounts.append(memberid)
                    middleware.bucketSet('mrconli.taikang.user', userid, json.dumps(current_accounts, ensure_ascii=False))
                else:
                    update_count += 1
                    status = "✅ 更新成功"
                    middleware.bucketSet('mrconli.taikang.token', memberid, account)
                    middleware.bucketSet('mrconli.taikang.mobile', memberid, mobile)
                    middleware.bucketSet('mrconli.taikang.name', memberid, name)
                    add_to_qinglong(account, memberid, userid)
                # 强制刷新全局账户缓存
                uservalue = json.dumps(current_accounts)    
            else:
                fail_count += 1
                status = "❌ 登录失败"
                error_reasons.append(f"{account[:3]}****{account[-7:]}: 认证失败")

            # 进度反馈
            progress = f"[{index}/{total}] {account[:3]}****{account[-7:]} {status}"
            sender.reply(progress)
        except Exception as e:
            fail_count += 1
            error_msg = f"{account[:3]}****{account[-7:]}: {str(e)}"
            error_reasons.append(error_msg)
            sender.reply(f"⚠️ 第{index}个账号处理失败: {error_msg}")
        time.sleep(2)

    # 生成统计报告
    report = (
        f"📊 登录完成\n"
        f"✔️ 执行成功: {success_count} 个\n"
        f"➕ 添加: {add_count} 个\n"
        f"🔄 更新: {update_count} 个\n"
        f"✖️ 失败: {fail_count} 个\n"
        f"------------------------\n"
        f"发送“{manage_cmd}”管理账号\n"
        f"发送“{query_cmd}”查询账号\n"
    )
    
    if error_reasons:
        report += "\n❌ 失败原因:\n" + "\n".join(error_reasons[:5])
        if len(error_reasons) > 5:
            report += f"\n...等{len(error_reasons)-5}个错误" 
    sender.reply(report)


def query():
    accounts = eval(uservalue or '[]')
    if not accounts:
        sender.reply(
            '\n=====泰康账号查询=====\n❌ 未找到任何账号\n------------------\n💡 发送"泰康登录"绑定账号\n===================')
        return
    # 生成交互菜单
    if len(accounts) > 1:
        menu = "=====请选择查询账号=====\n"
        menu += "[0] 查询全部账号\n"
        for idx, acc in enumerate(accounts, 1):
            menu += f"[{idx}] {acc[:3]}****{acc[-4:]}\n"
        menu += "=======================\n⚠️ 请回复数字序号(输入q退出)"
        sender.reply(menu)

        # 获取用户输入
        choice = sender.input(30000, 1, False)
        if choice.lower() == 'q':
            sender.reply('已取消查询')
            return
        if not choice.isdigit():
            sender.reply('输入格式错误，请回复数字')
            return

        choice = int(choice)
        if choice < 0 or choice > len(accounts):
            sender.reply('选择超出范围，已取消查询')
            return
    else:
        choice = 1  # 单个账号直接查询

    # 执行查询逻辑
    if choice == 0:
        target_accounts = accounts
        sender.reply('正在查询全部账号...')
    else:
        target_accounts = [accounts[choice - 1]]
        sender.reply('正在查询泰康，请耐心等待...')

    for account in target_accounts:

        try:
            accountVip = middleware.bucketGet('mrconli.taikang.auth', account)
            Token = middleware.bucketGet('mrconli.taikang.token', account)
            if not Token:
                sender.reply(f'【{account}】Token获取失败')
                continue
            if not accountVip:
                sender.reply(f'【{account}】账号未授权')
            elif accountVip < today_time:
                sender.reply(f'【{account}】云授权过期')
            else:
                mobile, name, balance = main_page(Token)
                dailingred, dailingred_show = get_coupon_list(Token)
                yilingred_total, yilingred_show,huizongred_total = get_mycoupon_list(Token)
                if mobile is None:
                    sender.reply('查询失败，无法获取账户信息')
                    continue
                sender.reply(
                    "=====泰康账号详情=====\n"
                    f"📱 账号: {mobile}\n"
                    f"👤 实名: {'* * '+name[-1] if name else '***'}\n"
                    f"💰 金币: {balance}\n"
                    f"⏰ 授权期限: {accountVip}\n"
                    "===================\n"
                    f"{dailingred}{dailingred_show}"
                    f"{yilingred_total}{yilingred_show}"
                    f"{huizongred_total}"
                    "===================\n"
                    )
        except Exception as e:
            sender.reply(f'【{mobile}】查询出错: {str(e)}')
        


def get_config():
    """获取插件配置"""
    try:

        coin_bucket = middleware.bucketGet('mrconli.taikang', 'coin_bucket') or 'dd_sign_points'
        middleware.bucketSet('mrconli.taikang', 'coin_bucket', coin_bucket)  # 确保配置项存在
        var_name = middleware.bucketGet('mrconli.taikang', 'var_name') or "mrconli_tkzx"
        if not var_name:
            print("未配置变量名，使用默认值: mrconli_tkzx")
            var_name = 'mrconli_tkzx'
            middleware.bucketSet('mrconli.taikang', 'var_name', var_name)
        ql_config = middleware.bucketGet('mrconli.taikang', 'ql_config')
        ql_params = ql_config.split('丨')
        if len(ql_params) == 3:
            ql_host = ql_params[0]
            ql_client_id = ql_params[1]
            ql_client_secret = ql_params[2]
        else:
            print("青龙配置不完整，请检查配置")
        manage_cmd = middleware.bucketGet('mrconli.taikang', 'manage_cmd') or '泰康管理'
        query_cmd = middleware.bucketGet('mrconli.taikang', 'query_cmd') or '泰康查询'
        login_cmd = middleware.bucketGet('mrconli.taikang', 'login_cmd') or '泰康登录'
        try:
            price = Decimal(middleware.bucketGet('mrconli.taikang', 'price') or '1')
            if price < 0:
                raise ValueError("价格不能为负数")
        except (ValueError, decimal.InvalidOperation):
            print("价格配置无效，使用默认值: 1")
            price = Decimal('1')
            middleware.bucketSet('mrconli.taikang', 'price', '1')
        try:
            coin_price = int(middleware.bucketGet('mrconli.taikang', 'coin') or '0')
            if coin_price < 0:
                raise ValueError("积分不能为负数")
        except ValueError:
            print("积分配置无效，使用默认值: 0")
            coin_price = 0
            middleware.bucketSet('mrconli.taikang', 'coin', '0')
        return (var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price)
    except Exception as e:
        error_msg = f"获取配置失败: {str(e)}"
        print(error_msg)
        sender.reply(f"❌ {error_msg}")
        raise


def init_qinglong():
    """初始化青龙连接"""
    try:
        ql_config = middleware.bucketGet('mrconli.taikang', 'ql_config')
        ql_params = ql_config.split('丨')
        if len(ql_params) == 3:
            ql_host = ql_params[0]
            ql_client_id = ql_params[1]
            ql_client_secret = ql_params[2]
        else:
            print("青龙配置不完整，请检查配置")
            exit(0)
        if not ql_host.endswith('/'):
            ql_host += '/'
        token = get_ql_token(ql_host, ql_client_id, ql_client_secret)
        return ql_host, token
    except Exception as e:
        sender.reply(f"❌ 连接青龙失败: {str(e)}")
        exit(0)


def get_ql_token(url, client_id, client_secret):
    """获取青龙token"""
    try:
        if not url.endswith('/'):
            url += '/'
        r = requests.get(f'{url}open/auth/token?client_id={client_id}&client_secret={client_secret}')
        if r.status_code != 200:
            raise Exception(f"请求失败: {r.status_code}")
        data = r.json()
        if "token" not in data.get('data', {}):
            raise Exception("获取token失败")
        return data['data']['token']
    except Exception as e:
        raise Exception(f"获取token失败: {str(e)}")


def add_to_qinglong(token, account, username):
    """添加变量到青龙"""
    try:
        url = f"{ql_host}/open/envs"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        
        # 强制更新逻辑（新增删除旧变量）
        existing_ids = []
        duplicate_vars = []
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            for env in response.json().get('data', []):
                if env['name'] == var_name and env.get('remarks', '') and account in env.get('remarks', ''):
                    existing_ids.append(env['id'])
                elif env['value'] == token:  # 新增重复值检测
                    duplicate_vars.append(env['id'])
        
        # 删除冲突变量（新增）
        if duplicate_vars:
            del_response = requests.delete(url, json=duplicate_vars, headers=headers)
            if del_response.status_code != 200:
                raise Exception(f"删除冲突变量失败: {del_response.text}")
        
        # 删除旧变量
        if existing_ids:
            del_response = requests.delete(url, json=existing_ids, headers=headers)
            if del_response.status_code != 200:
                raise Exception(f"删除旧变量失败: {del_response.text}")

        # 创建新变量（优化请求体格式）
        auth_time = middleware.bucketGet('mrconli.taikang.auth', account) or '未授权'
        data = {
            "name": var_name,
            "value": token,
            "remarks": f"泰康账号:{account}丨用户:{userid}丨授权时间:{auth_time}",
        }
        
        # 添加容错重试机制（新增）
        max_retries = 3
        for attempt in range(max_retries):
            response = requests.post(url, headers=headers, json=[data])
            if response.status_code == 200:
                new_ids = [item['id'] for item in response.json().get('data', [])]
                middleware.bucketSet('mrconli.taikang.env_id', account, json.dumps(new_ids))
                return True
            elif response.status_code == 500 and "SequelizeUniqueConstraintError" in response.text:
                print(f"🔄 检测到唯一性冲突，正在重试 ({attempt+1}/{max_retries})")
                time.sleep(1)
        
        # 增强错误信息（新增服务器响应详情）
        error_detail = response.json().get('message') or response.text
        raise Exception(f"操作失败：多次尝试后仍存在唯一性冲突 | {error_detail} [HTTP {response.status_code}]")
        
    except Exception as e:
        error_msg = f"青龙操作失败: {str(e)}"
        print(error_msg)
        sender.reply(f"❌ {error_msg}")
        return False


def enable_in_qinglong(env_ids):
    """启用环境变量"""
    try:
        url = f"{ql_url}/open/envs/enable"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, data=json.dumps(env_ids))
        if response.status_code == 200:
            rjson = response.json()
            if rjson.get('code') == 200:
                return True
            else:
                sender.reply(f"❌ 启用环境变量失败: {rjson.get('message')}")
                return False
        else:
            raise Exception(f"{response.status_code}")
    except Exception as e:
        sender.reply(f"❌ 启用环境变量失败: {str(e)}")
        return False


def disable_in_qinglong(env_ids):
    """禁用环境变量"""
    try:
        url = f"{ql_url}/open/envs/disable"
        headers = {
            "Authorization": f"Bearer {ql_token}",
            "Content-Type": "application/json"
        }
        response = requests.put(url, headers=headers, data=json.dumps(env_ids))
        if response.status_code == 200:
            rjson = response.json()
            if rjson.get('code') == 200:
                return True
            else:
                sender.reply(f"❌ 禁用环境变量失败: {rjson.get('message')}")
                return False
        else:
            raise Exception(f"{response.status_code}")
    except Exception as e:
        sender.reply(f"❌ 禁用环境变量失败: {str(e)}")
        return False


def delete_from_qinglong(account):
    """从青龙删除变量"""
    try:
        url = f"{ql_url}/open/envs"
        headers = {
            "Authorization": f"Bearer {ql_token}"
        }
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception("获取变量失败")
        env_id = None
        for env in response.json()['data']:
            if env['name'] == var_name and account in env.get('remarks', ''):
                env_id = env['id']
                break
        if env_id:
            response = requests.delete(url, headers=headers, json=[env_id])
            if response.status_code != 200:
                raise Exception("删除变量失败")
        return True
    except Exception as e:
        sender.reply(f"❌ 青龙操作失败: {str(e)}")
        return False


def manage_accounts():
    """管理账号"""
    accounts = eval(uservalue)
    if not accounts:
        sender.reply(f"""
=====账号管理=====
❌ 未找到任何账号
------------------
💡 发送"{login_cmd}"绑定账号
==================""")
        return

    # 账号列表构建
    account_list = """
=====账号列表=====
批量操作:
[00] 授权全部账号
[01] 删除全部账号
------------------
账号列表:"""
    for i, account in enumerate(accounts, 1):
        token = middleware.bucketGet('mrconli.taikang.token', account)
        auth = middleware.bucketGet('mrconli.taikang.auth', account)
        mobile = middleware.bucketGet('mrconli.taikang.mobile', account)
        auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        username = f"{account}"
        account_list += f"\n[{i}] {mobile}\n    {auth_status}"
        if auth and auth > today:
            account_list += f"\n    授权到期: {auth}"
    account_list += "\n------------------\n回复数字选择账号\n回复'q'退出"

    sender.reply(account_list)
    choice = sender.listen(60000)

    # 处理用户选择
    if not choice:
        sender.reply("❌ 操作超时")
        return
    elif choice == 'q':
        sender.reply("✅ 已取消操作")
        return

    try:
        if choice == '01':
            # 删除全部账号逻辑
            accounts_copy = accounts.copy()
            for account in accounts:
                delete_account(account)
            middleware.bucketSet('mrconli.taikang.user', userid, '[]')
            sender.reply("✅ 已删除全部账号")

        elif choice == '00':
            # 批量授权逻辑
            sender.reply("请输入授权天数:")
            days = sender.listen(60000)
            if not days:
                sender.reply("❌ 操作超时")
                return
            elif days == 'q':
                sender.reply("✅ 已取消授权")
                return
            # 新增配置获取（修复积分显示问题）
            coin_bucket = middleware.bucketGet('mrconli.taikang', 'coin_bucket') or 'dd_sign_points'
            coin_price = int(middleware.bucketGet('mrconli.taikang', 'coin') or '0')  # 确保获取最新积分价格

            try:
                days = int(days)
                if days <= 0:
                    raise ValueError("天数必须大于0")

                # 支付方式选择
                pay_choice = '1'
                if coin_price > 0:
                    user_coin = Decimal(middleware.bucketGet('coin_bucket', userid) or '0')
                    auth_guide = f"""
=====批量授权方式=====
[1] 微信支付
[2] 积分支付 (当前积分: {user_coin})
--------------------
💰 积分比例: {coin_price}积分/月
回复数字选择方式"""
                    sender.reply(auth_guide)
                    pay_choice = sender.listen(60000)
                    if pay_choice not in ['1', '2']:
                        sender.reply("❌ 无效的支付方式")
                        return

                # 微信支付处理
                if pay_choice == '1':
                    amount = price * (Decimal(days) / 30) * len(accounts)
                    amount = amount.quantize(Decimal('0.01'), rounding='ROUND_UP')
                    if process_payment(amount, days):
                        success_count = 0
                        for account in accounts:
                            auth_time = calculate_auth_time(account, days / 30)
                            middleware.bucketSet('mrconli.taikang.auth', account, auth_time)
                            token = middleware.bucketGet('mrconli.taikang.token', account)
                            username = account
                            if token and username:
                                add_to_qinglong(token, account, username)

                            success_count += 1
                        sender.reply(f"""
=====批量授权成功=====
💰 支付: {amount}元
⏰ 时长: {days}天
✅ 成功: {success_count}个账号
====================""")

                # 积分支付处理
                elif pay_choice == '2':
                    coin_bucket = middleware.bucketGet('mrconli.taikang', 'coin_bucket') or 'dd_sign_points'
                    user_coin = Decimal(middleware.bucketGet(coin_bucket, userid) or '0')
                    months = days / 30
                    if months != int(months):
                        sender.reply("❌ 积分支付需整月授权")
                        return
                    months = int(months)
                    need_coin = coin_price * months * len(accounts)
                    if user_coin < need_coin:
                        sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 所需积分: {need_coin}
💵 当前积分: {user_coin}
====================""")
                        return

                    new_coin = user_coin - need_coin
                    middleware.bucketSet(coin_bucket, userid, str(new_coin))
                    success_count = 0
                    for account in accounts:
                        auth_time = calculate_auth_time(account, months)
                        middleware.bucketSet('mrconli.taikang.auth', account, auth_time)
                        token = middleware.bucketGet('mrconli.taikang.token', account)
                        username = account
                        if token and username:
                            add_to_qinglong(token, account, username)

                        success_count += 1
                    sender.reply(f"""
=====批量授权成功=====
💰 消耗: {need_coin}积分
⏰ 时长: {days}天
✅ 成功: {success_count}个账号
💵 剩余: {new_coin}积分
====================""")

                # 更新青龙状态
                for account in accounts:
                    env_id_str = middleware.bucketGet('mrconli.taikang.env_id', account)
                    if env_id_str:
                        env_ids = json.loads(env_id_str)
                        enable_in_qinglong(env_ids)

            except ValueError as ve:
                sender.reply(f"❌ 无效的输入: {str(ve)}")
            except Exception as e:
                sender.reply(f"❌ 批量授权失败: {str(e)}")

        else:
            # 单个账号操作
            index = int(choice) - 1
            if 0 <= index < len(accounts):
                show_account_menu(accounts[index])
            else:
                sender.reply("❌ 无效的序号")

    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")


def show_account_menu(account):
    """显示账号操作菜单"""
    token = middleware.bucketGet('mrconli.taikang.token', account)
    auth = middleware.bucketGet('mrconli.taikang.auth', account)
    if len(token) == 32:
        username = f"Token...{token[-6:]}"
    else:
        username = f"{account}"
    auth_status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
    auth_info = f"\n    到期: {auth}" if auth and auth > today else ""
    menu = f"""
=====账号操作=====
📱 账号: {username[:3]}****{username[-4:]}
🔐 状态: {auth_status}{auth_info}
------------------
[1] 授权账号
[2] 删除账号
------------------
回复数字选择操作
回复"q"退出"""
    sender.reply(menu)
    choice = sender.listen(60000)
    if not choice:
        sender.reply("❌ 操作超时")
        return
    elif choice == 'q':
        sender.reply("✅ 已取消操作")
        return
    try:
        if choice == '1':
            auth_account(account)
        elif choice == '2':
            delete_account(account)
        else:
            sender.reply("❌ 无效的选择")
    except Exception as e:
        sender.reply(f"❌ 操作失败: {str(e)}")


def auth_account(account):
    """账号授权"""
    try:
        # 从配置获取积分桶名称
        coin_bucket = middleware.bucketGet('mrconli.taikang', 'coin_bucket') or 'dd_sign_points'
        user_coin = middleware.bucketGet(coin_bucket, userid) or '0'
        user_coin = Decimal(user_coin)  # 使用 Decimal 处理大数值
        month_coin = Decimal(coin_price)  # 从配置获取每月所需积分
        if month_coin <= 0:
            auth_guide = """
=====授权方式=====
[1] 微信支付
------------------
回复数字选择方式
回复"q"退出"""
        else:
            auth_guide = f"""
=====授权方式=====
[1] 微信支付
[2] 积分支付 (当前积分: {user_coin})
------------------
💰 积分比例: {month_coin}积分/月
回复数字选择方式
回复"q"退出"""
        sender.reply(auth_guide)
        choice = sender.listen(60000)
        if not choice:
            sender.reply("❌ 操作超时")
            return False
        elif choice == 'q':
            sender.reply("✅ 已取消授权")
            return False
        if choice == '1':
            sender.reply("请输入授权天数:")
            days = sender.listen(60000)
            if not days:
                sender.reply("❌ 操作超时")
                return False
            elif days == 'q':
                sender.reply("✅ 已取消授权")
                return False
            days = int(days)
            if days <= 0:
                raise ValueError()
            amount = price * (Decimal(days) / Decimal(30))
            amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding='ROUND_UP')
            if amount < Decimal('0.01'):
                amount = Decimal('0.01')
            payment_success = process_payment(amount, days)  # 处理支付
            if payment_success:  # 只有在支付成功的情况下才进行授权
                auth_time = calculate_auth_time(account, days / 30)
                middleware.bucketSet('mrconli.taikang.auth', account, auth_time)
                # 新增强制更新青龙变量逻辑
                token = middleware.bucketGet('mrconli.taikang.token', account)
                username = account  # 假设account存储的是手机号
                if token and username:
                    add_to_qinglong(token, account, username)  # 强制更新变量
                else:
                    sender.reply("⚠️ 令牌获取失败，请联系管理员")
                env_id_str = middleware.bucketGet('mrconli.taikang.env_id', account)
                if env_id_str:
                    env_ids = json.loads(env_id_str)
                    enable_in_qinglong(env_ids)
                sender.reply(f"""
=====授权成功=====
📱 账号: {account}
💰 支付: {amount}元
⏰ 时长: {days}天
📅 到期: {auth_time}
==================""")
                return True
            else:
                sender.reply("❌ 支付未成功，授权未完成")
                return False
        elif choice == '2' and month_coin > 0:  # 只有积分支付开启时才处理
            sender.reply("请输入授权月数:")
            months = sender.listen(60000)
            if not months:
                sender.reply("❌ 操作超时")
                return False
            elif months == 'q':
                sender.reply("✅ 已取消授权")
                return False
            months = int(months)
            if months <= 0:
                raise ValueError()
            need_coin = month_coin * months
            if user_coin < need_coin:
                sender.reply(f"""
=====积分不足=====
❌ 积分余额不足
------------------
💰 所需积分: {need_coin}
💵 当前积分: {user_coin}
==================""")
                return False
            new_coin = user_coin - need_coin
            middleware.bucketSet('coin_bucket', userid, str(new_coin))
            auth_time = calculate_auth_time(account, months)
            middleware.bucketSet('mrconli.taikang.auth', account, auth_time)
            token = middleware.bucketGet('mrconli.taikang.token', account)
            username = account  # 假设account存储的是手机号
            if token and username:
                add_to_qinglong(token, account, username)  # 强制更新变量
            else:
                sender.reply("⚠️ 令牌获取失败，请联系管理员")

            env_id_str = middleware.bucketGet('mrconli.taikang.env_id', account)
            if env_id_str:
                env_ids = json.loads(env_id_str)
                enable_in_qinglong(env_ids)
            sender.reply(f"""
=====授权成功=====
📱 账号: {account}
💰 消耗: {need_coin}积分
⏰ 时长: {months}月
📅 到期: {auth_time}
------------------
💵 剩余: {new_coin}积分
==================""")
            return True
        else:
            sender.reply("❌ 无效的选择")
    except ValueError:
        sender.reply("❌ 无效的数值")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")
    return False


def process_payment(amount, days):
    """处理支付"""
    zsm = middleware.bucketGet('mrconli.config', 'zsm')
    if not zsm:
        sender.reply("❌ 未配置收款码")
        return False
    zfzt = sender.atWaitPay()
    if zfzt:
        sender.reply('当前有人正在支付,请稍后再试！')
        exit(0)
    pay_msg = f"""
=====微信扫码支付====
🎫 商品: 泰康授权
📅 时长: {days}天
💰 金额: {amount}元
------------------
请使用微信扫码支付
回复"q"取消支付
=================="""
    sender.reply(pay_msg)
    sender.replyImage(zsm)
    result = sender.waitPay("q", 100000)
    if not result:
        sender.reply("❌ 支付超时")
        return False
    elif result == 'q':
        sender.reply("✅ 已取消支付")
        return False
    try:
        if isinstance(result, str):
            result = json.loads(result)
        if 'Money' in result:
            paid_amount = Decimal(str(result.get('Money', 0)))
            pay_time = result.get('Time', '')
            pay_from = ''
        else:
            paid_amount = Decimal(str(result.get('money', 0)))
            pay_time = result.get('Time', '')
            pay_from = result.get('FromName', '')
        if paid_amount >= amount:
            return True
        else:
            sender.reply(f"""
=====支付失败=====
❌ 支付金额不足
------------------
💰 应付: {amount}元
💵 实付: {paid_amount}元
==================""")
            return False
    except Exception as e:
        sender.reply(f"""
=====支付异常=====
❌ 支付验证失败
------------------
⚠️ 错误: {str(e)}
==================""")
        return False


def calculate_auth_time(account, months):
    """计算授权时间"""
    current = datetime.now().date()
    auth = middleware.bucketGet('mrconli.taikang.auth', account)
    if auth and auth > str(current):
        start = datetime.strptime(auth, "%Y-%m-%d").date()
    else:
        start = current
    days = int(months * 30)
    end = start + timedelta(days=days)
    return str(end)


def clean_expired():
    """清理过期账号"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    users = middleware.bucketAllKeys('mrconli.taikang.user')
    cleaned = 0
    for user in users:
        accounts = eval(middleware.bucketGet('mrconli.taikang.user', user) or '[]')
        valid = []
        for account in accounts:
            auth = middleware.bucketGet('mrconli.taikang.auth', account)
            if not auth or auth <= str(datetime.now().date()):
                middleware.bucketDel('mrconli.taikang.token', account)
                middleware.bucketDel('mrconli.taikang.auth', account)
                middleware.bucketDel('mrconli.taikang.env_id', account)
                cleaned += 1
            else:
                valid.append(account)
        if valid:
            middleware.bucketSet('mrconli.taikang.user', user, str(valid))
        else:
            middleware.bucketDel('mrconli.taikang.user', user)
    sender.reply(f"✅ 已清理 {cleaned} 个过期账号")


def cron_task():
    """定时任务处理"""
    if imtype != 'fake':
        return
    try:
        users = middleware.bucketAllKeys('mrconli.taikang.user')
        for user in users:
            accounts = eval(middleware.bucketGet('mrconli.taikang.user', user) or '[]')
            for account in accounts:
                try:
                    token = middleware.bucketGet('mrconli.taikang.token', account)
                    if not status:
                        continue
                    auth = middleware.bucketGet('mrconli.taikang.auth', account)
                    if auth and auth <= today:
                        env_id_str = middleware.bucketGet('mrconli.taikang.env_id', account)
                        if env_id_str:
                            env_ids = json.loads(env_id_str)
                            disable_in_qinglong(env_ids)
                        notify_user(user, account, "授权已过期,环境变量已禁用,请及时续费")
                        continue
                except Exception as e:
                    print(f"处理账号 {account} 出错: {str(e)}")
                    continue
    except Exception as e:
        print(f"定时任务出错: {str(e)}")


def notify_user(user, account, message):
    """发送用户通知"""
    try:
        notify_msg = f"""
=====账号通知=====
📱 账号: {account}
📢 消息: {message}
=================="""
        middleware.push('qq', '', user, '', notify_msg)
        middleware.push('wx', '', user, '', notify_msg)
        middleware.push('tg', '', user, '', notify_msg)
    except Exception as e:
        print(f"发送通知失败: {str(e)}")


def retry_on_error(func, retries=3, delay=1):
    """错误重试装饰器"""

    def wrapper(*args, **kwargs):
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == retries - 1:
                    raise e
                time.sleep(delay)
        return None

    return wrapper


def log_operation(operation, user, account, status, message=''):
    """记录操作日志"""
    try:
        log = {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'user': user,
            'account': account,
            'status': status,
            'message': message
        }
        logs = eval(middleware.bucketGet('mrconli.taikang.logs', 'operations') or '[]')
        logs.append(log)
        if len(logs) > 1000:  # 只保留最近1000条
            logs = logs[-1000:]
        middleware.bucketSet('mrconli.taikang.logs', 'operations', str(logs))
    except Exception as e:
        print(f"记录日志失败: {str(e)}")


def admin_auth():
    """管理员授权功能"""
    if not sender.isAdmin():
        sender.reply("❌ 需要管理员权限")
        return
    auth_menu = """
=====授权管理=====
[1] 一键授权所有用户
[2] 指定用户授权
------------------
回复数字选择功能
回复"q"退出"""
    sender.reply(auth_menu)
    choice = sender.listen(60000)
    if not choice or choice == 'q':
        return
    if choice == '1':
        auth_all_users()
    elif choice == '2':
        auth_specific_user()
    else:
        sender.reply("❌ 无效的选择")


def auth_all_users():
    """一键授权所有用户"""
    sender.reply("""
=====批量授权=====
请输入授权天数
------------------
回复数字设置天数
回复"q"退出""")
    try:
        days = sender.listen(60000)
        if not days or days == 'q':
            sender.reply("✅ 已取消授权")
            return
        days = int(days)
        if days <= 0:
            raise ValueError()
        users = middleware.bucketAllKeys('mrconli.taikang.user')
        success = 0
        failed = 0
        for user in users:
            accounts = eval(middleware.bucketGet('mrconli.taikang.user', user) or '[]')
            for account in accounts:
                try:
                    auth_time = calculate_auth_time(account, days / 30)
                    middleware.bucketSet('mrconli.taikang.auth', account, auth_time)
                    token = middleware.bucketGet('mrconli.taikang.token', account)
                    if token:
                        phone = account[:3] + '*' * 4 + account[7:]
                        add_to_qinglong(token, account, phone)
                    env_ids_str = middleware.bucketGet('mrconli.taikang.env_id', account)
                    if env_ids_str:
                        env_ids = json.loads(env_ids_str)
                        enable_in_qinglong(env_ids)
                    success += 1
                    log_operation('batch_auth', user, account, 'success')
                except Exception as e:
                    failed += 1
                    log_operation('batch_auth', user, account, 'failed', str(e))
        sender.reply(f"""
=====授权完成=====
✅ 成功: {success}个账号
❌ 失败: {failed}个账号
⏰ 授权: {days}天
==================""")
    except ValueError:
        sender.reply("❌ 无效的天数")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")


def auth_specific_user():
    """指定用户授权"""
    sender.reply("""
=====指定授权=====
请输入用户ID
(发送myuid可获取ID)
------------------
回复"q"退出""")
    user_id = sender.listen(60000)
    if not user_id or user_id == 'q':
        return
    accounts = eval(middleware.bucketGet('mrconli.taikang.user', user_id) or '[]')
    if not accounts:
        sender.reply("❌ 未找到该用户的账号")
        return
    account_list = """
=====账号列表=====
[0] 授权全部账号"""
    for i, account in enumerate(accounts, 1):
        auth = middleware.bucketGet('mrconli.taikang.auth', account)
        status = "✅ 已授权" if auth and auth > today else "❌ 未授权"
        account_list += f"\n[{i}] {account[:3]}****{account[-4:]}\n    {status}"
    account_list += """
------------------
回复数字选择账号
回复"q"退出"""
    sender.reply(account_list)
    choice = sender.listen(60000)
    if not choice or choice == 'q':
        return
    try:
        sender.reply("""
=====设置授权时间=====
请输入授权天数
------------------
回复数字设置天数
回复"q"退出""")
        days = sender.listen(60000)
        if not days or days == 'q':
            return
        days = int(days)
        if days <= 0:
            raise ValueError()
        if choice == '0':
            for account in accounts:
                try:
                    auth_time = calculate_auth_time(account, days / 30)
                    middleware.bucketSet('mrconli.taikang.auth', account, auth_time)
                    token = middleware.bucketGet('mrconli.taikang.token', account)
                    if token:
                        phone = account[:3] + '*' * 4 + account[7:]
                        add_to_qinglong(token, account, phone)
                    env_ids_str = middleware.bucketGet('mrconli.taikang.env_id', account)
                    if env_ids_str:
                        env_ids = json.loads(env_ids_str)
                        enable_in_qinglong(env_ids)
                    log_operation('auth', user_id, account, 'success')
                except Exception as e:
                    log_operation('auth', user_id, account, 'failed', str(e))
            sender.reply(f"✅ 已授权所有账号 {days}天")
        else:
            index = int(choice) - 1
            if not 0 <= index < len(accounts):
                raise ValueError()
            account = accounts[index]
            auth_time = calculate_auth_time(account, days / 30)
            middleware.bucketSet('mrconli.taikang.auth', account, auth_time)
            token = middleware.bucketGet('mrconli.taikang.token', account)
            if token:
                phone = account[:3] + '*' * 4 + account[7:]
                add_to_qinglong(token, account, phone)
            env_ids_str = middleware.bucketGet('mrconli.taikang.env_id', account)
            if env_ids_str:
                env_ids = json.loads(env_ids_str)
                enable_in_qinglong(env_ids)
            sender.reply(f"""
=====授权成功=====
📱 账号: {account}
⏰ 时长: {days}天
📅 到期: {auth_time}
==================""")
            log_operation('auth', user_id, account, 'success')
    except ValueError:
        sender.reply("❌ 无效的输入")
    except Exception as e:
        sender.reply(f"❌ 授权失败: {str(e)}")
        log_operation('auth', user_id, account, 'failed', str(e))


def check_account_status(self, token):
    """检查账号状态"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = {
        "service": "media",
        "api": "lottery/queryActivityAwardRecordList",
        "data": {
            "uid": "30a7f9016d224fc2a8367200cbbab62a",
            "content": "null"}
    }
    response = _send_request(
        'POST',
        "https://app.eyh.cn/gateway/api",
        json=data,
        headers=headers
    )
    return response


def delete_account(account):
    """删除账号"""
    try:
        if not delete_from_qinglong(account):
            raise Exception("从青龙删除变量失败")
        middleware.bucketDel('mrconli.taikang.token', account)
        middleware.bucketDel('mrconli.taikang.auth', account)
        middleware.bucketDel('mrconli.taikang.env_id', account)
        # 安全解析用户列表
        try:
            accounts = json.loads(str(uservalue)) if uservalue else []
        except (json.JSONDecodeError, TypeError) as e:
            print(f"用户列表解析失败: {str(e)}")
            accounts = []
        
        # 校验账号存在性并更新
        if account in accounts:
            accounts.remove(account)
            try:
                middleware.bucketSet('mrconli.taikang.user', userid, json.dumps(accounts, ensure_ascii=False))
            except Exception as e:
                raise Exception(f"用户列表更新失败: {str(e)}")
        sender.reply(f"""
=====删除成功=====
📱 账号: {account}
✅ 状态: 已删除
==================""")
        log_operation('delete_account', userid, account, 'success')
        return True
    except Exception as e:
        error_msg = f"删除账号失败: {str(e)}"
        sender.reply(f"❌ {error_msg}")
        log_operation('delete_account', userid, account, 'failed', str(e))
        return False


async def async_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()


@lru_cache(maxsize=100)
def cached_bucket_get(bucket, key):
    return middleware.bucketGet(bucket, key)


async def async_login():
    token = await async_request("https://app.eyh.cn/gateway/api", login_data)
    if token:
        await async_add_to_qinglong(token)


def tutorial():
    """显示泰康使用教程"""
    tutorial_text = (
        "=====泰康教程=====\n"
        "🌟 基础指令:\n"
        "1. 泰康登录 - 绑定账号\n"
        "2. 泰康查询 - 查看状态\n"
        "3. 泰康管理 - 管理账号\n"
        "4. 泰康授权 - 管理员授权账号\n"
        "4. 泰康清理 - 管理员清理过期\n"
        "-------------------\n"
        "🚩 收益说明:\n"
        "▸ 呆瓜为每日自动运行签到\n"
        "▸ 每礼拜可领一个低保0.3红包\n"
        "▸ 需要实名、绑定微信\n"
        "-------------------\n"
        "⚠️ 注意事项:\n"
        "1. 建议私聊登录更安全\n"
        "2. 需要手动提现\n"
        "=================="
    )
    sender.reply(tutorial_text)


def main():
    """主函数"""
    message = sender.getMessage()
    if '登录' in message:
        bind()
    elif '管理' in message:
        manage_accounts()
    elif '查询' in message:
        query()
    elif '教程' in message:
        tutorial()
    elif message == '泰康清理':
        clean_expired()
    elif message == '泰康授权' and sender.isAdmin():
        admin_auth()
    else:
        sender.setContinue()


if __name__ == "__main__":
    try:
        var_name, ql_host, ql_client_id, ql_client_secret, manage_cmd, query_cmd, login_cmd, price, coin_price = get_config()
        ql_url, ql_token = init_qinglong()
        imtype = sender.getImtype()
        today = str(datetime.now().date())
        if imtype == 'fake':
            cron_task()
        else:
            main()
    except Exception as e:
        sender.reply(f"❌ 运行出错: {str(e)}")
