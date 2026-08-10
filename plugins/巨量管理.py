#[author: chuan]
#[version: 2.1.0]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg]
#[title: 巨量管理]
#[price: 0]
#[service: 2669943482]
#[priority: 999]
#[public: true] 
#[description: 更新：增加重试。更新：修复签到，巨量签到增加管理员通知，请到配参填写，增加查询余额(查询token余额)，增加巨量签到，对接的第三方打码服务，需要自行购买token(http://www.gxfc-s4.com/)，应该是最后一个版本了。命令：ip，剩余ip，巨量加白，巨量账号管理，生成api(暂仅支持生成数量1)，查询余额，巨量签到。巨量多账号管理插件，支持账号密码登陆，只支持签到送的免费套餐（因为我只有这一个套餐），需要安装依赖requests。巨量加白可以设置定时指令，5分钟一次，巨量签到类似。]
#[disable:false] 
#[admin: true]
#[rule: ^ip$]
#[rule: ^剩余ip$]
#[rule: ^巨量账号管理$]
#[rule: ^巨量加白$]
#[rule: ^生成api$]
#[rule: ^巨量余额$]
#[rule: ^巨量签到$]
#[param: {"required":true,"key":"otto.jl_imtypes","bool":false,"placeholder":"管理员通知","name":"jl_imtypes","desc":"巨量签到通知平台，多个用,隔开，例如qq,wb"}]
#[param: {"required":true,"key":"otto.jl_token","bool":false,"placeholder":"签到过滑块token","name":"jl_token","desc":"请前往http://www.gxfc-s4.com购买token"}]


import re
import sys
import json
import requests
import random
import hashlib
import middleware
from urllib.parse import quote_plus

#获取当前ip
def current_ip():
    # proxies = {
    #     "http": "http://192.168.1.5:9090",
    #     "https": "http://192.168.1.5:9090",
    # }
    html = requests.get('https://ddns.oray.com/checkip')
    currentIp = re.findall( r'[0-9]+(?:\.[0-9]+){3}',html.text)[0]
    return currentIp

#随机ua
def get_ua():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)', '(X11; Linux x86_64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = 'Chrome/{}.0.{}.{}'.format(first_num, third_num, fourth_num)

    ua = ' '.join(['Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
                   '(KHTML, like Gecko)', chrome_version, 'Safari/537.36']
                  )
    return ua

#登录
def login(username,password,ua):
    try:
        url = f'https://www.juliangip.com/login/go?type=password&username={username}&password={password}&sms_code='
        headers = {
            'user-agent': ua,
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
            }
        res = requests.post(url,headers=headers)
        if res.json()['state'] == 'ok':
            print('登陆成功')
            return res.headers['Set-Cookie']
    except:
        return

def get_info(ck,ua):
    url = 'https://www.juliangip.com/users/'
    headers = {
        'Connection': 'keep-alive',
        'cookie': ck,
        'user-agent': ua,
        'content-type': 'application/json;charset=UTF-8'
    }
    res = requests.get(url,headers=headers)
    return res.text

#获取商品列表
def goods(ck,ua):
    url = 'https://www.juliangip.com/order/list'
    headers = {
        'Connection': 'keep-alive',
        'cookie': ck,
        'user-agent': ua,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    res = requests.post(url,headers=headers).json()
    return res

#获取订单详情
def getkey(ck,order,ua):
    url = f'https://www.juliangip.com/order/info?trade_no={order}'
    headers = {
        'Connection': 'keep-alive',
        'cookie': ck,
        'user-agent': ua,
        'content-type': 'application/json;charset=UTF-8'
    }
    res = requests.get(url,headers=headers).json()
    if res['code'] == 100000:
        return res['data']['key']

#更换ip
def change(ip,order,ck,ua):
    url = f'https://www.juliangip.com/users/product/time/setWhiteIp?trade_no={order}&ips={ip}'
    headers = {
        'Connection': 'keep-alive',
        'cookie': ck,
        'user-agent': ua,
        'content-type': 'application/json;charset=UTF-8'
    }
    res = requests.get(url,headers=headers).json()
    return res

#账户详情
def account(order,key,ck,ua):
    api = f'trade_no={order}&key={key}'
    md5 = hashlib.md5()	
    md5.update(api.encode('utf-8'))
    sign = md5.hexdigest()
    url = f'http://v2.api.juliangip.com/dynamic/balance?trade_no={order}&sign={sign}'
    headers = {
        'Connection': 'keep-alive',
        'cookie': ck,
        'user-agent': ua,
        'content-type': 'application/json;charset=UTF-8'
    }
    res = requests.get(url,headers=headers).json()
    return res

#生成api
def get_api(trade_no,key):
    api = f'auto_white=1&num=1&pt=1&result_type=text&split=2&trade_no={trade_no}&key={key}'
    md5 = hashlib.md5()	
    md5.update(api.encode('utf-8'))
    sign = md5.hexdigest()
    url = f'http://v2.api.juliangip.com/dynamic/getips?auto_white=1&num=1&pt=1&result_type=text&split=2&trade_no={trade_no}&sign={sign}'
    return url

def assign(randStr,ticket,ck,ua):
    url = 'https://www.juliangip.com/users/getFree'
    headers = {
        'Connection': 'keep-alive',
        'cookie': ck,
        'user-agent': ua,
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    data = f'randStr={quote_plus(randStr)}&ticket={ticket}'
    print(data)
    res = requests.post(url,headers=headers,data=data).json()
    return res.get('message')

def start_sign(user_info,token,ck,ua,username,trys=0):
    try:
        print('去签到')
        # 获取aid
        aid = re.findall(r"TencentCaptcha\('(.*?)',function\(res\)", user_info)[0]
        print(f'获取到aid：{aid}')
        randstr,ticket = get_ticket(aid,token)
        if randstr and ticket:
            res = assign(randstr,ticket,ck,ua)
            middleware.notifyMasters(f'【账号{username}】{res}',imtypes)
        else:
            res = '滑块失败'
            if trys > 3:
                middleware.notifyMasters(f'【账号{username}】重试次数用尽，签到失败',imtypes)
            else:
                trys += 1
                middleware.notifyMasters(f'【账号{username}】开始{trys}次重试',imtypes)
                return start_sign(user_info,token,ck,ua,username,trys)
    except:
        if trys > 3:
            middleware.notifyMasters(f'【账号{username}】重试次数用尽，签到失败',imtypes)
        else:
            trys += 1
            middleware.notifyMasters(f'【账号{username}】开始{trys}次重试',imtypes)
            return start_sign(user_info,token,ck,ua,username,trys)

def query_token(token):
    try:
        url = 'http://119.96.239.11:8888/api/getuserinformation'
        headers = {'Content-Type': 'application/json'}
        body = {'token': token}
        res = requests.post(url,headers=headers,json=body).json()
        token_num = res.get('data').get('余额')
        return f'当前余额：{token_num}积分'
    except:
        return '查询失败'

def get_ticket(appid,token):
    try:
        url = 'http://119.96.239.11:8888/api/getcode'
        headers = {'Content-Type': 'application/json'}
        body = {
            "timeout": "60", 
            "type": "tencent-turing", 
            "appid": appid, 
            "token": token, 
            "developeraccount": ""
        }
        res = requests.post(url,headers=headers,json=body,timeout=61).json()
        data = json.loads(res.get('data').get('code','{}'))
        print(data)
        randstr = data.get('randstr')
        ticket = data.get('ticket')
        return randstr,ticket
    except:
        return

def main():
    # 先去桶子查询账号数据
    username_list = middleware.bucketAllKeys(bucket)
    if msg == '剩余ip':
        if  username_list:
            pass
        else:
            sender.reply('暂无账号，先发送巨量账号管理添加账号吧')
            return
        
        sender.reply('开始查询，请稍后...')
        for username in username_list:
            ua = get_ua()
            password = middleware.bucketGet(bucket,username)
            ck = login(username,password,ua)
            if ck:
                order = goods(ck,ua)
                if order['state'] == 'ok':
                    order = order['data'][0]['children']
                    if order:
                        order = order[0]['value']
                        key = getkey(ck,order,ua)
                        res = account(order,key,ck,ua)
                        if res['code'] == 200:
                            balance = res['data']['balance']
                            sender.reply(f'【账号{username}】剩余{balance}ip可用')
                        else:
                            sender.reply(f'【账号{username}】{res["msg"]}')
                    else:
                        sender.reply('没有可用免费套餐!')
                else:
                    sender.reply('获取套餐失败')      
            else:
                sender.reply(f'账号{username}  登陆失败')
    elif msg == '巨量账号管理':
        send_msg = '请在60s内回复(q:退出，-:删除，0:添加):\n'

        if  username_list:
            index = 0
            for username in username_list:
                index += 1
                password = middleware.bucketGet(bucket,username)
                send_msg += f'{index}. {username}\n'
            
        sender.reply(send_msg)
        user_msg = sender.listen(60*1000)
        if 'q' == user_msg:
            sender.reply('退出')
            return
        elif '0' == user_msg:
            sender.reply(f'请60s内输入账号(q退出):')
            username = sender.listen(60*1000)
            if username == 'error' or username == 'q':
                sender.reply('退出')
                return
            
            sender.reply(f'请60s内输入密码(q退出):')
            password = sender.listen(60*1000)
            if password == 'error' or password == 'q':
                sender.reply('退出')
                return
            # 检测账号
            ck = login(username,password,get_ua())
            if ck:
                middleware.bucketSet(bucket,username,password)
                sender.reply('账号有效，添加成功')
            else:
                sender.reply('账号无效或输入错误，退出')
                return
        elif user_msg in [f'-{i+1}' for i in range(len(username_list))]:
            num = user_msg.split('-')[1]
            del_data = username_list[int(num)-1]
            middleware.bucketDel(bucket,del_data)
            sender.reply(f'{del_data}删除成功')
        else:
            sender.reply('输入错误，退出')

    elif msg == '巨量加白':
        if  username_list:
            pass
        else:
            sender.reply('暂无账号，先发送巨量账号管理添加账号吧')
            return
        
        sender.reply('开始执行，请稍后...')
        now_ip = current_ip()
        sender.reply(f'当前ip：{now_ip}')
        for username in username_list:
            ua = get_ua()
            password = middleware.bucketGet(bucket,username)
            ck = login(username,password,ua)
            if ck:
                order = goods(ck,ua)
                if order['state'] == 'ok':
                    order = order['data'][0]['children']
                    if order:
                        order = order[0]['value']
                        res = change(now_ip,order,ck,ua)
                        if res['state'] == 'ok':
                            sender.reply(f'【账号{username}】加白成功')
                        else:
                            sender.reply(f'【账号{username}】{res["message"]}')
                    else:
                        sender.reply(f'【账号{username}】没有可用免费套餐!')
                else:
                    sender.reply(f'【账号{username}】获取套餐失败')
            else:
                sender.reply(f'【账号{username}】登陆失败')
    elif msg == 'ip':
        now_ip = current_ip()
        sender.reply(f'当前ip：{now_ip}')
    
    elif msg == '生成api':
        if  username_list:
            pass
        else:
            sender.reply('暂无账号，先发送巨量账号管理添加账号吧')
            return
        
        sender.reply('开始生成，请稍后...')
        for username in username_list:
            ua = get_ua()
            password = middleware.bucketGet(bucket,username)
            ck = login(username,password,ua)
            if ck:
                order = goods(ck,ua)
                if order['state'] == 'ok':
                    order = order['data'][0]['children']
                    if order:
                        order = order[0]['value']
                        key = getkey(ck,order,ua)
                        api = get_api(order,key)
                        sender.reply(f'【账号{username}】\n提取api：{api}')
                    else:
                        sender.reply(f'【账号{username}】没有可用免费套餐!')
                else:
                    sender.reply(f'【账号{username}】获取套餐失败')
            else:
                sender.reply(f'【账号{username}】登陆失败')
    elif msg == '巨量余额':
        # 获取token
        token = middleware.get('jl_token')
        if not token:
            sender.reply(f'未设置token，请前往http://www.gxfc-s4.com/r购买\n发送set otto jl_token xxxxxx')
            sys.exit()
        res = query_token(token)
        sender.reply(res)
    elif msg == '巨量签到':
        # 获取token
        token = middleware.get('jl_token')
        if not token:
            middleware.notifyMasters(f'请前往http://www.gxfc-s4.com购买token\n发送set otto jl_token xxxxxx',imtypes)
            sys.exit()

        if  username_list:
            pass
        else:
            middleware.notifyMasters('暂无账号，先发送巨量账号管理添加账号吧',imtypes)
            return
        
        middleware.notifyMasters('开始签到，请稍后...',imtypes)
        for username in username_list:
            ua = get_ua()
            password = middleware.bucketGet(bucket,username)
            ck = login(username,password,ua)
            if ck:
                # 判断签到
                user_info = get_info(ck,ua)
                if '点击领取今日免费IP' in user_info:
                    start_sign(user_info,token,ck,ua,username)
                elif '您已成功领取' in user_info:
                    middleware.notifyMasters(f'【账号{username}】今日已签到',imtypes)
            else:
                middleware.notifyMasters(f'【账号{username}】登陆失败，建议换ip重试',imtypes)

if __name__ == "__main__":
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    msg = sender.getMessage()
    bucket = 'jl_data'
    imtypes = middleware.get('jl_imtypes')
    if not imtypes:
        sender.reply(f'未设置管理员通知，请前往配参填写')
        sys.exit()
    imtypes = imtypes.split(',')
    main()
