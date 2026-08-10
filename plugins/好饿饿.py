# [rule: ^.*cookie2=.*$]
# [rule: ^吃饱了$]
# [rule: ^我快饿死了$]
# [rule: ^夺宝信息$]
# [rule: ^(饿了.*|.*饿了)$]
# [cron: 28 8,18,21 * * *]
# [priority: 99999]
# [author: Lxg-021002]
# [title: 好饿饿]
# [version: 2.2.6]
# [class: 工具类]
# [platform: qq,qb,wx,tb,tg,web,wxmp]
# [public: true]
# [open_source: false]
# [price: 10.88]
# [icon: https://pp.myapp.com/ma_icon/0/icon_1029694_1725435529/256]
# [service:<img src="https://pic.fglt.net/common/a8/common_4_verify_icon.gif" border="0" /> <b>官方权威认证丨专业团队制作</b>  售后Q群951584089]
# [description: 如果需要账密续期 请在我的市场下载我的续期食用 增加提交 账号密码  (饿了管理>选择账号>提交账密)  也可以在ck中添加loginId=xxx;password=xxx;字段(即账号密码) 进行提交账密  绑定过一次账密之后 以后将不用再修改账密  提交普通app提取的ck即可(但ck中一定要有umt才可以续期)  如果需要账密续期 请在我的市场下载我的续期食用 不要频繁的更换设备登录 不保证其稳定性 还新增了提取某一个账号的ck  嗯...就这些 增加夺宝查询(常规查询)仅查询七天内的中奖记录，管理员可一键查询车上所有用户7天内的中奖记录(口令夺宝：信息)，  增加一键授权   容器上限优化，具体为: 以前是容器内所有ck超过设置数值则提示爆满，现在是只寻找相关变量名的ck提示爆满，现在是 当容器内有180个变量，150个乐园变量 变量上限设置为180 那么添加乐园变量不会提示爆满 增加了助力提交，优化了部分体验设计，改动较多BUG及时反馈！重写精简登陆逻辑，文字排版优化，查询性能优化，查询新增 今日总币 当前总币 全部明细 支持 查询丨删除 账号丨直接发送ck给机器人自动识别！吃饱了(查询)，我快饿死了(管理)，饿了查询，饿了管理 后续的任何使用问题都可以联系幼稚园小妹妹！使用前请安装py的sseclient依赖]


import middleware
from decimal import Decimal
import re
import urllib.parse
from datetime import datetime, timedelta
import hashlib
import json
import requests
import time
from urllib.parse import urlencode

# [param: {"required":true,"key":"Yzyxmm_elm.zsm","bool":true,"placeholder":"","name":"赞赏码发图或链接","desc":"勾选发图,不勾发链接"}]
# 赞赏码链接
# [param: {"required":true,"key":"Yzyxmm_elm.wx_zsm","bool":false,"placeholder":"必填项,http://xxxx.co/xxx.jpg","name":"收款方式","desc":"Wxbot赞赏码/收款码链接"}]
# 设置青龙容器
# [param: {"required":true,"key":"Yzyxmm_elm.elm_Qinglong","bool":false,"placeholder":"http://xxx.xx丨ClientID丨ClientSecret&http://xxx.xx丨ClientID丨ClientSecret","name":"设置对接容器","desc":"你的变量需要添加到的容器？参数用丨分割，这个符号是中文的竖(直接复制)，多容器用&分割"}]
# 乐园币价格
# [param: {"required":true,"key":"Yzyxmm_elm.elm_leyuanmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"乐园币价格","desc":"乐园币价格(单位:元)"}]
# 助力价格
# [param: {"required":true,"key":"Yzyxmm_elm.elm_zlmoney","bool":false,"placeholder":"例:0.88,不填为0元","name":"助力价格","desc":"助力价格(单位:元)"}]
# 容器上限
# [param: {"required":true,"key":"Yzyxmm_elm.elm_container_max","bool":false,"placeholder":"例:100,不填为180个","name":"单个容器变量上限","desc":"单个容器内可存放的Cookie上限\n当容器内达到上限用户再去支付将直接退款为积分，当然要保证积分系统为开启状态"}]
# 容器上限
# [param: {"required":true,"key":"Yzyxmm_elm.elm_zlcontainer_max","bool":false,"placeholder":"例:10,不填为5个","name":"助力容器上限","desc":"单个容器内可存放的助力Cookie上限\n当容器内达到上限用户再去支付将直接退款为积分，当然要保证积分系统为开启状态"}]
# 饿了么变量名称
# [param: {"required":true,"key":"Yzyxmm_elm.elm_leyuanosname","bool":false,"placeholder":"乐园和助力变量名不可一致！！！,默认elmck","name":"乐园币变量名","desc":"青龙容器内乐园币的变量名,默认elmck\n乐园和助力变量名不可一致！！！"}]
# 助力变量名称
# [param: {"required":true,"key":"Yzyxmm_elm.zlosname","bool":false,"placeholder":"乐园和助力变量名不可一致！！！,默认nczlck","name":"助力账号变量名","desc":"青龙容器内助力的变量名,默认nczlck\n乐园和助力变量名不可一致！！！"}]
# 饿了么需要多少积分一个月
# [param: {"required":true,"key":"Yzyxmm_elm.moneycoin","bool":false,"placeholder":"不填为关闭积分系统","name":"乐园币每月积分","desc":"乐园币一个月授权需要多少积分(只能为整数不能为小数)\n如果你要不想使用积分系统请什么都不要填写，也不要填类似99999的数字！"}]
# 助力需要多少积分一个月
# [param: {"required":true,"key":"Yzyxmm_elm.zlmoneycoin","bool":false,"placeholder":"不填为关闭积分系统","name":"助力每月积分","desc":"助力一个月授权需要多少积分(只能为整数不能为小数)如果你要不想使用积分系统请什么都不要填写，也不要填类似99999的数字！"}]
# ////////////////////////////////////////////////////////////////////
# //                          _ooOoo_                               //
# //                         o8888888o                              //
# //                         88" . "88                              //
# //                         (| ^_^ |)                              //
# //                         O\  =  /O                              //
# //                      ____/`---'\____                           //
# //                    .'  \\|     |//  `.                         //
# //                   /  \\|||  :  |||//  \                        //
# //                  /  _||||| -:- |||||-  \                       //
# //                  |   | \\\  -  /// |   |                       //
# //                  | \_|  ''\---/''  |   |                       //
# //                  \  .-\__  `-`  ___/-. /                       //
# //                ___`. .'  /--.--\  `. . ___                     //
# //              ."" '<  `.___\_<|>_/___.'  >'"".                  //
# //            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
# //            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
# //      ========`-.____`-.___\_____/___.-`____.-'========         //
# //                           `=---='                              //
# //      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
# //      佛祖保佑       屎山代码     永无BUG     永不修改               //
# ////////////////////////////////////////////////////////////////////


global QLurl
global qltoken


def getusercontent():
    # 包月价格
    elm_leyuanmoney = middleware.bucketGet(bucket='Yzyxmm_elm', key='elm_leyuanmoney')
    elm_zlmoney = middleware.bucketGet(bucket='Yzyxmm_elm', key='elm_zlmoney')
    elm_leyuanosname = middleware.bucketGet(bucket='Yzyxmm_elm', key='elm_leyuanosname')
    elm_zlosname = middleware.bucketGet(bucket='Yzyxmm_elm', key='zlosname')
    elm_container_max = middleware.bucketGet(bucket='Yzyxmm_elm', key='elm_container_max')
    elm_zlcontainer_max = middleware.bucketGet(bucket='Yzyxmm_elm', key='elm_zlcontainer_max')
    moneycoin = middleware.bucketGet(bucket='Yzyxmm_elm', key='moneycoin')
    zlmoneycoin = middleware.bucketGet(bucket='Yzyxmm_elm', key='zlmoneycoin')
    # 收款码链接
    wx_zsm = middleware.bucketGet(bucket='Yzyxmm_elm', key='wx_zsm')
    zsm = middleware.bucketGet(bucket='Yzyxmm_elm', key='zsm')
    if len(elm_leyuanmoney) == 0 or elm_leyuanmoney == '0':
        elm_leyuanmoney = Decimal('0')
    if len(elm_zlmoney) == 0 or elm_zlmoney == '0':
        elm_zlmoney = Decimal('0')
    if len(elm_leyuanosname) == 0:
        elm_leyuanosname = 'elmck'
    if len(elm_zlosname) == 0:
        elm_zlosname = 'nczlck'
    if len(moneycoin) == 0:
        moneycoin = 9999999
    if len(zlmoneycoin) == 0:
        zlmoneycoin = 9999999
    if len(elm_container_max) == 0 or elm_container_max == '0':
        elm_container_max = 180
    else:
        elm_container_max = int(elm_container_max)
    if len(elm_zlcontainer_max) == 0 or elm_zlcontainer_max == '0':
        elm_zlcontainer_max = 5
    else:
        elm_zlcontainer_max = int(elm_zlcontainer_max)
    randommanagecommand = '我快饿死了'
    randomquerycommand = '吃饱了'
    return zsm, wx_zsm, elm_leyuanmoney, elm_leyuanosname, moneycoin, randommanagecommand, randomquerycommand, elm_container_max, elm_zlmoney, elm_zlosname, zlmoneycoin, elm_zlcontainer_max


def seekql():
    try:
        qljson = {}
        Qinglong = middleware.bucketGet(bucket="Yzyxmm_elm", key="elm_Qinglong")
        if len(Qinglong) == 0:
            sender.reply('饿了么插件未填写插件对接的容器，请检查配参')
            exit(0)
        else:
            qllist = Qinglong.split('&')
            for index, ql in enumerate(qllist, start=1):
                try:

                    delimiters = ['丨', '|', '#', '＃']
                    Delimiter = next((d for d in delimiters if d in ql), None)
                    qls = ql.split(Delimiter)
                    QLurl = qls[0]
                    ClientID = qls[1]
                    ClientSecret = qls[2]
                    qltoken = QLtoken(QLurl=QLurl, ClientID=ClientID, ClientSecret=ClientSecret)
                    qljson[QLurl] = qltoken
                except Exception as e:
                    middleware.notifyMasters(
                        content=f'好饿饿检查发现第{index}个容器无法链接: {ql}请检查！',
                        imtypes=['wb', 'tg', 'qb', 'qq'])
            return qljson
    except Exception:
        sender.reply("获取青龙token失败")
        exit(0)


def delenvs(qlid, QLurl, qltoken):
    if qlid is None:
        return
    url = f"{QLurl}/open/envs"
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    data = [qlid]
    response = requests.delete(url, headers=headers, json=data).json()
    # sender.reply(f'删除账号{response}')
    code = response['code']
    if code == 200:
        print('删除成功')


# 获取发送者ID
senderID = middleware.getSenderID()
# 创建发送者
sender = middleware.Sender(senderID)
# 获取发送者QQ号
userid = sender.getUserID()


def req(cookie, api, data_str, v="1.0"):
    def hbh5tk(tk_cookie, enc_cookie, cookie_str):
        """
        合并带_m_h5_tk
        """
        txt = cookie_str.replace(" ", "")
        txt = txt.replace("chushi;", "")
        txt = txt.replace("zhuli;", "")
        txt = txt.replace("zhuli", "")
        if txt[-1] != ';':
            txt += ';'
        cookie_parts = txt.split(';')[:-1]
        updated = False
        for i, part in enumerate(cookie_parts):
            key_value = part.split('=')
            if key_value[0].strip() in ["_m_h5_tk", " _m_h5_tk"]:
                cookie_parts[i] = tk_cookie
                updated = True
            elif key_value[0].strip() in ["_m_h5_tk_enc", " _m_h5_tk_enc"]:
                cookie_parts[i] = enc_cookie
                updated = True

        if updated:
            return ';'.join(cookie_parts) + ';'
        else:
            return txt + tk_cookie + ';' + enc_cookie + ';'

    def check_cookie(cookie):
        url = "https://waimai-guide.ele.me/h5/mtop.alsc.personal.queryminecenter/1.0/?jsv=2.6.2&appKey=12574478"
        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.87 Safari/537.36"
        }

        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                cookie_jar = response.cookies
                token = cookie_jar.get('_m_h5_tk', '')
                token_cookie = "_m_h5_tk=" + token
                enc_token = cookie_jar.get('_m_h5_tk_enc', '')
                enc_token_cookie = "_m_h5_tk_enc=" + enc_token
                cookie = hbh5tk(token_cookie, enc_token_cookie, cookie)
                return cookie
            else:
                return None
        except Exception as e:
            print(f"解析ck错误{e}")
            return None

    def tq1(cookie_string):
        """
        获取_m_h5_tk
        """

        if not cookie_string:
            return '-1'
        cookie_pairs = cookie_string.split(';')
        for pair in cookie_pairs:
            key_value = pair.split('=')
            if key_value[0].strip() in ["_m_h5_tk", " _m_h5_tk"]:
                return key_value[1]
        return '-1'

    def md5(text):
        """
        md5加密
        """
        hash_md5 = hashlib.md5()
        hash_md5.update(text.encode())
        return hash_md5.hexdigest()

    try:
        cookie = check_cookie(cookie)
        headers = {
            "authority": "shopping.ele.me",
            "accept": "application/json",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "no-cache",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": cookie,
            "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; SM-G955U Build/R16NW) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36"
        }
        timestamp = int(time.time() * 1000)
        # data_str = json.dumps(data)
        token = tq1(cookie)
        token_part = token.split("_")[0]

        sign_str = f"{token_part}&{timestamp}&12574478&{data_str}"
        sign = md5(sign_str)
        url = f"https://guide-acs.m.taobao.com/h5/{api}/{v}/?jsv=2.6.1&appKey=12574478&t={timestamp}&sign={sign}&api={api}&v={v}&type=originaljson&dataType=json"
        data1 = urlencode({'data': data_str})
        r = requests.post(url, headers=headers, data=data1)
        if r:
            return r
        else:
            return None
    except Exception as e:
        return None


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
            sender.reply('链接青龙失败,请检查青龙配参！')
            exit(0)
    except Exception:
        sender.reply("链接青龙失败,请检查青龙配参！")
        exit(0)


def QLupdate(QLurl, qltoken, osname, value, account, qlid):
    qlurl = f"{QLurl}/open/envs"
    data = {
        "value": value,
        "name": osname,
        "remarks": f'饿了么管理丨用户:{userid}丨账号:{account}',
        "id": qlid
    }
    headers = {
        "Authorization": "Bearer" + ' ' + qltoken,
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.put(qlurl, headers=headers, data=json.dumps(data))
    qlurl2 = f"{QLurl}/open/envs/enable"
    data2 = [qlid]
    response2 = requests.put(qlurl2, headers=headers, json=data2)
    if response.status_code == 200:
        response_json = response.json()
        data = response_json['data']
        if data is None:
            exit(0)
        qlid = data['id']
        # createdAt = data['createdAt']
        qlurl2 = f"{QLurl}/open/envs/enable"
        return qlid


def QLzt(QLurl, qltoken, osname, value, account):  # 添加青龙变量
    try:
        qlurl = f"{QLurl}/open/envs"
        data = [{
            "value": value,
            "name": osname,
            "remarks": f'饿了么管理丨用户:{userid}丨账号:{account}'
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


def Addenvs(osname, value, account, OrderPoints=0):
    qlid = None
    QLurl = None
    qltoken = None
    for QLurl, qltoken in qljson.items():
        url = f"{QLurl}/open/envs"
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json"
        }
        response = requests.get(url=url, headers=headers).json()

        if response['code'] == 200:
            envslist = response['data']
            for envs in envslist:
                remarks = envs['remarks']
                envname = envs['name']
                if remarks is None:
                    continue

                if str(account) in remarks and osname == envname:
                    qlid = envs['id']
                    break
            if qlid is not None:
                break
        else:
            sender.reply('连接青龙获取变量失败')
            exit(0)

    if qlid is None:
        for idx, (QLurl, qltoken) in enumerate(qljson.items()):

            url = f"{QLurl}/open/envs"
            headers = {
                "Authorization": "Bearer" + ' ' + qltoken,
                "accept": "application/json"
            }
            response = requests.get(url=url, headers=headers).json()
            if response['code'] == 200:
                envslist = response['data']
                if osname == elm_zlosname:
                    count = sum(1 for item in envslist if item['name'] == elm_zlosname)
                    # for envs in envslist:
                    #     if envs['name'] == elm_zlosname:
                    #         zlnum += 1
                    if count < elm_zlcontainer_max:
                        QLzt(QLurl, qltoken, osname, value, account)
                        break

                    else:
                        if idx == len(qljson) - 1:
                            usercoin = middleware.bucketGet(bucket='Yzyxmm_sign_coin', key=f'{userid}')
                            if len(usercoin) == 0:
                                usercoin = 0
                            if zlmoneycoin == 9999999 or zlmoneycoin == 0:
                                sender.reply('当前服务容器内乐园账号已达上限，请联系管理员处理！')
                            else:
                                usercoin = int(usercoin) + int(OrderPoints)
                                middleware.bucketSet(bucket='Yzyxmm_sign_coin', key=f'{userid}', value=str(usercoin))
                                sender.reply('当前服务容器内账号已达上限，该次支付已经退为积分！')
                                sender.reply(f'当前积分{usercoin}！')
                            exit(0)
                        else:
                            continue
                elif osname == elm_leyuanosname:
                    count = sum(1 for item in envslist if item['name'] == elm_leyuanosname)
                    if count < elm_container_max:
                        QLzt(QLurl, qltoken, osname, value, account)
                        break
                    else:
                        if idx == len(qljson) - 1:
                            # sender.reply('当前全部容器内的助力Cookie均已爆满，请联系管理员清理！')
                            usercoin = middleware.bucketGet(bucket='Yzyxmm_sign_coin', key=f'{userid}')
                            if len(usercoin) == 0:
                                usercoin = 0
                            if moneycoin == 9999999 or moneycoin == 0:
                                sender.reply('当前服务容器内乐园账号已达上限，请联系管理员处理！')

                            else:
                                usercoin = int(usercoin) + int(OrderPoints)
                                middleware.bucketSet(bucket='Yzyxmm_sign_coin', key=f'{userid}', value=str(usercoin))
                                sender.reply('当前服务容器内账号已达上限，该次支付已经退为积分！')
                                sender.reply(f'当前积分{usercoin}！')
                            exit(0)
                        else:
                            continue

            else:
                sender.reply('连接青龙获取变量失败')
                exit(0)

    else:
        QLupdate(QLurl, qltoken, osname, value, account, qlid)


def allenvs(osname, token, account):
    qlid = None
    QLurl = None
    qltoken = None
    for QLurl, qltoken in qljson.items():
        url = f"{QLurl}/open/envs"
        headers = {
            "Authorization": "Bearer" + ' ' + qltoken,
            "accept": "application/json"
        }
        response = requests.get(url=url, headers=headers).json()
        if response['code'] == 200:
            envslist = response['data']
            for envs in envslist:
                remarks = envs['remarks']
                envname = envs['name']
                if remarks is None:
                    continue
                if str(account) in remarks and osname == envname:
                    qlid = envs['id']
                    break
            if qlid is not None:
                break

        else:
            sender.reply('连接青龙获取变量失败')
            exit(0)
    return qlid, QLurl, qltoken


def userdata(cookie):
    try:
        r = req(cookie, 'mtop.alsc.user.detail.query', json.dumps({}), v="1.0")
        if '过期' in r.text:
            return '查询失败', '查询失败', '查询失败'
        encryptMobile = r.json()['data']['encryptMobile']
        localId = r.json()['data']['localId']
        userName = r.json()['data']['userName']

        return str(localId), encryptMobile, userName
    except Exception:
        return '查询失败', '查询失败', '查询失败'


def tq2(txt):
    """
    拆分cookie，将字符串形式的Cookie解析为字典。
    """
    try:
        # 去除多余的标识符并清理空格
        txt = txt.replace(" ", "").replace("zhuli;", "").replace("zhuli", "").replace("chishi;", "")

        # 确保以分号结尾
        if not txt.endswith(';'):
            txt += ';'

        # 拆分成键值对，移除最后的空字符串
        pairs = txt.split(";")[:-1]
        ck_json = {}

        # 遍历键值对，拆分为键和值，并去掉两边的多余空格
        for pair in pairs:
            if "=" in pair:  # 确保是合法的键值对
                key, value = pair.split("=", 1)
                ck_json[key.strip()] = value.strip()
            else:
                raise ValueError(f"无效的键值对: {pair}")

        return ck_json
    except Exception as e:
        # 返回具体错误信息，方便调试
        print(f'Cookie解析错误: {e}')
        return {}


def sign(cookie):


    def accvip(Newaddition):
        if len(zlaccountVip) != 0 and zlaccountVip >= str(now_time):
            Addenvs(osname=elm_zlosname, value=cookie, account=account)
        if len(accountVip) != 0 and accountVip >= str(now_time):
            Addenvs(osname=elm_leyuanosname, value=cookie, account=account)

            if Newaddition:
                accounts.append(account)
                sender.reply(f'🤪{bind}添加成功！\n————————————————\n» 可发送‘饿了管理’进行管理！')
            else:
                sender.reply(f'🤪{bind}更新成功！\n————————————————\n» 可发送‘饿了管理’进行管理！')

        else:
            if Newaddition:
                accounts.append(account)
                sender.reply(f'🤪{bind}添加成功！\n————————————————\n» 暂未授权‘饿了管理’进行授权！')
            else:
                sender.reply(f'🤪{bind}更新成功！\n————————————————\n» 授权过期‘饿了管理’进行续期！')

        middleware.bucketSet(bucket='Yzyxmm_elm_bind', key=userid, value=f'{accounts}')


    account, bind, username = userdata(cookie)
    if account == '查询失败':
        if 'loginId' in cookie and 'password' in cookie and 'umt' in cookie:
            ck_json = tq2(cookie)
            account = ck_json['USERID']
            bind = ck_json['loginId']
            bind = bind[:3] + "*" * 4 + bind[7:]
            password = f'{ck_json["loginId"]}#{ck_json["password"]}'
            middleware.bucketSet(bucket='Yzyxmm_elm_password', key=f'{account}',
                                 value=password)
        else:
            sender.reply('用户信息查询失败,请检查Cookie后重试！')
            exit(0)
    uservalue = middleware.bucketGet(bucket='Yzyxmm_elm_bind', key=userid)
    accountVip = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=f'{account}')
    zlaccountVip = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=f'{account}')
    passwords = middleware.bucketGet(bucket='Yzyxmm_elm_password', key=f'{account}')
    middleware.bucketSet(bucket='Yzyxmm_elm_phone', key=f'{account}', value=f'{bind}')
    middleware.bucketSet(bucket='Yzyxmm_elm_account', key=f'{account}', value=f'{cookie}')

    if len(passwords) != 0:
        passwordlist = passwords.split('#')
        phone = passwordlist[0]
        password = passwordlist[1]
        cookie += f'loginId={phone};password={password};'
        middleware.bucketSet(bucket='Yzyxmm_elm_account', key=f'{account}', value=f'{cookie}')
    if len(uservalue) == 0:
        accounts = []
        accvip(True)
    else:
        accounts = eval(uservalue)
        if account in accounts:
            accvip(False)
        else:
            accvip(True)
    '''else:
        exit(0)'''


def getaccountmes(account):
    cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=f'{account}')
    accsvip = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=f'{account}')
    zlaccsvip = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=f'{account}')
    bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{account}')
    if len(accsvip) == 0:
        accsvip = '未授权'
    elif accsvip < str(now_time):
        accsvip = '授权过期'

    if len(zlaccsvip) == 0:
        zlaccsvip = '未授权'
    elif accsvip < str(now_time):
        zlaccsvip = '授权过期'

    return cookie, bind, accsvip, zlaccsvip


def empower2(empowertime, me_as_int):
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


def inputm(mes, long=99999999999, count=99999999999):
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


def Pointpayment2(OrderPoints):
    usercoin = middleware.bucketGet(bucket='Yzyxmm_sign_coin', key=f'{userid}')

    if len(usercoin) != 0 and usercoin != '0':
        if int(usercoin) >= int(OrderPoints):
            sender.reply(f'当前积分{usercoin}积分，订单所需{OrderPoints}积分是否使用积分进行抵扣？')
            sender.reply('[y]是丨[n]否')
            if inputm(''):
                usercoin = int(usercoin) - int(OrderPoints)
                middleware.bucketSet(bucket='Yzyxmm_sign_coin', key=f'{userid}',
                                     value=f'{usercoin}')
                # accountVip = empower(empowertime=accountVip, me_as_int=me_as_int)
                # middleware.bucketSet(bucket='Yzyxmm_xydj_Vip', key=account, value=accountVip)
                # Addenvs(osname=osname, value=token, account=account, phone=phone)
                # sender.reply(f'————《订单完成》————\n🎈名称:星芽授权\n🎉数量:{mation_int}月\n💰支付金额:{zfcoin}积分')
                return True
    return False


def zf2(project, me_as_int, money):
    zfzt = sender.atWaitPay()
    if money == 0:
        return
    if not zfzt:
        sender.reply(f'————《订单信息》————\n🎈名称:{project}\n🎉数量:{me_as_int}\n💰应付:{money}元')
        if zsm == 'true':
            sender.replyImage(wx_zsm)
        else:
            sender.reply(f'支付链接:{wx_zsm}')
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


def manage():
    # 获取绑定的所有账号
    accounts = middleware.bucketGet(bucket='Yzyxmm_elm_bind', key=userid)
    message = ''
    count = 1
    if len(accounts) != 0:
        accounts = acclist = eval(accounts)
        for accid in acclist:
            cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=accid)
            accsvip = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=accid)
            zlaccsvip = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=f'{accid}')
            bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{accid}')
            password = middleware.bucketGet(bucket='Yzyxmm_elm_password', key=f'{accid}')
            if len(accsvip) == 0:
                accsvip = '未授权'
            elif accsvip < str(now_time):
                accsvip = '授权过期'

            if len(zlaccsvip) == 0:
                zlaccsvip = '未授权'
            elif accsvip < str(now_time):
                zlaccsvip = '授权过期'
            account, binds, username = userdata(cookie)
            if account == '查询失败':
                accountst = 'Cookie过期'
            else:
                accountst = '状态正常'
            if len(password) == 0:
                password = '还没提交'
            else:
                password = '已经提交'
            bind = bind[:3] + "*" * 4 + bind[7:]
            message += f'【{count}】      ———\n🤪用户ID:{bind}\n🪫账号状态:{accountst}\n🔥账密状态:{password}\n☁助力授权:{zlaccsvip}\n☁乐园授权:{accsvip}\n'
            count = count + 1
        message_to_send = f"———《饿了管理》———\n乐园:{elm_leyuanmoney}元/月丨助力:{elm_zlmoney}元/月\n{message}"
        sender.reply(message_to_send)
        sender.reply('请输入【】中需要管理的账号:\n【a】一键授权丨【q】退出执行')
        mations = sender.input(120000, 1, False)
        if mations == 'q':
            sender.reply('退出！')
            exit(0)
        elif mations is None:
            sender.reply('超时,退出！')
            exit(0)
        elif mations == 'a' or mations == 'A':
            sender.reply('【1】丨授权乐园\n【2】丨授权助力')
            option = sender.input(120000, 1, False)
            if option not in ['1', '2']:
                sender.reply('输入错误！')
                exit(0)
            sender.reply('请输入每个账号需要的月数,例: 1')
            mation = sender.input(120000, 1, False)
            if option == '1':
                try:
                    mation_int = int(mation)
                    money = Decimal(mation) * Decimal(elm_leyuanmoney) * Decimal(len(accounts))
                    order = OrderPoints = int(moneycoin) * int(mation_int) * len(accounts)
                except ValueError:
                    sender.reply('输入错误！')
                    exit(0)
                if money == Decimal('0'):
                    for account in accounts:
                        cookie, bind, accsvip, zlaccsvip = getaccountmes(account)
                        accsvip = empower2(accsvip, mation_int)
                        Addenvs(osname=elm_leyuanosname, value=cookie, account=account)
                        middleware.bucketSet(bucket='Yzyxmm_elm_svip', key=account, value=accsvip)
                else:
                    Deduction = Pointpayment2(OrderPoints)
                    if not Deduction:
                        zf2(project='批量乐园', me_as_int=len(accounts) * int(mation_int), money=money)
                    for account in accounts:
                        cookie, bind, accsvip, zlaccsvip = getaccountmes(account)
                        accsvip = empower2(accsvip, mation_int)
                        Addenvs(osname=elm_leyuanosname, value=cookie, account=account, OrderPoints=OrderPoints)
                        middleware.bucketSet(bucket='Yzyxmm_elm_svip', key=account, value=accsvip)
                        OrderPoints -= int(moneycoin)
                    if not Deduction:
                        sender.reply(
                            f'———《订单完成》———\n🎈名称:批量乐园\n🎉数量:{len(accounts) * int(mation_int)}月\n💰支付金额:{money}元')
                    else:
                        sender.reply(
                            f'———《订单完成》———\n🎈名称:批量乐园\n🎉数量:{len(accounts) * int(mation_int)}月\n💰支付金额:{order}积分')
            elif option == '2':
                try:
                    mation_int = int(mation)
                    money = Decimal(mation) * Decimal(elm_zlmoney) * Decimal(len(accounts))

                    order = OrderPoints = int(zlmoneycoin) * int(mation_int) * len(accounts)

                except ValueError:
                    sender.reply('输入错误！')
                    exit(0)
                if money == Decimal('0'):
                    for account in accounts:
                        cookie, bind, accsvip, zlaccsvip = getaccountmes(account)
                        accsvip = empower2(zlaccsvip, mation_int)
                        Addenvs(osname=elm_zlosname, value=cookie, account=account)
                        middleware.bucketSet(bucket='Yzyxmm_elm_vip', key=account, value=accsvip)
                else:
                    Deduction = Pointpayment2(OrderPoints)
                    if not Deduction:
                        zf2(project='批量助力', me_as_int=len(accounts) * int(mation_int), money=money)

                    for account in accounts:
                        cookie, bind, accsvip, zlaccsvip = getaccountmes(account)
                        accsvip = empower2(zlaccsvip, mation_int)
                        Addenvs(osname=elm_zlosname, value=cookie, account=account, OrderPoints=OrderPoints)
                        middleware.bucketSet(bucket='Yzyxmm_elm_vip', key=account, value=accsvip)
                        OrderPoints -= int(zlmoneycoin)
                    if not Deduction:
                        sender.reply(
                            f'———《订单完成》———\n🎈名称:批量助力\n🎉数量:{len(accounts) * int(mation_int)}月\n💰支付金额:{money}元')
                    else:
                        sender.reply(
                            f'———《订单完成》———\n🎈名称:批量助力\n🎉数量:{len(accounts) * int(mation_int)}月\n💰支付金额:{order}积分')
            else:
                sender.reply('输入错误！')





        else:
            try:
                mation_int = int(mations)
                mation_int = mation_int - 1
                account = acclist[mation_int]
                cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=f'{account}')

                accsvip = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=f'{account}')
                zlaccsvip = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=f'{account}')
                bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{account}')
                password = middleware.bucketGet(bucket='Yzyxmm_elm_password', key=f'{account}')
                if len(accsvip) == 0:
                    accsvip = '未授权'
                elif accsvip < str(now_time):
                    accsvip = '授权过期'
                if len(zlaccsvip) == 0:
                    zlaccsvip = '未授权'
                elif accsvip < str(now_time):
                    zlaccsvip = '授权过期'
                accountzt, binds, username = userdata(cookie)
                if accountzt == '查询失败':
                    accountst = 'Cookie过期'
                else:
                    accountst = '状态正常'
                if len(password) == 0:
                    password = '还没提交'
                else:
                    password = '已经提交'
                '''ck_json = tq2(cookie)
                 passwords = password.split('#')
                ck_json['loginId'] = passwords[0]
                ck_json['password'] = passwords[1]
                cookie = ''
                for field, value in ck_json.items():
                    cookie += f"{field}={value};"
                bind = bind[:3] + "*" * 4 + bind[7:]'''
                sender.reply(
                    f'🤪用户ID:{bind}\n🪫账号状态:{accountst}\n🔥账密状态:{password}\n☁助力授权:{zlaccsvip}\n☁乐园授权:{accsvip}')

                sender.reply('【1】授权乐园\n【2】授权助力\n【3】提交账密\n【4】我要Cookie\n【5】删除账号\n【q】退出')

                mation = sender.input(120000, 1, False)
                if mation == '1':
                    # 开通乐园币
                    sender.reply('请输入需要的月数,例: 1')
                    mation = sender.input(120000, 1, False)
                    try:
                        mation_int = int(mation)
                        money = Decimal(mation) * Decimal(elm_leyuanmoney)
                        if money == Decimal('0'):
                            empower(empowertime=accsvip, account=account, cookie=cookie, mation_int=mation_int,
                                    phone=bind, osname=elm_leyuanosname, project='Yzyxmm_elm_svip')
                        else:
                            OrderPoints = int(moneycoin) * int(mation_int)
                            Pointpayment(mation_int, accsvip, cookie, account, bind, moneycoin, elm_leyuanosname,
                                         OrderPoints=OrderPoints)
                            zf(money=money, osname=elm_leyuanosname, mation_int=mation_int)
                            empower(empowertime=accsvip, account=account, cookie=cookie, mation_int=mation_int,
                                    phone=bind, osname=elm_leyuanosname, project='Yzyxmm_elm_svip',
                                    OrderPoints=OrderPoints)
                        sender.reply(
                            f'———《订单完成》———\n🎈名称:乐园币\n🎉数量:{mation_int}月\n💰支付金额:{money}元')
                    except ValueError:
                        sender.reply('输入错误')
                elif mation == '2':
                    try:
                        sender.reply('请输入需要的月数,例: 1')
                        mation = sender.input(120000, 1, False)
                        mation_int = int(mation)
                        money = Decimal(mation) * Decimal(elm_zlmoney)
                        if money == Decimal('0'):
                            empower(empowertime=zlaccsvip, account=account, cookie=cookie, mation_int=mation_int,
                                    phone=bind, osname=elm_zlosname, project='Yzyxmm_elm_vip')
                        else:
                            OrderPoints = int(zlmoneycoin) * int(mation_int)
                            Pointpayment(mation_int, zlaccsvip, cookie, account, bind, zlmoneycoin, elm_zlosname,
                                         OrderPoints=OrderPoints)
                            zf(money=money, osname=elm_zlosname, mation_int=mation_int)
                            empower(empowertime=zlaccsvip, account=account, cookie=cookie, mation_int=mation_int,
                                    phone=bind, osname=elm_zlosname, project='Yzyxmm_elm_vip', OrderPoints=OrderPoints)
                        sender.reply(
                            f'———《订单完成》———\n🎈名称:乐园助力\n🎉数量:{mation_int}月\n💰支付金额:{money}元')
                    except ValueError:
                        sender.reply('输入错误')
                elif mation == '3':
                    loginId = str(inputm('请输入11位手机号:', long=11))
                    password = str(inputm('请输入密码:'))
                    ck_json = tq2(cookie)
                    ck_json['loginId'] = loginId
                    ck_json['password'] = password
                    cookie = ''
                    for field, value in ck_json.items():
                        cookie += f"{field}={value};"
                    # cookie += f'loginId={loginId};password={password};'

                    middleware.bucketSet(bucket='Yzyxmm_elm_password', key=f'{account}', value=f'{loginId}#{password}')
                    middleware.bucketSet(bucket='Yzyxmm_elm_account', key=f'{account}', value=f'{cookie}')
                    if accsvip != '未授权' and accsvip != '授权过期':
                        Addenvs(osname=elm_leyuanosname, value=cookie, account=account)
                    if zlaccsvip != '未授权' and zlaccsvip != '授权过期':
                        Addenvs(osname=elm_zlosname, value=cookie, account=account)
                    sender.reply('账密提交成功！此功能不会检查账号密码的正确性,请自行检查！')
                elif mation == '4':
                    sender.reply(cookie)
                elif mation == '5':
                    sender.reply(
                        '请确认是否删除该账号？账号删除后授权时间会一同删除，这条信息将会通知管理员处理\n[y]确认丨[n]退出')
                    mation = sender.input(120000, 1, False)
                    if mation == 'y':
                        acclist.remove(f'{account}')
                        # 寻找青龙变量
                        qlid, QLurl, qltoken = allenvs(osname=elm_leyuanosname, token=cookie, account=account)
                        delenvs(qlid=qlid, QLurl=QLurl, qltoken=qltoken)
                        qlid, QLurl, qltoken = allenvs(osname=elm_zlosname, token=cookie, account=account)
                        delenvs(qlid=qlid, QLurl=QLurl, qltoken=qltoken)
                        if len(acclist) == 0:
                            middleware.bucketDel(bucket='Yzyxmm_elm_bind', key=userid)
                        else:
                            middleware.bucketSet(bucket='Yzyxmm_elm_bind', key=userid, value=f'{acclist}')
                        middleware.bucketDel(bucket='Yzyxmm_elm_account', key=f'{account}')
                        middleware.bucketDel(bucket='Yzyxmm_elm_vip', key=f'{account}')
                        middleware.bucketDel(bucket='Yzyxmm_elm_svip', key=f'{account}')
                        middleware.bucketDel(bucket='Yzyxmm_elm_vip', key=f'{account}')
                        middleware.notifyMasters(
                            content=f'用户:{userid}来自:{imtype}删除了一个账号，请您进行联系下一步的处理',
                            imtypes=['wb', 'tg', 'qb', 'qq'])
                        sender.reply('账号删除成功，并且已经告知管理员！')
                    elif mation == 'n':
                        sender.reply('退出！')
                    else:
                        sender.reply('输入错误')
                elif mation == 'q':
                    sender.reply('退出！')
                else:
                    sender.reply('输入错误！')
            except ValueError as e:
                sender.reply('输入错误')
    else:
        sender.reply('暂未绑定饿了么账号，请获取Cookie后直接发给我！')


def Pointpayment(mation_int, accsvip, cookie, account, bind, coin, osname, OrderPoints, batch=False):
    if osname == elm_leyuanosname:

        project = 'Yzyxmm_elm_svip'
        name = '乐园币'
        if batch:
            name = f'全部{name}'
    else:
        project = 'Yzyxmm_elm_vip'
        name = '乐园助力'
        if batch:
            name = f'全部{name}'
    usercoin = middleware.bucketGet(bucket='Yzyxmm_sign_coin', key=f'{userid}')
    if len(usercoin) != 0 and usercoin != '0':
        zfcoin = int(coin) * mation_int
        if int(usercoin) >= int(zfcoin):
            sender.reply(f'当前积分{usercoin}积分，订单所需{zfcoin}积分是否使用积分进行抵扣？')
            sender.reply('[y]是丨[n]否')
            yesorno = sender.input(120000, 1, False)
            if yesorno == 'Y' or yesorno == 'y' or yesorno == '是':
                usercoin = int(usercoin) - int(zfcoin)
                middleware.bucketSet(bucket='Yzyxmm_sign_coin', key=f'{userid}',
                                     value=f'{usercoin}')
                empower(empowertime=accsvip, account=account, cookie=cookie, mation_int=mation_int, phone=bind,
                        osname=osname, project=project, OrderPoints=OrderPoints, batch=batch)
                sender.reply(f'———《订单完成》———\n🎈名称:{name}\n🎉数量:{mation_int}月\n💰支付金额:{zfcoin}积分')
                exit(0)
            elif yesorno == 'n' or yesorno == 'N' or yesorno == '否':
                # 不使用积分抵扣
                return


def empower(empowertime, account, cookie, mation_int, phone, osname, project, OrderPoints=0, batch=False):
    day = mation_int * 30
    Addenvs(osname=osname, value=cookie, account=account, OrderPoints=OrderPoints)
    if empowertime == '授权过期' or empowertime == '未授权' or empowertime <= str(now_time):
        # 将当前时间延后
        new_time = now_time + timedelta(days=day)
        middleware.bucketSet(bucket=project, key=f'{account}',
                             value=str(new_time))
    elif empowertime > str(now_time):
        empower_date = datetime.strptime(empowertime, "%Y-%m-%d")
        delayed_date = empower_date + timedelta(days=day)
        new_time = delayed_date.date()
        middleware.bucketSet(bucket=project, key=f'{account}',
                             value=str(new_time))
    else:
        sender.reply('出错')
        exit(0)


def zf(money, osname, mation_int):  # 等待支付并且发送ck到青龙、
    zfzt = sender.atWaitPay()
    if osname == elm_leyuanosname:
        project = '乐园币'
    else:
        project = '乐园助力'
    if zfzt != True:
        sender.reply(f'———《订单结算》———\n🎈名称:{project}\n🎉数量:{mation_int}月\n💰应付:{money}元')
        if zsm == 'true':
            sender.replyImage(wx_zsm)
        else:
            sender.reply(f'支付链接:{wx_zsm}')
        # 等待支付120秒
        ddzf = sender.waitPay("q", 120 * 1000)

        if 'Time' in str(ddzf):
            try:
                zfjson = json.loads(ddzf)
                zfmoney = zfjson['Money']
            except Exception:
                zfmoney = ddzf['Money']
            if int(zfmoney) == int(money):
                # sender.reply('支付金额正确')
                return
            else:
                sender.reply(f'支付金额错误\n应付:{money}元\n实付:{zfmoney}元\n请联系管理员处理退款！')
                exit(0)

        elif ddzf is None:
            sender.reply('支付超时！')
            exit(0)
        else:
            sender.reply('退出支付')
            exit(0)
    else:
        sender.reply('当前有人正在支付,请稍后再试！')
        exit(0)


def signs(mh5tk, ts, data):
    # data = {"templateIds": "[\"1404\"]"}
    data_str = json.dumps(data, separators=(',', ':'))

    e = mh5tk + "&" + ts + "&" + '12574478' + "&" + data_str
    sign = hashlib.md5(e.encode()).hexdigest()
    return sign


def res(header, cookie):
    str_header = str(header)
    mh5tk = re.search(r'_m_h5_tk=([^_]+)', str_header).group(1)
    regex1 = r'_m_h5_tk=[0-9a-f]+_[0-9]+;'
    regex2 = r'_m_h5_tk_enc=[0-9a-f]+;'
    str1 = re.search(regex1, str_header).group(0)
    str2 = re.search(regex2, str_header).group(0)
    cookie = re.sub(r'_m_h5_tk=[^;]+;?', '', cookie)
    cookie = re.sub(r'_m_h5_tk_enc=[^;]+;?', '', cookie)
    cookie = str1 + str2 + cookie
    return cookie, mh5tk


def eatapi(cookie):
    try:
        todayeat = 0
        respnse = req(cookie, 'mtop.alibaba.svip.langrisser.query', json.dumps({
            "lgrsRequestItems": "[{\"backup\":false,\"count\":1,\"data\":{\"needHead\":true,\"month\":\"\"},\"resId\":\"867018\"}]",
            "latitude": "33.76706790179014",
            "longitude": "114.37013771384954"}),
                      v="1.0")

        if '未登录' in respnse.text:
            eatcount = '查询失败'
        else:

            eat = respnse.json()
            eatcount = eat['data']['data']['867018']['data'][0]['peaCount']

            records = eat['data']['data']['867018']['data'][0]['accountMonthRecords'][0]['records']

            if records is None:
                return eatcount, '0'
            for eats in records:
                createdTime = eats['createdTime']
                datetime_obj = datetime.strptime(createdTime, "%Y-%m-%d %H:%M:%S")
                recordtime = datetime_obj.strftime("%Y-%m-%d")
                if recordtime < str(now_time):
                    break
                else:
                    count = eats['count']
                    optType = eats['optType']
                    if optType == 2:
                        continue
                    else:
                        todayeat = todayeat + int(count)

        return eatcount, todayeat
    except Exception as e:
        print(e)
        return '查询错误', '查询错误'


def bbf(cookie):
    try:
        url = 'https://wallet.ele.me/api/storedcard/queryBalanceBycardType?cardType=platform'
        headers = {
            "cookie": cookie,
        }
        respnse = requests.get(url=url, headers=headers)
        if '未登录' in respnse.text or '成功' not in respnse.text:
            money = '- -'
        else:
            wallet = respnse.json()
            money = wallet['data']['totalAvailableAmount'] / 100
        return money
    except Exception:
        return '查询错误'


def leyuanB(cookie):
    try:
        mh5tk = 'a8b654ea8b2d8897556edb7eed592e4e'

        for _ in range(2):
            ts = str(time.time() * 1000)
            data = {"templateIds": "[\"1404\"]"}
            sign = signs(mh5tk, ts, data)
            url = f'https://mtop.ele.me/h5/mtop.koubei.interaction.center.common.queryintegralproperty.v2/1.0/?jsv=2.7.0&appKey=12574478&t={ts}&sign={sign}&api=mtop.koubei.interaction.center.common.queryintegralproperty.v2&v=1.0&ecode=1&type=json&valueType=string&needLogin=true&LoginRequest=true&dataType=jsonp'
            headers = {
                "Host": "mtop.ele.me",
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
                "Cookie": cookie,
            }
            data = "data=%7B%22templateIds%22%3A%22%5B%5C%221404%5C%22%5D%22%7D"
            response = requests.post(url, headers=headers, data=data)
            if '调用成功' in response.text:
                leyuan = response.json()
                count = leyuan['data']['data']['1404']['count']

                return count

            else:
                header = response.headers
                cookie, mh5tk = res(header, cookie)
    except Exception:
        return '查询错误'


def Orchard_inquiry(cookie):
    try:
        r = req(cookie, 'mtop.alsc.playgame.orchard.index.batch.query', json.dumps({
            "blockRequestList": "[{\"blockCode\":\"603040_6723057310\",\"status\":\"PUBLISH\",\"tagCallWay\":\"SYNC\",\"useRequestBlockTags\":false}]",
            "source": "KB_ORCHARD", "bizCode": "main",
            "locationInfos": "[{\"latitude\":\"99.597472842782736\",\"longitude\":\"99.75325090438128\",\"lat\":\"99.597472842782736\",\"lng\":\"99.75325090438128\"}]",
            "extData": "{\"ORCHARD_ELE_MARK\":\"KB_ORCHARD\",\"orchardVersion\":\"20240624\"}"}), v="1.0")
        for tag_data in r.json()["data"]["data"]["603040_6723057310"]["blockData"]["role"]["tagData"]:
            for result in tag_data["result"]:
                for role_info in result["roleInfoDtoList"]:
                    for cc in role_info["rolePropertyInfoDtoList"]:
                        remainingProgress = role_info['roleLevelExpInfoDto']["remainingProgress"]
                        levelName = role_info['roleLevelExpInfoDto']["levelName"]
                        return f"\n🍒果树进度:{100 - remainingProgress:.2f}/{levelName}"
        return f"\n🍒果树进度:- -"
    except Exception as e:
        return f"\n🍒果树进度:- -"


def WinningTheTreasureHunt(cookie):
    try:
        WinningInformations = ''

        def get_dates():
            today = datetime.today()
            date_format = "%Y-%m-%d"

            # 生成从今天开始的7天日期列表
            dates = [(today - timedelta(days=i)).strftime(date_format) for i in range(7)]

            return dates

        date = get_dates()
        data = json.dumps(
            {"bizScene": "duobao_external", "blockList": "[\"participants\",\"wonDetail\",\"noWonPrize\"]",
             "channel": "ELMC",
             "pageSize": "50", "rightId": ""})
        api = 'mtop.koubei.interactioncenter.snatch.mine.page'
        res = req(cookie, api, data, v="1.0")
        for prizes in res.json()['data']['list']:
            if prizes['status'] in ['ONLINE', 'DRAWN']:
                continue
            for sj in date:
                if sj in prizes['baseInfo']['awardTime']:
                    title = prizes['baseInfo']['title']
                    if prizes['awardStatus'] in ['not_won_wait_accept', 'not_won_has_finished']:  # 没中奖
                        continue
                    elif prizes['awardStatus'] == 'won_has_finished':  # 中奖

                        WinningInformations += f'\n🍡夺宝中奖:{title}'
                    else:  # 可能中奖了
                        # print(prizes['awardStatus'])
                        WinningInformations += f'\n🍡夺宝中奖:{title}'
        if WinningInformations == '':
            return '\n🍡夺宝中奖:- -'
        return WinningInformations
    except Exception as e:
        sender.reply(f'{e}')
        return '\n🍡夺宝中奖:- -'


def OrchardExchangeVoucher(cookie):
    try:
        respnse = req(cookie, 'mtop.koubei.interaction.center.common.queryintegralproperty.v2',
                      json.dumps({"templateIds": "[\"497\"]"}), v="1.0")
        count = respnse.json()['data']['data']['497']['count']
        return f"\n🌸果园兑换卡:{count}"

    except Exception:
        return f"\n🌸果园兑换卡:- -"


def todayreques(cookie):
    try:
        Bdetailed = {}
        pageNo = 1
        retrynum = 0
        todayleyuanB = 0
        mh5tk = 'a8b654ea8b2d8897556edb7eed592e4e'
        while True:
            ts = str(time.time() * 1000)
            data = {"templateId": "1404", "bizScene": "game_center", "convertType": "GAME_CENTER",
                    "startTime": "2023-1-5 00:00:00", "pageNo": str(pageNo), "pageSize": "100"}
            sign = signs(mh5tk, ts, data)
            url = f'https://mtop.ele.me/h5/mtop.koubei.interaction.center.common.querypropertydetail/1.0/5.0/?jsv=2.7.0&appKey=12574478&t={ts}&sign={sign}&api=mtop.koubei.interaction.center.common.querypropertydetail&v=1.0&ecode=1&type=json&valueType=string&needLogin=true&LoginRequest=true&dataType=jsonp'
            headers = {
                "Host": "mtop.ele.me",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
                "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
                "Origin": "https://tb.ele.me",
                "Referer": "https://tb.ele.me/",
                "Accept-Language": "zh-CN,zh-Hans;q=0.9",
                "x-ele-check-client": "ele",
                "Content-Length": "214",
                "Connection": "keep-alive",
                "Cookie": cookie
            }
            data = f'{{"templateId":"1404","bizScene":"game_center","convertType":"GAME_CENTER","startTime":"2023-1-5 00:00:00","pageNo":"{pageNo}","pageSize":"100"}}'
            # 对字符串进行URL编码
            encoded_string = urllib.parse.quote(data, safe='')
            response = requests.post(url, headers=headers, data=f'data={encoded_string}')
            if '调用成功' in response.text:
                tleyuan = response.json()
                list = tleyuan['data']['list']
                if len(list) == 0:
                    return todayleyuanB, Bdetailed
                for details in list:
                    gmtModifiedStr = details['gmtModifiedStr']
                    datetime_obj = datetime.strptime(gmtModifiedStr, "%Y-%m-%d %H:%M:%S")
                    recordtime = datetime_obj.strftime("%Y-%m-%d")
                    if recordtime < str(now_time):
                        return todayleyuanB, Bdetailed
                    else:
                        amount = details['amount']
                    detailType = details['detailType']
                    if detailType == 'REDUCE':
                        continue
                    else:
                        bizName = details['extInfo']['desc']
                        bizName = bizName.replace("玩一玩", "")
                        bizName = bizName.replace("玩", "")
                        # if '签到' not in bizName:
                        # bizName = bizName[1:]
                        if bizName in Bdetailed:
                            Bdetailed[bizName] = Bdetailed[bizName] + int(amount)
                        else:
                            Bdetailed[bizName] = int(amount)

                        todayleyuanB = todayleyuanB + int(amount)
                detailss = list[-1]
                gmtModifiedStr = detailss['gmtModifiedStr']
                datetime_obj = datetime.strptime(gmtModifiedStr, "%Y-%m-%d %H:%M:%S")
                recordtime = datetime_obj.strftime("%Y-%m-%d")
                if recordtime < str(now_time):
                    return todayleyuanB, Bdetailed
                else:
                    pageNo = pageNo + 1
                    continue

            else:
                if retrynum == 2:
                    exit(0)
                retrynum = retrynum + 1
                header = response.headers
                cookie, mh5tk = res(header, cookie)
    except Exception as e:
        print(e)
        return '查询错误', '查询错误'


def Checkcoupons():
    message = f'🌸大额券:'
    try:
        res = req(cookie, 'mtop.alsc.personal.querypasslist4native', json.dumps(
            {"condition": "", "cityCode": "411600", "latitude": "33.76706790179014", "tabCode": "HONG_BAO",
             "userId": "6011282906", "extInfo": "", "longitude": "114.37013771384954", "sourceFrom": "ELEME_APP",
             "userGeoHash": "ww124e1g3mey"}))
        for Coupons in res.json()['data']['data']['vouchers_list_component']['fields']['items']:
            Couponamount = Coupons['amountText']['yuanText']
            message += f'[{Couponamount}]'
        return message
    except Exception:
        message += f'--'


def cx(cookie):
    money = bbf(cookie)
    eatcount, todayeat = eatapi(cookie)
    count = leyuanB(cookie)
    todayleyuanB, Bdetailed = todayreques(cookie)
    return count, money, eatcount, todayeat, todayleyuanB


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


def cxs():
    # 获取绑定的所有账号
    accounts = middleware.bucketGet(bucket='Yzyxmm_elm_bind', key=userid)
    message = ''
    count = 4
    if len(accounts) != 0:
        acclist = eval(accounts)
        for accid in acclist:
            cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=accid)
            bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{accid}')
            bind = bind[:3] + "*" * 4 + bind[7:]
            message += f'\n【{count}】丨{bind}'
            count = count + 1
        message_to_send = f"———《饿了查询》———\n【0】常规全部【1】今日总币\n【2】当前总币【3】今日明细{message}"
        sender.reply(message_to_send)
        sender.reply('请输入【】中需要查询的账号:')
        mations = sender.input(120000, 1, False)

        if mations == '0':
            sender.reply('正在获取数据....')
            acclist = eval(accounts)
            for account in acclist:
                cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=f'{account}')
                accsvip = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=f'{account}')
                zlaccsvip = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=account)
                count = '查询失败'
                eatcount = '查询失败'
                money = '查询失败'
                todayeat = '查询失败'
                todayleyuanB = '查询失败'
                if len(accsvip) == 0:
                    count = accsvip = '未授权'
                elif accsvip < str(now_time):
                    count = accsvip = '云授权过期'
                if len(accsvip) == 0:
                    count = accsvip = '未授权'
                elif accsvip < str(now_time):
                    count = accsvip = '云授权过期'
                if len(zlaccsvip) == 0:
                    zlaccsvip = '未授权'
                elif zlaccsvip < str(now_time):
                    zlaccsvip = '云授权过期'
                account2, bind, username = userdata(cookie)
                if account2 == '查询失败':
                    bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{account}')
                    bind = bind[:3] + "*" * 4 + bind[7:]
                    sender.reply(
                        f'【{bind}】账号Cookie过期')
                else:
                    if accsvip not in ['未授权', '云授权过期'] or zlaccsvip not in ['未授权', '云授权过期']:
                        count, money, eatcount, todayeat, todayleyuanB = cx(cookie)

                        sender.reply(
                            f'🤪用户ID:{bind}\n📒今日乐园币:{todayleyuanB}\n🎈乐园币:{count}\n🔥今日吃货豆:{todayeat}\n🎉饿了吃货豆:{eatcount}{Orchard_inquiry(cookie)}{OrchardExchangeVoucher(cookie)}\n💰钱包余额:{money}{WinningTheTreasureHunt(cookie)}')

                        bind = bind[:3] + "*" * 4 + bind[7:]

                    else:
                        bind = bind[:3] + "*" * 4 + bind[7:]
                        sender.reply(
                            f'【{bind}】账号{accsvip}')
        elif mations == '1' or mations == '2' or mations == '3':
            sender.reply('正在努力获取数据....')
            acclist = eval(accounts)
            message = ''
            AlltodayleyuanB = 0
            AllleyuanB = 0
            todayleyuanB = 0
            success = 0
            for account in acclist:

                cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=f'{account}')
                accsvip = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=f'{account}')
                zlaccsvip = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=f'{account}')
                count = '查询失败'
                eatcount = '查询失败'
                money = '查询失败'
                todayeat = '查询失败'
                todayleyuanB = '查询失败'
                if len(accsvip) == 0:
                    count = accsvip = '未授权'
                elif accsvip < str(now_time):
                    count = accsvip = '云授权过期'
                if len(zlaccsvip) == 0:
                    zlaccsvip = '未授权'
                elif zlaccsvip < str(now_time):
                    zlaccsvip = '云授权过期'
                account2, bind, username = userdata(cookie)
                if account2 == '查询失败':
                    bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{account}')
                    bind = bind[:3] + "*" * 4 + bind[7:]
                    sender.reply(
                        f'【{bind}】账号Cookie过期')
                else:

                    if accsvip not in ['未授权', '云授权过期'] or zlaccsvip not in ['未授权', '云授权过期']:
                        if mations == '1':
                            todayleyuanB, Bdetailed = todayreques(cookie)
                            if todayleyuanB == '查询错误':
                                sender.reply(f'【{bind}】查询出错')
                                continue
                            bind = bind[:3] + "*" * 4 + bind[7:]
                            success += 1
                            message += f'\n【{bind}】丨{todayleyuanB}'
                            AlltodayleyuanB += todayleyuanB
                        if mations == '2':
                            leyuanBs = leyuanB(cookie)
                            if leyuanBs == '查询错误':
                                sender.reply(f'【{bind}】查询出错')
                                continue
                            success += 1
                            bind = bind[:3] + "*" * 4 + bind[7:]
                            message += f'\n【{bind}】丨{leyuanBs}'
                            AllleyuanB += leyuanBs
                        if mations == '3':
                            message = ''
                            todayleyuanB, Bdetailed = todayreques(cookie)
                            if todayleyuanB == '查询错误':
                                sender.reply(f'【{bind}】查询出错')
                                continue
                            if todayleyuanB == 0:
                                sender.reply(f'【{bind}】今日0币')
                                continue

                            bind = bind[:3] + "*" * 4 + bind[7:]
                            for key, value in Bdetailed.items():
                                message += f'\n【{key}】丨{value}'
                            sender.reply(f'———《{bind}》———\n【今日总币】丨{todayleyuanB}{message}')
                    else:
                        bind = bind[:3] + "*" * 4 + bind[7:]
                        sender.reply(
                            f'【{bind}】账号{accsvip}')
            if mations == '1':
                if success != 0:
                    sender.reply(f'【今日总币】丨{AlltodayleyuanB}{message}')

            if mations == '2':
                if success != 0:
                    sender.reply(f'【当前总币】丨{AllleyuanB}{message}')

        else:

            try:
                mation_int = int(mations)
                mation_int = mation_int - 4
                account = acclist[mation_int]
                sender.reply('正在努力获取数据...')
                cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=account)
                bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{account}')
                accsvip = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=account)
                zlaccsvip = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=f'{account}')

                if len(accsvip) == 0:
                    count = accsvip = '未授权'
                elif accsvip < str(now_time):
                    count = accsvip = '云授权过期'
                if len(zlaccsvip) == 0:
                    zlaccsvip = '未授权'
                elif zlaccsvip < str(now_time):
                    zlaccsvip = '云授权过期'

                account2, bind, username = userdata(cookie)
                if account2 == '查询失败':
                    bind = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{account}')
                    bind = bind[:3] + "*" * 4 + bind[7:]
                    sender.reply(
                        f'【{bind}】Cookie过期')
                else:
                    if accsvip not in ['未授权', '云授权过期'] or zlaccsvip not in ['未授权', '云授权过期']:
                        count, money, eatcount, todayeat, todayleyuanB = cx(cookie)
                        bind = bind[:3] + "*" * 4 + bind[7:]
                        sender.reply(
                            f'🤪用户ID:{bind}\n📒今日乐园币:{todayleyuanB}\n🎈乐园币:{count}\n🔥今日吃货豆:{todayeat}\n🎉饿了吃货豆:{eatcount}{Orchard_inquiry(cookie)}{OrchardExchangeVoucher(cookie)}\n💰钱包余额:{money}{WinningTheTreasureHunt(cookie)}')

                    else:
                        bind = bind[:3] + "*" * 4 + bind[7:]
                        sender.reply(
                            f'【{bind}】账号{accsvip}')
            except ValueError:
                sender.reply('输入错误！')




    else:
        sender.reply('未绑定饿了么账号，请获取Cookie后直接发给我！')


def AlluserTreasureHunt():
    sender.reply('正在检索所有用户的中奖信息，该过程时间较长 请耐心等待...')
    message = ''
    bindlist = middleware.bucketAllKeys(bucket='Yzyxmm_elm_bind')
    # bindlist = eval(bindlist)
    for user in bindlist:
        accouts = middleware.bucketGet(bucket='Yzyxmm_elm_bind', key=f'{user}')
        accouts = eval(accouts)
        # sender.reply(f'正在检索{user}的中奖信息...')
        UserHeader = f'\n{user}:'
        for account in accouts:
            # sender.reply(f'正在检索{account}的中奖信息...')
            '''if len(accsvip) == 0:
                accsvip = '未授权'
            elif accsvip < str(now_time):
                accsvip = '云授权过期'
            if len(accsvip) == 0:
                accsvip = '未授权'
            elif accsvip < str(now_time):
                accsvip = '云授权过期'
            if len(zlaccsvip) == 0:
                zlaccsvip = '未授权'
            elif zlaccsvip < str(now_time):
                zlaccsvip = '云授权过期'''
            cookie, bind, accsvip, zlaccsvip = getaccountmes(account)
            # sender.reply(f'正在检索{bind}的中奖信息...')
            if accsvip in ['未授权', '授权过期'] and zlaccsvip in ['未授权', '授权过期']:
                continue
            account, bind, username = userdata(cookie)

            if account == '查询失败':
                continue
            WinningInformations = WinningTheTreasureHunt(cookie)
            if WinningInformations == '\n🍡夺宝中奖:- -':
                continue
            UserHeader += f"\n———《{bind}》———{WinningInformations}"
            # UserHeader += accountheader
        if UserHeader == f'\n{user}:':
            continue
        message += UserHeader
    if message == '':
        sender.reply('检索所有用户均无中奖信息')
        exit(0)
    sender.reply(f'{message}')


today_date = datetime.now().date()
today_time = str(today_date)
now_time = datetime.now().date()
qljson = seekql()
zsm, wx_zsm, elm_leyuanmoney, elm_leyuanosname, moneycoin, randommanagecommand, randomquerycommand, elm_container_max, elm_zlmoney, elm_zlosname, zlmoneycoin, elm_zlcontainer_max = getusercontent()
imtype = sender.getImtype()
usermessage = sender.getMessage()
messageID = sender.getMessageID()
if 'cookie2=' in usermessage and 'SID=' in usermessage and 'USERID=' in usermessage:
    A = sender.recallMessage(messageID)
    sign(usermessage)
elif '我快饿死了' in usermessage or '管理' in usermessage:
    manage()
elif '吃饱了' in usermessage or '查询' in usermessage:
    cxs()
elif '夺宝' in usermessage:
    if sender.isAdmin():
        AlluserTreasureHunt()
    else:
        sender.reply('无权使用！')




elif imtype == 'fake':
    bindlist = middleware.bucketAllKeys(bucket='Yzyxmm_elm_bind')
    for user in bindlist:
        accouts = middleware.bucketGet(bucket='Yzyxmm_elm_bind', key=f'{user}')
        accoutlist = eval(accouts)
        for useraccount in accoutlist:
            cookie = middleware.bucketGet(bucket='Yzyxmm_elm_account', key=f'{useraccount}')
            phone = middleware.bucketGet(bucket='Yzyxmm_elm_phone', key=f'{useraccount}')
            empower = middleware.bucketGet(bucket='Yzyxmm_elm_svip', key=f'{useraccount}')
            zlempower = middleware.bucketGet(bucket='Yzyxmm_elm_vip', key=f'{useraccount}')
            account, bind, username = userdata(cookie)
            if '查询失败' in bind:
                push(user=user, mobile=phone, message='饿了么Cookie已过期,请及时更新！')
            if len(empower) == 0:
                pass
            elif str(now_time) > empower:
                qlid, QLurl, qltoken = allenvs(osname=elm_leyuanosname, token=cookie, account=useraccount)
                delenvs(qlid=qlid, QLurl=QLurl, qltoken=qltoken)
                push(user=user, mobile=phone, message=f'饿了么授权已过期,可发送‘{randommanagecommand}’进行授权！')
            if len(zlempower) == 0:
                pass
            elif str(now_time) > zlempower:
                qlid, QLurl, qltoken = allenvs(osname=elm_zlosname, token=cookie, account=useraccount)
                delenvs(qlid=qlid, QLurl=QLurl, qltoken=qltoken)
                push(user=user, mobile=phone, message=f'饿了么助力授权已过期,可发送‘{randommanagecommand}’进行授权！')

else:
    sender.setContinue()
# ////////////////////////////////////////////////////////////////////
# //                          _ooOoo_                               //
# //                         o8888888o                              //
# //                         88" . "88                              //
# //                         (| ^_^ |)                              //
# //                         O\  =  /O                              //
# //                      ____/`---'\____                           //
# //                    .'  \\|     |//  `.                         //
# //                   /  \\|||  :  |||//  \                        //
# //                  /  _||||| -:- |||||-  \                       //
# //                  |   | \\\  -  /// |   |                       //
# //                  | \_|  ''\---/''  |   |                       //
# //                  \  .-\__  `-`  ___/-. /                       //
# //                ___`. .'  /--.--\  `. . ___                     //
# //              ."" '<  `.___\_<|>_/___.'  >'"".                  //
# //            | | :  `- \`.;`\ _ /`;.`/ - ` : | |                 //
# //            \  \ `-.   \_ __\ /__ _/   .-` /  /                 //
# //      ========`-.____`-.___\_____/___.-`____.-'========         //
# //                           `=---='                              //
# //      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        //
# //      佛祖保佑       屎山代码     永无BUG     永不修改               //
# ////////////////////////////////////////////////////////////////////


