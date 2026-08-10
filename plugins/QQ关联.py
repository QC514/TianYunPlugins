#[author: chuan]
#[version: 1.0.2]
#[class: 工具类]
#[platform: qq,qb,wx,tb,tg,web,wxmp]
#[public: true] 
#[price: 0] 
#[service: qq2669943482]
#[description: 使用之前请先装requests依赖！球球了。更新：增加判断是否为微信好友（内置微信），在非qq平台绑定qq平台绑定的jd账号。命令：qq关联]
#[title: QQ关联]
#[disable:false]
#[rule: ^QQ关联$]
#[rule: ^qq关联$]

import middleware

def main():
    senderID = middleware.getSenderID()
    sender = middleware.Sender(senderID)
    user_id = sender.getUserID() # 获取用户id
    print(f'发送人ID：{user_id}')
    imtype = sender.getImtype()
    print(f'发送人平台：{imtype}')
    
    username = sender.getUserName()
    # 如果username中包含@，表示sender不是wxbot的好友
    if username.find("@")!=-1:
        sender.reply("请先添加机器人为好友")
        return
    
    sender.reply('请发送需要关联的QQ(发送q退出)：')
    user_msg = sender.listen(60*1000)
    if user_msg == 'q':
        sender.reply('退出')
        return
    # 查询在qq桶里的pin
    qq_pins = middleware.bucketKeys('pinQQ',user_msg)
    if qq_pins[0] == '':
        sender.reply('该QQ没有绑定任何账号哦~')
        return
    for pin in qq_pins:
        middleware.bucketSet(f'pin{imtype.upper()}',pin,user_id)
        sender.reply(f'用户uid：{user_id}\n{pin}关联{imtype.upper()}平台完成')

if __name__ == '__main__':
    main()