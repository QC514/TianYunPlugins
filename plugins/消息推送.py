#[author: chuan]
#[version: 1.6.3]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg]
#[title: 消息推送]
#[price: 0]
#[service: 2669943482]
#[priority: 999]
#[public:true] 
#[description: 介绍：用来推送消息的接口]
#[disable:false]
#[router: /push]请求路径
#[method: post]微服务方法
#[method: get]微服务方法

import middleware
import json
import re

def main():
    if method == 'get':
        sender.reply('你的推送正常运行中......')
    elif method == 'post':
        body = sender.getRouterBody()
        params = sender.getRouterParams()
        try:
            if body:
                print('body:', body)
                if isinstance(body, str):
                    body = json.loads(body)
                isAdmin = body.get('isAdmin', False)
                imtype = body.get('imtype')
                userId = body.get('userId')
                groupId = body.get('groupId')
                message = body.get('message')
                if isAdmin:
                    middleware.notifyMasters(message,re.split(r'[,，]', imtype))
                else:
                    middleware.push(imtype, groupId, userId, '', message)
            elif params:
                if isinstance(params, str):
                    params = json.loads(params)
                isAdmin = body.get('isAdmin', False)
                imtype = body.get('imtype')
                userId = body.get('userId')
                groupId = body.get('groupId')
                message = body.get('message')
            else:
                return
        except:
            return
        sender.reply(json.dumps({'status': 0,}))

if __name__ == '__main__':
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    # 获取路由
    router = sender.getRouterPath()
    method = sender.getRouterMethod()
    main()