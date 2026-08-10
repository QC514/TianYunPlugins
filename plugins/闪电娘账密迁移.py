#[author: chuan]
#[version: 1.0.1]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg]
#[admin: true]
#[title: 闪电娘账密迁移]
#[priority: 999]
#[rule: ^闪电娘账密迁移$]
#[price: 0]
#[service: 2669943482]
#[public:true]
#[description: 指令：闪电娘账密迁移。]
#[disable:true]

import json
import middleware
from urllib.parse import unquote_plus

senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)

sdnBuctet = 'AutoJdck'
myBucket = 'chuan_jd_accountPassword'

# 获取闪电娘数据
sdndata = middleware.bucketAllKeys(sdnBuctet)
sender.reply(f'获取到{len(sdndata)}个原账密数据，开始迁移')

for i in sdndata:
    if i:
        try:
            data = json.loads(middleware.bucketGet(sdnBuctet,i))
            account = data['account']
            password = data['password']
            user = data['user']
            platform = data['platform']
            middleware.bucketSet(f'pin{platform.upper()}',i,user)
            middleware.bucketSet(myBucket,i,f'{account}#{password}')
            sender.reply(f'【{unquote_plus(i)}】迁移成功')
        except:
            pass
