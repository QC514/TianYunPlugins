#[disable:true]
# [author: 601712460]
# [public: true]
# [title: 一键安装依赖]
# [version: 0]
# [create_at: 2024-05-10 15:00:04]
# [price: 0]
# [rule: ^一键安装依赖$]
# [priority: 6666666]优先级
# [admin: true]
# [description: 一键安装python/nodejs依赖，安装成功 请给你的机器人发送指令：一键安装依赖]
# =======================
# 脚本及其中涉及的任何解锁和解密分析脚本，仅用于测试和学习研究，禁止用于商业用途，不能保证其合法性，准确性，完整性和有效性，请根据情况自行判断。 您必须在下载后的24小时内从计算机或手机中完全删除此脚本

import middleware
import requests
import os


if __name__=="__main__":
    sender = middleware.Sender(middleware.getSenderID())
    sender.reply("开始安装依赖，请耐心等待！")
    d = {
            "py":["colorlog","js2py","pycryptodome","sseclient","fake_useragent","urllib3==1.25.11","redis"],
            "node":["moment","axios@0.27.2","request","md5","jsencrypt"]
        }
    d_py = d['py']
    if d_py:
        for index, module in enumerate(d_py,start=1):
            success=os.system("pip3 install "+module)
            #判断是否安装成功
            if success!=0:
                sender.reply(f"python 依赖【{module}】安装失败❌")
            else:
                sender.reply(f"python 依赖【{module}】安装成功✅")       
    d_node = d['node']
    if d_node:
        for index,module in enumerate(d_node,start=1):
            success=os.system("npm install "+module)
            #判断是否安装成功
            if success!=0:
                sender.reply(f"nodejs 依赖【{module}】安装失败❌")
            else:
                sender.reply(f"nodejs 依赖【{module}】安装成功✅")
    sender.reply("依赖安装完毕")
    exit("依赖安装完毕")
    
    