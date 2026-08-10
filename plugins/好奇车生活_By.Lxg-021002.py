
# [rule: ^(好奇.*|.*好奇)$]
# [cron: 28 8,18,21 * * *]
# [priority: 99999]
# [author: Lxg-021002]
# [title: 好奇车生活]
# [version: 1.0.0]
# [class: 工具类]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [public: true]
# [open_source: false]
# [price: 6.66]
# [icon: http://yi100.top:4455/hqcsh.png]
# [service:<img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif" border="0" /> <b>官方权威认证丨专业团队制作</b>  售后Q群951584089]
# [description: 只提交到青龙和查询脚本群文件，好奇登陆,好奇管理,好奇查询]
# [param: {"required":true,"key":"Yzyxmm_hqcsh_PluginsData.zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# 设置青龙容器
# [param: {"required":true,"key":"Yzyxmm_hqcsh_PluginsData.Qinglong","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割，这个符号是中文的竖(直接复制)"}]
# 领券的变量名
# [param: {"required":true,"key":"Yzyxmm_hqcsh_PluginsData.osname","bool":false,"placeholder":"必填项,例:hqcsh","name":"青龙变量名","desc":"青龙容器内联通的变量名"}]
# 联通上车价格
# [param: {"required":true,"key":"Yzyxmm_hqcsh_PluginsData.hqcshVipmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"上车价格","desc":"上车价格(单位:元)/月"}]
# 积分上车价格
# [param: {"required":true,"key":"Yzyxmm_hqcsh_PluginsData.hqcshcoin","bool":false,"placeholder":"不填为 关闭状态","name":"积分开通","desc":"授权一个月需要多少积分（只能为整数不能为小数）"}]
import requests
import json
import middleware
from datetime import datetime, timedelta
from decimal import Decimal
# 获取发送者ID
senderID = middleware.getSenderID()
# 创建发送者
sender = middleware.Sender(senderID)
# 获取发送者QQ号
userid = sender.getUserID()

uservalue = middleware.bucketGet(bucket='Yzyxmm_hqcsh_bind', key=userid)
today_date = datetime.now().date()
today_time = str(today_date)
def PluginsData():
    PluginsDatas = middleware.bucketAll(bucket='Yzyxmm_hqcsh_PluginsData')
    hqcshVipmoney = Decimal(0)
    hqcshcoin = 99999
    if 'Qinglong' not in PluginsDatas:
        sender.reply('车生活未填写插件对接的容器，请检查配参')
        exit(0)
    else:
        Qinglong = PluginsDatas['Qinglong']
        qllist = Qinglong.split('丨')
        QLurl = qllist[0]
        ClientID = qllist[1]
        ClientSecret = qllist[2]
    if 'osname' not in PluginsDatas:
        osname = 'hqcshck'
    else:
        osname = PluginsDatas['osname']
    if 'hqcshVipmoney' in PluginsDatas:
        hqcshVipmoney = Decimal(PluginsDatas['hqcshVipmoney'])
    if 'hqcshcoin' in PluginsDatas:
        hqcshcoin = PluginsDatas['hqcshcoin']
    if 'zsm' in PluginsDatas:
        zsm = PluginsDatas['zsm']
    else:
        if hqcshVipmoney != Decimal(0):
            sender.reply('车生活未配置赞赏码信息，请检查！')
            exit(0)
        zsm = ''
    return hqcshcoin, zsm, hqcshVipmoney, osname, QLurl, ClientID, ClientSecret

def inputm(mes, long=1, count=99999999):
    sender.reply(mes)
    mes = sender.input(120000, 1, False)
    if mes == 'y' or mes == 'Y':
        return True
    if mes == 'n' or mes == 'N':
        return False
    if mes is None:
        sender.reply('输入超时！')
        exit(0)
    elif mes.lower() == 'q':
        sender.reply('退出！')
        exit(0)
    elif len(mes) < long:
        sender.reply('输入错误！')
        exit(0)
    try:
        mes = int(mes)
        if mes > count:
            sender.reply('输入错误！')
            exit(0)
    except ValueError:
        pass
    return mes
def QLzt(osname, value, account, phone):  # 添加青龙变量
    try:
        qlurl = f"{QLurl}/open/envs"
        data = [{
            "value": value,
            "name": osname,
            "remarks": f'车生活:{account}丨用户:{userid}丨手机:{phone}丨车生活管理'
        }]
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        r = requests.post(qlurl, headers=headers, data=json.dumps(data))
        r_json = r.json()
        if "value must be unique" in r.text:
            return
        else:
            qlid = r_json['data'][0]['id']
            return
    except Exception:
        sender.reply("添加青龙变量错误,请联系管理员处理")
        exit(0)

def userdata(cookie):
    url = 'https://channel.cheryfs.cn/archer/activity-api/common/accountPointLeft?pointId=620415610219683840&showExpire=true&timeType=day&indexDay='
    h = {
        'Host': 'channel.cheryfs.cn',
        'wxappid': '619669369294712832',
        'accountId': cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
        'tenantId': '619669306447261696',
        'activityId': '621883730893492225',
        'Accept': 'application/json,text/plain, */*',
    }
    res = requests.get(url, headers=h)
    return res.json()['success']

def Addenvs(osname, value, account, phone):
    phone = phone[:3] + '*' * 4 + phone[7:]
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json"
    }
    response = requests.get(url=url, headers=headers).json()
    qlid = None
    if response['code'] == 200:
        envslist = response['data']
        for envs in envslist:
            remarks = envs['remarks']
            envname = envs['name']
            if remarks is None:
                continue
            if account in remarks and osname == envname:
                qlid = envs['id']
                break
    else:
        sender.reply('连接青龙获取变量失败')
        exit(0)
    #value = base64.b64encode(value.encode('utf-8')).decode('utf-8')
    if qlid is None:
        QLzt(osname, value, account, phone)
    else:
        QLupdate(osname, value, account, qlid, phone)
def QLtoken(QLurl, ClientID, ClientSecret):  # 获取青龙token
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        A = requests.get(url)
        if "token" in A.text:
            ql = A.content
            qlrequests = json.loads(ql)
            qltoken = qlrequests['data']['token']
            return qltoken
    except Exception:
        sender.reply("链接青龙失败,请检查对接容器！")
        exit(0)


def QLupdate(osname, value, account, qlid, phone):
    qlurl = f"{QLurl}/open/envs"
    data = {
        "value": value,
        "name": osname,
        "remarks": f'车生活:{account}丨用户:{userid}丨手机:{phone}丨车生活管理',
        "id": qlid
    }
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.put(qlurl, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        response_json = response.json()
        data = response_json['data']
        if data is None:
            exit(0)
        id = data['id']
        createdAt = data['createdAt']
        return id, createdAt
    else:
        sender.reply('更新变量失败,请联系管理员处理')
        exit(0)

def bindaccount():
    def accvip(Newaddition):
        if len(accountVip) != 0 and accountVip >= today_time:
            Addenvs(osname=osname, value=accountId, account=account, phone='查不到')
            if Newaddition:
                accounts.append(account)
                sender.reply(f'🤪{account}添加成功！\n————————————————\n» 可发送‘好奇管理’进行管理！')
            else:
                sender.reply(f'🤪{account}更新成功！\n————————————————\n» 可发送‘好奇管理’进行管理！')

        else:
            if Newaddition:
                accounts.append(account)
                sender.reply(f'🤪{account}添加成功！\n————————————————\n» 暂未授权‘好奇管理’进行授权！')
            else:
                sender.reply(f'🤪{account}更新成功！\n————————————————\n» 授权过期‘好奇管理’进行续期！')

        middleware.bucketSet(bucket='Yzyxmm_hqcsh_bind', key=userid, value=f'{accounts}')

    account = str(inputm('请输入账号备注:\n（建议手机尾号不能重复）\n如果要更新ck'))
    accountId = str(inputm('请输入账号accountId:'))
    if not userdata(accountId):
        sender.reply('账号无效！')
        exit(0)
    accountVip = middleware.bucketGet(bucket='Yzyxmm_hqcsh_accountVip', key=account)
    middleware.bucketSet(bucket='Yzyxmm_hqcsh_account', key=account, value=accountId)
    #mobile = phone[:3] + "*" * 4 + phone[7:]
    if len(uservalue) == 0:
        accounts = []
        accvip(True)
    else:
        accounts = eval(uservalue)
        if account in accounts:
            accvip(False)
        else:
            accvip(True)
def getaccountmessage(account):
    accountVip = middleware.bucketGet(bucket='Yzyxmm_hqcsh_accountVip', key=account)
    cookie = middleware.bucketGet(bucket='Yzyxmm_hqcsh_account', key=account)
    accountzt = '状态正常'
    if not userdata(cookie):
        accountzt = 'Token过期'
    #mobile = phone[:3] + "*" * 4 + phone[7:]
    if len(accountVip) == 0:
        accvip = '未授权'
    elif accountVip < today_time:
        accvip = '授权过期'
    else:
        accvip = accountVip
    return accvip, cookie, accountzt
def empower(empowertime, me_as_int):
    day = me_as_int * 30
    if empowertime == '未授权' or empowertime == '授权过期' or empowertime <= str(today_time):
        delayed_date = today_date + timedelta(days=day)
    elif empowertime > today_time:
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        delayed_date = delayed_date.date()
    else:
        sender.reply('出错！')
        exit(0)
    return str(delayed_date)
def Pointpayment(mation_int, accountVip, account, token, phone):
    usercoin = middleware.bucketGet(bucket='Yzyxmm_sign_coin', key=f'{userid}')

    if len(usercoin) != 0 and usercoin != '0':
        zfcoin = int(hqcshcoin) * mation_int
        if int(usercoin) >= int(zfcoin):
            sender.reply(f'当前积分{usercoin}积分，订单所需{zfcoin}积分是否使用积分进行抵扣？')
            sender.reply('[y]是丨[n]否')
            if inputm(''):
                usercoin = int(usercoin) - int(zfcoin)
                middleware.bucketSet(bucket='Yzyxmm_sign_coin', key=f'{userid}',
                                     value=f'{usercoin}')
                return True
    return False
def zf(project, me_as_int, accountVip, account, token, phone):
    zsm = middleware.bucketGet(bucket='Yzyxmm_hqcsh_PluginsData', key='zsm')
    zfzt = sender.atWaitPay()
    #Pointpayment(me_as_int, accountVip, account, token, phone)
    if hqcshVipmoney == Decimal(0):
        return
    money = Decimal(me_as_int) * Decimal(hqcshVipmoney)
    if not zfzt:
        sender.reply(f'————《订单信息》————\n🎈名称:{project}\n🎉数量:{me_as_int}\n💰应付:{money}元')
        sender.replyImage(zsm)
        ddzf = sender.waitPay("q", 100 * 1000)  # 等待支付
        if str(ddzf) == 'q':
            sender.reply('退出支付')
            exit(0)
        if 'Time' in str(ddzf):
            try:
                zfjson = json.loads(ddzf)
                zfmoney = zfjson['Money']
            except Exception:
                zfmoney = ddzf['Money']
            if float(zfmoney) >= float(money):
                return
            else:
                sender.reply(f'支付金额错误\n应付:{money}元\n实付:{zfmoney}元\n请联系管理员处理退款！')
                exit(0)
        elif ddzf == '':
            sender.reply('支付超时！')
            exit(0)
        else:
            exit(0)
    else:
        sender.reply('当前有人正在支付,请稍后再试！')
        exit(0)
def Administration():
    message = ''
    count = 1
    if len(uservalue) == 0:
        sender.reply('未绑定车生活账号，请发送好奇登录进行绑定！')
        exit(0)
    accounts = eval(uservalue)
    for account in accounts:
        accountVip, cookie, accountzt = getaccountmessage(account)

        message += f'【{count}】      ———\n🤪备注:{account}\n🪫账号状态:{accountzt}\n☁云授权:{accountVip}\n'
        count += 1
    sender.reply(f'————《车生活管理》————\n{message}')
    mes = inputm('请输入【】中需要操作的账号:', count=count)
    account = accounts[mes - 1]
    accountVip, cookie, accountzt = getaccountmessage(account)
    message += f'【{count}】      ———\n🤪用户备注:{account}\n☁云授权:{accountVip}\n'
    sender.reply(f'🤪用户ID:{account}\n☁云授权:{accountVip}')
    mes = inputm('【1】丨授权账号\n【2】丨删除账号', count=2)
    if mes == 1:
        mes = inputm('请输入需要的月数: 例1', count=99)
        if not Pointpayment(mation_int=mes, accountVip=accountVip, account=account, token=cookie, phone='查不到'):
            zf(project='车生活授权', me_as_int=mes, accountVip=accountVip, account=account, token=cookie, phone='查不到')
        money = Decimal(mes) * Decimal(hqcshVipmoney)
        accountVip = empower(empowertime=accountVip, me_as_int=mes)
        middleware.bucketSet(bucket='Yzyxmm_hqcsh_accountVip', key=account, value=accountVip)
        Addenvs(osname=osname, value=cookie, account=account, phone='查不到')
        # Addenvs(osname=osname, value=phone, account=mobile)
        sender.reply(f'————《订单完成》————\n🎈名称:车生活授权\n🎉数量:{mes}\n💰付款金额:{money}元')
    elif mes == 2:
        sender.reply('是否删除这个账号？\n[y] 是丨[n] 否')
        yesorno = sender.input(120000, 1, False)
        if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':

            accounts.remove(account)
            if len(accounts) == 0:
                middleware.bucketDel(bucket='Yzyxmm_hqcsh_bind', key=userid)
            else:
                middleware.bucketSet(bucket='Yzyxmm_hqcsh_bind', key=userid, value=f'{accounts}')
            sender.reply('删除完成！')
            exit(0)

def cxs():
    if len(uservalue) == 0:
        sender.reply('未绑定车生活账号，请发送‘好奇登陆’进行绑定！')
        exit(0)
    accounts = eval(uservalue)
    sender.reply('正在努力加载....')
    for account in accounts:
        accountVip, cookie, accountzt = getaccountmessage(account)
        if accountVip == '未授权' or accountVip == '授权过期':
            sender.reply(f'【{account}】{accountVip}')
            continue
        if accountzt == 'Token过期':
            sender.reply(f'【{account}】{accountzt}')
            continue
        url = 'https://channel.cheryfs.cn/archer/activity-api/common/accountPointLeft?pointId=620415610219683840&showExpire=true&timeType=day&indexDay='

        h = {
            'Host': 'channel.cheryfs.cn',
            'wxappid': '619669369294712832',
            'accountId': cookie,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'tenantId': '619669306447261696',
            'activityId': '621883730893492225',
            'Accept': 'application/json,text/plain, */*',
        }
        res = requests.get(url, headers=h)
        result = res.json()['result']
        sender.reply(f'【{account}】{result}分')
def allenvs(osname, account):
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json"
    }
    response = requests.get(url=url, headers=headers).json()
    qlid = None
    if response['code'] == 200:
        envslist = response['data']
        for envs in envslist:
            envname = envs['name']
            remarks = envs['remarks']
            if remarks is None:
                continue
            if osname == envname and str(account) in remarks:
                qlid = envs['id']
                break
        sender.reply(qlid)
        return qlid
    else:
        sender.reply('连接青龙获取变量失败')
        exit(0)
def push(user, mobile, message):
    middleware.push('wb', '', user, '',
                    f'🤪用户‘{mobile}’,{message}')
    middleware.push('tg', '', user, '',
                    f'🤪用户‘{mobile}’,{message}')
    middleware.push('qq', '', user, '',
                    f'🤪用户‘{mobile}’,{message}')
    middleware.push('qb', '', user, '',
                    f'🤪用户‘{mobile}’,{message}')
    middleware.push('wx', '', user, '',
                    f'🤪用户‘{mobile}’,{message}')
def delenvs(id):
    if id is None:
        return
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = [id]
    response = requests.delete(url, headers=headers, json=data).json()
hqcshcoin, zsm, hqcshVipmoney, osname, QLurl, ClientID, ClientSecret = PluginsData()
qltoken = QLtoken(QLurl, ClientID, ClientSecret)
usermessage = sender.getMessage()
imtype = sender.getImtype()
if '登录' in usermessage or '登陆' in usermessage:
    bindaccount()
elif '管理' in usermessage:
    Administration()
elif '查询' in usermessage:
    cxs()
elif imtype == 'fake':
    allkey = middleware.bucketAllKeys(bucket='Yzyxmm_hqcsh_bind')
    for key in allkey:
        accounts = middleware.bucketGet(bucket='Yzyxmm_hqcsh_account', key=key)
        accounts = eval(accounts)
        for account in accounts:
            accountVip, mobile, accountzt = getaccountmessage(account)
            if accountzt == 'Token过期':
                push(key, mobile, '车生活Token过期，请及时更新！')
                continue
            if accountVip == '未授权' or accountVip == '授权过期':
                qlid = allenvs(osname, account)
                delenvs(id=qlid)
                push(key, mobile, '车生活授权过期，请及时续费！')
                continue