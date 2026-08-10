#[author: chuan]
#[version: 1.6.3]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg]
#[title: JD通用sign]
#[price: 0]
#[service: 2669943482]
#[priority: 999]
#[public: true] 
#[description: 介绍：目前支持自动评价，口令登陆，9R以及6dy自定义sign。<br/>接口地址：http://奥特曼地址:端口/jd/sign]
#[disable:false]
#[router: /jd/sign]请求路径
#[method: post]微服务方法
#[method: get]微服务方法

import middleware
import base64
import hashlib
import time
import random
import uuid
import json
from urllib.parse import quote_plus

string1 = "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/"
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

def randomstr(num):
    randomstr = ''.join(str(uuid.uuid4()).split('-'))[num:]
    return randomstr

def randomstr1(num):
    randomstr = ""
    for i in range(num):
        randomstr = randomstr + random.choice("abcdefghijklmnopqrstuvwxyz0123456789")
    return randomstr

def sign_core(inarg):
    key = b'80306f4370b39fd5630ad0529f77adb6'
    mask = [0x37, 0x92, 0x44, 0x68, 0xA5, 0x3D, 0xCC, 0x7F, 0xBB, 0xF, 0xD9, 0x88, 0xEE, 0x9A, 0xE9, 0x5A]
    array = [0 for _ in range(len(inarg))]
    for i in range(len(inarg)):
        r0 = int(inarg[i])
        r2 = mask[i & 0xf]
        r4 = int(key[i & 7])
        r0 = r2 ^ r0
        r0 = r0 ^ r4
        r0 = r0 + r2
        r2 = r2 ^ r0
        r1 = int(key[i & 7])
        r2 = r2 ^ r1
        array[i] = r2 & 0xff
    return bytes(array)

def base64Encode(string):
    return base64.b64encode(string.encode("utf-8")).decode('utf-8').translate(str.maketrans(string1, string2))

def base64Decode(string):
    return base64.b64decode(string.translate(str.maketrans(string1, string2))).decode('utf-8')

def randomeid():
    return 'eidAaf8081218as20a2GM%s7FnfQYOecyDYLcd0rfzm3Fy2ePY4UJJOeV0Ub840kG8C7lmIqt3DTlc11fB/s4qsAP8gtPTSoxu' % randomstr1(
        20)

def get_ep():
    ts = str(int(time.time() * 1000))
    area = ''.join(random.sample('0123456789', 2)) + '_' + ''.join(random.sample('0123456789', 4)) + '_' + ''.join(
        random.sample('0123456789', 5)) + '_' + ''.join(random.sample('0123456789', 4))
    
    d_brand_model = {
        "OPPO":["PAFM00","PDEM10","PDRM00","PENM00","PGW110"],
        "Xiaomi":["23078PND5G","2211133C","M1902F1A"],
        "HUAWEI":["LIO-AL00","OCE-AN10","JER-AN20","RTE-AL00"]
        }
    d_brand = random.choice(list(d_brand_model.keys()))
    d_model = random.choice(d_brand_model[d_brand])
    wifiBssid = "TP_LINK_".join(random.sample('0123456789ABCDEFG', 6))
    osVersion = random.choice(["10", "11", "12"])
    screen = random.choice(["640x1136", "750x1334", "1080x1920"])
    jduuid = randomstr(16)
    ep = json.dumps({
        "hdid": "JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=",
        "ts": ts,
        "ridx": -1,
        "cipher": {
            "area": base64Encode(area),
            "d_model": base64Encode(d_model),
            "wifiBssid": base64Encode(wifiBssid),
            "osVersion": base64Encode(osVersion),
            "d_brand":base64Encode(d_brand),
            "screen": base64Encode(screen),
            "uuid": base64Encode(jduuid),
            "aid": base64Encode(jduuid),
            "openudid": base64Encode(jduuid)
            },
        "ciphertype": 5,
        "version": "1.2.0",
        "appname": "com.jingdong.app.mall",
    }).replace(" ", "")
    return ep,ts,jduuid,d_brand

def get_sign(functionId, body, client:str="android", clientVersion:str='12.1.4'):
    if isinstance(body,dict):
        d = body
        body = json.dumps(body)
    else:
        d = json.loads(body)

    if "eid" in d:
        eid = d["eid"]
    else:
        eid = randomeid()

    ep,ts,jduuid,d_brand = get_ep()
    version = [[0, 2], [1, 1], [2, 0]]
    r1r2 = random.choice(version)
    r1 = r1r2[0]
    r2 = r1r2[1]
    sv = "1%s%s" % (r1, r2)
    all_arg = "functionId=%s&body=%s&uuid=%s&client=%s&clientVersion=%s&st=%s&sv=%s" % (functionId, body, jduuid, client, clientVersion, ts, sv)
    back_bytes = sign_core(str.encode(all_arg))
    sign = hashlib.md5(base64.b64encode(back_bytes)).hexdigest()

    ext = quote_plus('{"prstate":"0","pvcStu":"1"}')
    partner = d_brand.lower()
    convertUrl='body=%s&clientVersion=%s&client=%s&partner=%s&sdkVersion=31&lang=zh_CN&harmonyOs=0&networkType=wifi&oaid=%s&eid=%s&ef=1&ep=%s&st=%s&sign=%s&sv=%s' % (body, clientVersion, client, partner, jduuid, eid, quote_plus(ep), ts, sign, sv)

    result = {
        'code': 200,
        'fn': functionId,
        'body': convertUrl,
        'data': {
            'functionId': functionId,
            'body': body,
            'clientVersion': clientVersion,
            'client': client,
            'partner': partner,
            'sdkVersion': 31,
            'lang': 'zh_CN',
            'harmonyOs': 0,
            'networkType': 'wifi',
            'oaid': jduuid,
            'ef': 1,
            'ep': quote_plus(ep),
            'st': ts,
            'sign': sign,
            'sv': sv,
            'convertUrl': convertUrl
        },
        'msg': 'success'
    }
    return result

def main():
    if method == 'get':
        sender.reply('你的sign正常运行中......')
    elif method == 'post':
        body = sender.getRouterBody()
        params = sender.getRouterParams()
        try:
            if body:
                # print(f'📢收到sign请求 body')
                # print(f'请求数据 {body}')
                if isinstance(body, str):
                    body = json.loads(body)
                fn = body.get('fn')
                body = body.get('body')
            elif params:
                # print(f'📢收到sign请求 params')
                # print(f'请求数据 {params}')
                if isinstance(params, str):
                    params = json.loads(params)
                fn = params.get('functionId')
                body = params.get('body')
            else:
                return
        except:
            return
        sign = get_sign(fn,body)
        sender.reply(json.dumps(sign))

if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    # 获取路由
    router = sender.getRouterPath()
    method = sender.getRouterMethod()
    main()