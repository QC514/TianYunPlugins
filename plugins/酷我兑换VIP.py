#[pin:false]
#[disable:true]
#[public:true]
#[rule: ^酷我兑换$]
#[version: 1.1]
#[title: 酷我兑换VIP]
#[author: sky2022]
#[admin: false]
#[icon: https://img.cdn1.vip/i/69d62b975e88c_1775643543.png]
#[price: 6.88]
#[description: 指令:酷我兑换 手机号#密码登陆，用于兑换酷我VIP会员]
import requests
import base64
import json
import time
import uuid
import random
from datetime import datetime
import middleware

# Get sender object
senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)

# 配置项
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 1  # 重试延迟(秒)
MAX_EXCHANGE_TIMES = 5  # 每日最大兑换次数

def recognize_captcha(image_base64: str) -> str:
    """使用远程ddddocr接口进行验证码识别"""
    try:
        ocr_url = 'https://ddddor.linzixuan.top/classification'
        
        # 移除base64头部信息
        if ',' in image_base64:
            image_base64 = image_base64.split(',')[1]
        image_base64 = image_base64.replace('data:image/jpeg;base64,', '')
        image_base64 = image_base64.replace('data:image/png;base64,', '')
        
        data = {'image': image_base64}
        
        response = requests.post(
            ocr_url,
            json=data,
            timeout=10
        )
        
        result = response.json()
        if not result or 'result' not in result:
            raise Exception("验证码识别失败: 返回结果无效")
            
        return result['result'].strip()
        
    except Exception as e:
        print(f"验证码识别出错: {str(e)}")
        raise

def login(phone: str, password: str):
    """登录酷我账号"""
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            # 获取验证码
            captcha_url = 'http://www.kuwo.cn/api/common/captcha/getcode'
            captcha_params = {
                'reqId': str(uuid.uuid4()),
                'httpsStatus': '1'
            }
            
            captcha_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Encoding': 'gzip, deflate',
                'Content-Type': 'application/json',
                'Referer': 'http://www.kuwo.cn/',
                'Accept-Language': 'zh-CN,zh;q=0.9'
            }
            
            response = requests.get(
                captcha_url,
                params=captcha_params,
                headers=captcha_headers
            )
            
            if 'data' not in response.json():
                retry_count += 1
                print(f"[重试] 获取验证码失败，第{retry_count}次重试...")
                time.sleep(RETRY_DELAY)
                continue
                
            captcha_data = response.json()['data']
            image_data = captcha_data['img']
            token = captcha_data['token']
            
            verify_code = recognize_captcha(
                image_data.replace('data:image/jpeg;base64,', '')
            )
            
            if not verify_code:
                retry_count += 1
                print(f"[重试] 验证码识别失败，第{retry_count}次重试...")
                time.sleep(RETRY_DELAY)
                continue
            
            # 执行登录
            login_url = 'https://wapi.kuwo.cn/api/www/login/loginByKw'
            login_data = json.dumps({
                'userIp': 'www.kuwo.cn',
                'uname': phone,
                'password': password,
                'verifyCode': verify_code,
                'img': image_data,
                'verifyCodeToken': token
            })
            
            login_headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.95 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json',
                'Origin': 'http://www.kuwo.cn',
                'Referer': 'http://www.kuwo.cn/',
                'Accept-Language': 'zh-CN,zh;q=0.9'
            }
            
            login_response = requests.post(
                login_url,
                params={'httpsStatus': '1'},
                data=login_data,
                headers=login_headers,
                timeout=10
            )
            
            result = login_response.json()
            
            if result.get('code') != 200:
                error_msg = result.get('msg', '未知错误')
                if "picture captcha error" in error_msg or "验证码错误" in error_msg:
                    retry_count += 1
                    print(f"[重试] 验证码错误，第{retry_count}次重试...")
                    time.sleep(RETRY_DELAY)
                    continue
                raise Exception(f"登录失败: {error_msg}")
            
            # 获取登录信息
            data = result['data']
            cookies = data['cookies']

            loginSid = cookies.get('websid')
            loginUid = cookies.get('userid')
            appUid = ''.join(random.choices('0123456789', k=10))

            return loginUid, loginSid, appUid
            
        except Exception as e:
            if retry_count < MAX_RETRIES - 1:
                retry_count += 1
                print(f"[重试] 登录失败，第{retry_count}次重试: {str(e)}")
                time.sleep(RETRY_DELAY)
                continue
            raise Exception(f"登录失败: {str(e)}")
    
    raise Exception("登录重试次数已用完")

def exchange_vip(loginUid: str, loginSid: str, appUid: str) -> bool:
    """兑换VIP"""
    url = "https://integralapi.kuwo.cn/api/v1/online/sign/getExchangeAward"
    params = {
        'loginUid': loginUid,
        'loginSid': loginSid,
        'appUid': appUid,
        'platform': 'ar',
        'source': 'kwplayer_ar_11.1.4.1_hw.apk',
        'version': '11.1.4.1',
        'quotaId': '13',
        'exchangeType': 'vip',
    }

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 14; POCO F2 Pro Build/UQ1A.240105.004; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/121.0.6167.101 Mobile Safari/537.36/ kuwopage',
        'Origin': 'https://h5app.kuwo.cn',
        'X-Requested-With': 'cn.kuwo.player',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7'
    }

    try:
        response = requests.get(url, params=params, headers=headers)
        r_json = response.json()
        if '成功' in response.text:
            sender.reply(f'✅ 账号 {loginUid} 已成功兑换1个月酷我VIP')
            return True
        else:
            description = r_json['data'].get('description', '未知错误')
            sender.reply(f'❌ 账号 {loginUid} {description}')
            return False
            
    except Exception as e:
        sender.reply(f'❌ 账号 {loginUid} 兑换VIP失败: {str(e)}')
        return False

def main():
    """主函数"""
    try:
        # 获取登录信息
        sender.reply(
            "=====酷我兑换VIP=====\n"
            "📝 请输入账号信息:\n"
            "格式: 手机号#密码\n"
            "⚠️ 建议私聊操作\n"
            "⭐ 输入q退出操作\n"
            "==================="
        )
        
        login_info = sender.input(120000, 1, False)
        if not login_info:
            sender.reply('输入超时！')
            return
        elif login_info.lower() == 'q':
            sender.reply('已取消操作')
            return
            
        # 解析登录信息
        try:
            phone, password = login_info.split('#')
            if len(phone) != 11:
                sender.reply('手机号格式错误')
                return
        except:
            sender.reply('输入格式错误！需要手机号#密码格式')
            return
            
        # 登录账号
        try:
            loginUid, loginSid, appUid = login(phone, password)
        except Exception as e:
            sender.reply(f"登录失败: {str(e)}")
            return
            
        # 获取兑换次数
        sender.reply(
            "=====兑换设置=====\n"
            "📝 请输入兑换次数(1-5):\n"
            "⚠️ 每日最多兑换5次\n"
            "⭐ 输入q退出操作\n"
            "==================="
        )
        
        exchange_times = sender.input(60000, 1, False)
        if not exchange_times:
            sender.reply('输入超时！')
            return
        elif exchange_times.lower() == 'q':
            sender.reply('已取消操作')
            return
            
        try:
            exchange_times = int(exchange_times)
            if exchange_times < 1 or exchange_times > MAX_EXCHANGE_TIMES:
                sender.reply(f'兑换次数必须在1-{MAX_EXCHANGE_TIMES}之间')
                return
        except:
            sender.reply('兑换次数必须是数字')
            return
            
        # 执行兑换
        for i in range(exchange_times):
            try:
                exchange_vip(loginUid, loginSid, appUid)
                time.sleep(1)  # 添加延迟避免请求过快
            except Exception as e:
                sender.reply(f"❌ 兑换出错: {str(e)}")
                
    except Exception as e:
        sender.reply(f"操作失败: {str(e)}")

# 执行主函数
main() 