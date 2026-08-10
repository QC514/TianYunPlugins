#[author: chuan]
#[version: 1.2.0]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg]
#[title: 京东口令解析]
#[class: 工具类]
#[price: 0]
#[service: 2669943482]
#[priority: 999]
#[public: true] 
#[description: 更新：解析后的链接送给奥特曼处理洞察。手动解析京东口令插件，已内置sign，支持京东，惊喜，特价，使用前请安装pycryptodome，requests依赖（python3）。命令：jx 口令，生成口令 活动链接]
#[disable:false]
#[admin: false]
#[rule: ^jx ?]
#[rule: ^生成口令 ?]

import re
import json
import uuid
import time
import time
import random
import base64
import hashlib
import requests
import middleware
import datetime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from urllib.parse import quote_plus

string1 = "KLMNOPQRSTABCDEFGHIJUVWXYZabcdopqrstuvwxefghijklmnyz0123456789+/"
string2 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

guuid = ''

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
    jduuid = randomstr(16)
    global guuid
    guuid = jduuid
    ts = str(int(time.time() * 1000))
    bsjduuid = base64Encode(jduuid)
    area = base64Encode('%s_%s_%s_%s' % (
        random.randint(1, 10000), random.randint(1, 10000), random.randint(1, 10000), random.randint(1, 10000)))
    d_model = random.choice(['Mi11Ultra', 'Mi11', 'Mi10'])
    d_model = base64Encode(d_model)
    return '{"hdid":"JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw=","ts":%s,"ridx":-1,"cipher":{"area":"%s","d_model":"%s","wifiBssid":"dW5hbw93bq==","osVersion":"CJS=","d_brand":"WQvrb21f","screen":"CtS1DIenCNqm","uuid":"%s","aid":"%s","openudid":"%s"},"ciphertype":5,"version":"1.2.0","appname":"com.jingdong.app.mall"}' % (
        int(ts) - random.randint(100, 1000), area, d_model, bsjduuid, bsjduuid, bsjduuid), jduuid, ts

def get_sign(functionId, body):
    body = json.dumps(body, ensure_ascii = False)
    client = 'android'
    clientVersion = '11.2.8'
    ep, suid, st = get_ep()
    sv = random.choice(["102", "111", "120"])
    all_arg = "functionId=%s&body=%s&uuid=%s&client=%s&clientVersion=%s&st=%s&sv=%s" % (
        functionId, body, suid, client, clientVersion, st, sv)
    back_bytes = sign_core(str.encode(all_arg))
    sign = hashlib.md5(base64.b64encode(back_bytes)).hexdigest()

    resultData = {}
    resultData['success'] = True
    resultData['message'] = '操作成功!'
    resultData['code'] = 200
    resultData['result'] = {}
    resultData['result']['st'] = st
    resultData['result']['functionId'] = functionId
    resultData['result']['sv'] = sv
    resultData['result']['sign'] = sign
    resultData['result']['client'] = client
    resultData['result']['body'] = body
    resultData['result']['clientVersion'] = clientVersion
    resultData['result']['uuid'] = guuid
    resultData['result']['ep'] = ep
    return resultData

def get_ts():
    current_datetime = datetime.datetime.now()
    one_month_later = current_datetime + datetime.timedelta(days=30)
    return int(one_month_later.timestamp() * 1000)

# aes加密
def aes_cbc_encrypt(plaintext):
    key = "5yKhoqodQjuHGlKZ"
    iv = "7WwXmH2TKSCIEJQ3"
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
    ciphertext = cipher.encrypt(pad(plaintext.encode(), AES.block_size))
    return base64.b64encode(ciphertext).decode()

def jComExchange(text):
    appCodes = ['jApp','jLite','jXi','jHealth']
    for appCode in appCodes:
        try:
            body = {"appCode":appCode,"commandType":0,"text":quote_plus(aes_cbc_encrypt(text))}
            params = get_sign('jComExchange',body)['result']
            url = 'https://api.m.jd.com/client.action'
            headers = {
                "Host":"api.m.jd.com",
                "Content-Type": "application/x-www-form-urlencoded",
                'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
            }
            data = f'body={quote_plus(json.dumps(body))}'
            res = requests.post(url,params=params,headers=headers,data=data).json()
            if res.get('code') == '0':
                return res.get('data')
            else:
                continue
        except:
            continue

def jCommand(url):
    try:
        body={
            "appCode": "jApp",
            "command":{
                "keyChannel": "Wxfriends",
                "keyContent": "未知活动",
                "keyEndTime": get_ts(),
                "keyId": url,
                "keyImg": "",
                "keyTitle": "京东用户",
                "sourceCode": "babel",
                "url": url
                }
            }
        api = 'https://api.m.jd.com/client.action'
        params = get_sign('jCommand',body)['result']
        headers = {
            "Host":"api.m.jd.com",
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
        }
        data = f'body={quote_plus(json.dumps(body))}'
        res = requests.post(api,params=params,headers=headers,data=data).json()
        if res.get('code') == '0':
            return res.get('data')
    except:
        return


def main():
    if 'jx' in Message:
        kl = sender.param(1)
        # 判断是否为口令
        pattern = r'[(|)|#|@|$|%|¥|￥|!|！][0-9a-zA-Z]{10,14}[(|)|#|@|$|%|¥|￥|!|！]'
        if re.findall(pattern,kl):
            try:
                res = jComExchange(kl)
                title = res.get('title')
                userName = res.get('userName')
                jumpUrl = res.get('jumpUrl')
                sender.reply(f'【标题】：{title}\n【来源】：{userName}\n【链接】：{jumpUrl}')
                sender.breakIn(jumpUrl)
            except:
                sender.reply('解析失败')
        else:
            sender.reply('好像不是京东口令哦')
    elif '生成口令' in Message:
        text = sender.param(1)
        kl = jCommand(text)
        if kl:
            sender.reply(kl)
        else:
            sender.reply('口令生成失败')


if __name__ == '__main__':
    senderID=middleware.getSenderID()
    sender=middleware.Sender(senderID)
    Message = sender.getMessage()
    kl = sender.param(1)
    main()