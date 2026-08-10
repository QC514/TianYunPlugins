# [disable:false]
# [title:bc_qq手机号撤回]
# [author: 241793]
# [class: 工具类]
# [platform: qq,qb]
# [price: 0]
# [service: 大帅逼]
# [rule: ^1[3-9]\d{9}$]
# [description: ntqq可用，其它不确定，记得给机器人管理员身份]
# [admin: false]
# [version: 1.0.0]
import middleware


senderID = middleware.getSenderID()
sender = middleware.Sender(senderID)
user = sender.getUserID()
messageid = sender.getMessageID()

sender.recallMessage(messageid)
sender.reply("手机号被我撤回了")