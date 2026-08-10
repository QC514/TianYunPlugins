#[pin:true]
# ==========================市场元数据=========================================
# [opensource: false]是否开源
# [title: 兔子登录]
# [author: buzhi] 
# [icon: https://pic.ziyuan.wang/2023/12/10/guest_77c52d3e94aa7.png]图标链接地址，支持http和https
# [version: 1.4.18]
# [description: 【说明】此插件为RabbitPro登录，包含短信、扫码以和口令登录，没有RabbitPro的不要购买。部分参数需要到配参进行添加<br/>【更新】修复短信登录问题<br/>【教程】教程链接：https://docs.qq.com/doc/DZHRWSkJXeGNWV05G<br/>【交流群】QQ群：862839828]
# [platform: qq,wx,tg]
# [public:true]
# [price: 2.5]
# [service: Q群862839828]
# [class: 工具类]
# ==========================函数解析元数据======================================
# [rule: ^(登录|登陆|京东登录)$] 匹配规则，多个规则时向下依次写多个
# [rule: ^(短信登录|短信登陆)$]
# [rule: ^(扫码登录|扫码登陆)$]
# [rule: ^(口令登录|口令登陆)$]
# [priority: 999]
# [admin: false]
# [disable: false]
# ==========================参数配置数据（最下面）===============================
# [param: {"required":true,"key":"buzhi_rabbitpro_login_config.host","placeholder":"","name":"RabbitPro地址","desc":"这里填RabbitPro地址，http://ip:prot"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.intSw","placeholder":"","bool":true,"name":"智能切换容器","desc":"是否开启智能切换储存ck的容器，当一个容器满了则自动储存到下一个容器。"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.containerId","placeholder":"","name":"提交容器","desc":"填写RabbitProWeb中创建的第几个容器，请填阿拉伯数字（从2开始），不填默认为创建的第一个容器，当开启智能切换时优先储存此处填的容器。只填写单个容器"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.generalRules","placeholder":"","name":"总规则","desc":"这里用默认总触发指令运行插件后会显示在配参中设定的各个指令，如果【插件配置】=》触发规则和这里不一样，请手动复制到触发规则中，可使用配参设置的自定义指令，这里不要手动填写。"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.overallReply","placeholder":"","name":"总触发关键词","desc":"多个指令请用英文逗号隔开，默认为：登录,登陆,京东登录"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.optioningReply","placeholder":"","name":"登录选项的尾巴","desc":"默认为空"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.loginedReply","placeholder":"","name":"登录成功回复","desc":""}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.notifyMasters","placeholder":"","bool":true,"name":"关闭管理员通知","desc":"是否关闭用户登录成功后进行管理员通知"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.masters","placeholder":"","name":"管理员通知通知类型","desc":"多个用英文逗号隔开。可选qq、qb、wx、wb、tg、tb等。默认全通知"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.smsCheckBox","placeholder":"","bool":true,"name":"短信开关","desc":"是否开启短信登录"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.smsReply","placeholder":"","name":"短信登陆快捷指令","desc":"多个指令请用英文逗号隔开，默认为：短信登录,短信登陆"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.smsExplain","placeholder":"","name":"短信登陆说明","desc":""}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.qrCheckBox","placeholder":"","bool":true,"name":"扫码开关","desc":"是否开启扫码登录"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.qrReply","placeholder":"","name":"扫码登陆快捷指令","desc":"多个指令请用英文逗号隔开，默认为：扫码登录,扫码登陆"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.qrExplain","placeholder":"","name":"扫码登陆说明","desc":""}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.genCheckBox","placeholder":"","bool":true,"name":"口令开关","desc":"是否开启口令登录"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.genReply","placeholder":"","name":"口令登陆快捷指令","desc":"多个指令请用英文逗号隔开，默认为：口令登录,口令登陆"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.genExplain","placeholder":"","name":"口令登陆说明","desc":""}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.wxCheckBoxr","placeholder":"","bool":true,"name":"wxpusher绑定","desc":" 是否开启在登录完成后推送wxpusher"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.wxpusherReply","placeholder":"","name":"绑wxpusher定选项的尾巴","desc":"默认为空"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.recallBox","placeholder":"","bool":true,"name":"自动撤回消息开关","desc":"是否开启自动撤回消息，部分场景能撤回"}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.recallTime","placeholder":"","name":"对话结束等待撤回时间","desc":"填写阿拉伯数字，单位秒，默认20秒撤回"}]
# [param: {"spliter":true}]
# [param: {"required":false,"key":"buzhi_rabbitpro_login_config.drawingBed","placeholder":"","name":"图床","desc":"1-第三方图床1、2-第三方图床2、3-第三方图床3、4-第三方图床4、5-第三方图床5<br/>这里填上述图床的阿拉伯编号，默认第三方图床1。如果二维码发送失败或不可用就根据上述图床切换，都试试，哪个可以用就用哪个。"}]


import middleware
import os

# 获取发送者ID
senderID = middleware.getSenderID()
# 打印到autMan日记，可用于调试
print("senderID:" + senderID)
# 创建发送者
sender = middleware.Sender(senderID)
# 获取用户id
userId = sender.getUserID()
# 获取渠道
imType = sender.getImtype()

import json

# 接收消息 
getMessage = sender.getMessage()
# 是否为管理员
isAdmin = sender.isAdmin()
# 插件名
getPluginName = sender.getPluginName()
# 获取消息ID
# gessId = sender.getMessageID()
# 撤回消息
# recall = sender.recallMessage(gessId)

try:
    import requests
except:
    sender.reply("正在安装requests依赖，请稍后...")
    os.system("pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple requests")
    os.system("pip install -i https://pypi.tuna.tsinghua.edu.cn/simple requests")
    sender.reply("requests依赖安装成功")
import time
import re


class ConfigCheck:
    """
    配参检测
    """

    def __init__(self):
        """
        触发关键词、地址、容器智能切换开关、容器id、选项尾部回复、登录成功回复、短信开关、短信说明、扫码开关、扫码说明、口令开关、口令说明、图床选项、撤回开关、撤回等待时间、功通知开关、通知类型、wxpusher、wxpusher尾巴
        """
        # self.mainRules = middleware.bucketGet("buzhi_rabbitpro_login_config", "mainRules")
        self.host = middleware.bucketGet("buzhi_rabbitpro_login_config", "host")
        self.intSw = middleware.bucketGet("buzhi_rabbitpro_login_config", "intSw")
        self.containerId = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "containerId"
        )
        self.optioningReply = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "optioningReply"
        )
        self.loginedReply = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "loginedReply"
        )
        self.smsCheckBox = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "smsCheckBox"
        )
        self.smsExplain = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "smsExplain"
        )
        self.qrCheckBox = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "qrCheckBox"
        )
        self.qrExplain = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "qrExplain"
        )
        self.genCheckBox = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "genCheckBox"
        )
        self.genExplain = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "genExplain"
        )
        self.drawingBed = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "drawingBed"
        )
        self.recallBox = middleware.bucketGet("buzhi_rabbitpro_login_config", "recallBox")
        self.recallTime = middleware.bucketGet("buzhi_rabbitpro_login_config", "recallTime")
        self.notifyMasters = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "notifyMasters"
        )
        self.masters = middleware.bucketGet("buzhi_rabbitpro_login_config", "masters")
        self.jds = middleware.bucketKeys("pin" + imType.upper(), userId)  # 返回列表
        # self.username = middleware.bucketGet("cloud", "username")
        # self.password = middleware.bucketGet("cloud", "password")
        self.wxCheckBoxr = middleware.bucketGet("buzhi_rabbitpro_login_config", "wxCheckBoxr")
        self.wxpusherReply = middleware.bucketGet("buzhi_rabbitpro_login_config", "wxpusherReply")
        # 总规则
        self.generalRules = middleware.bucketGet("buzhi_rabbitpro_login_config", "generalRules")
        # 总触发关键词
        self.overallReply = middleware.bucketGet("buzhi_rabbitpro_login_config", "overallReply")
        # 短信登陆快捷指令
        self.smsReply = middleware.bucketGet("buzhi_rabbitpro_login_config", "smsReply")
        # 扫码登陆快捷指令
        self.qrReply = middleware.bucketGet("buzhi_rabbitpro_login_config", "qrReply")
        # 口令登陆快捷指令
        self.genReply = middleware.bucketGet("buzhi_rabbitpro_login_config", "genReply")
    
    def master(self):
        """
        管理员通知类型
        """
        if self.masters == "":
            masters = ["qq", "qb", "wx", "wb", "tg", "tb"]
        else:
            masters = self.masters.split(",")
            # print(f"通知类型：{masters}")

        return masters
    
    def notifyToMasters(self, nottify):
        """
        通知模版
        """
        if self.notifyMasters == "" or self.notifyMasters == "false":
            middleware.notifyMasters(f"{getPluginName}提醒您，{nottify}", self.master())
        else:
            pass
    
    def checkConfig(self):
        """
        检查主要配参
        """
        # [param: {"required":true,"key":
        # "buzhi_rabbitpro_login_config.mainRules","placeholder":"","name":"总关键词","desc":"这里填写触发插件菜单选项的指令，多个关键词使用英文逗号“,”分割。"}]
        # if self.mainRules == "" or len(self.mainRules) == 0:
        #     middleware.notifyMasters(f"RabbitPro登录提醒您，插件未配置总关键词，请到插件配参进行配置总关键词。", masters)
        #     return False
        if self.host == "":
            if self.notifyMasters == "true":
                print(f"插件未填写RabbitPro地址，请到插件配参进行配置地址。")
            self.notifyToMasters("插件未填写RabbitPro地址，请到插件配参进行配置地址。")
            return False
        else:
            return True

    def checkHost(self):
        """
        检查host
        """
        url = self.host
        # if self.masters == "":
        #     masters = ["qq", "qb", "wx", "wb", "tg", "tb"]
        # else:
        #     masters = self.masters.split(",")
        # 判断url末尾是否为斜杠/，有则删除
        if url.endswith("/"):
            # url = url[:-1]
            if self.notifyMasters == "true":
                print(f"RabbitPro地址填写错误，请按示例修改插件配参地址")
            self.notifyToMasters("RabbitPro地址填写错误，请按示例修改插件配参地址")
            return False
        # 检查url是否规范
        pattern = r"^(https?:\/\/)([\w-]+(?:\.[\w-]+)*(?::\d+)?)$"
        if re.findall(pattern, url):
            return True
        else:
            sender.reply("地址错误，自动退出")
            if self.notifyMasters == "true":
                print(f"RabbitPro地址填写错误，请修改插件配参地址")
            self.notifyToMasters("RabbitPro地址填写错误，请修改插件配参地址")
            return False

    def getHost(self):
        """
        请求host是否能访问
        """
        # if self.masters == "":
        #     masters = ["qq", "qb", "wx", "wb", "tg", "tb"]
        # else:
        #     masters = self.masters.split(",")
        url = self.host
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.request("get", url=url, headers=headers, timeout=30)
            if response.status_code == 200:
                print("ok")
                return True
            else:
                sender.reply("地址请求错误，自动退出")
                self.notifyToMasters("RabbitPro地址请求错误，请检查插件配参地址是否正确")
                return False
        except:
            sender.reply("地址请求错误，自动退出")
            self.notifyToMasters("RabbitPro地址请求错误，请检查插件配参地址是否正确")
            return False

    def checkPhone(self, phone):
        """
        检查手机号
        """
        pattern = r"^1[3-9]\d{9}$"
        # pattern = r"^1[3,4,5,6,7,8,9][0-9]{9}$"
        if re.match(pattern, phone):
            return True
        else:
            return False

    def checkCode(self, code):
        """
        检查验证码
        """
        pattern = r"^[0-9]{6}$"
        if re.match(pattern, code):
            return True
        else:
            return False

    def checkId(self, id):
        """
        检查容器id是否为阿拉伯数字，并检查是否存在
        并判断ck容量是否已满（满了切换下个容器），资源占用是否已满
        """
        pattern = r"^[0-9]{0,3}$"
        if re.match(pattern, id):
            return True
        else:
            False

    def getImageUrl(self, qrContent):
        """
        第三方图床
        """
        # 获取图床url
        if self.drawingBed == "0":
            qrPath = sender.replyImage(qrContent)
            path = re.search(r"tmp(.*)", qrPath).group()
            qrKeyUrlMsg = requests.post(
                url="http://aut.zhelee.cn/imgUpload",
                data={
                    "username": self.username,
                    "password": self.password,
                },
                files={
                    "imgfile": open("./plugin/web/" + path, "rb"),
                },
            ).json()

            if qrKeyUrlMsg["code"] == 200:
                url = qrKeyUrlMsg["result"]["path"]
            else:
                url = ""

        elif self.drawingBed == "1" or self.drawingBed == "":
            # url = "https://v.api.aa1.cn/api/api-qrcode/sc.php?text=" + qrContent
            resqUrl = "https://v2.api-m.com/api/qrcode?text=" + qrContent
            response = requests.request("get", url=resqUrl, timeout=30).json()
            if response["code"] == 200:
                url = response["data"]
            else:
                url = False
            
        elif self.drawingBed == "2":
            url = "https://api.xingzhige.com/API/Qrcode/?text=" + qrContent
        elif self.drawingBed == "3":
            url = "http://api.tangdouz.com/tup.php?nr=" + qrContent
        elif self.drawingBed == "4":
            url = "https://api.btstu.cn/qrcode/api.php?size=200&text=" + qrContent
        elif self.drawingBed == "5":
            # url = f"https://api.linhun.vip/api/QRcode?url={qrContent}&apiKey=75b3d6c5aaf6f1c0fe752b0eabc64abc"
            url = "https://api.yujn.cn/api/qrcode.php?size=180&text=" + qrContent
        elif self.drawingBed == "6":
            url = "https://api.gmit.vip/Api/QrCode?text=" + qrContent
        else:
            url == False
        print(url)
        return url


def requestRabbitPro(path, method, params="", data=""):
    """
    请求封装
    path：请求
    method：请求方式
    data：请求参数
    header：请求头
    """
    host = middleware.bucketGet("buzhi_rabbitpro_login_config", "host")
    url = f"{host}/{path}"
    headers = {"Content-Type": "application/json"}
    response = requests.request(
        method, url, headers=headers, params=params, data=data, timeout=30
    )
    response.encoding = "utf-8"
    print(response.text)
    return response.json()


def menuOption():
    """
    菜单选择
    """
    idList = []
    menu = "请选择你要登录的方式(输入【】内得编号即可）\n【q】退出会话"
    config = ConfigCheck()
    loginOption = loginMethod()
    if config.masters == "":
        masters = ["qq", "qb", "wx", "wb", "tg", "tb"]
    else:
        masters = config.masters.split(",")
        print(f"通知类型：{masters}")
    option = 0
    menuType = 0
    
    if config.smsExplain != "":
        smsSign = "："
    else:
        smsSign = ""
    if config.qrExplain != "":
        qrSign = "："
    else:
        qrSign = ""
    if config.genExplain != "":
        genSign = "："
    else:
        genSign = ""
    
    if (
        config.smsCheckBox == "true"
        and config.qrCheckBox == "true"
        and config.genCheckBox == "true"
    ):
        menuType = 1
        option += 1
        menu += f"\n【{option}】短信登录{smsSign}{config.smsExplain}"
        option += 1
        menu += f"\n【{option}】扫码登录{qrSign}{config.qrExplain}"
        option += 1
        menu += f"\n【{option}】口令登录{genSign}{config.genExplain}"
    elif (
        config.smsCheckBox == "true"
        and config.qrCheckBox == "true"
        and (config.genCheckBox == "false" or config.genCheckBox == "")
    ):
        menuType = 2
        option += 1
        menu += f"\n【{option}】短信登录{smsSign}{config.smsExplain}"
        option += 1
        menu += f"\n【{option}】扫码登录{qrSign}{config.qrExplain}"
    elif (
        config.smsCheckBox == "true"
        and (config.qrCheckBox == "false" or config.qrCheckBox == "")
        and config.genCheckBox == "true"
    ):
        menuType = 3
        option += 1
        menu += f"\n【{option}】短信登录{smsSign}{config.smsExplain}"
        option += 1
        menu += f"\n【{option}】口令登录{genSign}{config.genExplain}"
    elif (
        (config.smsCheckBox == "false" or config.smsCheckBox == "")
        and config.qrCheckBox == "true"
        and config.genCheckBox == "true"
    ):
        menuType = 4
        option += 1
        menu += f"\n【{option}】扫码登录{qrSign}{config.qrExplain}"
        option += 1
        menu += f"\n【{option}】口令登录{genSign}{config.genExplain}"
    elif (
        config.smsCheckBox == "true"
        and (config.qrCheckBox == "false" or config.qrCheckBox == "")
        and (config.genCheckBox == "false" or config.genCheckBox == "")
    ):
        menuType = 5
        option += 1
        menu += f"\n【{option}】短信登录{smsSign}{config.smsExplain}"
    elif (
        (config.smsCheckBox == "false" or config.smsCheckBox == "")
        and config.qrCheckBox == "true"
        and (config.genCheckBox == "false" or config.genCheckBox == "")
    ):
        menuType = 6
        option += 1
        menu += f"\n【{option}】扫码登录{qrSign}{config.qrExplain}"
    elif (
        (config.smsCheckBox == "false" or config.smsCheckBox == "")
        and (config.qrCheckBox == "false" or config.qrCheckBox == "")
        and config.genCheckBox == "true"
    ):
        menuType = 7
        option += 1
        menu += f"\n【{option}】口令登录{genSign}{config.genExplain}"
    menu += f"\n{config.optioningReply}"

    id1 = sender.reply(menu)
    try:
        idList.append(json.loads(id1)[0])
    except:
        print("id获取失败")
    listen = sender.input(60000, 5000, False)
    if str(listen) == "q" or str(listen) == "Q":
        id1 = sender.reply("退出会话")
        try:
            idList.append(json.loads(id1)[0])
        except:
            print("id获取失败")
        loginMethod().recall(idList)
        return
    elif listen == None or str(listen) == "":
        id1 = sender.reply("超时退出")
        try:
            idList.append(json.loads(id1)[0])
        except:
            print("id获取失败")
        loginMethod().recall(idList)
        return
    try:
        if menuType == 1 and int(listen) in range(1, option + 1):
            # 短信登录
            if int(listen) == 1:
                loginOption.sms(idList)
            # 扫码登录
            elif int(listen) == 2:
                loginOption.qrKey(idList)
            # 口令登录
            elif int(listen) == 3:
                loginOption.gqc(idList)
        elif menuType == 2 and int(listen) in range(1, option + 1):
            # 短信登录
            if int(listen) == 1:
                loginOption.sms(idList)
            # 扫码登录
            elif int(listen) == 2:
                loginOption.qrKey(idList)
        elif menuType == 3 and int(listen) in range(1, option + 1):
            # 短信登录
            if int(listen) == 1:
                loginOption.sms(idList)
            # 口令登录
            elif int(listen) == 2:
                loginOption.gqc(idList)
        elif menuType == 4 and int(listen) in range(1, option + 1):
            # 扫码登录
            if int(listen) == 1:
                loginOption.qrKey(idList)
            # 口令登录
            elif int(listen) == 2:
                loginOption.gqc(idList)
        elif menuType == 5 and int(listen) in range(1, option + 1):
            # 短信登录
            if int(listen) == 1:
                loginOption.sms(idList)
        elif menuType == 6 and int(listen) in range(1, option + 1):
            # 扫码登录
            if int(listen) == 1:
                loginOption.qrKey(idList)
        elif menuType == 7 and int(listen) in range(1, option + 1):
            # 口令登录
            if int(listen) == 1:
                loginOption.gqc(idList)
        else:
            id1 = sender.reply("输入错误，退出会话")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            loginMethod().recall(idList)
            return
    except Exception as e:
        print(e)
        id1 = sender.reply("出错，退出会话")
        try:
            idList.append(json.loads(id1)[0])
        except:
            print("id获取失败")
        loginMethod().recall(idList)

class ApiRequest:
    """
    请求封装
    1、短信登录
    2、扫码登录
    3、口令登录
    """

    def __init__(self):
        pass

    def checkConfig(self):
        """
        检查总配置
        """
        path = "api/Config"

        return requestRabbitPro(path, "get")

    def qlConfig(self, id):
        """
        容器配置
        """
        path = f"api/QLConfig"
        params = {"container_id": id}

        return requestRabbitPro(path, "get", params)

    def sendSMS(self, phone, id=2):
        """
        发送短信获取验证码
        phone：手机号
        """
        path = "sms/sendSMS"
        data = {"Phone": phone, "container_id": id}  # 容器ID

        return requestRabbitPro(path, "post", "", json.dumps(data))
    
    def AutoCaptcha(self, phone):
        """
        验证是否发送
        """
        path = "sms/AutoCaptcha"
        data = {"Phone": phone}

        return requestRabbitPro(path, "post", "", json.dumps(data))

    def verifyCode(self, phone, code, id=2):
        """
        验证验证码
        """
        path = "sms/VerifyCode"
        data = {"Phone": phone, "Code": code, "container_id": id}

        return requestRabbitPro(path, "post", "", json.dumps(data))

    def info(self, user_index, pin, id=2):
        """
        获取登录信息
        """
        path = "api/User"
        params = {"container_id": id, "user_index": user_index, "pin": pin}

        return requestRabbitPro(path, "get", params)

    def getQrKey(self):
        """
        获取二维码Key或口令
        """
        path = "api/GenQrCode"

        return requestRabbitPro(path, "post")

    def checkQrKey(self, key, id=2):
        """
        检查二维码或口令状态
        """
        path = "api/QrCheck"
        data = {
            "QRCodeKey": key,
            "container_id": id,
            "token": "",
        }

        return requestRabbitPro(path, "post", "", json.dumps(data))
    
    def wxQrKey(self, user_index, pin, id=2):
        """
        获取wx绑定二维码进行账号绑定
        """
        path = "api/User"
        params = {"container_id": id, "user_index": user_index, "pin": pin}
        
        return requestRabbitPro(path, "get", params)
        
    def upRemarks(self, pin, remarks, user_index, id=2):
        """修改备注"""
        path = "api/Upremarks"
        data = {
            "container_id": id,
            "pin": pin,
            "user_index": user_index
        }
        
        return requestRabbitPro(path, "post", "", json.dumps(data))
    
class loginMethod:
    """
    选择登录方式
    """

    def __init__(self) -> None:
        self.config = ConfigCheck()
        self.apiRequest = ApiRequest()
        self.loginedReply1="登录成功"
        self.loginedReply2="更新成功"
        self.retry = 10

    def masters(self):
        """
        管理员通知类型
        """
        if self.config.masters == "":
            masters = ["qq", "qb", "wx", "wb", "tg", "tb"]
        else:
            masters = self.config.masters.split(",")
            print(f"通知类型：{masters}")

        return masters
    
    def bs64Tojpg(self, bs64):
        url = f"https://free.wqwlkj.cn/wqwlapi/imgChange.php"
        data = {
            "img": bs64,
            "format": "jpg"
        }
        response = requests.post(url=url, data=data)
        if response.status_code == 200:
            return str(response.text)
        else:
            return False
    
    def containerId(self):
        """
        容器ID
        """
        id_list1 = []  # 总id
        id_list2 = []
        data_list = None
        # 先获取所有容器
        containerData = self.apiRequest.checkConfig()
        # 获取填写的容器
        containerId = middleware.bucketGet(
            "buzhi_rabbitpro_login_config", "containerId"
        )
        # 智能调节开关
        intSwBox = self.config.intSw
        # 检测容器配置，并保存id
        if containerData["success"] == True:
            data_list = containerData["data"]["list"]
            # web未创建容器
            if len(data_list) == 0:
                self.config.notifyToMasters("检测到RabbitProWeb中未创建容器")
                return False
            else:
                for data in data_list:
                    id = data["container_id"]
                    id_list1.append(id)
        else:
            self.config.notifyToMasters("获取web容器失败，请检查网络是否正常")
            return False

        # 未填写优先容器且未开启智能切换
        if containerId == "":
            id_list2.append(id_list1[0])
            print(f"默认第一个容器：{id_list2}")
            return id_list2
        else:
            priority_id = int(containerId.replace('"', ""))  # 将字符串转换为整数
            # id存在且打开了智能切换
            if priority_id in id_list1 and intSwBox == "true":
                id_list1.remove(priority_id)
                id_list1.insert(0, priority_id)
                print(f"开启智能且已填：{id_list1}")
                return id_list1
            # 填写的id存在，而未开启智能切换
            elif priority_id in id_list1 and (intSwBox == "false" or intSwBox == ""):
                id_list2.append(priority_id)
                print(f"填写且未开启智能：{id_list2}")
                return id_list2
            elif priority_id not in id_list1:
                self.config.notifyToMasters("配参中填写的“提交容器”不存在，请更改正确")
                return False

    def ck_and_tabCount(self, id):
        """
        容器CK剩余储存数量
        当前请求剩余资源
        """
        counts = self.apiRequest.qlConfig(id)
        if counts["success"] == True:
            ckCount = counts["data"]["ckcount"]
            tabCount = counts["data"]["tabcount"]

        return ckCount, tabCount
    
    def recall(self, idList):
        """
        撤回消息体
        """
        recallBox = self.config.recallBox
        recallTime = self.config.recallTime
        if recallTime == "":
            recallTime = 20
        else:
            recallTime = int(recallTime)
        if recallBox == "true":
            print("开始进行消息撤回")
            time.sleep(recallTime)
            for messId in idList:
                time.sleep(0.2)
                sender.recallMessage(messId)
            print("全部消息撤回完成")
    
    def wxCheckPin(self, pin):
        """
        检查本地是否绑定wx记录
        """
        try:
            pinUserId = middleware.bucketGet("buzhi_rabbitpro_wxpuher", pin)
            if pinUserId != "":
                checkWxPusher = True
            else:
                checkWxPusher = False
        except:
            checkWxPusher = False
        
        return checkWxPusher
    
    def wxCheckQr(self, user_index, pin, id = 2):
        """
        检查wx绑定 qrurl \ remarks
        """
        idList = []
        def mask_string(input_string, mask_length):
            """
            处理字符串打码
            """
            # 获取字符串长度  
            string_length = len(input_string)
            # 计算要掩码的字符数量  
            mask_count = string_length - mask_length  
            # 切片出要掩码的字符  
            masked_string = input_string[:mask_length] + '*' * mask_count + input_string[-mask_length:]
            return masked_string
            
        try:
            pinUserId = middleware.bucketGet("buzhi_rabbitpro_wxpuher", pin)
            print(f"pinUserId:{pinUserId}")
            if pinUserId != "":
                # checkWxPusher = True
                pinUserId = f"当前账号已绑定“{mask_string(pinUserId, 4)}”推送"
            else:
                # checkWxPusher = False
                pinUserId = "当前账号未绑定wxpusher推送"
        except:
            # checkWxPusher = False
            pinUserId = "当前账号未绑定wxpusher推送"
        wxMenu = f"{pinUserId}，\n请30秒内输入下方【】内得编号\n【1】绑定wxpusher\n【q】退出\n{config.wxpusherReply}"
        
        id1 = sender.reply(wxMenu)
        try:
            idList.append(json.loads(id1)[0])
        except:
            print("id获取失败")
        print(wxMenu)
        wxReply = sender.listen(30000)
        print(f"监听wxReply值为：{wxReply}")
        if wxReply == None or wxReply == "None" or wxReply == "error" or wxReply == "Q" or wxReply == "q" or wxReply == "":
            id1 = sender.reply("退出wxpusher绑定")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
        elif wxReply == "1":
            print("选择wxpusher推送绑定")
            wxResponse = self.apiRequest.wxQrKey(user_index, pin, id)  # 返回wxpusher地址
            if wxResponse["success"] == True:
                id1 = sender.reply("请30秒内使用WX扫描下方二维码进行wxpusher推送绑定\n【1】确认已完成扫码绑定\n【q】退出绑定")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                print("请30秒内使用WX扫描下方二维码进行wxpusher推送绑定\n【1】确认已完成扫码绑定\n【q】退出绑定")
                wxUrl = self.config.getImageUrl(wxResponse["data"]["qrurl"])
                if wxUrl == "" or wxUrl == False:
                    sender.reply("二维码生成失败，退出")
                    print("二维码生成失败，退出")
                    # try:
                    #     idList.append(json.loads(id1)[0])
                    # except:
                    #     print("id获取失败")
                    # self.recall(idList)
                    self.wxCheckQr(user_index, pin, id)
                else:
                    sender.replyImage(wxResponse["data"]["qrurl"])
                    listen = sender.listen(30000)
                    if listen == "1":
                        print("wxpusher绑定成功")
                        sender.reply("wxpusher绑定成功")
                        middleware.bucketSet("buzhi_rabbitpro_wxpuher", pin, userId)
                        self.wxCheckQr(user_index, pin, id)
                    elif listen == "q" or listen == "Q" or listen == "" or listen == "error" or listen == None:
                        sender.reply("退出wxpusher会话")
                        self.wxCheckQr(user_index, pin, id)
                    else:
                        self.wxCheckQr(user_index, pin, id)
            else:
                sender.reply("获取二维码失败，请联系管理员")
                self.config.notifyToMasters("获取wxpusher推送二维码失败，请检查RabbitPro管理员配置")
        else:
            sender.reply("输入错误，请重新输入")
            self.wxCheckQr(user_index, pin, id)
        # elif wxReply == "2":
        #     print("选择修改备注")
        #     sender.reply("请30秒内完成备注的修改，回复【q】退出会话")
        #     print("请30秒内完成备注的修改，回复【q】退出会话")
        #     remarks = sender.listen(30000)
        #     if remarks == "q" or remarks == "Q" or remarks == "" or remarks == "error":
        #         sender.reply("退出修改备注")
        #         self.wxCheckQr(user_index, pin, id)
        #     else:
        #         checkRemarks = self.apiRequest.upRemarks(pin, remarks, user_index, id)
        #         if checkRemarks["success"] == True:
        #             sender.reply("备注修改成功")
        #         else:
        #             sender.reply("备注修改失败")
        #         self.wxCheckQr(user_index, pin, id)
                

    def sms(self, ids=[]):
        """
        短信登录方式
        """
        idList = []
        idList.extend(ids)
        id_list = self.containerId()
        if id_list == False:
            id1 = sender.reply("获取配置失败，请联系管理员")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        containerId = id_list[0]
        # 优先配参容器，检测空余id
        for id in id_list:
            ckCount, tabCount = self.ck_and_tabCount(id)
            if tabCount == 0:
                id2 = sender.reply("当前登录资源已达上限,请稍等片刻或联系管理员")
                self.config.notifyToMasters("当前登录剩余资源已达上限")
                try:
                    idList.append(json.loads(id2)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            if ckCount != 0:
                containerId = id
                break
            if id_list[-1] == id and ckCount == 0:
                id3 = sender.reply("当前车位已达上限,请联系管理员")
                self.config.notifyToMasters("当前所有容器容量已达上限，请修改RabbitPro的web容器配置")
                try:
                    idList.append(json.loads(id3)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
        print(f"当前使用的容器为：{containerId}")
        id4 = sender.reply("请输入11位手机号：（输入【q】退出会话）")
        try:
            idList.append(json.loads(id4)[0])
        except:
            print("id获取失败")
        print(f"liabei{idList}")
        phone = sender.input(60000, 500, False)
        if phone == "q" or phone == "Q":
            id5 = sender.reply("退出会话")
            try:
                idList.append(json.loads(id5)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        elif phone == "" or phone == None or phone == 'None' or phone == 'error':
            id5 = sender.reply("超时退出")
            try:
                idList.append(json.loads(id5)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        else:
            checkResult = self.config.checkPhone(phone)
            if checkResult == False:
                id6 = sender.reply("输入错误，退出")
                try:
                    idList.append(json.loads(id6)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
        id7 = sender.reply("正在发送验证码，请稍后...")
        try:
            idList.append(json.loads(id7)[0])
        except:
            print("id获取失败")
        sendSMS = self.apiRequest.sendSMS(phone, containerId)  # 请求手机号登录
        print(f'短信请求：{sendSMS}')  # {'success': True, 'message': '', 'data': {'status': 505}, 'code': 505}
        if sendSMS["code"] == 505 and sendSMS["success"] == False:
            AutoCaptcha = self.apiRequest.AutoCaptcha(phone)
            print(f'验证短信是否发送成功：{AutoCaptcha}')
            for i in range(15):
                if AutoCaptcha["code"] == 666 and AutoCaptcha["success"] == False:
                    AutoCaptcha = self.apiRequest.AutoCaptcha(phone)
                    print(f'验证短信是否发送成功：{AutoCaptcha}')
                elif AutoCaptcha["code"] == 505 and AutoCaptcha["success"] == True:
                    break
            if AutoCaptcha["code"] == 666 and AutoCaptcha["success"] == False:
                id1 = sender.reply("验证码发送失败，退出会话")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
        elif sendSMS["code"] == 505 and sendSMS["success"]:
            print("验证码发送成功")
        else:
            id18 = sender.reply("获取验证码失败，请联系管理员")
            self.config.notifyToMasters("请检查服务器状态，请到web页面检查是否正常使用")
            try:
                idList.append(json.loads(id18)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        id8 = sender.reply("验证码已发送，请输入6位验证码：（输入【q】退出会话）")
        try:
            idList.append(json.loads(id8)[0])
        except:
            print("id获取失败")
        code = sender.input(60000, 500, False)
        if code == "q" or code == "Q":
            id9 = sender.reply("退出会话")
            try:
                idList.append(json.loads(id9)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        elif code == "" or code == None or code == 'None' or code == 'error':
            id9 = sender.reply("超时退出")
            try:
                idList.append(json.loads(id9)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        else:
            codeResult = self.config.checkCode(str(code))
            if codeResult == False:
                id10 = sender.reply("输入错误，退出")
                try:
                    idList.append(json.loads(id10)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            verifyCode = self.apiRequest.verifyCode(
                phone, code, containerId
            )  # 验证验证码
            print(verifyCode)  
            # {'success': True, 'code': 200, 'message': '登陆成功', 'pin': 'fefefe', 'container_id': 2, 'user_index': '666'}
            if "code" in verifyCode and verifyCode["code"] == 200:
                pin = verifyCode["pin"]
                print(pin)
                user_index = verifyCode["user_index"]
                print(user_index)
                if pin not in self.config.jds:
                    print("不存在")
                    middleware.bucketSet("pin" + imType.upper(), pin, userId)
                else:
                    print("存在")
                    self.loginedReply1 = "更新成功"
                if self.wxCheckPin(pin) == False and self.config.wxCheckBoxr == "true":
                    self.wxCheckQr(user_index, pin, id)
                id11 = sender.reply(f"{pin} {self.loginedReply1}\n{self.config.loginedReply}")
                if (self.config.notifyMasters == "" or self.config.notifyMasters == "false"):
                    middleware.notifyMasters(f"{pin} 通过短信{self.loginedReply1}", self.masters())
                try:
                    idList.append(json.loads(id11)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            elif "code" in verifyCode and verifyCode["code"] == 220:
                id12 = sender.reply("账号存在安全风险，请使用其他方式登录")
                try:
                    idList.append(json.loads(id12)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            elif "err_code" in verifyCode and verifyCode["err_code"] == 142:
                err_msg = verifyCode["err_msg"]
                returnurl = verifyCode["returnurl"]
                id1 = sender.reply(f"{err_msg}\n（请点击下面的链接进行验证，验证成功后请重新登录）")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                id1 = sender.reply(returnurl)
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            elif (
                verifyCode["code"] != 200
                and verifyCode["code"] != 220
                and verifyCode["code"] != 555
            ):
                id16 = sender.reply("输入错误，退出会话")
                try:
                    idList.append(json.loads(id16)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            else:
                id17 = sender.reply("获取验证码失败，请联系管理员")
                self.config.notifyToMasters("请检查服务器状态，请到web页面检查是否正常使用")
                try:
                    idList.append(json.loads(id17)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
        print(idList)
        self.recall(idList)

    def qrKey(self, ids=[]):
        """
        二维码登录
        """
        idList = []
        idList.extend(ids)
        id_list = self.containerId()
        if id_list == False:
            id1 = sender.reply("获取配置失败，请联系管理员")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        containerId = id_list[0]
        for id in id_list:
            ckCount, tabCount = self.ck_and_tabCount(id)
            if tabCount == 0:
                id1 = sender.reply("当前登录资源已达上限,请稍等片刻或联系管理员")
                self.config.notifyToMasters("当前登录剩余资源已达上限")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            if ckCount != 0:
                containerId = id
                break
            if id_list[-1] == id and ckCount == 0:
                id1 = sender.reply("当前车位已达上限,请联系管理员")
                self.config.notifyToMasters("当前所有容器容量已达上限，请修改RabbitPro的web容器配置")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
        print(f"当前使用的容器为：{containerId}")
        qrKey = self.apiRequest.getQrKey()
        print(qrKey)
        if qrKey["code"] == 0:
            token = qrKey["token"]
            qrCodeKey = qrKey["QRCodeKey"]
            qrUrl = "data:image/jpg;base64," + qrKey["qr"]
            print(qrUrl)
            id1 = sender.reply("正在生成二维码，请稍等")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            qrContent = "https://qr.m.jd.com/p?k=" + qrCodeKey
            qrKeyUrl = self.config.getImageUrl(qrContent)
            # url = self.config.getImageUrl(qrUrl)
            if qrKeyUrl == "" or qrKeyUrl == False:
                id1 = sender.reply("二维码生成失败，退出")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            id1 = sender.replyImage(qrKeyUrl)
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            time.sleep(0.5)
            id1 = sender.reply("二维码生成成功，请在60秒内使用京东APP扫码登录（输入【q】退出会话）")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            time.sleep(0.5)
            for _ in range(10):
                checkQrKey = self.apiRequest.checkQrKey(qrCodeKey, containerId)
                print(f"状态检查：{checkQrKey}")
                # if checkQrKey["code"] == 200 and checkQrKey["msg"] == "登陆成功":
                if checkQrKey["code"] == 200:
                    pin = checkQrKey["pin"]
                    user_index = checkQrKey["user_index"]
                    if pin not in self.config.jds:
                        print("不存在")
                        middleware.bucketSet("pin" + imType.upper(), pin, userId)
                    else:
                        print("存在")
                        self.loginedReply1 = "更新成功"
                    if self.wxCheckPin(pin) == False and self.config.wxCheckBoxr == "true":
                        self.wxCheckQr(user_index, pin, id)
                    id1 = sender.reply(f"{pin} {self.loginedReply1}\n{self.config.loginedReply}")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    if (
                        self.config.notifyMasters == ""
                        or self.config.notifyMasters == "false"
                    ):
                        middleware.notifyMasters(f"{pin} 通过扫码{self.loginedReply1}", self.masters())
                    self.recall(idList)
                    return
                elif checkQrKey["code"] == 220:
                    id1 = sender.reply("账号存在安全风险，请使用其他方式登录")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    self.recall(idList)
                    return
                elif checkQrKey["code"] == 503:
                    id1 = sender.reply("用户取消登录，退出会话")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    self.recall(idList)
                    return
                elif checkQrKey["code"] == 502:
                    id1 = sender.reply("二维码已失效，请重新获取二维码")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    self.recall(idList)
                    return
                else:
                    listen = sender.input(6000, 1000, False)  # 监听输入6s
                    if listen == "q" or listen == "Q":
                        id1 = sender.reply("退出会话")
                        try:
                            idList.append(json.loads(id1)[0])
                        except:
                            print("id获取失败")
                        self.recall(idList)
                        return
            id1 = sender.reply("超时退出")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        else:
            id1 = sender.reply("获取二维码失败，请联系管理员")
            self.config.notifyToMasters("请检查服务器状态，请到web页面检查是否正常使用")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        print(idList)
        self.recall(idList)

    def gqc(self, ids=[]):
        """
        口令登录
        """
        idList = []
        idList.extend(ids)
        id_list = self.containerId()
        if id_list == False:
            id1 = sender.reply("获取配置失败，请联系管理员")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        containerId = id_list[0]
        time.sleep(0.5)
        for id in id_list:
            ckCount, tabCount = self.ck_and_tabCount(id)
            if tabCount == 0:
                id1 = sender.reply("当前登录资源已达上限,请稍等片刻或联系管理员")
                self.config.notifyToMasters("当前登录剩余资源已达上限")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
            if ckCount != 0:
                containerId = id
                break
            if id_list[-1] == id and ckCount == 0:
                id1 = sender.reply("当前车位已达上限,请联系管理员")
                self.config.notifyToMasters("当前所有容器容量已达上限，请修改RabbitPro的web容器配置")
                try:
                    idList.append(json.loads(id1)[0])
                except:
                    print("id获取失败")
                self.recall(idList)
                return
        print(f"当前使用的容器为：{containerId}")
        id1 = sender.reply("口令生成中，请稍等")
        try:
            idList.append(json.loads(id1)[0])
        except:
            print("id获取失败")
        getQrKey = self.apiRequest.getQrKey()
        code = getQrKey["code"]
        if code == 0:
            jcommond = getQrKey["jcommond"]
            qrCodeKey = getQrKey["QRCodeKey"]
            id1 = sender.reply(jcommond)
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            id1 = sender.reply("口令生成成功，请60秒内复制口令打开京东APP进行登录（输入【q】退出会话）")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            for _ in range(10):
                checkQrKey = self.apiRequest.checkQrKey(qrCodeKey, containerId)
                print(checkQrKey)
                if checkQrKey["code"] == 200:
                    pin = checkQrKey["pin"]
                    user_index = checkQrKey["user_index"]
                    if pin not in self.config.jds:
                        print("不存在")
                        middleware.bucketSet("pin" + imType.upper(), pin, userId)
                    else:
                        print("存在")
                        self.loginedReply1 = "更新成功"
                    if self.wxCheckPin(pin) == False and self.config.wxCheckBoxr == "true":
                        print("开始进行wxpusher绑定")
                        self.wxCheckQr(user_index, pin, id)
                    id1 = sender.reply(f"{pin} {self.loginedReply1}\n{self.config.loginedReply}")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    if (
                        self.config.notifyMasters == ""
                        or self.config.notifyMasters == "false"
                    ):
                        middleware.notifyMasters(f"{pin} 通过口令{self.loginedReply1}", self.masters())
                    self.recall(idList)
                    return
                elif checkQrKey["code"] == 220:
                    id1 = sender.reply("账号存在安全风险，请使用其他方式登录")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    self.recall(idList)
                    return
                elif checkQrKey["code"] == 502:
                    id1 = sender.reply("口令已失效，请重新获取口令")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    self.recall(idList)
                    return
                elif checkQrKey["code"] == 503:
                    id1 = sender.reply("用户取消登录，退出会话")
                    try:
                        idList.append(json.loads(id1)[0])
                    except:
                        print("id获取失败")
                    self.recall(idList)
                    return
                else:
                    listen = sender.input(6000, 10000, False)  # 监听输入10s
                    if listen == "q" or listen == "Q":
                        id1 = sender.reply("退出会话")
                        try:
                            idList.append(json.loads(id1)[0])
                        except:
                            print("id获取失败")
                        self.recall(idList)
                        return
            id1 = sender.reply("超时退出")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        else:
            id1 = sender.reply("获取口令失败，请联系管理员")
            self.config.notifyToMasters("请检查服务器状态，请到web页面检查是否正常使用")
            try:
                idList.append(json.loads(id1)[0])
            except:
                print("id获取失败")
            self.recall(idList)
            return
        print(idList)
        self.recall(idList)


if __name__ == "__main__":
    def rules(reply):
        # 规则处理成正则规则
        replyList = reply.split(",")
        reRules = ""
        for reply in replyList:
            if len(replyList) > 1:
                if reply == replyList[0]:
                    reRules += f"^({reply}|"
                elif reply != replyList[0] and reply != replyList[-1]:
                    reRules += f"{reply}|"
                else:
                    reRules += f"{reply})$"
            else:
                reRules += f"^({reply})$"
        return reRules
    config = ConfigCheck()
    configResult = config.checkConfig()
    if configResult == False:
        pass
    else:
        checkHost = config.checkHost()
        if checkHost == False:
            pass
        else:
            getHost = config.getHost()
            if getHost == False:
                pass
            else:
                # 总规则
                generalRules = ""
                if config.overallReply == "":
                    overallReply = "登录,登陆,京东登录"
                else:
                    overallReply = config.overallReply
                if config.smsReply == "":
                    smsReply = "短信登录,短信登陆"
                else:
                    smsReply = config.smsReply
                if config.qrReply == "":
                    qrReply = "扫码登录,扫码登陆"
                else:
                    qrReply = config.qrReply
                if config.genReply == "":
                    genReply = "口令登录,口令登陆"
                else:
                    genReply = config.genReply
                generalRules += rules(overallReply) + ","
                generalRules += rules(smsReply) + ","
                generalRules += rules(qrReply) + ","
                generalRules += rules(genReply)
                try:
                    value = json.loads(middleware.bucketGet("plugins_config", "RabbitPro登录"))
                    if value["rules"] != generalRules:
                        value["rules"] = generalRules
                        middleware.bucketSet("plugins_config", "RabbitPro登录", json.dumps(value, ensure_ascii=False))
                        print("触发规则设置成功")
                except:
                    print("触发规则设置失败")
                middleware.bucketSet("buzhi_rabbitpro_login_config", "generalRules", generalRules)
                
                if getMessage in overallReply.split(","):
                    menuOption()
                elif getMessage in smsReply.split(",") and config.smsCheckBox == "true":
                    loginMethod().sms()
                elif getMessage in qrReply.split(",") and config.qrCheckBox == "true":
                    loginMethod().qrKey()
                elif getMessage in genReply.split(",") and config.genCheckBox == "true":
                    loginMethod().gqc()
