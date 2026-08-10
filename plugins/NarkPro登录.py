# [author: chuan]
# [version: 1.4.1]
# [class: 工具类]
# [platform: qq,qb,wx,tb,tg]
# [title: NarkPro登录]
# [description: 指令：登录。<br/>介绍：对接京东narkpro的登陆插件，支持短信，扫码，口令，账密（需要安装账密插件），具体参数请查看配参。<br/>注意事项：使用口令登录请先安装JD通用sign插件<br/>适配ark账密,增加”一键迁移pro“指令]
# [price: 0]
# [service: 2669943482]
# [priority: 999]
# [public:true] 
# [disable:false]
# [admin: false]
# [rule: ?]
# [bypass: true]

# [param: {"required":true,"key":"chuan_narkpro_login_config.mainRules","placeholder":"","name":"总关键词","desc":"这里填的关键词将会触发选择选项，让用户自行选择登陆方式。多个关键词用逗号隔开"}]
# [param: {"required":true,"key":"chuan_narkpro_login_config.nark_url","placeholder":"","name":"NarkPro地址","desc":"http://ip:prot"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.selectingReply","placeholder":"","name":"登陆选择的尾巴","desc":""}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.loginedReply","placeholder":"","name":"登陆成功的提示","desc":""}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.smsCheckbox","placeholder":"","bool":true,"name":"短信登录","desc":"是否开启短信登录"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.smsRules","placeholder":"","name":"短信登陆关键词","desc":"多个关键词用逗号隔开"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.smsexplain","placeholder":"","name":"短信登陆说明","desc":""}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.qrCheckbox","placeholder":"","bool":true,"name":"扫码登录","desc":"是否开启扫码登录"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.qrRules","placeholder":"","name":"扫码登陆关键词","desc":"多个关键词用逗号隔开"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.qrexplain","placeholder":"","name":"扫码登陆说明","desc":""}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.keyCheckbox","placeholder":"","bool":true,"name":"口令登录","desc":"是否开启口令登录"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.keyRules","placeholder":"","name":"口令登陆关键词","desc":"多个关键词用逗号隔开"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.keyexplain","placeholder":"","name":"口令登陆说明","desc":""}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.sign_api","placeholder":"","name":"JD通用sign插件接口","desc":"http://奥特曼地址/jd/sign"}]
# [param: {"spliter":true}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.zmCheckbox","placeholder":"","bool":true,"name":"账密登录","desc":"是否开启账密登录，需要安装JD账密登录插件"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.zmRules","placeholder":"","name":"账密登陆关键词","desc":"不要填账密登录，会跟账密插件冲突。多个关键词用逗号隔开"}]
# [param: {"required":false,"key":"chuan_narkpro_login_config.zmexplain","placeholder":"","name":"账密登陆说明","desc":""}]


import re
import json
import requests
import middleware
from datetime import datetime,timedelta
from urllib.parse import quote_plus,unquote_plus
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64

key = b'chuan66666666666'
iv = b'chuan66666666666'

# 初始化配置
bucket = 'chuan_narkpro_login_config'

# 短信配置
smsTips = '短信服务在线！请输入11位手机号：\n（输入“q”即可退出会话）'
smsTips_success = '验证码已发送，请输入6位验证码：\n（输入“q”即可退出会话）'
smsTips_fail = '验证码发送失败，请联系管理员'

def decrypt_password(encrypted_password):
    encrypted_data = base64.b64decode(encrypted_password)
    iv = encrypted_data[:AES.block_size]
    ciphertext = encrypted_data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_password = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_password.decode('utf-8')

# 检查手机号
def checkModbile(mobile):
    re_pattern = r'^1[3,4,5,6,7,8,9][0-9]{9}$'
    result = re.match(re_pattern, mobile)
    if not result:
        return False # 若手机号码格式不正确则返回False
    return True

# 检查验证码
def checkCode(code):
    re_pattern = r'^[0-9]{6}$'
    result = re.match(re_pattern, code)
    if not result:
        return False  # 若验证码格式不正确则返回False
    return True

# 检测用以验证的身份证号码组成
def checkIDCardCode(code):
    re_pattern = r'^\d{5}[0-9xX]$'
    result = re.match(re_pattern, code)
    if not result:
        return False  # 若身份证号码格式不正确则返回False
    return True

# 生成二维码直链
def getQrKeyUrl(qrContent):
    try:
        return 'https://tools.aijiaoer.cn:16666/api/qrcode?data=' + quote_plus(qrContent)
    except:
        return

def get_ts():
    one_month_later = datetime.now() + timedelta(days=30)
    return int(one_month_later.timestamp() * 1000)

def get_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_sign(fn,body):
    body = {
        'fn': fn,
        'body': body
    }
    res = requests.post(middleware.bucketGet(bucket,'sign_api'),json=body).json() 
    return res

# 生成口令
def jCommand(url):
    body= {
        "appCode": "jApp",
        "command":{
            "keyChannel": "Wxfriends",
            "keyContent": "复制口令，打开京东APP",
            "keyEndTime": get_ts(),
            "keyId": '888888888888',
            "keyImg": "https://m.360buyimg.com/mobile/jfs/t1/16766/15/17658/955/61d55739E2f54d067/10199685f7bd09e3.png",
            "keyTitle": "请完成登录操作",
            "sourceCode": "babel",
            "url": url
            }
        }
    params = get_sign('jCommand',body)['body']
    url = 'https://api.m.jd.com/client.action?functionId=jCommand&' + params
    headers = {
        "Host":"api.m.jd.com",
        "Content-Type": "application/x-www-form-urlencoded",
        'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    }
    data = f'body={quote_plus(json.dumps(body))}'
    res = requests.post(url,headers=headers,data=data).json()
    if res.get('code') == '0':
        return res.get('data')

# 登录成功回复
def loginednotice(username, type):
    middleware.bucketSet('pin' + imtype.upper(),username,sender_id)
    sender.bucketDel('jdNotify', username)
    sender.reply(unquote_plus(username) + '登录成功。\n' + middleware.bucketGet(bucket,'loginedReply'))
    middleware.notifyMasters(f'======JD登陆通知======\n[登陆用户]：{sender_id}\n[登陆平台]：{imtype}\n[登陆账户]：{unquote_plus(username)}\n[登陆方式]：{type}\n[登陆时间]：{get_now()}')

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

def main_sms():
    sender.reply(smsTips)
    phone = sender.input(60*1000,3*1000,False)
    if phone == 'q' or phone == 'Q':
        sender.reply('退出成功')
        return
    
    if phone is None:
        sender.reply('输入超时，自动退出程序')
        return

    if checkModbile(phone) == False:
        sender.reply('输入错误，自动退出程序')
        return
    
    # 发送验证码
    sender.reply('正在发送验证码，请稍等')
    sendSMSMsg = pro.sendsms(phone)
    if sendSMSMsg.get('success') == False:
        sender.reply('发送验证码失败，自动退出程序')
        return
    
    sender.reply('验证码已发送，请输入6位验证码：\n（输入“q”即可退出会话）')
    code = sender.input(240*1000,3*1000,False)
    if code == 'q' or code == 'Q':
        sender.reply('退出成功')
        return
    
    if code is None:
        sender.reply('输入超时，自动退出程序')
        return

    if checkCode(code) == False:
        sender.reply('输入错误，自动退出程序')
        return
    
    # 请求登录
    verifyCodeMsg = pro.VerifyCode(phone,code)
    if verifyCodeMsg.get('success') == True: # 登陆成功
        username = verifyCodeMsg.get('data').get('username')
        loginednotice(username, '短信')
        return verifyCodeMsg.get('data').get('accessToken')

    # 风控
    if verifyCodeMsg.get('success') == False and verifyCodeMsg.get('message') == '您的账号存在风险，为了您的账号安全请到京东商城App登录':
        sender.reply('您的账号存在风险，无法使用短信登录，请尝试扫码登录')
        return

    # 出验证了
    if verifyCodeMsg.get('success') == False and verifyCodeMsg.get('data').get('status') == 555:
        sender.reply('帐号触发安全验证，请输入前两位和最后四位身份证号码')
        code = sender.input(60*1000,0,False)
        if code == 'q' or code == 'Q':
            sender.reply('退出成功')
            return
        
        if code is None:
            sender.reply('输入超时，自动退出程序')
            return

        if checkIDCardCode(code) == False:
            sender.reply('输入错误，自动退出程序')
            return
        sender.reply('验证中，请稍等')
        VerifyCardMsg = pro.VerifyCard(phone,code)
        if VerifyCardMsg.get('success') == True: # 登陆成功
            username = verifyCodeMsg.get('data').get('username')
            loginednotice(username, '短信')
            return verifyCodeMsg.get('data').get('accessToken')
        sender.reply(VerifyCardMsg.get('message') + '登录失败，请稍后再试')
    
    # 登录失败，返回pro返回的message提示
    sender.reply(verifyCodeMsg.get('message'))

def main_qr():
    sender.reply('请稍等，获取服务器配置中')
    qrKeyData = pro.getQrKey()

    if qrKeyData is None:
        sender.reply('获取二维码配置失败')
        return
    if qrKeyData.get('success') == False:
        sender.reply('获取二维码配置失败')
        return

    qrKey = qrKeyData.get('data').get('key')
    qrContent = 'https://qr.m.jd.com/p?k=' + qrKey
    qrKeyUrl = getQrKeyUrl(qrContent)
    if qrKeyUrl is None:
        sender.reply('获取二维码URL失败')
        return
    sender.replyImage(qrKeyUrl)
    sender.reply('二维码生成成功，请在60秒内使用京东APP扫码登录(回复【q】退出会话)')

    # 轮询检测扫码状态
    for _ in range(12):
        msg = sender.input(5*1000,0,False)
        if msg =='q' or msg == 'Q':
            sender.reply('退出会话成功')
            return
        
        data = pro.checkQrKey(qrKey)
        if data is None:
            sender.reply(('访问服务器失败，请联系管理员'))
            return
        
        if data.get('success') == False and data.get('data').get('status') == -2:
            sender.reply('二维码/口令已失效，请重新登录')
            return
        
        if data.get('success'):
            username = data.get('data').get('username')
            loginednotice(username, '扫码')
            return data.get('data').get('accessToken')
        
    sender.reply('扫码超时，自动退出程序')
    return

def main_key():
    sender.reply('请稍等，获取服务器配置中')
    qrKeyData = pro.getQrKey()

    if qrKeyData is None:
        sender.reply('获取口令配置失败')
        return
    if qrKeyData.get('success') == False:
        sender.reply('获取口令配置失败')
        return

    qrKey = qrKeyData.get('data').get('key')

    # 生成口令
    qrContent = 'https://lzkj-isv.isvjcloud.com/lzclient/cjwx/common/openJDApp.html?actlink=openapp.jdmobile://virtual?params={"category":"jump","des":"scanLogin","key":"' + qrKey + '","sourceType":"JSHOP_SOURCE_TYPE","sourceValue":"JSHOP_SOURCE_VALUE","M_sourceFrom":"mxz","msf_type":"auto"}'
    Command = jCommand(qrContent)
    sender.reply(Command)
    sender.reply('登录口令生成成功，请在60秒内复制口令，打开京东APP(回复【q】退出会话)')

    # 轮询检测扫码状态
    for _ in range(12):
        msg = sender.input(5*1000,0,False)
        if msg =='q' or msg == 'Q':
            sender.reply('退出会话成功')
            return
        
        data = pro.checkQrKey(qrKey)
        if data is None:
            sender.reply(('访问服务器失败，请联系管理员'))
            return
        
        if data.get('success') == False and data.get('data').get('status') == -2:
            sender.reply('二维码/口令已失效，请重新登录')
            return
        
        if data.get('success'):
            username = data.get('data').get('username')
            loginednotice(username, '口令')
            return data.get('data').get('accessToken')
    
    sender.reply('登录超时，自动退出程序')
    return

def main_zm():
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
    res = pro.pwdLogin(jdid,jdpw)
    if res.get('success') == True: # 登陆成功
        username = res.get('data').get('username')
        loginednotice(username, '账密')
        return res.get('data').get('accessToken')
    
    if res.get('success') == False:
        sender.reply(res.get('message') + '\n' + res.get('data').get('jmp_url'))
        return

def qianyi():
    # 获取所有账号
    allaccountID = middleware.bucketAllKeys('chuan_jd_accountPassword')
    for i in allaccountID:
        sender.reply(f'正在迁移{unquote_plus(i)}的账号')
        try:
            # 获取账号密码
            id_pw = middleware.bucketGet('chuan_jd_accountPassword',i)
            id = id_pw.split('#')[0]
            pw = id_pw.split('#')[1]
            try:
                pw = decrypt_password(pw)
            except:
                pw = id_pw.split('#')[1]
            # sender.reply(f'{unquote_plus(i)}-{id}-{pw}')
            res = pro.pwdLogin(id,pw)
            if res.get('success') == True: # 登陆成功
                sender.reply(f'{unquote_plus(i)}迁移成功')
            if res.get('success') == False:
                sender.reply(res.get('message') + '\n' + res.get('data').get('jmp_url'))
        except Exception as e:
            sender.reply(f'{unquote_plus(i)}迁移失败，错误信息：{e}')
def main():
    mainRules = re.split(r'[,，]', middleware.bucketGet(bucket,'mainRules'))
    smsRules = re.split(r'[,，]', middleware.bucketGet(bucket,'smsRules'))
    qrRules = re.split(r'[,，]', middleware.bucketGet(bucket,'qrRules'))
    keyRules = re.split(r'[,，]', middleware.bucketGet(bucket,'keyRules'))
    zmRules = re.split(r'[,，]', middleware.bucketGet(bucket,'zmRules'))

    if rule in mainRules:
        # 选择登陆方式
        msg = '请选择你要登录的方式(回复【】内得编号即可)\n'

        loginMode = []
        def getText(title, explain):
            login_mode_length = len(loginMode)  # 假设login_mode是在函数外定义的列表
            return f"【{login_mode_length + 1}】{title if explain == '' else f'{title}：{explain}'}\n"
        
        if middleware.bucketGet(bucket,'smsCheckbox') == 'true':
            text = getText("短信登录", middleware.bucketGet(bucket,'smsexplain'))
            loginMode.append('sms')
            msg += text
        
        if middleware.bucketGet(bucket,'qrCheckbox') == 'true':
            text = getText("扫码登录", middleware.bucketGet(bucket,'qrexplain'))
            loginMode.append('qr')
            msg += text
        
        if middleware.bucketGet(bucket,'keyCheckbox') == 'true':
            text = getText("口令登录", middleware.bucketGet(bucket,'keyexplain'))
            loginMode.append('key')
            msg += text
        
        if middleware.bucketGet(bucket,'zmCheckbox') == 'true':
            text = getText("账密登录", middleware.bucketGet(bucket,'zmexplain'))
            loginMode.append('zm')
            msg += text

        msg += middleware.bucketGet(bucket,'selectingReply')
        sender.reply(msg)
        # 接收回复消息
        num = sender.input(60*1000,0,False)
        if num == 'q' or num == 'Q':
            sender.reply('退出成功')
            return
        
        if num is None:
            sender.reply('输入超时，自动退出程序')
            return

        try:
            if int(num) > len(loginMode):
                sender.reply('输入错误，自动退出程序')
                return
        except:
            sender.reply('输入错误，自动退出程序')
            return

        judge = loginMode[int(num) - 1]
        if judge == "sms":
            main_sms()
        elif judge == "qr":
            main_qr()
        elif judge == 'key':
            main_key()
        elif judge == 'zm':
            sender.breakIn('账密登录')

    elif rule in smsRules:
        main_sms()
    elif rule in qrRules:
        main_qr()
    elif rule in keyRules:
        main_key()
    elif rule in zmRules:
        sender.breakIn('账密登录')
    elif '一键迁移pro' == rule:
        qianyi()


if __name__ == "__main__":
    pro = Nark(middleware.bucketGet(bucket,'nark_url'))
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    sender_id = sender.getUserID() # 获取用户id
    imtype = sender.getImtype() # 获取用户平台
    rule = sender.getMessage() # 获取用户消息
    main()
