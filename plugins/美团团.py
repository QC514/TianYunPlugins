# [rule: ^.*$]
# [disable:false]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [public: true]
# [open_source: false]
# [class: 工具类]
# [cron: 18 5,8,12,15,18,21 * * *]
# [author: Lxg-021002]
# [version: 2.2.7]
# [price: 8.88]
# [title: 美团团]
# [admin: false]
# [icon: http://150.158.10.200:9876/mtt.jpg]
# [service:<img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif" border="0" /> <b>官方权威认证丨专业团队制作</b>  售后Q群913193784]
# [description: 彻底解决千寻框架emjio问题 请使用最新版本Autman和千寻框架 以及奥特曼勾选 新版千寻框架 支持 查询丨删除 账号丨自定义命令(详见配参)，后续的任何使用问题都可以联系幼稚园小妹妹！使用前请安装Python的user-agent和sseclient依赖]
# [param: {"required":true,"key":"MMjson.zsm","bool":true,"placeholder":"","name":"赞赏码发图或链接","desc":"勾选发图,不勾发链接"}]
# 设置青龙容器
# [param: {"required":true,"key":"MMjson.Meituan_Qinglong","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割，这个符号是中文的竖(直接复制)"}]
# 设置领券的价格
# [param: {"required":true,"key":"MMjson.Meituan_Lingquanmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"领券价格","desc":"领券价格(单位:元)"}]
# 团币价格
# [param: {"required":true,"key":"MMjson.Meituan_tbmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"团币价格","desc":"团币价格(单位:元)"}]
# 赞赏码链接
# [param: {"required":true,"key":"MMjson.Meituan_zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# 发送登录命令回复的消息
# [param: {"required":true,"key":"MMjson.mtloginmessage","bool":false,"placeholder":"必填项,例:请输入你的Token","name":"登录消息","desc":"发送 登录命令 需要回复的消息"}]
# 领券的变量名
# [param: {"required":true,"key":"MMjson.Meituan_os_mtname","bool":false,"placeholder":"必填项,例:meituanCookie","name":"领券变量名","desc":"青龙容器内领券的变量名,不可与团币变量名相同"}]
# 团币的变量名
# [param: {"required":true,"key":"MMjson.Meituan_os_tbname","bool":false,"placeholder":"必填项,例:meituanToken","name":"团币变量名","desc":"青龙容器内团币的变量名,不可与领券变量名相同"}]
# 触发登录的口令
# [param: {"required":true,"key":"MMjson.Meituan_signcommand","bool":false,"placeholder":"默认为‘美团登录’，例如:美团登录丨团团登陆","name":"登陆口令","desc":"多个口令用‘丨’分割，这个符号是中文的竖(直接复制)"}]
# 触发查询的口令
# [param: {"required":true,"key":"MMjson.Meituan_querycommand","bool":false,"placeholder":"默认为‘美团查询’，例如:美团查询丨团团查询","name":"查询口令","desc":"多个口令用‘丨’分割，这个符号是中文的竖(直接复制)"}]
# 触发管理的口令
# [param: {"required":true,"key":"MMjson.Meituan_managecommand","bool":false,"placeholder":"默认为‘我的美团’，例如:我的团团丨我的美团","name":"账号管理口令","desc":"多个口令用‘丨’分割，这个符号是中文的竖(直接复制)"}]
# 开通团币的积分数
# [param: {"required":true,"key":"MMjson.Meituan_tbcoin","bool":false,"placeholder":"默认:9999999","name":"团币每月积分","desc":"团币一个月授权需要多少积分(只能为整数不能为小数)"}]
# 开通领券的积分数
# [param: {"required":true,"key":"MMjson.Meituan_Lingquancoin","bool":false,"placeholder":"默认:9999999","name":"领券每月积分","desc":"领券一个月授权需要多少积分(只能为整数不能为小数)"}]

import json
import random
import string
import requests
import middleware
from datetime import datetime, timedelta
from user_agent import generate_user_agent
from urllib.parse import urlparse, parse_qs
import re
import time
from decimal import Decimal

ua = generate_user_agent(os='android')
# 获取发送者ID
senderID = middleware.getSenderID()
# 创建发送者
sender = middleware.Sender(senderID)
# 获取发送者QQ号
userid = sender.getUserID()
# 获取用户的值
useroldvalue = middleware.bucketGet(bucket='MMjson', key=userid)
uservalue = middleware.bucketGet(bucket='Yzyxmm_mt_bind', key=userid)


def seekql():
    try:
        ql = middleware.bucketGet(bucket="MMjson", key="Meituan_Qinglong")
        if len(ql) == 0:
            sender.reply('美团团未填写插件对接的容器，请检查配参')
            exit(0)
        else:
            qllist = ql.split('丨')
            QLurl = qllist[0]
            ClientID = qllist[1]
            ClientSecret = qllist[2]
            qltoken = QLtoken(QLurl=QLurl, ClientID=ClientID, ClientSecret=ClientSecret)
            return QLurl, qltoken
    except Exception:
        sender.reply("美团团获取青龙Token失败,请检查对接容器的参数！并仔细阅读提示内容！")
        exit(0)


def QLtoken(QLurl, ClientID, ClientSecret):  # 获取青龙token
    try:
        url = f'{QLurl}/open/auth/token?client_id={ClientID}&client_secret={ClientSecret}'
        A = requests.get(url)
        if "token" in A.text:
            ql = A.content
            qlrequests = json.loads(ql)
            qltoken = qlrequests['data']['token']

            return qltoken
        else:
            sender.reply('美团团链接青龙失败,请检查青龙配参！并仔细阅读提示内容！')
            exit(0)
    except Exception:
        sender.reply("美团团链接青龙失败,请检查青龙配参！并仔细阅读提示内容！")
        exit(0)


def getusercontent():
    Meituan_Lingquanmoney = middleware.bucketGet(bucket='MMjson', key='Meituan_Lingquanmoney')  # 领券的价格
    Meituan_tbmoney = middleware.bucketGet(bucket='MMjson', key='Meituan_tbmoney')  # 团币价格
    Meituan_Lingquancoin = middleware.bucketGet(bucket='MMjson', key='Meituan_Lingquancoin')  # 领券的价格
    Meituan_tbcoin = middleware.bucketGet(bucket='MMjson', key='Meituan_tbcoin')
    Meituan_zsm = middleware.bucketGet(bucket='MMjson', key='Meituan_zsm')  # 收款码链接
    Meituan_os_mtname = middleware.bucketGet(bucket='MMjson', key='Meituan_os_mtname')  # 领券变量名
    Meituan_os_tbname = middleware.bucketGet(bucket='MMjson', key='Meituan_os_tbname')  # 团币变量名
    mt_managecommand = middleware.bucketGet(bucket='MMjson', key='Meituan_managecommand')  # 触发管理的命令
    mt_querycommand = middleware.bucketGet(bucket='MMjson', key='Meituan_querycommand')  # 触发查询的命令
    Mt_signcommand = middleware.bucketGet(bucket='MMjson', key='Meituan_signcommand')  # 触发登陆的命令
    mtloginmessage = middleware.bucketGet(bucket='MMjson', key='mtloginmessage')  # 美团登录发送的消息
    if len(Meituan_Lingquanmoney) == 0:
        Meituan_Lingquanmoney = Decimal('0')
    if len(Meituan_tbmoney) == 0:
        Meituan_tbmoney = Decimal('0')
    if len(Meituan_zsm) == 0:
        sender.reply("赞赏码链接未填写")
        exit(0)
    if len(Meituan_os_mtname) == 0:
        sender.reply("美团变量名称未填写")
        exit(0)
    if len(Meituan_os_tbname) == 0:
        sender.reply("团币变量名称未填写")
        exit(0)
    if len(Meituan_Lingquancoin) == 0:
        Meituan_Lingquancoin = 999999
    if len(Meituan_tbcoin) == 0:
        Meituan_tbcoin = 999999
    if len(mt_managecommand) == 0:
        mt_managecommand = '美团管理'
    randommanagecommand = mt_managecommand
    if '丨' in mt_managecommand:
        parts = mt_managecommand.split('丨')
        randommanagecommand = random.choice(parts)

    if len(mt_querycommand) == 0:
        mt_querycommand = '美团查询'
    randomquerycommand = mt_querycommand
    if '丨' in mt_querycommand:
        parts = mt_querycommand.split('丨')
        randomquerycommand = random.choice(parts)
    if len(Mt_signcommand) == 0:
        Mt_signcommand = '美团登录'
    randomsigncommand = Mt_signcommand
    if '丨' in Mt_signcommand:
        parts = Mt_signcommand.split('丨')
        randomsigncommand = random.choice(parts)
    if len(mtloginmessage) == 0:
        mtloginmessage = '美团Token获取丨http://u9v.cn/6hEfM8\n请输入您的Token:'
    return Meituan_tbmoney, Meituan_Lingquanmoney, Meituan_zsm, Meituan_os_mtname, Meituan_os_tbname, mt_managecommand, mt_querycommand, Mt_signcommand, randommanagecommand, randomsigncommand, randomquerycommand, Meituan_Lingquancoin, Meituan_tbcoin, mtloginmessage


def userdata(usertoken):  # 美团ck状态，用户信息
    try:
        url = "https://open.meituan.com/user/v1/info?fields=mobile,username,avatarurl,regTime"
        h = {
            'Connection': 'keep-alive',
            'Origin': 'https://mtaccount.meituan.com',
            'User-Agent': ua,
            'token': usertoken,
            'Referer': 'https://mtaccount.meituan.com/user/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'X-Requested-With': 'com.sankuai.meituan',
        }
        MT = requests.get(url, headers=h)

        if '登录失败' in MT.text:
            MTname = 'Token失效'
            mobile = '查询失败'
            accountid = 'Token失效'
            return MTname, accountid, mobile
        elif '已将账号锁定' in MT.text:
            MTname = 'Token失效'
            mobile = '查询失败'
            accountid = 'Token失效'
            return MTname, accountid, mobile
        else:
            MTjson = MT.json()
            MTname = MTjson['user']['username']
            mobile = MTjson['user']['mobile']
            accountid = MTjson['user']['id']
            return MTname, accountid, mobile
    except Exception:
        sender.reply(f'查询用户信息错误')
        exit(0)


def allenvs(osname, token, account):
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


def QLupdate(osname, value, account, oldToken):
    qlid = allenvs(osname=osname, token=oldToken, account=account)
    if qlid is None:
        QLzt(osname=osname, value=value, userid=userid, account=account)
    else:
        qlurl = f"{QLurl}/open/envs"
        data = {
            "value": value,
            "name": osname,
            "remarks": f'美团团管理丨用户:{userid}丨美团:{account}',
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


def QLzt(osname, value, userid, account):  # 添加青龙变量
    try:
        qlurl = f"{QLurl}/open/envs"
        data = [{
            "value": value,
            "name": osname,
            "remarks": f'美团团管理丨用户:{userid}丨美团:{account}'
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
        # createdAt = r_json['data'][0]['createdAt']

    except Exception:
        sender.reply("添加青龙变量错误,请联系管理员处理")
        exit(0)


def binds(accounts, Lingquantime, token, account, MTname, Tbtime, UUID, oldtoken):
    middleware.bucketSet(bucket='Yzyxmm_mt_bind', key=f'{userid}', value=f'{accounts}')
    if len(Lingquantime) != 0 and Lingquantime != '未开通' and Lingquantime != '授权过期' and Lingquantime >= str(
            today_time):
        QLzt(osname=Meituan_os_mtname, value=f'{token}', userid=userid, account=f'{account}')
    if len(Tbtime) != 0 and Tbtime != '未开通' and Tbtime != '授权过期' and Tbtime >= str(today_time):
        if len(UUID) == 0:
            middleware.bucketSet(bucket='Yzyxmm_mt_account', key=f'{account}', value=f'{oldtoken}')
            sender.reply('账号未添加UUID，请添加后重试！')
            exit(0)
        QLzt(osname=Meituan_os_tbname, value=f'{token}#{UUID}', userid=userid, account=f'{account}')
    sender.reply(f'登陆成功! 🤪用户名:{MTname}，可对我说‘{randommanagecommand}’对账号进行管理!')


def bindaccount():
    if len(useroldvalue) == 0:
        sender.reply(mtloginmessage)
        userurl = sender.input(120000, 1, False)
        if userurl == 'q' or userurl == 'Q':
            sender.reply('退出！')
            exit(0)
        if 'meituan.com' in userurl and 'token' in userurl:
            token = re.search(r"token=([^&]+)", userurl).group(1)
            MTname, account, mobile = userdata(token)
            if MTname == 'Token失效':
                sender.reply('Token无效，请重新获取！')
                exit(0)
            else:
                oldtoken = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
                middleware.bucketSet(bucket='Yzyxmm_mt_MTname', key=f'{account}', value=f'{MTname}')
                middleware.bucketSet(bucket='Yzyxmm_mt_account', key=f'{account}', value=f'{token}')
                middleware.bucketSet(bucket='Yzyxmm_mt_mobile', key=f'{account}', value=f'{mobile}')
                Lingquantime = middleware.bucketGet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}')
                UUID = middleware.bucketGet(bucket='Yzyxmm_mt_UUID', key=f'{account}')
                Tbtime = middleware.bucketGet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}')
        elif 'Ag' in userurl and '#' not in userurl:
            token = userurl
            MTname, account, mobile = userdata(token)
            if MTname == 'Token失效':
                sender.reply('Token无效，请重新获取！')
                exit(0)
            else:
                oldtoken = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
                middleware.bucketSet(bucket='Yzyxmm_mt_MTname', key=f'{account}', value=f'{MTname}')
                middleware.bucketSet(bucket='Yzyxmm_mt_account', key=f'{account}', value=f'{token}')
                middleware.bucketSet(bucket='Yzyxmm_mt_mobile', key=f'{account}', value=f'{mobile}')
                Lingquantime = middleware.bucketGet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}')
                UUID = middleware.bucketGet(bucket='Yzyxmm_mt_UUID', key=f'{account}')
                Tbtime = middleware.bucketGet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}')
        elif 'Ag' in userurl and '#' in userurl:
            tokens = userurl.split('#')
            token = tokens[0]
            UUID = tokens[1]
            MTname, account, mobile = userdata(token)
            if MTname == 'Token失效':
                sender.reply('Token无效，请重新获取！')
                exit(0)
            else:
                oldtoken = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
                middleware.bucketSet(bucket='Yzyxmm_mt_MTname', key=f'{account}', value=f'{MTname}')
                middleware.bucketSet(bucket='Yzyxmm_mt_account', key=f'{account}', value=f'{token}')
                middleware.bucketSet(bucket='Yzyxmm_mt_mobile', key=f'{account}', value=f'{mobile}')
                middleware.bucketSet(bucket='Yzyxmm_mt_UUID', key=f'{account}', value=f'{UUID}')
                Lingquantime = middleware.bucketGet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}')
                Tbtime = middleware.bucketGet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}')
        else:
            sender.reply('未找到有效Token，请检查！')
            exit(0)
        if len(uservalue) < 3:
            accounts = []
            accounts.append(str(account))
            binds(accounts, Lingquantime, token, account, MTname, Tbtime, UUID, oldtoken)
        else:
            accounts = eval(uservalue)
            if str(account) not in uservalue:
                accounts.append(str(account))
                binds(accounts, Lingquantime, token, account, MTname, Tbtime, UUID, oldtoken)
            else:
                if len(Lingquantime) != 0 and Lingquantime != '未开通' and Lingquantime != '授权过期' and Lingquantime >= str(
                        today_time):
                    QLupdate(osname=Meituan_os_mtname, value=token, account=account, oldToken=oldtoken)

                if len(Tbtime) != 0 and Tbtime != '未开通' and Tbtime != '授权过期' and Tbtime >= str(today_time):
                    if len(UUID) == 0:
                        sender.reply('账号未添加UUID，请添加UUID！')
                        UUID = getUUID()
                        if UUID is None:
                            middleware.bucketSet(bucket='Yzyxmm_mt_account', key=f'{account}', value=f'{oldtoken}')
                            sender.reply('提取UUID错误')
                            exit(0)
                        middleware.bucketSet(bucket='Yzyxmm_mt_UUID', key=f'{account}', value=f'{UUID}')

                        QLupdate(osname=Meituan_os_tbname, value=f'{token}#{UUID}', account=account,
                                 oldToken=f'{oldtoken}')
                        sender.reply(f'更新成功! 🤪用户名:{MTname}，可对我说‘{randommanagecommand}’对账号进行管理!')
                        exit(0)
                    else:
                        QLupdate(osname=Meituan_os_tbname, value=f'{token}#{UUID}', account=account,
                                 oldToken=f'{oldtoken}#{UUID}')
                sender.reply(f'更新成功! 🤪用户名:{MTname}，可对我说‘{randommanagecommand}’对账号进行管理!')




    else:
        oldmtt()


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


def lq(token):
    url = 'http://8.130.140.144:22222/mtcoupon'

    data = {
        "token": token
    }
    response = requests.post(url, json=data)
    return response


def meituanmanage():
    if len(uservalue) > 3:
        count = 1
        message = ''
        accounts = eval(uservalue)
        for account in accounts:
            token = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
            # MTname, account1, mobile = userdata(token)
            mobile = middleware.bucketGet(bucket='Yzyxmm_mt_mobile', key=f'{account}')
            MTname = middleware.bucketGet(bucket='Yzyxmm_mt_MTname', key=f'{account}')
            Lingquantime = middleware.bucketGet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}')
            Tbtime = middleware.bucketGet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}')
            UUID = middleware.bucketGet(bucket='Yzyxmm_mt_UUID', key=f'{account}')
            if len(UUID) == 0:
                UUID = '🥹'
            else:
                UUID = '😀'
            if len(Lingquantime) != 0 or Lingquantime < str(today_time):
                balance = '授权过期'
            if len(Lingquantime) == 0:
                balance = '未开通'
            if Lingquantime > str(today_time):
                balance = Lingquantime
            if len(Tbtime) != 0 or Tbtime < str(today_time):
                balance2 = '授权过期'
            if len(Tbtime) == 0:
                balance2 = '未开通'
            if Tbtime > str(today_time):
                balance2 = Tbtime
            message += f'[{count}]-----\n🤪用户名:{MTname}\n🔥用户ID:{mobile}\n☁领券授权:{balance}\n🌤团币授权:{balance2}\n🔗UUID:  {UUID}\n'
            count += 1
        message_to_send = f"=====我的团团=====\n团币:{str(Meituan_tbmoney)}元丨领券:{str(Meituan_Lingquanmoney)}元\n{message}"
        sender.reply(message_to_send)
        sender.reply('请选择[]内的数字对团团进行管理，回复‘q’退出')
        inputmessage = sender.input(120000, 1, False)
        if inputmessage == 'timeout':
            sender.reply('超时退出！')
            exit(0)
        elif inputmessage == 'q' or inputmessage == 'Q' or inputmessage == '0':
            sender.reply('退出！')
            exit(0)
        try:
            me_as_int = int(inputmessage)
            if me_as_int > count:
                sender.reply('输入错误')
                exit(0)
        except ValueError:
            sender.reply('输入错误')
            exit(0)
        accountA = accounts[me_as_int - 1]
        token = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{accountA}')
        MTname, account, mobile = userdata(token)
        accountst = None
        if MTname == 'Token失效':
            accountst = 'Token失效'
            mobile = middleware.bucketGet(bucket='Yzyxmm_mt_mobile', key=f'{accountA}')
            MTname = middleware.bucketGet(bucket='Yzyxmm_mt_MTname', key=f'{accountA}')
        Lingquantime = middleware.bucketGet(bucket='Yzyxmm_mt_Lingquantime', key=f'{accountA}')
        Tbtime = middleware.bucketGet(bucket='Yzyxmm_mt_Tbtime', key=f'{accountA}')
        UUID = middleware.bucketGet(bucket='Yzyxmm_mt_UUID', key=f'{accountA}')
        if len(UUID) == 0:
            UUIDs = '➖➖'
        else:
            UUIDs = '✔️'
        if Lingquantime > str(today_time):
            balance = Lingquantime
        if len(Tbtime) != 0 or Tbtime < str(today_time):
            balance2 = '授权过期'
        if len(Tbtime) == 0:
            balance2 = '未开通'
        if Tbtime > str(today_time):
            balance2 = Tbtime
        if accountst == 'Token失效':
            sender.reply(
                f'🤪用户名:{MTname}\n🔥用户ID:{mobile}\n🪫账号状态:Token失效')
            sender.reply('[3]丨关停服务 [4]丨添加UUID\n [q]丨退出')
        else:
            sender.reply(
                f'🤪用户名:{MTname}\n🔥用户ID:{mobile}\n☁领券授权:{balance}\n🌤团币授权:{balance2}\n🏷UUID:  {UUIDs}')
            sender.reply('[1]丨开通领券 [2]丨开通团币\n[3]丨关停服务 [4]丨添加UUID\n [q]丨退出')
        inputmessage = sender.input(120000, 1, False)
        if inputmessage == 'Q' or inputmessage == 'q' or inputmessage == '0':
            sender.reply('退出！')
            exit(0)
        try:
            me_as_int = int(inputmessage)
        except ValueError:
            sender.reply('输入错误')
            exit(0)
        if me_as_int == 1:
            if accountst == 'Token失效':
                sender.reply(f'【{mobile}】账号Token无效')
                exit(0)
            # 开通领券
            renew(Monthly=Meituan_Lingquanmoney, token=token, account=account, osname=Meituan_os_mtname, UUID=None,
                  Lingquantime=Lingquantime, Tbtime=Tbtime)
        elif me_as_int == 2:
            if accountst == 'Token失效':
                sender.reply(f'【{mobile}】账号Token无效')
                exit(0)
            if UUIDs != '✔️':
                sender.reply('请先添加UUID后再试！')
                exit(0)
            # 开通团币
            renew(Monthly=Meituan_tbmoney, token=token, account=account, osname=Meituan_os_tbname, UUID=UUID,
                  Lingquantime=Lingquantime, Tbtime=Tbtime)
        elif me_as_int == 3:
            if (balance == '未开通' or balance == '授权过期') and (balance2 == '未开通' or balance2 == '授权过期'):
                sender.reply('当前账号未开通任何授权，请问您是否要删除这个账号?')
                sender.reply('[y] 是丨[n] 否')
                yesorno = sender.input(120000, 1, False)
                if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
                    accounts.remove(str(accountA))
                    middleware.bucketSet(bucket='Yzyxmm_mt_bind', key=f'{userid}', value=f'{accounts}')
                    sender.reply('删除成功，感谢您的使用！')
                elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
                    sender.reply('退出！')
                    exit(0)
            else:
                delaccount(balance, balance2, token, UUID, accounts, accountA)
        elif me_as_int == 4:
            uuid = getUUID()
            if uuid is None:
                sender.reply('uuid提取失败，！')
                exit(0)
            if balance2 == '未开通' or balance2 == '授权过期':
                middleware.bucketSet(bucket='Yzyxmm_mt_UUID', key=f'{account}', value=f'{uuid}')
                sender.reply(f'添加成功！UUID_{uuid}')
            else:
                oldToken = f'{token}#{UUID}'
                QLupdate(osname=Meituan_os_tbname, value=f'{token}#{uuid}', account=account, oldToken=oldToken)
                middleware.bucketSet(bucket='Yzyxmm_mt_UUID', key=f'{account}', value=f'{uuid}')
                sender.reply(f'更新成功！UUID_{uuid}')

        '''elif me_as_int == 5:
            sender.reply(
                '该领券可能出现如下情况:\n情况一:25-8丨30-9丨40-10丨20-7\n情况二:20-6丨25-7丨30-8丨40-9\n情况三:20-5丨25-6丨30-7丨40-8\n情况四:活动过于火爆\n情况五:今日已经领过券\n账号正常只会有第一，第二种情况，其中:活动火爆丨今日已领，可询问群主退款\n注:该领券皆为代替手动领券实现自动化，不存在如:刷券丨卖券等')
            sender.reply('该次代领券费用(0.88)元，同意以上协议\n[y] 是丨[n] 否')
            yesorno = sender.input(120000, 1, False)
            if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
                zf(money='0.88', project='单次领券', me_as_int='1次')
                try:
                    r = lq(token)
                    message = r.json()['message']
                    coupons = r.json()['coupons']
                    if message == 'fail':
                        sender.reply(f'领券失败>>>{coupons}')
                    else:
                        sender.reply(f'{coupons}')
                except Exception as e:
                    sender.reply(f'领券异常出错>>>{e}')
                    exit(0)
            elif inputmessage == 'Q' or inputmessage == 'q' or inputmessage == '0':
                sender.reply('退出！')
            else:
                sender.reply('输入错误')'''


def delaccount(balance, balance2, token, UUID, accounts, account):
    sender.reply('[1]丨关停领券\n[2]丨关停团币\n[3]丨关停服务删除全部\n[q]丨退出')
    inputmessage = sender.input(120000, 1, False)
    if inputmessage == '1':
        if balance == '未开通' or balance == '授权过期':
            sender.reply('账号还未开通领券！')
            exit(0)
        else:
            qlid = allenvs(osname=Meituan_os_mtname, token=token, account=account)
            sender.reply(f'当前账号已经开通了领券，确定要关停领券服务吗？(授权时间会一并清空)')
            sender.reply('[y] 是丨[n] 否')
            yesorno = sender.input(120000, 1, False)
            if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
                delenvs(id=qlid)
                middleware.bucketDel(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}')
                sender.reply('删除成功，感谢您的使用！')
            elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
                sender.reply('退出！')
                exit(0)
    elif inputmessage == '2':
        if balance2 == '未开通' or balance2 == '授权过期':
            sender.reply('账号还未开通团币！')
            exit(0)
        else:
            qlid = allenvs(osname=Meituan_os_tbname, token=f'{token}#{UUID}', account=account)
        sender.reply(f'当前账号已经开通了团币，确定要关停团币服务吗？(授权时间会一并清空)')
        sender.reply('[y] 是丨[n] 否')
        yesorno = sender.input(120000, 1, False)
        if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
            middleware.bucketDel(bucket='Yzyxmm_mt_Tbtime', key=f'{account}')
            delenvs(id=qlid)
            sender.reply('删除成功，感谢您的使用！')
        elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
            sender.reply('退出！')
            exit(0)
    elif inputmessage == '3':
        sender.reply(f'确定要关停当前账号的全部数据吗？请您慎重选择！')
        sender.reply('[y] 是丨[n] 否')
        yesorno = sender.input(120000, 1, False)
        if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
            mtid = allenvs(osname=Meituan_os_mtname, token=token, account=account)
            tbid = allenvs(osname=Meituan_os_tbname, token=f'{token}#{UUID}', account=account)
            delenvs(id=mtid)
            delenvs(id=tbid)
            accounts.remove(str(account))
            middleware.bucketSet(bucket='Yzyxmm_mt_bind', key=f'{userid}', value=f'{accounts}')
        elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
            sender.reply('退出！')
            exit(0)
        sender.reply('删除成功！，感谢您的使用！')
    elif inputmessage == 'q':
        sender.reply('退出！')


def empower(empowertime, me_as_int):
    day = me_as_int * 30
    if len(empowertime) == 0 or empowertime == '未开通' or empowertime == '授权过期' or empowertime <= str(today_time):
        delayed_date = today_time + timedelta(days=day)
    elif empowertime > str(today_time):
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        delayed_date = delayed_date.date()

    else:
        sender.reply('出错！')
        exit(0)
    return str(delayed_date)


def renew(Monthly, token, account, osname, UUID, Lingquantime, Tbtime):
    usercoin = middleware.bucketGet(bucket='Yzyxmm_sign_coin', key=f'{userid}')
    if len(usercoin) == 0 or usercoin == '0':
        usercoin = 0
    sender.reply('请问您需要几个月？例:1')
    inputmessage = sender.input(120000, 1, False)
    if inputmessage == '0':
        sender.reply('退出！')
        exit(0)
    if inputmessage == 'q' or inputmessage == 'timeout' or inputmessage == '0':
        sender.reply('退出！')
        exit(0)
    numbers = re.findall(r'\d+', inputmessage)
    if numbers:
        numbers = [int(num) for num in numbers]
        num = numbers[0]
    else:
        sender.reply('输入错误！')
        exit(0)
    money = Decimal(num) * Decimal(Monthly)
    project = '出错！'
    if Decimal(money) == Decimal('0'):
        if osname == Meituan_os_mtname:
            project = '领券'
            delayed_date = empower(empowertime=Lingquantime, me_as_int=num)
            QLzt(osname=osname, value=f'{token}', userid=userid, account=f'{account}')
            middleware.bucketSet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}', value=f'{delayed_date}')
        if osname == Meituan_os_tbname:
            project = '团币'
            delayed_date = empower(empowertime=Tbtime, me_as_int=num)
            QLzt(osname=osname, value=f'{token}#{UUID}', userid=userid, account=f'{account}')
            middleware.bucketSet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}', value=f'{delayed_date}')
        sender.reply(
            f'=====订单完成=====\n🎈名称:{project}\n✨数量:{num}个月\n💰支付金额:{money}元')
        exit(0)
    else:
        if osname == Meituan_os_mtname:
            project = '领券'
            ordercoin = int(num) * int(Meituan_Lingquancoin)
            Deduction, usercoin = Pointpayment(ordercoin=ordercoin, usercoin=usercoin)
            if Deduction is True:
                cc = '积分'
                delayed_date = empower(empowertime=Lingquantime, me_as_int=num)
                middleware.bucketSet(bucket='Yzyxmm_sign_coin', key=f'{userid}', value=f'{usercoin}')
            else:
                cc = '元'
                zf(money=money, project=project, me_as_int=num)
                delayed_date = empower(empowertime=Lingquantime, me_as_int=num)
            QLzt(osname=osname, value=f'{token}', userid=userid, account=f'{account}')
            middleware.bucketSet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}', value=delayed_date)
        if osname == Meituan_os_tbname:
            project = '团币'
            ordercoin = int(num) * int(Meituan_tbcoin)
            Deduction, usercoin = Pointpayment(ordercoin=ordercoin, usercoin=usercoin)
            if Deduction is True:
                delayed_date = empower(empowertime=Tbtime, me_as_int=num)
                middleware.bucketSet(bucket='Yzyxmm_sign_coin', key=f'{userid}', value=f'{usercoin}')
                cc = '积分'
            else:
                cc = '元'
                zf(money=money, project=project, me_as_int=num)
                delayed_date = empower(empowertime=Tbtime, me_as_int=num)
            QLzt(osname=osname, value=f'{token}#{UUID}', userid=userid, account=f'{account}')
            middleware.bucketSet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}', value=delayed_date)

        sender.reply(
            f'=====订单完成=====\n🎈名称:{project}\n✨数量:{num}个月\n💰支付金额:{money}{cc}')
        exit(0)


def Pointpayment(ordercoin, usercoin):
    if int(ordercoin) <= int(usercoin):
        sender.reply(f'当前积分{usercoin}积分，订单所需{ordercoin}积分是否使用积分进行抵扣？')
        sender.reply('[y]是丨[n]否')
        yesorno = sender.input(120000, 1, False)
        if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
            usercoin = int(usercoin) - int(ordercoin)
            return True, usercoin
        else:
            return False, usercoin
    else:
        return False, usercoin


def zf(money, project, me_as_int):  # 等待支付并且发送ck到青龙
    zsm = middleware.bucketGet(bucket='MMjson', key='zsm')  # 获取发链接还是图片
    zfzt = sender.atWaitPay()
    if zfzt != True:
        if project == '单次领券':
            sender.reply(f'=====订单结算=====\n🎈名称:{project}\n✨数量:{me_as_int}\n💰应付:{money}元')
        else:
            sender.reply(f'=====订单结算=====\n🎈名称:{project}\n✨数量:{me_as_int}个月\n💰应付:{money}元')
        if zsm == 'true':
            sender.replyImage(Meituan_zsm)
        else:
            sender.reply(f'支付链接:{Meituan_zsm}')
        # 等待支付100秒
        ddzf = sender.waitPay("q", 100 * 1000)
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
        elif ddzf == 'timeout':
            sender.reply('支付超时！')
            exit(0)
    else:
        sender.reply('当前有人正在支付,请稍后再试！')
        exit(0)


def getUUID():
    def segmentation(UUIDurl):
        parsed_url1 = urlparse(UUIDurl)
        query_params1 = parse_qs(parsed_url1.query)
        utm_term_value1 = query_params1.get('utm_term', [''])[0]
        # 判断2024在utm_term的前半部分还是后半部分，并提取相应的64个字符
        if '2024' in utm_term_value1:
            index_2024 = utm_term_value1.index('2024')
            if index_2024 < len(utm_term_value1) / 2:
                start_index = index_2024 + 14
                end_index = start_index + 64
                uuid = utm_term_value1[start_index:end_index]
            else:
                end_index = index_2024
                start_index = max(0, end_index - 64)
                uuid = utm_term_value1[start_index:end_index]
        else:
            uuid = None
        return uuid

    def UUID(url):
        response = requests.get(url, allow_redirects=False)
        response.raise_for_status()
        redirect_url = response.headers.get('Location')
        uuid = segmentation(UUIDurl=redirect_url)
        return uuid

    sender.reply('请前往 美团APP-我的-团团赚-游戏中心右上角分享:')
    sender.replyImage('http://120.46.35.143:1212/UUID.png')
    inputmessage = sender.input(120000, 1, False)
    if '来团团赚玩更多游戏 您的好友邀请您来玩游戏！ http://dpurl.cn' in inputmessage:
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        # 使用正则表达式进行匹配
        urls = re.findall(url_pattern, inputmessage)
        url = urls[0]
        uuid = UUID(url)
    elif 'jumpUrl' in inputmessage:  # QQ的格式
        # 使用正则表达式提取 "jumpUrl" 的值
        jump_url = re.search(r'"jumpUrl":"(.*?)"', inputmessage).group(1)
        uuid = UUID(jump_url)
    elif '<url>' in inputmessage:
        # 使用字符串分割提取 <url> 标记之间的内容
        start_tag = "<url>"
        end_tag = "</url>"
        start_index = inputmessage.find(start_tag) + len(start_tag)
        end_index = inputmessage.find(end_tag)
        UUIDurl = inputmessage[start_index:end_index]
        uuid = segmentation(UUIDurl)
    else:
        uuid = None
        sender.reply('提取uuid失败，请联系管理员！')
        exit(0)
    return uuid


def Tbcx(usertoken):
    try:
        sing = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        url = "https://open.meituan.com/user/v1/info/auditting?fields=auditAvatarUrl%2CauditUsername"
        h = {
            'Connection': 'keep-alive',
            'Origin': 'https://mtaccount.meituan.com',
            'User-Agent': ua,
            'token': usertoken,
            'Referer': 'https://mtaccount.meituan.com/user/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,en-US;q=0.9',
            'X-Requested-With': 'com.sankuai.meituan',
        }
        r = requests.get(url, headers=h)

        MTdata = r.content
        MTjson = json.loads(MTdata)
        login = MTjson.keys()

        if "user" in login:
            rj = r.json()
            # 取usid
            usid = rj["user"]["id"]
            url1 = 'https://game.meituan.com/mgc/gamecenter/front/api/v1/login'
            h1 = {
                'Accept': 'application/json, text/plain, */*',
                'Content-Length': '307',
                'x-requested-with': 'XMLHttpRequest',
                'User-Agent': ua,
                'Content-Type': 'application/json;charset=UTF-8',
                'cookie': f'token={usertoken}'
            }
            data1 = {
                "mtToken": usertoken,
                "deviceUUID": '0000000000000A3467823460D436CAB51202F336236F6A167191373531985811',
                "mtUserId": usid,
                "idempotentString": sing
            }
            r1 = requests.post(url1, headers=h1, json=data1)
            actoken = r1.json()['data']['loginInfo']['accessToken']

            ###查询团币

            url2 = 'https://game.meituan.com/mgc/gamecenter/skuExchange/resource/counts?sceneId=3&gameId=10102'
            t_h = {
                # 'Accept': 'application/json, text/plain, */*',
                # 'x-requested-with': 'XMLHttpRequest',
                'User-Agent': ua,
                # 'Content-Type': 'application/json;charset=UTF-8',
                # 'mtgsig': '',
                'actoken': actoken,
                'mtoken': usertoken,
                # 'cookie': f'token={usertoken}'
            }
            r2 = requests.get(url2, headers=t_h)
            rj = r2.json()
            ttb = float(rj['data'][0]['count'])
            money = round(ttb / 1000, 2)
        else:
            ttb = "Token过期"
            money = "0"
        print(ttb, money)
        return int(ttb), money
    except Exception:
        return 'Token过期', '0'


def count_jrtb(usertoken):
    try:
        def get_coin_rec(usertoken, offset):
            headers = {
                'Host': 'game.meituan.com',
                'Accept': 'application/json, text/plain, */*',
                'X-Requested-With': 'XMLHttpRequest',
                'Sec-Fetch-Site': 'same-site',
                'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
                'Sec-Fetch-Mode': 'cors',
                'Content-Type': 'application/json',
                'Origin': 'https://awp.meituan.com',
                'User-Agent': ua,
                'Referer': 'https://awp.meituan.com/',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty'
            }
            params = {
                'yodaReady': 'h5',
                'csecplatform': '4',
                'csecversion': '2.3.1',
                'mtgsig': '{"a1":"1.1","a2":1703869899600,"a3":"1703667675570AAAUGGU868c0ee73ab28e1d0b03bc83148500067970","a5":"sES6rta18s7aMmHqRHX6","a6":"hs1.4a4gsvX1s4RLQYqBR3sFhAa3DMq/oCARZURaKrpiINxNiC0rXQnF5ffvc6Zi383ak+37Vcyy6mroJ3oQJHmnf1Ra37KQdKjE/bRI1E4RP7ho=","x0":4,"d1":"4eaa678b4abaf15b62bec14d041096d2"}',
            }
            json_data = {
                'mtToken': usertoken,
                'lastUpdateTime': int(time.time()) * 1000,
                'limit': 20,
                'offset': offset,
            }
            response = requests.post(
                'https://game.meituan.com/coin/billPage/getCoinAccountFlow',
                params=params,
                headers=headers,
                json=json_data,
            )
            record = response.json()
            if '身份验证失败' in response.text:
                record = 999
            return record

        TodayTb = 0
        current_time = datetime.now()
        todaytime = current_time.strftime("%Y-%m-%d")
        offset = 0
        while True:
            record = get_coin_rec(usertoken, offset)
            if record == 999:
                break
            else:
                recordlist = record['data']['coinChangeLogBOList']
                if len(recordlist) == 0:
                    break
                for recordjson in recordlist:
                    utimeGmt = recordjson['utimeGmt']
                    datetime_obj = datetime.strptime(utimeGmt, "%Y-%m-%d %H:%M:%S")
                    recordtime = datetime_obj.strftime("%Y-%m-%d")
                    if recordtime < todaytime:
                        break
                    else:
                        changeType = recordjson['changeType']
                        operationNote = recordjson['operationNote']
                        if changeType == 1:
                            if '退款' in operationNote:
                                continue
                            else:
                                changeAmount = recordjson['changeAmount']
                                TodayTb = changeAmount + TodayTb
                recordjson = recordlist[-1]
                utimeGmt = recordjson['utimeGmt']
                datetime_obj = datetime.strptime(utimeGmt, "%Y-%m-%d %H:%M:%S")
                recordtime = datetime_obj.strftime("%Y-%m-%d")
                if recordtime < todaytime:
                    break
                else:
                    offset = offset + 20
        while True:
            record = get_coin_rec(usertoken, offset)
            if record == 999:
                break
            else:
                recordlist = record['data']['coinChangeLogBOList']
                if len(recordlist) == 0:
                    break
                for recordjson in recordlist:
                    utimeGmt = recordjson['utimeGmt']
                    datetime_obj = datetime.strptime(utimeGmt, "%Y-%m-%d %H:%M:%S")
                    recordtime = datetime_obj.strftime("%Y-%m-%d")
                    if recordtime < todaytime:
                        break
                    else:
                        changeType = recordjson['changeType']
                        operationNote = recordjson['operationNote']
                        if changeType == 1:
                            if '退款' in operationNote:
                                continue
                            else:
                                changeAmount = recordjson['changeAmount']
                                TodayTb = changeAmount + TodayTb
                recordjson = recordlist[-1]
                utimeGmt = recordjson['utimeGmt']
                datetime_obj = datetime.strptime(utimeGmt, "%Y-%m-%d %H:%M:%S")
                recordtime = datetime_obj.strftime("%Y-%m-%d")
                if recordtime < todaytime:
                    break
                else:
                    offset = offset + 20
        Todaymoney = round(TodayTb / 1000, 2) if TodayTb != 0 else 0
        print(Todaymoney)
        return TodayTb, Todaymoney
    except Exception:
        return '查询失败', '0'


def cx(usertoken):
    TodayTb, Todaymoney = count_jrtb(usertoken)
    ttb, money = Tbcx(usertoken)
    return TodayTb, Todaymoney, ttb, money


def cxs():
    accounts = eval(uservalue)
    message = ''
    count = 1
    account3 = []
    account2 = []
    for account in accounts:
        token = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
        MTname, accountid, mobile = userdata(usertoken=token)
        if mobile == '查询失败':
            mobile = middleware.bucketGet(bucket='Yzyxmm_mt_mobile', key=f'{account}')
        Tbtime = middleware.bucketGet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}')
        if len(Tbtime) != 0 and Tbtime != '未开通' and Tbtime != '授权过期' and Tbtime > str(today_time):
            message += f'\n【{count}】丨{mobile}'
            count += 1
            account2.append(account)
        else:
            sender.reply(f'【{mobile}】团币云授权过期')
    if len(account2) == 1:
        account = account2[0]
        token = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
        mobile = middleware.bucketGet(bucket='Yzyxmm_mt_mobile', key=f'{account}')
        MTname = middleware.bucketGet(bucket='Yzyxmm_mt_MTname', key=f'{account}')
        TodayTb, Todaymoney, ttb, money = cx(token)
        if ttb == 'Token过期':
            sender.reply(f'【{mobile}】账号Token过期')
            exit(0)
        else:
            sender.reply(
                f'🤪用户名:{MTname}\n🔥用户ID:{mobile}\n💰团币余额:{ttb}({money})\n✨今日团币:{TodayTb}({Todaymoney})')
            exit(0)
    else:
        if message == '':
            exit(0)
        message_to_send = "=====团币查询=====\n" + '【0】丨全部账号' + message
        sender.reply(message_to_send)
        sender.reply('请输入[]内要查询的账号')
        inputmessage = sender.input(120000, 1, False)
        if inputmessage == 'q' or inputmessage == 'Q':
            sender.reply('退出查询！')
            exit(0)
        if inputmessage == '0':
            for account in account2:
                token = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
                TodayTb, Todaymoney, ttb, money = cx(token)
                mobile = middleware.bucketGet(bucket='Yzyxmm_mt_mobile', key=f'{account}')

                MTname = middleware.bucketGet(bucket='Yzyxmm_mt_MTname', key=f'{account}')
                if ttb == 'Token过期':
                    sender.reply(f'【{mobile}】账号Token过期')
                else:
                    sender.reply(
                        f'🤪用户名:{MTname}\n🔥用户ID:{mobile}\n💰团币余额:{ttb}({money})\n✨今日团币:{TodayTb}({Todaymoney})')
        else:
            try:
                me_as_int = int(inputmessage)
                if me_as_int > len(account2):
                    sender.reply('输入错误!')
                    exit(0)
            except ValueError:
                sender.reply('输入错误!')
                exit(0)
            account = account2[me_as_int - 1]
            token = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
            TodayTb, Todaymoney, ttb, money = cx(token)
            mobile = middleware.bucketGet(bucket='Yzyxmm_mt_mobile', key=f'{account}')
            MTname = middleware.bucketGet(bucket='Yzyxmm_mt_MTname', key=f'{account}')
            if ttb == 'Token过期':
                sender.reply(f'【{mobile}】账号Token过期')
                exit(0)
            else:
                sender.reply(
                    f'🤪用户名:{MTname}\n🔥用户ID:{mobile}\n💰团币余额:{ttb}({money})\n✨今日团币:{TodayTb}({Todaymoney})')


def oldmtt():
    sender.reply('检测到旧版本数据，正在更新数据！')
    accounts = eval(useroldvalue)
    newaccounts = []
    for account, item in accounts.items():
        token = item['token']
        MTname, accountid, mobile = userdata(token)
        MTname = item['MTname']
        Lingquantime = item['Lingquantime']
        Tbtime = item['Tbtime']
        middleware.bucketSet(bucket='Yzyxmm_mt_account', key=f'{account}', value=f'{token}')
        middleware.bucketSet(bucket='Yzyxmm_mt_MTname', key=f'{account}', value=f'{MTname}')
        middleware.bucketSet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}', value=f'{Lingquantime}')
        middleware.bucketSet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}', value=f'{Tbtime}')
        middleware.bucketSet(bucket='Yzyxmm_mt_mobile', key=f'{account}', value=f'{mobile}')
        newaccounts.append(str(account))
    middleware.bucketSet(bucket='Yzyxmm_mt_bind', key=f'{userid}', value=f'{newaccounts}')
    middleware.bucketDel(bucket='MMjson', key=f'{userid}')
    sender.reply('数据更新完成, 请重新唤起机器人！')


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


usermessage = sender.getMessage()
today_time = datetime.now().date()

if usermessage == '':
    usermessage = '1'
Meituan_tbmoney, Meituan_Lingquanmoney, Meituan_zsm, Meituan_os_mtname, Meituan_os_tbname, mt_managecommand, mt_querycommand, Mt_signcommand, randommanagecommand, randomsigncommand, randomquerycommand, Meituan_Lingquancoin, Meituan_tbcoin, mtloginmessage = getusercontent()
imtype = sender.getImtype()
if any(usermessage == s for s in Mt_signcommand.split('丨')):
    QLurl, qltoken = seekql()
    bindaccount()
elif any(usermessage == s for s in mt_managecommand.split('丨')):
    QLurl, qltoken = seekql()
    if len(useroldvalue) == 0:
        if len(uservalue) > 3:
            meituanmanage()
        else:
            sender.reply(f'未绑定美团账号，请发送’{randomsigncommand}‘进行账号绑定！')

    else:
        oldmtt()
elif any(usermessage == s for s in mt_querycommand.split('丨')):
    QLurl, qltoken = seekql()
    if len(useroldvalue) == 0:
        if len(uservalue) > 3:
            today_time = datetime.now().date()
            QLurl, qltoken = seekql()
            cxs()
        else:
            sender.reply(f'未绑定美团账号，请发送’{randomsigncommand}‘进行账号绑定！')
    else:
        oldmtt()
elif imtype == 'fake':

    QLurl, qltoken = seekql()
    today_time = datetime.now().date()
    userlist = middleware.bucketAllKeys(bucket='Yzyxmm_mt_bind')
    for user in userlist:

        uservalue = middleware.bucketGet(bucket='Yzyxmm_mt_bind', key=f'{user}')

        accounts = eval(uservalue)
        for account in accounts:
            token = middleware.bucketGet(bucket='Yzyxmm_mt_account', key=f'{account}')
            MTname = middleware.bucketGet(bucket='Yzyxmm_mt_MTname', key=f'{account}')
            mobile = middleware.bucketGet(bucket='Yzyxmm_mt_mobile', key=f'{account}')
            Lingquantime = middleware.bucketGet(bucket='Yzyxmm_mt_Lingquantime', key=f'{account}')
            Tbtime = middleware.bucketGet(bucket='Yzyxmm_mt_Tbtime', key=f'{account}')
            UUID = middleware.bucketGet(bucket='Yzyxmm_mt_UUID', key=f'{account}')

            if Lingquantime != '未开通' and Lingquantime != '授权过期' and len(Lingquantime) != 0:
                if Lingquantime < str(today_time):
                    qlid = allenvs(osname=Meituan_os_tbname, token=f'{token}', account=account)
                    if qlid is not None:
                        delenvs(qlid)
                    push(user, mobile, '美团领券云授权已过期,请及时续费！')

            if Tbtime != '未开通' and Tbtime != '授权过期' and len(Tbtime) != 0:
                if Tbtime < str(today_time):
                    qlid = allenvs(osname=Meituan_os_tbname, token=f'{token}#{UUID}', account=account)
                    if qlid is not None:
                        delenvs(qlid)
                    push(user, mobile, '美团团币云授权已过期,请及时续费！')
            MTname1, account1, mobile1 = userdata(token)
            if mobile1 == '查询失败':
                push(user, mobile, '美团账号Token过期,请及时更新！')

else:
    sender.setContinue()
